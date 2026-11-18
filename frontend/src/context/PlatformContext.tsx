import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { api } from '../lib/api'
import type { PlatformSnapshot } from '../types'

interface PlatformContextValue {
  snapshot: PlatformSnapshot | null
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  setSnapshot: (snap: PlatformSnapshot) => void
}

const PlatformContext = createContext<PlatformContextValue | null>(null)

export function PlatformProvider({ children }: { children: ReactNode }) {
  const [snapshot, setSnapshot] = useState<PlatformSnapshot | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.snapshot()
      setSnapshot(data)
    } catch (err) {
      try {
        const res = await fetch('/demo-snapshot.json')
        if (!res.ok) throw err
        const data = (await res.json()) as PlatformSnapshot
        setSnapshot(data)
        setError('API недоступен — показаны демо-данные (только чтение).')
      } catch {
        setError(err instanceof Error ? err.message : 'Не удалось загрузить данные')
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const value = useMemo(
    () => ({ snapshot, loading, error, refresh, setSnapshot }),
    [snapshot, loading, error, refresh],
  )

  return <PlatformContext.Provider value={value}>{children}</PlatformContext.Provider>
}

export function usePlatform() {
  const ctx = useContext(PlatformContext)
  if (!ctx) throw new Error('usePlatform must be used within PlatformProvider')
  return ctx
}
