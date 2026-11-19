import { useState, type FormEvent } from 'react'
import { usePlatform } from '../context/PlatformContext'
import { api } from '../lib/api'
import { LAYER_LABEL } from '../lib/labels'

export function DocumentsPage() {
  const { snapshot, refresh, setSnapshot } = usePlatform()
  const [title, setTitle] = useState('')
  const [summary, setSummary] = useState('')
  const [format, setFormat] = useState('pdf')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState<string | null>(null)

  if (!snapshot) return null

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (!title.trim()) return
    setBusy(true)
    setMessage(null)
    try {
      const result = await api.uploadDocument({
        title: title.trim(),
        format,
        summary: summary.trim(),
        content_hint: summary.trim(),
      })
      setMessage(result.message)
      setTitle('')
      setSummary('')
      await refresh()
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Ошибка загрузки')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
      <form onSubmit={onSubmit} className="panel space-y-4 p-5">
        <div>
          <h2 className="font-display text-lg font-bold">Приём документов</h2>
          <p className="mt-1 text-sm text-ink-500">
            PDF, DOCX, XLSX, PPTX. Классификация по слоям методологии; факты только из текста.
          </p>
        </div>
        <label className="block text-sm">
          <span className="mb-1 block font-medium">Название</span>
          <input
            className="w-full rounded-xl border border-ink-100 bg-white px-3 py-2 outline-none ring-tide-400 focus:ring-2"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Например: Политика качества данных"
          />
        </label>
        <label className="block text-sm">
          <span className="mb-1 block font-medium">Формат</span>
          <select
            className="w-full rounded-xl border border-ink-100 bg-white px-3 py-2"
            value={format}
            onChange={(e) => setFormat(e.target.value)}
          >
            {['pdf', 'docx', 'xlsx', 'pptx', 'link'].map((f) => (
              <option key={f} value={f}>
                {f.toUpperCase()}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="mb-1 block font-medium">Краткое содержание / фрагмент</span>
          <textarea
            className="min-h-28 w-full rounded-xl border border-ink-100 bg-white px-3 py-2 outline-none ring-tide-400 focus:ring-2"
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            placeholder="Вставьте ключевые формулировки: процессы, данные, API, риски…"
          />
        </label>
        <button
          type="submit"
          disabled={busy}
          className="rounded-xl bg-tide-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-tide-600 disabled:opacity-60"
        >
          {busy ? 'Классифицируем…' : 'Загрузить и классифицировать'}
        </button>
        {message && <p className="text-sm text-ink-600">{message}</p>}
        <button
          type="button"
          className="text-xs font-medium text-ink-500 underline"
          onClick={async () => {
            const snap = await api.reset()
            setSnapshot(snap)
          }}
        >
          Сбросить демо-данные
        </button>
      </form>

      <div className="space-y-3">
        {snapshot.documents.map((doc) => (
          <article key={doc.id} className="panel p-4">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <h3 className="font-semibold text-ink-900">{doc.title}</h3>
                <p className="mt-1 text-xs text-ink-500">
                  {doc.format.toUpperCase()} · v{doc.version} · {doc.uploaded_at} · свежесть{' '}
                  {doc.freshness_days} дн · {doc.size_label}
                </p>
              </div>
              <div className="flex flex-wrap gap-1">
                {doc.layers.map((layer) => (
                  <span key={layer} className="chip bg-tide-100 text-tide-600">
                    {LAYER_LABEL[layer]}
                  </span>
                ))}
              </div>
            </div>
            <p className="mt-3 text-sm leading-relaxed text-ink-600">{doc.summary}</p>
            {doc.replaces_id && (
              <p className="mt-2 text-xs text-ember-600">
                Версия заменяет документ {doc.replaces_id}
              </p>
            )}
          </article>
        ))}
      </div>
    </div>
  )
}
