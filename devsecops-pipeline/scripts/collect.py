#!/usr/bin/env python3
"""Collect every raw scanner report of one run into reports/findings.json.

Usage: collect.py --run-dir reports/<run-id>
The run directory is expected to contain a raw/ subfolder written by the
stage scripts. Which file belongs to which tool is declared in SOURCES.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from normalize import normalize_file, dedupe  # noqa: E402

# filename -> (format, tool, test_class)
SOURCES = {
    "gitleaks.json": ("gitleaks", "gitleaks", "secrets"),
    "gitleaks-history.json": ("gitleaks", "gitleaks-history", "secrets"),
    "gitleaks-workload.json": ("gitleaks", "gitleaks-workload", "secrets"),
    "semgrep.sarif": ("sarif", "semgrep", "sast"),
    "bandit.sarif": ("sarif", "bandit", "sast"),
    "hadolint.sarif": ("sarif", "hadolint", "image"),
    "trivy-fs.json": ("trivy", "trivy-fs", "sca"),
    "trivy-image.json": ("trivy", "trivy-image", "image"),
    "dockle.json": ("dockle", "dockle", "image"),
    "zap.json": ("zap", "owasp-zap", "dast"),
}


def git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--workload", default=os.environ.get("WORKLOAD", "unknown"))
    args = ap.parse_args()

    run_dir = pathlib.Path(args.run_dir)
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    findings: list[dict] = []
    tools_seen: list[str] = []
    for name, (fmt, tool, test_class) in SOURCES.items():
        path = raw_dir / name
        if not path.exists():
            continue
        tools_seen.append(tool)
        findings.extend(normalize_file(path, fmt, tool, test_class))

    findings = dedupe(findings)

    sbom = raw_dir / "sbom.cdx.json"
    components = 0
    if sbom.exists():
        try:
            components = len(json.loads(sbom.read_text()).get("components", []))
        except Exception:
            components = 0

    run = {
        "run_id": run_dir.name,
        "commit_hash": os.environ.get("CI_COMMIT_SHA") or git("rev-parse", "HEAD"),
        "branch": os.environ.get("CI_COMMIT_REF_NAME") or git("rev-parse", "--abbrev-ref", "HEAD"),
        "workload": args.workload,
        "tools": sorted(set(tools_seen)),
        "sbom_components": components,
        "findings": findings,
    }
    out = run_dir / "findings.json"
    out.write_text(json.dumps(run, indent=2))
    print(f"[collect] {len(findings)} findings from {len(set(tools_seen))} tools -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
