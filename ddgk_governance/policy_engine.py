"""
Policy Engine fuer Baumeister-Tool-Austria
Risikobewertung und Policy-Entscheidungen fuer Bau-Berechnungen.

Risk Levels: LOW, MEDIUM, HIGH, CRITICAL
Jede Berechnung wird bewertet und entsprechend behandelt.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
import hashlib


class RiskLevel(Enum):
    """Risikostufen fuer Bau-Berechnungen."""
    LOW = "LOW"          # Standard-Berechnungen, autonom OK
    MEDIUM = "MEDIUM"    # Erhoehte Aufmerksamkeit, Logging erforderlich
    HIGH = "HIGH"        # Kritische Berechnungen, HITL erforderlich
    CRITICAL = "CRITICAL" # Safety-relevant, zwingend HITL + Audit


@dataclass
class PolicyDecision:
    """Entscheidung der Policy-Engine."""
    calculation_type: str
    risk_level: RiskLevel
    allowed_autonomous: bool
    requires_human_approval: bool
    requires_audit: bool
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    policy_hash: str = ""

    def __post_init__(self):
        if not self.policy_hash:
            data = f"{self.calculation_type}:{self.risk_level.value}:{self.timestamp.isoformat()}"
            self.policy_hash = hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict:
        return {
            "calculation_type": self.calculation_type,
            "risk_level": self.risk_level.value,
            "allowed_autonomous": self.allowed_autonomous,
            "requires_human_approval": self.requires_human_approval,
            "requires_audit": self.requires_audit,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "policy_hash": self.policy_hash,
        }


class PolicyEngine:
    """
    Policy-Engine fuer Bau-Berechnungen.

    Bewertet jede Berechnung nach Risiko und trifft Entscheidungen:
    - LOW: Autonome Ausfuehrung erlaubt
    - MEDIUM: Logging erforderlich
    - HIGH: Human-in-the-Loop erforderlich
    - CRITICAL: Zwingend HITL + voller Audit-Trail
    """

    # Policy-Definitionen fuer Bau-Berechnungen
    POLICIES: Dict[str, Dict] = {
        # Structural Engineering - HIGH/CRITICAL
        "schneelast": {"risk": RiskLevel.HIGH, "reason": "Safety-critical: EN 1991-1-3"},
        "windlast": {"risk": RiskLevel.HIGH, "reason": "Safety-critical: EN 1991-1-4"},
        "erdbeben": {"risk": RiskLevel.CRITICAL, "reason": "Safety-critical: EN 1998"},
        "tragwerk": {"risk": RiskLevel.CRITICAL, "reason": "Safety-critical: Structural integrity"},
        "stahlbau_ec3": {"risk": RiskLevel.HIGH, "reason": "Safety-critical: EN 1993"},
        "massivbau_ec2": {"risk": RiskLevel.HIGH, "reason": "Safety-critical: EN 1992"},
        "holzbau_ec5": {"risk": RiskLevel.HIGH, "reason": "Safety-critical: EN 1995"},
        "grundbau_ec7": {"risk": RiskLevel.CRITICAL, "reason": "Safety-critical: EN 1997"},

        # Energy Calculations - MEDIUM
        "heizlast": {"risk": RiskLevel.MEDIUM, "reason": "EN 12831: Comfort, not safety"},
        "kuehllast": {"risk": RiskLevel.MEDIUM, "reason": "Comfort calculation"},
        "hwb_berechnung": {"risk": RiskLevel.MEDIUM, "reason": "OIB-RL 6: Energy compliance"},
        "u_wert": {"risk": RiskLevel.LOW, "reason": "EN ISO 6946: Standard calculation"},

        # Compliance - MEDIUM/HIGH
        "oib_rl2": {"risk": RiskLevel.HIGH, "reason": "Brandschutz: Safety-critical"},
        "oib_rl3": {"risk": RiskLevel.MEDIUM, "reason": "Hygiene: Health relevant"},
        "oib_rl4": {"risk": RiskLevel.HIGH, "reason": "Nutzungssicherheit: Safety"},
        "oib_rl5": {"risk": RiskLevel.MEDIUM, "reason": "Schallschutz: Comfort"},
        "oib_rl6": {"risk": RiskLevel.MEDIUM, "reason": "Energieeinsparung: Compliance"},
        "oib_rl7": {"risk": RiskLevel.LOW, "reason": "Nachhaltigkeit: Documentation"},

        # Other - LOW
        "tageslicht": {"risk": RiskLevel.LOW, "reason": "EN 17037: Comfort"},
        "raumakustik": {"risk": RiskLevel.LOW, "reason": "EN ISO 3382: Comfort"},
        "baukosten": {"risk": RiskLevel.LOW, "reason": "Cost estimation: No safety impact"},
        "gebauehren": {"risk": RiskLevel.LOW, "reason": "Fee calculation: Administrative"},
    }

    def __init__(self):
        self._decision_log: List[PolicyDecision] = []

    def evaluate(self, calculation_type: str, context: Optional[Dict] = None) -> PolicyDecision:
        """
        Bewertet eine Berechnung nach Risiko-Policy.

        Args:
            calculation_type: Typ der Berechnung
            context: Zusaetzlicher Kontext (optional)

        Returns:
            PolicyDecision mit Risikobewertung
        """
        policy = self.POLICIES.get(calculation_type, {
            "risk": RiskLevel.MEDIUM,
            "reason": f"Unknown calculation type: {calculation_type}"
        })

        risk = policy["risk"]
        reason = policy["reason"]

        # Kontext-basierte Anpassung
        if context:
            # Safety-relevant building => hoeheres Risiko
            if context.get("building_class") in ["hochhaus", "krankenhaus", "schule"]:
                if risk == RiskLevel.LOW:
                    risk = RiskLevel.MEDIUM
                elif risk == RiskLevel.MEDIUM:
                    risk = RiskLevel.HIGH
                reason += f" | Building class: {context['building_class']}"

            # Grenzwert-ueberschreitung => CRITICAL
            if context.get("limit_exceeded"):
                risk = RiskLevel.CRITICAL
                reason += " | LIMIT EXCEEDED"

        decision = PolicyDecision(
            calculation_type=calculation_type,
            risk_level=risk,
            allowed_autonomous=risk == RiskLevel.LOW,
            requires_human_approval=risk in (RiskLevel.HIGH, RiskLevel.CRITICAL),
            requires_audit=risk in (RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL),
            reason=reason,
        )

        self._decision_log.append(decision)
        return decision

    def get_decision_log(self) -> List[PolicyDecision]:
        return self._decision_log.copy()

    def get_statistics(self) -> Dict:
        if not self._decision_log:
            return {"total": 0}

        by_risk = {}
        for d in self._decision_log:
            by_risk[d.risk_level.value] = by_risk.get(d.risk_level.value, 0) + 1

        return {
            "total": len(self._decision_log),
            "by_risk": by_risk,
            "autonomous_allowed": by_risk.get("LOW", 0),
            "hitl_required": by_risk.get("HIGH", 0) + by_risk.get("CRITICAL", 0),
        }