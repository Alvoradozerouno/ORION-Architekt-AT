import { useState } from 'react'
import { Zap, Thermometer, Wind, Sun, Droplets, Building2 } from 'lucide-react'

interface EnergyParams {
  flaeche: number
  uWert: number
  klimazone: number
  luftwechsel: number
  innereWaerme: number
}

interface EnergyResult {
  hwb: number
  heb: number
  peb: number
  co2: number
  klasse: string
  konform: boolean
}

const klimazonen = [
  { value: 1, label: 'Zone 1 - Mild (Wiener Becken)', tage: 3200 },
  { value: 2, label: 'Zone 2 - Mittel (Mittelgebirge)', tage: 3800 },
  { value: 3, label: 'Zone 3 - Alpin (Hochalpin)', tage: 4800 },
]

const energieKlassen: Record<string, number[]> = {
  'A++': [0, 10],
  'A+': [10, 25],
  'A': [25, 50],
  'B': [50, 75],
  'C': [75, 100],
  'D': [100, 150],
  'E': [150, 200],
  'F': [200, 250],
  'G': [250, 9999],
}

function berechneHWB(params: EnergyParams): EnergyResult {
  const heizgradtage = klimazonen.find(k => k.value === params.klimazone)?.tage || 3800
  
  const leitwert = params.flaeche * params.uWert
  const raumvolumen = params.flaeche * 2.7
  const lueftung = 0.34 * params.luftwechsel * raumvolumen
  const qHt = (leitwert + lueftung) * heizgradtage * 24 / 1000
  
  const qInt = params.innereWaerme * params.flaeche * 8760 / 1000
  const qSol = params.flaeche * 15 * params.klimazone
  const qGains = 0.95 * (qInt + qSol)
  
  let hwb = (qHt - qGains) / params.flaeche
  hwb = Math.max(0, hwb)
  
  let klasse = 'G'
  for (const [k, [min, max]] of Object.entries(energieKlassen)) {
    if (hwb >= min && hwb < max) {
      klasse = k
      break
    }
  }
  
  return {
    hwb: Math.round(hwb * 10) / 10,
    heb: Math.round(hwb * 1.15 * 10) / 10,
    peb: Math.round(hwb * 1.15 * 1.1 * 10) / 10,
    co2: Math.round(hwb * 0.22 * 10) / 10,
    klasse,
    konform: hwb <= 75,
  }
}

export function EnergyPage() {
  const [params, setParams] = useState<EnergyParams>({
    flaeche: 150,
    uWert: 0.18,
    klimazone: 3,
    luftwechsel: 0.4,
    innereWaerme: 2.0,
  })
  const [result, setResult] = useState<EnergyResult | null>(null)

  const handleCalculate = () => {
    setResult(berechneHWB(params))
  }

  const getKlasseFarbe = (klasse: string) => {
    const colors: Record<string, string> = {
      'A++': 'text-emerald-600',
      'A+': 'text-emerald-500',
      'A': 'text-emerald-400',
      'B': 'text-green-500',
      'C': 'text-yellow-500',
      'D': 'text-orange-500',
      'E': 'text-red-400',
      'F': 'text-red-500',
      'G': 'text-red-600',
    }
    return colors[klasse] || 'text-neutral-500'
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 flex items-center gap-2">
          <Zap className="w-6 h-6 text-accent" />
          Energieberechnung
        </h1>
        <p className="mt-1 text-neutral-500">
          HWB/HEB/PEB nach ÖNORM EN 832 / OIB-RL 6:2023
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Parameter */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title flex items-center gap-2">
              <Building2 className="w-5 h-5" />
              Gebäudeparameter
            </h2>
          </div>
          <div className="card-content space-y-4">
            <div>
              <label className="label">Bruttogeschossfläche (m²)</label>
              <input
                type="number"
                value={params.flaeche}
                onChange={(e) => setParams({ ...params, flaeche: Number(e.target.value) })}
                className="input"
                min="10"
                max="10000"
              />
            </div>
            <div>
              <label className="label">U-Wert (W/m²K)</label>
              <input
                type="number"
                value={params.uWert}
                onChange={(e) => setParams({ ...params, uWert: Number(e.target.value) })}
                className="input"
                step="0.01"
                min="0.05"
                max="2"
              />
            </div>
            <div>
              <label className="label">Klimazone</label>
              <select
                value={params.klimazone}
                onChange={(e) => setParams({ ...params, klimazone: Number(e.target.value) })}
                className="input"
              >
                {klimazonen.map((k) => (
                  <option key={k.value} value={k.value}>
                    {k.label} ({k.tage} Heizgradtage)
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Luftwechsel (1/h)</label>
              <input
                type="number"
                value={params.luftwechsel}
                onChange={(e) => setParams({ ...params, luftwechsel: Number(e.target.value) })}
                className="input"
                step="0.1"
                min="0.1"
                max="2"
              />
            </div>
            <div>
              <label className="label">Interne Wärmequellen (W/m²)</label>
              <input
                type="number"
                value={params.innereWaerme}
                onChange={(e) => setParams({ ...params, innereWaerme: Number(e.target.value) })}
                className="input"
                step="0.1"
                min="0"
                max="5"
              />
            </div>
            <button onClick={handleCalculate} className="btn btn-accent w-full mt-4">
              <Zap className="w-4 h-4" />
              Berechnen
            </button>
          </div>
        </div>

        {/* Results */}
        <div className="space-y-4">
          {result ? (
            <>
              <div className="card">
                <div className="card-header">
                  <h2 className="card-title">Ergebnisse</h2>
                </div>
                <div className="card-content space-y-4">
                  <div className="flex items-center justify-between p-4 rounded-lg bg-neutral-50">
                    <div className="flex items-center gap-3">
                      <Thermometer className="w-5 h-5 text-danger" />
                      <span className="font-medium">HWB</span>
                    </div>
                    <span className="text-2xl font-bold">{result.hwb}</span>
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-lg bg-neutral-50">
                    <div className="flex items-center gap-3">
                      <Sun className="w-5 h-5 text-warning-400" />
                      <span className="font-medium">HEB</span>
                    </div>
                    <span className="text-2xl font-bold">{result.heb}</span>
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-lg bg-neutral-50">
                    <div className="flex items-center gap-3">
                      <Wind className="w-5 h-5 text-primary" />
                      <span className="font-medium">PEB</span>
                    </div>
                    <span className="text-2xl font-bold">{result.peb}</span>
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-lg bg-neutral-50">
                    <div className="flex items-center gap-3">
                      <Droplets className="w-5 h-5 text-success-500" />
                      <span className="font-medium">CO₂</span>
                    </div>
                    <span className="text-2xl font-bold">{result.co2} kg/m²a</span>
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="card-content">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-neutral-500">Energieklasse</p>
                      <p className={`text-4xl font-bold ${getKlasseFarbe(result.klasse)}`}>
                        {result.klasse}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-neutral-500">OIB-RL 6</p>
                      <span className={`badge ${result.konform ? 'badge-success' : 'badge-danger'}`}>
                        {result.konform ? '✅ Konform' : '❌ Nicht konform'}
                      </span>
                    </div>
                  </div>
                  <div className="mt-4">
                    <p className="text-xs text-neutral-400">
                      Einheit: kWh/m²a
                    </p>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="card text-center p-12">
              <Zap className="w-12 h-12 text-neutral-300 mx-auto mb-4" />
              <h3 className="font-medium text-neutral-900">Noch keine Berechnung</h3>
              <p className="text-sm text-neutral-500 mt-1">
                Geben Sie die Gebäudeparameter ein und starten Sie die Berechnung
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}