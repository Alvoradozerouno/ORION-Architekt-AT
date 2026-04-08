"""
Epistemology Module for THE ARCHITEKT
Knowledge Classification and Verification System

Standards Compliance:
- EU AI Act Article 12 (Transparency)
- ISO 26262 ASIL-D (Safety-critical systems)
- ÖNORM requirements for verifiable calculations
"""

from .state_taxonomy import EpistemicState, KnowledgeType, VerificationLevel

__all__ = ["EpistemicState", "KnowledgeType", "VerificationLevel"]
