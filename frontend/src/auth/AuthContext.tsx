import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import {
  fetchMe,
  login as apiLogin,
  registerCustomer,
  type CurrentUser,
  type RegisterPayload,
} from '../api/client'
import { clearToken, getToken, setToken, subscribeToken } from './authStore'

interface AuthContextValue {
  user: CurrentUser | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshUser = async () => {
    if (!getToken()) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      setUser(await fetchMe())
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refreshUser()
    return subscribeToken((token) => {
      if (!token) setUser(null)
    })
  }, [])

  const login = async (email: string, password: string) => {
    setToken(await apiLogin(email, password))
    await refreshUser()
  }

  const register = async (payload: RegisterPayload) => {
    setToken(await registerCustomer(payload))
    await refreshUser()
  }

  const logout = () => {
    clearToken()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>{children}</AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
