import json
import sys
import threading
from collections import Counter, OrderedDict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from queue import Queue
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

N_TOP_WORDS = 5
N_WORKERS = 6

ADDR = ""
PORT = 8087

InQueue: TypeAlias = Queue[str]
OutQueue: TypeAlias = Queue[dict[str, dict[str, int]] | dict[str, None]]
PrimeQueue: TypeAlias = Queue[tuple[InQueue, OutQueue]]

JsonTypes: TypeAlias = str | int | float | bool | None


def get_words_from_url(url: str) -> list[str] | None:
    try:
        resp = urlopen(url, timeout=5.0)
    except URLError:
        return None
    else:
        if resp.code == HTTPStatus.OK:
            result = parse_html(resp.read().decode())
            resp.close()
            return result


def get_top_words(url: str, n_top: int) -> dict[str, dict[str, int]] | dict[str, None]:
    words = get_words_from_url(url)
    if words:
        count = Counter(words)
        return {url: OrderedDict(count.most_common()[:n_top])}
    return {url: None}


class CustomRequestHandler(BaseHTTPRequestHandler):
    mainline_queue: PrimeQueue = Queue()

    def _parse_query(self) -> dict[str, JsonTypes] | None:
        c_len = self.headers["Content-Length"]
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
        for url in query.get(url_field_name, ()):
            client_in_queue.put(url)
            type(self).mainline_queue.put((client_in_queue, client_out_queue))
        client_in_queue.join()  # Waiting for url proccessing by workers
        for url_result in client_out_queue.queue:
            out_dict.update(url_result)
        return {url_field_name: out_dict}

    def do_POST(self):  # noqa: N802
        query = self._parse_query()  # ? Parse request
        ic(query)
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
            self.wfile.write(json_str.encode(encoding="utf-8"))
            # ? END Send reply


def worker(prime_queue) -> None:
    while True:
        name = threading.current_thread().name
        client_in_queue, client_out_queue = prime_queue.get()

        url = client_in_queue.get()
        print(f"{name} Working on {url}", file=sys.stderr)
        top_words = get_top_words(url, N_TOP_WORDS)
        client_out_queue.put(top_words)
        client_in_queue.task_done()
        print(f"{name} Finished {url}", file=sys.stderr)


if __name__ == "__main__":
    current_handler = CustomRequestHandler
    workers = [
        threading.Thread(
            target=worker,
            args=(current_handler.mainline_queue,),
            name=f"worker {i}",
            daemon=True,
        )
        for i in range(N_WORKERS)
    ]
    for thread in workers:
        thread.start()
    print(f"Started {N_WORKERS} workers.")

    with ThreadingHTTPServer((ADDR, PORT), current_handler) as httpd:
        print(
            f"serving at {httpd.server_address} port {httpd.server_port}",
            file=sys.stderr,
        )
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nClosing server...", file=sys.stderr)
        finally:
            httpd.server_close()
            print("Closed!", file=sys.stderr)
            sys.exit(0)
