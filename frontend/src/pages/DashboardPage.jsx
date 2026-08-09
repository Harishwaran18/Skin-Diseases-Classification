import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { DisclaimerBanner, Spinner, RiskBadge, ErrorText } from '../components/Common'

export function DashboardPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.dashboard().then(setData).catch((e) => setError(e.message))
  }, [])

  if (error) return <div className="alert alert-danger">{error}</div>
  if (!data) return <Spinner />

  const riskClass = `risk-box risk-${data.risk_level}`

  return (
    <div>
      <div className="page-title">Dashboard</div>
      <div className="page-subtitle">Your skin-health overview</div>
      <DisclaimerBanner />

      <div className="grid grid-4 mb-16">
        <div className="card stat">
          <span className="stat-label">Today's score</span>
          <span className="stat-value">{data.today_score !== null ? data.today_score : '—'}</span>
          <span className="muted small">out of 5</span>
        </div>
        <div className="card stat">
          <span className="stat-label">30-day trend</span>
          <span className="stat-value" style={{ textTransform: 'capitalize' }}>{data.severity_trend}</span>
        </div>
        <div className="card stat">
          <span className="stat-label">Adherence</span>
          <span className="stat-value">{data.adherence_pct}%</span>
        </div>
        <div className="card stat">
          <span className="stat-label">Entries (30d)</span>
          <span className="stat-value">{data.symptom_count_30d}</span>
        </div>
      </div>

      <div className="grid grid-2">
        <div className={`card ${riskClass}`}>
          <div className="row">
            <RiskBadge level={data.risk_level} />
            <span className="small muted">Risk level</span>
          </div>
          <p style={{ marginTop: 10 }}>{data.risk_message}</p>
        </div>

        <div className="card">
          <div className="card-title">Upcoming reminders</div>
          {data.upcoming_reminders && data.upcoming_reminders.length > 0 ? (
            <ul style={{ paddingLeft: 18 }}>
              {data.upcoming_reminders.map((r, i) => (
                <li key={i} className="small">{r.name} — {r.schedule}</li>
              ))}
            </ul>
          ) : <p className="muted small">No reminders scheduled.</p>}
        </div>
      </div>

      <div className="card mt-16">
        <div className="card-title">Recent triggers</div>
        {data.recent_triggers.length > 0 ? (
          <table>
            <thead><tr><th>Trigger</th><th>Category</th><th>Intensity</th><th>When</th></tr></thead>
            <tbody>
              {data.recent_triggers.map((t, i) => (
                <tr key={i}>
                  <td>{t.name}</td>
                  <td>{t.category}</td>
                  <td>{t.intensity}/5</td>
                  <td className="muted small">{new Date(t.recorded_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : <p className="muted small">No triggers recorded yet.</p>}
      </div>

      <div className="card mt-16">
        <div className="card-title">Latest AI screening</div>
        {data.last_prediction_category ? (
          <div className="row">
            <span className="badge badge-blue">{data.last_prediction_category}</span>
            <span className="small">Confidence: {(data.last_prediction_confidence * 100).toFixed(0)}%</span>
            <span className="small muted">(Demo model — not a diagnosis)</span>
          </div>
        ) : <p className="muted small">No AI screening performed yet. Visit <a href="/images">AI Screening</a> to analyze an image.</p>}
      </div>
    </div>
  )
}
