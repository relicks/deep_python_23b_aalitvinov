# pylint: disable=import-error
import pytest
from pytest_mock import MockerFixture

from jq import parse_json


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


def test_alpha_one(json_str_alpha: str, mocker: MockerFixture):
    callback = mocker.stub()
    parse_json(
        json_str=json_str_alpha,
        required_fields=["apply"],
        keywords=["HArd"],
        keyword_callback=callback,
    )
    callback.assert_called_once_with("apply", "hard")


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


def test_beta_not_called(json_str_beta: str, mocker: MockerFixture):
    callback = mocker.stub()
    parse_json(
        json_str=json_str_beta,
        required_fields=None,
        keywords=list(".!@i2ь"),
        keyword_callback=callback,
    )
    assert not callback.called


@pytest.mark.skip()
def test_giant_json(json_str_giant: str, mocker: MockerFixture):
    callback = mocker.stub()
    parse_json(json_str=json_str_giant, keyword_callback=callback)
    callback.assert_called()
