import { useEffect, useRef, useState } from 'react'
import { api } from '../api/client'
import { DisclaimerBanner, Spinner, ErrorText } from '../components/Common'

export function ImagesPage() {
  const [images, setImages] = useState([])
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [uploadMsg, setUploadMsg] = useState('')
  const [loading, setLoading] = useState(true)
  const fileRef = useRef(null)
  const [preview, setPreview] = useState(null)
  const [bodyLocation, setBodyLocation] = useState('')

  const load = () => {
    api.listImages().then(setImages).catch((e) => setError(e.message)).finally(() => setLoading(false))
  }
  useEffect(load, [])

  const onFile = (e) => {
    const f = e.target.files[0]
    if (f) {
      setPreview(f)
      setResult(null); setUploadMsg('')
    }
  }

  const upload = async () => {
    if (!preview) return
    setUploading(true); setError(''); setUploadMsg('')
    try {
      const res = await api.uploadImage(preview, bodyLocation)
      setUploadMsg(res.message)
      if (res.quality_ok) {
        setPreview(null); setBodyLocation(''); if (fileRef.current) fileRef.current.value = ''
        load()
        // auto-analyze
        setAnalyzing(res.image_id)
        const ai = await api.analyzeImage(res.image_id)
        setResult(ai)
        setAnalyzing(null)
        load()
      }
    } catch (err) { setError(err.message) }
    finally { setUploading(false) }
  }

  const analyze = async (id) => {
    setAnalyzing(id); setError(''); setResult(null)
    try {
      const ai = await api.analyzeImage(id)
      setResult(ai)
    } catch (err) { setError(err.message) }
    finally { setAnalyzing(null) }
  }

  if (loading) return <Spinner />

  return (
    <div>
      <div className="page-title">AI Image Screening</div>
      <div className="page-subtitle">Upload a skin image for AI-assisted screening (demo model)</div>
      <DisclaimerBanner />

      <div className="grid grid-2">
        <div className="card">
          <div className="card-title">Upload an image</div>
          <div className="upload-area" onClick={() => fileRef.current?.click()}>
            <input type="file" ref={fileRef} accept="image/jpeg,image/png" onChange={onFile} style={{ display: 'none' }} />
            {preview ? (
              <>
                <div className="has-file">✓ {preview.name}</div>
                <img className="preview-img" src={URL.createObjectURL(preview)} alt="preview" />
              </>
            ) : (
              <div>
                <div style={{ fontSize: 32 }}>📷</div>
                <p className="muted small">Click to select a JPG or PNG image (max 10MB)</p>
              </div>
            )}
          </div>
          <div className="form-group mt-16">
            <label>Body location (optional)</label>
            <input value={bodyLocation} onChange={(e) => setBodyLocation(e.target.value)} placeholder="e.g. left forearm" />
          </div>
          {uploadMsg && <div className="alert alert-info small">{uploadMsg}</div>}
          <ErrorText>{error}</ErrorText>
          <button className="btn" disabled={!preview || uploading} onClick={upload}>
            {uploading ? 'Uploading…' : 'Upload & analyze'}
          </button>
        </div>

        <div className="card">
          <div className="card-title">AI result</div>
          {analyzing ? (
            <div className="text-center"><Spinner /><p className="small muted">Analyzing image…</p></div>
          ) : result ? (
            <ResultDisplay result={result} />
          ) : (
            <p className="muted small">Upload an image to see the AI screening result here, or click "Analyze" on a past image below.</p>
          )}
        </div>
      </div>

      <div className="card mt-16">
        <div className="card-title">Image history</div>
        {images.length > 0 ? (
          <div className="grid grid-3">
            {images.map((img) => (
              <div key={img.id} className="card" style={{ boxShadow: 'none', border: '1px solid var(--border)' }}>
                <img src={api.imageUrl(img.id)} alt="skin" style={{ width: '100%', borderRadius: 8 }} />
                <p className="small muted">{new Date(img.created_at).toLocaleString()}</p>
                <p className="small">{img.body_location || 'No location'}</p>
                <p className="small">Quality: {img.quality_score} {img.quality_ok ? <span className="badge badge-green">OK</span> : <span className="badge badge-red">Low</span>}</p>
                <button className="btn btn-secondary btn-sm btn-block mt-16" disabled={!img.quality_ok || analyzing} onClick={() => analyze(img.id)}>
                  {analyzing === img.id ? 'Analyzing…' : 'Analyze'}
                </button>
              </div>
            ))}
          </div>
        ) : <p className="muted small">No images uploaded yet.</p>}
      </div>
    </div>
  )
}

function ResultDisplay({ result }) {
  const p = result.prediction
  return (
    <div>
      {p.is_demo && <div className="alert alert-warning small">Demo/prototype model — results are illustrative only, not a diagnosis.</div>}
      {!p.reliable ? (
        <div className="alert alert-danger">
          <strong>AI uncertainty: confidence too low.</strong>
          <p className="small mt-16">The model's confidence ({(p.confidence * 100).toFixed(0)}%) is below the reliability threshold.
          No specific category is being reported. {result.message}</p>
        </div>
      ) : (
        <div className="alert alert-info">
          <div className="row">
            <span className="badge badge-blue">{p.category}</span>
            <span className="small">Confidence: {(p.confidence * 100).toFixed(0)}%</span>
            {p.severity && <span className={`badge ${p.severity_score > 0.6 ? 'badge-yellow' : 'badge-green'}`}>Severity: {p.severity}</span>}
          </div>
        </div>
      )}

      {result.consultation_recommended && (
        <div className="alert alert-warning small">
          <strong>Consider consulting a healthcare professional.</strong> The AI screening result and/or confidence suggest a consultation may be beneficial.
        </div>
      )}

      <p className="small muted mt-16">{p.attention_note}</p>

      {p.probabilities && Object.keys(p.probabilities).length > 0 && (
        <div className="mt-16">
          <div className="small" style={{ fontWeight: 600 }}>Score distribution</div>
          {Object.entries(p.probabilities).map(([k, v]) => (
            <div key={k} className="small" style={{ display: 'flex', alignItems: 'center', gap: 8, margin: '4px 0' }}>
              <span style={{ width: 120 }}>{k}</span>
              <div style={{ flex: 1, background: '#f1f5f9', borderRadius: 4, height: 8 }}>
                <div style={{ width: `${v * 100}%`, background: 'var(--blue)', height: 8, borderRadius: 4 }} />
              </div>
              <span className="muted">{(v * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>
      )}

      <div className="alert alert-danger small mt-16">
        <strong>Disclaimer:</strong> {p.disclaimer}
      </div>
    </div>
  )
}
