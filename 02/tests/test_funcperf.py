# pylint: disable=import-error
import math
from time import sleep
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from funcperf import mean


def sleeper(ms: int) -> None:
    sleep(ms / 1000)


def run_true(a, b, tol=0.5):
    return math.isclose(a, b, abs_tol=tol)


@pytest.fixture()
def mocker_sleeper(mocker: MockerFixture) -> MagicMock:
    mock = mocker.MagicMock(wraps=sleeper)
    mock.__name__ = "sleeper"
    return mock


def test_exec_time(mocker_sleeper: MagicMock, capsys: pytest.CaptureFixture):
    time_to_sleep = 1  # ms
    trail_len = 10
    decorated_mock = mean(trail_len)(mocker_sleeper)
    for _ in range(500):
        decorated_mock(time_to_sleep)
    captured: str = capsys.readouterr().out
    assert all(
        run_true(float(line.split("`")[1]), time_to_sleep)
        for line in captured.splitlines()
    )


def test_call_nums(mocker_sleeper: MagicMock):
    time_to_sleep = 1  # ms
    trail_len = 10
    decorated_mock = mean(trail_len)(mocker_sleeper)
    expected_call_count = 100
    for _ in range(expected_call_count):
        decorated_mock(time_to_sleep)
    assert mocker_sleeper.call_count == expected_call_count
