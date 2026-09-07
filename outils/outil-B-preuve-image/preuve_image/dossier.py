"""
dossier.py — Le relevé unifié d’un fichier, quel que soit son format (§16).

CE QUE CE MODULE FAIT
─────────────────────
Il n’extrait rien lui-même. Il ORCHESTRE les six lecteurs du paquet — EXIF,
conteneurs à boîtes, conteneurs hors EXIF, provenance, quantification,
télémétrie — et range ce qu’ils rendent dans une structure unique, la même quel
que soit le format d’entrée.

C’est le seul endroit du paquet qui a le droit de dire « ce fichier vient d’un
iPhone » : les lecteurs, eux, ne rendent que ce qu’ils lisent.

CE QU’IL NE FAIT PAS, ET POURQUOI CHAQUE CHAMP VIDE PORTE SON MOTIF
──────────────────────────────────────────────────────────────────
Un relevé unifié a un défaut propre : il présente côte à côte des champs qui ne
s’établissent pas de la même façon. La marque lue dans l’EXIF, le numéro de
série lu dans l’EXIF, le type de matériel DÉDUIT, et la correspondance d’écran
qui n’existe pas — tous les quatre auraient la même apparence dans un JSON, et
un lecteur pressé les prendrait pour des faits de même nature.

Trois dispositions l’en empêchent :

  · chaque bloc porte un champ `etabli_par` qui dit d’où vient l’information ;
  · un champ qu’on ne peut pas renseigner vaut None ET porte son motif, jamais
    une valeur plausible ;
  · les déductions sont marquées comme telles, avec la règle qui les a
    produites, pour qu’on puisse les contester sans relire le code.

Rien ici n’est vérifié. Une métadonnée s’écrit ; ce module l’affiche.
"""

import hashlib
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .conteneurs import ConteneurError, InventaireConteneur, inventorier
from .isobmff import IsobmffError, StructureIsobmff, analyser_isobmff
from .metadata import (
    ConteneurNonSupporte,
    DonneesExif,
    MetadataError,
    decrire_flash,
    detecter_conteneur,
    lire_exif,
)
from .provenance import (
    EvenementXmp,
    Provenance,
    analyser_provenance,
    extraire_historique_xmp,
)
from .quantification import (
    MOTIF_AUCUNE_SIGNATURE,
    QuantificationError,
    analyser_quantification,
)
from .telemetrie import TelemetrieVol, extraire_telemetrie

__all__ = [
    "DossierFichier",
    "constituer_dossier",
    "TYPES_MIME",
    "FAMILLES",
    "MOTIF_NUMERO_SERIE_ABSENT",
    "MOTIF_DECLENCHEMENTS_ABSENT",
    "MOTIF_ECRAN_NON_EVALUE",
    "deduire_type_materiel",
]

#: Le type MIME de chaque conteneur reconnu. Il est DÉDUIT DES OCTETS, jamais
#: du nom du fichier : une extension se renomme, et c'est le premier geste de
#: qui veut faire passer une image pour une autre.
TYPES_MIME = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "HEIC": "image/heic",
    "AVIF": "image/avif",
    "CR3": "image/x-canon-cr3",
    "TIFF/RAW": "image/tiff",
    "RAF": "image/x-fuji-raf",
    "WebP": "image/webp",
    "GIF": "image/gif",
    "BMP": "image/bmp",
    "SVG": "image/svg+xml",
}

#: La famille structurelle du conteneur — ce qui dit comment le fichier est
#: bâti, indépendamment de ce qu'il contient.
FAMILLES = {
    "JPEG": "JFIF/EXIF (segments APP)",
    "PNG": "PNG (chunks)",
    "HEIC": "HEIF/ISOBMFF (boîtes)",
    "AVIF": "AVIF/ISOBMFF (boîtes)",
    "CR3": "CR3/ISOBMFF (boîtes)",
    "TIFF/RAW": "TIFF (IFD)",
    "RAF": "RAF Fujifilm (JPEG embarqué)",
    "WebP": "RIFF (morceaux)",
    "GIF": "GIF (blocs et extensions)",
    "BMP": "BMP (en-têtes DIB)",
    "SVG": "SVG (XML)",
}

MOTIF_NUMERO_SERIE_ABSENT = (
    "Aucun numéro de série dans les tags EXIF standard (BodySerialNumber, "
    "LensSerialNumber). Beaucoup d’appareils n’en écrivent pas, et les "
    "téléphones n’en écrivent jamais dans ces champs-là. Certains boîtiers le "
    "rangent dans leurs MakerNotes propriétaires, que ce paquet ne décode pas."
)

MOTIF_DECLENCHEMENTS_ABSENT = (
    "Le décompte des déclenchements n’existe dans AUCUN tag EXIF standard. Il "
    "n’est écrit que dans les MakerNotes propriétaires, différemment par chaque "
    "constructeur et souvent par chaque millésime. Ce paquet rend les "
    "MakerNotes bruts sans les décoder : les interpréter demanderait un "
    "dictionnaire par appareil, qu’on ne peut pas écrire de mémoire sans se "
    "tromper."
)

MOTIF_ECRAN_NON_EVALUE = (
    "Aucun rapprochement par la résolution : il n’existe pas de référentiel "
    "vérifié des définitions d’écrans dans ce dépôt. En écrire un de mémoire "
    "produirait des correspondances fausses présentées comme des faits. Et le "
    "signal serait faible même vérifié : une résolution de 1179 × 2556 "
    "identifie une capture d’écran d’iPhone 15 Pro autant que n’importe quelle "
    "image recadrée à ces dimensions."
)


@dataclass(frozen=True)
class Deduction:
    """Une conclusion tirée, avec la règle qui l’a produite.

    Une déduction n’a pas le même statut qu’une lecture, et les présenter de la
    même façon serait le défaut principal d’un relevé unifié. `regle` permet de
    la contester sans relire le code.
    """

    valeur: str
    regle: str


def deduire_type_materiel(
    exif: Optional[DonneesExif],
    telemetrie: Optional[TelemetrieVol],
    conteneur: str,
) -> Optional[Deduction]:
    """Le type de matériel, DÉDUIT — jamais lu, parce qu’aucun format ne l’écrit.

    Les règles sont peu nombreuses et volontairement conservatrices : chacune
    s’appuie sur une trace non ambiguë, et l’absence de règle applicable rend
    None plutôt qu’une supposition. Un « appareil photo » deviné à partir d’un
    fabricant vaudrait moins que rien.
    """
    if telemetrie is not None and telemetrie.present:
        return Deduction(
            "aéronef sans équipage",
            "le fichier porte de la télémétrie de vol (%s)" % ", ".join(telemetrie.prefixes),
        )
    if exif is None:
        return None
    modele = (exif.modele or "").lower()
    fabricant = (exif.fabricant or "").lower()
    # Le nom d'objectif que les téléphones écrivent contient « back camera » ou
    # « front camera » : c'est une trace non ambiguë, écrite par le système et
    # non par l'utilisateur.
    objectif = (exif.objectif or "").lower()
    if "back camera" in objectif or "front camera" in objectif or "back triple camera" in objectif:
        return Deduction("téléphone", "le nom d’objectif déclare une caméra avant ou arrière")
    # Un numéro de série de boîtier ET un objectif interchangeable nommé : c'est
    # la signature d'un reflex ou d'un hybride. Aucun téléphone n'écrit les deux.
    if exif.numero_serie_boitier and exif.numero_serie_objectif:
        return Deduction(
            "appareil à objectifs interchangeables",
            "numéros de série de boîtier ET d’objectif tous deux présents",
        )
    if conteneur in ("CR3", "TIFF/RAW", "RAF"):
        return Deduction(
            "appareil photo dédié",
            "le fichier est un format brut de constructeur (%s)" % conteneur,
        )
    if "scanner" in modele or "scan" in fabricant:
        return Deduction("scanner", "le modèle ou le fabricant déclaré contient « scan »")
    return None


@dataclass
class DossierFichier:
    """Le relevé unifié. Chaque champ vide porte son motif."""

    file_analysis: Dict[str, Any] = field(default_factory=dict)
    device_identification: Dict[str, Any] = field(default_factory=dict)
    capture_settings: Dict[str, Any] = field(default_factory=dict)
    telemetry_and_location: Dict[str, Any] = field(default_factory=dict)
    provenance_and_software: Dict[str, Any] = field(default_factory=dict)
    deep_fingerprint: Dict[str, Any] = field(default_factory=dict)
    #: Ce qui a échoué, et pourquoi. Un lecteur en échec n'est jamais tu :
    #: l'absence d'un bloc et l'échec de sa lecture ne s'établissent pas de la
    #: même façon, et les confondre ferait passer une panne pour un constat.
    lectures_en_echec: List[Dict[str, str]] = field(default_factory=list)
    avertissements: List[str] = field(default_factory=list)

    def en_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _vitesse(secondes: Optional[float]) -> Optional[str]:
    """« 1/200 » sous la seconde, « 2,5 s » au-delà. Forme d’affichage seulement."""
    if secondes is None or secondes <= 0:
        return None
    if secondes >= 1:
        return "%g s" % round(secondes, 6)
    return "1/%d" % round(1.0 / secondes)


def constituer_dossier(donnees: bytes, nom_fichier: Optional[str] = None) -> DossierFichier:
    """Assemble le relevé unifié d’un fichier, quel que soit son format.

    Aucun lecteur en échec n’interrompt les autres : un JPEG dont l’EXIF a été
    purgé garde ses tables de quantification, et un PNG sans texte garde son
    profil ICC. Chaque échec est consigné avec son motif.
    """
    d = DossierFichier()
    conteneur = detecter_conteneur(donnees)

    # ── Le fichier lui-même ────────────────────────────────────────────────
    d.file_analysis = {
        "filename": nom_fichier,
        # Le type MIME vient des OCTETS, pas de l'extension : une extension se
        # renomme, et c'est le premier geste de qui veut faire passer une image
        # pour une autre. L'extension déclarée est rendue à côté, pour que
        # l'écart se voie.
        "mime_type": TYPES_MIME.get(conteneur),
        "mime_source": "octets du fichier, jamais l’extension",
        "extension_declaree": (
            os.path.splitext(nom_fichier)[1].lower() or None) if nom_fichier else None,
        "file_size_bytes": len(donnees),
        "format_family": FAMILLES.get(conteneur, conteneur),
        "conteneur": conteneur,
        "sha256": hashlib.sha256(donnees).hexdigest(),
    }
    ext = d.file_analysis["extension_declaree"]
    attendu = TYPES_MIME.get(conteneur)
    if ext and attendu:
        # On ne dresse pas de table extension → MIME : elle serait incomplète et
        # ferait de faux positifs. On signale seulement le cas franc, celui où
        # l'extension nomme un format que les octets démentent.
        familles_ext = {
            ".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".gif": "GIF",
            ".bmp": "BMP", ".webp": "WebP", ".svg": "SVG", ".heic": "HEIC",
            ".heif": "HEIC", ".avif": "AVIF", ".cr3": "CR3", ".raf": "RAF",
        }
        annonce = familles_ext.get(ext)
        if annonce is not None and annonce != conteneur:
            d.avertissements.append(
                "L’extension « %s » annonce un %s, les octets disent %s. "
                "Ce n’est pas une preuve de manipulation — un fichier se renomme "
                "par mégarde — mais c’est un écart, et il est relevé."
                % (ext, annonce, conteneur)
            )

    # ── EXIF ───────────────────────────────────────────────────────────────
    exif: Optional[DonneesExif] = None
    try:
        exif = lire_exif(donnees)
    except (MetadataError, ConteneurNonSupporte) as exc:
        d.lectures_en_echec.append({"lecteur": "EXIF", "motif": str(exc)})

    # ── Conteneurs : boîtes, ou blocs propres au format ────────────────────
    structure: Optional[StructureIsobmff] = None
    inventaire: Optional[InventaireConteneur] = None
    if conteneur in ("HEIC", "AVIF", "CR3") or conteneur.startswith("ISO BMFF"):
        try:
            structure = analyser_isobmff(donnees)
        except IsobmffError as exc:
            d.lectures_en_echec.append({"lecteur": "ISOBMFF", "motif": str(exc)})
    else:
        try:
            inventaire = inventorier(donnees)
        except ConteneurError:
            # Un JPEG ou un TIFF n'a rien à faire ici : ce n'est pas un échec,
            # c'est un partage de responsabilité entre lecteurs. On ne le
            # consigne donc pas comme une panne.
            inventaire = None

    # ── Provenance : C2PA, XMP, IPTC ───────────────────────────────────────
    provenance: Optional[Provenance] = None
    try:
        provenance = analyser_provenance(donnees)
    except Exception as exc:  # noqa: BLE001 — un lecteur en échec ne fait pas tomber le reste
        d.lectures_en_echec.append({"lecteur": "provenance", "motif": str(exc)})

    # Les paquets XMP viennent de trois endroits selon le format. Les réunir
    # ici évite à chaque appelant de savoir lequel interroger.
    paquets_xmp: List[bytes] = []
    if provenance is not None:
        paquets_xmp += [b.brut.encode("utf-8") for b in provenance.xmp]
    if structure is not None:
        paquets_xmp += list(structure.paquets_xmp)
    if inventaire is not None:
        paquets_xmp += list(inventaire.paquets_xmp)

    telemetrie = extraire_telemetrie(paquets_xmp) if paquets_xmp else extraire_telemetrie([])

    historique: List[EvenementXmp] = []
    for p in paquets_xmp:
        historique += extraire_historique_xmp(p.decode("utf-8", errors="replace"))

    # ── Le matériel ────────────────────────────────────────────────────────
    deduction = deduire_type_materiel(exif, telemetrie, conteneur)
    numeros = [x for x in (
        exif.numero_serie_boitier if exif else None,
        exif.numero_serie_objectif if exif else None,
    ) if x]
    d.device_identification = {
        "make": exif.fabricant if exif else None,
        "model": exif.modele if exif else None,
        "hardware_type": deduction.valeur if deduction else None,
        "hardware_type_regle": deduction.regle if deduction else None,
        "hardware_type_statut": "déduit, non lu" if deduction else "indéterminé",
        "serial_number": exif.numero_serie_boitier if exif else None,
        "lens_serial_number": exif.numero_serie_objectif if exif else None,
        "lens_model": exif.objectif if exif else None,
        "lens_make": exif.fabricant_objectif if exif else None,
        "owner_declared": exif.proprietaire_declare if exif else None,
        "detection_method": _methode_detection(exif, structure, conteneur),
        "motif_serial_number": None if numeros else MOTIF_NUMERO_SERIE_ABSENT,
        "ce_que_ca_n_etablit_pas": (
            "Un numéro de série rattache le cliché à un appareil DÉCLARÉ, pas à "
            "un appareil établi : une métadonnée s’écrit et se modifie (§17.1). "
            "Il sert à confronter deux fichiers entre eux, pas à prouver une "
            "origine."
        ),
    }

    # ── Les réglages de prise de vue ───────────────────────────────────────
    d.capture_settings = {
        "iso": exif.sensibilite_iso if exif else None,
        "focal_length_mm": exif.focale_mm if exif else None,
        "focal_length_35mm": exif.focale_equivalente_35mm if exif else None,
        "exposure_time": _vitesse(exif.temps_pose_s if exif else None),
        "exposure_time_s": exif.temps_pose_s if exif else None,
        "f_number": exif.ouverture if exif else None,
        "flash": decrire_flash(exif.flash) if exif else None,
        "flash_code": exif.flash if exif else None,
        "lens_specification": list(exif.specification_objectif)
        if exif and exif.specification_objectif else None,
        # Le décompte des déclenchements n'est dans AUCUN tag standard.
        "shutter_count": None,
        "motif_shutter_count": MOTIF_DECLENCHEMENTS_ABSENT,
        "dimensions": (
            [exif.largeur_px, exif.hauteur_px]
            if exif and exif.largeur_px and exif.hauteur_px
            else ([inventaire.largeur, inventaire.hauteur]
                  if inventaire and inventaire.largeur else None)
        ),
    }

    # ── Position et télémétrie ─────────────────────────────────────────────
    gps = exif.gps if exif else None
    d.telemetry_and_location = {
        "gps": None if gps is None else {
            "latitude": gps.latitude_deg,
            "longitude": gps.longitude_deg,
            "altitude_meters": gps.altitude_m,
            "uncertainty_meters": gps.incertitude_m,
            "source": gps.source,
        },
        "drone_telemetry": None if not telemetrie.present else {
            "origine": telemetrie.origine,
            "prefixes": list(telemetrie.prefixes),
            "latitude": telemetrie.latitude_deg,
            "longitude": telemetrie.longitude_deg,
            "absolute_altitude_m": telemetrie.altitude_absolue_m,
            "relative_altitude_m": telemetrie.altitude_relative_m,
            "above_ground_altitude_m": telemetrie.altitude_sol_m,
            "gimbal_pitch_deg": telemetrie.tangage_nacelle_deg,
            "gimbal_yaw_deg": telemetrie.lacet_nacelle_deg,
            "gimbal_roll_deg": telemetrie.roulis_nacelle_deg,
            "visee_horizontale": telemetrie.visee_horizontale,
            "ground_station": None,
            "motif_ground_station": telemetrie.motif_station_sol,
            "avertissement_altitude": telemetrie.avertissement_altitude,
        },
        "ce_que_ca_n_etablit_pas": (
            "Une position GPS est ce que le récepteur a DÉCLARÉ au moment de "
            "l’écriture. Elle ne prouve pas où le cliché a été pris : le champ "
            "s’écrit, et un récepteur dérive, se trompe ou perd sa constellation."
        ),
    }

    # ── Provenance et logiciel ─────────────────────────────────────────────
    c2pa_present = bool(provenance and provenance.c2pa.present)
    d.provenance_and_software = {
        "software": exif.logiciel if exif else None,
        "creation_date": exif.date_heure_original if exif else None,
        "creation_date_offset": exif.decalage_horaire_original if exif else None,
        "modification_date": exif.date_heure_modification if exif else None,
        "digitized_date": exif.date_heure_numerisation if exif else None,
        "artist": exif.artiste if exif else None,
        "copyright": exif.droits if exif else None,
        "c2pa_credentials": c2pa_present,
        "c2pa_verified": False,
        "motif_c2pa_non_verifie": (
            "Aucune signature n’est vérifiée : ni la validation COSE, ni la "
            "chaîne X.509, ni les empreintes de liaison au contenu. Un "
            "manifeste présent est un manifeste DÉCLARÉ."
        ),
        "xmp_history": [asdict(e) for e in historique],
        "xmp_packets": len(paquets_xmp),
        "motif_xmp_history": None if historique else (
            "Aucun historique XMP. Cela ne veut pas dire que le fichier n’a pas "
            "été retouché : un historique se retire, se tronque et se réécrit, "
            "et un logiciel qui ne respecte pas la convention n’y laisse rien."
        ),
        "iptc_records": (
            len(provenance.iptc) if provenance else 0
        ),
    }

    # ── L'empreinte profonde ───────────────────────────────────────────────
    quantification = None
    if conteneur == "JPEG":
        try:
            quantification = analyser_quantification(donnees)
        except QuantificationError as exc:
            d.lectures_en_echec.append({"lecteur": "quantification", "motif": str(exc)})

    profil = None
    if inventaire is not None and inventaire.profil_icc is not None:
        profil = inventaire.profil_icc
    d.deep_fingerprint = {
        "icc_profile": profil.description if profil else None,
        "icc_class": profil.classe_libelle if profil else None,
        "icc_version": profil.version if profil else None,
        "motif_icc": None if profil else (
            "Aucun profil ICC intégré trouvé. Les JPEG rangent le leur dans un "
            "segment APP2 que ce relevé ne lit pas encore ; les PNG et les WebP "
            "sont couverts."
        ),
        "jpeg_quantization": None if quantification is None else {
            "empreinte_tables": quantification.empreinte_ensemble,
            "qualite_ijg": quantification.qualite_ijg,
            "ecart_a_ijg": quantification.ecart_a_ijg,
            "conforme_ijg": quantification.conforme_ijg,
            "sous_echantillonnage": quantification.sous_echantillonnage,
            "progressif": quantification.progressif,
            "nombre_de_tables": len(quantification.tables),
        },
        "jpeg_quantization_match": None,
        "motif_quantization_match": MOTIF_AUCUNE_SIGNATURE,
        "screen_resolution_match": None,
        "motif_screen_resolution": MOTIF_ECRAN_NON_EVALUE,
        "png_crc_corrompus": (
            list(inventaire.chunks_corrompus) if inventaire else []
        ),
        "motif_crc": (
            "Un CRC faux ÉTABLIT que les octets ont changé depuis l’écriture du "
            "chunk. Un CRC juste n’établit rien de plus que « celui qui a "
            "modifié le chunk a recalculé le CRC », ce que fait tout éditeur."
        ) if inventaire is not None and inventaire.format == "PNG" else None,
        "apercus_embarques": _apercus(exif, structure),
    }

    return d


def _methode_detection(
    exif: Optional[DonneesExif],
    structure: Optional[StructureIsobmff],
    conteneur: str,
) -> str:
    """D’où vient l’identification du matériel, en toutes lettres.

    Sans ce champ, un relevé rendrait « Apple / iPhone 15 Pro » sans dire si
    l’information vient d’un tag EXIF, d’un nom de fichier ou d’une déduction —
    et les trois n’ont pas le même poids.
    """
    voies: List[str] = []
    if exif is not None and (exif.fabricant or exif.modele):
        voies.append("tags EXIF standard (Make, Model)")
    if exif is not None and (exif.numero_serie_boitier or exif.numero_serie_objectif):
        voies.append("numéros de série EXIF (BodySerialNumber, LensSerialNumber)")
    if structure is not None and structure.makernotes:
        voies.append(
            "MakerNotes présents (%d octets) mais NON DÉCODÉS" % len(structure.makernotes))
    if not voies:
        return "aucune : rien dans ce fichier ne nomme d’appareil"
    return " ; ".join(voies) + " — conteneur %s" % conteneur


def _apercus(
    exif: Optional[DonneesExif], structure: Optional[StructureIsobmff]
) -> List[Dict[str, Any]]:
    """Les images embarquées, de la plus grande à la plus petite.

    Elles n’ont pas nécessairement été écrites au même moment du traitement, et
    c’est leur comparaison qui a valeur d’indice — d’où le fait de toutes les
    lister plutôt que de n’en montrer qu’une.
    """
    out: List[Dict[str, Any]] = []
    vus = set()
    if exif is not None:
        for m in exif.previsualisations:
            cle = hashlib.sha256(m.octets).hexdigest()
            if cle in vus:
                continue
            vus.add(cle)
            out.append({
                "origine": m.origine, "octets": m.longueur,
                "format": "JPEG" if m.est_jpeg else "non reconnu", "sha256": cle,
            })
    if structure is not None:
        for origine, octets in structure.apercus:
            cle = hashlib.sha256(octets).hexdigest()
            if cle in vus:
                continue
            vus.add(cle)
            out.append({
                "origine": origine, "octets": len(octets),
                "format": "JPEG" if octets[:2] == b"\xff\xd8" else "non reconnu",
                "sha256": cle,
            })
    return sorted(out, key=lambda x: x["octets"], reverse=True)
