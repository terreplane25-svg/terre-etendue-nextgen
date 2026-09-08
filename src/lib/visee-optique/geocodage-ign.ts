/**
 * geocodage-ign.ts — Une adresse tapée à la main, transformée en coordonnées.
 *
 * CE QUE CE MODULE FAIT, ET CE QU'IL NE BLOQUE JAMAIS
 * ──────────────────────────────────────────────────
 * Il lit d'abord la saisie comme des COORDONNÉES. « 50.94642, 1.75305 » est
 * compris sans qu'aucune requête ne parte : c'est le chemin normal, et il ne
 * dépend d'aucun réseau. Le service de géocodage n'est interrogé que si la
 * saisie n'est pas un couple de nombres.
 *
 * Conséquence voulue : la simulation tourne toujours sur les coordonnées
 * saisies, que le géocodage marche ou non. Quand il échoue, le module le dit
 * et demande les coordonnées exactes — il n'invente aucune position, et il
 * n'empêche rien.
 *
 * CE QUE CE MODULE N'A PAS ÉTÉ CONFRONTÉ À FAIRE
 * ──────────────────────────────────────────────
 * Comme la couche altimétrique, il est écrit d'après le contrat publié du
 * service. L'environnement où il a été développé n'a pas d'accès sortant vers
 * data.geopf.fr : il n'a JAMAIS été exécuté contre le service réel. Ce qui est
 * éprouvé, c'est la lecture d'un couple de coordonnées, la mise en forme de la
 * requête, l'interprétation d'une réponse conforme et le refus d'une réponse
 * non conforme — pas que le service réponde ce qu'on croit.
 */

/** Le service de géocodage de la Géoplateforme. Ouvert, sans clé. */
export const RACINE_GEOCODAGE = 'https://data.geopf.fr/geocodage/search';

export const RESERVE_GEOCODAGE =
  "Cette liaison avec le service de géocodage de l'IGN n'a jamais pu être "
  + "exécutée contre le service réel depuis l'environnement où elle a été "
  + 'écrite. Le contrat publié est respecté et les réponses non conformes sont '
  + 'refusées plutôt que comblées, mais la confrontation au service reste à faire.';

export class GeocodageError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'GeocodageError';
  }
}

export interface Position {
  latitude: number;
  longitude: number;
  /** D'où vient cette position : la saisie elle-même, ou le service nommé. */
  origine: string;
  /** Le libellé rendu par le service, quand c'est lui qui a répondu. */
  libelle: string | null;
}

/**
 * Lit un couple de coordonnées écrit à la main, ou rend null.
 *
 * Accepte le point comme la virgule décimale, séparés par une virgule, un
 * point-virgule ou une espace. « 50,94642 1,75305 » et « 50.94642, 1.75305 »
 * donnent le même résultat.
 *
 * Rendre null plutôt que lever : une saisie qui n'est pas un couple de nombres
 * est probablement une adresse, ce qui est un cas normal et pas une erreur.
 */
export function lireCoordonnees(saisie: string): Position | null {
  const t = saisie.trim();
  if (t === '') return null;

  // Deux nombres décimaux. La virgule sert de séparateur décimal ET de
  // séparateur de champs en français : on ne peut pas la traiter comme les
  // deux à la fois, donc la forme « 50,94 1,75 » est reconnue à part.
  const virguleDecimale = /^(-?\d+,\d+)[;\s]+(-?\d+,\d+)$/.exec(t);
  if (virguleDecimale) {
    return construire(
      Number(virguleDecimale[1].replace(',', '.')),
      Number(virguleDecimale[2].replace(',', '.')),
    );
  }
  const pointDecimal = /^(-?\d+(?:\.\d+)?)[,;\s]+(-?\d+(?:\.\d+)?)$/.exec(t);
  if (pointDecimal) {
    return construire(Number(pointDecimal[1]), Number(pointDecimal[2]));
  }
  return null;
}

function construire(latitude: number, longitude: number): Position | null {
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return null;
  // Hors de ces bornes, ce n'est pas une position : mieux vaut rendre null et
  // laisser la saisie être traitée comme une adresse que produire un point
  // que la géodésie accepterait sans broncher.
  if (Math.abs(latitude) > 90 || Math.abs(longitude) > 180) return null;
  return { latitude, longitude, origine: 'coordonnées saisies', libelle: null };
}

/**
 * Résout une saisie en position : coordonnées d'abord, géocodage ensuite.
 *
 * `fetchImpl` est injectable pour que le chemin réseau soit éprouvé sans
 * réseau — le service n'ayant jamais pu être atteint depuis l'environnement de
 * développement, c'est la seule manière de tester autre chose que l'espoir.
 */
export async function resoudrePosition(
  saisie: string,
  fetchImpl: typeof fetch = fetch,
): Promise<Position> {
  const directe = lireCoordonnees(saisie);
  if (directe !== null) return directe;

  const t = saisie.trim();
  if (t === '') throw new GeocodageError('Aucune position saisie.');

  const url = `${RACINE_GEOCODAGE}?q=${encodeURIComponent(t)}&limit=1&index=address`;
  let reponse: Response;
  try {
    reponse = await fetchImpl(url);
  } catch (err) {
    throw new GeocodageError(
      `Le service de géocodage de l'IGN est injoignable (${
        err instanceof Error ? err.message : String(err)
      }). Saisissez les coordonnées exactes — « latitude, longitude » — et la `
      + 'simulation tournera sans lui.',
    );
  }
  if (!reponse.ok) {
    throw new GeocodageError(
      `Le service de géocodage de l'IGN a répondu ${reponse.status}. Saisissez `
      + 'les coordonnées exactes — « latitude, longitude » — et la simulation '
      + 'tournera sans lui.',
    );
  }

  let doc: unknown;
  try {
    doc = await reponse.json();
  } catch {
    throw new GeocodageError(
      'La réponse du service de géocodage n’est pas du JSON. Saisissez les '
      + 'coordonnées exactes.',
    );
  }

  const position = premierPoint(doc);
  if (position === null) {
    throw new GeocodageError(
      `Aucune adresse trouvée pour « ${t} ». Saisissez les coordonnées exactes `
      + '— « latitude, longitude » — et la simulation tournera sans lui.',
    );
  }
  return position;
}

/**
 * Le premier résultat d'une réponse GeoJSON, ou null.
 *
 * Chaque champ est vérifié avant d'être lu. Une réponse non conforme est
 * refusée plutôt que comblée : une coordonnée manquante devenue zéro placerait
 * le point au large du golfe de Guinée sans que rien ne le signale.
 */
function premierPoint(doc: unknown): Position | null {
  if (typeof doc !== 'object' || doc === null) return null;
  const features = (doc as { features?: unknown }).features;
  if (!Array.isArray(features)) return null;
  // Sur une liste vide, `features[0]` vaut undefined et tombe ici : un
  // contrôle de longueur à part n'écarterait rien de plus.
  const f = features[0];
  if (typeof f !== 'object' || f === null) return null;

  const geometry = (f as { geometry?: unknown }).geometry;
  if (typeof geometry !== 'object' || geometry === null) return null;
  const coords = (geometry as { coordinates?: unknown }).coordinates;
  if (!Array.isArray(coords) || coords.length < 2) return null;
  // GeoJSON range la longitude AVANT la latitude. Les inverser placerait
  // Sangatte au large de la Somalie sans rien signaler.
  const [lon, lat] = coords;
  // `Number.isFinite` ne rend vrai que pour un vrai nombre fini : un contrôle
  // de type à part n'écarterait rien de plus, et se lirait comme une
  // protection qu'il n'apporte pas.
  if (!Number.isFinite(lon) || !Number.isFinite(lat)) return null;
  if (Math.abs(lat) > 90 || Math.abs(lon) > 180) return null;

  const props = (f as { properties?: unknown }).properties;
  const label = typeof props === 'object' && props !== null
    ? (props as { label?: unknown }).label
    : undefined;

  return {
    latitude: lat,
    longitude: lon,
    origine: 'géocodage IGN (Géoplateforme)',
    libelle: typeof label === 'string' ? label : null,
  };
}
