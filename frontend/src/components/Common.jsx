export function DisclaimerBanner() {
  return (
    <div className="disclaimer-banner">
      <span>⚠️</span>
      <div>
        <strong>Screening tool only — not a diagnosis.</strong> SkinCare AI does not diagnose
        skin conditions and cannot replace a qualified healthcare professional. If you are
        experiencing a medical emergency, seek care immediately.
      </div>
    </div>
  )
}

export function Spinner() {
  return (
    <div className="loading">
      <div className="spinner" />
    </div>
  )
}

export function ErrorText({ children }) {
  return children ? <div className="error-text">{children}</div> : null
}

export function RiskBadge({ level }) {
  const map = { green: 'badge-green', yellow: 'badge-yellow', red: 'badge-red' }
  const labels = { green: 'Low', yellow: 'Monitor', red: 'Attention' }
  return <span className={`badge ${map[level] || 'badge-gray'}`}>{labels[level] || level}</span>
}
