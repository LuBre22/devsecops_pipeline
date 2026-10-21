#!/usr/bin/env python3
"""Normalise heterogeneous scanner output into the common Finding model.

Implements the class model from the architecture plan (section 5.1). Every
scanner writes a raw report into reports/raw/; this module converts each one
into a list of Finding dicts so that the gate and the report stay independent
of the concrete tool (NF-05).

Supported input formats:
  sarif            Semgrep, Bandit (via --format sarif), hadolint-sarif
  gitleaks         Gitleaks JSON array
  trivy            Trivy JSON (fs and image mode)
  zap              OWASP ZAP baseline JSON report
  dockle           Dockle JSON
  syft             CycloneDX/Syft JSON (inventory only, never a finding)
"""
from __future__ import annotations

import json
import pathlib
import sys
from typing import Any, Iterable
from urllib.parse import urljoin

# Canonical severity ladder used across all tools.
SEVERITY_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]

# Per-tool severity vocabulary mapped onto the canonical ladder.
SEVERITY_MAP = {
    # SARIF levels
    "error": "HIGH", "warning": "MEDIUM", "note": "LOW", "none": "INFO",
    # Semgrep native
    "ERROR": "HIGH", "WARNING": "MEDIUM", "INFO": "INFO",
    # Trivy / Dockle / generic CVSS buckets
    "CRITICAL": "CRITICAL", "HIGH": "HIGH", "MEDIUM": "MEDIUM",
    "LOW": "LOW", "UNKNOWN": "INFO", "NEGLIGIBLE": "INFO",
    "FATAL": "CRITICAL", "WARN": "MEDIUM", "PASS": "INFO", "SKIP": "INFO",
    # ZAP risk codes: 3=High 2=Medium 1=Low 0=Informational
    "3": "HIGH", "2": "MEDIUM", "1": "LOW", "0": "INFO",
}


def _sev(raw: Any, default: str = "MEDIUM") -> str:
    if raw is None:
        return default
    key = str(raw).strip()
    return SEVERITY_MAP.get(key, SEVERITY_MAP.get(key.upper(), default))


def _finding(**kw: Any) -> dict:
    """Build a Finding with every field of the model present."""
    base = {
        "id": "",
        "tool": "",
        "test_class": "",
        "severity": "MEDIUM",
        "rule_id": "",
        "title": "",
        "location": "",
        "cve_id": "",
        "remediation": "",
        "false_positive": False,
    }
    base.update(kw)
    return base


# --------------------------------------------------------------------------
# Per-format parsers
# --------------------------------------------------------------------------
def parse_sarif(doc: dict, tool: str, test_class: str) -> list[dict]:
    out: list[dict] = []
    for run in doc.get("runs", []):
        driver = run.get("tool", {}).get("driver", {})
        tool_name = driver.get("name", tool)
        # Rule-level defaults, because Semgrep puts the severity on the rule.
        rule_levels = {
            r.get("id"): (r.get("defaultConfiguration") or {}).get("level")
            for r in driver.get("rules", [])
        }
        for res in run.get("results", []):
            rule_id = res.get("ruleId", "")
            level = res.get("level") or rule_levels.get(rule_id) or "warning"
            loc = ""
            locations = res.get("locations") or []
            if locations:
                phys = locations[0].get("physicalLocation", {})
                art = phys.get("artifactLocation", {}).get("uri", "")
                line = (phys.get("region") or {}).get("startLine", "")
                loc = f"{art}:{line}" if line else art
            out.append(_finding(
                id=f"{tool_name}:{rule_id}:{loc}",
                tool=tool_name,
                test_class=test_class,
                severity=_sev(level),
                rule_id=rule_id,
                title=(res.get("message") or {}).get("text", "")[:300],
                location=loc,
                remediation="See rule documentation",
            ))
    return out


def parse_gitleaks(doc: Any, tool: str = "gitleaks") -> list[dict]:
    # Gitleaks emits a JSON array; any hit is treated as CRITICAL by policy.
    items: Iterable[dict] = doc if isinstance(doc, list) else doc.get("findings", [])
    out = []
    for it in items:
        loc = f"{it.get('File', '')}:{it.get('StartLine', '')}"
        out.append(_finding(
            id=f"gitleaks:{it.get('RuleID', '')}:{loc}:{it.get('Commit', '')[:8]}",
            tool=tool,
            test_class="secrets",
            severity="CRITICAL",
            rule_id=it.get("RuleID", ""),
            title=it.get("Description", "Hardcoded secret"),
            location=loc,
            remediation="Rotate the credential and move it into Vault or a CI variable",
        ))
    return out


def parse_trivy(doc: dict, tool: str, test_class: str) -> list[dict]:
    out = []
    for result in doc.get("Results") or []:
        target = result.get("Target", "")
        for v in result.get("Vulnerabilities") or []:
            fixed = v.get("FixedVersion", "")
            out.append(_finding(
                id=f"trivy:{v.get('VulnerabilityID')}:{v.get('PkgName')}:{v.get('InstalledVersion')}",
                tool=tool,
                test_class=test_class,
                severity=_sev(v.get("Severity")),
                rule_id=v.get("VulnerabilityID", ""),
                cve_id=v.get("VulnerabilityID", ""),
                title=f"{v.get('PkgName')} {v.get('InstalledVersion')}: {v.get('Title', '')}"[:300],
                location=f"{target} -> {v.get('PkgName')}",
                remediation=(f"Upgrade to {fixed}" if fixed else "No fix available yet"),
            ))
        # Misconfigurations (Dockerfile / IaC checks in Trivy config mode)
        for m in result.get("Misconfigurations") or []:
            out.append(_finding(
                id=f"trivy-misconf:{m.get('ID')}:{target}",
                tool=tool,
                test_class=test_class,
                severity=_sev(m.get("Severity")),
                rule_id=m.get("ID", ""),
                title=m.get("Title", ""),
                location=target,
                remediation=m.get("Resolution", ""),
            ))
        # Verified secrets found inside an image layer
        for s in result.get("Secrets") or []:
            out.append(_finding(
                id=f"trivy-secret:{s.get('RuleID')}:{target}:{s.get('StartLine')}",
                tool=tool,
                test_class="secrets",
                severity="CRITICAL",
                rule_id=s.get("RuleID", ""),
                title=s.get("Title", "Secret in image layer"),
                location=f"{target}:{s.get('StartLine', '')}",
                remediation="Remove the secret from the image and rotate it",
            ))
    return out


def parse_zap(doc: dict, tool: str = "owasp-zap") -> list[dict]:
    out = []
    for site in doc.get("site") or []:
        host = site.get("@name", "")
        for alert in site.get("alerts") or []:
            inst = (alert.get("instances") or [{}])[0]
            out.append(_finding(
                id=f"zap:{alert.get('pluginid')}:{alert.get('name')}",
                tool=tool,
                test_class="dast",
                severity=_sev(alert.get("riskcode")),
                rule_id=str(alert.get("pluginid", "")),
                cve_id=(alert.get("cweid") and f"CWE-{alert['cweid']}") or "",
                title=alert.get("name", ""),
                location=urljoin(host.rstrip('/') + '/', inst.get('uri', '')),
                remediation=(alert.get("solution") or "")[:300],
            ))
    return out


def parse_dockle(doc: dict, tool: str = "dockle") -> list[dict]:
    out = []
    for d in doc.get("details") or []:
        level = d.get("level", "INFO")
        if level in ("PASS", "SKIP", "IGNORE"):
            continue
        out.append(_finding(
            id=f"dockle:{d.get('code')}",
            tool=tool,
            test_class="image",
            severity=_sev(level),
            rule_id=d.get("code", ""),
            title=d.get("title", ""),
            location="image",
            remediation="; ".join(d.get("alerts") or [])[:300],
            evidence="; ".join(d.get("alerts") or []),
        ))
    return out


PARSERS = {
    "sarif": parse_sarif,
    "gitleaks": parse_gitleaks,
    "trivy": parse_trivy,
    "zap": parse_zap,
    "dockle": parse_dockle,
}


def validate_report(doc: Any, fmt: str) -> None:
    """Distinguish an actual empty result from a failed/truncated scanner."""
    if fmt == 'gitleaks':
        valid = isinstance(doc, list) and all(isinstance(x, dict) and 'RuleID' in x for x in doc)
    elif not isinstance(doc, dict):
        valid = False
    elif fmt == 'sarif':
        valid = isinstance(doc.get('runs'), list) and bool(doc['runs'])
        if valid:
            valid = all(isinstance(r.get('results'), list) and
                        all(i.get('executionSuccessful', True) for i in r.get('invocations', []))
                        for r in doc['runs'])
    elif fmt == 'trivy':
        valid = doc.get('SchemaVersion') == 2 and 'ArtifactName' in doc
    elif fmt == 'dockle':
        valid = isinstance(doc.get('details'), list) and isinstance(doc.get('summary'), dict)
    elif fmt == 'zap':
        valid = isinstance(doc.get('site'), list) and bool(doc['site'])
    elif fmt == 'sbom':
        valid = doc.get('bomFormat') == 'CycloneDX' and isinstance(doc.get('components', []), list)
    else:
        valid = False
    if not valid:
        raise ValueError(f'invalid or unsuccessful {fmt} report')


def normalize_file(path: pathlib.Path, fmt: str, tool: str, test_class: str) -> list[dict]:
    """A report is evidence: missing, broken or unsuccessful output is an error."""
    if not path.exists() or path.stat().st_size == 0:
        raise ValueError(f'missing or empty report: {path}')
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f'invalid JSON report: {path}') from exc
    validate_report(doc, fmt)
    parser = PARSERS[fmt]
    if fmt == "gitleaks":
        return parser(doc, tool)
    if fmt in ("zap", "dockle"):
        return parser(doc, tool)
    return parser(doc, tool, test_class)


def dedupe(findings: list[dict]) -> list[dict]:
    """Deduplicate on the finding id, keeping the highest severity."""
    best: dict[tuple[str, str], dict] = {}
    for f in findings:
        key = (f['id'], f['test_class'])
        prev = best.get(key)
        if prev is None or SEVERITY_ORDER.index(f["severity"]) > SEVERITY_ORDER.index(prev["severity"]):
            best[key] = f
    return sorted(
        best.values(),
        key=lambda f: (-SEVERITY_ORDER.index(f["severity"]), f["tool"], f["rule_id"]),
    )
