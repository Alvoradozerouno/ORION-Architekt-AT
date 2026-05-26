"""
QUANTITY EXTRACTOR - Massenermittlung aus CAD-Plänen
=====================================================

Extrahiert Mengen, Flächen, Volumina aus CAD-Geometrie.
Berechnet Baumassen für Kostenplanung und Ausschreibung.

Autor: Baumeister Tool Austria Team
Datum: 2026-05-26
"""

import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class QuantityResult:
    """Ergebnis der Massenermittlung."""
    flaeche_gesamt: float = 0.0
    umfang_gesamt: float = 0.0
    volumen_gesamt: float = 0.0
    raum_groessen: Dict[str, float] = field(default_factory=dict)
    wand_flaechen: Dict[str, float] = field(default_factory=dict)
    oeffnungen: Dict[str, int] = field(default_factory=dict)
    material_mengen: Dict[str, float] = field(default_factory=dict)


class QuantityExtractor:
    """Massenermittlung aus CAD-Geometrie."""

    def __init__(self):
        self.hoehe_geschoss = 3.0  # Standard-Geschosshöhe in Metern

    def extract(self, geometrie: List[Dict[str, Any]], geschosse: int = 1) -> QuantityResult:
        """Extrahiere Massen aus CAD-Geometrie."""
        result = QuantityResult()

        for g in geometrie:
            typ = g.get("typ", "")
            props = g.get("properties", {})
            coords = g.get("coordinates", [])

            if typ == "LINE":
                result.umfang_gesamt += props.get("length", 0)
            elif typ == "CIRCLE":
                result.flaeche_gesamt += props.get("area", 0)
            elif typ == "POLYLINE":
                if props.get("closed", False):
                    # Geschlossene Polyline = Fläche
                    flaeche = self._polygon_area(coords)
                    result.flaeche_gesamt += flaeche
                else:
                    # Offene Polyline = Umfang
                    result.umfang_gesamt += self._polyline_length(coords)
            elif typ == "TEXT":
                text = props.get("text", "").lower()
                if "m2" in text or "qm" in text:
                    # Versuche Flächenangabe zu extrahieren
                    pass

        # Gesamtvolumen berechnen
        result.volumen_gesamt = result.flaeche_gesamt * self.hoehe_geschoss * geschosse

        # Material-Mengen schätzen
        result.material_mengen = self._estimate_materials(result)

        return result

    def _polygon_area(self, coords: List[Tuple[float, float, float]]) -> float:
        """Berechne Fläche eines Polygons (Shoelace-Formel)."""
        if len(coords) < 3:
            return 0.0

        n = len(coords)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += coords[i][0] * coords[j][1]
            area -= coords[j][0] * coords[i][1]
        return abs(area) / 2.0

    def _polyline_length(self, coords: List[Tuple[float, float, float]]) -> float:
        """Berechne Länge einer Polyline."""
        length = 0.0
        for i in range(len(coords) - 1):
            p1, p2 = coords[i], coords[i + 1]
            length += math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2)
        return length

    def _estimate_materials(self, result: QuantityResult) -> Dict[str, float]:
        """Schätze Material-Mengen."""
        # Annahmen für Baustoffe
        beton_m3 = result.volumen_gesamt * 0.15  # 15% des Volumens
        stahl_kg = beton_m3 * 100  # 100 kg/m3 Beton
        ziegel_m2 = result.flaeche_gesamt * 0.8  # 80% der Fläche
        daemmung_m2 = result.flaeche_gesamt * 0.3  # 30% der Fläche
        glas_m2 = result.flaeche_gesamt * 0.1  # 10% der Fläche

        return {
            "beton_m3": round(beton_m3, 2),
            "stahl_kg": round(stahl_kg, 2),
            "ziegel_m2": round(ziegel_m2, 2),
            "daemmung_m2": round(daemmung_m2, 2),
            "glas_m2": round(glas_m2, 2),
            "putz_m2": round(result.flaeche_gesamt * 1.5, 2),  # Innen + Außen
            "boden_m2": round(result.flaeche_gesamt, 2),
        }

    def to_dict(self, result: QuantityResult) -> Dict[str, Any]:
        """Konvertiere Ergebnis zu Dictionary."""
        return {
            "flaeche_gesamt_m2": round(result.flaeche_gesamt, 2),
            "umfang_gesamt_m": round(result.umfang_gesamt, 2),
            "volumen_gesamt_m3": round(result.volumen_gesamt, 2),
            "material_mengen": result.material_mengen
        }


if __name__ == "__main__":
    extractor = QuantityExtractor()
    print("Quantity Extractor bereit.")

    # Test mit Beispiel-Geometrie
    test_geometrie = [
        {"typ": "POLYLINE", "coordinates": [(0, 0, 0), (10, 0, 0), (10, 15, 0), (0, 15, 0)], "properties": {"closed": True}},
        {"typ": "LINE", "coordinates": [(0, 0, 0), (10, 0, 0)], "properties": {"length": 10}},
    ]
    result = extractor.extract(test_geometrie, geschosse=4)
    print(f"Fläche: {result.flaeche_gesamt}m2")
    print(f"Volumen: {result.volumen_gesamt}m3")
    print(f"Material: {result.material_mengen}")