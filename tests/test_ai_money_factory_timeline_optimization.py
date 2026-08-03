from __future__ import annotations

from pathlib import Path

import pytest

from applications.ai_money_factory.core.video_intelligence import (
    SelectedTimelineClip,
    TimelineOptimizationEngine,
)


def test_optimizes_all_five_purposes() -> None:
    clips = TimelineOptimizationEngine().optimize(_clips())

    assert [clip.purpose for clip in clips] == [
        "HOOK",
        "POUR",
        "MACRO",
        "PRODUCT",
        "CTA",
    ]
    assert [clip.scene_number for clip in clips] == [1, 2, 3, 4, 5]


def test_target_duration_uses_preferred_duration_when_source_is_long_enough() -> None:
    clips = TimelineOptimizationEngine().optimize(_clips(duration_seconds=10))

    assert [clip.target_duration_seconds for clip in clips] == [2.0, 2.5, 2.5, 3.0, 3.0]


def test_target_duration_uses_available_duration_when_source_is_shorter() -> None:
    clips = TimelineOptimizationEngine().optimize(_clips(duration_seconds=1.25))

    assert [clip.target_duration_seconds for clip in clips] == [
        1.25,
        1.25,
        1.25,
        1.25,
        1.25,
    ]


def test_output_timing_has_no_gaps_or_overlaps() -> None:
    clips = TimelineOptimizationEngine().optimize(
        [
            _clip(1, "HOOK", duration_seconds=5),
            _clip(2, "POUR", duration_seconds=5),
            _clip(3, "MACRO", duration_seconds=5),
            _clip(4, "PRODUCT", duration_seconds=5),
            _clip(5, "CTA", duration_seconds=5),
        ]
    )

    assert [(clip.output_start_seconds, clip.output_end_seconds) for clip in clips] == [
        (0.0, 2.0),
        (2.0, 4.5),
        (4.5, 7.0),
        (7.0, 10.0),
        (10.0, 13.0),
    ]


def test_croppable_watermark_sets_requires_crop_true() -> None:
    clips = TimelineOptimizationEngine().optimize(
        _clips(watermarks={1: "croppable"})
    )

    assert clips[0].requires_crop is True
    assert clips[0].watermark == "croppable"


def test_none_and_minor_watermarks_set_requires_crop_false() -> None:
    clips = TimelineOptimizationEngine().optimize(
        _clips(watermarks={1: "none", 2: "minor"})
    )

    assert clips[0].requires_crop is False
    assert clips[1].requires_crop is False


@pytest.mark.parametrize("watermark", ["major", "center", "reject"])
def test_unsafe_watermark_raises_value_error(watermark: str) -> None:
    with pytest.raises(ValueError, match="watermark"):
        TimelineOptimizationEngine().optimize(_clips(watermarks={1: watermark}))


def test_confidence_penalty_for_short_clip() -> None:
    clips = TimelineOptimizationEngine().optimize(
        _clips(duration_overrides={1: 1.0})
    )

    assert clips[0].confidence == 0.8


def test_confidence_penalty_for_croppable_watermark() -> None:
    clips = TimelineOptimizationEngine().optimize(
        _clips(watermarks={1: "croppable"})
    )

    assert clips[0].confidence == 0.9


def test_confidence_penalty_for_center_subtitle_safe_zone() -> None:
    clips = TimelineOptimizationEngine().optimize(
        _clips(subtitle_safe_zones={1: "center"})
    )

    assert clips[0].confidence == 0.9


def test_confidence_penalty_for_low_score() -> None:
    clips = TimelineOptimizationEngine().optimize(
        _clips(scores={1: 59})
    )

    assert clips[0].confidence == 0.95


def test_confidence_clamps_to_zero_and_one() -> None:
    clips = TimelineOptimizationEngine().optimize(
        _clips(
            duration_overrides={1: 1.0},
            watermarks={1: "croppable"},
            subtitle_safe_zones={1: "center"},
            scores={1: 59},
        )
    )

    assert clips[0].confidence == 0.55
    assert all(0.0 <= clip.confidence <= 1.0 for clip in clips)


def test_missing_purpose_raises_value_error() -> None:
    clips = _clips()
    clips[2] = _clip(3, "EXTRA")

    with pytest.raises(ValueError, match="missing purpose MACRO"):
        TimelineOptimizationEngine().optimize(clips)


def test_duplicate_purpose_raises_value_error() -> None:
    clips = _clips()
    clips[1] = _clip(2, "HOOK")

    with pytest.raises(ValueError, match="duplicate purpose HOOK"):
        TimelineOptimizationEngine().optimize(clips)


def test_incorrect_purpose_order_raises_value_error() -> None:
    clips = _clips()
    clips[1], clips[2] = clips[2], clips[1]

    with pytest.raises(ValueError, match="purpose order"):
        TimelineOptimizationEngine().optimize(clips)


def test_non_positive_duration_raises_value_error() -> None:
    clips = _clips(duration_overrides={1: 0})

    with pytest.raises(ValueError, match="duration must be positive"):
        TimelineOptimizationEngine().optimize(clips)


def _clips(
    *,
    duration_seconds: float = 5,
    duration_overrides: dict[int, float] | None = None,
    watermarks: dict[int, str] | None = None,
    subtitle_safe_zones: dict[int, str] | None = None,
    scores: dict[int, float] | None = None,
) -> list[SelectedTimelineClip]:
    purposes = ["HOOK", "POUR", "MACRO", "PRODUCT", "CTA"]
    duration_overrides = duration_overrides or {}
    watermarks = watermarks or {}
    subtitle_safe_zones = subtitle_safe_zones or {}
    scores = scores or {}

    return [
        _clip(
            scene_number=index,
            purpose=purpose,
            duration_seconds=duration_overrides.get(index, duration_seconds),
            watermark=watermarks.get(index, "none"),
            subtitle_safe_zone=subtitle_safe_zones.get(index, "bottom"),
            score=scores.get(index, 80),
        )
        for index, purpose in enumerate(purposes, start=1)
    ]


def _clip(
    scene_number: int,
    purpose: str,
    *,
    duration_seconds: float = 5,
    watermark: str = "none",
    subtitle_safe_zone: str = "bottom",
    score: float = 80,
) -> SelectedTimelineClip:
    return SelectedTimelineClip(
        scene_number=scene_number,
        source_path=Path("source.mp4"),
        source_start_seconds=scene_number * 10.0,
        source_end_seconds=scene_number * 10.0 + duration_seconds,
        output_start_seconds=0.0,
        output_end_seconds=duration_seconds,
        duration_seconds=duration_seconds,
        target_duration_seconds=duration_seconds,
        purpose=purpose,
        score=score,
        watermark=watermark,
        subtitle_safe_zone=subtitle_safe_zone,
        requires_crop=False,
        confidence=1.0,
    )
