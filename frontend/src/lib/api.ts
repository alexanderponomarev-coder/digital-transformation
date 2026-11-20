import type { ClassifyResult, Opportunity, PlatformSnapshot, RoiModel } from '../types'

const BASE = '/api'

function readStore(key: string): string {
  try {
    return sessionStorage.getItem(key) || ''
  } catch {
    return ''
  }
}

function authHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  const token =
    (import.meta.env.VITE_STRATUM_API_TOKEN as string | undefined) ||
    readStore('STRATUM_API_TOKEN')
  const user =
    (import.meta.env.VITE_STRATUM_USER as string | undefined) ||
    readStore('STRATUM_USER')
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }
  if (user) {
    headers['X-Stratum-User'] = user
  }
  return headers
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { ...authHeaders(), ...(init?.headers || {}) },
  })
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(detail || `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  snapshot: () => request<PlatformSnapshot>('/snapshot'),
  uploadDocument: (body: {
    title: string
    format: string
    summary?: string
    content_hint?: string
    acl_readers?: string[]
    read_error?: boolean
    read_error_detail?: string
  }) =>
    request<ClassifyResult>('/documents/upload', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  setDocumentAcl: (
    id: string,
    body: { acl_readers: string[]; owner_id?: string | null },
  ) =>
    request<PlatformSnapshot>(`/documents/${id}/acl`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),
  confirmDocumentVersion: (id: string, note = '') =>
    request<PlatformSnapshot>(`/documents/${id}/confirm-version`, {
      method: 'POST',
      body: JSON.stringify({ note }),
    }),
  getDocument: (id: string) =>
    request<{ document: unknown; facts: unknown[] }>(`/documents/${id}`),
  answerQuestion: (id: string, answer: string) =>
    request<PlatformSnapshot>(`/questions/${id}/answer`, {
      method: 'POST',
      body: JSON.stringify({ answer }),
    }),
  approveInsight: (id: string, status: 'approved' | 'rejected' | 'pending') =>
    request<PlatformSnapshot>(`/insights/${id}/approval`, {
      method: 'POST',
      body: JSON.stringify({ status }),
    }),
  screenOpportunity: (opportunity: Opportunity) =>
    request<{ admissible: boolean; checks: unknown[] }>('/regulatory/screen', {
      method: 'POST',
      body: JSON.stringify(opportunity),
    }),
  asIs: () => request<Record<string, unknown>>('/model/as-is'),
  toBe: () => request<Record<string, unknown>>('/model/to-be'),
  computeRoi: (body: Record<string, unknown>) =>
    request<RoiModel>('/roi/compute', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  reset: () => request<PlatformSnapshot>('/reset', { method: 'POST' }),
}
