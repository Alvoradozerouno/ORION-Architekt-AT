"""
⊘∞⧈∞⊘ ORION ARCHITEKTEN-ASSISTENT ÖSTERREICH ⊘∞⧈∞⊘
Normgerecht · Gerichtsfest · Tirol-spezifisch

Basierend auf:
- ÖNORM A 6240-1 & A 6240-2 (Plandarstellung Hochbau)
- ÖNORM B 1800 (Flächenberechnung)
- ÖNORM B 1600 (Barrierefreies Bauen)
- OIB-Richtlinien 1-6 (Österreichisches Institut für Bautechnik)
- Tiroler Bauordnung 2022 (TBO 2022)
- Bauunterlagenverordnung 2024 (LGBl. 42/2024, ab 18.07.2024)
- Technische Bauvorschriften 2016 (TBV 2016)

Quellen & Referenzen:
- ÖNORM A 6240-2:2018-04-15 (Austrian Standards)
- OIB-Richtlinien 2023 (Österreichisches Institut für Bautechnik)
- Tiroler Bauordnung 2022 (LGBl.)
- Bauunterlagenverordnung 2024 (LGBl. 42/2024, ab 18.07.2024)
- TBO 2022 Novelle (LGBl. 7/2025)
- Technische Bauvorschriften 2016 (TBV 2016)
- 1. Tiroler Erneuerbaren Ausbaugesetz (ab 15.11.2024)

Stand: Februar 2026 — Aktuelle Gesetze immer auf https://www.ris.bka.gv.at prüfen!
HINWEIS: Orientierungshilfe, ersetzt KEINE Beratung durch befugte Planer.

Erstellt & Eigentum von Elisabeth Steurer & Gerhard Hirschmann
"""

import json
import hashlib
import uuid
from datetime import datetime, timezone

OIBL_RICHTLINIEN = {
    "OIB-RL 1": {
        "titel": "Mechanische Festigkeit und Standsicherheit",
        "beschreibung": "Nachweis der Tragfähigkeit, Gebrauchstauglichkeit und Dauerhaftigkeit des Tragwerks",
        "nachweise": [
            "Statische Berechnung durch Ziviltechniker/Statiker",
            "Lastannahmen nach ÖNORM EN 1991",
            "Bemessung nach Eurocodes (EC2 Beton, EC3 Stahl, EC5 Holz, EC6 Mauerwerk)",
            "Erdbebensicherheit nach ÖNORM EN 1998 (Erdbebenzone Tirol beachten!)",
            "Fundamentierung und Gründung",
            "Schneelast-Nachweis (Tirol: erhöhte Schneelasten je nach Seehöhe!)",
        ],
        "dokumente": ["Statisches Gutachten", "Tragwerksplanung", "Prüfstatik (bei größeren Bauvorhaben)"],
        "tirol_besonderheit": "Tirol hat erhöhte Schneelasten (Zone 2-4) und liegt in Erdbebenzone 3-4. Besondere Beachtung erforderlich!"
    },
    "OIB-RL 2": {
        "titel": "Brandschutz",
        "beschreibung": "Maßnahmen zum vorbeugenden Brandschutz bei der Errichtung und Änderung von Bauwerken",
        "nachweise": [
            "Brandschutzkonzept",
            "Feuerwiderstandsklassen (REI 30/60/90) der Bauteile",
            "Fluchtweglängen und -breiten",
            "Brandabschnitte",
            "Rauch- und Wärmeabzugsanlagen (bei größeren Gebäuden)",
            "Brandschutztüren (EI2 30-C, EI2 60-C, EI2 90-C)",
            "Löschwasserversorgung",
        ],
        "dokumente": ["Brandschutzkonzept", "Brandschutzplan", "Fluchtwegeplan"],
        "tirol_besonderheit": "Bei Gebäuden in alpiner Lage: Zufahrt für Feuerwehr prüfen!"
    },
    "OIB-RL 3": {
        "titel": "Hygiene, Gesundheit und Umweltschutz",
        "beschreibung": "Schutz vor Feuchtigkeit, Schadstoffen und Beeinträchtigungen der Gesundheit",
        "nachweise": [
            "Feuchtigkeitsschutz (Abdichtung, Drainage)",
            "Trinkwasserhygiene",
            "Abwasserentsorgung (Kanalanschluss oder Kläranlage)",
            "Radonschutz (in Tirol stellenweise erhöhte Radonbelastung!)",
            "Tageslichtversorgung (Fensterfläche ≥ 1/10 der Bodenfläche)",
            "Raumhöhe (≥ 2,50 m bei Aufenthaltsräumen)",
        ],
        "dokumente": ["Kanalanschlussbescheid", "Bodengutachten (bei Verdacht auf Kontamination)"],
        "tirol_besonderheit": "Radonvorsorgegebiet in Teilen Tirols — Radonschutzmaßnahmen im Keller!"
    },
    "OIB-RL 4": {
        "titel": "Nutzungssicherheit und Barrierefreiheit",
        "beschreibung": "Schutz gegen Absturz, Rutschsicherheit und barrierefreie Gestaltung",
        "nachweise": [
            "Geländer und Absturzsicherungen (Höhe ≥ 1,00 m, bei Kindern ≤ 12 cm Öffnungen)",
            "Treppen: Steigung/Auftritt nach Schrittmaßregel (2s + a = 59-65 cm)",
            "Handlauf beidseitig bei Treppen > 1,20 m Breite",
            "Rutschhemmung bei Bodenbelägen",
            "Barrierefreiheit nach ÖNORM B 1600/1601",
            "Aufzug ab 3 Obergeschossen (bei Wohngebäuden)",
        ],
        "dokumente": ["Barrierefreiheitskonzept (bei öffentlichen Gebäuden)", "Treppenberechnung"],
        "tirol_besonderheit": "Bei Tourismusbetrieben in Tirol besondere Barrierefreiheits-Anforderungen!"
    },
    "OIB-RL 5": {
        "titel": "Schallschutz",
        "beschreibung": "Schutz gegen Lärm durch bauliche Maßnahmen",
        "nachweise": [
            "Luftschalldämmung (R'w ≥ 55 dB zwischen Wohnungen)",
            "Trittschalldämmung (L'nT,w ≤ 48 dB)",
            "Außenlärmschutz (Schalldämm-Maß der Fassade)",
            "Haustechnische Anlagen (Schallpegel ≤ 30 dB(A) in Schlafräumen)",
        ],
        "dokumente": ["Bauphysikalisches Gutachten — Schallschutz", "Schallschutznachweis"],
        "tirol_besonderheit": "Nähe zu Autobahn/Bundesstraße beachten — erhöhte Schallschutzanforderungen!"
    },
    "OIB-RL 6": {
        "titel": "Energieeinsparung und Wärmeschutz",
        "beschreibung": "Anforderungen an den Heizwärmebedarf und die Gesamtenergieeffizienz",
        "nachweise": [
            "Energieausweis (Pflicht bei Neubau und umfassender Sanierung)",
            "Heizwärmebedarf HWB (max. Referenzwert je nach Gebäudeart)",
            "U-Werte der Bauteile (Wand, Dach, Fenster, Boden)",
            "Wärmebrückennachweis",
            "Sommerlicher Wärmeschutz",
            "Erneuerbare Energiequellen (Tirol: 1. Tiroler Erneuerbaren Ausbaugesetz!)",
        ],
        "dokumente": ["Energieausweis", "U-Wert-Berechnungen", "Wärmebrückendetails"],
        "tirol_besonderheit": "Seit 15.11.2024: 1. Tiroler Erneuerbaren Ausbaugesetz — PV-Anlagen-Anforderungen!"
    },
}

EINREICHPLAN_CHECKLISTE = {
    "lageplan": {
        "titel": "Lageplan",
        "maßstab": "1:200, 1:500 oder 1:1000",
        "pflicht": True,
        "items": [
            {"text": "Grundstücksnummer des Bauplatzes", "pflicht": True},
            {"text": "In der Natur überprüfte Grundstücksgrenzen", "pflicht": True},
            {"text": "Koordinaten der Eckpunkte (Neu-/Zubau)", "pflicht": True},
            {"text": "Abstände zu Nachbargrundstücken", "pflicht": True},
            {"text": "Nordpfeil", "pflicht": True},
            {"text": "Höhenangaben (FBOK — Fertige Bodenkante)", "pflicht": True},
            {"text": "KFZ-Abstellplätze (Fläche, Anordnung)", "pflicht": True},
            {"text": "Zufahrt und Erschließung", "pflicht": True},
            {"text": "Kanal-, Wasser-, Stromanschlüsse", "pflicht": True},
            {"text": "Baumbestand (falls vorhanden)", "pflicht": False},
            {"text": "Bebauungsplan-Festlegungen", "pflicht": False},
        ]
    },
    "grundrisse": {
        "titel": "Grundrisse aller Geschosse",
        "maßstab": "1:100 (Einreichplan) / 1:50 (Polierplan)",
        "pflicht": True,
        "items": [
            {"text": "Keller (UG)", "pflicht": True},
            {"text": "Erdgeschoss (EG)", "pflicht": True},
            {"text": "Obergeschoss(e) (OG)", "pflicht": True},
            {"text": "Dachgeschoss (DG)", "pflicht": True},
            {"text": "Raumwidmungen (Abkürzungen nach ÖNORM)", "pflicht": True},
            {"text": "Raumflächen in m²", "pflicht": True},
            {"text": "Wandstärken und Raummaße", "pflicht": True},
            {"text": "Türen und Fenster (kotierte Achsen)", "pflicht": True},
            {"text": "Durchgangslichte (DL)", "pflicht": True},
            {"text": "Treppen (Auftritt, Steigung, Handlauf)", "pflicht": True},
            {"text": "Farbige Darstellung (Bestand/Abbruch/Neu)", "pflicht": True},
        ]
    },
    "schnitte": {
        "titel": "Schnitte",
        "maßstab": "1:100",
        "pflicht": True,
        "items": [
            {"text": "Mindestens 1 Schnitt durch die Stiege", "pflicht": True},
            {"text": "Raumhöhen (RH — lichte Raumhöhe)", "pflicht": True},
            {"text": "Geschoßhöhen (GH)", "pflicht": True},
            {"text": "Bodenaufbauten", "pflicht": True},
            {"text": "Fensterparapethöhen (RPH/FPH)", "pflicht": True},
            {"text": "Baurechtliche Höhe", "pflicht": True},
            {"text": "Höhendreiecke FBOK in Metern", "pflicht": True},
            {"text": "Geländeverlauf", "pflicht": True},
        ]
    },
    "ansichten": {
        "titel": "Ansichten (alle Fassaden)",
        "maßstab": "1:100",
        "pflicht": True,
        "items": [
            {"text": "Nord-, Süd-, Ost-, West-Ansicht", "pflicht": True},
            {"text": "FBOK und DUK in den Ecken", "pflicht": True},
            {"text": "Materialdarstellung (Farben nach ÖNORM)", "pflicht": True},
            {"text": "Anschlüsse an Nachbargebäude", "pflicht": False},
            {"text": "Dachform und Dachneigung", "pflicht": True},
            {"text": "Geländeverlauf", "pflicht": True},
        ]
    },
    "baubeschreibung": {
        "titel": "Baubeschreibung",
        "maßstab": "—",
        "pflicht": True,
        "items": [
            {"text": "Grundgröße und Nutzfläche", "pflicht": True},
            {"text": "Bauausführung und Materialien", "pflicht": True},
            {"text": "Verwendungszweck", "pflicht": True},
            {"text": "Angaben zur Elektromobilität (§37b TBV 2016)", "pflicht": True},
            {"text": "Angaben zur elektronischen Kommunikation (§37 TBV 2016)", "pflicht": True},
            {"text": "KFZ-Abstellplätze", "pflicht": True},
            {"text": "OIB-Richtlinien Nachweise (RL 1-6)", "pflicht": True},
        ]
    },
    "nachweise": {
        "titel": "Nachweise & Beilagen",
        "maßstab": "—",
        "pflicht": True,
        "items": [
            {"text": "Grundbuchsauszug (Eigentumsnachweis)", "pflicht": True},
            {"text": "Geometrischer Lageplan (vom Geometer)", "pflicht": True},
            {"text": "Energieausweis (registriert in Datenbank)", "pflicht": True},
            {"text": "Statische Vorbemessung", "pflicht": True},
            {"text": "Bauphysikalische Nachweise", "pflicht": True},
            {"text": "Kanalanschlussbescheid", "pflicht": True},
            {"text": "Stellplatzverpflichtung", "pflicht": False},
            {"text": "Anrainerverzeichnis", "pflicht": True},
            {"text": "Bebauungsplan (falls vorhanden)", "pflicht": False},
        ]
    },
}

OENORM_ABKUERZUNGEN = {
    "Höhenbezug": {
        "FBOK": "Fußbodenoberkante (fertiger Fußboden)",
        "DOK": "Deckenoberkante (Rohbaumaß)",
        "DUK": "Deckenunterkante (Rohbaumaß)",
        "OK": "Oberkante",
        "UK": "Unterkante",
        "STUK": "Sturzunterkante (Rohbaumaß)",
        "GH": "Geschoßhöhe",
        "RH": "Lichte Raumhöhe",
        "RPH": "Rohbauparapethöhe",
        "FPH": "Fertige Parapethöhe",
    },
    "Öffnungen": {
        "BR": "Baurichtmaß",
        "RBL": "Rohbaulichte",
        "AL": "Architekturlichte",
        "DL": "Durchgangslichte (nutzbar)",
        "WD": "Wanddurchbruch",
        "DD": "Deckendurchbruch",
        "FBD": "Fußbodendurchbruch",
    },
    "Geschosse": {
        "EG": "Erdgeschoss",
        "UG": "Untergeschoss",
        "OG": "Obergeschoss",
        "DG": "Dachgeschoss",
        "KG": "Kellergeschoss",
        "ST": "Stockwerk",
    },
    "Räume": {
        "WZ": "Wohnzimmer",
        "SZ": "Schlafzimmer",
        "KI": "Kinderzimmer",
        "KÜ": "Küche",
        "BD": "Bad",
        "WC": "WC",
        "VR": "Vorraum",
        "GG": "Gang",
        "AR": "Abstellraum",
        "TR": "Treppenraum",
        "GA": "Garage",
        "KE": "Keller",
        "HZ": "Heizraum",
        "WK": "Waschküche",
        "BK": "Balkon",
        "TE": "Terrasse",
        "LO": "Loggia",
    },
}

MASSSTAEBE = {
    "Übersichtslagepläne": ["1:2000", "1:1000", "1:500"],
    "Lagepläne": ["1:1000", "1:500", "1:200"],
    "Einreichpläne": ["1:100"],
    "Polierpläne (Ausführung)": ["1:50"],
    "Detailpläne": ["1:25", "1:20", "1:10", "1:5", "1:2", "1:1"],
    "Einrichtungspläne": ["1:50", "1:25", "1:20"],
    "Haustechnikpläne": ["1:100", "1:50", "1:20"],
}

FARBCODE_MATERIALIEN = {
    "Bestand (unverändert)": {"farbe": "#666666", "css": "#888"},
    "Neubau — Mauerwerk": {"farbe": "Rot", "css": "#cc3333"},
    "Neubau — Stahlbeton": {"farbe": "Dunkelgrün/Schwarz", "css": "#2d5a2d"},
    "Neubau — Holz": {"farbe": "Braun/Ocker", "css": "#8B6914"},
    "Neubau — Stahl": {"farbe": "Blau", "css": "#3355aa"},
    "Abbruch": {"farbe": "Gelb", "css": "#ccaa00"},
    "Dämmung": {"farbe": "Violett/Schraffur", "css": "#8844aa"},
}

TIROL_SPEZIFISCH = {
    "rechtsgrundlagen": [
        "Tiroler Bauordnung 2022 (TBO 2022)",
        "Bauunterlagenverordnung 2024 (LGBl. 42/2024) — ab 18.07.2024",
        "Technische Bauvorschriften 2016 (TBV 2016)",
        "1. Tiroler Erneuerbaren Ausbaugesetz — ab 15.11.2024",
        "Tiroler Raumordnungsgesetz 2022 (TROG 2022)",
        "Tiroler Digitalisierungsgesetz 2023 (LGBl. 85/2023)",
    ],
    "digitale_einreichung": {
        "seit": "01.07.2024",
        "beschreibung": "Bauansuchen können digital per E-Mail oder Online-Formular eingereicht werden",
        "anforderungen": [
            "Seitengrößen reglementiert (keine großformatigen Ausgabegeräte nötig)",
            "Getrennte Anhänge bei digitalen Beilagen ohne inhaltliche Einheit",
            "Bezeichnung muss Inhalt erkennen lassen",
        ],
    },
    "besonderheiten": [
        "Erhöhte Schneelasten je nach Seehöhe (Zone 2-4)",
        "Erdbebenzone 3-4 — besondere statische Anforderungen",
        "Radonvorsorgegebiet — Radonschutzmaßnahmen im Keller",
        "Lawinenschutz und Hangwasserschutz bei alpinen Lagen",
        "Tourismuszone — besondere Gestaltungsvorschriften",
        "PV-Anlagen: 1. Tiroler Erneuerbaren Ausbaugesetz seit 15.11.2024",
        "Lageplan: Grundstücksgrenzen müssen 'in der Natur überprüft' sein (§ Bauunterlagenverordnung 2024). TBO 2022 Novelle 2025 klärt: Dies bedeutet NICHT, dass nur Zivilingenieure Lagepläne erstellen dürfen — aber Baumeister sind nicht zur Erstellung berechtigt. Befugnis im Einzelfall prüfen!",
    ],
}

UWERTE_RICHTWERTE = {
    "Außenwand": {"max_u": 0.35, "empfohlen_u": 0.20, "einheit": "W/(m²·K)"},
    "Oberste Geschoßdecke": {"max_u": 0.20, "empfohlen_u": 0.15, "einheit": "W/(m²·K)"},
    "Dach (geneigt)": {"max_u": 0.20, "empfohlen_u": 0.15, "einheit": "W/(m²·K)"},
    "Kellerdecke (beheizt/unbeheizt)": {"max_u": 0.40, "empfohlen_u": 0.25, "einheit": "W/(m²·K)"},
    "Bodenplatte (erdberührt)": {"max_u": 0.40, "empfohlen_u": 0.25, "einheit": "W/(m²·K)"},
    "Fenster (inkl. Rahmen)": {"max_u": 1.40, "empfohlen_u": 0.90, "einheit": "W/(m²·K)"},
    "Haustür": {"max_u": 1.70, "empfohlen_u": 1.20, "einheit": "W/(m²·K)"},
}


def get_checkliste():
    return EINREICHPLAN_CHECKLISTE

def get_oib_richtlinien():
    return OIBL_RICHTLINIEN

def get_abkuerzungen():
    return OENORM_ABKUERZUNGEN

def get_massstaebe():
    return MASSSTAEBE

def get_farbcodes():
    return FARBCODE_MATERIALIEN

def get_tirol_info():
    return TIROL_SPEZIFISCH

def get_uwerte():
    return UWERTE_RICHTWERTE

def generate_baubeschreibung_template(projekt_daten=None):
    d = projekt_daten or {}
    template = f"""
══════════════════════════════════════════════════════════════
                    BAUBESCHREIBUNG
         gemäß Bauunterlagenverordnung 2024
              Tiroler Bauordnung 2022
══════════════════════════════════════════════════════════════

1. BAUWERBER
   Name:     {d.get('bauwerber_name', '___________________________')}
   Adresse:  {d.get('bauwerber_adresse', '___________________________')}
   Tel:      {d.get('bauwerber_tel', '___________________________')}
   E-Mail:   {d.get('bauwerber_email', '___________________________')}

2. BAUGRUNDSTÜCK
   Gemeinde:  {d.get('gemeinde', '___________________________')}
   KG:        {d.get('kg', '___________________________')}
   Gst.Nr.:   {d.get('gst_nr', '___________________________')}
   EZ:        {d.get('ez', '___________________________')}
   Fläche:    {d.get('flaeche', '___________')} m²

3. BAUVORHABEN
   Art:       {d.get('vorhaben_art', '☐ Neubau  ☐ Zubau  ☐ Umbau  ☐ Sanierung')}
   Widmung:   {d.get('widmung', '___________________________')}
   Verwendung: {d.get('verwendung', '☐ Wohngebäude  ☐ Betriebsgebäude  ☐ Sonstige')}

4. KENNGRÖSSEN
   Bebaute Fläche:      {d.get('bebaute_flaeche', '_____')} m²
   Bruttogeschoßfläche: {d.get('bgf', '_____')} m²
   Nutzfläche:          {d.get('nf', '_____')} m²
   Gebäudehöhe:         {d.get('hoehe', '_____')} m
   Anzahl Geschosse:    {d.get('geschosse', '_____')}
   Wohneinheiten:       {d.get('wohneinheiten', '_____')}
   KFZ-Stellplätze:     {d.get('stellplaetze', '_____')}

5. KONSTRUKTION
   Fundament:   {d.get('fundament', '☐ Streifenfundament  ☐ Bodenplatte  ☐ Pfahlgründung')}
   Tragwerk:    {d.get('tragwerk', '☐ Massivbau  ☐ Holzbau  ☐ Skelettbau  ☐ Mischbau')}
   Außenwand:   {d.get('aussenwand', '___________________________')}
   U-Wert Wand: {d.get('u_wand', '_____')} W/(m²·K) [max. 0,35]
   Dach:        {d.get('dach', '☐ Steildach  ☐ Flachdach  ☐ Pultdach')}
   U-Wert Dach: {d.get('u_dach', '_____')} W/(m²·K) [max. 0,20]
   Fenster:     {d.get('fenster', '___________________________')}
   U-Wert Fenster: {d.get('u_fenster', '_____')} W/(m²·K) [max. 1,40]

6. HAUSTECHNIK
   Heizung:     {d.get('heizung', '☐ Wärmepumpe  ☐ Pellets  ☐ Gas  ☐ Fernwärme')}
   Warmwasser:  {d.get('warmwasser', '___________________________')}
   Lüftung:     {d.get('lueftung', '☐ Kontrollierte Wohnraumlüftung  ☐ Natürliche Lüftung')}
   PV-Anlage:   {d.get('pv', '☐ Ja  ☐ Nein')}  [Tirol: Erneuerbaren Ausbaugesetz beachten!]

7. ELEKTROMOBILITÄT (§37b TBV 2016)
   Ladeinfrastruktur: {d.get('emob', '☐ Leerverrohrung  ☐ Wallbox  ☐ Nicht zutreffend')}
   Anzahl vorgerüsteter Stellplätze: {d.get('emob_stell', '_____')}

8. ELEKTRONISCHE KOMMUNIKATION (§37 TBV 2016)
   Breitband-Anschluss:  {d.get('breitband', '☐ Glasfaser  ☐ Kabel  ☐ Sonstige')}
   Gebäudeverkabelung:   {d.get('verkabelung', '☐ Cat.7  ☐ Cat.6a  ☐ Sonstige')}

9. OIB-RICHTLINIEN KONFORMITÄT
   ☐ OIB-RL 1: Mechanische Festigkeit — Statik liegt bei
   ☐ OIB-RL 2: Brandschutz — Konzept erstellt
   ☐ OIB-RL 3: Hygiene/Gesundheit — Nachweise erbracht
   ☐ OIB-RL 4: Nutzungssicherheit/Barrierefreiheit — Geprüft
   ☐ OIB-RL 5: Schallschutz — Nachweis liegt bei
   ☐ OIB-RL 6: Energieausweis — Registriert in Datenbank

10. UNTERSCHRIFTEN

    _________________________     _________________________
    Bauwerber                     Planverfasser (Langstempel)
    
    _________________________
    Grundstückseigentümer
    
    Ort, Datum: _________________________

══════════════════════════════════════════════════════════════
    Erstellt gemäß TBO 2022 & Bauunterlagenverordnung 2024
══════════════════════════════════════════════════════════════
"""
    return template
