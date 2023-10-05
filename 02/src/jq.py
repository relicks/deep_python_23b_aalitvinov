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
    """Calls `keyword_callback` on every found match in parsed JSON `str`.

    If `required_fields` is `None`, then looks for `keywords` in every row.

    :json_str: a JSON string to be parsed to Python dict
    :required_fields: keys of JSON dict to be searched for match in
    :keywords: values of JSON dict to search for in every matched key-value
    :keyword_callback: a function called on matched key, value
    """
    if keyword_callback is not None:
        # pylint: disable-next=no-member
        jdic: dict[str, str] = orjson.loads(json_str)

        if required_fields is None:
            required_fields = list(jdic.keys())

        if keywords is not None:
            keywords = [kword.casefold() for kword in keywords]

        for key in required_fields:  # iterating over json_dict keys
            words = jdic[key].split()
            for word in words:
                if (keywords is None) or (word.casefold() in keywords):
                    keyword_callback(key, word)
