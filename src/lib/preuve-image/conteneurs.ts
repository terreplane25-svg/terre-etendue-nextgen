/**
 * conteneurs.ts — Port TypeScript de `preuve_image.conteneurs` (outil B).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-B-preuve-image/preuve_image/conteneurs.py`.
 * Ce port est épinglé au Python par `vecteurs-or-conteneurs.json`, que
 * `scripts/verifier-port-conteneurs.mjs` rejoue ici.
 *
 * POURQUOI CE MODULE
 * ──────────────────
 * `noyau.ts` lit l'EXIF, `isobmff.ts` les conteneurs à boîtes, `provenance.ts`
 * le C2PA, le XMP et l'IPTC. Restait tout le reste : les blocs propres à chaque
 * format, qui portent souvent la SEULE information disponible quand l'EXIF a
 * été purgé — le cas ordinaire d'une capture d'écran, d'une image réexportée
 * par un service web, ou d'un fichier passé par une messagerie.
 *
 * POURQUOI C'EST ASYNCHRONE
 * ─────────────────────────
 * Les chunks zTXt et iCCP d'un PNG sont compressés en zlib. Le navigateur sait
 * les décompresser, mais seulement par `DecompressionStream`, qui est
 * asynchrone. Le Python, lui, appelle `zlib.decompress` de façon synchrone.
 * Les deux rendent la même chose ; c'est la forme d'appel qui diffère, et les
 * vecteurs comparent les résultats, pas les signatures.
 *
 * Aucune image n'est DÉCOMPRESSÉE, et rien n'est interprété : un chunk de type
 * inconnu est listé avec sa taille et son type, jamais deviné.
 */

export class ConteneurError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ConteneurError';
  }
}

export interface Chunk {
  type: string;
  offset: number;
  longueur: number;
  /** null quand le format n'en porte pas — seul le PNG a des CRC. */
  crcValide: boolean | null;
  /** Une description courte quand le type est documenté. Jamais devinée. */
  role: string | null;
}

export interface TexteEmbarque {
  origine: string;
  cle: string;
  valeur: string;
  /**
   * Vrai si le texte était compressé à l'origine. L'information compte : un
   * texte compressé échappe à une recherche de chaînes dans le fichier brut,
   * et quelqu'un qui aurait inspecté le fichier « à la main » ne l'aurait pas vu.
   */
  compresse: boolean;
  langue: string | null;
}

/** Classes de profil ICC (ICC.1:2010, tableau 17). */
export const CLASSES_ICC: Record<string, string> = {
  scnr: "périphérique d'entrée (scanner, capteur)",
  mntr: "périphérique d'affichage (écran)",
  prtr: 'périphérique de sortie (imprimante)',
  link: 'liaison entre périphériques',
  spac: 'espace colorimétrique abstrait',
  abst: 'transformation abstraite',
  nmcl: 'nuancier nommé',
};

export const ESPACES_ICC: Record<string, string> = {
  'RGB ': 'RVB', GRAY: 'niveaux de gris', CMYK: 'CMJN',
  'XYZ ': 'CIE XYZ', 'Lab ': 'CIE L*a*b*', YCbr: 'YCbCr',
};

export interface ProfilIcc {
  octets: number;
  version: string;
  classe: string;
  classeLibelle: string | null;
  espace: string;
  espaceLibelle: string | null;
  espaceConnexion: string;
  plateforme: string | null;
  createur: string | null;
  date: string | null;
  /** C'est elle qui porte le nom lisible : « Display P3 », « sRGB IEC61966-2.1 ». */
  description: string | null;
  copyright: string | null;
}

export interface InventaireConteneur {
  format: string;
  octets: number;
  largeur: number | null;
  hauteur: number | null;
  profondeurBits: number | null;
  chunks: Chunk[];
  textes: TexteEmbarque[];
  profilIcc: ProfilIcc | null;
  blocExif: Uint8Array | null;
  paquetsXmp: Uint8Array[];
  dpiX: number | null;
  dpiY: number | null;
  proprietes: Record<string, unknown>;
  /** Les chunks dont le CRC ne tombe pas juste. Vide n'atteste de rien. */
  chunksCorrompus: string[];
}

function vide(format: string, octets: number): InventaireConteneur {
  return {
    format, octets, largeur: null, hauteur: null, profondeurBits: null,
    chunks: [], textes: [], profilIcc: null, blocExif: null, paquetsXmp: [],
    dpiX: null, dpiY: null, proprietes: {}, chunksCorrompus: [],
  };
}

function ascii(d: Uint8Array, debut: number, fin: number): string {
  let out = '';
  for (let i = debut; i < fin && i < d.length; i++) out += String.fromCharCode(d[i]);
  return out;
}

const utf8 = (d: Uint8Array) => new TextDecoder('utf-8').decode(d);
const latin1 = (d: Uint8Array) => new TextDecoder('latin1').decode(d);

/**
 * CRC-32 (polynôme IEEE 802.3), celui du PNG.
 *
 * Réimplémenté plutôt qu'emprunté : le navigateur n'en expose aucun, et
 * dépendre d'une bibliothèque pour vérifier une intégrité serait ajouter au
 * périmètre de confiance exactement là où on cherche à le réduire.
 */
const TABLE_CRC = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();

export function crc32(donnees: Uint8Array): number {
  let c = 0xffffffff;
  for (let i = 0; i < donnees.length; i++) c = TABLE_CRC[(c ^ donnees[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

/**
 * Décompresse un bloc zlib, ou rend null si c'est impossible.
 *
 * Un bloc illisible n'interrompt pas l'inventaire : le reste du fichier reste
 * exploitable, et l'échec se voit à l'absence du texte.
 */
async function decompresser(charge: Uint8Array): Promise<Uint8Array | null> {
  try {
    const flux = new Blob([charge.slice() as unknown as BlobPart])
      .stream()
      .pipeThrough(new DecompressionStream('deflate'));
    return new Uint8Array(await new Response(flux).arrayBuffer());
  } catch {
    return null;
  }
}

// ── ICC ─────────────────────────────────────────────────────────────────────

/**
 * Lit un tag ICC textuel, dans l'une des trois formes en circulation.
 *
 * `text` est de l'ASCII terminé par NUL (v2). `desc` porte une longueur puis le
 * texte. `mluc` (v4) est de l'UTF-16BE avec une table de langues ; on prend le
 * premier enregistrement, faute d'une langue à préférer — et le dire vaut mieux
 * que de choisir en silence.
 */
function lireTagTexte(donnees: Uint8Array, offset: number, longueur: number): string | null {
  if (offset + 8 > donnees.length || longueur < 8) return null;
  const type = ascii(donnees, offset, offset + 4);
  const corps = donnees.subarray(offset, offset + longueur);
  const vue = new DataView(corps.buffer, corps.byteOffset, corps.byteLength);
  if (type === 'text') {
    return utf8(corps.subarray(8)).split('\u0000')[0].trim() || null;
  }
  if (type === 'desc') {
    if (corps.length < 12) return null;
    const n = vue.getUint32(8, false);
    return utf8(corps.subarray(12, 12 + n)).split('\u0000')[0].trim() || null;
  }
  if (type === 'mluc') {
    if (corps.length < 16) return null;
    if (vue.getUint32(8, false) === 0 || corps.length < 28) return null;
    const taille = vue.getUint32(20, false);
    const pos = vue.getUint32(24, false);
    if (pos + taille > corps.length) return null;
    return new TextDecoder('utf-16be').decode(corps.subarray(pos, pos + taille)).trim() || null;
  }
  return null;
}

/**
 * Lit l'en-tête d'un profil ICC (128 octets, ICC.1:2010 §7.2) et sa description.
 * On n'y cherche que la description et la mention de droits : le reste des tags
 * décrit des transformations que ce paquet n'applique pas.
 */
export function lireProfilIcc(donnees: Uint8Array): ProfilIcc {
  if (donnees.length < 132) {
    throw new ConteneurError('Profil ICC trop court pour porter un en-tête (128 octets).');
  }
  const vue = new DataView(donnees.buffer, donnees.byteOffset, donnees.byteLength);
  let tailleDeclaree = vue.getUint32(0, false);
  // On lit ce qui est là plutôt que de refuser : un profil tronqué garde un
  // en-tête exploitable, et le signaler vaut mieux que de tout perdre.
  if (tailleDeclaree > donnees.length) tailleDeclaree = donnees.length;

  const majeur = donnees[8];
  const mineur = donnees[9] >> 4;
  const classe = ascii(donnees, 12, 16);
  const espace = ascii(donnees, 16, 20);
  const pcs = ascii(donnees, 20, 24);
  const an = vue.getUint16(24, false);
  const mois = vue.getUint16(26, false);
  const jour = vue.getUint16(28, false);
  const h = vue.getUint16(30, false);
  const mi = vue.getUint16(32, false);
  const s = vue.getUint16(34, false);
  const deux = (x: number) => String(x).padStart(2, '0');
  const date = (mois >= 1 && mois <= 12 && jour >= 1 && jour <= 31 && an > 1980)
    ? `${String(an).padStart(4, '0')}-${deux(mois)}-${deux(jour)}T${deux(h)}:${deux(mi)}:${deux(s)}`
    : null;
  // L'octet nul est ecrit en ECHAPPEMENT, jamais en clair : un vrai NUL dans
  // un litteral rend ce fichier source binaire et la comparaison invisible a
  // la relecture. C'est la troisieme fois dans ce depot.
  const nettoyer = (x: string) => x.replace(/^[\u0000 ]+|[\u0000 ]+$/g, '');
  const plateforme = nettoyer(ascii(donnees, 40, 44)) || null;
  const createur = nettoyer(ascii(donnees, 80, 84)) || null;

  let description: string | null = null;
  let copyright: string | null = null;
  const nbTags = donnees.length >= 132 ? vue.getUint32(128, false) : 0;
  // Le parcours est borné par la LONGUEUR du profil : la sortie ci-dessous
  // arrête la boucle dès que la table de tags dépasse les données. Le
  // `Math.min(nbTags, 256)` est une ceinture par-dessus la bretelle, et non ce
  // qui protège — une rupture délibérée l'a montré : le retirer ne change
  // rien. Il est gardé parce qu'il ne coûte rien, mais le commentaire ne doit
  // pas lui prêter un rôle qu'il n'a pas.
  for (let i = 0; i < Math.min(nbTags, 256); i++) {
    const p = 132 + i * 12;
    if (p + 12 > donnees.length) break;
    const sig = ascii(donnees, p, p + 4);
    const off = vue.getUint32(p + 4, false);
    const lon = vue.getUint32(p + 8, false);
    if (off + lon > donnees.length) continue;
    if (sig === 'desc') description = lireTagTexte(donnees, off, lon);
    else if (sig === 'cprt') copyright = lireTagTexte(donnees, off, lon);
  }

  return {
    octets: tailleDeclaree,
    version: `${majeur}.${mineur}`,
    classe,
    classeLibelle: CLASSES_ICC[classe] ?? null,
    espace,
    espaceLibelle: ESPACES_ICC[espace] ?? null,
    espaceConnexion: pcs,
    plateforme, createur, date, description, copyright,
  };
}

// ── PNG ─────────────────────────────────────────────────────────────────────

const MAGIE_PNG = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

const ROLES_PNG: Record<string, string> = {
  IHDR: 'en-tête : dimensions, profondeur, type de couleur',
  PLTE: 'palette',
  IDAT: "données d'image compressées",
  IEND: 'fin du flux',
  tEXt: 'texte non compressé (Latin-1)',
  zTXt: 'texte compressé',
  iTXt: 'texte international (UTF-8), avec langue',
  iCCP: 'profil ICC intégré',
  gAMA: 'gamma',
  cHRM: 'primaires et point blanc',
  sRGB: "déclaration d'espace sRGB",
  pHYs: 'résolution physique',
  tIME: 'date de dernière modification',
  bKGD: 'couleur de fond',
  tRNS: 'transparence',
  sBIT: 'bits significatifs',
  eXIf: 'bloc EXIF (PNG 1.5 et suivantes)',
  acTL: 'animation APNG : table de contrôle',
  fcTL: 'animation APNG : contrôle de trame',
  fdAT: 'animation APNG : données de trame',
  caBX: 'manifeste C2PA (JUMBF)',
};

const TYPES_COULEUR_PNG: Record<number, string> = {
  0: 'niveaux de gris', 2: 'RVB', 3: 'palette',
  4: 'niveaux de gris + alpha', 6: 'RVB + alpha',
};

function indexDe(d: Uint8Array, octet: number, debut: number, fin: number): number {
  for (let i = debut; i < fin && i < d.length; i++) if (d[i] === octet) return i;
  return -1;
}

async function inventorierPng(donnees: Uint8Array): Promise<InventaireConteneur> {
  const inv = vide('PNG', donnees.length);
  const vue = new DataView(donnees.buffer, donnees.byteOffset, donnees.byteLength);
  let pos = 8;
  while (pos + 8 <= donnees.length) {
    const longueur = vue.getUint32(pos, false);
    const type = ascii(donnees, pos + 4, pos + 8);
    if (pos + 12 + longueur > donnees.length) break; // chunk qui déborde
    const charge = donnees.subarray(pos + 8, pos + 8 + longueur);
    const crcDeclare = vue.getUint32(pos + 8 + longueur, false);
    // Le CRC porte sur le TYPE et la charge, pas sur la longueur.
    const aVerifier = new Uint8Array(4 + longueur);
    aVerifier.set(donnees.subarray(pos + 4, pos + 8), 0);
    aVerifier.set(charge, 4);
    const valide = crcDeclare === crc32(aVerifier);
    if (!valide) inv.chunksCorrompus.push(`${type} à l'octet ${pos}`);
    inv.chunks.push({
      type, offset: pos, longueur, crcValide: valide, role: ROLES_PNG[type] ?? null,
    });

    const vc = new DataView(charge.buffer, charge.byteOffset, charge.byteLength);
    if (type === 'IHDR' && longueur >= 13) {
      inv.largeur = vc.getUint32(0, false);
      inv.hauteur = vc.getUint32(4, false);
      inv.profondeurBits = charge[8];
      inv.proprietes.type_couleur = charge[9];
      inv.proprietes.type_couleur_libelle = TYPES_COULEUR_PNG[charge[9]] ?? null;
      inv.proprietes.entrelacement = charge[12] !== 0;
    } else if (type === 'pHYs' && longueur >= 9) {
      const px = vc.getUint32(0, false);
      const py = vc.getUint32(4, false);
      if (charge[8] === 1) {
        // 1 pouce = 0,0254 m — la conversion est exacte, pas approchée.
        inv.dpiX = px * 0.0254;
        inv.dpiY = py * 0.0254;
      }
      inv.proprietes.pixels_par_unite = [px, py];
      inv.proprietes.unite_physique = charge[8] === 1 ? 'mètre' : 'inconnue';
    } else if (type === 'tIME' && longueur >= 7) {
      const deux = (x: number) => String(x).padStart(2, '0');
      inv.proprietes.derniere_modification =
        `${String(vc.getUint16(0, false)).padStart(4, '0')}-${deux(charge[2])}-${deux(charge[3])}`
        + `T${deux(charge[4])}:${deux(charge[5])}:${deux(charge[6])}`;
    } else if (type === 'eXIf') {
      inv.blocExif = charge;
    } else if (type === 'acTL' && longueur >= 8) {
      inv.proprietes.animation = true;
      inv.proprietes.trames_declarees = vc.getUint32(0, false);
      inv.proprietes.boucles = vc.getUint32(4, false);
    } else if (type === 'tEXt') {
      const i = indexDe(charge, 0, 0, charge.length);
      inv.textes.push({
        origine: 'PNG tEXt',
        cle: utf8(charge.subarray(0, i === -1 ? charge.length : i)),
        valeur: i === -1 ? '' : latin1(charge.subarray(i + 1)),
        compresse: false, langue: null,
      });
    } else if (type === 'zTXt') {
      const i = indexDe(charge, 0, 0, charge.length);
      // Le premier octet après le NUL est la méthode de compression (0 = zlib).
      const clair = i !== -1 && charge.length > i + 2
        ? await decompresser(charge.subarray(i + 2))
        : null;
      inv.textes.push({
        origine: 'PNG zTXt',
        cle: utf8(charge.subarray(0, i === -1 ? charge.length : i)),
        valeur: clair ? latin1(clair) : '',
        compresse: true, langue: null,
      });
    } else if (type === 'iTXt') {
      // cle \0 drapeau_compression methode \0 langue \0 cle_traduite \0 texte
      const i = indexDe(charge, 0, 0, charge.length);
      if (i !== -1 && charge.length >= i + 3) {
        const cle = utf8(charge.subarray(0, i));
        const comprime = charge[i + 1] === 1;
        const reste = charge.subarray(i + 3);
        const a = indexDe(reste, 0, 0, reste.length);
        const b = a === -1 ? -1 : indexDe(reste, 0, a + 1, reste.length);
        const langue = a === -1 ? '' : utf8(reste.subarray(0, a));
        let corps = b === -1 ? new Uint8Array(0) : reste.subarray(b + 1);
        if (comprime) corps = (await decompresser(corps)) ?? new Uint8Array(0);
        const valeur = utf8(corps);
        if (cle.includes('XML:com.adobe.xmp')
          || valeur.trimStart().startsWith('<?xpacket')
          || valeur.trimStart().startsWith('<x:xmpmeta')) {
          inv.paquetsXmp.push(corps);
        }
        inv.textes.push({
          origine: 'PNG iTXt', cle, valeur, compresse: comprime, langue: langue || null,
        });
      }
    } else if (type === 'iCCP') {
      const i = indexDe(charge, 0, 0, charge.length);
      const clair = i !== -1 && charge.length > i + 2
        ? await decompresser(charge.subarray(i + 2))
        : null;
      inv.proprietes.nom_profil_icc = utf8(charge.subarray(0, i === -1 ? charge.length : i));
      if (clair) {
        try { inv.profilIcc = lireProfilIcc(clair); } catch { inv.profilIcc = null; }
      }
    } else if (type === 'sRGB' && longueur >= 1) {
      inv.proprietes.intention_srgb = charge[0];
    }

    if (type === 'IEND') break;
    pos += 12 + longueur;
  }
  return inv;
}

// ── WebP (RIFF) ─────────────────────────────────────────────────────────────

const ROLES_WEBP: Record<string, string> = {
  'VP8 ': 'image avec perte',
  VP8L: 'image sans perte',
  VP8X: 'en-tête étendu : dimensions et drapeaux',
  ALPH: 'canal alpha',
  ANIM: "paramètres d'animation",
  ANMF: "trame d'animation",
  EXIF: 'bloc EXIF',
  'XMP ': 'paquet XMP',
  ICCP: 'profil ICC',
};

function inventorierWebp(donnees: Uint8Array): InventaireConteneur {
  const inv = vide('WebP', donnees.length);
  const vue = new DataView(donnees.buffer, donnees.byteOffset, donnees.byteLength);
  let pos = 12; // « RIFF » + taille + « WEBP »
  while (pos + 8 <= donnees.length) {
    const type = ascii(donnees, pos, pos + 4);
    const longueur = vue.getUint32(pos + 4, true);
    if (pos + 8 + longueur > donnees.length) break;
    const charge = donnees.subarray(pos + 8, pos + 8 + longueur);
    inv.chunks.push({
      type, offset: pos, longueur, crcValide: null, role: ROLES_WEBP[type] ?? null,
    });
    const vc = new DataView(charge.buffer, charge.byteOffset, charge.byteLength);

    if (type === 'VP8X' && longueur >= 10) {
      const drapeaux = charge[0];
      // Les dimensions sont écrites diminuées de 1, sur 24 bits.
      inv.largeur = (charge[4] | (charge[5] << 8) | (charge[6] << 16)) + 1;
      inv.hauteur = (charge[7] | (charge[8] << 8) | (charge[9] << 16)) + 1;
      inv.proprietes.icc = Boolean(drapeaux & 0x20);
      inv.proprietes.alpha = Boolean(drapeaux & 0x10);
      inv.proprietes.exif = Boolean(drapeaux & 0x08);
      inv.proprietes.xmp = Boolean(drapeaux & 0x04);
      inv.proprietes.animation = Boolean(drapeaux & 0x02);
    } else if (type === 'VP8 ' && longueur >= 10 && inv.largeur === null) {
      if (charge[3] === 0x9d && charge[4] === 0x01 && charge[5] === 0x2a) {
        inv.largeur = vc.getUint16(6, true) & 0x3fff;
        inv.hauteur = vc.getUint16(8, true) & 0x3fff;
      }
    } else if (type === 'VP8L' && longueur >= 5 && inv.largeur === null) {
      if (charge[0] === 0x2f) {
        const bits = charge[1] | (charge[2] << 8) | (charge[3] << 16) | (charge[4] << 24);
        inv.largeur = (bits & 0x3fff) + 1;
        inv.hauteur = ((bits >>> 14) & 0x3fff) + 1;
      }
    } else if (type === 'ANIM' && longueur >= 6) {
      inv.proprietes.boucles = vc.getUint16(4, true);
    } else if (type === 'ANMF') {
      inv.proprietes.trames = (Number(inv.proprietes.trames) || 0) + 1;
    } else if (type === 'EXIF') {
      // Certains encodeurs préfixent « Exif » et deux nuls, d'autres non.
      const prefixe = ascii(charge, 0, 4) === 'Exif' && charge[4] === 0 && charge[5] === 0;
      inv.blocExif = prefixe ? charge.subarray(6) : charge;
    } else if (type === 'XMP ') {
      inv.paquetsXmp.push(charge);
    } else if (type === 'ICCP') {
      try { inv.profilIcc = lireProfilIcc(charge); } catch { inv.profilIcc = null; }
    }

    // Les morceaux RIFF sont alignés sur deux octets. L'ignorer décalerait
    // tous les morceaux suivants, et le parcours s'arrêterait sur un type
    // illisible sans dire pourquoi.
    pos += 8 + longueur + (longueur & 1);
  }
  return inv;
}

// ── GIF ─────────────────────────────────────────────────────────────────────

function inventorierGif(donnees: Uint8Array): InventaireConteneur {
  const inv = vide('GIF', donnees.length);
  const vue = new DataView(donnees.buffer, donnees.byteOffset, donnees.byteLength);
  inv.proprietes.version = ascii(donnees, 3, 6);
  let tailleTable = 0;
  if (donnees.length >= 11) {
    inv.largeur = vue.getUint16(6, true);
    inv.hauteur = vue.getUint16(8, true);
    const champ = donnees[10];
    inv.profondeurBits = ((champ >> 4) & 0x07) + 1;
    const tableGlobale = Boolean(champ & 0x80);
    inv.proprietes.table_couleurs_globale = tableGlobale;
    tailleTable = tableGlobale ? 3 * 2 ** ((champ & 0x07) + 1) : 0;
  }

  let pos = 13 + tailleTable;
  let trames = 0;
  const extensions: string[] = [];

  /** Les données GIF sont en sous-blocs longueur+octets, terminés par 0. */
  const sauterSousBlocs = (p: number): [number, Uint8Array] => {
    const morceaux: Uint8Array[] = [];
    while (p < donnees.length) {
      const n = donnees[p];
      if (n === 0) {
        const total = morceaux.reduce((s, m) => s + m.length, 0);
        const out = new Uint8Array(total);
        let o = 0;
        for (const m of morceaux) { out.set(m, o); o += m.length; }
        return [p + 1, out];
      }
      morceaux.push(donnees.subarray(p + 1, p + 1 + n));
      p += 1 + n;
    }
    const total = morceaux.reduce((s, m) => s + m.length, 0);
    const out = new Uint8Array(total);
    let o = 0;
    for (const m of morceaux) { out.set(m, o); o += m.length; }
    return [p, out];
  };

  while (pos < donnees.length) {
    const bloc = donnees[pos];
    if (bloc === 0x3b) {
      inv.chunks.push({ type: 'Trailer', offset: pos, longueur: 1, crcValide: null, role: 'fin du flux' });
      break;
    }
    if (bloc === 0x21 && pos + 1 < donnees.length) {
      const etiquette = donnees[pos + 1];
      const debut = pos;
      if (etiquette === 0xfe) {
        const [p, texte] = sauterSousBlocs(pos + 2);
        pos = p;
        inv.textes.push({
          origine: 'GIF Comment Extension', cle: 'commentaire',
          valeur: latin1(texte), compresse: false, langue: null,
        });
        inv.chunks.push({ type: 'Comment', offset: debut, longueur: pos - debut, crcValide: null, role: 'commentaire' });
      } else if (etiquette === 0xff && pos + 14 <= donnees.length) {
        const identifiant = ascii(donnees, pos + 3, pos + 11);
        const code = ascii(donnees, pos + 11, pos + 14);
        const [p, charge] = sauterSousBlocs(pos + 14);
        pos = p;
        inv.chunks.push({
          type: `Application/${identifiant}`, offset: debut, longueur: pos - debut,
          crcValide: null, role: "extension d'application",
        });
        if (identifiant === 'NETSCAPE' && charge.length >= 3) {
          inv.proprietes.boucles = charge[1] | (charge[2] << 8);
        }
        extensions.push(identifiant + code);
        if (identifiant === 'XMP Data') inv.paquetsXmp.push(charge);
      } else if (etiquette === 0xf9) {
        const [p] = sauterSousBlocs(pos + 2);
        pos = p;
        inv.chunks.push({ type: 'GraphicControl', offset: debut, longueur: pos - debut, crcValide: null, role: 'contrôle de trame' });
      } else {
        const [p] = sauterSousBlocs(pos + 2);
        pos = p;
        inv.chunks.push({
          type: `Extension 0x${etiquette.toString(16).padStart(2, '0').toUpperCase()}`,
          offset: debut, longueur: pos - debut, crcValide: null, role: null,
        });
      }
      continue;
    }
    if (bloc === 0x2c && pos + 10 <= donnees.length) {
      trames += 1;
      const champ = donnees[pos + 9];
      const saut = 10 + (champ & 0x80 ? 3 * 2 ** ((champ & 0x07) + 1) : 0);
      const [p] = sauterSousBlocs(pos + saut + 1);
      inv.chunks.push({
        type: 'Image', offset: pos, longueur: p - pos, crcValide: null,
        role: "descripteur et données d'image",
      });
      pos = p;
      continue;
    }
    break;
  }

  if (extensions.length > 0) inv.proprietes.extensions_application = extensions;
  inv.proprietes.trames = trames;
  inv.proprietes.animation = trames > 1;
  return inv;
}

// ── BMP ─────────────────────────────────────────────────────────────────────

const COMPRESSIONS_BMP: Record<number, string> = {
  0: 'aucune (BI_RGB)', 1: 'RLE 8 bits', 2: 'RLE 4 bits',
  3: 'champs de bits (BI_BITFIELDS)', 4: 'JPEG', 5: 'PNG',
};

function inventorierBmp(donnees: Uint8Array): InventaireConteneur {
  const inv = vide('BMP', donnees.length);
  if (donnees.length < 26) return inv;
  const vue = new DataView(donnees.buffer, donnees.byteOffset, donnees.byteLength);
  const tailleEntete = vue.getUint32(14, true);
  inv.chunks.push({ type: 'BITMAPFILEHEADER', offset: 0, longueur: 14, crcValide: null, role: 'en-tête de fichier' });
  inv.chunks.push({ type: `DIB (${tailleEntete} octets)`, offset: 14, longueur: tailleEntete, crcValide: null, role: "en-tête d'image" });
  if (tailleEntete >= 40 && donnees.length >= 54) {
    const l = vue.getInt32(18, true);
    const h = vue.getInt32(22, true);
    inv.largeur = Math.abs(l);
    // Une hauteur négative signifie que les lignes sont stockées de haut en
    // bas. C'est une propriété d'écriture, pas une dimension : on la note.
    inv.hauteur = Math.abs(h);
    inv.proprietes.lignes_de_haut_en_bas = h < 0;
    inv.profondeurBits = vue.getUint16(28, true);
    const compression = vue.getUint32(30, true);
    inv.proprietes.compression = compression;
    inv.proprietes.compression_libelle = COMPRESSIONS_BMP[compression] ?? null;
    const ppmX = vue.getInt32(38, true);
    const ppmY = vue.getInt32(42, true);
    if (ppmX > 0) inv.dpiX = ppmX * 0.0254;
    if (ppmY > 0) inv.dpiY = ppmY * 0.0254;
  }
  return inv;
}

// ── SVG ─────────────────────────────────────────────────────────────────────

const ATTRS_SVG = ['width', 'height', 'viewBox', 'xmlns:inkscape', 'xmlns:sodipodi'];

/**
 * Un SVG est du XML : tout y est lisible en clair, et c'est le propos. On
 * relève ce qui identifie le producteur — les logiciels d'édition vectorielle
 * laissent des espaces de noms qui leur sont propres — et les commentaires, qui
 * portent souvent le nom de l'outil et sa version.
 */
function inventorierSvg(donnees: Uint8Array): InventaireConteneur {
  const inv = vide('SVG', donnees.length);
  const texte = utf8(donnees);

  // Pas de drapeau `s` : le projet vise ES2017, et il est inutile ici —
  // `[^>]` accepte déjà les retours à la ligne.
  const m = /<svg\b[^>]*>/i.exec(texte);
  const entete = m ? m[0] : '';
  for (const attr of ATTRS_SVG) {
    const a = new RegExp(`${attr.replace(':', ':')}\\s*=\\s*"([^"]*)"`).exec(entete);
    if (a) inv.proprietes[attr] = a[1];
  }
  // Les dimensions ne sont extraites que si elles sont en pixels nus : une
  // largeur en millimètres ou en pourcentage n'est pas un nombre de pixels, et
  // la convertir demanderait de connaître le contexte de rendu.
  for (const [cle, attr] of [['largeur', 'width'], ['hauteur', 'height']] as const) {
    const val = inv.proprietes[attr];
    if (typeof val === 'string') {
      const n = /^\s*([0-9]+(?:\.[0-9]+)?)\s*(?:px)?\s*$/.exec(val);
      if (n) {
        if (cle === 'largeur') inv.largeur = Math.trunc(Number(n[1]));
        else inv.hauteur = Math.trunc(Number(n[1]));
      }
    }
  }

  let i = 0;
  for (const c of texte.matchAll(/<!--([\s\S]{0,2000}?)-->/g)) {
    const v = c[1].trim();
    i += 1;
    if (v) {
      inv.textes.push({
        origine: 'SVG commentaire', cle: `commentaire ${i}`, valeur: v,
        compresse: false, langue: null,
      });
    }
  }
  for (const balise of ['title', 'desc']) {
    for (const t of texte.matchAll(new RegExp(`<${balise}\\b[^>]*>([\\s\\S]{0,2000}?)</${balise}>`, 'gi'))) {
      if (t[1].trim()) {
        inv.textes.push({
          origine: `SVG <${balise}>`, cle: balise, valeur: t[1].trim(),
          compresse: false, langue: null,
        });
      }
    }
  }

  const meta = /<metadata\b[^>]*>([\s\S]*?)<\/metadata>/i.exec(texte);
  if (meta) {
    inv.chunks.push({
      type: 'metadata', offset: meta.index, longueur: meta[0].length,
      crcValide: null, role: 'bloc de métadonnées RDF',
    });
    // Le XMP d'un SVG vit dans <metadata>, sans marqueur de paquet.
    if (meta[1].includes('adobe:ns:meta') || meta[1].includes('rdf:RDF')) {
      inv.paquetsXmp.push(new TextEncoder().encode(meta[1]));
    }
  }
  return inv;
}

// ── Point d'entrée ──────────────────────────────────────────────────────────

const commencePar = (d: Uint8Array, octets: readonly number[], offset = 0) =>
  octets.every((o, i) => d[offset + i] === o);

/**
 * Inventorie ce que le conteneur déclare, quel que soit son format.
 *
 * Lève `ConteneurError` pour un format que ce module ne couvre pas — le nommer
 * vaut mieux que rendre un inventaire vide, qui laisserait croire que le
 * fichier ne déclare rien.
 */
export async function inventorier(donnees: Uint8Array): Promise<InventaireConteneur> {
  if (donnees.length < 12) {
    throw new ConteneurError("Fichier trop court pour porter un en-tête de conteneur.");
  }
  if (commencePar(donnees, MAGIE_PNG)) return inventorierPng(donnees);
  if (ascii(donnees, 0, 4) === 'RIFF' && ascii(donnees, 8, 12) === 'WEBP') {
    return inventorierWebp(donnees);
  }
  const tete6 = ascii(donnees, 0, 6);
  if (tete6 === 'GIF87a' || tete6 === 'GIF89a') return inventorierGif(donnees);
  if (donnees[0] === 0x42 && donnees[1] === 0x4d) return inventorierBmp(donnees);
  const debut = utf8(donnees.subarray(0, 512)).replace(/^\s+/, '');
  if (debut.startsWith('<?xml') || debut.startsWith('<svg')) {
    if (utf8(donnees.subarray(0, 4096)).includes('<svg')) return inventorierSvg(donnees);
  }
  throw new ConteneurError(
    'Format non couvert par ce module : ni PNG, ni WebP, ni GIF, ni BMP, ni SVG. '
    + 'Les JPEG et TIFF se lisent par noyau.ts, les conteneurs à boîtes par isobmff.ts.',
  );
}
