# DevSecOps-Pipeline

Automatisierte Security-Pipeline für drei Python-Programme, entwickelt als Lehrprojekt im Fach IT-Sicherheit (DHBW).

Jedes Programm liegt in einer absichtlich verwundbaren (`vulnerable`) und einer bereinigten (`fixed`) Variante vor.
Die Pipeline erkennt die Schwachstellen der verwundbaren Variante und lehnt sie ab; die bereinigte Variante besteht die Policy.

## Programme

| Programm | Beschreibung |
|---|---|
| Flask-API | REST-API mit SQLite-Datenbank; demonstriert SQL-Injection, XSS und Shell-Injection |
| Konfigurations-CLI | Kommandozeilenwerkzeug mit YAML-Konfiguration; demonstriert unsichere Deserialisierung und TLS-Probleme |
| HTTP-Dateidienst | Einfacher Datei-Server; demonstriert Path Traversal und hartcodierte Secrets |

## Sicherheitsprüfungen

Die Pipeline setzt acht Werkzeuge ein:

| Werkzeug | Prüfbereich |
|---|---|
| Gitleaks | Secrets im Code und in der Git-Historie |
| Semgrep | SAST: gefährliche Code-Muster und Datenflüsse |
| Bandit | SAST: Python-spezifische Sicherheitsprobleme |
| Trivy | SCA: Abhängigkeiten und Image-Komponenten |
| Syft | SBOM: Komponentenverzeichnis |
| hadolint | Statische Dockerfile-Prüfung |
| Dockle | Container-Image-Prüfung |
| OWASP ZAP | DAST: passiver Scan am laufenden Webdienst |

## Schnellstart

→ [Pipeline-Dokumentation und Befehle](devsecops-pipeline/README.md)

## Automatisierung

Push und Pull Request starten GitHub Actions automatisch.
Drei Programme × zwei Varianten = sechs parallele Matrixfälle.
Der grüne Demo-Job bestätigt, dass verwundbare Varianten abgelehnt und bereinigte Varianten freigegeben wurden.

**Automatischer Push-Lauf nachgewiesen:** Workflow *DevSecOps demo verification #1*, Commit `234b46a` auf `validation/pipeline-pruefung`, Laufzeit **3 Minuten und 2 Sekunden**.

## Hinweis

Die verwundbaren Varianten enthalten ausschließlich künstliche Demo-Secrets.
Niemals echte Zugangsdaten in die Workloads eintragen.