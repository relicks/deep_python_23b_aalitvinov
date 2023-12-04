import json

import cjson
import ujson


def test_one():
    assert cjson.sum([1, 3, 5]) == 9


def test_parsers():
    json_str = '{"hello": 10, "world": "value"}'
    json_doc = json.loads(json_str)
    ujson_doc = ujson.loads(json_str)
    cjson_doc = cjson.loads(json_str)
    assert json_doc == ujson_doc == cjson_doc
    assert json_str == cjson.dumps(cjson.loads(json_str))
