# DevSecOps Pipeline - Lehrprojekt IT-Sicherheit Modul 6

Automatisierte DevSecOps-Pipeline fuer die Gruppenaufgabe aus Modul 6
(Sichere Anwendungsentwicklung, DHBW Mosbach). Die Pipeline fuehrt bei jedem
Commit ohne manuellen Eingriff mehrere Sicherheitswerkzeuge aus, bewertet die
Ergebnisse gegen eine versionierte Policy und bricht den Build ab, wenn der
Schwellwert ueberschritten wird.

## Was die Aufgabe fordert und wo es umgesetzt ist

| Aufgabenpunkt | Umsetzung |
|---|---|
| Kleine DevSecOps-Pipeline | `scripts/run-pipeline.sh` (lokal), `.gitlab-ci.yml` (CI) |
| Mindestens 4 Tools | Gitleaks, Semgrep, Bandit, Trivy, Syft, hadolint, Dockle, OWASP ZAP |
| Automatisierungsmechanismus | `.pre-commit-config.yaml` (bei Commit) und CI-Trigger bei Push/Merge Request |
| 3 verschiedene Code-Artefakte | `workloads/01-flask-api`, `workloads/02-cli-deps`, `workloads/03-container-service` |
| Dokumentation der Findings | `reports/FINDINGS_REPORT.md` und `reports/metrics.csv`, automatisch generiert |
| Praesentation mit Demo | `docs/DEMO_SCRIPT.md` |

## Schnellstart

Für Windows (ohne make) siehe weiter unten.

Voraussetzungen: Docker (oder Podman), Git, Python 3.10+, Bash. Die Scanner
laufen als Container mit festgepinnten Versionen. Beim ersten Lauf muessen die
Images und Scanner-Regeldatenbanken erreichbar sein; mit vorab geladenen Images
und Cache sind Folge-Laeufe weitgehend lokal reproduzierbar. `make setup` richtet
pytest und pre-commit fuer Entwickler ein.

```bash
# 1. Repository holen und betreten
git clone <repo-url> devsecops-pipeline && cd devsecops-pipeline

# 2. Developer-Abhaengigkeiten und Pre-commit-Hooks aktivieren
make setup

# 3. Ersten Lauf starten: absichtlich verwundbares Artefakt
scripts/run-pipeline.sh workloads/01-flask-api/vulnerable
#    -> Gate bricht ab, Exit-Code 1

# 4. Denselben Code in der bereinigten Variante
scripts/run-pipeline.sh workloads/01-flask-api/fixed
#    -> Gate besteht, Exit-Code 0

# 5. Bericht ansehen
cat reports/FINDINGS_REPORT.md
```

Alle Varianten in einem Durchgang (sechs Laeufe, erzeugt den vollstaendigen
Bericht fuer die Praesentation):

```bash
make demo
```

Ohne Container-Runtime laesst sich wenigstens die Pipeline-Logik pruefen:

```bash
make test      # 11 Unit-Tests fuer Normalisierung und Gate, keine Container noetig
```

## Windows ohne `make`

Wenn `make` unter Windows nicht installiert ist, koennen die Ziele direkt
aus PowerShell oder Git Bash ausgefuehrt werden. Docker Desktop muss fuer
echte Pipeline-Laeufe gestartet sein.

PowerShell: in das Pipeline-Verzeichnis wechseln und die Python-Abhaengigkeiten
installieren beziehungsweise die Unit-Tests ausfuehren:

```powershell
cd "C:\Users\WN00235115\OneDrive - WGS 365\Documents\DHBW\Semester 5\IT Security (Graupner)\Entwurf_Pipeline\devsecops-pipeline"
python -m pip install -r .\requirements-dev.txt
python -m pytest .\tests -q
```

Die Pipeline selbst besteht aus Bash-Skripten. Deshalb die folgenden Befehle
in Git Bash oder WSL ausfuehren:

```bash
cd "/mnt/c/Users/WN00235115/OneDrive - WGS 365/Documents/DHBW/Semester 5/IT Security (Graupner)/Entwurf_Pipeline/devsecops-pipeline"

# make scan WORKLOAD=workloads/01-flask-api/vulnerable
bash scripts/run-pipeline.sh workloads/01-flask-api/vulnerable

# make scan WORKLOAD=workloads/01-flask-api/fixed
bash scripts/run-pipeline.sh workloads/01-flask-api/fixed
```

Der Lauf mit `vulnerable` soll das Gate mit Exit-Code `1` abbrechen. Der Lauf
mit `fixed` soll mit Exit-Code `0` bestehen. Die sechs Laeufe von `make demo`
entsprechen diesen direkten Aufrufen:

```bash
set +e
bash scripts/run-pipeline.sh workloads/01-flask-api/vulnerable
bash scripts/run-pipeline.sh workloads/02-cli-deps/vulnerable
bash scripts/run-pipeline.sh workloads/03-container-service/vulnerable
set -e

bash scripts/run-pipeline.sh workloads/01-flask-api/fixed
bash scripts/run-pipeline.sh workloads/02-cli-deps/fixed
bash scripts/run-pipeline.sh workloads/03-container-service/fixed
```

Weitere `make`-Ersatzbefehle:

```powershell
# make report
python .\scripts\report.py
Get-Content .\reports\FINDINGS_REPORT.md
```

```bash
# make tooling-up
docker compose -f infra/docker-compose.tooling.yml up -d

# make tooling-down
docker compose -f infra/docker-compose.tooling.yml down -v

# make clean
rm -rf reports/*/ reports/FINDINGS_REPORT.md reports/metrics.csv
```

## Die neun Stages

| Stage | Tool | Testklasse | Gate |
|---|---|---|---|
| 0 pre-commit | Gitleaks, Semgrep, hadolint | lokal | blockiert den Commit |
| 1 secrets | Gitleaks | secrets | blockt immer |
| 2 sast | Semgrep, Bandit | sast | blockt ab HIGH |
| 3 sca | Trivy fs, Syft (SBOM) | sca | blockt ab CRITICAL |
| 4 build | hadolint, Image-Build | image | blockt bei Build-Fehler |
| 5 image-scan | Trivy image, Dockle | image | blockt ab HIGH |
| 6 deploy-test | ephemere Testinstanz | - | blockt bei Healthcheck-Fehler |
| 7 dast | OWASP ZAP Baseline | dast | nur Warnung |
| 8 report | collect, gate, report | alle | finale Entscheidung |
| 9 publish | Registry-Push, SBOM | - | laeuft nur bei gruenem Gate |

Nach Stage 3 greift ein Vorab-Gate: wenn die billigen Scans schon blockieren,
werden Build, Deploy und DAST uebersprungen (Fail Fast, Fail Cheap).

## Projektstruktur

```
.
|-- .gitlab-ci.yml               CI-Definition (automatischer Trigger)
|-- .github/workflows/           Fast-Gates als GitHub-Actions-Alternative
|-- .pre-commit-config.yaml      Stage 0, Shift Left
|-- .gitleaks.toml               Secret-Scan-Regeln
|-- Makefile                     alle Einstiegspunkte
|-- policy/
|   |-- thresholds.yaml          Gate-Policy als Daten, nicht als Code
|   |-- suppressions.json        befristete Ausnahmen mit Begruendung
|   `-- gate.rego                optionale OPA/Conftest-Variante
|-- scripts/
|   |-- run-pipeline.sh          lokaler Orchestrator aller neun Stages
|   |-- stages/0X_*.sh           je Stage ein Skript
|   |-- normalize.py             Tool-Output -> gemeinsames Finding-Modell
|   |-- collect.py               Rohreports eines Laufs zusammenfuehren
|   |-- gate.py                  Policy-Auswertung, Exit-Code 0/1
|   |-- report.py                Markdown-Bericht und Metriken
|   `-- defectdojo_import.py     optionale zentrale Findings-Verwaltung
|-- workloads/                   drei Demo-Artefakte, je vulnerable und fixed
|-- infra/                       Tooling-Zone: Gitea, Vault, DefectDojo, Registry
|-- tests/                       Unit-Tests der Pipeline-Logik
`-- docs/
    |-- DEVELOPMENT.md           Entwicklungsdokumentation
    `-- DEMO_SCRIPT.md           Drehbuch fuer die 15 Minuten
```

## Konfiguration

Alles ueber Umgebungsvariablen, keine Datei muss editiert werden:

| Variable | Bedeutung | Standard |
|---|---|---|
| `CONTAINER_RUNTIME` | docker oder podman | automatisch erkannt |
| `REGISTRY` | Ziel fuer Stage 9; leer = kein Push | leer |
| `TEST_API_TOKEN` | Secret fuer die Testinstanz | Platzhalter |
| `DEFECTDOJO_URL` / `DEFECTDOJO_TOKEN` | aktiviert den Findings-Import | leer |
| `IMG_*` | Ueberschreiben einzelner Tool-Images | gepinnte Versionen |

Die Schwellwerte stehen in `policy/thresholds.yaml`. Eine Aenderung der
Risikobereitschaft ist eine Datenaenderung, kein Pipeline-Umbau.

## Ergebnisse eines Laufs

```
reports/
|-- <run-id>/raw/           unveraenderte Tool-Reports (SARIF, JSON, HTML)
|-- <run-id>/findings.json  normalisierte Findings
|-- <run-id>/gate.json      Gate-Entscheidung
|-- <run-id>/timings.json   Laufzeit je Stage
|-- FINDINGS_REPORT.md      Bericht ueber alle Laeufe
`-- metrics.csv             Metriken fuer Auswertung und Diagramme
```

Im Repository liegt bereits ein Beispiellauf unter
`reports/20261014-101500-demo-dryrun/`, erzeugt aus den Test-Fixtures. So ist
der Berichtsaufbau sichtbar, bevor der erste echte Lauf gestartet wurde.

## Sicherheitshinweise

- Die Artefakte unter `workloads/*/vulnerable/` enthalten absichtlich
  Schwachstellen und Platzhalter-Secrets. Nichts davon gehoert in ein echtes
  Projekt, und die Secrets sind erfundene Beispielwerte.
- Die Datei `workloads/03-container-service/vulnerable/.env` ist absichtlich
  Teil des Gitleaks-Demos. Sie enthaelt ausschliesslich kuenstliche Werte, die
  keine Verbindung zu einem echten Dienst herstellen. Niemals echte
  Zugangsdaten oder Produktions-URLs in diese Datei eintragen oder in Git
  committen. Fuer eigene Experimente die Werte lokal durch Testwerte ersetzen
  und nach dem Lauf wieder entfernen.
- Der DAST-Scan laeuft ausschliesslich gegen die selbst gestartete, ephemere
  Testinstanz in einem isolierten Netzwerk. Niemals gegen fremde Systeme.
- Die Tooling-Zone bindet alle Ports an `127.0.0.1`. Passwoerter kommen aus
  Umgebungsvariablen, nicht aus der Compose-Datei.

## Lizenz und Herkunft

Lehrprojekt. Die eingesetzten Werkzeuge stehen unter ihren jeweiligen
Open-Source-Lizenzen; dieses Repository enthaelt nur Konfiguration, Skripte
und Demo-Code.
