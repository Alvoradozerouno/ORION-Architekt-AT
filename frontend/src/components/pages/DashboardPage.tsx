import { useState } from 'react'
import { Upload, FileUp, FileText, CheckCircle, XCircle, AlertCircle } from 'lucide-react'

const bundeslaender = [
  { value: 'wien', label: 'Wien' },
  { value: 'niederoesterreich', label: 'Niederösterreich' },
  { value: 'oberoesterreich', label: 'Oberösterreich' },
  { value: 'salzburg', label: 'Salzburg' },
  { value: 'tirol', label: 'Tirol' },
  { value: 'vorarlberg', label: 'Vorarlberg' },
  { value: 'steiermark', label: 'Steiermark' },
  { value: 'kaernten', label: 'Kärnten' },
  { value: 'burgenland', label: 'Burgenland' },
]

const buildingTypes = [
  { value: 'wohngebaeude', label: 'Wohngebäude' },
  { value: 'buerogebaeude', label: 'Bürogebäude' },
  { value: 'industrie', label: 'Industrie' },
  { value: 'handel', label: 'Einzelhandel' },
  { value: 'schule', label: 'Schule' },
]

interface ComplianceResult {
  id: string
  name: string
  status: 'pass' | 'fail' | 'warning' | 'info'
  message: string
  standard: string
}

export function DashboardPage() {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [bundesland, setBundesland] = useState('wien')
  const [buildingType, setBuildingType] = useState('wohngebaeude')
  const [analyzing, setAnalyzing] = useState(false)
  const [results, setResults] = useState<ComplianceResult[] | null>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0])
    }
  }

  const handleAnalyze = async () => {
    if (!selectedFile) return
    setAnalyzing(true)
    // Simulate analysis
    await new Promise(resolve => setTimeout(resolve, 2000))
    setResults([
      { id: '1', name: 'OIB-RL 2 Brandschutz', status: 'pass', message: 'Alle Anforderungen erfüllt', standard: 'OIB-RL 2:2023' },
      { id: '2', name: 'OIB-RL 3 Hygiene', status: 'pass', message: 'Lüftungsanforderungen erfüllt', standard: 'OIB-RL 3:2023' },
      { id: '3', name: 'OIB-RL 4 Nutzungssicherheit', status: 'warning', message: 'Barrierefreiheit prüfen', standard: 'OIB-RL 4:2023' },
      { id: '4', name: 'OIB-RL 5 Schallschutz', status: 'pass', message: 'Schallschutz nachgewiesen', standard: 'OIB-RL 5:2023' },
      { id: '5', name: 'OIB-RL 6 Energieeinsparung', status: 'pass', message: 'HWB: 45 kWh/m²a (Klasse A)', standard: 'OIB-RL 6:2023' },
      { id: '6', name: 'OIB-RL 7 Nachhaltigkeit', status: 'info', message: 'Grundlagendokumentation erforderlich', standard: 'OIB-RL 7:2023' },
    ])
    setAnalyzing(false)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass': return <CheckCircle className="w-5 h-5 text-success-500" />
      case 'fail': return <XCircle className="w-5 h-5 text-destructive" />
      case 'warning': return <AlertCircle className="w-5 h-5 text-warning-400" />
      default: return <AlertCircle className="w-5 h-5 text-neutral-400" />
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900">Dashboard</h1>
        <p className="mt-1 text-neutral-500">Laden Sie Ihre Pläne hoch und erhalten Sie sofort eine Compliance-Analyse</p>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Upload Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* File Upload */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title flex items-center gap-2">
                <FileUp className="w-5 h-5" />
                Datei hochladen
              </h2>
              <p className="card-description">IFC oder PDF Dateien werden automatisch analysiert</p>
            </div>
            <div className="card-content">
              <div
                className={`relative rounded-lg border-2 border-dashed p-8 text-center ${
                  dragActive ? 'border-accent bg-accent/5' : 'border-neutral-300'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  accept=".ifc,.pdf,.dwg"
                  onChange={(e) => e.target.files && setSelectedFile(e.target.files[0])}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <div className="flex flex-col items-center">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary-100 text-primary-700 mb-4">
                    <Upload className="w-8 h-8" />
                  </div>
                  <p className="text-lg font-medium text-neutral-900">
                    {selectedFile ? selectedFile.name : 'Datei hierher ziehen'}
                  </p>
                  <p className="mt-2 text-sm text-neutral-500">
                    Unterstützt: IFC, PDF, DWG (max. 500MB)
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Settings */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Einstellungen</h2>
            </div>
            <div className="card-content">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="label">Bundesland</label>
                  <select 
                    value={bundesland} 
                    onChange={(e) => setBundesland(e.target.value)}
                    className="input"
                  >
                    {bundeslaender.map((bl) => (
                      <option key={bl.value} value={bl.value}>{bl.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="label">Gebäudetyp</label>
                  <select 
                    value={buildingType} 
                    onChange={(e) => setBuildingType(e.target.value)}
                    className="input"
                  >
                    {buildingTypes.map((bt) => (
                      <option key={bt.value} value={bt.value}>{bt.label}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="mt-6">
                <button 
                  onClick={handleAnalyze}
                  disabled={!selectedFile || analyzing}
                  className="btn btn-primary w-full sm:w-auto"
                >
                  {analyzing ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Analysiere...
                    </>
                  ) : (
                    <>
                      <FileText className="w-4 h-4" />
                      Analyse starten
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Results Sidebar */}
        <div className="space-y-6">
          {results ? (
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Ergebnisse</h2>
                <div className="flex gap-2">
                  <span className="badge badge-success">
                    {results.filter(r => r.status === 'pass').length} erfüllt
                  </span>
                  {results.some(r => r.status === 'warning') && (
                    <span className="badge badge-warning">
                      {results.filter(r => r.status === 'warning').length} Warnungen
                    </span>
                  )}
                </div>
              </div>
              <div className="card-content space-y-3">
                {results.map((result) => (
                  <div key={result.id} className="flex gap-3 p-3 rounded-lg bg-neutral-50">
                    {getStatusIcon(result.status)}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-neutral-900">{result.name}</p>
                      <p className="text-xs text-neutral-500 mt-0.5">{result.message}</p>
                      <p className="text-xs text-primary-600 mt-1">{result.standard}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="card text-center p-8">
              <FileText className="w-12 h-12 text-neutral-300 mx-auto mb-4" />
              <h3 className="font-medium text-neutral-900">Noch keine Analyse</h3>
              <p className="text-sm text-neutral-500 mt-1">
                Laden Sie eine Datei hoch und starten Sie die Analyse
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}