"""
Tests for ORION Laws Registry System
"""

import pytest
from datetime import datetime

from api.laws.models import (
    AustrianLawModel,
    ComplianceMappingModel,
    LawVersionModel,
)
from api.laws.registry import get_registry, LawsRegistry


class TestLawsRegistry:
    """Test cases for Laws Registry"""

    @pytest.fixture
    def registry(self):
        """Get registry instance"""
        return get_registry()

    def test_registry_initialization(self, registry):
        """Test that registry initializes with laws"""
        assert registry is not None
        assert len(registry.laws) > 0
        assert len(registry.compliance_mappings) > 0

    def test_get_all_laws(self, registry):
        """Test getting all laws"""
        laws = registry.list_all_laws()
        assert len(laws) > 0
        assert all(isinstance(law, AustrianLawModel) for law in laws)

    def test_get_oib_richtlinien(self, registry):
        """Test getting OIB-RL standards"""
        oib_laws = registry.get_oib_richtlinien()
        assert len(oib_laws) == 7  # OIB-RL 1-7
        for law in oib_laws:
            assert law.type == "OIB-RL"

    def test_get_oenorm_standards(self, registry):
        """Test getting ÖNORM standards"""
        oenorm_laws = registry.get_oenorm_standards()
        assert len(oenorm_laws) > 0
        for law in oenorm_laws:
            assert law.type == "ÖNORM"

    def test_get_law_by_id(self, registry):
        """Test getting specific law"""
        law = registry.get_law("OIB-RL-1-2023")
        assert law is not None
        assert law.law_id == "OIB-RL-1-2023"
        assert law.name == "OIB-Richtlinie 1: Mechanische Festigkeit und Standsicherheit"

    def test_get_nonexistent_law(self, registry):
        """Test getting nonexistent law"""
        law = registry.get_law("NONEXISTENT-LAW")
        assert law is None

    def test_get_current_version(self, registry):
        """Test getting current version of law"""
        version = registry.get_current_version("OIB-RL-6-2023")
        assert version is not None
        assert version.version_id == "2023-v1"
        assert not version.deprecated

    def test_get_law_versions(self, registry):
        """Test getting all versions of law"""
        versions = registry.get_law_versions("OIB-RL-1-2023")
        assert len(versions) > 0
        assert all(isinstance(v, LawVersionModel) for v in versions)

    def test_get_laws_for_bundesland(self, registry):
        """Test getting laws for specific Bundesland"""
        wien_laws = registry.get_laws_for_bundesland("wien")
        assert len(wien_laws) > 0

    def test_salzburg_special_case(self, registry):
        """Test Salzburg special energy rules"""
        salzburg_is_special = registry.is_salzburg_special_case("salzburg")
        assert salzburg_is_special is True

        wien_is_special = registry.is_salzburg_special_case("wien")
        assert wien_is_special is False

    def test_get_salzburg_laws(self, registry):
        """Test getting Salzburg-specific laws"""
        salzburg_laws = registry.get_laws_for_bundesland("salzburg")
        # Should include SALZBURG-WSCHVO
        salzburg_law_ids = [law.law_id for law in salzburg_laws]
        assert "SALZBURG-WSCHVO-2024" in salzburg_law_ids

    def test_get_compliance_checks_for_law(self, registry):
        """Test getting compliance checks for law"""
        checks = registry.get_compliance_checks_for_law("OIB-RL-1-2023")
        assert len(checks) > 0

    def test_get_mandatory_checks_for_law(self, registry):
        """Test getting mandatory checks for law"""
        checks = registry.get_mandatory_checks_for_law("OIB-RL-6-2023")
        assert len(checks) > 0
        assert all(check.type == "mandatory" for check in checks)

    def test_was_law_valid_at(self, registry):
        """Test checking if law was valid at specific time"""
        # Test with a date after OIB-RL 6 came into force
        test_date = "2023-06-01T00:00:00Z"
        was_valid = registry.was_law_valid_at("OIB-RL-6-2023", test_date)
        assert was_valid is True

    def test_get_regional_variant_note(self, registry):
        """Test getting regional variant notes"""
        # Salzburg has special note for OIB-RL 6
        note = registry.get_regional_variant_note("OIB-RL-6-2023", "salzburg")
        assert note is not None
        assert "WSchVO" in note

    def test_get_related_standards(self, registry):
        """Test getting related standards"""
        standards = registry.get_related_standards("OIB-RL-1-2023")
        assert len(standards) > 0
        assert "EN 1990" in standards

    def test_export_law_as_audit_info(self, registry):
        """Test exporting law as audit info"""
        audit_info = registry.export_law_as_audit_info(
            "OIB-RL-1-2023", checks_performed=["check_oib_rl_1_structural"]
        )
        assert "law_id" in audit_info
        assert "law_version" in audit_info
        assert "version_id" in audit_info
        assert audit_info["law_id"] == "OIB-RL-1-2023"
        assert "check_oib_rl_1_structural" in audit_info["checks_performed"]

    def test_get_statistics(self, registry):
        """Test getting registry statistics"""
        stats = registry.get_statistics()
        assert stats["total_laws"] > 0
        assert stats["total_compliance_mappings"] > 0
        assert stats["oib_richtlinien"] == 7
        assert "laws_by_type" in stats

    def test_registry_singleton(self):
        """Test that registry is a singleton"""
        registry1 = get_registry()
        registry2 = get_registry()
        assert registry1 is registry2


class TestComplianceMappings:
    """Test cases for compliance mappings"""

    @pytest.fixture
    def registry(self):
        """Get registry instance"""
        return get_registry()

    def test_get_compliance_mapping(self, registry):
        """Test getting compliance mapping"""
        mapping = registry.get_compliance_mapping("COMPL-OIB-RL-1-2023")
        assert mapping is not None
        assert isinstance(mapping, ComplianceMappingModel)

    def test_get_mappings_for_law(self, registry):
        """Test getting all mappings for a law"""
        mappings = registry.get_mappings_for_law("OIB-RL-6-2023")
        assert len(mappings) > 0

    def test_get_check_by_id(self, registry):
        """Test finding specific check"""
        check = registry.get_check_by_id("check_oib_rl_1_structural")
        assert check is not None
        assert check.check_id == "check_oib_rl_1_structural"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
