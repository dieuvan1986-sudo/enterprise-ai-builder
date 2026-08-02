from dataclasses import dataclass, field
from typing import List


@dataclass
class Product:
    name: str
    category: str
    price: float
    commission: float
    trend_score: float
    competition_score: float
    video_score: float
    demand_score: float
    data_confidence: float = 1.0

    # Facts that are allowed to be used in consumer-facing content.
    # These must come from verified product information, not AI inference.
    verified_facts: List[str] = field(default_factory=list)

    # Visual facts explicitly verified from official product images,
    # packaging, seller materials, or other approved evidence.
    # Creative AI may depict only visual uses supported by this list.
    verified_visual_facts: List[str] = field(default_factory=list)

    # Human-readable provenance for fact checking.
    fact_source: str | None = None

    # Price is volatile. True only when recently checked.
    price_verified: bool = False


@dataclass
class Opportunity:
    product: Product
    win_score: float
    priority: str
    action: str
    reasons: List[str]
    confidence: str


class OpportunityEngine:

    def calculate(self, product: Product) -> Opportunity:

        score = (
            product.trend_score * 0.30
            + product.demand_score * 0.25
            + product.commission * 0.20
            + product.video_score * 0.15
            + (10 - product.competition_score) * 0.10
        )

        if product.data_confidence < 0.6:
            priority = "UNKNOWN"
            action = "COLLECT_MORE_DATA"
        elif score >= 8.5:
            priority = "HIGH"
            action = "DO_NOW"
        elif score >= 7:
            priority = "MEDIUM"
            action = "WATCH"
        else:
            priority = "LOW"
            action = "SKIP"

        if product.data_confidence >= 0.8:
            confidence = "HIGH"
        elif product.data_confidence >= 0.6:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        reasons = []

        if product.trend_score >= 8:
            reasons.append("Trending")

        if product.commission >= 8:
            reasons.append("High commission")

        if product.video_score >= 8:
            reasons.append("Easy AI video")

        if product.demand_score >= 8:
            reasons.append("High demand")

        if product.competition_score <= 4:
            reasons.append("Low competition")

        if product.data_confidence < 0.6:
            reasons.append("Insufficient data")

        return Opportunity(
            product=product,
            win_score=round(score, 2),
            priority=priority,
            action=action,
            reasons=reasons,
            confidence=confidence,
        )
