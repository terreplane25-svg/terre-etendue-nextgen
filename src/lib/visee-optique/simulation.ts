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
 * aussi, le relief de `relief.ts` — tous déjà épinglés.
 *
 * Ce qu'il ajoute est une RÈGLE DE LECTURE : à partir de quel écart entre les
 * deux modèles peut-on dire qu'une visée permet de les départager. Ce n'est pas
 * une loi physique, c'est une convention — écrite en constante nommée, affichée
 * à l'écran, et contestable, plutôt que cachée dans une condition d'interface.
 */

import type { AnalyseRelief } from './relief';
import { masqueParLeRelief } from './relief';

/**
 * Le plancher de lisibilité. Le modèle sphérique doit cacher au moins cette
 * FRACTION de la hauteur de la cible pour qu'on déclare la visée capable de
 * départager les deux modèles.
 *
 * 1 %, c'est-à-dire 1,1 m sur une cible de 110 m. Convention de lecture, pas
 * valeur normative : la changer change les verdicts.
 */
export const SEUIL_DISCRIMINATION_FRACTION = 0.01;

/**
 * La réfraction moyenne appliquée par défaut, et son enveloppe.
 *
 * 0,13 correspond à une atmosphère bien mélangée. Les bornes 0,10 et 0,40
 * encadrent ce qu'on rencontre au-dessus de l'eau sans avoir mesuré le profil
 * vertical de température — et on ne l'a jamais mesuré ici. Le calcul est donc
 * conduit sur l'ENVELOPPE : rendre un chiffre unique le ferait passer pour
 * mieux connu qu'il ne l'est.
 */
export const K_STANDARD = 0.13;
export const K_ENVELOPPE_MIN = 0.10;
export const K_ENVELOPPE_MAX = 0.40;

export const MOTIF_SEUIL =
  'Une visée est dite discriminante quand, même à la réfraction la plus '
  + 'défavorable, le modèle sphérique cache au moins 1 % de la hauteur de la '
  + 'cible. Ce plancher est une convention de lecture, pas une norme : sous '
  + "1 %, l'écart entre les deux modèles devient trop petit pour qu'une "
  + 'photographie ordinaire le montre, et annoncer « discriminante » '
  + 'promettrait une mesure que personne ne pourrait faire.';

export const MOTIF_REFRACTION =
  'La réfraction atmosphérique courbe les rayons lumineux et fait voir '
  + 'un peu plus loin que la géométrie pure. Faute de profil vertical de '
  + 'température mesuré sur le trajet, le calcul est conduit sur toute '
  + "l'enveloppe plausible au-dessus de l'eau — de 0,10 à 0,40, valeur "
  + 'moyenne 0,13 — et les résultats sont rendus comme un intervalle. Un '
  + "chiffre unique laisserait croire cette grandeur mieux connue qu'elle "
  + "ne l'est.";

/** Ce que la configuration permet de conclure, avant toute observation. */
export interface Verdict {
  discriminante: boolean;
  /** Le motif, en une phrase lisible par quelqu'un qui n'a lu aucun protocole. */
  motif: string;
  /**
   * La part de la cible que la courbure cache, au bord le plus favorable au
   * modèle plan — donc le plus défavorable à la discrimination.
   */
  fractionCacheeMin: number;
  fractionCacheeMax: number;
  hauteurCacheeMinM: number;
  hauteurCacheeMaxM: number;
  /**
   * Vrai quand le relief masque la cible dans les deux modèles : ce n'est
   * alors plus la courbure qui décide, et rien ne se départage.
   */
  masqueParLeRelief: boolean | null;
  seuilApplique: number;
}

/**
 * Le verdict, à partir des deux bornes de l'enveloppe de réfraction.
 *
 * Peu importe laquelle des deux cache le plus : le module les trie, parce que
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

  const cachees = [
    1 - globeMin.fractionVisibleCourbure,
    1 - globeMax.fractionVisibleCourbure,
  ].sort((a, b) => a - b);
  const cacheeMin = cachees[0];
  const cacheeMax = cachees[1];

  const commun = {
    fractionCacheeMin: cacheeMin,
    fractionCacheeMax: cacheeMax,
    hauteurCacheeMinM: cacheeMin * hauteurCibleM,
    hauteurCacheeMaxM: cacheeMax * hauteurCibleM,
    seuilApplique: SEUIL_DISCRIMINATION_FRACTION,
  };

  // Le relief d'abord : quand il masque, la question de la courbure ne se pose
  // plus. Les deux modèles prédisent la même chose, pour la même raison, et
  // cette raison n'est pas la forme de la Terre.
  const masque = masqueParLeRelief(globeMin);
  if (masque) {
    return {
      ...commun,
      discriminante: false,
      motif:
        'Le relief coupe la visée : les deux modèles prédisent une cible '
        + "cachée, pour la même raison, qui n'est pas la courbure. Cette "
        + "visée ne permet de départager ni l'un ni l'autre.",
      masqueParLeRelief: true,
    };
  }

  if (cacheeMin >= SEUIL_DISCRIMINATION_FRACTION) {
    return {
      ...commun,
      discriminante: true,
      motif:
        "Les deux modèles prédisent des choses différentes, et l'écart "
        + "reste visible sur toute l'enveloppe de réfraction. Une "
        + 'photographie de cette cible depuis ce point peut les départager.',
      masqueParLeRelief: masque,
    };
  }

  return {
    ...commun,
    discriminante: false,
    motif:
      'À la réfraction la plus favorable, le modèle sphérique ne cache '
      + 'presque rien : les deux modèles prédisent la même chose, à trop peu '
      + "près pour qu'une photographie les sépare. Il faut viser plus loin, "
      + 'ou plus bas, ou une cible plus courte.',
    masqueParLeRelief: masque,
  };
}
