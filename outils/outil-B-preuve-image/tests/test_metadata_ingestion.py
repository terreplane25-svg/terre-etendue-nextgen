"""
Champs EXIF ajoutés pour l'ingestion, et miniature de l'IFD1.

Les fixtures sont de deux natures, délibérément :

  · un TIFF construit octet par octet dans ce fichier, quand il s'agit de
    vérifier une structure que Pillow n'écrit pas — l'IFD1 en particulier ;
  · un JPEG produit par Pillow, quand il s'agit de vérifier qu'on lit bien ce
    qu'un ÉCRIVAIN INDÉPENDANT a écrit. C'est le contrôle croisé qui a valeur :
    deux implémentations qui se rencontrent, dont une seule est la nôtre.
"""

import struct
from io import BytesIO

import pytest
from PIL import Image
from PIL.TiffImagePlugin import IFDRational

from preuve_image.metadata import (
    MetadataError,
    decrire_flash,
    lire_exif_depuis_jpeg,
    lire_exif_depuis_tiff,
)

# ─────────────────────────────────────────────────────────────────────────────
# TIFF construit à la main, pour l'IFD1
# ─────────────────────────────────────────────────────────────────────────────

MINIATURE_JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 40 + b"\xff\xd9"


def entree(tag: int, type_: int, count: int, valeur: bytes) -> bytes:
    """Une entrée d'IFD : tag, type, nombre, et 4 octets de valeur ou d'offset."""
    return struct.pack("<HHI", tag, type_, count) + valeur.ljust(4, b"\x00")[:4]


def tiff_avec_miniature(offset_faux: bool = False) -> bytes:
    """TIFF petit-boutiste : IFD0 minimal, puis IFD1 décrivant une miniature JPEG.

    Les offsets sont calculés à la main pour que la structure soit exactement
    celle qu'un appareil écrit — et pour que le test échoue si le lecteur
    devine au lieu de suivre le chaînage.
    """
    entete = b"II" + struct.pack("<HI", 42, 8)

    ifd0_entrees = [
        entree(0x010F, 2, 6, b""),          # Make, valeur hors ligne
        entree(0x0131, 2, 8, b""),          # Software, hors ligne
    ]
    # IFD0 : 2 octets de compte + n×12 + 4 octets de pointeur suivant.
    debut_ifd0 = 8
    taille_ifd0 = 2 + 12 * len(ifd0_entrees) + 4
    debut_ifd1 = debut_ifd0 + taille_ifd0

    ifd1_entrees = [
        entree(0x0103, 3, 1, struct.pack("<H", 6)),   # Compression = JPEG
        entree(0x0201, 4, 1, b""),                     # offset de la miniature
        entree(0x0202, 4, 1, struct.pack("<I", len(MINIATURE_JPEG))),
    ]
    taille_ifd1 = 2 + 12 * len(ifd1_entrees) + 4
    debut_donnees = debut_ifd1 + taille_ifd1

    make = b"Essai\x00"
    software = b"Banc 1.0"
    offset_make = debut_donnees
    offset_software = offset_make + len(make)
    offset_miniature = offset_software + len(software)
    if offset_faux:
        offset_miniature = 999_999  # hors du flux : la miniature doit être refusée

    ifd0_entrees[0] = entree(0x010F, 2, len(make), struct.pack("<I", offset_make))
    ifd0_entrees[1] = entree(0x0131, 2, len(software), struct.pack("<I", offset_software))
    ifd1_entrees[1] = entree(0x0201, 4, 1, struct.pack("<I", offset_miniature))

    bloc = (
        entete
        + struct.pack("<H", len(ifd0_entrees)) + b"".join(ifd0_entrees)
        + struct.pack("<I", debut_ifd1)
        + struct.pack("<H", len(ifd1_entrees)) + b"".join(ifd1_entrees)
        + struct.pack("<I", 0)
        + make + software + MINIATURE_JPEG
    )
    return bloc


def test_miniature_extraite_de_l_ifd1():
    e = lire_exif_depuis_tiff(tiff_avec_miniature())
    assert e.miniature is not None
    assert e.miniature.longueur == len(MINIATURE_JPEG)
    assert e.miniature.octets == MINIATURE_JPEG
    assert e.miniature.est_jpeg is True
    assert e.miniature.compression == 6


def test_miniature_a_offset_incoherent_refusee():
    """Une miniature dont l'offset sort du flux n'est pas rendue tronquée.

    Rendre les octets disponibles jusqu'à la fin du fichier donnerait une
    vignette d'apparence normale, mais qui n'est pas celle que l'appareil a
    écrite. Mieux vaut rien qu'un artefact.
    """
    e = lire_exif_depuis_tiff(tiff_avec_miniature(offset_faux=True))
    assert e.miniature is None


def test_ifd0_lu_malgre_l_ifd1():
    e = lire_exif_depuis_tiff(tiff_avec_miniature())
    assert e.fabricant == "Essai"
    assert e.logiciel == "Banc 1.0"


def test_absence_d_ifd1_ne_leve_pas():
    entete = b"II" + struct.pack("<HI", 42, 8)
    bloc = entete + struct.pack("<H", 0) + struct.pack("<I", 0)
    e = lire_exif_depuis_tiff(bloc)
    assert e.miniature is None
    assert e.fabricant is None


def test_ifd1_malforme_ne_fait_pas_perdre_l_ifd0():
    """Un IFD1 qui pointe n'importe où ne doit pas emporter la lecture des champs."""
    entete = b"II" + struct.pack("<HI", 42, 8)
    e0 = entree(0x010F, 2, 6, struct.pack("<I", 8 + 2 + 12 + 4))
    bloc = (entete + struct.pack("<H", 1) + e0 + struct.pack("<I", 5)  # IFD1 à l'octet 5 : absurde
            + b"Essai\x00")
    e = lire_exif_depuis_tiff(bloc)
    assert e.fabricant == "Essai"
    assert e.miniature is None


# ─────────────────────────────────────────────────────────────────────────────
# JPEG écrit par Pillow : contrôle croisé sur les champs d'ingestion
# ─────────────────────────────────────────────────────────────────────────────


def jpeg_complet() -> bytes:
    img = Image.new("RGB", (64, 48), (20, 30, 40))
    exif = Image.Exif()
    exif[0x010F] = "EssaiCorp"
    exif[0x0110] = "Modele X"
    exif[0x0131] = "Retoucheur 2.4"
    exif[0x0132] = "2026:09:05 11:02:33"
    exif[0x013B] = "A. Photographe"
    exif[0x8298] = "Tous droits reserves"
    exif[0x011A] = IFDRational(300, 1)
    exif[0x011B] = IFDRational(300, 1)
    exif[0x0128] = 2  # pouce
    exif[0x0100] = 64
    exif[0x0101] = 48
    sous = exif.get_ifd(0x8769)
    sous[0x9003] = "2026:09:05 10:14:22"
    sous[0x9004] = "2026:09:05 10:14:25"
    sous[0x8822] = 2      # programme normal
    sous[0x9209] = 0x19   # déclenché, mode obligatoire
    sous[0xA001] = 1      # sRGB
    sous[0xA402] = 1      # manuel
    sous[0xA403] = 0      # automatique
    sous[0xA404] = IFDRational(2, 1)
    sous[0xA406] = 1      # paysage
    sous[0x8827] = 200
    sous[0x829D] = IFDRational(28, 10)
    sous[0x829A] = IFDRational(1, 250)
    sous[0x920A] = IFDRational(24, 1)
    sous[0xA405] = 36
    sous[0xA002] = 64
    sous[0xA003] = 48
    tampon = BytesIO()
    img.save(tampon, format="JPEG", exif=exif)
    return tampon.getvalue()


@pytest.fixture(scope="module")
def exif():
    return lire_exif_depuis_jpeg(jpeg_complet())


def test_appareil_et_logiciel(exif):
    assert exif.fabricant == "EssaiCorp"
    assert exif.modele == "Modele X"
    assert exif.logiciel == "Retoucheur 2.4"
    assert exif.artiste == "A. Photographe"
    assert exif.droits == "Tous droits reserves"


def test_horodatages(exif):
    assert exif.date_heure_original == "2026:09:05 10:14:22"
    assert exif.date_heure_numerisation == "2026:09:05 10:14:25"
    assert exif.date_heure_modification == "2026:09:05 11:02:33"


def test_prise_de_vue(exif):
    assert exif.sensibilite_iso == 200
    assert exif.ouverture == pytest.approx(2.8)
    assert exif.temps_pose_s == pytest.approx(1 / 250)
    assert exif.focale_mm == pytest.approx(24.0)
    assert exif.focale_equivalente_35mm == 36


def test_resolution_convertie_en_dpi(exif):
    assert exif.resolution_x == pytest.approx(300.0)
    assert exif.unite_resolution == 2
    assert exif.unite_resolution_libelle == "pouce"
    assert exif.dpi_x == pytest.approx(300.0)
    assert exif.dpi_y == pytest.approx(300.0)


def test_dpi_en_centimetres():
    """Unité 3 : 300 points par centimètre valent 762 par pouce."""
    from preuve_image.metadata import _dpi
    assert _dpi(300.0, 3) == pytest.approx(762.0)


def test_unite_sans_dimension_ne_donne_pas_de_dpi():
    """Unité 1 : le nombre est un rapport d'aspect, pas une densité.

    Le convertir en DPI reviendrait à inventer une grandeur que le fichier ne
    porte pas — c'est exactement ce que le §15.4 interdit.
    """
    from preuve_image.metadata import _dpi
    assert _dpi(72.0, 1) is None
    assert _dpi(None, 2) is None
    assert _dpi(0.0, 2) is None


def test_codes_et_libelles_rendus_ensemble(exif):
    assert exif.espace_colorimetrique == 1
    assert exif.espace_colorimetrique_libelle == "sRGB"
    assert exif.mode_exposition == 1
    assert exif.mode_exposition_libelle == "manuel"
    assert exif.programme_exposition == 2
    assert exif.programme_exposition_libelle == "programme normal"
    assert exif.balance_blancs == 0
    assert exif.balance_blancs_libelle == "automatique"
    assert exif.type_scene == 1
    assert exif.type_scene_libelle == "paysage"


def test_zoom_numerique_lu(exif):
    """Le §15 en dépend : le rapport dit ce que l'agrandissement doit à l'optique."""
    assert exif.rapport_zoom_numerique == pytest.approx(2.0)
    assert exif.zoom_numerique_applique is True


def test_zoom_numerique_nul_signifie_non_utilise():
    """0 est le code « non employé » de la norme, pas un rapport de zéro."""
    from preuve_image.metadata import DonneesExif
    e = DonneesExif(
        fabricant=None, modele=None, objectif=None, focale_mm=None,
        focale_equivalente_35mm=None, ouverture=None, temps_pose_s=None,
        sensibilite_iso=None, largeur_px=None, hauteur_px=None,
        date_heure_original=None, orientation=None, gps=None,
        rapport_zoom_numerique=0.0,
    )
    assert e.zoom_numerique_applique is False


# ─────────────────────────────────────────────────────────────────────────────
# Flash : un champ de bits, pas un code
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("code,attendus", [
    (0x00, ["non déclenché"]),
    (0x01, ["déclenché"]),
    (0x05, ["déclenché", "lumière de retour non détectée"]),
    (0x07, ["déclenché", "lumière de retour détectée"]),
    (0x09, ["déclenché", "mode obligatoire"]),
    (0x10, ["non déclenché", "mode supprimé"]),
    (0x19, ["déclenché", "mode automatique"]),
    (0x41, ["déclenché", "anti-yeux rouges"]),
])
def test_flash_decode_bit_a_bit(code, attendus):
    libelle = decrire_flash(code)
    for morceau in attendus:
        assert morceau in libelle


def test_flash_absent_de_l_appareil():
    """Bit 5 : l'appareil n'a pas de flash. Ce n'est pas « non déclenché »."""
    assert decrire_flash(0x20) == "l'appareil n'a pas de flash"


def test_flash_non_ecrit_reste_none():
    assert decrire_flash(None) is None


def test_flash_du_jpeg_de_reference(exif):
    assert exif.flash == 0x19
    assert "déclenché" in exif.flash_libelle
    assert "mode automatique" in exif.flash_libelle


def test_champs_non_ecrits_restent_none():
    """Une image sans EXIF étendu : tous les nouveaux champs à None, aucune valeur inventée."""
    img = Image.new("RGB", (8, 8))
    tampon = BytesIO()
    exif = Image.Exif()
    exif[0x010F] = "Nu"
    img.save(tampon, format="JPEG", exif=exif)
    e = lire_exif_depuis_jpeg(tampon.getvalue())
    assert e.fabricant == "Nu"
    for champ in ("logiciel", "flash", "espace_colorimetrique", "mode_exposition",
                  "rapport_zoom_numerique", "dpi_x", "artiste", "miniature"):
        assert getattr(e, champ) is None, champ
