import { Link } from 'react-router-dom'
import { ArrowRight, Layers3, ShieldCheck, FileSearch } from 'lucide-react'

const layers = [
  'Стратегия и аппетит к автономии',
  'Процессы и точки решений',
  'Данные и знания',
  'Инструменты и интеграции',
  'Управление и надзор',
]

export function LandingPage() {
  return (
    <div className="min-h-screen bg-mesh text-ink-900">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="font-display text-2xl font-extrabold tracking-tight">
          STRATUM
        </div>
        <Link
          to="/app"
          className="rounded-xl bg-ink-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-ink-800"
        >
          Открыть платформу
        </Link>
      </header>

      <main className="relative mx-auto grid max-w-6xl gap-10 px-6 pb-20 pt-8 lg:grid-cols-[1.05fr_0.95fr] lg:items-end lg:pt-16">
        <section className="animate-rise">
          <p className="mb-4 font-display text-5xl font-extrabold leading-[0.95] tracking-tight text-ink-900 sm:text-6xl md:text-7xl">
            STRATUM
          </p>
          <h1 className="max-w-xl text-balance text-xl font-medium text-ink-700 sm:text-2xl">
            Платформа агентной трансформации предприятия: от корпоративных
            документов — к модели, плану и ROI без домыслов.
          </h1>
          <p className="mt-5 max-w-lg text-base leading-relaxed text-ink-500">
            Загружаете документы. Система классифицирует их по пяти слоям
            методологии, показывает слепые зоны и задаёт точечные вопросы —
            а не выдумывает факты.
          </p>
          <p className="mt-3 max-w-lg text-sm leading-relaxed text-ink-400">
            Seed «СеверПром» — демонстрационный корпус. Состояние сессии
            хранится только в памяти API (без БД и бэкапа).
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link
              to="/app"
              className="inline-flex items-center gap-2 rounded-xl bg-tide-500 px-5 py-3 text-sm font-semibold text-white shadow-soft transition hover:bg-tide-600"
            >
              Смотреть демо СеверПром
              <ArrowRight size={16} />
            </Link>
            <a
              href="#method"
              className="inline-flex items-center gap-2 rounded-xl border border-ink-100 bg-white/70 px-5 py-3 text-sm font-semibold text-ink-800"
            >
              Методология
            </a>
          </div>
        </section>

        <section
          aria-hidden
          className="relative min-h-[320px] animate-rise overflow-hidden rounded-[28px] border border-ink-100 bg-ink-900 shadow-soft [animation-delay:120ms]"
        >
          <div className="absolute inset-0 bg-[linear-gradient(145deg,rgba(31,163,156,0.35),transparent_45%),linear-gradient(330deg,rgba(217,119,6,0.25),transparent_40%)]" />
          <div className="absolute inset-0 opacity-40 [background-image:linear-gradient(rgba(255,255,255,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.08)_1px,transparent_1px)] [background-size:28px_28px]" />
          <div className="relative flex h-full flex-col justify-between p-6 sm:p-8">
            <div className="animate-drift">
              <p className="text-xs uppercase tracking-[0.22em] text-tide-100/80">
                Five layers
              </p>
              <ul className="mt-4 space-y-2">
                {layers.map((label, i) => (
                  <li
                    key={label}
                    className="flex items-center gap-3 text-sm text-white/90"
                    style={{ animationDelay: `${i * 80}ms` }}
                  >
                    <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-white/10 font-display text-xs font-bold">
                      {i + 1}
                    </span>
                    {label}
                  </li>
                ))}
              </ul>
            </div>
            <p className="max-w-sm text-sm leading-relaxed text-white/70">
              Автономия агента растёт только вместе с доказанной управляемостью
              и соответствием регуляторике РФ.
            </p>
          </div>
        </section>
      </main>

      <section id="method" className="border-t border-ink-100/80 bg-white/50">
        <div className="mx-auto grid max-w-6xl gap-6 px-6 py-16 md:grid-cols-3">
          {[
            {
              icon: FileSearch,
              title: 'Атрибуция источника',
              body: 'Каждый факт и вывод хранит ссылку: документ + фрагмент. Нет источника — нет вывода.',
            },
            {
              icon: Layers3,
              title: 'Карта покрытия',
              body: 'Матрица слоёв показывает закрытые зоны и слепые пятна. Ниже порога — только вопросы.',
            },
            {
              icon: ShieldCheck,
              title: 'Регуляторный фильтр',
              body: '152-ФЗ, HITL, локализация моделей, запрет облачных ИИ на чувствительные данные.',
            },
          ].map((item, i) => (
            <article
              key={item.title}
              className="animate-rise rounded-2xl border border-ink-100 bg-white/80 p-6"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <item.icon className="mb-4 text-tide-500" size={22} />
              <h2 className="font-display text-lg font-bold text-ink-900">{item.title}</h2>
              <p className="mt-2 text-sm leading-relaxed text-ink-500">{item.body}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}
