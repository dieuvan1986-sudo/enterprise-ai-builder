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
