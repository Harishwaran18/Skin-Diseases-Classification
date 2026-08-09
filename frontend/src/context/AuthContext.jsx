import { createContext, useContext, useState, useCallback } from 'react'
import { api } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const s = localStorage.getItem('skincare_user')
    return s ? JSON.parse(s) : null
  })

  const persist = (data) => {
    localStorage.setItem('skincare_token', data.access_token)
    const u = { user_id: data.user_id, full_name: data.full_name, is_demo: data.is_demo }
    localStorage.setItem('skincare_user', JSON.stringify(u))
    setUser(u)
  }

  const login = useCallback(async (email, password) => {
    const data = await api.login(email, password)
    persist(data)
    return data
  }, [])

  const register = useCallback(async (email, fullName, password) => {
    const data = await api.register(email, fullName, password)
    persist(data)
    return data
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('skincare_token')
    localStorage.removeItem('skincare_user')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
