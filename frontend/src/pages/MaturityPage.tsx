import { useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'
import { usePlatform } from '../context/PlatformContext'
import type {
  MaturityAspectId,
  MaturityCell,
  MaturityDomainId,
  MaturityMatrix,
} from '../types'

const LEVEL_TONE: Record<number, string> = {
  1: 'border-ink-200 bg-ink-50 text-ink-500',
  2: 'border-ember-500/30 bg-ember-100 text-ember-600',
  3: 'border-tide-500/30 bg-tide-100 text-tide-600',
  4: 'border-moss-500/40 bg-moss-100 text-moss-600',
}

export function MaturityPage() {
  const { snapshot, setSnapshot } = usePlatform()
  const [matrix, setMatrix] = useState<MaturityMatrix | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    void api
      .maturityMatrix()
      .then(setMatrix)
      .catch((err: Error) => setError(err.message))
  }, [])

  const assessment = snapshot?.maturity
  const scoreMap = useMemo(() => {
    const m = new Map<string, number>()
    for (const s of assessment?.scores ?? []) {
      m.set(`${s.domain_id}:${s.aspect_id}`, s.level)
    }
    return m
  }, [assessment])

  const cellText = (domain: MaturityDomainId, aspect: MaturityAspectId, level: number) => {
    const cell = matrix?.cells.find(
      (c: MaturityCell) =>
        c.domain_id === domain && c.aspect_id === aspect && c.level === level,
    )
    return cell?.description ?? ''
  }

  const setLevel = async (
    domain_id: MaturityDomainId,
    aspect_id: MaturityAspectId,
    level: number,
  ) => {
    setSaving(true)
    setError(null)
    try {
      const snap = await api.updateMaturityScores([{ domain_id, aspect_id, level }])
      setSnapshot(snap)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось сохранить оценку')
    } finally {
      setSaving(false)
    }
  }

  if (!snapshot) return null

  return (
    <div className="space-y-8">
      <div>
        <h2 className="font-display text-2xl font-bold">Оценка зрелости</h2>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-ink-500">
          Одиннадцать возможностей в четырёх областях. В каждой области независимо
          оцениваются технология, ответственность и применение правил (уровни 1–4).
          Оценка области — минимум из трёх аспектов, не среднее.
        </p>
      </div>

      {assessment && (
        <section className="border border-ink-100 bg-white/80 p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-tide-600">
            Профиль · уровень системы {assessment.system_level}
          </p>
          <h3 className="mt-2 font-display text-xl font-bold text-ink-900">
            {assessment.mode_label}
          </h3>
          <p className="mt-3 max-w-3xl text-sm leading-relaxed text-ink-600">
            {assessment.next_step}
          </p>
          <p className="mt-3 text-xs leading-relaxed text-ink-400">
            {assessment.profile_summary}
          </p>
          {assessment.notes ? (
            <p className="mt-2 text-xs text-ink-400">{assessment.notes}</p>
          ) : null}
          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {assessment.domain_results.map((d) => (
              <div key={d.domain_id} className="border border-ink-100 p-3">
                <p className="text-xs uppercase tracking-[0.12em] text-ink-400">{d.title}</p>
                <p className="mt-1 font-display text-3xl font-bold text-ink-900">
                  {d.domain_level}
                </p>
                <p className="mt-1 text-xs text-ink-500">
                  слабее: {d.weakest_aspect}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {error && (
        <div className="border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {matrix?.aspects && (
        <section className="space-y-3">
          <h3 className="font-display text-lg font-bold">Три аспекта</h3>
          <ul className="grid gap-4 md:grid-cols-3">
            {matrix.aspects.map((a) => (
              <li key={a.id} className="border-t border-ink-100 pt-3">
                <p className="font-display font-bold">{a.title}</p>
                <p className="mt-1 text-sm leading-relaxed text-ink-500">{a.description}</p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {matrix &&
        matrix.domains.map((domain) => (
          <section key={domain.id} className="space-y-4">
            <div>
              <h3 className="font-display text-xl font-bold">
                {domain.title}
                <span className="ml-2 text-sm font-semibold text-tide-600">
                  {domain.capabilities}
                </span>
              </h3>
              <p className="mt-1 text-sm text-ink-500">{domain.focus}</p>
            </div>

            {matrix.aspects.map((aspect) => {
              const current = scoreMap.get(`${domain.id}:${aspect.id}`) ?? 1
              return (
                <div key={`${domain.id}-${aspect.id}`} className="border border-ink-100 bg-white/70">
                  <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-ink-100 px-4 py-3">
                    <p className="font-display font-bold">{aspect.title}</p>
                    <p className="text-xs text-ink-400">
                      выбрано: {current} — {matrix.levels.find((l) => l.level === current)?.title}
                      {saving ? ' · сохранение…' : ''}
                    </p>
                  </div>
                  <div className="grid gap-0 md:grid-cols-4">
                    {[1, 2, 3, 4].map((level) => {
                      const selected = current === level
                      return (
                        <button
                          key={level}
                          type="button"
                          disabled={saving}
                          onClick={() => void setLevel(domain.id, aspect.id, level)}
                          className={`border-t border-ink-100 p-3 text-left transition md:border-t-0 md:border-l first:border-l-0 ${
                            selected
                              ? LEVEL_TONE[level]
                              : 'bg-transparent text-ink-600 hover:bg-ink-50'
                          }`}
                        >
                          <p className="text-xs font-semibold uppercase tracking-[0.12em]">
                            {level} — {matrix.levels.find((l) => l.level === level)?.title}
                          </p>
                          <p className="mt-2 text-xs leading-relaxed opacity-90">
                            {cellText(domain.id, aspect.id, level)}
                          </p>
                        </button>
                      )
                    })}
                  </div>
                </div>
              )
            })}
          </section>
        ))}

      <section className="border-t border-ink-100 pt-6 text-sm text-ink-500">
        <p className="font-display font-bold text-ink-800">Как читать результат</p>
        <p className="mt-2 max-w-3xl leading-relaxed">
          {matrix?.rule ??
            'Важен не средний балл, а самый низкий по аспектам каждой области. Предельный режим обычно определяет самый слабый аспект в области управления.'}
        </p>
        <p className="mt-3 max-w-3xl leading-relaxed">
          Решение о запуске — ещё и классификация риска сценария. Эта методика оценивает
          готовность, но не задаёт допустимый уровень риска совета директоров.
        </p>
      </section>
    </div>
  )
}
