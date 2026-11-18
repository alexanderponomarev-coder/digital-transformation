import { usePlatform } from '../context/PlatformContext'

export function RoadmapPage() {
  const { snapshot } = usePlatform()
  if (!snapshot) return null
  const { roadmap, roi } = snapshot

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Дорожная карта и ROI</h2>
        <p className="mt-1 max-w-2xl text-sm text-ink-500">
          Прогнозная оценка на этапе планирования. Фактический ROI — в V3 после внедрения.
        </p>
      </div>

      <section className="grid gap-4 md:grid-cols-4">
        {[
          { label: 'Инвестиции', value: `${roi.investment_mln} млн ₽` },
          { label: 'Выгода / год', value: `${roi.annual_benefit_mln} млн ₽` },
          { label: 'Окупаемость', value: `${roi.payback_months} мес` },
          { label: 'TCO 3 года', value: `${roi.tco_3y_mln} млн ₽` },
        ].map((item) => (
          <div key={item.label} className="panel p-4">
            <p className="text-xs uppercase tracking-[0.14em] text-ink-500">{item.label}</p>
            <p className="mt-2 font-display text-2xl font-bold">{item.value}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        {roadmap.map((phase, idx) => (
          <article key={phase.id} className="panel p-5">
            <p className="text-xs uppercase tracking-[0.16em] text-tide-600">Фаза {idx}</p>
            <h3 className="mt-1 font-display text-lg font-bold">{phase.name}</h3>
            <p className="text-sm text-ink-500">
              {phase.horizon} · {phase.investment_mln} млн ₽
            </p>
            <ul className="mt-4 space-y-2 text-sm">
              {phase.items.map((item) => (
                <li key={item} className="rounded-lg bg-ink-50 px-3 py-2">
                  {item}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="panel p-5">
          <h3 className="font-display text-lg font-bold">KPI до / после</h3>
          <table className="mt-3 w-full text-left text-sm">
            <thead>
              <tr className="text-xs uppercase tracking-[0.12em] text-ink-500">
                <th className="py-2 font-medium">Показатель</th>
                <th className="py-2 font-medium">AS-IS</th>
                <th className="py-2 font-medium">TO-BE</th>
              </tr>
            </thead>
            <tbody>
              {roi.kpis.map((kpi) => (
                <tr key={kpi.name} className="border-t border-ink-100">
                  <td className="py-2 pr-2">{kpi.name}</td>
                  <td className="py-2 pr-2 text-ink-500">{kpi.as_is}</td>
                  <td className="py-2 font-semibold text-tide-600">{kpi.to_be}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="panel p-5">
          <h3 className="font-display text-lg font-bold">Допущения прогноза</h3>
          <ul className="mt-3 space-y-2 text-sm text-ink-600">
            {roi.assumptions.map((a) => (
              <li key={a} className="rounded-lg border border-ink-100 px-3 py-2">
                {a}
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  )
}
