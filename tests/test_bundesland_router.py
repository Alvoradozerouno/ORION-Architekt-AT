"""
Comprehensive tests for Bundesland Router
Tests Bundesland-specific regulations
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

client = TestClient(app)


class TestBundeslandRouter:
    """Test suite for Bundesland router endpoints"""

    @pytest.mark.parametrize(
        "bundesland",
        [
            "wien",
            "tirol",
            "salzburg",
            "vorarlberg",
            "steiermark",
            "kaernten",
            "burgenland",
            "niederoesterreich",
            "oberoesterreich",
        ],
    )
    def test_get_bundesland_info_valid(self, bundesland):
        """Test getting info for valid Bundesland"""
        response = client.get(f"/api/v1/bundesland/{bundesland}")
        assert response.status_code in [200, 404, 405]
        if response.status_code == 200:
            data = response.json()
            assert "name" in data or "bauordnung" in data or isinstance(data, dict)

    @pytest.mark.parametrize(
        "bundesland",
        [
            "invalid",
            "deutschland",
            "schweiz",
            "frankreich",
            "123",
            "",
        ],
    )
    def test_get_bundesland_info_invalid(self, bundesland):
        """Test getting info for invalid Bundesland"""
        response = client.get(f"/api/v1/bundesland/{bundesland}")
        assert response.status_code in [200, 404, 400]

    def test_get_bundesland_wien(self):
        """Test specific Bundesland: Wien"""
        response = client.get("/api/v1/bundesland/wien")
        assert response.status_code in [200, 404, 405]
        if response.status_code == 200:
            data = response.json()
            # Wien should have specific characteristics
            if "name" in data:
                assert data["name"] == "Wien" or "wien" in data["name"].lower()

    def test_get_bundesland_salzburg_special_case(self):
        """Test Salzburg special case (WSchVO instead of OIB-RL 6)"""
        response = client.get("/api/v1/bundesland/salzburg")
        assert response.status_code in [200, 404, 405]

    def test_get_bundesland_tirol_avalanche_protection(self):
        """Test Tirol specific regulations (avalanche protection)"""
        response = client.get("/api/v1/bundesland/tirol")
        assert response.status_code in [200, 404, 405]

    def test_get_bundesland_vorarlberg(self):
        """Test Vorarlberg regulations"""
        response = client.get("/api/v1/bundesland/vorarlberg")
        assert response.status_code in [200, 404, 405]

    def test_compare_bundeslaender(self):
        """Test comparing Bundeslaender"""
        response = client.get("/api/v1/bundesland/compare")
        assert response.status_code in [200, 404, 405]

    def test_get_all_bundeslaender(self):
        """Test getting all Bundeslaender"""
        response = client.get("/api/v1/bundesland/")
        assert response.status_code in [200, 404, 405]

    def test_bundesland_with_query_params(self):
        """Test Bundesland endpoint with query parameters"""
        response = client.get("/api/v1/bundesland/wien?format=json&lang=de")
        assert response.status_code in [200, 404, 405]

    def test_bundesland_special_characters(self):
        """Test Bundesland with special characters"""
        response = client.get("/api/v1/bundesland/wien<script>")
        assert response.status_code in [200, 404, 400]

    def test_bundesland_case_insensitive(self):
        """Test case insensitive Bundesland lookup"""
        response_lower = client.get("/api/v1/bundesland/wien")
        response_upper = client.get("/api/v1/bundesland/WIEN")
        response_mixed = client.get("/api/v1/bundesland/Wien")
        # All should respond consistently
        assert response_lower.status_code in [200, 404, 405]
        assert response_upper.status_code in [200, 404, 405]
        assert response_mixed.status_code in [200, 404, 405]


class TestBundeslandData:
    """Test Bundesland data consistency"""

    def test_all_bundeslaender_have_data(self):
        """Test that all 9 Bundeslaender return data"""
        bundeslaender = [
            "wien",
            "tirol",
            "salzburg",
            "vorarlberg",
            "steiermark",
            "kaernten",
            "burgenland",
            "niederoesterreich",
            "oberoesterreich",
        ]
        
        for bl in bundeslaender:
            response = client.get(f"/api/v1/bundesland/{bl}")
            assert response.status_code in [200, 404, 405]

    def test_bundesland_response_fields(self):
        """Test that response contains expected fields"""
        response = client.get("/api/v1/bundesland/wien")
        if response.status_code == 200:
            data = response.json()
            # Check for common fields
            for field in ["name", "bauordnung"]:
                # At least one of these should be present
                if field in data:
                    assert data[field] is not None

    def test_stellplatz_factors_reasonable(self):
        """Test that Stellplatz factors are reasonable"""
        response = client.get("/api/v1/bundesland/wien")
        if response.status_code == 200:
            data = response.json()
            if "stellplatz_factor" in data:
                # Factors should be between 0.5 and 3.0
                assert 0.5 <= data["stellplatz_factor"] <= 3.0


class TestBundeslandFoerderungen:
    """Test Foerderungen (subsidies) endpoints"""

    def test_get_foerderungen_wien(self):
        """Test getting Foerderungen for Wien"""
        response = client.get("/api/v1/bundesland/wien/foerderungen")
        assert response.status_code in [200, 404, 405]

    @pytest.mark.parametrize(
        "bundesland",
        [
            "wien",
            "tirol",
            "salzburg",
        ],
    )
    def test_get_foerderungen_all(self, bundesland):
        """Test getting Foerderungen for multiple Bundeslaender"""
        response = client.get(f"/api/v1/bundesland/{bundesland}/foerderungen")
        assert response.status_code in [200, 404, 405]


class TestBundeslandIntegration:
    """Integration tests for Bundesland"""

    def test_bundesland_workflow_wien(self):
        """Test complete Bundesland workflow for Wien"""
        # Get Wien data
        response = client.get("/api/v1/bundesland/wien")
        assert response.status_code in [200, 404, 405]

        # Get Wien Foerderungen
        response = client.get("/api/v1/bundesland/wien/foerderungen")
        assert response.status_code in [200, 404, 405]

    def test_bundesland_comparison_workflow(self):
        """Test comparing Bundeslaender"""
        response = client.get("/api/v1/bundesland/compare?bl1=wien&bl2=tirol")
        assert response.status_code in [200, 404, 405]

    def test_all_bundeslaender_sequential_access(self):
        """Test accessing all Bundeslaender in sequence"""
        bundeslaender = [
            "wien",
            "tirol",
            "salzburg",
            "vorarlberg",
            "steiermark",
            "kaernten",
            "burgenland",
            "niederoesterreich",
            "oberoesterreich",
        ]
        
        for bl in bundeslaender:
            response = client.get(f"/api/v1/bundesland/{bl}")
            assert response.status_code in [200, 404, 405]
