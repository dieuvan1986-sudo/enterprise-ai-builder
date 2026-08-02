from __future__ import annotations

from dataclasses import dataclass

from applications.ai_money_factory.core.creative_engine import (
    CreativeConcept,
)


@dataclass(slots=True)
class VideoScene:
    scene_number: int
    duration_seconds: int
    purpose: str
    narration: str
    visual_prompt: str
    text_overlay: str | None = None


@dataclass(slots=True)
class VideoPackage:
    title: str
    hook: str
    scenes: list[VideoScene]
    cta: str
    total_duration_seconds: int
    format: str = "9:16"
    production_style: str = "faceless_ai_video"


class VideoFactory:
    """
    Convert a winning CreativeConcept into a production-ready
    short-form affiliate video package.

    MVP format:
    - Vertical 9:16
    - Approximately 25 seconds
    - Faceless
    - Visual-first
    - Five scenes:
      hook -> pour -> dip/macro -> product reveal -> CTA
    """

    def build(
        self,
        concept: CreativeConcept,
    ) -> VideoPackage:

        script = list(concept.script)

        while len(script) < 3:
            script.append("")

        scenes = [
            VideoScene(
                scene_number=1,
                duration_seconds=3,
                purpose="HOOK",
                narration=concept.hook,
                text_overlay=concept.hook,
                visual_prompt=(
                    "Vertical 9:16 TikTok opening shot. "
                    "Create the strongest visually permitted action "
                    "from the concept immediately in the first frame. "
                    "Use an extreme close-up or macro food shot, "
                    "strong motion, clean composition and no face. "
                    "Do not show price. "
                    f"Creative direction: {concept.visual_idea}"
                ),
            ),
            VideoScene(
                scene_number=2,
                duration_seconds=5,
                purpose="POUR_ACTION",
                narration=script[0],
                visual_prompt=(
                    "Vertical 9:16 food cinematography. "
                    "Focus on a clear pouring action supported by the "
                    "creative direction. Use close-up framing and "
                    "visible movement. Keep the scene realistic and "
                    "do not introduce unverified product claims. "
                    f"Creative direction: {concept.visual_idea}"
                ),
            ),
            VideoScene(
                scene_number=3,
                duration_seconds=6,
                purpose="DIP_MACRO",
                narration=script[1],
                visual_prompt=(
                    "Vertical 9:16 macro food shot. "
                    "Show a dipping action and close-up movement of "
                    "the sauce as permitted by the creative concept. "
                    "Prioritize texture, motion and visual retention. "
                    "No face, no price, no unverified text. "
                    f"Creative direction: {concept.visual_idea}"
                ),
            ),
            VideoScene(
                scene_number=4,
                duration_seconds=6,
                purpose="PRODUCT_REVEAL",
                narration=script[2],
                visual_prompt=(
                    "Vertical 9:16 product recognition shot. "
                    "Keep the food in the foreground and reveal the "
                    "product packaging clearly in the composition. "
                    "The product label should face the camera. "
                    "Use subtle camera movement rather than a static "
                    "pack shot. Do not invent packaging text, price, "
                    "certifications or product claims. "
                    f"Creative direction: {concept.visual_idea}"
                ),
            ),
            VideoScene(
                scene_number=5,
                duration_seconds=5,
                purpose="CTA",
                narration=concept.cta,
                text_overlay="Xem sản phẩm trong giỏ",
                visual_prompt=(
                    "Vertical 9:16 closing shot for an affiliate video. "
                    "Show the product together with the food in a clean "
                    "composition. Use a gentle camera push-in. "
                    "Leave safe empty space for a CTA overlay. "
                    "No price and no unverified claims. "
                    f"Creative direction: {concept.visual_idea}"
                ),
            ),
        ]

        total_duration = sum(
            scene.duration_seconds
            for scene in scenes
        )

        return VideoPackage(
            title=concept.name,
            hook=concept.hook,
            scenes=scenes,
            cta=concept.cta,
            total_duration_seconds=total_duration,
        )
