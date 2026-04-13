#!/usr/bin/env python3
"""
=============================================================================
EUROCODE 6 (EC6-AT) V1.0 – MAUERWERKSBAU-BEMESSUNG
=============================================================================
ÖNORM EN 1996-1-1 (Eurocode 6 Austria) – Mauerwerkswände

Autoren: Elisabeth Steurer & Gerhard Hirschmann
Datum: 2026-04-07
Ort: Almdorf 9, St. Johann in Tirol, Austria
Lizenz: Apache 2.0

⚠️  WARNUNG: Nur für Vordimensionierung!
    Finale Bemessung durch befugten Ziviltechniker erforderlich!

NORMEN:
- ÖNORM EN 1996-1-1: Eurocode 6 - Mauerwerksbau
- ÖNORM B 3350: Österreichischer Nationaler Anhang

TRL (Technology Readiness Level): 4 (Laboratory Validation)
ISO 26262 ASIL-D Prinzipien für deterministische Berechnung

SCOPE (MVP):
- Unbewehrte Mauerwerkswände unter Vertikallast
- Knicknachweis für schlanke Wände
- Druckfestigkeit EN 1996-1-1 Section 6.1
- Österreichische Mauersteine (Ziegel, Porenbeton, Kalksandstein)

NICHT SCOPE (Future):
- Bewehrtes Mauerwerk
- Erdbebennachweis (siehe EC8)
- Horizontale Lasten (Wind)
=============================================================================
"""

import math
import hashlib
import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime


# =============================================================================
# ÖSTERREICHISCHE MAUERSTEIN-DATENBANK
# =============================================================================

MAUERSTEIN_KLASSEN_AT = {
    # Ziegel (Österreichische Tonziegel)
    "ZIEGEL_6": {
        "bezeichnung": "Hochlochziegel 6 N/mm²",
        "fb": 6.0,  # Normierte Druckfestigkeit N/mm²
        "rho": 800,  # Rohdichte kg/m³
        "lambda": 0.12,  # Wärmeleitfähigkeit W/(m·K)
    },
    "ZIEGEL_8": {
        "bezeichnung": "Hochlochziegel 8 N/mm²",
        "fb": 8.0,
        "rho": 900,
        "lambda": 0.14,
    },
    "ZIEGEL_12": {
        "bezeichnung": "Hochlochziegel 12 N/mm² (Standard)",
        "fb": 12.0,
        "rho": 1000,
        "lambda": 0.18,
    },
    # Porenbeton
    "PORENBETON_2": {
        "bezeichnung": "Porenbeton PP2/0.40",
        "fb": 2.0,
        "rho": 400,
        "lambda": 0.10,
    },
    "PORENBETON_4": {
        "bezeichnung": "Porenbeton PP4/0.50",
        "fb": 4.0,
        "rho": 500,
        "lambda": 0.12,
    },
    # Kalksandstein
    "KS_12": {
        "bezeichnung": "Kalksandstein KS 12",
        "fb": 12.0,
        "rho": 1800,
        "lambda": 0.70,
    },
    "KS_20": {
        "bezeichnung": "Kalksandstein KS 20 (Hochfest)",
        "fb": 20.0,
        "rho": 2000,
        "lambda": 0.80,
    },
}

MOERTEL_KLASSEN_AT = {
    "M5": {"fm": 5.0, "bezeichnung": "Mörtel M5"},
    "M10": {"fm": 10.0, "bezeichnung": "Mörtel M10 (Standard)"},
    "M15": {"fm": 15.0, "bezeichnung": "Mörtel M15"},
}


# =============================================================================
# KONFIGURATION
# =============================================================================


@dataclass
class EC6Config:
    """Konfiguration für EC6 Mauerwerksbemessung"""

    # Geometrie
    WANDHOEHE_M: float = 3.0  # Geschosshöhe
    WANDDICKE_MM: float = 300  # Wanddicke (250, 300, 380, 420 mm Standard)
    WANDLAENGE_M: float = 5.0  # Wandlänge

    # Material
    MAUERSTEIN: str = "ZIEGEL_12"  # Mauerstein-Klasse
    MOERTEL: str = "M10"  # Mörtel-Klasse

    # Belastung (Vertikallast)
    N_ED_KN: float = 200.0  # Bemessungs-Normalkraft

    # Lagerung
    LAGERUNG_OBEN: str = "FREI"  # FREI oder GEHALTEN
    LAGERUNG_UNTEN: str = "GEHALTEN"  # Immer gehalten (Fundament)

    # Teilsicherheitsbeiwerte (EN 1996-1-1 Table 2.3)
    GAMMA_M: float = 2.0  # Teilsicherheitsbeiwert Mauerwerk

    # Sonstige
    PROJEKT: str = "Mauerwerkswand - Vorbemessung"

    def __post_init__(self):
        # Mauerstein-Eigenschaften laden
        if self.MAUERSTEIN not in MAUERSTEIN_KLASSEN_AT:
            raise ValueError(f"Unbekannte Mauerstein-Klasse: {self.MAUERSTEIN}")
        stein_data = MAUERSTEIN_KLASSEN_AT[self.MAUERSTEIN]
        self.FB = stein_data["fb"]  # Normierte Steinfestigkeit

        # Mörtel-Eigenschaften laden
        if self.MOERTEL not in MOERTEL_KLASSEN_AT:
            raise ValueError(f"Unbekannte Mörtelklasse: {self.MOERTEL}")
        moertel_data = MOERTEL_KLASSEN_AT[self.MOERTEL]
        self.FM = moertel_data["fm"]  # Mörtelfestigkeit

        # Charakteristische Druckfestigkeit berechnen (EN 1996-1-1 Eq. 3.1)
        # fk = K * fb^0.7 * fm^0.3
        K = 0.45  # Faktor für Normalsteine mit Normalmörtel
        self.FK = K * (self.FB**0.7) * (self.FM**0.3)

        # Bemessungswert der Druckfestigkeit (EN 1996-1-1 Eq. 2.7)
        self.FD = self.FK / self.GAMMA_M


# =============================================================================
# ERGEBNISSE
# =============================================================================


@dataclass
class EC6Result:
    """Einzelnes Berechnungsergebnis"""

    wanddicke_mm: float
    hoehe_m: float
    schlankheit_lambda: float
    knickreduktion_phi: float
    N_Rd_kn: float
    eta_druck: float
    status: str  # OK, FAIL
    details: str


# =============================================================================
# HAUPTKLASSE: MAUERWERKSWAND EC6-AT
# =============================================================================


class MauerwerkWandEC6AT_V1:
    """
    Mauerwerkswand-Bemessung nach EN 1996-1-1 (Eurocode 6 Austria)

    Funktionen:
    - Drucknachweis unter Vertikallast
    - Knicknachweis für schlanke Wände
    - Schlankheitsberechnung
    - Iterative Optimierung der Wanddicke
    """

    def __init__(self, config: EC6Config):
        self.config = config
        self.results: List[EC6Result] = []

    def calculate_slenderness(self, h_m: float, t_mm: float) -> float:
        """
        Schlankheit berechnen (EN 1996-1-1 Section 5.5.1)

        λ = h_ef / t_ef

        Args:
            h_m: Wandhöhe in m
            t_mm: Wanddicke in mm

        Returns:
            Schlankheit λ
        """
        # Effektive Höhe (abhängig von Lagerung)
        if (
            self.config.LAGERUNG_OBEN == "GEHALTEN"
            and self.config.LAGERUNG_UNTEN == "GEHALTEN"
        ):
            rho = 0.75  # Beidseitig gehalten
        elif self.config.LAGERUNG_OBEN == "FREI":
            rho = 1.0  # Oben frei
        else:
            rho = 0.85  # Andere Fälle

        h_ef_mm = rho * h_m * 1000  # Effektive Höhe in mm
        t_ef_mm = t_mm  # Effektive Dicke = tatsächliche Dicke

        lambda_val = h_ef_mm / t_ef_mm
        return lambda_val

    def calculate_buckling_reduction(self, lambda_val: float) -> float:
        """
        Knick-Reduktionsfaktor berechnen (EN 1996-1-1 Eq. 6.2)

        Φi = 1 - 2 * (e_mk / t)^2   für λ ≤ 27

        Für MVP: Vereinfachte Formel für mittige Last (e=0):
        Φi ≈ 1.0 für λ ≤ 12
        Φi = 1 - 0.001 * (λ - 12)^2  für 12 < λ ≤ 27

        Args:
            lambda_val: Schlankheit

        Returns:
            Reduktionsfaktor Φ (0 bis 1)
        """
        if lambda_val <= 12:
            return 1.0
        elif lambda_val <= 27:
            return max(1.0 - 0.001 * (lambda_val - 12) ** 2, 0.3)
        else:
            # Sehr schlank - nur 30% Tragfähigkeit
            return 0.3

    def calculate_load_capacity(
        self, t_mm: float, wandlaenge_m: float, fd: float, phi: float
    ) -> float:
        """
        Tragfähigkeit berechnen (EN 1996-1-1 Eq. 6.1)

        N_Rd = Φ * t * l * fd

        Args:
            t_mm: Wanddicke in mm
            wandlaenge_m: Wandlänge in m
            fd: Bemessungswert der Druckfestigkeit in N/mm²
            phi: Knick-Reduktionsfaktor

        Returns:
            N_Rd in kN
        """
        A_mm2 = t_mm * wandlaenge_m * 1000  # Querschnittsfläche
        N_Rd_n = phi * A_mm2 * fd  # in N
        N_Rd_kn = N_Rd_n / 1000  # in kN
        return N_Rd_kn

    def run_optimization(self) -> List[EC6Result]:
        """
        Iterative Optimierung der Wanddicke

        Probiert Standard-Wanddicken durch:
        250, 300, 380, 420, 500 mm

        Returns:
            Liste der EC6Result
        """
        standard_dicken = [250, 300, 380, 420, 500]  # mm
        self.results = []

        for t_mm in standard_dicken:
            # Schlankheit
            lambda_val = self.calculate_slenderness(self.config.WANDHOEHE_M, t_mm)

            # Knick-Reduktion
            phi = self.calculate_buckling_reduction(lambda_val)

            # Tragfähigkeit
            N_Rd_kn = self.calculate_load_capacity(
                t_mm, self.config.WANDLAENGE_M, self.config.FD, phi
            )

            # Ausnutzung
            eta_druck = self.config.N_ED_KN / N_Rd_kn if N_Rd_kn > 0 else 999.0

            # Status
            status = "OK" if eta_druck <= 1.0 else "FAIL"

            # Details
            details = f"λ={lambda_val:.1f}, Φ={phi:.3f}, N_Rd={N_Rd_kn:.1f}kN"

            result = EC6Result(
                wanddicke_mm=t_mm,
                hoehe_m=self.config.WANDHOEHE_M,
                schlankheit_lambda=lambda_val,
                knickreduktion_phi=phi,
                N_Rd_kn=N_Rd_kn,
                eta_druck=eta_druck,
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
            "wandhoehe_m": self.config.WANDHOEHE_M,
            "n_ed_kn": self.config.N_ED_KN,
            "mauerstein": self.config.MAUERSTEIN,
        }
        audit_hash = hashlib.sha256(
            json.dumps(audit_data, sort_keys=True).encode()
        ).hexdigest()[:16]

        # Ergebnis
        if not self.results:
            final_result = "KEINE LÖSUNG"
            optimale_dicke = 0
        else:
            ok_results = [r for r in self.results if r.status == "OK"]
            if ok_results:
                final_result = ok_results[0]
                optimale_dicke = final_result.wanddicke_mm
            else:
                final_result = "KEINE AUSREICHENDE WANDDICKE"
                optimale_dicke = 0

        report = f"""
{'=' * 80}
TECHNISCHER BERICHT V1.0 – Mauerwerksbau-Bemessung (EC6-AT)
{'=' * 80}
Projekt:          {self.config.PROJEKT}
Berechnungsdatum: {datetime.utcnow().strftime('%Y-%m-%d')}
Norm:             ÖNORM EN 1996-1-1 (Eurocode 6 Austria)
TRL-Status:       4 (Laboratory Validation)
Version:          1.0.0 MVP
Prüf-Hash:        {audit_hash}

⚠️  WARNUNG: Nur für Vordimensionierung!
    Finale Bemessung durch befugten Ziviltechniker erforderlich!

{'-' * 80}
1. SYSTEMANGABEN
{'-' * 80}
Wandhöhe:         h = {self.config.WANDHOEHE_M:.2f} m
Wandlänge:        l = {self.config.WANDLAENGE_M:.2f} m
Lagerung oben:    {self.config.LAGERUNG_OBEN}
Lagerung unten:   {self.config.LAGERUNG_UNTEN}

{'-' * 80}
2. MATERIAL
{'-' * 80}
Mauerstein:       {MAUERSTEIN_KLASSEN_AT[self.config.MAUERSTEIN]['bezeichnung']}
  fb =            {self.config.FB:.1f} N/mm²
Mörtel:           {MOERTEL_KLASSEN_AT[self.config.MOERTEL]['bezeichnung']}
  fm =            {self.config.FM:.1f} N/mm²

fk =              {self.config.FK:.2f} N/mm² (charakteristisch)
fd =              {self.config.FD:.2f} N/mm² (Bemessung)

{'-' * 80}
3. BELASTUNG
{'-' * 80}
Normalkraft:      N_Ed = {self.config.N_ED_KN:.1f} kN

{'-' * 80}
4. NACHWEIS
{'-' * 80}
"""

        if isinstance(final_result, EC6Result):
            report += f"""Optimale Wanddicke: t = {optimale_dicke:.0f} mm
Schlankheit:      λ = {final_result.schlankheit_lambda:.1f}
Knick-Reduktion:  Φ = {final_result.knickreduktion_phi:.3f}
N_Rd =            {final_result.N_Rd_kn:.1f} kN
η_druck =         {final_result.eta_druck:.3f} {'✓' if final_result.eta_druck <= 1.0 else '✗'}

{'-' * 80}
5. ERGEBNIS
{'-' * 80}
Status:           {final_result.status}
Dicken geprüft:   {len(self.results)}
Gesamtbewertung:  {'BESTANDEN ✓' if final_result.status == 'OK' else 'NICHT BESTANDEN ✗'}
"""
        else:
            report += f"""Status:           {final_result}
Dicken geprüft:   {len(self.results)}
Empfehlung:       Tragwerk überarbeiten oder höhere Festigkeit wählen
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
    print("🧱 Eurocode 6 (EC6-AT) V1.0 – Mauerwerksbau-Bemessung")
    print("=" * 70)
    print("⚠️  WARNUNG: Nur für Vordimensionierung!")
    print("    Finale Bemessung durch befugten Ziviltechniker erforderlich!")
    print("=" * 70)
    print()

    # Standard-Konfiguration
    config = EC6Config(
        WANDHOEHE_M=3.0,
        WANDLAENGE_M=5.0,
        WANDDICKE_MM=300,  # Startwert (wird optimiert)
        MAUERSTEIN="ZIEGEL_12",
        MOERTEL="M10",
        N_ED_KN=200.0,
        LAGERUNG_OBEN="FREI",
        LAGERUNG_UNTEN="GEHALTEN",
    )

    print(f"SYSTEM: Mauerwerkswand")
    print(f"HÖHE: h = {config.WANDHOEHE_M} m")
    print(f"MAUERSTEIN: {config.MAUERSTEIN}")
    print(f"NORMALKRAFT: N_Ed = {config.N_ED_KN} kN")
    print()

    # Berechnung
    calc = MauerwerkWandEC6AT_V1(config)
    print("🔄 Starte Wanddicken-Optimierung...\n")
    results = calc.run_optimization()

    # Ergebnis
    ok_results = [r for r in results if r.status == "OK"]
    if ok_results:
        best = ok_results[0]
        print("✅ Lösung gefunden:")
        print(f"   Wanddicke: t = {best.wanddicke_mm:.0f} mm")
        print(f"   Schlankheit: λ = {best.schlankheit_lambda:.1f}")
        print(f"   Φ = {best.knickreduktion_phi:.3f}")
        print(f"   η_druck = {best.eta_druck:.3f}")
        print(f"   Status: {best.status}")
    else:
        print("❌ Keine ausreichende Lösung gefunden!")

    print()
    print("=" * 70)

    # Technischer Bericht
    report = calc.generate_report()
    print(report)
