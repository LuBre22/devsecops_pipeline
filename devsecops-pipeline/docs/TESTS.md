# Testdokumentation

Diese Dokumentation beschreibt die automatisierten Unit-Tests der
DevSecOps-Pipeline. Die Tests prüfen die zentrale Pipeline-Logik ohne
Container-Runtime und ohne Zugriff auf externe Scanner. Dadurch können sie
schnell und reproduzierbar ausgeführt werden.

## Tests ausführen

### PowerShell unter Windows

```powershell
python -m pytest .\tests -vv -s
```

### Git Bash oder WSL

```bash
python3 -m pytest tests -vv -s
```

Die Option `-vv` gibt jeden Test einzeln aus. Die Option `-s` zeigt zusätzlich
die Konsolenausgabe der Tests an.

Erwartetes Ergebnis:

```text
11 passed
```

## Testdatei und Testaufbau

Die Tests befinden sich in
[`tests/test_gate.py`](../tests/test_gate.py). Sie verwenden:

- die Gate-Implementierung aus `scripts/gate.py`,
- die Normalisierung aus `scripts/normalize.py`,
- Test-Fixtures aus `tests/fixtures/`,
- temporäre Finding-Dateien für die Gate-Prüfungen.

Die Gate-Tests starten `gate.py` als separaten Python-Prozess. Dadurch wird
auch die tatsächliche Kommandozeilenschnittstelle mit den verwendeten
Policy- und Suppression-Dateien geprüft.

## Einzelne Tests

### 1. `test_gate_passes_without_findings`

**Was wird getestet?**  
Ein Lauf ohne Findings wird gegen die Policy ausgewertet.

**Erwartung:**  
Das Gate besteht und liefert den Exit-Code `0`.

**Bedeutung:**  
Ein sauberer Scan darf den Build nicht blockieren.

### 2. `test_high_sast_finding_blocks`

**Was wird getestet?**  
Ein Finding der Testklasse `sast` mit der Severity `HIGH`.

**Erwartung:**  
Das Gate schlägt fehl, liefert den Exit-Code `1` und gibt `GATE FAILED`
aus.

**Bedeutung:**  
Schwere statische Codeanalyse-Findings müssen den Build blockieren.

### 3. `test_high_sca_finding_only_warns`

**Was wird getestet?**  
Ein `HIGH`-Finding aus der Testklasse `sca`, also beispielsweise eine
Abhängigkeit mit einer bekannten Schwachstelle.

**Erwartung:**  
Das Gate besteht mit Exit-Code `0`, gibt aber eine Warnung aus
(`warnings: 1`).

**Bedeutung:**  
Die Policy behandelt `HIGH`-SCA-Findings zunächst als Warnung, weil nicht
jede Schwachstelle in einer Abhängigkeit einen tatsächlich erreichbaren
oder ausnutzbaren Codepfad betrifft.

### 4. `test_any_secret_blocks`

**Was wird getestet?**  
Ein Secret-Finding mit der niedrigen Severity `INFO`.

**Erwartung:**  
Das Gate schlägt trotzdem mit Exit-Code `1` fehl.

**Bedeutung:**  
Ein erkanntes Secret blockiert unabhängig von seiner gemeldeten Severity.
Ein möglicherweise kompromittiertes Secret muss entfernt oder rotiert
werden.

### 5. `test_dast_never_blocks`

**Was wird getestet?**  
Ein `CRITICAL`-Finding aus einem DAST-Scan.

**Erwartung:**  
Das Gate besteht mit Exit-Code `0`.

**Bedeutung:**  
DAST-Findings sind in dieser Pipeline als Warnungen konfiguriert, weil
Baseline-Scans eine höhere Rate an False Positives haben können. Sie werden
weiterhin berichtet und müssen manuell bewertet werden.

### 6. `test_false_positive_is_ignored`

**Was wird getestet?**  
Ein als `false_positive` markiertes Secret-Finding.

**Erwartung:**  
Das Gate besteht mit Exit-Code `0`.

**Bedeutung:**  
Eine dokumentierte False-Positive-Markierung verhindert, dass das Finding
das Gate blockiert. Die Markierung muss fachlich nachvollziehbar bleiben und
darf nicht zum stillen Ausblenden echter Findings verwendet werden.

### 7. `test_sarif_normalisation`

**Was wird getestet?**  
Die Normalisierung des Semgrep-SARIF-Fixtures
`tests/fixtures/semgrep.sarif`.

**Erwartung:**  
Mindestens ein Finding wird erzeugt, die Testklasse ist `sast` und die
Severity entspricht einer gültigen gemeinsamen Severity-Stufe:
`INFO`, `LOW`, `MEDIUM`, `HIGH` oder `CRITICAL`.

**Bedeutung:**  
SARIF-Ergebnisse verschiedener Scanner werden in das gemeinsame
Finding-Modell der Pipeline überführt.

### 8. `test_trivy_normalisation_maps_severity`

**Was wird getestet?**  
Die Normalisierung des Trivy-Fixtures
`tests/fixtures/trivy-fs.json`.

**Erwartung:**  
Mindestens ein Finding wird auf `CRITICAL` abgebildet und alle CVE-IDs
beginnen mit `CVE-`.

**Bedeutung:**  
Trivy-Schweregrade und Advisory-Informationen werden korrekt in das
gemeinsame Finding-Modell übernommen.

### 9. `test_gitleaks_findings_are_always_critical`

**Was wird getestet?**  
Die Normalisierung des Gitleaks-Fixtures
`tests/fixtures/gitleaks.json`.

**Erwartung:**  
Es werden Findings erzeugt und jedes davon erhält die Severity `CRITICAL`.

**Bedeutung:**  
Gitleaks liefert keine einheitliche Severity. Ein gefundenes Secret wird
deshalb grundsätzlich als kritisch behandelt, weil es unabhängig von einer
ursprünglichen Klassifizierung entfernt und gegebenenfalls rotiert werden
muss.

### 10. `test_dedupe_keeps_highest_severity`

**Was wird getestet?**  
Zwei Findings mit derselben Finding-ID, aber unterschiedlichen Severities:
`LOW` und `CRITICAL`.

**Erwartung:**  
Nach der Deduplizierung bleibt genau ein Finding mit der Severity `CRITICAL`
übrig.

**Bedeutung:**  
Dasselbe Problem soll im Bericht nicht mehrfach erscheinen. Bei
zusammengeführten Meldungen darf jedoch die höchste Severity nicht verloren
gehen.

### 11. `test_missing_report_is_tolerated`

**Was wird getestet?**  
Die Normalisierung einer nicht vorhandenen SARIF-Reportdatei.

**Erwartung:**  
Die Normalisierung liefert eine leere Finding-Liste, ohne eine Exception
auszulösen. Zusätzlich wird eine Meldung ausgegeben, dass der Report fehlt
oder leer ist.

**Bedeutung:**  
Ein fehlender optionaler Tool-Report soll die nachfolgenden Pipeline-Schritte
nicht durch einen unkontrollierten Python-Fehler abbrechen. Der fehlende
Report bleibt durch die Konsolenausgabe sichtbar.

## Abdeckung der Pipeline-Logik

Die 11 Tests decken insbesondere folgende Regeln ab:

| Bereich | Abgedecktes Verhalten |
|---|---|
| Gate-Entscheidung | Bestanden, fehlgeschlagen und Warnungen |
| SAST | `HIGH` blockiert |
| SCA | `HIGH` warnt, blockiert aber nicht |
| Secrets | Jedes erkannte Secret blockiert |
| DAST | Findings blockieren nicht |
| False Positives | Markierte Findings werden nicht gewertet |
| SARIF | Scanner-Ausgabe wird normalisiert |
| Trivy | Severity und CVE-IDs werden übernommen |
| Gitleaks | Secrets werden als `CRITICAL` klassifiziert |
| Deduplizierung | Höchste Severity bleibt erhalten |
| Fehlerbehandlung | Fehlende Reports werden sichtbar toleriert |

## Grenzen der Tests

Die Unit-Tests prüfen nicht die Container selbst und starten keine externen
Scanner. Nicht abgedeckt sind daher insbesondere:

- die Verfügbarkeit und korrekte Version der Scanner-Images,
- der Docker- oder Podman-Image-Build,
- Deploy- und Healthcheck-Schritte,
- der OWASP-ZAP-Lauf gegen eine Testinstanz,
- Registry-Publishing und externe DefectDojo-Integration.

Für diese Bereiche ist ein vollständiger Pipeline-Lauf mit einem
Demo-Workload erforderlich. Die Unit-Tests bleiben trotzdem der schnellste
Feedback-Zyklus für Änderungen an Finding-Normalisierung, Policy und Gate.
