# Unsere DevSecOps-Pipeline verstehen und erklären

Diese README ist die Vorbereitung auf fachliche Rückfragen zur Abgabe. Sie erklärt den aktuellen Code: Was passiert wo, warum wurde es so umgesetzt und was belegen die Ergebnisse? Stand: 21.10.2026. Für die Bedienung gibt es zusätzlich den [Schnellstart](README.md), für die tatsächlich geprüften Ergebnisse die [Nachprüfung](docs/NACHPRUEFUNG.md).

## 1. Das Projekt in einer Minute erklären

> Wir prüfen drei kleine Python-Programme mit jeweils einer absichtlich verwundbaren und einer bereinigten Variante. Ein Push zu GitHub startet automatisch Tests und sechs Pipeline-Fälle. Die Pipeline sucht unter anderem nach Secrets, gefährlichen Codestellen, verwundbaren Abhängigkeiten und Containerproblemen. Für Webdienste folgen nach bestandenen Gates ein isolierter Start, Funktionstests und ein passiver ZAP-Scan. Die unterschiedlichen Scannerberichte werden vereinheitlicht und anhand einer versionierten Policy bewertet. Verwundbare Beispiele sollen abgelehnt werden, bereinigte Beispiele sollen die Policy bestehen. Rohdaten und Entscheidungen bleiben als Nachweise erhalten.

DevSecOps bedeutet hier: Sicherheitsprüfungen sind wiederholbarer Bestandteil des Entwicklungsablaufs. Die Gruppe muss die Ergebnisse weiterhin bewerten. Automatisierung ersetzt diese Bewertung nicht.

| Vorgabe der Aufgabe | Umsetzung im Projekt |
|---|---|
| Mindestens vier Tools | Acht Werkzeuge mit verschiedenen Aufgaben; siehe Abschnitt 3 |
| Automatisierte Security-Prüfung | GitHub Actions bei Push und Pull Request |
| Mindestens drei lauffähige Programme | Flask-API, Konfigurations-CLI und HTTP-Dateidienst; je zwei Varianten |
| Ergebnisse und Findings dokumentieren | Rohreports, normalisierte Findings, Gateentscheidung, Gesamtbericht und manuelle Bewertung |
| Ergebnisse mit Demo erklären | Positive und negative Fälle; [Demo-Ablauf](docs/DEMO_SCRIPT.md) und archivierte Nachweise |

Die Präsentationsdatei ist ein eigenes Abgabeprodukt und wird durch diese README nicht ersetzt.

## 2. Wo liegt welcher Teil?

Es gibt zwei wichtige Verzeichnisse: den **Git-Stamm** mit den CI-Konfigurationen und darunter **`devsecops-pipeline/`** mit der eigentlichen Implementierung. Alle folgenden lokalen Befehle gelten für das Projektverzeichnis `devsecops-pipeline/`, sofern nicht anders angegeben.

```text
<Git-Stamm>/
├── .github/workflows/devsecops.yml   GitHub: Trigger, Tests, sechs Matrixfälle
├── .gitlab-ci.yml                   Alternative für GitLab
├── .pre-commit-config.yaml          Optionale Prüfungen vor einem Commit
└── devsecops-pipeline/
    ├── workloads/                  Drei Programme, jeweils vulnerable/fixed
    ├── scripts/                    Orchestrierung, Auswertung und Berichte
    ├── policy/                     Regeln, Schwellenwerte, Ausnahmen, Image-Pins
    ├── infra/                      Bandit-Toolimage und optionale Entwürfe
    ├── tests/                      Tests der Pipeline- und Gate-Logik
    ├── reports/                    Ausgabe neuer lokaler Läufe
    └── docs/                       Bewertung und archivierte Nachweise
```

| Datei | Aufgabe und Grund für die Trennung |
|---|---|
| [scripts/prepare.py](scripts/prepare.py) | Bereitet Scanner-Images und Trivy-Cache vor. Downloads müssen nicht in jedem Prüfschritt neu erklärt oder eingerichtet werden. |
| [scripts/pipeline.py](scripts/pipeline.py) | Zentraler Orchestrator: legt Reihenfolge fest, startet Prozesse, prüft Reports und führt Gates aus. Lokal und in CI gilt derselbe Ablauf. |
| [scripts/collect.py](scripts/collect.py) | Ordnet Reportdateien ihren Werkzeugen und Testklassen zu, sammelt Findings und Metadaten. |
| [scripts/normalize.py](scripts/normalize.py) | Übersetzt die unterschiedlichen Scannerformate in ein gemeinsames Finding-Modell. |
| [scripts/gate.py](scripts/gate.py) | Entscheidet anhand der Policy und zulässiger Ausnahmen über PASS, FAIL oder ERROR. |
| [scripts/report.py](scripts/report.py) | Erzeugt aus den Ergebnissen einen lesbaren Gesamtbericht und CSV-Metriken. |
| [scripts/demo.py](scripts/demo.py) | Prüft, ob die vorgesehenen positiven und negativen Fälle tatsächlich eintreten. |
| [scripts/smoke.py](scripts/smoke.py) | Separater Nachweis der Lauffähigkeit, auch wenn ein verwundbarer Webdienst im normalen Ablauf früh gestoppt wird. |
| [scripts/run-pipeline.sh](scripts/run-pipeline.sh) | Dünner Bash-Einstieg, der an Python weitergibt; keine zweite Pipeline-Implementierung. |

**Warum Python?** Derselbe Einstieg funktioniert unter Windows und Linux. Der Orchestrator verwendet überwiegend die Standardbibliothek und startet Scanner in Containern. Die CI-Dateien müssen deshalb keine eigene Security-Logik duplizieren. Die YAML-Policy kann mit PyYAML gelesen werden; das Gate hat zusätzlich einen begrenzten Parser für seine einfache Mapping-Struktur, keinen allgemeinen YAML-Ersatz.

## 3. Welche Werkzeuge prüfen was?

Ein **Finding** ist zunächst eine Meldung eines Werkzeugs. Ob daraus eine Ablehnung entsteht, entscheidet die Policy. Unterschiedliche Tools betrachten unterschiedliche Teile des Systems.

| Werkzeug | Kategorie und Prüfgegenstand | Report unter `raw/` | Warum eingesetzt? |
|---|---|---|---|
| Gitleaks | Secrets im ausgewählten Quellverzeichnis und zusätzlich in der Git-Historie | `gitleaks.json`, `gitleaks-history.json` | Zugangsdaten können auch nach dem Löschen einer Datei in alten Commits liegen. |
| Semgrep | SAST: Muster und ausgewählte Datenflüsse im Quellcode | `semgrep.sarif` | Eigene, nachvollziehbare Regeln für die Demonstrationsschwachstellen. |
| Bandit | SAST mit Schwerpunkt Python | `bandit.sarif` | Ergänzende Prüfung gefährlicher Python-Aufrufe und Einstellungen. |
| Trivy | Dateisystem: Abhängigkeiten, Fehlkonfigurationen, Secrets; Image: Komponenten und Secrets | `trivy-fs.json`, `trivy-image.json` | Quellcode allein zeigt nicht die gesamte Software im fertigen Image. |
| Syft | Softwareinventar als SBOM | `sbom.cdx.json` | Dokumentiert Komponenten im CycloneDX-Format; erzeugt hier selbst keine Vulnerability-Findings. |
| hadolint | Statische Dockerfile-Prüfung | `hadolint.sarif` | Prüft die Bauanleitung des Images. |
| Dockle | Prüfung des gebauten Container-Images | `dockle.json` | Prüft Eigenschaften und Build-Historie des tatsächlich erzeugten Images. |
| OWASP ZAP | DAST am laufenden Webdienst, hier ausschließlich passiv | `zap.json`, `zap.html` | Ergänzt statische Prüfungen um Beobachtungen an HTTP-Antworten. |

**SAST** untersucht Code ohne den Webdienst zu betreiben. **SCA** untersucht verwendete Komponenten auf bekannte Schwachstellen. **DAST** untersucht einen laufenden Dienst. Eine **SBOM** ist ein Komponentenverzeichnis. **SARIF** ist ein Austauschformat für Analyseergebnisse; Gitleaks, Trivy und ZAP haben daneben eigene JSON-Formate.

Eine **CVE** bezeichnet eine konkrete veröffentlichte Schwachstelle, eine **CWE** eine Schwachstellenart, etwa SQL-Injection. Diese Begriffe sind nicht austauschbar. Der aktuelle Normalizer speichert bei ZAP auch CWE-Verweise im historisch benannten Feld `cve_id`; bei der Interpretation daher den tatsächlichen Bezeichner beachten.

GitHub Actions und Docker sind Infrastruktur für die Ausführung. Bereits Gitleaks, Semgrep, Bandit und Trivy erfüllen die vier geforderten Security-Werkzeuge; die optionalen Dienste unter `infra/` werden dafür nicht gebraucht.

## 4. Der vollständige Ablauf eines Pipeline-Laufs

Der Einstieg ist beispielsweise:

```bash
python scripts/pipeline.py workloads/01-flask-api/fixed
```

Der Pfad bestimmt das Programm und die Variante. Die jeweilige `workload.json` beschreibt, ob es eine CLI oder ein Webdienst ist und welche HTTP-Pfade als Smoke-Test aufgerufen werden. Beispiel: [Flask-Konfiguration](workloads/01-flask-api/fixed/workload.json).

**Ablaufübersicht:** Die Schritte werden von oben nach unten ausgeführt. Nach einem Gate geht es nur bei PASS weiter.

| Schritt | Für alle Workloads | Besonderheit bei CLI oder Webdienst |
|---|---|---|
| 1. Vorbereitung | Runtime prüfen und Laufverzeichnis anlegen. | – |
| 2. Grundlegende Scans | Gitleaks, Semgrep, Bandit, Trivy-FS und Syft ausführen. | – |
| 3. CLI-Funktion prüfen | – | Nur CLI: hadolint, Image-Build und tatsächlicher Programmstart. |
| 4. Vorab-Gate | Bisherige Ergebnisse anhand der Policy bewerten. | Bei FAIL oder ERROR direkt zum Abschluss. |
| 5. Web-Image bauen | – | Nur Webdienst: hadolint und Image-Build; das CLI-Image existiert bereits. |
| 6. Image prüfen | Image exportieren und mit Trivy-Image sowie Dockle prüfen; gegebenenfalls Paketcache-Nachweis erheben. | – |
| 7. Image-Gate | Auch die Image-Findings bewerten. | Bei FAIL oder ERROR direkt zum Abschluss. |
| 8. Laufzeit prüfen | – | Webdienst: isolierter Start, Healthcheck, API-Smoke und passiver ZAP-Scan. CLI: ZAP als nicht anwendbar vermerken. |
| 9. Abschließendes Gate | Alle bis dahin vorliegenden Ergebnisse bewerten. | Bei FAIL oder ERROR direkt zum Abschluss. |
| 10. Optional veröffentlichen | Bei PASS und konfigurierter Registry das Image pushen. | Ohne Registry wird Publishing als ausgelassen vermerkt. |
| 11. Abschluss | Ergebnisse nochmals auswerten, Bericht erzeugen und Testressourcen aufräumen. | Auch nach Ablehnung oder technischem Fehler; `--keep` behält Container und Netzwerk. |

Technische Fehler in den einzelnen Schritten führen ebenfalls in die Fehlerbehandlung. Die Übersicht fasst den Ablauf zusammen; die maßgebliche Implementierung ist `Pipeline.execute()` in [pipeline.py](scripts/pipeline.py).

### 4.1 Vorbereitung und statische Prüfungen

Der Konstruktor von `Pipeline` prüft, dass der Workload innerhalb von `workloads/` liegt. Er liest Konfiguration und Image-Lockdatei und erstellt eine eindeutige Run-ID aus UTC-Zeit, Workload und Zufallsanteil. Dadurch werden Berichte verschiedener Läufe getrennt.

`scans()` führt die grundlegenden Scanner nacheinander aus. Der Workload-Secret-Scan verwendet [`.gitleaks-workload.toml`](.gitleaks-workload.toml) ohne Ausnahmen für die absichtlichen Demo-Secrets. Der zusätzliche History-Scan verwendet [`.gitleaks.toml`](.gitleaks.toml), das bekannte Demo-Dateien ausnimmt. So bleibt das gesamte Lehrrepository verwendbar, während der ausgewählte verwundbare Workload seine Secrets trotzdem meldet. Das ist eine besondere Regelung für die Lehrbeispiele, keine Empfehlung für echte Zugangsdaten.

Die Historie wird am tatsächlichen Git-Stamm untersucht. Ohne Git-Checkout wird dieser Check ausdrücklich als ausgelassen protokolliert. Im GitHub-Workflow sorgt `fetch-depth: 0` dafür, dass die Historie vollständig ausgecheckt wird.

**Wichtig für die Reihenfolge:** Die grundlegenden Scans werden zunächst gesammelt. Ein Secret-Finding beendet nicht unmittelbar jeden folgenden statischen Scan. Ein technischer Scannerfehler kann die Ausführung dagegen schon an dieser Stelle abbrechen.

### 4.2 Vorab-Gate und Sonderfall CLI

Vor dem ersten Gate wird die CLI tatsächlich gebaut und gestartet. So wird auch für die verwundbare CLI nachgewiesen, dass ihre alten, absichtlich problematischen Abhängigkeiten installierbar sind und das Programm funktioniert. Dieser Start erfolgt ohne Netzwerk und mit schreibgeschütztem Dateisystem sowie temporärem `/tmp`.

Danach führt `checkpoint()` Collector und Gate aus. Ein blockierender Befund stoppt den regulären Ablauf. Verwundbare Webdienste werden deshalb normalerweise noch vor Build und HTTP-Start abgelehnt. Für deren Lauffähigkeitsnachweis gibt es die separat gekennzeichneten Smoke-Tests.

### 4.3 Build und Image-Gate

Bei einem Webdienst folgt der Build erst nach bestandenem Vorab-Gate. `build()` führt hadolint aus und baut das Image. Bei der CLI fand dieser Schritt bereits statt. Danach exportiert `image_scan()` das Image als `image.tar` und übergibt es an Trivy und Dockle.

**Warum der Export?** Die Scanner benötigen keinen eingebundenen Docker-Socket. Derselbe Dateieingang funktioniert mit dem lokalen Docker-Daemon und Docker-in-Docker. Nach den Scans wird die temporäre Image-Datei im normalen Ablauf entfernt.

Für das festgelegte aktuelle Python-Basisimage wird zusätzlich geprüft, ob Paketmanager-Caches leer sind. Dieser isolierte Prüfcontainer überschreibt den Programmeinstieg. Er dient als Nachweis für die eng begrenzte Dockle-Ausnahme aus Abschnitt 8; er startet keinen Webdienst vor bestandenem Image-Gate.

Das zweite Gate berücksichtigt auch die Image-Findings. Eine neue blockierende Meldung verhindert den anschließenden Webdienst-Start.

### 4.4 Laufender Webdienst und ZAP

`deploy()` erstellt ein internes Docker-Netzwerk und startet den Webdienst ohne veröffentlichten Host-Port. Ein Healthcheck wartet auf `/health`; anschließend werden die konfigurierten API-Pfade aufgerufen. Diese Smoke-Tests belegen Erreichbarkeit und grundlegende Funktion. Sie prüfen nicht sämtliche fachlichen Antworten oder alle Angriffsmöglichkeiten.

`dast()` liest die versionierte `openapi.json`, setzt den aktuellen internen Containernamen als Serveradresse und startet ZAP im selben Netzwerk. So werden ausdrücklich beschriebene Endpunkte geprüft, anstatt sich auf eine eventuell leere oder nicht vorhandene Startseite zu verlassen.

Der Aufruf verwendet `zap-api-scan.py` mit **`-S` für den passiven Modus**. ZAP ruft die beschriebenen Endpunkte auf und bewertet den HTTP-Verkehr. Das ist kein aktiver SQLi- oder XSS-Angriffstest. Nicht beschriebene Routen sind dadurch auch nicht automatisch abgedeckt; beispielsweise ist `/ping` derzeit nicht Teil der Flask-OpenAPI-Beschreibung.

Eine CLI hat keine HTTP-Schnittstelle. Deshalb wird ZAP dort ausdrücklich als `skipped` mit Begründung vermerkt. `--skip-dast` bei einem Webdienst kennzeichnet dagegen einen bewusst unvollständigen Teillauf.

### 4.5 Abschluss, Veröffentlichung und Aufräumen

Nach den Laufzeitprüfungen folgt erneut das Gate. Nur bei PASS kommt ein optionaler Registry-Push infrage. Ohne Umgebungsvariable `REGISTRY` wird Publishing als nicht ausgeführt dokumentiert. Mit konfigurierter Registry müssen Tagging und Push funktionieren; ein fehlgeschlagener Push ist ERROR.

Im `finally`-Block werden die bis dahin vorhandenen Ergebnisse nochmals ausgewertet und der Gesamtbericht erzeugt. Damit erscheinen auch Fehler nach einem zuvor grünen Gate, etwa beim Deployment oder Push, im Ergebnis. Anschließend werden Testcontainer und Testnetzwerk entfernt, außer bei `--keep`. Scanner-Images, gebaute Images und Cache bleiben für spätere Läufe erhalten. Sehr frühe Setup-Fehler können auftreten, bevor ein vollständiges Laufverzeichnis verfügbar ist.

### 4.6 Die wichtigsten Methoden im Orchestrator lesen

| Methode in `Pipeline` | Was macht der Code konkret? |
|---|---|
| `__init__()` | Löst Pfade auf, lädt JSON-Konfiguration, berechnet Hashes und initialisiert das Laufverzeichnis. |
| `save()` | Schreibt den aktuellen Zustand und die Zeitmessungen in `run.json` und `timings.json`. |
| `command()` | Startet die Container-Runtime mit `subprocess.run()` und einer Argumentliste; prüft erlaubte Exit-Codes und verwendet standardmäßig ein Timeout von 900 Sekunden. |
| `check()` | Ergänzt Statusprotokollierung, Reportprüfung und eine Zeitmessung um einen Prozessaufruf. Bei Fehlern wird eine `PipelineError` weitergegeben. |
| `tool()` | Baut die Argumentliste für einen Scanner-Container einschließlich Netzwerk und Dateimounts zusammen; startet ihn selbst noch nicht. |
| `trivy()` | Ergänzt die gemeinsamen Trivy-Optionen für Dateisystem-/Image-Prüfung, JSON-Ausgabe, Cache und Offline-Betrieb. |
| `checkpoint()` | Startet Collector und Gate, prüft deren Ergebnis und liefert die Entscheidung an `execute()` zurück. |
| `execute()` | Verknüpft alle Schritte und Entscheidungen; `try`/`except`/`finally` bilden Fehlerbehandlung und Abschluss ab. |

Die Übergabe als Argumentliste ist wichtig: Der Orchestrator baut keinen Shell-Befehl aus einem langen Textstring. Das unterscheidet diesen Prozessstart technisch von der absichtlich unsicheren `os.system()`-Verwendung im Flask-Negativbeispiel. Es beseitigt nicht jede mögliche Gefahr externer Prozesse, vermeidet hier aber eine zusätzliche Shell-Interpretation der Argumente.

## 5. Wie wird aus einem Scannerbericht eine Entscheidung?

Die Kette lautet:

```text
Scanner-Rohreport → collect.py / normalize.py → findings.json
                 → gate.py + thresholds.yaml + suppressions.json → gate.json
                 → report.py → FINDINGS_REPORT.md / metrics.csv
```

### 5.1 Gemeinsames Datenmodell

`collect.py` enthält die Zuordnung `SOURCES`: Welcher Dateiname gehört zu welchem Parser und welcher Testklasse? `normalize.py` liefert daraus Findings mit Feldern wie:

```json
{
  "id": "beispiel-finding",
  "tool": "semgrep",
  "test_class": "sast",
  "severity": "HIGH",
  "rule_id": "request-to-sql",
  "title": "Request input reaches SQL",
  "location": "app.py:42",
  "cve_id": "",
  "remediation": "Use bound parameters",
  "false_positive": false
}
```

Das ist ein erklärendes Beispiel, kein kopierter Messwert. Die einheitlichen Schweregrade sind `INFO`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`. Beispielsweise wird SARIF `error` zu `HIGH`; Gitleaks-Findings werden hier als `CRITICAL` behandelt. Das sind nachvollziehbare Projektzuordnungen, keine automatisch berechneten individuellen CVSS-Werte.

Bei der Deduplizierung bildet **Finding-ID plus Testklasse** den Schlüssel. Die höchste Severity bleibt erhalten. Dieselbe CVE aus SCA und Image-Prüfung darf in beiden Kontexten bestehen bleiben: Sonst könnte die strengere Image-Regel durch die mildere SCA-Regel verloren gehen. Verschiedene Tool-IDs für dieselbe Ursache werden nicht automatisch semantisch zusammengeführt. Die Finding-Anzahl ist daher keine verlässliche Anzahl unabhängiger Schwachstellen.

### 5.2 Die konkrete Gate-Policy

Maßgeblich ist [policy/thresholds.yaml](policy/thresholds.yaml), ausgewertet durch das Python-Gate. Der ältere [OPA-Entwurf](policy/gate.rego) gehört nicht zum unterstützten Ausführungspfad.

| Testklasse | Blockiert | Warnt | Nur Information |
|---|---|---|---|
| Secrets | Alle Schweregrade | – | – |
| SAST | HIGH und CRITICAL | MEDIUM | LOW und INFO |
| SCA | CRITICAL | HIGH und MEDIUM | LOW und INFO |
| Image, einschließlich hadolint | HIGH und CRITICAL | MEDIUM | LOW und INFO |
| DAST | Kein Finding allein | MEDIUM, HIGH und CRITICAL | LOW und INFO |

**Warum diese Unterschiede?** Es ist eine bewusst gewählte Lehrprojekt-Policy, die Signal und Prüfaufwand gewichtet. Die Warnstufe bedeutet, dass ein Befund weiterhin bewertet werden muss. Eine HIGH-Abhängigkeitslücke ist dadurch nicht nachweislich unerreichbar oder harmlos. Ebenso sind ZAP-Warnungen nicht pauschal Fehlalarme. Für einen Produktivbetrieb müssten Schwellenwerte und Freigabeprozess zum konkreten Risiko passen.

### 5.3 Scanner-Erfolg, Security-Ergebnis und technischer Fehler

`check()` protokolliert einen Check zunächst als `running`. Erst wenn der Prozess einen erlaubten Exit-Code liefert und der erwartete Report lesbar und strukturell plausibel ist, wird daraus `ok`. Das bedeutet **„Prüfung ausgeführt“**, nicht „keine Schwachstelle“.

Viele Scanner sind so eingestellt, dass Findings allein ihren Prozess nicht abbrechen. Dadurch können alle Meldungen gesammelt und zentral bewertet werden. Auch die zugelassenen ZAP-Exit-Codes haben ihre eigene Tool-Bedeutung. Sie dürfen nicht unmittelbar mit den folgenden Exit-Codes unserer Pipeline gleichgesetzt werden.

| Ergebnis der einzelnen Pipeline | Exit-Code | Bedeutung |
|---|---|---|
| PASS | 0 | Ausgeführte Pflichtprüfungen erfolgreich, keine aktiven blockierenden Findings |
| FAIL | 1 | Erfolgreiche Scans ergeben mindestens ein blockierendes Finding |
| ERROR | 2 | Technischer Fehler, etwa fehlender Report, Scanner-Ausfall, kaputtes Image oder fehlerhafter Healthcheck |

**Fail closed** heißt hier: Fehlende Pflichtnachweise führen nicht zu einer Freigabe. Collector und Gate prüfen sowohl Reportdateien als auch dokumentierte Checkzustände. Fehler haben Vorrang vor Security-Findings. `checkpoint()` entfernt alte normalisierte Ergebnisse und prüft, ob Gate-JSON und Gate-Exit-Code zusammenpassen. So kann kein altes PASS einfach weiterverwendet werden.

Die Reportprüfung kontrolliert erwartete Grundstrukturen, bei SARIF auch gemeldete fehlgeschlagene Ausführungen. Sie ist keine vollständige formale Schema- oder Inhaltsprüfung jedes Scannerformats.

## 6. Die drei Programme und ihre Korrekturen

### 6.1 Flask-API: Eingaben dürfen nicht zu Code werden

Dateien: [verwundbares app.py](workloads/01-flask-api/vulnerable/app.py), [bereinigtes app.py](workloads/01-flask-api/fixed/app.py).

Die API verwendet eine kleine SQLite-Datenbank und bietet unter anderem `/user`, `/greet`, `/ping`, `/hash` und `/health`. Die Schwachstellen wurden absichtlich eingebaut, um mehrere Prüfklassen anschaulich zu machen.

| Stelle | Problem der verwundbaren Variante | Änderung und Wirkung |
|---|---|---|
| `/user` | Nutzereingabe wird in SQL-Text eingesetzt. | Parameterbindung trennt SQL-Struktur und Daten. |
| `/greet` | Eingabe landet ungefiltert im HTML. | `escape()` maskiert HTML-Sonderzeichen für diese Ausgabestelle. |
| `/ping` | `os.system()` interpretiert zusammengesetzten Text durch eine Shell. | IP-Validierung und Argumentliste mit `shell=False` vermeiden Shell-Interpretation. |
| `/hash` | MD5 als ungeeignetes Sicherheitsbeispiel. | SHA-256 demonstriert einen moderneren allgemeinen Hash. |
| Start und Antworten | Debug-Modus und fehlende Schutzheader. | Debug aus; unter anderem CSP, `nosniff`, Frame-Schutz und `no-store`. |

Die entscheidende SQL-Korrektur im tatsächlichen Code lautet:

```python
rows = conn.execute(
    "SELECT id, name, role FROM users WHERE name = ?", (name,)
).fetchall()
```

Der Platzhalter wird vom Datenbanktreiber als Wert gebunden. Ein Apostroph in `name` wird dadurch nicht Teil eines neuen SQL-Befehls. Das Komma in `(name,)` erzeugt ein Tupel mit genau einem Element. Die zusätzliche Begrenzung auf 64 Zeichen ersetzt diese Parameterbindung nicht.

**Wie findet Semgrep das?** Die Regel `request-to-sql` in [semgrep.yml](policy/semgrep.yml) markiert `request.args.get(...)` als Quelle unzuverlässiger Daten und den passenden Datenbankaufruf als Senke. Bei der XSS-Regel ist `escape(...)` als Bereinigung angegeben. Insgesamt sind es neun lokale Lehrregeln, kein vollständiges Regelpaket für alle möglichen Schwachstellen.

**Grenzen:** SHA-256 allein ist kein geeignetes Passwortspeicherverfahren. Die Ping-Funktion prüft die Rückgabe des Ping-Prozesses nicht auf Erreichbarkeit. Auch die bereinigte API läuft mit dem Flask-Entwicklungsserver; das Beispiel ist keine fertige Produktionsbereitstellung.

### 6.2 Konfigurations-CLI: Parser, TLS und Abhängigkeiten

Dateien: [verwundbares main.py](workloads/02-cli-deps/vulnerable/main.py), [bereinigtes main.py](workloads/02-cli-deps/fixed/main.py), [bereinigte Dependencies](workloads/02-cli-deps/fixed/requirements.txt).

`main()` liest `--config`, lädt YAML und gibt die Anzahl der Konfigurationsschlüssel aus. Zusätzlich enthält das Programm exemplarische Funktionen zum Abrufen einer URL und zum Zwischenspeichern von Text. Diese beiden Funktionen werden vom normalen CLI-Start nicht aufgerufen. Ihre statischen Findings sind daher von einer tatsächlich im Smoke-Test ausgeführten Schwachstelle zu unterscheiden.

| Funktion | Verwundbar | Bereinigt und Begründung |
|---|---|---|
| `load_config()` | `yaml.unsafe_load()` kann Python-spezifische Objekte konstruieren. | `yaml.safe_load()` beschränkt die Deserialisierung auf sichere Datentypen. |
| `fetch()` | `verify=False` deaktiviert die Zertifikatsprüfung. | HTTPS-Schema wird verlangt, Zertifikatsprüfung bleibt mit `verify=True` aktiv; HTTP-Fehler werden ausgewertet. |
| `cache()` | `tempfile.mktemp()` liefert einen Namen ohne atomisches Anlegen. | `NamedTemporaryFile()` legt die Datei beim Erzeugen an und reduziert das Race-Problem. |
| Umgebung | Absichtlich alte Bibliotheken und alte Python-Basis. | Aktualisierte, exakt versionierte Abhängigkeiten und aktuelles festgelegtes Basisimage. |

TLS schützt unter anderem davor, einen falschen Server ohne gültiges Zertifikat zu akzeptieren. Der Code verwendet die Zertifikatsprüfung von Requests; es wird kein eigener CA-Pfad explizit übergeben. Eine reine Beschränkung auf `https` ist außerdem **kein vollständiger SSRF-Schutz**, da Zielhosts und interne IP-Adressen damit nicht eingeschränkt werden. Temporäre Cache-Dateien werden mit `delete=False` behalten; für eine größere Anwendung wäre deren Lebenszyklus zusätzlich zu regeln.

Die alten Komponenten im Negativbeispiel sind absichtlich kompatibel ausgewählt, damit das Beispiel wirklich installierbar bleibt. „Verwundbar“ darf für die Demonstration nicht einfach „Programm startet nicht“ bedeuten.

### 6.3 HTTP-Dateidienst: Secrets und Pfadbegrenzung

Dateien: [verwundbares app.py](workloads/03-container-service/vulnerable/app.py), [bereinigtes app.py](workloads/03-container-service/fixed/app.py).

Das Beispiel verwendet `http.server` und `socketserver` aus der Python-Standardbibliothek. Die verwundbare Variante enthält künstliche Zugangsdaten im Code und zusätzliche Demo-Dateien. Beim Dateizugriff wird der angefragte Name direkt an `/app/data/` angehängt. Mit `../` könnte ein Pfad aus diesem Verzeichnis herausführen.

Die bereinigte Variante prüft den aufgelösten Pfad:

```python
target = (DATA_ROOT / name).resolve()
if not target.is_relative_to(DATA_ROOT) or not target.is_file():
    self._json(404, {"error": "file not found"})
    return
```

`resolve()` löst unter anderem relative Pfadanteile auf. Anschließend muss das Ziel innerhalb des ebenfalls aufgelösten Datenverzeichnisses liegen und eine Datei sein. Eine bloße Zeichenkettenprüfung auf den Präfix `/app/data` wäre unzureichend, weil beispielsweise `/app/database` denselben Textanfang haben kann.

Die bereinigte Route gibt Dateiname und Größe als JSON zurück, während die verwundbare Variante Dateiinhalte ausliefert. Das Beispiel wurde also auch im Umfang der Funktion eingeschränkt; es ist kein vollständig identischer Ersatz für einen Dateidownload.

Der feste Token wurde durch `os.environ.get("API_TOKEN")` ersetzt. Ohne Token startet die bereinigte Anwendung nicht. Die Pipeline erzeugt beim Start einen zufälligen Testwert. **Der Handler kontrolliert diesen Token jedoch nicht bei eingehenden Requests.** Damit wird Konfigurationsinjektion demonstriert, keine implementierte API-Authentifizierung. Vault wird in diesem Ablauf nicht verwendet.

## 7. Warum Container, feste Versionen und ein Offline-Modus?

### 7.1 Dockerfile lesen können

Am [bereinigten Flask-Dockerfile](workloads/01-flask-api/fixed/Dockerfile) lassen sich die wesentlichen Anweisungen erklären:

| Anweisung | Bedeutung |
|---|---|
| `FROM python@sha256:...` | Legt das Basisimage anhand seines Inhalts-Digests fest. |
| `WORKDIR /app` | Setzt das Arbeitsverzeichnis für folgende Schritte und den Programmstart. |
| `COPY requirements.txt .` / `RUN ... pip install ...` | Installiert Abhängigkeiten beim Build; eigene Schicht vor dem Kopieren des Anwendungscodes ermöglicht Cache-Wiederverwendung. |
| `COPY app.py .` und `COPY data/ ...` | Fügt Programm und Beispieldaten in das Image ein. |
| `USER 10001` | Legt den Benutzer des späteren Anwendungsprozesses fest. |
| `ENV ...` | Setzt nicht geheime Laufzeitvorgaben. Echte Secrets gehören nicht dauerhaft ins Image. |
| `EXPOSE 8080` | Dokumentiert den vorgesehenen Port; veröffentlicht allein keinen Host-Port. |
| `HEALTHCHECK ...` | Beschreibt eine Zustandsprüfung für Docker; der Orchestrator prüft zusätzlich selbst. |
| `CMD ["python3", "app.py"]` | Standardprozess beim Containerstart. |

Ein **Image** ist die gebaute Vorlage, ein **Container** deren gestartete Instanz. Ein erfolgreicher Image-Build belegt noch nicht, dass die Anwendung startet oder ihre API funktioniert. Deshalb folgen gesonderte Funktionstests.

### 7.2 Schutzmaßnahmen bei der Ausführung

Scanner bekommen den Workload grundsätzlich lesend und nur das Reportverzeichnis schreibend eingebunden. Mehrere lokale Scanner laufen explizit ohne Netzwerk. Trivy kann online für Datenbankaktualisierungen Netzwerk benötigen.

Die Webdienste laufen mit schreibgeschütztem Dateisystem, temporärem `/tmp`, entfernten Linux-Capabilities und `no-new-privileges`. Im internen Netzwerk können ZAP und Anwendung miteinander sprechen, ohne einen Host-Port freizugeben. Die CLI wird ohne Netzwerk gestartet. Diese Einschränkungen begrenzen die Möglichkeiten der absichtlich unsicheren Programme; sie sind kein Beweis vollständiger Isolation oder Produktionssicherheit.

### 7.3 Reproduzierbarkeit und Cache

[images.lock.json](policy/images.lock.json) fixiert externe Tool- und Basisimages über Digests. Das Bandit-Toolimage wird lokal aus dem festgelegten Basisimage und versionierten Paketanforderungen gebaut. Zusätzlich werden die tatsächlich verwendeten Image-IDs protokolliert.

Ein Quellenhash entsteht aus den Workload-Dateipfaden und Dateiinhalten. Seine ersten 20 Zeichen bilden den lokalen Anwendungs-Image-Tag. `pipeline_source_digest` identifiziert zusätzlich wesentliche Implementierungs- und Policy-Dateien. Das dient der Zuordnung von Ergebnissen, nicht einer digitalen Signatur oder einem Sicherheitsnachweis des Codes.

`prepare.py` lädt online die festgelegten Images, baut das Bandit-Image und wärmt das Docker-Volume `devsecops-trivy-cache` vor. Es baut noch nicht sämtliche Anwendungsimages. Für eine spätere Offline-Demo müssen diese vorher ebenfalls erstellt worden sein, gegebenenfalls durch die separaten Smoke-Tests bei früh abgelehnten Webvarianten.

Im Offline-Modus werden keine fehlenden Anwendungsimages nachgebaut. Das exakt zum Workload-Hash passende lokale Image muss vorhanden sein. Trivy verwendet die vorhandene Datenbank ohne Update. Geänderte Quellen ohne passendes Image führen daher zu ERROR statt zu einem Scan eines alten Builds.

**Warum können spätere Ergebnisse trotzdem abweichen?** Image-Version, Regelversion und Schwachstellendatenbank sind verschiedene Eingaben. Neue CVEs können bei unverändertem Image neue Findings erzeugen. Feste Paketversionen pinnen außerdem keine Paketdatei-Hashes; vollständige Lieferkettenabsicherung wäre ein eigener weiterer Schritt.

## 8. Warum gibt es trotz „fixed“ eine Ausnahme und Warnungen?

Ein PASS bedeutet, dass die festgelegte Policy bestanden wurde. Es bedeutet weder null Findings noch null Restrisiko.

Die aktuelle [suppressions.json](policy/suppressions.json) enthält eine überprüfte Ausnahme für `dockle:DKL-DI-0004`. Dockle interpretiert einen geerbten Paketmanager-Befehl des offiziellen Python-Alpine-Images als problematische Cache-Nutzung. Die Bewertung berücksichtigt, dass der erste Installationsschritt `--no-cache` verwendet und ein späterer Schritt lokale Laufzeitabhängigkeiten mit `--no-network` auflöst. Zusätzlich muss die Prüfung `package-cache-empty` erfolgreich sein.

Diese Ausnahme gilt nur für die drei benannten Fixed-Workloads, den exakten Basisimage-Digest und den erwarteten Befehl im Befund. Sie hat einen Owner, eine Begründung und das **Ablaufdatum 20.11.2026**. Nach Ablauf oder bei abweichendem Kontext darf sie das Finding nicht mehr unterdrücken. Vor einem späteren Vortrag muss sie überprüft werden.

Der Rohbefund bleibt erhalten, und die Gateentscheidung weist die Ausnahme aus. Es handelt sich damit um eine nachvollziehbare Einzelfallbewertung. Eine unbegründete globale Abschaltung der Regel würde diese Nachvollziehbarkeit verlieren.

Die [manuelle Findingsbewertung](docs/FINDINGS_BEWERTUNG.md) unterscheidet echte Codeprobleme, kontextabhängige Meldungen und den geprüften Fehlalarm. Das Feld `false_positive` wird vom Normalizer nicht automatisch als fachliche Bewertung gesetzt; eine False-Positive-Quote lässt sich nicht einfach aus der Zahl grüner Läufe ableiten.

## 9. Wie startet GitHub die Pipeline automatisch?

Der Workflow liegt im Git-Stamm unter [`.github/workflows/devsecops.yml`](../.github/workflows/devsecops.yml). GitHub erkennt diese Datei an ihrem vorgesehenen Ort. Die entscheidenden Teile sind:

| YAML-Einstellung | Bedeutung in unserem Projekt |
|---|---|
| `on: push` | Push startet den Workflow automatisch. |
| `pull_request` | Änderungen in Pull Requests werden ebenfalls geprüft. |
| `workflow_dispatch` | Zusätzlicher manueller Start, sofern von GitHub für den Workflow angeboten. |
| `permissions: contents: read` | Der Workflow verlangt lesenden Repository-Zugriff. |
| Job `tests` | Installiert Entwicklungsabhängigkeiten und prüft zuerst die Pipeline-Logik mit pytest. |
| `needs: tests` | Die sechs Demo-Fälle starten erst nach erfolgreichen Tests. |
| Matrix `program × variant` | Drei Programme mal zwei Varianten ergeben sechs Jobs. |
| `strategy.fail-fast: false` | Ein fehlerhafter Matrixfall beendet nicht die anderen Fälle; ihre Nachweise bleiben verfügbar. |
| `working-directory: devsecops-pipeline` | Python-Befehle arbeiten trotz CI-Datei im Git-Stamm im richtigen Projektverzeichnis. |
| `fetch-depth: 0` | Vollständige Checkout-Historie für den Secret-History-Scan. |
| Artefakt-Upload mit `if: always()` | Lädt vorhandene Nachweise auch bei fehlgeschlagenen Prüfschritten hoch. |

`fail-fast: false` bei der **CI-Matrix** unterscheidet sich vom frühen Abbruch einer **einzelnen Pipeline** nach einem gescheiterten Gate. Der erste Fall hält unabhängige Versuche am Leben, der zweite verhindert spätere Schritte eines abgelehnten Workloads.

Der vom Benutzer bereitgestellte Screenshot bestätigt **DevSecOps demo verification #1**, ausgelöst durch den Push von Commit `234b46a` auf `validation/pipeline-pruefung`, erfolgreich in **3 Minuten und 2 Sekunden**. Damit ist der GitHub-Push-Trigger tatsächlich nachgewiesen.

Die alternative [GitLab-Konfiguration](../.gitlab-ci.yml) verwendet dieselben Python-Skripte, benötigt aber einen korrekt eingerichteten privilegierten Docker-in-Docker-Runner. Ein tatsächlicher GitLab-Lauf ist bislang nicht nachgewiesen.

Die optionale [Pre-commit-Konfiguration](../.pre-commit-config.yaml) kann nach lokaler Installation mit `python -m pre_commit install` **im Git-Stamm** aktiviert werden. Eine vorhandene Konfigurationsdatei allein installiert noch keinen Hook. Bekannte absichtliche Negativbeispiele sind dort ausgenommen; die CI prüft sie weiterhin als Negativtests.

## 10. Warum ist der Workflow grün, obwohl vulnerable FAIL liefert?

Der CI-Job startet `demo.py` und damit eine **Prüfung der Pipeline-Erwartungen**. Die Security-Entscheidung für einen Workload bleibt davon getrennt.

| Workload | Erwarteter Pipeline-Exit | Erwartete Gateentscheidung | Demo-Bewertung |
|---|---|---|---|
| `vulnerable` | 1 | FAIL mit mindestens einem blockierenden Finding | Erfolgreicher Negativtest |
| `fixed` | 0 | PASS | Erfolgreicher Positivtest |
| Beliebiger Workload mit technischem Fehler | 2 | ERROR | Demo fehlgeschlagen |
| `vulnerable` wird freigegeben oder `fixed` wird abgelehnt | Unerwartet | Unerwartet | Demo fehlgeschlagen |

`demo.py` vergleicht nicht nur den Prozess-Exit-Code: Es verlangt genau eine neue Gate-Datei, den passenden Status und beim Negativfall ein blockierendes Finding. Ein Python-Absturz mit Exit 1 wäre deshalb kein gültiger Nachweis einer Security-Ablehnung.

Der Demo-Runner selbst liefert 0, wenn alle ausgewählten Erwartungen erfüllt sind, sonst 1. Sein Exit 1 hat also eine andere Bedeutung als Exit 1 der einzelnen Security-Pipeline. Verwundbarer Code wird durch den grünen Demo-Job nicht freigegeben oder veröffentlicht.

## 11. Welche Nachweise zeigen wir bei Rückfragen?

Für jeden normalen Lauf entsteht ein eigener Ordner unter `reports/`. Am besten erklärt man einen konkreten Fall in dieser Reihenfolge:

| Datei | Was lässt sich damit beantworten? |
|---|---|
| `run.json` | Welcher Workload? Welche Images, Quellenhashes und Checkzustände? Was wurde ausdrücklich ausgelassen? |
| `raw/` | Was meldete das ursprüngliche Werkzeug tatsächlich? Welche SBOM wurde erzeugt? |
| `findings.json` | Wie wurden die Meldungen vereinheitlicht und welchen Testklassen zugeordnet? |
| `gate.json` | PASS, FAIL oder ERROR? Welche Befunde blockieren? Welche Ausnahme wurde angewendet? |
| `timings.json` | Welche Dauer wurde je Check erfasst? |
| `reports/FINDINGS_REPORT.md` und `metrics.csv` | Wie lassen sich mehrere Läufe überblicken und vergleichen? |
| `reports/demo-results.json` | Stimmen erwarteter Exit, tatsächlicher Exit und Gate-Status für die Demo-Fälle überein? |

Nach einem frühen Gate-Abbruch sind spätere Scans nicht durchgeführt. Fehlende spätere Checks sind dann kein Nachweis, dass diese Prüfungen bestanden wurden. Das Manifest unterscheidet solche Abläufe von ausdrücklich protokollierten Auslassungen, etwa ZAP bei einer CLI.

Die archivierte [Nachprüfung](docs/NACHPRUEFUNG.md) enthält zwölf echte Security-Läufe, sechs online und sechs offline, sowie sechs separate funktionale Smoke-Tests. Die folgenden Zahlen stammen aus [results.json](docs/validation/2026-10-21-fixed/results.json), jeweils aus den vollständigen Offline-Läufen:

| Programm | Vulnerable | Blockierende Findings | Fixed | Geprüfte Ausnahmen bei Fixed |
|---|---|---|---|---|
| Flask-API | FAIL / 1 | 8 | PASS / 0 | 1 |
| Konfigurations-CLI | FAIL / 1 | 4 | PASS / 0 | 1 |
| HTTP-Dateidienst | FAIL / 1 | 10 | PASS / 0 | 1 |

Weitere Nachweise: [archivierter Findings-Bericht](docs/validation/2026-10-21-fixed/FINDINGS_REPORT.md) und [Evidence-Archiv](docs/validation/2026-10-21-fixed/evidence.zip). Bei den Tests bestehen laut dokumentierter Nachprüfung 41 aktuelle Tests unter Linux; zusammen mit neun zusätzlichen ursprünglichen Akzeptanzprüfungen wurden unter Windows 50 Tests bestanden. Die reguläre Testsuite unter `tests/` ist daher nicht mit 50 Tests zu beschriften.

Der lokale Online-Durchlauf aller sechs Fälle dauerte ungefähr zehn Minuten. Ein Offline-History-Scan zeigte eine nicht abschließend erklärte Pause von rund 4265 Sekunden. Diese Werte sind keine belastbaren Benchmarks. Die sechs GitHub-Matrixfälle können parallel laufen; ihre Gesamtdauer ist deshalb nicht direkt mit der lokalen sequenziellen Suite vergleichbar.

## 12. Bedienung und Demonstration

Voraussetzungen sind Python 3.10+, Git sowie Docker mit laufender Linux-Container-Runtime. Für Erstinstallation, Vorbereitung und erste Builds wird Internet benötigt. Vom Git-Stamm aus zuerst `cd devsecops-pipeline` ausführen.

```bash
# Tests und Vorbereitung
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
python scripts/prepare.py

# Ein Negativfall: Exit 1 und Gate FAIL sind hier vorgesehen
python scripts/pipeline.py workloads/01-flask-api/vulnerable

# Ein Positivfall: Exit 0 und Gate PASS sind vorgesehen
python scripts/pipeline.py workloads/01-flask-api/fixed

# Alle sechs Erwartungen gemeinsam prüfen: Demo-Exit 0 vorgesehen
python scripts/demo.py

# Nur einen Fall im selben Prüfmodus wie die CI ausführen
python scripts/demo.py --workload workloads/03-container-service/fixed

# Separat zeigen, dass ein früh abgelehntes Programm trotzdem lauffähig ist
python scripts/smoke.py workloads/03-container-service/vulnerable
```

Unter PowerShell zeigt `$LASTEXITCODE` unmittelbar nach dem Python-Aufruf dessen Exit-Code; unter Bash ist es `echo $?`. Im Ausgabeordner die zugehörige neue `gate.json` öffnen und gemeinsam mit dem Exit-Code interpretieren.

Nach vollständig gefülltem Cache und vorher gebauten passenden Anwendungsimages:

```bash
python scripts/prepare.py --offline
python scripts/demo.py --offline
```

`smoke.py` führt keine vollständige Security-Pipeline und kein Gate aus und schreibt `smoke-only.json` mit `security_scanned: false`. Beim wiederverwendeten Build-Schritt läuft allerdings weiterhin hadolint mit. Der Smoke-Lauf ist ein Funktionsnachweis, keine Freigabe für Publishing. Neue Smoke-Ausgaben nicht mit vollständigen Gate-Läufen verwechseln.

Die wichtigsten optionalen Einstellungen werden über die Umgebung oder Startargumente übergeben:

| Einstellung | Wirkung |
|---|---|
| `REPORTS_DIR` | Separates Verzeichnis für Laufnachweise statt `reports/`. |
| `CONTAINER_RUNTIME` | Überschreibt den standardmäßig verwendeten Befehl `docker`; andere Runtimes sind damit nicht automatisch vollständig nachgewiesen. |
| `REGISTRY` | Aktiviert den Registry-Push nach bestandenem Gate; Anmeldung und Ziel müssen passend eingerichtet sein. |
| `--offline` | Verwendet lokale Images und vorhandene Scanner-Datenbanken. |
| `--skip-dast` | Lässt ZAP ausdrücklich aus; der Lauf belegt damit keine vollständige DAST-Ausführung. |
| `--keep` | Behält den Testcontainer und das Testnetzwerk für die Fehlersuche. |

Die letzten beiden Argumente gehören zu `pipeline.py`; `demo.py` bietet davon nur `--offline` sowie seine Workload-Auswahl an.

Für den Vortrag vorher vorwärmen und ein bis zwei Fälle live zeigen. Die übrigen Ergebnisse anhand des Archivs erläutern und eine Aufnahme als Reserve bereithalten. Der [Demo-Leitfaden](docs/DEMO_SCRIPT.md) hilft bei der Zeitplanung.

## 13. Typische Prüfungsfragen mit belastbaren Antworten

| Mögliche Rückfrage | Antwort anhand unserer Implementierung |
|---|---|
| Was ist an der Pipeline automatisiert? | GitHub startet bei Push und Pull Request die Tests und sechs Demo-Fälle. Der gemeinsame Python-Orchestrator startet die Scanner und wertet die Policy aus. |
| Warum sowohl Semgrep als auch Bandit? | Semgrep demonstriert lokale Muster und Datenflüsse, Bandit ergänzt Python-Prüfungen. Überschneidungen sind möglich und erhöhen nicht automatisch die Zahl unabhängiger Fehler. |
| Was prüft ihr ohne Programmstart? | Secrets, Code, Abhängigkeiten und Dockerfile lassen sich statisch prüfen. Ein Image muss zusätzlich gebaut werden, damit dessen tatsächliche Komponenten geprüft werden können. |
| Warum reichen Unit-Tests nicht aus? | Unit-Tests prüfen die implementierte Logik anhand ausgewählter Fälle. Sie ersetzen weder Schwachstellenwissen über Pakete noch Image-Prüfungen oder Beobachtungen am laufenden Dienst. |
| Warum scannt ihr Dependencies und Image separat? | Anforderungen im Projekt und tatsächlich installierte Anwendungs- und Betriebssystemkomponenten sind unterschiedliche Sichtweisen. Beide Kontexte bleiben auch bei gleicher CVE erhalten. |
| Warum sind Schwellenwerte im Repository? | Policy as Code macht Entscheidungen versionierbar und überprüfbar. Eine Regeländerung lässt sich wie eine Codeänderung reviewen. |
| Was passiert, wenn ein Scanner abstürzt? | Der Check wird fehlerhaft, die Pflichtnachweise fehlen und die Pipeline endet mit ERROR / 2. Das akzeptiert die Demo nicht als erfolgreichen Negativtest. |
| Warum darf DAST hier nur warnen? | Das ist die gewählte Lehrprojekt-Policy. Die Meldungen bleiben zur Bewertung sichtbar. Ein technisch gescheiterter Scan ist trotzdem ein Fehler. |
| Habt ihr mit ZAP SQL-Injection bewiesen oder ausgeschlossen? | Nein. Der eingesetzte Modus ist passiv und OpenAPI-begrenzt. SQL-Injection wird hier durch Codeanalyse und separate gezielte Akzeptanzprüfungen beurteilt. |
| Ist fixed vollständig sicher? | Es besteht die aktuelle Policy im dokumentierten Umfang. Warnungen, eine befristete geprüfte Ausnahme und nicht geprüfte Angriffsmöglichkeiten bleiben zu berücksichtigen. |
| Warum stoppt vulnerable so früh? | Das erste Gate erkennt bereits blockierende Befunde. Spätere Schritte sollen bei dieser Security-Ablehnung nicht mehr laufen. Separate Smoke-Tests belegen dennoch die Lauffähigkeit. |
| Warum ist der gesamte Workflow dann grün? | Er prüft, dass die Pipeline verwundbare Fälle korrekt ablehnt und Fixed-Fälle korrekt akzeptiert. Die jeweiligen Vulnerable-Gates bleiben FAIL. |
| Werden echte Secrets benutzt? | Die eingecheckten Werte sind künstliche Demo-Secrets. Der Test-Token beim Start wird zufällig erzeugt. Bei einem echten Leak müssten Zugangsdaten widerrufen oder rotiert werden; das Löschen aus dem aktuellen Code reicht nicht. |
| Wo ist Vault angebunden? | In diesem nachgewiesenen Scan-Pfad nicht. Der Token kommt direkt aus der Pipeline über eine Umgebungsvariable. Die Compose-Datei ist ein optionaler Entwurf. |
| Warum kein API-Token-Check beim Dateidienst? | Die aktuelle Implementierung zeigt externe Konfiguration, keine Authentifizierung. Ein Request-Check mit passendem Authentifizierungskonzept wäre eine zusätzliche Funktion. |
| Wozu die SBOM? | Sie dokumentiert Komponenten und unterstützt spätere Nachverfolgung. Syft bewertet hier selbst keine Sicherheitslücke. Die erzeugte SBOM beschreibt den gescannten Quellverzeichnis-Eingang, nicht automatisch jede OS-Komponente des fertigen Images. |
| Könnt ihr offline immer dieselben Ergebnisse garantieren? | Nur vorhandene Images, lokale Regeln und der vorhandene Datenbankstand werden verwendet. Fehlende passende Images führen zu ERROR. Online aktualisierte Datenbanken können neue Findings liefern. |
| Wird nach PASS automatisch produktiv deployed? | Nein. Es gibt ein isoliertes Testdeployment und optional einen Registry-Push bei Konfiguration. Ein Produktions-Rollout ist nicht implementiert. |
| Wie beurteilt ihr False Positives? | Rohbefund, Code und Kontext prüfen, begründen und gegebenenfalls eine enge, befristete Ausnahme dokumentieren. Eine allgemeine Fehlalarmquote wurde nicht belastbar gemessen. |
| Wie würdet ihr die Pipeline weiterentwickeln? | Etwa breitere Regelabdeckung, überprüfte Risiko-Schwellen, aktive autorisierte Laufzeittests, echte Authentifizierung und zusätzliche Lieferkettennachweise. Diese Erweiterungen sind von der bereits nachgewiesenen Funktion zu unterscheiden. |

## 14. Einen konkreten Befund durch die Pipeline verfolgen

Für die Erklärung bietet sich SQL-Injection in der Flask-API an:

1. Im verwundbaren `app.py` zeigen, wie der Request-Parameter in einen SQL-String gelangt. Die problematische Stelle konkret benennen, statt nur den Namen der Schwachstelle zu nennen.
2. In `policy/semgrep.yml` die Quelle und Senke der Regel `request-to-sql` zeigen. Ergänzende Bandit-Meldungen können denselben Code anders beschreiben.
3. Im echten `raw/semgrep.sarif` die Regel, Datei und Fundstelle suchen.
4. In `findings.json` die Klasse `sast` und Severity `HIGH` zeigen. Die normalisierte Severity stammt aus der Zuordnung des SARIF-Levels.
5. In `thresholds.yaml` zeigen: `sast` + `HIGH` ergibt `block`.
6. In `gate.json` das FAIL und die Entscheidung nachweisen. Der verwundbare Webdienst wird im normalen Ablauf nicht gestartet.
7. Im bereinigten `app.py` die Parameterbindung erklären und im zugehörigen Fixed-Lauf zeigen, dass keine aktiven blockierenden Findings übrig bleiben. Andere Warnungen können weiterhin vorhanden sein.

Damit lässt sich die Verbindung zwischen **Codefehler, Scannerregel, Report, Policy und Entscheidung** nachvollziehbar erklären.

## 15. Was gehört zum funktionierenden Kern, was ist nur vorbereitet?

Der nachgewiesene Kern umfasst die drei Programme, Scanner-Orchestrierung, Gates, Reports, lokale Online-/Offline-Nachweise und den bestätigten GitHub-Push-Lauf. Die automatisierten Tests sichern ausgewählte Fehlerfälle und Regressionen ab.

[infra/docker-compose.tooling.yml](infra/docker-compose.tooling.yml) ist ein experimenteller Entwurf für zusätzliche Dienste. Ein erfolgreiches `compose config` würde nur die Konfiguration prüfen. Es belegt weder einen funktionierenden DefectDojo-Betrieb noch Vault-Injektion oder Registry-Veröffentlichung. [defectdojo_import.py](scripts/defectdojo_import.py) ist ein separat aufzurufendes optionales Importwerkzeug. Auch eine lokal kopierte SBOM ist keine signierte Registry-Attestation.

In der Prüfung deshalb immer vom **belegten Umfang** ausgehen: zeigen, welche Checks wirklich liefen, welches Ergebnis sie meldeten und welche Entscheidung unsere Policy daraus getroffen hat. Für aktuelle Messwerte und Grenzen bleiben [NACHPRUEFUNG.md](docs/NACHPRUEFUNG.md) und die zugehörigen Rohdaten maßgeblich.
