const { defineConfig } = require('@playwright/test');
module.exports = defineConfig({
  testDir: './tests/browser',
  timeout: 90000,
  expect: { timeout: 15000 },
  workers: 1,
  retries: 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: { baseURL: 'http://127.0.0.1:8788', viewport: { width: 1280, height: 800 },
    locale: 'pt-BR', reducedMotion: 'reduce', screenshot: 'only-on-failure', trace: 'retain-on-failure' },
  webServer: { command: 'python scripts/serve.py --port 8788', url: 'http://127.0.0.1:8788/api/health',
    reuseExistingServer: !process.env.CI, timeout: 120000 }
});
