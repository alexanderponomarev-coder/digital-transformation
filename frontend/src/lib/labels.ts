import type { ApprovalStatus, Confidence, CoverageStatus, LayerId } from '../types'

export const LAYER_LABEL: Record<LayerId, string> = {
  strategy: 'Стратегия',
  processes: 'Процессы',
  data: 'Данные',
  tools: 'Инструменты',
  governance: 'Надзор',
}

export const COVERAGE_LABEL: Record<CoverageStatus, string> = {
  closed: 'Закрыт',
  partial: 'Частично',
  missing: 'Нет данных',
}

export const CONFIDENCE_LABEL: Record<Confidence, string> = {
  high: 'Высокая',
  medium: 'Средняя',
  low: 'Низкая',
  none: 'Нет',
}

export const APPROVAL_LABEL: Record<ApprovalStatus, string> = {
  draft: 'Черновик',
  hypothesis: 'Гипотеза',
  pending: 'На утверждении',
  approved: 'Утверждено',
  rejected: 'Отклонено',
}

export function pct(value: number): string {
  return `${Math.round(value * 100)}%`
}
