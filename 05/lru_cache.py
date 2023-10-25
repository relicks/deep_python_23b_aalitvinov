from collections import deque
from collections.abc import Hashable
from typing import Any


class LRUCache:
    def __init__(self, limit: int = 42) -> None:
        self.data: dict[Hashable, Any] = {}
        self.deck: deque[Hashable] = deque(maxlen=limit + 1)
        self.limit = limit

    def get(self, key: Hashable) -> Any | None:
        try:
            value = self.data[key]
        except KeyError:
            return None
        else:
            if key != self.deck[-1]:
                self.deck.append(key)

            if len(self.deck) > len(self.data):
                self.deck.popleft()
            return value

    def set(self, key, value) -> None:
        self.data[key] = value
        self.deck.append(key)
        if len(self.data) == self.limit + 1:
            self.data.pop(self.deck.popleft())

    def __repr__(self) -> str:
        return repr(self.data)
