from __future__ import annotations

from applications.ai_money_factory.collectors.shopee_collector import (
    ShopeeProductSignal,
)
from applications.ai_money_factory.core.opportunity_engine import Product


class ShopeeSignalMapper:
    """
    Convert Shopee market signals into normalized Product scores.

    All OpportunityEngine inputs use a 0-10 scale.
    Data confidence represents how complete the observed source data is.
    """

    def map(self, signal: ShopeeProductSignal) -> Product:
        return Product(
            name=signal.name,
            category=signal.category,
            price=signal.price,
            commission=self._commission_score(signal.commission_rate),
            trend_score=self._trend_score(signal.sales_growth_7d),
            competition_score=self._competition_score(
                signal.creator_count
            ),
            video_score=self._video_score(signal),
            demand_score=self._demand_score(
                signal.sold_count,
                signal.rating,
            ),
            data_confidence=self._data_confidence(signal),
        )

    @staticmethod
    def _commission_score(rate: float) -> float:
        return min(max(rate / 2.0, 0.0), 10.0)

    @staticmethod
    def _trend_score(growth_7d: int | None) -> float:
        if growth_7d is None:
            return 5.0

        if growth_7d >= 20_000:
            return 10.0
        if growth_7d >= 10_000:
            return 9.0
        if growth_7d >= 5_000:
            return 8.0
        if growth_7d >= 2_000:
            return 7.0
        if growth_7d >= 1_000:
            return 6.0
        if growth_7d >= 500:
            return 5.0
        if growth_7d >= 100:
            return 4.0

        return 2.0

    @staticmethod
    def _demand_score(
        sold_count: int | None,
        rating: float | None,
    ) -> float:
        if sold_count is None:
            sales_score = 5.0
        elif sold_count >= 100_000:
            sales_score = 10.0
        elif sold_count >= 50_000:
            sales_score = 9.0
        elif sold_count >= 20_000:
            sales_score = 8.0
        elif sold_count >= 10_000:
            sales_score = 7.0
        elif sold_count >= 5_000:
            sales_score = 6.0
        elif sold_count >= 1_000:
            sales_score = 5.0
        else:
            sales_score = 3.0

        if rating is None:
            rating_score = 5.0
        else:
            rating_score = min(max(rating * 2.0, 0.0), 10.0)

        return round(
            (sales_score * 0.8) + (rating_score * 0.2),
            2,
        )

    @staticmethod
    def _competition_score(
        creator_count: int | None,
    ) -> float:
        if creator_count is None:
            return 5.0

        if creator_count >= 10_000:
            return 10.0
        if creator_count >= 5_000:
            return 9.0
        if creator_count >= 2_000:
            return 8.0
        if creator_count >= 1_000:
            return 7.0
        if creator_count >= 500:
            return 6.0
        if creator_count >= 100:
            return 5.0

        return 3.0

    @staticmethod
    def _video_score(signal: ShopeeProductSignal) -> float:
        score = 5.0

        if signal.sales_growth_7d is not None:
            if signal.sales_growth_7d >= 10_000:
                score += 2.0
            elif signal.sales_growth_7d >= 2_000:
                score += 1.0

        if signal.sold_count is not None:
            if signal.sold_count >= 50_000:
                score += 1.0

        return min(score, 10.0)

    @staticmethod
    def _data_confidence(signal: ShopeeProductSignal) -> float:
        """
        Measure completeness of the observed Shopee signal.

        Core fields are always available:
        name, category, price and commission.

        Optional market signals contribute to confidence:
        - sold_count
        - sales_growth_7d
        - rating
        - creator_count
        """

        optional_signals = (
            signal.sold_count,
            signal.sales_growth_7d,
            signal.rating,
            signal.creator_count,
        )

        available = sum(
            value is not None
            for value in optional_signals
        )

        return round(available / len(optional_signals), 2)
