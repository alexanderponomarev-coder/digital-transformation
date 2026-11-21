import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'

const aspects = [
  {
    title: 'Технология',
    body: 'Что существует и можно показать: каталоги, онтологии, SHACL, PROV-O, оркестрация — под контролем версий.',
  },
  {
    title: 'Ответственность',
    body: 'Кто отвечает в оргструктуре. Назначены ли владельцы данных и процессов, есть ли мандат CDO у CEO.',
  },
  {
    title: 'Применение правил',
    body: 'Срабатывает ли контроль до действия: допуск, двойное подтверждение, аудит запросом, остановка на деле.',
  },
]

const domains = [
  {
    code: 'C1–C2',
    title: 'Инфраструктура',
    focus: 'Данные и связность',
  },
  {
    code: 'C3–C8',
    title: 'Управление',
    focus: 'Онтология, контракты, происхождение',
  },
  {
    code: 'C9',
    title: 'Агенты',
    focus: 'Функции и среда исполнения',
  },
  {
    code: 'C10–C11',
    title: 'Организация',
    focus: 'Модель работы и стратегия',
  },
]

const levels = [
  { n: '1', title: 'Отсутствует' },
  { n: '2', title: 'Ситуативный' },
  { n: '3', title: 'Определён' },
  { n: '4', title: 'Действует' },
]

const modes = [
  {
    title: 'Ниже режима 1',
    body: 'Большинство аспектов на 1–2. Управляемое делегирование невозможно без мандата и допуска данных.',
  },
  {
    title: 'Режим 1 — инфраструктура',
    body: 'Инфраструктура крепка, применение правил в управлении отстаёт. Несколько агентов по контрактам CDO — да; целый процесс — ещё нет.',
  },
  {
    title: 'Режим 2 — делегирование',
    body: 'Большинство аспектов на уровне 3. Можно формально делегировать рабочий процесс и двигаться к операционной подотчётности.',
  },
]

export function LandingPage() {
  return (
    <div className="min-h-screen bg-ink-950 text-ink-50">
      <section className="relative isolate min-h-[100svh] overflow-hidden">
        <div aria-hidden className="pointer-events-none absolute inset-0">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_90%_70%_at_12%_8%,rgba(20,131,126,0.42),transparent_55%),radial-gradient(ellipse_65%_50%_at_88%_18%,rgba(217,119,6,0.2),transparent_48%),linear-gradient(180deg,#0c1210_0%,#14201c_58%,#0c1210_100%)]" />
          <div className="absolute inset-0 opacity-[0.3] [background-image:linear-gradient(rgba(255,255,255,0.06)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] [background-size:56px_56px] [mask-image:radial-gradient(ellipse_72%_58%_at_48%_42%,#000_18%,transparent_78%)]" />
          {/* Four domain strata — maturity visual */}
          <div className="absolute inset-x-0 bottom-0 top-[32%] animate-drift">
            {domains.map((_, i) => (
              <div
                key={domains[i].code}
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
            to="/app/maturity"
            className="text-sm font-semibold text-white/80 transition hover:text-white"
          >
            Открыть оценку
          </Link>
        </header>

        <div className="relative z-10 mx-auto flex max-w-6xl flex-col justify-end px-6 pb-16 pt-10 sm:pb-20 sm:pt-16 lg:min-h-[calc(100svh-5.5rem)] lg:pb-24">
          <p className="animate-rise font-display text-[clamp(3.25rem,12vw,8rem)] font-extrabold leading-[0.88] tracking-tight text-white">
            STRATUM
          </p>
          <h1 className="animate-rise mt-6 max-w-2xl text-balance text-xl font-medium leading-snug text-white/90 sm:text-2xl md:text-3xl [animation-delay:80ms]">
            Готовность к агентам измеряется самым слабым звеном
          </h1>
          <p className="animate-rise mt-4 max-w-xl text-base leading-relaxed text-white/65 sm:text-lg [animation-delay:140ms]">
            Четыре области. Три аспекта. Четыре уровня зрелости. Не средний балл —
            минимум по технологии, ответственности и применению правил решает, чем
            система действительно способна управлять.
          </p>
          <div className="animate-rise mt-9 flex flex-wrap items-center gap-3 [animation-delay:200ms]">
            <Link
              to="/app/maturity"
              className="inline-flex items-center gap-2 bg-tide-400 px-6 py-3.5 text-sm font-semibold text-ink-950 transition hover:bg-tide-500"
            >
              Пройти оценку зрелости
              <ArrowRight size={16} />
            </Link>
            <a
              href="#method"
              className="inline-flex items-center gap-2 border border-white/25 bg-white/5 px-6 py-3.5 text-sm font-semibold text-white backdrop-blur-sm transition hover:border-white/40 hover:bg-white/10"
            >
              Как устроена оценка
            </a>
          </div>
        </div>
      </section>

      <section className="border-t border-white/10 bg-ink-50 text-ink-900">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
          <h2 className="font-display text-3xl font-extrabold tracking-tight sm:text-4xl">
            Инфраструктура есть. Управления на практике — нет.
          </h2>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-ink-500 sm:text-lg">
            Типичный профиль после лет инвестиций в данные: каталоги на уровне 3–4,
            руководство понимает тему, а применение правил в области управления — на
            1–2. Именно через этот пробел агенты строят выводы и действуют.
          </p>
        </div>
      </section>

      <section id="method" className="bg-white text-ink-900">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
          <h2 className="font-display text-3xl font-extrabold tracking-tight">
            Три аспекта в каждой области
          </h2>
          <p className="mt-3 max-w-2xl text-ink-500">
            Оценивайте независимо: наличие артефакта, полномочия роли и факт, что
            контроль срабатывает до действия.
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
            Четыре области · C1–C11
          </h2>
          <p className="mt-3 max-w-2xl text-ink-500">
            Одиннадцать возможностей сгруппированы так, чтобы видеть и вертикаль
            областей, и горизонталь аспектов внутри каждой.
          </p>
          <ul className="mt-12 grid gap-x-8 gap-y-10 sm:grid-cols-2 lg:grid-cols-4">
            {domains.map((d, i) => (
              <li key={d.code} className="animate-rise" style={{ animationDelay: `${i * 70}ms` }}>
                <p className="font-display text-sm font-bold tracking-[0.18em] text-tide-600">
                  {d.code}
                </p>
                <p className="mt-2 font-display text-lg font-bold">{d.title}</p>
                <p className="mt-1 text-sm text-ink-500">{d.focus}</p>
                <div
                  className="mt-4 h-1 origin-left animate-fillbar bg-tide-500"
                  style={{ animationDelay: `${180 + i * 90}ms`, width: `${48 + i * 12}%` }}
                />
              </li>
            ))}
          </ul>

          <div className="mt-14 border-t border-ink-100 pt-10">
            <h3 className="font-display text-xl font-bold">Четыре уровня зрелости</h3>
            <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {levels.map((l) => (
                <li key={l.n} className="border-t border-ink-200 pt-3">
                  <p className="font-display text-2xl font-extrabold text-ink-900">{l.n}</p>
                  <p className="mt-1 text-sm font-semibold text-ink-700">{l.title}</p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="bg-white text-ink-900">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
          <h2 className="font-display text-3xl font-extrabold tracking-tight">
            Правило минимума, не среднего
          </h2>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-ink-500 sm:text-lg">
            Оценка области — самый низкий из трёх аспектов. Если технология на 4, а
            применение правил на 1, область остаётся на уровне «Отсутствует» /
            «Ситуативный». То же между областями задаёт уровень всей системы и
            предельный режим делегирования агентам.
          </p>
        </div>
      </section>

      <section className="border-t border-ink-100 bg-ink-50 text-ink-900">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
          <h2 className="font-display text-3xl font-extrabold tracking-tight">
            От профиля — к режиму работы
          </h2>
          <p className="mt-3 max-w-2xl text-ink-500">
            Режим — объём полномочий агентам, а не этап календарного плана. Его обычно
            ограничивает самый слабый аспект в области управления.
          </p>
          <ol className="mt-12 space-y-0">
            {modes.map((m, i) => (
              <li
                key={m.title}
                className="grid gap-4 border-t border-ink-100 py-8 md:grid-cols-[5rem_1fr] md:gap-10"
              >
                <span className="font-display text-3xl font-extrabold text-tide-500">
                  {String(i).padStart(2, '0')}
                </span>
                <div>
                  <h3 className="font-display text-xl font-bold">{m.title}</h3>
                  <p className="mt-2 max-w-2xl text-base leading-relaxed text-ink-500">
                    {m.body}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="bg-ink-900 text-white">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
          <h2 className="font-display text-3xl font-extrabold tracking-tight">
            Двенадцать оценок вместо одной
          </h2>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-white/65">
            Откройте матрицу: выберите уровень для каждого аспекта в четырёх областях.
            STRATUM покажет профиль, слабые звенья и максимально допустимый режим.
            Решение о запуске дополнительно требует классификации риска сценария.
          </p>
          <div className="mt-10 flex flex-wrap gap-3">
            <Link
              to="/app/maturity"
              className="inline-flex items-center gap-2 bg-tide-400 px-6 py-3.5 text-sm font-semibold text-ink-950 transition hover:bg-tide-500"
            >
              Открыть матрицу оценки
              <ArrowRight size={16} />
            </Link>
            <Link
              to="/app"
              className="inline-flex items-center gap-2 border border-white/25 px-6 py-3.5 text-sm font-semibold text-white transition hover:border-white/40"
            >
              Демо СеверПром
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-white/10 bg-ink-950 px-6 py-8 text-center text-xs text-white/40">
        STRATUM · методика зрелости C1–C11 · seed «СеверПром» иллюстративен · сессия в
        RAM API
      </footer>
    </div>
  )
}
