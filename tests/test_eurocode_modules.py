#!/usr/bin/env python3
"""
=============================================================================
EUROCODE MODULE TESTS – Vollständige Test-Suite
=============================================================================
Tests für alle 5 Eurocode-Module:
- EC2 (Betonbau)
- EC3 (Stahlbau)
- EC6 (Mauerwerksbau)
- EC7 (Geotechnik)
- EC8 (Erdbeben)

Version: 1.0.0
Datum: 2026-04-07
=============================================================================
"""

import sys
from pathlib import Path

# Add module paths
sys.path.insert(0, str(Path(__file__).parent.parent / "eurocode_ec2_at" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "eurocode_ec3_at" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "eurocode_ec6_at" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "eurocode_ec7_at" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "eurocode_ec8_at" / "src"))


def test_ec2_betonbau():
    """Test EC2 Betonbau-Modul"""
    from beton_träger_v1 import BetonTraegerEC2AT_V1, EC2Config

    config = EC2Config(
        L_SPANNWEITE_M=8.0,
        QK_NUTZLAST_KN_PER_M=20.0,
    )

    calc = BetonTraegerEC2AT_V1(config)
    results = calc.run_optimization()

    assert len(results) > 0, "EC2: Keine Ergebnisse"
    # Find first result with acceptable utilization
    ok_results = [r for r in results if r.eta_bending <= 1.0]
    assert len(ok_results) > 0, "EC2: Keine gültige Lösung"
    best = ok_results[0]
    assert best.h_total_mm >= 500, "EC2: Trägerhöhe zu klein"
    assert best.As_vorh_mm2 > 0, "EC2: Keine Bewehrung"
    print(f"✅ EC2 Test OK: h={best.h_total_mm}mm, As={best.As_vorh_mm2:.0f}mm², η={best.eta_bending:.3f}")


def test_ec3_stahlbau():
    """Test EC3 Stahlbau-Modul"""
    from stahl_träger_v1 import StahlTraegerEC3AT_V1, EC3Config

    config = EC3Config(
        L_SPANNWEITE_M=8.0,
        QK_NUTZLAST_KN_PER_M=20.0,
    )

    calc = StahlTraegerEC3AT_V1(config)
    results = calc.run_optimization()

    assert len(results) > 0, "EC3: Keine Ergebnisse"
    ok_results = [r for r in results if r.bending_ok and r.shear_ok and r.deflection_ok]
    assert len(ok_results) > 0, "EC3: Keine gültige Lösung"
    best = ok_results[0]
    assert best.mass_kg_per_m > 0, "EC3: Masse = 0"
    assert best.eta_bending <= 1.0, "EC3: Biegung überschritten"
    print(f"✅ EC3 Test OK: {best.profile_name}, m={best.mass_kg_per_m}kg/m, η={best.eta_bending:.3f}")


def test_ec6_mauerwerksbau():
    """Test EC6 Mauerwerksbau-Modul"""
    from mauerwerk_wand_v1 import MauerwerkWandEC6AT_V1, EC6Config

    config = EC6Config(
        WANDHOEHE_M=3.0,
        WANDLAENGE_M=5.0,
        N_ED_KN=200.0,
        MAUERSTEIN="ZIEGEL_12",
        MOERTEL="M10",
    )

    calc = MauerwerkWandEC6AT_V1(config)
    results = calc.run_optimization()

    assert len(results) > 0, "EC6: Keine Ergebnisse"
    ok_results = [r for r in results if r.status == "OK"]
    assert len(ok_results) > 0, "EC6: Keine gültige Lösung"
    best = ok_results[0]
    assert best.wanddicke_mm >= 250, "EC6: Wanddicke zu klein"
    assert best.eta_druck <= 1.0, "EC6: Druck überschritten"
    print(f"✅ EC6 Test OK: t={best.wanddicke_mm}mm, λ={best.schlankheit_lambda:.1f}, η={best.eta_druck:.3f}")


def test_ec7_geotechnik():
    """Test EC7 Geotechnik-Modul"""
    from fundament_v1 import FlachfundamentEC7AT_V1, EC7Config

    config = EC7Config(
        N_ED_KN=500.0,
        BODENKLASSE="KIES_DICHT",
        T_M=1.0,
    )

    calc = FlachfundamentEC7AT_V1(config)
    results = calc.run_optimization()

    assert len(results) > 0, "EC7: Keine Ergebnisse"
    ok_results = [r for r in results if r.status == "OK"]
    assert len(ok_results) > 0, "EC7: Keine gültige Lösung"
    best = ok_results[0]
    assert best.A_m2 > 0, "EC7: Fläche = 0"
    assert best.eta_sohldruck <= 1.0, "EC7: Sohldruck überschritten"
    assert best.setzung_mm >= 0, "EC7: Setzung negativ"
    print(f"✅ EC7 Test OK: A={best.A_m2:.1f}m², σ={best.sigma_kpa:.1f}kPa, s={best.setzung_mm:.1f}mm")


def test_ec8_erdbeben():
    """Test EC8 Erdbeben-Modul"""
    from erdbeben_v1 import ErdbebenEC8AT_V1, EC8Config

    config = EC8Config(
        ERDBEBENZONE="TIROL_SUED",
        UNTERGRUND="C",
        BAUWERKSTYP="STAHLBETON_MITTEL",
        GESCHOSSZAHL=3,
        MASSE_PRO_GESCHOSS_T=200.0,
    )

    calc = ErdbebenEC8AT_V1(config)
    result = calc.run_calculation()

    assert result.T_s > 0, "EC8: Eigenperiode = 0"
    assert result.Sd_T_ms2 > 0, "EC8: Spektrale Beschleunigung = 0"
    assert result.F_b_kn > 0, "EC8: Basisscherkraft = 0"
    assert result.status == "INFO", "EC8: Falscher Status"
    print(f"✅ EC8 Test OK: T={result.T_s:.3f}s, Sd={result.Sd_T_ms2:.3f}m/s², Fb={result.F_b_kn:.1f}kN")


def run_all_tests():
    """Alle Tests ausführen"""
    print("=" * 70)
    print("EUROCODE MODULE TESTS – Start")
    print("=" * 70)
    print()

    tests = [
        ("EC2 Betonbau", test_ec2_betonbau),
        ("EC3 Stahlbau", test_ec3_stahlbau),
        ("EC6 Mauerwerksbau", test_ec6_mauerwerksbau),
        ("EC7 Geotechnik", test_ec7_geotechnik),
        ("EC8 Erdbeben", test_ec8_erdbeben),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            print(f"Testing {name}...", end=" ")
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
            failed += 1

    print()
    print("=" * 70)
    print(f"ERGEBNIS: {passed} PASSED, {failed} FAILED")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
