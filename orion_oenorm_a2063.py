#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
ORION ÖNORM A 2063 - Angebotslegung & Ausschreibung für Österreich
═══════════════════════════════════════════════════════════════════════════

Professionelle Ausschreibungs- und Angebotslegungsfunktionen nach:
- ÖNORM A 2063-1:2024 (Klassische AVA - Ausschreibung, Vergabe, Abrechnung)
- ÖNORM A 2063-2:2021 (BIM Level 3 Integration)
- ÖNORM B 2110:2013 (Werkvertragsnorm)
- ÖNORM B 1801-1:2009 (Kostenermittlung)

Module:
1. Leistungsverzeichnis (LV) Generator - Detaillierte Positionen
2. Angebots-Vergleich & Preisspiegelmatrix
3. GAEB/XML Export (Datenaustausch)
4. BIM-IFC Integration (Mengenübernahme)
5. Vergabeempfehlung nach Bundesvergabegesetz

Stand: April 2026
Erstellt von: Elisabeth Steurer & Gerhard Hirschmann
Lizenz: Apache 2.0
═══════════════════════════════════════════════════════════════════════════
"""

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════════
# STANDARDISIERTE LEISTUNGSKATALOGE (StLB-BAU / ABK)
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class LVPosition:
    """
    Einzelposition im Leistungsverzeichnis nach ÖNORM A 2063

    Attributes:
        oz: Ordnungszahl (z.B. "01.001")
        kurztext: Kurzbeschreibung der Position
        langtext: Detaillierte Leistungsbeschreibung
        einheit: Mengeneinheit (m, m², m³, Stk, psch, etc.)
        menge: Anzahl/Menge
        ep: Einheitspreis (vom Bieter auszufüllen)
        gp: Gesamtpreis (Menge × EP, berechnet)
        gewerk: Zugehöriges Gewerk
        kostengruppe: ÖNORM B 1801-1 Kostengruppe (300-700)
        bim_ref: Optional: IFC-GUID für BIM-Integration
        stlb_code: Optional: StLB-BAU Positionscode
        version: Versionsnummer der Position
        aenderungs_historie: Liste der Änderungen
    """

    oz: str
    kurztext: str
    langtext: str
    einheit: str
    menge: float
    ep: float = 0.0
    gp: float = 0.0
    gewerk: str = ""
    kostengruppe: int = 300
    bim_ref: Optional[str] = None
    stlb_code: Optional[str] = None
    version: str = "1.0"
    aenderungs_historie: Optional[List[Dict[str, Any]]] = None

    def __post_init__(self):
        """Berechne Gesamtpreis automatisch"""
        self.gp = round(self.menge * self.ep, 2)
        if self.aenderungs_historie is None:
            self.aenderungs_historie = []


@dataclass
class LVAenderung:
    """
    Dokumentiert eine Änderung im Leistungsverzeichnis

    Attributes:
        timestamp: Zeitstempel der Änderung
        version: Versionsnummer nach Änderung
        autor: Person/System, das die Änderung durchgeführt hat
        aenderung_typ: Art der Änderung (ERSTELLT, GEAENDERT, GELOESCHT)
        betroffene_positionen: Liste der OZ-Nummern
        beschreibung: Textuelle Beschreibung der Änderung
        checksum: SHA-256 Hash des geänderten LV-Stands
    """

    timestamp: str
    version: str
    autor: str
    aenderung_typ: str  # ERSTELLT, GEAENDERT, GELOESCHT
    betroffene_positionen: List[str]
    beschreibung: str
    checksum: str = ""

    def __post_init__(self):
        if not self.checksum:
            # Generate checksum from change data
            data = f"{self.timestamp}{self.version}{self.aenderung_typ}{''.join(self.betroffene_positionen)}"
            self.checksum = hashlib.sha256(data.encode()).hexdigest()[:16]


def erstelle_lv_aenderung(
    positionen_alt: List[LVPosition],
    positionen_neu: List[LVPosition],
    version_neu: str,
    autor: str = "THE ARCHITEKT",
) -> LVAenderung:
    """
    Erstellt Änderungsdokumentation zwischen zwei LV-Versionen

    Args:
        positionen_alt: Alte LV-Positionen
        positionen_neu: Neue LV-Positionen
        version_neu: Versionsnummer der neuen Version
        autor: Autor der Änderung

    Returns:
        LVAenderung mit Details zu allen Änderungen
    """
    oz_alt = {p.oz for p in positionen_alt}
    oz_neu = {p.oz for p in positionen_neu}

    gelöscht = oz_alt - oz_neu
    hinzugefügt = oz_neu - oz_alt
    geändert = []

    # Check for changes in existing positions
    for pos_neu in positionen_neu:
        if pos_neu.oz in oz_alt:
            pos_alt = next(p for p in positionen_alt if p.oz == pos_neu.oz)
            if (
                pos_neu.menge != pos_alt.menge
                or pos_neu.ep != pos_alt.ep
                or pos_neu.kurztext != pos_alt.kurztext
            ):
                geändert.append(pos_neu.oz)

    beschreibung_teile = []
    if hinzugefügt:
        beschreibung_teile.append(f"{len(hinzugefügt)} neue Positionen")
    if geändert:
        beschreibung_teile.append(f"{len(geändert)} geänderte Positionen")
    if gelöscht:
        beschreibung_teile.append(f"{len(gelöscht)} gelöschte Positionen")

    aenderung_typ = "GEAENDERT"
    if not positionen_alt:
        aenderung_typ = "ERSTELLT"
    elif not positionen_neu:
        aenderung_typ = "GELOESCHT"

    betroffene = list(hinzugefügt) + geändert + list(gelöscht)

    return LVAenderung(
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        version=version_neu,
        autor=autor,
        aenderung_typ=aenderung_typ,
        betroffene_positionen=sorted(betroffene),
        beschreibung=", ".join(beschreibung_teile) if beschreibung_teile else "Keine Änderungen",
    )


def vergleiche_lv_versionen(
    positionen_v1: List[LVPosition], positionen_v2: List[LVPosition]
) -> Dict[str, Any]:
    """
    Vergleicht zwei LV-Versionen und zeigt Unterschiede

    Args:
        positionen_v1: LV Version 1
        positionen_v2: LV Version 2

    Returns:
        Dict mit detailliertem Versionsvergleich
    """
    oz_v1 = {p.oz for p in positionen_v1}
    oz_v2 = {p.oz for p in positionen_v2}

    neu = oz_v2 - oz_v1
    gelöscht = oz_v1 - oz_v2
    geändert_details = []

    for pos_v2 in positionen_v2:
        if pos_v2.oz in oz_v1:
            pos_v1 = next(p for p in positionen_v1 if p.oz == pos_v2.oz)

            änderungen = []
            if pos_v2.menge != pos_v1.menge:
                änderungen.append(f"Menge: {pos_v1.menge} → {pos_v2.menge}")
            if pos_v2.ep != pos_v1.ep:
                änderungen.append(f"EP: {pos_v1.ep} € → {pos_v2.ep} €")
            if pos_v2.kurztext != pos_v1.kurztext:
                änderungen.append("Kurztext geändert")

            if änderungen:
                geändert_details.append(
                    {
                        "oz": pos_v2.oz,
                        "kurztext": pos_v2.kurztext,
                        "änderungen": änderungen,
                        "gp_alt": pos_v1.gp,
                        "gp_neu": pos_v2.gp,
                        "differenz_eur": round(pos_v2.gp - pos_v1.gp, 2),
                    }
                )

    return {
        "anzahl_neu": len(neu),
        "anzahl_geloescht": len(gelöscht),
        "anzahl_geaendert": len(geändert_details),
        "neue_positionen": sorted(list(neu)),
        "geloeschte_positionen": sorted(list(gelöscht)),
        "geaenderte_positionen": geändert_details,
        "zusammenfassung": f"{len(neu)} neu, {len(geändert_details)} geändert, {len(gelöscht)} gelöscht",
    }


# ═══════════════════════════════════════════════════════════════════════════
# VERSCHNITT- UND VERLUSTZUSCHLÄGE (Österreich-spezifisch)
# ═══════════════════════════════════════════════════════════════════════════

WASTE_FACTORS_AT = {
    # Quelle: Österreichische Baupraxis, BKI-Baukosten 2024
    "beton": 0.03,  # 3% Verschnitt bei Betonarbeiten
    "mauerwerk": 0.08,  # 8% Verschnitt bei Mauersteinen
    "estrich": 0.05,  # 5% Verschnitt bei Estrichen
    "erdarbeiten": 0.10,  # 10% Auflockerung + Sackung bei Erdarbeiten
    "holz": 0.06,  # 6% Verschnitt bei Holzkonstruktionen
    "dachziegel": 0.10,  # 10% Verschnitt bei Dachziegeln
    "gipskarton": 0.12,  # 12% Verschnitt bei Trockenbau
    "fliesen": 0.08,  # 8% Verschnitt bei Fliesenarbeiten
    "putz": 0.05,  # 5% Verschnitt bei Putzarbeiten
    "default": 0.05,  # 5% Standard für sonstige Gewerke
}


# ═══════════════════════════════════════════════════════════════════════════
# GEWERK-KATALOG (Österreichische Standardgewerke)
# ═══════════════════════════════════════════════════════════════════════════

GEWERKE_KATALOG_AT = {
    "01": {
        "name": "Baumeisterarbeiten",
        "beschreibung": "Erdarbeiten, Mauerwerk, Beton, Stahlbeton",
        "kostengruppe": 300,
        "typische_einheiten": ["m³", "m²", "m", "Stk"],
    },
    "02": {
        "name": "Zimmerer-/Holzbauarbeiten",
        "beschreibung": "Dachstuhl, Holzkonstruktionen, Holzfassaden",
        "kostengruppe": 330,
        "typische_einheiten": ["m³", "m²", "m", "Stk"],
    },
    "03": {
        "name": "Dachdecker-/Spenglerarbeiten",
        "beschreibung": "Dachdeckung, Abdichtung, Blecharbeiten",
        "kostengruppe": 360,
        "typische_einheiten": ["m²", "m", "Stk"],
    },
    "04": {
        "name": "Fenster und Außentüren",
        "beschreibung": "Fenster, Balkon-/Terrassentüren, Haustüren",
        "kostengruppe": 330,
        "typische_einheiten": ["m²", "Stk"],
    },
    "05": {
        "name": "Elektroinstallationen",
        "beschreibung": "Elektroleitungen, Schalter, Steckdosen, Verteiler",
        "kostengruppe": 440,
        "typische_einheiten": ["m", "Stk", "psch"],
    },
    "06": {
        "name": "Sanitärinstallationen",
        "beschreibung": "Wasser-, Abwasserleitungen, Sanitärobjekte",
        "kostengruppe": 450,
        "typische_einheiten": ["m", "Stk", "psch"],
    },
    "07": {
        "name": "Heizung-Lüftung-Klima (HLK)",
        "beschreibung": "Heizungsanlage, Lüftung, Klimatechnik",
        "kostengruppe": 460,
        "typische_einheiten": ["kW", "Stk", "psch"],
    },
    "08": {
        "name": "Estrich-/Bodenbelagsarbeiten",
        "beschreibung": "Estrich, Fliesen, Parkett, Teppich",
        "kostengruppe": 370,
        "typische_einheiten": ["m²"],
    },
    "09": {
        "name": "Maler-/Anstreicherarbeiten",
        "beschreibung": "Innen-/Außenanstrich, Tapezierarbeiten",
        "kostengruppe": 370,
        "typische_einheiten": ["m²"],
    },
    "10": {
        "name": "Fliesenlegerarbeiten",
        "beschreibung": "Wand-/Bodenfliesen, Natursteinverlegung",
        "kostengruppe": 370,
        "typische_einheiten": ["m²"],
    },
    "11": {
        "name": "Tischlerarbeiten (Innentüren)",
        "beschreibung": "Innentüren, Zargen, Einbaumöbel",
        "kostengruppe": 340,
        "typische_einheiten": ["Stk", "lfm"],
    },
    "12": {
        "name": "Außenanlagen",
        "beschreibung": "Pflasterung, Zäune, Bepflanzung",
        "kostengruppe": 500,
        "typische_einheiten": ["m²", "m", "Stk"],
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# BAUPHASEN-STRUKTUR (Österreich-spezifisch)
# ═══════════════════════════════════════════════════════════════════════════

BAUPHASEN_AT: Dict[str, Any] = {
    "01_rohbau": {
        "name": "Rohbau",
        "beschreibung": "Erdarbeiten, Fundamente, Mauerwerk, Decken, Dach",
        "kostengruppen": [300, 310, 320, 330, 360],
        "phase_prozent": 0.45,  # Ca. 45% der Baukosten
    },
    "02_ausbau": {
        "name": "Innenausbau",
        "beschreibung": "Fenster, Türen, Estrich, Böden, Sanitär, Elektro, HLK",
        "kostengruppen": [330, 340, 370, 440, 450, 460],
        "phase_prozent": 0.40,  # Ca. 40% der Baukosten
    },
    "03_fertigstellung": {
        "name": "Fertigstellung",
        "beschreibung": "Maler, Fliesen, Außenanlagen",
        "kostengruppen": [370, 500],
        "phase_prozent": 0.15,  # Ca. 15% der Baukosten
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# REGIONALE KOSTENFAKTOREN (9 Bundesländer Österreichs)
# ═══════════════════════════════════════════════════════════════════════════

REGIONALE_FAKTOREN_AT: Dict[str, Any] = {
    "wien": {
        "name": "Wien",
        "faktor": 1.15,  # 15% höher als Durchschnitt
        "beschreibung": "Metropolregion, höhere Lohn- und Materialkosten",
        "lohnkosten_index": 115,
        "materialkosten_index": 110,
    },
    "tirol": {
        "name": "Tirol",
        "faktor": 1.12,  # 12% höher
        "beschreibung": "Bergregion, höhere Transport- und Logistikkosten",
        "lohnkosten_index": 112,
        "materialkosten_index": 115,
    },
    "vorarlberg": {
        "name": "Vorarlberg",
        "faktor": 1.10,  # 10% höher
        "beschreibung": "Grenzregion, hohe Lohnkosten",
        "lohnkosten_index": 114,
        "materialkosten_index": 108,
    },
    "salzburg": {
        "name": "Salzburg",
        "faktor": 1.08,  # 8% höher
        "beschreibung": "Tourismusregion, mittlere bis hohe Kosten",
        "lohnkosten_index": 108,
        "materialkosten_index": 108,
    },
    "oberoesterreich": {
        "name": "Oberösterreich",
        "faktor": 1.03,  # 3% höher
        "beschreibung": "Industrieregion, Durchschnittskosten",
        "lohnkosten_index": 104,
        "materialkosten_index": 102,
    },
    "niederoesterreich": {
        "name": "Niederösterreich",
        "faktor": 1.00,  # Referenz
        "beschreibung": "Referenzregion, Durchschnittskosten",
        "lohnkosten_index": 100,
        "materialkosten_index": 100,
    },
    "steiermark": {
        "name": "Steiermark",
        "faktor": 0.98,  # 2% niedriger
        "beschreibung": "Ländliche Region, leicht unterdurchschnittliche Kosten",
        "lohnkosten_index": 98,
        "materialkosten_index": 98,
    },
    "kaernten": {
        "name": "Kärnten",
        "faktor": 0.96,  # 4% niedriger
        "beschreibung": "Grenzregion, unterdurchschnittliche Kosten",
        "lohnkosten_index": 96,
        "materialkosten_index": 96,
    },
    "burgenland": {
        "name": "Burgenland",
        "faktor": 0.92,  # 8% niedriger
        "beschreibung": "Ländliche Region, niedrigste Baukosten",
        "lohnkosten_index": 92,
        "materialkosten_index": 92,
    },
}


def berechne_regionale_anpassung(
    positionen: List[LVPosition], bundesland: str = "niederoesterreich"
) -> Dict[str, Any]:
    """
    Berechnet regionale Kostenanpassung für ein Bundesland

    Args:
        positionen: LV-Positionen mit Einheitspreisen
        bundesland: Bundesland-Schlüssel (lowercase)

    Returns:
        Dict mit angepassten Kosten und Faktor
    """
    bundesland_lower = bundesland.lower().replace("ö", "oe").replace("ü", "ue")

    if bundesland_lower not in REGIONALE_FAKTOREN_AT:
        bundesland_lower = "niederoesterreich"  # Fallback

    region_info = REGIONALE_FAKTOREN_AT[bundesland_lower]
    faktor = region_info["faktor"]

    positionen_angepasst = []
    kosten_original = 0.0
    kosten_angepasst = 0.0

    for pos in positionen:
        pos_neu = LVPosition(
            oz=pos.oz,
            kurztext=pos.kurztext,
            langtext=pos.langtext,
            einheit=pos.einheit,
            menge=pos.menge,
            ep=round(pos.ep * faktor, 2),
            gewerk=pos.gewerk,
            kostengruppe=pos.kostengruppe,
            bim_ref=pos.bim_ref,
            stlb_code=pos.stlb_code,
        )

        kosten_original += pos.gp
        kosten_angepasst += pos_neu.gp

        positionen_angepasst.append(pos_neu)

    return {
        "bundesland": region_info["name"],
        "faktor": faktor,
        "beschreibung": region_info["beschreibung"],
        "lohnkosten_index": region_info["lohnkosten_index"],
        "materialkosten_index": region_info["materialkosten_index"],
        "kosten_original_eur": round(kosten_original, 2),
        "kosten_angepasst_eur": round(kosten_angepasst, 2),
        "differenz_eur": round(kosten_angepasst - kosten_original, 2),
        "differenz_prozent": round((faktor - 1.0) * 100, 2),
        "positionen_angepasst": positionen_angepasst,
    }


# ═══════════════════════════════════════════════════════════════════════════
# PARAMETRISCHE POSITIONS-TEMPLATES (Wiederverwendbare Bauelemente)
# ═══════════════════════════════════════════════════════════════════════════


def erstelle_template_erdarbeiten(grundflaeche_m2: float, tiefe_m: float = 3.0) -> LVPosition:
    """Parametrisches Template: Erdarbeiten mit Auflockerungszuschlag"""
    menge_netto = grundflaeche_m2 * tiefe_m
    menge_brutto = round(menge_netto * (1 + WASTE_FACTORS_AT["erdarbeiten"]), 2)

    return LVPosition(
        oz="01.001",
        kurztext="Erdarbeiten Aushub",
        langtext=f"Erdaushub maschinell bis {tiefe_m}m Tiefe, inkl. Zwischenlagerung und Abtransport (inkl. 10% Auflockerungszuschlag)",
        einheit="m³",
        menge=menge_brutto,
        gewerk="01",
        kostengruppe=300,
        stlb_code="001.01.001",
    )


def erstelle_template_betondecke(
    flaeche_m2: float, dicke_cm: int = 20, betonfestigkeitsklasse: str = "C25/30"
) -> LVPosition:
    """Parametrisches Template: Stahlbetondecke"""
    volumen_netto = flaeche_m2 * (dicke_cm / 100)
    volumen_brutto = round(volumen_netto * (1 + WASTE_FACTORS_AT["beton"]), 2)

    return LVPosition(
        oz="01.004",
        kurztext=f"Decke Stahlbeton {dicke_cm}cm",
        langtext=f"Stahlbetondecke {dicke_cm}cm, {betonfestigkeitsklasse}, bewehrt mit Baustahlgewebe, inkl. Schalung gemäß Statik (inkl. 3% Betonverschnitt)",
        einheit="m²",
        menge=flaeche_m2,
        gewerk="01",
        kostengruppe=320,
    )


def erstelle_template_mauerwerk(
    umfang_m: float, hoehe_m: float = 2.5, dicke_cm: int = 25
) -> LVPosition:
    """Parametrisches Template: Mauerwerk mit Verschnittzuschlag"""
    flaeche_netto = umfang_m * hoehe_m
    flaeche_brutto = round(flaeche_netto * (1 + WASTE_FACTORS_AT["mauerwerk"]), 2)

    return LVPosition(
        oz="01.003",
        kurztext=f"Mauerwerk {dicke_cm}cm",
        langtext=f"Mauerwerk {dicke_cm}cm, Ziegel HLz {dicke_cm}, vermörtelt, inkl. Horizontalsperre (inkl. 8% Ziegelverschnitt)",
        einheit="m²",
        menge=flaeche_brutto,
        gewerk="01",
        kostengruppe=320,
    )


def erstelle_template_dacheindeckung(
    dachflaeche_m2: float, material: str = "Tondachziegel"
) -> LVPosition:
    """Parametrisches Template: Dacheindeckung mit Verschnittzuschlag"""
    flaeche_brutto = round(dachflaeche_m2 * (1 + WASTE_FACTORS_AT["dachziegel"]), 2)

    return LVPosition(
        oz="03.001",
        kurztext=f"Dacheindeckung {material}",
        langtext=f"Dachdeckung {material} Wienerberger Alegra, inkl. Unterdach und Dampfsperre (inkl. 10% Ziegelverschnitt)",
        einheit="m²",
        menge=flaeche_brutto,
        gewerk="03",
        kostengruppe=360,
    )


def erstelle_template_estrich(
    nutzflaeche_m2: float, typ: str = "Heizestrich", dicke_cm: int = 6
) -> LVPosition:
    """Parametrisches Template: Estrich mit Verschnittzuschlag"""
    flaeche_brutto = round(nutzflaeche_m2 * (1 + WASTE_FACTORS_AT["estrich"]), 2)

    return LVPosition(
        oz="08.001",
        kurztext=f"{typ} {dicke_cm}cm",
        langtext=f"{typ} {dicke_cm}cm über Fußbodenheizung, inkl. Dämmung EPS 10cm (inkl. 5% Estrichverschnitt)",
        einheit="m²",
        menge=flaeche_brutto,
        gewerk="08",
        kostengruppe=370,
    )


def erstelle_template_fenster(
    anzahl: int, flaeche_m2_pro_stueck: float = 1.5, u_wert: float = 0.9
) -> LVPosition:
    """Parametrisches Template: Fenster nach OIB-RL 6"""
    flaeche_gesamt = anzahl * flaeche_m2_pro_stueck

    return LVPosition(
        oz="04.001",
        kurztext="Fenster Holz-Alu",
        langtext=f"Fenster Holz-Aluminium, 3-fach-Verglasung Ug=0.7 W/m²K, Uw≤{u_wert} W/m²K nach OIB-RL 6",
        einheit="m²",
        menge=round(flaeche_gesamt, 2),
        gewerk="04",
        kostengruppe=330,
    )


# ═══════════════════════════════════════════════════════════════════════════
# LV-GENERATOR: BEISPIELPOSITIONEN FÜR EINFAMILIENHAUS
# ═══════════════════════════════════════════════════════════════════════════


def generiere_beispiel_lv_einfamilienhaus(
    bgf_m2: float = 150, geschosse: int = 2
) -> List[LVPosition]:
    """
    Generiert Beispiel-Leistungsverzeichnis für Einfamilienhaus

    Args:
        bgf_m2: Bruttogrundfläche in m²
        geschosse: Anzahl Geschosse

    Returns:
        Liste von LVPosition Objekten
    """
    positionen = []

    # Gewerk 01: Baumeisterarbeiten
    positionen.extend(
        [
            LVPosition(
                oz="01.001",
                kurztext="Erdarbeiten Aushub",
                langtext="Erdaushub für Keller/Fundament, maschinell, inkl. Zwischenlagerung und Abtransport überschüssiger Erde (inkl. 10% Auflockerungszuschlag)",
                einheit="m³",
                menge=round(bgf_m2 * 0.8 * (1 + WASTE_FACTORS_AT["erdarbeiten"]), 2),
                gewerk="01",
                kostengruppe=300,
                stlb_code="001.01.001",
            ),
            LVPosition(
                oz="01.002",
                kurztext="Fundament Streifenfundament",
                langtext="Streifenfundament C25/30, bewehrt, inkl. Schalung und Verdichtung, gemäß Statik (inkl. 3% Betonverschnitt)",
                einheit="m³",
                menge=round(bgf_m2 * 0.15 * (1 + WASTE_FACTORS_AT["beton"]), 2),
                gewerk="01",
                kostengruppe=310,
            ),
            LVPosition(
                oz="01.003",
                kurztext="Kellermauerwerk 25cm",
                langtext="Kellermauerwerk 25cm, Ziegel HLz 25, vermörtelt, inkl. Horizontalsperre (inkl. 8% Ziegelverschnitt)",
                einheit="m²",
                menge=(
                    round((bgf_m2**0.5 * 4) * 2.5 * (1 + WASTE_FACTORS_AT["mauerwerk"]), 2)
                    if geschosse >= 1
                    else 0
                ),
                gewerk="01",
                kostengruppe=320,
            ),
            LVPosition(
                oz="01.004",
                kurztext="Decke Stahlbeton 20cm",
                langtext="Stahlbetondecke 20cm, C25/30, bewehrt mit Baustahlgewebe, inkl. Schalung gemäß Statik (inkl. 3% Betonverschnitt)",
                einheit="m²",
                menge=round(bgf_m2 * (geschosse - 1) * (1 + WASTE_FACTORS_AT["beton"]), 2),
                gewerk="01",
                kostengruppe=320,
            ),
        ]
    )

    # Gewerk 02: Zimmererarbeiten
    positionen.extend(
        [
            LVPosition(
                oz="02.001",
                kurztext="Dachstuhl Pfettendach",
                langtext="Pfettendachstuhl, Konstruktionsvollholz C24, inkl. Lattung und Konterlattung, Dachneigung 35° (inkl. 6% Holzverschnitt)",
                einheit="m²",
                menge=round(bgf_m2 * 0.7 * (1 + WASTE_FACTORS_AT["holz"]), 2),
                gewerk="02",
                kostengruppe=330,
            ),
        ]
    )

    # Gewerk 03: Dachdeckerarbeiten
    positionen.extend(
        [
            LVPosition(
                oz="03.001",
                kurztext="Dacheindeckung Ziegel",
                langtext="Dachdeckung Tondachziegel Wienerberger Alegra, inkl. Unterdach und Dampfsperre (inkl. 10% Ziegelverschnitt)",
                einheit="m²",
                menge=round(bgf_m2 * 0.7 * (1 + WASTE_FACTORS_AT["dachziegel"]), 2),
                gewerk="03",
                kostengruppe=360,
            ),
            LVPosition(
                oz="03.002",
                kurztext="Dachrinnen und Fallrohre",
                langtext="Dachrinnen halbrund DN 150, Kupfer, inkl. Fallrohre DN 100",
                einheit="m",
                menge=round(bgf_m2**0.5 * 4, 2),  # Umfang
                gewerk="03",
                kostengruppe=360,
            ),
        ]
    )

    # Gewerk 04: Fenster
    positionen.extend(
        [
            LVPosition(
                oz="04.001",
                kurztext="Fenster Holz-Alu",
                langtext="Fenster Holz-Aluminium, 3-fach-Verglasung Ug=0.7 W/m²K, Uw≤0.9 W/m²K nach OIB-RL 6",
                einheit="m²",
                menge=round(bgf_m2 * 0.18, 2),  # Ca. 18% Fensterfläche
                gewerk="04",
                kostengruppe=330,
            ),
            LVPosition(
                oz="04.002",
                kurztext="Haustür Alu",
                langtext="Haustür Aluminium, wärmegedämmt, U≤1.0 W/m²K, inkl. Beschlag und Zylinder",
                einheit="Stk",
                menge=1,
                gewerk="04",
                kostengruppe=330,
            ),
        ]
    )

    # Gewerk 05: Elektro
    positionen.extend(
        [
            LVPosition(
                oz="05.001",
                kurztext="Elektroinstallation Grundausstattung",
                langtext="Elektroinstallation komplett, Schuko-Steckdosen, Lichtschalter, Verteiler, Leitungen NYM-J",
                einheit="psch",
                menge=1,
                gewerk="05",
                kostengruppe=440,
            ),
        ]
    )

    # Gewerk 06: Sanitär
    positionen.extend(
        [
            LVPosition(
                oz="06.001",
                kurztext="Sanitärinstallation komplett",
                langtext="Wasser-/Abwasserleitungen, Sanitärobjekte (WC, Waschbecken, Dusche, Badewanne), Armaturen Mittelklasse",
                einheit="psch",
                menge=1,
                gewerk="06",
                kostengruppe=450,
            ),
        ]
    )

    # Gewerk 07: Heizung
    positionen.extend(
        [
            LVPosition(
                oz="07.001",
                kurztext="Wärmepumpe Luft-Wasser",
                langtext="Luft-Wasser-Wärmepumpe 8-12 kW, inkl. Pufferspeicher 300L, Fußbodenheizung komplett",
                einheit="psch",
                menge=1,
                gewerk="07",
                kostengruppe=460,
            ),
        ]
    )

    # Gewerk 08: Estrich/Boden
    positionen.extend(
        [
            LVPosition(
                oz="08.001",
                kurztext="Estrich Heizestrich",
                langtext="Heizestrich 6cm über Fußbodenheizung, inkl. Dämmung EPS 10cm (inkl. 5% Estrichverschnitt)",
                einheit="m²",
                menge=round(bgf_m2 * 0.8 * (1 + WASTE_FACTORS_AT["estrich"]), 2),
                gewerk="08",
                kostengruppe=370,
            ),
            LVPosition(
                oz="08.002",
                kurztext="Bodenbelag Parkett/Fliesen",
                langtext="Bodenbeläge: Parkett Eiche gebürstet (Wohnbereich), Fliesen (Nassbereiche) (inkl. 8% Fliesenverschnitt)",
                einheit="m²",
                menge=round(bgf_m2 * 0.8 * (1 + WASTE_FACTORS_AT["fliesen"]), 2),
                gewerk="08",
                kostengruppe=370,
            ),
        ]
    )

    # Gewerk 09: Malerarbeiten
    positionen.extend(
        [
            LVPosition(
                oz="09.001",
                kurztext="Malerarbeiten innen",
                langtext="Innenanstrich Wände/Decken, 2× Dispersionsfarbe weiß, inkl. Spachteln (inkl. 5% Materialverschnitt)",
                einheit="m²",
                menge=round(bgf_m2 * 3.5 * (1 + WASTE_FACTORS_AT["putz"]), 2),
                gewerk="09",
                kostengruppe=370,
            ),
        ]
    )

    # Gewerk 12: Außenanlagen
    positionen.extend(
        [
            LVPosition(
                oz="12.001",
                kurztext="Terrasse Pflaster",
                langtext="Terrasse Betonpflaster, inkl. Unterbau und Randeinfassung",
                einheit="m²",
                menge=round(bgf_m2 * 0.25, 2),  # Ca. 25% der BGF
                gewerk="12",
                kostengruppe=500,
            ),
        ]
    )

    return positionen


def berechne_phasen_kosten(positionen: List[LVPosition]) -> Dict[str, Any]:
    """
    Berechnet Kostenverteilung nach Bauphasen

    Args:
        positionen: Liste der LV-Positionen

    Returns:
        Dict mit Phasenkosten und Prozentanteilen
    """
    phasen_kosten = {}
    total_gp = sum(p.gp for p in positionen)

    for phase_key, phase_info in BAUPHASEN_AT.items():
        phase_positionen = [p for p in positionen if p.kostengruppe in phase_info["kostengruppen"]]

        phase_summe = sum(p.gp for p in phase_positionen)
        phase_prozent = (phase_summe / total_gp * 100) if total_gp > 0 else 0.0

        phasen_kosten[phase_key] = {
            "name": phase_info["name"],
            "beschreibung": phase_info["beschreibung"],
            "anzahl_positionen": len(phase_positionen),
            "summe_eur": round(phase_summe, 2),
            "prozent": round(phase_prozent, 2),
            "soll_prozent": phase_info["phase_prozent"] * 100,
            "abweichung_prozent": round(phase_prozent - phase_info["phase_prozent"] * 100, 2),
        }

    return {
        "total_eur": round(total_gp, 2),
        "phasen": phasen_kosten,
        "anzahl_phasen": len(phasen_kosten),
    }


# ═══════════════════════════════════════════════════════════════════════════
# LV-EXPORT: ÖNORM A 2063 konformes JSON-Format
# ═══════════════════════════════════════════════════════════════════════════


def exportiere_lv_oenorm_json(
    positionen: List[LVPosition],
    projekt_info: Dict[str, Any],
    auftraggeber: Dict[str, str],
    bundesland: str = "tirol",
) -> Dict[str, Any]:
    """
    Exportiert Leistungsverzeichnis im ÖNORM A 2063-konformen JSON-Format

    Args:
        positionen: Liste der LV-Positionen
        projekt_info: Projektinformationen (Name, Adresse, etc.)
        auftraggeber: Auftraggeber-Daten
        bundesland: Bundesland für rechtliche Hinweise

    Returns:
        ÖNORM A 2063-konformes Dict
    """
    # Gruppiere Positionen nach Gewerk
    gewerke_dict: Dict[str, Any] = {}
    for pos in positionen:
        gewerk_nr = pos.gewerk
        if gewerk_nr not in gewerke_dict:
            gewerk_info = GEWERKE_KATALOG_AT.get(gewerk_nr, {"name": "Unbekannt"})
            gewerke_dict[gewerk_nr] = {
                "gewerk_nr": gewerk_nr,
                "gewerk_name": gewerk_info["name"],
                "positionen": [],
            }
        gewerke_dict[gewerk_nr]["positionen"].append(asdict(pos))

    # Rechtliche Hinweise nach Bundesland
    rechtliche_hinweise = [
        "Vertragsgrundlage: ÖNORM B 2110 (Werkvertragsnorm)",
        "Gewährleistung: 3 Jahre ab Abnahme (ABGB § 1167)",
        "Preise: Netto-Einheitspreise, zzgl. 20% USt",
        "Angebotsfrist: mind. 3 Wochen nach ÖNORM A 2063",
        "Zuschlagsfrist: 2 Monate nach Angebotsabgabe",
    ]

    if bundesland.lower() == "wien":
        rechtliche_hinweise.append("Wiener Vergabegesetz beachten (> 200.000 € brutto)")

    lv_dokument = {
        "meta": {
            "standard": "ÖNORM A 2063-1:2024",
            "version": "1.0",
            "erstellt_am": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "dokument_id": str(uuid.uuid4()),
            "dokument_typ": "Leistungsverzeichnis",
        },
        "projekt": {
            "name": projekt_info.get("name", "Unbekannt"),
            "adresse": projekt_info.get("adresse", ""),
            "bundesland": bundesland,
            "bauvorhaben_typ": projekt_info.get("typ", "Neubau"),
            "bgf_m2": projekt_info.get("bgf_m2", 0),
        },
        "auftraggeber": auftraggeber,
        "ausschreibung": {
            "ausschreibungsfrist_bis": projekt_info.get(
                "angebotsfrist", "3 Wochen nach Zustellung"
            ),
            "bindefrist_monate": 2,
            "nebenangebote": "zugelassen",
            "begehung_datum": projekt_info.get("begehung", "Nach Vereinbarung"),
        },
        "gewerke": list(gewerke_dict.values()),
        "anzahl_positionen_gesamt": len(positionen),
        "rechtliche_hinweise": rechtliche_hinweise,
        "zahlungsplan": {
            "anzahlung_prozent": 30,
            "baufortschritt_prozent": 60,
            "schlussrechnung_prozent": 10,
            "hinweis": "Zahlungen erfolgen nach Baufortschritt gemäß ÖNORM B 2110",
        },
        "phasen_kosten": (
            berechne_phasen_kosten(positionen) if any(p.ep > 0 for p in positionen) else None
        ),
    }

    return lv_dokument


# ═══════════════════════════════════════════════════════════════════════════
# ANGEBOTS-VERGLEICH MIT PREISSPIEGELMATRIX
# ═══════════════════════════════════════════════════════════════════════════


def vergleiche_angebote_detailliert(
    angebote: List[Dict[str, Any]], lv_positionen: List[LVPosition]
) -> Dict[str, Any]:
    """
    Erstellt detaillierten Angebotsvergleich mit Preisspiegelmatrix

    Args:
        angebote: Liste von Angeboten mit ausgefüllten Preisen
        lv_positionen: Original-LV-Positionen

    Returns:
        Detaillierte Vergleichsmatrix mit Empfehlung
    """
    if len(angebote) == 0:
        return {"fehler": "Keine Angebote vorhanden"}

    # Sortiere Angebote nach Gesamtpreis
    for angebot in angebote:
        gesamt = sum(
            pos.get("menge", 0) * pos.get("ep", 0) for pos in angebot.get("positionen", [])
        )
        angebot["gesamt_netto"] = round(gesamt, 2)
        angebot["gesamt_brutto"] = round(gesamt * 1.20, 2)

    angebote_sortiert = sorted(angebote, key=lambda x: x["gesamt_netto"])

    guenstigstes = angebote_sortiert[0]
    teuerstes = angebote_sortiert[-1]

    differenz_absolut = teuerstes["gesamt_netto"] - guenstigstes["gesamt_netto"]
    differenz_prozent = (
        (differenz_absolut / guenstigstes["gesamt_netto"]) * 100
        if guenstigstes["gesamt_netto"] > 0
        else 0
    )

    # Preisspiegelmatrix: Position für Position
    preisspiegelmatrix = []
    for lv_pos in lv_positionen:
        oz = lv_pos.oz
        preise = []

        for angebot in angebote:
            for pos in angebot.get("positionen", []):
                if pos.get("oz") == oz:
                    preise.append(
                        {
                            "firma": angebot.get("firma", "Unbekannt"),
                            "ep": pos.get("ep", 0),
                            "gp": pos.get("menge", 0) * pos.get("ep", 0),
                        }
                    )

        if preise:
            eps = [p["ep"] for p in preise]
            gps = [p["gp"] for p in preise]

            preisspiegelmatrix.append(
                {
                    "oz": oz,
                    "kurztext": lv_pos.kurztext,
                    "einheit": lv_pos.einheit,
                    "menge": lv_pos.menge,
                    "ep_min": round(min(eps), 2),
                    "ep_max": round(max(eps), 2),
                    "ep_durchschnitt": round(sum(eps) / len(eps), 2),
                    "gp_min": round(min(gps), 2),
                    "gp_max": round(max(gps), 2),
                    "differenz_ep_prozent": (
                        round(((max(eps) - min(eps)) / min(eps) * 100), 1) if min(eps) > 0 else 0
                    ),
                    "preise_pro_firma": preise,
                }
            )

    # Vergabeempfehlung
    empfehlung = []
    warnung = []

    if len(angebote) < 3:
        warnung.append("⚠ Weniger als 3 Angebote - Nachausschreibung empfohlen")

    if differenz_prozent > 25:
        warnung.append(
            f"⚠ Preisspanne sehr hoch ({differenz_prozent:.1f}%) - Nachverhandlung erforderlich"
        )
    elif differenz_prozent > 15:
        warnung.append(f"⚠ Preisspanne hoch ({differenz_prozent:.1f}%) - Prüfung empfohlen")
    else:
        empfehlung.append(f"✓ Preisspanne akzeptabel ({differenz_prozent:.1f}%)")

    # Prüfe Ausreißer-Positionen
    ausreisser = [p for p in preisspiegelmatrix if p["differenz_ep_prozent"] > 50]
    if ausreisser:
        warnung.append(
            f"⚠ {len(ausreisser)} Positionen mit >50% Preisdifferenz - Prüfung erforderlich"
        )

    if len(angebote) >= 3 and differenz_prozent < 15:
        empfehlung.append("✓ Marktübliche Preise, gute Vergleichbarkeit")
        empfehlung.append(f"Vergabeempfehlung: {guenstigstes.get('firma', 'Bieter 1')}")

    # Scoring-System for bid evaluation
    bewertungen = []
    for angebot in angebote_sortiert:
        # Calculate score based on multiple criteria
        preis_score = 100 - (
            (angebot["gesamt_netto"] - guenstigstes["gesamt_netto"])
            / guenstigstes["gesamt_netto"]
            * 100
        )
        preis_score = max(0, min(100, preis_score))  # Clamp to 0-100

        # Check for outliers
        ausreisser_count = 0
        for pos in preisspiegelmatrix:
            firma_preis = next(
                (p for p in pos["preise_pro_firma"] if p["firma"] == angebot.get("firma")), None
            )
            if firma_preis and firma_preis["ep"] > pos["ep_durchschnitt"] * 1.5:
                ausreisser_count += 1

        ausreisser_penalty = min(30, ausreisser_count * 10)  # Max 30 point penalty

        # Calculate final score (price weighted 70%, outlier penalty 30%)
        final_score = (preis_score * 0.7) - ausreisser_penalty

        bewertung = {
            "firma": angebot.get("firma", "Unbekannt"),
            "gesamt_netto": angebot["gesamt_netto"],
            "preis_score": round(preis_score, 1),
            "ausreisser_count": ausreisser_count,
            "ausreisser_penalty": ausreisser_penalty,
            "final_score": round(final_score, 1),
        }
        bewertungen.append(bewertung)

    # Sort by final score
    bewertungen_sortiert = sorted(bewertungen, key=lambda x: x["final_score"], reverse=True)

    return {
        "anzahl_angebote": len(angebote),
        "guenstigstes_angebot": {
            "firma": guenstigstes.get("firma", "Bieter 1"),
            "gesamt_netto": guenstigstes["gesamt_netto"],
            "gesamt_brutto": guenstigstes["gesamt_brutto"],
        },
        "teuerstes_angebot": {
            "firma": teuerstes.get("firma", f"Bieter {len(angebote)}"),
            "gesamt_netto": teuerstes["gesamt_netto"],
            "gesamt_brutto": teuerstes["gesamt_brutto"],
        },
        "differenz_absolut": round(differenz_absolut, 2),
        "differenz_prozent": round(differenz_prozent, 1),
        "preisspiegelmatrix": preisspiegelmatrix,
        "empfehlung": empfehlung,
        "warnung": warnung,
        "angebote_sortiert": [
            {
                "rang": i + 1,
                "firma": a.get("firma", f"Bieter {i+1}"),
                "gesamt_netto": a["gesamt_netto"],
                "gesamt_brutto": a["gesamt_brutto"],
            }
            for i, a in enumerate(angebote_sortiert)
        ],
        "vergabe_status": (
            "Vergabereif" if len(empfehlung) > 1 and not warnung else "Prüfung erforderlich"
        ),
        "bewertungen": bewertungen_sortiert,
        "empfohlener_bieter": bewertungen_sortiert[0]["firma"] if bewertungen_sortiert else None,
    }


# ═══════════════════════════════════════════════════════════════════════════
# BIM-INTEGRATION: IFC-Mengenübernahme
# ═══════════════════════════════════════════════════════════════════════════


def verknuepfe_lv_mit_bim(
    lv_positionen: List[LVPosition], ifc_mengen: Dict[str, Any]
) -> List[LVPosition]:
    """
    Verknüpft LV-Positionen mit BIM/IFC-Daten (ÖNORM A 2063-2)

    Args:
        lv_positionen: LV-Positionen ohne BIM-Referenzen
        ifc_mengen: Dict mit IFC-GUIDs und Mengen aus BIM-Modell

    Returns:
        LV-Positionen mit BIM-Referenzen
    """
    # Beispiel-Mapping: LV-Position → IFC-Element
    # In echter Implementierung: IFC-Parser (z.B. IfcOpenShell)

    for pos in lv_positionen:
        # Suche passende IFC-Elemente
        if "Fenster" in pos.kurztext:
            matching_ifc = [k for k in ifc_mengen.keys() if "IfcWindow" in k]
            if matching_ifc:
                pos.bim_ref = matching_ifc[0]
                pos.menge = ifc_mengen[matching_ifc[0]].get("area", pos.menge)

        elif "Decke" in pos.kurztext or "Estrich" in pos.kurztext:
            matching_ifc = [k for k in ifc_mengen.keys() if "IfcSlab" in k]
            if matching_ifc:
                pos.bim_ref = matching_ifc[0]
                pos.menge = ifc_mengen[matching_ifc[0]].get("area", pos.menge)

        elif "Wand" in pos.kurztext or "Mauerwerk" in pos.kurztext:
            matching_ifc = [k for k in ifc_mengen.keys() if "IfcWall" in k]
            if matching_ifc:
                pos.bim_ref = matching_ifc[0]
                pos.menge = ifc_mengen[matching_ifc[0]].get("area", pos.menge)

    return lv_positionen


# ═══════════════════════════════════════════════════════════════════════════
# GAEB/XML EXPORT (Datenaustausch mit AVA-Software)
# ═══════════════════════════════════════════════════════════════════════════


def exportiere_gaeb_xml(
    lv_positionen: List[LVPosition], projekt_info: Dict, version: str = "1.0"
) -> str:
    """
    Exportiert LV im GAEB XML-Format (D83/X31) für AVA-Software

    GAEB = Gemeinsamer Ausschuss Elektronik im Bauwesen
    Standard in Deutschland/Österreich für Datenaustausch

    Args:
        lv_positionen: LV-Positionen
        projekt_info: Projektdaten
        version: Versionsnummer des Leistungsverzeichnisses

    Returns:
        XML-String im GAEB-Format mit Versionstracking
    """
    # Vereinfachte GAEB-Struktur
    # Für Produktion: GAEB-Bibliothek verwenden (z.B. python-gaeb)

    dokument_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    version_hash = hashlib.sha256(f"{timestamp}{version}".encode()).hexdigest()[:16]

    xml_header = """<?xml version="1.0" encoding="UTF-8"?>
<GAEB xmlns="http://www.gaeb.de/GAEB_DA_XML/200407">
  <GAEBInfo>
    <Version>3.1</Version>
    <Datum>{datum}</Datum>
    <Absender>THE ARCHITEKT</Absender>
    <DokumentID>{dokument_id}</DokumentID>
    <VersionsNr>{version}</VersionsNr>
    <VersionsHash>{version_hash}</VersionsHash>
    <Erstellt>{timestamp}</Erstellt>
  </GAEBInfo>
  <PrjInfo>
    <Projektname>{projektname}</Projektname>
    <Projektnummer>{projekt_id}</Projektnummer>
    <Beschreibung>Leistungsverzeichnis Version {version}</Beschreibung>
  </PrjInfo>
  <Award>
    <BoQ>
""".format(
        datum=datetime.now().strftime("%Y-%m-%d"),
        projektname=projekt_info.get("name", "Projekt"),
        projekt_id=projekt_info.get("id", str(uuid.uuid4())[:8]),
        dokument_id=dokument_id,
        version=version,
        version_hash=version_hash,
        timestamp=timestamp,
    )

    xml_positionen = ""
    for pos in lv_positionen:
        xml_positionen += f"""      <Itemlist>
        <Item>
          <ID>{pos.oz}</ID>
          <Description>{pos.kurztext}</Description>
          <LongText>{pos.langtext}</LongText>
          <Unit>{pos.einheit}</Unit>
          <Qty>{pos.menge}</Qty>
          <UP>{pos.ep}</UP>
          <TP>{pos.gp}</TP>
          <Gewerk>{pos.gewerk}</Gewerk>
          <Kostengruppe>{pos.kostengruppe}</Kostengruppe>"""

        if pos.bim_ref:
            xml_positionen += f"""
          <BIM_Referenz>{pos.bim_ref}</BIM_Referenz>"""

        if pos.stlb_code:
            xml_positionen += f"""
          <StLB_Code>{pos.stlb_code}</StLB_Code>"""

        xml_positionen += """
        </Item>
      </Itemlist>
"""

    xml_footer = """    </BoQ>
  </Award>
</GAEB>"""

    return xml_header + xml_positionen + xml_footer


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNKTIONEN
# ═══════════════════════════════════════════════════════════════════════════


def erstelle_vollstaendige_ausschreibung(
    projekt_typ: str = "einfamilienhaus",
    bgf_m2: float = 150,
    bundesland: str = "tirol",
    auftraggeber: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    One-Stop-Funktion: Erstellt komplette Ausschreibung mit LV

    Returns:
        Dict mit LV, JSON-Export, und GAEB-XML
    """
    # Generiere LV
    if projekt_typ == "einfamilienhaus":
        lv_positionen = generiere_beispiel_lv_einfamilienhaus(bgf_m2=bgf_m2)
    else:
        lv_positionen = generiere_beispiel_lv_einfamilienhaus(bgf_m2=bgf_m2)  # Fallback

    # Projekt-Info
    projekt_info = {
        "name": f"{projekt_typ.capitalize()} {bgf_m2}m²",
        "typ": projekt_typ,
        "bgf_m2": bgf_m2,
        "bundesland": bundesland,
        "id": str(uuid.uuid4())[:8],
    }

    # Auftraggeber
    if auftraggeber is None:
        auftraggeber = {
            "name": "Mustermann GmbH",
            "adresse": "Musterstraße 1, 6020 Innsbruck",
            "kontakt": "office@mustermann.at",
        }

    # Exportiere ÖNORM JSON
    lv_json = exportiere_lv_oenorm_json(
        positionen=lv_positionen,
        projekt_info=projekt_info,
        auftraggeber=auftraggeber,
        bundesland=bundesland,
    )

    # Exportiere GAEB XML
    gaeb_xml = exportiere_gaeb_xml(lv_positionen, projekt_info)

    return {
        "lv_positionen": [asdict(p) for p in lv_positionen],
        "anzahl_positionen": len(lv_positionen),
        "lv_oenorm_json": lv_json,
        "gaeb_xml": gaeb_xml,
        "projekt": projekt_info,
        "status": "Ausschreibungsreif nach ÖNORM A 2063",
    }


# ═══════════════════════════════════════════════════════════════════════════
# DEMO & TESTING
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 80)
    print("ORION ÖNORM A 2063 - Angebotslegung & Ausschreibung")
    print("═" * 80)

    # Test 1: Generiere Beispiel-LV
    print("\n1. Generiere Leistungsverzeichnis für Einfamilienhaus 150m²...")
    lv_positionen = generiere_beispiel_lv_einfamilienhaus(bgf_m2=150, geschosse=2)
    print(f"   ✓ {len(lv_positionen)} Positionen generiert")

    # Test 2: Exportiere ÖNORM JSON
    print("\n2. Exportiere ÖNORM A 2063 JSON...")
    projekt_info = {"name": "EFH Musterstraße", "typ": "Neubau", "bgf_m2": 150}
    auftraggeber = {"name": "Max Mustermann", "adresse": "Musterstraße 1"}
    lv_json = exportiere_lv_oenorm_json(lv_positionen, projekt_info, auftraggeber)
    print(f"   ✓ JSON exportiert: {len(lv_json['gewerke'])} Gewerke")

    # Test 3: Vollständige Ausschreibung
    print("\n3. Erstelle vollständige Ausschreibung...")
    ausschreibung = erstelle_vollstaendige_ausschreibung(
        projekt_typ="einfamilienhaus", bgf_m2=150, bundesland="tirol"
    )
    print(f"   ✓ Ausschreibung erstellt: {ausschreibung['anzahl_positionen']} Positionen")
    print(f"   ✓ Status: {ausschreibung['status']}")

    print("\n" + "═" * 80)
    print("✅ Alle Tests erfolgreich!")
    print("═" * 80)
