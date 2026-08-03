from __future__ import annotations

from typing import NamedTuple

from applications.ai_money_factory.core.video_intelligence.models import (
    NarrativeBeat,
    SelectedTimelineClip,
)

PURPOSE_ORDER = ("HOOK", "POUR", "MACRO", "PRODUCT", "CTA")
TIMING_TOLERANCE_SECONDS = 0.001


class NarrativePolicy(NamedTuple):
    emotion: str
    narration_intent: str
    pacing: str
    voice_energy: str
    subtitle_emphasis: str
    transition_style: str


NARRATIVE_POLICIES = {
    "HOOK": NarrativePolicy(
        emotion="curiosity",
        narration_intent="pattern_interrupt",
        pacing="fast",
        voice_energy="high",
        subtitle_emphasis="strong",
        transition_style="hard_cut",
    ),
    "POUR": NarrativePolicy(
        emotion="craving",
        narration_intent="demonstrate_action",
        pacing="medium_fast",
        voice_energy="high",
        subtitle_emphasis="medium",
        transition_style="match_cut",
    ),
    "MACRO": NarrativePolicy(
        emotion="desire",
        narration_intent="describe_texture",
        pacing="medium",
        voice_energy="warm",
        subtitle_emphasis="medium",
        transition_style="smooth_cut",
    ),
    "PRODUCT": NarrativePolicy(
        emotion="trust",
        narration_intent="reveal_product",
        pacing="medium",
        voice_energy="clear",
        subtitle_emphasis="strong",
        transition_style="clean_cut",
    ),
    "CTA": NarrativePolicy(
        emotion="urgency",
        narration_intent="prompt_action",
        pacing="medium_fast",
        voice_energy="high",
        subtitle_emphasis="strong",
        transition_style="end_hold",
    ),
}


class NarrativeEngine:
    """
    Build deterministic narrative beats for an optimized short-form timeline.
    """

    def plan(
        self,
        clips: list[SelectedTimelineClip],
    ) -> list[NarrativeBeat]:
        _validate_clips(clips)

        return [
            _beat_from_clip(clip)
            for clip in clips
        ]


def _validate_clips(clips: list[SelectedTimelineClip]) -> None:
    if len(clips) != len(PURPOSE_ORDER):
        raise ValueError("narrative input must contain exactly five clips.")

    purposes = [clip.purpose for clip in clips]
    duplicate_purposes = [
        purpose
        for purpose in PURPOSE_ORDER
        if purposes.count(purpose) > 1
    ]

    if duplicate_purposes:
        raise ValueError(
            f"narrative input contains duplicate purpose {duplicate_purposes[0]}."
        )

    missing_purposes = sorted(set(PURPOSE_ORDER) - set(purposes))

    if missing_purposes:
        raise ValueError(f"narrative input is missing purpose {missing_purposes[0]}.")

    if purposes != list(PURPOSE_ORDER):
        raise ValueError(
            "narrative purpose order must be HOOK, POUR, MACRO, PRODUCT, CTA."
        )

    previous_end = 0.0

    for index, clip in enumerate(clips, start=1):
        if clip.output_end_seconds <= clip.output_start_seconds:
            raise ValueError(
                f"clip {index} output_end_seconds must be greater than "
                "output_start_seconds."
            )

        if abs(clip.output_start_seconds - previous_end) > TIMING_TOLERANCE_SECONDS:
            relation = "gap" if clip.output_start_seconds > previous_end else "overlap"
            raise ValueError(f"timeline has a timing {relation} before clip {index}.")

        actual_duration = clip.output_end_seconds - clip.output_start_seconds

        if abs(actual_duration - clip.target_duration_seconds) > TIMING_TOLERANCE_SECONDS:
            raise ValueError(
                f"clip {index} target_duration_seconds must equal output duration."
            )

        confidence = _confidence(clip)

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"clip {index} confidence must be between 0.0 and 1.0.")

        previous_end = clip.output_end_seconds


def _beat_from_clip(clip: SelectedTimelineClip) -> NarrativeBeat:
    policy = NARRATIVE_POLICIES[clip.purpose]

    return NarrativeBeat(
        scene_number=clip.scene_number,
        purpose=clip.purpose,
        output_start_seconds=clip.output_start_seconds,
        output_end_seconds=clip.output_end_seconds,
        target_duration_seconds=clip.target_duration_seconds,
        emotion=policy.emotion,
        narration_intent=policy.narration_intent,
        pacing=policy.pacing,
        voice_energy=policy.voice_energy,
        subtitle_emphasis=policy.subtitle_emphasis,
        transition_style=policy.transition_style,
        confidence=_confidence(clip),
    )


def _confidence(clip: SelectedTimelineClip) -> float:
    confidence = clip.confidence

    if clip.target_duration_seconds < 1.5:
        confidence -= 0.10

    if clip.requires_crop:
        confidence -= 0.10

    if clip.subtitle_safe_zone == "center":
        confidence -= 0.05

    if clip.score < 60:
        confidence -= 0.05

    return min(1.0, max(0.0, round(confidence, 6)))
