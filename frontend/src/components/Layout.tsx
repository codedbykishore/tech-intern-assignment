import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const navItems = [
  { path: '/', label: 'Dashboard' },
  { path: '/upload', label: 'Upload' },
  { path: '/review', label: 'Review' },
]

export default function Layout() {
  const location = useLocation()
  const logout = useAuth((s) => s.logout)

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <span className="font-bold text-lg">Breathe ESG</span>
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`text-sm ${location.pathname === item.path ? 'text-blue-600 font-medium' : 'text-gray-600 hover:text-gray-900'}`}
            >
              {item.label}
            </Link>
          ))}
        </div>
        <button onClick={logout} className="text-sm text-gray-600 hover:text-gray-900">
          Sign Out
        </button>
      </nav>
      <main className="p-6">
        <Outlet />
      </main>
    </div>
  )
}
