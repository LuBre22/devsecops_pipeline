"""Prepare locked images, a reusable Bandit image, and the persistent Trivy cache."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def prepare(offline=False):
    images = json.loads((ROOT / 'policy/images.lock.json').read_text())
    runtime = os.environ.get('CONTAINER_RUNTIME', 'docker')
    def run(*args, retries=1, retry_delay=0):
        for attempt in range(1, retries + 1):
            try:
                subprocess.run([runtime, *map(str, args)], cwd=ROOT, check=True)
                return
            except subprocess.CalledProcessError:
                if attempt >= retries:
                    raise
                print(f'Command failed (attempt {attempt}/{retries}): {runtime} {" ".join(map(str, args))}')
                if retry_delay:
                    print(f'Retrying in {retry_delay} seconds...')
                    time.sleep(retry_delay)
    for name, ref in images.items():
        if name != 'bandit':
            run('image', 'inspect', ref) if offline else run('pull', ref)
    if offline:
        run('image', 'inspect', images['bandit'])
    else:
        run('build', '--pull=false', '--build-arg', 'PYTHON_IMAGE=' + images['python'],
            '-f', ROOT / 'infra/bandit.Dockerfile', '-t', images['bandit'], ROOT / 'infra')
    run('volume', 'create', 'devsecops-trivy-cache')
    if not offline:
        run('run', '--rm', '-v', 'devsecops-trivy-cache:/cache', images['trivy'],
            'image', '--cache-dir', '/cache', '--download-db-only', '--no-progress',
            retries=3, retry_delay=15)
        run('run', '--rm', '-v', 'devsecops-trivy-cache:/cache', '-v', f'{ROOT / "policy"}:/src:ro',
            images['trivy'], 'fs', '--cache-dir', '/cache', '--scanners', 'misconfig', '--no-progress', '/src')
    print('Prepared. Offline scans reuse these images and the warmed cache.')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--offline', action='store_true')
    prepare(**vars(ap.parse_args()))
