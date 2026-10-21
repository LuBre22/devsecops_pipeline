"""Execute the unchanged pipeline in a disposable Linux runner; save evidence."""
import json
import pathlib
import shutil
import subprocess
import time

BASE = pathlib.Path(__file__).resolve().parent
SOURCE = BASE.parent / 'Entwurf_Pipeline' / 'devsecops-pipeline'
PROJECT = BASE / 'project'
EVIDENCE = BASE / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
if not PROJECT.exists():
    shutil.copytree(SOURCE, PROJECT, ignore=shutil.ignore_patterns('reports', '__pycache__', '.pytest_cache', '.venv'))

def execute(name, args, timeout=1800):
    start = time.monotonic()
    print(f'START {name}', flush=True)
    with (EVIDENCE / (name + '.log')).open('w', encoding='utf-8') as output:
        try:
            result = subprocess.run(args, stdout=output, stderr=subprocess.STDOUT, timeout=timeout)
            code = result.returncode
        except subprocess.TimeoutExpired:
            code = 124
    info = {'name': name, 'exit_code': code, 'seconds': round(time.monotonic() - start, 1)}
    (EVIDENCE / (name + '.json')).write_text(json.dumps(info, indent=2))
    print(info, flush=True)
    return code

if execute('runner-build', ['docker', 'build', '-t', 'devsecops-validation-runner:20261021', '-f', str(BASE / 'Dockerfile'), str(BASE)]) != 0:
    raise SystemExit(2)

# Match the Docker Desktop daemon's host path so nested scanner bind mounts
# point to exactly the same source directory as the outer runner's mount.
linux_path = '/run/desktop/mnt/host/' + PROJECT.drive[0].lower() + PROJECT.as_posix()[2:]
runner = ['docker', 'run', '--rm', '-v', f'{PROJECT}:{linux_path}',
          '-v', '/var/run/docker.sock:/var/run/docker.sock', '-w', linux_path,
          'devsecops-validation-runner:20261021']
execute('unit-linux', runner + ['python3', '-m', 'pytest', 'tests', '-q'], 120)
results = []
for workload in ('01-flask-api', '02-cli-deps', '03-container-service'):
    for variant in ('vulnerable', 'fixed'):
        name = f'{workload}-{variant}'
        code = execute(name, runner + ['bash', 'scripts/run-pipeline.sh', f'workloads/{workload}/{variant}'])
        results.append({'workload': workload, 'variant': variant, 'exit_code': code})
        (EVIDENCE / 'container-summary.json').write_text(json.dumps(results, indent=2))
