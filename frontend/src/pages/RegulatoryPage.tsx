import { usePlatform } from '../context/PlatformContext'
import { RegChip } from '../components/StatusChip'

export function RegulatoryPage() {
  const { snapshot } = usePlatform()
  if (!snapshot) return null

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Регуляторный скрининг РФ</h2>
        <p className="mt-1 max-w-2xl text-sm text-ink-500">
          Обязательный блок: ПДн, КИИ/ГИС, категории моделей, HITL, распределение ответственности.
          Фильтр допустимости кейсов встроен в анализ.
        </p>
      </div>

      <div className="grid gap-3">
        {snapshot.regulatory.map((check) => (
          <article key={check.id} className="panel p-5">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="font-semibold text-ink-900">{check.title}</h3>
              <RegChip status={check.status} />
            </div>
            <p className="mt-1 text-xs uppercase tracking-[0.12em] text-ink-500">{check.basis}</p>
            <p className="mt-3 text-sm leading-relaxed text-ink-600">{check.detail}</p>
          </article>
        ))}
      </div>

      <section className="panel p-5">
        <h3 className="font-display text-lg font-bold">Кейсы после фильтра</h3>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {snapshot.opportunities.map((o) => (
            <div
              key={o.id}
              className={`rounded-xl border px-4 py-3 text-sm ${
                o.admissible ? 'border-moss-100 bg-moss-100/30' : 'border-red-100 bg-red-50'
              }`}
            >
              <div className="font-medium">{o.title}</div>
              <p className="mt-1 text-ink-600">
                Автономия {o.autonomy_level} · {o.admissible ? 'допустим' : 'заблокирован'}
              </p>
              <p className="mt-1 text-xs text-ink-500">{o.regulatory_flags.join(' · ')}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
