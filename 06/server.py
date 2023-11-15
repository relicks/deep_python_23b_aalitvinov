import json
import sys
import threading
from ast import literal_eval
from collections import Counter, OrderedDict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from queue import Queue
from typing import Any
from urllib.error import URLError
from urllib.parse import parse_qs
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

main_queue: Queue[
    tuple[Queue[str], Queue[dict[str, dict[str, int]] | dict[str, None]]]
] = Queue()


class CustomRequestHandler(BaseHTTPRequestHandler):
    def _parse_query(self) -> dict[str, Any] | None:
        c_len = self.headers["Content-Length"]
        content_length = int(c_len) if c_len.isdecimal() else 0  # parsing
        if content_length:
            request_data = self.rfile.read(content_length)
            return {
                k: literal_eval(v[0])
                for k, v in parse_qs(request_data.decode()).items()
            }
        return None

    def do_POST(self):  # noqa: N802
        # ? Response head
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        # ? END Response head

        # ? Parse request
        # Getting the length of the data payload in bytes
        query = self._parse_query()
        out_dict = {}
        if query:
            ic(query)
            client_in_queue = Queue()
            client_out_queue = Queue()
            for url in query.get("query-url", ()):
                client_in_queue.put(url)
                main_queue.put((client_in_queue, client_out_queue))
            ic(threading.current_thread().name)
            client_in_queue.join()  # Waiting for url proccessing by workers
            # ic(client_out_queue.queue)
            for url_result in client_out_queue.queue:
                out_dict.update(url_result)
        # ? END Parse request

        # ? Send reply
        json_str = json.dumps(out_dict)
        self.wfile.write(json_str.encode(encoding="utf-8"))
        # ? END Send reply


def get_words_from_url(url: str) -> list[str] | None:
    try:
        resp = urlopen(url, timeout=5.0)
    except URLError:
        return None
    else:
        if resp.code == HTTPStatus.OK:
            return parse_html(resp.read().decode())


def get_top_words(url: str, n_top: int) -> dict[str, dict[str, int]] | dict[str, None]:
    words = get_words_from_url(url)
    if words:
        count = Counter(words)
        return {url: OrderedDict(count.most_common()[:n_top])}
    return {url: None}


def worker() -> None:
    while True:
        name = threading.current_thread().name
        client_in_queue, client_out_queue = main_queue.get()

        url = client_in_queue.get()
        print(f"{name} Working on {url}", file=sys.stderr)
        top_words = get_top_words(url, N_TOP_WORDS)
        client_out_queue.put(top_words)
        client_in_queue.task_done()
        print(f"{name} Finished {url}", file=sys.stderr)


if __name__ == "__main__":
    workers = [
        threading.Thread(target=worker, name=f"worker {i}", daemon=True)
        for i in range(N_WORKERS)
    ]
    for thread in workers:
        thread.start()
    print(f"Started {N_WORKERS} workers.")

    with ThreadingHTTPServer((ADDR, PORT), CustomRequestHandler) as httpd:
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
