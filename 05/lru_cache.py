"""Содержит решение первого пункта HW05."""
from abc import ABC, abstractmethod
from collections.abc import Hashable
from typing import Any


# from https://docs.python.org/3/howto/descriptor.html#validator-class
class Validator(ABC):  # from hw04 # pragma: no cover
    """Abstract base class for Validator data descriptors."""

    def __set_name__(self, owner: type, name: str):
        # pylint: disable-next=attribute-defined-outside-init
        self._private_name = "_" + name

    def __get__(self, obj: object, objtype: type | None = None):
        return getattr(obj, self._private_name)

    def __set__(self, obj: object, value: Any):
        err = self.validate(value)
        if err is not None:
            raise err
        setattr(obj, self._private_name, value)

    @abstractmethod
    def validate(self, value: Any) -> Exception | None:
        pass


class NaturalIntValidator(Validator):
    """Data descriptor that checks input to be valid positive int."""

    def validate(self, value: int) -> TypeError | ValueError | None:
        if not isinstance(value, int):
            return TypeError(f"Expected {value!r} to be of type int.")
        if not value > 0:
            return ValueError(f"Expected {value!r} to be positive.")
        return None


class LRUCache:
    """LRU cache implementation based on two `dict`s.

    Time complexity of `get` and `set` methods is O(1) on average and
    O(n) in the worst case.

    :param limit: The size of LRU cache, must be positive
    """

    _limit = NaturalIntValidator()

    def __init__(self, limit: int = 42) -> None:
        self._data: dict[Hashable, Any] = {}
        self._deck: dict[Hashable, None] = {}
        self._limit = limit

    def get(self, key: Hashable) -> Any | None:
        try:
            value = self._data[key]  # O(1)
        except KeyError:
            return None

        if key not in self._deck:  # O(1)
            self._deck[key] = None  # O(1)
        else:
            del self._deck[key]  # O(1)
            self._deck[key] = None  # O(1)

        if len(self._deck) > len(self._data):  # O(1)
            first_key = next(iter(self._deck))  # O(1)
            del self._deck[first_key]  # O(1)
        return value

    def set(self, key: Hashable, value: Any) -> None:
        self._data[key] = value  # O(1)
        if key not in self._deck:  # O(1)
            self._deck[key] = None  # O(1)
        else:
            del self._deck[key]  # O(1)
            self._deck[key] = None  # O(1)

        if len(self._data) == self._limit + 1:  # O(1)
            first_key = next(iter(self._deck))  # O(1)
            del self._data[first_key]  # O(1)

    def to_dict(self) -> dict[Hashable, Any]:
        return {k: self._data[k] for k in self._deck if k in self._data}

    def __repr__(self) -> str:
        return repr(self.to_dict())
