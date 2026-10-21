> Historischer Entwurf. Die aktuelle Implementierung und die unterstützten Einstiege sind in der [Pipeline-README](../../README.md) dokumentiert.

# Anforderungsanalyse — Gruppenaufgabe "DevSecOps Pipeline"

**Modul:** IT-Sicherheit, Modul 6 — Sichere Anwendungsentwicklung (DHBW Mosbach, Georg Graupner, WiSe 2024)
**Grundlage:** Aufgabenstellung Folie 47 (Seite 48 der PDF)
**Dokumentstatus:** Entwurf v1.0 — Basis für die Architekturplanung

---

## 1. Ausgangslage und Ziel

Die Vorlesung behandelt den Secure Development Lifecycle (SDL) mit den Grundsätzen SD3+C, Bedrohungsmodellierung (STRIDE/DREAD) und der Integration von Sicherheit über den gesamten Lifecycle (DevSecOps). Die Aufgabe überträgt diese Theorie in eine lauffähige, automatisierte Pipeline.

**Projektziel:** Aufbau einer kleinen, aber vollständig automatisierten DevSecOps-Pipeline, die Sicherheitsprüfungen ohne manuelles Eingreifen auslöst, auf mindestens drei Code-Beispielen nachweisbar Findings produziert, dokumentiert ist und in 15 Minuten inkl. Demo präsentiert werden kann.

**Nicht-Ziel:** Produktionsreife Enterprise-Pipeline, kommerzielle Tool-Lizenzen, Betrieb über den Vorlesungszeitraum hinaus.

---

## 2. Stakeholder und Rollen

| Stakeholder | Interesse / Erwartung |
|---|---|
| Dozent (Abnehmer) | Erfüllung der Aufgabenkriterien, nachvollziehbare Erkenntnisse, funktionierende Live-Demo |
| Gruppenmitglieder | Lerneffekt, gleichmäßige Arbeitsteilung, beherrschbarer Aufwand |
| Kommilitonen (Publikum) | Verständliche Darstellung in 15 Minuten |

**Empfohlene Rollenverteilung in der Gruppe** (angelehnt an das interdisziplinäre Team-Prinzip, Folie 34):
- *Platform/Ops*: CI-Runner, Container-Umgebung, Registry
- *Security Champion*: Tool-Auswahl, Schwellwerte (Quality/Security Gates), Bewertung der Findings
- *Developer*: Demo-Applikationen und Code-Snippets, Fix-Nachweis
- *Dokumentation/Präsentation*: Findings-Report, Folien, Demo-Drehbuch

---

## 3. Explizite Anforderungen (direkt aus der Aufgabenstellung)

| ID | Anforderung | Typ | Priorität | Abnahmekriterium |
|---|---|---|---|---|
| A-01 | Aufbau einer kleinen DevSecOps-Pipeline | funktional | Muss | Pipeline läuft reproduzierbar durch |
| A-02 | Mindestens **4 Tools** werden eingesetzt | funktional | Muss | ≥ 4 Tools namentlich in der Pipeline-Definition nachweisbar |
| A-03 | Tools dürfen aus der Vorlesung oder darüber hinaus gewählt werden | Randbedingung | Kann | Begründung der Tool-Wahl im Report |
| A-04 | **Automatisierungsmechanismus** für Security-Tools (z. B. SAST bei Code-Check-in) | funktional | Muss | Commit/Push löst Scan ohne manuelle Aktion aus |
| A-05 | Mindestens **3 verschiedene** Code-Snippets/Programme durchlaufen die Pipeline | funktional | Muss | 3 Pipeline-Runs mit unterschiedlichem Input dokumentiert |
| A-06 | Code darf aus bisherigen Vorlesungen stammen | Randbedingung | Kann | Herkunft im Report benannt |
| A-07 | **Dokumentation** der Ergebnisse und Findings | Doku | Muss | Findings-Report mit Severity, Ursache, Bewertung |
| A-08 | Präsentation ca. **15 Min. pro Gruppe** inkl. **Demo** | Doku/Prozess | Muss | Foliensatz + geprobte Live-Demo ≤ 15 Min. |
| A-09 | Erarbeitung im **Selbststudium**, Vorstellung im **kommenden Termin** | Rahmen | Muss | Termin eingehalten |

---

## 4. Abgeleitete funktionale Anforderungen

Diese Anforderungen sind in der Aufgabe nicht wörtlich genannt, folgen aber aus dem Vorlesungsstoff (Folien 36–44) und sind für eine fachlich saubere Lösung notwendig.

| ID | Anforderung | Begründung (Vorlesungsbezug) |
|---|---|---|
| F-01 | Versionskontrolle als Single Source of Truth, Pipeline-Definition als Code im Repo | CI/CD, Reproduzierbarkeit |
| F-02 | Abdeckung mehrerer Testklassen statt vier gleichartiger Tools: **SAST**, **SCA/FOSS-Scan**, **Secret Scanning**, **Container-Image-Scan**, optional **DAST** | Folie 36: Security über den gesamten Lifecycle |
| F-03 | **Security Gate** mit definiertem Schwellwert (z. B. "keine kritischen/hohen CVEs", "keine CVEs mit verfügbarem Fix") — Build bricht bei Überschreitung ab | Folie 32: Threshold-Prüfung nach Image-Scan |
| F-04 | Zentrale Aggregation und Nachverfolgung der Findings (Defect Management) | Folie 36: Defect Management |
| F-05 | Secrets werden nicht im Repo gehalten, sondern über CI-Variablen/Vault bereitgestellt | Folie 42: Secret Management |
| F-06 | Container-Build in der Pipeline, Push in eine Registry nur bei bestandenem Gate | Folie 32: Secure Build / Container Security |
| F-07 | Maschinenlesbare Reports (SARIF/JSON) als Build-Artefakte, versioniert je Run | Nachweisbarkeit, Metriken |
| F-08 | Mindestens ein **Positiv-** und ein **Negativ-Testfall** pro Tool (bewusst unsicherer Code vs. gefixter Code) | Wirksamkeitsnachweis, Vermeidung "grüner Pipeline ohne Aussage" |
| F-09 | Metriken erheben: Anzahl Findings je Severity, Laufzeit je Stage, False-Positive-Quote | Folie 10: "Wie messen wir Sicherheit?" |
| F-10 | DAST nur gegen eine ephemere, isolierte Testinstanz der eigenen Anwendung | Rechtliche/ethische Grenzen, Zonenkonzept Folie 13 |

---

## 5. Nicht-funktionale Anforderungen

| ID | Kategorie | Anforderung | Messgröße |
|---|---|---|---|
| NF-01 | Reproduzierbarkeit | Pipeline läuft auf jedem Gruppenrechner identisch (containerisiert, IaC/Compose) | Setup aus leerem Zustand < 30 Min. |
| NF-02 | Laufzeit | Vollständiger Pipeline-Run demotauglich | ≤ 10 Min., Demo-Teil ≤ 5 Min. |
| NF-03 | Kosten | Ausschließlich Open Source / kostenlose Tiers | 0 € |
| NF-04 | Betrieb | Lokal lauffähig, keine Abhängigkeit von Hochschul- oder Cloud-Infrastruktur | Offline-Demo möglich (Fallback: Screencast) |
| NF-05 | Wartbarkeit | Tools austauschbar, da pro Stage über standardisierte Reports gekoppelt | Tool-Tausch ohne Pipeline-Umbau |
| NF-06 | Nachvollziehbarkeit | Jeder Run ist einem Commit zuordenbar, Artefakte archiviert | Run-ID ↔ Commit-Hash |
| NF-07 | Sicherheit der Pipeline selbst | Least Privilege für Runner-Tokens, keine Secrets in Logs | Review der Berechtigungen |
| NF-08 | Datenschutz | Keine echten Personen-/Unternehmensdaten in Testdaten | Review der Testdaten |

---

## 6. Randbedingungen und Annahmen

**Randbedingungen**
- Zeitbudget: Selbststudium bis zum Folgetermin; Präsentation strikt 15 Min.
- Teamgröße: Projektgruppe (Annahme 3–5 Personen)
- Keine Lizenzbudgets, keine Produktionsdaten, kein Angriff auf Dritt-Systeme

**Annahmen**
- Docker (oder Podman) und Git sind auf den Entwicklerrechnern verfügbar
- Mindestens eine Programmiersprache ist im Team gemeinsam beherrscht (Annahme: Python und/oder Java)
- Ein Git-Hosting mit CI (selbst gehostet oder kostenlose Tier) kann genutzt werden

---

## 7. Risiken

| Risiko | Auswirkung | Wahrsch. | Gegenmaßnahme |
|---|---|---|---|
| Pipeline-Laufzeit zu lang für Demo | Demo scheitert | mittel | Caching, kleine Test-Images, vorbereiteter Run + Live-Trigger auf einem Mini-Snippet |
| "Grüne" Pipeline ohne Findings | Kein Erkenntnisgewinn | hoch | Bewusst verwundbare Snippets (F-08), z. B. SQL-Injection, veraltete Lib, hartcodiertes Secret |
| Hohe False-Positive-Rate (insb. DAST) | Fehlinterpretation | mittel | Findings manuell verifizieren, FP-Quote als Erkenntnis dokumentieren (Folie 39) |
| Netzwerk-/Internetabhängigkeit bei Demo | Totalausfall | mittel | Lokale Registry, Images vorab gezogen, Screencast als Fallback |
| Tool-Wildwuchs, Scope Creep | Zeitüberschreitung | hoch | Harte Begrenzung auf 4–6 Tools, Umfang nach Testklassen (F-02) |
| Ungleiche Arbeitsteilung | Qualitätsverlust | mittel | Rollen aus Abschnitt 2, Aufgaben im Issue-Tracker |

---

## 8. Abgrenzung des Umfangs

**In Scope:** Git-Repo, CI-Pipeline, SAST, SCA, Secret Scanning, Container-Image-Scan, Security Gate, Findings-Aggregation, 3 Demo-Workloads, Report, Präsentation.

**Out of Scope:** Kubernetes-Produktionsbetrieb, Container-Runtime-Security-Plattformen (NeuVector/Twistlock-Klasse), CSPM/CNAPP, IAST, kommerzielle Penetrationstests als Managed Service, Policy-Enforcement im Cluster (OPA).

---

## 9. Abnahmekriterien (Definition of Done)

1. Repository enthält Pipeline-as-Code und läuft ohne manuelle Schritte nach einem Push.
2. ≥ 4 Tools aus ≥ 4 Testklassen sind aktiv und erzeugen Reports.
3. Mindestens ein Run bricht nachweislich am Security Gate ab; nach dem Fix läuft derselbe Code grün durch.
4. 3 dokumentierte Runs mit unterschiedlichen Code-Artefakten.
5. Findings-Report liegt vor: Finding, Tool, Severity, Bewertung (echt/False Positive), Maßnahme.
6. Metriken je Run erfasst (Findings nach Severity, Laufzeit).
7. Präsentation geprobt, ≤ 15 Min., Demo inklusive Fallback.

---

## 10. Rückverfolgbarkeit

| Aufgaben-Anforderung | Umgesetzt durch |
|---|---|
| A-01, A-02 | F-01, F-02, F-06 |
| A-04 | F-01 (Pipeline-as-Code), Trigger bei Push/MR |
| A-05 | F-08, drei Demo-Workloads |
| A-07 | F-04, F-07, F-09 |
| A-08 | Abschnitt 9, NF-02, NF-04 |
