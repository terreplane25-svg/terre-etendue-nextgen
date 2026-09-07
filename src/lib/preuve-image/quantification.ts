/**
 * quantification.ts — Port TypeScript de `preuve_image.quantification` (outil B).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-B-preuve-image/preuve_image/quantification.py`.
 * Ce port est épinglé au Python par `vecteurs-or-extraction.json`, que
 * `scripts/verifier-port-extraction.mjs` rejoue ici.
 *
 * CE QUE CE MODULE ÉTABLIT, ET CE QU'IL N'ÉTABLIT PAS
 * ───────────────────────────────────────────────────
 * Une image JPEG porte, dans ses segments DQT, les tables qui ont servi à la
 * quantifier. Ce sont des données exactes, présentes dans tout JPEG, et elles
 * SURVIVENT à la purge de l'EXIF : un fichier dont toutes les métadonnées ont
 * été retirées porte encore ses tables.
 *
 * Établi : les tables, leur empreinte, le facteur de qualité IJG quand elles en
 * dérivent — avec l'écart résiduel —, le sous-échantillonnage et le mode.
 *
 * NON établi : la marque de l'appareil ou du logiciel. Associer une signature à
 * « Canon DIGIC » ou « algorithme WhatsApp » demande un corpus de fichiers
 * réels dont la provenance est établie. Ce paquet n'en a pas, et le registre
 * `SIGNATURES_CONNUES` est vide plutôt qu'inventé.
 */

export class QuantificationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'QuantificationError';
  }
}

/**
 * Table de luminance de l'annexe K d'ISO/IEC 10918-1, en ordre zigzag. C'est
 * la table dont dérivent, par mise à l'échelle, celles de la quasi-totalité
 * des encodeurs.
 */
export const TABLE_LUMINANCE_ANNEXE_K: readonly number[] = [
  16, 11, 12, 14, 12, 10, 16, 14, 13, 14, 18, 17, 16, 19, 24, 40,
  26, 24, 22, 22, 24, 49, 35, 37, 29, 40, 58, 51, 61, 60, 57, 51,
  56, 55, 64, 72, 92, 78, 64, 68, 87, 69, 55, 56, 80, 109, 81, 87,
  95, 98, 103, 104, 103, 62, 77, 113, 121, 112, 100, 120, 92, 101, 103, 99,
];

export const TABLE_CHROMINANCE_ANNEXE_K: readonly number[] = [
  17, 18, 18, 24, 21, 24, 47, 26, 26, 47, 99, 66, 56, 66, 99, 99,
  99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99,
  99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99,
  99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99,
];

/**
 * Le registre des signatures reconnues. VIDE, et c'est délibéré.
 *
 * Le remplir demande un corpus de fichiers réels, collectés appareil par
 * appareil et version par version. Y écrire des correspondances de mémoire
 * produirait des identifications fausses présentées comme des faits — et une
 * identification fausse dans un dossier probatoire coûte plus cher que pas
 * d'identification du tout.
 */
export const SIGNATURES_CONNUES: Record<string, [string, string]> = {};

export const MOTIF_AUCUNE_SIGNATURE =
  'Aucun rapprochement : le registre des signatures est vide. Le remplir '
  + "demande un corpus de fichiers réels dont la provenance est établie, "
  + 'appareil par appareil et version par version. L’empreinte ci-dessus reste '
  + 'utilisable pour COMPARER deux fichiers que vous avez tous les deux — '
  + 'des tables identiques sortent de la même chaîne d’encodage aux mêmes '
  + 'réglages — mais elle n’identifie rien contre une base qu’on n’a pas.';

export interface TableQuantification {
  identifiant: number;
  precisionBits: number;
  /** En ordre ZIGZAG, celui du fichier : les réordonner ferait diverger l'empreinte. */
  valeurs: number[];
  offset: number;
}

export interface AnalyseQuantification {
  tables: TableQuantification[];
  /** L'empreinte de l'ENSEMBLE des tables, dans l'ordre du fichier. */
  empreinteEnsemble: string;
  qualiteIjg: number | null;
  /** Nombre de coefficients qui diffèrent de la table IJG reconstruite. */
  ecartAIjg: number | null;
  conformeIjg: boolean;
  sousEchantillonnage: string | null;
  progressif: boolean | null;
  largeur: number | null;
  hauteur: number | null;
  composantes: number;
  signature: [string, string] | null;
  motifAbsenceSignature: string;
  marqueurs: string[];
}

/**
 * La table que produit la bibliothèque de référence IJG pour ce facteur.
 *
 * L'algorithme est celui de `jpeg_set_quality`, reproduit ici plutôt
 * qu'emprunté, pour que la comparaison ne dépende d'aucune bibliothèque.
 */
export function tableIjg(
  qualite: number, base: readonly number[] = TABLE_LUMINANCE_ANNEXE_K,
): number[] {
  if (!(qualite >= 1 && qualite <= 100)) {
    throw new QuantificationError('Le facteur de qualité IJG est compris entre 1 et 100.');
  }
  // Division ENTIÈRE des deux côtés : `Math.floor` là où Python écrit `//`.
  const echelle = qualite < 50 ? Math.floor(5000 / qualite) : 200 - qualite * 2;
  return base.map((v) => Math.min(255, Math.max(1, Math.floor((v * echelle + 50) / 100))));
}

/**
 * Le facteur IJG dont la table est la plus proche, et l'écart qui reste.
 *
 * L'écart est le nombre de coefficients qui DIFFÈRENT, pas une distance : zéro
 * veut dire que la table est exactement celle de ce facteur, et tout le reste
 * veut dire qu'elle n'en vient pas. Rendre un facteur « approché » sans cet
 * écart laisserait croire à une identification là où il n'y a qu'une
 * ressemblance.
 */
export function qualiteIjgEstimee(
  valeurs: readonly number[], base: readonly number[] = TABLE_LUMINANCE_ANNEXE_K,
): [number | null, number | null] {
  if (valeurs.length !== 64) return [null, null];
  let meilleur: number | null = null;
  let ecartMin: number | null = null;
  for (let q = 1; q <= 100; q++) {
    const candidate = tableIjg(q, base);
    let ecart = 0;
    for (let i = 0; i < 64; i++) if (valeurs[i] !== candidate[i]) ecart += 1;
    if (ecartMin === null || ecart < ecartMin) {
      meilleur = q;
      ecartMin = ecart;
      if (ecart === 0) break;
    }
  }
  return [meilleur, ecartMin];
}

/** Les marqueurs JPEG qu'on nomme. Un JPEG progressif sort rarement d'un appareil. */
const MARQUEURS: Record<number, string> = {
  0xc0: 'SOF0 (séquentiel, Huffman)',
  0xc1: 'SOF1 (séquentiel étendu)',
  0xc2: 'SOF2 (progressif)',
  0xc3: 'SOF3 (sans perte)',
  0xc4: 'DHT (tables de Huffman)',
  0xc9: 'SOF9 (arithmétique)',
  0xcc: 'DAC (codage arithmétique)',
  0xdb: 'DQT (tables de quantification)',
  0xdd: 'DRI (intervalle de redémarrage)',
  0xda: 'SOS (début du balayage)',
  0xe0: 'APP0 (JFIF)',
  0xe1: 'APP1 (EXIF ou XMP)',
  0xe2: 'APP2 (ICC ou MPF)',
  0xec: 'APP12 (Ducky, Picture Info)',
  0xed: 'APP13 (Photoshop IRB)',
  0xee: 'APP14 (Adobe)',
  0xfe: 'COM (commentaire)',
};

const NOTATIONS: Record<string, string> = {
  '1,1': '4:4:4', '2,1': '4:2:2', '2,2': '4:2:0',
  '1,2': '4:4:0', '4,1': '4:1:1', '4,2': '4:1:0',
};

/**
 * Déduit la notation « 4:x:x » des facteurs d'échantillonnage du SOF.
 * Elle n'a de sens qu'à trois composantes ; au-delà ou en deçà, on rend null
 * plutôt qu'une notation qui n'existe pas.
 */
function sousEchantillonnage(composantes: [number, number, number][]): string | null {
  if (composantes.length !== 3) return null;
  const [, hy, vy] = composantes[0];
  const [, hc, vc] = composantes[1];
  if (hc === 0 || vc === 0) return null;
  return NOTATIONS[`${Math.floor(hy / hc)},${Math.floor(vy / vc)}`] ?? null;
}

async function sha256Texte(texte: string): Promise<string> {
  const octets = new TextEncoder().encode(texte);
  const c = await crypto.subtle.digest('SHA-256', octets.slice().buffer);
  return Array.from(new Uint8Array(c)).map((b) => b.toString(16).padStart(2, '0')).join('');
}

/** L'empreinte d'une table seule, sur ses valeurs en ordre zigzag. */
export function empreinteTable(t: TableQuantification): Promise<string> {
  return sha256Texte(t.valeurs.join(','));
}

/**
 * Lit les tables DQT d'un JPEG et ce que le SOF déclare.
 *
 * Le balayage s'arrête au SOS : au-delà commencent les données comprimées, où
 * toute séquence d'octets peut ressembler à un marqueur.
 */
export async function analyserQuantification(donnees: Uint8Array): Promise<AnalyseQuantification> {
  if (donnees.length < 4 || donnees[0] !== 0xff || donnees[1] !== 0xd8) {
    throw new QuantificationError('Fichier non reconnu comme JPEG (SOI absent).');
  }
  const vue = new DataView(donnees.buffer, donnees.byteOffset, donnees.byteLength);
  const tables: TableQuantification[] = [];
  const marqueurs: string[] = [];
  const composantes: [number, number, number][] = [];
  let largeur: number | null = null;
  let hauteur: number | null = null;
  let progressif: boolean | null = null;

  let pos = 2;
  while (pos + 4 <= donnees.length) {
    if (donnees[pos] !== 0xff) break;
    const m = donnees[pos + 1];
    if (m === 0xd8 || (m >= 0xd0 && m <= 0xd7)) { pos += 2; continue; }
    if (m === 0xd9) break;
    const longueur = vue.getUint16(pos + 2, false);
    if (longueur < 2 || pos + 2 + longueur > donnees.length) break;
    const debutCorps = pos + 4;
    const finCorps = pos + 2 + longueur;
    const nom = MARQUEURS[m] ?? `0x${m.toString(16).padStart(2, '0').toUpperCase()}`;
    if (!marqueurs.includes(nom)) marqueurs.push(nom);

    if (m === 0xdb) {
      // Un même segment DQT peut porter plusieurs tables à la suite.
      let p = debutCorps;
      while (p < finCorps) {
        const entete = donnees[p];
        const precision = (entete >> 4) ? 16 : 8;
        const identifiant = entete & 0x0f;
        const n = 64 * (precision === 16 ? 2 : 1);
        if (p + 1 + n > finCorps) break;
        const valeurs: number[] = [];
        for (let i = 0; i < 64; i++) {
          valeurs.push(precision === 16
            ? vue.getUint16(p + 1 + i * 2, false)
            : donnees[p + 1 + i]);
        }
        tables.push({ identifiant, precisionBits: precision, valeurs, offset: p });
        p += 1 + n;
      }
    } else if ([0xc0, 0xc1, 0xc2, 0xc3, 0xc9].includes(m) && longueur >= 8) {
      progressif = m === 0xc2;
      hauteur = vue.getUint16(debutCorps + 1, false);
      largeur = vue.getUint16(debutCorps + 3, false);
      const nb = donnees[debutCorps + 5];
      for (let i = 0; i < nb; i++) {
        const q = debutCorps + 6 + i * 3;
        if (q + 3 > finCorps) break;
        composantes.push([donnees[q], donnees[q + 1] >> 4, donnees[q + 1] & 0x0f]);
      }
    } else if (m === 0xda) {
      break;
    }
    pos += 2 + longueur;
  }

  if (tables.length === 0) {
    throw new QuantificationError(
      'Aucune table de quantification (DQT) trouvée avant le début du balayage. '
      + "Un JPEG en porte toujours : le fichier est tronqué, ou ce n'en est pas un.",
    );
  }

  // L'empreinte porte sur TOUTES les tables, dans l'ordre du fichier : deux
  // images de même luminance mais de chrominance différente ne viennent pas de
  // la même chaîne, et les confondre serait un faux rapprochement.
  const ensemble = tables
    .map((t) => `${t.identifiant}:${t.precisionBits}:${t.valeurs.join(',')}`)
    .join(';');
  const empreinteEnsemble = await sha256Texte(ensemble);

  const luminance = tables.find((t) => t.identifiant === 0) ?? tables[0];
  const [qualite, ecart] = qualiteIjgEstimee(luminance.valeurs);

  return {
    tables,
    empreinteEnsemble,
    qualiteIjg: qualite,
    ecartAIjg: ecart,
    conformeIjg: ecart === 0,
    sousEchantillonnage: sousEchantillonnage(composantes),
    progressif,
    largeur,
    hauteur,
    composantes: composantes.length,
    signature: SIGNATURES_CONNUES[empreinteEnsemble] ?? null,
    motifAbsenceSignature: MOTIF_AUCUNE_SIGNATURE,
    marqueurs,
  };
}
