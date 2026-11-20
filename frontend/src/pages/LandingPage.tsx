import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'

const layers = [
  { n: '01', title: 'Стратегия', hint: 'аппетит к автономии' },
  { n: '02', title: 'Процессы', hint: 'точки решений' },
  { n: '03', title: 'Данные', hint: 'знания и факты' },
  { n: '04', title: 'Инструменты', hint: 'интеграции' },
  { n: '05', title: 'Надзор', hint: 'governance' },
]

const steps = [
  {
    title: 'Документы → факты',
    body: 'Загружаете регламенты, отчёты, политики. Каждый факт хранит ссылку на документ и фрагмент.',
  },
  {
    title: 'Покрытие → вопросы',
    body: 'Карта пяти слоёв показывает слепые зоны. Ниже порога система не домысливает — задаёт вопросы владельцам.',
  },
  {
    title: 'Модель → план и ROI',
    body: 'Утверждённые выводы собираются в AS-IS/TO-BE, дорожную карту и расчёт выгоды с явными допущениями.',
  },
]

export function LandingPage() {
  return (
    <div className="min-h-screen bg-ink-950 text-ink-50">
      {/* Full-bleed hero: one composition */}
      <section className="relative isolate min-h-[100svh] overflow-hidden">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0"
        >
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_90%_70%_at_15%_10%,rgba(20,131,126,0.45),transparent_55%),radial-gradient(ellipse_70%_55%_at_85%_20%,rgba(217,119,6,0.22),transparent_50%),linear-gradient(180deg,#0c1210_0%,#14201c_55%,#0c1210_100%)]" />
          <div className="absolute inset-0 opacity-[0.35] [background-image:linear-gradient(rgba(255,255,255,0.06)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] [background-size:48px_48px] [mask-image:radial-gradient(ellipse_70%_60%_at_50%_40%,#000_20%,transparent_75%)]" />
          {/* Dominant visual plane: strata bands */}
          <div className="absolute inset-x-0 bottom-0 top-[28%] animate-drift">
            {[0, 1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="absolute inset-x-[-8%] h-[18%] border-t border-white/10"
                style={{
                  top: `${i * 16}%`,
                  background: `linear-gradient(90deg, transparent, rgba(31,163,156,${0.08 + i * 0.04}), rgba(217,119,6,${0.05 + i * 0.02}), transparent)`,
                  transform: `skewY(${-2 + i * 0.4}deg)`,
                }}
              />
            ))}
          </div>
        </div>

        <header className="relative z-10 mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
          <span className="font-display text-lg font-extrabold tracking-[0.08em] text-white">
            STRATUM
          </span>
          <Link
            to="/app"
            className="text-sm font-semibold text-white/80 transition hover:text-white"
          >
            Войти в платформу
          </Link>
        </header>

        <div className="relative z-10 mx-auto flex max-w-6xl flex-col justify-end px-6 pb-16 pt-10 sm:pb-20 sm:pt-20 lg:min-h-[calc(100svh-5.5rem)] lg:pb-24">
          <p className="animate-rise font-display text-[clamp(3.25rem,12vw,8rem)] font-extrabold leading-[0.88] tracking-tight text-white">
            STRATUM
          </p>
          <h1 className="animate-rise mt-6 max-w-2xl text-balance text-xl font-medium leading-snug text-white/90 sm:text-2xl md:text-3xl [animation-delay:80ms]">
            Агентная трансформация предприятия без домыслов
          </h1>
          <p className="animate-rise mt-4 max-w-xl text-base leading-relaxed text-white/65 sm:text-lg [animation-delay:140ms]">
            От корпоративных документов — к модели, дорожной карте и ROI. Каждый
            вывод только с источником; где покрытия нет — точечный вопрос, а не
            выдумка.
          </p>
          <div className="animate-rise mt-9 flex flex-wrap items-center gap-3 [animation-delay:200ms]">
            <Link
              to="/app"
              className="inline-flex items-center gap-2 bg-tide-400 px-6 py-3.5 text-sm font-semibold text-ink-950 transition hover:bg-tide-500"
            >
              Смотреть демо СеверПром
              <ArrowRight size={16} />
            </Link>
            <a
              href="#how"
              className="inline-flex items-center gap-2 border border-white/25 bg-white/5 px-6 py-3.5 text-sm font-semibold text-white backdrop-blur-sm transition hover:border-white/40 hover:bg-white/10"
            >
              Как это работает
            </a>
          </div>
        </div>
      </section>

      <section className="border-t border-white/10 bg-ink-50 text-ink-900">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
          <h2 className="font-display text-3xl font-extrabold tracking-tight sm:text-4xl">
            Документы есть. Управляемой модели — нет.
          </h2>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-ink-500 sm:text-lg">
            Регламенты, KPI и политики лежат в разрозненных файлах. STRATUM
            собирает из них доказательную картину готовности к агентам: что
            закрыто, где дыры, что можно автоматизировать под регуляторику РФ.
          </p>
        </div>
      </section>

      <section id="how" className="bg-white text-ink-900">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
          <h2 className="font-display text-3xl font-extrabold tracking-tight">
            Три шага до дорожной карты
          </h2>
          <p className="mt-3 max-w-xl text-ink-500">
            Один поток: от загрузки корпуса до утверждённого плана изменений.
          </p>
          <ol className="mt-12 space-y-0">
            {steps.map((step, i) => (
              <li
                key={step.title}
                className="grid gap-4 border-t border-ink-100 py-8 md:grid-cols-[5rem_1fr] md:gap-10"
              >
                <span className="font-display text-3xl font-extrabold text-tide-500">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <div>
                  <h3 className="font-display text-xl font-bold">{step.title}</h3>
                  <p className="mt-2 max-w-2xl text-base leading-relaxed text-ink-500">
                    {step.body}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section id="method" className="border-t border-ink-100 bg-ink-50 text-ink-900">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
          <h2 className="font-display text-3xl font-extrabold tracking-tight">
            Пять слоёв методологии
          </h2>
          <p className="mt-3 max-w-xl text-ink-500">
            Автономия агента растёт только вместе с доказанной управляемостью.
          </p>
          <ul className="mt-12 grid gap-x-8 gap-y-10 sm:grid-cols-2 lg:grid-cols-5">
            {layers.map((layer, i) => (
              <li key={layer.n} className="animate-rise" style={{ animationDelay: `${i * 70}ms` }}>
                <p className="font-display text-sm font-bold tracking-[0.2em] text-tide-600">
                  {layer.n}
                </p>
                <p className="mt-2 font-display text-lg font-bold">{layer.title}</p>
                <p className="mt-1 text-sm text-ink-500">{layer.hint}</p>
                <div
                  className="mt-4 h-1 origin-left animate-fillbar bg-tide-500"
                  style={{ animationDelay: `${200 + i * 90}ms`, width: `${55 + i * 8}%` }}
                />
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="bg-ink-900 text-white">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
          <h2 className="font-display text-3xl font-extrabold tracking-tight">
            Регуляторика внутри контура, не в конце
          </h2>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-white/65">
            152-ФЗ, HITL на денежных решениях, локализация моделей, запрет
            облачного ИИ на чувствительные данные — кейсы отсекаются фильтром
            до попадания в исполнительную дорожную карту.
          </p>
          <div className="mt-10 flex flex-wrap gap-3">
            <Link
              to="/app"
              className="inline-flex items-center gap-2 bg-tide-400 px-6 py-3.5 text-sm font-semibold text-ink-950 transition hover:bg-tide-500"
            >
              Открыть демо
              <ArrowRight size={16} />
            </Link>
            <Link
              to="/app/regulatory"
              className="inline-flex items-center gap-2 border border-white/25 px-6 py-3.5 text-sm font-semibold text-white transition hover:border-white/40"
            >
              Регуляторный фильтр
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-white/10 bg-ink-950 px-6 py-8 text-center text-xs text-white/40">
        STRATUM · seed «СеверПром» — демонстрационный корпус · состояние сессии в
        RAM API (без БД)
      </footer>
    </div>
  )
}
