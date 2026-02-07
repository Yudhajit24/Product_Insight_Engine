import { test, expect } from '@playwright/test'

test('loads app shell', async ({ page }) => {
  await page.goto('http://localhost:5173')
  await expect(page.getByText('Signal > Noise')).toBeVisible()
})
