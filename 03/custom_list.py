"""Содержит решение для первого пункта домашнего задания #03."""
from __future__ import annotations

from collections.abc import Callable, Iterable
from itertools import zip_longest
from math import isclose
from typing import TypeAlias

from typing_extensions import Self, override

Number: TypeAlias = float | int


class CustomList(list):
    """Позволяет складываться/вычитаться друг с другом и с обычными списками.

    Результатом сложения/вычитания является новый кастомный список. При этом
    исходные списки остаются неизменными.
    Отсутствующие элементы меньшего списка считаются нулями.

    >>> CustomList([5, 1, 3, 7]) + CustomList([1, 2, 7])
    [6, 3, 10, 7]

    >>> CustomList([1]) + [2, 5]
    [3, 5]

    >>> CustomList([5, 1, 3, 7]) - CustomList([1, 2, 7])
    [4, -1, -4, 7]

    """

    @staticmethod
    def _zipper(
        func: Callable[[tuple[Number, Number]], Number],
        left: Iterable[Number],
        right: Iterable[Number],
    ) -> map[Number]:
        return map(func, zip_longest(left, right, fillvalue=0))

    def is_equal(self, other: object) -> bool:
        """Default list's element-wise `__eq__` behavior."""
        return super().__eq__(other)

    @override
    def __str__(self) -> str:
        return f"data={super().__str__()}, sum={sum(self)}"

    @override
    def __add__(self, right: Iterable[Number]) -> Self:  # type: ignore
        return type(self)(self._zipper(sum, self, right))

    def __radd__(self, left: Iterable[Number]) -> Self:
        return type(self)(self._zipper(sum, left, self))

    def __sub__(self, right: Iterable[Number]) -> Self:
        return type(self)(self._zipper(lambda tpl: tpl[0] - tpl[1], self, right))

    def __rsub__(self, left: Iterable[Number]) -> Self:
        return type(self)(self._zipper(lambda tpl: tpl[0] - tpl[1], left, self))

    @override
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, type(self)):
            return NotImplemented  # pragma: no cover
        return isclose(sum(self), sum(__value))

    @override
    def __le__(self, __value: list[Number]) -> bool:
        if not isinstance(__value, type(self)):
            return NotImplemented  # pragma: no cover
        return (sum(self) <= sum(__value)) or self == __value

    @override
    def __lt__(self, __value: list[Number]) -> bool:
        if not isinstance(__value, type(self)):
            return NotImplemented  # pragma: no cover
        return sum(self) < sum(__value)

    @override
    def __ge__(self, __value: list[Number]) -> bool:
        if not isinstance(__value, type(self)):
            return NotImplemented  # pragma: no cover
        return sum(self) >= sum(__value) or self == __value

    @override
    def __gt__(self, __value: list[Number]) -> bool:
        if not isinstance(__value, type(self)):
            return NotImplemented  # pragma: no cover
        return sum(self) > sum(__value)
