import React from 'react'

export default function CohortSelector({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="all">All Cohorts</option>
      <option value="cohort_0">Cohort 0</option>
      <option value="cohort_1">Cohort 1</option>
      <option value="cohort_2">Cohort 2</option>
    </select>
  )
}
