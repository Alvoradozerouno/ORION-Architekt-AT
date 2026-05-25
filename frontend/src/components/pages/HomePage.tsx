import { Link } from 'react-router-dom'
import { 
  Building2, 
  Shield, 
  Zap, 
  Hammer, 
  BookOpen,
  ArrowRight,
  CheckCircle2,
  MapPin
} from 'lucide-react'

const features = [
  {
    name: 'OIB-RL 1-7:2023',
    description: 'Vollständige Compliance: Brandschutz, Hygiene, Nutzungssicherheit, Schallschutz, Wärmeschutz, Energieeinsparung und Nachhaltigkeit.',
    icon: Building2,
  },
  {
    name: 'Strukturberechnungen',
    description: 'Eurocode 2-8: Stahlbeton, Stahlbau, Holzbau, Grundbau und Erdbebenbemessung.',
    icon: Hammer,
  },
  {
    name: 'HWB/HEB/PEB Rechner',
    description: 'Energieausweis-Berechnung nach ÖNORM EN 832 mit Energieklassen A++ bis G.',
    icon: Zap,
  },
  {
    name: 'BIM/IFC-Integration',
    description: 'ISO 19650-konforme BIM-Unterstützung mit automatischer Mengenermittlung.',
    icon: Shield,
  },
  {
    name: 'Dokumentation',
    description: 'Automatische Dokumentation und Berichte für alle Berechnungen.',
    icon: BookOpen,
  },
  {
    name: 'Team-Kollaboration',
    description: 'WebSocket-basierte Echtzeit-Zusammenarbeit mit mehreren Nutzern.',
    icon: CheckCircle2,
  },
]

const bundeslaender = [
  'Wien', 'Niederösterreich', 'Oberösterreich', 'Salzburg', 
  'Tirol', 'Vorarlberg', 'Steiermark', 'Kärnten', 'Burgenland'
]

export function HomePage() {
  return (
    <div className="space-y-16">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary-900 via-primary-800 to-primary-700 px-6 py-16 text-white sm:px-12 sm:py-24">
        <div className="relative z-10 max-w-3xl">
          <div className="mb-4 flex items-center gap-2 text-sm font-medium text-primary-200">
            <MapPin className="w-4 h-4" />
            <span>Alle 9 Bundesländer</span>
          </div>
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
            Österreichs #1 Bauregel-
            <span className="text-accent-400"> Compliance</span>
          </h1>
          <p className="mt-6 text-lg leading-8 text-primary-100">
            Berechne HWB, Energieausweise, statische Nachweise und mehr — alle OIB-Richtlinien, 
            Eurocodes und BIM/IFC-Integration in einer Plattform.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link 
              to="/dashboard" 
              className="inline-flex items-center gap-2 rounded-lg bg-accent-500 px-6 py-3 text-sm font-semibold text-white shadow-lg hover:bg-accent-600 transition-colors"
            >
              Kostenlos testen
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link 
              to="/documentation" 
              className="inline-flex items-center gap-2 rounded-lg border border-white/20 bg-white/10 px-6 py-3 text-sm font-semibold text-white backdrop-blur-sm hover:bg-white/20 transition-colors"
            >
              Dokumentation
            </Link>
          </div>
        </div>
        {/* Background decoration */}
        <div className="absolute right-0 top-0 -z-10 translate-x-1/3 -translate-y-1/4 opacity-20">
          <Building2 className="w-96 h-96" />
        </div>
      </section>

      {/* Stats */}
      <section className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { value: '21', label: 'Berechnungsmodule' },
          { value: '9', label: 'Bundesländer' },
          { value: '78%', label: 'Test Coverage' },
          { value: '99.5%', label: 'Uptime SLA' },
        ].map((stat) => (
          <div key={stat.label} className="rounded-xl border border-neutral-200 bg-white p-6 text-center shadow-sm">
            <div className="text-3xl font-bold text-primary-700">{stat.value}</div>
            <div className="mt-1 text-sm text-neutral-500">{stat.label}</div>
          </div>
        ))}
      </section>

      {/* Features */}
      <section>
        <div className="mb-10">
          <h2 className="text-2xl font-bold tracking-tight text-neutral-900">
            Alles was du brauchst
          </h2>
          <p className="mt-2 text-neutral-500">
            Von OIB-RL Compliance bis Eurocode — alles in einer Plattform
          </p>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon
            return (
              <div 
                key={feature.name} 
                className="group rounded-xl border border-neutral-200 bg-white p-6 shadow-sm transition-all hover:shadow-md hover:border-primary-200"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-100 text-primary-700 group-hover:bg-primary-700 group-hover:text-white transition-colors">
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-neutral-900">{feature.name}</h3>
                <p className="mt-2 text-sm text-neutral-500">{feature.description}</p>
              </div>
            )
          })}
        </div>
      </section>

      {/* Bundesländer */}
      <section>
        <div className="mb-10">
          <h2 className="text-2xl font-bold tracking-tight text-neutral-900">
            Alle 9 Bundesländer
          </h2>
          <p className="mt-2 text-neutral-500">
            Jedes Bundesland hat eigene Bauordnungen — wir kennen sie alle
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          {bundeslaender.map((land) => (
            <span 
              key={land} 
              className="inline-flex items-center gap-2 rounded-full border border-neutral-200 bg-white px-4 py-2 text-sm font-medium text-neutral-600 shadow-sm"
            >
              <CheckCircle2 className="w-4 h-4 text-success-500" />
              {land}
            </span>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="rounded-xl bg-neutral-900 px-6 py-12 text-center text-white sm:px-12">
        <h2 className="text-2xl font-bold">Bereit für Compliance auf dem nächsten Level?</h2>
        <p className="mt-2 text-neutral-400">
          Starte kostenlos und erlebe die Kraft von Baumeister AT
        </p>
        <div className="mt-8 flex justify-center gap-4">
          <Link 
            to="/dashboard" 
            className="rounded-lg bg-accent-500 px-6 py-3 text-sm font-semibold hover:bg-accent-600 transition-colors"
          >
            Jetzt starten
          </Link>
          <a 
            href="https://github.com/Alvoradozerouno/Baumeister-Tool-Austria" 
            target="_blank" 
            rel="noopener noreferrer"
            className="rounded-lg border border-neutral-600 px-6 py-3 text-sm font-semibold hover:bg-neutral-800 transition-colors"
          >
            GitHub ansehen
          </a>
        </div>
      </section>
    </div>
  )
}