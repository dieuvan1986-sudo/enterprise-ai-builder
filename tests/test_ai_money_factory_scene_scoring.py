from __future__ import annotations

import pytest

from applications.ai_money_factory.core.video_intelligence import (
    ScoredScene,
    SceneScoringEngine,
)


def test_score_applies_positive_rules_and_purposes() -> None:
    rows = [
        _review_row(
            scene_number=1,
            keep=True,
            hook=True,
            pour=True,
            macro=True,
            product=True,
            cta=True,
            food=True,
            packaging=True,
            human=True,
            pouring=True,
            macro_closeup=True,
        )
    ]

    assert SceneScoringEngine().score(rows) == [
        ScoredScene(
            scene_number=1,
            score=148,
            eligible=True,
            purposes=["HOOK", "POUR", "MACRO", "PRODUCT", "CTA"],
            rejection_reasons=[],
        )
    ]


def test_score_applies_quality_scoring() -> None:
    rows = [
        _review_row(scene_number=1, keep=True, quality=1),
        _review_row(scene_number=2, keep=True, quality=2),
        _review_row(scene_number=3, keep=True, quality=3),
        _review_row(scene_number=4, keep=True, quality=4),
        _review_row(scene_number=5, keep=True, quality=5),
    ]

    scored = {
        scene.scene_number: scene.score
        for scene in SceneScoringEngine().score(rows)
    }

    assert scored == {
        1: 20,
        2: 30,
        3: 40,
        4: 45,
        5: 50,
    }


def test_score_applies_watermark_penalties() -> None:
    rows = [
        _review_row(scene_number=1, keep=True, watermark="none"),
        _review_row(scene_number=2, keep=True, watermark="minor"),
        _review_row(scene_number=3, keep=True, watermark="croppable"),
        _review_row(scene_number=4, keep=True, watermark="major"),
        _review_row(scene_number=5, keep=True, watermark="center"),
    ]

    assert [scene.score for scene in SceneScoringEngine().score(rows)] == [
        40,
        35,
        30,
        15,
        0,
    ]


def test_score_marks_keep_false_ineligible() -> None:
    scored_scene = SceneScoringEngine().score(
        [_review_row(scene_number=1, keep=False, quality=5)]
    )[0]

    assert scored_scene == ScoredScene(
        scene_number=1,
        score=10,
        eligible=False,
        purposes=[],
        rejection_reasons=["keep is false"],
    )


def test_score_marks_reject_reason_ineligible() -> None:
    scored_scene = SceneScoringEngine().score(
        [_review_row(scene_number=1, keep=True, reject_reason="bad logo")]
    )[0]

    assert scored_scene == ScoredScene(
        scene_number=1,
        score=40,
        eligible=False,
        purposes=[],
        rejection_reasons=["reject_reason is not empty"],
    )


def test_score_marks_watermark_reject_ineligible() -> None:
    scored_scene = SceneScoringEngine().score(
        [_review_row(scene_number=1, keep=True, watermark="reject")]
    )[0]

    assert scored_scene == ScoredScene(
        scene_number=1,
        score=40,
        eligible=False,
        purposes=[],
        rejection_reasons=["watermark is reject"],
    )


def test_score_sorts_eligible_first_score_descending_and_scene_number_ties() -> None:
    rows = [
        _review_row(scene_number=3, keep=True, quality=4),
        _review_row(scene_number=2, keep=True, quality=4),
        _review_row(scene_number=1, keep=False, quality=5),
        _review_row(scene_number=4, keep=True, quality=5),
    ]

    assert [
        scene.scene_number
        for scene in SceneScoringEngine().score(rows)
    ] == [4, 2, 3, 1]


def test_score_rejects_invalid_quality() -> None:
    with pytest.raises(ValueError, match="quality"):
        SceneScoringEngine().score(
            [_review_row(scene_number=1, quality=6)]
        )


def test_score_rejects_invalid_watermark() -> None:
    with pytest.raises(ValueError, match="watermark"):
        SceneScoringEngine().score(
            [_review_row(scene_number=1, watermark="unknown")]
        )


def test_score_rejects_duplicate_scene_numbers() -> None:
    with pytest.raises(ValueError, match="duplicate scene_number"):
        SceneScoringEngine().score(
            [
                _review_row(scene_number=1),
                _review_row(scene_number=1),
            ]
        )


def _review_row(
    *,
    scene_number: int,
    keep: bool = False,
    hook: bool = False,
    pour: bool = False,
    macro: bool = False,
    product: bool = False,
    cta: bool = False,
    watermark: str = "none",
    subtitle_safe_zone: str = "bottom",
    quality: int = 3,
    food: bool = False,
    packaging: bool = False,
    human: bool = False,
    pouring: bool = False,
    macro_closeup: bool = False,
    reject_reason: str = "",
    notes: str = "",
) -> dict[str, object]:
    return {
        "scene_number": scene_number,
        "keep": keep,
        "hook": hook,
        "pour": pour,
        "macro": macro,
        "product": product,
        "cta": cta,
        "watermark": watermark,
        "subtitle_safe_zone": subtitle_safe_zone,
        "quality": quality,
        "food": food,
        "packaging": packaging,
        "human": human,
        "pouring": pouring,
        "macro_closeup": macro_closeup,
        "reject_reason": reject_reason,
        "notes": notes,
    }
