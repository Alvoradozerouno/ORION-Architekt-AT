#!/usr/bin/env python3
"""
=============================================================================
EUROCODE 8 (EC8-AT) V1.0 – ERDBEBEN-BEMESSUNG
=============================================================================
ÖNORM EN 1998-1 (Eurocode 8 Austria) – Seismische Bemessung

Autoren: Elisabeth Steurer & Gerhard Hirschmann
Datum: 2026-04-07
Ort: Almdorf 9, St. Johann in Tirol, Austria
Lizenz: Apache 2.0

⚠️  WARNUNG: Nur für Vordimensionierung!
    Finale Bemessung durch befugten Ziviltechniker erforderlich!

NORMEN:
- ÖNORM EN 1998-1: Eurocode 8 - Erdbeben
- ÖNORM B 1998-1: Österreichischer Nationaler Anhang

TRL (Technology Readiness Level): 4 (Laboratory Validation)
ISO 26262 ASIL-D Prinzipien für deterministische Berechnung

SCOPE (MVP):
- Horizontale Ersatzkraft für regelmäßige Gebäude
- Österreichische Erdbebenzonen
- Antwortspektrum (vereinfacht)
- Verhaltensbeiwert für Bauwerkstypen

NICHT SCOPE (Future):
- Vollständige modale Analyse
- Irreguläre Gebäude
- Bodeneigenschaften-Interaktion (detailliert)
- Zeitverlaufsberechnung
=============================================================================
"""

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# =============================================================================
# ÖSTERREICHISCHE ERDBEBENZONEN (ÖNORM B 1998-1)
# =============================================================================

ERDBEBENZONEN_AT = {
    "WIEN": {
        "bezeichnung": "Wien (Zone 1)",
        "ag": 0.7,  # Bemessungsgrundwert m/s² (0.7 m/s² = ~0.07g)
        "zone": 1,
    },
    "TIROL_SUED": {
        "bezeichnung": "Tirol Süd (Zone 2 - St. Johann)",
        "ag": 1.1,  # 1.1 m/s² = ~0.11g
        "zone": 2,
    },
    "KAERNTEN_SUED": {
        "bezeichnung": "Kärnten Süd (Zone 3 - höchste Gefahr)",
        "ag": 1.3,  # 1.3 m/s² = ~0.13g
        "zone": 3,
    },
    "NIEDEROESTERREICH": {
        "bezeichnung": "Niederösterreich (Zone 1)",
        "ag": 0.7,
        "zone": 1,
    },
    "VORARLBERG": {
        "bezeichnung": "Vorarlberg (Zone 0 - sehr niedrig)",
        "ag": 0.0,  # Keine Erdbebenauslegung erforderlich
        "zone": 0,
    },
}

UNTERGRUNDKLASSEN_AT = {
    "A": {
        "bezeichnung": "Fels",
        "S": 1.0,  # Bodenparameter (EN 1998-1 Table 3.2)
    },
    "B": {
        "bezeichnung": "Sehr steife Böden",
        "S": 1.2,
    },
    "C": {
        "bezeichnung": "Steife Böden (Standard)",
        "S": 1.15,
    },
    "D": {
        "bezeichnung": "Weiche Böden",
        "S": 1.35,
    },
}

BAUWERKSTYPEN_AT = {
    "STAHLBETON_DUKTIL": {
        "bezeichnung": "Stahlbeton, hohe Duktilität (DCH)",
        "q": 5.0,  # Verhaltensbeiwert
    },
    "STAHLBETON_MITTEL": {
        "bezeichnung": "Stahlbeton, mittlere Duktilität (DCM)",
        "q": 3.0,
    },
    "STAHL_DUKTIL": {
        "bezeichnung": "Stahlbau, hohe Duktilität (DCH)",
        "q": 4.0,
    },
    "MAUERWERK_UNBEWEHRT": {
        "bezeichnung": "Unbewehrtes Mauerwerk",
        "q": 1.5,
    },
    "HOLZBAU": {
        "bezeichnung": "Holzbau (Standard)",
        "q": 2.5,
    },
}


# =============================================================================
# KONFIGURATION
# =============================================================================


@dataclass
class EC8Config:
    """Konfiguration für EC8 Erdbeben-Bemessung"""

    # Standort
    ERDBEBENZONE: str = "TIROL_SUED"  # Erdbebenzone
    UNTERGRUND: str = "C"  # Untergrundklasse

    # Gebäude
    BAUWERKSTYP: str = "STAHLBETON_MITTEL"
    GESCHOSSZAHL: int = 3
    GESCHOSSHOEHE_M: float = 3.0
    MASSE_PRO_GESCHOSS_T: float = 200.0  # Tonnen

    # Sonstige
    WICHTIGKEITSFAKTOR: float = (
        1.0  # γI (EN 1998-1 Table 4.3: 1.0=normal, 1.2=wichtig, 1.4=kritisch)
    )
    PROJEKT: str = "Erdbeben-Bemessung - Vorbemessung"

    def __post_init__(self):
        # Erdbebenzone laden
        if self.ERDBEBENZONE not in ERDBEBENZONEN_AT:
            raise ValueError(f"Unbekannte Erdbebenzone: {self.ERDBEBENZONE}")
        zone_data = ERDBEBENZONEN_AT[self.ERDBEBENZONE]
        self.AG = zone_data["ag"]  # Bemessungsgrundwert m/s²

        # Untergrund laden
        if self.UNTERGRUND not in UNTERGRUNDKLASSEN_AT:
            raise ValueError(f"Unbekannte Untergrundklasse: {self.UNTERGRUND}")
        untergrund_data = UNTERGRUNDKLASSEN_AT[self.UNTERGRUND]
        self.S = untergrund_data["S"]  # Bodenparameter

        # Bauwerkstyp laden
        if self.BAUWERKSTYP not in BAUWERKSTYPEN_AT:
            raise ValueError(f"Unbekannter Bauwerkstyp: {self.BAUWERKSTYP}")
        typ_data = BAUWERKSTYPEN_AT[self.BAUWERKSTYP]
        self.Q = typ_data["q"]  # Verhaltensbeiwert

        # Gesamtmasse
        self.GESAMTMASSE_T = self.MASSE_PRO_GESCHOSS_T * self.GESCHOSSZAHL

        # Gesamthöhe
        self.GESAMTHOEHE_M = self.GESCHOSSHOEHE_M * self.GESCHOSSZAHL


# =============================================================================
# ERGEBNISSE
# =============================================================================


@dataclass
class EC8Result:
    """Berechnungsergebnis"""

    ag_ms2: float
    S: float
    q: float
    T_s: float  # Eigenperiode
    Sd_T_ms2: float  # Spektrale Beschleunigung
    F_b_kn: float  # Basisscherkraft
    masse_t: float
    hoehe_m: float
    status: str  # INFO
    details: str


# =============================================================================
# HAUPTKLASSE: ERDBEBEN-BEMESSUNG EC8-AT
# =============================================================================


class ErdbebenEC8AT_V1:
    """
    Erdbeben-Bemessung nach EN 1998-1 (Eurocode 8 Austria)

    Funktionen:
    - Antwortspektrum berechnen (vereinfacht)
    - Eigenperiode abschätzen (Näherungsformel)
    - Basisscherkraft berechnen
    """

    def __init__(self, config: EC8Config):
        self.config = config

    def calculate_fundamental_period(self, h_m: float, bauwerkstyp: str) -> float:
        """
        Grundeigenperiode abschätzen (EN 1998-1 Eq. 4.6)

        T = Ct * H^(3/4)

        Ct:
        - Stahlbeton: 0.075
        - Stahl: 0.085
        - Mauerwerk: 0.05
        - Holz: 0.05

        Args:
            h_m: Gebäudehöhe in m
            bauwerkstyp: Bauwerkstyp-Schlüssel

        Returns:
            T in Sekunden
        """
        # Ct-Wert bestimmen
        if "STAHLBETON" in bauwerkstyp:
            Ct = 0.075
        elif "STAHL" in bauwerkstyp:
            Ct = 0.085
        elif "MAUERWERK" in bauwerkstyp:
            Ct = 0.05
        elif "HOLZBAU" in bauwerkstyp:
            Ct = 0.05
        else:
            Ct = 0.05  # Konservativ

        T = Ct * (h_m ** (3 / 4))
        return T

    def calculate_response_spectrum(
        self, T_s: float, ag_ms2: float, S: float, q: float, gamma_I: float
    ) -> float:
        """
        Bemessungsspektrum berechnen (EN 1998-1 Eq. 3.15, vereinfacht)

        Für horizontale Komponente, elastisches Spektrum:
        Se(T) = ag * S * 2.5 / q * (T_C / T)^(2/3)   für T > T_C

        Vereinfacht für MVP:
        - T_C = 0.5 s (Eckperiode, Untergrundklasse C)
        - T_B = 0.15 s
        - T_D = 2.0 s

        Sd(T) = ag * S * 2.5 / q   für T_B ≤ T ≤ T_C (Plateau)
        Sd(T) = ag * S * 2.5 / q * (T_C / T)   für T_C < T ≤ T_D (abfallend)

        Args:
            T_s: Eigenperiode in s
            ag_ms2: Bemessungsgrundwert in m/s²
            S: Bodenparameter
            q: Verhaltensbeiwert
            gamma_I: Wichtigkeitsfaktor

        Returns:
            Sd(T) in m/s²
        """
        T_B = 0.15
        T_C = 0.5
        T_D = 2.0

        # Spektralbeschleunigung
        if T_s <= T_B:
            # Ansteigender Ast
            Sd = ag_ms2 * S * gamma_I * (1 + T_s / T_B * (2.5 / q - 1))
        elif T_s <= T_C:
            # Plateau
            Sd = ag_ms2 * S * gamma_I * 2.5 / q
        elif T_s <= T_D:
            # Abfallender Ast
            Sd = ag_ms2 * S * gamma_I * 2.5 / q * (T_C / T_s)
        else:
            # Sehr lange Perioden
            Sd = ag_ms2 * S * gamma_I * 2.5 / q * (T_C * T_D / (T_s**2))

        return Sd

    def calculate_base_shear(self, Sd_ms2: float, masse_t: float) -> float:
        """
        Basisscherkraft berechnen (EN 1998-1 Eq. 4.5)

        Fb = Sd(T) * m * λ

        λ = 0.85 für T ≥ 2*T_C (für regelmäßige Gebäude mit > 2 Geschossen)
        λ = 1.0 sonst

        Args:
            Sd_ms2: Spektrale Beschleunigung in m/s²
            masse_t: Gesamtmasse in Tonnen

        Returns:
            Fb in kN
        """
        # Vereinfacht: λ = 0.85 für > 2 Geschosse
        if self.config.GESCHOSSZAHL > 2:
            lambda_val = 0.85
        else:
            lambda_val = 1.0

        masse_kg = masse_t * 1000
        F_b_n = Sd_ms2 * masse_kg * lambda_val
        F_b_kn = F_b_n / 1000
        return F_b_kn

    def run_calculation(self) -> EC8Result:
        """
        Erdbeben-Bemessung durchführen

        Returns:
            EC8Result
        """
        # 1. Eigenperiode
        T_s = self.calculate_fundamental_period(self.config.GESAMTHOEHE_M, self.config.BAUWERKSTYP)

        # 2. Spektrale Beschleunigung
        Sd_ms2 = self.calculate_response_spectrum(
            T_s,
            self.config.AG,
            self.config.S,
            self.config.Q,
            self.config.WICHTIGKEITSFAKTOR,
        )

        # 3. Basisscherkraft
        F_b_kn = self.calculate_base_shear(Sd_ms2, self.config.GESAMTMASSE_T)

        # Status
        status = "INFO"
        details = f"T={T_s:.2f}s, Sd={Sd_ms2:.2f}m/s², Fb={F_b_kn:.1f}kN"

        result = EC8Result(
            ag_ms2=self.config.AG,
            S=self.config.S,
            q=self.config.Q,
            T_s=T_s,
            Sd_T_ms2=Sd_ms2,
            F_b_kn=F_b_kn,
            masse_t=self.config.GESAMTMASSE_T,
            hoehe_m=self.config.GESAMTHOEHE_M,
            status=status,
            details=details,
        )

        return result

    def generate_report(self, result: EC8Result) -> str:
        """Technischen Bericht generieren"""
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Audit-Hash
        audit_data = {
            "projekt": self.config.PROJEKT,
            "timestamp": timestamp,
            "erdbebenzone": self.config.ERDBEBENZONE,
            "masse_t": self.config.GESAMTMASSE_T,
        }
        audit_hash = hashlib.sha256(json.dumps(audit_data, sort_keys=True).encode()).hexdigest()[
            :16
        ]

        report = f"""
{'=' * 80}
TECHNISCHER BERICHT V1.0 – Erdbeben-Bemessung (EC8-AT)
{'=' * 80}
Projekt:          {self.config.PROJEKT}
Berechnungsdatum: {datetime.utcnow().strftime('%Y-%m-%d')}
Norm:             ÖNORM EN 1998-1 (Eurocode 8 Austria)
TRL-Status:       4 (Laboratory Validation)
Version:          1.0.0 MVP
Prüf-Hash:        {audit_hash}

⚠️  WARNUNG: Nur für Vordimensionierung!
    Finale Bemessung durch befugten Ziviltechniker erforderlich!

{'-' * 80}
1. STANDORT & ERDBEBENZONE
{'-' * 80}
Zone:             {ERDBEBENZONEN_AT[self.config.ERDBEBENZONE]['bezeichnung']}
ag =              {self.config.AG:.2f} m/s² (Bemessungsgrundwert)
Untergrund:       Klasse {self.config.UNTERGRUND} ({UNTERGRUNDKLASSEN_AT[self.config.UNTERGRUND]['bezeichnung']})
S =               {self.config.S:.2f} (Bodenparameter)
γI =              {self.config.WICHTIGKEITSFAKTOR:.2f} (Wichtigkeitsfaktor)

{'-' * 80}
2. GEBÄUDEDATEN
{'-' * 80}
Bauwerkstyp:      {BAUWERKSTYPEN_AT[self.config.BAUWERKSTYP]['bezeichnung']}
q =               {self.config.Q:.1f} (Verhaltensbeiwert)
Geschosse:        {self.config.GESCHOSSZAHL}
Höhe:             H = {self.config.GESAMTHOEHE_M:.1f} m
Gesamtmasse:      m = {self.config.GESAMTMASSE_T:.0f} t

{'-' * 80}
3. EIGENPERIODE
{'-' * 80}
T =               {result.T_s:.3f} s (Grundeigenperiode, Näherungsformel)

{'-' * 80}
4. ANTWORTSPEKTRUM
{'-' * 80}
Sd(T) =           {result.Sd_T_ms2:.3f} m/s²

{'-' * 80}
5. BASISSCHERKRAFT
{'-' * 80}
Fb =              {result.F_b_kn:.1f} kN

{'-' * 80}
6. INTERPRETATION
{'-' * 80}
Die Basisscherkraft Fb ist die horizontale Ersatzkraft, die das Gebäude
bei einem Erdbeben erfährt. Diese Kraft muss von den aussteifenden Bauteilen
(Wände, Rahmen) aufgenommen werden.

Verteilung über die Höhe nach EN 1998-1 Eq. 4.11:
Fi = Fb * (mi * hi) / Σ(mi * hi)

Für detaillierte Bemessung:
- Aussteifungssystem prüfen (Wände, Rahmen)
- Torsionseffekte berücksichtigen
- Detailausbildung nach EN 1998-1 Kapitel 5

{'-' * 80}
7. ERGEBNIS
{'-' * 80}
Status:           {result.status}
Gesamtbewertung:  BERECHNUNG ABGESCHLOSSEN ✓

⚠️  HINWEISE:
- Vereinfachtes Verfahren für regelmäßige Gebäude!
- Modale Analyse für komplexe Gebäude erforderlich!
- Detailausbildung nach EN 1998-1 beachten!

{'=' * 80}
Prüf-Hash: {audit_hash}
{'=' * 80}
"""
        return report


# =============================================================================
# MAIN: Demo-Berechnung
# =============================================================================

if __name__ == "__main__":
    print("🏔️  Eurocode 8 (EC8-AT) V1.0 – Erdbeben-Bemessung")
    print("=" * 70)
    print("⚠️  WARNUNG: Nur für Vordimensionierung!")
    print("    Finale Bemessung durch befugten Ziviltechniker erforderlich!")
    print("=" * 70)
    print()

    # Standard-Konfiguration für Tirol (St. Johann)
    config = EC8Config(
        ERDBEBENZONE="TIROL_SUED",
        UNTERGRUND="C",
        BAUWERKSTYP="STAHLBETON_MITTEL",
        GESCHOSSZAHL=3,
        GESCHOSSHOEHE_M=3.0,
        MASSE_PRO_GESCHOSS_T=200.0,
        WICHTIGKEITSFAKTOR=1.0,
    )

    print(f"STANDORT: {config.ERDBEBENZONE}")
    print(f"BAUWERKSTYP: {config.BAUWERKSTYP}")
    print(f"GESCHOSSE: {config.GESCHOSSZAHL}")
    print(f"MASSE: {config.GESAMTMASSE_T} t")
    print()

    # Berechnung
    calc = ErdbebenEC8AT_V1(config)
    print("🔄 Starte Erdbeben-Berechnung...\n")
    result = calc.run_calculation()

    # Ergebnis
    print("✅ Berechnung abgeschlossen:")
    print(f"   Eigenperiode: T = {result.T_s:.3f} s")
    print(f"   Spektrale Beschleunigung: Sd(T) = {result.Sd_T_ms2:.3f} m/s²")
    print(f"   Basisscherkraft: Fb = {result.F_b_kn:.1f} kN")
    print()
    print("=" * 70)

    # Technischer Bericht
    report = calc.generate_report(result)
    print(report)
