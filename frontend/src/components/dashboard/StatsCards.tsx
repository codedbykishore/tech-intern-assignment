interface Props {
  summary: {
    total_records: number
    pending_review: number
    flagged: number
    approved: number
    total_co2e_kg: string
  }
}

const cards = [
  { label: 'Total Records', key: 'total_records', color: 'bg-blue-500' },
  { label: 'Pending Review', key: 'pending_review', color: 'bg-yellow-500' },
  { label: 'Flagged', key: 'flagged', color: 'bg-red-500' },
  { label: 'Approved', key: 'approved', color: 'bg-green-500' },
]

export default function StatsCards({ summary }: Props) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div key={card.key} className="bg-white rounded-lg shadow p-4">
          <div className={`w-3 h-3 rounded-full ${card.color} mb-2`} />
          <div className="text-2xl font-bold">{summary[card.key as keyof typeof summary]}</div>
          <div className="text-sm text-gray-500">{card.label}</div>
        </div>
      ))}
      <div className="bg-white rounded-lg shadow p-4 col-span-2 lg:col-span-4">
        <div className="text-sm text-gray-500">Total CO₂e</div>
        <div className="text-2xl font-bold">{parseFloat(summary.total_co2e_kg).toLocaleString()} kg</div>
      </div>
    </div>
  )
}
