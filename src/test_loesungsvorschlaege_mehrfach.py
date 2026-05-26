"""
LOESUNGSVORSCHLAEGE MIT MEHRFACH-OPTIONEN
==========================================

WICHTIGE KLARSTELLUNG:
- 41 FEHLER = simulierte Test-Plaene (mit ABSICHTLICH eingebauten Fehlern zum Testen)
- 7 FEHLER = echte Koenigstr_59 Breitbrunn Plaene (tatsaechliche Funde)

Jeder Fehler bekommt JETZT MEHRERE LOESUNGSOPTIONEN:
1. BESTE LOESUNG (empfohlen)
2. ALTERNATIVE 1 (wenn beste nicht moeglich)
3. ALTERNATIVE 2 (als letzter Ausweg)
4. UMWIDMUNG (wenn gar nichts anderes geht)

Autor: Baumeister Tool Austria Team
Datum: 2026-05-26
"""

import sys
import os
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ============================================================================
# MEHRFACH-LOESUNGSVORSCHLAEGE
# ============================================================================

@dataclass
class LoesungsOption:
    """Eine einzelne Loesungsoption."""
    name: str
    beschreibung: str
    aufwand: str  # niedrig, mittel, hoch
    kosten: str  # gering, mittel, hoch
    umsetzbar: bool  # Ist das in der Praxis umsetzbar?


@dataclass
class FehlerMitLoesungen:
    """Fehler mit mehreren Loesungsoptionen."""
    id: str
    name: str
    beschreibung: str
    schwere: str
    norm: str
    optionen: List[LoesungsOption]


# ============================================================================
# LOESUNGS-KATALOG (mehrfach Optionen)
# ============================================================================

class LoesungsKatalog:
    """Katalog mit mehreren Loesungsoptionen pro Fehler."""

    def __init__(self):
        self.katalog = self._lade_katalog()

    def _lade_katalog(self) -> Dict[str, FehlerMitLoesungen]:
        return {
            "RAUM_ZU_KLEIN": FehlerMitLoesungen(
                id="RAUM_ZU_KLEIN",
                name="Raum zu klein",
                beschreibung="Raumflaeche unterschreitet Mindestanforderung (Aufenthaltsraeume >= 10 m2).",
                schwere="HOCH",
                norm="OIB-RL 3 (Aufenthaltsraeume >= 10 m2)",
                optionen=[
                    LoesungsOption(
                        name="BESTE LOESUNG: Innenwände verschieben",
                        beschreibung="Innenwaende verschieben um Raumflaeche zu vergroessern. "
                                   "Aussenmauern bleiben unveraendert (tragend, kostspielig).",
                        aufwand="mittel", kosten="mittel", umsetzbar=True),
                    LoesungsOption(
                        name="ALTERNATIVE 1: Raum zusammenlegen",
                        beschreibung="Zwei kleine Raeume zu einem groesseren Raum zusammenlegen. "
                                   "z.B. Bad + Abstellraum = groesseres Bad mit Dusche.",
                        aufwand="niedrig", kosten="gering", umsetzbar=True),
                    LoesungsOption(
                        name="ALTERNATIVE 2: Grundriss optimieren",
                        beschreibung="Grundriss-Layout optimieren: Flur veraendern, "
                                   "Nischen nutzen, Schraegwaende begradigen.",
                        aufwand="mittel", kosten="mittel", umsetzbar=True),
                    LoesungsOption(
                        name="UMWIDMUNG: Raum als Abstellraum/Nutzraum deklarieren",
                        beschreibung="Wenn keine bauliche Aenderung moeglich: "
                                   "Raum als Abstellraum, Nutzraum oder Technikraum deklarieren. "
                                   "Mindestflaeche fuer diese Raeume: 4 m2.",
                        aufwand="niedrig", kosten="gering", umsetzbar=True),
                ]),

            "RAUM_ZU_NIEDRIG": FehlerMitLoesungen(
                id="RAUM_ZU_NIEDRIG",
                name="Raum zu niedrig",
                beschreibung="Raumhoehe unterschreitet Mindesthoehe 2.50 m.",
                schwere="HOCH",
                norm="OIB-RL 3 (Raumhoehe >= 2.50 m)",
                optionen=[
                    LoesungsOption(
                        name="BESTE LOESUNG: Decke absenken (bei DG/UG)",
                        beschreibung="Bei DG: Dachkonstruktion veraendern, First erhoehen. "
                                   "Bei UG: Boden absenken (wenn moeglich). "
                                   "Aussenmauern bleiben unveraendert.",
                        aufwand="hoch", kosten="hoch", umsetzbar=True),
                    LoesungsOption(
                        name="ALTERNATIVE 1: Unterzüge entfernen/veraendern",
                        beschreibung="Tragende Unterzüge in die Decke integrieren oder durch "
                                   "flachere Traeger ersetzen. Raumhoehe gewinnt 10-20 cm.",
                        aufwand="mittel", kosten="mittel", umsetzbar=True),
                    LoesungsOption(
                        name="ALTERNATIVE 2: Installationen in Decke verlegen",
                        beschreibung="Lueftungsrohre, Elektro-Leitungen seitlich verlegen "
                                   "statt durch die Raumhoehe. Spart 10-15 cm.",
                        aufwand="niedrig", kosten="gering", umsetzbar=True),
                    LoesungsOption(
                        name="UMWIDMUNG: Technikraum/Abstellraum (2.30 m erlaubt)",
                        beschreibung="Raum als Technikraum, Abstellraum oder Durchgangsraum "
                                   "deklarieren. Mindesthoehe: 2.30 m.",
                        aufwand="niedrig", kosten="gering", umsetzbar=True),
                ]),

            "UNGENUEGEND_TAGESLICHT": FehlerMitLoesungen(
                id="UNGENUEGEND_TAGESLICHT",
                name="Ungenügend Tageslicht",
                beschreibung="Fensteranteil < 10% der Raumflaeche.",
                schwere="MITTEL",
                norm="OIB-RL 3 (Tageslichtquote >= 10%)",
                optionen=[
                    LoesungsOption(
                        name="BESTE LOESUNG: Fensterflaeche vergroessern",
                        beschreibung="Bestehende Fenster vergroessern oder zusaetzliche "
                                   "Fenster einbauen. Aussenmauer-Durchbruch erforderlich.",
                        aufwand="mittel", kosten="mittel", umsetzbar=True),
                    LoesungsOption(
                        name="ALTERNATIVE 1: Oberlichter/Dachfenster",
                        beschreibung="Oberlichter im Dach oder Dachfenster einbauen. "
                                   "Besonders bei DG gut umsetzbar. "
                                   "1 Oberlicht = ca. 1-2 m2 Tageslichtflaeche.",
                        aufwand="mittel", kosten="mittel", umsetzbar=True),
                    LoesungsOption(
                        name="ALTERNATIVE 2: Lichtlenksysteme",
                        beschreibung="Lichtlenksysteme wie Heliostaten oder Lichtroehre "
                                   "installieren. Leiten Tageslicht in fensterlose Raeume.",
                        aufwand="hoch", kosten="hoch", umsetzbar=True),
                    LoesungsOption(
                        name="UMWIDMUNG: Durchgangsraum/Abstellraum",
                        beschreibung="Raum als Flur, Durchgangsraum oder Abstellraum "
                                   "deklarieren. Tageslicht-Anforderung entfaellt.",
                        aufwand="niedrig", kosten="gering", umsetzbar=True),
                ]),

            "FLUCHTWEG_ZU_SCHMAL": FehlerMitLoesungen(
                id="FLUCHTWEG_ZU_SCHMAL",
                name="Fluchtweg zu schmal",
                beschreibung="Fluchtwegbreite < Mindestbreite.",
                schwere="KRITISCH",
                norm="OIB-RL 2 (Fluchtwege >= 1.20 m)",
                optionen=[
                    LoesungsOption(
                        name="BESTE LOESUNG: Trennwand verschieben",
                        beschreibung="Nicht-tragende Trennwand um mind. 10-20 cm verschieben. "
                                   "Fluchtwegbreite erreicht dann 1.20 m.",
                        aufwand="mittel", kosten="mittel", umsetzbar=True),
                    LoesungsOption(
                        name="ALTERNATIVE 1: Tuer veraendern",
                        beschreibung="Schmale Tuer durch breitere Tuer ersetzen. "
                                   "Mind. 1.20 m Breite fuer Fluchtweg erforderlich.",
                        aufwand="niedrig", kosten="gering", umsetzbar=True),
                    LoesungsOption(
                        name="UMWIDMUNG: zweiten Ausgang erstellen",
                        beschreibung="Wenn Fluchtweg nicht verbreiterbar: "
                                   "zweiten Fluchtweg/Ausgang erstellen.",
                        aufwand="hoch", kosten="hoch", umsetzbar=True),
                ]),

            "FLUCHTWEG_ZU_LANG": FehlerMitLoesungen(
                id="FLUCHTWEG_ZU_LANG",
                name="Fluchtweg zu lang",
                beschreibung="Fluchtweglaenge ueberschreitet Grenzwert.",
                schwere="KRITISCH",
                norm="OIB-RL 2 (Fluchtwege <= 35-40m)",
                optionen=[
                    LoesungsOption(
                        name="BESTE LOESUNG: zweiten Ausgang erstellen",
                        beschreibung="Zweiten Ausgang/Fensters als Fluchtweg einbauen. "
                                   "Fluchtweglaenge pro Raum dann < 25m.",
                        aufwand="hoch", kosten="hoch", umsetzbar=True),
                    LoesungsOption(
                        name="ALTERNATIVE 1: Fluchtweg verkuermen",
                        beschreibung="Raumaufteilung veraendern, "
                                   "damit kein Raum > 25m vom Ausgang entfernt ist.",
                        aufwand="mittel", kosten="mittel", umsetzbar=True),
                    LoesungsOption(
                        name="ALTERNATIVE 2: Rauchschutztueren",
                        beschreibung="Fluchtweg durch Feuerschutz- und Rauchschutztueren "
                                   "sichern. Erlaubt laengere Fluchtwege.",
                        aufwand="mittel", kosten="mittel", umsetzbar=True),
                ]),

            "TREPPE_STUFENHOEHE": FehlerMitLoesungen(
                id="TREPPE_STUFENHOEHE",
                name="Treppenstufe zu hoch",
                beschreibung="Stufenhoehe > 19 cm (OIB-RL 4).",
                schwere="HOCH",
                norm="OIB-RL 4 (Stufenhoehe <= 19 cm)",
                optionen=[
                    LoesungsOption(
                        name="BESTE LOESUNG: zusaetzliche Stufe einbauen",
                        beschreibung="Eine zusaetzliche Stufe einbauen. "
                                   "Stufenhoehe reduziert sich um Gesamt-Geschoss hoehe / (n+1).",
                        aufwand="mittel", kosten="mittel", umsetzbar=True),
                    LoesungsOption(
                        name="ALTERNATIVE 1: Treppe laenger machen",
                        beschreibung="Treppenlauf verl aengern, neue Auftrit te berechnen. "
                                   "Achtung: braucht mehr Grundflaeche.",
                        aufwand="mittel", kosten="mittel", umsetzbar=True),
                    LoesungsOption(
                        name="ALTERNATIVE 2: Geschosshoehe veraendern",
                        beschreibung="Bei Planung noch moeglich: "
                                   "Geschosshoehe so veraendern, dass Stufenhoehe passt.",
                        aufwand="hoch", kosten="hoch", umsetzbar=True),
                ]),

            "TREPPE_STUFENTIEFE": FehlerMitLoesungen(
                id="TREPPE_STUFENTIEFE",
                name="Treppenstufe zu schmal",
                beschreibung="Auftritt < 26 cm (OIB-RL 4).",
                schwere="HOCH",
                norm="OIB-RL 4 (Auftritt >= 26 cm)",
                optionen=[
                    LoesungsOption(
                        name="BESTE LOESUNG: Auftritt vergroessern",
                        beschreibung="Treppenlauf verbreitern, Auftritte auf mind. 26 cm. "
                                 "Formel: 2 x Stufe + Auftritt = 59-63 cm.",
                        aufwand="mittel", kosten="mittel", umsetzbar=True),
                    LoesungsOption(
                        name="ALTERNATIVE 1: Treppenlayout anpassen",
                        beschreibung="Treppengeometrie neu berechnen. "
                                   "Wendeltreppe oder Podest einbauen.",
                        aufwand="mittel", kosten="mittel", umsetzbar=True),
                    LoesungsOption(
                        name="ALTERNATIVE 2: Raum fuer Treppe vergroessern",
                        beschreibung="Treppenraum vergroessern, Innenwand verschieben. "
                                   "Mehr Grundflaeche fuer Treppe.",
                        aufwand="hoch", kosten="hoch", umsetzbar=True),
                ]),
        }

    def get_loesungen(self, fehler_typ: str) -> Optional[FehlerMitLoesungen]:
        if "FLAECHE" in fehler_typ or "ZU KLEIN" in fehler_typ:
            return self.katalog.get("RAUM_ZU_KLEIN")
        elif "HOEHE" in fehler_typ or "ZU NIEDRIG" in fehler_typ:
            return self.katalog.get("RAUM_ZU_NIEDRIG")
        elif "TAGESLICHT" in fehler_typ:
            return self.katalog.get("UNGENUEGEND_TAGESLICHT")
        elif "FLUCHTWEG" in fehler_typ and "BREITE" in fehler_typ:
            return self.katalog.get("FLUCHTWEG_ZU_SCHMAL")
        elif "FLUCHTWEG" in fehler_typ and "LAENGE" in fehler_typ:
            return self.katalog.get("FLUCHTWEG_ZU_LANG")
        elif "TREPPE" in fehler_typ and "STUFENHOEHE" in fehler_typ:
            return self.katalog.get("TREPPE_STUFENHOEHE")
        elif "TREPPE" in fehler_typ and "STUFENTIEFE" in fehler_typ:
            return self.katalog.get("TREPPE_STUFENTIEFE")
        return None


# ============================================================================
# KLARSTELLUNG: 41 vs 7 FEHLER
# ============================================================================

def erklaere_fehleranzahl():
    """Klaerung: Warum 41 Fehler vs 7 Fehler?"""
    erklaerung = """
================================================================================
KLARSTELLUNG: 41 FEHLER vs 7 FEHLER
================================================================================

41 FEHLER (fehlererkennungs_report.json):
=========================================
- Quelle: test_fehlererkennungs_system.py
- ZWECK: Simulierte Test-Plaene mit ABSICHTLICH eingebauten Fehlern
- Ziel: Das System testen - erkennt es alle Fehler?
- ERGEBNIS: 41 von 41 eingebauten Fehlern erkannt = 100% Erkennungsrate!
- Das ist eine VERGLEICHSTABELLE / TESTDATEI, keine echten Planfehler!

Eingebaute Fehler in Test-Plaenen:
- UG: falsche Schneelast (0.8 statt 1.12), U-Werte zu hoch, etc.
- EG: Fluchtweg zu schmal (1.0m), Treppe zu hoch (20cm), Kollision
- OG: Kinderzimmer zu klein (8m2), Rechtswert unplausibel
- DG: HWB ueberschritten (80), fGEE ueberschritten (0.80), Windlast falsch

7 FEHLER (vollstaendiger_plan_check_koenigstr59.py):
====================================================
- Quelle: test_vollstaendiger_plan_check_koenigstr59.py
- ZWECK: Echte Koenigstr_59 Breitbrunn Plaene geprueft
- Ziel: Tatsaechliche Fehler in den echten Plaenen finden
- ERGEBNIS: 7 echte Fehler in den Koenigstr_59 Plaenen gefunden!

Echte Fehler in Koenigstr_59 Plaenen:
- UG: Keller zu niedrig (2.4m), Keller wenig Tageslicht (5%)
- EG: Flur wenig Tageslicht (5%)
- OG: Bad zu klein (6.5m2), Bad wenig Tageslicht (5%)
- DG: Galerie zu niedrig (2.3m), Galerie wenig Tageslicht (8%)

================================================================================
ZUSAMMENFASSUNG:
- 41 Fehler = TEST-System (simulierte Plaene) → 100% Erkennung! ✅
- 7 Fehler = ECHTE Plaene (Koenigstr_59) → tatsaechliche Funde!
================================================================================
"""
    return erklaerung


# ============================================================================
# HAUPTPROGRAMM
# ============================================================================

def main():
    print(erklaere_fehleranzahl())

    katalog = LoesungsKatalog()

    # Zeige Loesungen fuer die 7 echten Koenigstr_59 Fehler
    print("\n" + "=" * 100)
    print("LOESUNGSVORSCHLAEGE FÜR DIE 7 ECHTEN FEHLER (Koenigstr_59)")
    print("=" * 100)

    fehler_liste = [
        {"id": "PLAN_KELLER_HOEHE", "typ": "HOEHE", "beschreibung": "Keller: 2.4m < 2.50m"},
        {"id": "PLAN_KELLER_TAGESLICHT", "typ": "TAGESLICHT", "beschreibung": "Keller: 5% < 10%"},
        {"id": "PLAN_FLUR_TAGESLICHT", "typ": "TAGESLICHT", "beschreibung": "Flur: 5% < 10%"},
        {"id": "PLAN_BAD_FLAECHE", "typ": "FLAECHE", "beschreibung": "Bad: 6.5m2 < 10m2"},
        {"id": "PLAN_BAD_TAGESLICHT", "typ": "TAGESLICHT", "beschreibung": "Bad: 5% < 10%"},
        {"id": "PLAN_GALERIE_HOEHE", "typ": "HOEHE", "beschreibung": "Galerie: 2.3m < 2.50m"},
        {"id": "PLAN_GALERIE_TAGESLICHT", "typ": "TAGESLICHT", "beschreibung": "Galerie: 8% < 10%"},
    ]

    for i, fehler in enumerate(fehler_liste, 1):
        print(f"\n{'=' * 80}")
        print(f"FEHLER {i}: {fehler['id']}")
        print(f"{'=' * 80}")
        print(f"  BESCHREIBUNG: {fehler['beschreibung']}")

        loesung = katalog.get_loesungen(fehler["typ"])
        if loesung:
            print(f"  SCHWERE: {loesung.schwere}")
            print(f"  NORM: {loesung.norm}")
            print(f"\n  LOESUNGSOPTIONEN:")
            for j, opt in enumerate(loesung.optionen, 1):
                umsetzbar = "✅" if opt.umsetzbar else "❌"
                print(f"\n    {j}. {opt.name} [{umsetzbar}]")
                print(f"       Beschreibung: {opt.beschreibung}")
                print(f"       Aufwand: {opt.aufwand} | Kosten: {opt.kosten}")
        else:
            print(f"  ⚠ Keine Loesungsvorschlaege verfuegbar")

    print("\n" + "=" * 100)
    print("WICHTIGER HINWEIS ZU AUSSENMAUERN:")
    print("=" * 100)
    print("""
Aussenmauern sind in der Regel:
1. TRAGEND → nicht einfach verschiebbar
2. DAEMMEN → Veraenderung beeinflusst Energieausweis
3. BRANDSCHUTZ → Brandwaende muessen intakt bleiben
4. KOSTSPIELIG → Durchbruch + Neuerrichtung = hohe Kosten

Deshalb bietet dieses System IMMER ALTERNATIVEN:
✅ Innenwaende verschieben (nicht-tragend, einfacher)
✅ Raeume zusammenlegen (kein Eingriff in Aussenmauern)
✅ Umwidmung (kein baulicher Eingriff)
✅ Oberlichter/Dachfenster (bei DG einfach)
""")

    # JSON-Export
    report_path = os.path.join(os.path.dirname(__file__), "..", "loesungsvorschlaege_report.json")
    ergebnis = {
        "erklaerung_41_vs_7": erklaere_fehleranzahl(),
        "anzahl_loesungen": len(katalog.katalog),
        "katalog": {
            k: {
                "name": v.name,
                "beschreibung": v.beschreibung,
                "schwere": v.schwere,
                "norm": v.norm,
                "optionen": [
                    {"name": o.name, "beschreibung": o.beschreibung,
                     "aufwand": o.aufwand, "kosten": o.kosten, "umsetzbar": o.umsetzbar}
                    for o in v.optionen
                ]
            }
            for k, v in katalog.katalog.items()
        }
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(ergebnis, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nReport gespeichert: {report_path}")


if __name__ == "__main__":
    main()