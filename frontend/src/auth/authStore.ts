const TOKEN_KEY = 'contoso_token'
type Listener = (token: string | null) => void

const listeners = new Set<Listener>()

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
  listeners.forEach((listener) => listener(token))
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
  listeners.forEach((listener) => listener(null))
}

export function subscribeToken(listener: Listener): () => void {
  listeners.add(listener)
  return () => listeners.delete(listener)
}
