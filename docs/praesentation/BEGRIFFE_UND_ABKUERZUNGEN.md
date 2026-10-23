# Begriffe und Abkürzungen – DevSecOps-Präsentation

Alle Fachbegriffe und Abkürzungen, die in der Präsentation, im Sprechtext und in der Demo vorkommen. Sortiert nach Themenbereich.

---

## Methodiken und Konzepte

| Begriff / Abkürzung | Ausschreibung / Definition |
|---|---|
| **DevSecOps** | Development, Security, Operations – Ansatz, bei dem Sicherheitsprüfungen von Anfang an fest in den Entwicklungs- und Betriebsprozess integriert werden, anstatt sie am Ende nachzulagern. |
| **CI** | Continuous Integration – automatischer Prozess, der bei jedem Code-Push Tests und Prüfungen auslöst, hier über GitHub Actions. |
| **CD** | Continuous Delivery / Continuous Deployment – automatisches Ausliefern oder Veröffentlichen von Software nach bestandener CI-Prüfung. Im Projekt nur optional mit `REGISTRY`-Variable. |
| **Pipeline** | Abfolge automatischer Schritte (Scans, Gates, Tests), die bei einem Push nacheinander ausgeführt werden. |
| **Gate** | Entscheidungspunkt in der Pipeline: PASS, FAIL oder ERROR. Erst nach PASS geht es weiter. |
| **Fail Closed** | Sicherheitsprinzip: Wenn ein Scanner ausfällt oder kein Report vorhanden ist, wird das Ergebnis als Fehler (ERROR) gewertet – niemals als „sauber". Gegenteil: Fail Open. |
| **Policy as Code** | Sicherheitsregeln (z. B. Schwellenwerte, Ausnahmen) werden als Dateien im Repository versioniert und können wie Code überprüft und geändert werden. |
| **Workload** | Eines der drei geprüften Programme (Flask-API, CLI, Dateidienst) in einer Variante (vulnerable oder fixed). |
| **Vulnerable** | Absichtlich unsichere Variante eines Programms – soll vom Gate abgelehnt werden (FAIL). |
| **Fixed** | Bereinigte, korrigierte Variante eines Programms – soll das Gate bestehen (PASS). |
| **Triage** | Manuelle Bewertung eines Scanner-Befunds: Ist das Finding echt, ausnutzbar, ein Fehlalarm? |
| **False Positive (FP)** | Fehlalarm – Scanner meldet ein Problem, das nach manueller Prüfung keines ist. |
| **Suppression / Ausnahme** | Dokumentierte, begründete und zeitlich begrenzte Ausnahme für einen konkreten Befund, der nach Triage als nicht blockierend eingestuft wurde. |
| **Deduplizierung** | Zusammenführen von gleichen Befunden aus verschiedenen Scannern. Im Projekt: Finding-ID + Testklasse als Schlüssel, damit SCA- und Image-Policy nicht verwechselt werden. |
| **Exit-Code** | Zahl, die ein Programm beim Beenden zurückgibt. Im Projekt: `0` = PASS, `1` = FAIL (Security-Ablehnung), `2` = ERROR (technischer Fehler). |

---

## Scanner-Kategorien

| Begriff / Abkürzung | Ausschreibung / Definition |
|---|---|
| **SAST** | Static Application Security Testing – Analyse des Quellcodes ohne das Programm zu starten. Findet gefährliche Code-Muster, unsichere Aufrufe, Datenflüsse. Werkzeuge: Semgrep, Bandit. |
| **SCA** | Software Composition Analysis – Prüfung der verwendeten Bibliotheken und Abhängigkeiten auf bekannte Schwachstellen. Werkzeug: Trivy (Dateisystem-Modus). |
| **DAST** | Dynamic Application Security Testing – Prüfung eines tatsächlich laufenden Dienstes durch Beobachtung von HTTP-Anfragen und -Antworten. Im Projekt: passiver ZAP-Scan. |
| **Passiver Scan** | DAST-Modus, bei dem der Scanner nur beobachtet und keine aktiven Angriffe startet. ZAP im passiven Modus führt keine SQL-Injection- oder XSS-Angriffe durch. |
| **Aktiver Scan** | DAST-Modus mit echten Angriffsversuchen. Im Projekt **nicht** eingesetzt. |
| **SBOM** | Software Bill of Materials – Komponentenverzeichnis: eine Liste aller im Programm oder Image enthaltenen Pakete und Bibliotheken. Werkzeug: Syft. Bewertet selbst keine Schwachstellen. |

---

## Eingesetzte Werkzeuge

| Werkzeug | Vollständige Bezeichnung / Erklärung |
|---|---|
| **Semgrep** | Open-Source-SAST-Tool. Prüft Code anhand selbstgeschriebener Muster (Regeln). Im Projekt: 9 eigene Lehrregeln, z. B. für SQL-Injection, XSS, Shell-Ausführung. |
| **Bandit** | Python-spezifisches SAST-Tool. Erkennt gefährliche Python-Aufrufe wie `os.system`, MD5, Debug-Modus, unsichere TLS-Einstellungen. |
| **Trivy** | Vielseitiger Open-Source-Scanner für Dateisysteme (SCA), Container-Images (Image-Scan) und Secrets. Liefert CVE-Berichte. |
| **Gitleaks** | Sucht nach Secrets (Passwörter, API-Keys, Tokens) im Quellcode und in der gesamten Git-Historie. |
| **hadolint** | Statisches Prüfwerkzeug für Dockerfiles. Prüft die Bauanleitung des Container-Images auf Probleme. |
| **Dockle** | Prüft das fertig gebaute Container-Image auf Sicherheitsprobleme (z. B. Root-Nutzer, Paketmanager-Cache). |
| **OWASP ZAP** | OWASP Zed Attack Proxy – Open-Source-DAST-Tool. Im Projekt nur passiv und OpenAPI-begrenzt eingesetzt. |
| **Syft** | Erstellt eine SBOM (Komponentenverzeichnis) im CycloneDX-Format. Findet selbst keine Schwachstellen. |
| **GitHub Actions** | CI/CD-Plattform von GitHub. Führt bei Push oder Pull Request automatisch Workflows aus. |
| **Docker** | Plattform für Container. Scanner und Programme laufen als isolierte Container. |
| **pytest** | Python-Test-Framework. Wird für die 41 Unit-Tests der Pipeline-Logik verwendet. |

---

## Schwachstellen und Sicherheitsbegriffe

| Begriff / Abkürzung | Ausschreibung / Definition |
|---|---|
| **CVE** | Common Vulnerabilities and Exposures – öffentlich registrierte, benannte Schwachstelle in einer konkreten Software-Version, z. B. `CVE-2023-25577`. Vergeben von MITRE. |
| **CWE** | Common Weakness Enumeration – Katalog von Schwachstellen-Arten (z. B. CWE-89 = SQL-Injection). Nicht dasselbe wie CVE. |
| **CVSS** | Common Vulnerability Scoring System – standardisiertes Bewertungssystem für den Schweregrad einer Schwachstelle (0–10). |
| **SQL-Injection** | Angriff, bei dem Benutzereingaben als SQL-Code interpretiert werden, weil sie direkt in eine SQL-Abfrage eingebaut werden. Gegenmaßnahme: Parameterbindung. |
| **XSS** | Cross-Site Scripting – Angriff, bei dem Benutzereingaben als HTML/JavaScript im Browser ausgeführt werden. Gegenmaßnahme: HTML-Escaping. |
| **Path Traversal** | Angriff, bei dem mit `../`-Pfadanteilen aus einem erlaubten Verzeichnis herausgegangen wird. Im Dateidienst-Beispiel demonstriert. |
| **Secret** | Zugangsdaten im Code oder in der Git-Historie (API-Keys, Passwörter, Tokens). Im Projekt: künstliche Demo-Secrets im verwundbaren Dateidienst. |
| **TLS** | Transport Layer Security – Verschlüsselungsprotokoll für Netzwerkverbindungen (früher SSL). `verify=False` deaktiviert die Zertifikatsprüfung, was Man-in-the-Middle-Angriffe ermöglicht. |
| **SSRF** | Server-Side Request Forgery – Angreifer bringt den Server dazu, interne oder unerlaubte Anfragen zu stellen. |
| **Severity** | Schweregrad eines Findings: INFO, LOW, MEDIUM, HIGH, CRITICAL. |
| **Finding** | Eine einzelne Sicherheitsmeldung eines Scanners. Ob daraus eine Ablehnung folgt, entscheidet die Policy. |
| **Blocking** | Ein Finding, das laut Policy einen Gate-FAIL auslöst. Im Gegensatz zu Warnungen (warn) oder reinen Infos. |

---

## Formate und Dateien

| Begriff / Abkürzung | Ausschreibung / Definition |
|---|---|
| **SARIF** | Static Analysis Results Interchange Format – standardisiertes JSON-Austauschformat für Ergebnisse statischer Analyse. Wird von Semgrep, Bandit und hadolint erzeugt. |
| **CycloneDX** | Offenes SBOM-Format (Software Bill of Materials). Syft erstellt SBOMs in diesem Format (`sbom.cdx.json`). |
| **OpenAPI** | Standard zur Beschreibung von HTTP-APIs. ZAP nutzt die `openapi.json` im Projekt, um gezielt nur die beschriebenen Endpunkte zu prüfen. |
| **gate.json** | Ausgabedatei des Gate-Skripts. Enthält `status` (PASS/FAIL/ERROR), `blocking` (Anzahl aktiver Blocker) und `suppressed` (Anzahl angewandter Ausnahmen). |
| **run.json** | Protokolldatei eines Pipeline-Laufs: Workload, Images, Checkzustände, Run-ID. |
| **findings.json** | Normalisierte, vereinheitlichte Liste aller Findings aus allen Scannern. Eingabe für das Gate. |
| **suppressions.json** | Datei mit dokumentierten Ausnahmen (Owner, Begründung, Ablaufdatum, Bedingungen). |
| **thresholds.yaml** | Policy-Datei: legt fest, welche Schweregrade je Testklasse blockieren, warnen oder nur informieren. |
| **smoke-only.json** | Ausgabedatei eines Smoke-Tests. Enthält `security_scanned: false` – kein Security-Gate wurde ausgeführt. |

---

## Container und Infrastruktur

| Begriff / Abkürzung | Ausschreibung / Definition |
|---|---|
| **Container** | Isolierte Laufzeitumgebung für ein Programm, basierend auf einem Image. Kein vollständiges Betriebssystem, aber eigenes Dateisystem, Netzwerk und Prozessraum. |
| **Image** | Unveränderliche Vorlage für einen Container. Wird aus einem Dockerfile gebaut. |
| **Dockerfile** | Textdatei mit Bauanleitung für ein Container-Image. Beschreibt Basis-Image, installierte Pakete, Programmcode und Startbefehl. |
| **Alpine** | Sehr kleines Linux-Betriebssystem, das häufig als Basis für Container-Images verwendet wird. Paketmanager: `apk`. |
| **Digest / SHA256** | Eindeutiger kryptografischer Fingerabdruck eines Images. Im Projekt: Images werden per Digest festgelegt, damit immer dieselbe Version verwendet wird. |
| **Registry** | Zentrales Lager für Container-Images (z. B. Docker Hub, GitHub Container Registry). Im Projekt optional, nicht produktiv angebunden. |
| **Docker-in-Docker** | Betrieb von Docker innerhalb eines Docker-Containers. Wird für den CI-Betrieb auf GitHub Actions benötigt. |
| **Host-Port** | Port des eigentlichen Rechners (außerhalb des Containers). Im Projekt: der Dateidienst veröffentlicht keinen Host-Port, ist also nicht über `localhost:8080` erreichbar. |
| **apk** | Package manager von Alpine Linux. Entspricht `apt` bei Debian/Ubuntu. |

---

## Projekt-spezifische Begriffe

| Begriff / Abkürzung | Ausschreibung / Definition |
|---|---|
| **Matrix (GitHub Actions)** | Konfiguration, die mehrere Jobs parallel mit verschiedenen Parametern startet. Im Projekt: 3 Programme × 2 Varianten = 6 Matrixfälle. |
| **Smoke-Test** | Einfacher Funktionstest: Startet das Programm und prüft, ob es grundsätzlich läuft – **ohne** Security-Scanner und Gate. Beweist Lauffähigkeit auch für verwundbare Varianten. |
| **Offline-Lauf** | Pipeline-Durchlauf ohne Internetverbindung, mit lokal gecachten Scanner-Images und Datenbanken. |
| **Online-Lauf** | Pipeline-Durchlauf mit Internetverbindung; Scanner laden aktuelle Datenbanken. |
| **Run-ID** | Eindeutige Kennung eines Pipeline-Laufs, z. B. `20261021-094239-01-flask-api-vulnerable-39dd26`. Besteht aus Datum, Uhrzeit, Programm, Variante und Zufallsanteil. |
| **Testklasse** | Kategorie eines Findings: `sast`, `sca`, `secrets`, `image`, `dast`. Bestimmt zusammen mit der Severity, ob ein Finding blockiert. |
| **Parameterbindung** | Sichere SQL-Technik: Benutzereingaben werden als separate Werte übergeben (`?`-Platzhalter), nicht in den SQL-Text eingebaut. Verhindert SQL-Injection. |
| **Vault** | HashiCorp Vault – Tool zur sicheren Verwaltung von Secrets. Im Projekt erwähnt, aber **nicht** produktiv angebunden. |
| **DefectDojo** | Open-Source-Plattform zur Verwaltung von Schwachstellenbefunden aus verschiedenen Scannern. Im Projekt erwähnt, aber **nicht** produktiv angebunden. |
| **OWASP** | Open Worldwide Application Security Project – gemeinnützige Organisation, die Standards und Tools für Anwendungssicherheit entwickelt (z. B. ZAP, OWASP Top 10). |
| **DKL-DI-0004** | Konkrete Dockle-Regel: „Verwende `apk add` mit `--no-cache`." Im Projekt: löst die einzige dokumentierte Ausnahme aus, weil das offizielle Python-Alpine-Image diese Zeile enthält. |
| **package-cache-empty** | Zusätzlicher Check im Projekt: prüft, ob tatsächlich kein Paket-Cache im Image vorhanden ist. Voraussetzung für die Dockle-Ausnahme. |
| **Owner** | Verantwortliche Person oder Gruppe für eine Suppression/Ausnahme. Im Projekt: „DevSecOps project group". |
