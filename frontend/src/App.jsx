import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { Navbar } from './components/Navbar'
import { LoginPage } from './pages/LoginPage'
import { DashboardPage } from './pages/DashboardPage'
import { SymptomsPage } from './pages/SymptomsPage'
import { TriggersPage } from './pages/TriggersPage'
import { ImagesPage } from './pages/ImagesPage'
import { TreatmentsPage } from './pages/TreatmentsPage'
import { ReportsPage } from './pages/ReportsPage'
import { ProfilePage } from './pages/ProfilePage'

function Protected({ children }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  return (
    <div className="app-shell">
      <Navbar />
      <main className="app-main">{children}</main>
      <footer className="small muted text-center" style={{ padding: 20 }}>
        SkinCare AI · Screening/monitoring tool only — not a medical device · Not a diagnosis
      </footer>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Protected><DashboardPage /></Protected>} />
      <Route path="/symptoms" element={<Protected><SymptomsPage /></Protected>} />
      <Route path="/triggers" element={<Protected><TriggersPage /></Protected>} />
      <Route path="/images" element={<Protected><ImagesPage /></Protected>} />
      <Route path="/treatments" element={<Protected><TreatmentsPage /></Protected>} />
      <Route path="/reports" element={<Protected><ReportsPage /></Protected>} />
      <Route path="/profile" element={<Protected><ProfilePage /></Protected>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
