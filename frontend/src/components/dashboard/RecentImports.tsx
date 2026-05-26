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

function StatusBadge({ status }: { status: string }) {
  if (status === 'completed') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-50 text-green-700">
        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
        Completed
      </span>
    )
  }
  if (status === 'failed') {
    return <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-red-50 text-red-700">{status}</span>
  }
  return <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-50 text-yellow-700">{status}</span>
}

export default function RecentImports({ records }: Props) {
  const { data: batches } = useQuery({
    queryKey: ['import-batches'],
    queryFn: () => api.get('/ingestion/batches/').then((r) => r.data?.results || r.data || []),
  })

  const recentBatches = (batches || []).slice(-5)

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm h-full">
      <div className="p-6 pb-4">
        <h2 className="font-semibold text-gray-900 mb-4">Recent Imports</h2>
        {recentBatches.length === 0 ? (
          <p className="text-sm text-gray-400">No imports yet</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-400 text-xs uppercase tracking-wider border-b border-gray-100">
                <th className="pb-2 font-medium">Source</th>
                <th className="pb-2 font-medium">File Name</th>
                <th className="pb-2 font-medium text-right">Status</th>
              </tr>
            </thead>
            <tbody>
              {[...recentBatches].reverse().map((b: { id: number; source_type: string; filename: string; status: string }) => (
                <tr key={b.id} className="border-b border-gray-50 last:border-0">
                  <td className="py-3 capitalize text-gray-700">{b.source_type}</td>
                  <td className="py-3 text-gray-500">{b.filename}</td>
                  <td className="py-3 text-right">
                    <StatusBadge status={b.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="border-t border-gray-100 p-6 pt-4">
        <h2 className="font-semibold text-gray-900 mb-3">Suspicious Records</h2>
        {records.length === 0 ? (
          <p className="text-sm text-gray-400">No flagged records</p>
        ) : (
          <div className="space-y-2">
            {records.map((r) => (
              <Link
                key={r.id}
                to={`/review?id=${r.id}`}
                className="flex items-center gap-3 text-sm hover:bg-gray-50 rounded-lg p-2 -mx-2 transition-colors"
              >
                <span className="inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-50 text-red-800">
                  {r.flag}
                </span>
                <span className="text-gray-600 truncate">{r.activity_type}</span>
                <span className="ml-auto font-semibold text-gray-800 whitespace-nowrap">
                  {parseFloat(r.co2e_amount).toLocaleString()} kgCO₂e
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
