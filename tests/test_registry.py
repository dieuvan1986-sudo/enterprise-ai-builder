import pytest

from registry.base import Registry


def test_register_and_get() -> None:
    registry = Registry[str]()

    registry.register("hello", "world")

    assert registry.get("hello") == "world"


def test_has() -> None:
    registry = Registry[int]()

    registry.register("value", 100)

    assert registry.has("value") is True
    assert registry.has("missing") is False


def test_remove() -> None:
    registry = Registry[str]()

    registry.register("a", "A")

    registry.remove("a")

    assert registry.has("a") is False


def test_clear() -> None:
    registry = Registry[int]()

    registry.register("one", 1)
    registry.register("two", 2)

    registry.clear()

    assert registry.names() == []


def test_names_are_sorted() -> None:
    registry = Registry[int]()

    registry.register("z", 1)
    registry.register("a", 2)
    registry.register("m", 3)

    assert registry.names() == [
        "a",
        "m",
        "z",
    ]


def test_get_unknown_item() -> None:
    registry = Registry[str]()

    with pytest.raises(
        ValueError,
        match="Unknown item: missing",
    ):
        registry.get("missing")


def test_overwrite_existing_item() -> None:
    registry = Registry[int]()

    registry.register("count", 1)
    registry.register("count", 2)

    assert registry.get("count") == 2
