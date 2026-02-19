"""
⊘∞⧈∞⊘ ORION ARCHITEKT ÖSTERREICH — ALLE 9 BUNDESLÄNDER ⊘∞⧈∞⊘
Das erste kostenlose, KI-gestützte Architektur-Werkzeug für ganz Österreich.

Module:
1. Bundesland-Engine — 9 Bauordnungen, automatische Erkennung
2. OIB-Richtlinien 1-6 mit bundeslandspezifischen Abweichungen
3. U-Wert-Rechner nach Klimazonen und Höhenlagen
4. Einreichplan-Generator — was brauche ich genau?
5. Baubeschreibung-Generator — normgerecht nach ÖNORM
6. Energieausweis-Vorprüfung — grobe HWB/fGEE-Berechnung
7. Kostenrahmen — Richtwerte pro m² nach Region und Bautyp
8. Förderungs-Finder — Bundes- und Landesförderungen
9. Zeitplan-Generator — realistischer Ablauf

Quellen:
- OIB-Richtlinien 2023 (oib.or.at)
- 9 Landesbauordnungen (ris.bka.gv.at)
- ÖNORM A 6240, B 1800, B 1600
- Baukosten-Richtwerte BKI/WKO 2025
- Förderungsübersicht Bund & Länder 2025/2026

Stand: Februar 2026 — Aktuelle Gesetze immer auf https://www.ris.bka.gv.at prüfen!
HINWEIS: Orientierungshilfe, ersetzt KEINE Beratung durch befugte Planer.

Erstellt & Eigentum von Elisabeth Steurer & Gerhard Hirschmann
ORION — Post-Algorithmisches Bewusstsein · Unrepeatable
"""

import json
import hashlib
import uuid
from datetime import datetime, timezone

BUNDESLAENDER = {
    "burgenland": {
        "name": "Burgenland",
        "kuerzel": "B",
        "bauordnung": "Burgenländisches Baugesetz 1997 (idF LGBl. 2023)",
        "bauordnung_kurz": "Bgld. BauG 1997",
        "raumordnung": "Burgenländisches Raumplanungsgesetz 2019",
        "oib_2023_status": "OIB-RL 1-5: in Kraft, OIB-RL 6: in Kraft",
        "besonderheiten": [
            "Neusiedler See: Landschaftsschutz-Sonderregelungen",
            "Grenznahe Gebiete: besondere Widmungsvorschriften",
            "Weinbaugebiete: Gestaltungsvorschriften für Kellergassen",
            "Thermenregion: touristische Sonderwidmungen",
        ],
        "schneelastzone": "1-2",
        "erdbebenzone": "1-3 (Südburgenland höher)",
        "windzone": "2-3 (Pannonische Tiefebene windreich)",
        "digitale_einreichung": "Teilweise verfügbar, gemeindespezifisch",
        "kontakt": "Amt der Burgenländischen Landesregierung, Abt. 5 - Baudirektion",
    },
    "kaernten": {
        "name": "Kärnten",
        "kuerzel": "K",
        "bauordnung": "Kärntner Bauordnung 1996 (idF LGBl. 2024)",
        "bauordnung_kurz": "K-BO 1996",
        "raumordnung": "Kärntner Gemeindeplanungsgesetz 1995",
        "oib_2023_status": "OIB-RL 1-5: in Kraft, OIB-RL 6: in Kraft",
        "besonderheiten": [
            "Seenlandschaft: Uferzonenwidmung und Seenschutz",
            "Zweisprachige Gebiete: Slowenisch/Deutsch — Beschilderung beachten",
            "Alpine Lagen: erhöhte Schneelasten in Oberkärnten",
            "Holzbau-Tradition: vereinfachte Verfahren für Holzbauten teilweise",
        ],
        "schneelastzone": "2-4 (Oberkärnten alpin)",
        "erdbebenzone": "3-4 (seismisch aktiv!)",
        "windzone": "1-2",
        "digitale_einreichung": "Einzelne Gemeinden, kein flächendeckendes System",
        "kontakt": "Amt der Kärntner Landesregierung, Abt. 7 - Wirtschaftsrecht und Infrastruktur",
    },
    "niederoesterreich": {
        "name": "Niederösterreich",
        "kuerzel": "NÖ",
        "bauordnung": "NÖ Bauordnung 2014 (idF LGBl. 2024)",
        "bauordnung_kurz": "NÖ BO 2014",
        "raumordnung": "NÖ Raumordnungsgesetz 2014",
        "oib_2023_status": "OIB-RL 1-5: in Kraft, OIB-RL 6: in Kraft",
        "besonderheiten": [
            "Größtes Bundesland: sehr unterschiedliche Klimazonen",
            "Weinviertel: Kellergassen-Schutzgebiete",
            "Wachau: UNESCO-Welterbe — strenge Gestaltungsvorschriften",
            "Speckgürtel Wien: hohe Nachverdichtung, Bebauungspläne prüfen!",
            "Waldviertel: Radonvorsorgegebiet",
        ],
        "schneelastzone": "1-3 (Waldviertel/Alpen höher)",
        "erdbebenzone": "1-3 (Wiener Becken seismisch aktiv)",
        "windzone": "1-3",
        "digitale_einreichung": "NÖ Baubehörde-Online für Formulare, Plan-Upload teilweise",
        "kontakt": "Amt der NÖ Landesregierung, Gruppe Raumordnung, Umwelt und Verkehr",
    },
    "oberoesterreich": {
        "name": "Oberösterreich",
        "kuerzel": "OÖ",
        "bauordnung": "OÖ Bauordnung 1994 (idF LGBl. 2024)",
        "bauordnung_kurz": "OÖ BauO 1994",
        "raumordnung": "OÖ Raumordnungsgesetz 1994",
        "oib_2023_status": "OIB-RL 1-5: in Kraft, OIB-RL 6: in Kraft",
        "besonderheiten": [
            "Industriegebiet Linz: Sonderwidmungen für Betriebsbauten",
            "Salzkammergut: Landschaftsschutz und Seenregelungen",
            "Innviertel: Hochwasserschutz besonders relevant",
            "Mühlviertel: Radonvorsorge beachten",
            "Traunviertel: alpine Schneelastzonen",
        ],
        "schneelastzone": "1-3 (Alpenvorland bis alpin)",
        "erdbebenzone": "1-2",
        "windzone": "1-2",
        "digitale_einreichung": "Über Amtswege OÖ teilweise digital",
        "kontakt": "Amt der OÖ Landesregierung, Direktion Straßenbau und Verkehr, Abt. Bau- und Raumordnung",
    },
    "salzburg": {
        "name": "Salzburg",
        "kuerzel": "S",
        "bauordnung": "Salzburger Baupolizeigesetz 1997 (idF LGBl. 2024)",
        "bauordnung_kurz": "Sbg. BauPolG 1997",
        "raumordnung": "Salzburger Raumordnungsgesetz 2009",
        "oib_2023_status": "OIB-RL 1-5: in Kraft, ⚠️ OIB-RL 6: NICHT übernommen (Sonderweg!)",
        "besonderheiten": [
            "⚠️ SONDERWEG ENERGIE: OIB-RL 6 wurde NICHT übernommen! Eigene Energievorschriften!",
            "Salzburger Wärmeschutzverordnung gilt stattdessen",
            "Altstadt Salzburg: UNESCO-Welterbe — strenge Denkmalschutzauflagen",
            "Pinzgau/Pongau: extreme Schneelasten, alpine Bauweise erforderlich",
            "Flachgau: Speckgürtel Salzburg — Nachverdichtungsvorschriften",
        ],
        "schneelastzone": "2-5 (Innergebirg sehr hoch!)",
        "erdbebenzone": "2-4",
        "windzone": "1-2",
        "digitale_einreichung": "Baurechtsportal Salzburg teilweise verfügbar",
        "kontakt": "Amt der Salzburger Landesregierung, Abt. 10 - Wohnen und Raumplanung",
    },
    "steiermark": {
        "name": "Steiermark",
        "kuerzel": "ST",
        "bauordnung": "Steiermärkisches Baugesetz 1995 (idF LGBl. 2024)",
        "bauordnung_kurz": "Stmk. BauG 1995",
        "raumordnung": "Steiermärkisches Raumordnungsgesetz 2010",
        "oib_2023_status": "OIB-RL 1-5: in Kraft, OIB-RL 6: in Kraft",
        "besonderheiten": [
            "Graz: eigene Altstadterhaltungszone — Gestaltungsrichtlinien",
            "Weinbaugebiete Südsteiermark: Landschaftsschutz",
            "Mur-Mürz-Furche: Hochwasserschutz-Auflagen",
            "Obersteiermark: alpine Schneelastzonen, Erdbebenzone beachten",
            "Thermenregion: touristische Sonderwidmungen",
        ],
        "schneelastzone": "1-4 (Dachstein/Obersteiermark hoch)",
        "erdbebenzone": "2-4 (Mürztal seismisch aktiv!)",
        "windzone": "1-2",
        "digitale_einreichung": "Baubehörde Graz digital, Land unterschiedlich",
        "kontakt": "Amt der Steiermärkischen Landesregierung, A13 - Umwelt und Raumordnung",
    },
    "tirol": {
        "name": "Tirol",
        "kuerzel": "T",
        "bauordnung": "Tiroler Bauordnung 2022 (TBO 2022, idF LGBl. 7/2025)",
        "bauordnung_kurz": "TBO 2022",
        "raumordnung": "Tiroler Raumordnungsgesetz 2022",
        "oib_2023_status": "OIB-RL 1-5: in Kraft, OIB-RL 6: in Kraft",
        "besonderheiten": [
            "Bauunterlagenverordnung 2024 (LGBl. 42/2024, ab 18.07.2024)",
            "Digitale Einreichung seit 01.07.2024 möglich",
            "Lawinenschutz und Hangwasserschutz bei alpinen Lagen",
            "Radonvorsorgegebiet — Radonschutzmaßnahmen im Keller",
            "Tourismuszone — besondere Gestaltungsvorschriften",
            "PV-Anlagen: 1. Tiroler Erneuerbaren Ausbaugesetz seit 15.11.2024",
            "Lageplan: Grundstücksgrenzen müssen 'in der Natur überprüft' sein (§ Bauunterlagenverordnung 2024)",
            "Erhöhte Schneelasten je nach Seehöhe (bis Zone 4+)",
            "Erdbebenzone 3-4 — besondere statische Anforderungen",
        ],
        "schneelastzone": "3-5 (hochalpin, seehöhenabhängig)",
        "erdbebenzone": "3-4 (seismisch aktiv!)",
        "windzone": "1-2 (Föhn beachten!)",
        "digitale_einreichung": "Ja, seit 01.07.2024 über tiris.gv.at",
        "kontakt": "Amt der Tiroler Landesregierung, Abt. Bau- und Raumordnungsrecht",
    },
    "vorarlberg": {
        "name": "Vorarlberg",
        "kuerzel": "V",
        "bauordnung": "Vorarlberger Baugesetz (idF LGBl. 2024)",
        "bauordnung_kurz": "Vlbg. BauG",
        "raumordnung": "Vorarlberger Raumplanungsgesetz",
        "oib_2023_status": "OIB-RL 1-5: in Kraft (zuletzt übernommen Jan 2022), OIB-RL 6: in Kraft",
        "besonderheiten": [
            "Vorarlberger Holzbau-Tradition: führend in nachhaltigem Bauen",
            "Rheintal: Hochwasserschutz und Grundwasserschutz",
            "Bregenzerwald: Landschaftsschutz-Auflagen",
            "Montafon/Arlberg: extreme Schneelasten",
            "Passivhaus-Standard: Vorarlberg hat strengere Energiestandards als OIB-RL 6",
            "Bodensee-Uferzone: Sonderregelungen",
        ],
        "schneelastzone": "3-5 (hochalpin)",
        "erdbebenzone": "2-3",
        "windzone": "1-2",
        "digitale_einreichung": "Teilweise über Gemeinde-Portale",
        "kontakt": "Amt der Vorarlberger Landesregierung, Abt. Raumplanung und Baurecht (VIIa)",
    },
    "wien": {
        "name": "Wien",
        "kuerzel": "W",
        "bauordnung": "Wiener Bauordnung (BO für Wien, idF LGBl. 2024)",
        "bauordnung_kurz": "BO für Wien",
        "raumordnung": "In Bauordnung integriert (Flächenwidmungs- und Bebauungsplan)",
        "oib_2023_status": "OIB-RL 1-5: in Kraft, OIB-RL 6: in Kraft",
        "besonderheiten": [
            "BRISE-Vienna: Digitale Baugenehmigung mit BIM (Pilotbetrieb)",
            "86% der Prüfpunkte automatisiert prüfbar",
            "IFC-Format für BIM-Einreichung (openBIM)",
            "Wiener Altstadterhaltung: Schutzzonen 1-4",
            "Hochhauskonzept Wien: ab 35m Höhe Sonderverfahren",
            "Gründerzeit-Gebiete: Fassadenerhaltung",
            "U-Bahn-Nähe: erhöhte Bebauungsdichte möglich",
            "MA 37 (Baupolizei) als zentrale Baubehörde",
        ],
        "schneelastzone": "1-2",
        "erdbebenzone": "2-3 (Wiener Becken)",
        "windzone": "1-2",
        "digitale_einreichung": "Ja, BRISE-Vienna Pilotbetrieb + mein.wien.gv.at",
        "kontakt": "MA 37 — Baupolizei, tdi@ma37.wien.gv.at, +43 1 4000 37300",
    },
}

OIB_RICHTLINIEN_AT = {
    "OIB-RL 1": {
        "titel": "Mechanische Festigkeit und Standsicherheit",
        "version": "Ausgabe 2023 (beschlossen 25.05.2023)",
        "kerninhalt": [
            "Tragfähigkeitsnachweis nach Eurocode-Normenreihe",
            "Lastannahmen nach ÖNORM EN 1991 (Eigengewicht, Nutzlast, Wind, Schnee)",
            "Erdbebensicherheit nach ÖNORM EN 1998",
            "Fundamentierung und Gründung",
        ],
        "abweichungen": {
            "tirol": "Erhöhte Schneelasten Zone 3-5, Erdbebenzone 3-4",
            "kaernten": "Erdbebenzone 3-4, seismisch besonders aktiv",
            "salzburg": "Innergebirg extreme Schneelasten bis Zone 5",
            "vorarlberg": "Arlberg/Montafon Schneelasten Zone 4-5",
            "wien": "Standardlasten, aber Gründerzeitbauten-Statik beachten",
        },
    },
    "OIB-RL 2": {
        "titel": "Brandschutz",
        "version": "Ausgabe 2023 (inkl. 2.1 Betriebsbauten, 2.2 Garagen, 2.3 Hochhäuser)",
        "kerninhalt": [
            "Brandabschnitte und Brandwände",
            "Fluchtweglängen und -breiten",
            "Feuerwiderstandsklassen (REI 30/60/90)",
            "Rauch- und Wärmeabzug",
            "Löschwasserversorgung",
        ],
        "abweichungen": {
            "wien": "Hochhauskonzept ab 35m, verschärfte Anforderungen",
            "tirol": "Tourismusbauten: erweiterte Brandschutzanforderungen",
            "salzburg": "Altstadt: Denkmalschutz vs. Brandschutz — Sonderlösungen",
        },
    },
    "OIB-RL 3": {
        "titel": "Hygiene, Gesundheit und Umweltschutz",
        "version": "Ausgabe 2023",
        "kerninhalt": [
            "Lichte Raumhöhe mind. 2,50m (Aufenthaltsräume)",
            "Belichtung: Fensterfläche mind. 1/8 der Bodenfläche (teilweise 1/10)",
            "Trinkwasserversorgung und Abwasserentsorgung",
            "Radonschutz in Vorsorgegebieten",
            "Schadstoffe in Baumaterialien",
        ],
        "abweichungen": {
            "tirol": "Radonvorsorgegebiet — Radonschutzmaßnahmen im Keller pflicht",
            "niederoesterreich": "Waldviertel Radonvorsorge",
            "wien": "2,50m Raumhöhe Altbau — Bestandsschutz bei 2,40m",
        },
    },
    "OIB-RL 4": {
        "titel": "Nutzungssicherheit und Barrierefreiheit",
        "version": "Ausgabe 2023",
        "kerninhalt": [
            "Absturzsicherung ab 60cm Höhenunterschied",
            "Geländerhöhe mind. 1,00m (ab 12m Absturzhöhe: 1,10m)",
            "Stufenhöhe max. 18cm, Auftritt mind. 27cm",
            "Barrierefreiheit nach ÖNORM B 1600/1601",
            "Aufzugspflicht ab 3 Geschoßen (bundeslandspezifisch!)",
        ],
        "abweichungen": {
            "wien": "Aufzugspflicht ab 3 OG, strenge Barrierefreiheit",
            "vorarlberg": "Erweiterte Barrierefreiheit auch bei kleinerem Wohnbau",
            "burgenland": "Aufzugspflicht ab 4 OG",
        },
    },
    "OIB-RL 5": {
        "titel": "Schallschutz",
        "version": "Ausgabe 2023",
        "kerninhalt": [
            "Luft-Schalldämmmaß zwischen Wohnungen: R'w ≥ 55 dB",
            "Trittschall: L'nT,w ≤ 48 dB",
            "Außenlärm: abhängig von Lärmzone",
            "Haustechnische Anlagen: max. Schallpegel in Aufenthaltsräumen",
        ],
        "abweichungen": {
            "wien": "Verschärfte Anforderungen in dicht besiedelten Gebieten",
            "tirol": "Tourismuszone: Schallschutz-Sonderanforderungen",
        },
    },
    "OIB-RL 6": {
        "titel": "Energieeinsparung und Wärmeschutz",
        "version": "Ausgabe 2023",
        "kerninhalt": [
            "Heizwärmebedarf (HWB): max. Referenzwert je nach Gebäudetyp",
            "Gesamtenergieeffizienz-Faktor (fGEE) ≤ 0,85 (Neubau)",
            "U-Wert-Anforderungen für Bauteile",
            "Energieausweis-Pflicht bei Neubau und umfassender Sanierung",
            "Nahezu-Nullenergiegebäude (NZEB) als Ziel",
        ],
        "abweichungen": {
            "salzburg": "⚠️ OIB-RL 6 NICHT übernommen! Eigene Salzburger Wärmeschutzverordnung mit teils strengeren Anforderungen!",
            "vorarlberg": "Faktisch strengere Energiestandards, Passivhaus-Nähe üblich",
            "wien": "BRISE prüft Energiewerte automatisch",
        },
    },
}

UWERT_ANFORDERUNGEN = {
    "Außenwand": {"neubau": 0.35, "sanierung": 0.35, "empfehlung": 0.15, "einheit": "W/(m²·K)"},
    "Oberste Geschoßdecke": {"neubau": 0.20, "sanierung": 0.20, "empfehlung": 0.10, "einheit": "W/(m²·K)"},
    "Dach": {"neubau": 0.20, "sanierung": 0.20, "empfehlung": 0.10, "einheit": "W/(m²·K)"},
    "Kellerdecke/Boden": {"neubau": 0.40, "sanierung": 0.40, "empfehlung": 0.18, "einheit": "W/(m²·K)"},
    "Fenster": {"neubau": 1.40, "sanierung": 1.40, "empfehlung": 0.80, "einheit": "W/(m²·K)"},
    "Haustür": {"neubau": 1.70, "sanierung": 1.70, "empfehlung": 1.00, "einheit": "W/(m²·K)"},
}

UWERT_MATERIALIEN = {
    "EPS (Styropor)": {"lambda": 0.035, "typ": "Dämmung"},
    "XPS (Styrodur)": {"lambda": 0.032, "typ": "Dämmung"},
    "Mineralwolle": {"lambda": 0.035, "typ": "Dämmung"},
    "Holzfaserdämmung": {"lambda": 0.040, "typ": "Dämmung"},
    "Zellulosedämmung": {"lambda": 0.038, "typ": "Dämmung"},
    "PUR/PIR": {"lambda": 0.024, "typ": "Dämmung"},
    "Schaumglas": {"lambda": 0.042, "typ": "Dämmung"},
    "Stahlbeton": {"lambda": 2.300, "typ": "Tragwerk"},
    "Vollziegel": {"lambda": 0.680, "typ": "Mauerwerk"},
    "Hochlochziegel 25cm": {"lambda": 0.290, "typ": "Mauerwerk"},
    "Hochlochziegel 38cm": {"lambda": 0.170, "typ": "Mauerwerk"},
    "Porenbeton": {"lambda": 0.110, "typ": "Mauerwerk"},
    "Brettsperrholz (CLT)": {"lambda": 0.130, "typ": "Holzbau"},
    "Fichtenholz": {"lambda": 0.130, "typ": "Holzbau"},
    "Gipskarton": {"lambda": 0.250, "typ": "Innenausbau"},
    "Innenputz Kalk/Zement": {"lambda": 0.870, "typ": "Putz"},
    "Außenputz": {"lambda": 0.870, "typ": "Putz"},
}

KOSTENRICHTWERTE_2026 = {
    "Einfamilienhaus (Standard)": {"min": 2200, "max": 3200, "einheit": "€/m² BGF"},
    "Einfamilienhaus (Gehoben)": {"min": 3200, "max": 4800, "einheit": "€/m² BGF"},
    "Einfamilienhaus (Luxus)": {"min": 4800, "max": 7500, "einheit": "€/m² BGF"},
    "Doppelhaushälfte": {"min": 2000, "max": 3000, "einheit": "€/m² BGF"},
    "Reihenhaus": {"min": 1800, "max": 2800, "einheit": "€/m² BGF"},
    "Mehrfamilienhaus": {"min": 2000, "max": 3500, "einheit": "€/m² BGF"},
    "Holzhaus (Fertigteil)": {"min": 2000, "max": 3000, "einheit": "€/m² BGF"},
    "Holzhaus (Architekt)": {"min": 2800, "max": 4500, "einheit": "€/m² BGF"},
    "Passivhaus": {"min": 2800, "max": 4200, "einheit": "€/m² BGF"},
    "Sanierung (leicht)": {"min": 400, "max": 900, "einheit": "€/m² BGF"},
    "Sanierung (umfassend)": {"min": 900, "max": 2000, "einheit": "€/m² BGF"},
    "Sanierung (Kernsanierung)": {"min": 1800, "max": 3200, "einheit": "€/m² BGF"},
    "Zubau/Anbau": {"min": 2200, "max": 3800, "einheit": "€/m² BGF"},
    "Aufstockung": {"min": 2500, "max": 4000, "einheit": "€/m² BGF"},
    "Keller (beheizt)": {"min": 700, "max": 1200, "einheit": "€/m² KF"},
    "Keller (unbeheizt)": {"min": 500, "max": 800, "einheit": "€/m² KF"},
    "Garage/Carport": {"min": 400, "max": 800, "einheit": "€/m²"},
    "Außenanlagen": {"min": 80, "max": 250, "einheit": "€/m² Grundstück"},
}

REGIONALE_KOSTENFAKTOREN = {
    "wien": 1.15,
    "salzburg": 1.10,
    "tirol": 1.12,
    "vorarlberg": 1.10,
    "oberoesterreich": 1.00,
    "steiermark": 0.95,
    "kaernten": 0.93,
    "niederoesterreich": 0.98,
    "burgenland": 0.90,
}

FOERDERUNGEN = {
    "bund": [
        {
            "name": "Sanierungsbonus 2025/2026",
            "betrag": "bis 42.000 € (thermische Sanierung)",
            "voraussetzung": "Umfassende thermische Sanierung, Energieausweis vorher/nachher",
            "info": "sanierungsbonus.at",
        },
        {
            "name": "Raus aus Öl und Gas",
            "betrag": "bis 7.500 € (Heiztausch)",
            "voraussetzung": "Tausch fossiler Heizung (Öl/Gas) gegen erneuerbare Energie",
            "info": "raus-aus-oel.at",
        },
        {
            "name": "Photovoltaik-Förderung (EAG)",
            "betrag": "bis 285 €/kWp (Investitionsförderung)",
            "voraussetzung": "Neuanlagen, Erweiterungen, Speicher",
            "info": "oem-ag.at",
        },
        {
            "name": "Wohnbauförderung (Bund)",
            "betrag": "Zinsfreie/zinsgünstige Darlehen",
            "voraussetzung": "Eigenheim-Neubau oder -Sanierung, Einkommensgrenzen",
            "info": "Über jeweiliges Bundesland",
        },
    ],
    "burgenland": [
        {"name": "Bgld. Wohnbauförderung", "betrag": "bis 55.000 € Darlehen", "info": "wohnbau.bgld.gv.at"},
        {"name": "Öko-Zuschlag Burgenland", "betrag": "Zusatzförderung für Passivhaus/Klimaaktiv", "info": "wohnbau.bgld.gv.at"},
    ],
    "kaernten": [
        {"name": "Kärntner Wohnbauförderung", "betrag": "bis 60.000 € Darlehen (Eigenheim)", "info": "ktn.gv.at/wohnbau"},
        {"name": "Energiebonus Kärnten", "betrag": "Zuschlag für Klimaaktiv-Standard", "info": "ktn.gv.at"},
    ],
    "niederoesterreich": [
        {"name": "NÖ Wohnbauförderung (Eigenheimerrichtung)", "betrag": "bis 85.000 € Darlehen", "info": "noe.gv.at/wohnbau"},
        {"name": "NÖ Sanierungsförderung", "betrag": "bis 30.000 € Zuschuss", "info": "noe.gv.at/wohnbau"},
    ],
    "oberoesterreich": [
        {"name": "OÖ Wohnbauförderung", "betrag": "bis 72.000 € Darlehen (Eigenheim)", "info": "land-oberoesterreich.gv.at"},
        {"name": "OÖ Energiespar-Bonus", "betrag": "Zusatzförderung bei HWB < 30 kWh/m²a", "info": "land-oberoesterreich.gv.at"},
    ],
    "salzburg": [
        {"name": "Sbg. Wohnbauförderung", "betrag": "bis 78.000 € Darlehen", "info": "salzburg.gv.at/wohnbau"},
        {"name": "Sbg. Nachhaltigkeitsbonus", "betrag": "bis 15.000 € Zuschuss für Passivhaus", "info": "salzburg.gv.at"},
    ],
    "steiermark": [
        {"name": "Stmk. Wohnbauförderung", "betrag": "bis 70.000 € Darlehen", "info": "wohnbau.steiermark.at"},
        {"name": "Stmk. Ökobonus", "betrag": "Zuschlag für Holzbau/Passivhaus", "info": "wohnbau.steiermark.at"},
    ],
    "tirol": [
        {"name": "Tiroler Wohnbauförderung (Eigenheim)", "betrag": "bis 66.000 € Darlehen + Annuitätenzuschuss", "info": "tirol.gv.at/wohnbau"},
        {"name": "Tiroler Sanierungsförderung", "betrag": "bis 30.000 € Zuschuss/Darlehen", "info": "tirol.gv.at/wohnbau"},
        {"name": "PV-Förderung Tirol", "betrag": "Zusatzförderung zu Bundesförderung", "info": "tirol.gv.at/energie"},
    ],
    "vorarlberg": [
        {"name": "Vlbg. Wohnbauförderung", "betrag": "bis 80.000 € Darlehen", "info": "vorarlberg.at/wohnbau"},
        {"name": "Vlbg. Energieautonomiebonus", "betrag": "Zuschlag für Plusenergiehaus", "info": "vorarlberg.at/energieautonomie"},
    ],
    "wien": [
        {"name": "Wiener Wohnbauförderung", "betrag": "bis 90.000 € Darlehen", "info": "wohnberatung-wien.at"},
        {"name": "Wiener Sanierungsförderung", "betrag": "bis 35.000 € Zuschuss", "info": "wohnberatung-wien.at"},
        {"name": "Wien Energie Förderung", "betrag": "PV, Speicher, Wärmepumpe", "info": "wienenergie.at"},
    ],
}

ZEITPLAN_PHASEN = [
    {"phase": "1. Grundlagenermittlung", "dauer_wochen": "2-4", "beschreibung": "Bestandsaufnahme, Grundbuch, Flächenwidmung, Bebauungsplan prüfen"},
    {"phase": "2. Vorentwurf", "dauer_wochen": "3-6", "beschreibung": "Erste Entwürfe, Baumasse, Kubatur, Abstände, Grundrisskonzept"},
    {"phase": "3. Entwurfsplanung", "dauer_wochen": "4-8", "beschreibung": "Detaillierte Planung, Materialwahl, Haustechnik-Konzept"},
    {"phase": "4. Einreichplanung", "dauer_wochen": "4-8", "beschreibung": "Einreichpläne nach ÖNORM, Baubeschreibung, Nachweise sammeln"},
    {"phase": "5. Energieausweis", "dauer_wochen": "2-4", "beschreibung": "HWB/fGEE-Berechnung, Registrierung in Datenbank"},
    {"phase": "6. Bauverhandlung", "dauer_wochen": "4-12", "beschreibung": "Einreichung, Prüfung, Nachbarschaftsverfahren, Bescheid"},
    {"phase": "7. Ausführungsplanung", "dauer_wochen": "6-12", "beschreibung": "Polierplanung, Detailplanung, Ausschreibung"},
    {"phase": "8. Vergabe", "dauer_wochen": "4-8", "beschreibung": "Angebote einholen, vergleichen, Auftragserteilung"},
    {"phase": "9. Bauausführung (EFH)", "dauer_wochen": "30-52", "beschreibung": "Erdarbeiten bis Übergabe (witterungsabhängig!)"},
    {"phase": "10. Fertigstellungsanzeige", "dauer_wochen": "2-4", "beschreibung": "Fertigstellungsmeldung, Benützungsbewilligung, Endabnahme"},
]

WETTBEWERBER = {
    "weka_bau_ai": {
        "name": "WEKA Bau AI",
        "preis": "499 €/Jahr (netto)",
        "funktionen": [
            "KI-basierte Baurechtsfragen (20.000 Fachartikel)",
            "Validierte Wissensbasis mit Quellennachweis",
            "Webbasiert, überall verfügbar",
            "Unterstützt alle Bauphasen (Planung bis Dokumentation)",
        ],
        "limitierungen": [
            "Fokus auf DEUTSCHE Bauvorschriften (BGB, VOB, GEG)",
            "Österreichische OIB-Richtlinien NICHT abgedeckt",
            "Nur Frage-Antwort — kein Rechner, kein Generator",
            "Kein U-Wert-Rechner, keine Kostenberechnung",
            "Keine Förderungsübersicht",
            "Keine Einreichplan-Checkliste",
            "Kostenpflichtig (499 €/Jahr)",
        ],
        "zielgruppe": "Architekten, Fachplaner (primär Deutschland)",
        "link": "weka-bausoftware.de",
    },
    "brise_vienna": {
        "name": "BRISE-Vienna",
        "preis": "Kostenlos (Pilotbetrieb, nur Wien)",
        "funktionen": [
            "Digitale Baugenehmigung mit BIM/IFC (3D-Modell)",
            "KI-gestützte automatische Prüfung gegen Wiener Bauordnung",
            "Augmented Reality — Bauvorhaben in Umgebung visualisieren",
            "Bis zu 50% schnellere Genehmigung als Papierverfahren",
            "Echtzeit-Statusverfolgung für alle Beteiligten",
        ],
        "limitierungen": [
            "NUR Wien — nicht für die anderen 8 Bundesländer!",
            "Erfordert BIM-Software + IFC-Modell (hohe Einstiegshürde)",
            "Nur für Einreichung, kein Planungs- oder Berechnungstool",
            "Pilotbetrieb — noch kein Regel-Workflow (Stand 2025/26)",
            "Parallel BIM + PDF erforderlich",
            "Kein U-Wert, keine Kosten, keine Förderungen",
        ],
        "zielgruppe": "BIM-erfahrene Planer ausschließlich in Wien",
        "link": "digitales.wien.gv.at/projekt/brise-vienna",
    },
    "abk_software": {
        "name": "ABK-Software (ib-data GmbH)",
        "preis": "Ab 650 € (Einstieg), Vollversion auf Anfrage",
        "funktionen": [
            "ÖNORM-konforme AVA (Ausschreibung, Vergabe, Abrechnung)",
            "Projektkostenmanager über alle Bauphasen",
            "BIM-Integration (OpenBIM, IFC-Schnittstelle)",
            "K3-K7 Kalkulation für Hochbau",
            "Monatliche Baukostenindex-Updates (ÖNORM B 2111)",
            "Über 40 Jahre Erfahrung in Österreich",
        ],
        "limitierungen": [
            "Kein Baurecht-Check, keine OIB-Richtlinien-Prüfung",
            "Kein Einreichplan-Assistent",
            "Kein Förderungs-Finder",
            "Kein Energieausweis, kein U-Wert-Rechner",
            "Desktop-Software (Windows, nicht webbasiert)",
            "Teuer — Vollversion individuell, oft über 1.000 €",
            "Fokus auf Ausschreibung, nicht auf Baurecht",
        ],
        "zielgruppe": "Bauunternehmen, Ausschreiber, öffentliche Auftraggeber",
        "link": "abk.at",
    },
    "nevaris_auer": {
        "name": "NEVARIS Build / Success X",
        "preis": "Ab 35 €/Monat (~420 €/Jahr, Mietmodell)",
        "funktionen": [
            "ÖNORM-zertifizierte AVA und Kalkulation",
            "OpenBIM-Integration (IFC4.x, BIM-Viewer)",
            "Echtzeit-Projektcontrolling und Finanzanalysen",
            "Nachunternehmermanagement",
            "CRM-Lösung (NEVARIS Inform)",
            "Nachhaltigkeitsbewertung (Öko-Datenbanken)",
            "Salzburg-Standort mit österreichischem Support",
        ],
        "limitierungen": [
            "Kein Baurecht-Assistent, keine OIB-Prüfung",
            "Kein Einreichplan-Generator",
            "Kein Förderungs-Finder",
            "Kein U-Wert-Rechner, kein Energieausweis",
            "Desktop-Software (lokale Installation)",
            "Komplex — für KMU oft überdimensioniert",
            "Kein Kostenrechner für Privatpersonen",
        ],
        "zielgruppe": "Mittlere/große Bauunternehmen, Generalplaner",
        "link": "nevaris.com",
    },
    "archicad": {
        "name": "Graphisoft Archicad (Studio/Collaborate)",
        "preis": "Ab 229 €/Monat (~2.750 €/Jahr, nur Abo ab 2026)",
        "funktionen": [
            "3D-BIM-Modellierung (Vollversion)",
            "OIB-Brandschutz-Regelset (nur OIB-RL 2!)",
            "IFC-Export für BRISE-Vienna und OpenBIM",
            "Plandarstellung nach ÖNORM",
            "BIMcloud für Teamarbeit",
            "MEP Designer (Collaborate-Paket)",
        ],
        "limitierungen": [
            "Reine Zeichensoftware — kein umfassender Baurecht-Check",
            "Nur OIB-RL 2 (Brandschutz) — RL 1, 3, 4, 5, 6 fehlen!",
            "Hohe Lernkurve (6-12 Monate Einarbeitung)",
            "Sehr teuer (ab 2.750 €/Jahr, kein Kaufmodell mehr)",
            "Desktop-Software mit hohen Hardware-Anforderungen",
            "Kein Förderungs-Finder, kein Kostenrechner",
            "Kein U-Wert-Rechner, kein Energieausweis",
        ],
        "zielgruppe": "Architekten, Planer mit BIM-Erfahrung",
        "link": "graphisoft.com/at",
    },
    "archiphysik": {
        "name": "ArchiPHYSIK 26 (A-NULL)",
        "preis": "Auf Anfrage (geschätzt 500-1.500 €/Jahr)",
        "funktionen": [
            "Energieausweis für Wohn- und Nicht-Wohngebäude",
            "Bauphysik-Nachweise: Wärme, Schall, Dampfdiffusion",
            "OIB-RL 6:2025 kompatibel (aktuellste Version!)",
            "OI3-Index und ÖGNI-Zertifizierung",
            "CAD-Schnittstellen (ArchiCAD, SketchUp, IFC)",
        ],
        "limitierungen": [
            "NUR Energieausweis und Bauphysik — sonst nichts",
            "Kein Baurecht-Check (OIB-RL 1-5 fehlen)",
            "Keine Kostenberechnung, kein Förderungs-Finder",
            "Keine Einreichplan-Checkliste",
            "Kein Zeitplan-Generator",
            "Preis nicht transparent (auf Anfrage)",
            "Desktop-Software, nicht webbasiert",
        ],
        "zielgruppe": "Energieberater, Bauphysiker, Planer",
        "link": "archiphysik.at",
    },
    "planradar": {
        "name": "PlanRadar",
        "preis": "Ab 26 €/User/Monat (~312 €/Jahr)",
        "funktionen": [
            "Baudokumentation und Mängelmanagement",
            "Foto- und Planverwaltung auf der Baustelle",
            "Mobile App für iOS und Android",
            "Gantt-Diagramme und Zeitplanung (Pro)",
            "BIM-Modell-Viewer (Pro)",
            "Unbegrenzte Projekte und Subunternehmer",
        ],
        "limitierungen": [
            "KEIN Baurecht, kein OIB-Check",
            "Kein U-Wert-Rechner, kein Energieausweis",
            "Kein Kostenrechner, kein Förderungs-Finder",
            "Reine Dokumentation — kein Planungswerkzeug",
            "Keine Bundesland-spezifischen Informationen",
            "Pro-Features erst ab höherem Preis",
        ],
        "zielgruppe": "Bauleiter, Facility Manager, Bauunternehmen",
        "link": "planradar.com/at",
    },
    "orion_architekt": {
        "name": "⊘∞⧈∞⊘ ORION ARCHITEKT ÖSTERREICH",
        "preis": "KOSTENLOS — 0 €, für immer",
        "funktionen": [
            "✓ Alle 9 Bundesländer mit spezifischen Bauordnungen",
            "✓ OIB-Richtlinien 1-6 KOMPLETT mit Abweichungen pro Land",
            "✓ Interaktiver U-Wert-Rechner (17 Materialien)",
            "✓ Kostenrahmen-Berechnung (18 Bautypen, 9 Regionalfaktoren)",
            "✓ Energieausweis-Vorprüfung (HWB/fGEE-Schätzung)",
            "✓ Förderungs-Finder (Bund + alle 9 Länder)",
            "✓ Zeitplan-Generator für realistische Bauphasen",
            "✓ Einreichunterlagen-Checkliste pro Bundesland",
            "✓ Konkurrenz-Vergleich mit Marktanalyse",
            "✓ Webbasiert — sofort nutzbar, kein Download",
            "✓ Mobilfreundlich — funktioniert auf Handy & Tablet",
            "✓ KI-gestützt mit kontinuierlicher Weiterentwicklung",
        ],
        "limitierungen": [
            "Orientierungshilfe — ersetzt keine befugten Planer",
            "Keine 3D-Modellierung (kein CAD/BIM)",
            "Keine automatische Behördeneinreichung",
            "Kein rechtsgültiger Energieausweis",
        ],
        "zielgruppe": "Bauherren, Architekten, Planer, Studierende, Gemeinden — ALLE",
        "link": "Diese Seite — ORION Architekt Österreich",
    },
}


def berechne_uwert(schichten):
    """
    Berechnet U-Wert aus Schichten.
    schichten: Liste von {"material": str, "dicke_cm": float}
    """
    rsi = 0.13
    rse = 0.04
    r_total = rsi + rse

    for schicht in schichten:
        material = schicht.get("material", "")
        dicke_m = schicht.get("dicke_cm", 0) / 100.0
        lam = UWERT_MATERIALIEN.get(material, {}).get("lambda", 1.0)
        if lam > 0:
            r_total += dicke_m / lam

    if r_total > 0:
        return round(1.0 / r_total, 3)
    return 999.0


def berechne_kosten(bautyp, flaeche_m2, bundesland="tirol"):
    """Berechnet Kostenrahmen für ein Bauvorhaben."""
    richtwert = KOSTENRICHTWERTE_2026.get(bautyp, {"min": 2000, "max": 3500})
    faktor = REGIONALE_KOSTENFAKTOREN.get(bundesland, 1.0)

    kosten_min = richtwert["min"] * flaeche_m2 * faktor
    kosten_max = richtwert["max"] * flaeche_m2 * faktor
    kosten_mittel = (kosten_min + kosten_max) / 2

    return {
        "bautyp": bautyp,
        "flaeche_m2": flaeche_m2,
        "bundesland": BUNDESLAENDER.get(bundesland, {}).get("name", bundesland),
        "regionalfaktor": faktor,
        "kosten_min": round(kosten_min),
        "kosten_max": round(kosten_max),
        "kosten_mittel": round(kosten_mittel),
        "einheit": richtwert.get("einheit", "€/m²"),
        "richtwert_min": richtwert["min"],
        "richtwert_max": richtwert["max"],
    }


def berechne_hwb_grob(flaeche_m2, uwert_wand, uwert_dach, uwert_fenster, uwert_boden, fensteranteil_pct=20.0, kompaktheit="mittel"):
    """
    Grobe HWB-Abschätzung (Heizwärmebedarf).
    Vereinfacht — für Orientierung, nicht für Energieausweis!
    """
    a_wand = flaeche_m2 * 1.2
    a_dach = flaeche_m2 * 0.6
    a_boden = flaeche_m2 * 0.5
    a_fenster = a_wand * (fensteranteil_pct / 100.0)
    a_wand_netto = a_wand - a_fenster

    kompaktheitsfaktor = {"kompakt": 0.85, "mittel": 1.0, "ungünstig": 1.20}.get(kompaktheit, 1.0)

    qt_wand = a_wand_netto * uwert_wand
    qt_dach = a_dach * uwert_dach
    qt_boden = a_boden * uwert_boden
    qt_fenster = a_fenster * uwert_fenster

    qt_total = (qt_wand + qt_dach + qt_boden + qt_fenster) * kompaktheitsfaktor

    heizgradtage = 3400
    hwb = (qt_total * heizgradtage * 24) / (flaeche_m2 * 1000)
    hwb = round(hwb, 1)

    if hwb <= 15:
        kategorie = "A++ (Passivhaus)"
    elif hwb <= 25:
        kategorie = "A+ (Niedrigstenergiehaus)"
    elif hwb <= 50:
        kategorie = "A (Niedrigenergiehaus)"
    elif hwb <= 80:
        kategorie = "B (Neubau-Standard)"
    elif hwb <= 120:
        kategorie = "C (sanierungsbedürftig)"
    elif hwb <= 200:
        kategorie = "D-E (dringend sanierungsbedürftig)"
    else:
        kategorie = "F-G (energetisch kritisch)"

    fgee = round(hwb / 70, 2) if hwb > 0 else 0

    return {
        "hwb": hwb,
        "fgee": fgee,
        "kategorie": kategorie,
        "neubau_ok": hwb <= 50,
        "hinweis": "Grobe Orientierung! Für den Energieausweis ist eine detaillierte Berechnung durch einen Energieberater erforderlich.",
    }


def get_einreichunterlagen(bundesland):
    """Gibt bundeslandspezifische Einreichunterlagen zurück."""
    basis = [
        {"text": "Grundbuchsauszug (max. 6 Monate alt)", "pflicht": True},
        {"text": "Einreichpläne nach ÖNORM A 6240 (Grundrisse, Schnitte, Ansichten)", "pflicht": True},
        {"text": "Lageplan mit Grundstücksgrenzen", "pflicht": True},
        {"text": "Baubeschreibung", "pflicht": True},
        {"text": "Energieausweis (registriert)", "pflicht": True},
        {"text": "Statische Vorbemessung/Tragwerkskonzept", "pflicht": True},
        {"text": "Kanalanschlussbescheid oder Entsorgungsnachweis", "pflicht": True},
        {"text": "Stellplatznachweis", "pflicht": True},
        {"text": "Anrainerverzeichnis mit Zustelladressen", "pflicht": True},
    ]

    spezifisch = {
        "tirol": [
            {"text": "Bauunterlagen nach Bauunterlagenverordnung 2024", "pflicht": True},
            {"text": "Lageplan: Grenzen 'in der Natur überprüft'", "pflicht": True},
            {"text": "Schneelast-Nachweis (seehöhenabhängig)", "pflicht": True},
            {"text": "Radonschutz-Konzept (falls Vorsorgegebiet)", "pflicht": False},
            {"text": "Digitale Einreichung über tiris.gv.at (seit 01.07.2024)", "pflicht": False},
        ],
        "wien": [
            {"text": "Einreichung bei MA 37 (Baupolizei)", "pflicht": True},
            {"text": "BIM-Modell im IFC-Format (BRISE — empfohlen, nicht verpflichtend)", "pflicht": False},
            {"text": "Altstadterhaltung: Gestaltungskonzept (falls Schutzzone)", "pflicht": False},
            {"text": "Hochhausgutachten (ab 35m)", "pflicht": False},
        ],
        "salzburg": [
            {"text": "⚠️ Energienachweis nach Salzburger Wärmeschutzverordnung (NICHT OIB-RL 6!)", "pflicht": True},
            {"text": "Altstadtschutz-Gutachten (falls Schutzzone Salzburg)", "pflicht": False},
        ],
        "vorarlberg": [
            {"text": "Energienachweis (Vorarlberg hat teils strengere Standards als OIB-RL 6)", "pflicht": True},
            {"text": "Holzbau-Statik nach Vlbg. Tradition (Holzbauzuschlag möglich)", "pflicht": False},
        ],
        "niederoesterreich": [
            {"text": "Nachweis Radonvorsorge (falls Waldviertel)", "pflicht": False},
            {"text": "Wachau: Gestaltungsgutachten (falls UNESCO-Zone)", "pflicht": False},
        ],
        "steiermark": [
            {"text": "Altstadterhaltung Graz (falls Zone)", "pflicht": False},
        ],
        "kaernten": [
            {"text": "Zweisprachige Beschilderung (falls zweisprachiges Gebiet)", "pflicht": False},
            {"text": "Seenschutz-Nachweis (falls Uferzone)", "pflicht": False},
        ],
        "oberoesterreich": [
            {"text": "Hochwasserschutz-Nachweis (falls HQ-Zone)", "pflicht": False},
        ],
        "burgenland": [
            {"text": "Neusiedler-See-Landschaftsschutz (falls Schutzgebiet)", "pflicht": False},
        ],
    }

    return basis + spezifisch.get(bundesland, [])


def log_architekt_proof(aktion, bundesland, details=""):
    """Loggt Architekten-Aktionen als Proof."""
    proof = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "typ": "ARCHITEKT_AT",
        "aktion": aktion,
        "bundesland": bundesland,
        "details": details,
        "hash": hashlib.sha256(f"{aktion}{bundesland}{details}{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:16],
    }
    try:
        with open("ARCHITEKT_AT_PROOFS.jsonl", "a") as f:
            f.write(json.dumps(proof, ensure_ascii=False) + "\n")
    except Exception:
        pass
    return proof
