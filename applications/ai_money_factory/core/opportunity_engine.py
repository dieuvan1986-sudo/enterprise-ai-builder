from dataclasses import dataclass
from typing import List


@dataclass
class Product:
    name: str
    category: str
    price: float
    commission: float
    trend_score: int
    competition_score: int
    video_score: int
    demand_score: int


@dataclass
class Opportunity:
    product: Product
    win_score: float
    priority: str
    action: str
    reasons: List[str]


class OpportunityEngine:

    def calculate(self, product: Product) -> Opportunity:

        score = (
            product.trend_score * 0.30 +
            product.demand_score * 0.25 +
            product.commission * 0.20 +
            product.video_score * 0.15 +
            (10 - product.competition_score) * 0.10
        )

        if score >= 8.5:
            priority = "HIGH"
            action = "DO_NOW"
        elif score >= 7:
            priority = "MEDIUM"
            action = "WATCH"
        else:
            priority = "LOW"
            action = "SKIP"

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

        return Opportunity(
            product=product,
            win_score=round(score, 2),
            priority=priority,
            action=action,
            reasons=reasons,
        )
