"""
Epistemology Module for THE ARCHITEKT
Knowledge Classification and Verification System

Standards Compliance:
- EU AI Act Article 12 (Transparency)
- ISO 26262 ASIL-D (Safety-critical systems)
- ÖNORM requirements for verifiable calculations
"""

from .state_taxonomy import (
    EpistemicState,
    KnowledgeType,
    VerificationLevel,
    create_estimated_state,
    create_unknown_state,
    create_verified_state,
)

__all__ = [
    "EpistemicState",
    "KnowledgeType",
    "VerificationLevel",
    "create_verified_state",
    "create_estimated_state",
    "create_unknown_state",
]
