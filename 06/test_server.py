from collections.abc import Mapping
from http import HTTPStatus
from itertools import chain, repeat
from random import shuffle

import pytest
from pytest_mock import MockerFixture

from server import get_top_words, get_url_vocab


class TestCustomRequestHandler:
    ...


class TestGetUrlVocab:
    def test_ok(self, mocker: MockerFixture):
        test_string = "The naughty fox jumps over the lazy fox. Fox!"
        mock_response = mocker.Mock(
            code=HTTPStatus.OK,
            read=mocker.Mock(return_value=b"<p> %a </p>" % test_string),
            close=mocker.Mock(return_value=None),
        )

        mocker.patch("server.urlopen", return_value=mock_response)
        result = get_url_vocab("")

        assert result is not None
        assert sorted(result) == sorted(
            ["the", "naughty", "fox", "jumps", "over", "the", "lazy", "fox", "fox"]
        )

        assert [mocker.call.read(), mocker.call.close()] == mock_response.mock_calls

    def test_error(self):
        assert get_url_vocab("") is None
        assert get_url_vocab("http://exampleetyrbsgdz21234.com") is None

    def test_not_ok(self, mocker: MockerFixture):
        mock_response = mocker.Mock(code=HTTPStatus.BAD_REQUEST)

        mocker.patch("server.urlopen", return_value=mock_response)
        assert get_url_vocab("") is None
        assert not mock_response.mock_calls


class TestGetTopWords:
    @staticmethod
    def flatten_shuffle(word_count: Mapping[str, int]) -> list[str]:
        result = list(
            chain.from_iterable(
                repeat(word, count) for word, count in word_count.items()
            )
        )
        shuffle(result)
        return result

    @pytest.mark.parametrize(
        ("freq", "k_top"),
        [
            ({"jumps": 1, "the": 2, "fox": 3, "over": 1, "lazy": 5}, 50),
            ({"jumps": 1, "the": 2, "fox": 3, "over": 1, "lazy": 5}, 3),
        ],
    )
    def test_ok_bounded(self, freq, k_top, mocker: MockerFixture):
        mocker.patch("server.get_url_vocab", return_value=self.flatten_shuffle(freq))
        result = get_top_words("http://some-url", k_top)["http://some-url"]

        assert result is not None
        assert sorted(result.items()) == sorted(
            sorted(freq.items(), key=lambda x: x[1], reverse=True)[
                : min(len(freq), k_top)
            ]
        )

    def test_none(self):
        ...
