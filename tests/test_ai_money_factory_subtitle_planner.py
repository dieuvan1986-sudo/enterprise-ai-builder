from __future__ import annotations

from pathlib import Path

import pytest

from applications.ai_money_factory.core.video_intelligence import (
    NarrativeBeat,
    SelectedTimelineClip,
    SubtitlePlanner,
    VoiceSegmentPlan,
)
from applications.ai_money_factory.core.video_intelligence import subtitle_planner


def test_plans_successful_five_segment_subtitle_plan() -> None:
    plans = SubtitlePlanner().plan(*_inputs())

    assert len(plans) == 5
    assert [plan.purpose for plan in plans] == ["HOOK", "POUR", "MACRO", "PRODUCT", "CTA"]


def test_preserves_exact_purpose_order() -> None:
    plans = SubtitlePlanner().plan(*_inputs())

    assert [plan.purpose for plan in plans] == ["HOOK", "POUR", "MACRO", "PRODUCT", "CTA"]


def test_maps_top_safe_zone_to_top_center() -> None:
    plans = SubtitlePlanner().plan(*_inputs(safe_zones={1: "top"}))

    assert plans[0].anchor == "top_center"


def test_maps_bottom_safe_zone_to_bottom_center() -> None:
    plans = SubtitlePlanner().plan(*_inputs(safe_zones={1: "bottom"}))

    assert plans[0].anchor == "bottom_center"


def test_maps_left_safe_zone_to_middle_left() -> None:
    plans = SubtitlePlanner().plan(*_inputs(safe_zones={1: "left"}))

    assert plans[0].anchor == "middle_left"


def test_maps_right_safe_zone_to_middle_right() -> None:
    plans = SubtitlePlanner().plan(*_inputs(safe_zones={1: "right"}))

    assert plans[0].anchor == "middle_right"


def test_center_safe_zone_maps_to_top_center() -> None:
    plans = SubtitlePlanner().plan(*_inputs(safe_zones={1: "center"}))

    assert plans[0].anchor == "top_center"


def test_center_safe_zone_never_maps_to_center_center() -> None:
    plans = SubtitlePlanner().plan(*_inputs(safe_zones={1: "center"}))

    assert plans[0].anchor != "center_center"


def test_sets_correct_font_scale_per_purpose() -> None:
    plans = SubtitlePlanner().plan(*_inputs())

    assert [plan.font_scale for plan in plans] == [0.82, 0.76, 0.72, 0.76, 0.80]


def test_sets_correct_max_chars_per_line() -> None:
    plans = SubtitlePlanner().plan(*_inputs())

    assert [plan.max_chars_per_line for plan in plans] == [18, 20, 20, 22, 18]


def test_max_lines_always_equals_two() -> None:
    plans = SubtitlePlanner().plan(*_inputs())

    assert [plan.max_lines for plan in plans] == [2, 2, 2, 2, 2]


def test_avoid_center_subject_is_always_true() -> None:
    plans = SubtitlePlanner().plan(*_inputs())

    assert all(plan.avoid_center_subject is True for plan in plans)


def test_preserves_timing_from_voice_segments() -> None:
    _, voice_segments, _ = _inputs()
    plans = SubtitlePlanner().plan(*_inputs())

    assert [
        (plan.start_seconds, plan.end_seconds, plan.duration_seconds)
        for plan in plans
    ] == [
        (segment.start_seconds, segment.end_seconds, segment.duration_seconds)
        for segment in voice_segments
    ]


def test_preserves_scene_numbers() -> None:
    plans = SubtitlePlanner().plan(*_inputs(scene_numbers=[8, 3, 5, 1, 9]))

    assert [plan.scene_number for plan in plans] == [8, 3, 5, 1, 9]


def test_confidence_uses_minimum_upstream_confidence() -> None:
    plans = SubtitlePlanner().plan(
        *_inputs(beat_confidences={1: 0.9}, voice_confidences={1: 0.7}, clip_confidences={1: 0.8})
    )

    assert plans[0].confidence == 0.7


def test_confidence_penalty_for_center_safe_zone() -> None:
    plans = SubtitlePlanner().plan(*_inputs(safe_zones={1: "center"}))

    assert plans[0].confidence == 0.85


def test_confidence_penalty_for_requires_crop() -> None:
    plans = SubtitlePlanner().plan(*_inputs(requires_crop={1: True}))

    assert plans[0].confidence == 0.9


def test_confidence_penalty_for_strong_emphasis_on_short_duration() -> None:
    plans = SubtitlePlanner().plan(*_inputs(durations={1: 1.4}))

    assert plans[0].confidence == 0.95


def test_confidence_penalty_for_duration_below_one_point_two_seconds() -> None:
    plans = SubtitlePlanner().plan(*_inputs(durations={2: 1.1}))

    assert plans[1].confidence == 0.95


def test_confidence_clamps_to_zero_and_one() -> None:
    plans = SubtitlePlanner().plan(
        *_inputs(
            durations={1: 1.1},
            safe_zones={1: "center"},
            requires_crop={1: True},
            beat_confidences={1: 0.1},
        )
    )

    assert plans[0].confidence == 0.0
    assert all(0.0 <= plan.confidence <= 1.0 for plan in plans)


def test_missing_purpose_raises_value_error() -> None:
    beats, voice_segments, clips = _inputs()
    beats[2] = _beat(3, "EXTRA", start=7.0, duration=4.0)

    with pytest.raises(ValueError, match="missing purpose MACRO"):
        SubtitlePlanner().plan(beats, voice_segments, clips)


def test_duplicate_purpose_raises_value_error() -> None:
    beats, voice_segments, clips = _inputs()
    voice_segments[1] = _voice_segment(2, "HOOK", start=3.0, duration=4.0)

    with pytest.raises(ValueError, match="duplicate purpose HOOK"):
        SubtitlePlanner().plan(beats, voice_segments, clips)


def test_incorrect_order_raises_value_error() -> None:
    beats, voice_segments, clips = _inputs()
    clips[1], clips[2] = clips[2], clips[1]

    with pytest.raises(ValueError, match="purpose order"):
        SubtitlePlanner().plan(beats, voice_segments, clips)


def test_mismatched_scene_number_raises_value_error() -> None:
    beats, voice_segments, clips = _inputs()
    clips[0] = _clip(9, "HOOK", start=0.0, duration=3.0)

    with pytest.raises(ValueError, match="scene_number values must match"):
        SubtitlePlanner().plan(beats, voice_segments, clips)


def test_mismatched_purpose_raises_value_error() -> None:
    beats, voice_segments, clips = _inputs()
    clips[0] = _clip(1, "POUR", start=0.0, duration=3.0)

    with pytest.raises(ValueError, match="duplicate purpose POUR"):
        SubtitlePlanner().plan(beats, voice_segments, clips)


def test_timing_gap_raises_value_error() -> None:
    beats, voice_segments, clips = _inputs(starts={2: 3.25})

    with pytest.raises(ValueError, match="timing gap"):
        SubtitlePlanner().plan(beats, voice_segments, clips)


def test_timing_overlap_raises_value_error() -> None:
    beats, voice_segments, clips = _inputs(starts={2: 2.75})

    with pytest.raises(ValueError, match="timing overlap"):
        SubtitlePlanner().plan(beats, voice_segments, clips)


def test_invalid_duration_raises_value_error() -> None:
    beats, voice_segments, clips = _inputs(durations={1: 0})

    with pytest.raises(ValueError, match="greater than start_seconds"):
        SubtitlePlanner().plan(beats, voice_segments, clips)


def test_invalid_safe_zone_raises_value_error() -> None:
    beats, voice_segments, clips = _inputs(safe_zones={1: "diagonal"})

    with pytest.raises(ValueError, match="safe_zone"):
        SubtitlePlanner().plan(beats, voice_segments, clips)


def test_font_safety_constraints_are_enforced(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    unsafe_policy = subtitle_planner.SubtitlePolicy(
        max_chars_per_line=30,
        max_lines=3,
        font_scale=1.0,
        emphasis="strong",
        animation_hint="quick_pop",
        background_style="compact_box",
    )
    patched_policies = {
        **subtitle_planner.SUBTITLE_POLICIES,
        "HOOK": unsafe_policy,
    }
    monkeypatch.setattr(subtitle_planner, "SUBTITLE_POLICIES", patched_policies)

    with pytest.raises(ValueError, match="font_scale"):
        SubtitlePlanner().plan(*_inputs())


def _inputs(
    *,
    scene_numbers: list[int] | None = None,
    starts: dict[int, float] | None = None,
    durations: dict[int, float] | None = None,
    safe_zones: dict[int, str] | None = None,
    requires_crop: dict[int, bool] | None = None,
    beat_confidences: dict[int, float] | None = None,
    voice_confidences: dict[int, float] | None = None,
    clip_confidences: dict[int, float] | None = None,
) -> tuple[list[NarrativeBeat], list[VoiceSegmentPlan], list[SelectedTimelineClip]]:
    purposes = ["HOOK", "POUR", "MACRO", "PRODUCT", "CTA"]
    default_durations = [3.0, 4.0, 4.0, 4.0, 4.0]
    scene_numbers = scene_numbers or [1, 2, 3, 4, 5]
    starts = starts or {}
    durations = durations or {}
    safe_zones = safe_zones or {}
    requires_crop = requires_crop or {}
    beat_confidences = beat_confidences or {}
    voice_confidences = voice_confidences or {}
    clip_confidences = clip_confidences or {}
    continuous_start = 0.0
    beats = []
    voice_segments = []
    clips = []

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
                confidence=beat_confidences.get(scene_number, 1.0),
            )
        )
        voice_segments.append(
            _voice_segment(
                scene_number,
                purpose,
                start=start,
                duration=duration,
                confidence=voice_confidences.get(scene_number, 1.0),
            )
        )
        clips.append(
            _clip(
                scene_number,
                purpose,
                start=start,
                duration=duration,
                safe_zone=safe_zones.get(scene_number, "bottom"),
                requires_crop=requires_crop.get(scene_number, False),
                confidence=clip_confidences.get(scene_number, 1.0),
            )
        )
        continuous_start = start + duration

    return beats, voice_segments, clips


def _beat(
    scene_number: int,
    purpose: str,
    *,
    start: float,
    duration: float,
    confidence: float = 1.0,
) -> NarrativeBeat:
    return NarrativeBeat(
        scene_number=scene_number,
        purpose=purpose,
        output_start_seconds=start,
        output_end_seconds=start + duration,
        target_duration_seconds=duration,
        emotion="emotion",
        narration_intent=f"{purpose.lower()}_intent",
        pacing="pacing",
        voice_energy="high",
        subtitle_emphasis="strong",
        transition_style="cut",
        confidence=confidence,
    )


def _voice_segment(
    scene_number: int,
    purpose: str,
    *,
    start: float,
    duration: float,
    confidence: float = 1.0,
) -> VoiceSegmentPlan:
    return VoiceSegmentPlan(
        scene_number=scene_number,
        purpose=purpose,
        start_seconds=start,
        end_seconds=start + duration,
        duration_seconds=duration,
        language="vi-VN",
        gender="female",
        accent="northern_standard",
        voice_id="vi-VN-HoaiMyNeural",
        speech_rate=1.0,
        pause_before_seconds=0.0,
        pause_after_seconds=0.0,
        max_words=8,
        energy="high",
        narration_intent=f"{purpose.lower()}_intent",
        confidence=confidence,
    )


def _clip(
    scene_number: int,
    purpose: str,
    *,
    start: float,
    duration: float,
    safe_zone: str = "bottom",
    requires_crop: bool = False,
    confidence: float = 1.0,
) -> SelectedTimelineClip:
    return SelectedTimelineClip(
        scene_number=scene_number,
        source_path=Path("source.mp4"),
        source_start_seconds=scene_number * 10.0,
        source_end_seconds=scene_number * 10.0 + duration,
        output_start_seconds=start,
        output_end_seconds=start + duration,
        duration_seconds=duration,
        target_duration_seconds=duration,
        purpose=purpose,
        score=80,
        watermark="croppable" if requires_crop else "none",
        subtitle_safe_zone=safe_zone,
        requires_crop=requires_crop,
        confidence=confidence,
    )
