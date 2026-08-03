import { useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import InterestsEditor from '../components/InterestsEditor.jsx'
import SummaryPanel from '../components/SummaryPanel.jsx'

export default function Dashboard() {
  const { logout } = useAuth()
  const [interests, setInterests] = useState([])

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <h1>AI News Assistant</h1>
        <button type="button" onClick={logout}>
          Sign out
        </button>
      </header>

      <InterestsEditor interests={interests} setInterests={setInterests} />
      <SummaryPanel />
    </div>
  )
}
