import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Spinner, ErrorText } from '../components/Common'

export function TreatmentsPage() {
  const [list, setList] = useState([])
  const [form, setForm] = useState({ name: '', schedule: '', notes: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    api.listTreatments().then(setList).catch((e) => setError(e.message)).finally(() => setLoading(false))
  }
  useEffect(load, [])

  const submit = async (e) => {
    e.preventDefault(); setError('')
    try { await api.addTreatment(form); setForm({ name: '', schedule: '', notes: '' }); load() }
    catch (err) { setError(err.message) }
  }

  if (loading) return <Spinner />

  return (
    <div>
      <div className="page-title">Treatment Adherence</div>
      <div className="page-subtitle">Track your treatments and mark them as completed</div>

      <div className="alert alert-info">
        The system only tracks adherence and reminds. It does not prescribe or adjust treatments.
        Always follow your healthcare provider's instructions.
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-title">Add a treatment</div>
          <form onSubmit={submit}>
            <div className="form-group">
              <label>Name</label>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Moisturizer" required />
            </div>
            <div className="form-group">
              <label>Schedule</label>
              <input value={form.schedule} onChange={(e) => setForm({ ...form, schedule: e.target.value })} placeholder="e.g. Twice daily" required />
            </div>
            <div className="form-group">
              <label>Notes</label>
              <textarea rows={2} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
            </div>
            <ErrorText>{error}</ErrorText>
            <button className="btn">Add</button>
          </form>
        </div>

        <div className="card">
          <div className="card-title">Your treatments</div>
          {list.length > 0 ? (
            <div className="grid">
              {list.map((t) => (
                <div key={t.id} className="card" style={{ boxShadow: 'none', border: '1px solid var(--border)' }}>
                  <div className="row">
                    <strong>{t.name}</strong>
                    {t.active ? <span className="badge badge-green">Active</span> : <span className="badge badge-gray">Inactive</span>}
                  </div>
                  <p className="small muted">{t.schedule}</p>
                  <p className="small">Adherence: <strong>{t.adherence_pct}%</strong> ({t.completed_count} done / {t.skipped_count} missed)</p>
                  <div className="row mt-16">
                    <button className="btn btn-secondary btn-sm" onClick={() => api.logTreatment(t.id, 'completed').then(load)}>✓ Done</button>
                    <button className="btn btn-secondary btn-sm" onClick={() => api.logTreatment(t.id, 'skipped').then(load)}>✗ Missed</button>
                    <div className="spacer" />
                    <button className="btn btn-danger btn-sm" onClick={() => { if (confirm('Delete this treatment?')) api.deleteTreatment(t.id).then(load) }}>Delete</button>
                  </div>
                </div>
              ))}
            </div>
          ) : <p className="muted small">No treatments yet.</p>}
        </div>
      </div>
    </div>
  )
}
