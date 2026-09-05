"""
Le document JSON d'ingestion, et les quatre écarts assumés au schéma reçu.

Le schéma est suivi champ pour champ. Ces tests vérifient d'abord qu'il l'est,
puis qu'aux quatre endroits où il ne pouvait pas l'être sans écrire quelque
chose de faux, l'écart est bien celui qui a été décidé — et pas un oubli.
"""

import json
import struct
from io import BytesIO

import pytest
from PIL import Image
from PIL.TiffImagePlugin import IFDRational

from preuve_image.document import (
    MOTIF_SIGNATURE_NON_VERIFIEE,
    dimensions_jpeg,
    document_ingestion,
    horodatage_iso,
    vitesse_obturation,
)
from test_provenance import (  # noqa: F401 — fixtures partagées
    XMP_EXEMPLE,
    dataset_iim,
    manifeste_c2pa_synthetique,
)


def jpeg(largeur=1024, hauteur=576, avec_offset=False, unite=2, resolution=(300, 300)):
    img = Image.new("RGB", (largeur, hauteur), (24, 34, 48))
    exif = Image.Exif()
    exif[0x010F] = "SONY"
    exif[0x0110] = "ILCE-6000"
    exif[0x0131] = "darktable 1.6.6"
    exif[0x0132] = "2015:08:14 15:32:39"
    exif[0x011A] = IFDRational(resolution[0], 1)
    exif[0x011B] = IFDRational(resolution[1], 1)
    exif[0x0128] = unite
    s = exif.get_ifd(0x8769)
    s[0x9003] = "2014:07:31 18:05:43"
    s[0x8827] = 100
    s[0x829D] = IFDRational(11, 1)
    s[0x829A] = IFDRational(1, 200)
    s[0x920A] = IFDRational(10, 1)
    s[0xA001] = 1
    s[0xA002] = largeur
    s[0xA003] = hauteur
    s[0xA434] = "E 10-18mm F4 OSS"
    if avec_offset:
        s[0x9011] = "+02:00"
        s[0x9010] = "+02:00"
    g = exif.get_ifd(0x8825)
    g[1] = "N"
    g[2] = (IFDRational(47, 1), IFDRational(21, 1), IFDRational(0, 1))
    g[3] = "E"
    g[4] = (IFDRational(8, 1), IFDRational(29, 1), IFDRational(5280, 100))
    tampon = BytesIO()
    img.save(tampon, format="JPEG", exif=exif)
    return tampon.getvalue()


@pytest.fixture(scope="module")
def doc():
    return document_ingestion(jpeg(), nom_fichier="essai.jpg")


# ─────────────────────────────────────────────────────────────────────────────
# Le schéma demandé, champ par champ
# ─────────────────────────────────────────────────────────────────────────────


def test_forme_generale(doc):
    for cle in ("file_info", "exif", "c2pa", "thumbnail"):
        assert cle in doc, cle


def test_file_info(doc):
    assert doc["file_info"]["dimensions"] == [1024, 576]
    assert doc["file_info"]["color_space"] == "sRGB"
    assert doc["file_info"]["dpi"] == 300.0


def test_exif_camera_logiciel_objectif(doc):
    assert doc["exif"]["camera"] == "SONY ILCE-6000"
    assert doc["exif"]["software"] == "darktable 1.6.6"
    assert doc["exif"]["lens"] == "E 10-18mm F4 OSS"


def test_exif_settings(doc):
    s = doc["exif"]["settings"]
    assert s["iso"] == 100
    assert s["f_number"] == pytest.approx(11.0)
    assert s["shutter_speed"] == "1/200"


def test_exif_gps(doc):
    assert doc["exif"]["gps"]["latitude"] == pytest.approx(47.35, abs=1e-6)
    assert doc["exif"]["gps"]["longitude"] == pytest.approx(8.498, abs=1e-6)


def test_document_serialisable(doc):
    json.dumps(doc)  # doit passer sans convertisseur


# ─────────────────────────────────────────────────────────────────────────────
# Écart 1 — le fuseau horaire n'est jamais inventé
# ─────────────────────────────────────────────────────────────────────────────


def test_horodatage_sans_offset_declare_reste_local():
    """C'est l'écart qui compte le plus.

    `DateTimeOriginal` est une heure locale sans fuseau. Lui accoler « +02:00 »
    parce que le schéma d'exemple en portait un reviendrait à inventer une
    information — et sur une observation horodatée, ce genre d'invention décide
    d'un résultat.
    """
    d = document_ingestion(jpeg(avec_offset=False))
    o = d["exif"]["dates"]["original"]
    assert o["valeur"] == "2014-07-31T18:05:43"
    assert o["offset_declare"] is False
    assert "+" not in o["valeur"] and not o["valeur"].endswith("Z")
    assert o["brut"] == "2014:07:31 18:05:43"


def test_horodatage_avec_offset_declare_le_porte():
    """Quand l'appareil écrit OffsetTimeOriginal, l'ISO 8601 est complet."""
    d = document_ingestion(jpeg(avec_offset=True))
    o = d["exif"]["dates"]["original"]
    assert o["valeur"] == "2014-07-31T18:05:43+02:00"
    assert o["offset_declare"] is True


def test_horodatage_absent():
    r = horodatage_iso(None, None)
    assert r["valeur"] is None and r["offset_declare"] is False


def test_horodatage_dit_ce_qu_il_n_etablit_pas(doc):
    texte = doc["exif"]["dates"]["ce_que_ca_n_etablit_pas"]
    assert "ne date pas la prise de vue" in texte
    assert "INCONNU" in texte


# ─────────────────────────────────────────────────────────────────────────────
# Écart 2 — dpi scalaire seulement quand il en existe un
# ─────────────────────────────────────────────────────────────────────────────


def test_dpi_scalaire_quand_les_deux_axes_coincident(doc):
    assert doc["file_info"]["dpi"] == 300.0
    assert doc["file_info"]["dpi_x"] == doc["file_info"]["dpi_y"] == 300.0


def test_dpi_nul_quand_les_axes_different():
    """Une valeur unique masquerait une anisotropie réelle."""
    d = document_ingestion(jpeg(resolution=(300, 150)))
    assert d["file_info"]["dpi"] is None
    assert d["file_info"]["dpi_x"] == 300.0
    assert d["file_info"]["dpi_y"] == 150.0


def test_dpi_nul_quand_l_unite_n_en_definit_pas():
    """Unité 1 : le nombre est un rapport d'aspect, pas une densité."""
    d = document_ingestion(jpeg(unite=1))
    assert d["file_info"]["dpi"] is None
    assert d["file_info"]["dpi_x"] is None
    assert d["file_info"]["resolution_unit"]["code"] == 1
    assert d["file_info"]["resolution_unit"]["libelle"] == "sans unité"


# ─────────────────────────────────────────────────────────────────────────────
# Écart 3 — camera concatène, make et model restent
# ─────────────────────────────────────────────────────────────────────────────


def test_make_et_model_restent_separes(doc):
    """« SONY ILCE-6000 » ne se redécoupe pas à coup sûr."""
    assert doc["exif"]["make"] == "SONY"
    assert doc["exif"]["model"] == "ILCE-6000"
    assert doc["exif"]["camera"] == "SONY ILCE-6000"


# ─────────────────────────────────────────────────────────────────────────────
# Écart 4 — « signature » ne se lit jamais comme un verdict
# ─────────────────────────────────────────────────────────────────────────────


def jpeg_avec_c2pa() -> bytes:
    base = jpeg()
    magasin = manifeste_c2pa_synthetique()
    segments = b""
    for numero, i in enumerate(range(0, len(magasin), 200), start=1):
        corps = b"JP" + struct.pack(">H", 1) + struct.pack(">I", numero) + magasin[i : i + 200]
        segments += b"\xff\xeb" + struct.pack(">H", len(corps) + 2) + corps
    return base[:2] + segments + base[2:]


def test_signature_porte_l_identite_declaree_et_le_dit():
    d = document_ingestion(jpeg_avec_c2pa())
    c = d["c2pa"]
    assert c["present"] is True
    assert c["signature"] == "essai-c2pa/0.1"
    assert c["verified"] is False
    assert c["motif"] == MOTIF_SIGNATURE_NON_VERIFIEE
    assert "DÉCLARE" in c["motif"]


def test_actions_c2pa_dans_le_document():
    d = document_ingestion(jpeg_avec_c2pa())
    assert d["c2pa"]["actions"] == [
        "c2pa.created", "c2pa.color_adjustments", "c2pa.cropped",
    ]


def test_absence_de_c2pa_ne_fabrique_rien(doc):
    assert doc["c2pa"]["present"] is False
    assert doc["c2pa"]["actions"] == []
    assert doc["c2pa"]["signature"] is None
    assert doc["c2pa"]["verified"] is False


def test_aucune_affirmation_d_authenticite_dans_le_document():
    """Le document entier est balayé : aucune tournure affirmative nulle part."""
    texte = json.dumps(document_ingestion(jpeg_avec_c2pa()), ensure_ascii=False).lower()
    for affirmation in (
        "est authentique", "signature valide", "provenance vérifiée",
        "authenticité confirmée", "certifié conforme", "image authentifiée",
    ):
        assert affirmation not in texte, affirmation


# ─────────────────────────────────────────────────────────────────────────────
# Miniature
# ─────────────────────────────────────────────────────────────────────────────


def test_dimensions_jpeg_lues_dans_le_sof():
    """Sans décodage : le marqueur SOF porte hauteur puis largeur."""
    assert dimensions_jpeg(jpeg(320, 240)) == (320, 240)


def test_dimensions_jpeg_refuse_ce_qui_n_en_est_pas():
    assert dimensions_jpeg(b"pas un jpeg") is None
    assert dimensions_jpeg(b"\xff\xd8\xff\xda\x00\x02\xff\xd9") is None


def test_thumbnail_absente(doc):
    assert doc["thumbnail"]["present"] is False
    assert doc["thumbnail"]["dimensions"] is None


def test_thumbnail_presente_avec_ses_dimensions():
    """La miniature est chaînée dans un IFD1, comme un appareil l'écrit."""
    from test_metadata_ingestion import tiff_avec_miniature
    from preuve_image.metadata import lire_exif_depuis_tiff

    e = lire_exif_depuis_tiff(tiff_avec_miniature())
    assert e.miniature is not None
    # La vignette de cette fixture est un JPEG minimal sans SOF : les
    # dimensions sont donc INCONNUES, et c'est ce qu'il faut rendre.
    from preuve_image.document import _bloc_thumbnail
    t = _bloc_thumbnail(e)
    assert t["present"] is True
    assert t["dimensions"] is None
    assert t["format"] == "JPEG"
    assert len(t["sha256"]) == 64


def test_thumbnail_dit_ce_qu_elle_n_etablit_pas():
    from test_metadata_ingestion import tiff_avec_miniature
    from preuve_image.metadata import lire_exif_depuis_tiff
    from preuve_image.document import _bloc_thumbnail

    t = _bloc_thumbnail(lire_exif_depuis_tiff(tiff_avec_miniature()))
    assert "Seul un ÉCART" in t["ce_que_ca_n_etablit_pas"]


# ─────────────────────────────────────────────────────────────────────────────
# Vitesse d'obturation
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("secondes,attendu", [
    (1 / 200, "1/200"),
    (1 / 60, "1/60"),
    (0.5, "1/2"),
    (1.0, "1 s"),
    (2.5, "2,5 s"),
    (30.0, "30 s"),
    # Inverses non entiers : ce que les boîtiers écrivent réellement, l'échelle
    # APEX ne tombant pas rond. Sans eux, une erreur d'arrondi passe inaperçue.
    (0.0049, "1/204"),
    (1 / 3, "1/3"),
    (1.7, "1,7 s"),
])
def test_vitesse_obturation(secondes, attendu):
    assert vitesse_obturation(secondes) == attendu


def test_vitesse_obturation_absente_ou_absurde():
    assert vitesse_obturation(None) is None
    assert vitesse_obturation(0.0) is None
    assert vitesse_obturation(-1.0) is None


def test_valeur_exacte_conservee_a_cote(doc):
    """Une fraction arrondie ne se recalcule pas : le nombre reste disponible."""
    s = doc["exif"]["settings"]
    assert s["shutter_speed"] == "1/200"
    assert s["shutter_speed_s"] == pytest.approx(1 / 200)


# ─────────────────────────────────────────────────────────────────────────────
# Fichier sans EXIF
# ─────────────────────────────────────────────────────────────────────────────


def test_fichier_sans_exif_rend_le_motif():
    d = document_ingestion(b"\xff\xd8\xff\xda\x00\x02\xff\xd9")
    assert d["exif"]["lu"] is False
    assert "APP1" in d["exif"]["motif"]
    assert d["c2pa"]["present"] is False
    assert d["thumbnail"]["present"] is False
    json.dumps(d)


def test_empreinte_du_fichier_presente(doc):
    assert len(doc["sha256"]) == 64
    assert doc["fichier"] == "essai.jpg"
