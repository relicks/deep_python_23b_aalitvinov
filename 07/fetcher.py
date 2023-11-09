import argparse
import asyncio
from collections.abc import Iterable

import aiohttp


async def fetch_url(url: str, que: asyncio.Queue, sem: asyncio.Semaphore):
    async with aiohttp.ClientSession() as session:
        async with sem:
            async with session.get(url) as resp:
                # print(resp.status, url)
                body = await resp.read()
                await que.put((url, resp.status, body))
                # return resp.status


async def batch_fetch(
    urls: Iterable[str], que: asyncio.Queue, sem: asyncio.Semaphore, timeout: float
):
    tasks = [
        asyncio.create_task(asyncio.wait_for(fetch_url(url, que, sem), timeout=timeout))
        for url in urls
    ]
    await asyncio.gather(*tasks, return_exceptions=True)


async def main():
    parser = argparse.ArgumentParser(prog="Скрипт для асинхронной обкачки урлов")
    parser.add_argument(
        "-c",
        "--connections",
        type=int,
        default=10,
        help="number of simultaneous connections (default: 10)",
    )
    parser.add_argument("file_path", type=open, help="path to file with urls")
    args = parser.parse_args()

    sem = asyncio.Semaphore(args.connections)
    que = asyncio.Queue()
    urls = args.file_path.read().rstrip("\n").split("\n")
    await batch_fetch(urls, que, sem, 5.0)

    for i, (_, status, body) in enumerate(que._queue):  # type: ignore
        if status == 200:
            with open(f"./parsed_htmls/{i+1}.html", "w") as fs:
                fs.write(body.decode())

    print(que.qsize())


if __name__ == "__main__":
    asyncio.run(main())
