from __future__ import annotations

from applications.ai_money_factory.core.video_intelligence.models import (
    ScoredScene,
)

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

PURPOSE_RULES = {
    "hook": (20, "HOOK"),
    "pour": (15, "POUR"),
    "macro": (15, "MACRO"),
    "product": (15, "PRODUCT"),
    "cta": (15, "CTA"),
}

SIGNAL_RULES = {
    "food": 5,
    "packaging": 5,
    "human": 2,
    "pouring": 8,
    "macro_closeup": 8,
}

QUALITY_SCORES = {
    1: -20,
    2: -10,
    3: 0,
    4: 5,
    5: 10,
}

WATERMARK_SCORES = {
    "none": 0,
    "minor": -5,
    "croppable": -10,
    "major": -25,
    "center": -40,
    "reject": 0,
}


class SceneScoringEngine:
    """
    Score human-reviewed scene rows using deterministic business rules.
    """

    def score(
        self,
        review_rows: list[dict[str, object]],
    ) -> list[ScoredScene]:
        seen_scene_numbers: set[int] = set()
        scored_scenes: list[ScoredScene] = []

        for row in review_rows:
            scene_number = _positive_int(
                row.get("scene_number"),
                "scene_number",
            )

            if scene_number in seen_scene_numbers:
                raise ValueError(
                    f"duplicate scene_number: {scene_number}"
                )

            seen_scene_numbers.add(scene_number)
            scored_scenes.append(
                _score_row(
                    row,
                    scene_number,
                )
            )

        return sorted(
            scored_scenes,
            key=lambda scene: (
                not scene.eligible,
                -scene.score,
                scene.scene_number,
            ),
        )


def _score_row(
    row: dict[str, object],
    scene_number: int,
) -> ScoredScene:
    for field in BOOLEAN_FIELDS:
        _boolean(
            row.get(field),
            field,
            scene_number,
        )

    quality = _quality(
        row.get("quality"),
        scene_number,
    )
    watermark = _watermark(
        row.get("watermark"),
        scene_number,
    )
    reject_reason = _string(
        row.get("reject_reason", ""),
        "reject_reason",
        scene_number,
    )

    score = 0.0
    purposes: list[str] = []
    rejection_reasons: list[str] = []

    if row["keep"]:
        score += 40

    for field, (points, purpose) in PURPOSE_RULES.items():
        if row[field]:
            score += points
            purposes.append(purpose)

    for field, points in SIGNAL_RULES.items():
        if row[field]:
            score += points

    score += QUALITY_SCORES[quality]
    score += WATERMARK_SCORES[watermark]

    if not row["keep"]:
        rejection_reasons.append(
            "keep is false"
        )

    if reject_reason.strip():
        rejection_reasons.append(
            "reject_reason is not empty"
        )

    if watermark == "reject":
        rejection_reasons.append(
            "watermark is reject"
        )

    return ScoredScene(
        scene_number=scene_number,
        score=score,
        eligible=not rejection_reasons,
        purposes=purposes,
        rejection_reasons=rejection_reasons,
    )


def _positive_int(
    value: object,
    field: str,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value <= 0
    ):
        raise ValueError(
            f"{field} must be a positive integer."
        )

    return value


def _boolean(
    value: object,
    field: str,
    scene_number: int,
) -> bool:
    if not isinstance(value, bool):
        raise ValueError(
            f"{field} must be a boolean "
            f"for scene_number {scene_number}."
        )

    return value


def _quality(
    value: object,
    scene_number: int,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value not in QUALITY_SCORES
    ):
        raise ValueError(
            "quality must be an integer from 1 to 5 "
            f"for scene_number {scene_number}."
        )

    return value


def _watermark(
    value: object,
    scene_number: int,
) -> str:
    if (
        not isinstance(value, str)
        or value not in WATERMARK_SCORES
    ):
        allowed = ", ".join(
            WATERMARK_SCORES
        )

        raise ValueError(
            f"watermark must be one of {allowed} "
            f"for scene_number {scene_number}."
        )

    return value


def _string(
    value: object,
    field: str,
    scene_number: int,
) -> str:
    if not isinstance(value, str):
        raise ValueError(
            f"{field} must be a string "
            f"for scene_number {scene_number}."
        )

    return value
