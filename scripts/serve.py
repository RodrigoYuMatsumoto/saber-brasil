"""Servidor local do Saber Brasil, sem dependências externas."""
from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    quiet = False

    def log_message(self, format, *args):
        if not self.quiet:
            super().log_message(format, *args)

    def do_GET(self):
        if self.path == "/api/health":
            body = json.dumps({"app": "saber-brasil", "version": "3.0.0", "offline": True}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        resolved = Path(self.translate_path(self.path)).resolve()
        if not resolved.is_relative_to(ROOT):
            self.send_error(403)
            return
        return super().do_GET()

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def list_directory(self, path):
        self.send_error(404)
        return None


def main():
    parser = argparse.ArgumentParser(description="Abra o Saber Brasil neste computador.")
    parser.add_argument("--port", type=int, default=8788)
    parser.add_argument("--quiet", action="store_true", help="Suprimir o log de cada solicitação durante os testes.")
    args = parser.parse_args()
    Handler.quiet = args.quiet
    server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=str(ROOT)))
    print(f"Saber Brasil: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
