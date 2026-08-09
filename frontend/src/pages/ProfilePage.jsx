import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Spinner, ErrorText } from '../components/Common'

export function ProfilePage() {
  const [profile, setProfile] = useState(null)
  const [exportData, setExportData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.getProfile().then(setProfile).catch((e) => setError(e.message)).finally(() => setLoading(false))
  }, [])

  const save = async (e) => {
    e.preventDefault(); setSaving(true); setError(''); setSaved(false)
    try {
      const { id, user_id, updated_at, ...rest } = profile
      await api.updateProfile(rest)
      setSaved(true)
    } catch (err) { setError(err.message) }
    finally { setSaving(false) }
  }

  const doExport = async () => {
    try {
      const data = await api.exportData()
      setExportData(data)
    } catch (err) { setError(err.message) }
  }

  if (loading) return <Spinner />

  const set = (k) => (v) => setProfile({ ...profile, [k]: v })

  return (
    <div>
      <div className="page-title">Profile</div>
      <div className="page-subtitle">Your information helps personalize your monitoring</div>

      <div className="card">
        <div className="card-title">Patient profile</div>
        <form onSubmit={save}>
          <div className="grid grid-2">
            <div className="form-group">
              <label>Age</label>
              <input type="number" value={profile.age ?? ''} onChange={(e) => set('age')(e.target.value ? Number(e.target.value) : null)} />
            </div>
            <div className="form-group">
              <label>Gender</label>
              <select value={profile.gender ?? ''} onChange={(e) => set('gender')(e.target.value || null)}>
                <option value="">—</option>
                <option>female</option><option>male</option><option>other</option><option>prefer not to say</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Known condition</label>
            <input value={profile.known_condition ?? ''} onChange={(e) => set('known_condition')(e.target.value || null)} />
          </div>
          <div className="form-group">
            <label>Allergies</label>
            <input value={profile.allergies ?? ''} onChange={(e) => set('allergies')(e.target.value || null)} />
          </div>
          <div className="form-group">
            <label>Current treatments</label>
            <input value={profile.current_treatments ?? ''} onChange={(e) => set('current_treatments')(e.target.value || null)} />
          </div>
          <div className="form-group">
            <label>Notes</label>
            <textarea rows={3} value={profile.notes ?? ''} onChange={(e) => set('notes')(e.target.value || null)} />
          </div>
          {saved && <div className="alert alert-success small">Profile saved.</div>}
          <ErrorText>{error}</ErrorText>
          <button className="btn" disabled={saving}>{saving ? 'Saving…' : 'Save profile'}</button>
        </form>
      </div>

      <div className="card mt-16">
        <div className="card-title">Privacy &amp; data export</div>
        <p className="small muted mb-16">Your data is stored privately and only accessible by you. Export a full copy at any time.</p>
        <button className="btn btn-secondary" onClick={doExport}>Export my data (JSON)</button>
        {exportData && (
          <div className="mt-16">
            <p className="small">Exported at: {new Date(exportData.exported_at).toLocaleString()}</p>
            <p className="small">Symptoms: {exportData.symptoms?.length} · Triggers: {exportData.triggers?.length} · Images: {exportData.images?.length} · AI predictions: {exportData.ai_predictions?.length}</p>
            <details>
              <summary className="small">View raw JSON</summary>
              <pre style={{ maxHeight: 300, overflow: 'auto', fontSize: 11, background: '#f8fafc', padding: 12, borderRadius: 8 }}>
                {JSON.stringify(exportData, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </div>
    </div>
  )
}
