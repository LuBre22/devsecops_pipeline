# Nachweise der Validierung vom 21.10.2026

Die Pipeline wurde nicht verändert. Die Ergebnisse gehören zum im übergeordneten
Validierungsbericht genannten Arbeitsstand.

- `results.json`: kompakte Ergebnisse der sechs echten Pipeline-Läufe.
- `FINDINGS_REPORT.md` und `metrics.csv`: unveränderte Ausgaben des Reportgenerators.
- `evidence.zip`: vollständige Rohreports, normalisierte Findings, Gateentscheidungen,
  Zeitdaten, Testergebnisse, Fehlerreproduktionen und Build-/Scan-Logs.
- `test_validation.py`: zusätzliche Akzeptanztests. Aus dem Pipeline-Verzeichnis
  mit `python -m pytest docs/validation/2026-10-21/test_validation.py -vv`
  ausführen. Benötigt pytest, Flask 3.0.3, Werkzeug 3.0.4, Jinja2 3.1.4,
  MarkupSafe 2.1.5, PyYAML 6.0.2, requests 2.32.3 und bandit[sarif] 1.7.9.
  Die vier fehlgeschlagenen Tests beschreiben bestätigte Fehler der Pipeline.
- `run_containers.py`, `diagnostics.py` und `Dockerfile`: Aufzeichnung des verwendeten
  Testaufbaus. Diese Hilfsskripte wurden ursprünglich unter `.validation/` neben
  `Entwurf_Pipeline/` ausgeführt und setzen diese relative Verzeichnisstruktur
  voraus. Sie führen Scanner bzw. Smoke-Tests aus und laden Container-Images.
  Sie sind keine neue CI-Konfiguration.

Die Container-Run-IDs verwenden UTC. Der letzte vollständige Lauf dauerte wegen
des ersten ZAP-Downloads etwa neun Minuten. Das ist keine gemessene Laufzeit
einer bereits vorbereiteten Live-Demo.
