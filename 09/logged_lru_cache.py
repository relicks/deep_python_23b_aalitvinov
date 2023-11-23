"""Содержит решение первого пункта HW09."""
import argparse
import logging
from collections.abc import Hashable
from typing import Any

modlogger = logging.getLogger(__name__)


class LRUCache:
    def __init__(self, limit: int = 42) -> None:
        modlogger.info("Initialized LRUCache instance with limit %d", limit)
        self._data: dict[Hashable, Any] = {}
        self._limit = limit

    def _emerge(self, key: Hashable) -> None:
        """Moves KV pair to the top of the data-dictionary."""
        modlogger.info("Moved key `%s` to the top", key)
        value = self._data[key]
        del self._data[key]
        self._data[key] = value
        modlogger.debug("Value moved was `%s`", value)

    def get(self, key: Hashable) -> Any | None:
        try:
            value = self._data[key]
        except KeyError:
            modlogger.error("Key `%s` does not exist in the LRUCache", key)
            return None
        else:
            modlogger.info("Key `%s` exists in the LRUCache", key)
            self._emerge(key)
            return value

    def set(self, key: Hashable, value: Any) -> None:
        if key in self._data:
            modlogger.info("Setting existing key `%s` with value `%s`", key, value)
        else:
            modlogger.info(
                "Key `%s` not found in the LRUCache, setting it with value `%s`",
                key,
                value,
            )

        self._data[key] = value
        self._emerge(key)
        if self._limit and len(self._data) >= self._limit + 1:
            modlogger.warning("LRUCache limit is reached, deleting bottom KV pair")
            first_key = next(iter(self._data))
            modlogger.debug("KV pair to be deleted -> `%s: %s`", key, value)
            del self._data[first_key]
        self._emerge(key)

    def _explode(self):
        modlogger.critical("💥💥💥! That shouldn't ever have been called. ☠️⚰️")
        raise NotImplementedError

    def __repr__(self) -> str:  # pragma: no cover
        return repr(self._data)

    def __iter__(self):
        return iter(self._data.items())


class _ExtraFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.args is not None and len(record.args) > 1


class _MyArgs(argparse.Namespace):
    print_stdout: bool
    enable_filter: bool


def _args_parser() -> _MyArgs:
    parser = argparse.ArgumentParser(prog="LRU-cache с логированием.")
    parser.add_argument(
        "-s",
        "--print-stdout",
        action="store_true",
        help="включает логирование в stdout",
    )
    parser.add_argument(
        "-f",
        "--enable-filter",
        action="store_true",
        help="включает фильтр логгера",
    )
    args: _MyArgs = parser.parse_args()  # type: ignore
    return args


def _configure_logger(logger: logging.Logger, cfg: _MyArgs):
    logger.setLevel(logging.DEBUG)

    file_handler_formatter = logging.Formatter(
        "\t{asctime} * [{levelname}]\t `{name}`\t in: {filename} | {message}",
        style="{",
    )
    file_handler = logging.FileHandler("./cache.log")
    file_handler.setFormatter(file_handler_formatter)
    file_handler.setLevel(logging.INFO)

    stream_handler_formatter = logging.Formatter(
        "\t{asctime}\t[{levelname}]\t --> "
        "{name}\t in: {filename}, lineno: {lineno} | {message}",
        style="{",
        datefmt="%I:%M:%S",
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_handler_formatter)
    stream_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)

    if cfg.print_stdout:
        logger.addHandler(stream_handler)

    if cfg.enable_filter:
        logger.addFilter(_ExtraFilter())


def _test_lru_cache():
    cache = LRUCache(3)

    cache.set("k1", "val1")
    cache.set("k2", "val2")
    cache.set("k3", "val3")

    assert cache.get("k2") == "val2"
    assert cache.get("k1") == "val1"
    assert cache.get("k2") == "val2"

    cache.set("k4", "val4")

    assert cache.get("k3") is None
    assert all(cache.get(k) is not None for k in ("k1", "k2", "k4"))

    try:
        cache._explode()
    except Exception:
        pass


def _main():
    _configure_logger(logger=modlogger, cfg=_args_parser())
    _test_lru_cache()


if __name__ == "__main__":
    _main()
