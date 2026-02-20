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

SCHNEELASTZONEN_AT = {
    "zone_1": {"bezeichnung": "Zone 1 (niedrig)", "sk_kn_m2": 1.12, "regionen": "Wiener Becken, östliches Flachland, Südburgenland"},
    "zone_2": {"bezeichnung": "Zone 2 (mittel)", "sk_kn_m2": 1.60, "regionen": "Alpenvorland, Mühlviertel, Weinviertel"},
    "zone_3": {"bezeichnung": "Zone 3 (hoch)", "sk_kn_m2": 2.30, "regionen": "Voralpengebiet, mittlere Höhenlagen"},
    "zone_4": {"bezeichnung": "Zone 4 (sehr hoch)", "sk_kn_m2": 3.40, "regionen": "Inneralpine Täler, höhere Lagen"},
    "zone_5": {"bezeichnung": "Zone 5 (extrem)", "sk_kn_m2": 5.60, "regionen": "Hochgebirge, Arlberg, Brenner-Region"},
}

WINDLASTZONEN_AT = {
    "zone_1": {"bezeichnung": "Zone 1 (gering)", "v_b0_ms": 25.0, "q_b_kn_m2": 0.39, "regionen": "Inneralpine Täler, geschützte Lagen"},
    "zone_2": {"bezeichnung": "Zone 2 (mittel)", "v_b0_ms": 27.4, "q_b_kn_m2": 0.47, "regionen": "Alpenvorland, Flachland"},
    "zone_3": {"bezeichnung": "Zone 3 (hoch)", "v_b0_ms": 30.0, "q_b_kn_m2": 0.56, "regionen": "Donauniederung, Wiener Becken, Burgenland"},
}

STAHLPROFILE = [
    {"typ": "IPE 100", "h_mm": 100, "b_mm": 55, "gewicht_kg_m": 8.1, "iy_cm4": 171, "wy_cm3": 34.2, "iz_cm4": 15.9, "a_cm2": 10.3},
    {"typ": "IPE 120", "h_mm": 120, "b_mm": 64, "gewicht_kg_m": 10.4, "iy_cm4": 318, "wy_cm3": 53.0, "iz_cm4": 27.7, "a_cm2": 13.2},
    {"typ": "IPE 140", "h_mm": 140, "b_mm": 73, "gewicht_kg_m": 12.9, "iy_cm4": 541, "wy_cm3": 77.3, "iz_cm4": 44.9, "a_cm2": 16.4},
    {"typ": "IPE 160", "h_mm": 160, "b_mm": 82, "gewicht_kg_m": 15.8, "iy_cm4": 869, "wy_cm3": 109, "iz_cm4": 68.3, "a_cm2": 20.1},
    {"typ": "IPE 180", "h_mm": 180, "b_mm": 91, "gewicht_kg_m": 18.8, "iy_cm4": 1317, "wy_cm3": 146, "iz_cm4": 101, "a_cm2": 23.9},
    {"typ": "IPE 200", "h_mm": 200, "b_mm": 100, "gewicht_kg_m": 22.4, "iy_cm4": 1943, "wy_cm3": 194, "iz_cm4": 142, "a_cm2": 28.5},
    {"typ": "IPE 220", "h_mm": 220, "b_mm": 110, "gewicht_kg_m": 26.2, "iy_cm4": 2772, "wy_cm3": 252, "iz_cm4": 205, "a_cm2": 33.4},
    {"typ": "IPE 240", "h_mm": 240, "b_mm": 120, "gewicht_kg_m": 30.7, "iy_cm4": 3892, "wy_cm3": 324, "iz_cm4": 284, "a_cm2": 39.1},
    {"typ": "IPE 270", "h_mm": 270, "b_mm": 135, "gewicht_kg_m": 36.1, "iy_cm4": 5790, "wy_cm3": 429, "iz_cm4": 420, "a_cm2": 45.9},
    {"typ": "IPE 300", "h_mm": 300, "b_mm": 150, "gewicht_kg_m": 42.2, "iy_cm4": 8356, "wy_cm3": 557, "iz_cm4": 604, "a_cm2": 53.8},
    {"typ": "IPE 330", "h_mm": 330, "b_mm": 160, "gewicht_kg_m": 49.1, "iy_cm4": 11770, "wy_cm3": 713, "iz_cm4": 788, "a_cm2": 62.6},
    {"typ": "IPE 360", "h_mm": 360, "b_mm": 170, "gewicht_kg_m": 57.1, "iy_cm4": 16270, "wy_cm3": 904, "iz_cm4": 1043, "a_cm2": 72.7},
    {"typ": "HEA 100", "h_mm": 96, "b_mm": 100, "gewicht_kg_m": 16.7, "iy_cm4": 349, "wy_cm3": 72.8, "iz_cm4": 134, "a_cm2": 21.2},
    {"typ": "HEA 120", "h_mm": 114, "b_mm": 120, "gewicht_kg_m": 19.9, "iy_cm4": 606, "wy_cm3": 106, "iz_cm4": 231, "a_cm2": 25.3},
    {"typ": "HEA 140", "h_mm": 133, "b_mm": 140, "gewicht_kg_m": 24.7, "iy_cm4": 1033, "wy_cm3": 155, "iz_cm4": 389, "a_cm2": 31.4},
    {"typ": "HEA 160", "h_mm": 152, "b_mm": 160, "gewicht_kg_m": 30.4, "iy_cm4": 1673, "wy_cm3": 220, "iz_cm4": 616, "a_cm2": 38.8},
    {"typ": "HEA 200", "h_mm": 190, "b_mm": 200, "gewicht_kg_m": 42.3, "iy_cm4": 3692, "wy_cm3": 389, "iz_cm4": 1336, "a_cm2": 53.8},
    {"typ": "HEA 240", "h_mm": 230, "b_mm": 240, "gewicht_kg_m": 60.3, "iy_cm4": 7763, "wy_cm3": 675, "iz_cm4": 2769, "a_cm2": 76.8},
    {"typ": "HEA 300", "h_mm": 290, "b_mm": 300, "gewicht_kg_m": 88.3, "iy_cm4": 18260, "wy_cm3": 1260, "iz_cm4": 6310, "a_cm2": 112.5},
    {"typ": "HEB 100", "h_mm": 100, "b_mm": 100, "gewicht_kg_m": 20.4, "iy_cm4": 450, "wy_cm3": 89.9, "iz_cm4": 167, "a_cm2": 26.0},
    {"typ": "HEB 120", "h_mm": 120, "b_mm": 120, "gewicht_kg_m": 26.7, "iy_cm4": 864, "wy_cm3": 144, "iz_cm4": 318, "a_cm2": 34.0},
    {"typ": "HEB 140", "h_mm": 140, "b_mm": 140, "gewicht_kg_m": 33.7, "iy_cm4": 1509, "wy_cm3": 216, "iz_cm4": 550, "a_cm2": 43.0},
    {"typ": "HEB 160", "h_mm": 160, "b_mm": 160, "gewicht_kg_m": 42.6, "iy_cm4": 2492, "wy_cm3": 311, "iz_cm4": 889, "a_cm2": 54.3},
    {"typ": "HEB 200", "h_mm": 200, "b_mm": 200, "gewicht_kg_m": 61.3, "iy_cm4": 5696, "wy_cm3": 570, "iz_cm4": 2003, "a_cm2": 78.1},
    {"typ": "HEB 240", "h_mm": 240, "b_mm": 240, "gewicht_kg_m": 83.2, "iy_cm4": 11260, "wy_cm3": 938, "iz_cm4": 3923, "a_cm2": 106.0},
    {"typ": "HEB 300", "h_mm": 300, "b_mm": 300, "gewicht_kg_m": 117.0, "iy_cm4": 25170, "wy_cm3": 1678, "iz_cm4": 8563, "a_cm2": 149.1},
]

BETONKLASSEN = [
    {"klasse": "C12/15", "fck_mpa": 12, "fcd_mpa": 8.0, "fctm_mpa": 1.6, "ecm_gpa": 27, "verwendung": "Sauberkeitsschichten, unbewehrte Fundamente"},
    {"klasse": "C16/20", "fck_mpa": 16, "fcd_mpa": 10.7, "fctm_mpa": 1.9, "ecm_gpa": 29, "verwendung": "Einfache Fundamente, Bodenplatten"},
    {"klasse": "C20/25", "fck_mpa": 20, "fcd_mpa": 13.3, "fctm_mpa": 2.2, "ecm_gpa": 30, "verwendung": "Standardbeton: Wände, Decken, Fundamente (Wohnbau)"},
    {"klasse": "C25/30", "fck_mpa": 25, "fcd_mpa": 16.7, "fctm_mpa": 2.6, "ecm_gpa": 31, "verwendung": "Häufigste Klasse: Decken, Stützen, Wände, Treppen"},
    {"klasse": "C30/37", "fck_mpa": 30, "fcd_mpa": 20.0, "fctm_mpa": 2.9, "ecm_gpa": 33, "verwendung": "Höher belastete Bauteile, Tiefgaragen, Keller bei Grundwasser"},
    {"klasse": "C35/45", "fck_mpa": 35, "fcd_mpa": 23.3, "fctm_mpa": 3.2, "ecm_gpa": 34, "verwendung": "Vorgespannte Bauteile, Brücken, Fertigteile"},
    {"klasse": "C40/50", "fck_mpa": 40, "fcd_mpa": 26.7, "fctm_mpa": 3.5, "ecm_gpa": 35, "verwendung": "Hochbau-Sonderbauteile, Hochleistungsbeton"},
    {"klasse": "C50/60", "fck_mpa": 50, "fcd_mpa": 33.3, "fctm_mpa": 4.1, "ecm_gpa": 37, "verwendung": "Hochleistungsbeton, Hochhäuser, Spezialbauten"},
]

HOLZKLASSEN = [
    {"klasse": "C14", "fm_mpa": 14, "ft0_mpa": 7.2, "fc0_mpa": 16, "e0_gpa": 7.0, "rho_kg_m3": 290, "verwendung": "Einfache tragende Bauteile, temporäre Konstruktionen"},
    {"klasse": "C16", "fm_mpa": 16, "ft0_mpa": 8.5, "fc0_mpa": 17, "e0_gpa": 8.0, "rho_kg_m3": 310, "verwendung": "Dachlatten, leichte Tragkonstruktionen"},
    {"klasse": "C20", "fm_mpa": 20, "ft0_mpa": 11.5, "fc0_mpa": 19, "e0_gpa": 9.5, "rho_kg_m3": 330, "verwendung": "Sparren, Pfetten, Deckenbalken (Wohnbau Standard)"},
    {"klasse": "C24", "fm_mpa": 24, "ft0_mpa": 14.0, "fc0_mpa": 21, "e0_gpa": 11.0, "rho_kg_m3": 350, "verwendung": "Standard-Bauholz: Sparren, Pfetten, Deckenbalken, Stützen"},
    {"klasse": "C27", "fm_mpa": 27, "ft0_mpa": 16.0, "fc0_mpa": 22, "e0_gpa": 11.5, "rho_kg_m3": 370, "verwendung": "Höher belastete Bauteile, Holzrahmenbau"},
    {"klasse": "C30", "fm_mpa": 30, "ft0_mpa": 18.0, "fc0_mpa": 23, "e0_gpa": 12.0, "rho_kg_m3": 380, "verwendung": "Ingenieurholzbau, Brettschichtholz-Äquivalent"},
    {"klasse": "GL24h", "fm_mpa": 24, "ft0_mpa": 19.2, "fc0_mpa": 24, "e0_gpa": 11.5, "rho_kg_m3": 385, "verwendung": "Brettschichtholz (BSH): Binder, Träger, Stützen"},
    {"klasse": "GL28h", "fm_mpa": 28, "ft0_mpa": 22.3, "fc0_mpa": 26.5, "e0_gpa": 12.6, "rho_kg_m3": 410, "verwendung": "BSH: Weitgespannte Träger, Hallenbau"},
    {"klasse": "GL32h", "fm_mpa": 32, "ft0_mpa": 25.6, "fc0_mpa": 29, "e0_gpa": 13.7, "rho_kg_m3": 430, "verwendung": "BSH: Hochbelastete Bauteile, große Spannweiten"},
]

BEWEHRUNGSSTAHL = [
    {"bezeichnung": "B 550 A (Stabstahl)", "fyk_mpa": 550, "ftk_mpa": 605, "es_gpa": 200, "durchmesser_mm": "6, 8, 10, 12, 14, 16, 20, 25, 28, 32"},
    {"bezeichnung": "B 550 B (Mattenstahl)", "fyk_mpa": 550, "ftk_mpa": 605, "es_gpa": 200, "durchmesser_mm": "4, 5, 6, 7, 8, 9, 10, 12"},
]

BEWEHRUNGSQUERSCHNITTE = [
    {"durchmesser_mm": 6, "as_cm2": 0.283, "gewicht_kg_m": 0.222},
    {"durchmesser_mm": 8, "as_cm2": 0.503, "gewicht_kg_m": 0.395},
    {"durchmesser_mm": 10, "as_cm2": 0.785, "gewicht_kg_m": 0.617},
    {"durchmesser_mm": 12, "as_cm2": 1.131, "gewicht_kg_m": 0.888},
    {"durchmesser_mm": 14, "as_cm2": 1.539, "gewicht_kg_m": 1.208},
    {"durchmesser_mm": 16, "as_cm2": 2.011, "gewicht_kg_m": 1.578},
    {"durchmesser_mm": 20, "as_cm2": 3.142, "gewicht_kg_m": 2.466},
    {"durchmesser_mm": 25, "as_cm2": 4.909, "gewicht_kg_m": 3.853},
    {"durchmesser_mm": 28, "as_cm2": 6.158, "gewicht_kg_m": 4.834},
    {"durchmesser_mm": 32, "as_cm2": 8.042, "gewicht_kg_m": 6.313},
]

TAUPUNKT_MATERIALIEN = {
    "beton": {"name": "Stahlbeton", "lambda_w_mk": 2.3, "mu": 80, "rho_kg_m3": 2400},
    "ziegel": {"name": "Hochlochziegel", "lambda_w_mk": 0.36, "mu": 10, "rho_kg_m3": 800},
    "porenbeton": {"name": "Porenbeton", "lambda_w_mk": 0.16, "mu": 8, "rho_kg_m3": 500},
    "vollholz": {"name": "Vollholz (Fichte)", "lambda_w_mk": 0.13, "mu": 40, "rho_kg_m3": 450},
    "eps": {"name": "EPS Dämmung", "lambda_w_mk": 0.035, "mu": 30, "rho_kg_m3": 20},
    "xps": {"name": "XPS Dämmung", "lambda_w_mk": 0.035, "mu": 100, "rho_kg_m3": 35},
    "mineralwolle": {"name": "Mineralwolle", "lambda_w_mk": 0.035, "mu": 1, "rho_kg_m3": 30},
    "steinwolle": {"name": "Steinwolle", "lambda_w_mk": 0.036, "mu": 1, "rho_kg_m3": 40},
    "holzfaser": {"name": "Holzfaserdämmplatte", "lambda_w_mk": 0.042, "mu": 5, "rho_kg_m3": 160},
    "gipskarton": {"name": "Gipskartonplatte", "lambda_w_mk": 0.25, "mu": 8, "rho_kg_m3": 900},
    "gipsfaser": {"name": "Gipsfaserplatte", "lambda_w_mk": 0.32, "mu": 13, "rho_kg_m3": 1100},
    "kalkzement_putz": {"name": "Kalk-Zement-Putz", "lambda_w_mk": 0.87, "mu": 20, "rho_kg_m3": 1800},
    "kalkputz": {"name": "Kalkputz (innen)", "lambda_w_mk": 0.70, "mu": 7, "rho_kg_m3": 1600},
    "dampfsperre": {"name": "Dampfsperre (PE-Folie)", "lambda_w_mk": 0.50, "mu": 100000, "rho_kg_m3": 950},
    "dampfbremse": {"name": "Dampfbremse (variabel)", "lambda_w_mk": 0.50, "mu": 2000, "rho_kg_m3": 950},
    "osb": {"name": "OSB-Platte", "lambda_w_mk": 0.13, "mu": 200, "rho_kg_m3": 600},
    "zellulose": {"name": "Zellulosedämmung", "lambda_w_mk": 0.040, "mu": 2, "rho_kg_m3": 50},
    "schaumglas": {"name": "Schaumglas", "lambda_w_mk": 0.040, "mu": 100000, "rho_kg_m3": 115},
}

SCHALLSCHUTZ_ANFORDERUNGEN = {
    "wohnungstrennwand": {
        "bauteil": "Wohnungstrennwand",
        "rw_min_db": 55,
        "beschreibung": "Wand zwischen zwei Wohneinheiten",
        "empfehlung": "≥ 57 dB für erhöhten Komfort",
    },
    "wohnungstrenndecke": {
        "bauteil": "Wohnungstrenndecke",
        "rw_min_db": 55,
        "ln_max_db": 48,
        "beschreibung": "Decke zwischen Wohneinheiten (Luft + Trittschall)",
        "empfehlung": "≥ 57 dB Luft, ≤ 46 dB Tritt für Komfort",
    },
    "treppenhaus_wand": {
        "bauteil": "Treppenhauswand",
        "rw_min_db": 55,
        "beschreibung": "Wand zwischen Wohnung und Stiegenhaus",
        "empfehlung": "≥ 57 dB empfohlen",
    },
    "treppenhaus_decke": {
        "bauteil": "Treppenhausdecke/Podest",
        "rw_min_db": 55,
        "ln_max_db": 48,
        "beschreibung": "Decke/Podest zu Wohnungen",
        "empfehlung": "Schwimmender Estrich erforderlich",
    },
    "aussenwand": {
        "bauteil": "Außenwand",
        "rw_min_db": 43,
        "beschreibung": "Je nach Lärmpegelbereich (I-VII)",
        "empfehlung": "Höhere Werte bei Straßenlärm nötig",
    },
    "innenwand_gleiche_wohnung": {
        "bauteil": "Innenwand (gleiche Wohnung)",
        "rw_min_db": 40,
        "beschreibung": "Zwischen Räumen derselben Wohnung",
        "empfehlung": "Keine gesetzl. Anforderung, 40 dB empfohlen",
    },
    "keller_wohndecke": {
        "bauteil": "Kellerdecke zu Wohnung",
        "rw_min_db": 55,
        "ln_max_db": 48,
        "beschreibung": "Decke zwischen Keller/Tiefgarage und Wohnung",
        "empfehlung": "Besondere Beachtung bei Tiefgaragen",
    },
    "dach": {
        "bauteil": "Dach/oberste Decke",
        "rw_min_db": 45,
        "beschreibung": "Schutz gegen Außenlärm und Regen",
        "empfehlung": "Abhängig von Fluglärmzone",
    },
}

SCHALLSCHUTZ_BAUTEILE = [
    {"bauteil": "11.5 cm Gipskartonwand (Metallständer, 1-fach beplankt)", "rw_db": 37, "flaechen_masse_kg_m2": 25, "typ": "leicht"},
    {"bauteil": "12.5 cm Gipskartonwand (Metallständer, 2-fach beplankt)", "rw_db": 45, "flaechen_masse_kg_m2": 42, "typ": "leicht"},
    {"bauteil": "15 cm Gipskartonwand (Metallständer, 2-fach beplankt, Mineralwolle)", "rw_db": 52, "flaechen_masse_kg_m2": 48, "typ": "leicht"},
    {"bauteil": "17.5 cm Doppelständer-Wand (2x2-fach beplankt, Mineralwolle)", "rw_db": 62, "flaechen_masse_kg_m2": 72, "typ": "leicht"},
    {"bauteil": "11.5 cm Hochlochziegel (verputzt)", "rw_db": 42, "flaechen_masse_kg_m2": 130, "typ": "massiv"},
    {"bauteil": "17.5 cm Hochlochziegel (verputzt)", "rw_db": 47, "flaechen_masse_kg_m2": 200, "typ": "massiv"},
    {"bauteil": "25 cm Hochlochziegel (verputzt)", "rw_db": 52, "flaechen_masse_kg_m2": 300, "typ": "massiv"},
    {"bauteil": "30 cm Hochlochziegel (verputzt)", "rw_db": 55, "flaechen_masse_kg_m2": 370, "typ": "massiv"},
    {"bauteil": "38 cm Hochlochziegel (verputzt)", "rw_db": 58, "flaechen_masse_kg_m2": 475, "typ": "massiv"},
    {"bauteil": "20 cm Stahlbeton", "rw_db": 57, "flaechen_masse_kg_m2": 480, "typ": "massiv"},
    {"bauteil": "25 cm Stahlbeton", "rw_db": 60, "flaechen_masse_kg_m2": 600, "typ": "massiv"},
    {"bauteil": "18 cm Stahlbetondecke + schw. Estrich", "rw_db": 56, "flaechen_masse_kg_m2": 520, "typ": "decke", "ln_db": 46},
    {"bauteil": "20 cm Stahlbetondecke + schw. Estrich", "rw_db": 58, "flaechen_masse_kg_m2": 570, "typ": "decke", "ln_db": 44},
    {"bauteil": "22 cm Stahlbetondecke + schw. Estrich", "rw_db": 60, "flaechen_masse_kg_m2": 620, "typ": "decke", "ln_db": 42},
    {"bauteil": "25 cm Stahlbetondecke + schw. Estrich", "rw_db": 62, "flaechen_masse_kg_m2": 700, "typ": "decke", "ln_db": 40},
    {"bauteil": "Holzbalkendecke (Schüttung + Estrich)", "rw_db": 52, "flaechen_masse_kg_m2": 120, "typ": "decke", "ln_db": 54},
    {"bauteil": "Holzbalkendecke (BSP + schw. Estrich)", "rw_db": 56, "flaechen_masse_kg_m2": 200, "typ": "decke", "ln_db": 48},
]

GEBAEUEDEKLASSEN_OIB = {
    "gk1": {
        "klasse": "GK 1",
        "beschreibung": "Freistehende Gebäude mit max. 2 Wohnungen, max. 400 m² je Geschoß, Fluchtniveau ≤ 7 m",
        "beispiele": "Einfamilienhaus, Doppelhaushälfte",
        "anforderungen": {
            "tragende_waende": "R 30 (brennbar zulässig)",
            "tragende_decken": "REI 30 (brennbar zulässig)",
            "trennwaende": "Keine Anforderung",
            "aussenwand_bekleidung": "Keine Anforderung",
            "dach": "Harte Bedachung empfohlen",
            "fluchtweg_laenge": "40 m",
            "rauchmelder": "Ja, in allen Aufenthaltsräumen + Fluren",
        },
    },
    "gk2": {
        "klasse": "GK 2",
        "beschreibung": "Gebäude mit max. 3 oberirdischen Geschoßen, Fluchtniveau ≤ 7 m",
        "beispiele": "Kleines Mehrfamilienhaus (3 Geschoße), Reihenhaus",
        "anforderungen": {
            "tragende_waende": "R 60 / REI 60 (brennbar mit Einschränkungen)",
            "tragende_decken": "REI 60",
            "trennwaende": "EI 30 (nicht brennbar empfohlen)",
            "aussenwand_bekleidung": "Schwer brennbar (B1/C-s2,d0)",
            "dach": "Harte Bedachung",
            "fluchtweg_laenge": "40 m",
            "rauchmelder": "Ja, in allen Aufenthaltsräumen + Fluren",
        },
    },
    "gk3": {
        "klasse": "GK 3",
        "beschreibung": "Gebäude mit Fluchtniveau ≤ 11 m, nicht GK1/GK2",
        "beispiele": "Mehrfamilienhaus bis 4 Geschoße, Bürogebäude",
        "anforderungen": {
            "tragende_waende": "R 90 / REI 90 (nicht brennbar — A2)",
            "tragende_decken": "REI 90 (nicht brennbar — A2)",
            "trennwaende": "EI 60 (nicht brennbar)",
            "aussenwand_bekleidung": "Nicht brennbar (A2-s1,d0)",
            "dach": "Nicht brennbar oder mit Brandabschnitten",
            "fluchtweg_laenge": "35 m",
            "rauchmelder": "Ja + Brandmeldeanlage bei > 800 m²",
        },
    },
    "gk4": {
        "klasse": "GK 4",
        "beschreibung": "Gebäude mit Fluchtniveau ≤ 22 m",
        "beispiele": "Wohnhochhaus bis ca. 7 Geschoße, größere Bürogebäude",
        "anforderungen": {
            "tragende_waende": "R 90 / REI 90 (nicht brennbar — A2)",
            "tragende_decken": "REI 90 (nicht brennbar — A2)",
            "trennwaende": "EI 90 (nicht brennbar)",
            "aussenwand_bekleidung": "Nicht brennbar (A2-s1,d0)",
            "dach": "Nicht brennbar (A2)",
            "fluchtweg_laenge": "35 m",
            "rauchmelder": "Brandmeldeanlage (BMA) + Rauchabzug in Stiegenhäusern",
        },
    },
    "gk5": {
        "klasse": "GK 5",
        "beschreibung": "Gebäude mit Fluchtniveau > 22 m (Hochhaus)",
        "beispiele": "Hochhäuser, Bürotürme",
        "anforderungen": {
            "tragende_waende": "R 90 / REI 90 (nicht brennbar — A1/A2)",
            "tragende_decken": "REI 90 (nicht brennbar — A1/A2)",
            "trennwaende": "EI 90 (nicht brennbar)",
            "aussenwand_bekleidung": "Nicht brennbar (A1/A2-s1,d0)",
            "dach": "Nicht brennbar (A1)",
            "fluchtweg_laenge": "35 m + 2 Fluchttreppenhäuser",
            "rauchmelder": "BMA + Sprinkleranlage + Druckbelüftung Stiegenhäuser",
        },
    },
}

BRANDSCHUTZ_FEUERWIDERSTAND = [
    {"bezeichnung": "R 30", "dauer_min": 30, "beschreibung": "Tragfähigkeit 30 Min.", "anwendung": "GK 1, untergeordnete Bauteile"},
    {"bezeichnung": "R 60", "dauer_min": 60, "beschreibung": "Tragfähigkeit 60 Min.", "anwendung": "GK 2, Wohnbau"},
    {"bezeichnung": "R 90", "dauer_min": 90, "beschreibung": "Tragfähigkeit 90 Min.", "anwendung": "GK 3-5, Hochhäuser"},
    {"bezeichnung": "REI 30", "dauer_min": 30, "beschreibung": "Tragfähigkeit + Raumabschluss + Wärmedämmung 30 Min.", "anwendung": "Decken GK 1"},
    {"bezeichnung": "REI 60", "dauer_min": 60, "beschreibung": "Tragfähigkeit + Raumabschluss + Wärmedämmung 60 Min.", "anwendung": "Decken GK 2"},
    {"bezeichnung": "REI 90", "dauer_min": 90, "beschreibung": "Tragfähigkeit + Raumabschluss + Wärmedämmung 90 Min.", "anwendung": "Decken GK 3-5"},
    {"bezeichnung": "EI 30", "dauer_min": 30, "beschreibung": "Raumabschluss + Wärmedämmung 30 Min.", "anwendung": "Trennwände GK 2"},
    {"bezeichnung": "EI 60", "dauer_min": 60, "beschreibung": "Raumabschluss + Wärmedämmung 60 Min.", "anwendung": "Trennwände GK 3"},
    {"bezeichnung": "EI 90", "dauer_min": 90, "beschreibung": "Raumabschluss + Wärmedämmung 90 Min.", "anwendung": "Trennwände GK 4-5, Brandwände"},
]

BRANDKLASSEN_BAUSTOFFE = [
    {"euroklasse": "A1", "oenorm": "nicht brennbar", "beispiele": "Stahl, Beton, Ziegel, Stein, Glas, Mineralwolle", "rauchentwicklung": "keine"},
    {"euroklasse": "A2-s1,d0", "oenorm": "nicht brennbar", "beispiele": "Gipskarton, Gipsfaser, Steinwolle mit Bindemittel", "rauchentwicklung": "gering"},
    {"euroklasse": "B-s1,d0", "oenorm": "schwer brennbar", "beispiele": "Bestimmte Holzwerkstoffe mit Brandschutz, PVC-Böden", "rauchentwicklung": "gering"},
    {"euroklasse": "C-s2,d0", "oenorm": "schwer brennbar", "beispiele": "Hartholz ≥18mm, manche Dämmstoffe", "rauchentwicklung": "mittel"},
    {"euroklasse": "D-s2,d0", "oenorm": "normal brennbar", "beispiele": "Nadelholz, Holzwerkstoffe, OSB", "rauchentwicklung": "mittel"},
    {"euroklasse": "E", "oenorm": "normal brennbar", "beispiele": "EPS-Dämmung (mit Flammschutzmittel)", "rauchentwicklung": "hoch"},
    {"euroklasse": "F", "oenorm": "leicht brennbar", "beispiele": "Ungeschütztes EPS, PU-Schaum", "rauchentwicklung": "sehr hoch"},
]

BAUBOOK_MATERIALIEN = {
    "daemmstoffe": {
        "kategorie": "Dämmstoffe",
        "materialien": [
            {"name": "EPS (Styropor) WLG 035", "lambda": 0.035, "mu": 30, "rho": 20, "brandklasse": "E", "oi3": 7.5, "gwp_kg_co2": 3.3, "pei_mj": 105, "kosten_eur_m2_10cm": 8, "oekologisch": False},
            {"name": "EPS (Styropor) WLG 032", "lambda": 0.032, "mu": 30, "rho": 18, "brandklasse": "E", "oi3": 8.0, "gwp_kg_co2": 3.5, "pei_mj": 110, "kosten_eur_m2_10cm": 10, "oekologisch": False},
            {"name": "XPS (Styrodur)", "lambda": 0.035, "mu": 100, "rho": 35, "brandklasse": "E", "oi3": 9.2, "gwp_kg_co2": 4.8, "pei_mj": 140, "kosten_eur_m2_10cm": 18, "oekologisch": False},
            {"name": "Mineralwolle (Glaswolle)", "lambda": 0.035, "mu": 1, "rho": 30, "brandklasse": "A1", "oi3": 4.2, "gwp_kg_co2": 1.5, "pei_mj": 45, "kosten_eur_m2_10cm": 9, "oekologisch": False},
            {"name": "Steinwolle", "lambda": 0.036, "mu": 1, "rho": 40, "brandklasse": "A1", "oi3": 4.8, "gwp_kg_co2": 1.8, "pei_mj": 55, "kosten_eur_m2_10cm": 11, "oekologisch": False},
            {"name": "Steinwolle (Fassade, 140 kg/m³)", "lambda": 0.036, "mu": 1, "rho": 140, "brandklasse": "A1", "oi3": 5.5, "gwp_kg_co2": 2.2, "pei_mj": 70, "kosten_eur_m2_10cm": 20, "oekologisch": False},
            {"name": "PUR/PIR Hartschaum", "lambda": 0.024, "mu": 60, "rho": 32, "brandklasse": "B-s1,d0", "oi3": 10.5, "gwp_kg_co2": 5.2, "pei_mj": 160, "kosten_eur_m2_10cm": 22, "oekologisch": False},
            {"name": "Holzfaserdämmplatte (flex)", "lambda": 0.040, "mu": 5, "rho": 50, "brandklasse": "E", "oi3": 1.2, "gwp_kg_co2": -1.1, "pei_mj": 20, "kosten_eur_m2_10cm": 14, "oekologisch": True},
            {"name": "Holzfaserdämmplatte (steif)", "lambda": 0.042, "mu": 5, "rho": 160, "brandklasse": "E", "oi3": 1.8, "gwp_kg_co2": -0.8, "pei_mj": 28, "kosten_eur_m2_10cm": 18, "oekologisch": True},
            {"name": "Zellulosedämmung (Einblas)", "lambda": 0.040, "mu": 2, "rho": 50, "brandklasse": "B-s2,d0", "oi3": 0.8, "gwp_kg_co2": -1.5, "pei_mj": 12, "kosten_eur_m2_10cm": 10, "oekologisch": True},
            {"name": "Hanffaser-Dämmung", "lambda": 0.040, "mu": 2, "rho": 35, "brandklasse": "E", "oi3": 0.6, "gwp_kg_co2": -1.8, "pei_mj": 10, "kosten_eur_m2_10cm": 16, "oekologisch": True},
            {"name": "Flachsfaser-Dämmung", "lambda": 0.040, "mu": 2, "rho": 30, "brandklasse": "E", "oi3": 0.7, "gwp_kg_co2": -1.6, "pei_mj": 11, "kosten_eur_m2_10cm": 18, "oekologisch": True},
            {"name": "Schafwolle-Dämmung", "lambda": 0.040, "mu": 3, "rho": 25, "brandklasse": "B-s1,d0", "oi3": 0.5, "gwp_kg_co2": -0.9, "pei_mj": 8, "kosten_eur_m2_10cm": 22, "oekologisch": True},
            {"name": "Korkdämmung (expandiert)", "lambda": 0.045, "mu": 10, "rho": 120, "brandklasse": "E", "oi3": 1.0, "gwp_kg_co2": -1.2, "pei_mj": 15, "kosten_eur_m2_10cm": 28, "oekologisch": True},
            {"name": "Schaumglas (Foamglas)", "lambda": 0.040, "mu": 100000, "rho": 115, "brandklasse": "A1", "oi3": 8.5, "gwp_kg_co2": 3.0, "pei_mj": 90, "kosten_eur_m2_10cm": 35, "oekologisch": False},
            {"name": "Vakuum-Isolationspaneel (VIP)", "lambda": 0.007, "mu": 100000, "rho": 200, "brandklasse": "A2-s1,d0", "oi3": 12.0, "gwp_kg_co2": 6.5, "pei_mj": 200, "kosten_eur_m2_10cm": 120, "oekologisch": False},
            {"name": "Aerogel-Dämmung", "lambda": 0.015, "mu": 5, "rho": 150, "brandklasse": "A2-s1,d0", "oi3": 11.0, "gwp_kg_co2": 5.8, "pei_mj": 180, "kosten_eur_m2_10cm": 90, "oekologisch": False},
            {"name": "Perlite-Schüttung", "lambda": 0.050, "mu": 3, "rho": 90, "brandklasse": "A1", "oi3": 3.5, "gwp_kg_co2": 0.8, "pei_mj": 25, "kosten_eur_m2_10cm": 7, "oekologisch": False},
            {"name": "Blähton-Schüttung", "lambda": 0.100, "mu": 3, "rho": 350, "brandklasse": "A1", "oi3": 3.0, "gwp_kg_co2": 0.5, "pei_mj": 18, "kosten_eur_m2_10cm": 6, "oekologisch": False},
        ],
    },
    "mauerwerk": {
        "kategorie": "Mauerwerk",
        "materialien": [
            {"name": "Hochlochziegel 25 cm", "lambda": 0.290, "mu": 10, "rho": 800, "brandklasse": "A1", "oi3": 2.5, "gwp_kg_co2": 0.22, "pei_mj": 3.8, "kosten_eur_m2": 35, "oekologisch": False},
            {"name": "Hochlochziegel 30 cm", "lambda": 0.230, "mu": 10, "rho": 750, "brandklasse": "A1", "oi3": 2.8, "gwp_kg_co2": 0.24, "pei_mj": 4.0, "kosten_eur_m2": 42, "oekologisch": False},
            {"name": "Hochlochziegel 38 cm", "lambda": 0.170, "mu": 10, "rho": 700, "brandklasse": "A1", "oi3": 3.2, "gwp_kg_co2": 0.26, "pei_mj": 4.5, "kosten_eur_m2": 52, "oekologisch": False},
            {"name": "Hochlochziegel 50 cm (plangeschliffen)", "lambda": 0.080, "mu": 10, "rho": 600, "brandklasse": "A1", "oi3": 3.8, "gwp_kg_co2": 0.28, "pei_mj": 5.0, "kosten_eur_m2": 68, "oekologisch": False},
            {"name": "Wärmedämmziegel (gefüllt)", "lambda": 0.075, "mu": 10, "rho": 650, "brandklasse": "A1", "oi3": 4.5, "gwp_kg_co2": 0.35, "pei_mj": 6.5, "kosten_eur_m2": 75, "oekologisch": False},
            {"name": "Vollziegel (Normalformat)", "lambda": 0.680, "mu": 10, "rho": 1800, "brandklasse": "A1", "oi3": 2.0, "gwp_kg_co2": 0.20, "pei_mj": 3.5, "kosten_eur_m2": 30, "oekologisch": False},
            {"name": "Kalksandstein 17.5 cm", "lambda": 0.700, "mu": 15, "rho": 1600, "brandklasse": "A1", "oi3": 1.8, "gwp_kg_co2": 0.14, "pei_mj": 2.5, "kosten_eur_m2": 28, "oekologisch": False},
            {"name": "Kalksandstein 24 cm", "lambda": 0.990, "mu": 15, "rho": 1800, "brandklasse": "A1", "oi3": 2.0, "gwp_kg_co2": 0.16, "pei_mj": 2.8, "kosten_eur_m2": 35, "oekologisch": False},
            {"name": "Porenbeton 20 cm (P2-0,35)", "lambda": 0.090, "mu": 8, "rho": 350, "brandklasse": "A1", "oi3": 3.5, "gwp_kg_co2": 0.30, "pei_mj": 4.0, "kosten_eur_m2": 32, "oekologisch": False},
            {"name": "Porenbeton 30 cm (P2-0,35)", "lambda": 0.090, "mu": 8, "rho": 350, "brandklasse": "A1", "oi3": 4.0, "gwp_kg_co2": 0.35, "pei_mj": 5.0, "kosten_eur_m2": 45, "oekologisch": False},
            {"name": "Porenbeton 36.5 cm (P2-0,30)", "lambda": 0.080, "mu": 8, "rho": 300, "brandklasse": "A1", "oi3": 4.5, "gwp_kg_co2": 0.38, "pei_mj": 5.5, "kosten_eur_m2": 55, "oekologisch": False},
            {"name": "Leichtbeton-Hohlblock 20 cm", "lambda": 0.550, "mu": 10, "rho": 1200, "brandklasse": "A1", "oi3": 3.0, "gwp_kg_co2": 0.18, "pei_mj": 3.0, "kosten_eur_m2": 22, "oekologisch": False},
        ],
    },
    "beton": {
        "kategorie": "Beton & Stahlbeton",
        "materialien": [
            {"name": "Normalbeton C20/25", "lambda": 2.100, "mu": 80, "rho": 2400, "brandklasse": "A1", "oi3": 3.8, "gwp_kg_co2": 0.13, "pei_mj": 1.2, "kosten_eur_m3": 120, "oekologisch": False},
            {"name": "Normalbeton C25/30", "lambda": 2.100, "mu": 80, "rho": 2400, "brandklasse": "A1", "oi3": 4.0, "gwp_kg_co2": 0.14, "pei_mj": 1.3, "kosten_eur_m3": 130, "oekologisch": False},
            {"name": "Stahlbeton (2% Bewehrung)", "lambda": 2.300, "mu": 100, "rho": 2500, "brandklasse": "A1", "oi3": 5.5, "gwp_kg_co2": 0.22, "pei_mj": 2.5, "kosten_eur_m3": 250, "oekologisch": False},
            {"name": "Leichtbeton", "lambda": 0.700, "mu": 50, "rho": 1400, "brandklasse": "A1", "oi3": 3.0, "gwp_kg_co2": 0.10, "pei_mj": 1.0, "kosten_eur_m3": 140, "oekologisch": False},
            {"name": "Dämmbeton", "lambda": 0.300, "mu": 30, "rho": 800, "brandklasse": "A1", "oi3": 3.5, "gwp_kg_co2": 0.15, "pei_mj": 1.5, "kosten_eur_m3": 180, "oekologisch": False},
            {"name": "Recycling-Beton", "lambda": 2.100, "mu": 80, "rho": 2350, "brandklasse": "A1", "oi3": 2.5, "gwp_kg_co2": 0.09, "pei_mj": 0.8, "kosten_eur_m3": 115, "oekologisch": True},
        ],
    },
    "holz": {
        "kategorie": "Holz & Holzwerkstoffe",
        "materialien": [
            {"name": "Fichtenholz (Konstruktionsholz C24)", "lambda": 0.130, "mu": 40, "rho": 450, "brandklasse": "D-s2,d0", "oi3": 0.3, "gwp_kg_co2": -1.6, "pei_mj": 5.0, "kosten_eur_m3": 450, "oekologisch": True},
            {"name": "Brettsperrholz (CLT)", "lambda": 0.130, "mu": 50, "rho": 470, "brandklasse": "D-s2,d0", "oi3": 0.5, "gwp_kg_co2": -1.5, "pei_mj": 8.0, "kosten_eur_m3": 650, "oekologisch": True},
            {"name": "Brettschichtholz (BSH) GL24h", "lambda": 0.130, "mu": 50, "rho": 420, "brandklasse": "D-s2,d0", "oi3": 0.4, "gwp_kg_co2": -1.4, "pei_mj": 7.5, "kosten_eur_m3": 600, "oekologisch": True},
            {"name": "OSB-Platte", "lambda": 0.130, "mu": 200, "rho": 600, "brandklasse": "D-s2,d0", "oi3": 1.5, "gwp_kg_co2": -0.8, "pei_mj": 12, "kosten_eur_m2_cm": 1.2, "oekologisch": True},
            {"name": "Sperrholz (Birke)", "lambda": 0.150, "mu": 200, "rho": 680, "brandklasse": "D-s2,d0", "oi3": 1.8, "gwp_kg_co2": -0.7, "pei_mj": 14, "kosten_eur_m2_cm": 2.5, "oekologisch": True},
            {"name": "MDF-Platte", "lambda": 0.140, "mu": 20, "rho": 750, "brandklasse": "D-s2,d0", "oi3": 2.5, "gwp_kg_co2": -0.3, "pei_mj": 20, "kosten_eur_m2_cm": 1.0, "oekologisch": False},
            {"name": "Spanplatte", "lambda": 0.130, "mu": 30, "rho": 650, "brandklasse": "D-s2,d0", "oi3": 2.8, "gwp_kg_co2": -0.2, "pei_mj": 18, "kosten_eur_m2_cm": 0.8, "oekologisch": False},
            {"name": "Eichenholz (Hartholz)", "lambda": 0.200, "mu": 50, "rho": 700, "brandklasse": "C-s2,d0", "oi3": 0.4, "gwp_kg_co2": -1.7, "pei_mj": 6.0, "kosten_eur_m3": 1200, "oekologisch": True},
            {"name": "Lärche (Fassade/Terrasse)", "lambda": 0.130, "mu": 40, "rho": 550, "brandklasse": "D-s2,d0", "oi3": 0.3, "gwp_kg_co2": -1.5, "pei_mj": 5.5, "kosten_eur_m3": 800, "oekologisch": True},
        ],
    },
    "putze_moertel": {
        "kategorie": "Putze & Mörtel",
        "materialien": [
            {"name": "Kalkputz (innen)", "lambda": 0.700, "mu": 7, "rho": 1600, "brandklasse": "A1", "oi3": 1.5, "gwp_kg_co2": 0.12, "pei_mj": 1.5, "kosten_eur_m2_cm": 3.5, "oekologisch": True},
            {"name": "Kalk-Zement-Putz", "lambda": 0.870, "mu": 20, "rho": 1800, "brandklasse": "A1", "oi3": 2.0, "gwp_kg_co2": 0.18, "pei_mj": 2.2, "kosten_eur_m2_cm": 3.0, "oekologisch": False},
            {"name": "Zementputz", "lambda": 1.400, "mu": 25, "rho": 2000, "brandklasse": "A1", "oi3": 2.5, "gwp_kg_co2": 0.22, "pei_mj": 2.8, "kosten_eur_m2_cm": 2.5, "oekologisch": False},
            {"name": "Lehmputz", "lambda": 0.700, "mu": 5, "rho": 1500, "brandklasse": "A1", "oi3": 0.3, "gwp_kg_co2": 0.01, "pei_mj": 0.5, "kosten_eur_m2_cm": 8.0, "oekologisch": True},
            {"name": "Wärmedämmputz", "lambda": 0.090, "mu": 8, "rho": 400, "brandklasse": "A2-s1,d0", "oi3": 3.0, "gwp_kg_co2": 0.15, "pei_mj": 2.0, "kosten_eur_m2_cm": 6.0, "oekologisch": False},
            {"name": "Silikonharzputz (Fassade)", "lambda": 0.870, "mu": 30, "rho": 1800, "brandklasse": "A2-s1,d0", "oi3": 3.5, "gwp_kg_co2": 0.25, "pei_mj": 3.5, "kosten_eur_m2_cm": 5.0, "oekologisch": False},
            {"name": "Silikatputz (Fassade)", "lambda": 0.870, "mu": 20, "rho": 1800, "brandklasse": "A1", "oi3": 2.5, "gwp_kg_co2": 0.20, "pei_mj": 3.0, "kosten_eur_m2_cm": 5.5, "oekologisch": False},
        ],
    },
    "platten_trockenbau": {
        "kategorie": "Platten & Trockenbau",
        "materialien": [
            {"name": "Gipskartonplatte (GKB) 12.5mm", "lambda": 0.250, "mu": 8, "rho": 900, "brandklasse": "A2-s1,d0", "oi3": 2.0, "gwp_kg_co2": 0.12, "pei_mj": 3.5, "kosten_eur_m2": 4.5, "oekologisch": False},
            {"name": "Gipsfaserplatte (GF) 12.5mm", "lambda": 0.320, "mu": 13, "rho": 1100, "brandklasse": "A2-s1,d0", "oi3": 2.2, "gwp_kg_co2": 0.14, "pei_mj": 4.0, "kosten_eur_m2": 7.0, "oekologisch": False},
            {"name": "Feuchtraum-Gipskarton (GKBI)", "lambda": 0.250, "mu": 8, "rho": 900, "brandklasse": "A2-s1,d0", "oi3": 2.5, "gwp_kg_co2": 0.15, "pei_mj": 4.0, "kosten_eur_m2": 6.0, "oekologisch": False},
            {"name": "Brandschutz-Gipskarton (GKF) 15mm", "lambda": 0.250, "mu": 8, "rho": 950, "brandklasse": "A2-s1,d0", "oi3": 2.5, "gwp_kg_co2": 0.14, "pei_mj": 4.0, "kosten_eur_m2": 8.0, "oekologisch": False},
            {"name": "Zementgebundene Platte", "lambda": 0.350, "mu": 50, "rho": 1400, "brandklasse": "A1", "oi3": 3.0, "gwp_kg_co2": 0.18, "pei_mj": 3.5, "kosten_eur_m2": 12.0, "oekologisch": False},
            {"name": "Lehmbauplatten", "lambda": 0.700, "mu": 5, "rho": 1500, "brandklasse": "A1", "oi3": 0.4, "gwp_kg_co2": 0.02, "pei_mj": 0.8, "kosten_eur_m2": 15.0, "oekologisch": True},
        ],
    },
    "abdichtung_folien": {
        "kategorie": "Abdichtung & Folien",
        "materialien": [
            {"name": "PE-Dampfsperre (sd > 100m)", "lambda": 0.500, "mu": 100000, "rho": 950, "brandklasse": "E", "oi3": 5.0, "gwp_kg_co2": 2.5, "pei_mj": 80, "kosten_eur_m2": 2.5, "oekologisch": False},
            {"name": "Variable Dampfbremse (sd 0,25-10m)", "lambda": 0.500, "mu": 2000, "rho": 950, "brandklasse": "E", "oi3": 4.5, "gwp_kg_co2": 2.0, "pei_mj": 60, "kosten_eur_m2": 4.0, "oekologisch": False},
            {"name": "Bitumenbahn V60 S4", "lambda": 0.170, "mu": 50000, "rho": 1100, "brandklasse": "E", "oi3": 6.0, "gwp_kg_co2": 1.8, "pei_mj": 45, "kosten_eur_m2": 8.0, "oekologisch": False},
            {"name": "Bitumen-Dachabdichtung (2-lagig)", "lambda": 0.170, "mu": 50000, "rho": 1100, "brandklasse": "E", "oi3": 7.0, "gwp_kg_co2": 2.2, "pei_mj": 55, "kosten_eur_m2": 18.0, "oekologisch": False},
            {"name": "EPDM-Folie (Flachdach)", "lambda": 0.250, "mu": 80000, "rho": 1200, "brandklasse": "E", "oi3": 5.5, "gwp_kg_co2": 2.8, "pei_mj": 90, "kosten_eur_m2": 12.0, "oekologisch": False},
            {"name": "Unterspannbahn (diffusionsoffen)", "lambda": 0.500, "mu": 100, "rho": 300, "brandklasse": "E", "oi3": 3.5, "gwp_kg_co2": 1.5, "pei_mj": 40, "kosten_eur_m2": 3.0, "oekologisch": False},
        ],
    },
    "estrich_boeden": {
        "kategorie": "Estrich & Böden",
        "materialien": [
            {"name": "Zementestrich", "lambda": 1.400, "mu": 30, "rho": 2000, "brandklasse": "A1", "oi3": 2.5, "gwp_kg_co2": 0.18, "pei_mj": 2.5, "kosten_eur_m2_cm": 3.0, "oekologisch": False},
            {"name": "Anhydrit-Fließestrich", "lambda": 1.200, "mu": 20, "rho": 1800, "brandklasse": "A1", "oi3": 2.0, "gwp_kg_co2": 0.12, "pei_mj": 1.8, "kosten_eur_m2_cm": 4.0, "oekologisch": False},
            {"name": "Trockenestrich (Gipsfaser)", "lambda": 0.320, "mu": 13, "rho": 1100, "brandklasse": "A2-s1,d0", "oi3": 2.2, "gwp_kg_co2": 0.14, "pei_mj": 3.5, "kosten_eur_m2": 14.0, "oekologisch": False},
            {"name": "Trittschalldämmung EPS-T", "lambda": 0.040, "mu": 30, "rho": 15, "brandklasse": "E", "oi3": 5.0, "gwp_kg_co2": 2.0, "pei_mj": 60, "kosten_eur_m2": 3.0, "oekologisch": False},
            {"name": "Trittschalldämmung Mineralwolle", "lambda": 0.040, "mu": 1, "rho": 100, "brandklasse": "A1", "oi3": 3.5, "gwp_kg_co2": 1.2, "pei_mj": 35, "kosten_eur_m2": 5.0, "oekologisch": False},
            {"name": "Trittschalldämmung Holzfaser", "lambda": 0.042, "mu": 5, "rho": 160, "brandklasse": "E", "oi3": 1.0, "gwp_kg_co2": -0.8, "pei_mj": 15, "kosten_eur_m2": 8.0, "oekologisch": True},
        ],
    },
    "fenster_glas": {
        "kategorie": "Fenster & Glas",
        "materialien": [
            {"name": "2-fach Wärmeschutzglas", "lambda": None, "mu": None, "rho": None, "brandklasse": "A1", "oi3": 6.0, "gwp_kg_co2": 1.8, "pei_mj": 35, "uw_gesamt": 1.3, "ug_wert": 1.1, "kosten_eur_m2": 120, "oekologisch": False},
            {"name": "3-fach Wärmeschutzglas", "lambda": None, "mu": None, "rho": None, "brandklasse": "A1", "oi3": 8.0, "gwp_kg_co2": 2.2, "pei_mj": 45, "uw_gesamt": 0.80, "ug_wert": 0.60, "kosten_eur_m2": 180, "oekologisch": False},
            {"name": "3-fach Passivhaus-Glas", "lambda": None, "mu": None, "rho": None, "brandklasse": "A1", "oi3": 9.0, "gwp_kg_co2": 2.5, "pei_mj": 50, "uw_gesamt": 0.65, "ug_wert": 0.50, "kosten_eur_m2": 250, "oekologisch": False},
            {"name": "Kunststoff-Fenster (PVC)", "lambda": None, "mu": None, "rho": None, "brandklasse": "B-s2,d0", "oi3": 8.0, "gwp_kg_co2": 3.5, "pei_mj": 80, "uf_wert": 1.3, "kosten_eur_m2": 200, "oekologisch": False},
            {"name": "Holz-Fenster (Fichte)", "lambda": None, "mu": None, "rho": None, "brandklasse": "D-s2,d0", "oi3": 2.0, "gwp_kg_co2": -0.5, "pei_mj": 15, "uf_wert": 1.4, "kosten_eur_m2": 350, "oekologisch": True},
            {"name": "Holz-Alu-Fenster", "lambda": None, "mu": None, "rho": None, "brandklasse": "D-s2,d0", "oi3": 4.0, "gwp_kg_co2": 0.8, "pei_mj": 35, "uf_wert": 1.2, "kosten_eur_m2": 450, "oekologisch": False},
            {"name": "Alu-Fenster", "lambda": None, "mu": None, "rho": None, "brandklasse": "A1", "oi3": 10.0, "gwp_kg_co2": 5.0, "pei_mj": 120, "uf_wert": 2.0, "kosten_eur_m2": 380, "oekologisch": False},
        ],
    },
    "metalle": {
        "kategorie": "Metalle",
        "materialien": [
            {"name": "Baustahl S235", "lambda": 50.0, "mu": None, "rho": 7850, "brandklasse": "A1", "oi3": 8.0, "gwp_kg_co2": 1.5, "pei_mj": 25, "kosten_eur_kg": 1.2, "oekologisch": False},
            {"name": "Edelstahl (rostfrei)", "lambda": 15.0, "mu": None, "rho": 7900, "brandklasse": "A1", "oi3": 12.0, "gwp_kg_co2": 4.5, "pei_mj": 55, "kosten_eur_kg": 5.0, "oekologisch": False},
            {"name": "Aluminium", "lambda": 160.0, "mu": None, "rho": 2700, "brandklasse": "A1", "oi3": 15.0, "gwp_kg_co2": 8.5, "pei_mj": 150, "kosten_eur_kg": 3.5, "oekologisch": False},
            {"name": "Kupfer (Dach/Fassade)", "lambda": 380.0, "mu": None, "rho": 8900, "brandklasse": "A1", "oi3": 18.0, "gwp_kg_co2": 3.8, "pei_mj": 60, "kosten_eur_kg": 8.0, "oekologisch": False},
            {"name": "Zink (Dach/Fassade)", "lambda": 110.0, "mu": None, "rho": 7135, "brandklasse": "A1", "oi3": 12.0, "gwp_kg_co2": 3.0, "pei_mj": 40, "kosten_eur_kg": 4.0, "oekologisch": False},
        ],
    },
    "naturstein": {
        "kategorie": "Naturstein & Keramik",
        "materialien": [
            {"name": "Granit", "lambda": 3.500, "mu": 10000, "rho": 2800, "brandklasse": "A1", "oi3": 1.5, "gwp_kg_co2": 0.06, "pei_mj": 1.0, "kosten_eur_m2_cm": 15, "oekologisch": True},
            {"name": "Kalkstein", "lambda": 2.300, "mu": 40, "rho": 2500, "brandklasse": "A1", "oi3": 1.2, "gwp_kg_co2": 0.04, "pei_mj": 0.8, "kosten_eur_m2_cm": 12, "oekologisch": True},
            {"name": "Sandstein", "lambda": 2.300, "mu": 30, "rho": 2200, "brandklasse": "A1", "oi3": 1.0, "gwp_kg_co2": 0.03, "pei_mj": 0.6, "kosten_eur_m2_cm": 10, "oekologisch": True},
            {"name": "Keramik-Fliese", "lambda": 1.000, "mu": 200, "rho": 2000, "brandklasse": "A1", "oi3": 5.0, "gwp_kg_co2": 0.55, "pei_mj": 10, "kosten_eur_m2": 25, "oekologisch": False},
            {"name": "Feinsteinzeug", "lambda": 1.300, "mu": 10000, "rho": 2300, "brandklasse": "A1", "oi3": 6.0, "gwp_kg_co2": 0.70, "pei_mj": 12, "kosten_eur_m2": 35, "oekologisch": False},
        ],
    },
}

ENERGIEAUSWEIS_KLASSEN = [
    {"klasse": "A++", "hwb_min": 0, "hwb_max": 10, "fgee_max": 0.55, "beschreibung": "Passivhaus", "farbe": "#00aa00", "sanierung": False, "foerderung": "Höchste Förderung, klimaaktiv Gold"},
    {"klasse": "A+", "hwb_min": 10, "hwb_max": 15, "fgee_max": 0.65, "beschreibung": "Passivhaus-nahe", "farbe": "#33bb00", "sanierung": False, "foerderung": "Sehr hohe Förderung"},
    {"klasse": "A", "hwb_min": 15, "hwb_max": 25, "fgee_max": 0.75, "beschreibung": "Niedrigenergiehaus", "farbe": "#66cc00", "sanierung": False, "foerderung": "Hohe Förderung, Neubau-Standard (ab 2025)"},
    {"klasse": "B", "hwb_min": 25, "hwb_max": 50, "fgee_max": 1.00, "beschreibung": "Energiesparhaus", "farbe": "#99dd00", "sanierung": False, "foerderung": "Gute Förderung, Neubau akzeptabel"},
    {"klasse": "C", "hwb_min": 50, "hwb_max": 100, "fgee_max": 1.50, "beschreibung": "Neubau-Standard (bis 2020)", "farbe": "#ffcc00", "sanierung": True, "foerderung": "Sanierung empfohlen, Förderung möglich"},
    {"klasse": "D", "hwb_min": 100, "hwb_max": 150, "fgee_max": 2.00, "beschreibung": "Sanierungsbedürftig", "farbe": "#ff9900", "sanierung": True, "foerderung": "Dringend: Sanierungsbonus nutzen!"},
    {"klasse": "E", "hwb_min": 150, "hwb_max": 200, "fgee_max": 2.50, "beschreibung": "Stark sanierungsbedürftig", "farbe": "#ff6600", "sanierung": True, "foerderung": "Hohe Förderung für umfassende Sanierung"},
    {"klasse": "F", "hwb_min": 200, "hwb_max": 250, "fgee_max": 3.00, "beschreibung": "Energetisch schlecht", "farbe": "#ff3300", "sanierung": True, "foerderung": "Dringende Sanierung, hohe Heizkosten"},
    {"klasse": "G", "hwb_min": 250, "hwb_max": 999, "fgee_max": 999, "beschreibung": "Energetisch kritisch", "farbe": "#cc0000", "sanierung": True, "foerderung": "Sofortige Maßnahmen empfohlen"},
]

ENERGIEAUSWEIS_UWERT_ANFORDERUNGEN = {
    "neubau": {
        "titel": "Neubau (OIB-RL 6:2023)",
        "anforderungen": [
            {"bauteil": "Außenwand", "uwert_max": 0.35, "empfehlung": 0.15, "einheit": "W/(m²·K)"},
            {"bauteil": "Oberste Geschoßdecke", "uwert_max": 0.20, "empfehlung": 0.10, "einheit": "W/(m²·K)"},
            {"bauteil": "Dach (beheizt)", "uwert_max": 0.20, "empfehlung": 0.10, "einheit": "W/(m²·K)"},
            {"bauteil": "Kellerdecke / Boden gg. Erdreich", "uwert_max": 0.40, "empfehlung": 0.18, "einheit": "W/(m²·K)"},
            {"bauteil": "Fenster / Fenstertüren", "uwert_max": 1.40, "empfehlung": 0.80, "einheit": "W/(m²·K)"},
            {"bauteil": "Haustür / Außentür", "uwert_max": 1.70, "empfehlung": 1.00, "einheit": "W/(m²·K)"},
            {"bauteil": "Wand gg. unbeheizt", "uwert_max": 0.60, "empfehlung": 0.30, "einheit": "W/(m²·K)"},
        ],
    },
    "sanierung": {
        "titel": "Sanierung (OIB-RL 6, Einzelmaßnahmen)",
        "anforderungen": [
            {"bauteil": "Außenwand", "uwert_max": 0.35, "empfehlung": 0.20, "einheit": "W/(m²·K)"},
            {"bauteil": "Oberste Geschoßdecke", "uwert_max": 0.20, "empfehlung": 0.12, "einheit": "W/(m²·K)"},
            {"bauteil": "Dach (beheizt)", "uwert_max": 0.20, "empfehlung": 0.12, "einheit": "W/(m²·K)"},
            {"bauteil": "Kellerdecke / Boden gg. Erdreich", "uwert_max": 0.40, "empfehlung": 0.22, "einheit": "W/(m²·K)"},
            {"bauteil": "Fenster / Fenstertüren", "uwert_max": 1.40, "empfehlung": 0.90, "einheit": "W/(m²·K)"},
            {"bauteil": "Haustür / Außentür", "uwert_max": 1.70, "empfehlung": 1.20, "einheit": "W/(m²·K)"},
        ],
    },
}

WOHNBAUFOERDERUNG_DETAIL = {
    "wien": {
        "name": "Wien",
        "foerderart": "Landesdarlehen",
        "zinssatz": "1,0 % Fixzins",
        "laufzeit": "30 Jahre",
        "max_darlehen": "bis 90.000 €",
        "einkommensgrenzen": {
            "1_person": 48810,
            "2_personen": 72730,
            "je_weitere": 8000,
        },
        "besonderheiten": [
            "Superförderung für Neubau + Sanierung",
            "Eigenmittel: mind. 10 % der Gesamtkosten",
            "Wohnfläche: max. 150 m² (Eigenheim)",
            "Energieausweis Pflicht (HWB ≤ Grenzwert)",
            "Keine fossilen Heizungen (kein Öl/Gas)",
        ],
        "kontakt": "MA 50 – Wohnbauförderung, wohnberatung-wien.at",
        "antrag_vor_baubeginn": True,
    },
    "niederoesterreich": {
        "name": "Niederösterreich",
        "foerderart": "Wohnbaudarlehen + Eigenheim-Zuschüsse",
        "zinssatz": "variabel, aktuell ca. 1,0 %",
        "laufzeit": "bis 35 Jahre",
        "max_darlehen": "bis 85.000 €",
        "einkommensgrenzen": {
            "1_person": 40000,
            "2_personen": 65000,
            "je_weitere": 8000,
        },
        "besonderheiten": [
            "Ökopunktesystem für Neubau (mehr Punkte = mehr Förderung)",
            "Jungfamilien-Bonus verfügbar",
            "Sanierungsförderung bis 30.000 € Zuschuss",
            "Radonvorsorge-Nachweis in Waldviertel-Gemeinden",
            "Wohnfläche: 30-150 m²",
        ],
        "kontakt": "NÖ Landesregierung, Abt. Wohnbauförderung, noe.gv.at/wohnbau",
        "antrag_vor_baubeginn": True,
    },
    "oberoesterreich": {
        "name": "Oberösterreich",
        "foerderart": "Wohnbaudarlehen + Zuschüsse",
        "zinssatz": "variabel nach Programm",
        "laufzeit": "bis 30 Jahre",
        "max_darlehen": "bis 72.000 €",
        "einkommensgrenzen": {
            "1_person": 37000,
            "2_personen": 55000,
            "je_weitere": 5000,
        },
        "besonderheiten": [
            "Energiespar-Bonus bei HWB < 30 kWh/m²a",
            "Holzbau-Zuschlag (Förderung Holzanteil > 50%)",
            "Barrierefreiheits-Zuschlag",
            "Hochwasserschutz-Nachweis bei HQ-Zonen erforderlich",
            "Überschreitung Einkommensgrenze +10% = -25% Förderung",
        ],
        "kontakt": "OÖ Landesregierung, Abt. Wohnbauförderung",
        "antrag_vor_baubeginn": True,
    },
    "salzburg": {
        "name": "Salzburg",
        "foerderart": "Einmalige Zuschüsse + Annuitätenzuschüsse",
        "zinssatz": "Annuitätenzuschuss bis 500 €/Monat",
        "laufzeit": "variabel",
        "max_darlehen": "bis 78.000 € (Darlehen)",
        "einkommensgrenzen": {
            "1_person": 57027,
            "2_personen": 85540,
            "je_weitere": 7000,
            "grossfamilie_max": 126720,
        },
        "besonderheiten": [
            "Eigene Salzburger Wärmeschutzverordnung (NICHT OIB-RL 6!)",
            "Mind. 10% Eigenmittel + 20% Fremdmittel",
            "Nachhaltigkeitsbonus für Passivhaus (bis 15.000 €)",
            "Altstadtschutz Salzburg: Sondergenehmigung erforderlich",
            "Wohnnutzfläche: max. 150 m²",
        ],
        "kontakt": "SIR – Salzburger Institut für Raumordnung und Wohnen",
        "antrag_vor_baubeginn": True,
    },
    "steiermark": {
        "name": "Steiermark",
        "foerderart": "Landesdarlehen + Wohnbauscheck",
        "zinssatz": "1,0 % (Landesdarlehen) / 3,0 % (Wohnbauscheck)",
        "laufzeit": "max. 30 Jahre",
        "max_darlehen": "bis 70.000 €",
        "einkommensgrenzen": {
            "1_person": 56300,
            "2_personen": 84450,
            "je_weitere": 6570,
        },
        "besonderheiten": [
            "Jungfamilien: mind. 1 Partner unter 35, beide unter 40",
            "Ökobonus für Holzbau/Passivhaus",
            "Sonderwohnbauförderung: bis 100.000 € für Heizungstausch",
            "Altstadterhaltung Graz: Gestaltungsgutachten nötig",
            "Antragstellung ab 01.03.2026 wieder möglich",
        ],
        "kontakt": "Stmk. Landesregierung, Abt. 15 – Energie, Wohnbau, Technik",
        "antrag_vor_baubeginn": True,
    },
    "tirol": {
        "name": "Tirol",
        "foerderart": "Förderkredit ODER Wohnbauscheck",
        "zinssatz": "Start 0,2 % (steigend)",
        "laufzeit": "max. 37,5 Jahre",
        "max_darlehen": "bis 66.000 € (Darlehen) + Annuitätenzuschuss",
        "einkommensgrenzen": {
            "1_person": 45600,
            "2_personen": 75600,
            "je_weitere": 5760,
        },
        "besonderheiten": [
            "Wohnbauscheck: 18.900 € einmaliger, nicht rückzahlbarer Zuschuss",
            "Sanierungsförderung: bis 30.000 € Zuschuss/Darlehen",
            "PV-Förderung zusätzlich zu Bundesförderung",
            "Schneelast-Nachweis seehöhenabhängig Pflicht",
            "Digitale Einreichung über tiris.gv.at seit 01.07.2024",
        ],
        "kontakt": "Tiroler Landesregierung, Abt. Wohnbauförderung, tirol.gv.at/wohnbau",
        "antrag_vor_baubeginn": True,
    },
    "kaernten": {
        "name": "Kärnten",
        "foerderart": "Förderkredit + Zinszuschüsse + Häuslbauerbonus",
        "zinssatz": "0,5 % (Jahre 1-20), 1,5 % (Jahre 21-30)",
        "laufzeit": "30 Jahre",
        "max_darlehen": "bis 60.000 €",
        "einkommensgrenzen": {
            "1_person": 48000,
            "2_personen": 74000,
            "je_weitere": 7000,
        },
        "besonderheiten": [
            "Häuslbauerbonus (Einmalzuschuss)",
            "Energiebonus für Klimaaktiv-Standard",
            "Seenschutz: Uferzonenwidmung beachten",
            "Erdbebenzone 3-4: erhöhte Statik-Anforderungen",
            "Zinszuschüsse seit 10/2024 verfügbar",
        ],
        "kontakt": "Kärntner Landesregierung, Abt. Wirtschaft und Wohnbau",
        "antrag_vor_baubeginn": True,
    },
    "vorarlberg": {
        "name": "Vorarlberg",
        "foerderart": "Förderkredit",
        "zinssatz": "Fixzins 3,30 % (ab 07/2025) oder Staffelzins 1,0-5,0 %",
        "laufzeit": "bis 35 Jahre",
        "max_darlehen": "bis 80.000 €",
        "einkommensgrenzen": {
            "1_person": 42000,
            "2_personen": 63000,
            "je_weitere": 6000,
        },
        "besonderheiten": [
            "Strengste Energiestandards in Österreich!",
            "Passivhaus-Nähe faktisch Standard",
            "Energieautonomiebonus für Plusenergiehaus",
            "Holzbau-Tradition: vereinfachte Verfahren",
            "Förderung auch für Eigentumswohnungen",
        ],
        "kontakt": "Vlbg. Landesregierung, Abt. Wohnbauförderung",
        "antrag_vor_baubeginn": True,
    },
    "burgenland": {
        "name": "Burgenland",
        "foerderart": "Zinszuschuss + Darlehen",
        "zinssatz": "1,4 % Zinszuschuss (2024-2028)",
        "laufzeit": "variabel",
        "max_darlehen": "bis 55.000 €",
        "einkommensgrenzen": {
            "1_person": 40000,
            "2_personen": 60000,
            "je_weitere": 5000,
        },
        "besonderheiten": [
            "Öko-Zuschlag für Passivhaus/Klimaaktiv",
            "Neusiedlersee: Landschaftsschutz-Sonderregelungen",
            "Günstigstes Bauland in Österreich",
            "Thermische Sanierung: extra Zuschüsse verfügbar",
            "Bevorzugte Förderung bei Ortskernbelebung",
        ],
        "kontakt": "Bgld. Landesregierung, Abt. 5 – Baudirektion",
        "antrag_vor_baubeginn": True,
    },
}

BAUORDNUNG_VERGLEICH = {
    "burgenland": {
        "name": "Burgenland",
        "gesetz": "Bgld. Baugesetz 1997",
        "bewilligungsfrei": [
            "Gartengerätehaus bis 20 m² und 3,0 m Höhe",
            "Terrassenüberdachung bis 20 m²",
            "Einfriedung bis 1,5 m (blickdicht) / 2,0 m (transparent)",
            "Sichtschutzwand bis 1,8 m und 3,0 m Länge",
            "Fassadenanstrich und Fensteraustausch (gleiche Größe)",
            "Solaranlagen/PV auf Dach (bis 200 m²)",
            "Schwimmbecken bis 35 m³",
            "Geräteschuppen bis 10 m²",
        ],
        "anzeigepflichtig": [
            "Carport/Garage bis 50 m²",
            "Wintergarten bis 30 m²",
            "Pool/Schwimmbecken über 35 m³",
            "Änderung Raumeinteilung (Innenwände)",
            "Stützmauern über 1,5 m Höhe",
        ],
        "bewilligungspflichtig": [
            "Neubau (alle Gebäude)",
            "Zubauten und Umbauten",
            "Nutzungsänderungen",
            "Abbrucharbeiten",
        ],
    },
    "kaernten": {
        "name": "Kärnten",
        "gesetz": "Kärntner Bauordnung 1996",
        "bewilligungsfrei": [
            "Gerätehütte bis 10 m² und 2,5 m Höhe",
            "Pergola ohne Überdachung",
            "Einfriedung bis 1,5 m",
            "Fassadeninstandhaltung",
            "PV-Anlagen auf Dach",
            "Schwimmbecken bis 35 m³ (ortsfest)",
        ],
        "anzeigepflichtig": [
            "Terrassenüberdachung bis 40 m² und 3,5 m Höhe",
            "Carport bis 40 m²",
            "Gartenhaus bis 30 m²",
            "Einfriedung 1,5-2,0 m",
            "Wintergarten bis 30 m²",
            "Loggienverglasungen",
            "Innere Umbauten (Raumeinteilung)",
        ],
        "bewilligungspflichtig": [
            "Neubau von Gebäuden",
            "Zubauten und Aufstockungen",
            "Wesentliche Umbauten",
            "Nutzungsänderungen",
        ],
    },
    "niederoesterreich": {
        "name": "Niederösterreich",
        "gesetz": "NÖ Bauordnung 2014",
        "bewilligungsfrei": [
            "Gartenhaus bis 10 m² und 2,5 m Höhe (außerhalb Bauland)",
            "Einfriedung bis 1,5 m (geschlossen) / 2,5 m (offen)",
            "Fassadenanstrich, Dachreparatur",
            "PV-Anlagen auf Dach und Fassade (in Bauland)",
            "Schwimmbecken bis 35 m³",
            "Spielgeräte",
        ],
        "anzeigepflichtig": [
            "Nebengebäude bis 100 m² in Bauland-Widmung",
            "Terrassenüberdachung",
            "Carport/Garage",
            "Wintergarten",
            "Stützmauern",
            "Kanalherstellungen",
            "Innere Umbauten (Raumeinteilung)",
        ],
        "bewilligungspflichtig": [
            "Neubau von Gebäuden über bestimmte Größen",
            "Zubauten",
            "Aufstockungen",
            "Nutzungsänderungen",
            "Gebäude im Grünland (immer!)",
        ],
    },
    "oberoesterreich": {
        "name": "Oberösterreich",
        "gesetz": "OÖ Bauordnung 1994",
        "bewilligungsfrei": [
            "Gerätehütte/Schuppen bis 10 m² und 2,5 m Höhe",
            "Einfriedung bis 1,5 m",
            "Fassadenanstrich ohne Gestaltungsänderung",
            "PV-Anlage auf Dach (gebäudeintegriert)",
            "Schwimmbecken bis 35 m³",
        ],
        "anzeigepflichtig": [
            "Terrassenüberdachung bis 35 m²",
            "Carport/Garage bis 50 m²",
            "Gartenhaus bis 50 m²",
            "Wintergarten bis 40 m²",
            "Loggienverglasungen",
            "Innere Umbauten",
        ],
        "bewilligungspflichtig": [
            "Neubau von Gebäuden",
            "Zubauten über anzeigepflichtige Grenzen",
            "Aufstockungen",
            "Nutzungsänderungen",
            "Terrassenüberdachung über 35 m²",
        ],
    },
    "salzburg": {
        "name": "Salzburg",
        "gesetz": "Salzburger Baupolizeigesetz",
        "bewilligungsfrei": [
            "Geräteschuppen bis 6 m² und 2,0 m Höhe",
            "Einfriedung bis 1,5 m",
            "Fassadenanstrich gleicher Farbton",
            "PV-Anlagen auf Dach (Flach- und Schrägdach)",
            "Schwimmbecken bis 35 m³",
        ],
        "anzeigepflichtig": [
            "Gartenhaus/Schuppen 6-25 m²",
            "Carport bis 30 m²",
            "Innere Umbauten",
            "Einfriedung über 1,5 m",
        ],
        "bewilligungspflichtig": [
            "GENERELL: Terrassenüberdachung (jede Größe!)",
            "Neubau von Gebäuden",
            "Zubauten und Aufstockungen",
            "Wintergarten (jede Größe)",
            "Nutzungsänderungen",
            "Altstadtzone: fast alles bewilligungspflichtig",
        ],
    },
    "steiermark": {
        "name": "Steiermark",
        "gesetz": "Stmk. Baugesetz",
        "bewilligungsfrei": [
            "Geräteschuppen bis 15 m² und 2,5 m Höhe",
            "Terrassenüberdachung bis 40 m²",
            "Einfriedung bis 1,5 m",
            "Fassadeninstandhaltung",
            "PV-Anlagen auf Dach",
            "Schwimmbecken bis 35 m³",
            "Carport bis 30 m² (eingeschossig)",
        ],
        "anzeigepflichtig": [
            "Carport/Garage 30-50 m²",
            "Gartenhaus 15-40 m²",
            "Wintergarten bis 30 m²",
            "Innere Umbauten (Raumeinteilung)",
            "Stützmauern",
        ],
        "bewilligungspflichtig": [
            "Neubau von Gebäuden",
            "Zubauten über anzeigepflichtige Grenzen",
            "Aufstockungen",
            "Nutzungsänderungen",
        ],
    },
    "tirol": {
        "name": "Tirol",
        "gesetz": "Tiroler Bauordnung 2022",
        "bewilligungsfrei": [
            "Gerätehütte bis 6 m² und 2,3 m Höhe",
            "Einfriedung bis 1,5 m Höhe",
            "Fassadeninstandhaltung (gleiche Gestaltung)",
            "PV-Anlagen auf Dach und Fassade (in Bauland)",
            "Schwimmbecken bis 35 m³",
        ],
        "anzeigepflichtig": [
            "Gartenhaus/Schuppen 6-25 m²",
            "Carport bis 30 m²",
            "Innere Umbauten (ohne tragende Bauteile)",
            "Einfriedung über 1,5 m bis 2,0 m",
        ],
        "bewilligungspflichtig": [
            "GENERELL: Terrassenüberdachung (jede Größe!)",
            "Neubau von Gebäuden (inkl. Ferienwohnungen!)",
            "Zubauten und Aufstockungen",
            "Wintergarten (jede Größe)",
            "Nutzungsänderungen",
            "Tourismuszone: verschärfte Auflagen",
        ],
    },
    "vorarlberg": {
        "name": "Vorarlberg",
        "gesetz": "Vorarlberger Baugesetz",
        "bewilligungsfrei": [
            "Geräteschuppen bis 10 m² und 2,5 m Höhe",
            "Einfriedung bis 1,5 m",
            "Fassadeninstandhaltung",
            "PV-Anlagen auf Dach (bis 200 m²)",
            "Schwimmbecken bis 35 m³",
        ],
        "anzeigepflichtig": [
            "Gartenhaus bis 25 m²",
            "Carport/Garage bis 40 m²",
            "Terrassenüberdachung bis 25 m²",
            "Wintergarten bis 20 m²",
            "Innere Umbauten",
        ],
        "bewilligungspflichtig": [
            "Neubau von Gebäuden",
            "Zubauten über anzeigepflichtige Grenzen",
            "Aufstockungen",
            "Nutzungsänderungen",
            "Gestaltungsgutachten bei ortsbildrelevanten Bauten",
        ],
    },
    "wien": {
        "name": "Wien",
        "gesetz": "Bauordnung für Wien",
        "bewilligungsfrei": [
            "Einfriedung bis 2,5 m (offene Bauweise) / 1,5 m (geschlossen)",
            "Fassadenanstrich (gleicher Farbton)",
            "PV-Anlagen auf Flach-/Schrägdach",
            "Schwimmbecken bis 35 m³",
            "Spielgeräte, Fahrradabstellanlagen",
            "Klimageräte (Außengeräte unter Bedingungen)",
        ],
        "anzeigepflichtig": [
            "Dachgeschoßausbau (unter Bedingungen)",
            "Innere Umbauten (Raumeinteilung)",
            "Gartenhaus/Schuppen bis 25 m²",
            "Carport bis 30 m²",
            "Terrassenüberdachung",
            "Loggienverglasungen",
        ],
        "bewilligungspflichtig": [
            "Neubau von Gebäuden",
            "Zubauten und Aufstockungen",
            "Dachgeschoßausbau mit Kubaturänderung",
            "Nutzungsänderungen",
            "Schutzzone: fast alles bewilligungspflichtig",
            "BRISE: digitale Einreichung empfohlen (bis 50% schneller)",
        ],
    },
}

OENORM_NACHSCHLAGEWERK = [
    {
        "kategorie": "Wärmeschutz & Energie",
        "normen": [
            {"nummer": "ÖNORM B 8110-1", "titel": "Wärmeschutz im Hochbau — Anforderungen", "pflicht": True, "inhalt": "HWB-Anforderungen, Transmissionswärmeverlust, Basis für Energieausweis", "verweis": "OIB-RL 6"},
            {"nummer": "ÖNORM B 8110-2", "titel": "Wasserdampfdiffusion und Kondensationsschutz", "pflicht": True, "inhalt": "Nachweis Taupunkt, Schimmelvermeidung, Feuchteschutz (Glaser-Verfahren)", "verweis": "OIB-RL 6"},
            {"nummer": "ÖNORM B 8110-3", "titel": "Sommerlicher Wärmeschutz", "pflicht": True, "inhalt": "Vermeidung Überhitzung, operative Temperatur max. 21,8 °C, Verschattung", "verweis": "OIB-RL 6"},
            {"nummer": "ÖNORM B 8110-5", "titel": "Klimamodell und Nutzungsprofile", "pflicht": True, "inhalt": "Randbedingungen für Berechnungen (Klima, Nutzung, Standardwerte)", "verweis": "OIB-RL 6"},
            {"nummer": "ÖNORM B 8110-6", "titel": "Heizwärmebedarf und Kühlbedarf", "pflicht": True, "inhalt": "Berechnungsverfahren HWB, Monatsbilanzverfahren, Energiekennzahlen", "verweis": "OIB-RL 6"},
            {"nummer": "ÖNORM B 8110-7", "titel": "Tabellierte wärmeschutztechnische Bemessungswerte", "pflicht": False, "inhalt": "Nachschlagewerk: Lambda-Werte, µ-Werte, Rohdichte aller Baustoffe", "verweis": "Baubook-Richtwerte"},
        ],
    },
    {
        "kategorie": "Brandschutz",
        "normen": [
            {"nummer": "ÖNORM EN 13501-1", "titel": "Brandverhalten von Baustoffen — Klassifizierung", "pflicht": True, "inhalt": "Euroklassen A1 bis F, Rauchentwicklung s1-s3, Tropfenbildung d0-d2", "verweis": "OIB-RL 2"},
            {"nummer": "ÖNORM EN 13501-2", "titel": "Feuerwiderstand von Bauteilen", "pflicht": True, "inhalt": "REI-Klassifizierung (R=Tragfähigkeit, E=Raumabschluss, I=Wärmedämmung)", "verweis": "OIB-RL 2"},
            {"nummer": "ÖNORM B 3806", "titel": "Brandschutzanforderungen Außenwandbekleidungen", "pflicht": True, "inhalt": "Fassaden-Brandschutz, WDVS-Systeme, Brandriegel-Anforderungen", "verweis": "OIB-RL 2"},
        ],
    },
    {
        "kategorie": "Schallschutz",
        "normen": [
            {"nummer": "ÖNORM B 8115-1", "titel": "Schallschutz und Raumakustik — Begriffe", "pflicht": False, "inhalt": "Definitionen: Luft-/Trittschall, Flankenschall, R'w, L'n,w", "verweis": "OIB-RL 5"},
            {"nummer": "ÖNORM B 8115-2", "titel": "Schallschutz — Anforderungen", "pflicht": True, "inhalt": "Mindestanforderungen Luft- und Trittschall für Wohn- und Bürogebäude", "verweis": "OIB-RL 5"},
            {"nummer": "ÖNORM B 8115-4", "titel": "Schallschutz — Maßnahmen", "pflicht": False, "inhalt": "Planungsrichtlinien: Wandaufbauten, Decken, Estrich, Fenster, Türen", "verweis": "OIB-RL 5"},
        ],
    },
    {
        "kategorie": "Tragwerk & Statik",
        "normen": [
            {"nummer": "ÖNORM EN 1990", "titel": "Eurocode 0 — Grundlagen", "pflicht": True, "inhalt": "Grundlagen Tragwerksplanung, Sicherheitskonzept, Grenzzustände", "verweis": "OIB-RL 1"},
            {"nummer": "ÖNORM EN 1991", "titel": "Eurocode 1 — Einwirkungen", "pflicht": True, "inhalt": "Lasten: Eigengewicht, Nutzlasten, Schnee, Wind, Temperatur, Brand", "verweis": "OIB-RL 1"},
            {"nummer": "ÖNORM EN 1992", "titel": "Eurocode 2 — Betonbau", "pflicht": True, "inhalt": "Bemessung Stahlbeton: Biegung, Querkraft, Bewehrung, Rissbreite", "verweis": "OIB-RL 1"},
            {"nummer": "ÖNORM EN 1993", "titel": "Eurocode 3 — Stahlbau", "pflicht": True, "inhalt": "Bemessung Stahlkonstruktionen: Stabilitätsnachweise, Verbindungen", "verweis": "OIB-RL 1"},
            {"nummer": "ÖNORM EN 1995", "titel": "Eurocode 5 — Holzbau", "pflicht": True, "inhalt": "Bemessung Holzkonstruktionen: Biegung, Knicken, Verbindungsmittel", "verweis": "OIB-RL 1"},
            {"nummer": "ÖNORM EN 1996", "titel": "Eurocode 6 — Mauerwerksbau", "pflicht": True, "inhalt": "Bemessung Mauerwerk: Druckfestigkeit, Schub, Biegung", "verweis": "OIB-RL 1"},
            {"nummer": "ÖNORM EN 1997", "titel": "Eurocode 7 — Geotechnik", "pflicht": True, "inhalt": "Gründungen: Grundbruch, Setzungen, Böschungen, Stützbauwerke", "verweis": "OIB-RL 1"},
            {"nummer": "ÖNORM EN 1998", "titel": "Eurocode 8 — Erdbeben", "pflicht": True, "inhalt": "Erdbebeneinwirkungen: Bemessungsspektrum, Duktilität, Erdbebenzonen", "verweis": "OIB-RL 1"},
        ],
    },
    {
        "kategorie": "Planung & Ausschreibung",
        "normen": [
            {"nummer": "ÖNORM A 6240", "titel": "Technische Zeichnungen für das Bauwesen", "pflicht": True, "inhalt": "Plandarstellung: Grundrisse, Schnitte, Ansichten, Maßketten, Symbole", "verweis": "Bauordnungen"},
            {"nummer": "ÖNORM A 2063", "titel": "Austausch von Leistungsbeschreibungen", "pflicht": True, "inhalt": "Digitaler Austausch AVA-Daten, LV-Erstellung, ONLV-Format", "verweis": "BVergG"},
            {"nummer": "ÖNORM B 1800", "titel": "Flächenberechnung", "pflicht": True, "inhalt": "Nutzfläche, Bruttogrundfläche, Wohnfläche, Kubatur — Berechnungsregeln", "verweis": "Bauordnungen"},
            {"nummer": "ÖNORM B 1801-1", "titel": "Bauprojekt- und Objektmanagement — Kosten", "pflicht": False, "inhalt": "Kostengliederung: Kostengruppen 1-7, Planungsorientierte Kostenermittlung", "verweis": "Honorarordnungen"},
            {"nummer": "ÖNORM B 2110", "titel": "Werkvertragsnorm Bauleistungen", "pflicht": True, "inhalt": "ABGB-Ergänzung: Bau-Werkvertrag, Gewährleistung, Schadenersatz, Übernahme", "verweis": "Bauverträge"},
        ],
    },
    {
        "kategorie": "Hygiene & Gesundheit",
        "normen": [
            {"nummer": "ÖNORM B 5019", "titel": "Trinkwasser — Legionellenprophylaxe", "pflicht": True, "inhalt": "Warmwasser ≥60°C, Zirkulation, Probenahmestellen, Desinfektion", "verweis": "OIB-RL 3"},
            {"nummer": "ÖNORM B 2501", "titel": "Entwässerung von Gebäuden", "pflicht": True, "inhalt": "Abwasserleitungen: Dimensionierung, Gefälle, Belüftung, Materialien", "verweis": "OIB-RL 3"},
        ],
    },
    {
        "kategorie": "Barrierefreiheit",
        "normen": [
            {"nummer": "ÖNORM B 1600", "titel": "Barrierefreies Bauen — Planungsgrundsätze", "pflicht": True, "inhalt": "Rollstuhlgerechte Planung: Türbreiten (≥80cm), Rampen (≤6%), Aufzüge", "verweis": "OIB-RL 4"},
            {"nummer": "ÖNORM B 1601", "titel": "Barrierefreie Gesundheitseinrichtungen", "pflicht": False, "inhalt": "Spezielle Anforderungen für Spitäler, Arztpraxen, Pflegeheime", "verweis": "OIB-RL 4"},
            {"nummer": "ÖNORM B 1602", "titel": "Barrierefreie Bildungseinrichtungen", "pflicht": False, "inhalt": "Schulen, Kindergärten, Universitäten: spezifische Anforderungen", "verweis": "OIB-RL 4"},
        ],
    },
]


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


DETAILLIERTE_KOSTENPOSITIONEN = {
    "grundstueck": {
        "name": "Grundstück & Nebenkosten",
        "positionen": {
            "grunderwerbsteuer": {"anteil": 0.035, "basis": "grundstueckspreis", "name": "Grunderwerbsteuer (3,5%)"},
            "grundbuch": {"anteil": 0.011, "basis": "grundstueckspreis", "name": "Grundbucheintragung (1,1%)"},
            "makler": {"anteil": 0.036, "basis": "grundstueckspreis", "name": "Makler (3% + USt)"},
            "vertrag": {"anteil": 0.015, "basis": "grundstueckspreis", "name": "Vertragserrichtung (~1,5%)"},
        }
    },
    "rohbau": {
        "name": "Rohbau",
        "anteil_gesamt": 0.40,
        "positionen": {
            "erdarbeiten": {"euro_m2": 45, "name": "Erdarbeiten & Baugrube"},
            "fundament": {"euro_m2": 85, "name": "Fundament & Bodenplatte"},
            "mauerwerk": {"euro_m2": 180, "name": "Mauerwerk & Tragwerk"},
            "decken": {"euro_m2": 120, "name": "Decken (Stahlbeton)"},
            "dachstuhl": {"euro_m2": 95, "name": "Dachstuhl & Dacheindeckung"},
            "kamin_schacht": {"euro_m2": 15, "name": "Kamin & Installationsschächte"},
        }
    },
    "ausbau": {
        "name": "Ausbau & Technik",
        "anteil_gesamt": 0.35,
        "positionen": {
            "fenster_tueren": {"euro_m2": 110, "name": "Fenster & Außentüren"},
            "daemmung_fassade": {"euro_m2": 75, "name": "Dämmung & Fassade (WDVS)"},
            "innenputz": {"euro_m2": 35, "name": "Innenputz & Spachtelung"},
            "estrich": {"euro_m2": 30, "name": "Estrich (schwimmend)"},
            "elektro": {"euro_m2": 85, "name": "Elektroinstallation"},
            "sanitaer": {"euro_m2": 75, "name": "Sanitär & Heizung"},
            "heizung": {"euro_m2": 90, "name": "Heizungssystem"},
            "lueftung": {"euro_m2": 25, "name": "Lüftungsanlage (KWL)"},
        }
    },
    "innenausbau": {
        "name": "Innenausbau & Oberflächen",
        "anteil_gesamt": 0.15,
        "positionen": {
            "bodenbelag": {"euro_m2": 55, "name": "Bodenbeläge"},
            "fliesen": {"euro_m2": 40, "name": "Fliesen (Bad/WC/Küche)"},
            "malerarbeiten": {"euro_m2": 20, "name": "Malerarbeiten"},
            "innentueren": {"euro_m2": 25, "name": "Innentüren"},
            "kueche": {"pauschal": 8000, "name": "Küche (Einbauküche)"},
            "bad_ausstattung": {"pauschal": 5000, "name": "Bad-Ausstattung"},
        }
    },
    "nebenkosten_bau": {
        "name": "Baunebenkosten",
        "anteil_gesamt": 0.10,
        "positionen": {
            "planung_architekt": {"anteil": 0.08, "basis": "baukosten", "name": "Architekt/Planung (~8%)"},
            "statik": {"anteil": 0.02, "basis": "baukosten", "name": "Statik (~2%)"},
            "energieausweis": {"pauschal": 350, "name": "Energieausweis"},
            "baubewilligung": {"pauschal": 1500, "name": "Baubewilligungsgebühren"},
            "baustrom_wasser": {"pauschal": 2000, "name": "Baustrom & Bauwasser"},
            "versicherung": {"pauschal": 800, "name": "Bauversicherung"},
            "vermessung": {"pauschal": 2500, "name": "Vermessung & Einmessung"},
        }
    }
}

HEIZUNGSSYSTEME = {
    "waermepumpe_erd": {"name": "Wärmepumpe (Erdwärme)", "kosten_euro": 22000, "cop": 4.5, "co2_kg_kwh": 0.05, "foerderbar": True, "ideal_fuer": "Neubau mit Garten"},
    "waermepumpe_luft": {"name": "Wärmepumpe (Luft/Wasser)", "kosten_euro": 14000, "cop": 3.5, "co2_kg_kwh": 0.07, "foerderbar": True, "ideal_fuer": "Neubau, Sanierung"},
    "pellets": {"name": "Pelletsheizung", "kosten_euro": 18000, "cop": 0.92, "co2_kg_kwh": 0.04, "foerderbar": True, "ideal_fuer": "Sanierung mit Lagerraum"},
    "fernwaerme": {"name": "Fernwärme", "kosten_euro": 8000, "cop": 1.0, "co2_kg_kwh": 0.08, "foerderbar": True, "ideal_fuer": "Stadtgebiet"},
    "gasbrennwert": {"name": "Gasbrennwert (Bestand)", "kosten_euro": 7000, "cop": 0.98, "co2_kg_kwh": 0.24, "foerderbar": False, "ideal_fuer": "Nur Bestand (Neubau verboten!)"},
    "oelheizung": {"name": "Ölheizung (Bestand)", "kosten_euro": 9000, "cop": 0.90, "co2_kg_kwh": 0.31, "foerderbar": False, "ideal_fuer": "Nur Bestand (Neubau verboten!)"},
}

SANIERUNG_MASSNAHMEN = [
    {"id": "fassade", "name": "Fassadendämmung (WDVS 16cm EPS)", "kosten_m2": 120, "hwb_reduktion_pct": 25, "uwert_vorher": 1.2, "uwert_nachher": 0.18, "lebensdauer_jahre": 35, "foerderung_pct": 30},
    {"id": "fassade_holzfaser", "name": "Fassadendämmung (20cm Holzfaser)", "kosten_m2": 165, "hwb_reduktion_pct": 28, "uwert_vorher": 1.2, "uwert_nachher": 0.15, "lebensdauer_jahre": 40, "foerderung_pct": 35},
    {"id": "dach", "name": "Dachdämmung (Zwischensparren 24cm)", "kosten_m2": 95, "hwb_reduktion_pct": 20, "uwert_vorher": 0.9, "uwert_nachher": 0.14, "lebensdauer_jahre": 40, "foerderung_pct": 30},
    {"id": "kellerdecke", "name": "Kellerdeckendämmung (12cm)", "kosten_m2": 50, "hwb_reduktion_pct": 10, "uwert_vorher": 1.0, "uwert_nachher": 0.28, "lebensdauer_jahre": 30, "foerderung_pct": 25},
    {"id": "fenster_2fach", "name": "Fenstertausch (2-fach Verglasung)", "kosten_m2": 450, "hwb_reduktion_pct": 12, "uwert_vorher": 2.8, "uwert_nachher": 1.1, "lebensdauer_jahre": 30, "foerderung_pct": 20},
    {"id": "fenster_3fach", "name": "Fenstertausch (3-fach Verglasung)", "kosten_m2": 580, "hwb_reduktion_pct": 15, "uwert_vorher": 2.8, "uwert_nachher": 0.7, "lebensdauer_jahre": 35, "foerderung_pct": 25},
    {"id": "heizung_wp", "name": "Heizungstausch → Wärmepumpe", "kosten_pauschal": 16000, "hwb_reduktion_pct": 0, "energie_reduktion_pct": 65, "lebensdauer_jahre": 20, "foerderung_pct": 40},
    {"id": "heizung_pellets", "name": "Heizungstausch → Pellets", "kosten_pauschal": 20000, "hwb_reduktion_pct": 0, "energie_reduktion_pct": 15, "lebensdauer_jahre": 20, "foerderung_pct": 35},
    {"id": "solar", "name": "Solaranlage (Warmwasser)", "kosten_pauschal": 6000, "hwb_reduktion_pct": 0, "energie_reduktion_pct": 20, "lebensdauer_jahre": 25, "foerderung_pct": 30},
    {"id": "pv", "name": "Photovoltaik (5 kWp)", "kosten_pauschal": 9000, "hwb_reduktion_pct": 0, "energie_reduktion_pct": 25, "lebensdauer_jahre": 25, "foerderung_pct": 25},
    {"id": "kwl", "name": "Kontrollierte Wohnraumlüftung", "kosten_pauschal": 8000, "hwb_reduktion_pct": 8, "energie_reduktion_pct": 10, "lebensdauer_jahre": 20, "foerderung_pct": 20},
]

DAEMMSTOFFE_VERGLEICH = [
    {"name": "EPS (Styropor)", "lambda": 0.035, "kosten_m2_10cm": 18, "oekologisch": False, "brandklasse": "E", "diffusion_mu": 30},
    {"name": "XPS (Styrodur)", "lambda": 0.032, "kosten_m2_10cm": 28, "oekologisch": False, "brandklasse": "E", "diffusion_mu": 100},
    {"name": "Mineralwolle (MW)", "lambda": 0.035, "kosten_m2_10cm": 15, "oekologisch": False, "brandklasse": "A1", "diffusion_mu": 1},
    {"name": "Steinwolle (SW)", "lambda": 0.036, "kosten_m2_10cm": 16, "oekologisch": False, "brandklasse": "A1", "diffusion_mu": 1},
    {"name": "Holzfaser (WF)", "lambda": 0.042, "kosten_m2_10cm": 32, "oekologisch": True, "brandklasse": "E", "diffusion_mu": 5},
    {"name": "Zellulose (eingeblasen)", "lambda": 0.038, "kosten_m2_10cm": 12, "oekologisch": True, "brandklasse": "B2", "diffusion_mu": 2},
    {"name": "Hanfdämmung", "lambda": 0.042, "kosten_m2_10cm": 35, "oekologisch": True, "brandklasse": "E", "diffusion_mu": 2},
    {"name": "Schafwolle", "lambda": 0.040, "kosten_m2_10cm": 38, "oekologisch": True, "brandklasse": "B2", "diffusion_mu": 2},
    {"name": "PUR/PIR", "lambda": 0.024, "kosten_m2_10cm": 35, "oekologisch": False, "brandklasse": "B2", "diffusion_mu": 50},
    {"name": "Schaumglas (CG)", "lambda": 0.042, "kosten_m2_10cm": 55, "oekologisch": False, "brandklasse": "A1", "diffusion_mu": 100000},
    {"name": "Vakuumdämmung (VIP)", "lambda": 0.007, "kosten_m2_10cm": 180, "oekologisch": False, "brandklasse": "A2", "diffusion_mu": 100000},
]


def berechne_uwert_mehrschicht(schichten):
    """Exakte U-Wert-Berechnung nach ÖNORM EN ISO 6946 für mehrschichtigen Aufbau.
    schichten: Liste von {"material": str, "dicke_cm": float, "lambda_wert": float}
    Rückgabe: dict mit U-Wert, R-Wert, Schichtdetails
    """
    rsi = 0.13
    rse = 0.04
    r_gesamt = rsi + rse
    schicht_details = []

    for s in schichten:
        dicke_m = s["dicke_cm"] / 100.0
        lambda_w = s["lambda_wert"]
        r_schicht = dicke_m / lambda_w if lambda_w > 0 else 0
        r_gesamt += r_schicht
        schicht_details.append({
            "material": s["material"],
            "dicke_cm": s["dicke_cm"],
            "lambda": lambda_w,
            "r_wert": round(r_schicht, 4),
            "dicke_m": round(dicke_m, 4),
        })

    u_wert = 1.0 / r_gesamt if r_gesamt > 0 else 999
    gesamt_dicke = sum(s["dicke_cm"] for s in schichten)

    oib_bewertung = "Nicht OIB-konform"
    if u_wert <= 0.10:
        oib_bewertung = "Passivhaus-Niveau (hervorragend)"
    elif u_wert <= 0.15:
        oib_bewertung = "Niedrigstenergiehaus (sehr gut)"
    elif u_wert <= 0.20:
        oib_bewertung = "Niedrigenergiehaus (gut)"
    elif u_wert <= 0.35:
        oib_bewertung = "OIB-RL 6 konform (Neubau)"
    elif u_wert <= 0.50:
        oib_bewertung = "Sanierung akzeptabel"

    return {
        "u_wert": round(u_wert, 4),
        "r_gesamt": round(r_gesamt, 4),
        "rsi": rsi,
        "rse": rse,
        "schichten": schicht_details,
        "gesamt_dicke_cm": round(gesamt_dicke, 1),
        "bewertung": oib_bewertung,
    }


def berechne_baukosten_detail(wohnflaeche_m2, bautyp, bundesland, keller=False, garage=False,
                                grundstueckspreis=0, qualitaet="standard", heizung="waermepumpe_luft"):
    """Detaillierte Baukostenberechnung mit Aufschlüsselung nach Positionen."""
    kostentyp_map = {
        "standard": "Einfamilienhaus (Standard)",
        "gehoben": "Einfamilienhaus (Gehoben)",
        "luxus": "Einfamilienhaus (Luxus)",
        "passivhaus": "Passivhaus",
        "holzhaus": "Holzhaus (Fertigteil)",
        "reihenhaus": "Reihenhaus",
    }
    typ_key = kostentyp_map.get(bautyp, "Einfamilienhaus (Standard)")
    richtwert = KOSTENRICHTWERTE_2026.get(typ_key, {"min": 2200, "max": 3200})
    regionalfaktor = REGIONALE_KOSTENFAKTOREN.get(bundesland, 1.0)

    preis_m2_min = richtwert["min"] * regionalfaktor
    preis_m2_max = richtwert["max"] * regionalfaktor
    preis_m2_mittel = (preis_m2_min + preis_m2_max) / 2

    baukosten_netto = wohnflaeche_m2 * preis_m2_mittel

    positionen = []
    for kat_key, kat in DETAILLIERTE_KOSTENPOSITIONEN.items():
        if kat_key == "grundstueck" and grundstueckspreis > 0:
            for pos_key, pos in kat["positionen"].items():
                betrag = grundstueckspreis * pos["anteil"]
                positionen.append({"kategorie": kat["name"], "position": pos["name"], "betrag": round(betrag)})
        elif kat_key == "nebenkosten_bau":
            for pos_key, pos in kat["positionen"].items():
                if "anteil" in pos:
                    betrag = baukosten_netto * pos["anteil"]
                else:
                    betrag = pos.get("pauschal", 0)
                positionen.append({"kategorie": kat["name"], "position": pos["name"], "betrag": round(betrag)})
        elif kat_key in ("rohbau", "ausbau", "innenausbau"):
            for pos_key, pos in kat["positionen"].items():
                if "euro_m2" in pos:
                    betrag = wohnflaeche_m2 * pos["euro_m2"] * regionalfaktor
                else:
                    betrag = pos.get("pauschal", 0) * regionalfaktor
                positionen.append({"kategorie": kat["name"], "position": pos["name"], "betrag": round(betrag)})

    keller_kosten = 0
    if keller:
        keller_kosten = wohnflaeche_m2 * 0.6 * 950 * regionalfaktor
        positionen.append({"kategorie": "Keller", "position": "Keller (beheizt, ~60% der WFL)", "betrag": round(keller_kosten)})

    garage_kosten = 0
    if garage:
        garage_kosten = 30 * 600 * regionalfaktor
        positionen.append({"kategorie": "Garage", "position": "Garage/Carport (~30m²)", "betrag": round(garage_kosten)})

    heizung_sys = HEIZUNGSSYSTEME.get(heizung, HEIZUNGSSYSTEME["waermepumpe_luft"])
    positionen.append({"kategorie": "Heizung", "position": heizung_sys["name"], "betrag": round(heizung_sys["kosten_euro"] * regionalfaktor)})

    gesamt = sum(p["betrag"] for p in positionen)
    gesamt_mit_grundstueck = gesamt + grundstueckspreis

    return {
        "positionen": positionen,
        "baukosten_netto": round(baukosten_netto),
        "gesamt_ohne_grundstueck": round(gesamt),
        "grundstueckspreis": grundstueckspreis,
        "gesamt_mit_grundstueck": round(gesamt_mit_grundstueck),
        "preis_pro_m2": round(gesamt / wohnflaeche_m2) if wohnflaeche_m2 > 0 else 0,
        "regionalfaktor": regionalfaktor,
        "bundesland": bundesland,
        "wohnflaeche": wohnflaeche_m2,
        "qualitaet": bautyp,
        "heizung": heizung_sys["name"],
    }


def berechne_hwb_exakt(wohnflaeche_m2, uwert_wand, uwert_dach, uwert_boden, uwert_fenster,
                        fenster_anteil_pct=20, geschosse=2, kompaktheit="mittel", heizung="waermepumpe_luft",
                        kwl=False, bundesland="wien"):
    """Vereinfachte HWB-Berechnung nach OIB-RL 6 Methodik.
    Liefert geschätzten Heizwärmebedarf und Gesamtenergieeffizienz.
    """
    hgt = {"wien": 3200, "niederoesterreich": 3400, "burgenland": 3100, "oberoesterreich": 3600,
           "salzburg": 3800, "steiermark": 3500, "kaernten": 3300, "tirol": 4000, "vorarlberg": 3700}
    hgt_wert = hgt.get(bundesland, 3500)

    a_boden = wohnflaeche_m2 / geschosse
    hoehe = 2.7
    a_gesamt_bgf = wohnflaeche_m2
    umfang = (a_boden ** 0.5) * 4
    a_wand = umfang * hoehe * geschosse
    a_fenster = a_wand * (fenster_anteil_pct / 100.0)
    a_wand_opak = a_wand - a_fenster
    a_dach = a_boden
    a_boden_fl = a_boden

    kompaktheit_faktor = {"kompakt": 0.85, "mittel": 1.0, "gestreckt": 1.15}.get(kompaktheit, 1.0)

    qt_wand = a_wand_opak * uwert_wand
    qt_dach = a_dach * uwert_dach
    qt_boden = a_boden_fl * uwert_boden
    qt_fenster = a_fenster * uwert_fenster
    qt_gesamt = (qt_wand + qt_dach + qt_boden + qt_fenster) * kompaktheit_faktor

    lueftungsverlust = 0.34 * 0.4 * (a_gesamt_bgf * hoehe)
    if kwl:
        lueftungsverlust *= 0.25

    solare_gewinne = a_fenster * 150 * 0.5
    interne_gewinne = a_gesamt_bgf * 3.75 * 24 * 200 / 1000

    hwb_gesamt = (qt_gesamt + lueftungsverlust) * hgt_wert / 1000 - solare_gewinne - interne_gewinne
    hwb_gesamt = max(hwb_gesamt, 0)
    hwb_m2 = hwb_gesamt / a_gesamt_bgf if a_gesamt_bgf > 0 else 0

    heiz = HEIZUNGSSYSTEME.get(heizung, HEIZUNGSSYSTEME["waermepumpe_luft"])
    cop = heiz["cop"]
    if cop > 1:
        endenergie = hwb_gesamt / cop
    else:
        endenergie = hwb_gesamt / cop if cop > 0 else hwb_gesamt

    fgee = endenergie / (a_gesamt_bgf * 55) if a_gesamt_bgf > 0 else 2.0

    if hwb_m2 <= 10:
        klasse = "A++"
    elif hwb_m2 <= 15:
        klasse = "A+"
    elif hwb_m2 <= 25:
        klasse = "A"
    elif hwb_m2 <= 50:
        klasse = "B"
    elif hwb_m2 <= 100:
        klasse = "C"
    elif hwb_m2 <= 150:
        klasse = "D"
    elif hwb_m2 <= 200:
        klasse = "E"
    elif hwb_m2 <= 250:
        klasse = "F"
    else:
        klasse = "G"

    return {
        "hwb_gesamt_kwh": round(hwb_gesamt),
        "hwb_m2_a": round(hwb_m2, 1),
        "endenergie_kwh": round(endenergie),
        "fgee": round(fgee, 2),
        "klasse": klasse,
        "qt_wand": round(qt_wand, 1),
        "qt_dach": round(qt_dach, 1),
        "qt_boden": round(qt_boden, 1),
        "qt_fenster": round(qt_fenster, 1),
        "qt_gesamt": round(qt_gesamt, 1),
        "lueftungsverlust": round(lueftungsverlust, 1),
        "solare_gewinne": round(solare_gewinne),
        "interne_gewinne": round(interne_gewinne),
        "hgt": hgt_wert,
        "a_wand": round(a_wand_opak, 1),
        "a_fenster": round(a_fenster, 1),
        "a_dach": round(a_dach, 1),
        "a_boden": round(a_boden_fl, 1),
        "heizung": heiz["name"],
        "co2_kg_jahr": round(endenergie * heiz["co2_kg_kwh"]),
    }


def optimiere_kosten(wohnflaeche_m2, bundesland, budget_max=0):
    """Kostenoptimierer: Findet günstigste Bauweise bei gleicher Qualität."""
    varianten = []
    for bautyp in ["standard", "holzhaus", "reihenhaus"]:
        for heizung_key in ["waermepumpe_luft", "fernwaerme", "pellets"]:
            for keller in [False, True]:
                result = berechne_baukosten_detail(wohnflaeche_m2, bautyp, bundesland,
                                                    keller=keller, heizung=heizung_key)
                heiz = HEIZUNGSSYSTEME[heizung_key]
                varianten.append({
                    "bautyp": bautyp.replace("_", " ").title(),
                    "heizung": heiz["name"],
                    "keller": "Ja" if keller else "Nein",
                    "gesamt": result["gesamt_ohne_grundstueck"],
                    "pro_m2": result["preis_pro_m2"],
                    "co2": heiz["co2_kg_kwh"],
                    "foerderbar": heiz["foerderbar"],
                })

    varianten.sort(key=lambda x: x["gesamt"])
    if budget_max > 0:
        varianten = [v for v in varianten if v["gesamt"] <= budget_max]

    spartipps = [
        "Keller weglassen spart 40.000–80.000 € → Bodenplatte stattdessen",
        "Fertigteilhaus statt Architekt: 15–25% günstiger bei gleicher Qualität",
        "Eigenleistung bei Innenausbau: 20.000–40.000 € Ersparnis möglich",
        "Mehrere Angebote einholen: Preisunterschiede von 30%+ üblich!",
        "Förderungen nutzen: Sanierungsbonus, Wohnbauförderung, PV-Förderung",
        "Kompakte Bauform wählen: Weniger Außenwand = weniger Kosten + Energie",
        "Standardisierte Fenstermaße verwenden: Sondermaße +40% teurer",
        "Bauphase im Frühjahr starten: Weniger Witterungsverzögerungen",
    ]

    return {"varianten": varianten[:12], "spartipps": spartipps}


def optimiere_energie(wohnflaeche_m2, bundesland, ziel_klasse="A"):
    """Niedrigenergie-Optimierer: Findet optimalen Aufbau für Ziel-Energieklasse."""
    ziel_hwb = {"A++": 10, "A+": 15, "A": 25, "B": 50}.get(ziel_klasse, 25)

    empfehlungen = []
    daemmvarianten = [
        {"name": "Budget-Effizienz", "wand": 0.22, "dach": 0.15, "boden": 0.30, "fenster": 1.1,
         "daemmung": "EPS 14cm", "kosten_extra": 0, "kwl": False},
        {"name": "Niedrigenergiehaus", "wand": 0.18, "dach": 0.12, "boden": 0.25, "fenster": 0.9,
         "daemmung": "Mineralwolle 18cm", "kosten_extra": 5000, "kwl": False},
        {"name": "Niedrigstenergiehaus", "wand": 0.14, "dach": 0.10, "boden": 0.20, "fenster": 0.8,
         "daemmung": "EPS/Holzfaser 22cm", "kosten_extra": 12000, "kwl": True},
        {"name": "Passivhaus-Standard", "wand": 0.10, "dach": 0.08, "boden": 0.15, "fenster": 0.7,
         "daemmung": "Holzfaser 30cm", "kosten_extra": 25000, "kwl": True},
        {"name": "Plus-Energie-Haus", "wand": 0.08, "dach": 0.06, "boden": 0.12, "fenster": 0.6,
         "daemmung": "PUR/PIR + Holzfaser 35cm", "kosten_extra": 45000, "kwl": True},
    ]

    for var in daemmvarianten:
        result = berechne_hwb_exakt(wohnflaeche_m2, var["wand"], var["dach"], var["boden"], var["fenster"],
                                     kwl=var["kwl"], bundesland=bundesland, heizung="waermepumpe_luft")
        erreicht_ziel = result["hwb_m2_a"] <= ziel_hwb
        empfehlungen.append({
            "name": var["name"],
            "hwb": result["hwb_m2_a"],
            "klasse": result["klasse"],
            "fgee": result["fgee"],
            "uwerte": {"wand": var["wand"], "dach": var["dach"], "boden": var["boden"], "fenster": var["fenster"]},
            "daemmung": var["daemmung"],
            "kwl": var["kwl"],
            "kosten_extra": var["kosten_extra"],
            "co2_jahr": result["co2_kg_jahr"],
            "erreicht_ziel": erreicht_ziel,
        })

    return {"empfehlungen": empfehlungen, "ziel_klasse": ziel_klasse, "ziel_hwb": ziel_hwb}


def optimiere_sanierung(wohnflaeche_m2, hwb_aktuell, bundesland, budget_max=0):
    """Sanierungsoptimierer: Priorisiert Maßnahmen nach Kosten-Nutzen-Verhältnis."""
    ergebnisse = []
    for m in SANIERUNG_MASSNAHMEN:
        if "kosten_m2" in m:
            if m["id"] in ("fenster_2fach", "fenster_3fach"):
                flaeche = wohnflaeche_m2 * 0.2
            elif m["id"] in ("fassade", "fassade_holzfaser"):
                flaeche = wohnflaeche_m2 * 1.2
            elif m["id"] == "dach":
                flaeche = wohnflaeche_m2 / 2
            elif m["id"] == "kellerdecke":
                flaeche = wohnflaeche_m2 / 2
            else:
                flaeche = wohnflaeche_m2
            kosten_brutto = flaeche * m["kosten_m2"]
        else:
            kosten_brutto = m.get("kosten_pauschal", 0)

        foerderung = kosten_brutto * m.get("foerderung_pct", 0) / 100
        kosten_netto = kosten_brutto - foerderung

        hwb_einsparung = hwb_aktuell * m.get("hwb_reduktion_pct", 0) / 100
        energie_einsparung = hwb_aktuell * wohnflaeche_m2 * m.get("energie_reduktion_pct", 0) / 100

        einsparung_kwh_jahr = hwb_einsparung * wohnflaeche_m2 + energie_einsparung
        einsparung_euro_jahr = einsparung_kwh_jahr * 0.12
        amortisation = kosten_netto / einsparung_euro_jahr if einsparung_euro_jahr > 0 else 999

        ergebnisse.append({
            "name": m["name"],
            "kosten_brutto": round(kosten_brutto),
            "foerderung": round(foerderung),
            "kosten_netto": round(kosten_netto),
            "hwb_reduktion_pct": m.get("hwb_reduktion_pct", 0),
            "einsparung_kwh_jahr": round(einsparung_kwh_jahr),
            "einsparung_euro_jahr": round(einsparung_euro_jahr),
            "amortisation_jahre": round(amortisation, 1),
            "lebensdauer": m.get("lebensdauer_jahre", 30),
            "prioritaet": round(einsparung_euro_jahr / kosten_netto * 1000, 1) if kosten_netto > 0 else 0,
        })

    ergebnisse.sort(key=lambda x: x["prioritaet"], reverse=True)

    if budget_max > 0:
        gewaehlte = []
        rest_budget = budget_max
        for e in ergebnisse:
            if e["kosten_netto"] <= rest_budget:
                gewaehlte.append(e)
                rest_budget -= e["kosten_netto"]
        paket_kosten = sum(e["kosten_netto"] for e in gewaehlte)
        paket_einsparung = sum(e["einsparung_euro_jahr"] for e in gewaehlte)
        paket_hwb_reduktion = sum(e["hwb_reduktion_pct"] for e in gewaehlte)
    else:
        gewaehlte = ergebnisse
        paket_kosten = sum(e["kosten_netto"] for e in ergebnisse)
        paket_einsparung = sum(e["einsparung_euro_jahr"] for e in ergebnisse)
        paket_hwb_reduktion = sum(e["hwb_reduktion_pct"] for e in ergebnisse)

    hwb_nachher = hwb_aktuell * (1 - min(paket_hwb_reduktion, 80) / 100)

    return {
        "alle_massnahmen": ergebnisse,
        "empfohlenes_paket": gewaehlte,
        "paket_kosten": round(paket_kosten),
        "paket_einsparung_jahr": round(paket_einsparung),
        "hwb_vorher": hwb_aktuell,
        "hwb_nachher": round(hwb_nachher, 1),
        "budget_max": budget_max,
    }


GRUNDSTUECK_CHECKLISTE = {
    "vor_besichtigung": {
        "name": "Vor der Besichtigung",
        "icon": "🔍",
        "items": [
            {"id": "flwp", "text": "Flächenwidmungsplan prüfen", "detail": "Bauland-Wohngebiet (BW), Bauland-Kerngebiet (BK), Bauland-gemischt (BG)? Grünland = KEIN Bauen!", "wichtig": True},
            {"id": "bebplan", "text": "Bebauungsplan einholen", "detail": "Bebauungsdichte, Bauweise (offen/geschlossen/gekuppelt), Gebäudehöhe, Baufluchtlinien"},
            {"id": "grundbuch", "text": "Grundbuchauszug anfordern", "detail": "Eigentümer, Belastungen, Dienstbarkeiten, Vorkaufsrechte, Pfandrechte prüfen"},
            {"id": "kataster", "text": "Katasterplan besorgen", "detail": "Exakte Grundstücksgrenzen, Grenzpunkte, Vermessungsurkunden"},
            {"id": "altlasten", "text": "Altlastenkataster prüfen", "detail": "verdachtsflaechen.umweltbundesamt.at — Altlasten können Sanierungspflicht auslösen!"},
        ]
    },
    "bei_besichtigung": {
        "name": "Bei der Besichtigung",
        "icon": "👁",
        "items": [
            {"id": "lage", "text": "Lage und Ausrichtung beurteilen", "detail": "Südausrichtung ideal für Solarenergie, Hanglage = Mehrkosten für Fundament"},
            {"id": "zufahrt", "text": "Zufahrt und Erschließung prüfen", "detail": "Öffentliche Straße vorhanden? Privatweg = Wegerecht nötig!"},
            {"id": "nachbarn", "text": "Nachbarschaft begutachten", "detail": "Lärm, Geruch, Verschattung durch Nachbargebäude, Baumbestand"},
            {"id": "hochwasser", "text": "Hochwasser- und Hangwasserrisiko", "detail": "hora.gv.at — Gefahrenzonen prüfen! HQ30/HQ100/HQ300 Überflutungsflächen"},
            {"id": "boden", "text": "Bodenbeschaffenheit einschätzen", "detail": "Felsiger Boden = teurer Aushub, lehmig = Drainage nötig, Grundwasser?"},
            {"id": "infrastruktur", "text": "Infrastruktur bewerten", "detail": "Öffis, Schule, Kindergarten, Einkauf, Arzt — Entfernungen notieren"},
        ]
    },
    "rechtliches": {
        "name": "Rechtliche Prüfung",
        "icon": "⚖",
        "items": [
            {"id": "aufschliessung", "text": "Aufschließungskosten erfragen", "detail": "Kanal, Wasser, Strom, Gas, Telekom — können 20.000–50.000 € betragen!"},
            {"id": "anschlussgebuehren", "text": "Anschlussgebühren der Gemeinde", "detail": "Kanaleinmündungsabgabe, Wasseranschluss, Verkehrserschließungsbeitrag"},
            {"id": "servitute", "text": "Dienstbarkeiten/Servitute prüfen", "detail": "Wegerechte, Leitungsrechte, Fensterrechte — im Grundbuch C-Blatt"},
            {"id": "bauverbot", "text": "Bauverbote und Schutzgebiete", "detail": "Denkmalschutz, Naturschutz, Wasserschutzgebiet, Lärmschutzzone"},
            {"id": "bausperre", "text": "Bausperre der Gemeinde?", "detail": "Bei Überarbeitung des Flächenwidmungsplans — kann Monate bis Jahre dauern!"},
            {"id": "widmungsaenderung", "text": "Widmungsänderung nötig?", "detail": "Wenn ja: Verfahren dauert 1-3 Jahre, KEIN Rechtsanspruch auf Umwidmung!"},
        ]
    },
    "finanzielles": {
        "name": "Finanzielle Prüfung",
        "icon": "💰",
        "items": [
            {"id": "kaufpreis", "text": "Kaufpreis vergleichen", "detail": "Bodenrichtwerte der Gemeinde, bev.gv.at Statistik, Immobilienpreisspiegel WKO"},
            {"id": "nebenkosten", "text": "Kaufnebenkosten einplanen", "detail": "Grunderwerbsteuer 3,5% + Grundbuch 1,1% + Notar/Anwalt 1-3% + Makler 3,6%"},
            {"id": "foerderung", "text": "Förderungsfähigkeit prüfen", "detail": "Grundstückskauf ist NICHT förderfähig! Aber: Gebührenbefreiung 2024-2026 bis 500.000 €"},
            {"id": "finanzierung", "text": "Finanzierung vorab klären", "detail": "Bankbestätigung holen, Eigenkapital mind. 20%, Wohnbauförderung VOR Kauf beantragen"},
        ]
    },
    "vor_kaufvertrag": {
        "name": "Vor dem Kaufvertrag",
        "icon": "📋",
        "items": [
            {"id": "bodengutachten", "text": "Bodengutachten beauftragen", "detail": "Geologe prüft Tragfähigkeit, Grundwasser, Radon — ca. 800-2.000 €"},
            {"id": "vermessung", "text": "Grenzkataster-Vermessung", "detail": "Exakte Grenzen nur im Grenzkataster verbindlich — Vermessung ca. 2.000-5.000 €"},
            {"id": "bebauungsstudie", "text": "Bebauungsstudie erstellen lassen", "detail": "Architekt prüft was auf dem Grundstück möglich ist (Größe, Position, Höhe)"},
            {"id": "notar", "text": "Notar/Rechtsanwalt beauftragen", "detail": "Kaufvertrag prüfen lassen, Treuhandschaft, Grundbucheintragung"},
            {"id": "vorbescheid", "text": "Bau-Vorbescheid beantragen", "detail": "Manche Gemeinden erteilen Vorbescheid VOR Kauf — gibt Sicherheit!"},
        ]
    },
}

BAUZEITLEISTE_GEWERKE = [
    {"phase": "Planung & Genehmigung", "gewerke": [
        {"name": "Grundlagenermittlung", "wochen_min": 2, "wochen_max": 4, "parallel": False},
        {"name": "Vorentwurf & Entwurf", "wochen_min": 4, "wochen_max": 8, "parallel": False},
        {"name": "Einreichplanung", "wochen_min": 3, "wochen_max": 6, "parallel": False},
        {"name": "Behördenverfahren", "wochen_min": 6, "wochen_max": 16, "parallel": False},
        {"name": "Ausführungsplanung & Vergabe", "wochen_min": 4, "wochen_max": 8, "parallel": True},
    ]},
    {"phase": "Rohbau", "gewerke": [
        {"name": "Erdarbeiten & Fundament", "wochen_min": 2, "wochen_max": 4, "parallel": False},
        {"name": "Keller (falls vorhanden)", "wochen_min": 3, "wochen_max": 5, "parallel": False},
        {"name": "Bodenplatte / EG-Rohbau", "wochen_min": 2, "wochen_max": 4, "parallel": False},
        {"name": "OG-Rohbau", "wochen_min": 2, "wochen_max": 4, "parallel": False},
        {"name": "Dachstuhl & Dacheindeckung", "wochen_min": 2, "wochen_max": 4, "parallel": False},
        {"name": "Fenster & Außentüren", "wochen_min": 1, "wochen_max": 2, "parallel": True},
    ]},
    {"phase": "Ausbau", "gewerke": [
        {"name": "Elektroinstallation (Rohinstallation)", "wochen_min": 2, "wochen_max": 3, "parallel": True},
        {"name": "Sanitär-Rohinstallation", "wochen_min": 2, "wochen_max": 3, "parallel": True},
        {"name": "Heizungsinstallation", "wochen_min": 2, "wochen_max": 3, "parallel": True},
        {"name": "Innenputz", "wochen_min": 2, "wochen_max": 4, "parallel": False},
        {"name": "Estrich & Trocknungszeit", "wochen_min": 4, "wochen_max": 6, "parallel": False},
        {"name": "Fassade & WDVS", "wochen_min": 3, "wochen_max": 5, "parallel": True},
    ]},
    {"phase": "Innenausbau", "gewerke": [
        {"name": "Fliesen & Böden", "wochen_min": 2, "wochen_max": 4, "parallel": False},
        {"name": "Malerarbeiten", "wochen_min": 1, "wochen_max": 3, "parallel": False},
        {"name": "Innentüren & Stiegen", "wochen_min": 1, "wochen_max": 2, "parallel": True},
        {"name": "Sanitär-Fertigmontage", "wochen_min": 1, "wochen_max": 2, "parallel": True},
        {"name": "Elektro-Fertigmontage", "wochen_min": 1, "wochen_max": 2, "parallel": True},
        {"name": "Küche & Einbauten", "wochen_min": 1, "wochen_max": 2, "parallel": True},
    ]},
    {"phase": "Fertigstellung", "gewerke": [
        {"name": "Außenanlagen & Garten", "wochen_min": 2, "wochen_max": 4, "parallel": True},
        {"name": "Reinigung & Mängelbehebung", "wochen_min": 1, "wochen_max": 2, "parallel": False},
        {"name": "Abnahme & Fertigstellungsanzeige", "wochen_min": 1, "wochen_max": 2, "parallel": False},
    ]},
]


def generiere_bauzeitleiste(startmonat, startjahr, mit_keller=True, bautyp="standard"):
    """Generiert detaillierten Bauzeitplan mit konkreten Kalenderwochen."""
    from datetime import timedelta
    startdatum = datetime(startjahr, startmonat, 1)
    aktuelles_datum = startdatum
    phasen_ergebnis = []
    gesamt_wochen = 0

    tempo_faktor = {"schnell": 0.8, "standard": 1.0, "komfort": 1.2}.get(bautyp, 1.0)

    for phase in BAUZEITLEISTE_GEWERKE:
        phase_gewerke = []
        phase_start = aktuelles_datum
        for gewerk in phase["gewerke"]:
            if "Keller" in gewerk["name"] and not mit_keller:
                continue
            dauer_min = max(1, round(gewerk["wochen_min"] * tempo_faktor))
            dauer_max = max(1, round(gewerk["wochen_max"] * tempo_faktor))
            dauer_realistisch = round((dauer_min + dauer_max) / 2)
            gewerk_start = aktuelles_datum
            gewerk_ende = aktuelles_datum + timedelta(weeks=dauer_realistisch)
            phase_gewerke.append({
                "name": gewerk["name"],
                "start": gewerk_start.strftime("%d.%m.%Y"),
                "ende": gewerk_ende.strftime("%d.%m.%Y"),
                "dauer_wochen": dauer_realistisch,
                "parallel": gewerk["parallel"],
            })
            if not gewerk["parallel"]:
                aktuelles_datum = gewerk_ende
                gesamt_wochen += dauer_realistisch

        phase_ende = aktuelles_datum
        phasen_ergebnis.append({
            "phase": phase["phase"],
            "start": phase_start.strftime("%d.%m.%Y"),
            "ende": phase_ende.strftime("%d.%m.%Y"),
            "gewerke": phase_gewerke,
        })

    monate_gesamt = round(gesamt_wochen / 4.33)

    winterpause_hinweis = ""
    for monat in range(startmonat, startmonat + monate_gesamt + 1):
        m = ((monat - 1) % 12) + 1
        if m in (12, 1, 2):
            winterpause_hinweis = "Winterpause Dezember–Februar möglich: Rohbau +2-4 Wochen, Außenarbeiten +2-3 Wochen"
            gesamt_wochen += 3
            break

    return {
        "phasen": phasen_ergebnis,
        "startdatum": startdatum.strftime("%d.%m.%Y"),
        "enddatum": aktuelles_datum.strftime("%d.%m.%Y"),
        "gesamt_wochen": gesamt_wochen,
        "gesamt_monate": round(gesamt_wochen / 4.33),
        "winterpause": winterpause_hinweis,
        "mit_keller": mit_keller,
        "tempo": bautyp,
    }


def vergleiche_neubau_sanierung(wohnflaeche, bundesland, baujahr_bestand=1970, zustand="mittel"):
    """Vergleicht Neubau vs. Sanierung: Kosten, Energie, Förderungen, Lebensdauer."""
    regionalfaktor = REGIONALE_KOSTENFAKTOREN.get(bundesland, 1.0)

    neubau_m2 = 2700 * regionalfaktor
    neubau_gesamt = wohnflaeche * neubau_m2
    neubau_nebenkosten = neubau_gesamt * 0.15
    neubau_total = neubau_gesamt + neubau_nebenkosten
    neubau_hwb = 25
    neubau_heizkosten_jahr = wohnflaeche * neubau_hwb * 0.12
    neubau_instandhaltung_jahr = neubau_gesamt * 0.01
    neubau_foerderung = min(neubau_gesamt * 0.08, 80000)

    zustand_faktor = {"gut": 0.7, "mittel": 1.0, "schlecht": 1.4}.get(zustand, 1.0)
    alter = 2026 - baujahr_bestand
    alter_faktor = 1.0 + max(0, (alter - 30)) * 0.01

    san_m2 = 1400 * regionalfaktor * zustand_faktor * alter_faktor
    san_gesamt = wohnflaeche * san_m2
    san_nebenkosten = san_gesamt * 0.10
    san_total = san_gesamt + san_nebenkosten

    if baujahr_bestand < 1960:
        san_hwb = 80
    elif baujahr_bestand < 1980:
        san_hwb = 55
    elif baujahr_bestand < 2000:
        san_hwb = 40
    else:
        san_hwb = 30
    san_hwb = san_hwb * 0.45

    san_heizkosten_jahr = wohnflaeche * san_hwb * 0.12
    san_instandhaltung_jahr = san_gesamt * 0.005 + neubau_gesamt * 0.008
    san_foerderung = min(san_gesamt * 0.25, 42000)

    neubau_30j = neubau_total - neubau_foerderung + (neubau_heizkosten_jahr + neubau_instandhaltung_jahr) * 30
    san_30j = san_total - san_foerderung + (san_heizkosten_jahr + san_instandhaltung_jahr) * 30

    neubau_daten = {
        "label": "Neubau",
        "baukosten": round(neubau_gesamt),
        "nebenkosten": round(neubau_nebenkosten),
        "gesamtkosten": round(neubau_total),
        "foerderung": round(neubau_foerderung),
        "netto": round(neubau_total - neubau_foerderung),
        "hwb": neubau_hwb,
        "klasse": "A" if neubau_hwb <= 25 else "B",
        "heizkosten_jahr": round(neubau_heizkosten_jahr),
        "instandhaltung_jahr": round(neubau_instandhaltung_jahr),
        "kosten_30_jahre": round(neubau_30j),
        "bauzeit_monate": "12-18",
        "lebensdauer_jahre": "80-100",
        "co2_heizen_kg": round(wohnflaeche * neubau_hwb * 0.05),
        "vorteile": [
            "Modernste Technik und Energiestandards",
            "Freie Grundrissgestaltung",
            "Keine versteckten Mängel",
            "Gewährleistung auf alle Gewerke",
            "Niedrigste Betriebskosten",
        ],
        "nachteile": [
            "Höhere Anfangsinvestition",
            "Grundstück erforderlich",
            "Längere Planungs- und Bauzeit",
            "Graue Energie: CO2 für Neubau höher",
        ],
    }

    san_daten = {
        "label": "Umfassende Sanierung",
        "baukosten": round(san_gesamt),
        "nebenkosten": round(san_nebenkosten),
        "gesamtkosten": round(san_total),
        "foerderung": round(san_foerderung),
        "netto": round(san_total - san_foerderung),
        "hwb": round(san_hwb),
        "klasse": "B" if san_hwb <= 50 else "C",
        "heizkosten_jahr": round(san_heizkosten_jahr),
        "instandhaltung_jahr": round(san_instandhaltung_jahr),
        "kosten_30_jahre": round(san_30j),
        "bauzeit_monate": "4-8",
        "lebensdauer_jahre": "30-50 (Sanierung)",
        "co2_heizen_kg": round(wohnflaeche * san_hwb * 0.08),
        "vorteile": [
            "Deutlich günstiger als Neubau",
            "Kein neues Grundstück nötig",
            "Schnellere Umsetzung",
            "Höhere Förderquoten (bis 42.000 €)",
            "Bestehende Infrastruktur nutzbar",
            "Graue Energie bleibt erhalten",
        ],
        "nachteile": [
            "Grundriss oft nicht optimal änderbar",
            "Versteckte Mängel möglich (Asbest, Schimmel)",
            "Höhere Betriebskosten als Neubau",
            "Kompromisse bei Raumhöhe, Dämmung",
        ],
    }

    empfehlung = ""
    if san_30j < neubau_30j * 0.85:
        empfehlung = "Sanierung deutlich günstiger — empfohlen wenn Substanz gut"
    elif neubau_30j < san_30j * 0.95:
        empfehlung = "Neubau langfristig wirtschaftlicher — empfohlen bei schlechter Substanz"
    else:
        empfehlung = "Beide Optionen finanziell ähnlich — Entscheidung nach Lebensqualität und Grundstück"

    return {
        "neubau": neubau_daten,
        "sanierung": san_daten,
        "empfehlung": empfehlung,
        "differenz_30j": round(abs(neubau_30j - san_30j)),
        "guenstiger_30j": "Sanierung" if san_30j < neubau_30j else "Neubau",
    }


def finde_foerderungen_persoenlich(bundesland, vorhaben, einkommen_netto=0, personen=1, baujahr=0):
    """Findet alle passenden Förderungen basierend auf persönlicher Situation."""
    ergebnisse = []

    bund_foerderungen = [
        {"name": "Sanierungsbonus 2025/2026", "max_betrag": 42000, "typ": "Zuschuss",
         "voraussetzung": "Umfassende thermische Sanierung", "vorhaben_match": ["sanierung"],
         "einkommensgrenzen": False, "info": "sanierungsbonus.at"},
        {"name": "Raus aus Öl und Gas", "max_betrag": 7500, "typ": "Zuschuss",
         "voraussetzung": "Tausch fossile Heizung gegen erneuerbare", "vorhaben_match": ["sanierung", "heizungstausch"],
         "einkommensgrenzen": False, "info": "raus-aus-oel.at"},
        {"name": "Photovoltaik-Förderung (EAG)", "max_betrag": 5700, "typ": "Investitionsförderung",
         "voraussetzung": "PV-Anlage Neubau/Bestand", "vorhaben_match": ["neubau", "sanierung", "pv"],
         "einkommensgrenzen": False, "info": "oem-ag.at"},
        {"name": "Gebührenbefreiung Eigenheim 2024-2026", "max_betrag": 11500, "typ": "Gebührenbefreiung",
         "voraussetzung": "Kauf bis 500.000 €, Eigenbedarf", "vorhaben_match": ["neubau", "kauf"],
         "einkommensgrenzen": False, "info": "bmf.gv.at"},
        {"name": "Handwerkerbonus 2025/2026", "max_betrag": 2000, "typ": "Steuerbonus",
         "voraussetzung": "Handwerkerleistungen am Eigenheim", "vorhaben_match": ["neubau", "sanierung", "umbau"],
         "einkommensgrenzen": False, "info": "bmf.gv.at"},
    ]

    wbf = WOHNBAUFOERDERUNG_DETAIL.get(bundesland, {})
    land_foerderungen = []
    if wbf:
        eg = wbf.get("einkommensgrenzen", {})
        einkommensgrenze = eg.get("1_person", 99999)
        if personen >= 2:
            einkommensgrenze = eg.get("2_personen", 99999) + max(0, personen - 2) * eg.get("je_weitere", 5000)

        einkommensberechtigt = einkommen_netto <= einkommensgrenze or einkommen_netto == 0
        land_foerderungen.append({
            "name": f"Wohnbauförderung {wbf.get('name', bundesland.title())}",
            "max_betrag_text": wbf.get("max_darlehen", "auf Anfrage"),
            "typ": wbf.get("foerderart", "Darlehen"),
            "zinssatz": wbf.get("zinssatz", "variabel"),
            "voraussetzung": f"Einkommensgrenze: {'erfüllt' if einkommensberechtigt else 'NICHT erfüllt'} ({'{:,.0f}'.format(einkommensgrenze).replace(',','.')} € netto/Jahr für {personen} Person(en))",
            "einkommensberechtigt": einkommensberechtigt,
            "vorhaben_match": ["neubau", "sanierung", "kauf"],
            "antrag_vor_baubeginn": wbf.get("antrag_vor_baubeginn", True),
            "kontakt": wbf.get("kontakt", ""),
        })

    for lf in FOERDERUNGEN.get(bundesland, []):
        land_foerderungen.append({
            "name": lf["name"],
            "max_betrag_text": lf["betrag"],
            "typ": "Förderung",
            "voraussetzung": lf.get("info", ""),
            "vorhaben_match": ["neubau", "sanierung"],
            "einkommensberechtigt": True,
        })

    for f in bund_foerderungen:
        if vorhaben in f["vorhaben_match"] or vorhaben == "alle":
            ergebnisse.append({**f, "quelle": "Bund", "passt": True})

    for f in land_foerderungen:
        if vorhaben in f.get("vorhaben_match", []) or vorhaben == "alle":
            ergebnisse.append({**f, "quelle": f"Land {BUNDESLAENDER.get(bundesland, {}).get('name', bundesland.title())}", "passt": True})

    gesamt_max = sum(f.get("max_betrag", 0) for f in ergebnisse if "max_betrag" in f)

    return {
        "foerderungen": ergebnisse,
        "anzahl": len(ergebnisse),
        "gesamt_max_betrag": gesamt_max,
        "bundesland": bundesland,
        "vorhaben": vorhaben,
    }


def vergleiche_baukosten_bundeslaender(wohnflaeche, bautyp="standard"):
    """Vergleicht Baukosten für gleichen Haustyp über alle 9 Bundesländer."""
    kostentyp_map = {
        "standard": "Einfamilienhaus (Standard)",
        "gehoben": "Einfamilienhaus (Gehoben)",
        "passivhaus": "Passivhaus",
        "holzhaus": "Holzhaus (Fertigteil)",
        "reihenhaus": "Reihenhaus",
    }
    typ_key = kostentyp_map.get(bautyp, "Einfamilienhaus (Standard)")
    richtwert = KOSTENRICHTWERTE_2026.get(typ_key, {"min": 2200, "max": 3200})

    vergleich = []
    for land_key, land in BUNDESLAENDER.items():
        faktor = REGIONALE_KOSTENFAKTOREN.get(land_key, 1.0)
        preis_min = richtwert["min"] * faktor * wohnflaeche
        preis_max = richtwert["max"] * faktor * wohnflaeche
        preis_mittel = (preis_min + preis_max) / 2
        preis_m2 = (richtwert["min"] * faktor + richtwert["max"] * faktor) / 2

        wbf = WOHNBAUFOERDERUNG_DETAIL.get(land_key, {})
        max_foerderung = wbf.get("max_darlehen", "k.A.")

        vergleich.append({
            "bundesland": land["name"],
            "kuerzel": land["kuerzel"],
            "faktor": faktor,
            "preis_min": round(preis_min),
            "preis_max": round(preis_max),
            "preis_mittel": round(preis_mittel),
            "preis_m2": round(preis_m2),
            "foerderung": max_foerderung,
            "differenz_pct": round((faktor - 1.0) * 100, 1),
        })

    vergleich.sort(key=lambda x: x["preis_mittel"])
    guenstigstes = vergleich[0]
    teuerstes = vergleich[-1]
    differenz = teuerstes["preis_mittel"] - guenstigstes["preis_mittel"]

    return {
        "vergleich": vergleich,
        "bautyp": typ_key,
        "wohnflaeche": wohnflaeche,
        "guenstigstes": guenstigstes["bundesland"],
        "teuerstes": teuerstes["bundesland"],
        "differenz_euro": round(differenz),
        "differenz_pct": round(differenz / guenstigstes["preis_mittel"] * 100, 1),
    }


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
