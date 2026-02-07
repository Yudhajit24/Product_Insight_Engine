import React from 'react'
import { Funnel, FunnelChart as ReFunnelChart, LabelList, Tooltip } from 'recharts'

const data = [
  { name: 'Signup', value: 1000 },
  { name: 'Onboarded', value: 650 },
  { name: 'Activated', value: 420 },
  { name: 'Retained', value: 260 }
]

export default function FunnelChart() {
  return (
    <ReFunnelChart width={360} height={260}>
      <Tooltip />
      <Funnel dataKey="value" data={data} isAnimationActive>
        <LabelList position="right" fill="#1a1a1a" stroke="none" dataKey="name" />
      </Funnel>
    </ReFunnelChart>
  )
}
