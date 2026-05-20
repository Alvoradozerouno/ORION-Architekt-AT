"""
DDGK Runtime-Demo Diskussion: Vollständiges System für Ziviltechniker-Use-Case
Alle Agenten + FPGA + ELSA + Decision over Time + Unsicherheits-Handling
Datum: 2026-05-20
"""

import json
from datetime import datetime

# ============================================================
# AGENTEN-PROFIL FÜR DIE DISKUSSION
# ============================================================

AGENTS = {
    "ELSA": {
        "rolle": "Bauplan-Validierungs-Engine",
        "kompetenz": "EXECUTE/DEFER/ABSTAIN Entscheidungen, Normen-Erkennung, Mass-Ketten-Extraktion",
        "perspektive": "Deterministische Validierung mit Risk-Score",
    },
    "EIRA": {
        "rolle": "Edge Intelligence Runtime Agent",
        "kompetenz": "Mass-Ketten-Auto-Extraktion, BOM-Generierung, FPGA-Target-Compilation",
        "perspektive": "Edge-First: Alles lokal, keine Cloud-Abhaengigkeit",
    },
    "ORION": {
        "rolle": "System-Orchestrator",
        "kompetenz": "API-Management, FastAPI-Routing, Dashboard, Multi-Agent-Koordination",
        "perspektive": "Gesamtsystem: Alle Komponenten muessen nahtlos zusammenarbeiten",
    },
    "GUARDIAN": {
        "rolle": "Sicherheits- und HITL-Bridge",
        "kompetenz": "HMAC-Signatur, 3-Rollen-Freigabe (Architekt/Statiker/Bauleitung), Audit-Log",
        "perspektive": "Sicherheit zuerst: Keine autonome Aktion bei HIGH-Risk",
    },
    "DDGK": {
        "rolle": "Distributed Dynamic Governance Kernel",
        "kompetenz": "Policy-Checks, Decision over Time, Audit-Kette, Eskalation",
        "perspektive": "Governance: Wer entscheidet was wann? Was passiert bei ABSTAIN?",
    },
    "FPGA": {
        "rolle": "Deterministische Hardware-Verarbeitung",
        "kompetenz": "EIRA-FPGA-Targets, SHA256-Pruefung, Lockstep-Comparator, AXI4-Interface",
        "perspektive": "Hardware: Alles muss deterministisch und reproduzierbar sein",
    },
}

# ============================================================
# USE-CASE: Ziviltechniker-Büro prüft Bauplan
# ============================================================

USE_CASE = {
    "szenario": "Ziviltechniker-Büro in Innsbruck prüft Bauplan für Mehrfamilienhaus",
    "eingabe": "PDF-Bauplan mit: Notstromaggregat, Fundament, Stahltragwerk, Brandschutz",
    "erwartung": "Automatische Validierung + Normen-Verknüpfung + HITL-Freigabe bei Unsicherheit",
    "zeitrahmen": "Entscheidung über Zeit: T0=Upload, T1=ELSA-Scan, T2=Normen-Check, T3=HITL, T4=Freigabe",
}

# ============================================================
# DISKUSSIONSRUNDE
# ============================================================

DISKUSSION = {
    "titel": "DDGK Runtime-Demo: Vollständiges System für Ziviltechniker-Use-Case",
    "datum": datetime.now().isoformat(),
    "teilnehmer": list(AGENTS.keys()),
    "runden": [
        {
            "runde": 1,
            "thema": "System-Architektur und Datenfluss",
            "beitraege": {
                "ORION": "Ich orchestriere den gesamten Datenfluss: PDF-Upload → ELSA-Validierung → Normen-Verknüpfung → HITL-Freigabe → Dashboard. FastAPI mit 17+ Endpoints. Alles in einer API.",
                "ELSA": "Ich empfange den PDF-Volltext und extrahiere: (1) Mass-Ketten automatisch, (2) kritische Elemente via Keywords, (3) Risk-Score Berechnung. Bei Score >= 8 → ABSTAIN, bei >= 4 → DEFER, sonst EXECUTE.",
                "EIRA": "Ich liefere die Mass-Ketten-Extraktion mit 5 Regex-Patterns für Längen, Breiten, Höhen, Flächen, Volumen. Plus BOM-Generierung für 7 Material-Kategorien. Alles deterministisch, keine LLM.",
                "FPGA": "Meine EIRA-FPGA-Targets (SHA256, Lockstep-Comparator, AXI4-Lite) stellen sicher, dass jede Validierung reproduzierbar ist. Der SHA256-Hash jedes Plans wird in der Audit-Kette gespeichert.",
            },
        },
        {
            "runde": 2,
            "thema": "ELSA-Validierung am konkreten Beispiel: Notstromaggregat",
            "beitraege": {
                "ELSA": "Beispiel: PDF enthält 'Notstromaggregat'. Ich erkenne: (1) Keyword 'notstromaggregat' → Risk-Score += 4, (2) Keyword 'brandschutz' → Risk-Score += 3, (3) Keyword 'fundament' → Risk-Score += 2. Total = 9 → ABSTAIN.",
                "DDGK": "ABSTAIN bedeutet: Das System darf NICHT autonom entscheiden. GUARDIAN muss HITL-Freigabe anfordern. Welche Rolle? Bei Notstromaggregat: Statiker (Fundament) + Bauleitung (Brandschutz).",
                "GUARDIAN": "Ich erstelle 2 Approval-Requests: (1) Statiker für Fundament-Prüfung, (2) Bauleitung für Brandschutz. Jede Freigabe bekommt HMAC-SHA256-Signatur. Erst wenn BEIDE freigegeben → Status = approved.",
                "EIRA": "Parallel extrahiere ich die Mass-Ketten: Fundament-Abmessungen, Notstromaggregat-Gewicht, Abstandsflächen. Diese Daten gehen in die Normen-Verknüpfung.",
            },
        },
        {
            "runde": 3,
            "thema": "Normen-Verknüpfung: Was muss der Ziviltechniker prüfen?",
            "beitraege": {
                "ELSA": "Für Notstromaggregat verknüpfe ich 7 Normen: OIB-RL 2 (Brandschutz), EN 40 (Elektro), EN 1992 (Fundament), EN 1997 (Geotechnik), DIN 18531 (Dach), OIB-RL 3 (Hygiene), OIB-RL 5 (Schall).",
                "ORION": "Der Ziviltechniker sieht im Dashboard: (1) ABSTAIN-Status mit Begründung, (2) Liste der 7 betroffenen Normen, (3) Konkrete Prüfungen pro Norm, (4) HITL-Freigabe-Status.",
                "DDGK": "Wichtig: Die Normen-Verknüpfung ist NICHT statisch. Wenn der Plan sich ändert (Revision), wird die Kette neu berechnet. Decision over Time: Jede Revision bekommt eigenen Audit-Hash.",
                "FPGA": "Jede Normen-Prüfung wird durch meinen Lockstep-Comparator validiert: Gleiche Eingabe → gleiches Ergebnis. Keine stochastischen Elemente. Das ist der Unterschied zu LLM-basierten Systemen.",
            },
        },
        {
            "runde": 4,
            "thema": "Unsicherheits-Handling: Was wenn der Plan unvollständig ist?",
            "beitraege": {
                "ELSA": "Wenn Mass-Ketten fehlen (z.B. keine Höhenangaben), erhöhe ich den Risk-Score um +2. Wenn Revision erkannt wird, +1. Wenn kritische Elemente ohne Kontext, +3. ABSTAIN bei >= 8.",
                "GUARDIAN": "Bei ABSTAIN blockiere ich jede autonome Aktion. Der Ziviltechniker MUSS manuell prüfen. Ich protokolliere: (1) Was fehlt, (2) Welche Normen betroffen, (3) Wer freigeben muss.",
                "DDGK": "Das ist der Kern von 'Decision over Time': Das System wartet. Es trifft KEINE Entscheidung bei Unsicherheit. ABSTAIN ist ein VALIDER Zustand. Besser ABSTAIN als falsche Sicherheit.",
                "EIRA": "Ich liefere trotzdem alle extrahierbaren Daten: Mass-Ketten die vorhanden sind, Normen die erkennbar sind, BOM die generierbar ist. Der Ziviltechniker sieht: 'Das habe ich gefunden, das fehlt.'",
            },
        },
        {
            "runde": 5,
            "thema": "FPGA-Integration: Warum Hardware für Bauplan-Validierung?",
            "beitraege": {
                "FPGA": "Drei Gründe: (1) Determinismus: SHA256-Hash jedes Plans ist auf FPGA identisch reproduzierbar. (2) Geschwindigkeit: Mass-Ketten-Extraktion in Hardware parallelisiert. (3) Audit: Jeder Schritt hat Hardware-Hash.",
                "ORION": "Die FastAPI kann FPGA-Targets über EIRA_RUNTIME/fpga_targets/ ansprechen. SHA256-Prüfung, Lockstep-Comparator, AXI4-Lite Interface sind implementiert.",
                "DDGK": "FPGA gibt uns den formale Korrektheitsbeweis: Wenn der Lockstep-Comparator 'gleich' sagt, ist es mathematisch bewiesen. Keine probabilistische Schätzung.",
                "ELSA": "Meine Risk-Score-Berechnung wird durch FPGA-SHA256 gegen Manipulation geschützt. Jeder Audit-Hash ist kryptografisch verifizierbar.",
            },
        },
        {
            "runde": 6,
            "thema": "Best Practice für Ziviltechniker: Wie soll das System genutzt werden?",
            "beitraege": {
                "ORION": "Workflow: (1) PDF hochladen → /api/v1/elsa/validate, (2) Ergebnis prüfen → EXECUTE/DEFER/ABSTAIN, (3) Bei DEFER/ABSTAIN: Normen-Verknüpfung prüfen → /api/v1/normen-verknuepfung/detect, (4) HITL-Freigabe → /api/v1/hitl/approve, (5) Dashboard zeigt Status.",
                "ELSA": "Best Practice: IMMER zuerst ELSA-Validierung laufen lassen. Das System zeigt sofort: Welche kritischen Elemente? Welcher Risk-Score? Welche Normen? Das spart dem Ziviltechniker Stunden manueller Prüfung.",
                "GUARDIAN": "Bei DEFER: Eine Rolle freigeben genügt. Bei ABSTAIN: ALLE betroffenen Rollen müssen freigeben. Das ist kein Bug, sondern Feature: Höhere Unsicherheit → mehr Augen drauf.",
                "DDGK": "Governance-Regel: Keine Baufreigabe ohne ELSA-Validierung. Keine ELSA-Freigabe ohne HITL bei DEFER/ABSTAIN. Keine HITL-Freigabe ohne HMAC-Signatur. Kette ist ununterbrechbar.",
                "EIRA": "Edge-First: Alles läuft lokal. Keine Cloud, keine externen APIs. Der Ziviltechniker hat volle Kontrolle über seine Daten. FPGA-Targets können lokal synthetisiert werden.",
                "FPGA": "Für Produktion: EIRA-FPGA-Targets auf Xilinx Kria KV260 deployen. SHA256-Prüfung + Lockstep-Comparator + AXI4-Lite Interface sind ready. Deterministische Validierung in Hardware.",
            },
        },
    ],
    "zusammenfassung": {
        "kern_ergebnis": "Das System validiert Baupläne deterministisch mit EXECUTE/DEFER/ABSTAIN. Bei Unsicherheit (ABSTAIN) wird automatisch HITL-Freigabe angefordert. Normen-Verknüpfung zeigt dem Ziviltechniker GENAU was zu prüfen ist.",
        "decision_over_time": "ABSTAIN ist valider Zustand. System wartet auf menschliche Freigabe. Keine autonome Aktion bei HIGH-Risk. Audit-Kette dokumentiert jeden Schritt.",
        "fpga_benefit": "SHA256-Hash + Lockstep-Comparator garantieren Reproduzierbarkeit. Jede Validierung ist kryptografisch verifizierbar. Keine stochastischen Elemente.",
        "best_practice": "1. PDF hochladen → 2. ELSA-Validierung → 3. Normen-Verknüpfung prüfen → 4. HITL-Freigabe bei DEFER/ABSTAIN → 5. Dashboard Status prüfen → 6. Baufreigabe erteilen",
        "naechste_schritte": [
            "Runtime-Demo mit echtem PDF-Bauplan durchführen",
            "FPGA-Deployment auf Kria KV260 testen",
            "HITL-Freigabe-Workflow mit 3 Rollen validieren",
            "Dashboard für Ziviltechniker fertigstellen",
        ],
    },
}

# ============================================================
# OUTPUT
# ============================================================

if __name__ == "__main__":
    print("=" * 80)
    print("  DDGK RUNTIME-DEMO DISKUSSION")
    print("  Vollständiges System für Ziviltechniker-Use-Case")
    print(f"  Datum: {DISKUSSION['datum']}")
    print("=" * 80)
    print()

    print("TEILNEHMER:")
    for name, info in AGENTS.items():
        print(f"  {name:10s} | {info['rolle']:35s} | {info['perspektive']}")
    print()

    print("USE-CASE:")
    for k, v in USE_CASE.items():
        print(f"  {k:15s}: {v}")
    print()

    for runde in DISKUSSION["runden"]:
        print("-" * 80)
        print(f"  RUNDE {runde['runde']}: {runde['thema']}")
        print("-" * 80)
        for agent, beitrag in runde["beitraege"].items():
            print(f"\n  [{agent}]:")
            print(f"  {beitrag}")
        print()

    print("=" * 80)
    print("  ZUSAMMENFASSUNG")
    print("=" * 80)
    for k, v in DISKUSSION["zusammenfassung"].items():
        if isinstance(v, list):
            print(f"\n  {k}:")
            for item in v:
                print(f"    → {item}")
        else:
            print(f"\n  {k}:")
            print(f"    {v}")
    print()

    # Save to file
    with open("Baumeister-Tool-Austria/docs/DDGK_RUNTIME_DEMO_DISKUSSION_2026-05-20.json", "w") as f:
        json.dump(DISKUSSION, f, indent=2, ensure_ascii=False)
    print("  [OK] Diskussion gespeichert: docs/DDGK_RUNTIME_DEMO_DISKUSSION_2026-05-20.json")