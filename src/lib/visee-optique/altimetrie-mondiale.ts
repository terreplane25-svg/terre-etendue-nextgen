/**
 * altimetrie-mondiale.ts — Le profil de terrain, partout sur la planète.
 *
 * POURQUOI UNE SECONDE SOURCE
 * ───────────────────────────
 * `altimetrie-ign.ts` interroge le RGE ALTI, qui couvre la France et les DOM
 * avec une résolution d'un mètre. C'est la meilleure donnée disponible — sur
 * son emprise. Hors de celle-ci, le service répond −99999, et une visée vers
 * le Kilimandjaro, l'Elbrouz ou depuis Chicago n'avait aucun relief.
 *
 * Ce module rend le relief disponible partout, en interrogeant l'API
 * d'élévation d'Open-Meteo — mondiale, sans clé, fondée sur le modèle
 * numérique Copernicus GLO-90.
 *
 * POURQUOI ELLE EST EMPLOYÉE PARTOUT, Y COMPRIS EN FRANCE
 * ──────────────────────────────────────────────────────
 * Deux raisons, et la première suffit.
 *
 *   1. Le PAS D'ÉCHANTILLONNAGE domine la résolution. Le profil est relevé
 *      tous les 250 m au mieux — voir `pasEchantillonnageM`. Sur un relevé
 *      aussi espacé, un modèle à 90 m et un modèle à 1 m rendent la même
 *      chose : l'avantage du RGE ALTI ne se voit pas, et il ne se verrait
 *      qu'en resserrant le pas, ce qui multiplierait les requêtes.
 *   2. Une seule source par profil, donc une seule RÉFÉRENCE VERTICALE.
 *      Mélanger une altitude NGF-IGN69 à une altitude rapportée à l'EGM2008
 *      introduit une erreur de plusieurs dizaines de mètres, muette et
 *      systématique — `relief.py` met déjà en garde contre exactement cela.
 *      Basculer de source en cours de trajet serait le plus sûr moyen de
 *      fabriquer un obstacle qui n'existe pas.
 *
 * `altimetrie-ign.ts` reste dans le dépôt, éprouvé et non branché. Il servira
 * le jour où un mode « France, au pas fin » aura un sens ; l'y raccorder
 * aujourd'hui n'ajouterait aucune précision utile et ajouterait un chemin de
 * plus à vérifier.
 *
 * CE QUE CE MODULE CHANGE À LA POSTURE DU LAB
 * ───────────────────────────────────────────
 * Les autres outils ne transmettent rien : le fichier de l'utilisateur ne
 * quitte pas sa machine. Celui-ci est différent, et il faut le dire plutôt que
 * le laisser découvrir — demander un profil de terrain suppose d'envoyer les
 * coordonnées du poste et de la cible à un tiers. Ce sont ces deux couples de
 * coordonnées et rien d'autre, et l'interface l'affiche avec le résultat.
 *
 * CE QUE CE MODULE N'A PAS ÉTÉ CONFRONTÉ À FAIRE
 * ──────────────────────────────────────────────
 * Il est écrit d'après le contrat publié du service. L'environnement où il a
 * été développé n'a d'accès sortant vers AUCUN service d'altitude — ni
 * Open-Meteo, ni l'IGN, ni les autres essayés. Il n'a donc jamais été exécuté
 * contre le service réel. Ce qui est éprouvé : la mise en forme des requêtes,
 * l'interprétation d'une réponse conforme, le refus d'une réponse qui ne l'est
 * pas, et le câblage complet contre une réponse simulée dans un navigateur.
 * Pas que le service réponde ce qu'on croit. Tant que ce n'est pas confronté
 * sur le terrain, tout profil rendu ici porte cette réserve.
 */

// La mise en place des points SUR la géodésique vit dans le module IGN et
// n'est pas dupliquée ici : une seule implémentation du semis, donc un seul
// endroit où une erreur de placement peut se produire.
import {
  AltimetrieError,
  type PointVise,
  type ResultatProfil,
  pointsSurLaGeodesique,
} from './altimetrie-ign';
import { construireProfil } from './relief';

/** L'API d'élévation d'Open-Meteo. Ouverte, sans clé. */
export const RACINE_MONDIALE = 'https://api.open-meteo.com/v1/elevation';

/**
 * Combien de points par requête.
 *
 * Le service en documente cent au plus. Les demander par lots plutôt qu'un par
 * un divise par cent le nombre d'allers-retours — sur une visée de 2 000 km au
 * pas de 2 km, mille points font dix requêtes et non mille.
 */
export const POINTS_PAR_REQUETE = 100;

export const SOURCE_MONDIALE = 'Copernicus GLO-90 (via Open-Meteo)';

export const RESERVE_MONDIALE =
  'Profil altimétrique fourni par l’API d’élévation d’Open-Meteo, fondée sur le '
  + 'modèle numérique de terrain Copernicus GLO-90, interrogée depuis votre '
  + 'navigateur : les coordonnées du poste et de la cible lui ont été transmises. '
  + 'Ce que cela établit : ce que ce modèle de terrain déclare. Ce que cela '
  + 'n’établit pas : l’état réel du terrain à la date de l’observation — un '
  + 'modèle numérique a une date, une résolution d’environ 90 m et une '
  + 'incertitude verticale, et il décrit le SOL : ni les bâtiments, ni la '
  + 'végétation, ni les ouvrages, ni rien de ce qui flotte.';

interface ReponseMondiale {
  elevation?: unknown;
}

type Fetch = (url: string) => Promise<{ ok: boolean; status: number; json: () => Promise<unknown> }>;

/** L'URL d'un lot. Exposée pour être vérifiable sans réseau. */
export function urlRequete(lot: PointVise[]): string {
  if (lot.length === 0) throw new AltimetrieError('Un lot vide ne se demande pas.');
  // Cinq décimales : environ un mètre au sol. Au-delà, on allonge l'URL sans
  // rien gagner face à une résolution de 90 m.
  const q = new URLSearchParams({
    latitude: lot.map((p) => p.latitudeDeg.toFixed(5)).join(','),
    longitude: lot.map((p) => p.longitudeDeg.toFixed(5)).join(','),
  });
  return `${RACINE_MONDIALE}?${q.toString()}`;
}

/**
 * Les altitudes d'une réponse, ou le refus de l'interpréter.
 *
 * Un compte qui ne correspond pas est REFUSÉ plutôt qu'apparié de travers :
 * apparier dans cet état placerait le relief aux mauvaises distances, et le
 * résultat resterait plausible.
 */
export function altitudesDepuisReponse(brut: unknown, nbAttendu: number): (number | null)[] {
  const r = brut as ReponseMondiale;
  if (!r || !Array.isArray(r.elevation)) {
    throw new AltimetrieError(
      'Réponse altimétrique non conforme : le champ « elevation » est absent ou '
      + 'n’est pas une liste. Aucun profil n’est construit à partir d’une '
      + 'réponse qu’on ne comprend pas.',
    );
  }
  if (r.elevation.length !== nbAttendu) {
    throw new AltimetrieError(
      `Réponse altimétrique incohérente : ${r.elevation.length} altitudes pour `
      + `${nbAttendu} points demandés. Les apparier dans cet état placerait le `
      + 'relief aux mauvaises distances.',
    );
  }
  return (r.elevation as unknown[]).map((e) => {
    const z = typeof e === 'number' ? e : Number(e);
    // Une valeur non numérique est une LACUNE, jamais une altitude nulle. Zéro
    // est une altitude légitime au-dessus de la mer, et la confondre avec
    // l'absence de donnée creuserait un trou là où il y a une plage.
    return Number.isFinite(z) ? z : null;
  });
}

/**
 * Demande le profil au service, lot par lot.
 *
 * `recuperer` est injecté plutôt que d'appeler `fetch` directement : c'est ce
 * qui permet d'éprouver la mise en forme des requêtes et le traitement des
 * réponses sans réseau — et cet environnement n'en a vers aucun service
 * d'altitude.
 */
export async function profilDepuisSourceMondiale(
  latA: number, lonA: number, latB: number, lonB: number,
  options: { pasM?: number; recuperer?: Fetch } = {},
): Promise<ResultatProfil> {
  const pasM = options.pasM ?? 500.0;
  const recuperer: Fetch = options.recuperer
    ?? ((url) => fetch(url, { method: 'GET', headers: { Accept: 'application/json' } }));

  const { points, distanceM, azimutDeg, pasReelM } =
    pointsSurLaGeodesique(latA, lonA, latB, lonB, pasM);

  const altitudes: (number | null)[] = [];
  for (let i = 0; i < points.length; i += POINTS_PAR_REQUETE) {
    const lot = points.slice(i, i + POINTS_PAR_REQUETE);
    let reponse;
    try {
      reponse = await recuperer(urlRequete(lot));
    } catch (err) {
      throw new AltimetrieError(
        'Le service d’élévation n’a pas pu être joint : '
        + `${err instanceof Error ? err.message : String(err)}. `
        + 'La simulation, elle, ne dépend pas de ce service : elle a tourné sur '
        + 'vos coordonnées et reste valide. Le relief demeure NON ÉVALUÉ, ce qui '
        + 'n’est pas « aucun obstacle ».',
      );
    }
    if (!reponse.ok) {
      throw new AltimetrieError(
        `Le service d’élévation a répondu ${reponse.status}. Le relief reste `
        + 'NON ÉVALUÉ, ce qui n’est pas « aucun obstacle ».',
      );
    }
    altitudes.push(...altitudesDepuisReponse(await reponse.json(), lot.length));
  }

  const couples: [number, number][] = [];
  const lacunesM: number[] = [];
  points.forEach((p, i) => {
    const z = altitudes[i];
    // Une lacune n'est jamais comblée. Interpoler entre deux sommets
    // inventerait une vallée, et la boucher par zéro inventerait une mer.
    if (z === null) lacunesM.push(p.distanceM);
    else couples.push([p.distanceM, z]);
  });

  if (couples.length < 2) {
    throw new AltimetrieError(
      'Le service n’a rendu aucune altitude exploitable sur ce trajet. Cela ne '
      + 'veut pas dire que le terrain est plat, et le relief reste NON ÉVALUÉ.',
    );
  }

  return {
    profil: construireProfil(couples, SOURCE_MONDIALE, pasReelM, null),
    distanceM,
    azimutDeg,
    lacunesM,
    reserve: RESERVE_MONDIALE,
  };
}
