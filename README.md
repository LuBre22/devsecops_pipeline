# DevSecOps Pipeline Lehrprojekt

Dieses Repository enthaelt die Entwurfs- und Entwicklungsdokumentation sowie
die vollstaendige Pipeline-Implementierung fuer das IT-Sicherheitsprojekt.

- [Anforderungsanalyse](./Anforderungsanalyse_DevSecOps_Pipeline.md)
- [Architekturplan](./Architekturplan_DevSecOps_Pipeline.md)
- [Entwicklungsdokumentation](./Entwicklungsdokumentation_DevSecOps.md)
- [Pipeline-Projekt](./devsecops-pipeline/)
- [Pipeline-README](./devsecops-pipeline/README.md)

## Sicherheitshinweis

Die Pipeline enthaelt absichtlich verwundbare Demo-Artefakte. Die Datei
[`devsecops-pipeline/workloads/03-container-service/vulnerable/.env`](./devsecops-pipeline/workloads/03-container-service/vulnerable/.env)
ist ein Gitleaks-Testfixture und enthaelt nur kuenstliche Werte. Sie darf
niemals mit echten Zugangsdaten oder Produktions-URLs befuellt werden.
