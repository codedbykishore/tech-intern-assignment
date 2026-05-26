import { useQuery } from '@tanstack/react-query'
import api from '../../lib/api'

interface Props {
  id: number
  onClose: () => void
}

interface AuditLog {
  id: number
  action: string
  field_name: string
  old_value: string
  new_value: string
  changed_by_name: string
  timestamp: string
}

interface Detail {
  id: number
  activity_type: string
  scope: number
  subcategory: string
  co2e_amount: string
  status: string
  flag: string
  source_type: string
  activity_quantity: string
  activity_unit: string
  emission_factor_used: string
  activity_date_start: string
  activity_date_end: string
  facility_or_plant: string
  analyst_notes: string
  reviewed_by_name: string | null
  locked_by_name: string | null
  import_batch_filename: string
  audit_logs: AuditLog[]
}

export default function EmissionDetail({ id, onClose }: Props) {
  const { data, isLoading } = useQuery<Detail>({
    queryKey: ['emission', id],
    queryFn: () => api.get(`/emissions/records/${id}/`).then((r) => r.data),
  })

  return (
    <div className="fixed inset-0 bg-black/30 z-50 flex justify-end" onClick={onClose}>
      <div className="bg-white w-full max-w-lg overflow-y-auto p-6" onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-bold">Record Detail</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
        </div>

        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : !data ? (
          <p className="text-red-500">Failed to load</p>
        ) : (
          <div className="space-y-6">
            <Section label="Activity" value={data.activity_type} />
            <Section label="Scope" value={`Scope ${data.scope}`} />
            <Section label="Subcategory" value={data.subcategory} />
            <Section label="Quantity" value={data.activity_quantity ? `${data.activity_quantity} ${data.activity_unit}` : '-'} />
            <Section label="CO₂e" value={`${parseFloat(data.co2e_amount).toLocaleString()} kgCO₂e`} />
            <Section label="Emission Factor" value={data.emission_factor_used} />
            <Section label="Status" value={data.status} />
            <Section label="Flag" value={data.flag} />
            <Section label="Source" value={data.source_type} />
            <Section label="Facility/Plant" value={data.facility_or_plant} />
            <Section label="Period" value={data.activity_date_start && data.activity_date_end ? `${data.activity_date_start} — ${data.activity_date_end}` : '-'} />
            <Section label="Import File" value={data.import_batch_filename || '-'} />
            <Section label="Reviewed By" value={data.reviewed_by_name || '-'} />
            <Section label="Locked By" value={data.locked_by_name || '-'} />

            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-1">Analyst Notes</h3>
              <textarea
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                rows={3}
                defaultValue={data.analyst_notes}
                onBlur={(e) => {
                  if (e.target.value !== data.analyst_notes) {
                    api.patch(`/emissions/records/${id}/`, { analyst_notes: e.target.value })
                  }
                }}
              />
            </div>

            <div>
              <h3 className="font-semibold mb-2">Audit Log</h3>
              <div className="space-y-2">
                {data.audit_logs.map((log) => (
                  <div key={log.id} className="text-xs text-gray-600 border-l-2 border-gray-200 pl-3">
                    <span className="font-medium capitalize">{log.action}</span>
                    {log.field_name && (
                      <span> — {log.field_name}: "{log.old_value}" → "{log.new_value}"</span>
                    )}
                    <div className="text-gray-400">{log.changed_by_name} · {new Date(log.timestamp).toLocaleString()}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function Section({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="text-xs text-gray-400 uppercase tracking-wide">{label}</span>
      <p className="text-sm">{value}</p>
    </div>
  )
}
