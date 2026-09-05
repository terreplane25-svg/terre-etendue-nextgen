/**
 * document.ts — Port TypeScript de `preuve_image.document` (outil B).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-B-preuve-image/preuve_image/document.py`. Ce
 * port est épinglé au Python par les vecteurs de `vecteurs-or-provenance.json`,
 * que `scripts/verifier-port-provenance.mjs` rejoue ici.
 *
 * QUATRE ÉCARTS AU SCHÉMA DEMANDÉ, ET POURQUOI
 * ────────────────────────────────────────────
 * Le schéma est suivi champ pour champ. Quatre points ne pouvaient pas l'être
 * sans écrire des choses fausses ; dans les quatre cas, la clé demandée existe
 * et une clé voisine porte ce qui manquait.
 *
 * 1. L'horodatage ne porte un fuseau que si l'appareil a écrit
 *    `OffsetTimeOriginal`. Sinon la valeur est une heure locale nue et
 *    `offset_declare` vaut faux : accoler « +02:00 » par défaut inventerait une
 *    information, et sur une observation horodatée cette invention déciderait
 *    d'un résultat.
 * 2. `dpi` est un scalaire ; il n'est rempli que si les deux axes coïncident,
 *    `dpi_x` / `dpi_y` restant toujours là.
 * 3. `camera` concatène Make et Model, ce qui ne se défait pas : `make` et
 *    `model` restent séparément disponibles.
 * 4. `c2pa.signature` porte l'identité DÉCLARÉE du signataire, jamais un
 *    verdict : `verified: false` et son motif l'accompagnent toujours.
 */

import {
  LIBELLE_COLOR_SPACE,
  LIBELLE_EXPOSURE_MODE,
  LIBELLE_EXPOSURE_PROGRAM,
  LIBELLE_RESOLUTION_UNIT,
  LIBELLE_SCENE_CAPTURE,
  LIBELLE_WHITE_BALANCE,
  decrireFlash,
  empreinteSha256,
  lireExifDepuisJpeg,
  zoomNumeriqueApplique,
  type DonneesExif,
} from './noyau';
import { AVERTISSEMENT_C2PA, analyserProvenance, type Provenance } from './provenance';

export const MOTIF_SIGNATURE_NON_VERIFIEE =
  "Aucune signature n'est vérifiée : ni la validation COSE, ni la chaîne X.509, "
  + "ni les empreintes de liaison au contenu. La valeur du champ « signature » est "
  + "l'identité que le manifeste DÉCLARE, pas une identité établie.";

/**
 * Marqueurs SOF d'un JPEG. DHT (0xC4), JPG (0xC8) et DAC (0xCC) tombent dans la
 * même plage sans être des en-têtes de trame : ils sont exclus.
 */
function estSof(marqueur: number): boolean {
  return marqueur >= 0xc0 && marqueur < 0xd0
    && marqueur !== 0xc4 && marqueur !== 0xc8 && marqueur !== 0xcc;
}

/** Dimensions d'un JPEG, lues dans son marqueur SOF — sans le décoder. */
export function dimensionsJpeg(donnees: Uint8Array): [number, number] | null {
  if (donnees.length < 4 || donnees[0] !== 0xff || donnees[1] !== 0xd8) return null;
  let pos = 2;
  while (pos + 4 <= donnees.length) {
    if (donnees[pos] !== 0xff) return null;
    const marqueur = donnees[pos + 1];
    if (marqueur === 0xd8 || (marqueur >= 0xd0 && marqueur <= 0xd7)) { pos += 2; continue; }
    if (marqueur === 0xd9 || marqueur === 0xda) return null;
    const longueur = (donnees[pos + 2] << 8) + donnees[pos + 3];
    if (estSof(marqueur)) {
      if (pos + 9 > donnees.length) return null;
      const hauteur = (donnees[pos + 5] << 8) + donnees[pos + 6];
      const largeur = (donnees[pos + 7] << 8) + donnees[pos + 8];
      return [largeur, hauteur];
    }
    pos += 2 + longueur;
  }
  return null;
}

export interface Horodatage {
  valeur: string | null;
  offset_declare: boolean;
  brut: string | null;
}

/** « AAAA:MM:JJ HH:MM:SS » en ISO 8601, sans jamais inventer de fuseau. */
export function horodatageIso(exifDatetime: string | null, decalage: string | null): Horodatage {
  if (!exifDatetime) return { valeur: null, offset_declare: false, brut: null };
  const brut = exifDatetime.trim();
  const partie = brut.replace(':', '-').replace(':', '-').replace(' ', 'T');
  if (decalage && decalage.trim()) {
    return { valeur: partie + decalage.trim(), offset_declare: true, brut };
  }
  return { valeur: partie, offset_declare: false, brut };
}

/**
 * « 1/200 » sous la seconde, « 2,5 s » au-delà. Forme d'affichage seulement :
 * le nombre exact reste à côté dans `shutter_speed_s`, car une fraction
 * arrondie ne se recalcule pas.
 */
export function vitesseObturation(secondes: number | null): string | null {
  if (secondes === null || secondes <= 0) return null;
  if (secondes >= 1) {
    // `%g` côté Python : au plus six chiffres significatifs, sans zéro inutile.
    const t = Number(secondes.toPrecision(6));
    return `${String(t).replace('.', ',')} s`;
  }
  return `1/${Math.round(1 / secondes)}`;
}

function codeEtLibelle(code: number | null, table: Record<number, string>) {
  return { code, libelle: code === null ? null : table[code] ?? null };
}

function camera(e: DonneesExif): string | null {
  const morceaux = [e.fabricant, e.modele].filter((m): m is string => !!m && m.trim() !== '')
    .map((m) => m.trim());
  return morceaux.length > 0 ? morceaux.join(' ') : null;
}

function blocC2pa(prov: Provenance) {
  const c = prov.c2pa;
  const actions: string[] = [];
  const signataires: string[] = [];
  for (const m of c.manifestes) {
    for (const a of m.actions) {
      const nom = a.action;
      if (typeof nom === 'string' && !actions.includes(nom)) actions.push(nom);
    }
    if (m.generateur && !signataires.includes(m.generateur)) signataires.push(m.generateur);
  }
  return {
    present: c.present,
    actions,
    // Identité DÉCLARÉE du signataire, jamais une identité établie.
    signature: signataires.length > 0 ? signataires[0] : null,
    verified: false as const,
    motif: MOTIF_SIGNATURE_NON_VERIFIEE,
    avertissement: AVERTISSEMENT_C2PA,
    conteneur: c.conteneur,
    octets: c.octets,
    manifestes: c.manifestes.map((m) => ({
      label: m.label,
      generateur_declare: m.generateur,
      algorithme_declare: m.algorithmeSignature,
      bloc_signature_present: m.signaturePresente,
      assertions: Object.keys(m.assertions).sort(),
      actions: m.actions,
    })),
  };
}

async function blocThumbnail(e: DonneesExif | null) {
  const m = e?.miniature ?? null;
  if (m === null) return { present: false, dimensions: null };
  const dims = m.estJpeg ? dimensionsJpeg(m.octets) : null;
  return {
    present: true,
    dimensions: dims,
    octets: m.longueur,
    offset: m.offset,
    format: m.estJpeg ? 'JPEG' : 'non reconnu',
    sha256: await empreinteSha256(m.octets),
    ce_que_ca_n_etablit_pas:
      "Une miniature qui concorde avec l'image n'établit rien : tout éditeur "
      + "qui la régénère efface la trace. Seul un ÉCART entre elle et l'image "
      + 'principale est un fait.',
  };
}

/** Tout ce que le fichier déclare, dans la forme convenue. Rien n'est vérifié. */
export async function documentIngestion(
  donnees: Uint8Array, nomFichier: string | null = null,
): Promise<Record<string, unknown>> {
  let exif: DonneesExif | null = null;
  let motifExif: string | null = null;
  try {
    exif = lireExifDepuisJpeg(donnees);
  } catch (err) {
    motifExif = err instanceof Error ? err.message : String(err);
  }

  const prov = analyserProvenance(donnees);

  let largeur = exif ? (exif.largeurPx ?? exif.largeurIfd0Px) : null;
  let hauteur = exif ? (exif.hauteurPx ?? exif.hauteurIfd0Px) : null;
  if (largeur === null || hauteur === null) {
    const dims = dimensionsJpeg(donnees);
    if (dims) { [largeur, hauteur] = dims; }
  }

  let dpiCommun: number | null = null;
  if (exif && exif.dpiX !== null && exif.dpiY !== null && Math.abs(exif.dpiX - exif.dpiY) < 1e-9) {
    dpiCommun = exif.dpiX;
  }

  const doc: Record<string, unknown> = {
    outil: 'preuve-image (outil B) — ingestion',
    protocole: "Portion visible d'une cible éloignée au-dessus de la mer v1.0",
    fichier: nomFichier,
    sha256: await empreinteSha256(donnees),
    octets: donnees.length,
    file_info: {
      dimensions: largeur && hauteur ? [largeur, hauteur] : null,
      color_space: exif && exif.espaceColorimetrique !== null
        ? LIBELLE_COLOR_SPACE[exif.espaceColorimetrique] ?? null : null,
      color_space_code: exif ? exif.espaceColorimetrique : null,
      // Scalaire seulement quand les deux axes coïncident : sinon une valeur
      // unique masquerait une anisotropie réelle.
      dpi: dpiCommun,
      dpi_x: exif ? exif.dpiX : null,
      dpi_y: exif ? exif.dpiY : null,
      resolution_unit: codeEtLibelle(exif ? exif.uniteResolution : null, LIBELLE_RESOLUTION_UNIT),
    },
    exif: null,
    c2pa: blocC2pa(prov),
    thumbnail: await blocThumbnail(exif),
    xmp: prov.xmp.map((b) => ({
      conteneur: b.conteneur, octets: b.octets, etendu: b.etendu, champs: b.champs,
    })),
    iptc: prov.iptc.map((e) => ({
      jeu: e.jeu, numero: e.numero, libelle: e.libelle, valeur: e.valeur,
    })),
    chaines: {
      nombre: prov.chaines.length,
      marqueurs_logiciels: prov.marqueursLogiciels,
      ce_que_ca_n_etablit_pas:
        "Un marqueur logiciel n'établit pas qu'il y a eu retouche — un "
        + 'convertisseur de format écrit son nom sans toucher au contenu '
        + "visible — et son absence n'établit pas le contraire.",
    },
  };

  if (exif === null) {
    doc.exif = { lu: false, motif: motifExif };
    return doc;
  }

  doc.exif = {
    lu: true,
    camera: camera(exif),
    make: exif.fabricant,
    model: exif.modele,
    software: exif.logiciel,
    lens: exif.objectif,
    artist: exif.artiste,
    copyright: exif.droits,
    orientation: exif.orientation,
    settings: {
      iso: exif.sensibiliteIso,
      f_number: exif.ouverture,
      shutter_speed: vitesseObturation(exif.tempsPoseS),
      // Le nombre exact : une fraction arrondie ne se recalcule pas.
      shutter_speed_s: exif.tempsPoseS,
      focal_length_mm: exif.focaleMm,
      focal_length_35mm: exif.focaleEquivalente35mm,
      digital_zoom_ratio: exif.rapportZoomNumerique,
      digital_zoom_applied: zoomNumeriqueApplique(exif),
      flash: { code: exif.flash, libelle: decrireFlash(exif.flash) },
      exposure_mode: codeEtLibelle(exif.modeExposition, LIBELLE_EXPOSURE_MODE),
      exposure_program: codeEtLibelle(exif.programmeExposition, LIBELLE_EXPOSURE_PROGRAM),
      white_balance: codeEtLibelle(exif.balanceBlancs, LIBELLE_WHITE_BALANCE),
      scene_capture_type: codeEtLibelle(exif.typeScene, LIBELLE_SCENE_CAPTURE),
    },
    dates: {
      original: horodatageIso(exif.dateHeureOriginal, exif.decalageHoraireOriginal),
      digitized: horodatageIso(exif.dateHeureNumerisation, exif.decalageHoraireNumerisation),
      modified: horodatageIso(exif.dateHeureModification, exif.decalageHoraire),
      ce_que_ca_n_etablit_pas:
        "Un horodatage EXIF est réglé par l'appareil et se modifie avec un "
        + 'éditeur de texte : il documente une déclaration, il ne date pas la '
        + 'prise de vue. Quand `offset_declare` est faux, l\'heure est locale et '
        + "son fuseau est INCONNU — il n'est pas supposé.",
    },
    gps: exif.gps === null ? null : {
      latitude: exif.gps.latitudeDeg,
      longitude: exif.gps.longitudeDeg,
      altitude_m: exif.gps.altitudeM,
      // Presque aucun boîtier n'écrit GPSHPositioningError. L'absence est
      // rendue telle quelle : le §15.4 interdit de la combler.
      incertitude_m: exif.gps.incertitudeM,
      source: exif.gps.source,
    },
  };
  return doc;
}
