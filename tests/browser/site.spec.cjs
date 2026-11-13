const { test, expect } = require('@playwright/test');
const fs = require('node:fs/promises');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const baseURL = `http://127.0.0.1:${Number(process.env.SABER_TEST_PORT || 8791)}`;
const datasets = ['brazil_topics', 'international', 'east_asia'].map(name => require(path.join(root, 'data', `${name}.json`)));
const topics = datasets.flatMap(data => data.topics);
const baseLayers = ['base-br', 'base-marble'];
const baseTopics = topics.filter(topic => baseLayers.includes(topic.layer));
const intl = datasets[1].topics[0];
const translated = require(path.join(root, 'data/translations.json')).topics;

async function ready(page, address = '/') {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto(address);
  await page.locator('#subjects button').first().waitFor();
  await expect.poll(() => page.locator('#graph').getAttribute('data-camera')).not.toBeNull();
  if (!(await summary(page)).paused) await page.locator('#rotate').click();
  await expect.poll(async () => (await summary(page)).paused).toBe(true);
}
async function camera(page) { return JSON.parse(await page.locator('#graph').getAttribute('data-camera')); }
async function summary(page) { return page.evaluate(() => window.__SABER_TEST__.getSummary()); }
async function point(page, id) { return page.evaluate(id => window.__SABER_TEST__.getProjectedTopic(id), id); }
async function screenshot(page, info, name) {
  await page.evaluate(() => window.scrollTo(0, 0));
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBe(0);
  const target = path.join(root, 'evidence', name);
  try {
    await fs.access(target);
    const folder = path.join(root, 'backups', 'screenshot_' + new Date().toISOString().replace(/[:.]/g, '_'));
    await fs.mkdir(folder, { recursive: true }); await fs.copyFile(target, path.join(folder, name));
  } catch (error) { if (error.code !== 'ENOENT') throw error; }
  await page.screenshot({ path: target, fullPage: true });
  await info.attach(name, { path: target, contentType: 'image/png' });
}
async function enableLayer(page, layer) {
  const details = page.locator('details.layer-controls');
  if (!(await details.evaluate(el => el.open))) await details.locator('summary').click();
  await page.locator(`input[data-layer="${layer}"]`).check();
}
async function closeLayers(page) {
  const details = page.locator('details.layer-controls');
  if (await details.evaluate(el => el.open)) await details.locator('summary').click();
}
const upY = q => 1 - 2 * (q[0] * q[0] + q[2] * q[2]);

test('A01 Base de consenso, IDs únicos e camadas adicionais desligadas', async ({ page, browser }, info) => {
  await ready(page);
  await info.attach('browser-version', { body: Buffer.from(browser.version()), contentType: 'text/plain' });
  const ids = await page.locator('[id]').evaluateAll(elements => elements.map(element => element.id));
  expect(new Set(ids).size).toBe(ids.length);
  expect(baseTopics.length).toBe(3315);
  const state = await summary(page);
  expect(state.topicCount).toBe(topics.length); expect(state.filteredCount).toBe(3315);
  expect(state.activeEdgeCount).toBe(4003); expect(state.inferredEdgesEnabled).toBe(false);
  expect(state.enabledLayers.sort()).toEqual(baseLayers.sort());
  await expect(page.locator('#layer-summary')).toContainText('3.315');
  await screenshot(page, info, 'Consenso_V3_Desktop.png');
});

test('A02 Camada editorial opcional, ID próprio e selo de revisão', async ({ page }, info) => {
  await ready(page); await enableLayer(page, 'editorial-ia'); await closeLayers(page);
  await expect.poll(async () => (await summary(page)).filteredCount).toBe(4058);
  await page.goto('/#ED-EF01CI01-01'); await expect(page.locator('#detail')).toBeVisible();
  expect((await summary(page)).selected).toBe('ED-EF01CI01-01');
  await expect(page.locator('#detail-content')).toContainText(/editorial/i);
  await expect(page.locator('#detail-content')).toContainText(/revisão/i);
  await expect(page.locator('#detail-content')).toContainText(/não é texto oficial/i);
  await screenshot(page, info, 'Consenso_V3_Editorial.png');
  await page.locator('#detail-close').click(); await page.locator('#clear-filters').click();
  await expect.poll(async () => (await summary(page)).filteredCount).toBe(3315);
});

test('A03 Links por código oficial e aliases anteriores resolvem o mesmo nó', async ({ page }) => {
  const ei = topics.find(topic => topic.layer === 'ei-source');
  for (const [hash, id] of [['EF67LP33', 'br_ef67lp33'], ['EF05CO11', 'br_ef05co11'], ['EF01MA01', 'br_ef01ma01'], ['br_ef01ci01_m01', 'ED-EF01CI01-01'], [ei.code, ei.id]]) {
    await ready(page, '/#' + hash);
    await expect.poll(async () => (await summary(page)).selected).toBe(id);
    await expect(page.locator('#detail')).toBeVisible();
    if (hash === 'EF05CO11') await expect(page.locator('#detail-content')).toContainText('EF05CO011');
  }
});

test('A04 Séries dos cinco sistemas e atalhos por blocos publicados', async ({ page }, info) => {
  await ready(page);
  const options = {
    BR: ['all', 'EI', ...Array.from({ length: 9 }, (_, i) => String(i + 1))],
    US: ['all', ...Array.from({ length: 9 }, (_, i) => String(i))],
    'GB-ENG': ['all', ...Array.from({ length: 9 }, (_, i) => String(i + 1)), 'KS1', 'KS2', 'KS3'],
    JP: ['all', ...Array.from({ length: 9 }, (_, i) => String(i + 1))],
    CN: ['all', ...Array.from({ length: 9 }, (_, i) => String(i + 1)), 'CN1', 'CN2', 'CN3', 'CN4']
  };
  for (const [system, year] of [['BR', 3], ['US', 3], ['GB-ENG', 3], ['JP', 3], ['CN', 9]]) {
    if (system === 'JP') await enableLayer(page, 'jp-editorial');
    if (system === 'CN') await enableLayer(page, 'cn-editorial');
    await closeLayers(page); await page.locator('#school-system').selectOption(system);
    expect((await page.locator('#grade option').evaluateAll(items => items.map(item => item.value))).sort()).toEqual(options[system].sort());
    await page.locator('#grade').selectOption(String(year));
    const enabled = (await summary(page)).enabledLayers;
    const expected = topics.filter(topic => enabled.includes(topic.layer) && (topic.schoolPlacements || []).some(p => p.system === system && p.years.includes(year))).length;
    expect(expected).toBeGreaterThan(0);
    await expect.poll(async () => (await summary(page)).filteredCount).toBe(expected);
  }
  for (const [system, stage, years] of [['GB-ENG', 'KS2', [3, 4, 5, 6]], ['CN', 'CN3', [5, 6]]]) {
    await page.locator('#school-system').selectOption(system); await page.locator('#grade').selectOption(stage);
    const enabled = (await summary(page)).enabledLayers;
    const expected = topics.filter(topic => enabled.includes(topic.layer) && (topic.schoolPlacements || []).some(p => p.system === system && p.years.some(year => years.includes(year)))).length;
    await expect.poll(async () => (await summary(page)).filteredCount).toBe(expected);
  }
  await page.locator('#school-system').selectOption('BR'); await page.locator('#grade').selectOption('EI');
  await expect.poll(async () => (await summary(page)).filteredCount).toBe(0);
  await expect(page.locator('#placement-note')).toContainText(/infantil/i);
  await enableLayer(page, 'ei-source'); await closeLayers(page);
  await expect.poll(async () => (await summary(page)).filteredCount).toBe(104);
  const ei = datasets[0].topics.filter(topic => topic.layer === 'ei-source');
  expect(ei).toHaveLength(104);
  expect(await page.evaluate(() => window.__SABER_TEST__.getFilteredIds().sort())).toEqual(ei.map(topic => topic.id).sort());
  await page.locator('#clear-filters').click(); await screenshot(page, info, 'Consenso_V3_Filtros.png');
});

test('A05 Selecionar tudo, desmarcar tudo e limpar restaura o padrão', async ({ page }) => {
  await ready(page); await enableLayer(page, 'editorial-ia'); await closeLayers(page);
  await page.locator('#subjects-none').click();
  await expect.poll(async () => (await summary(page)).filteredCount).toBe(0);
  await expect(page.locator('#empty')).toBeVisible(); await page.locator('#subjects-reset').click();
  await expect.poll(async () => (await summary(page)).filteredCount).toBe(4058);
  await page.locator('#school-system').selectOption('BR'); await page.locator('#grade').selectOption('4');
  await page.locator('#search').fill('EF04MA01'); await page.locator('#clear-filters').click();
  await expect(page.locator('#school-system')).toHaveValue('all'); await expect(page.locator('#grade')).toHaveValue('all');
  await expect(page.locator('#search')).toHaveValue('');
  expect((await summary(page)).enabledLayers.sort()).toEqual(baseLayers.sort());
  expect((await summary(page)).filteredCount).toBe(3315);
});

test('A06 Zoom real, limites 0,25x a 24x e restauração da vista', async ({ page }) => {
  await ready(page); const start = await camera(page);
  await page.locator('#zoom-in').click(); await page.locator('#zoom-in').click();
  expect((await camera(page)).distance).toBeLessThan(start.distance);
  await page.locator('#zoom-out').click(); await page.locator('#zoom-out').click();
  expect((await camera(page)).distance).toBeCloseTo(start.distance, 1);
  for (let i = 0; i < 30; i++) await page.locator('#zoom-in').click();
  expect((await summary(page)).zoom).toBeCloseTo(24, 6);
  for (let i = 0; i < 55; i++) await page.locator('#zoom-out').click();
  expect((await summary(page)).zoom).toBeCloseTo(0.25, 6);
  await page.locator('#reset-camera').click();
  expect((await summary(page)).zoom).toBeCloseTo(1, 6); expect((await camera(page)).pan).toEqual([0, 0]);
});

test('A07 Roda ancorada no cursor conserva a projeção do ponto', async ({ page }) => {
  await ready(page);
  const candidates = await page.evaluate(ids => { const canvas = document.querySelector('#graph'), box = canvas.getBoundingClientRect(); return ids.map(id => window.__SABER_TEST__.getProjectedTopic(id)).filter(p => p?.visible && p.x > 760 && p.x < 1170 && p.y > 230 && p.y < 620 && document.elementFromPoint(box.left + p.x, box.top + p.y) === canvas); }, baseTopics.map(topic => topic.id));
  expect(candidates.length).toBeGreaterThan(0); const chosen = candidates[0];
  const cursor = { x: Math.floor(chosen.x), y: Math.floor(chosen.y) };
  const hit = await page.evaluate(({ x, y }) => window.__SABER_TEST__.hitTest(x, y), cursor);
  expect(hit).not.toBeNull();
  const box = await page.locator('#graph').boundingBox(); const before = await camera(page);
  await page.mouse.move(box.x + cursor.x, box.y + cursor.y); await page.mouse.wheel(0, -180);
  await expect.poll(async () => (await camera(page)).distance).toBeLessThan(before.distance);
  const after = await point(page, hit.id);
  expect(Math.hypot(after.x - hit.x, after.y - hit.y)).toBeLessThan(4);
});

test('A08 Órbita ultrapassa os polos, roll e deslocamento real por arraste', async ({ page }) => {
  await ready(page); const start = await camera(page);
  await page.mouse.move(950, 390); await page.mouse.down();
  await page.mouse.move(1080, 510, { steps: 10 }); await page.mouse.up();
  expect((await camera(page)).quaternion).not.toEqual(start.quaternion);
  await page.locator('#reset-camera').click(); let crossedPole = false;
  for (let i = 0; i < 90; i++) {
    await page.locator('#graph').press('ArrowUp');
    if (upY((await camera(page)).quaternion) < -0.5) crossedPole = true;
  }
  expect(crossedPole).toBe(true);
  const beforeRoll = await camera(page);
  await page.locator('#roll-right').click(); expect((await camera(page)).quaternion).not.toEqual(beforeRoll.quaternion);
  const beforePan = (await camera(page)).pan;
  await page.mouse.move(1000, 380); await page.mouse.down({ button: 'right' });
  await page.mouse.move(1060, 410, { steps: 5 }); await page.mouse.up({ button: 'right' });
  expect((await camera(page)).pan[0]).toBeGreaterThan(beforePan[0]);
  await page.keyboard.down('Shift'); await page.mouse.move(1010, 400); await page.mouse.down();
  await page.mouse.move(1080, 430, { steps: 4 }); await page.mouse.up(); await page.keyboard.up('Shift');
  expect((await camera(page)).pan[0]).toBeGreaterThan(beforePan[0] + 60);
});

test('A09 Foco individual usa o nó como pivô ao girar', async ({ page }, info) => {
  await ready(page, '/#EF03MA01'); await page.locator('#focus-topic').click();
  const selected = await point(page, 'br_ef03ma01'); const before = await camera(page);
  before.target.forEach((value, i) => expect(value).toBeCloseTo(selected.world[i], 3)); expect(before.focused).toBe('br_ef03ma01');
  await page.locator('#graph').press('ArrowRight'); await page.locator('#graph').press('ArrowUp');
  const after = await point(page, 'br_ef03ma01');
  expect((await camera(page)).quaternion).not.toEqual(before.quaternion);
  expect(Math.hypot(after.x - selected.x, after.y - selected.y)).toBeLessThan(0.01);
  await screenshot(page, info, 'Consenso_V3_Foco.png');
});

test('A10 Duplo clique no mapa e enquadramento da seleção filtrada', async ({ page }) => {
  await ready(page);
  const candidates = await page.evaluate(ids => { const canvas = document.querySelector('#graph'), box = canvas.getBoundingClientRect(); return ids.map(id => window.__SABER_TEST__.getProjectedTopic(id)).filter(p => p?.visible && p.x > 780 && p.x < 1150 && p.y > 260 && p.y < 600 && document.elementFromPoint(box.left + p.x, box.top + p.y) === canvas); }, baseTopics.map(topic => topic.id));
  expect(candidates.length).toBeGreaterThan(0); const chosen = candidates[0];
  await page.mouse.dblclick(chosen.x, chosen.y); const state = await summary(page);
  expect(state.selected).not.toBeNull(); expect(state.camera.focused).toBe(state.selected);
  await page.locator('#clear-filters').click();
  await page.locator('#school-system').selectOption('BR'); await page.locator('#grade').selectOption('1');
  await page.locator('#fit-selection').click(); const selection = await camera(page);
  await page.locator('#fit-all').click(); expect((await camera(page)).distance).toBeGreaterThan(selection.distance);
});

test('A11 Quatro idiomas, pergunta traduzida e original inglês visível', async ({ page }, info) => {
  await ready(page, '/#' + intl.id);
  for (const language of ['pt-BR', 'en', 'ja', 'zh-Hant']) {
    await page.locator('#language').selectOption(language);
    await expect(page.locator('html')).toHaveAttribute('lang', language);
    await expect(page.locator('#detail-title')).toHaveText(translated[intl.id][language].name);
    await expect(page.locator('#detail-content')).toContainText(translated[intl.id][language].assessmentPrompt);
    if (language !== 'en') {
      await expect(page.locator('#detail-content')).toContainText(intl.originalName);
      await expect(page.locator('#detail-content')).toContainText(intl.originalDescription);
      await expect(page.locator('#detail-content')).toContainText(intl.originalAssessmentPrompt);
    }
  }
  await page.locator('#language').selectOption('pt-BR');
  await expect(page.locator('#detail-content')).toContainText(/automática/i);
  await screenshot(page, info, 'Consenso_V3_Traducao.png');
});

test('A12 Exportações reais preservam camadas, IDs e tipos de conexão', async ({ page }) => {
  await ready(page); await enableLayer(page, 'editorial-ia'); await closeLayers(page);
  await page.locator('#search').fill('EF01CI01'); await page.locator('#list-view').click();
  const waitingJson = page.waitForEvent('download'); await page.locator('#export-json').click();
  const exportedJson = await waitingJson;
  const data = JSON.parse(await fs.readFile(await exportedJson.path(), 'utf8'));
  expect(data.topics.map(topic => topic.id).sort()).toEqual(['br_ef01ci01', 'ED-EF01CI01-01', 'ED-EF01CI01-02'].sort());
  const official = data.topics.find(topic => topic.id === 'br_ef01ci01');
  expect(official.prerequisites.every(row => row.relation === 'parte-da-habilidade')).toBe(true);
  const waitingCsv = page.waitForEvent('download'); await page.locator('#export-csv').click(); const exportedCsv = await waitingCsv;
  const csv = await fs.readFile(await exportedCsv.path(), 'utf8');
  expect(csv.charCodeAt(0)).toBe(0xfeff); expect(csv).toContain('ED-EF01CI01-01'); expect(csv).toContain('parte-da-habilidade');
});

test('A13 Layout móvel, filtros e idiomas sem transbordamento', async ({ page }, info) => {
  await page.setViewportSize({ width: 390, height: 844 }); await ready(page);
  const bounds = await page.evaluate(() => ({ width: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth }));
  expect(bounds.scroll).toBeLessThanOrEqual(bounds.width);
  expect((await page.locator('#hero-title').innerText()).replace(/\s+/g, ' ')).toContain('que uma criança');
  await enableLayer(page, 'cn-editorial'); await closeLayers(page);
  await page.locator('#school-system').selectOption('CN'); await page.locator('#grade').selectOption('9');
  await page.locator('#language').selectOption('zh-Hant'); await page.locator('#list-view').click();
  await expect(page.locator('#results button').first()).toBeVisible();
  await page.locator('#language').selectOption('pt-BR'); await page.locator('#clear-filters').click(); await page.locator('#graph-view').click();
  await page.locator('#graph').focus();
  await screenshot(page, info, 'Consenso_V3_Mobile.png');
});

test('A14 Pinça e movimento de dois dedos em celular emulado', async ({ browser }, info) => {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true, reducedMotion: 'reduce' });
  const page = await context.newPage();
  try {
    await ready(page, baseURL + '/'); const session = await context.newCDPSession(page); const before = await camera(page);
    const touch = (x, y, id) => ({ x, y, id, radiusX: 3, radiusY: 3, force: 1 });
    await session.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [touch(160, 330, 1), touch(240, 330, 2)] });
    for (let i = 1; i <= 5; i++) await session.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [touch(160 - i * 8, 330 + i * 2, 1), touch(240 + i * 8, 330 + i * 2, 2)] });
    await session.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    expect((await camera(page)).distance).toBeLessThan(before.distance); expect((await camera(page)).pan).not.toEqual(before.pan);
    await screenshot(page, info, 'Consenso_V3_Toque_Emulado.png');
  } finally { await context.close(); }
});

test('A15 HTML portátil conserva a base e usa uma solicitação de documento', async ({ page }, info) => {
  const requests = []; page.on('request', request => requests.push(request.url()));
  await ready(page, '/Saber_Brasil_Offline.html');
  expect((await summary(page)).topicCount).toBe(topics.length); expect((await summary(page)).filteredCount).toBe(3315);
  await enableLayer(page, 'jp-editorial'); await closeLayers(page);
  await page.locator('#school-system').selectOption('JP'); await page.locator('#grade').selectOption('3'); await page.locator('#language').selectOption('ja');
  expect((await summary(page)).filteredCount).toBeGreaterThan(0);
  expect(requests).toEqual([baseURL + '/Saber_Brasil_Offline.html']);
  await page.locator('#language').selectOption('pt-BR'); await page.locator('#clear-filters').click();
  await screenshot(page, info, 'Consenso_V3_Portatil.png');
});

test('A16 Unidades literais da EI e Ásia têm camada própria e identificador de origem', async ({ page }, info) => {
  for (const layer of ['jp-source', 'cn-source', 'ei-source']) {
    const topic = topics.find(row => row.layer === layer);
    expect(topic).toBeTruthy();
    await ready(page, '/#' + topic.id);
    expect((await summary(page)).enabledLayers).toContain(layer);
    await expect(page.locator('#detail .original-text')).toBeVisible();
    await expect(page.locator('#detail .original-text')).toContainText(topic.sourceLiteral.text);
    if (layer === 'cn-source') await expect(page.locator('#detail .original-text')).toContainText(/local/i);
    const image = { 'jp-source': 'Consenso_V3_Japao_Literal.png', 'cn-source': 'Consenso_V3_China_Literal.png', 'ei-source': 'Consenso_V3_Educacao_Infantil.png' }[layer];
    await screenshot(page, info, image);
  }
});

test('A17 Relações propostas e composição têm controles e contagens separados', async ({ page }) => {
  await ready(page);
  await page.locator('details.layer-controls summary').click();
  await page.locator('#inferred-relations').check();
  expect((await summary(page)).activeEdgeCount).toBe(4100);
  await enableLayer(page, 'editorial-ia'); expect((await summary(page)).activeEdgeCount).toBe(4843);
  await enableLayer(page, 'jp-editorial'); await enableLayer(page, 'cn-editorial');
  expect((await summary(page)).activeEdgeCount).toBe(4885);
  await page.locator('#inferred-relations').uncheck();
  expect((await summary(page)).activeEdgeCount).toBe(4746);
});
