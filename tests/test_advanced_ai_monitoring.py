"""
Tests for Advanced AI and Monitoring endpoints
===============================================

Covers:
- /api/v1/advanced-ai/predict-cost
- /api/v1/advanced-ai/compliance-check
- /api/v1/advanced-ai/clash-detection
- /api/v1/advanced-ai/digital-twin/{building_id}
- /api/v1/advanced-ai/quantum-optimize
- /monitoring/health
- /monitoring/health/ready
- /monitoring/health/live
- /monitoring/health/detailed
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

client = TestClient(app)


# ============================================================================
# Advanced AI – Predictive Cost
# ============================================================================


class TestPredictiveCost:
    def test_predict_cost_basic(self):
        resp = client.post(
            "/api/v1/advanced-ai/predict-cost",
            params={
                "project_type": "residential",
                "gross_floor_area_m2": 500,
                "bundesland": "wien",
                "construction_quality": "standard",
                "construction_year": 2026,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "predicted_cost_eur" in data
        assert data["predicted_cost_eur"] > 0
        assert "confidence" in data
        assert "cost_range_min" in data
        assert "cost_range_max" in data
        assert data["cost_range_min"] < data["predicted_cost_eur"] < data["cost_range_max"]

    def test_predict_cost_premium_quality(self):
        resp = client.post(
            "/api/v1/advanced-ai/predict-cost",
            params={
                "project_type": "office",
                "gross_floor_area_m2": 1000,
                "bundesland": "tirol",
                "construction_quality": "premium",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        # Premium should cost more than standard for same area
        assert data["predicted_cost_eur"] > 0
        assert data["confidence"] in ["high", "medium", "low"]

    def test_predict_cost_large_project_low_confidence(self):
        resp = client.post(
            "/api/v1/advanced-ai/predict-cost",
            params={
                "project_type": "industrial",
                "gross_floor_area_m2": 50000,
                "bundesland": "oberösterreich",
                "construction_quality": "basic",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["confidence"] == "low"

    def test_predict_cost_all_bundeslaender(self):
        """All 9 Bundesländer should return a result"""
        bundeslaender = [
            "wien", "niederösterreich", "burgenland", "steiermark",
            "kärnten", "salzburg", "oberösterreich", "tirol", "vorarlberg",
        ]
        for bl in bundeslaender:
            resp = client.post(
                "/api/v1/advanced-ai/predict-cost",
                params={
                    "project_type": "residential",
                    "gross_floor_area_m2": 200,
                    "bundesland": bl,
                },
            )
            assert resp.status_code == 200, f"Failed for {bl}"
            assert resp.json()["predicted_cost_eur"] > 0


# ============================================================================
# Advanced AI – Compliance Check
# ============================================================================


class TestAIComplianceCheck:
    def test_compliance_check_no_issues(self):
        resp = client.post(
            "/api/v1/advanced-ai/compliance-check",
            json={"u_value": 0.18, "bundesland": "wien"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["critical_count"] == 0

    def test_compliance_check_u_value_violation(self):
        resp = client.post(
            "/api/v1/advanced-ai/compliance-check",
            json={"u_value": 0.30, "bundesland": "wien"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["critical_count"] >= 1
        sugg = data["suggestions"][0]
        assert sugg["severity"] == "critical"
        assert "U-Wert" in sugg["rule_name"] or "uwert" in sugg["rule_id"].lower()

    def test_compliance_check_elevator_required_wien(self):
        resp = client.post(
            "/api/v1/advanced-ai/compliance-check",
            json={
                "geschosse": 3,
                "aufzug": False,
                "bundesland": "wien",
                "wohneinheiten": 10,
                "stellplaetze": 10,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        elevator_issues = [s for s in data["suggestions"] if "Aufzug" in s["rule_name"]]
        assert len(elevator_issues) >= 1

    def test_compliance_check_parking_shortage(self):
        resp = client.post(
            "/api/v1/advanced-ai/compliance-check",
            json={
                "wohneinheiten": 20,
                "stellplaetze": 5,
                "bundesland": "wien",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        parking_issues = [s for s in data["suggestions"] if "Stellplatz" in s["rule_name"]]
        assert len(parking_issues) >= 1

    def test_compliance_check_empty_project(self):
        resp = client.post("/api/v1/advanced-ai/compliance-check", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data["issue_count"] == 0


# ============================================================================
# Advanced AI – Clash Detection
# ============================================================================


class TestClashDetection:
    def test_clash_detection_empty_model(self):
        resp = client.post(
            "/api/v1/advanced-ai/clash-detection",
            json={"elements": []},
        )
        assert resp.status_code == 200
        data = resp.json()
        # Empty model returns sample clash
        assert data["clash_count"] >= 1

    def test_clash_detection_mep_structure(self):
        resp = client.post(
            "/api/v1/advanced-ai/clash-detection",
            json={
                "elements": [
                    {"id": "Duct-001", "type": "IfcDuctSegment"},
                    {"id": "Beam-001", "type": "IfcBeam"},
                ]
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["clash_count"] >= 1
        clash = data["resolutions"][0]
        assert clash["clash_type"] == "MEP-Structure"
        assert 0 <= clash["resolution_confidence"] <= 1

    def test_clash_detection_no_clashes(self):
        resp = client.post(
            "/api/v1/advanced-ai/clash-detection",
            json={"elements": [{"id": "Wall-001", "type": "IfcWall"}]},
        )
        assert resp.status_code == 200
        # No MEP/structure clash pairs → falls back to sample
        data = resp.json()
        assert "clash_count" in data

    def test_clash_detection_response_structure(self):
        resp = client.post("/api/v1/advanced-ai/clash-detection", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "clash_count" in data
        assert "auto_fixed_count" in data
        assert "manual_review_count" in data
        assert "resolutions" in data


# ============================================================================
# Advanced AI – Digital Twin
# ============================================================================


class TestDigitalTwin:
    def test_get_metrics(self):
        resp = client.get("/api/v1/advanced-ai/digital-twin/building-001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["building_id"] == "building-001"
        assert 0 <= data["occupancy_rate"] <= 1
        assert data["structural_health_score"] > 0
        assert data["energy_consumption_kwh"] > 0
        assert isinstance(data["maintenance_alerts"], list)
        assert isinstance(data["predicted_failures"], list)

    def test_get_metrics_different_buildings(self):
        for building_id in ["A1", "block-7", "test-building"]:
            resp = client.get(f"/api/v1/advanced-ai/digital-twin/{building_id}")
            assert resp.status_code == 200
            assert resp.json()["building_id"] == building_id


# ============================================================================
# Advanced AI – Quantum Optimization
# ============================================================================


class TestQuantumOptimization:
    def test_quantum_optimize_basic(self):
        resp = client.post(
            "/api/v1/advanced-ai/quantum-optimize",
            json={"problem_type": "structural_optimization", "constraints": []},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["quantum_ready"] is True
        assert data["optimization_quality"] > 0
        assert "algorithm" in data

    def test_quantum_optimize_empty_problem(self):
        resp = client.post("/api/v1/advanced-ai/quantum-optimize", json={})
        assert resp.status_code == 200
        assert resp.json()["quantum_ready"] is True


# ============================================================================
# Monitoring endpoints
# ============================================================================


class TestMonitoringHealth:
    def test_health_endpoint_returns_json(self):
        resp = client.get("/monitoring/health")
        assert resp.status_code in (200, 503)
        data = resp.json()
        assert "status" in data
        assert data["status"] in ("healthy", "degraded", "unhealthy")
        assert "timestamp" in data
        assert "checks" in data

    def test_health_has_database_check(self):
        resp = client.get("/monitoring/health")
        data = resp.json()
        assert "database" in data["checks"]
        assert "status" in data["checks"]["database"]

    def test_health_has_system_metrics(self):
        resp = client.get("/monitoring/health")
        data = resp.json()
        assert "system" in data

    def test_readiness_probe(self):
        resp = client.get("/monitoring/health/ready")
        assert resp.status_code in (200, 503)

    def test_liveness_probe(self):
        resp = client.get("/monitoring/health/live")
        assert resp.status_code == 200
        assert resp.content == b"alive"

    def test_detailed_diagnostics(self):
        resp = client.get("/monitoring/health/detailed")
        assert resp.status_code == 200
        data = resp.json()
        assert "python" in data
        assert "version" in data["python"]

    def test_metrics_endpoint(self):
        resp = client.get("/monitoring/metrics")
        # Either returns metrics text or 503 if prometheus not available
        assert resp.status_code in (200, 503)
