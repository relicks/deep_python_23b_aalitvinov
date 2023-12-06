# flake8: noqa: E501
from __future__ import annotations

import argparse
import asyncio
import logging
import pathlib
from collections.abc import Iterable, Sequence
from http import HTTPStatus
from types import TracebackType

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
        logger.debug("Shutting down `Fetcher` instance...")
        await self.session.close()
        await self.conn.close()
        logger.debug("`Fetcher` instance is closed!")

    async def fetch_url(self, url: str):
        save_path = self.out_dir.joinpath(f"{self.read_count}.html").resolve()
        self.read_count += 1
        logger.debug("Spinning up fetching routine with url %s", url)
        async with self.session.get(url) as resp:
            if resp.status == HTTPStatus.OK:
                logger.debug("Response is OK, streaming to file on disk")
                async with aiofiles.open(file=save_path, mode="wb") as fd:
                    async for chunk in resp.content.iter_chunked(self.chunk_size):
                        await fd.write(chunk)

    async def __aenter__(self) -> Fetcher:
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
        logger.info("Creating fetching tasks")
        tasks = [
            asyncio.create_task(
                asyncio.wait_for(fetcher.fetch_url(url), timeout=timeout)
            )
            for url in urls
        ]
        logger.info("Awaiting fetching tasks")
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


def configure_logger(
    logger: logging.Logger,
    log_file_path: str,
    logger_level: int = logging.DEBUG,
    print_stdout: bool = False,
):
    logger.setLevel(logger_level)

    file_handler_formatter = logging.Formatter(
        "({asctime}) [{levelname}] in: {filename} |> {message}",
        style="{",
    )
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(file_handler_formatter)
    file_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)

    if print_stdout:
        stream_handler = logging.StreamHandler()
        stream_handler_formatter = logging.Formatter(
            "({asctime}) [{levelname}] in: {filename}, lineno:{lineno} |> {message}",
            style="{",
            datefmt="%I:%M:%S",
        )
        stream_handler.setFormatter(stream_handler_formatter)
        stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler)


async def main():
    args = setup_cli()
    logger.info("Parsed CLI args: %s", args)
    configure_logger(logger, log_file_path="./logs/fetcher.log", print_stdout=True)

    # TODO: Read file with urls iteratively and async-ly
    with open(args.file_path) as file_stream:
        logger.info("Reading file with urls from '%s'", args.file_path)
        urls = file_stream.read().rstrip("\n").split("\n")
    logger.info("Input file proccessed")
    PRODUCE_DIR.mkdir(exist_ok=True)

    logger.info("Spawning fetching coroutines")
    await batch_fetch(urls, limit=args.connections, timeout=30.0)


if __name__ == "__main__":
    # ? for rationale see https://github.com/aio-libs/aiohttp/issues/1925#issuecomment-1625391433
    loop = asyncio.get_event_loop_policy().get_event_loop()
    logger.info("Starting main in current event loop")
    loop.run_until_complete(main())
    # asyncio.run(main())
