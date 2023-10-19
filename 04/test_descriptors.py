from unittest import mock

import pytest
from pytest_mock import MockerFixture

from descriptors import Validator

# @pytest.fixture(scope="class")
# def mocked_validator_inst() -> Validator:
#     with mock.patch.multiple(
#         Validator,
#         __abstractmethods__=set(),
#         validate=mock.Mock(return_value=None),
#     ):
#         return Validator()  # type: ignore


class TestValidator:
    test_name = "test_attr"
    test_value = "VALID_VALUE"

    @pytest.fixture()
    def mocked_validator(self, mocker: MockerFixture) -> type[Validator]:
        mocker.patch.multiple(
            Validator,
            __abstractmethods__=set(),
            validate=mock.Mock(return_value=None),
        )
        return Validator

    @pytest.fixture()
    def mocked_validator_inst(self, mocked_validator: type[Validator]) -> Validator:
        validator = mocked_validator()  # type: ignore
        validator.__set_name__(type, self.test_name)
        return validator

    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            # pylint: disable-next=abstract-class-instantiated
            Validator()  # type: ignore

    def test_special_set_name(self, mocked_validator_inst: Validator):
        assert mocked_validator_inst._private_name == "_" + self.test_name

    def test_special_set(self, mocked_validator_inst: Validator, mocker: MockerFixture):
        mock_obj = mocker.Mock()
        mocked_validator_inst.__set__(mock_obj, self.test_value)
        assert getattr(mock_obj, "_" + self.test_name) == self.test_value

    def test_special_set_raises(
        self, mocked_validator_inst: Validator, mocker: MockerFixture
    ):
        mock_obj = mocker.Mock()
        mocker.patch.object(
            mocked_validator_inst, "validate", return_value=ValueError("тест")
        )
        with pytest.raises(ValueError, match="тест"):
            mocked_validator_inst.__set__(mock_obj, self.test_value)

    def test_special_set_not_mutates(
        self, mocked_validator_inst: Validator, mocker: MockerFixture
    ):
        mock_obj = mocker.Mock()
        mocked_validator_inst.__set__(mock_obj, self.test_value)
        initial_value = getattr(mock_obj, "_" + self.test_name)
        assert initial_value == self.test_value
        mocker.patch.object(
            mocked_validator_inst, "validate", return_value=ValueError("тест")
        )
        with pytest.raises(ValueError, match="тест"):
            mocked_validator_inst.__set__(mock_obj, "INVALID_VALUE")
        assert initial_value == getattr(mock_obj, "_" + self.test_name)

    def test_special_get(self, mocked_validator_inst: Validator, mocker: MockerFixture):
        mock_obj = mocker.Mock()
        mocked_validator_inst.__set__(mock_obj, self.test_value)
        private_attr_value = getattr(mock_obj, "_" + self.test_name)
        public_getter_value = mocked_validator_inst.__get__(mock_obj)

        assert private_attr_value == public_getter_value == self.test_value
