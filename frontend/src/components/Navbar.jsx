import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  if (!user) return null
  const links = [
    { to: '/', label: 'Dashboard' },
    { to: '/symptoms', label: 'Symptoms' },
    { to: '/triggers', label: 'Triggers' },
    { to: '/images', label: 'AI Screening' },
    { to: '/treatments', label: 'Treatments' },
    { to: '/reports', label: 'Reports' },
    { to: '/profile', label: 'Profile' },
  ]
  return (
    <nav className="navbar">
      <div className="navbar-brand">🩺 SkinCare AI</div>
      <div className="navbar-links">
        {links.map((l) => (
          <NavLink key={l.to} to={l.to} end={l.to === '/'}>
            {l.label}
          </NavLink>
        ))}
      </div>
      <div className="navbar-user">
        <span>{user.full_name}</span>
        <button className="btn btn-secondary btn-sm" onClick={() => { logout(); navigate('/login') }}>
          Logout
        </button>
      </div>
    </nav>
  )
}
