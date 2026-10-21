# DevSecOps-Pipeline – Lehrprojekt

- [Pipeline und Schnellstart](devsecops-pipeline/README.md)
- [Aktuelle Implementierung](devsecops-pipeline/docs/DEVELOPMENT.md)
- [Historische Erstvalidierung](devsecops-pipeline/docs/VALIDIERUNG.md)
- [Nachprüfung der Korrekturen](devsecops-pipeline/docs/NACHPRUEFUNG.md)
- [Manuelle Findingsbewertung](devsecops-pipeline/docs/FINDINGS_BEWERTUNG.md)
- [Anforderungsentwurf](Anforderungsanalyse_DevSecOps_Pipeline.md)
- [Architekturentwurf](Architekturplan_DevSecOps_Pipeline.md)

Die automatische Ausführung über GitHub Actions ist bestätigt: Der Workflow
**DevSecOps demo verification #1** wurde durch den Push von Commit `234b46a`
auf `validation/pipeline-pruefung` ausgelöst und erfolgreich abgeschlossen.
Der bereitgestellte GitHub-Actions-Screenshot dokumentiert eine Laufzeit von
**3 Minuten und 2 Sekunden**.

Die ausführbaren CI-Konfigurationen und Pre-commit-Konfiguration liegen direkt
in diesem Git-Stamm. Die Pipeline-Implementierung liegt in `devsecops-pipeline/`.
Die verwundbaren Varianten enthalten absichtliche Schwachstellen und ausschließlich
künstliche Demo-Secrets. Niemals echte Zugangsdaten dort eintragen.
