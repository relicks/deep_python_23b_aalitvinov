# import json

import cjson

# import ujson


def test_one():
    assert cjson.sum([1, 3, 5]) == 9
