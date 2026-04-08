"""
GENESIS × EIRA Framework Integration for THE ARCHITEKT
Epistemological Safety and Decision Policy Engine

Integrated: 2026-04-08
Based on: GENESIS DUAL-SYSTEM V4.2
License: Apache 2.0
"""

__version__ = "4.2.0"
__framework__ = "GENESIS × EIRA"

from .epistemology.state_taxonomy import (
    EpistemicState,
    KnowledgeType,
    VerificationLevel,
)
from .policy.decision_policy import (
    DecisionPolicyEngine,
    DecisionMode,
    PolicyViolationError,
)

__all__ = [
    "EpistemicState",
    "KnowledgeType",
    "VerificationLevel",
    "DecisionPolicyEngine",
    "DecisionMode",
    "PolicyViolationError",
]
