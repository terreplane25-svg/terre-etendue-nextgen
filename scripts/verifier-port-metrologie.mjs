/**
 * verifier-port-metrologie.mjs — Épingle le port TypeScript de l'outil D au Python.
 *
 * L'analyse d'image tourne dans le navigateur — l'image ne doit pas quitter la
 * machine de l'opérateur — donc en TypeScript, alors que la référence testée
 * est le paquet Python `metrologie_image`. Deux implémentations de la même
 * formule, c'est le défaut qu'on passe son temps à corriger : une valeur
 * rectifiée d'un côté et restée vieille de l'autre.
 *
 * Ce script refait, en TypeScript, les calculs que le Python a produits dans
 * `src/lib/metrologie-image/vecteurs-or.json`, et compare.
 *
 *     node scripts/verifier-port-metrologie.mjs
 *
 * Régénérer les vecteurs après toute correction du Python :
 *     python3 scripts/generer-vecteurs-or-metrologie.py
 *
 * Deux fichiers sont compilés, pas un : le port de l'outil D importe la
 * géométrie du port de l'outil A plutôt que de la recopier. Le spécificateur
 * d'import émis est complété en `.js` avant chargement — tsc ne réécrit pas
 * les extensions, et l'ESM de Node les exige.
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const SRC_D = join(RACINE, 'src', 'lib', 'metrologie-image', 'noyau.ts');
const SRC_A = join(RACINE, 'src', 'lib', 'visee-optique', 'noyau.ts');
const VECTEURS = join(RACINE, 'src', 'lib', 'metrologie-image', 'vecteurs-or.json');

// Tolérances. Elles ne sont pas uniformes parce que les grandeurs ne le sont
// pas. Celle sur k mérite un mot : la bissection s'arrête après 200 itérations
// sur un intervalle de largeur 2, donc bien en deçà du dernier bit du double ;
// l'écart entre les deux implémentations vient de l'ordre des opérations, pas
// de la convergence.
const TOL_REL = 1e-12;
const TOL_ABS_M = 1e-6; // mètres
const TOL_ABS_RAD = 1e-15; // angles, en radians
const TOL_ABS_ADIM = 1e-12; // fractions, facteurs
const TOL_ABS_PX = 1e-9; // pixels

/**
 * Tolérance sur k, et pourquoi elle est plus large que les autres.
 *
 * L'angle prédit est une fonction QUANTIFIÉE de k : `altitudeDepuisArc`
 * calcule R·(1/cos θ − 1), où la soustraction retranche 1 d'un nombre valant
 * 1,0000087. Il ne reste que 11 chiffres significatifs sur (sec θ − 1), si
 * bien que l'angle rendu est le même double sur tout un intervalle de k, large
 * d'environ 10⁻¹¹ dans les configurations d'infra-réfraction.
 *
 * La bissection converge donc dans ce plateau, à un endroit qui dépend de
 * l'ordre des évaluations — Python et TypeScript n'y tombent pas au même
 * point. Les deux racines sont pourtant également exactes : elles produisent
 * le MÊME angle, bit pour bit. C'est ce que vérifie le contrôle de résidu
 * ci-dessous, qui est l'invariant réel ; cette tolérance-ci n'est que le
 * garde-fou grossier qui l'accompagne.
 *
 * 10⁻⁹ est cent fois la largeur de plateau observée, et sept ordres de
 * grandeur sous ce qu'une mesure photographique peut résoudre sur k — les
 * enveloppes réelles font ±0,01 au mieux. Un vrai désaccord de formule
 * produirait un écart bien supérieur, et resterait attrapé.
 */
const TOL_ABS_K = 1e-9;

/**
 * Tolérance du contrôle de résidu, et pourquoi elle n'est pas l'epsilon machine.
 *
 * Même cause que ci-dessus, vue depuis l'autre bout. `elevation` retranche
 * (R+h) de R·cos ψ : deux nombres de l'ordre de 7·10⁶ dont la différence vaut
 * quelques dizaines. Il reste ~11 chiffres significatifs, soit une incertitude
 * de calcul d'environ 10⁻¹³ rad sur une élévation, et l'angle en est une
 * différence.
 *
 * 10⁻¹² rad est dix fois cette résolution — et surtout un MILLIONIÈME de pixel,
 * pour un pas angulaire de 5·10⁻⁶ rad. Aucune dérive capable de changer une
 * mesure ne peut passer sous ce seuil.
 */
const TOL_RESIDU_RAD = 1e-12;

function compiler() {
  const dossier = mkdtempSync(join(tmpdir(), 'metrologie-port-'));
  execFileSync(
    'npx',
    ['--no-install', 'tsc', SRC_D, SRC_A, '--target', 'ES2022', '--module', 'ES2022',
     '--moduleResolution', 'bundler', '--outDir', dossier, '--strict'],
    { cwd: RACINE, stdio: 'pipe' },
  );
  const entree = join(dossier, 'metrologie-image', 'noyau.js');
  const code = readFileSync(entree, 'utf8');
  // Deux spécificateurs à compléter, pas un : l'import des fonctions employées
  // et le réexport de celles que l'appelant reçoit. Les compter avant de
  // remplacer — un remplacement silencieusement partiel laisserait un import
  // sans extension, que Node refuserait plus loin sans dire pourquoi.
  const occurrences = code.split("'../visee-optique/noyau'").length - 1;
  if (occurrences === 0) {
    throw new Error(
      "Aucun import de '../visee-optique/noyau' dans le JS émis : le port a "
      + "cessé de réutiliser la géométrie de l'outil A, ce qui est exactement "
      + 'ce que ce dépôt interdit.',
    );
  }
  const corrige = code.replaceAll("'../visee-optique/noyau'", "'../visee-optique/noyau.js'");
  writeFileSync(entree, corrige);
  return { dossier, entree };
}

const ecarts = [];
let n = 0;

function comparer(sujet, champ, attendu, obtenu, tolAbs) {
  n += 1;
  if (attendu === null || attendu === undefined) {
    if (obtenu !== null && obtenu !== undefined) {
      ecarts.push({ sujet, champ, attendu: 'null', obtenu, ecart: '—' });
    }
    return;
  }
  if (typeof attendu === 'boolean' || typeof attendu === 'string') {
    if (attendu !== obtenu) ecarts.push({ sujet, champ, attendu, obtenu, ecart: '—' });
    return;
  }
  if (obtenu === null || obtenu === undefined) {
    ecarts.push({ sujet, champ, attendu, obtenu: 'null', ecart: '—' });
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
  const R0 = v.R0;

  const capteurDe = (c) => M.capteur(c.largeur_mm, c.largeur_native_px, c.hauteur_native_px);
  const cadrageDe = (c) => M.cadrage(
    c.largeur_px, c.hauteur_px, c.largeur_recadree_px, c.hauteur_recadree_px,
    c.origine_x_px, c.origine_y_px,
  );

  // --- Étalonnage ---
  for (const e of v.etalonnage) {
    const cap = capteurDe(e.capteur);
    const cad = cadrageDe(e.cadrage);
    const obj = M.objectif(e.focale_mm);
    comparer(e.nom, 'pas_pixel_mm', e.pas_pixel_mm, M.pasPixelMm(cap), 1e-15);
    comparer(e.nom, 'pas_pixel_livre_mm', e.pas_pixel_livre_mm, M.pasPixelLivreMm(cap, cad), 1e-15);
    comparer(e.nom, 'pas_angulaire_rad', e.pas_angulaire_rad, M.pasAngulaireRad(cap, cad, obj), TOL_ABS_RAD);
    comparer(e.nom, 'facteur_reechantillonnage', e.facteur_reechantillonnage, M.facteurReechantillonnage(cad), TOL_ABS_ADIM);
    comparer(e.nom, 'point_principal_connu', e.point_principal_connu, M.pointPrincipalConnu(cad));
    comparer(e.nom, 'recadree', e.recadree, M.estRecadree(cad));
    comparer(e.nom, 'echelle_m_par_px', e.echelle_m_par_px_a_40km, M.echelleMParPx(40000, cap, cad, obj), 1e-9);
    if (e.ordonnee_point_principal_px !== undefined) {
      comparer(e.nom, 'y_point_principal', e.ordonnee_point_principal_px, M.ordonneePointPrincipalPx(cap, cad), TOL_ABS_PX);
    }
    for (const s of e.segments) {
      const sujet = `${e.nom} | segment ${s.y_haut}→${s.y_bas}`;
      comparer(sujet, 'paraxial', s.paraxial_rad, M.angleEntreLignesParaxial(s.y_haut, s.y_bas, cap, cad, obj), TOL_ABS_RAD);
      const [b, hh] = M.angleEntreLignesEnveloppe(s.y_haut, s.y_bas, cap, cad, obj);
      comparer(sujet, 'borne_basse', s.borne_basse_rad, b, TOL_ABS_RAD);
      comparer(sujet, 'borne_haute', s.borne_haute_rad, hh, TOL_ABS_RAD);
      if (s.exact_rad !== undefined) {
        comparer(sujet, 'exact', s.exact_rad, M.angleEntreLignes(s.y_haut, s.y_bas, cap, cad, obj), TOL_ABS_RAD);
      }
    }
  }

  // --- Géométrie apparente ---
  for (const g of v.geometrie) {
    const ci = M.cible(g.H, g.z_b);
    comparer(g.nom, 'R', g.R, M.rayonEffectif(R0, g.k), TOL_ABS_M);
    comparer(g.nom, 'elevation_horizon', g.elevation_horizon_rad, M.elevationHorizon(g.h, g.R), TOL_ABS_RAD);
    comparer(g.nom, 'elevation_sommet', g.elevation_sommet_rad, M.elevation(g.z_b + g.H, g.D, g.h, g.R), TOL_ABS_RAD);
    comparer(g.nom, 'elevation_base', g.elevation_base_rad, M.elevation(g.z_b, g.D, g.h, g.R), TOL_ABS_RAD);
    comparer(g.nom, 'angle_portion_visible', g.angle_portion_visible_rad, M.anglePortionVisible(g.D, g.h, ci, g.R), TOL_ABS_RAD);
    comparer(g.nom, 'angle_horizon_base', g.angle_horizon_base_rad, M.angleHorizonBase(g.D, g.h, ci, g.R), TOL_ABS_RAD);
    comparer(g.nom, 'fraction_visible', g.fraction_visible, M.fractionVisible(g.D, g.h, ci, g.R), TOL_ABS_ADIM);
    if (g.angle_portion_visible_rad > 0) {
      comparer(g.nom, 'hauteur_emergente_m', g.hauteur_emergente_m,
        M.hauteurEmergenteMesuree(g.angle_portion_visible_rad, g.D, g.h, ci, g.R), 1e-6);
    }
    comparer(g.nom, 'hauteur_petit_angle_m', g.hauteur_petit_angle_m,
      M.hauteurEmergentePetitAngle(g.angle_portion_visible_rad, g.D), 1e-9);
  }

  // --- Seuils ---
  for (const s of v.seuils) {
    const ci = M.cible(s.H, s.z_b);
    comparer(s.nom, 'k_saturation', s.k_saturation, M.kDeSaturation(s.D, s.h, ci, R0), TOL_ABS_ADIM);
    comparer(s.nom, 'k_extinction', s.k_extinction, M.kDExtinction(s.D, s.h, ci, R0), TOL_ABS_ADIM);
  }

  // --- Inversion ---
  for (const i of v.inversion) {
    const ci = M.cible(i.H, i.z_b);
    const r = M.coefficientRefractionEffectif(i.angle_rad, i.u_rad, i.D, i.h, ci, R0);
    comparer(i.nom, 'statut', i.statut, r.statut);
    comparer(i.nom, 'k', i.k, r.k, TOL_ABS_K);
    comparer(i.nom, 'k_min', i.k_min, r.kMin, TOL_ABS_K);
    comparer(i.nom, 'k_max', i.k_max, r.kMax, TOL_ABS_K);
    // L'invariant qui compte : les deux racines résolvent la même équation.
    // Le k du Python, réévalué ici, doit rendre exactement l'angle du vecteur —
    // et celui trouvé ici aussi. Un désaccord de formule le ferait tomber,
    // quelle que soit la tolérance accordée à k lui-même.
    if (i.statut === 'déterminé' && i.k !== null) {
      comparer(i.nom, 'angle au k du Python', i.angle_rad,
        M.anglePortionVisible(i.D, i.h, ci, M.rayonEffectif(R0, i.k)), TOL_RESIDU_RAD);
      comparer(i.nom, 'angle au k du port', i.angle_rad, r.angleModeleRad, TOL_RESIDU_RAD);
    }
    comparer(i.nom, 'k_saturation', i.k_saturation, r.kSaturation, TOL_ABS_ADIM);
    comparer(i.nom, 'k_extinction', i.k_extinction, r.kExtinction, TOL_ABS_ADIM);
    comparer(i.nom, 'dans_zone_saturee', i.dans_zone_saturee, r.dansZoneSaturee);
    comparer(i.nom, 'dans_zone_eteinte', i.dans_zone_eteinte, r.dansZoneEteinte);
    comparer(i.nom, 'regime', i.regime, r.regime);
    comparer(i.nom, 'regime_determine', i.regime_determine, r.regimeDetermine);
  }

  // --- Pointés et contrôle d'horizon ---
  {
    const cap = M.capteur(36.0, 6000, 4000);
    const cad = M.cadragePleinCapteur(cap);
    const obj = M.objectif(300.0);
    for (const p of v.pointes) {
      const ci = M.cible(p.H, p.z_b);
      const pts = M.pointes(p.y_horizon, p.y_base, p.y_sommet, p.sigma_px);
      const a = M.anglePortionEmergente(pts, cap, cad, obj);
      comparer(p.nom, 'angle_exact', p.angle_exact_rad, a.exact, TOL_ABS_RAD);
      comparer(p.nom, 'angle_paraxial', p.angle_paraxial_rad, a.paraxial, TOL_ABS_RAD);
      comparer(p.nom, 'incertitude', p.incertitude_rad, a.incertitude, TOL_ABS_RAD);
      const ctl = M.controlerHorizon(pts, cap, cad, obj, p.D, p.h, ci, p.R);
      comparer(p.nom, 'ecart_px', p.controle_ecart_px, ctl.ecartPx, TOL_ABS_PX);
      comparer(p.nom, 'ecart_predit_px', p.controle_ecart_predit_px, ctl.ecartPreditPx, 1e-6);
      comparer(p.nom, 'tolerance_px', p.controle_tolerance_px, ctl.tolerancePx, TOL_ABS_PX);
      comparer(p.nom, 'coherent', p.controle_coherent, ctl.coherent);
    }
  }

  // --- Constantes et fonctions isolées ---
  comparer('divers', 'facteur_elargissement', v.divers.facteur_elargissement, M.FACTEUR_ELARGISSEMENT, TOL_ABS_ADIM);
  comparer('divers', 'k_plancher', v.divers.k_plancher, M.K_PLANCHER, TOL_ABS_ADIM);
  comparer('divers', 'k_plafond', v.divers.k_plafond, M.K_PLAFOND, TOL_ABS_ADIM);
  for (const d of v.divers.dispersion) {
    comparer('dispersion', `n=${d.pointes.length}`, d.ecart_type, M.dispersionPointes(d.pointes), 1e-12);
  }
  for (const d of v.divers.diffraction) {
    comparer('diffraction', `D=${d.diametre_m} m`, d.limite_rad,
      M.resolutionAngulaireLimiteRad(d.lambda_m, d.diametre_m), 1e-18);
  }

  // --- Refus attendus : le port doit refuser là où le Python refuse ---
  const refus = [
    ['capteur de largeur nulle', () => M.capteur(0, 6000, 4000)],
    ['définition native nulle', () => M.capteur(36, 0, 4000)],
    ['focale négative', () => M.objectif(-1)],
    ['rééchantillonnage anisotrope', () => M.cadrage(3000, 1000, 1500, 1000, 0, 0)],
    ['origine partielle', () => M.cadrage(6000, 4000, 6000, 4000, 0, null)],
    ['origine négative', () => M.cadrage(100, 100, 100, 100, -1, 0)],
    ['point principal sur cadrage non documenté',
      () => M.ordonneePointPrincipalPx(M.capteur(36, 6000, 4000), M.cadrage(1500, 1000, 1500, 1000))],
    ['enveloppe sur segment inversé',
      () => M.angleEntreLignesEnveloppe(400, 300, M.capteur(36, 6000, 4000), M.cadrage(1500, 1000, 1500, 1000), M.objectif(300))],
    ['élévation à distance nulle', () => M.elevation(10, 0, 10, 6.371e6)],
    ['élévation à altitude négative', () => M.elevation(-1, 1000, 10, 6.371e6)],
    ['échelle à distance nulle',
      () => M.echelleMParPx(0, M.capteur(36, 6000, 4000), M.cadragePleinCapteur(M.capteur(36, 6000, 4000)), M.objectif(300))],
    ['diffraction sur pupille nulle', () => M.resolutionAngulaireLimiteRad(550e-9, 0)],
    ['sommet sous la base', () => M.pointes(2000, 1800, 1900)],
    ['sigma de pointé nul', () => M.pointes(2000, 2000, 1900, 0)],
    ['dispersion sur deux pointés', () => M.dispersionPointes([1900, 1902])],
    ['incertitude négative',
      () => M.coefficientRefractionEffectif(1e-4, -1e-6, 40000, 30, M.cible(60), 6.371e6)],
    ['plage hors de son enveloppe', () => M.plage('distance', 100, 200, 300, 'SHOM')],
    ['plage sans source', () => M.plage('distance', 100, 90, 110, '   ')],
    ['altitude pour élévation hors domaine',
      () => M.altitudePourElevation(-0.5, 40000, 30, 6.371e6)],
  ];
  for (const [nom, f] of refus) {
    n += 1;
    let leve = false;
    try { f(); } catch { leve = true; }
    if (!leve) ecarts.push({ sujet: 'refus attendu', champ: nom, attendu: 'erreur', obtenu: 'aucune', ecart: '—' });
  }

  // --- Enveloppe sur les entrées : seize sommets, et le refus d'une borne ouverte ---
  {
    const R0b = 6371008.8;
    const ci = M.cible(60, 0);
    const angle = M.anglePortionVisible(40000, 30, ci, M.rayonEffectif(R0b, 0.13));
    const p = (nom, val, bb, bh) => M.plage(nom, val, bb, bh, 'vecteur de contrôle');
    const env = M.enveloppeCoefficient(
      angle, 1e-6,
      p('distance', 40000, 39500, 40500), p('altitude_observateur', 30, 29, 31),
      p('hauteur_cible', 60, 58, 62), p('altitude_base', 0, 0, 0), R0b,
    );
    n += 3;
    if (env.combinaisons !== 16) {
      ecarts.push({ sujet: 'enveloppe', champ: 'combinaisons', attendu: 16, obtenu: env.combinaisons, ecart: '—' });
    }
    if (!env.determinee) {
      ecarts.push({ sujet: 'enveloppe', champ: 'determinee', attendu: true, obtenu: false, ecart: '—' });
    }
    if (!(env.kMin < 0.13 && 0.13 < env.kMax)) {
      ecarts.push({ sujet: 'enveloppe', champ: 'encadre k', attendu: 'kMin < 0,13 < kMax', obtenu: `[${env.kMin} ; ${env.kMax}]`, ecart: '—' });
    }
  }

  // --- Restitution : ce que le texte doit dire, et ne jamais dire ---
  {
    const R0b = 6371008.8;
    const ci = M.cible(60, 0);
    const angle = M.anglePortionVisible(40000, 30, ci, M.rayonEffectif(R0b, 0.13));
    const texte = M.interpreter(M.coefficientRefractionEffectif(angle, 1e-7, 40000, 30, ci, R0b));
    for (const interdit of ['surélevée', 'enfoncée', 'prouve', 'démontre']) {
      n += 1;
      if (texte.includes(interdit)) {
        ecarts.push({ sujet: 'restitution', champ: `mot proscrit « ${interdit} »`, attendu: 'absent', obtenu: 'présent', ecart: '—' });
      }
    }
    n += 1;
    const nul = M.interpreter(M.coefficientRefractionEffectif(0, 1e-6, 40000, 30, ci, R0b));
    if (!nul.includes('majore k, il ne le mesure pas')) {
      ecarts.push({ sujet: 'restitution', champ: 'relevé nul', attendu: 'majore k, il ne le mesure pas', obtenu: nul.slice(0, 60), ecart: '—' });
    }
    n += 1;
    if (M.CE_QUE_CA_N_ETABLIT_PAS.length !== 3) {
      ecarts.push({ sujet: 'restitution', champ: "ce que ça n'établit pas", attendu: 3, obtenu: M.CE_QUE_CA_N_ETABLIT_PAS.length, ecart: '—' });
    }
  }

  if (ecarts.length > 0) {
    console.error(`\n✗ Le port TypeScript a dérivé du paquet Python : ${ecarts.length} écart(s) sur ${n} contrôles.\n`);
    for (const e of ecarts.slice(0, 25)) {
      console.error(`  ${e.sujet}\n    ${e.champ} : attendu ${e.attendu}, obtenu ${e.obtenu} (écart ${e.ecart})`);
    }
    if (ecarts.length > 25) console.error(`  … et ${ecarts.length - 25} autre(s).`);
    console.error("\n  Corriger le Python d'abord, puis répercuter ici, puis régénérer les vecteurs.\n");
    process.exitCode = 1;
  } else {
    console.log(`✓ Port TypeScript conforme au paquet Python : ${n} contrôles, aucun écart.`);
    console.log(`  Vecteurs générés le ${v.genere_le}`);
  }
} finally {
  rmSync(dossier, { recursive: true, force: true });
}
