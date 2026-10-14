# Demo-Drehbuch - 15 Minuten

Ziel: zeigen, dass die Pipeline automatisch ausloest, echte Findings
produziert und den Build nachweislich blockiert. Nicht das Werkzeug erklaeren,
sondern die Wirkung zeigen.

## Vorbereitung am Vortag

- [ ] Alle Tool-Images lokal vorhanden (`make demo` einmal komplett laufen lassen)
- [ ] `reports/FINDINGS_REPORT.md` aus einem vollstaendigen Lauf vorhanden
- [ ] Zwei Terminals offen: links die Pipeline, rechts der Bericht
- [ ] Screencast der beiden Laeufe als Rueckfallebene aufgenommen
- [ ] Schriftgroesse im Terminal auf Projektorgroesse gestellt
- [ ] Netzwerkunabhaengigkeit geprueft: Pipeline einmal mit getrenntem WLAN starten

## Ablauf

| Zeit | Inhalt | Wer |
|---|---|---|
| 0:00-1:30 | Aufgabe und Zielbild. Eine Folie: die neun Stages und die Zonen. | Doku |
| 1:30-3:30 | Tool-Auswahl: vier Testklassen statt vier aehnlicher Scanner. Warum Gitleaks, Semgrep, Trivy und ZAP. | Security Champion |
| 3:30-5:00 | Automatisierung zeigen: `.pre-commit-config.yaml` und den CI-Trigger in `.gitlab-ci.yml`. Kurz, nur das Trigger-Prinzip. | Ops |
| 5:00-9:30 | **Live-Demo** (siehe unten) | Developer |
| 9:30-12:00 | Findings und Metriken: Severity-Matrix, False-Positive-Quote je Tool, Laufzeit je Stage als Beleg fuer Fail Fast. | Security Champion |
| 12:00-14:00 | Lessons Learned und Grenzen: keine Laufzeitsicherheit, DAST-Falschpositive, Schwellwerte als Aushandlung. | alle |
| 14:00-15:00 | Fragen | alle |

## Live-Demo, Schritt fuer Schritt

```bash
# 1. Verwundbares Artefakt durch die Pipeline schicken
scripts/run-pipeline.sh workloads/01-flask-api/vulnerable
```

Waehrend es laeuft erklaeren: Secret-Scan zuerst, weil er Sekunden dauert.

Nach dem Abbruch zeigen:
- die Gate-Ausgabe mit den blockierenden Findings
- eine konkrete Codestelle, zum Beispiel die zusammengesetzte SQL-Abfrage
- dass Build, Deploy und DAST uebersprungen wurden (Fail Fast)

```bash
# 2. Bereinigte Variante derselben Anwendung
scripts/run-pipeline.sh workloads/01-flask-api/fixed
```

Nach dem gruenen Lauf zeigen:
- Gate bestanden, Image wird publiziert
- der Unterschied im Code, Zeile fuer Zeile: parametrisierte Abfrage,
  Escaping, kein Shell-Aufruf, Debug aus

```bash
# 3. Nachweis fuer Abhaengigkeiten und Container
scripts/run-pipeline.sh workloads/02-cli-deps/vulnerable --skip-dast
scripts/run-pipeline.sh workloads/03-container-service/vulnerable --skip-dast
```

Kernaussage dazu: Workload 2 hat sauberen Code und faellt trotzdem durch - das
Risiko steckt in den Abhaengigkeiten. Workload 3 faellt am Secret-Scan, bevor
ueberhaupt ein Image gebaut wird.

```bash
# 4. Bericht zeigen
cat reports/FINDINGS_REPORT.md
```

## Antworten auf wahrscheinliche Fragen

**Warum blockiert HIGH bei SAST, aber nicht bei SCA?**
Beim eigenen Code ist der Fundort bekannt und der Fix guenstig. Eine
Abhaengigkeits-CVE betrifft oft Codepfade, die die Anwendung nie aufruft; dort
blockiert erst CRITICAL, HIGH wird triagiert.

**Warum bricht der DAST-Scan den Build nicht ab?**
Baseline-Scans melden viele Falsch-Positive. Ein Gate darauf wird nach wenigen
Tagen umgangen, und dann ist gar nichts mehr geprueft.

**Was ist nicht abgedeckt?**
Laufzeitsicherheit im Cluster, IAST, authentifizierte Scans und
Artefaktsignierung. Die Pipeline prueft vor dem Deployment.

**Wie verhindert man, dass Ausnahmen zur Dauerloesung werden?**
Jede Suppression braucht Begruendung, Verantwortlichen und Ablaufdatum. Nach
Ablauf aktiviert das Gate das Finding automatisch wieder und protokolliert das.

## Rueckfallebene

Wenn die Container-Runtime oder das Netzwerk streikt: Screencast abspielen und
parallel `make test` live ausfuehren. Die elf Unit-Tests belegen die
Gate-Logik auch ohne Container.
