from __future__ import annotations

import pytest

from applications.ai_money_factory.core.video_intelligence import (
    NarrativeBeat,
    VoicePlanner,
)


def test_plans_successful_five_segment_voice_plan() -> None:
    plans = VoicePlanner().plan(_beats())

    assert len(plans) == 5
    assert [plan.purpose for plan in plans] == ["HOOK", "POUR", "MACRO", "PRODUCT", "CTA"]


def test_preserves_exact_purpose_order() -> None:
    plans = VoicePlanner().plan(_beats())

    assert [plan.purpose for plan in plans] == ["HOOK", "POUR", "MACRO", "PRODUCT", "CTA"]


def test_uses_locked_vietnamese_female_northern_voice_profile() -> None:
    plans = VoicePlanner().plan(_beats())

    assert {plan.language for plan in plans} == {"vi-VN"}
    assert {plan.gender for plan in plans} == {"female"}
    assert {plan.accent for plan in plans} == {"northern_standard"}


def test_voice_id_is_locked_to_hoai_my() -> None:
    plans = VoicePlanner().plan(_beats())

    assert {plan.voice_id for plan in plans} == {"vi-VN-HoaiMyNeural"}


def test_sets_correct_speech_rate_per_purpose() -> None:
    plans = VoicePlanner().plan(_beats())

    assert [plan.speech_rate for plan in plans] == [1.08, 1.03, 0.98, 0.96, 1.04]


def test_sets_correct_pauses_per_purpose() -> None:
    plans = VoicePlanner().plan(_beats())

    assert [
        (plan.pause_before_seconds, plan.pause_after_seconds)
        for plan in plans
    ] == [
        (0.0, 0.08),
        (0.05, 0.08),
        (0.05, 0.10),
        (0.08, 0.10),
        (0.08, 0.0),
    ]


def test_sets_correct_max_words_per_purpose() -> None:
    plans = VoicePlanner().plan(_beats())

    assert [plan.max_words for plan in plans] == [8, 10, 11, 12, 10]


def test_preserves_timing() -> None:
    beats = _beats()
    plans = VoicePlanner().plan(beats)

    assert [
        (plan.start_seconds, plan.end_seconds, plan.duration_seconds)
        for plan in plans
    ] == [
        (
            beat.output_start_seconds,
            beat.output_end_seconds,
            beat.output_end_seconds - beat.output_start_seconds,
        )
        for beat in beats
    ]


def test_preserves_scene_numbers() -> None:
    plans = VoicePlanner().plan(_beats(scene_numbers=[8, 3, 5, 1, 9]))

    assert [plan.scene_number for plan in plans] == [8, 3, 5, 1, 9]


def test_preserves_narration_intent() -> None:
    beats = _beats(narration_intents={1: "custom_hook"})
    plans = VoicePlanner().plan(beats)

    assert plans[0].narration_intent == "custom_hook"


def test_preserves_energy() -> None:
    beats = _beats(voice_energies={3: "warm"})
    plans = VoicePlanner().plan(beats)

    assert plans[2].energy == "warm"


def test_inherits_confidence() -> None:
    plans = VoicePlanner().plan(_beats(confidences={1: 0.77}))

    assert plans[0].confidence == 0.77


def test_applies_confidence_penalty_for_short_duration() -> None:
    plans = VoicePlanner().plan(_beats(durations={3: 1.25}))

    assert plans[2].confidence == 0.85


def test_applies_confidence_penalty_for_word_density_risk() -> None:
    plans = VoicePlanner().plan(_beats(durations={3: 3.5}))

    assert plans[2].confidence == 0.95


def test_applies_confidence_penalty_for_high_energy_short_duration() -> None:
    plans = VoicePlanner().plan(
        _beats(durations={1: 1.6}, voice_energies={1: "high"})
    )

    assert plans[0].confidence == 0.9


def test_confidence_clamps_to_zero_and_one() -> None:
    plans = VoicePlanner().plan(
        _beats(durations={1: 1.2}, voice_energies={1: "high"}, confidences={1: 0.1})
    )

    assert plans[0].confidence == 0.0
    assert all(0.0 <= plan.confidence <= 1.0 for plan in plans)


def test_missing_purpose_raises_value_error() -> None:
    beats = _beats()
    beats[2] = _beat(3, "EXTRA", start=4.5, duration=2.5)

    with pytest.raises(ValueError, match="missing purpose MACRO"):
        VoicePlanner().plan(beats)


def test_duplicate_purpose_raises_value_error() -> None:
    beats = _beats()
    beats[1] = _beat(2, "HOOK", start=2.0, duration=2.5)

    with pytest.raises(ValueError, match="duplicate purpose HOOK"):
        VoicePlanner().plan(beats)


def test_incorrect_order_raises_value_error() -> None:
    beats = _beats()
    beats[1], beats[2] = beats[2], beats[1]

    with pytest.raises(ValueError, match="purpose order"):
        VoicePlanner().plan(beats)


def test_timing_gap_raises_value_error() -> None:
    beats = _beats(starts={2: 3.25})

    with pytest.raises(ValueError, match="timing gap"):
        VoicePlanner().plan(beats)


def test_timing_overlap_raises_value_error() -> None:
    beats = _beats(starts={2: 2.75})

    with pytest.raises(ValueError, match="timing overlap"):
        VoicePlanner().plan(beats)


def test_invalid_duration_raises_value_error() -> None:
    beats = _beats(durations={1: 0})

    with pytest.raises(ValueError, match="greater than start_seconds"):
        VoicePlanner().plan(beats)


def _beats(
    *,
    scene_numbers: list[int] | None = None,
    starts: dict[int, float] | None = None,
    durations: dict[int, float] | None = None,
    narration_intents: dict[int, str] | None = None,
    voice_energies: dict[int, str] | None = None,
    confidences: dict[int, float] | None = None,
) -> list[NarrativeBeat]:
    purposes = ["HOOK", "POUR", "MACRO", "PRODUCT", "CTA"]
    default_durations = [3.0, 4.0, 4.0, 4.0, 4.0]
    default_voice_energies = {
        "HOOK": "high",
        "POUR": "high",
        "MACRO": "warm",
        "PRODUCT": "clear",
        "CTA": "high",
    }
    scene_numbers = scene_numbers or [1, 2, 3, 4, 5]
    starts = starts or {}
    durations = durations or {}
    narration_intents = narration_intents or {}
    voice_energies = voice_energies or {}
    confidences = confidences or {}
    continuous_start = 0.0
    beats = []

    for index, purpose in enumerate(purposes):
        scene_number = scene_numbers[index]
        duration = durations.get(scene_number, default_durations[index])
        start = starts.get(scene_number, continuous_start)
        beats.append(
            _beat(
                scene_number,
                purpose,
                start=start,
                duration=duration,
                narration_intent=narration_intents.get(
                    scene_number,
                    f"{purpose.lower()}_intent",
                ),
                voice_energy=voice_energies.get(
                    scene_number,
                    default_voice_energies[purpose],
                ),
                confidence=confidences.get(scene_number, 1.0),
            )
        )
        continuous_start = start + duration

    return beats


def _beat(
    scene_number: int,
    purpose: str,
    *,
    start: float,
    duration: float,
    narration_intent: str | None = None,
    voice_energy: str = "high",
    confidence: float = 1.0,
) -> NarrativeBeat:
    return NarrativeBeat(
        scene_number=scene_number,
        purpose=purpose,
        output_start_seconds=start,
        output_end_seconds=start + duration,
        target_duration_seconds=duration,
        emotion="emotion",
        narration_intent=narration_intent or f"{purpose.lower()}_intent",
        pacing="pacing",
        voice_energy=voice_energy,
        subtitle_emphasis="strong",
        transition_style="cut",
        confidence=confidence,
    )
