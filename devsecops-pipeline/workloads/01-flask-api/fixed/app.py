"""Hardened demo API - workload 1 (fixed variant).

Identical behaviour to the vulnerable variant, every finding remediated:
  - parameterised SQL statements              (CWE-89)
  - explicit output escaping                  (CWE-79)
  - no shell call, IP address allow-list      (CWE-78)
  - SHA-256 instead of MD5                    (CWE-327)
  - debug disabled, security headers applied  (CWE-489, CWE-693)
"""
import hashlib
import ipaddress
import os
import sqlite3
import subprocess

from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)
DB = os.environ.get("DB_PATH", "/tmp/demo.db")


def init_db() -> None:
    with sqlite3.connect(DB) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, role TEXT)")
        conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'alice', 'admin')")


@app.after_request
def security_headers(response):
    # Secure by default: restrictive headers on every response.
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/user")
def get_user():
    # FIX: bound parameter, the driver handles quoting.
    name = request.args.get("name", "")[:64]
    with sqlite3.connect(DB) as conn:
        rows = conn.execute(
            "SELECT id, name, role FROM users WHERE name = ?", (name,)
        ).fetchall()
    return {"rows": rows}


@app.route("/greet")
def greet():
    # FIX: escape untrusted input before it reaches the response body.
    name = escape(request.args.get("name", "world")[:64])
    return f"<h1>Hello {name}</h1>"


@app.route("/ping")
def ping():
    # FIX: validate as an IP address, then exec without a shell.
    host = request.args.get("host", "127.0.0.1")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return {"error": "host must be a valid IP address"}, 400
    subprocess.run(["ping", "-c", "1", host], check=False, timeout=5, shell=False)
    return {"pinged": host}


@app.route("/hash")
def strong_hash():
    # FIX: SHA-256 instead of MD5.
    value = request.args.get("value", "")
    return {"sha256": hashlib.sha256(value.encode()).hexdigest()}


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080, debug=False)
