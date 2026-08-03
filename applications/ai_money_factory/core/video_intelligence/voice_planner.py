from __future__ import annotations

import math
from typing import NamedTuple

from applications.ai_money_factory.core.video_intelligence.models import (
    NarrativeBeat,
    VoiceSegmentPlan,
)

PURPOSE_ORDER = ("HOOK", "POUR", "MACRO", "PRODUCT", "CTA")
TIMING_TOLERANCE_SECONDS = 0.001
LANGUAGE = "vi-VN"
GENDER = "female"
ACCENT = "northern_standard"
VOICE_ID = "vi-VN-HoaiMyNeural"


class VoicePolicy(NamedTuple):
    speech_rate: float
    pause_before_seconds: float
    pause_after_seconds: float
    max_words: int


VOICE_POLICIES = {
    "HOOK": VoicePolicy(
        speech_rate=1.08,
        pause_before_seconds=0.0,
        pause_after_seconds=0.08,
        max_words=8,
    ),
    "POUR": VoicePolicy(
        speech_rate=1.03,
        pause_before_seconds=0.05,
        pause_after_seconds=0.08,
        max_words=10,
    ),
    "MACRO": VoicePolicy(
        speech_rate=0.98,
        pause_before_seconds=0.05,
        pause_after_seconds=0.10,
        max_words=11,
    ),
    "PRODUCT": VoicePolicy(
        speech_rate=0.96,
        pause_before_seconds=0.08,
        pause_after_seconds=0.10,
        max_words=12,
    ),
    "CTA": VoicePolicy(
        speech_rate=1.04,
        pause_before_seconds=0.08,
        pause_after_seconds=0.0,
        max_words=10,
    ),
}


class VoicePlanner:
    """
    Build deterministic Vietnamese voice segment plans from narrative beats.
    """

    def plan(
        self,
        beats: list[NarrativeBeat],
    ) -> list[VoiceSegmentPlan]:
        _validate_beats(beats)

        plans = [
            _voice_segment_from_beat(beat)
            for beat in beats
        ]
        _validate_voice_safety(plans)

        return plans


def _validate_beats(beats: list[NarrativeBeat]) -> None:
    if len(beats) != len(PURPOSE_ORDER):
        raise ValueError("voice planner input must contain exactly five beats.")

    purposes = [beat.purpose for beat in beats]
    duplicate_purposes = [
        purpose
        for purpose in PURPOSE_ORDER
        if purposes.count(purpose) > 1
    ]

    if duplicate_purposes:
        raise ValueError(
            f"voice planner input contains duplicate purpose {duplicate_purposes[0]}."
        )

    missing_purposes = sorted(set(PURPOSE_ORDER) - set(purposes))

    if missing_purposes:
        raise ValueError(f"voice planner input is missing purpose {missing_purposes[0]}.")

    if purposes != list(PURPOSE_ORDER):
        raise ValueError(
            "voice planner purpose order must be HOOK, POUR, MACRO, PRODUCT, CTA."
        )

    previous_end = 0.0

    for index, beat in enumerate(beats, start=1):
        if beat.output_end_seconds <= beat.output_start_seconds:
            raise ValueError(
                f"beat {index} end_seconds must be greater than start_seconds."
            )

        if abs(beat.output_start_seconds - previous_end) > TIMING_TOLERANCE_SECONDS:
            relation = "gap" if beat.output_start_seconds > previous_end else "overlap"
            raise ValueError(f"voice timeline has a timing {relation} before beat {index}.")

        duration = beat.output_end_seconds - beat.output_start_seconds

        if duration <= 0:
            raise ValueError(f"beat {index} duration must be positive.")

        if not 0.0 <= beat.confidence <= 1.0:
            raise ValueError(f"beat {index} confidence must be between 0.0 and 1.0.")

        previous_end = beat.output_end_seconds


def _voice_segment_from_beat(beat: NarrativeBeat) -> VoiceSegmentPlan:
    policy = VOICE_POLICIES[beat.purpose]
    duration = beat.output_end_seconds - beat.output_start_seconds

    return VoiceSegmentPlan(
        scene_number=beat.scene_number,
        purpose=beat.purpose,
        start_seconds=beat.output_start_seconds,
        end_seconds=beat.output_end_seconds,
        duration_seconds=duration,
        language=LANGUAGE,
        gender=GENDER,
        accent=ACCENT,
        voice_id=VOICE_ID,
        speech_rate=policy.speech_rate,
        pause_before_seconds=policy.pause_before_seconds,
        pause_after_seconds=policy.pause_after_seconds,
        max_words=policy.max_words,
        energy=beat.voice_energy,
        narration_intent=beat.narration_intent,
        confidence=_confidence(beat, policy, duration),
    )


def _confidence(
    beat: NarrativeBeat,
    policy: VoicePolicy,
    duration: float,
) -> float:
    confidence = beat.confidence

    if duration < 1.5:
        confidence -= 0.10

    if policy.max_words > math.floor(duration * 3.0):
        confidence -= 0.05

    if beat.voice_energy == "high" and duration < 1.8:
        confidence -= 0.05

    return min(1.0, max(0.0, round(confidence, 6)))


def _validate_voice_safety(plans: list[VoiceSegmentPlan]) -> None:
    for plan in plans:
        if plan.language != LANGUAGE:
            raise ValueError("voice language must remain vi-VN.")

        if plan.gender != GENDER:
            raise ValueError("voice gender must remain female.")

        if plan.accent != ACCENT:
            raise ValueError("voice accent must remain northern_standard.")

        if plan.voice_id != VOICE_ID:
            raise ValueError("voice_id must remain vi-VN-HoaiMyNeural.")

        if not 0.0 <= plan.confidence <= 1.0:
            raise ValueError(
                f"voice segment {plan.scene_number} confidence must be between 0.0 and 1.0."
            )
