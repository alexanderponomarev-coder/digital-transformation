import { usePlatform } from '../context/PlatformContext'
import { ApprovalChip } from '../components/StatusChip'
import { CONFIDENCE_LABEL, LAYER_LABEL } from '../lib/labels'
import { api } from '../lib/api'

export function MethodologyPage() {
  const { snapshot, setSnapshot } = usePlatform()
  if (!snapshot) return null

  const mvpLayers = snapshot.layers.filter((l) => l.mvp)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Автопрохождение методологии</h2>
        <p className="mt-1 max-w-2xl text-sm text-ink-500">
          MVP: слои 1–3. Факты → выводы → предложения. Каждый вывод со ссылкой на источник и явным
          уровнем достоверности. Существенное — только после утверждения человеком.
        </p>
      </div>

      {mvpLayers.map((layer) => {
        const coverage = snapshot.coverage.find((c) => c.layer_id === layer.id)
        const facts = snapshot.facts.filter((f) => f.layers.includes(layer.id))
        const insights = snapshot.insights.filter((i) => i.layer_id === layer.id)

        return (
          <section key={layer.id} className="panel p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h3 className="font-display text-lg font-bold">
                  Слой {layer.number}. {layer.title}
                </h3>
                <p className="mt-1 text-sm text-ink-500">{layer.practices.join(' · ')}</p>
              </div>
              <span className="chip bg-ink-100 text-ink-700">
                {coverage?.can_infer ? 'Выводы активны' : 'Только вопросы'}
              </span>
            </div>

            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-[0.14em] text-ink-500">
                  Факты ({facts.length})
                </h4>
                <ul className="mt-2 space-y-2">
                  {facts.map((fact) => (
                    <li key={fact.id} className="rounded-xl border border-ink-100 p-3 text-sm">
                      <p>{fact.text}</p>
                      <p className="mt-2 text-xs text-ink-500">
                        {fact.source.document_title} · «{fact.source.fragment}»
                        {fact.source.page ? ` · с.${fact.source.page}` : ''} · достоверность{' '}
                        {CONFIDENCE_LABEL[fact.confidence]}
                      </p>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="text-xs font-semibold uppercase tracking-[0.14em] text-ink-500">
                  Выводы и предложения ({insights.length})
                </h4>
                {!coverage?.can_infer && (
                  <p className="mt-2 rounded-xl bg-ember-100 px-3 py-2 text-sm text-ember-600">
                    Покрытие слоя «{LAYER_LABEL[layer.id]}» недостаточно для устойчивых выводов.
                  </p>
                )}
                <ul className="mt-2 space-y-2">
                  {insights.map((insight) => (
                    <li key={insight.id} className="rounded-xl border border-ink-100 p-3 text-sm">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="chip bg-tide-100 text-tide-600">
                          {insight.kind === 'finding' ? 'Вывод' : 'Предложение'}
                        </span>
                        <ApprovalChip status={insight.approval} />
                      </div>
                      <h5 className="mt-2 font-semibold">{insight.title}</h5>
                      <p className="mt-1 text-ink-600">{insight.body}</p>
                      <p className="mt-2 text-xs text-ink-500">
                        Владелец: {insight.owner_role} · достоверность{' '}
                        {CONFIDENCE_LABEL[insight.confidence]}
                      </p>
                      <ul className="mt-1 text-xs text-ink-500">
                        {insight.sources.map((s, idx) => (
                          <li key={idx}>
                            → {s.document_title}: «{s.fragment}»
                          </li>
                        ))}
                      </ul>
                      {insight.approval !== 'approved' && (
                        <div className="mt-3 flex gap-2">
                          <button
                            className="rounded-lg bg-moss-500 px-3 py-1.5 text-xs font-semibold text-white"
                            onClick={async () => {
                              const next = await api.approveInsight(insight.id, 'approved')
                              setSnapshot(next)
                            }}
                          >
                            Утвердить
                          </button>
                          <button
                            className="rounded-lg bg-ink-100 px-3 py-1.5 text-xs font-semibold text-ink-700"
                            onClick={async () => {
                              const next = await api.approveInsight(insight.id, 'rejected')
                              setSnapshot(next)
                            }}
                          >
                            Отклонить
                          </button>
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </section>
        )
      })}
    </div>
  )
}
