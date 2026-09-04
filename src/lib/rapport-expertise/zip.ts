/**
 * zip.ts — Écriture d'une archive ZIP sans compression, sans dépendance.
 *
 * Pourquoi sans compression : l'archive du §34 sert à être vérifiée. Une
 * entrée stockée telle quelle a la même empreinte dans l'archive et hors
 * d'elle, ce qui permet de contrôler un SHA256SUMS sans passer par un
 * décompresseur. Le gain de place n'a aucun intérêt ici ; la vérifiabilité,
 * si.
 *
 * Pourquoi sans dépendance : ajouter une bibliothèque de compression au site
 * pour écrire des en-têtes de cent octets serait disproportionné, et le format
 * ZIP en mode « store » tient en une page. Le CRC-32 est celui de la norme,
 * table calculée au premier appel.
 *
 * Ce module n'est pas un port du Python : le paquet `rapport_expertise` écrit
 * une vraie arborescence sur un système de fichiers, ce qu'un navigateur ne
 * peut pas faire. Le ZIP est l'équivalent transportable de cette arborescence,
 * et la différence est dite à l'utilisateur plutôt que masquée.
 */

let tableCrc: Uint32Array | null = null;

function table(): Uint32Array {
  if (tableCrc) return tableCrc;
  const t = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[i] = c >>> 0;
  }
  tableCrc = t;
  return t;
}

export function crc32(octets: Uint8Array): number {
  const t = table();
  let c = 0xffffffff;
  for (let i = 0; i < octets.length; i++) c = t[(c ^ octets[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

export interface EntreeZip {
  /** Chemin dans l'archive, séparé par des barres obliques. */
  chemin: string;
  /** Contenu. Absent pour un répertoire. */
  contenu?: Uint8Array;
}

/** Date et heure au format DOS, tel que le ZIP les attend. */
function dateDos(d: Date): { heure: number; date: number } {
  return {
    heure: ((d.getHours() & 0x1f) << 11) | ((d.getMinutes() & 0x3f) << 5) | ((d.getSeconds() / 2) & 0x1f),
    date: (((d.getFullYear() - 1980) & 0x7f) << 9) | (((d.getMonth() + 1) & 0x0f) << 5) | (d.getDate() & 0x1f),
  };
}

const encodeur = new TextEncoder();

/**
 * Assemble une archive ZIP en mode « store ».
 *
 * Un chemin terminé par « / » est un répertoire : entrée de taille nulle, avec
 * le bit de répertoire dans les attributs externes, de façon que les
 * répertoires imposés du §34 existent dans l'archive même quand ils sont
 * vides — c'est l'ordre de lecture qui compte, pas leur contenu initial.
 */
export function construireZip(entrees: EntreeZip[], quand: Date = new Date()): Uint8Array {
  const { heure, date } = dateDos(quand);
  const locaux: Uint8Array[] = [];
  const centraux: Uint8Array[] = [];
  let offset = 0;

  for (const e of entrees) {
    const estDossier = e.chemin.endsWith('/');
    const nom = encodeur.encode(e.chemin);
    const contenu = estDossier ? new Uint8Array(0) : (e.contenu ?? new Uint8Array(0));
    const somme = estDossier ? 0 : crc32(contenu);

    const local = new Uint8Array(30 + nom.length);
    const vl = new DataView(local.buffer);
    vl.setUint32(0, 0x04034b50, true);
    vl.setUint16(4, 20, true);          // version minimale
    vl.setUint16(6, 0x0800, true);      // nom de fichier en UTF-8
    vl.setUint16(8, 0, true);           // stocké, pas compressé
    vl.setUint16(10, heure, true);
    vl.setUint16(12, date, true);
    vl.setUint32(14, somme, true);
    vl.setUint32(18, contenu.length, true);
    vl.setUint32(22, contenu.length, true);
    vl.setUint16(26, nom.length, true);
    vl.setUint16(28, 0, true);
    local.set(nom, 30);
    locaux.push(local, contenu);

    const central = new Uint8Array(46 + nom.length);
    const vc = new DataView(central.buffer);
    vc.setUint32(0, 0x02014b50, true);
    vc.setUint16(4, 20, true);
    vc.setUint16(6, 20, true);
    vc.setUint16(8, 0x0800, true);
    vc.setUint16(10, 0, true);
    vc.setUint16(12, heure, true);
    vc.setUint16(14, date, true);
    vc.setUint32(16, somme, true);
    vc.setUint32(20, contenu.length, true);
    vc.setUint32(24, contenu.length, true);
    vc.setUint16(28, nom.length, true);
    vc.setUint16(30, 0, true);
    vc.setUint16(32, 0, true);
    vc.setUint16(34, 0, true);
    vc.setUint16(36, 0, true);
    // Droits Unix dans les seize bits hauts : 0755 pour un répertoire, 0644
    // pour un fichier ; le bit 0x10 marque le répertoire pour les outils DOS.
    vc.setUint32(38, estDossier ? (0o40755 << 16) | 0x10 : 0o100644 << 16, true);
    vc.setUint32(42, offset, true);
    central.set(nom, 46);
    centraux.push(central);

    offset += local.length + contenu.length;
  }

  const tailleCentral = centraux.reduce((s, c) => s + c.length, 0);
  const fin = new Uint8Array(22);
  const vf = new DataView(fin.buffer);
  vf.setUint32(0, 0x06054b50, true);
  vf.setUint16(4, 0, true);
  vf.setUint16(6, 0, true);
  vf.setUint16(8, entrees.length, true);
  vf.setUint16(10, entrees.length, true);
  vf.setUint32(12, tailleCentral, true);
  vf.setUint32(16, offset, true);
  vf.setUint16(20, 0, true);

  const morceaux = [...locaux, ...centraux, fin];
  const total = morceaux.reduce((s, m) => s + m.length, 0);
  const sortie = new Uint8Array(total);
  let p = 0;
  for (const m of morceaux) {
    sortie.set(m, p);
    p += m.length;
  }
  return sortie;
}

export function texte(s: string): Uint8Array {
  return encodeur.encode(s);
}
