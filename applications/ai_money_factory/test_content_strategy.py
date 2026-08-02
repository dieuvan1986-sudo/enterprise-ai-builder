from __future__ import annotations

from applications.ai_money_factory.core.content_strategy_engine import (
    ContentStrategyEngine,
)
from applications.ai_money_factory.core.opportunity_engine import Product


def main() -> None:
    product = Product(
        name="Xot Pho Mai Tanzy Foods 500g",
        category="Bach Hoa Online",
        price=64_000,
        commission=8.25,
        trend_score=10.0,
        competition_score=9.0,
        video_score=8.0,
        demand_score=9.96,
        data_confidence=1.0,
    )

    engine = ContentStrategyEngine()
    mission = engine.generate(product)

    print("=== MON HAY 365 - VIDEO MISSION #001 ===")
    print()
    print(f"Product: {mission.product_name}")
    print(f"Angle:   {mission.angle.name}")
    print()
    print(f"HOOK: {mission.script.hook}")
    print()

    print("SCRIPT:")
    for line in mission.script.body:
        print(f"- {line}")

    print()
    print(f"CTA: {mission.script.cta}")
    print()
    print(f"Caption: {mission.caption}")
    print(f"Hashtags: {' '.join(mission.hashtags)}")
    print()
    print(f"Scenes: {len(mission.scenes)}")

    for scene in mission.scenes:
        print()
        print(f"Scene {scene.order} ({scene.duration_seconds}s)")
        print(f"  Voice:  {scene.voiceover}")
        print(f"  Text:   {scene.on_screen_text}")
        print(f"  Visual: {scene.visual_prompt}")


if __name__ == "__main__":
    main()
