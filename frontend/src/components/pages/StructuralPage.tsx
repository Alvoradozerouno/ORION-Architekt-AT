import { Hammer, CheckCircle, AlertCircle } from 'lucide-react'

const structuralModules = [
  { id: 'ec2', name: 'Eurocode 2 - Stahlbeton', icon: '🏗️', desc: 'Bemessung von Stahlbetonbauteilen' },
  { id: 'ec3', name: 'Eurocode 3 - Stahlbau', icon: '🔩', desc: 'Bemessung von Stahlkonstruktionen' },
  { id: 'ec5', name: 'Eurocode 5 - Holzbau', icon: '', desc: 'Bemessung von Holztragwerken' },
  { id: 'ec7', name: 'Eurocode 7 - Grundbau', icon: '🏔️', desc: 'Geotechnische Bemessung' },
  { id: 'ec8', name: 'Eurocode 8 - Erdbeben', icon: '', desc: 'Erdbebenbemessung' },
  { id: 'lasten', name: 'Einwirkungen (EC1)', icon: '⚖️', desc: 'Schneelast, Windlast, Nutzlast' },
]

export function StructuralPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 flex items-center gap-2">
          <Hammer className="w-6 h-6 text-accent" />
          Statik & Eurocodes
        </h1>
        <p className="mt-1 text-neutral-500">Strukturberechnungen nach Eurocodes</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {structuralModules.map((module) => (
          <div key={module.id} className="card hover:shadow-md transition-all cursor-pointer group">
            <div className="p-6">
              <div className="text-4xl mb-4">{module.icon}</div>
              <h3 className="font-semibold text-neutral-900 group-hover:text-primary transition-colors">{module.name}</h3>
              <p className="text-sm text-neutral-500 mt-2">{module.desc}</p>
              <div className="mt-4 flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-success-500" />
                <span className="text-xs font-medium text-success-600">Verfügbar</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="card bg-primary-50 border-primary-200">
        <div className="card-content flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-primary-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-semibold text-primary-900">Hinweis zur Verwendung</h3>
            <p className="text-sm text-primary-700 mt-1">
              Die statischen Berechnungen dienen als Planungshilfe und ersetzen nicht die offizielle Statiknachweisführung 
              durch einen befugten Ziviltechniker oder Statiker. Für offizielle Einreichungen ist die Unterschrift eines 
              autorisierten Sachverständigen erforderlich.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}