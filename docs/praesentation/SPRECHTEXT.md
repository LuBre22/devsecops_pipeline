# Sprechtext zur DevSecOps-Präsentation

Für **Lukas Breuer, Leo Hofmann, Maxim Krüger und Valentin Gehrig** im Fach **IT-Sicherheit bei Herrn Graupner**.

Der Text gehört zur [PowerPoint](DevSecOps_Pipeline_DHBW.pptx). Er ist als ausformulierter Vorschlag zum Üben gedacht. Die fett markierten Bedienhinweise werden **nicht vorgelesen**. Technische Details können bei Rückfragen mit eigenen Worten ergänzt werden. Maßgeblich sind die tatsächlichen Ergebnisse des gezeigten Laufs.

Die 16 Vortragsfolien haben zusammen ein Zielbudget von **13:15 Minuten einschließlich drei Minuten Demo**. Bis zur 15-Minuten-Grenze bleiben etwa 1:45 Minuten für Wechsel, Verzögerungen oder Fragen. Die Folien 17–20 sind Reserve. Eine vollständige Generalprobe entscheidet, wo ihr kürzen müsst.

Die [Präsentationsanleitung](PRAESENTATIONSANLEITUNG.md) enthält Vorbereitung, Rollen, konkrete Befehle und Ausweichmöglichkeiten.

## Lukas: Einstieg und Aufbau

### Folie 1 – DevSecOps-Pipeline

**Zeit: 0:00–0:20. Titelfolie zeigen.**

Wir stellen unsere DevSecOps-Pipeline vor. Wir haben drei kleine Python-Programme jeweils in einer verwundbaren und einer bereinigten Variante geprüft. Wir zeigen, wie die Sicherheitsprüfungen automatisch starten, welche Fehler sie erkennen und wie daraus eine nachvollziehbare Freigabe oder Ablehnung entsteht.

### Folie 2 – Aufgabe und geprüfter Umfang

**Zeit: 0:20–0:50. Auf die Zuordnung von Vorgabe und Umsetzung zeigen.**

Die Aufgabe verlangt mindestens vier Werkzeuge, einen automatischen Auslöser und drei lauffähige Programme. Wir verwenden eine Flask-API, eine Konfigurations-CLI und einen HTTP-Dateidienst. Durch die beiden Varianten entstehen sechs Testfälle. Insgesamt setzen wir acht Werkzeuge ein. Ihre Rohberichte und Gateentscheidungen haben wir archiviert und die Findings zusätzlich manuell bewertet.

### Folie 3 – Aufbau und Ablauf der Pipeline

**Zeit: 0:50–1:50. Das Diagramm in Pfeilrichtung erklären.**

Ein Push oder Pull Request startet zunächst die Tests unserer Pipeline-Logik. Danach untersuchen die Scanner den Quellcode, Secrets und Abhängigkeiten. Das erste Gate entscheidet, ob der Ablauf weitergehen darf.

Nach bestandenem Vorab-Gate baut die Pipeline das Web-Image und prüft dessen Komponenten und Konfiguration. Erst nach bestandenem Image-Gate startet der Webdienst in einem internen Testnetzwerk. Es folgen Healthcheck, konkrete API-Aufrufe und ein passiver ZAP-Scan.

Die CLI ist ein Sonderfall: Sie wird schon vor dem ersten Gate gebaut und gestartet, damit wir auch im Negativfall ihre Lauffähigkeit belegen. HTTP-Prüfungen entfallen bei ihr. Der gemeinsame Python-Orchestrator steuert lokal und in der CI denselben Ablauf. Er sichert die vorhandenen Ergebnisse auch nach einer Ablehnung.

### Folie 4 – Werkzeuge und Bezug zur Vorlesung

**Zeit: 1:50–2:35. SAST, SCA, Container und DAST nacheinander benennen.**

Die Werkzeugauswahl folgt den Prüfbereichen aus der Vorlesung. Auf Skriptfolie 46 nennt Herr Graupner unter anderem Bandit und Semgrep für SAST, ZAP für DAST sowie Trivy für Container Security. Diese vier verwenden wir tatsächlich.

Trivy prüft zusätzlich unsere Abhängigkeiten. hadolint untersucht das Dockerfile, Dockle das gebaute Image und Gitleaks sucht nach Secrets. Syft erzeugt eine SBOM, also ein Komponentenverzeichnis. Diese Inventarisierung bewertet selbst noch keine Schwachstellen. Die Werkzeuge ergänzen sich, weil sie unterschiedliche Eingaben und Fehlerarten betrachten.

**Übergabe:** Leo zeigt jetzt die drei Programme und die konkreten Korrekturen.

## Leo: Die drei Codebeispiele

### Folie 5 – Codebeispiel 1: Flask-API und SQL-Injection

**Zeit: 2:35–3:20. Zuerst auf die Stringverkettung, danach auf den Platzhalter zeigen.**

Bei der Flask-API stammt der Name aus einem HTTP-Request. Die verwundbare Variante setzt ihn direkt in den SQL-Text ein. Damit kann eine Eingabe die Bedeutung der Abfrage verändern. Unsere gezielte Akzeptanzprüfung hat diesen Fehler bestätigt.

Die bereinigte Variante verwendet einen Platzhalter und übergibt den Namen separat als Parameter. Der Datenbanktreiber behandelt ihn dadurch als Wert. Semgrep erkennt im verwundbaren Code den Datenfluss von der Request-Eingabe zum SQL-Aufruf. Das Beispiel enthält außerdem unmaskiertes HTML, einen Shell-Aufruf, MD5 und den Debug-Modus. Die Codeanalyse und die gezielten Funktionstests sind hier die Nachweise, kein aktiver ZAP-Angriffstest.

### Folie 6 – Codebeispiel 2: YAML-CLI und Abhängigkeiten

**Zeit: 3:20–4:00. Die drei unsicheren Aufrufe ihren Gegenmaßnahmen gegenüberstellen.**

Die CLI zeigt sowohl eigenen unsicheren Code als auch problematische Abhängigkeiten. Der Unsafe Loader kann Python-spezifische Objekte deserialisieren. `verify=False` deaktiviert die TLS-Zertifikatsprüfung. `mktemp` liefert nur einen Dateinamen, ohne die Datei atomar anzulegen.

Die bereinigte Variante verwendet einen Safe Loader, aktive Zertifikatsprüfung und `NamedTemporaryFile`. Zusätzlich aktualisieren wir die Paketversionen. SAST untersucht die Aufrufe, SCA die bekannten Lücken in den Paketen. Der eigentliche CLI-Start lädt nur die Konfiguration. Die gezeigten Abruf- und Cache-Funktionen werden dabei nicht ausgeführt, bleiben aber statisch prüfbare Codestellen.

### Folie 7 – Codebeispiel 3: Dateidienst und Secrets

**Zeit: 4:00–4:40. Den direkten Pfadzusammenbau und die nachfolgende Bereichsprüfung erklären.**

Beim Dateidienst hängt die verwundbare Variante den angefragten Namen direkt an das Datenverzeichnis an. Relative Pfadanteile könnten damit aus diesem Verzeichnis herausführen. Die bereinigte Variante löst den Pfad auf und prüft, ob das Ziel im erlaubten Verzeichnis liegt und eine Datei ist. Sie gibt nur noch Dateimetadaten zurück.

Außerdem enthält der Negativfall künstliche Secrets, die Gitleaks erkennen soll. Fixed liest den Token aus einer Umgebungsvariable. Die Pipeline injiziert dafür einen zufälligen Testwert. Das demonstriert externe Konfiguration. Eine Prüfung dieses Tokens bei HTTP-Requests und damit eine vollständige Authentifizierung sind noch nicht implementiert.

**Übergabe:** Maxim erklärt jetzt die automatische Ausführung, die Ergebnisse und die Probleme, die wir korrigiert haben.

## Maxim: Automatisierung, Ergebnisse und Korrekturen

### Folie 8 – Automatisierung mit GitHub Actions

**Zeit: 4:40–5:15. YAML-Auszug zeigen; noch nicht in den Browser wechseln.**

GitHub erkennt unseren Workflow im vorgesehenen Verzeichnis am Git-Stamm. Push und Pull Request starten ihn automatisch. Nach den Unit-Tests folgen drei Programme mal zwei Varianten, also sechs Matrixfälle. Alle rufen dieselben Python-Skripte auf. Die CI enthält keine abweichende Gate-Implementierung.

Die vollständige Git-Historie steht für den Secret-Scan bereit, und die Ergebnisdateien werden als Artefakte hochgeladen. Der dokumentierte erste Push-Lauf war erfolgreich und dauerte drei Minuten und zwei Sekunden. Diese Zeit beschreibt diesen Lauf und ist keine Garantie für die nächste Demo.

### Folie 9 – Gate-Policy und Fehlerbehandlung

**Zeit: 5:15–6:00. Die drei Exit-Codes deutlich voneinander trennen.**

Die Policy legt je Prüfklasse fest, welche Schweregrade blockieren. Secrets blockieren immer, SAST und Images ab HIGH und SCA ab CRITICAL. Die passiven DAST-Findings warnen nach unserer gewählten Lehrprojekt-Policy und müssen weiterhin bewertet werden.

Davon getrennt behandeln wir technische Fehler. Exit-Code null bedeutet: Policy bestanden. Eins bedeutet: Ein erfolgreich ausgeführter Scan hat einen blockierenden Befund geliefert. Zwei bedeutet: Der Ablauf konnte technisch nicht verlässlich prüfen.

Ein fehlender oder beschädigter Pflichtreport darf deshalb niemals als sauberer Scan gelten. Genau diese Trennung nennen wir hier fail closed. Auch ein technisch fehlgeschlagener DAST-Scan führt zu ERROR.

### Folie 10 – Ergebnisse der drei Programme

**Zeit: 6:00–6:45. Die Zahlen ausdrücklich den archivierten Läufen zuordnen.**

Die Tabelle zeigt die archivierten Offline-Ergebnisse vom 21. Oktober 2026. Bei der Flask-API hatten wir acht aktive blockierende Findings, bei der CLI vier und beim Dateidienst zehn. Alle drei Fixed-Varianten bestanden die Policy mit null aktiven Blockern und jeweils einer geprüften Ausnahme.

Insgesamt haben wir sechs Online- und sechs Offline-Läufe dokumentiert. Sechs separate Smoke-Tests belegen die Lauffähigkeit aller Varianten. Außerdem bestanden die 41 aktuellen Tests der Pipeline-Logik. Ein PASS bedeutet trotzdem nicht null Findings oder vollständige Sicherheit. Warnungen bleiben sichtbar, und mehrere Meldungen können dieselbe Ursache betreffen.

### Folie 11 – Probleme während der Implementierung

**Zeit: 6:45–7:35. Pro Tabellenzeile Problem und Korrektur kurz verbinden.**

Die Validierung hat mehrere konkrete Probleme aufgedeckt. Zunächst lagen CI-Konfigurationen beziehungsweise Arbeitsverzeichnisse falsch. Wir haben die Einstiege am Git-Stamm und die Pfade korrigiert.

Kritischer war, dass ein ausgefallener Scanner ursprünglich zu einer grünen Entscheidung führen konnte. Heute verlangen wir erfolgreiche Checkzustände und gültige Pflichtberichte. Ein Runtime-Ausfall endet mit ERROR.

Die alte CLI war außerdem zunächst nicht zuverlässig installierbar. Wir haben kompatible Versionen festgelegt und beide Varianten tatsächlich gestartet. Schließlich konnte die Deduplizierung den Image-Kontext verlieren. Mit Finding-ID und Testklasse als Schlüssel bleibt die strengere Image-Policy erhalten. Regressionstests sichern diese Korrekturen ab.

### Folie 12 – Findings bewerten und Ausnahmen begrenzen

**Zeit: 7:35–8:15. Owner und Ablaufdatum hervorheben.**

Eine Scanner-Meldung braucht manchmal eine Kontextprüfung. Dockle beanstandet hier einen geerbten Paketmanager-Aufruf des offiziellen Python-Alpine-Images. Wir haben die Buildzeile geprüft und kontrollieren zusätzlich, dass keine Paketcache-Dateien vorhanden sind.

Die Ausnahme gilt nur für die benannten Fixed-Workloads, den exakten Basis-Digest und den passenden Befund. Sie benötigt einen erfolgreichen Zusatzcheck, einen Owner und eine Begründung. Ihr Ablaufdatum ist der 20. November 2026. Danach ist eine erneute Bewertung nötig. Der Rohbefund bleibt sichtbar. Damit haben wir eine konkrete Ausnahme dokumentiert, ohne die Regel allgemein abzuschalten.

**Übergabe:** Valentin zeigt jetzt die Verbindung zwischen Code, Scannerbefund und Gateentscheidung in der Demo.

## Valentin: Demo, Erkenntnisse und Bewertung

### Folie 13 – Demo: Code, Finding und Gateentscheidung

**Zeit: 8:15–11:15. Die Bedienfolge steht ausführlich in der [Anleitung](PRAESENTATIONSANLEITUNG.md#5-demo-auf-folie-13-genau-drei-minuten).**

**Browser: Den tatsächlich vorhandenen GitHub-Actions-Lauf öffnen. Auf Event, Branch und Matrixfälle zeigen.**

Hier sehen wir den automatischen Start durch einen Push. Die sechs Fälle prüfen drei unterschiedliche Programme jeweils verwundbar und bereinigt. Ein grüner Demo-Job bedeutet, dass die erwarteten Ergebnisse eingetreten sind. Die Security-Gates der verwundbaren Beispiele bleiben dabei FAIL.

**Editor: Im Dateidienst auf das künstliche Secret und den ungeprüften Dateipfad zeigen. Terminal: Einen vorbereiteten Negativfall starten. Während der Scanner arbeitet, den gespeicherten Bericht öffnen.**

Wir starten jetzt den Dateidienst als Negativbeispiel. Die Pipeline soll seine problematischen Stellen erkennen und den Ablauf ablehnen. Im gespeicherten Nachweis sehen wir den ursprünglichen Toolbefund und anschließend die Gateentscheidung. Das ist der Unterschied zwischen einer Meldung und ihrer Bewertung durch unsere Policy.

**Archiv oder rechtzeitig abgeschlossener neuer Lauf: Zugehöriges `gate.json` für vulnerable und fixed vergleichen. Quelle des Nachweises benennen.**

Beim verwundbaren Beispiel sehen wir FAIL mit aktiven Blockern. Die bereinigte Variante besteht die Policy und führt ihre Warnungen und die geprüfte Ausnahme weiterhin auf. Die vollständigen Nachweise für die Flask-API und die CLI liegen ebenfalls im Archiv.

**Falls der aktuelle Lauf noch arbeitet, stattdessen ausdrücklich sagen:**

Der Live-Lauf ist noch nicht abgeschlossen. Für den Vergleich verwenden wir deshalb die gespeicherten Ergebnisse vom 21. Oktober. Wir behaupten damit keinen bereits abgeschlossenen neuen Lauf.

**Spätestens bei 11:15 zurück zur Präsentation wechseln. Den Scanner bei Bedarf weiterlaufen lassen.**

### Folie 14 – Lessons Learned

**Zeit: 11:15–11:55. Vier Erkenntnisse erläutern, keine Werkzeugliste wiederholen.**

Unsere wichtigste Erkenntnis ist, dass wir auch den Prüfablauf selbst testen müssen. Ein gestarteter Scanner und null Findings reichen nicht aus. Prozessstatus und Report müssen zusammenpassen.

Zweitens sind Lauffähigkeit und Sicherheitsfreigabe getrennte Nachweise. Ein Negativbeispiel muss funktionieren und trotzdem am Gate scheitern können. Drittens braucht die Bewertung den Anwendungskontext. Eine bekannte Paketlücke ist noch kein Nachweis ihrer Ausnutzbarkeit im konkreten Programm. Viertens brauchen wiederholbare Ergebnisse auch dokumentierte Regeln, Quellen, Images und Datenbankstände. Neue CVEs können einen unveränderten Build später berechtigt stoppen.

### Folie 15 – Bewertung für den produktiven Einsatz

**Zeit: 11:55–12:55. Urteil voranstellen, anschließend die wichtigsten Voraussetzungen nennen.**

Als Grundlage für reale CI-Prüfungen ist der Ansatz brauchbar. Den aktuellen Stand würden wir aber nicht unverändert für Produktionsfreigaben verwenden.

Wir haben automatische Gates, isolierte Testläufe und nachvollziehbare Reports. Vor einem produktiven Einsatz bräuchten wir verbindliche Reviews und geschützte Branches. Actions sollten an vollständige Commit-SHAs gebunden sein. Regeln und Schwellenwerte müssten zum Risiko der tatsächlichen Anwendung passen.

Unsere Semgrep-Regeln sind bewusst begrenzte Lehrregeln, und ZAP arbeitet nur passiv. Die Demonstrationsprogramme benötigen außerdem ein vollständiges Authentifizierungs- und Betriebskonzept. Für den laufenden Betrieb fehlen nachgewiesene Prozesse für Secrets, Monitoring, Patchfristen und Rollback.

Unsere Bewertung lautet deshalb: Der geprüfte Scan-Pfad bietet eine technische Grundlage. Eine Produktionsfreigabe braucht zusätzliche Schutzmaßnahmen und klare Zuständigkeiten.

### Folie 16 – Ergebnis und nächste Schritte

**Zeit: 12:55–13:15. Danach auf dieser Folie bleiben und Fragen zulassen.**

Wir haben drei lauffähige Programme, sechs Varianten und einen nachgewiesenen automatischen Push-Trigger. Die vorgesehenen Negativfälle werden erkannt und ihre Entscheidungen bleiben überprüfbar. Als Nächstes würden wir die Testabdeckung und den verbindlichen Betriebsprozess ausbauen. Damit sind wir am Ende und beantworten gern eure Fragen.

## Reservefolien: nur bei passenden Rückfragen

### Folie 17 – Vollständige Gate-Matrix

**Anlass:** Jemand fragt nach einem bestimmten Schweregrad oder nach unterschiedlichen Regeln für SCA und Images.

Hier ist die vollständige Zuordnung von Testklasse und Severity zu `block`, `warn` oder `info`. Dieselbe HIGH-CVE kann im SCA-Kontext warnen und im Image-Kontext blockieren. Deshalb bleibt die Testklasse Bestandteil des Deduplizierungsschlüssels. Technische Fehler führen unabhängig davon zu ERROR.

### Folie 18 – Code und Ergebnisdateien

**Anlass:** Jemand fragt, welche Datei eine Entscheidung trifft oder wie ein Scannerfehler erkannt wird.

`pipeline.py` steuert den Ablauf. `collect.py` sammelt Reports und `normalize.py` vereinheitlicht ihre Findings. `gate.py` wertet die Policy aus und schreibt `gate.json`. `report.py` erstellt den Gesamtbericht. `demo.py` prüft zusätzlich, ob die erwarteten positiven und negativen Fälle eintreten. Dafür reicht ein Prozess-Exit-Code allein nicht aus: Es muss eine passende neue Gateentscheidung vorliegen.

### Folie 19 – Demo-Vorbereitung und Grenzen

**Anlass:** Jemand fragt nach Offline-Betrieb, Laufzeiten oder fehlenden Live-Nachweisen.

Offline benötigen wir bereits vorhandene Scanner-Images, Datenbanken und exakt zum Workload passende Anwendungsimages. `prepare.py` allein baut noch nicht alle Anwendungen. Die lokale Online-Suite dauerte ungefähr zehn Minuten. Bei einem Offline-History-Scan gab es eine ungewöhnlich lange, nicht abschließend erklärte Pause. Deshalb behandeln wir diese Zeiten nicht als Benchmark und haben archivierte Nachweise als Reserve.

### Folie 20 – Quellen und weiterführende Nachweise

**Anlass:** Jemand fragt nach dem Vorlesungsbezug oder der Grundlage der Aussagen.

Unsere Toolzuordnung bezieht sich auf die aufgedruckten Foliennummern des Skripts von Herrn Graupner. Die Open-Source-Werkzeuge stehen auf Folie 46, das ist PDF-Seite 47. Implementierung, Korrekturen und Messwerte sind im Repository dokumentiert. Die Detailquellen stehen zusätzlich in den Sprechernotizen. Die Produktionsbewertung berücksichtigt außerdem die verlinkten Hinweise von GitHub und OWASP.

## Grundlagen dieses Sprechtexts

- [PowerPoint](DevSecOps_Pipeline_DHBW.pptx) und die darin enthaltenen Sprechernotizen.
- [Pipeline und Code erklärt](../README_PIPELINE_ERKLAERT.md).
- [Nachprüfung](../NACHPRUEFUNG.md) und [archivierte Messwerte](../../devsecops-pipeline/docs/validation/2026-10-21-fixed/results.json).
- [Manuelle Findingsbewertung](../FINDINGS_BEWERTUNG.md).
- Bereitgestelltes Vorlesungsskript `06_SecureDevelopment.pdf`, Georg Graupner, Wintersemester 2024.

Bei Änderungen an Folien oder Pipeline den Sprechtext entsprechend aktualisieren. Die Zahlen beschreiben die archivierte Prüfung vom 21.10.2026 und werden nicht automatisch durch neue Scannerläufe ersetzt.
