from __future__ import annotations

from dataclasses import dataclass
from typing import List

from pytrends.request import TrendReq


@dataclass
class TrendItem:
    keyword: str
    score: int


class GoogleTrendsCollector:

    def __init__(self, geo: str = "VN", hl: str = "vi-VN"):
        self._client = TrendReq(
            hl=hl,
            tz=420,
        )
        self._geo = geo

    def trending_searches(self) -> List[TrendItem]:

        data = self._client.trending_searches(
            pn=self._geo
        )

        results: List[TrendItem] = []

        for keyword in data.iloc[:, 0].tolist():
            results.append(
                TrendItem(
                    keyword=str(keyword),
                    score=100,
                )
            )

        return results

    def interest(self, keyword: str) -> int:

        self._client.build_payload(
            [keyword],
            geo=self._geo,
        )

        interest = self._client.interest_over_time()

        if interest.empty:
            return 0

        return int(
            interest[keyword].iloc[-1]
        )
