from __future__ import annotations

from typing import Iterable

from applications.ai_money_factory.core.product_facts import ProductFacts


class ProductFactCollector:
    """
    Converts verified product information into ProductFacts.

    This collector does not scrape websites directly.
    It normalizes trusted product information coming from
    approved sources such as Shopee, official product pages,
    or verified seller data.
    """

    def collect(
        self,
        *,
        product_id: str,
        name: str,
        brand: str | None = None,
        category: str | None = None,
        weight: str | None = None,
        description: str | None = None,
        verified_facts: Iterable[str] = (),
        ingredients: Iterable[str] = (),
        usage: Iterable[str] = (),
        warnings: Iterable[str] = (),
        price: float | None = None,
        affiliate_url: str | None = None,
        source: str | None = None,
        source_url: str | None = None,
    ) -> ProductFacts:
        return ProductFacts(
            product_id=product_id,
            name=name,
            brand=brand,
            category=category,
            weight=weight,
            description=description,
            verified_facts=list(verified_facts),
            ingredients=list(ingredients),
            usage=list(usage),
            warnings=list(warnings),
            price=price,
            price_verified=price is not None,
            affiliate_url=affiliate_url,
            source=source,
            source_url=source_url,
        )
