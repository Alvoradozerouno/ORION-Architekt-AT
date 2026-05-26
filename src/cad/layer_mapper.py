"""
LAYER MAPPER - CAD-Layer auf ÖNORM-Bauteilkategorien mappen
=============================================================

Mappt CAD-Layer-Namen auf standardisierte ÖNORM-Kategorien.
Ermöglicht automatische Bauteil-Erkennung aus CAD-Plänen.

Autor: Baumeister Tool Austria Team
Datum: 2026-05-26
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


# ÖNORM-Kategorien Mapping
OENORM_MAPPING = {
    # Tragende Bauteile
    "wand_tragend": ["wand_tragend", "tragende_wand", "loadbearing_wall", "wand", "wall_trag"],
    "decke_tragend": ["decke_tragend", "tragende_decke", "loadbearing_slab", "decke", "slab_trag"],
    "stuetze": ["stuetze", "stütze", "column", "stütze_tragend", "stuetze_tragend"],
    "fundament": ["fundament", "foundation", "fundament_tragend", "bodenplatte"],

    # Nicht-tragende Bauteile
    "wand_nicht_tragend": ["wand_nt", "nicht_tragend", "non_loadbearing", "trennwand", "partition"],
    "decke_nicht_tragend": ["decke_nt", "nicht_tragend_decke", "abhangende_decke"],

    # Öffnungen
    "tuer": ["tuer", "tür", "door", "tuer_oeffnung", "door_opening"],
    "fenster": ["fenster", "window", "fenster_oeffnung", "window_opening"],
    "tor": ["tor", "gate", "tor_oeffnung"],

    # Installationen
    "heizung": ["heizung", "heating", "hzg", "heizung_rohr"],
    "lueftung": ["lueftung", "lüftung", "ventilation", "luft", "lueftungsrohr"],
    "wasser": ["wasser", "water", "sanitaer", "sanitär", "wasser_rohr"],
    "elektro": ["elektro", "electric", "strom", "kabel", "elektro_leitung"],

    # Außenbereiche
    "aussen_wand": ["aussen_wand", "außen_wand", "exterior_wall", "fassade"],
    "dach": ["dach", "roof", "dach_tragend", "dachhaut"],
    "boden": ["boden", "floor", "bodenbelag", "estrich"],

    # Besondere Bereiche
    "treppe": ["treppe", "stair", "staircase", "treppenlauf"],
    "balkon": ["balkon", "balcony", "balkon_tragend"],
    "garage": ["garage", "carport", "tiefgarage"],
}


@dataclass
class MappedLayer:
    """Ein gemappter Layer mit ÖNORM-Kategorie."""
    original_name: str
    oenorm_category: str
    confidence: float  # 0.0 - 1.0
    bauteil_typ: str
    ist_tragend: bool = False


@dataclass
class LayerMappingResult:
    """Ergebnis der Layer-Zuordnung."""
    layer_gesamt: int = 0
    zugeordnet: int = 0
    nicht_zugeordnet: int = 0
    gemappte_layer: List[MappedLayer] = field(default_factory=list)
    kategorien_uebersicht: Dict[str, int] = field(default_factory=dict)


class LayerMapper:
    """Mapper für CAD-Layer auf ÖNORM-Kategorien."""

    def __init__(self):
        self.mapping = OENORM_MAPPING

    def map_layers(self, layer_namen: List[str]) -> LayerMappingResult:
        """Mappe CAD-Layer auf ÖNORM-Kategorien."""
        result = LayerMappingResult()
        result.layer_gesamt = len(layer_namen)

        for name in layer_namen:
            mapped = self._map_single(name)
            result.gemappte_layer.append(mapped)

            if mapped.confidence > 0.5:
                result.zugeordnet += 1
                kat = mapped.oenorm_category
                result.kategorien_uebersicht[kat] = result.kategorien_uebersicht.get(kat, 0) + 1
            else:
                result.nicht_zugeordnet += 1

        return result

    def _map_single(self, name: str) -> MappedLayer:
        """Mappe einen einzelnen Layer-Namen."""
        name_lower = name.lower().strip()

        best_match = MappedLayer(
            original_name=name,
            oenorm_category="unbekannt",
            confidence=0.0,
            bauteil_typ="unbekannt",
            ist_tragend=False
        )

        for category, keywords in self.mapping.items():
            for keyword in keywords:
                if keyword in name_lower:
                    confidence = len(keyword) / max(len(name_lower), 1)
                    if confidence > best_match.confidence:
                        ist_tragend = "tragend" in category or category in ["stuetze", "fundament", "dach"]
                        best_match = MappedLayer(
                            original_name=name,
                            oenorm_category=category,
                            confidence=min(confidence, 1.0),
                            bauteil_typ=self._get_bauteil_typ(category),
                            ist_tragend=ist_tragend
                        )

        return best_match

    def _get_bauteil_typ(self, category: str) -> str:
        """Bestimme den Bauteil-Typ aus der Kategorie."""
        typen = {
            "wand_tragend": "Wand (tragend)",
            "decke_tragend": "Decke (tragend)",
            "stuetze": "Stütze",
            "fundament": "Fundament",
            "wand_nicht_tragend": "Wand (nicht tragend)",
            "decke_nicht_tragend": "Decke (nicht tragend)",
            "tuer": "Tür",
            "fenster": "Fenster",
            "tor": "Tor",
            "heizung": "Heizung",
            "lueftung": "Lüftung",
            "wasser": "Wasser/Sanitär",
            "elektro": "Elektro",
            "aussen_wand": "Außenwand",
            "dach": "Dach",
            "boden": "Boden",
            "treppe": "Treppe",
            "balkon": "Balkon",
            "garage": "Garage",
        }
        return typen.get(category, "Unbekannt")

    def to_dict(self, result: LayerMappingResult) -> Dict[str, Any]:
        """Konvertiere Ergebnis zu Dictionary."""
        return {
            "layer_gesamt": result.layer_gesamt,
            "zugeordnet": result.zugeordnet,
            "nicht_zugeordnet": result.nicht_zugeordnet,
            "kategorien": result.kategorien_uebersicht,
            "gemappte_layer": [
                {
                    "original": l.original_name,
                    "category": l.oenorm_category,
                    "confidence": round(l.confidence, 2),
                    "bauteil": l.bauteil_typ,
                    "tragend": l.ist_tragend
                }
                for l in result.gemappte_layer
            ]
        }


if __name__ == "__main__":
    mapper = LayerMapper()
    print("Layer Mapper bereit.")

    # Test mit Beispiel-Layern
    test_layer = [
        "Wand_tragend_OG1",
        "Decke_NT_EG",
        "Fenster_Nord",
        "Heizung_Rohr",
        "Unbekannter_Layer",
        "Stuetze_S1",
    ]
    result = mapper.map_layers(test_layer)
    print(f"Layer: {result.layer_gesamt}")
    print(f"Zugeordnet: {result.zugeordnet}")
    print(f"Kategorien: {result.kategorien_uebersicht}")