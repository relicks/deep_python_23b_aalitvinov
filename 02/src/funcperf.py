"""Содержит решение для второго пункта домашнего задание #02."""


import statistics
import sys
from collections import deque
from collections.abc import Callable
from functools import wraps
from time import perf_counter_ns
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def mean(n_last: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Calculates the average time of `n_last` calls to `func` and prints it to stdout.

    :n_last: how many last calls to include in average time calculation.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        timings: deque[int] = deque(maxlen=n_last)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            begin = perf_counter_ns()
            result = func(*args, **kwargs)
            time_elapsed_ns = perf_counter_ns() - begin

            timings.append(time_elapsed_ns)
            print(
                f"The last {len(timings)} calls of {func.__name__} took "
                f"`{statistics.mean(timings) / 1e6:.2f}` ms on average.",
                file=sys.stderr,
            )
            return result

        return wrapper

    return decorator
