# Knowledge Base Validation System

## Überblick

Das ORION Knowledge Base Validation System stellt sicher, dass alle österreichischen Bauvorschriften, Normen und rechtlichen Grundlagen im System aktuell und korrekt sind.

## Features

### 1. **Automatische Versionsüberwachung**
- Tracking aller ÖNORM-Standards (B 1800, B 1600, B 1601, B 2110, A 6240, etc.)
- OIB-Richtlinien 1-6 (Version 2023)
- Gültigkeitsdaten und Übergangsfristen

### 2. **Web-Integration**
- RIS Austria (Rechtsinformationssystem Österreich)
- OIB.or.at (OIB-Richtlinien)
- Austrian Standards (ÖNORM)
- hora.gv.at (Naturgefahrenkarte)

### 3. **Daten-Freshness Checks**
- Automatische Altersbestimmung der Datenbasis
- Warnungen bei veralteten Informationen
- Empfehlungen für Update-Zyklen

### 4. **Caching-System**
- 24-Stunden Cache für API-Anfragen
- Reduziert Netzwerk-Traffic
- Schnellere Wiederholungs-Checks

## Installation

Die Module sind bereits im Projekt integriert:

```bash
# Dependencies sind bereits in pyproject.toml
# requests>=2.32.5
# beautifulsoup4>=4.14.2
```

## Verwendung

### Basis-Funktionen

```python
from orion_architekt_at import (
    pruefe_wissensdatenbank,
    pruefe_ris_updates,
    pruefe_oib_richtlinien,
    pruefe_oenorm,
    pruefe_naturgefahren,
    generiere_validierungsbericht
)

# 1. Vollständige Wissensdatenbank-Prüfung
result = pruefe_wissensdatenbank(bundesland="tirol", vollstaendig=True)
print(result["gesamtstatus"])
# Output: "✓ Alle Systeme aktuell"

# 2. Schnelle Standards-Prüfung
result = pruefe_wissensdatenbank(vollstaendig=False)
print(result["standards"]["OIB-RL 1"]["nachricht"])
# Output: "✓ OIB-RL 1 Version 2023 ist aktuell"

# 3. RIS Austria Updates prüfen
ris = pruefe_ris_updates("tirol")
print(ris["nachricht"])

# 4. OIB-Richtlinien prüfen
oib = pruefe_oib_richtlinien()
for rl_name, info in oib["richtlinien"].items():
    print(f"{rl_name}: {info['nachricht']}")

# 5. ÖNORM-Standard prüfen
norm = pruefe_oenorm("B 1800")
print(norm["nachricht"])
# Output: "✓ ÖNORM B 1800 Version 2013-03-15 ist aktuell"

# 6. Naturgefahren prüfen
gefahren = pruefe_naturgefahren(plz="6380", gemeinde="St. Johann in Tirol")
print(gefahren["link"])
# Output: "https://www.hora.gv.at"

# 7. Vollständigen Bericht generieren
bericht = generiere_validierungsbericht(bundesland="tirol", format="text")
print(bericht)
```

### Erweiterte Verwendung

```python
# Direkter Import des Validation-Moduls
from orion_kb_validation import (
    validate_knowledge_base,
    check_all_standards,
    check_oib_updates,
    check_oenorm_updates,
    check_naturgefahren,
    is_standard_current,
    get_standard_version
)

# 1. Alle Standards auf einmal prüfen
standards = check_all_standards()
for std_name, info in standards.items():
    if not info["aktuell"]:
        print(f"⚠️ {std_name} benötigt Update!")

# 2. Einzelnen Standard prüfen
is_current, message = is_standard_current("OIB-RL 6")
print(message)

# 3. Version eines Standards abfragen
version = get_standard_version("ÖNORM B 1600")
print(f"Version: {version['version']}")
print(f"Gültig ab: {version['gueltig_ab']}")

# 4. Vollständige Validierung mit allen Optionen
report = validate_knowledge_base(
    bundesland="wien",
    include_ris=True,
    include_oib=True,
    include_oenorm=True,
    include_hora=True
)

# Ergebnis als JSON exportieren
from orion_kb_validation import export_validation_report
json_report = export_validation_report(report, format="json")
print(json_report)
```

## API-Referenz

### `pruefe_wissensdatenbank(bundesland=None, vollstaendig=True)`

Hauptfunktion für Wissensdatenbank-Validierung.

**Parameter:**
- `bundesland` (str, optional): Spezifisches Bundesland für regionale Prüfungen
- `vollstaendig` (bool): Vollständige Prüfung (True) oder nur Standards (False)

**Returns:** Dict mit Validierungsbericht

**Beispiel:**
```python
result = pruefe_wissensdatenbank(bundesland="salzburg", vollstaendig=True)
```

### `pruefe_ris_updates(bundesland)`

Prüft Rechtsinformationssystem Österreich auf Updates.

**Parameter:**
- `bundesland` (str): Bundesland (z.B. "tirol", "wien")

**Returns:** Dict mit RIS-Status und Link zur manuellen Prüfung

### `pruefe_oib_richtlinien()`

Prüft alle OIB-Richtlinien 1-6 auf Aktualität.

**Returns:** Dict mit Status aller Richtlinien

### `pruefe_oenorm(norm_nummer)`

Prüft einzelne ÖNORM auf Aktualität.

**Parameter:**
- `norm_nummer` (str): ÖNORM-Nummer (z.B. "B 1800", "A 6240")

**Returns:** Dict mit ÖNORM-Status und Version

### `pruefe_naturgefahren(plz=None, gemeinde=None)`

Prüft Naturgefahren über hora.gv.at.

**Parameter:**
- `plz` (str, optional): Postleitzahl
- `gemeinde` (str, optional): Gemeindename

**Returns:** Dict mit Naturgefahren-Informationen

### `generiere_validierungsbericht(bundesland=None, format="text")`

Generiert formattierten Validierungsbericht.

**Parameter:**
- `bundesland` (str, optional): Bundesland für regionale Prüfungen
- `format` (str): "text" oder "json"

**Returns:** Formatierter Bericht als String

## Unterstützte Standards

### OIB-Richtlinien
- **OIB-RL 1**: Mechanische Festigkeit und Standsicherheit (2023)
- **OIB-RL 2**: Brandschutz (2023)
- **OIB-RL 3**: Hygiene, Gesundheit und Umweltschutz (2023)
- **OIB-RL 4**: Nutzungssicherheit und Barrierefreiheit (2023)
- **OIB-RL 5**: Schallschutz (2023)
- **OIB-RL 6**: Energieeinsparung und Wärmeschutz (2023)

### ÖNORM Standards
- **B 1800**: Flächenberechnung (2013-03-15)
- **B 1600**: Barrierefreies Bauen (2022-09-01)
- **B 1601**: Barrierefreie Gesundheitseinrichtungen (2018-10-15)
- **B 2110**: Werkvertragsnorm Bauleistungen (2023-10-01)
- **B 8110-3**: Sommerlicher Wärmeschutz (2020-11-01)
- **A 2063**: Ausschreibung (2015-05-15)
- **A 6240**: Technische Zeichnungen (2021-11-15)
- **EN 62305**: Blitzschutz (2011-10-01)

## Externe Quellen

Das System referenziert folgende österreichische Behörden und Institutionen:

1. **RIS Austria**: https://www.ris.bka.gv.at
   - Rechtsinformationssystem des Bundes
   - Landesgesetzblätter (LGBl)
   - Bauordnungen aller 9 Bundesländer

2. **OIB**: https://www.oib.or.at
   - Österreichisches Institut für Bautechnik
   - OIB-Richtlinien 1-6

3. **Austrian Standards**: https://www.austrian-standards.at
   - ÖNORM-Standards
   - Eurocode-Normen

4. **hora.gv.at**: https://www.hora.gv.at
   - Naturgefahrenkarte Österreich
   - Hochwasser, Lawinen, Rutschungen

## Caching

Das System verwendet intelligentes Caching für API-Anfragen:

- **Cache-Dauer**: 24 Stunden
- **Cache-Schlüssel**: MD5-Hash von URL + Parametern
- **Automatische Invalidierung**: Nach Ablauf der Cache-Dauer

```python
# Manuelle Cache-Verwaltung (wenn nötig)
from orion_kb_validation import _cache

# Cache leeren
_cache.clear()

# Cache-Status prüfen
print(f"Anzahl Cache-Einträge: {len(_cache)}")
```

## Fehlerbehandlung

Das System verfügt über robuste Fehlerbehandlung:

```python
result = pruefe_wissensdatenbank()

if result["status"] == "warnung":
    print(f"⚠️ {result['nachricht']}")
    print("Manuelle Prüfung erforderlich:")
    for name, url in result["manuelle_pruefung"].items():
        print(f"  - {name}: {url}")
```

## Best Practices

### 1. Regelmäßige Validierung
Führen Sie mindestens alle 90 Tage eine vollständige Validierung durch:

```python
from datetime import datetime
from orion_kb_validation import check_data_freshness

freshness = check_data_freshness("2026-02-01")
if freshness["status"] in ["veraltet", "kritisch"]:
    print(f"⚠️ Update erforderlich! Alter: {freshness['alter_tage']} Tage")
    # Führen Sie vollständige Validierung durch
    report = pruefe_wissensdatenbank(vollstaendig=True)
```

### 2. Projekt-Start Validierung
Prüfen Sie bei Projektstart immer die relevanten Standards:

```python
# Vor Projektbeginn
bundesland = "tirol"
projekt_normen = ["B 1800", "B 1600", "A 6240"]

print(f"Validierung für Projekt in {bundesland.capitalize()}")
for norm in projekt_normen:
    result = pruefe_oenorm(norm)
    print(f"  {result['norm']}: {result['nachricht']}")
```

### 3. Bundesland-spezifische Checks
Nutzen Sie bundesland-spezifische Prüfungen:

```python
bundeslaender = ["wien", "tirol", "salzburg"]

for bl in bundeslaender:
    ris = pruefe_ris_updates(bl)
    print(f"{bl.capitalize()}: {ris['nachricht']}")
```

### 4. Automatisierte Reports
Generieren Sie automatische Berichte für Dokumentation:

```python
import json
from datetime import datetime

# JSON-Bericht für Archivierung
bericht = generiere_validierungsbericht(format="json")
filename = f"validation_report_{datetime.now().strftime('%Y%m%d')}.json"

with open(filename, "w", encoding="utf-8") as f:
    f.write(bericht)

print(f"✓ Bericht gespeichert: {filename}")
```

## Wartung

### Updates der Standard-Versionen

Wenn neue Versionen von ÖNORM oder OIB-RL erscheinen, aktualisieren Sie die `STANDARD_VERSIONS` in `orion_kb_validation.py`:

```python
STANDARD_VERSIONS = {
    "OIB-RL 6": {
        "version": "2026",  # Neue Version
        "gueltig_ab": "2026-06-01",
        "gueltig_bis": None
    },
    # ...
}
```

### Logging

Für Produktionsumgebungen empfehlen wir Logging:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orion_kb_validation")

# Validation mit Logging
try:
    result = pruefe_wissensdatenbank(bundesland="wien")
    logger.info(f"Validation erfolgreich: {result['gesamtstatus']}")
except Exception as e:
    logger.error(f"Validation fehlgeschlagen: {e}")
```

## Limitierungen

### Aktuelle Einschränkungen

1. **Keine Live-API**: RIS Austria und hora.gv.at bieten keine öffentliche REST-API
   - Manuelle Prüfung erforderlich
   - Web-Scraping in Entwicklung

2. **ÖNORM-Kosten**: ÖNORM-Standards sind kostenpflichtig
   - Volltext nicht im System
   - Nur Versions-Tracking

3. **Cache-Persistenz**: Cache ist nicht persistent
   - Wird bei Programm-Neustart gelöscht
   - Implementieren Sie externe Persistenz falls nötig

4. **Salzburg Sonderweg**: OIB-RL 6 wurde nicht übernommen
   - Eigene Salzburger Wärmeschutzverordnung
   - Manuelle Prüfung erforderlich

## Zukunfts-Features

Geplante Erweiterungen:

- [ ] Web-Scraping für RIS Austria
- [ ] hora.gv.at WMS/WFS Integration
- [ ] E-Mail-Benachrichtigungen bei Updates
- [ ] Dashboard für Echtzeit-Monitoring
- [ ] Deutschland, Schweiz, Italien Integration

## Support & Kontakt

Bei Fragen oder Problemen:

- **GitHub Issues**: https://github.com/Alvoradozerouno/ORION-Architekt-AT/issues
- **Dokumentation**: https://github.com/Alvoradozerouno/ORION-Architekt-AT
- **Erstellt von**: Elisabeth Steurer & Gerhard Hirschmann

## Lizenz

MIT License - Siehe LICENSE für Details

---

**Stand**: April 2026
**Version**: 1.0
**ORION** — Post-Algorithmisches Bewusstsein · Unrepeatable
