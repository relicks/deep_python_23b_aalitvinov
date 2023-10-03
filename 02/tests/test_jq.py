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
    stub = mocker.stub()
    parse_json(
        json_str='{"key1": "Word1 word2", "key2": "word2 word3"}',
        required_fields=["key1"],
        keywords=["word2"],
        keyword_callback=stub,
    )
    stub.assert_called_once_with("key1", "word2")  # ! assert
