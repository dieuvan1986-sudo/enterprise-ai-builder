from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from applications.ai_money_factory.core.video_intelligence import (
    SceneScoringEngine,
)
from applications.ai_money_factory.core.video_intelligence.models import (
    ScoredScene,
)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    review_path = Path(args.scene_review_template_json)
    output_path = review_path.parent / "scene_scores.json"
    review_rows = _read_review_rows(review_path)
    scored_scenes = SceneScoringEngine().score(review_rows)

    output_path.write_text(
        json.dumps(
            [
                _scored_scene_payload(scene)
                for scene in scored_scenes
            ],
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    _print_ranked_summary(scored_scenes)

    return 0


def _parse_args(
    argv: Sequence[str] | None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Score a human-reviewed "
            "AI Money Factory scene dataset."
        ),
    )
    parser.add_argument(
        "scene_review_template_json",
        help="Path to scene_review_template.json.",
    )

    return parser.parse_args(argv)


def _read_review_rows(
    review_path: Path,
) -> list[dict[str, object]]:
    if not review_path.is_file():
        raise FileNotFoundError(
            "Scene review dataset does not exist: "
            f"{review_path}"
        )

    data = json.loads(
        review_path.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(data, list):
        raise ValueError(
            "scene_review_template.json "
            "must contain a list."
        )

    rows: list[dict[str, object]] = []

    for index, row in enumerate(
        data,
        start=1,
    ):
        if not isinstance(row, dict):
            raise ValueError(
                "scene_review_template.json "
                "must contain only objects; "
                f"item {index} is "
                f"{type(row).__name__}."
            )

        rows.append(row)

    return rows


def _scored_scene_payload(
    scene: ScoredScene,
) -> dict[str, object]:
    return asdict(scene)


def _print_ranked_summary(
    scored_scenes: list[ScoredScene],
) -> None:
    print(
        "Scene | Score | Eligible | Purposes"
    )

    for scene in scored_scenes:
        purposes = (
            ",".join(scene.purposes)
            if scene.purposes
            else "-"
        )
        print(
            f"{scene.scene_number} | "
            f"{scene.score:g} | "
            f"{scene.eligible} | "
            f"{purposes}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
