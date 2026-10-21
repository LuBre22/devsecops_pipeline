"""One Docker pipeline for Windows, Linux, GitHub Actions and GitLab CI.

0 = passed, 1 = security policy rejected the workload, 2 = technical error.
"""
from __future__ import annotations
import argparse
import hashlib
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
import uuid

from collect import git
from normalize import validate_report

ROOT = Path(__file__).resolve().parents[1]


class PipelineError(Exception):
    pass


class Pipeline:
    def __init__(self, workload: str, *, offline=False, skip_dast=False, keep=False):
        self.workload = (ROOT / workload).resolve()
        if not self.workload.is_relative_to(ROOT / 'workloads') or not self.workload.is_dir():
            raise ValueError('workload must be a directory below workloads/')
        self.name = self.workload.relative_to(ROOT / 'workloads').as_posix().replace('/', '-')
        self.config = json.loads((self.workload / 'workload.json').read_text())
        self.images = json.loads((ROOT / 'policy' / 'images.lock.json').read_text())
        self.run_id = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + self.name + '-' + uuid.uuid4().hex[:6]
        self.reports_dir = Path(os.environ.get('REPORTS_DIR', str(ROOT / 'reports'))).resolve()
        self.run_dir = self.reports_dir / self.run_id
        self.raw = self.run_dir / 'raw'
        self.raw.mkdir(parents=True)
        self.runtime = os.environ.get('CONTAINER_RUNTIME', 'docker')
        self.offline, self.skip_dast, self.keep = offline, skip_dast, keep
        digest = hashlib.sha256()
        for file in sorted(self.workload.rglob('*')):
            if file.is_file() and '__pycache__' not in file.parts and file.suffix != '.pyc':
                digest.update(file.relative_to(self.workload).as_posix().encode())
                digest.update(b'\0' + file.read_bytes() + b'\0')
        self.source_digest = digest.hexdigest()
        self.tag = 'devsecops-demo-' + self.name + ':' + self.source_digest[:20]
        suffix = uuid.uuid4().hex[:12]
        self.container, self.network = 'dso-app-' + suffix, 'dso-net-' + suffix
        self.data = {'started_at': datetime.now(timezone.utc).isoformat(), 'workload': self.name,
                     'images': self.images, 'offline': offline, 'checks': {}}
        self.data['base_image'] = next(line.split()[1] for line in (self.workload / 'Dockerfile').read_text().splitlines() if line.startswith('FROM '))
        self.data['source_digest'] = self.source_digest
        implementation = hashlib.sha256()
        for file in sorted([*ROOT.glob('scripts/*.py'), *ROOT.glob('policy/*'), *ROOT.glob('infra/bandit*')]):
            if file.is_file():
                implementation.update(file.relative_to(ROOT).as_posix().encode() + b'\0' + file.read_bytes())
        self.data['pipeline_source_digest'] = implementation.hexdigest()
        self.timings = {}
        self.save()

    def save(self):
        (self.run_dir / 'run.json').write_text(json.dumps(self.data, indent=2), encoding='utf-8')
        (self.run_dir / 'timings.json').write_text(json.dumps(self.timings, indent=2), encoding='utf-8')

    def command(self, args, *, allowed=(0,), stdout=None, timeout=900):
        result = subprocess.run([self.runtime, *map(str, args)], cwd=ROOT, stdout=stdout, timeout=timeout)
        if result.returncode not in allowed:
            raise PipelineError(f'command {args[:3]} exited {result.returncode}')

    def check(self, name, args, *, report=None, fmt=None, allowed=(0,), stdout=False):
        state = {'status': 'running'}
        if report:
            state['report'] = report
        self.data['checks'][name] = state
        self.save()
        start = time.monotonic()
        print(f'\n[{name}]', flush=True)
        try:
            if stdout:
                with (self.raw / report).open('w', encoding='utf-8') as output:
                    self.command(args, allowed=allowed, stdout=output)
            else:
                self.command(args, allowed=allowed)
            if report:
                validate_report(json.loads((self.raw / report).read_text(encoding='utf-8')), fmt)
            state['status'] = 'ok'
        except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError, PipelineError) as exc:
            state.update(status='error', error=str(exc))
            raise PipelineError(f'{name}: {exc}') from exc
        finally:
            self.timings[name] = round(time.monotonic() - start, 2)
            self.save()

    def tool(self, image, *args, network=None, mounts=()):
        command = ['run', '--rm', '--network', network or ('none' if self.offline else 'bridge'),
                   '-v', f'{self.workload}:/src:ro', '-v', f'{self.raw}:/out:rw', '-w', '/src']
        for source, target, mode in mounts:
            command += ['-v', f'{source}:{target}:{mode}']
        return [*command, self.images[image], *args]

    def trivy(self, mode, target, output):
        flags = ['--cache-dir', '/cache', '--no-progress', '--scanners', 'vuln,misconfig,secret' if mode == 'fs' else 'vuln,secret',
                 '--format', 'json', '--output', '/out/' + output, '--exit-code', '0']
        if self.offline:
            flags += ['--skip-db-update', '--skip-check-update', '--offline-scan']
        return self.tool('trivy', mode, *target, *flags,
                         mounts=[('devsecops-trivy-cache', '/cache', 'rw')])

    def checkpoint(self):
        (self.run_dir / 'findings.json').unlink(missing_ok=True)
        (self.run_dir / 'gate.json').unlink(missing_ok=True)
        collect = subprocess.run([sys.executable, str(ROOT / 'scripts/collect.py'), '--run-dir', str(self.run_dir), '--workload', self.name], cwd=ROOT)
        gate = subprocess.run([sys.executable, str(ROOT / 'scripts/gate.py'), '--findings', str(self.run_dir / 'findings.json'),
                               '--policy', str(ROOT / 'policy/thresholds.yaml'), '--suppressions', str(ROOT / 'policy/suppressions.json'),
                               '--out', str(self.run_dir / 'gate.json')], cwd=ROOT)
        try:
            decision = json.loads((self.run_dir / 'gate.json').read_text(encoding='utf-8'))
            consistent = decision['status'] == {0: 'PASS', 1: 'FAIL', 2: 'ERROR'}.get(gate.returncode)
        except (OSError, ValueError, KeyError):
            consistent = False
        if not consistent:
            error = 'Gate did not produce a decision consistent with its exit code'
            self.data['checks']['gate'] = {'status': 'error', 'error': error}
            self.save()
            (self.run_dir / 'gate.json').write_text(json.dumps({'run_id': self.run_id, 'workload': self.name,
                'passed': False, 'status': 'ERROR', 'errors': [error], 'blocking': 0, 'warnings': 0, 'suppressed': 0}))
            return 2
        if collect.returncode or gate.returncode == 2:
            return 2
        return gate.returncode

    def scans(self):
        resolved = {}
        for name, ref in self.images.items():
            doc = json.loads(subprocess.check_output([self.runtime, 'image', 'inspect', ref], cwd=ROOT))
            resolved[name] = {'reference': ref, 'image_id': doc[0]['Id']}
        self.data['resolved_images'] = resolved
        self.save()
        self.check('gitleaks', self.tool('gitleaks', 'detect', '--no-git', '--source', '/src',
                   '--config', '/config/gitleaks.toml', '--report-format', 'json', '--report-path', '/out/gitleaks.json', '--redact', '--exit-code', '0',
                   network='none', mounts=[(ROOT / '.gitleaks-workload.toml', '/config/gitleaks.toml', 'ro')]), report='gitleaks.json', fmt='gitleaks')
        repo = git('rev-parse', '--show-toplevel')
        if repo != 'unknown':
            self.check('history', ['run', '--rm', '--network', 'none', '-v', f'{repo}:/repo:ro', '-v', f'{self.raw}:/out:rw',
                       '-v', f'{ROOT / ".gitleaks.toml"}:/config.toml:ro', self.images['gitleaks'], 'detect', '--source', '/repo',
                       '--config', '/config.toml', '--report-format', 'json', '--report-path', '/out/gitleaks-history.json', '--redact', '--exit-code', '0'],
                       report='gitleaks-history.json', fmt='gitleaks')
        else:
            self.data['checks']['history'] = {'status': 'skipped', 'reason': 'No Git checkout available'}
            self.save()
        self.check('semgrep', self.tool('semgrep', 'semgrep', 'scan', '--config', '/rules/semgrep.yml', '--sarif',
                   '--output', '/out/semgrep.sarif', '--metrics', 'off', '--disable-version-check', '/src', network='none',
                   mounts=[(ROOT / 'policy/semgrep.yml', '/rules/semgrep.yml', 'ro')]), report='semgrep.sarif', fmt='sarif')
        self.check('bandit', self.tool('bandit', 'bandit', '-r', '/src', '-f', 'sarif', '-o', '/out/bandit.sarif', '--exit-zero', network='none'), report='bandit.sarif', fmt='sarif')
        self.check('trivy-fs', self.trivy('fs', ['/src'], 'trivy-fs.json'), report='trivy-fs.json', fmt='trivy')
        self.check('syft', self.tool('syft', 'scan', 'dir:/src', '-o', 'cyclonedx-json=/out/sbom.cdx.json', '-q', network='none'), report='sbom.cdx.json', fmt='sbom')

    def build(self):
        self.check('hadolint', self.tool('hadolint', 'hadolint', '--format', 'sarif', '/src/Dockerfile', network='none'),
                   report='hadolint.sarif', fmt='sarif', allowed=(0, 1), stdout=True)
        if self.offline:
            # Reuse only an image keyed to exactly these workload contents.
            # Do not rely on BuildKit reusing a networked RUN layer offline.
            self.check('build', ['image', 'inspect', self.tag])
        else:
            self.check('build', ['build', '--pull=false', '-t', self.tag, str(self.workload)])

    def image_scan(self):
        # Tar input works with a local daemon, Docker-in-Docker and Podman.
        self.check('image-export', ['save', self.tag, '-o', str(self.raw / 'image.tar')])
        self.check('trivy-image', self.trivy('image', ['--input', '/out/image.tar'], 'trivy-image.json'), report='trivy-image.json', fmt='trivy')
        self.check('dockle', self.tool('dockle', '--input', '/out/image.tar', '--format', 'json', '--output', '/out/dockle.json', '--exit-code', '0', network='none'),
                   report='dockle.json', fmt='dockle')
        if self.data['base_image'] == self.images['python']:
            # Inspect package caches in an isolated container with application
            # startup overridden. This is evidence for a scoped Dockle review.
            code = "from pathlib import Path; files=[str(p) for d in ('/var/cache/apk','/var/lib/apt/lists','/var/cache/apt') for p in Path(d).rglob('*') if p.is_file() and p.name!='lock']; print('Package cache files:',files); assert not files"
            self.check('package-cache-empty', ['run', '--rm', '--network', 'none', '--read-only', '--cap-drop', 'ALL',
                       '--security-opt', 'no-new-privileges', '--entrypoint', 'python3', self.tag, '-c', code])
        (self.raw / 'image.tar').unlink()

    def cli_smoke(self):
        self.check('cli-smoke', ['run', '--rm', '--network', 'none', '--read-only', '--tmpfs', '/tmp', self.tag])

    def deploy(self):
        self.check('test-network', ['network', 'create', '--internal', self.network])
        self.check('deploy', ['run', '-d', '--name', self.container, '--network', self.network, '--read-only', '--tmpfs', '/tmp',
                   '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '-e', 'API_TOKEN=' + secrets.token_hex(24), self.tag])
        code = "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=2).read()"
        for attempt in range(30):
            ready = subprocess.run([self.runtime, 'exec', self.container, 'python3', '-c', code], capture_output=True, timeout=5)
            if ready.returncode == 0:
                break
            time.sleep(1)
        else:
            self.data['checks']['health'] = {'status': 'error', 'error': 'Healthcheck timed out'}
            self.save()
            raise PipelineError('Application healthcheck failed')
        self.check('health', ['exec', self.container, 'python3', '-c', code])
        paths = self.config['smoke_paths']
        smoke = "import urllib.request,json; paths=" + repr(paths) + "; print(json.dumps({p:urllib.request.urlopen('http://127.0.0.1:8080'+p,timeout=10).status for p in paths}))"
        self.check('api-smoke', ['exec', self.container, 'python3', '-c', smoke])

    def dast(self):
        if self.skip_dast:
            self.data['checks']['zap'] = {'status': 'skipped', 'reason': 'Explicit --skip-dast; no complete DAST evidence'}
            self.save()
            return
        spec = json.loads((self.workload / 'openapi.json').read_text())
        spec['servers'] = [{'url': f'http://{self.container}:8080'}]
        (self.raw / 'openapi.json').write_text(json.dumps(spec), encoding='utf-8')
        self.check('zap', ['run', '--rm', '--network', self.network, '-v', f'{self.raw}:/zap/wrk:rw', '--user', 'root',
                   self.images['zap'], 'zap-api-scan.py', '-t', '/zap/wrk/openapi.json', '-f', 'openapi', '-S', '-I', '-J', 'zap.json', '-r', 'zap.html'],
                   report='zap.json', fmt='zap', allowed=(0, 1, 2))

    def publish(self):
        registry = os.environ.get('REGISTRY', '').rstrip('/')
        if not registry:
            self.data['checks']['publish'] = {'status': 'skipped', 'reason': 'No REGISTRY configured'}
            self.save()
            return
        remote = registry + '/devsecops-' + self.name + ':' + self.run_id
        self.check('tag', ['tag', self.tag, remote])
        self.check('publish', ['push', remote])
        (self.run_dir / 'sbom.cdx.json').write_bytes((self.raw / 'sbom.cdx.json').read_bytes())

    def execute(self):
        result = 2
        try:
            self.check('runtime', ['info'])
            self.scans()
            # The CLI is actually installed/executed even in the negative demo.
            if self.config['kind'] == 'cli':
                self.build()
                self.cli_smoke()
            result = self.checkpoint()
            if result:
                return result
            if self.config['kind'] == 'web':
                self.build()
            self.image_scan()
            result = self.checkpoint()
            if result:
                return result
            if self.config['kind'] == 'web':
                self.deploy()
                self.dast()
            else:
                self.data['checks']['zap'] = {'status': 'skipped', 'reason': 'CLI has no HTTP interface'}
                self.save()
            result = self.checkpoint()
            if result == 0:
                self.publish()
            return result
        except Exception as exc:
            if not any(s.get('status') == 'error' for s in self.data['checks'].values()):
                self.data['checks']['pipeline'] = {'status': 'error', 'error': str(exc)}
                self.save()
            print(f'[pipeline] ERROR: {exc}', file=sys.stderr)
            return 2
        finally:
            # Also capture build, deployment and publish failures after an earlier green gate.
            self.checkpoint()
            subprocess.run([sys.executable, str(ROOT / 'scripts/report.py'), '--reports-dir', str(self.reports_dir),
                            '--out', str(self.reports_dir / 'FINDINGS_REPORT.md'), '--metrics', str(self.reports_dir / 'metrics.csv')], cwd=ROOT)
            if not self.keep:
                subprocess.run([self.runtime, 'rm', '-f', self.container], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run([self.runtime, 'network', 'rm', self.network], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f'Results: {self.run_dir}', flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('workload')
    ap.add_argument('--offline', action='store_true')
    ap.add_argument('--skip-dast', action='store_true')
    ap.add_argument('--keep', action='store_true')
    args = ap.parse_args()
    os.chdir(ROOT)
    try:
        return Pipeline(**vars(args)).execute()
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        print(f'[pipeline] setup error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
