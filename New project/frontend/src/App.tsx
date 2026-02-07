import React, { useEffect, useState } from 'react'
import { fetchInsights, generateInsights, login, seedDemo, type Insight } from './api'
import InsightCards from './components/InsightCards'
import FunnelChart from './components/FunnelChart'
import CohortSelector from './components/CohortSelector'

export default function App() {
  const [token, setToken] = useState<string | null>(null)
  const [insights, setInsights] = useState<Insight[]>([])
  const [cohort, setCohort] = useState('all')
  const [status, setStatus] = useState('')

  useEffect(() => {
    async function boot() {
      try {
        const auth = await login('demo', 'demo')
        setToken(auth.access_token)
        const list = await fetchInsights(auth.access_token)
        setInsights(list)
      } catch (err) {
        setStatus('Login or fetch failed')
      }
    }
    boot()
  }, [])

  const handleGenerate = async () => {
    if (!token) return
    setStatus('Generating insights...')
    await generateInsights(token)
    const list = await fetchInsights(token)
    setInsights(list)
    setStatus('')
  }

  const handleSeed = async () => {
    setStatus('Seeding demo data...')
    await seedDemo()
    setStatus('Demo data seeded')
  }

  const filtered = cohort === 'all' ? insights : insights.filter((i) => i.payload?.cohort === cohort)

  return (
    <div className="page">
      <header>
        <h1>Signal &gt; Noise</h1>
        <p>Behavioral intelligence for product teams.</p>
      </header>

      <section className="controls">
        <button onClick={handleGenerate}>Generate Insights</button>
        <button onClick={handleSeed}>Replay Demo Data</button>
        <CohortSelector value={cohort} onChange={setCohort} />
        <span className="status">{status}</span>
      </section>

      <section className="grid">
        <div className="panel">
          <h2>Funnel</h2>
          <FunnelChart />
        </div>
        <div className="panel">
          <h2>Insights</h2>
          <InsightCards insights={filtered} />
        </div>
      </section>
    </div>
  )
}
