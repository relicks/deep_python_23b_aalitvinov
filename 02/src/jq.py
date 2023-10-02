"""Содержит решение для первого пункта домашнего задание #02."""
from collections.abc import Callable
from typing import Any

import orjson


def parse_json(
    json_str: str,
    required_fields: list[str] | None = None,
    keywords: list[str] | None = None,
    keyword_callback: Callable[[str], Any] | None = None,
) -> None:
    jdic: dict[str, str] = orjson.loads(json_str)

    if required_fields is None:
        required_fields = list(jdic.keys())

    for k in required_fields:
        words = jdic[k].split()
        if keyword_callback is not None:
            if keywords is None:
                [keyword_callback(word) for word in words]
            else:
                [keyword_callback(word) for word in words if word in keywords]
