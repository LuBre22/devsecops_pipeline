"""Status service - workload 3 (vulnerable variant).

This workload targets the secret and container stages:
  - hardcoded API token and database password  -> Gitleaks, Trivy secret scan
  - private key committed to the repository    -> Gitleaks
  - path traversal in a file endpoint          -> Semgrep
"""
import http.server
import json
import os
import socketserver

# VULNERABILITY: hardcoded credentials in source (CWE-798).
API_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyzAB"
DB_PASSWORD = "Sup3rS3cret-Pr0d-Password!"
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 - stdlib naming
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            return
        if self.path.startswith("/file?"):
            # VULNERABILITY: path traversal, no normalisation (CWE-22).
            name = self.path.split("=", 1)[1]
            with open("/app/data/" + name, "rb") as fh:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(fh.read())
            return
        self.send_response(404)
        self.end_headers()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
        httpd.serve_forever()
