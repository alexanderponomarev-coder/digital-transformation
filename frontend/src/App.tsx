import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { PlatformProvider } from './context/PlatformContext'
import { WorkspaceShell } from './components/WorkspaceShell'
import { LandingPage } from './pages/LandingPage'
import { OverviewPage } from './pages/OverviewPage'
import { DocumentsPage } from './pages/DocumentsPage'
import { CoveragePage } from './pages/CoveragePage'
import { MethodologyPage } from './pages/MethodologyPage'
import { QuestionsPage } from './pages/QuestionsPage'
import { ModelPage } from './pages/ModelPage'
import { RoadmapPage } from './pages/RoadmapPage'
import { RegulatoryPage } from './pages/RegulatoryPage'
import { MaturityPage } from './pages/MaturityPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route
          path="/app"
          element={
            <PlatformProvider>
              <WorkspaceShell />
            </PlatformProvider>
          }
        >
          <Route index element={<OverviewPage />} />
          <Route path="documents" element={<DocumentsPage />} />
          <Route path="coverage" element={<CoveragePage />} />
          <Route path="methodology" element={<MethodologyPage />} />
          <Route path="maturity" element={<MaturityPage />} />
          <Route path="questions" element={<QuestionsPage />} />
          <Route path="model" element={<ModelPage />} />
          <Route path="roadmap" element={<RoadmapPage />} />
          <Route path="regulatory" element={<RegulatoryPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
