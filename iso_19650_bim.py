#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
ISO 19650 BIM Level 3 Compliance Module
═══════════════════════════════════════════════════════════════════════════

Implements ISO 19650 standards for Building Information Modeling:
- ISO 19650-1:2018 - Concepts and principles
- ISO 19650-2:2018 - Delivery phase of assets
- ISO 19650-3:2020 - Operational phase of assets
- ISO 19650-5:2020 - Security-minded approach

Integration with ÖNORM A 2063-2:2021 (BIM Level 3)

Features:
1. Exchange Information Requirements (EIR)
2. Asset Information Requirements (AIR)
3. Information Delivery Planning
4. Level of Information Need (LOIN)
5. Common Data Environment (CDE) structure
6. BIM Execution Plan (BEP)

Stand: April 2026
Lizenz: Apache 2.0
═══════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum
import json
import hashlib

# ═══════════════════════════════════════════════════════════════════════════
# ISO 19650 Enums and Constants
# ═══════════════════════════════════════════════════════════════════════════


class InformationDeliveryMilestone(str, Enum):
    """Information Delivery Milestones per ISO 19650-2"""

    STAGE_0_STRATEGIC_DEFINITION = "stage_0"
    STAGE_1_PREPARATION_BRIEF = "stage_1"
    STAGE_2_CONCEPT_DESIGN = "stage_2"
    STAGE_3_SPATIAL_COORDINATION = "stage_3"
    STAGE_4_TECHNICAL_DESIGN = "stage_4"
    STAGE_5_MANUFACTURING_CONSTRUCTION = "stage_5"
    STAGE_6_HANDOVER = "stage_6"
    STAGE_7_IN_USE = "stage_7"


class LevelOfInformationNeed(str, Enum):
    """Level of Information Need (LOIN) - ISO 19650"""

    LOD_100 = "LOD_100"  # Conceptual
    LOD_200 = "LOD_200"  # Approximate geometry
    LOD_300 = "LOD_300"  # Precise geometry
    LOD_350 = "LOD_350"  # Precise with connections
    LOD_400 = "LOD_400"  # Fabrication
    LOD_500 = "LOD_500"  # As-built


class CDEStatus(str, Enum):
    """Common Data Environment status workflow"""

    WIP = "work_in_progress"
    SHARED = "shared"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PurposeOfIssue(str, Enum):
    """Purpose of information exchange"""

    INFORMATION = "information"
    COMMENT = "comment"
    APPROVAL = "approval"
    CONSTRUCTION = "construction"
    AS_BUILT = "as_built"


# ═══════════════════════════════════════════════════════════════════════════
# ISO 19650 Data Classes
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class InformationRequirement:
    """
    Information Requirement per ISO 19650

    Specifies what information is needed, when, and to what level of detail
    """

    id: str
    description: str
    milestone: InformationDeliveryMilestone
    loin: LevelOfInformationNeed
    format: str  # IFC, PDF, DWG, etc.
    responsible_party: str
    delivery_date: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ExchangeInformationRequirements:
    """
    EIR - Exchange Information Requirements per ISO 19650-2

    Defines appointing party's information requirements for a project
    """

    project_id: str
    project_name: str
    appointing_party: str
    information_requirements: List[InformationRequirement] = field(default_factory=list)
    technical_requirements: Dict[str, Any] = field(default_factory=dict)
    management_requirements: Dict[str, Any] = field(default_factory=dict)
    commercial_requirements: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Export EIR to dictionary"""
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "appointing_party": self.appointing_party,
            "information_requirements": [
                {
                    "id": ir.id,
                    "description": ir.description,
                    "milestone": ir.milestone.value,
                    "loin": ir.loin.value,
                    "format": ir.format,
                    "responsible_party": ir.responsible_party,
                    "delivery_date": ir.delivery_date,
                    "metadata": ir.metadata or {},
                }
                for ir in self.information_requirements
            ],
            "technical_requirements": self.technical_requirements,
            "management_requirements": self.management_requirements,
            "commercial_requirements": self.commercial_requirements,
            "created_at": self.created_at,
            "version": self.version,
            "standard": "ISO 19650-2:2018",
        }


@dataclass
class AssetInformationRequirements:
    """
    AIR - Asset Information Requirements per ISO 19650-3

    Defines information needed for operational phase
    """

    asset_id: str
    asset_name: str
    owner: str
    operational_requirements: List[InformationRequirement] = field(default_factory=list)
    maintenance_requirements: Dict[str, Any] = field(default_factory=dict)
    performance_requirements: Dict[str, Any] = field(default_factory=dict)
    sustainability_requirements: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Export AIR to dictionary"""
        return {
            "asset_id": self.asset_id,
            "asset_name": self.asset_name,
            "owner": self.owner,
            "operational_requirements": [
                {
                    "id": ir.id,
                    "description": ir.description,
                    "milestone": ir.milestone.value,
                    "loin": ir.loin.value,
                    "format": ir.format,
                    "responsible_party": ir.responsible_party,
                    "delivery_date": ir.delivery_date,
                    "metadata": ir.metadata or {},
                }
                for ir in self.operational_requirements
            ],
            "maintenance_requirements": self.maintenance_requirements,
            "performance_requirements": self.performance_requirements,
            "sustainability_requirements": self.sustainability_requirements,
            "created_at": self.created_at,
            "version": self.version,
            "standard": "ISO 19650-3:2020",
        }


@dataclass
class BIMExecutionPlan:
    """
    BEP - BIM Execution Plan per ISO 19650-2

    Response to EIR from appointed party
    """

    project_id: str
    appointed_party: str
    delivery_team: List[str]
    information_delivery_strategy: str
    responsibility_matrix: Dict[str, str]  # Task -> Responsible party
    delivery_milestones: List[InformationDeliveryMilestone]
    software_platforms: List[str]
    data_exchange_protocols: List[str]
    quality_assurance_procedures: str
    security_strategy: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    version: str = "1.0"


@dataclass
class InformationContainer:
    """
    Information Container in Common Data Environment

    Represents a file or model in the CDE with ISO 19650 metadata
    """

    id: str
    name: str
    version: str
    status: CDEStatus
    purpose: PurposeOfIssue
    milestone: InformationDeliveryMilestone
    loin: LevelOfInformationNeed
    author: str
    file_format: str
    file_path: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    checksum: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Generate checksum if not provided"""
        if not self.checksum:
            data = f"{self.id}{self.name}{self.version}{self.created_at}"
            self.checksum = hashlib.sha256(data.encode()).hexdigest()[:16]


# ═══════════════════════════════════════════════════════════════════════════
# ISO 19650 Functions
# ═══════════════════════════════════════════════════════════════════════════


def erstelle_eir_template_oesterreich(
    projekt_name: str, auftraggeber: str, projekt_typ: str = "Neubau"
) -> ExchangeInformationRequirements:
    """
    Creates EIR template for Austrian construction project

    Combines ISO 19650-2 with ÖNORM A 2063-2:2021 requirements
    """

    # Standard information requirements for Austrian projects
    requirements = [
        InformationRequirement(
            id="EIR-001",
            description="Architectural Model (IFC 4.3)",
            milestone=InformationDeliveryMilestone.STAGE_4_TECHNICAL_DESIGN,
            loin=LevelOfInformationNeed.LOD_350,
            format="IFC",
            responsible_party="Architekt",
            delivery_date="",
            metadata={"oenorm": "A 2063-2:2021", "bim_level": 3},
        ),
        InformationRequirement(
            id="EIR-002",
            description="Structural Model (IFC 4.3)",
            milestone=InformationDeliveryMilestone.STAGE_4_TECHNICAL_DESIGN,
            loin=LevelOfInformationNeed.LOD_350,
            format="IFC",
            responsible_party="Statiker",
            delivery_date="",
            metadata={"oenorm": "B 1992", "bim_level": 3},
        ),
        InformationRequirement(
            id="EIR-003",
            description="MEP Model (IFC 4.3)",
            milestone=InformationDeliveryMilestone.STAGE_4_TECHNICAL_DESIGN,
            loin=LevelOfInformationNeed.LOD_350,
            format="IFC",
            responsible_party="HKLS Planer",
            delivery_date="",
            metadata={"oenorm": "H 5020", "bim_level": 3},
        ),
        InformationRequirement(
            id="EIR-004",
            description="Leistungsverzeichnis (ÖNORM A 2063)",
            milestone=InformationDeliveryMilestone.STAGE_5_MANUFACTURING_CONSTRUCTION,
            loin=LevelOfInformationNeed.LOD_400,
            format="GAEB-XML",
            responsible_party="Ausschreiber",
            delivery_date="",
            metadata={"oenorm": "A 2063-1:2024", "format": "GAEB DA XML 3.1"},
        ),
        InformationRequirement(
            id="EIR-005",
            description="As-Built Documentation",
            milestone=InformationDeliveryMilestone.STAGE_6_HANDOVER,
            loin=LevelOfInformationNeed.LOD_500,
            format="IFC",
            responsible_party="Bauunternehmer",
            delivery_date="",
            metadata={"oenorm": "B 1801-4", "bim_level": 3},
        ),
    ]

    return ExchangeInformationRequirements(
        project_id=hashlib.md5(projekt_name.encode()).hexdigest()[:8],
        project_name=projekt_name,
        appointing_party=auftraggeber,
        information_requirements=requirements,
        technical_requirements={
            "ifc_version": "IFC 4.3",
            "coordinate_system": "MGI / Austria GK",
            "unit_system": "Metric",
            "classification_systems": ["ÖNORM B 1801-1", "StLB-BAU"],
        },
        management_requirements={
            "cde_platform": "Required",
            "model_checking": "Solibri/Navisworks",
            "collaboration_frequency": "Weekly",
        },
        commercial_requirements={
            "liability": "ÖNORM B 2110:2013",
            "ip_rights": "Per Austrian Copyright Law",
        },
    )


def erstelle_air_template_oesterreich(
    asset_name: str, eigentümer: str
) -> AssetInformationRequirements:
    """
    Creates AIR template for Austrian asset management

    Combines ISO 19650-3 with Austrian operational requirements
    """

    operational_reqs = [
        InformationRequirement(
            id="AIR-001",
            description="Facility Management Model",
            milestone=InformationDeliveryMilestone.STAGE_7_IN_USE,
            loin=LevelOfInformationNeed.LOD_500,
            format="COBie",
            responsible_party="Facility Manager",
            delivery_date="",
            metadata={"standard": "COBie 2.4"},
        ),
        InformationRequirement(
            id="AIR-002",
            description="Maintenance Schedules",
            milestone=InformationDeliveryMilestone.STAGE_7_IN_USE,
            loin=LevelOfInformationNeed.LOD_500,
            format="PDF",
            responsible_party="Facility Manager",
            delivery_date="Quarterly",
            metadata={"oenorm": "B 1801-4"},
        ),
    ]

    return AssetInformationRequirements(
        asset_id=hashlib.md5(asset_name.encode()).hexdigest()[:8],
        asset_name=asset_name,
        owner=eigentümer,
        operational_requirements=operational_reqs,
        maintenance_requirements={
            "inspection_frequency": "Annual",
            "documentation_format": "Digital",
        },
        performance_requirements={
            "energy_monitoring": "Required",
            "comfort_monitoring": "Required",
        },
        sustainability_requirements={
            "certification": "klimaaktiv",
            "energy_class": "A++",
        },
    )


def validiere_iso_19650_compliance(
    information_container: InformationContainer, eir: ExchangeInformationRequirements
) -> Dict[str, Any]:
    """
    Validates if information container meets ISO 19650 and EIR requirements

    Returns compliance report
    """
    compliance = {"compliant": True, "issues": [], "warnings": []}

    # Check if file format matches requirements
    required_formats = [ir.format for ir in eir.information_requirements]
    if information_container.file_format not in required_formats:
        compliance["compliant"] = False
        compliance["issues"].append(
            f"File format {information_container.file_format} not in required formats: {required_formats}"
        )

    # Check LOIN level
    required_loin = [ir.loin for ir in eir.information_requirements]
    if information_container.loin not in required_loin:
        compliance["warnings"].append(
            f"LOIN {information_container.loin} may not match project requirements"
        )

    # Check CDE status workflow
    if information_container.status == CDEStatus.PUBLISHED:
        if information_container.purpose not in [
            PurposeOfIssue.APPROVAL,
            PurposeOfIssue.CONSTRUCTION,
        ]:
            compliance["warnings"].append(
                "Published status should have approval or construction purpose"
            )

    return compliance


# ═══════════════════════════════════════════════════════════════════════════
# Convenience Functions
# ═══════════════════════════════════════════════════════════════════════════


def erstelle_vollstaendiges_iso_19650_package(
    projekt_name: str, auftraggeber: str, projekt_typ: str = "Neubau"
) -> Dict[str, Any]:
    """
    Creates complete ISO 19650 information package

    Returns EIR, AIR templates, and BEP framework
    """

    eir = erstelle_eir_template_oesterreich(projekt_name, auftraggeber, projekt_typ)
    air = erstelle_air_template_oesterreich(projekt_name, auftraggeber)

    bep = BIMExecutionPlan(
        project_id=eir.project_id,
        appointed_party="TBD",
        delivery_team=[],
        information_delivery_strategy="Federated model approach with IFC coordination",
        responsibility_matrix={
            "Architectural Model": "Architekt",
            "Structural Model": "Statiker",
            "MEP Model": "HKLS Planer",
            "Coordination": "BIM Koordinator",
        },
        delivery_milestones=[
            InformationDeliveryMilestone.STAGE_2_CONCEPT_DESIGN,
            InformationDeliveryMilestone.STAGE_4_TECHNICAL_DESIGN,
            InformationDeliveryMilestone.STAGE_6_HANDOVER,
        ],
        software_platforms=["Revit", "ArchiCAD", "Solibri", "Navisworks"],
        data_exchange_protocols=["IFC 4.3", "BCF 2.1"],
        quality_assurance_procedures="Weekly model checks, clash detection, ÖNORM compliance verification",
        security_strategy="ISO 19650-5 compliant, encrypted CDE, role-based access control",
    )

    return {
        "eir": eir.to_dict(),
        "air": air.to_dict(),
        "bep": {
            "project_id": bep.project_id,
            "appointed_party": bep.appointed_party,
            "delivery_team": bep.delivery_team,
            "information_delivery_strategy": bep.information_delivery_strategy,
            "responsibility_matrix": bep.responsibility_matrix,
            "delivery_milestones": [m.value for m in bep.delivery_milestones],
            "software_platforms": bep.software_platforms,
            "data_exchange_protocols": bep.data_exchange_protocols,
            "quality_assurance_procedures": bep.quality_assurance_procedures,
            "security_strategy": bep.security_strategy,
            "created_at": bep.created_at,
            "version": bep.version,
            "standard": "ISO 19650-2:2018",
        },
        "metadata": {
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "standards": [
                "ISO 19650-1:2018",
                "ISO 19650-2:2018",
                "ISO 19650-3:2020",
                "ISO 19650-5:2020",
                "ÖNORM A 2063-2:2021",
            ],
        },
    }
