"""
ORION Central Laws Registry System - Documentation & Guide

Central repository for all Austrian building laws, standards, and regulations.
Provides a single source of truth for compliance checks, transparency, and audit trails.
"""

# QUICK START
# ===========

# Get the registry singleton
from api.laws.registry import get_registry

registry = get_registry()

# ============================================================================
# A. QUERYING LAWS
# ============================================================================

# 1. Get all laws
all_laws = registry.list_all_laws()

# 2. Get OIB-RL standards (1-7)
oib_standards = registry.get_oib_richtlinien()

# 3. Get ÖNORM standards
oenorm_standards = registry.get_oenorm_standards()

# 4. Get specific law
oib_rl_6 = registry.get_law("OIB-RL-6-2023")
print(f"Law: {oib_rl_6.name}")
print(f"Ziviltechniker required: {oib_rl_6.ziviltechniker_required}")

# 5. Get laws for Bundesland (including regional variants)
wien_laws = registry.get_laws_for_bundesland("wien")
salzburg_laws = registry.get_laws_for_bundesland("salzburg")  # Includes SALZBURG-WSCHVO

# ============================================================================
# B. VERSIONING & HISTORY
# ============================================================================

# 1. Get current (active) version of a law
current_version = registry.get_current_version("OIB-RL-6-2023")
print(f"Current version: {current_version.version}")
print(f"Valid from: {current_version.valid_from}")

# 2. Get all versions of a law (complete history)
all_versions = registry.get_law_versions("OIB-RL-6-2023")
for version in all_versions:
    print(f"  {version.version_id}: {version.valid_from} - {version.valid_to}")

# 3. Get specific historical version
v1 = registry.get_law_version("OIB-RL-6-2023", "2023-v1")

# 4. Check if law was valid at specific timestamp
was_valid = registry.was_law_valid_at("OIB-RL-6-2023", "2023-06-01T00:00:00Z")

# 5. Get which version was applicable at specific time
applicable_version = registry.get_applicable_version_at("OIB-RL-6-2023", "2023-06-01T00:00:00Z")

# ============================================================================
# C. COMPLIANCE CHECKS & MAPPINGS
# ============================================================================

# 1. Get all compliance checks for a law
checks = registry.get_compliance_checks_for_law("OIB-RL-1-2023")
for check in checks:
    print(f"  {check.check_id}: {check.name} (type: {check.type})")

# 2. Get only mandatory compliance checks
mandatory_checks = registry.get_mandatory_checks_for_law("OIB-RL-6-2023")

# 3. Find specific check by ID
check = registry.get_check_by_id("check_oib_rl_1_structural")
print(f"Check function: {check.validation_function}")
print(f"Audit event: {check.audit_trail_event}")

# ============================================================================
# D. REGIONAL VARIANTS & SPECIAL CASES
# ============================================================================

# 1. Check if Salzburg special case (different energy rules)
is_salzburg_special = registry.is_salzburg_special_case("salzburg")

# 2. Get regional variant notes
salzburg_note = registry.get_regional_variant_note("OIB-RL-6-2023", "salzburg")
# Returns: "ACHTUNG: Salzburg wendet OIB-RL 6 NICHT an! Eigene Salzburger Wärmeschutzverordnung..."

# 3. Get Ziviltechniker requirements for specific project
ziviltechniker_required_laws = registry.get_ziviltechniker_required_for_project("wien", "buildings")

# ============================================================================
# E. AUDIT TRAIL INTEGRATION
# ============================================================================

# Export law information suitable for audit trails
from api.safety.audit_trail import create_compliance_trail

audit_trail = create_compliance_trail("PROJECT_2026_001")

# When performing compliance check:
law_audit_info = registry.export_law_as_audit_info(
    law_id="OIB-RL-6-2023",
    checks_performed=["check_fgee_calculation", "check_hwb_calculation"]
)

# Add audit entry with law version information
audit_trail.add_entry(
    event_type="compliance_check",
    actor="user_arch_001",
    action="oib_rl_6_check",
    resource="building_project_123",
    result="success",
    details={
        **law_audit_info,  # Includes law_id, law_version, version_id, etc.
        "fgee_value": 0.72,
        "hwb_value": 45,
        "calculation_result": {"status": "pass"}
    }
)

# ============================================================================
# F. TRANSPARENCY FOR ZIVILTECHNIKER
# ============================================================================

# When calculating building compliance:
from api.laws.registry import get_registry

registry = get_registry()
bundesland = "wien"
building_type = "buildings"

applicable_laws = registry.get_laws_for_bundesland(bundesland)
compliance_checks = []

for law in applicable_laws:
    if building_type in law.mandatory_for:
        checks = registry.get_mandatory_checks_for_law(law.law_id)
        compliance_checks.extend(checks)
        
        # Ziviltechniker can see which laws are being checked:
        print(f"Checking {law.name} ({law.law_id}/{law.versions[0].version_id})")
        for check in checks:
            print(f"  - {check.name}")

# ============================================================================
# G. STATISTICS
# ============================================================================

stats = registry.get_statistics()
print(f"Total laws in registry: {stats['total_laws']}")
print(f"OIB-RL standards: {stats['oib_richtlinien']}")
print(f"ÖNORM standards: {stats['oenorm_standards']}")
print(f"Laws by type: {stats['laws_by_type']}")

# ============================================================================
# H. API ENDPOINTS
# ============================================================================

"""
GET  /api/v1/laws/
  List all laws, optionally filtered by type or Bundesland

GET  /api/v1/laws/{law_id}
  Get detailed information about specific law

GET  /api/v1/laws/{law_id}/versions
  Get complete version history of law

GET  /api/v1/laws/{law_id}/versions/{version_id}
  Get specific version of law

GET  /api/v1/laws/bundesland/{bundesland}
  Get all laws applicable to Bundesland (including regional variants)

GET  /api/v1/laws/{law_id}/compliance-mapping
  Get all compliance checks for law

POST /api/v1/laws/validate-current
  Check if all laws are current against external sources (RIS, OIB, ÖNORM)

GET  /api/v1/transparency/calculations/{calc_id}
  Which laws were checked for calculation (Ziviltechniker view)

GET  /api/v1/audit/compliance-trail/{project_id}
  Complete audit trail with law versions for project

GET  /api/v1/laws/stats
  Registry statistics
"""

# ============================================================================
# I. INTEGRATION WITH COMPLIANCE CHECKS
# ============================================================================

# In compliance.py, when checking OIB-RL 6:

def check_oib_rl_6_compliance(bundesland: str, bgf_m2: float) -> dict:
    """Check OIB-RL 6 compliance"""
    registry = get_registry()
    
    # Get applicable law version for this Bundesland
    laws = registry.get_laws_for_bundesland(bundesland)
    rl_6_law = next((l for l in laws if l.law_id == "OIB-RL-6-2023"), None)
    
    if not rl_6_law:
        # Use national standard
        current_version = registry.get_current_version("OIB-RL-6-2023")
    else:
        current_version = registry.get_current_version(rl_6_law.law_id)
    
    # Check for regional variant
    regional_note = registry.get_regional_variant_note("OIB-RL-6-2023", bundesland)
    if regional_note and "WSchVO" in regional_note:
        # Use Salzburg rules instead
        return check_salzburg_wschvo(bgf_m2)
    
    # Perform compliance check
    fgee_limit = 0.75  # OIB-RL 6 requirement
    hwb_limit = 10 + 30 * (150 / 900)  # Example A/V = 150/900
    
    # Return with law version for audit trail
    return {
        "law_id": rl_6_law.law_id,
        "law_version": f"{rl_6_law.law_id}/{current_version.version_id}",
        "version_valid_from": current_version.valid_from,
        "fgee_limit": fgee_limit,
        "hwb_limit": hwb_limit,
        "compliant": True
    }

# ============================================================================
# J. EXTENDING THE REGISTRY
# ============================================================================

"""
To add new laws or standards:

1. Edit api/laws/data/austrian_laws.json
   Add new law entry with all versions and metadata

2. Edit api/laws/data/compliance_mapping.json
   Add mappings for this law's compliance checks

3. The registry will automatically load on next startup
   No code changes needed in registry.py

4. Tests will validate automatically
   Run: pytest tests/test_laws_registry.py

Example new law:
{
  "law_id": "EN-1991-1-1-2002",
  "name": "Eurocode 1: Actions on structures",
  "type": "EN",
  "number": null,
  "versions": [{
    "version_id": "2002-v1",
    "version": "2002",
    "valid_from": "2002-01-01",
    ...
  }],
  ...
}
"""

# ============================================================================
# K. DATA FLOW FOR COMPLIANCE CHECK WITH LAW VERSIONING
# ============================================================================

"""
1. User submits calculation for building in Wien

2. API calls compliance check:
   - Looks up applicable laws via registry.get_laws_for_bundesland("wien")
   - Gets current versions for each law
   - Gets compliance checks for each law

3. Compliance checks executed with law versions:
   - Each check records which law version it used
   - Results include law_id, law_version in details

4. Audit trail records complete picture:
   - Timestamp of calculation
   - Which laws were checked
   - Which versions were active at that time
   - Immutable SHA-256 hash chain

5. Ziviltechniker can verify:
   - GET /api/v1/transparency/calculations/{calc_id}
   - See exactly which laws were checked
   - See which versions applied
   - Verify compliance basis

6. Auditor can review later:
   - GET /api/v1/audit/compliance-trail/{project_id}
   - Proof that calculation used correct law versions
   - Historical record if laws changed later
"""
