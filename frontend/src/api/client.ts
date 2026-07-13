const API_BASE = 'http://127.0.0.1:8000'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!res.ok) {
    const body = await res.json().catch(() => null)
    const detail = typeof body?.detail === 'string' ? body.detail : `Request failed (${res.status})`
    throw new Error(detail)
  }

  if (res.status === 204) {
    return undefined as T
  }
  return (await res.json()) as T
}

export const api = {
  list: <T>(path: string): Promise<T[]> => request<T[]>(path),
  create: <T>(path: string, data: Record<string, unknown>): Promise<T> =>
    request<T>(path, { method: 'POST', body: JSON.stringify(data) }),
  update: <T>(path: string, id: number, data: Record<string, unknown>): Promise<T> =>
    request<T>(`${path}/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  remove: (path: string, id: number): Promise<void> =>
    request<void>(`${path}/${id}`, { method: 'DELETE' }),
}
