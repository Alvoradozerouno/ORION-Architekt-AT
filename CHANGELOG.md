# Changelog

Alle wichtigen Änderungen an Baumeister Tool Austria werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/) und verwendet [Semantic Versioning](https://semver.org/lang/de/).

## [Unreleased]

### Geplant
- Vollständige React-Frontend-Implementierung mit Vite
- GPT-4 API-Integration für AI-Funktionen
- BIM/IFC Computer Vision-Modul
- Team-Kollaboration mit WebSockets
- Mobile-responsive App

---

## [3.0.0] - 2026-05-20

### Hinzugefügt
- **Multi-Agent-System**: 5 spezialisierte Agenten (Zivilingenieur, Bauphysiker, Kostenplaner, Risikomanager, The Architekt)
- **OIB-RL 7:2023**: Nachhaltigkeit und Kreislaufwirtschaft
- **EIRA Runtime**: PDF-Analyse und automatische Regel-Extraktion
- **DDGK Governance**: Governance-Modul mit IST-SOLL-Analyse
- **GitHub Actions**: 6 Workflows (CI, CD, Security, SBOM, CodeQL, Deploy)
- **Docker/Kubernetes**: Produktionsreife Deployment-Konfiguration
- **Monitoring**: Prometheus + Grafana Integration

### Geändert
- API-Struktur auf FastAPI umgestellt
- Datenbank auf PostgreSQL mit SQLAlchemy optimiert
- Security-Middleware verbessert (JWT, Rate Limiting, CORS)
- Dokumentation aktualisiert und erweitert

### Behoben
- OIB-RL 6 Energieberechnung korrigiert
- Eurocode-Berechnungen validiert
- Docker-Build-Prozess stabilisiert

---

## [2.0.0] - 2026-04-10

### Hinzugefügt
- **21 Berechnungsmodule**: OIB-RL 1-7, Eurocode EC2-EC8, Energie, BIM
- **Alle 9 Bundesländer**: Landesspezifische Bauordnungen implementiert
- **Genesis Integration**: ORION Ökosystem-Anbindung
- **API-Dokumentation**: Swagger/OpenAPI automatisch generiert
- **Test-Suite**: Unit-Tests für Kernmodule

### Geändert
- Projektstruktur modularisiert
- Python 3.11+ als Mindestversion

### Entfernt
- Veraltete Berechnungsmethoden nach OIB-RL 2019

---

## [1.0.0] - 2026-02-15

### Hinzugefügt
- **Erste stabile Version**
- OIB-RL 1-6 (2019) Berechnungen
- Grundlegende Energieberechnung (HWB/HEB/PEB)
- U-Wert-Berechnung
- Basis-API mit Flask
- SQLite-Datenbank

---

## Versionierung

Wir verwenden [Semantic Versioning](https://semver.org/lang/de/) für unsere Releases:

- **MAJOR** (X.0.0): Inkompatible API-Änderungen
- **MINOR** (0.X.0): Neue, abwärtskompatible Funktionalitäten
- **PATCH** (0.0.X): Fehlerkorrekturen

---

## Links

- [Releases](https://github.com/Alvoradozerouno/Baumeister-Tool-Austria/releases)
- [Milestones](https://github.com/Alvoradozerouno/Baumeister-Tool-Austria/milestones)
- [Projekt-Roadmap](./PUBLIC_ROADMAP.md)