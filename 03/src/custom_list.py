from __future__ import annotations

from collections.abc import Callable, Sequence
from itertools import zip_longest
from typing import Self, TypeAlias

from typing_extensions import override

# Number = TypeVar("Number", bound=float | int)
Number: TypeAlias = float | int


class CustomList(list):
    @staticmethod
    def _zipper(
        func: Callable[[tuple[float, float]], float],
        left: Sequence[Number],
        right: Sequence[Number],
    ) -> map[float]:
        return map(func, zip_longest(left, right, fillvalue=0))

    @override
    def __add__(self, right: Sequence[Number]) -> Self:  # type: ignore
        return CustomList(self._zipper(sum, self, right))  # type: ignore

    def __radd__(self, left: Sequence[Number]) -> Self:
        return CustomList(self._zipper(sum, left, self))

    def __sub__(self, right: Sequence[Number]) -> Self:
        raise NotImplementedError
