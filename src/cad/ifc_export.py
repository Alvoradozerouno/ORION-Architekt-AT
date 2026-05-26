"""
IFC EXPORT - IFC-Dateien erstellen und exportieren
===================================================

Verwendet IfcOpenShell für IFC-Export (BIM-Standard).
Erstellt IFC-Modelle aus CAD-Daten und Plantypen.

Autor: Baumeister Tool Austria Team
Datum: 2026-05-26
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

try:
    import ifcopenshell
    import ifcopenshell.api
    HAS_IFCOPENSHELL = True
except ImportError:
    HAS_IFCOPENSHELL = False


@dataclass
class IFCBuilding:
    """Ein Gebäude für IFC-Export."""
    name: str
    description: str = ""
    storeys: List[Dict[str, Any]] = field(default_factory=list)
    area: float = 0.0
    height: float = 0.0


@dataclass
class IFCExportResult:
    """Ergebnis des IFC-Exports."""
    datei: str
    erfolgreich: bool
    fehler: str = ""
    elemente: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class IFCExporter:
    """Exporter für IFC-Dateien (BIM)."""

    def __init__(self):
        self.model = None

    def create_model(self, building: IFCBuilding) -> IFCExportResult:
        """Erstelle ein IFC-Modell aus einem Gebäude."""
        if not HAS_IFCOPENSHELL:
            return IFCExportResult(
                datei="",
                erfolgreich=False,
                fehler="IfcOpenShell nicht installiert. pip install ifcopenshell"
            )

        try:
            # IFC4 Template erstellen
            self.model = ifcopenshell.file(schema="IFC4")

            # Projekt erstellen
            project = self.model.create_entity("IfcProject")
            project.Name = building.name
            project.Description = building.description

            # Einheit hinzufügen
            unit = self.model.create_entity("IfcSIUnit", UnitType="LENGTHUNIT", Prefix=None, Name="METRE")
            self.model.create_entity("IfcUnitAssignment", Units=[unit])

            # Gebäude erstellen
            ifc_building = self.model.create_entity("IfcBuilding")
            ifc_building.Name = building.name
            ifc_building.Description = building.description

            # Geschosse erstellen
            for storey in building.storeys:
                ifc_storey = self.model.create_entity("IfcBuildingStorey")
                ifc_storey.Name = storey.get("name", "Geschoss")
                ifc_storey.Elevation = storey.get("elevation", 0.0)

            return IFCExportResult(
                datei="",
                erfolgreich=True,
                elemente=len(self.model.by_type("IfcBuildingStorey")) + 2,
                metadata={
                    "schema": "IFC4",
                    "building": building.name,
                    "storeys": len(building.storeys),
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            return IFCExportResult(
                datei="",
                erfolgreich=False,
                fehler=str(e)
            )

    def export(self, building: IFCBuilding, output_pfad: str) -> IFCExportResult:
        """Exportiere IFC-Modell in eine Datei."""
        result = self.create_model(building)
        if result.erfolgreich and self.model:
            try:
                self.model.write(output_pfad)
                result.datei = output_pfad
                result.metadata["output_file"] = output_pfad
                result.metadata["file_size"] = os.path.getsize(output_pfad)
            except Exception as e:
                result.erfolgreich = False
                result.fehler = str(e)
        return result

    def to_json(self, result: IFCExportResult) -> str:
        """Konvertiere Ergebnis zu JSON."""
        return json.dumps({
            "datei": result.datei,
            "erfolgreich": result.erfolgreich,
            "fehler": result.fehler,
            "elemente": result.elemente,
            "metadata": result.metadata
        }, indent=2, ensure_ascii=False)

    @staticmethod
    def create_sample_building(name: str = "Mustergebäude", area: float = 150, storeys: int = 4) -> IFCBuilding:
        """Erstelle ein Beispiel-Gebäude."""
        building = IFCBuilding(
            name=name,
            description=f"Gebäude mit {storeys} Geschossen, {area}m2 pro Geschoss",
            area=area,
            height=storeys * 3.0
        )

        # Standard-Geschosse
        geschoss_namen = ["Untergeschoss", "Erdgeschoss", "Obergeschoss 1", "Obergeschoss 2", "Dachgeschoss"]
        for i in range(storeys):
            building.storeys.append({
                "name": geschoss_namen[i] if i < len(geschoss_namen) else f"Geschoss {i}",
                "elevation": i * 3.0,
                "area": area
            })

        return building


if __name__ == "__main__":
    exporter = IFCExporter()
    print("IFC-Exporter bereit.")
    print(f"IfcOpenShell verfügbar: {HAS_IFCOPENSHELL}")
    if not HAS_IFCOPENSHELL:
        print("Installation: pip install ifcopenshell")
    else:
        # Test-Export
        building = IFCExporter.create_sample_building("Testhaus", 150, 4)
        result = exporter.export(building, "test.ifc")
        print(f"Export: {result.erfolgreich}")
        print(f"Elemente: {result.elemente}")
        print(exporter.to_json(result))