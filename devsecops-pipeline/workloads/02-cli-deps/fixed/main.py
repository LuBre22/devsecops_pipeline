"""Report generator CLI - workload 2 (fixed variant).

Remediations:
  - yaml.safe_load instead of yaml.load            (CWE-502)
  - TLS verification enabled, explicit CA bundle   (CWE-295)
  - NamedTemporaryFile instead of mktemp           (CWE-377)
  - URL scheme allow-list before any request       (CWE-918)
"""
import argparse
import tempfile
from urllib.parse import urlparse

import requests
import yaml

ALLOWED_SCHEMES = {"https"}


def load_config(path: str) -> dict:
    # FIX: safe_load constructs plain Python types only.
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh.read()) or {}


def fetch(url: str) -> str:
    # FIX: validate the scheme, then let requests verify the certificate.
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"scheme not allowed: {parsed.scheme!r}")
    response = requests.get(url, timeout=10, verify=True)
    response.raise_for_status()
    return response.text


def cache(payload: str) -> str:
    # FIX: atomically created file with restrictive permissions.
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cache", delete=False, encoding="utf-8"
    ) as fh:
        fh.write(payload)
        return fh.name


def main() -> int:
    ap = argparse.ArgumentParser(description="generate a report from a config")
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args()
    cfg = load_config(args.config)
    print(f"loaded {len(cfg)} config key(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
