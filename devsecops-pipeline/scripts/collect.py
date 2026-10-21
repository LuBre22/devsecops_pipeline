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
from normalize import normalize_file, dedupe, validate_report  # noqa: E402

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
    manifest = run_dir / 'run.json'
    metadata = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else {}
    statuses = metadata.get('checks', {})
    errors = []
    required = {'gitleaks.json', 'semgrep.sarif', 'bandit.sarif', 'trivy-fs.json', 'sbom.cdx.json'}
    if not statuses:
        errors.append('Missing run manifest with scanner execution status')
    for name in required:
        matching = [s for s in statuses.values() if s.get('report') == name]
        if not matching or matching[0].get('status') != 'ok':
            errors.append(f'Required scan not successful: {name}')

    findings: list[dict] = []
    tools_seen: list[str] = []
    for name, (fmt, tool, test_class) in SOURCES.items():
        path = raw_dir / name
        if not path.exists():
            continue
        try:
            findings.extend(normalize_file(path, fmt, tool, test_class))
            tools_seen.append(tool)
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            errors.append(f'{name}: {exc}')
    for tool, state in statuses.items():
        if state.get('report') and state.get('status') == 'ok' and not (raw_dir / state['report']).is_file():
            errors.append(f'{tool}: successful check has no report')

    findings = dedupe(findings)

    sbom = raw_dir / "sbom.cdx.json"
    components = 0
    if sbom.exists():
        try:
            doc = json.loads(sbom.read_text(encoding='utf-8'))
            validate_report(doc, 'sbom')
            components = len(doc.get("components", []))
            tools_seen.append('syft')
        except (ValueError, TypeError, KeyError) as exc:
            errors.append(f'sbom: {exc}')

    run = {
        "run_id": run_dir.name,
        "commit_hash": os.environ.get("CI_COMMIT_SHA") or git("rev-parse", "HEAD"),
        "branch": os.environ.get("CI_COMMIT_REF_NAME") or git("rev-parse", "--abbrev-ref", "HEAD"),
        "workload": args.workload,
        "tools": sorted(set(tools_seen)),
        "sbom_components": components,
        "findings": findings,
        "scan_status": statuses,
        "scan_errors": sorted(set(errors)),
        "started_at": metadata.get('started_at'),
        "images": metadata.get('images', {}),
        "resolved_images": metadata.get('resolved_images', {}),
        "base_image": metadata.get('base_image'),
        "source_digest": metadata.get('source_digest'),
        "pipeline_source_digest": metadata.get('pipeline_source_digest'),
        "offline": metadata.get('offline', False),
    }
    out = run_dir / "findings.json"
    out.write_text(json.dumps(run, indent=2), encoding='utf-8')
    print(f"[collect] {len(findings)} findings from {len(set(tools_seen))} tools -> {out}")
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
