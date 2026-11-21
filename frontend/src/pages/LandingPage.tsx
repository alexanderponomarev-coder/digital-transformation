import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'

const aspects = [
  {
    title: 'Технология',
    body: 'Есть ли то, что можно открыть и проверить: каталог данных, правила, журнал действий, среда запуска агентов — не слайд, а рабочий артефакт.',
  },
  {
    title: 'Ответственность',
    body: 'Назначены ли владельцы данных и процессов, есть ли офис CDO с мандатом у генерального директора — роль существует и наделена полномочиями.',
  },
  {
    title: 'Применение правил',
    body: 'Срабатывает ли контроль до действия: двойной допуск, фиксируемое подтверждение, проверяемый аудит и реальная остановка при нарушении.',
  },
]

const domains = [
  {
    code: 'C1–C2',
    title: 'Инфраструктура',
    focus: 'Данные связаны, каталогизированы, происхождение прослеживается',
  },
  {
    code: 'C3–C8',
    title: 'Управление',
    focus: 'Смысл данных, ограничения, контракты и цепочка аудита',
  },
  {
    code: 'C9',
    title: 'Агенты',
    focus: 'Реестр, оркестрация, мониторинг и допуск к запуску',
  },
  {
    code: 'C10–C11',
    title: 'Организация',
    focus: 'Модель работы, надзор совета и должная осмотрительность',
  },
]

const modes = [
  {
    title: 'Пока нельзя делегировать',
    body: 'Оценка в основном на уровнях «нет» или «только пилоты». Сначала мандат CDO, владельцы данных и процедура допуска.',
  },
  {
    title: 'Можно точечных агентов',
    body: 'Инфраструктура сильная, а контроль в управлении ещё слабый. Допустимы отдельные агенты по контрактам CDO — не целый процесс.',
  },
  {
    title: 'Можно делегировать процесс',
    body: 'Большинство аспектов формально определены. Организация готова передать рабочий процесс под контролем и идти к полной подотчётности.',
  },
]

export function LandingPage() {
  return (
    <div className="min-h-screen bg-ink-950 text-ink-50">
      <section className="relative isolate min-h-[100svh] overflow-hidden">
        <div aria-hidden className="pointer-events-none absolute inset-0">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_90%_70%_at_12%_8%,rgba(20,131,126,0.42),transparent_55%),radial-gradient(ellipse_65%_50%_at_88%_18%,rgba(217,119,6,0.18),transparent_48%),linear-gradient(180deg,#0c1210_0%,#14201c_58%,#0c1210_100%)]" />
          <div className="absolute inset-0 opacity-[0.28] [background-image:linear-gradient(rgba(255,255,255,0.06)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] [background-size:56px_56px] [mask-image:radial-gradient(ellipse_72%_58%_at_48%_42%,#000_18%,transparent_78%)]" />
          <div className="absolute inset-x-0 bottom-0 top-[34%] animate-drift">
            {domains.map((d, i) => (
              <div
                key={d.code}
                className="absolute inset-x-[-10%] h-[20%] border-t border-white/10"
                style={{
                  top: `${i * 18}%`,
                  background: `linear-gradient(90deg, transparent, rgba(31,163,156,${0.1 + i * 0.05}), rgba(217,119,6,${0.04 + i * 0.02}), transparent)`,
                  transform: `skewY(${-1.6 + i * 0.35}deg)`,
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
            Платформа
          </Link>
        </header>

        <div className="relative z-10 mx-auto flex max-w-6xl flex-col justify-end px-6 pb-16 pt-10 sm:pb-20 sm:pt-16 lg:min-h-[calc(100svh-5.5rem)] lg:pb-24">
          <p className="animate-rise font-display text-[clamp(3.25rem,12vw,8rem)] font-extrabold leading-[0.88] tracking-tight text-white">
            STRATUM
          </p>
          <h1 className="animate-rise mt-6 max-w-2xl text-balance text-xl font-medium leading-snug text-white/90 sm:text-2xl md:text-3xl [animation-delay:80ms]">
            Сколько автономии агентам можно отдать — без потери контроля
          </h1>
          <p className="animate-rise mt-4 max-w-xl text-base leading-relaxed text-white/65 sm:text-lg [animation-delay:140ms]">
            Платформа для CDO и руководства: оценка зрелости по четырём областям
            показывает слабое звено и допустимый режим работы — до масштабирования
            ИИ-агентов на процессы.
          </p>
          <div className="animate-rise mt-9 flex flex-wrap items-center gap-3 [animation-delay:200ms]">
            <Link
              to="/app/maturity"
              className="inline-flex items-center gap-2 bg-tide-400 px-6 py-3.5 text-sm font-semibold text-ink-950 transition hover:bg-tide-500"
            >
              Узнать допустимый режим
              <ArrowRight size={16} />
            </Link>
            <a
              href="#method"
              className="inline-flex items-center gap-2 border border-white/25 bg-white/5 px-6 py-3.5 text-sm font-semibold text-white backdrop-blur-sm transition hover:border-white/40 hover:bg-white/10"
            >
              Как считается оценка
            </a>
          </div>
        </div>
      </section>

      <section className="border-t border-white/10 bg-ink-50 text-ink-900">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
          <h2 className="font-display text-3xl font-extrabold tracking-tight sm:text-4xl">
            Данные в порядке. Контроля за агентами — нет.
          </h2>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-ink-500 sm:text-lg">
            После лет вложений в аналитику часто так: каталоги и платформы сильные,
            а правила на практике не срабатывают. Агенты действуют как раз через этот
            разрыв — STRATUM делает его видимым до запуска.
          </p>
        </div>
      </section>

      <section id="method" className="bg-white text-ink-900">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
          <h2 className="font-display text-3xl font-extrabold tracking-tight">
            Три вопроса в каждой области
          </h2>
          <p className="mt-3 max-w-2xl text-ink-500">
            Не один балл «цифровой зрелости», а двенадцать оценок: есть ли средство,
            кто отвечает, и работает ли правило в бою.
          </p>
          <ol className="mt-12 space-y-0">
            {aspects.map((item, i) => (
              <li
                key={item.title}
                className="grid gap-4 border-t border-ink-100 py-8 md:grid-cols-[5rem_1fr] md:gap-10"
              >
                <span className="font-display text-3xl font-extrabold text-tide-500">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <div>
                  <h3 className="font-display text-xl font-bold">{item.title}</h3>
                  <p className="mt-2 max-w-2xl text-base leading-relaxed text-ink-500">
                    {item.body}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="border-t border-ink-100 bg-ink-50 text-ink-900">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
          <h2 className="font-display text-3xl font-extrabold tracking-tight">
            Четыре области готовности
          </h2>
          <p className="mt-3 max-w-2xl text-ink-500">
            Инфраструктура, управление, агенты и организация. Уровень области —
            минимум из трёх ответов выше, не среднее арифметическое.
          </p>
          <ul className="mt-12 grid gap-x-10 gap-y-12 sm:grid-cols-2">
            {domains.map((d, i) => (
              <li key={d.code} className="animate-rise border-t border-ink-200 pt-5" style={{ animationDelay: `${i * 70}ms` }}>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-tide-600">
                  {d.code}
                </p>
                <p className="mt-2 font-display text-xl font-bold">{d.title}</p>
                <p className="mt-2 text-sm leading-relaxed text-ink-500">{d.focus}</p>
                <div
                  className="mt-5 h-1 origin-left animate-fillbar bg-tide-500"
                  style={{ animationDelay: `${160 + i * 80}ms`, width: `${52 + i * 10}%` }}
                />
              </li>
            ))}
          </ul>
          <p className="mt-12 max-w-2xl text-sm leading-relaxed text-ink-500">
            Шкала в каждой ячейке: отсутствует → ситуативный → определён → действует.
            Самое слабое звено между областями задаёт потолок системы целиком.
          </p>
        </div>
      </section>

      <section className="bg-ink-900 text-white">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
          <h2 className="font-display text-3xl font-extrabold tracking-tight">
            Результат — режим, а не «средний балл»
          </h2>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-white/65">
            По профилю видно, какой объём полномочий агентам можно отдать ответственно.
            Обычно предел ставит управление: нельзя делегировать больше, чем
            контролируете на практике.
          </p>
          <ol className="mt-12 space-y-0">
            {modes.map((m) => (
              <li key={m.title} className="border-t border-white/15 py-8">
                <h3 className="font-display text-xl font-bold">{m.title}</h3>
                <p className="mt-2 max-w-2xl text-base leading-relaxed text-white/60">
                  {m.body}
                </p>
              </li>
            ))}
          </ol>
          <div className="mt-10 flex flex-wrap gap-3">
            <Link
              to="/app/maturity"
              className="inline-flex items-center gap-2 bg-tide-400 px-6 py-3.5 text-sm font-semibold text-ink-950 transition hover:bg-tide-500"
            >
              Открыть матрицу в STRATUM
              <ArrowRight size={16} />
            </Link>
            <Link
              to="/app"
              className="inline-flex items-center gap-2 border border-white/25 px-6 py-3.5 text-sm font-semibold text-white transition hover:border-white/40"
            >
              Смотреть платформу
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-white/10 bg-ink-950 px-6 py-8 text-center text-xs text-white/40">
        STRATUM · для CDO, CIO и руководства · оценка готовности к агентному управлению
      </footer>
    </div>
  )
}
