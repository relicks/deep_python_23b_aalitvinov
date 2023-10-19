from typing import Any
from unittest import mock

import pytest
from pytest_mock import MockerFixture

from descriptors import EmailValidator, UInt64Validator, UrlValidator, Validator


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
        """Проверяет, что возвращаемый `validate` Exception поднимается."""
        mock_obj = mocker.Mock()
        mocker.patch.object(
            mocked_validator_inst, "validate", return_value=ValueError("тест")
        )
        with pytest.raises(ValueError, match="тест"):
            mocked_validator_inst.__set__(mock_obj, self.test_value)

    def test_special_set_not_mutates(
        self, mocked_validator_inst: Validator, mocker: MockerFixture
    ):
        """
        Проверяет, что setting невалидного значения в дескриптор не меняет его значение.
        """
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

    @pytest.fixture()
    def validator_example(self):
        class ExampleValidator(Validator):
            def validate(self, value: Any) -> Exception | None:
                if value not in (1, "two", "other", "new"):
                    raise ValueError("from ExampleValidator")
                return None

        class Example:
            var_one = ExampleValidator()
            var_two = ExampleValidator()

            def __init__(self) -> None:
                self.var_one = 1
                self.var_two = "two"

        return Example()

    def test_double_validator(self, validator_example):
        assert validator_example.var_one == 1
        assert validator_example.var_two == "two"

    def test_double_validator_set(self, validator_example):
        validator_example.var_one = "new"
        validator_example.var_two = "other"
        assert validator_example.var_one == "new"
        assert validator_example.var_two == "other"

    def test_double_validator_raises(self, validator_example):
        with pytest.raises(ValueError, match="from ExampleValidator"):
            validator_example.var_one = 2


class TestUInt64Validator:
    @pytest.fixture()
    def example_class(self):
        class Example:
            count = UInt64Validator()
            page = UInt64Validator()

            def __init__(self, count, page) -> None:
                self.count = count
                self.page = page

        return Example

    @pytest.mark.parametrize("value", [(0, 1), (12, 3), (2**63, 2**63 - 1)])
    def test_validate(self, example_class, value):
        inst = example_class(value[0], value[1])
        assert inst.count == value[0]
        assert inst.page == value[1]
        assert inst.count == value[0]

    def test_validate_raises_type(self, example_class):
        with pytest.raises(TypeError, match="Expected"):
            example_class("string", None)

        with pytest.raises(TypeError, match="Expected"):
            example_class(0.45, 9)

    @pytest.mark.parametrize("value", [-1, -457362, 2**64])
    def test_validate_raises_value(self, example_class, value):
        with pytest.raises(ValueError, match="Expected"):
            example_class(value, 1)

        with pytest.raises(ValueError, match="Expected"):
            example_class(1, value)


class TestEmailValidator:
    @pytest.fixture()
    def example_class(self):
        class Example:
            email = EmailValidator()

            def __init__(self, email) -> None:
                self.email = email

        return Example

    @pytest.mark.parametrize(
        "value",
        [
            "sklingel.hoefer@example.net",
            "_______@example.com",
            "firstname_lastname@example.com",
            "мяу_lastname@example.com",
            "email@123.123.123.123",
        ],
    )
    def test_validate(self, example_class, value):
        inst = example_class(value)
        assert inst.email == value

    @pytest.mark.parametrize("value", [999, None, sum])
    def test_validate_raises_type(self, example_class, value):
        with pytest.raises(TypeError, match="Expected"):
            example_class(value)

    @pytest.mark.parametrize(
        "value",
        [
            "plain_address",
            "Abc..123@example.com",
            "email@example.com (Joe Smith)",
            ".email@example.com",
            r"”(),:;<>[\]@example.com",
        ],
    )
    def test_validate_raises_value(self, example_class, value):
        with pytest.raises(ValueError, match="Expected"):
            example_class(value)


class TestUrlValidator:
    @pytest.fixture()
    def example_class(self):
        class Example:
            url = UrlValidator()

            def __init__(self, url) -> None:
                self.url = url

        return Example

    @pytest.mark.parametrize(
        "value",
        [
            "https://www.asr-uglesbit.edu/",
            "http://www.google.com/~as_db3.2123/134-1a",
            "http://2.google.co.",
            "http://ko.wikipedia.org/wiki/위키백과:대문",
        ],
    )
    def test_validate(self, example_class, value):
        inst = example_class(value)
        assert inst.url == value

    @pytest.mark.parametrize("value", [999, None, sum])
    def test_validate_raises_type(self, example_class, value):
        with pytest.raises(TypeError, match="Expected"):
            example_class(value)

    @pytest.mark.parametrize(
        "value",
        [
            "plain_address",
            "example.com",
            "http://..google.co.",
            "http:///..google.co.",
            "http://...",
        ],
    )
    def test_validate_raises_value(self, example_class, value):
        with pytest.raises(ValueError, match="Expected"):
            example_class(value)
