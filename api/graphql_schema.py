#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
GraphQL API Schema for ÖNORM A 2063 Tendering
═══════════════════════════════════════════════════════════════════════════

Advanced GraphQL interface for complex queries, real-time subscriptions,
and nested data access for Austrian construction tendering.

Features:
1. Complex nested queries (LV → Positionen → Bids → Bidders)
2. Real-time subscriptions for bid updates
3. Mutations for LV generation and bid submission
4. Filtering, sorting, pagination
5. ISO 19650 BIM data integration
6. eIDAS signature verification

Standards:
- GraphQL Specification (June 2018)
- ÖNORM A 2063-1:2024
- ISO 19650 series
- eIDAS (EU) No 910/2014

Stand: April 2026
Lizenz: Apache 2.0
═══════════════════════════════════════════════════════════════════════════
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json

try:
    import strawberry
    from strawberry.types import Info
    from strawberry.schema.config import StrawberryConfig

    GRAPHQL_AVAILABLE = True
except ImportError:
    GRAPHQL_AVAILABLE = False

    # Fallback type definitions for when strawberry is not installed
    def _passthrough(cls):
        return cls

    class Info:
        """Fallback Info type"""

        def __init__(self):
            self.context = {}

    class strawberry:
        type = staticmethod(_passthrough)
        field = staticmethod(lambda func=None, **kwargs: func if func else lambda f: f)
        input = staticmethod(_passthrough)
        mutation = staticmethod(_passthrough)
        subscription = staticmethod(_passthrough)

    class StrawberryConfig:
        def __init__(self, **kwargs):
            pass


# Import from existing modules
try:
    from orion_oenorm_a2063 import (
        generiere_beispiel_lv_einfamilienhaus,
        berechne_regionale_anpassung,
        vergleiche_angebote_mehrkriteriell,
        Bundesland,
    )
    from iso_19650_bim import (
        erstelle_eir_template_oesterreich,
        erstelle_air_template,
        InformationDeliveryMilestone,
    )
    from eidas_signature import (
        signiere_oenorm_lv,
        verifiziere_signatur,
        DigitalSignature as EidasSignature,
        SignatureStatus,
    )

    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════
# GraphQL Types - Austrian Tendering Domain
# ═══════════════════════════════════════════════════════════════════════════


@strawberry.type
class Position:
    """Single position in Bill of Quantities (LV)"""

    oz: str
    bezeichnung: str
    einheit: str
    menge: float
    einheitspreis_basis: float
    gesamtpreis_basis: float
    leistungsgruppe: str
    kurzbeschreibung: Optional[str] = None
    abfall_kg: Optional[float] = None
    regional_faktor: Optional[float] = None

    @strawberry.field
    def gesamtpreis_formatted(self) -> str:
        """Formatted total price"""
        return f"€ {self.gesamtpreis_basis:,.2f}"


@strawberry.type
class Leistungsverzeichnis:
    """Bill of Quantities per ÖNORM A 2063"""

    dokument_id: str
    projekt_name: str
    projekt_ort: str
    auftraggeber: str
    erstellt_am: str
    version: str
    standard: str
    bgf_m2: Optional[float] = None
    geschosse: Optional[int] = None
    bundesland: Optional[str] = None

    @strawberry.field
    def positionen(self, info: Info) -> List[Position]:
        """All positions in this LV"""
        # In production: fetch from database
        return info.context.get("lv_positionen", [])

    @strawberry.field
    def gesamtsumme(self, info: Info) -> float:
        """Total sum of all positions"""
        positionen = self.positionen(info)
        return sum(p.gesamtpreis_basis for p in positionen)

    @strawberry.field
    def anzahl_positionen(self, info: Info) -> int:
        """Number of positions"""
        return len(self.positionen(info))


@strawberry.type
class BidPosition:
    """Bid position with price from bidder"""

    oz: str
    bezeichnung: str
    menge: float
    einheit: str
    einheitspreis: float
    gesamtpreis: float


@strawberry.type
class Bidder:
    """Company submitting bid"""

    firma: str
    uid_nummer: str
    ansprechpartner: str
    email: str
    telefon: str
    adresse: Optional[str] = None
    zertifizierungen: List[str] = strawberry.field(default_factory=list)


@strawberry.type
class Angebot:
    """Bid submitted by company"""

    angebot_id: str
    lv_id: str
    bidder: Bidder
    eingereicht_am: str
    angebotssumme: float
    ausfuehrungszeit_tage: int
    gewaehrleistung_jahre: int
    zahlungskonditionen: str
    verfuegbar: bool = True

    @strawberry.field
    def positionen(self, info: Info) -> List[BidPosition]:
        """All bid positions"""
        return info.context.get("bid_positionen", [])

    @strawberry.field
    def preis_punkte(self) -> float:
        """Price evaluation points (0-100)"""
        # In production: calculate against lowest bid
        return 85.0

    @strawberry.field
    def qualitaet_punkte(self) -> float:
        """Quality evaluation points (0-100)"""
        # In production: evaluate based on criteria
        return 78.0

    @strawberry.field
    def gesamt_punkte(self) -> float:
        """Total evaluation points"""
        return self.preis_punkte * 0.6 + self.qualitaet_punkte * 0.4


@strawberry.type
class BidComparison:
    """Multi-criteria bid comparison result"""

    lv_id: str
    anzahl_angebote: int
    niedrigstes_angebot: float
    hoechstes_angebot: float
    durchschnitt: float
    empfehlung: str
    gewinner_firma: str
    ranking: List[str]  # Firm names in order


@strawberry.type
class DigitalSignatureInfo:
    """eIDAS digital signature information"""

    signature_id: str
    document_hash: str
    signer_name: str
    signer_email: str
    signature_type: str
    timestamp: str
    status: str
    valid: bool


@strawberry.type
class ISO19650Info:
    """ISO 19650 BIM information"""

    eir_id: Optional[str] = None
    air_id: Optional[str] = None
    bep_id: Optional[str] = None
    loin_level: Optional[str] = None
    current_milestone: Optional[str] = None
    appointing_party: Optional[str] = None
    lead_appointed_party: Optional[str] = None


@strawberry.type
class ProjectMetadata:
    """Project metadata combining all standards"""

    projekt_id: str
    projekt_name: str
    auftraggeber: str
    bundesland: str
    bim_level: Optional[str] = None
    oenorm_version: str = "A 2063-1:2024"
    iso_19650_compliant: bool = False
    eidas_signed: bool = False
    created_at: str

    @strawberry.field
    def lv_liste(self, info: Info) -> List[Leistungsverzeichnis]:
        """All LVs for this project"""
        return info.context.get("project_lvs", [])

    @strawberry.field
    def iso_info(self, info: Info) -> Optional[ISO19650Info]:
        """ISO 19650 BIM information"""
        return info.context.get("iso_info")


# ═══════════════════════════════════════════════════════════════════════════
# GraphQL Input Types
# ═══════════════════════════════════════════════════════════════════════════


@strawberry.input
class LVGenerateInput:
    """Input for LV generation"""

    projekt_name: str
    projekt_ort: str
    auftraggeber: str
    bgf_m2: float
    geschosse: int
    bundesland: str
    apply_waste_factors: bool = True
    apply_regional_factors: bool = True


@strawberry.input
class BidSubmitInput:
    """Input for bid submission"""

    lv_id: str
    firma: str
    uid_nummer: str
    ansprechpartner: str
    email: str
    telefon: str
    angebotssumme: float
    ausfuehrungszeit_tage: int
    gewaehrleistung_jahre: int
    zahlungskonditionen: str


@strawberry.input
class SignLVInput:
    """Input for signing LV with eIDAS"""

    lv_id: str
    signer_name: str
    signer_email: str
    organization: str


@strawberry.input
class BidFilter:
    """Filter for bid queries"""

    lv_id: Optional[str] = None
    max_angebotssumme: Optional[float] = None
    min_gewaehrleistung_jahre: Optional[int] = None
    firma: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# GraphQL Queries
# ═══════════════════════════════════════════════════════════════════════════


@strawberry.type
class Query:
    """GraphQL root query type"""

    @strawberry.field
    def lv_by_id(self, info: Info, lv_id: str) -> Optional[Leistungsverzeichnis]:
        """Get LV by ID"""
        # In production: fetch from database
        return Leistungsverzeichnis(
            dokument_id=lv_id,
            projekt_name="Example Project",
            projekt_ort="Wien",
            auftraggeber="Example Client",
            erstellt_am=datetime.now(timezone.utc).isoformat(),
            version="1.0",
            standard="ÖNORM A 2063-1:2024",
        )

    @strawberry.field
    def all_lvs(
        self, info: Info, limit: int = 10, offset: int = 0, bundesland: Optional[str] = None
    ) -> List[Leistungsverzeichnis]:
        """Get all LVs with pagination and filtering"""
        # In production: fetch from database with filters
        return []

    @strawberry.field
    def angebote_for_lv(
        self, info: Info, lv_id: str, filter: Optional[BidFilter] = None
    ) -> List[Angebot]:
        """Get all bids for a specific LV"""
        # In production: fetch from database
        return []

    @strawberry.field
    def compare_bids(
        self, info: Info, lv_id: str, preis_gewicht: float = 0.6, qualitaet_gewicht: float = 0.4
    ) -> Optional[BidComparison]:
        """Compare all bids for LV using multi-criteria evaluation"""
        # In production: run actual comparison
        return BidComparison(
            lv_id=lv_id,
            anzahl_angebote=0,
            niedrigstes_angebot=0.0,
            hoechstes_angebot=0.0,
            durchschnitt=0.0,
            empfehlung="",
            gewinner_firma="",
            ranking=[],
        )

    @strawberry.field
    def verify_signature(self, info: Info, lv_id: str) -> Optional[DigitalSignatureInfo]:
        """Verify eIDAS signature on LV"""
        # In production: verify actual signature
        return None

    @strawberry.field
    def project_by_id(self, info: Info, projekt_id: str) -> Optional[ProjectMetadata]:
        """Get complete project metadata"""
        # In production: fetch from database
        return None

    @strawberry.field
    def search_positionen(self, info: Info, lv_id: str, search_term: str) -> List[Position]:
        """Search positions in LV by description"""
        # In production: full-text search
        return []

    @strawberry.field
    def bundeslaender(self) -> List[str]:
        """Get list of Austrian federal states"""
        return [
            "Wien",
            "Niederösterreich",
            "Oberösterreich",
            "Steiermark",
            "Kärnten",
            "Salzburg",
            "Tirol",
            "Vorarlberg",
            "Burgenland",
        ]

    @strawberry.field
    def leistungsgruppen(self) -> List[str]:
        """Get list of ÖNORM A 2063 trade groups"""
        return [
            "Baumeisterarbeiten",
            "Erdarbeiten",
            "Maurerarbeiten",
            "Stahlbetonarbeiten",
            "Zimmererarbeiten",
            "Dachdeckerarbeiten",
            "Spenglerarbeiten",
            "Installationsarbeiten",
            "Elektroarbeiten",
            "Malerarbeiten",
        ]


# ═══════════════════════════════════════════════════════════════════════════
# GraphQL Mutations
# ═══════════════════════════════════════════════════════════════════════════


@strawberry.type
class Mutation:
    """GraphQL root mutation type"""

    @strawberry.mutation
    def generate_lv(self, info: Info, input: LVGenerateInput) -> Leistungsverzeichnis:
        """Generate new LV per ÖNORM A 2063"""

        if not MODULES_AVAILABLE:
            raise Exception("ÖNORM A 2063 module not available")

        # Generate positions
        positionen = generiere_beispiel_lv_einfamilienhaus(
            bgf_m2=input.bgf_m2, geschosse=input.geschosse
        )

        # Apply regional factors
        if input.apply_regional_factors:
            bundesland_enum = Bundesland(input.bundesland)
            result = berechne_regionale_anpassung(positionen, bundesland_enum)
            positionen = result["positionen_angepasst"]

        # Create LV document
        lv_id = f"LV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Convert positions to GraphQL types
        graphql_positionen = [
            Position(
                oz=p.oz,
                bezeichnung=p.bezeichnung,
                einheit=p.einheit,
                menge=p.menge,
                einheitspreis_basis=p.einheitspreis_basis,
                gesamtpreis_basis=p.gesamtpreis_basis,
                leistungsgruppe=p.leistungsgruppe,
                kurzbeschreibung=getattr(p, "kurzbeschreibung", None),
                abfall_kg=getattr(p, "abfall_kg", None),
                regional_faktor=getattr(p, "regional_faktor", None),
            )
            for p in positionen
        ]

        # Store in context for later queries
        info.context["lv_positionen"] = graphql_positionen

        return Leistungsverzeichnis(
            dokument_id=lv_id,
            projekt_name=input.projekt_name,
            projekt_ort=input.projekt_ort,
            auftraggeber=input.auftraggeber,
            erstellt_am=datetime.now(timezone.utc).isoformat(),
            version="1.0",
            standard="ÖNORM A 2063-1:2024",
            bgf_m2=input.bgf_m2,
            geschosse=input.geschosse,
            bundesland=input.bundesland,
        )

    @strawberry.mutation
    def submit_bid(self, info: Info, input: BidSubmitInput) -> Angebot:
        """Submit bid for LV"""

        bidder = Bidder(
            firma=input.firma,
            uid_nummer=input.uid_nummer,
            ansprechpartner=input.ansprechpartner,
            email=input.email,
            telefon=input.telefon,
        )

        angebot_id = f"BID-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        return Angebot(
            angebot_id=angebot_id,
            lv_id=input.lv_id,
            bidder=bidder,
            eingereicht_am=datetime.now(timezone.utc).isoformat(),
            angebotssumme=input.angebotssumme,
            ausfuehrungszeit_tage=input.ausfuehrungszeit_tage,
            gewaehrleistung_jahre=input.gewaehrleistung_jahre,
            zahlungskonditionen=input.zahlungskonditionen,
        )

    @strawberry.mutation
    def sign_lv_eidas(self, info: Info, input: SignLVInput) -> DigitalSignatureInfo:
        """Sign LV with eIDAS qualified signature"""

        if not MODULES_AVAILABLE:
            raise Exception("eIDAS signature module not available")

        # In production: fetch actual LV content
        lv_content = json.dumps({"lv_id": input.lv_id, "signed": True})

        # Create signature
        signatur = signiere_oenorm_lv(
            lv_json=lv_content,
            projekt_name="Project",
            verantwortlicher=input.signer_name,
            email=input.signer_email,
            firma=input.organization,
        )

        sig_data = signatur["digital_signature"]

        return DigitalSignatureInfo(
            signature_id=sig_data["signature_id"],
            document_hash=sig_data["document_hash"],
            signer_name=sig_data["signer"]["name"],
            signer_email=sig_data["signer"]["email"],
            signature_type=sig_data["metadata"]["signature_type"],
            timestamp=sig_data["metadata"]["timestamp"],
            status="valid",
            valid=True,
        )

    @strawberry.mutation
    def create_iso_19650_eir(
        self, info: Info, projekt_name: str, auftraggeber: str, projekt_typ: str = "Neubau"
    ) -> ISO19650Info:
        """Create ISO 19650 EIR template"""

        if not MODULES_AVAILABLE:
            raise Exception("ISO 19650 module not available")

        eir = erstelle_eir_template_oesterreich(
            projekt_name=projekt_name, auftraggeber=auftraggeber, projekt_typ=projekt_typ
        )

        return ISO19650Info(
            eir_id=eir.project_id,
            appointing_party=eir.appointing_party,
            current_milestone="M1",
            loin_level="LOD 200",
        )


# ═══════════════════════════════════════════════════════════════════════════
# GraphQL Subscriptions (Real-time updates)
# ═══════════════════════════════════════════════════════════════════════════


@strawberry.type
class Subscription:
    """GraphQL subscription type for real-time updates"""

    @strawberry.subscription
    async def bid_submitted(self, info: Info, lv_id: str) -> Angebot:
        """Subscribe to new bids for specific LV"""
        # In production: use WebSocket or async queue
        # This is a placeholder showing the structure
        yield Angebot(
            angebot_id="placeholder",
            lv_id=lv_id,
            bidder=Bidder(
                firma="Example",
                uid_nummer="ATU12345678",
                ansprechpartner="Test",
                email="test@example.com",
                telefon="+43 1 12345",
            ),
            eingereicht_am=datetime.now(timezone.utc).isoformat(),
            angebotssumme=100000.0,
            ausfuehrungszeit_tage=180,
            gewaehrleistung_jahre=5,
            zahlungskonditionen="30 Tage netto",
        )

    @strawberry.subscription
    async def lv_status_changed(self, info: Info, projekt_id: str) -> Leistungsverzeichnis:
        """Subscribe to LV status changes"""
        # Placeholder
        yield Leistungsverzeichnis(
            dokument_id="placeholder",
            projekt_name="Example",
            projekt_ort="Wien",
            auftraggeber="Test",
            erstellt_am=datetime.now(timezone.utc).isoformat(),
            version="1.0",
            standard="ÖNORM A 2063-1:2024",
        )


# ═══════════════════════════════════════════════════════════════════════════
# Schema Creation
# ═══════════════════════════════════════════════════════════════════════════

if GRAPHQL_AVAILABLE:
    schema = strawberry.Schema(
        query=Query,
        mutation=Mutation,
        subscription=Subscription,
        config=StrawberryConfig(
            auto_camel_case=False  # Keep snake_case for Austrian naming conventions
        ),
    )
else:
    schema = None


# ═══════════════════════════════════════════════════════════════════════════
# FastAPI Integration
# ═══════════════════════════════════════════════════════════════════════════


def get_graphql_app():
    """
    Get GraphQL app for FastAPI integration

    Usage in main.py:
        from strawberry.fastapi import GraphQLRouter
        graphql_app = GraphQLRouter(schema)
        app.include_router(graphql_app, prefix="/graphql")
    """
    if not GRAPHQL_AVAILABLE:
        raise ImportError(
            "strawberry-graphql not installed. Install with: pip install 'strawberry-graphql[fastapi]'"
        )

    from strawberry.fastapi import GraphQLRouter

    return GraphQLRouter(schema)


# ═══════════════════════════════════════════════════════════════════════════
# Example Queries for Testing
# ═══════════════════════════════════════════════════════════════════════════

EXAMPLE_QUERIES = {
    "get_lv": """
        query GetLV($lvId: String!) {
            lv_by_id(lv_id: $lvId) {
                dokument_id
                projekt_name
                projekt_ort
                auftraggeber
                standard
                gesamtsumme
                anzahl_positionen
                positionen {
                    oz
                    bezeichnung
                    einheit
                    menge
                    gesamtpreis_formatted
                }
            }
        }
    """,
    "generate_lv": """
        mutation GenerateLV($input: LVGenerateInput!) {
            generate_lv(input: $input) {
                dokument_id
                projekt_name
                bundesland
                gesamtsumme
                anzahl_positionen
            }
        }
    """,
    "compare_bids": """
        query CompareBids($lvId: String!) {
            compare_bids(lv_id: $lvId) {
                anzahl_angebote
                niedrigstes_angebot
                durchschnitt
                gewinner_firma
                ranking
                empfehlung
            }
        }
    """,
    "sign_lv": """
        mutation SignLV($input: SignLVInput!) {
            sign_lv_eidas(input: $input) {
                signature_id
                document_hash
                signer_name
                timestamp
                status
                valid
            }
        }
    """,
    "nested_query": """
        query ComplexProjectQuery($projektId: String!) {
            project_by_id(projekt_id: $projektId) {
                projekt_name
                auftraggeber
                bundesland
                oenorm_version
                iso_19650_compliant
                eidas_signed
                lv_liste {
                    dokument_id
                    projekt_name
                    gesamtsumme
                    positionen {
                        oz
                        bezeichnung
                        gesamtpreis_basis
                    }
                }
                iso_info {
                    eir_id
                    current_milestone
                    loin_level
                }
            }
        }
    """,
    "subscribe_bids": """
        subscription BidUpdates($lvId: String!) {
            bid_submitted(lv_id: $lvId) {
                angebot_id
                bidder {
                    firma
                    email
                }
                angebotssumme
                eingereicht_am
                gesamt_punkte
            }
        }
    """,
}


if __name__ == "__main__":
    print("═" * 80)
    print("GraphQL Schema für ÖNORM A 2063 Tendering")
    print("═" * 80)
    print()

    if GRAPHQL_AVAILABLE:
        print("✓ Strawberry GraphQL verfügbar")
        print(f"✓ Schema erstellt mit {len(EXAMPLE_QUERIES)} Beispiel-Queries")
        print()
        print("Schema-Statistik:")
        print(f"  - Queries: {len([f for f in dir(Query) if not f.startswith('_')])}")
        print(f"  - Mutations: {len([f for f in dir(Mutation) if not f.startswith('_')])}")
        print(f"  - Subscriptions: {len([f for f in dir(Subscription) if not f.startswith('_')])}")
        print(f"  - Types: Position, Leistungsverzeichnis, Angebot, BidComparison, etc.")
        print()
        print("Beispiel-Queries verfügbar:")
        for name in EXAMPLE_QUERIES.keys():
            print(f"  - {name}")
    else:
        print("⚠ Strawberry GraphQL nicht installiert")
        print("Installation: pip install 'strawberry-graphql[fastapi]'")
