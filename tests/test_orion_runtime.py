"""
Tests for ORION Runtime Router
====================================

Purpose: Verify deterministic decision logic and state machine
- VERIFIED/ESTIMATED/UNKNOWN state transitions
- ISO 26262 ASIL-D fallback mechanisms
- SHA256 audit trail integrity
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestOrionComponentStatus:
    """Test ORION Runtime component status"""

    def test_component_status_green(self):
        """14th component should be GREEN"""
        response = client.get("/api/v1/orion-runtime/component-status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "GREEN"
        assert data["component_index"] == 14
        assert data["total_components"] == 14

    def test_health_check(self):
        """Health check should succeed"""
        response = client.get("/api/v1/orion-runtime/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["component"] == "ORION Runtime"


class TestDecisionEvaluation:
    """Test deterministic decision evaluation"""

    def test_deterministic_decision_with_verified_inputs(self):
        """VERIFIED inputs should allow deterministic decision"""
        request_data = {
            "decision_type": "structural_safety",
            "mode": "deterministic",
            "work_step": "calculate_beam_capacity",
            "inputs": {
                "material": {"value": "concrete", "knowledge_type": "verified"},
                "span_m": {"value": 8.0, "knowledge_type": "verified"},
                "load_kn_per_m": {"value": 20.0, "knowledge_type": "verified"},
            },
        }
        response = client.post("/api/v1/orion-runtime/evaluate-decision", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["decision_allowed"] is True
        assert data["work_step_state"]["state"] == "VERIFIED"
        assert data["work_step_state"]["knowledge_type"] == "verified"

    def test_deterministic_decision_with_unknown_input(self):
        """UNKNOWN input should trigger fallback"""
        request_data = {
            "decision_type": "structural_safety",
            "mode": "deterministic",
            "work_step": "calculate_beam_capacity",
            "inputs": {
                "material": {"value": "unknown", "knowledge_type": "unknown"},
                "span_m": {"value": 8.0, "knowledge_type": "verified"},
            },
        }
        response = client.post("/api/v1/orion-runtime/evaluate-decision", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["decision_allowed"] is False
        assert data["fallback_required"] is True
        assert data["work_step_state"]["state"] == "ABSTAIN"

    def test_probabilistic_decision_with_estimated_inputs(self):
        """ESTIMATED inputs should allow probabilistic decision"""
        request_data = {
            "decision_type": "cost_estimation",
            "mode": "probabilistic",
            "work_step": "estimate_construction_cost",
            "inputs": {
                "area_m2": {"value": 500.0, "knowledge_type": "verified"},
                "cost_per_m2": {"value": 1250.0, "confidence": 0.85, "knowledge_type": "estimated"},
            },
        }
        response = client.post("/api/v1/orion-runtime/evaluate-decision", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["work_step_state"]["state"] == "ESTIMATED"
        assert data["work_step_state"]["knowledge_type"] == "verified"  # Overall state can be verified

    def test_decision_response_includes_recommendations(self):
        """Fallback decisions should include recommendations"""
        request_data = {
            "decision_type": "structural_safety",
            "mode": "deterministic",
            "work_step": "calculate_foundation",
            "inputs": {"soil_type": {"value": "unknown", "knowledge_type": "unknown"}},
        }
        response = client.post("/api/v1/orion-runtime/evaluate-decision", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) > 0
        assert any("human" in rec.lower() for rec in data["recommendations"])


class TestWorkflowState:
    """Test workflow state management and audit trail"""

    def test_create_workflow(self):
        """Create new workflow with audit trail"""
        response = client.post("/api/v1/orion-runtime/workflow/create?workflow_id=wf_001")
        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == "wf_001"
        assert data["component_status"] == "GREEN"
        assert len(data["audit_hash"]) == 16  # SHA256 truncated

    def test_add_workflow_step_verified(self):
        """Add VERIFIED step to workflow"""
        # Create workflow
        wf_response = client.post("/api/v1/orion-runtime/workflow/create?workflow_id=wf_002")
        workflow_id = wf_response.json()["workflow_id"]

        # Add step
        step_response = client.post(
            f"/api/v1/orion-runtime/workflow/{workflow_id}/step",
            params={
                "step_id": "step_001",
                "step_name": "Structural Analysis",
                "state": "VERIFIED",
                "deterministic": True,
                "knowledge_type": "verified",
                "verification_level": "eurocode_en1992",
                "confidence": 1.0,
            },
            json={"bending_moment": 125.0, "shear_force": 85.0},
        )
        assert step_response.status_code == 200
        step_data = step_response.json()
        assert step_data["state"] == "VERIFIED"
        assert step_data["deterministic"] is True
        assert len(step_data["current_hash"]) == 16

    def test_workflow_steps_chain_hashes(self):
        """Each step should have SHA256 link to previous"""
        wf_response = client.post("/api/v1/orion-runtime/workflow/create?workflow_id=wf_003")
        workflow_id = wf_response.json()["workflow_id"]

        # Add first step
        step1 = client.post(
            f"/api/v1/orion-runtime/workflow/{workflow_id}/step",
            params={
                "step_id": "step_1",
                "step_name": "Step 1",
                "state": "VERIFIED",
                "deterministic": True,
                "knowledge_type": "verified",
                "verification_level": "calculated",
                "confidence": 1.0,
            },
            json={"result": 100},
        ).json()

        # Add second step
        step2 = client.post(
            f"/api/v1/orion-runtime/workflow/{workflow_id}/step",
            params={
                "step_id": "step_2",
                "step_name": "Step 2",
                "state": "VERIFIED",
                "deterministic": True,
                "knowledge_type": "verified",
                "verification_level": "calculated",
                "confidence": 1.0,
            },
            json={"result": 200},
        ).json()

        # Step 2 should link to Step 1
        assert step2["previous_hash"] == step1["current_hash"]
        assert step2["previous_hash"] is not None

    def test_get_workflow_with_steps(self):
        """Retrieve complete workflow with all steps"""
        wf_response = client.post("/api/v1/orion-runtime/workflow/create?workflow_id=wf_004")
        workflow_id = wf_response.json()["workflow_id"]

        # Add step
        client.post(
            f"/api/v1/orion-runtime/workflow/{workflow_id}/step",
            params={
                "step_id": "step_001",
                "step_name": "Analysis",
                "state": "VERIFIED",
                "deterministic": True,
                "knowledge_type": "verified",
                "verification_level": "measured",
                "confidence": 1.0,
            },
            json={"value": 42},
        )

        # Retrieve workflow
        get_response = client.get(f"/api/v1/orion-runtime/workflow/{workflow_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert len(data["steps"]) == 1
        assert data["steps"][0]["step_id"] == "step_001"

    def test_workflow_not_found(self):
        """Non-existent workflow should return 404"""
        response = client.get("/api/v1/orion-runtime/workflow/nonexistent_wf")
        assert response.status_code == 404


class TestFallbackMechanism:
    """Test ISO 26262 ASIL-D fallback mechanisms"""

    def test_register_fallback_case(self):
        """Register fallback case for human review"""
        response = client.post(
            "/api/v1/orion-runtime/fallback-case",
            params={
                "case_id": "fb_001",
                "reason": "Insufficient data for automated decision",
                "workflow_id": "wf_test",
                "step_id": "step_test",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["fallback_case"]["case_id"] == "fb_001"
        assert data["fallback_case"]["status"] == "open"
        assert data["fallback_case"]["assigned_to"] == "human_expert"


class TestStateTransitions:
    """Test valid state transitions"""

    def test_state_verified_to_verified(self):
        """VERIFIED → VERIFIED is valid"""
        request_data = {
            "decision_type": "structural_safety",
            "mode": "deterministic",
            "work_step": "step_001",
            "inputs": {
                "input1": {"value": 100, "knowledge_type": "verified"},
            },
        }
        response = client.post("/api/v1/orion-runtime/evaluate-decision", json=request_data)
        assert response.status_code == 200
        assert response.json()["work_step_state"]["state"] == "VERIFIED"

    def test_state_estimated_is_allowed_in_probabilistic(self):
        """ESTIMATED state should be generated for probabilistic decisions"""
        request_data = {
            "decision_type": "cost_estimation",
            "mode": "probabilistic",
            "work_step": "step_002",
            "inputs": {
                "cost": {"value": 1000, "confidence": 0.8, "knowledge_type": "estimated"},
            },
        }
        response = client.post("/api/v1/orion-runtime/evaluate-decision", json=request_data)
        assert response.status_code == 200
        state = response.json()["work_step_state"]["state"]
        assert state in ["VERIFIED", "ESTIMATED"]

    def test_state_unknown_triggers_abstain(self):
        """UNKNOWN knowledge should trigger ABSTAIN state"""
        request_data = {
            "decision_type": "structural_safety",
            "mode": "deterministic",
            "work_step": "step_003",
            "inputs": {
                "critical_data": {"value": None, "knowledge_type": "unknown"},
            },
        }
        response = client.post("/api/v1/orion-runtime/evaluate-decision", json=request_data)
        assert response.status_code == 200
        assert response.json()["work_step_state"]["state"] == "ABSTAIN"


class TestAuditTrail:
    """Test SHA256 audit trail integrity"""

    def test_hash_is_deterministic(self):
        """Same inputs should produce same hash"""
        wf_response = client.post("/api/v1/orion-runtime/workflow/create?workflow_id=wf_hash_001")
        workflow_id = wf_response.json()["workflow_id"]

        # Add two identical steps
        step1 = client.post(
            f"/api/v1/orion-runtime/workflow/{workflow_id}/step",
            params={
                "step_id": "hash_step_1",
                "step_name": "Test",
                "state": "VERIFIED",
                "deterministic": True,
                "knowledge_type": "verified",
                "verification_level": "normative",
                "confidence": 1.0,
            },
            json={"value": 123},
        ).json()

        # Create another workflow and add identical step
        wf_response2 = client.post("/api/v1/orion-runtime/workflow/create?workflow_id=wf_hash_002")
        workflow_id2 = wf_response2.json()["workflow_id"]

        step2 = client.post(
            f"/api/v1/orion-runtime/workflow/{workflow_id2}/step",
            params={
                "step_id": "hash_step_1",
                "step_name": "Test",
                "state": "VERIFIED",
                "deterministic": True,
                "knowledge_type": "verified",
                "verification_level": "normative",
                "confidence": 1.0,
            },
            json={"value": 123},
        ).json()

        # Hashes should be identical (deterministic)
        assert step1["current_hash"] == step2["current_hash"]

    def test_hash_changes_with_different_data(self):
        """Different inputs should produce different hashes"""
        wf_response = client.post("/api/v1/orion-runtime/workflow/create?workflow_id=wf_hash_003")
        workflow_id = wf_response.json()["workflow_id"]

        # Add first step with value 100
        step1 = client.post(
            f"/api/v1/orion-runtime/workflow/{workflow_id}/step",
            params={
                "step_id": "hash_step_1",
                "step_name": "Test",
                "state": "VERIFIED",
                "deterministic": True,
                "knowledge_type": "verified",
                "verification_level": "normative",
                "confidence": 1.0,
            },
            json={"value": 100},
        ).json()

        # Add second step with value 200
        step2 = client.post(
            f"/api/v1/orion-runtime/workflow/{workflow_id}/step",
            params={
                "step_id": "hash_step_2",
                "step_name": "Test",
                "state": "VERIFIED",
                "deterministic": True,
                "knowledge_type": "verified",
                "verification_level": "normative",
                "confidence": 1.0,
            },
            json={"value": 200},
        ).json()

        # Hashes should be different
        assert step1["current_hash"] != step2["current_hash"]
