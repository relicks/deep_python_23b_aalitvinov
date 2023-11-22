import argparse
import json
import logging
import os
import sys
import threading
from collections import Counter, OrderedDict
from collections.abc import Sequence
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from queue import Queue
from signal import SIGINT
from typing import Any, TypeAlias
from urllib.error import URLError
from urllib.request import urlopen

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa
else:
    ic.configureOutput(includeContext=True)

from html_parser import parse_html

LOG_LEVEL = os.environ.get("LOGLEVEL", logging.NOTSET)


DEFAULT_MAX_WORKERS = 10
DEFAULT_TOP_WORDS = 5
RESPONSE_TIMEOUT = 5.0

ADDR = ""
PORT = 8087
DEBUG_LOCK = threading.Lock()

logger = logging.getLogger(__name__)
if LOG_LEVEL:
    logger.setLevel(LOG_LEVEL)
    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVEL)
    logger.addHandler(ch)

InQueue: TypeAlias = Queue[str]
OutQueue: TypeAlias = Queue[dict[str, dict[str, int]] | dict[str, None]]
PrimeQueue: TypeAlias = Queue[tuple[InQueue, OutQueue]]

JsonTypes: TypeAlias = str | int | float | bool | None


def get_url_vocab(url: str) -> list[str] | None:
    try:
        resp = urlopen(url, timeout=RESPONSE_TIMEOUT)
    except URLError:
        return None
    else:
        if resp.code == HTTPStatus.OK:
            result = parse_html(resp.read().decode())
            resp.close()
            return result
        return None


def get_top_words(url: str, n_top: int) -> dict[str, dict[str, int]] | dict[str, None]:
    words = get_url_vocab(url)
    if words:
        count = Counter(words)
        return {url: OrderedDict(count.most_common()[:n_top])}
    return {url: None}


class CustomRequestHandler(BaseHTTPRequestHandler):
    mainline_queue: PrimeQueue = Queue()

    def _parse_request_query(self) -> dict[str, JsonTypes] | None:
        c_len = self.headers.get("Content-Length", "")
        content_length = int(c_len) if c_len.isdecimal() else 0  # parsing
        if content_length:
            request_binary = self.rfile.read(content_length)
            try:
                return json.loads(request_binary.decode())
            except json.decoder.JSONDecodeError:
                return None
        return None

    def _proccess_request(
        self,
        query: dict[str, Any],
        url_field_name: str,
    ) -> dict[str, dict[str, int] | None]:
        out_dict = {}
        client_in_queue: InQueue = Queue()
        client_out_queue: OutQueue = Queue()

        # ? Putting elements in Consumer queue
        for url in query.get(url_field_name, ()):
            client_in_queue.put(url)
            type(self).mainline_queue.put((client_in_queue, client_out_queue))
        client_in_queue.join()  # Waiting for url proccessing by workers

        # ? Getting elements from Producer queue
        for url_result in client_out_queue.queue:
            out_dict.update(url_result)
        return {url_field_name: out_dict}

    def do_POST(self):  # noqa: N802
        logger.info(f"Connection from {self.client_address}")

        query = self._parse_request_query()  # ? Parse request
        if not query:
            # ? Response head
            self.send_error(400, "Cannot parse your query.")
            self.end_headers()
            # ? END Response head
        else:
            # ? Response head
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            # ? END Response head

            # ? Proccess request
            url_field_name = "urls"
            result = self._proccess_request(query, url_field_name)
            # ? END Proccess request

            # ? Send reply
            json_str = json.dumps(result)
            self.wfile.write(json_str.encode(encoding="utf-8"))  # type: ignore
            # ? END Send reply


_global_url_counter = 0


def _worker(main_queue: PrimeQueue, num_top_words: int) -> None:
    global _global_url_counter  # noqa: PLW0603
    while True:
        name = threading.current_thread().name
        client_in_queue, client_out_queue = main_queue.get()

        url = client_in_queue.get()
        logger.debug(f"{name} Working on {url}")

        top_words = get_top_words(url, num_top_words)
        client_out_queue.put(top_words)
        client_in_queue.task_done()
        logger.debug(f"{name} Finished {url}")

        _global_url_counter += 1
        print("Urls parsed: ", _global_url_counter)


def _spawn_workers(
    main_queue: PrimeQueue, num_workers: int, num_top_words: int
) -> list[threading.Thread]:
    workers = [
        threading.Thread(
            target=_worker,
            args=(main_queue, num_top_words),
            name=f"worker {i}",
            daemon=True,
        )
        for i in range(num_workers)
    ]
    for thread in workers:
        thread.start()
    logger.info(f"Started {num_workers} workers.")
    return workers


def _serve(
    handler: type[BaseHTTPRequestHandler],
    main_queue: PrimeQueue,
    num_workers: int,
    num_top_words: int,
) -> None:
    _ = _spawn_workers(main_queue, num_workers, num_top_words)

    with ThreadingHTTPServer((ADDR, PORT), handler) as httpd:
        print(
            f"Serving at {httpd.server_address[0]} port {httpd.server_port}",
            file=sys.stderr,
        )
        httpd.serve_forever()


class _MyArgs(argparse.Namespace):
    num_workers: int
    num_top_words: int


def _args_parser(default_commands: Sequence[str] | None = None) -> _MyArgs:
    commands = sys.argv[1:] or default_commands
    logger.debug(f"Passed commands to _args_parser: {commands}")
    parser = argparse.ArgumentParser(
        prog="Серверный скрипт для асинхронной обкачки урлов с помощью потоков."
    )
    parser.add_argument(
        "-w",
        "--num-workers",
        type=int,
        default=(dv := DEFAULT_MAX_WORKERS),
        help=f"number of simultaneous connections (default: {dv})",
    )
    parser.add_argument(
        "-k",
        "--num-top-words",
        type=int,
        default=(dv := DEFAULT_TOP_WORDS),
        help=f"number of top words to return (default: {dv})",
    )
    args: _MyArgs = parser.parse_args(commands)  # type: ignore
    return args


def _main() -> None:
    handler = CustomRequestHandler
    cfg = _args_parser()
    logger.info(f"Parsed args: {cfg}")
    try:
        _serve(handler, handler.mainline_queue, cfg.num_workers, cfg.num_top_words)
    except KeyboardInterrupt:
        print("\nClosing server...", file=sys.stderr)
        sys.exit(128 + SIGINT)
    finally:
        print("Closed!", file=sys.stderr)


if __name__ == "__main__":
    _main()
