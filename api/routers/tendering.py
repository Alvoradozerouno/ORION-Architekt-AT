"""
ÖNORM A 2063 Tendering & Bid Management Router
Complete API for Austrian construction tendering
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from orion_oenorm_a2063 import (
    LVPosition,
    LVAenderung,
    generiere_beispiel_lv_einfamilienhaus,
    exportiere_lv_oenorm_json,
    exportiere_gaeb_xml,
    vergleiche_angebote_detailliert,
    berechne_regionale_anpassung,
    berechne_phasen_kosten,
    erstelle_lv_aenderung,
    vergleiche_lv_versionen,
    erstelle_template_erdarbeiten,
    erstelle_template_betondecke,
    erstelle_template_mauerwerk,
    erstelle_template_dacheindeckung,
    erstelle_template_estrich,
    erstelle_template_fenster,
    WASTE_FACTORS_AT,
    REGIONALE_FAKTOREN_AT,
    BAUPHASEN_AT,
    GEWERKE_KATALOG_AT,
)

router = APIRouter(
    prefix="/api/v1/tendering",
    tags=["tendering"],
)


# ═══════════════════════════════════════════════════════════════════════════
# Pydantic Models
# ═══════════════════════════════════════════════════════════════════════════

class Bundesland(str, Enum):
    """Austrian Bundesländer"""
    WIEN = "wien"
    TIROL = "tirol"
    VORARLBERG = "vorarlberg"
    SALZBURG = "salzburg"
    OBEROESTERREICH = "oberoesterreich"
    NIEDEROESTERREICH = "niederoesterreich"
    STEIERMARK = "steiermark"
    KAERNTEN = "kaernten"
    BURGENLAND = "burgenland"


class ExportFormat(str, Enum):
    """Export formats"""
    OENORM_JSON = "oenorm_json"
    GAEB_XML = "gaeb_xml"
    BOTH = "both"


class LVPositionModel(BaseModel):
    """LV Position API model"""
    oz: str = Field(..., description="Ordnungszahl (e.g. 01.001)")
    kurztext: str = Field(..., description="Short description")
    langtext: str = Field(..., description="Detailed description")
    einheit: str = Field(..., description="Unit (m, m², m³, Stk, psch)")
    menge: float = Field(..., gt=0, description="Quantity")
    ep: float = Field(0.0, ge=0, description="Unit price")
    gewerk: str = Field(..., description="Trade number (01-12)")
    kostengruppe: int = Field(300, ge=300, le=700, description="ÖNORM B 1801-1 cost group")
    bim_ref: Optional[str] = Field(None, description="IFC-GUID reference")
    stlb_code: Optional[str] = Field(None, description="StLB-BAU code")
    version: str = Field("1.0", description="Version number")

    class Config:
        schema_extra = {
            "example": {
                "oz": "01.001",
                "kurztext": "Erdarbeiten Aushub",
                "langtext": "Erdaushub maschinell, inkl. Abtransport",
                "einheit": "m³",
                "menge": 132.0,
                "ep": 45.50,
                "gewerk": "01",
                "kostengruppe": 300,
            }
        }


class LVGenerateRequest(BaseModel):
    """Request to generate LV"""
    projekt_typ: str = Field("einfamilienhaus", description="Project type")
    bgf_m2: float = Field(..., gt=0, description="Gross floor area in m²")
    geschosse: int = Field(2, ge=1, le=10, description="Number of floors")
    bundesland: Bundesland = Field(Bundesland.NIEDEROESTERREICH, description="Austrian Bundesland")
    apply_regional_factors: bool = Field(True, description="Apply regional cost factors")

    class Config:
        schema_extra = {
            "example": {
                "projekt_typ": "einfamilienhaus",
                "bgf_m2": 150,
                "geschosse": 2,
                "bundesland": "tirol",
                "apply_regional_factors": True
            }
        }


class LVGenerateResponse(BaseModel):
    """Response with generated LV"""
    lv_id: str
    positionen: List[LVPositionModel]
    anzahl_positionen: int
    bundesland: str
    regional_factor: Optional[float] = None
    waste_factors_applied: bool = True
    created_at: str
    metadata: Dict[str, Any]


class ProjektInfo(BaseModel):
    """Project information"""
    name: str = Field(..., description="Project name")
    adresse: str = Field("", description="Project address")
    bundesland: Bundesland = Field(Bundesland.NIEDEROESTERREICH)
    bauvorhaben_typ: str = Field("Neubau", description="Construction type")
    bgf_m2: float = Field(..., gt=0)


class Auftraggeber(BaseModel):
    """Client/Owner information"""
    name: str
    adresse: str = ""
    kontakt: str = ""


class ExportRequest(BaseModel):
    """Request to export LV"""
    positionen: List[LVPositionModel]
    projekt_info: ProjektInfo
    auftraggeber: Auftraggeber
    format: ExportFormat = Field(ExportFormat.OENORM_JSON)
    version: str = Field("1.0", description="LV version number")


class BidPosition(BaseModel):
    """Bid position"""
    oz: str
    menge: float
    ep: float


class BidSubmission(BaseModel):
    """Bid submission"""
    firma: str = Field(..., description="Company name")
    positionen: List[BidPosition]
    submission_date: Optional[str] = None


class BidComparisonRequest(BaseModel):
    """Request to compare bids"""
    angebote: List[BidSubmission] = Field(..., min_items=1)
    lv_positionen: List[LVPositionModel]


class ParametricTemplateRequest(BaseModel):
    """Request for parametric template"""
    template_type: str = Field(..., description="erdarbeiten, betondecke, mauerwerk, dacheindeckung, estrich, fenster")
    parameters: Dict[str, Any]


# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════

def convert_to_lv_position(pos_model: LVPositionModel) -> LVPosition:
    """Convert API model to internal LVPosition"""
    return LVPosition(
        oz=pos_model.oz,
        kurztext=pos_model.kurztext,
        langtext=pos_model.langtext,
        einheit=pos_model.einheit,
        menge=pos_model.menge,
        ep=pos_model.ep,
        gewerk=pos_model.gewerk,
        kostengruppe=pos_model.kostengruppe,
        bim_ref=pos_model.bim_ref,
        stlb_code=pos_model.stlb_code,
        version=pos_model.version,
    )


def convert_from_lv_position(pos: LVPosition) -> LVPositionModel:
    """Convert internal LVPosition to API model"""
    return LVPositionModel(
        oz=pos.oz,
        kurztext=pos.kurztext,
        langtext=pos.langtext,
        einheit=pos.einheit,
        menge=pos.menge,
        ep=pos.ep,
        gewerk=pos.gewerk,
        kostengruppe=pos.kostengruppe,
        bim_ref=pos.bim_ref,
        stlb_code=pos.stlb_code,
        version=pos.version,
    )


# ═══════════════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/lv/generate", response_model=LVGenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate_lv(request: LVGenerateRequest):
    """
    Generate Bill of Quantities (Leistungsverzeichnis) according to ÖNORM A 2063

    - **projekt_typ**: Type of project (einfamilienhaus, mehrfamilienhaus, etc.)
    - **bgf_m2**: Gross floor area in square meters
    - **geschosse**: Number of floors
    - **bundesland**: Austrian Bundesland for regional cost factors
    - **apply_regional_factors**: Whether to apply regional cost adjustments

    Returns complete LV with 16+ positions including waste factors.
    """
    try:
        # Generate LV
        positionen = generiere_beispiel_lv_einfamilienhaus(
            bgf_m2=request.bgf_m2,
            geschosse=request.geschosse
        )

        # Apply regional factors if requested
        regional_factor = None
        if request.apply_regional_factors:
            regional_result = berechne_regionale_anpassung(
                positionen,
                request.bundesland.value
            )
            positionen = regional_result["positionen_angepasst"]
            regional_factor = regional_result["faktor"]

        # Generate LV ID
        import uuid
        lv_id = str(uuid.uuid4())

        # Convert to API models
        positionen_models = [convert_from_lv_position(p) for p in positionen]

        return LVGenerateResponse(
            lv_id=lv_id,
            positionen=positionen_models,
            anzahl_positionen=len(positionen_models),
            bundesland=request.bundesland.value,
            regional_factor=regional_factor,
            waste_factors_applied=True,
            created_at=datetime.utcnow().isoformat() + "Z",
            metadata={
                "projekt_typ": request.projekt_typ,
                "bgf_m2": request.bgf_m2,
                "geschosse": request.geschosse,
                "standard": "ÖNORM A 2063-1:2024",
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating LV: {str(e)}"
        )


@router.post("/lv/export")
async def export_lv(request: ExportRequest):
    """
    Export LV in ÖNORM JSON or GAEB XML format

    - **format**: Export format (oenorm_json, gaeb_xml, both)
    - **positionen**: List of LV positions
    - **projekt_info**: Project information
    - **auftraggeber**: Client information
    - **version**: LV version number

    Returns exported data in requested format(s).
    """
    try:
        # Convert API models to internal format
        positionen = [convert_to_lv_position(p) for p in request.positionen]

        result = {}

        if request.format in [ExportFormat.OENORM_JSON, ExportFormat.BOTH]:
            oenorm_json = exportiere_lv_oenorm_json(
                positionen=positionen,
                projekt_info=request.projekt_info.dict(),
                auftraggeber=request.auftraggeber.dict(),
                bundesland=request.projekt_info.bundesland.value
            )
            result["oenorm_json"] = oenorm_json

        if request.format in [ExportFormat.GAEB_XML, ExportFormat.BOTH]:
            gaeb_xml = exportiere_gaeb_xml(
                lv_positionen=positionen,
                projekt_info=request.projekt_info.dict(),
                version=request.version
            )
            result["gaeb_xml"] = gaeb_xml

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting LV: {str(e)}"
        )


@router.post("/bids/compare")
async def compare_bids(request: BidComparisonRequest):
    """
    Compare multiple bid submissions with scoring and evaluation

    - **angebote**: List of bid submissions from different companies
    - **lv_positionen**: Original LV positions for comparison

    Returns detailed comparison with:
    - Price comparison matrix (Preisspiegelmatrix)
    - Multi-criteria scoring (price 70%, outlier penalty 30%)
    - Recommended bidder
    - Warnings and compliance checks
    """
    try:
        # Convert to internal format
        lv_positionen = [convert_to_lv_position(p) for p in request.lv_positionen]
        angebote = [a.dict() for a in request.angebote]

        # Perform comparison
        comparison = vergleiche_angebote_detailliert(angebote, lv_positionen)

        return comparison

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing bids: {str(e)}"
        )


@router.get("/lv/phase-costs")
async def calculate_phase_costs(lv_id: str):
    """
    Calculate construction phase cost breakdown

    Returns:
    - Rohbau (45% target)
    - Ausbau (40% target)
    - Fertigstellung (15% target)
    - Deviation analysis from target percentages
    """
    # Note: In production, retrieve LV from database using lv_id
    # For now, return example
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Phase cost calculation requires LV storage implementation"
    )


@router.post("/templates/parametric")
async def create_parametric_position(request: ParametricTemplateRequest):
    """
    Create LV position from parametric template

    Available templates:
    - erdarbeiten: parameters {grundflaeche_m2, tiefe_m}
    - betondecke: parameters {flaeche_m2, dicke_cm, betonfestigkeitsklasse}
    - mauerwerk: parameters {umfang_m, hoehe_m, dicke_cm}
    - dacheindeckung: parameters {dachflaeche_m2, material}
    - estrich: parameters {nutzflaeche_m2, typ, dicke_cm}
    - fenster: parameters {anzahl, flaeche_m2_pro_stueck, u_wert}
    """
    try:
        template_type = request.template_type.lower()
        params = request.parameters

        position = None

        if template_type == "erdarbeiten":
            position = erstelle_template_erdarbeiten(
                grundflaeche_m2=params.get("grundflaeche_m2", 150),
                tiefe_m=params.get("tiefe_m", 3.0)
            )
        elif template_type == "betondecke":
            position = erstelle_template_betondecke(
                flaeche_m2=params.get("flaeche_m2", 150),
                dicke_cm=params.get("dicke_cm", 20),
                betonfestigkeitsklasse=params.get("betonfestigkeitsklasse", "C25/30")
            )
        elif template_type == "mauerwerk":
            position = erstelle_template_mauerwerk(
                umfang_m=params.get("umfang_m", 40),
                hoehe_m=params.get("hoehe_m", 2.5),
                dicke_cm=params.get("dicke_cm", 25)
            )
        elif template_type == "dacheindeckung":
            position = erstelle_template_dacheindeckung(
                dachflaeche_m2=params.get("dachflaeche_m2", 100),
                material=params.get("material", "Tondachziegel")
            )
        elif template_type == "estrich":
            position = erstelle_template_estrich(
                nutzflaeche_m2=params.get("nutzflaeche_m2", 120),
                typ=params.get("typ", "Heizestrich"),
                dicke_cm=params.get("dicke_cm", 6)
            )
        elif template_type == "fenster":
            position = erstelle_template_fenster(
                anzahl=params.get("anzahl", 15),
                flaeche_m2_pro_stueck=params.get("flaeche_m2_pro_stueck", 1.5),
                u_wert=params.get("u_wert", 0.9)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown template type: {template_type}"
            )

        return convert_from_lv_position(position)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating parametric position: {str(e)}"
        )


@router.get("/metadata/waste-factors")
async def get_waste_factors():
    """
    Get waste/loss factors for all material types

    Returns dictionary of waste factors for Austrian construction practice:
    - beton: 3%
    - mauerwerk: 8%
    - estrich: 5%
    - erdarbeiten: 10%
    - etc.
    """
    return {
        "waste_factors": WASTE_FACTORS_AT,
        "source": "Österreichische Baupraxis, BKI-Baukosten 2024"
    }


@router.get("/metadata/regional-factors")
async def get_regional_factors():
    """
    Get regional cost adjustment factors for all 9 Austrian Bundesländer

    Returns factors ranging from:
    - Wien: 1.15 (+15%)
    - Tirol: 1.12 (+12%)
    - Burgenland: 0.92 (-8%)
    """
    return {
        "regional_factors": REGIONALE_FAKTOREN_AT,
        "reference": "Niederösterreich = 1.00 (baseline)"
    }


@router.get("/metadata/trades")
async def get_trades():
    """
    Get catalog of all construction trades (Gewerke)

    Returns 12 standardized Austrian construction trades from ÖNORM.
    """
    return {
        "gewerke": GEWERKE_KATALOG_AT,
        "standard": "ÖNORM A 2063, StLB-BAU"
    }


@router.get("/metadata/construction-phases")
async def get_construction_phases():
    """
    Get construction phase definitions

    Returns 3 phases with target cost percentages:
    - Rohbau: 45%
    - Ausbau: 40%
    - Fertigstellung: 15%
    """
    return {
        "bauphasen": BAUPHASEN_AT,
        "standard": "ÖNORM B 1801-1:2009"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for tendering module"""
    return {
        "status": "healthy",
        "module": "ÖNORM A 2063 Tendering",
        "version": "1.0.0",
        "standards": [
            "ÖNORM A 2063-1:2024",
            "ÖNORM A 2063-2:2021",
            "ÖNORM B 2110:2013",
            "ÖNORM B 1801-1:2009"
        ]
    }
