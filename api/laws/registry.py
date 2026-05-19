"""
ORION Central Laws Registry

Manages all Austrian building laws, standards, and their versions.
Acts as single source of truth for compliance checks and audit trails.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from api.laws.models import (
    AustrianLawModel,
    ComplianceMappingModel,
    ComplianceCheckModel,
    LawVersionModel,
)

logger = logging.getLogger(__name__)


class LawsRegistry:
    """Central registry for all Austrian building laws and standards"""

    def __init__(self):
        """Initialize registry by loading JSON data"""
        self.laws: Dict[str, AustrianLawModel] = {}
        self.compliance_mappings: Dict[str, ComplianceMappingModel] = {}
        self._load_laws()
        self._load_compliance_mappings()
        logger.info(f"✅ Laws Registry initialized: {len(self.laws)} laws, {len(self.compliance_mappings)} compliance mappings")

    def _load_laws(self):
        """Load laws from JSON file"""
        data_dir = Path(__file__).parent / "data"
        laws_file = data_dir / "austrian_laws.json"

        if not laws_file.exists():
            logger.warning(f"Laws file not found: {laws_file}")
            return

        try:
            with open(laws_file, "r", encoding="utf-8") as f:
                laws_data = json.load(f)

            for law_data in laws_data:
                law_model = AustrianLawModel(**law_data)
                self.laws[law_model.law_id] = law_model
                logger.debug(f"Loaded law: {law_model.law_id}")
        except Exception as e:
            logger.error(f"Failed to load laws: {e}")
            raise

    def _load_compliance_mappings(self):
        """Load compliance mappings from JSON file"""
        data_dir = Path(__file__).parent / "data"
        mappings_file = data_dir / "compliance_mapping.json"

        if not mappings_file.exists():
            logger.warning(f"Compliance mappings file not found: {mappings_file}")
            return

        try:
            with open(mappings_file, "r", encoding="utf-8") as f:
                mappings_data = json.load(f)

            for mapping_data in mappings_data:
                mapping_model = ComplianceMappingModel(**mapping_data)
                self.compliance_mappings[mapping_model.mapping_id] = mapping_model
                logger.debug(f"Loaded compliance mapping: {mapping_model.mapping_id}")
        except Exception as e:
            logger.error(f"Failed to load compliance mappings: {e}")
            raise

    # =========================================================================
    # Law Queries
    # =========================================================================

    def get_law(self, law_id: str) -> Optional[AustrianLawModel]:
        """Get a specific law by ID"""
        return self.laws.get(law_id)

    def list_all_laws(self) -> List[AustrianLawModel]:
        """Get all laws"""
        return list(self.laws.values())

    def get_laws_by_type(self, law_type: str) -> List[AustrianLawModel]:
        """Get all laws of a specific type"""
        return [law for law in self.laws.values() if law.type == law_type]

    def get_oib_richtlinien(self) -> List[AustrianLawModel]:
        """Get all OIB-RL standards"""
        return self.get_laws_by_type("OIB-RL")

    def get_oenorm_standards(self) -> List[AustrianLawModel]:
        """Get all ÖNORM standards"""
        return self.get_laws_by_type("ÖNORM")

    def get_laws_for_bundesland(self, bundesland: str) -> List[AustrianLawModel]:
        """Get all laws applicable to a specific Bundesland, including regional variants"""
        applicable_laws = []
        for law in self.laws.values():
            # Always include laws without regional variants
            if not law.bundeslaender_abweichungen:
                applicable_laws.append(law)
            # Include if there's a specific variant for this Bundesland
            elif bundesland.lower() in law.bundeslaender_abweichungen:
                applicable_laws.append(law)
            # For Salzburg WSchVO: only if Salzburg
            elif "SALZBURG" in law.law_id.upper() and bundesland.lower() == "salzburg":
                applicable_laws.append(law)

        return applicable_laws

    def get_current_version(self, law_id: str) -> Optional[LawVersionModel]:
        """Get current (non-deprecated, valid) version of a law"""
        law = self.get_law(law_id)
        if not law:
            return None

        now = datetime.now().isoformat()

        for version in law.versions:
            # Check if deprecated
            if version.deprecated:
                continue

            # Check if currently valid
            if version.valid_from <= now:
                if version.valid_to is None or version.valid_to >= now:
                    return version

        # Fallback: return latest non-deprecated version
        for version in reversed(law.versions):
            if not version.deprecated:
                return version

        return None

    def get_law_version(self, law_id: str, version_id: str) -> Optional[LawVersionModel]:
        """Get specific version of a law"""
        law = self.get_law(law_id)
        if not law:
            return None

        for version in law.versions:
            if version.version_id == version_id:
                return version

        return None

    def get_law_versions(self, law_id: str) -> List[LawVersionModel]:
        """Get all versions of a law"""
        law = self.get_law(law_id)
        if not law:
            return []

        return law.versions

    def was_law_valid_at(self, law_id: str, timestamp: str) -> bool:
        """Check if a law was valid at a specific timestamp"""
        law = self.get_law(law_id)
        if not law:
            return False

        for version in law.versions:
            if version.valid_from <= timestamp:
                if version.valid_to is None or version.valid_to >= timestamp:
                    return True

        return False

    def get_applicable_version_at(self, law_id: str, timestamp: str) -> Optional[LawVersionModel]:
        """Get which version of a law was applicable at a specific timestamp"""
        law = self.get_law(law_id)
        if not law:
            return None

        for version in law.versions:
            if version.valid_from <= timestamp:
                if version.valid_to is None or version.valid_to >= timestamp:
                    return version

        return None

    # =========================================================================
    # Compliance Queries
    # =========================================================================

    def get_compliance_mapping(self, mapping_id: str) -> Optional[ComplianceMappingModel]:
        """Get a specific compliance mapping by ID"""
        return self.compliance_mappings.get(mapping_id)

    def get_mappings_for_law(self, law_id: str) -> List[ComplianceMappingModel]:
        """Get all compliance mappings for a specific law"""
        mappings = []
        for mapping in self.compliance_mappings.values():
            if law_id in mapping.law_version:
                mappings.append(mapping)
        return mappings

    def get_compliance_checks_for_law(self, law_id: str) -> List[ComplianceCheckModel]:
        """Get all compliance checks defined for a law"""
        checks = []
        mappings = self.get_mappings_for_law(law_id)
        for mapping in mappings:
            checks.extend(mapping.checks)
        return checks

    def get_check_by_id(self, check_id: str) -> Optional[ComplianceCheckModel]:
        """Find a compliance check by its ID"""
        for mapping in self.compliance_mappings.values():
            for check in mapping.checks:
                if check.check_id == check_id:
                    return check
        return None

    def get_mandatory_checks_for_law(self, law_id: str) -> List[ComplianceCheckModel]:
        """Get all mandatory compliance checks for a law"""
        all_checks = self.get_compliance_checks_for_law(law_id)
        return [check for check in all_checks if check.type == "mandatory"]

    # =========================================================================
    # Special Queries
    # =========================================================================

    def get_ziviltechniker_required_for_project(self, bundesland: str, building_type: str = "buildings") -> List[str]:
        """Get list of laws requiring Ziviltechniker signature for this project"""
        applicable_laws = self.get_laws_for_bundesland(bundesland)
        return [
            law.law_id
            for law in applicable_laws
            if law.ziviltechniker_required and building_type in law.mandatory_for
        ]

    def is_salzburg_special_case(self, bundesland: str) -> bool:
        """Check if Salzburg with its special energy rules"""
        return bundesland.lower() == "salzburg"

    def get_regional_variant_note(self, law_id: str, bundesland: str) -> Optional[str]:
        """Get any regional variant notes for this law"""
        law = self.get_law(law_id)
        if not law or not law.bundeslaender_abweichungen:
            return None

        return law.bundeslaender_abweichungen.get(bundesland.lower())

    def get_related_standards(self, law_id: str) -> List[str]:
        """Get related standards for a law"""
        law = self.get_law(law_id)
        if not law:
            return []

        return law.related_standards

    # =========================================================================
    # Versioning & Audit
    # =========================================================================

    def export_law_as_audit_info(self, law_id: str, checks_performed: Optional[List[str]] = None) -> Dict[str, Any]:
        """Export law information suitable for audit trail"""
        law = self.get_law(law_id)
        if not law:
            return {}

        current_version = self.get_current_version(law_id)
        if not current_version:
            return {}

        now = datetime.now().isoformat()
        return {
            "law_id": law.law_id,
            "law_version": f"{law.law_id}/{current_version.version_id}",
            "version_id": current_version.version_id,
            "valid_from": current_version.valid_from,
            "valid_to": current_version.valid_to,
            "valid_at_calculation_time": self.was_law_valid_at(law_id, now),
            "checks_performed": checks_performed or [],
        }

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "total_laws": len(self.laws),
            "total_compliance_mappings": len(self.compliance_mappings),
            "oib_richtlinien": len(self.get_oib_richtlinien()),
            "oenorm_standards": len(self.get_oenorm_standards()),
            "laws_by_type": {
                law_type: len(self.get_laws_by_type(law_type))
                for law_type in set(law.type for law in self.laws.values())
            },
        }


# Singleton instance
_registry_instance: Optional[LawsRegistry] = None


def get_registry() -> LawsRegistry:
    """Get or create the singleton registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = LawsRegistry()
    return _registry_instance
