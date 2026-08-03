from __future__ import annotations

import json
import logging
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from applications.ai_money_factory.core.video_intelligence.models import (
    DetectedScene,
    SourceVideo,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SceneDetectionSettings:
    """
    FFprobe/FFmpeg settings for deterministic scene boundary detection.
    """

    ffprobe_path: Path | str = "ffprobe"
    ffmpeg_path: Path | str = "ffmpeg"
    scene_threshold: float = 0.35
    min_scene_duration_seconds: float = 1.0
    timeout_seconds: int = 120


class SceneDetectionError(RuntimeError):
    """
    Raised when source video scene detection cannot complete.
    """


class SceneDetectionEngine:
    """
    Detect source-video scene boundaries using FFprobe and FFmpeg.

    The engine never performs fixed trimming. It builds scenes exclusively from
    source metadata and FFmpeg scene-change timestamps.
    """

    def __init__(
        self,
        settings: SceneDetectionSettings | None = None,
    ) -> None:
        self.settings = settings or SceneDetectionSettings()
        self._validate_settings()

    def detect(
        self,
        source_path: str | Path,
    ) -> tuple[SourceVideo, list[DetectedScene]]:
        path = Path(source_path)

        if not path.is_file():
            raise FileNotFoundError(
                f"Source video does not exist: {path}"
            )

        source_video = self._probe_source(path)
        boundaries = self._detect_boundaries(path)
        scenes = self._scenes_from_boundaries(
            source_video,
            boundaries,
        )

        logger.info(
            "Detected %s scenes in source video %s.",
            len(scenes),
            source_video.path,
        )

        return source_video, scenes

    def _validate_settings(self) -> None:
        if not 0 < self.settings.scene_threshold < 1:
            raise ValueError(
                "scene_threshold must be greater than 0 and less than 1."
            )

        if self.settings.min_scene_duration_seconds <= 0:
            raise ValueError(
                "min_scene_duration_seconds must be positive."
            )

        if self.settings.timeout_seconds < 1:
            raise ValueError(
                "timeout_seconds must be at least 1."
            )

    def _probe_source(self, source_path: Path) -> SourceVideo:
        command = [
            str(self.settings.ffprobe_path),
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,r_frame_rate",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(source_path),
        ]
        result = self._run_command(
            command=command,
            error_prefix=(
                "ffprobe failed while reading source video metadata"
            ),
        )

        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise SceneDetectionError(
                "ffprobe returned invalid JSON."
            ) from exc

        streams = payload.get("streams") or []
        format_payload = payload.get("format") or {}

        if not streams:
            raise SceneDetectionError(
                "ffprobe found no video stream."
            )

        stream = streams[0]
        duration = float(
            format_payload.get("duration", 0)
        )
        width = int(stream.get("width", 0))
        height = int(stream.get("height", 0))
        fps = _parse_frame_rate(
            str(stream.get("r_frame_rate", "0/1"))
        )

        if duration <= 0:
            raise SceneDetectionError(
                "Source video duration must be positive."
            )

        if width <= 0 or height <= 0:
            raise SceneDetectionError(
                "Source video dimensions must be positive."
            )

        if fps <= 0:
            raise SceneDetectionError(
                "Source video frame rate must be positive."
            )

        return SourceVideo(
            path=source_path,
            duration_seconds=round(duration, 3),
            width=width,
            height=height,
            fps=round(fps, 3),
        )

    def _detect_boundaries(
        self,
        source_path: Path,
    ) -> list[float]:
        command = [
            str(self.settings.ffmpeg_path),
            "-hide_banner",
            "-i",
            str(source_path),
            "-filter:v",
            (
                "select='gt(scene,"
                f"{self.settings.scene_threshold}"
                ")',showinfo"
            ),
            "-f",
            "null",
            "-",
        ]
        result = self._run_command(
            command=command,
            error_prefix=(
                "ffmpeg failed while detecting scene changes"
            ),
        )

        return _parse_scene_timestamps(
            f"{result.stdout}\n{result.stderr}"
        )

    def _scenes_from_boundaries(
        self,
        source_video: SourceVideo,
        boundaries: list[float],
    ) -> list[DetectedScene]:
        normalized_boundaries = [
            boundary
            for boundary in sorted(
                set(round(value, 3) for value in boundaries)
            )
            if 0 < boundary < source_video.duration_seconds
        ]

        timestamps = [
            0.0,
            *normalized_boundaries,
            source_video.duration_seconds,
        ]

        scenes = [
            (start, end)
            for start, end in zip(
                timestamps,
                timestamps[1:],
            )
            if end > start
        ]

        merged_scenes = _merge_short_scenes(
            scenes,
            min_duration_seconds=(
                self.settings.min_scene_duration_seconds
            ),
        )

        return [
            DetectedScene(
                source_path=source_video.path,
                scene_number=index,
                start_seconds=round(start, 3),
                end_seconds=round(end, 3),
                duration_seconds=round(
                    end - start,
                    3,
                ),
            )
            for index, (start, end) in enumerate(
                merged_scenes,
                start=1,
            )
        ]

    def _run_command(
        self,
        *,
        command: list[str],
        error_prefix: str,
    ) -> subprocess.CompletedProcess[str]:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=self.settings.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise SceneDetectionError(
                f"{error_prefix}: timed out."
            ) from exc

        if result.returncode != 0:
            error = (
                result.stderr.strip()
                or result.stdout.strip()
            )
            raise SceneDetectionError(
                f"{error_prefix}: {error}"
            )

        return result


def _parse_scene_timestamps(
    output: str,
) -> list[float]:
    timestamps: list[float] = []

    for match in re.finditer(
        r"pts_time:([0-9]+(?:\.[0-9]+)?)",
        output,
    ):
        timestamps.append(float(match.group(1)))

    return timestamps


def _merge_short_scenes(
    scenes: list[tuple[float, float]],
    *,
    min_duration_seconds: float,
) -> list[tuple[float, float]]:
    merged: list[tuple[float, float]] = []
    index = 0

    while index < len(scenes):
        start, end = scenes[index]

        while (
            end - start < min_duration_seconds
            and index + 1 < len(scenes)
        ):
            index += 1
            _, end = scenes[index]

        if (
            merged
            and end - start < min_duration_seconds
        ):
            previous_start, _ = merged[-1]
            merged[-1] = (
                previous_start,
                end,
            )
        else:
            merged.append((start, end))

        index += 1

    return merged


def _parse_frame_rate(value: str) -> float:
    if "/" not in value:
        return float(value)

    numerator, denominator = value.split(
        "/",
        maxsplit=1,
    )
    denominator_value = float(denominator)

    if denominator_value == 0:
        return 0

    return (
        float(numerator)
        / denominator_value
    )
