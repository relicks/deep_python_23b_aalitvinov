"""Содержит решение ко второму пункту ДЗ#04."""
import re
from abc import ABC, abstractmethod
from typing import Any


# from https://docs.python.org/3/howto/descriptor.html#validator-class
class Validator(ABC):
    """Abstract base class for Validator data descriptors."""

    def __set_name__(self, owner: type, name: str):
        self.private_name = "_" + name

    def __get__(self, obj: object, objtype: type | None = None):
        return getattr(obj, self.private_name)

    def __set__(self, obj: object, value: Any):
        err = self.validate(value)
        if err is not None:
            raise err
        setattr(obj, self.private_name, value)

    @abstractmethod
    def validate(self, value: Any) -> Exception | None:
        pass


class UInt64Validator(Validator):
    """Data descriptor that checks input to be valid 64-bit unsigned int."""

    _min_val = 0
    _max_val = 2**64 - 1

    def validate(self, value: int) -> TypeError | ValueError | None:
        if not isinstance(value, int):
            return TypeError(f"Expected {value!r} to be of type int.")
        if not self._min_val <= value <= self._max_val:
            return ValueError(
                f"Expected {value!r} to be in range "
                f"[{self._min_val}, {self._max_val}]"
            )
        return None


class EmailValidator(Validator):
    """Data descriptor that checks input to be valid email `str`."""

    _email_pattern = re.compile(
        r"^(?![\w\.@]*\.\.)(?![\w\.@]*\.@)(?![\w\.]*@\.)\w+[\w\.]*@[\w\.]+\.\w{2,}$"
    )

    def validate(self, value: str) -> TypeError | ValueError | None:
        if not isinstance(value, str):
            return TypeError(f"Expected {value!r} to be of type str.")
        if re.match(self._email_pattern, value) is None:
            return ValueError(f"Expected {value!r} to be a valid email address.")
        return None


class UrlValidator(Validator):
    """Data descriptor that checks input to be valid URL `str`."""

    # https://github.com/django/django/blob/stable/1.3.x/django/core/validators.py#L45
    _url_pattern = re.compile(
        r"^(?:http|ftp)s?://"  # scheme
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"  # domain...
        r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.UNICODE | re.IGNORECASE,
    )

    def validate(self, value: Any) -> TypeError | ValueError | None:
        if not isinstance(value, str):
            return TypeError(f"Expected {value!r} to be of type str.")
        if re.match(self._url_pattern, value) is None:
            return ValueError(f"Expected {value!r} to be a valid URL.")
        return None
