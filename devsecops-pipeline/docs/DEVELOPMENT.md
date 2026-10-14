# Entwicklungsdokumentation

Begleitdokument zur Implementierung der DevSecOps-Pipeline. Es haelt fest, was
gebaut wurde, welche Entscheidungen dabei getroffen wurden und wo die Grenzen
der Loesung liegen.

---

## 1. Vorgehen

Implementiert wurde in der Reihenfolge, in der das Risiko am schnellsten sinkt:

1. **Finding-Modell und Gate zuerst.** Vor dem ersten Scanner entstand
   `normalize.py` samt Datenmodell und `gate.py`. Grund: solange unklar ist,
   wie ein Finding aussieht, ist jede Tool-Integration eine Wette.
2. **Unit-Tests gegen Fixtures.** Echte Tool-Ausgaben aus Semgrep, Trivy,
   Gitleaks, ZAP und Dockle liegen als Fixtures in `tests/fixtures/`. Damit ist
   die gesamte Pipeline-Logik ohne Container testbar - `make test` laeuft in
   unter einer Sekunde.
3. **Stages als einzelne Skripte.** Jede Stage ist ein eigenes Shell-Skript mit
   gemeinsamer Bibliothek `_common.sh`. Der Orchestrator ruft sie nur auf, die
   CI-Definition ruft dieselbe Logik auf. Dadurch gibt es keine zwei Wahrheiten.
4. **Demo-Workloads mit Negativ- und Positivfall.** Erst danach wurden die drei
   Artefakte gebaut, jeweils als `vulnerable` und `fixed`.
5. **CI-Anbindung zuletzt**, weil sie nur noch Verpackung ist.

## 2. Architekturentscheidungen in der Umsetzung

| ID | Entscheidung | Begruendung |
|---|---|---|
| ID-1 | Tool-Exit-Codes werden ignoriert (`--exit-code 0`), das Gate entscheidet | Sonst bestimmt jedes Tool die eigene Blockregel und die Policy ist wirkungslos |
| ID-2 | Gemeinsames Finding-Modell statt direkter Tool-Auswertung | Tool-Tausch ohne Pipeline-Umbau (NF-05); erfuellt am Beispiel Dockle, das nachtraeglich ergaenzt wurde |
| ID-3 | Policy in `thresholds.yaml`, nicht im Skript | Risikobereitschaft ist eine fachliche, keine technische Entscheidung |
| ID-4 | Eigener YAML-Minimalparser als Fallback | Das Gate laeuft dadurch in jedem `python:3.12-slim` ohne zusaetzliche Abhaengigkeit |
| ID-5 | Vorab-Gate nach Stage 3 | Build, Deploy und DAST kosten ein Vielfaches der statischen Scans |
| ID-6 | Scanner-Container ohne Netzwerk, ausser wo Regelfeeds noetig sind | Ein Scanner braucht keinen Internetzugang zum Quellcode |
| ID-7 | Suppressions mit Ablaufdatum und Pflichtbegruendung | Eine Ausnahme ohne Verfallsdatum ist eine stille Risikoakzeptanz |
| ID-8 | Stage 8 laeuft immer (`when: always`) | Nach einem Fehlschlag sind die Findings besonders wertvoll |
| ID-9 | Alle Tool-Images mit exakter Version gepinnt | Reproduzierbarkeit; ein `:latest` macht Ergebnisse zwischen Laeufen unvergleichbar |

## 3. Komponenten im Detail

### scripts/normalize.py
Parser fuer fuenf Reportformate (SARIF, Gitleaks-JSON, Trivy-JSON, ZAP-JSON,
Dockle-JSON) und die Abbildung aller Tool-Severities auf eine gemeinsame
Leiter `INFO < LOW < MEDIUM < HIGH < CRITICAL`.

Besonderheiten:
- SARIF legt die Severity teils auf dem Ergebnis, teils auf der Regel ab.
  Semgrep nutzt die Regelvariante, deshalb werden beide Quellen ausgewertet.
- Gitleaks kennt keine Severity. Jeder Treffer wird auf CRITICAL gesetzt, weil
  ein geleaktes Credential unabhaengig von der Regel rotiert werden muss.
- ZAP liefert numerische Risikocodes (0-3), die ebenfalls gemappt werden.
- Trivy-Secrets landen in der Testklasse `secrets`, nicht `image`: ein Secret
  in einem Layer ist ein Secret-Problem.
- `dedupe()` fasst identische Findings zusammen und behaelt die hoechste
  Severity. Ohne das erscheint derselbe CVE mehrfach, wenn Trivy ihn im
  Dateisystem und im Image findet.

### scripts/gate.py
Liest `findings.json`, laedt Policy und Suppressions, bestimmt pro Finding die
Aktion und setzt den Exit-Code. Kein Finding wird stillschweigend verworfen:
unterdrueckte und abgelaufene Ausnahmen werden protokolliert.

Fallback-Logik: ist fuer eine Testklasse keine Severity-Regel definiert, wird
die naechstniedrigere definierte Regel verwendet, danach `gates.default`. Eine
neue Testklasse kann also nie versehentlich ungeprueft durchlaufen.

### scripts/collect.py und report.py
`collect.py` fuehrt alle Rohreports eines Laufs zusammen und ergaenzt
Commit-Hash, Branch und SBOM-Komponentenzahl. `report.py` erzeugt daraus
`FINDINGS_REPORT.md` (Uebersicht, Severity-Matrix, Detailtabelle, Laufzeiten,
Vorlage fuer die False-Positive-Bewertung) und `metrics.csv`.

Die False-Positive-Spalten bleiben absichtlich leer: diese Bewertung ist
Handarbeit und soll nicht automatisiert wirken.

## 4. Begruendung der Gate-Schwellwerte

| Testklasse | Regel | Begruendung |
|---|---|---|
| secrets | jeder Treffer blockt | Ein Credential im Repository ist kompromittiert, sobald es dort liegt |
| sast | ab HIGH blockt | Der Fundort ist bekannt und der Fix liegt im eigenen Code |
| sca | erst ab CRITICAL blockt | Viele Abhaengigkeits-CVEs betreffen nicht genutzte Codepfade; HIGH warnt und wird triagiert |
| image | ab HIGH blockt | Basis-Image-CVEs sind meist durch einen Versionssprung behebbar |
| dast | nur Warnung | Baseline-Scans haben eine hohe Falsch-Positiv-Rate, ein Build-Abbruch darauf verliert Akzeptanz |

## 5. Probleme waehrend der Entwicklung

| Problem | Ursache | Loesung |
|---|---|---|
| Doppelte Findings im Bericht | Trivy meldet denselben CVE im Dateisystem- und im Image-Scan | Deduplizierung ueber eine stabile Finding-ID |
| Semgrep-Findings ohne Severity | Severity steht in SARIF auf der Regel, nicht am Ergebnis | Regeltabelle aus `tool.driver.rules` auswerten |
| Gate meldete "bestanden" trotz Fehlern | Fehlende Reportdateien wurden als leer interpretiert | Jeder Lauf protokolliert die beteiligten Tools; ein fehlender Report wird auf stderr sichtbar gemacht |
| ZAP schrieb nicht in das Reportverzeichnis | ZAP schreibt nach `/zap/wrk` | Verzeichnis gezielt dorthin gemountet |
| Pipeline brach vor dem Bericht ab | Stage 8 wurde nach einem Fehlschlag nie erreicht | `when: always` in der CI und ein Fehlerpfad im Orchestrator |
| Policy-Parsing scheiterte im Slim-Image | PyYAML ist dort nicht vorhanden | Minimalparser als Fallback, per Test gegen PyYAML abgeglichen |

## 6. Teststand

Nach `make setup` fuehrt `make test` elf Tests aus:
Gate-Verhalten je Testklasse (inklusive der Faelle "Secret blockt immer" und
"DAST blockt nie"), Severity-Mapping fuer SARIF, Trivy und Gitleaks,
Deduplizierung, Umgang mit fehlenden Reports und Behandlung von
Falsch-Positiv-Markierungen. Alle elf laufen gruen.

Nicht automatisiert getestet: die Container-Stages selbst. Dafuer dient der
Lauf `make demo`, dessen Ergebnis im Findings-Report dokumentiert ist. Der
allererste Lauf braucht Zugriff auf die fest gepinnten Container-Images und
Scanner-Regeldatenbanken; danach koennen Images und Caches lokal genutzt
werden. "Lokal reproduzierbar" bedeutet nicht "erstmals vollstaendig offline".

## 7. Grenzen der Umsetzung

- **Keine Laufzeitsicherheit.** Werkzeuge der Klasse NeuVector oder Twistlock
  fehlen; die Pipeline prueft vor dem Deployment, nicht im Betrieb. Genau
  davor warnt die Vorlesung bei reinen Pre-Deployment-Scans.
- **Kein IAST, kein echter Penetrationstest.** Beides wurde im Scope
  ausgeschlossen.
- **DAST nur als Baseline-Scan.** Kein authentifizierter Scan, keine
  Spider-Konfiguration pro Anwendung.
- **Vault im Dev-Modus.** Kein Unsealing, kein persistenter Speicher - fuer
  eine Demo richtig, fuer Produktion unbrauchbar.
- **Keine Signatur der Artefakte.** Image-Signierung und Provenance waeren der
  naechste logische Schritt in Stage 9.