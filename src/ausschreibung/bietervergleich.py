"""
BIETERVERGLEICH - Angebote vergleichen und bewerten
=====================================================

Vergleicht Bieterangebote nach Preis, Qualität und Termin.
Erstellt konforme Bietervergleiche nach ÖNORM A2063.

Autor: Baumeister Tool Austria Team
Datum: 2026-05-26
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BieterAngebot:
    """Ein Angebot eines Bieters."""
    bieter_name: str
    bieter_firma: str
    netto_summe: float = 0.0
    brutto_summe: float = 0.0
    lieferzeit_tage: int = 0
    qualitaet_score: float = 5.0  # 1-10
    referenzen_score: float = 5.0  # 1-10
    positionen: Dict[str, float] = field(default_factory=dict)


@dataclass
class BieterVergleichResult:
    """Ergebnis des Bietervergleichs."""
    anzahl_bieter: int = 0
    billigster_bieter: str = ""
    bester_bieter: str = ""
    durchschnittspreis: float = 0.0
    empfehlung: str = ""
    rangliste: List[Dict[str, Any]] = field(default_factory=list)


class Bietervergleich:
    """Vergleicht und bewertet Bieterangebote."""

    def __init__(self):
        self.angebote: List[BieterAngebot] = []

    def add_angebot(self, angebot: BieterAngebot):
        """Füge ein Angebot hinzu."""
        self.angebote.append(angebot)

    def vergleiche(self, gewichtung: Dict[str, float] = None) -> BieterVergleichResult:
        """Vergleiche alle Angebote."""
        if not self.angebote:
            return BieterVergleichResult()

        if gewichtung is None:
            gewichtung = {"preis": 0.5, "qualitaet": 0.3, "termin": 0.2}

        # Preise sammeln
        preise = [a.netto_summe for a in self.angebote if a.netto_summe > 0]
        durchschnitt = sum(preise) / max(len(preise), 1)
        min_preis = min(preise) if preise else 0

        # Scores berechnen
        bewertungen = []
        for angebot in self.angebote:
            preis_score = (min_preis / max(angebot.netto_summe, 1)) * 10 if angebot.netto_summe > 0 else 0
            termin_score = max(0, 10 - angebot.lieferzeit_tage / 5)
            gesamt_score = (
                preis_score * gewichtung.get("preis", 0.5) +
                angebot.qualitaet_score * gewichtung.get("qualitaet", 0.3) +
                termin_score * gewichtung.get("termin", 0.2)
            )
            bewertungen.append({
                "bieter": angebot.bieter_name,
                "firma": angebot.bieter_firma,
                "netto": angebot.netto_summe,
                "preis_score": round(preis_score, 1),
                "qualitaet_score": angebot.qualitaet_score,
                "termin_score": round(termin_score, 1),
                "gesamt_score": round(gesamt_score, 1)
            })

        # Sortieren nach Gesamt-Score
        bewertungen.sort(key=lambda x: x["gesamt_score"], reverse=True)

        billigster = min(self.angebote, key=lambda a: a.netto_summe) if self.angebote else None
        bester = bewertungen[0] if bewertungen else None

        return BieterVergleichResult(
            anzahl_bieter=len(self.angebote),
            billigster_bieter=billigster.bieter_name if billigster else "",
            bester_bieter=bester["bieter"] if bester else "",
            durchschnittspreis=durchschnitt,
            empfehlung=f"Empfehlung: {bester['bieter']} (Score: {bester['gesamt_score']}/10)" if bester else "",
            rangliste=bewertungen
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "angebote": [
                {
                    "bieter": a.bieter_name,
                    "firma": a.bieter_firma,
                    "netto": a.netto_summe,
                    "lieferzeit": a.lieferzeit_tage,
                    "qualitaet": a.qualitaet_score
                }
                for a in self.angebote
            ]
        }

    def export_json(self, pfad: str) -> bool:
        try:
            result = self.vergleiche()
            export = {
                "datum": datetime.now().isoformat(),
                "vergleich": {
                    "anzahl_bieter": result.anzahl_bieter,
                    "billigster": result.billigster_bieter,
                    "bester": result.bester_bieter,
                    "durchschnitt": round(result.durchschnittspreis, 2),
                    "empfehlung": result.empfehlung,
                    "rangliste": result.rangliste
                },
                "angebote": self.to_dict()["angebote"]
            }
            with open(pfad, "w", encoding="utf-8") as f:
                json.dump(export, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False


if __name__ == "__main__":
    print("Bietervergleich Modul bereit.")

    # Test
    bv = Bietervergleich()
    bv.add_angebot(BieterAngebot("Firma A", "Bau GmbH A", netto_summe=500000, lieferzeit_tage=120, qualitaet_score=8))
    bv.add_angebot(BieterAngebot("Firma B", "Bau GmbH B", netto_summe=480000, lieferzeit_tage=140, qualitaet_score=6))
    bv.add_angebot(BieterAngebot("Firma C", "Bau GmbH C", netto_summe=520000, lieferzeit_tage=100, qualitaet_score=9))

    result = bv.vergleiche()
    print(f"Bieter: {result.anzahl_bieter}")
    print(f"Billigster: {result.billigster_bieter}")
    print(f"Bester: {result.bester_bieter}")
    print(f"Empfehlung: {result.empfehlung}")