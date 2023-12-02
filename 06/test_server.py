# import pytest
from pytest_mock import MockerFixture

from server import get_url_vocab


class TestCustomRequestHandler:
    ...


class TestGetUrlVocab:
    def test_ok(self, mocker: MockerFixture):
        test_string = "The naughty fox jumps over the lazy fox. Fox!"
        mock_response = mocker.Mock(
            code=200,
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
        mock_response = mocker.Mock(code=400)

        mocker.patch("server.urlopen", return_value=mock_response)
        assert get_url_vocab("") is None
        assert not mock_response.mock_calls
