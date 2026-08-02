from __future__ import annotations

from applications.ai_money_factory.core.opportunity_engine import Product
from applications.ai_money_factory.core.product_facts import ProductFacts


class ProductFactMapper:
    """
    Converts ProductFacts into the Product model consumed by the
    Opportunity Engine and Creative Engine.

    Verified factual claims and verified visual facts are preserved
    so downstream creative generation stays grounded in evidence.
    """

    @staticmethod
    def to_product(facts: ProductFacts) -> Product:
        return Product(
            name=facts.name,
            category=facts.category or "Unknown",
            price=facts.price or 0.0,
            commission=0.0,
            trend_score=0.0,
            competition_score=0.0,
            video_score=0.0,
            demand_score=0.0,
            data_confidence=facts.confidence,
            verified_facts=list(facts.verified_facts),
            verified_visual_facts=list(
                facts.verified_visual_facts
            ),
            fact_source=facts.source,
            price_verified=facts.price_verified,
        )
