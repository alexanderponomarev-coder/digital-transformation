import { useState, type FormEvent } from 'react'
import { usePlatform } from '../context/PlatformContext'
import { api } from '../lib/api'
import { LAYER_LABEL } from '../lib/labels'

export function QuestionsPage() {
  const { snapshot, setSnapshot } = usePlatform()
  const [drafts, setDrafts] = useState<Record<string, string>>({})
  const [busyId, setBusyId] = useState<string | null>(null)

  if (!snapshot) return null

  async function submit(e: FormEvent, id: string) {
    e.preventDefault()
    const answer = drafts[id]?.trim()
    if (!answer) return
    setBusyId(id)
    try {
      const next = await api.answerQuestion(id, answer)
      setSnapshot(next)
      setDrafts((prev) => ({ ...prev, [id]: '' }))
    } finally {
      setBusyId(null)
    }
  }

  const open = snapshot.questions.filter((q) => q.status === 'open')
  const answered = snapshot.questions.filter((q) => q.status === 'answered')

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Вопросы и уточнения</h2>
        <p className="mt-1 max-w-2xl text-sm text-ink-500">
          Где данных нет — система не достраивает картину. Ответы фиксируются как источник наравне с
          документами.
        </p>
      </div>

      <section className="space-y-3">
        <h3 className="text-sm font-semibold uppercase tracking-[0.14em] text-ink-500">
          Открытые ({open.length})
        </h3>
        {open.map((q) => (
          <article key={q.id} className="panel p-5">
            <div className="flex flex-wrap gap-2">
              <span className="chip bg-tide-100 text-tide-600">{LAYER_LABEL[q.layer_id]}</span>
              <span className="chip bg-ink-100 text-ink-700">{q.to_role}</span>
            </div>
            <h4 className="mt-3 font-semibold text-ink-900">{q.question}</h4>
            <p className="mt-1 text-sm text-ink-500">{q.why}</p>
            <form className="mt-4 flex flex-col gap-2 sm:flex-row" onSubmit={(e) => submit(e, q.id)}>
              <input
                className="flex-1 rounded-xl border border-ink-100 px-3 py-2 text-sm outline-none ring-tide-400 focus:ring-2"
                placeholder="Ответ ответственного…"
                value={drafts[q.id] ?? ''}
                onChange={(e) => setDrafts((prev) => ({ ...prev, [q.id]: e.target.value }))}
              />
              <button
                type="submit"
                disabled={busyId === q.id}
                className="rounded-xl bg-ink-900 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
              >
                {busyId === q.id ? 'Сохраняем…' : 'Зафиксировать ответ'}
              </button>
            </form>
          </article>
        ))}
      </section>

      <section className="space-y-3">
        <h3 className="text-sm font-semibold uppercase tracking-[0.14em] text-ink-500">
          Отвеченные ({answered.length})
        </h3>
        {answered.map((q) => (
          <article key={q.id} className="rounded-2xl border border-moss-100 bg-moss-100/40 p-4">
            <p className="text-sm font-medium">{q.question}</p>
            <p className="mt-2 text-sm text-ink-700">{q.answer}</p>
            <p className="mt-1 text-xs text-ink-500">
              {q.to_role} · {q.answered_at} · источник answer:{q.id}
            </p>
          </article>
        ))}
      </section>
    </div>
  )
}
