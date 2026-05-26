import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function AuthGuard() {
  const token = useAuth((s) => s.token)
  if (!token) return <Navigate to="/login" replace />
  return <Outlet />
}
