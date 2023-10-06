from typing import NewType

import pytest
from pytest_mock import MockerFixture

from src.predict_message_mood import SomeModel, predict_message_mood

MockedSomeModel = NewType("MockedSomeModel", SomeModel)


@pytest.fixture()
def mocked_model(
    mocker: MockerFixture, request: pytest.FixtureRequest
) -> MockedSomeModel:
    return_value: float = request.keywords["return_value"].args[0]
    model = SomeModel()
    mocker.patch.object(model, "predict", return_value=return_value)
    return MockedSomeModel(model)


@pytest.mark.return_value(0.1)
def test_low(mocked_model: MockedSomeModel):
    assert predict_message_mood("lIpSuM", mocked_model) == "неуд"


@pytest.mark.return_value(0.5)
def test_mid(mocked_model: MockedSomeModel):
    assert predict_message_mood("lIpSuM", mocked_model) == "норм"


@pytest.mark.return_value(0.9)
def test_high(mocked_model: MockedSomeModel):
    assert predict_message_mood("lIpSuM", mocked_model) == "отл"
