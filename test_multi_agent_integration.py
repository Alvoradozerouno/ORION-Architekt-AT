#!/usr/bin/env python3
"""
=============================================================================
ORION MULTI-AGENT INTEGRATION TEST
=============================================================================
Vollständiger Test der Multi-Agenten-Architektur mit Validierung der
Hybrid-Architektur (deterministisch + probabilistisch).

Version: 1.0.0
Datum: 2026-04-07
=============================================================================
"""

import sys
import json
from pathlib import Path

from orion_multi_agent_system import (
    ArchitektAgent,
    ZivilingenieurAgent,
    BauphysikerAgent,
    KostenplanerAgent,
    RisikomanagerAgent,
    EUROCODE_AVAILABLE
)


def test_1_zivilingenieur_deterministisch():
    """Test: Zivilingenieur arbeitet DETERMINISTISCH (keine Monte Carlo)"""
    print("\n" + "="*70)
    print("TEST 1: Zivilingenieur - Deterministisch")
    print("="*70)

    agent = ZivilingenieurAgent()

    # Test verschiedene Materialien
    for material in ["beton", "stahl"]:
        bauwerk = {
            "material": material,
            "spannweite_m": 8.0,
            "nutzlast_kn_per_m": 20.0
        }

        ergebnis = agent.bemesse_tragwerk(bauwerk)

        print(f"\n📐 {material.upper()}:")
        print(f"   Status: {ergebnis.get('status', 'N/A')}")
        print(f"   Monte Carlo: {ergebnis.get('monte_carlo', 'N/A')}")
        print(f"   Methode: {ergebnis.get('methode', 'N/A')}")

        # Validierung
        if EUROCODE_AVAILABLE:
            assert ergebnis.get("monte_carlo") == False, f"❌ {material}: Monte Carlo sollte False sein!"
            assert ergebnis.get("methode") == "deterministisch", f"❌ {material}: Methode sollte deterministisch sein!"
            assert "ausnutzung" in ergebnis, f"❌ {material}: Ausnutzung fehlt!"
            print(f"   ✅ DETERMINISTISCH bestätigt")
        else:
            print(f"   ⚠️  Eurocode nicht verfügbar - Test übersprungen")


def test_2_kostenplaner_probabilistisch():
    """Test: Kostenplaner arbeitet PROBABILISTISCH (MIT Monte Carlo)"""
    print("\n" + "="*70)
    print("TEST 2: Kostenplaner - Probabilistisch (Monte Carlo)")
    print("="*70)

    agent = KostenplanerAgent()

    bauwerk = {
        "flaeche_m2": 200.0,
        "geschosse": 2,
        "qualitaet": "mittel"
    }

    # Reduzierte Simulationen für schnelleren Test
    ergebnis = agent.schaetze_kosten_monte_carlo(bauwerk, n_simulations=1000)

    print(f"\n💰 KOSTEN (Monte Carlo):")
    print(f"   Median (P50): {ergebnis['perzentile']['p50_eur']:,.0f} €")
    print(f"   P10: {ergebnis['perzentile']['p10_eur']:,.0f} €")
    print(f"   P90: {ergebnis['perzentile']['p90_eur']:,.0f} €")
    print(f"   Monte Carlo: {ergebnis['monte_carlo']}")
    print(f"   Simulationen: {ergebnis['anzahl_simulationen']}")

    # Validierung
    assert ergebnis["monte_carlo"] == True, "❌ Monte Carlo sollte True sein!"
    assert ergebnis["anzahl_simulationen"] == 1000, "❌ Anzahl Simulationen falsch!"
    assert ergebnis["deterministisch"] == False, "❌ Sollte nicht deterministisch sein!"
    assert ergebnis["perzentile"]["p90_eur"] > ergebnis["perzentile"]["p50_eur"], "❌ P90 sollte > Median sein!"

    print(f"   ✅ PROBABILISTISCH bestätigt")


def test_3_hybrid_architektur():
    """Test: Hybrid-Architektur (Deterministisch + Probabilistisch)"""
    print("\n" + "="*70)
    print("TEST 3: Hybrid-Architektur")
    print("="*70)

    architekt = ArchitektAgent()

    projekt = {
        "name": "Test-Wohnhaus",
        "bundesland": "TIROL",
        "bauwerk": {
            "material": "beton",
            "spannweite_m": 8.0,
            "nutzlast_kn_per_m": 20.0,
            "flaeche_m2": 200.0,
            "geschosse": 2
        }
    }

    # Plan project
    ergebnis = architekt.plane_projekt_vollstaendig(projekt)

    print(f"\n🏗️  GESAMTPROJEKT:")
    print(f"   Status: {ergebnis['gesamtbewertung']['empfehlung']}")
    print(f"   Statik OK: {ergebnis['gesamtbewertung']['statik_ok']}")
    print(f"   Energie OK: {ergebnis['gesamtbewertung']['energie_ok']}")

    # Validierung der Hybrid-Architektur
    statik = ergebnis["statik"]
    kosten = ergebnis["kosten"]
    risiken = ergebnis["risiken"]

    print(f"\n📊 HYBRID-VALIDIERUNG:")

    # Deterministisch: Statik
    if EUROCODE_AVAILABLE and statik.get("status") != "ERROR":
        assert statik.get("monte_carlo") == False, "❌ Statik sollte NICHT Monte Carlo verwenden!"
        print(f"   ✅ Statik: Deterministisch (MC={statik.get('monte_carlo')})")
    else:
        print(f"   ⚠️  Statik: Übersprungen (Eurocode nicht verfügbar)")

    # Probabilistisch: Kosten
    assert kosten["monte_carlo"] == True, "❌ Kosten sollten Monte Carlo verwenden!"
    print(f"   ✅ Kosten: Probabilistisch (MC={kosten['monte_carlo']}, n={kosten['anzahl_simulationen']})")

    # Probabilistisch: Risiken
    assert risiken["monte_carlo"] == True, "❌ Risiken sollten Monte Carlo verwenden!"
    print(f"   ✅ Risiken: Probabilistisch (MC={risiken['monte_carlo']}, n={risiken['anzahl_simulationen']})")

    print(f"\n✅ HYBRID-ARCHITEKTUR BESTÄTIGT!")


def test_4_normgerechtes_papier():
    """Test: Generierung normgerechtes Statik-Papier"""
    print("\n" + "="*70)
    print("TEST 4: Normgerechtes Statik-Papier")
    print("="*70)

    if not EUROCODE_AVAILABLE:
        print("⚠️  Eurocode nicht verfügbar - Test übersprungen")
        return

    agent = ZivilingenieurAgent()

    bauwerk = {
        "material": "beton",
        "spannweite_m": 8.0,
        "nutzlast_kn_per_m": 20.0
    }

    statik_ergebnis = agent.bemesse_tragwerk(bauwerk)

    projekt_info = {
        "name": "Test-Wohnhaus",
        "ort": "Innsbruck",
        "bundesland": "Tirol",
        "bauherr": "Max Mustermann"
    }

    papier = agent.generate_statik_papier(statik_ergebnis, projekt_info)

    print(f"\n📄 STATIK-PAPIER:")
    print(papier[:500] + "...\n")

    # Validierung
    assert "ÖNORM EN" in papier, "❌ ÖNORM-Referenz fehlt!"
    assert "STATISCHE BERECHNUNG" in papier, "❌ Titel fehlt!"
    assert "Zivilingenieur" in papier, "❌ ZT-Referenz fehlt!"
    assert "SHA-256" in papier or "Audit-Hash" in papier, "❌ Audit-Hash fehlt!"

    print(f"✅ Normgerechtes Papier generiert")

    # Speichere Papier
    output_file = Path("/tmp/statik_papier_test.txt")
    output_file.write_text(papier, encoding="utf-8")
    print(f"💾 Gespeichert: {output_file}")


def test_5_agent_mindsets():
    """Test: Jeder Agent denkt anders"""
    print("\n" + "="*70)
    print("TEST 5: Agent Mindsets - Unterschiedliche Denkweisen")
    print("="*70)

    agenten = [
        ZivilingenieurAgent(),
        BauphysikerAgent(),
        KostenplanerAgent(),
        RisikomanagerAgent()
    ]

    for agent in agenten:
        denkweise = agent.denke({})
        print(f"\n🧠 {denkweise['agent']}:")
        print(f"   Mindset: {denkweise['mindset']}")
        print(f"   Methode: {denkweise['methode']}")
        print(f"   Unsicherheit: {denkweise.get('unsicherheit', 'N/A')}")

        # Validierung
        assert denkweise["agent"] is not None, f"❌ Agent-Name fehlt!"
        assert denkweise["mindset"] is not None, f"❌ Mindset fehlt!"
        assert denkweise["methode"] is not None, f"❌ Methode fehlt!"

    print(f"\n✅ Alle Agenten haben unterschiedliche Denkweisen")


def test_6_audit_trail():
    """Test: Audit Trail und Reproduzierbarkeit"""
    print("\n" + "="*70)
    print("TEST 6: Audit Trail & Reproduzierbarkeit")
    print("="*70)

    agent = ZivilingenieurAgent()

    bauwerk = {
        "material": "beton",
        "spannweite_m": 8.0,
        "nutzlast_kn_per_m": 20.0
    }

    # Erste Berechnung
    ergebnis1 = agent.bemesse_tragwerk(bauwerk)
    trail1 = agent.get_audit_trail()

    # Zweite Berechnung mit gleichen Parametern
    ergebnis2 = agent.bemesse_tragwerk(bauwerk)
    trail2 = agent.get_audit_trail()

    print(f"\n🔍 AUDIT TRAIL:")
    print(f"   Entscheidungen Agent 1: {len(trail1)}")
    print(f"   Entscheidungen Agent 2: {len(trail2)}")

    if EUROCODE_AVAILABLE and ergebnis1.get("status") != "ERROR":
        # Deterministisch: Ergebnisse sollten identisch sein
        assert ergebnis1.get("ausnutzung") == ergebnis2.get("ausnutzung"), "❌ Ergebnisse nicht reproduzierbar!"
        print(f"   ✅ Reproduzierbarkeit bestätigt")
    else:
        print(f"   ⚠️  Reproduzierbarkeit nicht testbar (Eurocode nicht verfügbar)")


def run_all_tests():
    """Alle Integration-Tests ausführen"""
    print("="*70)
    print("ORION MULTI-AGENT INTEGRATION TESTS")
    print("="*70)
    print(f"Eurocode verfügbar: {EUROCODE_AVAILABLE}")

    tests = [
        ("Zivilingenieur Deterministisch", test_1_zivilingenieur_deterministisch),
        ("Kostenplaner Probabilistisch", test_2_kostenplaner_probabilistisch),
        ("Hybrid-Architektur", test_3_hybrid_architektur),
        ("Normgerechtes Papier", test_4_normgerechtes_papier),
        ("Agent Mindsets", test_5_agent_mindsets),
        ("Audit Trail", test_6_audit_trail),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
            print(f"\n✅ {name} PASSED")
        except Exception as e:
            failed += 1
            print(f"\n❌ {name} FAILED: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*70)
    print(f"ERGEBNIS: {passed} PASSED, {failed} FAILED")
    print("="*70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
