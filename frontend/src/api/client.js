const BASE = '/api'

function token() {
  return localStorage.getItem('skincare_token')
}

async function request(path, opts = {}) {
  const headers = { ...(opts.headers || {}) }
  if (!(opts.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }
  const tok = token()
  if (tok) headers['Authorization'] = `Bearer ${tok}`
  const res = await fetch(`${BASE}${path}`, { ...opts, headers })
  if (res.status === 401) {
    localStorage.removeItem('skincare_token')
    localStorage.removeItem('skincare_user')
    if (!window.location.pathname.startsWith('/login')) {
      window.location.href = '/login'
    }
  }
  if (!res.ok) {
    let detail = 'Request failed'
    try { const j = await res.json(); detail = j.detail || j.message || detail } catch {}
    const err = new Error(detail)
    err.status = res.status
    throw err
  }
  if (res.headers.get('content-type')?.includes('application/json')) {
    return res.json()
  }
  return res
}

export const api = {
  // auth
  register: (email, fullName, password) =>
    request('/auth/register', { method: 'POST', body: JSON.stringify({ email, full_name: fullName, password }) }),
  login: (email, password) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),

  // profile
  getProfile: () => request('/profile'),
  updateProfile: (data) => request('/profile', { method: 'PUT', body: JSON.stringify(data) }),
  exportData: () => request('/profile/export'),

  // symptoms
  listSymptoms: () => request('/symptoms'),
  addSymptom: (data) => request('/symptoms', { method: 'POST', body: JSON.stringify(data) }),
  deleteSymptom: (id) => request(`/symptoms/${id}`, { method: 'DELETE' }),
  symptomTrends: (window = 30) => request(`/symptoms/trends?window=${window}`),

  // triggers
  listTriggers: () => request('/triggers'),
  addTrigger: (data) => request('/triggers', { method: 'POST', body: JSON.stringify(data) }),
  deleteTrigger: (id) => request(`/triggers/${id}`, { method: 'DELETE' }),
  triggerAnalysis: (window = 30) => request(`/triggers/analysis?window=${window}`),

  // treatments
  listTreatments: () => request('/treatments'),
  addTreatment: (data) => request('/treatments', { method: 'POST', body: JSON.stringify(data) }),
  deleteTreatment: (id) => request(`/treatments/${id}`, { method: 'DELETE' }),
  logTreatment: (id, status) => request(`/treatments/${id}/logs`, { method: 'POST', body: JSON.stringify({ status }) }),

  // images
  uploadImage: (file, bodyLocation) => {
    const fd = new FormData()
    fd.append('file', file)
    if (bodyLocation) fd.append('body_location', bodyLocation)
    return request('/images/upload', { method: 'POST', body: fd })
  },
  listImages: () => request('/images'),
  imageUrl: (id) => `${BASE}/images/${id}/file`,

  // ai
  analyzeImage: (id) => request(`/ai/analyze/${id}`, { method: 'POST' }),
  aiHistory: () => request('/ai/history'),

  // reports
  generateReport: (data) => request('/reports/generate', { method: 'POST', body: JSON.stringify(data) }),
  listReports: () => request('/reports'),
  reportDownloadUrl: (id) => `${BASE}/reports/${id}/download`,

  // dashboard
  dashboard: () => request('/dashboard'),
}
