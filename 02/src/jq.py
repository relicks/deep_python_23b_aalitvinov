"""Содержит решение для первого пункта домашнего задание #02."""
from collections.abc import Callable
from typing import Any

import orjson


def parse_json(
    json_str: str,
    required_fields: list[str] | None = None,
    keywords: list[str] | None = None,
    keyword_callback: Callable[[str, str], Any] | None = None,
) -> None:
    if keyword_callback is not None:
        jdic: dict[str, str] = orjson.loads(json_str)

        if required_fields is None:
            required_fields = list(jdic.keys())

        if keywords is not None:
            keywords = [kword.lower() for kword in keywords]

        for key in required_fields:  # iterating over json_dict keys
            words = jdic[key].split()
            for word in words:
                if (keywords is None) or (word.lower() in keywords):
                    keyword_callback(key, word)
