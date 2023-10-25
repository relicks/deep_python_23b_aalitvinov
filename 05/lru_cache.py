"""Содержит решение первого пункта HW05."""
from collections.abc import Hashable
from typing import Any


class LRUCache:
    __slots__ = ["data", "deck", "limit"]

    def __init__(self, limit: int = 42) -> None:
        self.data: dict[Hashable, Any] = {}
        self.deck: dict[Hashable, None] = {}
        self.limit = limit

    def get(self, key: Hashable) -> Any | None:
        try:
            value = self.data[key]  # O(1)
        except KeyError:
            return None

        if key not in self.deck:  # O(1)
            self.deck[key] = None  # O(1)
        else:
            del self.deck[key]  # O(1)
            self.deck[key] = None  # O(1)

        if len(self.deck) > len(self.data):  # O(1)
            first_key = next(iter(self.deck))  # O(1)
            del self.deck[first_key]  # O(1)
        return value

    def set(self, key: Hashable, value: Any) -> None:
        self.data[key] = value  # O(1)
        if key not in self.deck:  # O(1)
            self.deck[key] = None  # O(1)
        else:
            del self.deck[key]  # O(1)
            self.deck[key] = None  # O(1)

        if len(self.data) == self.limit + 1:  # O(1)
            first_key = next(iter(self.deck))  # O(1)
            del self.data[first_key]  # O(1)

    def to_dict(self) -> dict[Hashable, Any]:
        return {k: self.data[k] for k in self.deck if k in self.data}

    def __repr__(self) -> str:
        return repr(self.to_dict())
