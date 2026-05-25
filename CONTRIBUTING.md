# Contributing zu Baumeister Tool Austria

**Danke für dein Interesse, zum Projekt beizutragen!** 🇦🏗️

Baumeister Tool Austria ist eine Open-Source-Compliance-Plattform für österreichische Bauregeln. Wir freuen uns über jede Art von Beitrag — Code, Doku, Tests, Übersetzungen oder Feedback.

---

## Schnellstart für Entwickler:innen

### Voraussetzungen
- Python 3.11+
- Git
- Virtual Environment (empfohlen)

### Setup
```bash
# Repository clonen
git clone https://github.com/Alvoradozerouno/Baumeister-Tool-Austria.git
cd Baumeister-Tool-Austria

# Virtuelle Umgebung erstellen
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt
pip install -e ".[dev]"  # Dev-Dependencies

# Tests ausführen
pytest tests/ -v --cov=.
```

### Development-Server starten
```bash
python main.py
# oder mit Auto-Reload
uvicorn api.main:app --reload --port 8000
```

---

## Beiträge einreichen

### 1. Issue erstellen
Bevor du mit der Arbeit beginnst, [öffne ein Issue](https://github.com/Alvoradozerouno/Baumeister-Tool-Austria/issues) und beschreibe:
- Was möchtest du ändern/hinzufügen?
- Warum ist das wichtig?
- Gibt es bestehende Issues/PRs dazu?

### 2. Branch erstellen
```bash
git checkout -b feature/dein-feature-name
# oder
git checkout -b fix/bugfix-name
```

### 3. Code schreiben
- Folge [PEP 8](https://peps.python.org/pep-0008/) für Python-Code
- Schreibe Tests für neue Funktionen
- Aktualisiere die Dokumentation bei API-Änderungen
- Verwende type hints wo möglich

### 4. Tests ausführen
```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=. --cov-report=html

# Linting
flake8 .
black .
mypy .
```

### 5. Pull Request erstellen
- Beschreibe deine Änderungen klar
- Verlinke relevante Issues (`Fixes #123`)
- Stelle sicher, dass alle CI-Checks bestehen
- Bitte um Review

---

## Coding Standards

### Python
- **Style**: Black (88 Zeichen Zeilenlänge)
- **Linting**: Flake8 + MyPy
- **Type Hints**: Erfordert für neue Funktionen
- **Docstrings**: Google Style

### Commit Messages
Wir folgen [Conventional Commits](https://www.conventionalcommits.org/):
```
feat: add OIB-RL 7 sustainability module
fix: correct HWB calculation for climate zone 3
docs: update API documentation
test: add unit tests for Eurocode 5
refactor: improve energy calculation performance
```

### Branch Naming
- `feature/xxx` — Neue Features
- `fix/xxx` — Bugfixes
- `docs/xxx` — Dokumentation
- `test/xxx` — Tests
- `refactor/xxx` — Refactoring

---

## Gute First Issues

Suchst du nach einem Einstieg? Schau dir diese Labels an:
- [`good-first-issue`](https://github.com/Alvoradozerouno/Baumeister-Tool-Austria/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
- [`help-wanted`](https://github.com/Alvoradozerouno/Baumeister-Tool-Austria/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
- [`documentation`](https://github.com/Alvoradozerouno/Baumeister-Tool-Austria/issues?q=is%3Aissue+is%3Aopen+label%3A%22documentation%22)

---

## Projektstruktur

```
Baumeister-Tool-Austria/
├── api/              # FastAPI Backend
├── frontend/         # React Frontend (in Entwicklung)
├── src/              # Core-Bibliotheken
│   ├── eurocode*/    # Eurocode-Module
│   ├── oib_rl*/      # OIB-Richtlinien
│   └── shared/       # Gemeinsame Utilities
├── tests/            # Test-Suite
├── docs/             # Dokumentation
├── k8s/              # Kubernetes Deployments
└── .github/          # GitHub Actions & Templates
```

---

## Community

- **Discussions**: [GitHub Discussions](https://github.com/Alvoradozerouno/Baumeister-Tool-Austria/discussions)
- **Issues**: [Bug Reports & Feature Requests](https://github.com/Alvoradozerouno/Baumeister-Tool-Austria/issues)
- **Roadmap**: [PUBLIC_ROADMAP.md](./PUBLIC_ROADMAP.md)

---

## Lizenz

Mit deinem Beitrag erklärst du dich einverstanden, dass er unter der [MIT-Lizenz](./LICENSE) veröffentlicht wird.

---

**Vielen Dank für dein Engagement!** 🙏

Das Baumeister-Tool-Austria Team  
*Owner: Elisabeth Steurer & Gerhard Hirschmann*