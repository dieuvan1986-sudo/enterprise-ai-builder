from __future__ import annotations

from applications.ai_money_factory.collectors.registry import CollectorRegistry
from applications.ai_money_factory.collectors.shopee_collector import (
    ShopeeProductSignal,
)
from applications.ai_money_factory.core.daily_opportunity_engine import (
    DailyMission,
    DailyOpportunityEngine,
)
from applications.ai_money_factory.core.opportunity_engine import Product
from applications.ai_money_factory.core.shopee_signal_mapper import (
    ShopeeSignalMapper,
)


class DailyMissionService:
    """
    Orchestrates market collectors and converts supported source signals
    into normalized Products for the DailyOpportunityEngine.

    Source-specific mapping stays outside the core ranking engine.
    """

    def __init__(self, registry: CollectorRegistry) -> None:
        self.registry = registry
        self.engine = DailyOpportunityEngine(registry)
        self.shopee_mapper = ShopeeSignalMapper()

    def generate(self) -> DailyMission:
        collected = self.registry.collect_all()
        products: list[Product] = []

        shopee_data = collected.get("shopee", [])

        if isinstance(shopee_data, list):
            products.extend(self._map_shopee(shopee_data))

        return self.engine.generate(products)

    def _map_shopee(
        self,
        raw_products: list[object],
    ) -> list[Product]:
        products: list[Product] = []

        for raw in raw_products:
            if not isinstance(raw, dict):
                continue

            try:
                signal = ShopeeProductSignal(**raw)
                products.append(
                    self.shopee_mapper.map(signal)
                )
            except (TypeError, ValueError):
                continue

        return products
