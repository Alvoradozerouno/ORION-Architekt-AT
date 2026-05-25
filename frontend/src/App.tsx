import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AppLayout } from '@components/layout/AppLayout'
import { HomePage } from '@components/pages/HomePage'
import { DashboardPage } from '@components/pages/DashboardPage'
import { CompliancePage } from '@components/pages/CompliancePage'
import { EnergyPage } from '@components/pages/EnergyPage'
import { StructuralPage } from '@components/pages/StructuralPage'
import { DocumentationPage } from '@components/pages/DocumentationPage'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<HomePage />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="compliance" element={<CompliancePage />} />
          <Route path="energy" element={<EnergyPage />} />
          <Route path="structural" element={<StructuralPage />} />
          <Route path="documentation" element={<DocumentationPage />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App