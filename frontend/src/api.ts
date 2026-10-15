import { useEffect, useState } from 'react'
import type { Dashboard } from './types'

export async function fetchDashboard(): Promise<Dashboard> {
  const resp = await fetch('/api/dashboard')
  if (!resp.ok) {
    throw new Error(`HTTP ${resp.status}`)
  }
  return resp.json()
}

export function useDashboard(intervalMs: number): {
  data: Dashboard | null
  error: string | null
} {
  const [data, setData] = useState<Dashboard | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    const load = async () => {
      try {
        const result = await fetchDashboard()
        if (active) {
          setData(result)
          setError(null)
        }
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : 'Błąd sieci')
        }
      }
    }

    load()
    const id = setInterval(load, intervalMs)
    return () => {
      active = false
      clearInterval(id)
    }
  }, [intervalMs])

  return { data, error }
}
