/**
 * verifier-port-visee.mjs — Épingle le port TypeScript au paquet Python.
 *
 * Le calculateur du site tourne dans le navigateur, donc en TypeScript, alors
 * que la référence testée est le paquet Python `visee_optique`. Deux
 * implémentations de la même formule, c'est le défaut qu'on passe son temps à
 * corriger : une valeur rectifiée d'un côté et restée vieille de l'autre.
 *
 * Ce script refait, en TypeScript, les 61 calculs que le Python a produits
 * dans `src/lib/visee-optique/vecteurs-or.json`, et compare. Une dérive
 * supérieure à la tolérance fait échouer le contrôle.
 *
 *     node scripts/verifier-port-visee.mjs
 *
 * Régénérer les vecteurs après toute correction du Python :
 *     python3 scripts/generer-vecteurs-or-visee.py
 *
 * Le fichier .ts est compilé à la volée par le tsc du projet, dans un dossier
 * temporaire — aucune dépendance nouvelle, et rien n'est écrit dans src/.
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const SRC = join(RACINE, 'src', 'lib', 'visee-optique', 'noyau.ts');
const VECTEURS = join(RACINE, 'src', 'lib', 'visee-optique', 'vecteurs-or.json');

// Tolérances. Elles ne sont pas uniformes parce que les grandeurs ne le sont
// pas : une distance de 13 000 km et une fraction bornée à [0;1] n'ont pas la
// même échelle. La tolérance relative de 1e-12 est celle du double, pas une
// marge de confort.
const TOL_REL = 1e-12;
const TOL_ABS_M = 1e-6; // mètres — sur une distance ou un rayon
const TOL_ABS_ADIM = 1e-12; // fractions, k, deltas

function compiler() {
  const dossier = mkdtempSync(join(tmpdir(), 'visee-port-'));
  execFileSync(
    'npx',
    ['--no-install', 'tsc', SRC, '--target', 'ES2022', '--module', 'ES2022',
     '--moduleResolution', 'bundler', '--outDir', dossier, '--strict'],
    { cwd: RACINE, stdio: 'pipe' },
  );
  return { dossier, entree: join(dossier, 'noyau.js') };
}

const ecarts = [];
function comparer(sujet, champ, attendu, obtenu, tolAbs) {
  if (typeof attendu === 'boolean' || typeof attendu === 'string') {
    if (attendu !== obtenu) ecarts.push({ sujet, champ, attendu, obtenu, ecart: '—' });
    return;
  }
  if (Number.isNaN(attendu)) {
    if (!Number.isNaN(obtenu)) ecarts.push({ sujet, champ, attendu: 'NaN', obtenu, ecart: '—' });
    return;
  }
  const abs = Math.abs(attendu - obtenu);
  const rel = Math.abs(attendu) > 0 ? abs / Math.abs(attendu) : abs;
  if (abs > tolAbs && rel > TOL_REL) {
    ecarts.push({ sujet, champ, attendu, obtenu, ecart: abs.toExponential(3) });
  }
}

const { dossier, entree } = compiler();
try {
  const M = await import(pathToFileURL(entree).href);
  const v = JSON.parse(readFileSync(VECTEURS, 'utf8'));
  let n = 0;

  comparer('constantes', 'GRS80_A', v.constantes.GRS80_A, M.GRS80_A, TOL_ABS_M);
  comparer('constantes', 'GRS80_F', v.constantes.GRS80_F, M.GRS80_F, TOL_ABS_ADIM);
  comparer('constantes', 'GRS80_E2', v.constantes.GRS80_E2, M.GRS80_E2, TOL_ABS_ADIM);
  comparer('constantes', 'IUGG_R1', v.constantes.IUGG_R1, M.IUGG_R1, TOL_ABS_M);
  n += 4;

  for (const c of v.vincenty) {
    const r = M.vincentyInverse(c.lat1, c.lon1, c.lat2, c.lon2);
    comparer(c.nom, 'distance_m', c.distance_m, r.distanceM, TOL_ABS_M);
    comparer(c.nom, 'azimut_depart', c.azimut_depart_deg, r.azimutDepartDeg, TOL_ABS_ADIM);
    comparer(c.nom, 'azimut_arrivee', c.azimut_arrivee_deg, r.azimutArriveeDeg, TOL_ABS_ADIM);
    comparer(c.nom, 'converge', c.converge, r.converge);
    n += 4;
  }

  for (const c of v.rayons) {
    comparer(c.nom, 'meridien', c.meridien, M.rayonMeridien(c.latitude_deg), TOL_ABS_M);
    comparer(c.nom, 'grande_normale', c.grande_normale, M.rayonGrandeNormale(c.latitude_deg), TOL_ABS_M);
    comparer(c.nom, 'euler', c.euler, M.rayonEuler(c.latitude_deg, c.azimut_deg), TOL_ABS_M);
    n += 3;
  }

  for (const g of v.geometrie) {
    const ci = M.cible(g.H, g.z_b);
    const sujet = `géom h=${g.h} H=${g.H} z_b=${g.z_b} D=${g.D} k=${g.k}`;
    comparer(sujet, 'R', g.R, M.rayonEffectif(M.IUGG_R1, g.k), TOL_ABS_M);
    comparer(sujet, 'arc_tangence', g.arc_tangence_h, M.arcTangence(g.h, g.R), TOL_ABS_M);
    comparer(sujet, 'distance_critique', g.distance_critique, M.distanceCritique(g.h, ci, g.R), TOL_ABS_M);
    comparer(sujet, 'distance_limite', g.distance_limite, M.distanceLimite(g.h, ci, g.R), TOL_ABS_M);
    comparer(sujet, 'hauteur_occultee', g.hauteur_occultee, M.hauteurOccultee(g.D, g.h, ci, g.R), TOL_ABS_M);
    comparer(sujet, 'fraction_visible', g.fraction_visible, M.fractionVisible(g.D, g.h, ci, g.R), TOL_ABS_ADIM);
    n += 6;
  }

  for (const r of v.refraction) {
    if (r.k_direct !== undefined) {
      const sujet = `réfraction k=${r.k_direct}`;
      comparer(sujet, 'rayon_effectif', r.rayon_effectif, M.rayonEffectif(M.IUGG_R1, r.k_direct), TOL_ABS_M);
      comparer(sujet, 'regime', r.regime, M.classerRegime(r.k_direct));
      n += 2;
    } else {
      const sujet = `réfraction P=${r.P_hPa} T=${r.T_K} grad=${r.dT_dh_K_par_km}`;
      const k = M.kDepuisGradient(r.P_hPa, r.T_K, r.dT_dh_K_par_km);
      comparer(sujet, 'k', r.k, k, TOL_ABS_ADIM);
      comparer(sujet, 'regime', r.regime, M.classerRegime(k));
      n += 2;
    }
  }

  for (const d of v.discrimination) {
    const sujet = `§28.2 h=${d.h} H=${d.H} D=${d.D} k∈[${d.k_min};${d.k_max}]`;
    const cd = M.conditionDiscrimination(
      d.h, M.cible(d.H, d.z_b), M.IUGG_R1, d.D, d.k_min, d.k_max, d.u_f, d.facteur,
    );
    comparer(sujet, 'delta', d.delta, cd.delta, TOL_ABS_ADIM);
    comparer(sujet, 'seuil', d.seuil, cd.seuil, TOL_ABS_ADIM);
    comparer(sujet, 'satisfaite', d.satisfaite, cd.satisfaite);
    comparer(sujet, 'k_defavorable', d.combinaison_defavorable.k, cd.combinaisonDefavorable.k, TOL_ABS_ADIM);
    n += 4;
  }

  // Contrôles de comportement que les vecteurs ne couvrent pas : le port doit
  // refuser là où le Python refuse.
  const refus = [
    ['Vincenty quasi-antipodal', () => M.vincentyInverse(0, 0, 0, 179.5)],
    ['k ≥ 1', () => M.rayonEffectif(M.IUGG_R1, 1.0)],
    ['H négative', () => M.cible(-5)],
    ['z_b négative', () => M.cible(10, -1)],
    ['latitude hors domaine', () => M.rayonEuler(95, 10)],
    ['azimut hors domaine', () => M.rayonEuler(45, 360)],
  ];
  for (const [nom, f] of refus) {
    let leve = false;
    try { f(); } catch { leve = true; }
    if (!leve) ecarts.push({ sujet: 'refus attendu', champ: nom, attendu: 'erreur', obtenu: 'aucune', ecart: '—' });
    n += 1;
  }

  const pointsConfondus = M.vincentyInverse(43.5, 1.48, 43.5, 1.48);
  if (pointsConfondus.distanceM !== 0 || !Number.isNaN(pointsConfondus.azimutDepartDeg)) {
    ecarts.push({ sujet: 'points confondus', champ: 'azimut', attendu: 'NaN', obtenu: pointsConfondus.azimutDepartDeg, ecart: '—' });
  }
  n += 1;

  if (ecarts.length > 0) {
    console.error(`\n✗ Le port TypeScript a dérivé du paquet Python : ${ecarts.length} écart(s) sur ${n} contrôles.\n`);
    for (const e of ecarts.slice(0, 25)) {
      console.error(`  ${e.sujet}\n    ${e.champ} : attendu ${e.attendu}, obtenu ${e.obtenu} (écart ${e.ecart})`);
    }
    if (ecarts.length > 25) console.error(`  … et ${ecarts.length - 25} autre(s).`);
    console.error('\n  Corriger le Python d\'abord, puis répercuter ici, puis régénérer les vecteurs.\n');
    process.exitCode = 1;
  } else {
    console.log(`✓ Port TypeScript conforme au paquet Python : ${n} contrôles, aucun écart.`);
    console.log(`  Vecteurs générés le ${v.genere_le}`);
  }
} finally {
  rmSync(dossier, { recursive: true, force: true });
}
