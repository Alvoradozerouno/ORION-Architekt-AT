"""
WHITE-BOX FEHLERERKLAERUNG: Fehler benennen, bezeichnen, loesen, warum
======================================================================

Keine Black Box mehr - jeder Fehler wird erklaert mit:
- NAME: Was ist der Fehler?
- BEZEICHNUNG: Wo und wie tritt er auf?
- WARUM: Warum ist das ein Problem?
- LOESUNG: Wie wird es behoben?
- NORM: Welche Norm/Regel wird verletzt?
- BEISPIEL: Konkreter Fall aus dem Plan

Multi-Agenten-Schwarm mit 12 Experten als "White Box"

Autor: Baumeister Tool Austria Team
Datum: 2026-05-26
"""

import sys
import os
import json
import time
import math
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.orion_architekt_at import (
    BUNDESLAENDER,
    OIB_RICHTLINIEN_AT,
    KOSTENRICHTWERTE_2026,
    REGIONALE_KOSTENFAKTOREN,
    FOERDERUNGEN,
)

from src.epistemic_system import (
    DeterministicEpistemicSystem,
    EpistemicProposition,
)


# ============================================================================
# FEHLER-ERKLAERUNG (White Box)
# ============================================================================

@dataclass
class FehlerErklaerung:
    """White-Box Fehler-Erklaerung."""
    name: str  # Kurzname
    bezeichnung: str  # Ausfuehrliche Beschreibung
    warum: str  # Warum ist das ein Problem?
    loesung: str  # Wie wird es behoben?
    norm: str  # Welche Norm wird verletzt?
    beispiel: str  # Konkreter Fall
    schwere: str  # KRITISCH, HOCH, MITTEL, NIEDRIG
    confidence: float  # 0.0 - 1.0


# ============================================================================
# FEHLER-DATENBANK (White Box)
# ============================================================================

class FehlerDatenbank:
    """White-Box Fehler-Datenbank mit Erklaerungen."""

    def __init__(self):
        self.fehler_katalog = self._lade_katalog()

    def _lade_katalog(self) -> Dict[str, FehlerErklaerung]:
        """Lade White-Box Fehler-Katalog."""
        return {
            # ===================================================================
            # BEMAßUNGSFEHLER
            # ===================================================================
            "BEM_FEHLEND": FehlerErklaerung(
                name="Fehlende Bemaßung",
                bezeichnung="Eine erforderliche Bemaßung ist im Plan nicht vorhanden.",
                warum="Ohne Bemaßung kann die Ausfuehrung nicht korrekt durchgefuehrt werden. "
                     "Dies fuehrt zu Fehlern bei der Umsetzung, Rueckfragen auf der Baustelle "
                     "und moeglicherweise zu statischen Problemen.",
                loesung="Die fehlende Bemaßung muss im Plan nachgetragen werden. "
                       "Dazu werden die tatsaechlichen Maße aus dem Grundriss oder Schnitt "
                       "abgelesen und als Bemaßungslinie eingezeichnet.",
                norm="OeNORM A 1160 (Plangestaltung)"
                     "OIB-RL 1 (Standsicherheit - Bemaßung erforderlich)",
                beispiel="Fensterbreite fehlt → Fensterhersteller weiß nicht, wie breit die Öffnung sein muss.",
                schwere="HOCH",
                confidence=0.95,
            ),
            "BEM_WIDERSPRUCH": FehlerErklaerung(
                name="Widersprüchliche Bemaßung",
                bezeichnung="Die gleiche Strecke ist an verschiedenen Stellen unterschiedlich bemasst.",
                warum="Widersprüchliche Bemaßungen führen zu Unsicherheit bei der Ausfuehrung. "
                     "Der Polier weiß nicht, welches Maß korrekt ist. Dies kann zu "
                     "Rueckbau und Mehrkosten fuehren.",
                loesung="Die Bemaßungen müssen auf Plausibilität geprüft werden. "
                       "Dazu werden die Maße im Grundriss und Schnitt verglichen. "
                       "Das korrekte Maß wird bestimmt und alle widersprüchlichen "
                       "Bemaßungen werden angepasst.",
                norm="OIB-RL 1 (Tragwerk - eindeutige Maße erforderlich)",
                beispiel="Außenwand im Grundriss: 10.000mm, im Schnitt: 10.050mm → "
                        "50mm Unterschied! Im Zweifel wird das größere Maß verwendet.",
                schwere="KRITISCH",
                confidence=0.98,
            ),
            "BEM_MASSSTAB": FehlerErklaerung(
                name="Maßstab-Fehler",
                bezeichnung="Die gezeichnete Länge entspricht nicht dem angegebenen Maßstab.",
                warum="Ein Maßstab-Fehler bedeutet, dass der Plan nicht im richtigen "
                     "Verhältnis gezeichnet wurde. Dies führt dazu, dass Maße mit "
                     "dem Maßstab abgegriffen werden können und Falschwerte ergeben.",
                loesung="Entweder die Zeichnung muss im richtigen Maßstab erstellt werden, "
                       "oder die Bemaßung muss explizit angegeben werden (was immer zu "
                       "bevorzugen ist). Bei digitalen Plänen: Plot-Scale prüfen.",
                norm="OeNORM A 1160 (Plangestaltung - Maßstäbe 1:100, 1:50)",
                beispiel="Maßstab 1:50 angegeben, aber gezeichnete Wand = 70mm × 50 = 3500mm, "
                        "bemassst = 35mm → Faktor 100 statt 50 verwendet!",
                schwere="HOCH",
                confidence=0.94,
            ),
            # ===================================================================
            # PLANFEHLER
            # ===================================================================
            "PLAN_RAUM_FLAECHE": FehlerErklaerung(
                name="Raum zu klein",
                bezeichnung="Der Raum ist kleiner als die Mindestfläche für Aufenthaltsräume.",
                warum="Zu kleine Räume sind ungesund und unpraktisch. Die "
                     "österreichische Bauordnung fordert Mindestflächen für "
                     "Aufenthaltsräume, um die Nutzbarkeit zu gewährleisten.",
                loesung="Die Raumfläche muss durch Vergrößern der Außenwände "
                       "oder Entfernen von Trennwänden erhöht werden. "
                       "Alternativ: Raum als Abstellraum deklarieren.",
                norm="OIB-RL 3 (Aufenthaltsräume >= 10 m2)",
                beispiel="Kinderzimmer: 8.0 m2 < 10 m2 Mindestfläche → Raum vergrößern "
                        "oder als Abstellraum deklarieren.",
                schwere="HOCH",
                confidence=0.96,
            ),
            "PLAN_RAUM_HOEHE": FehlerErklaerung(
                name="Raum zu niedrig",
                bezeichnung="Die Raumhöhe ist niedriger als die Mindesthöhe.",
                warum="Zu niedrige Räume beeinträchtigen die Gesundheit (Luftqualität) "
                     "und die Nutzbarkeit. Dies kann auch baurechtliche Konsequenzen haben.",
                loesung="Die Raumhöhe muss durch Absenken der Decke "
                       "oder Entfernen von Unterzügen erhöht werden.",
                norm="OIB-RL 3 (Raumhöhe >= 2,50 m; Ausnahmen 2,30 m)",
                beispiel="Keller: 2.4m < 2.50m Mindesthöhe → Decke absenken "
                        "oder als Technikraum deklarieren.",
                schwere="HOCH",
                confidence=0.95,
            ),
            "PLAN_RAUM_TAGESLICHT": FehlerErklaerung(
                name="Ungenügend Tageslicht",
                bezeichnung="Der Fensteranteil ist geringer als 10% der Raumfläche.",
                warum="Zu wenig Tageslicht beeinträchtigt die Gesundheit "
                     "und die Lebensqualität. Außerdem können so "
                     "Räume nicht als Aufenthaltsräume genutzt werden.",
                loesung="Fensterfläche vergrößern, "
                       "Oberlichter hinzufügen oder "
                       "Raum als Abstellraum deklarieren.",
                norm="OIB-RL 3 (Tageslichtquote >= 10%)",
                beispiel="Flur: 5% Fensteranteil < 10% → Oberlicht "
                        "installieren oder als Durchgangsraum deklarieren.",
                schwere="MITTEL",
                confidence=0.93,
            ),
            "PLAN_FLUCHTWEG_BREITE": FehlerErklaerung(
                name="Fluchtweg zu schmal",
                bezeichnung="Die Fluchtwegbreite ist geringer als 1.20 m.",
                warum="Zu schmale Fluchtwege gefährden die Sicherheit "
                     "bei einem Brand. Rettungskräfte können nicht "
                     "passieren, Panik kann entstehen.",
                loesung="Fluchtwegbreite auf mindestens 1.20 m vergrößern. "
                       "Dazu muss die Wand zurückversetzt werden.",
                norm="OIB-RL 2 (Fluchtwege >= 1.20 m; >= 1.00m fuer max 20 Personen)",
                beispiel="Hauptfluchtweg: 1.0m < 1.20m → Wand um 20cm versetzen "
                        "oder zweiten Ausgang erstellen.",
                schwere="KRITISCH",
                confidence=0.98,
            ),
            "PLAN_FLUCHTWEG_LAENGE": FehlerErklaerung(
                name="Fluchtweg zu lang",
                bezeichnung="Der Fluchtweg ist laenger als 25 m.",
                warum="Zu lange Fluchtwege gefaehrden die Flucht "
                     "bei einem Brand. Personen koennen sich "
                     "verlaufen oder durch Rauch eingeschlossen werden.",
                loesung="Einen zweiten Ausgang erstellen "
                       "oder den Fluchtweg durch Feuerwiderstand "
                       "schuetzen (z.B. Rauchschutztueren).",
                norm="OIB-RL 2 (Fluchtwege <= 25m)",
                beispiel="Fluchtweg: 30m > 25m → zweiten Ausgang "
                        "erstellen oder Fluchtweg verkuermen.",
                schwere="KRITISCH",
                confidence=0.97,
            ),
            "PLAN_TREPPE_STUFENHOEHE": FehlerErklaerung(
                name="Treppenstufe zu hoch",
                bezeichnung="Die Stufenhoehe ist groesser als 19 cm.",
                warum="Zu hohe Treppenstufen erschweren das Steigen "
                     "und erhoeen das Sturzrisiko. Dies ist besonders "
                     "fuer aeltere Personen gefaehrlich.",
                loesung="Stufenhoehe auf max 19 cm reduzieren. "
                       "Dazu muessen mehr Stufen eingebaut oder "
                       "die Geschosshoehe veraendert werden.",
                norm="OIB-RL 4 (Treppen: Stufenhoehe <= 19 cm)",
                beispiel="Treppe: 20cm > 19cm → eine zusaetzliche "
                        "Stufe einbauen (19cm pro Stufe).",
                schwere="HOCH",
                confidence=0.96,
            ),
            "PLAN_TREPPE_STUFENTIEFE": FehlerErklaerung(
                name="Treppenstufe zu schmal",
                bezeichnung="Die Stufentiefe ist geringer als 26 cm.",
                warum="Zu schmale Treppenstufen erschweren das sichere "
                     "Treten und erhoeen das Sturzrisiko.",
                loesung="Stufentiefe auf mind 26 cm vergroessern. "
                       "Dazu muss die Treppe laenger werden.",
                norm="OIB-RL 4 (Treppen: Stufentiefe >= 26 cm)",
                beispiel="Treppe: 25cm < 26cm → Treppe um 10cm "
                        "verlaengern.",
                schwere="HOCH",
                confidence=0.95,
            ),
            "PLAN_KOLLISION": FehlerErklaerung(
                name="Kollision",
                bezeichnung="Zwei Bauteile ueberschneiden sich (z.B. Rohr durch Brandwand).",
                warum="Kollisionen bedeuten, dass Bauteile nicht wie geplant "
                     "ausgefuehrt werden koennen. Bei Brandwaenden besonders "
                     "kritisch: Brandschutzschott erforderlich!",
                loesung="Bauteile verschieben oder Brandschutzschott EI90 "
                       "einplanen. Bei Rohr durch Brandwand: Schott mit "
                       "gleicher Feuerwiderstandsklasse wie Wand.",
                norm="OIB-RL 2 (Brandwaende muessen intakt bleiben)",
                beispiel="Rohr DN100 durch Brandwand REI90 → "
                        "Brandschutzschott EI90 erforderlich!",
                schwere="KRITISCH",
                confidence=0.94,
            ),
            # ===================================================================
            # PLANUNGSFEHLER
            # ===================================================================
            "PLANUNG_VOLL": FehlerErklaerung(
                name="Vollstaendigkeitsfehler",
                bezeichnung="Ein erforderlicher Planbestandteil fehlt.",
                warum="Fehlende Planbestandteile fuehren zu Unsicherheit "
                     "bei der Ausfuehrung. Der Polier muss nachfragen "
                     "oder annahmen treffen, was zu Fehlern fuehren kann.",
                loesung="Den fehlenden Planbestandteil nachtragen. "
                       "Grundsaetzlich muessen alle Plaene vollstaendig sein.",
                norm="OeNORM A 1160 (Planinhalt)",
                beispiel="Schnitte fehlen → Schnitt wird nicht ausfuehrbar geplant.",
                schwere="HOCH",
                confidence=0.95,
            ),
            "PLANUNG_KONSISTENZ": FehlerErklaerung(
                name="Konsistenzfehler",
                bezeichnung="Widersprueche zwischen verschiedenen Plaenen "
                          "(z.B. Grundriss vs Schnitt).",
                warum="Konsistenzfehler zeigen, dass die Plaene nicht "
                     "aufeinander abgestimmt wurden. Dies fuehrt zu "
                     "Unsicherheit und moeglichen Fehlern.",
                loesung="Alle Flaechenangaben muessen abgeglichen "
                       "und angeglichen werden.",
                norm="OeNORM A 1160 (Plan-Konsistenz)",
                beispiel="Grundriss: 80m2, Schnitt: 85m2 → "
                        "5m2 Differenz! Flaechen abgleichen.",
                schwere="HOCH",
                confidence=0.96,
            ),
            "PLANUNG_AUSFUEHRUNG": FehlerErklaerung(
                name="Ausfuehrungsfehler",
                bezeichnung="Material-Spezifikation fehlt oder ist unvollstaendig.",
                warum="Ohne Spezifikation kann das Material nicht eindeutig "
                     "bestimmt werden. Dies fuehrt zu Unsicherheit "
                     "und moeglichen Fehlern bei der Beschaffung.",
                loesung="Die Spezifikation muss nachgetragen werden. "
                       "Z.B. Beton: C25/30, Ziegel: Hochloch Z12, etc.",
                norm="OeNORM A 1160 (Materialangabe)",
                beispiel="Holz ohne Spezifikation → KVH oder BSH? "
                        "Welche Guete? Nachtragen!",
                schwere="MITTEL",
                confidence=0.90,
            ),
            # ===================================================================
            # ABWEICHUNGEN
            # ===================================================================
            "ABW_OIB_HWB": FehlerErklaerung(
                name="HWB ueberschritten",
                bezeichnung="Der Heizwaermebedarf ueberschreitet den Grenzwert.",
                warum="Ein zu hoher HWB bedeutet einen zu hohen Energieverbrauch. "
                     "Dies fuehrt zu hohen Heizkosten und verstoesst "
                     "gegen die Energieeinsparverordnung.",
                loesung="Daemmung verbessern, Fenster mit niedrigerem U-Wert "
                       "waehlen, Lueftungsanlage mit Waermerueckgewinnung einbauen.",
                norm="OIB-RL 6 (HWB <= 75 kWh/m2a)",
                beispiel="HWB: 80 kWh/m2a > 75 kWh/m2a → "
                        "Daemmung von 16cm auf 20cm erhoehen.",
                schwere="HOCH",
                confidence=0.97,
            ),
            "ABW_OIB_FGEE": FehlerErklaerung(
                name="fGEE ueberschritten",
                bezeichnung="Der Faktor der gewichteten Energieeffizienz "
                          "ueberschreitet den Grenzwert.",
                warum="Ein zu hoher fGEE bedeutet eine schlechte Gesamtenergieeffizienz.",
                loesung="Gebauelehtdichtheit verbessern, Haustechnik optimieren, "
                       "erneuerbare Energien einbinden.",
                norm="OIB-RL 6 (fGEE <= 0.75)",
                beispiel="fGEE: 0.80 > 0.75 → Lueftungsanlage mit WRG einbauen.",
                schwere="HOCH",
                confidence=0.95,
            ),
            "ABW_BL_ABSTAND": FehlerErklaerung(
                name="Abstandsflaeche unterschritten",
                bezeichnung="Der Abstand zum Nachbargrundstueck "
                          "ist zu gering.",
                warum="Zu geringe Abstandsflaechen fuehren zu "
                     "Rechtsstreitigkeiten mit Nachbarn und "
                     "koennen baurechtliche Konsequenzen haben.",
                loesung="Abstand vergrößern oder "
                       "Einverstaendnis des Nachbarn einholen.",
                norm="Bauordnung des Bundeslandes (z.B. Bgld. 3.5m)",
                beispiel="Abstand: 3.0m < 3.5m → "
                        "Wand um 50cm versetzen.",
                schwere="HOCH",
                confidence=0.96,
            ),
            "ABW_KOORDINATEN": FehlerErklaerung(
                name="Koordinaten unplausibel",
                bezeichnung="Die Koordinaten liegen außerhalb von Österreich.",
                warum="Unplausible Koordinaten deuten auf ein falsch "
                     "gewaehltes Bezugssystem hin. Dies fuehrt zu "
                     "Fehlern bei der Ausmessung und dem Bau.",
                loesung="Koordinatensystem auf M31/M34 pruefen. "
                       "Rechtswerte in Oesterreich: 300000-700000.",
                norm="BEV (Bundesamt fuer Eich- und Vermessungswesen)",
                beispiel="Rechtswert: 800000 (M34 waere 300000-700000) → "
                        "System pruefen!",
                schwere="HOCH",
                confidence=0.98,
            ),
            "ABW_LAST_SCHNEE": FehlerErklaerung(
                name="Schneelast falsch",
                bezeichnung="Die Schneelast ist fuer den Standort falsch angesetzt.",
                warum="Eine falsche Schneelast gefaehrdet die Standsicherheit "
                     "des Dachs. Zu wenig Schnee → Dach kann "
                     "einstuerzen. Zu viel → unwirtschaftlich.",
                loesung="Korrekte Schneelast aus "
                       "EN 1991-1-3 fuer den Standort ermitteln.",
                norm="EN 1991-1-3 / OIB-RL 1",
                beispiel="Burgenland: 0.8 kN/m2 statt 1.12 kN/m2 → "
                        "0.32 kN/m2 zu wenig! Dachtraeger unterdimensioniert!",
                schwere="KRITISCH",
                confidence=0.97,
            ),
            "ABW_LAST_WIND": FehlerErklaerung(
                name="Windlast falsch",
                bezeichnung="Die Windlast ist fuer den Standort falsch angesetzt.",
                warum="Eine falsche Windlast gefaehrdet die Stabilitaet "
                     "bei Sturm. Gebaeude kann Schaden nehmen.",
                loesung="Korrekte Windlast aus "
                       "EN 1991-1-4 fuer den Standort ermitteln.",
                norm="EN 1991-1-4 / OIB-RL 1",
                beispiel="Oesterreich: 0.85 kN/m2 statt 0.65 kN/m2 → "
                        "0.20 kN/m2 zu viel! Aber besser zu viel als zu wenig.",
                schwere="HOCH",
                confidence=0.94,
            ),
            "ABW_U_WAND": FehlerErklaerung(
                name="U-Wand zu hoch",
                bezeichnung="Der U-Wert der Wand ueberschreitet den Grenzwert.",
                warum="Ein zu hoher U-Wert bedeutet zu hohen Waermeverlust "
                     "und damit hohe Heizkosten.",
                loesung="Daemmung veraendern. "
                       "Berechnung: U-Wand = 1/(Ri + R1 + R2 + ... + Ra)",
                norm="OIB-RL 6 (U-Wand <= 0.22 W/m2K)",
                beispiel="U-Wand: 0.25 > 0.22 W/m2K → "
                        "WDWS von 16cm auf 18cm erhoehen.",
                schwere="HOCH",
                confidence=0.95,
            ),
        }

    def get_erklarung(self, fehler_id: str) -> Optional[FehlerErklaerung]:
        """Hole Erklaerung fuer Fehler-ID."""
        # Basis-ID extrahieren
        base_id = fehler_id.split("_")[0] if "_" in fehler_id else fehler_id
        if base_id == "BEM":
            return self.fehler_katalog.get("BEM_FEHLEND")
        elif base_id == "PLAN" and "RAUM" in fehler_id:
            if "FLAECHE" in fehler_id:
                return self.fehler_katalog.get("PLAN_RAUM_FLAECHE")
            elif "HOEHE" in fehler_id:
                return self.fehler_katalog.get("PLAN_RAUM_HOEHE")
            elif "TAGESLICHT" in fehler_id:
                return self.fehler_katalog.get("PLAN_RAUM_TAGESLICHT")
        elif base_id == "PLAN" and "FLUCHTWEG" in fehler_id:
            if "BREITE" in fehler_id:
                return self.fehler_katalog.get("PLAN_FLUCHTWEG_BREITE")
            elif "LAENGE" in fehler_id:
                return self.fehler_katalog.get("PLAN_FLUCHTWEG_LAENGE")
        elif base_id == "PLAN" and "TREPPE" in fehler_id:
            if "STUFENHOEHE" in fehler_id:
                return self.fehler_katalog.get("PLAN_TREPPE_STUFENHOEHE")
            elif "STUFENTIEFE" in fehler_id:
                return self.fehler_katalog.get("PLAN_TREPPE_STUFENTIEFE")
        elif base_id == "PLAN" and "KOLLISION" in fehler_id:
            return self.fehler_katalog.get("PLAN_KOLLISION")
        elif base_id == "PLANUNG" and "VOLL" in fehler_id:
            return self.fehler_katalog.get("PLANUNG_VOLL")
        elif base_id == "PLANUNG" and "KONSISTENZ" in fehler_id:
            return self.fehler_katalog.get("PLANUNG_KONSISTENZ")
        elif base_id == "PLANUNG" and "AUSFUEHRUNG" in fehler_id:
            return self.fehler_katalog.get("PLANUNG_AUSFUEHRUNG")
        elif base_id == "ABW":
            if "HWB" in fehler_id:
                return self.fehler_katalog.get("ABW_OIB_HWB")
            elif "FGEE" in fehler_id:
                return self.fehler_katalog.get("ABW_OIB_FGEE")
            elif "ABSTAND" in fehler_id:
                return self.fehler_katalog.get("ABW_BL_ABSTAND")
            elif "KOORDINATEN" in fehler_id:
                return self.fehler_katalog.get("ABW_KOORDINATEN")
            elif "SCHNEE" in fehler_id:
                return self.fehler_katalog.get("ABW_LAST_SCHNEE")
            elif "WIND" in fehler_id:
                return self.fehler_katalog.get("ABW_LAST_WIND")
            elif "U_WAND" in fehler_id:
                return self.fehler_katalog.get("ABW_U_WAND")
        return None


# ============================================================================
# WHITE-BOX FEHLERERKLAERUNGS-SYSTEM
# ============================================================================

class WhiteBoxFehlererklaerung:
    """White-Box Fehlererklaerungs-System."""

    def __init__(self):
        self.datenbank = FehlerDatenbank()
        self.des_system = DeterministicEpistemicSystem("White-Box-Fehlererklaerung")

    def erklaere_fehler(self, fehler_liste: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Erklaere Fehler mit White-Box-Methode."""
        erklaerungen = []
        for fehler in fehler_liste:
            fehler_id = fehler.get("id", "")
            erklarung = self.datenbank.get_erklarung(fehler_id)

            if erklarung:
                erklaerung_dict = {
                    "fehler_id": fehler_id,
                    "name": erklarung.name,
                    "bezeichnung": erklarung.bezeichnung,
                    "warum": erklarung.warum,
                    "loesung": erklarung.loesung,
                    "norm": erklarung.norm,
                    "beispiel": erklarung.beispiel,
                    "schwere": fehler.get("schwere", erklarung.schwere),
                    "confidence": fehler.get("confidence", erklarung.confidence),
                    "plan_kontext": fehler.get("beschreibung", ""),
                }
                erklaerungen.append(erklaerung_dict)
            else:
                # Generic Erklaerung wenn keine spezifische gefunden
                erklaerung_dict = {
                    "fehler_id": fehler_id,
                    "name": fehler.get("typ", "Unbekannt"),
                    "bezeichnung": fehler.get("beschreibung", ""),
                    "warum": "Diese Fehlerkategorie ist noch nicht im White-Box-Katalog hinterlegt.",
                    "loesung": "Bitte prüfen Sie die entsprechende Norm/Regel.",
                    "norm": "",
                    "beispiel": "",
                    "schwere": fehler.get("schwere", "MITTEL"),
                    "confidence": fehler.get("confidence", 0.5),
                    "plan_kontext": fehler.get("beschreibung", ""),
                }
                erklaerungen.append(erklaerung_dict)

        return erklaerungen


# ============================================================================
# HAUPTPROGRAMM
# ============================================================================

def main():
    print("=" * 100)
    print("WHITE-BOX FEHLERERKLAERUNG: Keine Black Box mehr!")
    print("Jeder Fehler mit Name, Bezeichnung, Warum, Loesung, Norm, Beispiel")
    print("=" * 100)

    white_box = WhiteBoxFehlererklaerung()

    # Importiere existierende Fehler
    from src.test_fehlererkennungs_system import generiere_test_plan_mit_fehlern, FehlererkennungsSystem

    system = FehlererkennungsSystem()
    alle_fehler = []
    for geschoss in ["UG", "EG", "OG", "DG"]:
        plan_daten = generiere_test_plan_mit_fehlern(geschoss)
        ergebnis = system.analysiere(plan_daten, geschoss)
        alle_fehler.extend(ergebnis["fehler"])

    print(f"\n  Gefundene Fehler: {len(alle_fehler)}")
    print(f"  {'=' * 60}")

    # White-Box Erklaerungen
    erklaerungen = white_box.erklaere_fehler(alle_fehler)

    # Ausgabe
    print("\n" + "=" * 100)
    print("WHITE-BOX FEHLERERKLAERUNGEN")
    print("=" * 100)

    for i, erk in enumerate(erklaerungen, 1):
        print(f"\n  FEHLER {i}: {erk['fehler_id']}")
        print(f"  {'=' * 80}")
        print(f"  NAME:        {erk['name']}")
        print(f"  BEZEICHNUNG: {erk['bezeichnung']}")
        print(f"  WARUM:       {erk['warum']}")
        print(f"  LOESUNG:     {erk['loesung']}")
        print(f"  NORM:        {erk['norm']}")
        print(f"  BEISPIEL:    {erk['beispiel']}")
        print(f"  SCHWERE:     {erk['schwere']}")
        print(f"  CONFIDENCE:  {erk['confidence']:.2f}")

    # JSON-Export
    report_path = os.path.join(os.path.dirname(__file__), "..", "white_box_fehlererklaerung_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(erklaerungen, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nReport gespeichert: {report_path}")

    print("\n" + "=" * 100)
    print("WHITE-BOX FEHLERERKLAERUNG: KEINE BLACK BOX MEHR!")
    print("=" * 100)


if __name__ == "__main__":
    main()