import { Link } from 'react-router-dom'
import { usePlatform } from '../context/PlatformContext'
import { CoverageChip } from '../components/StatusChip'
import { LAYER_LABEL, pct } from '../lib/labels'

export function CoveragePage() {
  const { snapshot } = usePlatform()
  if (!snapshot) return null

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Карта покрытия</h2>
        <p className="mt-1 max-w-2xl text-sm text-ink-500">
          Матрица «раздел методологии × статус». Слепые зоны — то, что документы принципиально не
          закрывают. По каждой зоне — вопросы ответственному.
        </p>
      </div>

      <div className="grid gap-4">
        {snapshot.coverage.map((layer) => {
          const layerMeta = snapshot.layers.find((l) => l.id === layer.layer_id)
          const docs = snapshot.documents.filter((d) => layer.document_ids.includes(d.id))
          return (
            <article key={layer.layer_id} className="panel p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-display text-lg font-bold">
                      {layerMeta?.number}. {LAYER_LABEL[layer.layer_id]}
                    </h3>
                    <CoverageChip status={layer.status} />
                    {layerMeta && !layerMeta.mvp && (
                      <span className="chip bg-ink-100 text-ink-500">V2/V3</span>
                    )}
                  </div>
                  <p className="mt-1 text-sm text-ink-500">{layerMeta?.description}</p>
                </div>
                <div className="text-right">
                  <div className="font-display text-2xl font-bold">{pct(layer.score)}</div>
                  <div className="text-xs text-ink-500">
                    порог {pct(layer.threshold)} ·{' '}
                    {layer.can_infer ? 'выводы разрешены' : 'только вопросы'}
                  </div>
                </div>
              </div>

              <div className="mt-4 h-2 overflow-hidden rounded-full bg-ink-50">
                <div
                  className="h-full origin-left animate-fillbar rounded-full bg-tide-500"
                  style={{ width: `${Math.round(layer.score * 100)}%` }}
                />
              </div>

              <div className="mt-5 grid gap-4 md:grid-cols-2">
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-[0.14em] text-ink-500">
                    Документы
                  </h4>
                  <ul className="mt-2 space-y-1 text-sm">
                    {docs.length === 0 && <li className="text-ink-500">Нет документов</li>}
                    {docs.map((d) => (
                      <li key={d.id}>
                        {d.title}{' '}
                        <span className="text-ink-500">({d.freshness_days} дн)</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-[0.14em] text-ink-500">
                    Слепые зоны
                  </h4>
                  <ul className="mt-2 space-y-2">
                    {layer.blind_zones.length === 0 && (
                      <li className="text-sm text-ink-500">Не отмечены</li>
                    )}
                    {layer.blind_zones.map((bz) => (
                      <li key={bz.id} className="rounded-lg bg-ember-100/60 px-3 py-2 text-sm">
                        <div className="font-medium text-ember-600">{bz.title}</div>
                        <p className="text-ink-600">{bz.reason}</p>
                        {bz.question_ids.length > 0 && (
                          <Link
                            to="/app/questions"
                            className="mt-1 inline-block text-xs font-semibold text-tide-600"
                          >
                            Вопросы: {bz.question_ids.join(', ')}
                          </Link>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </article>
          )
        })}
      </div>
    </div>
  )
}
