"""
metadata.py — EXIF/MakerNotes, échelle métrique et position GNSS (§16, §19.1).

Ce module lit ce que l'appareil ou le récepteur ont réellement écrit —
il n'estime rien. Trois responsabilités :

  - un lecteur EXIF/TIFF minimal, écrit ici plutôt qu'emprunté à une
    bibliothèque tierce opaque : pour un usage probatoire, comprendre
    exactement ce qui est extrait (et ce qui ne l'est pas) compte autant
    que l'extraction elle-même. Il couvre les champs que le §15.4 et le
    §16.1 exigent — pas la norme EXIF entière ;
  - la détermination de l'échelle métrique par les deux voies
    indépendantes du §19.1, et leur confrontation à 2 % ;
  - un lecteur de trames NMEA 0183 ($--GGA), pour la position GNSS
    quand elle vient d'un récepteur séparé plutôt que du boîtier.

Ce module NE FAIT PAS l'analyse de manipulation (PRNU, ELA — voir
sensor_forensics.py, à venir) et ne certifie aucune origine : une
métadonnée EXIF s'écrit, elle documente la chaîne, elle ne prouve pas
la provenance (§17.1, encadré) — ce module l'affiche, rien de plus.
"""

import struct
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

__all__ = [
    "MetadataError",
    "PositionGPS",
    "DonneesExif",
    "Miniature",
    "decrire_flash",
    "lire_exif_depuis_tiff",
    "lire_exif_depuis_jpeg",
    "lire_exif",
    "detecter_conteneur",
    "ConteneurNonSupporte",
    "FORMATS_RAW_TIFF",
    "INDISPONIBLE",
    "declarer",
    "FicheGrossissement",
    "angle_par_pixel_depuis_focale",
    "angle_par_pixel_depuis_reperes",
    "ResultatEchelle",
    "verifier_coherence_echelle",
    "PositionGNSS",
    "lire_trame_gga",
    "precision_horizontale_estimee",
]


class MetadataError(ValueError):
    """Domaine invalide, flux EXIF/TIFF malformé, ou trame NMEA invalide."""


# --- Lecteur EXIF/TIFF minimal ---

# Tags TIFF/EXIF utilisés (identifiants standard CIPA DC-008 / JEITA CP-3451, §35.1 n°9).
_TAG_MAKE = 0x010F
_TAG_MODEL = 0x0110
_TAG_ORIENTATION = 0x0112
_TAG_EXIF_IFD_POINTER = 0x8769
_TAG_GPS_IFD_POINTER = 0x8825

_TAG_EXPOSURE_TIME = 0x829A
_TAG_FNUMBER = 0x829D
_TAG_ISO_SPEED = 0x8827
_TAG_DATETIME_ORIGINAL = 0x9003
_TAG_FOCAL_LENGTH = 0x920A
_TAG_PIXEL_X_DIMENSION = 0xA002
_TAG_PIXEL_Y_DIMENSION = 0xA003
_TAG_FOCAL_LENGTH_35MM = 0xA405
_TAG_LENS_MODEL = 0xA434

# Ajoutés pour l'ingestion : tout ce que le §16 demande de LIRE sans rien conclure.
_TAG_IMAGE_WIDTH = 0x0100
_TAG_IMAGE_LENGTH = 0x0101
_TAG_X_RESOLUTION = 0x011A
_TAG_Y_RESOLUTION = 0x011B
_TAG_RESOLUTION_UNIT = 0x0128
_TAG_SOFTWARE = 0x0131
_TAG_DATETIME = 0x0132          # date de dernière modification du fichier par l'appareil ou l'éditeur
_TAG_ARTIST = 0x013B
_TAG_COPYRIGHT = 0x8298

# Décalages horaires (EXIF 2.31 et suivantes). Sans eux, DateTimeOriginal est une
# heure locale SANS fuseau : la convertir en horodatage ISO 8601 avec un offset
# reviendrait à inventer une information que le fichier ne porte pas.
_TAG_OFFSET_TIME = 0x9010
_TAG_OFFSET_TIME_ORIGINAL = 0x9011
_TAG_OFFSET_TIME_DIGITIZED = 0x9012

_TAG_EXPOSURE_PROGRAM = 0x8822
_TAG_DATETIME_DIGITIZED = 0x9004
_TAG_FLASH = 0x9209
_TAG_COLOR_SPACE = 0xA001
_TAG_EXPOSURE_MODE = 0xA402
_TAG_WHITE_BALANCE = 0xA403
_TAG_DIGITAL_ZOOM_RATIO = 0xA404
_TAG_SCENE_CAPTURE_TYPE = 0xA406

# IFD1 : la miniature. Le §16 la veut pour la confronter à l'image principale —
# une miniature qui ne correspond plus au contenu est la trace la plus simple
# d'une retouche postérieure à la prise de vue.
_TAG_JPEG_INTERCHANGE_FORMAT = 0x0201
_TAG_JPEG_INTERCHANGE_FORMAT_LENGTH = 0x0202
_TAG_COMPRESSION = 0x0103
# Les sous-IFD, où les RAW rangent leurs prévisualisations. Un CR2 en met une
# pleine résolution dans l'IFD0 lui-même, un NEF dans un sous-IFD : les deux
# doivent être parcourus, sinon la vignette d'un RAW reste invisible.
_TAG_SUB_IFDS = 0x014A
_TAG_STRIP_OFFSETS = 0x0111
_TAG_STRIP_BYTE_COUNTS = 0x0117
_TAG_NEW_SUBFILE_TYPE = 0x00FE

_TAG_GPS_LAT_REF = 1
_TAG_GPS_LAT = 2
_TAG_GPS_LON_REF = 3
_TAG_GPS_LON = 4
_TAG_GPS_ALT_REF = 5
_TAG_GPS_ALT = 6
_TAG_GPS_H_POSITIONING_ERROR = 31

# Taille en octets d'un élément de chaque type TIFF géré (spec TIFF 6.0 §2).
_TAILLE_TYPE = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8}


def _decoder_entree(donnees: bytes, endian: str, type_: int, count: int, champ_valeur: bytes):
    taille_elem = _TAILLE_TYPE.get(type_, 1)
    taille_totale = taille_elem * count
    if taille_totale <= 4:
        bloc = champ_valeur[:taille_totale]
    else:
        offset = struct.unpack_from(endian + "I", champ_valeur, 0)[0]
        bloc = donnees[offset : offset + taille_totale]
        if len(bloc) < taille_totale:
            raise MetadataError("Bloc TIFF tronqué : donnée hors des limites du flux.")

    if type_ == 2:  # ASCII, terminée par NUL
        return bloc.split(b"\x00", 1)[0].decode("ascii", errors="replace")
    if type_ in (1, 7):  # BYTE / UNDEFINED
        valeurs = list(bloc)
        return valeurs[0] if count == 1 else tuple(valeurs)
    if type_ == 3:  # SHORT
        valeurs = struct.unpack_from(endian + f"{count}H", bloc)
        return valeurs[0] if count == 1 else valeurs
    if type_ == 4:  # LONG
        valeurs = struct.unpack_from(endian + f"{count}I", bloc)
        return valeurs[0] if count == 1 else valeurs
    if type_ == 9:  # SLONG
        valeurs = struct.unpack_from(endian + f"{count}i", bloc)
        return valeurs[0] if count == 1 else valeurs
    if type_ in (5, 10):  # RATIONAL / SRATIONAL
        fmt = "I" if type_ == 5 else "i"
        valeurs = []
        for i in range(count):
            num, den = struct.unpack_from(endian + f"2{fmt}", bloc, i * 8)
            valeurs.append(float(num) / den if den else float("nan"))
        return valeurs[0] if count == 1 else tuple(valeurs)
    return bloc  # type non géré : rendre les octets bruts plutôt qu'échouer


def _lire_ifd_et_suivant(
    donnees: bytes, offset: int, endian: str
) -> Tuple[Dict[int, object], int]:
    """Lit un IFD et rend aussi l'offset de l'IFD suivant (0 s'il n'y en a pas).

    Les quatre octets qui suivent la dernière entrée pointent vers l'IFD suivant.
    C'est par là que se trouve l'IFD1, celui de la miniature : sans lui, elle
    est invisible.
    """
    if offset + 2 > len(donnees):
        raise MetadataError("Offset d'IFD hors des limites du flux.")
    nb_entrees = struct.unpack_from(endian + "H", donnees, offset)[0]
    entrees: Dict[int, object] = {}
    pos = offset + 2
    for _ in range(nb_entrees):
        if pos + 12 > len(donnees):
            raise MetadataError("IFD tronqué : entrée hors des limites du flux.")
        tag, type_, count = struct.unpack_from(endian + "HHI", donnees, pos)
        champ_valeur = donnees[pos + 8 : pos + 12]
        entrees[tag] = _decoder_entree(donnees, endian, type_, count, champ_valeur)
        pos += 12
    suivant = 0
    if pos + 4 <= len(donnees):
        suivant = struct.unpack_from(endian + "I", donnees, pos)[0]
    return entrees, suivant


def _lire_ifd(donnees: bytes, offset: int, endian: str) -> Dict[int, object]:
    return _lire_ifd_et_suivant(donnees, offset, endian)[0]


def _dms_vers_degres(dms, ref: Optional[str]) -> float:
    d, m, s = dms
    degres = d + m / 60.0 + s / 3600.0
    if ref in ("S", "W"):
        degres = -degres
    return degres


def _construire_position_gps(ifd_gps: Dict[int, object]) -> Optional["PositionGPS"]:
    if _TAG_GPS_LAT not in ifd_gps or _TAG_GPS_LON not in ifd_gps:
        return None
    latitude = _dms_vers_degres(ifd_gps[_TAG_GPS_LAT], ifd_gps.get(_TAG_GPS_LAT_REF, "N"))
    longitude = _dms_vers_degres(ifd_gps[_TAG_GPS_LON], ifd_gps.get(_TAG_GPS_LON_REF, "E"))
    altitude = ifd_gps.get(_TAG_GPS_ALT)
    if altitude is not None and ifd_gps.get(_TAG_GPS_ALT_REF, 0) == 1:
        altitude = -altitude
    incertitude = ifd_gps.get(_TAG_GPS_H_POSITIONING_ERROR)
    return PositionGPS(
        latitude_deg=latitude,
        longitude_deg=longitude,
        altitude_m=altitude,
        incertitude_m=incertitude,
        source="EXIF GPS IFD",
    )


@dataclass(frozen=True)
class PositionGPS:
    """Position lue dans l'IFD GPS de l'EXIF (§16.1 : « position GNSS et incertitude annoncée »).

    `incertitude_m` reste None si l'appareil n'a pas écrit GPSHPositioningError — ce
    qui est le cas courant : la plupart des boîtiers ne l'annoncent pas. Une absence
    ici ne doit jamais être comblée par une valeur supposée (§15.4).
    """

    latitude_deg: float
    longitude_deg: float
    altitude_m: Optional[float]
    incertitude_m: Optional[float]
    source: str

    def __post_init__(self):
        if not (-90.0 <= self.latitude_deg <= 90.0):
            raise MetadataError("Latitude GPS hors bornes [-90 ; 90].")
        if not (-180.0 <= self.longitude_deg <= 180.0):
            raise MetadataError("Longitude GPS hors bornes [-180 ; 180].")


# --- Champs codés : on rend le code ET son libellé, jamais le libellé seul ---
#
# Un libellé est une interprétation ; le code est ce que l'appareil a écrit. Les
# deux sont conservés pour qu'un lecteur puisse contester la table sans perdre
# la donnée. Les tables suivent CIPA DC-008 (EXIF 2.32).

_LIBELLE_EXPOSURE_MODE = {0: "automatique", 1: "manuel", 2: "bracketing automatique"}

_LIBELLE_EXPOSURE_PROGRAM = {
    0: "non défini", 1: "manuel", 2: "programme normal", 3: "priorité ouverture",
    4: "priorité vitesse", 5: "création (profondeur de champ)", 6: "action (vitesse)",
    7: "portrait", 8: "paysage",
}

_LIBELLE_WHITE_BALANCE = {0: "automatique", 1: "manuel"}

_LIBELLE_COLOR_SPACE = {1: "sRGB", 2: "Adobe RGB", 0xFFFF: "non calibré"}

_LIBELLE_SCENE_CAPTURE = {0: "standard", 1: "paysage", 2: "portrait", 3: "scène de nuit"}

_LIBELLE_RESOLUTION_UNIT = {1: "sans unité", 2: "pouce", 3: "centimètre"}


def decrire_flash(code: Optional[int]) -> Optional[str]:
    """Décode le champ Flash (0x9209), qui est un champ de bits et non un code.

    bit 0 : l'éclair s'est déclenché ; bits 1-2 : lumière de retour détectée ;
    bits 3-4 : mode ; bit 5 : l'appareil n'a pas de flash ; bit 6 : anti-yeux rouges.

    Rendre « 16 » à un opérateur ne lui apprend rien ; rendre « flash présent,
    non déclenché » si. Le code brut reste disponible à côté.
    """
    if code is None:
        return None
    if code & 0x20:
        return "l'appareil n'a pas de flash"
    parties = ["déclenché" if code & 0x01 else "non déclenché"]
    mode = (code >> 3) & 0x03
    if mode == 1:
        parties.append("mode obligatoire")
    elif mode == 2:
        parties.append("mode supprimé")
    elif mode == 3:
        parties.append("mode automatique")
    retour = (code >> 1) & 0x03
    if retour == 2:
        parties.append("lumière de retour non détectée")
    elif retour == 3:
        parties.append("lumière de retour détectée")
    if code & 0x40:
        parties.append("anti-yeux rouges")
    return ", ".join(parties)


def _dpi(resolution: Optional[float], unite: Optional[int]) -> Optional[float]:
    """Résolution ramenée en points par pouce, ou None si l'unité ne le permet pas.

    Unité 1 (« sans unité ») ne donne PAS de DPI : le nombre est alors un rapport
    d'aspect, pas une densité. Le convertir serait inventer une grandeur.
    """
    if resolution is None or unite is None or resolution <= 0:
        return None
    if unite == 2:
        return float(resolution)
    if unite == 3:
        return float(resolution) * 2.54
    return None


@dataclass(frozen=True)
class Miniature:
    """La miniature de l'IFD1, telle qu'elle est stockée.

    `octets` est le flux JPEG intégral, extrait sans être décodé ni recompressé :
    c'est lui qu'on confronte à l'image principale. `empreinte` permet de le citer
    dans une fiche sans le joindre.

    Ce que sa présence établit : l'appareil ou le logiciel a écrit une vignette.
    Ce qu'elle n'établit pas : que l'image principale n'a pas été modifiée. Un
    éditeur qui régénère la miniature efface la trace ; un éditeur qui ne la
    régénère pas la laisse. L'absence de divergence ne prouve donc rien, seule
    une divergence est un fait.
    """

    offset: int
    longueur: int
    octets: bytes
    compression: Optional[int]
    #  D'où elle vient : « IFD1 » pour la vignette EXIF classique, « IFD0 » ou
    #  « sous-IFD n » pour les prévisualisations d'un RAW. Un fichier brut en
    #  porte plusieurs, de tailles très différentes, et laquelle on regarde
    #  change ce qu'on voit.
    origine: str = "IFD1"

    @property
    def est_jpeg(self) -> bool:
        return self.octets[:2] == b"\xff\xd8"


def _miniature_depuis_ifd(
    donnees: bytes, ifd: Dict[int, object], origine: str
) -> Optional[Miniature]:
    """Extrait la prévisualisation d'un IFD, par l'une des deux conventions.

    JpegIFOffset / JpegIFByteCount est la voie normale. Les bandes
    (StripOffsets / StripByteCounts) en sont l'autre : plusieurs RAW y rangent
    leur aperçu, et l'ignorer laisserait la vignette invisible sur ces
    fichiers-là. Une bande unique suffit ici : un aperçu découpé en plusieurs
    bandes n'est pas un JPEG contigu, et le recoller demanderait de décoder.
    """
    offset = ifd.get(_TAG_JPEG_INTERCHANGE_FORMAT)
    longueur = ifd.get(_TAG_JPEG_INTERCHANGE_FORMAT_LENGTH)
    if not isinstance(offset, int) or not isinstance(longueur, int):
        o, l = ifd.get(_TAG_STRIP_OFFSETS), ifd.get(_TAG_STRIP_BYTE_COUNTS)
        if isinstance(o, int) and isinstance(l, int):
            offset, longueur = o, l
        else:
            return None
    if longueur <= 0 or offset < 0 or offset + longueur > len(donnees):
        # Offsets incohérents : on ne rend pas une miniature tronquée qui
        # passerait pour entière.
        return None
    return Miniature(
        offset=offset,
        longueur=longueur,
        octets=donnees[offset : offset + longueur],
        compression=ifd.get(_TAG_COMPRESSION),
        origine=origine,
    )


def _extraire_miniature(donnees: bytes, ifd1: Dict[int, object]) -> Optional[Miniature]:
    return _miniature_depuis_ifd(donnees, ifd1, "IFD1")


def _sous_ifds(donnees: bytes, ifd0: Dict[int, object], endian: str) -> List[Dict[int, object]]:
    """Les sous-IFD listés au tag 0x014A. Un pointeur illisible est ignoré, pas fatal."""
    pointeurs = ifd0.get(_TAG_SUB_IFDS)
    if isinstance(pointeurs, int):
        pointeurs = (pointeurs,)
    if not isinstance(pointeurs, (tuple, list)):
        return []
    out: List[Dict[int, object]] = []
    for p in pointeurs[:8]:  # borne de sûreté : aucun format n'en aligne davantage
        if not isinstance(p, int) or not (0 < p < len(donnees)):
            continue
        try:
            out.append(_lire_ifd(donnees, p, endian))
        except MetadataError:
            continue
    return out


def _collecter_previsualisations(
    donnees: bytes, ifd0: Dict[int, object], ifd1: Dict[int, object], endian: str
) -> Tuple[Miniature, ...]:
    """Toutes les images embarquées trouvées, de la plus grande à la plus petite.

    Un fichier brut en porte plusieurs : un aperçu pleine résolution, un aperçu
    moyen, une vignette. En choisir une silencieusement masquerait les autres —
    or elles ne montrent pas la même chose, et c'est précisément leur
    comparaison qui a une valeur d'indice.
    """
    trouvees: List[Miniature] = []
    vus = set()
    sources = [(ifd0, "IFD0"), (ifd1, "IFD1")]
    sources += [(sub, "sous-IFD %d" % i) for i, sub in enumerate(_sous_ifds(donnees, ifd0, endian))]
    for ifd, origine in sources:
        if not ifd:
            continue
        m = _miniature_depuis_ifd(donnees, ifd, origine)
        if m is None or not m.est_jpeg:
            continue
        if (m.offset, m.longueur) in vus:
            continue
        vus.add((m.offset, m.longueur))
        trouvees.append(m)
    return tuple(sorted(trouvees, key=lambda x: x.longueur, reverse=True))


@dataclass(frozen=True)
class DonneesExif:
    """Les champs EXIF que le protocole utilise. Un champ à None n'a pas été écrit par
    l'appareil — ce n'est pas la même chose qu'une déclaration « indisponible » au
    sens du §15.4 (voir FicheGrossissement) : ici, personne n'a encore regardé.
    """

    fabricant: Optional[str]
    modele: Optional[str]
    objectif: Optional[str]
    focale_mm: Optional[float]
    focale_equivalente_35mm: Optional[int]
    ouverture: Optional[float]
    temps_pose_s: Optional[float]
    sensibilite_iso: Optional[int]
    largeur_px: Optional[int]
    hauteur_px: Optional[int]
    date_heure_original: Optional[str]
    orientation: Optional[int]
    gps: Optional[PositionGPS]
    # --- Ajouts d'ingestion (§16) ---
    logiciel: Optional[str] = None
    date_heure_modification: Optional[str] = None
    date_heure_numerisation: Optional[str] = None
    artiste: Optional[str] = None
    droits: Optional[str] = None
    largeur_ifd0_px: Optional[int] = None
    hauteur_ifd0_px: Optional[int] = None
    resolution_x: Optional[float] = None
    resolution_y: Optional[float] = None
    unite_resolution: Optional[int] = None
    dpi_x: Optional[float] = None
    dpi_y: Optional[float] = None
    espace_colorimetrique: Optional[int] = None
    mode_exposition: Optional[int] = None
    programme_exposition: Optional[int] = None
    balance_blancs: Optional[int] = None
    rapport_zoom_numerique: Optional[float] = None
    type_scene: Optional[int] = None
    flash: Optional[int] = None
    miniature: Optional[Miniature] = None
    decalage_horaire: Optional[str] = None
    decalage_horaire_original: Optional[str] = None
    decalage_horaire_numerisation: Optional[str] = None
    conteneur: Optional[str] = None
    previsualisations: Tuple["Miniature", ...] = ()

    @property
    def previsualisation_principale(self) -> Optional["Miniature"]:
        """La plus grande image embarquée, ou None. C'est celle qu'on affiche.

        Sur un JPEG ordinaire il n'y en a qu'une, la vignette de l'IFD1. Sur un
        RAW il y en a plusieurs : la plus grande est celle qui montre le plus,
        et les autres restent listées dans `previsualisations`.
        """
        return self.previsualisations[0] if self.previsualisations else None

    # Libellés : l'interprétation des codes, jamais à leur place.
    @property
    def flash_libelle(self) -> Optional[str]:
        return decrire_flash(self.flash)

    @property
    def mode_exposition_libelle(self) -> Optional[str]:
        return _LIBELLE_EXPOSURE_MODE.get(self.mode_exposition) if self.mode_exposition is not None else None

    @property
    def programme_exposition_libelle(self) -> Optional[str]:
        return _LIBELLE_EXPOSURE_PROGRAM.get(self.programme_exposition) if self.programme_exposition is not None else None

    @property
    def balance_blancs_libelle(self) -> Optional[str]:
        return _LIBELLE_WHITE_BALANCE.get(self.balance_blancs) if self.balance_blancs is not None else None

    @property
    def espace_colorimetrique_libelle(self) -> Optional[str]:
        return _LIBELLE_COLOR_SPACE.get(self.espace_colorimetrique) if self.espace_colorimetrique is not None else None

    @property
    def type_scene_libelle(self) -> Optional[str]:
        return _LIBELLE_SCENE_CAPTURE.get(self.type_scene) if self.type_scene is not None else None

    @property
    def unite_resolution_libelle(self) -> Optional[str]:
        return _LIBELLE_RESOLUTION_UNIT.get(self.unite_resolution) if self.unite_resolution is not None else None

    @property
    def zoom_numerique_applique(self) -> Optional[bool]:
        """Le §15 en dépend directement : un zoom numérique agrandit sans ajouter
        d'information, et le rapport écrit ici est ce qui permet de retrouver la
        définition réellement enregistrée. 0 signifie « non utilisé » dans la norme,
        et non « rapport nul »."""
        if self.rapport_zoom_numerique is None:
            return None
        return self.rapport_zoom_numerique > 1.0


# Nombres magiques TIFF admis, à l'octet 2 de l'en-tête.
#
# 42 est celui de la norme TIFF 6.0, et celui que porte tout bloc EXIF d'un
# JPEG. Les fabricants de RAW s'en écartent pour signaler leur variante tout en
# gardant la même structure d'IFD derrière : Panasonic RW2 vaut 85, et Olympus
# emploie 0x4F52 (« RO ») ou 0x5352 (« RS ») selon le millésime.
#
# La distinction compte : un bloc EXIF de JPEG qui ne vaudrait pas 42 est un
# bloc corrompu, et l'accepter masquerait la corruption. C'est pourquoi le
# lecteur exige 42 PAR DÉFAUT, et n'admet les variantes que lorsque l'appelant
# a lui-même reconnu un conteneur RAW.
_MAGIQUE_TIFF_STANDARD = 42
_MAGIQUES_TIFF = (_MAGIQUE_TIFF_STANDARD, 85, 0x4F52, 0x5352)


def lire_exif_depuis_tiff(
    donnees: bytes, magiques_admis: Tuple[int, ...] = (_MAGIQUE_TIFF_STANDARD,)
) -> DonneesExif:
    """Lit un bloc TIFF/EXIF brut (en-tête « II » ou « MM ») et en extrait les champs utiles.

    N'implémente pas la norme TIFF/EXIF entière : seulement IFD0, le sous-IFD Exif et
    le sous-IFD GPS, et seulement les tags listés en tête de module. Un tag absent
    donne un champ à None, jamais une exception.

    `magiques_admis` borne les en-têtes acceptés. Par défaut le seul 42 de la
    norme ; `lire_exif` élargit à `_MAGIQUES_TIFF` quand il a reconnu un RAW,
    de sorte qu'un bloc EXIF de JPEG corrompu échoue toujours.
    """
    if len(donnees) < 8:
        raise MetadataError("Bloc TIFF/EXIF trop court pour contenir un en-tête.")
    marqueur = donnees[0:2]
    if marqueur == b"II":
        endian = "<"
    elif marqueur == b"MM":
        endian = ">"
    else:
        raise MetadataError(f"En-tête TIFF invalide : {marqueur!r} n'est ni « II » ni « MM ».")
    magique = struct.unpack_from(endian + "H", donnees, 2)[0]
    if magique not in magiques_admis:
        attendus = ", ".join(str(m) for m in magiques_admis)
        raise MetadataError(
            f"En-tête TIFF invalide : nombre magique {magique} hors des valeurs admises ({attendus})."
        )
    offset_ifd0 = struct.unpack_from(endian + "I", donnees, 4)[0]

    ifd0, offset_ifd1 = _lire_ifd_et_suivant(donnees, offset_ifd0, endian)
    ifd_exif = _lire_ifd(donnees, ifd0[_TAG_EXIF_IFD_POINTER], endian) if _TAG_EXIF_IFD_POINTER in ifd0 else {}
    ifd_gps = _lire_ifd(donnees, ifd0[_TAG_GPS_IFD_POINTER], endian) if _TAG_GPS_IFD_POINTER in ifd0 else {}
    # L'IFD1 est facultatif et souvent malformé chez les éditeurs : son échec
    # ne doit pas emporter la lecture des champs principaux.
    ifd1: Dict[int, object] = {}
    if 0 < offset_ifd1 < len(donnees):
        try:
            ifd1 = _lire_ifd(donnees, offset_ifd1, endian)
        except MetadataError:
            ifd1 = {}

    resolution_x = ifd0.get(_TAG_X_RESOLUTION)
    resolution_y = ifd0.get(_TAG_Y_RESOLUTION)
    unite = ifd0.get(_TAG_RESOLUTION_UNIT)

    return DonneesExif(
        fabricant=ifd0.get(_TAG_MAKE),
        modele=ifd0.get(_TAG_MODEL),
        objectif=ifd_exif.get(_TAG_LENS_MODEL),
        focale_mm=ifd_exif.get(_TAG_FOCAL_LENGTH),
        focale_equivalente_35mm=ifd_exif.get(_TAG_FOCAL_LENGTH_35MM),
        ouverture=ifd_exif.get(_TAG_FNUMBER),
        temps_pose_s=ifd_exif.get(_TAG_EXPOSURE_TIME),
        sensibilite_iso=ifd_exif.get(_TAG_ISO_SPEED),
        largeur_px=ifd_exif.get(_TAG_PIXEL_X_DIMENSION),
        hauteur_px=ifd_exif.get(_TAG_PIXEL_Y_DIMENSION),
        date_heure_original=ifd_exif.get(_TAG_DATETIME_ORIGINAL),
        orientation=ifd0.get(_TAG_ORIENTATION),
        gps=_construire_position_gps(ifd_gps) if ifd_gps else None,
        logiciel=ifd0.get(_TAG_SOFTWARE),
        date_heure_modification=ifd0.get(_TAG_DATETIME),
        date_heure_numerisation=ifd_exif.get(_TAG_DATETIME_DIGITIZED),
        artiste=ifd0.get(_TAG_ARTIST),
        droits=ifd0.get(_TAG_COPYRIGHT),
        largeur_ifd0_px=ifd0.get(_TAG_IMAGE_WIDTH),
        hauteur_ifd0_px=ifd0.get(_TAG_IMAGE_LENGTH),
        resolution_x=resolution_x,
        resolution_y=resolution_y,
        unite_resolution=unite,
        dpi_x=_dpi(resolution_x, unite),
        dpi_y=_dpi(resolution_y, unite),
        espace_colorimetrique=ifd_exif.get(_TAG_COLOR_SPACE),
        mode_exposition=ifd_exif.get(_TAG_EXPOSURE_MODE),
        programme_exposition=ifd_exif.get(_TAG_EXPOSURE_PROGRAM),
        balance_blancs=ifd_exif.get(_TAG_WHITE_BALANCE),
        rapport_zoom_numerique=ifd_exif.get(_TAG_DIGITAL_ZOOM_RATIO),
        type_scene=ifd_exif.get(_TAG_SCENE_CAPTURE_TYPE),
        flash=ifd_exif.get(_TAG_FLASH),
        miniature=_extraire_miniature(donnees, ifd1) if ifd1 else None,
        decalage_horaire=ifd_exif.get(_TAG_OFFSET_TIME),
        decalage_horaire_original=ifd_exif.get(_TAG_OFFSET_TIME_ORIGINAL),
        decalage_horaire_numerisation=ifd_exif.get(_TAG_OFFSET_TIME_DIGITIZED),
        previsualisations=_collecter_previsualisations(donnees, ifd0, ifd1, endian),
    )


# --- Conteneurs bruts (RAW) ---
#
# Un fichier RAW d'appareil photo n'est pas un JPEG : il n'y a pas de segment
# APP1 à chercher. La quasi-totalité des formats sont en réalité des TIFF —
# CR2, NEF, ARW, DNG, ORF, PEF, SRW, RW2 — et leur EXIF est directement dans
# l'IFD0 et le sous-IFD Exif du fichier lui-même. Le lecteur TIFF déjà écrit
# ici les couvre donc, à condition de le lui donner à lire plutôt que de
# chercher un APP1 qui n'existe pas.
#
# Deux exceptions notables :
#   · RAF (Fujifilm) n'est pas un TIFF : il commence par « FUJIFILMCCD-RAW » et
#     embarque un JPEG complet, dont l'EXIF se lit normalement ;
#   · CR3 (Canon récent) est un conteneur ISO BMFF, comme un MP4. Il est
#     DÉTECTÉ et refusé explicitement plutôt que lu de travers — un lecteur qui
#     rendrait des champs vides laisserait croire que le fichier n'en porte pas.

FORMATS_RAW_TIFF = (
    "CR2 (Canon)", "NEF / NRW (Nikon)", "ARW / SR2 (Sony)", "DNG (Adobe)",
    "ORF (Olympus)", "PEF (Pentax)", "SRW (Samsung)", "RW2 (Panasonic)",
    "IIQ (Phase One)", "3FR (Hasselblad)",
)


class ConteneurNonSupporte(MetadataError):
    """Format reconnu, mais que ce lecteur n'implémente pas. Dit lequel, et pourquoi."""


def detecter_conteneur(donnees: bytes) -> str:
    """Nomme le conteneur : « JPEG », « TIFF/RAW », « RAF », « CR3 », « PNG », ou « inconnu ».

    Le nom est rendu même quand la lecture échouera ensuite : savoir qu'un
    fichier EST un CR3 et que le lecteur ne le couvre pas vaut mieux que de ne
    rien savoir.
    """
    # Chaque signature a sa propre longueur minimale, et le test se fait dans
    # l'ordre croissant de celle-ci. Un plancher unique de 12 octets écartait
    # les tout petits fichiers : un JPEG de 8 octets EST un JPEG, et le
    # déclarer « inconnu » envoyait ensuite un motif d'échec qui parlait de
    # conteneur non reconnu là où il fallait dire « aucun segment EXIF ».
    if len(donnees) < 2:
        return "inconnu"
    if donnees[0:2] == b"\xff\xd8":
        return "JPEG"
    if donnees[0:8] == b"\x89PNG\r\n\x1a\n":
        return "PNG"
    if donnees[0:15] == b"FUJIFILMCCD-RAW":
        return "RAF"
    if len(donnees) < 12:
        return "inconnu"
    # ISO BMFF : taille de boîte sur 4 octets, puis « ftyp ». La marque et les
    # marques compatibles nomment la variante — un HEIC et un CR3 sont le même
    # conteneur, et les confondre sous « ISO BMFF » perdrait ce qui les sépare.
    if donnees[4:8] == b"ftyp":
        marque = donnees[8:12].decode("ascii", errors="replace").strip("\x00 ")
        toutes = {marque}
        try:
            taille_ftyp = struct.unpack_from(">I", donnees, 0)[0]
            for i in range(16, min(taille_ftyp, len(donnees)), 4):
                toutes.add(donnees[i : i + 4].decode("ascii", errors="replace").strip("\x00 "))
        except struct.error:
            pass
        if marque == "crx":
            return "CR3"
        if toutes & {"avif", "avis"}:
            return "AVIF"
        if toutes & {"heic", "heix", "heim", "heis", "hevc", "mif1", "msf1"}:
            return "HEIC"
        return "ISO BMFF (%s)" % marque
    if donnees[0:2] in (b"II", b"MM"):
        endian = "<" if donnees[0:2] == b"II" else ">"
        try:
            magique = struct.unpack_from(endian + "H", donnees, 2)[0]
        except struct.error:
            return "inconnu"
        if magique in _MAGIQUES_TIFF:
            return "TIFF/RAW"
    return "inconnu"


def _jpeg_embarque_raf(donnees: bytes) -> Optional[bytes]:
    """Extrait le JPEG que porte un RAF Fujifilm.

    L'en-tête RAF donne l'offset et la longueur du JPEG en clair, aux octets
    84 et 88. On les préfère à une recherche du marqueur SOI : celle-ci
    trouverait aussi les vignettes internes, et rien ne garantirait laquelle.
    """
    if len(donnees) < 92:
        return None
    offset, longueur = struct.unpack_from(">II", donnees, 84)
    if longueur <= 0 or offset + longueur > len(donnees):
        return None
    bloc = donnees[offset : offset + longueur]
    return bloc if bloc[:2] == b"\xff\xd8" else None


def _fusionner_apercus(
    depuis_exif: Tuple[Miniature, ...], depuis_conteneur: Tuple[Tuple[str, bytes], ...]
) -> Tuple[Miniature, ...]:
    """Réunit les aperçus des deux origines, sans doublon, du plus grand au plus petit.

    Les offsets des aperçus du conteneur ne sont pas comparables à ceux du bloc
    TIFF — ils ne sont pas dans le même repère. On dédoublonne donc sur les
    OCTETS eux-mêmes : deux aperçus identiques le sont quels que soient les
    repères, et c'est le seul critère qui ne dépend d'aucune convention.
    """
    out = list(depuis_exif)
    vus = {m.octets for m in out}
    for origine, octets in depuis_conteneur:
        if octets in vus:
            continue
        vus.add(octets)
        out.append(Miniature(
            offset=-1, longueur=len(octets), octets=octets,
            compression=None, origine=origine,
        ))
    return tuple(sorted(out, key=lambda m: m.longueur, reverse=True))


def lire_exif(chemin_ou_donnees: Union[str, Path, bytes]) -> DonneesExif:
    """Lit l'EXIF quel que soit le conteneur : JPEG, TIFF/RAW, ou RAF.

    C'est le point d'entrée à employer. `lire_exif_depuis_jpeg` reste disponible
    pour un JPEG dont on sait qu'il en est un ; ici, le conteneur est reconnu et
    la lecture routée. Un conteneur reconnu mais non implémenté lève
    `ConteneurNonSupporte` en le NOMMANT — rendre des champs vides laisserait
    croire que le fichier n'en porte pas.
    """
    if isinstance(chemin_ou_donnees, (bytes, bytearray)):
        donnees = bytes(chemin_ou_donnees)
    else:
        donnees = Path(chemin_ou_donnees).read_bytes()

    conteneur = detecter_conteneur(donnees)
    if conteneur == "JPEG":
        # Le conteneur est inscrit ici, et nulle part ailleurs : c'est ce
        # routage qui le connaît. Une lecture directe par
        # `lire_exif_depuis_tiff` laisse donc le champ à None — elle ne sait
        # pas, et ne doit pas prétendre savoir, d'où vient le bloc.
        return replace(lire_exif_depuis_jpeg(donnees), conteneur=conteneur)
    if conteneur == "TIFF/RAW":
        # Le conteneur est reconnu comme RAW : les variantes de nombre magique
        # (RW2, ORF) sont ici légitimes, alors qu'elles ne le seraient pas dans
        # le bloc EXIF d'un JPEG.
        return replace(lire_exif_depuis_tiff(donnees, _MAGIQUES_TIFF), conteneur=conteneur)
    if conteneur == "RAF":
        jpeg = _jpeg_embarque_raf(donnees)
        if jpeg is None:
            raise MetadataError("RAF Fujifilm : le JPEG embarqué est introuvable ou tronqué.")
        return replace(lire_exif_depuis_jpeg(jpeg), conteneur=conteneur)
    if conteneur in ("CR3", "HEIC", "AVIF") or conteneur.startswith("ISO BMFF"):
        # Les conteneurs à boîtes. Le bloc EXIF qu'ils portent est un TIFF
        # ordinaire : il n'y a pas de second lecteur EXIF à écrire, seulement
        # le bon bloc à trouver.
        from .isobmff import IsobmffError, analyser_isobmff

        try:
            structure = analyser_isobmff(donnees)
        except IsobmffError as exc:
            raise ConteneurNonSupporte(
                "Conteneur %s : sa structure de boîtes est illisible (%s). L'empreinte "
                "du fichier, elle, reste valide — les deux sont indépendantes."
                % (conteneur, exc)
            ) from exc
        if structure.bloc_exif is None:
            raise ConteneurNonSupporte(
                "Conteneur %s : la structure est lue, mais elle ne porte aucun bloc EXIF "
                "localisable. Ce n'est pas la même chose qu'un fichier sans métadonnées — "
                "les items peuvent être rangés hors du fichier, ou dans une variante que "
                "ce lecteur ne couvre pas. L'empreinte, elle, reste valide." % conteneur
            )
        releve = lire_exif_depuis_tiff(structure.bloc_exif, _MAGIQUES_TIFF)
        return replace(
            releve,
            conteneur=conteneur,
            # Les aperçus du conteneur s'ajoutent à ceux de l'EXIF, en gardant
            # l'ordre du plus grand au plus petit : un HEIC porte souvent une
            # vignette JPEG que le bloc TIFF ne mentionne pas.
            previsualisations=_fusionner_apercus(releve.previsualisations, structure.apercus),
        )
    raise MetadataError(
        "Conteneur non reconnu (%s) : ni JPEG, ni TIFF/RAW, ni RAF." % conteneur
    )


def lire_exif_depuis_jpeg(chemin_ou_donnees: Union[str, Path, bytes]) -> DonneesExif:
    """Localise le segment APP1/Exif d'un JPEG et délègue à lire_exif_depuis_tiff.

    Balaie les marqueurs JPEG depuis le SOI jusqu'au premier APP1 portant l'en-tête
    « Exif\\0\\0 », ou jusqu'au SOS (début des données de balayage, au-delà duquel
    aucune métadonnée ne peut plus apparaître).
    """
    if isinstance(chemin_ou_donnees, (bytes, bytearray)):
        donnees = bytes(chemin_ou_donnees)
    else:
        donnees = Path(chemin_ou_donnees).read_bytes()

    if donnees[0:2] != b"\xff\xd8":
        raise MetadataError("Fichier non reconnu comme JPEG (SOI absent).")

    pos = 2
    while pos + 4 <= len(donnees):
        if donnees[pos] != 0xFF:
            raise MetadataError(f"Flux JPEG malformé à l'octet {pos} : marqueur attendu.")
        marqueur = donnees[pos + 1]
        if marqueur == 0xD8 or 0xD0 <= marqueur <= 0xD7:  # SOI, RSTn : pas de champ de longueur
            pos += 2
            continue
        if marqueur == 0xD9:  # EOI
            break
        if marqueur == 0xDA:  # SOS : fin des métadonnées possibles
            break
        longueur = struct.unpack_from(">H", donnees, pos + 2)[0]
        if marqueur == 0xE1 and donnees[pos + 4 : pos + 10] == b"Exif\x00\x00":
            bloc_tiff = donnees[pos + 10 : pos + 2 + longueur]
            return lire_exif_depuis_tiff(bloc_tiff)
        pos += 2 + longueur

    raise MetadataError("Aucun segment EXIF (APP1) trouvé dans ce JPEG.")


# --- §15.4 : ce qui doit être documenté — jamais None, jamais estimé ---

INDISPONIBLE = "indisponible"


def declarer(valeur, nom_champ: str):
    """Force un choix explicite : une vraie valeur, ou le sentinel INDISPONIBLE — jamais
    None, jamais une chaîne vide (§15.4 : « une information indisponible est déclarée
    indisponible, jamais estimée »)."""
    if valeur is None or valeur == "":
        raise MetadataError(
            f"« {nom_champ} » doit être renseigné ou explicitement « {INDISPONIBLE} », jamais omis."
        )
    return valeur


@dataclass(frozen=True)
class FicheGrossissement:
    """Le §15.4, littéralement : chaque poste doit être fourni — une valeur réelle, ou
    le sentinel INDISPONIBLE. Aucun champ ne peut rester non renseigné.
    """

    focale_optique_reelle: object
    focale_equivalente: object
    facteur_grossissement: object
    part_optique_vs_numerique: object
    resolution_native: object
    resolution_fichier: object
    recadrage_avant_enregistrement: object
    traitements_computationnels_actifs: object
    autre_etape_scene_vers_fichier: object

    def __post_init__(self):
        import dataclasses as _dc

        for champ in _dc.fields(self):
            declarer(getattr(self, champ.name), champ.name)


# --- §19.1 : échelle métrique par deux voies indépendantes ---


def angle_par_pixel_depuis_focale(focale_mm: float, pas_photosite_um: float) -> float:
    """Angle sous-tendu par un pixel (rad) = pas de photosite / focale réelle (§19.1, §20.1)."""
    if focale_mm <= 0 or pas_photosite_um <= 0:
        raise MetadataError("La focale et le pas de photosite doivent être strictement positifs.")
    return (pas_photosite_um * 1e-6) / (focale_mm * 1e-3)


def angle_par_pixel_depuis_reperes(hauteur_reperes_m: float, distance_m: float, separation_pixels: float) -> float:
    """Angle sous-tendu par un pixel (rad), déduit de deux repères de hauteur connue (§19.1).

    hauteur_reperes_m : distance verticale réelle entre les deux repères (donnée externe,
    jamais déduite de l'image elle-même) ; separation_pixels : leur écart mesuré sur l'image.
    """
    if hauteur_reperes_m <= 0 or distance_m <= 0 or separation_pixels <= 0:
        raise MetadataError("Hauteur de repères, distance et séparation en pixels doivent être positives.")
    angle_reperes = hauteur_reperes_m / distance_m  # angle réel sous-tendu, petit angle
    return angle_reperes / separation_pixels


@dataclass(frozen=True)
class ResultatEchelle:
    """La confrontation des deux déterminations de l'échelle (§19.1)."""

    angle_par_pixel_focale: float
    angle_par_pixel_reperes: float
    ecart_relatif: float
    focale_invalidee: bool


def verifier_coherence_echelle(
    angle_focale: float, angle_reperes: float, seuil_pourcent: float = 2.0
) -> ResultatEchelle:
    """« Un écart supérieur à 2 % entre les deux invalide la focale déclarée, non les
    repères. » (§19.1) — l'asymétrie est dans le texte, pas ajoutée ici : c'est
    `focale_invalidee`, jamais `reperes_invalides`, qui existe sur le résultat.
    """
    if angle_reperes <= 0:
        raise MetadataError("L'angle par pixel déduit des repères doit être strictement positif.")
    ecart = abs(angle_focale - angle_reperes) / angle_reperes
    return ResultatEchelle(
        angle_par_pixel_focale=angle_focale,
        angle_par_pixel_reperes=angle_reperes,
        ecart_relatif=ecart,
        focale_invalidee=(ecart * 100.0) > seuil_pourcent,
    )


# --- Position GNSS par trame NMEA 0183 ($--GGA) ---


def _checksum_nmea(corps: str) -> int:
    valeur = 0
    for caractere in corps:
        valeur ^= ord(caractere)
    return valeur


def _nmea_vers_degres(valeur: str, ref: str) -> float:
    if not valeur:
        raise MetadataError("Coordonnée NMEA manquante.")
    point = valeur.find(".")
    if point < 2:
        raise MetadataError(f"Coordonnée NMEA illisible : « {valeur} ».")
    idx_minutes = point - 2
    degres = float(valeur[:idx_minutes])
    minutes = float(valeur[idx_minutes:])
    decimal = degres + minutes / 60.0
    if ref in ("S", "W"):
        decimal = -decimal
    return decimal


@dataclass(frozen=True)
class PositionGNSS:
    """Position issue d'une trame NMEA $--GGA, avec ses indicateurs de qualité (§16.1)."""

    heure_utc: Optional[str]
    latitude_deg: float
    longitude_deg: float
    qualite_fix: int
    nb_satellites: int
    hdop: Optional[float]
    altitude_m: Optional[float]
    unite_altitude: Optional[str]
    separation_geoidale_m: Optional[float]
    source: str

    def __post_init__(self):
        if not (-90.0 <= self.latitude_deg <= 90.0):
            raise MetadataError("Latitude NMEA hors bornes [-90 ; 90].")
        if not (-180.0 <= self.longitude_deg <= 180.0):
            raise MetadataError("Longitude NMEA hors bornes [-180 ; 180].")
        if self.qualite_fix == 0:
            raise MetadataError("Trame GGA sans fix valide (qualité 0) : position non exploitable.")


def lire_trame_gga(trame: str) -> PositionGNSS:
    """Décode une trame NMEA 0183 $--GGA, checksum vérifié.

    Le HDOP transmis n'est PAS une incertitude directe : ce n'est un
    indicateur de précision qu'une fois multiplié par l'erreur de portée
    du récepteur (UERE), que la trame ne contient pas (voir
    precision_horizontale_estimee ci-dessous, à utiliser seulement si
    aucune incertitude n'est annoncée directement par le récepteur).
    """
    trame = trame.strip()
    if not trame.startswith("$"):
        raise MetadataError("Une trame NMEA doit commencer par « $ ».")
    if "*" not in trame:
        raise MetadataError("Trame NMEA sans checksum.")
    corps, reste = trame[1:].split("*", 1)
    if len(reste) < 2:
        raise MetadataError("Checksum NMEA tronqué.")
    checksum_calcule = _checksum_nmea(corps)
    try:
        checksum_declare = int(reste[:2], 16)
    except ValueError as exc:
        raise MetadataError("Checksum NMEA illisible.") from exc
    if checksum_calcule != checksum_declare:
        raise MetadataError(
            f"Checksum NMEA invalide : calculé {checksum_calcule:02X}, déclaré {reste[:2].upper()}."
        )

    champs = corps.split(",")
    if len(champs) < 13 or not champs[0].endswith("GGA"):
        raise MetadataError("Trame non reconnue comme une trame GGA.")

    heure_utc = champs[1] or None
    latitude = _nmea_vers_degres(champs[2], champs[3])
    longitude = _nmea_vers_degres(champs[4], champs[5])
    qualite_fix = int(champs[6]) if champs[6] else 0
    nb_satellites = int(champs[7]) if champs[7] else 0
    hdop = float(champs[8]) if champs[8] else None
    altitude_m = float(champs[9]) if champs[9] else None
    unite_altitude = champs[10] or None
    separation_geoidale_m = float(champs[11]) if champs[11] else None

    return PositionGNSS(
        heure_utc=heure_utc,
        latitude_deg=latitude,
        longitude_deg=longitude,
        qualite_fix=qualite_fix,
        nb_satellites=nb_satellites,
        hdop=hdop,
        altitude_m=altitude_m,
        unite_altitude=unite_altitude,
        separation_geoidale_m=separation_geoidale_m,
        source="trame NMEA GGA",
    )


def precision_horizontale_estimee(hdop: float, erreur_portee_recepteur_m: float) -> float:
    """Estimation grossière : HDOP × UERE (erreur de portée du récepteur, propre à
    l'appareil, jamais déduite du HDOP seul). À n'utiliser que si le récepteur
    n'annonce pas directement une incertitude (§16.1 la préfère quand elle existe).
    """
    if hdop <= 0 or erreur_portee_recepteur_m <= 0:
        raise MetadataError("Le HDOP et l'erreur de portée doivent être strictement positifs.")
    return hdop * erreur_portee_recepteur_m
