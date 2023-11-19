import argparse
import json
import os
import sys
from collections.abc import Iterable, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import islice
from pprint import pp
from typing import TypeVar
from urllib.request import urlopen

DEBUG = bool(os.environ.get("PY_DEBUG"))

ADDR = "http://localhost"
PORT = "8087"
SERVER_URL = f"{ADDR}:{PORT}"
DEFAULT_MAX_WORKERS = 10
BATCH_SIZE = 4
FILE_PATH = "./urls.txt"
T = TypeVar("T")


class MyArgs(argparse.Namespace):
    num_workers: int
    file_path: str


def batched(iterable: Iterable[T], chunk_size: int) -> Iterator[tuple[T, ...]]:
    """Batch data from the iterable into tuples of length n.

    The last batch may be shorter than n.
    Loops over the input iterable and accumulates data into tuples up to size n.
    he input is consumed lazily, just enough to fill a batch. The result is
    yielded as soon as the batch is full or when the input iterable is exhausted.

    SOURCE: https://realpython.com/how-to-split-a-python-list-into-chunks
    """
    iterator = iter(iterable)
    while chunk := tuple(islice(iterator, chunk_size)):
        yield chunk


def args_parser() -> MyArgs:
    commands = sys.argv[1:] or (["urls.txt"] if DEBUG else None)
    parser = argparse.ArgumentParser(
        prog="Клиентский скрипт для асинхронной обкачки урлов с помощью потоков."
    )
    parser.add_argument(
        "-w",
        "--num-workers",
        type=int,
        default=(dv := DEFAULT_MAX_WORKERS),
        help=f"number of simultaneous connections (default: {dv})",
    )
    parser.add_argument("file_path", help="path to file with urls")
    args: MyArgs = parser.parse_args(commands)  # type: ignore
    return args


def getter(
    addr: str, values: dict[str, Iterable[str]]
) -> dict[str, dict[str, int] | None]:
    resp = urlopen(addr, data=json.dumps(values).encode())
    return json.loads(resp.read())


def main() -> None:
    args = args_parser()

    url_field_name = "urls"
    with ThreadPoolExecutor(max_workers=args.num_workers) as executor:
        with open(args.file_path) as fs:
            futures = tuple(
                executor.submit(
                    getter,
                    SERVER_URL,
                    {url_field_name: [url.rstrip("\n") for url in batch]},
                )
                for batch in batched(fs, BATCH_SIZE)
            )
        for future in as_completed(futures):
            pp(future.result()[url_field_name])


if __name__ == "__main__":
    main()
