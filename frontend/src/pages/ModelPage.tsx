import { usePlatform } from '../context/PlatformContext'

const typeTone: Record<string, string> = {
  org: 'bg-ink-900 text-white',
  process: 'bg-tide-100 text-tide-600',
  system: 'bg-ember-100 text-ember-600',
  data: 'bg-moss-100 text-moss-600',
  agent: 'bg-tide-500 text-white',
  kpi: 'bg-ink-100 text-ink-800',
}

export function ModelPage() {
  const { snapshot } = usePlatform()
  if (!snapshot) return null

  const approved = snapshot.insights.filter((i) => i.approval === 'approved')
  const hypotheses = snapshot.insights.filter((i) => i.approval !== 'approved')
  const admissible = snapshot.opportunities.filter((o) => o.admissible)
  const blocked = snapshot.opportunities.filter((o) => !o.admissible)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Единая модель предприятия</h2>
        <p className="mt-1 max-w-2xl text-sm text-ink-500">
          AS-IS, карта возможностей и TO-BE. Утверждённое входит в модель; остальное помечено как
          гипотеза.
        </p>
      </div>

      <section className="panel p-5">
        <h3 className="font-display text-lg font-bold">Связанный граф</h3>
        <div className="mt-4 flex flex-wrap gap-3">
          {snapshot.model_nodes.map((node) => (
            <div
              key={node.id}
              className={`min-w-[160px] max-w-[220px] rounded-2xl px-4 py-3 ${typeTone[node.type]}`}
            >
              <div className="text-[10px] uppercase tracking-[0.16em] opacity-70">{node.type}</div>
              <div className="mt-1 text-sm font-semibold">{node.label}</div>
              {node.meta && <div className="mt-1 text-xs opacity-80">{node.meta}</div>}
              <div className="mt-2 text-[10px] opacity-70">
                связей: {node.linked_ids.length}
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="panel p-5">
          <h3 className="font-display text-lg font-bold">AS-IS (утверждено)</h3>
          <ul className="mt-3 space-y-2">
            {approved.map((i) => (
              <li key={i.id} className="rounded-xl bg-moss-100/50 px-3 py-2 text-sm">
                <div className="font-medium">{i.title}</div>
                <p className="text-ink-600">{i.body}</p>
              </li>
            ))}
            {approved.length === 0 && (
              <li className="text-sm text-ink-500">Пока нет утверждённых выводов.</li>
            )}
          </ul>
        </section>

        <section className="panel p-5">
          <h3 className="font-display text-lg font-bold">Гипотезы / на утверждении</h3>
          <ul className="mt-3 space-y-2">
            {hypotheses.map((i) => (
              <li key={i.id} className="rounded-xl bg-ember-100/40 px-3 py-2 text-sm">
                <div className="font-medium">{i.title}</div>
                <p className="text-ink-600">{i.body}</p>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="panel p-5">
          <h3 className="font-display text-lg font-bold">Карта возможностей</h3>
          <ul className="mt-3 space-y-2">
            {admissible.map((o) => (
              <li key={o.id} className="rounded-xl border border-ink-100 p-3 text-sm">
                <div className="font-medium">{o.title}</div>
                <p className="text-ink-500">
                  {o.process} · автономия {o.autonomy_level} · impact {o.impact}
                </p>
                <p className="mt-1 text-xs text-tide-600">{o.roi_hint}</p>
              </li>
            ))}
          </ul>
        </section>
        <section className="panel p-5">
          <h3 className="font-display text-lg font-bold">TO-BE и блокировки</h3>
          <p className="mt-2 rounded-xl bg-tide-100 px-3 py-2 text-sm text-tide-600">
            Целевой паттерн: агент-рекомендатель + HITL на деньги, договоры, доступы и ПДн.
          </p>
          <ul className="mt-3 space-y-2">
            {blocked.map((o) => (
              <li key={o.id} className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">
                <div className="font-medium">{o.title}</div>
                <p>{o.regulatory_flags.join(' · ')}</p>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  )
}
