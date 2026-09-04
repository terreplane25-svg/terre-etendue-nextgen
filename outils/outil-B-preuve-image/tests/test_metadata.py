"""
Tests de metadata.py — lecteur EXIF/TIFF (round-trip sur fixtures binaires
construites ici même), échelle métrique du §19.1, discipline de déclaration
du §15.4, et lecteur de trames NMEA $--GGA (§16.1).
"""

import struct

import pytest

from preuve_image.metadata import (
    DonneesExif,
    FicheGrossissement,
    INDISPONIBLE,
    MetadataError,
    PositionGNSS,
    PositionGPS,
    ResultatEchelle,
    angle_par_pixel_depuis_focale,
    angle_par_pixel_depuis_reperes,
    declarer,
    lire_exif_depuis_jpeg,
    lire_exif_depuis_tiff,
    lire_trame_gga,
    precision_horizontale_estimee,
    verifier_coherence_echelle,
)
from preuve_image.metadata import (
    _TAG_DATETIME_ORIGINAL,
    _TAG_EXIF_IFD_POINTER,
    _TAG_EXPOSURE_TIME,
    _TAG_FNUMBER,
    _TAG_FOCAL_LENGTH,
    _TAG_FOCAL_LENGTH_35MM,
    _TAG_GPS_ALT,
    _TAG_GPS_ALT_REF,
    _TAG_GPS_H_POSITIONING_ERROR,
    _TAG_GPS_IFD_POINTER,
    _TAG_GPS_LAT,
    _TAG_GPS_LAT_REF,
    _TAG_GPS_LON,
    _TAG_GPS_LON_REF,
    _TAG_ISO_SPEED,
    _TAG_LENS_MODEL,
    _TAG_MAKE,
    _TAG_MODEL,
    _TAG_ORIENTATION,
    _TAG_PIXEL_X_DIMENSION,
    _TAG_PIXEL_Y_DIMENSION,
)


# --- Constructeur TIFF/EXIF minimal, réservé aux tests -----------------------
#
# Le protocole veut un lecteur EXIF « écrit ici plutôt qu'emprunté » (docstring
# du module) ; par symétrie, on ne le vérifie pas contre une bibliothèque
# tierce mais contre des flux d'octets qu'on assemble soi-même, champ par
# champ, selon TIFF 6.0 §2. Chaque fonction ci-dessous encode un seul type
# TIFF ; construire_tiff() place les IFD (0, Exif, GPS) les uns après les
# autres et calcule leurs offsets — la seule arithmétique qu'un test manuel
# aurait dû refaire à la main.

def campo_ascii(valeur: str):
    brut = valeur.encode("ascii") + b"\x00"
    return (2, len(brut), brut)


def campo_short(*valeurs):
    return (3, len(valeurs), b"".join(struct.pack("<H", v) for v in valeurs))


def campo_long(*valeurs):
    return (4, len(valeurs), b"".join(struct.pack("<I", v) for v in valeurs))


def campo_rational(*paires):
    brut = b"".join(struct.pack("<2I", num, den) for num, den in paires)
    return (5, len(paires), brut)


def campo_byte(*valeurs):
    return (1, len(valeurs), bytes(valeurs))


def _serialiser_ifd(entrees: dict, offset_depart: int):
    items = sorted(entrees.items())
    taille_entete = 2 + 12 * len(items) + 4
    debut_debordement = offset_depart + taille_entete
    morceaux = [struct.pack("<H", len(items))]
    debordement = bytearray()
    for tag, (type_, count, brut) in items:
        entree = struct.pack("<HHI", tag, type_, count)
        if len(brut) <= 4:
            champ_valeur = brut + b"\x00" * (4 - len(brut))
        else:
            decalage = debut_debordement + len(debordement)
            champ_valeur = struct.pack("<I", decalage)
            debordement.extend(brut)
        morceaux.append(entree + champ_valeur)
    morceaux.append(struct.pack("<I", 0))  # pas d'IFD suivant
    return b"".join(morceaux), bytes(debordement)


def construire_tiff(entrees_ifd0: dict, entrees_exif: dict = None, entrees_gps: dict = None) -> bytes:
    entrees_ifd0 = dict(entrees_ifd0)
    if entrees_exif is not None:
        entrees_ifd0[_TAG_EXIF_IFD_POINTER] = campo_long(0)
    if entrees_gps is not None:
        entrees_ifd0[_TAG_GPS_IFD_POINTER] = campo_long(0)

    ifd0_octets, ifd0_debordement = _serialiser_ifd(entrees_ifd0, 8)
    apres_ifd0 = 8 + len(ifd0_octets) + len(ifd0_debordement)

    exif_octets = exif_debordement = b""
    offset_exif = None
    apres_exif = apres_ifd0
    if entrees_exif is not None:
        offset_exif = apres_ifd0
        exif_octets, exif_debordement = _serialiser_ifd(entrees_exif, offset_exif)
        apres_exif = offset_exif + len(exif_octets) + len(exif_debordement)

    gps_octets = gps_debordement = b""
    offset_gps = None
    if entrees_gps is not None:
        offset_gps = apres_exif
        gps_octets, gps_debordement = _serialiser_ifd(entrees_gps, offset_gps)

    if offset_exif is not None:
        entrees_ifd0[_TAG_EXIF_IFD_POINTER] = campo_long(offset_exif)
    if offset_gps is not None:
        entrees_ifd0[_TAG_GPS_IFD_POINTER] = campo_long(offset_gps)
    ifd0_octets, ifd0_debordement = _serialiser_ifd(entrees_ifd0, 8)  # tailles inchangées (valeurs inline)

    flux = b"II" + struct.pack("<H", 42) + struct.pack("<I", 8)
    flux += ifd0_octets + ifd0_debordement
    flux += exif_octets + exif_debordement
    flux += gps_octets + gps_debordement
    return flux


def _fixture_complete() -> bytes:
    ifd0 = {
        _TAG_MAKE: campo_ascii("Canon"),
        _TAG_MODEL: campo_ascii("EOS R5"),
        _TAG_ORIENTATION: campo_short(1),
    }
    exif = {
        _TAG_FOCAL_LENGTH: campo_rational((2400, 100)),
        _TAG_FOCAL_LENGTH_35MM: campo_short(24),
        _TAG_FNUMBER: campo_rational((280, 100)),
        _TAG_EXPOSURE_TIME: campo_rational((1, 500)),
        _TAG_ISO_SPEED: campo_short(200),
        _TAG_PIXEL_X_DIMENSION: campo_long(6000),
        _TAG_PIXEL_Y_DIMENSION: campo_long(4000),
        _TAG_DATETIME_ORIGINAL: campo_ascii("2026:09:03 10:15:00"),
        _TAG_LENS_MODEL: campo_ascii("RF24-105mm F4 L IS USM"),
    }
    gps = {
        _TAG_GPS_LAT_REF: campo_ascii("N"),
        _TAG_GPS_LAT: campo_rational((48, 1), (51, 1), (30, 1)),
        _TAG_GPS_LON_REF: campo_ascii("E"),
        _TAG_GPS_LON: campo_rational((2, 1), (21, 1), (3, 1)),
        _TAG_GPS_ALT_REF: campo_byte(0),
        _TAG_GPS_ALT: campo_rational((35, 1)),
        _TAG_GPS_H_POSITIONING_ERROR: campo_rational((5, 1)),
    }
    return construire_tiff(ifd0, exif, gps)


# --- lire_exif_depuis_tiff ---

def test_lire_exif_depuis_tiff_champs_ifd0_et_exif():
    d = lire_exif_depuis_tiff(_fixture_complete())
    assert isinstance(d, DonneesExif)
    assert d.fabricant == "Canon"
    assert d.modele == "EOS R5"
    assert d.orientation == 1
    assert d.objectif == "RF24-105mm F4 L IS USM"
    assert d.focale_mm == pytest.approx(24.0)
    assert d.focale_equivalente_35mm == 24
    assert d.ouverture == pytest.approx(2.8)
    assert d.temps_pose_s == pytest.approx(0.002)
    assert d.sensibilite_iso == 200
    assert d.largeur_px == 6000
    assert d.hauteur_px == 4000
    assert d.date_heure_original == "2026:09:03 10:15:00"


def test_lire_exif_depuis_tiff_position_gps():
    d = lire_exif_depuis_tiff(_fixture_complete())
    assert isinstance(d.gps, PositionGPS)
    assert d.gps.latitude_deg == pytest.approx(48.0 + 51 / 60.0 + 30 / 3600.0)
    assert d.gps.longitude_deg == pytest.approx(2.0 + 21 / 60.0 + 3 / 3600.0)
    assert d.gps.altitude_m == pytest.approx(35.0)
    assert d.gps.incertitude_m == pytest.approx(5.0)
    assert d.gps.source == "EXIF GPS IFD"


def test_lire_exif_depuis_tiff_gps_sud_ouest_et_altitude_negative():
    gps = {
        _TAG_GPS_LAT_REF: campo_ascii("S"),
        _TAG_GPS_LAT: campo_rational((33, 1), (51, 1), (36, 1)),
        _TAG_GPS_LON_REF: campo_ascii("W"),
        _TAG_GPS_LON: campo_rational((70, 1), (39, 1), (0, 1)),
        _TAG_GPS_ALT_REF: campo_byte(1),  # 1 = au-dessous du niveau de la mer
        _TAG_GPS_ALT: campo_rational((10, 1)),
    }
    tiff = construire_tiff({_TAG_MAKE: campo_ascii("Sony")}, entrees_gps=gps)
    d = lire_exif_depuis_tiff(tiff)
    assert d.gps.latitude_deg < 0
    assert d.gps.longitude_deg < 0
    assert d.gps.altitude_m == pytest.approx(-10.0)
    assert d.gps.incertitude_m is None  # HPositioningError non écrit par ce boîtier


def test_lire_exif_depuis_tiff_ifd0_seul_sans_exif_ni_gps():
    tiff = construire_tiff({_TAG_MAKE: campo_ascii("Nikon"), _TAG_MODEL: campo_ascii("Z9")})
    d = lire_exif_depuis_tiff(tiff)
    assert d.fabricant == "Nikon"
    assert d.modele == "Z9"
    assert d.objectif is None  # pas de sous-IFD Exif : champ absent, pas une exception
    assert d.gps is None
    assert d.focale_mm is None


def _serialiser_ifd_be(entrees: dict, offset_depart: int):
    # Même logique que _serialiser_ifd, mais en gros-boutiste (marqueur « MM ») —
    # pour vérifier que lire_exif_depuis_tiff gère les deux boutismes symétriquement.
    items = sorted(entrees.items())
    taille_entete = 2 + 12 * len(items) + 4
    debut_debordement = offset_depart + taille_entete
    morceaux = [struct.pack(">H", len(items))]
    debordement = bytearray()
    for tag, (type_, count, brut) in items:
        entree = struct.pack(">HHI", tag, type_, count)
        if len(brut) <= 4:
            champ_valeur = brut + b"\x00" * (4 - len(brut))
        else:
            decalage = debut_debordement + len(debordement)
            champ_valeur = struct.pack(">I", decalage)
            debordement.extend(brut)
        morceaux.append(entree + champ_valeur)
    morceaux.append(struct.pack(">I", 0))
    return b"".join(morceaux), bytes(debordement)


def test_lire_exif_depuis_tiff_endian_big_endian_mm():
    # On rejoue une fixture minimale en gros-boutiste pour vérifier que le marqueur
    # « MM » et les décodages struct.unpack_from(">...") fonctionnent symétriquement à "II".
    exif_be = {_TAG_FOCAL_LENGTH: (5, 1, struct.pack(">2I", 500, 10))}  # RATIONAL 500/10 = 50.0
    # campo_long() emballe toujours en petit-boutiste : pour le pointeur de sous-IFD,
    # qui doit être lu comme un LONG gros-boutiste ici, on emballe la valeur nous-mêmes.
    ifd0_be = {_TAG_MAKE: campo_ascii("Pentax"), _TAG_EXIF_IFD_POINTER: (4, 1, struct.pack(">I", 0))}

    ifd0_octets, ifd0_deb = _serialiser_ifd_be(ifd0_be, 8)
    offset_exif = 8 + len(ifd0_octets) + len(ifd0_deb)
    ifd0_be[_TAG_EXIF_IFD_POINTER] = (4, 1, struct.pack(">I", offset_exif))
    ifd0_octets, ifd0_deb = _serialiser_ifd_be(ifd0_be, 8)
    exif_octets, exif_deb = _serialiser_ifd_be(exif_be, offset_exif)

    flux = b"MM" + struct.pack(">H", 42) + struct.pack(">I", 8)
    flux += ifd0_octets + ifd0_deb + exif_octets + exif_deb

    d = lire_exif_depuis_tiff(flux)
    assert d.fabricant == "Pentax"
    assert d.focale_mm == pytest.approx(50.0)


def test_lire_exif_depuis_tiff_rejette_entete_invalide():
    with pytest.raises(MetadataError, match="II.*MM|en-tête"):
        lire_exif_depuis_tiff(b"XX" + b"\x00" * 20)


def test_lire_exif_depuis_tiff_rejette_nombre_magique_invalide():
    flux = b"II" + struct.pack("<H", 43) + struct.pack("<I", 8) + b"\x00" * 10
    with pytest.raises(MetadataError, match="magique"):
        lire_exif_depuis_tiff(flux)


def test_lire_exif_depuis_tiff_rejette_flux_trop_court():
    with pytest.raises(MetadataError):
        lire_exif_depuis_tiff(b"II*\x00")


def test_lire_exif_depuis_tiff_rejette_ifd_tronque():
    # IFD0 annonce 5 entrées mais le flux s'arrête après la première
    flux = b"II" + struct.pack("<H", 42) + struct.pack("<I", 8)
    flux += struct.pack("<H", 5) + struct.pack("<HHI", _TAG_MAKE, 2, 1) + b"A\x00\x00\x00"
    with pytest.raises(MetadataError):
        lire_exif_depuis_tiff(flux)


# --- lire_exif_depuis_jpeg ---

def _envelopper_en_jpeg(tiff_bytes: bytes) -> bytes:
    charge = b"Exif\x00\x00" + tiff_bytes
    longueur = 2 + len(charge)
    return b"\xff\xd8" + b"\xff\xe1" + struct.pack(">H", longueur) + charge + b"\xff\xd9"


def test_lire_exif_depuis_jpeg_octets():
    jpeg = _envelopper_en_jpeg(_fixture_complete())
    d = lire_exif_depuis_jpeg(jpeg)
    assert d.fabricant == "Canon"
    assert d.gps.altitude_m == pytest.approx(35.0)


def test_lire_exif_depuis_jpeg_fichier(tmp_path):
    jpeg = _envelopper_en_jpeg(_fixture_complete())
    chemin = tmp_path / "photo.jpg"
    chemin.write_bytes(jpeg)
    d = lire_exif_depuis_jpeg(chemin)
    assert d.modele == "EOS R5"


def test_lire_exif_depuis_jpeg_avec_segments_avant_app1():
    # Un APP0 (JFIF) quelconque précède l'APP1/Exif — le parseur doit le sauter.
    app0 = b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + b"\x00" * 9
    jpeg = b"\xff\xd8" + app0 + _envelopper_en_jpeg(_fixture_complete())[2:]
    d = lire_exif_depuis_jpeg(jpeg)
    assert d.fabricant == "Canon"


def test_lire_exif_depuis_jpeg_rejette_non_jpeg():
    with pytest.raises(MetadataError, match="SOI"):
        lire_exif_depuis_jpeg(b"pas un jpeg du tout")


def test_lire_exif_depuis_jpeg_sans_segment_exif():
    jpeg = b"\xff\xd8" + b"\xff\xda" + b"\x00\x02"  # SOS immédiat, aucune métadonnée possible
    with pytest.raises(MetadataError, match="Aucun segment EXIF"):
        lire_exif_depuis_jpeg(jpeg)


# --- §15.4 : declarer() et FicheGrossissement ---

def test_declarer_accepte_valeur_reelle_et_sentinel():
    assert declarer("50mm f/1.4", "objectif") == "50mm f/1.4"
    assert declarer(INDISPONIBLE, "objectif") == INDISPONIBLE


def test_declarer_rejette_none_et_chaine_vide():
    with pytest.raises(MetadataError, match="objectif"):
        declarer(None, "objectif")
    with pytest.raises(MetadataError, match="objectif"):
        declarer("", "objectif")


def test_declarer_accepte_zero_et_false_comme_valeurs_reelles():
    # 0 et False sont des valeurs réelles renseignées, pas des absences (piège classique
    # d'un test « if not valeur » — declarer() teste bien « is None or == "" »).
    assert declarer(0, "part_optique_vs_numerique") == 0
    assert declarer(False, "recadrage_avant_enregistrement") is False


def test_fiche_grossissement_complete_ne_leve_pas():
    fiche = FicheGrossissement(
        focale_optique_reelle=105.0,
        focale_equivalente=105.0,
        facteur_grossissement=1.0,
        part_optique_vs_numerique="100% optique",
        resolution_native=(6000, 4000),
        resolution_fichier=(6000, 4000),
        recadrage_avant_enregistrement=False,
        traitements_computationnels_actifs=INDISPONIBLE,
        autre_etape_scene_vers_fichier=INDISPONIBLE,
    )
    assert fiche.traitements_computationnels_actifs == INDISPONIBLE


def test_fiche_grossissement_rejette_un_champ_omis():
    with pytest.raises(MetadataError, match="autre_etape_scene_vers_fichier"):
        FicheGrossissement(
            focale_optique_reelle=105.0,
            focale_equivalente=105.0,
            facteur_grossissement=1.0,
            part_optique_vs_numerique="100% optique",
            resolution_native=(6000, 4000),
            resolution_fichier=(6000, 4000),
            recadrage_avant_enregistrement=False,
            traitements_computationnels_actifs=INDISPONIBLE,
            autre_etape_scene_vers_fichier=None,
        )


# --- §19.1 : échelle métrique ---

def test_angle_par_pixel_depuis_focale():
    # Capteur 4.4 µm, focale 600 mm
    angle = angle_par_pixel_depuis_focale(focale_mm=600.0, pas_photosite_um=4.4)
    assert angle == pytest.approx((4.4e-6) / (600e-3))


def test_angle_par_pixel_depuis_focale_domaine_invalide():
    with pytest.raises(MetadataError):
        angle_par_pixel_depuis_focale(focale_mm=0.0, pas_photosite_um=4.4)
    with pytest.raises(MetadataError):
        angle_par_pixel_depuis_focale(focale_mm=600.0, pas_photosite_um=-1.0)


def test_angle_par_pixel_depuis_reperes():
    # Deux repères réels séparés de 20 m, à 15 km, séparés de 500 px sur l'image
    angle = angle_par_pixel_depuis_reperes(hauteur_reperes_m=20.0, distance_m=15000.0, separation_pixels=500.0)
    assert angle == pytest.approx((20.0 / 15000.0) / 500.0)


def test_angle_par_pixel_depuis_reperes_domaine_invalide():
    with pytest.raises(MetadataError):
        angle_par_pixel_depuis_reperes(hauteur_reperes_m=0.0, distance_m=15000.0, separation_pixels=500.0)


def test_verifier_coherence_echelle_dans_la_tolerance():
    angle_focale = 1.0e-5
    angle_reperes = 1.005e-5  # 0.5 % d'écart
    resultat = verifier_coherence_echelle(angle_focale, angle_reperes)
    assert isinstance(resultat, ResultatEchelle)
    assert resultat.focale_invalidee is False
    assert resultat.ecart_relatif == pytest.approx(abs(angle_focale - angle_reperes) / angle_reperes)


def test_verifier_coherence_echelle_hors_tolerance_invalide_la_focale():
    angle_focale = 1.10e-5
    angle_reperes = 1.00e-5  # 10 % d'écart
    resultat = verifier_coherence_echelle(angle_focale, angle_reperes)
    assert resultat.focale_invalidee is True
    # L'asymétrie du §19.1 est dans la forme du résultat lui-même : jamais de champ
    # « reperes_invalides » — seuls les repères externes font foi en cas de désaccord.
    assert not hasattr(resultat, "reperes_invalides")


def test_verifier_coherence_echelle_seuil_personnalise():
    angle_focale = 1.03e-5
    angle_reperes = 1.00e-5  # 3 %
    assert verifier_coherence_echelle(angle_focale, angle_reperes, seuil_pourcent=2.0).focale_invalidee is True
    assert verifier_coherence_echelle(angle_focale, angle_reperes, seuil_pourcent=5.0).focale_invalidee is False


def test_verifier_coherence_echelle_rejette_angle_reperes_non_positif():
    with pytest.raises(MetadataError):
        verifier_coherence_echelle(1.0e-5, 0.0)


# --- NMEA 0183 $--GGA ---

_TRAME_EXEMPLE = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"


def test_lire_trame_gga_exemple_de_reference():
    position = lire_trame_gga(_TRAME_EXEMPLE)
    assert isinstance(position, PositionGNSS)
    assert position.heure_utc == "123519"
    assert position.latitude_deg == pytest.approx(48.0 + 7.038 / 60.0)
    assert position.longitude_deg == pytest.approx(11.0 + 31.000 / 60.0)
    assert position.qualite_fix == 1
    assert position.nb_satellites == 8
    assert position.hdop == pytest.approx(0.9)
    assert position.altitude_m == pytest.approx(545.4)
    assert position.unite_altitude == "M"
    assert position.separation_geoidale_m == pytest.approx(46.9)
    assert position.source == "trame NMEA GGA"


def test_lire_trame_gga_hemispheres_sud_ouest():
    # Même trame que la référence mais recalculée pour S/W (checksum ré-émis).
    corps = "GPGGA,123519,4807.038,S,01131.000,W,1,08,0.9,545.4,M,46.9,M,,"
    checksum = 0
    for caractere in corps:
        checksum ^= ord(caractere)
    trame = f"${corps}*{checksum:02X}"
    position = lire_trame_gga(trame)
    assert position.latitude_deg < 0
    assert position.longitude_deg < 0


def test_lire_trame_gga_rejette_checksum_invalide():
    trame = _TRAME_EXEMPLE[:-2] + "00"
    with pytest.raises(MetadataError, match="[Cc]hecksum"):
        lire_trame_gga(trame)


def test_lire_trame_gga_rejette_absence_de_dollar():
    with pytest.raises(MetadataError, match=r"\$"):
        lire_trame_gga("GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47")


def test_lire_trame_gga_rejette_fix_invalide():
    corps = "GPGGA,123519,4807.038,N,01131.000,E,0,00,,,,,,,"
    checksum = 0
    for caractere in corps:
        checksum ^= ord(caractere)
    trame = f"${corps}*{checksum:02X}"
    with pytest.raises(MetadataError, match="fix"):
        lire_trame_gga(trame)


def test_lire_trame_gga_rejette_sentence_non_gga():
    corps = "GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1,"
    checksum = 0
    for caractere in corps:
        checksum ^= ord(caractere)
    trame = f"${corps}*{checksum:02X}"
    with pytest.raises(MetadataError, match="GGA"):
        lire_trame_gga(trame)


def test_precision_horizontale_estimee():
    assert precision_horizontale_estimee(hdop=0.9, erreur_portee_recepteur_m=5.0) == pytest.approx(4.5)


def test_precision_horizontale_estimee_domaine_invalide():
    with pytest.raises(MetadataError):
        precision_horizontale_estimee(hdop=0.0, erreur_portee_recepteur_m=5.0)
