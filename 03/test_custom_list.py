"""Содержит тесты решения первого пункта домашнего задания #03."""
# pylint: disable=missing-function-docstring, protected-access, missing-class-docstring
# pylint: disable=invalid-name, eval-used, use-list-literal, unneeded-not
import os
from math import isclose

import numpy as np
from hypothesis import given, note, settings
from hypothesis import strategies as st
from numpy.random import default_rng

from custom_list import CustomList, Number

settings.register_profile("release", max_examples=1000)
settings.register_profile("dev", max_examples=50)
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))


def test__zipper():
    zipper = CustomList()._zipper
    mapped = zipper(lambda lr: lr[0] * lr[1], range(6), [-3, 11, 0, 2])
    assert list(mapped) == [0, 11, 0, 6, 0, 0]


def test__zipper_empty():
    zipper = CustomList()._zipper
    mapped = zipper(lambda lr: lr[0] / lr[1], [], [])
    assert not list(mapped)


custom_list_strategy: st.SearchStrategy[list[Number]] = st.lists(
    st.integers() | st.floats(allow_infinity=False, allow_nan=False, width=32)
)


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
        result: CustomList = [] + CustomList()  # type: ignore
        assert result.is_equal(CustomList())

    @given(xs=custom_list_strategy)
    def test_only_one_empty(self, xs: list[Number]):
        result: CustomList = [] + CustomList(xs)  # type: ignore
        assert result.is_equal(CustomList(xs))
        result: CustomList = xs + CustomList()  # type: ignore
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
        assert (CustomList() - []).is_equal(CustomList())

    @given(xs=custom_list_strategy)
    def test_only_one_empty(self, xs: list[Number]):
        neg_xs = [-x for x in xs]
        assert (CustomList() - CustomList(xs)).is_equal(CustomList(neg_xs))
        assert (CustomList() - list(xs)).is_equal(CustomList(neg_xs))
        assert (CustomList(xs) - CustomList()).is_equal(CustomList(xs))
        assert (CustomList(xs) - []).is_equal(CustomList(xs))

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
        result = [] - CustomList()
        assert result.is_equal(CustomList())

    @given(xs=custom_list_strategy)
    def test_only_one_empty(self, xs: list[Number]):
        neg_xs = [-x for x in xs]
        result = [] - CustomList(xs)
        assert result.is_equal(CustomList(neg_xs))
        result = xs - CustomList()
        assert result.is_equal(CustomList(xs))

    @given(xs=..., ys=...)
    def test_purity(self, xs: list[Number], ys: list[Number]):
        """Проверяет, что исходные списки остаются неизменными."""
        left_was = list(xs)  # creates a copy
        right_was = CustomList(ys)  # creates a copy
        _ = left_was - right_was
        assert left_was == xs
        assert right_was.is_equal(CustomList(ys))


def sum_lists(l_sum: float, r_sum: float, l_length: int, r_length: int):
    assert l_length >= 1
    assert r_length >= 1

    rng = default_rng()
    left = rng.dirichlet(np.ones(l_length), size=1) * l_sum
    right = rng.dirichlet(np.ones(r_length), size=1) * r_sum
    return left.tolist()[0], right.tolist()[0]


class TestSpecialEq:
    @given(st.data())
    def test_fuzzy(self, data: st.DataObject):
        n = data.draw(st.integers())
        elements = st.integers(min_value=1, max_value=100_000)
        ls, rs = sum_lists(n, n, data.draw(elements), data.draw(elements))
        assert CustomList(ls) == CustomList(rs)

    def test_empty(self):
        assert CustomList([]) == CustomList([])

    @given(
        xs=st.lists(
            st.floats(allow_infinity=False, allow_nan=False).filter(
                lambda x: not isclose(x, 0)
            ),
            min_size=1,
        ).filter(lambda list_x: not isclose(sum(list_x), 0))
    )
    def test_half_empty(self, xs: list[float]):
        assert not CustomList(xs) == CustomList([])
        assert not CustomList([]) == CustomList(xs)


class TestSpecialNe:
    @given(
        xs=st.lists(
            st.floats(allow_infinity=False, allow_nan=False).filter(
                lambda x: not isclose(x, 0)
            ),
            min_size=1,
        ).filter(lambda list_x: not isclose(sum(list_x), 0))
    )
    def test_neq_half_empty(self, xs: list[float]):
        assert not CustomList(xs) == CustomList([])
        assert not CustomList([]) == CustomList(xs)

        assert CustomList(xs) != CustomList([])
        assert CustomList([]) != CustomList(xs)


class TestSpecialLe:
    @given(st.data())
    def test_fuzzy(self, data: st.DataObject):  # self <= other
        max_value = int(1e9)
        # * l_sum must be <= r_sum
        l_sum = data.draw(st.integers(min_value=-max_value, max_value=max_value))
        r_sum = data.draw(st.integers(min_value=l_sum, max_value=max_value + 1))
        elements = st.integers(min_value=1, max_value=100_000)
        ls, rs = sum_lists(l_sum, r_sum, data.draw(elements), data.draw(elements))
        assert CustomList(ls) <= CustomList(rs)

    def test_empty(self):
        assert CustomList([]) <= CustomList([])


class TestSpecialLt:
    @given(st.data())
    def test_fuzzy(self, data: st.DataObject):  # self < other
        max_value = int(1e9)
        # * l_sum must be < r_sum
        l_sum = data.draw(st.integers(min_value=-max_value, max_value=max_value))
        r_sum = data.draw(st.integers(min_value=l_sum + 1, max_value=max_value + 1))
        elements = st.integers(min_value=1, max_value=100_000)
        ls, rs = sum_lists(l_sum, r_sum, data.draw(elements), data.draw(elements))
        assert CustomList(ls) < CustomList(rs)

    def test_lt_empty(self):
        assert not CustomList([]) < CustomList([])


class TestSpecialGe:
    @given(st.data())
    def test_fuzzy(self, data: st.DataObject):  # self >= other
        max_value = int(1e9)
        # * l_sum must be >= r_sum
        r_sum = data.draw(st.integers(min_value=-max_value, max_value=max_value))
        l_sum = data.draw(st.integers(min_value=r_sum, max_value=max_value + 1))
        elements = st.integers(min_value=1, max_value=100_000)
        ls, rs = sum_lists(l_sum, r_sum, data.draw(elements), data.draw(elements))
        assert CustomList(ls) >= CustomList(rs)

    def test_ge_empty(self):
        assert CustomList([]) >= CustomList([])


class TestSpecialGt:
    @given(st.data())
    def test_fuzzy(self, data: st.DataObject):  # self > other
        max_value = int(1e9)
        # * l_sum must be > r_sum
        r_sum = data.draw(st.integers(min_value=-max_value, max_value=max_value))
        l_sum = data.draw(st.integers(min_value=r_sum + 1, max_value=max_value + 1))
        elements = st.integers(min_value=1, max_value=100_000)
        ls, rs = sum_lists(l_sum, r_sum, data.draw(elements), data.draw(elements))
        assert CustomList(ls) > CustomList(rs)

    def test_gt_empty(self):
        assert not CustomList([]) > CustomList([])


class TestSpecialEqualityChecks:
    @given(
        xs=st.lists(
            st.floats(allow_infinity=False, allow_nan=False).filter(
                lambda x: not isclose(x, 0)
            ),
            min_size=1,
        ).filter(lambda list_x: sum(list_x) >= 0)
    )
    def test_ge_le_half_empty(self, xs: list[float]):
        assert CustomList(xs) >= CustomList([])
        assert CustomList([]) <= CustomList(xs)

    @given(
        xs=st.lists(
            st.floats(allow_infinity=False, allow_nan=False).filter(
                lambda x: not isclose(x, 0)
            ),
            min_size=1,
        ).filter(lambda list_x: sum(list_x) > 0)
    )
    def test_gt_lt_half_empty(self, xs: list[float]):
        note(f"{sum(xs)=}")
        assert CustomList(xs) > CustomList([])
        assert CustomList([]) < CustomList(xs)
