"""Содержит решение к первому пункту ДЗ#04."""
from typing import Any

from typing_extensions import Self

PREFIX = "custom_"


def prefix_dict(dict_: dict[str, Any], prefix: str | None = None):
    prefix = prefix or PREFIX
    return {
        f"{prefix}{k}" if not k.startswith(("__", PREFIX)) else k: v
        for k, v in dict_.items()
    }


def attr_setter(obj: object, name: str, value: Any, supertype: object):
    print(f"Setting from {obj.__class__.__name__}, {name = }, {value = }")
    if name.startswith(("__", PREFIX)):
        supertype.__setattr__(name, value)
    else:
        supertype.__setattr__(f"{PREFIX}{name}", value)


class AttrSetter:
    def __setattr__(self, name: str, value: Any) -> None:
        attr_setter(self, name, value, super())


class CustomMeta(type):
    def __new__(
        cls: type[Self], name: str, bases: tuple[type, ...], dct: dict[str, Any]
    ) -> Self:
        print("meta __new__")
        new_dct = prefix_dict(dct)
        new_class = super().__new__(cls, name, (AttrSetter, *bases), new_dct)
        return new_class

    def __init__(
        cls: type[Any], name: str, bases: tuple[type, ...], dct: dict[str, Any]
    ) -> None:
        print("meta __init__")
        # super().__init__(name, bases, dct)

    def __call__(cls: type[Any], *args, **kwargs) -> Any:
        print("meta __call__")
        result = super().__call__(*args, **kwargs)
        result.__dict__ = prefix_dict(result.__dict__)
        return result

    def __setattr__(cls, name: str, value: Any) -> None:
        attr_setter(cls, name, value, super())
