import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Spinner, ErrorText } from '../components/Common'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const DIMS = ['itching', 'redness', 'dryness', 'pain', 'swelling', 'irritation', 'burning', 'scaling']

function scaleInput(label, value, set) {
  return (
    <div className="form-group" key={label}>
      <label>{label}: {value}/5</label>
      <input type="range" min="0" max="5" value={value} onChange={(e) => set(Number(e.target.value))} />
    </div>
  )
}

export function SymptomsPage() {
  const [list, setList] = useState([])
  const [trends, setTrends] = useState(null)
  const [vals, setVals] = useState({ itching: 0, redness: 0, dryness: 0, pain: 0, swelling: 0, irritation: 0, burning: 0, scaling: 0, lesion_count: 0, notes: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  const load = () => {
    Promise.all([api.listSymptoms(), api.symptomTrends(30)])
      .then(([s, t]) => { setList(s); setTrends(t) })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }
  useEffect(load, [])

  const submit = async (e) => {
    e.preventDefault()
    setSubmitting(true); setError('')
    try {
      await api.addSymptom(vals)
      setVals({ itching: 0, redness: 0, dryness: 0, pain: 0, swelling: 0, irritation: 0, burning: 0, scaling: 0, lesion_count: 0, notes: '' })
      load()
    } catch (err) { setError(err.message) }
    finally { setSubmitting(false) }
  }

  if (loading) return <Spinner />

  const set = (k) => (v) => setVals({ ...vals, [k]: v })

  return (
    <div>
      <div className="page-title">Symptom Tracking</div>
      <div className="page-subtitle">Log how your skin feels today (0 = none, 5 = severe)</div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-title">Log new entry</div>
          <form onSubmit={submit}>
            <div className="grid grid-2">
              {DIMS.map((d) => scaleInput(d.charAt(0).toUpperCase() + d.slice(1), vals[d], set(d)))}
            </div>
            <div className="form-group">
              <label>Lesion count: {vals.lesion_count}</label>
              <input type="range" min="0" max="50" value={vals.lesion_count} onChange={(e) => set('lesion_count')(Number(e.target.value))} />
            </div>
            <div className="form-group">
              <label>Notes (optional)</label>
              <textarea rows={2} value={vals.notes} onChange={(e) => set('notes')(e.target.value)} />
            </div>
            <ErrorText>{error}</ErrorText>
            <button className="btn" disabled={submitting}>{submitting ? 'Saving…' : 'Save entry'}</button>
          </form>
        </div>

        <div className="card">
          <div className="card-title">30-day trend</div>
          {trends && trends.points && trends.points.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={trends.points}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 5]} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="avg_score" stroke="#4f7cff" strokeWidth={2} dot={{ r: 3 }} name="Avg score" />
              </LineChart>
            </ResponsiveContainer>
          ) : <p className="muted small">Not enough data yet. Log a few entries over several days to see your trend.</p>}
          {trends && (
            <p className="small mt-16">
              Direction: <strong style={{ textTransform: 'capitalize' }}>{trends.direction}</strong>
              {trends.current_avg !== null && <> · Current avg: {trends.current_avg}</>}
            </p>
          )}
        </div>
      </div>

      <div className="card mt-16">
        <div className="card-title">History</div>
        {list.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead><tr><th>Date</th>{DIMS.map((d) => <th key={d}>{d.slice(0, 4)}</th>)}<th>Lesions</th><th></th></tr></thead>
              <tbody>
                {list.map((s) => (
                  <tr key={s.id}>
                    <td className="small">{new Date(s.recorded_at).toLocaleString()}</td>
                    {DIMS.map((d) => <td key={d}>{s[d]}</td>)}
                    <td>{s.lesion_count}</td>
                    <td><button className="btn btn-secondary btn-sm" onClick={() => { api.deleteSymptom(s.id).then(load) }}>Delete</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <p className="muted small">No entries yet.</p>}
      </div>
    </div>
  )
}
