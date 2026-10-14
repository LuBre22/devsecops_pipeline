"""Status service - workload 3 (fixed variant).

Remediations:
  - every secret is read from the environment at runtime, injected by Vault
    or a CI variable, never committed                        (CWE-798)
  - the file endpoint resolves and confines the path          (CWE-22)
  - unknown routes return a plain 404 without a stack trace
"""
import http.server
import json
import os
import pathlib
import socketserver
from urllib.parse import parse_qs, urlparse

# FIX: secrets come from the environment. The process fails fast if the
# deployment forgot to inject them, instead of falling back to a default.
API_TOKEN = os.environ.get("API_TOKEN")
DATA_ROOT = pathlib.Path(os.environ.get("DATA_ROOT", "/app/data")).resolve()


class Handler(http.server.BaseHTTPRequestHandler):
    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802 - stdlib naming
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._json(200, {"status": "ok"})
            return
        if parsed.path == "/file":
            name = (parse_qs(parsed.query).get("name") or [""])[0]
            target = (DATA_ROOT / name).resolve()
            # FIX: confine the resolved path to the data directory.
            if not target.is_relative_to(DATA_ROOT) or not target.is_file():
                self._json(404, {"error": "file not found"})
                return
            self._json(200, {"name": target.name, "size": target.stat().st_size})
            return
        self._json(404, {"error": "unknown route"})

    def log_message(self, fmt, *args):  # keep access logs structured and quiet
        print(json.dumps({"client": self.address_string(), "msg": fmt % args}))


if __name__ == "__main__":
    if not API_TOKEN:
        raise SystemExit("API_TOKEN is not set - inject it from Vault or a CI variable")
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    port = int(os.environ.get("PORT", "8080"))
    with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
        httpd.serve_forever()
