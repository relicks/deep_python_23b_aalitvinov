# pylint: disable=import-error
from json import JSONDecodeError
from typing import Any

import pytest
from pytest_mock import MockerFixture

from src.jq import parse_json


def test_example_print(capsys: pytest.CaptureFixture):
    parse_json(
        json_str='{"key1": "Word1 word2", "key2": "word2 word3"}',
        required_fields=["key1"],
        keywords=["word2"],
        keyword_callback=print,
    )
    assert capsys.readouterr().out == "key1 word2\n"


def test_example_mock(mocker: MockerFixture):
    callback = mocker.stub()
    parse_json(
        json_str='{"key1": "Word1 word2", "key2": "word2 word3"}',
        required_fields=["key1"],
        keywords=["word2"],
        keyword_callback=callback,
    )
    callback.assert_called_once_with("key1", "word2")  # ! assert


def test_noop(mocker: MockerFixture):
    mock = mocker.stub()
    mocker.patch("orjson.loads", mock)
    parse_json(
        json_str='{"key1": "Word1 word2", "key2": "word2 word3"}',
        keyword_callback=None,
    )
    mock.assert_not_called()  # ! assert


def test_alpha_one(json_str_alpha: str, mocker: MockerFixture):
    callback = mocker.stub()
    parse_json(
        json_str=json_str_alpha,
        required_fields=["apply"],
        keywords=["HArd"],
        keyword_callback=callback,
    )
    callback.assert_called_once_with("apply", "hard")  # ! assert


def test_alpha_two_specified(json_str_alpha: str, mocker: MockerFixture):
    callback = mocker.stub()
    parse_json(
        json_str=json_str_alpha,
        required_fields=["apply", "provide", "Value"],
        keywords=["hard"],
        keyword_callback=callback,
    )
    assert callback.call_args_list == [
        mocker.call("apply", "hard"),
        mocker.call("provide", "Hard"),
    ]


def test_alpha_two_unspecified(json_str_alpha: str, mocker: MockerFixture):
    callback = mocker.stub()
    parse_json(
        json_str=json_str_alpha,
        required_fields=None,
        keywords=["Hard"],
        keyword_callback=callback,
    )
    assert callback.call_args_list == [
        mocker.call("apply", "hard"),
        mocker.call("provide", "Hard"),
    ]


def test_alpha_invalid_key(json_str_alpha: str, mocker: MockerFixture):
    callback = mocker.stub()
    invalid_key = "oops"
    with pytest.raises(KeyError) as er:
        parse_json(
            json_str=json_str_alpha,
            required_fields=[invalid_key, "noop"],
            keywords=["Hard"],
            keyword_callback=callback,
        )
    assert er.match(invalid_key)


@pytest.mark.parametrize("kw_list", [[], list(".!@i2ь")])
def test_beta_not_called(json_str_beta: str, mocker: MockerFixture, kw_list: list[Any]):
    callback = mocker.stub()
    parse_json(
        json_str=json_str_beta,
        required_fields=None,
        keywords=kw_list,
        keyword_callback=callback,
    )
    callback.assert_not_called()  # ! assert


def test_beta_one(json_str_beta: str, mocker: MockerFixture):
    callback = mocker.stub()
    parse_json(
        json_str=json_str_beta,
        required_fields=["Головной!"],
        keywords=["палкА"],
        keyword_callback=callback,
    )
    callback.assert_called_once_with("Головной!", "палка")  # ! assert


def test_beta_many(json_str_beta: str, mocker: MockerFixture):
    callback = mocker.stub()
    parse_json(
        json_str=json_str_beta,
        required_fields=None,
        keywords=["палка"],
        keyword_callback=callback,
    )
    assert callback.call_args_list == [
        mocker.call("Головной!", "палка"),
        mocker.call("34876командование", "Палка"),
        mocker.call("Палка", "ПАЛКА"),
        mocker.call("Палка", "палка"),
        mocker.call("Палка", "ПаЛка"),
    ]


def test_parse_error(mocker: MockerFixture):
    callback = mocker.stub()
    with pytest.raises(JSONDecodeError):
        parse_json("+=12qwsasd,12 asgeht", keyword_callback=callback)


def test_all_call(mocker: MockerFixture):
    expected_num_calls = 6

    callback = mocker.stub()
    parse_json(
        json_str='{"Anything":"fund and apt","role":"Process","Evidence":"buy Sign"}',
        required_fields=None,
        keywords=None,
        keyword_callback=callback,
    )
    assert callback.call_count == expected_num_calls


def test_giant_json(json_str_giant: str, mocker: MockerFixture):
    callback = mocker.stub()
    parse_json(json_str=json_str_giant, keyword_callback=callback)
    callback.assert_called()  # ! assert
