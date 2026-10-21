# Manuelle Bewertung und Erkenntnisse

Diese Einordnung bezieht sich auf konkrete Muster und geprüfte Codestellen.
Sie ersetzt keine pauschale False-Positive-Quote für alle Scanner-Meldungen.
Die Rohdaten der Vorher- und Nachher-Prüfung bleiben separat erhalten.

| Befund | Bewertung | Nachweis / Behandlung |
|---|---|---|
| Zusammengesetzte SQL-Abfrage in Flask vulnerable | Bestätigter Codefehler | Funktionstest lieferte bei `' OR 1=1 --` Datensätze; parametrisierte Fixed-Abfrage nicht |
| Unescaped `/greet` | Bestätigter Codefehler | Vulnerable liefert Script-Markup unverändert, Fixed escaped es; kein behaupteter ZAP-Aktivnachweis |
| `os.system` mit Request-Eingabe | Bestätigter gefährlicher Datenfluss | Codestelle in `/ping`; Fixed validiert IP und ruft ohne Shell auf |
| `yaml.unsafe_load`, `verify=False`, `tempfile.mktemp` in CLI | Bestätigte unsichere Muster | Safe Loader, Zertifikatsprüfung und atomare Tempdatei beheben die Muster; `fetch` wird nicht vom simplen CLI-Hauptpfad ausgeführt |
| Festgeschriebene Test-Secrets | Beabsichtigte echte Erkennung künstlicher Werte | Gitleaks meldet die Code-/ENV-Werte; keine kompromittierten realen Credentials |
| Alte Requests-/urllib3-/PyYAML-Pakete | Reale veraltete Komponenten | SCA-Advisories dokumentieren, deren Erreichbarkeit getrennt bewerten; Fixed verwendet aktuelle kompatible Pins |
| `certifi==2024.8.30` in früherer Fixed-CLI | Berechtigter Aktualisierungsbedarf | Kritisches Advisory der Erstprüfung; auf 2026.10.19 aktualisiert |
| Dockle DKL-DI-0005 gegen das frühere Python-Slim-Basisimage | Begründeter Fehlalarmkandidat | Regel verlangt alten rm-Aufruf, Basis verwendet `apt-get dist-clean`; keine apt-Listen vorhanden. Neues Fixed-Image verwendet Alpine ohne apt |
| Bandit B104 bei Webdiensten | Kontextabhängige Warnung | Bindung an Containerinterfaces wird für die interne Testkommunikation gebraucht; keine veröffentlichten Host-Ports |
| hadolint: ungepinnte Paketinstallation | Kontext bewerten | Python-Pakete sind über Requirements gepinnt; Basisimage per Digest. Keine pauschale Unterdrückung |
| Fehlende Header / Serverinformationen | Passive DAST-Beobachtung | Header des Fixed-Statusdienstes ergänzt, Python-Versionsbanner entfernt; aktuelle ZAP-Rohdaten maßgeblich |

Eine eng begrenzte Ausnahme behandelt Dockle DKL-DI-0004 in der geerbten offiziellen
Python-Alpine-Buildzeile: Der erste apk-Aufruf verwendet `--no-cache`, der spätere
Aufruf `--no-network` verwendet lokal vorhandene Bibliotheken. Die Ausnahme ist
auf den exakten Basis-Digest, drei Fixed-Workloads, den konkreten Meldungstext und
eine erfolgreiche zusätzliche Prüfung auf leere Paket-Caches begrenzt. Sie läuft
am 20.11.2026 ab. Echte Findings derselben Regel in anderen Images bleiben wirksam.
Jede weitere Ausnahme braucht ebenfalls fachliche Begründung, Owner und Ablaufdatum.
Ein als HIGH oder CRITICAL gemeldetes Paketproblem ist erst nach Triage ein
bestätigt ausnutzbarer Anwendungsfehler. Das Gate setzt bewusst eine strengere
automatisierte Grenze als diese manuelle Exploitability-Aussage.

Erkenntnisse: Ausführungsfehler und Security-Ablehnung müssen getrennt sein.
Lauffähiger Code kann berechtigt am Security-Gate scheitern. Aktuelle CVE-Daten
können einen gestern grünen unveränderten Build stoppen. Scanner ergänzen sich;
statische Analyse findet andere Muster als Inventarisierung und passiver DAST.
Ein erfolgreicher passiver Scan beweist weder Authentifizierung noch komplette
Angriffsresistenz. Ein geprüfter Offline-Cache ist Teil der Demo-Vorbereitung.
