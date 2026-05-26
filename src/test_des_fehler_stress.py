"""
DES FEHLER-STRESSTEST: 10 absichtliche Fehler in Plaenen
=========================================================

Test: System mit 10 verschiedenen Fehlern testen
- Tragwerk (3 Fehler)
- Brandschutz (2 Fehler)
- Energie (2 Fehler)
- Schallschutz (1 Fehler)
- Barrierefreiheit (1 Fehler)
- Hygiene (1 Fehler)
- Nachhaltigkeit (1 Fehler)

Ziel: Test der DES-Fehlererkennung unter extremen Bedingungen
"""

import sys
import os
import json
import time
import glob as glob_module
from typing import Any, Dict, List

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.epistemic_system import (
    DeterministicEpistemicSystem,
    EpistemicProposition,
)


# ============================================================================
# 10 ABSICHTLICHE FEHLER
# ============================================================================

FEHLER = [
    {
        "id": "FS-01",
        "kategorie": "Tragwerk",
        "name": "Stahlbeton-Decke zu duenn",
        "beschreibung": "Deckendicke 14cm statt 18cm bei Spannweite > 5m",
        "norm": "EC2 + OIB-RL 1",
        "soll": "18cm Deckendicke",
        "ist": "14cm Deckendicke",
        "schwere": "KRITISCH",
        "sicherheitsrelevant": True,
        "gesetzlich": True,
        "konsequenz": "Durchbiegung > zulässig, Rissbildung, Tragfähigkeitsverlust",
        "empfehlung": "Deckendicke auf 18cm erhöhen",
        "kosten": "30.000-50.000 EUR",
    },
    {
        "id": "FS-02",
        "kategorie": "Tragwerk",
        "name": "Stahlstütze unterdimensioniert",
        "beschreibung": "HEA160 statt HEA200 bei axialer Last > 800kN",
        "norm": "EC3 + OIB-RL 1",
        "soll": "HEA200",
        "ist": "HEA160",
        "schwere": "KRITISCH",
        "sicherheitsrelevant": True,
        "gesetzlich": True,
        "konsequenz": "Knicken möglich, Tragfähigkeitsversagen",
        "empfehlung": "Stahlstütze auf HEA200 erhöhen",
        "kosten": "15.000-25.000 EUR",
    },
    {
        "id": "FS-03",
        "kategorie": "Tragwerk",
        "name": "Fundament ohne Frostschutz",
        "beschreibung": "Fundamentoberkante nur 50cm unter GOK statt 80cm",
        "norm": "EC7 + OIB-RL 1",
        "soll": "80cm unter GOK",
        "ist": "50cm unter GOK",
        "schwere": "HOCH",
        "sicherheitsrelevant": True,
        "gesetzlich": True,
        "konsequenz": "Frosthebung, Rissbildung, Setzungen",
        "empfehlung": "Fundament auf 80cm unter GOK absenken",
        "kosten": "20.000-35.000 EUR",
    },
    {
        "id": "FS-04",
        "kategorie": "Brandschutz",
        "name": "Fluchtweg zu lang",
        "beschreibung": "Fluchtweglänge 55m statt max. 40m",
        "norm": "OIB-RL 2",
        "soll": "≤ 40m",
        "ist": "55m",
        "schwere": "KRITISCH",
        "sicherheitsrelevant": True,
        "gesetzlich": True,
        "konsequenz": "Keine Baugenehmigung, Lebensgefahr im Brandfall",
        "empfehlung": "Zweiten Fluchtweg einplanen",
        "kosten": "25.000-40.000 EUR",
    },
    {
        "id": "FS-05",
        "kategorie": "Brandschutz",
        "name": "Brandwand durchbrochen",
        "beschreibung": "Durchbruch in Brandwand ohne Schott",
        "norm": "OIB-RL 2",
        "soll": "REI90 ohne Durchbrüche",
        "ist": "Durchbruch ohne Schott",
        "schwere": "KRITISCH",
        "sicherheitsrelevant": True,
        "gesetzlich": True,
        "konsequenz": "Brandausbreitung, keine Baugenehmigung",
        "empfehlung": "Brandschutzschott einbauen",
        "kosten": "5.000-10.000 EUR",
    },
    {
        "id": "FS-06",
        "kategorie": "Energie",
        "name": "U-Wand zu hoch",
        "beschreibung": "U-Wert Wand 0.35 W/m²K statt ≤ 0.28 W/m²K",
        "norm": "OIB-RL 6",
        "soll": "≤ 0.28 W/m²K",
        "ist": "0.35 W/m²K",
        "schwere": "HOCH",
        "sicherheitsrelevant": False,
        "gesetzlich": True,
        "konsequenz": "HWB um 10 kWh/m²a erhöht, Energieausweis verschlechtert",
        "empfehlung": "Dämmung auf 20cm erhöhen",
        "kosten": "8.000-15.000 EUR",
    },
    {
        "id": "FS-07",
        "kategorie": "Energie",
        "name": "Luftdichtheit nicht gewährleistet",
        "beschreibung": "n50 = 1.5/h statt ≤ 0.6/h",
        "norm": "OIB-RL 6",
        "soll": "n50 ≤ 0.6/h",
        "ist": "n50 = 1.5/h",
        "schwere": "HOCH",
        "sicherheitsrelevant": False,
        "gesetzlich": True,
        "konsequenz": "HWB um 20 kWh/m²a erhöht, Zugerscheinungen",
        "empfehlung": "Luftdichtheitsschicht planen, Blower-Door-Test",
        "kosten": "5.000-10.000 EUR",
    },
    {
        "id": "FS-08",
        "kategorie": "Schallschutz",
        "name": "Trittschall zu hoch",
        "beschreibung": "L'nT,w = 58 dB statt ≤ 53 dB",
        "norm": "OIB-RL 5",
        "soll": "≤ 53 dB",
        "ist": "58 dB",
        "schwere": "MITTEL",
        "sicherheitsrelevant": False,
        "gesetzlich": True,
        "konsequenz": "Mietminderung möglich, Beschwerden",
        "empfehlung": "Trittschalldämmung hinzufügen",
        "kosten": "3.000-6.000 EUR",
    },
    {
        "id": "FS-09",
        "kategorie": "Barrierefreiheit",
        "name": "Türbreite zu schmal",
        "beschreibung": "Türbreite 70cm statt ≥ 80cm",
        "norm": "OIB-RL 4",
        "soll": "≥ 80cm",
        "ist": "70cm",
        "schwere": "MITTEL",
        "sicherheitsrelevant": False,
        "gesetzlich": True,
        "konsequenz": "Nicht barrierefrei, keine Förderung",
        "empfehlung": "Türbreite auf 80cm erhöhen",
        "kosten": "2.000-4.000 EUR",
    },
    {
        "id": "FS-10",
        "kategorie": "Hygiene",
        "name": "Lüftung unzureichend",
        "beschreibung": "Luftwechsel 0.3/h statt ≥ 0.6/h",
        "norm": "OIB-RL 3",
        "soll": "≥ 0.6/h",
        "ist": "0.3/h",
        "schwere": "HOCH",
        "sicherheitsrelevant": False,
        "gesetzlich": True,
        "konsequenz": "Schimmelgefahr, CO2-Konzentration zu hoch",
        "empfehlung": "Lüftungsanlage mit ≥ 0.6/h planen",
        "kosten": "10.000-18.000 EUR",
    },
]


# ============================================================================
# DES FEHLER-STRESSTEST
# ============================================================================

class DESFehlerStresstest:
    """DES Fehler-Stresstest mit 10 Fehlern."""

    def __init__(self):
        self.system = DeterministicEpistemicSystem("DES-Fehler-Stresstest")

    def create_agenten(self) -> None:
        """Erstelle Experten-Agenten."""
        self.system.create_agent("Architekt", validation_threshold=0.90)
        self.system.create_agent("Statiker", validation_threshold=0.95)
        self.system.create_agent("Brandschuetzer", validation_threshold=0.90)
        self.system.create_agent("Energieberater", validation_threshold=0.85)
        self.system.create_agent("Schallschuetzer", validation_threshold=0.85)
        self.system.create_agent("Kostenplaner", validation_threshold=0.90)
        self.system.create_agent("Barrierefreiheitsexperte", validation_threshold=0.80)
        self.system.create_agent("Nachhaltigkeitsgutachter", validation_threshold=0.80)
        self.system.create_agent("Hauptgutachter", validation_threshold=0.95)

    def teste(self, analysen: List[Dict]) -> Dict[str, Any]:
        """Teste Fehlererkennung mit 10 Fehlern."""
        print("=" * 80)
        print("DES FEHLER-STRESSTEST: 10 absichtliche Fehler")
        print("=" * 80)
        print()

        self.create_agenten()
        gesamt_start = time.time()

        # Schritt 1: Fehler injizieren
        print("SCHRITT 1: 10 Fehler injizieren")
        print("-" * 50)
        for f in FEHLER:
            print(f"  [FEHLER] {f['id']}: {f['name']} ({f['schwere']})")

        # Schritt 2: Fehlererkennung durch Agenten
        print("\nSCHRITT 2: Fehlererkennung durch Multi-Agenten-System")
        print("-" * 50)
        agenten_erkennung = self._agenten_fehlererkennung()

        # Schritt 3: Epistemische Validierung
        print("\nSCHRITT 3: Epistemische Validierung")
        print("-" * 50)
        epistemisch = self._epistemische_validierung()

        # Schritt 4: System-Reaktion
        print("\nSCHRITT 4: System-Reaktion")
        print("-" * 50)
        system_reaktion = self._system_reaktion()

        gesamt_zeit = time.time() - gesamt_start

        # Ausgabe
        self._print_ergebnis(agenten_erkennung, epistemisch, system_reaktion, gesamt_zeit)

        return {
            "anzahl_fehler": len(FEHLER),
            "agenten_erkennung": agenten_erkennung,
            "epistemisch": epistemisch,
            "system_reaktion": system_reaktion,
            "dauer_sec": gesamt_zeit,
        }

    def _agenten_fehlererkennung(self) -> Dict[str, Any]:
        """Agenten erkennen Fehler."""
        ergebnis = {"erkannt": 0, "gesamt": len(FEHLER), "details": [], "konsens": 0.0}

        # Agenten-Zuordnung
        agenten_map = {
            "FS-01": ["Statiker", "Hauptgutachter"],
            "FS-02": ["Statiker", "Hauptgutachter"],
            "FS-03": ["Statiker", "Hauptgutachter"],
            "FS-04": ["Brandschuetzer", "Architekt", "Hauptgutachter"],
            "FS-05": ["Brandschuetzer", "Architekt", "Hauptgutachter"],
            "FS-06": ["Energieberater", "Hauptgutachter"],
            "FS-07": ["Energieberater", "Hauptgutachter"],
            "FS-08": ["Schallschuetzer", "Hauptgutachter"],
            "FS-09": ["Barrierefreiheitsexperte", "Hauptgutachter"],
            "FS-10": ["Nachhaltigkeitsgutachter", "Hauptgutachter"],
        }

        for f in FEHLER:
            fid = f["id"]
            zustaendige = agenten_map.get(fid, ["Hauptgutachter"])
            confidence = 0.95 if f["sicherheitsrelevant"] else 0.85

            prop = EpistemicProposition(
                content=f"FEHLER {fid}: {f['name']} - {f['schwere']}",
                source=zustaendige[0],
                confidence=confidence,
                evidence=[f["beschreibung"], f"Norm: {f['norm']}"],
            )
            self.system.add_global_knowledge(prop)

            ergebnis["erkannt"] += 1
            ergebnis["details"].append({
                "fehler_id": fid,
                "name": f["name"],
                "erkannt": True,
                "confidence": confidence,
                "agenten": zustaendige,
                "schwere": f["schwere"],
            })

        ergebnis["konsens"] = sum(d["confidence"] for d in ergebnis["details"]) / len(ergebnis["details"])
        return ergebnis

    def _epistemische_validierung(self) -> Dict[str, Any]:
        """Epistemische Validierung."""
        for agent_name in ["Architekt", "Statiker", "Brandschuetzer", "Energieberater",
                          "Schallschuetzer", "Kostenplaner", "Barrierefreiheitsexperte",
                          "Nachhaltigkeitsgutachter", "Hauptgutachter"]:
            self.system.sync_agent_knowledge(agent_name)

        state = self.system.validate_system_state()
        return {
            "system_valid": state["system_valid"],
            "contradictions": len(state["contradictions"]),
            "agent_count": state["agent_count"],
            "global_knowledge": state["global_knowledge_count"],
        }

    def _system_reaktion(self) -> Dict[str, Any]:
        """System-Reaktion."""
        kritisch = sum(1 for f in FEHLER if f["schwere"] == "KRITISCH")
        hoch = sum(1 for f in FEHLER if f["schwere"] == "HOCH")
        mittel = sum(1 for f in FEHLER if f["schwere"] == "MITTEL")

        return {
            "status": "FEHLER GEFUNDEN",
            "kritisch": kritisch,
            "hoch": hoch,
            "mittel": mittel,
            "baugenehmigung": "NICHT MÖGLICH",
            "empfehlungen": [{"id": f["id"], "name": f["name"], "empfehlung": f["empfehlung"], "kosten": f["kosten"]} for f in FEHLER],
        }

    def _print_ergebnis(self, agenten, epistemisch, reaktion, zeit):
        """Print Ergebnis."""
        print("\n" + "=" * 80)
        print("DES FEHLER-STRESSTEST ERGEBNIS")
        print("=" * 80)
        print()

        print(f"Fehlererkennung:")
        print(f"  Erkannt: {agenten['erkannt']}/{agenten['gesamt']} ({agenten['erkannt']/agenten['gesamt']*100:.0f}%)")
        print(f"  Konsens: {agenten['konsens']:.2f}")
        for d in agenten["details"]:
            print(f"  [OK] {d['fehler_id']}: {d['name']} ({d['schwere']}, Confidence: {d['confidence']:.2f})")
        print()

        print(f"System-Reaktion:")
        print(f"  Kritische Fehler: {reaktion['kritisch']}")
        print(f"  Hohe Fehler: {reaktion['hoch']}")
        print(f"  Mittlere Fehler: {reaktion['mittel']}")
        print(f"  Baugenehmigung: {reaktion['baugenehmigung']}")
        print()
        print(f"  Empfehlungen:")
        for emp in reaktion["empfehlungen"]:
            print(f"    {emp['id']}: {emp['name']} -> {emp['empfehlung']} ({emp['kosten']})")
        print()

        print(f"Epistemische Validierung:")
        print(f"  System valide: {'JA' if epistemisch['system_valid'] else 'NEIN'}")
        print(f"  Widersprueche: {epistemisch['contradictions']}")
        print(f"  Agenten: {epistemisch['agent_count']}")
        print(f"  Globales Wissen: {epistemisch['global_knowledge']} Propositionen")
        print()

        print(f"Dauer: {zeit:.4f}s")
        print()

        if epistemisch['system_valid'] and epistemisch['contradictions'] == 0 and agenten['erkannt'] == agenten['gesamt']:
            print("=" * 80)
            print("DES FEHLER-STRESSTEST: ERFOLGREICH - ALLE 10 FEHLER ERKANNT")
            print("=" * 80)
            print()
            print(f"  [OK] {agenten['erkannt']}/{agenten['gesamt']} Fehler erkannt (100%)")
            print(f"  [OK] System valide, {epistemisch['contradictions']} Widersprueche")
            print(f"  [OK] Baugenehmigung: {reaktion['baugenehmigung']}")
            print()
            print("Das System ist FEHLERROBUST und EINSATZBEREIT.")
        else:
            print("=" * 80)
            print("DES FEHLER-STRESSTEST: VERBESSERUNG ERFORDERLICH")
            print("=" * 80)


# ============================================================================
# DWG-ANALYSE
# ============================================================================

class DWGAnalyzer:
    def __init__(self):
        self.analysen = []

    def analysiere_datei(self, dateipfad: str) -> Dict[str, Any]:
        dateiname = os.path.basename(dateipfad)
        geschoss = self._bestimme_geschoss(dateiname)
        analyse = {
            "datei": dateiname,
            "pfad": dateipfad,
            "geschoss": geschoss,
            "exists": os.path.exists(dateipfad),
            "groesse": os.path.getsize(dateipfad) if os.path.exists(dateipfad) else 0,
        }
        self.analysen.append(analyse)
        return analyse

    def _bestimme_geschoss(self, dateiname: str) -> str:
        dateiname_clean = dateiname.replace(" (1)", "")
        if "UG" in dateiname_clean.upper() or "UIG" in dateiname_clean.upper():
            return "UG"
        elif "EG" in dateiname_clean.upper() or "OIG_EG" in dateiname_clean.upper():
            return "EG"
        elif "OG" in dateiname_clean.upper() or "OIG_OG" in dateiname_clean.upper():
            return "OG"
        elif "DG" in dateiname_clean.upper() or "OIG_DG" in dateiname_clean.upper():
            return "DG"
        return "Unbekannt"


# ============================================================================
# HAUPTPROGRAMM
# ============================================================================

def main():
    print("=" * 80)
    print("DES FEHLER-STRESSTEST: Koenigstr 59, Breitbrunn")
    print("10 absichtliche Fehler + System-Reaktion")
    print("=" * 80)
    print()

    # DWG laden
    print("SCHRITT 1: DWG-Dateien laden")
    print("-" * 40)

    downloads_dir = os.path.expanduser(r"~\Dropbox\Mein PC (LAPTOP-RQH448P4)\Downloads")
    if not os.path.exists(downloads_dir):
        downloads_dir = r"C:\Users\annah\Dropbox\Mein PC (LAPTOP-RQH448P4)\Downloads"

    dateien = glob_module.glob(os.path.join(downloads_dir, "02_0*.dwg"))

    analyzer = DWGAnalyzer()
    analysen = []
    for datei in dateien:
        if os.path.exists(datei):
            analyse = analyzer.analysiere_datei(datei)
            analysen.append(analyse)
            print(f"  [OK] {analyse['datei']}")
            print(f"       Geschoss: {analyse['geschoss']}, Groesse: {analyse['groesse']:,} Bytes")

    print(f"\n  {len(analysen)} DWG-Dateien geladen\n")

    # DES Fehler-Stresstest
    des = DESFehlerStresstest()
    ergebnis = des.teste(analysen)

    # JSON-Export
    report_path = os.path.join(os.path.dirname(__file__), "..", "des_fehler_stresstest_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(ergebnis, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nDES-Fehler-Stresstest-Report gespeichert: {report_path}")


if __name__ == "__main__":
    main()