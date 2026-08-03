from __future__ import annotations

from typing import NamedTuple

from applications.ai_money_factory.core.video_intelligence.models import (
    NarrativeBeat,
    SelectedTimelineClip,
    SubtitleSegmentPlan,
    VoiceSegmentPlan,
)

PURPOSE_ORDER = ("HOOK", "POUR", "MACRO", "PRODUCT", "CTA")
TIMING_TOLERANCE_SECONDS = 0.001
SAFE_ZONES = {"top", "bottom", "left", "right", "center"}
ANCHORS = {
    "top": "top_center",
    "bottom": "bottom_center",
    "left": "middle_left",
    "right": "middle_right",
    "center": "top_center",
}


class SubtitlePolicy(NamedTuple):
    max_chars_per_line: int
    max_lines: int
    font_scale: float
    emphasis: str
    animation_hint: str
    background_style: str


SUBTITLE_POLICIES = {
    "HOOK": SubtitlePolicy(
        max_chars_per_line=18,
        max_lines=2,
        font_scale=0.82,
        emphasis="strong",
        animation_hint="quick_pop",
        background_style="compact_box",
    ),
    "POUR": SubtitlePolicy(
        max_chars_per_line=20,
        max_lines=2,
        font_scale=0.76,
        emphasis="medium",
        animation_hint="fade_up",
        background_style="compact_box",
    ),
    "MACRO": SubtitlePolicy(
        max_chars_per_line=20,
        max_lines=2,
        font_scale=0.72,
        emphasis="medium",
        animation_hint="soft_fade",
        background_style="minimal_shadow",
    ),
    "PRODUCT": SubtitlePolicy(
        max_chars_per_line=22,
        max_lines=2,
        font_scale=0.76,
        emphasis="strong",
        animation_hint="clean_reveal",
        background_style="compact_box",
    ),
    "CTA": SubtitlePolicy(
        max_chars_per_line=18,
        max_lines=2,
        font_scale=0.80,
        emphasis="strong",
        animation_hint="pulse_once",
        background_style="compact_box",
    ),
}


class SubtitlePlanner:
    """
    Build deterministic mobile-safe Vietnamese subtitle layout plans.
    """

    def plan(
        self,
        beats: list[NarrativeBeat],
        voice_segments: list[VoiceSegmentPlan],
        clips: list[SelectedTimelineClip],
    ) -> list[SubtitleSegmentPlan]:
        _validate_inputs(beats, voice_segments, clips)

        plans = [
            _subtitle_segment_from_records(beat, voice_segment, clip)
            for beat, voice_segment, clip in zip(
                beats,
                voice_segments,
                clips,
                strict=True,
            )
        ]
        _validate_font_safety(plans)

        return plans


def _validate_inputs(
    beats: list[NarrativeBeat],
    voice_segments: list[VoiceSegmentPlan],
    clips: list[SelectedTimelineClip],
) -> None:
    _validate_collection("narrative beats", beats)
    _validate_collection("voice segments", voice_segments)
    _validate_collection("timeline clips", clips)
    _validate_record_alignment(beats, voice_segments, clips)
    _validate_timing(voice_segments)

    for clip in clips:
        if clip.subtitle_safe_zone not in SAFE_ZONES:
            raise ValueError(
                f"scene {clip.scene_number} safe_zone must be one of "
                "bottom, center, left, right, top."
            )

        if not 0.0 <= clip.confidence <= 1.0:
            raise ValueError(
                f"scene {clip.scene_number} clip confidence must be between 0.0 and 1.0."
            )

    for beat in beats:
        if not 0.0 <= beat.confidence <= 1.0:
            raise ValueError(
                f"scene {beat.scene_number} beat confidence must be between 0.0 and 1.0."
            )

    for segment in voice_segments:
        if not 0.0 <= segment.confidence <= 1.0:
            raise ValueError(
                "scene "
                f"{segment.scene_number} voice confidence must be between 0.0 and 1.0."
            )


def _validate_collection(
    label: str,
    records: list[NarrativeBeat] | list[VoiceSegmentPlan] | list[SelectedTimelineClip],
) -> None:
    if len(records) != len(PURPOSE_ORDER):
        raise ValueError(f"{label} must contain exactly five records.")

    purposes = [record.purpose for record in records]
    duplicate_purposes = [
        purpose
        for purpose in PURPOSE_ORDER
        if purposes.count(purpose) > 1
    ]

    if duplicate_purposes:
        raise ValueError(f"{label} contains duplicate purpose {duplicate_purposes[0]}.")

    missing_purposes = sorted(set(PURPOSE_ORDER) - set(purposes))

    if missing_purposes:
        raise ValueError(f"{label} is missing purpose {missing_purposes[0]}.")

    if purposes != list(PURPOSE_ORDER):
        raise ValueError(
            f"{label} purpose order must be HOOK, POUR, MACRO, PRODUCT, CTA."
        )


def _validate_record_alignment(
    beats: list[NarrativeBeat],
    voice_segments: list[VoiceSegmentPlan],
    clips: list[SelectedTimelineClip],
) -> None:
    for index, (beat, segment, clip) in enumerate(
        zip(beats, voice_segments, clips, strict=True),
        start=1,
    ):
        scene_numbers = {beat.scene_number, segment.scene_number, clip.scene_number}

        if len(scene_numbers) != 1:
            raise ValueError(f"record {index} scene_number values must match.")

        purposes = {beat.purpose, segment.purpose, clip.purpose}

        if len(purposes) != 1:
            raise ValueError(f"record {index} purpose values must match.")


def _validate_timing(voice_segments: list[VoiceSegmentPlan]) -> None:
    previous_end = 0.0

    for index, segment in enumerate(voice_segments, start=1):
        if segment.end_seconds <= segment.start_seconds:
            raise ValueError(
                f"voice segment {index} end_seconds must be greater than start_seconds."
            )

        if segment.duration_seconds <= 0:
            raise ValueError(f"voice segment {index} duration must be positive.")

        duration = segment.end_seconds - segment.start_seconds

        if abs(duration - segment.duration_seconds) > TIMING_TOLERANCE_SECONDS:
            raise ValueError(
                f"voice segment {index} duration_seconds must equal output duration."
            )

        if abs(segment.start_seconds - previous_end) > TIMING_TOLERANCE_SECONDS:
            relation = "gap" if segment.start_seconds > previous_end else "overlap"
            raise ValueError(
                f"subtitle timing has a timing {relation} before segment {index}."
            )

        previous_end = segment.end_seconds


def _subtitle_segment_from_records(
    beat: NarrativeBeat,
    voice_segment: VoiceSegmentPlan,
    clip: SelectedTimelineClip,
) -> SubtitleSegmentPlan:
    policy = SUBTITLE_POLICIES[beat.purpose]
    safe_zone = clip.subtitle_safe_zone

    return SubtitleSegmentPlan(
        scene_number=voice_segment.scene_number,
        purpose=voice_segment.purpose,
        start_seconds=voice_segment.start_seconds,
        end_seconds=voice_segment.end_seconds,
        duration_seconds=voice_segment.duration_seconds,
        safe_zone=safe_zone,
        anchor=ANCHORS[safe_zone],
        max_chars_per_line=policy.max_chars_per_line,
        max_lines=policy.max_lines,
        font_scale=policy.font_scale,
        emphasis=policy.emphasis,
        animation_hint=policy.animation_hint,
        background_style=policy.background_style,
        avoid_center_subject=True,
        confidence=_confidence(beat, voice_segment, clip, policy),
    )


def _confidence(
    beat: NarrativeBeat,
    voice_segment: VoiceSegmentPlan,
    clip: SelectedTimelineClip,
    policy: SubtitlePolicy,
) -> float:
    confidence = min(beat.confidence, voice_segment.confidence, clip.confidence)

    if clip.subtitle_safe_zone == "center":
        confidence -= 0.15

    if clip.requires_crop:
        confidence -= 0.10

    if policy.emphasis == "strong" and voice_segment.duration_seconds < 1.5:
        confidence -= 0.05

    if voice_segment.duration_seconds < 1.2:
        confidence -= 0.05

    return min(1.0, max(0.0, round(confidence, 6)))


def _validate_font_safety(plans: list[SubtitleSegmentPlan]) -> None:
    for plan in plans:
        if not 0.65 <= plan.font_scale <= 0.85:
            raise ValueError(
                f"subtitle segment {plan.scene_number} font_scale is outside safety bounds."
            )

        if plan.max_lines > 2:
            raise ValueError(
                f"subtitle segment {plan.scene_number} max_lines must not exceed 2."
            )

        if not 16 <= plan.max_chars_per_line <= 24:
            raise ValueError(
                "subtitle segment "
                f"{plan.scene_number} max_chars_per_line is outside safety bounds."
            )

        if plan.anchor == "center_center":
            raise ValueError(
                f"subtitle segment {plan.scene_number} anchor must not be center_center."
            )

        if not 0.0 <= plan.confidence <= 1.0:
            raise ValueError(
                f"subtitle segment {plan.scene_number} confidence must be between 0.0 and 1.0."
            )
