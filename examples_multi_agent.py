#!/usr/bin/env python3
"""
=============================================================================
ORION MULTI-AGENT SYSTEM - QUICK START
=============================================================================

Dieses Beispiel zeigt die vollständige Nutzung des Multi-Agent Systems.

Autor: Elisabeth Steurer & Gerhard Hirschmann
Datum: 2026-04-07
=============================================================================
"""

from orion_multi_agent_system import (
    ArchitektAgent,
    ZivilingenieurAgent,
    BauphysikerAgent,
    KostenplanerAgent,
    RisikomanagerAgent
)


def beispiel_1_vollstaendige_planung():
    """Beispiel 1: Vollständige Projektplanung mit allen Agenten"""
    print("="*70)
    print("BEISPIEL 1: Vollständige Projektplanung")
    print("="*70)

    architekt = ArchitektAgent()

    projekt = {
        "name": "Wohnhaus Familie Müller",
        "bundesland": "TIROL",
        "ort": "Innsbruck",
        "bauherr": "Franz Müller",
        "bauwerk": {
            "material": "beton",
            "spannweite_m": 8.0,
            "nutzlast_kn_per_m": 20.0,
            "flaeche_m2": 200.0,
            "geschosse": 2,
            "bgf_m2": 180.0
        }
    }

    ergebnis = architekt.plane_projekt_vollstaendig(projekt)

    print("\n📊 ZUSAMMENFASSUNG:")
    print(f"   Status: {ergebnis['gesamtbewertung']['empfehlung']}")
    print(f"   Statik OK: {ergebnis['gesamtbewertung']['statik_ok']}")
    print(f"   Energie OK: {ergebnis['gesamtbewertung']['energie_ok']}")
    print(f"   Kosten P90: {ergebnis['kosten']['empfehlung']['budget_konservativ_eur']:,.0f} €")
    print(f"   Zeitpuffer: {ergebnis['risiken']['empfehlung']['zeitpuffer_tage']:.0f} Tage")


def beispiel_2_nur_statik():
    """Beispiel 2: Nur Statik-Berechnung (deterministisch)"""
    print("\n" + "="*70)
    print("BEISPIEL 2: Nur Statik-Berechnung (DETERMINISTISCH)")
    print("="*70)

    zt = ZivilingenieurAgent()

    bauwerk_beton = {
        "material": "beton",
        "spannweite_m": 10.0,
        "nutzlast_kn_per_m": 25.0
    }

    statik = zt.bemesse_tragwerk(bauwerk_beton)

    print(f"\n📐 STATIK STAHLBETON:")
    print(f"   Status: {statik['status']}")
    print(f"   Höhe: {statik['hoehe_mm']:.0f} mm")
    print(f"   Bewehrung: {statik['bewehrung_mm2']:.0f} mm²")
    print(f"   Ausnutzung: η = {statik['ausnutzung']:.3f}")
    print(f"   Monte Carlo: {statik['monte_carlo']}")
    print(f"   Methode: {statik['methode']}")

    # Generiere normgerechtes Papier
    projekt_info = {
        "name": "Wohnhaus Müller",
        "ort": "Innsbruck",
        "bundesland": "Tirol",
        "bauherr": "Franz Müller"
    }
    papier = zt.generate_statik_papier(statik, projekt_info)
    print(f"\n📄 Statik-Papier generiert ({len(papier)} Zeichen)")


def beispiel_3_nur_kosten():
    """Beispiel 3: Nur Kostenschätzung (probabilistisch, Monte Carlo)"""
    print("\n" + "="*70)
    print("BEISPIEL 3: Nur Kostenschätzung (PROBABILISTISCH - MONTE CARLO)")
    print("="*70)

    kp = KostenplanerAgent()

    bauwerk = {
        "bgf_m2": 250.0,
        "basis_kosten_m2": 2800.0
    }

    kosten = kp.schaetze_kosten_monte_carlo(bauwerk, n_simulations=10000)

    print(f"\n💰 KOSTEN (Monte Carlo, 10.000 Simulationen):")
    print(f"   Basis: {kosten['basis_kosten_eur']:,.0f} €")
    print(f"   P10 (optimistisch): {kosten['perzentile']['p10_eur']:,.0f} €")
    print(f"   P50 (Median): {kosten['perzentile']['p50_eur']:,.0f} €")
    print(f"   P90 (konservativ): {kosten['perzentile']['p90_eur']:,.0f} €")
    print(f"   P95 (Worst-case): {kosten['perzentile']['p95_eur']:,.0f} €")
    print(f"\n   📊 EMPFEHLUNG:")
    print(f"      Budget realistisch: {kosten['empfehlung']['budget_realistisch_eur']:,.0f} € (P75)")
    print(f"      Budget konservativ: {kosten['empfehlung']['budget_konservativ_eur']:,.0f} € (P90)")
    print(f"\n   ⚠️  {kosten['warnung']}")


def beispiel_4_nur_risiken():
    """Beispiel 4: Nur Risikoanalyse (probabilistisch, Monte Carlo)"""
    print("\n" + "="*70)
    print("BEISPIEL 4: Nur Risikoanalyse (PROBABILISTISCH - MONTE CARLO)")
    print("="*70)

    rm = RisikomanagerAgent()

    projekt = {
        "baukosten_eur": 600000.0
    }

    risiken = rm.analysiere_risiken_monte_carlo(projekt, n_simulations=5000)

    print(f"\n⚠️  RISIKEN (Monte Carlo, 5.000 Simulationen):")
    print(f"   Risiken identifiziert: {risiken['risiken_identifiziert']}")
    print(f"   Methode: {risiken['methode']}")

    print(f"\n   ⏱️  VERZÖGERUNGEN:")
    print(f"      Mittel: {risiken['verzoegerung_tage']['mittel']:.1f} Tage")
    print(f"      Median: {risiken['verzoegerung_tage']['median']:.1f} Tage")
    print(f"      P90: {risiken['verzoegerung_tage']['p90']:.1f} Tage")
    print(f"      Maximum: {risiken['verzoegerung_tage']['maximum']:.1f} Tage")

    print(f"\n   💸 MEHRKOSTEN:")
    print(f"      Mittel: {risiken['mehrkosten_eur']['mittel']:,.0f} €")
    print(f"      Median: {risiken['mehrkosten_eur']['median']:,.0f} €")
    print(f"      P90: {risiken['mehrkosten_eur']['p90']:,.0f} €")
    print(f"      Maximum: {risiken['mehrkosten_eur']['maximum']:,.0f} €")

    print(f"\n   💡 EMPFEHLUNG (P80):")
    print(f"      Zeitpuffer: {risiken['empfehlung']['zeitpuffer_tage']:.0f} Tage")
    print(f"      Kostenreserve: {risiken['empfehlung']['kostenreserve_eur']:,.0f} €")


def beispiel_5_vergleich_hybrid():
    """Beispiel 5: Vergleich deterministisch vs probabilistisch"""
    print("\n" + "="*70)
    print("BEISPIEL 5: Vergleich DETERMINISTISCH vs PROBABILISTISCH")
    print("="*70)

    zt = ZivilingenieurAgent()
    kp = KostenplanerAgent()

    bauwerk = {
        "material": "beton",
        "spannweite_m": 8.0,
        "nutzlast_kn_per_m": 20.0,
        "bgf_m2": 180.0
    }

    # Deterministisch: Statik
    statik = zt.bemesse_tragwerk(bauwerk)
    print(f"\n🔒 DETERMINISTISCH (Statik):")
    print(f"   Methode: {statik['methode']}")
    print(f"   Monte Carlo: {statik['monte_carlo']}")
    print(f"   Ausnutzung: η = {statik['ausnutzung']:.3f} (exakt, reproduzierbar)")
    print(f"   Unsicherheit: 0.0 (KEINE Wahrscheinlichkeiten!)")

    # Probabilistisch: Kosten
    kosten = kp.schaetze_kosten_monte_carlo(bauwerk, n_simulations=10000)
    print(f"\n🎲 PROBABILISTISCH (Kosten):")
    print(f"   Methode: {kosten['methode']}")
    print(f"   Monte Carlo: {kosten['monte_carlo']}")
    print(f"   Median: {kosten['perzentile']['p50_eur']:,.0f} € (P50)")
    print(f"   Spanne: {kosten['perzentile']['p10_eur']:,.0f} - {kosten['perzentile']['p90_eur']:,.0f} € (P10-P90)")
    print(f"   Unsicherheit: ~15% (NORMALE Schwankungen im Bauwesen)")

    print(f"\n💡 FAZIT:")
    print(f"   Statik: MUSS deterministisch sein (Zivilingenieur-Unterschrift!)")
    print(f"   Kosten: SOLLEN probabilistisch sein (Realistische Schätzung!)")


if __name__ == "__main__":
    print("⊘∞⧈∞⊘ ORION MULTI-AGENT SYSTEM - EXAMPLES")
    print("Version 1.0.0")
    print()

    try:
        beispiel_1_vollstaendige_planung()
        beispiel_2_nur_statik()
        beispiel_3_nur_kosten()
        beispiel_4_nur_risiken()
        beispiel_5_vergleich_hybrid()

        print("\n" + "="*70)
        print("✅ Alle Beispiele erfolgreich ausgeführt!")
        print("="*70)
        print("\nWeitere Informationen: MULTI_AGENT_IMPLEMENTATION_REPORT.md")

    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
