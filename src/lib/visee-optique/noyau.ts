/**
 * noyau.ts — Port TypeScript du paquet Python `visee_optique` (outil A).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-A-visee-optique/`, qui porte 321 tests. Ce
 * port existe parce que le calculateur du site tourne dans le navigateur, et
 * il est épinglé au Python par 61 vecteurs d'or : `vecteurs-or.json` est
 * produit par le paquet Python, et `scripts/verifier-port-visee.mjs` refait
 * ici les mêmes calculs et compare. Si ce fichier dérive, le contrôle échoue.
 *
 * Toute correction de formule se fait DANS LE PYTHON d'abord, puis se
 * répercute ici, puis les vecteurs sont régénérés. Jamais l'inverse.
 *
 * Les renvois §N pointent vers le protocole « Portion visible d'une cible
 * éloignée au-dessus de la mer » v1.0.
 */

// --- Constantes (§4.1, §12.2 ; Moritz 2000) ---

export const GRS80_A = 6_378_137.0;
export const GRS80_F = 1.0 / 298.257222101;
export const GRS80_B = GRS80_A * (1.0 - GRS80_F);
export const GRS80_E2 = GRS80_F * (2.0 - GRS80_F);
/** R1 = (2a+b)/3. Commodité de calcul — jamais la valeur d'une observation réelle. */
export const IUGG_R1 = 6_371_008.8;

export class ViseeError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ViseeError';
  }
}

const rad = (d: number) => (d * Math.PI) / 180.0;
const deg = (r: number) => (r * 180.0) / Math.PI;

// --- §12.3 : la géodésique (Vincenty 1975) ---

export interface GeodesiqueInverse {
  distanceM: number;
  /** Azimut au départ, α₁. */
  azimutDepartDeg: number;
  /**
   * Azimut À L'ARRIVÉE dans le même sens de parcours (α₂), et non le
   * gisement de retour. Vers l'est sur l'équateur il vaut 90°, pas 270°.
   * Le gisement de retour est cette valeur plus 180° modulo 360.
   */
  azimutArriveeDeg: number;
  iterations: number;
  converge: boolean;
}

export function vincentyInverse(
  lat1Deg: number,
  lon1Deg: number,
  lat2Deg: number,
  lon2Deg: number,
  a: number = GRS80_A,
  f: number = GRS80_F,
  tol = 1e-12,
  maxIter = 200,
): GeodesiqueInverse {
  for (const [nom, v] of [['lat1', lat1Deg], ['lat2', lat2Deg]] as [string, number][]) {
    if (!(v >= -90.0 && v <= 90.0)) {
      throw new ViseeError(`${nom} hors domaine : ${v}°. Attendu entre -90 et 90.`);
    }
  }
  const b = a * (1.0 - f);
  const L = rad(lon2Deg - lon1Deg);
  const U1 = Math.atan((1.0 - f) * Math.tan(rad(lat1Deg)));
  const U2 = Math.atan((1.0 - f) * Math.tan(rad(lat2Deg)));
  const sinU1 = Math.sin(U1), cosU1 = Math.cos(U1);
  const sinU2 = Math.sin(U2), cosU2 = Math.cos(U2);

  let lam = L;
  let converge = false;
  let tours = 0;
  let sinSigma = 0, cosSigma = 0, sigma = 0, cos2Alpha = 0, cos2SigmaM = 0;
  let sinLam = 0, cosLam = 0;

  for (tours = 1; tours <= maxIter; tours++) {
    sinLam = Math.sin(lam);
    cosLam = Math.cos(lam);
    sinSigma = Math.sqrt(
      (cosU2 * sinLam) ** 2 + (cosU1 * sinU2 - sinU1 * cosU2 * cosLam) ** 2,
    );
    if (sinSigma === 0.0) {
      // Points confondus : distance nulle, azimut indéterminé — et le dire,
      // plutôt que de rendre 0° qui aurait l'air d'une direction mesurée.
      return {
        distanceM: 0.0,
        azimutDepartDeg: NaN,
        azimutArriveeDeg: NaN,
        iterations: tours,
        converge: true,
      };
    }
    cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLam;
    sigma = Math.atan2(sinSigma, cosSigma);
    const sinAlpha = (cosU1 * cosU2 * sinLam) / sinSigma;
    cos2Alpha = 1.0 - sinAlpha ** 2;
    cos2SigmaM = cos2Alpha !== 0.0 ? cosSigma - (2.0 * sinU1 * sinU2) / cos2Alpha : 0.0;
    const C = (f / 16.0) * cos2Alpha * (4.0 + f * (4.0 - 3.0 * cos2Alpha));
    const lamPrec = lam;
    lam =
      L +
      (1.0 - C) *
        f *
        sinAlpha *
        (sigma + C * sinSigma * (cos2SigmaM + C * cosSigma * (-1.0 + 2.0 * cos2SigmaM ** 2)));
    if (Math.abs(lam - lamPrec) < tol) {
      converge = true;
      break;
    }
  }

  if (!converge) {
    throw new ViseeError(
      `Vincenty n'a pas convergé en ${maxIter} itérations : le couple est ` +
        'probablement quasi-antipodal. Aucune distance n\'est retournée.',
    );
  }

  const u2 = (cos2Alpha * (a ** 2 - b ** 2)) / b ** 2;
  const A = 1.0 + (u2 / 16384.0) * (4096.0 + u2 * (-768.0 + u2 * (320.0 - 175.0 * u2)));
  const B = (u2 / 1024.0) * (256.0 + u2 * (-128.0 + u2 * (74.0 - 47.0 * u2)));
  const deltaSigma =
    B *
    sinSigma *
    (cos2SigmaM +
      (B / 4.0) *
        (cosSigma * (-1.0 + 2.0 * cos2SigmaM ** 2) -
          (B / 6.0) *
            cos2SigmaM *
            (-3.0 + 4.0 * sinSigma ** 2) *
            (-3.0 + 4.0 * cos2SigmaM ** 2)));

  const mod360 = (x: number) => ((x % 360.0) + 360.0) % 360.0;
  return {
    distanceM: b * A * (sigma - deltaSigma),
    azimutDepartDeg: mod360(deg(Math.atan2(cosU2 * sinLam, cosU1 * sinU2 - sinU1 * cosU2 * cosLam))),
    azimutArriveeDeg: mod360(deg(Math.atan2(cosU1 * sinLam, -sinU1 * cosU2 + cosU1 * sinU2 * cosLam))),
    iterations: tours,
    converge: true,
  };
}

// --- §12.2 : rayons de courbure de l'ellipsoïde ---

function validerLatitude(latDeg: number): number {
  if (!(latDeg >= -90.0 && latDeg <= 90.0)) {
    throw new ViseeError(`Latitude hors domaine : ${latDeg}°.`);
  }
  return rad(latDeg);
}

export function rayonMeridien(latDeg: number, a = GRS80_A, e2 = GRS80_E2): number {
  const phi = validerLatitude(latDeg);
  return (a * (1.0 - e2)) / (1.0 - e2 * Math.sin(phi) ** 2) ** 1.5;
}

export function rayonGrandeNormale(latDeg: number, a = GRS80_A, e2 = GRS80_E2): number {
  const phi = validerLatitude(latDeg);
  return a / Math.sqrt(1.0 - e2 * Math.sin(phi) ** 2);
}

/**
 * Rayon de courbure normal à l'azimut de la visée — rayon d'Euler (§12.2).
 * C'est ce rayon, jamais IUGG_R1, qu'une observation réelle doit employer :
 * l'écart entre les deux atteint 1 %, soit plusieurs pour cent sur la hauteur
 * occultée.
 */
export function rayonEuler(latDeg: number, azimutDeg: number, a = GRS80_A, e2 = GRS80_E2): number {
  const phi = validerLatitude(latDeg);
  if (!(azimutDeg >= 0.0 && azimutDeg < 360.0)) {
    throw new ViseeError("L'azimut doit être compris entre 0° (inclus) et 360° (exclu).");
  }
  const az = rad(azimutDeg);
  const M = (a * (1.0 - e2)) / (1.0 - e2 * Math.sin(phi) ** 2) ** 1.5;
  const N = a / Math.sqrt(1.0 - e2 * Math.sin(phi) ** 2);
  return 1.0 / (Math.cos(az) ** 2 / M + Math.sin(az) ** 2 / N);
}

// --- §11 : réfraction ---

const G_SUR_RD = 0.0342; // K/m — gradient autoconvectif, annule k
const CONSTANTE_K = 503.3;

/** k = 503,3 · (P/T²) · (0,0342 + dT/dh) — §11.2. dT/dh en K/km. */
export function kDepuisGradient(pHpa: number, tK: number, dTdhKParKm: number): number {
  if (pHpa <= 0) throw new ViseeError('La pression doit être strictement positive.');
  if (tK <= 0) throw new ViseeError('La température doit être strictement positive (kelvins).');
  return CONSTANTE_K * (pHpa / tK ** 2) * (G_SUR_RD + dTdhKParKm / 1000.0);
}

/** R_eff = R / (1 − k), valable pour k < 1 (§11.1). */
export function rayonEffectif(R: number, k: number): number {
  if (R <= 0) throw new ViseeError('R doit être strictement positif.');
  if (k >= 1) {
    throw new ViseeError(
      'k ≥ 1 : régime de conduit optique (Tableau 8). R_eff n\'est plus défini ' +
        'par cette formule, et la construction du §8 ne s\'applique plus.',
    );
  }
  return R / (1.0 - k);
}

export type RegimeRefraction =
  | 'aucune réfraction'
  | 'réfraction standard'
  | 'réfraction forte'
  | 'réfraction très forte'
  | 'inversion et mirage supérieur'
  | 'conduit optique';

/** Tableau 8 (§11.3). Classement informatif, jamais décisionnel. */
export function classerRegime(k: number): RegimeRefraction {
  if (k <= 0) return 'aucune réfraction';
  if (k < 0.2) return 'réfraction standard';
  if (k < 0.4) return 'réfraction forte';
  if (k < 0.8) return 'réfraction très forte';
  if (k < 1.0) return 'inversion et mirage supérieur';
  return 'conduit optique';
}

// --- §9 : géométrie ---

export interface Cible {
  /** Hauteur totale, en mètres. */
  H: number;
  /** Altitude de la base au-dessus de la surface de référence, en mètres. */
  zB: number;
}

export function cible(H: number, zB = 0.0): Cible {
  if (H <= 0) throw new ViseeError('La hauteur de cible H doit être strictement positive.');
  if (zB < 0) throw new ViseeError("L'altitude de base z_b ne peut pas être négative.");
  return { H, zB };
}

/** s(x) = R·arccos[R/(R+x)] — §9.1. */
export function arcTangence(x: number, R: number): number {
  if (R <= 0) throw new ViseeError('R doit être strictement positif.');
  if (x < 0) throw new ViseeError("L'altitude x ne peut pas être négative.");
  return R * Math.acos(R / (R + x));
}

/** Inverse exacte : x tel que arcTangence(x, R) === arc. C'est z_v du §9.3. */
export function altitudeDepuisArc(arc: number, R: number): number {
  if (R <= 0) throw new ViseeError('R doit être strictement positif.');
  if (arc < 0) throw new ViseeError('Un arc ne peut pas être négatif.');
  const theta = arc / R;
  if (theta >= Math.PI / 2) {
    throw new ViseeError('Arc hors du domaine de la construction de tangence (arc/R ≥ π/2).');
  }
  return R * (1.0 / Math.cos(theta) - 1.0);
}

export function distancePourHauteurOccultee(c: number, h: number, ci: Cible, R: number): number {
  if (c < 0) throw new ViseeError('La hauteur occultée cible ne peut pas être négative.');
  return arcTangence(h, R) + arcTangence(c + ci.zB, R);
}

/** D_crit = s(h) + s(z_b) — la base cesse d'être visible au-delà (§9.2). */
export function distanceCritique(h: number, ci: Cible, R: number): number {
  return distancePourHauteurOccultee(0.0, h, ci, R);
}

/** D_lim = s(h) + s(z_b + H) — le sommet cesse de l'être au-delà (§9.2). */
export function distanceLimite(h: number, ci: Cible, R: number): number {
  return distancePourHauteurOccultee(ci.H, h, ci, R);
}

/**
 * c(D) — hauteur occultée (§9.3). Peut dépasser H au-delà de D_lim : c'est
 * `fractionVisible`, et non cette fonction, qui borne à [0 ; 1].
 */
export function hauteurOccultee(D: number, h: number, ci: Cible, R: number): number {
  if (D <= distanceCritique(h, ci, R)) return 0.0;
  return altitudeDepuisArc(D - arcTangence(h, R), R) - ci.zB;
}

/** f = (H − c)/H, bornée à [0 ; 1] — la grandeur comparée (§6.1, §9.3). */
export function fractionVisible(D: number, h: number, ci: Cible, R: number): number {
  const c = hauteurOccultee(D, h, ci, R);
  return Math.min(1.0, Math.max(0.0, (ci.H - c) / ci.H));
}

/** Modèle P (§4.2) : aucune occultation géométrique, à toute distance. */
export function fractionVisibleModelePlan(D: number): number {
  if (D <= 0) throw new ViseeError('La distance D doit être strictement positive.');
  return 1.0;
}

// --- §23 : enveloppe de sensibilité ---

export interface PlageParametre {
  nom: string;
  minimum: number;
  maximum: number;
  justification?: string;
}

export interface EnveloppeSensibilite {
  minimum: number;
  maximum: number;
  combinaisonMinimale: Record<string, number>;
  combinaisonMaximale: Record<string, number>;
  nEvaluations: number;
}

/**
 * Balaie chaque paramètre dans sa plage et rapporte l'enveloppe — jamais une
 * valeur centrale (§23.1). Grille complète uniquement : le port ne fait pas de
 * Monte-Carlo, et refuse si la grille dépasserait la borne, plutôt que de
 * resserrer l'intervalle en silence.
 */
export function balayerEnveloppe(
  fonction: (params: Record<string, number>) => number,
  plages: PlageParametre[],
  pasParParametre = 9,
  maxGrille = 100_000,
): EnveloppeSensibilite {
  if (plages.length === 0) throw new ViseeError('Au moins une plage de paramètre est nécessaire.');
  if (pasParParametre ** plages.length > maxGrille) {
    throw new ViseeError(
      `La grille complète dépasserait ${maxGrille} combinaisons. Le port ne ` +
        'fait pas de tirage aléatoire : réduisez le nombre de paramètres libres.',
    );
  }
  const valeurs = plages.map((p) => {
    if (pasParParametre <= 1 || p.minimum === p.maximum) return [p.minimum];
    const pas = (p.maximum - p.minimum) / (pasParParametre - 1);
    return Array.from({ length: pasParParametre }, (_, i) => p.minimum + i * pas);
  });

  let minimum = Infinity;
  let maximum = -Infinity;
  let combiMin: Record<string, number> = {};
  let combiMax: Record<string, number> = {};
  let n = 0;

  const parcourir = (i: number, acc: Record<string, number>) => {
    if (i === plages.length) {
      const v = fonction(acc);
      n += 1;
      if (v < minimum) {
        minimum = v;
        combiMin = { ...acc };
      }
      if (v > maximum) {
        maximum = v;
        combiMax = { ...acc };
      }
      return;
    }
    for (const val of valeurs[i]) parcourir(i + 1, { ...acc, [plages[i].nom]: val });
  };
  parcourir(0, {});

  return {
    minimum,
    maximum,
    combinaisonMinimale: combiMin,
    combinaisonMaximale: combiMax,
    nEvaluations: n,
  };
}

// --- §28.2 : condition de discrimination ---

export interface ConditionDiscrimination {
  /** Écart minimal |f_S − f_P| sur l'enveloppe jointe — le bord le plus défavorable. */
  delta: number;
  combinaisonDefavorable: Record<string, number>;
  uF: number;
  facteur: number;
  seuil: number;
  satisfaite: boolean;
}

/**
 * Δ ≥ facteur · u(f) — §28.2.
 *
 * Δ est pris au bord d'enveloppe le PLUS DÉFAVORABLE à la discrimination, pas
 * au point nominal. Le facteur 5 est la valeur recommandée au §26 ; elle n'a
 * rien d'obligatoire et se remplace par celle réellement déposée.
 *
 * Ce résultat est un préalable géométrique. Il ne dit rien sur la forme de la
 * Terre, et ne devient un verdict qu'au terme d'une mesure photographique
 * réelle conduite selon le protocole.
 */
export function conditionDiscrimination(
  h: number,
  ci: Cible,
  R: number,
  D: number,
  kMin: number,
  kMax: number,
  uF: number,
  facteur = 5.0,
  pasParParametre = 9,
): ConditionDiscrimination {
  if (uF < 0) throw new ViseeError('u(f) ne peut pas être négative.');
  const enveloppe = balayerEnveloppe(
    (p) => Math.abs(fractionVisible(D, h, ci, rayonEffectif(R, p.k)) - fractionVisibleModelePlan(D)),
    [{ nom: 'k', minimum: kMin, maximum: kMax }],
    pasParParametre,
  );
  const seuil = facteur * uF;
  return {
    delta: enveloppe.minimum,
    combinaisonDefavorable: enveloppe.combinaisonMinimale,
    uF,
    facteur,
    seuil,
    satisfaite: enveloppe.minimum >= seuil,
  };
}
