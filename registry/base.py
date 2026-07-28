from typing import Generic, TypeVar


T = TypeVar("T")


class Registry(Generic[T]):
    """
    Generic registry for Enterprise AI Builder.

    This class provides a reusable registry implementation that can be
    specialized for Actions, Services, Plugins, Tools, LLMs and other
    framework components.
    """

    def __init__(self) -> None:
        self._items: dict[str, T] = {}

    def register(
        self,
        name: str,
        item: T,
    ) -> None:
        """
        Register an item.
        """
        self._items[name] = item

    def get(self, name: str) -> T:
        """
        Return a registered item.
        """
        if name not in self._items:
            raise ValueError(f"Unknown item: {name}")

        return self._items[name]

    def has(self, name: str) -> bool:
        """
        Return True if an item exists.
        """
        return name in self._items

    def remove(self, name: str) -> None:
        """
        Remove an item.
        """
        if name in self._items:
            del self._items[name]

    def names(self) -> list[str]:
        """
        Return all registered names.
        """
        return sorted(self._items.keys())

    def clear(self) -> None:
        """
        Remove all items.
        """
        self._items.clear()
