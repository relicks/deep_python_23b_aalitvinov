import argparse
import json
import logging
import os
import re
import sys
import threading
from abc import ABC, abstractmethod
from collections import Counter, OrderedDict
from collections.abc import Sequence
from html.parser import HTMLParser
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


LOG_LEVEL = os.environ.get("LOGLEVEL", logging.NOTSET)


DEFAULT_MAX_WORKERS = 10
DEFAULT_TOP_WORDS = 5
RESPONSE_TIMEOUT = 5.0

ADDR = ""
PORT = 8087
DEBUG_LOCK = threading.Lock()

logger = logging.getLogger(__name__)
global_url_counter = 0


WordCounts: TypeAlias = dict[str, int]
InQueue: TypeAlias = Queue[str]
OutQueue: TypeAlias = Queue[dict[str, WordCounts] | dict[str, None]]
PrimeQueue: TypeAlias = Queue[tuple[InQueue, OutQueue]]

JsonTypes: TypeAlias = str | int | float | bool | None


class HTMLDataParser(HTMLParser, ABC):
    @abstractmethod
    def handle_data(self, data: str) -> None:
        pass

    @property
    @abstractmethod
    def parsed_data(self) -> list[str]:
        pass


class WordParser(HTMLDataParser):
    def __init__(self):
        super().__init__()
        self._text: list[str] = []

    def handle_data(self, data):
        start_tag = self.get_starttag_text()
        alpha_string = re.sub(r"[^A-Za-z0-9 ]+", "", data).lower()
        parsed_data = [word.lower() for word in alpha_string.split()]
        if (
            start_tag is not None
            and parsed_data
            and not any(substr in start_tag for substr in ("script", "style"))
        ):
            self._text.extend(parsed_data)

    @property
    def parsed_data(self) -> list[str]:
        return self._text


def parse_html(body: str) -> list[str]:
    parser = WordParser()
    parser.feed(body)
    return parser.parsed_data


def get_url_vocab(url: str) -> list[str] | None:
    try:
        resp = urlopen(url, timeout=RESPONSE_TIMEOUT)
    except (URLError, ValueError):
        return None
    else:
        if resp.code == HTTPStatus.OK:
            result = parse_html(resp.read().decode())
            resp.close()
            return result
        return None


def get_top_words(url: str, n_top: int) -> dict[str, WordCounts] | dict[str, None]:
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
    ) -> dict[str, WordCounts | None]:
        out_dict: WordCounts = {}
        client_in_queue: InQueue = Queue()
        client_out_queue: OutQueue = Queue()

        # ? Putting elements in request's Consumer queue
        for url in query.get(url_field_name, ()):
            client_in_queue.put(url)
            type(self).mainline_queue.put((client_in_queue, client_out_queue))
        client_in_queue.join()  # Waiting for url proccessing by workers

        # ? Getting elements from request's Producer queue
        for url_result in client_out_queue.queue:
            out_dict.update(url_result)
        return {url_field_name: out_dict}

    def do_POST(self):  # noqa: N802
        logger.info("Connection from %s", self.client_address)

        query = self._parse_request_query()  # ? Parse request
        print(query)
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


def _worker(main_queue: PrimeQueue, num_top_words: int) -> None:
    global global_url_counter  # noqa: PLW0603
    while True:
        name = threading.current_thread().name
        client_in_queue, client_out_queue = main_queue.get()

        url = client_in_queue.get()
        logger.debug("%s Working on %s", name, url)

        top_words = get_top_words(url, num_top_words)
        client_out_queue.put(top_words)
        client_in_queue.task_done()
        logger.debug("%s Finished %s", name, url)

        global_url_counter += 1
        print("Urls parsed: ", global_url_counter)


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
    logger.info("Started %s workers", num_workers)
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
    logger.debug("Passed commands to _args_parser: %s", commands)
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


def _configure_logger(
    logger: logging.Logger,
    logger_level: int = logging.DEBUG,
    log_file_path: str = "./server.log",
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


def main() -> None:
    _configure_logger(logger, print_stdout=True)

    handler = CustomRequestHandler
    cfg = _args_parser()
    logger.debug("Parsed args: %s", cfg)
    try:
        _serve(handler, handler.mainline_queue, cfg.num_workers, cfg.num_top_words)
    except KeyboardInterrupt:
        print("\nClosing server...", file=sys.stderr)
        sys.exit(128 + SIGINT)
    finally:
        print("Closed!", file=sys.stderr)


if __name__ == "__main__":
    main()
