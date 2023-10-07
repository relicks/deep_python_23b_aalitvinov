"""Содержит тесты решения ДЗ#01.2."""
# pylint: disable=redefined-outer-name
# pylint: disable=missing-function-docstring,missing-class-docstring

from collections.abc import Iterator
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from src.read_generator import grepfile, grepiter


@pytest.fixture(scope="module")
def datafiles_path() -> Path:
    return Path(__file__).resolve().parent.joinpath("data")


@pytest.fixture(scope="module")
def file_path(datafiles_path: Path) -> Path:
    data_path = datafiles_path.joinpath("calabaria.txt")
    if data_path.exists():
        return data_path
    raise FileNotFoundError(f"This file doesn't exist: {data_path}")


class TestGrepIter:
    @pytest.fixture()
    def in_text(self) -> list[str]:
        return [
            "   In the simplest terms, a test is meant to look at the ",
            "result of a particular behavior, and make sure that result ",
            "aligns with what you would expect. Behavior is not ",
            "something that can be empirically measured, which is",
            "why writing tests can be challenging.",
        ]

    def test_empty(self):
        assert not list(grepiter([], [""]))

    def test_normal(self, in_text: list[str]):
        assert list(grepiter(in_text, ["test"])) == [
            "   In the simplest terms, a test is meant to look at the "
        ]
        assert list(grepiter(in_text, ["is"])) == [
            "   In the simplest terms, a test is meant to look at the ",
            "aligns with what you would expect. Behavior is not ",
            "something that can be empirically measured, which is",
        ]

    def test_several_words(self, in_text: list[str]):
        """Несколько совпадений."""
        filter_words = ["test", "can"]
        assert list(grepiter(in_text, filter_words)) == [
            "   In the simplest terms, a test is meant to look at the ",  # ? "test"
            "something that can be empirically measured, which is",  # ? "can"
            "why writing tests can be challenging.",  # ? "can"
        ]

    def test_word_case(self, in_text: list[str]):
        """Проверка совпадения с учетом регистронезависимости."""
        filter_words = ["WRIting"]
        assert list(grepiter(in_text, filter_words)) == [
            "why writing tests can be challenging."
        ]

    def test_several_matches(self, in_text: list[str]):
        """Совпадение нескольких фильтров в одной строке."""
        filter_words = ["the", "test", "meant"]
        assert list(grepiter(in_text, filter_words)) == [
            "   In the simplest terms, a test is meant to look at the "
        ]

    def test_match_whole_line(self):
        """Слово фильтр целиком совпадает со строкой в файле."""
        assert list(grepiter(["aa", "bb"], ["aa"])) == ["aa"]


class TestGrepFile:
    @staticmethod
    def assert_iter(file_or_path):
        itr: Iterator[str] = grepfile(file_or_path, ["ОКРАСКА"])
        assert next(itr) == "Окраска калабарии невзрачна"
        with pytest.raises(StopIteration):
            next(itr)

    def test_open_path(self, file_path: Path):
        self.assert_iter(file_path)

    def test_open_str(self, file_path: Path):
        self.assert_iter(str(file_path))

    def test_with_opened_file(self, file_path: Path):
        with open(file_path, encoding="utf-8") as file_stream:
            self.assert_iter(file_stream)

    def test_empty_file(self, datafiles_path: Path):
        empty_file_grepped: Iterator[str] = grepfile(datafiles_path / "empty.txt", [""])
        with pytest.raises(StopIteration):
            next(empty_file_grepped)

    def test_mocking(self, mocker: MockerFixture, file_path: Path):
        mock = mocker.mock_open(read_data="Данные\nУдалены")
        mocker.patch("builtins.open", mock)

        itr: Iterator[str] = grepfile(file_path, ["ДАННЫЕ"])
        assert next(itr) == "Данные"
        with pytest.raises(StopIteration):
            next(itr)

    def test_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            list(grepfile("./invalid/path", ["noop"]))

    def test_type_error(self):
        with pytest.raises(TypeError):
            list(grepfile(43, ["oops"]))  # type: ignore
