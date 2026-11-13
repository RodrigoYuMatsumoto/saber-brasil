const { test, expect } = require('@playwright/test');
const fs = require('node:fs/promises');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const datasets = ['brazil_topics', 'international', 'east_asia', 'official_units'].map(name => require(path.join(root, 'data', `${name}.json`)));
const topics = datasets.flatMap(data => data.topics);

async function ready(page, address = '/') {
  await page.goto(address);
  await page.locator('#subjects button').first().waitFor();
  await expect.poll(() => page.locator('#graph').getAttribute('data-camera')).not.toBeNull();
}
async function camera(page) { return JSON.parse(await page.locator('#graph').getAttribute('data-camera')); }
async function summary(page) { return page.evaluate(() => window.__SABER_TEST__.getSummary()); }

test('IDs únicos, zoom real, giro, deslocamento e foco individual', async ({ page }, info) => {
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  await ready(page);
  const ids = await page.locator('[id]').evaluateAll(elements => elements.map(element => element.id));
  expect(new Set(ids).size).toBe(ids.length);
  expect((await summary(page)).topicCount).toBe(topics.length);
  const start = await camera(page);
  await page.locator('#zoom-in').click(); await page.locator('#zoom-in').click();
  await expect.poll(async () => (await camera(page)).distance).toBeLessThan(start.distance);
  await page.locator('#zoom-out').click(); await page.locator('#zoom-out').click();
  await expect.poll(async () => (await camera(page)).distance).toBeCloseTo(start.distance, 1);
  await page.mouse.move(900, 400); await page.mouse.down();
  await page.mouse.move(1020, 480, { steps: 8 }); await page.mouse.up();
  expect((await camera(page)).quaternion).not.toEqual(start.quaternion);
  await page.locator('#graph').press('Shift+ArrowRight');
  expect((await camera(page)).pan[0]).toBeGreaterThan(0);
  await page.locator('#graph').press('Home');
  expect((await camera(page)).pan).toEqual([0, 0]);
  await page.locator('#search').fill('EF03MA01');
  await page.locator('#search-results button').first().click();
  await page.locator('#focus-topic').click();
  await expect.poll(async () => (await camera(page)).focused).toBe('br_ef03ma01');
  expect((await camera(page)).distance).toBeLessThan(start.distance);
  await page.locator('#clear-filters').click(); await page.locator('#fit-all').click();
  expect((await camera(page)).focused).toBeNull();
  expect(errors).toEqual([]);
  await page.screenshot({ path: info.outputPath('Saber_Brasil_Desktop.png'), fullPage: true });
});

test('Séries de cinco sistemas, selecionar e desmarcar todas', async ({ page }) => {
  await ready(page);
  for (const [system, year] of [['BR', 3], ['US', 3], ['GB-ENG', 3], ['JP', 3], ['CN', 9]]) {
    await page.locator('#school-system').selectOption(system);
    await page.locator('#grade').selectOption(String(year));
    const expected = topics.filter(topic => (topic.schoolPlacements || []).some(placement =>
      placement.system === system && placement.years.includes(year))).length;
    expect(expected).toBeGreaterThan(0);
    await expect.poll(async () => (await summary(page)).filteredCount).toBe(expected);
  }
  await page.locator('#subjects-none').click();
  await expect.poll(async () => (await summary(page)).filteredCount).toBe(0);
  await expect(page.locator('#empty')).toBeVisible();
  await page.locator('#subjects-reset').click();
  expect((await summary(page)).filteredCount).toBeGreaterThan(0);
  await page.locator('#clear-filters').click();
  await expect.poll(async () => (await summary(page)).filteredCount).toBe(topics.length);
});

test('Quatro idiomas da interface e rótulos de acessibilidade', async ({ page }) => {
  await ready(page);
  for (const [language, label] of [['pt-BR', 'Selecionar todas'], ['en', 'Select all'], ['ja', 'すべて選択'], ['zh-Hant', '全部選取']]) {
    await page.locator('#language').selectOption(language);
    await expect(page.locator('html')).toHaveAttribute('lang', language);
    await expect(page.locator('#subjects-reset')).toHaveText(label);
    if (language !== 'pt-BR') {
      expect(await page.locator('.explore-controls').getAttribute('aria-label')).not.toBe('Explorar o mapa');
      expect(await page.locator('.legend').getAttribute('aria-label')).not.toBe('Filtrar por matéria');
    }
  }
});

test('Exportações reais preservam habilidade, recortes e tipos de conexão', async ({ page }) => {
  await ready(page);
  await page.locator('#search').fill('EF01CI01'); await page.locator('#list-view').click();
  const waitingJson = page.waitForEvent('download'); await page.locator('#export-json').click();
  const exportedJson = await waitingJson;
  const data = JSON.parse(await fs.readFile(await exportedJson.path(), 'utf8'));
  expect(data.topics.map(topic => topic.id)).toEqual(['br_ef01ci01', 'br_ef01ci01_m01', 'br_ef01ci01_m02']);
  expect(data.topics[0].prerequisites.every(row => row.relation === 'parte-da-habilidade')).toBe(true);
  const waitingCsv = page.waitForEvent('download'); await page.locator('#export-csv').click();
  const exportedCsv = await waitingCsv;
  const csv = await fs.readFile(await exportedCsv.path(), 'utf8');
  expect(csv.charCodeAt(0)).toBe(0xfeff);
  expect(csv).toContain('br_ef01ci01_m01'); expect(csv).toContain('parte-da-habilidade');
});

test('Layout móvel sem transbordamento e título com espaços', async ({ page }, info) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await ready(page);
  const bounds = await page.evaluate(() => ({ width: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth }));
  expect(bounds.scroll).toBeLessThanOrEqual(bounds.width);
  const title = (await page.locator('#hero-title').innerText()).replace(/\s+/g, ' ');
  expect(title).toContain('que uma criança');
  await page.locator('#school-system').selectOption('CN'); await page.locator('#grade').selectOption('9');
  await page.locator('#language').selectOption('zh-Hant');
  await page.locator('#list-view').click();
  await expect(page.locator('#results button').first()).toBeVisible();
  await page.locator('#language').selectOption('pt-BR');
  await page.locator('#clear-filters').click(); await page.locator('#graph-view').click();
  await page.screenshot({ path: info.outputPath('Saber_Brasil_Mobile.png'), fullPage: true });
});

test('HTML portátil usa apenas seu próprio documento', async ({ page }, info) => {
  const requests = []; page.on('request', request => requests.push(request.url()));
  await ready(page, '/Saber_Brasil_Offline.html');
  expect((await summary(page)).topicCount).toBe(topics.length);
  await page.locator('#school-system').selectOption('JP'); await page.locator('#grade').selectOption('3');
  await page.locator('#language').selectOption('ja');
  expect((await summary(page)).filteredCount).toBeGreaterThan(0);
  expect(requests).toEqual(['http://127.0.0.1:8788/Saber_Brasil_Offline.html']);
  await page.locator('#language').selectOption('pt-BR'); await page.locator('#clear-filters').click();
  await page.screenshot({ path: info.outputPath('Saber_Brasil_Portatil.png'), fullPage: true });
});
