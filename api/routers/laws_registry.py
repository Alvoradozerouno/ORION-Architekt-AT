"""
ORION Laws Registry API Router

Public API endpoints for accessing Austrian building laws and standards.
Provides transparency, audit trails, and compliance mapping information.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from api.laws.models import (
    AustrianLawModel,
    ComplianceMappingModel,
    LawAuditTrailModel,
    TransparencyCalculationModel,
)
from api.laws.registry import get_registry

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/laws",
    tags=["laws-registry"],
)


# =============================================================================
# Pydantic Response Models
# =============================================================================


class LawDetailResponse(BaseModel):
    """Detailed law information"""

    law_id: str
    name: str
    type: str
    number: Optional[int] = None
    current_version_id: Optional[str] = None
    total_versions: int
    is_current: bool
    mandatory_for: List[str]
    ziviltechniker_required: bool
    bundeslaender_abweichungen: dict = {}
    related_standards: List[str] = []
    compliance_checks_count: int


class LawVersionDetailResponse(BaseModel):
    """Detailed law version information"""

    version_id: str
    version: str
    valid_from: str
    valid_to: Optional[str]
    published_at: str
    deprecated: bool
    changes: List[str]
    source_url: Optional[str]


class ComplianceCheckDetailResponse(BaseModel):
    """Detailed compliance check information"""

    check_id: str
    name: str
    type: str
    law_id: str
    validation_function: Optional[str]
    audit_trail_event: str
    result_fields: List[str]


class RegistryStatsResponse(BaseModel):
    """Registry statistics"""

    total_laws: int
    total_compliance_mappings: int
    oib_richtlinien: int
    oenorm_standards: int
    laws_by_type: dict


# =============================================================================
# API Endpoints
# =============================================================================


@router.get("/", response_model=List[LawDetailResponse])
async def list_all_laws(
    law_type: Optional[str] = Query(None, description="Filter by law type (OIB-RL, ÖNORM, etc.)"),
    bundesland: Optional[str] = Query(None, description="Filter by Bundesland"),
):
    """
    📋 **List All Austrian Building Laws**

    Returns all available laws and standards in the central registry.

    Query Parameters:
    - `law_type`: Filter by type (OIB-RL, ÖNORM, EN, etc.)
    - `bundesland`: Get laws specific to a Bundesland including regional variants

    Returns list of laws with current version info.
    """
    registry = get_registry()

    if bundesland:
        laws = registry.get_laws_for_bundesland(bundesland)
    elif law_type:
        laws = registry.get_laws_by_type(law_type)
    else:
        laws = registry.list_all_laws()

    results = []
    for law in laws:
        current_version = registry.get_current_version(law.law_id)
        checks = registry.get_compliance_checks_for_law(law.law_id)

        results.append(
            LawDetailResponse(
                law_id=law.law_id,
                name=law.name,
                type=law.type,
                number=law.number,
                current_version_id=current_version.version_id if current_version else None,
                total_versions=len(law.versions),
                is_current=current_version is not None,
                mandatory_for=law.mandatory_for,
                ziviltechniker_required=law.ziviltechniker_required,
                bundeslaender_abweichungen=law.bundeslaender_abweichungen,
                related_standards=law.related_standards,
                compliance_checks_count=len(checks),
            )
        )

    return results


@router.get("/{law_id}", response_model=LawDetailResponse)
async def get_law_detail(law_id: str):
    """
    🔍 **Get Law Details**

    Returns detailed information about a specific law including:
    - Current version information
    - Regional variants
    - Related standards
    - Associated compliance checks
    - Ziviltechniker requirements

    Parameters:
    - `law_id`: Law identifier (e.g., OIB-RL-1-2023, OENORM-B-1800-2013)
    """
    registry = get_registry()
    law = registry.get_law(law_id)

    if not law:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Law not found: {law_id}")

    current_version = registry.get_current_version(law_id)
    checks = registry.get_compliance_checks_for_law(law_id)

    return LawDetailResponse(
        law_id=law.law_id,
        name=law.name,
        type=law.type,
        number=law.number,
        current_version_id=current_version.version_id if current_version else None,
        total_versions=len(law.versions),
        is_current=current_version is not None,
        mandatory_for=law.mandatory_for,
        ziviltechniker_required=law.ziviltechniker_required,
        bundeslaender_abweichungen=law.bundeslaender_abweichungen,
        related_standards=law.related_standards,
        compliance_checks_count=len(checks),
    )


@router.get("/{law_id}/versions", response_model=List[LawVersionDetailResponse])
async def get_law_versions(law_id: str):
    """
    📜 **Get Law Version History**

    Returns complete version history of a law including:
    - All versions (current and deprecated)
    - Valid date ranges
    - Changes in each version
    - Source documentation

    Parameters:
    - `law_id`: Law identifier
    """
    registry = get_registry()
    versions = registry.get_law_versions(law_id)

    if not versions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Law not found: {law_id}")

    return [
        LawVersionDetailResponse(
            version_id=v.version_id,
            version=v.version,
            valid_from=v.valid_from,
            valid_to=v.valid_to,
            published_at=v.published_at,
            deprecated=v.deprecated,
            changes=v.changes,
            source_url=v.source_url,
        )
        for v in versions
    ]


@router.get("/{law_id}/versions/{version_id}", response_model=LawVersionDetailResponse)
async def get_specific_version(law_id: str, version_id: str):
    """
    🔎 **Get Specific Law Version**

    Returns information about a specific version of a law.

    Parameters:
    - `law_id`: Law identifier
    - `version_id`: Version identifier (e.g., 2023-v1)
    """
    registry = get_registry()
    version = registry.get_law_version(law_id, version_id)

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Version not found: {law_id}/{version_id}"
        )

    return LawVersionDetailResponse(
        version_id=version.version_id,
        version=version.version,
        valid_from=version.valid_from,
        valid_to=version.valid_to,
        published_at=version.published_at,
        deprecated=version.deprecated,
        changes=version.changes,
        source_url=version.source_url,
    )


@router.get("/bundesland/{bundesland}", response_model=List[LawDetailResponse])
async def get_laws_for_bundesland(bundesland: str):
    """
    🏛️ **Get Laws for Bundesland**

    Returns all applicable laws for a specific Bundesland, including:
    - Regional variants and special rules (e.g., Salzburg WSchVO)
    - Mandatory and optional standards
    - Local Ziviltechniker requirements

    Parameters:
    - `bundesland`: Bundesland name (wien, salzburg, oberösterreich, etc.)
    """
    registry = get_registry()
    laws = registry.get_laws_for_bundesland(bundesland)

    if not laws:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No laws found for: {bundesland}"
        )

    results = []
    for law in laws:
        current_version = registry.get_current_version(law.law_id)
        checks = registry.get_compliance_checks_for_law(law.law_id)
        regional_note = registry.get_regional_variant_note(law.law_id, bundesland)

        result = LawDetailResponse(
            law_id=law.law_id,
            name=law.name,
            type=law.type,
            number=law.number,
            current_version_id=current_version.version_id if current_version else None,
            total_versions=len(law.versions),
            is_current=current_version is not None,
            mandatory_for=law.mandatory_for,
            ziviltechniker_required=law.ziviltechniker_required,
            bundeslaender_abweichungen={bundesland: regional_note} if regional_note else {},
            related_standards=law.related_standards,
            compliance_checks_count=len(checks),
        )
        results.append(result)

    return results


@router.get("/{law_id}/compliance-mapping", response_model=List[ComplianceCheckDetailResponse])
async def get_compliance_mapping(law_id: str):
    """
    ✅ **Get Compliance Mapping for Law**

    Returns all compliance checks that are automatically performed for a specific law:
    - Check identifiers
    - Validation functions
    - Audit trail event types
    - Result fields

    This helps transparency about which laws drive which checks.

    Parameters:
    - `law_id`: Law identifier
    """
    registry = get_registry()
    checks = registry.get_compliance_checks_for_law(law_id)

    if not checks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No compliance mappings found for: {law_id}"
        )

    return [
        ComplianceCheckDetailResponse(
            check_id=check.check_id,
            name=check.name,
            type=check.type,
            law_id=law_id,
            validation_function=check.validation_function,
            audit_trail_event=check.audit_trail_event,
            result_fields=check.result_fields,
        )
        for check in checks
    ]


@router.post("/validate-current", response_model=dict)
async def validate_current_laws():
    """
    🔄 **Validate Current Laws Against External Sources**

    Checks if all laws in the registry are still current by validating against:
    - RIS Austria (Rechtsinformationssystem)
    - OIB (https://www.oib.or.at)
    - ÖNORM standards database

    Returns validation results for each law.

    ⚠️ This operation may take several seconds as it contacts external services.
    """
    registry = get_registry()

    # TODO: Implement actual external validation
    validation_results = {
        "checked_at": datetime.now().isoformat(),
        "total_laws": len(registry.laws),
        "validation_status": "not_implemented",
        "message": "External validation not yet implemented. See api/laws/validation/ for integration points.",
        "details": [],
    }

    return validation_results


@router.get("/transparency/calculations/{calc_id}", response_model=TransparencyCalculationModel)
async def get_calculation_transparency(calc_id: str):
    """
    👁️ **Transparency: Which Laws Were Checked?**

    Returns detailed information about which laws and standards were checked
    for a specific calculation, including:
    - Law versions that were applicable at calculation time
    - Which compliance checks were performed
    - Results for each law
    - Immutable audit trail link

    This endpoint provides the transparency required for:
    - Ziviltechniker to verify compliance
    - Auditors to trace legal compliance
    - Building authorities to review approval basis

    Parameters:
    - `calc_id`: Calculation identifier

    Note: This is a placeholder. Actual implementation requires integration
    with the audit trail system to retrieve historical law versions.
    """
    # In a real implementation, this would:
    # 1. Look up the calculation in audit trail
    # 2. Retrieve the audit entry with law_version details
    # 3. Return full transparency including all laws checked

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Transparency endpoint requires integration with audit trail system. "
        "This will be enabled once audit trail modifications are complete.",
    )


@router.get("/audit/compliance-trail/{project_id}", response_model=dict)
async def get_compliance_audit_trail(project_id: str):
    """
    📋 **Get Compliance Audit Trail with Law Versions**

    Returns the complete audit trail for a project showing:
    - Which laws were checked
    - What version of each law was used
    - When each check was performed
    - Results and any changes over time

    This is the immutable record proving compliance at time of calculation.

    Parameters:
    - `project_id`: Project identifier
    """
    # In a real implementation, this would retrieve audit trail entries
    # filtered by project_id and enhanced with law version information

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Audit trail retrieval requires integration with audit trail system.",
    )


@router.get("/stats", response_model=RegistryStatsResponse)
async def get_registry_stats():
    """
    📊 **Registry Statistics**

    Returns statistics about the laws registry:
    - Total number of laws
    - Breakdown by type (OIB-RL, ÖNORM, EN, etc.)
    - Compliance mapping coverage
    """
    registry = get_registry()
    stats = registry.get_statistics()

    return RegistryStatsResponse(**stats)
