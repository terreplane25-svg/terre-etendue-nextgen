/**
 * telemetrie.ts — Port TypeScript de `preuve_image.telemetrie` (outil B).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-B-preuve-image/preuve_image/telemetrie.py`.
 * Ce port est épinglé au Python par `vecteurs-or-extraction.json`.
 *
 * CE QUE CE MODULE LIT
 * ────────────────────
 * Les aéronefs civils écrivent leur état de vol dans le paquet XMP de chaque
 * image. Ce sont des champs d'espaces de noms propriétaires mais PUBLIÉS —
 * DJI, Parrot et Autel les documentent — donc lisibles sans conjecture.
 *
 * Pour le protocole ils comptent doublement : l'altitude relative donne la
 * hauteur de l'axe optique (la grandeur h du §12), et le tangage de la nacelle
 * dit si la visée était horizontale, sans quoi aucune mesure d'angle n'a de
 * sens.
 *
 * CE QU'IL N'ÉTABLIT PAS
 * ──────────────────────
 * Rien n'est vérifié : un champ XMP s'écrit et se modifie comme n'importe quel
 * texte. Deux pièges sont nommés plutôt que tus — l'altitude relative part du
 * point de DÉCOLLAGE, et la position de la station sol n'est presque jamais
 * écrite.
 */

export class TelemetrieError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'TelemetrieError';
  }
}

/**
 * Les espaces de noms de télémétrie qu'on sait nommer. Un préfixe absent est
 * relevé quand même sous son nom brut : savoir qu'il y a de la télémétrie
 * qu'on ne sait pas attribuer vaut mieux que de l'écarter.
 */
export const ESPACES_CONNUS: Record<string, string> = {
  'drone-dji': 'DJI',
  'drone-parrot': 'Parrot',
  Camera: 'espace « Camera » (Parrot, Autel, et DJI pour l’attitude)',
  drone: 'espace « drone » générique (Autel)',
  FLIR: 'FLIR (imagerie thermique)',
  GPano: 'panorama sphérique (Google)',
};

export const MOTIF_STATION_SOL_ABSENTE =
  'La position de la station sol n’est pas écrite dans le fichier. Ce que '
  + 'l’aéronef enregistre est SA position ; le point de décollage ne l’est '
  + 'qu’exceptionnellement, et jamais par les modèles courants. La renseigner '
  + 'avec la position du drone sous une autre étiquette donnerait un champ '
  + 'rempli et faux.';

export const AVERTISSEMENT_ALTITUDE_RELATIVE =
  'L’altitude relative est comptée depuis le POINT DE DÉCOLLAGE, pas depuis '
  + 'le sol survolé ni depuis le niveau de la mer. Un décollage depuis une '
  + 'colline la décale d’autant, et le fichier ne dit pas d’où l’appareil est '
  + 'parti. Pour servir de hauteur h au sens du §12, elle demande l’altitude '
  + 'du point de décollage, qui est une donnée EXTÉRIEURE au fichier.';

export interface ChampTelemetrie {
  prefixe: string;
  nom: string;
  /** Conservé à côté de la valeur : DJI écrit « +12.30 », et la forme compte. */
  brut: string;
  valeur: number | null;
  cle: string;
}

/** Le sens des champs qu'on connaît, par nom (le préfixe varie). */
const SENS: Record<string, string> = {
  AbsoluteAltitude: 'altitude absolue déclarée (au-dessus du niveau de référence GNSS)',
  RelativeAltitude: 'altitude au-dessus du point de décollage',
  AboveGroundAltitude: 'altitude au-dessus du sol survolé',
  GpsLatitude: 'latitude du porteur',
  GpsLongitude: 'longitude du porteur',
  GpsLongtitude: 'longitude du porteur (orthographe DJI)',
  GpsAltitude: 'altitude GNSS du porteur',
  GimbalRollDegree: 'roulis de la nacelle',
  GimbalYawDegree: 'lacet de la nacelle',
  GimbalPitchDegree: 'tangage de la nacelle',
  FlightRollDegree: 'roulis du porteur',
  FlightYawDegree: 'lacet du porteur',
  FlightPitchDegree: 'tangage du porteur',
  FlightXSpeed: 'vitesse selon X',
  FlightYSpeed: 'vitesse selon Y',
  FlightZSpeed: 'vitesse verticale',
  Yaw: 'lacet',
  Pitch: 'tangage',
  Roll: 'roulis',
  GPSXYAccuracy: 'incertitude horizontale annoncée',
  GPSZAccuracy: 'incertitude verticale annoncée',
  RtkFlag: 'état de la correction RTK',
  RtkStdLon: 'écart-type RTK en longitude',
  RtkStdLat: 'écart-type RTK en latitude',
  RtkStdHgt: 'écart-type RTK en altitude',
  CalibratedFocalLength: 'focale étalonnée déclarée',
  DewarpFlag: 'correction de distorsion appliquée',
  DewarpData: 'coefficients de correction de distorsion',
  GimbalReverse: 'nacelle retournée',
  CamReverse: 'caméra retournée',
  SelfData: 'champ libre du constructeur',
};

/**
 * Le tangage de nacelle, quel que soit le constructeur. L'ordre compte :
 * `GimbalPitchDegree` est le champ le plus spécifique et doit primer sur
 * `Pitch`, qui peut désigner le porteur.
 */
const NOMS_TANGAGE = ['GimbalPitchDegree', 'Pitch'];

export interface TelemetrieVol {
  present: boolean;
  origine: string | null;
  prefixes: string[];
  champs: ChampTelemetrie[];
  latitudeDeg: number | null;
  longitudeDeg: number | null;
  altitudeAbsolueM: number | null;
  altitudeRelativeM: number | null;
  altitudeSolM: number | null;
  tangageNacelleDeg: number | null;
  lacetNacelleDeg: number | null;
  roulisNacelleDeg: number | null;
  /** Ce que le fichier ne porte pas. Toujours null, avec son motif. */
  stationSol: null;
  motifStationSol: string;
  avertissementAltitude: string;
  sens: Record<string, string>;
}

/**
 * Vrai si le tangage de nacelle est à moins d'un degré de l'horizontale.
 * null quand il n'est pas déclaré — jamais false par défaut : une absence de
 * mesure n'établit pas que la visée était inclinée.
 */
export function viseeHorizontale(t: TelemetrieVol): boolean | null {
  if (t.tangageNacelleDeg === null) return null;
  return Math.abs(t.tangageNacelleDeg) <= 1.0;
}

/**
 * Convertit une valeur XMP en nombre, ou rend null si ce n'en est pas un.
 * Rendre 0 pour un champ illisible ferait une altitude au niveau de la mer.
 */
function nombre(brut: string): number | null {
  const m = /^\s*([+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)/.exec(brut);
  if (!m) return null;
  const v = Number(m[1]);
  return Number.isFinite(v) ? v : null;
}

const echapper = (s: string) => s.replace(/[.*+?^${}()|[\]\\-]/g, '\\$&');

/**
 * Les deux formes d'écriture du XMP. Un même champ peut apparaître en attribut
 * d'un rdf:Description ou en élément à part entière — les constructeurs
 * emploient les deux, parfois dans le même fichier. Ne traiter que la première
 * perdrait tout Parrot.
 */
function relever(texte: string, prefixes: string[]): ChampTelemetrie[] {
  const trouves = new Map<string, ChampTelemetrie>();
  for (const prefixe of prefixes) {
    const p = echapper(prefixe);
    for (const m of texte.matchAll(new RegExp(`${p}:([A-Za-z0-9_]+)\\s*=\\s*"([^"]*)"`, 'g'))) {
      const cle = `${prefixe}:${m[1]}`;
      if (!trouves.has(cle)) {
        trouves.set(cle, { prefixe, nom: m[1], brut: m[2], valeur: nombre(m[2]), cle });
      }
    }
    for (const m of texte.matchAll(new RegExp(`${p}:([A-Za-z0-9_]+)[^>]*>([^<]{0,200})<`, 'g'))) {
      const cle = `${prefixe}:${m[1]}`;
      if (!trouves.has(cle)) {
        trouves.set(cle, { prefixe, nom: m[1], brut: m[2].trim(), valeur: nombre(m[2]), cle });
      }
    }
  }
  return [...trouves.values()].sort((a, b) => (a.cle < b.cle ? -1 : a.cle > b.cle ? 1 : 0));
}

function premier(champs: ChampTelemetrie[], ...noms: string[]): number | null {
  for (const nom of noms) {
    for (const c of champs) {
      if (c.nom === nom && c.valeur !== null) return c.valeur;
    }
  }
  return null;
}

function vide(prefixes: string[] = []): TelemetrieVol {
  return {
    present: false, origine: null, prefixes, champs: [],
    latitudeDeg: null, longitudeDeg: null, altitudeAbsolueM: null,
    altitudeRelativeM: null, altitudeSolM: null, tangageNacelleDeg: null,
    lacetNacelleDeg: null, roulisNacelleDeg: null,
    stationSol: null, motifStationSol: MOTIF_STATION_SOL_ABSENTE,
    avertissementAltitude: AVERTISSEMENT_ALTITUDE_RELATIVE, sens: {},
  };
}

/**
 * Relève la télémétrie de vol dans un ou plusieurs paquets XMP.
 *
 * Accepte des octets ou du texte, un paquet ou une suite : les paquets viennent
 * selon les cas de `provenance`, de `conteneurs` ou d'`isobmff`, et leur
 * imposer une forme unique déplacerait seulement la conversion chez l'appelant.
 */
export function extraireTelemetrie(
  paquets: Uint8Array | string | (Uint8Array | string)[],
): TelemetrieVol {
  const liste = Array.isArray(paquets) ? paquets : [paquets];
  const decodeur = new TextDecoder('utf-8');
  const texte = liste
    .map((p) => (typeof p === 'string' ? p : decodeur.decode(p)))
    .join('\n');

  const prefixesVus: string[] = [];
  for (const prefixe of Object.keys(ESPACES_CONNUS)) {
    if (new RegExp(`${echapper(prefixe)}\\s*[:=]`).test(texte)) prefixesVus.push(prefixe);
  }
  // Un préfixe de télémétrie hors table est relevé sous son nom brut.
  for (const m of texte.matchAll(/xmlns:([A-Za-z0-9_-]*[Dd]rone[A-Za-z0-9_-]*)\s*=/g)) {
    if (!prefixesVus.includes(m[1])) prefixesVus.push(m[1]);
  }
  if (prefixesVus.length === 0) return vide();

  const champs = relever(texte, prefixesVus);
  if (champs.length === 0) return vide(prefixesVus);

  // « Camera » seul ne désigne aucun constructeur : c'est un espace partagé, et
  // l'annoncer comme une origine serait une attribution sans fondement.
  const specifiques = prefixesVus
    .filter((p) => ['drone-dji', 'drone-parrot', 'FLIR'].includes(p))
    .map((p) => ESPACES_CONNUS[p]);

  const sens: Record<string, string> = {};
  for (const c of champs) if (SENS[c.nom]) sens[c.cle] = SENS[c.nom];

  return {
    present: true,
    origine: specifiques.length > 0 ? specifiques[0] : null,
    prefixes: prefixesVus,
    champs,
    latitudeDeg: premier(champs, 'GpsLatitude'),
    // DJI écrit « GpsLongtitude », avec un t de trop, depuis des années. Ne
    // traiter que l'orthographe correcte ferait perdre la longitude sur la
    // majorité des images de drone en circulation, silencieusement.
    longitudeDeg: premier(champs, 'GpsLongitude', 'GpsLongtitude'),
    altitudeAbsolueM: premier(champs, 'AbsoluteAltitude', 'GpsAltitude'),
    altitudeRelativeM: premier(champs, 'RelativeAltitude'),
    altitudeSolM: premier(champs, 'AboveGroundAltitude'),
    tangageNacelleDeg: premier(champs, ...NOMS_TANGAGE),
    lacetNacelleDeg: premier(champs, 'GimbalYawDegree', 'Yaw'),
    roulisNacelleDeg: premier(champs, 'GimbalRollDegree', 'Roll'),
    stationSol: null,
    motifStationSol: MOTIF_STATION_SOL_ABSENTE,
    avertissementAltitude: AVERTISSEMENT_ALTITUDE_RELATIVE,
    sens,
  };
}
