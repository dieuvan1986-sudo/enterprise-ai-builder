from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseCollector(ABC):
    """
    Base interface for all market data collectors.
    """

    name: str = "base"

    @abstractmethod
    def collect(self) -> Any:
        """
        Collect raw data from the source.
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """
        Return True if the data source is available.
        """
        raise NotImplementedError
