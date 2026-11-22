"""Minimal HTTP adapter; the interview work lives in handlers and the client."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit

from handlers import Response, batch_assets, get_asset
from upstream import AssetClient


client = AssetClient()


class Handler(BaseHTTPRequestHandler):
    def send_json(self, response):
        data = json.dumps(response.body).encode("utf-8")
        self.send_response(response.status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path.startswith("/assets/") and len(path.split("/")) == 3:
            self.send_json(get_asset(unquote(path.split("/")[2]), client))
        else:
            self.send_json(Response(404, {"error": "Unknown route"}))

    def do_POST(self):
        if urlsplit(self.path).path != "/assets/batch":
            self.send_json(Response(404, {"error": "Unknown route"}))
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 16384:
                raise ValueError("Invalid body length")
            body = json.loads(self.rfile.read(length))
        except (ValueError, UnicodeDecodeError):
            self.send_json(Response(400, {"error": "Expected a JSON body under 16 KiB"}))
            return
        try:
            response = batch_assets(body, client)
        except NotImplementedError as exc:
            response = Response(501, {"error": str(exc)})
        self.send_json(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print("Asset service: http://127.0.0.1:%d (Ctrl-C to stop)" % server.server_port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
