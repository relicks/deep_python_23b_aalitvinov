from lru_cache import LRUCache


def test_given():
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


def test_bad_case():
    cache = LRUCache(4)

    cache.set("k1", "val1")
    cache.set("k2", "val2")
    cache.set("k3", "val3")
