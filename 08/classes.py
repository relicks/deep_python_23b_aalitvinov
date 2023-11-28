import statistics
import timeit
import weakref
from random import Random
from typing import Any

SEED = 999
rng = Random(SEED)


class Regular:
    def __init__(self, first: Any, second: Any) -> None:
        self.first = first
        self.second = second


class Slotted:
    __slots__ = ("first", "second")

    def __init__(self, first: Any, second: Any) -> None:
        self.first = first
        self.second = second


class Weak:
    def __init__(self, first: Any, second: Any) -> None:
        self.first = weakref.ref(first)
        self.second = weakref.ref(second)


def invoker(cls: type) -> Any:
    return cls({rng.random()}, {rng.random()})


def attr_reader(cls: type) -> None:
    inst = invoker(cls)
    _ = inst.first
    _ = inst.second


def attr_writer(cls: type) -> None:
    inst = invoker(cls)
    inst.first = {rng.random()}
    inst.second = {rng.random()}


def bench(func, n_runs=5, n_loops=1_000_000):
    race = timeit.repeat(func, repeat=n_runs, number=n_loops)
    race = [run / n_loops for run in race]
    infimum = round(min(race) * 10**9)
    mean = round(statistics.mean(race) * 10**9)
    std = round(statistics.stdev(race) * 10**9, 1)
    print(
        f"\033[1m{mean} ns ± {std} ns\033[0m per loop"
        + f" (mean ± std. dev. of {n_runs} runs, {n_loops} loops each)"
        + f"\nbest time \033[1m\033[32m{infimum}\033[39m ns"
    )
    return {"mean": mean, "stdev": std, "min": infimum}
