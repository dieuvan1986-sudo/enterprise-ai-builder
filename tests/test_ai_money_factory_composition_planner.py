from __future__ import annotations

from pathlib import Path

import pytest

from applications.ai_money_factory.core.video_intelligence import (
    CompositionPlanner,
    NarrativeBeat,
    SelectedTimelineClip,
    SubtitleSegmentPlan,
    VoiceSegmentPlan,
)


def test_plans_successful_composition() -> None:
    plan = CompositionPlanner().plan(*_inputs())

    assert len(plan.segments) == 5
    assert plan.render_ready is True
    assert plan.blocking_reasons == []
    assert plan.total_duration_seconds == 19.0


def test_uses_vertical_short_defaults() -> None:
    plan = CompositionPlanner().plan(*_inputs())

    assert plan.target_width == 1080
    assert plan.target_height == 1920
    assert plan.fps == 30
    assert plan.video_codec == "libx264"
    assert plan.audio_codec == "aac"
    assert plan.pixel_format == "yuv420p"


def test_preserves_purpose_order_and_scene_numbers() -> None:
    plan = CompositionPlanner().plan(*_inputs(scene_numbers=[8, 3, 5, 1, 9]))

    assert [segment.purpose for segment in plan.segments] == [
        "HOOK",
        "POUR",
        "MACRO",
        "PRODUCT",
        "CTA",
    ]
    assert [segment.scene_number for segment in plan.segments] == [8, 3, 5, 1, 9]


def test_preserves_source_and_output_timing() -> None:
    clips, _, _, _ = _inputs()
    plan = CompositionPlanner().plan(*_inputs())

    assert [
        (
            segment.source_start_seconds,
            segment.source_end_seconds,
            segment.output_start_seconds,
            segment.output_end_seconds,
            segment.target_duration_seconds,
        )
        for segment in plan.segments
    ] == [
        (
            clip.source_start_seconds,
            clip.source_end_seconds,
            clip.output_start_seconds,
            clip.output_end_seconds,
            clip.target_duration_seconds,
        )
        for clip in clips
    ]


def test_preserves_voice_and_subtitle_timing() -> None:
    _, _, voice_segments, subtitle_segments = _inputs()
    plan = CompositionPlanner().plan(*_inputs())

    assert [
        (
            segment.voice_start_seconds,
            segment.voice_end_seconds,
            segment.subtitle_start_seconds,
            segment.subtitle_end_seconds,
        )
        for segment in plan.segments
    ] == [
        (
            voice_segment.start_seconds,
            voice_segment.end_seconds,
            subtitle_segment.start_seconds,
            subtitle_segment.end_seconds,
        )
        for voice_segment, subtitle_segment in zip(
            voice_segments,
            subtitle_segments,
            strict=True,
        )
    ]


def test_voice_profile_remains_locked() -> None:
    plan = CompositionPlanner().plan(*_inputs())

    assert {segment.language for segment in plan.segments} == {"vi-VN"}
    assert {segment.gender for segment in plan.segments} == {"female"}
    assert {segment.accent for segment in plan.segments} == {"northern_standard"}
    assert {segment.voice_id for segment in plan.segments} == {"vi-VN-HoaiMyNeural"}


def test_invalid_voice_profile_raises_value_error() -> None:
    clips, beats, voice_segments, subtitle_segments = _inputs()
    voice_segments[0] = _voice_segment(1, "HOOK", start=0.0, duration=3.0, voice_id="bad")

    with pytest.raises(ValueError, match="vi-VN-HoaiMyNeural"):
        CompositionPlanner().plan(clips, beats, voice_segments, subtitle_segments)


def test_subtitles_remain_two_lines_and_not_center_center() -> None:
    plan = CompositionPlanner().plan(*_inputs())

    assert {segment.subtitle_max_lines for segment in plan.segments} == {2}
    assert "center_center" not in {segment.subtitle_anchor for segment in plan.segments}


def test_invalid_subtitle_anchor_raises_value_error() -> None:
    clips, beats, voice_segments, subtitle_segments = _inputs()
    subtitle_segments[0] = _subtitle_segment(
        1,
        "HOOK",
        start=0.0,
        duration=3.0,
        anchor="center_center",
    )

    with pytest.raises(ValueError, match="center_center"):
        CompositionPlanner().plan(clips, beats, voice_segments, subtitle_segments)


def test_unsafe_watermark_blocks_render_readiness() -> None:
    for watermark in ["major", "center", "reject"]:
        plan = CompositionPlanner().plan(*_inputs(watermarks={1: watermark}))

        assert plan.render_ready is False
        assert plan.segments[0].render_ready is False
        assert f"scene 1: unsafe watermark: {watermark}" in plan.blocking_reasons


def test_croppable_sets_crop_required_without_claiming_success() -> None:
    plan = CompositionPlanner().plan(*_inputs(watermarks={1: "croppable"}, requires_crop={1: True}))

    assert plan.render_ready is True
    assert plan.segments[0].crop_required is True
    assert plan.segments[0].blocking_reasons == []


def test_missing_purpose_raises_value_error() -> None:
    clips, beats, voice_segments, subtitle_segments = _inputs()
    beats[2] = _beat(3, "EXTRA", start=7.0, duration=4.0)

    with pytest.raises(ValueError, match="missing purpose MACRO"):
        CompositionPlanner().plan(clips, beats, voice_segments, subtitle_segments)


def test_duplicate_purpose_raises_value_error() -> None:
    clips, beats, voice_segments, subtitle_segments = _inputs()
    clips[1] = _clip(2, "HOOK", start=3.0, duration=4.0)

    with pytest.raises(ValueError, match="duplicate purpose HOOK"):
        CompositionPlanner().plan(clips, beats, voice_segments, subtitle_segments)


def test_incorrect_order_raises_value_error() -> None:
    clips, beats, voice_segments, subtitle_segments = _inputs()
    clips[1], clips[2] = clips[2], clips[1]

    with pytest.raises(ValueError, match="purpose order"):
        CompositionPlanner().plan(clips, beats, voice_segments, subtitle_segments)


def test_mismatched_scene_number_raises_value_error() -> None:
    clips, beats, voice_segments, subtitle_segments = _inputs()
    subtitle_segments[0] = _subtitle_segment(9, "HOOK", start=0.0, duration=3.0)

    with pytest.raises(ValueError, match="scene_number values must match"):
        CompositionPlanner().plan(clips, beats, voice_segments, subtitle_segments)


def test_mismatched_purpose_raises_value_error() -> None:
    clips, beats, voice_segments, subtitle_segments = _inputs()
    subtitle_segments[0] = _subtitle_segment(1, "POUR", start=0.0, duration=3.0)

    with pytest.raises(ValueError, match="duplicate purpose POUR"):
        CompositionPlanner().plan(clips, beats, voice_segments, subtitle_segments)


def test_timing_gap_raises_value_error() -> None:
    clips, beats, voice_segments, subtitle_segments = _inputs(starts={2: 3.25})

    with pytest.raises(ValueError, match="timing gap"):
        CompositionPlanner().plan(clips, beats, voice_segments, subtitle_segments)


def test_timing_overlap_raises_value_error() -> None:
    clips, beats, voice_segments, subtitle_segments = _inputs(starts={2: 2.75})

    with pytest.raises(ValueError, match="timing overlap"):
        CompositionPlanner().plan(clips, beats, voice_segments, subtitle_segments)


def test_invalid_clip_duration_raises_value_error() -> None:
    clips, beats, voice_segments, subtitle_segments = _inputs(durations={1: 0})

    with pytest.raises(ValueError, match="greater than output_start_seconds"):
        CompositionPlanner().plan(clips, beats, voice_segments, subtitle_segments)


def test_voice_timing_must_match_clip_timing() -> None:
    clips, beats, voice_segments, subtitle_segments = _inputs()
    voice_segments[0] = _voice_segment(1, "HOOK", start=0.1, duration=2.9)

    with pytest.raises(ValueError, match="voice segment 1 start_seconds must match"):
        CompositionPlanner().plan(clips, beats, voice_segments, subtitle_segments)


def test_confidence_uses_minimum_upstream_confidence() -> None:
    plan = CompositionPlanner().plan(
        *_inputs(
            clip_confidences={1: 0.8},
            beat_confidences={1: 0.7},
            voice_confidences={1: 0.9},
            subtitle_confidences={1: 0.6},
        )
    )

    assert plan.segments[0].confidence == 0.6
    assert plan.confidence == 0.6


def _inputs(
    *,
    scene_numbers: list[int] | None = None,
    starts: dict[int, float] | None = None,
    durations: dict[int, float] | None = None,
    watermarks: dict[int, str] | None = None,
    requires_crop: dict[int, bool] | None = None,
    clip_confidences: dict[int, float] | None = None,
    beat_confidences: dict[int, float] | None = None,
    voice_confidences: dict[int, float] | None = None,
    subtitle_confidences: dict[int, float] | None = None,
) -> tuple[
    list[SelectedTimelineClip],
    list[NarrativeBeat],
    list[VoiceSegmentPlan],
    list[SubtitleSegmentPlan],
]:
    purposes = ["HOOK", "POUR", "MACRO", "PRODUCT", "CTA"]
    default_durations = [3.0, 4.0, 4.0, 4.0, 4.0]
    scene_numbers = scene_numbers or [1, 2, 3, 4, 5]
    starts = starts or {}
    durations = durations or {}
    watermarks = watermarks or {}
    requires_crop = requires_crop or {}
    clip_confidences = clip_confidences or {}
    beat_confidences = beat_confidences or {}
    voice_confidences = voice_confidences or {}
    subtitle_confidences = subtitle_confidences or {}
    continuous_start = 0.0
    clips = []
    beats = []
    voice_segments = []
    subtitle_segments = []

    for index, purpose in enumerate(purposes):
        scene_number = scene_numbers[index]
        duration = durations.get(scene_number, default_durations[index])
        start = starts.get(scene_number, continuous_start)
        watermark = watermarks.get(scene_number, "none")
        crop_required = requires_crop.get(scene_number, watermark == "croppable")
        clips.append(
            _clip(
                scene_number,
                purpose,
                start=start,
                duration=duration,
                watermark=watermark,
                requires_crop=crop_required,
                confidence=clip_confidences.get(scene_number, 1.0),
            )
        )
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
        subtitle_segments.append(
            _subtitle_segment(
                scene_number,
                purpose,
                start=start,
                duration=duration,
                confidence=subtitle_confidences.get(scene_number, 1.0),
            )
        )
        continuous_start = start + duration

    return clips, beats, voice_segments, subtitle_segments


def _clip(
    scene_number: int,
    purpose: str,
    *,
    start: float,
    duration: float,
    watermark: str = "none",
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
        watermark=watermark,
        subtitle_safe_zone="bottom",
        requires_crop=requires_crop,
        confidence=confidence,
    )


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
    language: str = "vi-VN",
    gender: str = "female",
    accent: str = "northern_standard",
    voice_id: str = "vi-VN-HoaiMyNeural",
    confidence: float = 1.0,
) -> VoiceSegmentPlan:
    return VoiceSegmentPlan(
        scene_number=scene_number,
        purpose=purpose,
        start_seconds=start,
        end_seconds=start + duration,
        duration_seconds=duration,
        language=language,
        gender=gender,
        accent=accent,
        voice_id=voice_id,
        speech_rate=1.0,
        pause_before_seconds=0.0,
        pause_after_seconds=0.0,
        max_words=8,
        energy="high",
        narration_intent=f"{purpose.lower()}_intent",
        confidence=confidence,
    )


def _subtitle_segment(
    scene_number: int,
    purpose: str,
    *,
    start: float,
    duration: float,
    anchor: str = "bottom_center",
    max_lines: int = 2,
    confidence: float = 1.0,
) -> SubtitleSegmentPlan:
    return SubtitleSegmentPlan(
        scene_number=scene_number,
        purpose=purpose,
        start_seconds=start,
        end_seconds=start + duration,
        duration_seconds=duration,
        safe_zone="bottom",
        anchor=anchor,
        max_chars_per_line=18,
        max_lines=max_lines,
        font_scale=0.8,
        emphasis="strong",
        animation_hint="quick_pop",
        background_style="compact_box",
        avoid_center_subject=True,
        confidence=confidence,
    )
