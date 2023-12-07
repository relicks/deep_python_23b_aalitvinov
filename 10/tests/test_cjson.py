import json

import cjson
import pytest
import ujson


def test_loads_valid():
    json_str = '{"hello": 10, "world": "value"}'
    json_doc = json.loads(json_str)
    ujson_doc = ujson.loads(json_str)
    cjson_doc = cjson.loads(json_str)
    assert json_doc == ujson_doc == cjson_doc


def test_loads_invaid():
    json_invalid_strs = ["{1, 2, 3}", "ipp", "{[]: 2}"]
    for js in json_invalid_strs:
        with pytest.raises(ValueError):
            _ = cjson.loads(js)


def test_load_object():
    json_str = '{"json_object": {"another": "one"} }'
    with pytest.raises(NotImplementedError):
        _ = cjson.loads(json_str)


def test_dumps_valid():
    json_str = '{"hello!": 10, "world": "value", "world2": "value2"}'
    assert json_str == cjson.dumps(cjson.loads(json_str))


def test_dumps_nested():
    with pytest.raises(NotImplementedError):
        _ = cjson.dumps({"json_object": {"another": "one"}})
