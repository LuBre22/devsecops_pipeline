"""Build and run one program without security gating; records only functional evidence.

Used to demonstrate executability of negative examples that security gates reject.
Never publishes an image. No host ports are exposed; test network is internal.
"""
import argparse
import json
import subprocess
from pipeline import Pipeline, PipelineError


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('workload')
    args = ap.parse_args()
    pipeline = Pipeline(args.workload)
    code = 2
    try:
        pipeline.check('runtime', ['info'])
        pipeline.build()
        if pipeline.config['kind'] == 'cli':
            pipeline.cli_smoke()
        else:
            pipeline.deploy()
        code = 0
    except (PipelineError, OSError, subprocess.SubprocessError) as exc:
        print(f'[smoke] ERROR: {exc}')
    finally:
        (pipeline.run_dir / 'smoke-only.json').write_text(json.dumps({'workload': args.workload,
            'exit_code': code, 'security_scanned': False, 'checks': pipeline.data['checks']}, indent=2))
        subprocess.run([pipeline.runtime, 'rm', '-f', pipeline.container], capture_output=True)
        subprocess.run([pipeline.runtime, 'network', 'rm', pipeline.network], capture_output=True)
        print(f'Functional evidence only: {pipeline.run_dir}')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
