/**
 * verifier-port-relief.mjs — Épingle le port TypeScript du relief au Python.
 *
 * Le simulateur d'observation tourne dans le navigateur, donc en TypeScript.
 * La référence testée reste le paquet Python `visee_optique` et ses tests.
 *
 * Ce script rejoue en TypeScript les vecteurs de
 * `src/lib/visee-optique/vecteurs-or-relief.json` — lignes de visée sphérique
 * et plane, analyses de relief dans les quatre situations à distinguer, et
 * refus attendus — puis compare.
 *
 *     node scripts/verifier-port-relief.mjs
 *
 * Régénérer les vecteurs après toute correction du Python :
 *     python3 scripts/generer-vecteurs-or-relief.py
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const SRC_RELIEF = join(RACINE, 'src', 'lib', 'visee-optique', 'relief.ts');
const SRC_NOYAU = join(RACINE, 'src', 'lib', 'visee-optique', 'noyau.ts');
const VECTEURS = join(RACINE, 'src', 'lib', 'visee-optique', 'vecteurs-or-relief.json');

const ecarts = [];
function faux(sujet, champ, attendu, obtenu) {
  ecarts.push({ sujet, champ, attendu, obtenu });
}

/**
 * Tolérance sur les altitudes de visée.
 *
 * Les deux implémentations font la MÊME suite d'opérations flottantes, dans le
 * même ordre : l'accord attendu est donc celui de l'arithmétique IEEE 754, pas
 * celui d'un modèle. Mais le calcul soustrait R (≈ 6,4·10⁶ m) d'une hypoténuse
 * du même ordre : l'annulation catastrophique y coûte une dizaine de chiffres
 * significatifs. 10⁻⁶ m est le plancher de cette annulation, et non une marge
 * choisie pour faire passer le contrôle — une divergence de formule, elle,
 * produirait des écarts de l'ordre du mètre.
 */
const TOL_ALTITUDE_M = 1e-6;

function comparer(sujet, champ, attendu, obtenu, tol = 0) {
  if (attendu === null || attendu === undefined) {
    if (obtenu !== null && obtenu !== undefined) faux(sujet, champ, 'null', obtenu);
    return;
  }
  if (typeof attendu === 'boolean' || typeof attendu === 'string') {
    if (attendu !== obtenu) faux(sujet, champ, attendu, obtenu);
    return;
  }
  if (typeof obtenu !== 'number' || !Number.isFinite(obtenu)) {
    faux(sujet, champ, attendu, obtenu);
    return;
  }
  if (Math.abs(attendu - obtenu) > tol) faux(sujet, champ, attendu, obtenu);
}

const dossier = mkdtempSync(join(tmpdir(), 'relief-port-'));
try {
  execFileSync(
    'npx',
    ['--no-install', 'tsc', SRC_RELIEF, SRC_NOYAU, '--target', 'ES2022', '--module', 'ES2022',
     '--moduleResolution', 'bundler', '--outDir', dossier, '--strict', '--lib', 'ES2022,DOM'],
    { cwd: RACINE, stdio: 'pipe' },
  );
  // tsc ne réécrit pas les extensions ; l'ESM de Node les exige. On compte les
  // occurrences : un remplacement silencieusement partiel laisserait un import
  // que Node refuserait plus loin sans dire pourquoi.
  const emis = join(dossier, 'relief.js');
  const code = readFileSync(emis, 'utf8');
  const n = code.split("'./noyau'").length - 1;
  if (n === 0) throw new Error("relief.js n'importe pas './noyau' : la compilation a changé de forme.");
  writeFileSync(emis, code.replaceAll("'./noyau'", "'./noyau.js'"));

  const R = await import(pathToFileURL(emis).href);
  const N = await import(pathToFileURL(join(dossier, 'noyau.js')).href);
  const v = JSON.parse(readFileSync(VECTEURS, 'utf8'));
  let controles = 0;

  /**
   * Les profils des cas de lignes, refabriqués à l'identique du générateur.
   * Les porter dans le JSON ferait deux cents points par cas pour rien : ce
   * qui doit être épinglé, ce sont les RÉSULTATS, et la fabrication est
   * déterministe des deux côtés.
   */
  const croupe = (D, altitude, debut, fin, pas = 250) => {
    const n = Math.trunc(D / pas);
    const points = [];
    for (let i = 0; i <= n; i++) {
      const d = i * pas;
      points.push({ distanceM: d, altitudeM: (d >= debut && d <= fin) ? altitude : 0 });
    }
    return { points, source: "profil d'essai", pasM: pas, incertitudeVerticaleM: null };
  };
  const R013 = N.rayonEffectif(6371008.7714, 0.13);
  const CIBLE = { H: 500, zB: 0 };
  const CAS_LIGNES = {
    'croupe de 300 m, cible de 500 m — le pied seul est masqué':
      { D: 50000, h: 500, cible: CIBLE, R: R013, profil: croupe(50000, 300, 20000, 24000) },
    'croupe de 900 m — les deux lignes sont coupées':
      { D: 50000, h: 500, cible: CIBLE, R: R013, profil: croupe(50000, 900, 20000, 24000) },
    "terrain plat — aucune des deux n'est coupée":
      { D: 50000, h: 500, cible: CIBLE, R: R013, profil: croupe(50000, 0, 0, 0) },
    'croupe de 300 m, modèle plan':
      { D: 50000, h: 500, cible: CIBLE, R: null, profil: croupe(50000, 300, 20000, 24000) },
  };

  // Le sentinel doit être identique des deux côtés : sinon un relief déclaré
  // non évalué d'un côté ne l'est pas de l'autre.
  comparer('sentinel', 'RELIEF_NON_EVALUE', v.relief_non_evalue, R.RELIEF_NON_EVALUE);
  controles += 1;

  // La formule directe, qui place les points du profil le long de la
  // géodésique. La tolérance est en DEGRÉS : 1e-11° vaut environ 1 µm de
  // méridien, soit le plancher de convergence des deux implémentations.
  for (const c of v.vincenty_direct) {
    const sujet = `Vincenty direct lat=${c.lat1} lon=${c.lon1} az=${c.azimut1} d=${c.distance_m}`;
    const obtenu = N.vincentyDirect(c.lat1, c.lon1, c.azimut1, c.distance_m);
    comparer(sujet, 'latitude', c.lat2, obtenu.latitudeDeg, 1e-11);
    comparer(sujet, 'longitude', c.lon2, obtenu.longitudeDeg, 1e-11);
    controles += 2;
  }

  for (const c of v.ligne_de_visee) {
    const obtenu = R.altitudeLigneDeVisee(c.distance_m, c.D, c.h, c.z_vise, c.R);
    comparer(`visée D=${c.D} h=${c.h} z=${c.z_vise} k=${c.k} d=${c.distance_m}`,
      'altitude', c.altitude, obtenu, TOL_ALTITUDE_M);
    controles += 1;
  }

  for (const c of v.ligne_de_visee_plane) {
    const obtenu = R.altitudeLigneDeViseePlane(c.distance_m, c.D, c.h, c.z_vise);
    comparer(`visée plane D=${c.D} h=${c.h} z=${c.z_vise} d=${c.distance_m}`,
      'altitude', c.altitude, obtenu, TOL_ALTITUDE_M);
    controles += 1;
  }

  for (const a of v.analyses) {
    const cible = N.cible(a.H, a.z_b);
    const profil = a.profil === null
      ? null
      : R.construireProfil(a.profil.map(([d, z]) => [d, z]), "profil d'essai");

    for (const [nomModele, rayon, attendu] of [
      ['sphérique', a.R, a.spherique],
      ['plan', null, a.plan],
    ]) {
      const sujet = `${a.nom} — ${nomModele}`;
      const obtenu = R.analyserRelief(a.D, a.h, cible, rayon, profil, nomModele, a.marge_requise_m);

      comparer(sujet, 'hauteur occultée par la courbure',
        attendu.hauteur_occultee_courbure_m, obtenu.hauteurOccultéeCourbureM, TOL_ALTITUDE_M);
      comparer(sujet, 'fraction visible',
        attendu.fraction_visible_courbure, obtenu.fractionVisibleCourbure, 1e-12);
      comparer(sujet, 'masqué par le relief',
        attendu.masque_par_le_relief, R.masqueParLeRelief(obtenu));
      comparer(sujet, "nombre d'obstacles",
        attendu.nombre_obstacles, obtenu.obstacles.length);
      controles += 4;

      // La marge minimale n'est rendue que si le relief a été évalué : c'est
      // la distinction que le module existe pour tenir.
      if (attendu.marge_minimale_m === null) {
        comparer(sujet, 'marge minimale', null, obtenu.margeMinimaleM);
      } else {
        comparer(sujet, 'marge minimale', attendu.marge_minimale_m, obtenu.margeMinimaleM, TOL_ALTITUDE_M);
      }
      controles += 1;

      const pire = attendu.obstacle_le_plus_genant;
      if (pire === null) {
        if (obtenu.obstacleLePlusGenant !== null) {
          faux(sujet, 'obstacle le plus gênant', 'null', JSON.stringify(obtenu.obstacleLePlusGenant));
        }
        controles += 1;
      } else if (obtenu.obstacleLePlusGenant === null) {
        faux(sujet, 'obstacle le plus gênant', 'un obstacle', 'null');
        controles += 1;
      } else {
        const o = obtenu.obstacleLePlusGenant;
        comparer(sujet, 'obstacle : distance', pire.distance_m, o.distanceM, 1e-6);
        comparer(sujet, 'obstacle : altitude du terrain', pire.altitude_terrain_m, o.altitudeTerrainM, 1e-9);
        comparer(sujet, 'obstacle : altitude de la visée', pire.altitude_visee_m, o.altitudeViseeM, TOL_ALTITUDE_M);
        comparer(sujet, 'obstacle : manque', pire.manque_m, o.manqueM, TOL_ALTITUDE_M);
        controles += 4;
      }
    }

    if (a.spherique.relief_evalue === false) {
      const obtenu = R.analyserRelief(a.D, a.h, cible, a.R, null);
      comparer(a.nom, 'motif de non-évaluation',
        a.spherique.motif_relief_non_evalue, obtenu.motifReliefNonEvalue);
      controles += 1;
    }
  }

  // Les refus : le port doit refuser là où le Python refuse. Les messages
  // n'ont pas à être identiques mot pour mot — le fait de lever, si.
  const REFUS_TS = {
    'profil désordonné': () => R.construireProfil([[0, 0], [500, 1], [200, 2]], 'essai'),
    'profil sans source': () => R.construireProfil([[0, 0], [100, 1]], '   '),
    "profil d'un seul point": () => R.construireProfil([[0, 0]], 'essai'),
    'marge requise négative': () => R.analyserRelief(
      1000, 1, N.cible(10), v.rayon_terre_m,
      R.construireProfil([[0, 0], [500, 0], [1000, 0]], 'essai'), 'sphérique', -1),
    'distance nulle': () => R.analyserRelief(0, 1, N.cible(10), v.rayon_terre_m),
    'rayon nul': () => R.altitudeLigneDeVisee(0, 1000, 0, 0, 0),
  };
  for (const r of v.refus) {
    const appel = REFUS_TS[r.nom];
    if (!appel) {
      faux(`refus ${r.nom}`, 'couverture', 'un cas côté TypeScript', 'aucun');
      controles += 1;
      continue;
    }
    let leve = false;
    try { appel(); } catch { leve = true; }
    if (!leve) faux(`refus ${r.nom}`, 'appel', 'erreur levée', 'aucune erreur');
    controles += 1;
  }

    // ── Les deux lignes : sommet et base ────────────────────────────────────
  //
  // Elles répondent à deux questions différentes — « la cible est-elle
  // entièrement cachée » et « le pied est-il visible ». Un port qui ignorerait
  // le paramètre rendrait toujours la même analyse, et resterait plausible.
  for (const cas of v.lignes_visees) {
    const c = CAS_LIGNES[cas.nom];
    if (c === undefined) { faux(cas.nom, 'cas', 'connu du vérificateur', 'inconnu'); controles += 1; continue; }
    const a = R.analyserRelief(c.D, c.h, c.cible, c.R, c.profil, 'sphérique', 0, 0, cas.viser);
    const ou = `${cas.nom} — ${cas.viser}`;
    comparer(ou, 'nombre d’obstacles', cas.obstacles, a.obstacles.length);
    comparer(ou, 'marge minimale', cas.marge_minimale_m, a.margeMinimaleM, TOL_ALTITUDE_M);
    comparer(ou, 'distance de la marge minimale', cas.distance_marge_minimale_m, a.distanceMargeMinimaleM);
    controles += 3;
    if (cas.plus_genant !== null) {
      const p = a.obstacleLePlusGenant;
      if (p === null) { faux(ou, 'obstacle le plus gênant', 'présent', 'absent'); }
      else {
        comparer(ou, 'plus gênant — distance', cas.plus_genant.distance_m, p.distanceM);
        comparer(ou, 'plus gênant — dépassement', cas.plus_genant.manque_m, p.manqueM, TOL_ALTITUDE_M);
      }
      controles += 2;
    } else if (a.obstacleLePlusGenant !== null) {
      faux(ou, 'obstacle le plus gênant', 'aucun', 'un obstacle rendu');
      controles += 1;
    }
  }

  // Une ligne mal nommée doit être REFUSÉE : « Sommet » mal capitalisé
  // tomberait sinon sur la base, et le résultat resterait plausible.
  {
    const c = Object.values(CAS_LIGNES)[0];
    let leve = false;
    try { R.analyserRelief(c.D, c.h, c.cible, c.R, c.profil, 'sphérique', 0, 0, 'Sommet'); }
    catch { leve = true; }
    if (!leve) faux('ligne mal nommée', 'refus', 'erreur levée', 'aucune');
    controles += 1;
  }

  // ── Le regroupement en occlusions ────────────────────────────────────────
  //
  // C'est ce qui transforme une liste de points qui dépassent en un NOMBRE de
  // reliefs. Une divergence ici annoncerait « 20 occlusions » là où le paquet
  // en compte une, sans qu'aucun chiffre de géométrie ne bouge.
  for (const cas of v.occlusions) {
    const obstacles = cas.obstacles.map(([d, mq]) => ({
      distanceM: d, altitudeTerrainM: 100.0, altitudeViseeM: 100.0 - mq, manqueM: mq,
    }));
    const obtenu = R.grouperOcclusions(obstacles, cas.pas_m);
    comparer(cas.nom, 'nombre d’occlusions', cas.groupes.length, obtenu.length);
    controles += 1;
    for (let i = 0; i < cas.groupes.length; i++) {
      const a = cas.groupes[i];
      const o = obtenu[i];
      if (o === undefined) { faux(cas.nom, `occlusion ${i + 1}`, 'présente', 'absente'); controles += 1; continue; }
      const ou = `occlusion ${i + 1}`;
      comparer(cas.nom, `${ou} — début`, a.debut_m, o.debutM);
      comparer(cas.nom, `${ou} — fin`, a.fin_m, o.finM);
      comparer(cas.nom, `${ou} — largeur`, a.largeur_m, R.largeurOcclusionM(o));
      comparer(cas.nom, `${ou} — nombre de points`, a.nb_points, o.nbPoints);
      comparer(cas.nom, `${ou} — distance du sommet`, a.sommet.distance_m, o.sommet.distanceM);
      comparer(cas.nom, `${ou} — dépassement du sommet`, a.sommet.manque_m, o.sommet.manqueM);
      controles += 6;
    }
  }

if (ecarts.length > 0) {
    console.error(`\n✗ Le port TypeScript a dérivé du paquet Python : ${ecarts.length} écart(s) sur ${controles} contrôles.\n`);
    for (const e of ecarts.slice(0, 30)) {
      console.error(`  ${e.sujet}\n    ${e.champ} : attendu ${e.attendu}, obtenu ${e.obtenu}`);
    }
    if (ecarts.length > 30) console.error(`  … et ${ecarts.length - 30} autre(s).`);
    console.error("\n  Corriger le Python d'abord, puis répercuter ici, puis régénérer les vecteurs.\n");
    process.exitCode = 1;
  } else {
    console.log(`✓ Port TypeScript conforme au paquet Python : ${controles} contrôles, aucun écart.`);
    console.log(`  Vecteurs générés le ${v.genere_le}`);
  }
} finally {
  rmSync(dossier, { recursive: true, force: true });
}
