"""Содержит решение к первому пункту ДЗ#04."""
from __future__ import annotations

import logging
from typing import Any

PREFIX = "custom_"


def is_dunder_name(name: str) -> bool:
    """Checks if `name` is a double-underscore special name.

    Taken from C source:
    https://github.com/python/cpython/blob/dcb16c98be61630369227f0d893f8d9262d25cac/Objects/typeobject.c#L3870C2-L3870C2
    """  # noqa: E501, RUF100
    return (
        len(name) > 4
        and name.endswith("__")
        and name.startswith("__")
        and name.isascii()
    )


def prefix_dict(dict_: dict[str, Any], prefix: str):
    return {
        f"{prefix}{k}" if not (is_dunder_name(k) or k.startswith(prefix)) else k: v
        for k, v in dict_.items()
    }


def attr_setter(obj: object, name: str, value: Any, supertype: object):
    logging.info(f"Setting from {obj.__class__.__name__}, {name = }, {value = }")
    is_special_or_prefixed = is_dunder_name(name) or name.startswith(PREFIX)
    if is_special_or_prefixed:
        supertype.__setattr__(name, value)
    else:
        supertype.__setattr__(f"{PREFIX}{name}", value)


class _AttrSetter:
    def __setattr__(self, name: str, value: Any) -> None:
        attr_setter(self, name, value, super())


class CustomMeta(type):
    def __new__(
        mcs: type[CustomMeta],  # noqa: N804
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> CustomMeta:
        logging.info("meta __new__")
        new_namespace_dict = prefix_dict(namespace, PREFIX)
        new_class = super().__new__(
            mcs, name, (_AttrSetter, *bases), new_namespace_dict
        )
        return new_class

    def __init__(
        cls, name: str, bases: tuple[type, ...], dct: dict[str, Any], **kwds: Any
    ) -> None:
        logging.info("meta __init__")
        super().__init__(name, bases, dct, **kwds)

    def __call__(cls, *args, **kwargs) -> Any:
        logging.info("meta __call__")
        result = super().__call__(*args, **kwargs)
        result.__dict__ = prefix_dict(result.__dict__, PREFIX)
        return result

    def __setattr__(cls, name: str, value: Any) -> None:
        attr_setter(cls, name, value, super())
