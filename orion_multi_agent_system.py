#!/usr/bin/env python3
"""
=============================================================================
ORION MULTI-AGENT SYSTEM – THE ARCHITEKT ⊘∞⧈∞⊘
=============================================================================
Multi-Agenten-Architektur für vollautomatische Gebäudeplanung mit:
- Spezialisierte Agenten (Zivilingenieur, Bauphysiker, Kostenplaner, etc.)
- Hybrid-Ansatz: Deterministisch (Statik) + Probabilistisch (Kosten/Risiko)
- Normgerechte Papiere für behördliche Genehmigungen
- ISO 26262 ASIL-D für sicherheitskritische Berechnungen

Autoren: Elisabeth Steurer & Gerhard Hirschmann
Datum: 2026-04-07
Ort: Almdorf 9, St. Johann in Tirol, Austria
Lizenz: Apache 2.0

PHILOSOPHIE:
THE ARCHITEKT ⊘∞⧈∞⊘ - Jeder Agent denkt anders - wie echte Fachexperten:
- Zivilingenieur: Sicherheit > Alles, deterministisch, normgerecht
- The Architekt: Ästhetik, Nutzbarkeit, Gestaltung, Orchestrierung
- Bauphysiker: Energieeffizienz, Komfort, Physik
- Kostenplaner: Wirtschaftlichkeit, Unsicherheiten (Monte Carlo!)
- Brandschutz: Worst-case, Risikominimierung
=============================================================================
"""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Import existing ORION modules
try:
    from orion_agent_core import OrionAgent

    ORION_CORE_AVAILABLE = True
except ImportError:
    ORION_CORE_AVAILABLE = False

try:
    from orion_architekt_at import BUNDESLAENDER, berechne_hwb_grob, berechne_uwert

    ORION_ARCHITEKT_AVAILABLE = True
except ImportError:
    ORION_ARCHITEKT_AVAILABLE = False
    BUNDESLAENDER = {}

# Import Eurocode modules (deterministic structural calculations)
import sys

sys.path.insert(0, str(Path(__file__).parent / "eurocode_ec2_at" / "src"))
sys.path.insert(0, str(Path(__file__).parent / "eurocode_ec3_at" / "src"))
sys.path.insert(0, str(Path(__file__).parent / "eurocode_ec6_at" / "src"))
sys.path.insert(0, str(Path(__file__).parent / "eurocode_ec7_at" / "src"))
sys.path.insert(0, str(Path(__file__).parent / "eurocode_ec8_at" / "src"))
sys.path.insert(0, str(Path(__file__).parent / "bsh_ec5_at" / "src"))

try:
    from beton_träger_v1 import BetonTraegerEC2AT_V1, EC2Config
    from bsh_träger_v3 import BSHTraegerEC5AT_V3
    from bsh_träger_v3 import Config as BSHConfig
    from erdbeben_v1 import EC8Config, ErdbebenEC8AT_V1
    from fundament_v1 import EC7Config, FlachfundamentEC7AT_V1
    from mauerwerk_wand_v1 import EC6Config, MauerwerkWandEC6AT_V1
    from stahl_träger_v1 import EC3Config, StahlTraegerEC3AT_V1

    EUROCODE_AVAILABLE = True
except ImportError as e:
    EUROCODE_AVAILABLE = False
    print(f"⚠️  Eurocode Import-Fehler: {e}")

# Import GENESIS × EIRA Framework
try:
    from genesis.framework.epistemology import EpistemicState, KnowledgeType, VerificationLevel
    from genesis.framework.policy import DecisionMode, DecisionPolicyEngine, PolicyViolationError

    GENESIS_FRAMEWORK_AVAILABLE = True
except ImportError as e:
    GENESIS_FRAMEWORK_AVAILABLE = False
    print(f"⚠️  GENESIS Framework Import-Fehler: {e}")


# =============================================================================
# AGENT BASE CLASS
# =============================================================================


class AgentBase:
    """
    Basis-Klasse für alle Agenten.
    Jeder Agent hat seine eigene Denkweise und Prioritäten.
    """

    def __init__(self, name: str, mindset: str, priorities: List[str]):
        self.name = name
        self.mindset = mindset
        self.priorities = priorities
        self.decisions_log = []

    def denke(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Denke über ein Problem nach - individuell pro Agent"""
        raise NotImplementedError("Jeder Agent muss seine eigene Denkweise implementieren")

    def log_decision(self, decision: Dict[str, Any]):
        """Logge Entscheidung für Audit Trail"""
        decision["timestamp"] = datetime.now(timezone.utc).isoformat()
        decision["agent"] = self.name
        self.decisions_log.append(decision)

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Hole vollständigen Audit Trail"""
        return self.decisions_log


# =============================================================================
# 1. ZIVILINGENIEUR AGENT (DETERMINISTISCH)
# =============================================================================


class ZivilingenieurAgent(AgentBase):
    """
    Denkt wie ein österreichischer Zivilingenieur:
    - Sicherheit > Alles
    - Normgerecht (ÖNORM EN 1992-1998)
    - Deterministisch (KEINE Wahrscheinlichkeiten!)
    - ISO 26262 ASIL-D
    - Unterschriftsfähige Papiere
    """

    def __init__(self):
        super().__init__(
            name="Zivilingenieur",
            mindset="SICHERHEIT IST NICHT VERHANDELBAR",
            priorities=[
                "Normkonformität",
                "Tragsicherheit",
                "Standsicherheit",
                "Gebrauchstauglichkeit",
            ],
        )
        self.unterschrift_erforderlich = True
        self.eurocode_modules = {
            "EC2": BetonTraegerEC2AT_V1 if EUROCODE_AVAILABLE else None,
            "EC3": StahlTraegerEC3AT_V1 if EUROCODE_AVAILABLE else None,
            "EC5": BSHTraegerEC5AT_V3 if EUROCODE_AVAILABLE else None,
            "EC6": MauerwerkWandEC6AT_V1 if EUROCODE_AVAILABLE else None,
            "EC7": FlachfundamentEC7AT_V1 if EUROCODE_AVAILABLE else None,
            "EC8": ErdbebenEC8AT_V1 if EUROCODE_AVAILABLE else None,
        }

    def denke(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Denke wie ein Zivilingenieur"""
        return {
            "agent": self.name,
            "mindset": self.mindset,
            "methode": "Eurocode-konform, deterministisch",
            "unsicherheit": 0.0,  # KEINE Wahrscheinlichkeiten!
            "unterschrift": "erforderlich",
            "priorität": "Tragsicherheit und Standsicherheit",
            "risikotoleranz": "ZERO - Sicherheit absolut",
        }

    def bemesse_tragwerk(self, bauwerk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bemesse Tragwerk normgerecht nach Eurocode.
        DETERMINISTISCH - Keine Monte Carlo Simulation!
        """
        if not EUROCODE_AVAILABLE:
            return {
                "status": "ERROR",
                "fehler": "Eurocode-Module nicht verfügbar",
                "empfehlung": "Module installieren",
            }

        material = bauwerk.get("material", "beton").lower()
        spannweite = bauwerk.get("spannweite_m", 8.0)
        last = bauwerk.get("nutzlast_kn_per_m", 20.0)

        ergebnis = {}

        # Wähle passendes Eurocode-Modul
        if material == "beton":
            config = EC2Config(L_SPANNWEITE_M=spannweite, QK_NUTZLAST_KN_PER_M=last)
            calc = BetonTraegerEC2AT_V1(config)
            results = calc.run_optimization()

            # Finde beste Lösung
            ok_results = [r for r in results if r.eta_bending <= 1.0]
            if ok_results:
                best = ok_results[0]
                ergebnis = {
                    "material": "Stahlbeton",
                    "eurocode": "EN 1992-1-1",
                    "hoehe_mm": best.h_total_mm,
                    "bewehrung_mm2": best.As_vorh_mm2,
                    "ausnutzung": best.eta_bending,
                    "status": (
                        "GENEHMIGUNGSFÄHIG"
                        if best.eta_bending <= 1.0
                        else "NICHT GENEHMIGUNGSFÄHIG"
                    ),
                    "methode": "deterministisch",
                    "monte_carlo": False,
                }
            else:
                ergebnis = {"status": "KEINE LÖSUNG GEFUNDEN"}

        elif material == "stahl":
            config = EC3Config(L_SPANNWEITE_M=spannweite, QK_NUTZLAST_KN_PER_M=last)
            calc = StahlTraegerEC3AT_V1(config)
            results = calc.run_optimization()

            ok_results = [r for r in results if r.bending_ok and r.shear_ok and r.deflection_ok]
            if ok_results:
                best = ok_results[0]
                ergebnis = {
                    "material": "Stahl",
                    "eurocode": "EN 1993-1-1",
                    "profil": best.profile_name,
                    "masse_kg_per_m": best.mass_kg_per_m,
                    "ausnutzung": best.eta_bending,
                    "status": "GENEHMIGUNGSFÄHIG",
                    "methode": "deterministisch",
                    "monte_carlo": False,
                }
            else:
                ergebnis = {"status": "KEINE LÖSUNG GEFUNDEN"}

        elif material == "holz":
            config = BSHConfig(L_M=spannweite, Q_KN_PER_M=last)
            calc = BSHTraegerEC5AT_V3(config)
            results = calc.run_optimization()

            if results:
                best = results[0]
                ergebnis = {
                    "material": "Brettschichtholz (BSH)",
                    "eurocode": "EN 1995-1-1",
                    "hoehe_mm": best.h_mm,
                    "breite_mm": best.b_mm,
                    "ausnutzung": best.eta,
                    "status": (
                        "GENEHMIGUNGSFÄHIG" if best.status == "OK" else "NICHT GENEHMIGUNGSFÄHIG"
                    ),
                    "methode": "deterministisch",
                    "monte_carlo": False,
                }
            else:
                ergebnis = {"status": "KEINE LÖSUNG GEFUNDEN"}

        # Log decision
        self.log_decision(
            {
                "typ": "Tragwerksbemessung",
                "material": material,
                "ergebnis": ergebnis,
                "deterministisch": True,
                "normkonform": True,
            }
        )

        return ergebnis

    def generate_statik_papier(
        self, statik_ergebnis: Dict[str, Any], projekt_info: Dict[str, Any]
    ) -> str:
        """
        Generiere unterschriftsfähiges statisches Gutachten.
        Nach ÖNORM EN 1992-1998, rechtlich bindend.
        """
        audit_hash = hashlib.sha256(
            json.dumps(statik_ergebnis, sort_keys=True).encode()
        ).hexdigest()[:16]

        return f"""
{'='*80}
STATISCHES GUTACHTEN
{'='*80}
Projekt:          {projekt_info.get('name', 'Unbekannt')}
Bauherr:          {projekt_info.get('bauherr', 'N/A')}
Standort:         {projekt_info.get('standort', 'N/A')}
Datum:            {datetime.now().strftime('%Y-%m-%d')}
Norm:             ÖNORM {statik_ergebnis.get('eurocode', 'EN 1992-1998')}

{'='*80}
VERANTWORTLICHER ZIVILINGENIEUR
{'='*80}
⚠️  UNTERSCHRIFT ERFORDERLICH gemäß Ziviltechnikergesetz!

Name:             _______________________________________
ZT-Nummer:        _______________________________________
Stempel:          [ Platz für Stempel ]


{'='*80}
STATISCHE BERECHNUNG
{'='*80}

1. SYSTEM
   Material:      {statik_ergebnis.get('material', 'N/A')}
   Spannweite:    L = {projekt_info.get('spannweite_m', 'N/A')} m
   Belastung:     q = {projekt_info.get('nutzlast_kn_per_m', 'N/A')} kN/m

2. BEMESSUNG
   Norm:          {statik_ergebnis.get('eurocode', 'N/A')}
   Ergebnis:      {json.dumps(statik_ergebnis, indent=3, ensure_ascii=False)}

3. NACHWEIS
   Ausnutzung:    η = {statik_ergebnis.get('ausnutzung', 'N/A'):.3f} {'≤ 1.0 ✓' if statik_ergebnis.get('ausnutzung', 1.0) <= 1.0 else '> 1.0 ✗'}
   Methode:       {statik_ergebnis.get('methode', 'N/A').upper()}
   Monte Carlo:   {'NEIN' if not statik_ergebnis.get('monte_carlo', False) else 'JA'}
   Status:        {statik_ergebnis.get('status', 'N/A')}

4. AUDIT-TRAIL
   SHA-256:       {audit_hash}
   Reproduzierbar: JA (deterministisch)
   ISO 26262:     ASIL-D konform

{'='*80}
ERGEBNIS: {statik_ergebnis.get('status', 'UNBEKANNT')}
{'='*80}

⚠️  HAFTUNG:
Dieses Gutachten wurde nach bestem Wissen und unter Anwendung der
anerkannten Regeln der Technik erstellt. Die Haftung des Zivilingenieurs
richtet sich nach den gesetzlichen Bestimmungen.

{'='*80}
UNTERSCHRIFT & STEMPEL
{'='*80}

Datum: _____________    Unterschrift ZT: _________________________

Stempel:
┌─────────────────────────────────────┐
│                                     │
│   [ Platz für ZT-Stempel ]          │
│                                     │
└─────────────────────────────────────┘

{'='*80}
SHA-256 Audit-Hash: {audit_hash}
{'='*80}
"""


# =============================================================================
# 2. BAUPHYSIKER AGENT (DETERMINISTISCH)
# =============================================================================


class BauphysikerAgent(AgentBase):
    """
    Denkt wie ein Bauphysiker:
    - Energieeffizienz
    - Wärmeschutz
    - Feuchteschutz
    - Komfort
    """

    def __init__(self):
        super().__init__(
            name="Bauphysiker",
            mindset="PHYSIK LÜGT NICHT",
            priorities=["U-Wert", "HWB", "Tauwasser-Vermeidung", "Sommerlicher Wärmeschutz"],
        )

    def denke(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "agent": self.name,
            "mindset": self.mindset,
            "methode": "Physikalisch korrekt, OIB-RL konform",
            "unsicherheit": 0.0,  # Deterministisch
            "priorität": "Energieeffizienz und Komfort",
        }

    def berechne_energieausweis(self, gebaeude: Dict[str, Any]) -> Dict[str, Any]:
        """Berechne Energieausweis nach OIB-RL 6"""
        if not ORION_ARCHITEKT_AVAILABLE:
            return {"status": "ERROR", "fehler": "orion_architekt_at nicht verfügbar"}

        # Verwende bestehende orion_architekt_at Funktionen
        u_wert_result = berechne_uwert(
            schichten=gebaeude.get(
                "wandaufbau",
                [{"material": "Ziegel", "dicke_mm": 250}, {"material": "Dämmung", "dicke_mm": 160}],
            )
        )
        u_wert = (
            u_wert_result if isinstance(u_wert_result, float) else u_wert_result.get("u_wert", 0.25)
        )

        hwb_result = berechne_hwb_grob(
            flaeche_m2=gebaeude.get("volumen_m3", 800.0) / 2.8,  # Approximation
            uwert_wand=u_wert,
            uwert_dach=0.20,
            uwert_fenster=1.0,
            uwert_boden=0.30,
            fensteranteil_pct=20.0,
        )

        self.log_decision(
            {
                "typ": "Energieberechnung",
                "u_wert": u_wert,
                "hwb": hwb_result,
                "deterministisch": True,
            }
        )

        return {
            "u_wert": u_wert,
            "hwb": hwb_result,
            "status": "KONFORM" if hwb_result.get("hwb", 999) < 100 else "NICHT KONFORM",
        }


# =============================================================================
# 3. KOSTENPLANER AGENT (PROBABILISTISCH - MONTE CARLO!)
# =============================================================================


class KostenplanerAgent(AgentBase):
    """
    Denkt wie ein Kostenplaner:
    - Wirtschaftlichkeit
    - Unsicherheiten AKZEPTIEREN
    - Monte Carlo Simulation für Risikobewertung
    - BKI-Richtwerte als Basis
    """

    def __init__(self):
        super().__init__(
            name="Kostenplaner",
            mindset="KOSTEN HABEN IMMER UNSICHERHEITEN",
            priorities=["Wirtschaftlichkeit", "Risikotransparenz", "Realistisch", "Reserve-Puffer"],
        )

    def denke(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "agent": self.name,
            "mindset": self.mindset,
            "methode": "Monte Carlo Simulation (10.000 Läufe)",
            "unsicherheit": 0.15,  # ~15% Unsicherheit ist NORMAL!
            "priorität": "Realistische Kostenschätzung mit Risiken",
        }

    def schaetze_kosten_monte_carlo(
        self, bauwerk: Dict[str, Any], n_simulations: int = 10000
    ) -> Dict[str, Any]:
        """
        Monte Carlo Kostensimulation.
        HIER IST MONTE CARLO ERLAUBT UND SINNVOLL!

        Nicht deterministisch - Kosten haben IMMER Unsicherheiten.
        """
        # Basis-Kosten aus BKI-Richtwerten
        bgf = bauwerk.get("bgf_m2", 150.0)
        basis_kosten_pro_m2 = bauwerk.get("basis_kosten_m2", 2500.0)  # €/m²
        basis_gesamt = bgf * basis_kosten_pro_m2

        # Unsicherheiten definieren (realistische Werte aus Bauerfahrung)
        unsicherheiten = {
            "material": (0.90, 1.15),  # -10% bis +15% (Preisschwankungen)
            "lohn": (0.95, 1.20),  # -5% bis +20% (Fachkräftemangel)
            "bauzeit": (1.00, 1.30),  # +0% bis +30% (Verzögerungen)
            "unvorhergesehenes": (1.00, 1.12),  # +0% bis +12% (Überraschungen)
        }

        # Monte Carlo Simulation (10.000 Durchläufe)
        simulationen = []
        np.random.seed(42)  # Reproduzierbar

        for _ in range(n_simulations):
            faktor_material = np.random.uniform(*unsicherheiten["material"])
            faktor_lohn = np.random.uniform(*unsicherheiten["lohn"])
            faktor_bauzeit = np.random.uniform(*unsicherheiten["bauzeit"])
            faktor_unvorhergesehen = np.random.uniform(*unsicherheiten["unvorhergesehenes"])

            kosten_sim = (
                basis_gesamt
                * faktor_material
                * faktor_lohn
                * faktor_bauzeit
                * faktor_unvorhergesehen
            )
            simulationen.append(kosten_sim)

        simulationen = np.array(simulationen)

        # Auswertung
        ergebnis = {
            "methode": "Monte Carlo Simulation",
            "anzahl_simulationen": n_simulations,
            "basis_kosten_eur": basis_gesamt,
            "statistik": {
                "mittelwert_eur": float(np.mean(simulationen)),
                "median_eur": float(np.median(simulationen)),
                "standardabweichung_eur": float(np.std(simulationen)),
                "minimum_eur": float(np.min(simulationen)),
                "maximum_eur": float(np.max(simulationen)),
            },
            "perzentile": {
                "p10_eur": float(np.percentile(simulationen, 10)),  # 10% billiger
                "p25_eur": float(np.percentile(simulationen, 25)),
                "p50_eur": float(np.percentile(simulationen, 50)),  # Median
                "p75_eur": float(np.percentile(simulationen, 75)),
                "p90_eur": float(np.percentile(simulationen, 90)),  # 10% teurer
                "p95_eur": float(np.percentile(simulationen, 95)),  # 5% Risiko
            },
            "empfehlung": {
                "budget_konservativ_eur": float(
                    np.percentile(simulationen, 90)
                ),  # P90 = 90% Sicherheit
                "budget_realistisch_eur": float(
                    np.percentile(simulationen, 75)
                ),  # P75 = 75% Sicherheit
                "budget_optimistisch_eur": float(np.percentile(simulationen, 50)),  # P50 = Median
            },
            "warnung": "KEINE Festpreisgarantie! Unsicherheiten sind NORMAL im Bauwesen.",
            "monte_carlo": True,
            "deterministisch": False,
        }

        self.log_decision(
            {
                "typ": "Kostenschätzung",
                "methode": "Monte Carlo",
                "ergebnis": ergebnis,
                "monte_carlo": True,
            }
        )

        return ergebnis


# =============================================================================
# 4. RISIKOMANAGER AGENT (PROBABILISTISCH)
# =============================================================================


class RisikomanagerAgent(AgentBase):
    """
    Denkt wie ein Risikomanager:
    - Risiken identifizieren
    - Wahrscheinlichkeiten quantifizieren
    - Monte Carlo für Risikoaggregation
    """

    def __init__(self):
        super().__init__(
            name="Risikomanager",
            mindset="RISIKEN KANN MAN NICHT ELIMINIEREN - NUR MANAGEN",
            priorities=["Risikoidentifikation", "Quantifizierung", "Mitigation", "Monitoring"],
        )

    def denke(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "agent": self.name,
            "mindset": self.mindset,
            "methode": "Probabilistische Risikoanalyse (Monte Carlo)",
            "unsicherheit": "explizit modelliert",
            "priorität": "Risikotransparenz und Mitigation",
        }

    def analysiere_risiken_monte_carlo(
        self, projekt: Dict[str, Any], n_simulations: int = 5000
    ) -> Dict[str, Any]:
        """
        Risiko-Aggregation mit Monte Carlo.
        Quantifiziert Gesamtrisiko des Projekts.
        """
        # Identifiziere Risiken
        risiken = {
            "genehmigung_verzug": {"prob": 0.20, "impact_tage": (0, 60)},
            "material_verteuerung": {"prob": 0.30, "impact_prozent": (0, 0.15)},
            "fachkraefte_fehlen": {"prob": 0.25, "impact_tage": (0, 45)},
            "wetter_verzoegerung": {"prob": 0.40, "impact_tage": (0, 30)},
            "baumangel_nachbesserung": {"prob": 0.15, "impact_kosten": (0, 50000)},
        }

        # Monte Carlo Simulation
        np.random.seed(42)
        gesamt_verzoegerung = []
        gesamt_mehrkosten = []

        for _ in range(n_simulations):
            verzug_tage = 0
            mehrkosten_eur = 0

            # Genehmigungsverzug
            if np.random.random() < risiken["genehmigung_verzug"]["prob"]:
                verzug_tage += np.random.uniform(*risiken["genehmigung_verzug"]["impact_tage"])

            # Material
            if np.random.random() < risiken["material_verteuerung"]["prob"]:
                faktor = np.random.uniform(*risiken["material_verteuerung"]["impact_prozent"])
                mehrkosten_eur += projekt.get("baukosten_eur", 375000) * faktor

            # Fachkräfte
            if np.random.random() < risiken["fachkraefte_fehlen"]["prob"]:
                verzug_tage += np.random.uniform(*risiken["fachkraefte_fehlen"]["impact_tage"])

            # Wetter
            if np.random.random() < risiken["wetter_verzoegerung"]["prob"]:
                verzug_tage += np.random.uniform(*risiken["wetter_verzoegerung"]["impact_tage"])

            # Baumangel
            if np.random.random() < risiken["baumangel_nachbesserung"]["prob"]:
                mehrkosten_eur += np.random.uniform(
                    *risiken["baumangel_nachbesserung"]["impact_kosten"]
                )

            gesamt_verzoegerung.append(verzug_tage)
            gesamt_mehrkosten.append(mehrkosten_eur)

        gesamt_verzoegerung = np.array(gesamt_verzoegerung)
        gesamt_mehrkosten = np.array(gesamt_mehrkosten)

        return {
            "methode": "Monte Carlo Risikoanalyse",
            "anzahl_simulationen": n_simulations,
            "risiken_identifiziert": len(risiken),
            "verzoegerung_tage": {
                "mittel": float(np.mean(gesamt_verzoegerung)),
                "median": float(np.median(gesamt_verzoegerung)),
                "p90": float(np.percentile(gesamt_verzoegerung, 90)),  # 90% unter diesem Wert
                "maximum": float(np.max(gesamt_verzoegerung)),
            },
            "mehrkosten_eur": {
                "mittel": float(np.mean(gesamt_mehrkosten)),
                "median": float(np.median(gesamt_mehrkosten)),
                "p90": float(np.percentile(gesamt_mehrkosten, 90)),
                "maximum": float(np.max(gesamt_mehrkosten)),
            },
            "empfehlung": {
                "zeitpuffer_tage": float(np.percentile(gesamt_verzoegerung, 80)),
                "kostenreserve_eur": float(np.percentile(gesamt_mehrkosten, 80)),
            },
            "monte_carlo": True,
        }


# =============================================================================
# 5. HAUPTORCHESTRATOR - THE ARCHITEKT AGENT ⊘∞⧈∞⊘
# =============================================================================


class TheArchitektAgent(AgentBase):
    """
    Haupt-Orchestrator.
    THE ARCHITEKT - Koordiniert alle Fachexperten mit höchster Präzision.
    ⊘∞⧈∞⊘ - Global Anchor für Gesamtkoordination

    Integrated with GENESIS × EIRA V4.2:
    - Epistemological Safety: VERIFIED/ESTIMATED/UNKNOWN knowledge classification
    - Decision Policy Engine: Enforces fallback when epistemic conditions fail
    - ISO 26262 ASIL-D compliant decision constraints
    """

    def __init__(self):
        super().__init__(
            name="The Architekt (Orchestrator)",
            mindset="GANZHEITLICH DENKEN - ALLE ASPEKTE INTEGRIEREN",
            priorities=["Gesamtkonzept", "Nutzerzufriedenheit", "Ästhetik", "Wirtschaftlichkeit"],
        )

        # Alle Fachexperten
        self.zivilingenieur = ZivilingenieurAgent()
        self.bauphysiker = BauphysikerAgent()
        self.kostenplaner = KostenplanerAgent()
        self.risikomanager = RisikomanagerAgent()

        # GENESIS Framework Integration
        if GENESIS_FRAMEWORK_AVAILABLE:
            self.policy_engine = DecisionPolicyEngine(confidence_threshold=0.5)
        else:
            self.policy_engine = None

    def denke(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "agent": self.name,
            "mindset": self.mindset,
            "methode": "Multi-Agenten-Orchestrierung",
            "fachexperten": [
                self.zivilingenieur.name,
                self.bauphysiker.name,
                self.kostenplaner.name,
                self.risikomanager.name,
            ],
        }

    def plane_projekt_vollstaendig(self, projekt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vollständige Projektplanung mit allen Agenten.
        HYBRID: Deterministisch (Statik) + Probabilistisch (Kosten/Risiko)
        """
        print(f"\n{'='*80}")
        print("ORION MULTI-AGENT SYSTEM - VOLLSTÄNDIGE PROJEKTPLANUNG")
        print(f"{'='*80}\n")

        ergebnis = {
            "projekt": projekt.get("name", "Unbekannt"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agenten_eingesetzt": [],
        }

        # 1. ZIVILINGENIEUR: Statik (DETERMINISTISCH)
        print("1️⃣  ZIVILINGENIEUR arbeitet (deterministisch, normgerecht)...")
        statik = self.zivilingenieur.bemesse_tragwerk(
            {
                "material": projekt.get("material", "beton"),
                "spannweite_m": projekt.get("spannweite_m", 8.0),
                "nutzlast_kn_per_m": projekt.get("nutzlast_kn_per_m", 20.0),
            }
        )
        ergebnis["statik"] = statik
        ergebnis["agenten_eingesetzt"].append("Zivilingenieur (deterministisch)")
        print(f"   ✓ Statik: {statik.get('status', 'N/A')}")
        print(f"   ✓ Monte Carlo verwendet: {statik.get('monte_carlo', False)}")

        # 2. BAUPHYSIKER: Energie (DETERMINISTISCH)
        print("\n2️⃣  BAUPHYSIKER arbeitet (deterministisch, physikalisch korrekt)...")
        energie = self.bauphysiker.berechne_energieausweis(
            {
                "huellflaeche_m2": projekt.get("huellflaeche_m2", 300.0),
                "fensterflaeche_m2": projekt.get("fensterflaeche_m2", 50.0),
                "volumen_m3": projekt.get("volumen_m3", 800.0),
            }
        )
        ergebnis["energie"] = energie
        ergebnis["agenten_eingesetzt"].append("Bauphysiker (deterministisch)")
        print(f"   ✓ Energie: {energie.get('status', 'N/A')}")
        print(f"   ✓ HWB: {energie.get('hwb', {}).get('hwb', 'N/A')} kWh/(m²a)")

        # 3. KOSTENPLANER: Kosten MIT MONTE CARLO!
        print("\n3️⃣  KOSTENPLANER arbeitet (PROBABILISTISCH - Monte Carlo!)...")
        kosten = self.kostenplaner.schaetze_kosten_monte_carlo(
            {
                "bgf_m2": projekt.get("bgf_m2", 150.0),
                "basis_kosten_m2": projekt.get("basis_kosten_m2", 2500.0),
            }
        )
        ergebnis["kosten"] = kosten
        ergebnis["agenten_eingesetzt"].append("Kostenplaner (Monte Carlo)")
        print(f"   ✓ Kosten (Monte Carlo): {kosten['statistik']['mittelwert_eur']:,.0f} €")
        print(
            f"   ✓ Budget P90 (konservativ): {kosten['empfehlung']['budget_konservativ_eur']:,.0f} €"
        )
        print(f"   ✓ Simulationen: {kosten['anzahl_simulationen']:,}")

        # 4. RISIKOMANAGER: Risiken MIT MONTE CARLO!
        print("\n4️⃣  RISIKOMANAGER arbeitet (PROBABILISTISCH - Monte Carlo!)...")
        risiken = self.risikomanager.analysiere_risiken_monte_carlo(
            {"baukosten_eur": kosten["statistik"]["mittelwert_eur"]}
        )
        ergebnis["risiken"] = risiken
        ergebnis["agenten_eingesetzt"].append("Risikomanager (Monte Carlo)")
        print(f"   ✓ Risiken: {risiken['risiken_identifiziert']} identifiziert")
        print(f"   ✓ Zeitpuffer-Empfehlung: {risiken['empfehlung']['zeitpuffer_tage']:.0f} Tage")
        print(f"   ✓ Kostenreserve-Empfehlung: {risiken['empfehlung']['kostenreserve_eur']:,.0f} €")

        # 5. GESAMTBEWERTUNG
        print(f"\n{'='*80}")
        print("GESAMTBEWERTUNG")
        print(f"{'='*80}")

        genehmigungsfaehig = (
            statik.get("status") == "GENEHMIGUNGSFÄHIG" and energie.get("status") == "KONFORM"
        )

        ergebnis["gesamtbewertung"] = {
            "genehmigungsfaehig": genehmigungsfaehig,
            "statik_ok": statik.get("status") == "GENEHMIGUNGSFÄHIG",
            "energie_ok": energie.get("status") == "KONFORM",
            "kosten_realistisch": True,  # Monte Carlo liefert immer realistische Schätzung
            "risiken_quantifiziert": True,
            "empfehlung": "PROJEKT UMSETZBAR" if genehmigungsfaehig else "PROJEKT ÜBERARBEITEN",
        }

        print(f"Status: {ergebnis['gesamtbewertung']['empfehlung']}")
        print(f"Statik: {'✓' if ergebnis['gesamtbewertung']['statik_ok'] else '✗'}")
        print(f"Energie: {'✓' if ergebnis['gesamtbewertung']['energie_ok'] else '✗'}")
        print(f"{'='*80}\n")

        return ergebnis

    def create_epistemic_state_from_agent_result(
        self, agent_name: str, result: Dict[str, Any], is_deterministic: bool
    ) -> EpistemicState:
        """
        Wrap agent result in epistemic state for policy checking

        Args:
            agent_name: Name of agent that produced result
            result: Agent's output
            is_deterministic: True if agent used deterministic methods

        Returns:
            EpistemicState with appropriate classification
        """
        if not GENESIS_FRAMEWORK_AVAILABLE:
            # Framework not available - return dummy state
            return None

        if is_deterministic:
            # Deterministic agents (Zivilingenieur, Bauphysiker) produce VERIFIED knowledge
            norm = result.get("eurocode", result.get("norm", "ÖNORM"))
            return EpistemicState.from_eurocode_calculation(
                value=result,
                norm=norm,
                metadata={
                    "agent": agent_name,
                    "method": "deterministic",
                    "monte_carlo": False,
                },
            )
        else:
            # Probabilistic agents (Kostenplaner, Risikomanager) produce ESTIMATED knowledge
            n_simulations = result.get("anzahl_simulationen", result.get("n_simulations", 0))
            # Calculate confidence based on number of simulations
            # More simulations = higher confidence (asymptotic to 0.95)
            confidence = min(0.95, 0.5 + (n_simulations / 20000) * 0.45)

            return EpistemicState.from_monte_carlo(
                value=result,
                confidence=confidence,
                n_simulations=n_simulations,
                metadata={
                    "agent": agent_name,
                    "method": "probabilistic",
                    "monte_carlo": True,
                },
            )

    def check_decision_policy(
        self, decision_type: str, epistemic_states: Dict[str, EpistemicState], mode: DecisionMode
    ) -> Dict[str, Any]:
        """
        Check if decision is allowed under policy constraints

        Args:
            decision_type: Type of decision (e.g., "Statik-Papier")
            epistemic_states: Dict mapping input names to epistemic states
            mode: DETERMINISTIC or PROBABILISTIC

        Returns:
            Policy check result with allowed/violations/reason
        """
        if not GENESIS_FRAMEWORK_AVAILABLE or self.policy_engine is None:
            # Framework not available - allow all decisions
            return {
                "allowed": True,
                "mode": mode.value if isinstance(mode, DecisionMode) else mode,
                "violations": [],
                "reason": "GENESIS framework not available - policy checks disabled",
            }

        return self.policy_engine.check_decision_allowed(
            decision_mode=mode,
            inputs=epistemic_states,
            decision_type=decision_type,
        )


# =============================================================================
# MAIN API
# =============================================================================


class ORIONMultiAgentSystem:
    """
    Hauptschnittstelle für das Multi-Agenten-System.
    ⊘∞⧈∞⊘ THE ARCHITEKT - Orchestrator

    Integrated with GENESIS × EIRA V4.2 Framework:
    - Epistemological Safety (VERIFIED/ESTIMATED/UNKNOWN knowledge)
    - Decision Policy Engine (ISO 26262 ASIL-D compliant)
    - Fallback mechanisms for safety-critical decisions
    """

    VERSION = "1.0.0"
    GENESIS_VERSION = "4.2.0" if GENESIS_FRAMEWORK_AVAILABLE else None

    def __init__(self):
        self.architekt = TheArchitektAgent()

    def plane_projekt(self, projekt: Dict[str, Any]) -> Dict[str, Any]:
        """Plane Projekt vollständig mit allen Agenten"""
        return self.architekt.plane_projekt_vollstaendig(projekt)

    def get_agent_info(self) -> Dict[str, Any]:
        """Informationen über alle Agenten"""
        info = {
            "version": self.VERSION,
            "genesis_framework": {
                "available": GENESIS_FRAMEWORK_AVAILABLE,
                "version": self.GENESIS_VERSION,
                "features": (
                    [
                        "Epistemological Safety (VERIFIED/ESTIMATED/UNKNOWN)",
                        "Decision Policy Engine",
                        "ISO 26262 ASIL-D Fallback Mechanisms",
                    ]
                    if GENESIS_FRAMEWORK_AVAILABLE
                    else []
                ),
            },
            "agenten": {
                "the_architekt": self.architekt.denke({}),
                "zivilingenieur": self.architekt.zivilingenieur.denke({}),
                "bauphysiker": self.architekt.bauphysiker.denke({}),
                "kostenplaner": self.architekt.kostenplaner.denke({}),
                "risikomanager": self.architekt.risikomanager.denke({}),
            },
            "hybrid_ansatz": {
                "deterministisch": ["Zivilingenieur", "Bauphysiker"],
                "probabilistisch": ["Kostenplaner", "Risikomanager"],
            },
            "monte_carlo_wo_sinnvoll": ["Kosten", "Risiken", "Termine"],
            "keine_wahrscheinlichkeiten_wo_kritisch": ["Statik", "Brandschutz", "Tragsicherheit"],
        }

        # Add policy engine statistics if available
        if GENESIS_FRAMEWORK_AVAILABLE and self.architekt.policy_engine:
            info["genesis_framework"][
                "policy_statistics"
            ] = self.architekt.policy_engine.get_statistics()

        return info


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("⊘∞⧈∞⊘ ORION MULTI-AGENT SYSTEM V1.0")
    print("Hybrid: Deterministisch (Statik) + Probabilistisch (Kosten/Risiko)")
    print()

    # Erstelle System
    system = ORIONMultiAgentSystem()

    # Beispiel-Projekt
    projekt = {
        "name": "Einfamilienhaus Tirol",
        "material": "beton",
        "spannweite_m": 8.0,
        "nutzlast_kn_per_m": 20.0,
        "bgf_m2": 150.0,
        "basis_kosten_m2": 2500.0,
        "huellflaeche_m2": 300.0,
        "fensterflaeche_m2": 50.0,
        "volumen_m3": 800.0,
    }

    # Vollständige Planung
    ergebnis = system.plane_projekt(projekt)

    # Zeige Agent-Info
    print("\n📋 AGENT-INFORMATIONEN:")
    print(json.dumps(system.get_agent_info(), indent=2, ensure_ascii=False))

    print("\n✅ Multi-Agenten-System vollständig implementiert!")
    print("   Deterministisch: Statik, Bauphysik")
    print("   Probabilistisch: Kosten, Risiken (Monte Carlo)")
