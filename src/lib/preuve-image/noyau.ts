/**
 * noyau.ts — Port TypeScript du paquet Python `preuve_image` (outil B).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-B-preuve-image/`, qui porte 137 tests. Ce port
 * existe parce que le vérificateur du site tourne dans le navigateur — et ce
 * n'est pas seulement une commodité : le fichier de l'utilisateur ne quitte
 * jamais sa machine, ce qu'un tiers de confiance doit pouvoir dire. Aucun
 * octet n'est transmis, aucune trace n'est laissée sur un serveur.
 *
 * Le port est épinglé au Python par les vecteurs de `vecteurs-or.json` et le
 * contrôle `scripts/verifier-port-preuve.mjs`. Toute correction se fait dans
 * le Python d'abord, puis se répercute ici, puis les vecteurs sont régénérés.
 *
 * Les renvois §N pointent vers le protocole « Portion visible d'une cible
 * éloignée au-dessus de la mer » v1.0.
 */

export class PreuveError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'PreuveError';
  }
}

/** §15.4 : une information indisponible se déclare, elle ne se devine pas. */
export const INDISPONIBLE = 'indisponible';

// --- §17.1 : intégrité ---

/**
 * SHA-256 d'un flux d'octets, en hexadécimal minuscule.
 *
 * Passe par WebCrypto, présent dans le navigateur comme dans Node ≥ 18 : la
 * même primitive des deux côtés, donc rien à réimplémenter.
 *
 * L'empreinte établit que le fichier n'a pas changé depuis sa déclaration.
 * Elle n'établit ni qu'il sort d'un appareil, ni la date de la prise de vue
 * (§17.1) : c'est une propriété d'intégrité, pas d'authenticité.
 */
export async function empreinteSha256(octets: Uint8Array | ArrayBuffer): Promise<string> {
  const buf = octets instanceof Uint8Array
    ? (octets.buffer.slice(octets.byteOffset, octets.byteOffset + octets.byteLength) as ArrayBuffer)
    : octets;
  const condensat = await crypto.subtle.digest('SHA-256', buf);
  return Array.from(new Uint8Array(condensat))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

/** Une empreinte bien formée : 64 caractères hexadécimaux. */
export function empreinteValide(e: string): boolean {
  const v = e.trim().toLowerCase();
  return v.length === 64 && /^[0-9a-f]+$/.test(v);
}

// --- §17.2 : traitements admis et exclus sur la copie de travail ---

export const OPERATIONS_ADMISES = new Set([
  'reglage_contraste_luminosite',
  'conversion_lineaire_sans_accentuation',
  'agrandissement_interpolation_declaree',
  'recadrage_declare_coordonnees_conservees',
]);

export const OPERATIONS_EXCLUES = new Set([
  'synthese_generative',
  'sur_resolution_apprise',
  'reconstruction_detail',
  'interpolation_creatrice',
  'accentuation_agressive',
  'reduction_bruit_non_lineaire',
  'fusion_multivues_structure_absente',
]);

/**
 * True si l'opération est admise, false si elle est exclue (§17.2).
 * Lève si le nom n'est ni l'un ni l'autre : une opération non reconnue se
 * classe avant d'entrer dans la chaîne, jamais présumée anodine (§15.4).
 */
export function classerOperation(nom: string): boolean {
  if (OPERATIONS_ADMISES.has(nom)) return true;
  if (OPERATIONS_EXCLUES.has(nom)) return false;
  throw new PreuveError(
    `Opération non reconnue : « ${nom} ». Doit être classée admise ou exclue ` +
      'avant d\'être journalisée (§17.2).',
  );
}

// --- §16, §19.1 : lecture EXIF ---

const TAG_MAKE = 0x010f;
const TAG_MODEL = 0x0110;
const TAG_ORIENTATION = 0x0112;
const TAG_EXIF_IFD_POINTER = 0x8769;
const TAG_GPS_IFD_POINTER = 0x8825;

const TAG_EXPOSURE_TIME = 0x829a;
const TAG_FNUMBER = 0x829d;
const TAG_ISO_SPEED = 0x8827;
const TAG_DATETIME_ORIGINAL = 0x9003;
const TAG_FOCAL_LENGTH = 0x920a;
const TAG_PIXEL_X_DIMENSION = 0xa002;
const TAG_PIXEL_Y_DIMENSION = 0xa003;
const TAG_FOCAL_LENGTH_35MM = 0xa405;
const TAG_LENS_MODEL = 0xa434;

// Ajoutés pour l'ingestion : tout ce que le §16 demande de LIRE sans rien conclure.
const TAG_IMAGE_WIDTH = 0x0100;
const TAG_IMAGE_LENGTH = 0x0101;
const TAG_X_RESOLUTION = 0x011a;
const TAG_Y_RESOLUTION = 0x011b;
const TAG_RESOLUTION_UNIT = 0x0128;
const TAG_SOFTWARE = 0x0131;
const TAG_DATETIME = 0x0132;
const TAG_ARTIST = 0x013b;
const TAG_COPYRIGHT = 0x8298;

// Décalages horaires (EXIF 2.31 et suivantes). Sans eux, DateTimeOriginal est une
// heure locale SANS fuseau : lui accoler un offset inventerait une information
// que le fichier ne porte pas.
const TAG_OFFSET_TIME = 0x9010;
const TAG_OFFSET_TIME_ORIGINAL = 0x9011;
const TAG_OFFSET_TIME_DIGITIZED = 0x9012;

const TAG_EXPOSURE_PROGRAM = 0x8822;
const TAG_DATETIME_DIGITIZED = 0x9004;
const TAG_FLASH = 0x9209;
const TAG_COLOR_SPACE = 0xa001;
const TAG_EXPOSURE_MODE = 0xa402;
const TAG_WHITE_BALANCE = 0xa403;
const TAG_DIGITAL_ZOOM_RATIO = 0xa404;
const TAG_SCENE_CAPTURE_TYPE = 0xa406;

// IFD1 : la miniature.
const TAG_JPEG_INTERCHANGE_FORMAT = 0x0201;
const TAG_JPEG_INTERCHANGE_FORMAT_LENGTH = 0x0202;
const TAG_COMPRESSION = 0x0103;

const TAG_GPS_LAT_REF = 1;
const TAG_GPS_LAT = 2;
const TAG_GPS_LON_REF = 3;
const TAG_GPS_LON = 4;
const TAG_GPS_ALT_REF = 5;
const TAG_GPS_ALT = 6;
const TAG_GPS_H_POSITIONING_ERROR = 31;

/** Taille en octets d'un élément de chaque type TIFF géré (spec TIFF 6.0 §2). */
const TAILLE_TYPE: Record<number, number> = {
  1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8,
};

type ValeurTiff = string | number | number[] | Uint8Array;

function decoderEntree(
  vue: DataView,
  petitBoutien: boolean,
  type: number,
  count: number,
  offsetChamp: number,
): ValeurTiff {
  const tailleElem = TAILLE_TYPE[type] ?? 1;
  const tailleTotale = tailleElem * count;
  let debut = offsetChamp;
  if (tailleTotale > 4) {
    debut = vue.getUint32(offsetChamp, petitBoutien);
    if (debut + tailleTotale > vue.byteLength) {
      throw new PreuveError('Bloc TIFF tronqué : donnée hors des limites du flux.');
    }
  }

  if (type === 2) {
    // ASCII, terminée par NUL.
    const brut = new Uint8Array(vue.buffer, vue.byteOffset + debut, tailleTotale);
    const fin = brut.indexOf(0);
    return new TextDecoder('ascii').decode(fin === -1 ? brut : brut.subarray(0, fin));
  }
  if (type === 1 || type === 7) {
    const vals = Array.from(new Uint8Array(vue.buffer, vue.byteOffset + debut, tailleTotale));
    return count === 1 ? vals[0] : vals;
  }
  if (type === 3) {
    const vals = Array.from({ length: count }, (_, i) => vue.getUint16(debut + i * 2, petitBoutien));
    return count === 1 ? vals[0] : vals;
  }
  if (type === 4) {
    const vals = Array.from({ length: count }, (_, i) => vue.getUint32(debut + i * 4, petitBoutien));
    return count === 1 ? vals[0] : vals;
  }
  if (type === 9) {
    const vals = Array.from({ length: count }, (_, i) => vue.getInt32(debut + i * 4, petitBoutien));
    return count === 1 ? vals[0] : vals;
  }
  if (type === 5 || type === 10) {
    const lire = type === 5
      ? (o: number) => vue.getUint32(o, petitBoutien)
      : (o: number) => vue.getInt32(o, petitBoutien);
    const vals = Array.from({ length: count }, (_, i) => {
      const num = lire(debut + i * 8);
      const den = lire(debut + i * 8 + 4);
      return den ? num / den : NaN;
    });
    return count === 1 ? vals[0] : vals;
  }
  // Type non géré : rendre les octets bruts plutôt qu'échouer.
  return new Uint8Array(vue.buffer, vue.byteOffset + debut, tailleTotale);
}

/**
  * Lit un IFD et rend aussi l'offset de l'IFD suivant (0 s'il n'y en a pas).
  * Les quatre octets qui suivent la dernière entrée pointent vers l'IFD suivant :
  * c'est par là que se trouve l'IFD1, celui de la miniature.
  */
function lireIfdEtSuivant(
  vue: DataView, offset: number, petitBoutien: boolean,
): { entrees: Map<number, ValeurTiff>; suivant: number } {
  if (offset + 2 > vue.byteLength) {
    throw new PreuveError("Offset d'IFD hors des limites du flux.");
  }
  const nb = vue.getUint16(offset, petitBoutien);
  const entrees = new Map<number, ValeurTiff>();
  let pos = offset + 2;
  for (let i = 0; i < nb; i++) {
    if (pos + 12 > vue.byteLength) {
      throw new PreuveError('IFD tronqué : entrée hors des limites du flux.');
    }
    const tag = vue.getUint16(pos, petitBoutien);
    const type = vue.getUint16(pos + 2, petitBoutien);
    const count = vue.getUint32(pos + 4, petitBoutien);
    entrees.set(tag, decoderEntree(vue, petitBoutien, type, count, pos + 8));
    pos += 12;
  }
  const suivant = pos + 4 <= vue.byteLength ? vue.getUint32(pos, petitBoutien) : 0;
  return { entrees, suivant };
}

function lireIfd(vue: DataView, offset: number, petitBoutien: boolean): Map<number, ValeurTiff> {
  return lireIfdEtSuivant(vue, offset, petitBoutien).entrees;
}

function dmsVersDegres(dms: ValeurTiff, ref: ValeurTiff | undefined): number {
  const t = dms as number[];
  const degres = t[0] + t[1] / 60.0 + t[2] / 3600.0;
  return ref === 'S' || ref === 'W' ? -degres : degres;
}

/**
 * Position lue dans l'IFD GPS (§16.1). `incertitudeM` reste nulle si l'appareil
 * n'a pas écrit GPSHPositioningError — le cas courant. Une absence ici n'est
 * jamais comblée par une valeur supposée (§15.4).
 */
export interface PositionGPS {
  latitudeDeg: number;
  longitudeDeg: number;
  altitudeM: number | null;
  incertitudeM: number | null;
  source: string;
}

/**
 * Les champs EXIF que le protocole utilise. Un champ nul n'a pas été écrit par
 * l'appareil — ce n'est pas la même chose qu'une déclaration « indisponible »
 * au sens du §15.4 : ici, personne n'a encore regardé.
 */
/**
 * Champs codés : on rend le code ET son libellé, jamais le libellé seul.
 * Un libellé est une interprétation ; le code est ce que l'appareil a écrit.
 * Les tables suivent CIPA DC-008 (EXIF 2.32).
 */
export const LIBELLE_EXPOSURE_MODE: Record<number, string> = {
  0: 'automatique', 1: 'manuel', 2: 'bracketing automatique',
};
export const LIBELLE_EXPOSURE_PROGRAM: Record<number, string> = {
  0: 'non défini', 1: 'manuel', 2: 'programme normal', 3: 'priorité ouverture',
  4: 'priorité vitesse', 5: 'création (profondeur de champ)', 6: 'action (vitesse)',
  7: 'portrait', 8: 'paysage',
};
export const LIBELLE_WHITE_BALANCE: Record<number, string> = { 0: 'automatique', 1: 'manuel' };
export const LIBELLE_COLOR_SPACE: Record<number, string> = {
  1: 'sRGB', 2: 'Adobe RGB', 0xffff: 'non calibré',
};
export const LIBELLE_SCENE_CAPTURE: Record<number, string> = {
  0: 'standard', 1: 'paysage', 2: 'portrait', 3: 'scène de nuit',
};
export const LIBELLE_RESOLUTION_UNIT: Record<number, string> = {
  1: 'sans unité', 2: 'pouce', 3: 'centimètre',
};

/**
 * Décode le champ Flash (0x9209), qui est un champ de bits et non un code.
 * bit 0 : déclenché ; bits 1-2 : lumière de retour ; bits 3-4 : mode ;
 * bit 5 : pas de flash sur l'appareil ; bit 6 : anti-yeux rouges.
 */
export function decrireFlash(code: number | null): string | null {
  if (code === null) return null;
  if (code & 0x20) return "l'appareil n'a pas de flash";
  const parties = [code & 0x01 ? 'déclenché' : 'non déclenché'];
  const mode = (code >> 3) & 0x03;
  if (mode === 1) parties.push('mode obligatoire');
  else if (mode === 2) parties.push('mode supprimé');
  else if (mode === 3) parties.push('mode automatique');
  const retour = (code >> 1) & 0x03;
  if (retour === 2) parties.push('lumière de retour non détectée');
  else if (retour === 3) parties.push('lumière de retour détectée');
  if (code & 0x40) parties.push('anti-yeux rouges');
  return parties.join(', ');
}

/**
 * Résolution ramenée en points par pouce, ou null si l'unité ne le permet pas.
 * L'unité 1 (« sans unité ») ne donne PAS de DPI : le nombre est alors un
 * rapport d'aspect, pas une densité. Le convertir inventerait une grandeur.
 */
export function versDpi(resolution: number | null, unite: number | null): number | null {
  if (resolution === null || unite === null || resolution <= 0) return null;
  if (unite === 2) return resolution;
  if (unite === 3) return resolution * 2.54;
  return null;
}

/**
 * La miniature de l'IFD1, telle qu'elle est stockée — ni décodée, ni recompressée.
 *
 * Ce que sa présence établit : un logiciel a écrit une vignette. Ce qu'elle
 * n'établit pas : que l'image principale n'a pas été modifiée. Un éditeur qui
 * régénère la miniature efface la trace ; seul un ÉCART entre elle et l'image
 * est un fait.
 */
export interface Miniature {
  offset: number;
  longueur: number;
  /**
   * Tampon propre, et non une vue sur le fichier : la miniature est affichée et
   * hachée séparément, et retenir tout le fichier pour quelques kilo-octets
   * n'aurait pas de sens. Le type est explicite pour que `new Blob([octets])`
   * l'accepte sous `--strict`.
   */
  octets: Uint8Array<ArrayBuffer>;
  compression: number | null;
  estJpeg: boolean;
}

export interface DonneesExif {
  fabricant: string | null;
  modele: string | null;
  objectif: string | null;
  focaleMm: number | null;
  focaleEquivalente35mm: number | null;
  ouverture: number | null;
  tempsPoseS: number | null;
  sensibiliteIso: number | null;
  largeurPx: number | null;
  hauteurPx: number | null;
  dateHeureOriginal: string | null;
  orientation: number | null;
  gps: PositionGPS | null;
  // --- Ajouts d'ingestion (§16) ---
  logiciel: string | null;
  dateHeureModification: string | null;
  dateHeureNumerisation: string | null;
  artiste: string | null;
  droits: string | null;
  largeurIfd0Px: number | null;
  hauteurIfd0Px: number | null;
  resolutionX: number | null;
  resolutionY: number | null;
  uniteResolution: number | null;
  dpiX: number | null;
  dpiY: number | null;
  espaceColorimetrique: number | null;
  modeExposition: number | null;
  programmeExposition: number | null;
  balanceBlancs: number | null;
  rapportZoomNumerique: number | null;
  typeScene: number | null;
  flash: number | null;
  miniature: Miniature | null;
  decalageHoraire: string | null;
  decalageHoraireOriginal: string | null;
  decalageHoraireNumerisation: string | null;
}

/** Les libellés des codes d'un relevé. Jamais à la place des codes. */
export function libellesExif(e: DonneesExif): Record<string, string | null> {
  return {
    flash: decrireFlash(e.flash),
    modeExposition: e.modeExposition === null ? null : LIBELLE_EXPOSURE_MODE[e.modeExposition] ?? null,
    programmeExposition: e.programmeExposition === null ? null : LIBELLE_EXPOSURE_PROGRAM[e.programmeExposition] ?? null,
    balanceBlancs: e.balanceBlancs === null ? null : LIBELLE_WHITE_BALANCE[e.balanceBlancs] ?? null,
    espaceColorimetrique: e.espaceColorimetrique === null ? null : LIBELLE_COLOR_SPACE[e.espaceColorimetrique] ?? null,
    typeScene: e.typeScene === null ? null : LIBELLE_SCENE_CAPTURE[e.typeScene] ?? null,
    uniteResolution: e.uniteResolution === null ? null : LIBELLE_RESOLUTION_UNIT[e.uniteResolution] ?? null,
  };
}

/**
 * Le §15 en dépend : un zoom numérique agrandit sans ajouter d'information.
 * 0 est le code « non employé » de la norme, pas un rapport nul.
 */
export function zoomNumeriqueApplique(e: DonneesExif): boolean | null {
  if (e.rapportZoomNumerique === null) return null;
  return e.rapportZoomNumerique > 1.0;
}

function ouNull<T>(m: Map<number, ValeurTiff>, tag: number): T | null {
  const v = m.get(tag);
  return v === undefined ? null : (v as unknown as T);
}

function construirePositionGps(ifd: Map<number, ValeurTiff>): PositionGPS | null {
  if (!ifd.has(TAG_GPS_LAT) || !ifd.has(TAG_GPS_LON)) return null;
  const latitude = dmsVersDegres(ifd.get(TAG_GPS_LAT)!, ifd.get(TAG_GPS_LAT_REF) ?? 'N');
  const longitude = dmsVersDegres(ifd.get(TAG_GPS_LON)!, ifd.get(TAG_GPS_LON_REF) ?? 'E');
  let altitude = ouNull<number>(ifd, TAG_GPS_ALT);
  if (altitude !== null && ifd.get(TAG_GPS_ALT_REF) === 1) altitude = -altitude;
  if (!(latitude >= -90.0 && latitude <= 90.0)) {
    throw new PreuveError('Latitude GPS hors bornes [-90 ; 90].');
  }
  if (!(longitude >= -180.0 && longitude <= 180.0)) {
    throw new PreuveError('Longitude GPS hors bornes [-180 ; 180].');
  }
  return {
    latitudeDeg: latitude,
    longitudeDeg: longitude,
    altitudeM: altitude,
    incertitudeM: ouNull<number>(ifd, TAG_GPS_H_POSITIONING_ERROR),
    source: 'EXIF GPS IFD',
  };
}

function extraireMiniature(donnees: Uint8Array, ifd1: Map<number, ValeurTiff>): Miniature | null {
  const offset = ifd1.get(TAG_JPEG_INTERCHANGE_FORMAT);
  const longueur = ifd1.get(TAG_JPEG_INTERCHANGE_FORMAT_LENGTH);
  if (typeof offset !== 'number' || typeof longueur !== 'number') return null;
  // Offsets incohérents : on ne rend pas une miniature tronquée qui passerait
  // pour entière.
  if (longueur <= 0 || offset < 0 || offset + longueur > donnees.length) return null;
  const octets = new Uint8Array(donnees.slice(offset, offset + longueur));
  const compression = ifd1.get(TAG_COMPRESSION);
  return {
    offset, longueur, octets,
    compression: typeof compression === 'number' ? compression : null,
    estJpeg: octets[0] === 0xff && octets[1] === 0xd8,
  };
}

/**
 * Lit un bloc TIFF/EXIF brut (en-tête « II » ou « MM »).
 * N'implémente pas la norme entière : IFD0, le sous-IFD Exif et le sous-IFD
 * GPS, et seulement les tags listés plus haut. Un tag absent donne un champ
 * nul, jamais une exception.
 */
export function lireExifDepuisTiff(donnees: Uint8Array): DonneesExif {
  if (donnees.length < 8) {
    throw new PreuveError('Bloc TIFF/EXIF trop court pour contenir un en-tête.');
  }
  const m0 = donnees[0], m1 = donnees[1];
  let petitBoutien: boolean;
  if (m0 === 0x49 && m1 === 0x49) petitBoutien = true;         // « II »
  else if (m0 === 0x4d && m1 === 0x4d) petitBoutien = false;   // « MM »
  else {
    const vu = String.fromCharCode(m0, m1);
    throw new PreuveError(`En-tête TIFF invalide : « ${vu} » n'est ni « II » ni « MM ».`);
  }
  const vue = new DataView(donnees.buffer, donnees.byteOffset, donnees.byteLength);
  const magique = vue.getUint16(2, petitBoutien);
  if (magique !== 42) {
    throw new PreuveError(`En-tête TIFF invalide : nombre magique ${magique} ≠ 42.`);
  }
  const premier = lireIfdEtSuivant(vue, vue.getUint32(4, petitBoutien), petitBoutien);
  const ifd0 = premier.entrees;
  // L'IFD1 est facultatif et souvent malformé chez les éditeurs : son échec ne
  // doit pas emporter la lecture des champs principaux.
  let ifd1 = new Map<number, ValeurTiff>();
  if (premier.suivant > 0 && premier.suivant < donnees.length) {
    try { ifd1 = lireIfd(vue, premier.suivant, petitBoutien); } catch { ifd1 = new Map(); }
  }
  const ifdExif = ifd0.has(TAG_EXIF_IFD_POINTER)
    ? lireIfd(vue, ifd0.get(TAG_EXIF_IFD_POINTER) as number, petitBoutien)
    : new Map<number, ValeurTiff>();
  const ifdGps = ifd0.has(TAG_GPS_IFD_POINTER)
    ? lireIfd(vue, ifd0.get(TAG_GPS_IFD_POINTER) as number, petitBoutien)
    : new Map<number, ValeurTiff>();

  const resolutionX = ouNull<number>(ifd0, TAG_X_RESOLUTION);
  const resolutionY = ouNull<number>(ifd0, TAG_Y_RESOLUTION);
  const unite = ouNull<number>(ifd0, TAG_RESOLUTION_UNIT);

  return {
    fabricant: ouNull<string>(ifd0, TAG_MAKE),
    modele: ouNull<string>(ifd0, TAG_MODEL),
    objectif: ouNull<string>(ifdExif, TAG_LENS_MODEL),
    focaleMm: ouNull<number>(ifdExif, TAG_FOCAL_LENGTH),
    focaleEquivalente35mm: ouNull<number>(ifdExif, TAG_FOCAL_LENGTH_35MM),
    ouverture: ouNull<number>(ifdExif, TAG_FNUMBER),
    tempsPoseS: ouNull<number>(ifdExif, TAG_EXPOSURE_TIME),
    sensibiliteIso: ouNull<number>(ifdExif, TAG_ISO_SPEED),
    largeurPx: ouNull<number>(ifdExif, TAG_PIXEL_X_DIMENSION),
    hauteurPx: ouNull<number>(ifdExif, TAG_PIXEL_Y_DIMENSION),
    dateHeureOriginal: ouNull<string>(ifdExif, TAG_DATETIME_ORIGINAL),
    orientation: ouNull<number>(ifd0, TAG_ORIENTATION),
    gps: ifdGps.size > 0 ? construirePositionGps(ifdGps) : null,
    logiciel: ouNull<string>(ifd0, TAG_SOFTWARE),
    dateHeureModification: ouNull<string>(ifd0, TAG_DATETIME),
    dateHeureNumerisation: ouNull<string>(ifdExif, TAG_DATETIME_DIGITIZED),
    artiste: ouNull<string>(ifd0, TAG_ARTIST),
    droits: ouNull<string>(ifd0, TAG_COPYRIGHT),
    largeurIfd0Px: ouNull<number>(ifd0, TAG_IMAGE_WIDTH),
    hauteurIfd0Px: ouNull<number>(ifd0, TAG_IMAGE_LENGTH),
    resolutionX,
    resolutionY,
    uniteResolution: unite,
    dpiX: versDpi(resolutionX, unite),
    dpiY: versDpi(resolutionY, unite),
    espaceColorimetrique: ouNull<number>(ifdExif, TAG_COLOR_SPACE),
    modeExposition: ouNull<number>(ifdExif, TAG_EXPOSURE_MODE),
    programmeExposition: ouNull<number>(ifdExif, TAG_EXPOSURE_PROGRAM),
    balanceBlancs: ouNull<number>(ifdExif, TAG_WHITE_BALANCE),
    rapportZoomNumerique: ouNull<number>(ifdExif, TAG_DIGITAL_ZOOM_RATIO),
    typeScene: ouNull<number>(ifdExif, TAG_SCENE_CAPTURE_TYPE),
    flash: ouNull<number>(ifdExif, TAG_FLASH),
    miniature: ifd1.size > 0 ? extraireMiniature(donnees, ifd1) : null,
    decalageHoraire: ouNull<string>(ifdExif, TAG_OFFSET_TIME),
    decalageHoraireOriginal: ouNull<string>(ifdExif, TAG_OFFSET_TIME_ORIGINAL),
    decalageHoraireNumerisation: ouNull<string>(ifdExif, TAG_OFFSET_TIME_DIGITIZED),
  };
}

/**
 * Localise le segment APP1/Exif d'un JPEG et délègue à lireExifDepuisTiff.
 * Balaie les marqueurs depuis le SOI jusqu'au premier APP1 portant l'en-tête
 * « Exif\0\0 », ou jusqu'au SOS, au-delà duquel aucune métadonnée ne peut
 * plus apparaître.
 */
/** « Exif » puis deux octets nuls — l'en-tête du segment APP1 porteur d'EXIF. */
const ENTETE_EXIF = [0x45, 0x78, 0x69, 0x66, 0x00, 0x00];

function estEnteteExif(donnees: Uint8Array, offset: number): boolean {
  return ENTETE_EXIF.every((octet, i) => donnees[offset + i] === octet);
}

export function lireExifDepuisJpeg(donnees: Uint8Array): DonneesExif {
  if (donnees.length < 2 || donnees[0] !== 0xff || donnees[1] !== 0xd8) {
    throw new PreuveError('Fichier non reconnu comme JPEG (SOI absent).');
  }
  const vue = new DataView(donnees.buffer, donnees.byteOffset, donnees.byteLength);
  let pos = 2;
  while (pos + 4 <= donnees.length) {
    if (donnees[pos] !== 0xff) {
      throw new PreuveError(`Flux JPEG malformé à l'octet ${pos} : marqueur attendu.`);
    }
    const marqueur = donnees[pos + 1];
    if (marqueur === 0xd8 || (marqueur >= 0xd0 && marqueur <= 0xd7)) {
      pos += 2;
      continue;
    }
    if (marqueur === 0xd9) break; // EOI
    if (marqueur === 0xda) break; // SOS : fin des métadonnées possibles
    const longueur = vue.getUint16(pos + 2, false);
    // L'en-tête est « Exif » suivi de DEUX OCTETS NULS, pas de deux espaces.
    // On compare les octets, jamais une chaîne décodée : écrire le sentinel
    // en clair dans un littéral y glisserait de vrais octets nuls, ce qui rend
    // le fichier source binaire et la comparaison invisible à la relecture.
    if (marqueur === 0xe1 && donnees.length >= pos + 10 && estEnteteExif(donnees, pos + 4)) {
      return lireExifDepuisTiff(donnees.subarray(pos + 10, pos + 2 + longueur));
    }
    pos += 2 + longueur;
  }
  throw new PreuveError('Aucun segment EXIF (APP1) trouvé dans ce JPEG.');
}

// --- Lecture d'ensemble, pour l'interface ---

export interface RapportFichier {
  nom: string;
  tailleOctets: number;
  typeDeclare: string;
  empreinte: string;
  exif: DonneesExif | null;
  /** Pourquoi l'EXIF n'a pas pu être lu, le cas échéant. Jamais masqué. */
  motifExifAbsent: string | null;
}

/**
 * Empreinte et métadonnées d'un fichier, sans jamais l'envoyer nulle part.
 *
 * Une lecture EXIF impossible n'invalide pas l'empreinte : les deux sont
 * indépendantes, et le motif de l'échec est rapporté tel quel plutôt
 * qu'escamoté.
 */
export async function analyserFichier(
  nom: string,
  typeDeclare: string,
  octets: Uint8Array,
): Promise<RapportFichier> {
  const empreinte = await empreinteSha256(octets);
  let exif: DonneesExif | null = null;
  let motif: string | null = null;
  try {
    exif = lireExifDepuisJpeg(octets);
  } catch (err) {
    motif = err instanceof Error ? err.message : String(err);
  }
  return {
    nom,
    tailleOctets: octets.length,
    typeDeclare: typeDeclare || INDISPONIBLE,
    empreinte,
    exif,
    motifExifAbsent: motif,
  };
}
