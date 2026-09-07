/**
 * makernotes.ts — Port TypeScript de `preuve_image.makernotes` (outil B).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-B-preuve-image/preuve_image/makernotes.py`.
 * Ce port est épinglé au Python par `vecteurs-or-makernotes.json`, que
 * `scripts/verifier-port-makernotes.mjs` rejoue ici.
 *
 * CE QUE CE MODULE ÉTABLIT, ET CE QU'IL N'ÉTABLIT PAS
 * ───────────────────────────────────────────────────
 * Le tag EXIF 0x927C, dit MakerNote, est le seul champ de la norme dont le
 * contenu n'est pas normalisé : chaque constructeur y écrit ce qu'il veut,
 * dans la forme qu'il veut, et le change d'un millésime à l'autre.
 *
 * Établi : le constructeur reconnu à sa SIGNATURE, qui est dans les octets ;
 * la base des offsets, ESSAYÉE puis vérifiée contre les données ; l'inventaire
 * des tags — identifiant, type, cardinalité, taille, empreinte — et la FORME de
 * certaines valeurs (texte, liste de propriétés binaire, IFD imbriqué).
 *
 * NON établi : ce que les tags SIGNIFIENT. « 0x0095 = type d'objectif » écrit
 * de mémoire est une attribution, pas une lecture, et le sens d'un même
 * identifiant change d'un millésime à l'autre chez un même constructeur. Le
 * registre `SENS_CONNUS` est vide et extensible, comme celui des signatures de
 * quantification.
 *
 * Ce qui reste est utilisable : deux notes de même empreinte sortent du même
 * appareil aux mêmes réglages, ce qui permet de CONFRONTER deux fichiers qu'on
 * a tous les deux.
 *
 * LA BASE DES OFFSETS : LE PIÈGE, ET COMMENT IL EST DÉSAMORCÉ
 * ──────────────────────────────────────────────────────────
 * L'origine des offsets d'un IFD change selon le constructeur : l'en-tête TIFF
 * du fichier pour les uns, le début de la note pour les autres, un en-tête TIFF
 * interne pour Nikon. Se tromper d'origine ne lève AUCUNE erreur : on lit
 * simplement des octets quelconques, qui ressemblent à des données. Les bases
 * candidates sont donc essayées, celle qui donne un IFD cohérent est retenue,
 * et l'écart avec la base annoncée est signalé plutôt que tu.
 */

import { empreinteSha256 } from './noyau';

export class MakerNoteError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'MakerNoteError';
  }
}

/** Octets d'une signature, écrits lisiblement. Les non-imprimables sont échappés. */
function octetsDe(texte: string): Uint8Array {
  const out = new Uint8Array(texte.length);
  for (let i = 0; i < texte.length; i += 1) out[i] = texte.charCodeAt(i) & 0xff;
  return out;
}

/**
 * Ce qu'on sait d'une famille de notes propriétaires.
 *
 * `baseAttendue` est ce que la documentation publiée annonce. Elle n'est PAS
 * appliquée telle quelle : elle sert de candidat, et le résultat dit si c'est
 * bien elle qui a produit un IFD cohérent.
 */
export interface SignatureConstructeur {
  nom: string;
  /** Les octets par lesquels la note commence. */
  magie: Uint8Array;
  /** Où commence l'IFD, compté depuis le début de la note. */
  decalageIfd: number;
  /** « note », « tiff » ou « tiff_interne ». */
  baseAttendue: string;
  /** Boutisme imposé par le constructeur, ou null s'il suit celui du fichier. */
  boutisme: '<' | '>' | null;
  /** Ce qui est publié sur cette famille, en une ligne. */
  remarque: string;
}

/**
 * Les signatures publiées. Elles sont reconnues AUX OCTETS ; ce qui suit la
 * reconnaissance est vérifié contre les données, jamais présumé.
 *
 * L'ordre compte : les signatures les plus longues d'abord, car certaines sont
 * préfixes d'autres (« OLYMP\u0000 » et « OLYMPUS\u0000 »).
 */
export const SIGNATURES: readonly SignatureConstructeur[] = [
  {
    nom: 'Apple', magie: octetsDe('Apple iOS\u0000\u0000\u0001MM'), decalageIfd: 14,
    baseAttendue: 'note', boutisme: '>',
    remarque: 'En-tête de 14 octets, boutisme gros-boutien imposé par les deux '
      + 'derniers octets « MM ».',
  },
  {
    nom: 'Apple (variante)', magie: octetsDe('Apple iOS\u0000'), decalageIfd: 14,
    baseAttendue: 'note', boutisme: '>',
    remarque: "Même famille, octet de version différent selon la version d'iOS.",
  },
  {
    nom: 'Nikon (type 3)', magie: octetsDe('Nikon\u0000\u0002'), decalageIfd: 10,
    baseAttendue: 'tiff_interne', boutisme: null,
    remarque: "Dix octets d'en-tête, puis un en-tête TIFF COMPLET dont les offsets "
      + "partent — c'est la seule famille à en porter un.",
  },
  {
    nom: 'Nikon (type 1)', magie: octetsDe('Nikon\u0000\u0001'), decalageIfd: 8,
    baseAttendue: 'note', boutisme: null,
    remarque: 'Ancien format, sans en-tête TIFF interne.',
  },
  {
    nom: 'Olympus (type 2)', magie: octetsDe('OLYMPUS\u0000'), decalageIfd: 12,
    baseAttendue: 'note', boutisme: null,
    remarque: 'Huit octets de signature, puis le boutisme et une version.',
  },
  {
    nom: 'Olympus (type 1)', magie: octetsDe('OLYMP\u0000'), decalageIfd: 8,
    baseAttendue: 'tiff', boutisme: null, remarque: 'Ancien format Olympus.',
  },
  {
    nom: 'Fujifilm', magie: octetsDe('FUJIFILM'), decalageIfd: 12,
    baseAttendue: 'note', boutisme: '<',
    remarque: 'Huit octets de signature, puis un entier petit-boutien qui donne '
      + "l'offset de l'IFD depuis le début de la note.",
  },
  {
    nom: 'Panasonic', magie: octetsDe('Panasonic\u0000\u0000\u0000'), decalageIfd: 12,
    baseAttendue: 'tiff', boutisme: null, remarque: '',
  },
  {
    nom: 'Leica', magie: octetsDe('LEICA\u0000'), decalageIfd: 8,
    baseAttendue: 'tiff', boutisme: null, remarque: '',
  },
  {
    nom: 'Pentax', magie: octetsDe('AOC\u0000'), decalageIfd: 6,
    baseAttendue: 'note', boutisme: null, remarque: '',
  },
  {
    nom: 'Pentax (PENTAX)', magie: octetsDe('PENTAX \u0000'), decalageIfd: 10,
    baseAttendue: 'note', boutisme: null, remarque: '',
  },
  {
    nom: 'Sony (DSC)', magie: octetsDe('SONY DSC \u0000\u0000\u0000'), decalageIfd: 12,
    baseAttendue: 'tiff', boutisme: null, remarque: '',
  },
  {
    nom: 'Sony (CAM)', magie: octetsDe('SONY CAM \u0000\u0000\u0000'), decalageIfd: 12,
    baseAttendue: 'tiff', boutisme: null, remarque: '',
  },
  {
    nom: 'Sony (PIC)', magie: octetsDe('SONY PIC\u0000'), decalageIfd: 12,
    baseAttendue: 'tiff', boutisme: null, remarque: '',
  },
  {
    nom: 'Sigma / Foveon', magie: octetsDe('SIGMA\u0000\u0000\u0000'), decalageIfd: 10,
    baseAttendue: 'tiff', boutisme: null, remarque: '',
  },
  {
    nom: 'Foveon', magie: octetsDe('FOVEON\u0000\u0000'), decalageIfd: 10,
    baseAttendue: 'tiff', boutisme: null, remarque: '',
  },
  {
    nom: 'Ricoh', magie: octetsDe('RICOH\u0000'), decalageIfd: 8,
    baseAttendue: 'tiff', boutisme: null, remarque: '',
  },
  {
    nom: 'Casio (type 2)', magie: octetsDe('QVC\u0000\u0000\u0000'), decalageIfd: 6,
    baseAttendue: 'tiff', boutisme: null, remarque: '',
  },
  {
    nom: 'Samsung', magie: octetsDe('SAMSUNG\u0000'), decalageIfd: 8,
    baseAttendue: 'tiff', boutisme: null, remarque: '',
  },
];

/**
 * Le registre du SENS des tags. VIDE, et c'est délibéré.
 *
 * Chaque entrée serait : « constructeur|identifiant » → [nom, ce qui l'établit].
 * Le remplir demande la documentation d'un constructeur, ou un corpus de
 * fichiers réels dont on connaît les réglages. Y écrire « 0x0095 = type
 * d'objectif » de mémoire produirait des attributions fausses présentées comme
 * des lectures — et le sens d'un tag change d'un millésime à l'autre chez le
 * même constructeur.
 */
export const SENS_CONNUS: Record<string, [string, string]> = {};

export const MOTIF_AUCUN_SENS =
  'Les tags sont inventoriés par leur STRUCTURE — identifiant, type, '
  + 'cardinalité, taille, empreinte — jamais par leur sens. Le registre des '
  + "significations est vide : le remplir demande la documentation d'un "
  + "constructeur ou un corpus de fichiers dont on connaît les réglages, et le "
  + "sens d'un même identifiant change d'un millésime à l'autre chez un même "
  + "constructeur. L'inventaire reste utilisable pour CONFRONTER deux fichiers "
  + "qu'on a tous les deux : deux notes de même empreinte sortent du même "
  + 'appareil aux mêmes réglages.';

/**
 * Taille d'un élément par type TIFF. Un type hors table rend la taille 0, ce
 * qui écarte l'entrée : mieux vaut ignorer un type inconnu que multiplier une
 * cardinalité par une taille devinée.
 */
const TAILLE_TYPE: Record<number, number> = {
  1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8,
};

const NOMS_TYPE: Record<number, string> = {
  1: 'BYTE', 2: 'ASCII', 3: 'SHORT', 4: 'LONG', 5: 'RATIONAL',
  6: 'SBYTE', 7: 'UNDEFINED', 8: 'SSHORT', 9: 'SLONG', 10: 'SRATIONAL',
  11: 'FLOAT', 12: 'DOUBLE',
};

/** Un tag de note propriétaire, décrit par sa forme seule. */
export interface TagProprietaire {
  identifiant: number;
  type: number;
  typeNom: string;
  cardinalite: number;
  octets: number;
  /** Vrai si la valeur tient dans les quatre octets de l'entrée. */
  enLigne: boolean;
  /** Empreinte de la valeur. C'est elle qui permet de comparer deux fichiers. */
  empreinte: string;
  /** La forme reconnue aux octets. Jamais un SENS, seulement une forme. */
  forme: string | null;
  /** Un aperçu du texte, quand la valeur EST du texte. Tronqué. */
  apercuTexte: string | null;
  /** Le sens, s'il est au registre. Vide par construction. */
  sens: [string, string] | null;
}

/** Ce que la structure d'une note propriétaire permet de dire. */
export interface AnalyseMakerNote {
  present: boolean;
  octets: number;
  constructeur: string | null;
  signatureHex: string | null;
  /**
   * L'empreinte de la note ENTIÈRE. Deux fichiers qui la partagent sortent du
   * même appareil aux mêmes réglages.
   */
  empreinte: string | null;
  /** La base d'offset RETENUE, celle qui a donné un IFD cohérent. */
  baseRetenue: string | null;
  baseAttendue: string | null;
  /** Vrai quand la base retenue est celle que la documentation annonçait. */
  baseConforme: boolean | null;
  boutisme: string | null;
  tags: TagProprietaire[];
  nombreDeTags: number;
  /** Pourquoi la structure n'a pas pu être lue, le cas échéant. */
  motifStructureIllisible: string | null;
  motifAucunSens: string;
  remarqueConstructeur: string;
}

/**
 * Le constructeur, reconnu à sa signature dans les octets.
 *
 * Canon n'a PAS de signature : sa note commence directement par un IFD. Elle
 * n'est donc pas reconnue ici, et c'est volontaire — deviner « Canon » parce
 * qu'aucune autre signature ne correspond attribuerait à Canon toutes les
 * notes de constructeurs qu'on ne connaît pas.
 */
export function reconnaitreConstructeur(note: Uint8Array): SignatureConstructeur | null {
  for (const s of SIGNATURES) {
    if (note.length < s.magie.length) continue;
    let egal = true;
    for (let i = 0; i < s.magie.length; i += 1) {
      if (note[i] !== s.magie[i]) { egal = false; break; }
    }
    if (egal) return s;
  }
  return null;
}

/** Une entrée d'IFD : identifiant, type, cardinalité, position de la valeur, en ligne. */
type EntreeIfd = [number, number, number, number, boolean];

/**
 * Parcourt un IFD et rend ses entrées, ou null si la structure est incohérente.
 *
 * Rendre null plutôt que lever : l'appelant essaie plusieurs bases, et un échec
 * est une information normale du protocole d'essai, pas une anomalie.
 *
 * UNE CARDINALITÉ ABERRANTE est bien le signal le plus fiable d'une mauvaise
 * base — mais elle n'a pas besoin d'un contrôle à elle. Un balayage l'a établi :
 * toute taille supérieure à la note fait déborder le contrôle d'offset qui
 * suit, puisqu'un offset négatif est écarté à part. Un second contrôle
 * n'écarterait rien de plus, et se lirait comme une protection qu'il n'apporte
 * pas.
 */
function lireIfd(
  note: Uint8Array, offsetIfd: number, endian: '<' | '>', base: number,
): EntreeIfd[] | null {
  if (offsetIfd < 0 || offsetIfd + 2 > note.length) return null;
  const vue = new DataView(note.buffer, note.byteOffset, note.byteLength);
  const pt = endian === '<';
  const nb = vue.getUint16(offsetIfd, pt);
  // Un IFD réel dépasse rarement la centaine d'entrées ; au-delà de 512, on a
  // certainement lu des octets qui ne sont pas un compteur.
  if (nb === 0 || nb > 512) return null;
  if (offsetIfd + 2 + 12 * nb > note.length) return null;

  const entrees: EntreeIfd[] = [];
  for (let i = 0; i < nb; i += 1) {
    const p = offsetIfd + 2 + 12 * i;
    const tag = vue.getUint16(p, pt);
    const type = vue.getUint16(p + 2, pt);
    const cardinalite = vue.getUint32(p + 4, pt);
    const tailleElem = TAILLE_TYPE[type] ?? 0;
    if (tailleElem === 0) {
      // Type inconnu : l'entrée est écartée, mais elle ne condamne pas l'IFD —
      // un constructeur peut employer un type non normalisé.
      continue;
    }
    const total = tailleElem * cardinalite;
    if (total <= 4) {
      entrees.push([tag, type, cardinalite, p + 8, true]);
    } else {
      const offsetValeur = vue.getUint32(p + 8, pt) - base;
      if (offsetValeur < 0 || offsetValeur + total > note.length) return null;
      entrees.push([tag, type, cardinalite, offsetValeur, false]);
    }
  }
  // Un IFD dont TOUTES les entrées ont été écartées n'est pas un IFD.
  return entrees.length > 0 ? entrees : null;
}

function debutEgal(valeur: Uint8Array, motif: string): boolean {
  if (valeur.length < motif.length) return false;
  for (let i = 0; i < motif.length; i += 1) {
    if (valeur[i] !== (motif.charCodeAt(i) & 0xff)) return false;
  }
  return true;
}

/**
 * La forme reconnue aux octets, et un aperçu si c'est du texte.
 *
 * Une forme n'est pas un sens : dire qu'un tag contient une liste de propriétés
 * binaire ne dit rien de ce qu'il y a dedans. Mais savoir qu'un tag de 400
 * octets est du texte lisible oriente l'analyste vers ce qu'il peut aller
 * regarder.
 */
function formeDe(valeur: Uint8Array): [string | null, string | null] {
  if (valeur.length === 0) return [null, null];
  if (debutEgal(valeur, 'bplist00')) return ['liste de propriétés binaire (bplist)', null];
  if (valeur.length > 4 && valeur[0] === 0xff && valeur[1] === 0xd8) return ['JPEG embarqué', null];
  if (debutEgal(valeur, 'II*\u0000') || debutEgal(valeur, 'MM\u0000*')) {
    return ['en-tête TIFF imbriqué', null];
  }
  if (debutEgal(valeur, '<?xml') || debutEgal(valeur, '<?xpacket')) return ['XML', null];
  // Du texte : au moins 90 % d'octets imprimables, et au moins quatre octets.
  if (valeur.length >= 4) {
    let imprimables = 0;
    for (const o of valeur) {
      if ((o >= 32 && o < 127) || o === 9 || o === 10 || o === 13 || o === 0) imprimables += 1;
    }
    if (imprimables >= 0.9 * valeur.length) {
      let fin = valeur.indexOf(0);
      if (fin < 0) fin = valeur.length;
      let texte = '';
      for (let i = 0; i < fin; i += 1) {
        const o = valeur[i];
        texte += o < 128 ? String.fromCharCode(o) : '�';
      }
      texte = texte.trim();
      if (texte) return ['texte', texte.slice(0, 120)];
    }
  }
  return [null, null];
}

function hex(octets: Uint8Array): string {
  let s = '';
  for (const o of octets) s += o.toString(16).padStart(2, '0');
  return s;
}

/**
 * Analyse la STRUCTURE d'une note propriétaire.
 *
 * `offsetDansLeTiff` est la position de la note depuis l'en-tête TIFF du
 * fichier. Elle est nécessaire pour la base « tiff » : les offsets y sont
 * comptés depuis cet en-tête, alors que `note` commence plus loin.
 *
 * `boutismeFichier` est celui du bloc TIFF englobant. Il sert de défaut aux
 * constructeurs qui n'imposent pas le leur.
 */
export async function analyserMakerNote(
  note: Uint8Array,
  offsetDansLeTiff = 0,
  boutismeFichier: '<' | '>' = '<',
): Promise<AnalyseMakerNote> {
  const vide: AnalyseMakerNote = {
    present: false, octets: 0, constructeur: null, signatureHex: null,
    empreinte: null, baseRetenue: null, baseAttendue: null, baseConforme: null,
    boutisme: null, tags: [], nombreDeTags: 0, motifStructureIllisible: null,
    motifAucunSens: MOTIF_AUCUN_SENS, remarqueConstructeur: '',
  };
  if (note.length === 0) return vide;

  const a: AnalyseMakerNote = {
    ...vide,
    present: true,
    octets: note.length,
    empreinte: await empreinteSha256(note),
    signatureHex: hex(note.subarray(0, 16)),
  };

  const s = reconnaitreConstructeur(note);
  let boutisme: '<' | '>';
  let decalage: number;
  if (s !== null) {
    a.constructeur = s.nom;
    a.baseAttendue = s.baseAttendue;
    a.remarqueConstructeur = s.remarque;
    boutisme = s.boutisme ?? boutismeFichier;
    decalage = s.decalageIfd;
  } else {
    // Aucune signature. La note commence peut-être directement par un IFD —
    // c'est le cas de Canon — mais on ne le NOMME pas : attribuer à Canon toute
    // note sans signature lui attribuerait tous les constructeurs qu'on ne
    // connaît pas.
    a.constructeur = null;
    a.baseAttendue = null;
    boutisme = boutismeFichier;
    decalage = 0;
  }

  // Les bases candidates, dans l'ordre où on les essaie. Les formes
  // PARTICULIÈRES d'abord — en-tête TIFF interne de Nikon, offset écrit en
  // clair chez Fujifilm — parce qu'elles se vérifient aux octets. Viennent
  // ensuite les deux bases générales, « note » puis « tiff ».
  //
  // Cet ordre ne privilégie PAS la base annoncée par la documentation, et c'est
  // délibéré : c'est la cohérence de l'IFD qui tranche, pas ce qu'on attendait.
  // `baseConforme` dit ensuite si les deux coïncident.
  const candidats: [string, number, number, '<' | '>'][] = [];
  const ajouter = (nom: string, offsetIfd: number, base: number, endian: '<' | '>') => {
    for (const c of candidats) {
      if (c[0] === nom && c[1] === offsetIfd && c[2] === base && c[3] === endian) return;
    }
    candidats.push([nom, offsetIfd, base, endian]);
  };

  const vueNote = new DataView(note.buffer, note.byteOffset, note.byteLength);
  if (s !== null && s.baseAttendue === 'tiff_interne') {
    // Nikon type 3 : un en-tête TIFF COMPLET commence au décalage annoncé.
    // C'est la seule famille dans ce cas, et l'en-tête se vérifie.
    const p = s.decalageIfd;
    if (p + 8 <= note.length
        && ((note[p] === 0x49 && note[p + 1] === 0x49)
          || (note[p] === 0x4d && note[p + 1] === 0x4d))) {
      const e: '<' | '>' = note[p] === 0x49 ? '<' : '>';
      if (vueNote.getUint16(p + 2, e === '<') === 42) {
        const offset0 = vueNote.getUint32(p + 4, e === '<');
        ajouter('tiff_interne', p + offset0, -p, e);
      }
    }
  }
  if (s !== null && s.nom === 'Fujifilm' && note.length >= 12) {
    // L'offset de l'IFD est écrit en clair aux octets 8 à 11.
    const off = vueNote.getUint32(8, true);
    if (off > 0 && off < note.length) ajouter('note', off, 0, '<');
  }

  const boutismes: ('<' | '>')[] = (s !== null && s.boutisme)
    ? [boutisme]
    : [boutismeFichier, '<', '>'];
  for (const endian of boutismes) {
    ajouter('note', decalage, 0, endian);
    ajouter('tiff', decalage, offsetDansLeTiff, endian);
    if (s === null) {
      // Sans signature, l'IFD peut aussi commencer plus loin — certaines notes
      // portent quelques octets d'en-tête non reconnus.
      for (const d of [2, 4, 6, 8, 10, 12]) ajouter('note', d, 0, endian);
    }
  }

  for (const [nomBase, offsetIfd, base, endian] of candidats) {
    const entrees = lireIfd(note, offsetIfd, endian, base);
    if (entrees === null) continue;
    a.baseRetenue = nomBase;
    a.boutisme = endian === '<' ? 'petit-boutien' : 'gros-boutien';
    a.baseConforme = a.baseAttendue === null || nomBase === a.baseAttendue;
    const tags: TagProprietaire[] = [];
    for (const [tag, type, cardinalite, pos, enLigne] of entrees) {
      const total = (TAILLE_TYPE[type] ?? 0) * cardinalite;
      const valeur = note.subarray(pos, pos + total);
      const [forme, apercu] = formeDe(valeur);
      tags.push({
        identifiant: tag,
        type,
        typeNom: NOMS_TYPE[type] ?? `type ${type}`,
        cardinalite,
        octets: total,
        enLigne,
        // eslint-disable-next-line no-await-in-loop
        empreinte: await empreinteSha256(valeur),
        forme,
        apercuTexte: apercu,
        sens: SENS_CONNUS[`${a.constructeur ?? ''}|${tag}`] ?? null,
      });
    }
    tags.sort((x, y) => x.identifiant - y.identifiant);
    a.tags = tags;
    a.nombreDeTags = tags.length;
    return a;
  }

  a.motifStructureIllisible =
    `Aucune base d'offset ne donne un IFD cohérent (${candidats.length} essayées). `
    + 'La note est présente et son empreinte reste valide, mais sa structure '
    + "n'est pas celle d'un IFD TIFF — plusieurs constructeurs emploient des "
    + 'formats binaires propres, et certains chiffrent une partie de leurs notes.';
  return a;
}
