import type { ClassifyResult, Opportunity, PlatformSnapshot } from '../types'

const BASE = '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
    ...init,
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
  }) =>
    request<ClassifyResult>('/documents/upload', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
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
  reset: () => request<PlatformSnapshot>('/reset', { method: 'POST' }),
}
