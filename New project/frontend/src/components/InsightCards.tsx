import React from 'react'
import type { Insight } from '../api'

export default function InsightCards({ insights }: { insights: Insight[] }) {
  return (
    <div className="cards">
      {insights.map((insight) => (
        <div key={insight.id} className="card">
          <div className="card-header">
            <strong>{insight.type}</strong>
            <span className="score">Confidence {insight.score.toFixed(2)}</span>
          </div>
          <div className="card-body">
            <p>{insight.explanation || 'No explanation available.'}</p>
            <pre>{JSON.stringify(insight.payload, null, 2)}</pre>
          </div>
        </div>
      ))}
    </div>
  )
}
