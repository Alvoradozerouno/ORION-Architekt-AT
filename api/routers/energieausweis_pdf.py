"""
Energieausweis PDF-Export
Erstellt einen österreichischen Energieausweis als druckfähiges PDF.
Layout nach OIB-RL 6:2023 / ÖNORM EN 15217.
Benötigt: reportlab>=4.0.0
"""

import io
from datetime import date
from typing import List, Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

router = APIRouter()


# ─── Farbdefinitionen Energieklassen (RGB 0–1) ───────────────────────────────

_KLASSEN_FARBEN = {
    "A++": (0.00, 0.53, 0.20),   # Dunkelgrün
    "A+":  (0.13, 0.69, 0.30),
    "A":   (0.40, 0.78, 0.25),
    "B":   (0.69, 0.87, 0.18),
    "C":   (1.00, 0.85, 0.00),   # Gelb
    "D":   (1.00, 0.60, 0.00),   # Orange
    "E":   (0.93, 0.38, 0.10),
    "F":   (0.82, 0.18, 0.08),
    "G":   (0.65, 0.04, 0.04),   # Dunkelrot
}

_KLASSEN_LISTE = ["A++", "A+", "A", "B", "C", "D", "E", "F", "G"]

_KLASSE_RANG = {k: i for i, k in enumerate(_KLASSEN_LISTE)}


def _hwb_zu_klasse(hwb: float) -> str:
    if hwb <= 10:   return "A++"
    if hwb <= 25:   return "A+"
    if hwb <= 50:   return "A"
    if hwb <= 75:   return "B"
    if hwb <= 100:  return "C"
    if hwb <= 150:  return "D"
    if hwb <= 200:  return "E"
    if hwb <= 250:  return "F"
    return "G"


# ─── Request Model ────────────────────────────────────────────────────────────


class EnergyAusweisPDFRequest(BaseModel):
    # Gebäudedaten
    projektname: str = Field("Mein Projekt", min_length=1, max_length=100)
    adresse: str = Field("", max_length=200)
    bundesland: str = Field("Tirol", max_length=50)
    gebaudetyp: str = Field("Mehrfamilienhaus", max_length=100)
    bgf_m2: float = Field(..., gt=0, description="Bruttogeschossfläche m²")
    baujahr: Optional[int] = Field(None, ge=1800, le=2030)
    bauherr: str = Field("", max_length=100)

    # Energiedaten
    hwb_kwh_m2a: float = Field(..., gt=0, description="Heizwärmebedarf kWh/m²a")
    heb_kwh_m2a: Optional[float] = Field(None, gt=0, description="Heizenergiebedarf kWh/m²a")
    peb_kwh_m2a: Optional[float] = Field(None, gt=0, description="Primärenergiebedarf kWh/m²a")
    co2_kg_m2a: Optional[float] = Field(None, ge=0, description="CO₂-Emissionen kg/m²a")
    fgee: Optional[float] = Field(None, gt=0, description="Gesamtenergieeffizienz-Faktor")

    # U-Werte (optional)
    u_wert_aussenwand: Optional[float] = Field(None, gt=0)
    u_wert_dach: Optional[float] = Field(None, gt=0)
    u_wert_fenster: Optional[float] = Field(None, gt=0)
    u_wert_boden: Optional[float] = Field(None, gt=0)

    # Heizung / Technik
    heizungstyp: str = Field("Wärmepumpe", max_length=100)
    warmwasser: str = Field("Solar", max_length=100)
    belueftung: str = Field("Kontrollierte Wohnraumlüftung", max_length=100)

    # Aussteller
    aussteller_name: str = Field("ORION Architekt-AT", max_length=100)
    aussteller_zahl: str = Field("", max_length=50, description="ZT-Kammer Mitglieds-Nr.")
    ausstellungsdatum: Optional[str] = Field(None, description="YYYY-MM-DD")


# ─── PDF-Generierung ──────────────────────────────────────────────────────────


def _build_pdf(req: EnergyAusweisPDFRequest) -> bytes:
    """Erstellt das Energieausweis-PDF und gibt es als bytes zurück."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm, mm
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError as exc:
        raise RuntimeError(
            "reportlab ist nicht installiert. Bitte 'pip install reportlab>=4.0.0' ausführen."
        ) from exc

    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)
    W, H = A4  # 595 × 842 pt

    energieklasse = _hwb_zu_klasse(req.hwb_kwh_m2a)
    fgee_konform = req.fgee is not None and req.fgee <= 0.75

    # ── Kopfzeile ────────────────────────────────────────────────────────────
    c.setFillColorRGB(0.15, 0.35, 0.70)
    c.rect(0, H - 55, W, 55, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1.5 * cm, H - 30, "ENERGIEAUSWEIS")
    c.setFont("Helvetica", 10)
    c.drawString(1.5 * cm, H - 46, "nach OIB-Richtlinie 6:2023 / ÖNORM EN 15217")
    # Rechts: Datum
    ausstellungsdatum = req.ausstellungsdatum or date.today().isoformat()
    c.setFont("Helvetica", 9)
    c.drawRightString(W - 1.5 * cm, H - 38, f"Ausstellungsdatum: {ausstellungsdatum}")

    # ── Gebäudedaten-Box ──────────────────────────────────────────────────────
    y = H - 75
    c.setFillColorRGB(0.93, 0.96, 1.0)
    c.rect(1 * cm, y - 65, W - 2 * cm, 65, fill=1, stroke=0)
    c.setStrokeColorRGB(0.7, 0.8, 0.9)
    c.rect(1 * cm, y - 65, W - 2 * cm, 65, fill=0, stroke=1)

    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1.5 * cm, y - 12, req.projektname)
    c.setFont("Helvetica", 9)
    line2 = req.adresse + (f"  |  {req.bundesland}" if req.adresse else req.bundesland)
    c.drawString(1.5 * cm, y - 25, line2)
    c.drawString(1.5 * cm, y - 38, f"Gebäudetyp: {req.gebaudetyp}   |   BGF: {req.bgf_m2:.0f} m²"
                 + (f"   |   Baujahr: {req.baujahr}" if req.baujahr else ""))
    c.drawString(1.5 * cm, y - 51, f"Bauherr/Eigentümer: {req.bauherr or '—'}")
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(1.5 * cm, y - 62, f"Aussteller: {req.aussteller_name}"
                 + (f"  |  ZT-Nr.: {req.aussteller_zahl}" if req.aussteller_zahl else ""))

    # ── Energieklassen-Skala ──────────────────────────────────────────────────
    skala_x = 1.2 * cm
    skala_y = H - 195
    skala_h = 22
    skala_w_basis = 3.5 * cm
    skala_abstand = 1

    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.drawString(skala_x, skala_y + len(_KLASSEN_LISTE) * (skala_h + skala_abstand) + 8,
                 "Energieklasse")

    ziel_rang = _KLASSE_RANG.get(energieklasse, 8)

    for i, klasse in enumerate(_KLASSEN_LISTE):
        r_col, g_col, b_col = _KLASSEN_FARBEN[klasse]
        breite = skala_w_basis + (len(_KLASSEN_LISTE) - i) * 0.35 * cm  # Pfeilform
        box_y = skala_y + (len(_KLASSEN_LISTE) - 1 - i) * (skala_h + skala_abstand)

        # Pfeilform (Trapez)
        p = c.beginPath()
        pfeil_spitze = 8
        p.moveTo(skala_x, box_y)
        p.lineTo(skala_x + breite, box_y)
        p.lineTo(skala_x + breite + pfeil_spitze, box_y + skala_h / 2)
        p.lineTo(skala_x + breite, box_y + skala_h)
        p.lineTo(skala_x, box_y + skala_h)
        p.close()
        c.setFillColorRGB(r_col, g_col, b_col)
        c.drawPath(p, fill=1, stroke=0)

        # Klassen-Label
        c.setFillColorRGB(1, 1, 1) if i < 4 else c.setFillColorRGB(0.1, 0.1, 0.1)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(skala_x + 6, box_y + 6, klasse)

        # HWB-Grenzwert
        grenzwerte = {
            "A++": "≤ 10", "A+": "≤ 25", "A": "≤ 50", "B": "≤ 75",
            "C": "≤ 100", "D": "≤ 150", "E": "≤ 200", "F": "≤ 250", "G": "> 250"
        }
        c.setFont("Helvetica", 7)
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.drawString(skala_x + breite + pfeil_spitze + 4, box_y + 6,
                     f"{grenzwerte[klasse]} kWh/m²a")

        # Markierungspfeil für aktuelle Klasse
        if i == ziel_rang:
            pfeil_x = skala_x + breite + pfeil_spitze + 45
            c.setFillColorRGB(0.15, 0.35, 0.70)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(pfeil_x, box_y + 6, f"◄  {req.hwb_kwh_m2a:.1f} kWh/m²a")

    # ── Energiekennzahlen Box (rechts) ────────────────────────────────────────
    kenn_x = 10.5 * cm
    kenn_y = H - 195
    kenn_w = W - kenn_x - 1.2 * cm
    kenn_h = len(_KLASSEN_LISTE) * (skala_h + skala_abstand) + 20

    c.setFillColorRGB(0.97, 0.97, 0.97)
    c.rect(kenn_x, kenn_y, kenn_w, kenn_h, fill=1, stroke=0)
    c.setStrokeColorRGB(0.80, 0.80, 0.80)
    c.rect(kenn_x, kenn_y, kenn_w, kenn_h, fill=0, stroke=1)

    # Große Energieklassen-Anzeige
    r_col, g_col, b_col = _KLASSEN_FARBEN[energieklasse]
    c.setFillColorRGB(r_col, g_col, b_col)
    c.rect(kenn_x + 5, kenn_y + kenn_h - 52, kenn_w - 10, 45, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1) if ziel_rang < 4 else c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(kenn_x + kenn_w / 2, kenn_y + kenn_h - 37, energieklasse)
    c.setFont("Helvetica", 8)
    c.drawCentredString(kenn_x + kenn_w / 2, kenn_y + kenn_h - 57, "Energieklasse")

    # Kennzahlen-Tabelle
    zeilen = [
        ("HWB", f"{req.hwb_kwh_m2a:.1f}", "kWh/m²a", "Heizwärmebedarf"),
    ]
    if req.heb_kwh_m2a:
        zeilen.append(("HEB", f"{req.heb_kwh_m2a:.1f}", "kWh/m²a", "Heizenergiebedarf"))
    if req.peb_kwh_m2a:
        zeilen.append(("PEB", f"{req.peb_kwh_m2a:.1f}", "kWh/m²a", "Primärenergiebedarf"))
    if req.co2_kg_m2a is not None:
        zeilen.append(("CO₂", f"{req.co2_kg_m2a:.1f}", "kg/m²a", "CO₂-Emissionen"))
    if req.fgee is not None:
        konform_str = " ✓" if fgee_konform else " ✗"
        zeilen.append(("fGEE", f"{req.fgee:.2f}{konform_str}", "", "Gesamtenerg.-faktor (≤0,75)"))

    row_h = 18
    for j, (kuerzel, wert, einheit, bezeichnung) in enumerate(zeilen):
        ry = kenn_y + kenn_h - 75 - j * row_h
        if j % 2 == 0:
            c.setFillColorRGB(0.93, 0.93, 0.93)
            c.rect(kenn_x + 5, ry - 3, kenn_w - 10, row_h, fill=1, stroke=0)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(kenn_x + 8, ry + 3, kuerzel)
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(kenn_x + kenn_w - 8, ry + 4, wert)
        c.setFont("Helvetica", 7)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(kenn_x + 8, ry - 5, bezeichnung)

    # ── Gebäudetechnik ────────────────────────────────────────────────────────
    tech_y = kenn_y - 25
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0.15, 0.35, 0.70)
    c.drawString(skala_x, tech_y, "Gebäudetechnik")
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.1, 0.1, 0.1)
    techzeilen = [
        f"Heizung: {req.heizungstyp}",
        f"Warmwasser: {req.warmwasser}",
        f"Lüftung: {req.belueftung}",
    ]
    for j, z in enumerate(techzeilen):
        c.drawString(skala_x, tech_y - 14 - j * 13, z)

    # ── U-Werte ───────────────────────────────────────────────────────────────
    if any([req.u_wert_aussenwand, req.u_wert_dach, req.u_wert_fenster, req.u_wert_boden]):
        u_x = kenn_x
        u_y = tech_y
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0.15, 0.35, 0.70)
        c.drawString(u_x, u_y, "U-Werte [W/m²K]")
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        u_werte = []
        if req.u_wert_aussenwand:
            oib_ok = req.u_wert_aussenwand <= 0.25
            u_werte.append(f"Außenwand: {req.u_wert_aussenwand:.3f}" + (" ✓" if oib_ok else " ✗"))
        if req.u_wert_dach:
            oib_ok = req.u_wert_dach <= 0.15
            u_werte.append(f"Dach/Decke: {req.u_wert_dach:.3f}" + (" ✓" if oib_ok else " ✗"))
        if req.u_wert_fenster:
            oib_ok = req.u_wert_fenster <= 1.0
            u_werte.append(f"Fenster: {req.u_wert_fenster:.3f}" + (" ✓" if oib_ok else " ✗"))
        if req.u_wert_boden:
            oib_ok = req.u_wert_boden <= 0.35
            u_werte.append(f"Bodenplatte: {req.u_wert_boden:.3f}" + (" ✓" if oib_ok else " ✗"))
        for j, z in enumerate(u_werte):
            c.drawString(u_x, u_y - 14 - j * 13, z)

    # ── OIB Konformitäts-Banner ───────────────────────────────────────────────
    banner_y = 3.5 * cm
    oib_konform = ziel_rang <= 3 and (req.fgee is None or fgee_konform)
    if oib_konform:
        c.setFillColorRGB(0.13, 0.69, 0.30)
    else:
        c.setFillColorRGB(0.82, 0.18, 0.08)
    c.rect(1 * cm, banner_y, W - 2 * cm, 20, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 9)
    status_text = (
        "✓ OIB-RL 6:2023 KONFORM — Neubau-Anforderungen erfüllt"
        if oib_konform
        else "✗ OIB-RL 6:2023 — Neubau-Anforderungen NICHT erfüllt (Energieklasse schlechter als B)"
    )
    c.drawCentredString(W / 2, banner_y + 6, status_text)

    # ── Fußzeile ──────────────────────────────────────────────────────────────
    c.setFillColorRGB(0.93, 0.93, 0.93)
    c.rect(0, 0, W, 2.8 * cm, fill=1, stroke=0)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.setFont("Helvetica", 7.5)
    footer1 = (
        "Dieser Energieausweis wurde automatisch erstellt von ORION Architekt-AT (⊘∞⧈∞⊘). "
        "Rechtlich verbindliche Energieausweise müssen von befugten Fachleuten (ZT, Ingenieur) ausgestellt werden."
    )
    footer2 = (
        "OIB-RL 6:2023 | HWBmax = 10 + 30×(A/V) kWh/m²a | fGEE ≤ 0,75 (Neubau) | "
        f"Bundesland: {req.bundesland} | Aussteller: {req.aussteller_name}"
    )
    c.drawCentredString(W / 2, 1.8 * cm, footer1)
    c.drawCentredString(W / 2, 1.1 * cm, footer2)

    c.save()
    buf.seek(0)
    return buf.read()


# ─── Endpoint ─────────────────────────────────────────────────────────────────


@router.post("/pdf")
async def erstelle_energieausweis_pdf(req: EnergyAusweisPDFRequest):
    """
    📄 **Energieausweis PDF**

    Erstellt einen druckfähigen österreichischen Energieausweis als PDF-Datei.

    **Layout nach OIB-RL 6:2023:**
    - Farbige Energieklassen-Skala (A++ bis G) mit Pfeil-Markierung
    - Kennwerte: HWB, HEB, PEB, CO₂, fGEE
    - U-Wert Tabelle mit OIB-Grenzwert-Check
    - Gebäudetechnik-Übersicht
    - OIB-Konformitäts-Banner
    - Professionelle Fußzeile mit Aussteller-Info

    **Antwort:** PDF-Datei als Download
    """
    pdf_bytes = _build_pdf(req)
    safe_name = req.projektname.replace(" ", "_").replace("/", "-")[:40]
    filename = f"Energieausweis_{safe_name}_{date.today().isoformat()}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
