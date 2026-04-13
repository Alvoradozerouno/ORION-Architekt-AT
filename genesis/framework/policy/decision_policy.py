"""
Decision Policy Engine for THE ARCHITEKT
Enforces "when decisions must NOT be made" principle

Based on GENESIS × EIRA V4.2 Policy Module
Adapted for ISO 26262 ASIL-D compliance and Austrian building regulations

Use Cases:
- Prevent deterministic agents from making decisions with UNKNOWN data
- Enforce fallback to human review when epistemic conditions fail
- Ensure compliance with ZiviltechnikerG (Austrian Civil Engineer Law)
- Implement ISO 26262 safety constraints

Standards:
- ISO 26262 ASIL-D (Fallback mechanisms for safety-critical systems)
- EU AI Act Article 12 (Automated decision documentation)
- Austrian ZiviltechnikerG (Human signature required for legal documents)
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timezone

from ..epistemology.state_taxonomy import EpistemicState, KnowledgeType


class DecisionMode(Enum):
    """Decision modes with different safety levels"""

    DETERMINISTIC = "deterministic"      # Eurocode calculations - requires VERIFIED inputs
    PROBABILISTIC = "probabilistic"      # Monte Carlo - allows ESTIMATED inputs
    FALLBACK = "fallback"                # Human review required
    PROHIBITED = "prohibited"            # Decision cannot be made under any circumstances

    def __str__(self):
        return self.value


class PolicyViolationError(Exception):
    """Raised when a decision violates policy constraints"""
    pass


@dataclass
class PolicyRule:
    """
    Represents a policy constraint on decision-making

    Attributes:
        name: Rule identifier
        condition: What triggers this rule
        action: What to do when triggered (ALLOW, FALLBACK, PROHIBIT)
        reason: Human-readable explanation
    """
    name: str
    condition: str
    action: str  # "ALLOW", "FALLBACK", "PROHIBIT"
    reason: str


class DecisionPolicyEngine:
    """
    Enforces decision policy constraints for THE ARCHITEKT

    Key Principle: "System enforces when decisions must NOT be made"

    Policy Rules:
    1. DETERMINISTIC mode requires ALL inputs to be VERIFIED
    2. PROBABILISTIC mode allows ESTIMATED but requires confidence > threshold
    3. ANY UNKNOWN input triggers FALLBACK (human review)
    4. Legal documents require human signature (ZiviltechnikerG)
    """

    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize policy engine

        Args:
            confidence_threshold: Minimum confidence for ESTIMATED inputs in probabilistic mode
        """
        self.confidence_threshold = confidence_threshold
        self.policy_log: List[Dict[str, Any]] = []

        # Define policy rules
        self.rules = [
            PolicyRule(
                name="DETERMINISTIC_VERIFIED_ONLY",
                condition="Decision mode is DETERMINISTIC",
                action="PROHIBIT if any input is not VERIFIED",
                reason="ISO 26262 ASIL-D: Deterministic calculations require verified inputs",
            ),
            PolicyRule(
                name="UNKNOWN_TRIGGERS_FALLBACK",
                condition="Any input has knowledge_type = UNKNOWN",
                action="FALLBACK to human review",
                reason="Insufficient data for automated decision",
            ),
            PolicyRule(
                name="LOW_CONFIDENCE_FALLBACK",
                condition=f"ESTIMATED input has confidence < {confidence_threshold}",
                action="FALLBACK to human review",
                reason=f"Confidence below threshold ({confidence_threshold})",
            ),
            PolicyRule(
                name="LEGAL_DOCUMENT_SIGNATURE",
                condition="Output is legal document (Statik-Papier, Gutachten)",
                action="FALLBACK - requires Zivilingenieur signature",
                reason="Austrian ZiviltechnikerG requires human professional signature",
            ),
        ]

    def check_decision_allowed(
        self,
        decision_mode: DecisionMode,
        inputs: Dict[str, EpistemicState],
        decision_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Check if a decision is allowed under current policy

        Args:
            decision_mode: DETERMINISTIC, PROBABILISTIC, or FALLBACK
            inputs: Dictionary of epistemic states for all decision inputs
            decision_type: Type of decision (e.g., "Tragwerksbemessung", "Kostenplanung")
            metadata: Additional context

        Returns:
            Dict with:
                - allowed: bool (can decision proceed?)
                - mode: str (final decision mode, may be changed to FALLBACK)
                - violations: list of policy violations
                - reason: explanation

        Raises:
            PolicyViolationError: If decision is prohibited
        """
        violations = []
        final_mode = decision_mode
        metadata = metadata or {}

        # Rule 1: Check for UNKNOWN inputs (always triggers fallback)
        unknown_inputs = [k for k, v in inputs.items() if v.is_unknown()]
        if unknown_inputs:
            violations.append({
                "rule": "UNKNOWN_TRIGGERS_FALLBACK",
                "inputs": unknown_inputs,
                "reason": "Insufficient data for automated decision",
            })
            final_mode = DecisionMode.FALLBACK

        # Rule 2: DETERMINISTIC mode requires ALL VERIFIED inputs
        if decision_mode == DecisionMode.DETERMINISTIC:
            non_verified = [k for k, v in inputs.items() if not v.is_verified()]
            if non_verified:
                violations.append({
                    "rule": "DETERMINISTIC_VERIFIED_ONLY",
                    "inputs": non_verified,
                    "reason": "Deterministic mode requires all inputs to be VERIFIED",
                })
                # This is a hard violation - cannot proceed
                raise PolicyViolationError(
                    f"DETERMINISTIC decision '{decision_type}' cannot proceed with non-verified inputs: {non_verified}"
                )

        # Rule 3: PROBABILISTIC mode - check confidence threshold
        if decision_mode == DecisionMode.PROBABILISTIC:
            low_confidence = [
                k for k, v in inputs.items()
                if v.is_estimated() and v.confidence < self.confidence_threshold
            ]
            if low_confidence:
                violations.append({
                    "rule": "LOW_CONFIDENCE_FALLBACK",
                    "inputs": low_confidence,
                    "reason": f"Confidence below threshold ({self.confidence_threshold})",
                })
                final_mode = DecisionMode.FALLBACK

        # Rule 4: Legal documents require human signature
        legal_document_types = ["Statik-Papier", "Gutachten", "Bauantrag", "Compliance-Papier"]
        if decision_type in legal_document_types:
            violations.append({
                "rule": "LEGAL_DOCUMENT_SIGNATURE",
                "reason": "Austrian ZiviltechnikerG requires human professional signature",
            })
            final_mode = DecisionMode.FALLBACK

        # Log decision
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "decision_type": decision_type,
            "requested_mode": decision_mode.value,
            "final_mode": final_mode.value,
            "violations": violations,
            "inputs": {k: v.to_dict() for k, v in inputs.items()},
            "metadata": metadata,
        }
        self.policy_log.append(log_entry)

        # Determine if allowed
        allowed = len(violations) == 0 or final_mode == DecisionMode.FALLBACK

        return {
            "allowed": allowed,
            "mode": final_mode.value,
            "violations": violations,
            "reason": self._format_reason(violations, final_mode),
            "log_entry": log_entry,
        }

    def _format_reason(self, violations: List[Dict], final_mode: DecisionMode) -> str:
        """Format human-readable reason for policy decision"""
        if not violations:
            return "All policy constraints satisfied"

        if final_mode == DecisionMode.FALLBACK:
            reasons = [v.get("reason", "Unknown") for v in violations]
            return f"FALLBACK required: {'; '.join(reasons)}"

        return "Policy violations detected"

    def require_verified_inputs(self, inputs: Dict[str, EpistemicState], decision_type: str):
        """
        Convenience method: Require all inputs to be VERIFIED

        Args:
            inputs: Dictionary of epistemic states
            decision_type: Type of decision

        Raises:
            PolicyViolationError: If any input is not VERIFIED
        """
        result = self.check_decision_allowed(
            decision_mode=DecisionMode.DETERMINISTIC,
            inputs=inputs,
            decision_type=decision_type,
        )

        if not result["allowed"]:
            raise PolicyViolationError(result["reason"])

    def get_fallback_recommendation(self, violations: List[Dict]) -> str:
        """
        Generate recommendation for human review

        Args:
            violations: List of policy violations

        Returns:
            Human-readable recommendation
        """
        if not violations:
            return "No fallback needed - all constraints satisfied"

        recommendations = []
        for v in violations:
            rule = v.get("rule", "UNKNOWN")
            if rule == "UNKNOWN_TRIGGERS_FALLBACK":
                inputs = v.get("inputs", [])
                recommendations.append(f"Obtain verified data for: {', '.join(inputs)}")
            elif rule == "LOW_CONFIDENCE_FALLBACK":
                inputs = v.get("inputs", [])
                recommendations.append(f"Increase confidence for: {', '.join(inputs)} (run more simulations)")
            elif rule == "LEGAL_DOCUMENT_SIGNATURE":
                recommendations.append("Forward to Zivilingenieur for signature")

        return "FALLBACK REQUIRED:\n- " + "\n- ".join(recommendations)

    def export_policy_log(self) -> List[Dict[str, Any]]:
        """Export complete policy decision log (for audit trail)"""
        return self.policy_log.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """Get policy engine statistics"""
        if not self.policy_log:
            return {
                "total_decisions": 0,
                "fallbacks": 0,
                "violations": 0,
            }

        total = len(self.policy_log)
        fallbacks = sum(1 for entry in self.policy_log if entry["final_mode"] == "fallback")
        violations = sum(len(entry["violations"]) for entry in self.policy_log)

        return {
            "total_decisions": total,
            "fallbacks": fallbacks,
            "fallback_rate": fallbacks / total * 100 if total > 0 else 0.0,
            "total_violations": violations,
            "avg_violations_per_decision": violations / total if total > 0 else 0.0,
        }


# =============================================================================
# CONVENIENCE FUNCTIONS FOR THE ARCHITEKT
# =============================================================================

def create_policy_engine(confidence_threshold: float = 0.5) -> DecisionPolicyEngine:
    """Create decision policy engine with default rules"""
    return DecisionPolicyEngine(confidence_threshold=confidence_threshold)
