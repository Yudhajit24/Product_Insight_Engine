export type Insight = {
  id: number
  type: string
  score: number
  payload: Record<string, unknown>
  created_at: string
  explanation?: string
}

export async function login(username: string, password: string) {
  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  })
  if (!res.ok) throw new Error('Login failed')
  return res.json() as Promise<{ access_token: string }>
}

export async function fetchInsights(token: string): Promise<Insight[]> {
  const res = await fetch('/api/insights?limit=10', {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (!res.ok) throw new Error('Failed to load insights')
  return res.json()
}

export async function generateInsights(token: string) {
  const now = new Date()
  const start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
  const res = await fetch('/api/insights/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ start_time: start.toISOString(), end_time: now.toISOString() })
  })
  if (!res.ok) throw new Error('Failed to generate insights')
  return res.json()
}

export async function seedDemo() {
  const res = await fetch('/api/seed/demo', { method: 'POST' })
  if (!res.ok) throw new Error('Seed failed')
  return res.json()
}
