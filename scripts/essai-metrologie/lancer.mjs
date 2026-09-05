/**
 * lancer.mjs — Construit le site, le sert, joue l'essai de bout en bout, arrête tout.
 *
 *     npm run essai:metrologie
 *
 * L'essai lui-même est dans `essai-bout-en-bout.mjs` ; ce script ne fait que
 * l'entourer, pour qu'une seule commande suffise et qu'aucun serveur ne reste
 * en vie derrière lui.
 *
 * Playwright n'est pas une dépendance du site — il ne sert qu'ici. Le script
 * le cherche là où il peut être, et dit quoi faire s'il est absent, plutôt que
 * d'échouer sur une trace d'import.
 */
import { execFileSync, spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ICI = dirname(fileURLToPath(import.meta.url));
const RACINE = dirname(dirname(ICI));
const PORT = process.env.PORT_ESSAI || '3111';

const require = createRequire(import.meta.url);
let playwright = null;
try {
  playwright = dirname(require.resolve('playwright/package.json'));
} catch {
  for (const base of ['/opt/node22/lib/node_modules', '/usr/lib/node_modules', '/usr/local/lib/node_modules']) {
    if (existsSync(join(base, 'playwright', 'package.json'))) { playwright = join(base, 'playwright'); break; }
  }
}
if (!playwright) {
  console.error(
    'Playwright introuvable. Il ne sert qu’à cet essai et n’est pas une dépendance du site :\n'
    + '    npm install --no-save playwright && npx playwright install chromium\n',
  );
  process.exit(2);
}

for (const [chemin, generateur] of [
  [join(RACINE, 'public', 'protocoles', 'image-test-metrologie.jpg'), 'image-test-metrologie.py'],
  [join(RACINE, 'public', 'audit', 'image-test-ingestion.jpg'), 'image-test-ingestion.py'],
]) {
  if (!existsSync(chemin)) {
    console.log(`Image de test absente — je la fabrique (${generateur}).`);
    execFileSync('python3', [join(RACINE, 'scripts', generateur)], { cwd: RACINE, stdio: 'inherit' });
  }
}

if (!existsSync(join(RACINE, '.next', 'BUILD_ID'))) {
  console.log('Site non construit — npx next build.');
  execFileSync('npx', ['next', 'build'], { cwd: RACINE, stdio: 'inherit' });
}

const serveur = spawn('npx', ['next', 'start', '-p', PORT], { cwd: RACINE, stdio: 'ignore' });
const arreter = () => { try { serveur.kill('SIGTERM'); } catch { /* déjà mort */ } };
process.on('exit', arreter);
process.on('SIGINT', () => { arreter(); process.exit(130); });

async function attendre() {
  for (let i = 0; i < 60; i += 1) {
    try {
      const r = await fetch(`http://localhost:${PORT}/lab`);
      if (r.ok) return true;
    } catch { /* pas encore là */ }
    await new Promise((r) => setTimeout(r, 500));
  }
  return false;
}

if (!(await attendre())) {
  console.error(`Le serveur n’a pas répondu sur le port ${PORT}.`);
  arreter();
  process.exit(1);
}

// Quel essai jouer : `npm run essai:metrologie` ou `npm run essai:ingestion`.
const ESSAI = process.argv[2] ?? 'essai-bout-en-bout.mjs';

let code = 0;
try {
  execFileSync(process.execPath, [join(ICI, ESSAI)], {
    cwd: RACINE,
    stdio: 'inherit',
    env: { ...process.env, PORT_ESSAI: PORT, NODE_PATH: dirname(playwright) },
  });
} catch (err) {
  code = err.status ?? 1;
}
arreter();
process.exit(code);
