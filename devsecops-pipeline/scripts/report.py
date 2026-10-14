#!/usr/bin/env python3
"""Render the findings report (Markdown) and the metrics file (CSV).

Covers requirement A-07 (documentation of results and findings) and F-09
(metrics: findings per severity, stage duration, false positive rate).
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
from collections import Counter, defaultdict

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]


def load_runs(reports_dir: pathlib.Path) -> list[dict]:
    runs = []
    for findings in sorted(reports_dir.glob("*/findings.json")):
        run = json.loads(findings.read_text())
        timing = findings.parent / "timings.json"
        run["timings"] = json.loads(timing.read_text()) if timing.exists() else {}
        gate = findings.parent / "gate.json"
        run["gate"] = json.loads(gate.read_text()) if gate.exists() else {}
        runs.append(run)
    return runs


def table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |")
    return "\n".join(out)


def render(runs: list[dict]) -> str:
    md = ["# Findings Report - DevSecOps Pipeline", ""]
    if not runs:
        md.append("_No pipeline runs found. Execute `make demo` first._")
        return "\n".join(md)

    md += ["## 1. Run overview", "",
           table(["Run", "Workload", "Branch", "Commit", "Tools", "Findings", "Gate"],
                 [[r["run_id"], r.get("workload", ""), r.get("branch", ""),
                   (r.get("commit_hash") or "")[:8], len(r.get("tools", [])),
                   len(r.get("findings", [])),
                   "PASS" if r.get("gate", {}).get("passed") else "FAIL"]
                  for r in runs]), ""]

    md += ["## 2. Findings per severity and test class", ""]
    for r in runs:
        counts = defaultdict(Counter)
        for f in r.get("findings", []):
            counts[f["test_class"]][f["severity"]] += 1
        classes = sorted(counts)
        rows = [[c] + [counts[c].get(s, 0) for s in SEVERITY_ORDER] for c in classes]
        total = [sum(counts[c].get(s, 0) for c in classes) for s in SEVERITY_ORDER]
        rows.append(["**total**"] + total)
        md += [f"### {r['run_id']} - {r.get('workload', '')}", "",
               table(["Test class"] + SEVERITY_ORDER, rows), ""]

    md += ["## 3. Findings detail (blocking and high severity)", ""]
    for r in runs:
        interesting = [f for f in r.get("findings", [])
                       if f["severity"] in ("CRITICAL", "HIGH")][:40]
        if not interesting:
            md += [f"### {r['run_id']}", "", "_No critical or high findings._", ""]
            continue
        md += [f"### {r['run_id']}", "",
               table(["Severity", "Tool", "Rule / CVE", "Location", "Title", "Remediation"],
                     [[f["severity"], f["tool"], f["cve_id"] or f["rule_id"],
                       f["location"][:60], f["title"][:80], f["remediation"][:60]]
                      for f in interesting]), ""]

    md += ["## 4. Stage duration (fail-fast evidence)", ""]
    for r in runs:
        t = r.get("timings", {})
        if not t:
            continue
        md += [f"### {r['run_id']}", "",
               table(["Stage", "Duration (s)"],
                     [[k, v] for k, v in t.items()]), ""]

    md += ["## 5. False positive assessment", "",
           "Fill in during triage. A finding counts as a false positive only after",
           "manual verification; the rate per tool is a core insight for the presentation.", "",
           table(["Tool", "Findings", "Verified true", "False positive", "FP rate"],
                 [[tool, n, "", "", ""] for tool, n in
                  Counter(f["tool"] for r in runs for f in r.get("findings", [])).most_common()]), ""]

    md += ["## 6. Lessons learned", "",
           "- Which tool produced the most actionable findings?",
           "- Where did the gate block, and was the threshold appropriate?",
           "- Which findings only the dynamic scan could reveal?",
           "- What is still uncovered (container runtime security, IAST, pen testing)?", ""]
    return "\n".join(md)


def write_metrics(runs: list[dict], path: pathlib.Path) -> None:
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["run_id", "workload", "commit", "tool", "test_class",
                    "severity", "count"])
        for r in runs:
            counter = Counter((f["tool"], f["test_class"], f["severity"])
                              for f in r.get("findings", []))
            for (tool, tc, sev), n in sorted(counter.items()):
                w.writerow([r["run_id"], r.get("workload", ""),
                            (r.get("commit_hash") or "")[:8], tool, tc, sev, n])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports-dir", default="reports")
    ap.add_argument("--out", default="reports/FINDINGS_REPORT.md")
    ap.add_argument("--metrics", default="reports/metrics.csv")
    args = ap.parse_args()

    runs = load_runs(pathlib.Path(args.reports_dir))
    pathlib.Path(args.out).write_text(render(runs))
    write_metrics(runs, pathlib.Path(args.metrics))
    print(f"[report] {len(runs)} runs -> {args.out} and {args.metrics}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
