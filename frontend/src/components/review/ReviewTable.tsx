import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../../lib/api'
import EmissionDetail from './EmissionDetail'

interface Record {
  id: number
  activity_type: string
  scope: number
  co2e_amount: string
  status: string
  flag: string
  activity_date_start: string
  source_type: string
  subcategory: string
}

export default function ReviewTable() {
  const [page, setPage] = useState(1)
  const [status, setStatus] = useState('')
  const [scope, setScope] = useState('')
  const [flag, setFlag] = useState('')
  const [sourceType, setSourceType] = useState('')
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState<Set<number>>(new Set())
  const [detailId, setDetailId] = useState<number | null>(null)

  const params = new URLSearchParams({ organization: '1', page: String(page) })
  if (status) params.set('status', status)
  if (scope) params.set('scope', scope)
  if (flag) params.set('flag', flag)
  if (sourceType) params.set('source_type', sourceType)
  if (search) params.set('search', search)

  const { data, isLoading } = useQuery({
    queryKey: ['emissions', params.toString()],
    queryFn: () => api.get(`/emissions/records/?${params}`).then((r) => r.data),
  })

  const toggleSelect = (id: number) => {
    const next = new Set(selected)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setSelected(next)
  }

  const records: Record[] = data?.results || []
  const totalPages = data?.count ? Math.ceil(data.count / 50) : 1

  const badgeClass = (val: string, map: Record<string, string>) =>
    `px-2 py-0.5 rounded text-xs font-medium ${map[val] || ''}`

  const statusColors: Record<string, string> = {
    imported: 'bg-gray-100 text-gray-700',
    approved: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
    locked: 'bg-blue-100 text-blue-700',
  }
  const flagColors: Record<string, string> = {
    none: '',
    outlier: 'bg-red-100 text-red-700',
    missing_data: 'bg-yellow-100 text-yellow-700',
    duplicate: 'bg-purple-100 text-purple-700',
    unit_ambiguity: 'bg-orange-100 text-orange-700',
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Review Emissions</h1>

      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap gap-3 mb-4">
          <input
            placeholder="Search activity..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="border border-gray-300 rounded px-3 py-1.5 text-sm"
          />
          <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1) }} className="border border-gray-300 rounded px-3 py-1.5 text-sm">
            <option value="">All Status</option>
            <option value="imported">Imported</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="locked">Locked</option>
          </select>
          <select value={scope} onChange={(e) => { setScope(e.target.value); setPage(1) }} className="border border-gray-300 rounded px-3 py-1.5 text-sm">
            <option value="">All Scopes</option>
            <option value="1">Scope 1</option>
            <option value="2">Scope 2</option>
            <option value="3">Scope 3</option>
          </select>
          <select value={flag} onChange={(e) => { setFlag(e.target.value); setPage(1) }} className="border border-gray-300 rounded px-3 py-1.5 text-sm">
            <option value="">All Flags</option>
            <option value="outlier">Outlier</option>
            <option value="missing_data">Missing Data</option>
            <option value="duplicate">Duplicate</option>
            <option value="unit_ambiguity">Unit Ambiguity</option>
          </select>
          <select value={sourceType} onChange={(e) => { setSourceType(e.target.value); setPage(1) }} className="border border-gray-300 rounded px-3 py-1.5 text-sm">
            <option value="">All Sources</option>
            <option value="utility">Utility</option>
            <option value="sap">SAP</option>
            <option value="travel">Travel</option>
          </select>
        </div>

        {isLoading ? (
          <p className="text-gray-400 text-sm py-8 text-center">Loading records...</p>
        ) : records.length === 0 ? (
          <p className="text-gray-400 text-sm py-8 text-center">No records found</p>
        ) : (
          <>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 w-8"><input type="checkbox" className="hidden" /></th>
                  <th className="pb-2">Activity</th>
                  <th className="pb-2">Scope</th>
                  <th className="pb-2">CO₂e (kg)</th>
                  <th className="pb-2">Status</th>
                  <th className="pb-2">Flag</th>
                  <th className="pb-2">Date</th>
                  <th className="pb-2">Source</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r) => (
                  <tr key={r.id} className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer" onClick={() => setDetailId(r.id)}>
                    <td className="py-2" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={selected.has(r.id)}
                        onChange={() => toggleSelect(r.id)}
                      />
                    </td>
                    <td className="py-2">{r.activity_type}</td>
                    <td className="py-2">Scope {r.scope}</td>
                    <td className="py-2">{parseFloat(r.co2e_amount).toLocaleString()}</td>
                    <td className="py-2"><span className={badgeClass(r.status, statusColors)}>{r.status}</span></td>
                    <td className="py-2">{r.flag !== 'none' && <span className={badgeClass(r.flag, flagColors)}>{r.flag}</span>}</td>
                    <td className="py-2 text-gray-500">{r.activity_date_start || '-'}</td>
                    <td className="py-2 capitalize">{r.source_type}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="flex justify-between items-center mt-4 text-sm text-gray-500">
              <span>{data?.count || 0} total records</span>
              <div className="flex gap-2">
                <button disabled={page <= 1} onClick={() => setPage(page - 1)} className="px-3 py-1 border rounded disabled:opacity-50">Prev</button>
                <span className="px-3 py-1">Page {page} of {totalPages}</span>
                <button disabled={page >= totalPages} onClick={() => setPage(page + 1)} className="px-3 py-1 border rounded disabled:opacity-50">Next</button>
              </div>
            </div>
          </>
        )}
      </div>

      {detailId && <EmissionDetail id={detailId} onClose={() => setDetailId(null)} />}
    </div>
  )
}
