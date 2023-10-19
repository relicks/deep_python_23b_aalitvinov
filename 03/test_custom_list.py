"""Содержит тесты решения первого пункта домашнего задания #03."""
# pylint: disable=missing-function-docstring, protected-access, missing-class-docstring
# pylint: disable=invalid-name, eval-used, use-list-literal, unneeded-not
from random import Random

import pytest

from custom_list import CustomList, Number

SEED: int | None = None


def test__zipper():
    zipper = CustomList()._zipper
    mapped = zipper(lambda lr: lr[0] * lr[1], range(6), [-3, 11, 0, 2])
    assert list(mapped) == [0, 11, 0, 6, 0, 0]


def test__zipper_empty():
    zipper = CustomList()._zipper
    mapped = zipper(lambda lr: lr[0] / lr[1], [], [])
    assert not list(mapped)


@pytest.fixture(name="xs", params=[[-3, 5, 10, -97], [2], [0, 0, 0], []])
def list_gen_one(request: pytest.FixtureRequest):
    return request.param


@pytest.fixture(name="ys", params=[[2, 5], [0, 44, 3], [6, -7, -5, 3], []])
def list_gen_two(request: pytest.FixtureRequest):
    return request.param


class TestSpecialStr:
    def test_concrete(self):
        assert str(CustomList([5.2, 4])) == "data=[5.2, 4], sum=9.2"
        assert str(CustomList([3, 2, 1])) == "data=[3, 2, 1], sum=6"
        assert str(CustomList()) == "data=[], sum=0"


class TestSpecialAdd:  # self + other
    def test_custom_long_custom_short(self):
        left = CustomList([5, 1, 3, 7])
        right = CustomList([1, 2, 7])
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left + right).is_equal(CustomList([6, 3, 10, 7]))

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_custom_short_custom_long(self):
        left = CustomList([-4, 11])
        right = CustomList([5, -11, 4, 90, 8])
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left + right).is_equal(CustomList([1, 0, 4, 90, 8]))

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_custom_equal_length(self):
        left = CustomList([-77, 6, 16])
        right = CustomList([4, 0, 8])
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left + right).is_equal(CustomList([-73, 6, 24]))

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_custom_short_list_long(self):
        left = CustomList([1])
        right = [2, 5]
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left + right).is_equal(CustomList([3, 5]))

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_custom_long_list_short(self):
        left = CustomList([6, -7, -5, 3])
        right = [0, 44, 3]
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left + right).is_equal(CustomList([6, 37, -2, 3]))

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_both_empty(self):
        assert (CustomList() + CustomList()).is_equal(CustomList())
        assert (CustomList() + list()).is_equal(CustomList())  # noqa: C408

    def test_only_one_empty(self, xs: list[Number]):
        assert (CustomList() + CustomList(xs)).is_equal(CustomList(xs))
        assert (CustomList() + list(xs)).is_equal(CustomList(xs))
        assert (CustomList(xs) + CustomList()).is_equal(CustomList(xs))
        assert (CustomList(xs) + list()).is_equal(CustomList(xs))  # noqa: C408

    def test_purity(self, xs: list[Number], ys: list[Number]):
        """Проверяет, что исходные списки остаются неизменными."""
        left = CustomList(xs)
        right = list(ys)
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        _ = left + right

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after


class TestSpecialRadd:  # other + self
    def test_list_long_custom_short(self):
        left = [2, 5]
        right = CustomList([1])
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left + right).is_equal(CustomList([3, 5]))  # type: ignore

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_list_short_custom_long(self):
        left = [0, 12, -99]
        right = CustomList([-7, 0, 10, 55, 0])
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left + right).is_equal(CustomList([-7, 12, -89, 55, 0]))  # type: ignore

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_list_custom_equal_length(self):
        left = [0, 0, -1, 4]
        right = CustomList([0, 14, 1, 5])
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left + right).is_equal(CustomList([0, 14, 0, 9]))  # type: ignore

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_both_empty(self):
        result: CustomList = [] + CustomList()  # type: ignore
        assert result.is_equal(CustomList())

    def test_only_one_empty(self, xs: list[Number]):
        result: CustomList = [] + CustomList(xs)  # type: ignore
        assert result.is_equal(CustomList(xs))
        result: CustomList = xs + CustomList()  # type: ignore
        assert result.is_equal(CustomList(xs))

    def test_purity(self, xs: list[Number], ys: list[Number]):
        """Проверяет, что исходные списки остаются неизменными."""
        left = list(xs)
        right = CustomList(ys)
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        _ = left + right

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after


class TestSpecialSub:  # self - other
    def test_custom_long_custom_short(self):
        left = CustomList([5, 1, 3, 7])
        right = CustomList([1, 2, 7])
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left - right).is_equal(CustomList([4, -1, -4, 7]))

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_custom_short_custom_long(self):
        left = CustomList([-4, 11])
        right = CustomList([5, -11, 4, 90, 8])
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left - right).is_equal(CustomList([-9, 22, -4, -90, -8]))

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_custom_equal_length(self):
        left = CustomList([-77, 6, 16])
        right = CustomList([4, 0, 8])
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left - right).is_equal(CustomList([-81, 6, 8]))

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_custom_short_list_long(self):
        left = CustomList([1])
        right = [2, 5]
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left - right).is_equal(CustomList([-1, -5]))

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_custom_long_list_short(self):
        left = CustomList([6, -7, -5, 3])
        right = [0, 44, 3]
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left - right).is_equal(CustomList([6, -51, -8, 3]))

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_both_empty(self):
        assert (CustomList() - CustomList()).is_equal(CustomList())
        assert (CustomList() - []).is_equal(CustomList())

    def test_only_one_empty(self, xs: list[Number]):
        neg_xs = [-x for x in xs]
        assert (CustomList() - CustomList(xs)).is_equal(CustomList(neg_xs))
        assert (CustomList() - list(xs)).is_equal(CustomList(neg_xs))
        assert (CustomList(xs) - CustomList()).is_equal(CustomList(xs))
        assert (CustomList(xs) - []).is_equal(CustomList(xs))

    def test_purity(self, xs: list[Number], ys: list[Number]):
        """Проверяет, что исходные списки остаются неизменными."""
        left = CustomList(xs)
        right = list(ys)
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        _ = left - right

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after


class TestSpecialRsub:  # other - self
    def test_list_long_custom_short(self):
        left = [2, 5]
        right = CustomList([1])
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left - right).is_equal(CustomList([1, 5]))

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_list_short_custom_long(self):
        left = [0, 12, -99]
        right = CustomList([-7, 0, 10, 55, 0])
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left - right).is_equal(CustomList([7, 12, -109, -55, 0]))

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_list_custom_equal_length(self):
        left = [0, 0, -1, 4]
        right = CustomList([0, 14, 1, 5])
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert (left - right).is_equal(CustomList([0, -14, -2, -1]))

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_both_empty(self):
        result = [] - CustomList()
        assert result.is_equal(CustomList())

    def test_only_one_empty(self, xs: list[Number]):
        neg_xs = [-x for x in xs]
        result = [] - CustomList(xs)
        assert result.is_equal(CustomList(neg_xs))
        result = xs - CustomList()
        assert result.is_equal(CustomList(xs))

    def test_purity(self, xs: list[Number], ys: list[Number]):
        """Проверяет, что исходные списки остаются неизменными."""
        left = list(xs)
        right = CustomList(ys)
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        _ = left - right

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after


class TestSpecialEq:
    @pytest.mark.parametrize(
        ("ls", "rs"),
        [
            ([5, 1, 3, 7, 0], [2, 5, 9]),
            ([-1, -17, 8] * 10**3, [-10, 4, -4] * 10**3),
            ([5], [2, 3]),
            ([0, 0], [0, 0, 0, 0, 0]),
            ([-2, 1, 1], [0]),
        ],
    )
    def test_differing_lengths(self, ls, rs):
        left = CustomList(ls)
        right = CustomList(rs)
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert left == right

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_empty(self):
        assert CustomList([]) == CustomList([])

    @pytest.mark.parametrize("xs", [[-3, 5, 10, -97], [-2], [0, 12]])
    def test_half_empty(self, xs: list[float]):
        assert not CustomList(xs) == CustomList([])
        assert not CustomList([]) == CustomList(xs)


class TestSpecialNe:
    @pytest.mark.parametrize(
        ("ls", "rs"),
        [
            ([5, 1, 3, 7, 0], [2, 5, 9]),
            ([-1, -17, 8], [-10, 4, -4]),
            ([5], [2, 3]),
            ([0, 0], [0, 0, 0, 0, 0]),
            ([-2, 1, 1], [0]),
        ],
    )
    def test_differing_lengths(self, ls, rs):
        left = CustomList(ls)
        right = CustomList(rs)

        assert not left != right

    def test_neq_half_empty(self, ys: list[Number]):
        if ys:
            assert not CustomList(ys) == CustomList([])
            assert not CustomList([]) == CustomList(ys)

            assert CustomList(ys) != CustomList([])
            assert CustomList([]) != CustomList(ys)

    def test_purity(self, xs: list[Number], ys: list[Number]):
        left = CustomList(xs)
        right = CustomList(ys)
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        _ = left != right

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after


class TestSpecialLe:  # self <= other
    @pytest.mark.parametrize(
        ("ls", "rs"),
        [
            ([5, 1, 3, 7, 0], [2, 5, 90]),  # <
            ([-1, -17, -8], [-10, 4, -4]),  # <
            ([5], [2, 3]),  # ==
            ([0, 0], [0, 0, 0, 0, 0]),  # ==
        ],
    )
    def test_fuzzy(self, ls, rs):
        left, right = CustomList(ls), CustomList(rs)
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert left <= right

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_empty(self):
        assert CustomList([]) <= CustomList([])


class TestSpecialLt:  # self < other
    @pytest.mark.parametrize(
        ("ls", "rs"),
        [
            ([5, 1, 3, 7, 0], [2, 5, 90]),  # <
            ([-1, -17, -8], [-10, 4, -4]),  # <
            ([5], [2, 3, 0.1]),  # <
            ([0, -0.01], [0, 0, 0, 0, 0]),  # <
        ],
    )
    def test_fuzzy(self, ls, rs):
        left, right = CustomList(ls), CustomList(rs)
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert left < right

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_lt_empty(self):
        assert not CustomList([]) < CustomList([])


class TestSpecialGe:  # self >= other
    @pytest.mark.parametrize(
        ("ls", "rs"),
        [
            ([5, 1, 3, 7, 0], [2, 5, -90]),  # >
            ([-1, -17, 8], [-10, 4, -4]),  # ==
            ([5.5], [2, 3]),  # >
            ([0, 0], [0, 0, 0, 0, 0]),  # ==
            ([-2, 1, 1], [-0.05]),  # >
        ],
    )
    def test_fuzzy(self, ls, rs):
        left, right = CustomList(ls), CustomList(rs)
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert left >= right

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_ge_empty(self):
        assert CustomList([]) >= CustomList([])


class TestSpecialGt:  # self > other
    @pytest.mark.parametrize(
        ("ls", "rs"),
        [
            ([5, 1, 3, 7, 0], [2, 5, -90]),  # >
            ([-1, 17, 8], [-1, 4, -4]),  # >
            ([5.5], [2, 3]),  # >
            ([0, 0, 100], [0, 0, 0, 0, -10]),  # >
            ([-2, 1, 1], [-0.05]),  # >
        ],
    )
    def test_fuzzy(self, ls, rs):
        left, right = CustomList(ls), CustomList(rs)
        hashes_before = (hash(tuple(left)), hash(tuple(right)))

        assert left > right

        hashes_after = (hash(tuple(left)), hash(tuple(right)))
        assert hashes_before == hashes_after

    def test_gt_empty(self):
        assert not CustomList([]) > CustomList([])


class TestSpecialEqualityChecks:
    def test_ge_le_half_empty(self):
        rng = Random(SEED)
        xs = rng.choices(range(1, 10**9), k=rng.randint(1, 10**5))
        assert CustomList(xs) >= CustomList([])
        assert CustomList([]) <= CustomList(xs)

    def test_gt_lt_half_empty(self):
        rng = Random(SEED)
        xs = rng.choices(range(1, 10**9), k=rng.randint(1, 10**5))
        assert CustomList(xs) > CustomList([])
        assert CustomList([]) < CustomList(xs)
