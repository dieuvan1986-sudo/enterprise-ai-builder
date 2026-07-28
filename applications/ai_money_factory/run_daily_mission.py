from __future__ import annotations

from applications.ai_money_factory.collectors.registry import CollectorRegistry
from applications.ai_money_factory.collectors.shopee_collector import (
    ShopeeCollector,
    ShopeeProductSignal,
)
from applications.ai_money_factory.core.daily_brief_formatter import (
    DailyBriefFormatter,
)
from applications.ai_money_factory.core.daily_mission_service import (
    DailyMissionService,
)
from applications.ai_money_factory.core.openclaw_telegram_sender import (
    OpenClawTelegramSender,
)


def build_shopee_collector() -> ShopeeCollector:
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

    return shopee


def main() -> None:
    registry = CollectorRegistry()
    registry.register(build_shopee_collector())

    mission_service = DailyMissionService(registry)
    mission = mission_service.generate()

    formatter = DailyBriefFormatter()
    brief = formatter.format(mission)

    print(brief)

    sender = OpenClawTelegramSender()
    sender.send(brief)

    print()
    print("Daily Mission delivered to Telegram successfully.")


if __name__ == "__main__":
    main()
