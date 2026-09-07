/**
 * dossier.ts — Port TypeScript de `preuve_image.dossier` (outil B).
 *
 * CE FICHIER N’EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-B-preuve-image/preuve_image/dossier.py`. Ce
 * port est épinglé au Python par `vecteurs-or-dossier.json`, que
 * `scripts/verifier-port-dossier.mjs` rejoue ici.
 *
 * CE QUE CE MODULE FAIT
 * ─────────────────────
 * Il n’extrait rien lui-même. Il ORCHESTRE les six lecteurs du paquet — EXIF,
 * conteneurs à boîtes, conteneurs hors EXIF, provenance, quantification,
 * télémétrie — et range ce qu’ils rendent dans une structure unique, la même
 * quel que soit le format d’entrée.
 *
 * LE DÉFAUT PROPRE À UN RELEVÉ UNIFIÉ
 * ───────────────────────────────────
 * Il présente côte à côte des champs qui ne s’établissent pas de la même
 * façon : une marque LUE, un numéro de série LU, un type de matériel DÉDUIT,
 * une correspondance d’écran qui N’EXISTE PAS. Dans un JSON, les quatre ont
 * exactement la même apparence.
 *
 * Trois dispositions l’en empêchent : chaque bloc porte un `detection_method`
 * qui dit d’où vient l’information ; un champ qu’on ne peut pas renseigner
 * vaut null ET porte son motif ; les déductions portent la RÈGLE qui les a
 * produites, pour qu’on puisse les contester sans relire le code.
 *
 * Rien ici n’est vérifié. Une métadonnée s’écrit ; ce module l’affiche.
 */

import { inventorier, type InventaireConteneur } from './conteneurs';
import { analyserIsobmff, type StructureIsobmff } from './isobmff';
import {
  type DonneesExif,
  decrireFlash,
  detecterConteneur,
  empreinteSha256,
  lireExif,
} from './noyau';
import {
  type EvenementXmp,
  type Provenance,
  analyserProvenance,
  extraireHistoriqueXmp,
} from './provenance';
import {
  MOTIF_AUCUNE_SIGNATURE,
  type AnalyseQuantification,
  analyserQuantification,
} from './quantification';
import { type TelemetrieVol, extraireTelemetrie, viseeHorizontale } from './telemetrie';

/**
 * Le type MIME de chaque conteneur reconnu. Il est DÉDUIT DES OCTETS, jamais du
 * nom du fichier : une extension se renomme, et c’est le premier geste de qui
 * veut faire passer une image pour une autre.
 */
export const TYPES_MIME: Record<string, string> = {
  JPEG: 'image/jpeg',
  PNG: 'image/png',
  HEIC: 'image/heic',
  AVIF: 'image/avif',
  CR3: 'image/x-canon-cr3',
  'TIFF/RAW': 'image/tiff',
  RAF: 'image/x-fuji-raf',
  WebP: 'image/webp',
  GIF: 'image/gif',
  BMP: 'image/bmp',
  SVG: 'image/svg+xml',
};

/** La famille structurelle du conteneur — comment le fichier est bâti. */
export const FAMILLES: Record<string, string> = {
  JPEG: 'JFIF/EXIF (segments APP)',
  PNG: 'PNG (chunks)',
  HEIC: 'HEIF/ISOBMFF (boîtes)',
  AVIF: 'AVIF/ISOBMFF (boîtes)',
  CR3: 'CR3/ISOBMFF (boîtes)',
  'TIFF/RAW': 'TIFF (IFD)',
  RAF: 'RAF Fujifilm (JPEG embarqué)',
  WebP: 'RIFF (morceaux)',
  GIF: 'GIF (blocs et extensions)',
  BMP: 'BMP (en-têtes DIB)',
  SVG: 'SVG (XML)',
};

export const MOTIF_NUMERO_SERIE_ABSENT =
  'Aucun numéro de série dans les tags EXIF standard (BodySerialNumber, '
  + "LensSerialNumber). Beaucoup d’appareils n’en écrivent pas, et les "
  + "téléphones n’en écrivent jamais dans ces champs-là. Certains boîtiers le "
  + 'rangent dans leurs MakerNotes propriétaires, que ce paquet ne décode pas.';

export const MOTIF_DECLENCHEMENTS_ABSENT =
  "Le décompte des déclenchements n’existe dans AUCUN tag EXIF standard. Il "
  + "n’est écrit que dans les MakerNotes propriétaires, différemment par chaque "
  + 'constructeur et souvent par chaque millésime. Ce paquet rend les '
  + 'MakerNotes bruts sans les décoder : les interpréter demanderait un '
  + "dictionnaire par appareil, qu’on ne peut pas écrire de mémoire sans se "
  + 'tromper.';

export const MOTIF_ECRAN_NON_EVALUE =
  'Aucun rapprochement par la résolution : il n’existe pas de référentiel '
  + 'vérifié des définitions d’écrans dans ce dépôt. En écrire un de mémoire '
  + 'produirait des correspondances fausses présentées comme des faits. Et le '
  + 'signal serait faible même vérifié : une résolution de 1179 × 2556 '
  + 'identifie une capture d’écran d’iPhone 15 Pro autant que n’importe quelle '
  + 'image recadrée à ces dimensions.';

/**
 * Une conclusion tirée, avec la règle qui l’a produite.
 *
 * Une déduction n’a pas le même statut qu’une lecture, et les présenter de la
 * même façon serait le défaut principal d’un relevé unifié. `regle` permet de
 * la contester sans relire le code.
 */
export interface Deduction {
  valeur: string;
  regle: string;
}

export interface DossierFichier {
  file_analysis: Record<string, unknown>;
  device_identification: Record<string, unknown>;
  capture_settings: Record<string, unknown>;
  telemetry_and_location: Record<string, unknown>;
  provenance_and_software: Record<string, unknown>;
  deep_fingerprint: Record<string, unknown>;
  /**
   * Ce qui a échoué, et pourquoi. Un lecteur en échec n’est jamais tu :
   * l’absence d’un bloc et l’échec de sa lecture ne s’établissent pas de la
   * même façon, et les confondre ferait passer une panne pour un constat.
   */
  lectures_en_echec: { lecteur: string; motif: string }[];
  avertissements: string[];
}

/**
 * Le type de matériel, DÉDUIT — jamais lu, parce qu’aucun format ne l’écrit.
 *
 * Les règles sont peu nombreuses et volontairement conservatrices : chacune
 * s’appuie sur une trace non ambiguë, et l’absence de règle applicable rend
 * null plutôt qu’une supposition. Un « appareil photo » deviné à partir d’un
 * fabricant vaudrait moins que rien.
 */
export function deduireTypeMateriel(
  exif: DonneesExif | null,
  telemetrie: TelemetrieVol | null,
  conteneur: string,
): Deduction | null {
  if (telemetrie !== null && telemetrie.present) {
    return {
      valeur: 'aéronef sans équipage',
      regle: `le fichier porte de la télémétrie de vol (${telemetrie.prefixes.join(', ')})`,
    };
  }
  if (exif === null) return null;
  const modele = (exif.modele ?? '').toLowerCase();
  const fabricant = (exif.fabricant ?? '').toLowerCase();
  // Le nom d’objectif que les téléphones écrivent contient « back camera » ou
  // « front camera » : trace non ambiguë, écrite par le système et non par
  // l’utilisateur.
  const objectif = (exif.objectif ?? '').toLowerCase();
  if (objectif.includes('back camera') || objectif.includes('front camera')
    || objectif.includes('back triple camera')) {
    return { valeur: 'téléphone', regle: "le nom d’objectif déclare une caméra avant ou arrière" };
  }
  // Numéro de série de boîtier ET d’objectif : signature d’un reflex ou d’un
  // hybride. Aucun téléphone n’écrit les deux.
  if (exif.numeroSerieBoitier && exif.numeroSerieObjectif) {
    return {
      valeur: 'appareil à objectifs interchangeables',
      regle: "numéros de série de boîtier ET d’objectif tous deux présents",
    };
  }
  if (['CR3', 'TIFF/RAW', 'RAF'].includes(conteneur)) {
    return {
      valeur: 'appareil photo dédié',
      regle: `le fichier est un format brut de constructeur (${conteneur})`,
    };
  }
  if (modele.includes('scanner') || fabricant.includes('scan')) {
    return { valeur: 'scanner', regle: 'le modèle ou le fabricant déclaré contient « scan »' };
  }
  return null;
}

/** « 1/200 » sous la seconde, « 2,5 s » au-delà. Forme d’affichage seulement. */
function vitesse(secondes: number | null): string | null {
  if (secondes === null || secondes <= 0) return null;
  // `%g` côté Python : au plus six chiffres significatifs, sans zéro inutile.
  if (secondes >= 1) return `${Number(secondes.toPrecision(6))} s`;
  return `1/${Math.round(1 / secondes)}`;
}

const FAMILLES_EXT: Record<string, string> = {
  '.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG', '.gif': 'GIF',
  '.bmp': 'BMP', '.webp': 'WebP', '.svg': 'SVG', '.heic': 'HEIC',
  '.heif': 'HEIC', '.avif': 'AVIF', '.cr3': 'CR3', '.raf': 'RAF',
};

function extension(nom: string | null): string | null {
  if (!nom) return null;
  const i = nom.lastIndexOf('.');
  return i > 0 ? nom.slice(i).toLowerCase() : null;
}

/**
 * D’où vient l’identification du matériel, en toutes lettres.
 *
 * Sans ce champ, un relevé rendrait « Apple / iPhone 15 Pro » sans dire si
 * l’information vient d’un tag EXIF, d’un nom de fichier ou d’une déduction —
 * et les trois n’ont pas le même poids.
 */
function methodeDetection(
  exif: DonneesExif | null, structure: StructureIsobmff | null, conteneur: string,
): string {
  const voies: string[] = [];
  if (exif !== null && (exif.fabricant || exif.modele)) {
    voies.push('tags EXIF standard (Make, Model)');
  }
  if (exif !== null && (exif.numeroSerieBoitier || exif.numeroSerieObjectif)) {
    voies.push('numéros de série EXIF (BodySerialNumber, LensSerialNumber)');
  }
  if (structure !== null && structure.makernotes) {
    voies.push(`MakerNotes présents (${structure.makernotes.length} octets) mais NON DÉCODÉS`);
  }
  if (voies.length === 0) return "aucune : rien dans ce fichier ne nomme d’appareil";
  return `${voies.join(' ; ')} — conteneur ${conteneur}`;
}

/**
 * Les images embarquées, de la plus grande à la plus petite.
 *
 * Elles n’ont pas nécessairement été écrites au même moment du traitement, et
 * c’est leur comparaison qui a valeur d’indice — d’où le fait de toutes les
 * lister plutôt que de n’en montrer qu’une.
 */
async function apercus(
  exif: DonneesExif | null, structure: StructureIsobmff | null,
): Promise<Record<string, unknown>[]> {
  const out: Record<string, unknown>[] = [];
  const vus = new Set<string>();
  if (exif !== null) {
    for (const m of exif.previsualisations) {
      const cle = await empreinteSha256(m.octets);
      if (vus.has(cle)) continue;
      vus.add(cle);
      out.push({
        origine: m.origine, octets: m.longueur,
        format: m.estJpeg ? 'JPEG' : 'non reconnu', sha256: cle,
      });
    }
  }
  if (structure !== null) {
    for (const { origine, octets } of structure.apercus) {
      const cle = await empreinteSha256(octets);
      if (vus.has(cle)) continue;
      vus.add(cle);
      out.push({
        origine, octets: octets.length,
        format: octets[0] === 0xff && octets[1] === 0xd8 ? 'JPEG' : 'non reconnu',
        sha256: cle,
      });
    }
  }
  return out.sort((a, b) => (b.octets as number) - (a.octets as number));
}

/**
 * Assemble le relevé unifié d’un fichier, quel que soit son format.
 *
 * Aucun lecteur en échec n’interrompt les autres : un JPEG dont l’EXIF a été
 * purgé garde ses tables de quantification, et un PNG sans texte garde son
 * profil ICC. Chaque échec est consigné avec son motif.
 */
export async function constituerDossier(
  donnees: Uint8Array, nomFichier: string | null = null,
): Promise<DossierFichier> {
  const d: DossierFichier = {
    file_analysis: {}, device_identification: {}, capture_settings: {},
    telemetry_and_location: {}, provenance_and_software: {}, deep_fingerprint: {},
    lectures_en_echec: [], avertissements: [],
  };
  const conteneur = detecterConteneur(donnees);
  const ext = extension(nomFichier);

  d.file_analysis = {
    filename: nomFichier,
    // Le type MIME vient des OCTETS, pas de l’extension. L’extension déclarée
    // est rendue à côté, pour que l’écart se voie.
    mime_type: TYPES_MIME[conteneur] ?? null,
    mime_source: "octets du fichier, jamais l’extension",
    extension_declaree: ext,
    file_size_bytes: donnees.length,
    format_family: FAMILLES[conteneur] ?? conteneur,
    conteneur,
    sha256: await empreinteSha256(donnees),
  };
  if (ext && TYPES_MIME[conteneur]) {
    // On ne dresse pas de table extension → MIME complète : elle ferait de
    // faux positifs. On signale seulement le cas franc.
    const annonce = FAMILLES_EXT[ext];
    if (annonce !== undefined && annonce !== conteneur) {
      d.avertissements.push(
        `L’extension « ${ext} » annonce un ${annonce}, les octets disent ${conteneur}. `
        + "Ce n’est pas une preuve de manipulation — un fichier se renomme par mégarde — "
        + 'mais c’est un écart, et il est relevé.',
      );
    }
  }

  let exif: DonneesExif | null = null;
  try {
    exif = lireExif(donnees);
  } catch (err) {
    d.lectures_en_echec.push({
      lecteur: 'EXIF', motif: err instanceof Error ? err.message : String(err),
    });
  }

  let structure: StructureIsobmff | null = null;
  let inventaire: InventaireConteneur | null = null;
  if (['HEIC', 'AVIF', 'CR3'].includes(conteneur) || conteneur.startsWith('ISO BMFF')) {
    try {
      structure = analyserIsobmff(donnees);
    } catch (err) {
      d.lectures_en_echec.push({
        lecteur: 'ISOBMFF', motif: err instanceof Error ? err.message : String(err),
      });
    }
  } else {
    try {
      inventaire = await inventorier(donnees);
    } catch {
      // Un JPEG ou un TIFF n’a rien à faire ici : ce n’est pas un échec, c’est
      // un partage de responsabilité entre lecteurs. On ne le consigne donc pas
      // comme une panne.
      inventaire = null;
    }
  }

  let provenance: Provenance | null = null;
  try {
    provenance = analyserProvenance(donnees);
  } catch (err) {
    d.lectures_en_echec.push({
      lecteur: 'provenance', motif: err instanceof Error ? err.message : String(err),
    });
  }

  // Les paquets XMP viennent de trois endroits selon le format. Les réunir ici
  // évite à chaque appelant de savoir lequel interroger.
  const encodeur = new TextEncoder();
  const paquetsXmp: Uint8Array[] = [];
  if (provenance !== null) for (const b of provenance.xmp) paquetsXmp.push(encodeur.encode(b.brut));
  if (structure !== null) paquetsXmp.push(...structure.paquetsXmp);
  if (inventaire !== null) paquetsXmp.push(...inventaire.paquetsXmp);

  const telemetrie = extraireTelemetrie(paquetsXmp);
  const decodeur = new TextDecoder('utf-8');
  const historique: EvenementXmp[] = [];
  for (const p of paquetsXmp) historique.push(...extraireHistoriqueXmp(decodeur.decode(p)));

  const deduction = deduireTypeMateriel(exif, telemetrie, conteneur);
  const aUnNumero = Boolean(exif && (exif.numeroSerieBoitier || exif.numeroSerieObjectif));
  d.device_identification = {
    make: exif?.fabricant ?? null,
    model: exif?.modele ?? null,
    hardware_type: deduction ? deduction.valeur : null,
    hardware_type_regle: deduction ? deduction.regle : null,
    hardware_type_statut: deduction ? 'déduit, non lu' : 'indéterminé',
    serial_number: exif?.numeroSerieBoitier ?? null,
    lens_serial_number: exif?.numeroSerieObjectif ?? null,
    lens_model: exif?.objectif ?? null,
    lens_make: exif?.fabricantObjectif ?? null,
    owner_declared: exif?.proprietaireDeclare ?? null,
    detection_method: methodeDetection(exif, structure, conteneur),
    motif_serial_number: aUnNumero ? null : MOTIF_NUMERO_SERIE_ABSENT,
    ce_que_ca_n_etablit_pas:
      'Un numéro de série rattache le cliché à un appareil DÉCLARÉ, pas à un '
      + "appareil établi : une métadonnée s’écrit et se modifie (§17.1). Il sert "
      + 'à confronter deux fichiers entre eux, pas à prouver une origine.',
  };

  d.capture_settings = {
    iso: exif?.sensibiliteIso ?? null,
    focal_length_mm: exif?.focaleMm ?? null,
    focal_length_35mm: exif?.focaleEquivalente35mm ?? null,
    exposure_time: vitesse(exif?.tempsPoseS ?? null),
    exposure_time_s: exif?.tempsPoseS ?? null,
    f_number: exif?.ouverture ?? null,
    flash: exif ? decrireFlash(exif.flash) : null,
    flash_code: exif?.flash ?? null,
    lens_specification: exif?.specificationObjectif ?? null,
    // Le décompte des déclenchements n’est dans AUCUN tag standard.
    shutter_count: null,
    motif_shutter_count: MOTIF_DECLENCHEMENTS_ABSENT,
    dimensions: exif && exif.largeurPx && exif.hauteurPx
      ? [exif.largeurPx, exif.hauteurPx]
      : (inventaire && inventaire.largeur ? [inventaire.largeur, inventaire.hauteur] : null),
  };

  const gps = exif?.gps ?? null;
  d.telemetry_and_location = {
    gps: gps === null ? null : {
      latitude: gps.latitudeDeg,
      longitude: gps.longitudeDeg,
      altitude_meters: gps.altitudeM,
      uncertainty_meters: gps.incertitudeM,
      source: gps.source,
    },
    drone_telemetry: !telemetrie.present ? null : {
      origine: telemetrie.origine,
      prefixes: telemetrie.prefixes,
      latitude: telemetrie.latitudeDeg,
      longitude: telemetrie.longitudeDeg,
      absolute_altitude_m: telemetrie.altitudeAbsolueM,
      relative_altitude_m: telemetrie.altitudeRelativeM,
      above_ground_altitude_m: telemetrie.altitudeSolM,
      gimbal_pitch_deg: telemetrie.tangageNacelleDeg,
      gimbal_yaw_deg: telemetrie.lacetNacelleDeg,
      gimbal_roll_deg: telemetrie.roulisNacelleDeg,
      visee_horizontale: viseeHorizontale(telemetrie),
      ground_station: null,
      motif_ground_station: telemetrie.motifStationSol,
      avertissement_altitude: telemetrie.avertissementAltitude,
    },
    ce_que_ca_n_etablit_pas:
      'Une position GPS est ce que le récepteur a DÉCLARÉ au moment de '
      + "l’écriture. Elle ne prouve pas où le cliché a été pris : le champ "
      + "s’écrit, et un récepteur dérive, se trompe ou perd sa constellation.",
  };

  d.provenance_and_software = {
    software: exif?.logiciel ?? null,
    creation_date: exif?.dateHeureOriginal ?? null,
    creation_date_offset: exif?.decalageHoraireOriginal ?? null,
    modification_date: exif?.dateHeureModification ?? null,
    digitized_date: exif?.dateHeureNumerisation ?? null,
    artist: exif?.artiste ?? null,
    copyright: exif?.droits ?? null,
    c2pa_credentials: Boolean(provenance && provenance.c2pa.present),
    c2pa_verified: false,
    motif_c2pa_non_verifie:
      "Aucune signature n’est vérifiée : ni la validation COSE, ni la chaîne "
      + 'X.509, ni les empreintes de liaison au contenu. Un manifeste présent '
      + 'est un manifeste DÉCLARÉ.',
    xmp_history: historique.map((e) => ({
      action: e.action, logiciel: e.logiciel, quand: e.quand,
      change: e.change, identifiant_instance: e.identifiantInstance,
      parametres: e.parametres,
    })),
    xmp_packets: paquetsXmp.length,
    motif_xmp_history: historique.length > 0 ? null
      : "Aucun historique XMP. Cela ne veut pas dire que le fichier n’a pas été "
        + 'retouché : un historique se retire, se tronque et se réécrit, et un '
        + "logiciel qui ne respecte pas la convention n’y laisse rien.",
    iptc_records: provenance ? provenance.iptc.length : 0,
  };

  let quantification: AnalyseQuantification | null = null;
  if (conteneur === 'JPEG') {
    try {
      quantification = await analyserQuantification(donnees);
    } catch (err) {
      d.lectures_en_echec.push({
        lecteur: 'quantification', motif: err instanceof Error ? err.message : String(err),
      });
    }
  }

  const profil = inventaire?.profilIcc ?? null;
  d.deep_fingerprint = {
    icc_profile: profil?.description ?? null,
    icc_class: profil?.classeLibelle ?? null,
    icc_version: profil?.version ?? null,
    motif_icc: profil ? null
      : 'Aucun profil ICC intégré trouvé. Les JPEG rangent le leur dans un '
        + 'segment APP2 que ce relevé ne lit pas encore ; les PNG et les WebP '
        + 'sont couverts.',
    jpeg_quantization: quantification === null ? null : {
      empreinte_tables: quantification.empreinteEnsemble,
      qualite_ijg: quantification.qualiteIjg,
      ecart_a_ijg: quantification.ecartAIjg,
      conforme_ijg: quantification.conformeIjg,
      sous_echantillonnage: quantification.sousEchantillonnage,
      progressif: quantification.progressif,
      nombre_de_tables: quantification.tables.length,
    },
    jpeg_quantization_match: null,
    motif_quantization_match: MOTIF_AUCUNE_SIGNATURE,
    screen_resolution_match: null,
    motif_screen_resolution: MOTIF_ECRAN_NON_EVALUE,
    png_crc_corrompus: inventaire ? inventaire.chunksCorrompus : [],
    motif_crc: inventaire !== null && inventaire.format === 'PNG'
      ? 'Un CRC faux ÉTABLIT que les octets ont changé depuis l’écriture du '
        + 'chunk. Un CRC juste n’établit rien de plus que « celui qui a modifié '
        + 'le chunk a recalculé le CRC », ce que fait tout éditeur.'
      : null,
    apercus_embarques: await apercus(exif, structure),
  };

  return d;
}
