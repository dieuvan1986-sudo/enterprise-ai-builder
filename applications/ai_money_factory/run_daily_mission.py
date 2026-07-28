from __future__ import annotations

from applications.ai_money_factory.collectors.registry import CollectorRegistry
from applications.ai_money_factory.collectors.shopee_collector import (
    ShopeeCollector,
    ShopeeProductSignal,
)
from applications.ai_money_factory.core.daily_mission_service import (
    DailyMissionService,
)


def main() -> None:
    registry = CollectorRegistry()
    shopee = ShopeeCollector()

    products = [
        ShopeeProductSignal(
            name="Xot Pho Mai Tanzy Foods 500g",
            category="Bach Hoa Online",
            price=64_000,
            commission_rate=16.5,
            sold_count=200_000,
            sales_growth_7d=28_600,
            rating=4.9,
            creator_count=8_500,
        ),
        ShopeeProductSignal(
            name="Mi Indomie Bo Cay",
            category="Bach Hoa Online",
            price=210_000,
            commission_rate=8.5,
            sales_growth_7d=12_200,
        ),
        ShopeeProductSignal(
            name="Khan Giay TopGia",
            category="Nha Cua Doi Song",
            price=65_000,
            commission_rate=11.5,
            sold_count=29_600,
        ),
        ShopeeProductSignal(
            name="Tui Tai Lieu 13 Ngan",
            category="Van Phong Pham",
            price=42_999,
            commission_rate=13.5,
            sales_growth_7d=1_900,
        ),
        ShopeeProductSignal(
            name="Banh Trang Bo Toi",
            category="Bach Hoa Online",
            price=33_999,
            commission_rate=8.5,
            sold_count=80_200,
        ),
    ]

    for product in products:
        shopee.add_product(product)

    registry.register(shopee)

    service = DailyMissionService(registry)
    mission = service.generate()

    print("=== MON HAY 365 - DAILY MISSION ===")
    print(f"Products analyzed: {mission.total_products}")
    print()

    for rank, opportunity in enumerate(
        mission.top_products,
        start=1,
    ):
        product = opportunity.product

        print(f"#{rank} {product.name}")
        print(f"  Price:     {product.price:,.0f} VND")
        print(f"  Win Score: {opportunity.win_score}/10")
        print(f"  Priority:   {opportunity.priority}")
        print(f"  Confidence: {opportunity.confidence}")
        print(f"  Action:     {opportunity.action}")
        print(
            "  Reasons:   "
            + (
                ", ".join(opportunity.reasons)
                if opportunity.reasons
                else "None"
            )
        )
        print()


if __name__ == "__main__":
    main()
