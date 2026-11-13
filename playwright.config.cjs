const { defineConfig } = require('@playwright/test');
const port = Number(process.env.SABER_TEST_PORT || 8791);
module.exports = defineConfig({
  testDir: './tests/browser',
  timeout: 90000,
  expect: { timeout: 15000 },
  workers: 1,
  retries: 0,
  reporter: [['list'], ['html', { open: 'never' }], ['./tests/browser/consensus_reporter.cjs']],
  use: { baseURL: `http://127.0.0.1:${port}`, viewport: { width: 1280, height: 800 },
    channel: process.env.SABER_BROWSER_CHANNEL || undefined,
    locale: 'pt-BR', reducedMotion: 'reduce', screenshot: 'only-on-failure', trace: 'off' },
  webServer: { command: `python scripts/serve.py --quiet --port ${port}`, url: `http://127.0.0.1:${port}/api/health`,
    reuseExistingServer: false, timeout: 30000 }
});
