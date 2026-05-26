import { Link } from 'react-router-dom'
import api from '../../lib/api'
import { useQuery } from '@tanstack/react-query'

interface SuspiciousRecord {
  id: number
  activity_type: string
  flag: string
  co2e_amount: string
}

interface Props {
  records: SuspiciousRecord[]
}

export default function RecentImports({ records }: Props) {
  const { data: batches } = useQuery({
    queryKey: ['import-batches'],
    queryFn: () => api.get('/ingestion/batches/').then((r) => r.data?.results || r.data || []),
  })

  const recentBatches = (batches || []).slice(-5)

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="font-semibold mb-4">Recent Imports</h2>
        {recentBatches.length === 0 ? (
          <p className="text-sm text-gray-400">No imports yet</p>
        ) : (
          <div className="space-y-2">
            {recentBatches.map((b: { id: number; source_type: string; filename: string; status: string; created_at: string }) => (
              <div key={b.id} className="flex justify-between text-sm">
                <span className="capitalize">{b.source_type}</span>
                <span className="text-gray-500">{b.filename}</span>
                <span className={`${b.status === 'completed' ? 'text-green-600' : b.status === 'failed' ? 'text-red-600' : 'text-yellow-600'}`}>
                  {b.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="font-semibold mb-4">Suspicious Records</h2>
        {records.length === 0 ? (
          <p className="text-sm text-gray-400">No flagged records</p>
        ) : (
          <div className="space-y-2">
            {records.map((r) => (
              <Link key={r.id} to={`/review?id=${r.id}`} className="block text-sm hover:bg-gray-50 p-1 rounded">
                <span className="text-red-600 font-medium">{r.flag}</span>
                {' — '}{r.activity_type}
                <span className="text-gray-400 ml-2">{parseFloat(r.co2e_amount).toLocaleString()} kgCO₂e</span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
