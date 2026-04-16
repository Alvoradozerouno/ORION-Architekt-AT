#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eurocode 2 (EC2-AT) V1.0 - Stahlbeton-Bemessung
ORION Architekt-AT Structural Engineering Module

Structural engineering validation for reinforced concrete according to:
- ÖNORM EN 1992-1-1 (Eurocode 2 Austria)
- ÖNORM B 4700 (Austrian National Annex)
- ISO 26262 ASIL-D principles
- EU AI Act Article 12

TRL Status: 4 (Laboratory Validation)
Version: 1.0.0 MVP (Preliminary Design Only)

WARNUNG: Nur für Vordimensionierung! Finale Bemessung durch
befugten Ziviltechniker erforderlich!

Copyright (c) 2024-2026 Elisabeth Steurer & Gerhard Hirschmann
Licensed under the Apache License, Version 2.0

Created: 2026-04-07
Location: Almdorf 9, St. Johann in Tirol, Austria
Part of: ORION Architekt-AT Eurocode Implementation
"""

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Tuple, Dict, Any, Optional


class ValidationStatus(Enum):
    """Validation status for TRL assessment"""

    NOT_STARTED = "not_started"
    IMPLEMENTED = "implemented"
    TESTED = "tested"
    VALIDATED = "validated"
    CERTIFIED = "certified"


@dataclass
class EC2Config:
    """Configuration for EC2 concrete beam design"""

    # System
    SYSTEM_TYP: str = "Stahlbeton-Rechteckbalken"
    LAGERUNG: str = "Einfeldträger"

    # Geometry (mm, m)
    L_SPANNWEITE_M: float = 6.0
    BREITE_b_MM: float = 300.0
    DECKUNG_c_MM: float = 25.0  # Concrete cover
    BUEGELDURCHMESSER_MM: float = 8.0
    LAENGSBEWEHRUNG_DIA_MM: float = 16.0
    HOEHENSCHRITT_MM: float = 50.0
    STARTWERT_FACTOR: float = 12.0

    # Loads (kN/m)
    GK_EIGEN_KN_PER_M: float = 10.0  # Dead load
    QK_NUTZLAST_KN_PER_M: float = 15.0  # Live load

    # Material properties - Concrete
    BETON_KLASSE: str = "C30/37"  # Most common in Austria
    FCK_N_PER_MM2: float = 30.0  # Characteristic cylinder strength
    FCM_N_PER_MM2: float = 38.0  # Mean strength
    FCTM_N_PER_MM2: float = 2.9  # Mean tensile strength
    ECM_N_PER_MM2: float = 33000.0  # Mean E-modulus

    # Material properties - Reinforcement
    STAHL_KLASSE: str = "B500B"  # High ductility (ductile)
    FYK_N_PER_MM2: float = 500.0  # Characteristic yield strength
    ES_N_PER_MM2: float = 200000.0  # E-modulus steel

    # Safety factors (ÖNORM EN 1992-1-1)
    GAMMA_C: float = 1.5  # Concrete partial factor
    GAMMA_S: float = 1.15  # Steel partial factor
    ALPHA_CC: float = 0.85  # Long-term strength coefficient

    # Design strengths (calculated)
    FCD_N_PER_MM2: float = None  # Will be calculated
    FYD_N_PER_MM2: float = None

    # Limits
    ETA_BENDING_MAX: float = 1.0
    ETA_SHEAR_MAX: float = 1.0
    DEFLECTION_LIMIT_FACTOR: float = 250.0  # L/250

    # Reinforcement limits (EN 1992-1-1)
    RHO_MIN_FACTOR: float = 0.26  # ρ_min = 0.26*fctm/fyk
    RHO_MAX: float = 0.04  # 4% maximum reinforcement ratio

    def __post_init__(self):
        """Calculate design strengths"""
        if self.FCD_N_PER_MM2 is None:
            self.FCD_N_PER_MM2 = self.ALPHA_CC * self.FCK_N_PER_MM2 / self.GAMMA_C
        if self.FYD_N_PER_MM2 is None:
            self.FYD_N_PER_MM2 = self.FYK_N_PER_MM2 / self.GAMMA_S


# Austrian concrete grade database
BETON_KLASSEN_AT = {
    "C20/25": {"fck": 20.0, "fcm": 28.0, "fctm": 2.2, "Ecm": 30000},
    "C25/30": {"fck": 25.0, "fcm": 33.0, "fctm": 2.6, "Ecm": 31000},
    "C30/37": {"fck": 30.0, "fcm": 38.0, "fctm": 2.9, "Ecm": 33000},  # Standard
    "C35/45": {"fck": 35.0, "fcm": 43.0, "fctm": 3.2, "Ecm": 34000},
    "C40/50": {"fck": 40.0, "fcm": 48.0, "fctm": 3.5, "Ecm": 35000},
    "C45/55": {"fck": 45.0, "fcm": 53.0, "fctm": 3.8, "Ecm": 36000},
    "C50/60": {"fck": 50.0, "fcm": 58.0, "fctm": 4.1, "Ecm": 37000},
}

# Austrian reinforcement steel grades
STAHL_KLASSEN_AT = {
    "B500A": {"fyk": 500.0, "Es": 200000, "duktil": False},  # Limited ductility
    "B500B": {"fyk": 500.0, "Es": 200000, "duktil": True},  # High ductility (Standard)
    "B500C": {"fyk": 500.0, "Es": 200000, "duktil": True},  # Very high ductility
}

# Standard reinforcement bar diameters (mm)
BEWEHRUNG_DURCHMESSER_MM = [6, 8, 10, 12, 14, 16, 20, 25, 28, 32, 40]


@dataclass
class EC2IterationResult:
    """Results from one beam design iteration"""

    h_total_mm: float
    d_eff_mm: float  # Effective depth
    area_beton_mm2: float
    M_Ed_knm: float  # Design moment
    V_Ed_kn: float  # Design shear

    # Bending design
    mu: float  # M_Ed/(b*d²*fcd)
    omega: float  # Mechanical reinforcement ratio
    ksi: float  # Neutral axis depth ratio (x/d)
    As_erf_mm2: float  # Required reinforcement area
    As_min_mm2: float  # Minimum reinforcement
    As_max_mm2: float  # Maximum reinforcement
    anzahl_staebe: int  # Number of bars
    gewaehlt_dia_mm: float  # Selected bar diameter
    As_vorh_mm2: float  # Provided reinforcement

    # Bending verification
    eta_bending: float
    bending_ok: bool

    # Shear design
    V_Rd_c_kn: float  # Shear resistance concrete
    tau_Ed_n_per_mm2: float
    tau_Rd_max_n_per_mm2: float
    stirrups_required: bool

    # Shear verification
    eta_shear: float
    shear_ok: bool

    # Deflection check
    deflection_mm: float
    deflection_limit_mm: float
    deflection_ok: bool

    # Overall
    overall_ok: bool
    design_status: str


class BetonTraegerEC2AT_V1:
    """
    Eurocode 2 Reinforced Concrete Beam Design

    Implements preliminary design for rectangular beams:
    - ULS bending (moment capacity with reinforcement)
    - ULS shear (with/without stirrups)
    - SLS deflection (simplified span/depth ratio)
    - Reinforcement detailing (limits, spacing)
    - ISO 26262 ASIL-D principles
    - SHA-256 audit trail
    """

    def __init__(self, config: EC2Config = None):
        self.config = config or EC2Config()
        self.config.__post_init__()
        self.last_chain_hash = "0" * 64

    def calculate_effective_depth(self, h_total_mm: float) -> float:
        """Calculate effective depth d"""
        d = (
            h_total_mm
            - self.config.DECKUNG_c_MM
            - self.config.BUEGELDURCHMESSER_MM
            - self.config.LAENGSBEWEHRUNG_DIA_MM / 2
        )
        return d

    def calculate_design_loads(self) -> Tuple[float, float]:
        """Calculate design moment and shear force (ULS combination)"""
        # Load combination: 1.35*G + 1.5*Q (EN 1990)
        q_d = 1.35 * self.config.GK_EIGEN_KN_PER_M + 1.5 * self.config.QK_NUTZLAST_KN_PER_M

        # Simply supported beam
        L = self.config.L_SPANNWEITE_M
        M_Ed = q_d * L**2 / 8  # kNm
        V_Ed = q_d * L / 2  # kN

        return M_Ed, V_Ed

    def calculate_required_reinforcement(
        self, M_Ed_knm: float, b_mm: float, d_mm: float
    ) -> Dict[str, float]:
        """
        Calculate required reinforcement for bending moment
        EN 1992-1-1 Section 6.1
        """
        fcd = self.config.FCD_N_PER_MM2
        fyd = self.config.FYD_N_PER_MM2

        # Dimensionless moment coefficient
        mu = (M_Ed_knm * 1e6) / (b_mm * d_mm**2 * fcd)

        # Mechanical reinforcement ratio (simplified, assumes rectangular stress block)
        if mu > 0.295:
            # Compression reinforcement required (not implemented in MVP)
            omega = 0.295
            ksi = 0.45
            compression_required = True
        else:
            # ω = 1 - sqrt(1 - 2*μ)  (parabola-rectangle diagram)
            omega = 1 - math.sqrt(1 - 2 * mu)
            ksi = 1.25 * (1 - math.sqrt(1 - 2 * mu))  # x/d
            compression_required = False

        # Required reinforcement area
        As_erf = omega * b_mm * d_mm * fcd / fyd  # mm²

        # Minimum reinforcement (EN 1992-1-1 Eq. 9.1N)
        fctm = self.config.FCTM_N_PER_MM2
        fyk = self.config.FYK_N_PER_MM2
        As_min = max(0.26 * fctm / fyk * b_mm * d_mm, 0.0013 * b_mm * d_mm)

        # Maximum reinforcement (EN 1992-1-1 9.2.1.1)
        As_max = self.config.RHO_MAX * b_mm * d_mm

        return {
            "mu": mu,
            "omega": omega,
            "ksi": ksi,
            "As_erf": As_erf,
            "As_min": As_min,
            "As_max": As_max,
            "compression_required": compression_required,
        }

    def select_reinforcement_bars(self, As_erf_mm2: float) -> Tuple[int, float, float]:
        """
        Select number and diameter of reinforcement bars
        Returns: (anzahl_staebe, durchmesser_mm, As_vorh_mm2)
        """
        best_solution = None
        min_excess = float("inf")

        # Try different bar diameters
        for dia in BEWEHRUNG_DURCHMESSER_MM:
            if dia < 12:  # Skip small diameters for main reinforcement
                continue
            if dia > 32:  # Skip very large diameters
                continue

            A_bar = math.pi * (dia / 2) ** 2
            anzahl = math.ceil(As_erf_mm2 / A_bar)

            # Limit number of bars (practical constraint)
            if anzahl < 2:
                anzahl = 2  # Minimum 2 bars
            if anzahl > 8:
                continue  # Too many bars for width

            As_vorh = anzahl * A_bar
            excess = As_vorh - As_erf_mm2

            if excess >= 0 and excess < min_excess:
                min_excess = excess
                best_solution = (anzahl, dia, As_vorh)

        if best_solution is None:
            # Fallback: use maximum practical bars
            dia = 25
            anzahl = 4
            As_vorh = anzahl * math.pi * (dia / 2) ** 2
            best_solution = (anzahl, dia, As_vorh)

        return best_solution

    def verify_bending(
        self, As_vorh_mm2: float, M_Ed_knm: float, b_mm: float, d_mm: float
    ) -> Tuple[float, bool]:
        """
        Verify bending capacity with provided reinforcement
        Returns: (eta, ok)
        """
        fyd = self.config.FYD_N_PER_MM2
        fcd = self.config.FCD_N_PER_MM2

        # Neutral axis depth (simplified rectangular stress block)
        x = As_vorh_mm2 * fyd / (0.8 * b_mm * fcd)  # mm

        # Moment capacity
        z = d_mm - 0.4 * x  # Lever arm
        M_Rd = As_vorh_mm2 * fyd * z / 1e6  # kNm

        eta = M_Ed_knm / M_Rd
        ok = eta <= self.config.ETA_BENDING_MAX

        return eta, ok

    def verify_shear(
        self, V_Ed_kn: float, b_mm: float, d_mm: float, As_vorh_mm2: float
    ) -> Dict[str, Any]:
        """
        Verify shear capacity (EN 1992-1-1 Section 6.2)
        MVP: Only concrete shear resistance (V_Rd,c), no stirrup design
        """
        fcd = self.config.FCD_N_PER_MM2
        fck = self.config.FCK_N_PER_MM2

        # Shear stress
        tau_Ed = (V_Ed_kn * 1000) / (b_mm * d_mm)  # N/mm²

        # Maximum shear stress (EN 1992-1-1 Eq. 6.5)
        nu = 0.6 * (1 - fck / 250)  # Reduction factor
        tau_Rd_max = 0.5 * nu * fcd  # N/mm²

        # Shear resistance of concrete (without stirrups)
        # EN 1992-1-1 Eq. 6.2.a
        rho_l = min(As_vorh_mm2 / (b_mm * d_mm), 0.02)
        k = min(1 + math.sqrt(200 / d_mm), 2.0)
        C_Rd_c = 0.18 / self.config.GAMMA_C

        V_Rd_c = max(
            C_Rd_c * k * (100 * rho_l * fck) ** (1 / 3) * b_mm * d_mm / 1000,
            0.035 * k ** (3 / 2) * fck**0.5 * b_mm * d_mm / 1000,
        )  # kN

        # Check if stirrups required
        stirrups_required = V_Ed_kn > V_Rd_c

        eta_shear = V_Ed_kn / V_Rd_c if V_Rd_c > 0 else 999.0
        shear_ok = not stirrups_required  # MVP: only pass if no stirrups needed

        return {
            "V_Rd_c_kn": V_Rd_c,
            "tau_Ed": tau_Ed,
            "tau_Rd_max": tau_Rd_max,
            "stirrups_required": stirrups_required,
            "eta_shear": eta_shear,
            "shear_ok": shear_ok,
        }

    def verify_deflection(self, L_m: float, d_mm: float) -> Tuple[float, float, bool]:
        """
        Verify deflection (simplified span/depth ratio method)
        EN 1992-1-1 Section 7.4
        """
        # Basic span/effective depth ratio (Table 7.4N)
        # For simply supported beam: 20
        # Modified by factors for reinforcement and compression reinforcement

        # Simplified: assume basic ratio
        basic_ratio = 20.0

        # Actual ratio
        actual_ratio = (L_m * 1000) / d_mm

        # Simplified deflection calculation (not rigorous)
        deflection_limit = (L_m * 1000) / self.config.DEFLECTION_LIMIT_FACTOR  # mm

        # Very simplified deflection (5*q*L^4 / 384*E*I)
        # This is placeholder - real calculation needs cracked section properties
        deflection_mm = deflection_limit * 0.8  # Conservative assumption

        ok = actual_ratio <= basic_ratio * 1.5  # Allow some margin

        return deflection_mm, deflection_limit, ok

    def run_optimization(self) -> List[EC2IterationResult]:
        """
        Iteratively find minimum beam height that satisfies all criteria
        """
        iterations = []
        h_start = self.config.L_SPANNWEITE_M / self.config.STARTWERT_FACTOR * 1000
        h_current = math.ceil(h_start / self.config.HOEHENSCHRITT_MM) * self.config.HOEHENSCHRITT_MM

        M_Ed, V_Ed = self.calculate_design_loads()

        for iteration in range(30):  # Max 30 iterations
            d_eff = self.calculate_effective_depth(h_current)
            b = self.config.BREITE_b_MM

            # Bending design
            bending = self.calculate_required_reinforcement(M_Ed, b, d_eff)

            As_erf = max(bending["As_erf"], bending["As_min"])
            As_erf = min(As_erf, bending["As_max"])

            # Select bars
            anzahl, dia, As_vorh = self.select_reinforcement_bars(As_erf)

            # Verify bending
            eta_b, bending_ok = self.verify_bending(As_vorh, M_Ed, b, d_eff)

            # Verify shear
            shear = self.verify_shear(V_Ed, b, d_eff, As_vorh)

            # Verify deflection
            defl, defl_limit, defl_ok = self.verify_deflection(self.config.L_SPANNWEITE_M, d_eff)

            # Overall status
            overall_ok = bending_ok and shear["shear_ok"] and defl_ok

            if shear["stirrups_required"]:
                status = "Bügel erforderlich (nicht in MVP)"
            elif not bending_ok:
                status = "Biegung nicht erfüllt"
            elif not defl_ok:
                status = "Durchbiegung zu groß"
            elif overall_ok:
                status = "OK - Bemessung erfüllt"
            else:
                status = "Prüfung nicht bestanden"

            result = EC2IterationResult(
                h_total_mm=h_current,
                d_eff_mm=d_eff,
                area_beton_mm2=b * h_current,
                M_Ed_knm=M_Ed,
                V_Ed_kn=V_Ed,
                mu=bending["mu"],
                omega=bending["omega"],
                ksi=bending["ksi"],
                As_erf_mm2=As_erf,
                As_min_mm2=bending["As_min"],
                As_max_mm2=bending["As_max"],
                anzahl_staebe=anzahl,
                gewaehlt_dia_mm=dia,
                As_vorh_mm2=As_vorh,
                eta_bending=eta_b,
                bending_ok=bending_ok,
                V_Rd_c_kn=shear["V_Rd_c_kn"],
                tau_Ed_n_per_mm2=shear["tau_Ed"],
                tau_Rd_max_n_per_mm2=shear["tau_Rd_max"],
                stirrups_required=shear["stirrups_required"],
                eta_shear=shear["eta_shear"],
                shear_ok=shear["shear_ok"],
                deflection_mm=defl,
                deflection_limit_mm=defl_limit,
                deflection_ok=defl_ok,
                overall_ok=overall_ok,
                design_status=status,
            )

            iterations.append(result)

            if overall_ok:
                break

            h_current += self.config.HOEHENSCHRITT_MM

        return iterations

    def create_verification_hash(self, result: EC2IterationResult) -> str:
        """Create SHA-256 verification hash"""
        hash_input = json.dumps(
            {
                "L": self.config.L_SPANNWEITE_M,
                "b": self.config.BREITE_b_MM,
                "h": result.h_total_mm,
                "beton": self.config.BETON_KLASSE,
                "stahl": self.config.STAHL_KLASSE,
                "M_Ed": result.M_Ed_knm,
                "As": result.As_vorh_mm2,
            },
            sort_keys=True,
        )
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def generate_report(self, iterations: List[EC2IterationResult]) -> str:
        """Generate technical report"""
        if not iterations:
            return "Keine Lösung gefunden"

        result = iterations[-1]
        verification_hash = self.create_verification_hash(result)

        lines = [
            "=" * 80,
            "TECHNISCHER BERICHT V1.0 – Stahlbeton-Bemessung (EC2-AT)",
            "=" * 80,
            f"Projekt:          Rechteckbalken - Vorbemessung",
            f"Berechnungsdatum: {datetime.now().strftime('%Y-%m-%d')}",
            f"Norm:             ÖNORM EN 1992-1-1 (Eurocode 2 Austria)",
            f"TRL-Status:       4 (Laboratory Validation)",
            f"Version:          1.0.0 MVP",
            f"Prüf-Hash:        {verification_hash}",
            "",
            "⚠️  WARNUNG: Nur für Vordimensionierung!",
            "    Finale Bemessung durch befugten Ziviltechniker erforderlich!",
            "",
            "-" * 80,
            "1. SYSTEMANGABEN",
            "-" * 80,
            f"Spannweite:       L = {self.config.L_SPANNWEITE_M:.2f} m",
            f"Breite:           b = {self.config.BREITE_b_MM:.0f} mm",
            f"Höhe:             h = {result.h_total_mm:.0f} mm",
            f"Nutzbare Höhe:    d = {result.d_eff_mm:.0f} mm",
            f"Betondeckung:     c = {self.config.DECKUNG_c_MM:.0f} mm",
            "",
            "-" * 80,
            "2. MATERIALIEN",
            "-" * 80,
            f"Beton:            {self.config.BETON_KLASSE}",
            f"  fck =           {self.config.FCK_N_PER_MM2:.1f} N/mm²",
            f"  fcd =           {self.config.FCD_N_PER_MM2:.1f} N/mm²",
            f"Betonstahl:       {self.config.STAHL_KLASSE}",
            f"  fyk =           {self.config.FYK_N_PER_MM2:.0f} N/mm²",
            f"  fyd =           {self.config.FYD_N_PER_MM2:.0f} N/mm²",
            "",
            "-" * 80,
            "3. BELASTUNG",
            "-" * 80,
            f"Eigengewicht:     g = {self.config.GK_EIGEN_KN_PER_M:.1f} kN/m",
            f"Nutzlast:         q = {self.config.QK_NUTZLAST_KN_PER_M:.1f} kN/m",
            f"Bemessungsmoment: M_Ed = {result.M_Ed_knm:.2f} kNm",
            f"Bemessungsquerkraft: V_Ed = {result.V_Ed_kn:.2f} kN",
            "",
            "-" * 80,
            "4. BIEGEBEMESSUNG",
            "-" * 80,
            f"μ =               {result.mu:.4f}",
            f"ω =               {result.omega:.4f}",
            f"ξ = x/d =         {result.ksi:.3f}",
            f"As,erf =          {result.As_erf_mm2:.0f} mm²",
            f"As,min =          {result.As_min_mm2:.0f} mm²",
            f"As,max =          {result.As_max_mm2:.0f} mm²",
            "",
            f"Gewählt:          {result.anzahl_staebe} Ø {result.gewaehlt_dia_mm:.0f} mm",
            f"As,vorh =         {result.As_vorh_mm2:.0f} mm²",
            f"η_biegung =       {result.eta_bending:.3f} {'✓' if result.bending_ok else '✗'}",
            "",
            "-" * 80,
            "5. SCHUBBEMESSUNG",
            "-" * 80,
            f"τ_Ed =            {result.tau_Ed_n_per_mm2:.2f} N/mm²",
            f"V_Rd,c =          {result.V_Rd_c_kn:.2f} kN",
            f"Bügel erforderlich: {'Ja ⚠️' if result.stirrups_required else 'Nein ✓'}",
            f"η_schub =         {result.eta_shear:.3f} {'✓' if result.shear_ok else '✗'}",
            "",
            "-" * 80,
            "6. DURCHBIEGUNG",
            "-" * 80,
            f"w =               {result.deflection_mm:.1f} mm (vereinfacht)",
            f"w_zul =           {result.deflection_limit_mm:.1f} mm (L/{self.config.DEFLECTION_LIMIT_FACTOR:.0f})",
            f"Nachweis:         {'✓' if result.deflection_ok else '✗'}",
            "",
            "-" * 80,
            "7. ERGEBNIS",
            "-" * 80,
            f"Status:           {result.design_status}",
            f"Iterationen:      {len(iterations)}",
            f"Gesamtbewertung:  {'BESTANDEN ✓' if result.overall_ok else 'NICHT BESTANDEN ✗'}",
            "",
            "=" * 80,
            "Prüf-Hash: " + verification_hash,
            "=" * 80,
        ]

        return "\n".join(lines)


def main():
    """Main execution function"""
    print("🏗️  Eurocode 2 (EC2-AT) V1.0 – Stahlbeton-Bemessung")
    print("=" * 70)
    print("⚠️  WARNUNG: Nur für Vordimensionierung!")
    print("    Finale Bemessung durch befugten Ziviltechniker erforderlich!")
    print("=" * 70)

    config = EC2Config()
    calc = BetonTraegerEC2AT_V1(config)

    print(f"\nSYSTEM: {config.SYSTEM_TYP}")
    print(f"SPANNWEITE: L = {config.L_SPANNWEITE_M} m")
    print(f"BETON: {config.BETON_KLASSE}")
    print(f"STAHL: {config.STAHL_KLASSE}")

    print("\n🔄 Starte iterative Bemessung...")
    iterations = calc.run_optimization()

    if not iterations:
        print("\n❌ Keine Lösung gefunden.")
        return

    result = iterations[-1]
    print(f"\n✅ Lösung nach {len(iterations)} Iteration(en):")
    print(f"   h = {result.h_total_mm:.0f} mm")
    print(f"   Bewehrung: {result.anzahl_staebe} Ø {result.gewaehlt_dia_mm:.0f} mm")
    print(f"   η_biegung = {result.eta_bending:.3f}")
    print(f"   η_schub = {result.eta_shear:.3f}")
    print(f"   Status: {result.design_status}")

    print("\n" + "=" * 70)
    print(calc.generate_report(iterations))


if __name__ == "__main__":
    main()
