from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ContentAngle:
    """
    A strategic angle for selling a product through short-form content.
    """

    name: str
    description: str
    target_audience: str
    pain_point: str
    promise: str


@dataclass(slots=True)
class VideoScript:
    """
    Structured script for a short-form affiliate video.
    """

    hook: str
    body: list[str]
    cta: str
    duration_seconds: int = 25


@dataclass(slots=True)
class VisualScene:
    """
    One scene in the AI video production plan.
    """

    order: int
    duration_seconds: int
    visual_prompt: str
    voiceover: str
    on_screen_text: str = ""


@dataclass(slots=True)
class VideoMission:
    """
    Complete production brief for one affiliate video.

    This object will later be consumed by:
    - AI image/video generators
    - voice generation
    - video renderer
    - Telegram approval
    - publishing pipeline
    """

    product_name: str
    angle: ContentAngle
    script: VideoScript
    scenes: list[VisualScene] = field(default_factory=list)

    caption: str = ""
    hashtags: list[str] = field(default_factory=list)
    affiliate_url: str | None = None


@dataclass(slots=True)
class NarrationSegment:
    """
    One timed narration segment for a short-form video.
    """

    scene_number: int
    duration_seconds: float
    text: str
    purpose: str = ""


@dataclass(slots=True)
class Narration:
    """
    Complete narration plan before voice audio is rendered.
    """

    title: str
    segments: list[NarrationSegment]
    total_duration_seconds: float | None = None


@dataclass(slots=True)
class VoiceTrackSegment:
    """
    One rendered voice segment with timing metadata.
    """

    scene_number: int
    duration_seconds: float
    narration: str
    purpose: str = ""
    audio_path: Path | None = None


@dataclass(slots=True)
class VoiceTrack:
    """
    Rendered voice track that can be aligned with subtitles.
    """

    title: str
    segments: list[VoiceTrackSegment]
    total_duration_seconds: float | None = None


@dataclass(slots=True)
class SubtitleCue:
    """
    One timed subtitle cue.
    """

    scene_number: int
    cue_number: int
    start_seconds: float
    end_seconds: float
    text: str


@dataclass(slots=True)
class SubtitleTrack:
    """
    Complete subtitle track for downstream video composition.
    """

    title: str
    total_duration_seconds: float
    cues: list[SubtitleCue]
