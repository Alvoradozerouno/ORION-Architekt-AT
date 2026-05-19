"""
ORION Laws Registry Data Models

Pydantic models for law versions, compliance mappings, and audit trails.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LawVersionModel(BaseModel):
    """Single version of a law or standard"""

    version_id: str = Field(..., description="Unique version identifier (e.g., '2023-v1')")
    version: str = Field(..., description="Version number (e.g., '2023')")
    valid_from: str = Field(..., description="ISO 8601 date when version becomes valid")
    valid_to: Optional[str] = Field(None, description="ISO 8601 date when version expires")
    source_url: Optional[str] = Field(None, description="URL to official document")
    pdf_hash: Optional[str] = Field(None, description="SHA256 hash of PDF document")
    published_at: str = Field(..., description="When version was published (ISO 8601)")
    deprecated: bool = Field(False, description="Whether this version is deprecated")
    changes: List[str] = Field(default_factory=list, description="List of changes in this version")

    class Config:
        json_schema_extra = {
            "example": {
                "version_id": "2023-v1",
                "version": "2023",
                "valid_from": "2023-05-25",
                "valid_to": None,
                "source_url": "https://www.oib.or.at/...",
                "pdf_hash": "sha256:abc123...",
                "published_at": "2023-05-25T00:00:00Z",
                "deprecated": False,
                "changes": ["Modernisierte Anforderungen", "Eurocode Anpassung"],
            }
        }


class AustrianLawModel(BaseModel):
    """Complete law record with all versions and metadata"""

    law_id: str = Field(..., description="Unique law identifier (e.g., 'OIB-RL-1-2023')")
    name: str = Field(..., description="Full name of the law or standard")
    type: str = Field(..., description="Type (OIB-RL, ÖNORM, EN, etc.)")
    number: Optional[int] = Field(None, description="Law/standard number if applicable")
    versions: List[LawVersionModel] = Field(..., description="List of all versions")
    bundeslaender_abweichungen: Dict[str, str] = Field(
        default_factory=dict, description="Regional deviations per Bundesland"
    )
    related_standards: List[str] = Field(
        default_factory=list, description="Related standards (e.g., EN 1991-1-1)"
    )
    compliance_checks: List[str] = Field(
        default_factory=list, description="Function names for compliance checks"
    )
    mandatory_for: List[str] = Field(
        default_factory=list, description="Building types this applies to"
    )
    ziviltechniker_required: bool = Field(
        False, description="Whether Ziviltechniker signature required"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "law_id": "OIB-RL-1-2023",
                "name": "OIB-Richtlinie 1: Mechanische Festigkeit und Standsicherheit",
                "type": "OIB-RL",
                "number": 1,
                "versions": [
                    {
                        "version_id": "2023-v1",
                        "version": "2023",
                        "valid_from": "2023-05-25",
                    }
                ],
            }
        }


class ComplianceCheckModel(BaseModel):
    """Single compliance check definition"""

    check_id: str = Field(..., description="Unique check identifier")
    name: str = Field(..., description="Human-readable check name")
    type: str = Field(..., description="Check type: mandatory, recommended, informational")
    validation_function: Optional[str] = Field(None, description="Python function path")
    audit_trail_event: str = Field(..., description="Event type for audit trail")
    result_fields: List[str] = Field(
        default_factory=list, description="Fields that will be returned in result"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "check_id": "check_oib_rl_1_structural",
                "name": "Statische Berechnung erforderlich",
                "type": "mandatory",
                "validation_function": "api.routers.compliance._check_oib_rl_1",
                "audit_trail_event": "compliance_check/oib_rl_1_structural",
                "result_fields": ["status", "details", "referenced_law_version"],
            }
        }


class ComplianceMappingModel(BaseModel):
    """Mapping between laws and compliance checks"""

    mapping_id: str = Field(..., description="Unique mapping identifier")
    law_version: str = Field(..., description="Law version this mapping applies to")
    checks: List[ComplianceCheckModel] = Field(..., description="Compliance checks for this law")

    class Config:
        json_schema_extra = {
            "example": {
                "mapping_id": "COMPL-001",
                "law_version": "OIB-RL-1-2023/2023-v1",
                "checks": [{"check_id": "check_oib_rl_1_structural"}],
            }
        }


class LawAuditTrailModel(BaseModel):
    """Law version information for audit trail"""

    law_id: str = Field(..., description="Law identifier")
    law_version: str = Field(..., description="Full version string")
    version_id: str = Field(..., description="Version ID within the law")
    valid_from: str = Field(..., description="When this version became valid")
    valid_to: Optional[str] = Field(None, description="When this version expires")
    valid_at_calculation_time: bool = Field(..., description="Was law valid at calculation time?")
    checks_performed: List[str] = Field(default_factory=list, description="Checks performed")

    class Config:
        json_schema_extra = {
            "example": {
                "law_id": "OIB-RL-1-2023",
                "law_version": "OIB-RL-1-2023/2023-v1",
                "version_id": "2023-v1",
                "valid_from": "2023-05-25",
                "valid_to": None,
                "valid_at_calculation_time": True,
                "checks_performed": ["structural_safety", "foundations"],
            }
        }


class TransparencyCalculationModel(BaseModel):
    """Transparent view of what laws were checked in a calculation"""

    calculation_id: str = Field(..., description="Calculation identifier")
    project_id: str = Field(..., description="Project identifier")
    timestamp: str = Field(..., description="When calculation was performed (ISO 8601)")
    laws_referenced: List[LawAuditTrailModel] = Field(
        ..., description="All laws/standards referenced"
    )
    audit_trail_id: Optional[str] = Field(None, description="Link to audit trail entry")

    class Config:
        json_schema_extra = {
            "example": {
                "calculation_id": "CALC_123",
                "project_id": "PROJ_456",
                "timestamp": "2026-04-15T10:30:00Z",
                "laws_referenced": [],
            }
        }
