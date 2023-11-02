import asyncio
import concurrent.futures
import json
import threading
from asyncio import StreamReader, StreamWriter
from collections import Counter
from html.parser import HTMLParser
from http import HTTPStatus
from urllib.error import URLError
from urllib.request import urlopen

N_TOP_WORDS = 10
N_WORKERS = 6


class MyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._text = []

    def handle_data(self, data):
        start_tag = self.get_starttag_text()
        parsed_data = [word.lower() for word in data.split() if word.isalpha()]
        if (
            start_tag is not None
            and parsed_data
            and not any(substr in start_tag for substr in ("script", "style"))
        ):
            self._text.extend(parsed_data)

    def get_parsed_data(self):
        return self._text


def get_words_from_url(url: str, parser_cls: type[MyParser]) -> list[str] | None:
    parser = parser_cls()
    try:
        resp = urlopen(url)
    except URLError:
        return None
    else:
        if resp.code == HTTPStatus.OK:
            parser.feed(resp.read().decode())
            return parser.get_parsed_data()


def count_top_words(words, n_top):
    count = Counter(words)
    return dict(count.most_common()[: n_top - 1])


async def handle_url(reader: StreamReader, writer: StreamWriter) -> None:
    data = await reader.read(5000)
    url = data.decode()

    addr = writer.get_extra_info("peername")
    print(f"Received {url!r} from {addr!r}")

    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(pool, worker_one, url)

    writer.write(json.dumps(response).encode())
    await writer.drain()

    writer.close()
    await writer.wait_closed()


def worker_one(url: str) -> dict[str, int]:
    name = threading.current_thread().name
    print(f"{name} Working on {url}")
    words = get_words_from_url(url, MyParser)
    top_words = count_top_words(words, N_TOP_WORDS)
    print(f"{name} Finished {url}")
    return top_words


async def main():
    server = await asyncio.start_server(handle_url, "127.0.0.1", 8888)

    address = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {address}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=N_TOP_WORDS)
    asyncio.run(main())
