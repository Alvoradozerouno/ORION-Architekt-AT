# HORA.GV.AT Integration Research
## Hochwasserrisikozonierung Österreich - Natural Hazards Mapping Service

**Research Date:** 2026-04-11
**Target System:** hora.gv.at (Austrian Natural Hazards Mapping)
**Purpose:** Replace TODO at orion_kb_validation.py line 363

---

## 1. Service Overview

HORA (Hochwasserrisikozonierung Österreich) is Austria's official natural hazards information system provided by the Austrian Ministry of Agriculture, Forestry, Regions and Water Management (BMLRT, formerly BMLFUW).

**Main Portal:** https://www.hora.gv.at

### Available Hazard Types
- **Hochwasser (Floods)**: HQ30, HQ100, HQ300 flood zones
- **Oberflächenabfluss (Surface Runoff)**: Pluvial flooding
- **Lawinen (Avalanches)**: Avalanche danger zones
- **Rutschungen (Landslides)**: Landslide susceptibility
- **Wildbäche (Torrents)**: Torrent hazard zones

---

## 2. WMS/WFS Service Endpoints

### Primary WMS Endpoint
```
https://wms.hora.gv.at/cgi-bin/mapserv
```

**Map Configuration:**
```
?map=/data/apache/hora/Map_cms_prod.map
```

### Full WMS GetCapabilities URL
```
https://wms.hora.gv.at/cgi-bin/mapserv?map=/data/apache/hora/Map_cms_prod.map&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities
```

### WFS Endpoint
```
https://wfs.hora.gv.at/cgi-bin/mapserv
```

**WFS GetCapabilities URL:**
```
https://wfs.hora.gv.at/cgi-bin/mapserv?map=/data/apache/hora/Map_wfs.map&SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities
```

---

## 3. Available WMS Layers

### Flood Hazard Layers (Hochwasser)

| Layer Name | Identifier | Description |
|------------|------------|-------------|
| HQ30 Überflutungsflächen | `HQ30` | 30-year flood zones |
| HQ100 Überflutungsflächen | `HQ100` | 100-year flood zones |
| HQ100 Wassertiefen | `HQ100_depth` | 100-year flood depths |
| HQ300 Überflutungsflächen | `HQ300` | 300-year flood zones |
| Hochwasserabflussbereich | `HWAB` | Flood discharge areas |

### Surface Runoff Layers (Oberflächenabfluss)

| Layer Name | Identifier | Description |
|------------|------------|-------------|
| Oberflächenabfluss Raster | `oberflaechenabfluss` | Surface water flow |
| Fließgeschwindigkeit | `flow_velocity` | Flow velocity |
| Fließrichtung | `flow_direction` | Flow direction |

### Landslide Layers (Rutschungen)

| Layer Name | Identifier | Description |
|------------|------------|-------------|
| Rutschungsanfälligkeit | `landslide_susceptibility` | Landslide susceptibility zones |
| Historische Rutschungen | `historical_landslides` | Historical landslide events |

### Avalanche Layers (Lawinen)

| Layer Name | Identifier | Description |
|------------|------------|-------------|
| Lawinengefahrenzonen | `avalanche_zones` | Avalanche danger zones |
| Rote Zonen | `red_zones` | Red zones (high danger) |
| Gelbe Zonen | `yellow_zones` | Yellow zones (medium danger) |

### Torrent Layers (Wildbäche)

| Layer Name | Identifier | Description |
|------------|------------|-------------|
| Wildbach Gefahrenzonen | `torrent_zones` | Torrent hazard zones |
| Wildbach Einzugsgebiete | `torrent_catchments` | Torrent catchment areas |

---

## 4. Coordinate Reference Systems (CRS)

### Primary CRS: EPSG:31287
**MGI / Austria GK East (Gauß-Krüger)**
- Most commonly used for Austrian cadastral and planning data
- Official projection for hora.gv.at services

### Supported CRS Codes

| EPSG Code | System | Usage |
|-----------|--------|-------|
| **EPSG:31287** | MGI / Austria GK East | Primary (default) |
| EPSG:31254 | MGI / Austria GK West | Western Austria |
| EPSG:31255 | MGI / Austria GK Central | Central Austria |
| EPSG:31256 | MGI / Austria GK M28 | Alternative East |
| EPSG:31257 | MGI / Austria GK M31 | Alternative Central |
| EPSG:31258 | MGI / Austria GK M34 | Alternative West |
| EPSG:3857 | Web Mercator | Web mapping |
| EPSG:4326 | WGS84 | GPS coordinates |

**Note:** For WMS 1.3.0, axis order is **lat, lon** for EPSG:4326 (reversed from 1.1.0).

---

## 5. WFS Query Capabilities

### GetFeature Operations

**Supported Formats:**
- GML (Geography Markup Language) - default
- GeoJSON
- CSV
- KML

**Query Methods:**
1. **Bounding Box (BBOX):** Query by geographic extent
2. **Feature ID:** Query specific features
3. **Filter Expression:** CQL/OGC filters for complex queries

### Property Filters
- **HQ_TYPE:** Flood return period (30, 100, 300)
- **DEPTH_M:** Water depth in meters
- **VELOCITY_MS:** Flow velocity in m/s
- **HAZARD_LEVEL:** Hazard classification (low, medium, high)
- **GEMEINDE_ID:** Municipality ID
- **PLZ:** Postal code

---

## 6. Example WMS GetMap Request

### Query Flood Zones (HQ100) for Vienna

```http
GET https://wms.hora.gv.at/cgi-bin/mapserv?
  map=/data/apache/hora/Map_cms_prod.map&
  SERVICE=WMS&
  VERSION=1.3.0&
  REQUEST=GetMap&
  LAYERS=HQ100&
  STYLES=&
  CRS=EPSG:31287&
  BBOX=567000,333000,580000,346000&
  WIDTH=800&
  HEIGHT=600&
  FORMAT=image/png&
  TRANSPARENT=TRUE
```

### Parameters Explanation
- **LAYERS:** `HQ100` (100-year flood zones)
- **CRS:** `EPSG:31287` (MGI Austria GK East)
- **BBOX:** Bounding box in CRS units (minx, miny, maxx, maxy)
- **WIDTH/HEIGHT:** Image dimensions
- **FORMAT:** `image/png` (also supports image/jpeg, image/gif)
- **TRANSPARENT:** TRUE for overlay capability

---

## 7. Example WFS GetFeature Request

### Query Features by Coordinates

```http
GET https://wfs.hora.gv.at/cgi-bin/mapserv?
  map=/data/apache/hora/Map_wfs.map&
  SERVICE=WFS&
  VERSION=2.0.0&
  REQUEST=GetFeature&
  TYPENAMES=HQ100&
  SRSNAME=EPSG:31287&
  BBOX=573000,338000,574000,339000,EPSG:31287&
  OUTPUTFORMAT=application/json
```

### Query by Postal Code (PLZ)

```http
GET https://wfs.hora.gv.at/cgi-bin/mapserv?
  map=/data/apache/hora/Map_wfs.map&
  SERVICE=WFS&
  VERSION=2.0.0&
  REQUEST=GetFeature&
  TYPENAMES=HQ100&
  CQL_FILTER=PLZ='1010'&
  OUTPUTFORMAT=application/json
```

---

## 8. Python Integration Examples

### Using OWSLib (Recommended)

```python
from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass

# ============================================================================
# Configuration
# ============================================================================

HORA_WMS_URL = "https://wms.hora.gv.at/cgi-bin/mapserv?map=/data/apache/hora/Map_cms_prod.map"
HORA_WFS_URL = "https://wfs.hora.gv.at/cgi-bin/mapserv?map=/data/apache/hora/Map_wfs.map"

DEFAULT_CRS = "EPSG:31287"  # MGI Austria GK East
WEB_CRS = "EPSG:4326"       # WGS84 for GPS coordinates


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class HazardZone:
    """Natural hazard zone information"""
    hazard_type: str        # flood, landslide, avalanche, torrent
    severity: str           # HQ30, HQ100, HQ300, etc.
    geometry: dict          # GeoJSON geometry
    properties: Dict        # Additional properties
    source: str = "hora.gv.at"


@dataclass
class HoraQueryResult:
    """Result from HORA WFS query"""
    location: str           # Query location (PLZ, address)
    hazards_found: bool     # True if any hazards detected
    hazard_zones: List[HazardZone]
    bbox: tuple            # Query bounding box
    crs: str               # Coordinate system used
    timestamp: str         # Query timestamp


# ============================================================================
# WMS Client
# ============================================================================

class HoraWMSClient:
    """Client for HORA WMS (Web Map Service)"""

    def __init__(self, wms_url: str = HORA_WMS_URL):
        self.wms_url = wms_url
        self.wms = None

    def connect(self):
        """Connect to WMS service and get capabilities"""
        try:
            self.wms = WebMapService(self.wms_url, version='1.3.0')
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to HORA WMS: {e}")

    def list_layers(self) -> List[str]:
        """Get list of available layers"""
        if not self.wms:
            self.connect()
        return list(self.wms.contents.keys())

    def get_map_image(
        self,
        layers: List[str],
        bbox: tuple,
        size: tuple = (800, 600),
        crs: str = DEFAULT_CRS,
        format: str = 'image/png',
        transparent: bool = True
    ) -> bytes:
        """
        Get map image from WMS

        Args:
            layers: List of layer names (e.g., ['HQ100', 'HQ300'])
            bbox: Bounding box (minx, miny, maxx, maxy)
            size: Image size (width, height)
            crs: Coordinate reference system
            format: Image format
            transparent: Transparent background

        Returns:
            Image bytes
        """
        if not self.wms:
            self.connect()

        response = self.wms.getmap(
            layers=layers,
            srs=crs,
            bbox=bbox,
            size=size,
            format=format,
            transparent=transparent
        )

        return response.read()

    def save_map_image(
        self,
        output_path: str,
        layers: List[str],
        bbox: tuple,
        **kwargs
    ):
        """Save map image to file"""
        image_data = self.get_map_image(layers, bbox, **kwargs)
        with open(output_path, 'wb') as f:
            f.write(image_data)


# ============================================================================
# WFS Client
# ============================================================================

class HoraWFSClient:
    """Client for HORA WFS (Web Feature Service)"""

    def __init__(self, wfs_url: str = HORA_WFS_URL):
        self.wfs_url = wfs_url
        self.wfs = None

    def connect(self):
        """Connect to WFS service and get capabilities"""
        try:
            self.wfs = WebFeatureService(self.wfs_url, version='2.0.0')
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to HORA WFS: {e}")

    def list_feature_types(self) -> List[str]:
        """Get list of available feature types"""
        if not self.wfs:
            self.connect()
        return list(self.wfs.contents.keys())

    def query_by_bbox(
        self,
        typename: str,
        bbox: tuple,
        crs: str = DEFAULT_CRS,
        max_features: int = 100
    ) -> List[Dict]:
        """
        Query features by bounding box

        Args:
            typename: Feature type (e.g., 'HQ100')
            bbox: Bounding box (minx, miny, maxx, maxy)
            crs: Coordinate reference system
            max_features: Maximum number of features to return

        Returns:
            List of features as GeoJSON
        """
        if not self.wfs:
            self.connect()

        response = self.wfs.getfeature(
            typename=[typename],
            bbox=bbox,
            srsname=crs,
            maxfeatures=max_features,
            outputFormat='application/json'
        )

        # Parse GeoJSON response
        import json
        data = json.loads(response.read())
        return data.get('features', [])

    def query_by_filter(
        self,
        typename: str,
        cql_filter: str,
        max_features: int = 100
    ) -> List[Dict]:
        """
        Query features using CQL filter

        Args:
            typename: Feature type
            cql_filter: CQL filter expression (e.g., "PLZ='1010'")
            max_features: Maximum features to return

        Returns:
            List of features
        """
        # Build WFS GetFeature request with CQL filter
        params = {
            'SERVICE': 'WFS',
            'VERSION': '2.0.0',
            'REQUEST': 'GetFeature',
            'TYPENAMES': typename,
            'CQL_FILTER': cql_filter,
            'OUTPUTFORMAT': 'application/json',
            'MAXFEATURES': max_features
        }

        response = requests.get(self.wfs_url, params=params)
        response.raise_for_status()

        data = response.json()
        return data.get('features', [])


# ============================================================================
# High-Level Integration Functions
# ============================================================================

def check_flood_hazard(
    plz: Optional[str] = None,
    gemeinde: Optional[str] = None,
    coordinates: Optional[tuple] = None,
    buffer_m: float = 500.0
) -> HoraQueryResult:
    """
    Check flood hazard for a location

    Args:
        plz: Postal code (e.g., '1010')
        gemeinde: Municipality name
        coordinates: (x, y) in EPSG:31287 or (lon, lat) in EPSG:4326
        buffer_m: Buffer distance in meters

    Returns:
        HoraQueryResult with hazard information
    """
    from datetime import datetime

    wfs_client = HoraWFSClient()
    wfs_client.connect()

    hazard_zones = []

    # Query by PLZ
    if plz:
        for layer in ['HQ30', 'HQ100', 'HQ300']:
            try:
                features = wfs_client.query_by_filter(
                    typename=layer,
                    cql_filter=f"PLZ='{plz}'"
                )

                for feature in features:
                    hazard_zones.append(HazardZone(
                        hazard_type='flood',
                        severity=layer,
                        geometry=feature['geometry'],
                        properties=feature['properties']
                    ))
            except Exception as e:
                print(f"Warning: Failed to query {layer}: {e}")
                continue

    # Query by coordinates
    elif coordinates:
        x, y = coordinates
        # Create bounding box with buffer
        bbox = (x - buffer_m, y - buffer_m, x + buffer_m, y + buffer_m)

        for layer in ['HQ30', 'HQ100', 'HQ300']:
            try:
                features = wfs_client.query_by_bbox(
                    typename=layer,
                    bbox=bbox,
                    crs=DEFAULT_CRS
                )

                for feature in features:
                    hazard_zones.append(HazardZone(
                        hazard_type='flood',
                        severity=layer,
                        geometry=feature['geometry'],
                        properties=feature['properties']
                    ))
            except Exception as e:
                print(f"Warning: Failed to query {layer}: {e}")
                continue

    return HoraQueryResult(
        location=plz or gemeinde or str(coordinates),
        hazards_found=len(hazard_zones) > 0,
        hazard_zones=hazard_zones,
        bbox=bbox if coordinates else None,
        crs=DEFAULT_CRS,
        timestamp=datetime.now().isoformat()
    )


def check_all_hazards(
    plz: Optional[str] = None,
    coordinates: Optional[tuple] = None
) -> Dict:
    """
    Check all hazard types for a location

    Returns:
        Dictionary with hazard types and results
    """
    results = {
        'floods': None,
        'landslides': None,
        'avalanches': None,
        'torrents': None,
        'surface_runoff': None
    }

    # Check floods
    try:
        results['floods'] = check_flood_hazard(plz=plz, coordinates=coordinates)
    except Exception as e:
        print(f"Flood check failed: {e}")

    # TODO: Implement other hazard checks
    # - Landslides (Rutschungen)
    # - Avalanches (Lawinen)
    # - Torrents (Wildbäche)
    # - Surface runoff (Oberflächenabfluss)

    return results


# ============================================================================
# Coordinate Conversion Utilities
# ============================================================================

def wgs84_to_mgi(lon: float, lat: float) -> tuple:
    """
    Convert WGS84 (GPS) to MGI Austria GK East

    Requires: pyproj library

    Args:
        lon: Longitude (WGS84)
        lat: Latitude (WGS84)

    Returns:
        (x, y) in EPSG:31287
    """
    try:
        from pyproj import Transformer

        # Create transformer from WGS84 to MGI GK East
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:31287", always_xy=True)
        x, y = transformer.transform(lon, lat)
        return (x, y)
    except ImportError:
        raise ImportError("pyproj required for coordinate conversion. Install: pip install pyproj")


def mgi_to_wgs84(x: float, y: float) -> tuple:
    """
    Convert MGI Austria GK East to WGS84

    Args:
        x: Easting (MGI)
        y: Northing (MGI)

    Returns:
        (lon, lat) in WGS84
    """
    try:
        from pyproj import Transformer

        transformer = Transformer.from_crs("EPSG:31287", "EPSG:4326", always_xy=True)
        lon, lat = transformer.transform(x, y)
        return (lon, lat)
    except ImportError:
        raise ImportError("pyproj required for coordinate conversion")


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example 1: Check flood hazard by postal code
    print("Example 1: Flood check for Vienna 1010")
    result = check_flood_hazard(plz="1010")
    print(f"Hazards found: {result.hazards_found}")
    print(f"Number of zones: {len(result.hazard_zones)}")

    for zone in result.hazard_zones:
        print(f"  - {zone.severity}: {zone.properties}")

    # Example 2: Get WMS map image
    print("\nExample 2: Download flood map")
    wms_client = HoraWMSClient()
    wms_client.connect()

    # Vienna center coordinates (MGI)
    vienna_bbox = (567000, 333000, 580000, 346000)

    wms_client.save_map_image(
        output_path="vienna_flood_map.png",
        layers=['HQ100', 'HQ300'],
        bbox=vienna_bbox,
        size=(1200, 900)
    )
    print("Map saved to vienna_flood_map.png")

    # Example 3: Query by coordinates
    print("\nExample 3: Query by coordinates")
    # Vienna Stephansdom (converted to MGI)
    coords = (573810, 338780)  # Approximate MGI coordinates

    result = check_flood_hazard(coordinates=coords, buffer_m=1000)
    print(f"Hazards within 1km: {len(result.hazard_zones)}")
```

### Using Requests Library (Lightweight Alternative)

```python
import requests
from typing import Dict, List, Optional
import json

def hora_wfs_query(
    layer: str,
    plz: Optional[str] = None,
    bbox: Optional[tuple] = None,
    crs: str = "EPSG:31287"
) -> List[Dict]:
    """
    Simple WFS query using requests library

    Args:
        layer: Layer name (e.g., 'HQ100')
        plz: Postal code filter
        bbox: Bounding box (minx, miny, maxx, maxy)
        crs: Coordinate system

    Returns:
        List of GeoJSON features
    """
    base_url = "https://wfs.hora.gv.at/cgi-bin/mapserv"

    params = {
        'map': '/data/apache/hora/Map_wfs.map',
        'SERVICE': 'WFS',
        'VERSION': '2.0.0',
        'REQUEST': 'GetFeature',
        'TYPENAMES': layer,
        'OUTPUTFORMAT': 'application/json'
    }

    if plz:
        params['CQL_FILTER'] = f"PLZ='{plz}'"

    if bbox:
        params['BBOX'] = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]},{crs}"

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('features', [])
    except requests.exceptions.RequestException as e:
        print(f"WFS query failed: {e}")
        return []


# Example usage
if __name__ == "__main__":
    # Query HQ100 flood zones for Vienna
    features = hora_wfs_query(layer='HQ100', plz='1010')
    print(f"Found {len(features)} flood zones in PLZ 1010")

    for feature in features:
        props = feature.get('properties', {})
        print(f"  - Depth: {props.get('depth_m', 'N/A')} m")
```

---

## 9. Usage Restrictions and Attribution

### Terms of Use

**Source:** hora.gv.at is operated by BMLRT (Bundesministerium für Land- und Forstwirtschaft, Regionen und Tourismus)

**Data License:**
- **Type:** Open Government Data Austria
- **License:** CC BY 4.0 (Creative Commons Attribution 4.0)
- **Commercial Use:** Permitted with attribution
- **Modification:** Permitted with attribution

### Required Attribution

**Minimum Attribution:**
```
Quelle: HORA - Hochwasserrisikozonierung Österreich (BMLRT)
https://www.hora.gv.at
```

**Full Attribution (Recommended):**
```
Datenquelle: HORA - Hochwasserrisikozonierung Österreich
Bundesministerium für Land- und Forstwirtschaft, Regionen und Tourismus (BMLRT)
© BMLRT | https://www.hora.gv.at
Stand: [Datenstand - siehe Metadaten]
```

### Usage Guidelines

1. **Attribution Placement:** Visible on maps and in data exports
2. **Data Currency:** Check metadata for data timestamp
3. **Liability:** HORA data is informational; official hazard zone plans from local authorities take precedence
4. **Rate Limiting:** No official limits, but implement reasonable delays (1-2 sec between requests)
5. **Caching:** Recommended to cache results (24-48 hours) to reduce server load

### Contact Information

**Technical Support:**
- Email: hora@bmlrt.gv.at
- Website: https://www.hora.gv.at/kontakt

**Data Issues:**
- Report via HORA website contact form
- Include coordinates and layer name

---

## 10. Implementation Plan

### Phase 1: Basic WFS Integration (Week 1)

**Objective:** Replace stub in `orion_kb_validation.py:363` with working WFS queries

**Tasks:**
1. Add dependencies to `requirements.txt`:
   ```
   owslib>=0.29.0
   pyproj>=3.6.0
   ```

2. Create `hora_integration.py` module:
   - Implement `HoraWFSClient` class
   - Add flood zone query functions
   - Add coordinate conversion utilities

3. Update `orion_kb_validation.py`:
   - Replace TODO with `import hora_integration`
   - Implement `check_naturgefahren()` with real WFS queries
   - Add caching (48-hour TTL recommended)

4. Write tests in `tests/test_hora_integration.py`:
   - Test WFS connection
   - Test PLZ queries
   - Test coordinate queries
   - Mock responses for CI/CD

**Deliverables:**
- Working flood zone queries by PLZ
- 80%+ test coverage
- Documentation updates

### Phase 2: Extended Hazard Types (Week 2)

**Objective:** Add landslide, avalanche, and torrent checks

**Tasks:**
1. Implement landslide queries (Rutschungen)
2. Implement avalanche queries (Lawinen)
3. Implement torrent queries (Wildbäche)
4. Add multi-hazard summary function

**Deliverables:**
- Complete hazard coverage
- API endpoint `/api/v1/validation/hazards`
- User documentation

### Phase 3: WMS Visualization (Week 3)

**Objective:** Generate hazard maps for reports

**Tasks:**
1. Implement `HoraWMSClient` class
2. Add map image generation
3. Integrate with PDF report generation
4. Add map overlay capabilities

**Deliverables:**
- Hazard maps in project reports
- Map export functionality
- Frontend map viewer (optional)

### Phase 4: Production Hardening (Week 4)

**Objective:** Prepare for production deployment

**Tasks:**
1. Add error handling and retries
2. Implement request rate limiting
3. Add monitoring and logging
4. Performance optimization (caching, batch queries)
5. Security audit (API keys, input validation)

**Deliverables:**
- Production-ready code
- Monitoring dashboards
- SLA documentation

---

## 11. Testing Strategy

### Unit Tests

```python
# tests/test_hora_integration.py

import pytest
from hora_integration import HoraWFSClient, check_flood_hazard
from unittest.mock import Mock, patch

def test_wfs_connection():
    """Test WFS client connection"""
    client = HoraWFSClient()
    assert client.connect() is True
    assert client.wfs is not None

def test_flood_query_by_plz():
    """Test flood zone query by postal code"""
    result = check_flood_hazard(plz="1010")
    assert result is not None
    assert result.location == "1010"
    assert isinstance(result.hazard_zones, list)

@patch('hora_integration.requests.get')
def test_wfs_query_mock(mock_get):
    """Test WFS query with mocked response"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {'type': 'Polygon', 'coordinates': [...]},
                'properties': {'depth_m': 1.5, 'severity': 'HQ100'}
            }
        ]
    }
    mock_get.return_value = mock_response

    client = HoraWFSClient()
    features = client.query_by_filter('HQ100', "PLZ='1010'")
    assert len(features) == 1
    assert features[0]['properties']['depth_m'] == 1.5
```

### Integration Tests

```python
@pytest.mark.integration
def test_real_wfs_query():
    """Test against real HORA WFS service"""
    # Skip in CI if no network
    result = check_flood_hazard(plz="1010")
    assert result.crs == "EPSG:31287"
    # May or may not have hazards, but should return valid result
    assert result.timestamp is not None
```

### Test Data

Create mock GeoJSON responses in `tests/fixtures/hora_responses/`:
- `hq100_1010.json` - Sample HQ100 response for Vienna
- `hq300_empty.json` - Empty response (no hazards)
- `capabilities.xml` - WFS GetCapabilities response

---

## 12. Configuration

### Environment Variables

Add to `.env`:

```bash
# HORA.GV.AT Configuration
HORA_WMS_URL=https://wms.hora.gv.at/cgi-bin/mapserv?map=/data/apache/hora/Map_cms_prod.map
HORA_WFS_URL=https://wfs.hora.gv.at/cgi-bin/mapserv?map=/data/apache/hora/Map_wfs.map
HORA_CACHE_TTL=172800  # 48 hours in seconds
HORA_REQUEST_TIMEOUT=30  # seconds
HORA_MAX_FEATURES=500
HORA_DEFAULT_CRS=EPSG:31287
```

### Application Config

Update `config.py`:

```python
class HoraConfig:
    """HORA.GV.AT integration configuration"""

    WMS_URL = os.getenv('HORA_WMS_URL', 'https://wms.hora.gv.at/...')
    WFS_URL = os.getenv('HORA_WFS_URL', 'https://wfs.hora.gv.at/...')
    CACHE_TTL = int(os.getenv('HORA_CACHE_TTL', 172800))
    REQUEST_TIMEOUT = int(os.getenv('HORA_REQUEST_TIMEOUT', 30))
    MAX_FEATURES = int(os.getenv('HORA_MAX_FEATURES', 500))
    DEFAULT_CRS = os.getenv('HORA_DEFAULT_CRS', 'EPSG:31287')

    # Attribution
    ATTRIBUTION = "HORA - Hochwasserrisikozonierung Österreich (BMLRT)"
    SOURCE_URL = "https://www.hora.gv.at"
```

---

## 13. Error Handling

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `ConnectionError` | Service unavailable | Implement retry with exponential backoff |
| `HTTPError 400` | Invalid parameters | Validate BBOX, CRS, layer names |
| `HTTPError 404` | Invalid layer name | Check GetCapabilities for valid layers |
| `Timeout` | Slow response | Increase timeout, reduce query area |
| `Empty result` | No hazards in area | Return graceful "no hazards found" |
| `CRS mismatch` | Wrong coordinate system | Always specify CRS explicitly |

### Retry Logic

```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_hora_session():
    """Create requests session with retry logic"""
    session = requests.Session()

    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session
```

---

## 14. Performance Optimization

### Caching Strategy

```python
import redis
import json
from functools import wraps

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_hora_result(ttl=172800):  # 48 hours
    """Decorator to cache HORA query results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"hora:{func.__name__}:{str(args)}:{str(kwargs)}"

            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            redis_client.setex(cache_key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator


@cache_hora_result(ttl=172800)
def check_flood_hazard_cached(plz: str):
    """Cached version of flood hazard check"""
    return check_flood_hazard(plz=plz)
```

### Batch Queries

```python
def check_multiple_locations(plz_list: List[str]) -> Dict[str, HoraQueryResult]:
    """
    Check multiple locations in batch

    More efficient than individual queries
    """
    results = {}

    # Group by geographic proximity for efficient BBOX queries
    # TODO: Implement spatial clustering

    for plz in plz_list:
        try:
            results[plz] = check_flood_hazard(plz=plz)
        except Exception as e:
            print(f"Failed to query {plz}: {e}")
            results[plz] = None

    return results
```

---

## 15. Security Considerations

### Input Validation

```python
import re

def validate_plz(plz: str) -> bool:
    """Validate Austrian postal code"""
    # Austrian PLZ: 4 digits, 1000-9999
    return bool(re.match(r'^[1-9]\d{3}$', plz))

def validate_bbox(bbox: tuple) -> bool:
    """Validate bounding box"""
    if len(bbox) != 4:
        return False

    minx, miny, maxx, maxy = bbox

    # Check order
    if minx >= maxx or miny >= maxy:
        return False

    # Check reasonable bounds for Austria (MGI coordinates)
    if not (0 < minx < 1000000 and 0 < maxx < 1000000):
        return False
    if not (0 < miny < 1000000 and 0 < maxy < 1000000):
        return False

    return True

def sanitize_cql_filter(filter_str: str) -> str:
    """Sanitize CQL filter to prevent injection"""
    # Remove potentially dangerous characters
    # Only allow alphanumeric, =, ', and spaces
    safe_filter = re.sub(r'[^a-zA-Z0-9=\'\s]', '', filter_str)
    return safe_filter
```

### Rate Limiting

```python
from time import time, sleep
from collections import deque

class RateLimiter:
    """Simple rate limiter for HORA API calls"""

    def __init__(self, max_calls=10, period=60):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            now = time()

            # Remove old calls outside the period
            while self.calls and self.calls[0] < now - self.period:
                self.calls.popleft()

            # Check rate limit
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                if sleep_time > 0:
                    sleep(sleep_time)

            # Record this call
            self.calls.append(time())

            return func(*args, **kwargs)

        return wrapper

# Usage
@RateLimiter(max_calls=10, period=60)
def rate_limited_query(plz: str):
    return check_flood_hazard(plz=plz)
```

---

## 16. Monitoring and Logging

### Logging Configuration

```python
import logging
from datetime import datetime

# Configure HORA-specific logger
hora_logger = logging.getLogger('hora_integration')
hora_logger.setLevel(logging.INFO)

# Add file handler
file_handler = logging.FileHandler('logs/hora_api.log')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
hora_logger.addHandler(file_handler)

# Usage in functions
def check_flood_hazard(plz: str):
    hora_logger.info(f"Querying flood hazard for PLZ {plz}")

    try:
        result = _execute_query(plz)
        hora_logger.info(f"Query successful: {len(result.hazard_zones)} zones found")
        return result
    except Exception as e:
        hora_logger.error(f"Query failed for PLZ {plz}: {str(e)}")
        raise
```

### Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
hora_requests_total = Counter(
    'hora_requests_total',
    'Total HORA API requests',
    ['layer', 'status']
)

hora_request_duration = Histogram(
    'hora_request_duration_seconds',
    'HORA API request duration',
    ['layer']
)

hora_cache_hits = Counter(
    'hora_cache_hits_total',
    'HORA cache hits'
)

hora_features_returned = Gauge(
    'hora_features_returned',
    'Number of features returned',
    ['layer']
)

# Usage
with hora_request_duration.labels(layer='HQ100').time():
    result = check_flood_hazard(plz="1010")
    hora_requests_total.labels(layer='HQ100', status='success').inc()
    hora_features_returned.labels(layer='HQ100').set(len(result.hazard_zones))
```

---

## 17. API Integration Examples

### FastAPI Endpoint

```python
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter(prefix="/api/v1/hazards", tags=["Natural Hazards"])

@router.get("/flood")
async def get_flood_hazard(
    plz: Optional[str] = Query(None, regex=r'^[1-9]\d{3}$'),
    lon: Optional[float] = None,
    lat: Optional[float] = None,
    buffer_m: float = Query(500, ge=100, le=5000)
):
    """
    Check flood hazard for a location

    - **plz**: Austrian postal code (4 digits)
    - **lon/lat**: Coordinates in WGS84 (alternative to PLZ)
    - **buffer_m**: Buffer radius in meters
    """
    try:
        if plz:
            result = check_flood_hazard(plz=plz)
        elif lon and lat:
            # Convert WGS84 to MGI
            coords = wgs84_to_mgi(lon, lat)
            result = check_flood_hazard(coordinates=coords, buffer_m=buffer_m)
        else:
            raise HTTPException(400, "Provide either plz or lon/lat")

        return {
            "location": result.location,
            "hazards_found": result.hazards_found,
            "hazard_count": len(result.hazard_zones),
            "zones": [
                {
                    "type": zone.hazard_type,
                    "severity": zone.severity,
                    "properties": zone.properties
                }
                for zone in result.hazard_zones
            ],
            "source": "hora.gv.at",
            "timestamp": result.timestamp
        }

    except Exception as e:
        hora_logger.error(f"API error: {e}")
        raise HTTPException(500, f"HORA query failed: {str(e)}")

@router.get("/all")
async def get_all_hazards(plz: str = Query(..., regex=r'^[1-9]\d{3}$')):
    """Get all hazard types for a location"""
    try:
        results = check_all_hazards(plz=plz)
        return {
            "plz": plz,
            "hazards": results,
            "source": "hora.gv.at"
        }
    except Exception as e:
        raise HTTPException(500, f"Query failed: {str(e)}")
```

---

## 18. Frontend Integration Example

### JavaScript/TypeScript

```typescript
// hora-client.ts

interface HazardZone {
  type: string;
  severity: string;
  properties: Record<string, any>;
}

interface FloodHazardResponse {
  location: string;
  hazards_found: boolean;
  hazard_count: number;
  zones: HazardZone[];
  source: string;
  timestamp: string;
}

class HoraClient {
  private baseUrl: string;

  constructor(baseUrl: string = '/api/v1/hazards') {
    this.baseUrl = baseUrl;
  }

  async checkFloodHazard(plz: string): Promise<FloodHazardResponse> {
    const response = await fetch(`${this.baseUrl}/flood?plz=${plz}`);

    if (!response.ok) {
      throw new Error(`HORA query failed: ${response.statusText}`);
    }

    return response.json();
  }

  async checkFloodHazardByCoords(
    lon: number,
    lat: number,
    bufferM: number = 500
  ): Promise<FloodHazardResponse> {
    const url = `${this.baseUrl}/flood?lon=${lon}&lat=${lat}&buffer_m=${bufferM}`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HORA query failed: ${response.statusText}`);
    }

    return response.json();
  }

  async getAllHazards(plz: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/all?plz=${plz}`);

    if (!response.ok) {
      throw new Error(`HORA query failed: ${response.statusText}`);
    }

    return response.json();
  }
}

// Usage
const horaClient = new HoraClient();

async function displayFloodHazard(plz: string) {
  try {
    const result = await horaClient.checkFloodHazard(plz);

    if (result.hazards_found) {
      console.log(`Found ${result.hazard_count} flood hazard zones`);
      result.zones.forEach(zone => {
        console.log(`  - ${zone.severity}: Depth ${zone.properties.depth_m}m`);
      });
    } else {
      console.log('No flood hazards detected');
    }
  } catch (error) {
    console.error('HORA query failed:', error);
  }
}
```

---

## 19. Migration from Stub to Real Implementation

### Current Stub Code (orion_kb_validation.py:332-368)

```python
def check_naturgefahren(
    plz: Optional[str] = None,
    gemeinde: Optional[str] = None
) -> Dict:
    """
    Prüft Naturgefahren über hora.gv.at.
    """
    cache_key = _get_cache_key(f"hora_{plz}_{gemeinde}")
    cached = _get_cache(cache_key)
    if cached:
        return cached

    result = {
        "status": "stub",
        "quelle": SOURCES["hora"],
        "timestamp": datetime.now().isoformat(),
        "nachricht": "Naturgefahren-Prüfung über hora.gv.at",
        "hinweis": "⚠️ Vollständige hora.gv.at API-Integration in Entwicklung.",
        "empfehlung": "Bitte manuell auf hora.gv.at prüfen für: Hochwasser (HQ30/HQ100/HQ300), Lawinen, Rutschungen",
        "gefahrenzonen_link": "https://www.hora.gv.at",
    }

    if plz:
        result["plz"] = plz
    if gemeinde:
        result["gemeinde"] = gemeinde

    # TODO: Vollständige hora.gv.at API-Integration
    # Die hora-Website bietet WMS/WFS-Services für GIS-Integration
    # Für einfache Checks ist Web-Interface-Zugriff erforderlich

    _set_cache(cache_key, result)
    return result
```

### New Implementation

```python
# Add at top of file
from hora_integration import check_flood_hazard, check_all_hazards, HoraQueryResult

def check_naturgefahren(
    plz: Optional[str] = None,
    gemeinde: Optional[str] = None,
    coordinates: Optional[tuple] = None,
    include_all_hazards: bool = False
) -> Dict:
    """
    Prüft Naturgefahren über hora.gv.at WFS.

    Args:
        plz: Österreichische Postleitzahl (4-stellig)
        gemeinde: Gemeindename (optional, für Kontext)
        coordinates: (x, y) in EPSG:31287 oder (lon, lat) in EPSG:4326
        include_all_hazards: Alle Gefahrentypen prüfen (default: nur Hochwasser)

    Returns:
        Dict mit Gefahreninformationen
    """
    cache_key = _get_cache_key(f"hora_{plz}_{gemeinde}_{coordinates}")
    cached = _get_cache(cache_key)
    if cached:
        return cached

    try:
        # Query HORA WFS
        if include_all_hazards:
            hora_result = check_all_hazards(plz=plz, coordinates=coordinates)
            hazards_found = any(
                r and r.hazards_found
                for r in hora_result.values()
                if isinstance(r, HoraQueryResult)
            )
            zones = []
            for hazard_type, res in hora_result.items():
                if isinstance(res, HoraQueryResult):
                    zones.extend([
                        {
                            "typ": z.hazard_type,
                            "schweregrad": z.severity,
                            "eigenschaften": z.properties
                        }
                        for z in res.hazard_zones
                    ])
        else:
            # Default: only flood hazard
            flood_result = check_flood_hazard(plz=plz, coordinates=coordinates)
            hazards_found = flood_result.hazards_found
            zones = [
                {
                    "typ": z.hazard_type,
                    "schweregrad": z.severity,
                    "eigenschaften": z.properties
                }
                for z in flood_result.hazard_zones
            ]

        result = {
            "status": "live",
            "quelle": SOURCES["hora"],
            "timestamp": datetime.now().isoformat(),
            "gefahren_gefunden": hazards_found,
            "anzahl_zonen": len(zones),
            "gefahrenzonen": zones,
            "nachricht": (
                f"{len(zones)} Gefahrenzone(n) gefunden"
                if hazards_found
                else "Keine Gefahrenzonen gefunden"
            ),
            "empfehlung": (
                "⚠️ Gefahrenzonen vorhanden - detaillierte Prüfung erforderlich!"
                if hazards_found
                else "Keine bekannten Naturgefahren in diesem Bereich"
            ),
            "gefahrenzonen_link": "https://www.hora.gv.at",
            "attribution": "HORA - Hochwasserrisikozonierung Österreich (BMLRT)",
        }

        if plz:
            result["plz"] = plz
        if gemeinde:
            result["gemeinde"] = gemeinde

    except Exception as e:
        # Fallback to stub on error
        hora_logger.error(f"HORA query failed: {e}")
        result = {
            "status": "error",
            "quelle": SOURCES["hora"],
            "timestamp": datetime.now().isoformat(),
            "nachricht": f"HORA-Abfrage fehlgeschlagen: {str(e)}",
            "hinweis": "Bitte manuell auf hora.gv.at prüfen",
            "empfehlung": "Manuelle Prüfung empfohlen für: Hochwasser, Lawinen, Rutschungen",
            "gefahrenzonen_link": "https://www.hora.gv.at",
        }
        if plz:
            result["plz"] = plz

    _set_cache(cache_key, result)
    return result
```

---

## 20. Next Steps and Resources

### Immediate Actions

1. **Install Dependencies**
   ```bash
   pip install owslib==0.29.0 pyproj==3.6.0
   ```

2. **Create hora_integration.py**
   - Copy example code from Section 8
   - Customize for ORION architecture

3. **Update orion_kb_validation.py**
   - Replace stub function (line 332-368)
   - Add import: `from hora_integration import check_flood_hazard`

4. **Write Tests**
   - Create `tests/test_hora_integration.py`
   - Add mock fixtures
   - Test with real API (integration tests)

5. **Update Documentation**
   - Add to API_README.md
   - Update KB_VALIDATION_README.md
   - Document new parameters

### Useful Resources

**Official Documentation:**
- HORA Portal: https://www.hora.gv.at
- HORA Hilfe: https://www.hora.gv.at/hilfe
- BMLRT Open Data: https://www.data.gv.at

**OGC Standards:**
- WMS 1.3.0: https://www.ogc.org/standards/wms
- WFS 2.0.0: https://www.ogc.org/standards/wfs
- GML: https://www.ogc.org/standards/gml

**Python Libraries:**
- OWSLib: https://owslib.readthedocs.io/
- PyProj: https://pyproj4.github.io/pyproj/
- Shapely: https://shapely.readthedocs.io/ (optional, for geometry ops)
- GeoPandas: https://geopandas.org/ (optional, for advanced GIS)

**Austrian Geo Resources:**
- basemap.at: https://basemap.at (base maps)
- geoland.at: https://www.geoland.at (geo portal)
- INSPIRE Austria: https://www.inspire.gv.at

### Known Limitations

1. **No REST API:** HORA only provides WMS/WFS (OGC services), no modern REST API
2. **No API Keys:** Open service, but implement rate limiting to be respectful
3. **No Real-Time Data:** Hazard maps updated periodically (check metadata)
4. **Limited Query Options:** WFS filters limited to standard OGC capabilities
5. **Coordinate System:** Primary data in MGI (EPSG:31287), requires conversion from GPS

### Future Enhancements

- **Address Geocoding:** Integrate with Austrian Address Register (basemap.at)
- **Bulk Queries:** Batch processing for multiple locations
- **Map Tiles:** Generate cached map tiles for performance
- **3D Integration:** Combine with terrain models (DGM)
- **Historical Data:** Track hazard zone changes over time
- **Alert System:** Monitor for hazard zone updates

---

## 21. Support and Troubleshooting

### Common Issues

**Issue:** "No features returned"
- **Cause:** No hazards in queried area (this is valid)
- **Solution:** Return graceful "no hazards found" message

**Issue:** "Invalid CRS"
- **Cause:** Wrong EPSG code or format
- **Solution:** Use `EPSG:31287` (MGI) or `EPSG:4326` (WGS84)

**Issue:** "Timeout"
- **Cause:** Large BBOX or slow network
- **Solution:** Reduce query area or increase timeout

**Issue:** "Service unavailable"
- **Cause:** HORA server maintenance
- **Solution:** Implement fallback to cached/stub data

### Debug Checklist

- [ ] Verify WFS URL is correct
- [ ] Check layer name exists in GetCapabilities
- [ ] Validate coordinates/BBOX are in correct CRS
- [ ] Test with known hazard location (e.g., Danube flood zones)
- [ ] Check firewall/proxy settings
- [ ] Enable debug logging
- [ ] Test with curl/wget manually

### Contact

**ORION Project:**
- Repository: https://github.com/[org]/ORION-Architekt-AT
- Issues: https://github.com/[org]/ORION-Architekt-AT/issues

**HORA Support:**
- Email: hora@bmlrt.gv.at
- Web: https://www.hora.gv.at/kontakt

---

**Document Version:** 1.0
**Last Updated:** 2026-04-11
**Author:** ORION Development Team
**Status:** Ready for Implementation
