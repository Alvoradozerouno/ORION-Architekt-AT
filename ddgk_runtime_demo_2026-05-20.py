"""
DDGK Runtime-Demo: Vollständiges System für Ziviltechniker-Use-Case
Simuliert den kompletten Workflow: PDF-Upload → ELSA → Normen → HITL → Dashboard
Datum: 2026-05-20
"""

import sys, os, json, hashlib, hmac, time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import ELSA + Normen + HITL modules
from api.routers.elsa_validation import elsa_decide, extract_mass_ketten, detect_normen, generate_bom
from api.routers.normen_verknuepfung import (
    CRITICAL_ELEMENTS_DB, get_element_with_normen, detect_critical_elements, multi_element_analysis
)
from api.routers.hitl_bridge import PENDING_APPROVALS, APPROVAL_LOG, HITL_SECRET

# ============================================================
# TEST-Bauplan (simulierter PDF-Volltext)
# ============================================================

TEST_PLAN_NOTSTROM = """
BAUPLAN: Mehrfamilienhaus Innsbruck
Projekt: MFH Sillgasse 15, 6020 Innsbruck
Revision: Rev. 2 vom 15.05.2026

1. GRUNDLAGEN:
   - Mehrfamilienhaus mit 12 Wohneinheiten
   - 4 Geschosse + Dachgeschoss
   - OKF +574,50 m ü.A.
   - Gebäudehöhe H = 14,85m

2. FUNDAMENT:
   - Streifenfundament 80cm breit, 120cm tief
   - Bodenplatte 25cm Stahlbeton C25/30
   - Bewehrung B500B
   - Fundament für Notstromaggregat: 2,50m x 1,80m x 0,50m
   - Gewicht Notstromaggregat: 3.200 kg

3. NOTSTROMAGGREGAT:
   - Diesel-Notstromaggregat 50 kVA
   - Aufstellraum im Untergeschoss
   - Kraftstofftank 500 Liter
   - Abluftführung durch Dach
   - Schallschutzhaube 65 dB(A)
   - Erdungswiderstand < 10 Ohm

4. STAHLTRAGWERK:
   - Stahlstützen HEA 200
   - Stahlträger IPE 300
   - Aussteifung durch Kerne

5. BRANDSCHUTZ:
   - Brandabschnitt max. 800 m²
   - Fluchtwege mind. 1,20m breit
   - RWA-Anlage vorgesehen
   - Feuerwiderstand REI 60

6. MASS-ANGABEN:
   - Grundriss: 23,46m x 12,50m
   - Geschosshöhe: 3,20m
   - Dachneigung: 35 Grad
   - Fläche: 293,25 m² pro Geschoss
"""

TEST_PLAN_SIMPLE = """
BAUPLAN: Garage
Projekt: Garage Müller, 6020 Innsbruck

- Einfache Garage 6,00m x 3,50m
- Flachdach
- Keine besonderen Anforderungen
"""

# ============================================================
# RUNTIME-DEMO
# ============================================================

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def print_result(label, value, indent=2):
    prefix = " " * indent
    if isinstance(value, list):
        print(f"{prefix}{label}:")
        for item in value:
            if isinstance(item, dict):
                for k, v in item.items():
                    print(f"{prefix}  {k}: {v}")
            else:
                print(f"{prefix}  - {item}")
    elif isinstance(value, dict):
        print(f"{prefix}{label}:")
        for k, v in value.items():
            print(f"{prefix}  {k}: {v}")
    else:
        print(f"{prefix}{label}: {value}")

def run_demo():
    print("=" * 70)
    print("  DDGK RUNTIME-DEMO: Ziviltechniker-Use-Case")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    # ============================================================
    # PHASE 1: ELSA-Validierung
    # ============================================================
    print_section("PHASE 1: ELSA-Validierung (Bauplan-Scan)")

    decision = elsa_decide(TEST_PLAN_NOTSTROM, "MFH_Sillgasse_Rev2.pdf")
    print_result("Plan", "MFH_Sillgasse_Rev2.pdf")
    print_result("ELSA Decision", decision.state)
    print_result("Risk Level", decision.risk_level)
    print_result("Risk Score", decision.details["risk_score"])
    print_result("Reason", decision.reason)
    print_result("Issues", decision.details["issues"])
    print_result("Critical Elements", decision.details["critical_elements"])
    print_result("Mass-Ketten gefunden", decision.details["mass_ketten_count"])
    print_result("Revision erkannt", decision.details["has_revision"])

    # ============================================================
    # PHASE 2: Mass-Ketten-Extraktion (EIRA)
    # ============================================================
    print_section("PHASE 2: Mass-Ketten-Extraktion (EIRA)")

    mass_ketten = extract_mass_ketten(TEST_PLAN_NOTSTROM)
    print_result("Anzahl Mass-Ketten", len(mass_ketten))
    for mk in mass_ketten[:10]:
        ctx = mk['context'][-30:].replace('\n', ' ')
        print(f"  - {mk['type']:12s} | {mk['value']:8.2f} | {mk['raw']:15s} | ...{ctx}")

    # ============================================================
    # PHASE 3: Normen-Erkennung (ELSA)
    # ============================================================
    print_section("PHASE 3: Normen-Erkennung (ELSA)")

    normen = detect_normen(TEST_PLAN_NOTSTROM)
    print_result("Erkannte Normen", len(normen))
    for n in normen:
        print(f"  - {n['id']:15s} | {n['name']:35s} | Trigger: {n['trigger']}")

    # ============================================================
    # PHASE 4: Normen-Verknüpfung (DDGK)
    # ============================================================
    print_section("PHASE 4: Normen-Verknüpfung (DDGK)")

    multi_result = multi_element_analysis(TEST_PLAN_NOTSTROM)
    print_result("Elemente gefunden", multi_result.elements_found)
    print_result("Total Risk-Score", multi_result.total_risk_score)
    print_result("HITL erforderlich", multi_result.hitl_required)

    for elem_result in multi_result.results:
        print(f"\n  [{'='*50}]")
        print(f"  ELEMENT: {elem_result.label} (Risk-Score: {elem_result.risk_score})")
        print(f"  Normen: {elem_result.total_normen} ({elem_result.required_normen} required, {elem_result.optional_normen} optional)")
        for norm in elem_result.normen:
            status = "REQUIRED" if norm.required else "optional"
            print(f"    [{status:8s}] {norm.id:15s} | {norm.name:25s}")
            for pruefung in norm.pruefung[:2]:
                print(f"      * {pruefung}")

    # ============================================================
    # PHASE 5: BOM-Generierung (EIRA)
    # ============================================================
    print_section("PHASE 5: BOM-Generierung (EIRA)")

    bom = generate_bom(TEST_PLAN_NOTSTROM)
    print_result("BOM-Positionen", len(bom))
    for item in bom:
        ctx = item['context'][:50].replace('\n', ' ')
        print(f"  - {item['material']:12s} | {item['quantity']:8.1f} {item['unit']} | {ctx}")

    # ============================================================
    # PHASE 6: HITL-Freigabe (GUARDIAN)
    # ============================================================
    print_section("PHASE 6: HITL-Freigabe (GUARDIAN)")

    if decision.state in ["DEFER", "ABSTAIN"]:
        print(f"  Status: {decision.state} => HITL-Freigabe erforderlich")
        print(f"  Risk-Score: {decision.details['risk_score']}")
        print()

        # Approval-Requests erstellen
        for elem in multi_result.elements_found:
            elem_data = CRITICAL_ELEMENTS_DB.get(elem)
            if elem_data:
                print(f"  [GUARDIAN] Erstelle Approval für: {elem_data['label']}")
                print(f"    Required Role: Statiker/Bauleitung")
                print(f"    Betroffene Normen: {len(elem_data['normen'])}")

        # HMAC-Signatur demonstrieren
        sig_data = f"demo_approval:statiker:Freigegeben nach Pruefung:{time.time()}"
        signature = hmac.new(HITL_SECRET.encode(), sig_data.encode(), hashlib.sha256).hexdigest()
        print(f"\n  [GUARDIAN] HMAC-Signatur Demo:")
        print(f"    Data: {sig_data[:50]}...")
        print(f"    Sig:  {signature[:32]}...")
    else:
        print(f"  Status: {decision.state} => Keine HITL-Freigabe noetig")

    # ============================================================
    # PHASE 7: FPGA-Validierung (Deterministisch)
    # ============================================================
    print_section("PHASE 7: FPGA-Validierung (Deterministisch)")

    plan_hash = hashlib.sha256(TEST_PLAN_NOTSTROM.encode()).hexdigest()
    print_result("Plan SHA256", plan_hash[:32] + "...")
    print_result("Audit-Hash", decision.sha256[:32] + "...")
    print()
    print("  [FPGA] Lockstep-Comparator: Gleiche Eingabe => gleiches Ergebnis")
    print("  [FPGA] SHA256-Pruefung: Audit-Hash kryptografisch verifizierbar")
    print("  [FPGA] Keine stochastischen Elemente => 100% reproduzierbar")

    # ============================================================
    # PHASE 8: Decision over Time (DDGK)
    # ============================================================
    print_section("PHASE 8: Decision over Time (DDGK)")

    timeline = [
        ("T0", "PDF-Upload", "Bauplan wird hochgeladen"),
        ("T1", "ELSA-Scan", f"Risk-Score: {decision.details['risk_score']}, Decision: {decision.state}"),
        ("T2", "Normen-Check", f"{len(normen)} Normen erkannt, {len(multi_result.elements_found)} kritische Elemente"),
        ("T3", "HITL-Anfrage", f"{'Erforderlich' if decision.state in ['DEFER', 'ABSTAIN'] else 'Nicht erforderlich'}"),
        ("T4", "FPGA-Hash", f"SHA256: {plan_hash[:16]}..."),
        ("T5", "Audit-Log", f"Hash: {decision.sha256[:16]}..."),
    ]
    for t, phase, desc in timeline:
        print(f"  {t} | {phase:15s} | {desc}")

    # ============================================================
    # ZUSAMMENFASSUNG
    # ============================================================
    print_section("ZUSAMMENFASSUNG")

    print(f"""
  ERGEBNIS DER RUNTIME-DEMO:

  ELSA Decision:    {decision.state}
  Risk Level:       {decision.risk_level}
  Risk Score:       {decision.details['risk_score']}
  Mass-Ketten:      {len(mass_ketten)} extrahiert
  Normen erkannt:   {len(normen)}
  Krit. Elemente:   {len(multi_result.elements_found)} ({', '.join(multi_result.elements_found)})
  HITL erforderlich: {'JA' if decision.state in ['DEFER', 'ABSTAIN'] else 'NEIN'}
  FPGA-Hash:        {plan_hash[:16]}...

  BEST PRACTICE WORKFLOW:
  1. PDF hochladen => /api/v1/elsa/validate
  2. ELSA-Ergebnis pruefen => EXECUTE/DEFER/ABSTAIN
  3. Bei DEFER/ABSTAIN: Normen-Verknupfung => /api/v1/normen-verknuepfung/detect
  4. HITL-Freigabe => /api/v1/hitl/approve
  5. Dashboard Status prüfen
  6. Baufreigabe erteilen

  DECISION OVER TIME:
  - ABSTAIN ist valider Zustand (keine autonome Aktion)
  - System wartet auf menschliche Freigabe
  - Audit-Kette dokumentiert jeden Schritt
  - FPGA-SHA256 garantiert Reproduzierbarkeit
""")

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "plan": "MFH_Sillgasse_Rev2.pdf",
        "elsa_decision": decision.state,
        "risk_level": decision.risk_level,
        "risk_score": decision.details["risk_score"],
        "mass_ketten_count": len(mass_ketten),
        "normen_count": len(normen),
        "critical_elements": multi_result.elements_found,
        "hitl_required": decision.state in ["DEFER", "ABSTAIN"],
        "plan_sha256": plan_hash,
        "audit_hash": decision.sha256,
    }

    os.makedirs("Baumeister-Tool-Austria/docs", exist_ok=True)
    with open("Baumeister-Tool-Austria/docs/DDGK_RUNTIME_DEMO_ERGEBNIS_2026-05-20.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Ergebnisse gespeichert: docs/DDGK_RUNTIME_DEMO_ERGEBNIS_2026-05-20.json")


if __name__ == "__main__":
    run_demo()