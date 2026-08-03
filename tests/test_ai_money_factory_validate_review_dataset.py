from __future__ import annotations

import json
from pathlib import Path

from applications.ai_money_factory.tools.validate_review_dataset import main


def test_validate_review_dataset_accepts_valid_dataset(
    tmp_path: Path,
    capsys,
) -> None:
    review_path = tmp_path / "scene_review_template.json"
    review_path.write_text(json.dumps([_review_row(scene_number=1)]), encoding="utf-8")
    original_content = review_path.read_text(encoding="utf-8")

    result = main([str(review_path)])

    assert result == 0
    assert capsys.readouterr().out == (
        f"Scene review dataset is valid: {review_path}\n"
    )
    assert review_path.read_text(encoding="utf-8") == original_content


def test_validate_review_dataset_reports_missing_required_fields(
    tmp_path: Path,
    capsys,
) -> None:
    review_path = tmp_path / "scene_review_template.json"
    review_path.write_text('[{"scene_number":1}]', encoding="utf-8")

    result = main([str(review_path)])

    assert result == 1
    output = capsys.readouterr().out
    assert "Scene review dataset validation failed:" in output
    assert "Row 1: missing required field 'keep'." in output
    assert "Row 1: missing required field 'notes'." in output


def test_validate_review_dataset_reports_invalid_enums_and_quality(
    tmp_path: Path,
    capsys,
) -> None:
    review_path = tmp_path / "scene_review_template.json"
    row = _review_row(
        scene_number=1,
        watermark="bad",
        subtitle_safe_zone="diagonal",
        quality=6,
    )
    review_path.write_text(json.dumps([row]), encoding="utf-8")

    result = main([str(review_path)])

    output = capsys.readouterr().out

    assert result == 1
    assert "Row 1: quality must be an integer from 1 to 5." in output
    assert "Row 1: watermark must be one of" in output
    assert "Row 1: subtitle_safe_zone must be one of" in output


def test_validate_review_dataset_reports_duplicate_scene_numbers(
    tmp_path: Path,
    capsys,
) -> None:
    review_path = tmp_path / "scene_review_template.json"
    review_path.write_text(
        json.dumps(
            [
                _review_row(scene_number=1),
                _review_row(scene_number=1),
            ]
        ),
        encoding="utf-8",
    )

    result = main([str(review_path)])

    assert result == 1
    assert "Row 2: duplicate scene_number 1." in capsys.readouterr().out


def test_validate_review_dataset_reports_non_boolean_fields(
    tmp_path: Path,
    capsys,
) -> None:
    review_path = tmp_path / "scene_review_template.json"
    row = _review_row(scene_number=1)
    row["keep"] = "yes"
    review_path.write_text(json.dumps([row]), encoding="utf-8")

    result = main([str(review_path)])

    assert result == 1
    assert "Row 1: keep must be a boolean." in capsys.readouterr().out


def test_validate_review_dataset_reports_conflicting_purposes(
    tmp_path: Path,
    capsys,
) -> None:
    review_path = tmp_path / "scene_review_template.json"
    review_path.write_text(
        json.dumps([_review_row(scene_number=1, hook=True, cta=True)]),
        encoding="utf-8",
    )

    result = main([str(review_path)])

    assert result == 1
    assert "Row 1: hook and cta cannot both be true." in capsys.readouterr().out


def test_validate_review_dataset_reports_top_level_schema_errors(
    tmp_path: Path,
    capsys,
) -> None:
    review_path = tmp_path / "scene_review_template.json"
    review_path.write_text("{}", encoding="utf-8")

    result = main([str(review_path)])

    assert result == 1
    assert "scene_review_template.json must contain a list." in capsys.readouterr().out


def test_validate_review_dataset_reports_missing_file(
    tmp_path: Path,
    capsys,
) -> None:
    review_path = tmp_path / "scene_review_template.json"

    result = main([str(review_path)])

    assert result == 1
    assert f"Scene review dataset does not exist: {review_path}" in capsys.readouterr().out


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
