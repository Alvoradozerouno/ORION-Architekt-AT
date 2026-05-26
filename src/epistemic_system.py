"""
Deterministisches Epistemisches System (DES)
=============================================

Ein formales System zur Wissensrepräsentation und -validierung
basierend auf deterministischen epistemologischen Prinzipien.

Kernkonzepte:
- Epistemische Zustände: Wissen, Glaube, Unsicherheit
- Deterministische Transitionen: Zustandsübergänge sind berechenbar
- Wissensvalidierung: Formale Verifikation von Wissensansprüchen
- Epistemische Logik: Modallogik für Wissen und Glauben

Autor: Baumeister Tool Austria Team
Version: 3.1.0
Lizenz: Apache 2.0
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class EpistemicState(Enum):
    """Epistemische Zustände nach formaler Epistemologie."""
    CERTAIN = "certain"           # Sicheres Wissen (verifiziert)
    PROBABLE = "probable"         # Wahrscheinliches Wissen (hohe Konfidenz)
    POSSIBLE = "possible"         # Mögliches Wissen (mittlere Konfidenz)
    UNCERTAIN = "uncertain"       # Unsicheres Wissen (niedrige Konfidenz)
    UNKNOWN = "unknown"           # Unbekannt (kein Wissen vorhanden)
    CONTRADICTED = "contradicted" # Widersprüchlich (konfligierende Evidenz)
    INVALID = "invalid"           # Ungültig (falsifiziert)


class EpistemicOperator(Enum):
    """Epistemische Operatoren nach Hintikka-Semantik."""
    K = "knows"           # Wissen (Kφ: Agent weiß dass φ)
    B = "believes"        # Glauben (Bφ: Agent glaubt dass φ)
    P = "possible"        # Möglichkeit (Pφ: φ ist möglich)
    N = "necessary"       # Notwendigkeit (Nφ: φ ist notwendig)
    C = "consistent"      # Konsistenz (Cφ: φ ist konsistent)


@dataclass(frozen=True)
class EpistemicProposition:
    """Eine epistemische Proposition mit formaler Struktur."""
    content: str                          # Inhalt der Proposition
    source: str                           # Quelle des Wissens
    timestamp: float = field(default_factory=time.time)
    confidence: float = 0.5               # Konfidenzwert [0, 1]
    evidence: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be in [0, 1], got {self.confidence}")

    @property
    def id(self) -> str:
        """Eindeutige ID basierend auf Inhalt und Quelle."""
        content = f"{self.content}:{self.source}:{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def __hash__(self):
        return hash(self.id)


@dataclass
class InferenceRule:
    """Eine deterministische Inferenzregel."""
    name: str
    premise_ids: List[str]
    conclusion_template: str
    confidence_factor: float = 0.9

    def apply(self, premises: List[EpistemicProposition]) -> Optional[EpistemicProposition]:
        """Wendet die Regel auf die Prämissen an."""
        if len(premises) != len(self.premise_ids):
            return None

        # Berechne kombinierte Konfidenz
        combined_confidence = 1.0
        for p in premises:
            combined_confidence *= p.confidence
        combined_confidence *= self.confidence_factor

        # Erstelle Schlussfolgerung
        content = self.conclusion_template.format(
            *[p.content for p in premises]
        )

        return EpistemicProposition(
            content=content,
            source=f"inference:{self.name}",
            confidence=combined_confidence,
            dependencies=[p.id for p in premises],
            evidence=[f"Derived via {self.name} from {[p.id for p in premises]}"]
        )


@dataclass
class EpistemicAgent:
    """Ein epistemischer Agent mit Wissenszuständen."""
    name: str
    knowledge_base: Dict[str, EpistemicProposition] = field(default_factory=dict)
    belief_base: Dict[str, EpistemicProposition] = field(default_factory=dict)
    inference_rules: List[InferenceRule] = field(default_factory=list)
    validation_threshold: float = 0.8

    def add_knowledge(self, proposition: EpistemicProposition) -> bool:
        """Fügt Wissen hinzu, wenn es validiert werden kann."""
        if proposition.confidence >= self.validation_threshold:
            self.knowledge_base[proposition.id] = proposition
            return True
        return False

    def add_belief(self, proposition: EpistemicProposition) -> None:
        """Fügt einen Glauben hinzu (niedrigere Schwelle)."""
        self.belief_base[proposition.id] = proposition

    def get_state(self, proposition_id: str) -> EpistemicState:
        """Bestimmt den epistemischen Zustand einer Proposition."""
        if proposition_id in self.knowledge_base:
            prop = self.knowledge_base[proposition_id]
            if prop.confidence >= 0.95:
                return EpistemicState.CERTAIN
            elif prop.confidence >= 0.8:
                return EpistemicState.PROBABLE
            return EpistemicState.POSSIBLE
        elif proposition_id in self.belief_base:
            prop = self.belief_base[proposition_id]
            if prop.confidence >= 0.5:
                return EpistemicState.POSSIBLE
            return EpistemicState.UNCERTAIN
        return EpistemicState.UNKNOWN

    def validate(self, proposition: EpistemicProposition) -> Tuple[bool, str]:
        """Validiert eine Proposition gegen die Wissensbasis."""
        # Prüfe auf Widersprüche
        for existing in self.knowledge_base.values():
            if self._is_contradiction(existing, proposition):
                return False, f"Contradicts with {existing.id}"

        # Prüfe Konsistenz mit Abhängigkeiten
        for dep_id in proposition.dependencies:
            if dep_id in self.knowledge_base:
                dep = self.knowledge_base[dep_id]
                if dep.confidence < 0.5:
                    return False, f"Dependency {dep_id} has low confidence"

        return True, "Valid"

    def _is_contradiction(self, p1: EpistemicProposition, p2: EpistemicProposition) -> bool:
        """Prüft ob zwei Propositionen widersprüchlich sind."""
        # Einfache Heuristik: gleicher Inhalt, unterschiedliche Quellen
        if p1.content == p2.content and p1.source != p2.source:
            return abs(p1.confidence - p2.confidence) > 0.3
        return False

    def infer(self, rule: InferenceRule) -> List[EpistemicProposition]:
        """Wendet eine Inferenzregel an und leitet neue Propositionen ab."""
        results = []
        premises = [self.knowledge_base.get(pid) for pid in rule.premise_ids]
        premises = [p for p in premises if p is not None]

        if len(premises) == len(rule.premise_ids):
            # Alle Prämissen erfüllt
            conclusion = rule.apply(premises)
            if conclusion:
                results.append(conclusion)

        return results

    def get_epistemic_closure(self) -> Set[str]:
        """Berechnet den epistemischen Abschluss (alle ableitbaren Propositionen)."""
        closure = set(self.knowledge_base.keys())
        changed = True

        while changed:
            changed = False
            for rule in self.inference_rules:
                new_props = self.infer(rule)
                for prop in new_props:
                    if prop.id not in closure:
                        if self.add_knowledge(prop):
                            closure.add(prop.id)
                            changed = True

        return closure

    def to_dict(self) -> Dict[str, Any]:
        """Serialisiert den Agent-Zustand."""
        return {
            "name": self.name,
            "knowledge_count": len(self.knowledge_base),
            "belief_count": len(self.belief_base),
            "validation_threshold": self.validation_threshold,
            "knowledge": {k: v.__dict__ for k, v in self.knowledge_base.items()},
            "beliefs": {k: v.__dict__ for k, v in self.belief_base.items()},
        }


class EpistemicValidator:
    """Validiert epistemische Ansprüche deterministisch."""

    def __init__(self):
        self.validation_log: List[Dict[str, Any]] = []

    def validate_chain(self, propositions: List[EpistemicProposition]) -> Dict[str, Any]:
        """Validiert eine Kette von Propositionen."""
        results = {
            "valid": True,
            "chain_length": len(propositions),
            "min_confidence": 1.0,
            "max_confidence": 0.0,
            "avg_confidence": 0.0,
            "contradictions": [],
            "weak_links": [],
        }

        confidences = []
        for i, prop in enumerate(propositions):
            confidences.append(prop.confidence)

            if prop.confidence < 0.5:
                results["weak_links"].append({
                    "index": i,
                    "id": prop.id,
                    "confidence": prop.confidence
                })

            # Prüfe auf Widersprüche mit vorherigen Propositionen
            for j in range(i):
                if self._contradicts(propositions[j], prop):
                    results["contradictions"].append({
                        "proposition_1": propositions[j].id,
                        "proposition_2": prop.id,
                    })
                    results["valid"] = False

        if confidences:
            results["min_confidence"] = min(confidences)
            results["max_confidence"] = max(confidences)
            results["avg_confidence"] = sum(confidences) / len(confidences)

        if results["min_confidence"] < 0.5:
            results["valid"] = False

        self.validation_log.append(results)
        return results

    def _contradicts(self, p1: EpistemicProposition, p2: EpistemicProposition) -> bool:
        """Prüft Widerspruch zwischen zwei Propositionen."""
        if p1.content == p2.content:
            return abs(p1.confidence - p2.confidence) > 0.4
        return False

    def compute_epistemic_distance(self, agent1: EpistemicAgent, agent2: EpistemicAgent) -> float:
        """Berechnet den epistemischen Abstand zwischen zwei Agenten."""
        all_ids = set(agent1.knowledge_base.keys()) | set(agent2.knowledge_base.keys())
        if not all_ids:
            return 0.0

        distance = 0.0
        for prop_id in all_ids:
            state1 = agent1.get_state(prop_id)
            state2 = agent2.get_state(prop_id)
            if state1 != state2:
                distance += 1.0

        return distance / len(all_ids)


class KnowledgeGraph:
    """Wissensgraph mit Abhängigkeiten zwischen Propositionen."""

    def __init__(self):
        self.nodes: Dict[str, EpistemicProposition] = {}
        self.edges: Dict[str, List[str]] = {}  # parent -> children

    def add_node(self, prop: EpistemicProposition) -> None:
        self.nodes[prop.id] = prop
        if prop.id not in self.edges:
            self.edges[prop.id] = []

    def add_edge(self, parent_id: str, child_id: str) -> None:
        if parent_id not in self.edges:
            self.edges[parent_id] = []
        self.edges[parent_id].append(child_id)

    def get_dependencies(self, prop_id: str) -> List[str]:
        return self.edges.get(prop_id, [])

    def get_all_ancestors(self, prop_id: str, visited: Optional[Set[str]] = None) -> Set[str]:
        if visited is None:
            visited = set()
        for parent_id, children in self.edges.items():
            if prop_id in children and parent_id not in visited:
                visited.add(parent_id)
                self.get_all_ancestors(parent_id, visited)
        return visited

    def propagate_confidence(self, prop_id: str) -> float:
        """Berechnet die effektive Konfidenz basierend auf Abhängigkeiten."""
        prop = self.nodes.get(prop_id)
        if not prop:
            return 0.0

        ancestors = self.get_all_ancestors(prop_id)
        min_ancestor_confidence = 1.0
        for ancestor_id in ancestors:
            ancestor = self.nodes.get(ancestor_id)
            if ancestor:
                min_ancestor_confidence = min(min_ancestor_confidence, ancestor.confidence)

        return prop.confidence * min_ancestor_confidence

    def detect_cycles(self) -> List[List[str]]:
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node_id: str, path: List[str]):
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            for child_id in self.edges.get(node_id, []):
                if child_id not in visited:
                    dfs(child_id, path)
                elif child_id in rec_stack:
                    cycle_start = path.index(child_id)
                    cycles.append(path[cycle_start:] + [child_id])

            rec_stack.discard(node_id)

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id, [])

        return cycles


class ConflictResolver:
    """Automatische Konfliktlösung zwischen widersprüchlichen Propositionen."""

    @staticmethod
    def resolve_conflicts(propositions: List[EpistemicProposition]) -> List[EpistemicProposition]:
        """Löst Konflikte durch Quellen-Gewichtung und Evidenz-Stärke."""
        if not propositions:
            return []

        # Gruppiere nach Inhalt
        by_content: Dict[str, List[EpistemicProposition]] = {}
        for prop in propositions:
            if prop.content not in by_content:
                by_content[prop.content] = []
            by_content[prop.content].append(prop)

        resolved = []
        for content, props in by_content.items():
            if len(props) == 1:
                resolved.append(props[0])
            else:
                # Wähle die Proposition mit höchster Konfidenz und stärkster Evidenz
                best = max(props, key=lambda p: p.confidence * (1 + len(p.evidence) * 0.1))
                resolved.append(best)

        return resolved


class TemporalKnowledgeManager:
    """Verwaltet zeitbasierte Wissensdegradation."""

    def __init__(self, half_life_hours: float = 720.0):  # 30 Tage
        self.half_life_hours = half_life_hours

    def degrade_confidence(self, prop: EpistemicProposition, current_time: Optional[float] = None) -> float:
        """Berechnet degradierte Konfidenz basierend auf Alter."""
        if current_time is None:
            current_time = time.time()

        age_hours = (current_time - prop.timestamp) / 3600.0
        decay_factor = 0.5 ** (age_hours / self.half_life_hours)

        return prop.confidence * decay_factor

    def refresh_knowledge(self, prop: EpistemicProposition, new_confidence: float) -> EpistemicProposition:
        """Aktualisiert Wissen mit neuer Konfidenz."""
        return EpistemicProposition(
            content=prop.content,
            source=prop.source,
            timestamp=time.time(),
            confidence=new_confidence,
            evidence=prop.evidence,
            dependencies=prop.dependencies,
            metadata=prop.metadata,
        )


class SwarmConsensusEngine:
    """Swarm-Intelligenz für epistemische Konsensbildung."""

    @staticmethod
    def compute_weighted_consensus(
        agents: Dict[str, EpistemicAgent],
        proposition_id: str,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Berechnet gewichteten Konsens basierend auf Agenten-Expertise."""
        if weights is None:
            weights = {name: 1.0 for name in agents}

        states = {}
        weighted_votes: Dict[str, float] = {}

        for name, agent in agents.items():
            state = agent.get_state(proposition_id)
            states[name] = state.value

            state_key = state.value
            weight = weights.get(name, 1.0) * agent.validation_threshold
            weighted_votes[state_key] = weighted_votes.get(state_key, 0.0) + weight

        total_weight = sum(weights.get(name, 1.0) * agent.validation_threshold for name in agents)
        if total_weight == 0:
            total_weight = 1.0

        consensus_state = max(weighted_votes, key=weighted_votes.get) if weighted_votes else "unknown"
        consensus_strength = weighted_votes.get(consensus_state, 0.0) / total_weight

        return {
            "proposition_id": proposition_id,
            "states": states,
            "weighted_votes": weighted_votes,
            "consensus_state": consensus_state,
            "consensus_strength": consensus_strength,
            "is_consensus": consensus_strength >= 0.7,
            "participating_agents": len(agents),
        }


class InferenceEngine:
    """Automatische Inferenz mit Regel-Anwendung."""

    def __init__(self):
        self.rules: List[InferenceRule] = []
        self.inference_log: List[Dict[str, Any]] = []

    def add_rule(self, rule: InferenceRule) -> None:
        self.rules.append(rule)

    def apply_all_rules(
        self,
        knowledge_base: Dict[str, EpistemicProposition]
    ) -> List[EpistemicProposition]:
        """Wendet alle Inferenzregeln an und leitet neue Propositionen ab."""
        new_props = []
        changed = True
        iterations = 0
        max_iterations = 100

        while changed and iterations < max_iterations:
            changed = False
            iterations += 1

            for rule in self.rules:
                premises = [knowledge_base.get(pid) for pid in rule.premise_ids]
                premises = [p for p in premises if p is not None]

                if len(premises) == len(rule.premise_ids):
                    conclusion = rule.apply(premises)
                    if conclusion and conclusion.id not in knowledge_base:
                        knowledge_base[conclusion.id] = conclusion
                        new_props.append(conclusion)
                        changed = True
                        self.inference_log.append({
                            "rule": rule.name,
                            "premises": [p.id for p in premises],
                            "conclusion": conclusion.id,
                            "confidence": conclusion.confidence,
                        })

        return new_props

    def get_built_in_rules(self) -> List[InferenceRule]:
        """Erstellt eingebaute Regeln für Bau-Compliance."""
        return [
            InferenceRule(
                name="OIB-RL6-Compliance",
                premise_ids=["oib_rl6_hwb_limit", "building_hwb_value"],
                conclusion_template="Gebäude erfüllt OIB-RL 6: HWB {{0}} ≤ 75 kWh/m²a",
                confidence_factor=0.95,
            ),
            InferenceRule(
                name="Brandschutz-Compliance",
                premise_ids=["oib_rl2_fire", "building_fire_rating"],
                conclusion_template="Gebäude erfüllt OIB-RL 2: Feuerwiderstand {{0}}",
                confidence_factor=0.95,
            ),
            InferenceRule(
                name="Schallschutz-Compliance",
                premise_ids=["oib_rl5_sound", "building_sound_rating"],
                conclusion_template="Gebäude erfüllt OIB-RL 5: Schalldämmung {{0}}",
                confidence_factor=0.90,
            ),
            InferenceRule(
                name="Gesamt-Compliance",
                premise_ids=["oib_rl6_compliant", "oib_rl2_compliant", "oib_rl5_compliant"],
                conclusion_template="Gebäude ist OIB-konform: {{0}}, {{1}}, {{2}}",
                confidence_factor=0.85,
            ),
        ]


class DeterministicEpistemicSystem:
    """
    Das deterministische epistemische System.

    Verwaltet mehrere epistemische Agenten und ermöglicht
    deterministische Wissensvalidierung und -inferenz.
    """

    def __init__(self, name: str = "DES"):
        self.name = name
        self.agents: Dict[str, EpistemicAgent] = {}
        self.validator = EpistemicValidator()
        self.global_knowledge: Dict[str, EpistemicProposition] = {}
        self.system_log: List[Dict[str, Any]] = []

        # Neue Best-Practice-Komponenten
        self.knowledge_graph = KnowledgeGraph()
        self.conflict_resolver = ConflictResolver()
        self.temporal_manager = TemporalKnowledgeManager()
        self.swarm_engine = SwarmConsensusEngine()
        self.inference_engine = InferenceEngine()

        # Eingebaute Regeln hinzufügen
        for rule in self.inference_engine.get_built_in_rules():
            self.inference_engine.add_rule(rule)

    def create_agent(self, name: str, validation_threshold: float = 0.8) -> EpistemicAgent:
        """Erstellt einen neuen epistemischen Agenten."""
        agent = EpistemicAgent(
            name=name,
            validation_threshold=validation_threshold
        )
        self.agents[name] = agent
        self._log(f"Agent '{name}' created with threshold {validation_threshold}")
        return agent

    def add_global_knowledge(self, proposition: EpistemicProposition) -> bool:
        """Fügt globales Wissen hinzu (für alle Agenten verfügbar)."""
        # Validiere gegen bestehendes globales Wissen
        for existing in self.global_knowledge.values():
            if existing.content == proposition.content:
                if abs(existing.confidence - proposition.confidence) > 0.3:
                    self._log(f"Contradiction detected for global knowledge: {proposition.id}")
                    return False

        self.global_knowledge[proposition.id] = proposition
        self._log(f"Global knowledge added: {proposition.id}")
        return True

    def sync_agent_knowledge(self, agent_name: str) -> int:
        """Synchronisiert globales Wissen zu einem Agenten."""
        if agent_name not in self.agents:
            return 0

        agent = self.agents[agent_name]
        synced = 0
        for prop_id, prop in self.global_knowledge.items():
            if prop_id not in agent.knowledge_base:
                if agent.add_knowledge(prop):
                    synced += 1

        self._log(f"Synced {synced} propositions to agent '{agent_name}'")
        return synced

    def validate_system_state(self) -> Dict[str, Any]:
        """Validiert den gesamten Systemzustand."""
        result = {
            "system_name": self.name,
            "agent_count": len(self.agents),
            "global_knowledge_count": len(self.global_knowledge),
            "total_knowledge": sum(
                len(a.knowledge_base) for a in self.agents.values()
            ),
            "total_beliefs": sum(
                len(a.belief_base) for a in self.agents.values()
            ),
            "validation_results": {},
            "contradictions": [],
            "system_valid": True,
        }

        # Validiere jeden Agenten
        for name, agent in self.agents.items():
            agent_result = {
                "knowledge_count": len(agent.knowledge_base),
                "belief_count": len(agent.belief_base),
                "states": {},
            }

            for prop_id in agent.knowledge_base:
                state = agent.get_state(prop_id)
                agent_result["states"][prop_id] = state.value

                if state == EpistemicState.CONTRADICTED:
                    result["contradictions"].append({
                        "agent": name,
                        "proposition": prop_id
                    })
                    result["system_valid"] = False

            result["validation_results"][name] = agent_result

        return result

    def compute_consensus(self, proposition_id: str) -> Dict[str, Any]:
        """Berechnet den Konsens über eine Proposition."""
        states = {}
        for name, agent in self.agents.items():
            states[name] = agent.get_state(proposition_id).value

        # Bestimme Mehrheitszustand
        state_counts = {}
        for state in states.values():
            state_counts[state] = state_counts.get(state, 0) + 1

        consensus_state = max(state_counts, key=state_counts.get)
        consensus_strength = state_counts[consensus_state] / len(states) if states else 0

        return {
            "proposition_id": proposition_id,
            "states": states,
            "consensus_state": consensus_state,
            "consensus_strength": consensus_strength,
            "is_consensus": consensus_strength >= 0.7,
        }

    def _log(self, message: str) -> None:
        """Protokolliert eine Systemnachricht."""
        self.system_log.append({
            "timestamp": time.time(),
            "message": message
        })

    def get_system_report(self) -> str:
        """Erstellt einen Systembericht."""
        state = self.validate_system_state()
        report = f"""
=== Deterministisches Epistemisches System: {self.name} ===

Agenten: {state['agent_count']}
Globales Wissen: {state['global_knowledge_count']} Propositionen
Gesamtwissen: {state['total_knowledge']} Propositionen
Gesamtglauben: {state['total_beliefs']} Überzeugungen

System valide: {'JA' if state['system_valid'] else 'NEIN'}
Widersprüche: {len(state['contradictions'])}

"""
        for name, result in state["validation_results"].items():
            report += f"Agent '{name}':\n"
            report += f"  Wissen: {result['knowledge_count']}\n"
            report += f"  Glauben: {result['belief_count']}\n\n"

        return report

    def to_json(self) -> str:
        """Serialisiert das gesamte System als JSON."""
        return json.dumps({
            "name": self.name,
            "agents": {name: agent.to_dict() for name, agent in self.agents.items()},
            "global_knowledge": {k: v.__dict__ for k, v in self.global_knowledge.items()},
            "log": self.system_log[-100:],  # Letzte 100 Einträge
        }, indent=2, default=str)


# ============================================================================
# Beispielverwendung
# ============================================================================

def create_building_compliance_system() -> DeterministicEpistemicSystem:
    """Erstellt ein epistemisches System für Bau-Compliance."""
    system = DeterministicEpistemicSystem("BauCompliance-DES")

    # Erstelle Agenten für verschiedene Rollen
    architect = system.create_agent("Architekt", validation_threshold=0.85)
    engineer = system.create_agent("Ingenieur", validation_threshold=0.90)
    inspector = system.create_agent("Prüfer", validation_threshold=0.95)

    # Füge globales Wissen hinzu (OIB-Richtlinien)
    oib_rl2 = EpistemicProposition(
        content="Brandschutzanforderungen nach OIB-RL 2:2023",
        source="OIB-RL-2",
        confidence=1.0,
        evidence=["Official OIB publication 2023"]
    )
    system.add_global_knowledge(oib_rl2)

    oib_rl6 = EpistemicProposition(
        content="Energieeinsparung nach OIB-RL 6:2023 (HWB ≤ 75 kWh/m²a)",
        source="OIB-RL-6",
        confidence=1.0,
        evidence=["Official OIB publication 2023"]
    )
    system.add_global_knowledge(oib_rl6)

    # Synchronisiere Wissen zu Agenten
    system.sync_agent_knowledge("Architekt")
    system.sync_agent_knowledge("Ingenieur")
    system.sync_agent_knowledge("Prüfer")

    # Füge spezifisches Wissen hinzu
    building_hwb = EpistemicProposition(
        content="Gebäude HWB: 45 kWh/m²a",
        source="Energieberechnung",
        confidence=0.92,
        evidence=["Berechnung nach ÖNORM EN 832"]
    )
    architect.add_knowledge(building_hwb)

    # Erstelle Inferenzregel
    compliance_rule = InferenceRule(
        name="HWB-Compliance-Check",
        premise_ids=[oib_rl6.id, building_hwb.id],
        conclusion_template="Gebäude erfüllt OIB-RL 6 (HWB {} ≤ 75 kWh/m²a)",
        confidence_factor=0.95
    )
    architect.inference_rules.append(compliance_rule)

    return system


if __name__ == "__main__":
    # Demo: Bau-Compliance System
    system = create_building_compliance_system()
    print(system.get_system_report())

    # Validiere Systemzustand
    state = system.validate_system_state()
    print(f"\nSystem valide: {state['system_valid']}")

    # Berechne Konsens
    for prop_id in system.global_knowledge:
        consensus = system.compute_consensus(prop_id)
        print(f"\nKonsens für {prop_id[:8]}...: {consensus['consensus_state']} "
              f"(Stärke: {consensus['consensus_strength']:.2f})")