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
