import concurrent.futures
import json
from collections.abc import Iterable, Iterator
from itertools import islice
from pprint import pp
from typing import Any
from urllib.request import urlopen

ADDR = "http://localhost"
PORT = "8087"
SERVER_URL = f"{ADDR}:{PORT}"
MAX_WORKERS = 10


def batched(iterable: Iterable[Any], chunk_size: int) -> Iterator[tuple[Any, ...]]:
    iterator = iter(iterable)
    while chunk := tuple(islice(iterator, chunk_size)):
        yield chunk


def getter(addr: str, values: dict[str, Iterable[str]]):
    resp = urlopen(addr, data=json.dumps(values).encode())
    return json.loads(resp.read())


# for _ in range(10):
#     th = threading.Thread(
#         target=asyncio.run,
#         args=(tcp_echo_client("https://ru.wikipedia.org/wiki/Python"),),
#     )
#     th.start()


if __name__ == "__main__":
    with open("./urls.txt") as fs:
        urls_list = [line.rstrip("\r\n") for line in fs.readlines()]

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(getter, SERVER_URL, {"urls": [url]})
            for url in urls_list[:5]
        ]
        for future in concurrent.futures.as_completed(futures):
            pp(future.result()["urls"])
