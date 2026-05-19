"""
Compliance Checker fuer Baumeister-Tool-Austria
EU AI Act Compliance und Bau-Normen Pruefung.

Prueft:
- EU AI Act High-Risk Classification
- OIB-RL Konformitaet
- Eurocode Compliance
- Documentation Requirements
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum


class ComplianceStatus(Enum):
    """Compliance-Status."""
    COMPLIANT = "COMPLIANT"
    PARTIAL = "PARTIAL"
    NON_COMPLIANT = "NON_COMPLIANT"
    NOT_ASSESSED = "NOT_ASSESSED"


@dataclass
class EUAIActCompliance:
    """
    EU AI Act Compliance Assessment.

    Baumeister-Tool-Austria ist ein High-Risk AI System gem. Art. 6 + Annex III:
    - Safety component in construction/infrastructure
    - Requires conformity assessment
    - Technical documentation required
    - Human oversight required
    """
    is_high_risk: bool = True
    risk_reason: str = "Safety component in construction (Annex III, Section 2)"
    conformity_assessment_required: bool = True
    technical_documentation: Dict[str, bool] = field(default_factory=lambda: {
        "system_description": False,
        "data_requirements": False,
        "technical_documentation": False,
        "record_keeping": False,
        "human_oversight": False,
        "accuracy_robustness": False,
        "cybersecurity": False,
    })
    human_oversight_implemented: bool = False
    audit_trail_implemented: bool = False
    risk_management_system: bool = False
    assessed_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def overall_compliance(self) -> ComplianceStatus:
        """Gesamt-Compliance-Status."""
        doc_complete = all(self.technical_documentation.values())
        if doc_complete and self.human_oversight_implemented and self.audit_trail_implemented:
            return ComplianceStatus.COMPLIANT
        elif any(self.technical_documentation.values()):
            return ComplianceStatus.PARTIAL
        return ComplianceStatus.NON_COMPLIANT

    def to_dict(self) -> Dict:
        return {
            "is_high_risk": self.is_high_risk,
            "risk_reason": self.risk_reason,
            "conformity_assessment_required": self.conformity_assessment_required,
            "technical_documentation": self.technical_documentation,
            "human_oversight_implemented": self.human_oversight_implemented,
            "audit_trail_implemented": self.audit_trail_implemented,
            "risk_management_system": self.risk_management_system,
            "overall_compliance": self.overall_compliance.value,
            "assessed_at": self.assessed_at.isoformat(),
        }


@dataclass
class ComplianceReport:
    """Compliance-Bericht fuer eine Berechnung."""
    calculation_id: str
    calculation_type: str
    oib_rl_compliant: bool
    eurocode_compliant: bool
    eu_ai_act: EUAIActCompliance
    missing_requirements: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def overall_status(self) -> ComplianceStatus:
        if self.oib_rl_compliant and self.eurocode_compliant and self.eu_ai_act.overall_compliance == ComplianceStatus.COMPLIANT:
            return ComplianceStatus.COMPLIANT
        elif self.oib_rl_compliant or self.eurocode_compliant:
            return ComplianceStatus.PARTIAL
        return ComplianceStatus.NON_COMPLIANT

    def to_dict(self) -> Dict:
        return {
            "calculation_id": self.calculation_id,
            "calculation_type": self.calculation_type,
            "oib_rl_compliant": self.oib_rl_compliant,
            "eurocode_compliant": self.eurocode_compliant,
            "eu_ai_act": self.eu_ai_act.to_dict(),
            "missing_requirements": self.missing_requirements,
            "recommendations": self.recommendations,
            "overall_status": self.overall_status.value,
            "assessed_at": self.assessed_at.isoformat(),
        }


class ComplianceChecker:
    """
    Compliance-Checker fuer Bau-Berechnungen.

    Prueft:
    - OIB-RL Konformitaet
    - Eurocode Compliance
    - EU AI Act Requirements
    """

    def __init__(self):
        self._reports: List[ComplianceReport] = []
        self._eu_ai_act = EUAIActCompliance()

    def check_calculation(
        self,
        calculation_id: str,
        calculation_type: str,
        result: Dict[str, Any],
        input_data: Dict[str, Any],
    ) -> ComplianceReport:
        """Prueft eine Berechnung auf Compliance."""
        missing = []
        recommendations = []

        # OIB-RL Pruefung
        oib_compliant = self._check_oib_rl(calculation_type, result, missing, recommendations)

        # Eurocode Pruefung
        eurocode_compliant = self._check_eurocode(calculation_type, result, missing, recommendations)

        report = ComplianceReport(
            calculation_id=calculation_id,
            calculation_type=calculation_type,
            oib_rl_compliant=oib_compliant,
            eurocode_compliant=eurocode_compliant,
            eu_ai_act=self._eu_ai_act,
            missing_requirements=missing,
            recommendations=recommendations,
        )

        self._reports.append(report)
        return report

    def _check_oib_rl(
        self,
        calculation_type: str,
        result: Dict,
        missing: List[str],
        recommendations: List[str],
    ) -> bool:
        """Prueft OIB-RL Konformitaet."""
        oib_mappings = {
            "oib_rl2": "Brandschutz",
            "oib_rl3": "Hygiene",
            "oib_rl4": "Nutzungssicherheit",
            "oib_rl5": "Schallschutz",
            "oib_rl6": "Energieeinsparung",
            "oib_rl7": "Nachhaltigkeit",
        }

        if calculation_type in oib_mappings:
            if not result.get("oib_compliant", False):
                missing.append(f"OIB-RL nicht erfuellt: {oib_mappings[calculation_type]}")
                return False
        return True

    def _check_eurocode(
        self,
        calculation_type: str,
        result: Dict,
        missing: List[str],
        recommendations: List[str],
    ) -> bool:
        """Prueft Eurocode Compliance."""
        ec_mappings = {
            "stahlbau_ec3": "EN 1993",
            "massivbau_ec2": "EN 1992",
            "holzbau_ec5": "EN 1995",
            "grundbau_ec7": "EN 1997",
            "erdbeben": "EN 1998",
            "schneelast": "EN 1991-1-3",
            "windlast": "EN 1991-1-4",
        }

        if calculation_type in ec_mappings:
            utilization = result.get("utilization", 0)
            if utilization > 1.0:
                missing.append(f"Utilization > 1.0 ({utilization:.2f}) - {ec_mappings[calculation_type]}")
                recommendations.append("Querschnitt vergroessern oder Material upgrade")
                return False
            elif utilization > 0.9:
                recommendations.append(f"Utilization nahe Limit ({utilization:.2f}) - pruefen")
        return True

    def get_reports(self) -> List[ComplianceReport]:
        return self._reports.copy()

    def get_eu_ai_act_status(self) -> EUAIActCompliance:
        return self._eu_ai_act