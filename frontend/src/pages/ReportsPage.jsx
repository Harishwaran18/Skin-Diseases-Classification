import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Spinner, ErrorText } from '../components/Common'

export function ReportsPage() {
  const [list, setList] = useState([])
  const [includeImages, setIncludeImages] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    api.listReports().then(setList).catch((e) => setError(e.message)).finally(() => setLoading(false))
  }
  useEffect(load, [])

  const generate = async () => {
    setGenerating(true); setError('')
    try {
      await api.generateReport({ include_images: includeImages })
      load()
    } catch (err) { setError(err.message) }
    finally { setGenerating(false) }
  }

  if (loading) return <Spinner />

  return (
    <div>
      <div className="page-title">PDF Reports</div>
      <div className="page-subtitle">Generate a doctor-friendly summary of your monitoring data</div>

      <div className="card">
        <div className="card-title">Generate a report</div>
        <div className="form-group">
          <label>
            <input type="checkbox" checked={includeImages} onChange={(e) => setIncludeImages(e.target.checked)} style={{ width: 'auto', marginRight: 8 }} />
            Include images (with timestamps)
          </label>
        </div>
        <ErrorText>{error}</ErrorText>
        <button className="btn" disabled={generating} onClick={generate}>
          {generating ? 'Generating…' : 'Generate PDF report'}
        </button>
      </div>

      <div className="card mt-16">
        <div className="card-title">Your reports</div>
        {list.length > 0 ? (
          <table>
            <thead><tr><th>Created</th><th>Period</th><th></th></tr></thead>
            <tbody>
              {list.map((r) => (
                <tr key={r.id}>
                  <td className="small">{new Date(r.created_at).toLocaleString()}</td>
                  <td className="small">{new Date(r.date_from).toLocaleDateString()} — {new Date(r.date_to).toLocaleDateString()}</td>
                  <td><a className="btn btn-secondary btn-sm" href={api.reportDownloadUrl(r.id)} target="_blank" rel="noopener">Download PDF</a></td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : <p className="muted small">No reports generated yet.</p>}
      </div>
    </div>
  )
}
