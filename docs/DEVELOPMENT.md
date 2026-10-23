# Implementierung

Die aktuelle Implementierung hat einen gemeinsamen Orchestrator
`scripts/pipeline.py` für Windows, Linux und beide CI-Dienste. `run-pipeline.sh`
ist nur ein mit `bash` aufzurufender Kompatibilitätseinstieg. Die alten Stage-Skripte
wurden entfernt, damit deren frühere Fehlerpfade nicht weiter genutzt werden.
Die Architekturpläne beschreiben den Entwurf; die README dokumentiert den Iststand.

`prepare.py` trennt Toolinstallation und Datenbankvorbereitung von den Scans.
`policy/images.lock.json` hält unveränderliche Image-Digests fest. Das selbst
gebaute Bandit-Image wird lokal vorbereitet. Semgrep verwendet ausschließlich
die neun im Repository reviewbaren Regeln; die Abdeckung ist bewusst kleiner
als die vorher dynamisch geladenen OWASP-Pakete. Bandit ergänzt Python-Regeln.
Eine vollständige OWASP-Abdeckung wird damit nicht behauptet.

Jeder externe Prozess bekommt einen Checkstatus. Zulässige Tool-Exit-Codes für
Findings (hadolint 1, ZAP 1/2) werden von technischen Fehlern getrennt. Zusätzlich
werden Rohreports validiert. `collect.py` verlangt die grundlegenden Scans und
ein Ausführungsmanifest; `gate.py` lehnt fehlende/fehlerhafte Evidenz ab. So kann
weder ein Build-, Healthcheck- noch ein Publish-Fehler von einem leeren Finding-
Array verdeckt werden. Der Bericht wird erst nach der Gateentscheidung erzeugt.

Trivy und Dockle prüfen exportierte Image-Tars. Dadurch benötigen Scanner keinen
Docker-Socket und funktionieren auch bei einem separaten Docker-in-Docker-Daemon.
Docker-DinD teilt keine lokalen Images zwischen Jobs; deshalb läuft eine Variante
vollständig im selben Job. Vor Deployment wird das Image-Gate synchron ausgewertet.

Die CLI wird tatsächlich in ihrer deklarierten Umgebung installiert und ausgeführt.
Die bereinigte Variante nutzt eine unterstützte Python-Laufzeit. Ein separater
Smoke-Test belegt auch die Lauffähigkeit der früh gestoppten Web-Negativbeispiele.
Er stellt ausdrücklich keine bestandene Security-Pipeline dar.

ZAP erhält eine versionierte OpenAPI-Beschreibung und läuft passiv mit `-S`.
Funktionale Smoke-Aufrufe prüfen die vorgesehenen Endpunkte vor dem Scan.
Aktive Angriffe, Authentifizierungstests, IAST und Runtime-Schutz bleiben außerhalb
des Umfangs. Der Statusserver liest einen Start-Token; er implementiert damit
noch keine vollständige API-Authentifizierung.

Die historische Validierung und ihre Rohdaten werden nicht überschrieben.
`docs/NACHPRUEFUNG.md` dokumentiert die Prüfung nach den Korrekturen.
