import { BookOpen, FileText, Code, Terminal, Github } from 'lucide-react'

const docSections = [
  {
    id: 'getting-started',
    title: 'Erste Schritte',
    icon: <Terminal className="w-5 h-5" />,
    items: [
      { name: 'Installation', desc: 'Backend und Frontend einrichten', href: '#' },
      { name: 'Quick Start', desc: 'In 5 Minuten zum ersten Ergebnis', href: '#' },
      { name: 'Konfiguration', desc: 'Umgebungsvariablen und Einstellungen', href: '#' },
    ],
  },
  {
    id: 'api',
    title: 'API Dokumentation',
    icon: <Code className="w-5 h-5" />,
    items: [
      { name: 'REST API', desc: 'Alle Endpunkte und Parameter', href: '#' },
      { name: 'GraphQL', desc: 'GraphQL Schema und Queries', href: '#' },
      { name: 'Authentifizierung', desc: 'JWT und API Keys', href: '#' },
    ],
  },
  {
    id: 'normen',
    title: 'Normen & Richtlinien',
    icon: <FileText className="w-5 h-5" />,
    items: [
      { name: 'OIB-RL 1-7', desc: 'Alle OIB-Richtlinien erklärt', href: '#' },
      { name: 'Eurocodes', desc: 'EC2 bis EC8 Anwendung', href: '#' },
      { name: 'ÖNORM', desc: 'Österreichische Normen', href: '#' },
    ],
  },
  {
    id: 'contributing',
    title: 'Mitwirken',
    icon: <Github className="w-5 h-5" />,
    items: [
      { name: 'Contributing Guide', desc: 'So kannst du beitragen', href: '#' },
      { name: 'Code Standards', desc: 'Linting, Testing, Style', href: '#' },
      { name: 'Good First Issues', desc: 'Perfekt für den Einstieg', href: '#' },
    ],
  },
]

export function DocumentationPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-primary" />
          Dokumentation
        </h1>
        <p className="mt-1 text-neutral-500">
          Alles was du über Baumeister Tool Austria wissen musst
        </p>
      </div>

      {/* Quick Links */}
      <div className="grid gap-6 md:grid-cols-2">
        {docSections.map((section) => (
          <div key={section.id} className="card">
            <div className="card-header">
              <h2 className="card-title flex items-center gap-2">
                {section.icon}
                {section.title}
              </h2>
            </div>
            <div className="card-content space-y-3">
              {section.items.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="block p-3 rounded-lg hover:bg-neutral-50 transition-colors group"
                >
                  <p className="font-medium text-primary-600 group-hover:text-primary-700">{item.name}</p>
                  <p className="text-sm text-neutral-500">{item.desc}</p>
                </a>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Tech Stack */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Technologien</h2>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: 'Python', badge: '3.11+' },
              { name: 'FastAPI', badge: '0.123+' },
              { name: 'React', badge: '18.x' },
              { name: 'TypeScript', badge: '5.x' },
              { name: 'TailwindCSS', badge: '3.4' },
              { name: 'PostgreSQL', badge: '16' },
              { name: 'Docker', badge: '24.x' },
              { name: 'Kubernetes', badge: '1.28' },
            ].map((tech) => (
              <div key={tech.name} className="flex items-center justify-between p-3 rounded-lg bg-neutral-50">
                <span className="font-medium text-neutral-900">{tech.name}</span>
                <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded-full">{tech.badge}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}