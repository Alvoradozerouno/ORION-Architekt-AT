#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
Live Cost Database Integration for Austria
═══════════════════════════════════════════════════════════════════════════

Echtzeit-Baupreisindizes und Kostenaktualisierung für Österreich.

Features:
1. Integration mit Statistik Austria Baupreisindex
2. Regionale Marktpreise (live updates)
3. Materialpreis-Tracking (Stahl, Holz, Beton, etc.)
4. Automatische LV-Preisaktualisierung
5. Historische Preisentwicklung und Trends

Datenquellen:
- Statistik Austria: Baupreisindex
- BM Finanzen: Öffentliche Vergaben
- Markt-APIs: Baustoffhändler (optional)

Basierend auf:
- Global Best Practice: RSMeans Data Online
- Research 2026: Real-time cost databases

Stand: April 2026
Lizenz: Apache 2.0
═══════════════════════════════════════════════════════════════════════════
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════════
# Material Categories
# ═══════════════════════════════════════════════════════════════════════════


class MaterialCategory(str, Enum):
    """Hauptgruppen für Baupreisindex"""

    BETON = "beton"
    STAHL = "stahl"
    HOLZ = "holz"
    ZIEGEL = "ziegel"
    DAEMMUNG = "daemmung"
    FENSTER = "fenster"
    DACHZIEGEL = "dachziegel"
    ELEKTRO = "elektro"
    INSTALLATION = "installation"
    LOHN = "lohn"


# ═══════════════════════════════════════════════════════════════════════════
# Data Classes
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class PriceIndex:
    """Baupreisindex für bestimmte Kategorie"""

    category: str
    index_value: float  # Basis 2015 = 100
    timestamp: str
    bundesland: str = "AT"  # AT = österreichweit
    source: str = "Statistik Austria"

    # Trend
    previous_month: Optional[float] = None
    previous_year: Optional[float] = None

    def change_month_pct(self) -> float:
        """Änderung zum Vormonat in %"""
        if self.previous_month:
            return ((self.index_value - self.previous_month) / self.previous_month) * 100
        return 0.0

    def change_year_pct(self) -> float:
        """Änderung zum Vorjahr in %"""
        if self.previous_year:
            return ((self.index_value - self.previous_year) / self.previous_year) * 100
        return 0.0


@dataclass
class LiveCostData:
    """Live-Kostendaten für LV-Position"""

    material_category: str
    base_price_eur: float  # Basispreis 2015
    current_price_eur: float  # Aktueller Preis
    last_updated: str
    bundesland: str

    # Index-basierte Berechnung
    price_index: float = 100.0
    adjustment_factor: float = 1.0

    # Volatilität
    volatility_7d: Optional[float] = None  # % Schwankung 7 Tage
    volatility_30d: Optional[float] = None  # % Schwankung 30 Tage


@dataclass
class CostDatabaseEntry:
    """Eintrag in der Kostendatenbank"""

    item_code: str  # z.B. "02.001" ÖNORM Position
    description: str
    unit: str
    material_category: str

    # Pricing
    base_price_2015: float  # Basispreis
    current_prices: Dict[str, float] = field(default_factory=dict)  # Bundesland → Preis

    # Metadata
    valid_from: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_update: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════════════════════════════════════
# Live Price Database (simulated)
# ═══════════════════════════════════════════════════════════════════════════

# Statistik Austria Baupreisindex (Q1 2026 - simuliert)
BAUPREISINDEX_2026 = {
    MaterialCategory.BETON: PriceIndex(
        category="Beton und Betonwaren",
        index_value=143.2,  # +43.2% seit 2015
        timestamp="2026-03-01",
        previous_month=142.8,
        previous_year=138.5,
    ),
    MaterialCategory.STAHL: PriceIndex(
        category="Baustahl",
        index_value=168.5,  # +68.5% seit 2015
        timestamp="2026-03-01",
        previous_month=167.2,
        previous_year=155.8,
    ),
    MaterialCategory.HOLZ: PriceIndex(
        category="Bauholz",
        index_value=152.3,  # +52.3% seit 2015
        timestamp="2026-03-01",
        previous_month=151.9,
        previous_year=148.2,
    ),
    MaterialCategory.ZIEGEL: PriceIndex(
        category="Ziegel",
        index_value=135.8,
        timestamp="2026-03-01",
        previous_month=135.5,
        previous_year=132.1,
    ),
    MaterialCategory.DAEMMUNG: PriceIndex(
        category="Dämmstoffe",
        index_value=128.4,
        timestamp="2026-03-01",
        previous_month=128.1,
        previous_year=124.7,
    ),
    MaterialCategory.FENSTER: PriceIndex(
        category="Fenster und Türen",
        index_value=141.6,
        timestamp="2026-03-01",
        previous_month=141.2,
        previous_year=137.9,
    ),
    MaterialCategory.DACHZIEGEL: PriceIndex(
        category="Dachziegel",
        index_value=133.2,
        timestamp="2026-03-01",
        previous_month=133.0,
        previous_year=130.5,
    ),
    MaterialCategory.LOHN: PriceIndex(
        category="Löhne Baugewerbe",
        index_value=156.8,  # +56.8% seit 2015
        timestamp="2026-03-01",
        previous_month=156.8,  # Stabil
        previous_year=148.2,
    ),
}


# Basisdatenbank (Preise 2015 als Referenz)
COST_DATABASE_BASE = {
    "02.001": CostDatabaseEntry(
        item_code="02.001",
        description="Außenwand Ziegel wärmegedämmt",
        unit="m2",
        material_category=MaterialCategory.ZIEGEL.value,
        base_price_2015=88.50,  # EUR/m2 Basis 2015
        current_prices={},  # Wird berechnet
    ),
    "03.001": CostDatabaseEntry(
        item_code="03.001",
        description="Stahlbeton C30/37",
        unit="m3",
        material_category=MaterialCategory.BETON.value,
        base_price_2015=315.00,
        current_prices={},
    ),
    "04.001": CostDatabaseEntry(
        item_code="04.001",
        description="Holzbau Konstruktion",
        unit="m3",
        material_category=MaterialCategory.HOLZ.value,
        base_price_2015=620.00,
        current_prices={},
    ),
    "05.001": CostDatabaseEntry(
        item_code="05.001",
        description="Dacheindeckung Tondachziegel",
        unit="m2",
        material_category=MaterialCategory.DACHZIEGEL.value,
        base_price_2015=63.80,
        current_prices={},
    ),
    "07.001": CostDatabaseEntry(
        item_code="07.001",
        description="Kunststofffenster 3-fach verglast",
        unit="m2",
        material_category=MaterialCategory.FENSTER.value,
        base_price_2015=388.00,
        current_prices={},
    ),
}


# ═══════════════════════════════════════════════════════════════════════════
# Live Price Functions
# ═══════════════════════════════════════════════════════════════════════════


def get_current_price_index(material: str) -> Optional[PriceIndex]:
    """
    Get current price index from Statistik Austria

    In production: API call to Statistik Austria
    https://www.statistik.at/services/tools/services/jsstat
    """

    # Find matching category
    for cat in MaterialCategory:
        if cat.value == material.lower():
            return BAUPREISINDEX_2026.get(cat)

    return None


def calculate_live_price(
    base_price_2015: float, material_category: str, bundesland: str = "wien"
) -> LiveCostData:
    """
    Calculate current price based on live index

    Formula: current_price = base_price * (index / 100)
    """

    price_index_obj = get_current_price_index(material_category)

    if price_index_obj:
        index_value = price_index_obj.index_value
        current_price = base_price_2015 * (index_value / 100.0)

        # Regional adjustment (simplified)
        regional_factors = {
            "wien": 1.15,
            "niederösterreich": 1.05,
            "oberösterreich": 1.08,
            "steiermark": 1.03,
            "salzburg": 1.12,
            "tirol": 1.18,
            "vorarlberg": 1.20,
            "kärnten": 1.02,
            "burgenland": 1.00,
        }

        regional_factor = regional_factors.get(bundesland.lower(), 1.0)
        current_price *= regional_factor

        return LiveCostData(
            material_category=material_category,
            base_price_eur=base_price_2015,
            current_price_eur=round(current_price, 2),
            last_updated=price_index_obj.timestamp,
            bundesland=bundesland,
            price_index=index_value,
            adjustment_factor=regional_factor,
            volatility_7d=abs(price_index_obj.change_month_pct()),
            volatility_30d=abs(price_index_obj.change_year_pct() / 12),
        )
    else:
        # Fallback: no index available
        return LiveCostData(
            material_category=material_category,
            base_price_eur=base_price_2015,
            current_price_eur=base_price_2015,
            last_updated=datetime.now(timezone.utc).isoformat(),
            bundesland=bundesland,
        )


def update_cost_database_live(bundesland: str = "wien") -> Dict[str, CostDatabaseEntry]:
    """
    Update entire cost database with live prices

    Returns: Updated database with current prices
    """

    updated_db = {}

    for code, entry in COST_DATABASE_BASE.items():
        # Calculate live price
        live_data = calculate_live_price(entry.base_price_2015, entry.material_category, bundesland)

        # Update entry
        entry.current_prices[bundesland] = live_data.current_price_eur
        entry.last_update = live_data.last_updated

        updated_db[code] = entry

    return updated_db


def get_live_price_for_item(item_code: str, bundesland: str = "wien") -> Optional[float]:
    """
    Get current live price for specific ÖNORM position

    Returns: Current price in EUR
    """

    db = update_cost_database_live(bundesland)
    entry = db.get(item_code)

    if entry:
        return entry.current_prices.get(bundesland)

    return None


# ═══════════════════════════════════════════════════════════════════════════
# Integration with LV
# ═══════════════════════════════════════════════════════════════════════════


def enrich_lv_with_live_prices(
    lv_positions: List[Dict[str, Any]], bundesland: str = "wien"
) -> List[Dict[str, Any]]:
    """
    Enrich LV positions with live market prices

    Replaces static prices with index-adjusted prices
    """

    for position in lv_positions:
        # Try to find matching entry in cost database
        oz = position.get("oz", "")

        # Simplified matching (would be more sophisticated in production)
        if "Außenwand" in position.get("bezeichnung", ""):
            live_price = get_live_price_for_item("02.001", bundesland)
        elif "Stahlbeton" in position.get("bezeichnung", ""):
            live_price = get_live_price_for_item("03.001", bundesland)
        elif "Dach" in position.get("bezeichnung", ""):
            live_price = get_live_price_for_item("05.001", bundesland)
        elif "Fenster" in position.get("bezeichnung", ""):
            live_price = get_live_price_for_item("07.001", bundesland)
        else:
            live_price = None

        if live_price:
            position["einheitspreis_live"] = live_price
            position["gesamtpreis_live"] = live_price * position["menge"]
            position["preis_quelle"] = "Live Index 2026"
            position["preisstand"] = BAUPREISINDEX_2026[
                list(BAUPREISINDEX_2026.keys())[0]
            ].timestamp

    return lv_positions


def generate_price_trend_report() -> Dict[str, Any]:
    """
    Generate report on price trends

    Shows development over time
    """

    trends = {}

    for mat_cat, price_idx in BAUPREISINDEX_2026.items():
        trends[mat_cat.value] = {
            "category": price_idx.category,
            "current_index": price_idx.index_value,
            "change_month_pct": round(price_idx.change_month_pct(), 2),
            "change_year_pct": round(price_idx.change_year_pct(), 2),
            "timestamp": price_idx.timestamp,
            "trend": "steigend" if price_idx.change_month_pct() > 0 else "fallend",
        }

    return {
        "report_date": datetime.now(timezone.utc).isoformat(),
        "source": "Statistik Austria Baupreisindex",
        "base_year": "2015",
        "trends": trends,
    }


# ═══════════════════════════════════════════════════════════════════════════
# API Integration (Placeholder)
# ═══════════════════════════════════════════════════════════════════════════


def fetch_live_data_from_statistik_austria() -> Dict[str, PriceIndex]:
    """
    Fetch live data from Statistik Austria API

    NOTE: In production, use actual API
    https://www.statistik.at/services/tools/services/jsstat
    """

    # Placeholder: Would make HTTP request to API
    # import requests
    # response = requests.get("https://www.statistik.at/api/baupreisindex")
    # data = response.json()

    return BAUPREISINDEX_2026


# ═══════════════════════════════════════════════════════════════════════════
# Main Workflow
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 80)
    print("Live Cost Database - ÖSTERREICH")
    print("═" * 80)
    print()

    # Test 1: Get current indices
    print("Test 1: Aktuelle Baupreisindizes (Q1 2026)...")
    for mat, idx in BAUPREISINDEX_2026.items():
        print(
            f"  {idx.category:30s} Index: {idx.index_value:6.1f}  "
            f"ΔM: {idx.change_month_pct():+.2f}%  ΔJ: {idx.change_year_pct():+.2f}%"
        )
    print()

    # Test 2: Calculate live price
    print("Test 2: Live-Preis für Stahlbeton Wien...")
    live_price = calculate_live_price(315.00, MaterialCategory.BETON.value, "wien")
    print(f"  Basispreis 2015: EUR {live_price.base_price_eur:.2f}/m³")
    print(f"  Aktueller Preis:  EUR {live_price.current_price_eur:.2f}/m³")
    print(f"  Preisindex: {live_price.price_index:.1f}")
    print(f"  Regional-Faktor Wien: {live_price.adjustment_factor:.2f}")
    print(f"  Volatilität 30d: {live_price.volatility_30d:.2f}%")
    print()

    # Test 3: Update full database
    print("Test 3: Kostendatenbank aktualisieren (Wien)...")
    db_updated = update_cost_database_live("wien")
    print(f"  ✓ {len(db_updated)} Positionen aktualisiert")
    for code, entry in db_updated.items():
        wien_price = entry.current_prices.get("wien", 0)
        base_price = entry.base_price_2015
        change = ((wien_price - base_price) / base_price) * 100
        print(
            f"  {code} - {entry.description[:40]:40s} "
            f"EUR {wien_price:8.2f}/{entry.unit} ({change:+.1f}%)"
        )
    print()

    # Test 4: Price trend report
    print("Test 4: Preistrend-Report...")
    report = generate_price_trend_report()
    print(f"  Report-Datum: {report['report_date'][:10]}")
    print(f"  Quelle: {report['source']}")
    print()
    print("  Top Preisänderungen (Jahr):")
    sorted_trends = sorted(
        report["trends"].items(), key=lambda x: abs(x[1]["change_year_pct"]), reverse=True
    )
    for mat, trend in sorted_trends[:5]:
        print(f"    {trend['category']:30s} {trend['change_year_pct']:+6.2f}% ({trend['trend']})")
    print()

    print("✓ Live Cost Database FUNKTIONIERT")
    print("  NOTE: In Produktion API-Integration mit Statistik Austria")
