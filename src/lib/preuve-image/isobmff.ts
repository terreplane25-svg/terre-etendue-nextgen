/**
 * isobmff.ts — Port TypeScript de `preuve_image.isobmff` (outil B).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-B-preuve-image/preuve_image/isobmff.py`. Ce
 * port est épinglé au Python par les vecteurs de `vecteurs-or-isobmff.json`,
 * que `scripts/verifier-port-isobmff.mjs` rejoue ici. Toute correction se fait
 * dans le Python d'abord.
 *
 * POURQUOI CE MODULE
 * ──────────────────
 * Un JPEG range ses métadonnées dans des segments APP, un TIFF dans des IFD :
 * le paquet lisait déjà les deux. Une troisième famille couvre aujourd'hui la
 * majorité des photographies prises au téléphone, et le vérificateur la
 * refusait en bloc : ISO/IEC 14496-12, le conteneur à boîtes du MP4, réemployé
 * par HEIF (.HEIC), AVIF, et le CR3 des Canon récents.
 *
 * Le bloc EXIF qu'ils portent est un TIFF ordinaire. Il n'y a donc pas de
 * second lecteur EXIF à écrire — seulement le bon bloc à trouver.
 *
 * Aucune image n'est DÉCODÉE. Une carte de profondeur est signalée présente,
 * avec sa taille et son type ; l'interpréter demanderait de décompresser du
 * HEVC, ce qui ne servirait pas le protocole.
 */

export class IsobmffError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'IsobmffError';
  }
}

/** La boîte `uuid` où Canon range les métadonnées d'un CR3. Publié, pas deviné. */
export const UUID_CANON_CR3 = new Uint8Array([
  0x85, 0xc0, 0xb6, 0x87, 0x82, 0x0f, 0x11, 0xe0,
  0x81, 0x11, 0xf4, 0xce, 0x46, 0x2b, 0x6a, 0x48,
]);

/**
 * Les boîtes qui en contiennent d'autres. Une boîte absente d'ici est traitée
 * comme opaque : on relève son type et sa taille, pas son contenu. Mieux vaut
 * ignorer une boîte qu'interpréter ses octets au hasard.
 */
const CONTENEURS = new Set([
  'moov', 'trak', 'mdia', 'minf', 'stbl', 'udta', 'iprp', 'ipco',
  'dinf', 'edts', 'mvex', 'moof', 'traf', 'grpl', 'mfra',
]);

/**
 * Conteneurs précédés d'un champ version+drapeaux de quatre octets (FullBox).
 * Les traiter comme des conteneurs ordinaires décale la lecture de quatre
 * octets : on ne lève pas d'erreur, on lit des boîtes qui n'existent pas — et
 * l'absence d'EXIF passe pour une propriété du fichier.
 */
const CONTENEURS_PLEINS = new Set(['meta']);

/** Les types auxiliaires qu'on sait NOMMER. Leur contenu n'est jamais décodé. */
export const TYPES_AUXILIAIRES: Record<string, string> = {
  'urn:com:apple:photo:2020:aux:hdrgainmap': 'carte de gain HDR (Apple)',
  'urn:com:apple:photo:2019:aux:hdrgainmap': 'carte de gain HDR (Apple, 2019)',
  'urn:com:apple:photo:2018:aux:hdrgainmap': 'carte de gain HDR (Apple, 2018)',
  'urn:mpeg:hevc:2015:auxid:1': 'carte de profondeur (alpha/profondeur MPEG)',
  'urn:mpeg:hevc:2015:auxid:2': 'carte de profondeur (MPEG)',
  'urn:com:apple:photo:2020:aux:semanticsegmentationmatte': 'masque de segmentation (Apple)',
};

export interface Boite {
  type: string;
  debut: number;
  taille: number;
  debutCharge: number;
  finCharge: number;
  profondeur: number;
  uuid: Uint8Array | null;
}

export interface Item {
  identifiant: number;
  type: string;
  nom: string | null;
  offset: number | null;
  longueur: number | null;
  typeAuxiliaire: string | null;
  referenceVers: number[];
  /**
   * Les dimensions DÉCLARÉES par la boîte `ispe` associée à cet item. null
   * quand `ipma` ne lui en associe aucune — jamais empruntées à une autre
   * `ispe` du fichier : donner à la photographie la taille de la carte de
   * profondeur serait faux sans que rien ne le signale.
   */
  largeur: number | null;
  hauteur: number | null;
}

export interface StructureIsobmff {
  marque: string;
  marquesCompatibles: string[];
  boites: Boite[];
  items: Item[];
  itemPrincipal: number | null;
  blocExif: Uint8Array | null;
  paquetsXmp: Uint8Array[];
  apercus: { origine: string; octets: Uint8Array }[];
  auxiliaires: Item[];
  versionCodec: string | null;
  makernotes: Uint8Array | null;
  /**
   * Les dimensions de l'item PRINCIPAL, lues dans sa boîte `ispe`. C'est la
   * mesure d'un HEIF ou d'un AVIF, celle qu'on confronte à la déclaration
   * EXIF. null quand aucune `ispe` n'est associée à l'item principal — un CR3
   * n'en porte pas du tout.
   */
  largeur: number | null;
  hauteur: number | null;
}

const MARQUES_HEIF = new Set(['heic', 'heix', 'heim', 'heis', 'hevc', 'mif1', 'msf1']);
const MARQUES_AVIF = new Set(['avif', 'avis']);

export function estHeif(s: StructureIsobmff): boolean {
  return [s.marque, ...s.marquesCompatibles].some((m) => MARQUES_HEIF.has(m));
}
export function estAvif(s: StructureIsobmff): boolean {
  return [s.marque, ...s.marquesCompatibles].some((m) => MARQUES_AVIF.has(m));
}
export function estCr3(s: StructureIsobmff): boolean {
  return s.marque === 'crx';
}

function ascii(d: Uint8Array, debut: number, fin: number): string {
  let out = '';
  for (let i = debut; i < fin && i < d.length; i++) out += String.fromCharCode(d[i]);
  return out;
}

// Les octets nuls sont écrits en ÉCHAPPEMENT, jamais en clair : un vrai NUL
// dans un littéral rend ce fichier source binaire et la comparaison invisible
// à la relecture. Le même piège s'est déjà produit dans noyau.ts.
const nettoyer = (s: string) => s.replace(/^[\u0000 ]+|[\u0000 ]+$/g, '');

/**
 * Parcourt les boîtes d'un intervalle, en descendant dans les conteneurs.
 *
 * Les tailles déclarées sont VÉRIFIÉES contre les bornes réelles : un fichier
 * fabriqué annonce volontiers des boîtes qui débordent, et suivre une taille
 * aberrante conduirait à lire n'importe quoi comme une métadonnée. Une boîte
 * incohérente arrête son niveau plutôt que de lever — le reste du fichier peut
 * rester exploitable.
 */
export function parcourirBoites(
  donnees: Uint8Array, debut = 0, fin: number | null = null,
  profondeur = 0, maxProfondeur = 12,
): Boite[] {
  const borne = fin === null ? donnees.length : fin;
  const boites: Boite[] = [];
  if (profondeur > maxProfondeur) return boites;
  const vue = new DataView(donnees.buffer, donnees.byteOffset, donnees.byteLength);
  let pos = debut;
  while (pos + 8 <= borne) {
    let taille = vue.getUint32(pos, false);
    const type = ascii(donnees, pos + 4, pos + 8);
    let entete = 8;
    let uuid: Uint8Array | null = null;
    if (taille === 1) {
      if (pos + 16 > borne) break;
      // Taille sur 64 bits. Au-delà de 2^53 les entiers JavaScript perdent en
      // exactitude, mais une boîte de 9 pétaoctets n'existe pas : la borne
      // réelle du fichier écarte le cas juste après.
      taille = Number(vue.getBigUint64(pos + 8, false));
      entete = 16;
    } else if (taille === 0) {
      taille = borne - pos;
    }
    if (type === 'uuid') {
      if (pos + entete + 16 > borne) break;
      uuid = donnees.slice(pos + entete, pos + entete + 16);
      entete += 16;
    }
    if (taille < entete || pos + taille > borne) break;

    const b: Boite = {
      type, debut: pos, taille,
      debutCharge: pos + entete, finCharge: pos + taille,
      profondeur, uuid,
    };
    boites.push(b);

    if (CONTENEURS.has(type)) {
      boites.push(...parcourirBoites(donnees, b.debutCharge, b.finCharge, profondeur + 1, maxProfondeur));
    } else if (CONTENEURS_PLEINS.has(type)) {
      if (b.debutCharge + 4 <= b.finCharge) {
        boites.push(...parcourirBoites(donnees, b.debutCharge + 4, b.finCharge, profondeur + 1, maxProfondeur));
      }
    } else if (type === 'uuid' && uuid !== null && UUID_CANON_CR3.every((o, i) => uuid![i] === o)) {
      boites.push(...parcourirBoites(donnees, b.debutCharge, b.finCharge, profondeur + 1, maxProfondeur));
    }
    pos += taille;
  }
  return boites;
}

function lireIinf(donnees: Uint8Array, b: Boite): Map<number, [string, string | null]> {
  const out = new Map<number, [string, string | null]>();
  const vue = new DataView(donnees.buffer, donnees.byteOffset, donnees.byteLength);
  let pos = b.debutCharge;
  if (pos + 4 > b.finCharge) return out;
  const version = donnees[pos];
  pos += 4;
  let nb: number;
  if (version === 0) {
    if (pos + 2 > b.finCharge) return out;
    nb = vue.getUint16(pos, false); pos += 2;
  } else {
    if (pos + 4 > b.finCharge) return out;
    nb = vue.getUint32(pos, false); pos += 4;
  }
  for (let i = 0; i < nb; i++) {
    if (pos + 8 > b.finCharge) break;
    const taille = vue.getUint32(pos, false);
    if (ascii(donnees, pos + 4, pos + 8) !== 'infe' || taille < 12 || pos + taille > b.finCharge) break;
    const v = donnees[pos + 8];
    let p = pos + 12;
    if (v >= 2) {
      const largeurId = v === 2 ? 2 : 4;
      if (p + largeurId + 4 > b.finCharge) break;
      const ident = v === 2 ? vue.getUint16(p, false) : vue.getUint32(p, false);
      p += largeurId + 2;
      const typeItem = ascii(donnees, p, p + 4);
      p += 4;
      let finNom = -1;
      for (let k = p; k < pos + taille; k++) if (donnees[k] === 0) { finNom = k; break; }
      const nom = finNom !== -1 ? ascii(donnees, p, finNom) : '';
      out.set(ident, [typeItem, nom || null]);
    }
    pos += taille;
  }
  return out;
}

/**
 * Les emplacements d'items. Seule la méthode de construction 0 (offset dans le
 * fichier) est traitée : les items rangés dans `idat` ou par référence externe
 * sont IGNORÉS plutôt que lus de travers — rendre un offset faux placerait des
 * octets arbitraires à la place d'un bloc EXIF.
 */
function lireIloc(donnees: Uint8Array, b: Boite): Map<number, [number, number]> {
  const out = new Map<number, [number, number]>();
  const vue = new DataView(donnees.buffer, donnees.byteOffset, donnees.byteLength);
  let pos = b.debutCharge;
  if (pos + 8 > b.finCharge) return out;
  const version = donnees[pos];
  pos += 4;
  const tailles = donnees[pos];
  const offsetSize = tailles >> 4;
  const lengthSize = tailles & 0xf;
  const tailles2 = donnees[pos + 1];
  const baseOffsetSize = tailles2 >> 4;
  const indexSize = (version === 1 || version === 2) ? (tailles2 & 0xf) : 0;
  pos += 2;

  let nb: number;
  if (version < 2) { nb = vue.getUint16(pos, false); pos += 2; }
  else { nb = vue.getUint32(pos, false); pos += 4; }

  const lire = (n: number): number => {
    if (n === 0) return 0;
    let v = 0;
    for (let i = 0; i < n; i++) v = v * 256 + donnees[pos + i];
    pos += n;
    return v;
  };

  for (let i = 0; i < nb; i++) {
    if (pos + 2 > b.finCharge) break;
    const ident = version < 2 ? lire(2) : lire(4);
    let methode = 0;
    if (version === 1 || version === 2) {
      methode = vue.getUint16(pos, false) & 0xf;
      pos += 2;
    }
    pos += 2; // data_reference_index
    const base = lire(baseOffsetSize);
    if (pos + 2 > b.finCharge) break;
    const nbExtents = vue.getUint16(pos, false);
    pos += 2;
    let premier: [number, number] | null = null;
    for (let j = 0; j < nbExtents; j++) {
      lire(indexSize);
      const off = lire(offsetSize);
      const lon = lire(lengthSize);
      if (j === 0) premier = [base + off, lon];
    }
    if (methode === 0 && premier !== null) out.set(ident, premier);
  }
  return out;
}

function lireIref(donnees: Uint8Array, b: Boite): Map<number, number[]> {
  const out = new Map<number, number[]>();
  const vue = new DataView(donnees.buffer, donnees.byteOffset, donnees.byteLength);
  let pos = b.debutCharge;
  if (pos + 4 > b.finCharge) return out;
  const version = donnees[pos];
  pos += 4;
  const largeur = version === 0 ? 2 : 4;
  const lireN = (p: number) => {
    let v = 0;
    for (let i = 0; i < largeur; i++) v = v * 256 + donnees[p + i];
    return v;
  };
  while (pos + 8 <= b.finCharge) {
    const taille = vue.getUint32(pos, false);
    if (taille < 12 || pos + taille > b.finCharge) break;
    let p = pos + 8;
    const de = lireN(p);
    p += largeur;
    if (p + 2 > pos + taille) break;
    const nb = vue.getUint16(p, false);
    p += 2;
    const vers: number[] = [];
    for (let i = 0; i < nb; i++) {
      if (p + largeur > pos + taille) break;
      vers.push(lireN(p));
      p += largeur;
    }
    out.set(de, [...(out.get(de) ?? []), ...vers]);
    pos += taille;
  }
  return out;
}

/**
 * Les dimensions déclarées par une ImageSpatialExtentsProperty.
 *
 * FullBox : quatre octets de version et de drapeaux, puis largeur et hauteur
 * sur quatre octets chacune. Une dimension nulle est REFUSÉE plutôt que
 * rendue : elle ne décrit aucune image, et diviserait par zéro au calcul du
 * rapport d'aspect. Une dimension énorme, en revanche, est rendue telle
 * quelle — c'est ce que le fichier DÉCLARE, et le rôle de ce module s'arrête là.
 */
function lireIspe(donnees: Uint8Array, b: Boite): [number, number] | null {
  if (b.finCharge - b.debutCharge < 12) return null;
  const vue = new DataView(donnees.buffer, donnees.byteOffset, donnees.byteLength);
  const largeur = vue.getUint32(b.debutCharge + 4, false);
  const hauteur = vue.getUint32(b.debutCharge + 8, false);
  if (largeur === 0 || hauteur === 0) return null;
  return [largeur, hauteur];
}

/**
 * Les associations item → propriétés : identifiant → indices dans `ipco`.
 *
 * Les indices sont ceux des ENFANTS DIRECTS d'`ipco`, numérotés à partir de 1
 * dans l'ordre du fichier. L'indice 0 signifie « aucune » et n'est pas écarté
 * ici : c'est l'appelant qui borne, une seule fois.
 *
 * Chaque association porte un bit `essential` sur le bit de poids fort du
 * champ. Il dit qu'un lecteur qui ne comprend pas la propriété doit refuser
 * l'item — ce n'est pas notre cas. Il est donc MASQUÉ, pas interprété ; ne pas
 * le masquer ajouterait 128 ou 32 768 à l'indice, qui pointerait hors de la
 * liste : les dimensions disparaîtraient en silence, sans erreur levée.
 */
function lireIpma(donnees: Uint8Array, b: Boite): Map<number, number[]> {
  const out = new Map<number, number[]>();
  const vue = new DataView(donnees.buffer, donnees.byteOffset, donnees.byteLength);
  let pos = b.debutCharge;
  if (pos + 8 > b.finCharge) return out;
  const version = donnees[pos];
  const flags = (donnees[pos + 1] << 16) | (donnees[pos + 2] << 8) | donnees[pos + 3];
  pos += 4;
  const nb = vue.getUint32(pos, false);
  pos += 4;
  const largeurId = version < 1 ? 2 : 4;
  const largeurIndex = (flags & 1) ? 2 : 1;
  const masque = largeurIndex === 2 ? 0x7fff : 0x7f;

  const lireN = (p: number, n: number): number => {
    let v = 0;
    for (let i = 0; i < n; i++) v = v * 256 + donnees[p + i];
    return v;
  };

  for (let e = 0; e < nb; e++) {
    if (pos + largeurId + 1 > b.finCharge) break;
    const ident = lireN(pos, largeurId);
    pos += largeurId;
    const nbAssoc = donnees[pos];
    pos += 1;
    const indices: number[] = [];
    for (let a = 0; a < nbAssoc; a++) {
      if (pos + largeurIndex > b.finCharge) break;
      indices.push(lireN(pos, largeurIndex) & masque);
      pos += largeurIndex;
    }
    out.set(ident, [...(out.get(ident) ?? []), ...indices]);
  }
  return out;
}

/**
 * Les boîtes filles immédiates d'un conteneur, DANS L'ORDRE du fichier.
 *
 * L'ordre est ce qui donne son sens aux indices d'`ipma` : ils comptent les
 * enfants d'`ipco` à partir de 1. `parcourirBoites` rend les boîtes dans
 * l'ordre du fichier ; filtrer sur la profondeur et sur les bornes du parent
 * conserve cet ordre sans le reconstruire.
 */
function enfantsDirects(boites: Boite[], parent: Boite): Boite[] {
  return boites.filter((b) => b.profondeur === parent.profondeur + 1
    && b.debut >= parent.debutCharge && b.debut < parent.finCharge);
}

/**
 * Les dimensions de chaque item, par le chemin `iprp` → `ipma` + `ipco`.
 *
 * L'association est résolue POUR DE BON, jamais approchée par « la plus grande
 * `ispe` du fichier ». Un HEIF d'iPhone en porte au moins deux : celle de la
 * photographie et celle de la carte de gain HDR. L'heuristique donnerait la
 * bonne réponse la plupart du temps, et la mauvaise sans prévenir — la
 * quasi-justesse qu'un relevé probatoire ne peut pas se permettre.
 *
 * Chaque `ipma` est lu contre l'`ipco` de SON `iprp` : les indices sont
 * relatifs à ce conteneur-là, et les croiser associerait des propriétés au
 * hasard.
 */
function dimensionsParItem(donnees: Uint8Array, boites: Boite[]): Map<number, [number, number]> {
  const out = new Map<number, [number, number]>();
  for (const iprp of boites.filter((b) => b.type === 'iprp')) {
    const enfants = enfantsDirects(boites, iprp);
    const ipco = enfants.find((b) => b.type === 'ipco');
    if (!ipco) continue;
    const proprietes = enfantsDirects(boites, ipco);
    for (const ipma of enfants.filter((b) => b.type === 'ipma')) {
      for (const [ident, indices] of lireIpma(donnees, ipma)) {
        for (const i of indices) {
          if (i < 1 || i > proprietes.length) continue;
          const p = proprietes[i - 1];
          if (p.type !== 'ispe') continue;
          const dim = lireIspe(donnees, p);
          // La PREMIÈRE `ispe` associée fait foi : un item qui en porterait
          // deux est incohérent, et prendre la seconde reviendrait à préférer
          // arbitrairement la dernière écrite.
          if (dim !== null && !out.has(ident)) out.set(ident, dim);
        }
      }
    }
  }
  return out;
}

/**
 * Le bloc TIFF d'un item « Exif » de HEIF.
 *
 * L'item commence par un entier de quatre octets donnant le décalage jusqu'à
 * l'en-tête TIFF — presque toujours 6, pour sauter « Exif\0\0 ». On s'y fie,
 * puis on VÉRIFIE que l'en-tête est bien là. Suivre aveuglément un décalage
 * aberrant donnerait un bloc décalé, que le lecteur EXIF déclarerait corrompu
 * alors que le fichier est sain.
 */
function blocExifDepuisItem(charge: Uint8Array): Uint8Array | null {
  if (charge.length < 8) return null;
  const vue = new DataView(charge.buffer, charge.byteOffset, charge.byteLength);
  const debut = 4 + vue.getUint32(0, false);
  if (debut >= 0 && debut <= charge.length - 8) {
    const m = ascii(charge, debut, debut + 2);
    if (m === 'II' || m === 'MM') return charge.subarray(debut);
  }
  for (const marqueur of [[0x49, 0x49, 0x2a, 0x00], [0x4d, 0x4d, 0x00, 0x2a]]) {
    for (let i = 0; i + 4 <= charge.length; i++) {
      if (marqueur.every((o, k) => charge[i + k] === o)) return charge.subarray(i);
    }
  }
  return null;
}

export function analyserIsobmff(donnees: Uint8Array): StructureIsobmff {
  if (donnees.length < 12 || ascii(donnees, 4, 8) !== 'ftyp') {
    throw new IsobmffError(
      'Ce fichier ne commence pas par une boîte « ftyp » : ce n’est pas un conteneur '
      + 'ISOBMFF, ou il est tronqué en tête.',
    );
  }
  const vue = new DataView(donnees.buffer, donnees.byteOffset, donnees.byteLength);
  const tailleFtyp = vue.getUint32(0, false);
  const marque = nettoyer(ascii(donnees, 8, 12));
  const compat: string[] = [];
  if (tailleFtyp >= 16 && tailleFtyp <= donnees.length) {
    for (let i = 16; i < tailleFtyp; i += 4) {
      const m = nettoyer(ascii(donnees, i, i + 4));
      if (m) compat.push(m);
    }
  }

  const s: StructureIsobmff = {
    marque, marquesCompatibles: compat, boites: parcourirBoites(donnees),
    items: [], itemPrincipal: null, blocExif: null, paquetsXmp: [],
    apercus: [], auxiliaires: [], versionCodec: null, makernotes: null,
    largeur: null, hauteur: null,
  };

  const parType = new Map<string, Boite[]>();
  for (const b of s.boites) parType.set(b.type, [...(parType.get(b.type) ?? []), b]);

  const infos = new Map<number, [string, string | null]>();
  for (const b of parType.get('iinf') ?? []) for (const [k, v] of lireIinf(donnees, b)) infos.set(k, v);
  const emplacements = new Map<number, [number, number]>();
  for (const b of parType.get('iloc') ?? []) for (const [k, v] of lireIloc(donnees, b)) emplacements.set(k, v);
  const references = new Map<number, number[]>();
  for (const b of parType.get('iref') ?? []) for (const [k, v] of lireIref(donnees, b)) references.set(k, v);
  for (const b of parType.get('pitm') ?? []) {
    if (b.finCharge - b.debutCharge >= 6) {
      const version = donnees[b.debutCharge];
      const p = b.debutCharge + 4;
      s.itemPrincipal = version === 0 ? vue.getUint16(p, false) : vue.getUint32(p, false);
    }
  }

  const dimensions = dimensionsParItem(donnees, s.boites);
  if (s.itemPrincipal !== null && dimensions.has(s.itemPrincipal)) {
    [s.largeur, s.hauteur] = dimensions.get(s.itemPrincipal)!;
  }

  const apercus: { origine: string; octets: Uint8Array }[] = [];
  const xmp: Uint8Array[] = [];
  const auxiliaires: Item[] = [];

  for (const ident of [...infos.keys()].sort((a, b2) => a - b2)) {
    const [typeItem, nom] = infos.get(ident)!;
    const emp = emplacements.get(ident);
    const offset = emp ? emp[0] : null;
    const longueur = emp ? emp[1] : null;
    // `Uint8Array` explicite : `new Uint8Array(0)` infère le type le plus
    // étroit, et une vue sur le fichier ne s'y assigne plus sous --strict.
    // Déclarer le type large plutôt que caster garde la vérification.
    let charge: Uint8Array = new Uint8Array(0);
    if (offset !== null && longueur !== null && offset >= 0 && offset <= donnees.length - longueur) {
      charge = donnees.subarray(offset, offset + longueur);
    }

    let aux: string | null = null;
    if (nom && TYPES_AUXILIAIRES[nom]) aux = TYPES_AUXILIAIRES[nom];
    else if (nom && nom.startsWith('urn:')) {
      // Un type auxiliaire inconnu est NOMMÉ plutôt qu'écarté : savoir qu'il y
      // a une couche qu'on ne sait pas lire est une information ; la taire
      // n'en est pas une.
      aux = `auxiliaire non répertorié — ${nom}`;
    }

    const dim = dimensions.get(ident) ?? null;
    const item: Item = {
      identifiant: ident, type: typeItem, nom, offset, longueur,
      typeAuxiliaire: aux, referenceVers: references.get(ident) ?? [],
      largeur: dim ? dim[0] : null, hauteur: dim ? dim[1] : null,
    };
    s.items.push(item);

    const tete = ascii(charge, 0, 5);
    if (typeItem === 'Exif' && charge.length > 0 && s.blocExif === null) {
      s.blocExif = blocExifDepuisItem(charge);
    } else if (typeItem === 'mime' && (tete === '<?xpa' || tete === '<x:xm' || tete === '<?xml')) {
      xmp.push(charge);
    } else if (typeItem === 'mime' && ascii(charge, 0, Math.min(2048, charge.length)).includes('adobe:ns:meta')) {
      xmp.push(charge);
    }
    if (aux !== null) auxiliaires.push(item);
    if (charge.length >= 2 && charge[0] === 0xff && charge[1] === 0xd8) {
      apercus.push({ origine: `item ${ident} (${typeItem})`, octets: charge });
    }
  }

  // CR3 : CMT1 porte l'IFD0, CMT3 les MakerNotes, CNCV la version du codec.
  for (const b of parType.get('CMT1') ?? []) {
    const bloc = donnees.subarray(b.debutCharge, b.finCharge);
    const m = ascii(bloc, 0, 2);
    if ((m === 'II' || m === 'MM') && s.blocExif === null) s.blocExif = bloc;
  }
  for (const b of parType.get('CMT3') ?? []) s.makernotes = donnees.subarray(b.debutCharge, b.finCharge);
  for (const b of parType.get('CNCV') ?? []) {
    s.versionCodec = ascii(donnees, b.debutCharge, b.finCharge).replace(/\u0000+$/g, '');
  }
  for (const nomBoite of ['PRVW', 'THMB']) {
    for (const b of parType.get(nomBoite) ?? []) {
      const charge = donnees.subarray(b.debutCharge, b.finCharge);
      for (let i = 0; i + 3 <= charge.length; i++) {
        if (charge[i] === 0xff && charge[i + 1] === 0xd8 && charge[i + 2] === 0xff) {
          apercus.push({ origine: `boîte ${nomBoite}`, octets: charge.subarray(i) });
          break;
        }
      }
    }
  }

  for (const b of parType.get('xml ') ?? []) xmp.push(donnees.subarray(b.debutCharge, b.finCharge));

  s.paquetsXmp = xmp;
  s.auxiliaires = auxiliaires;
  s.apercus = apercus.sort((a, b) => b.octets.length - a.octets.length);
  return s;
}
