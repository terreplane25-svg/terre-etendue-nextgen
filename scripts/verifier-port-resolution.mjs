/**
 * verifier-port-resolution.mjs — Épingle le port de l'analyse de résolution.
 *
 * Rejoue en TypeScript les vecteurs de
 * `src/lib/preuve-image/vecteurs-or-resolution.json`, champ par champ, y
 * compris les PHRASES affichées — caractère par caractère. Une divergence
 * d'apostrophe entre les deux implémentations s'est produite quatre fois dans
 * ce dépôt : elle est invisible à l'œil et change le texte affiché.
 *
 *     node scripts/verifier-port-resolution.mjs
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const DIR = join(RACINE, 'src', 'lib', 'preuve-image');
const VECTEURS = join(DIR, 'vecteurs-or-resolution.json');

const ecarts = [];
function comparer(sujet, champ, attendu, obtenu) {
  const a = attendu === undefined ? null : attendu;
  const o = obtenu === undefined ? null : obtenu;
  if (JSON.stringify(a) !== JSON.stringify(o)) {
    ecarts.push({ sujet, champ, attendu: JSON.stringify(a), obtenu: JSON.stringify(o) });
  }
}

/** L'analyse TypeScript remise dans la forme du Python, sans rien omettre. */
function enFormePython(r) {
  return {
    largeur_mesuree: r.largeurMesuree,
    hauteur_mesuree: r.hauteurMesuree,
    largeur_declaree: r.largeurDeclaree,
    hauteur_declaree: r.hauteurDeclaree,
    dimensions_coherentes: r.dimensionsCoherentes,
    motif_ecart: r.motifEcart,
    rapport: r.rapport ? [...r.rapport] : null,
    rapport_decimal: r.rapportDecimal,
    orientation: r.orientation,
    megapixels: r.megapixels,
    denomination: r.denomination,
    alignement_jpeg: r.alignementJpeg,
    ecran_rapproche: r.ecranRapproche,
    motif_aucun_ecran: r.motifAucunEcran,
  };
}

const dossier = mkdtempSync(join(tmpdir(), 'resolution-'));
try {
  execFileSync('npx', ['--no-install', 'tsc', join(DIR, 'resolution.ts'),
    '--target', 'ES2022', '--module', 'ES2022', '--moduleResolution', 'bundler',
    '--outDir', dossier, '--strict', '--lib', 'ES2022,DOM'], { cwd: RACINE, stdio: 'pipe' });

  // `resolution.ts` ne dépend d'aucun autre module : c'est de l'arithmétique.
  // Un import qui apparaîtrait signalerait un glissement de responsabilité.
  const compile = readFileSync(join(dossier, 'resolution.js'), 'utf8');
  const imports = compile.match(/from ['"]\.[^'"]*['"]/g) ?? [];
  if (imports.length > 0) {
    throw new Error(`resolution.ts a pris des dépendances : ${imports.join(', ')}`);
  }

  const R = await import(pathToFileURL(join(dossier, 'resolution.js')).href);
  const v = JSON.parse(readFileSync(VECTEURS, 'utf8'));
  let n = 0;

  const c = v.constantes;
  comparer('constantes', 'registre des écrans (vide)', c.ecrans_connus, R.ECRANS_CONNUS);
  comparer('constantes', 'dénominations', c.definitions_nommees, R.DEFINITIONS_NOMMEES);
  comparer('constantes', 'motif aucun écran', c.motif_aucun_ecran, R.MOTIF_AUCUN_ECRAN);
  comparer('constantes', 'motif dénomination', c.motif_denomination, R.MOTIF_DENOMINATION);
  comparer('constantes', 'motif alignement', c.motif_alignement, R.MOTIF_ALIGNEMENT);
  n += 5;

  for (const cas of v.cas) {
    const [lm, hm] = cas.mesuree;
    const [ld, hd] = cas.declaree;
    const obtenu = enFormePython(R.analyserResolution(lm, hm, ld, hd));
    for (const champ of Object.keys(cas.resolution)) {
      comparer(cas.nom, champ, cas.resolution[champ], obtenu[champ]);
      n += 1;
    }
    // Le port ne doit rien rendre de PLUS que le Python : un champ en trop est
    // une divergence de contrat, même s'il ne contredit aucune valeur.
    const enTrop = Object.keys(obtenu).filter((k) => !(k in cas.resolution));
    if (enTrop.length > 0) comparer(cas.nom, 'champs en trop', [], enTrop);
  }

  // Le rapport est refusé sur une dimension nulle des deux côtés : le rendre
  // donnerait une fraction infinie.
  for (const [l, h] of [[0, 100], [100, 0], [-1, 100]]) {
    let leve = false;
    try { R.rapportExact(l, h); } catch { leve = true; }
    if (!leve) {
      ecarts.push({ sujet: `rapport ${l}×${h}`, champ: 'refus', attendu: 'erreur levée', obtenu: 'aucune' });
    }
    n += 1;
  }

  if (ecarts.length > 0) {
    console.error(`\n✗ Le port TypeScript a dérivé du paquet Python : ${ecarts.length} écart(s) sur ${n} contrôles.\n`);
    for (const e of ecarts.slice(0, 15)) {
      console.error(`  ${e.sujet}\n    ${e.champ} :\n      attendu ${String(e.attendu).slice(0, 300)}\n      obtenu  ${String(e.obtenu).slice(0, 300)}`);
    }
    if (ecarts.length > 15) console.error(`  … et ${ecarts.length - 15} autre(s).`);
    console.error("\n  Corriger le Python d'abord, puis répercuter ici, puis régénérer les vecteurs.\n");
    process.exitCode = 1;
  } else {
    console.log(`✓ Port TypeScript conforme au paquet Python : ${n} contrôles, aucun écart.`);
    console.log(`  Vecteurs générés le ${v.genere_le}`);
  }
} finally {
  rmSync(dossier, { recursive: true, force: true });
}
