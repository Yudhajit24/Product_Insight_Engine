import { render, screen } from '@testing-library/react'
import App from './App'

vi.mock('./api', () => ({
  login: () => Promise.resolve({ access_token: 'token' }),
  fetchInsights: () => Promise.resolve([]),
  generateInsights: () => Promise.resolve([]),
  seedDemo: () => Promise.resolve({})
}))

it('renders title', async () => {
  render(<App />)
  expect(await screen.findByText(/Signal > Noise/i)).toBeInTheDocument()
})
