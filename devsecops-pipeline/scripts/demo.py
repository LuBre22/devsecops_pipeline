"""Check all expected PASS/FAIL cases without hiding technical errors."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workload', help='Run just one workloads/<program>/<variant>')
    ap.add_argument('--offline', action='store_true')
    args = ap.parse_args()
    workloads = [args.workload] if args.workload else [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / 'workloads').glob('*/*')) if p.is_dir()]
    results = []
    reports = Path(os.environ.get('REPORTS_DIR', str(ROOT / 'reports')))
    reports.mkdir(exist_ok=True, parents=True)
    for workload in workloads:
        before = set(reports.glob('*/gate.json'))
        expected = 1 if workload.endswith('/vulnerable') else 0
        command = [sys.executable, str(ROOT / 'scripts/pipeline.py'), workload]
        if args.offline:
            command.append('--offline')
        actual = subprocess.run(command, cwd=ROOT).returncode
        created = set(reports.glob('*/gate.json')) - before
        decisions = []
        for path in created:
            try:
                decisions.append(json.loads(path.read_text(encoding='utf-8')))
            except (OSError, ValueError):
                pass
        decision = decisions[0] if len(decisions) == 1 else {}
        expected_status = 'FAIL' if expected == 1 else 'PASS'
        matched = actual == expected and decision.get('status') == expected_status
        matched = matched and (expected == 0 or decision.get('blocking', 0) > 0)
        results.append({'workload': workload, 'run_id': decision.get('run_id'), 'expected': expected,
                        'actual': actual, 'gate_status': decision.get('status'), 'matched': matched})
    (reports / 'demo-results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(json.dumps(results, indent=2))
    return 0 if all(r['matched'] for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
