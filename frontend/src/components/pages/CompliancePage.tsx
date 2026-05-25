import { Shield } from 'lucide-react'

const complianceModules = [
  {
    id: 'oib-rl-1',
    title: 'OIB-RL 1: Mechanik & Tragfähigkeit',
    standard: 'OIB-RL 1:2023',
    status: 'implemented',
    description: 'Tragfähigkeit und mechanische Widerstandsfähigkeit',
  },
  {
    id: 'oib-rl-2',
    title: 'OIB-RL 2: Brandschutz',
    standard: 'OIB-RL 2:2023',
    status: 'implemented',
    description: 'Brandverhalten von Baustoffen, Brandschutzmaßnahmen',
  },
  {
    id: 'oib-rl-3',
    title: 'OIB-RL 3: Hygiene, Gesundheit, Umweltschutz',
    standard: 'OIB-RL 3:2023',
    status: 'implemented',
    description: 'Schadstofffreiheit, Trinkwasser, Abwasser, Luft',
  },
  {
    id: 'oib-rl-4',
    title: 'OIB-RL 4: Nutzungssicherheit',
    standard: 'OIB-RL 4:2023',
    status: 'implemented',
    description: 'Stolpern, Ausrutschen, Durchsturzsicherung',
  },
  {
    id: 'oib-rl-5',
    title: 'OIB-RL 5: Schallschutz',
    standard: 'OIB-RL 5:2023',
    status: 'implemented',
    description: 'Trittschall, Luftschall, Haustechnikschall',
  },
  {
    id: 'oib-rl-6',
    title: 'OIB-RL 6: Energieeinsparung',
    standard: 'OIB-RL 6:2023',
    status: 'implemented',
    description: 'HWB, HEB, PEB, CO2-Emissionen, fGEE ≤ 0,75',
  },
  {
    id: 'oib-rl-7',
    title: 'OIB-RL 7: Nachhaltigkeit',
    standard: 'OIB-RL 7:2023',
    status: 'base',
    description: 'Grundlagendokumentation für Kreislaufwirtschaft',
  },
  {
    id: 'ec-2',
    title: 'Eurocode 2: Stahlbeton',
    standard: 'EN 1992',
    status: 'implemented',
    description: 'Bemessung und Konstruktion von Stahlbetontragwerken',
  },
  {
    id: 'ec-3',
    title: 'Eurocode 3: Stahlbau',
    standard: 'EN 1993',
    status: 'implemented',
    description: 'Bemessung und Konstruktion von Stahltragwerken',
  },
  {
    id: 'ec-5',
    title: 'Eurocode 5: Holzbau',
    standard: 'EN 1995',
    status: 'implemented',
    description: 'Bemessung und Konstruktion von Holztragwerken',
  },
  {
    id: 'ec-7',
    title: 'Eurocode 7: Grundbau',
    standard: 'EN 1997',
    status: 'implemented',
    description: 'Entwurf, Berechnung und Bemessung in der Geotechnik',
  },
  {
    id: 'ec-8',
    title: 'Eurocode 8: Erdbeben',
    standard: 'EN 1998',
    status: 'implemented',
    description: 'Auslegung von Tragwerken gegen Erdbeben',
  },
]

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'implemented':
      return <span className="badge badge-success">✅ Implementiert</span>
    case 'base':
      return <span className="badge badge-warning">️ Basis</span>
    case 'planned':
      return <span className="badge badge-default">📋 Geplant</span>
    default:
      return <span className="badge badge-default">❓ Unbekannt</span>
  }
}

export function CompliancePage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 flex items-center gap-2">
          <Shield className="w-6 h-6" />
          Compliance Module
        </h1>
        <p className="mt-1 text-neutral-500">
          Übersicht aller implementierten Normen und Richtlinien
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card p-4 text-center">
          <div className="text-3xl font-bold text-success-500">7</div>
          <div className="text-sm text-neutral-500">OIB-RL</div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-3xl font-bold text-success-500">5</div>
          <div className="text-sm text-neutral-500">Eurocode</div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-3xl font-bold text-primary-700">9</div>
          <div className="text-sm text-neutral-500">Bundesländer</div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-3xl font-bold text-accent">21</div>
          <div className="text-sm text-neutral-500">Berechnungen</div>
        </div>
      </div>

      {/* Modules Grid */}
      <div className="grid gap-4">
        {complianceModules.map((module) => (
          <div key={module.id} className="card hover:shadow-md transition-shadow">
            <div className="flex flex-col sm:flex-row sm:items-center gap-4 p-6">
              <div className="flex-1">
                <h3 className="font-semibold text-neutral-900">{module.title}</h3>
                <p className="text-sm text-neutral-500 mt-1">{module.description}</p>
                <p className="text-xs text-primary-600 mt-2">{module.standard}</p>
              </div>
              <div className="flex items-center gap-2">
                {getStatusBadge(module.status)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}