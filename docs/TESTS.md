# Tests

```bash
python -m pytest tests -q
```

Die Tests prüfen Policy-Entscheidungen, Severity-Mapping, unterschiedliche
Scan-Kontexte, fehlende/kaputte Reports, fehlende Ausführungsevidenz, technische
Fehler, Suppression-Ablaufdaten, ZAP-URLs, YAML-Fallback und Berichtsstatus.
Ein leeres Finding-Array besteht nur zusammen mit erfolgreicher Ausführungsevidenz.
Ein kaputter Report wird jetzt ausdrücklich abgelehnt; der frühere Test, der ihn
als leer tolerierte, wurde entsprechend ersetzt.

Die zusätzlichen Tests der ursprünglichen Prüfung bleiben als historische
Momentaufnahme unter `docs/validation/2026-10-21/` erhalten. Die laufende Testsuite
ist ausschließlich `tests/` und enthält die entsprechenden Regressionstests.

Container und Scanner werden separat mit echten Läufen geprüft:

```bash
python scripts/prepare.py
python scripts/demo.py
python scripts/smoke.py workloads/01-flask-api/vulnerable
```

Die Demo erwartet dreimal Security-Ablehnung (1) und dreimal PASS (0). Technische
Fehler (2) sind für keine Variante akzeptabel. Ein grüner Demo-Job bedeutet,
dass alle Erwartungen zutreffen; er erklärt verwundbaren Code nicht für sicher.
Scanner-Reports, manifeste Checkzustände, konkrete Findings und verbleibende
Grenzen gehören zu den Nachweisen. Ein echter Remote-CI-Trigger muss zusätzlich
nach einem Push am jeweiligen CI-Dienst geprüft werden.
