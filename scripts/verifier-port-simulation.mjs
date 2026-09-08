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
import { mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
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

/**
 * Une analyse de relief réduite à ce que la règle de lecture consulte —
 * la même fabrication que `analyse()` côté Python.
 */
function analyse(masqueeM, obstacle, reliefEvalue) {
  const o = obstacle
    ? { distanceM: 500, altitudeTerrainM: 50, altitudeViseeM: 40, manqueM: 10 }
    : null;
  const H = 100;
  return {
    modele: 'sphérique',
    rayonEffectifM: 7_000_000,
    hauteurOccultéeCourbureM: masqueeM,
    fractionVisibleCourbure: Math.min(1, Math.max(0, (H - masqueeM) / H)),
    reliefEvalue,
    motifReliefNonEvalue: reliefEvalue ? null : 'non évalué',
    obstacles: o ? [o] : [],
    obstacleLePlusGenant: o,
    margeMinimaleM: o ? -10 : 5,
    distanceMargeMinimaleM: 500,
  };
}

const dossier = mkdtempSync(join(tmpdir(), 'simulation-'));
try {
  const modules = ['simulation', 'relief', 'noyau'];
  execFileSync('npx', ['--no-install', 'tsc', ...modules.map((f) => join(DIR, `${f}.ts`)),
    '--target', 'ES2022', '--module', 'ES2022', '--moduleResolution', 'bundler',
    '--outDir', dossier, '--strict', '--lib', 'ES2022,DOM'], { cwd: RACINE, stdio: 'pipe' });

  // tsc ne réécrit pas les extensions ; l'ESM de Node les exige. On compte les
  // remplacements : un remplacement silencieusement nul laisserait un import
  // que Node refuserait plus loin sans dire pourquoi.
  let total = 0;
  for (const f of readdirSync(dossier).filter((x) => x.endsWith('.js'))) {
    const p = join(dossier, f);
    let code = readFileSync(p, 'utf8');
    for (const m of modules) {
      total += code.split(`'./${m}'`).length - 1;
      code = code.replaceAll(`'./${m}'`, `'./${m}.js'`);
    }
    writeFileSync(p, code);
  }
  if (total === 0) throw new Error('aucun import relatif réécrit : la compilation a changé de forme.');

  const S = await import(pathToFileURL(join(dossier, 'simulation.js')).href);
  const v = JSON.parse(readFileSync(VECTEURS, 'utf8'));
  let n = 0;

  const c = v.constantes;
  comparer('constantes', 'seuil', c.seuil_discrimination_fraction, S.SEUIL_DISCRIMINATION_FRACTION);
  comparer('constantes', 'k standard', c.k_standard, S.K_STANDARD);
  comparer('constantes', 'k min', c.k_enveloppe_min, S.K_ENVELOPPE_MIN);
  comparer('constantes', 'k max', c.k_enveloppe_max, S.K_ENVELOPPE_MAX);
  comparer('constantes', 'motif du seuil', c.motif_seuil, S.MOTIF_SEUIL);
  comparer('constantes', 'motif de la réfraction', c.motif_refraction, S.MOTIF_REFRACTION);
  comparer('constantes', 'motif de la réserve', c.motif_reserve_relief, S.MOTIF_RESERVE_RELIEF);
  comparer('constantes', 'pas court', c.pas_court_m, S.PAS_COURT_M);
  comparer('constantes', 'pas moyen', c.pas_moyen_m, S.PAS_MOYEN_M);
  comparer('constantes', 'pas long', c.pas_long_m, S.PAS_LONG_M);
  comparer('constantes', 'seuil distance moyenne', c.seuil_distance_moyenne_m, S.SEUIL_DISTANCE_MOYENNE_M);
  comparer('constantes', 'seuil distance longue', c.seuil_distance_longue_m, S.SEUIL_DISTANCE_LONGUE_M);
  n += 12;

  // Le pas d'échantillonnage : aucune distance n'est refusée, et les trois
  // paliers doivent tomber aux mêmes endroits des deux côtés.
  for (const p of v.pas_echantillonnage) {
    comparer(`pas à ${p.distance_m} m`, 'pas', p.pas_m, S.pasEchantillonnageM(p.distance_m));
    n += 1;
  }
  let leveDistance = false;
  try { S.pasEchantillonnageM(0); } catch { leveDistance = true; }
  if (!leveDistance) ecarts.push({ sujet: 'distance nulle', champ: 'refus', attendu: 'erreur levée', obtenu: 'aucune' });
  n += 1;

  for (const cas of v.cas) {
    const a = analyse(cas.masquee_borne_1_m, cas.obstacle, cas.relief_evalue);
    const b = analyse(cas.masquee_borne_2_m, cas.obstacle, cas.relief_evalue);
    const obtenu = S.juger(a, b, cas.hauteur_cible_m);
    const attendu = cas.verdict;
    comparer(cas.nom, 'discriminante', attendu.discriminante, obtenu.discriminante);
    comparer(cas.nom, 'motif', attendu.motif, obtenu.motif);
    comparer(cas.nom, 'hauteur masquée base min', attendu.hauteur_masquee_base_min_m, obtenu.hauteurMasqueeBaseMinM);
    comparer(cas.nom, 'hauteur masquée base max', attendu.hauteur_masquee_base_max_m, obtenu.hauteurMasqueeBaseMaxM);
    comparer(cas.nom, 'fraction masquée base min', attendu.fraction_masquee_base_min, obtenu.fractionMasqueeBaseMin);
    comparer(cas.nom, 'fraction masquée base max', attendu.fraction_masquee_base_max, obtenu.fractionMasqueeBaseMax);
    comparer(cas.nom, 'masqué par le relief', attendu.masque_par_le_relief, obtenu.masqueParLeRelief);
    comparer(cas.nom, 'distance de l’obstacle', attendu.distance_obstacle_m, obtenu.distanceObstacleM);
    comparer(cas.nom, 'réserve relief', attendu.reserve_relief, obtenu.reserveRelief);
    comparer(cas.nom, 'seuil appliqué', attendu.seuil_applique, obtenu.seuilApplique);
    n += 10;
  }

  // Une hauteur nulle doit être refusée des deux côtés, pas rendre l'infini.
  let leve = false;
  try { S.juger(analyse(1, false, true), analyse(1, false, true), 0); } catch { leve = true; }
  if (!leve) ecarts.push({ sujet: 'hauteur nulle', champ: 'refus', attendu: 'erreur levée', obtenu: 'aucune' });
  n += 1;

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
