/**
 * simulation.ts — Port TypeScript de `visee_optique.simulation` (outil A).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-A-visee-optique/visee_optique/simulation.py`.
 * Ce port est épinglé au Python par `vecteurs-or-simulation.json`, que
 * `scripts/verifier-port-simulation.mjs` rejoue ici.
 *
 * CE QUE CE MODULE AJOUTE, ET CE QU'IL N'AJOUTE PAS
 * ─────────────────────────────────────────────────
 * Il n'ajoute AUCUNE physique. La géodésie vient de `noyau.ts`, l'occultation
 * aussi, le relief de `relief.ts` — tous déjà épinglés. Ce qu'il ajoute, ce
 * sont deux CONVENTIONS : à partir de quel écart une visée départage les deux
 * modèles, et à quel pas échantillonner le terrain. Elles sont donc écrites en
 * constantes nommées, affichées à l'écran, et contestables.
 *
 * CE QUI SE MESURE : LE PIED DE LA CIBLE, PAS SON SOMMET
 * ──────────────────────────────────────────────────────
 * C'est le PIED de la cible qui disparaît en premier sous l'horizon, et c'est
 * là que les deux modèles divergent en premier. La grandeur mise en avant est
 * donc la hauteur masquée EN PARTANT DE LA BASE, et non la part visible du
 * sommet, qui reste à 100 % longtemps après que la divergence est devenue
 * mesurable. Elle n'est pas bornée à la hauteur de la cible : au-delà de la
 * distance limite elle continue de croître et dit de combien la cible est
 * passée sous l'horizon.
 */

import type { AnalyseRelief } from './relief';
import { masqueParLeRelief } from './relief';

/**
 * Le seuil critique. La courbure doit masquer au moins cette FRACTION de la
 * hauteur de la cible, EN PARTANT DE LA BASE, pour que la visée départage.
 *
 * 10 %, c'est-à-dire 11 m sur une cible de 110 m : une différence qu'une
 * photographie montre sans ambiguïté. Convention de lecture, pas norme.
 */
export const SEUIL_DISCRIMINATION_FRACTION = 0.10;

/**
 * La réfraction moyenne appliquée par défaut, et son enveloppe.
 *
 * 0,13 correspond à une atmosphère bien mélangée. Les bornes 0,10 et 0,40
 * encadrent ce qu'on rencontre au-dessus de l'eau sans avoir mesuré le profil
 * vertical de température — et on ne l'a jamais mesuré ici.
 */
export const K_STANDARD = 0.13;
export const K_ENVELOPPE_MIN = 0.10;
export const K_ENVELOPPE_MAX = 0.40;

/**
 * Le pas d'échantillonnage du terrain, par tranche de distance.
 *
 * Aucune longueur de visée n'est refusée. Ce qui croît avec la distance, c'est
 * le NOMBRE de points d'altitude à demander : un pas fixe de 250 m sur 2 000 km
 * ferait 8 000 points, l'élargissement le ramène à 1 000. Il ne PLAFONNE pas ce
 * nombre, il le freine — à 20 000 km il en reste 10 000.
 *
 * Contrepartie assumée et affichée : sur une visée longue, une colline étroite
 * peut passer entre deux points de mesure.
 */
export const PAS_COURT_M = 250.0;
export const PAS_MOYEN_M = 500.0;
export const PAS_LONG_M = 2000.0;
export const SEUIL_DISTANCE_MOYENNE_M = 100_000.0;
export const SEUIL_DISTANCE_LONGUE_M = 500_000.0;

export const MOTIF_SEUIL =
  'Une visée est dite discriminante quand DEUX conditions sont réunies : la '
  + 'courbure masque au moins 10 % de la hauteur de la cible en partant de sa '
  + 'base, même à la réfraction la plus défavorable ; et le relief intermédiaire '
  + 'laisse la visée entièrement dégagée. La première condition écarte les '
  + 'visées où les deux modèles prédisent presque la même chose ; la seconde '
  + "écarte celles où c'est une colline, et non la forme de la Terre, qui "
  + "décide de ce qu'on voit. Ce seuil de 10 % est une convention de lecture, "
  + 'pas une norme.';

export const MOTIF_REFRACTION =
  'La réfraction atmosphérique courbe les rayons lumineux et fait voir '
  + 'un peu plus loin que la géométrie pure. Faute de profil vertical de '
  + 'température mesuré sur le trajet, le calcul est conduit sur toute '
  + "l'enveloppe plausible au-dessus de l'eau — de 0,10 à 0,40, valeur "
  + 'moyenne 0,13 — et les résultats sont rendus comme un intervalle. Un '
  + "chiffre unique laisserait croire cette grandeur mieux connue qu'elle "
  + "ne l'est.";

export const MOTIF_RESERVE_RELIEF =
  "Le relief intermédiaire n'a pas pu être évalué : la seconde condition de "
  + "discrimination n'est donc pas vérifiée, seulement présumée. Ce n'est pas "
  + "« aucun obstacle » — c'est « on ne sait pas », et un talus non vu "
  + 'invaliderait la visée sans rien changer à la courbure.';

/**
 * Le pas d'échantillonnage du terrain, choisi d'après la distance.
 *
 * Aucune distance n'est refusée : cette fonction ne borne rien, elle règle
 * seulement la finesse du relevé pour que le nombre de points reste tenable.
 */
export function pasEchantillonnageM(distanceM: number): number {
  if (distanceM <= 0) throw new Error('La distance doit être strictement positive.');
  if (distanceM < SEUIL_DISTANCE_MOYENNE_M) return PAS_COURT_M;
  if (distanceM < SEUIL_DISTANCE_LONGUE_M) return PAS_MOYEN_M;
  return PAS_LONG_M;
}

/** Ce que la configuration permet de conclure, avant toute observation. */
export interface Verdict {
  discriminante: boolean;
  /** Le motif, en une phrase lisible par quelqu'un qui n'a lu aucun protocole. */
  motif: string;
  /**
   * La hauteur masquée EN PARTANT DE LA BASE, aux deux bornes de réfraction.
   * Non bornée à H : au-delà de la distance limite elle continue de croître.
   */
  hauteurMasqueeBaseMinM: number;
  hauteurMasqueeBaseMaxM: number;
  /** La même chose en fraction de la hauteur de la cible. Peut dépasser 1. */
  fractionMasqueeBaseMin: number;
  fractionMasqueeBaseMax: number;
  /**
   * Vrai quand le relief masque la cible dans les deux modèles ; null quand le
   * relief n'a pas été évalué — jamais false par défaut.
   */
  masqueParLeRelief: boolean | null;
  /** Où se trouve l'obstacle qui bloque, quand il y en a un. */
  distanceObstacleM: number | null;
  /**
   * Vrai quand le verdict porte sur la courbure seule, faute d'avoir pu
   * vérifier la seconde condition.
   */
  reserveRelief: boolean;
  seuilApplique: number;
}

const m = (x: number) => x.toFixed(1).replace('.', ',');
const km = (x: number) => (x / 1000).toFixed(2).replace('.', ',');
const pc = (f: number) => (100 * f).toFixed(1).replace('.', ',');

/**
 * Le verdict, à partir des deux bornes de l'enveloppe de réfraction.
 *
 * Peu importe laquelle des deux masque le plus : le module les trie, parce que
 * l'ordre dépend du signe d'une dérivée que l'appelant n'a pas à connaître.
 */
export function juger(
  globeMin: AnalyseRelief,
  globeMax: AnalyseRelief,
  hauteurCibleM: number,
): Verdict {
  if (hauteurCibleM <= 0) {
    throw new Error('La hauteur de la cible doit être strictement positive.');
  }

  const masquees = [
    globeMin.hauteurOccultéeCourbureM,
    globeMax.hauteurOccultéeCourbureM,
  ].sort((a, b) => a - b);
  const bas = masquees[0];
  const haut = masquees[1];

  const masque = masqueParLeRelief(globeMin);
  const obstacle = globeMin.obstacleLePlusGenant;
  const distanceObstacle = obstacle !== null ? obstacle.distanceM : null;

  const commun = {
    hauteurMasqueeBaseMinM: bas,
    hauteurMasqueeBaseMaxM: haut,
    fractionMasqueeBaseMin: bas / hauteurCibleM,
    fractionMasqueeBaseMax: haut / hauteurCibleM,
    masqueParLeRelief: masque,
    distanceObstacleM: distanceObstacle,
    seuilApplique: SEUIL_DISCRIMINATION_FRACTION,
  };

  // Le relief d'abord : quand il bloque, la question de la courbure ne se pose
  // plus. Les deux modèles prédisent la même chose, pour la même raison, et
  // cette raison n'est pas la forme de la Terre.
  if (masque) {
    const ou = distanceObstacle !== null ? `à ${km(distanceObstacle)} km` : 'sur le trajet';
    return {
      ...commun,
      discriminante: false,
      motif:
        `La cible est bloquée à la base par le relief local (${ou}) dans `
        + "les deux modèles, ce qui empêche d'évaluer la courbure à grande "
        + "distance. Ce n'est pas la forme de la Terre qui décide ici, "
        + "c'est un obstacle du terrain — et il masque identiquement quel "
        + 'que soit le modèle.',
      reserveRelief: false,
    };
  }

  if (commun.fractionMasqueeBaseMin < SEUIL_DISCRIMINATION_FRACTION) {
    return {
      ...commun,
      discriminante: false,
      motif:
        'À la réfraction la plus favorable, la courbure ne masque que '
        + `${m(bas)} m à la base de la cible, soit ${pc(commun.fractionMasqueeBaseMin)} % de sa hauteur — sous le `
        + `seuil de ${pc(SEUIL_DISCRIMINATION_FRACTION)} %. Les deux modèles prédisent presque la même `
        + 'chose. Il faut viser plus loin, ou plus bas, ou une cible plus '
        + 'courte.',
      reserveRelief: false,
    };
  }

  const reserve = masque === null;
  let detail =
    `Sur le modèle sphérique, la courbure masque de ${m(bas)} à ${m(haut)} m à la base de `
    + "la cible ; sur le modèle plat, rien n'est masqué. ";
  detail += reserve
    ? "Le relief intermédiaire n'a pas pu être vérifié : la seconde "
      + 'condition est présumée, pas établie.'
    : 'Le relief intermédiaire laisse la visée entièrement dégagée : '
      + "l'écart observable revient bien à la courbure.";

  return { ...commun, discriminante: true, motif: detail, reserveRelief: reserve };
}
