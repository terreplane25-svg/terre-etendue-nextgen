/**
 * verifier-port-simulation.mjs — Épingle la règle de lecture du simulateur.
 *
 * Rejoue en TypeScript les vecteurs de
 * `src/lib/visee-optique/vecteurs-or-simulation.json`, y compris les PHRASES
 * affichées au visiteur — caractère par caractère. Une divergence d'apostrophe
 * entre les deux implémentations s'est produite trois fois dans ce dépôt : elle
 * est invisible à l'œil et change le texte affiché.
 *
 *     node scripts/verifier-port-simulation.mjs
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const DIR = join(RACINE, 'src', 'lib', 'visee-optique');
const VECTEURS = join(DIR, 'vecteurs-or-simulation.json');

const ecarts = [];
function comparer(sujet, champ, attendu, obtenu) {
  const a = attendu === undefined ? null : attendu;
  const o = obtenu === undefined ? null : obtenu;
  if (JSON.stringify(a) !== JSON.stringify(o)) {
    ecarts.push({ sujet, champ, attendu: JSON.stringify(a), obtenu: JSON.stringify(o) });
  }
}

const dossier = mkdtempSync(join(tmpdir(), 'simulation-'));
try {
  // Le simulateur ne dépend plus du relief : un seul module à compiler.
  const modules = ['simulation'];
  execFileSync('npx', ['--no-install', 'tsc', ...modules.map((f) => join(DIR, `${f}.ts`)),
    '--target', 'ES2022', '--module', 'ES2022', '--moduleResolution', 'bundler',
    '--outDir', dossier, '--strict', '--lib', 'ES2022,DOM'], { cwd: RACINE, stdio: 'pipe' });

  // `simulation.ts` ne dépend plus d'aucun autre module : c'est la trace de la
  // suppression du relief, et elle se vérifie. Un import relatif qui
  // réapparaîtrait ramènerait le terrain par la porte de service — et il
  // ferait aussi échouer le chargement, tsc ne réécrivant pas les extensions
  // que l'ESM de Node exige.
  const compile = readFileSync(join(dossier, 'simulation.js'), 'utf8');
  const imports = compile.match(/from ['"]\.[^'"]*['"]/g) ?? [];
  if (imports.length > 0) {
    throw new Error(`simulation.ts a repris des dépendances : ${imports.join(', ')}`);
  }

  const S = await import(pathToFileURL(join(dossier, 'simulation.js')).href);
  const v = JSON.parse(readFileSync(VECTEURS, 'utf8'));
  let n = 0;

  const c = v.constantes;
  comparer('constantes', 'seuil', c.seuil_discrimination_fraction, S.SEUIL_DISCRIMINATION_FRACTION);
  comparer('constantes', 'k standard', c.k_standard, S.K_STANDARD);
  comparer('constantes', 'k min', c.k_enveloppe_min, S.K_ENVELOPPE_MIN);
  comparer('constantes', 'k max', c.k_enveloppe_max, S.K_ENVELOPPE_MAX);
  comparer('constantes', 'masque du modèle plat', c.masque_modele_plat_m, S.MASQUE_MODELE_PLAT_M);
  comparer('constantes', 'motif du seuil', c.motif_seuil, S.MOTIF_SEUIL);
  comparer('constantes', 'motif de la réfraction', c.motif_refraction, S.MOTIF_REFRACTION);
  comparer('constantes', 'motif sans relief', c.motif_sans_relief, S.MOTIF_SANS_RELIEF);
  n += 8;

  // Le module ne doit RIEN exporter du relief : un reliquat finirait par être
  // réutilisé, et le terrain reviendrait par la porte de service.
  for (const parti of ['pasEchantillonnageM', 'MOTIF_RESERVE_RELIEF', 'PAS_COURT_M',
    'PAS_MOYEN_M', 'PAS_LONG_M', 'SEUIL_DISTANCE_MOYENNE_M', 'SEUIL_DISTANCE_LONGUE_M']) {
    if (parti in S) {
      ecarts.push({ sujet: 'relief retiré', champ: parti, attendu: '(absent)', obtenu: 'encore exporté' });
    }
    n += 1;
  }

  for (const cas of v.cas) {
    const obtenu = S.juger(cas.masquee_base_m, cas.hauteur_cible_m);
    const attendu = cas.verdict;
    comparer(cas.nom, 'discriminante', attendu.discriminante, obtenu.discriminante);
    comparer(cas.nom, 'motif', attendu.motif, obtenu.motif);
    comparer(cas.nom, 'hauteur masquée base', attendu.hauteur_masquee_base_m, obtenu.hauteurMasqueeBaseM);
    comparer(cas.nom, 'fraction masquée base', attendu.fraction_masquee_base, obtenu.fractionMasqueeBase);
    comparer(cas.nom, 'hauteur masquée sur le plat', attendu.hauteur_masquee_plat_m, obtenu.hauteurMasqueePlatM);
    comparer(cas.nom, 'écart entre modèles', attendu.ecart_entre_modeles_m, obtenu.ecartEntreModelesM);
    comparer(cas.nom, 'seuil appliqué', attendu.seuil_applique, obtenu.seuilApplique);
    n += 7;
  }

  // Les refus, des deux côtés : une hauteur nulle rendrait l'infini, une
  // occultation négative trahirait une erreur d'appel.
  for (const [nom, appel] of [
    ['hauteur nulle', () => S.juger(10, 0)],
    ['occultation négative', () => S.juger(-1, 100)],
  ]) {
    let leve = false;
    try { appel(); } catch { leve = true; }
    if (!leve) ecarts.push({ sujet: nom, champ: 'refus', attendu: 'erreur levée', obtenu: 'aucune' });
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
