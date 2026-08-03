from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import overload

from applications.ai_money_factory.core.content_models import (
    Narration,
    NarrationSegment,
    SubtitleCue,
    SubtitleTrack,
    VoiceTrack,
    VoiceTrackSegment,
)
from applications.ai_money_factory.core.video_factory import VideoPackage

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SubtitleScene:
    scene_number: int
    purpose: str
    start_seconds: float
    end_seconds: float
    cues: list[SubtitleCue]


@dataclass(slots=True)
class SubtitleRenderResult:
    title: str
    total_duration_seconds: int
    scenes: list[SubtitleScene]
    cues: list[SubtitleCue]


@dataclass(slots=True)
class _SubtitleSourceSegment:
    scene_number: int
    duration_seconds: float
    text: str
    purpose: str


class SubtitleRenderError(RuntimeError):
    """
    Raised when narration cannot be converted into subtitle timing.
    """


class SubtitleRenderer:
    """
    Build subtitle timing from Narration, VoiceTrack, or legacy VideoPackage input.

    Narration and VoiceTrack inputs produce the content-model SubtitleTrack.
    VideoPackage input preserves the existing SubtitleRenderResult API.
    """

    def __init__(
        self,
        *,
        max_chars_per_cue: int = 42,
        min_cue_seconds: float = 0.8,
    ) -> None:
        if max_chars_per_cue < 12:
            raise ValueError("max_chars_per_cue must be at least 12.")

        if min_cue_seconds <= 0:
            raise ValueError("min_cue_seconds must be greater than zero.")

        self.max_chars_per_cue = max_chars_per_cue
        self.min_cue_seconds = min_cue_seconds

    @overload
    def render(self, source: Narration) -> SubtitleTrack: ...

    @overload
    def render(self, source: VoiceTrack) -> SubtitleTrack: ...

    @overload
    def render(self, source: VideoPackage) -> SubtitleRenderResult: ...

    def render(
        self,
        source: Narration | VoiceTrack | VideoPackage,
    ) -> SubtitleTrack | SubtitleRenderResult:
        if isinstance(source, VideoPackage):
            return self._render_video_package(source)

        if isinstance(source, Narration):
            return self._render_subtitle_track(
                title=source.title,
                segments=[
                    _segment_from_narration_segment(segment)
                    for segment in source.segments
                ],
                expected_duration_seconds=source.total_duration_seconds,
            )

        if isinstance(source, VoiceTrack):
            return self._render_subtitle_track(
                title=source.title,
                segments=[
                    _segment_from_voice_track_segment(segment)
                    for segment in source.segments
                ],
                expected_duration_seconds=source.total_duration_seconds,
            )

        raise TypeError(
            "SubtitleRenderer.render expects Narration, VoiceTrack, or "
            "VideoPackage."
        )

    def _render_video_package(
        self,
        package: VideoPackage,
    ) -> SubtitleRenderResult:
        segments = [
            _SubtitleSourceSegment(
                scene_number=scene.scene_number,
                duration_seconds=float(scene.duration_seconds),
                text=scene.narration,
                purpose=scene.purpose,
            )
            for scene in package.scenes
        ]
        scenes, cues, _ = self._render_segments(
            title=package.title,
            segments=segments,
            expected_duration_seconds=float(package.total_duration_seconds),
        )

        return SubtitleRenderResult(
            title=package.title,
            total_duration_seconds=package.total_duration_seconds,
            scenes=scenes,
            cues=cues,
        )

    def _render_subtitle_track(
        self,
        *,
        title: str,
        segments: list[_SubtitleSourceSegment],
        expected_duration_seconds: float | None,
    ) -> SubtitleTrack:
        _, cues, duration = self._render_segments(
            title=title,
            segments=segments,
            expected_duration_seconds=expected_duration_seconds,
        )

        return SubtitleTrack(
            title=title,
            total_duration_seconds=duration,
            cues=cues,
        )

    def _render_segments(
        self,
        *,
        title: str,
        segments: list[_SubtitleSourceSegment],
        expected_duration_seconds: float | None,
    ) -> tuple[list[SubtitleScene], list[SubtitleCue], float]:
        if not segments:
            raise ValueError("Subtitle source must contain at least one segment.")

        logger.info(
            "Rendering subtitles for '%s' with %s segments.",
            title,
            len(segments),
        )

        scenes: list[SubtitleScene] = []
        cues: list[SubtitleCue] = []
        cursor_seconds = 0.0

        for segment in segments:
            scene_start = cursor_seconds
            scene_end = scene_start + self._validated_duration(segment)
            scene_cues = self._render_segment(
                segment=segment,
                scene_start_seconds=scene_start,
                scene_end_seconds=scene_end,
                cue_offset=len(cues),
            )

            scenes.append(
                SubtitleScene(
                    scene_number=segment.scene_number,
                    purpose=segment.purpose,
                    start_seconds=round(scene_start, 3),
                    end_seconds=round(scene_end, 3),
                    cues=scene_cues,
                )
            )
            cues.extend(scene_cues)
            cursor_seconds = scene_end

        if not cues:
            raise SubtitleRenderError("No subtitle cues were generated.")

        total_duration = round(cursor_seconds, 3)

        if expected_duration_seconds is not None and (
            round(float(expected_duration_seconds), 3) != total_duration
        ):
            logger.warning(
                "Subtitle duration %ss differs from expected duration %ss.",
                total_duration,
                expected_duration_seconds,
            )

        logger.info("Rendered %s subtitle cues for '%s'.", len(cues), title)

        return scenes, cues, total_duration

    def _render_segment(
        self,
        *,
        segment: _SubtitleSourceSegment,
        scene_start_seconds: float,
        scene_end_seconds: float,
        cue_offset: int,
    ) -> list[SubtitleCue]:
        narration = _normalize_text(segment.text)

        if not narration:
            raise ValueError(
                f"Segment {segment.scene_number} narration cannot be empty."
            )

        chunks = _split_text(
            narration,
            max_chars_per_cue=self.max_chars_per_cue,
        )

        if not chunks:
            raise SubtitleRenderError(
                f"Segment {segment.scene_number} produced no subtitle chunks."
            )

        duration = scene_end_seconds - scene_start_seconds
        cue_durations = self._cue_durations(chunks, duration)
        cues: list[SubtitleCue] = []
        cursor_seconds = scene_start_seconds

        for index, chunk in enumerate(chunks):
            start_seconds = cursor_seconds
            end_seconds = (
                scene_end_seconds
                if index == len(chunks) - 1
                else start_seconds + cue_durations[index]
            )

            if end_seconds <= start_seconds:
                raise SubtitleRenderError(
                    f"Invalid subtitle timing for segment "
                    f"{segment.scene_number}."
                )

            cues.append(
                SubtitleCue(
                    scene_number=segment.scene_number,
                    cue_number=cue_offset + index + 1,
                    start_seconds=round(start_seconds, 3),
                    end_seconds=round(end_seconds, 3),
                    text=chunk,
                )
            )
            cursor_seconds = end_seconds

        return cues

    def _cue_durations(
        self,
        chunks: list[str],
        total_duration_seconds: float,
    ) -> list[float]:
        minimum_duration = self.min_cue_seconds * len(chunks)

        if minimum_duration > total_duration_seconds:
            raise SubtitleRenderError(
                "Segment duration is too short for readable subtitle cues."
            )

        weights = [max(1, len(chunk.split())) for chunk in chunks]
        total_weight = sum(weights)
        distributable_duration = total_duration_seconds - minimum_duration

        return [
            self.min_cue_seconds
            + (distributable_duration * weight / total_weight)
            for weight in weights
        ]

    @staticmethod
    def _validated_duration(segment: _SubtitleSourceSegment) -> float:
        if segment.duration_seconds <= 0:
            raise ValueError(
                f"Segment {segment.scene_number} duration must be positive."
            )

        return float(segment.duration_seconds)


def _segment_from_narration_segment(
    segment: NarrationSegment,
) -> _SubtitleSourceSegment:
    return _SubtitleSourceSegment(
        scene_number=segment.scene_number,
        duration_seconds=segment.duration_seconds,
        text=segment.text,
        purpose=segment.purpose,
    )


def _segment_from_voice_track_segment(
    segment: VoiceTrackSegment,
) -> _SubtitleSourceSegment:
    return _SubtitleSourceSegment(
        scene_number=segment.scene_number,
        duration_seconds=segment.duration_seconds,
        text=segment.narration,
        purpose=segment.purpose,
    )


def _normalize_text(value: str) -> str:
    return " ".join(value.split())


def _split_text(
    text: str,
    *,
    max_chars_per_cue: int,
) -> list[str]:
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text)
        if sentence.strip()
    ]

    chunks: list[str] = []

    for sentence in sentences:
        words = sentence.split()
        current: list[str] = []

        for word in words:
            candidate = " ".join([*current, word])

            if current and len(candidate) > max_chars_per_cue:
                chunks.append(" ".join(current))
                current = [word]
            else:
                current.append(word)

        if current:
            chunks.append(" ".join(current))

    return chunks
