# flake8: noqa: E501
import argparse
import asyncio
import logging
import pathlib
from collections.abc import Iterable, Sequence

import aiohttp

PRODUCE_DIR = pathlib.Path("./parsed_htmls/")

logger = logging.getLogger(__name__)


# see: https://docs.aiohttp.org/en/stable/client_quickstart.html#streaming-response-content
# TODO: Don't create a session per request. A session contains a connection pool inside.
async def fetch_url(url: str, que: asyncio.Queue, sem: asyncio.Semaphore) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with sem:
            async with session.get(url) as resp:
                body = await resp.read()
                await que.put((url, resp.status, body))
                return body


async def batch_fetch(
    urls: Iterable[str], que: asyncio.Queue, sem: asyncio.Semaphore, timeout: float
):
    tasks = [
        asyncio.create_task(asyncio.wait_for(fetch_url(url, que, sem), timeout=timeout))
        for url in urls
    ]
    return await asyncio.gather(*tasks, return_exceptions=True)


class MyArgs(argparse.Namespace):
    connections: int
    file_path: pathlib.Path


def setup_cli(default_args: Sequence[str] | None = None) -> MyArgs:
    parser = argparse.ArgumentParser(prog="Скрипт для асинхронной обкачки урлов")
    parser.add_argument(
        "-c",
        "--connections",
        type=int,
        default=(df := 10),
        help=f"number of simultaneous connections (default: {df})",
    )
    parser.add_argument("file_path", type=pathlib.Path, help="path to file with urls")
    namespace = MyArgs()
    parser.parse_args(default_args, namespace)
    return namespace


async def main():
    args = setup_cli()

    sem = asyncio.Semaphore(args.connections)
    que = asyncio.Queue()

    with open(args.file_path) as file_stream:
        urls = file_stream.read().rstrip("\n").split("\n")
    await batch_fetch(urls, que, sem, 5.0)

    PRODUCE_DIR.mkdir(exist_ok=True)
    for i, (_, status, body) in enumerate(que._queue):  # type: ignore
        if status == 200:
            with open(f"{PRODUCE_DIR}/{i+1}.html", "w") as fs:
                fs.write(body.decode())

    logger.info("%s URLs parsed", que.qsize())


if __name__ == "__main__":
    # ? for rationale see https://github.com/aio-libs/aiohttp/issues/1925#issuecomment-1625391433
    loop = asyncio.get_event_loop_policy().get_event_loop()
    loop.run_until_complete(main())
    # asyncio.run(main())
