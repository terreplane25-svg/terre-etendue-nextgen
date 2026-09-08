/**
 * simulation.ts — Port TypeScript de `visee_optique.simulation` (outil A).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-A-visee-optique/visee_optique/simulation.py`.
 * Ce port est épinglé au Python par `vecteurs-or-simulation.json`, que
 * `scripts/verifier-port-simulation.mjs` rejoue ici.
 *
 * GÉOMÉTRIE PURE : PLUS AUCUN MODÈLE DE TERRAIN
 * ─────────────────────────────────────────────
 * Le simulateur ne consulte plus de profil altimétrique et ne détecte plus
 * d'obstacle local. Le calcul porte exclusivement sur la ligne de visée
 * théorique entre les deux altitudes saisies.
 *
 * Ce n'est pas un renoncement, c'est un partage des rôles : chercher ce qui
 * bouche la vue depuis un poste donné relève du contrôle de l'analyste SUR
 * L'IMAGE RÉELLE — une haie, un cargo, un bâtiment récent ne figurent dans
 * aucun modèle numérique de terrain.
 *
 * CE QUI SE MESURE : LE PIED DE LA CIBLE, PAS SON SOMMET
 * ──────────────────────────────────────────────────────
 * C'est le PIED de la cible qui disparaît en premier sous l'horizon, et c'est
 * là que les deux modèles divergent en premier. La grandeur jugée est donc la
 * hauteur masquée EN PARTANT DE LA BASE. Elle n'est pas bornée à la hauteur de
 * la cible : au-delà de la distance limite elle continue de croître et dit de
 * combien la cible est passée sous l'horizon.
 */

import { rayonEffectif } from './noyau';

/**
 * Le seuil critique. La courbure doit masquer au moins cette FRACTION de la
 * hauteur de la cible, EN PARTANT DE LA BASE, pour que la visée départage.
 *
 * 10 %, c'est-à-dire 11 m sur une cible de 110 m : une différence qu'une
 * photographie montre sans ambiguïté. Convention de lecture, pas norme.
 */
export const SEUIL_DISCRIMINATION_FRACTION = 0.10;

/**
 * La réfraction appliquée. `K_STANDARD` est la valeur moyenne qui sert au
 * calcul principal et au verdict ; les deux bornes encadrent ce qu'on peut
 * rencontrer au-dessus de l'eau sans avoir mesuré le profil vertical de
 * température, et servent à AFFICHER l'écart que cette ignorance laisse.
 */
export const K_STANDARD = 0.13;
export const K_ENVELOPPE_MIN = 0.10;
export const K_ENVELOPPE_MAX = 0.40;

/**
 * Le plancher admis dans le formulaire pour un k saisi à la main.
 *
 * Le plafond, lui, n'est pas une convention : `rayonEffectif` refuse déjà
 * k ≥ 1, où le rayon épouse la surface et la construction ne s'applique plus.
 * Le plancher est une commodité de saisie — sous −1, le rayon effectif tombe
 * sous la moitié du rayon terrestre, ce qui ne décrit aucune atmosphère
 * rencontrée. Il est nommé pour qu'on puisse le contester.
 */
export const K_PLANCHER_ADMIS = -1.0;

/**
 * Ce qui est dit au visiteur quand k ≥ 1.
 *
 * La RÈGLE reste celle de `rayonEffectif`, qui décide seul : on l'appelle et on
 * rhabille son refus. Le message du paquet de référence parle de « §8 » et de
 * « Tableau 8 » — juste dans un protocole, illisible dans un simulateur dont on
 * a retiré tous les renvois. Deux messages pour une seule règle ne divergeront
 * pas, puisque le second ne décide de rien.
 */
export const MOTIF_CONDUIT_OPTIQUE =
  'Un coefficient de réfraction supérieur ou égal à 1 décrit un conduit '
  + "optique : le rayon lumineux se courbe autant que la surface et ne s'en "
  + "détache plus. La construction géométrique employée ici ne s'applique "
  + 'plus du tout dans ce régime, et aucun résultat ne serait interprétable. '
  + "Les valeurs rencontrées au-dessus de l'eau vont de 0 à 0,4 environ.";

/**
 * Ce que le modèle plat masque à la base : rien, à toute distance. Nommé
 * plutôt qu'écrit en dur, pour que la comparaison se lise comme une
 * soustraction entre deux prédictions et non comme un cas particulier.
 */
export const MASQUE_MODELE_PLAT_M = 0.0;

export const MOTIF_SEUIL =
  'Une visée est dite discriminante quand la courbure masque au moins 10 % '
  + 'de la hauteur de la cible en partant de sa base. Sous ce seuil, les deux '
  + "modèles prédisent des choses trop proches pour qu'une photographie les "
  + 'sépare, et annoncer « discriminante » promettrait une mesure que personne '
  + 'ne pourrait faire. Ce seuil est une convention de lecture, pas une norme.';

export const MOTIF_REFRACTION_STANDARD =
  'La réfraction atmosphérique courbe les rayons lumineux et fait voir '
  + 'un peu plus loin que la géométrie pure. Le calcul emploie le gradient '
  + "moyen k = 0,13, celui d'une atmosphère bien mélangée. Faute de profil "
  + "vertical de température mesuré sur le trajet, l'écart que cette "
  + 'ignorance laisse est affiché à part, entre k = 0,10 et k = 0,40.';

/**
 * Refuse un coefficient de réfraction hors du domaine de la construction.
 *
 * Le plafond vient de la physique et non d'ici : `rayonEffectif` lève pour
 * k ≥ 1. On le rejoue avec le même message plutôt que d'en inventer un second,
 * qui divergerait le jour où l'un des deux changerait.
 */
export function verifierK(k: number): void {
  if (!Number.isFinite(k)) {
    throw new Error('Le coefficient de réfraction doit être un nombre.');
  }
  if (k < K_PLANCHER_ADMIS) {
    throw new Error(
      `Coefficient de réfraction sous le plancher admis (${K_PLANCHER_ADMIS.toFixed(2)}) : le `
      + 'rayon effectif tomberait sous la moitié du rayon terrestre, ce '
      + 'qui ne décrit aucune atmosphère rencontrée.',
    );
  }
  // C'est `rayonEffectif` qui DÉCIDE ; on ne fait que rhabiller son refus dans
  // la langue de l'interface. Réécrire la condition ici créerait deux règles
  // pour un seul phénomène.
  try {
    rayonEffectif(1.0, k);
  } catch {
    throw new Error(MOTIF_CONDUIT_OPTIQUE);
  }
}

/**
 * La phrase affichée, avec le coefficient RÉELLEMENT employé.
 *
 * Une phrase figée qui nommerait 0,13 alors que le calcul a tourné sur 0,18
 * serait un mensonge d'affichage — le genre qui survit longtemps parce que
 * personne ne relit la prose.
 */
export function motifRefraction(k: number): string {
  verifierK(k);
  if (k === K_STANDARD) return MOTIF_REFRACTION_STANDARD;
  return (
    'La réfraction atmosphérique courbe les rayons lumineux et fait voir '
    + 'un peu plus loin que la géométrie pure. Le calcul a été mené avec le '
    + `coefficient PERSONNALISÉ k = ${kf(k)}, saisi par vous, et non avec la `
    + 'moyenne standard de 0,13. Cette valeur est déclarée, pas mesurée par '
    + "cet outil : c'est à vous de la justifier par un relevé du profil "
    + "vertical de température sur le trajet. Aucune enveloppe n'est "
    + 'affichée, puisque vous affirmez connaître la valeur.'
  );
}

export const MOTIF_SANS_RELIEF =
  'Ce simulateur ne consulte aucun modèle de terrain : il calcule la ligne '
  + "de visée théorique entre les deux altitudes saisies, et rien d'autre. Ce "
  + 'qui bouche réellement la vue depuis un poste — une haie, un cargo, un '
  + 'bâtiment récent — ne figure dans aucun modèle numérique et se constate '
  + "sur l'image. C'est le contrôle de l'analyste, pas celui du simulateur.";

/** Ce que la géométrie permet de conclure, avant toute observation. */
export interface Verdict {
  discriminante: boolean;
  /** Le motif, en une phrase lisible par quelqu'un qui n'a lu aucun protocole. */
  motif: string;
  /**
   * La hauteur masquée EN PARTANT DE LA BASE sur le modèle sphérique. Non
   * bornée à H : au-delà de la distance limite elle continue de croître.
   */
  hauteurMasqueeBaseM: number;
  /** La même chose en fraction de la hauteur de la cible. Peut dépasser 1. */
  fractionMasqueeBase: number;
  /** Ce que le modèle plat masque : rien, à toute distance. */
  hauteurMasqueePlatM: number;
  /**
   * L'écart entre les deux prédictions. C'est ce qu'une photographie doit
   * pouvoir montrer, et c'est exactement `hauteurMasqueeBaseM` puisque le
   * modèle plat ne masque rien.
   */
  ecartEntreModelesM: number;
  seuilApplique: number;
}

const m = (x: number) => x.toFixed(1).replace('.', ',');
const pc = (f: number) => (100 * f).toFixed(1).replace('.', ',');
/** Un coefficient de réfraction, à deux décimales, virgule française. */
const kf = (x: number) => x.toFixed(2).replace('.', ',');

/**
 * Le verdict, sur la seule occultation à la base.
 *
 * `hauteurMasqueeBaseM` est `c` calculé au gradient moyen K_STANDARD.
 */
export function juger(hauteurMasqueeBaseM: number, hauteurCibleM: number): Verdict {
  if (hauteurCibleM <= 0) {
    throw new Error('La hauteur de la cible doit être strictement positive.');
  }
  if (hauteurMasqueeBaseM < 0) {
    throw new Error('La hauteur masquée ne peut pas être négative.');
  }

  const fraction = hauteurMasqueeBaseM / hauteurCibleM;
  // L'écart s'écrit comme la SOUSTRACTION des deux prédictions, parce que
  // c'est ce qu'il est. Arithmétiquement, c'est aujourd'hui une identité : le
  // modèle plat masque zéro, donc l'écart vaut l'occultation sphérique. Aucun
  // test ne peut distinguer cette ligne de `= hauteurMasqueeBaseM`, et c'est
  // écrit ici pour que personne ne la prenne pour un garde-fou.
  const ecart = hauteurMasqueeBaseM - MASQUE_MODELE_PLAT_M;

  const commun = {
    hauteurMasqueeBaseM,
    fractionMasqueeBase: fraction,
    hauteurMasqueePlatM: MASQUE_MODELE_PLAT_M,
    ecartEntreModelesM: ecart,
    seuilApplique: SEUIL_DISCRIMINATION_FRACTION,
  };

  if (fraction >= SEUIL_DISCRIMINATION_FRACTION) {
    return {
      ...commun,
      discriminante: true,
      motif:
        `Le modèle sphérique masque ${m(hauteurMasqueeBaseM)} m à la base de la cible ; le modèle `
        + `plat n'en masque aucun. L'écart entre les deux prédictions est de `
        + `${m(ecart)} m, soit ${pc(fraction)} % de la hauteur de la cible — assez pour qu'une `
        + 'photographie les départage.',
    };
  }

  return {
    ...commun,
    discriminante: false,
    motif:
      `Le modèle sphérique ne masque que ${m(hauteurMasqueeBaseM)} m à la base de la cible, soit `
      + `${pc(fraction)} % de sa hauteur — sous le seuil de ${pc(SEUIL_DISCRIMINATION_FRACTION)} %. Les deux modèles `
      + 'prédisent presque la même chose : il faut viser plus loin, ou plus '
      + 'bas, ou une cible plus courte.',
  };
}
