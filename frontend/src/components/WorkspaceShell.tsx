import { NavLink, Outlet } from 'react-router-dom'
import {
  LayoutDashboard,
  Files,
  Grid3X3,
  MessageSquareQuote,
  Waypoints,
  Route,
  LineChart,
  ShieldAlert,
  Layers3,
  Gauge,
} from 'lucide-react'
import { usePlatform } from '../context/PlatformContext'
import { pct } from '../lib/labels'

const links = [
  { to: '/app', end: true, label: 'Обзор', icon: LayoutDashboard },
  { to: '/app/documents', label: 'Документы', icon: Files },
  { to: '/app/coverage', label: 'Покрытие', icon: Grid3X3 },
  { to: '/app/methodology', label: 'Методология', icon: Layers3 },
  { to: '/app/maturity', label: 'Зрелость', icon: Gauge },
  { to: '/app/questions', label: 'Вопросы', icon: MessageSquareQuote },
  { to: '/app/model', label: 'Модель', icon: Waypoints },
  { to: '/app/roadmap', label: 'План и ROI', icon: Route },
  { to: '/app/regulatory', label: 'Регуляторика', icon: ShieldAlert },
]

export function WorkspaceShell() {
  const { snapshot, loading, error } = usePlatform()

  return (
    <div className="min-h-screen bg-mesh lg:grid lg:grid-cols-[240px_1fr]">
      <aside className="border-b border-ink-100 bg-white/80 px-4 py-5 backdrop-blur lg:border-b-0 lg:border-r">
        <div className="mb-6 px-2">
          <div className="font-display text-xl font-extrabold tracking-tight">STRATUM</div>
          <p className="mt-1 text-xs text-ink-500">Agentic Enterprise Platform</p>
        </div>
        <nav className="flex gap-1 overflow-x-auto pb-2 lg:flex-col lg:overflow-visible lg:pb-0">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                `nav-link whitespace-nowrap ${isActive ? 'nav-link-active' : ''}`
              }
            >
              <link.icon size={16} />
              {link.label}
            </NavLink>
          ))}
        </nav>
        {snapshot && (
          <div className="mt-6 hidden rounded-2xl bg-ink-900 p-4 text-white lg:block">
            <p className="text-xs uppercase tracking-[0.18em] text-white/50">Покрытие</p>
            <p className="mt-2 font-display text-3xl font-bold">
              {pct(snapshot.overview.overall_coverage)}
            </p>
            <p className="mt-1 text-xs text-white/60">
              {snapshot.overview.open_questions_count} открытых вопросов
            </p>
            <div className="mt-3 flex items-center gap-2 text-xs text-white/70">
              <LineChart size={14} />
              ROI payback {snapshot.roi.payback_months} мес
            </div>
          </div>
        )}
      </aside>

      <div className="min-w-0">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-ink-100 bg-white/60 px-5 py-4 backdrop-blur">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-tide-600">
              {snapshot?.overview.version ?? 'MVP'}
              {snapshot?.overview.deploy_mode ? (
                <span className="ml-2 tracking-normal text-ink-400">
                  · {snapshot.overview.deploy_mode === 'demo' ? 'demo-стенд' : 'lab'}
                </span>
              ) : null}
            </p>
            <h1 className="font-display text-xl font-bold text-ink-900">
              {snapshot?.overview.project_name ?? 'Загрузка…'}
            </h1>
          </div>
          <div className="text-right text-sm text-ink-500">
            <div>{snapshot?.overview.company_name}</div>
            <div className="text-xs">{snapshot?.overview.industry}</div>
          </div>
        </header>

        {snapshot?.overview.storage_disclaimer ? (
          <div
            role="note"
            className="border-b border-amber-200/80 bg-amber-50/90 px-5 py-2 text-xs leading-relaxed text-ink-700"
          >
            {snapshot.overview.storage_disclaimer}
          </div>
        ) : null}

        <main className="px-5 py-6">
          {loading && !snapshot && (
            <div className="panel p-8 text-sm text-ink-500">Загружаем модель предприятия…</div>
          )}
          {error && (
            <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              {error}
              <div className="mt-1 text-xs text-red-600/80">
                Убедитесь, что API запущен на :8000
              </div>
            </div>
          )}
          {snapshot && <Outlet />}
        </main>
      </div>
    </div>
  )
}
