from __future__ import annotations

from typing import Dict, List

from .base import BaseCollector


class CollectorRegistry:

    def __init__(self):
        self._collectors: Dict[str, BaseCollector] = {}

    def register(self, collector: BaseCollector) -> None:
        self._collectors[collector.name] = collector

    def unregister(self, name: str) -> None:
        self._collectors.pop(name, None)

    def get(self, name: str) -> BaseCollector:
        return self._collectors[name]

    def all(self) -> List[BaseCollector]:
        return list(self._collectors.values())

    def available(self) -> List[str]:
        return sorted(self._collectors.keys())

    def health(self) -> Dict[str, bool]:
        status = {}

        for collector in self._collectors.values():
            try:
                status[collector.name] = collector.health_check()
            except Exception:
                status[collector.name] = False

        return status

    def collect_all(self) -> Dict[str, object]:
        data = {}

        for collector in self._collectors.values():
            try:
                data[collector.name] = collector.collect()
            except Exception as ex:
                data[collector.name] = {
                    "error": str(ex)
                }

        return data
