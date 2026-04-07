#!/usr/bin/env python3
"""
=============================================================================
EUROCODE 7 (EC7-AT) V1.0 – GEOTECHNIK-BEMESSUNG
=============================================================================
ÖNORM EN 1997-1 (Eurocode 7 Austria) – Flachfundamente

Autoren: Elisabeth Steurer & Gerhard Hirschmann
Datum: 2026-04-07
Ort: Almdorf 9, St. Johann in Tirol, Austria
Lizenz: Apache 2.0

⚠️  WARNUNG: Nur für Vordimensionierung!
    Finale Bemessung durch befugten Ziviltechniker mit Baugrundgutachten!

NORMEN:
- ÖNORM EN 1997-1: Eurocode 7 - Geotechnik
- ÖNORM B 4435: Österreichischer Nationaler Anhang

TRL (Technology Readiness Level): 4 (Laboratory Validation)
ISO 26262 ASIL-D Prinzipien für deterministische Berechnung

SCOPE (MVP):
- Zentrische Flachfundamente unter Vertikallast
- Sohldruckberechnung
- Setzungsabschätzung (vereinfacht)
- Typische österreichische Böden

NICHT SCOPE (Future):
- Exzentrische Belastung
- Pfahlgründungen
- Grundbruchnachweis (komplex)
- Böschungsstatik
=============================================================================
"""

import math
import hashlib
import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime


# =============================================================================
# ÖSTERREICHISCHE BODEN-DATENBANK (Typische Werte)
# =============================================================================

BODEN_KLASSEN_AT = {
    "KIES_DICHT": {
        "bezeichnung": "Kies, dicht gelagert (Tirol typisch)",
        "phi_grad": 35.0,  # Reibungswinkel °
        "c_kpa": 0.0,  # Kohäsion kN/m²
        "gamma_kn_m3": 20.0,  # Wichte kN/m³
        "E_s_mpa": 100.0,  # Steifemodul MPa (für Setzung)
        "sigma_zul_kpa": 400.0,  # Zulässige Sohldruckspannung kN/m²
    },
    "SAND_MITTEL": {
        "bezeichnung": "Sand, mitteldicht",
        "phi_grad": 30.0,
        "c_kpa": 0.0,
        "gamma_kn_m3": 18.0,
        "E_s_mpa": 50.0,
        "sigma_zul_kpa": 200.0,
    },
    "TON_STEIF": {
        "bezeichnung": "Ton, steif (cu = 100 kPa)",
        "phi_grad": 0.0,  # Undräniert
        "c_kpa": 100.0,  # Undränierte Scherfestigkeit
        "gamma_kn_m3": 19.0,
        "E_s_mpa": 20.0,
        "sigma_zul_kpa": 150.0,
    },
    "LEHM_FEST": {
        "bezeichnung": "Lehm, fest",
        "phi_grad": 25.0,
        "c_kpa": 15.0,
        "gamma_kn_m3": 19.0,
        "E_s_mpa": 30.0,
        "sigma_zul_kpa": 250.0,
    },
    "FELS_VERWITTERT": {
        "bezeichnung": "Fels, verwittert (Alpen)",
        "phi_grad": 40.0,
        "c_kpa": 50.0,
        "gamma_kn_m3": 22.0,
        "E_s_mpa": 500.0,
        "sigma_zul_kpa": 1000.0,
    },
}


# =============================================================================
# KONFIGURATION
# =============================================================================


@dataclass
class EC7Config:
    """Konfiguration für EC7 Geotechnik-Bemessung"""

    # Belastung
    N_ED_KN: float = 500.0  # Bemessungs-Normalkraft (vertikal)

    # Boden
    BODENKLASSE: str = "KIES_DICHT"  # Bodenklasse

    # Fundament (Startwerte)
    B_M: float = 2.0  # Breite in m
    L_M: float = 2.0  # Länge in m
    T_M: float = 0.8  # Tiefe unter Gelände in m

    # Beton
    GAMMA_BETON_KN_M3: float = 25.0  # Wichte Stahlbeton

    # Teilsicherheitsbeiwerte (EN 1997-1 Anhang A)
    GAMMA_G: float = 1.35  # Ständige Lasten
    GAMMA_Q: float = 1.5  # Veränderliche Lasten

    # Sonstige
    PROJEKT: str = "Flachfundament - Vorbemessung"

    def __post_init__(self):
        # Bodeneigenschaften laden
        if self.BODENKLASSE not in BODEN_KLASSEN_AT:
            raise ValueError(f"Unbekannte Bodenklasse: {self.BODENKLASSE}")
        boden_data = BODEN_KLASSEN_AT[self.BODENKLASSE]
        self.SIGMA_ZUL_KPA = boden_data["sigma_zul_kpa"]
        self.GAMMA_BODEN_KN_M3 = boden_data["gamma_kn_m3"]
        self.E_S_MPA = boden_data["E_s_mpa"]


# =============================================================================
# ERGEBNISSE
# =============================================================================


@dataclass
class EC7Result:
    """Einzelnes Berechnungsergebnis"""

    b_m: float
    l_m: float
    t_m: float
    A_m2: float
    N_gesamt_kn: float
    sigma_kpa: float
    sigma_zul_kpa: float
    eta_sohldruck: float
    setzung_mm: float
    status: str  # OK, FAIL
    details: str


# =============================================================================
# HAUPTKLASSE: FLACHFUNDAMENT EC7-AT
# =============================================================================


class FlachfundamentEC7AT_V1:
    """
    Flachfundament-Bemessung nach EN 1997-1 (Eurocode 7 Austria)

    Funktionen:
    - Sohldruckberechnung
    - Setzungsabschätzung (vereinfacht)
    - Iterative Optimierung der Fundamentfläche
    """

    def __init__(self, config: EC7Config):
        self.config = config
        self.results: List[EC7Result] = []

    def calculate_total_load(self, b_m: float, l_m: float, t_m: float) -> float:
        """
        Gesamtlast berechnen (Nutzlast + Eigengewicht Fundament + Erdauflast)

        Args:
            b_m: Breite in m
            l_m: Länge in m
            t_m: Tiefe unter Gelände in m

        Returns:
            N_gesamt in kN
        """
        # Nutzlast (von Gebäude)
        N_nutz = self.config.N_ED_KN

        # Eigengewicht Fundament (Annahme: Höhe = 0.5 m)
        h_fundament_m = 0.5
        V_fundament_m3 = b_m * l_m * h_fundament_m
        N_fundament = V_fundament_m3 * self.config.GAMMA_BETON_KN_M3

        # Erdauflast (Tiefe minus Fundamenthöhe)
        h_erde_m = max(t_m - h_fundament_m, 0.0)
        V_erde_m3 = b_m * l_m * h_erde_m
        N_erde = V_erde_m3 * self.config.GAMMA_BODEN_KN_M3

        N_gesamt = N_nutz + N_fundament + N_erde
        return N_gesamt

    def calculate_soil_pressure(
        self, N_gesamt_kn: float, b_m: float, l_m: float
    ) -> float:
        """
        Sohldruckspannung berechnen (EN 1997-1 Section 6.5)

        σ = N / A

        Args:
            N_gesamt_kn: Gesamtlast in kN
            b_m: Breite in m
            l_m: Länge in m

        Returns:
            σ in kPa
        """
        A_m2 = b_m * l_m
        if A_m2 <= 0:
            return 999999.0
        sigma_kpa = N_gesamt_kn / A_m2
        return sigma_kpa

    def calculate_settlement(
        self, sigma_kpa: float, b_m: float, e_s_mpa: float
    ) -> float:
        """
        Setzung abschätzen (vereinfacht, elastisch)

        s = σ * b / E_s

        Args:
            sigma_kpa: Sohldruckspannung in kPa
            b_m: Breite in m
            e_s_mpa: Steifemodul in MPa

        Returns:
            Setzung in mm
        """
        sigma_mpa = sigma_kpa / 1000.0  # kPa → MPa
        s_m = sigma_mpa * b_m / e_s_mpa  # Elastische Setzung
        s_mm = s_m * 1000.0  # m → mm
        return s_mm

    def run_optimization(self) -> List[EC7Result]:
        """
        Iterative Optimierung der Fundamentgröße

        Probiert quadratische Fundamente durch:
        1.0x1.0, 1.5x1.5, 2.0x2.0, 2.5x2.5, 3.0x3.0 m

        Returns:
            Liste der EC7Result
        """
        standard_groessen = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]  # m
        self.results = []

        for b_m in standard_groessen:
            l_m = b_m  # Quadratisch
            t_m = self.config.T_M

            # Gesamtlast
            N_gesamt_kn = self.calculate_total_load(b_m, l_m, t_m)

            # Sohldruckspannung
            sigma_kpa = self.calculate_soil_pressure(N_gesamt_kn, b_m, l_m)

            # Ausnutzung
            eta_sohldruck = sigma_kpa / self.config.SIGMA_ZUL_KPA

            # Setzung
            setzung_mm = self.calculate_settlement(sigma_kpa, b_m, self.config.E_S_MPA)

            # Status (vereinfacht: nur Sohldruck-Check)
            status = "OK" if eta_sohldruck <= 1.0 else "FAIL"

            # Details
            A_m2 = b_m * l_m
            details = f"A={A_m2:.1f}m², σ={sigma_kpa:.1f}kPa, s={setzung_mm:.1f}mm"

            result = EC7Result(
                b_m=b_m,
                l_m=l_m,
                t_m=t_m,
                A_m2=A_m2,
                N_gesamt_kn=N_gesamt_kn,
                sigma_kpa=sigma_kpa,
                sigma_zul_kpa=self.config.SIGMA_ZUL_KPA,
                eta_sohldruck=eta_sohldruck,
                setzung_mm=setzung_mm,
                status=status,
                details=details,
            )

            self.results.append(result)

            # Erste OK-Lösung gefunden? → Fertig
            if status == "OK":
                break

        return self.results

    def generate_report(self) -> str:
        """Technischen Bericht generieren"""
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Audit-Hash
        audit_data = {
            "projekt": self.config.PROJEKT,
            "timestamp": timestamp,
            "n_ed_kn": self.config.N_ED_KN,
            "bodenklasse": self.config.BODENKLASSE,
        }
        audit_hash = hashlib.sha256(
            json.dumps(audit_data, sort_keys=True).encode()
        ).hexdigest()[:16]

        # Ergebnis
        if not self.results:
            final_result = "KEINE LÖSUNG"
            optimale_groesse = 0
        else:
            ok_results = [r for r in self.results if r.status == "OK"]
            if ok_results:
                final_result = ok_results[0]
                optimale_groesse = final_result.b_m
            else:
                final_result = "KEINE AUSREICHENDE GRÖSSE"
                optimale_groesse = 0

        report = f"""
{'=' * 80}
TECHNISCHER BERICHT V1.0 – Geotechnik-Bemessung (EC7-AT)
{'=' * 80}
Projekt:          {self.config.PROJEKT}
Berechnungsdatum: {datetime.utcnow().strftime('%Y-%m-%d')}
Norm:             ÖNORM EN 1997-1 (Eurocode 7 Austria)
TRL-Status:       4 (Laboratory Validation)
Version:          1.0.0 MVP
Prüf-Hash:        {audit_hash}

⚠️  WARNUNG: Nur für Vordimensionierung!
    Finale Bemessung durch Ziviltechniker mit Baugrundgutachten!

{'-' * 80}
1. SYSTEMANGABEN
{'-' * 80}
Fundamenttyp:     Flachfundament (zentrisch belastet)
Gründungstiefe:   t = {self.config.T_M:.2f} m

{'-' * 80}
2. BODEN
{'-' * 80}
Bodenklasse:      {BODEN_KLASSEN_AT[self.config.BODENKLASSE]['bezeichnung']}
γ_Boden =         {self.config.GAMMA_BODEN_KN_M3:.1f} kN/m³
E_s =             {self.config.E_S_MPA:.1f} MPa
σ_zul =           {self.config.SIGMA_ZUL_KPA:.1f} kPa

{'-' * 80}
3. BELASTUNG
{'-' * 80}
Nutzlast:         N_Ed = {self.config.N_ED_KN:.1f} kN

{'-' * 80}
4. NACHWEIS
{'-' * 80}
"""

        if isinstance(final_result, EC7Result):
            report += f"""Optimale Größe:   {optimale_groesse:.1f} x {optimale_groesse:.1f} m
Fläche:           A = {final_result.A_m2:.1f} m²
Gesamtlast:       N_gesamt = {final_result.N_gesamt_kn:.1f} kN
Sohldruckspannung: σ = {final_result.sigma_kpa:.1f} kPa
η_sohldruck =     {final_result.eta_sohldruck:.3f} {'✓' if final_result.eta_sohldruck <= 1.0 else '✗'}
Setzung:          s ≈ {final_result.setzung_mm:.1f} mm

{'-' * 80}
5. ERGEBNIS
{'-' * 80}
Status:           {final_result.status}
Größen geprüft:   {len(self.results)}
Gesamtbewertung:  {'BESTANDEN ✓' if final_result.status == 'OK' else 'NICHT BESTANDEN ✗'}

⚠️  HINWEISE:
- Setzungsberechnung ist stark vereinfacht!
- Baugrundgutachten durch geotechnischen Sachverständigen erforderlich!
- Grundbruchnachweis nicht enthalten (Future)!
"""
        else:
            report += f"""Status:           {final_result}
Größen geprüft:   {len(self.results)}
Empfehlung:       Baugrundverbesserung oder Tiefgründung prüfen
"""

        report += f"""
{'=' * 80}
Prüf-Hash: {audit_hash}
{'=' * 80}
"""
        return report


# =============================================================================
# MAIN: Demo-Berechnung
# =============================================================================

if __name__ == "__main__":
    print("🏔️  Eurocode 7 (EC7-AT) V1.0 – Geotechnik-Bemessung")
    print("=" * 70)
    print("⚠️  WARNUNG: Nur für Vordimensionierung!")
    print("    Finale Bemessung durch Ziviltechniker mit Baugrundgutachten!")
    print("=" * 70)
    print()

    # Standard-Konfiguration
    config = EC7Config(
        N_ED_KN=500.0,
        BODENKLASSE="KIES_DICHT",
        T_M=1.0,
    )

    print(f"SYSTEM: Flachfundament")
    print(f"BODEN: {config.BODENKLASSE}")
    print(f"LAST: N_Ed = {config.N_ED_KN} kN")
    print()

    # Berechnung
    calc = FlachfundamentEC7AT_V1(config)
    print("🔄 Starte Fundamentgrößen-Optimierung...\n")
    results = calc.run_optimization()

    # Ergebnis
    ok_results = [r for r in results if r.status == "OK"]
    if ok_results:
        best = ok_results[0]
        print("✅ Lösung gefunden:")
        print(f"   Größe: {best.b_m:.1f} x {best.l_m:.1f} m")
        print(f"   Fläche: A = {best.A_m2:.1f} m²")
        print(f"   σ = {best.sigma_kpa:.1f} kPa")
        print(f"   η_sohldruck = {best.eta_sohldruck:.3f}")
        print(f"   Setzung ≈ {best.setzung_mm:.1f} mm")
        print(f"   Status: {best.status}")
    else:
        print("❌ Keine ausreichende Lösung gefunden!")

    print()
    print("=" * 70)

    # Technischer Bericht
    report = calc.generate_report()
    print(report)
