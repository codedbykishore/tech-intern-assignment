interface Props {
  data: { scope: number; count: number; total_co2e_kg: string }[]
}

const scopeColors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500']
const scopeLabels = ['Scope 1', 'Scope 2', 'Scope 3']

export default function ScopeBreakdown({ data }: Props) {
  const total = data.reduce((sum, s) => sum + parseFloat(s.total_co2e_kg), 0)

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="font-semibold mb-4">Scope Breakdown</h2>
      <div className="space-y-3">
        {data.map((item, i) => {
          const pct = total > 0 ? (parseFloat(item.total_co2e_kg) / total) * 100 : 0
          return (
            <div key={item.scope}>
              <div className="flex justify-between text-sm mb-1">
                <span>{scopeLabels[i]}</span>
                <span>{pct.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`${scopeColors[i]} h-2 rounded-full`}
                  style={{ width: `${pct}%` }}
                />
              </div>
              <div className="text-xs text-gray-400 mt-1">
                {item.count} records · {parseFloat(item.total_co2e_kg).toLocaleString()} kgCO₂e
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
