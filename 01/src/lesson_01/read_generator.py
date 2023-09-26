"""Содержит решение к ДЗ#01.1."""
from collections.abc import Iterable, Iterator
from io import TextIOBase
from os import PathLike
from typing import TypeAlias, get_type_hints

TextFile: TypeAlias = TextIOBase


def grepiter(iterable: Iterable[str], wordfilter: list[str]) -> Iterator[str]:
    """Итеративно ищет список слов в каждом елементе `iterable`.

    Перебирает строки в итераторе и возвращает только
    те из них (строку целиком), где встретилось хотя бы одно из слов для поиска.
    Поиск выполняется по полному совпадению слова без учета регистра.
    """
    for line in iterable:
        if set(map(str.lower, wordfilter)).intersection(line.lower().split()):
            yield line.rstrip("\n")


def grepfile(
    file: str | PathLike[str] | TextFile, wordfilter: list[str], encoding="utf-8"
) -> Iterator[str]:
    """Итеративно ищет список слов в каждой строке `file`'а.

    Перебирает строки в файле и возвращает только
    те из них (строку целиком), где встретилось хотя бы одно из слов для поиска.
    Поиск выполняется по полному совпадению слова без учета регистра.
    """
    match file:
        case TextIOBase():  # if opened file, then pass directly to grepiter
            yield from grepiter(file, wordfilter)
        case str() | PathLike():  # if path to file, then we open it
            with open(file, encoding=encoding) as fstr:
                yield from grepiter(fstr, wordfilter)
        case _:
            raise TypeError(
                f"Incorrect file type: {type(file)}. "
                "The `file` argument only accepts the following types:\n"
                f"\t   {get_type_hints(grepfile)['file']}"
            )
