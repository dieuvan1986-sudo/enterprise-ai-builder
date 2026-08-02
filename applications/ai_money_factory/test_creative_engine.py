from __future__ import annotations

from applications.ai_money_factory.core.creative_engine import (
    CreativeEngine,
)
from applications.ai_money_factory.core.creative_scoring_engine import (
    CreativeScoringEngine,
)
from applications.ai_money_factory.core.openclaw_creative_provider import (
    OpenClawCreativeProvider,
)
from applications.ai_money_factory.core.opportunity_engine import Product


def main() -> None:
    product = Product(
        name="Xot Pho Mai Tanzy Foods 500g",
        category="Bach Hoa Online",

        # Commercial data is intentionally not exposed as a verified
        # consumer-facing claim in this creative test.
        price=0.0,
        commission=8.25,

        # Internal strategy signals only.
        trend_score=10.0,
        competition_score=9.0,
        video_score=8.0,
        demand_score=9.96,
        data_confidence=1.0,

        # Facts allowed in spoken/written consumer-facing content.
        verified_facts=[
            "Tên sản phẩm: Xot Pho Mai Tanzy Foods 500g",
            "Thương hiệu: Tanzy Foods",
            "Khối lượng: 500g",
        ],

        # Visual evidence allowed for AI creative generation.
        verified_visual_facts=[
            (
                "Hình ảnh sản phẩm chính thức thể hiện "
                "xốt phô mai dùng cùng món ăn."
            ),
            (
                "Xốt được phép thể hiện bằng cảnh rưới "
                "hoặc chấm cùng món ăn."
            ),
            (
                "Có thể dùng cảnh cận và macro để thể hiện "
                "chuyển động của xốt khi rưới hoặc chấm."
            ),
        ],

        fact_source="Shopee / Tanzy Foods",
        price_verified=False,
    )

    provider = OpenClawCreativeProvider(
        session_key="agent:main:ai-money-factory-creative-tanzy",
        thinking="minimal",
    )

    creative_engine = CreativeEngine(provider)
    scoring_engine = CreativeScoringEngine()

    print("=== MON HAY 365 - CREATIVE LAB ===")
    print(f"Product: {product.name}")
    print()

    print("=== VERIFIED PRODUCT FACTS ===")
    for fact in product.verified_facts:
        print(f"- {fact}")

    print()
    print("=== VERIFIED VISUAL FACTS ===")
    for fact in product.verified_visual_facts:
        print(f"- {fact}")

    print()
    print("Generating 3 TikTok concepts with GPT-5.5...")
    print()

    concepts = creative_engine.generate_concepts(
        product=product,
        count=3,
    )

    ranked = scoring_engine.rank(concepts)

    print("=== CREATIVE RANKING ===")
    print()

    for index, result in enumerate(ranked, start=1):
        concept = result.concept

        print("=" * 60)
        print(f"#{index} {concept.name}")
        print("=" * 60)

        print(f"Angle:       {concept.angle}")
        print(f"Audience:    {concept.target_audience}")
        print(f"Hook:        {concept.hook}")
        print()

        print("SCORES:")
        print(f"  Hook:       {result.hook_score}/10")
        print(f"  Visual:     {result.visual_score}/10")
        print(f"  Conversion: {result.conversion_score}/10")
        print(f"  Brand Fit:  {result.brand_fit_score}/10")
        print(f"  Safety:     {result.claim_safety_score}/10")
        print()

        print(f"TOTAL:  {result.total_score}/10")
        print(f"STATUS: {result.status}")

        if result.warnings:
            print()
            print("WARNINGS:")

            for warning in result.warnings:
                print(f"- {warning}")

        print()
        print("SCRIPT:")

        for line in concept.script:
            print(f"- {line}")

        print()
        print(f"CTA: {concept.cta}")
        print()
        print(f"VISUAL: {concept.visual_idea}")
        print()

    winner = ranked[0]

    print("=" * 60)
    print("🏆 CREATIVE WINNER")
    print("=" * 60)
    print(f"Concept: {winner.concept.name}")
    print(f"Score:   {winner.total_score}/10")
    print(f"Status:  {winner.status}")

    if winner.status == "READY":
        print("Decision: APPROVED_FOR_VIDEO_FACTORY")
    elif winner.status == "PROMISING":
        print("Decision: REVIEW_BEFORE_PRODUCTION")
    elif winner.status == "NEEDS_REVIEW":
        print("Decision: BLOCKED_BY_SAFETY_REVIEW")
    else:
        print("Decision: REJECTED")


if __name__ == "__main__":
    main()
