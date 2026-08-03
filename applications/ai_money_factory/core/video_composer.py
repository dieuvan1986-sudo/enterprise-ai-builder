from __future__ import annotations

import json
import logging
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from applications.ai_money_factory.core.content_models import SubtitleTrack
from applications.ai_money_factory.core.music_engine import MusicTrack
from applications.ai_money_factory.core.subtitle_renderer import (
    SubtitleRenderResult,
)
from applications.ai_money_factory.core.voice_render import VoiceRenderResult

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class VisualAsset:
    """
    One caller-provided visual artifact for a composed video scene.
    """

    scene_number: int
    path: Path | str
    duration_seconds: float


@dataclass(slots=True)
class VideoRenderConfig:
    """
    FFmpeg and output settings for vertical short video composition.
    """

    width: int = 1080
    height: int = 1920
    fps: int = 30
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    pixel_format: str = "yuv420p"
    ffmpeg_path: Path | str = "ffmpeg"
    ffprobe_path: Path | str = "ffprobe"
    timeout_seconds: int = 300
    crf: int = 20
    audio_bitrate: str = "192k"


@dataclass(slots=True)
class VideoCompositionRequest:
    """
    Caller-provided assets and configuration for one final MP4 render.
    """

    title: str
    visual_assets: list[VisualAsset]
    voice_track: VoiceRenderResult | None
    subtitles: SubtitleRenderResult | SubtitleTrack | None
    music_track: MusicTrack | None
    output_path: Path | str
    duration_seconds: float | None = None
    config: VideoRenderConfig = field(default_factory=VideoRenderConfig)


@dataclass(slots=True)
class VideoCompositionResult:
    """
    Verified MP4 artifact produced by VideoComposer.
    """

    title: str
    output_path: Path
    duration_seconds: float
    width: int
    height: int
    fps: int
    video_codec: str
    audio_codec: str
    has_voice: bool
    has_music: bool
    has_subtitles: bool


class VideoComposerError(RuntimeError):
    """
    Raised when assets cannot be composed or verified.
    """


class VideoComposer:
    """
    Compose caller-provided visual, voice, subtitle, and music artifacts.

    The composer does not generate upstream assets. It validates files,
    constructs FFmpeg manifests, renders one vertical MP4, and verifies the
    generated artifact with FFprobe before returning success.
    """

    _IMAGE_EXTENSIONS = {".jpeg", ".jpg", ".png", ".webp"}

    def compose(
        self,
        request: VideoCompositionRequest,
    ) -> VideoCompositionResult:
        output_path = Path(request.output_path)
        config = request.config
        duration_seconds = self._duration_for(request)

        self._validate_request(
            request=request,
            output_path=output_path,
            duration_seconds=duration_seconds,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        work_dir = output_path.parent / f".{output_path.stem}_composer"
        work_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Composing video '%s' to %s at %sx%s %sfps.",
            request.title,
            output_path,
            config.width,
            config.height,
            config.fps,
        )

        visual_manifest = self._write_visual_manifest(
            request.visual_assets,
            work_dir / "visuals.ffconcat",
        )
        voice_manifest = self._write_voice_manifest(request.voice_track, work_dir)
        subtitle_path = self._write_subtitle_file(request.subtitles, work_dir)
        command = self._build_ffmpeg_command(
            request=request,
            output_path=output_path,
            visual_manifest=visual_manifest,
            voice_manifest=voice_manifest,
            subtitle_path=subtitle_path,
            duration_seconds=duration_seconds,
        )

        self._run_command(
            command=command,
            timeout_seconds=config.timeout_seconds,
            error_prefix="ffmpeg failed while composing video",
        )
        self._verify_output(
            output_path=output_path,
            request=request,
            duration_seconds=duration_seconds,
        )

        logger.info("Composed and verified video artifact at %s.", output_path)

        return VideoCompositionResult(
            title=request.title,
            output_path=output_path,
            duration_seconds=duration_seconds,
            width=config.width,
            height=config.height,
            fps=config.fps,
            video_codec=config.video_codec,
            audio_codec=config.audio_codec,
            has_voice=request.voice_track is not None,
            has_music=request.music_track is not None,
            has_subtitles=request.subtitles is not None,
        )

    def _validate_request(
        self,
        *,
        request: VideoCompositionRequest,
        output_path: Path,
        duration_seconds: float,
    ) -> None:
        config = request.config

        if output_path.suffix.lower() != ".mp4":
            raise ValueError("VideoComposer output_path must use a .mp4 suffix.")

        if duration_seconds <= 0:
            raise ValueError("Composition duration must be positive.")

        if not request.visual_assets:
            raise ValueError("At least one visual asset is required.")

        if config.width <= 0 or config.height <= 0:
            raise ValueError("Render width and height must be positive.")

        if config.fps <= 0:
            raise ValueError("Render fps must be positive.")

        if config.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be at least 1.")

        for asset in request.visual_assets:
            self._validate_visual_asset(asset)

        if request.voice_track is not None:
            for scene in request.voice_track.scenes:
                _require_file(Path(scene.audio_path), "Voice audio")

        if request.music_track is not None:
            _require_file(Path(request.music_track.audio_path), "Music audio")

    def _validate_visual_asset(self, asset: VisualAsset) -> None:
        if asset.scene_number <= 0:
            raise ValueError("Visual asset scene_number must be positive.")

        if asset.duration_seconds <= 0:
            raise ValueError(
                f"Visual asset {asset.scene_number} duration must be positive."
            )

        _require_file(Path(asset.path), "Visual asset")

    def _duration_for(self, request: VideoCompositionRequest) -> float:
        if request.duration_seconds is not None:
            return float(request.duration_seconds)

        return round(
            sum(asset.duration_seconds for asset in request.visual_assets),
            3,
        )

    def _write_visual_manifest(
        self,
        visual_assets: list[VisualAsset],
        manifest_path: Path,
    ) -> Path:
        ordered_assets = sorted(
            visual_assets,
            key=lambda asset: asset.scene_number,
        )
        lines = ["ffconcat version 1.0"]

        for asset in ordered_assets:
            visual_path = Path(asset.path)
            lines.append(f"file '{_concat_escape(visual_path)}'")
            lines.append(f"duration {_format_seconds(asset.duration_seconds)}")

        lines.append(f"file '{_concat_escape(Path(ordered_assets[-1].path))}'")
        manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        return manifest_path

    def _write_voice_manifest(
        self,
        voice_track: VoiceRenderResult | None,
        work_dir: Path,
    ) -> Path | None:
        if voice_track is None:
            return None

        manifest_path = work_dir / "voice.ffconcat"
        lines = ["ffconcat version 1.0"]

        for scene in sorted(voice_track.scenes, key=lambda item: item.scene_number):
            lines.append(f"file '{_concat_escape(scene.audio_path)}'")

        manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        return manifest_path

    def _write_subtitle_file(
        self,
        subtitles: SubtitleRenderResult | SubtitleTrack | None,
        work_dir: Path,
    ) -> Path | None:
        if subtitles is None:
            return None

        subtitle_path = work_dir / "subtitles.srt"
        blocks: list[str] = []

        for cue in subtitles.cues:
            blocks.append(
                "\n".join(
                    [
                        str(cue.cue_number),
                        (
                            f"{_srt_timestamp(cue.start_seconds)} --> "
                            f"{_srt_timestamp(cue.end_seconds)}"
                        ),
                        cue.text,
                    ]
                )
            )

        subtitle_path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")

        return subtitle_path

    def _build_ffmpeg_command(
        self,
        *,
        request: VideoCompositionRequest,
        output_path: Path,
        visual_manifest: Path,
        voice_manifest: Path | None,
        subtitle_path: Path | None,
        duration_seconds: float,
    ) -> list[str]:
        config = request.config
        command = [
            str(config.ffmpeg_path),
            "-y",
            "-safe",
            "0",
            "-f",
            "concat",
            "-i",
            str(visual_manifest),
        ]
        input_index = 1
        voice_index: int | None = None
        music_index: int | None = None

        if voice_manifest is not None:
            command.extend(
                [
                    "-safe",
                    "0",
                    "-f",
                    "concat",
                    "-i",
                    str(voice_manifest),
                ]
            )
            voice_index = input_index
            input_index += 1

        if request.music_track is not None:
            command.extend(["-i", str(request.music_track.audio_path)])
            music_index = input_index

        filter_complex, audio_label = self._filter_complex(
            request=request,
            subtitle_path=subtitle_path,
            voice_index=voice_index,
            music_index=music_index,
        )
        command.extend(
            [
                "-filter_complex",
                filter_complex,
                "-map",
                "[vout]",
            ]
        )

        if audio_label is not None:
            command.extend(["-map", audio_label, "-c:a", config.audio_codec])
        else:
            command.extend(["-an"])

        command.extend(
            [
                "-t",
                _format_seconds(duration_seconds),
                "-r",
                str(config.fps),
                "-c:v",
                config.video_codec,
                "-crf",
                str(config.crf),
                "-pix_fmt",
                config.pixel_format,
                "-movflags",
                "+faststart",
            ]
        )

        if audio_label is not None:
            command.extend(["-b:a", config.audio_bitrate])

        command.append(str(output_path))

        return command

    def _filter_complex(
        self,
        *,
        request: VideoCompositionRequest,
        subtitle_path: Path | None,
        voice_index: int | None,
        music_index: int | None,
    ) -> tuple[str, str | None]:
        config = request.config
        video_filter = (
            f"[0:v]fps={config.fps},"
            f"scale={config.width}:{config.height}:force_original_aspect_ratio=decrease,"
            f"pad={config.width}:{config.height}:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1,format={config.pixel_format}"
        )

        if subtitle_path is not None:
            video_filter += f",subtitles='{_filter_path_escape(subtitle_path)}'"

        filters = [f"{video_filter}[vout]"]

        if voice_index is not None and music_index is not None:
            filters.append(f"[{music_index}:a]volume=0.35[music]")
            filters.append(f"[{voice_index}:a][music]amix=inputs=2:duration=first[aout]")

            return ";".join(filters), "[aout]"

        if voice_index is not None:
            return ";".join(filters), f"{voice_index}:a"

        if music_index is not None:
            return ";".join(filters), f"{music_index}:a"

        return ";".join(filters), None

    def _verify_output(
        self,
        *,
        output_path: Path,
        request: VideoCompositionRequest,
        duration_seconds: float,
    ) -> None:
        _require_file(output_path, "Composed video")
        command = [
            str(request.config.ffprobe_path),
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,codec_name",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(output_path),
        ]
        result = self._run_command(
            command=command,
            timeout_seconds=request.config.timeout_seconds,
            error_prefix="ffprobe failed while verifying video",
        )

        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise VideoComposerError("ffprobe returned invalid JSON.") from exc

        streams = payload.get("streams") or []
        format_payload = payload.get("format") or {}

        if not streams:
            raise VideoComposerError("ffprobe found no video stream.")

        stream = streams[0]

        if int(stream.get("width", 0)) != request.config.width:
            raise VideoComposerError("Verified video width does not match config.")

        if int(stream.get("height", 0)) != request.config.height:
            raise VideoComposerError("Verified video height does not match config.")

        verified_duration = float(format_payload.get("duration", 0))

        if verified_duration <= 0:
            raise VideoComposerError("Verified video duration is invalid.")

        if abs(verified_duration - duration_seconds) > 1.0:
            logger.warning(
                "Verified video duration %ss differs from requested %ss.",
                verified_duration,
                duration_seconds,
            )

    @staticmethod
    def _run_command(
        *,
        command: list[str],
        timeout_seconds: int,
        error_prefix: str,
    ) -> subprocess.CompletedProcess[str]:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise VideoComposerError(f"{error_prefix}: timed out.") from exc

        if result.returncode != 0:
            error = result.stderr.strip() or result.stdout.strip()
            raise VideoComposerError(f"{error_prefix}: {error}")

        return result


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{label} file does not exist: {path}")


def _format_seconds(duration_seconds: float) -> str:
    return f"{duration_seconds:.3f}".rstrip("0").rstrip(".")


def _concat_escape(path: Path) -> str:
    return path.as_posix().replace("'", "'\\''")


def _filter_path_escape(path: Path) -> str:
    return path.as_posix().replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def _srt_timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1_000)

    return (
        f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},"
        f"{milliseconds:03d}"
    )


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    slug = slug.strip("_")

    return slug or "video"
