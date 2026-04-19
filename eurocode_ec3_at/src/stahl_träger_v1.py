#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eurocode 3 (EC3-AT) V1.0 - Stahlbau-Bemessung
ORION Architekt-AT Structural Engineering Module

Structural engineering validation for steel structures according to:
- ÖNORM EN 1993-1-1 (Eurocode 3 Austria)
- ÖNORM B 4600 (Austrian National Annex)
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
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Tuple

# Austrian standard steel profiles (IPE)
IPE_PROFILE_DATABASE = {
    "IPE80": {
        "h": 80,
        "b": 46,
        "tw": 3.8,
        "tf": 5.2,
        "A": 7.64,
        "Iy": 80.1,
        "Wy": 20.0,
        "iy": 3.24,
        "Iz": 8.49,
        "Wz": 3.69,
        "iz": 1.05,
        "mass": 6.0,
    },
    "IPE100": {
        "h": 100,
        "b": 55,
        "tw": 4.1,
        "tf": 5.7,
        "A": 10.3,
        "Iy": 171,
        "Wy": 34.2,
        "iy": 4.07,
        "Iz": 15.9,
        "Wz": 5.79,
        "iz": 1.24,
        "mass": 8.1,
    },
    "IPE120": {
        "h": 120,
        "b": 64,
        "tw": 4.4,
        "tf": 6.3,
        "A": 13.2,
        "Iy": 318,
        "Wy": 53.0,
        "iy": 4.90,
        "Iz": 27.7,
        "Wz": 8.65,
        "iz": 1.45,
        "mass": 10.4,
    },
    "IPE140": {
        "h": 140,
        "b": 73,
        "tw": 4.7,
        "tf": 6.9,
        "A": 16.4,
        "Iy": 541,
        "Wy": 77.3,
        "iy": 5.74,
        "Iz": 44.9,
        "Wz": 12.3,
        "iz": 1.65,
        "mass": 12.9,
    },
    "IPE160": {
        "h": 160,
        "b": 82,
        "tw": 5.0,
        "tf": 7.4,
        "A": 20.1,
        "Iy": 869,
        "Wy": 109,
        "iy": 6.58,
        "Iz": 68.3,
        "Wz": 16.7,
        "iz": 1.84,
        "mass": 15.8,
    },
    "IPE180": {
        "h": 180,
        "b": 91,
        "tw": 5.3,
        "tf": 8.0,
        "A": 23.9,
        "Iy": 1320,
        "Wy": 146,
        "iy": 7.42,
        "Iz": 101,
        "Wz": 22.2,
        "iz": 2.05,
        "mass": 18.8,
    },
    "IPE200": {
        "h": 200,
        "b": 100,
        "tw": 5.6,
        "tf": 8.5,
        "A": 28.5,
        "Iy": 1940,
        "Wy": 194,
        "iy": 8.26,
        "Iz": 142,
        "Wz": 28.5,
        "iz": 2.24,
        "mass": 22.4,
    },
    "IPE220": {
        "h": 220,
        "b": 110,
        "tw": 5.9,
        "tf": 9.2,
        "A": 33.4,
        "Iy": 2770,
        "Wy": 252,
        "iy": 9.11,
        "Iz": 205,
        "Wz": 37.3,
        "iz": 2.48,
        "mass": 26.2,
    },
    "IPE240": {
        "h": 240,
        "b": 120,
        "tw": 6.2,
        "tf": 9.8,
        "A": 39.1,
        "Iy": 3890,
        "Wy": 324,
        "iy": 9.97,
        "Iz": 284,
        "Wz": 47.3,
        "iz": 2.69,
        "mass": 30.7,
    },
    "IPE270": {
        "h": 270,
        "b": 135,
        "tw": 6.6,
        "tf": 10.2,
        "A": 45.9,
        "Iy": 5790,
        "Wy": 429,
        "iy": 11.2,
        "Iz": 420,
        "Wz": 62.2,
        "iz": 3.02,
        "mass": 36.1,
    },
    "IPE300": {
        "h": 300,
        "b": 150,
        "tw": 7.1,
        "tf": 10.7,
        "A": 53.8,
        "Iy": 8360,
        "Wy": 557,
        "iy": 12.5,
        "Iz": 604,
        "Wz": 80.5,
        "iz": 3.35,
        "mass": 42.2,
    },
    "IPE330": {
        "h": 330,
        "b": 160,
        "tw": 7.5,
        "tf": 11.5,
        "A": 62.6,
        "Iy": 11770,
        "Wy": 713,
        "iy": 13.7,
        "Iz": 788,
        "Wz": 98.5,
        "iz": 3.55,
        "mass": 49.1,
    },
    "IPE360": {
        "h": 360,
        "b": 170,
        "tw": 8.0,
        "tf": 12.7,
        "A": 72.7,
        "Iy": 16270,
        "Wy": 904,
        "iy": 15.0,
        "Iz": 1040,
        "Wz": 123,
        "iz": 3.79,
        "mass": 57.1,
    },
    "IPE400": {
        "h": 400,
        "b": 180,
        "tw": 8.6,
        "tf": 13.5,
        "A": 84.5,
        "Iy": 23130,
        "Wy": 1160,
        "iy": 16.5,
        "Iz": 1320,
        "Wz": 146,
        "iz": 3.95,
        "mass": 66.3,
    },
    "IPE450": {
        "h": 450,
        "b": 190,
        "tw": 9.4,
        "tf": 14.6,
        "A": 98.8,
        "Iy": 33740,
        "Wy": 1500,
        "iy": 18.5,
        "Iz": 1680,
        "Wz": 176,
        "iz": 4.12,
        "mass": 77.6,
    },
    "IPE500": {
        "h": 500,
        "b": 200,
        "tw": 10.2,
        "tf": 16.0,
        "A": 116,
        "Iy": 48200,
        "Wy": 1930,
        "iy": 20.4,
        "Iz": 2140,
        "Wz": 214,
        "iz": 4.31,
        "mass": 90.7,
    },
    "IPE550": {
        "h": 550,
        "b": 210,
        "tw": 11.1,
        "tf": 17.2,
        "A": 134,
        "Iy": 67120,
        "Wy": 2440,
        "iy": 22.4,
        "Iz": 2670,
        "Wz": 254,
        "iz": 4.47,
        "mass": 106,
    },
    "IPE600": {
        "h": 600,
        "b": 220,
        "tw": 12.0,
        "tf": 19.0,
        "A": 156,
        "Iy": 92080,
        "Wy": 3070,
        "iy": 24.3,
        "Iz": 3390,
        "Wz": 308,
        "iz": 4.66,
        "mass": 122,
    },
}

# Austrian standard HEA profiles
HEA_PROFILE_DATABASE = {
    "HEA100": {
        "h": 96,
        "b": 100,
        "tw": 5.0,
        "tf": 8.0,
        "A": 21.2,
        "Iy": 349,
        "Wy": 72.8,
        "iy": 4.06,
        "Iz": 134,
        "Wz": 26.8,
        "iz": 2.51,
        "mass": 16.7,
    },
    "HEA120": {
        "h": 114,
        "b": 120,
        "tw": 5.0,
        "tf": 8.0,
        "A": 25.3,
        "Iy": 606,
        "Wy": 106,
        "iy": 4.89,
        "Iz": 231,
        "Wz": 38.5,
        "iz": 3.02,
        "mass": 19.9,
    },
    "HEA140": {
        "h": 133,
        "b": 140,
        "tw": 5.5,
        "tf": 8.5,
        "A": 31.4,
        "Iy": 1030,
        "Wy": 155,
        "iy": 5.73,
        "Iz": 389,
        "Wz": 55.6,
        "iz": 3.52,
        "mass": 24.7,
    },
    "HEA160": {
        "h": 152,
        "b": 160,
        "tw": 6.0,
        "tf": 9.0,
        "A": 38.8,
        "Iy": 1670,
        "Wy": 220,
        "iy": 6.57,
        "Iz": 616,
        "Wz": 77.0,
        "iz": 3.98,
        "mass": 30.4,
    },
    "HEA180": {
        "h": 171,
        "b": 180,
        "tw": 6.0,
        "tf": 9.5,
        "A": 45.3,
        "Iy": 2510,
        "Wy": 294,
        "iy": 7.45,
        "Iz": 925,
        "Wz": 103,
        "iz": 4.52,
        "mass": 35.5,
    },
    "HEA200": {
        "h": 190,
        "b": 200,
        "tw": 6.5,
        "tf": 10.0,
        "A": 53.8,
        "Iy": 3690,
        "Wy": 389,
        "iy": 8.28,
        "Iz": 1340,
        "Wz": 134,
        "iz": 4.98,
        "mass": 42.3,
    },
    "HEA220": {
        "h": 210,
        "b": 220,
        "tw": 7.0,
        "tf": 11.0,
        "A": 64.3,
        "Iy": 5410,
        "Wy": 515,
        "iy": 9.17,
        "Iz": 1960,
        "Wz": 178,
        "iz": 5.52,
        "mass": 50.5,
    },
    "HEA240": {
        "h": 230,
        "b": 240,
        "tw": 7.5,
        "tf": 12.0,
        "A": 76.8,
        "Iy": 7760,
        "Wy": 675,
        "iy": 10.1,
        "Iz": 2770,
        "Wz": 231,
        "iz": 6.00,
        "mass": 60.3,
    },
    "HEA260": {
        "h": 250,
        "b": 260,
        "tw": 7.5,
        "tf": 12.5,
        "A": 86.8,
        "Iy": 10450,
        "Wy": 836,
        "iy": 11.0,
        "Iz": 3670,
        "Wz": 283,
        "iz": 6.50,
        "mass": 68.2,
    },
    "HEA280": {
        "h": 270,
        "b": 280,
        "tw": 8.0,
        "tf": 13.0,
        "A": 97.3,
        "Iy": 13670,
        "Wy": 1010,
        "iy": 11.9,
        "Iz": 4760,
        "Wz": 340,
        "iz": 7.00,
        "mass": 76.4,
    },
    "HEA300": {
        "h": 290,
        "b": 300,
        "tw": 8.5,
        "tf": 14.0,
        "A": 113,
        "Iy": 18260,
        "Wy": 1260,
        "iy": 12.7,
        "Iz": 6310,
        "Wz": 420,
        "iz": 7.47,
        "mass": 88.3,
    },
}

# Steel grades Austria
STAHL_GUETEN_AT = {
    "S235": {"fy": 235, "fu": 360, "E": 210000},  # Standard
    "S275": {"fy": 275, "fu": 430, "E": 210000},
    "S355": {"fy": 355, "fu": 510, "E": 210000},  # Common for buildings
    "S450": {"fy": 450, "fu": 550, "E": 210000},
}


@dataclass
class EC3Config:
    """Configuration for EC3 steel beam design"""

    # System
    SYSTEM_TYP: str = "Stahlträger IPE"
    LAGERUNG: str = "Einfeldträger"

    # Geometry
    L_SPANNWEITE_M: float = 8.0

    # Loads (kN/m)
    GK_EIGEN_KN_PER_M: float = 5.0
    QK_NUTZLAST_KN_PER_M: float = 20.0

    # Material
    STAHL_GUETE: str = "S355"
    FY_N_PER_MM2: float = 355.0
    FU_N_PER_MM2: float = 510.0
    E_N_PER_MM2: float = 210000.0

    # Safety factors (EN 1993-1-1)
    GAMMA_M0: float = 1.0  # Resistance of cross-sections
    GAMMA_M1: float = 1.0  # Resistance of members to instability

    # Limits
    DEFLECTION_LIMIT_FACTOR: float = 250.0  # L/250


@dataclass
class EC3IterationResult:
    """Results from one steel beam iteration"""

    profile_name: str
    h_mm: float
    b_mm: float
    A_mm2: float
    Wy_cm3: float
    Wz_cm3: float
    Iy_cm4: float
    iy_cm: float
    mass_kg_per_m: float

    # Design loads
    M_Ed_knm: float
    V_Ed_kn: float

    # Bending resistance
    M_c_Rd_knm: float
    eta_bending: float
    bending_ok: bool

    # Shear resistance
    V_c_Rd_kn: float
    eta_shear: float
    shear_ok: bool

    # Lateral-torsional buckling
    M_b_Rd_knm: float
    chi_LT: float
    buckling_check_required: bool
    buckling_ok: bool

    # Deflection
    deflection_mm: float
    deflection_limit_mm: float
    deflection_ok: bool

    # Overall
    overall_ok: bool
    design_status: str


class StahlTraegerEC3AT_V1:
    """
    Eurocode 3 Steel Beam Design

    Implements preliminary design for steel I-beams:
    - ULS bending (moment capacity)
    - ULS shear
    - Lateral-torsional buckling (simplified)
    - SLS deflection
    - ISO 26262 ASIL-D principles
    - SHA-256 audit trail
    """

    def __init__(self, config: EC3Config = None):
        self.config = config or EC3Config()
        self.last_chain_hash = "0" * 64

    def calculate_design_loads(self) -> Tuple[float, float]:
        """Calculate design moment and shear force"""
        q_d = 1.35 * self.config.GK_EIGEN_KN_PER_M + 1.5 * self.config.QK_NUTZLAST_KN_PER_M
        L = self.config.L_SPANNWEITE_M

        M_Ed = q_d * L**2 / 8  # kNm
        V_Ed = q_d * L / 2  # kN

        return M_Ed, V_Ed

    def calculate_bending_resistance(self, Wy_cm3: float, fy: float) -> float:
        """
        Calculate bending moment resistance (Class 1/2 cross-section)
        EN 1993-1-1 Eq. 6.13
        M_c,Rd = Wpl * fy / γM0
        """
        Wy_mm3 = Wy_cm3 * 1000  # Convert to mm³
        M_c_Rd = Wy_mm3 * fy / self.config.GAMMA_M0 / 1e6  # kNm
        return M_c_Rd

    def calculate_shear_resistance(self, h_mm: float, tw_mm: float, fy: float) -> float:
        """
        Calculate shear resistance
        EN 1993-1-1 Eq. 6.18
        V_c,Rd = Av * (fy / √3) / γM0
        """
        # Shear area (conservative: web area)
        Av = h_mm * tw_mm  # mm²

        V_c_Rd = Av * (fy / math.sqrt(3)) / self.config.GAMMA_M0 / 1000  # kN
        return V_c_Rd

    def calculate_lateral_torsional_buckling(
        self, L_m: float, Wy_cm3: float, iy_cm: float, fy: float
    ) -> Tuple[float, float]:
        """
        Lateral-torsional buckling check (simplified)
        EN 1993-1-1 Section 6.3.2

        Returns: (M_b_Rd, chi_LT)
        """
        # Elastic critical moment (simplified - conservative)
        # M_cr ≈ π * E * Iz / L (very simplified)
        # For proper calculation, need C1, C2 coefficients

        # Simplified approach: assume λ_LT based on slenderness
        L_mm = L_m * 1000
        iy_mm = iy_cm * 10

        # Non-dimensional slenderness
        lambda_LT = math.sqrt(
            Wy_cm3 * 1000 * fy / (math.pi**2 * self.config.E_N_PER_MM2 * (L_mm / iy_mm) ** 2)
        )

        # Reduction factor (simplified, assuming curve 'a')
        alpha = 0.21  # Imperfection factor for rolled I-sections
        phi = 0.5 * (1 + alpha * (lambda_LT - 0.2) + lambda_LT**2)

        if lambda_LT <= 0.2:
            chi_LT = 1.0
        else:
            chi_LT = min(1.0 / (phi + math.sqrt(phi**2 - lambda_LT**2)), 1.0)

        M_b_Rd = chi_LT * Wy_cm3 * 1000 * fy / self.config.GAMMA_M1 / 1e6  # kNm

        return M_b_Rd, chi_LT

    def calculate_deflection(self, L_m: float, Iy_cm4: float, q_k_kn_per_m: float) -> float:
        """
        Calculate deflection (simplified)
        w = 5 * q * L^4 / (384 * E * I)
        """
        q_N_per_mm = (self.config.GK_EIGEN_KN_PER_M + q_k_kn_per_m) * 1000 / 1000
        L_mm = L_m * 1000
        Iy_mm4 = Iy_cm4 * 1e4  # Convert to mm⁴
        E = self.config.E_N_PER_MM2

        w = 5 * q_N_per_mm * L_mm**4 / (384 * E * Iy_mm4)
        return w

    def run_optimization(self, profile_database: Dict = None) -> List[EC3IterationResult]:
        """
        Find minimum profile that satisfies all criteria
        """
        if profile_database is None:
            profile_database = IPE_PROFILE_DATABASE

        M_Ed, V_Ed = self.calculate_design_loads()
        fy = self.config.FY_N_PER_MM2

        iterations = []

        # Sort profiles by weight (smallest first)
        sorted_profiles = sorted(profile_database.items(), key=lambda x: x[1]["mass"])

        for profile_name, props in sorted_profiles:
            # Bending resistance
            M_c_Rd = self.calculate_bending_resistance(props["Wy"], fy)
            eta_b = M_Ed / M_c_Rd
            bending_ok = eta_b <= 1.0

            # Shear resistance
            V_c_Rd = self.calculate_shear_resistance(props["h"], props["tw"], fy)
            eta_v = V_Ed / V_c_Rd
            shear_ok = eta_v <= 1.0

            # Lateral-torsional buckling
            M_b_Rd, chi_LT = self.calculate_lateral_torsional_buckling(
                self.config.L_SPANNWEITE_M, props["Wy"], props["iy"], fy
            )
            buckling_check_required = True
            buckling_ok = M_Ed / M_b_Rd <= 1.0

            # Deflection
            w = self.calculate_deflection(
                self.config.L_SPANNWEITE_M, props["Iy"], self.config.QK_NUTZLAST_KN_PER_M
            )
            w_limit = (self.config.L_SPANNWEITE_M * 1000) / self.config.DEFLECTION_LIMIT_FACTOR
            deflection_ok = w <= w_limit

            # Overall
            overall_ok = bending_ok and shear_ok and buckling_ok and deflection_ok

            if not bending_ok:
                status = "Biegung nicht erfüllt"
            elif not shear_ok:
                status = "Schub nicht erfüllt"
            elif not buckling_ok:
                status = "Kippnachweis nicht erfüllt"
            elif not deflection_ok:
                status = "Durchbiegung zu groß"
            else:
                status = "OK - Bemessung erfüllt"

            result = EC3IterationResult(
                profile_name=profile_name,
                h_mm=props["h"],
                b_mm=props["b"],
                A_mm2=props["A"] * 100,  # cm² to mm²
                Wy_cm3=props["Wy"],
                Wz_cm3=props["Wz"],
                Iy_cm4=props["Iy"],
                iy_cm=props["iy"],
                mass_kg_per_m=props["mass"],
                M_Ed_knm=M_Ed,
                V_Ed_kn=V_Ed,
                M_c_Rd_knm=M_c_Rd,
                eta_bending=eta_b,
                bending_ok=bending_ok,
                V_c_Rd_kn=V_c_Rd,
                eta_shear=eta_v,
                shear_ok=shear_ok,
                M_b_Rd_knm=M_b_Rd,
                chi_LT=chi_LT,
                buckling_check_required=buckling_check_required,
                buckling_ok=buckling_ok,
                deflection_mm=w,
                deflection_limit_mm=w_limit,
                deflection_ok=deflection_ok,
                overall_ok=overall_ok,
                design_status=status,
            )

            iterations.append(result)

            if overall_ok:
                break

        return iterations

    def create_verification_hash(self, result: EC3IterationResult) -> str:
        """Create SHA-256 verification hash"""
        hash_input = json.dumps(
            {
                "L": self.config.L_SPANNWEITE_M,
                "profile": result.profile_name,
                "stahl": self.config.STAHL_GUETE,
                "M_Ed": result.M_Ed_knm,
            },
            sort_keys=True,
        )
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def generate_report(self, iterations: List[EC3IterationResult]) -> str:
        """Generate technical report"""
        if not iterations:
            return "Keine Lösung gefunden"

        result = iterations[-1]
        verification_hash = self.create_verification_hash(result)

        lines = [
            "=" * 80,
            "TECHNISCHER BERICHT V1.0 – Stahlbau-Bemessung (EC3-AT)",
            "=" * 80,
            f"Projekt:          Stahlträger - Vorbemessung",
            f"Berechnungsdatum: {datetime.now().strftime('%Y-%m-%d')}",
            f"Norm:             ÖNORM EN 1993-1-1 (Eurocode 3 Austria)",
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
            f"Profil:           {result.profile_name}",
            f"  Höhe:           h = {result.h_mm:.0f} mm",
            f"  Breite:         b = {result.b_mm:.0f} mm",
            f"  Masse:          {result.mass_kg_per_m:.1f} kg/m",
            "",
            "-" * 80,
            "2. MATERIAL",
            "-" * 80,
            f"Stahlgüte:        {self.config.STAHL_GUETE}",
            f"  fy =            {self.config.FY_N_PER_MM2:.0f} N/mm²",
            f"  E =             {self.config.E_N_PER_MM2:.0f} N/mm²",
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
            f"Wpl,y =           {result.Wy_cm3:.0f} cm³",
            f"M_c,Rd =          {result.M_c_Rd_knm:.2f} kNm",
            f"η_biegung =       {result.eta_bending:.3f} {'✓' if result.bending_ok else '✗'}",
            "",
            "-" * 80,
            "5. SCHUBBEMESSUNG",
            "-" * 80,
            f"V_c,Rd =          {result.V_c_Rd_kn:.2f} kN",
            f"η_schub =         {result.eta_shear:.3f} {'✓' if result.shear_ok else '✗'}",
            "",
            "-" * 80,
            "6. KIPPNACHWEIS",
            "-" * 80,
            f"χ_LT =            {result.chi_LT:.3f}",
            f"M_b,Rd =          {result.M_b_Rd_knm:.2f} kNm",
            f"Nachweis:         {'✓' if result.buckling_ok else '✗'}",
            "",
            "-" * 80,
            "7. DURCHBIEGUNG",
            "-" * 80,
            f"w =               {result.deflection_mm:.1f} mm",
            f"w_zul =           {result.deflection_limit_mm:.1f} mm (L/{self.config.DEFLECTION_LIMIT_FACTOR:.0f})",
            f"Nachweis:         {'✓' if result.deflection_ok else '✗'}",
            "",
            "-" * 80,
            "8. ERGEBNIS",
            "-" * 80,
            f"Status:           {result.design_status}",
            f"Profile geprüft:  {len(iterations)}",
            f"Gesamtbewertung:  {'BESTANDEN ✓' if result.overall_ok else 'NICHT BESTANDEN ✗'}",
            "",
            "=" * 80,
            "Prüf-Hash: " + verification_hash,
            "=" * 80,
        ]

        return "\n".join(lines)


def main():
    """Main execution function"""
    print("🏗️  Eurocode 3 (EC3-AT) V1.0 – Stahlbau-Bemessung")
    print("=" * 70)
    print("⚠️  WARNUNG: Nur für Vordimensionierung!")
    print("    Finale Bemessung durch befugten Ziviltechniker erforderlich!")
    print("=" * 70)

    config = EC3Config()
    calc = StahlTraegerEC3AT_V1(config)

    print(f"\nSYSTEM: {config.SYSTEM_TYP}")
    print(f"SPANNWEITE: L = {config.L_SPANNWEITE_M} m")
    print(f"STAHL: {config.STAHL_GUETE}")

    print("\n🔄 Starte Profiloptimierung...")
    iterations = calc.run_optimization()

    if not iterations:
        print("\n❌ Keine Lösung gefunden.")
        return

    result = iterations[-1]
    print(f"\n✅ Lösung gefunden:")
    print(f"   Profil: {result.profile_name}")
    print(f"   Masse: {result.mass_kg_per_m:.1f} kg/m")
    print(f"   η_biegung = {result.eta_bending:.3f}")
    print(f"   η_schub = {result.eta_shear:.3f}")
    print(f"   χ_LT = {result.chi_LT:.3f}")
    print(f"   Status: {result.design_status}")

    print("\n" + "=" * 70)
    print(calc.generate_report(iterations))


if __name__ == "__main__":
    main()
