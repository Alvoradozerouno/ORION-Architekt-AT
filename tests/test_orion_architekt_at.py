"""
Test Suite for orion_architekt_at core functionality
Tests Austrian building regulations, calculations, compliance checks
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orion_architekt_at import (
    berechne_uwert_mehrschicht,
    berechne_stellplaetze,
    pruefe_barrierefreiheit,
    berechne_fluchtweg,
    berechne_tageslicht,
    berechne_abstandsflaechen,
    pruefe_blitzschutz,
    pruefe_rauchableitung,
    pruefe_gefahrenzonen,
    berechne_flaechen_oenorm_b1800,
    generiere_leistungsverzeichnis,
    generiere_raumprogramm,
    # New validation functions
    pruefe_wissensdatenbank,
    pruefe_oib_richtlinien,
    pruefe_oenorm,
    BUNDESLAENDER,
    OIB_RICHTLINIEN_AT
)


class TestBundeslaender:
    """Test Bundesländer data structure"""

    def test_all_bundeslaender_exist(self):
        """Test that all 9 Bundesländer are defined"""
        expected = [
            "burgenland", "kaernten", "niederoesterreich",
            "oberoesterreich", "salzburg", "steiermark",
            "tirol", "vorarlberg", "wien"
        ]
        for bl in expected:
            assert bl in BUNDESLAENDER, f"{bl} not found"

    def test_bundesland_structure(self):
        """Test structure of Bundesland data"""
        for bl_key, bl_data in BUNDESLAENDER.items():
            assert "name" in bl_data
            assert "bauordnung" in bl_data
            assert "oib_2023_status" in bl_data


class TestOIBRichtlinien:
    """Test OIB-Richtlinien data"""

    def test_all_oib_rl_exist(self):
        """Test that all 6 OIB-RL are defined"""
        for i in range(1, 7):
            assert f"OIB-RL {i}" in OIB_RICHTLINIEN_AT

    def test_oib_rl_structure(self):
        """Test structure of OIB-RL data"""
        for rl_key, rl_data in OIB_RICHTLINIEN_AT.items():
            assert "titel" in rl_data
            assert "version" in rl_data
            assert "2023" in rl_data["version"]


class TestUWertBerechnung:
    """Test U-Wert calculations"""

    def test_uwert_simple_wall(self):
        """Test U-value calculation for simple wall"""
        schichten = [
            {"material": "Putz", "dicke_cm": 2, "lambda_wert": 0.87},
            {"material": "Mauerwerk", "dicke_cm": 25, "lambda_wert": 0.21},
            {"material": "Dämmung", "dicke_cm": 16, "lambda_wert": 0.035},
        ]
        result = berechne_uwert_mehrschicht(schichten)
        assert "u_wert" in result
        assert result["u_wert"] > 0
        assert result["u_wert"] < 1.0  # Should be well-insulated

    def test_uwert_oib_konform(self):
        """Test that result indicates OIB compliance"""
        schichten = [
            {"material": "Mauerwerk", "dicke_cm": 30, "lambda_wert": 0.20},
            {"material": "EPS", "dicke_cm": 20, "lambda_wert": 0.035},
        ]
        result = berechne_uwert_mehrschicht(schichten)
        assert "oib_bewertung" in result


class TestStellplatzberechnung:
    """Test parking space calculations"""

    def test_stellplatz_wohnbau_tirol(self):
        """Test parking calculation for residential in Tirol"""
        result = berechne_stellplaetze(
            nutzungsart="wohnbau",
            flaeche_m2=300,
            anzahl_wohnungen=4,
            bundesland="tirol"
        )
        assert "stellplaetze_erforderlich" in result
        assert result["stellplaetze_erforderlich"] >= 4

    def test_stellplatz_wohnbau_wien(self):
        """Test parking calculation for residential in Wien"""
        result = berechne_stellplaetze(
            nutzungsart="wohnbau",
            flaeche_m2=200,
            anzahl_wohnungen=3,
            bundesland="wien"
        )
        assert "stellplaetze_erforderlich" in result
        # Wien requires 1-1.5 per apartment
        assert result["stellplaetze_erforderlich"] >= 3

    def test_stellplatz_buero(self):
        """Test parking calculation for office"""
        result = berechne_stellplaetze(
            nutzungsart="buero",
            flaeche_m2=500,
            bundesland="tirol"
        )
        assert result["stellplaetze_erforderlich"] > 0


class TestBarrierefreiheit:
    """Test accessibility compliance"""

    def test_barrierefreiheit_wien_3og(self):
        """Test Wien requires elevator from 3 floors"""
        result = pruefe_barrierefreiheit(
            gebaeudetyp="mehrfamilienhaus",
            geschosse=3,
            wohnungen_pro_geschoss=2,
            tueren_breite_cm=85,
            aufzug_vorhanden=True,
            bundesland="wien"
        )
        assert result["erfuellt"] == True

    def test_barrierefreiheit_wien_3og_kein_aufzug(self):
        """Test Wien - no elevator at 3 floors fails"""
        result = pruefe_barrierefreiheit(
            gebaeudetyp="mehrfamilienhaus",
            geschosse=3,
            wohnungen_pro_geschoss=2,
            tueren_breite_cm=85,
            aufzug_vorhanden=False,
            bundesland="wien"
        )
        assert result["erfuellt"] == False
        assert any("Aufzug" in m for m in result["mangel"])

    def test_barrierefreiheit_tuerbreite(self):
        """Test door width requirements"""
        result = pruefe_barrierefreiheit(
            gebaeudetyp="mehrfamilienhaus",
            geschosse=2,
            wohnungen_pro_geschoss=2,
            tueren_breite_cm=75,  # Too narrow
            aufzug_vorhanden=False,
            bundesland="tirol"
        )
        assert result["erfuellt"] == False


class TestFluchtwegBerechnung:
    """Test emergency exit calculations"""

    def test_fluchtweg_gk1(self):
        """Test escape route for building class 1"""
        result = berechne_fluchtweg(
            gebaeuedeklasse=1,
            geschosse=2,
            personen=50,
            fluchtweglaenge_m=30,
            anzahl_fluchtwege=1,
            treppenbreite_cm=120,
            bundesland="tirol"
        )
        assert "erfuellt" in result

    def test_fluchtweg_zu_lang(self):
        """Test escape route too long"""
        result = berechne_fluchtweg(
            gebaeuedeklasse=1,
            geschosse=2,
            personen=50,
            fluchtweglaenge_m=50,  # Too long for GK1
            anzahl_fluchtwege=1,
            treppenbreite_cm=120,
            bundesland="tirol"
        )
        assert result["erfuellt"] == False


class TestTageslichtBerechnung:
    """Test daylight calculations"""

    def test_tageslicht_ausreichend(self):
        """Test sufficient daylight"""
        result = berechne_tageslicht(
            raumflaeche_m2=20,
            fensterflaeche_m2=3,
            raumtiefe_m=5,
            fensterhoehe_m=1.5,
            raumtyp="wohnraum"
        )
        assert "tageslichtfaktor" in result
        assert result["bewertung"] != "unzureichend"

    def test_tageslicht_zu_wenig(self):
        """Test insufficient daylight"""
        result = berechne_tageslicht(
            raumflaeche_m2=30,
            fensterflaeche_m2=1,  # Too small
            raumtiefe_m=8,
            fensterhoehe_m=1.0,
            raumtyp="wohnraum"
        )
        assert result["bewertung"] in ["mangelhaft", "unzureichend"]


class TestAbstandsflaechen:
    """Test building setback calculations"""

    def test_abstandsflaechen_tirol(self):
        """Test setback for Tirol"""
        result = berechne_abstandsflaechen(
            gebaeudehöhe_m=10,
            bebauungsart="offen",
            grenztyp="nachbar",
            bundesland="tirol"
        )
        assert "abstand_erforderlich_m" in result
        assert result["abstand_erforderlich_m"] >= 10  # Tirol factor 1.0

    def test_abstandsflaechen_wien(self):
        """Test setback for Wien"""
        result = berechne_abstandsflaechen(
            gebaeudehöhe_m=10,
            bebauungsart="offen",
            grenztyp="nachbar",
            bundesland="wien"
        )
        assert result["abstand_erforderlich_m"] >= 4  # Wien factor 0.4


class TestBlitzschutz:
    """Test lightning protection classification"""

    def test_blitzschutz_wohnhaus(self):
        """Test lightning protection for residential"""
        result = pruefe_blitzschutz(
            gebaeudetyp="wohnhaus",
            hoehe_m=10,
            exponiert=False
        )
        assert "lpk" in result
        assert result["lpk"] in ["LPK I", "LPK II", "LPK III", "LPK IV"]

    def test_blitzschutz_hochhaus(self):
        """Test lightning protection for high-rise"""
        result = pruefe_blitzschutz(
            gebaeudetyp="hochhaus",
            hoehe_m=30,
            exponiert=True
        )
        assert result["lpk"] in ["LPK I", "LPK II"]


class TestRauchableitung:
    """Test smoke extraction requirements"""

    def test_rauchableitung_gk1(self):
        """Test smoke extraction for GK1"""
        result = pruefe_rauchableitung(
            gebaeuedeklasse=1,
            geschosse=2,
            treppenhaus_typ="offen"
        )
        assert "anforderung" in result

    def test_rauchableitung_gk4(self):
        """Test smoke extraction for GK4"""
        result = pruefe_rauchableitung(
            gebaeuedeklasse=4,
            geschosse=6,
            treppenhaus_typ="geschlossen"
        )
        assert "Sicherheitstreppenhaus" in result["anforderung"]


class TestGefahrenzonen:
    """Test hazard zone checks"""

    def test_gefahrenzonen_lawinen(self):
        """Test avalanche check"""
        result = pruefe_gefahrenzonen(
            seehöhe_m=1500,
            gemeinde="St. Johann in Tirol",
            bundesland="tirol"
        )
        assert "gefahren" in result
        assert any("Lawinen" in g for g in result["gefahren"])

    def test_gefahrenzonen_tal(self):
        """Test low altitude - no avalanche"""
        result = pruefe_gefahrenzonen(
            seehöhe_m=500,
            gemeinde="Wien",
            bundesland="wien"
        )
        # Should have less avalanche risk
        assert "gefahren" in result


class TestFlaechenberechnung:
    """Test ÖNORM B 1800 area calculations"""

    def test_flaechen_wohnhaus(self):
        """Test area calculation for residential"""
        result = berechne_flaechen_oenorm_b1800(
            nf_m2=120,
            vf_m2=15,
            ff_m2=8,
            wanddicke_m=0.30,
            geschosshöhe_m=2.8,
            anzahl_geschosse=2
        )
        assert "bgf_m2" in result
        assert "bri_m3" in result
        assert "kompaktheit" in result

    def test_flaechen_kompaktheit(self):
        """Test compactness calculation"""
        result = berechne_flaechen_oenorm_b1800(
            nf_m2=100,
            vf_m2=10,
            ff_m2=5,
            wanddicke_m=0.25,
            geschosshöhe_m=2.7,
            anzahl_geschosse=2
        )
        assert result["kompaktheit"]["av_verhaeltnis"] > 0


class TestLeistungsverzeichnis:
    """Test service specification generation"""

    def test_lv_neubau(self):
        """Test LV for new construction"""
        result = generiere_leistungsverzeichnis(
            projektart="neubau",
            bgf_m2=200,
            gebaeudetyp="einfamilienhaus"
        )
        assert "gewerke" in result
        assert len(result["gewerke"]) >= 10
        assert "gesamtsumme_netto" in result

    def test_lv_sanierung(self):
        """Test LV for renovation"""
        result = generiere_leistungsverzeichnis(
            projektart="sanierung",
            bgf_m2=150,
            gebaeudetyp="mehrfamilienhaus"
        )
        assert result["gesamtsumme_netto"] > 0


class TestRaumprogramm:
    """Test room program generation"""

    def test_raumprogramm_familie(self):
        """Test room program for family"""
        result = generiere_raumprogramm(
            haushaltsgroesse=4,
            wohnwunsch_typ="komfortabel",
            budget_euro=500000,
            besondere_wuensche=["homeoffice"]
        )
        assert "raeume" in result
        assert "nf_gesamt_m2" in result
        assert any("Home-Office" in r["raum"] for r in result["raeume"])

    def test_raumprogramm_budget_check(self):
        """Test budget checking"""
        result = generiere_raumprogramm(
            haushaltsgroesse=2,
            wohnwunsch_typ="kompakt",
            budget_euro=200000,
            besondere_wuensche=[]
        )
        assert "budget_status" in result
        assert "schaetzkosten_euro" in result


class TestValidationFunctions:
    """Test new validation functions"""

    def test_pruefe_wissensdatenbank(self):
        """Test knowledge base validation"""
        result = pruefe_wissensdatenbank(vollstaendig=False)
        assert "status" in result

    def test_pruefe_oib_richtlinien(self):
        """Test OIB guidelines check"""
        result = pruefe_oib_richtlinien()
        assert "status" in result or "aktuelle_version" in result

    def test_pruefe_oenorm(self):
        """Test ÖNORM check"""
        result = pruefe_oenorm("B 1800")
        assert "norm" in result or "nachricht" in result


# Integration tests
class TestIntegration:
    """Integration tests for complete workflows"""

    def test_complete_building_check_workflow(self):
        """Test complete building compliance workflow"""
        # 1. Stellplatz
        stellplatz = berechne_stellplaetze(
            nutzungsart="wohnbau",
            flaeche_m2=250,
            anzahl_wohnungen=3,
            bundesland="tirol"
        )
        assert stellplatz["stellplaetze_erforderlich"] > 0

        # 2. Barrierefreiheit
        barrierefrei = pruefe_barrierefreiheit(
            gebaeudetyp="mehrfamilienhaus",
            geschosse=3,
            wohnungen_pro_geschoss=1,
            tueren_breite_cm=85,
            aufzug_vorhanden=False,
            bundesland="tirol"
        )
        assert "erfuellt" in barrierefrei

        # 3. Fluchtweg
        fluchtweg = berechne_fluchtweg(
            gebaeuedeklasse=2,
            geschosse=3,
            personen=30,
            fluchtweglaenge_m=35,
            anzahl_fluchtwege=1,
            treppenbreite_cm=120,
            bundesland="tirol"
        )
        assert "erfuellt" in fluchtweg


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
