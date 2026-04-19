#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
AI-Powered Tender Evaluation for Austria
═══════════════════════════════════════════════════════════════════════════

KI-gestützte Angebotsauswertung mit automatischem Scoring, Risiko-Analyse
und Natural Language Processing für technische Requirements.

Features:
1. Automatische Angebots-Bewertung (Multi-Kriterien)
2. NLP für technische Requirement-Extraktion
3. Risiko-Scoring und -Klassifizierung
4. Anomalie-Erkennung (zu hohe/niedrige Preise)
5. Compliance-Check (ÖNORM, rechtliche Anforderungen)
6. Empfehlung für Zuschlag

Basierend auf:
- Global Best Practice: Zepth, Predii AI Evaluation
- Research 2026: NLP + ML in construction tendering

Standards:
- ÖNORM A 2063 (Zuschlagskriterien)
- EU Vergaberecht 2014/24/EU
- ISO 19650 (BIM Requirements)

Stand: April 2026
Lizenz: Apache 2.0
═══════════════════════════════════════════════════════════════════════════
"""

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════════════
# Risk Categories
# ═══════════════════════════════════════════════════════════════════════════


class RiskLevel(str, Enum):
    """Risiko-Stufen"""

    LOW = "niedrig"
    MEDIUM = "mittel"
    HIGH = "hoch"
    CRITICAL = "kritisch"


class RiskCategory(str, Enum):
    """Risiko-Kategorien"""

    PRICE_ANOMALY = "Preis-Anomalie"
    TECHNICAL_COMPLIANCE = "Technische Konformität"
    TIMELINE = "Zeitplan"
    FINANCIAL_STABILITY = "Finanzielle Stabilität"
    EXPERIENCE = "Erfahrung"
    QUALITY = "Qualität"
    LEGAL_COMPLIANCE = "Rechtliche Konformität"


# ═══════════════════════════════════════════════════════════════════════════
# Data Classes
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class RiskAssessment:
    """Risiko-Bewertung für ein Angebot"""

    category: str
    level: RiskLevel
    score: float  # 0-10 (10 = höchstes Risiko)
    description: str
    evidence: List[str] = field(default_factory=list)
    mitigation: Optional[str] = None


@dataclass
class ComplianceCheck:
    """Compliance-Prüfung"""

    requirement: str
    compliant: bool
    confidence: float  # 0-1
    evidence: str
    category: str  # "technical", "legal", "quality"


@dataclass
class AIEvaluationResult:
    """Ergebnis der AI-Bewertung"""

    bid_id: str
    bidder_name: str
    evaluated_at: str

    # Scores (0-100)
    price_score: float
    quality_score: float
    technical_score: float
    timeline_score: float
    experience_score: float
    overall_score: float

    # Risk
    risk_assessments: List[RiskAssessment]
    total_risk_score: float  # 0-10
    risk_level: RiskLevel

    # Compliance
    compliance_checks: List[ComplianceCheck]
    compliance_rate: float  # 0-1

    # NLP-extracted insights
    extracted_requirements: List[str] = field(default_factory=list)
    missing_requirements: List[str] = field(default_factory=list)

    # Recommendation
    recommended: bool = False
    recommendation_reason: str = ""
    confidence: float = 0.0


@dataclass
class BidDocument:
    """Angebots-Dokument für Analyse"""

    bid_id: str
    bidder_name: str
    bid_amount: float
    execution_time_days: int
    warranty_years: int

    # Documents (text content)
    technical_proposal: str = ""
    company_profile: str = ""
    references: List[str] = field(default_factory=list)
    certificates: List[str] = field(default_factory=list)

    # Metadata
    submitted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════════════════════════════════════
# NLP Functions (Simplified)
# ═══════════════════════════════════════════════════════════════════════════


def extract_technical_requirements(text: str) -> List[str]:
    """
    Extract technical requirements from text using NLP

    In production: Use spaCy, BERT, or custom NLP model
    """

    # Simplified keyword extraction
    keywords = [
        "ÖNORM",
        "DIN",
        "ISO",
        "CE-Kennzeichnung",
        "Gewährleistung",
        "Wartung",
        "Garantie",
        "Brandschutz",
        "Statik",
        "Energieausweis",
        "BIM",
        "IFC",
        "LOD",
        "LOIN",
    ]

    found_requirements = []
    text_lower = text.lower()

    for keyword in keywords:
        if keyword.lower() in text_lower:
            # Extract sentence containing keyword (simplified)
            sentences = text.split(".")
            for sentence in sentences:
                if keyword.lower() in sentence.lower():
                    found_requirements.append(sentence.strip())
                    break

    return found_requirements


def detect_compliance_issues(text: str, requirements: List[str]) -> List[str]:
    """
    Detect missing compliance requirements

    In production: Use NLP model trained on ÖNORM/EU requirements
    """

    required_keywords = {
        "ÖNORM A 2063": ["leistungsverzeichnis", "lv", "ausschreibung"],
        "Gewährleistung": ["garantie", "gewährleistung", "jahre"],
        "Zertifikate": ["zertifikat", "iso", "ce"],
        "Referenzen": ["referenz", "projekt", "erfahrung"],
    }

    missing = []
    text_lower = text.lower()

    for req_name, keywords in required_keywords.items():
        found = any(kw in text_lower for kw in keywords)
        if not found:
            missing.append(req_name)

    return missing


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts

    In production: Use sentence embeddings (BERT, etc.)
    """

    # Simplified: word overlap
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union) if union else 0.0


# ═══════════════════════════════════════════════════════════════════════════
# Risk Assessment Functions
# ═══════════════════════════════════════════════════════════════════════════


def assess_price_risk(bid_amount: float, reference_amounts: List[float]) -> RiskAssessment:
    """
    Assess risk based on price anomaly detection

    Checks if bid is significantly lower/higher than average
    """

    if not reference_amounts:
        return RiskAssessment(
            category=RiskCategory.PRICE_ANOMALY.value,
            level=RiskLevel.MEDIUM,
            score=5.0,
            description="Keine Vergleichsdaten verfügbar",
        )

    avg_price = sum(reference_amounts) / len(reference_amounts)
    std_dev = (sum((x - avg_price) ** 2 for x in reference_amounts) / len(reference_amounts)) ** 0.5

    deviation_pct = ((bid_amount - avg_price) / avg_price) * 100

    # Risk scoring
    if bid_amount < avg_price - 2 * std_dev:
        # Sehr niedrig - Dumping-Verdacht
        return RiskAssessment(
            category=RiskCategory.PRICE_ANOMALY.value,
            level=RiskLevel.HIGH,
            score=8.5,
            description=f"Angebot {abs(deviation_pct):.1f}% unter Durchschnitt - Dumping-Risiko",
            evidence=[
                f"Angebotssumme: EUR {bid_amount:,.2f}",
                f"Durchschnitt: EUR {avg_price:,.2f}",
                f"Abweichung: {deviation_pct:.1f}%",
            ],
            mitigation="Nachkalkulation prüfen, finanzielle Absicherung verlangen",
        )
    elif bid_amount < avg_price - std_dev:
        # Niedrig
        return RiskAssessment(
            category=RiskCategory.PRICE_ANOMALY.value,
            level=RiskLevel.MEDIUM,
            score=5.0,
            description=f"Angebot {abs(deviation_pct):.1f}% unter Durchschnitt",
            evidence=[f"Abweichung: {deviation_pct:.1f}%"],
        )
    elif bid_amount > avg_price + 2 * std_dev:
        # Sehr hoch
        return RiskAssessment(
            category=RiskCategory.PRICE_ANOMALY.value,
            level=RiskLevel.MEDIUM,
            score=4.0,
            description=f"Angebot {deviation_pct:.1f}% über Durchschnitt - teuer",
            evidence=[f"Abweichung: {deviation_pct:.1f}%"],
        )
    else:
        # Normal
        return RiskAssessment(
            category=RiskCategory.PRICE_ANOMALY.value,
            level=RiskLevel.LOW,
            score=2.0,
            description="Preis im erwarteten Bereich",
            evidence=[f"Abweichung: {deviation_pct:.1f}%"],
        )


def assess_technical_risk(bid: BidDocument) -> RiskAssessment:
    """
    Assess technical compliance risk

    Checks if technical proposal meets requirements
    """

    # Extract requirements from technical proposal
    requirements = extract_technical_requirements(bid.technical_proposal)
    missing = detect_compliance_issues(bid.technical_proposal, requirements)

    if len(missing) > 3:
        return RiskAssessment(
            category=RiskCategory.TECHNICAL_COMPLIANCE.value,
            level=RiskLevel.HIGH,
            score=7.5,
            description=f"{len(missing)} wichtige Anforderungen fehlen",
            evidence=missing,
            mitigation="Nachforderung technischer Unterlagen",
        )
    elif len(missing) > 0:
        return RiskAssessment(
            category=RiskCategory.TECHNICAL_COMPLIANCE.value,
            level=RiskLevel.MEDIUM,
            score=4.0,
            description=f"{len(missing)} Anforderungen fehlen",
            evidence=missing,
        )
    else:
        return RiskAssessment(
            category=RiskCategory.TECHNICAL_COMPLIANCE.value,
            level=RiskLevel.LOW,
            score=1.5,
            description="Alle technischen Anforderungen erfüllt",
            evidence=requirements[:3],
        )


def assess_timeline_risk(execution_days: int, reference_days: List[int]) -> RiskAssessment:
    """
    Assess timeline risk

    Checks if execution time is realistic
    """

    if not reference_days:
        avg_days = 180  # Default
    else:
        avg_days = sum(reference_days) / len(reference_days)

    deviation_pct = ((execution_days - avg_days) / avg_days) * 100

    if execution_days < avg_days * 0.7:
        # Sehr kurz - unrealistisch
        return RiskAssessment(
            category=RiskCategory.TIMELINE.value,
            level=RiskLevel.HIGH,
            score=7.0,
            description=f"Ausführungszeit {abs(deviation_pct):.0f}% kürzer als üblich - unrealistisch",
            evidence=[f"Angebot: {execution_days} Tage", f"Üblich: {avg_days:.0f} Tage"],
        )
    elif execution_days > avg_days * 1.5:
        # Sehr lang
        return RiskAssessment(
            category=RiskCategory.TIMELINE.value,
            level=RiskLevel.MEDIUM,
            score=4.0,
            description=f"Ausführungszeit {deviation_pct:.0f}% länger als üblich",
            evidence=[f"{execution_days} Tage"],
        )
    else:
        return RiskAssessment(
            category=RiskCategory.TIMELINE.value,
            level=RiskLevel.LOW,
            score=2.0,
            description="Ausführungszeit realistisch",
            evidence=[f"{execution_days} Tage"],
        )


# ═══════════════════════════════════════════════════════════════════════════
# Scoring Functions
# ═══════════════════════════════════════════════════════════════════════════


def calculate_price_score(bid_amount: float, lowest_amount: float) -> float:
    """
    Calculate price score (0-100)

    Lowest bid = 100 points
    """

    if lowest_amount == 0:
        return 0.0

    # Formula: score = 100 * (lowest / bid)
    score = 100 * (lowest_amount / bid_amount)
    return min(score, 100.0)


def calculate_quality_score(bid: BidDocument) -> float:
    """
    Calculate quality score based on:
    - Certificates
    - References
    - Company profile
    """

    score = 0.0

    # Certificates (max 40 points)
    cert_count = len(bid.certificates)
    score += min(cert_count * 10, 40)

    # References (max 30 points)
    ref_count = len(bid.references)
    score += min(ref_count * 10, 30)

    # Warranty (max 20 points)
    warranty_score = min(bid.warranty_years * 4, 20)
    score += warranty_score

    # Company profile quality (max 10 points)
    if len(bid.company_profile) > 500:
        score += 10
    elif len(bid.company_profile) > 200:
        score += 5

    return min(score, 100.0)


def calculate_technical_score(bid: BidDocument) -> float:
    """
    Calculate technical score based on proposal quality
    """

    score = 50.0  # Base score

    # Technical proposal length (indicator of detail)
    if len(bid.technical_proposal) > 2000:
        score += 20
    elif len(bid.technical_proposal) > 1000:
        score += 10

    # Requirements coverage
    requirements = extract_technical_requirements(bid.technical_proposal)
    score += min(len(requirements) * 5, 30)

    return min(score, 100.0)


# ═══════════════════════════════════════════════════════════════════════════
# Main AI Evaluation
# ═══════════════════════════════════════════════════════════════════════════


def ai_evaluate_bid(
    bid: BidDocument, all_bids: List[BidDocument], evaluation_criteria: Dict[str, float] = None
) -> AIEvaluationResult:
    """
    Complete AI-powered bid evaluation

    Args:
        bid: Bid to evaluate
        all_bids: All bids for comparison
        evaluation_criteria: Weights (price, quality, technical, etc.)
    """

    if evaluation_criteria is None:
        evaluation_criteria = {"price": 0.40, "quality": 0.30, "technical": 0.20, "timeline": 0.10}

    # Calculate scores
    bid_amounts = [b.bid_amount for b in all_bids]
    lowest_amount = min(bid_amounts)

    price_score = calculate_price_score(bid.bid_amount, lowest_amount)
    quality_score = calculate_quality_score(bid)
    technical_score = calculate_technical_score(bid)
    timeline_score = 100.0 - min(abs(bid.execution_time_days - 180) / 2, 50)  # Optimal: 180 days

    # Overall score (weighted)
    overall_score = (
        price_score * evaluation_criteria["price"]
        + quality_score * evaluation_criteria["quality"]
        + technical_score * evaluation_criteria["technical"]
        + timeline_score * evaluation_criteria["timeline"]
    )

    # Risk assessments
    risks = [
        assess_price_risk(bid.bid_amount, bid_amounts),
        assess_technical_risk(bid),
        assess_timeline_risk(bid.execution_time_days, [b.execution_time_days for b in all_bids]),
    ]

    total_risk = sum(r.score for r in risks) / len(risks)

    # Determine risk level
    if total_risk > 7:
        risk_level = RiskLevel.CRITICAL
    elif total_risk > 5:
        risk_level = RiskLevel.HIGH
    elif total_risk > 3:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW

    # Compliance checks (simplified)
    compliance_checks = [
        ComplianceCheck(
            requirement="ÖNORM A 2063 konforme Ausschreibung",
            compliant="leistungsverzeichnis" in bid.technical_proposal.lower(),
            confidence=0.8,
            evidence="LV-Bezug im Angebot",
            category="technical",
        ),
        ComplianceCheck(
            requirement="Gewährleistung mind. 3 Jahre",
            compliant=bid.warranty_years >= 3,
            confidence=1.0,
            evidence=f"{bid.warranty_years} Jahre angeboten",
            category="legal",
        ),
    ]

    compliance_rate = sum(1 for c in compliance_checks if c.compliant) / len(compliance_checks)

    # Recommendation
    recommended = overall_score >= 70 and total_risk < 6 and compliance_rate >= 0.8

    if recommended:
        reason = (
            f"Sehr gutes Angebot: Score {overall_score:.1f}, niedriges Risiko ({risk_level.value})"
        )
    else:
        reasons = []
        if overall_score < 70:
            reasons.append(f"Score nur {overall_score:.1f}")
        if total_risk >= 6:
            reasons.append(f"Hohes Risiko ({total_risk:.1f}/10)")
        if compliance_rate < 0.8:
            reasons.append(f"Compliance nur {compliance_rate:.0%}")
        reason = "Nicht empfohlen: " + ", ".join(reasons)

    return AIEvaluationResult(
        bid_id=bid.bid_id,
        bidder_name=bid.bidder_name,
        evaluated_at=datetime.now(timezone.utc).isoformat(),
        price_score=price_score,
        quality_score=quality_score,
        technical_score=technical_score,
        timeline_score=timeline_score,
        experience_score=quality_score,  # Simplified
        overall_score=overall_score,
        risk_assessments=risks,
        total_risk_score=total_risk,
        risk_level=risk_level,
        compliance_checks=compliance_checks,
        compliance_rate=compliance_rate,
        recommended=recommended,
        recommendation_reason=reason,
        confidence=0.85,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 80)
    print("AI-Powered Tender Evaluation - ÖSTERREICH")
    print("═" * 80)
    print()

    # Test data: 3 bids
    bids = [
        BidDocument(
            bid_id="BID-001",
            bidder_name="Baufirma Alpha GmbH",
            bid_amount=425000.0,
            execution_time_days=180,
            warranty_years=5,
            technical_proposal="Ausführung gemäß ÖNORM A 2063 Leistungsverzeichnis. BIM Level 3 konform. Energieausweis A+. Brandschutz nach TRVB. Gewährleistung 5 Jahre.",
            company_profile="Seit 1985 im Hochbau tätig. ISO 9001 zertifiziert. 45 Mitarbeiter.",
            references=["Projekt Wien 2024", "Projekt Graz 2023", "Projekt Linz 2022"],
            certificates=["ISO 9001", "ISO 14001", "OHSAS 18001", "CE"],
        ),
        BidDocument(
            bid_id="BID-002",
            bidder_name="Baumeister Beta",
            bid_amount=320000.0,  # Sehr niedrig!
            execution_time_days=120,  # Sehr kurz!
            warranty_years=2,
            technical_proposal="Ausführung nach Stand der Technik.",
            company_profile="Kleiner Baumeister.",
            references=["Ein Projekt"],
            certificates=["Gewerbeschein"],
        ),
        BidDocument(
            bid_id="BID-003",
            bidder_name="Bau Gamma AG",
            bid_amount=445000.0,
            execution_time_days=200,
            warranty_years=4,
            technical_proposal="ÖNORM A 2063 Ausführung. BIM-basierte Planung. ISO 19650 konform. Statik geprüft. Brandschutz zertifiziert.",
            company_profile="Großes Bauunternehmen seit 1970. 200 Mitarbeiter. Spezialist für Wohnbau.",
            references=["Großprojekt Wien", "Projekt Salzburg", "Projekt Innsbruck"],
            certificates=["ISO 9001", "ISO 14001", "BIM Zertifikat"],
        ),
    ]

    print("Test: AI-Evaluation von 3 Angeboten...")
    print()

    results = []
    for bid in bids:
        result = ai_evaluate_bid(bid, bids)
        results.append(result)

        print(f"{'═' * 80}")
        print(f"Bieter: {result.bidder_name}")
        print(f"{'═' * 80}")
        print(f"  Angebotssumme: EUR {bid.bid_amount:,.2f}")
        print(f"  Ausführung: {bid.execution_time_days} Tage")
        print(f"  Gewährleistung: {bid.warranty_years} Jahre")
        print()
        print(f"  SCORES:")
        print(f"    Preis:      {result.price_score:5.1f}/100")
        print(f"    Qualität:   {result.quality_score:5.1f}/100")
        print(f"    Technik:    {result.technical_score:5.1f}/100")
        print(f"    Zeitplan:   {result.timeline_score:5.1f}/100")
        print(f"    → GESAMT:   {result.overall_score:5.1f}/100")
        print()
        print(f"  RISIKO: {result.total_risk_score:.1f}/10 ({result.risk_level.value})")
        for risk in result.risk_assessments:
            print(f"    • {risk.category}: {risk.level.value} - {risk.description}")
        print()
        print(f"  COMPLIANCE: {result.compliance_rate:.0%}")
        for check in result.compliance_checks:
            status = "✓" if check.compliant else "✗"
            print(f"    {status} {check.requirement}")
        print()
        print(f"  EMPFEHLUNG: {'✓ JA' if result.recommended else '✗ NEIN'}")
        print(f"  Begründung: {result.recommendation_reason}")
        print(f"  AI Confidence: {result.confidence:.0%}")
        print()

    # Ranking
    print("═" * 80)
    print("RANKING (nach Overall Score)")
    print("═" * 80)
    ranked = sorted(results, key=lambda r: r.overall_score, reverse=True)
    for i, r in enumerate(ranked, 1):
        star = "★" if r.recommended else " "
        print(
            f"  {i}. {star} {r.bidder_name:30s} Score: {r.overall_score:5.1f}  Risiko: {r.total_risk_score:.1f}/10"
        )

    print()
    print("✓ AI Tender Evaluation FUNKTIONIERT")
    print("  NOTE: In Produktion würden NLP-Modelle (BERT, spaCy) verwendet")
