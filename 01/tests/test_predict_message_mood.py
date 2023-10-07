from typing import NewType

import pytest
from pytest_mock import MockerFixture

from src.predict_message_mood import SomeModel, predict_message_mood

MockedSomeModel = NewType("MockedSomeModel", SomeModel)

BAD_THRESHOLD = 0.3
GOOD_THRESHOLD = 0.8


@pytest.fixture()
def model() -> SomeModel:
    return SomeModel()


def test_call_predict(model: SomeModel, mocker: MockerFixture):
    spy = mocker.spy(model, "predict")

    message = "lIpSuM\n!щыщ"
    predict_message_mood(message, model)
    spy.assert_called_once_with(message)

    predict_message_mood(42, model)  # type: ignore
    assert spy.call_args_list == [
        mocker.call(
            message,
        ),
        mocker.call(
            42,
        ),
    ]


@pytest.mark.parametrize(
    argnames=("predict_returns", "out"),
    argvalues=[
        (BAD_THRESHOLD - 0.1, "неуд"),
        ((GOOD_THRESHOLD + BAD_THRESHOLD) / 2, "норм"),
        (GOOD_THRESHOLD + 0.1, "отл"),
    ],
    ids=("low", "mid", "high"),
)
def test_normal_returns(
    model: SomeModel, predict_returns: float, out: str, mocker: MockerFixture
):
    """Проверяются нормальные случаи порогов для `predict`a."""
    mock = mocker.Mock(return_value=predict_returns)
    model = SomeModel()
    mocker.patch.object(model, "predict", mock)
    assert predict_message_mood("lIpSuM", model, BAD_THRESHOLD, GOOD_THRESHOLD) == out


@pytest.mark.parametrize(
    argnames=("predict_returns", "out"),
    argvalues=(
        (BAD_THRESHOLD, "неуд"),
        (BAD_THRESHOLD - 1e-16, "неуд"),
        (BAD_THRESHOLD + 1e-16, "неуд"),
        (GOOD_THRESHOLD, "отл"),
        (GOOD_THRESHOLD - 1e-16, "отл"),
        (GOOD_THRESHOLD + 1e-16, "отл"),
    ),
    ids=(
        "bad_th_eq",
        "bad_th_less",
        "bad_th_greater",
        "good_th_eq",
        "good_th_less",
        "good_th_greater",
    ),
)
def test_borders(
    model: SomeModel, predict_returns: float, out: str, mocker: MockerFixture
):
    """Проверяются краевые и околокраевые случаи порогов для `predict`a."""
    mock = mocker.Mock(return_value=predict_returns)
    model = SomeModel()
    mocker.patch.object(model, "predict", mock)
    assert predict_message_mood("lIpSuM", model, BAD_THRESHOLD, GOOD_THRESHOLD) == out
