# GENESIS V3.0.1 - Validation Scenarios

## Overview

This directory contains YAML-based validation scenarios for automated testing of the GENESIS DUAL-SYSTEM components.

## Structure

```
validation/
├── scenarios/
│   ├── oib_rl_6_energy.yaml       # OIB-RL 6 Energieausweis
│   ├── bsh_typical_spans.yaml     # Typische Spannweiten BSH-Träger
│   ├── dmacas_building_clash.yaml # BIM Clash Detection
│   └── ...
├── results/                        # Test results (auto-generated)
└── README.md                       # This file
```

## Scenario Format

Each YAML file defines one or more test scenarios:

```yaml
name: "OIB-RL 6 Energieausweis Compliance"
version: "3.0.1"
standard: "ÖNORM B 1995-1-1"
trl: 6

scenarios:
  - id: "OIB-RL-6-001"
    description: "6m Spannweite, GL24h, Wohnnutzung"
    input:
      span_m: 6.0
      width_mm: 140
      material: "GL24h"
      dead_load_kn_per_m2: 2.5
      live_load_kn_per_m: 13.5
    expected:
      height_mm: 540
      tolerance_mm: 20
      eta_bending_max: 1.0
      eta_shear_max: 1.0
      w_fin_limit_factor: 200.0
    validation:
      - type: "range_check"
        parameter: "height_mm"
        min: 520
        max: 560
      - type: "compliance"
        parameter: "eta_bending"
        condition: "<=1.0"
      - type: "audit_trail"
        required: true
```

## Running Validation

### Python (BSH-Träger)

```bash
# Run single scenario
python validation/run_scenario.py scenarios/oib_rl_6_energy.yaml

# Run all scenarios
python validation/run_all_scenarios.py
```

### C++ (DMACAS)

```bash
# Build with validation
cd cpp_core/build
cmake .. -DBUILD_VALIDATION=ON
make
./validation_runner ../validation/scenarios/
```

## Test Coverage

| Category | Scenarios | Status |
|----------|-----------|--------|
| OIB-RL 6 (Energy) | 5 | ⏳ Planned |
| Typical Spans | 10 | ⏳ Planned |
| Edge Cases | 8 | ⏳ Planned |
| DMACAS Clash Detection | 6 | ⏳ Planned |
| Multi-Agent Decision | 4 | ⏳ Planned |
| **Total** | **33** | **0% Done** |

## Example Scenarios

### 1. OIB-RL 6 Energy Efficiency

**File**: `oib_rl_6_energy.yaml`

Tests compliance with Austrian energy efficiency regulations for typical residential floor spans.

### 2. BSH Typical Spans

**File**: `bsh_typical_spans.yaml`

Covers standard spans from 4m to 12m with various load conditions.

### 3. DMACAS Building Clash

**File**: `dmacas_building_clash.yaml`

Tests geometric conflict detection between building elements (walls, ducts, pipes).

## Validation Report

After running scenarios, a validation report is generated:

```json
{
  "timestamp": "2026-04-06T17:30:00Z",
  "total_scenarios": 33,
  "passed": 28,
  "failed": 3,
  "skipped": 2,
  "coverage": 84.8,
  "trl_assessment": {
    "current": 6,
    "target": 7,
    "blocking_issues": []
  }
}
```

## Next Steps

1. **Create Scenario Files** (Q2 2026)
   - 5 OIB-RL scenarios
   - 10 typical span scenarios
   - 8 edge case scenarios

2. **Implement Validation Runner** (Q2 2026)
   - Python script for automated execution
   - C++ validation binary

3. **CI/CD Integration** (Q3 2026)
   - GitHub Actions workflow
   - Automated regression testing

4. **Extended Field Testing** (Q3-Q4 2026)
   - 300+ real-world runs
   - Performance monitoring
   - TÜV certification preparation

---

**Version**: 1.0.0
**Status**: 📋 Planned (Structure ready, scenarios to be implemented)
**TRL**: 6 (ready for scenario implementation)
