"""
DDGK Normen-Verknuepfungs-Router
Automatische Verknuepfung kritischer Elemente mit ALLEN relevanten Normen.
Beispiel: Notstromaggregat -> OIB-RL 2 (Brandschutz) + EN 40 (Elektro) + EN 1992 (Fundament) + ...
"""

import os, sys, hashlib
from datetime import datetime
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/normen-verknuepfung", tags=["normen-verknuepfung"])

CRITICAL_ELEMENTS_DB = {
    "notstromaggregat": {
        "label": "Notstromaggregat",
        "risk_score": 4,
        "category": "electrical",
        "description": "Netzersatzanlage - Erfordert multiple Normen",
        "normen": [
            {"id": "OIB-RL 2", "name": "Brandschutz", "reason": "Brandgefahr durch Kraftstofflagerung + Abwaerme", "required": True, "pruefung": ["Abstandsflaechen nach OIB-RL 2 Z 3.2.4", "Brandlastberechnung fuer Aufstellraum", "Kraftstofflager > 200L => besondere Massnahmen"]},
            {"id": "EN 40", "name": "Elektrische Anlagen", "reason": "Norm fuer elektr. Einrichtungen von Beleuchtungsanlagen / Notstrom", "required": True, "pruefung": ["Netzumschaltung innerhalb 15s", "Erdungswiderstand < 10 Ohm", "Notbeleuchtung mindestens 1h"]},
            {"id": "EN 1992", "name": "Stahlbeton-Fundament", "reason": "Fundament fuer Aggregat muss Schwingungen aufnehmen", "required": True, "pruefung": ["Fundament mind. 2x Maschengewicht", "Bewehrung nach Eurocode 2", "Schwingungsisolierung nachweisen"]},
            {"id": "EN 1997", "name": "Geotechnik", "reason": "Baugrund fuer Fundament muss traegfahig sein", "required": False, "pruefung": ["Baugrundgutachten bei > 5t Fundament", "Setzungsrechnung nach EC7"]},
            {"id": "DIN 18531", "name": "Dachabdichtung", "reason": "Abluftfuehrung durch Dach => Abdichtung affected", "required": False, "pruefung": ["Dachdurchfuehrung Abdichtung pruefen", "Ablufttemperatur >= 200C => besondere Massnahmen"]},
            {"id": "OIB-RL 3", "name": "Hygiene/Gesundheit", "reason": "Abgasfuehrung (CO, NOx) muss Gebaeude nicht belasten", "required": True, "pruefung": ["Abgasfuehrung ueber Firsthoehe", "CO-Konzentration am Austritt < 10mg/m3"]},
            {"id": "OIB-RL 5", "name": "Schallschutz", "reason": "Notstromaggregat erzeugt Laerm > 65dB(A)", "required": True, "pruefung": ["Schallschutznachweis fuer Umgebung", "Sendezeiten nach TA Laerm", "Schallisolierung Aufstellraum"]},
        ],
    },
    "brandschutz": {
        "label": "Brandschutz",
        "risk_score": 4,
        "category": "safety",
        "description": "Brandschutz betrifft IMMER multiple Normen",
        "normen": [
            {"id": "OIB-RL 2", "name": "Brandschutz", "reason": "Primaere Brandschutz-Norm", "required": True, "pruefung": ["Fluchtwege mind. 1.20m breit", "Brandabschnitte max. 1600m2", "Feuerwiderstandsdauer REI 30-90 je Gebaeudeklasse"]},
            {"id": "EN 1991-1-2", "name": "Einwirkungen im Brandfall", "reason": "Bemessung fuer Brandsituation", "required": True, "pruefung": ["Brandlastberechnung", "Temperatur-Zeit-Kurve nach ETK"]},
            {"id": "EN 1992-1-2", "name": "Stahlbeton im Brandfall", "reason": "Tragfaehigkeit unter Brandeinfluss", "required": True, "pruefung": ["Betondeckung mind. 25mm", "Abplatzungen verhindern"]},
            {"id": "EN 1993-1-2", "name": "Stahlbau im Brandfall", "reason": "Stahl verliert Festigkeit bei Hitze", "required": True, "pruefung": ["Brandbekleidung fuer Stahlbauteile", "kritische Temperatur < 500C"]},
            {"id": "EN 1995-1-2", "name": "Holzbau im Brandfall", "reason": "Abbrandrate von Holz bemessen", "required": False, "pruefung": ["Verkaemmungsrate 0.65-0.80mm/min", "Nulllinie der Zonaehigkeit"]},
            {"id": "OIB-RL 5", "name": "Rauchschutz", "reason": "Rauchableitung und -schutz", "required": True, "pruefung": ["RWA-Anlage bei > 200m2", "Rauchschotten in Lueftungsanlagen"]},
        ],
    },
    "fundament": {
        "label": "Fundament",
        "risk_score": 3,
        "category": "structural",
        "description": "Fundament erfordert Geotechnik + Stahlbeton + Einwirkungen",
        "normen": [
            {"id": "EN 1997", "name": "Geotechnik", "reason": "Baugrund und Gruendung", "required": True, "pruefung": ["Gruendungssohle unter Frostgrenze (0.80m)", "Zulaessige Bodenpressung nach EC7", "Grundwasserabstand pruefen"]},
            {"id": "EN 1992", "name": "Stahlbeton", "reason": "Bemessung des Fundaments", "required": True, "pruefung": ["Bewehrungsgrad 0.1-1.5%", "Betondruckfestigkeit pruefen", "Durchstanznachweis bei Einzelfundament"]},
            {"id": "EN 1991", "name": "Einwirkungen", "reason": "Lastannahmen fuer Fundament", "required": True, "pruefung": ["Eigengewicht + Nutzlast + Wind + Schnee", "Teilsicherheitsbeiwerte gamma_G=1.35, gamma_Q=1.50"]},
            {"id": "EN 1998", "name": "Erdbeben", "reason": "Fundament muss Erdbeben standhalten", "required": False, "pruefung": ["Erdbebenzone Oesterreich pruefen", "Untergrundkategorie A-E"]},
            {"id": "OeNORM B 1991", "name": "Einwirkungen (Oesterreich)", "reason": "Oesterreich-spezifische Lastannahmen", "required": True, "pruefung": ["Schneelast nach Standort", "Windlast nach Gelaendekategorie"]},
        ],
    },
    "tragwerk": {
        "label": "Tragwerk",
        "risk_score": 4,
        "category": "structural",
        "description": "Tragendes System => Eurocodes 1-6",
        "normen": [
            {"id": "EN 1990", "name": "Grundlagen der Tragwerksplanung", "required": True, "reason": "Bemessungskonzepte und Kombinationsregeln", "pruefung": ["Gleichgewichtsnachweis EQU", "Tragfaehigkeit STR", "Gebrauchstauglichkeit SLS"]},
            {"id": "EN 1991", "name": "Einwirkungen", "required": True, "reason": "Alle Lasten auf Tragwerk", "pruefung": ["Eigengewicht", "Nutzlast", "Wind", "Schnee", "Temperatur"]},
            {"id": "EN 1992", "name": "Stahlbeton", "required": True, "reason": "Bemessung Stahlbetonbauteile", "pruefung": ["Biegebemessung", "Schubbemessung", "Rissbreitennachweis"]},
            {"id": "EN 1993", "name": "Stahlbau", "required": True, "reason": "Bemessung Stahllauteile", "pruefung": ["Querschnittsklasse", "Knicken", "Beulen"]},
            {"id": "EN 1995", "name": "Holzbau", "required": False, "reason": "Bemessung Holzbauteile", "pruefung": ["Biegung", "Schub", "Verformung"]},
            {"id": "EN 1998", "name": "Erdbeben", "required": False, "reason": "Erdbebenauslegung", "pruefung": ["Verhaltenbeiwert q", "Spektrum", "Drift-Nachweis"]},
            {"id": "OIB-RL 1", "name": "Tragfaehigkeit", "required": True, "reason": "OIB-Anforderungen an Tragwerk", "pruefung": ["Standfestigkeit", "Gebrauchstauglichkeit", "Dauerhaftigkeit"]},
        ],
    },
    "dach": {
        "label": "Dachkonstruktion",
        "risk_score": 3,
        "category": "structural",
        "description": "Dach => Abdichtung + Lasten + Brandschutz",
        "normen": [
            {"id": "DIN 18531", "name": "Dachabdichtung", "required": True, "reason": "Abdichtung von Dach und Waenden", "pruefung": ["Gefaelle mind. 2%", "Ueberstand mind. 150mm", "Schweissbahn-Verlegung"]},
            {"id": "OIB-RL 2", "name": "Brandschutz", "required": True, "reason": "Brandverhalten Dachhaut", "pruefung": ["Dachhaut Klasse BROof(t1)", "Durchsturzsicherung"]},
            {"id": "OIB-RL 6", "name": "Energie", "required": True, "reason": "Waermedaemmung Dach", "pruefung": ["U-Wert Dach <= 0.15 W/m2K", "Waermebrueckenfreiheit"]},
            {"id": "EN 1991-1-3", "name": "Schneelast", "required": True, "reason": "Schneelast am Dach", "pruefung": ["Schneezone Oesterreich", "Dachneigung", "Verwehungen"]},
            {"id": "EN 1991-1-4", "name": "Windlast", "required": True, "reason": "Windlast auf Dach (Sog/Druck)", "pruefung": ["Windzone", "Gelaendekategorie", "Dachneigung"]},
        ],
    },
    "erdung": {
        "label": "Erdung/Blitzschutz",
        "risk_score": 3,
        "category": "electrical",
        "description": "Erdung => Elektro + Fundament + Blitzschutz",
        "normen": [
            {"id": "EN 40", "name": "Elektrische Anlagen", "required": True, "reason": "Erdung elektrischer Anlagen", "pruefung": ["Erdungswiderstand < 10 Ohm", "Potenzialausgleich"]},
            {"id": "EN 62305", "name": "Blitzschutz", "required": True, "reason": "Blitzschutzanlage", "pruefung": ["Blitzschutzklasse I-IV", "Fangeinrichtungen", "Erdungssystem"]},
            {"id": "EN 1992", "name": "Stahlbeton-Fundament", "required": True, "reason": "Fundamenterder", "pruefung": ["Runder Stahl >= 10mm", "Verlegung in unterer Bewehrungslage"]},
            {"id": "OIB-RL 2", "name": "Brandschutz", "required": False, "reason": "Blitzschlag kann Brand ausloesen", "pruefung": ["Ueberspannungsschutz", "Blitzstromableitung"]},
        ],
    },
    "stahl": {
        "label": "Stahlkonstruktion",
        "risk_score": 3,
        "category": "structural",
        "description": "Stahlbau => EC3 + Brandschutz + Korrosion",
        "normen": [
            {"id": "EN 1993", "name": "Stahlbau", "required": True, "reason": "Bemessung von Stahlbauteilen", "pruefung": ["Querschnittsklasse 1-4", "Grenzzustand Tragfaehigkeit", "Grenzzustand Gebrauchstauglichkeit"]},
            {"id": "EN 1993-1-2", "name": "Stahlbau im Brandfall", "required": True, "reason": "Stahl verliert Festigkeit bei Hitze", "pruefung": ["Brandbekleidung", "kritische Temperatur 500C"]},
            {"id": "EN 1090", "name": "Ausfuehrung Stahlbau", "required": True, "reason": "Ausfuehrungsklasse EXC 1-4", "pruefung": ["EXC nach Gebaeudeklasse", "Schweissnahtqualitaet", "Oberflaechenschutz"]},
            {"id": "EN ISO 12944", "name": "Korrosionsschutz", "required": True, "reason": "Korrosionsschutzbeschichtung", "pruefung": ["Korrosivitaetskategorie C1-C5", "Beschichtungssystem"]},
        ],
    },
}


class NormenDetail(BaseModel):
    id: str
    name: str
    reason: str
    required: bool
    pruefung: list[str]


class CriticalElementResult(BaseModel):
    element: str
    label: str
    risk_score: int
    category: str
    description: str
    total_normen: int
    required_normen: int
    optional_normen: int
    normen: list[NormenDetail]
    audit_hash: str
    timestamp: str


class MultiElementResult(BaseModel):
    elements_found: list[str]
    total_risk_score: int
    all_normen: dict
    results: list[CriticalElementResult]
    hitl_required: bool
    timestamp: str


def lookup_critical_element(element_key: str) -> Optional[dict]:
    key_lower = element_key.lower()
    for key, data in CRITICAL_ELEMENTS_DB.items():
        if key in key_lower or key_lower in key:
            return {"key": key, "data": data}
    return None


def detect_critical_elements(text: str) -> list[dict]:
    text_lower = text.lower()
    found = []
    for key, data in CRITICAL_ELEMENTS_DB.items():
        if key in text_lower:
            found.append({"key": key, "data": data})
    return found


def get_element_with_normen(element_key: str) -> Optional[CriticalElementResult]:
    lookup = lookup_critical_element(element_key)
    if not lookup:
        return None
    key = lookup["key"]
    data = lookup["data"]
    normen = [NormenDetail(**n) for n in data["normen"]]
    required_count = sum(1 for n in normen if n.required)
    optional_count = len(normen) - required_count
    audit_hash = hashlib.sha256(f"{key}:{len(normen)}:{datetime.now().isoformat()}".encode()).hexdigest()[:16]
    return CriticalElementResult(
        element=key, label=data["label"], risk_score=data["risk_score"],
        category=data["category"], description=data["description"],
        total_normen=len(normen), required_normen=required_count,
        optional_normen=optional_count, normen=normen,
        audit_hash=audit_hash, timestamp=datetime.now().isoformat(),
    )


def multi_element_analysis(text: str) -> MultiElementResult:
    elements = detect_critical_elements(text)
    results = []
    all_normen: dict[str, list[str]] = {}
    total_risk = 0
    for elem in elements:
        result = get_element_with_normen(elem["key"])
        if result:
            results.append(result)
            total_risk += result.risk_score
            for norm in result.normen:
                if norm.id not in all_normen:
                    all_normen[norm.id] = []
                all_normen[norm.id].append(result.label)
    hitl_required = total_risk >= 6
    return MultiElementResult(
        elements_found=[r.element for r in results],
        total_risk_score=total_risk, all_normen=all_normen,
        results=results, hitl_required=hitl_required,
        timestamp=datetime.now().isoformat(),
    )


@router.get("/catalog")
async def get_catalog():
    catalog = []
    for key, data in CRITICAL_ELEMENTS_DB.items():
        catalog.append({"key": key, "label": data["label"], "risk_score": data["risk_score"], "category": data["category"], "normen_count": len(data["normen"])})
    return {"catalog": catalog, "total": len(catalog)}


@router.get("/element/{element_key}", response_model=CriticalElementResult)
async def get_element(element_key: str):
    result = get_element_with_normen(element_key)
    if not result:
        raise HTTPException(404, f"Element '{element_key}' nicht gefunden. Verfuegbar: {list(CRITICAL_ELEMENTS_DB.keys())}")
    return result


@router.post("/detect", response_model=MultiElementResult)
async def detect_elements(text: str):
    return multi_element_analysis(text)


@router.get("/norm/{norm_id}")
async def get_elements_by_norm(norm_id: str):
    affected = []
    for key, data in CRITICAL_ELEMENTS_DB.items():
        for norm in data["normen"]:
            if norm["id"].lower() == norm_id.lower() or norm_id.lower() in norm["id"].lower():
                affected.append({"element": key, "label": data["label"], "risk_score": data["risk_score"], "norm_reason": norm["reason"]})
    if not affected:
        raise HTTPException(404, f"Norm '{norm_id}' nicht im Mapping gefunden")
    return {"norm_id": norm_id, "affected_elements": affected, "count": len(affected)}


@router.get("/stats")
async def get_stats():
    norm_stats: dict[str, int] = {}
    for key, data in CRITICAL_ELEMENTS_DB.items():
        for norm in data["normen"]:
            norm_stats[norm["id"]] = norm_stats.get(norm["id"], 0) + 1
    sorted_stats = sorted(norm_stats.items(), key=lambda x: x[1], reverse=True)
    return {"normen_usage": [{"norm": k, "count": v} for k, v in sorted_stats], "elements_count": len(CRITICAL_ELEMENTS_DB), "total_normen_links": sum(norm_stats.values())}