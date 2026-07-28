from __future__ import annotations

from dataclasses import dataclass
from typing import List

from applications.ai_money_factory.collectors.registry import CollectorRegistry
from applications.ai_money_factory.core.opportunity_engine import (
    Opportunity,
    OpportunityEngine,
    Product,
)


@dataclass
class DailyMission:
    top_products: List[Opportunity]
    total_products: int


class DailyOpportunityEngine:

    def __init__(self, registry: CollectorRegistry):
        self.registry = registry
        self.engine = OpportunityEngine()

    def generate(self, products: List[Product]) -> DailyMission:

        ranked = [
            self.engine.calculate(product)
            for product in products
        ]

        ranked.sort(
            key=lambda item: item.win_score,
            reverse=True,
        )

        return DailyMission(
            top_products=ranked[:20],
            total_products=len(ranked),
        )

    def collector_health(self):
        return self.registry.health()

    def collector_data(self):
        return self.registry.collect_all()
