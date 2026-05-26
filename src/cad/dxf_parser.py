"""
DXF PARSER - DXF-Dateien parsen und extrahieren
================================================

Verwendet ezdxf für DXF-Dateien (Open Source Alternative zu DWG).
Extrahiert: Geometrie, Layer, Blöcke, Maße, Texte.

Autor: Baumeister Tool Austria Team
Datum: 2026-05-26
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

try:
    import ezdxf
    from ezdxf.entities import Entity, Line, Circle, Arc, Polyline, Text, MText, Dimension
    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False


@dataclass
class CADLayer:
    """Ein CAD-Layer mit Informationen."""
    name: str
    description: str
    entities_count: int
    color: int = 7
    linetype: str = "CONTINUOUS"


@dataclass
class CADGeometry:
    """Ein extrahiertes Geometrie-Element."""
    typ: str  # LINE, CIRCLE, ARC, POLYLINE, TEXT, DIMENSION
    layer: str
    properties: Dict[str, Any] = field(default_factory=dict)
    coordinates: List[Tuple[float, float, float]] = field(default_factory=list)


@dataclass
class CADResult:
    """Ergebnis des DXF-Parsings."""
    datei: str
    erfolgreich: bool
    fehler: str = ""
    layer: List[CADLayer] = field(default_factory=list)
    geometrie: List[CADGeometry] = field(default_factory=list)
    masse: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DXFParser:
    """Parser für DXF-Dateien."""

    def __init__(self):
        self.doc = None
        self.modelspace = None

    def parse(self, datei_pfad: str) -> CADResult:
        """Parse eine DXF-Datei und extrahiere alle Informationen."""
        if not HAS_EZDXF:
            return CADResult(
                datei=datei_pfad,
                erfolgreich=False,
                fehler="ezdxf nicht installiert. pip install ezdxf"
            )

        if not os.path.exists(datei_pfad):
            return CADResult(
                datei=datei_pfad,
                erfolgreich=False,
                fehler=f"Datei nicht gefunden: {datei_pfad}"
            )

        try:
            self.doc = ezdxf.readfile(datei_pfad)
            self.modelspace = self.doc.modelspace()

            layer = self._extract_layers()
            geometrie = self._extract_geometry()
            masse = self._extract_masse(geometrie)
            metadata = self._extract_metadata(datei_pfad)

            return CADResult(
                datei=datei_pfad,
                erfolgreich=True,
                layer=layer,
                geometrie=geometrie,
                masse=masse,
                metadata=metadata
            )
        except Exception as e:
            return CADResult(
                datei=datei_pfad,
                erfolgreich=False,
                fehler=str(e)
            )

    def _extract_layers(self) -> List[CADLayer]:
        """Extrahiere alle Layer aus der DXF-Datei."""
        layer_list = []
        for layer in self.doc.layers:
            entities = list(self.modelspace.query(f"*[layer=='{layer.dxf.name}']"))
            layer_list.append(CADLayer(
                name=layer.dxf.name,
                description=layer.dxf.description if hasattr(layer.dxf, 'description') else "",
                entities_count=len(entities),
                color=layer.dxf.color if hasattr(layer.dxf, 'color') else 7,
                linetype=layer.dxf.linetype if hasattr(layer.dxf, 'linetype') else "CONTINUOUS"
            ))
        return layer_list

    def _extract_geometry(self) -> List[CADGeometry]:
        """Extrahiere alle Geometrie-Elemente."""
        geometrie = []

        for entity in self.modelspace:
            try:
                if entity.dxftype() == "LINE":
                    geometrie.append(CADGeometry(
                        typ="LINE",
                        layer=entity.dxf.layer,
                        coordinates=[
                            (entity.dxf.start.x, entity.dxf.start.y, entity.dxf.start.z),
                            (entity.dxf.end.x, entity.dxf.end.y, entity.dxf.end.z)
                        ],
                        properties={"length": self._line_length(entity)}
                    ))
                elif entity.dxftype() == "CIRCLE":
                    geometrie.append(CADGeometry(
                        typ="CIRCLE",
                        layer=entity.dxf.layer,
                        coordinates=[(entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z)],
                        properties={"radius": entity.dxf.radius, "area": 3.14159 * entity.dxf.radius ** 2}
                    ))
                elif entity.dxftype() == "ARC":
                    geometrie.append(CADGeometry(
                        typ="ARC",
                        layer=entity.dxf.layer,
                        coordinates=[(entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z)],
                        properties={
                            "radius": entity.dxf.radius,
                            "start_angle": entity.dxf.start_angle,
                            "end_angle": entity.dxf.end_angle
                        }
                    ))
                elif entity.dxftype() == "POLYLINE" or entity.dxftype() == "LWPOLYLINE":
                    points = [(p[0], p[1], p[2] if len(p) > 2 else 0) for p in entity.points()]
                    geometrie.append(CADGeometry(
                        typ="POLYLINE",
                        layer=entity.dxf.layer,
                        coordinates=points,
                        properties={"points_count": len(points), "closed": entity.is_closed}
                    ))
                elif entity.dxftype() in ("TEXT", "MTEXT"):
                    geometrie.append(CADGeometry(
                        typ="TEXT",
                        layer=entity.dxf.layer,
                        coordinates=[(entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z)],
                        properties={"text": entity.plain_text() if hasattr(entity, 'plain_text') else entity.dxf.text}
                    ))
                elif entity.dxftype() == "DIMENSION":
                    geometrie.append(CADGeometry(
                        typ="DIMENSION",
                        layer=entity.dxf.layer,
                        properties={"measurement": entity.measurement if hasattr(entity, 'measurement') else 0}
                    ))
            except Exception:
                continue

        return geometrie

    def _extract_masse(self, geometrie: List[CADGeometry]) -> Dict[str, float]:
        """Extrahiere Masseninformationen."""
        flaeche = 0
        umfang = 0
        for g in geometrie:
            if g.typ == "CIRCLE":
                flaeche += g.properties.get("area", 0)
            elif g.typ == "LINE":
                umfang += g.properties.get("length", 0)
            elif g.typ == "POLYLINE":
                # Einfache Schätzung
                for i in range(len(g.coordinates) - 1):
                    p1, p2 = g.coordinates[i], g.coordinates[i + 1]
                    umfang += ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

        return {
            "flaeche_m2": round(flaeche, 2),
            "umfang_m": round(umfang, 2),
            "elemente_gesamt": len(geometrie)
        }

    def _extract_metadata(self, datei_pfad: str) -> Dict[str, Any]:
        """Extrahiere Metadaten."""
        metadata = {
            "datei": datei_pfad,
            "dateiname": os.path.basename(datei_pfad),
            "groesse_bytes": os.path.getsize(datei_pfad),
            "timestamp": datetime.now().isoformat(),
            "dxf_version": self.doc.dxfversion if hasattr(self.doc, 'dxfversion') else "unknown"
        }
        return metadata

    @staticmethod
    def _line_length(line) -> float:
        """Berechne die Länge einer Linie."""
        dx = line.dxf.end.x - line.dxf.start.x
        dy = line.dxf.end.y - line.dxf.start.y
        dz = line.dxf.end.z - line.dxf.start.z
        return (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5

    def to_json(self, result: CADResult) -> str:
        """Konvertiere Ergebnis zu JSON."""
        return json.dumps({
            "datei": result.datei,
            "erfolgreich": result.erfolgreich,
            "fehler": result.fehler,
            "layer": [{"name": l.name, "entities": l.entities_count, "color": l.color} for l in result.layer],
            "masse": result.masse,
            "metadata": result.metadata,
            "geometrie_count": len(result.geometrie)
        }, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    parser = DXFParser()
    print("DXF-Parser bereit.")
    print(f"ezdxf verfügbar: {HAS_EZDXF}")
    if HAS_EZDXF:
        print("Installation: pip install ezdxf")