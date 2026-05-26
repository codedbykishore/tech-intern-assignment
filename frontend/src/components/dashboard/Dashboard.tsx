import { useQuery } from '@tanstack/react-query'
import api from '../../lib/api'
import { HeroCard, KPIGrid } from './StatsCards'
import ScopeBreakdown from './ScopeBreakdown'
import RecentImports from './RecentImports'

interface DashboardData {
  summary: {
    total_records: number
    pending_review: number
    flagged: number
    approved: number
    total_co2e_kg: string
  }
  scope_breakdown: { scope: number; count: number; total_co2e_kg: string }[]
  recent_suspicious: { id: number; activity_type: string; flag: string; co2e_amount: string }[]
}

export default function Dashboard() {
  const { data, isLoading } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: () => api.get('/analytics/dashboard/?organization=1').then((r) => r.data),
    refetchInterval: 30000,
  })

  if (isLoading) return <div className="text-gray-500">Loading dashboard...</div>
  if (!data) return <div className="text-red-500">Failed to load dashboard</div>

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-4">
          <HeroCard totalCo2eKg={data.summary.total_co2e_kg} />
        </div>
        <div className="col-span-12 lg:col-span-8">
          <KPIGrid summary={data.summary} />
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-6">
          <ScopeBreakdown data={data.scope_breakdown} />
        </div>
        <div className="col-span-12 lg:col-span-6">
          <RecentImports records={data.recent_suspicious} />
        </div>
      </div>
    </div>
  )
}
