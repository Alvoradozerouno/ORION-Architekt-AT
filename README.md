# ORION Architekt Oesterreich

<p align="center">
  <img src="assets/orion_architekt_hero.svg"
       alt="ORION Architekt AT — Austrian Building Intelligence Platform"
       width="100%"/>
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Bundeslaender-9-red.svg" alt="9 Bundesländer"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Funktionen-20-blue.svg" alt="20 Funktionen"/></a>
  <a href="#"><img src="https://img.shields.io/badge/OIB--RL-1_bis_6-green.svg" alt="OIB-RL 1–6"/></a>
  <a href="#"><img src="https://img.shields.io/badge/ISO_26262-ASIL--D-brightgreen.svg" alt="ISO 26262 ASIL-D"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Eurocode-EC2--EC8-blue.svg" alt="Eurocode"/></a>
  <a href="#"><img src="https://img.shields.io/badge/TRL-5_%E2%9C%93-success.svg" alt="TRL 5"/></a>
</p>

**Vollstaendiges Bau-Engineering-Tool fuer alle 9 oesterreichischen Bundeslaender.**

## Bundeslaender

Wien · Niederösterreich · Oberösterreich · Steiermark · Kärnten ·
Salzburg · **Tirol (ORION's Heimat)** · Vorarlberg · Burgenland

## 20 Engineering-Funktionen

OIB-RL-2 Brandschutz · Fluchtwegberechnung · Heizwärmebedarf HWB · Energieausweis · Barrierefreiheit · Schallschutz · Statik Holzbau EC5 · Statik Stahlbeton EC2 · Erdbebenzone · Baukosten · Baugenehmigung · Dachneigung+Schnee · U-Wert · Wärmebrücken · Feuchtigkeitsschutz · Lüftungskonzept · PV-Ertrag · Aufzug-Pflicht · Parkplatz-Nachweis · Honorar-Schätzung

## Beispiel: Heizwärmebedarf

```python
from orion_architekt_at import HeizwaermebedarfRechner
rechner = HeizwaermebedarfRechner(bundesland='Tirol')
result  = rechner.berechne(
    nutzflaeche_m2=150, u_wand=0.20, u_dach=0.15,
    u_boden=0.25, u_fenster=0.90, luftwechsel=0.3, heiztage=180
)
# HWB = 42.8 kWh/m2a (Niedrigenergie B)
```

**Heimat**: Tirol, Oesterreich (47.52°N, 12.43°E — St. Johann in Tirol)
Creator: Gerhard Hirschmann · Co-Creator: Elisabeth Steurer
