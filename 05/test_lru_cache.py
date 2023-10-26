"""Содержит второй пункт (тесты решения первого пункта) HW05."""
import pytest

from lru_cache import LRUCache, NaturalIntValidator


class TestNaturalIntValidator:
    @pytest.fixture()
    def example_class(self):
        class Example:
            field = NaturalIntValidator()

            def __init__(self, field) -> None:
                self.field = field

        return Example

    def test_validate(self, example_class: type):
        inst = example_class(15)
        assert inst.field == 15
        inst.field = 1
        assert inst.field == 1

    def test_validate_raises(self, example_class: type):
        with pytest.raises(TypeError):
            example_class("number")

        with pytest.raises(ValueError, match="positive"):
            example_class(0)

        inst = example_class(2)
        with pytest.raises(TypeError):
            inst.field = "number"

        with pytest.raises(ValueError, match="positive"):
            inst.field = 0


class TestLRUCache:
    def test_given(self):
        cache = LRUCache(2)

        cache.set("k1", "val1")
        cache.set("k2", "val2")

        assert cache.get("k3") is None
        assert cache.get("k2") == "val2"
        assert cache.get("k1") == "val1"

        cache.set("k3", "val3")

        assert cache.get("k3") == "val3"
        assert cache.get("k2") is None
        assert cache.get("k1") == "val1"

    def test_bad_case(self):
        cache = LRUCache(3)

        cache.set("k1", "val1")
        cache.set("k2", "val2")
        cache.set("k3", "val3")

        assert cache.get("k2") == "val2"
        assert cache.get("k1") == "val1"
        assert cache.get("k2") == "val2"

        cache.set("k4", "val4")

        assert cache.get("k3") is None
        assert all(cache.get(k) is not None for k in ("k1", "k2", "k4"))
