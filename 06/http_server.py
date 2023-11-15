import json
import sys
from ast import literal_eval
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from queue import Queue
from typing import Any
from urllib.parse import parse_qs

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa
else:
    ic.configureOutput(includeContext=True)

ADDR = ""
PORT = 8087

main_queue = Queue()


class CustomRequestHandler(BaseHTTPRequestHandler):
    def _proccess_query(self) -> dict[str, Any] | None:
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
        query = self._proccess_query()
        if query:
            ic(query)
            client_queue = Queue()
            for url in query.get("query-url", ()):
                main_queue.put((client_queue, url))
        # ? END Parse request

        # ? Send reply
        json_str = json.dumps({"test": 10, "hi": "you"})
        self.wfile.write(json_str.encode(encoding="utf-8"))
        # ? END Send reply


if __name__ == "__main__":
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
