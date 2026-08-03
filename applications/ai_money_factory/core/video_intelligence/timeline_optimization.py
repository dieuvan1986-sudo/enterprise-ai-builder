from __future__ import annotations

from dataclasses import replace
from typing import NamedTuple

from applications.ai_money_factory.core.video_intelligence.models import (
    SelectedTimelineClip,
)

PURPOSE_ORDER = ("HOOK", "POUR", "MACRO", "PRODUCT", "CTA")
SAFE_WATERMARKS = {"none", "minor", "croppable"}
UNSAFE_WATERMARKS = {"major", "center", "reject"}


class DurationPolicy(NamedTuple):
    preferred_seconds: float
    minimum_seconds: float
    maximum_seconds: float


DURATION_POLICIES = {
    "HOOK": DurationPolicy(
        preferred_seconds=2.0,
        minimum_seconds=1.5,
        maximum_seconds=2.5,
    ),
    "POUR": DurationPolicy(
        preferred_seconds=2.5,
        minimum_seconds=1.8,
        maximum_seconds=3.0,
    ),
    "MACRO": DurationPolicy(
        preferred_seconds=2.5,
        minimum_seconds=1.8,
        maximum_seconds=3.0,
    ),
    "PRODUCT": DurationPolicy(
        preferred_seconds=3.0,
        minimum_seconds=2.0,
        maximum_seconds=3.5,
    ),
    "CTA": DurationPolicy(
        preferred_seconds=3.0,
        minimum_seconds=2.0,
        maximum_seconds=3.5,
    ),
}


class TimelineOptimizationEngine:
    """
    Produce a deterministic short-form output timing plan from selected clips.
    """

    def optimize(
        self,
        clips: list[SelectedTimelineClip],
    ) -> list[SelectedTimelineClip]:
        _validate_clips(clips)

        optimized_clips: list[SelectedTimelineClip] = []
        output_start = 0.0

        for clip in clips:
            policy = DURATION_POLICIES[clip.purpose]
            target_duration = _target_duration(clip, policy)
            output_end = output_start + target_duration
            watermark = _watermark(clip)

            optimized_clips.append(
                replace(
                    clip,
                    output_start_seconds=output_start,
                    output_end_seconds=output_end,
                    target_duration_seconds=target_duration,
                    requires_crop=watermark == "croppable",
                    confidence=_confidence(clip, policy),
                )
            )
            output_start = output_end

        if output_start <= 0:
            raise ValueError("total target duration must be greater than 0.")

        if output_start > sum(clip.duration_seconds for clip in clips):
            raise ValueError("total target duration cannot exceed source durations.")

        return optimized_clips


def _validate_clips(clips: list[SelectedTimelineClip]) -> None:
    if len(clips) != len(PURPOSE_ORDER):
        raise ValueError("timeline must contain exactly five clips.")

    purposes = [clip.purpose for clip in clips]

    duplicate_purposes = [
        purpose
        for purpose in PURPOSE_ORDER
        if purposes.count(purpose) > 1
    ]

    if duplicate_purposes:
        raise ValueError(f"timeline contains duplicate purpose {duplicate_purposes[0]}.")

    missing_purposes = sorted(set(PURPOSE_ORDER) - set(purposes))

    if missing_purposes:
        raise ValueError(f"timeline is missing purpose {missing_purposes[0]}.")

    if purposes != list(PURPOSE_ORDER):
        raise ValueError(
            "timeline purpose order must be HOOK, POUR, MACRO, PRODUCT, CTA."
        )

    for clip in clips:
        if clip.duration_seconds <= 0:
            raise ValueError(f"scene {clip.scene_number} duration must be positive.")

        if clip.source_end_seconds <= clip.source_start_seconds:
            raise ValueError(f"scene {clip.scene_number} source end must be after start.")

        _watermark(clip)


def _target_duration(
    clip: SelectedTimelineClip,
    policy: DurationPolicy,
) -> float:
    if clip.duration_seconds >= policy.preferred_seconds:
        return policy.preferred_seconds

    return clip.duration_seconds


def _watermark(clip: SelectedTimelineClip) -> str:
    if clip.watermark in UNSAFE_WATERMARKS:
        raise ValueError(
            f"scene {clip.scene_number} watermark {clip.watermark} is not selectable."
        )

    if clip.watermark not in SAFE_WATERMARKS:
        raise ValueError(f"scene {clip.scene_number} watermark is unsupported.")

    return clip.watermark


def _confidence(
    clip: SelectedTimelineClip,
    policy: DurationPolicy,
) -> float:
    confidence = 1.0

    if clip.duration_seconds < policy.minimum_seconds:
        confidence -= 0.20

    if clip.watermark == "croppable":
        confidence -= 0.10
    elif clip.watermark == "minor":
        confidence -= 0.05

    if clip.subtitle_safe_zone == "center":
        confidence -= 0.10

    if clip.score < 60:
        confidence -= 0.05

    return min(1.0, max(0.0, round(confidence, 6)))
