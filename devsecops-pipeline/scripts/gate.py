#!/usr/bin/env python3
"""Security gate: evaluate findings.json against policy/thresholds.yaml.

Exit codes
  0  gate passed (no blocking finding)
  1  gate failed (at least one blocking finding)
  2  configuration or input error

The policy is data, not code, so a change of the risk appetite never requires
a change to the pipeline (Policy as Code, architecture plan section 4.2).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import date

SEVERITY_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
ACTIONS = ("block", "warn", "info")


def load_yaml(path: pathlib.Path) -> dict:
    try:
        import yaml  # type: ignore
        return yaml.safe_load(path.read_text())
    except ModuleNotFoundError:
        return minimal_yaml(path.read_text())


def minimal_yaml(text: str) -> dict:
    """Tiny two-level YAML reader so the gate also runs without PyYAML.

    Supports exactly the shape of policy/thresholds.yaml: nested mappings of
    scalars, two spaces per level.
    """
    root: dict = {}
    stack = [(-1, root)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        key, _, value = raw.strip().partition(":")
        value = value.strip().strip('"').strip("'")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value == "":
            node: dict = {}
            parent[key] = node
            stack.append((indent, node))
        else:
            if value.lower() in ("true", "false"):
                parent[key] = value.lower() == "true"
            elif value.isdigit():
                parent[key] = int(value)
            else:
                parent[key] = value
    return root


def load_suppressions(path: pathlib.Path) -> dict[str, dict]:
    """Suppressions expire; an expired entry is reported but no longer honoured."""
    if not path.exists():
        return {}
    doc = json.loads(path.read_text())
    active = {}
    today = date.today()
    for entry in doc.get("suppressions", []):
        expires = entry.get("expires_at")
        if expires and date.fromisoformat(expires) < today:
            print(f"[gate] suppression expired, re-enabled: {entry.get('finding_id')}")
            continue
        if not entry.get("justification") or not entry.get("owner"):
            print(f"[gate] suppression ignored, missing justification/owner: {entry.get('finding_id')}")
            continue
        active[entry["finding_id"]] = entry
    return active


def action_for(policy: dict, test_class: str, severity: str) -> str:
    """Resolve the policy action for one (test class, severity) pair."""
    gates = policy.get("gates", {})
    rules = gates.get(test_class) or gates.get("default") or {}
    action = rules.get(severity)
    if action is None:
        # Fall back to the next lower severity that is defined.
        idx = SEVERITY_ORDER.index(severity)
        for lower in reversed(SEVERITY_ORDER[:idx]):
            if lower in rules:
                action = rules[lower]
                break
    action = (action or "info").lower()
    return action if action in ACTIONS else "info"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", required=True)
    ap.add_argument("--policy", default="policy/thresholds.yaml")
    ap.add_argument("--suppressions", default="policy/suppressions.json")
    ap.add_argument("--out", default=None, help="write gate result JSON here")
    args = ap.parse_args()

    findings_path = pathlib.Path(args.findings)
    if not findings_path.exists():
        print(f"[gate] ERROR findings file not found: {findings_path}", file=sys.stderr)
        return 2

    run = json.loads(findings_path.read_text())
    policy = load_yaml(pathlib.Path(args.policy))
    suppressed = load_suppressions(pathlib.Path(args.suppressions))

    blocking, warnings, suppressed_hits = [], [], []
    for f in run.get("findings", []):
        if f.get("false_positive"):
            continue
        if f["id"] in suppressed:
            f["suppressed"] = True
            suppressed_hits.append(f)
            continue
        act = action_for(policy, f["test_class"], f["severity"])
        f["gate_action"] = act
        if act == "block":
            blocking.append(f)
        elif act == "warn":
            warnings.append(f)

    print("\n=== Security Gate ===")
    print(f"run       : {run.get('run_id')}  workload={run.get('workload')}")
    print(f"commit    : {run.get('commit_hash', '')[:12]}  branch={run.get('branch')}")
    print(f"tools     : {', '.join(run.get('tools', [])) or 'none'}")
    print(f"findings  : {len(run.get('findings', []))} total")
    print(f"blocking  : {len(blocking)} | warnings: {len(warnings)} | suppressed: {len(suppressed_hits)}")

    for f in blocking[:25]:
        print(f"  BLOCK [{f['severity']:8}] {f['tool']:13} {f['rule_id'][:40]:40} {f['location'][:60]}")
    if len(blocking) > 25:
        print(f"  ... and {len(blocking) - 25} more blocking findings")
    for f in warnings[:10]:
        print(f"  warn  [{f['severity']:8}] {f['tool']:13} {f['rule_id'][:40]:40} {f['location'][:60]}")

    result = {
        "run_id": run.get("run_id"),
        "workload": run.get("workload"),
        "passed": not blocking,
        "blocking": len(blocking),
        "warnings": len(warnings),
        "suppressed": len(suppressed_hits),
        "top_blocking": blocking[:5],
    }
    if args.out:
        pathlib.Path(args.out).write_text(json.dumps(result, indent=2))

    if blocking:
        print("\nGATE FAILED - fix the blocking findings or file a justified, "
              "time-boxed suppression in policy/suppressions.json\n")
        return 1
    print("\nGATE PASSED\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
