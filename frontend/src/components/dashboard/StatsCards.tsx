interface Summary {
  total_records: number
  pending_review: number
  flagged: number
  approved: number
  total_co2e_kg: string
}

export function HeroCard({ totalCo2eKg }: { totalCo2eKg: string }) {
  const tonnes = parseFloat((parseFloat(totalCo2eKg) / 1000).toFixed(2))
  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 h-full">
      <div className="text-sm text-gray-500 mb-1">Total CO₂e</div>
      <div className="flex items-baseline gap-1">
        <span className="text-4xl font-bold text-gray-900">{tonnes.toLocaleString()}</span>
        <span className="text-xl text-gray-500 font-medium">tCO₂e</span>
      </div>
    </div>
  )
}

const kpiCards = [
  { label: 'Total Records', key: 'total_records' as const, dotColor: 'bg-blue-500' },
  { label: 'Pending Review', key: 'pending_review' as const, dotColor: 'bg-yellow-500' },
  { label: 'Flagged', key: 'flagged' as const, dotColor: 'bg-red-500' },
  { label: 'Approved', key: 'approved' as const, dotColor: 'bg-green-500' },
]

export function KPIGrid({ summary }: { summary: Summary }) {
  return (
    <div className="grid grid-cols-2 gap-4 h-full">
      {kpiCards.map((card) => (
        <div key={card.key} className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <div className={`w-3 h-3 rounded-full ${card.dotColor} mb-3`} />
          <div className="text-2xl font-bold text-gray-900">{summary[card.key]}</div>
          <div className="text-sm text-gray-500">{card.label}</div>
        </div>
      ))}
    </div>
  )
}
