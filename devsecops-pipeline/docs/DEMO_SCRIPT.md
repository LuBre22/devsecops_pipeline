# Demo – ungefähr 15 Minuten

Vorbereitung: Docker starten, `python scripts/prepare.py` und einen vollständigen
`python scripts/demo.py` durchführen. Ergebnisse sichern und ein kurzes Video
aufnehmen. Offline nur mit zuvor bestätigtem vollständigem Cache demonstrieren.
Keine Paketinstallationen oder große Image-Downloads in die Livezeit einplanen.

| Zeit | Inhalt |
|---|---|
| 0–2 Min. | Aufgabe, drei Programme und Security-Klassen vorstellen |
| 2–4 Min. | Den automatischen Push-Trigger am Git-Stamm und sechs CI-Fälle zeigen |
| 4–8 Min. | Einen verwundbaren Workload mit Exit 1 und denselben bereinigt mit Exit 0 zeigen |
| 8–11 Min. | Echte Berichte aller drei Programme; SQLi, Secrets und Dependencies erläutern |
| 11–13 Min. | Scanner-Ausfall als ERROR; manuelle Findingsbewertung und DAST-Grenzen |
| 13–15 Min. | Erkenntnisse und Fragen |

```bash
python scripts/pipeline.py workloads/03-container-service/vulnerable
python scripts/pipeline.py workloads/03-container-service/fixed
python scripts/demo.py
```

Nicht alle sechs Scanner-Läufe live abwarten. Vollständige gespeicherte Nachweise
zeigen und ein bis zwei bereits vorbereitete Läufe demonstrieren. Erwartete
Ablehnung eines Negativbeispiels ist kein technischer Fehler. Eine fehlgeschlagene
Runtime dagegen muss mit 2 enden; null Findings sind dann kein Erfolg.

Die drei Beispiele decken unterschiedliche Ursachen ab: eigener Code, fremde
Abhängigkeiten und Secrets/Container. Der CLI-Negativfall enthält zusätzlich
unsicheren Code – er ist kein reines SCA-Beispiel. ZAP führt einen passiven
OpenAPI-Scan durch; keinen aktiven Nachweis von SQLi oder Reflected XSS behaupten.
Ohne REGISTRY-Konfiguration findet kein Image-Push statt. Optionale Dienste nur
als tatsächlich demonstriert bezeichnen, wenn sie separat eingerichtet wurden.

Für Rückfragen die echten Unterschiede im Code und
`docs/FINDINGS_BEWERTUNG.md` verwenden. Bei neuen CVEs einen roten Fixed-Lauf
offen erklären und vorab beheben, statt den Schwellwert für die Demo abzusenken.
