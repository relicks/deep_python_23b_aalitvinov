"""Содержит решение к первому пункту ДЗ#04."""
from __future__ import annotations

import logging
from typing import Any

PREFIX = "custom_"


def prefix_dict(dict_: dict[str, Any], prefix: str):
    return {
        f"{prefix}{k}" if not k.startswith(("__", prefix)) else k: v
        for k, v in dict_.items()
    }


def attr_setter(obj: object, name: str, value: Any, supertype: object):
    logging.info(f"Setting from {obj.__class__.__name__}, {name = }, {value = }")
    is_special_or_prefixed = name.startswith(("__", PREFIX)) and name.endswith("__")
    if is_special_or_prefixed:
        supertype.__setattr__(name, value)
    else:
        supertype.__setattr__(f"{PREFIX}{name}", value)


class AttrSetter:
    def __setattr__(self, name: str, value: Any) -> None:
        attr_setter(self, name, value, super())


class CustomMeta(type):
    def __new__(
        mcs: type[CustomMeta],  # noqa: N804
        name: str,
        bases: tuple[type, ...],
        dct: dict[str, Any],
    ) -> CustomMeta:
        logging.info("meta __new__")
        new_dct = prefix_dict(dct, PREFIX)
        new_class = super().__new__(mcs, name, (AttrSetter, *bases), new_dct)
        return new_class

    def __init__(cls, name: str, bases: tuple[type, ...], dct: dict[str, Any]) -> None:
        logging.info("meta __init__")
        super().__init__(name, bases, dct)

    def __call__(cls, *args, **kwargs) -> Any:
        logging.info("meta __call__")
        result = super().__call__(*args, **kwargs)
        result.__dict__ = prefix_dict(result.__dict__, PREFIX)
        return result

    def __setattr__(cls, name: str, value: Any) -> None:
        attr_setter(cls, name, value, super())
