"""
DDGK-ELSA GESAMT-DISKUSSION: Epistemische Runtime fuer Bauprojekte
Datum: 2026-05-19
Agenten: DDGK, ORION, EIRA, GUARDIAN, NEXUS, ELSA

Thema: Was muss getan werden um Baumeister-Tool-Austria zu einem
vollstaendigen ELSA OS zu machen?
"""

import json
import sys
import os
from datetime import datetime

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def run_discussion():
    print("="*70)
    print("  DDGK-ELSA GESAMT-DISKUSSION")
    print(f"  Datum: {datetime.now().isoformat()}")
    print("="*70)

    # DDGK: Governance und Architektur
    print("\n[DDGK] Governance und Architektur")
    print("-"*50)
    ddgk = {
        "position": "ELSA ist kein BIM-Tool. ELSA ist die Validierungsschicht.",
        "architecture": {
            "layer_1": "Connector Layer (BIM, AVA, Sensorik, Zeit, Audit, Normen)",
            "layer_2": "EIRA Runtime (Epistemic States, Deterministic Executor)",
            "layer_3": "DDGK Governance (Policy Engine, Compliance, HITL)",
            "layer_4": "ELSA Temporal Kernel (Decision over Time)"
        },
        "current_status": "Layer 2+3 existieren (10 Dateien). Layer 1 fehlt.",
        "decision": "Connector Layer ist naechster Schritt."
    }
    for k, v in ddgk.items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for kk, vv in v.items():
                print(f"    {kk}: {vv}")
        else:
            print(f"  {k}: {v}")

    # ORION: Systemintegration
    print("\n[ORION] Systemintegration")
    print("-"*50)
    orion = {
        "position": "6 Connector-Layer sind notwendig fuer reale Funktion",
        "connectors": {
            "BIM": {"formats": ["IFC", "RVT", "BCF", "DWG"], "libs": ["ifcopenshell", "ezdxf", "pymupdf"]},
            "AVA": {"formats": ["OENORM-A2063-XML", "GAEB", "ONLV"], "libs": ["lxml", "csv"]},
            "Zeit": {"formats": ["MSP", "XER", "ICS", "JSON"], "libs": ["icalendar", "json"]},
            "Sensorik": {"protocols": ["MQTT", "OPC-UA", "ROS2", "Modbus"], "hw": ["Kria", "Pi5", "Note10"]},
            "Audit": {"formats": ["PDF", "E-Mail", "Protokoll"], "libs": ["pymupdf", "imaplib"]},
            "Normen": {"sources": ["OIB", "BauKG", "OENORM"], "status": "teilweise oeffentlich"}
        },
        "installed": ["pymupdf", "ezdxf"],
        "missing": ["ifcopenshell", "lxml", "paho-mqtt", "opcua"]
    }
    print(f"  Position: {orion['position']}")
    print(f"  Installiert: {orion['installed']}")
    print(f"  Fehlend: {orion['missing']}")

    # EIRA: Deterministische Validierung
    print("\n[EIRA] Deterministische Validierung")
    print("-"*50)
    eira = {
        "position": "PDF/DWG Plaene erkennen = Computer Vision + Parsing",
        "pdf_analysis": {
            "text_extraction": "PyMuPDF -> Text -> Mustererkennung",
            "image_extraction": "PyMuPDF -> Pixmaps -> Preview-Bilder",
            "dimension_detection": "Regex -> Masse erkennen (z.B. 5.00 x 3.50)",
            "plan_type_detection": "Keywords -> SCHNITT/ANSICHT/GRUNDRISS"
        },
        "epistemic_states": {
            "VERIFIED": "Alle Dimensionen konsistent, Text lesbar",
            "ABSTAIN": "Nur Bilder, kein Text, keine Masse erkennbar",
            "UNKNOWN": "Datei beschaeedigt oder kein PDF",
            "TRANSITION": "Text teilweise lesbar, OCR noetig"
        },
        "deterministic_guarantee": "Gleicher Input -> Gleicher Output (immer)"
    }
    print(f"  Position: {eira['position']}")
    print(f"  States: {list(eira['epistemic_states'].keys())}")
    print(f"  Garantie: {eira['deterministic_guarantee']}")

    # GUARDIAN: Safety und Risiko
    print("\n[GUARDIAN] Safety und Risiko")
    print("-"*50)
    guardian = {
        "position": "Standalone ohne Normen-Datenbank = ABSTAIN",
        "normen_status": {
            "OENORM": "Urheberrechtlich geschuetzt (Beuth-Verlag, EUR 200/Stueck)",
            "OIB": "Teilweise oeffentlich (Richtlinien)",
            "BauKG": "Gesetz (vollstaendig oeffentlich)",
            "Eurocode": "DIN EN (lizenziert, aber Grundformeln frei)"
        },
        "loesung": "Nur Referenz-IDs speichern, nicht volle Norm-Texte",
        "safety_rules": [
            "Kritische Berechnungen -> HITL Pflicht",
            "ABSTAIN bei fehlenden Daten",
            "Audit Chain nicht manipulierbar",
            "Keine autonomen Ausfuehrungen ohne Verifikation"
        ]
    }
    print(f"  Position: {guardian['position']}")
    print(f"  Loesung: {guardian['loesung']}")

    # NEXUS: Datenquellen
    print("\n[NEXUS] Datenquellen")
    print("-"*50)
    nexus = {
        "position": "Woher kommen die Informationen?",
        "sources": [
            {"name": "IFC Dateien", "format": ".ifc", "access": "Open Source (ifcopenshell)"},
            {"name": "PDF Plaene", "format": ".pdf", "access": "PyMuPDF + OCR"},
            {"name": "DWG Plaene", "format": ".dwg", "access": "ezdxf (eingeschraenkt)"},
            {"name": "OENORM A2063", "format": ".xml", "access": "Lizenziert"},
            {"name": "OIB Richtlinien", "format": "Web", "access": "Oeffentlich"},
            {"name": "BauKG", "format": "Gesetz", "access": "Oeffentlich"}
        ],
        "pdf_files_expected": [
            "09f CARPORT.pdf",
            "10d BBQ LOUNGE.pdf",
            "11aa EG Gesamtplan 100.pdf",
            "06u SCHNITTE CC, DD.pdf",
            "08r ANSICHTEN SUED+WEST.pdf",
            "07r ANSICHTEN NORD+OST.pdf"
        ]
    }
    print(f"  Position: {nexus['position']}")
    for s in nexus['sources']:
        print(f"  {s['name']}: {s['format']} -> {s['access']}")

    # ELSA: Epistemischer Kernel
    print("\n[ELSA] Epistemischer Kernel")
    print("-"*50)
    elsa = {
        "position": "ELSA ist keine klassische BIM-Software",
        "difference": {
            "klassisch": "Plan freigegeben -> EXECUTE",
            "elsa": "5 Dimensionen pruefen -> ABSTAIN wenn eine instabil"
        },
        "validation_dimensions": [
            "BIM-Konsistenz (Kollisionen? Attribute vollstaendig?)",
            "Zeitstabilitaet (Deadlines realistisch? Drift erkannt?)",
            "Sensor-Evidenz (Baustelle matcht Plan?)",
            "Audit-Kette (Freigaben dokumentiert? SHA-256 valide?)",
            "Normen-Compliance (OIB/OENORM erfuellt?)"
        ],
        "runtime_states": ["EXECUTE", "ABSTAIN", "DEFER", "REQUIRE_MORE_EVIDENCE"],
        "core_principle": "Unsichere Entscheidungen vor realer Ausfuehrung verhindern"
    }
    print(f"  Position: {elsa['position']}")
    print(f"  States: {elsa['runtime_states']}")
    print(f"  Prinzip: {elsa['core_principle']}")

    # ZUSAMMENFASSUNG UND NAECHESTE SCHRITTE
    print("\n" + "="*70)
    print("  ZUSAMMENFASSUNG: 3-PHASEN PLAN")
    print("="*70)

    phases = {
        "Phase 1 - PDF/IFC Parser (Sofort)": {
            "tasks": [
                "PyMuPDF + ezdxf installiert [OK]",
                "ifcopenshell installieren",
                "PDF-Plaene analysieren (Text, Masse, Typ)",
                "Erster EIRA State: VERIFIED/ABSTAIN/UNKNOWN"
            ]
        },
        "Phase 2 - Connector Layer (2-4 Wochen)": {
            "tasks": [
                "BIM Connector (IFC Parser)",
                "AVA Connector (OENORM XML)",
                "Temporal Runtime (Kalender/Deadlines)",
                "API Layer (FastAPI)"
            ]
        },
        "Phase 3 - Full Runtime (2-3 Monate)": {
            "tasks": [
                "Sensorik-Anbindung (Kria/Pi5)",
                "Audit Chain mit HITL",
                "EU AI Act Compliance vollstaendig",
                "Mobile Baustellenruntime"
            ]
        }
    }

    for phase, details in phases.items():
        print(f"\n  {phase}")
        for task in details['tasks']:
            status = "[OK]" if "[OK]" in task else "[ ]"
            print(f"    {status} {task.replace(' [OK]', '')}")

    print("\n" + "="*70)
    print("  DISKUSSION ABGESCHLOSSEN")
    print("="*70)

    return {
        "discussion": "DDGK-ELSA Gesamt",
        "date": datetime.now().isoformat(),
        "agents": ["DDGK", "ORION", "EIRA", "GUARDIAN", "NEXUS", "ELSA"],
        "phases": list(phases.keys()),
        "conclusion": "Connector Layer ist naechster Schritt. PDF-Analyse lauft."
    }


if __name__ == "__main__":
    result = run_discussion()
    print(f"\nErgebnis: {json.dumps(result, indent=2, ensure_ascii=False)}")