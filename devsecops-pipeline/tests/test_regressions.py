"""Regression coverage of the failures demonstrated in docs/VALIDIERUNG.md."""
import json
import os
import pathlib
import subprocess
import sys
from datetime import date, timedelta
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from gate import load_suppressions, minimal_yaml, load_yaml, suppression_matches
from normalize import dedupe, normalize_file, parse_trivy, parse_zap, validate_report
from report import render
from test_gate import run_gate, write_run, finding


@pytest.mark.parametrize('raw', ['', '{broken', '{}', '{"runs":[]}'])
def test_invalid_sarif_cannot_be_clean(tmp_path, raw):
    path = tmp_path / 'scan.sarif'
    path.write_text(raw)
    with pytest.raises(ValueError):
        normalize_file(path, 'sarif', 'semgrep', 'sast')


def test_sarif_unsuccessful_invocation_rejected():
    with pytest.raises(ValueError):
        validate_report({'runs': [{'results': [], 'invocations': [{'executionSuccessful': False}]}]}, 'sarif')


def test_no_execution_evidence_fails_closed(tmp_path):
    path = write_run(tmp_path, [])
    doc = json.loads(path.read_text())
    doc.pop('scan_status')
    path.write_text(json.dumps(doc))
    assert run_gate(path).returncode == 2


@pytest.mark.parametrize('check', ['runtime', 'semgrep', 'health', 'publish'])
def test_technical_errors_block_even_without_findings(tmp_path, check):
    path = write_run(tmp_path, [])
    doc = json.loads(path.read_text())
    doc['scan_status'][check] = {'status': 'error', 'error': 'injected failure'}
    path.write_text(json.dumps(doc))
    assert run_gate(path).returncode == 2


def test_equal_severity_sca_cannot_hide_image_policy(tmp_path):
    doc = {'Results': [{'Target': 'requirements.txt', 'Vulnerabilities': [{
        'VulnerabilityID': 'CVE-TEST', 'PkgName': 'pkg', 'InstalledVersion': '1', 'Severity': 'HIGH'}]}]}
    fs = parse_trivy(doc, 'trivy-fs', 'sca')
    image = parse_trivy(doc, 'trivy-image', 'image')
    merged = dedupe(fs + image)
    assert len(merged) == 2
    assert run_gate(write_run(tmp_path, merged)).returncode == 1


@pytest.mark.parametrize('expiry,active', [(None, False), ('invalid', False),
    ((date.today()-timedelta(days=1)).isoformat(), False),
    ((date.today()+timedelta(days=1)).isoformat(), True)])
def test_suppression_expiry_is_required(tmp_path, expiry, active):
    path = tmp_path / 'suppressions.json'
    entry = {'finding_id': 'x', 'owner': 'team', 'justification': 'reviewed test'}
    if expiry is not None:
        entry['expires_at'] = expiry
    path.write_text(json.dumps({'suppressions': [entry]}))
    assert ('x' in load_suppressions(path)) is active


def test_policy_fallback_matches_yaml_parser():
    path = ROOT / 'policy/thresholds.yaml'
    assert minimal_yaml(path.read_text()) == load_yaml(path)


@pytest.mark.parametrize('changed', ['workload', 'base_image', 'scan_status', 'evidence'])
def test_dockle_exception_cannot_escape_its_scope(changed):
    entry = json.loads((ROOT/'policy/suppressions.json').read_text())['suppressions'][0]
    run = {'workload': '01-flask-api-fixed', 'base_image': entry['base_image'],
           'scan_status': {'package-cache-empty': {'status': 'ok'}}}
    f = {'evidence': entry['evidence_contains']}
    assert suppression_matches(entry, f, run)
    if changed == 'evidence':
        f['evidence'] = 'different command'
    else:
        run[changed] = {} if changed == 'scan_status' else 'different'
    assert not suppression_matches(entry, f, run)


@pytest.mark.parametrize('uri', ['http://app:8080/file?name=x', '/file?name=x'])
def test_zap_absolute_and_relative_urls(uri):
    doc = {'site': [{'@name': 'http://app:8080', 'alerts': [{'pluginid': '1', 'name': 'test',
        'riskcode': '1', 'instances': [{'uri': uri}]}]}]}
    assert parse_zap(doc)[0]['location'] == 'http://app:8080/file?name=x'


def test_pending_gate_is_not_reported_as_failed():
    assert '| PENDING |' in render([{'run_id': 'pending', 'findings': []}])


def test_report_distinguishes_technical_error_from_policy_rejection():
    text = render([{'run_id': 'error', 'findings': [], 'gate': {'status': 'ERROR', 'passed': False}}])
    assert '| ERROR |' in text


def test_collect_rejects_absent_run_evidence(tmp_path):
    result = subprocess.run([sys.executable, str(ROOT/'scripts/collect.py'), '--run-dir', str(tmp_path)], capture_output=True)
    assert result.returncode == 2
    assert json.loads((tmp_path/'findings.json').read_text())['scan_errors']


def test_entire_pipeline_rejects_broken_runtime(tmp_path):
    # Python interprets the Docker subcommand "info" as a missing script.
    # No container runtime is needed to reproduce a total runtime failure.
    env = {**os.environ, 'CONTAINER_RUNTIME': sys.executable, 'REPORTS_DIR': str(tmp_path)}
    result = subprocess.run([sys.executable, str(ROOT/'scripts/pipeline.py'),
                             'workloads/02-cli-deps/fixed'], env=env, capture_output=True, timeout=60)
    assert result.returncode == 2
    gates = list(tmp_path.glob('*/gate.json'))
    assert len(gates) == 1
    gate = json.loads(gates[0].read_text())
    assert gate['status'] == 'ERROR' and not gate['passed']


@pytest.mark.parametrize('exit_code', [1, 2])
def test_demo_needs_actual_security_evidence(monkeypatch, tmp_path, exit_code):
    import demo
    from types import SimpleNamespace
    monkeypatch.setenv('REPORTS_DIR', str(tmp_path))
    monkeypatch.setattr(sys, 'argv', ['demo.py', '--workload', 'workloads/02-cli-deps/vulnerable'])
    monkeypatch.setattr(demo.subprocess, 'run', lambda *a, **kw: SimpleNamespace(returncode=exit_code))
    assert demo.main() == 1


def test_demo_accepts_a_proven_security_rejection(monkeypatch, tmp_path):
    import demo
    from types import SimpleNamespace
    monkeypatch.setenv('REPORTS_DIR', str(tmp_path))
    monkeypatch.setattr(sys, 'argv', ['demo.py', '--workload', 'workloads/02-cli-deps/vulnerable'])
    def run(*args, **kwargs):
        folder = tmp_path/'test-run'
        folder.mkdir()
        (folder/'gate.json').write_text(json.dumps({'run_id': 'test-run', 'status': 'FAIL', 'blocking': 1}))
        return SimpleNamespace(returncode=1)
    monkeypatch.setattr(demo.subprocess, 'run', run)
    assert demo.main() == 0


def test_offline_cache_is_keyed_to_source_contents(monkeypatch, tmp_path):
    import pipeline
    monkeypatch.setattr(pipeline, 'ROOT', tmp_path)
    work = tmp_path/'workloads/unit/fixed'
    work.mkdir(parents=True)
    (tmp_path/'policy').mkdir()
    (tmp_path/'policy/images.lock.json').write_text('{"python":"locked","hadolint":"locked"}')
    (work/'workload.json').write_text('{"kind":"cli"}')
    (work/'Dockerfile').write_text('FROM locked\n')
    (work/'main.py').write_text('print(1)\n')
    original = pipeline.Pipeline('workloads/unit/fixed', offline=True)
    (work/'__pycache__').mkdir()
    (work/'__pycache__/ignored.pyc').write_bytes(b'cache')
    assert pipeline.Pipeline('workloads/unit/fixed', offline=True).tag == original.tag
    (work/'main.py').write_text('print(2)\n')
    assert pipeline.Pipeline('workloads/unit/fixed', offline=True).tag != original.tag
    commands = []
    original.check = lambda name, args, **kwargs: commands.append((name, args))
    original.build()
    assert commands[-1] == ('build', ['image', 'inspect', original.tag])
