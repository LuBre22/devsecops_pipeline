"""Report generator CLI - workload 2 (vulnerable variant).

The point of this workload is the dependency tree, not the code: an outdated
PyYAML and urllib3 are exploitable even when the application code is clean.
Additional intentional code defects:
  - yaml.load without a safe loader  (CWE-502, arbitrary object construction)
  - TLS verification disabled        (CWE-295)
  - insecure temporary file          (CWE-377)
"""
import argparse
import tempfile

import requests
import yaml


def load_config(path: str) -> dict:
    # VULNERABILITY: unsafe deserialisation of untrusted YAML (CWE-502).
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.load(fh.read())


def fetch(url: str) -> str:
    # VULNERABILITY: certificate validation disabled (CWE-295).
    return requests.get(url, verify=False, timeout=10).text


def cache(payload: str) -> str:
    # VULNERABILITY: predictable temp file name (CWE-377).
    path = tempfile.mktemp(suffix=".cache")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(payload)
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description="generate a report from a config")
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args()
    cfg = load_config(args.config)
    print(f"loaded {len(cfg)} config key(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
