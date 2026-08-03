from __future__ import annotations

from pathlib import Path

import pytest

from applications.ai_money_factory.core.video_intelligence import (
    DetectedScene,
    ScoredScene,
    SelectedTimelineClip,
    TimelineSelectionEngine,
)


def test_selects_required_purpose_order() -> None:
    clips = TimelineSelectionEngine().select(
        detected_scenes=_detected_scenes([3, 1, 5, 2, 4]),
        scored_scenes=[
            _scored_scene(3, 90, ["HOOK"]),
            _scored_scene(1, 80, ["POUR"]),
            _scored_scene(5, 70, ["MACRO"]),
            _scored_scene(2, 60, ["PRODUCT"]),
            _scored_scene(4, 50, ["CTA"]),
        ],
        review_rows=_review_rows([3, 1, 5, 2, 4]),
    )

    assert [clip.purpose for clip in clips] == [
        "HOOK",
        "POUR",
        "MACRO",
        "PRODUCT",
        "CTA",
    ]
    assert [clip.scene_number for clip in clips] == [3, 1, 5, 2, 4]


def test_selects_highest_score_for_each_purpose() -> None:
    clips = TimelineSelectionEngine().select(
        detected_scenes=_detected_scenes([1, 2, 3, 4, 5, 6]),
        scored_scenes=[
            _scored_scene(1, 80, ["HOOK"]),
            _scored_scene(6, 95, ["HOOK"]),
            _scored_scene(2, 70, ["POUR"]),
            _scored_scene(3, 60, ["MACRO"]),
            _scored_scene(4, 50, ["PRODUCT"]),
            _scored_scene(5, 40, ["CTA"]),
        ],
        review_rows=_review_rows([1, 2, 3, 4, 5, 6]),
    )

    assert clips[0].scene_number == 6
    assert clips[0].score == 95


def test_selects_lower_scene_number_for_score_ties() -> None:
    clips = TimelineSelectionEngine().select(
        detected_scenes=_detected_scenes([1, 2, 3, 4, 5, 6]),
        scored_scenes=[
            _scored_scene(6, 90, ["HOOK"]),
            _scored_scene(1, 90, ["HOOK"]),
            _scored_scene(2, 70, ["POUR"]),
            _scored_scene(3, 60, ["MACRO"]),
            _scored_scene(4, 50, ["PRODUCT"]),
            _scored_scene(5, 40, ["CTA"]),
        ],
        review_rows=_review_rows([1, 2, 3, 4, 5, 6]),
    )

    assert clips[0].scene_number == 1


def test_does_not_reuse_scene_for_multiple_positions() -> None:
    clips = TimelineSelectionEngine().select(
        detected_scenes=_detected_scenes([1, 2, 3, 4, 5, 6]),
        scored_scenes=[
            _scored_scene(1, 100, ["HOOK", "POUR"]),
            _scored_scene(2, 90, ["POUR"]),
            _scored_scene(3, 80, ["MACRO"]),
            _scored_scene(4, 70, ["PRODUCT"]),
            _scored_scene(5, 60, ["CTA"]),
            _scored_scene(6, 50, ["HOOK"]),
        ],
        review_rows=_review_rows([1, 2, 3, 4, 5, 6]),
    )

    assert [clip.scene_number for clip in clips] == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("watermark", ["major", "center", "reject"])
def test_rejects_unsafe_watermarks(watermark: str) -> None:
    review_rows = _review_rows([1, 2, 3, 4, 5, 6])
    review_rows[0]["watermark"] = watermark

    clips = TimelineSelectionEngine().select(
        detected_scenes=_detected_scenes([1, 2, 3, 4, 5, 6]),
        scored_scenes=[
            _scored_scene(1, 100, ["HOOK"]),
            _scored_scene(6, 90, ["HOOK"]),
            _scored_scene(2, 70, ["POUR"]),
            _scored_scene(3, 60, ["MACRO"]),
            _scored_scene(4, 50, ["PRODUCT"]),
            _scored_scene(5, 40, ["CTA"]),
        ],
        review_rows=review_rows,
    )

    assert clips[0].scene_number == 6


def test_croppable_watermark_is_selectable_and_preserved() -> None:
    review_rows = _review_rows([1, 2, 3, 4, 5])
    review_rows[0]["watermark"] = "croppable"

    clips = TimelineSelectionEngine().select(
        detected_scenes=_detected_scenes([1, 2, 3, 4, 5]),
        scored_scenes=[
            _scored_scene(1, 100, ["HOOK"]),
            _scored_scene(2, 70, ["POUR"]),
            _scored_scene(3, 60, ["MACRO"]),
            _scored_scene(4, 50, ["PRODUCT"]),
            _scored_scene(5, 40, ["CTA"]),
        ],
        review_rows=review_rows,
    )

    assert clips[0].watermark == "croppable"


def test_output_timing_has_no_gaps_or_overlaps() -> None:
    clips = TimelineSelectionEngine().select(
        detected_scenes=[
            _detected_scene(1, start=8, end=10),
            _detected_scene(2, start=2, end=5),
            _detected_scene(3, start=14, end=18),
            _detected_scene(4, start=0, end=1.5),
            _detected_scene(5, start=20, end=22),
        ],
        scored_scenes=[
            _scored_scene(1, 100, ["HOOK"]),
            _scored_scene(2, 90, ["POUR"]),
            _scored_scene(3, 80, ["MACRO"]),
            _scored_scene(4, 70, ["PRODUCT"]),
            _scored_scene(5, 60, ["CTA"]),
        ],
        review_rows=_review_rows([1, 2, 3, 4, 5]),
    )

    assert clips == [
        SelectedTimelineClip(
            scene_number=1,
            source_path=Path("source.mp4"),
            source_start_seconds=8,
            source_end_seconds=10,
            output_start_seconds=0.0,
            output_end_seconds=2.0,
            duration_seconds=2,
            purpose="HOOK",
            score=100,
            watermark="none",
            subtitle_safe_zone="bottom",
        ),
        SelectedTimelineClip(
            scene_number=2,
            source_path=Path("source.mp4"),
            source_start_seconds=2,
            source_end_seconds=5,
            output_start_seconds=2.0,
            output_end_seconds=5.0,
            duration_seconds=3,
            purpose="POUR",
            score=90,
            watermark="none",
            subtitle_safe_zone="bottom",
        ),
        SelectedTimelineClip(
            scene_number=3,
            source_path=Path("source.mp4"),
            source_start_seconds=14,
            source_end_seconds=18,
            output_start_seconds=5.0,
            output_end_seconds=9.0,
            duration_seconds=4,
            purpose="MACRO",
            score=80,
            watermark="none",
            subtitle_safe_zone="bottom",
        ),
        SelectedTimelineClip(
            scene_number=4,
            source_path=Path("source.mp4"),
            source_start_seconds=0,
            source_end_seconds=1.5,
            output_start_seconds=9.0,
            output_end_seconds=10.5,
            duration_seconds=1.5,
            purpose="PRODUCT",
            score=70,
            watermark="none",
            subtitle_safe_zone="bottom",
        ),
        SelectedTimelineClip(
            scene_number=5,
            source_path=Path("source.mp4"),
            source_start_seconds=20,
            source_end_seconds=22,
            output_start_seconds=10.5,
            output_end_seconds=12.5,
            duration_seconds=2,
            purpose="CTA",
            score=60,
            watermark="none",
            subtitle_safe_zone="bottom",
        ),
    ]


def test_missing_required_purpose_raises_value_error() -> None:
    with pytest.raises(ValueError, match="required purpose MACRO"):
        TimelineSelectionEngine().select(
            detected_scenes=_detected_scenes([1, 2, 4, 5]),
            scored_scenes=[
                _scored_scene(1, 100, ["HOOK"]),
                _scored_scene(2, 90, ["POUR"]),
                _scored_scene(4, 70, ["PRODUCT"]),
                _scored_scene(5, 60, ["CTA"]),
            ],
            review_rows=_review_rows([1, 2, 4, 5]),
        )


def test_missing_detected_scene_raises_value_error() -> None:
    with pytest.raises(ValueError, match="matching DetectedScene"):
        TimelineSelectionEngine().select(
            detected_scenes=_detected_scenes([1, 2, 3, 4]),
            scored_scenes=[
                _scored_scene(1, 100, ["HOOK"]),
                _scored_scene(2, 90, ["POUR"]),
                _scored_scene(3, 80, ["MACRO"]),
                _scored_scene(4, 70, ["PRODUCT"]),
                _scored_scene(5, 60, ["CTA"]),
            ],
            review_rows=_review_rows([1, 2, 3, 4, 5]),
        )


def test_missing_review_row_raises_value_error() -> None:
    with pytest.raises(ValueError, match="matching review row"):
        TimelineSelectionEngine().select(
            detected_scenes=_detected_scenes([1, 2, 3, 4, 5]),
            scored_scenes=[
                _scored_scene(1, 100, ["HOOK"]),
                _scored_scene(2, 90, ["POUR"]),
                _scored_scene(3, 80, ["MACRO"]),
                _scored_scene(4, 70, ["PRODUCT"]),
                _scored_scene(5, 60, ["CTA"]),
            ],
            review_rows=_review_rows([1, 2, 3, 4]),
        )


def test_duplicate_scene_numbers_raise_value_error() -> None:
    with pytest.raises(ValueError, match="duplicate detected scene_number"):
        TimelineSelectionEngine().select(
            detected_scenes=[
                _detected_scene(1, start=0, end=1),
                _detected_scene(1, start=1, end=2),
            ],
            scored_scenes=[],
            review_rows=[],
        )

    with pytest.raises(ValueError, match="duplicate scored scene_number"):
        TimelineSelectionEngine().select(
            detected_scenes=[],
            scored_scenes=[
                _scored_scene(1, 100, ["HOOK"]),
                _scored_scene(1, 90, ["POUR"]),
            ],
            review_rows=[],
        )

    with pytest.raises(ValueError, match="duplicate review scene_number"):
        TimelineSelectionEngine().select(
            detected_scenes=[],
            scored_scenes=[],
            review_rows=[
                _review_row(1),
                _review_row(1),
            ],
        )


def test_invalid_or_non_positive_scene_duration_raises_value_error() -> None:
    with pytest.raises(ValueError, match="duration must be positive"):
        TimelineSelectionEngine().select(
            detected_scenes=[_detected_scene(1, start=0, end=1, duration=0)],
            scored_scenes=[],
            review_rows=[],
        )

    with pytest.raises(ValueError, match="end must be after start"):
        TimelineSelectionEngine().select(
            detected_scenes=[_detected_scene(1, start=1, end=1, duration=1)],
            scored_scenes=[],
            review_rows=[],
        )


def _detected_scenes(scene_numbers: list[int]) -> list[DetectedScene]:
    return [
        _detected_scene(scene_number, start=index * 2, end=index * 2 + 2)
        for index, scene_number in enumerate(scene_numbers)
    ]


def _detected_scene(
    scene_number: int,
    *,
    start: float,
    end: float,
    duration: float | None = None,
) -> DetectedScene:
    return DetectedScene(
        source_path=Path("source.mp4"),
        scene_number=scene_number,
        start_seconds=start,
        end_seconds=end,
        duration_seconds=duration if duration is not None else end - start,
    )


def _scored_scene(
    scene_number: int,
    score: float,
    purposes: list[str],
    *,
    eligible: bool = True,
) -> ScoredScene:
    return ScoredScene(
        scene_number=scene_number,
        score=score,
        eligible=eligible,
        purposes=purposes,
        rejection_reasons=[] if eligible else ["not eligible"],
    )


def _review_rows(
    scene_numbers: list[int],
    *,
    watermark: str = "none",
    subtitle_safe_zone: str = "bottom",
) -> list[dict[str, object]]:
    return [
        _review_row(
            scene_number,
            watermark=watermark,
            subtitle_safe_zone=subtitle_safe_zone,
        )
        for scene_number in scene_numbers
    ]


def _review_row(
    scene_number: int,
    *,
    watermark: str = "none",
    subtitle_safe_zone: str = "bottom",
) -> dict[str, object]:
    return {
        "scene_number": scene_number,
        "watermark": watermark,
        "subtitle_safe_zone": subtitle_safe_zone,
    }
