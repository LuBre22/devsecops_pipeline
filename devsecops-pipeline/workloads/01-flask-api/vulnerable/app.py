"""Deliberately vulnerable demo API - workload 1 (vulnerable variant).

DO NOT COPY THIS CODE. Every defect below is intentional and exists to prove
that the pipeline actually detects something. Expected findings:
  - SQL injection via string concatenation  -> Semgrep, Bandit
  - debug mode enabled in a container       -> Semgrep, Bandit
  - command injection through a shell call  -> Semgrep, Bandit
  - broken hash function (MD5)              -> Bandit
  - reflected XSS (unescaped output)        -> Semgrep, ZAP
  - missing security headers                -> ZAP
"""
import hashlib
import os
import sqlite3

from flask import Flask, request

app = Flask(__name__)
DB = "/tmp/demo.db"


def init_db() -> None:
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT, role TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'alice', 'admin')")
    conn.commit()
    conn.close()


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/user")
def get_user():
    # VULNERABILITY: untrusted input concatenated into SQL (CWE-89).
    name = request.args.get("name", "")
    conn = sqlite3.connect(DB)
    query = "SELECT id, name, role FROM users WHERE name = '" + name + "'"
    rows = conn.execute(query).fetchall()
    conn.close()
    return {"query": query, "rows": rows}


@app.route("/greet")
def greet():
    # VULNERABILITY: reflected cross-site scripting (CWE-79).
    name = request.args.get("name", "world")
    return f"<h1>Hello {name}</h1>"


@app.route("/ping")
def ping():
    # VULNERABILITY: OS command injection through a shell call (CWE-78).
    host = request.args.get("host", "127.0.0.1")
    os.system("ping -c 1 " + host)
    return {"pinged": host}


@app.route("/hash")
def weak_hash():
    # VULNERABILITY: broken cryptographic hash (CWE-327).
    value = request.args.get("value", "")
    return {"md5": hashlib.md5(value.encode()).hexdigest()}


if __name__ == "__main__":
    init_db()
    # VULNERABILITY: debugger exposed, binds to every interface (CWE-489).
    app.run(host="0.0.0.0", port=8080, debug=True)
