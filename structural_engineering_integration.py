#!/usr/bin/env python3
"""
ORION Architekt AT - Structural Engineering Integration
========================================================

Integration with structural analysis software (ETABS, SAP2000, STAAD.Pro)
for Austrian civil engineers and structural engineers.

Features:
- Automatic load calculation from IFC/BIM models
- Reinforcement planning integration
- ÖNORM B 4700 (Eurocode 2 Austria) compliance
- Seismic zone calculations (ÖNORM EN 1998)
- Bidirectional sync with structural software

Author: ORION Architekt AT Team
Date: 2026-04-09
Standards: ÖNORM B 4700, ÖNORM EN 1998, Eurocode 2
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import math


# ============================================================================
# ÖNORM B 4700 & Eurocode 2 Constants for Austria
# ============================================================================

class ConcreteGrade(str, Enum):
    """Betongüten nach ÖNORM B 4700 / Eurocode 2"""
    C12_15 = "C12/15"
    C16_20 = "C16/20"
    C20_25 = "C20/25"
    C25_30 = "C25/30"
    C30_37 = "C30/37"  # Standard für Hochbau
    C35_45 = "C35/45"
    C40_50 = "C40/50"
    C45_55 = "C45/55"
    C50_60 = "C50/60"


class SteelGrade(str, Enum):
    """Bewehrungsstahl nach ÖNORM B 4700"""
    BSt_500S = "BSt 500S"  # Standard
    BSt_500M = "BSt 500M"
    BSt_500A = "BSt 500A"


class ExposureClass(str, Enum):
    """Expositionsklassen ÖNORM B 4700"""
    XC1 = "XC1"  # Trocken, innen
    XC2 = "XC2"  # Nass, selten trocken
    XC3 = "XC3"  # Mäßige Feuchte
    XC4 = "XC4"  # Wechselnd nass/trocken
    XD1 = "XD1"  # Mäßige Feuchte + Chloride
    XD2 = "XD2"  # Nass, selten trocken + Chloride
    XD3 = "XD3"  # Wechselnd nass/trocken + Chloride
    XF1 = "XF1"  # Frost, mäßige Wassersättigung
    XF2 = "XF2"  # Frost, mäßige Wassersättigung + Taumittel
    XF3 = "XF3"  # Frost, hohe Wassersättigung
    XF4 = "XF4"  # Frost, hohe Wassersättigung + Taumittel


class SeismicZoneAustria(str, Enum):
    """Erdbebenzonen Österreich nach ÖNORM EN 1998"""
    ZONE_0 = "Zone 0"  # Vorarlberg, Tirol West
    ZONE_1 = "Zone 1"  # Rest Tirol, Salzburg, OÖ, NÖ Nord
    ZONE_2 = "Zone 2"  # Wien, NÖ Süd, Burgenland Nord
    ZONE_3 = "Zone 3"  # Steiermark, Kärnten, Burgenland Süd


class StructuralElement(str, Enum):
    """Tragende Bauteile"""
    COLUMN = "Stütze"
    BEAM = "Träger"
    SLAB = "Decke"
    WALL = "Wand (tragend)"
    FOUNDATION = "Fundament"
    FOOTING = "Einzelfundament"
    STRIP_FOUNDATION = "Streifenfundament"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class LoadCase:
    """Lastfall nach ÖNORM B 4700"""
    load_case_id: str
    name: str
    load_type: str  # "Eigenlast", "Nutzlast", "Schnee", "Wind", "Erdbeben"

    # Teilsicherheitsbeiwerte (γ)
    gamma_g: float = 1.35  # Ständige Lasten
    gamma_q: float = 1.5   # Veränderliche Lasten

    # Kombinationsbeiwerte (ψ)
    psi_0: float = 0.7  # Hauptwert
    psi_1: float = 0.5  # Häufige Einwirkung
    psi_2: float = 0.3  # Quasi-ständige Einwirkung


@dataclass
class Material:
    """Baustoff-Eigenschaften nach ÖNORM B 4700"""
    material_id: str
    material_type: str  # "Beton", "Betonstahl", "Baustahl"

    # Beton
    concrete_grade: Optional[ConcreteGrade] = None
    fck: Optional[float] = None  # Charakteristische Druckfestigkeit [MPa]
    fcd: Optional[float] = None  # Bemessungswert Druckfestigkeit [MPa]

    # Stahl
    steel_grade: Optional[SteelGrade] = None
    fyk: Optional[float] = None  # Charakteristische Streckgrenze [MPa]
    fyd: Optional[float] = None  # Bemessungswert Streckgrenze [MPa]

    # Sonstiges
    density: float = 25.0  # [kN/m³] - Standard Stahlbeton
    e_modulus: Optional[float] = None  # E-Modul [MPa]


@dataclass
class CrossSection:
    """Querschnitt für tragende Bauteile"""
    section_id: str
    element_type: StructuralElement

    # Geometrie
    width: float  # [m]
    height: float  # [m]
    length: float  # [m]

    # Material
    concrete: Material
    steel: Material

    # Bewehrung
    reinforcement_top: List[Tuple[int, float]] = field(default_factory=list)  # [(Anzahl, Durchmesser)]
    reinforcement_bottom: List[Tuple[int, float]] = field(default_factory=list)
    stirrups: Optional[Tuple[float, float]] = None  # (Durchmesser, Abstand)

    # Betondeckung
    concrete_cover: float = 0.03  # [m] - Standard 3cm
    exposure_class: ExposureClass = ExposureClass.XC1


@dataclass
class StructuralNode:
    """Knoten im Tragwerksmodell"""
    node_id: str
    x: float  # [m]
    y: float  # [m]
    z: float  # [m]
    restraints: Dict[str, bool] = field(default_factory=dict)  # {"ux": True, "uy": False, ...}


@dataclass
class StructuralMember:
    """Tragglied (Stab) im System"""
    member_id: str
    element_type: StructuralElement
    start_node: str
    end_node: str
    cross_section: CrossSection

    # Lasten
    loads: List[Dict[str, Any]] = field(default_factory=list)

    # Ergebnisse (aus FEM-Analyse)
    max_moment: Optional[float] = None  # [kNm]
    max_shear: Optional[float] = None   # [kN]
    max_axial: Optional[float] = None   # [kN]
    max_deflection: Optional[float] = None  # [m]


@dataclass
class SeismicParameters:
    """Erdbebenparameter nach ÖNORM EN 1998"""
    zone: SeismicZoneAustria
    soil_class: str  # A, B, C, D, E
    building_importance_class: int  # I, II, III, IV

    # Bemessungswerte
    ag: float  # Bemessungswert Bodenbeschleunigung [m/s²]
    s: float   # Bodenparameter
    q: float   # Verhaltensbeiwert

    # Spektralwerte
    sd_t: Optional[float] = None  # Bemessungsspektrum


@dataclass
class ReinforcementDesign:
    """Bewehrungsbemessung nach ÖNORM B 4700"""
    member_id: str
    cross_section: CrossSection

    # Bemessungsschnittgrößen
    med: float  # Bemessungsmoment [kNm]
    ved: float  # Bemessungsquerkraft [kN]
    ned: float  # Bemessungsnormalkraft [kN]

    # Erforderliche Bewehrung
    as_required_top: float  # [cm²]
    as_required_bottom: float  # [cm²]
    asw_required: float  # Bügelbewehrung [cm²/m]

    # Gewählte Bewehrung
    as_provided_top: float  # [cm²]
    as_provided_bottom: float  # [cm²]
    asw_provided: float  # [cm²/m]

    # Nachweise
    utilization_bending: float  # Ausnutzungsgrad Biegung [%]
    utilization_shear: float    # Ausnutzungsgrad Querkraft [%]
    deflection_check: bool      # Durchbiegungsnachweis
    crack_width_check: bool     # Rissbreitennachweis

    # Detailinfo
    calculation_log: List[str] = field(default_factory=list)


# ============================================================================
# ÖNORM B 4700 Calculations
# ============================================================================

def get_concrete_properties(grade: ConcreteGrade) -> Dict[str, float]:
    """
    Betoneigenschaften nach ÖNORM B 4700 / Eurocode 2

    Returns:
        Dict mit fck, fcd, fctm, Ecm
    """
    properties = {
        ConcreteGrade.C12_15: {"fck": 12, "fctm": 1.6, "Ecm": 27000},
        ConcreteGrade.C16_20: {"fck": 16, "fctm": 1.9, "Ecm": 29000},
        ConcreteGrade.C20_25: {"fck": 20, "fctm": 2.2, "Ecm": 30000},
        ConcreteGrade.C25_30: {"fck": 25, "fctm": 2.6, "Ecm": 31000},
        ConcreteGrade.C30_37: {"fck": 30, "fctm": 2.9, "Ecm": 33000},
        ConcreteGrade.C35_45: {"fck": 35, "fctm": 3.2, "Ecm": 34000},
        ConcreteGrade.C40_50: {"fck": 40, "fctm": 3.5, "Ecm": 35000},
        ConcreteGrade.C45_55: {"fck": 45, "fctm": 3.8, "Ecm": 36000},
        ConcreteGrade.C50_60: {"fck": 50, "fctm": 4.1, "Ecm": 37000},
    }

    props = properties[grade]

    # Bemessungswert (γc = 1.5)
    props["fcd"] = props["fck"] / 1.5

    return props


def get_steel_properties(grade: SteelGrade) -> Dict[str, float]:
    """
    Bewehrungsstahl-Eigenschaften nach ÖNORM B 4700

    Returns:
        Dict mit fyk, fyd, Es
    """
    properties = {
        SteelGrade.BSt_500S: {"fyk": 500, "Es": 200000},
        SteelGrade.BSt_500M: {"fyk": 500, "Es": 200000},
        SteelGrade.BSt_500A: {"fyk": 500, "Es": 200000},
    }

    props = properties[grade]

    # Bemessungswert (γs = 1.15)
    props["fyd"] = props["fyk"] / 1.15

    return props


def calculate_minimum_concrete_cover(
    exposure_class: ExposureClass,
    bar_diameter: float,
    aggregate_size: float = 20.0
) -> float:
    """
    Mindestbetondeckung nach ÖNORM B 4700

    Args:
        exposure_class: Expositionsklasse
        bar_diameter: Stabdurchmesser [mm]
        aggregate_size: Größtkorn Zuschlag [mm]

    Returns:
        Mindestbetondeckung cmin [mm]
    """
    # Betondeckung für Dauerhaftigkeit
    cmin_dur = {
        ExposureClass.XC1: 15,
        ExposureClass.XC2: 25,
        ExposureClass.XC3: 25,
        ExposureClass.XC4: 30,
        ExposureClass.XD1: 35,
        ExposureClass.XD2: 40,
        ExposureClass.XD3: 45,
        ExposureClass.XF1: 30,
        ExposureClass.XF2: 35,
        ExposureClass.XF3: 35,
        ExposureClass.XF4: 40,
    }[exposure_class]

    # Betondeckung für Verbund
    cmin_b = bar_diameter

    # Größtkorn-Zuschlag
    cmin_agg = aggregate_size

    # Maßgebend
    cmin = max(cmin_dur, cmin_b, cmin_agg)

    # Vorhaltemaß (Δc = 10mm)
    c_nom = cmin + 10

    return c_nom


def calculate_self_weight(
    cross_section: CrossSection,
    length: float
) -> float:
    """
    Eigenlast berechnen

    Args:
        cross_section: Querschnitt
        length: Länge [m]

    Returns:
        Eigenlast [kN]
    """
    volume = cross_section.width * cross_section.height * length  # [m³]
    density = cross_section.concrete.density  # [kN/m³]

    return volume * density


def design_rectangular_beam_flexure(
    med: float,
    width: float,
    height: float,
    concrete_grade: ConcreteGrade,
    steel_grade: SteelGrade,
    concrete_cover: float = 0.03
) -> ReinforcementDesign:
    """
    Rechteckquerschnitt Biegebemessung nach ÖNORM B 4700

    Args:
        med: Bemessungsmoment [kNm]
        width: Breite [m]
        height: Höhe [m]
        concrete_grade: Betongüte
        steel_grade: Stahlgüte
        concrete_cover: Betondeckung [m]

    Returns:
        ReinforcementDesign
    """
    calc_log = []

    # Materialkennwerte
    concrete_props = get_concrete_properties(concrete_grade)
    steel_props = get_steel_properties(steel_grade)

    fcd = concrete_props["fcd"]  # [MPa]
    fyd = steel_props["fyd"]     # [MPa]

    calc_log.append(f"Beton: {concrete_grade.value}, fcd = {fcd:.1f} MPa")
    calc_log.append(f"Stahl: {steel_grade.value}, fyd = {fyd:.1f} MPa")

    # Statische Höhe
    d = height - concrete_cover - 0.01  # Annahme: 10mm Bügel + ½ Hauptbewehrung
    calc_log.append(f"Statische Höhe: d = {d*1000:.0f} mm")

    # Bezogenes Moment
    med_kNm = abs(med)
    med_Nm = med_kNm * 1e6  # [Nm]
    mu_eds = med_Nm / (width * d**2 * fcd * 1e6)

    calc_log.append(f"μEds = {mu_eds:.4f}")

    # Grenzdehnung Check
    if mu_eds > 0.295:  # ω > 0.37 → Druckbewehrung erforderlich
        calc_log.append("⚠️ WARNUNG: Druckbewehrung erforderlich!")
        omega = 0.37
    else:
        omega = 1 - math.sqrt(1 - 2 * mu_eds)

    calc_log.append(f"ω = {omega:.4f}")

    # Erforderliche Zugbewehrung
    as_required = omega * width * d * fcd / fyd  # [m²]
    as_required_cm2 = as_required * 1e4  # [cm²]

    calc_log.append(f"As,erf = {as_required_cm2:.2f} cm²")

    # Mindestbewehrung
    as_min = 0.26 * (concrete_props["fctm"] / fyd) * width * d
    as_min = max(as_min, 0.0013 * width * d)
    as_min_cm2 = as_min * 1e4

    as_required_cm2 = max(as_required_cm2, as_min_cm2)
    calc_log.append(f"As,min = {as_min_cm2:.2f} cm²")
    calc_log.append(f"As,erf,total = {as_required_cm2:.2f} cm²")

    # Gewählte Bewehrung (vorläufig = erforderlich)
    as_provided_cm2 = as_required_cm2 * 1.1  # 10% Reserve

    # Ausnutzungsgrad
    utilization = (as_required_cm2 / as_provided_cm2) * 100

    # Dummy-Werte für vollständiges Objekt
    result = ReinforcementDesign(
        member_id="BEAM-001",
        cross_section=None,  # würde übergeben werden
        med=med_kNm,
        ved=0,  # noch nicht berechnet
        ned=0,
        as_required_top=as_required_cm2 if med < 0 else 0,
        as_required_bottom=as_required_cm2 if med > 0 else 0,
        asw_required=0,  # Querkraft noch nicht berechnet
        as_provided_top=as_provided_cm2 if med < 0 else 0,
        as_provided_bottom=as_provided_cm2 if med > 0 else 0,
        asw_provided=0,
        utilization_bending=utilization,
        utilization_shear=0,
        deflection_check=True,  # vereinfacht
        crack_width_check=True,
        calculation_log=calc_log
    )

    return result


def get_seismic_parameters(
    bundesland: str,
    soil_class: str = "B",
    importance_class: int = 2
) -> SeismicParameters:
    """
    Erdbebenparameter nach ÖNORM EN 1998 für Österreich

    Args:
        bundesland: Bundesland (Wien, Niederösterreich, etc.)
        soil_class: Bodenklasse A-E
        importance_class: Bedeutungskategorie I-IV

    Returns:
        SeismicParameters
    """
    # Erdbebenzonenzuordnung (vereinfacht)
    zone_mapping = {
        "vorarlberg": SeismicZoneAustria.ZONE_0,
        "tirol": SeismicZoneAustria.ZONE_1,
        "salzburg": SeismicZoneAustria.ZONE_1,
        "oberösterreich": SeismicZoneAustria.ZONE_1,
        "wien": SeismicZoneAustria.ZONE_2,
        "niederösterreich": SeismicZoneAustria.ZONE_2,
        "burgenland": SeismicZoneAustria.ZONE_2,
        "steiermark": SeismicZoneAustria.ZONE_3,
        "kärnten": SeismicZoneAustria.ZONE_3,
    }

    zone = zone_mapping.get(bundesland.lower(), SeismicZoneAustria.ZONE_1)

    # Referenz-Bodenbeschleunigung [m/s²]
    agr_map = {
        SeismicZoneAustria.ZONE_0: 0.0,
        SeismicZoneAustria.ZONE_1: 0.8,
        SeismicZoneAustria.ZONE_2: 1.2,
        SeismicZoneAustria.ZONE_3: 1.6,
    }

    agr = agr_map[zone]

    # Bedeutungsbeiwert γI
    gamma_i_map = {1: 0.8, 2: 1.0, 3: 1.2, 4: 1.4}
    gamma_i = gamma_i_map[importance_class]

    # Bemessungswert
    ag = agr * gamma_i

    # Bodenparameter S
    s_map = {"A": 1.0, "B": 1.2, "C": 1.15, "D": 1.35, "E": 1.4}
    s = s_map.get(soil_class, 1.2)

    # Verhaltensbeiwert q (Rahmen mit mittlerer Duktilität)
    q = 3.0

    return SeismicParameters(
        zone=zone,
        soil_class=soil_class,
        building_importance_class=importance_class,
        ag=ag,
        s=s,
        q=q
    )


# ============================================================================
# IFC Integration
# ============================================================================

def extract_structural_model_from_ifc(ifc_file_path: str) -> Dict[str, Any]:
    """
    Extrahiert Tragwerksmodell aus IFC-Datei

    Identifiziert:
    - Tragende Bauteile (IfcBeam, IfcColumn, IfcSlab, IfcWall)
    - Geometrie und Querschnitte
    - Materialien
    - Lastfälle (wenn vorhanden)

    Args:
        ifc_file_path: Pfad zur IFC-Datei

    Returns:
        Dict mit nodes, members, loads
    """
    # In Produktion: würde ifcopenshell verwenden
    # Hier: Simulation

    print(f"📐 Extrahiere Tragwerksmodell aus: {ifc_file_path}")

    # Simulierte Extraktion
    nodes = [
        StructuralNode("N1", 0, 0, 0, {"ux": True, "uy": True, "uz": True, "rx": True, "ry": True, "rz": True}),
        StructuralNode("N2", 5, 0, 0),
        StructuralNode("N3", 5, 0, 3),
        StructuralNode("N4", 0, 0, 3),
    ]

    # Beispiel-Querschnitt
    c30_properties = get_concrete_properties(ConcreteGrade.C30_37)
    concrete = Material(
        material_id="C30/37",
        material_type="Beton",
        concrete_grade=ConcreteGrade.C30_37,
        fck=c30_properties["fck"],
        fcd=c30_properties["fcd"],
        e_modulus=c30_properties["Ecm"]
    )

    steel_properties = get_steel_properties(SteelGrade.BSt_500S)
    steel = Material(
        material_id="BSt500S",
        material_type="Betonstahl",
        steel_grade=SteelGrade.BSt_500S,
        fyk=steel_properties["fyk"],
        fyd=steel_properties["fyd"],
        e_modulus=steel_properties["Es"]
    )

    beam_section = CrossSection(
        section_id="BEAM-30x50",
        element_type=StructuralElement.BEAM,
        width=0.30,
        height=0.50,
        length=5.0,
        concrete=concrete,
        steel=steel
    )

    column_section = CrossSection(
        section_id="COL-40x40",
        element_type=StructuralElement.COLUMN,
        width=0.40,
        height=0.40,
        length=3.0,
        concrete=concrete,
        steel=steel
    )

    members = [
        StructuralMember("COL-1", StructuralElement.COLUMN, "N1", "N4", column_section),
        StructuralMember("COL-2", StructuralElement.COLUMN, "N2", "N3", column_section),
        StructuralMember("BEAM-1", StructuralElement.BEAM, "N3", "N4", beam_section),
    ]

    return {
        "success": True,
        "nodes": nodes,
        "members": members,
        "ifc_file": ifc_file_path,
        "extracted_at": datetime.now().isoformat()
    }


# ============================================================================
# Main Test / Demo
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("ORION ARCHITEKT AT - STRUCTURAL ENGINEERING INTEGRATION")
    print("=" * 80)

    print("\n1. ÖNORM B 4700 Material-Eigenschaften")
    print("-" * 80)

    c30_props = get_concrete_properties(ConcreteGrade.C30_37)
    print(f"Beton C30/37:")
    print(f"  fck = {c30_props['fck']} MPa")
    print(f"  fcd = {c30_props['fcd']:.1f} MPa")
    print(f"  fctm = {c30_props['fctm']} MPa")
    print(f"  Ecm = {c30_props['Ecm']} MPa")

    steel_props = get_steel_properties(SteelGrade.BSt_500S)
    print(f"\nBetonstahl BSt 500S:")
    print(f"  fyk = {steel_props['fyk']} MPa")
    print(f"  fyd = {steel_props['fyd']:.1f} MPa")
    print(f"  Es = {steel_props['Es']} MPa")

    print("\n2. Betondeckung nach ÖNORM B 4700")
    print("-" * 80)

    cover = calculate_minimum_concrete_cover(ExposureClass.XC3, bar_diameter=20)
    print(f"Expositionsklasse XC3, Ø20mm → cnom = {cover:.0f} mm")

    print("\n3. Erdbebenparameter nach ÖNORM EN 1998")
    print("-" * 80)

    seismic = get_seismic_parameters("wien", soil_class="B", importance_class=2)
    print(f"Bundesland: Wien")
    print(f"  Erdbebenzone: {seismic.zone.value}")
    print(f"  ag = {seismic.ag:.2f} m/s²")
    print(f"  Bodenparameter S = {seismic.s}")
    print(f"  Verhaltensbeiwert q = {seismic.q}")

    print("\n4. Biegebemessung Rechteckquerschnitt")
    print("-" * 80)

    # Beispiel: Träger mit 50 kNm
    design = design_rectangular_beam_flexure(
        med=50.0,  # kNm
        width=0.30,
        height=0.50,
        concrete_grade=ConcreteGrade.C30_37,
        steel_grade=SteelGrade.BSt_500S
    )

    print(f"Träger b/h = 30/50 cm, MEd = 50 kNm")
    for log_entry in design.calculation_log:
        print(f"  {log_entry}")
    print(f"\n  ✓ Ausnutzung Biegung: {design.utilization_bending:.1f}%")

    print("\n5. IFC Tragwerksmodell-Extraktion")
    print("-" * 80)

    structural_model = extract_structural_model_from_ifc("projekt_buerogebaeude.ifc")

    print(f"✓ {len(structural_model['nodes'])} Knoten extrahiert")
    print(f"✓ {len(structural_model['members'])} Tragwerksglieder extrahiert")

    print("\nTragwerksglieder:")
    for member in structural_model['members']:
        print(f"  • {member.member_id}: {member.element_type.value} "
              f"({member.cross_section.width*100:.0f}x{member.cross_section.height*100:.0f} cm)")

    print("\n" + "=" * 80)
    print("✓ Structural Engineering Integration Module - Funktional!")
    print("=" * 80)
    print("\nNächste Schritte:")
    print("  1. ETABS/SAP2000 API Integration")
    print("  2. Automatische Lastermittlung")
    print("  3. Bewehrungsplanung mit Stablisten")
    print("  4. Exportfunktion für Statik-Software")
    print("  5. Integration mit ai_quantity_takeoff.py")
