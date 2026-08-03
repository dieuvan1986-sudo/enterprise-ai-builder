from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

BOOLEAN_FIELDS = (
    "keep",
    "hook",
    "pour",
    "macro",
    "product",
    "cta",
    "food",
    "packaging",
    "human",
    "pouring",
    "macro_closeup",
)
REQUIRED_FIELDS = (
    "scene_number",
    *BOOLEAN_FIELDS,
    "watermark",
    "subtitle_safe_zone",
    "quality",
    "reject_reason",
    "notes",
)
WATERMARK_VALUES = {
    "none",
    "minor",
    "major",
    "center",
    "croppable",
    "reject",
}
SUBTITLE_SAFE_ZONE_VALUES = {
    "top",
    "bottom",
    "left",
    "right",
    "center",
}


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    review_path = Path(args.scene_review_template_json)
    errors = validate_review_dataset(review_path)

    if errors:
        print("Scene review dataset validation failed:")

        for error in errors:
            print(f"- {error}")

        return 1

    print(f"Scene review dataset is valid: {review_path}")

    return 0


def validate_review_dataset(review_path: Path) -> list[str]:
    if not review_path.is_file():
        return [f"Scene review dataset does not exist: {review_path}"]

    try:
        data = json.loads(review_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f"Invalid JSON: {error.msg} at line {error.lineno}, column {error.colno}"]

    if not isinstance(data, list):
        return ["scene_review_template.json must contain a list."]

    errors: list[str] = []
    seen_scene_numbers: set[int] = set()

    for index, row in enumerate(data, start=1):
        if not isinstance(row, dict):
            errors.append(f"Row {index} must be an object.")
            continue

        _validate_row(
            row=row,
            row_number=index,
            seen_scene_numbers=seen_scene_numbers,
            errors=errors,
        )

    return errors


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an AI Money Factory scene review dataset.",
    )
    parser.add_argument(
        "scene_review_template_json",
        help="Path to scene_review_template.json.",
    )

    return parser.parse_args(argv)


def _validate_row(
    *,
    row: dict[str, object],
    row_number: int,
    seen_scene_numbers: set[int],
    errors: list[str],
) -> None:
    for field in REQUIRED_FIELDS:
        if field not in row:
            errors.append(f"Row {row_number}: missing required field '{field}'.")

    scene_number = row.get("scene_number")

    if isinstance(scene_number, bool) or not isinstance(scene_number, int):
        errors.append(f"Row {row_number}: scene_number must be a positive integer.")
    elif scene_number <= 0:
        errors.append(f"Row {row_number}: scene_number must be a positive integer.")
    elif scene_number in seen_scene_numbers:
        errors.append(f"Row {row_number}: duplicate scene_number {scene_number}.")
    else:
        seen_scene_numbers.add(scene_number)

    for field in BOOLEAN_FIELDS:
        if field in row and not isinstance(row[field], bool):
            errors.append(f"Row {row_number}: {field} must be a boolean.")

    _validate_quality(row, row_number, errors)
    _validate_enum(row, row_number, errors, "watermark", WATERMARK_VALUES)
    _validate_enum(
        row,
        row_number,
        errors,
        "subtitle_safe_zone",
        SUBTITLE_SAFE_ZONE_VALUES,
    )
    _validate_string(row, row_number, errors, "reject_reason")
    _validate_string(row, row_number, errors, "notes")
    _validate_conflicts(row, row_number, errors)


def _validate_quality(
    row: dict[str, object],
    row_number: int,
    errors: list[str],
) -> None:
    if "quality" not in row:
        return

    quality = row["quality"]

    if isinstance(quality, bool) or not isinstance(quality, int) or quality not in range(1, 6):
        errors.append(f"Row {row_number}: quality must be an integer from 1 to 5.")


def _validate_enum(
    row: dict[str, object],
    row_number: int,
    errors: list[str],
    field: str,
    allowed_values: set[str],
) -> None:
    if field not in row:
        return

    value = row[field]

    if not isinstance(value, str) or value not in allowed_values:
        allowed = ", ".join(sorted(allowed_values))
        errors.append(f"Row {row_number}: {field} must be one of {allowed}.")


def _validate_string(
    row: dict[str, object],
    row_number: int,
    errors: list[str],
    field: str,
) -> None:
    if field in row and not isinstance(row[field], str):
        errors.append(f"Row {row_number}: {field} must be a string.")


def _validate_conflicts(
    row: dict[str, object],
    row_number: int,
    errors: list[str],
) -> None:
    if row.get("hook") is True and row.get("cta") is True:
        errors.append("Row {row_number}: hook and cta cannot both be true.".format(
            row_number=row_number,
        ))


if __name__ == "__main__":
    raise SystemExit(main())
