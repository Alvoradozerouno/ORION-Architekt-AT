#!/usr/bin/env python3
"""
Tests für ORION ÖNORM A 2063 - Angebotslegung & Ausschreibung

Testet alle Funktionen des Ausschreibungs- und Angebotsmoduls
"""

import pytest
import json
from orion_oenorm_a2063 import (
    LVPosition,
    generiere_beispiel_lv_einfamilienhaus,
    exportiere_lv_oenorm_json,
    vergleiche_angebote_detailliert,
    erstelle_vollstaendige_ausschreibung,
    exportiere_gaeb_xml,
    GEWERKE_KATALOG_AT,
)


class TestLVPosition:
    """Test LVPosition Dataclass"""

    def test_lv_position_creation(self):
        """Test LV-Position creation and automatic GP calculation"""
        pos = LVPosition(
            oz="01.001",
            kurztext="Erdarbeiten",
            langtext="Erdaushub maschinell",
            einheit="m³",
            menge=100.0,
            ep=50.0,
            gewerk="01",
        )

        assert pos.oz == "01.001"
        assert pos.menge == 100.0
        assert pos.ep == 50.0
        assert pos.gp == 5000.0  # Automatically calculated

    def test_lv_position_gp_recalculation(self):
        """Test that GP is recalculated correctly"""
        pos = LVPosition(
            oz="02.001",
            kurztext="Mauerwerk",
            langtext="Mauerwerk 25cm",
            einheit="m²",
            menge=50.5,
            ep=75.25,
            gewerk="01",
        )

        assert pos.gp == round(50.5 * 75.25, 2)


class TestLVGeneration:
    """Test LV-Generierung für verschiedene Gebäudetypen"""

    def test_generiere_lv_einfamilienhaus_basic(self):
        """Test basic LV generation for single family house"""
        positionen = generiere_beispiel_lv_einfamilienhaus(bgf_m2=150, geschosse=2)

        assert len(positionen) > 10  # Mindestens 10 Positionen
        assert all(isinstance(p, LVPosition) for p in positionen)

        # Check that all positions have required fields
        for pos in positionen:
            assert pos.oz
            assert pos.kurztext
            assert pos.einheit
            assert pos.menge > 0
            assert pos.gewerk in GEWERKE_KATALOG_AT

    def test_generiere_lv_groessere_bgf(self):
        """Test LV generation scales with BGF"""
        positionen_klein = generiere_beispiel_lv_einfamilienhaus(bgf_m2=100, geschosse=1)
        positionen_gross = generiere_beispiel_lv_einfamilienhaus(bgf_m2=300, geschosse=2)

        # Mengen sollten größer sein bei größerer BGF
        erdaushub_klein = next(p for p in positionen_klein if "Erdarbeiten" in p.kurztext)
        erdaushub_gross = next(p for p in positionen_gross if "Erdarbeiten" in p.kurztext)

        assert erdaushub_gross.menge > erdaushub_klein.menge

    def test_lv_gewerke_vollstaendig(self):
        """Test that LV contains all major Gewerke"""
        positionen = generiere_beispiel_lv_einfamilienhaus(bgf_m2=150, geschosse=2)

        gewerke_vorhanden = set(p.gewerk for p in positionen)

        # Mindestens diese Gewerke sollten vorhanden sein
        erwartet = {"01", "02", "03", "04", "05", "06", "07", "08", "09"}
        assert erwartet.issubset(gewerke_vorhanden)


class TestOENORMExport:
    """Test ÖNORM A 2063 JSON Export"""

    def test_exportiere_oenorm_json_structure(self):
        """Test JSON export structure complies with ÖNORM A 2063"""
        positionen = generiere_beispiel_lv_einfamilienhaus(bgf_m2=150, geschosse=2)

        projekt_info = {
            "name": "Test Projekt",
            "typ": "Neubau",
            "bgf_m2": 150,
        }
        auftraggeber = {"name": "Test GmbH", "adresse": "Teststraße 1"}

        lv_json = exportiere_lv_oenorm_json(
            positionen=positionen,
            projekt_info=projekt_info,
            auftraggeber=auftraggeber,
            bundesland="tirol",
        )

        # Check required ÖNORM fields
        assert "meta" in lv_json
        assert lv_json["meta"]["standard"] == "ÖNORM A 2063-1:2024"
        assert "projekt" in lv_json
        assert "auftraggeber" in lv_json
        assert "gewerke" in lv_json
        assert "rechtliche_hinweise" in lv_json
        assert "zahlungsplan" in lv_json

    def test_exportiere_oenorm_json_gewerke_gruppierung(self):
        """Test that positions are correctly grouped by Gewerk"""
        positionen = generiere_beispiel_lv_einfamilienhaus(bgf_m2=150, geschosse=2)

        projekt_info = {"name": "Test", "typ": "Neubau", "bgf_m2": 150}
        auftraggeber = {"name": "Test", "adresse": "Test"}

        lv_json = exportiere_lv_oenorm_json(positionen, projekt_info, auftraggeber)

        # Jedes Gewerk sollte Positionen haben
        for gewerk in lv_json["gewerke"]:
            assert "gewerk_nr" in gewerk
            assert "gewerk_name" in gewerk
            assert "positionen" in gewerk
            assert len(gewerk["positionen"]) > 0

    def test_exportiere_oenorm_bundesland_spezifika(self):
        """Test that Bundesland-specific hints are included"""
        positionen = generiere_beispiel_lv_einfamilienhaus(bgf_m2=150)

        projekt_info = {"name": "Test", "typ": "Neubau", "bgf_m2": 150}
        auftraggeber = {"name": "Test", "adresse": "Test"}

        lv_json_wien = exportiere_lv_oenorm_json(
            positionen, projekt_info, auftraggeber, bundesland="wien"
        )

        # Wien sollte Vergabegesetz-Hinweis haben
        assert any("Vergabegesetz" in h for h in lv_json_wien["rechtliche_hinweise"])


class TestAngebotsvergleich:
    """Test Angebotsvergleich und Preisspiegelmatrix"""

    def test_vergleiche_angebote_basic(self):
        """Test basic offer comparison"""
        lv_positionen = [
            LVPosition(
                oz="01.001",
                kurztext="Test 1",
                langtext="Test",
                einheit="m²",
                menge=100,
                gewerk="01",
            ),
            LVPosition(
                oz="01.002", kurztext="Test 2", langtext="Test", einheit="m³", menge=50, gewerk="01"
            ),
        ]

        angebote = [
            {
                "firma": "Firma A",
                "positionen": [
                    {"oz": "01.001", "menge": 100, "ep": 50},
                    {"oz": "01.002", "menge": 50, "ep": 80},
                ],
            },
            {
                "firma": "Firma B",
                "positionen": [
                    {"oz": "01.001", "menge": 100, "ep": 55},
                    {"oz": "01.002", "menge": 50, "ep": 75},
                ],
            },
        ]

        vergleich = vergleiche_angebote_detailliert(angebote, lv_positionen)

        assert vergleich["anzahl_angebote"] == 2
        assert "guenstigstes_angebot" in vergleich
        assert "teuerstes_angebot" in vergleich
        assert "preisspiegelmatrix" in vergleich
        assert len(vergleich["preisspiegelmatrix"]) == 2

    def test_vergleiche_angebote_preisspanne(self):
        """Test that price spread is calculated correctly"""
        lv_positionen = [
            LVPosition(
                oz="01.001", kurztext="Test", langtext="Test", einheit="Stk", menge=1, gewerk="01"
            ),
        ]

        angebote = [
            {"firma": "Firma A", "positionen": [{"oz": "01.001", "menge": 1, "ep": 1000}]},
            {"firma": "Firma B", "positionen": [{"oz": "01.001", "menge": 1, "ep": 1500}]},
        ]

        vergleich = vergleiche_angebote_detailliert(angebote, lv_positionen)

        # 50% Differenz zwischen 1000 und 1500
        assert vergleich["differenz_prozent"] == 50.0

    def test_vergleiche_angebote_empfehlung_warnung(self):
        """Test that recommendations and warnings are generated"""
        lv_positionen = [
            LVPosition(
                oz="01.001", kurztext="Test", langtext="Test", einheit="Stk", menge=1, gewerk="01"
            ),
        ]

        # Nur 2 Angebote (weniger als 3) → Warnung
        angebote = [
            {"firma": "Firma A", "positionen": [{"oz": "01.001", "menge": 1, "ep": 1000}]},
            {"firma": "Firma B", "positionen": [{"oz": "01.001", "menge": 1, "ep": 1100}]},
        ]

        vergleich = vergleiche_angebote_detailliert(angebote, lv_positionen)

        assert len(vergleich["warnung"]) > 0
        assert any("3 Angebote" in w for w in vergleich["warnung"])

    def test_vergleiche_angebote_sortierung(self):
        """Test that offers are sorted by price"""
        lv_positionen = [
            LVPosition(
                oz="01.001", kurztext="Test", langtext="Test", einheit="Stk", menge=1, gewerk="01"
            ),
        ]

        angebote = [
            {"firma": "Firma C", "positionen": [{"oz": "01.001", "menge": 1, "ep": 1500}]},
            {"firma": "Firma A", "positionen": [{"oz": "01.001", "menge": 1, "ep": 1000}]},
            {"firma": "Firma B", "positionen": [{"oz": "01.001", "menge": 1, "ep": 1200}]},
        ]

        vergleich = vergleiche_angebote_detailliert(angebote, lv_positionen)

        sortiert = vergleich["angebote_sortiert"]
        assert sortiert[0]["firma"] == "Firma A"  # Günstigstes
        assert sortiert[1]["firma"] == "Firma B"
        assert sortiert[2]["firma"] == "Firma C"  # Teuerstes


class TestGAEBExport:
    """Test GAEB XML Export"""

    def test_exportiere_gaeb_xml_structure(self):
        """Test GAEB XML export generates valid XML"""
        positionen = generiere_beispiel_lv_einfamilienhaus(bgf_m2=150)[:3]  # Only first 3 positions

        projekt_info = {"name": "Test Projekt", "id": "TEST-001"}

        gaeb_xml = exportiere_gaeb_xml(positionen, projekt_info)

        # Check basic XML structure
        assert '<?xml version="1.0"' in gaeb_xml
        assert "<GAEB" in gaeb_xml
        assert "</GAEB>" in gaeb_xml
        assert "<GAEBInfo>" in gaeb_xml
        assert "<PrjInfo>" in gaeb_xml
        assert "<BoQ>" in gaeb_xml

        # Check that positions are included
        for pos in positionen:
            assert pos.oz in gaeb_xml
            assert pos.kurztext in gaeb_xml


class TestVollstaendigeAusschreibung:
    """Test vollständige Ausschreibungserstellung"""

    def test_erstelle_vollstaendige_ausschreibung_einfamilienhaus(self):
        """Test complete tender creation for single family house"""
        ausschreibung = erstelle_vollstaendige_ausschreibung(
            projekt_typ="einfamilienhaus", bgf_m2=150, bundesland="tirol"
        )

        assert "lv_positionen" in ausschreibung
        assert "lv_oenorm_json" in ausschreibung
        assert "gaeb_xml" in ausschreibung
        assert "projekt" in ausschreibung
        assert ausschreibung["anzahl_positionen"] > 10
        assert ausschreibung["status"] == "Ausschreibungsreif nach ÖNORM A 2063"

    def test_erstelle_ausschreibung_verschiedene_bundeslaender(self):
        """Test tender creation for different Bundesländer"""
        bundeslaender = ["wien", "tirol", "salzburg", "steiermark"]

        for bl in bundeslaender:
            ausschreibung = erstelle_vollstaendige_ausschreibung(
                projekt_typ="einfamilienhaus", bgf_m2=150, bundesland=bl
            )

            assert ausschreibung["projekt"]["bundesland"] == bl
            assert ausschreibung["lv_oenorm_json"]["projekt"]["bundesland"] == bl

    def test_erstelle_ausschreibung_custom_auftraggeber(self):
        """Test tender with custom client data"""
        auftraggeber = {
            "name": "Custom Client GmbH",
            "adresse": "Hauptstraße 123",
            "kontakt": "office@client.at",
        }

        ausschreibung = erstelle_vollstaendige_ausschreibung(
            projekt_typ="einfamilienhaus", bgf_m2=200, bundesland="wien", auftraggeber=auftraggeber
        )

        assert ausschreibung["lv_oenorm_json"]["auftraggeber"]["name"] == "Custom Client GmbH"


class TestGewerkeKatalog:
    """Test Gewerke-Katalog Struktur"""

    def test_gewerke_katalog_vollstaendig(self):
        """Test that Gewerke catalog contains all standard trades"""
        assert "01" in GEWERKE_KATALOG_AT  # Baumeister
        assert "02" in GEWERKE_KATALOG_AT  # Zimmerer
        assert "05" in GEWERKE_KATALOG_AT  # Elektro
        assert "06" in GEWERKE_KATALOG_AT  # Sanitär
        assert "07" in GEWERKE_KATALOG_AT  # HLK

    def test_gewerke_katalog_structure(self):
        """Test that each Gewerk has required fields"""
        for gewerk_nr, gewerk_info in GEWERKE_KATALOG_AT.items():
            assert "name" in gewerk_info
            assert "beschreibung" in gewerk_info
            assert "kostengruppe" in gewerk_info
            assert "typische_einheiten" in gewerk_info
            assert isinstance(gewerk_info["kostengruppe"], int)
            assert isinstance(gewerk_info["typische_einheiten"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
