"""
Building Calculations Router
U-Wert, Stellplätze, Flächenberechnung, etc.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

router = APIRouter()

# Models
class Schicht(BaseModel):
    """Layer in construction"""
    material: str
    dicke_mm: float = Field(..., gt=0)
    lambda_wert: float = Field(..., gt=0)

class UWertRequest(BaseModel):
    """U-value calculation request"""
    schichten: List[Schicht]
    innen_uebergang: float = Field(0.13, description="Internal heat transfer coefficient")
    aussen_uebergang: float = Field(0.04, description="External heat transfer coefficient")

class UWertResult(BaseModel):
    """U-value calculation result"""
    uwert: float
    gesamtdicke_mm: float
    r_gesamt: float
    oib_rl6_compliant: bool
    energy_class: str

class StellplatzRequest(BaseModel):
    """Parking space calculation request"""
    bundesland: str
    wohnungen: int = Field(..., gt=0)
    building_type: str = Field("mehrfamilienhaus")

class StellplatzResult(BaseModel):
    """Parking space calculation result"""
    required_stellplaetze: int
    factor: float
    bundesland: str
    regulation: str

class FlaecheRequest(BaseModel):
    """Area calculation request (ÖNORM B 1800)"""
    raumtyp: str
    laenge_m: float = Field(..., gt=0)
    breite_m: float = Field(..., gt=0)
    hoehe_m: float = Field(..., gt=0)

class FlaecheResult(BaseModel):
    """Area calculation result"""
    bgf_m2: float
    ngf_m2: float
    nrf_m2: float
    vgf_m2: float
    standard: str = "ÖNORM B 1800"

# Endpoints

@router.post("/uwert", response_model=UWertResult)
async def berechne_uwert(request: UWertRequest):
    """
    🌡️ **U-Wert Berechnung**

    Calculate thermal transmittance (U-value) for multi-layer construction.
    According to ÖNORM EN ISO 6946.

    U = 1 / R_total
    where R_total = R_si + Σ(d/λ) + R_se
    """
    # Calculate R-values
    r_innen = request.innen_uebergang
    r_aussen = request.aussen_uebergang

    r_schichten = sum(
        schicht.dicke_mm / 1000 / schicht.lambda_wert
        for schicht in request.schichten
    )

    r_gesamt = r_innen + r_schichten + r_aussen

    # Calculate U-value
    uwert = 1 / r_gesamt

    # Calculate total thickness
    gesamtdicke_mm = sum(schicht.dicke_mm for schicht in request.schichten)

    # Check OIB-RL 6 compliance (exterior wall: max 0.25 W/m2K)
    oib_rl6_compliant = uwert <= 0.25

    # Determine energy class
    if uwert <= 0.15:
        energy_class = "A+"
    elif uwert <= 0.20:
        energy_class = "A"
    elif uwert <= 0.25:
        energy_class = "B"
    else:
        energy_class = "C"

    return UWertResult(
        uwert=round(uwert, 3),
        gesamtdicke_mm=gesamtdicke_mm,
        r_gesamt=round(r_gesamt, 3),
        oib_rl6_compliant=oib_rl6_compliant,
        energy_class=energy_class
    )

@router.post("/stellplaetze", response_model=StellplatzResult)
async def berechne_stellplaetze(request: StellplatzRequest):
    """
    🚗 **Stellplatz-Berechnung**

    Calculate required parking spaces according to Bundesland building codes.

    Each Bundesland has different requirements:
    - Wien: 1.2 spaces per apartment
    - Tirol: 1.5 spaces per apartment
    - Salzburg: 1.3 spaces per apartment
    - etc.
    """
    # Stellplatz factors by Bundesland
    stellplatz_factors = {
        "wien": 1.2,
        "tirol": 1.5,
        "salzburg": 1.3,
        "vorarlberg": 1.4,
        "burgenland": 1.0,
        "kaernten": 1.2,
        "steiermark": 1.3,
        "oberoesterreich": 1.3,
        "niederoesterreich": 1.2
    }

    bundesland_lower = request.bundesland.lower()

    if bundesland_lower not in stellplatz_factors:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Bundesland: {request.bundesland}"
        )

    factor = stellplatz_factors[bundesland_lower]
    required = int(request.wohnungen * factor)

    return StellplatzResult(
        required_stellplaetze=required,
        factor=factor,
        bundesland=request.bundesland,
        regulation=f"{request.bundesland.title()} Bauordnung"
    )

@router.post("/flaeche", response_model=FlaecheResult)
async def berechne_flaeche(request: FlaecheRequest):
    """
    📐 **Flächenberechnung nach ÖNORM B 1800**

    Calculate building areas according to Austrian standard ÖNORM B 1800:
    - BGF: Brutto-Grundfläche (Gross floor area)
    - NGF: Netto-Grundfläche (Net floor area)
    - NRF: Nutz-Raumfläche (Usable room area)
    - VGF: Verkehrs-Grundfläche (Circulation area)
    """
    grundflaeche = request.laenge_m * request.breite_m

    # BGF = total gross area
    bgf_m2 = grundflaeche

    # NGF = BGF - construction area (approx 15%)
    ngf_m2 = bgf_m2 * 0.85

    # NRF = usable area (depends on room type, typically 70-75% of NGF)
    nrf_factor = 0.75 if request.raumtyp in ["wohnung", "buero"] else 0.70
    nrf_m2 = ngf_m2 * nrf_factor

    # VGF = circulation area (NGF - NRF)
    vgf_m2 = ngf_m2 - nrf_m2

    return FlaecheResult(
        bgf_m2=round(bgf_m2, 2),
        ngf_m2=round(ngf_m2, 2),
        nrf_m2=round(nrf_m2, 2),
        vgf_m2=round(vgf_m2, 2)
    )

@router.post("/barrierefreiheit-check")
async def check_barrierefreiheit(
    tuer_breite_cm: float,
    rampe_vorhanden: bool,
    rampe_steigung_prozent: Optional[float] = None,
    aufzug_vorhanden: bool = False,
    geschosse: int = 1
):
    """
    ♿ **Barrierefreiheit Check**

    Check accessibility requirements according to ÖNORM B 1600:
    - Door width minimum 90cm
    - Ramp maximum 6% slope
    - Elevator required for buildings with 4+ floors
    """
    mangel = []

    # Door width check
    if tuer_breite_cm < 90:
        mangel.append(f"Türbreite {tuer_breite_cm}cm zu gering (minimum: 90cm)")

    # Ramp check
    if rampe_vorhanden and rampe_steigung_prozent:
        if rampe_steigung_prozent > 6:
            mangel.append(f"Rampensteigung {rampe_steigung_prozent}% zu steil (maximum: 6%)")

    # Elevator check
    if geschosse >= 4 and not aufzug_vorhanden:
        mangel.append(f"Aufzug erforderlich bei {geschosse} Geschoßen")

    return {
        "compliant": len(mangel) == 0,
        "standard": "ÖNORM B 1600",
        "mangel": mangel,
        "status": "pass" if len(mangel) == 0 else "fail"
    }

@router.post("/fluchtweg-check")
async def check_fluchtweg(
    max_entfernung_m: float,
    treppenhaus_breite_m: float,
    geschosse: int,
    gebaudetyp: str = "wohngebaeude"
):
    """
    🚨 **Fluchtweg Check**

    Check emergency exit requirements according to OIB-RL 4:
    - Maximum distance to exit: 40m (residential)
    - Stairway minimum width: 1.20m
    - Additional requirements for high-rise buildings
    """
    mangel = []
    warnings = []

    # Distance check
    max_allowed = 40 if gebaudetyp == "wohngebaeude" else 35
    if max_entfernung_m > max_allowed:
        mangel.append(f"Fluchtweg {max_entfernung_m}m zu lang (maximum: {max_allowed}m)")

    # Stairway width check
    min_breite = 1.20 if geschosse >= 4 else 1.00
    if treppenhaus_breite_m < min_breite:
        mangel.append(f"Treppenhaus {treppenhaus_breite_m}m zu schmal (minimum: {min_breite}m)")
    elif treppenhaus_breite_m < min_breite + 0.1:
        warnings.append(f"Treppenhaus {treppenhaus_breite_m}m knapp bemessen (empfohlen: >{min_breite}m)")

    # High-rise requirements
    if geschosse >= 5:
        warnings.append("Hochhaus-Anforderungen prüfen: zweiter Fluchtweg, Feuerwehraufzug")

    return {
        "compliant": len(mangel) == 0,
        "standard": "OIB-RL 4",
        "mangel": mangel,
        "warnings": warnings,
        "status": "pass" if len(mangel) == 0 else ("warning" if len(warnings) > 0 else "fail")
    }

@router.post("/schallschutz-berechnung")
async def berechne_schallschutz(
    wandaufbau: List[Schicht],
    gebaudetyp: str = "mehrfamilienhaus"
):
    """
    🔊 **Schallschutz-Berechnung**

    Calculate sound insulation according to ÖNORM B 8115-2:
    - Residential buildings: minimum R'w = 52 dB
    - Between apartments: minimum R'w = 55 dB
    """
    # Simplified calculation - real version would use more complex algorithm
    # Sound reduction index increases with mass
    gesamtmasse_kg_m2 = sum(
        schicht.dicke_mm / 1000 * 2000  # Simplified: assuming 2000 kg/m3 average density
        for schicht in wandaufbau
    )

    # Simplified mass law: R = 20*log10(m*f) - 47
    # Using reference frequency 500 Hz
    rw_estimated = 20 * (gesamtmasse_kg_m2 ** 0.5)  # Simplified

    # Requirements
    required_rw = 55 if gebaudetyp == "mehrfamilienhaus" else 52

    return {
        "rw_estimated": round(rw_estimated, 1),
        "required_rw": required_rw,
        "compliant": rw_estimated >= required_rw,
        "standard": "ÖNORM B 8115-2",
        "wandmasse_kg_m2": round(gesamtmasse_kg_m2, 1),
        "status": "pass" if rw_estimated >= required_rw else "fail"
    }

@router.post("/heizlast-berechnung")
async def berechne_heizlast(
    bgf_m2: float,
    uwert_wand: float,
    uwert_dach: float,
    uwert_fenster: float,
    bundesland: str = "wien"
):
    """
    🔥 **Heizlast-Berechnung**

    Calculate heating load according to ÖNORM EN 12831:
    - Transmission losses
    - Ventilation losses
    - Climate zone factors
    """
    # Climate factors by Bundesland (simplified)
    klima_faktoren = {
        "wien": 1.0,
        "tirol": 1.2,
        "salzburg": 1.15,
        "vorarlberg": 1.15,
        "kaernten": 1.1,
        "steiermark": 1.05,
        "oberoesterreich": 1.05,
        "niederoesterreich": 0.95,
        "burgenland": 0.9
    }

    klima_faktor = klima_faktoren.get(bundesland.lower(), 1.0)

    # Simplified calculation
    # Transmission losses: Q_T = A * U * ΔT
    delta_t = 25  # Temperature difference (20°C inside - (-5°C) outside)

    q_wand = bgf_m2 * 3 * uwert_wand * delta_t  # Assuming 3x wall area
    q_dach = bgf_m2 * uwert_dach * delta_t
    q_fenster = bgf_m2 * 0.3 * uwert_fenster * delta_t  # 30% window area

    q_transmission = (q_wand + q_dach + q_fenster) * klima_faktor

    # Ventilation losses: Q_V = V * ρ * c * n * ΔT
    volumen = bgf_m2 * 2.7  # 2.7m ceiling height
    q_ventilation = volumen * 0.34 * 0.5 * delta_t  # 0.5 air changes/hour

    heizlast_gesamt = q_transmission + q_ventilation

    # Specific heating load
    spezifische_heizlast = heizlast_gesamt / bgf_m2

    return {
        "heizlast_gesamt_w": round(heizlast_gesamt, 0),
        "spezifische_heizlast_w_m2": round(spezifische_heizlast, 1),
        "q_transmission_w": round(q_transmission, 0),
        "q_ventilation_w": round(q_ventilation, 0),
        "klima_faktor": klima_faktor,
        "bundesland": bundesland,
        "standard": "ÖNORM EN 12831"
    }

@router.get("/materialdatenbank")
async def get_materialdatenbank(material_typ: Optional[str] = None):
    """
    📚 **Materialdatenbank**

    Get standard building materials with thermal properties.
    Based on ÖNORM standards and manufacturer data.
    """
    materials = [
        {"name": "Beton C30/37", "lambda": 2.3, "dichte": 2400, "kategorie": "Tragkonstruktion"},
        {"name": "Ziegel 25cm", "lambda": 0.65, "dichte": 1600, "kategorie": "Mauerwerk"},
        {"name": "EPS Dämmung", "lambda": 0.035, "dichte": 20, "kategorie": "Dämmung"},
        {"name": "Mineralwolle", "lambda": 0.035, "dichte": 50, "kategorie": "Dämmung"},
        {"name": "Holz (Fichte)", "lambda": 0.13, "dichte": 450, "kategorie": "Tragkonstruktion"},
        {"name": "Gipskarton", "lambda": 0.21, "dichte": 750, "kategorie": "Ausbau"},
        {"name": "Kalkzementputz", "lambda": 0.70, "dichte": 1600, "kategorie": "Oberfläche"},
        {"name": "3-fach Verglasung", "lambda": 0.7, "dichte": 2500, "kategorie": "Fenster"},
    ]

    if material_typ:
        materials = [m for m in materials if m["kategorie"].lower() == material_typ.lower()]

    return {"materials": materials, "total": len(materials)}
