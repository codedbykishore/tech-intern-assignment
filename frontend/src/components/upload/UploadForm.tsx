import { useState, useRef } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import api from '../../lib/api'

const SOURCE_OPTIONS = [
  { value: 'utility', label: 'Utility (Electricity)' },
  { value: 'sap', label: 'SAP (Fuel & Procurement)' },
  { value: 'travel', label: 'Travel (Concur)' },
]

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null)
  const [sourceType, setSourceType] = useState('utility')
  const [dragOver, setDragOver] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)
  const queryClient = useQueryClient()

  const { data: batches, isLoading: batchesLoading } = useQuery({
    queryKey: ['import-batches'],
    queryFn: () => api.get('/ingestion/batches/').then((r) => r.data?.results || r.data || []),
  })

  const uploadMutation = useMutation({
    mutationFn: (formData: FormData) =>
      api.post('/ingestion/batches/upload/', formData),
    onSuccess: () => {
      setFile(null)
      queryClient.invalidateQueries({ queryKey: ['import-batches'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
    onError: (err) => {
      console.error('Upload failed:', err)
    },
  })

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped && dropped.name.endsWith('.csv')) setFile(dropped)
  }

  const handleSubmit = () => {
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    formData.append('source_type', sourceType)
    formData.append('org_id', '1')
    uploadMutation.mutate(formData)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Upload Data</h1>

      <div className="bg-white rounded-lg shadow p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Source Type</label>
          <select
            value={sourceType}
            onChange={(e) => setSourceType(e.target.value)}
            className="border border-gray-300 rounded px-3 py-2 w-full max-w-xs"
          >
            {SOURCE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer ${
            dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input
            ref={fileRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          {file ? (
            <p className="text-green-600">{file.name}</p>
          ) : (
            <p className="text-gray-500">Drop a CSV file here, or click to browse</p>
          )}
        </div>

        <button
          onClick={handleSubmit}
          disabled={!file || uploadMutation.isPending}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
        </button>

        {uploadMutation.isSuccess && (
          <p className="text-green-600 text-sm">
            Uploaded successfully — {uploadMutation.data?.data?.rows_imported} rows imported
          </p>
        )}
        {uploadMutation.isError && (
          <p className="text-red-600 text-sm">
            Upload failed: {(uploadMutation.error as any)?.response?.data?.error || 'Unknown error'}
          </p>
        )}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="font-semibold mb-4">Import History</h2>
        {batchesLoading ? (
          <p className="text-sm text-gray-400">Loading...</p>
        ) : !batches || batches.length === 0 ? (
          <p className="text-sm text-gray-400">No imports yet</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Source</th>
                <th className="pb-2">File</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Date</th>
              </tr>
            </thead>
            <tbody>
              {[...(batches || [])].reverse().map((b: { id: number; source_type: string; filename: string; status: string; created_at: string }) => (
                <tr key={b.id} className="border-b border-gray-100">
                  <td className="py-2 capitalize">{b.source_type}</td>
                  <td className="py-2">{b.filename}</td>
                  <td className="py-2">
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      b.status === 'completed' ? 'bg-green-100 text-green-700' :
                      b.status === 'failed' ? 'bg-red-100 text-red-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>{b.status}</span>
                  </td>
                  <td className="py-2">{new Date(b.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
