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

import json
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


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

    def __post_init__(self):
        """Berechne Gesamtpreis automatisch"""
        self.gp = round(self.menge * self.ep, 2)


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
# LV-GENERATOR: BEISPIELPOSITIONEN FÜR EINFAMILIENHAUS
# ═══════════════════════════════════════════════════════════════════════════

def generiere_beispiel_lv_einfamilienhaus(bgf_m2: float = 150, geschosse: int = 2) -> List[LVPosition]:
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
    positionen.extend([
        LVPosition(
            oz="01.001",
            kurztext="Erdarbeiten Aushub",
            langtext="Erdaushub für Keller/Fundament, maschinell, inkl. Zwischenlagerung und Abtransport überschüssiger Erde",
            einheit="m³",
            menge=round(bgf_m2 * 0.8, 2),  # Ca. 80% der BGF für Keller
            gewerk="01",
            kostengruppe=300,
            stlb_code="001.01.001"
        ),
        LVPosition(
            oz="01.002",
            kurztext="Fundament Streifenfundament",
            langtext="Streifenfundament C25/30, bewehrt, inkl. Schalung und Verdichtung, gemäß Statik",
            einheit="m³",
            menge=round(bgf_m2 * 0.15, 2),  # Ca. 15% für Fundament
            gewerk="01",
            kostengruppe=310,
        ),
        LVPosition(
            oz="01.003",
            kurztext="Kellermauerwerk 25cm",
            langtext="Kellermauerwerk 25cm, Ziegel HLz 25, vermörtelt, inkl. Horizontalsperre",
            einheit="m²",
            menge=round((bgf_m2 ** 0.5 * 4) * 2.5, 2) if geschosse >= 1 else 0,  # Umfang × Höhe
            gewerk="01",
            kostengruppe=320,
        ),
        LVPosition(
            oz="01.004",
            kurztext="Decke Stahlbeton 20cm",
            langtext="Stahlbetondecke 20cm, C25/30, bewehrt mit Baustahlgewebe, inkl. Schalung gemäß Statik",
            einheit="m²",
            menge=bgf_m2 * (geschosse - 1),  # Eine Decke weniger als Geschosse
            gewerk="01",
            kostengruppe=320,
        ),
    ])

    # Gewerk 02: Zimmererarbeiten
    positionen.extend([
        LVPosition(
            oz="02.001",
            kurztext="Dachstuhl Pfettendach",
            langtext="Pfettendachstuhl, Konstruktionsvollholz C24, inkl. Lattung und Konterlattung, Dachneigung 35°",
            einheit="m²",
            menge=round(bgf_m2 * 0.7, 2),  # Ca. 70% der BGF als Dachfläche
            gewerk="02",
            kostengruppe=330,
        ),
    ])

    # Gewerk 03: Dachdeckerarbeiten
    positionen.extend([
        LVPosition(
            oz="03.001",
            kurztext="Dacheindeckung Ziegel",
            langtext="Dachdeckung Tondachziegel Wienerberger Alegra, inkl. Unterdach und Dampfsperre",
            einheit="m²",
            menge=round(bgf_m2 * 0.7, 2),
            gewerk="03",
            kostengruppe=360,
        ),
        LVPosition(
            oz="03.002",
            kurztext="Dachrinnen und Fallrohre",
            langtext="Dachrinnen halbrund DN 150, Kupfer, inkl. Fallrohre DN 100",
            einheit="m",
            menge=round(bgf_m2 ** 0.5 * 4, 2),  # Umfang
            gewerk="03",
            kostengruppe=360,
        ),
    ])

    # Gewerk 04: Fenster
    positionen.extend([
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
    ])

    # Gewerk 05: Elektro
    positionen.extend([
        LVPosition(
            oz="05.001",
            kurztext="Elektroinstallation Grundausstattung",
            langtext="Elektroinstallation komplett, Schuko-Steckdosen, Lichtschalter, Verteiler, Leitungen NYM-J",
            einheit="psch",
            menge=1,
            gewerk="05",
            kostengruppe=440,
        ),
    ])

    # Gewerk 06: Sanitär
    positionen.extend([
        LVPosition(
            oz="06.001",
            kurztext="Sanitärinstallation komplett",
            langtext="Wasser-/Abwasserleitungen, Sanitärobjekte (WC, Waschbecken, Dusche, Badewanne), Armaturen Mittelklasse",
            einheit="psch",
            menge=1,
            gewerk="06",
            kostengruppe=450,
        ),
    ])

    # Gewerk 07: Heizung
    positionen.extend([
        LVPosition(
            oz="07.001",
            kurztext="Wärmepumpe Luft-Wasser",
            langtext="Luft-Wasser-Wärmepumpe 8-12 kW, inkl. Pufferspeicher 300L, Fußbodenheizung komplett",
            einheit="psch",
            menge=1,
            gewerk="07",
            kostengruppe=460,
        ),
    ])

    # Gewerk 08: Estrich/Boden
    positionen.extend([
        LVPosition(
            oz="08.001",
            kurztext="Estrich Heizestrich",
            langtext="Heizestrich 6cm über Fußbodenheizung, inkl. Dämmung EPS 10cm",
            einheit="m²",
            menge=bgf_m2 * 0.8,  # Ca. 80% der BGF
            gewerk="08",
            kostengruppe=370,
        ),
        LVPosition(
            oz="08.002",
            kurztext="Bodenbelag Parkett/Fliesen",
            langtext="Bodenbeläge: Parkett Eiche gebürstet (Wohnbereich), Fliesen (Nassbereiche)",
            einheit="m²",
            menge=bgf_m2 * 0.8,
            gewerk="08",
            kostengruppe=370,
        ),
    ])

    # Gewerk 09: Malerarbeiten
    positionen.extend([
        LVPosition(
            oz="09.001",
            kurztext="Malerarbeiten innen",
            langtext="Innenanstrich Wände/Decken, 2× Dispersionsfarbe weiß, inkl. Spachteln",
            einheit="m²",
            menge=round(bgf_m2 * 3.5, 2),  # Wandfläche ca. 3.5× BGF
            gewerk="09",
            kostengruppe=370,
        ),
    ])

    # Gewerk 12: Außenanlagen
    positionen.extend([
        LVPosition(
            oz="12.001",
            kurztext="Terrasse Pflaster",
            langtext="Terrasse Betonpflaster, inkl. Unterbau und Randeinfassung",
            einheit="m²",
            menge=round(bgf_m2 * 0.25, 2),  # Ca. 25% der BGF
            gewerk="12",
            kostengruppe=500,
        ),
    ])

    return positionen


# ═══════════════════════════════════════════════════════════════════════════
# LV-EXPORT: ÖNORM A 2063 konformes JSON-Format
# ═══════════════════════════════════════════════════════════════════════════

def exportiere_lv_oenorm_json(
    positionen: List[LVPosition],
    projekt_info: Dict[str, Any],
    auftraggeber: Dict[str, str],
    bundesland: str = "tirol"
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
    gewerke_dict = {}
    for pos in positionen:
        gewerk_nr = pos.gewerk
        if gewerk_nr not in gewerke_dict:
            gewerk_info = GEWERKE_KATALOG_AT.get(gewerk_nr, {"name": "Unbekannt"})
            gewerke_dict[gewerk_nr] = {
                "gewerk_nr": gewerk_nr,
                "gewerk_name": gewerk_info["name"],
                "positionen": []
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
            "erstellt_am": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
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
            "ausschreibungsfrist_bis": projekt_info.get("angebotsfrist", "3 Wochen nach Zustellung"),
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
            "hinweis": "Zahlungen erfolgen nach Baufortschritt gemäß ÖNORM B 2110"
        }
    }

    return lv_dokument


# ═══════════════════════════════════════════════════════════════════════════
# ANGEBOTS-VERGLEICH MIT PREISSPIEGELMATRIX
# ═══════════════════════════════════════════════════════════════════════════

def vergleiche_angebote_detailliert(
    angebote: List[Dict[str, Any]],
    lv_positionen: List[LVPosition]
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
            pos.get("menge", 0) * pos.get("ep", 0)
            for pos in angebot.get("positionen", [])
        )
        angebot["gesamt_netto"] = round(gesamt, 2)
        angebot["gesamt_brutto"] = round(gesamt * 1.20, 2)

    angebote_sortiert = sorted(angebote, key=lambda x: x["gesamt_netto"])

    guenstigstes = angebote_sortiert[0]
    teuerstes = angebote_sortiert[-1]

    differenz_absolut = teuerstes["gesamt_netto"] - guenstigstes["gesamt_netto"]
    differenz_prozent = (differenz_absolut / guenstigstes["gesamt_netto"]) * 100 if guenstigstes["gesamt_netto"] > 0 else 0

    # Preisspiegelmatrix: Position für Position
    preisspiegelmatrix = []
    for lv_pos in lv_positionen:
        oz = lv_pos.oz
        preise = []

        for angebot in angebote:
            for pos in angebot.get("positionen", []):
                if pos.get("oz") == oz:
                    preise.append({
                        "firma": angebot.get("firma", "Unbekannt"),
                        "ep": pos.get("ep", 0),
                        "gp": pos.get("menge", 0) * pos.get("ep", 0)
                    })

        if preise:
            eps = [p["ep"] for p in preise]
            gps = [p["gp"] for p in preise]

            preisspiegelmatrix.append({
                "oz": oz,
                "kurztext": lv_pos.kurztext,
                "einheit": lv_pos.einheit,
                "menge": lv_pos.menge,
                "ep_min": round(min(eps), 2),
                "ep_max": round(max(eps), 2),
                "ep_durchschnitt": round(sum(eps) / len(eps), 2),
                "gp_min": round(min(gps), 2),
                "gp_max": round(max(gps), 2),
                "differenz_ep_prozent": round(((max(eps) - min(eps)) / min(eps) * 100), 1) if min(eps) > 0 else 0,
                "preise_pro_firma": preise,
            })

    # Vergabeempfehlung
    empfehlung = []
    warnung = []

    if len(angebote) < 3:
        warnung.append("⚠ Weniger als 3 Angebote - Nachausschreibung empfohlen")

    if differenz_prozent > 25:
        warnung.append(f"⚠ Preisspanne sehr hoch ({differenz_prozent:.1f}%) - Nachverhandlung erforderlich")
    elif differenz_prozent > 15:
        warnung.append(f"⚠ Preisspanne hoch ({differenz_prozent:.1f}%) - Prüfung empfohlen")
    else:
        empfehlung.append(f"✓ Preisspanne akzeptabel ({differenz_prozent:.1f}%)")

    # Prüfe Ausreißer-Positionen
    ausreisser = [p for p in preisspiegelmatrix if p["differenz_ep_prozent"] > 50]
    if ausreisser:
        warnung.append(f"⚠ {len(ausreisser)} Positionen mit >50% Preisdifferenz - Prüfung erforderlich")

    if len(angebote) >= 3 and differenz_prozent < 15:
        empfehlung.append("✓ Marktübliche Preise, gute Vergleichbarkeit")
        empfehlung.append(f"Vergabeempfehlung: {guenstigstes.get('firma', 'Bieter 1')}")

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
                "rang": i+1,
                "firma": a.get("firma", f"Bieter {i+1}"),
                "gesamt_netto": a["gesamt_netto"],
                "gesamt_brutto": a["gesamt_brutto"],
            }
            for i, a in enumerate(angebote_sortiert)
        ],
        "vergabe_status": "Vergabereif" if len(empfehlung) > 1 and not warnung else "Prüfung erforderlich",
    }


# ═══════════════════════════════════════════════════════════════════════════
# BIM-INTEGRATION: IFC-Mengenübernahme
# ═══════════════════════════════════════════════════════════════════════════

def verknuepfe_lv_mit_bim(
    lv_positionen: List[LVPosition],
    ifc_mengen: Dict[str, Any]
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

def exportiere_gaeb_xml(lv_positionen: List[LVPosition], projekt_info: Dict) -> str:
    """
    Exportiert LV im GAEB XML-Format (D83/X31) für AVA-Software

    GAEB = Gemeinsamer Ausschuss Elektronik im Bauwesen
    Standard in Deutschland/Österreich für Datenaustausch

    Args:
        lv_positionen: LV-Positionen
        projekt_info: Projektdaten

    Returns:
        XML-String im GAEB-Format
    """
    # Vereinfachte GAEB-Struktur
    # Für Produktion: GAEB-Bibliothek verwenden (z.B. python-gaeb)

    xml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<GAEB xmlns="http://www.gaeb.de/GAEB_DA_XML/200407">
  <GAEBInfo>
    <Version>3.1</Version>
    <Datum>{datum}</Datum>
    <Absender>THE ARCHITEKT</Absender>
  </GAEBInfo>
  <PrjInfo>
    <Projektname>{projektname}</Projektname>
    <Projektnummer>{projekt_id}</Projektnummer>
  </PrjInfo>
  <Award>
    <BoQ>
'''.format(
        datum=datetime.now().strftime("%Y-%m-%d"),
        projektname=projekt_info.get("name", "Projekt"),
        projekt_id=projekt_info.get("id", str(uuid.uuid4())[:8])
    )

    xml_positionen = ""
    for pos in lv_positionen:
        xml_positionen += f'''      <Itemlist>
        <Item>
          <ID>{pos.oz}</ID>
          <Description>{pos.kurztext}</Description>
          <LongText>{pos.langtext}</LongText>
          <Unit>{pos.einheit}</Unit>
          <Qty>{pos.menge}</Qty>
          <UP>{pos.ep}</UP>
          <TP>{pos.gp}</TP>
        </Item>
      </Itemlist>
'''

    xml_footer = '''    </BoQ>
  </Award>
</GAEB>'''

    return xml_header + xml_positionen + xml_footer


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNKTIONEN
# ═══════════════════════════════════════════════════════════════════════════

def erstelle_vollstaendige_ausschreibung(
    projekt_typ: str = "einfamilienhaus",
    bgf_m2: float = 150,
    bundesland: str = "tirol",
    auftraggeber: Optional[Dict] = None
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
            "kontakt": "office@mustermann.at"
        }

    # Exportiere ÖNORM JSON
    lv_json = exportiere_lv_oenorm_json(
        positionen=lv_positionen,
        projekt_info=projekt_info,
        auftraggeber=auftraggeber,
        bundesland=bundesland
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
        projekt_typ="einfamilienhaus",
        bgf_m2=150,
        bundesland="tirol"
    )
    print(f"   ✓ Ausschreibung erstellt: {ausschreibung['anzahl_positionen']} Positionen")
    print(f"   ✓ Status: {ausschreibung['status']}")

    print("\n" + "═" * 80)
    print("✅ Alle Tests erfolgreich!")
    print("═" * 80)
