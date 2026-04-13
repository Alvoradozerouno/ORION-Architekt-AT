"""
Input Validation Utilities for ORION Architekt-AT API
======================================================

Comprehensive validation schemas and utilities for all API endpoints.
Implements security best practices and Austrian building code requirements.

Author: ORION Engineering Team
Date: 2026-04-11
Status: PRODUCTION
"""

import re
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field, root_validator, validator

# ============================================================================
# AUSTRIAN BUILDING CODE CONSTANTS
# ============================================================================


class Bundesland(str, Enum):
    """Austrian federal states (Bundesländer)"""

    WIEN = "wien"
    TIROL = "tirol"
    SALZBURG = "salzburg"
    VORARLBERG = "vorarlberg"
    BURGENLAND = "burgenland"
    KAERNTEN = "kaernten"
    STEIERMARK = "steiermark"
    OBEROESTERREICH = "oberoesterreich"
    NIEDEROESTERREICH = "niederoesterreich"


class BuildingType(str, Enum):
    """Common building types"""

    EINFAMILIENHAUS = "einfamilienhaus"
    MEHRFAMILIENHAUS = "mehrfamilienhaus"
    WOHNGEBAEUDE = "wohngebaeude"
    BUEROGEBAEUDE = "buerogebaeude"
    GEWERBE = "gewerbe"
    INDUSTRIE = "industrie"
    MIXED = "mixed"


class Raumtyp(str, Enum):
    """Room types for area calculations"""

    WOHNUNG = "wohnung"
    BUERO = "buero"
    LAGER = "lager"
    VERKAUF = "verkauf"
    TECHNIK = "technik"
    VERKEHR = "verkehr"


class MaterialKategorie(str, Enum):
    """Material categories"""

    TRAGKONSTRUKTION = "Tragkonstruktion"
    MAUERWERK = "Mauerwerk"
    DAEMMUNG = "Dämmung"
    AUSBAU = "Ausbau"
    OBERFLAECHE = "Oberfläche"
    FENSTER = "Fenster"


# ============================================================================
# VALIDATION HELPERS
# ============================================================================


def validate_positive(v: float, field_name: str = "value") -> float:
    """Validate that a number is positive"""
    if v <= 0:
        raise ValueError(f"{field_name} must be positive, got {v}")
    return v


def validate_percentage(v: float, field_name: str = "value") -> float:
    """Validate that a percentage is between 0 and 100"""
    if not 0 <= v <= 100:
        raise ValueError(f"{field_name} must be between 0 and 100, got {v}")
    return v


def validate_bundesland(v: str) -> str:
    """Validate Austrian Bundesland name"""
    valid_bundeslaender = {bl.value for bl in Bundesland}
    if v.lower() not in valid_bundeslaender:
        raise ValueError(
            f"Invalid Bundesland: {v}. Must be one of: {', '.join(valid_bundeslaender)}"
        )
    return v.lower()


def sanitize_string(v: str, max_length: int = 1000) -> str:
    """Sanitize string input to prevent injection attacks"""
    if not isinstance(v, str):
        raise ValueError(f"Expected string, got {type(v)}")

    # Remove null bytes
    v = v.replace("\x00", "")

    # Limit length
    if len(v) > max_length:
        raise ValueError(f"String too long: {len(v)} > {max_length}")

    # Remove potentially dangerous characters
    # Allow: alphanumeric, German special chars, spaces, common punctuation
    allowed_pattern = r"^[a-zA-ZäöüÄÖÜß0-9\s\.,\-_/\(\)\[\]]+$"
    if not re.match(allowed_pattern, v):
        # More permissive for descriptions
        if len(v) > 100:
            raise ValueError("String contains invalid characters")

    return v.strip()


# ============================================================================
# ENHANCED VALIDATION MODELS
# ============================================================================


class ValidatedSchicht(BaseModel):
    """Layer in construction with validation"""

    material: str = Field(..., min_length=1, max_length=200)
    dicke_mm: float = Field(..., gt=0, le=5000, description="Thickness in mm (max 5m)")
    lambda_wert: float = Field(..., gt=0, le=10, description="Thermal conductivity W/mK")

    @validator("material")
    def validate_material(cls, v):
        return sanitize_string(v, max_length=200)

    @validator("dicke_mm")
    def validate_dicke(cls, v):
        if v > 5000:  # 5 meters maximum
            raise ValueError("Layer thickness unrealistic: > 5m")
        if v < 1:  # 1mm minimum
            raise ValueError("Layer thickness too thin: < 1mm")
        return v

    @validator("lambda_wert")
    def validate_lambda(cls, v):
        if v > 10:  # Unrealistically high
            raise ValueError("Lambda value unrealistic: > 10 W/mK")
        if v < 0.001:  # Unrealistically low
            raise ValueError("Lambda value unrealistic: < 0.001 W/mK")
        return v


class ValidatedUWertRequest(BaseModel):
    """U-value calculation request with comprehensive validation"""

    schichten: List[ValidatedSchicht] = Field(..., min_items=1, max_items=20)
    innen_uebergang: float = Field(0.13, ge=0.04, le=0.25)
    aussen_uebergang: float = Field(0.04, ge=0.02, le=0.10)

    @validator("schichten")
    def validate_schichten(cls, v):
        if len(v) < 1:
            raise ValueError("At least one layer required")
        if len(v) > 20:
            raise ValueError("Maximum 20 layers allowed")

        # Check total thickness is realistic
        total_thickness = sum(s.dicke_mm for s in v)
        if total_thickness > 2000:  # 2 meters
            raise ValueError(f"Total wall thickness unrealistic: {total_thickness}mm > 2000mm")
        if total_thickness < 50:  # 5cm minimum
            raise ValueError(f"Total wall thickness too thin: {total_thickness}mm < 50mm")

        return v


class ValidatedStellplatzRequest(BaseModel):
    """Parking space calculation with validation"""

    bundesland: Bundesland
    wohnungen: int = Field(..., gt=0, le=10000, description="Number of apartments")
    building_type: BuildingType = Field(BuildingType.MEHRFAMILIENHAUS)

    @validator("wohnungen")
    def validate_wohnungen(cls, v):
        if v > 10000:
            raise ValueError("Number of apartments unrealistic: > 10000")
        if v < 1:
            raise ValueError("At least 1 apartment required")
        return v


class ValidatedFlaecheRequest(BaseModel):
    """Area calculation with validation"""

    raumtyp: Raumtyp
    laenge_m: float = Field(..., gt=0, le=1000)
    breite_m: float = Field(..., gt=0, le=1000)
    hoehe_m: float = Field(..., gt=0, le=100)

    @validator("laenge_m", "breite_m")
    def validate_dimensions(cls, v):
        if v > 1000:
            raise ValueError("Dimension unrealistic: > 1000m")
        if v < 0.1:
            raise ValueError("Dimension too small: < 0.1m")
        return v

    @validator("hoehe_m")
    def validate_hoehe(cls, v):
        if v > 100:
            raise ValueError("Height unrealistic: > 100m")
        if v < 1.5:
            raise ValueError("Height too low: < 1.5m (Austrian minimum)")
        return v

    @root_validator(skip_on_failure=True)
    def validate_area(cls, values):
        laenge = values.get("laenge_m", 0)
        breite = values.get("breite_m", 0)
        area = laenge * breite

        if area > 100000:  # 10 hectares
            raise ValueError(f"Room area unrealistic: {area}m² > 100000m²")
        if area < 1:
            raise ValueError(f"Room area too small: {area}m² < 1m²")

        return values


class ValidatedBarrierefreiheitRequest(BaseModel):
    """Accessibility check with validation"""

    tuer_breite_cm: float = Field(..., ge=50, le=300, description="Door width in cm")
    rampe_vorhanden: bool
    rampe_steigung_prozent: Optional[float] = Field(None, ge=0, le=100)
    aufzug_vorhanden: bool = False
    geschosse: int = Field(..., ge=1, le=200)
    bundesland: Optional[Bundesland] = Field(Bundesland.WIEN)

    @validator("rampe_steigung_prozent")
    def validate_rampe(cls, v, values):
        if values.get("rampe_vorhanden") and v is None:
            raise ValueError("Ramp slope required when ramp exists")
        if v is not None and v > 100:
            raise ValueError("Ramp slope percentage unrealistic: > 100%")
        return v

    @validator("geschosse")
    def validate_geschosse(cls, v):
        if v > 200:
            raise ValueError("Number of floors unrealistic: > 200")
        return v


class ValidatedFluchtwegRequest(BaseModel):
    """Emergency exit check with validation"""

    max_entfernung_m: float = Field(..., ge=0, le=200)
    treppenhaus_breite_m: float = Field(..., ge=0.5, le=10)
    geschosse: int = Field(..., ge=1, le=200)
    gebaudetyp: BuildingType = Field(BuildingType.WOHNGEBAEUDE)

    @validator("max_entfernung_m")
    def validate_entfernung(cls, v):
        if v > 200:
            raise ValueError("Distance unrealistic: > 200m")
        return v


class ValidatedSchallschutzRequest(BaseModel):
    """Sound insulation check with validation"""

    wandaufbau: List[ValidatedSchicht] = Field(..., min_items=1, max_items=15)
    gebaudetyp: BuildingType = Field(BuildingType.MEHRFAMILIENHAUS)

    @validator("wandaufbau")
    def validate_wandaufbau(cls, v):
        total_thickness = sum(s.dicke_mm for s in v)
        if total_thickness > 1000:  # 1 meter
            raise ValueError(f"Wall thickness unrealistic: {total_thickness}mm > 1000mm")
        return v


class ValidatedHeizlastRequest(BaseModel):
    """Heating load calculation with validation"""

    bgf_m2: float = Field(..., gt=0, le=1000000)
    uwert_wand: float = Field(..., gt=0, le=5)
    uwert_dach: float = Field(..., gt=0, le=5)
    uwert_fenster: float = Field(..., gt=0, le=10)
    bundesland: Bundesland = Field(Bundesland.WIEN)

    @validator("bgf_m2")
    def validate_bgf(cls, v):
        if v > 1000000:  # 100 hectares
            raise ValueError("Building area unrealistic: > 1,000,000 m²")
        if v < 10:
            raise ValueError("Building area too small: < 10 m²")
        return v

    @validator("uwert_wand", "uwert_dach", "uwert_fenster")
    def validate_uwert(cls, v):
        if v > 5:
            raise ValueError(f"U-value unrealistic: {v} > 5 W/m²K")
        if v < 0.01:
            raise ValueError(f"U-value unrealistic: {v} < 0.01 W/m²K")
        return v


class ValidatedComplianceRequest(BaseModel):
    """OIB-RL compliance check with validation"""

    bundesland: Bundesland
    building_type: BuildingType
    bgf_m2: float = Field(..., gt=0, le=1000000)
    geschosse: int = Field(..., ge=1, le=200)
    wohnungen: Optional[int] = Field(None, ge=0, le=10000)
    richtlinien: List[int] = Field(default=[1, 2, 3, 4, 5, 6], min_items=1, max_items=6)

    @validator("richtlinien")
    def validate_richtlinien(cls, v):
        for rl in v:
            if rl < 1 or rl > 6:
                raise ValueError(f"Invalid OIB-RL number: {rl}. Must be 1-6")
        return v

    @validator("wohnungen")
    def validate_wohnungen_optional(cls, v, values):
        building_type = values.get("building_type")
        if building_type in [BuildingType.MEHRFAMILIENHAUS, BuildingType.WOHNGEBAEUDE]:
            if v is None or v < 1:
                raise ValueError("Number of apartments required for residential buildings")
        return v


# ============================================================================
# FILE UPLOAD VALIDATION
# ============================================================================


class ValidatedFileUpload(BaseModel):
    """File upload validation"""

    filename: str = Field(..., min_length=1, max_length=255)
    file_size_bytes: int = Field(..., gt=0, le=104857600)  # 100 MB max
    mime_type: str

    ALLOWED_EXTENSIONS: ClassVar[set] = {
        ".ifc",
        ".ifcxml",
        ".pdf",
        ".dwg",
        ".dxf",
        ".rvt",
        ".jpg",
        ".png",
    }
    ALLOWED_MIME_TYPES: ClassVar[set] = {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "application/octet-stream",  # For IFC files
        "application/xml",
        "text/xml",
    }

    @validator("filename")
    def validate_filename(cls, v):
        # Sanitize filename
        v = sanitize_string(v, max_length=255)

        # Check extension
        import os

        ext = os.path.splitext(v)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Invalid file extension: {ext}. " f"Allowed: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            )

        # Prevent path traversal
        if ".." in v or "/" in v or "\\" in v:
            raise ValueError("Invalid filename: path traversal detected")

        return v

    @validator("file_size_bytes")
    def validate_file_size(cls, v):
        max_size = 104857600  # 100 MB
        if v > max_size:
            raise ValueError(f"File too large: {v} bytes > {max_size} bytes (100 MB)")
        if v < 1:
            raise ValueError("File is empty")
        return v

    @validator("mime_type")
    def validate_mime_type(cls, v):
        if v not in cls.ALLOWED_MIME_TYPES:
            raise ValueError(
                f"Invalid MIME type: {v}. " f"Allowed: {', '.join(cls.ALLOWED_MIME_TYPES)}"
            )
        return v


# ============================================================================
# API KEY VALIDATION
# ============================================================================


def validate_api_key(api_key: str) -> bool:
    """Validate API key format and structure"""
    if not api_key:
        return False

    # API key format: orion_{tier}_{32_char_hex}
    pattern = r"^orion_(free|premium|enterprise)_[a-f0-9]{32}$"
    return bool(re.match(pattern, api_key))


def validate_jwt_format(token: str) -> bool:
    """Basic JWT format validation"""
    if not token:
        return False

    # JWT format: header.payload.signature
    parts = token.split(".")
    if len(parts) != 3:
        return False

    # Each part should be base64url encoded
    import base64

    try:
        for part in parts:
            # Add padding if needed
            padded = part + "=" * (4 - len(part) % 4)
            base64.urlsafe_b64decode(padded)
        return True
    except Exception:
        return False


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    # Enums
    "Bundesland",
    "BuildingType",
    "Raumtyp",
    "MaterialKategorie",
    # Validation helpers
    "validate_positive",
    "validate_percentage",
    "validate_bundesland",
    "sanitize_string",
    "validate_api_key",
    "validate_jwt_format",
    # Validated models
    "ValidatedSchicht",
    "ValidatedUWertRequest",
    "ValidatedStellplatzRequest",
    "ValidatedFlaecheRequest",
    "ValidatedBarrierefreiheitRequest",
    "ValidatedFluchtwegRequest",
    "ValidatedSchallschutzRequest",
    "ValidatedHeizlastRequest",
    "ValidatedComplianceRequest",
    "ValidatedFileUpload",
]
