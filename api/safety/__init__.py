"""
ORION Safety Module
Adapted from GENESIS DUAL-SYSTEM V3.0.1

Provides safety-critical functionality for ORION Architekt-AT:
- Cryptographic audit trails
- Compliance chain verification
- Deterministic validation
- TRL-based assessment

Version: 1.0.0
License: Apache 2.0
"""

from api.safety.audit_trail import (
    AuditEntry,
    AuditTrail,
    create_bim_trail,
    create_calculation_trail,
    create_compliance_trail,
)

__all__ = [
    "AuditEntry",
    "AuditTrail",
    "create_compliance_trail",
    "create_calculation_trail",
    "create_bim_trail",
]

__version__ = "1.0.0"
