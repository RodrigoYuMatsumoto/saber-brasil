const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../..');
const author = 'Rodrigo Yú Matsumoto OAB/PE nº 1.338-B';
class ConsensusReporter {
  constructor() { this.rows = []; this.browser = null; }
  onTestEnd(test, result) {
    const version = result.attachments.find(row => row.name === 'browser-version');
    if (version?.body) this.browser = version.body.toString('utf8');
    this.rows.push({ item: test.title, status: result.status === 'passed' ? 'PASS' : 'FAIL',
      playwrightStatus: result.status, durationMs: result.duration,
      errors: result.errors.map(row => row.message?.replace(/\u001b\[[0-9;]*m/g, '') || ''),
      screenshots: result.attachments.filter(row => row.contentType === 'image/png' && row.path).map(row =>
        /^Consenso_V3_[A-Za-z0-9_]+\.png$/.test(row.name) ? 'evidence/' + row.name : path.relative(root, row.path).split(path.sep).join('/')) });
  }
  onEnd(result) {
    const output = path.join(root, 'evidence/Testes_Navegador_Consenso_V3.json');
    if (fs.existsSync(output)) {
      const folder = path.join(root, 'backups', 'browser_report_' + new Date().toISOString().replace(/[:.]/g, '_'));
      fs.mkdirSync(folder, { recursive: true }); fs.copyFileSync(output, path.join(folder, path.basename(output)));
    }
    const inputFiles = ['app.js', 'index.html', 'styles.css', 'assets/locales.json', 'data/brazil_topics.json', 'data/international.json', 'data/east_asia.json', 'data/translations.json'];
    const report = { metadata: { lang: 'pt-BR', author, keywords: author, manager: author,
      title: 'Testes headless do consenso v3', subject: 'Resultado PASS ou FAIL por item em computador e celular emulado' },
      checkedAt: new Date().toISOString(), status: result.status === 'passed' ? 'PASS' : 'FAIL',
      browser: { channel: process.env.SABER_BROWSER_CHANNEL || 'chromium', version: this.browser, headless: true,
                 serverPort: Number(process.env.SABER_TEST_PORT), isolation: 'fresh-loopback-server' },
      total: this.rows.length, passed: this.rows.filter(row => row.status === 'PASS').length,
      failed: this.rows.filter(row => row.status === 'FAIL').length, items: this.rows,
      sourceFiles: inputFiles.map(name => ({ path: name, sha256: crypto.createHash('sha256').update(fs.readFileSync(path.join(root, name))).digest('hex') })),
      notVerified: ['Gestos em aparelho físico.', 'Revisão docente ou linguística.', 'Validação B.9 por família arquitetural distinta.', 'Abertura do HTML pelo protocolo de arquivo.'] };
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n', 'utf8');
  }
}
module.exports = ConsensusReporter;
