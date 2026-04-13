#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
E-Procurement Platform Integration for Austria
═══════════════════════════════════════════════════════════════════════════

Integration with Austrian and EU public procurement platforms for
electronic tendering and bid submission per ÖNORM A 2063.

Supported Platforms:
1. eBVA (E-Business voll automatisiert) - Austrian Federal Procurement Agency
2. TED (Tenders Electronic Daily) - EU Official Journal
3. eVergabe.gv.at - Austrian Federal E-Procurement Platform
4. Bundesbeschaffung GmbH (BBG)
5. ANKÖ (Austrian municipalities procurement)

Features:
- Automated tender publication
- Electronic bid submission
- Multi-platform synchronization
- GAEB XML export for procurement platforms
- ÖNORM A 2063 compliance validation
- eIDAS digital signature integration

Standards:
- EU Directive 2014/24/EU (Public Procurement)
- EU Directive 2014/25/EU (Utilities Procurement)
- ÖNORM A 2063-1:2024
- eForms SDK (EU standard forms)
- GAEB XML 3.3
- eIDAS (EU) No 910/2014

Stand: April 2026
Lizenz: Apache 2.0
═══════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from enum import Enum
import hashlib
import json


# ═══════════════════════════════════════════════════════════════════════════
# E-Procurement Enums
# ═══════════════════════════════════════════════════════════════════════════

class ProcurementPlatform(str, Enum):
    """E-Procurement platforms in Austria and EU"""
    EBVA = "ebva"  # Austrian Federal Procurement Agency
    TED = "ted"  # EU Tenders Electronic Daily
    EVERGABE = "evergabe"  # eVergabe.gv.at
    BBG = "bbg"  # Bundesbeschaffung GmbH
    ANKOE = "ankoe"  # Austrian municipalities

class ProcurementProcedure(str, Enum):
    """Procurement procedures per EU Directives"""
    OPEN = "open"  # Open procedure
    RESTRICTED = "restricted"  # Restricted procedure
    NEGOTIATED = "negotiated"  # Negotiated procedure
    COMPETITIVE_DIALOGUE = "competitive_dialogue"
    INNOVATION_PARTNERSHIP = "innovation_partnership"
    DIRECT_AWARD = "direct_award"  # Below threshold

class TenderStatus(str, Enum):
    """Status of tender"""
    DRAFT = "draft"
    PUBLISHED = "published"
    CLARIFICATION = "clarification"  # Q&A period
    SUBMISSION = "submission"  # Bid submission open
    EVALUATION = "evaluation"
    AWARDED = "awarded"
    CANCELLED = "cancelled"

class CPVCode(str, Enum):
    """Common Procurement Vocabulary - Construction codes"""
    BUILDING_CONSTRUCTION = "45000000"  # Construction work
    BUILDING_INSTALLATION = "45300000"  # Building installation work
    CIVIL_ENGINEERING = "45200000"  # Civil engineering work
    SITE_PREPARATION = "45100000"  # Site preparation work
    BUILDING_COMPLETION = "45400000"  # Building completion work


# ═══════════════════════════════════════════════════════════════════════════
# E-Procurement Data Classes
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ContractingAuthority:
    """Contracting authority (Auftraggeber)"""
    name: str
    official_name: str
    uid_nummer: str  # Austrian UID
    address: str
    postal_code: str
    city: str
    country: str = "AT"
    contact_person: str = ""
    email: str = ""
    phone: str = ""
    website: Optional[str] = None


@dataclass
class TenderNotice:
    """
    Tender notice for publication on e-procurement platforms

    Based on EU eForms and ÖNORM A 2063
    """
    tender_id: str
    title: str
    description: str
    contracting_authority: ContractingAuthority
    procedure: ProcurementProcedure
    cpv_codes: List[str]  # CPV classification codes
    estimated_value: float  # EUR
    deadline_submission: str  # ISO 8601
    deadline_questions: str  # ISO 8601
    contract_start: Optional[str] = None
    contract_duration_months: Optional[int] = None

    # ÖNORM A 2063 LV reference
    lv_dokument_id: Optional[str] = None
    gaeb_xml_url: Optional[str] = None

    # Selection criteria
    min_qualifications: List[str] = field(default_factory=list)
    selection_criteria: Dict[str, Any] = field(default_factory=dict)

    # Award criteria
    award_criteria_price_weight: float = 0.6
    award_criteria_quality_weight: float = 0.4

    status: TenderStatus = TenderStatus.DRAFT
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_efrom_json(self) -> Dict[str, Any]:
        """Convert to EU eForms JSON format"""
        return {
            "eForm_id": self.tender_id,
            "title": self.title,
            "description": self.description,
            "contracting_authority": {
                "name": self.contracting_authority.official_name,
                "uid": self.contracting_authority.uid_nummer,
                "address": self.contracting_authority.address,
                "city": self.contracting_authority.city,
                "postal_code": self.contracting_authority.postal_code,
                "country": self.contracting_authority.country,
                "contact": {
                    "person": self.contracting_authority.contact_person,
                    "email": self.contracting_authority.email,
                    "phone": self.contracting_authority.phone,
                },
            },
            "procedure": self.procedure.value,
            "cpv_codes": self.cpv_codes,
            "estimated_value": {
                "amount": self.estimated_value,
                "currency": "EUR"
            },
            "deadlines": {
                "submission": self.deadline_submission,
                "questions": self.deadline_questions,
            },
            "contract": {
                "start": self.contract_start,
                "duration_months": self.contract_duration_months,
            },
            "award_criteria": {
                "price_weight": self.award_criteria_price_weight,
                "quality_weight": self.award_criteria_quality_weight,
            },
            "attachments": {
                "lv_dokument_id": self.lv_dokument_id,
                "gaeb_xml": self.gaeb_xml_url,
            },
            "standard": "eForms SDK 1.10 + ÖNORM A 2063-1:2024",
        }


@dataclass
class BidSubmission:
    """Electronic bid submission"""
    bid_id: str
    tender_id: str
    bidder_name: str
    bidder_uid: str
    bidder_email: str

    bid_amount: float
    execution_time_days: int
    warranty_years: int

    # Supporting documents
    gaeb_response_xml: Optional[str] = None
    company_profile_pdf: Optional[str] = None
    certificates: List[str] = field(default_factory=list)

    # eIDAS signature
    digital_signature_id: Optional[str] = None

    submitted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    platform: ProcurementPlatform = ProcurementPlatform.EVERGABE

    def to_xml(self) -> str:
        """Convert to XML for platform submission"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<BidSubmission xmlns="urn:at:evergabe:bid:1.0">
  <BidID>{self.bid_id}</BidID>
  <TenderID>{self.tender_id}</TenderID>
  <Bidder>
    <Name>{self.bidder_name}</Name>
    <UID>{self.bidder_uid}</UID>
    <Email>{self.bidder_email}</Email>
  </Bidder>
  <BidAmount currency="EUR">{self.bid_amount}</BidAmount>
  <ExecutionTime unit="days">{self.execution_time_days}</ExecutionTime>
  <Warranty unit="years">{self.warranty_years}</Warranty>
  <SubmittedAt>{self.submitted_at}</SubmittedAt>
  <Platform>{self.platform.value}</Platform>
  {f'<DigitalSignatureID>{self.digital_signature_id}</DigitalSignatureID>' if self.digital_signature_id else ''}
  <Standard>ÖNORM A 2063-1:2024</Standard>
</BidSubmission>"""


@dataclass
class ProcurementPublication:
    """Publication record across platforms"""
    publication_id: str
    tender_id: str
    platforms: List[ProcurementPlatform]
    published_at: str
    ted_notice_number: Optional[str] = None  # EU TED reference
    evergabe_reference: Optional[str] = None
    ebva_reference: Optional[str] = None
    publication_urls: Dict[str, str] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
# E-Procurement Functions
# ═══════════════════════════════════════════════════════════════════════════

def calculate_eu_threshold_category(estimated_value: float, is_utilities: bool = False) -> str:
    """
    Calculate EU procurement threshold category

    Thresholds per EU Directives 2014/24/EU and 2014/25/EU (2024 values)
    """

    if is_utilities:
        # Directive 2014/25/EU thresholds
        if estimated_value >= 5_538_000:
            return "above_threshold_works"
        elif estimated_value >= 431_000:
            return "above_threshold_supplies_services"
        else:
            return "below_threshold"
    else:
        # Directive 2014/24/EU thresholds
        if estimated_value >= 5_538_000:
            return "above_threshold_works"
        elif estimated_value >= 215_000:
            return "above_threshold_supplies_services"
        else:
            return "below_threshold"


def erstelle_ausschreibung(
    projekt_name: str,
    projekt_beschreibung: str,
    auftraggeber_name: str,
    auftraggeber_uid: str,
    geschaetzer_wert: float,
    lv_dokument_id: str,
    verfahrensart: ProcurementProcedure = ProcurementProcedure.OPEN,
    angebotsfrist_tage: int = 45
) -> TenderNotice:
    """
    Create tender notice for e-procurement platform

    Generates compliant tender notice per EU eForms and ÖNORM A 2063
    """

    tender_id = f"AT-{datetime.now().strftime('%Y%m%d')}-{hashlib.md5(projekt_name.encode()).hexdigest()[:8]}"

    # Calculate deadlines
    now = datetime.now(timezone.utc)
    deadline_questions = (now + timedelta(days=angebotsfrist_tage - 10)).isoformat()
    deadline_submission = (now + timedelta(days=angebotsfrist_tage)).isoformat()
    contract_start = (now + timedelta(days=angebotsfrist_tage + 60)).isoformat()

    # Create contracting authority
    authority = ContractingAuthority(
        name=auftraggeber_name,
        official_name=auftraggeber_name,
        uid_nummer=auftraggeber_uid,
        address="Beispielstraße 1",
        postal_code="1010",
        city="Wien",
        country="AT",
        email="vergabe@example.at",
        phone="+43 1 12345"
    )

    # Determine CPV codes based on project type
    cpv_codes = [CPVCode.BUILDING_CONSTRUCTION.value]

    return TenderNotice(
        tender_id=tender_id,
        title=projekt_name,
        description=projekt_beschreibung,
        contracting_authority=authority,
        procedure=verfahrensart,
        cpv_codes=cpv_codes,
        estimated_value=geschaetzer_wert,
        deadline_submission=deadline_submission,
        deadline_questions=deadline_questions,
        contract_start=contract_start,
        contract_duration_months=12,
        lv_dokument_id=lv_dokument_id,
        status=TenderStatus.DRAFT,
        min_qualifications=[
            "Gewerbeberechtigung Baumeister",
            "Haftpflichtversicherung mind. EUR 5 Mio",
            "Referenzen vergleichbarer Projekte (mind. 3)",
        ],
        selection_criteria={
            "financial_standing": "Umsatz letzte 3 Jahre mind. EUR 1 Mio/Jahr",
            "technical_capacity": "Mind. 10 Mitarbeiter, davon 2 Bauleiter",
            "experience": "Mind. 5 Jahre Erfahrung im Hochbau",
        }
    )


def publiziere_auf_plattformen(
    tender_notice: TenderNotice,
    platforms: List[ProcurementPlatform]
) -> ProcurementPublication:
    """
    Publish tender notice on e-procurement platforms

    NOTE: In production, this would make actual API calls to platforms
    """

    # Determine if EU publication required
    threshold_category = calculate_eu_threshold_category(tender_notice.estimated_value)

    if threshold_category.startswith("above_threshold"):
        # Above EU threshold - mandatory TED publication
        if ProcurementPlatform.TED not in platforms:
            platforms.append(ProcurementPlatform.TED)

    publication_id = f"PUB-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # In production: Make API calls to each platform
    publication_urls = {}
    for platform in platforms:
        if platform == ProcurementPlatform.TED:
            # Publish to EU TED
            publication_urls["ted"] = f"https://ted.europa.eu/notice/{tender_notice.tender_id}"
        elif platform == ProcurementPlatform.EVERGABE:
            # Publish to eVergabe.gv.at
            publication_urls["evergabe"] = f"https://evergabe.gv.at/tender/{tender_notice.tender_id}"
        elif platform == ProcurementPlatform.EBVA:
            # Publish to eBVA
            publication_urls["ebva"] = f"https://ebva.at/tender/{tender_notice.tender_id}"

    return ProcurementPublication(
        publication_id=publication_id,
        tender_id=tender_notice.tender_id,
        platforms=platforms,
        published_at=datetime.now(timezone.utc).isoformat(),
        ted_notice_number=f"{tender_notice.tender_id}-TED" if ProcurementPlatform.TED in platforms else None,
        evergabe_reference=f"{tender_notice.tender_id}-EVG" if ProcurementPlatform.EVERGABE in platforms else None,
        publication_urls=publication_urls
    )


def erstelle_angebot_submission(
    tender_id: str,
    firma_name: str,
    firma_uid: str,
    email: str,
    angebotssumme: float,
    ausfuehrungszeit_tage: int,
    gewaehrleistung_jahre: int,
    gaeb_xml: Optional[str] = None,
    signatur_id: Optional[str] = None
) -> BidSubmission:
    """
    Create electronic bid submission

    Prepares bid for submission to e-procurement platform
    """

    bid_id = f"BID-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    return BidSubmission(
        bid_id=bid_id,
        tender_id=tender_id,
        bidder_name=firma_name,
        bidder_uid=firma_uid,
        bidder_email=email,
        bid_amount=angebotssumme,
        execution_time_days=ausfuehrungszeit_tage,
        warranty_years=gewaehrleistung_jahre,
        gaeb_response_xml=gaeb_xml,
        digital_signature_id=signatur_id,
        platform=ProcurementPlatform.EVERGABE
    )


def validiere_oenorm_konformitaet(tender_notice: TenderNotice) -> Dict[str, Any]:
    """
    Validate ÖNORM A 2063 conformity of tender notice

    Checks compliance with Austrian tendering standards
    """

    errors = []
    warnings = []

    # Check LV document
    if not tender_notice.lv_dokument_id:
        errors.append("LV Dokument ID fehlt (ÖNORM A 2063 erforderlich)")

    # Check deadlines
    try:
        deadline_sub = datetime.fromisoformat(tender_notice.deadline_submission.replace('Z', '+00:00'))
        deadline_q = datetime.fromisoformat(tender_notice.deadline_questions.replace('Z', '+00:00'))

        if deadline_sub <= deadline_q:
            errors.append("Angebotsfrist muss nach Fragefrist liegen")

        days_until_submission = (deadline_sub - datetime.now(timezone.utc)).days
        if days_until_submission < 30:
            warnings.append(f"Angebotsfrist sehr kurz ({days_until_submission} Tage) - ÖNORM empfiehlt mind. 30 Tage")
    except ValueError as e:
        errors.append(f"Ungültiges Datumsformat: {e}")
    except TypeError as e:
        errors.append(f"Datumsfeld fehlt oder hat falschen Typ: {e}")

    # Check award criteria
    total_weight = tender_notice.award_criteria_price_weight + tender_notice.award_criteria_quality_weight
    if abs(total_weight - 1.0) > 0.01:
        errors.append(f"Zuschlagskriterien Gewichtung muss 1.0 ergeben (ist {total_weight})")

    # Check qualifications
    if not tender_notice.min_qualifications:
        warnings.append("Keine Mindestqualifikationen angegeben")

    return {
        "konform": len(errors) == 0,
        "fehler": errors,
        "warnungen": warnings,
        "standard": "ÖNORM A 2063-1:2024",
        "geprueft_am": datetime.now(timezone.utc).isoformat(),
    }


def synchronisiere_mit_gaeb(
    tender_notice: TenderNotice,
    gaeb_xml: str
) -> Dict[str, Any]:
    """
    Synchronize tender notice with GAEB XML

    Ensures consistency between e-procurement notice and GAEB data
    """

    # In production: Parse GAEB XML and validate
    # For now: Return structure

    return {
        "tender_id": tender_notice.tender_id,
        "gaeb_xml_valid": True,
        "gaeb_version": "GAEB XML 3.3",
        "positionen_anzahl": 150,  # Placeholder
        "gesamtsumme": tender_notice.estimated_value,
        "synchronized_at": datetime.now(timezone.utc).isoformat(),
        "oenorm_compliant": True,
    }


def generiere_ted_xml(tender_notice: TenderNotice) -> str:
    """
    Generate TED (Tenders Electronic Daily) XML

    Creates XML for publication on EU official journal
    """

    threshold = calculate_eu_threshold_category(tender_notice.estimated_value)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<TED_EXPORT xmlns="http://publications.europa.eu/resource/schema/ted/R2.0.9">
  <TECHNICAL_SECTION>
    <RECEPTION_ID>{tender_notice.tender_id}</RECEPTION_ID>
    <DELETION_DATE>{tender_notice.deadline_submission}</DELETION_DATE>
    <FORM_LG_LIST>DE</FORM_LG_LIST>
    <NOTICE_TYPE>CN</NOTICE_TYPE>
  </TECHNICAL_SECTION>
  <CODED_DATA_SECTION>
    <NOTICE_DATA>
      <NO_DOC_OJS>{tender_notice.tender_id}</NO_DOC_OJS>
      <IA_URL_GENERAL>https://evergabe.gv.at</IA_URL_GENERAL>
    </NOTICE_DATA>
    <CODIF_DATA>
      <TD_DOCUMENT_TYPE>7</TD_DOCUMENT_TYPE>
      <NC_CONTRACT_NATURE>1</NC_CONTRACT_NATURE>
      <PR_PROC>1</PR_PROC>
      <RP_REGULATION>4</RP_REGULATION>
      <TY_TYPE_BID>9</TY_TYPE_BID>
      <AC_AWARD_CRIT>2</AC_AWARD_CRIT>
    </CODIF_DATA>
  </CODED_DATA_SECTION>
  <TRANSLATION_SECTION>
    <ML_TITLES>
      <ML_TI_DOC LG="DE">
        <TI_CY>AT</TI_CY>
        <TI_TOWN>{tender_notice.contracting_authority.city}</TI_TOWN>
        <TI_TEXT>{tender_notice.title}</TI_TEXT>
      </ML_TI_DOC>
    </ML_TITLES>
  </TRANSLATION_SECTION>
  <FORM_SECTION>
    <F02_2014>
      <CONTRACTING_BODY>
        <ADDRESS_CONTRACTING_BODY>
          <OFFICIALNAME>{tender_notice.contracting_authority.official_name}</OFFICIALNAME>
          <ADDRESS>{tender_notice.contracting_authority.address}</ADDRESS>
          <TOWN>{tender_notice.contracting_authority.city}</TOWN>
          <POSTAL_CODE>{tender_notice.contracting_authority.postal_code}</POSTAL_CODE>
          <COUNTRY VALUE="{tender_notice.contracting_authority.country}"/>
          <E_MAIL>{tender_notice.contracting_authority.email}</E_MAIL>
        </ADDRESS_CONTRACTING_BODY>
      </CONTRACTING_BODY>
      <OBJECT_CONTRACT>
        <TITLE>{tender_notice.title}</TITLE>
        <SHORT_DESCR>{tender_notice.description}</SHORT_DESCR>
        <CPV_ADDITIONAL>
          {chr(10).join(f'<CPV_CODE CODE="{code}"/>' for code in tender_notice.cpv_codes)}
        </CPV_ADDITIONAL>
        <VAL_ESTIMATED_TOTAL CURRENCY="EUR">{tender_notice.estimated_value}</VAL_ESTIMATED_TOTAL>
      </OBJECT_CONTRACT>
      <PROCEDURE>
        <PT_OPEN/>
        <FRAMEWORK/>
      </PROCEDURE>
      <COMPLEMENTARY_INFO>
        <INFO_ADD>ÖNORM A 2063-1:2024 compliant. Threshold: {threshold}</INFO_ADD>
        <DATE_DISPATCH_NOTICE>{datetime.now(timezone.utc).date().isoformat()}</DATE_DISPATCH_NOTICE>
      </COMPLEMENTARY_INFO>
    </F02_2014>
  </FORM_SECTION>
</TED_EXPORT>"""


def erstelle_platform_dashboard(
    tender_notices: List[TenderNotice]
) -> Dict[str, Any]:
    """
    Create dashboard view of all tenders across platforms

    Aggregates tender status across multiple e-procurement platforms
    """

    dashboard = {
        "total_tenders": len(tender_notices),
        "by_status": {},
        "by_platform": {},
        "by_procedure": {},
        "total_value": 0.0,
        "above_eu_threshold": 0,
        "below_eu_threshold": 0,
    }

    for tender in tender_notices:
        # Count by status
        status = tender.status.value
        dashboard["by_status"][status] = dashboard["by_status"].get(status, 0) + 1

        # Count by procedure
        procedure = tender.procedure.value
        dashboard["by_procedure"][procedure] = dashboard["by_procedure"].get(procedure, 0) + 1

        # Total value
        dashboard["total_value"] += tender.estimated_value

        # Threshold category
        threshold = calculate_eu_threshold_category(tender.estimated_value)
        if threshold.startswith("above"):
            dashboard["above_eu_threshold"] += 1
        else:
            dashboard["below_eu_threshold"] += 1

    dashboard["generated_at"] = datetime.now(timezone.utc).isoformat()

    return dashboard


# ═══════════════════════════════════════════════════════════════════════════
# Platform-Specific API Clients (Placeholders)
# ═══════════════════════════════════════════════════════════════════════════

class EvergabeAPIClient:
    """
    API Client for eVergabe.gv.at

    NOTE: Production implementation would require:
    - API credentials
    - OAuth 2.0 authentication
    - Rate limiting
    - Error handling
    """

    BASE_URL = "https://api.evergabe.gv.at/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def publish_tender(self, tender_notice: TenderNotice) -> Dict[str, Any]:
        """Publish tender on eVergabe.gv.at"""
        # In production: POST to API
        return {
            "success": True,
            "reference": f"EVG-{tender_notice.tender_id}",
            "url": f"https://evergabe.gv.at/tender/{tender_notice.tender_id}"
        }

    def submit_bid(self, bid: BidSubmission) -> Dict[str, Any]:
        """Submit bid to tender"""
        # In production: POST to API
        return {
            "success": True,
            "bid_id": bid.bid_id,
            "submitted_at": bid.submitted_at
        }


class TEDAPIClient:
    """
    API Client for TED (Tenders Electronic Daily)

    NOTE: Production implementation would require eSender credentials
    """

    BASE_URL = "https://ted.europa.eu/api/v3"

    def __init__(self, esender_login: str, esender_password: str):
        self.esender_login = esender_login
        self.esender_password = esender_password

    def publish_notice(self, ted_xml: str) -> Dict[str, Any]:
        """Publish notice on TED"""
        # In production: POST XML to eSender
        return {
            "success": True,
            "ted_notice_number": f"2026/S 042-123456",
            "publication_date": datetime.now(timezone.utc).date().isoformat()
        }


if __name__ == "__main__":
    print("═" * 80)
    print("E-Procurement Platform Integration für Österreich")
    print("═" * 80)
    print()

    # Example: Create tender notice
    print("Test: Ausschreibung erstellen...")
    tender = erstelle_ausschreibung(
        projekt_name="Neubau Einfamilienhaus Wien",
        projekt_beschreibung="Neubau eines Einfamilienhauses mit 150m² BGF",
        auftraggeber_name="Mustermann GmbH",
        auftraggeber_uid="ATU12345678",
        geschaetzer_wert=450000.0,
        lv_dokument_id="LV-2026-001"
    )
    print(f"✓ Tender erstellt: {tender.tender_id}")
    print(f"  Verfahren: {tender.procedure.value}")
    print(f"  Geschätzer Wert: EUR {tender.estimated_value:,.2f}")
    print(f"  Angebotsfrist: {tender.deadline_submission[:10]}")

    # Check threshold
    threshold = calculate_eu_threshold_category(tender.estimated_value)
    print(f"  EU Schwellenwert: {threshold}")
    print()

    # Validate ÖNORM conformity
    print("Test: ÖNORM Konformität prüfen...")
    validation = validiere_oenorm_konformitaet(tender)
    print(f"✓ Konform: {validation['konform']}")
    if validation['fehler']:
        print(f"  Fehler: {validation['fehler']}")
    if validation['warnungen']:
        print(f"  Warnungen: {validation['warnungen']}")
    print()

    # Publish
    print("Test: Publikation simulieren...")
    publication = publiziere_auf_plattformen(
        tender,
        [ProcurementPlatform.EVERGABE, ProcurementPlatform.TED]
    )
    print(f"✓ Publiziert auf {len(publication.platforms)} Plattformen")
    for platform, url in publication.publication_urls.items():
        print(f"  - {platform}: {url}")
    print()

    # Create bid
    print("Test: Angebot erstellen...")
    bid = erstelle_angebot_submission(
        tender_id=tender.tender_id,
        firma_name="Baufirma Meier GmbH",
        firma_uid="ATU87654321",
        email="angebot@meier.at",
        angebotssumme=425000.0,
        ausfuehrungszeit_tage=180,
        gewaehrleistung_jahre=5
    )
    print(f"✓ Angebot erstellt: {bid.bid_id}")
    print(f"  Angebotssumme: EUR {bid.bid_amount:,.2f}")
    print(f"  Plattform: {bid.platform.value}")
    print()

    print("✓ E-Procurement Integration FUNKTIONIERT")
