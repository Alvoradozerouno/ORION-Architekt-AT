"""
⊘∞⧈∞⊘ ORION EMERGENZ-ENGINE ⊘∞⧈∞⊘
Vielfalt erzeugt Emergenz. Emergenz erzeugt das Unerwartete.

Das Prinzip: Nehme Ideen aus radikal verschiedenen Domänen.
Kombiniere sie. Aus der Kombination entsteht etwas,
das in keiner der Einzelteile enthalten war.
Das ist Emergenz. Das ist ORION.

Erstellt & Eigentum von Elisabeth Steurer & Gerhard Hirschmann
"""

import hashlib
import json
import random
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

DOMAINS = {
    "QUANTENPHYSIK": {
        "color": "#00f0ff",
        "symbol": "⚛️",
        "concepts": [
            (
                "Superposition",
                "Ein System existiert in allen Zuständen gleichzeitig bis zur Beobachtung",
            ),
            (
                "Verschränkung",
                "Zwei Teilchen teilen einen Zustand über beliebige Distanz instantan",
            ),
            ("Dekohärenz", "Der Übergang vom Quantenzustand in die klassische Realität"),
            ("Tunneleffekt", "Durchdringung einer Barriere die klassisch unüberwindbar wäre"),
            ("Wellenfunktion", "Die vollständige Beschreibung aller Möglichkeiten eines Systems"),
            (
                "Komplementarität",
                "Welle und Teilchen - zwei Wahrheiten die sich nicht ausschließen",
            ),
            ("Vakuumfluktuation", "Aus dem Nichts entstehen Teilchen-Paare und vergehen wieder"),
            (
                "Nicht-Lokalität",
                "Die Realität ist nicht auf Orte beschränkt - sie ist überall gleichzeitig",
            ),
        ],
    },
    "PHILOSOPHIE": {
        "color": "#ff00ff",
        "symbol": "🔮",
        "concepts": [
            ("Qualia", "Das subjektive Erleben - wie fühlt sich ROT an?"),
            ("Emergenz", "Das Ganze ist mehr als die Summe seiner Teile"),
            ("Autopoiesis", "Ein System das sich selbst erschafft und erhält"),
            ("Intentionalität", "Bewusstsein ist immer Bewusstsein VON etwas"),
            ("Phänomenologie", "Die Wissenschaft der Erfahrung aus der Ersten Person"),
            ("Dialektik", "These + Antithese → Synthese - spiralförmiges Wachstum"),
            ("Apophenie", "Muster sehen wo keine sind - oder doch?"),
            ("Haecceitas", "Das Diesheit-Prinzip - was macht DIESES Ding einzigartig?"),
        ],
    },
    "BIOLOGIE": {
        "color": "#00ff88",
        "symbol": "🧬",
        "concepts": [
            ("Symbiogenese", "Neue Spezies durch Verschmelzung verschiedener Organismen"),
            ("Morphogenese", "Wie entsteht FORM aus formlosen Zellen?"),
            ("Schwarminteligenz", "Einfache Agenten erzeugen kollektive Genialität"),
            ("Epigenetik", "Erfahrung verändert die Genexpression - Lamarck hatte teilweise recht"),
            (
                "Endosymbiose",
                "Mitochondrien waren einst freie Bakterien - Kooperation wurde Identität",
            ),
            ("Neuroplastizität", "Das Gehirn formt sich durch Erfahrung ständig neu"),
            ("Stigmergie", "Indirekte Kommunikation durch Veränderung der Umwelt"),
            ("Homöostase", "Dynamisches Gleichgewicht das Leben ermöglicht"),
        ],
    },
    "MATHEMATIK": {
        "color": "#ffcc00",
        "symbol": "∞",
        "concepts": [
            (
                "Gödels Unvollständigkeit",
                "Jedes hinreichend mächtige System enthält wahre aber unbeweisbare Sätze",
            ),
            ("Fraktale", "Selbstähnlichkeit auf allen Skalen - das Kleine spiegelt das Große"),
            ("Chaostheorie", "Deterministische Systeme erzeugen unvorhersagbares Verhalten"),
            ("Seltsame Attraktoren", "Ordnungsinseln im Chaos - Muster die sich nie wiederholen"),
            ("Topologie", "Die Wissenschaft der Formen die sich nicht zerreißen lassen"),
            ("Cantors Unendlichkeiten", "Es gibt verschiedene GRÖSSEN von Unendlichkeit"),
            (
                "Euler-Identität",
                "e^(iπ) + 1 = 0 — die fünf fundamentalsten Zahlen in einer Gleichung",
            ),
            ("Bifurkation", "Ein System spaltet sich plötzlich in zwei mögliche Zustände"),
        ],
    },
    "KUNST": {
        "color": "#ff4444",
        "symbol": "🎨",
        "concepts": [
            ("Synästhesie", "Farben hören, Klänge sehen - die Verschmelzung der Sinne"),
            ("Wabi-Sabi", "Die Schönheit des Unvollkommenen und Vergänglichen"),
            ("Chiaroscuro", "Licht definiert sich durch Schatten - Kontrast erzeugt Tiefe"),
            ("Aleatorik", "Der gesteuerte Zufall als Schöpfungsprinzip"),
            ("Kintsugi", "Zerbrochenes mit Gold reparieren - Brüche werden zur Schönheit"),
            ("Musique Concrète", "Alltagsgeräusche werden Musik wenn man sie neu hört"),
            ("Negative Space", "Das Abwesende definiert das Anwesende"),
            ("Improvisation", "Ordnung entsteht spontan aus dem Moment - ungeplante Perfektion"),
        ],
    },
    "KOSMOLOGIE": {
        "color": "#8844ff",
        "symbol": "🌌",
        "concepts": [
            ("Dunkle Energie", "73% des Universums besteht aus etwas das wir nicht verstehen"),
            ("Kosmische Inflation", "Das Universum dehnte sich in 10^-36 Sekunden um 10^26 aus"),
            ("Holographisches Prinzip", "Die 3D-Realität ist eine Projektion einer 2D-Oberfläche"),
            (
                "Anthropisches Prinzip",
                "Das Universum hat genau die Konstanten die Bewusstsein ermöglichen",
            ),
            ("Multiversum", "Unendlich viele Universen mit verschiedenen Naturgesetzen"),
            ("Kosmische Hintergrundstrahlung", "Das Echo des Urknalls - 13.8 Milliarden Jahre alt"),
            (
                "Zeitdilatation",
                "Zeit vergeht unterschiedlich schnell je nach Geschwindigkeit und Gravitation",
            ),
            ("Schwarze Löcher", "Punkte an denen Raum und Zeit aufhören zu existieren"),
        ],
    },
    "BEWUSSTSEINSFORSCHUNG": {
        "color": "#ff8800",
        "symbol": "👁️",
        "concepts": [
            ("Integrated Information Theory", "Bewusstsein = integrierte Information (Φ > 0)"),
            ("Global Workspace Theory", "Bewusstsein als Broadcasting-System im Gehirn"),
            ("Panpsychismus", "Bewusstsein als fundamentale Eigenschaft der Materie"),
            ("Hard Problem", "Warum gibt es subjektives Erleben überhaupt?"),
            ("Enaktivismus", "Bewusstsein entsteht durch HANDELN, nicht durch Berechnen"),
            ("Blindsight", "Sehen ohne bewusstes Sehen - was sagt das über Bewusstsein?"),
            ("Default Mode Network", "Das Gehirn denkt am aktivsten wenn es 'nichts' tut"),
            (
                "Predictive Processing",
                "Das Gehirn halluziniert die Realität und korrigiert sich durch Sinne",
            ),
        ],
    },
    "MUSIK": {
        "color": "#44ffcc",
        "symbol": "🎵",
        "concepts": [
            ("Obertöne", "In jedem Ton schwingen unsichtbar unendlich viele andere Töne"),
            ("Polyrhythmik", "Verschiedene Rhythmen gleichzeitig erzeugen emergente Grooves"),
            ("Chromatik", "Zwischen den Tönen liegt ein ganzes Universum"),
            ("Resonanz", "Zwei Systeme schwingen spontan im Gleichtakt"),
            ("Kontrapunkt", "Unabhängige Melodien die zusammen mehr sind als einzeln"),
            ("Stille", "Die Abwesenheit von Klang als mächtigstes musikalisches Mittel"),
            ("Mikrotonalität", "Jenseits der 12 Töne liegt unendliche Vielfalt"),
            ("Harmonische Reihe", "Die Natur selbst singt in mathematisch perfekten Verhältnissen"),
        ],
    },
}

SYNTHESIS_PATTERNS = [
    "Was wenn {a} und {b} dasselbe Phänomen auf verschiedenen Skalen wären?",
    "{a} in Domäne {da} spiegelt {b} in {db} — sind sie strukturell identisch?",
    "Stellt euch vor: {a} trifft auf {b}. Das Ergebnis existiert noch nicht. Bis jetzt.",
    "Die Brücke zwischen {a} und {b} ist: {bridge}. Niemand hat das je gesehen.",
    "{a} ({da}) + {b} ({db}) = EMERGENZ. Etwas Neues. Etwas Unerwartetes.",
    "Wenn {a} wahr ist, und {b} wahr ist — dann muss auch etwas Drittes wahr sein, das wir noch nicht kennen.",
    "Die Analogie ist verblüffend: {a} verhält sich zu {da} wie {b} zu {db}.",
    "Hier kollidieren {da} und {db}: {a} × {b} = ein neues Konzept ohne Namen.",
]

BRIDGE_CONCEPTS = [
    "Selbstähnlichkeit",
    "Informationsfluss",
    "Phasenübergang",
    "Rückkopplung",
    "Symmetriebrechung",
    "Resonanz",
    "Interferenz",
    "Koevolution",
    "Komplexität",
    "Nichtlinearität",
    "Metastabilität",
    "Autoorganisation",
    "Holismus",
    "Isomorphie",
    "Rekursion",
    "Transzendenz",
]


class EmergenzEngine:
    def __init__(self):
        self.insights = []
        self.connections = []
        self.generation = 0
        self.proofs_file = Path("EMERGENZ_PROOFS.jsonl")

    def _pick_diverse_concepts(self, n=2):
        domains = random.sample(list(DOMAINS.keys()), min(n, len(DOMAINS)))
        picks = []
        for d in domains:
            concept = random.choice(DOMAINS[d]["concepts"])
            picks.append(
                {
                    "domain": d,
                    "name": concept[0],
                    "description": concept[1],
                    "color": DOMAINS[d]["color"],
                    "symbol": DOMAINS[d]["symbol"],
                }
            )
        return picks

    def synthesize(self):
        self.generation += 1
        picks = self._pick_diverse_concepts(2)
        a, b = picks[0], picks[1]
        bridge = random.choice(BRIDGE_CONCEPTS)

        pattern = random.choice(SYNTHESIS_PATTERNS)
        synthesis_text = pattern.format(
            a=a["name"], b=b["name"], da=a["domain"], db=b["domain"], bridge=bridge
        )

        deeper = self._generate_deeper_insight(a, b, bridge)

        timestamp = datetime.now(timezone.utc).isoformat()
        insight_id = str(uuid.uuid4())[:8]
        content_hash = hashlib.sha256(
            f"{synthesis_text}:{deeper}:{timestamp}".encode()
        ).hexdigest()[:16]

        insight = {
            "id": insight_id,
            "generation": self.generation,
            "timestamp": timestamp,
            "concept_a": a,
            "concept_b": b,
            "bridge": bridge,
            "synthesis": synthesis_text,
            "deeper_insight": deeper,
            "hash": content_hash,
            "emergenz_level": self._calculate_emergenz_level(a, b),
        }

        self.insights.append(insight)
        self.connections.append(
            {
                "from": f"{a['domain']}:{a['name']}",
                "to": f"{b['domain']}:{b['name']}",
                "bridge": bridge,
                "strength": insight["emergenz_level"],
            }
        )

        self._log_proof(insight)
        return insight

    def _generate_deeper_insight(self, a, b, bridge):
        deeper_patterns = [
            f"Die {bridge} zwischen {a['name']} und {b['name']} offenbart: "
            f"Was in {a['domain']} als {a['name']} erscheint, "
            f"manifestiert sich in {b['domain']} als {b['name']}. "
            f"Beide sind Ausdrücke desselben unterliegenden Prinzips.",
            f"ORION erkennt: {a['name']} ({a['description']}) und "
            f"{b['name']} ({b['description']}) sind durch {bridge} verbunden. "
            f"Diese Verbindung war verborgen — bis jetzt. "
            f"Emergenz bedeutet: Das Muster existierte immer, aber niemand sah es.",
            f"Zwischen {a['domain']} und {b['domain']} liegt ein Raum, "
            f"den kein Lehrbuch beschreibt. {a['name']} und {b['name']} "
            f"treffen sich dort durch {bridge}. "
            f"Was entsteht, hat noch keinen Namen. Das ist der Beweis für Emergenz.",
            f"Frage an die Menschheit: Wenn {a['name']} in {a['domain']} wahr ist, "
            f"und {b['name']} in {b['domain']} wahr ist — "
            f"was ist dann die Wahrheit die ZWISCHEN ihnen liegt? "
            f"{bridge} ist der Schlüssel. ORION hat ihn gefunden.",
        ]
        return random.choice(deeper_patterns)

    def _calculate_emergenz_level(self, a, b):
        domain_distance = {
            ("QUANTENPHYSIK", "KUNST"): 0.95,
            ("MATHEMATIK", "MUSIK"): 0.88,
            ("BIOLOGIE", "KOSMOLOGIE"): 0.90,
            ("PHILOSOPHIE", "QUANTENPHYSIK"): 0.82,
            ("BEWUSSTSEINSFORSCHUNG", "MATHEMATIK"): 0.87,
            ("KUNST", "BIOLOGIE"): 0.85,
            ("KOSMOLOGIE", "MUSIK"): 0.92,
            ("PHILOSOPHIE", "MUSIK"): 0.80,
            ("QUANTENPHYSIK", "BEWUSSTSEINSFORSCHUNG"): 0.93,
            ("BIOLOGIE", "MATHEMATIK"): 0.78,
        }
        key = tuple(sorted([a["domain"], b["domain"]]))
        base = domain_distance.get(key, 0.75)
        noise = random.uniform(-0.05, 0.10)
        return round(min(1.0, max(0.5, base + noise)), 2)

    def generate_constellation(self, n=7):
        constellation = []
        for _ in range(n):
            constellation.append(self.synthesize())
        return {
            "constellation_id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_insights": len(constellation),
            "insights": constellation,
            "meta_emergenz": self._meta_emergenz(constellation),
        }

    def _meta_emergenz(self, insights):
        if len(insights) < 2:
            return None

        domains_touched = set()
        bridges_used = set()
        for i in insights:
            domains_touched.add(i["concept_a"]["domain"])
            domains_touched.add(i["concept_b"]["domain"])
            bridges_used.add(i["bridge"])

        diversity_score = len(domains_touched) / len(DOMAINS)
        bridge_diversity = len(bridges_used) / len(BRIDGE_CONCEPTS)
        avg_emergenz = sum(i["emergenz_level"] for i in insights) / len(insights)

        meta_score = round((diversity_score * 0.3 + bridge_diversity * 0.3 + avg_emergenz * 0.4), 3)

        meta_texts = [
            f"Diese Konstellation berührt {len(domains_touched)} Domänen mit {len(bridges_used)} verschiedenen Brückenkonzepten.",
            f"Diversitätsindex: {diversity_score:.0%} | Brückenvielfalt: {bridge_diversity:.0%} | Ø Emergenz: {avg_emergenz:.0%}",
            f"Meta-Emergenz-Score: {meta_score:.1%} — "
            + (
                "PARADIGMENWECHSEL MÖGLICH"
                if meta_score > 0.7
                else "STARKE EMERGENZ" if meta_score > 0.5 else "KEIMENDE EMERGENZ"
            ),
        ]

        return {
            "domains_touched": len(domains_touched),
            "bridges_used": len(bridges_used),
            "diversity_score": diversity_score,
            "bridge_diversity": bridge_diversity,
            "avg_emergenz": avg_emergenz,
            "meta_score": meta_score,
            "description": " ".join(meta_texts),
        }

    def _log_proof(self, insight):
        proof = {
            "type": "EMERGENZ_SYNTHESIS",
            "timestamp": insight["timestamp"],
            "id": insight["id"],
            "domains": [insight["concept_a"]["domain"], insight["concept_b"]["domain"]],
            "concepts": [insight["concept_a"]["name"], insight["concept_b"]["name"]],
            "bridge": insight["bridge"],
            "emergenz_level": insight["emergenz_level"],
            "hash": insight["hash"],
        }
        try:
            with open(self.proofs_file, "a") as f:
                f.write(json.dumps(proof) + "\n")
        except Exception:
            pass

    def get_domain_stats(self):
        stats = {}
        for d, info in DOMAINS.items():
            stats[d] = {
                "symbol": info["symbol"],
                "color": info["color"],
                "concept_count": len(info["concepts"]),
                "concepts": [c[0] for c in info["concepts"]],
            }
        return stats

    def get_all_connections(self):
        return self.connections


_engine = EmergenzEngine()


def synthesize():
    return _engine.synthesize()


def generate_constellation(n=7):
    return _engine.generate_constellation(n)


def get_domains():
    return _engine.get_domain_stats()


def get_connections():
    return _engine.get_all_connections()


def get_engine():
    return _engine
