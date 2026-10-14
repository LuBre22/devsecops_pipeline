#!/usr/bin/env python3
"""Import raw scanner reports into OWASP DefectDojo (central defect management).

Optional stage: runs only when DEFECTDOJO_URL and DEFECTDOJO_TOKEN are set.
Uses the stdlib only, so no extra dependency enters the pipeline image.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
import os
import pathlib
import urllib.request
import uuid

# raw report file -> DefectDojo scan type identifier
SCAN_TYPES = {
    "gitleaks.json": "Gitleaks Scan",
    "semgrep.sarif": "SARIF",
    "bandit.sarif": "SARIF",
    "hadolint.sarif": "SARIF",
    "trivy-fs.json": "Trivy Scan",
    "trivy-image.json": "Trivy Scan",
    "dockle.json": "SARIF",
    "zap.json": "ZAP Scan",
}


def post_multipart(url: str, token: str, fields: dict, file_path: pathlib.Path, scan_type: str) -> int:
    boundary = uuid.uuid4().hex
    body = bytearray()

    def add_field(name: str, value: str) -> None:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.extend(f"{value}\r\n".encode())

    for key, value in {**fields, "scan_type": scan_type}.items():
        add_field(key, str(value))

    body.extend(f"--{boundary}\r\n".encode())
    body.extend(
        f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n".encode()
    )
    body.extend(file_path.read_bytes())
    body.extend(f"\r\n--{boundary}--\r\n".encode())

    req = urllib.request.Request(
        url,
        data=bytes(body),
        method="POST",
        headers={
            "Authorization": f"Token {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()

    base = os.environ.get("DEFECTDOJO_URL", "").rstrip("/")
    token = os.environ.get("DEFECTDOJO_TOKEN", "")
    engagement = os.environ.get("DEFECTDOJO_ENGAGEMENT", "1")
    if not base or not token:
        print("[defectdojo] URL or token missing, skipping import")
        return 0

    run_dir = pathlib.Path(args.run_dir)
    run = json.loads((run_dir / "findings.json").read_text())
    url = f"{base}/api/v2/import-scan/"
    fields = {
        "engagement": engagement,
        "active": "true",
        "verified": "false",
        "close_old_findings": "false",
        "scan_date": datetime.strptime(run["run_id"][:8], "%Y%m%d").date().isoformat(),
        "version": (run.get("commit_hash") or "")[:12],
        "test_title": f"{run.get('workload')} / {run['run_id']}",
    }

    imported = 0
    for name, scan_type in SCAN_TYPES.items():
        path = run_dir / "raw" / name
        if not path.exists() or path.stat().st_size == 0:
            continue
        try:
            status = post_multipart(url, token, fields, path, scan_type)
            print(f"[defectdojo] {name} -> HTTP {status}")
            imported += 1
        except Exception as exc:  # noqa: BLE001 - import must never break the run
            print(f"[defectdojo] WARN import of {name} failed: {exc}")
    print(f"[defectdojo] imported {imported} report(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
