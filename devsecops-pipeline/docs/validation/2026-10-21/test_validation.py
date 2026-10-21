"""Independent acceptance checks. Failures expose gaps in the original code."""
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = next((p for p in pathlib.Path(__file__).resolve().parents
             if (p / 'scripts' / 'gate.py').exists()),
            pathlib.Path(__file__).resolve().parents[1] / 'Entwurf_Pipeline' / 'devsecops-pipeline')
sys.path.insert(0, str(ROOT / 'scripts'))
from normalize import parse_trivy, dedupe, parse_sarif
from gate import action_for, load_yaml, load_suppressions


def command(script, *args):
    return subprocess.run([sys.executable, str(ROOT / 'scripts' / script), *map(str, args)],
                          cwd=ROOT, capture_output=True, text=True)


@pytest.mark.parametrize('report', ['absent', 'malformed'])
def test_scanner_failure_must_not_pass_gate(tmp_path, report):
    raw = tmp_path / 'raw'
    raw.mkdir()
    if report == 'malformed':
        (raw / 'semgrep.sarif').write_text('{broken')
    collected = command('collect.py', '--run-dir', tmp_path, '--workload', 'audit')
    if collected.returncode != 0:
        return
    result = command('gate.py', '--findings', tmp_path / 'findings.json')
    assert result.returncode != 0, f'No successful scanners, but gate passed: {result.stdout}'


def test_image_policy_survives_cross_class_deduplication():
    doc = {'Results': [{'Target': 'requirements.txt', 'Vulnerabilities': [{
        'VulnerabilityID': 'CVE-TEST', 'PkgName': 'example',
        'InstalledVersion': '1', 'Severity': 'HIGH'}]}]}
    findings = dedupe(parse_trivy(doc, 'trivy-fs', 'sca') + parse_trivy(doc, 'trivy-image', 'image'))
    policy = load_yaml(ROOT / 'policy' / 'thresholds.yaml')
    assert any(action_for(policy, f['test_class'], f['severity']) == 'block' for f in findings)


def test_high_bandit_severity_survives_sarif_conversion(tmp_path):
    source = tmp_path / 'source.py'
    source.write_text('import subprocess\nsubprocess.call(input(), shell=True)\n')
    report = tmp_path / 'bandit.sarif'
    result = subprocess.run([sys.executable, '-m', 'bandit', str(source), '-f', 'sarif',
                             '-o', str(report), '--exit-zero'], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    doc = json.loads(report.read_text())
    normalized = parse_sarif(doc, 'bandit', 'sast')
    dangerous = [f for f in normalized if f['rule_id'] == 'B602']
    assert dangerous and dangerous[0]['severity'] == 'HIGH', dangerous


def test_suppression_requires_expiration(tmp_path):
    path = tmp_path / 'suppressions.json'
    path.write_text(json.dumps({'suppressions': [{'finding_id': 'x', 'owner': 'audit',
                                                'justification': 'test'}]}))
    assert 'x' not in load_suppressions(path)


def load_app(variant):
    spec = importlib.util.spec_from_file_location('audit_' + variant,
        ROOT / 'workloads' / '01-flask-api' / variant / 'app.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('variant', ['vulnerable', 'fixed'])
def test_flask_sql_and_xss_behaviour(tmp_path, variant):
    module = load_app(variant)
    module.DB = str(tmp_path / (variant + '.db'))
    module.init_db()
    with module.app.test_client() as client:
        assert client.get('/health').status_code == 200
        assert client.get('/user?name=alice').json['rows'][0][1] == 'alice'
        injected = client.get('/user', query_string={'name': "' OR 1=1 --"})
        assert bool(injected.json['rows']) == (variant == 'vulnerable')
        xss = client.get('/greet', query_string={'name': '<script>alert(1)</script>'})
        assert ('<script>' in xss.text) == (variant == 'vulnerable')
        assert client.get('/hash?value=test').status_code == 200
        if variant == 'fixed':
            assert client.get('/ping?host=invalid').status_code == 400
            assert client.get('/health').headers['Content-Security-Policy'] == "default-src 'self'"


def test_fixed_cli_runs():
    path = ROOT / 'workloads' / '02-cli-deps' / 'fixed'
    result = subprocess.run([sys.executable, 'main.py'], cwd=path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert 'loaded 1 config key(s)' in result.stdout


def test_container_fixed_traversal_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv('DATA_ROOT', str(tmp_path / 'data'))
    (tmp_path / 'data').mkdir()
    (tmp_path / 'outside.txt').write_text('test')
    (tmp_path / 'data' / 'inside.txt').write_text('test')
    spec = importlib.util.spec_from_file_location('audit_container',
        ROOT / 'workloads' / '03-container-service' / 'fixed' / 'app.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    handler = object.__new__(module.Handler)
    replies = []
    handler._json = lambda status, payload: replies.append(status)
    for path in ['/health', '/file?name=inside.txt', '/file?name=../outside.txt', '/unknown']:
        handler.path = path
        handler.do_GET()
    assert replies == [200, 200, 404, 404]
