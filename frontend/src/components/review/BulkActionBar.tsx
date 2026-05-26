import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import api from '../../lib/api'

interface Props {
  selectedIds: number[]
  onDone: () => void
}

export default function BulkActionBar({ selectedIds, onDone }: Props) {
  const [action, setAction] = useState('approve')
  const [flagType, setFlagType] = useState('outlier')

  const mutation = useMutation({
    mutationFn: (data: { record_ids: number[]; action: string; flag_type?: string }) =>
      api.post('/emissions/records/bulk_action/', data),
    onSuccess: onDone,
  })

  return (
    <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-4 flex items-center gap-3">
      <span className="text-sm font-medium">{selectedIds.length} selected</span>
      <select
        value={action}
        onChange={(e) => setAction(e.target.value)}
        className="border border-gray-300 rounded px-2 py-1 text-sm"
      >
        <option value="approve">Approve</option>
        <option value="reject">Reject</option>
        <option value="lock">Lock</option>
        <option value="flag">Flag</option>
      </select>
      {action === 'flag' && (
        <select
          value={flagType}
          onChange={(e) => setFlagType(e.target.value)}
          className="border border-gray-300 rounded px-2 py-1 text-sm"
        >
          <option value="outlier">Outlier</option>
          <option value="missing_data">Missing Data</option>
          <option value="duplicate">Duplicate</option>
          <option value="unit_ambiguity">Unit Ambiguity</option>
        </select>
      )}
      <button
        onClick={() => mutation.mutate({ record_ids: selectedIds, action, flag_type: action === 'flag' ? flagType : undefined })}
        disabled={mutation.isPending}
        className="bg-blue-600 text-white px-4 py-1 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
      >
        {mutation.isPending ? 'Processing...' : 'Apply'}
      </button>
      {mutation.isError && <span className="text-red-600 text-sm">Action failed</span>}
    </div>
  )
}
