import { create } from 'zustand'
import api from '../lib/api'

interface AuthState {
  user: { email: string } | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: () => boolean
}

export const useAuth = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  login: async (email: string, password: string) => {
    const { data } = await api.post('/auth/login/', {
      username: email,
      password,
    })
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    set({ token: data.access, user: { email } })
  },
  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ token: null, user: null })
    window.location.href = '/login'
  },
  isAuthenticated: () => {
    return !!get().token
  },
}))
