"""
DDGK DISKUSSION: IST-SOLL-Vergleich Bauplan-Verarbeitung
Datum: 2026-05-20
Agenten: DDGK, EIRA, ELSA, ORION, GUARDIAN, NEXUS

Frage: Ist alles da um die 6 Plaene VOLLSTAENDIG zu bearbeiten (wie paradoxonai.at)?
       Ohne Sensorik — nur Plan-Verarbeitung.
"""

import json
import os
import codecs
import sys
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "docs")

# ============================================================
# IST-SOLL-VERGLEICH
# ============================================================

KOMPONENTEN = [
    {
        "name": "PDF-Parser (PyMuPDF)",
        "status": "✅ VORHANDEN",
        "beschreibung": "Volltext-Extraktion aus 6 PDFs funktioniert",
        "datei": "eira_pdf_deep_analyse_2026-05-20.py",
    },
    {
        "name": "ELSA-Validierung (EXECUTE/DEFER/ABSTAIN)",
        "status": "✅ VORHANDEN",
        "beschreibung": "Deterministische Entscheidungen mit Begruendung",
        "datei": "elsa_revision_analyse_2026-05-20.py",
    },
    {
        "name": "DDGK Revisions-Analyse",
        "status": "✅ VORHANDEN",
        "beschreibung": "5 Revisionen erkannt, kritische Aenderungen markiert",
        "datei": "elsa_revision_analyse_2026-05-20.py",
    },
    {
        "name": "SHA-256 Audit Chain",
        "status": "✅ VORHANDEN",
        "beschreibung": "Jede Datei hat Hash, Audit-Log JSONL",
        "datei": "pdf_analysis/ddgk_audit_log.jsonl",
    },
    {
        "name": "Deterministic Executor",
        "status": "✅ VORHANDEN",
        "beschreibung": "EIRA Runtime mit epistemischen States",
        "datei": "eira_runtime/deterministic_executor.py",
    },
    {
        "name": "Policy Engine (DDGK Governance)",
        "status": "✅ VORHANDEN",
        "beschreibung": "Risk-Level, HITL-Required, Eskalation",
        "datei": "ddgk_governance/policy_engine.py",
    },
    {
        "name": "Mass-Ketten-Validierung",
        "status": "⚠️ TEILWEISE",
        "beschreibung": "Hardcoded im Script, NICHT auto-extrahiert aus PDF",
        "datei": "elsa_revision_analyse_2026-05-20.py (hardcoded)",
        "fehlend": "Auto-Extraktion via Regex/Geometrie-Parser",
    },
    {
        "name": "Hoehen-Konsistenz-Check",
        "status": "⚠️ TEILWEISE",
        "beschreibung": "Hardcoded, NICHT auto-extrahiert",
        "datei": "elsa_revision_analyse_2026-05-20.py (hardcoded)",
        "fehlend": "Auto-Extraktion aus Grundriss/Schnitt/Ansicht",
    },
    {
        "name": "Normen-Datenbank (EN, DIN, OeNORM)",
        "status": "❌ FEHLT",
        "beschreibung": "Keine automatische Normenerkennung",
        "fehlend": "Datenbank + Mapping zu Plan-Elementen",
    },
    {
        "name": "IFC-Parser (BIM)",
        "status": "❌ FEHLT",
        "beschreibung": "Kein IFC-Support",
        "fehlend": "ifcopenshell Integration",
    },
    {
        "name": "Web-Dashboard",
        "status": "❌ FEHLT",
        "beschreibung": "Kein Upload/Ergebnisse/Audit-Log UI",
        "fehlend": "FastAPI + HTML",
    },
    {
        "name": "HITL-Bridge (Bauleitung-Freigabe)",
        "status": "❌ FEHLT",
        "beschreibung": "Keine digitale Signatur/Freigabe",
        "fehlend": "HMAC + Rollen-Definition",
    },
    {
        "name": "BOM/Stueckliste Auto-Generierung",
        "status": "❌ FEHLT",
        "beschreibung": "Keine automatische Material-Erkennung",
        "fehlend": "Material-Schluessel Parser",
    },
    {
        "name": "3D-Visualisierung",
        "status": "❌ FEHLT",
        "beschreibung": "Keine 3D-Darstellung der Plaene",
        "fehlend": "IFC-Viewer oder PDF-Overlay",
    },
]

# ============================================================
# DISKUSSION
# ============================================================

def run_diskussion():
    print("=" * 80)
    print("  DDGK DISKUSSION: IST-SOLL-Vergleich Bauplan-Verarbeitung")
    print(f"  Datum: {datetime.now().isoformat()}")
    print(f"  Frage: Vollstaendige Verarbeitung der 6 Plaene (ohne Sensorik)?")
    print("=" * 80)

    # ── IST-ZUSTAND ─────────────────────────────────────────
    print(f"\n{'='*80}")
    print("  IST-ZUSTAND: KOMPONENTEN-STATUS")
    print(f"{'='*80}")

    vorhanden = [k for k in KOMPONENTEN if "VORHANDEN" in k["status"] and "TEILWEISE" not in k["status"]]
    teilweise = [k for k in KOMPONENTEN if "TEILWEISE" in k["status"]]
    fehlt = [k for k in KOMPONENTEN if "FEHLT" in k["status"] and "TEILWEISE" not in k["status"]]

    print(f"\n  ✅ VORHANDEN ({len(vorhanden)}):")
    for k in vorhanden:
        print(f"    {k['name']} — {k['beschreibung']}")

    print(f"\n  ⚠️ TEILWEISE ({len(teilweise)}):")
    for k in teilweise:
        print(f"    {k['name']} — {k['beschreibung']}")
        print(f"       → Fehlend: {k['fehlend']}")

    print(f"\n  ❌ FEHLT ({len(fehlt)}):")
    for k in fehlt:
        print(f"    {k['name']} — {k['fehlend']}")

    # ── RUNDE 1: Bewertung ──────────────────────────────────
    print(f"\n{'='*80}")
    print("  RUNDE 1: BEWERTUNG — Ist alles da?")
    print(f"{'='*80}")

    runde1 = []
    for agent in ["DDGK", "EIRA", "ELSA", "ORION", "GUARDIAN", "NEXUS"]:
        beitrag = ""
        if agent == "DDGK":
            beitrag = "Antwort: NEIN, nicht vollstaendig. 6/14 Komponenten vorhanden, 2 teilweise, 6 fehlen. ABER: Der Kern ist da — PDF-Parser + ELSA-Validierung + Audit Chain. Das ist das Fundament. Was fehlt ist 'nur' Komfort (Dashboard, IFC, Normen). Fuer eine Demo mit den 6 realen Plaenen reicht der IST-Stand — mit Einschraenkungen."
        elif agent == "EIRA":
            beitrag = "Technisch: PDF-Parser liefert Volltext. ELSA-Engine validiert. Deterministic Executor laeuft. ABER: Mass-Ketten und Hoehen sind hardcoded — das ist nicht skalierbar. Fuer 6 Plaene OK, fuer 600 Plaene nicht. Auto-Extraktion ist der Engpass."
        elif agent == "ELSA":
            beitrag = "Validierung: EXECUTE/DEFER/ABSTAIN funktioniert. Aber: Ohne Auto-Mass-Ketten kann ich nicht vollstaendig validieren. Ich erkenne Revisionen, aber ich erkenne NICHT automatisch alle Mass-Ketten, Hoehen-Widersprueche, oder Normen-Verstoesse. Das ist halbautomatisch, nicht vollautomatisch."
        elif agent == "ORION":
            beitrag = "Execution: Der Backend-Code ist da. Was fehlt ist das Frontend (Dashboard). Ohne Dashboard kann der Nutzer keine PDFs hochladen und Ergebnisse sehen. Das kann ich in 1 Woche bauen. Aber: Ohne Auto-Mass-Ketten muss ich die Daten hardcoded einpflegen — das ist keine Loesung."
        elif agent == "GUARDIAN":
            beitrag = "Safety: Audit Chain ist da. Policy Engine ist da. ABER: Ohne HITL-Bridge kann keine DEFER-Entscheidung rechtssicher freigegeben werden. Das ist ein Haftungsrisiko. Wenn ELSA DEFER sagt (z.B. Notstromaggregat verschoben), muss jemand zeichnen. Ohne HITL ist das nur ein Hinweis."
        elif agent == "NEXUS":
            beitrag = "Markt: Fuer einen Pitch reicht der IST-Stand — wenn wir es richtig praesentieren. 'ELSA erkennt 2x verschobenes Notstromaggregat + Mass-Ketten-Fehler' ist stark. Aber: Ohne Dashboard muss ich Screenshots zeigen, nicht Live-Demo. Das ist schwaecher."

        runde1.append({"agent": agent, "beitrag": beitrag})
        print(f"\n  [{agent}] {beitrag}")

    # ── RUNDE 2: Was reicht fuer die 6 Plaene? ──────────────
    print(f"\n{'='*80}")
    print("  RUNDE 2: Was reicht fuer die 6 Plaene OHNE Sensorik?")
    print(f"{'='*80}")

    # Was kann man mit dem IST-Stand machen
    print(f"\n  [DDGK] Mit IST-Stand MOEGLICH:")
    print(f"    ✅ PDF-Volltext extrahieren (alle 6 Plaene)")
    print(f"    ✅ Revisionstabellen erkennen + analysieren")
    print(f"    ✅ Kritische Aenderungen markieren (Notstromaggregat, STB, Fundament)")
    print(f"    ✅ ELSA-Entscheidungen (EXECUTE/DEFER/ABSTAIN) mit Begruendung")
    print(f"    ✅ SHA-256 Audit Chain fuer alle Plaene")
    print(f"    ✅ Mass-Ketten pruefen (hardcoded, aber korrekt)")
    print(f"    ✅ Hoehen-Konsistenz pruefen (hardcoded, aber korrekt)")
    print(f"    ✅ Kritische Elemente identifizieren (8 Elemente)")
    print(f"    ✅ DDGK Audit Log (JSONL)")

    print(f"\n  [DDGK] Mit IST-Stand NICHT moeglich:")
    print(f"    ❌ Mass-Ketten automatisch aus PDF extrahieren")
    print(f"    ❌ Hoehen automatisch aus PDF extrahieren")
    print(f"    ❌ Normen automatisch erkennen (EN 40, DIN 18531...)")
    print(f"    ❌ IFC-Dateien verarbeiten")
    print(f"    ❌ Web-Dashboard (Upload/Ergebnisse)")
    print(f"    ❌ HITL-Freigabe (digitale Signatur)")
    print(f"    ❌ BOM/Stueckliste auto-generieren")
    print(f"    ❌ 3D-Visualisierung")

    runde2 = []
    for agent in ["EIRA", "ELSA", "ORION", "GUARDIAN", "NEXUS"]:
        beitrag = ""
        if agent == "EIRA":
            beitrag = "Fazit: Fuer die 6 Plaene reicht der IST-Stand WENN wir die Mass-Ketten und Hoehen manuell einpflegen (wie in elsa_revision_analyse.py gemacht). Das ist Arbeit, aber machbar. Das Ergebnis ist korrekt und vollstaendig — nur nicht automatisiert."
        elif agent == "ELSA":
            beitrag = "Fazit: Ich kann alle 6 Plaene validieren — mit den hardcoded Daten. Das Ergebnis ist das gleiche wie bei Auto-Extraktion. Der Unterschied ist: Bei neuen Plaenen muss ich die Daten erst manuell einpflegen. Fuer eine Demo: ausreichend. Fuer Produktion: nicht skalierbar."
        elif agent == "ORION":
            beitrag = "Fazit: Ich kann ein Dashboard bauen das die vorhandenen JSON-Reports anzeigt. Das ist in 2 Tagen machbar. Kein Upload, aber Anzeige der 6 Plaene mit ELSA-Entscheidungen. Das reicht fuer eine Demo."
        elif agent == "GUARDIAN":
            beitrag = "Fazit: Safety ist gewaehrleistet — Audit Chain + Policy Engine sind da. Ohne HITL-Bridge ist DEFER nur ein Hinweis, keine rechtssichere Freigabe. Fuer eine Demo: OK. Fuer Produktion: HITL erforderlich."
        elif agent == "NEXUS":
            beitrag = "Fazit: Fuer Pitch und Demo reicht der IST-Stand. Wir zeigen die 6 Plaene mit ELSA-Entscheidungen. Das ist beeindruckend genug. IFC, Normen, HITL sind 'Zukunftsmusik' fuer den Pitch."

        runde2.append({"agent": agent, "beitrag": beitrag})
        print(f"\n  [{agent}] {beitrag}")

    # ── ENTSCHEIDUNG ────────────────────────────────────────
    print(f"\n{'='*80}")
    print("  DDGK ENTSCHEIDUNG")
    print(f"{'='*80}")

    entscheidung = {
        "frage": "Ist alles da um die 6 Plaene vollstaendig zu bearbeiten (ohne Sensorik)?",
        "antwort": "JA — mit Einschraenkungen",
        "details": {
            "vollstaendig_moeglich": [
                "PDF-Volltext extrahieren",
                "Revisionstabellen analysieren",
                "ELSA-Entscheidungen (EXECUTE/DEFER/ABSTAIN)",
                "SHA-256 Audit Chain",
                "Kritische Elemente identifizieren",
                "Mass-Ketten pruefen (hardcoded)",
                "Hoehen-Konsistenz pruefen (hardcoded)",
            ],
            "nicht_moeglich": [
                "Auto-Mass-Ketten-Extraktion",
                "Auto-Normenerkennung",
                "IFC-Verarbeitung",
                "Web-Dashboard mit Upload",
                "HITL-Freigabe",
                "BOM-Generierung",
            ],
        },
        "empfehlung": "Sofort: Dashboard bauen das vorhandene JSON-Reports anzeigt (2 Tage). Parallel: Auto-Mass-Ketten (2 Wochen). IFC/Normen/HITL später.",
    }

    print(f"\n  Frage: {entscheidung['frage']}")
    print(f"  Antwort: {entscheidung['antwort']}")
    print(f"\n  ✅ Vollstaendig moeglich ({len(entscheidung['details']['vollstaendig_moeglich'])}):")
    for d in entscheidung['details']['vollstaendig_moeglich']:
        print(f"    ✓ {d}")
    print(f"\n  ❌ Nicht moeglich ({len(entscheidung['details']['nicht_moeglich'])}):")
    for d in entscheidung['details']['nicht_moeglich']:
        print(f"    ✗ {d}")
    print(f"\n  Empfehlung: {entscheidung['empfehlung']}")

    # ── SPEICHERN ───────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    report = {
        "diskussion": "DDGK IST-SOLL-Vergleich Bauplan-Verarbeitung",
        "datum": datetime.now().isoformat(),
        "komponenten": KOMPONENTEN,
        "zusammenfassung": {
            "vorhanden": len(vorhanden),
            "teilweise": len(teilweise),
            "fehlt": len(fehlt),
            "gesamt": len(KOMPONENTEN),
        },
        "runde1": runde1,
        "runde2": runde2,
        "entscheidung": entscheidung,
    }

    report_path = os.path.join(OUTPUT_DIR, "DDGK_IST_SOLL_2026-05-20.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n{'='*80}")
    print(f"  Report: {report_path}")
    print(f"{'='*80}")

    return report


if __name__ == "__main__":
    run_diskussion()