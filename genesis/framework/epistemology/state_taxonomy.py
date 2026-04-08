"""
Epistemic State Taxonomy for THE ARCHITEKT
Classifies knowledge by verification level and confidence

Based on GENESIS × EIRA V4.2 Epistemology Module
Adapted for Austrian building design compliance

Use Cases:
- VERIFIED: Eurocode calculations, material properties from standards
- ESTIMATED: Cost predictions, Monte Carlo simulations
- UNKNOWN: Missing data, triggers human review

Standards:
- ISO 26262 ASIL-D (Safety-critical knowledge classification)
- EU AI Act Article 12 (Transparency in AI decision-making)
- ÖNORM requirements (Verifiable engineering calculations)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, Dict
from datetime import datetime, timezone


class KnowledgeType(Enum):
    """Classification of knowledge by verification level"""

    VERIFIED = "verified"          # Direct measurement, normative calculation, certified data
    ESTIMATED = "estimated"        # Probabilistic analysis, Monte Carlo, prediction
    UNKNOWN = "unknown"            # Missing data, insufficient information

    def __str__(self):
        return self.value


class VerificationLevel(Enum):
    """Level of verification for knowledge claims"""

    NORMATIVE = "normative"        # Eurocode, ÖNORM standards (highest confidence)
    CERTIFIED = "certified"        # Certified material properties, manufacturer data
    MEASURED = "measured"          # Direct physical measurement
    CALCULATED = "calculated"      # Engineering calculation with verified inputs
    SIMULATED = "simulated"        # Monte Carlo, FEM analysis with confidence interval
    PREDICTED = "predicted"        # AI/ML prediction, cost estimation
    ASSUMED = "assumed"            # Engineering assumption, requires documentation
    UNAVAILABLE = "unavailable"    # Data not available, triggers fallback

    def __str__(self):
        return self.value


@dataclass
class EpistemicState:
    """
    Represents the epistemic state of a piece of knowledge

    Attributes:
        value: The actual knowledge value (number, string, dict, etc.)
        knowledge_type: VERIFIED, ESTIMATED, or UNKNOWN
        verification_level: How the knowledge was obtained
        confidence: Confidence level (0.0 to 1.0) for ESTIMATED types
        source: Where the knowledge came from (e.g., "EN 1992-1-1", "Monte Carlo 10k runs")
        timestamp: When the knowledge was created
        metadata: Additional context (units, assumptions, etc.)
    """

    value: Any
    knowledge_type: KnowledgeType
    verification_level: VerificationLevel
    confidence: float = 1.0  # 1.0 for VERIFIED, <1.0 for ESTIMATED, 0.0 for UNKNOWN
    source: str = ""
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate epistemic state after initialization"""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        # Validation rules
        if self.knowledge_type == KnowledgeType.VERIFIED:
            if self.confidence < 1.0:
                raise ValueError("VERIFIED knowledge must have confidence = 1.0")
            if self.verification_level == VerificationLevel.UNAVAILABLE:
                raise ValueError("VERIFIED knowledge cannot have UNAVAILABLE verification")

        elif self.knowledge_type == KnowledgeType.ESTIMATED:
            if self.confidence <= 0.0 or self.confidence >= 1.0:
                raise ValueError("ESTIMATED knowledge must have 0.0 < confidence < 1.0")
            if self.verification_level in [VerificationLevel.NORMATIVE, VerificationLevel.CERTIFIED]:
                raise ValueError("ESTIMATED knowledge cannot have NORMATIVE/CERTIFIED verification")

        elif self.knowledge_type == KnowledgeType.UNKNOWN:
            if self.confidence != 0.0:
                raise ValueError("UNKNOWN knowledge must have confidence = 0.0")
            if self.verification_level != VerificationLevel.UNAVAILABLE:
                raise ValueError("UNKNOWN knowledge must have UNAVAILABLE verification")

    def is_verified(self) -> bool:
        """Check if knowledge is verified (suitable for deterministic calculations)"""
        return self.knowledge_type == KnowledgeType.VERIFIED

    def is_estimated(self) -> bool:
        """Check if knowledge is estimated (requires probabilistic treatment)"""
        return self.knowledge_type == KnowledgeType.ESTIMATED

    def is_unknown(self) -> bool:
        """Check if knowledge is unknown (triggers fallback/human review)"""
        return self.knowledge_type == KnowledgeType.UNKNOWN

    def requires_fallback(self) -> bool:
        """Check if this epistemic state requires fallback mechanism"""
        return (
            self.knowledge_type == KnowledgeType.UNKNOWN or
            (self.knowledge_type == KnowledgeType.ESTIMATED and self.confidence < 0.5)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization"""
        return {
            "value": self.value,
            "knowledge_type": self.knowledge_type.value,
            "verification_level": self.verification_level.value,
            "confidence": self.confidence,
            "source": self.source,
            "timestamp": self.timestamp,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_eurocode_calculation(cls, value: Any, norm: str, metadata: Optional[Dict] = None) -> "EpistemicState":
        """Create verified epistemic state from Eurocode calculation"""
        return cls(
            value=value,
            knowledge_type=KnowledgeType.VERIFIED,
            verification_level=VerificationLevel.NORMATIVE,
            confidence=1.0,
            source=f"Eurocode {norm}",
            metadata=metadata or {},
        )

    @classmethod
    def from_monte_carlo(cls, value: Any, confidence: float, n_simulations: int, metadata: Optional[Dict] = None) -> "EpistemicState":
        """Create estimated epistemic state from Monte Carlo simulation"""
        if not (0.0 < confidence < 1.0):
            raise ValueError(f"Monte Carlo confidence must be 0.0 < c < 1.0, got {confidence}")

        return cls(
            value=value,
            knowledge_type=KnowledgeType.ESTIMATED,
            verification_level=VerificationLevel.SIMULATED,
            confidence=confidence,
            source=f"Monte Carlo ({n_simulations:,} simulations)",
            metadata=metadata or {},
        )

    @classmethod
    def from_unknown(cls, reason: str) -> "EpistemicState":
        """Create unknown epistemic state (triggers fallback)"""
        return cls(
            value=None,
            knowledge_type=KnowledgeType.UNKNOWN,
            verification_level=VerificationLevel.UNAVAILABLE,
            confidence=0.0,
            source=f"UNKNOWN: {reason}",
            metadata={"reason": reason},
        )

    def __str__(self) -> str:
        return f"EpistemicState({self.knowledge_type.value}, {self.verification_level.value}, confidence={self.confidence:.2f})"

    def __repr__(self) -> str:
        return f"EpistemicState(value={self.value}, type={self.knowledge_type}, verification={self.verification_level}, conf={self.confidence:.2f})"


# =============================================================================
# CONVENIENCE FUNCTIONS FOR THE ARCHITEKT
# =============================================================================

def create_verified_state(value: Any, source: str, metadata: Optional[Dict] = None) -> EpistemicState:
    """Create verified epistemic state (deterministic, normative)"""
    return EpistemicState(
        value=value,
        knowledge_type=KnowledgeType.VERIFIED,
        verification_level=VerificationLevel.NORMATIVE,
        confidence=1.0,
        source=source,
        metadata=metadata,
    )


def create_estimated_state(value: Any, confidence: float, source: str, metadata: Optional[Dict] = None) -> EpistemicState:
    """Create estimated epistemic state (probabilistic)"""
    return EpistemicState(
        value=value,
        knowledge_type=KnowledgeType.ESTIMATED,
        verification_level=VerificationLevel.SIMULATED,
        confidence=confidence,
        source=source,
        metadata=metadata,
    )


def create_unknown_state(reason: str) -> EpistemicState:
    """Create unknown epistemic state (triggers fallback)"""
    return EpistemicState.from_unknown(reason)
