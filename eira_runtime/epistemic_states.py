"""
Epistemische States fuer Baumeister-Tool-Austria
Deterministische Zustandsmaschine fuer Bau-Berechnungen.

States: VERIFIED, TRANSITION, INSTABIL, UNKNOWN, ABSTAIN

Jede statische Berechnung (Schneelast, Windlast, Erdbeben, etc.)
durchlaeuft diese States und erhaelt einen epistemischen Status.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any, Dict
import hashlib
import json


class EpistemicState(Enum):
    """
    Epistemische States fuer deterministische Entscheidungsfindung.

    VERIFIED   - Berechnung ist formal verifiziert und sicher
    TRANSITION - Berechnung ist im Uebergang (neue Daten pending)
    INSTABIL   - Berechnung zeigt Instabilitaet (Warnung!)
    UNKNOWN    - Unzureichende Daten fuer Entscheidung
    ABSTAIN    - System verweigert Entscheidung (Safety-First)
    """
    VERIFIED = "VERIFIED"
    TRANSITION = "TRANSITION"
    INSTABIL = "INSTABIL"
    UNKNOWN = "UNKNOWN"
    ABSTAIN = "ABSTAIN"

    @property
    def is_safe(self) -> bool:
        """Ist dieser State sicher fuer autonome Entscheidungen?"""
        return self == EpistemicState.VERIFIED

    @property
    def requires_human(self) -> bool:
        """Benoetigt dieser State menschliche Freigabe?"""
        return self in (EpistemicState.INSTABIL, EpistemicState.UNKNOWN, EpistemicState.ABSTAIN)

    @property
    def color(self) -> str:
        """Farbe fuer UI-Darstellung."""
        colors = {
            EpistemicState.VERIFIED: "#00ff88",    # Gruen
            EpistemicState.TRANSITION: "#00d4ff",  # Blau
            EpistemicState.INSTABIL: "#ffaa00",    # Orange
            EpistemicState.UNKNOWN: "#ff6600",     # Dunkelorange
            EpistemicState.ABSTAIN: "#ff0044",     # Rot
        }
        return colors.get(self, "#888888")

    @property
    def icon(self) -> str:
        """Icon fuer UI-Darstellung."""
        icons = {
            EpistemicState.VERIFIED: "✓",
            EpistemicState.TRANSITION: "↑",
            EpistemicState.INSTABIL: "⚠",
            EpistemicState.UNKNOWN: "?",
            EpistemicState.ABSTAIN: "⛔",
        }
        return icons.get(self, "•")


@dataclass
class StateTransition:
    """
    Repraesentiert einen State-Transition im epistemischen System.

    Jeder Transition wird protokolliert mit Timestamp, Reason und Hash.
    """
    from_state: EpistemicState
    to_state: EpistemicState
    timestamp: datetime = field(default_factory=datetime.utcnow)
    reason: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    transition_hash: str = ""

    def __post_init__(self):
        """Berechne Hash fuer Integritaet."""
        if not self.transition_hash:
            data = f"{self.from_state.value}:{self.to_state.value}:{self.timestamp.isoformat()}:{self.reason}"
            self.transition_hash = hashlib.sha256(data.encode()).hexdigest()[:16]

    @property
    def is_valid(self) -> bool:
        """Ist dieser Transition gueltig?"""
        valid_transitions = {
            EpistemicState.UNKNOWN: [EpistemicState.TRANSITION, EpistemicState.ABSTAIN],
            EpistemicState.TRANSITION: [EpistemicState.VERIFIED, EpistemicState.INSTABIL, EpistemicState.UNKNOWN],
            EpistemicState.INSTABIL: [EpistemicState.VERIFIED, EpistemicState.ABSTAIN, EpistemicState.TRANSITION],
            EpistemicState.VERIFIED: [EpistemicState.TRANSITION],  # Nur bei neuen Daten
            EpistemicState.ABSTAIN: [EpistemicState.UNKNOWN],  # Nur mit neuen Daten
        }
        return self.to_state in valid_transitions.get(self.from_state, [])

    def to_dict(self) -> Dict:
        return {
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
            "context": self.context,
            "transition_hash": self.transition_hash,
            "is_valid": self.is_valid,
        }


@dataclass
class EpistemicDecision:
    """
    Eine epistemische Entscheidung mit vollem Audit-Trail.

    Wird fuer jede Bau-Berechnung erstellt (Schneelast, Windlast, etc.)
    """
    calculation_id: str
    calculation_type: str  # "schneelast", "windlast", "erdbeben", etc.
    state: EpistemicState
    value: Optional[float] = None
    unit: str = ""
    standard: str = ""  # "EN 1991-1-3", "EN 1991-1-4", etc.
    confidence: float = 0.0
    transitions: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    decision_hash: str = ""

    def __post_init__(self):
        if not self.decision_hash:
            data = f"{self.calculation_id}:{self.calculation_type}:{self.state.value}:{self.created_at.isoformat()}"
            self.decision_hash = hashlib.sha256(data.encode()).hexdigest()[:16]

    @property
    def can_actuate(self) -> bool:
        """Darf diese Entscheidung Hardware/Output ausloesen?"""
        return self.state.is_safe and self.confidence >= 0.95

    @property
    def requires_human_approval(self) -> bool:
        """Benoetigt menschliche Freigabe?"""
        return self.state.requires_human or self.confidence < 0.95

    def transition_to(self, new_state: EpistemicState, reason: str = "", context: Optional[Dict] = None) -> Optional[StateTransition]:
        """Fuehre State-Transition durch."""
        transition = StateTransition(
            from_state=self.state,
            to_state=new_state,
            reason=reason,
            context=context or {},
        )
        if transition.is_valid:
            self.transitions.append(transition.to_dict())
            self.state = new_state
            return transition
        return None

    def to_dict(self) -> Dict:
        return {
            "calculation_id": self.calculation_id,
            "calculation_type": self.calculation_type,
            "state": self.state.value,
            "value": self.value,
            "unit": self.unit,
            "standard": self.standard,
            "confidence": self.confidence,
            "can_actuate": self.can_actuate,
            "requires_human_approval": self.requires_human_approval,
            "transitions": self.transitions,
            "created_at": self.created_at.isoformat(),
            "decision_hash": self.decision_hash,
        }

    def __str__(self) -> str:
        return (
            f"EpistemicDecision({self.calculation_type}: "
            f"{self.state.value} {self.icon} | "
            f"{self.value} {self.unit} | "
            f"confidence={self.confidence:.2f})"
        )

    @property
    def icon(self) -> str:
        return self.state.icon