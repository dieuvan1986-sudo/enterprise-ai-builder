from __future__ import annotations

from dataclasses import dataclass, field


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
