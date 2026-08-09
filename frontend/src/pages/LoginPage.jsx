import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { DisclaimerBanner, ErrorText } from '../components/Common'

export function LoginPage() {
  const { login, register } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (mode === 'login') {
        await login(email, password)
      } else {
        await register(email, fullName, password)
      }
      navigate('/')
    } catch (err) {
      setError(err.message || 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrap">
      <div className="card auth-card">
        <div className="auth-title">🩺 SkinCare AI</div>
        <div className="auth-subtitle">AI-assisted skin-health monitoring &amp; tracking</div>
        <DisclaimerBanner />
        <form onSubmit={submit}>
          {mode === 'register' && (
            <div className="form-group">
              <label>Full name</label>
              <input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
            </div>
          )}
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
          </div>
          <ErrorText>{error}</ErrorText>
          <button className="btn btn-block" disabled={loading}>
            {loading ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Create account'}
          </button>
        </form>
        <div className="auth-switch">
          {mode === 'login' ? (
            <>New here? <a href="#" onClick={(e) => { e.preventDefault(); setMode('register') }}>Create an account</a></>
          ) : (
            <>Already have an account? <a href="#" onClick={(e) => { e.preventDefault(); setMode('login') }}>Log in</a></>
          )}
        </div>
      </div>
    </div>
  )
}
