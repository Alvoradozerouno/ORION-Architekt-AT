"""
ÖNORM A2063 - Ausschreibungsmodul
===================================

Implementiert die ÖNORM A2063 für Bauausschreibungen in Österreich.
Erstellt konforme Leistungsverzeichnisse und Ausschreibungsunterlagen.

Autor: Baumeister Tool Austria Team
Datum: 2026-05-26
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LVPosition:
    """Eine Position im Leistungsverzeichnis."""
    position_nr: str
    text: str
    einheit: str
    menge: float
    einheitpreis: float = 0.0
    gesamt: float = 0.0
    oenorm_code: str = ""
    zusatz: str = ""

    def __post_init__(self):
        if self.gesamt == 0.0 and self.menge > 0:
            self.gesamt = self.menge * self.einheitpreis


@dataclass
class LVTitle:
    """Ein Titel (Abschnitt) im Leistungsverzeichnis."""
    titel_nr: str
    titel_text: str
    positionen: List[LVPosition] = field(default_factory=list)


@dataclass
class Ausschreibung:
    """Eine vollständige Ausschreibung."""
    projekt: str
    auftraggeber: str
    ausschreibungs_nr: str
    datum: str
    frist: str
    leistungsverzeichnis: List[LVTitle] = field(default_factory=list)
    allgemeine_bedingungen: str = ""
    besondere_bedingungen: str = ""


@dataclass
class AusschreibungResult:
    """Ergebnis der Ausschreibungserstellung."""
    erfolgreich: bool
    fehler: str = ""
    positionen_gesamt: int = 0
    netto_gesamt: float = 0.0
    datei: str = ""


class OENORMA2063:
    """ÖNORM A2063 Ausschreibungsmodul."""

    # Standard ÖNORM-Codes
    OENORM_CODES = {
        "erdarbeiten": "A2063-1",
        "fundamente": "A2063-2",
        "mauerwerk": "A2063-3",
        "beton": "A2063-4",
        "stahlbeton": "A2063-5",
        "dachdecker": "A2063-6",
        "tischler": "A2063-7",
        "maler": "A2063-8",
        "heizung": "A2063-9",
        "lueftung": "A2063-10",
        "elektro": "A2063-11",
        "sanitaer": "A2063-12",
        "bodenbelag": "A2063-13",
        "fliesen": "A2063-14",
        "glas": "A2063-15",
        "geruest": "A2063-16",
        "abfluss": "A2063-17",
        "aussenanlagen": "A2063-18",
    }

    def __init__(self):
        self.ausschreibung = None

    def create_ausschreibung(self, projekt: str, auftraggeber: str,
                              frist: str = "30 Tage") -> Ausschreibung:
        """Erstelle eine neue Ausschreibung."""
        self.ausschreibung = Ausschreibung(
            projekt=projekt,
            auftraggeber=auftraggeber,
            ausschreibungs_nr=f"A-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            datum=datetime.now().strftime("%d.%m.%Y"),
            frist=frist,
            allgemeine_bedingungen=self._get_allgemeine_bedingungen(),
            besondere_bedingungen=self._get_besondere_bedingungen()
        )
        return self.ausschreibung

    def add_titel(self, titel_nr: str, titel_text: str) -> LVTitle:
        """Füge einen Titel (Abschnitt) hinzu."""
        titel = LVTitle(titel_nr=titel_nr, titel_text=titel_text)
        self.ausschreibung.leistungsverzeichnis.append(titel)
        return titel

    def add_position(self, titel_nr: str, position: LVPosition) -> bool:
        """Füge eine Position zu einem Titel hinzu."""
        for titel in self.ausschreibung.leistungsverzeichnis:
            if titel.titel_nr == titel_nr:
                titel.positionen.append(position)
                return True
        return False

    def create_standard_lv(self, gebaeude_typ: str = "wohnhaus") -> List[LVTitle]:
        """Erstelle ein Standard-Leistungsverzeichnis."""
        titel_list = []

        if gebaeude_typ == "wohnhaus":
            titel_list = [
                LVTitle("01", "Erdarbeiten", [
                    LVPosition("01.1", "Baugrube ausheben", "m3", 500, 25, oenorm_code="A2063-1"),
                    LVPosition("01.2", "Baugrube verfüllen", "m3", 300, 15, oenorm_code="A2063-1"),
                    LVPosition("01.3", "Boden austauschen", "m3", 100, 35, oenorm_code="A2063-1"),
                ]),
                LVTitle("02", "Fundamente", [
                    LVPosition("02.1", "Streifenfundament", "m3", 80, 250, oenorm_code="A2063-2"),
                    LVPosition("02.2", "Einzelfundament", "m3", 20, 300, oenorm_code="A2063-2"),
                    LVPosition("02.3", "Fundamentabdichtung", "m2", 150, 45, oenorm_code="A2063-2"),
                ]),
                LVTitle("03", "Mauerwerk", [
                    LVPosition("03.1", "Ziegelmauerwerk 25cm", "m2", 400, 85, oenorm_code="A2063-3"),
                    LVPosition("03.2", "Ziegelmauerwerk 30cm", "m2", 200, 95, oenorm_code="A2063-3"),
                    LVPosition("03.3", "Trennwand 12cm", "m2", 150, 55, oenorm_code="A2063-3"),
                ]),
                LVTitle("04", "Beton/Stahlbeton", [
                    LVPosition("04.1", "Stahlbetondecke", "m3", 60, 450, oenorm_code="A2063-5"),
                    LVPosition("04.2", "Beton C25/30", "m3", 100, 180, oenorm_code="A2063-4"),
                    LVPosition("04.3", "Bewehrung B550B", "kg", 5000, 2.5, oenorm_code="A2063-5"),
                ]),
                LVTitle("05", "Dachdecker", [
                    LVPosition("05.1", "Dachdichtung", "m2", 200, 65, oenorm_code="A2063-6"),
                    LVPosition("05.2", "Dachdämmung 180mm", "m2", 200, 45, oenorm_code="A2063-6"),
                    LVPosition("05.3", "Dachentwässerung", "m", 80, 35, oenorm_code="A2063-6"),
                ]),
                LVTitle("06", "Fenster/Türen", [
                    LVPosition("06.1", "Kunststofffenster", "Stk", 20, 450, oenorm_code="A2063-7"),
                    LVPosition("06.2", "Haustür", "Stk", 2, 2500, oenorm_code="A2063-7"),
                    LVPosition("06.3", "Innentür", "Stk", 15, 350, oenorm_code="A2063-7"),
                ]),
                LVTitle("07", "Elektro", [
                    LVPosition("07.1", "Elektroinstallation", "m2", 600, 45, oenorm_code="A2063-11"),
                    LVPosition("07.2", "Sicherungskasten", "Stk", 4, 800, oenorm_code="A2063-11"),
                    LVPosition("07.3", "Netzwerkverkabelung", "m", 300, 12, oenorm_code="A2063-11"),
                ]),
                LVTitle("08", "Sanitär/Heizung", [
                    LVPosition("08.1", "Heizungsinstallation", "Stk", 1, 15000, oenorm_code="A2063-9"),
                    LVPosition("08.2", "Sanitärinstallation", "Stk", 1, 12000, oenorm_code="A2063-12"),
                    LVPosition("08.3", "Badeinrichtung", "Stk", 3, 5000, oenorm_code="A2063-12"),
                ]),
                LVTitle("09", "Maler/Boden", [
                    LVPosition("09.1", "Innenanstrich", "m2", 800, 12, oenorm_code="A2063-8"),
                    LVPosition("09.2", "Fassadenanstrich", "m2", 400, 18, oenorm_code="A2063-8"),
                    LVPosition("09.3", "Parkettboden", "m2", 300, 65, oenorm_code="A2063-13"),
                ]),
            ]

        self.ausschreibung.leistungsverzeichnis = titel_list
        return titel_list

    def export_json(self, output_pfad: str) -> AusschreibungResult:
        """Exportiere Ausschreibung als JSON."""
        try:
            positionen_gesamt = 0
            netto_gesamt = 0.0

            for titel in self.ausschreibung.leistungsverzeichnis:
                for pos in titel.positionen:
                    pos.gesamt = pos.menge * pos.einheitpreis
                    netto_gesamt += pos.gesamt
                    positionen_gesamt += 1

            export_data = {
                "projekt": self.ausschreibung.projekt,
                "auftraggeber": self.ausschreibung.auftraggeber,
                "ausschreibungs_nr": self.ausschreibung.ausschreibungs_nr,
                "datum": self.ausschreibung.datum,
                "frist": self.ausschreibung.frist,
                "netto_gesamt": round(netto_gesamt, 2),
                "positionen_gesamt": positionen_gesamt,
                "leistungsverzeichnis": [
                    {
                        "titel_nr": t.titel_nr,
                        "titel_text": t.titel_text,
                        "positionen": [
                            {
                                "nr": p.position_nr,
                                "text": p.text,
                                "menge": p.menge,
                                "einheit": p.einheit,
                                "einheitpreis": p.einheitpreis,
                                "gesamt": p.gesamt,
                                "oenorm_code": p.oenorm_code
                            }
                            for p in t.positionen
                        ]
                    }
                    for t in self.ausschreibung.leistungsverzeichnis
                ]
            }

            with open(output_pfad, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            return AusschreibungResult(
                erfolgreich=True,
                positionen_gesamt=positionen_gesamt,
                netto_gesamt=netto_gesamt,
                datei=output_pfad
            )
        except Exception as e:
            return AusschreibungResult(erfolgreich=False, fehler=str(e))

    def _get_allgemeine_bedingungen(self) -> str:
        """Allgemeine Vertragsbedingungen nach ÖNORM A2063."""
        return """ALLGEMEINE VERTRAGSBEDINGUNGEN (AVB)
1. Geltungsbereich: ÖNORM A2063
2. Vergabeart: Offenes Verfahren
3. Leistungsbeschreibung: Siehe Leistungsverzeichnis
4. Ausführungsfrist: Siehe Ausschreibung
5. Gewährleistung: 3 Jahre ab Abnahme
6. Vertragsstrafe: 0.5% pro Tag der Verspätung
7. Zahlungsbedingungen: 30 Tage netto
8. Preisbasis: Festpreis
9. Nachträge: Nur mit schriftlicher Genehmigung
10. Abnahme: Gemäß ÖNORM B2110"""

    def _get_besondere_bedingungen(self) -> str:
        """Besondere Vertragsbedingungen."""
        return """BESONDERE VERTRAGSBEDINGUNGEN (BVB)
1. Baustelleneinrichtung: Durch Auftragnehmer
2. Bauwasser/Baustrom: Durch Auftraggeber
3. Koordinierung: Durch Bauleiter
4. Sicherheitskoordination: Gemäß BauKG
5. Umweltschutz: Gemäß lokalen Vorschriften
6. Lärmschutz: Werktags 07:00-18:00
7. Reinigung: Tägliche Baustellenreinigung"""


if __name__ == "__main__":
    oenorm = OENORMA2063()
    print("ÖNORM A2063 Modul bereit.")

    # Test-Ausschreibung
    ausschreibung = oenorm.create_ausschreibung("Musterprojekt", "Muster AG")
    oenorm.create_standard_lv("wohnhaus")
    result = oenorm.export_json("ausschreibung_test.json")
    print(f"Export: {result.erfolgreich}")
    print(f"Positionen: {result.positionen_gesamt}")
    print(f"Netto: € {result.netto_gesamt:,.2f}")