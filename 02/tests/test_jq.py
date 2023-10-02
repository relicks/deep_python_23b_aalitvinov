import pytest

from jq import parse_json


def test_jq():
    with pytest.raises(NotImplementedError):
        parse_json("")
