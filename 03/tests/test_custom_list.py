import os
from operator import neg

from hypothesis import given, settings
from hypothesis import strategies as st

from src.custom_list import CustomList, Number

settings.register_profile("release", max_examples=1000)
settings.register_profile("dev", max_examples=50)
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))


custom_list_strategy: st.SearchStrategy[list[Number]] = st.lists(
    st.integers() | st.floats(allow_infinity=False, allow_nan=False, width=32)
)


def test__zipper():
    ...


class TestSpecialStr:
    @given(xs=custom_list_strategy)
    def test_validity(self, xs: list[Number]):
        custom_list = CustomList(xs)
        str_data: dict[str, int] = eval(f"dict({custom_list!s})")
        assert xs == str_data["data"]
        assert sum(xs) == str_data["sum"]


class TestSpecialAdd:  # self + other
    def test_both_custom(self):
        left = CustomList([5, 1, 3, 7])
        right = CustomList([1, 2, 7])
        assert (left + right).is_equal(CustomList([6, 3, 10, 7]))

    def test_only_left_custom(self):
        left = CustomList([1])
        right = [2, 5]
        assert (left + right).is_equal(CustomList([3, 5]))

    def test_both_empty(self):
        assert (CustomList() + CustomList()).is_equal(CustomList())
        assert (CustomList() + list()).is_equal(CustomList())  # noqa: C408

    @given(xs=custom_list_strategy)
    def test_only_one_empty(self, xs: list[Number]):
        assert (CustomList() + CustomList(xs)).is_equal(CustomList(xs))
        assert (CustomList() + list(xs)).is_equal(CustomList(xs))
        assert (CustomList(xs) + CustomList()).is_equal(CustomList(xs))
        assert (CustomList(xs) + list()).is_equal(CustomList(xs))  # noqa: C408

    @given(xs=..., ys=...)
    def test_purity(self, xs: list[Number], ys: list[Number]):
        """Проверяет, что исходные списки остаются неизменными."""
        left_was = CustomList(xs)  # creates a copy
        right_was = list(ys)  # creates a copy
        _ = left_was + right_was
        assert left_was.is_equal(CustomList(xs))
        assert right_was == ys


class TestSpecialRadd:  # other + self
    def test_only_right_custom(self):
        left = [2, 5]
        right = CustomList([1])
        assert (left + right).is_equal(CustomList([3, 5]))  # type: ignore

    def test_both_empty(self):
        result = CustomList().__radd__([])  # [] + CustomList()
        assert result.is_equal(CustomList())

    @given(xs=custom_list_strategy)
    def test_only_one_empty(self, xs: list[Number]):
        result = CustomList(xs).__radd__([])  # [] + CustomList(xs)
        assert result.is_equal(CustomList(xs))
        result = CustomList().__radd__(xs)  # xs + CustomList()
        assert result.is_equal(CustomList(xs))

    @given(xs=..., ys=...)
    def test_purity(self, xs: list[Number], ys: list[Number]):
        """Проверяет, что исходные списки остаются неизменными."""
        left_was = list(xs)  # creates a copy
        right_was = CustomList(ys)  # creates a copy
        _ = left_was + right_was
        assert left_was == xs
        assert right_was.is_equal(CustomList(ys))


class TestSpecialSub:  # self - other
    def test_both_custom(self):
        left = CustomList([5, 1, 3, 7])
        right = CustomList([1, 2, 7])
        assert (left - right).is_equal(CustomList([4, -1, -4, 7]))

    def test_only_left_custom(self):
        left = CustomList([1])
        right = [2, 5]
        assert (left - right).is_equal(CustomList([-1, -5]))

    def test_both_empty(self):
        assert (CustomList() - CustomList()).is_equal(CustomList())
        assert (CustomList() - list()).is_equal(CustomList())  # noqa: C408

    @given(xs=custom_list_strategy)
    def test_only_one_empty(self, xs: list[Number]):
        neg_xs = list(map(neg, xs))
        assert (CustomList() - CustomList(xs)).is_equal(CustomList(neg_xs))
        assert (CustomList() - list(xs)).is_equal(CustomList(neg_xs))
        assert (CustomList(xs) - CustomList()).is_equal(CustomList(xs))
        assert (CustomList(xs) - list()).is_equal(CustomList(xs))  # noqa: C408

    @given(xs=..., ys=...)
    def test_purity(self, xs: list[Number], ys: list[Number]):
        """Проверяет, что исходные списки остаются неизменными."""
        left = CustomList(xs)  # creates a copy
        right = list(ys)  # creates a copy
        _ = left - right
        assert left.is_equal(CustomList(xs))
        assert right == ys


class TestSpecialRsub:  # other - self
    def test_only_right_custom(self):
        left = [2, 5]
        right = CustomList([1])
        assert (left - right).is_equal(CustomList([1, 5]))

    def test_both_empty(self):
        result = [] - CustomList()  # [] - CustomList()
        assert result.is_equal(CustomList())

    @given(xs=custom_list_strategy)
    def test_only_one_empty(self, xs: list[Number]):
        neg_xs = list(map(neg, xs))
        result = [] - CustomList(xs)  # [] - CustomList(xs)
        assert result.is_equal(CustomList(neg_xs))
        result = xs - CustomList()  # xs - CustomList()
        assert result.is_equal(CustomList(xs))

    @given(xs=..., ys=...)
    def test_purity(self, xs: list[Number], ys: list[Number]):
        """Проверяет, что исходные списки остаются неизменными."""
        left_was = list(xs)  # creates a copy
        right_was = CustomList(ys)  # creates a copy
        _ = left_was - right_was
        assert left_was == xs
        assert right_was.is_equal(CustomList(ys))


class TestSpecialEqualityChecks:
    ...


# class TestSpecialLe: ...

# class TestSpecialLt: ...

# class TestSpecialGe: ...

# class TestSpecialGt: ...
