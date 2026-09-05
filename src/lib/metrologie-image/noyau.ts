/**
 * noyau.ts — Port TypeScript du paquet Python `metrologie_image` (outil D).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-D-metrologie-image/`, qui porte 99 tests. Ce
 * port existe parce que l'image ne doit pas quitter la machine de l'opérateur :
 * l'analyse tourne dans le navigateur. Il est épinglé au Python par les
 * vecteurs de `vecteurs-or.json`, que `scripts/verifier-port-metrologie.mjs`
 * rejoue ici. Si ce fichier dérive, le contrôle échoue.
 *
 * Toute correction de formule se fait DANS LE PYTHON d'abord, puis se
 * répercute ici, puis les vecteurs sont régénérés. Jamais l'inverse.
 *
 * La géométrie du §9 n'est pas réécrite ici : elle est importée du port de
 * l'outil A (`src/lib/visee-optique/noyau.ts`), qui est lui-même épinglé.
 *
 * Les renvois §N pointent vers le protocole « Portion visible d'une cible
 * éloignée au-dessus de la mer » v1.0.
 */

// Import relatif et non `@/lib/...` : le contrôle d'épinglage compile ce fichier
// avec le tsc du projet, hors du contexte Next où l'alias de chemin est résolu.
import {
  arcTangence,
  cible as construireCible,
  distanceCritique,
  distanceLimite,
  hauteurOccultee,
  rayonEffectif,
  classerRegime,
  type Cible,
  type RegimeRefraction,
} from '../visee-optique/noyau';

/**
 * Réexport de ce que la chaîne emprunte à l'outil A, sans le redéfinir.
 *
 * L'appelant — le composant du Lab comme le contrôle d'épinglage — n'a ainsi
 * qu'un module à importer, et la géométrie qu'il obtient reste celle du port
 * de l'outil A, épinglée par ses propres vecteurs. Redéfinir ici `cible` ou
 * `rayonEffectif` créerait la seconde implémentation que tout le reste du
 * dépôt s'emploie à éviter.
 */
export {
  cible,
  rayonEffectif,
  fractionVisible,
  distanceCritique,
  distanceLimite,
  classerRegime,
  IUGG_R1,
  type Cible,
  type RegimeRefraction,
} from '../visee-optique/noyau';

export const INDISPONIBLE = 'indisponible';

/** Largeur du format 24×36, par définition de la « focale équivalent 35 mm ». */
export const LARGEUR_24x36_MM = 36.0;

/**
 * Bornes d'exploration de k. Le plafond est sous 1 parce que R_eff n'est plus
 * défini au-delà (§11.1). Le plancher est là pour que l'absence de solution
 * soit constatée, pas pour être atteint.
 */
export const K_PLANCHER = -1.0;
export const K_PLAFOND = 0.99;

/** Incertitude de pointé par défaut, en pixels, à un écart-type (§19.3). */
export const SIGMA_POINTE_PX_DEFAUT = 3.0;

/** Facteur d'élargissement k = 2, soit ~95 % (JCGM 100:2008, §6.3.2). */
export const FACTEUR_ELARGISSEMENT = 2.0;

export class MetrologieError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'MetrologieError';
  }
}

// --- §14-15 : étalonnage spatial ---

export interface Capteur {
  largeurMm: number;
  /** Définition NATIVE, avant tout recadrage. C'est elle qui fixe le pas pixel. */
  largeurNativePx: number;
  hauteurNativePx: number;
}

export function capteur(largeurMm: number, largeurNativePx: number, hauteurNativePx: number): Capteur {
  if (largeurMm <= 0) throw new MetrologieError('La largeur du capteur doit être strictement positive.');
  if (largeurNativePx <= 0 || hauteurNativePx <= 0) {
    throw new MetrologieError('La définition native doit être strictement positive.');
  }
  return { largeurMm, largeurNativePx, hauteurNativePx };
}

/** Capteur fictif de 36 mm, à employer avec une focale équivalent 35 mm. */
export function capteurEquivalent35mm(largeurNativePx: number, hauteurNativePx: number): Capteur {
  return capteur(LARGEUR_24x36_MM, largeurNativePx, hauteurNativePx);
}

export function pasPixelMm(c: Capteur): number {
  return c.largeurMm / c.largeurNativePx;
}

export interface Objectif {
  focaleMm: number;
}

export function objectif(focaleMm: number): Objectif {
  if (focaleMm <= 0) throw new MetrologieError('La focale doit être strictement positive.');
  return { focaleMm };
}

export interface Cadrage {
  largeurPx: number;
  hauteurPx: number;
  /** Dimensions du recadrage AVANT rééchantillonnage, en pixels natifs. */
  largeurRecadreePx: number;
  hauteurRecadreePx: number;
  /** Coin haut-gauche du recadrage dans le repère natif, ou null si non documenté. */
  origineXPx: number | null;
  origineYPx: number | null;
}

export function cadrage(
  largeurPx: number,
  hauteurPx: number,
  largeurRecadreePx: number,
  hauteurRecadreePx: number,
  origineXPx: number | null = null,
  origineYPx: number | null = null,
): Cadrage {
  const dims: [string, number][] = [
    ['largeurPx', largeurPx], ['hauteurPx', hauteurPx],
    ['largeurRecadreePx', largeurRecadreePx], ['hauteurRecadreePx', hauteurRecadreePx],
  ];
  for (const [nom, v] of dims) {
    if (v <= 0) throw new MetrologieError(`${nom} doit être strictement positif.`);
  }
  const rx = largeurPx / largeurRecadreePx;
  const ry = hauteurPx / hauteurRecadreePx;
  // Un rééchantillonnage anisotrope déforme les angles verticaux et
  // horizontaux différemment : la chaîne le refuse plutôt que d'appliquer un
  // facteur moyen qui n'existe pas.
  if (Math.abs(rx - ry) > 1e-6 * Math.max(rx, ry)) {
    throw new MetrologieError(
      `Rééchantillonnage anisotrope (${rx.toFixed(6)} en largeur, ${ry.toFixed(6)} en hauteur) : ` +
      'les angles verticaux et horizontaux ne sont plus dans le même rapport, ' +
      "la mesure n'est pas définie.",
    );
  }
  if ((origineXPx === null) !== (origineYPx === null)) {
    throw new MetrologieError(
      "L'origine du recadrage se déclare entière ou pas du tout : une seule des deux coordonnées ne suffit pas.",
    );
  }
  if (origineXPx !== null && (origineXPx < 0 || (origineYPx as number) < 0)) {
    throw new MetrologieError("L'origine du recadrage ne peut pas être négative.");
  }
  return { largeurPx, hauteurPx, largeurRecadreePx, hauteurRecadreePx, origineXPx, origineYPx };
}

export function cadragePleinCapteur(c: Capteur): Cadrage {
  return cadrage(c.largeurNativePx, c.hauteurNativePx, c.largeurNativePx, c.hauteurNativePx, 0, 0);
}

/** ρ = pixels livrés / pixels natifs employés. > 1 : image agrandie. */
export function facteurReechantillonnage(cad: Cadrage): number {
  return cad.largeurPx / cad.largeurRecadreePx;
}

export function estRecadree(cad: Cadrage): boolean {
  const memesDims = cad.largeurRecadreePx === cad.largeurPx && cad.hauteurRecadreePx === cad.hauteurPx;
  const origineNulle = (cad.origineXPx === null || cad.origineXPx === 0)
    && (cad.origineYPx === null || cad.origineYPx === 0);
  return !memesDims || !origineNulle;
}

export function pointPrincipalConnu(cad: Cadrage): boolean {
  return cad.origineYPx !== null;
}

/**
 * Pas pixel effectif DANS LE FICHIER LIVRÉ.
 *
 * Le recadrage ne change pas le pas ; le rééchantillonnage le divise par ρ.
 * Un fichier agrandi deux fois a des pixels deux fois plus fins — sans porter
 * pour autant deux fois plus d'information (§15).
 */
export function pasPixelLivreMm(c: Capteur, cad: Cadrage): number {
  return pasPixelMm(c) / facteurReechantillonnage(cad);
}

/**
 * r = arctan(p_livré / f) — angle sous-tendu par un pixel SUR L'AXE.
 * Hors axe, l'angle par pixel décroît : c'est `angleEntreLignes` qui est juste.
 */
export function pasAngulaireRad(c: Capteur, cad: Cadrage, obj: Objectif): number {
  return Math.atan(pasPixelLivreMm(c, cad) / obj.focaleMm);
}

/** Ordonnée du point principal dans le repère du fichier livré. */
export function ordonneePointPrincipalPx(c: Capteur, cad: Cadrage): number {
  if (!pointPrincipalConnu(cad)) {
    throw new MetrologieError(
      `Origine du recadrage non déclarée : l'ordonnée du point principal est ${INDISPONIBLE}. ` +
      'Employer `angleEntreLignesEnveloppe`, qui borne le résultat au lieu de supposer un centre.',
    );
  }
  const centreNatif = c.hauteurNativePx / 2.0;
  return (centreNatif - (cad.origineYPx as number)) * facteurReechantillonnage(cad);
}

/**
 * Angle vertical exact entre deux lignes du fichier, en radians.
 *
 *     θ = arctan(u_haut·p/f) − arctan(u_bas·p/f),  u = y_pp − y
 *
 * Positif quand yHaut < yBas, c'est-à-dire quand la première ligne est
 * effectivement au-dessus de la seconde.
 */
export function angleEntreLignes(
  yHaut: number, yBas: number, c: Capteur, cad: Cadrage, obj: Objectif,
): number {
  const p = pasPixelLivreMm(c, cad);
  const yPp = ordonneePointPrincipalPx(c, cad);
  const f = obj.focaleMm;
  return Math.atan(((yPp - yHaut) * p) / f) - Math.atan(((yPp - yBas) * p) / f);
}

/**
 * La forme du cahier des charges : θ ≈ (yBas − yHaut) · p/f.
 * Conservée pour être comparée à la forme exacte, jamais pour s'y substituer.
 */
export function angleEntreLignesParaxial(
  yHaut: number, yBas: number, c: Capteur, cad: Cadrage, obj: Objectif,
): number {
  return ((yBas - yHaut) * pasPixelLivreMm(c, cad)) / obj.focaleMm;
}

/**
 * Bornes de l'angle quand l'ordonnée du point principal est inconnue.
 *
 * L'origine du recadrage vit dans [0 ; h_native − h_recadrée], ce qui confine
 * y_pp à [(h_rec − h_native/2)·ρ ; (h_native/2)·ρ]. L'angle est maximal au
 * centrage et décroît avec l'excentrement : les bornes sont donc atteintes au
 * centrage s'il est dans ce domaine, sinon à l'une de ses extrémités.
 */
export function angleEntreLignesEnveloppe(
  yHaut: number, yBas: number, c: Capteur, cad: Cadrage, obj: Objectif,
): [number, number] {
  if (pointPrincipalConnu(cad)) {
    const a = angleEntreLignes(yHaut, yBas, c, cad, obj);
    return [a, a];
  }
  if (yBas <= yHaut) {
    throw new MetrologieError('yHaut doit être strictement au-dessus de yBas (ordonnée plus petite).');
  }
  const p = pasPixelLivreMm(c, cad);
  const f = obj.focaleMm;
  const rho = facteurReechantillonnage(cad);
  const anglePour = (yPp: number) =>
    Math.atan(((yPp - yHaut) * p) / f) - Math.atan(((yPp - yBas) * p) / f);

  const yPpMin = (cad.hauteurRecadreePx - c.hauteurNativePx / 2.0) * rho;
  const yPpMax = (c.hauteurNativePx / 2.0) * rho;
  const centre = (yHaut + yBas) / 2.0;

  const candidats = [yPpMin, yPpMax];
  if (yPpMin <= centre && centre <= yPpMax) candidats.push(centre);
  const valeurs = candidats.map(anglePour);
  return [Math.min(...valeurs), Math.max(...valeurs)];
}

/**
 * Mètres par pixel à la distance donnée, SUR L'AXE : D · tan(r).
 * Grandeur de tableau de bord, pas grandeur de calcul : l'inversion travaille
 * en angles et ne passe jamais par cette conversion.
 */
export function echelleMParPx(distanceM: number, c: Capteur, cad: Cadrage, obj: Objectif): number {
  if (distanceM <= 0) throw new MetrologieError('La distance doit être strictement positive.');
  return distanceM * Math.tan(pasAngulaireRad(c, cad, obj));
}

/** Critère de Rayleigh : θ = 1,22 · λ / D — limite de diffraction (§20). */
export function resolutionAngulaireLimiteRad(longueurOndeM: number, diametrePupilleM: number): number {
  if (longueurOndeM <= 0 || diametrePupilleM <= 0) {
    throw new MetrologieError('λ et le diamètre de pupille doivent être strictement positifs.');
  }
  return (1.22 * longueurOndeM) / diametrePupilleM;
}

// --- §9, §11 : géométrie apparente ---

/**
 * Élévation apparente, en radians, d'un point à l'altitude z et à l'arc D.
 *
 *     tan E = (r₂·cos ψ − r₁) / (r₂·sin ψ),  ψ = D/R, r₁ = R+h, r₂ = R+z
 *
 * Le numérateur est presque toujours négatif — une cible lointaine se voit
 * sous l'horizontale — mais le dénominateur reste positif sur tout le domaine
 * admissible (0 < ψ < π), si bien qu'`atan2` y coïncide avec `atan` du
 * quotient. Il est employé parce qu'il ne divise pas, et reste donc défini
 * au bord du domaine ; ce n'est pas une correction de signe.
 */
export function elevation(z: number, D: number, h: number, R: number): number {
  if (R <= 0) throw new MetrologieError('R doit être strictement positif.');
  if (D <= 0) throw new MetrologieError('La distance D doit être strictement positive.');
  if (h < 0 || z < 0) throw new MetrologieError('Les altitudes ne peuvent pas être négatives.');
  const psi = D / R;
  if (psi >= Math.PI) throw new MetrologieError("D/R ≥ π : la cible est au-delà de l'antipode.");
  const r1 = R + h;
  const r2 = R + z;
  return Math.atan2(r2 * Math.cos(psi) - r1, r2 * Math.sin(psi));
}

/** Dépression de l'horizon : E = −s(h)/R, exactement. */
export function elevationHorizon(h: number, R: number): number {
  return -arcTangence(h, R) / R;
}

/** z_v = c + z_b — altitude du point le plus bas encore visible de la cible. */
export function altitudeVisibleLaPlusBasse(D: number, h: number, ci: Cible, R: number): number {
  return hauteurOccultee(D, h, ci, R) + ci.zB;
}

/**
 * Angle vertical entre le point le plus bas visible et le sommet, en radians.
 * C'est la grandeur que l'image mesure. Vaut 0 quand la cible est
 * entièrement occultée.
 */
export function anglePortionVisible(D: number, h: number, ci: Cible, R: number): number {
  const zV = altitudeVisibleLaPlusBasse(D, h, ci, R);
  const zSommet = ci.zB + ci.H;
  if (zV >= zSommet) return 0.0;
  return elevation(zSommet, D, h, R) - elevation(zV, D, h, R);
}

/**
 * Angle prédit entre l'horizon et le point le plus bas visible, en radians.
 *
 * Vaut exactement 0 dès que D dépasse D_crit : le rayon rasant qui définit
 * l'horizon est le même qui définit le point le plus bas visible. En deçà,
 * la base de la cible est plus proche que l'horizon et apparaît AU-DESSOUS
 * de lui — l'angle est alors négatif.
 */
export function angleHorizonBase(D: number, h: number, ci: Cible, R: number): number {
  const zV = altitudeVisibleLaPlusBasse(D, h, ci, R);
  return elevation(zV, D, h, R) - elevationHorizon(h, R);
}

// --- Seuils où l'inversion perd son pouvoir de résolution ---

function bissecterKSurDistance(
  distanceModele: (h: number, ci: Cible, R: number) => number,
  D: number, h: number, ci: Cible, R0: number, kPlancher: number, kPlafond: number,
): number | null {
  const ecart = (k: number) => distanceModele(h, ci, rayonEffectif(R0, k)) - D;
  if (ecart(kPlancher) >= 0 || ecart(kPlafond) < 0) return null;
  let lo = kPlancher;
  let hi = kPlafond;
  for (let i = 0; i < 200; i += 1) {
    const mid = (lo + hi) / 2.0;
    if (ecart(mid) < 0) lo = mid;
    else hi = mid;
  }
  return (lo + hi) / 2.0;
}

/** Le k au-dessus duquel plus rien n'est occulté (D = D_crit), ou null. */
export function kDeSaturation(
  D: number, h: number, ci: Cible, R0: number,
  kPlancher = K_PLANCHER, kPlafond = K_PLAFOND,
): number | null {
  if (distanceCritique(h, ci, rayonEffectif(R0, kPlancher)) >= D) return kPlancher;
  return bissecterKSurDistance(distanceCritique, D, h, ci, R0, kPlancher, kPlafond);
}

/**
 * Le k au-dessous duquel la cible est entièrement occultée (D = D_lim), ou null.
 * Sous ce seuil l'angle prédit vaut exactement zéro pour TOUTE valeur de k :
 * un relevé nul majore k, il ne le mesure pas.
 */
export function kDExtinction(
  D: number, h: number, ci: Cible, R0: number,
  kPlancher = K_PLANCHER, kPlafond = K_PLAFOND,
): number | null {
  if (distanceLimite(h, ci, rayonEffectif(R0, kPlafond)) < D) return kPlafond;
  return bissecterKSurDistance(distanceLimite, D, h, ci, R0, kPlancher, kPlafond);
}

// --- Inversion ---

export type StatutK = 'déterminé' | 'minoré seulement' | 'majoré seulement' | 'indéterminé';

function resoudreK(
  angleMesureRad: number, D: number, h: number, ci: Cible, R0: number,
  kPlancher: number, kPlafond: number,
): { k: number | null; statut: StatutK } {
  const ecart = (k: number) => anglePortionVisible(D, h, ci, rayonEffectif(R0, k)) - angleMesureRad;

  // Rien de visible relevé. L'angle prédit vaut exactement zéro sur tout
  // l'intervalle où la cible est occultée jusqu'au sommet : une bissection
  // prise au mot y rendrait le plancher d'exploration comme s'il s'agissait
  // d'une mesure. C'est une borne, pas une valeur.
  if (angleMesureRad <= 0.0) return { k: null, statut: 'majoré seulement' };

  if (ecart(kPlancher) > 0) return { k: null, statut: 'majoré seulement' };
  if (ecart(kPlafond) < 0) return { k: null, statut: 'minoré seulement' };

  let lo = kPlancher;
  let hi = kPlafond;
  for (let i = 0; i < 200; i += 1) {
    const mid = (lo + hi) / 2.0;
    if (ecart(mid) < 0) lo = mid;
    else hi = mid;
  }
  return { k: (lo + hi) / 2.0, statut: 'déterminé' };
}

export interface ResultatK {
  statut: StatutK;
  k: number | null;
  kMin: number | null;
  kMax: number | null;
  angleMesureRad: number;
  angleModeleRad: number | null;
  kSaturation: number | null;
  kExtinction: number | null;
  dansZoneSaturee: boolean;
  dansZoneEteinte: boolean;
  regime: RegimeRefraction | null;
  regimeMin: RegimeRefraction | null;
  regimeMax: RegimeRefraction | null;
  regimeDetermine: boolean;
  enveloppeOuverte: boolean;
}

/**
 * Inverse l'angle mesuré en coefficient de réfraction, avec son enveloppe.
 *
 * L'enveloppe est obtenue en réinversant aux deux bornes de l'angle, pas en
 * dérivant : la relation k ↦ angle est trop plate près de la saturation pour
 * qu'une dérivée y ait un sens, et une enveloppe ouverte est un résultat.
 */
export function coefficientRefractionEffectif(
  angleMesureRad: number,
  angleIncertitudeRad: number,
  D: number, h: number, ci: Cible, R0: number,
  kPlancher = K_PLANCHER, kPlafond = K_PLAFOND,
): ResultatK {
  if (angleIncertitudeRad < 0) {
    throw new MetrologieError("L'incertitude sur l'angle ne peut pas être négative.");
  }
  const central = resoudreK(angleMesureRad, D, h, ci, R0, kPlancher, kPlafond);
  const bas = resoudreK(angleMesureRad - angleIncertitudeRad, D, h, ci, R0, kPlancher, kPlafond);
  const haut = resoudreK(angleMesureRad + angleIncertitudeRad, D, h, ci, R0, kPlancher, kPlafond);
  const kSat = kDeSaturation(D, h, ci, R0, kPlancher, kPlafond);
  const kExt = kDExtinction(D, h, ci, R0, kPlancher, kPlafond);

  const k = central.k;
  const regime = k !== null ? classerRegime(k) : null;
  const regimeMin = bas.k !== null ? classerRegime(bas.k) : null;
  const regimeMax = haut.k !== null ? classerRegime(haut.k) : null;

  return {
    statut: central.statut,
    k,
    kMin: bas.k,
    kMax: haut.k,
    angleMesureRad,
    angleModeleRad: k !== null ? anglePortionVisible(D, h, ci, rayonEffectif(R0, k)) : null,
    kSaturation: kSat,
    kExtinction: kExt,
    dansZoneSaturee: k !== null && kSat !== null && k >= kSat,
    dansZoneEteinte: central.statut === 'majoré seulement' && angleMesureRad <= 0.0,
    regime,
    regimeMin,
    regimeMax,
    regimeDetermine: regimeMin !== null && regimeMax !== null && regimeMin === regimeMax,
    enveloppeOuverte: bas.k === null || haut.k === null,
  };
}

// --- Enveloppe sur les grandeurs d'entrée ---

export interface Plage {
  nom: string;
  valeur: number;
  borneBasse: number;
  borneHaute: number;
  /**
   * La source est RELEVÉE, plus exigée. Une première version refusait de
   * construire une `Plage` sans elle : le raisonnement était bon et la
   * conséquence mauvaise, car une chaîne saisie dans un champ n'est pas une
   * source vérifiée, et l'analyste qui reprend le dossier refait le travail. Le
   * verrou ne garantissait rien ; il empêchait seulement de calculer.
   *
   * L'absence est donc portée plutôt que bloquante : `sourceDeclaree` la dit,
   * `sourcesManquantes` en fait la liste, et cette liste va jusque dans
   * l'export.
   */
  source: string;
}

export function plage(
  nom: string, valeur: number, borneBasse: number, borneHaute: number, source = '',
): Plage {
  // Ce qui reste refusé : une incohérence, pas une lacune.
  if (!(borneBasse <= valeur && valeur <= borneHaute)) {
    throw new MetrologieError(
      `${nom} : la valeur ${valeur} doit être dans son enveloppe [${borneBasse} ; ${borneHaute}].`,
    );
  }
  return { nom, valeur, borneBasse, borneHaute, source };
}

export function sourceDeclaree(p: Plage): boolean {
  return !!p.source && p.source.trim() !== '';
}

/** Les grandeurs entrées sans source déclarée. Un relevé, pas un refus. */
export function sourcesManquantes(plages: Plage[]): string[] {
  return plages.filter((p) => !sourceDeclaree(p)).map((p) => p.nom);
}

export const AVERTISSEMENT_SOURCES =
  "Une source saisie ici est une DÉCLARATION de l'opérateur, jamais une "
  + 'vérification : rien dans cette chaîne ne contrôle qu\'une fiche d\'ouvrage '
  + "dit bien ce qu'on lui fait dire. Les grandeurs sans source ne sont pas "
  + "écartées du calcul, elles sont listées — c'est à l'analyste de les établir.";

export interface EnveloppeK {
  kMin: number | null;
  kMax: number | null;
  combinaisons: number;
  combinaisonsNonBornees: number;
  determinee: boolean;
}

/**
 * Balaie les seize sommets des quatre enveloppes d'entrée.
 *
 * Le balayage se fait aux sommets et non par tirage : les quatre grandeurs
 * entrent de façon monotone dans la géométrie. Ce n'est pas une hypothèse de
 * commodité — `test_sommets_bornent_le_tirage`, côté Python, la confronte à
 * mille tirages uniformes à l'intérieur du domaine.
 */
export function enveloppeCoefficient(
  angleMesureRad: number,
  angleIncertitudeRad: number,
  distance: Plage,
  altitudeObservateur: Plage,
  hauteurCible: Plage,
  altitudeBase: Plage,
  R0: number,
  kPlancher = K_PLANCHER,
  kPlafond = K_PLAFOND,
): EnveloppeK {
  const ks: number[] = [];
  let ouvertBas = false;
  let ouvertHaut = false;
  let nonBornees = 0;
  let combinaisons = 0;

  for (const d of [distance.borneBasse, distance.borneHaute]) {
    for (const h of [altitudeObservateur.borneBasse, altitudeObservateur.borneHaute]) {
      for (const H of [hauteurCible.borneBasse, hauteurCible.borneHaute]) {
        for (const zb of [altitudeBase.borneBasse, altitudeBase.borneHaute]) {
          combinaisons += 1;
          const r = coefficientRefractionEffectif(
            angleMesureRad, angleIncertitudeRad, d, h, construireCible(H, zb), R0, kPlancher, kPlafond,
          );
          if (r.kMin === null) ouvertBas = true;
          else ks.push(r.kMin);
          if (r.kMax === null) ouvertHaut = true;
          else ks.push(r.kMax);
          if (r.enveloppeOuverte) nonBornees += 1;
        }
      }
    }
  }

  const kMin = ouvertBas || ks.length === 0 ? null : Math.min(...ks);
  const kMax = ouvertHaut || ks.length === 0 ? null : Math.max(...ks);
  return { kMin, kMax, combinaisons, combinaisonsNonBornees: nonBornees, determinee: kMin !== null && kMax !== null };
}

// --- §19 : les trois pointés ---

export interface Pointes {
  yHorizon: number;
  yBase: number;
  ySommet: number;
  sigmaPx: number;
}

export function pointes(
  yHorizon: number, yBase: number, ySommet: number, sigmaPx = SIGMA_POINTE_PX_DEFAUT,
): Pointes {
  if (sigmaPx <= 0) throw new MetrologieError("L'incertitude de pointé doit être strictement positive.");
  if (ySommet >= yBase) {
    throw new MetrologieError(
      `Le sommet doit être au-dessus du bas visible : ySommet < yBase. Relevé : ySommet=${ySommet}, yBase=${yBase}.`,
    );
  }
  return { yHorizon, yBase, ySommet, sigmaPx };
}

/** Écart-type expérimental de pointés répétés sur le même repère (§19.3). */
export function dispersionPointes(ordonnees: number[]): number {
  const n = ordonnees.length;
  if (n < 3) {
    throw new MetrologieError('Au moins trois pointés répétés sont nécessaires pour une dispersion (§19.3).');
  }
  const moyenne = ordonnees.reduce((a, b) => a + b, 0) / n;
  const somme = ordonnees.reduce((acc, y) => acc + (y - moyenne) ** 2, 0);
  return Math.sqrt(somme / (n - 1));
}

export interface AngleReleve {
  /** Projection rectilinéaire, null si le point principal n'est pas connu. */
  exact: number | null;
  paraxial: number;
  borneBasse: number;
  borneHaute: number;
  /** Incertitude élargie due au seul pointé (k = 2, deux pointés indépendants). */
  incertitude: number;
  /** paraxial − exact : ce que coûte l'approximation du cahier des charges. */
  ecartParaxial: number | null;
  /** La valeur à employer : l'exacte si elle existe, le milieu de l'enveloppe sinon. */
  valeur: number;
}

function angleReleve(
  yHaut: number, yBas: number, sigmaPx: number, c: Capteur, cad: Cadrage, obj: Objectif,
): AngleReleve {
  const paraxial = angleEntreLignesParaxial(yHaut, yBas, c, cad, obj);
  const [borneBasse, borneHaute] = angleEntreLignesEnveloppe(yHaut, yBas, c, cad, obj);
  const exact = pointPrincipalConnu(cad) ? angleEntreLignes(yHaut, yBas, c, cad, obj) : null;
  // Deux pointés indépendants : les variances s'ajoutent, d'où le √2.
  const incertitude = FACTEUR_ELARGISSEMENT * Math.SQRT2 * sigmaPx * pasAngulaireRad(c, cad, obj);
  return {
    exact,
    paraxial,
    borneBasse,
    borneHaute,
    incertitude,
    ecartParaxial: exact === null ? null : paraxial - exact,
    valeur: exact !== null ? exact : (borneBasse + borneHaute) / 2.0,
  };
}

/** Clics 2 → 3 : l'angle sous lequel se voit la portion émergente. La mesure. */
export function anglePortionEmergente(
  p: Pointes, c: Capteur, cad: Cadrage, obj: Objectif,
): AngleReleve {
  return angleReleve(p.ySommet, p.yBase, p.sigmaPx, c, cad, obj);
}

export const CAUSES_ECART_HORIZON: readonly string[] = [
  "la cible n'émerge pas directement de l'eau (relief, estran ou ouvrage devant sa base)",
  "la ligne pointée comme horizon n'en est pas un (banc de brume, côte lointaine, nuage bas)",
  'un mirage soulève, abaisse ou dédouble la base (régimes du Tableau 8, §11.3 et §19.4)',
  "l'altitude de base z_b déclarée ne correspond pas à la surface de référence adoptée",
  "l'un des deux pointés est erroné",
];

export interface ControleHorizon {
  ecartPx: number;
  ecartPreditPx: number;
  tolerancePx: number;
  coherent: boolean;
  causesPossibles: readonly string[];
}

/**
 * Vérifie que l'horizon et le bas visible coïncident, comme le modèle l'exige.
 *
 * Ce contrôle ne valide pas la mesure : il peut être satisfait sur un relevé
 * dont les deux pointés sont faux de la même manière. Il n'écarte qu'une
 * famille de défauts, celle où les deux pointés se contredisent.
 */
export function controlerHorizon(
  p: Pointes, c: Capteur, cad: Cadrage, obj: Objectif,
  D: number, h: number, ci: Cible, R: number,
): ControleHorizon {
  const ecartPx = p.yHorizon - p.yBase;
  const r = pasAngulaireRad(c, cad, obj);
  const ecartPreditPx = angleHorizonBase(D, h, ci, R) / r;
  const tolerancePx = FACTEUR_ELARGISSEMENT * Math.SQRT2 * p.sigmaPx;
  const coherent = Math.abs(ecartPx - ecartPreditPx) <= tolerancePx;
  return {
    ecartPx,
    ecartPreditPx,
    tolerancePx,
    coherent,
    causesPossibles: coherent ? [] : CAUSES_ECART_HORIZON,
  };
}

// --- Restitution ---

/** z tel que elevation(z, D, h, R) == eCibleRad — inverse de `elevation`. */
export function altitudePourElevation(
  eCibleRad: number, D: number, h: number, R: number, zMin = 0.0, zMax = 100_000.0,
): number {
  const eBas = elevation(zMin, D, h, R);
  const eHaut = elevation(zMax, D, h, R);
  if (!(eBas <= eCibleRad && eCibleRad <= eHaut)) {
    throw new MetrologieError(
      `Élévation ${eCibleRad} rad hors du domaine balayé [${eBas} ; ${eHaut}] pour z ∈ [${zMin} ; ${zMax}] m.`,
    );
  }
  let lo = zMin;
  let hi = zMax;
  for (let i = 0; i < 200; i += 1) {
    const mid = (lo + hi) / 2.0;
    if (elevation(mid, D, h, R) < eCibleRad) lo = mid;
    else hi = mid;
  }
  return (lo + hi) / 2.0;
}

/**
 * Hauteur, en mètres, de la portion vue sous `angleRad` depuis le bas visible.
 * Calcul exact dans le modèle — ce n'est pas D·tan(θ), qui suppose la scène
 * plane et perpendiculaire à la visée.
 */
export function hauteurEmergenteMesuree(
  angleRad: number, D: number, h: number, ci: Cible, R: number,
): number {
  const zV = altitudeVisibleLaPlusBasse(D, h, ci, R);
  const eBase = elevation(zV, D, h, R);
  return altitudePourElevation(eBase + angleRad, D, h, R) - zV;
}

/** D · tan(θ) — la forme du cahier des charges, pour comparaison seulement. */
export function hauteurEmergentePetitAngle(angleRad: number, D: number): number {
  return D * Math.tan(angleRad);
}

/**
 * Phrase de restitution. Décrit ce qui est établi, jamais davantage.
 *
 * Les seuils du cahier des charges (k ≈ 0,13 ; k > 0,25 ; k < 0,00) ne sont
 * pas ceux du protocole : le Tableau 8 (§11.3) donne 0,13–0,17 pour le régime
 * standard et 0,20–0,40 pour la réfraction forte. Le classement employé est
 * celui du Tableau 8, par `classerRegime` — une seule table de régimes dans
 * tout le dépôt. Le libellé « cible surélevée » est écarté : c'est une
 * conclusion sur la scène, quand la seule chose établie est une valeur de k.
 */
export function interpreter(r: ResultatK): string {
  if (r.statut === 'minoré seulement') {
    return (
      'La portion relevée excède ce que le modèle prédit pour tout k exploré : '
      + "k n'est pas déterminé, il est seulement minoré. Cela se produit quand la "
      + "cible paraît plus haute que la géométrie ne l'autorise — régime de conduit, "
      + 'erreur sur D, h_obs ou H, ou cible mal identifiée.'
    );
  }
  if (r.statut === 'majoré seulement') {
    if (r.dansZoneEteinte) {
      const seuil = r.kExtinction !== null
        ? ` Sous k = ${r.kExtinction.toFixed(3)} la cible est occultée jusqu'au sommet, `
          + "et l'angle prédit y vaut exactement zéro quelle que soit la valeur de k : "
          + 'un relevé nul majore k, il ne le mesure pas.'
        : " L'angle prédit vaut zéro sur tout l'intervalle exploré.";
      return (
        'Aucune portion émergente n\'a été relevée.' + seuil
        + ' Ce résultat est compatible avec une cible réellement invisible comme avec '
        + 'un sommet manqué au pointé : il ne les distingue pas.'
      );
    }
    return (
      'La portion relevée est inférieure à ce que le modèle prédit pour tout k '
      + "exploré : k n'est pas déterminé, il est seulement majoré. Une occultation "
      + 'autre que la courbure — relief, brume, ouvrage — suffit à produire cela.'
    );
  }
  if (r.k === null) return "k n'est pas établi par ce relevé.";

  const socle = r.dansZoneSaturee && r.kSaturation !== null
    ? `Au-delà de k = ${r.kSaturation.toFixed(3)} la cible est entièrement émergée et l'angle `
      + `cesse de dépendre de k. La valeur trouvée (${r.k.toFixed(3)}) est dans cette zone : `
      + 'elle est compatible avec le relevé, mais le relevé ne la distingue pas des valeurs '
      + 'supérieures. À traiter comme un minorant, pas comme une mesure.'
    : `k = ${r.k.toFixed(3)} rend compte de l'angle relevé.`;

  const borne = r.kMin === null || r.kMax === null
    ? " L'enveloppe de pointé est ouverte d'un côté : k n'y est pas encadré."
    : ` Enveloppe due au seul pointé : k ∈ [${r.kMin.toFixed(3)} ; ${r.kMax.toFixed(3)}].`;

  let regime: string;
  if (r.regimeDetermine && r.regimeMin !== null) {
    regime = ` Les deux bornes tombent dans le régime « ${r.regimeMin} » (Tableau 8, §11.3).`;
  } else if (r.regimeMin !== null && r.regimeMax !== null) {
    regime = ` L'enveloppe traverse plusieurs régimes du Tableau 8, de « ${r.regimeMin} » `
      + `à « ${r.regimeMax} » : aucun n'est établi.`;
  } else {
    regime = " Le régime n'est pas déterminé.";
  }

  return socle + borne + regime;
}

export const CE_QUE_CA_N_ETABLIT_PAS: readonly string[] = [
  "Le modèle sphérique est une entrée de ce calcul, pas sa conclusion : k est le "
  + "coefficient qui réconcilierait l'angle relevé avec ce modèle, si D, h_obs et H "
  + "sont exacts. Rien ici ne mesure la réfraction — aucune donnée atmosphérique "
  + "n'entre dans la chaîne — et rien ici ne tranche sur la forme de la surface. "
  + "Toute erreur sur les paramètres d'entrée se déverse dans k, qui est la variable "
  + "d'ajustement.",
  "L'angle relevé n'établit la portion émergente que si la cible pointée est bien "
  + 'celle dont H est déclarée, et si le sommet pointé est bien son sommet.',
  "Une valeur de k compatible avec un régime du Tableau 8 ne démontre pas que ce "
  + "régime régnait : le §11.7 interdit d'invoquer un régime après coup pour "
  + 'justifier la valeur obtenue.',
];
