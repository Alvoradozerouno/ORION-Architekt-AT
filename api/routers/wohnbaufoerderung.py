"""
Wohnbauförderungs-Router
Förderfähigkeits-Check für alle 9 österreichischen Bundesländer.
Stand: 2025 (offizielle Landesförderungsprogramme)
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

# ─── Förder-Datenbank Stand 2025 ────────────────────────────────────────────
# Quellen: Landesgesetzblätter, offizielle Förderseiten der Länder

_FOERDERUNG: Dict[str, Dict[str, Any]] = {
    "wien": {
        "name": "Wien",
        "programm": "Wiener Wohnbauförderung (WBF)",
        "behoerde": "MA 50 — Wohnbauförderung und Schlichtungsstelle",
        "url": "https://www.wien.gv.at/wohnen/wohnbaufoerderung/",
        "einkommensgrenze_netto_1p": 35_000,
        "einkommensgrenze_netto_2p": 52_500,
        "einkommensgrenze_netto_je_kind": 4_200,
        "einkommenstyp": "netto",
        "max_foerderung_m2_eur": 500,
        "max_wohnflaeche_m2": 150,
        "min_energieklasse": "B",
        "oeko_bonus_max_eur": 6_000,
        "foerderart": "Direktzuschuss + zinsgünstiges Darlehen",
        "besonderheiten": [
            "Mindest-Energieausweis Klasse B erforderlich",
            "Öko-Bonus bei erneuerbarer Energie: +€2.000–€6.000",
            "Barrierefreiheit-Bonus: +€3.000",
            "Freifinanzierte Wohnungen ausgeschlossen",
            "Antragsportal: Wohnservice Wien",
        ],
        "antrag_online": True,
        "antragsfrist_hinweis": "Antrag muss vor Baubeginn gestellt werden",
    },
    "niederoesterreich": {
        "name": "Niederösterreich",
        "programm": "NÖ Wohnbauförderung (WFW NÖ)",
        "behoerde": "NÖ Landesregierung — Abt. Wohnungsförderung RU3",
        "url": "https://www.noe.gv.at/noe/Wohnen/Wohnbaufoerderung.html",
        "einkommensgrenze_brutto_1p": 37_500,
        "einkommensgrenze_brutto_2p": 65_000,
        "einkommensgrenze_brutto_je_kind": 5_000,
        "einkommenstyp": "brutto",
        "max_darlehen_eur": 80_000,
        "zinssatz_prozent": 1.0,
        "laufzeit_jahre": 25,
        "min_energieklasse": "B",
        "foerderart": "Zinsgünstiges Landesdarlehen",
        "besonderheiten": [
            "Zusatzförderung für ökologische Bauweise: +€5.000–€8.000",
            "Passivhaus-Bonus: +€5.000",
            "Eigenheim und Reihenhäuser förderfähig",
            "Mindestgrundfläche 50 m²",
        ],
        "antrag_online": True,
        "antragsfrist_hinweis": "Antrag vor Rohbaufertigstellung stellen",
    },
    "oberoesterreich": {
        "name": "Oberösterreich",
        "programm": "OÖ Wohnbauförderung",
        "behoerde": "Land OÖ — Wohnbauförderungsabteilung (Direktion Soziales)",
        "url": "https://www.ooe.gv.at/themen/bauen-wohnen/wohnen/wohnbaufoerderung.html",
        "einkommensgrenze_brutto_1p": 42_500,
        "einkommensgrenze_brutto_2p": 70_000,
        "einkommensgrenze_brutto_je_kind": 5_500,
        "einkommenstyp": "brutto",
        "max_darlehen_eur": 80_000,
        "zinssatz_prozent": 0.5,
        "laufzeit_jahre": 30,
        "min_energieklasse": "B",
        "foerderart": "Zinsgünstiges Landesdarlehen",
        "besonderheiten": [
            "Öko-Sonderförderung bis €15.000 (erneuerbare Energie, Holzbau)",
            "PV-Pflicht für Neubauten ab 2024 + €3.000 Förderung",
            "Holzbau-Bonus: +€3.000",
            "Günstigster Zinssatz aller Bundesländer (0,5 %)",
            "Sanierungsförderung gesondert verfügbar",
        ],
        "antrag_online": True,
        "antragsfrist_hinweis": "Antrag vor Baubeginn; Baubewilligung ausreichend",
    },
    "salzburg": {
        "name": "Salzburg",
        "programm": "Salzburger Wohnbauförderung (WFG Sbg)",
        "behoerde": "Land Salzburg — Referat Wohnbauförderung (Abt. 10)",
        "url": "https://www.salzburg.gv.at/themen/bauen-wohnen/wohnen/wohnbaufoerderung",
        "einkommensgrenze_netto_1p": 37_000,
        "einkommensgrenze_netto_2p": 56_000,
        "einkommensgrenze_netto_je_kind": 4_000,
        "einkommenstyp": "netto",
        "max_darlehen_eur": 120_000,
        "zinssatz_prozent": 1.0,
        "laufzeit_jahre": 27,
        "min_energieklasse": "B",
        "foerderart": "Zinsgünstiges Darlehen + Direktzuschuss",
        "besonderheiten": [
            "Salzburg hat eigene WSchVO (keine OIB-RL 6!) — strengere Wärmeschutzwerte",
            "Höchstes Darlehen aller Bundesländer: bis €120.000",
            "Passivhaus-Bonus: bis €10.000",
            "Öko-Bonifikation für Holzbau, Bioziegel, Stroh u.a.",
            "Tourismusgemeinden: besondere Regelungen für Zweitwohnsitze",
        ],
        "antrag_online": True,
        "antragsfrist_hinweis": "Antrag vor Baubeginn",
    },
    "tirol": {
        "name": "Tirol",
        "programm": "Tiroler Wohnbauförderung (TWFG)",
        "behoerde": "Land Tirol — Wohnbauförderung (Abt. Wohnungswesen)",
        "url": "https://www.tirol.gv.at/bauen-wohnen/wohnbaufoerderung/",
        "einkommensgrenze_netto_1p": 33_000,
        "einkommensgrenze_netto_2p": 50_000,
        "einkommensgrenze_netto_je_kind": 3_800,
        "einkommenstyp": "netto",
        "max_darlehen_eur": 90_000,
        "zinssatz_prozent": 1.5,
        "laufzeit_jahre": 25,
        "oeko_bonus_max_eur": 18_000,
        "min_energieklasse": "B",
        "foerderart": "Zinsgünstiges Darlehen + Öko-Bonus",
        "besonderheiten": [
            "Strengste Einkommensgrenzen in AT (stark sozial orientiert)",
            "Öko-Sonderförderung bis €18.000 (höchster Ökbonus AT)",
            "Passivhaus oder Niedrigenergiebonus: +€5.000",
            "TROG (Tiroler Raumordnungsgesetz) Stellplatzregeln beachten",
            "Lawinenschutz- und Hochwasserschutzanforderungen prüfen",
        ],
        "antrag_online": True,
        "antragsfrist_hinweis": "Antrag innerhalb von 6 Monaten nach Baubewilligung",
    },
    "vorarlberg": {
        "name": "Vorarlberg",
        "programm": "Vorarlberger Wohnbauförderung",
        "behoerde": "Land Vorarlberg — Wohnbauförderung (Abt. VIId)",
        "url": "https://www.vorarlberg.at/vorarlberg/bauen_wohnen/wohnen/wohnbaufoerderung/",
        "einkommensgrenze_netto_1p": 38_500,
        "einkommensgrenze_netto_2p": 58_000,
        "einkommensgrenze_netto_je_kind": 4_500,
        "einkommenstyp": "netto",
        "max_darlehen_eur": 60_000,
        "zinssatz_prozent": 1.0,
        "laufzeit_jahre": 20,
        "min_energieklasse": "B",
        "foerderart": "Zinsgünstiges Darlehen",
        "besonderheiten": [
            "Ökobeitrag für besonders nachhaltige Bauweise (Montafon-Standard)",
            "Gemeinschaftsräume für Mehrfamilienhäuser förderbar",
            "Stark auf Klimaschutzziele Vorarlbergs ausgerichtet",
        ],
        "antrag_online": True,
        "antragsfrist_hinweis": "Antrag vor Baubeginn",
    },
    "steiermark": {
        "name": "Steiermark",
        "programm": "Steirische Wohnbauförderung (WBF Stmk)",
        "behoerde": "Land Steiermark — Wohnbauförderung (Abt. 11)",
        "url": "https://www.wohnbaufoerderung.steiermark.at/",
        "einkommensgrenze_netto_1p": 37_500,
        "einkommensgrenze_netto_2p": 56_000,
        "einkommensgrenze_netto_je_kind": 4_000,
        "einkommenstyp": "netto",
        "max_darlehen_eur": 75_000,
        "zinssatz_prozent": 1.0,
        "laufzeit_jahre": 25,
        "min_energieklasse": "B",
        "foerderart": "Zinsgünstiges Darlehen + Direktzuschuss",
        "besonderheiten": [
            "Graz-spezifische Regelungen für dichte Bebauung",
            "Sanierungsbonus besonders attraktiv (thermische Sanierung)",
            "Ökologischer Bonus für Holzbau und Bioziegel",
        ],
        "antrag_online": True,
        "antragsfrist_hinweis": "Antrag vor Baubewilligung empfohlen",
    },
    "kaernten": {
        "name": "Kärnten",
        "programm": "Kärntner Wohnbauförderung (K-WFG)",
        "behoerde": "Land Kärnten — Abt. 12 Wohnbauförderung",
        "url": "https://www.ktn.gv.at/Service/Formulare-und-Leistungen/Wohnbaufoerderung",
        "einkommensgrenze_netto_1p": 35_000,
        "einkommensgrenze_netto_2p": 52_500,
        "einkommensgrenze_netto_je_kind": 4_000,
        "einkommenstyp": "netto",
        "max_darlehen_eur": 60_000,
        "zinssatz_prozent": 1.0,
        "laufzeit_jahre": 25,
        "min_energieklasse": "B",
        "foerderart": "Zinsgünstiges Darlehen",
        "besonderheiten": [
            "Seeufergrundstücke: besondere Bau- und Naturschutzregelungen",
            "Ferienwohnungen und Zweitwohnsitz NICHT förderfähig",
            "Antrag persönlich oder per Post bei Bezirksverwaltungsbehörde",
        ],
        "antrag_online": False,
        "antragsfrist_hinweis": "Antrag persönlich bei Bezirksverwaltungsbehörde einreichen",
    },
    "burgenland": {
        "name": "Burgenland",
        "programm": "Burgenländische Wohnbauförderung (Bgld WBF)",
        "behoerde": "Land Burgenland — Wohnbauförderung",
        "url": "https://www.burgenland.at/themen/bauen-wohnen/wohnbaufoerderung/",
        "einkommensgrenze_brutto_1p": 40_500,
        "einkommensgrenze_brutto_2p": 68_000,
        "einkommensgrenze_brutto_je_kind": 5_000,
        "einkommenstyp": "brutto",
        "max_darlehen_eur": 50_000,
        "zinssatz_prozent": 1.5,
        "laufzeit_jahre": 25,
        "min_energieklasse": "B",
        "foerderart": "Zinsgünstiges Darlehen",
        "besonderheiten": [
            "Günstigste Grundstückspreise in AT",
            "Esterhazy-Gebiet: besondere Grundstücks- und Baurechtsregelungen",
            "Energiebonus für thermische Solaranlage und PV",
        ],
        "antrag_online": True,
        "antragsfrist_hinweis": "Antrag vor Baubeginn",
    },
}

# Energieklassen-Rangfolge (A++ = bestes)
_KLASSE_RANG = {"A++": 0, "A+": 1, "A": 2, "B": 3, "C": 4, "D": 5, "E": 6, "F": 7, "G": 8}


def _normalize_bundesland(bl: str) -> str:
    """Normalisiert Bundesland-Bezeichnungen auf interne Schlüssel."""
    bl = bl.lower().strip()
    mapping = {
        "nö": "niederoesterreich",
        "niederösterreich": "niederoesterreich",
        "oö": "oberoesterreich",
        "oberösterreich": "oberoesterreich",
        "vbg": "vorarlberg",
        "ktn": "kaernten",
        "kärnten": "kaernten",
        "stmk": "steiermark",
        "bgld": "burgenland",
        "sbg": "salzburg",
    }
    return mapping.get(bl, bl)


def _energieklasse_ok(klasse: str, mindest: str) -> bool:
    """Prüft ob die Energieklasse die Mindestanforderung erfüllt."""
    rang_klasse = _KLASSE_RANG.get(klasse.upper(), 9)
    rang_mindest = _KLASSE_RANG.get(mindest.upper(), 9)
    return rang_klasse <= rang_mindest


# ─── Request / Response Models ────────────────────────────────────────────────


class FoerderCheckRequest(BaseModel):
    bundesland: str = Field(..., description="Österreichisches Bundesland")
    wohnflaeche_m2: float = Field(..., gt=0, le=1000, description="Wohnnutzfläche in m²")
    baukosten_eur: float = Field(..., gt=0, description="Geschätzte Baukosten in €")
    personen_im_haushalt: int = Field(1, ge=1, le=10, description="Personenanzahl im Haushalt")
    kinder: int = Field(0, ge=0, le=10, description="Anzahl der Kinder im Haushalt")
    jahreseinkommen_eur: float = Field(..., gt=0, description="Jahreseinkommen in € (Netto oder Brutto je BL)")
    energieklasse: str = Field("B", description="Erreichte Energieklasse (A++ bis G)")
    neubau: bool = Field(True, description="Neubau (True) oder Sanierung (False)")
    gebaudetyp: str = Field("mehrfamilienhaus", description="Gebäudetyp")


class EinkommensCheck(BaseModel):
    foerderbar: bool
    ihr_einkommen_eur: float
    einkommensgrenze_eur: float
    einkommenstyp: str
    differenz_eur: float


class EnergieCheck(BaseModel):
    foerderbar: bool
    ihre_klasse: str
    mindest_klasse: str


class FoerderCheckResult(BaseModel):
    bundesland: str
    programm: str
    foerderbar: bool
    ablehnungsgrund: Optional[str]
    einkommens_check: EinkommensCheck
    energieklasse_check: EnergieCheck
    max_foerderung_eur: float
    jahrliche_zinseinsparung_eur: Optional[float]
    foerderart: str
    zinssatz_prozent: Optional[float]
    laufzeit_jahre: Optional[int]
    besonderheiten: List[str]
    behoerde: str
    url: str
    antrag_online: bool
    antragsfrist_hinweis: str


# ─── Endpoints ────────────────────────────────────────────────────────────────


@router.post("/check", response_model=FoerderCheckResult)
async def check_foerderung(req: FoerderCheckRequest):
    """
    🏘️ **Wohnbauförderungs-Check**

    Prüft automatisch die Förderfähigkeit nach dem jeweiligen Bundesland-Förderungsgesetz.
    Berücksichtigt Einkommensgrenzen (Netto/Brutto je BL), Kinderzuschläge und Energieklasse.

    Alle 9 Bundesländer:
    - Wien WBF, NÖ WFW, OÖ WFG, Salzburg WFG, Tirol TWFG,
      Vorarlberg WBF, Steiermark WBF, Kärnten K-WFG, Burgenland WBF
    """
    bl_key = _normalize_bundesland(req.bundesland)
    foerder = _FOERDERUNG.get(bl_key)
    if not foerder:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Bundesland '{req.bundesland}' nicht gefunden. "
                f"Gültige Werte: {', '.join(_FOERDERUNG.keys())}"
            ),
        )

    einkommenstyp = foerder["einkommenstyp"]

    # Einkommensgrenze berechnen (Basis + Kinderzuschlag)
    if req.personen_im_haushalt == 1:
        grenze_basis = foerder.get(
            f"einkommensgrenze_{einkommenstyp}_1p",
            foerder.get(f"einkommensgrenze_{einkommenstyp}_2p", 40_000),
        )
    else:
        grenze_basis = foerder.get(
            f"einkommensgrenze_{einkommenstyp}_2p",
            foerder.get(f"einkommensgrenze_{einkommenstyp}_1p", 40_000),
        )
    kind_zuschlag = foerder.get(f"einkommensgrenze_{einkommenstyp}_je_kind", 4_000)
    grenze_gesamt = grenze_basis + req.kinder * kind_zuschlag

    einkommen_ok = req.jahreseinkommen_eur <= grenze_gesamt
    energieklasse_ok = _energieklasse_ok(req.energieklasse, foerder["min_energieklasse"])
    gesamt_foerderbar = einkommen_ok and energieklasse_ok

    # Ablehnungsgrund
    ablehnungsgrund = None
    if not einkommen_ok:
        ablehnungsgrund = (
            f"Einkommen ({req.jahreseinkommen_eur:,.0f} €) übersteigt Grenze "
            f"({grenze_gesamt:,.0f} € {einkommenstyp})"
        )
    elif not energieklasse_ok:
        ablehnungsgrund = (
            f"Energieklasse {req.energieklasse} schlechter als Mindestanforderung "
            f"{foerder['min_energieklasse']}"
        )

    # Maximale Förderung
    if foerder.get("max_foerderung_m2_eur"):
        flaeche_gefoerdert = min(req.wohnflaeche_m2, foerder.get("max_wohnflaeche_m2", 150))
        max_foerderung = flaeche_gefoerdert * foerder["max_foerderung_m2_eur"]
    else:
        max_foerderung = float(foerder.get("max_darlehen_eur", 0))

    # Jährliche Zinseinsparung vs. Marktzins (Referenz: 4 % Marktzins 2025)
    jaehrliche_zinseinsparung = None
    zinssatz = foerder.get("zinssatz_prozent")
    if zinssatz is not None and max_foerderung > 0:
        marktzins = 4.0
        jaehrliche_zinseinsparung = round(max_foerderung * (marktzins - zinssatz) / 100, 2)

    return FoerderCheckResult(
        bundesland=foerder["name"],
        programm=foerder["programm"],
        foerderbar=gesamt_foerderbar,
        ablehnungsgrund=ablehnungsgrund,
        einkommens_check=EinkommensCheck(
            foerderbar=einkommen_ok,
            ihr_einkommen_eur=req.jahreseinkommen_eur,
            einkommensgrenze_eur=grenze_gesamt,
            einkommenstyp=einkommenstyp,
            differenz_eur=round(grenze_gesamt - req.jahreseinkommen_eur, 2),
        ),
        energieklasse_check=EnergieCheck(
            foerderbar=energieklasse_ok,
            ihre_klasse=req.energieklasse,
            mindest_klasse=foerder["min_energieklasse"],
        ),
        max_foerderung_eur=max_foerderung if gesamt_foerderbar else 0.0,
        jahrliche_zinseinsparung_eur=jaehrliche_zinseinsparung if gesamt_foerderbar else None,
        foerderart=foerder["foerderart"],
        zinssatz_prozent=zinssatz,
        laufzeit_jahre=foerder.get("laufzeit_jahre"),
        besonderheiten=foerder.get("besonderheiten", []),
        behoerde=foerder["behoerde"],
        url=foerder["url"],
        antrag_online=foerder.get("antrag_online", False),
        antragsfrist_hinweis=foerder.get("antragsfrist_hinweis", ""),
    )


@router.get("/bundesland/{bundesland}")
async def get_foerderung_details(bundesland: str):
    """
    📋 **Förderdetails für ein Bundesland**

    Gibt alle Förderparameter (Einkommensgrenzen, Darlehenshöhe, Zinssatz,
    Öko-Boni, zuständige Behörde) für das gewählte Bundesland zurück.
    """
    bl_key = _normalize_bundesland(bundesland)
    foerder = _FOERDERUNG.get(bl_key)
    if not foerder:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Bundesland '{bundesland}' nicht gefunden. "
                f"Verfügbar: {', '.join(_FOERDERUNG.keys())}"
            ),
        )
    return foerder


@router.get("/alle")
async def get_alle_bundeslaender():
    """
    🗺️ **Alle Bundesländer — Förderübersicht**

    Kurzübersicht aller 9 Bundesländer mit den wichtigsten Eckdaten.
    """
    result = []
    for bl_key, f in _FOERDERUNG.items():
        einkommenstyp = f["einkommenstyp"]
        einkommensgrenze_1p = f.get(
            f"einkommensgrenze_{einkommenstyp}_1p",
            f.get(f"einkommensgrenze_{einkommenstyp}_2p", 0),
        )
        result.append(
            {
                "bundesland_key": bl_key,
                "name": f["name"],
                "programm": f["programm"],
                "einkommensgrenze_1p_eur": einkommensgrenze_1p,
                "einkommenstyp": einkommenstyp,
                "max_foerderung_eur": f.get("max_darlehen_eur") or f.get("max_foerderung_m2_eur"),
                "foerderart": f["foerderart"],
                "zinssatz_prozent": f.get("zinssatz_prozent"),
                "min_energieklasse": f["min_energieklasse"],
                "antrag_online": f.get("antrag_online", False),
                "url": f["url"],
            }
        )
    return {"bundeslaender": result, "total": len(result), "stand": "2025"}
