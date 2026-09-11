/**
 * relief.ts — Port TypeScript de `visee_optique.relief` (outil A).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-A-visee-optique/visee_optique/relief.py`. Ce
 * port est épinglé au Python par les vecteurs de `vecteurs-or-relief.json`,
 * que `scripts/verifier-port-relief.mjs` rejoue ici. Toute correction se fait
 * dans le Python d'abord, puis se répercute ici, puis les vecteurs sont
 * régénérés — jamais l'inverse.
 *
 * POURQUOI CE MODULE EXISTE
 * ─────────────────────────
 * Le reste du paquet répond à une question de géométrie pure : à cette
 * distance, sur cette surface, quelle fraction de la cible reste au-dessus de
 * l'horizon ? Cette question suppose une surface lisse entre les deux points.
 *
 * Le terrain ne l'est pas. Une colline à mi-chemin peut masquer une cible que
 * la courbure laisserait entièrement visible, et le §9.1.3 est explicite : un
 * relief qui dépasse la ligne de visée rend le masquage TOPOGRAPHIQUE, pas
 * géométrique. Confondre les deux, c'est attribuer à la forme de la Terre ce
 * qui revient à une colline — et l'erreur va dans les deux sens.
 *
 * Ce module sépare donc les deux causes, et les rapporte séparément. Il ne
 * PRODUIT pas le profil : un profil de terrain est une donnée, avec sa
 * résolution, sa date et son incertitude. Un profil absent donne un résultat
 * qui déclare le relief NON ÉVALUÉ, jamais un résultat qui déclare l'absence
 * d'obstacle (§15.4).
 */

import { ViseeError, type Cible, fractionVisible, hauteurOccultee } from './noyau';

export class ReliefError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ReliefError';
  }
}

/**
 * Les deux points de la cible qu'une ligne de visée peut rejoindre, et ce que
 * chacun SIGNIFIE quand un relief la coupe :
 *
 *   · SOMMET — la cible est ENTIÈREMENT cachée. Si même son point le plus
 *     favorable est masqué, tout l'est.
 *   · BASE — le PIED n'est pas visible, donc l'occultation par la courbure ne
 *     peut pas être mesurée. La cible peut rester parfaitement visible par
 *     ailleurs : ce n'est pas « on ne voit rien », c'est « on ne peut pas
 *     mesurer ce qu'on était venu mesurer ».
 *
 * Nommés plutôt qu'écrits en chaînes libres : « Sommet » mal capitalisé
 * tomberait silencieusement sur la base, et le résultat resterait plausible.
 */
/**
 * De combien un terrain doit s'élever au-dessus de la surface de référence
 * pour compter comme un RELIEF, quand le profil ne déclare pas sa propre
 * incertitude verticale.
 *
 * Un modèle numérique ne rend pas zéro sur la mer : il rend un mètre, ou
 * trois, selon le géoïde qu'il emploie et la marée du jour. Sans plancher,
 * chaque visée maritime annoncerait « le pied est masqué par le relief » — en
 * désignant la mer, et en recomptant sous le nom de relief l'occultation par
 * la courbure, qui est le résultat principal de l'outil.
 *
 * Contrepartie assumée : une digue de trois mètres ne sera jamais nommée.
 */
export const RELIEF_MINIMAL_M = 5.0;

export const VISER_SOMMET = 'sommet';
export const VISER_BASE = 'base';

/** Ce que dit un résultat sans profil. Ce n'est PAS « aucun obstacle ». */
export const RELIEF_NON_EVALUE = 'relief non évalué — aucun profil de terrain fourni';

export interface PointProfil {
  distanceM: number;
  /**
   * Altitude au-dessus de la MÊME surface de référence que h et z_b. Mélanger
   * une altitude ellipsoïdale à une altitude orthométrique introduit ici une
   * erreur de plusieurs dizaines de mètres, muette et systématique (§12.1).
   */
  altitudeM: number;
}

export interface ProfilTerrain {
  points: PointProfil[];
  /** Exigée : un relief sans provenance ne permet de conclure ni dans un sens ni dans l'autre. */
  source: string;
  pasM: number | null;
  /** Incertitude verticale annoncée par le producteur, si elle l'est. */
  incertitudeVerticaleM: number | null;
}

export interface Obstacle {
  distanceM: number;
  altitudeTerrainM: number;
  altitudeViseeM: number;
  /** POSITIF : de combien le terrain dépasse la ligne (garde comprise). */
  manqueM: number;
}

export interface AnalyseRelief {
  modele: string;
  rayonEffectifM: number | null;
  /** Occultation due à la seule courbure, sans le relief (§9.3). */
  hauteurOccultéeCourbureM: number;
  fractionVisibleCourbure: number;
  reliefEvalue: boolean;
  motifReliefNonEvalue: string | null;
  obstacles: Obstacle[];
  obstacleLePlusGenant: Obstacle | null;
  /** Marge minimale de la visée au-dessus du terrain. Nulle si non évalué. */
  margeMinimaleM: number | null;
  distanceMargeMinimaleM: number | null;
}

/** null quand le relief n'a pas été évalué — jamais false par défaut. */
export function masqueParLeRelief(a: AnalyseRelief): boolean | null {
  if (!a.reliefEvalue) return null;
  return a.obstacleLePlusGenant !== null;
}

export function construireProfil(
  couples: [number, number][],
  source: string,
  pasM: number | null = null,
  incertitudeVerticaleM: number | null = null,
): ProfilTerrain {
  if (couples.length < 2) {
    throw new ReliefError(
      'Un profil de terrain demande au moins deux points : un point isolé ne '
      + 'décrit aucun trajet.',
    );
  }
  if (!source || source.trim() === '') {
    throw new ReliefError(
      'Le profil doit déclarer sa source (§33) : un relief sans provenance ne '
      + 'permet de conclure ni dans un sens ni dans l’autre.',
    );
  }
  let precedent = -Infinity;
  const points: PointProfil[] = [];
  for (const [d, z] of couples) {
    if (d < 0) throw new ReliefError('Une distance de profil ne peut pas être négative.');
    if (d <= precedent) {
      throw new ReliefError(
        'Les points du profil doivent être strictement croissants en distance : '
        + 'un profil non ordonné se lit de travers sans jamais lever d’erreur.',
      );
    }
    precedent = d;
    points.push({ distanceM: d, altitudeM: z });
  }
  return { points, source, pasM, incertitudeVerticaleM };
}

/**
 * Altitude de la ligne de visée droite, au-dessus de la surface de référence.
 *
 * Construction EXACTE, sans développement en série. L'observateur est au rayon
 * R+h à l'angle 0 ; le point visé au rayon R+zVise à l'angle θ_D = D/R. La
 * visée est le SEGMENT DROIT entre les deux — c'est bien une droite : c'est la
 * surface qui est courbe, pas le rayon. On cherche à quel rayon ce segment
 * passe au-dessus de l'angle θ = distance/R, et on en retire R.
 *
 * L'approximation usuelle d(D−d)/2R en est le premier terme. Elle est
 * excellente aux distances usuelles, mais le reste du paquet n'approxime pas :
 * mélanger les deux voies rendrait les résultats incomparables.
 *
 * R est le rayon EFFECTIF quand la réfraction compte : c'est à l'appelant de
 * substituer R/(1−k), comme partout ailleurs.
 */
export function altitudeLigneDeVisee(
  distanceM: number, D: number, h: number, zVise: number, R: number,
): number {
  if (R <= 0) throw new ReliefError('Le rayon doit être strictement positif.');
  if (D <= 0) throw new ReliefError('La distance à la cible doit être strictement positive.');
  const thetaD = D / R;
  const theta = distanceM / R;
  if (thetaD >= Math.PI / 2) {
    throw new ViseeError(
      'Trajet hors du domaine défini (theta = D/R >= pi/2) : la construction en '
      + 'segment droit n’y a plus de sens.',
    );
  }
  const rA = R + h;
  const rB = R + zVise;
  const bx = rB * Math.sin(thetaD);
  const by = rB * Math.cos(thetaD);
  const ax = 0.0;
  const ay = rA;

  const tanT = Math.tan(theta);
  const denominateur = (bx - ax) - tanT * (by - ay);
  if (Math.abs(denominateur) < 1e-12) {
    throw new ReliefError('Géométrie dégénérée : la ligne de visée est radiale à cette distance.');
  }
  const t = (tanT * ay - ax) / denominateur;
  const px = ax + t * (bx - ax);
  const py = ay + t * (by - ay);
  return Math.hypot(px, py) - R;
}

/**
 * Modèle P (§4.2) : la surface est plane, la visée est une droite dessus.
 * Aucun bombement à retrancher. Le relief, lui, masque exactement de la même
 * façon dans les deux modèles — c'est ce qui permet de le distinguer de la
 * courbure.
 */
export function altitudeLigneDeViseePlane(
  distanceM: number, D: number, h: number, zVise: number,
): number {
  if (D <= 0) throw new ReliefError('La distance à la cible doit être strictement positive.');
  return h + (zVise - h) * (distanceM / D);
}

/**
 * Ce que la courbure occulte, ce que le relief masque, et les deux séparément.
 *
 * R vaut null pour le modèle plan. La visée est dirigée vers le SOMMET de la
 * cible (z_b + H) : c'est le point le plus favorable, donc si même lui est
 * masqué, tout l'est. L'inverse serait faux — qu'il soit visible n'implique
 * pas que la base le soit.
 *
 * Un point ne devient obstacle que s'il coupe la visée ET s'élève au-dessus de
 * la surface de référence. Sans cette seconde condition, dès que la courbure
 * occulte quoi que ce soit, la mer elle-même couperait la visée dirigée vers
 * le sommet et serait rapportée comme « obstacle de relief » : la distinction
 * que ce module existe pour établir s'effondrerait exactement dans les cas où
 * elle sert. Conséquence assumée : un terrain plat AU NIVEAU de la surface de
 * référence est traité comme la surface elle-même.
 *
 * `margeRequiseM` permet d'exiger une garde plutôt que le simple contact. Une
 * visée qui frôle un sommet à 20 cm près, avec un modèle de terrain donné à
 * ±2 m, ne conclut rien : c'est à l'appelant de fixer cette garde d'après
 * l'incertitude de SON profil, pas à ce module de la deviner.
 */
export function analyserRelief(
  D: number,
  h: number,
  cible: Cible,
  R: number | null,
  profil: ProfilTerrain | null = null,
  modele = 'sphérique',
  margeRequiseM = 0.0,
  altitudeReferenceM = 0.0,
  viser: string = VISER_SOMMET,
): AnalyseRelief {
  if (viser !== VISER_SOMMET && viser !== VISER_BASE) {
    throw new ReliefError(
      `La ligne à tester vaut '${VISER_SOMMET}' ou '${VISER_BASE}', pas `
      + `'${viser}'. Les deux répondent à des questions différentes et `
      + `confondre les deux rendrait un résultat juste à une question qu'on ne `
      + `posait pas.`,
    );
  }
  if (D <= 0) throw new ReliefError('La distance doit être strictement positive.');
  if (margeRequiseM < 0) throw new ReliefError('La marge requise ne peut pas être négative.');

  const occultee = R === null ? 0.0 : hauteurOccultee(D, h, cible, R);
  const fraction = R === null ? 1.0 : fractionVisible(D, h, cible, R);

  if (profil === null) {
    return {
      modele,
      rayonEffectifM: R,
      hauteurOccultéeCourbureM: occultee,
      fractionVisibleCourbure: fraction,
      reliefEvalue: false,
      motifReliefNonEvalue: RELIEF_NON_EVALUE,
      obstacles: [],
      obstacleLePlusGenant: null,
      margeMinimaleM: null,
      distanceMargeMinimaleM: null,
    };
  }

  const zVise = viser === VISER_SOMMET ? cible.zB + cible.H : cible.zB;
  const obstacles: Obstacle[] = [];
  // Le plancher de relief : l'incertitude verticale que le profil DÉCLARE, ou
  // RELIEF_MINIMAL_M à défaut. Sans lui, la mer — qu'aucun modèle ne rend à
  // exactement zéro — serait rapportée comme un obstacle de relief, et
  // l'occultation par la courbure serait comptée deux fois sous deux noms.
  const plancher = altitudeReferenceM + (
    profil.incertitudeVerticaleM !== null ? profil.incertitudeVerticaleM : RELIEF_MINIMAL_M
  );
  let margeMin = Infinity;
  let distanceMargeMin = 0.0;
  for (const p of profil.points) {
    // Les deux extrémités sont l'observateur et la cible eux-mêmes : les
    // compter ferait qu'un poste posé au sol se masquerait lui-même.
    if (p.distanceM <= 0.0 || p.distanceM >= D) continue;
    const zVisee = R === null
      ? altitudeLigneDeViseePlane(p.distanceM, D, h, zVise)
      : altitudeLigneDeVisee(p.distanceM, D, h, zVise, R);
    const marge = zVisee - p.altitudeM;
    if (marge < margeMin) {
      margeMin = marge;
      distanceMargeMin = p.distanceM;
    }
    if (marge < margeRequiseM && p.altitudeM > plancher) {
      obstacles.push({
        distanceM: p.distanceM,
        altitudeTerrainM: p.altitudeM,
        altitudeViseeM: zVisee,
        manqueM: margeRequiseM - marge,
      });
    }
  }

  // Le plus gênant : celui qui manque le plus. À manque égal, le plus proche
  // de l'observateur — c'est celui qu'on peut aller vérifier.
  let pire: Obstacle | null = null;
  for (const o of obstacles) {
    if (pire === null
      || o.manqueM > pire.manqueM
      || (o.manqueM === pire.manqueM && o.distanceM < pire.distanceM)) {
      pire = o;
    }
  }

  return {
    modele,
    rayonEffectifM: R,
    hauteurOccultéeCourbureM: occultee,
    fractionVisibleCourbure: fraction,
    reliefEvalue: true,
    motifReliefNonEvalue: null,
    obstacles,
    obstacleLePlusGenant: pire,
    margeMinimaleM: Number.isFinite(margeMin) ? margeMin : NaN,
    distanceMargeMinimaleM: distanceMargeMin,
  };
}

// ── Le regroupement en occlusions ───────────────────────────────────────────

/**
 * Un RELIEF continu qui coupe la visée, et non un point de mesure isolé.
 *
 * POURQUOI CE REGROUPEMENT EXISTE
 * ───────────────────────────────
 * `analyserRelief` rend un obstacle PAR POINT ÉCHANTILLONNÉ dépassant la
 * ligne. C'est ce qu'il faut pour calculer, et c'est inutilisable pour dire ce
 * qu'on voit : au pas de 250 m, une seule colline large de six kilomètres
 * produit vingt-quatre « obstacles ». Annoncer « 24 occlusions » quand il y a
 * une colline serait faux dans le seul sens qui compte — celui du nombre.
 *
 * Une occlusion est un intervalle CONTIGU de points qui dépassent tous. Deux
 * collines séparées par une trouée où la visée passe font deux occlusions ;
 * une colline échantillonnée vingt-quatre fois en fait une.
 *
 * CE QUE LE REGROUPEMENT NE SAIT PAS
 * ──────────────────────────────────
 * Il ne voit que des échantillons : une trouée plus étroite que le pas ne
 * laisse aucune trace, et deux collines très voisines peuvent être comptées
 * pour une. Le pas est rendu avec le résultat pour que cette limite se lise.
 */
export interface Occlusion {
  /** Distance du PREMIER point qui dépasse, depuis l'observateur. */
  debutM: number;
  /** Distance du DERNIER point qui dépasse. */
  finM: number;
  /** Le point le plus gênant de l'intervalle : celui qui dépasse le plus. */
  sommet: Obstacle;
  /** Combien de points échantillonnés composent cette occlusion. */
  nbPoints: number;
}

/**
 * L'étendue mesurée d'une occlusion. Nulle quand un seul point dépasse.
 *
 * C'est une borne INFÉRIEURE : le relief commence avant le premier point qui
 * dépasse et finit après le dernier, quelque part dans les deux intervalles
 * d'échantillonnage voisins.
 */
export function largeurOcclusionM(o: Occlusion): number {
  return o.finM - o.debutM;
}

/**
 * Regroupe les points qui dépassent en reliefs contigus.
 *
 * Deux points appartiennent à la même occlusion quand rien ne les sépare : ni
 * un point qui passe sous la visée, ni un trou plus large que le pas.
 *
 * `pasM` sert à décider de la contiguïté. Sans lui, la règle retombe sur
 * l'écart minimal observé, ce qui reste juste pour un profil régulier et se
 * dégrade proprement pour les autres : au pire deux reliefs sont comptés pour
 * un, jamais l'inverse — et compter trop peu est le sens prudent, puisque
 * personne n'en déduira qu'une visée est dégagée.
 */
export function grouperOcclusions(obstacles: Obstacle[], pasM: number | null = null): Occlusion[] {
  const tries = [...obstacles].sort((a, b) => a.distanceM - b.distanceM);
  if (tries.length === 0) return [];

  let ecart = pasM;
  if (ecart === null && tries.length >= 2) {
    ecart = Math.min(...tries.slice(1).map((b, i) => b.distanceM - tries[i].distanceM));
  }
  // Un facteur 1,5 admet le pas nominal et ses irrégularités, sans franchir
  // une trouée d'un pas entier.
  const tolerance = (ecart ?? 0) * 1.5;

  const groupes: Obstacle[][] = [[tries[0]]];
  for (let i = 1; i < tries.length; i++) {
    if (tries[i].distanceM - tries[i - 1].distanceM <= tolerance) groupes[groupes.length - 1].push(tries[i]);
    else groupes.push([tries[i]]);
  }

  return groupes.map((g) => ({
    debutM: g[0].distanceM,
    finM: g[g.length - 1].distanceM,
    sommet: g.reduce((meilleur, o) => (o.manqueM > meilleur.manqueM ? o : meilleur), g[0]),
    nbPoints: g.length,
  }));
}
