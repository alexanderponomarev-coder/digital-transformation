import type { ApprovalStatus, CoverageStatus } from '../types'
import { APPROVAL_LABEL, COVERAGE_LABEL } from '../lib/labels'

const coverageClass: Record<CoverageStatus, string> = {
  closed: 'bg-moss-100 text-moss-600',
  partial: 'bg-ember-100 text-ember-600',
  missing: 'bg-ink-100 text-ink-700',
}

const approvalClass: Record<ApprovalStatus, string> = {
  approved: 'bg-moss-100 text-moss-600',
  pending: 'bg-ember-100 text-ember-600',
  hypothesis: 'bg-ink-100 text-ink-700',
  draft: 'bg-ink-100 text-ink-500',
  rejected: 'bg-red-100 text-red-700',
}

export function CoverageChip({ status }: { status: CoverageStatus }) {
  return <span className={`chip ${coverageClass[status]}`}>{COVERAGE_LABEL[status]}</span>
}

export function ApprovalChip({ status }: { status: ApprovalStatus }) {
  return <span className={`chip ${approvalClass[status]}`}>{APPROVAL_LABEL[status]}</span>
}

export function RegChip({ status }: { status: 'pass' | 'warn' | 'block' }) {
  const map = {
    pass: 'bg-moss-100 text-moss-600',
    warn: 'bg-ember-100 text-ember-600',
    block: 'bg-red-100 text-red-700',
  }
  const label = { pass: 'OK', warn: 'Внимание', block: 'Блок' }
  return <span className={`chip ${map[status]}`}>{label[status]}</span>
}
