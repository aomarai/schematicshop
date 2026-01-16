import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface User {
  id: number
  username: string
  email: string
  avatar?: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Load user from localStorage on mount
  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const response = await axios.get(`${API_URL}/api/auth/me/`, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          })
          setUser(response.data)
        } catch (error) {
          console.error('Failed to load user:', error)
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      }
      setLoading(false)
    }

    loadUser()
  }, [])

  const login = async (username: string, password: string) => {
    const response = await axios.post(`${API_URL}/api/auth/login/`, {
      username,
      password
    })

    const { access, refresh } = response.data
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)

    // Fetch user data
    const userResponse = await axios.get(`${API_URL}/api/auth/me/`, {
      headers: {
        Authorization: `Bearer ${access}`
      }
    })
    setUser(userResponse.data)
  }

  const register = async (username: string, email: string, password: string) => {
    await axios.post(`${API_URL}/api/auth/register/`, {
      username,
      email,
      password
    })

    // Auto-login after registration
    await login(username, password)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
