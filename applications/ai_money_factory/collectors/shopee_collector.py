from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .base import BaseCollector


@dataclass(slots=True)
class ShopeeProductSignal:
    """
    Raw market signal observed from Shopee Affiliate.

    This model stores source data only.
    Opportunity scoring belongs to the core layer.
    """

    name: str
    category: str
    price: float
    commission_rate: float

    sold_count: int | None = None
    sales_growth_7d: int | None = None
    rating: float | None = None
    creator_count: int | None = None

    affiliate_url: str | None = None
    source: str = "shopee_affiliate"


class ShopeeCollector(BaseCollector):
    """
    Collector for Shopee Affiliate product signals.

    MVP implementation accepts verified market observations manually.
    A future adapter may replace this input mechanism with an official
    or otherwise approved automated data source.
    """

    name = "shopee"

    def __init__(self) -> None:
        self._products: list[ShopeeProductSignal] = []

    def add_product(self, product: ShopeeProductSignal) -> None:
        self._products.append(product)

    def collect(self) -> list[dict[str, Any]]:
        return [asdict(product) for product in self._products]

    def health_check(self) -> bool:
        return True
