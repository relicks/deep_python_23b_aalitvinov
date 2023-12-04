# flake8: noqa: E501
import argparse
import asyncio
import logging
import pathlib
from collections.abc import Iterable, Sequence
from http import HTTPStatus
from types import TracebackType
from typing import Self

import aiofiles
import aiohttp

PRODUCE_DIR = pathlib.Path("./parsed_htmls/")

logger = logging.getLogger(__name__)


class Fetcher:
    def __init__(
        self,
        limit: int,
    ) -> None:
        self.conn = aiohttp.TCPConnector(limit=limit, ttl_dns_cache=300)
        self.session = aiohttp.ClientSession(connector=self.conn)
        self.out_dir = pathlib.Path("./parsed_htmls/")
        self.chunk_size = 512

        self.read_count = 0
        self.out_dir.mkdir(exist_ok=True)

    async def close(self) -> None:
        await self.session.close()
        await self.conn.close()

    async def fetch_url(self, url: str):
        async with self.session.get(url) as resp:
            if resp.status == HTTPStatus.OK:
                async with aiofiles.open(
                    file=self.out_dir / f"{self.read_count}", mode="wb"
                ) as fd:
                    async for chunk in resp.content.iter_chunked(self.chunk_size):
                        await fd.write(chunk)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        await self.close()


async def batch_fetch(urls: Iterable[str], limit: int, timeout: float):
    async with Fetcher(limit=limit) as fetcher:
        tasks = [
            asyncio.create_task(
                asyncio.wait_for(fetcher.fetch_url(url), timeout=timeout)
            )
            for url in urls
        ]
        await asyncio.gather(*tasks, return_exceptions=True)


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

    with open(args.file_path) as file_stream:
        urls = file_stream.read().rstrip("\n").split("\n")
    await batch_fetch(urls, limit=args.connections, timeout=30.0)

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
