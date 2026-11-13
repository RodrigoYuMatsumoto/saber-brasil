// Testes adicionais da auditoria Grok de 2026-11-12 (itens 3 a 6 do pedido).
const { test, expect } = require('@playwright/test');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const topics = ['brazil_topics', 'international', 'east_asia', 'official_units']
  .flatMap(name => require(path.join(root, 'data', `${name}.json`)).topics);
const shots = process.env.SABER_SHOTS || null;

async function ready(page) {
  await page.goto('/');
  await page.locator('#subjects button').first().waitFor();
  await expect.poll(() => page.locator('#graph').getAttribute('data-camera')).not.toBeNull();
}
const camera = async page => JSON.parse(await page.locator('#graph').getAttribute('data-camera'));
const zoom = async page => Number(await page.locator('#graph').getAttribute('data-zoom'));
const summary = page => page.evaluate(() => window.__SABER_TEST__.getSummary());
const options = page => page.locator('#grade option').evaluateAll(list => list.map(o => o.value));

test('Listas fixas de séries por sistema, inclusive EI e K-8', async ({ page }) => {
  await ready(page);
  const want = { BR: ['all','0','1','2','3','4','5','6','7','8','9'], US: ['all','0','1','2','3','4','5','6','7','8'],
    'GB-ENG': ['all','1','2','3','4','5','6','7','8','9'], JP: ['all','1','2','3','4','5','6','7','8','9'], CN: ['all','1','2','3','4','5','6','7','8','9'] };
  for (const [system, values] of Object.entries(want)) {
    await page.locator('#school-system').selectOption(system);
    expect(await options(page)).toEqual(values);
  }
  await page.locator('#school-system').selectOption('BR'); await page.locator('#grade').selectOption('0');
  const ei = topics.filter(t => (t.schoolPlacements || []).some(p => p.system === 'BR' && p.years.includes(0))).length;
  expect(ei).toBe(104);
  await expect.poll(async () => (await summary(page)).filteredCount).toBe(ei);
  await page.locator('#school-system').selectOption('JP'); await page.locator('#grade').selectOption('7');
  const jp7 = topics.filter(t => (t.schoolPlacements || []).some(p => p.system === 'JP' && p.years.includes(7))).length;
  await expect.poll(async () => (await summary(page)).filteredCount).toBe(jp7);
  await expect(page.locator('#grade option[value="7"]')).toHaveText('中学1年', { useInnerText: false }).catch(() => {});
});

test('Contador "Mostrando N de M" e botões de seleção', async ({ page }) => {
  await ready(page);
  const fmt = n => new Intl.NumberFormat('pt-BR').format(n);
  await expect(page.locator('#visible-count')).toContainText(`Mostrando ${fmt(topics.length)} de ${fmt(topics.length)}`);
  await page.locator('#subjects-none').click();
  await expect(page.locator('#visible-count')).toContainText(`Mostrando 0 de ${fmt(topics.length)}`);
  await page.locator('#subjects-reset').click(); await page.locator('#clear-filters').click();
  await page.locator('#language').selectOption('en');
  await expect(page.locator('#visible-count')).toContainText('Showing');
  await page.locator('#language').selectOption('pt-BR');
});

test('Zoom de 0,25x a 24x, duplo clique e pivô na seleção', async ({ page }) => {
  await ready(page);
  for (let i = 0; i < 40; i++) await page.locator('#zoom-in').click();
  expect(await zoom(page)).toBe(2400);
  await page.locator('#fit-all').click();
  for (let i = 0; i < 40; i++) await page.locator('#zoom-out').click();
  expect(await zoom(page)).toBe(25);
  await page.locator('#fit-all').click();
  const before = await zoom(page);
  await page.mouse.dblclick(760, 560);
  await expect.poll(() => zoom(page)).toBeGreaterThan(before);
  const mid = await zoom(page);
  await page.keyboard.down('Shift'); await page.mouse.dblclick(760, 560); await page.keyboard.up('Shift');
  await expect.poll(() => zoom(page)).toBeLessThan(mid);
  await page.locator('#fit-all').click();
  await page.locator('#search').fill('EF03MA01');
  await page.locator('#search-results button').first().click();
  const c = await camera(page);
  expect(c.pivot).toBe('br_ef03ma01');
  const node = await page.evaluate(() => window.__SABER_TEST__.getSummary().selected);
  expect(node).toBe('br_ef03ma01');
  await page.mouse.move(700, 400); await page.mouse.down(); await page.mouse.move(820, 470, { steps: 6 }); await page.mouse.up();
  expect((await camera(page)).target).toEqual(c.target);
  await page.locator('#reset-camera').click();
});

test('Conteúdo nos quatro idiomas, unidades oficiais e capturas', async ({ page }, info) => {
  await ready(page);
  await page.locator('#search').fill('8350213121400000');
  await expect(page.locator('#search-results button').first()).toBeVisible();
  await page.locator('#search-results button').first().click();
  await expect(page.locator('#detail-content')).toContainText('8350213121400000');
  await expect(page.locator('#detail-content')).toContainText('Unidade curricular oficial');
  for (const language of ['en', 'ja', 'zh-Hant']) {
    await page.locator('#language').selectOption(language);
    await expect(page.locator('html')).toHaveAttribute('lang', language);
  }
  await page.locator('#language').selectOption('ja');
  await page.locator('#search').fill('EF01MA01');
  await page.locator('#search-results button').first().click();
  const text = await page.locator('#detail-content').innerText();
  expect(/[\u3040-\u30ff]/.test(text)).toBe(true);
  if (shots) await page.screenshot({ path: path.join(shots, 'desktop_ja_detalhe.png') });
  await page.locator('#language').selectOption('pt-BR'); await page.locator('#search').fill('');
  await page.locator('#school-system').selectOption('BR'); await page.locator('#grade').selectOption('0');
  await expect.poll(async () => (await summary(page)).filteredCount).toBe(104);
  if (shots) await page.screenshot({ path: path.join(shots, 'desktop_br_ei.png') });
  await page.locator('#clear-filters').click();
  if (shots) await page.screenshot({ path: path.join(shots, 'desktop_geral.png') });
});

test('Móvel: sem transbordamento, seletor de sistema e idioma visíveis', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await ready(page);
  const b = await page.evaluate(() => ({ w: document.documentElement.clientWidth, s: document.documentElement.scrollWidth }));
  expect(b.s).toBeLessThanOrEqual(b.w);
  await expect(page.locator('#language')).toBeVisible();
  await page.locator('#school-system').selectOption('US'); await page.locator('#grade').selectOption('0');
  if (shots) await page.screenshot({ path: path.join(shots, 'mobile_us_k.png'), fullPage: true });
  await page.locator('#school-system').selectOption('CN'); await page.locator('#grade').selectOption('9');
  await page.locator('#language').selectOption('zh-Hant');
  await page.locator('#list-view').click();
  if (shots) await page.screenshot({ path: path.join(shots, 'mobile_cn9_zh-Hant_lista.png'), fullPage: true });
  await page.locator('#language').selectOption('pt-BR'); await page.locator('#clear-filters').click();
});
