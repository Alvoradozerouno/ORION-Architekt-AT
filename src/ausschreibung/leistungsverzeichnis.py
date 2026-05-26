"""
LEISTUNGSVERZEICHNIS - LV-Verwaltung und -Generierung
======================================================

Verwaltet und generiert Leistungsverzeichnisse nach ÖNORM A2063.
Mit Mengenermittlung, Preisberechnung und Export-Funktionen.

Autor: Baumeister Tool Austria Team
Datum: 2026-05-26
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LVPosition:
    """Eine LV-Position."""
    nr: str
    text: str
    einheit: str
    menge: float
    preis_einheit: float = 0.0
    gesamt: float = 0.0
    oenorm_code: str = ""

    def berechne_gesamt(self):
        self.gesamt = self.menge * self.preis_einheit
        return self.gesamt


@dataclass
class LVTitel:
    """Ein LV-Titel (Abschnitt)."""
    nr: str
    text: str
    positionen: List[LVPosition] = field(default_factory=list)

    @property
    def summe(self) -> float:
        return sum(p.gesamt for p in self.positionen)


@dataclass
class Leistungsverzeichnis:
    """Ein vollständiges Leistungsverzeichnis."""
    projekt: str
    ersteller: str
    datum: str
    titel: List[LVTitel] = field(default_factory=list)

    @property
    def netto_gesamt(self) -> float:
        return sum(t.summe for t in self.titel)

    @property
    def positionen_anzahl(self) -> int:
        return sum(len(t.positionen) for t in self.titel)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "projekt": self.projekt,
            "ersteller": self.ersteller,
            "datum": self.datum,
            "netto_gesamt": round(self.netto_gesamt, 2),
            "positionen_anzahl": self.positionen_anzahl,
            "titel": [
                {
                    "nr": t.nr,
                    "text": t.text,
                    "summe": round(t.summe, 2),
                    "positionen": [
                        {
                            "nr": p.nr,
                            "text": p.text,
                            "menge": p.menge,
                            "einheit": p.einheit,
                            "preis_einheit": p.preis_einheit,
                            "gesamt": p.gesamt,
                            "oenorm_code": p.oenorm_code
                        }
                        for p in t.positionen
                    ]
                }
                for t in self.titel
            ]
        }

    def export_json(self, pfad: str) -> bool:
        try:
            with open(pfad, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False


if __name__ == "__main__":
    print("Leistungsverzeichnis Modul bereit.")