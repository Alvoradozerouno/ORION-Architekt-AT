# ORION Central Laws Registry System

## Overview

The **Central Laws Registry** is a comprehensive, centralized repository of all Austrian building laws, standards, and regulations. It provides:

- **Single source of truth** for all laws and standards
- **Complete version history** tracking
- **Automatic compliance check mapping** 
- **Regional variant handling** (Bundesland-specific rules)
- **Immutable audit trails** with law version tracking
- **Transparency for Ziviltechniker** (architects & engineers)
- **Effortless maintainability** when laws change

## Architecture

### Directory Structure

```
api/laws/
├── __init__.py                 # Package initialization
├── models.py                   # Pydantic data models
├── registry.py                 # Central registry class (singleton)
├── data/
│   ├── austrian_laws.json      # Master law definitions (11 laws + 7 OIB-RL)
│   ├── compliance_mapping.json # Compliance check mappings
│   └── audit_links.json        # Links to audit trail (future)
└── validation/
    ├── __init__.py
    ├── ris_austria.py          # RIS Austria API integration
    ├── oib_validator.py        # OIB guidelines validator
    └── standards_validator.py  # ÖNORM standards validator

api/routers/
└── laws_registry.py            # FastAPI endpoints for laws

api/main.py                      # Updated to mount laws_registry router
```

## Data Structure

### Austrian Laws JSON (`austrian_laws.json`)

Each law entry contains:

```json
{
  "law_id": "OIB-RL-6-2023",
  "name": "OIB-Richtlinie 6: Energieeinsparung und Wärmeschutz",
  "type": "OIB-RL",
  "number": 6,
  "versions": [
    {
      "version_id": "2023-v1",
      "version": "2023",
      "valid_from": "2023-05-25",
      "valid_to": null,
      "source_url": "https://www.oib.or.at/",
      "pdf_hash": null,
      "published_at": "2023-05-25T00:00:00Z",
      "deprecated": false,
      "changes": ["fGEE ≤ 0.75 für Neubauten"]
    }
  ],
  "bundeslaender_abweichungen": {
    "salzburg": "ACHTUNG: Salzburg wendet OIB-RL 6 NICHT an!"
  },
  "related_standards": ["EN 1990", "EN 1991"],
  "compliance_checks": ["check_oib_rl_6"],
  "mandatory_for": ["buildings", "renovations"],
  "ziviltechniker_required": true
}
```

### Compliance Mapping JSON (`compliance_mapping.json`)

Maps laws to their compliance checks:

```json
{
  "mapping_id": "COMPL-OIB-RL-6-2023",
  "law_version": "OIB-RL-6-2023/2023-v1",
  "checks": [
    {
      "check_id": "check_fgee_calculation",
      "name": "fGEE Berechnung (≤ 0.75)",
      "type": "mandatory",
      "validation_function": "api.routers.compliance._check_fgee_value",
      "audit_trail_event": "compliance_check/fgee_calculation",
      "result_fields": ["fgee_result", "max_allowed", "pass_fail"]
    }
  ]
}
```

## Current Laws in Registry

### OIB-Richtlinien (1-7)
- **OIB-RL 1**: Mechanische Festigkeit und Standsicherheit
- **OIB-RL 2**: Brandschutz
- **OIB-RL 3**: Hygiene, Gesundheit und Umweltschutz
- **OIB-RL 4**: Nutzungssicherheit und Barrierefreiheit
- **OIB-RL 5**: Schallschutz
- **OIB-RL 6**: Energieeinsparung und Wärmeschutz (with Salzburg exception!)
- **OIB-RL 7**: Nachhaltige Nutzung der natürlichen Ressourcen

### ÖNORM Standards
- ÖNORM B 1800: Allgemeine Vorschriften
- ÖNORM B 1600: Barrierefreie Nutzung
- ÖNORM B 8110-1: Wärmeschutz Anforderungen
- ÖNORM S 5280: Radonschutz
- ÖNORM A 2063: Tendering (integrated in tendering router)

### Regional Variants
- **Salzburg WSchVO**: Salzburg uses its own energy rules instead of OIB-RL 6

## Core Features

### 1. Single Source of Truth

```python
from api.laws.registry import get_registry

registry = get_registry()

# Get any law
oib_rl_6 = registry.get_law("OIB-RL-6-2023")

# All other modules use same data
# No duplicates, no inconsistencies
```

### 2. Complete Version History

```python
# Get all versions of a law
versions = registry.get_law_versions("OIB-RL-6-2023")

# Find what was valid at specific date
version_2024 = registry.get_applicable_version_at(
    "OIB-RL-6-2023", 
    "2024-01-15T00:00:00Z"
)
```

### 3. Regional Variants

```python
# Get laws for specific Bundesland
salzburg_laws = registry.get_laws_for_bundesland("salzburg")
# Includes SALZBURG-WSCHVO instead of OIB-RL 6

# Get regional note
note = registry.get_regional_variant_note("OIB-RL-6-2023", "salzburg")
# "ACHTUNG: Salzburg wendet OIB-RL 6 NICHT an! Eigene WSchVO..."
```

### 4. Automatic Compliance Check Mapping

```python
# Get all compliance checks for law
checks = registry.get_compliance_checks_for_law("OIB-RL-6-2023")
# Returns: check_oib_rl_6, check_fgee_calculation, check_hwb_calculation

# Get only mandatory checks
mandatory = registry.get_mandatory_checks_for_law("OIB-RL-6-2023")
```

### 5. Audit Trail Integration

```python
from api.safety.audit_trail import create_compliance_trail

audit_trail = create_compliance_trail("PROJECT_001")

# Export law info for audit
law_info = registry.export_law_as_audit_info(
    "OIB-RL-6-2023",
    checks_performed=["check_fgee_calculation"]
)

# Add audit entry with law version
audit_trail.add_entry(
    event_type="compliance_check",
    actor="user_arch_001",
    action="oib_rl_6_check",
    resource="building_project_123",
    result="success",
    details={
        **law_info,  # law_id, law_version, version_id, valid_from, etc.
        "fgee_value": 0.72,
        "hwb_value": 45
    }
)
```

Now the audit trail contains:
- ✅ What law version was used
- ✅ When the law became valid
- ✅ Immutable SHA-256 hash chain
- ✅ Complete calculation context

### 6. Transparency for Ziviltechniker

```python
# After calculation completes, Ziviltechniker can call:
GET /api/v1/transparency/calculations/{calc_id}

# Returns:
{
  "calculation_id": "CALC_123",
  "project_id": "PROJ_456",
  "timestamp": "2026-04-15T10:30:00Z",
  "laws_referenced": [
    {
      "law_id": "OIB-RL-6-2023",
      "version": "2023-v1",
      "valid_from": "2023-05-25",
      "checks_performed": ["check_fgee_calculation"],
      "results": {"status": "pass", "fgee_value": 0.72}
    }
  ],
  "audit_trail_id": "AUDIT_789"
}
```

## API Endpoints

### Laws Discovery

```
GET /api/v1/laws/
  List all laws, filter by type or Bundesland

GET /api/v1/laws/{law_id}
  Get law details and current version

GET /api/v1/laws/{law_id}/versions
  Get version history

GET /api/v1/laws/{law_id}/versions/{version_id}
  Get specific version

GET /api/v1/laws/bundesland/{bundesland}
  Get laws for Bundesland with regional variants

GET /api/v1/laws/{law_id}/compliance-mapping
  Get compliance checks for law
```

### Compliance & Audit

```
POST /api/v1/laws/validate-current
  Check against RIS Austria, OIB, ÖNORM for updates

GET /api/v1/audit/compliance-trail/{project_id}
  Get audit trail with law versions

GET /api/v1/transparency/calculations/{calc_id}
  Ziviltechniker view: which laws were checked
```

### Statistics

```
GET /api/v1/laws/stats
  Registry statistics
```

## Benefits

| Feature | Benefit |
|---------|---------|
| **Central Source** | Single place to update all laws - no duplicates |
| **Version History** | Track changes over time, audit compliance at calculation date |
| **Regional Variants** | Salzburg WSchVO, local Ziviltechniker rules automatically applied |
| **Compliance Mapping** | Transparent which laws drive which checks |
| **Audit Trail** | Immutable proof of which laws were applied |
| **Ziviltechniker Transparency** | See exactly which laws were checked for their design |
| **Easy Maintenance** | Add new law? Just update JSON, no code changes |
| **Scalability** | Easily add more Bundesländer or international standards |

## Usage Examples

### Example 1: Checking OIB-RL 6 Compliance

```python
def check_oib_rl_6(bundesland: str, bgf_m2: float) -> dict:
    """Check OIB-RL 6 compliance with law version tracking"""
    registry = get_registry()
    
    # 1. Get applicable laws for this Bundesland
    laws = registry.get_laws_for_bundesland(bundesland)
    
    # 2. Find OIB-RL 6 (or Salzburg equivalent)
    rl_6 = next((l for l in laws if "OIB-RL-6" in l.law_id), None)
    salzburg_wschvo = next((l for l in laws if "SALZBURG-WSCHVO" in l.law_id), None)
    
    if salzburg_wschvo:
        # Salzburg: use WSchVO instead
        applicable_law = salzburg_wschvo
    else:
        applicable_law = rl_6
    
    # 3. Get current version
    current_version = registry.get_current_version(applicable_law.law_id)
    
    # 4. Perform check
    fgee_limit = 0.75  # OIB requirement
    fgee_actual = 0.72
    passed = fgee_actual <= fgee_limit
    
    # 5. Return with law version for audit trail
    return {
        "law_id": applicable_law.law_id,
        "law_version": f"{applicable_law.law_id}/{current_version.version_id}",
        "version_valid_from": current_version.valid_from,
        "fgee_limit": fgee_limit,
        "fgee_actual": fgee_actual,
        "passed": passed
    }
```

### Example 2: Auditor Verification

```python
# Auditor wants to check compliance from 6 months ago
from datetime import datetime, timedelta

calculation_date = "2025-11-15T10:30:00Z"

registry = get_registry()

# Get which law versions were active at that date
applicable_version = registry.get_applicable_version_at(
    "OIB-RL-6-2023",
    calculation_date
)

# Check if this version is still current
current_version = registry.get_current_version("OIB-RL-6-2023")

if applicable_version.version_id != current_version.version_id:
    print(f"⚠️  Law changed since calculation:")
    print(f"   Then: {applicable_version.version_id}")
    print(f"   Now: {current_version.version_id}")
    print(f"   Changes: {current_version.changes}")
else:
    print("✅ Same law version still in effect")
```

## Integration with Existing Code

The laws registry integrates seamlessly with:

### Compliance Router (`api/routers/compliance.py`)
- Uses central registry instead of hardcoded checks
- Gets current law versions automatically
- Returns law_version in compliance results

### Tendering Router (`api/routers/tendering.py`)
- References laws via registry
- Uses ÖNORM A 2063 from central registry

### Validation Router (`api/routers/validation.py`)
- Uses registry for version checking
- Integrates with external validators (RIS, OIB, ÖNORM)

### Audit Trail (`api/safety/audit_trail.py`)
- Already supports law_version in details dict
- No changes needed - just populate it!

## Future Enhancements

1. **Real RIS Austria Integration**
   - Connect to Rechtsinformationssystem
   - Auto-fetch new laws
   - Auto-detect deprecations

2. **OIB & ÖNORM Auto-Sync**
   - Periodically check for updates
   - Alert when new versions available
   - Auto-update registry

3. **International Standards**
   - Add Eurocodes (EN 1990-1999)
   - Add ISO standards
   - Regional European variants

4. **Advanced Queries**
   - "Which laws changed since last calculation?"
   - "Are there stricter requirements now?"
   - "Historical law genealogy"

5. **Compliance Dashboard**
   - Real-time law update notifications
   - Compliance coverage visualization
   - Regional requirement comparison

## Testing

Run the registry tests:

```bash
pytest tests/test_laws_registry.py -v
```

Key tests cover:
- ✅ Registry initialization and loading
- ✅ Law queries by ID, type, Bundesland
- ✅ Version history and applicable versions
- ✅ Regional variants (Salzburg)
- ✅ Compliance check mappings
- ✅ Audit trail integration
- ✅ Singleton pattern
- ✅ Statistics

## Configuration

All configuration is in JSON files:

- **`austrian_laws.json`**: Add/modify laws here
- **`compliance_mapping.json`**: Map laws to checks
- **`validation/`**: External data source validators

No Python code changes needed to add laws!

## Support

For questions or issues with the Laws Registry:

1. Check `LAWS_REGISTRY_GUIDE.py` for examples
2. Review test cases in `tests/test_laws_registry.py`
3. Read endpoint documentation at `/docs`
4. Check Austrian standards at:
   - OIB: https://www.oib.or.at
   - Austrian Standards: https://www.austrian-standards.at
   - RIS Austria: https://www.ris.bka.gv.at
