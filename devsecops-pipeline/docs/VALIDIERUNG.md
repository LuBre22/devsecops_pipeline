# Validierung der DevSecOps-Pipeline

> Historische Erstprüfung. Die nachfolgenden Befunde wurden anschließend korrigiert; aktuelle Ergebnisse und verbleibende Grenzen stehen in [NACHPRUEFUNG.md](NACHPRUEFUNG.md).

Stand: 21.10.2026 (Europe/Berlin). Geprüfter Commit: `63ff468f54079987ad6169c8b02b857fbe323bec` mit dem vorhandenen lokalen Arbeitsstand.

## Ergebnis

Die Grundidee und die Scanner-Integration funktionieren. Die Pipeline ist im geprüften Zustand aber noch nicht zuverlässig für die Abgabe und die angekündigte Vorher/Nachher-Demo: Die Automatisierung ist in der aktuellen Repository-Struktur nicht korrekt angeschlossen, Scanner-Ausfälle können erfolgreich enden, und bereinigte Varianten scheitern an aktuellen Findings.

Die ursprünglichen Pipeline-Dateien wurden bei dieser Prüfung nicht verändert. Die sechs echten Läufe erfolgten mit einer separaten Kopie der unveränderten Implementierung in einem Linux-Runner mit Zugriff auf Docker Desktop. Registry-Publishing und DefectDojo-Import waren nicht aktiviert. Die vorher vorhandene Löschung von `Entwicklungsdokumentation_DevSecOps.md` blieb unverändert.

## Abgleich mit der Prüfungsaufgabe

| Vorgabe | Bewertung am Ende der Prüfung |
|---|---|
| Kleine DevSecOps-Pipeline aufbauen | Umgesetzt; Gates haben aber bestätigte Fehler in der Fehlerbehandlung. |
| Mindestens vier Tools nutzen | Erfüllt durch echte Ausführung von Gitleaks, Semgrep, Bandit, Trivy und Syft. Für Container zusätzlich hadolint und Dockle. |
| Security-Tools automatisch auslösen | Konfiguration vorhanden, in der tatsächlichen Git-Struktur nicht funktionsfähig angeschlossen; kein echter Push-Lauf nachgewiesen. |
| Mindestens drei verschiedene Programme durchlaufen lassen | In dieser Validierung erstmals für alle drei Programme plus beide Varianten mit echten Scannern belegt. |
| Code muss lauffähig sein | Die beiden bereinigten Webdienste gebaut, gestartet und mit HTTP 200 geprüft. Bereinigte CLI funktional geprüft; verwundbare CLI hat einen nachgewiesenen Abhängigkeitskonflikt. |
| Ergebnisse und Findings dokumentieren | Vorher nur Fixture-Beispiel; jetzt echte Berichte und Rohdaten unter `docs/validation/2026-10-21/`. Manuelle Bewertung wichtiger Findings noch vervollständigen. |
| 15 Minuten Präsentation/Demo | Noch nicht erstellt, ausdrücklich außerhalb dieser Prüfung. Das vorhandene Drehbuch setzt grüne Fixed-Läufe voraus, die aktuell nicht durchgehend eintreten. |

## Echte Pipeline-Läufe

| Programm | Variante | Exit-Code | Findings | Blockierend | Letzter Entscheidungspunkt | Dauer (s) |
|---|---|---|---|---|---|---|
| 01-flask-api | vulnerable | 1 | 35 | 7 | Vorab-Gate | 139.7 |
| 01-flask-api | fixed | 1 | 309 | 49 | Image-Gate | 177.8 |
| 02-cli-deps | vulnerable | 1 | 41 | 5 | Vorab-Gate | 68.7 |
| 02-cli-deps | fixed | 1 | 19 | 1 | Vorab-Gate | 125.0 |
| 03-container-service | vulnerable | 1 | 15 | 9 | Vorab-Gate | 107.8 |
| 03-container-service | fixed | 0 | 6 | 0 | Ende | 565.1 |

Die Zahlen sind normalisierte Scanner-Meldungen gemäß eurer Implementierung. Sie sind keine Aussage darüber, dass jede CVE im konkreten Programm ausnutzbar ist. Gleichartige Meldungen unterschiedlicher Tools können weiterhin mehrfach auftreten. Laufzeiten enthalten Downloads und Datenbankinitialisierung; sie sind keine warmen Benchmark-Zeiten. Run-IDs in den Container-Berichten verwenden UTC.

Die Resultate und alle Rohreports sind in [evidence.zip](validation/2026-10-21/evidence.zip) gesichert. Der [echte Findings-Bericht](validation/2026-10-21/FINDINGS_REPORT.md), die [Metriken](validation/2026-10-21/metrics.csv) und die [kompakte Ergebnisdatei](validation/2026-10-21/results.json) gehören zu diesen Läufen, nicht zum bisherigen Beispielbericht.

## Bestätigte Probleme und Korrekturen

### 1. Automatisierung liegt außerhalb des Repository-Stammverzeichnisses – hoch

Das Git-Repository liegt in `Entwurf_Pipeline/`, die Implementierung noch eine Ebene tiefer in `devsecops-pipeline/`. GitHub findet `.github/workflows/devsecops.yml` daher nicht automatisch. GitLab erwartet standardmäßig `.gitlab-ci.yml` am Repository-Stamm. Ein separat eingestellter GitLab-Konfigurationspfad ist lokal nicht nachgewiesen; selbst dann arbeiten die vorhandenen Skriptpfade ohne zusätzlichen Verzeichniswechsel vom falschen Verzeichnis aus.

Auch `.pre-commit-config.yaml` liegt nicht am Git-Stamm. `make setup` installiert den Hook ohne expliziten Konfigurationspfad. Der lokale History-Scan prüft `ROOT/.git`, obwohl `.git` tatsächlich im übergeordneten Verzeichnis liegt; er wird damit übersprungen.

**Korrektur:** Einen tatsächlichen Einstieg am Git-Stamm einrichten, Arbeitsverzeichnis und Artefaktpfade konsistent auf `devsecops-pipeline` ausrichten und den Hook ausdrücklich mit der verschachtelten Konfiguration installieren. Git-Stamm mit `git rev-parse --show-toplevel` ermitteln. Danach einen echten Push und dessen automatisch gestarteten Lauf belegen. Allein das Verschieben der CI-Datei reicht wegen der relativen Pfade nicht.

Grundlage: [GitHub – Workflow-Erkennung](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows) und [GitLab – Konfigurationspfad](https://docs.gitlab.com/ci/pipelines/settings/).

### 2. Komplett ausgefallene Scanner ergeben eine erfolgreiche Pipeline – kritisch

`scripts/collect.py` überspringt fehlende Rohreports. `scripts/normalize.py` behandelt leere oder ungültige JSON-Dateien wie null Findings. `scripts/gate.py` wertet ausschließlich Findings aus; erfolgreiche Pflichtscanner werden nicht verlangt. Die Stage-Skripte fangen technische Fehler vielfach mit Warnungen ab.

**Reproduktion über den vollständigen Orchestrator:** `CONTAINER_RUNTIME=false bash scripts/run-pipeline.sh workloads/02-cli-deps/fixed`. Alle Container-Kommandos scheitern. Trotzdem werden null Findings gemeldet, das Gate besteht und der Prozess liefert Exit-Code **0**. Siehe `logs/all-scanners-failed.log` im Archiv.

**Korrektur:** Scannerstatus und Findingstatus getrennt erfassen. Pro Phase erwartete Pflichtreports mit gültigem Schema und erfolgreichem Scannerlauf verlangen. Fehlender oder beschädigter Pflichtreport muss einen technischen Fehler liefern; null Findings sind nur nach erfolgreichem Scan ein grünes Ergebnis. Dasselbe gilt für CI-`allow_failure` und `continue-on-error`.

### 3. Bereinigte Varianten sind aktuell nicht durchgehend grün – hoch

Die bereinigte Flask-API besteht das Vorab-Gate und funktioniert als Programm, scheitert aber am Image-Gate mit **49 blockierenden Findings**: 48 HIGH-Meldungen aus dem Trivy-Image-Scan und eine durch Dockle als FATAL bewertete Regel. Das heruntergeladene `python:3.12-slim` basiert bei dieser Prüfung auf Debian 13.7; ein bewegliches Tag liefert nicht dauerhaft denselben Inhalt.

Das Dockle-Finding `DKL-DI-0005` bezieht sich auf eine geerbte Basis-Image-Schicht mit `apt-get dist-clean`. Die direkte Gegenprüfung findet keine Dateien in `/var/lib/apt/lists` und nur die Lockdatei in `/var/cache/apt`. Das ist ein begründeter Fehlalarmkandidat des älteren Scanners; eine pauschale Unterdrückung aller Image-Findings wäre fachlich falsch. Auch ohne diese Meldung bleiben die 48 HIGH-Meldungen blockierend.

Die bereinigte CLI scheitert an einem CRITICAL-Finding für `certifi==2024.8.30` (`GHSA-6q48-6c7w-9gw2`). Der Scanner nennt `2026.10.19` als Fix-Version. Maßgeblich sind die im Archiv enthaltenen Rohdaten und ihre anschließende Bewertung.

**Korrektur:** Abhängigkeiten und Basis-Images gezielt aktualisieren, wichtige Findings auf tatsächliche Betroffenheit prüfen und berechtigte Ausnahmen eng, begründet und befristet dokumentieren. Danach alle Varianten erneut ausführen. Die README-Zusagen `fixed -> 0` und das Demo-Drehbuch erst dann als bestätigt darstellen. `make demo` bricht derzeit bereits beim ersten Fixed-Lauf ab, wodurch weitere Fixed-Beispiele nicht mehr ausgeführt werden.

### 4. Verwundbare CLI ist mit ihren Anforderungen nicht installierbar – hoch

`workloads/02-cli-deps/vulnerable/requirements.txt` fordert `requests==2.19.1` und `urllib3==1.24.1`. Requests 2.19.1 verlangt aber `urllib3>=1.21.1,<1.24`. Ein echter pip-Probelauf endet mit `ResolutionImpossible`; er installiert nichts. Log: `logs/cli-vulnerable-resolver.log`.

Die Pipeline scannt diese Requirements lediglich. Weil kein Dockerfile vorhanden ist, werden Build, Start und DAST übersprungen; die CLI wird auch sonst nicht ausgeführt. Ein erfolgreicher Scan beweist daher nicht die geforderte Lauffähigkeit.

**Korrektur:** Einen absichtlich verwundbaren, aber miteinander kompatiblen Abhängigkeitssatz und eine passende Python-Version festlegen. Beide CLI-Varianten in isolierten Umgebungen installieren und `main.py --config config.yaml` als Funktionstest starten.

### 5. Deduplizierung kann eine strengere Image-Policy umgehen – hoch

Die ID für Trivy-CVEs in `scripts/normalize.py` enthält CVE, Paket und Version, aber weder Testklasse noch Scan-Kontext. `dedupe()` behält bei gleicher Severity den zuerst eingelesenen Fund. `collect.py` liest den Dateisystembericht vor dem Imagebericht.

Ein identisches HIGH-Finding aus SCA und Image bleibt dadurch nur als `sca` erhalten: Die Policy warnt, obwohl dasselbe Finding im Image blockieren müsste. Ein zusätzlicher Akzeptanztest reproduziert das.

**Korrektur:** Scan-Kontexte erhalten oder sämtliche Gate-relevanten Bewertungen zusammenführen und die strengste Aktion verwenden. Den Fall unterschiedlicher Testklassen ausdrücklich als Regressionstest behalten.

### 6. GitLab-Jobabhängigkeiten umgehen das Image-Gate bzw. brechen bei der CLI – hoch

Der Job `dast` hat ausschließlich `needs: [build-image]`. Er wartet deshalb nicht auf `image-scan` und `image-gate`; die Stage-Reihenfolge allein schützt bei `needs` nicht. Das widerspricht der behaupteten Reihenfolge „Image prüfen, erst danach starten“.

Für Workload 2 wird `build-image` wegen des fehlenden Dockerfiles per `rules:exists` nicht angelegt. Die Jobs `image-scan`, `image-gate` und `dast` benötigen diesen Job trotzdem ohne passende Regeln oder optionale Abhängigkeit. Nach den dokumentierten GitLab-Regeln verhindert eine solche Konstellation die Pipeline-Erstellung. Das ist eine statische Prüfung der Definition; ein GitLab-Serverlauf wurde nicht ausgelöst.

**Korrektur:** DAST explizit von einem erfolgreichen Image-Gate abhängig machen. Containerjobs einschließlich Publish konsistent nur für Container-Workloads anlegen. Eine CLI braucht einen eigenen Installations- und Ausführungspfad. [GitLab dokumentiert die Wirkung von `needs` und optionalen Jobs.](https://docs.gitlab.com/ci/yaml/needs/)

### 7. Der GitHub-Secret-Scan blendet die Demo-Secrets aus – hoch

Der GitHub-Workflow verwendet nur den Repository-/History-Scan mit `.gitleaks.toml`. Diese Datei erlaubt pauschal `workloads/.*/vulnerable/.*`; dort liegen gerade die beabsichtigten Test-Secrets. Im Gegensatz zur GitLab-Definition und zum lokalen Workload-Scan fehlt im GitHub-Workflow ein separater Scan mit `.gitleaks-workload.toml`.

**Korrektur:** Bewusste Demo-Ausnahmen im Repository-Scan klar vom nicht ausgenommenen Scan des ausgewählten Workloads trennen. Mit Workload 3 prüfen, dass Gitleaks selbst die Secrets meldet. Der Workflow prüft zudem standardmäßig nur Workload 1; weitere Programme benötigen eine Matrix oder dokumentierte Variantenläufe.

### 8. Linux-Einstiege, Healthcheck und Berichtsstatus sind inkonsistent – mittel bis hoch

- Alle `.sh`-Dateien sind im Git-Index als **100644** gespeichert. `make scan`, `make demo` und mehrere dokumentierte Befehle starten `scripts/run-pipeline.sh` direkt. In einem frischen Linux-Checkout fehlt dafür das Ausführungsrecht. Die Validierung verwendet deshalb ausdrücklich `bash scripts/run-pipeline.sh`. Korrektur: ausführbar versionieren oder Aufrufe durchgehend mit `bash` starten.
- Der lokale Orchestrator ruft `06_deploy_test.sh` als **optional** auf. Ein fehlgeschlagener Healthcheck kann so trotz gegenteiliger README-Aussage grün enden. Auch Publish-Fehler werden als optional behandelt. Pflichtschritte müssen den Gesamtstatus beeinflussen.
- Der GitHub-Workflow erzeugt den Bericht **vor** `gate.py`. `report.py` stellt einen noch nicht vorhandenen Gateentscheid als FAIL dar. Ergebnisdatei zuerst schreiben, dann den Bericht auch nach einer Gateablehnung erzeugen; „nicht ausgewertet“ braucht einen eigenen Status.

### 9. Suppressions ohne Ablaufdatum werden dauerhaft akzeptiert – mittel

`load_suppressions()` prüft ein Ablaufdatum nur, wenn es existiert. Ein Eintrag mit Finding-ID, Owner und Begründung bleibt ohne `expires_at` dauerhaft aktiv. Der zusätzliche Test bestätigt den Widerspruch zur Dokumentation.

**Korrektur:** Ein gültiges Ablaufdatum für jede Ausnahme verlangen, fehlerhafte Einträge kontrolliert ablehnen und fehlende, abgelaufene sowie aktive Einträge testen.

### 10. Vorhandene Ergebnisdokumentation und Offline-Zusagen sind nicht belastbar – mittel

Alle fünf Rohreports in `reports/example-run/raw` sind bytegleich mit `tests/fixtures`. Der Beispielbericht mischt etwa PyYAML-Findings aus der CLI mit dem Workloadnamen der Flask-API, enthält erfundene Beispiel-Commitwerte und feste Zeitwerte. Er darf nicht als tatsächlicher Lauf oder Laufzeitmessung vorgestellt werden. Die README beschreibt ebenfalls einen Fixture-Dryrun, nennt dafür aber ein anderes Verzeichnis. Die echte Prüfung ist nun separat archiviert.

Für eine Bewertung wichtiger Findings fehlen bisher ausgefüllte True-/False-Positive-Angaben und konkrete Lessons Learned. ZAP Baseline ist ein Spider mit passivem Scan; das Fixture mit einem aktiv erkannten Reflected-XSS-Fund beweist daher keinen solchen Fund des konfigurierten Baseline-Laufs. [Offizielle Beschreibung des ZAP-Baseline-Scans.](https://www.zaproxy.org/docs/docker/baseline-scan/)

Der echte ZAP-Lauf der bereinigten Container-Variante wird ausgeführt und liefert drei Alerts. Sein Spider meldet jedoch HTTP 404 für den Startpfad; `/health` und `/file` werden nicht als gezielte Scan-Endpunkte vorgegeben. Ein grünes Ergebnis belegt deshalb keinen vollständigen dynamischen Test dieser Schnittstellen. Zusätzlich erzeugt `parse_zap()` durch Verkettung von Host und bereits absoluter URI fehlerhafte Fundorte wie `http://host:8080http://host:8080/robots.txt`. Korrektur: gezielte Endpoint-/OpenAPI-Vorgaben und Normalisierung mit absoluter URI bzw. URL-Auflösung. ZAP meldet außerdem seine veraltete eigene Version; der alte Scannerstand sollte vor einer weiteren Demo überprüft werden.

Ein Offline-Lauf ist mit der vorhandenen Konfiguration nicht zuverlässig: Bandit wird in jedem frischen Container über pip installiert, Semgrep lädt Regelpakete und Trivy verwendet ohne persistentes Volume pro Scan eine neue Datenbank. Im Test wurde die Datenbank wiederholt heruntergeladen. Tags wie `python:3.12-slim`, `alpine:3.20` und Registry-Regelpakete sind trotz Versionsangaben beweglich. Für eine Demo besser vorab vollständige Läufe und ein Video sichern; für Reproduzierbarkeit Image-Digests, Regelstände und Caches festhalten.

## Durchgeführte Prüfungen und Grenzen

| Prüfung | Ergebnis |
|---|---|
| Vorhandene 11 Unit-Tests unter Windows / Python 3.12.14 | 11 bestanden |
| Dieselben Tests im Linux-Runner / Python 3.12.13 | 11 bestanden |
| 9 zusätzliche Akzeptanztests | 5 bestanden, 4 fehlgeschlagen: fehlender Bericht, beschädigter Bericht, Deduplizierung über Testklassen, fehlendes Suppression-Ablaufdatum |
| Bandit-SARIF gegen echten Bandit-Output | HIGH bleibt korrekt HIGH; kein Severity-Verlust in diesem geprüften Fall |
| Flask-Funktionstests beider Varianten | Health, normale SQL-Abfrage, SQL-Injection-Vergleich, XSS-Vergleich und Hash-Endpunkt bestanden; ungültige Ping-Adresse und Header der Fixed-Variante geprüft |
| Bereinigte CLI | `main.py` in isolierter Testumgebung erfolgreich ausgeführt; kein Beleg für die Installation jeder exakt gepinnten Zusatzabhängigkeit |
| Pfadbegrenzung des bereinigten Statusdienstes | Zugriff innerhalb des Datenverzeichnisses erlaubt, Traversal abgelehnt |
| Container-Build und HTTP-Smoke-Test beider Fixed-Webdienste | Beide Builds erfolgreich, beide `/health` mit HTTP 200; Flask `/ping` ebenfalls HTTP 200 |
| Vollständiger Scanner-Ausfall | Fehler nachgewiesen: Pipeline endet trotzdem mit 0 |
| Bash-Syntax aller Pipeline-Skripte | `bash -n` erfolgreich |
| Python- und YAML-Syntax | Alle 12 Python-Dateien und fünf zentrale YAML-Konfigurationen erfolgreich geparst; kein Ersatz für serverseitige CI-Validierung |
| Tooling-Compose | `docker compose ... config --quiet` erfolgreich; Dienste nicht gestartet |
| Verwundbare CLI-Dependencies | Versionskonflikt durch pip-Probelauf bestätigt |

Die zusätzlichen Tests liegen unter [test_validation.py](validation/2026-10-21/test_validation.py). Die bewusst roten Akzeptanztests beschreiben erwartetes robustes Verhalten; sie wurden zusätzlich zur bestehenden Testsuite ausgeführt. Testskripte, Container-Runner und Logs sind ebenfalls im Ergebnisordner bzw. Archiv enthalten.

Nicht nachgewiesen: ein tatsächlicher CI-Push-Trigger, GitLab-Runner/DinD-Konfiguration, Registry-Publishing, Vault-Injektion und DefectDojo-Betrieb/Import. Diese optionalen Integrationen sind keine Voraussetzung für die geforderten vier Security-Tools, sollten aber in der Präsentation nur bei echtem Nachweis als funktionierend bezeichnet werden. Das ursprüngliche Repository und dessen vorhandene Berichte wurden durch die Ausführung nicht überschrieben. Die erzeugten lokalen Testimages und die isolierte Arbeitsumgebung liegen weiterhin auf diesem Rechner.

## Reihenfolge bis zur abgabefähigen Pipeline

1. CI-Einstieg und Arbeitsverzeichnis korrigieren und einen automatischen Lauf belegen.
2. Pflichtscanner, technische Fehler und Healthchecks korrekt auf den Gesamtstatus abbilden.
3. Deduplizierung und Suppression-Validierung korrigieren, zusätzliche Tests grün bekommen.
4. Dependencies und Basis-Images überarbeiten, CLI ausführbar machen, legitime Ausnahmen dokumentieren.
5. Alle sechs Varianten neu ausführen; verwundbar muss nachvollziehbar rot, bereinigt begründet grün sein. Ausgelassene Stages sichtbar dokumentieren.
6. Echte Rohreports, Gateentscheidungen, Findingsbewertung und Demoaufzeichnung sichern; daraus anschließend die Präsentation erstellen.
