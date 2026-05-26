interface Props {
  data: { scope: number; count: number; total_co2e_kg: string }[]
}

const COLORS = ['#3B82F6', '#10B981', '#8B5CF6']
const SCOPE_LABELS = ['Scope 1', 'Scope 2', 'Scope 3']
const DOT_CLASSES = ['bg-blue-500', 'bg-green-500', 'bg-purple-500']

function DonutChart({ data }: Props) {
  const total = data.reduce((sum, s) => sum + parseFloat(s.total_co2e_kg), 0)
  const percentages = data.map((s) => (total > 0 ? (parseFloat(s.total_co2e_kg) / total) * 100 : 0))

  const size = 160
  const strokeWidth = 20
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const cx = size / 2
  const cy = size / 2

  let cumulative = 0
  const segments = percentages.map((pct) => {
    const length = circumference * (pct / 100)
    const seg = { length, offset: cumulative }
    cumulative += length
    return seg
  })

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={cx} cy={cy} r={radius} fill="none" stroke="#E5E7EB" strokeWidth={strokeWidth} />
      {segments.map((seg, i) => (
        <circle
          key={i}
          cx={cx}
          cy={cy}
          r={radius}
          fill="none"
          stroke={COLORS[i]}
          strokeWidth={strokeWidth}
          strokeDasharray={`${seg.length} ${circumference - seg.length}`}
          strokeDashoffset={-seg.offset}
          transform={`rotate(-90 ${cx} ${cy})`}
        />
      ))}
      <text x={cx} y={cy - 6} textAnchor="middle" className="fill-gray-700 text-sm font-bold">
        Total
      </text>
      <text x={cx} y={cy + 12} textAnchor="middle" className="fill-gray-500 text-xs">
        CO₂e
      </text>
    </svg>
  )
}

export default function ScopeBreakdown({ data }: Props) {
  const total = data.reduce((sum, s) => sum + parseFloat(s.total_co2e_kg), 0)

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 h-full">
      <h2 className="font-semibold text-gray-900 mb-6">Scope Breakdown</h2>
      <div className="flex flex-col sm:flex-row items-center gap-8">
        <DonutChart data={data} />
        <div className="space-y-5 flex-1 w-full">
          {data.map((item, i) => {
            const pct = total > 0 ? (parseFloat(item.total_co2e_kg) / total) * 100 : 0
            return (
              <div key={item.scope}>
                <div className="flex items-center gap-2 mb-1">
                  <div className={`w-2.5 h-2.5 rounded-full ${DOT_CLASSES[i]}`} />
                  <span className="text-sm font-medium text-gray-700">{SCOPE_LABELS[i]}</span>
                  <span className="ml-auto text-sm font-semibold text-gray-900">{pct.toFixed(1)}%</span>
                </div>
                <div className="text-xs text-gray-400 ml-[18px]">
                  {item.count} records · {parseFloat(item.total_co2e_kg).toLocaleString()} kgCO₂e
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
