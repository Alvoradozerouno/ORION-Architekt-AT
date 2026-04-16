#!/usr/bin/env python3
"""
ORION Architekt AT - AI Integration Test
=========================================

End-to-End Integration Test demonstrating complete AI-powered tendering workflow:
1. AI Quantity Takeoff from BIM/IFC
2. Live Cost Database pricing
3. LV Generation (ÖNORM A 2063)
4. AI Tender Evaluation

Author: ORION Architekt AT Team
Date: 2026-04-09
"""

from typing import Dict, List, Any
from datetime import datetime
import sys

# Import all AI modules
from ai_quantity_takeoff import automatic_quantity_takeoff_workflow, IFCElement, IFCElementType
from live_cost_database import (
    calculate_live_price,
    get_current_price_index,
    generate_price_trend_report,
    MaterialCategory,
    BAUPREISINDEX_2026,
)
from ai_tender_evaluation import BidDocument, ai_evaluate_bid


def print_separator(title: str = ""):
    """Print formatted separator"""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    else:
        print(f"\n{'-'*80}\n")


def end_to_end_integration_test():
    """
    Complete integration test: BIM → AI Takeoff → Live Pricing → LV → AI Evaluation

    Scenario: Einfamilienhaus in Wien, 3 Angebote evaluieren
    """

    print_separator("ORION Architekt AT - AI Integration Test")
    print(f"Testdatum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Projekt: Einfamilienhaus Wien - Neubau")
    print(f"Workflow: IFC → AI Takeoff → Live Costs → LV → AI Evaluation")

    # ========================================================================
    # PHASE 1: AI Quantity Takeoff from BIM
    # ========================================================================
    print_separator("PHASE 1: AI Quantity Takeoff from BIM/IFC")

    print("🤖 Analysiere IFC-Modell mit AI...")
    takeoff_result = automatic_quantity_takeoff_workflow(
        source_file="projekt_einfamilienhaus_wien.ifc",
        project_name="Einfamilienhaus Wien",
        bundesland="wien",
    )

    print(f"✓ Projekt: {takeoff_result['project_name']}")
    print(f"✓ Elemente extrahiert: {takeoff_result['statistics']['total_elements']}")
    print(f"✓ Gesamtvolumen: {takeoff_result['statistics']['total_volume_m3']:.2f} m³")
    print(f"✓ Gesamtfläche: {takeoff_result['statistics']['total_area_m2']:.2f} m²")
    print(f"✓ AI Confidence: {takeoff_result['statistics']['confidence_score']}%")
    print(f"✓ Geschätzte Kosten: EUR {takeoff_result['statistics']['estimated_cost_eur']:,.2f}")

    print("\nExtrahierte Bauteile:")
    trades = list(takeoff_result.get("quantities_by_trade", {}).items())[:5]
    for gewerk, positions in trades:  # Show first 5
        print(f"  • Gewerk {gewerk}: {len(positions)} Positionen")

    # ========================================================================
    # PHASE 2: Live Cost Database Integration
    # ========================================================================
    print_separator("PHASE 2: Live Cost Database - Aktuelle Preise")

    print("📊 Lade aktuelle Baupreisindizes (Statistik Austria)...")
    indices = BAUPREISINDEX_2026

    print("\nAktuelle Indices (Q1 2026, Basis 2015=100):")
    for category in [
        MaterialCategory.BETON,
        MaterialCategory.STAHL,
        MaterialCategory.HOLZ,
        MaterialCategory.ZIEGEL,
    ]:
        idx = indices[category]
        month_change = (
            ((idx.index_value / idx.previous_month - 1) * 100) if idx.previous_month else 0
        )
        year_change = ((idx.index_value / idx.previous_year - 1) * 100) if idx.previous_year else 0
        print(
            f"  {idx.category:30} Index: {idx.index_value:6.1f}  "
            f"ΔM: {month_change:+.2f}%  ΔJ: {year_change:+.2f}%"
        )

    # Calculate live prices for key materials
    print("\nLive-Preise für Wien (Regionalfaktor: 1.15):")

    sample_prices = {
        "Stahlbeton C30/37": (315.00, MaterialCategory.BETON),
        "Baustahl S235": (1.85, MaterialCategory.STAHL),
        "Brettschichtholz GL24": (780.00, MaterialCategory.HOLZ),
        "Hochlochziegel 38cm": (42.50, MaterialCategory.ZIEGEL),
    }

    live_prices = {}
    for material_name, (base_price, category) in sample_prices.items():
        live_data = calculate_live_price(base_price, category, "wien")
        live_prices[material_name] = live_data.current_price_eur

        price_increase = (live_data.current_price_eur / base_price - 1) * 100
        print(
            f"  {material_name:30} EUR {live_data.current_price_eur:8.2f}  "
            f"(Basis: EUR {base_price:6.2f}, +{price_increase:.1f}%)"
        )

    # ========================================================================
    # PHASE 3: LV Generation (ÖNORM A 2063)
    # ========================================================================
    print_separator("PHASE 3: LV-Generierung (ÖNORM A 2063)")

    print("📝 Leistungsverzeichnis aus AI Takeoff...")

    # Use positions from takeoff_result
    lv_positions = takeoff_result["lv_positions"]
    lv_sum = takeoff_result["statistics"]["estimated_cost_eur"]

    print(f"✓ LV-Positionen generiert: {len(lv_positions)}")
    print(f"✓ Gewerke abgedeckt: {len(set(p['leistungsgruppe'] for p in lv_positions))}")

    print("\nLeistungsverzeichnis (Auszug):")
    print(f"{'OZ':<8} {'LG':<12} {'Bezeichnung':<40} {'Menge':>10} {'EP':>12} {'GP':>14}")
    print("-" * 100)

    total_lv_cost = 0
    for pos in lv_positions[:8]:  # Show first 8 positions
        gp = pos["gesamtpreis_basis"]
        total_lv_cost += gp
        print(
            f"{pos['oz']:<8} {pos['leistungsgruppe']:<12} {pos['bezeichnung']:<40} "
            f"{pos['menge']:>8.2f} {pos['einheit']:<2} EUR {pos['einheitspreis_basis']:>8.2f} "
            f"EUR {gp:>10.2f}"
        )

    if len(lv_positions) > 8:
        remaining = len(lv_positions) - 8
        print(f"... und {remaining} weitere Positionen")

    print(f"\n{'GESAMT LV-SUMME:':<62} EUR {lv_sum:>10,.2f}")

    # ========================================================================
    # PHASE 4: Simulate Bids Reception
    # ========================================================================
    print_separator("PHASE 4: Angebote empfangen")

    print("📬 3 Angebote eingegangen...")

    # Create realistic bid amounts based on LV sum

    bids = [
        BidDocument(
            bid_id="BID-2026-001",
            bidder_name="Baufirma Alpha GmbH",
            bid_amount=lv_sum * 1.12,  # +12% (realistic markup)
            execution_time_days=180,
            warranty_years=5,
            technical_proposal="Detaillierte Ausführungsplanung, BIM-Koordination, "
            "wöchentliche Baubesprechungen, Qualitätssicherung nach ÖNORM",
            company_profile="ÖNORM B 2110 Werkvertrag, Gewährleistung 5 Jahre, "
            "Bauzeit 180 Tage, Sicherheitskonzept vorhanden",
        ),
        BidDocument(
            bid_id="BID-2026-002",
            bidder_name="Baumeister Beta",
            bid_amount=lv_sum * 0.84,  # -16% (suspiciously low - dumping!)
            execution_time_days=120,  # Too short
            warranty_years=2,  # Too little
            technical_proposal="Standardausführung",
            company_profile="Werkvertrag, Gewährleistung 2 Jahre",
        ),
        BidDocument(
            bid_id="BID-2026-003",
            bidder_name="Bau Gamma AG",
            bid_amount=lv_sum * 1.17,  # +17% (higher price)
            execution_time_days=200,
            warranty_years=4,
            technical_proposal="Hochwertige Ausführung, Nachhaltigkeitskonzept, "
            "Energieeffizienz-Optimierung",
            company_profile="ÖNORM B 2110, Gewährleistung 4 Jahre, Bauzeit 200 Tage",
        ),
    ]

    print(f"\n{'Firma':<30} {'Angebotssumme':>15} {'Bauzeit':>10} {'Garantie':>10}")
    print("-" * 70)
    for bid in bids:
        deviation = (bid.bid_amount / lv_sum - 1) * 100
        print(
            f"{bid.bidder_name:<30} EUR {bid.bid_amount:>10,.2f} "
            f"({deviation:+.1f}%)  {bid.execution_time_days:>3} Tage  {bid.warranty_years:>2} Jahre"
        )

    # ========================================================================
    # PHASE 5: AI Tender Evaluation
    # ========================================================================
    print_separator("PHASE 5: AI-gestützte Angebotsbewertung")

    print("🤖 AI analysiert und bewertet Angebote...")

    # Define evaluation criteria
    criteria = {
        "price": 0.40,  # 40% weight
        "quality": 0.25,  # 25% weight
        "technical": 0.20,  # 20% weight
        "timeline": 0.15,  # 15% weight
    }

    print("\nBewertungskriterien:")
    for criterion, weight in criteria.items():
        print(f"  • {criterion}: {weight*100:.0f}%")

    # Evaluate all bids
    evaluations = []
    for bid in bids:
        evaluation = ai_evaluate_bid(bid, bids, criteria)
        evaluations.append((bid, evaluation))

    # Sort by overall score
    evaluations.sort(key=lambda x: x[1].overall_score, reverse=True)

    print("\n" + "=" * 100)
    print("AI BEWERTUNGSERGEBNIS")
    print("=" * 100)

    for rank, (bid, eval_result) in enumerate(evaluations, 1):
        star = "★" if eval_result.recommended else " "

        print(
            f"\n{rank}. {star} {bid.bidder_name:<30} Gesamtscore: {eval_result.overall_score:.1f}/100"
        )
        print(f"   {'─'*95}")
        print(f"   Angebotssumme:  EUR {bid.bid_amount:>10,.2f}")
        print(f"   Bauzeit:        {bid.execution_time_days:>3} Tage")
        print(f"   Garantie:       {bid.warranty_years:>3} Jahre")
        print(f"")
        print(f"   Score-Details:")
        print(f"     • Preis:      {eval_result.price_score:>5.1f}/100  (Gewicht: 40%)")
        print(f"     • Qualität:   {eval_result.quality_score:>5.1f}/100  (Gewicht: 25%)")
        print(f"     • Technik:    {eval_result.technical_score:>5.1f}/100  (Gewicht: 20%)")
        print(f"     • Zeitplan:   {eval_result.price_score:>5.1f}/100  (Gewicht: 15%)")
        print(f"")
        print(f"   Risiko-Assessment: {eval_result.total_risk_score:.1f}/10")

        if eval_result.risk_assessments:
            high_risks = [
                r for r in eval_result.risk_assessments if r.level.value in ["hoch", "kritisch"]
            ]
            if high_risks:
                print(f"   ⚠️  Risiken gefunden:")
                for risk in high_risks[:3]:  # Show top 3 risks
                    print(f"      • {risk.category}: {risk.description} ({risk.level.value})")

        compliance_rate = (
            (
                len([c for c in eval_result.compliance_checks if c.compliant])
                / len(eval_result.compliance_checks)
                * 100
            )
            if eval_result.compliance_checks
            else 0
        )
        print(
            f"   Compliance:    {compliance_rate:.0f}% ({len([c for c in eval_result.compliance_checks if c.compliant])}/{len(eval_result.compliance_checks)} erfüllt)"
        )

        print(f"")
        print(f"   EMPFEHLUNG:    {'✓ JA' if eval_result.recommended else '✗ NEIN'}")
        print(f"   Begründung:    {eval_result.recommendation_reason}")

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print_separator("ZUSAMMENFASSUNG - End-to-End Integration")

    best_bid, best_eval = evaluations[0]

    print(
        f"✓ AI Quantity Takeoff:     {takeoff_result['statistics']['total_elements']} Bauteile extrahiert"
    )
    print(f"✓ Live Cost Database:       {len(indices)} Material-Kategorien aktualisiert")
    print(f"✓ LV-Generierung:           {len(lv_positions)} Positionen, EUR {lv_sum:,.2f}")
    print(f"✓ AI Tender Evaluation:     {len(bids)} Angebote bewertet")
    print(f"")
    print(f"🏆 BESTE WAHL: {best_bid.bidder_name}")
    print(f"   Score: {best_eval.overall_score:.1f}/100")
    print(f"   Preis: EUR {best_bid.bid_amount:,.2f}")
    print(f"   Risiko: {best_eval.total_risk_score:.1f}/10")
    print(f"   {best_eval.recommendation_reason}")

    print_separator()
    print("✓ Integration Test erfolgreich abgeschlossen!")
    print(f"  Workflow-Dauer: Echtzeit (automatisiert)")
    print(f"  Manueller Aufwand ohne AI: ~2-3 Wochen")
    print(f"  Zeitersparnis: >95%")
    print_separator()

    return {
        "takeoff_result": takeoff_result,
        "live_prices": live_prices,
        "lv_positions": lv_positions,
        "bids": bids,
        "evaluations": evaluations,
        "recommended_bid": (best_bid, best_eval),
    }


if __name__ == "__main__":
    try:
        result = end_to_end_integration_test()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Integration Test fehlgeschlagen: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
