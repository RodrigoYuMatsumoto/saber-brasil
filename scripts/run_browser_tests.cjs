/* Escolhe uma porta local livre para não reutilizar servidores de outros colaboradores. */
const net = require('node:net');
const path = require('node:path');
const { spawn } = require('node:child_process');
async function freePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer(); server.on('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const port = server.address().port;
      server.close(error => error ? reject(error) : resolve(port));
    });
  });
}
async function main() {
  const port = process.env.SABER_TEST_PORT ? Number(process.env.SABER_TEST_PORT) : await freePort();
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('Porta de teste inválida.');
  const cli = path.join(path.dirname(require.resolve('@playwright/test')), 'cli.js');
  const child = spawn(process.execPath, [cli, 'test', ...process.argv.slice(2)], {
    cwd: path.resolve(__dirname, '..'), env: { ...process.env, SABER_TEST_PORT: String(port) },
    stdio: 'inherit', windowsHide: true
  });
  child.on('error', error => { console.error(error.message); process.exitCode = 1; });
  child.on('exit', (code, signal) => { process.exitCode = code ?? (signal ? 1 : 0); });
}
main().catch(error => { console.error(error.message); process.exitCode = 1; });
