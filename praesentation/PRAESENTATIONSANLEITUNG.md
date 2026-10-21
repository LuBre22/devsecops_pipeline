# Anleitung für die Präsentierenden

Diese Anleitung gehört zur [PowerPoint](DevSecOps_Pipeline_DHBW.pptx) und zum [Sprechtext](SPRECHTEXT.md). Sie beschreibt die Vorbereitung und die konkrete Bedienung während des Vortrags. Stand der archivierten Ergebnisse: 21.10.2026.

## 1. Rollen und Zeitplan

Die folgende Aufteilung ist ein Vorschlag und kann innerhalb der Gruppe getauscht werden. Die Rolle am Demo-Rechner sollte bei der Generalprobe feststehen.

| Person | Folien | Inhalt | Zielzeit |
|---|---|---|---|
| Lukas Breuer | 1–4 | Aufgabe, Aufbau und Vorlesungsbezug | 0:00–2:35 |
| Leo Hofmann | 5–7 | Drei Codebeispiele und Korrekturen | 2:35–4:40 |
| Maxim Krüger | 8–12 | CI, Policy, Ergebnisse und Entwicklungsprobleme | 4:40–8:15 |
| Valentin Gehrig | 13–16 | Demo, Lessons Learned und Produktionsbewertung | 8:15–13:15 |
| Alle | Fragen, bei Bedarf 17–20 | Rückfragen und Reserve | 13:15–15:00 |

Die Demo enthält Bedienzeit, deshalb ist der letzte Block länger. Währenddessen übernimmt eine andere Person die Zeitkontrolle. Alle sollten das grüne Demo-Ergebnis, die drei Exit-Codes und die ZAP-Grenzen selbst erklären können.

**Ziel:** An einem konkreten Beispiel die Verbindung zwischen Code, Scannerbefund und Gateentscheidung zeigen. Die vollständigen Nachweise aller drei Programme stehen im Archiv. In den drei Minuten Demo müssen nicht sechs neue Scannerläufe abschließen.

## 2. Was ihr spätestens am Vortag vorbereitet

1. PowerPoint öffnen und die Darstellung auf dem tatsächlichen Präsentationsrechner prüfen. Folien 1–16 bilden den Vortrag, 17–20 die Reserve. Die Referentenansicht und Bildschirmfreigabe einmal ausprobieren.
2. [Sprechtext](SPRECHTEXT.md) gemeinsam durchgehen. Begriffe wie SAST, SCA, DAST, SBOM und Gate mit eigenen Worten erklären können. Die Tabellen nicht vollständig vorlesen.
3. Docker mit Linux-Containern starten. Internetzugang für Vorbereitung und erste Builds einplanen.
4. Die unten beschriebene Vorbereitung und vollständige Demo ausführen. Neue Findings bewerten, bevor ihr den Vortrag haltet. Einen unerwartet roten Fixed-Fall nicht durch niedrigere Schwellenwerte grün machen.
5. Die tatsächlichen Berichte sichern. Die Gates der verwundbaren Varianten müssen FAIL zeigen, die bereinigten Varianten sollen PASS liefern. Ein ERROR ist kein erfolgreicher Negativtest.
6. Eine kurze eigene Aufnahme als Reserve erstellen, falls ihr Video verwenden wollt. Eine solche Aufnahme wird hier nicht mitgeliefert. Aufzeichnungen bei der Vorführung als Aufzeichnung bezeichnen.
7. Die Dockle-Ausnahme prüfen: dokumentiertes Ablaufdatum **20.11.2026**. Bei einem späteren Termin ist eine erneute fachliche Bewertung nötig.
8. Einen kompletten Probedurchlauf mit Sprecherwechseln und Demo stoppen. Ziel sind ungefähr 13:15 Minuten plus Reserve bis 15 Minuten.

### Befehle zur Vorbereitung

Die folgenden Befehle gelten im Verzeichnis **`devsecops-pipeline`**, also vom Git-Stamm aus zunächst:

```powershell
cd devsecops-pipeline
```

Dann:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
python scripts/prepare.py
python scripts/demo.py
$LASTEXITCODE
```

Die **Demo-Suite** soll mit `0` enden: alle sechs Erwartungen sind erfüllt. In `reports/demo-results.json` müssen die sechs Einträge `matched: true` enthalten. Jeder Eintrag nennt die zugehörige Run-ID.

`prepare.py` bereitet Scanner und Trivy-Daten vor. Die vollständige Demo baut die Workloads, soweit ihre Gates das zulassen. Früh abgelehnte verwundbare Webdienste könnt ihr zusätzlich funktional ausführen:

```powershell
python scripts/smoke.py workloads/01-flask-api/vulnerable
python scripts/smoke.py workloads/03-container-service/vulnerable
```

Diese Smoke-Tests belegen die Lauffähigkeit und sind keine Security-Freigabe. Beim wiederverwendeten Build läuft hadolint mit; ein vollständiger Security-Scan und ein Gate erfolgen dabei nicht.

## 3. Archivierte Nachweise als verlässliche Reserve öffnen

Die Dateien unter [docs/validation/2026-10-21-fixed](../devsecops-pipeline/docs/validation/2026-10-21-fixed) sind gespeicherte Nachweise. Sie werden beim Vortrag ausdrücklich als Ergebnisse vom 21.10.2026 benannt.

Direkt verfügbar sind:

- [Findings-Bericht aller Programme](../devsecops-pipeline/docs/validation/2026-10-21-fixed/FINDINGS_REPORT.md).
- [Messwerte und Run-IDs](../devsecops-pipeline/docs/validation/2026-10-21-fixed/results.json).
- [Rohdatenarchiv](../devsecops-pipeline/docs/validation/2026-10-21-fixed/evidence.zip).

Für einzelne Rohreports und Gate-Dateien das Archiv **vorher** entpacken. Im Projektverzeichnis `devsecops-pipeline` unter PowerShell:

```powershell
Expand-Archive -LiteralPath "docs/validation/2026-10-21-fixed/evidence.zip" -DestinationPath "reports/vortrag-archiv"
```

Den Befehl einmal für ein neues Zielverzeichnis ausführen. Ist das Verzeichnis bereits vorhanden, könnt ihr die vorhandenen Dateien verwenden; für eine erneute Extraktion einen neuen Zielnamen wählen. Die ZIP-Datei enthält selbst einen Ordner `reports/`. Die Gate-Dateien liegen danach deshalb unter **`reports/vortrag-archiv/reports/<Run-ID>/gate.json`**.

Für den letzten vollständigen Offline-Durchgang sind diese Run-IDs im Archiv enthalten:

| Programm | Vulnerable: FAIL | Fixed: PASS |
|---|---|---|
| Flask-API | `20261021-094239-01-flask-api-vulnerable-39dd26` | `20261021-094047-01-flask-api-fixed-ffd215` |
| Konfigurations-CLI | `20261021-094444-02-cli-deps-vulnerable-a201e5` | `20261021-094326-02-cli-deps-fixed-1c5456` |
| HTTP-Dateidienst | `20261021-094744-03-container-service-vulnerable-d6b5a1` | `20261021-094540-03-container-service-fixed-51a564` |

In jedem Run-Ordner zuerst `run.json`, danach einen passenden Report in `raw/` und zuletzt `gate.json` zeigen. Im Dateidienst-Negativfall eignet sich `raw/gitleaks.json`; beim Positivfall sind unter anderem die ZAP-Ergebnisse und die dokumentierte Ausnahme interessant.

Bei Verwendung selbst neu erzeugter Ergebnisse können die Finding-Zahlen abweichen. Dann die tatsächlich gezeigten Werte nennen und den Zeitpunkt ihres Laufs angeben.

## 4. Was vor Vortragsbeginn geöffnet sein sollte

| Fenster oder Datei | Verwendungszweck |
|---|---|
| PowerPoint, Folie 1 | Vortrag; beim Wechsel zur Demo auf Folie 13 bleiben |
| Referentenansicht oder Sprechtext auf zweitem Bildschirm | Orientierung, ohne Bedienhinweise vorzulesen |
| GitHub: Repository, Registerkarte Actions | Tatsächliches Push-Event, Branch und sechs Matrixfälle zeigen |
| Editor: beide `03-container-service/.../app.py` | Künstliches Secret und ungeprüften Pfad mit Fixed-Code vergleichen |
| Terminal im Projektverzeichnis | Genau einen vorbereiteten Pipeline-Aufruf starten |
| Archivierter Findings-Bericht und zwei Dateidienst-Gates | Ergebnisvergleich auch bei laufendem Scanner ermöglichen |
| Ergebnisse von Flask und CLI im Bericht | Beleg für die beiden anderen Programme bei Rückfragen |

Für den Browser wird gegebenenfalls eine funktionierende GitHub-Anmeldung benötigt. Der Dateidienst veröffentlicht während der Pipeline **keinen Host-Port**. Er ist daher nicht einfach unter `localhost:8080` im Browser erreichbar. Für die Demo werden Code, Prozessausgabe und Reports gezeigt.

## 5. Demo auf Folie 13: genau drei Minuten

### 0:00–0:30: Automatischen Start zeigen

Im vorbereiteten GitHub-Actions-Lauf das tatsächliche Event und den Branch zeigen. Die sechs Matrixfälle benennen. Ein dokumentierter älterer Lauf ist ein gültiger gespeicherter Nachweis, wenn ihr ihn so bezeichnet.

**Kernaussage:** Der Workflow startet bei Push automatisch. Der grüne Demo-Job bedeutet, dass vulnerable korrekt abgelehnt und fixed korrekt akzeptiert wurde.

Ein neuer Live-Push ist für diesen Nachweis nicht nötig. Falls ihr einen zeigen wollt, nur eine vorher vereinbarte, gespeicherte Änderung pushen und während der CI-Laufzeit mit lokalen beziehungsweise archivierten Ergebnissen weitermachen. Den neuen Lauf erst als erfolgreich bezeichnen, wenn er tatsächlich fertig ist.

### 0:30–1:00: Code und einen Live-Aufruf zeigen

Im verwundbaren Dateidienst das künstliche Secret und `open("/app/data/" + name, ...)` zeigen. Dann den vorgesehenen Negativfall starten:

```powershell
python scripts/pipeline.py workloads/03-container-service/vulnerable
```

Die erwartete **Security-Ablehnung** ist `FAIL` mit Pipeline-Exit `1`. Unter PowerShell `$LASTEXITCODE` erst nach Ende des Python-Aufrufs auswerten. Solange er läuft, liegt noch kein abschließendes neues Ergebnis vor.

### 1:00–2:20: Rohbefund und Gate erklären

Während der Scanner arbeitet, in den vorher geöffneten archivierten Nachweis wechseln. Als Quelle den gespeicherten Lauf vom 21.10.2026 nennen.

Im Dateidienst-Negativfall:

1. `run.json`: Workload und erfolgreich ausgeführte Checks zeigen.
2. `raw/gitleaks.json`: eine Erkennung der künstlichen Secrets zeigen.
3. `gate.json`: `status: "FAIL"` und `blocking: 10` zeigen. Die Zehn ist die Gesamtzahl aktiver blockierender Findings dieses archivierten Laufs, nicht die Zahl unabhängiger Secret-Leaks.

Danach im archivierten Fixed-Lauf `status: "PASS"`, `blocking: 0` und `suppressed: 1` zeigen. Die Ausnahme kurz als geprüften Dockle-Befund einordnen. PASS bedeutet keine vollständige Fehlerfreiheit.

### 2:20–3:00: Positivfall und Rückkehr zu den Folien

Die Gegenmaßnahmen im Fixed-Code benennen: aufgelöster und begrenzter Pfad sowie Token aus der Umgebung. Falls der Rechner frei ist und genügend Zeit besteht, kann ein neuer Fixed-Lauf gestartet werden:

```powershell
python scripts/pipeline.py workloads/03-container-service/fixed
```

**Diesen Aufruf nicht hinter den noch laufenden Negativfall in dasselbe belegte Terminal tippen.** Entweder dessen Ende abwarten oder ein zweites vorbereitetes Terminal verwenden. Für den engen Zeitplan reicht der gespeicherte Positivnachweis. Kein vollständiger Abschluss innerhalb der drei Minuten wird versprochen.

Zum Schluss auf die dokumentierten Ergebnisse der beiden anderen Programme verweisen. Nach spätestens drei Minuten zurück zu Folie 14 wechseln. Neue Scannerläufe dürfen im Hintergrund weiterarbeiten.

## 6. Umgang mit Wartezeiten und unerwarteten Ergebnissen

| Situation | Vorgehen und passende Aussage |
|---|---|
| Scanner läuft noch | Auf das Archiv wechseln: „Der neue Lauf arbeitet noch. Hier zeigen wir den gespeicherten Nachweis vom 21. Oktober.“ |
| Docker läuft nicht oder Pflichtreport fehlt | Als ERROR / 2 benennen. Gespeicherten korrekten Lauf zeigen und die technische Ursache nach dem Vortrag untersuchen. |
| Vulnerable liefert Exit 1 | Gate-Datei prüfen. Nur FAIL mit aktivem blockierendem Finding ist der erwartete Negativtest. |
| Fixed liefert jetzt FAIL | Neue Findings öffnen. Datenbankupdates können neue CVEs melden. Das aktuelle Ergebnis offen erklären und vom älteren archivierten PASS unterscheiden. |
| Ausnahme ist abgelaufen | Erneute Triage erforderlich. Nicht nur für den Vortrag das Ablaufdatum hochsetzen. |
| GitHub oder Internet fällt aus | Lokal vorhandene Rohberichte, Gate-Dateien und den archivierten Bericht verwenden. Einen gegebenenfalls vorhandenen Screenshot als gespeicherten Trigger-Nachweis benennen. |
| Keine Zeit für den vollständigen Positivlauf | Archivierten Fixed-Lauf zeigen. Nicht auf den laufenden Scanner warten, wenn dadurch Lessons Learned und Bewertung entfallen. |
| PowerPoint fällt aus | Vorher eine eigene PDF-Reserve exportieren oder mit einem anderen Präsentationsprogramm testen. Ein PDF gehört nicht zum hier gelieferten Paket. |

Offline nur nach einem erfolgreich geprobten vollständigen Offline-Durchgang präsentieren:

```powershell
python scripts/prepare.py --offline
python scripts/demo.py --offline
```

Diese Befehle dienen der Vorbereitung. Die gesamte Suite wird nicht während der drei Minuten Live-Demo abgewartet. Ein früherer History-Scan erfasste eine ungeklärte Pause von rund 4265 Sekunden. Ein voller Cache ist deshalb kein Versprechen einer bestimmten Laufzeit.

## 7. Antworten, die jedes Gruppenmitglied beherrschen sollte

| Frage | Belastbare kurze Antwort |
|---|---|
| Warum ist der Workflow trotz verwundbarem Code grün? | `demo.py` überprüft die erwarteten negativen und positiven Fälle. Die verwundbaren Workload-Gates bleiben FAIL. |
| Was bedeuten 0, 1 und 2? | Bei `pipeline.py`: Policy bestanden, Security-Ablehnung oder technischer Fehler. `demo.py` hat eigene Exit-Bedeutungen: 0 bedeutet, dass alle ausgewählten Erwartungen erfüllt sind. |
| Habt ihr mit ZAP SQL-Injection bewiesen? | Unser ZAP-Lauf ist passiv und OpenAPI-begrenzt. SQL-Injection bewerten wir anhand von Codeanalyse und gezielten Akzeptanzprüfungen. |
| Sind die drei Programme wirklich lauffähig? | Ja, alle sechs Varianten haben separate dokumentierte Smoke-Tests. Früh abgelehnte Webvarianten werden im normalen Scan-Pfad nicht gestartet. |
| Warum gibt es Warnungen bei fixed? | Das Gate bewertet definierte Schweregrade. PASS bedeutet keine aktiven Blocker nach Policy; Warnungen und eine geprüfte Ausnahme können verbleiben. |
| Wie verhindert ihr falsches Grün bei Scanner-Ausfall? | Erfolgreicher Checkstatus, lesbarer plausibler Pflichtreport und konsistente Gateentscheidung sind erforderlich. |
| Habt ihr Vault oder DefectDojo produktiv angebunden? | Für den nachgewiesenen Ablauf nicht. Die optionale Tooling-Compose-Datei ist ein experimenteller Entwurf. |
| Ist die SBOM vollständig für das fertige Image? | Syft inventarisiert hier das Quellverzeichnis. Das ist nicht automatisch ein vollständiges Inventar aller Betriebssystemkomponenten im Image. |
| Implementiert der Dateidienst Authentifizierung? | Nein. Er verlangt einen Token als Startkonfiguration, prüft ihn aber nicht pro HTTP-Request. |
| Könnte die Pipeline in Produktion laufen? | Der Scan-Pfad ist eine Grundlage für CI. Produktionsfreigaben brauchen zusätzliche technische Kontrollen und verbindliche Betriebsprozesse. |

Bei einer unbekannten Detailfrage die passende Datei oder Reservefolie öffnen. Keine spontane vollständige Exploitability-, Laufzeit- oder Sicherheitsgarantie aus einem grünen Scan ableiten.

## 8. Bearbeiten und Abgeben

Die [PowerPoint](DevSecOps_Pipeline_DHBW.pptx) enthält bearbeitbare Texte, Codebeispiele, native Tabellen und ein bearbeitbares Ablaufdiagramm. Logo und Welle sind Bilddateien. In PowerPoint sind bereits zusätzliche Sprechernotizen vorhanden; der ausformulierte [Sprechtext](SPRECHTEXT.md) liegt separat zum gemeinsamen Üben vor.

Wenn Folien, Namen, Zahlen oder Reihenfolge geändert werden, den Sprechtext und die Zeitplanung mit anpassen. Vor der Abgabe noch einmal speichern und eine Probe auf dem Präsentationsrechner durchführen. Die Präsentationsdatei selbst muss entsprechend der Prüfungsanforderung abgegeben werden; README und Sprechtext ersetzen diese Abgabe nicht.
