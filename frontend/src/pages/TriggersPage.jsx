import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Spinner, ErrorText } from '../components/Common'

const CATS = ['lifestyle', 'food', 'environmental', 'cosmetic', 'medication', 'other']

export function TriggersPage() {
  const [list, setList] = useState([])
  const [analysis, setAnalysis] = useState(null)
  const [form, setForm] = useState({ category: 'lifestyle', name: '', intensity: 3 })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  const load = () => {
    Promise.all([api.listTriggers(), api.triggerAnalysis(30)])
      .then(([t, a]) => { setList(t); setAnalysis(a) })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }
  useEffect(load, [])

  const submit = async (e) => {
    e.preventDefault()
    setSubmitting(true); setError('')
    try { await api.addTrigger(form); setForm({ category: 'lifestyle', name: '', intensity: 3 }); load() }
    catch (err) { setError(err.message) }
    finally { setSubmitting(false) }
  }

  if (loading) return <Spinner />

  return (
    <div>
      <div className="page-title">Trigger Analysis</div>
      <div className="page-subtitle">Track possible triggers and see associations with symptom flares</div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-title">Log a trigger</div>
          <form onSubmit={submit}>
            <div className="form-group">
              <label>Category</label>
              <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                {CATS.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Name</label>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. stress, dairy, heat" required />
            </div>
            <div className="form-group">
              <label>Intensity: {form.intensity}/5</label>
              <input type="range" min="0" max="5" value={form.intensity} onChange={(e) => setForm({ ...form, intensity: Number(e.target.value) })} />
            </div>
            <ErrorText>{error}</ErrorText>
            <button className="btn" disabled={submitting}>{submitting ? 'Saving…' : 'Save trigger'}</button>
          </form>
        </div>

        <div className="card">
          <div className="card-title">Associations (last 30 days)</div>
          {analysis && analysis.associations && analysis.associations.length > 0 ? (
            <>
              {analysis.associations.map((a, i) => (
                <div key={i} className="small mb-16">
                  <strong>{a.trigger_name}</strong> ({a.category}) —
                  avg score after: {a.avg_score_after_trigger?.toFixed(2)} vs
                  baseline {a.avg_score_baseline?.toFixed(2)}
                  {' '}<span className={`badge ${a.lift > 0 ? 'badge-yellow' : 'badge-gray'}`}>
                    lift {a.lift > 0 ? '+' : ''}{a.lift?.toFixed(2)}
                  </span>
                </div>
              ))}
              <p className="muted small mt-16">{analysis.note}</p>
            </>
          ) : <p className="muted small">Not enough data. Log triggers and symptoms on different days to detect associations.</p>}
        </div>
      </div>

      <div className="card mt-16">
        <div className="card-title">Trigger history</div>
        {list.length > 0 ? (
          <table>
            <thead><tr><th>Date</th><th>Category</th><th>Name</th><th>Intensity</th><th></th></tr></thead>
            <tbody>
              {list.map((t) => (
                <tr key={t.id}>
                  <td className="small">{new Date(t.recorded_at).toLocaleString()}</td>
                  <td>{t.category}</td>
                  <td>{t.name}</td>
                  <td>{t.intensity}/5</td>
                  <td><button className="btn btn-secondary btn-sm" onClick={() => { api.deleteTrigger(t.id).then(load) }}>Delete</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : <p className="muted small">No triggers logged.</p>}
      </div>
    </div>
  )
}
