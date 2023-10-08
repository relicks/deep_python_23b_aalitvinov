from typing import Self, TypeVar

T = TypeVar("T", float, int)


class CustomList(list[T]):
    def __add__(self, right: list[T]) -> Self:
        self.extend(right)
        return self

    def __radd__(self, left: list) -> Self:
        ...
