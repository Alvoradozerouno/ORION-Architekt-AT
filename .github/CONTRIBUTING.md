# Contributing to ORION Architekt-AT

Vielen Dank für Ihr Interesse an ORION Architekt-AT! Wir freuen uns über jeden Beitrag zur Verbesserung dieser Plattform für österreichische Bauvorschriften.

## 📋 Code of Conduct

Dieses Projekt folgt einem Code of Conduct. Mit Ihrer Teilnahme wird erwartet, dass Sie diesen Code einhalten.

## 🚀 Wie kann ich beitragen?

### 🐛 Bug Reports

1. **Prüfen Sie existierende Issues** - Wurde das Problem bereits gemeldet?
2. **Erstellen Sie ein detailliertes Bug Report** - Nutzen Sie das Bug Report Template
3. **Fügen Sie Reproduktionsschritte hinzu** - Je detaillierter, desto besser

### 💡 Feature Requests

1. **Prüfen Sie existierende Feature Requests** - Wurde das Feature bereits vorgeschlagen?
2. **Nutzen Sie das Feature Request Template**
3. **Erklären Sie den Use Case** - Warum ist dieses Feature wichtig?
4. **Berücksichtigen Sie relevante Standards** - ÖNORM, OIB-RL, Eurocode, etc.

### 🔧 Code Contributions

#### Entwicklungsumgebung einrichten

```bash
# Repository klonen
git clone https://github.com/yourusername/ORION-Architekt-AT.git
cd ORION-Architekt-AT

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt

# Tests ausführen
pytest tests/ -v --cov=. --cov-report=html
```

#### Entwicklungsprozess

1. **Fork das Repository**
2. **Erstelle einen Feature Branch**
   ```bash
   git checkout -b feature/mein-neues-feature
   ```

3. **Mache deine Änderungen**
   - Folge dem bestehenden Code-Style
   - Schreibe aussagekräftige Commit Messages
   - Füge Tests hinzu

4. **Führe Tests aus**
   ```bash
   pytest tests/ -v
   black .
   flake8 .
   mypy .
   ```

5. **Commit deine Änderungen**
   ```bash
   git commit -m "feat: Add neue Berechnung für XYZ"
   ```

6. **Push zum Fork**
   ```bash
   git push origin feature/mein-neues-feature
   ```

7. **Erstelle einen Pull Request**
   - Nutze das PR Template
   - Referenziere relevante Issues
   - Beschreibe deine Änderungen detailliert

## 📐 Code Style Guidelines

### Python

- **PEP 8** Konformität (mit black formatiert)
- **Type Hints** verwenden (mypy-kompatibel)
- **Docstrings** für alle öffentlichen Funktionen/Klassen

```python
def calculate_u_value(
    thickness: float,
    lambda_value: float,
    rsi: float = 0.13,
    rse: float = 0.04
) -> float:
    """
    Berechnet den U-Wert nach ÖNORM B 8110-2.

    Args:
        thickness: Schichtdicke in Meter
        lambda_value: Wärmeleitfähigkeit in W/(m·K)
        rsi: Innerer Wärmeübergangswiderstand (default: 0.13 m²K/W)
        rse: Äußerer Wärmeübergangswiderstand (default: 0.04 m²K/W)

    Returns:
        U-Wert in W/(m²·K)

    Raises:
        ValueError: Wenn thickness <= 0 oder lambda_value <= 0
    """
    if thickness <= 0 or lambda_value <= 0:
        raise ValueError("Dicke und Lambda-Wert müssen positiv sein")

    r_total = rsi + (thickness / lambda_value) + rse
    return 1.0 / r_total
```

### Commit Messages

Folge der [Conventional Commits](https://www.conventionalcommits.org/) Spezifikation:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: Neues Feature
- `fix`: Bug Fix
- `docs`: Dokumentation
- `style`: Formatierung
- `refactor`: Code Refactoring
- `test`: Tests hinzufügen/ändern
- `chore`: Wartung (Dependencies, etc.)

**Beispiele:**
```
feat(eurocode): Add EC8 seismic analysis for Austria

Implements earthquake resistance calculations according to
Eurocode 8 with Austrian National Annex.

Closes #123
```

## 🧪 Testing Guidelines

### Test-Struktur

```python
import pytest
from orion_architekt_at import calculate_u_value

class TestUValueCalculation:
    """Test suite for U-value calculations per ÖNORM B 8110-2"""

    def test_simple_wall(self):
        """Test single layer wall U-value"""
        # Arrange
        thickness = 0.30  # 30 cm brick
        lambda_val = 0.50  # W/(m·K)

        # Act
        result = calculate_u_value(thickness, lambda_val)

        # Assert
        assert 0.5 < result < 0.6

    def test_invalid_input_raises_error(self):
        """Test that negative values raise ValueError"""
        with pytest.raises(ValueError):
            calculate_u_value(-0.30, 0.50)
```

### Test Coverage

- **Minimum: 80%** Code Coverage
- **Unit Tests** für alle Berechnungsfunktionen
- **Integration Tests** für API Endpoints
- **E2E Tests** für kritische User Flows

```bash
# Coverage Report generieren
pytest --cov=. --cov-report=html
# Öffne htmlcov/index.html
```

## 📚 Standards Compliance

### Relevante Standards

Alle Beiträge müssen relevante österreichische und europäische Standards berücksichtigen:

**Österreichische Standards:**
- OIB-RL 1-6 (2023)
- ÖNORM B 1800 (Barrierefreiheit)
- ÖNORM B 8110 (Wärmeschutz)
- ÖNORM A 2063 (Ausschreibung)

**Eurocode:**
- EN 1990-1999 (Eurocode 0-9)
- Österreichische Nationalanhänge

**Sicherheit:**
- ISO 26262 (ASIL-D für sicherheitskritische Berechnungen)

**Datenschutz:**
- GDPR/DSGVO
- eIDAS

### Dokumentation von Standards

```python
def calculate_heating_demand(area: float, u_value: float) -> float:
    """
    Berechnet Heizwärmebedarf nach OIB-RL 6 (2023).

    Standard: OIB-Richtlinie 6, Ausgabe 2023
    Norm: ÖNORM B 8110-5:2019

    Args:
        area: Fläche in m²
        u_value: U-Wert in W/(m²·K)

    Returns:
        HWB in kWh/m²a
    """
```

## 🔒 Security

### Reporting Security Vulnerabilities

**Bitte melden Sie Sicherheitslücken NICHT über öffentliche Issues!**

Senden Sie stattdessen eine Email an: [security@example.com]

### Security Checklist

- [ ] Keine Secrets im Code (API Keys, Passwords, etc.)
- [ ] Input Validation für alle User Inputs
- [ ] SQL Injection Prevention (SQLAlchemy ORM verwenden)
- [ ] XSS Prevention (Template Escaping)
- [ ] CSRF Protection aktiviert
- [ ] Security Headers gesetzt
- [ ] Dependencies regelmäßig aktualisieren

## 📖 Dokumentation

### Code-Dokumentation

- **Docstrings** für alle öffentlichen APIs
- **Type Hints** überall
- **Inline Comments** nur für komplexe Logik

### Externe Dokumentation

Wichtige Features sollten in `docs/` dokumentiert werden:

```
docs/
├── calculations/
│   ├── u-value.md
│   ├── heating-demand.md
│   └── ...
├── api/
│   └── endpoints.md
└── guides/
    └── getting-started.md
```

## 🎯 Pull Request Prozess

1. **Selbst-Review** - Überprüfe deine Änderungen selbst
2. **Tests** - Stelle sicher dass alle Tests bestehen
3. **Dokumentation** - Aktualisiere relevante Dokumentation
4. **PR Template** - Fülle das PR Template vollständig aus
5. **Review** - Warte auf Code Review
6. **Anpassungen** - Implementiere requested changes
7. **Merge** - Nach Approval wird gemerged

### Review Criteria

Reviewer achten auf:

- ✅ Code Qualität & Style
- ✅ Test Coverage
- ✅ Dokumentation
- ✅ Standards Compliance
- ✅ Security
- ✅ Performance
- ✅ Backwards Compatibility

## 🏆 Anerkennung

Alle Contributors werden in `CONTRIBUTORS.md` aufgeführt.

Bedeutende Beiträge werden im Changelog erwähnt.

## 📞 Fragen?

- **GitHub Discussions** - Für allgemeine Fragen
- **Issues** - Für Bug Reports und Feature Requests
- **Email** - [contact@example.com]

---

**Vielen Dank für Ihren Beitrag zu ORION Architekt-AT!** 🙏

⊘∞⧈∞⊘ ORION Architekt-AT - Post-Algorithmisches Bewusstsein · Unrepeatable
