/**
 * altimetrie-ign.ts — Le profil de terrain, demandé au service altimétrique de l'IGN.
 *
 * CE QUE CE MODULE CHANGE À LA POSTURE DU LAB, ET POURQUOI C'EST DIT
 * ─────────────────────────────────────────────────────────────────
 * Les autres outils du Lab ne transmettent rien : le fichier de l'utilisateur
 * ne quitte pas sa machine, et c'est une propriété qu'on peut vérifier en
 * coupant le réseau. Celui-ci est différent, et il faut le dire plutôt que le
 * laisser découvrir : interroger un modèle numérique de terrain suppose de
 * DEMANDER les altitudes à quelqu'un, donc de lui envoyer les coordonnées du
 * poste d'observation et de la cible.
 *
 * Trois conséquences, toutes assumées et toutes affichées dans l'interface :
 *   · l'appel n'est jamais automatique — il part sur une action explicite ;
 *   · les coordonnées transmises sont exactement celles saisies, rien d'autre ;
 *   · la SIMULATION ne dépend jamais de ce service. Elle tourne sur les
 *     coordonnées saisies, avant tout relevé, et un échec du service la laisse
 *     entière : seul le relief reste non évalué. Un outil qui exigerait le
 *     réseau pour fonctionner ferait dépendre une démonstration de la
 *     disponibilité d'un tiers.
 *
 * CE QUE CE MODULE N'A PAS ÉTÉ CONFRONTÉ À FAIRE
 * ──────────────────────────────────────────────
 * Il est écrit d'après le contrat publié du service. L'environnement où il a
 * été développé n'a pas d'accès sortant vers data.geopf.fr : il n'a donc JAMAIS
 * été exécuté contre le service réel. Ce qui est éprouvé, c'est la mise en
 * forme de la requête, l'interprétation d'une réponse conforme, et le refus
 * d'une réponse non conforme — pas que le service réponde ce qu'on croit.
 * Tant que ce n'est pas confronté sur le terrain, tout profil rendu ici porte
 * cette réserve, et l'interface l'affiche.
 *
 * Le RGE ALTI couvre la France et les DOM. Ailleurs, le service répond
 * -99999, qui veut dire « pas de donnée » et surtout pas « altitude zéro » :
 * c'est traité comme une lacune, jamais comme une mesure.
 */

import { ViseeError, vincentyDirect, vincentyInverse } from './noyau';
import { construireProfil, type ProfilTerrain } from './relief';

/** Le service altimétrique de la Géoplateforme. Ouvert, sans clé. */
export const RACINE_IGN = 'https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json';

/** La ressource altimétrique interrogée. Le nom fait partie de la provenance. */
export const RESSOURCE_IGN = 'ign_rge_alti_wld';

/**
 * La valeur que le service rend là où il n'a pas de donnée.
 * Ce n'est PAS une altitude. La confondre avec zéro placerait un gouffre de
 * 100 km sous la visée et déclarerait tout visible.
 */
export const SENTINEL_SANS_DONNEE = -99999.0;

/**
 * Nombre de points par requête.
 *
 * Le service accepte davantage, mais l'URL d'une requête GET est bornée par
 * les navigateurs et les intermédiaires autour de 8 000 caractères. Chaque
 * point coûte une vingtaine de caractères en longitude et autant en latitude :
 * 150 points laissent une marge confortable, et les lots sont enchaînés.
 */
export const POINTS_PAR_REQUETE = 150;

export class AltimetrieError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AltimetrieError';
  }
}

export interface PointVise {
  latitudeDeg: number;
  longitudeDeg: number;
  distanceM: number;
}

/**
 * Les points où interroger le terrain, placés SUR la géodésique.
 *
 * Ils sont calculés par la formule directe de Vincenty depuis le poste, en
 * suivant l'azimut de départ. Interpoler linéairement entre les deux
 * extrémités en latitude/longitude serait plus simple et faux : sur quelques
 * dizaines de kilomètres l'écart à la géodésique atteint plusieurs dizaines de
 * mètres, et le terrain serait échantillonné à côté du trajet — sans que rien
 * ne le signale.
 *
 * `pasM` est le pas visé ; le §33 demande 500 m au plus, ce qui est la valeur
 * par défaut. Le pas réel est ajusté pour tomber juste sur la distance totale,
 * et il est rendu avec le profil.
 */
export function pointsSurLaGeodesique(
  latA: number, lonA: number, latB: number, lonB: number, pasM = 500.0,
): { points: PointVise[]; distanceM: number; azimutDeg: number; pasReelM: number } {
  if (pasM <= 0) throw new AltimetrieError('Le pas d’échantillonnage doit être strictement positif.');
  const geo = vincentyInverse(latA, lonA, latB, lonB);
  if (geo.distanceM === 0) {
    throw new AltimetrieError('Les deux points sont confondus : il n’y a pas de trajet à profiler.');
  }
  const nbIntervalles = Math.max(1, Math.ceil(geo.distanceM / pasM));
  const pasReelM = geo.distanceM / nbIntervalles;
  const points: PointVise[] = [];
  for (let i = 0; i <= nbIntervalles; i++) {
    const d = i * pasReelM;
    // Aux deux extrémités, on emploie les coordonnées SAISIES plutôt que le
    // résultat d'un aller-retour de calcul : l'écart serait micrométrique,
    // mais rendre autre chose que ce que l'opérateur a écrit est une source
    // d'incompréhension sans contrepartie.
    if (i === 0) {
      points.push({ latitudeDeg: latA, longitudeDeg: lonA, distanceM: 0 });
    } else if (i === nbIntervalles) {
      points.push({ latitudeDeg: latB, longitudeDeg: lonB, distanceM: geo.distanceM });
    } else {
      const p = vincentyDirect(latA, lonA, geo.azimutDepartDeg, d);
      points.push({ latitudeDeg: p.latitudeDeg, longitudeDeg: p.longitudeDeg, distanceM: d });
    }
  }
  return { points, distanceM: geo.distanceM, azimutDeg: geo.azimutDepartDeg, pasReelM };
}

/** L'URL d'un lot. Exposée pour être vérifiable sans réseau. */
export function urlRequete(lot: PointVise[], ressource = RESSOURCE_IGN): string {
  if (lot.length === 0) throw new AltimetrieError('Lot vide : rien à demander.');
  // Six décimales valent une dizaine de centimètres : au-delà, on allongerait
  // l'URL sans rien gagner face à la résolution du modèle de terrain (1 m).
  const lon = lot.map((p) => p.longitudeDeg.toFixed(6)).join('|');
  const lat = lot.map((p) => p.latitudeDeg.toFixed(6)).join('|');
  const q = new URLSearchParams({
    lon, lat, resource: ressource, delimiter: '|', zonly: 'false', indent: 'false',
  });
  return `${RACINE_IGN}?${q.toString()}`;
}

interface ReponseIgn {
  elevations?: { z?: unknown; lon?: unknown; lat?: unknown; acc?: unknown }[];
}

/**
 * Lit une réponse du service et rend les altitudes, ou null là où il n'y en a pas.
 *
 * Rien n'est comblé : une altitude manquante reste manquante. Le §15.4 est
 * explicite, et ici la conséquence est directe — une lacune remplacée par zéro
 * ferait disparaître une montagne.
 */
export function altitudesDepuisReponse(brut: unknown, nbAttendu: number): (number | null)[] {
  const r = brut as ReponseIgn;
  if (!r || !Array.isArray(r.elevations)) {
    throw new AltimetrieError(
      'Réponse altimétrique non conforme : le champ « elevations » est absent ou n’est '
      + 'pas une liste. Aucun profil n’est construit à partir d’une réponse qu’on ne '
      + 'comprend pas.',
    );
  }
  if (r.elevations.length !== nbAttendu) {
    throw new AltimetrieError(
      `Réponse altimétrique incohérente : ${r.elevations.length} altitudes pour `
      + `${nbAttendu} points demandés. Les apparier dans cet état placerait le relief `
      + 'aux mauvaises distances.',
    );
  }
  return r.elevations.map((e) => {
    const z = typeof e?.z === 'number' ? e.z : Number(e?.z);
    if (!Number.isFinite(z)) return null;
    // Le service marque l'absence de donnée par un nombre, pas par un vide.
    if (z <= SENTINEL_SANS_DONNEE + 1) return null;
    return z;
  });
}

export interface ResultatProfil {
  profil: ProfilTerrain;
  distanceM: number;
  azimutDeg: number;
  /** Les points sans donnée, en distance depuis le poste. Jamais comblés. */
  lacunesM: number[];
  /** Ce que l'interface doit afficher avec le résultat. */
  reserve: string;
}

export const RESERVE_IGN =
  'Profil altimétrique fourni par le service RGE ALTI de l’IGN, interrogé depuis votre '
  + 'navigateur : les coordonnées du poste et de la cible lui ont été transmises. '
  + 'Ce que cela établit : ce que ce modèle de terrain déclare. Ce que cela n’établit '
  + 'pas : l’état réel du terrain à la date de l’observation — un modèle numérique a une '
  + 'date, une résolution et une incertitude verticale, et il ignore les bâtiments, la '
  + 'végétation et les ouvrages.';

type Fetch = (url: string) => Promise<{ ok: boolean; status: number; json: () => Promise<unknown> }>;

/**
 * Demande le profil au service, lot par lot.
 *
 * `recuperer` est injecté plutôt que d'appeler `fetch` directement : c'est ce
 * qui permet d'éprouver la mise en forme des requêtes et le traitement des
 * réponses sans réseau — et cet environnement n'en a pas vers data.geopf.fr.
 */
export async function profilDepuisIgn(
  latA: number, lonA: number, latB: number, lonB: number,
  options: { pasM?: number; recuperer?: Fetch; ressource?: string } = {},
): Promise<ResultatProfil> {
  const pasM = options.pasM ?? 500.0;
  const ressource = options.ressource ?? RESSOURCE_IGN;
  const recuperer: Fetch = options.recuperer
    ?? ((url) => fetch(url, { method: 'GET', headers: { Accept: 'application/json' } }));

  const { points, distanceM, azimutDeg, pasReelM } = pointsSurLaGeodesique(latA, lonA, latB, lonB, pasM);

  const altitudes: (number | null)[] = [];
  for (let i = 0; i < points.length; i += POINTS_PAR_REQUETE) {
    const lot = points.slice(i, i + POINTS_PAR_REQUETE);
    let reponse;
    try {
      reponse = await recuperer(urlRequete(lot, ressource));
    } catch (err) {
      throw new AltimetrieError(
        'Le service altimétrique de l’IGN n’a pas pu être joint : '
        + `${err instanceof Error ? err.message : String(err)}. `
        + 'La simulation, elle, ne dépend pas de ce service : elle a tourné sur vos '
        + 'coordonnées et reste valide. Le relief demeure NON ÉVALUÉ, ce qui n’est pas '
        + '« aucun obstacle ».',
      );
    }
    if (!reponse.ok) {
      throw new AltimetrieError(
        `Le service altimétrique de l’IGN a répondu ${reponse.status}. Le profil peut `
        + 'reste NON ÉVALUÉ, ce qui n’est pas « aucun obstacle ».',
      );
    }
    altitudes.push(...altitudesDepuisReponse(await reponse.json(), lot.length));
  }

  const couples: [number, number][] = [];
  const lacunesM: number[] = [];
  for (let i = 0; i < points.length; i++) {
    const z = altitudes[i];
    if (z === null) lacunesM.push(points[i].distanceM);
    else couples.push([points[i].distanceM, z]);
  }
  if (couples.length < 2) {
    throw new AltimetrieError(
      'Le service n’a rendu aucune altitude exploitable sur ce trajet. Le RGE ALTI '
      + 'couvre la France et les DOM ; ailleurs, il n’a pas de donnée — ce qui ne veut '
      + 'pas dire que le terrain est plat, et le relief reste NON ÉVALUÉ sur ce trajet.',
    );
  }

  return {
    profil: construireProfil(
      couples,
      `IGN — ${ressource}, interrogé le ${new Date().toISOString().slice(0, 10)}`,
      pasReelM,
      null,
    ),
    distanceM,
    azimutDeg,
    lacunesM,
    reserve: RESERVE_IGN,
  };
}

/**
 * Lit un profil saisi à la main : une paire « distance, altitude » par ligne.
 *
 * L'interface ne propose PAS cette saisie aujourd'hui — le relief a été
 * rétabli en relevé IGN seul. La fonction reste ici parce qu'elle sert aux
 * essais et aux vecteurs, et parce qu'elle est le chemin tout tracé le jour où
 * l'on voudra consigner ce qu'aucun modèle de terrain ne porte : une digue
 * récente, un cargo, une rangée d'arbres.
 *
 * C'est la voie sans réseau, et elle n'est pas un pis-aller : un opérateur qui
 * a relevé son propre profil au terrain a une donnée dont il connaît la
 * provenance, ce qui vaut mieux qu'un modèle national dont il ignore la date.
 * La source est donc exigée ici comme partout ailleurs.
 *
 * Les séparateurs admis sont la virgule, le point-virgule, la tabulation et
 * les espaces — un opérateur qui colle une colonne de tableur ne doit pas
 * avoir à la reformater. Le séparateur décimal peut être la virgule À
 * CONDITION que le séparateur de colonnes ne le soit pas : sinon « 1,5 » est
 * indécidable, et l'outil le dit plutôt que de trancher au hasard.
 */
export function profilDepuisTexte(texte: string, source: string, pasM: number | null = null): ProfilTerrain {
  const lignes = texte.split(/\r?\n/).map((l) => l.trim()).filter((l) => l !== '' && !l.startsWith('#'));
  if (lignes.length < 2) {
    throw new AltimetrieError(
      'Un profil demande au moins deux lignes « distance, altitude ».',
    );
  }
  const couples: [number, number][] = [];
  lignes.forEach((ligne, i) => {
    // Le séparateur de colonnes est déterminé PAR LIGNE, du plus explicite au
    // moins : point-virgule ou tabulation d'abord, puis espace, puis virgule.
    // C'est ce qui rend la virgule décimale utilisable — « 0 12,5 » se lit
    // comme deux champs séparés par l'espace, donc « 12,5 » reste un nombre.
    // Découper d'abord sur la virgule en ferait « 12 » et « 5 », silencieusement.
    const separateur = /[;\t]/.test(ligne) ? /[;\t]/ : (/\s/.test(ligne) ? /\s+/ : /,/);
    const champs = ligne.split(separateur).map((c) => c.trim()).filter((c) => c !== '');
    if (champs.length < 2) {
      throw new AltimetrieError(
        `Ligne ${i + 1} : « ${ligne} » ne contient pas deux nombres.`,
      );
    }
    const d = Number(champs[0].replace(',', '.'));
    const z = Number(champs[1].replace(',', '.'));
    if (!Number.isFinite(d) || !Number.isFinite(z)) {
      throw new AltimetrieError(`Ligne ${i + 1} : « ${ligne} » n’est pas lisible comme deux nombres.`);
    }
    couples.push([d, z]);
  });
  try {
    return construireProfil(couples, source, pasM, null);
  } catch (err) {
    if (err instanceof ViseeError || err instanceof Error) throw new AltimetrieError(err.message);
    throw err;
  }
}
