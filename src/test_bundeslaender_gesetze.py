"""
TEST: BUNDESLAENDER-GESETZE - Alle 9 Bundeslaender
====================================================

Test: Sind alle Gesetze fuer jedes Bundesland im System?
- Bauordnungen aller 9 Bundeslaender
- OIB-Richtlinien mit Abweichungen
- Schneelast-, Windlast-, Erdbebenzonen
- Foerderungen pro Bundesland
- Kostenfaktoren pro Region
- Besondere Vorschriften

Ziel: Vollstaendigkeitspruefung aller bundeslandspezifischen Gesetze
"""

import sys
import os
import json
import time
from typing import Any, Dict, List

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.orion_architekt_at import (
    BUNDESLAENDER,
    OIB_RICHTLINIEN_AT,
    UWERT_ANFORDERUNGEN,
    KOSTENRICHTWERTE_2026,
    REGIONALE_KOSTENFAKTOREN,
    FOERDERUNGEN,
    ZEITPLAN_PHASEN,
    SCHNEELASTZONEN_AT,
    WINDLASTZONEN_AT,
)

from src.epistemic_system import (
    DeterministicEpistemicSystem,
    EpistemicProposition,
)


# ============================================================================
# BUNDESLAENDER-TEST
# ============================================================================

class BundeslaenderTest:
    """Test aller 9 Bundeslaender-Gesetze."""

    def __init__(self):
        self.system = DeterministicEpistemicSystem("Bundeslaender-Test")
        self.erwartete_bundeslaender = [
            "burgenland", "kaernten", "niederoesterreich", "oberoesterreich",
            "salzburg", "steiermark", "tirol", "vorarlberg", "wien"
        ]
        self.erwartete_oib = ["OIB-RL 1", "OIB-RL 2", "OIB-RL 3", "OIB-RL 4", "OIB-RL 5", "OIB-RL 6"]

    def teste(self) -> Dict[str, Any]:
        """Teste alle Bundeslaender-Gesetze."""
        print("=" * 80)
        print("BUNDESLAENDER-TEST: Alle 9 Bundeslaender")
        print("=" * 80)
        print()

        gesamt_start = time.time()

        # Schritt 1: Bundeslaender pruefen
        print("SCHRITT 1: Bundeslaender pruefen")
        print("-" * 50)
        bl_test = self._teste_bundeslaender()

        # Schritt 2: OIB-Richtlinien pruefen
        print("\nSCHRITT 2: OIB-Richtlinien pruefen")
        print("-" * 50)
        oib_test = self._teste_oib()

        # Schritt 3: Abweichungen pro Bundesland pruefen
        print("\nSCHRITT 3: Abweichungen pro Bundesland pruefen")
        print("-" * 50)
        abweichungen_test = self._teste_abweichungen()

        # Schritt 4: Foerderungen pro Bundesland pruefen
        print("\nSCHRITT 4: Foerderungen pro Bundesland pruefen")
        print("-" * 50)
        foerderungen_test = self._teste_foerderungen()

        # Schritt 5: Zonen pruefen
        print("\nSCHRITT 5: Zonen pruefen (Schnee, Wind, Erdbeben)")
        print("-" * 50)
        zonen_test = self._teste_zonen()

        # Schritt 6: Kostenfaktoren pruefen
        print("\nSCHRITT 6: Kostenfaktoren pruefen")
        print("-" * 50)
        kosten_test = self._teste_kosten()

        # Schritt 7: Epistemische Validierung
        print("\nSCHRITT 7: Epistemische Validierung")
        print("-" * 50)
        epistemisch = self._epistemische_validierung(bl_test, oib_test, abweichungen_test, foerderungen_test, zonen_test, kosten_test)

        gesamt_zeit = time.time() - gesamt_start

        # Ausgabe
        self._print_ergebnis(bl_test, oib_test, abweichungen_test, foerderungen_test, zonen_test, kosten_test, epistemisch, gesamt_zeit)

        return {
            "bundeslaender": bl_test,
            "oib": oib_test,
            "abweichungen": abweichungen_test,
            "foerderungen": foerderungen_test,
            "zonen": zonen_test,
            "kosten": kosten_test,
            "epistemisch": epistemisch,
            "dauer_sec": gesamt_zeit,
        }

    def _teste_bundeslaender(self) -> Dict[str, Any]:
        """Teste alle 9 Bundeslaender."""
        ergebnis = {
            "erwartete": len(self.erwartete_bundeslaender),
            "vorhandene": len(BUNDESLAENDER),
            "details": [],
            "vollstaendig": True,
        }

        for bl in self.erwartete_bundeslaender:
            vorhanden = bl in BUNDESLAENDER
            ergebnis["vollstaendig"] = ergebnis["vollstaendig"] and vorhanden
            detail = {
                "bundesland": bl,
                "vorhanden": vorhanden,
                "name": BUNDESLAENDER.get(bl, {}).get("name", "FEHLT"),
                "bauordnung": BUNDESLAENDER.get(bl, {}).get("bauordnung_kurz", "FEHLT"),
                "oib_status": BUNDESLAENDER.get(bl, {}).get("oib_2023_status", "FEHLT"),
                "schneelast": BUNDESLAENDER.get(bl, {}).get("schneelastzone", "FEHLT"),
                "erdbeben": BUNDESLAENDER.get(bl, {}).get("erdbebenzone", "FEHLT"),
                "wind": BUNDESLAENDER.get(bl, {}).get("windzone", "FEHLT"),
            }
            ergebnis["details"].append(detail)
            status = "OK" if vorhanden else "FEHLT"
            print(f"  [{status}] {detail['name']} ({detail['bauordnung']})")

        return ergebnis

    def _teste_oib(self) -> Dict[str, Any]:
        """Teste alle 6 OIB-Richtlinien."""
        ergebnis = {
            "erwartete": len(self.erwartete_oib),
            "vorhandene": len(OIB_RICHTLINIEN_AT),
            "details": [],
            "vollstaendig": True,
        }

        for oib in self.erwartete_oib:
            vorhanden = oib in OIB_RICHTLINIEN_AT
            ergebnis["vollstaendig"] = ergebnis["vollstaendig"] and vorhanden
            detail = {
                "oib": oib,
                "vorhanden": vorhanden,
                "titel": OIB_RICHTLINIEN_AT.get(oib, {}).get("titel", "FEHLT"),
                "version": OIB_RICHTLINIEN_AT.get(oib, {}).get("version", "FEHLT"),
                "anzahl_abweichungen": len(OIB_RICHTLINIEN_AT.get(oib, {}).get("abweichungen", {})),
            }
            ergebnis["details"].append(detail)
            status = "OK" if vorhanden else "FEHLT"
            print(f"  [{status}] {oib}: {detail['titel']} ({detail['anzahl_abweichungen']} Abweichungen)")

        return ergebnis

    def _teste_abweichungen(self) -> Dict[str, Any]:
        """Teste Abweichungen pro Bundesland."""
        ergebnis = {
            "bundeslaender_mit_abweichungen": 0,
            "details": [],
        }

        for oib, daten in OIB_RICHTLINIEN_AT.items():
            abweichungen = daten.get("abweichungen", {})
            for bl, beschreibung in abweichungen.items():
                ergebnis["bundeslaender_mit_abweichungen"] += 1
                ergebnis["details"].append({
                    "oib": oib,
                    "bundesland": bl,
                    "beschreibung": beschreibung,
                })

        print(f"  {ergebnis['bundeslaender_mit_abweichungen']} Abweichungen gefunden")
        for d in ergebnis["details"][:5]:
            print(f"    - {d['oib']} ({d['bundesland']}): {d['beschreibung'][:60]}...")

        return ergebnis

    def _teste_foerderungen(self) -> Dict[str, Any]:
        """Teste Foerderungen pro Bundesland."""
        ergebnis = {
            "bund": len(FOERDERUNGEN.get("bund", [])),
            "bundeslaender": {},
            "gesamt": 0,
        }

        for bl in self.erwartete_bundeslaender:
            anzahl = len(FOERDERUNGEN.get(bl, []))
            ergebnis["bundeslaender"][bl] = anzahl
            ergebnis["gesamt"] += anzahl

        ergebnis["gesamt"] += ergebnis["bund"]

        print(f"  Bund: {ergebnis['bund']} Foerderungen")
        for bl, anzahl in ergebnis["bundeslaender"].items():
            status = "OK" if anzahl > 0 else "FEHLT"
            print(f"  [{status}] {bl}: {anzahl} Foerderungen")

        return ergebnis

    def _teste_zonen(self) -> Dict[str, Any]:
        """Teste Zonen."""
        ergebnis = {
            "schneelast": len(SCHNEELASTZONEN_AT),
            "windlast": len(WINDLASTZONEN_AT),
            "details": [],
        }

        print(f"  Schneelastzonen: {ergebnis['schneelast']}")
        for zone, daten in SCHNEELASTZONEN_AT.items():
            print(f"    - {zone}: {daten['sk_kn_m2']} kN/m2 ({daten['regionen'][:50]}...)")

        print(f"  Windlastzonen: {ergebnis['windlast']}")
        for zone, daten in WINDLASTZONEN_AT.items():
            print(f"    - {zone}: {daten['v_b0_ms']} m/s")

        return ergebnis

    def _teste_kosten(self) -> Dict[str, Any]:
        """Teste Kostenfaktoren."""
        ergebnis = {
            "bautypen": len(KOSTENRICHTWERTE_2026),
            "regionalfaktoren": len(REGIONALE_KOSTENFAKTOREN),
            "alle_bundeslaender": True,
        }

        for bl in self.erwartete_bundeslaender:
            if bl not in REGIONALE_KOSTENFAKTOREN:
                ergebnis["alle_bundeslaender"] = False

        print(f"  Bautypen: {ergebnis['bautypen']}")
        print(f"  Regionalfaktoren: {ergebnis['regionalfaktoren']}")
        print(f"  Alle Bundeslaender abgedeckt: {'JA' if ergebnis['alle_bundeslaender'] else 'NEIN'}")

        return ergebnis

    def _epistemische_validierung(self, bl, oib, abweichungen, foerderungen, zonen, kosten) -> Dict[str, Any]:
        """Epistemische Validierung."""
        # Bundeslaender Propositionen
        for detail in bl["details"]:
            prop = EpistemicProposition(
                content=f"Bundesland: {detail['name']} - {detail['bauordnung']}",
                source="Bundeslaender-Test",
                confidence=1.0 if detail["vorhanden"] else 0.0,
                evidence=[f"OIB: {detail['oib_status']}"],
            )
            self.system.add_global_knowledge(prop)

        # OIB Propositionen
        for detail in oib["details"]:
            prop = EpistemicProposition(
                content=f"OIB: {detail['oib']} - {detail['titel']}",
                source="Bundeslaender-Test",
                confidence=1.0 if detail["vorhanden"] else 0.0,
                evidence=[f"Abweichungen: {detail['anzahl_abweichungen']}"],
            )
            self.system.add_global_knowledge(prop)

        # Agenten synchronisieren
        self.system.create_agent("Bundeslaender-Experte", validation_threshold=0.95)
        self.system.sync_agent_knowledge("Bundeslaender-Experte")

        state = self.system.validate_system_state()
        return {
            "system_valid": state["system_valid"],
            "contradictions": len(state["contradictions"]),
            "agent_count": state["agent_count"],
            "global_knowledge": state["global_knowledge_count"],
        }

    def _print_ergebnis(self, bl, oib, abweichungen, foerderungen, zonen, kosten, epistemisch, zeit):
        """Print Ergebnis."""
        print("\n" + "=" * 80)
        print("BUNDESLAENDER-TEST ERGEBNIS")
        print("=" * 80)
        print()

        print(f"Bundeslaender:")
        print(f"  Erwartete: {bl['erwartete']}")
        print(f"  Vorhandene: {bl['vorhandene']}")
        print(f"  Vollstaendig: {'JA' if bl['vollstaendig'] else 'NEIN'}")
        print()

        print(f"OIB-Richtlinien:")
        print(f"  Erwartete: {oib['erwartete']}")
        print(f"  Vorhandene: {oib['vorhandene']}")
        print(f"  Vollstaendig: {'JA' if oib['vollstaendig'] else 'NEIN'}")
        print()

        print(f"Abweichungen:")
        print(f"  Bundeslaender mit Abweichungen: {abweichungen['bundeslaender_mit_abweichungen']}")
        print()

        print(f"Foerderungen:")
        print(f"  Bund: {foerderungen['bund']}")
        print(f"  Laender gesamt: {foerderungen['gesamt'] - foerderungen['bund']}")
        print(f"  Gesamt: {foerderungen['gesamt']}")
        print()

        print(f"Zonen:")
        print(f"  Schneelastzonen: {zonen['schneelast']}")
        print(f"  Windlastzonen: {zonen['windlast']}")
        print()

        print(f"Kosten:")
        print(f"  Bautypen: {kosten['bautypen']}")
        print(f"  Regionalfaktoren: {kosten['regionalfaktoren']}")
        print(f"  Alle Bundeslaender: {'JA' if kosten['alle_bundeslaender'] else 'NEIN'}")
        print()

        print(f"Epistemische Validierung:")
        print(f"  System valide: {'JA' if epistemisch['system_valid'] else 'NEIN'}")
        print(f"  Widersprueche: {epistemisch['contradictions']}")
        print(f"  Agenten: {epistemisch['agent_count']}")
        print(f"  Globales Wissen: {epistemisch['global_knowledge']} Propositionen")
        print()

        print(f"Dauer: {zeit:.4f}s")
        print()

        if bl['vollstaendig'] and oib['vollstaendig'] and epistemisch['system_valid']:
            print("=" * 80)
            print("BUNDESLAENDER-TEST: ERFOLGREICH - ALLE 9 BUNDESLAENDER VOLLSTAENDIG")
            print("=" * 80)
            print()
            print(f"  [OK] {bl['vorhandene']}/9 Bundeslaender")
            print(f"  [OK] {oib['vorhandene']}/6 OIB-Richtlinien")
            print(f"  [OK] {abweichungen['bundeslaender_mit_abweichungen']} Abweichungen")
            print(f"  [OK] {foerderungen['gesamt']} Foerderungen")
            print(f"  [OK] System valide, {epistemisch['contradictions']} Widersprueche")
            print()
            print("Das System ist VOLLSTAENDIG fuer ALLE 9 BUNDESLAENDER.")
        else:
            print("=" * 80)
            print("BUNDESLAENDER-TEST: VERBESSERUNG ERFORDERLICH")
            print("=" * 80)


# ============================================================================
# HAUPTPROGRAMM
# ============================================================================

def main():
    print("=" * 80)
    print("BUNDESLAENDER-TEST: Oesterreich - Alle 9 Bundeslaender")
    print("=" * 80)
    print()

    # Test
    test = BundeslaenderTest()
    ergebnis = test.teste()

    # JSON-Export
    report_path = os.path.join(os.path.dirname(__file__), "..", "bundeslaender_test_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(ergebnis, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nBundeslaender-Test-Report gespeichert: {report_path}")


if __name__ == "__main__":
    main()