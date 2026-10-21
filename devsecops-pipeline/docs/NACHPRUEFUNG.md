# Nachprüfung der korrigierten Pipeline

Stand: 21.10.2026, Branch `validation/pipeline-pruefung`.
Die Erstprüfung in [VALIDIERUNG.md](VALIDIERUNG.md) bleibt als historischer Befund erhalten.
Diese Nachprüfung bezieht sich auf den danach korrigierten Arbeitsstand.

**Ergebnis:** Alle sechs Programme lassen sich bauen und isoliert ausführen.
Die Security-Demo erfüllt online und mit deaktiviertem externem Scanner-Netzwerk
alle Erwartungen: drei Security-Ablehnungen (1), drei bestandene Fixed-Läufe (0).
Die Gate-Policy wurde dafür nicht abgesenkt.

## Echte Ergebnisse

| Programm / Variante | Online-Exit | Offline-Exit | Blockierende Findings offline | Geprüfte Ausnahmen offline |
|---|---|---|---|---|
| 01-flask-api-fixed | 0 | 0 | 0 | 1 |
| 01-flask-api-vulnerable | 1 | 1 | 8 | 0 |
| 02-cli-deps-fixed | 0 | 0 | 0 | 1 |
| 02-cli-deps-vulnerable | 1 | 1 | 4 | 0 |
| 03-container-service-fixed | 0 | 0 | 0 | 1 |
| 03-container-service-vulnerable | 1 | 1 | 10 | 0 |

Alle sechs separaten Smoke-Tests endeten mit 0. Zusätzlich wird die CLI in jedem
vollständigen CLI-Pipeline-Lauf tatsächlich installiert und ausgeführt. Die
bereinigten Webdienste wurden erst nach bestandenem Image-Gate gestartet;
Healthcheck, konkrete API-Aufrufe und passiver OpenAPI-ZAP-Scan waren erfolgreich.
Die bewusst verwundbaren Webdienste werden vom Gate vorher gestoppt. Ihre
separaten Smoke-Tests belegen Lauffähigkeit, keine Security-Freigabe.

Nachweise: [Ergebnisse als JSON](validation/2026-10-21-fixed/results.json),
[Findings-Bericht](validation/2026-10-21-fixed/FINDINGS_REPORT.md),
[Metriken](validation/2026-10-21-fixed/metrics.csv) und
[vollständiges Archiv](validation/2026-10-21-fixed/evidence.zip).
Das Archiv enthält Rohreports, Gateentscheidungen, Manifeste, Zeitdaten, Logs
und einen Quellcode-Snapshot. Der letzte vollständige Offline-Durchgang stimmt
mit dem finalen Implementierungs-Hash überein:
`acbe04c1314d0700b0c96e0a527a9134971b44dcef64ef8dce91990d51480f50`.

## Korrekturen zu den zehn Befundgruppen

| Erstbefund | Umsetzung und Prüfung |
|---|---|
| CI-/Hook-Dateien im falschen Verzeichnis; falscher History-Stamm | Einstiege am Git-Stamm, korrekte Arbeitsverzeichnisse, sechs GitHub-Matrixfälle; History-Scan fand den echten Git-Stamm und scannte die Historie |
| Ausgefallene Scanner liefern PASS | Erfolgreiche Checkzustände und gültige Pflichtberichte sind erforderlich; komplette Runtime-Störung endet mit 2 und ERROR, auch im vollständigen Regressionstest |
| Fixed-Läufe scheitern an alten Dependencies/Images | Aktuelle direkte und transitive Pins; feste Basis-Digests; reale grüne Fixed-Läufe. Ein bestätigter Dockle-Fehlalarm wird eng und befristet behandelt |
| CLI nicht installierbar und nicht ausgeführt | Kompatible isolierte CLI-Runtimes, Build plus echter Start beider Varianten. Der Negativfall verwendet ausdrücklich `yaml.unsafe_load` und alte verwundbare Komponenten |
| SCA-Deduplizierung umgeht Image-Policy | Testklasse bleibt Teil des Deduplizierungsschlüssels; HIGH im Image blockiert trotz gleicher SCA-CVE |
| GitLab-DAG startet vor Gate / braucht fehlende Jobs | Beide CI-Dienste verwenden einen synchronen Orchestrator; CLI/Web unterscheiden sich im Manifest, keine widersprüchlichen bedingten Container-Jobs |
| GitHub blendet Demo-Secrets aus | Separater Workload-Scan ohne Ausnahmen sowie History-Scan; dieselbe Logik für lokale Läufe und CI |
| Shell-Einstiege / optionale Pflichtschritte / falsche Reportreihenfolge | Native Python-Einstiege, dünner Bash-Wrapper; Build, Healthcheck und aktiviertes Publishing sind Pflicht; frische Gateentscheidung vor Bericht, eigener ERROR-/PENDING-Status |
| Dauerhafte Suppressions ohne Ablauf | Fehlende/ungültige Daten werden abgelehnt; Ablauf und zusätzliche Kontextbedingungen sind getestet |
| Fixture-Daten als Ergebnis; DAST-URLs / Abdeckung; Offline-Zusagen | Historische Fixtures getrennt; zwölf echte Security-Läufe und sechs funktionale Läufe archiviert; korrekte ZAP-URLs, explizite API-Spezifikationen, erfolgreiche Offline-Suite mit Cache und Quellcode-gebundenen Images |

## Tests und manuelle Bewertung

- **41 aktuelle Tests** bestehen unter Linux (Python 3.12.13).
- Zusammen mit den neun zusätzlichen Akzeptanzprüfungen der Erstvalidierung
  bestehen **50 Tests** unter Windows (Python 3.12.14).
- Die frühere grüne Pipeline bei komplett ausgefallener Runtime ist als echter
  Regressionstest abgedeckt. Technische Fehler und beschädigte Reports können
  keine erfolgreiche Demo vortäuschen; der Demo-Runner prüft den Gate-Nachweis.
- YAML-Syntax und die sechs automatischen GitHub-Matrixfälle wurden lokal geprüft.
- SQL-Injection, XSS-Escaping, CLI-Start und Pfadbegrenzung aus den ursprünglichen
  Akzeptanzprüfungen bestehen weiterhin.

Die konkrete Findingsbewertung steht in [FINDINGS_BEWERTUNG.md](FINDINGS_BEWERTUNG.md).
Die feste Pipeline-Grenze ist eine Policy-Entscheidung; einzelne CVEs sind damit
noch nicht als im Demo-Code ausnutzbar bewiesen. HIGH-SCA- und MEDIUM-Findings
können gemäß unveränderter Policy weiterhin Warnungen sein.

Für Dockle `DKL-DI-0004` gilt genau eine Ausnahme: nur die drei Fixed-Varianten,
nur der festgehaltene offizielle Python-Alpine-Basis-Digest, nur die geerbte
`apk add --no-network`-Buildzeile und nur nach erfolgreicher Prüfung leerer
Paket-Caches. Owner und Begründung sind hinterlegt; sie läuft am **20.11.2026** ab.
Die Meldung bleibt im Rohreport und als unterdrücktes Finding sichtbar.
Andere Images, andere Meldungstexte und ein fehlender Cache-Nachweis sind nicht
ausgenommen. Nach Ablauf ist eine erneute Bewertung nötig.

## Aussagegrenzen für die Abgabe

Der automatische GitHub-Push-Trigger und der erfolgreiche Workflow-Abschluss
sind inzwischen durch den bereitgestellten GitHub-Actions-Screenshot bestätigt:
**DevSecOps demo verification #1**, Commit `234b46a`, Branch
`validation/pipeline-pruefung`, Laufzeit **3 Minuten und 2 Sekunden**, grüner Gesamtstatus.
Lokal sind zusätzlich Konfiguration, Orchestrator und alle sechs Varianten geprüft.
Ein tatsächlicher GitLab-Lauf wurde nicht nachgewiesen; GitLab braucht einen
korrekt konfigurierten DinD-Runner. Registry-Push, externe Vault-Injektion und
DefectDojo-Betrieb sind optionale, nicht als funktionierend nachgewiesene Dienste.
Die kleine Tooling-Compose-Datei bleibt ausdrücklich ein experimenteller Entwurf.
Für die geforderten mindestens vier Security-Tools werden diese Dienste nicht benötigt.

ZAP arbeitet passiv anhand expliziter OpenAPI-Endpunkte. Ein grüner Lauf ist kein
aktiver Penetrationstest und kein Nachweis vollständiger Authentifizierung oder
Laufzeitsicherheit. Fehlende HTTP-Schnittstellen der CLI sowie nicht aktiviertes
Publishing sind im Manifest ausdrücklich als nicht ausgeführt vermerkt.

Die Online-Demo dauerte im Test etwa zehn Minuten. Die Offline-Suite zeigte beim
letzten History-Scan eine auffällige Pause: ungefähr 4265 Sekunden wurden für
diesen Check erfasst, obwohl er erfolgreich endete. Die Ursache dieser Wartezeit
ist nicht abschließend geklärt. Die Rohzeiten sind deshalb keine belastbaren
Performance-Benchmarks und kein Versprechen für die Live-Demo. Vor dem Termin
erneut vorwärmen, gespeicherte Nachweise und Video bereithalten und nur ein bis
zwei Läufe live zeigen. Scanner-Datenbanken können später neue Findings melden.
