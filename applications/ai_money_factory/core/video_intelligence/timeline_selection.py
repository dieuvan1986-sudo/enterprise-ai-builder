from __future__ import annotations

from applications.ai_money_factory.core.video_intelligence.models import (
    DetectedScene,
    ScoredScene,
    SelectedTimelineClip,
)

PURPOSE_ORDER = ("HOOK", "POUR", "MACRO", "PRODUCT", "CTA")
UNSAFE_WATERMARKS = {"reject", "center", "major"}
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


class TimelineSelectionEngine:
    """
    Select a deterministic conversion-purpose timeline from reviewed scenes.
    """

    def select(
        self,
        detected_scenes: list[DetectedScene],
        scored_scenes: list[ScoredScene],
        review_rows: list[dict[str, object]],
    ) -> list[SelectedTimelineClip]:
        detected_by_scene = _detected_scene_map(detected_scenes)
        scored_by_scene = _scored_scene_map(scored_scenes)
        review_by_scene = _review_row_map(review_rows)
        selected_clips: list[SelectedTimelineClip] = []
        used_scene_numbers: set[int] = set()
        output_start = 0.0

        _validate_required_scene_metadata(
            scored_scenes=scored_scenes,
            detected_by_scene=detected_by_scene,
            review_by_scene=review_by_scene,
        )

        for purpose in PURPOSE_ORDER:
            scored_scene = _select_scored_scene_for_purpose(
                purpose=purpose,
                scored_scenes=list(scored_by_scene.values()),
                review_by_scene=review_by_scene,
                used_scene_numbers=used_scene_numbers,
            )
            detected_scene = detected_by_scene[scored_scene.scene_number]
            review_row = review_by_scene[scored_scene.scene_number]
            duration = detected_scene.end_seconds - detected_scene.start_seconds
            output_end = output_start + duration

            selected_clips.append(
                SelectedTimelineClip(
                    scene_number=scored_scene.scene_number,
                    source_path=detected_scene.source_path,
                    source_start_seconds=detected_scene.start_seconds,
                    source_end_seconds=detected_scene.end_seconds,
                    output_start_seconds=output_start,
                    output_end_seconds=output_end,
                    duration_seconds=duration,
                    purpose=purpose,
                    score=scored_scene.score,
                    watermark=str(review_row["watermark"]),
                    subtitle_safe_zone=str(review_row["subtitle_safe_zone"]),
                )
            )
            used_scene_numbers.add(scored_scene.scene_number)
            output_start = output_end

        return selected_clips


def _detected_scene_map(
    detected_scenes: list[DetectedScene],
) -> dict[int, DetectedScene]:
    detected_by_scene: dict[int, DetectedScene] = {}

    for scene in detected_scenes:
        if scene.scene_number in detected_by_scene:
            raise ValueError(f"duplicate detected scene_number: {scene.scene_number}")

        if scene.duration_seconds <= 0:
            raise ValueError(
                f"detected scene {scene.scene_number} duration must be positive."
            )

        if scene.end_seconds <= scene.start_seconds:
            raise ValueError(
                f"detected scene {scene.scene_number} end must be after start."
            )

        detected_by_scene[scene.scene_number] = scene

    return detected_by_scene


def _scored_scene_map(scored_scenes: list[ScoredScene]) -> dict[int, ScoredScene]:
    scored_by_scene: dict[int, ScoredScene] = {}

    for scene in scored_scenes:
        if scene.scene_number in scored_by_scene:
            raise ValueError(f"duplicate scored scene_number: {scene.scene_number}")

        scored_by_scene[scene.scene_number] = scene

    return scored_by_scene


def _review_row_map(
    review_rows: list[dict[str, object]],
) -> dict[int, dict[str, object]]:
    review_by_scene: dict[int, dict[str, object]] = {}

    for row_number, row in enumerate(review_rows, start=1):
        scene_number = row.get("scene_number")

        if not isinstance(scene_number, int) or isinstance(scene_number, bool):
            raise ValueError(
                f"review row {row_number} scene_number must be an integer."
            )

        if scene_number in review_by_scene:
            raise ValueError(f"duplicate review scene_number: {scene_number}")

        _validate_review_metadata(row, scene_number)
        review_by_scene[scene_number] = row

    return review_by_scene


def _validate_review_metadata(row: dict[str, object], scene_number: int) -> None:
    watermark = row.get("watermark")
    subtitle_safe_zone = row.get("subtitle_safe_zone")

    if not isinstance(watermark, str) or watermark not in WATERMARK_VALUES:
        allowed = ", ".join(sorted(WATERMARK_VALUES))

        raise ValueError(
            f"review row {scene_number} watermark must be one of {allowed}."
        )

    if (
        not isinstance(subtitle_safe_zone, str)
        or subtitle_safe_zone not in SUBTITLE_SAFE_ZONE_VALUES
    ):
        allowed = ", ".join(sorted(SUBTITLE_SAFE_ZONE_VALUES))

        raise ValueError(
            "review row "
            f"{scene_number} subtitle_safe_zone must be one of {allowed}."
        )


def _validate_required_scene_metadata(
    *,
    scored_scenes: list[ScoredScene],
    detected_by_scene: dict[int, DetectedScene],
    review_by_scene: dict[int, dict[str, object]],
) -> None:
    for scored_scene in scored_scenes:
        if not scored_scene.eligible:
            continue

        if not set(scored_scene.purposes).intersection(PURPOSE_ORDER):
            continue

        if scored_scene.scene_number not in detected_by_scene:
            raise ValueError(
                "eligible scored scene "
                f"{scored_scene.scene_number} has no matching DetectedScene."
            )

        if scored_scene.scene_number not in review_by_scene:
            raise ValueError(
                "eligible scored scene "
                f"{scored_scene.scene_number} has no matching review row."
            )


def _select_scored_scene_for_purpose(
    *,
    purpose: str,
    scored_scenes: list[ScoredScene],
    review_by_scene: dict[int, dict[str, object]],
    used_scene_numbers: set[int],
) -> ScoredScene:
    candidates = [
        scene
        for scene in scored_scenes
        if scene.eligible
        and scene.scene_number not in used_scene_numbers
        and purpose in scene.purposes
        and _is_brand_safe(scene, review_by_scene)
    ]

    if not candidates:
        raise ValueError(f"no eligible safe scene exists for required purpose {purpose}.")

    return sorted(
        candidates,
        key=lambda scene: (
            -scene.score,
            scene.scene_number,
        ),
    )[0]


def _is_brand_safe(
    scored_scene: ScoredScene,
    review_by_scene: dict[int, dict[str, object]],
) -> bool:
    review_row = review_by_scene[scored_scene.scene_number]

    return review_row["watermark"] not in UNSAFE_WATERMARKS
