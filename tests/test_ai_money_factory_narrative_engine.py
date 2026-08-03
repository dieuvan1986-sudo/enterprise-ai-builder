from __future__ import annotations

from pathlib import Path

import pytest

from applications.ai_money_factory.core.video_intelligence import (
    NarrativeBeat,
    NarrativeEngine,
    SelectedTimelineClip,
)


def test_plans_successful_five_beat_narrative() -> None:
    beats = NarrativeEngine().plan(_clips())

    assert len(beats) == 5
    assert [beat.purpose for beat in beats] == [
        "HOOK",
        "POUR",
        "MACRO",
        "PRODUCT",
        "CTA",
    ]


def test_preserves_exact_purpose_order() -> None:
    beats = NarrativeEngine().plan(_clips())

    assert [beat.purpose for beat in beats] == [
        "HOOK",
        "POUR",
        "MACRO",
        "PRODUCT",
        "CTA",
    ]


def test_applies_deterministic_policy_for_every_purpose() -> None:
    beats = NarrativeEngine().plan(_clips())

    assert beats == [
        _beat(
            scene_number=1,
            purpose="HOOK",
            start=0.0,
            end=2.0,
            emotion="curiosity",
            narration_intent="pattern_interrupt",
            pacing="fast",
            voice_energy="high",
            subtitle_emphasis="strong",
            transition_style="hard_cut",
        ),
        _beat(
            scene_number=2,
            purpose="POUR",
            start=2.0,
            end=4.5,
            emotion="craving",
            narration_intent="demonstrate_action",
            pacing="medium_fast",
            voice_energy="high",
            subtitle_emphasis="medium",
            transition_style="match_cut",
        ),
        _beat(
            scene_number=3,
            purpose="MACRO",
            start=4.5,
            end=7.0,
            emotion="desire",
            narration_intent="describe_texture",
            pacing="medium",
            voice_energy="warm",
            subtitle_emphasis="medium",
            transition_style="smooth_cut",
        ),
        _beat(
            scene_number=4,
            purpose="PRODUCT",
            start=7.0,
            end=10.0,
            emotion="trust",
            narration_intent="reveal_product",
            pacing="medium",
            voice_energy="clear",
            subtitle_emphasis="strong",
            transition_style="clean_cut",
        ),
        _beat(
            scene_number=5,
            purpose="CTA",
            start=10.0,
            end=13.0,
            emotion="urgency",
            narration_intent="prompt_action",
            pacing="medium_fast",
            voice_energy="high",
            subtitle_emphasis="strong",
            transition_style="end_hold",
        ),
    ]


def test_preserves_timing() -> None:
    clips = _clips()
    beats = NarrativeEngine().plan(clips)

    assert [
        (
            beat.output_start_seconds,
            beat.output_end_seconds,
            beat.target_duration_seconds,
        )
        for beat in beats
    ] == [
        (
            clip.output_start_seconds,
            clip.output_end_seconds,
            clip.target_duration_seconds,
        )
        for clip in clips
    ]


def test_preserves_scene_numbers() -> None:
    beats = NarrativeEngine().plan(_clips(scene_numbers=[9, 3, 7, 1, 5]))

    assert [beat.scene_number for beat in beats] == [9, 3, 7, 1, 5]


def test_inherits_confidence_from_clip() -> None:
    beats = NarrativeEngine().plan(_clips(confidences={1: 0.77}))

    assert beats[0].confidence == 0.77


def test_applies_confidence_penalty_for_short_clip() -> None:
    beats = NarrativeEngine().plan(_clips(durations={1: 1.25}))

    assert beats[0].confidence == 0.9


def test_applies_confidence_penalty_for_requires_crop() -> None:
    beats = NarrativeEngine().plan(_clips(requires_crop={1: True}))

    assert beats[0].confidence == 0.9


def test_applies_confidence_penalty_for_center_subtitle_zone() -> None:
    beats = NarrativeEngine().plan(_clips(subtitle_safe_zones={1: "center"}))

    assert beats[0].confidence == 0.95


def test_applies_confidence_penalty_for_low_score() -> None:
    beats = NarrativeEngine().plan(_clips(scores={1: 59}))

    assert beats[0].confidence == 0.95


def test_confidence_clamps_to_zero_and_one() -> None:
    beats = NarrativeEngine().plan(
        _clips(
            durations={1: 1.25},
            requires_crop={1: True},
            subtitle_safe_zones={1: "center"},
            scores={1: 59},
            confidences={1: 0.1},
        )
    )

    assert beats[0].confidence == 0.0
    assert all(0.0 <= beat.confidence <= 1.0 for beat in beats)


def test_missing_purpose_raises_value_error() -> None:
    clips = _clips()
    clips[2] = _clip(3, "EXTRA", start=4.5, duration=2.5)

    with pytest.raises(ValueError, match="missing purpose MACRO"):
        NarrativeEngine().plan(clips)


def test_duplicate_purpose_raises_value_error() -> None:
    clips = _clips()
    clips[1] = _clip(2, "HOOK", start=2.0, duration=2.5)

    with pytest.raises(ValueError, match="duplicate purpose HOOK"):
        NarrativeEngine().plan(clips)


def test_incorrect_order_raises_value_error() -> None:
    clips = _clips()
    clips[1], clips[2] = clips[2], clips[1]

    with pytest.raises(ValueError, match="purpose order"):
        NarrativeEngine().plan(clips)


def test_timing_gap_raises_value_error() -> None:
    clips = _clips(starts={2: 2.25})

    with pytest.raises(ValueError, match="timing gap"):
        NarrativeEngine().plan(clips)


def test_timing_overlap_raises_value_error() -> None:
    clips = _clips(starts={2: 1.75})

    with pytest.raises(ValueError, match="timing overlap"):
        NarrativeEngine().plan(clips)


def test_invalid_duration_raises_value_error() -> None:
    clips = _clips(durations={1: 0})

    with pytest.raises(ValueError, match="greater than output_start_seconds"):
        NarrativeEngine().plan(clips)


def test_incorrect_target_duration_relationship_raises_value_error() -> None:
    clips = _clips(target_durations={1: 1.5})

    with pytest.raises(ValueError, match="target_duration_seconds"):
        NarrativeEngine().plan(clips)


def _clips(
    *,
    scene_numbers: list[int] | None = None,
    starts: dict[int, float] | None = None,
    durations: dict[int, float] | None = None,
    target_durations: dict[int, float] | None = None,
    requires_crop: dict[int, bool] | None = None,
    subtitle_safe_zones: dict[int, str] | None = None,
    scores: dict[int, float] | None = None,
    confidences: dict[int, float] | None = None,
) -> list[SelectedTimelineClip]:
    purposes = ["HOOK", "POUR", "MACRO", "PRODUCT", "CTA"]
    default_durations = [2.0, 2.5, 2.5, 3.0, 3.0]
    scene_numbers = scene_numbers or [1, 2, 3, 4, 5]
    starts = starts or {}
    durations = durations or {}
    target_durations = target_durations or {}
    requires_crop = requires_crop or {}
    subtitle_safe_zones = subtitle_safe_zones or {}
    scores = scores or {}
    confidences = confidences or {}
    continuous_start = 0.0
    clips = []

    for index, purpose in enumerate(purposes):
        scene_number = scene_numbers[index]
        duration = durations.get(scene_number, default_durations[index])
        start = starts.get(scene_number, continuous_start)
        clips.append(
            _clip(
                scene_number=scene_number,
                purpose=purpose,
                start=start,
                duration=duration,
                target_duration=target_durations.get(scene_number, duration),
                requires_crop=requires_crop.get(scene_number, False),
                subtitle_safe_zone=subtitle_safe_zones.get(
                    scene_number,
                    "bottom",
                ),
                score=scores.get(scene_number, 80),
                confidence=confidences.get(scene_number, 1.0),
            )
        )
        continuous_start = start + duration

    return clips


def _clip(
    scene_number: int,
    purpose: str,
    *,
    start: float,
    duration: float,
    target_duration: float | None = None,
    requires_crop: bool = False,
    subtitle_safe_zone: str = "bottom",
    score: float = 80,
    confidence: float = 1.0,
) -> SelectedTimelineClip:
    target_duration = target_duration if target_duration is not None else duration

    return SelectedTimelineClip(
        scene_number=scene_number,
        source_path=Path("source.mp4"),
        source_start_seconds=scene_number * 10.0,
        source_end_seconds=scene_number * 10.0 + duration,
        output_start_seconds=start,
        output_end_seconds=start + duration,
        duration_seconds=duration,
        target_duration_seconds=target_duration,
        purpose=purpose,
        score=score,
        watermark="croppable" if requires_crop else "none",
        subtitle_safe_zone=subtitle_safe_zone,
        requires_crop=requires_crop,
        confidence=confidence,
    )


def _beat(
    *,
    scene_number: int,
    purpose: str,
    start: float,
    end: float,
    emotion: str,
    narration_intent: str,
    pacing: str,
    voice_energy: str,
    subtitle_emphasis: str,
    transition_style: str,
    confidence: float = 1.0,
) -> NarrativeBeat:
    return NarrativeBeat(
        scene_number=scene_number,
        purpose=purpose,
        output_start_seconds=start,
        output_end_seconds=end,
        target_duration_seconds=end - start,
        emotion=emotion,
        narration_intent=narration_intent,
        pacing=pacing,
        voice_energy=voice_energy,
        subtitle_emphasis=subtitle_emphasis,
        transition_style=transition_style,
        confidence=confidence,
    )
