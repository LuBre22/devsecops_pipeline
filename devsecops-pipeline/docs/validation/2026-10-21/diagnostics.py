"""Extra smoke checks that do not bypass or modify the real pipeline gates."""
import json
import pathlib
import shutil
import subprocess
import time

BASE = pathlib.Path(__file__).resolve().parent
PROJECT = BASE / 'project'
OUT = BASE / 'evidence'
summary = []

def run(name, args, timeout=900):
    start = time.monotonic()
    with (OUT / (name + '.log')).open('w', encoding='utf-8') as output:
        try:
            proc = subprocess.run(args, stdout=output, stderr=subprocess.STDOUT, timeout=timeout)
            code = proc.returncode
        except subprocess.TimeoutExpired:
            code = 124
    summary.append({'name': name, 'exit_code': code, 'seconds': round(time.monotonic()-start, 1)})
    (OUT / 'diagnostics-summary.json').write_text(json.dumps(summary, indent=2))
    print(summary[-1], flush=True)
    return code

# A completely broken runtime must not produce a successful run.
failure_project = BASE / 'failure-project'
if not failure_project.exists():
    shutil.copytree(PROJECT, failure_project, ignore=shutil.ignore_patterns('reports', '__pycache__', '.pytest_cache'))
run('all-scanners-failed', ['docker', 'run', '--rm', '-e', 'CONTAINER_RUNTIME=false',
    '-v', f'{failure_project}:/project', '-w', '/project', 'devsecops-validation-runner:20261021',
    'bash', 'scripts/run-pipeline.sh', 'workloads/02-cli-deps/fixed'], 120)

# Test the documented fixed images independently, even if their security gate
# rejects them. Run without publishing any host port.
for workload in ('01-flask-api', '03-container-service'):
    name = workload + '-fixed'
    tag = 'devsecops-validation-' + name + ':20261021'
    if run('build-' + name, ['docker', 'build', '-t', tag,
                           str(PROJECT / 'workloads' / workload / 'fixed')]) != 0:
        continue
    container = 'devsecops-validation-' + name
    try:
        code = run('start-' + name, ['docker', 'run', '-d', '--rm', '--name', container,
            '--network', 'none', '--read-only', '--tmpfs', '/tmp', '--cap-drop', 'ALL',
            '--security-opt', 'no-new-privileges', '-e', 'API_TOKEN=validation-only', tag])
        if code != 0:
            continue
        time.sleep(3)
        run('health-' + name, ['docker', 'exec', container, 'python3', '-c',
            "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=5); print(r.status, r.read().decode())"], 30)
        if workload == '01-flask-api':
            run('ping-' + name, ['docker', 'exec', container, 'python3', '-c',
                "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8080/ping?host=127.0.0.1', timeout=10); print(r.status, r.read().decode())"], 30)
    finally:
        run('logs-' + name, ['docker', 'logs', container], 30)
        run('cleanup-' + name, ['docker', 'rm', '-f', container], 30)
