from __future__ import annotations

import json
from pathlib import Path

import pytest

from applications.ai_money_factory.tools.score_review_dataset import (
    main,
)


def test_score_review_dataset_writes_scores_and_ranked_summary(
    tmp_path: Path,
    capsys,
) -> None:
    review_path = (
        tmp_path / "scene_review_template.json"
    )
    review_path.write_text(
        json.dumps(
            [
                _review_row(
                    scene_number=1,
                    keep=True,
                    hook=True,
                    product=True,
                    quality=5,
                ),
                _review_row(
                    scene_number=2,
                    keep=True,
                    pour=True,
                    food=True,
                    quality=4,
                ),
                _review_row(
                    scene_number=3,
                    keep=False,
                    quality=5,
                ),
            ]
        ),
        encoding="utf-8",
    )

    result = main([str(review_path)])

    scores_path = (
        tmp_path / "scene_scores.json"
    )

    assert result == 0
    assert capsys.readouterr().out == (
        "Scene | Score | Eligible | Purposes\n"
        "1 | 85 | True | HOOK,PRODUCT\n"
        "2 | 65 | True | POUR\n"
        "3 | 10 | False | -\n"
    )
    assert json.loads(
        scores_path.read_text(
            encoding="utf-8",
        )
    ) == [
        {
            "scene_number": 1,
            "score": 85.0,
            "eligible": True,
            "purposes": [
                "HOOK",
                "PRODUCT",
            ],
            "rejection_reasons": [],
        },
        {
            "scene_number": 2,
            "score": 65.0,
            "eligible": True,
            "purposes": ["POUR"],
            "rejection_reasons": [],
        },
        {
            "scene_number": 3,
            "score": 10.0,
            "eligible": False,
            "purposes": [],
            "rejection_reasons": [
                "keep is false"
            ],
        },
    ]


def test_score_review_dataset_rejects_non_list_dataset(
    tmp_path: Path,
) -> None:
    review_path = (
        tmp_path / "scene_review_template.json"
    )
    review_path.write_text(
        "{}",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="must contain a list",
    ):
        main([str(review_path)])


def test_score_review_dataset_rejects_non_object_rows(
    tmp_path: Path,
) -> None:
    review_path = (
        tmp_path / "scene_review_template.json"
    )
    review_path.write_text(
        "[1]",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="must contain only objects",
    ):
        main([str(review_path)])


def test_score_review_dataset_uses_scoring_validation(
    tmp_path: Path,
) -> None:
    review_path = (
        tmp_path / "scene_review_template.json"
    )
    row = _review_row(scene_number=1)
    row["quality"] = 6

    review_path.write_text(
        json.dumps([row]),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="quality",
    ):
        main([str(review_path)])


def test_score_review_dataset_rejects_missing_file(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="does not exist",
    ):
        main(
            [
                str(
                    tmp_path
                    / "scene_review_template.json"
                )
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
        "subtitle_safe_zone": (
            subtitle_safe_zone
        ),
        "quality": quality,
        "food": food,
        "packaging": packaging,
        "human": human,
        "pouring": pouring,
        "macro_closeup": macro_closeup,
        "reject_reason": reject_reason,
        "notes": notes,
    }
