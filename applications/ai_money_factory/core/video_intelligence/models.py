from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SourceVideo:
    """
    Metadata for one caller-provided source video.
    """

    path: Path
    duration_seconds: float
    width: int
    height: int
    fps: float


@dataclass(slots=True)
class DetectedScene:
    """
    One detected source-video scene with exact source timestamps.
    """

    source_path: Path
    scene_number: int
    start_seconds: float
    end_seconds: float
    duration_seconds: float


@dataclass(slots=True)
class ScoredScene:
    """
    Rule-based review score for a detected scene.
    """

    scene_number: int
    score: float
    eligible: bool
    purposes: list[str]
    rejection_reasons: list[str]


@dataclass(slots=True)
class SelectedTimelineClip:
    """
    Planned output clip selected from a source scene.
    """

    scene_number: int
    source_path: Path
    source_start_seconds: float
    source_end_seconds: float
    output_start_seconds: float
    output_end_seconds: float
    duration_seconds: float
    target_duration_seconds: float
    purpose: str
    score: float
    watermark: str
    subtitle_safe_zone: str
    requires_crop: bool
    confidence: float


@dataclass(slots=True)
class NarrativeBeat:
    """
    Semantic narrative plan for one selected timeline clip.
    """

    scene_number: int
    purpose: str
    output_start_seconds: float
    output_end_seconds: float
    target_duration_seconds: float
    emotion: str
    narration_intent: str
    pacing: str
    voice_energy: str
    subtitle_emphasis: str
    transition_style: str
    confidence: float


@dataclass(slots=True)
class VoiceSegmentPlan:
    """
    Deterministic voice plan for one narrative beat.
    """

    scene_number: int
    purpose: str
    start_seconds: float
    end_seconds: float
    duration_seconds: float
    language: str
    gender: str
    accent: str
    voice_id: str
    speech_rate: float
    pause_before_seconds: float
    pause_after_seconds: float
    max_words: int
    energy: str
    narration_intent: str
    confidence: float


@dataclass(slots=True)
class SubtitleSegmentPlan:
    """
    Deterministic subtitle layout plan for one voice segment.
    """

    scene_number: int
    purpose: str
    start_seconds: float
    end_seconds: float
    duration_seconds: float
    safe_zone: str
    anchor: str
    max_chars_per_line: int
    max_lines: int
    font_scale: float
    emphasis: str
    animation_hint: str
    background_style: str
    avoid_center_subject: bool
    confidence: float


@dataclass(slots=True)
class CompositionSegmentPlan:
    """
    Deterministic composition readiness plan for one timeline segment.
    """

    scene_number: int
    purpose: str
    source_path: Path
    source_start_seconds: float
    source_end_seconds: float
    output_start_seconds: float
    output_end_seconds: float
    duration_seconds: float
    target_duration_seconds: float
    voice_start_seconds: float
    voice_end_seconds: float
    subtitle_start_seconds: float
    subtitle_end_seconds: float
    language: str
    gender: str
    accent: str
    voice_id: str
    subtitle_anchor: str
    subtitle_max_lines: int
    watermark: str
    crop_required: bool
    render_ready: bool
    blocking_reasons: list[str]
    confidence: float


@dataclass(slots=True)
class CompositionPlan:
    """
    Deterministic composition plan for a vertical short-form video.
    """

    segments: list[CompositionSegmentPlan]
    total_duration_seconds: float
    render_ready: bool
    blocking_reasons: list[str]
    target_width: int
    target_height: int
    fps: int
    video_codec: str
    audio_codec: str
    pixel_format: str
    confidence: float
