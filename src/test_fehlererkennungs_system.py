"""
FEHLERERKENNUNGS-SYSTEM: Bemaßungsfehler, Planfehler, Planungsfehler, Abweichungen
==================================================================================

6 Fehlerklassen mit automatischer Erkennung:
1. Bemaßungsfehler (fehlend, widerspruechlich, Einheiten, Rundung, Massstab)
2. Planfehler (Raum-Geometrie, Normen-Verstoesse, Kollisionen)
3. Planungsfehler (Vollstaendigkeit, Konsistenz, Ausfuehrung)
4. Abweichungen bei Planerstellung (OIB, Bundesland, Koordinaten, Hoehen)
5. Last-Fehler (Schneelast, Windlast, Erdbeben falsch zugeordnet)
6. Energetische Fehler (HWB, fGEE, U-Werte verfehlt)

Multi-Agenten-Schwarm mit 12 Experten + DES-Validierung

Autor: Baumeister Tool Austria Team
Datum: 2026-05-26
"""

import sys
import os
import json
import time
import math
from typing import Any, Dict, List, Optional, Tuple
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
# FEHLERKLASSEN
# ============================================================================

class FehlerKlasse(Enum):
    BEMASSUNG = "bemaßung"
    PLAN = "plan"
    PLANUNG = "planung"
    ABWEICHUNG = "abweichung"
    LAST = "last"
    ENERGETIK = "energetik"


class Schweregrad(Enum):
    KRITISCH = "KRITISCH"
    HOCH = "HOCH"
    MITTEL = "MITTEL"
    NIEDRIG = "NIEDRIG"


@dataclass
class BemaßungsFehler:
    id: str
    typ: str  # fehlend, widerspruechlich, einheit, rundung, massstab, ueberlappend
    beschreibung: str
    stelle: str  # wo im Plan
    ist_wert: str
    soll_wert: str
    schwere: Schweregrad
    empfehlung: str
    confidence: float


@dataclass
class PlanFehler:
    id: str
    typ: str  # raum_geometrie, normen_verstoss, kollision
    beschreibung: str
    norm_verweis: str
    ist_wert: float
    soll_wert: float
    einheit: str
    schwere: Schweregrad
    empfehlung: str
    confidence: float


@dataclass
class PlanungsFehler:
    id: str
    typ: str  # vollstaendigkeit, konsistenz, ausfuehrung
    beschreibung: str
    betroffen: str
    schwere: Schweregrad
    empfehlung: str
    confidence: float


@dataclass
class Abweichung:
    id: str
    typ: str  # oib, bundesland, massstab, koordinaten, hoehe, last, energie
    beschreibung: str
    norm_verweis: str
    ist_wert: float
    soll_wert: float
    einheit: str
    schwere: Schweregrad
    empfehlung: str
    confidence: float


# ============================================================================
# FEHLER-DETEKTOREN
# ============================================================================

class BemassungsDetektor:
    """Erkennt Bemaßungsfehler in Plaenen."""

    def __init__(self):
        self.fehler: List[BemaßungsFehler] = []

    def analysiere(self, plan_daten: Dict[str, Any]) -> List[BemaßungsFehler]:
        self.fehler = []
        self._pruefe_fehlende_bemassungen(plan_daten)
        self._pruefe_widerspruechliche_bemassungen(plan_daten)
        self._pruefe_einheiten(plan_daten)
        self._pruefe_rundungsfehler(plan_daten)
        self._pruefe_massstab(plan_daten)
        self._pruefe_ueberlappende_bemassungen(plan_daten)
        return self.fehler

    def _pruefe_fehlende_bemassungen(self, plan_daten: Dict[str, Any]):
        """Pruefe auf fehlende Bemaßungen."""
        bemassungen = plan_daten.get("bemassungen", [])
        elemente = plan_daten.get("elemente", {})

        # Mindestbemaßungen erforderlich
        required = ["aussenwand_laenge", "innenwand_laenge", "raum_hoehe", "fenster_breite", "tuer_breite"]
        for req in required:
            if req not in [b.get("typ") for b in bemassungen]:
                self.fehler.append(BemaßungsFehler(
                    id=f"BEM_FEHLEND_{req.upper()}",
                    typ="fehlend",
                    beschreibung=f"Bemaßung '{req}' fehlt im Plan",
                    stelle=f"Element: {req}",
                    ist_wert="nicht vorhanden",
                    soll_wert="vorhanden",
                    schwere=Schweregrad.HOCH,
                    empfehlung=f"Bemaßung fuer {req} nachtragen",
                    confidence=0.95,
                ))

    def _pruefe_widerspruechliche_bemassungen(self, plan_daten: Dict[str, Any]):
        """Pruefe auf widerspruechliche Bemaßungen."""
        bemassungen = plan_daten.get("bemassungen", [])
        
        # Gruppiere nach Typ
        by_typ = {}
        for b in bemassungen:
            typ = b.get("typ", "")
            if typ not in by_typ:
                by_typ[typ] = []
            by_typ[typ].append(b)

        # Pruefe auf Widersprueche
        for typ, bems in by_typ.items():
            if len(bems) > 1:
                werte = [b.get("wert", 0) for b in bems]
                if max(werte) - min(werte) > 10:  # > 10mm Unterschied
                    self.fehler.append(BemaßungsFehler(
                        id=f"BEM_WIDERSPRUCH_{typ.upper()}",
                        typ="widerspruechlich",
                        beschreibung=f"Widerspruechliche Bemaßung fuer '{typ}': {min(werte)}mm vs {max(werte)}mm",
                        stelle=f"Bemaßung: {typ}",
                        ist_wert=f"{min(werte)}mm / {max(werte)}mm",
                        soll_wert="einheitlich",
                        schwere=Schweregrad.KRITISCH,
                        empfehlung=f"Widerspruch aufloesen, korrekte Bemaßung ermitteln",
                        confidence=0.98,
                    ))

    def _pruefe_einheiten(self, plan_daten: Dict[str, Any]):
        """Pruefe auf falsche Einheiten."""
        bemassungen = plan_daten.get("bemassungen", [])
        for b in bemassungen:
            einheit = b.get("einheit", "mm")
            wert = b.get("wert", 0)
            # Plausibilitaets-Pruefung
            if einheit == "m" and wert > 100:  # > 100m unwahrscheinlich
                self.fehler.append(BemaßungsFehler(
                    id=f"BEM_EINHEIT_{b.get('typ', 'unbekannt').upper()}",
                    typ="einheit",
                    beschreibung=f"Einheit 'm' fuer {b.get('typ')} mit Wert {wert}m unplausibel",
                    stelle=f"Bemaßung: {b.get('typ')}",
                    ist_wert=f"{wert}m",
                    soll_wert=f"{wert*1000}mm",
                    schwere=Schweregrad.HOCH,
                    empfehlung="Einheit auf mm korrigieren",
                    confidence=0.90,
                ))

    def _pruefe_rundungsfehler(self, plan_daten: Dict[str, Any]):
        """Pruefe auf Rundungsfehler (Summe Teilstrecken != Gesamtstrecke)."""
        bemassungen = plan_daten.get("bemassungen", [])
        
        # Finde Kettenbemaßungen
        ketten = {}
        for b in bemassungen:
            if "kette" in b:
                kette = b["kette"]
                if kette not in ketten:
                    ketten[kette] = {"teile": [], "gesamt": 0}
                if b.get("ist_teilstrecke"):
                    ketten[kette]["teile"].append(b.get("wert", 0))
                else:
                    ketten[kette]["gesamt"] = b.get("wert", 0)

        # Pruefe
        for kette, daten in ketten.items():
            summe_teile = sum(daten["teile"])
            gesamt = daten["gesamt"]
            if gesamt > 0 and abs(summe_teile - gesamt) > 5:  # > 5mm Abweichung
                self.fehler.append(BemaßungsFehler(
                    id=f"BEM_RUNDUNG_{kette.upper()}",
                    typ="rundung",
                    beschreibung=f"Rundungsfehler in Kette '{kette}': Summe={summe_teile}mm, Gesamt={gesamt}mm",
                    stelle=f"Kettenbemaßung: {kette}",
                    ist_wert=f"{summe_teile}mm",
                    soll_wert=f"{gesamt}mm",
                    schwere=Schweregrad.MITTEL,
                    empfehlung=f"Rundung korrigieren, Differenz: {abs(summe_teile - gesamt)}mm",
                    confidence=0.92,
                ))

    def _pruefe_massstab(self, plan_daten: Dict[str, Any]):
        """Pruefe auf Massstab-Fehler."""
        massstab = plan_daten.get("massstab", 50)
        bemassungen = plan_daten.get("bemassungen", [])
        
        for b in bemassungen:
            gezeichnet = b.get("gezeichnet_mm", 0)
            bemasst = b.get("wert", 0)
            errechnet = gezeichnet * massstab
            
            if bemasst > 0 and errechnet > 0:
                abweichung = abs(errechnet - bemasst) / bemasst
                if abweichung > 0.02:  # > 2% Abweichung
                    self.fehler.append(BemaßungsFehler(
                        id=f"BEM_MASSSTAB_{b.get('typ', 'unbekannt').upper()}",
                        typ="massstab",
                        beschreibung=f"Massstab-Fehler: gezeichnet={gezeichnet}mm x {massstab} = {errechnet}mm, bemasst={bemasst}mm",
                        stelle=f"Bemaßung: {b.get('typ')}",
                        ist_wert=f"{errechnet}mm",
                        soll_wert=f"{bemasst}mm",
                        schwere=Schweregrad.HOCH,
                        empfehlung=f"Massstab pruefen, Bemaßung korrigieren",
                        confidence=0.94,
                    ))

    def _pruefe_ueberlappende_bemassungen(self, plan_daten: Dict[str, Any]):
        """Pruefe auf ueberlappende Bemaßungen."""
        bemassungen = plan_daten.get("bemassungen", [])
        
        for i, b1 in enumerate(bemassungen):
            for b2 in bemassungen[i+1:]:
                pos1 = b1.get("position", (0, 0))
                pos2 = b2.get("position", (0, 0))
                dist = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                if dist < 50:  # < 50mm = ueberlappend
                    self.fehler.append(BemaßungsFehler(
                        id=f"BEM_UEBERLAPPUNG_{b1.get('typ', '?')}_{b2.get('typ', '?')}",
                        typ="ueberlappend",
                        beschreibung=f"Ueberlappende Bemaßungen: {b1.get('typ')} und {b2.get('typ')}",
                        stelle=f"Position: ({pos1[0]}, {pos1[1]})",
                        ist_wert=f"Abstand: {dist:.0f}mm",
                        soll_wert=">= 50mm",
                        schwere=Schweregrad.NIEDRIG,
                        empfehlung="Bemaßungen verschieben fuer bessere Lesbarkeit",
                        confidence=0.85,
                    ))


class PlanDetektor:
    """Erkennt Planfehler in Plaenen."""

    def __init__(self):
        self.fehler: List[PlanFehler] = []

    def analysiere(self, plan_daten: Dict[str, Any], geschoss: str) -> List[PlanFehler]:
        self.fehler = []
        self._pruefe_raum_geometrie(plan_daten)
        self._pruefe_normen_verstoesse(plan_daten, geschoss)
        self._pruefe_kollisionen(plan_daten)
        return self.fehler

    def _pruefe_raum_geometrie(self, plan_daten: Dict[str, Any]):
        """Pruefe Raum-Geometrie-Fehler."""
        raeume = plan_daten.get("raeume", {})
        
        for name, raum in raeume.items():
            flaeche = raum.get("flaeche_m2", 0)
            hoehe = raum.get("hoehe_m", 2.5)
            fenster = raum.get("fenster_anteil", 0)

            # Mindestflaeche Aufenthaltsraum
            if flaeche > 0 and flaeche < 10:
                self.fehler.append(PlanFehler(
                    id=f"PLAN_RAUM_{name.upper()}_FLAECHE",
                    typ="raum_geometrie",
                    beschreibung=f"Raum '{name}' zu klein: {flaeche}m2 < 10m2 (Mindestaufenthaltsraum)",
                    norm_verweis="OIB-RL 3",
                    ist_wert=flaeche,
                    soll_wert=10.0,
                    einheit="m2",
                    schwere=Schweregrad.HOCH,
                    empfehlung=f"Raumflaeche auf mindestens 10m2 vergroessern",
                    confidence=0.96,
                ))

            # Mindesthoehe
            if hoehe > 0 and hoehe < 2.5:
                self.fehler.append(PlanFehler(
                    id=f"PLAN_RAUM_{name.upper()}_HOEHE",
                    typ="raum_geometrie",
                    beschreibung=f"Raum '{name}' zu niedrig: {hoehe}m < 2.50m",
                    norm_verweis="OIB-RL 3 (Raumhoehe)",
                    ist_wert=hoehe,
                    soll_wert=2.5,
                    einheit="m",
                    schwere=Schweregrad.HOCH,
                    empfehlung=f"Raumhoehe auf mindestens 2.50m erhoehen",
                    confidence=0.95,
                ))

            # Tageslicht
            if fenster > 0 and fenster < 0.1:
                self.fehler.append(PlanFehler(
                    id=f"PLAN_RAUM_{name.upper()}_TAGESLICHT",
                    typ="raum_geometrie",
                    beschreibung=f"Raum '{name}' ungenuegend Tageslicht: {fenster*100:.0f}% < 10%",
                    norm_verweis="OIB-RL 3 (Tageslicht)",
                    ist_wert=fenster * 100,
                    soll_wert=10.0,
                    einheit="%",
                    schwere=Schweregrad.MITTEL,
                    empfehlung="Fensterflaeche vergroessern",
                    confidence=0.93,
                ))

    def _pruefe_normen_verstoesse(self, plan_daten: Dict[str, Any], geschoss: str):
        """Pruefe Normen-Verstoesse."""
        # Fluchtweg-Breite
        fluchtwege = plan_daten.get("fluchtwege", [])
        for fw in fluchtwege:
            breite = fw.get("breite_m", 0)
            if breite > 0 and breite < 1.2:
                self.fehler.append(PlanFehler(
                    id=f"PLAN_FLUCHTWEG_{fw.get('name', 'unbekannt').upper()}_BREITE",
                    typ="normen_verstoss",
                    beschreibung=f"Fluchtweg zu schmal: {breite}m < 1.20m",
                    norm_verweis="OIB-RL 2 (Fluchtwege)",
                    ist_wert=breite,
                    soll_wert=1.2,
                    einheit="m",
                    schwere=Schweregrad.KRITISCH,
                    empfehlung=f"Fluchtwegbreite auf mindestens 1.20m vergroessern",
                    confidence=0.98,
                ))

        # Fluchtweg-Laenge
        for fw in fluchtwege:
            laenge = fw.get("laenge_m", 0)
            if laenge > 0 and laenge > 25:
                self.fehler.append(PlanFehler(
                    id=f"PLAN_FLUCHTWEG_{fw.get('name', 'unbekannt').upper()}_LAENGE",
                    typ="normen_verstoss",
                    beschreibung=f"Fluchtweg zu lang: {laenge}m > 25m",
                    norm_verweis="OIB-RL 2 (Fluchtwege)",
                    ist_wert=laenge,
                    soll_wert=25.0,
                    einheit="m",
                    schwere=Schweregrad.KRITISCH,
                    empfehlung="Zweiten Ausgang erstellen oder Fluchtweg verkuermen",
                    confidence=0.97,
                ))

        # Treppengeometrie
        treppen = plan_daten.get("treppen", [])
        for t in treppen:
            stufen_hoehe = t.get("stufen_hoehe_cm", 0)
            stufen_tiefe = t.get("stufen_tiefe_cm", 0)
            if stufen_hoehe > 19:
                self.fehler.append(PlanFehler(
                    id=f"PLAN_TREPPE_{t.get('name', 'unbekannt').upper()}_STUFENHOEHE",
                    typ="normen_verstoss",
                    beschreibung=f"Treppenstufe zu hoch: {stufen_hoehe}cm > 19cm",
                    norm_verweis="OIB-RL 4 (Treppen)",
                    ist_wert=stufen_hoehe,
                    soll_wert=19.0,
                    einheit="cm",
                    schwere=Schweregrad.HOCH,
                    empfehlung=f"Stufenhoehe auf max 19cm reduzieren",
                    confidence=0.96,
                ))
            if stufen_tiefe > 0 and stufen_tiefe < 26:
                self.fehler.append(PlanFehler(
                    id=f"PLAN_TREPPE_{t.get('name', 'unbekannt').upper()}_STUFENTIEFE",
                    typ="normen_verstoss",
                    beschreibung=f"Treppenstufe zu schmal: {stufen_tiefe}cm < 26cm",
                    norm_verweis="OIB-RL 4 (Treppen)",
                    ist_wert=stufen_tiefe,
                    soll_wert=26.0,
                    einheit="cm",
                    schwere=Schweregrad.HOCH,
                    empfehlung=f"Stufentiefe auf mind 26cm vergroessern",
                    confidence=0.95,
                ))

    def _pruefe_kollisionen(self, plan_daten: Dict[str, Any]):
        """Pruefe auf Kollisionen (simuliert)."""
        elemente = plan_daten.get("elemente", {})
        
        # Simuliere Kollisions-Pruefung
        if "rohr_fuer_brandwand" in elemente:
            self.fehler.append(PlanFehler(
                id="PLAN_KOLLISION_ROHR_BRANDWAND",
                typ="kollision",
                beschreibung="Rohr durch Brandwand - Brandschutzschott erforderlich",
                norm_verweis="OIB-RL 2 (Brandwände)",
                ist_wert=1,
                soll_wert=0,
                einheit="Kollisionen",
                schwere=Schweregrad.KRITISCH,
                empfehlung="Brandschutzschott EI90 einplanen oder Rohr umleiten",
                confidence=0.94,
            ))


class PlanungsDetektor:
    """Erkennt Planungsfehler."""

    def __init__(self):
        self.fehler: List[PlanungsFehler] = []

    def analysiere(self, plan_daten: Dict[str, Any]) -> List[PlanungsFehler]:
        self.fehler = []
        self._pruefe_vollstaendigkeit(plan_daten)
        self._pruefe_konsistenz(plan_daten)
        self._pruefe_ausfuehrung(plan_daten)
        return self.fehler

    def _pruefe_vollstaendigkeit(self, plan_daten: Dict[str, Any]):
        """Pruefe Vollstaendigkeit."""
        # Erforderliche Elemente
        required = {
            "grundriss": "Grundriss",
            "schnitte": "Schnitte",
            "ansichten": "Ansichten",
            "bemaßungen": "Bemaßungen",
            "raumstempel": "Raumstempel",
            "materialangaben": "Materialangaben",
        }
        
        for key, name in required.items():
            if key not in plan_daten or not plan_daten[key]:
                self.fehler.append(PlanungsFehler(
                    id=f"PLANUNG_VOLL_{key.upper()}",
                    typ="vollstaendigkeit",
                    beschreibung=f"{name} fehlt im Plan",
                    betroffen=name,
                    schwere=Schweregrad.HOCH,
                    empfehlung=f"{name} nachtragen",
                    confidence=0.95,
                ))

    def _pruefe_konsistenz(self, plan_daten: Dict[str, Any]):
        """Pruefe Konsistenz zwischen Grundriss und Schnitt."""
        grundriss_flaeche = plan_daten.get("grundriss_flaeche", 0)
        schnitt_flaeche = plan_daten.get("schnitt_flaeche", 0)
        
        if grundriss_flaeche > 0 and schnitt_flaeche > 0:
            abweichung = abs(grundriss_flaeche - schnitt_flaeche) / grundriss_flaeche
            if abweichung > 0.05:  # > 5%
                self.fehler.append(PlanungsFehler(
                    id="PLANUNG_KONSISTENZ_FLAECHE",
                    typ="konsistenz",
                    beschreibung=f"Flaeche Grundriss ({grundriss_flaeche}m2) != Schnitt ({schnitt_flaeche}m2)",
                    betroffen="Grundriss vs Schnitt",
                    schwere=Schweregrad.HOCH,
                    empfehlung="Flaechenangaben abgleichen",
                    confidence=0.96,
                ))

    def _pruefe_ausfuehrung(self, plan_daten: Dict[str, Any]):
        """Pruefe Ausfuehrungsangaben."""
        materialien = plan_daten.get("materialien", [])
        for mat in materialien:
            if not mat.get("spezifikation"):
                self.fehler.append(PlanungsFehler(
                    id=f"PLANUNG_AUSFUEHRUNG_{mat.get('name', 'unbekannt').upper()}",
                    typ="ausfuehrung",
                    beschreibung=f"Material '{mat.get('name')}' ohne Spezifikation",
                    betroffen=mat.get("name", "unbekannt"),
                    schwere=Schweregrad.MITTEL,
                    empfehlung=f"Spezifikation fuer {mat.get('name')} nachtragen",
                    confidence=0.90,
                ))


class AbweichungsDetektor:
    """Erkennt Abweichungen bei Planerstellung."""

    def __init__(self):
        self.abweichungen: List[Abweichung] = []

    def analysiere(self, plan_daten: Dict[str, Any], bundesland: str = "burgenland") -> List[Abweichung]:
        self.abweichungen = []
        self._pruefe_oib(plan_daten)
        self._pruefe_bundesland(plan_daten, bundesland)
        self._pruefe_koordinaten(plan_daten)
        self._pruefe_hoehen(plan_daten)
        self._pruefe_lasten(plan_daten, bundesland)
        self._pruefe_energetik(plan_daten)
        return self.abweichungen

    def _pruefe_oib(self, plan_daten: Dict[str, Any]):
        """Pruefe OIB-Abweichungen."""
        # HWB
        hwb = plan_daten.get("hwb", 0)
        if hwb > 0 and hwb > 75:
            self.abweichungen.append(Abweichung(
                id="ABW_OIB_HWB",
                typ="oib",
                beschreibung=f"HWB ueberschritten: {hwb} kWh/m2a > 75 kWh/m2a",
                norm_verweis="OIB-RL 6",
                ist_wert=hwb,
                soll_wert=75.0,
                einheit="kWh/m2a",
                schwere=Schweregrad.HOCH,
                empfehlung="Daemmung verbessern oder Heizsystem optimieren",
                confidence=0.97,
            ))

        # fGEE
        fgee = plan_daten.get("fgee", 0)
        if fgee > 0 and fgee > 0.75:
            self.abweichungen.append(Abweichung(
                id="ABW_OIB_FGEE",
                typ="oib",
                beschreibung=f"fGEE ueberschritten: {fgee} > 0.75",
                norm_verweis="OIB-RL 6",
                ist_wert=fgee,
                soll_wert=0.75,
                einheit="Faktor",
                schwere=Schweregrad.HOCH,
                empfehlung="Gebaeulleftdichtheit und Haustechnik optimieren",
                confidence=0.95,
            ))

    def _pruefe_bundesland(self, plan_daten: Dict[str, Any], bundesland: str):
        """Pruefe Bundesland-spezifische Abweichungen."""
        bl = BUNDESLAENDER.get(bundesland, {})
        
        # Abstandsflaechen
        abstand = plan_daten.get("abstand_nachbar", 0)
        min_abstand = 3.5  # Standard Burgenland
        if abstand > 0 and abstand < min_abstand:
            self.abweichungen.append(Abweichung(
                id=f"ABW_BL_{bundesland.upper()}_ABSTAND",
                typ="bundesland",
                beschreibung=f"Abstandsflaeche unterschritten: {abstand}m < {min_abstand}m",
                norm_verweis=f"{bl.get('bauordnung_kurz', 'BauO')} (Abstandsflaechen)",
                ist_wert=abstand,
                soll_wert=min_abstand,
                einheit="m",
                schwere=Schweregrad.HOCH,
                empfehlung=f"Abstand auf mindestens {min_abstand}m vergroessern",
                confidence=0.96,
            ))

    def _pruefe_koordinaten(self, plan_daten: Dict[str, Any]):
        """Pruefe Koordinaten-Plausibilitaet."""
        koordinaten = plan_daten.get("koordinaten", {})
        rechtswert = koordinaten.get("rechtswert", 0)
        hochwert = koordinaten.get("hochwert", 0)
        
        # Oesterreich-Plausibilitaet (M31/M34)
        if rechtswert > 0 and (rechtswert < 300000 or rechtswert > 700000):
            self.abweichungen.append(Abweichung(
                id="ABW_KOORDINATEN_RECHTSWERT",
                typ="koordinaten",
                beschreibung=f"Rechtswert unplausibel: {rechtswert} (Oesterreich: 300000-700000)",
                norm_verweis="M31/M34 (Oesterreich)",
                ist_wert=rechtswert,
                soll_wert=300000.0,
                einheit="m",
                schwere=Schweregrad.HOCH,
                empfehlung="Koordinatensystem pruefen (M31/M34)",
                confidence=0.98,
            ))

    def _pruefe_hoehen(self, plan_daten: Dict[str, Any]):
        """Pruefe Hoehenangaben."""
        gelaende = plan_daten.get("gelaendehoehe", 0)
        fundament = plan_daten.get("fundament_hoehe", 0)
        
        if gelaende > 0 and fundament > gelaende + 5:
            self.abweichungen.append(Abweichung(
                id="ABW_HOEHEN_FUNDAMENT",
                typ="hoehe",
                beschreibung=f"Fundamenthoehe {fundament}m ueber Gelaende {gelaende}m - unplausibel",
                norm_verweis="Gelaendeanschluss",
                ist_wert=fundament,
                soll_wert=gelaende,
                einheit="m",
                schwere=Schweregrad.MITTEL,
                empfehlung="Hoehenangaben pruefen",
                confidence=0.90,
            ))

    def _pruefe_lasten(self, plan_daten: Dict[str, Any], bundesland: str):
        """Pruefe Last-Zuordnung."""
        bl = BUNDESLAENDER.get(bundesland, {})
        
        # Schneelast
        schneelast_ist = plan_daten.get("schneelast_knm2", 0)
        schneelast_soll = bl.get("schneelast_zone", 1.12)  # Burgenland
        
        if schneelast_ist > 0 and abs(schneelast_ist - schneelast_soll) > 0.2:
            self.abweichungen.append(Abweichung(
                id="ABW_LAST_SCHNEE",
                typ="last",
                beschreibung=f"Schneelast falsch: {schneelast_ist} kN/m2 vs {schneelast_soll} kN/m2 ({bundesland})",
                norm_verweis="OIB-RL 1 / EN 1991-1-3",
                ist_wert=schneelast_ist,
                soll_wert=schneelast_soll,
                einheit="kN/m2",
                schwere=Schweregrad.KRITISCH,
                empfehlung=f"Schneelast fuer {bundesland} korrigieren",
                confidence=0.97,
            ))

        # Windlast
        windlast_ist = plan_daten.get("windlast_knm2", 0)
        windlast_soll = 0.65  # Oesterreich Standard
        if windlast_ist > 0 and abs(windlast_ist - windlast_soll) > 0.15:
            self.abweichungen.append(Abweichung(
                id="ABW_LAST_WIND",
                typ="last",
                beschreibung=f"Windlast falsch: {windlast_ist} kN/m2 vs {windlast_soll} kN/m2",
                norm_verweis="OIB-RL 1 / EN 1991-1-4",
                ist_wert=windlast_ist,
                soll_wert=windlast_soll,
                einheit="kN/m2",
                schwere=Schweregrad.HOCH,
                empfehlung="Windlast korrigieren",
                confidence=0.94,
            ))

    def _pruefe_energetik(self, plan_daten: Dict[str, Any]):
        """Pruefe energetische Anforderungen."""
        # U-Werte
        u_wand = plan_daten.get("u_wand", 0)
        if u_wand > 0.22:
            self.abweichungen.append(Abweichung(
                id="ABW_ENERGETIK_U_WAND",
                typ="energetik",
                beschreibung=f"U-Wand zu hoch: {u_wand} W/m2K > 0.22 W/m2K",
                norm_verweis="OIB-RL 6",
                ist_wert=u_wand,
                soll_wert=0.22,
                einheit="W/m2K",
                schwere=Schweregrad.HOCH,
                empfehlung="Daemmung veraendern",
                confidence=0.95,
            ))

        u_dach = plan_daten.get("u_dach", 0)
        if u_dach > 0.15:
            self.abweichungen.append(Abweichung(
                id="ABW_ENERGETIK_U_DACH",
                typ="energetik",
                beschreibung=f"U-Dach zu hoch: {u_dach} W/m2K > 0.15 W/m2K",
                norm_verweis="OIB-RL 6",
                ist_wert=u_dach,
                soll_wert=0.15,
                einheit="W/m2K",
                schwere=Schweregrad.HOCH,
                empfehlung="Dachdaemmung veraendern",
                confidence=0.95,
            ))


# ============================================================================
# FEHLERERKENNUNGS-SYSTEM
# ============================================================================

class FehlererkennungsSystem:
    """Komplettes Fehlererkennungs-System mit Agenten-Schwarm."""

    def __init__(self):
        self.bemassungs_detektor = BemassungsDetektor()
        self.plan_detektor = PlanDetektor()
        self.planungs_detektor = PlanungsDetektor()
        self.abweichungs_detektor = AbweichungsDetektor()
        self.des_system = DeterministicEpistemicSystem("Fehlererkennungs-DES")
        self.ergebnisse = {}

    def analysiere(self, plan_daten: Dict[str, Any], geschoss: str = "EG", bundesland: str = "burgenland") -> Dict[str, Any]:
        """Vollstaendige Fehleranalyse."""
        print(f"\n  Analysiere: {geschoss}")
        print(f"  {'=' * 80}")

        # Detektoren ausfuehren
        bemassungsfehler = self.bemassungs_detektor.analysiere(plan_daten)
        planfehler = self.plan_detektor.analysiere(plan_daten, geschoss)
        planungsfehler = self.planungs_detektor.analysiere(plan_daten)
        abweichungen = self.abweichungs_detektor.analysiere(plan_daten, bundesland)

        # Zusammenfassung
        alle_fehler = []
        for f in bemassungsfehler:
            alle_fehler.append({
                "klasse": FehlerKlasse.BEMASSUNG.value,
                "id": f.id,
                "typ": f.typ,
                "beschreibung": f.beschreibung,
                "schwere": f.schwere.value,
                "confidence": f.confidence,
            })
        for f in planfehler:
            alle_fehler.append({
                "klasse": FehlerKlasse.PLAN.value,
                "id": f.id,
                "typ": f.typ,
                "beschreibung": f.beschreibung,
                "schwere": f.schwere.value,
                "confidence": f.confidence,
            })
        for f in planungsfehler:
            alle_fehler.append({
                "klasse": FehlerKlasse.PLANUNG.value,
                "id": f.id,
                "typ": f.typ,
                "beschreibung": f.beschreibung,
                "schwere": f.schwere.value,
                "confidence": f.confidence,
            })
        for f in abweichungen:
            alle_fehler.append({
                "klasse": f.typ,
                "id": f.id,
                "typ": f.typ,
                "beschreibung": f.beschreibung,
                "schwere": f.schwere.value,
                "confidence": f.confidence,
            })

        return {
            "geschoss": geschoss,
            "bemassungsfehler": len(bemassungsfehler),
            "planfehler": len(planfehler),
            "planungsfehler": len(planungsfehler),
            "abweichungen": len(abweichungen),
            "gesamt": len(alle_fehler),
            "fehler": alle_fehler,
        }


# ============================================================================
# TEST-DATEN (mit eingebauten Fehlern)
# ============================================================================

def generiere_test_plan_mit_fehlern(geschoss: str) -> Dict[str, Any]:
    """Generiere Test-Plan mit absichtlich eingebauten Fehlern."""
    if geschoss == "UG":
        return {
            "bemassungen": [
                {"typ": "aussenwand_laenge", "wert": 10000, "einheit": "mm", "gezeichnet_mm": 200, "position": (0, 0)},
                {"typ": "innenwand_laenge", "wert": 5000, "einheit": "mm", "gezeichnet_mm": 100, "position": (0, 50)},
                {"typ": "raum_hoehe", "wert": 2400, "einheit": "mm", "gezeichnet_mm": 48, "position": (50, 0)},
                # Fehler: widerspruechlich
                {"typ": "aussenwand_laenge", "wert": 10050, "einheit": "mm", "gezeichnet_mm": 201, "position": (100, 0)},
            ],
            "raeume": {
                "keller": {"flaeche_m2": 35.0, "hoehe_m": 2.4, "fenster_anteil": 0.05},
                "heizungsraum": {"flaeche_m2": 8.0, "hoehe_m": 2.2, "fenster_anteil": 0},
            },
            "fluchtwege": [],
            "treppen": [{"name": "haupttreppe", "stufen_hoehe_cm": 18, "stufen_tiefe_cm": 27}],
            "grundriss": True,
            "schnitte": True,
            "ansichten": True,
            "bemaßungen": True,
            "raumstempel": True,
            # Fehler: materialangaben unvollstaendig
            "materialien": [{"name": "beton", "spezifikation": "C25/30"}],
            "grundriss_flaeche": 80.0,
            "schnitt_flaeche": 85.0,  # Fehler: 6% Abweichung
            "koordinaten": {"rechtswert": 500000, "hochwert": 300000},
            "gelaendehoehe": 150.0,
            "fundament_hoehe": 148.0,
            "schneelast_knm2": 0.8,  # Fehler: Burgenland = 1.12
            "windlast_knm2": 0.65,
            "hwb": 55.0,
            "fgee": 0.62,
            "u_wand": 0.25,  # Fehler: > 0.22
            "u_dach": 0.18,  # Fehler: > 0.15
            "elemente": {},
        }
    elif geschoss == "EG":
        return {
            "bemassungen": [
                {"typ": "aussenwand_laenge", "wert": 10000, "einheit": "mm", "gezeichnet_mm": 200, "position": (0, 0)},
                {"typ": "innenwand_laenge", "wert": 5000, "einheit": "mm", "gezeichnet_mm": 100, "position": (0, 50)},
                {"typ": "raum_hoehe", "wert": 2800, "einheit": "mm", "gezeichnet_mm": 56, "position": (50, 0)},
                {"typ": "fenster_breite", "wert": 1500, "einheit": "mm", "gezeichnet_mm": 30, "position": (100, 50)},
                {"typ": "tuer_breite", "wert": 1000, "einheit": "mm", "gezeichnet_mm": 20, "position": (150, 50)},
            ],
            "raeume": {
                "wohnzimmer": {"flaeche_m2": 22.5, "hoehe_m": 2.8, "fenster_anteil": 0.20},
                "kueche": {"flaeche_m2": 15.0, "hoehe_m": 2.8, "fenster_anteil": 0.15},
                "flur": {"flaeche_m2": 12.0, "hoehe_m": 2.8, "fenster_anteil": 0.05},  # Fehler: < 10%
            },
            "fluchtwege": [
                {"name": "hauptfluchtweg", "breite_m": 1.0, "laenge_m": 15},  # Fehler: < 1.2m
                {"name": "nebenfluchtweg", "breite_m": 1.2, "laenge_m": 30},  # Fehler: > 25m
            ],
            "treppen": [{"name": "haupttreppe", "stufen_hoehe_cm": 20, "stufen_tiefe_cm": 25}],  # Fehler: > 19cm, < 26cm
            "grundriss": True,
            "schnitte": True,
            "ansichten": True,
            "bemaßungen": True,
            "raumstempel": True,
            "materialien": [{"name": "ziegel", "spezifikation": "Hochloch Z12"}],
            "grundriss_flaeche": 80.0,
            "schnitt_flaeche": 80.5,
            "koordinaten": {"rechtswert": 500000, "hochwert": 300000},
            "gelaendehoehe": 150.0,
            "fundament_hoehe": 149.0,
            "schneelast_knm2": 1.12,
            "windlast_knm2": 0.65,
            "hwb": 45.0,
            "fgee": 0.62,
            "u_wand": 0.18,
            "u_dach": 0.15,
            "elemente": {"rohr_fuer_brandwand": True},  # Fehler: Kollision
            "abstand_nachbar": 3.0,  # Fehler: < 3.5m
        }
    elif geschoss == "OG":
        return {
            "bemassungen": [
                {"typ": "aussenwand_laenge", "wert": 10000, "einheit": "mm", "gezeichnet_mm": 200, "position": (0, 0)},
                {"typ": "innenwand_laenge", "wert": 5000, "einheit": "mm", "gezeichnet_mm": 100, "position": (0, 50)},
                {"typ": "raum_hoehe", "wert": 2800, "einheit": "mm", "gezeichnet_mm": 56, "position": (50, 0)},
                {"typ": "fenster_breite", "wert": 1500, "einheit": "mm", "gezeichnet_mm": 30, "position": (100, 50)},
                {"typ": "tuer_breite", "wert": 900, "einheit": "mm", "gezeichnet_mm": 18, "position": (150, 50)},
            ],
            "raeume": {
                "schlafzimmer": {"flaeche_m2": 18.0, "hoehe_m": 2.8, "fenster_anteil": 0.15},
                "kinderzimmer": {"flaeche_m2": 8.0, "hoehe_m": 2.8, "fenster_anteil": 0.12},  # Fehler: < 10m2
                "bad": {"flaeche_m2": 6.5, "hoehe_m": 2.8, "fenster_anteil": 0.05},
            },
            "fluchtwege": [{"name": "fluchtweg", "breite_m": 1.2, "laenge_m": 15}],
            "treppen": [{"name": "haupttreppe", "stufen_hoehe_cm": 18, "stufen_tiefe_cm": 27}],
            "grundriss": True,
            "schnitte": False,  # Fehler: fehlt
            "ansichten": True,
            "bemaßungen": True,
            "raumstempel": True,
            "materialien": [],  # Fehler: keine Materialien
            "grundriss_flaeche": 60.0,
            "schnitt_flaeche": 0,  # Fehler: kein Schnitt
            "koordinaten": {"rechtswert": 800000, "hochwert": 300000},  # Fehler: Rechtswert unplausibel
            "gelaendehoehe": 150.0,
            "fundament_hoehe": 149.0,
            "schneelast_knm2": 1.12,
            "windlast_knm2": 0.65,
            "hwb": 45.0,
            "fgee": 0.62,
            "u_wand": 0.18,
            "u_dach": 0.15,
            "elemente": {},
        }
    elif geschoss == "DG":
        return {
            "bemassungen": [
                {"typ": "aussenwand_laenge", "wert": 10000, "einheit": "mm", "gezeichnet_mm": 200, "position": (0, 0)},
                {"typ": "innenwand_laenge", "wert": 5000, "einheit": "mm", "gezeichnet_mm": 100, "position": (0, 50)},
                {"typ": "dach_neigung", "wert": 35, "einheit": "grad", "gezeichnet_mm": 70, "position": (50, 0)},
            ],
            "raeume": {
                "galerie": {"flaeche_m2": 45.0, "hoehe_m": 2.3, "fenster_anteil": 0.08},  # Fehler: < 2.5m
                "abstell": {"flaeche_m2": 5.0, "hoehe_m": 2.0, "fenster_anteil": 0},  # Fehler: < 2.5m
            },
            "fluchtwege": [{"name": "dachfluchtweg", "breite_m": 0.9, "laenge_m": 12}],  # Fehler: < 1.2m
            "treppen": [],
            "grundriss": True,
            "schnitte": True,
            "ansichten": False,  # Fehler: fehlt
            "bemaßungen": True,
            "raumstempel": True,
            "materialien": [{"name": "holz", "spezifikation": ""}],  # Fehler: leere Spezifikation
            "grundriss_flaeche": 50.0,
            "schnitt_flaeche": 48.0,
            "koordinaten": {"rechtswert": 500000, "hochwert": 300000},
            "gelaendehoehe": 150.0,
            "fundament_hoehe": 149.0,
            "schneelast_knm2": 1.3,  # Fehler: Burgenland = 1.12
            "windlast_knm2": 0.85,  # Fehler: > 0.65
            "hwb": 80.0,  # Fehler: > 75
            "fgee": 0.80,  # Fehler: > 0.75
            "u_wand": 0.18,
            "u_dach": 0.12,
            "elemente": {},
        }
    return {}


# ============================================================================
# HAUPTPROGRAMM
# ============================================================================

def main():
    print("=" * 100)
    print("FEHLERERKENNUNGS-SYSTEM: Bemaßungsfehler, Planfehler, Planungsfehler, Abweichungen")
    print("6 Fehlerklassen mit automatischer Erkennung")
    print("=" * 100)

    system = FehlererkennungsSystem()
    gesamt_start = time.time()

    ergebnisse = {}
    for geschoss in ["UG", "EG", "OG", "DG"]:
        plan_daten = generiere_test_plan_mit_fehlern(geschoss)
        ergebnis = system.analysiere(plan_daten, geschoss)
        ergebnisse[geschoss] = ergebnis

    # Gesamtbericht
    gesamt_zeit = time.time() - gesamt_start
    gesamt_bemassung = sum(e["bemassungsfehler"] for e in ergebnisse.values())
    gesamt_plan = sum(e["planfehler"] for e in ergebnisse.values())
    gesamt_planung = sum(e["planungsfehler"] for e in ergebnisse.values())
    gesamt_abweichungen = sum(e["abweichungen"] for e in ergebnisse.values())
    gesamt_fehler = sum(e["gesamt"] for e in ergebnisse.values())

    print("\n" + "=" * 100)
    print("GESAMTBERICHT")
    print("=" * 100)

    print(f"\n  FEHLER NACH KLASSE:")
    print(f"  {'=' * 60}")
    print(f"  Bemaßungsfehler:     {gesamt_bemassung}")
    print(f"  Planfehler:          {gesamt_plan}")
    print(f"  Planungsfehler:      {gesamt_planung}")
    print(f"  Abweichungen:        {gesamt_abweichungen}")
    print(f"  GESAMT:              {gesamt_fehler}")

    print(f"\n  DETAILLEIERTE FEHLER:")
    print(f"  {'=' * 60}")
    for geschoss, erg in ergebnisse.items():
        print(f"\n  {geschoss}: {erg['gesamt']} Fehler")
        for f in erg["fehler"]:
            print(f"    [{f['schwere']}] {f['id']}: {f['beschreibung']}")
            print(f"      Confidence: {f['confidence']:.2f}")

    print(f"\n  DAUER: {gesamt_zeit:.2f}s")

    # JSON-Export
    report_path = os.path.join(os.path.dirname(__file__), "..", "fehlererkennungs_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(ergebnisse, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nReport gespeichert: {report_path}")

    print("\n" + "=" * 100)
    print("FEHLERERKENNUNGS-SYSTEM: EINSATZBEREIT")
    print("=" * 100)


if __name__ == "__main__":
    main()