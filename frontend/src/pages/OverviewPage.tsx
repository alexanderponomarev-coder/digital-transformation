import { Link } from 'react-router-dom'
import { usePlatform } from '../context/PlatformContext'
import { CoverageChip } from '../components/StatusChip'
import { LAYER_LABEL, pct } from '../lib/labels'

export function OverviewPage() {
  const { snapshot } = usePlatform()
  if (!snapshot) return null
  const { overview, coverage, engine_metrics, opportunities, regulatory } = snapshot

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-4">
        {[
          { label: 'Покрытие', value: pct(overview.overall_coverage) },
          { label: 'Открытые вопросы', value: String(overview.open_questions_count) },
          { label: 'Утверждено', value: String(overview.approved_insights_count) },
          { label: 'Блокировки', value: String(overview.blocked_cases_count) },
        ].map((item) => (
          <div key={item.label} className="panel p-4">
            <p className="text-xs uppercase tracking-[0.14em] text-ink-500">{item.label}</p>
            <p className="mt-2 font-display text-3xl font-bold text-ink-900">{item.value}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="panel p-5">
          <div className="mb-4 flex items-end justify-between gap-3">
            <div>
              <h2 className="font-display text-lg font-bold">Карта покрытия методологии</h2>
              <p className="text-sm text-ink-500">
                Порог выводов: {pct(overview.coverage_threshold)}. Ниже — только вопросы.
              </p>
            </div>
            <Link to="/app/coverage" className="text-sm font-semibold text-tide-600">
              Подробнее
            </Link>
          </div>
          <div className="space-y-3">
            {coverage.map((layer) => (
              <div key={layer.layer_id} className="rounded-xl border border-ink-100 p-3">
                <div className="mb-2 flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{LAYER_LABEL[layer.layer_id]}</span>
                    <CoverageChip status={layer.status} />
                  </div>
                  <span className="text-sm text-ink-500">{pct(layer.score)}</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-ink-50">
                  <div
                    className="h-full origin-left animate-fillbar rounded-full bg-tide-500"
                    style={{ width: `${Math.round(layer.score * 100)}%` }}
                  />
                </div>
                {!layer.can_infer && (
                  <p className="mt-2 text-xs text-ember-600">
                    Выводы заблокированы — покрытие ниже порога или слой вне MVP.
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <div className="panel p-5">
            <h2 className="font-display text-lg font-bold">AI Transformation Engine</h2>
            <ul className="mt-4 space-y-3 text-sm">
              <li className="flex justify-between">
                <span className="text-ink-500">Точность извлечения</span>
                <span className="font-semibold">{pct(engine_metrics.extraction_accuracy)}</span>
              </li>
              <li className="flex justify-between">
                <span className="text-ink-500">Доля галлюцинаций</span>
                <span className="font-semibold">{pct(engine_metrics.hallucination_rate)}</span>
              </li>
              <li className="flex justify-between">
                <span className="text-ink-500">Полнота покрытия</span>
                <span className="font-semibold">{pct(engine_metrics.coverage_completeness)}</span>
              </li>
            </ul>
          </div>

          <div className="panel p-5">
            <h2 className="font-display text-lg font-bold">Допустимые возможности</h2>
            <p className="mt-1 text-sm text-ink-500">
              {opportunities.filter((o) => o.admissible).length} из {opportunities.length} прошли
              фильтр
            </p>
            <ul className="mt-3 space-y-2">
              {opportunities.slice(0, 3).map((o) => (
                <li key={o.id} className="rounded-lg bg-ink-50 px-3 py-2 text-sm">
                  <div className="font-medium">{o.title}</div>
                  <div className="text-xs text-ink-500">
                    {o.admissible ? 'Допустимо' : 'Заблокировано'} · ур. {o.autonomy_level}
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div className="panel p-5">
            <h2 className="font-display text-lg font-bold">Регуляторный статус</h2>
            <div className="mt-3 flex flex-wrap gap-2">
              {regulatory.map((r) => (
                <span
                  key={r.id}
                  className={`chip ${
                    r.status === 'pass'
                      ? 'bg-moss-100 text-moss-600'
                      : r.status === 'warn'
                        ? 'bg-ember-100 text-ember-600'
                        : 'bg-red-100 text-red-700'
                  }`}
                >
                  {r.title}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
