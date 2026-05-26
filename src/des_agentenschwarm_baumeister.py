"""
DES AGENTENSCHWARM FÜR BAUMEISTER-TOOL-AUSTRIA
================================================

Integriert das ORION/DDGK Multi-Agent-System aus orion-ros2-consciousness-node
für erweiterte Baumeister-Features:

1. AUTOMATISCHE BAUEINGABE-GENERIERUNG
2. KOSTENPLANUNG AUS DWG-PLÄNEN
3. BIM-INTEGRATION (4D/5D)
4. CLASH DETECTION
5. ÖNORM A2063 AUSSCHREIBUNGEN
6. BAUBEGLEITUNG & MÄNGELVERWALTUNG

Agenten (inspiriert von ORION/DDGK):
- EIRA: Runtime Validator (OIB-Compliance)
- ORION: System Orchestrator (Konsens)
- DDGK: Governance Kernel (Audit)
- GUARDIAN: Safety Auditor (Sicherheit)
- NEXUS: Hardware Bridge (BIM/IFC)
- EPISTEMIC: Wissens-Validierung
- BAUEINGABE: Automatische Generierung
- KOSTEN: Kostenplanung
- BIM: BIM-Integration
- CLASH: Kollisionsprüfung
- OENORM: ÖNORM A2063
- BAUBEGLEITUNG: Mängelverwaltung

Autor: Baumeister Tool Austria Team
Datum: 2026-05-26
"""

import sys
import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ============================================================================
# AGENTEN-DEFINITIONEN
# ============================================================================

@dataclass
class AgentBewertung:
    """Bewertung eines einzelnen Agenten."""
    name: str
    rolle: str
    score: float  # 0-10
    position: str  # APPROVED, REVIEW REQUIRED, REJECTED
    analyse: str
    empfehlung: str
    umsetzbar: bool = True


@dataclass
class SchwarmErgebnis:
    """Gesamtergebnis des Agentenschwarms."""
    timestamp: str
    konsens: str  # GREEN, YELLOW, RED
    durchschnitt_score: float
    produktion_bereit: float  # 0-100
    agenten: List[AgentBewertung]
    features: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# AGENTEN-KLASSEN
# ============================================================================

class BaueingabeAgent:
    """Agent 1: Automatische Baueingabe-Generierung."""

    name = "BAUEINGABE"
    rolle = "Automatische Baueingabe-Generierung"

    @staticmethod
    def pruefe(plan_daten: Dict) -> AgentBewertung:
        fehlende_docs = []
        if not plan_daten.get("lageplan"):
            fehlende_docs.append("Lageplan")
        if not plan_daten.get("grundrisse"):
            fehlende_docs.append("Grundrisse")
        if not plan_daten.get("schnitte"):
            fehlende_docs.append("Schnitte")
        if not plan_daten.get("ansichten"):
            fehlende_docs.append("Ansichten")
        if not plan_daten.get("energieausweis"):
            fehlende_docs.append("Energieausweis")
        if not plan_daten.get("statik"):
            fehlende_docs.append("Statik")

        vollstaendig = len(fehlende_docs) == 0
        score = 10.0 if vollstaendig else max(3.0, 10.0 - len(fehlende_docs) * 1.5)

        return AgentBewertung(
            name=BaueingabeAgent.name,
            rolle=BaueingabeAgent.rolle,
            score=round(score, 1),
            position="APPROVED" if vollstaendig else "FEHLER: " + ", ".join(fehlende_docs),
            analyse=f"Baueingabe-Unterlagen: {len(fehlende_docs)} fehlend",
            empfehlung="Fehlende Dokumente ergänzen" if fehlende_docs else "Baueingabe bereit",
            umsetzbar=vollstaendig
        )


class KostenAgent:
    """Agent 2: Kostenplanung aus DWG-Plänen."""

    name = "KOSTEN"
    rolle = "Kostenplanung aus DWG-Plänen"

    @staticmethod
    def pruefe(plan_daten: Dict) -> AgentBewertung:
        flaeche = plan_daten.get("nutzflaeche", 0)
        geschosse = plan_daten.get("geschosse", 1)
        qualitaet = plan_daten.get("qualitaet", "mittel")

        # Kosten-Schätzung pro m2
        kosten_pro_m2 = {"einfach": 1500, "mittel": 2500, "gehoben": 4000}
        gesamt_kosten = flaeche * geschosse * kosten_pro_m2.get(qualitaet, 2500)

        score = 8.0 if flaeche > 0 else 3.0

        return AgentBewertung(
            name=KostenAgent.name,
            rolle=KostenAgent.rolle,
            score=score,
            position="APPROVED" if flaeche > 0 else "UNVOLLSTAENDIG",
            analyse=f"Kosten: ~€ {gesamt_kosten:,.0f} ({flaeche}m2 x {geschosse} OG x {qualitaet})",
            empfehlung="Massenermittlung aus DWG für präzise Kosten",
            umsetzbar=flaeche > 0
        )


class BimAgent:
    """Agent 3: BIM-Integration (4D/5D)."""

    name = "BIM"
    rolle = "BIM-Integration (4D/5D)"

    @staticmethod
    def pruefe(plan_daten: Dict) -> AgentBewertung:
        ifc_verfuegbar = plan_daten.get("ifc_export", False)
        zeitplan = plan_daten.get("zeitplan", False)
        kosten_5d = plan_daten.get("kosten_5d", False)

        score = 5.0
        if ifc_verfuegbar: score += 2.0
        if zeitplan: score += 1.5
        if kosten_5d: score += 1.5
        score = min(10.0, score)

        return AgentBewertung(
            name=BimAgent.name,
            rolle=BimAgent.rolle,
            score=score,
            position="APPROVED" if score >= 7 else "IN ARBEIT",
            analyse=f"BIM: IFC={'ja' if ifc_verfuegbar else 'nein'}, 4D={'ja' if zeitplan else 'nein'}, 5D={'ja' if kosten_5d else 'nein'}",
            empfehlung="IFC-Export aus DWG aktivieren",
            umsetzbar=True
        )


class ClashAgent:
    """Agent 4: Kollisionsprüfung (Clash Detection)."""

    name = "CLASH"
    rolle = "Kollisionsprüfung (Clash Detection)"

    @staticmethod
    def pruefe(plan_daten: Dict) -> AgentBewertung:
        kollisionen = plan_daten.get("kollisionen", [])
        tragend = [k for k in kollisionen if k.get("typ") == "tragend"]
        installation = [k for k in kollisionen if k.get("typ") == "installation"]

        score = max(3.0, 10.0 - len(kollisionen) * 1.5 - len(tragend) * 2.0)

        return AgentBewertung(
            name=ClashAgent.name,
            rolle=ClashAgent.rolle,
            score=round(score, 1),
            position="APPROVED" if len(kollisionen) == 0 else f"{len(kollisionen)} Kollisionen",
            analyse=f"Kollisionen: {len(kollisionen)} gesamt, {len(tragend)} tragend, {len(installation)} Installation",
            empfehlung="Tragende Kollisionen sofort beheben",
            umsetzbar=len(tragend) == 0
        )


class OenormAgent:
    """Agent 5: ÖNORM A2063 Ausschreibungen."""

    name = "OENORM"
    rolle = "ÖNORM A2063 Ausschreibungen"

    @staticmethod
    def pruefe(plan_daten: Dict) -> AgentBewertung:
        leistungsverzeichnis = plan_daten.get("leistungsverzeichnis", False)
        ausschreibung = plan_daten.get("ausschreibung", False)
        bietervergleich = plan_daten.get("bietervergleich", False)

        score = 5.0
        if leistungsverzeichnis: score += 2.0
        if ausschreibung: score += 1.5
        if bietervergleich: score += 1.5
        score = min(10.0, score)

        return AgentBewertung(
            name=OenormAgent.name,
            rolle=OenormAgent.rolle,
            score=score,
            position="APPROVED" if score >= 7 else "IN ARBEIT",
            analyse=f"ÖNORM: LV={'ja' if leistungsverzeichnis else 'nein'}, Ausschreibung={'ja' if ausschreibung else 'nein'}",
            empfehlung="ÖNORM A2063 konforme Ausschreibung erstellen",
            umsetzbar=True
        )


class BaubegleitungAgent:
    """Agent 6: Baubegleitung & Mängelverwaltung."""

    name = "BAUBEGLEITUNG"
    rolle = "Baubegleitung & Mängelverwaltung"

    @staticmethod
    def pruefe(plan_daten: Dict) -> AgentBewertung:
        maengel = plan_daten.get("maengel", [])
        offen = [m for m in maengel if m.get("status") == "offen"]
        behoben = [m for m in maengel if m.get("status") == "behoben"]

        score = max(3.0, 10.0 - len(offen) * 1.0)

        return AgentBewertung(
            name=BaubegleitungAgent.name,
            rolle=BaubegleitungAgent.rolle,
            score=round(score, 1),
            position="APPROVED" if len(offen) == 0 else f"{len(offen)} offene Mängel",
            analyse=f"Mängel: {len(maengel)} gesamt, {len(offen)} offen, {len(behoben)} behoben",
            empfehlung="Offene Mängel priorisieren",
            umsetzbar=True
        )


# ============================================================================
# ORION/DDGK INSPIRIERTE AGENTEN
# ============================================================================

class EiraAgent:
    """EIRA: Runtime Validator (OIB-Compliance)."""
    name = "EIRA"
    rolle = "Runtime Validator | OIB-Compliance"

    @staticmethod
    def pruefe(plan_daten: Dict) -> AgentBewertung:
        oib_fehler = plan_daten.get("oib_fehler", [])
        score = max(3.0, 10.0 - len(oib_fehler) * 1.2)
        return AgentBewertung(
            name=EiraAgent.name, rolle=EiraAgent.rolle,
            score=round(score, 1),
            position="APPROVED" if len(oib_fehler) == 0 else f"{len(oib_fehler)} OIB-Fehler",
            analyse=f"OIB-Compliance: {len(oib_fehler)} Fehler",
            empfehlung="OIB-Fehler beheben",
            umsetzbar=len(oib_fehler) < 5
        )


class OrionAgent:
    """ORION: System Orchestrator (Konsens)."""
    name = "ORION"
    rolle = "System Orchestrator | Konsens"

    @staticmethod
    def pruefe(plan_daten: Dict) -> AgentBewertung:
        alle_agenten = plan_daten.get("alle_scores", [])
        konsens = sum(alle_agenten) / max(len(alle_agenten), 1)
        return AgentBewertung(
            name=OrionAgent.name, rolle=OrionAgent.rolle,
            score=round(konsens, 1),
            position="APPROVED" if konsens >= 7 else "REVIEW",
            analyse=f"Konsens-Score: {konsens:.1f}/10",
            empfehlung="System bereit" if konsens >= 7 else "Review erforderlich",
            umsetzbar=konsens >= 6
        )


class DdgkAgent:
    """DDGK: Governance Kernel (Audit)."""
    name = "DDGK"
    rolle = "Governance Kernel | Audit"

    @staticmethod
    def pruefe(plan_daten: Dict) -> AgentBewertung:
        audit_kette = plan_daten.get("audit_kette", True)
        return AgentBewertung(
            name=DdgkAgent.name, rolle=DdgkAgent.rolle,
            score=8.0 if audit_kette else 4.0,
            position="APPROVED" if audit_kette else "AUDIT FEHLER",
            analyse=f"Audit-Kette: {'valid' if audit_kette else 'INVALID'}",
            empfehlung="Audit-Kette prüfen",
            umsetzbar=audit_kette
        )


class GuardianAgent:
    """GUARDIAN: Safety Auditor (Sicherheit)."""
    name = "GUARDIAN"
    rolle = "Safety Auditor | Sicherheit"

    @staticmethod
    def pruefe(plan_daten: Dict) -> AgentBewertung:
        sicherheit = plan_daten.get("sicherheit", {})
        fluchtwege = sicherheit.get("fluchtwege", True)
        brandschutz = sicherheit.get("brandschutz", True)
        return AgentBewertung(
            name=GuardianAgent.name, rolle=GuardianAgent.rolle,
            score=10.0 if (fluchtwege and brandschutz) else 5.0,
            position="APPROVED" if (fluchtwege and brandschutz) else "SAFETY REVIEW",
            analyse=f"Sicherheit: Fluchtwege={'OK' if fluchtwege else 'FEHLER'}, Brandschutz={'OK' if brandschutz else 'FEHLER'}",
            empfehlung="Sicherheitsmängel beheben",
            umsetzbar=fluchtwege and brandschutz
        )


class NexusAgent:
    """NEXUS: Hardware Bridge (BIM/IFC)."""
    name = "NEXUS"
    rolle = "Hardware Bridge | BIM/IFC"

    @staticmethod
    def pruefe(plan_daten: Dict) -> AgentBewertung:
        ifc_export = plan_daten.get("ifc_export", False)
        dwg_parser = plan_daten.get("dwg_parser", False)
        return AgentBewertung(
            name=NexusAgent.name, rolle=NexusAgent.rolle,
            score=7.0 if (ifc_export or dwg_parser) else 4.0,
            position="APPROVED" if (ifc_export or dwg_parser) else "HARDWARE REVIEW",
            analyse=f"BIM-Export: IFC={'ja' if ifc_export else 'nein'}, DWG={'ja' if dwg_parser else 'nein'}",
            empfehlung="DWG-Parser aktivieren",
            umsetzbar=True
        )


class EpistemicAgent:
    """EPISTEMIC: Wissens-Validierung."""
    name = "EPISTEMIC"
    rolle = "Wissens-Validierung | Lernen"

    @staticmethod
    def pruefe(plan_daten: Dict) -> AgentBewertung:
        wissen_db = plan_daten.get("wissen_db", 0)
        bestaetigungen = plan_daten.get("bestaetigungen", 0)
        widerlegungen = plan_daten.get("widerlegungen", 0)
        confidence = max(0.3, min(1.0, 0.5 + (bestaetigungen - widerlegungen) * 0.05))
        return AgentBewertung(
            name=EpistemicAgent.name, rolle=EpistemicAgent.rolle,
            score=round(confidence * 10, 1),
            position="APPROVED" if confidence >= 0.7 else "UNCERTAIN",
            analyse=f"Wissen: {wissen_db} Einträge, {bestaetigungen} bestätigt, {widerlegungen} widerlegt",
            empfehlung="Mehr Pläne prüfen für besseres Lernen",
            umsetzbar=True
        )


# ============================================================================
# AGENTENSCHWARM
# ============================================================================

class Agentenschwarm:
    """Der intelligente Agentenschwarm für Baumeister-Tool-Austria."""

    def __init__(self):
        self.agenten = [
            EiraAgent(),
            OrionAgent(),
            DdgkAgent(),
            GuardianAgent(),
            NexusAgent(),
            EpistemicAgent(),
            BaueingabeAgent(),
            KostenAgent(),
            BimAgent(),
            ClashAgent(),
            OenormAgent(),
            BaubegleitungAgent(),
        ]

    def bewerte(self, plan_daten: Dict) -> SchwarmErgebnis:
        """Bewerte einen Plan mit allen Agenten."""
        bewertungen = []
        scores = []

        for agent in self.agenten:
            bewertung = agent.pruefe(plan_daten)
            bewertungen.append(bewertung)
            scores.append(bewertung.score)

        # Konsens berechnen
        avg_score = sum(scores) / len(scores) if scores else 0
        if avg_score >= 8:
            konsens = "GREEN"
        elif avg_score >= 6:
            konsens = "YELLOW"
        else:
            konsens = "RED"

        # Produktions-Reife
        produktion = round(
            (avg_score / 10 * 0.5 +
             sum(1 for b in bewertungen if b.umsetzbar) / len(bewertungen) * 0.3 +
             (1.0 if konsens == "GREEN" else 0.5 if konsens == "YELLOW" else 0.0) * 0.2) * 100, 1
        )

        # Plan-Daten für Features
        plan_daten["alle_scores"] = scores

        return SchwarmErgebnis(
            timestamp=datetime.utcnow().isoformat(),
            konsens=konsens,
            durchschnitt_score=round(avg_score, 2),
            produktion_bereit=produktion,
            agenten=bewertungen,
            features=plan_daten
        )


# ============================================================================
# HAUPTPROGRAMM
# ============================================================================

def main():
    print("=" * 80)
    print("DES AGENTENSCHWARM FÜR BAUMEISTER-TOOL-AUSTRIA")
    print("Inspired by ORION/DDGK Multi-Agent Consensus Layer")
    print("=" * 80)

    # Test-Plan-Daten (Breitbrunn Koenigstr_59)
    test_plan = {
        # OIB-Compliance
        "oib_fehler": [
            "Keller Hoehe 2.4m < 2.50m",
            "Keller Tageslicht 5% < 10%",
            "Flur Tageslicht 5% < 10%",
            "Bad Flaeche 6.5m2 < 10m2",
            "Bad Tageslicht 5% < 10%",
            "Galerie Hoehe 2.3m < 2.50m",
            "Galerie Tageslicht 8% < 10%",
        ],
        # Baueingabe
        "lageplan": True,
        "grundrisse": True,
        "schnitte": True,
        "ansichten": True,
        "energieausweis": True,
        "statik": True,
        # Kosten
        "nutzflaeche": 150,
        "geschosse": 4,
        "qualitaet": "mittel",
        # BIM
        "ifc_export": False,
        "zeitplan": False,
        "kosten_5d": False,
        # Clash
        "kollisionen": [],
        # ÖNORM
        "leistungsverzeichnis": False,
        "ausschreibung": False,
        "bietervergleich": False,
        # Baubegleitung
        "maengel": [],
        # Sicherheit
        "sicherheit": {
            "fluchtwege": True,
            "brandschutz": True,
        },
        # Epistemisch
        "wissen_db": 150,
        "bestaetigungen": 45,
        "widerlegungen": 3,
        # Audit
        "audit_kette": True,
        # Parser
        "dwg_parser": False,
    }

    schwarm = Agentenschwarm()
    ergebnis = schwarm.bewerte(test_plan)

    print(f"\n{'=' * 80}")
    print(f"AGENTENSCHWARM ERGEBNIS")
    print(f"{'=' * 80}")
    print(f"KONSENS:           {ergebnis.konsens}")
    print(f"DURCHSCHNITT:      {ergebnis.durchschnitt_score}/10")
    print(f"PRODUKTION BEREIT: {ergebnis.produktion_bereit}%")
    print(f"TIMESTAMP:         {ergebnis.timestamp}")

    print(f"\n{'=' * 80}")
    print(f"AGENTEN-BEWERTUNGEN")
    print(f"{'=' * 80}")

    for agent in ergebnis.agenten:
        status = "✅" if agent.umsetzbar else "❌"
        print(f"\n  {status} {agent.name}")
        print(f"     Rolle:       {agent.rolle}")
        print(f"     Score:       {agent.score}/10")
        print(f"     Position:    {agent.position}")
        print(f"     Analyse:     {agent.analyse}")
        print(f"     Empfehlung:  {agent.empfehlung}")

    # JSON-Export
    report_path = os.path.join(os.path.dirname(__file__), "..", "agentenschwarm_report.json")
    export = {
        "timestamp": ergebnis.timestamp,
        "konsens": ergebnis.konsens,
        "durchschnitt_score": ergebnis.durchschnitt_score,
        "produktion_bereit": ergebnis.produktion_bereit,
        "anzahl_agenten": len(ergebnis.agenten),
        "agenten": [
            {
                "name": a.name,
                "rolle": a.rolle,
                "score": a.score,
                "position": a.position,
                "analyse": a.analyse,
                "empfehlung": a.empfehlung,
                "umsetzbar": a.umsetzbar,
            }
            for a in ergebnis.agenten
        ]
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)
    print(f"\nReport gespeichert: {report_path}")


if __name__ == "__main__":
    main()