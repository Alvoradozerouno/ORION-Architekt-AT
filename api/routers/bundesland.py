"""
Bundesland-specific regulations Router
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()


class BundeslandInfo(BaseModel):
    """Bundesland information"""

    name: str
    bauordnung: str
    stellplatz_factor: float
    aufzug_ab_geschoss: int
    special_regulations: List[str]


@router.get("/{bundesland}", response_model=BundeslandInfo)
async def get_bundesland_info(bundesland: str):
    """
    🗺️ **Bundesland-Specific Information**

    Get building regulations specific to each Bundesland.
    Each of Austria's 9 Bundesländer has its own Bauordnung.
    """
    bundesland_data = {
        "wien": BundeslandInfo(
            name="Wien",
            bauordnung="Wiener Bauordnung",
            stellplatz_factor=1.2,
            aufzug_ab_geschoss=4,
            special_regulations=[
                "Dachgeschoßausbau: besondere Bestimmungen",
                "Stellplatzpflicht: 1,2 pro Wohnung",
                "Grünflächenanteil erforderlich",
            ],
        ),
        "tirol": BundeslandInfo(
            name="Tirol",
            bauordnung="Tiroler Bauordnung 2022",
            stellplatz_factor=1.5,
            aufzug_ab_geschoss=4,
            special_regulations=[
                "Höhere Stellplatzpflicht: 1,5 pro Wohnung",
                "Lawinenschutz beachten",
                "Ortsbildschutz in Tourismusgebieten",
            ],
        ),
        "salzburg": BundeslandInfo(
            name="Salzburg",
            bauordnung="Salzburger Baupolizeigesetz",
            stellplatz_factor=1.3,
            aufzug_ab_geschoss=4,
            special_regulations=[
                "Altstadtschutzzone: besondere Auflagen",
                "Schneelast: erhöhte Anforderungen",
            ],
        ),
        "vorarlberg": BundeslandInfo(
            name="Vorarlberg",
            bauordnung="Vorarlberger Baugesetz",
            stellplatz_factor=1.4,
            aufzug_ab_geschoss=4,
            special_regulations=[
                "Energiestandard: oft höher als OIB-RL 6",
                "Holzbau: förderungswürdig",
            ],
        ),
    }

    bundesland_lower = bundesland.lower()
    if bundesland_lower not in bundesland_data:
        # Return default for other Bundesländer
        return BundeslandInfo(
            name=bundesland.title(),
            bauordnung=f"{bundesland.title()} Bauordnung",
            stellplatz_factor=1.2,
            aufzug_ab_geschoss=4,
            special_regulations=["Lokale Bauordnung beachten"],
        )

    return bundesland_data[bundesland_lower]


@router.get("/{bundesland}/stellplaetze")
async def get_stellplatz_requirements(bundesland: str, wohnungen: int):
    """Get parking requirements for Bundesland"""
    info = await get_bundesland_info(bundesland)
    required = int(wohnungen * info.stellplatz_factor)

    return {
        "bundesland": bundesland,
        "wohnungen": wohnungen,
        "factor": info.stellplatz_factor,
        "required_stellplaetze": required,
        "regulation": info.bauordnung,
    }


@router.get("/{bundesland}/aufzug")
async def get_aufzug_requirements(bundesland: str, geschosse: int):
    """Get elevator requirements for Bundesland"""
    info = await get_bundesland_info(bundesland)
    required = geschosse >= info.aufzug_ab_geschoss

    return {
        "bundesland": bundesland,
        "geschosse": geschosse,
        "aufzug_required": required,
        "ab_geschoss": info.aufzug_ab_geschoss,
        "regulation": info.bauordnung,
    }
