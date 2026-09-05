/**
 * essai-ingestion.mjs — L'ingestion, éprouvée dans un vrai navigateur.
 *
 * Les 363 contrôles de `scripts/verifier-port-provenance.mjs` épinglent les
 * lecteurs du port au paquet Python. Ils ne disent rien du CÂBLAGE : chargement
 * du fichier, affichage des champs, rendu de la miniature, blocs de provenance.
 * C'est ce que cet essai vérifie, en pilotant la page réelle sur un fichier qui
 * porte délibérément tout — EXIF étendu, IFD1, GPS, C2PA, XMP, IPTC.
 *
 * Il vérifie aussi ce que la page NE DOIT PAS dire : aucune affirmation
 * d'authenticité, nulle part, sur un manifeste dont la signature n'est pas
 * vérifiée.
 *
 *     npm run essai:ingestion
 */
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
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

const ICI = dirname(fileURLToPath(import.meta.url));
const RACINE = dirname(dirname(ICI));
const PORT = process.env.PORT_ESSAI || '3111';
const NAVIGATEUR = process.env.CHROMIUM || undefined;
const IMAGE = join(RACINE, 'public', 'audit', 'image-test-ingestion.jpg');

if (!existsSync(IMAGE)) {
  console.log("Image d'essai absente — je la fabrique.");
  execFileSync('python3', [join(RACINE, 'scripts', 'image-test-ingestion.py')],
    { cwd: RACINE, stdio: 'inherit' });
}

const echecs = [];
const verifier = (nom, ok, detail) => {
  if (ok) console.log(`  ✓ ${nom}`);
  else { console.log(`  ✗ ${nom}${detail ? ` — ${detail}` : ''}`); echecs.push(nom); }
};

const nav = await chromium.launch(NAVIGATEUR ? { executablePath: NAVIGATEUR } : {});
const page = await nav.newPage({ viewport: { width: 1400, height: 1100 } });
page.on('pageerror', (e) => echecs.push('erreur JS : ' + e.message.slice(0, 120)));

await page.goto(`http://localhost:${PORT}/lab?sim=integrite-image`, { waitUntil: 'networkidle' });
await page.waitForSelector('input[type=file]', { state: 'attached', timeout: 20000 });
await page.setInputFiles('input[type=file]', IMAGE);
await page.waitForFunction(() => /JUMBF/.test(document.body.innerText), { timeout: 30000 });
await page.waitForTimeout(800);

const t = await page.locator('body').innerText();

// --- EXIF de base et champs d'ingestion ---
verifier('empreinte SHA-256 du fichier', /[0-9a-f]{64}/.test(t));
verifier('logiciel déclaré lu', t.includes('Adobe Photoshop 25.0'));
verifier('auteur et droits lus', t.includes('A. Photographe') && t.includes('Tous droits reserves'));
verifier('horodatages : prise de vue, numérisation, modification',
  t.includes('2026:09:05 10:14:22') && t.includes('2026:09:05 10:14:25') && t.includes('2026:09:05 11:02:33'));
verifier('paramètres de prise de vue', /ISO 200/.test(t) && /f\/2,8/.test(t) && /1\/250 s/.test(t));
verifier('focale et équivalent 35 mm', /24 mm/.test(t) && /36 mm/.test(t));
verifier('densité en DPI', /300.*DPI/.test(t.replace(/\s+/g, ' ')));
verifier('espace colorimétrique : code ET libellé', /1 — sRGB/.test(t));
verifier('mode d’exposition : code ET libellé', /1 — manuel/.test(t));
verifier('flash décodé bit à bit', /25 — déclenché, mode automatique/.test(t));
verifier('zoom numérique signalé (§15)', /zoom numérique appliqué/.test(t));

// --- GPS ---
verifier('coordonnées GPS lues', /50,933464/.test(t) && /1,750031/.test(t));
verifier('altitude GPS lue', /23 m/.test(t));
verifier('incertitude GPS déclarée non écrite', t.includes('non écrit par l’appareil'));

// --- Miniature ---
verifier('miniature affichée', (await page.locator('img[alt*="Miniature"]').count()) === 1);
verifier('empreinte de la miniature seule', /SHA-256 de la miniature seule/i.test(t));
verifier('taille et format de la miniature', /JPEG/.test(t) && /octets/.test(t));

// --- C2PA ---
verifier('conteneur C2PA identifié', t.includes('JPEG APP11 / JUMBF'));
verifier('manifeste et générateur déclarés', t.includes('essai-c2pa/0.1') && t.includes('ps256'));
verifier('actions de retouche listées',
  t.includes('c2pa.created') && t.includes('c2pa.color_adjustments') && t.includes('Retoucheur 2.4'));
verifier('assertions listées', t.includes('stds.schema-org.CreativeWork'));
verifier('signature déclarée présente mais NON vérifiée',
  t.includes('présent') && /non — voir ci-dessous/.test(t));
verifier('avertissement C2PA affiché en entier',
  /Aucune signature n[’']est vérifiée/.test(t) && t.includes('entièrement fabriqué'));

// --- XMP et IPTC ---
verifier('champs XMP relevés',
  t.includes('xmp:CreatorTool') && t.includes('Adobe Photoshop 25.0 (Windows)'));
verifier('enregistrements IPTC relevés',
  t.includes('Vue de la digue au lever du jour') && t.includes('Légende') && t.includes('Mots-clés'));

// --- Chaînes ---
verifier('marqueurs logiciels reconnus', /Marqueurs logiciels/i.test(t));
{
  const details = page.locator('summary', { hasText: /chaîne/ });
  if (await details.count() > 0) {
    await details.first().click();
    await page.waitForTimeout(300);
  }
  const t2 = await page.locator('body').innerText();
  verifier('chaînes listées avec leur offset', /\d{6} (asc|u16)/.test(t2));
}

// --- Ce que la page ne doit jamais dire ---
for (const affirmation of [
  'image authentique', 'est authentique', 'signature valide', 'provenance vérifiée',
  'authenticité confirmée', 'certifié conforme',
]) {
  verifier(`aucune affirmation « ${affirmation} »`, !t.toLowerCase().includes(affirmation));
}

// --- Le document JSON ---
{
  const attente = page.waitForEvent('download', { timeout: 15000 });
  await page.getByRole('button', { name: /Télécharger la synthèse/ }).click();
  const dl = await attente;
  const chemin = join(RACINE, 'public', 'audit', 'ingestion-export.json');
  await dl.saveAs(chemin);
  const doc = JSON.parse(readFileSync(chemin, 'utf8'));
  verifier('synthèse JSON téléchargée', true);
  for (const cle of ['file_info', 'exif', 'c2pa', 'thumbnail']) {
    verifier(`document : clé « ${cle} »`, cle in doc);
  }
  verifier('document : dimensions', JSON.stringify(doc.file_info.dimensions) === '[800,600]',
    JSON.stringify(doc.file_info.dimensions));
  verifier('document : espace colorimétrique', doc.file_info.color_space === 'sRGB');
  verifier('document : dpi scalaire', doc.file_info.dpi === 300);
  verifier('document : camera concaténée', doc.exif.camera === 'EssaiCorp Modele X');
  verifier('document : make et model séparés',
    doc.exif.make === 'EssaiCorp' && doc.exif.model === 'Modele X');
  verifier('document : vitesse d’obturation', doc.exif.settings.shutter_speed === '1/250');
  verifier('document : valeur exacte conservée',
    Math.abs(doc.exif.settings.shutter_speed_s - 1 / 250) < 1e-12);
  verifier('document : GPS avec altitude', doc.exif.gps.altitude_m === 23);
  verifier('document : incertitude GPS non comblée', doc.exif.gps.incertitude_m === null);
  verifier('document : miniature avec ses dimensions',
    doc.thumbnail.present === true && Array.isArray(doc.thumbnail.dimensions),
    JSON.stringify(doc.thumbnail.dimensions));
  verifier('document : C2PA actions', JSON.stringify(doc.c2pa.actions).includes('c2pa.cropped'));
  verifier('document : signature déclarée, non vérifiée',
    doc.c2pa.signature === 'essai-c2pa/0.1' && doc.c2pa.verified === false);

  // L'écart qui compte : aucun fuseau n'est inventé.
  const o = doc.exif.dates.original;
  verifier('document : horodatage sans fuseau inventé',
    o.offset_declare === false && !o.valeur.includes('+') && !o.valeur.endsWith('Z'),
    JSON.stringify(o));

  const texte = JSON.stringify(doc).toLowerCase();
  for (const affirmation of ['est authentique', 'signature valide', 'provenance vérifiée']) {
    verifier(`document : aucune affirmation « ${affirmation} »`, !texte.includes(affirmation));
  }
}

// --- Un fichier sans rien ne doit rien inventer ---
{
  const nu = join(RACINE, 'public', 'protocoles', 'image-test-metrologie.jpg');
  if (existsSync(nu)) {
    await page.setInputFiles('input[type=file]', nu);
    await page.waitForTimeout(1500);
    const t3 = await page.locator('body').innerText();
    verifier('fichier sans C2PA : dit que ce n’est pas un indice',
      t3.includes('Aucun manifeste C2PA') && t3.includes('ni une anomalie'));
    verifier('fichier sans C2PA : aucun manifeste inventé', !t3.includes('essai-c2pa/0.1'));
  }
}

await nav.close();
console.log(echecs.length === 0
  ? "\n✓ Câblage de l'ingestion vérifié de bout en bout, aucun échec."
  : `\n✗ ${echecs.length} échec(s) : ${echecs.join(' ; ')}`);
process.exit(echecs.length === 0 ? 0 : 1);
