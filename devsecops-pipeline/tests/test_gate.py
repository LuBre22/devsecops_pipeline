"""Unit tests for the pipeline logic.

These tests run without any container runtime, which makes them the fastest
feedback loop during development:  make test
"""
import json
import pathlib
import subprocess
import sys
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from normalize import dedupe, normalize_file  # noqa: E402

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def run_gate(findings_path: pathlib.Path):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "gate.py"),
         "--findings", str(findings_path),
         "--policy", str(ROOT / "policy" / "thresholds.yaml"),
         "--suppressions", str(ROOT / "policy" / "suppressions.json")],
        capture_output=True, text=True,
    )


def write_run(tmp_path, findings):
    path = tmp_path / "findings.json"
    path.write_text(json.dumps({"run_id": "test", "workload": "unit",
                                "tools": ["unit"], "findings": findings,
                                "scan_status": {"unit": {"status": "ok"}}}))
    return path


def finding(**kw):
    base = {"id": "x", "tool": "unit", "test_class": "sast", "severity": "HIGH",
            "rule_id": "r", "title": "t", "location": "l", "cve_id": "",
            "remediation": "", "false_positive": False}
    base.update(kw)
    return base


def test_gate_passes_without_findings(tmp_path):
    assert run_gate(write_run(tmp_path, [])).returncode == 0


def test_high_sast_finding_blocks(tmp_path):
    result = run_gate(write_run(tmp_path, [finding(severity="HIGH", test_class="sast")]))
    assert result.returncode == 1
    assert "GATE FAILED" in result.stdout


def test_high_sca_finding_only_warns(tmp_path):
    # Policy decision: an unreachable dependency CVE must not break the build.
    result = run_gate(write_run(tmp_path, [finding(severity="HIGH", test_class="sca")]))
    assert result.returncode == 0
    assert "warnings: 1" in result.stdout


def test_any_secret_blocks(tmp_path):
    result = run_gate(write_run(tmp_path, [finding(severity="INFO", test_class="secrets")]))
    assert result.returncode == 1


def test_dast_never_blocks(tmp_path):
    result = run_gate(write_run(tmp_path, [finding(severity="CRITICAL", test_class="dast")]))
    assert result.returncode == 0


def test_false_positive_is_ignored(tmp_path):
    result = run_gate(write_run(tmp_path, [finding(test_class="secrets", false_positive=True)]))
    assert result.returncode == 0


def test_sarif_normalisation():
    findings = normalize_file(FIXTURES / "semgrep.sarif", "sarif", "semgrep", "sast")
    assert findings, "expected at least one finding from the SARIF fixture"
    assert findings[0]["test_class"] == "sast"
    assert findings[0]["severity"] in ("HIGH", "MEDIUM", "LOW", "INFO", "CRITICAL")


def test_trivy_normalisation_maps_severity():
    findings = normalize_file(FIXTURES / "trivy-fs.json", "trivy", "trivy-fs", "sca")
    assert any(f["severity"] == "CRITICAL" for f in findings)
    assert all(f["cve_id"].startswith("CVE-") for f in findings)


def test_gitleaks_findings_are_always_critical():
    findings = normalize_file(FIXTURES / "gitleaks.json", "gitleaks", "gitleaks", "secrets")
    assert findings and all(f["severity"] == "CRITICAL" for f in findings)


def test_dedupe_keeps_highest_severity():
    merged = dedupe([finding(id="same", severity="LOW"), finding(id="same", severity="CRITICAL")])
    assert len(merged) == 1 and merged[0]["severity"] == "CRITICAL"


def test_missing_report_is_rejected(tmp_path):
    with pytest.raises(ValueError, match='missing or empty'):
        normalize_file(tmp_path / "nope.sarif", "sarif", "semgrep", "sast")
