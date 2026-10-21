# DevSecOps-Pipeline – Lehrprojekt

Drei Programme, je eine absichtlich verwundbare und eine bereinigte Variante:
Flask-API, Konfigurations-CLI und HTTP-Dateidienst. Gitleaks, Semgrep, Bandit,
Trivy, Syft, hadolint, Dockle und OWASP ZAP arbeiten mit einer gemeinsamen Policy.

## Start unter Windows und Linux

Voraussetzungen: Python 3.10+, Git und Docker mit Linux-Containern. Docker Desktop
muss laufen. Aus dem Git-Stamm zuerst `cd devsecops-pipeline` ausführen.
Ein `make` oder WSL ist für die Pipeline nicht erforderlich.

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
python scripts/prepare.py
python scripts/pipeline.py workloads/01-flask-api/vulnerable
python scripts/pipeline.py workloads/01-flask-api/fixed
python scripts/demo.py
```

`prepare.py` lädt die per SHA-256 fixierten Images, baut das Bandit-Toolimage
einmalig und füllt den persistenten Trivy-Cache. Die ersten Builds der Programme
installieren ihre exakt versionierten Dependencies. Dafür wird Internet benötigt.

Die Exit-Codes der **einzelnen Pipeline** sind:

| Code | Bedeutung |
|---|---|
| 0 | Alle ausgeführten Pflichtprüfungen erfolgreich, Policy bestanden |
| 1 | Erfolgreiche Scans haben blockierende Security-Findings ergeben |
| 2 | Technischer Fehler, etwa Scanner-Ausfall, kaputter Report, Build- oder Healthcheck-Fehler |

`demo.py` führt alle sechs Varianten aus und prüft die Erwartungen: vulnerable=1,
fixed=0. Es läuft auch nach einem fehlgeschlagenen Fall weiter und endet nur dann
mit 0, wenn **alle sechs** Erwartungen eintreten. Ein Scanner-Ausfall (2) gilt nie
als erfolgreicher Negativtest. Zukünftige CVEs können auch einen Fixed-Lauf
berechtigt stoppen; dann Findings bewerten und Abhängigkeiten aktualisieren.

## Ablauf und Automatisierung

1. Runtime prüfen; ausgewählten Workload ohne Demo-Ausnahmen auf Secrets scannen.
2. Zusätzlich Git-Historie am tatsächlichen Git-Stamm scannen. Nur die bekannten
   absichtlichen Negativbeispiele sind im History-Scan ausgenommen.
3. Lokale, versionierte Semgrep-Regeln und Bandit ausführen.
4. Trivy-Dateisystemscan und CycloneDX-SBOM mit Syft erzeugen.
5. CLI tatsächlich bauen/installieren und ohne Netzwerk ausführen; Vorab-Gate.
6. Web-Image bauen, Trivy und Dockle gegen das exportierte Image prüfen; Image-Gate.
7. Erst nach bestandenem Image-Gate Webdienst ohne Host-Port und mit internem
   Netzwerk starten; Healthcheck und funktionale API-Aufrufe sind Pflicht.
8. ZAP importiert die explizite OpenAPI-Beschreibung. Der API-Scan verwendet
   `-S` und prüft passiv; er ist kein aktiver SQLi-/XSS-Penetrationstest.
9. Gate auswerten, Bericht erzeugen und optional in `REGISTRY` veröffentlichen.
   Ein aktivierter, fehlgeschlagener Push ist ein technischer Fehler.

CLI-Images werden nach dem Vorab-Gate ebenfalls gescannt; nur HTTP-Deployment
und ZAP sind mangels HTTP-Schnittstelle ausdrücklich nicht anwendbar.
Nach Security-Ablehnung werden spätere Schritte nicht gestartet. Nach technischen
Fehlern werden die vorhandenen Ergebnisse mit Status ERROR dokumentiert.

Die GitHub-Actions-Datei liegt unter **`<Git-Stamm>/.github/workflows/devsecops.yml`**.
Push und Pull Request starten Unit-Tests und eine Matrix aller sechs Fälle.
Der grüne CI-Demo-Job belegt die erwarteten positiven und negativen Fälle; die
Security-Gates der verwundbaren Varianten bleiben in den Artefakten FAIL.

Alternativ liegt `<Git-Stamm>/.gitlab-ci.yml` vor. Sie nutzt dieselben Python-Skripte.
GitLab benötigt einen eigenen Runner mit privilegiertem Docker-in-Docker; diese
Runner-Einstellung muss am Server gesetzt werden. Es existiert keine zweite,
abweichende Implementierung der Gates in YAML. Ein tatsächlicher Push-Trigger
ist erst nach Push dieses Branches zum CI-Dienst nachgewiesen.

Die optionale `.pre-commit-config.yaml` liegt ebenfalls am Git-Stamm:

```bash
# Vom Git-Stamm, nachdem pre-commit installiert wurde:
python -m pre_commit install
```

## Policy, Fehler und Ausnahmen

`policy/thresholds.yaml`: Secrets blockieren immer, SAST ab HIGH, SCA ab CRITICAL,
Images ab HIGH. DAST-Findings warnen; ein **technisch fehlgeschlagener DAST-Scan**
blockiert trotzdem. Pflichtreports müssen gültig sein und einen erfolgreichen
Scannerlauf belegen. Fehlende, leere oder fehlerhafte Reports sind keine sauberen Scans.

`policy/suppressions.json`: Jede Ausnahme braucht Finding-ID, Owner, Begründung
und ein gültiges Ablaufdatum. Nach Ablauf ist das Finding wieder wirksam.
SCA- und Image-Kontext bleiben beim Deduplizieren erhalten, damit die strengere
Image-Policy nicht verloren geht. Der alternative historische OPA-Entwurf ist
kein unterstützter Einstieg; maßgeblich ist das getestete Python-Gate.

## Ergebnisse

Jeder Lauf schreibt `reports/<UTC-Zeit>-<Workload>-<Zufalls-ID>/`:

- `run.json`: Checkstatus, explizite Auslassungen, Tool-Images und Startzeit.
- `raw/`: echte Scannerberichte und SBOM.
- `findings.json`, `gate.json`, `timings.json`: normalisierte Ergebnisse,
  Entscheidung mit PASS/FAIL/ERROR und Laufzeiten.
- `reports/FINDINGS_REPORT.md`, `metrics.csv`, `demo-results.json`: Zusammenfassung.

`REPORTS_DIR` kann auf ein separates Ausgabeverzeichnis zeigen.
Der alte unversionierte `reports/example-run` ist ein Fixture-Beispiel und wird
vom Reportgenerator nicht als echter Lauf übernommen. Die historische Erstprüfung
steht in [VALIDIERUNG.md](docs/VALIDIERUNG.md); ihr Ergebnisordner bleibt erhalten.
Aktuelle Nachweise und Grenzen stehen in [NACHPRUEFUNG.md](docs/NACHPRUEFUNG.md).
Die manuelle Einordnung findet sich in [FINDINGS_BEWERTUNG.md](docs/FINDINGS_BEWERTUNG.md).

## Funktionstest und Offline-Demo

```bash
# Führt auch ein verwundbares Programm isoliert aus, das das Gate sonst stoppt:
python scripts/smoke.py workloads/02-cli-deps/vulnerable

# Nach einem vollständigen Online-Durchlauf und lokal gecachten Image-Builds:
python scripts/prepare.py --offline
python scripts/demo.py --offline
```

Der Smoke-Test ist separat gekennzeichnet und belegt ausschließlich Lauffähigkeit.
Er umgeht kein Gate für Publishing. Die bewusst alte Python-3.8-CLI-Umgebung
existiert nur für das isolierte Negativbeispiel. Dort sind verwundbare Pakete Absicht.

Offline werden lokale Regeln, installierter Bandit, persistente Trivy-Datenbanken
und vorgebaute Images verwendet. Deren Tag enthält den Hash der Workload-Dateien.
Geänderte Quellen oder Dependencies ohne exakt passendes Image müssen mit ERROR enden.
`--skip-dast` ist ein ausdrücklich dokumentierter Teillauf, kein vollständiger
DAST-Nachweis. Images, Regeln und aktuelle CVE-Datenbank sind unterschiedliche
Versionsstände; gleiche Images garantieren bei aktualisierter DB keine gleichen Findings.

## Optionale Dienste

Die Compose-Datei unter `infra/` ist ein experimenteller Tooling-Entwurf für Gitea,
Vault, DefectDojo und eine Registry. Sie ist nicht Bestandteil des benötigten
Security-Scan-Pfads. `compose config` validiert nur Syntax. Besonders DefectDojo
benötigt sein vollständiges offizielles Deployment mit Initialisierung und Worker;
die kleine Entwurfsdatei ist dafür kein Betriebsnachweis. Gitea allein führt keine
Pipeline aus. Vault injiziert ohne zusätzliche Runner-Konfiguration keine Secrets.
`defectdojo_import.py` ist ein optionales, separat aufzurufendes Importwerkzeug;
inkompatible Dockle-/ZAP-JSON-Dateien werden nicht als SARIF/XML importiert.

Die absichtlichen Secrets sind erfundene Demo-Werte. Niemals echte Zugangsdaten
in die Workloads schreiben. Die Pipeline veröffentlicht keine Testports;
Scans und Smoke-Tests richten sich ausschließlich gegen die eigenen Container.
