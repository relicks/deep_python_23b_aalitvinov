# flake8: noqa: E501, PLR0913
from __future__ import annotations

import argparse
import asyncio
import logging
import pathlib
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus
from types import TracebackType

import aiofiles
import aiohttp

PRODUCE_DIR = pathlib.Path("./parsed_htmls/")
N_LINES = 50
TIMEOUT = 10.0
PRODUCER_QUEUE_LIMIT = 500

logger = logging.getLogger(__name__)


class Fetcher:
    def __init__(
        self,
        limit: int,
        input_file: pathlib.Path | str,
        out_dir: pathlib.Path,
        max_io_workers: int | None = None,
        chunk_size: int = 512,
    ) -> None:
        self.conn = aiohttp.TCPConnector(limit=limit, ttl_dns_cache=300)
        self.session = aiohttp.ClientSession(connector=self.conn)
        self.th_pool = ThreadPoolExecutor(max_workers=max_io_workers)
        self.que = asyncio.Queue(maxsize=PRODUCER_QUEUE_LIMIT)

        self.input_file = input_file
        self.out_dir = out_dir
        self.chunk_size = chunk_size
        self.read_count = 1

        self.out_dir.mkdir(exist_ok=True)

    async def close(self) -> None:
        logger.info("Shutting down `Fetcher` instance...")
        await self.session.close()
        await self.conn.close()
        self.th_pool.shutdown(wait=True)
        logger.info("`Fetcher` instance is closed!")

    async def _fetch_url(self, url: str):
        n_file = self.read_count
        save_path = self.out_dir.joinpath(f"{n_file}.html").resolve()
        self.read_count += 1
        logger.debug("Spinning up fetching routine with url %s", url)
        async with self.session.get(url) as resp:
            if resp.status == HTTPStatus.OK:
                logger.debug("Response is OK, opening file %d on disk", n_file)

                async with aiofiles.open(
                    file=save_path, mode="wb", executor=self.th_pool
                ) as fd:
                    logger.debug("File %d is opened, writing to disk", n_file)
                    async for chunk in resp.content.iter_chunked(self.chunk_size):
                        await fd.write(chunk)
                logger.debug("File %d is closed, exiting coroutine", n_file)

    async def _read_urls_from_file(self) -> None:
        async with aiofiles.open(self.input_file, mode="r") as f:
            logger.info("Started reading input file")
            file_count = 0
            async for line in f:
                await self.que.put(line.rstrip("\n"))
                # ? Reading only `N_LINES` first lines
                if N_LINES is not None and file_count >= N_LINES:
                    break
                file_count += 1
        logger.info("Done reading input file, sending STOP signal")
        await self.que.put(None)

    async def task_runner(self, timeout: float):
        reader = asyncio.create_task(self._read_urls_from_file())
        tasks = []
        logger.info("Firing fetching coroutine")
        while True:
            logger.debug("Waiting for queue")
            url = await self.que.get()
            if url is None:  # None is STOP signal
                break
            logger.debug("Got url: %s", url)
            tasks.append(
                asyncio.create_task(
                    asyncio.wait_for(self._fetch_url(url), timeout=timeout)
                )
            )
        logger.info("Awaiting reader task")
        await reader
        logger.info("Awaiting fetching tasks")
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Fetching coroutine done")

    async def __aenter__(self) -> Fetcher:
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        await self.close()


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
        "({asctime}) [{levelname}] in: {filename}:{lineno} |> {message}",
        style="{",
    )
    file_handler = logging.FileHandler(log_file_path, mode="w")
    file_handler.setFormatter(file_handler_formatter)
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)

    if print_stdout:
        stream_handler = logging.StreamHandler()
        stream_handler_formatter = logging.Formatter(
            "({asctime}) [{levelname}] in: {filename}:{lineno} |> {message}",
            style="{",
            datefmt="%I:%M:%S",
        )
        stream_handler.setFormatter(stream_handler_formatter)
        stream_handler.setLevel(logging.INFO)
        logger.addHandler(stream_handler)


async def main():
    args = setup_cli()
    logger.info("Parsed CLI args: %s", args)
    configure_logger(logger, log_file_path="./logs/fetcher.log", print_stdout=True)

    PRODUCE_DIR.mkdir(exist_ok=True)

    logger.info("Spawning fetching coroutines")
    async with Fetcher(
        limit=args.connections, input_file=args.file_path, out_dir=PRODUCE_DIR
    ) as fetcher:
        await fetcher.task_runner(timeout=TIMEOUT)


if __name__ == "__main__":
    # ? for rationale see https://github.com/aio-libs/aiohttp/issues/1925#issuecomment-1625391433
    loop = asyncio.get_event_loop_policy().get_event_loop()
    logger.info("Starting 'main' in current event loop")
    loop.run_until_complete(main())
    # asyncio.run(main())
