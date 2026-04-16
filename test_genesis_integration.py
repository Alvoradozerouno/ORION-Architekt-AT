#!/usr/bin/env python3
"""
Integration Tests for GENESIS × EIRA Framework in THE ARCHITEKT

Tests epistemic safety and decision policy engine integration.

Run: pytest test_genesis_integration.py -v
"""

import pytest

from genesis.framework.epistemology import (
    EpistemicState,
    KnowledgeType,
    VerificationLevel,
    create_estimated_state,
    create_unknown_state,
    create_verified_state,
)
from genesis.framework.policy import (
    DecisionMode,
    DecisionPolicyEngine,
    PolicyViolationError,
)
from orion_multi_agent_system import ORIONMultiAgentSystem, TheArchitektAgent


class TestEpistemicStates:
    """Test epistemic state creation and validation"""

    def test_create_verified_state_from_eurocode(self):
        """Test creating VERIFIED state from Eurocode calculation"""
        state = EpistemicState.from_eurocode_calculation(
            value={"uwert": 0.16, "status": "OK"},
            norm="EN 1992-1-1",
            metadata={"calculation_method": "deterministic"},
        )

        assert state.knowledge_type == KnowledgeType.VERIFIED
        assert state.verification_level == VerificationLevel.NORMATIVE
        assert state.confidence == 1.0
        assert state.is_verified()
        assert not state.is_estimated()
        assert not state.is_unknown()
        assert not state.requires_fallback()

    def test_create_estimated_state_from_monte_carlo(self):
        """Test creating ESTIMATED state from Monte Carlo simulation"""
        state = EpistemicState.from_monte_carlo(
            value={"kosten": 250000, "p90": 280000},
            confidence=0.85,
            n_simulations=10000,
            metadata={"method": "monte_carlo"},
        )

        assert state.knowledge_type == KnowledgeType.ESTIMATED
        assert state.verification_level == VerificationLevel.SIMULATED
        assert state.confidence == 0.85
        assert not state.is_verified()
        assert state.is_estimated()
        assert not state.is_unknown()
        assert not state.requires_fallback()  # confidence >= 0.5

    def test_create_unknown_state(self):
        """Test creating UNKNOWN state (triggers fallback)"""
        state = EpistemicState.from_unknown(reason="Missing material data")

        assert state.knowledge_type == KnowledgeType.UNKNOWN
        assert state.verification_level == VerificationLevel.UNAVAILABLE
        assert state.confidence == 0.0
        assert not state.is_verified()
        assert not state.is_estimated()
        assert state.is_unknown()
        assert state.requires_fallback()  # Always true for UNKNOWN

    def test_low_confidence_requires_fallback(self):
        """Test that low confidence ESTIMATED states require fallback"""
        state = EpistemicState.from_monte_carlo(
            value={"estimate": 100},
            confidence=0.3,  # Low confidence
            n_simulations=100,
        )

        assert state.is_estimated()
        assert state.requires_fallback()  # confidence < 0.5

    def test_verified_state_validation(self):
        """Test validation rules for VERIFIED states"""
        # Should raise if confidence != 1.0 for VERIFIED
        with pytest.raises(ValueError, match="VERIFIED knowledge must have confidence = 1.0"):
            EpistemicState(
                value=42,
                knowledge_type=KnowledgeType.VERIFIED,
                verification_level=VerificationLevel.NORMATIVE,
                confidence=0.95,  # Invalid!
            )

    def test_estimated_state_validation(self):
        """Test validation rules for ESTIMATED states"""
        # Should raise if confidence not in (0, 1)
        with pytest.raises(ValueError, match="ESTIMATED knowledge must have"):
            EpistemicState(
                value=42,
                knowledge_type=KnowledgeType.ESTIMATED,
                verification_level=VerificationLevel.SIMULATED,
                confidence=1.0,  # Invalid!
            )


class TestDecisionPolicyEngine:
    """Test decision policy engine constraints"""

    def test_deterministic_mode_requires_verified_inputs(self):
        """Test that DETERMINISTIC mode requires all VERIFIED inputs"""
        policy = DecisionPolicyEngine(confidence_threshold=0.5)

        verified_state = create_verified_state(
            value={"statik": "OK"},
            source="EN 1992-1-1",
        )

        # Should allow with VERIFIED inputs
        result = policy.check_decision_allowed(
            decision_mode=DecisionMode.DETERMINISTIC,
            inputs={"statik": verified_state},
            decision_type="Tragwerksbemessung",
        )

        assert result["allowed"]
        assert result["mode"] == "deterministic"
        assert len(result["violations"]) == 0

    def test_deterministic_mode_rejects_estimated_inputs(self):
        """Test that DETERMINISTIC mode rejects ESTIMATED inputs"""
        policy = DecisionPolicyEngine(confidence_threshold=0.5)

        estimated_state = create_estimated_state(
            value={"kosten": 250000},
            confidence=0.85,
            source="Monte Carlo",
        )

        # Should raise PolicyViolationError
        with pytest.raises(PolicyViolationError, match="cannot proceed with non-verified inputs"):
            policy.check_decision_allowed(
                decision_mode=DecisionMode.DETERMINISTIC,
                inputs={"kosten": estimated_state},
                decision_type="Tragwerksbemessung",
            )

    def test_unknown_inputs_trigger_fallback(self):
        """Test that UNKNOWN inputs always trigger fallback"""
        policy = DecisionPolicyEngine(confidence_threshold=0.5)

        unknown_state = create_unknown_state(reason="Missing data")

        result = policy.check_decision_allowed(
            decision_mode=DecisionMode.PROBABILISTIC,
            inputs={"material": unknown_state},
            decision_type="Kostenplanung",
        )

        assert result["allowed"]  # Fallback is allowed
        assert result["mode"] == "fallback"  # Mode changed to FALLBACK
        assert len(result["violations"]) > 0
        assert any("UNKNOWN" in v["rule"] for v in result["violations"])

    def test_legal_documents_require_fallback(self):
        """Test that legal documents always require fallback (human signature)"""
        policy = DecisionPolicyEngine(confidence_threshold=0.5)

        verified_state = create_verified_state(
            value={"statik": "OK"},
            source="EN 1992-1-1",
        )

        # Legal document types trigger fallback
        for doc_type in ["Statik-Papier", "Gutachten", "Bauantrag"]:
            result = policy.check_decision_allowed(
                decision_mode=DecisionMode.DETERMINISTIC,
                inputs={"statik": verified_state},
                decision_type=doc_type,
            )

            assert result["allowed"]
            assert result["mode"] == "fallback"  # Always fallback for legal docs
            assert any("LEGAL_DOCUMENT" in v["rule"] for v in result["violations"])

    def test_low_confidence_triggers_fallback(self):
        """Test that low confidence ESTIMATED inputs trigger fallback"""
        policy = DecisionPolicyEngine(confidence_threshold=0.5)

        low_confidence_state = create_estimated_state(
            value={"estimate": 100},
            confidence=0.3,  # Below threshold
            source="Few simulations",
        )

        result = policy.check_decision_allowed(
            decision_mode=DecisionMode.PROBABILISTIC,
            inputs={"data": low_confidence_state},
            decision_type="Analysis",
        )

        assert result["allowed"]
        assert result["mode"] == "fallback"
        assert any("LOW_CONFIDENCE" in v["rule"] for v in result["violations"])

    def test_policy_engine_statistics(self):
        """Test policy engine statistics tracking"""
        policy = DecisionPolicyEngine(confidence_threshold=0.5)

        verified_state = create_verified_state(value=42, source="Test")
        unknown_state = create_unknown_state(reason="Test")

        # Make some decisions
        policy.check_decision_allowed(
            DecisionMode.DETERMINISTIC,
            {"input": verified_state},
            "Test1",
        )

        policy.check_decision_allowed(
            DecisionMode.PROBABILISTIC,
            {"input": unknown_state},
            "Test2",
        )

        stats = policy.get_statistics()
        assert stats["total_decisions"] == 2
        assert stats["fallbacks"] >= 1  # Unknown triggered fallback
        assert stats["total_violations"] >= 1


class TestTheArchitektIntegration:
    """Test GENESIS framework integration with TheArchitektAgent"""

    def test_architekt_has_policy_engine(self):
        """Test that TheArchitektAgent has policy engine"""
        architekt = TheArchitektAgent()
        assert architekt.policy_engine is not None
        assert isinstance(architekt.policy_engine, DecisionPolicyEngine)

    def test_create_epistemic_state_from_deterministic_result(self):
        """Test epistemic state creation from deterministic agent result"""
        architekt = TheArchitektAgent()

        deterministic_result = {
            "eurocode": "EN 1992-1-1",
            "status": "GENEHMIGUNGSFÄHIG",
            "ausnutzung": 0.85,
        }

        state = architekt.create_epistemic_state_from_agent_result(
            agent_name="Zivilingenieur",
            result=deterministic_result,
            is_deterministic=True,
        )

        assert state.is_verified()
        assert state.verification_level == VerificationLevel.NORMATIVE
        assert state.confidence == 1.0

    def test_create_epistemic_state_from_probabilistic_result(self):
        """Test epistemic state creation from probabilistic agent result"""
        architekt = TheArchitektAgent()

        probabilistic_result = {
            "anzahl_simulationen": 10000,
            "statistik": {"mittelwert_eur": 250000},
        }

        state = architekt.create_epistemic_state_from_agent_result(
            agent_name="Kostenplaner",
            result=probabilistic_result,
            is_deterministic=False,
        )

        assert state.is_estimated()
        assert state.verification_level == VerificationLevel.SIMULATED
        assert 0.0 < state.confidence < 1.0

    def test_check_decision_policy(self):
        """Test decision policy checking through TheArchitektAgent"""
        architekt = TheArchitektAgent()

        verified_state = create_verified_state(
            value={"statik": "OK"},
            source="EN 1992-1-1",
        )

        result = architekt.check_decision_policy(
            decision_type="Tragwerksbemessung",
            epistemic_states={"statik": verified_state},
            mode=DecisionMode.DETERMINISTIC,
        )

        assert result["allowed"]
        assert len(result["violations"]) == 0


class TestORIONMultiAgentSystem:
    """Test GENESIS integration with ORIONMultiAgentSystem"""

    def test_system_reports_genesis_framework(self):
        """Test that system reports GENESIS framework availability"""
        system = ORIONMultiAgentSystem()
        info = system.get_agent_info()

        assert "genesis_framework" in info
        assert info["genesis_framework"]["available"] is True
        assert info["genesis_framework"]["version"] == "4.2.0"
        assert len(info["genesis_framework"]["features"]) == 3

    def test_system_has_policy_statistics(self):
        """Test that system includes policy statistics"""
        system = ORIONMultiAgentSystem()
        info = system.get_agent_info()

        assert "policy_statistics" in info["genesis_framework"]
        stats = info["genesis_framework"]["policy_statistics"]
        assert "total_decisions" in stats
        assert "fallbacks" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
