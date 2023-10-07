from typing import NewType

import pytest
from pytest_mock import MockerFixture

from src.predict_message_mood import SomeModel, predict_message_mood

MockedSomeModel = NewType("MockedSomeModel", SomeModel)

BAD_THRESHOLD = 0.3
GOOD_THRESHOLD = 0.8


@pytest.fixture()
def mocked_model(
    mocker: MockerFixture, request: pytest.FixtureRequest
) -> MockedSomeModel:
    return_value: float = request.keywords["return_value"].args[0]

    model = SomeModel()
    mocker.patch.object(model, "predict", return_value=return_value)
    return MockedSomeModel(model)


def test_call_predict(mocker: MockerFixture):
    model = SomeModel()
    spy = mocker.spy(model, "predict")

    message = "lIpSuM\n!щыщ"
    predict_message_mood(message, model)
    spy.assert_called_once_with(message)

    predict_message_mood(42, model)  # type: ignore
    assert spy.call_args_list == [(message,), (42,)]


@pytest.mark.return_value(0.1)
def test_low(mocked_model: MockedSomeModel):
    assert (
        predict_message_mood("lIpSuM", mocked_model, BAD_THRESHOLD, GOOD_THRESHOLD)
        == "неуд"
    )


@pytest.mark.return_value(0.5)
def test_mid(mocked_model: MockedSomeModel):
    assert (
        predict_message_mood("lIpSuM", mocked_model, BAD_THRESHOLD, GOOD_THRESHOLD)
        == "норм"
    )


@pytest.mark.return_value(0.9)
def test_high(mocked_model: MockedSomeModel):
    assert (
        predict_message_mood("lIpSuM", mocked_model, BAD_THRESHOLD, GOOD_THRESHOLD)
        == "отл"
    )
