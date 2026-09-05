/**
 * audit-mobile.mjs — Ce que les outils du Lab peuvent faire sur un téléphone.
 *
 * On mesure, on ne suppose pas. Mobile émulé (iPhone 13 : 390×844, DPR 3,
 * tactile) et processeur bridé ×4 par rapport à la machine qui joue ce test —
 * un milieu de gamme, pas un modèle de démonstration.
 *
 * Pour chaque outil : débordement horizontal, cibles tactiles sous 44 px,
 * erreurs JavaScript. Puis, pour ceux qui calculent : la durée réelle sur une
 * photo de téléphone ordinaire, confrontée au seuil de 3 s.
 *
 *     npm run audit:mobile
 *
 * Le bridage se règle par BRIDAGE=8 pour un appareil plus modeste.
 */
import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const requerir = createRequire(import.meta.url);
function trouverPlaywright() {
  try { return requerir.resolve('playwright'); } catch { /* pas en local */ }
  for (const base of ['/opt/node22/lib/node_modules', '/usr/lib/node_modules', '/usr/local/lib/node_modules']) {
    const p = `${base}/playwright/index.mjs`;
    if (existsSync(p)) return p;
  }
  throw new Error('Playwright introuvable : npm install --no-save playwright');
}
const pw = await import(trouverPlaywright());
const chromium = pw.chromium ?? pw.default?.chromium;
const devices = pw.devices ?? pw.default?.devices;

const ICI = dirname(fileURLToPath(import.meta.url));
const RACINE = dirname(dirname(ICI));
const PORT = process.env.PORT_ESSAI || '3111';
const BRIDAGE = Number(process.env.BRIDAGE || 4);
const NAVIGATEUR = process.env.CHROMIUM || undefined;
const PHOTO = join(RACINE, 'public', 'audit', 'photo-charge.jpg');
const SEUIL_MS = 3000;

const OUTILS = [
  ['visee-optique', 'A — Portion visible'],
  ['integrite-image', 'B — Vérificateur d’intégrité'],
  ['fiche-archive', 'C — Fiche et archive'],
  ['metrologie-image', 'D — Analyse d’image'],
  ['density', 'Simulateur de densité'],
  ['classifier', 'Fait / Modèle / Hypothèse'],
];

const nav = await chromium.launch(NAVIGATEUR ? { executablePath: NAVIGATEUR } : {});
const echecs = [];

async function ouvrir(id) {
  const ctx = await nav.newContext({ ...devices['iPhone 13'] });
  const page = await ctx.newPage();
  const cdp = await ctx.newCDPSession(page);
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: BRIDAGE });
  const erreurs = [];
  page.on('pageerror', (e) => erreurs.push(e.message.slice(0, 100)));
  await page.goto(`http://localhost:${PORT}/lab?sim=${id}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);
  return { ctx, page, erreurs };
}

const ligne = (c) => console.log('| ' + c.join(' | ') + ' |');

console.log(`\nMobile émulé : iPhone 13 (390×844, DPR 3, tactile) — processeur bridé ×${BRIDAGE}`);
console.log(`Seuil retenu pour un calcul : ${SEUIL_MS} ms\n`);
console.log('## Mise en page et interaction\n');
ligne(['Outil', 'Débordement horizontal', 'Cibles < 44 px', 'Erreurs JS']);
ligne(['---', '---', '---', '---']);

for (const [id, nom] of OUTILS) {
  const { ctx, page, erreurs } = await ouvrir(id);
  const m = await page.evaluate(() => {
    const de = document.documentElement;
    let pire = null;
    let large = de.clientWidth;
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect();
      if (r.width > large + 1) { large = r.width; pire = el.tagName.toLowerCase(); }
    }
    const petites = [...document.querySelectorAll('button, input, select, a')]
      .filter((el) => {
        const r = el.getBoundingClientRect();
        return r.width > 0 && r.height > 0 && r.height < 44;
      }).length;
    return { deborde: de.scrollWidth - de.clientWidth, pire, petites };
  });
  if (m.deborde > 0) echecs.push(`${nom} déborde de ${m.deborde} px`);
  if (erreurs.length) echecs.push(`${nom} : ${erreurs[0]}`);
  ligne([nom, m.deborde > 0 ? `**${m.deborde} px** (${m.pire})` : 'aucun',
    String(m.petites), erreurs.length ? erreurs[0] : 'aucune']);
  await ctx.close();
}

console.log('\n## Durée des calculs, sur une photo de 4032 × 3024 (12,2 Mpx, 3,4 Mo)\n');
ligne(['Opération', 'Outil', 'Durée', `Sous ${SEUIL_MS} ms`]);
ligne(['---', '---', '---', '---']);

if (!existsSync(PHOTO)) {
  console.log('*(photo de charge absente — je la fabrique)*');
  execFileSync('python3', [join(RACINE, 'scripts', 'photo-charge-mobile.py')],
    { cwd: RACINE, stdio: 'inherit' });
}
{
  for (const [id, nom, attendreCanevas] of [
    ['integrite-image', 'B', false],
    ['metrologie-image', 'D', true],
  ]) {
    const { ctx, page } = await ouvrir(id);
    const t0 = Date.now();
    await page.setInputFiles('input[type=file]', PHOTO);
    await page.waitForFunction(() => /[0-9a-f]{64}/.test(document.body.innerText), { timeout: 120000 });
    const tHash = Date.now() - t0;
    ligne([`Empreinte SHA-256 + EXIF + affichage`, nom, `${tHash} ms`, tHash < SEUIL_MS ? 'oui' : '**NON**']);
    if (tHash >= SEUIL_MS) echecs.push(`${nom} : empreinte en ${tHash} ms`);

    if (attendreCanevas) {
      const t1 = Date.now();
      await page.waitForFunction(() => {
        const c = document.querySelector('canvas');
        return c && c.getBoundingClientRect().width > 10;
      }, { timeout: 120000 });
      const tCanevas = Date.now() - t1;
      ligne(['Décodage et rendu du canevas', nom, `${tCanevas} ms`, tCanevas < SEUIL_MS ? 'oui' : '**NON**']);
      if (tCanevas >= SEUIL_MS) echecs.push(`${nom} : canevas en ${tCanevas} ms`);

      // Le pointé tactile complet : appui, retouche au pixel, validation.
      const cv = page.locator('canvas').first();
      await cv.scrollIntoViewIfNeeded();
      await page.waitForTimeout(400);
      const b = await cv.boundingBox();
      const t2 = Date.now();
      await page.touchscreen.tap(b.x + b.width / 2, b.y + b.height * 0.6);
      await page.waitForFunction(() => /Valider ce pointé/.test(document.body.innerText), { timeout: 30000 })
        .catch(() => { echecs.push('D : le pointé au doigt ne produit rien'); });
      const tPointe = Date.now() - t2;
      ligne(['Pointé au doigt → barre de validation', nom, `${tPointe} ms`, tPointe < SEUIL_MS ? 'oui' : '**NON**']);

      const texte = await page.locator('body').innerText();
      const res = texte.match(/vaut\s*([\d,.]+)\s*px d.image/i);
      const loupe = (await page.locator('canvas').count()) > 1;
      console.log('');
      console.log('## Précision de pointé, mesurée sur le canevas rendu\n');
      ligne(['Grandeur', 'Valeur']);
      ligne(['---', '---']);
      ligne(['Un pixel d’écran vaut', res ? `${res[1]} px d’image` : '—']);
      ligne(['Sous la loupe ×8', res ? `${(Number(res[1].replace(',', '.')) / 8).toFixed(2)} px d’image` : '—']);
      ligne(['Loupe affichée au doigt', loupe ? 'oui' : '**non**']);
      if (!loupe) echecs.push('D : la loupe ne s’affiche pas au doigt');

      // Retouche au pixel, puis validation.
      const avant = texte.match(/y = ([\d.]+) px/)?.[1];
      await page.getByRole('button', { name: 'Décaler le pointé de -1 pixel' }).click();
      await page.waitForTimeout(300);
      const apres = (await page.locator('body').innerText()).match(/y = ([\d.]+) px/)?.[1];
      const retoucheOk = avant && apres && Math.abs(Number(avant) - Number(apres) - 1) < 1e-6;
      ligne(['Retouche au pixel', retoucheOk ? `${avant} → ${apres}` : '**inopérante**']);
      if (!retoucheOk) echecs.push('D : la retouche au pixel ne fonctionne pas');

      await page.getByRole('button', { name: /Valider ce pointé/ }).click();
      await page.waitForTimeout(400);
      const valide = /Ligne d.horizon · [\d.]+ px/.test(await page.locator('body').innerText());
      ligne(['Validation du pointé', valide ? 'enregistré' : '**perdu**']);
      if (!valide) echecs.push('D : le pointé validé n’est pas enregistré');
    }
    await ctx.close();
  }
}

await nav.close();
console.log('');
if (echecs.length === 0) {
  console.log('✓ Aucun blocage sur mobile : mise en page, pointé tactile et calculs sous le seuil.');
} else {
  console.log(`✗ ${echecs.length} point(s) à reprendre :`);
  for (const e of echecs) console.log(`  · ${e}`);
  process.exitCode = 1;
}
