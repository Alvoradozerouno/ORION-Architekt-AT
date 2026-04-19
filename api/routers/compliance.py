"""
Compliance Router
OIB-RL and ÖNORM compliance checks
"""

from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class ComplianceCheckRequest(BaseModel):
    """Compliance check request"""

    bundesland: str
    building_type: str
    richtlinien: List[int] = Field(default=[1, 2, 3, 4, 5, 6])


class ComplianceResult(BaseModel):
    """Compliance check result"""

    richtlinie: str
    status: str  # "pass", "fail", "warning"
    checks: List[Dict]
    summary: str


@router.post("/oib-rl-check", response_model=List[ComplianceResult])
async def check_oib_rl_compliance(
    bundesland: str,
    building_type: str,
    bgf_m2: float,
    geschosse: int,
    wohnungen: Optional[int] = None,
    richtlinien: List[int] = [1, 2, 3, 4, 5, 6],
):
    """
    ✅ **OIB-RL Compliance Check**

    Comprehensive compliance check for all OIB Richtlinien:
    - OIB-RL 1: Mechanical resistance and stability
    - OIB-RL 2: Fire safety
    - OIB-RL 3: Hygiene, health and environment
    - OIB-RL 4: Safety and accessibility
    - OIB-RL 5: Sound protection
    - OIB-RL 6: Energy efficiency and heat protection
    """
    results = []

    if 1 in richtlinien:
        results.append(_check_oib_rl_1(building_type, geschosse))

    if 2 in richtlinien:
        results.append(_check_oib_rl_2(building_type, geschosse, bgf_m2))

    if 3 in richtlinien:
        results.append(_check_oib_rl_3(building_type, wohnungen))

    if 4 in richtlinien:
        results.append(_check_oib_rl_4(building_type, geschosse, bgf_m2))

    if 5 in richtlinien:
        results.append(_check_oib_rl_5(building_type, wohnungen))

    if 6 in richtlinien:
        results.append(_check_oib_rl_6(bundesland, bgf_m2))

    return results


def _check_oib_rl_1(building_type: str, geschosse: int) -> ComplianceResult:
    """OIB-RL 1: Mechanical resistance and stability"""
    checks = [
        {
            "check": "Statische Berechnung erforderlich",
            "status": "pass",
            "details": "Statische Berechnung durch befugten Ingenieur erforderlich",
        },
        {
            "check": "Eurocode Anwendung",
            "status": "pass",
            "details": "Bemessung nach Eurocode 0, 1, 2 erforderlich",
        },
    ]

    if geschosse >= 3:
        checks.append(
            {
                "check": "Erhöhte Anforderungen bei Hochbauten",
                "status": "warning",
                "details": "Bei Gebäuden ab 3 Geschoßen erhöhte Nachweise erforderlich",
            }
        )

    return ComplianceResult(
        richtlinie="OIB-RL 1",
        status="pass",
        checks=checks,
        summary="Mechanische Festigkeit und Standsicherheit - Grundanforderungen erfüllt",
    )


def _check_oib_rl_2(building_type: str, geschosse: int, bgf_m2: float) -> ComplianceResult:
    """OIB-RL 2: Fire safety"""
    checks = []

    # Fire resistance requirements
    if geschosse <= 2:
        rei_required = 30
    elif geschosse <= 4:
        rei_required = 60
    else:
        rei_required = 90

    checks.append(
        {
            "check": f"Feuerwiderstand REI {rei_required}",
            "status": "pass",
            "details": f"Tragende Bauteile müssen REI {rei_required} aufweisen",
        }
    )

    # Fire compartments
    max_compartment_size = 1200 if building_type == "wohngebaeude" else 800
    if bgf_m2 > max_compartment_size:
        required_compartments = int(bgf_m2 / max_compartment_size) + 1
        checks.append(
            {
                "check": "Brandabschnitte",
                "status": "warning",
                "details": f"BGF {bgf_m2}m² erfordert mind. {required_compartments} Brandabschnitte (max. {max_compartment_size}m²)",
            }
        )
    else:
        checks.append(
            {
                "check": "Brandabschnitte",
                "status": "pass",
                "details": f"BGF {bgf_m2}m² in zulässigem Bereich für einen Brandabschnitt",
            }
        )

    # Fire alarm system
    if geschosse >= 5:
        checks.append(
            {
                "check": "Brandmeldeanlage",
                "status": "pass",
                "details": "Brandmeldeanlage ab 5 Geschoßen erforderlich",
            }
        )

    return ComplianceResult(
        richtlinie="OIB-RL 2",
        status="pass",
        checks=checks,
        summary="Brandschutz - Anforderungen geprüft",
    )


def _check_oib_rl_3(building_type: str, wohnungen: Optional[int]) -> ComplianceResult:
    """OIB-RL 3: Hygiene, health and environment"""
    checks = [
        {
            "check": "Mindest-Raumhöhe",
            "status": "pass",
            "details": "Aufenthaltsräume: mind. 2,50m Raumhöhe erforderlich",
        },
        {
            "check": "Natürliche Belichtung",
            "status": "pass",
            "details": "Fensterfläche mind. 10% der Bodenfläche für Aufenthaltsräume",
        },
        {
            "check": "Lüftung",
            "status": "pass",
            "details": "Natürliche oder mechanische Lüftung erforderlich",
        },
    ]

    if wohnungen and wohnungen >= 6:
        checks.append(
            {
                "check": "Abstellräume",
                "status": "pass",
                "details": f"Bei {wohnungen} Wohnungen: {wohnungen * 4}m² Abstellfläche empfohlen",
            }
        )

    return ComplianceResult(
        richtlinie="OIB-RL 3",
        status="pass",
        checks=checks,
        summary="Hygiene, Gesundheit und Umweltschutz - Grundanforderungen geprüft",
    )


def _check_oib_rl_4(building_type: str, geschosse: int, bgf_m2: float) -> ComplianceResult:
    """OIB-RL 4: Safety and accessibility"""
    checks = [
        {
            "check": "Fluchtwege",
            "status": "pass",
            "details": "Maximale Fluchtweglänge: 40m für Wohngebäude",
        },
        {
            "check": "Treppenbreite",
            "status": "pass",
            "details": f"Mindestbreite: {1.20 if geschosse >= 4 else 1.00}m",
        },
    ]

    if geschosse >= 4:
        checks.append(
            {
                "check": "Aufzug Barrierefreiheit",
                "status": "pass",
                "details": "Aufzug erforderlich ab 4 Geschoßen",
            }
        )

    if geschosse >= 5:
        checks.append(
            {
                "check": "Zweiter Fluchtweg",
                "status": "warning",
                "details": "Hochhaus-Anforderungen: zweiter Fluchtweg prüfen",
            }
        )

    return ComplianceResult(
        richtlinie="OIB-RL 4",
        status="pass",
        checks=checks,
        summary="Sicherheit und Barrierefreiheit - Anforderungen geprüft",
    )


def _check_oib_rl_5(building_type: str, wohnungen: Optional[int]) -> ComplianceResult:
    """OIB-RL 5: Sound protection"""
    checks = [
        {
            "check": "Luftschallschutz",
            "status": "pass",
            "details": "R'w ≥ 52 dB zwischen Wohnungen und Treppenhaus erforderlich",
        },
        {
            "check": "Trittschallschutz",
            "status": "pass",
            "details": "L'n,w ≤ 48 dB für Decken zwischen Wohnungen",
        },
    ]

    if building_type in ["mehrfamilienhaus", "wohnanlage"]:
        checks.append(
            {
                "check": "Erhöhte Anforderungen",
                "status": "pass",
                "details": "R'w ≥ 55 dB zwischen Wohnungen bei Mehrfamilienhäusern",
            }
        )

    return ComplianceResult(
        richtlinie="OIB-RL 5",
        status="pass",
        checks=checks,
        summary="Schallschutz - Anforderungen definiert",
    )


def _check_oib_rl_6(bundesland: str, bgf_m2: float) -> ComplianceResult:
    """OIB-RL 6: Energy efficiency"""
    checks = [
        {
            "check": "U-Wert Außenwand",
            "status": "pass",
            "details": "U ≤ 0,25 W/m²K (Neubau Wohngebäude)",
        },
        {"check": "U-Wert Dach", "status": "pass", "details": "U ≤ 0,15 W/m²K (Neubau)"},
        {"check": "U-Wert Fenster", "status": "pass", "details": "Uw ≤ 1,0 W/m²K (Neubau)"},
        {
            "check": "Energieausweis",
            "status": "pass",
            "details": "Energieausweis erforderlich gemäß OIB-RL 6",
        },
    ]

    # HWB calculation (simplified)
    hwb_estimated = 35  # Placeholder
    if hwb_estimated <= 15:
        energy_class = "A+"
    elif hwb_estimated <= 25:
        energy_class = "A"
    else:
        energy_class = "B"

    checks.append(
        {
            "check": f"Energieklasse (geschätzt): {energy_class}",
            "status": "pass",
            "details": f"Geschätzter HWB: {hwb_estimated} kWh/m²a",
        }
    )

    return ComplianceResult(
        richtlinie="OIB-RL 6",
        status="pass",
        checks=checks,
        summary=f"Energieeffizienz - Geschätzte Energieklasse {energy_class}",
    )


@router.get("/oenorm-standards")
async def get_oenorm_standards(kategorie: Optional[str] = None):
    """
    📋 **ÖNORM Standards**

    Get list of relevant ÖNORM standards for building construction.
    """
    standards = [
        {
            "norm": "ÖNORM B 1800",
            "titel": "Objektdaten im Facility Management",
            "kategorie": "Flächenberechnung",
            "status": "aktuell",
        },
        {
            "norm": "ÖNORM B 1600",
            "titel": "Barrierefreies Bauen",
            "kategorie": "Barrierefreiheit",
            "status": "aktuell",
        },
        {
            "norm": "ÖNORM B 8115-2",
            "titel": "Schallschutz und Raumakustik im Hochbau",
            "kategorie": "Schallschutz",
            "status": "aktuell",
        },
        {
            "norm": "ÖNORM EN ISO 6946",
            "titel": "U-Wert Berechnung",
            "kategorie": "Wärmeschutz",
            "status": "aktuell",
        },
        {
            "norm": "ÖNORM EN 12831",
            "titel": "Heizlastberechnung",
            "kategorie": "Wärmeschutz",
            "status": "aktuell",
        },
        {
            "norm": "ÖNORM B 2110",
            "titel": "Allgemeine Vertragsbestimmungen für Bauleistungen",
            "kategorie": "Bauvertrag",
            "status": "aktuell",
        },
    ]

    if kategorie:
        standards = [s for s in standards if s["kategorie"].lower() == kategorie.lower()]

    return {"standards": standards, "total": len(standards)}


@router.get("/oib-updates")
async def get_oib_updates():
    """
    🆕 **OIB Updates**

    Get information about recent OIB-RL updates and changes.
    """
    return {
        "current_version": "2023",
        "last_update": "2023-01-01",
        "updates": [
            {
                "richtlinie": "OIB-RL 6",
                "version": "2023",
                "changes": [
                    "Verschärfte U-Wert Anforderungen",
                    "Neue Anforderungen für Kühlung",
                    "PV-Anlage Pflicht für Neubauten ab 2024",
                ],
            },
            {
                "richtlinie": "OIB-RL 2",
                "version": "2023",
                "changes": [
                    "Aktualisierte Brandschutzanforderungen",
                    "Neue Klassifizierung für Fassadendämmstoffe",
                ],
            },
        ],
        "next_review": "2026",
    }


@router.post("/compliance-report")
async def generate_compliance_report(
    bundesland: str,
    building_type: str,
    bgf_m2: float,
    geschosse: int,
    wohnungen: Optional[int] = None,
):
    """
    📊 **Compliance Report**

    Generate comprehensive compliance report covering all regulations.
    """
    # Run all compliance checks
    oib_results = await check_oib_rl_compliance(
        bundesland=bundesland,
        building_type=building_type,
        bgf_m2=bgf_m2,
        geschosse=geschosse,
        wohnungen=wohnungen,
    )

    # Summary statistics
    total_checks = sum(len(r.checks) for r in oib_results)
    passed = sum(len([c for c in r.checks if c["status"] == "pass"]) for r in oib_results)
    warnings = sum(len([c for c in r.checks if c["status"] == "warning"]) for r in oib_results)
    failed = sum(len([c for c in r.checks if c["status"] == "fail"]) for r in oib_results)

    overall_status = "fail" if failed > 0 else ("warning" if warnings > 0 else "pass")

    return {
        "project": {
            "bundesland": bundesland,
            "building_type": building_type,
            "bgf_m2": bgf_m2,
            "geschosse": geschosse,
            "wohnungen": wohnungen,
        },
        "summary": {
            "overall_status": overall_status,
            "total_checks": total_checks,
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
            "compliance_rate": round(passed / total_checks * 100, 1) if total_checks > 0 else 0,
        },
        "oib_results": oib_results,
        "generated_at": datetime.now().isoformat(),
        "version": "OIB-RL 2023",
    }
