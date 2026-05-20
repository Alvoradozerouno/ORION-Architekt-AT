"""
DDGK DISKUSSION: Naechste Schritte Baumeister-Tool-Austria
Datum: 2026-05-20
Agenten: DDGK (Moderation), EIRA, ELSA, ORION, GUARDIAN, NEXUS

Thema: Web-Dashboard, IFC-Parser, HITL-Bridge, Pilot-Projekt
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
# AGENTEN-PROFILEN
# ============================================================

AGENTEN = {
    "DDGK": {
        "rolle": "Governance + Strategie + Moderation",
        "fokus": "Roadmap, Priorisierung, Foerderung, IP",
        "mantra": "Inception: 10 Schritte voraus denken.",
    },
    "EIRA": {
        "rolle": "Runtime + Edge + FPGA",
        "fokus": "Deterministische Ausfuehrung, Latenz, Hardware",
        "mantra": "Decision over Time. ABSTAIN ist valider Output.",
    },
    "ELSA": {
        "rolle": "Epistemic Building Validation",
        "fokus": "Plan-Validierung, EXECUTE/DEFER/ABSTAIN, Normen",
        "mantra": "Kein Output ohne Validierung.",
    },
    "ORION": {
        "rolle": "Full-Stack Executor + Integration",
        "fokus": "Web-Dashboard, API, Deployment, CI/CD",
        "mantra": "Execute over speculation.",
    },
    "GUARDIAN": {
        "rolle": "Safety + Compliance + Risiko",
        "fokus": "EU AI Act, Haftung, HITL, Datenschutz",
        "mantra": "Safety first. Human-in-the-Loop immer.",
    },
    "NEXUS": {
        "rolle": "Markt + Outreach + Partnerschaften",
        "fokus": "Pilot-Projekte, Foerderung, Kunden, Pitch",
        "mantra": "Global No One. Paradoxon AI.",
    },
}

# ============================================================
# THEMEN
# ============================================================

THEMEN = [
    {
        "id": "T1",
        "titel": "Web-Dashboard (FastAPI + HTML)",
        "prioritaet": "HOCH",
        "aufwand": "2 Wochen",
        "beschreibung": "Live-Demo mit 6 realen Plaenen. PDF-Upload → ELSA-Validierung → EXECUTE/DEFER/ABSTAIN Dashboard.",
        "agenten_zustaendig": ["ORION", "ELSA"],
        "abhaengigkeiten": ["EIRA PDF-Parser (fertig)", "ELSA Engine (fertig)"],
    },
    {
        "id": "T2",
        "titel": "IFC-Parser (ifcopenshell)",
        "prioritaet": "HOCH",
        "aufwand": "4-8 Wochen",
        "beschreibung": "BIM-IFC-Integration. IFC-Dateien lesen, Geometrie extrahieren, ELSA-Validierung auf IFC-Elemente.",
        "agenten_zustaendig": ["EIRA", "ELSA"],
        "abhaengigkeiten": ["ifcopenshell Installation", "IFC-Schema-Verstaendnis"],
    },
    {
        "id": "T3",
        "titel": "HITL-Bridge (Bauleitung-Freigabe)",
        "prioritaet": "MITTEL",
        "aufwand": "2-4 Wochen",
        "beschreibung": "Biometrische Signatur fuer DEFER-Entscheidungen. Bauleitung bestaetigt Aenderungen digital.",
        "agenten_zustaendig": ["GUARDIAN", "DDGK"],
        "abhaengigkeiten": ["HITL-Secret-Store", "Signatur-Algorithmus"],
    },
    {
        "id": "T4",
        "titel": "Mass-Ketten-Auto-Extraktion",
        "prioritaet": "HOCH",
        "aufwand": "2-3 Wochen",
        "beschreibung": "Mass-Ketten direkt aus PDF extrahieren (nicht hardcoded). Regex + Geometrie-Parser.",
        "agenten_zustaendig": ["EIRA", "ELSA"],
        "abhaengigkeiten": ["PyMuPDF Volltext (fertig)"],
    },
    {
        "id": "T5",
        "titel": "Pilot-Projekt: Golfakademie Grassau",
        "prioritaet": "HOCH",
        "aufwand": "laufend",
        "beschreibung": "6 reale Plaene als Referenz. ELSA-Validierung live zeigen. Matteo Thun Milano als Partner.",
        "agenten_zustaendig": ["NEXUS", "DDGK"],
        "abhaengigkeiten": ["Web-Dashboard (T1)", "Einverstaendnis Bauherr"],
    },
    {
        "id": "T6",
        "titel": "Foerderung: digital.tirol 2026",
        "prioritaet": "MITTEL",
        "aufwand": "4 Wochen",
        "beschreibung": "Foerderantrag fuer ELSA als epistemische Planungssoftware. Innsbruck AI Factory Pilot.",
        "agenten_zustaendig": ["NEXUS", "DDGK"],
        "abhaengigkeiten": ["Pitch-Deck", "Technischer Nachweis (T1)"],
    },
    {
        "id": "T7",
        "titel": "EU AI Act Zertifizierung",
        "prioritaet": "NIEDRIG",
        "aufwand": "3-6 Monate",
        "beschreibung": "ELSA als High-Risk AI System (Bau) zertifizieren. Compliance-Mapping.",
        "agenten_zustaendig": ["GUARDIAN", "DDGK"],
        "abhaengigkeiten": ["EU AI Act Final-Text", "Rechtsberatung"],
    },
]

# ============================================================
# DISKUSSION
# ============================================================

def run_diskussion():
    print("=" * 80)
    print("  DDGK DISKUSSION: Naechste Schritte Baumeister-Tool-Austria")
    print(f"  Datum: {datetime.now().isoformat()}")
    print(f"  Agenten: {', '.join(AGENTEN.keys())}")
    print("=" * 80)

    diskussion = []

    # ── RUNDE 1: Priorisierung ──────────────────────────────
    print(f"\n{'='*80}")
    print("  RUNDE 1: PRIORISIERUNG")
    print(f"{'='*80}")

    runde1 = []
    for agent, profil in AGENTEN.items():
        beitrag = ""
        if agent == "DDGK":
            beitrag = "Priorisierung: T1 (Dashboard) → T4 (Mass-Ketten) → T2 (IFC) → T5 (Pilot). T1 ist der Hebel fuer alles andere. Ohne Dashboard kein Pitch, keine Foerderung, kein Pilot."
        elif agent == "EIRA":
            beitrag = "Technisch: T1 ist sofort machbar — PDF-Parser + ELSA Engine sind fertig. FastAPI + HTML = 1 Woche. T4 (Mass-Ketten) braucht bessere Regex + Geometrie-Logik. T2 (IFC) ist der grosse Sprung — ifcopenshell ist komplex, aber machbar."
        elif agent == "ELSA":
            beitrag = "Validierung: T1 zeigt EXECUTE/DEFER/ABSTAIN live. Das ist der USP. T4 ist kritisch — ohne Auto-Mass-Ketten bleibt ELSA halbautomatisch. T2 (IFC) bringt 3D-Validierung — das ist die naechste Stufe."
        elif agent == "ORION":
            beitrag = "Execution: T1 = FastAPI Backend + HTML Frontend. Ich baue das Dashboard. 1 Endpoint: /validate (PDF upload) → JSON Response mit ELSA-Entscheidungen. Frontend: Tabelle + Farbcodes (gruen/gelb/rot)."
        elif agent == "GUARDIAN":
            beitrag = "Safety: T3 (HITL) ist wichtig fuer Haftung. Wenn ELSA DEFER entscheidet, muss jemand verantwortlich zeichnen. Ohne HITL-Bridge ist ELSA nur ein Tool — mit HITL wird es rechtssicher."
        elif agent == "NEXUS":
            beitrag = "Markt: T5 (Pilot Grassau) ist der Beweis. Matteo Thun Milano hat die Plaene. Wenn wir ELSA live zeigen, haben wir den Referenzfall fuer digital.tirol 2026 und ESA Phi-Lab."

        runde1.append({"agent": agent, "runde": 1, "beitrag": beitrag})
        print(f"\n  [{agent}] {beitrag}")

    # ── RUNDE 2: Abhaengigkeiten + Risiken ──────────────────
    print(f"\n{'='*80}")
    print("  RUNDE 2: ABHAENGIGKEITEN + RISIKEN")
    print(f"{'='*80}")

    runde2 = []
    for agent, profil in AGENTEN.items():
        beitrag = ""
        if agent == "DDGK":
            beitrag = "Risiko: T1 ohne T4 = halbautomatisch. T4 ohne T1 = unsichtbar. Parallel starten: ORION baut T1, EIRA baut T4. Merge nach 2 Wochen."
        elif agent == "EIRA":
            beitrag = "Risiko T2 (IFC): ifcopenshell ist Python-basiert, aber IFC4-Unterstützung ist lückenhaft. Fallback: IFC2x3 zuerst. Edge-Deployment: IFC-Parser braucht mehr RAM als Pi5 hat → Laptop/Cloud für IFC, Pi5 für PDF."
        elif agent == "ELSA":
            beitrag = "Risiko T3 (HITL): Wer zeichnet? Bauleitung? Architekt? Statiker? Wir brauchen eine klare Rollen-Definition. Vorschlag: 3 HITL-Level (Architekt, Statiker, Bauleitung) — jeder muss seine Domäne freigeben."
        elif agent == "ORION":
            beitrag = "Risiko T1: Deployment. Wo läuft das Dashboard? Lokal (Laptop), Cloud (AWS), oder Edge (Pi5)? Vorschlag: Lokal für Demo, Cloud für Pilot, Edge für Baustelle."
        elif agent == "GUARDIAN":
            beitrag = "Risiko T5 (Pilot): Datenschutz. Baupläne sind vertraulich. Wir brauchen eine DSGVO-konforme Lösung. Vorschlag: Lokale Verarbeitung (kein Cloud-Upload), SHA-256 Hashes statt Dateien speichern."
        elif agent == "NEXUS":
            beitrag = "Risiko T6 (Foerderung): digital.tirol 2026 hat Deadline Q3 2026. Wir brauchen bis Juni einen funktionierenden Prototyp (T1) und bis Juli den Foerderantrag."

        runde2.append({"agent": agent, "runde": 2, "beitrag": beitrag})
        print(f"\n  [{agent}] {beitrag}")

    # ── RUNDE 3: Entscheidung + Roadmap ─────────────────────
    print(f"\n{'='*80}")
    print("  RUNDE 3: ENTSCHEIDUNG + ROADMAP")
    print(f"{'='*80}")

    runde3 = []
    for agent, profil in AGENTEN.items():
        beitrag = ""
        if agent == "DDGK":
            beitrag = "ENTSCHEIDUNG: T1 + T4 parallel starten (Woche 1-2). T2 starten (Woche 3-8). T3 parallel zu T1 (Woche 2-4). T5 sobald T1 fertig (Woche 3). T6 parallel zu T5 (Woche 4-8). T7 später (Q4 2026)."
        elif agent == "EIRA":
            beitrag = "Zusage: T4 (Mass-Ketten-Auto) in 2 Wochen. Regex-Engine + Geometrie-Parser. Output: JSON mit allen Mass-Ketten + Konsistenz-Check."
        elif agent == "ELSA":
            beitrag = "Zusage: T1 Dashboard-Integration. ELSA-Engine liefert bereits JSON-Response. Nur FastAPI-Wrapper + HTML-Template nötig."
        elif agent == "ORION":
            beitrag = "Zusage: T1 Dashboard in 1 Woche. FastAPI + HTML. 3 Seiten: Upload, Ergebnisse, Audit-Log."
        elif agent == "GUARDIAN":
            beitrag = "Zusage: T3 HITL-Bridge in 2 Wochen. HMAC-Signatur + Rollen-Definition (Architekt/Statiker/Bauleitung)."
        elif agent == "NEXUS":
            beitrag = "Zusage: T5 Pilot-Koordination. Kontakt zu Matteo Thun Milano + Bauherr. T6 Foerderantrag-Vorbereitung."

        runde3.append({"agent": agent, "runde": 3, "beitrag": beitrag})
        print(f"\n  [{agent}] {beitrag}")

    # ── ROADMAP ─────────────────────────────────────────────
    print(f"\n{'='*80}")
    print("  ROADMAP: WOCHE 1-8")
    print(f"{'='*80}")

    roadmap = [
        {"woche": "1-2", "themen": ["T1: Web-Dashboard (ORION)", "T4: Mass-Ketten-Auto (EIRA)"], "ziel": "Dashboard live + Auto-Mass-Ketten"},
        {"woche": "3", "themen": ["T1+T4 Merge", "T5: Pilot-Kontakt (NEXUS)"], "ziel": "Dashboard mit Auto-Mass-Ketten + Pilot-Gespräch"},
        {"woche": "3-4", "themen": ["T3: HITL-Bridge (GUARDIAN)"], "ziel": "HITL-Freigabe für DEFER-Entscheidungen"},
        {"woche": "3-8", "themen": ["T2: IFC-Parser (EIRA+ELSA)"], "ziel": "IFC2x3-Parser + 3D-Validierung"},
        {"woche": "4-8", "themen": ["T6: Foerderantrag (NEXUS+DDGK)"], "ziel": "digital.tirol 2026 Antrag"},
        {"woche": "Q4 2026", "themen": ["T7: EU AI Act (GUARDIAN+DDGK)"], "ziel": "Zertifizierungsvorbereitung"},
    ]

    for r in roadmap:
        print(f"\n  Woche {r['woche']}:")
        for t in r['themen']:
            print(f"    → {t}")
        print(f"    Ziel: {r['ziel']}")

    # ── SPEZIAL: Agenten-Aufgabenverteilung ─────────────────
    print(f"\n{'='*80}")
    print("  AGENTEN-AUFGABENVERTEILUNG")
    print(f"{'='*80}")

    aufgaben = {
        "ORION": ["T1: FastAPI Backend", "T1: HTML Frontend", "T1: Deployment (lokal + cloud)", "CI/CD Pipeline"],
        "EIRA": ["T4: Mass-Ketten-Auto-Extraktion", "T4: Regex-Engine", "T2: IFC-Parser (ifcopenshell)", "T2: IFC2x3 Schema"],
        "ELSA": ["T1: ELSA-JSON-Response", "T4: Mass-Ketten-Validierung", "T2: 3D-Validierung", "Normen-Datenbank"],
        "GUARDIAN": ["T3: HITL-Bridge", "T3: HMAC-Signatur", "T3: Rollen-Definition", "T7: EU AI Act Mapping"],
        "NEXUS": ["T5: Pilot-Koordination", "T5: Matteo Thun Kontakt", "T6: Foerderantrag", "Pitch-Deck"],
        "DDGK": ["Roadmap-Koordination", "T6: IP-Strategie", "T7: Governance", "Audit-Log"],
    }

    for agent, tasks in aufgaben.items():
        print(f"\n  [{agent}]")
        for t in tasks:
            print(f"    ☐ {t}")

    # ── DDGK ENTSCHEIDUNG ───────────────────────────────────
    print(f"\n{'='*80}")
    print("  DDGK ENTSCHIEDUNG")
    print(f"{'='*80}")

    entscheidung = {
        "status": "BESCHLOSSEN",
        "prioritaet": "T1 + T4 parallel (Woche 1-2)",
        "begruendung": "Dashboard ist der Hebel fuer Pilot, Foerderung, Markt. Mass-Ketten-Auto ist der technische USP.",
        "naechster_schritt": "ORION startet T1 (FastAPI + HTML). EIRA startet T4 (Mass-Ketten-Auto).",
        "review": "Woche 2: Merge T1+T4. Demo mit 6 realen Plaenen.",
    }

    print(f"\n  Status: {entscheidung['status']}")
    print(f"  Prioritaet: {entscheidung['prioritaet']}")
    print(f"  Begruendung: {entscheidung['begruendung']}")
    print(f"  Naechster Schritt: {entscheidung['naechster_schritt']}")
    print(f"  Review: {entscheidung['review']}")

    # ── SPEICHERN ───────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    report = {
        "diskussion": "DDGK Naechste Schritte Baumeister-Tool-Austria",
        "datum": datetime.now().isoformat(),
        "agenten": AGENTEN,
        "themen": THEMEN,
        "runde1": runde1,
        "runde2": runde2,
        "runde3": runde3,
        "roadmap": roadmap,
        "aufgaben": aufgaben,
        "entscheidung": entscheidung,
    }

    report_path = os.path.join(OUTPUT_DIR, "DDGK_NAECHSTE_SCHRITTE_2026-05-20.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n{'='*80}")
    print(f"  Report: {report_path}")
    print(f"{'='*80}")

    return report


if __name__ == "__main__":
    run_diskussion()