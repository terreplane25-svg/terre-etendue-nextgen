/**
 * verifier-geocodage-ign.mjs — Éprouve le géocodage SANS réseau.
 *
 * CE QUE CE CONTRÔLE ÉTABLIT, ET CE QU'IL N'ÉTABLIT PAS
 * ────────────────────────────────────────────────────
 * Il établit : qu'un couple de coordonnées est lu SANS qu'aucune requête ne
 * parte — c'est la propriété qui garantit que la simulation tourne même quand
 * le service est en panne —, que la requête est mise en forme selon le contrat
 * publié, et qu'une réponse non conforme est REFUSÉE au lieu d'être comblée.
 *
 * Il n'établit PAS que le service de l'IGN répond ce qu'on croit. Cet
 * environnement n'a pas d'accès sortant vers data.geopf.fr : le service n'a
 * jamais été interrogé. C'est une limite réelle, elle est écrite dans le
 * module et affichée dans l'interface.
 *
 *     node scripts/verifier-geocodage-ign.mjs
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const DIR = join(RACINE, 'src', 'lib', 'visee-optique');

let echecs = 0;
let controles = 0;
function verifier(nom, condition, detail = '') {
  controles += 1;
  if (!condition) {
    echecs += 1;
    console.error(`  ✗ ${nom}${detail ? `\n      ${detail}` : ''}`);
  }
}
async function leve(nom, appel, motif = '') {
  controles += 1;
  try {
    await appel();
    echecs += 1;
    console.error(`  ✗ ${nom} : aucune erreur levée`);
  } catch (err) {
    if (motif && !String(err.message).includes(motif)) {
      echecs += 1;
      console.error(`  ✗ ${nom} : le message ne mentionne pas « ${motif} »\n      ${err.message}`);
    }
  }
}

/** Un fetch qui compte ses appels : c'est ce compteur qui prouve l'absence de requête. */
function fauxFetch(reponse) {
  const appels = [];
  const f = async (url) => {
    appels.push(url);
    return typeof reponse === 'function' ? reponse(url) : reponse;
  };
  f.appels = appels;
  return f;
}
const json = (doc, ok = true, status = 200) => ({
  ok, status, json: async () => doc,
});

const dossier = mkdtempSync(join(tmpdir(), 'geoc-'));
try {
  execFileSync('npx', ['--no-install', 'tsc', join(DIR, 'geocodage-ign.ts'),
    '--target', 'ES2022', '--module', 'ES2022', '--moduleResolution', 'bundler',
    '--outDir', dossier, '--strict', '--lib', 'ES2022,DOM'], { cwd: RACINE, stdio: 'pipe' });
  const G = await import(pathToFileURL(join(dossier, 'geocodage-ign.js')).href);

  // ── 1. Les coordonnées se lisent sans réseau ─────────────────────────────
  //
  // C'est LA propriété qui compte : elle garantit que la simulation tourne sur
  // les coordonnées saisies, service en panne ou non.
  for (const [saisie, lat, lon] of [
    ['50.94642, 1.75305', 50.94642, 1.75305],
    ['50.94642 1.75305', 50.94642, 1.75305],
    ['50.94642;1.75305', 50.94642, 1.75305],
    ['50,94642 1,75305', 50.94642, 1.75305],
    ['-33.9 18.4', -33.9, 18.4],
    ['0 0', 0, 0],
  ]) {
    const p = G.lireCoordonnees(saisie);
    verifier(`« ${saisie} » lu comme coordonnées`,
      p !== null && Math.abs(p.latitude - lat) < 1e-12 && Math.abs(p.longitude - lon) < 1e-12,
      p === null ? 'rendu null' : `${p.latitude} / ${p.longitude}`);
  }

  const sansAppel = fauxFetch(json({}));
  const direct = await G.resoudrePosition('50.94642, 1.75305', sansAppel);
  verifier('aucune requête pour un couple de coordonnées', sansAppel.appels.length === 0,
    `${sansAppel.appels.length} appel(s)`);
  verifier('origine déclarée comme saisie', direct.origine === 'coordonnées saisies');

  // Ce qui n'est PAS un couple de coordonnées doit rendre null, pour être
  // traité comme une adresse — pas être forcé en position.
  for (const saisie of ['Sangatte', '12 rue de la Mer, Calais', '', '50.94642',
    '91 0', '0 181', 'abc def']) {
    verifier(`« ${saisie} » n'est pas lu comme coordonnées`,
      G.lireCoordonnees(saisie) === null);
  }

  // ── 2. La requête suit le contrat publié ─────────────────────────────────
  const reponseValide = json({
    features: [{
      geometry: { type: 'Point', coordinates: [1.75305, 50.94642] },
      properties: { label: 'Sangatte, 62231' },
    }],
  });
  const f2 = fauxFetch(reponseValide);
  const p2 = await G.resoudrePosition('Sangatte', f2);
  verifier('une seule requête pour une adresse', f2.appels.length === 1);
  verifier('racine du service conforme', String(f2.appels[0]).startsWith(G.RACINE_GEOCODAGE));
  verifier('la saisie est encodée dans la requête', String(f2.appels[0]).includes('q=Sangatte'));
  // GeoJSON range la longitude AVANT la latitude. Les inverser placerait
  // Sangatte au large de la Somalie sans que rien ne le signale.
  verifier('longitude et latitude lues dans le bon ordre',
    Math.abs(p2.latitude - 50.94642) < 1e-12 && Math.abs(p2.longitude - 1.75305) < 1e-12,
    `${p2.latitude} / ${p2.longitude}`);
  verifier('libellé du service conservé', p2.libelle === 'Sangatte, 62231');
  verifier('origine déclarée comme géocodage', p2.origine.includes('IGN'));

  // ── 3. Une réponse non conforme est REFUSÉE, jamais comblée ──────────────
  await leve('aucun résultat', () => G.resoudrePosition('xyz', fauxFetch(json({ features: [] }))),
    'Aucune adresse trouvée');
  await leve('features absent', () => G.resoudrePosition('xyz', fauxFetch(json({}))),
    'Aucune adresse trouvée');
  await leve('coordonnées manquantes',
    () => G.resoudrePosition('xyz', fauxFetch(json({ features: [{ geometry: {} }] }))),
    'Aucune adresse trouvée');
  await leve('coordonnée non numérique',
    () => G.resoudrePosition('xyz', fauxFetch(json({
      features: [{ geometry: { coordinates: ['1.75', '50.94'] } }],
    }))), 'Aucune adresse trouvée');
  await leve('latitude hors bornes',
    () => G.resoudrePosition('xyz', fauxFetch(json({
      features: [{ geometry: { coordinates: [1.75, 950.94] } }],
    }))), 'Aucune adresse trouvée');
  await leve('service en erreur',
    () => G.resoudrePosition('xyz', fauxFetch(json({}, false, 503))), '503');
  await leve('service injoignable',
    () => G.resoudrePosition('xyz', async () => { throw new Error('ECONNREFUSED'); }),
    'injoignable');
  await leve('saisie vide', () => G.resoudrePosition('   ', fauxFetch(json({}))),
    'Aucune position saisie');

  // Chaque message d'échec doit dire quoi faire : saisir les coordonnées.
  // Sans cela, le visiteur reste devant un mur.
  for (const [nom, appel] of [
    ['service en erreur', () => G.resoudrePosition('xyz', fauxFetch(json({}, false, 503)))],
    ['service injoignable', () => G.resoudrePosition('xyz', async () => { throw new Error('x'); })],
    ['aucun résultat', () => G.resoudrePosition('xyz', fauxFetch(json({ features: [] })))],
  ]) {
    controles += 1;
    try {
      await appel();
      echecs += 1;
    } catch (err) {
      if (!String(err.message).includes('coordonnées exactes')) {
        echecs += 1;
        console.error(`  ✗ ${nom} : le message n'indique pas la sortie de secours\n      ${err.message}`);
      }
    }
  }

  if (echecs === 0) {
    console.log(`✓ Géocodage : ${controles} contrôles, aucun écart.`);
    console.log('  Réserve : le service de l’IGN n’a jamais été interrogé depuis cet');
    console.log('  environnement (pas d’accès sortant). Seul le contrat est éprouvé.');
  } else {
    console.error(`\n✗ ${echecs} écart(s) sur ${controles} contrôles.`);
    process.exitCode = 1;
  }
} finally {
  rmSync(dossier, { recursive: true, force: true });
}
