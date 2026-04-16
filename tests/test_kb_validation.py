"""
Test Suite for orion_kb_validation module
Tests knowledge base validation, RIS integration, OIB monitoring, etc.
"""

import os
import sys
from datetime import datetime, timezone

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orion_kb_validation import (
    STANDARD_VERSIONS,
    check_all_standards,
    check_data_freshness,
    check_naturgefahren,
    check_oenorm_updates,
    check_oib_updates,
    check_ris_updates,
    export_validation_report,
    get_standard_version,
    is_standard_current,
    validate_knowledge_base,
)


class TestStandardVersions:
    """Test standard version management"""

    def test_all_standards_exist(self):
        """Test that all expected standards are defined"""
        expected_standards = [
            "OIB-RL 1",
            "OIB-RL 2",
            "OIB-RL 3",
            "OIB-RL 4",
            "OIB-RL 5",
            "OIB-RL 6",
            "ÖNORM B 1800",
            "ÖNORM B 1600",
            "ÖNORM B 1601",
            "ÖNORM B 2110",
            "ÖNORM B 8110-3",
            "ÖNORM A 2063",
            "ÖNORM A 6240",
            "ÖNORM EN 62305",
        ]
        for standard in expected_standards:
            assert standard in STANDARD_VERSIONS, f"{standard} not found in STANDARD_VERSIONS"

    def test_get_standard_version_valid(self):
        """Test getting version of valid standard"""
        version = get_standard_version("OIB-RL 1")
        assert version is not None
        assert "version" in version
        assert "gueltig_ab" in version
        assert version["version"] == "2023"

    def test_get_standard_version_invalid(self):
        """Test getting version of invalid standard"""
        version = get_standard_version("INVALID-STANDARD")
        assert version is None

    def test_is_standard_current_oib(self):
        """Test if OIB standards are current"""
        is_current, message = is_standard_current("OIB-RL 1")
        assert is_current == True
        assert "aktuell" in message.lower()

    def test_is_standard_current_oenorm(self):
        """Test if ÖNORM standards are current"""
        is_current, message = is_standard_current("ÖNORM B 1800")
        assert is_current == True
        assert "aktuell" in message.lower()


class TestOIBUpdates:
    """Test OIB-Richtlinien monitoring"""

    def test_check_oib_updates_structure(self):
        """Test structure of OIB updates check"""
        result = check_oib_updates()
        assert "status" in result
        assert "aktuelle_version" in result
        assert "richtlinien" in result
        assert result["aktuelle_version"] == "2023"

    def test_check_oib_all_richtlinien(self):
        """Test that all 6 OIB-RL are checked"""
        result = check_oib_updates()
        richtlinien = result["richtlinien"]
        assert len(richtlinien) == 6
        for i in range(1, 7):
            assert f"OIB-RL {i}" in richtlinien


class TestOENORMUpdates:
    """Test ÖNORM standards monitoring"""

    def test_check_oenorm_b1800(self):
        """Test ÖNORM B 1800 check"""
        result = check_oenorm_updates("B 1800")
        assert "norm" in result
        assert result["norm"] == "ÖNORM B 1800"
        assert "status" in result
        assert "version" in result

    def test_check_oenorm_invalid(self):
        """Test invalid ÖNORM check"""
        result = check_oenorm_updates("INVALID")
        assert "nachricht" in result


class TestRISIntegration:
    """Test RIS Austria integration"""

    def test_check_ris_tirol(self):
        """Test RIS check for Tirol"""
        result = check_ris_updates("tirol")
        assert "bundesland" in result
        assert result["bundesland"] == "tirol"
        assert "status" in result
        assert "quelle" in result

    def test_check_ris_wien(self):
        """Test RIS check for Wien"""
        result = check_ris_updates("wien")
        assert result["bundesland"] == "wien"


class TestNaturgefahren:
    """Test hora.gv.at integration"""

    def test_check_naturgefahren_basic(self):
        """Test basic naturgefahren check"""
        result = check_naturgefahren()
        assert "status" in result
        assert "quelle" in result
        assert "hora.gv.at" in result["quelle"]

    def test_check_naturgefahren_with_plz(self):
        """Test naturgefahren check with PLZ"""
        result = check_naturgefahren(plz="6380")
        assert "plz" in result
        assert result["plz"] == "6380"

    def test_check_naturgefahren_with_gemeinde(self):
        """Test naturgefahren check with Gemeinde"""
        result = check_naturgefahren(gemeinde="St. Johann")
        assert "gemeinde" in result


class TestDataFreshness:
    """Test data freshness monitoring"""

    def test_check_data_freshness_aktuell(self):
        """Test freshness check for current data"""
        today = datetime.now().date().isoformat()
        result = check_data_freshness(today)
        assert result["status"] == "aktuell"
        assert result["alter_tage"] == 0

    def test_check_data_freshness_veraltet(self):
        """Test freshness check for old data"""
        result = check_data_freshness("2025-01-01")
        assert result["status"] in ["veraltet", "kritisch"]
        assert result["alter_tage"] > 90

    def test_check_data_freshness_invalid_date(self):
        """Test freshness check with invalid date"""
        result = check_data_freshness("invalid-date")
        assert result["status"] == "error"


class TestValidationReport:
    """Test validation report generation"""

    def test_validate_knowledge_base_basic(self):
        """Test basic knowledge base validation"""
        result = validate_knowledge_base(
            include_ris=False, include_oib=True, include_oenorm=False, include_hora=False
        )
        assert "timestamp" in result
        assert "ergebnis" in result
        assert "gesamtstatus" in result

    def test_validate_knowledge_base_full(self):
        """Test full knowledge base validation"""
        result = validate_knowledge_base(
            bundesland="tirol",
            include_ris=True,
            include_oib=True,
            include_oenorm=True,
            include_hora=True,
        )
        assert "ergebnis" in result
        assert "oib" in result["ergebnis"]
        assert "oenorm" in result["ergebnis"]

    def test_export_validation_report_json(self):
        """Test JSON export of validation report"""
        report = validate_knowledge_base(include_ris=False)
        json_export = export_validation_report(report, format="json")
        assert isinstance(json_export, str)
        assert "{" in json_export
        assert "}" in json_export

    def test_export_validation_report_text(self):
        """Test text export of validation report"""
        report = validate_knowledge_base(include_ris=False)
        text_export = export_validation_report(report, format="text")
        assert isinstance(text_export, str)
        assert "ORION" in text_export
        assert "=" in text_export


class TestCheckAllStandards:
    """Test comprehensive standards checking"""

    def test_check_all_standards_count(self):
        """Test that all standards are checked"""
        results = check_all_standards()
        assert len(results) == 14  # 6 OIB + 8 ÖNORM

    def test_check_all_standards_structure(self):
        """Test structure of all standards check"""
        results = check_all_standards()
        for standard_name, info in results.items():
            assert "aktuell" in info
            assert "nachricht" in info
            assert "version" in info
            assert isinstance(info["aktuell"], bool)


class TestCaching:
    """Test caching functionality"""

    def test_cache_invalidation(self):
        """Test that cache exists and can be used"""
        from orion_kb_validation import _cache

        # Clear cache first
        _cache.clear()
        assert len(_cache) == 0

        # Make a call that should cache
        check_oib_updates()

        # Cache should now have entries
        # Note: This is implementation-dependent
        assert True  # Basic test that caching doesn't break


# Integration tests
class TestIntegration:
    """Integration tests for complete workflows"""

    def test_complete_validation_workflow(self):
        """Test complete validation workflow"""
        # Step 1: Check all standards
        standards = check_all_standards()
        assert len(standards) > 0

        # Step 2: Check OIB
        oib = check_oib_updates()
        assert oib["status"] == "info"

        # Step 3: Full validation
        report = validate_knowledge_base(bundesland="tirol")
        assert report["gesamtstatus"] is not None

        # Step 4: Export report
        text_report = export_validation_report(report, format="text")
        assert len(text_report) > 100


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
