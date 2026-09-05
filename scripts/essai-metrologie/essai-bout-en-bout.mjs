/**
 * essai-bout-en-bout.mjs — L'outil D, éprouvé dans un vrai navigateur.
 *
 * Les 786 contrôles de `scripts/verifier-port-metrologie.mjs` épinglent les
 * formules du port au paquet Python. Ils ne disent rien du CÂBLAGE : chargement
 * du fichier, empreinte, lecture EXIF, saisie, clics sur le canevas, tableau de
 * bord, exports. C'est ce que cet essai vérifie, en pilotant la page réelle.
 *
 * La scène est connue d'avance : `scripts/image-test-metrologie.py` fabrique un
 * diagramme dont la cible est dessinée aux ordonnées qu'un k choisi impose. Le
 * navigateur doit retrouver ce k — et c'est le paquet Python, la référence, qui
 * juge son résultat, à partir des pointés que le navigateur a RÉELLEMENT
 * enregistrés. Comparer à un relevé idéal mesurerait la précision du pilote
 * automatique, pas celle de l'outil : un clic est quantifié au pixel de
 * l'affichage, réduit par rapport à l'image.
 *
 * Prérequis : le site construit et servi.
 *
 *     npx next build && npx next start -p 3111 &
 *     node scripts/essai-metrologie/essai-bout-en-bout.mjs
 *
 * Ou, tout en un :
 *     npm run essai:metrologie
 */
import { createRequire } from 'node:module';
import { existsSync } from 'node:fs';

// Playwright ne sert qu'à cet essai et n'est pas une dépendance du site :
// on le cherche là où il peut être plutôt que de l'exiger dans node_modules.
const requerir = createRequire(import.meta.url);
function trouverPlaywright() {
  try { return requerir.resolve('playwright'); } catch { /* pas en local */ }
  for (const base of ['/opt/node22/lib/node_modules', '/usr/lib/node_modules', '/usr/local/lib/node_modules']) {
    const p = `${base}/playwright/index.mjs`;
    if (existsSync(p)) return p;
  }
  throw new Error(
    'Playwright introuvable :\n'
    + '    npm install --no-save playwright && npx playwright install chromium',
  );
}
// Selon l'endroit où il est trouvé, Playwright arrive en module ES ou en
// CommonJS enveloppé : dans le second cas les exports sont sous `default`.
const modulePlaywright = await import(trouverPlaywright());
const chromium = modulePlaywright.chromium ?? modulePlaywright.default?.chromium;
if (!chromium) throw new Error('Playwright trouvé mais sans export `chromium`.');
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { execFileSync } from 'node:child_process';

import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ICI = dirname(fileURLToPath(import.meta.url));
const RACINE = dirname(dirname(ICI));
const PORT = process.env.PORT_ESSAI || '3111';
const NAVIGATEUR = process.env.CHROMIUM || undefined;
const attendu = JSON.parse(readFileSync(
  `${RACINE}/outils/outil-D-metrologie-image/tests/releve-attendu.json`, 'utf8'));

const echecs = [];
const verifier = (nom, ok, detail) => {
  if (ok) console.log(`  ✓ ${nom}`);
  else { console.log(`  ✗ ${nom} — ${detail}`); echecs.push(nom); }
};

const nav = await chromium.launch(NAVIGATEUR ? { executablePath: NAVIGATEUR } : {});
const page = await nav.newPage({ viewport: { width: 1500, height: 1100 } });
page.on('pageerror', (e) => { echecs.push('erreur JS : ' + e.message); });

await page.goto(`http://localhost:${PORT}/lab?sim=metrologie-image`, { waitUntil: 'networkidle' });
await page.waitForSelector('input[type=file]', { timeout: 20000 });

// 1. Chargement du fichier
await page.setInputFiles('input[type=file]', `${RACINE}/${attendu.image}`);
await page.waitForSelector('canvas', { timeout: 20000 });

const texte = () => page.locator('body').innerText();
let t = await texte();
verifier('empreinte SHA-256 affichée', /SHA-256\s+[0-9a-f]{64}/.test(t), t.slice(0, 200));
verifier('EXIF lu et fabricant affiché', t.includes('Terre Etendue (diagramme calcule)'), 'EXIF absent');
verifier('dimensions livrées affichées',
  t.includes(`${attendu.appareil.largeur_native_px} × ${attendu.appareil.hauteur_native_px} px livrés`), '—');

// 2. Adoption explicite de l'EXIF — rien ne doit avoir bougé avant ce clic
const focaleAvant = await page.locator('input').nth(0).inputValue();
await page.getByRole('button', { name: /Adopter ces valeurs/ }).click();

// 3. Saisie. Les champs sont repérés par leur libellé, via le conteneur.
async function remplir(cle, valeur, source, incertitude) {
  await page.locator(`[data-champ="${cle}-valeur"]`).fill(valeur);
  if (incertitude !== undefined) {
    await page.locator(`[data-champ="${cle}-incertitude"]`).fill(incertitude);
  }
  await page.locator(`[data-champ="${cle}-source"]`).fill(source);
}

const SRC = 'Image de test — scène construite par scripts/image-test-metrologie.py';
await remplir('largeurCapteurMm', String(attendu.appareil.largeur_capteur_mm), SRC);
await remplir('focaleMm', String(attendu.appareil.focale_mm), SRC);
await remplir('largeurNativePx', String(attendu.appareil.largeur_native_px), SRC);
await remplir('hauteurNativePx', String(attendu.appareil.hauteur_native_px), SRC);
await remplir('distanceKm', String(attendu.scene.D_km), SRC, '0');
await remplir('altitudeObsM', String(attendu.scene.h_obs_m), SRC, '0');
await remplir('hauteurCibleM', String(attendu.scene.H_m), SRC, '0');
await remplir('altitudeBaseM', String(attendu.scene.z_b_m), SRC, '0');

// 4. Les trois clics, aux ordonnées exactes du relevé attendu.
const cv = page.locator('canvas').first();
await cv.scrollIntoViewIfNeeded();
await page.waitForTimeout(200);
// `locator.click({position})` arrondit au pixel CSS ; le canevas étant affiché
// réduit, un pixel CSS vaut ici plusieurs pixels d'image. On passe donc par la
// souris en coordonnées absolues flottantes, pour que le pointé du pilote soit
// aussi fin que celui d'un opérateur à la loupe.
// Le cadre est relu AVANT CHAQUE CLIC : la fenêtre de l'outil défile, et un
// cadre mesuré une fois pour toutes devient faux dès le premier pointé. C'est
// ce qui décalait les clics de 1,4 px au jet précédent.
const cliquer = async (yImage) => {
  const b = await cv.boundingBox();
  const echelle = b.width / attendu.appareil.largeur_native_px;
  await page.mouse.click(b.x + b.width * 0.62, b.y + yImage * echelle);
  await page.waitForTimeout(120);
};
const p = attendu.pointes_a_cliquer;
await cliquer(p.y_horizon);
await cliquer(p.y_base);
await cliquer(p.y_sommet);
await page.waitForTimeout(400);

const clicsLus = await page.locator('button').filter({ hasText: /px$/ }).allInnerTexts();
console.log('  pointés enregistrés :', clicsLus.join(' | '));

// 5. Le tableau de bord
t = await texte();
const valeurLigne = async (cle) => {
  const l = page.locator(`[data-valeur="${cle}"]`);
  return (await l.count()) === 0 ? null : (await l.first().innerText()).trim();
};
const nombreLigne = async (cle) => {
  const v = await valeurLigne(cle);
  return v === null ? null : Number(v.replace(/[\s\u202f\u00a0]/g, '').replace(',', '.'));
};
const kAffiche = await nombreLigne('k');
verifier('k affiché dans le tableau de bord', kAffiche !== null && Number.isFinite(kAffiche),
  `lu ${await valeurLigne('k')}`);
verifier('statut « déterminé »', (await valeurLigne('statut')) === 'déterminé',
  `lu ${await valeurLigne('statut')}`);
verifier('régime « réfraction standard »', t.includes(attendu.attendu.regime), '—');
verifier('contrôle horizon satisfait', /Contrôle\s*\n?\s*satisfait/.test(t), '—');
verifier("bloc « ce que ça n'établit pas » présent",
  t.includes('Le modèle sphérique est une entrée de ce calcul'), '—');
verifier('aucun verdict sur la forme de la Terre',
  !/plate|sphérique est (?:donc )?(?:confirmé|prouvé)|prouve que/i.test(t), '—');



// 6. Le refus : une source effacée doit bloquer le calcul.
{
  const source = page.locator('[data-champ="distanceKm-source"]');
  await source.fill('');
  await page.waitForTimeout(300);
  const t2 = await page.locator('body').innerText();
  verifier('source effacée → le calcul se bloque et le dit',
    t2.includes('Le calcul attend encore') && t2.includes('n’entre pas dans le calcul'), '—');
  await source.fill(SRC);
  await page.waitForTimeout(300);
}

// 7. Les deux exports
const dossier = mkdtempSync(join(tmpdir(), 'essai-metrologie-'));
for (const [nom, motif] of [['PNG', /image annotée/], ['JSON', /synthèse/]]) {
  const attente = page.waitForEvent('download', { timeout: 15000 });
  await page.getByRole('button', { name: motif }).click();
  const dl = await attente;
  const chemin = `${dossier}/export-${nom.toLowerCase()}`;
  await dl.saveAs(chemin);
  verifier(`export ${nom} téléchargé (${dl.suggestedFilename()})`, true);
  if (nom === 'JSON') {
    const doc = JSON.parse(readFileSync(chemin, 'utf8'));
    verifier('JSON : empreinte reportée', /^[0-9a-f]{64}$/.test(doc['traçabilité'].sha256), '—');
    verifier('JSON : les quatre sources présentes',
      Object.values(doc['traçabilité'].sources).filter((s) => s && s.length > 0).length >= 5, '—');
    // Ce que l'on attend du k rendu par le navigateur n'est PAS qu'il retombe
    // sur le k de construction : un clic piloté est quantifié au pixel CSS, le
    // canevas est affiché réduit, et un pixel d'image vaut ici ~0,003 sur k.
    // Ce que l'on attend, c'est que l'ENVELOPPE déclarée par l'outil contienne
    // la valeur de construction — c'est à cela qu'une enveloppe sert, et c'est
    // une propriété de l'outil, pas du pilote.
    const dansEnveloppe = doc.refraction.k_min <= attendu.k_de_construction
      && attendu.k_de_construction <= doc.refraction.k_max;
    verifier(`JSON : l'enveloppe [${doc.refraction.k_min} ; ${doc.refraction.k_max}] contient le k de construction (${attendu.k_de_construction})`,
      dansEnveloppe, `k rendu ${doc.refraction.k}`);
    const dansEnveloppeEntrees = doc.refraction.enveloppe_entrees.k_min <= attendu.k_de_construction
      && attendu.k_de_construction <= doc.refraction.enveloppe_entrees.k_max;
    verifier("JSON : l'enveloppe pointé + entrées le contient aussi", dansEnveloppeEntrees, '—');
    verifier('JSON : écart horizon/base prédit nul',
      Math.abs(doc.controle_horizon_base.ecart_predit_px) < 0.05, `lu ${doc.controle_horizon_base.ecart_predit_px}`);
    verifier("JSON : ce que ça n'établit pas, trois entrées",
      doc.ce_que_ca_n_etablit_pas.length === 3, '—');
  }
}

await page.screenshot({ path: `${dossier}/metrologie-image.png`, fullPage: true });

// 8. La contre-épreuve : Python recalcule à partir des pointés RÉELLEMENT
// enregistrés par l'interface. Le clic d'un pilote automatique ne tombe pas au
// pixel exact — l'écran affiche l'image réduite — et comparer à un relevé idéal
// mesurerait la précision de Playwright, pas celle de l'outil. La référence
// juge donc le navigateur sur ce que le navigateur a effectivement relevé.
const doc = JSON.parse(readFileSync(`${dossier}/export-json`, 'utf8'));
writeFileSync(`${dossier}/pointes-releves.json`, JSON.stringify({
  y_horizon: doc['relevé'].y_horizon_px,
  y_base: doc['relevé'].y_base_px,
  y_sommet: doc['relevé'].y_sommet_px,
  sigma_px: doc['relevé'].sigma_pointe_px,
}));
const py = execFileSync(
  `${RACINE}/outils/.venv/bin/python`,
  [join(ICI, 'contre-epreuve.py'), `${dossier}/pointes-releves.json`],
  { encoding: 'utf8' },
);
const ref = JSON.parse(py);
const ecartK = Math.abs(ref.k - doc.refraction.k);
verifier(`contre-épreuve Python : k = ${ref.k.toFixed(6)} contre ${doc.refraction.k} au navigateur (écart ${ecartK.toExponential(1)})`,
  ecartK < 1e-6, `écart ${ecartK}`);
const ecartAngle = Math.abs(ref.angle_arcsec - Number((await valeurLigne('angleEmergent')).split('±')[0].replace(/[\s\u202f\u00a0]/g, '').replace(',', '.')));
verifier(`contre-épreuve Python : angle = ${ref.angle_arcsec.toFixed(3)}″ (écart affiché ${ecartAngle.toExponential(1)}″)`,
  ecartAngle < 0.01, `écart ${ecartAngle}`);
verifier(`contre-épreuve Python : hauteur émergente = ${ref.hauteur_m.toFixed(3)} m`,
  Math.abs(ref.hauteur_m - doc.mesure.hauteur_emergente_m) < 1e-3,
  `Python ${ref.hauteur_m}, navigateur ${doc.mesure.hauteur_emergente_m}`);
// Le pointé du pilote, mesuré : c'est lui qui explique l'écart au k de
// construction, et non un défaut de l'outil.
const ideal = attendu.pointes_a_cliquer;
const erreurPointe = Math.max(
  Math.abs(doc['relevé'].y_base_px - ideal.y_base),
  Math.abs(doc['relevé'].y_sommet_px - ideal.y_sommet),
);
const sensibilite = Math.abs(ref.k - attendu.k_de_construction) / Math.max(erreurPointe, 1e-9);
console.log(`  pointé du pilote à ${erreurPointe.toFixed(2)} px de l'idéal — soit ${sensibilite.toFixed(4)} sur k par pixel`);
verifier(`l'écart au k de construction s'explique par le pointé (${erreurPointe.toFixed(2)} px, quantification de l'affichage réduit)`,
  erreurPointe < 5 && Math.abs(ref.k - attendu.k_de_construction) < 0.02,
  `pointé ${erreurPointe} px, écart k ${Math.abs(ref.k - attendu.k_de_construction)}`);

await nav.close();
rmSync(dossier, { recursive: true, force: true });

console.log(echecs.length === 0
  ? `\n✓ Câblage de l'interface vérifié de bout en bout, aucun échec.`
  : `\n✗ ${echecs.length} échec(s) : ${echecs.join(' ; ')}`);
process.exit(echecs.length === 0 ? 0 : 1);
