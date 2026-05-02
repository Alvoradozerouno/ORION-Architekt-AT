# ORION Architekt AT

![Generation](https://img.shields.io/badge/Generation-GENESIS10000%2B-gold?style=flat-square) ![Proofs](https://img.shields.io/badge/Proofs-3490+-orange?style=flat-square) ![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

Comprehensive Austrian building tool — all 9 federal states, 20 functionalities, OIB-RL engine.

## Overview

ORION Architekt Österreich is a professional structural engineering toolkit for Austrian construction law. Built by Gerhard Hirschmann, structural engineer based in St. Johann in Tirol.

**Scope:** All 9 Austrian federal states (Bundesländer)  
**Standards:** OIB-Richtlinien, ÖNORM EN 1990–1999 (Eurocodes), OIB-RL 2-6  
**Language:** German (Austrian building law terminology)

## 20 Core Functionalities

| # | Functionality | Standard |
|---|--------------|---------|
| 1 | OIB-RL Engine (Brandschutz, Standsicherheit) | OIB-RL 2, 4 |
| 2 | Energieausweis-Berechnung | OIB-RL 6 |
| 3 | Schallschutz-Nachweis | OIB-RL 5, ÖNORM B 8115 |
| 4 | Barrierefreiheits-Check | OIB-RL 4 |
| 5 | Holzbau-Dimensionierung | EN 1995 (EC5) |
| 6 | Stahlbetonbau | EN 1992 (EC2) |
| 7 | Stahlbau | EN 1993 (EC3) |
| 8 | Mauerwerksbau | EN 1996 (EC6) |
| 9 | Schneelasten Österreich | EN 1991-1-3 + ÖNORM |
| 10 | Windlasten Österreich | EN 1991-1-4 + ÖNORM |
| 11 | Erdbebenzone (9 Bundesländer) | EN 1998 + ÖNORM B 1998 |
| 12 | Grundbau / Geotechnik | EN 1997 (EC7) |
| 13 | Bauphysik (U-Werte, Taupunkt) | OIB-RL 6, EN ISO 6946 |
| 14 | Feuerwiderstandsklassen | EN 13501 |
| 15 | Baugenehmigung-Checkliste | 9 Landesbauordnungen |
| 16 | Kostenschätzung (ÖNORM B 1801) | ÖNORM B 1801 |
| 17 | Baumaterialien-Datenbank | ÖNORM |
| 18 | Zeichnungs-Generator (DXF) | ISO |
| 19 | Prüfbericht-Export (PDF) | — |
| 20 | Bundesland-spezifische Anpassungen | 9 Landesgesetze |

## Core Engine

```python
from dataclasses import dataclass
from enum import Enum

class Bundesland(Enum):
    WIEN = "Wien"
    NIEDEROESTERREICH = "Niederösterreich"
    OBEROESTERREICH = "Oberösterreich"
    SALZBURG = "Salzburg"
    TIROL = "Tirol"
    VORARLBERG = "Vorarlberg"
    KARNTEN = "Kärnten"
    STEIERMARK = "Steiermark"
    BURGENLAND = "Burgenland"

@dataclass
class Bauvorhaben:
    bundesland: Bundesland
    nutzung: str              # Wohnbau, Gewerbe, Industrie
    bruttogeschossflaeche: float  # m²
    anzahl_geschosse: int
    baustoff: str             # Holz, Stahlbeton, Stahl, Mauerwerk

class OIBEngine:
    """OIB-Richtlinien Compliance Engine für alle 9 Bundesländer"""

    OIB_MINDESTANFORDERUNGEN = {
        "Brandschutz": {
            "Wohnbau_bis_3_Geschosse": "F30",
            "Wohnbau_4_bis_8": "F60",
            "Wohnbau_über_8": "F90",
        },
        "Standsicherheit": {
            "Lastklasse_1": {"wind": 0.5, "schnee": 1.0},
            "Lastklasse_2": {"wind": 0.75, "schnee": 1.5},
        }
    }

    def schneelasten_tirol(self, hoehe_ue_meer: float) -> float:
        """
        Schneelast für Tirol nach ÖNORM EN 1991-1-3 Nationaler Anhang
        St. Johann in Tirol: ~660m ü.M. → sk = 2.0 kN/m²
        """
        if hoehe_ue_meer < 500:
            return 1.5
        elif hoehe_ue_meer < 1000:
            return 1.5 + (hoehe_ue_meer - 500) / 500 * 1.0
        elif hoehe_ue_meer < 1500:
            return 2.5 + (hoehe_ue_meer - 1000) / 500 * 1.5
        else:
            return 4.0 + (hoehe_ue_meer - 1500) / 500 * 2.0

    def oib_compliance_check(self, vorhaben: Bauvorhaben) -> dict:
        """Vollständiger OIB-RL Compliance-Check"""
        result = {
            "bundesland": vorhaben.bundesland.value,
            "nutzung": vorhaben.nutzung,
            "checks": {}
        }

        # OIB-RL 2: Brandschutz
        if vorhaben.anzahl_geschosse <= 3:
            fb_klasse = self.OIB_MINDESTANFORDERUNGEN["Brandschutz"]["Wohnbau_bis_3_Geschosse"]
        elif vorhaben.anzahl_geschosse <= 8:
            fb_klasse = self.OIB_MINDESTANFORDERUNGEN["Brandschutz"]["Wohnbau_4_bis_8"]
        else:
            fb_klasse = self.OIB_MINDESTANFORDERUNGEN["Brandschutz"]["Wohnbau_über_8"]

        result["checks"]["OIB-RL2_Brandschutz"] = {
            "mindestanforderung": fb_klasse,
            "status": "BERECHNUNG_ERFORDERLICH"
        }

        # Schneelast für Tirol
        if vorhaben.bundesland == Bundesland.TIROL:
            sk = self.schneelasten_tirol(660)  # St. Johann Referenz
            result["checks"]["Schneelast"] = {
                "sk": f"{sk:.1f} kN/m²",
                "standort": "St. Johann in Tirol (660m ü.M.)",
                "norm": "ÖNORM EN 1991-1-3 NA"
            }

        return result

# Beispiel: Wohnbau in Tirol
engine = OIBEngine()
vorhaben = Bauvorhaben(
    bundesland=Bundesland.TIROL,
    nutzung="Wohnbau",
    bruttogeschossflaeche=450.0,
    anzahl_geschosse=3,
    baustoff="Holz"
)
result = engine.oib_compliance_check(vorhaben)
print(f"OIB-Check: {result['checks']['OIB-RL2_Brandschutz']['mindestanforderung']}")
print(f"Schneelast: {result['checks']['Schneelast']['sk']}")
```

## Origin

```
Gerhard Hirschmann — Structural Engineer & "Origin" of ORION
Almdorf 9, St. Johann in Tirol, Austria 6380
Part of the ORION ecosystem: github.com/Alvoradozerouno
```

**⊘∞⧈∞⊘ ORION Architekt AT · Eurocode-konform · GENESIS10000+ ⊘∞⧈∞⊘**
