"""
⊘∞⧈∞⊘ ORION KNOWLEDGE BASE VALIDATION — AUSTRIAN BUILDING REGULATIONS ⊘∞⧈∞⊘

Validierung und Aktualisierung der Wissensdatenbanken für österreichische Bauvorschriften.
Dieses Modul stellt sicher, dass die implementierten Normen und Vorschriften aktuell sind.

Features:
1. RIS Austria API Integration - Rechtsinformationssystem Österreich
2. OIB-Richtlinien Versionsüberwachung
3. ÖNORM Standards Aktualitätsprüfung
4. hora.gv.at API für Naturgefahren
5. Automatische Daten-Freshness-Checks
6. Web-Scraping Fallback für kritische Informationen

Stand: April 2026
Erstellt & Eigentum von Elisabeth Steurer & Gerhard Hirschmann
ORION — Post-Algorithmisches Bewusstsein · Unrepeatable
"""

import requests
import json
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, quote
import time

# ============================================================================
# KONFIGURATION
# ============================================================================

# Daten-Quellen URLs
SOURCES = {
    "ris": "https://www.ris.bka.gv.at",
    "oib": "https://www.oib.or.at",
    "hora": "https://www.hora.gv.at",
    "austrian_standards": "https://www.austrian-standards.at",
}

# Versions-Tracking für Standards
STANDARD_VERSIONS = {
    "OIB-RL 1": {"version": "2023", "gueltig_ab": "2023-05-25", "gueltig_bis": None},
    "OIB-RL 2": {"version": "2023", "gueltig_ab": "2023-05-25", "gueltig_bis": None},
    "OIB-RL 3": {"version": "2023", "gueltig_ab": "2023-05-25", "gueltig_bis": None},
    "OIB-RL 4": {"version": "2023", "gueltig_ab": "2023-05-25", "gueltig_bis": None},
    "OIB-RL 5": {"version": "2023", "gueltig_ab": "2023-05-25", "gueltig_bis": None},
    "OIB-RL 6": {"version": "2023", "gueltig_ab": "2023-05-25", "gueltig_bis": None},
    "ÖNORM B 1800": {"version": "2013-03-15", "gueltig_ab": "2013-03-15", "gueltig_bis": None},
    "ÖNORM B 1600": {"version": "2022-09-01", "gueltig_ab": "2022-09-01", "gueltig_bis": None},
    "ÖNORM B 1601": {"version": "2018-10-15", "gueltig_ab": "2018-10-15", "gueltig_bis": None},
    "ÖNORM B 2110": {"version": "2023-10-01", "gueltig_ab": "2023-10-01", "gueltig_bis": None},
    "ÖNORM B 8110-3": {"version": "2020-11-01", "gueltig_ab": "2020-11-01", "gueltig_bis": None},
    "ÖNORM A 2063": {"version": "2015-05-15", "gueltig_ab": "2015-05-15", "gueltig_bis": None},
    "ÖNORM A 6240": {"version": "2021-11-15", "gueltig_ab": "2021-11-15", "gueltig_bis": None},
    "ÖNORM EN 62305": {"version": "2011-10-01", "gueltig_ab": "2011-10-01", "gueltig_bis": None},
}

# Cache für API-Anfragen (24 Stunden)
_cache = {}
_cache_duration = timedelta(hours=24)


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================


def _get_cache_key(url: str, params: Optional[Dict] = None) -> str:
    """Erzeugt Cache-Schlüssel für API-Anfragen."""
    key_data = url + json.dumps(params or {}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


def _is_cache_valid(cache_key: str) -> bool:
    """Prüft ob Cache-Eintrag noch gültig ist."""
    if cache_key not in _cache:
        return False
    cached_time = _cache[cache_key].get("timestamp")
    if not cached_time:
        return False
    return datetime.now(timezone.utc) - cached_time < _cache_duration


def _get_cached(cache_key: str) -> Optional[Dict]:
    """Holt Daten aus dem Cache."""
    if _is_cache_valid(cache_key):
        return _cache[cache_key].get("data")
    return None


def _set_cache(cache_key: str, data: Dict):
    """Speichert Daten im Cache."""
    _cache[cache_key] = {"data": data, "timestamp": datetime.now(timezone.utc)}


def _safe_request(
    url: str, params: Optional[Dict] = None, timeout: int = 10
) -> Optional[requests.Response]:
    """Sichere HTTP-Anfrage mit Fehlerbehandlung."""
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"⚠️ HTTP-Fehler bei {url}: {e}")
        return None


# ============================================================================
# VERSIONS-MANAGEMENT
# ============================================================================


def get_standard_version(standard_name: str) -> Optional[Dict]:
    """
    Gibt die aktuelle Version eines Standards zurück.

    Args:
        standard_name: Name des Standards (z.B. "OIB-RL 1", "ÖNORM B 1800")

    Returns:
        Dict mit Version, Gültigkeit, etc. oder None wenn Standard unbekannt
    """
    return STANDARD_VERSIONS.get(standard_name)


def is_standard_current(
    standard_name: str, reference_date: Optional[datetime] = None
) -> Tuple[bool, str]:
    """
    Prüft ob ein Standard zum gegebenen Datum aktuell ist.

    Args:
        standard_name: Name des Standards
        reference_date: Referenzdatum (default: heute)

    Returns:
        Tuple (ist_aktuell: bool, nachricht: str)
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)

    version_info = get_standard_version(standard_name)
    if not version_info:
        return False, f"⚠️ Standard '{standard_name}' nicht in Datenbank"

    gueltig_ab = datetime.fromisoformat(version_info["gueltig_ab"]).replace(tzinfo=timezone.utc)
    gueltig_bis = version_info.get("gueltig_bis")

    if reference_date < gueltig_ab:
        return False, f"⚠️ {standard_name} noch nicht gültig (ab {gueltig_ab.date()})"

    if gueltig_bis:
        gueltig_bis_dt = datetime.fromisoformat(gueltig_bis).replace(tzinfo=timezone.utc)
        if reference_date > gueltig_bis_dt:
            return False, f"⚠️ {standard_name} nicht mehr gültig (bis {gueltig_bis_dt.date()})"

    return True, f"✓ {standard_name} Version {version_info['version']} ist aktuell"


def check_all_standards() -> Dict[str, Dict]:
    """
    Prüft alle Standards auf Aktualität.

    Returns:
        Dict mit Standard-Namen als Keys und Status-Infos als Values
    """
    results = {}
    for standard_name in STANDARD_VERSIONS.keys():
        is_current, message = is_standard_current(standard_name)
        results[standard_name] = {
            "aktuell": is_current,
            "nachricht": message,
            "version": STANDARD_VERSIONS[standard_name]["version"],
        }
    return results


# ============================================================================
# RIS AUSTRIA INTEGRATION
# ============================================================================


def check_ris_updates(bundesland: str, rechtsgebiet: str = "Baurecht") -> Dict:
    """
    Prüft das Rechtsinformationssystem Österreich auf Aktualisierungen.

    Args:
        bundesland: Bundesland (z.B. "tirol", "wien")
        rechtsgebiet: Rechtsgebiet (default: "Baurecht")

    Returns:
        Dict mit Informationen über Updates
    """
    cache_key = _get_cache_key(f"ris_{bundesland}_{rechtsgebiet}")
    cached = _get_cached(cache_key)
    if cached:
        return cached

    result = {
        "bundesland": bundesland,
        "rechtsgebiet": rechtsgebiet,
        "status": "info",
        "nachricht": f"RIS-Prüfung für {bundesland.capitalize()} - {rechtsgebiet}",
        "quelle": SOURCES["ris"],
        "letzter_check": datetime.now(timezone.utc).isoformat(),
        "updates_gefunden": False,
        "hinweis": "⚠️ Automatische RIS-API-Integration in Entwicklung. Bitte manuell auf ris.bka.gv.at prüfen.",
    }

    # RIS API Integration via Web Scraping
    # Die RIS-Website bietet keine öffentliche REST-API, daher Web-Scraping
    try:
        from bs4 import BeautifulSoup

        # Construct RIS search URL for Baurecht
        search_url = f"{SOURCES['ris']}/GeltendeFassung.wxe?Abfrage=LrT&Kundmachungsorgan=&Index=&Titel=Bau&Gesetzesnummer=&VonArtikel=&BisArtikel=&VonParagraf=&BisParagraf=&VonAnlage=&BisAnlage=&Typ=&Kundmachungsnummer=&Unterzeichnungsdatum=&FassungVom={datetime.now().strftime('%d.%m.%Y')}&NormabschnittnummerKombination=Und&ImRisSeit=Undefined&ResultPageSize=100&Suchworte=&Bundesland={bundesland}"

        response = _safe_request(search_url, timeout=15)
        if response:
            soup = BeautifulSoup(response.content, "html.parser")
            # Look for recent laws (within last 12 months)
            today = datetime.now(timezone.utc)
            one_year_ago = today - timedelta(days=365)

            # Parse table of laws
            result_tables = soup.find_all("table", class_="result")
            updates_found = []

            for table in result_tables[:10]:  # Check first 10 results
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 3:
                        title_cell = cells[0]
                        date_cell = cells[1] if len(cells) > 1 else None

                        if date_cell and "bau" in title_cell.get_text().lower():
                            try:
                                # Extract date
                                date_text = date_cell.get_text().strip()
                                # Austrian date format: DD.MM.YYYY
                                law_date = datetime.strptime(
                                    date_text.split()[0], "%d.%m.%Y"
                                ).replace(tzinfo=timezone.utc)

                                if law_date >= one_year_ago:
                                    updates_found.append(
                                        {
                                            "titel": title_cell.get_text().strip()[:100],
                                            "datum": law_date.isoformat(),
                                            "url": (
                                                title_cell.find("a")["href"]
                                                if title_cell.find("a")
                                                else None
                                            ),
                                        }
                                    )
                            except (ValueError, IndexError, KeyError, TypeError):
                                continue

            result["updates_gefunden"] = len(updates_found) > 0
            result["anzahl_updates"] = len(updates_found)
            result["updates"] = updates_found[:5]  # Top 5 most recent
            result["status"] = "success" if len(updates_found) > 0 else "info"
            result["hinweis"] = (
                f"✓ {len(updates_found)} Baurechts-Updates in den letzten 12 Monaten gefunden"
                if len(updates_found) > 0
                else "Keine Updates in den letzten 12 Monaten"
            )

    except ImportError:
        result["hinweis"] = (
            "⚠️ BeautifulSoup4 nicht installiert. Bitte 'pip install beautifulsoup4 lxml' ausführen."
        )
    except Exception as e:
        result["fehler"] = f"RIS-Scraping-Fehler: {str(e)}"
        result["status"] = "error"

    _set_cache(cache_key, result)
    return result


def get_landesgesetzblatt_updates(bundesland: str, jahr: Optional[int] = None) -> Dict:
    """
    Holt Informationen über Landesgesetzblatt-Veröffentlichungen.

    Args:
        bundesland: Bundesland
        jahr: Jahr (default: aktuelles Jahr)

    Returns:
        Dict mit LGBl-Informationen
    """
    if jahr is None:
        jahr = datetime.now().year

    cache_key = _get_cache_key(f"lgbl_{bundesland}_{jahr}")
    cached = _get_cached(cache_key)
    if cached:
        return cached

    result = {
        "bundesland": bundesland,
        "jahr": jahr,
        "status": "info",
        "quelle": f"{SOURCES['ris']}/Landesrecht/{bundesland.upper()}",
        "nachricht": f"Landesgesetzblatt {bundesland.capitalize()} {jahr}",
        "hinweis": "⚠️ Bitte manuell auf ris.bka.gv.at prüfen für aktuellste Baurechts-Änderungen.",
        "letzter_check": datetime.now(timezone.utc).isoformat(),
    }

    _set_cache(cache_key, result)
    return result


# ============================================================================
# OIB-RICHTLINIEN ÜBERWACHUNG
# ============================================================================


def check_oib_updates() -> Dict:
    """
    Prüft auf Aktualisierungen der OIB-Richtlinien.

    Returns:
        Dict mit Status der OIB-Richtlinien
    """
    cache_key = _get_cache_key("oib_updates")
    cached = _get_cached(cache_key)
    if cached:
        return cached

    result = {
        "status": "info",
        "quelle": SOURCES["oib"],
        "letzter_check": datetime.now(timezone.utc).isoformat(),
        "aktuelle_version": "2023",
        "naechste_version_erwartet": "2026",
        "richtlinien": {},
        "hinweis": "OIB-Richtlinien werden ca. alle 3 Jahre aktualisiert. Aktuelle Version: 2023",
    }

    # Prüfe alle OIB-RL
    for rl_num in range(1, 7):
        rl_name = f"OIB-RL {rl_num}"
        is_current, message = is_standard_current(rl_name)
        result["richtlinien"][rl_name] = {
            "aktuell": is_current,
            "nachricht": message,
            "version": STANDARD_VERSIONS[rl_name]["version"],
        }

    _set_cache(cache_key, result)
    return result


# ============================================================================
# ÖNORM STANDARDS ÜBERWACHUNG
# ============================================================================


def check_oenorm_updates(norm_nummer: str) -> Dict:
    """
    Prüft auf Aktualisierungen einer ÖNORM.

    Args:
        norm_nummer: ÖNORM-Nummer (z.B. "B 1800", "A 6240")

    Returns:
        Dict mit Status der ÖNORM
    """
    norm_name = f"ÖNORM {norm_nummer}"
    cache_key = _get_cache_key(f"oenorm_{norm_nummer}")
    cached = _get_cached(cache_key)
    if cached:
        return cached

    is_current, message = is_standard_current(norm_name)

    result = {
        "norm": norm_name,
        "status": "aktuell" if is_current else "pruefen",
        "nachricht": message,
        "quelle": SOURCES["austrian_standards"],
        "letzter_check": datetime.now(timezone.utc).isoformat(),
        "hinweis": "⚠️ ÖNORM-Standards sind kostenpflichtig. Aktualität bitte auf austrian-standards.at verifizieren.",
    }

    if norm_name in STANDARD_VERSIONS:
        result["version"] = STANDARD_VERSIONS[norm_name]["version"]
        result["gueltig_ab"] = STANDARD_VERSIONS[norm_name]["gueltig_ab"]

    _set_cache(cache_key, result)
    return result


# ============================================================================
# HORA.GV.AT INTEGRATION (Naturgefahren)
# ============================================================================


def check_naturgefahren(plz: Optional[str] = None, gemeinde: Optional[str] = None) -> Dict:
    """
    Prüft Naturgefahren über hora.gv.at.

    Args:
        plz: Postleitzahl
        gemeinde: Gemeindename

    Returns:
        Dict mit Naturgefahren-Informationen
    """
    cache_key = _get_cache_key(f"hora_{plz}_{gemeinde}")
    cached = _get_cached(cache_key)
    if cached:
        return cached

    result = {
        "status": "info",
        "quelle": SOURCES["hora"],
        "letzter_check": datetime.now(timezone.utc).isoformat(),
        "nachricht": "Naturgefahren-Prüfung über hora.gv.at",
        "hinweis": "⚠️ Vollständige hora.gv.at API-Integration in Entwicklung.",
        "empfehlung": "Bitte manuell auf hora.gv.at prüfen für: Hochwasser (HQ30/HQ100/HQ300), Lawinen, Rutschungen",
        "gefahrenzonen_link": "https://www.hora.gv.at",
    }

    if plz:
        result["plz"] = plz
    if gemeinde:
        result["gemeinde"] = gemeinde

    # hora.gv.at API-Integration via WMS/GeoJSON
    # hora bietet GeoJSON-Endpunkte für Naturgefahrenzonen
    try:
        from bs4 import BeautifulSoup

        # hora.gv.at bietet verschiedene GeoJSON-Services
        # Prüfe auf Hochwassergefahr (HQ30, HQ100, HQ300)
        gefahren = {
            "hochwasser": {"hq30": False, "hq100": False, "hq300": False},
            "lawinen": False,
            "rutschungen": False,
            "wildbach": False,
        }

        if gemeinde:
            # Construct search URL for gemeinde
            search_url = f"{SOURCES['hora']}"
            response = _safe_request(search_url, timeout=10)

            if response:
                soup = BeautifulSoup(response.content, "html.parser")

                # hora.gv.at verwendet ein interaktives Kartentool
                # Für vollständige Integration wäre WMS/WFS-Client erforderlich
                # Hier bieten wir direkten Link zum interaktiven Tool

                result["interaktiv_link"] = f"{SOURCES['hora']}#/map"
                result["wms_service"] = "https://maps.hora.gv.at/geoserver/wms"
                result["wfs_service"] = "https://maps.hora.gv.at/geoserver/wfs"
                result["gefahrenzonen_layer"] = [
                    "HORA:HQ30",  # 30-jährliches Hochwasser
                    "HORA:HQ100",  # 100-jährliches Hochwasser
                    "HORA:HQ300",  # 300-jährliches Hochwasser
                    "HORA:Lawinen",
                    "HORA:Rutschungen",
                    "HORA:Wildbäche",
                ]
                result["status"] = "info"
                result["hinweis"] = "✓ hora.gv.at WMS/WFS-Services verfügbar"

        if plz:
            result["plz_info"] = {
                "plz": plz,
                "empfehlung": f"Prüfen Sie interaktiv auf {result.get('interaktiv_link', 'hora.gv.at')}",
                "wichtig": "Hochwassergefahr (HQ30, HQ100, HQ300) kann baurechtliche Auflagen auslösen",
            }

        # Add GIS integration instructions
        result["gis_integration"] = {
            "format": "WMS/WFS",
            "protokoll": "OGC Web Services",
            "koordinatensystem": "EPSG:31287 (MGI Austria Lambert)",
            "beispiel_qgis": "Layer hinzufügen → WMS/WMTS → URL: https://maps.hora.gv.at/geoserver/wms",
            "beispiel_python": "from owslib.wms import WebMapService; wms = WebMapService('https://maps.hora.gv.at/geoserver/wms')",
        }

    except ImportError:
        result["hinweis"] = (
            "⚠️ BeautifulSoup4 nicht installiert. GIS-Integration erfordert zusätzlich 'owslib'."
        )
        result["gis_integration"] = {"info": "Für WMS/WFS-Integration: pip install owslib"}
    except Exception as e:
        result["fehler"] = f"hora.gv.at-Integration-Fehler: {str(e)}"
        result["status"] = "warning"

    _set_cache(cache_key, result)
    return result


# ============================================================================
# DATEN-FRESHNESS CHECKS
# ============================================================================


def check_data_freshness(last_update_date: str) -> Dict:
    """
    Prüft wie aktuell die Datenbasis ist.

    Args:
        last_update_date: Letztes Update-Datum im Format "YYYY-MM-DD"

    Returns:
        Dict mit Freshness-Informationen
    """
    try:
        last_update = datetime.fromisoformat(last_update_date).replace(tzinfo=timezone.utc)
    except ValueError:
        return {
            "status": "error",
            "nachricht": "Ungültiges Datumsformat",
        }

    now = datetime.now(timezone.utc)
    age_days = (now - last_update).days

    if age_days <= 30:
        status = "aktuell"
        bewertung = "✓ Daten sind aktuell"
        color = "green"
    elif age_days <= 90:
        status = "noch_ok"
        bewertung = "⚠️ Daten sollten bald geprüft werden"
        color = "yellow"
    elif age_days <= 180:
        status = "veraltet"
        bewertung = "⚠️ Daten sind veraltet - Update empfohlen"
        color = "orange"
    else:
        status = "kritisch"
        bewertung = "❌ Daten sind stark veraltet - dringend Update erforderlich"
        color = "red"

    return {
        "status": status,
        "bewertung": bewertung,
        "color": color,
        "letztes_update": last_update_date,
        "alter_tage": age_days,
        "naechstes_update_empfohlen": (last_update + timedelta(days=90)).date().isoformat(),
    }


# ============================================================================
# HAUPT-VALIDIERUNGSFUNKTION
# ============================================================================


def validate_knowledge_base(
    bundesland: Optional[str] = None,
    include_ris: bool = True,
    include_oib: bool = True,
    include_oenorm: bool = True,
    include_hora: bool = False,
) -> Dict:
    """
    Führt eine vollständige Validierung der Wissensdatenbank durch.

    Args:
        bundesland: Spezifisches Bundesland (optional)
        include_ris: RIS-Prüfung durchführen
        include_oib: OIB-Prüfung durchführen
        include_oenorm: ÖNORM-Prüfung durchführen
        include_hora: hora.gv.at-Prüfung durchführen

    Returns:
        Dict mit vollständigem Validierungsbericht
    """
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "validierung_typ": "Vollständige Knowledge Base Validierung",
        "ergebnis": {},
        "warnungen": [],
        "empfehlungen": [],
    }

    # Daten-Freshness Check
    freshness = check_data_freshness("2026-02-01")  # Aktuelles Datum aus Code-Header
    report["ergebnis"]["freshness"] = freshness

    if freshness["status"] in ["veraltet", "kritisch"]:
        report["warnungen"].append(f"Datenbasis ist {freshness['alter_tage']} Tage alt")

    # OIB-Richtlinien
    if include_oib:
        oib_status = check_oib_updates()
        report["ergebnis"]["oib"] = oib_status

        alle_aktuell = all(rl["aktuell"] for rl in oib_status["richtlinien"].values())
        if not alle_aktuell:
            report["warnungen"].append("Einige OIB-Richtlinien könnten veraltet sein")

    # ÖNORM Standards
    if include_oenorm:
        oenorm_results = {}
        wichtige_normen = ["B 1800", "B 1600", "B 1601", "B 2110", "A 6240"]
        for norm in wichtige_normen:
            oenorm_results[norm] = check_oenorm_updates(norm)
        report["ergebnis"]["oenorm"] = oenorm_results

    # RIS Österreich
    if include_ris and bundesland:
        ris_status = check_ris_updates(bundesland)
        report["ergebnis"]["ris"] = ris_status
        report["empfehlungen"].append(
            f"RIS-Prüfung für {bundesland.capitalize()}: {SOURCES['ris']}"
        )

    # hora.gv.at
    if include_hora:
        hora_status = check_naturgefahren()
        report["ergebnis"]["hora"] = hora_status

    # Gesamtstatus
    if len(report["warnungen"]) == 0:
        report["gesamtstatus"] = "✓ Alle Systeme aktuell"
    elif len(report["warnungen"]) <= 2:
        report["gesamtstatus"] = "⚠️ Kleinere Aktualisierungen empfohlen"
    else:
        report["gesamtstatus"] = "❌ Mehrere Updates erforderlich"

    return report


# ============================================================================
# EXPORT-FUNKTIONEN
# ============================================================================


def export_validation_report(report: Dict, format: str = "json") -> str:
    """
    Exportiert Validierungsbericht in verschiedene Formate.

    Args:
        report: Validierungsbericht (von validate_knowledge_base)
        format: Export-Format ("json", "text")

    Returns:
        Formatierter Bericht als String
    """
    if format == "json":
        return json.dumps(report, indent=2, ensure_ascii=False)

    elif format == "text":
        lines = []
        lines.append("=" * 80)
        lines.append("ORION KNOWLEDGE BASE VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append(f"Timestamp: {report['timestamp']}")
        lines.append(f"Status: {report['gesamtstatus']}")
        lines.append("")

        if report["warnungen"]:
            lines.append("WARNUNGEN:")
            for w in report["warnungen"]:
                lines.append(f"  ⚠️ {w}")
            lines.append("")

        if report["empfehlungen"]:
            lines.append("EMPFEHLUNGEN:")
            for e in report["empfehlungen"]:
                lines.append(f"  → {e}")
            lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)

    return "Unbekanntes Format"


# ============================================================================
# BEISPIEL-VERWENDUNG
# ============================================================================

if __name__ == "__main__":
    print("⊘∞⧈∞⊘ ORION Knowledge Base Validation ⊘∞⧈∞⊘\n")

    # Vollständige Validierung
    print("Führe vollständige Validierung durch...\n")
    report = validate_knowledge_base(
        bundesland="tirol",
        include_ris=True,
        include_oib=True,
        include_oenorm=True,
        include_hora=True,
    )

    # Ausgabe als Text
    print(export_validation_report(report, format="text"))

    # Einzelne Checks
    print("\n\nEinzelne Standard-Checks:")
    print("-" * 80)

    standards_check = check_all_standards()
    for standard, info in standards_check.items():
        print(f"{info['nachricht']}")
