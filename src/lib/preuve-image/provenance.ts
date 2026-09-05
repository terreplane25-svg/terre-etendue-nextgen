/**
 * provenance.ts — Port TypeScript de `preuve_image.provenance` (outil B).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-B-preuve-image/preuve_image/provenance.py`.
 * Ce port existe parce que l'image ne doit pas quitter la machine de
 * l'opérateur : l'ingestion tourne dans le navigateur. Il est épinglé au Python
 * par les vecteurs de `vecteurs-or-provenance.json`, que
 * `scripts/verifier-port-provenance.mjs` rejoue ici.
 *
 * Toute correction se fait DANS LE PYTHON d'abord, puis se répercute ici, puis
 * les vecteurs sont régénérés. Jamais l'inverse.
 *
 * CE QUE CE MODULE ÉTABLIT, ET CE QU'IL N'ÉTABLIT PAS
 * ───────────────────────────────────────────────────
 * Il établit ce qu'un fichier DÉCLARE. Il n'établit rien de ce que ces
 * déclarations affirment. En particulier, **aucune signature n'est vérifiée** :
 * ni la validation COSE, ni la chaîne X.509, ni les empreintes de liaison au
 * contenu. Un manifeste C2PA lisible peut être authentique, désolidarisé de
 * l'image, ou entièrement fabriqué — cette lecture ne les distingue pas.
 * Symétriquement, son absence n'est pas un indice : presque aucun appareil n'en
 * écrit, et la plupart des retouches effacent ceux qui existaient.
 */

export class ProvenanceError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ProvenanceError';
  }
}

export const AVERTISSEMENT_C2PA =
  "Aucune signature n'est vérifiée. Ce qui suit est ce que le fichier déclare, "
  + 'pas ce qui est établi : un manifeste C2PA peut être authentique, désolidarisé '
  + 'du contenu, ou entièrement fabriqué — cette lecture ne les distingue pas. '
  + "L'absence de manifeste n'est pas davantage un indice : presque aucun appareil "
  + "n'en écrit, et la plupart des retouches effacent ceux qui existaient.";

export const MOTIF_NON_VERIFIEE =
  'La vérification exige la validation COSE, la chaîne X.509 et une liste de '
  + "confiance : rien de cela n'est implémenté ici.";

const PROFONDEUR_MAX = 32;

// ─────────────────────────────────────────────────────────────────────────────
// CBOR (RFC 8949)
// ─────────────────────────────────────────────────────────────────────────────

export type ValeurCbor =
  | number | string | boolean | null | Uint8Array
  | ValeurCbor[] | { [cle: string]: ValeurCbor };

interface Lecture { valeur: ValeurCbor; pos: number }

function lireTete(d: Uint8Array, pos: number): { majeur: number; arg: number; pos: number } {
  if (pos >= d.length) throw new ProvenanceError('CBOR tronqué : en-tête attendu.');
  const octet = d[pos];
  const majeur = octet >> 5;
  const info = octet & 0x1f;
  pos += 1;
  if (info < 24) return { majeur, arg: info, pos };
  if (info === 24) {
    if (pos + 1 > d.length) throw new ProvenanceError('CBOR tronqué : argument sur 1 octet.');
    return { majeur, arg: d[pos], pos: pos + 1 };
  }
  for (const [code, n] of [[25, 2], [26, 4], [27, 8]] as const) {
    if (info === code) {
      if (pos + n > d.length) throw new ProvenanceError(`CBOR tronqué : argument sur ${n} octets.`);
      let v = 0;
      for (let i = 0; i < n; i += 1) v = v * 256 + d[pos + i];
      return { majeur, arg: v, pos: pos + n };
    }
  }
  if (info === 31) return { majeur, arg: -1, pos };
  throw new ProvenanceError(`CBOR : information additionnelle ${info} réservée.`);
}

const utf8 = new TextDecoder('utf-8');

function decoderElement(d: Uint8Array, posInitiale: number, profondeur: number): Lecture {
  if (profondeur > PROFONDEUR_MAX) {
    throw new ProvenanceError("CBOR : imbrication au-delà de la profondeur admise.");
  }
  const tete = lireTete(d, posInitiale);
  const majeur = tete.majeur;
  const arg = tete.arg;
  let pos = tete.pos;

  if (majeur === 0) return { valeur: arg, pos };
  if (majeur === 1) return { valeur: -1 - arg, pos };

  if (majeur === 2 || majeur === 3) {
    if (arg === -1) {
      const morceaux: ValeurCbor[] = [];
      for (;;) {
        if (pos < d.length && d[pos] === 0xff) { pos += 1; break; }
        const r = decoderElement(d, pos, profondeur + 1);
        morceaux.push(r.valeur);
        pos = r.pos;
      }
      if (majeur === 2) {
        const blocs = morceaux as Uint8Array[];
        const total = blocs.reduce((n: number, m) => n + m.length, 0);
        const out = new Uint8Array(total);
        let o = 0;
        for (const m of blocs) { out.set(m, o); o += m.length; }
        return { valeur: out, pos };
      }
      return { valeur: (morceaux as string[]).join(''), pos };
    }
    if (pos + arg > d.length) throw new ProvenanceError('CBOR tronqué : chaîne hors des limites.');
    const bloc = d.subarray(pos, pos + arg);
    pos += arg;
    return { valeur: majeur === 2 ? new Uint8Array(bloc) : utf8.decode(bloc), pos };
  }

  if (majeur === 4) {
    const elements: ValeurCbor[] = [];
    if (arg === -1) {
      for (;;) {
        if (pos < d.length && d[pos] === 0xff) { pos += 1; break; }
        const r = decoderElement(d, pos, profondeur + 1);
        elements.push(r.valeur);
        pos = r.pos;
      }
    } else {
      for (let i = 0; i < arg; i += 1) {
        const r = decoderElement(d, pos, profondeur + 1);
        elements.push(r.valeur);
        pos = r.pos;
      }
    }
    return { valeur: elements, pos };
  }

  if (majeur === 5) {
    const table: { [cle: string]: ValeurCbor } = {};
    const poser = (cle: ValeurCbor, val: ValeurCbor) => {
      table[typeof cle === 'string' || typeof cle === 'number' ? String(cle) : JSON.stringify(cle)] = val;
    };
    if (arg === -1) {
      for (;;) {
        if (pos < d.length && d[pos] === 0xff) { pos += 1; break; }
        const c = decoderElement(d, pos, profondeur + 1);
        const v = decoderElement(d, c.pos, profondeur + 1);
        poser(c.valeur, v.valeur);
        pos = v.pos;
      }
    } else {
      for (let i = 0; i < arg; i += 1) {
        const c = decoderElement(d, pos, profondeur + 1);
        const v = decoderElement(d, c.pos, profondeur + 1);
        poser(c.valeur, v.valeur);
        pos = v.pos;
      }
    }
    return { valeur: table, pos };
  }

  if (majeur === 6) {
    const r = decoderElement(d, pos, profondeur + 1);
    return { valeur: { _etiquette_cbor: arg, valeur: r.valeur }, pos: r.pos };
  }

  if (arg === 20) return { valeur: false, pos };
  if (arg === 21) return { valeur: true, pos };
  if (arg === 22) return { valeur: null, pos };
  if (arg === 23) return { valeur: '_indefini', pos };
  return { valeur: arg, pos };
}

/** Décode un élément CBOR. Les octets restants sont ignorés, comme côté Python. */
export function decoderCbor(donnees: Uint8Array): ValeurCbor {
  return decoderElement(donnees, 0, 0).valeur;
}

// ─────────────────────────────────────────────────────────────────────────────
// JUMBF (ISO/IEC 19566-5)
// ─────────────────────────────────────────────────────────────────────────────

export interface BoiteJumbf {
  type: string;
  taille: number;
  offset: number;
  label: string | null;
  uuidType: string | null;
  charge: Uint8Array;
  filles: BoiteJumbf[];
}

const ascii = new TextDecoder('ascii');

function lireDescription(charge: Uint8Array): { label: string | null; uuidType: string | null } {
  if (charge.length < 17) return { label: null, uuidType: null };
  let uuidType = '';
  for (let i = 0; i < 16; i += 1) uuidType += charge[i].toString(16).padStart(2, '0');
  const drapeaux = charge[16];
  let label: string | null = null;
  if (drapeaux & 0x02) {
    let fin = 17;
    while (fin < charge.length && charge[fin] !== 0) fin += 1;
    label = utf8.decode(charge.subarray(17, fin));
  }
  return { label, uuidType };
}

function u32(d: Uint8Array, pos: number): number {
  return ((d[pos] << 24) >>> 0) + (d[pos + 1] << 16) + (d[pos + 2] << 8) + d[pos + 3];
}

function u64(d: Uint8Array, pos: number): number {
  let v = 0;
  for (let i = 0; i < 8; i += 1) v = v * 256 + d[pos + i];
  return v;
}

/**
 * Décode une suite de boîtes JUMBF. Une boîte malformée arrête le parcours du
 * niveau courant sans lever : un conteneur partiel se lit jusqu'où il est
 * lisible, et ce qui précède reste utilisable.
 */
export function analyserBoitesJumbf(
  donnees: Uint8Array, offsetBase = 0, profondeur = 0,
): BoiteJumbf[] {
  if (profondeur > PROFONDEUR_MAX) return [];
  const boites: BoiteJumbf[] = [];
  let pos = 0;
  while (pos + 8 <= donnees.length) {
    let lbox = u32(donnees, pos);
    const tbox = donnees.subarray(pos + 4, pos + 8);
    let entete = 8;
    if (lbox === 1) {
      if (pos + 16 > donnees.length) break;
      lbox = u64(donnees, pos + 8);
      entete = 16;
    } else if (lbox === 0) {
      lbox = donnees.length - pos;
    }
    if (lbox < entete || pos + lbox > donnees.length) break;
    const charge = donnees.subarray(pos + entete, pos + lbox);
    const type = ascii.decode(tbox);
    const boite: BoiteJumbf = {
      type, taille: lbox, offset: offsetBase + pos,
      label: null, uuidType: null, charge: new Uint8Array(0), filles: [],
    };
    if (type === 'jumb') {
      boite.filles = analyserBoitesJumbf(charge, offsetBase + pos + entete, profondeur + 1);
      for (const f of boite.filles) {
        if (f.type === 'jumd') {
          const d = lireDescription(f.charge);
          boite.label = d.label;
          boite.uuidType = d.uuidType;
          break;
        }
      }
    } else {
      // Copie dans un tampon neuf : `subarray` partage la mémoire du fichier
      // entier, qu'on ne veut pas retenir pour quelques octets de charge.
      boite.charge = new Uint8Array(charge);
    }
    boites.push(boite);
    pos += lbox;
  }
  return boites;
}

function trouverBoite(b: BoiteJumbf, label: string): BoiteJumbf | null {
  if (b.label === label) return b;
  for (const f of b.filles) {
    const t = trouverBoite(f, label);
    if (t !== null) return t;
  }
  return null;
}

function toutesLesBoites(b: BoiteJumbf): BoiteJumbf[] {
  const out = [b];
  for (const f of b.filles) out.push(...toutesLesBoites(f));
  return out;
}

// ─────────────────────────────────────────────────────────────────────────────
// C2PA
// ─────────────────────────────────────────────────────────────────────────────

export interface ManifesteC2PA {
  label: string;
  assertions: { [label: string]: ValeurCbor };
  actions: Array<{ [cle: string]: ValeurCbor }>;
  revendication: { [cle: string]: ValeurCbor } | null;
  signaturePresente: boolean;
  algorithmeSignature: string | null;
  generateur: string | null;
}

export interface ResultatC2PA {
  present: boolean;
  conteneur: string | null;
  octets: number;
  manifestes: ManifesteC2PA[];
  boites: string[];
  avertissement: string;
  signatureVerifiee: false;
  motifNonVerifiee: string;
}

function segmentsC2paJpeg(d: Uint8Array): Array<[number, number, Uint8Array]> {
  const segments: Array<[number, number, Uint8Array]> = [];
  let pos = 2;
  while (pos + 4 <= d.length) {
    if (d[pos] !== 0xff) break;
    const marqueur = d[pos + 1];
    if (marqueur === 0xd8 || (marqueur >= 0xd0 && marqueur <= 0xd7)) { pos += 2; continue; }
    if (marqueur === 0xd9 || marqueur === 0xda) break;
    const longueur = (d[pos + 2] << 8) + d[pos + 3];
    if (marqueur === 0xeb) {
      const corps = d.subarray(pos + 4, pos + 2 + longueur);
      if (corps.length >= 8 && corps[0] === 0x4a && corps[1] === 0x50) {
        const instance = (corps[2] << 8) + corps[3];
        const paquet = u32(corps, 4);
        segments.push([instance, paquet, corps.subarray(8)]);
      }
    }
    pos += 2 + longueur;
  }
  return segments;
}

/**
 * Recolle les fragments répartis sur plusieurs segments APP11 : regroupés par
 * numéro d'instance, triés par numéro de paquet. Un fichier dont les paquets
 * arrivent dans le désordre est ainsi lu correctement.
 */
function reassemblerApp11(segments: Array<[number, number, Uint8Array]>): Uint8Array {
  const parInstance = new Map<number, Array<[number, Uint8Array]>>();
  for (const [instance, paquet, charge] of segments) {
    if (!parInstance.has(instance)) parInstance.set(instance, []);
    parInstance.get(instance)!.push([paquet, charge]);
  }
  const morceaux: Uint8Array[] = [];
  for (const instance of [...parInstance.keys()].sort((a, b) => a - b)) {
    const liste = parInstance.get(instance)!.slice().sort((a, b) => a[0] - b[0]);
    for (const [, charge] of liste) morceaux.push(charge);
  }
  const total = morceaux.reduce((n, m) => n + m.length, 0);
  const out = new Uint8Array(total);
  let o = 0;
  for (const m of morceaux) { out.set(m, o); o += m.length; }
  return out;
}

function c2paDepuisPng(d: Uint8Array): Uint8Array {
  const morceaux: Uint8Array[] = [];
  let pos = 8;
  while (pos + 8 <= d.length) {
    const longueur = u32(d, pos);
    const type = ascii.decode(d.subarray(pos + 4, pos + 8));
    if (pos + 12 + longueur > d.length) break;
    if (type === 'caBX') morceaux.push(d.subarray(pos + 8, pos + 8 + longueur));
    if (type === 'IEND') break;
    pos += 12 + longueur;
  }
  const total = morceaux.reduce((n, m) => n + m.length, 0);
  const out = new Uint8Array(total);
  let o = 0;
  for (const m of morceaux) { out.set(m, o); o += m.length; }
  return out;
}

function chargeUtile(boite: BoiteJumbf): ValeurCbor {
  for (const fille of boite.filles) {
    if (fille.type === 'cbor') {
      try { return decoderCbor(fille.charge); } catch { return null; }
    }
    if (fille.type === 'json') {
      try { return JSON.parse(utf8.decode(fille.charge)) as ValeurCbor; } catch { return null; }
    }
  }
  return null;
}

function lireManifeste(boite: BoiteJumbf): ManifesteC2PA {
  const assertions: { [label: string]: ValeurCbor } = {};
  const actions: Array<{ [cle: string]: ValeurCbor }> = [];
  let revendication: { [cle: string]: ValeurCbor } | null = null;
  let signaturePresente = false;
  let algorithmeSignature: string | null = null;
  let generateur: string | null = null;

  for (const fille of boite.filles) {
    if (fille.label === 'c2pa.assertions') {
      for (const a of fille.filles) {
        if (a.label === null) continue;
        const contenu = chargeUtile(a);
        assertions[a.label] = contenu;
        if (a.label.startsWith('c2pa.actions') && contenu && typeof contenu === 'object' && !Array.isArray(contenu)) {
          const liste = (contenu as { [c: string]: ValeurCbor }).actions;
          if (Array.isArray(liste)) {
            for (const x of liste) {
              if (x && typeof x === 'object' && !Array.isArray(x) && !(x instanceof Uint8Array)) {
                actions.push(x as { [cle: string]: ValeurCbor });
              }
            }
          }
        }
      }
    } else if (fille.label === 'c2pa.claim' || fille.label === 'c2pa.claim.v2') {
      const c = chargeUtile(fille);
      if (c && typeof c === 'object' && !Array.isArray(c) && !(c instanceof Uint8Array)) {
        revendication = c as { [cle: string]: ValeurCbor };
        const gen = revendication.claim_generator;
        if (typeof gen === 'string') {
          generateur = gen;
        } else if (Array.isArray(revendication.claim_generator_info)) {
          const infos = revendication.claim_generator_info;
          const premier = infos[0];
          if (premier && typeof premier === 'object' && !Array.isArray(premier)) {
            const nom = (premier as { [c: string]: ValeurCbor }).name;
            generateur = nom ? String(nom) : null;
          }
        }
        if (typeof revendication.alg === 'string') algorithmeSignature = revendication.alg;
      }
    } else if (fille.label === 'c2pa.signature') {
      signaturePresente = true;
    }
  }

  return {
    label: boite.label ?? '(sans label)',
    assertions, actions, revendication,
    signaturePresente, algorithmeSignature, generateur,
  };
}

/** Localise et lit le conteneur C2PA d'un JPEG ou d'un PNG. Ne vérifie RIEN. */
export function extraireC2pa(donnees: Uint8Array): ResultatC2PA {
  const vide: ResultatC2PA = {
    present: false, conteneur: null, octets: 0, manifestes: [], boites: [],
    avertissement: AVERTISSEMENT_C2PA, signatureVerifiee: false,
    motifNonVerifiee: MOTIF_NON_VERIFIEE,
  };

  let conteneur: string | null = null;
  // Annotation explicite : les fonctions de collecte rendent des vues dont le
  // tampon est `ArrayBufferLike`, et l'inférence à partir de `new Uint8Array(0)`
  // les refuserait sous `--strict`.
  let brut: Uint8Array<ArrayBufferLike> = new Uint8Array(0);
  const estJpeg = donnees[0] === 0xff && donnees[1] === 0xd8;
  const signaturePng = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
  const estPng = signaturePng.every((o, i) => donnees[i] === o);

  if (estJpeg) {
    const segments = segmentsC2paJpeg(donnees);
    if (segments.length > 0) {
      conteneur = 'JPEG APP11 / JUMBF';
      brut = reassemblerApp11(segments);
    }
  } else if (estPng) {
    brut = c2paDepuisPng(donnees);
    if (brut.length > 0) conteneur = 'PNG caBX / JUMBF';
  }

  if (brut.length === 0) return vide;

  const boites = analyserBoitesJumbf(brut);
  let magasin: BoiteJumbf | null = null;
  for (const b of boites) {
    const t = trouverBoite(b, 'c2pa');
    if (t !== null) { magasin = t; break; }
  }
  const manifestes: ManifesteC2PA[] = [];
  if (magasin !== null) {
    for (const m of magasin.filles) {
      if (m.type === 'jumb' && m.label) manifestes.push(lireManifeste(m));
    }
  }
  const etiquettes: string[] = [];
  for (const b of boites) {
    for (const x of toutesLesBoites(b)) if (x.label) etiquettes.push(x.label);
  }

  return {
    present: true, conteneur, octets: brut.length, manifestes, boites: etiquettes,
    avertissement: AVERTISSEMENT_C2PA, signatureVerifiee: false,
    motifNonVerifiee: MOTIF_NON_VERIFIEE,
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// XMP
// ─────────────────────────────────────────────────────────────────────────────

export interface BlocXmp {
  conteneur: string;
  octets: number;
  brut: string;
  etendu: boolean;
  champs: { [nom: string]: string };
}

const CHAMPS_XMP = [
  'xmp:CreatorTool', 'xmp:ModifyDate', 'xmp:CreateDate', 'xmp:MetadataDate',
  'tiff:Make', 'tiff:Model', 'dc:creator', 'dc:rights',
  'photoshop:DateCreated', 'photoshop:History',
  'crs:Version', 'crs:ProcessVersion',
  'dcterms:provenance', 'c2pa:manifest',
  'GCamera:MicroVideo', 'Container:Directory',
];

const echapper = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

function releverChampsXmp(texte: string): { [nom: string]: string } {
  const champs: { [nom: string]: string } = {};
  for (const nom of CHAMPS_XMP) {
    const attribut = new RegExp(`${echapper(nom)}\\s*=\\s*"([^"]*)"`).exec(texte);
    if (attribut) { champs[nom] = attribut[1]; continue; }
    const element = new RegExp(`${echapper(nom)}[^>]*>([^<]{1,400})<`).exec(texte);
    if (element) champs[nom] = element[1].trim();
  }
  return champs;
}

const NS_XMP = 'http://ns.adobe.com/xap/1.0/\0';
const NS_XMP_ETENDU = 'http://ns.adobe.com/xmp/extension/\0';

function commencePar(d: Uint8Array, prefixe: string): boolean {
  if (d.length < prefixe.length) return false;
  for (let i = 0; i < prefixe.length; i += 1) if (d[i] !== prefixe.charCodeAt(i)) return false;
  return true;
}

/** Relève les paquets XMP d'un JPEG (APP1) ou d'un PNG (iTXt/tEXt). */
export function extraireXmp(donnees: Uint8Array): BlocXmp[] {
  const blocs: BlocXmp[] = [];
  const estJpeg = donnees[0] === 0xff && donnees[1] === 0xd8;
  const signaturePng = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
  const estPng = signaturePng.every((o, i) => donnees[i] === o);

  if (estJpeg) {
    let pos = 2;
    while (pos + 4 <= donnees.length) {
      if (donnees[pos] !== 0xff) break;
      const marqueur = donnees[pos + 1];
      if (marqueur === 0xd8 || (marqueur >= 0xd0 && marqueur <= 0xd7)) { pos += 2; continue; }
      if (marqueur === 0xd9 || marqueur === 0xda) break;
      const longueur = (donnees[pos + 2] << 8) + donnees[pos + 3];
      const corps = donnees.subarray(pos + 4, pos + 2 + longueur);
      if (marqueur === 0xe1) {
        for (const [ns, etendu] of [[NS_XMP, false], [NS_XMP_ETENDU, true]] as const) {
          if (commencePar(corps, ns)) {
            let charge = corps.subarray(ns.length);
            // Le XMP étendu porte 40 octets d'en-tête (GUID, tailles).
            if (etendu && charge.length > 40) charge = charge.subarray(40);
            const texte = utf8.decode(charge);
            blocs.push({
              conteneur: 'JPEG APP1 / XMP' + (etendu ? ' étendu' : ''),
              octets: charge.length, brut: texte, etendu, champs: releverChampsXmp(texte),
            });
          }
        }
      }
      pos += 2 + longueur;
    }
  } else if (estPng) {
    let pos = 8;
    while (pos + 8 <= donnees.length) {
      const longueur = u32(donnees, pos);
      const type = ascii.decode(donnees.subarray(pos + 4, pos + 8));
      if (pos + 12 + longueur > donnees.length) break;
      const charge = donnees.subarray(pos + 8, pos + 8 + longueur);
      if (type === 'iTXt' || type === 'tEXt') {
        const entete = ascii.decode(charge.subarray(0, Math.min(64, charge.length)));
        if (entete.includes('XML:com.adobe.xmp')) {
          const texteEntier = utf8.decode(charge);
          let debut = texteEntier.indexOf('<x:xmpmeta');
          if (debut === -1) debut = texteEntier.indexOf('<?xpacket');
          if (debut !== -1) {
            const texte = texteEntier.slice(debut);
            blocs.push({
              conteneur: `PNG ${type} / XMP`, octets: texte.length,
              brut: texte, etendu: false, champs: releverChampsXmp(texte),
            });
          }
        }
      }
      if (type === 'IEND') break;
      pos += 12 + longueur;
    }
  }
  return blocs;
}

// ─────────────────────────────────────────────────────────────────────────────
// IPTC-IIM (APP13 / Photoshop IRB)
// ─────────────────────────────────────────────────────────────────────────────

export interface EnregistrementIptc {
  jeu: number;
  numero: number;
  libelle: string;
  valeur: string;
}

const CHAMPS_IIM: { [n: number]: string } = {
  5: "Titre de l'objet", 10: 'Urgence', 15: 'Catégorie', 20: 'Catégorie supplémentaire',
  25: 'Mots-clés', 40: 'Instructions particulières', 55: 'Date de création',
  60: 'Heure de création', 62: 'Date de numérisation', 65: "Programme d'origine",
  70: 'Version du programme', 80: 'Auteur', 85: "Fonction de l'auteur",
  90: 'Ville', 92: 'Lieu-dit', 95: 'Région', 100: 'Code pays', 101: 'Pays',
  103: 'Référence de transmission', 105: 'Titre rédactionnel', 110: 'Crédit',
  115: 'Source', 116: 'Mention de droits', 120: 'Légende', 122: 'Auteur de la légende',
};

const ENTETE_PHOTOSHOP = 'Photoshop 3.0\0';
const RESSOURCE_IPTC = 0x0404;

function lireIim(bloc: Uint8Array): EnregistrementIptc[] {
  const out: EnregistrementIptc[] = [];
  let pos = 0;
  while (pos + 5 <= bloc.length) {
    if (bloc[pos] !== 0x1c) { pos += 1; continue; }
    const jeu = bloc[pos + 1];
    const numero = bloc[pos + 2];
    let taille = (bloc[pos + 3] << 8) + bloc[pos + 4];
    let debut = pos + 5;
    if (taille & 0x8000) {
      const n = taille & 0x7fff;
      if (debut + n > bloc.length) break;
      taille = 0;
      for (let i = 0; i < n; i += 1) taille = taille * 256 + bloc[debut + i];
      debut += n;
    }
    if (debut + taille > bloc.length) break;
    out.push({
      jeu, numero,
      libelle: CHAMPS_IIM[numero] ?? `jeu ${jeu}, champ ${numero}`,
      valeur: utf8.decode(bloc.subarray(debut, debut + taille)),
    });
    pos = debut + taille;
  }
  return out;
}

function lireIrb(bloc: Uint8Array): EnregistrementIptc[] {
  const out: EnregistrementIptc[] = [];
  let pos = 0;
  while (pos + 12 <= bloc.length) {
    if (ascii.decode(bloc.subarray(pos, pos + 4)) !== '8BIM') break;
    const identifiant = (bloc[pos + 4] << 8) + bloc[pos + 5];
    const tailleNom = bloc[pos + 6];
    let posApresNom = pos + 6 + 1 + tailleNom;
    if ((tailleNom + 1) % 2) posApresNom += 1;
    if (posApresNom + 4 > bloc.length) break;
    const taille = u32(bloc, posApresNom);
    const debut = posApresNom + 4;
    if (debut + taille > bloc.length) break;
    if (identifiant === RESSOURCE_IPTC) out.push(...lireIim(bloc.subarray(debut, debut + taille)));
    pos = debut + taille + (taille % 2);
  }
  return out;
}

/** Relève les enregistrements IPTC-IIM d'un JPEG (APP13 / Photoshop IRB). */
export function extraireIptc(donnees: Uint8Array): EnregistrementIptc[] {
  if (!(donnees[0] === 0xff && donnees[1] === 0xd8)) return [];
  const out: EnregistrementIptc[] = [];
  let pos = 2;
  while (pos + 4 <= donnees.length) {
    if (donnees[pos] !== 0xff) break;
    const marqueur = donnees[pos + 1];
    if (marqueur === 0xd8 || (marqueur >= 0xd0 && marqueur <= 0xd7)) { pos += 2; continue; }
    if (marqueur === 0xd9 || marqueur === 0xda) break;
    const longueur = (donnees[pos + 2] << 8) + donnees[pos + 3];
    const corps = donnees.subarray(pos + 4, pos + 2 + longueur);
    if (marqueur === 0xed && commencePar(corps, ENTETE_PHOTOSHOP)) {
      out.push(...lireIrb(corps.subarray(ENTETE_PHOTOSHOP.length)));
    }
    pos += 2 + longueur;
  }
  return out;
}

// ─────────────────────────────────────────────────────────────────────────────
// Chaînes des en-têtes
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Marqueurs qu'un éditeur laisse derrière lui. La liste ne prétend pas être
 * complète, et une correspondance n'est PAS une preuve de retouche : un
 * convertisseur de format écrit son nom sans rien modifier du contenu visible.
 */
export const MARQUEURS_LOGICIELS = [
  'Adobe', 'Photoshop', 'Lightroom', 'GIMP', 'Paint.NET', 'Affinity',
  'Capture One', 'darktable', 'RawTherapee', 'Luminar', 'Snapseed',
  'PicsArt', 'Canva', 'Pixelmator', 'ImageMagick', 'libvips', 'GraphicsMagick',
  'Google', 'Picasa', 'Instagram', 'Facebook', 'WhatsApp', 'Signal',
  'Midjourney', 'DALL', 'Stable Diffusion', 'Firefly', 'Imagen',
];

export const LONGUEUR_MIN_CHAINE = 6;

export interface ChaineTrouvee {
  offset: number;
  encodage: 'ASCII' | 'UTF-16LE';
  texte: string;
  marqueur: string | null;
}

/**
 * Relève les suites de caractères lisibles dans l'en-tête du fichier.
 *
 * Le balayage s'arrête à `limiteOctets`, et sur un JPEG au SOS : au-delà
 * commencent les données d'image, où toute suite « lisible » est un artefact de
 * compression et non un texte.
 */
export function extraireChaines(
  donnees: Uint8Array, longueurMin = LONGUEUR_MIN_CHAINE, limiteOctets = 262_144,
): ChaineTrouvee[] {
  let fin = Math.min(donnees.length, limiteOctets);
  if (donnees[0] === 0xff && donnees[1] === 0xd8) {
    for (let i = 0; i + 1 < fin; i += 1) {
      if (donnees[i] === 0xff && donnees[i + 1] === 0xda) { fin = i; break; }
    }
  }

  const trouvees: ChaineTrouvee[] = [];
  const vues = new Set<string>();
  const ajouter = (offset: number, encodage: 'ASCII' | 'UTF-16LE', brut: string) => {
    const texte = brut.trim();
    if (texte.length < longueurMin || vues.has(texte)) return;
    vues.add(texte);
    const bas = texte.toLowerCase();
    const marqueur = MARQUEURS_LOGICIELS.find((m) => bas.includes(m.toLowerCase())) ?? null;
    trouvees.push({ offset, encodage, texte, marqueur });
  };

  // ASCII imprimable : 0x20 à 0x7e.
  let debut = -1;
  for (let i = 0; i <= fin; i += 1) {
    const lisible = i < fin && donnees[i] >= 0x20 && donnees[i] <= 0x7e;
    if (lisible && debut === -1) debut = i;
    else if (!lisible && debut !== -1) {
      if (i - debut >= longueurMin) {
        ajouter(debut, 'ASCII', ascii.decode(donnees.subarray(debut, i)));
      }
      debut = -1;
    }
  }

  // UTF-16LE : un octet lisible sur deux, l'autre nul.
  let debut16 = -1;
  let nb = 0;
  // La borne va JUSQU'À `fin` incluse, et non `fin - 1` : c'est l'itération
  // finale, où `paire` est faux, qui vide le tampon. Un premier jet s'arrêtait
  // une itération trop tôt et perdait la dernière chaîne — donc la seule, quand
  // le fichier n'en porte qu'une. Le contrôle d'épinglage l'a signalé.
  for (let i = 0; i <= fin; i += 2) {
    const paire = i + 1 < fin && donnees[i] >= 0x20 && donnees[i] <= 0x7e && donnees[i + 1] === 0;
    if (paire) {
      if (debut16 === -1) { debut16 = i; nb = 0; }
      nb += 1;
    } else if (debut16 !== -1) {
      if (nb >= longueurMin) {
        let texte = '';
        for (let j = debut16; j < debut16 + nb * 2; j += 2) texte += String.fromCharCode(donnees[j]);
        ajouter(debut16, 'UTF-16LE', texte);
      }
      debut16 = -1;
    }
  }

  trouvees.sort((a, b) => a.offset - b.offset);
  return trouvees;
}

// ─────────────────────────────────────────────────────────────────────────────
// Assemblage
// ─────────────────────────────────────────────────────────────────────────────

export interface Provenance {
  c2pa: ResultatC2PA;
  xmp: BlocXmp[];
  iptc: EnregistrementIptc[];
  chaines: ChaineTrouvee[];
  /**
   * Les logiciels relevés. Ce n'est PAS une liste de retouches : un
   * convertisseur écrit son nom sans toucher au contenu visible, et un éditeur
   * peut n'en écrire aucun.
   */
  marqueursLogiciels: string[];
}

/** Tout ce que les en-têtes déclarent, d'un seul appel. Rien n'est vérifié. */
export function analyserProvenance(donnees: Uint8Array): Provenance {
  const chaines = extraireChaines(donnees);
  const marqueurs: string[] = [];
  for (const c of chaines) {
    if (c.marqueur && !marqueurs.includes(c.marqueur)) marqueurs.push(c.marqueur);
  }
  return {
    c2pa: extraireC2pa(donnees),
    xmp: extraireXmp(donnees),
    iptc: extraireIptc(donnees),
    chaines,
    marqueursLogiciels: marqueurs,
  };
}
