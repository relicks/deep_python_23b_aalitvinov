"""Содержит решение первого пункта HW09."""
from collections.abc import Hashable
from typing import Any


class LRUCache:
    """LRU cache implementation based on two `dict`s.

    Time complexity of `get` and `set` methods is O(1) on average and
    O(n) in the worst case.
    """

    def __init__(self, limit: int | None = None) -> None:
        """
        :param limit: The size of LRU cache, must be positive. If `None`, then no limit.
        """
        self._data: dict[Hashable, Any] = {}
        self._deck: dict[Hashable, None] = {}
        self._limit = limit

    def _update_deck(self, key: Hashable) -> None:
        if key not in self._deck:
            self._deck[key] = None
        else:  # ? move this key to the top, since it is being used
            del self._deck[key]
            self._deck[key] = None

        # ? if deck is bigger than cache data -> delete first deck element
        if len(self._deck) > len(self._data):
            first_key = next(iter(self._deck))
            del self._deck[first_key]

    def get(self, key: Hashable) -> Any | None:
        try:
            value = self._data[key]
        except KeyError:
            return None
        else:
            self._update_deck(key)
            return value

    def set(self, key: Hashable, value: Any) -> None:
        self._data[key] = value

        self._update_deck(key)

        if self._limit and self._limit > 0 and len(self._data) == self._limit + 1:
            first_key = next(iter(self._deck))
            del self._data[first_key]

        self._update_deck(key)

    def to_dict(self) -> dict[Hashable, Any]:
        return {k: self._data[k] for k in self._deck if k in self._data}

    def __repr__(self) -> str:  # pragma: no cover
        return repr(self.to_dict())

    def __iter__(self):
        return iter(self.to_dict().items())


if __name__ == "__main__":
    ...
