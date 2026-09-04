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
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

__all__ = [
    "MetadataError",
    "PositionGPS",
    "DonneesExif",
    "lire_exif_depuis_tiff",
    "lire_exif_depuis_jpeg",
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


def _lire_ifd(donnees: bytes, offset: int, endian: str) -> Dict[int, object]:
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
    return entrees


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


def lire_exif_depuis_tiff(donnees: bytes) -> DonneesExif:
    """Lit un bloc TIFF/EXIF brut (en-tête « II » ou « MM ») et en extrait les champs utiles.

    N'implémente pas la norme TIFF/EXIF entière : seulement IFD0, le sous-IFD Exif et
    le sous-IFD GPS, et seulement les tags listés en tête de module. Un tag absent
    donne un champ à None, jamais une exception.
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
    if magique != 42:
        raise MetadataError(f"En-tête TIFF invalide : nombre magique {magique} != 42.")
    offset_ifd0 = struct.unpack_from(endian + "I", donnees, 4)[0]

    ifd0 = _lire_ifd(donnees, offset_ifd0, endian)
    ifd_exif = _lire_ifd(donnees, ifd0[_TAG_EXIF_IFD_POINTER], endian) if _TAG_EXIF_IFD_POINTER in ifd0 else {}
    ifd_gps = _lire_ifd(donnees, ifd0[_TAG_GPS_IFD_POINTER], endian) if _TAG_GPS_IFD_POINTER in ifd0 else {}

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
