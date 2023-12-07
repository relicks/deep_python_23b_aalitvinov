"""Библиотека для парсинга и сериализации json (с помощью C API)."""
# pylint: disable-next=E0401
from cjsonmodule import dumps, loads

__all__ = ["loads", "dumps"]
