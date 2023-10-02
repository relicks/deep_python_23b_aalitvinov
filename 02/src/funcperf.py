"""Содержит решение для первого пункта домашнего задание #02."""


import logging
import statistics
from collections import deque
from collections.abc import Callable
from functools import wraps
from time import perf_counter_ns
from typing import ParamSpec, TypeVar

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

P = ParamSpec("P")
R = TypeVar("R")


def mean(n_last: int):
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        timings = deque(maxlen=n_last)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            begin = perf_counter_ns()
            result = func(*args, **kwargs)
            time_elapsed_ns = perf_counter_ns() - begin
            timings.append(time_elapsed_ns)
            logger.info(
                f"The last {len(timings)} calls of {func.__name__} took "
                f"{statistics.mean(timings) / 1e6:.2f} ms on average."
            )
            return result

        return wrapper

    return decorator
