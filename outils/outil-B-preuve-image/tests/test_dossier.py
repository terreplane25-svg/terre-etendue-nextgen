"""
Le relevé unifié : ce qu'il rassemble, et ce qu'il refuse de remplir.

CE QUE CES TESTS ÉTABLISSENT
────────────────────────────
Qu'un même fichier donne la même structure quel que soit son format, que
chaque lecteur en échec est consigné sans faire tomber les autres, et surtout
que les champs qu'on ne peut PAS renseigner restent nuls AVEC leur motif.

Ce dernier point est le seul qui compte vraiment. Un relevé unifié présente
côte à côte des champs qui ne s'établissent pas de la même façon — une marque
lue, un numéro de série lu, un type de matériel déduit, une correspondance
d'écran qui n'existe pas. Dans un JSON, les quatre ont la même apparence. Ces
tests vérifient que la différence reste lisible.
"""

import struct
from io import BytesIO

import pytest
from PIL import Image

from preuve_image.dossier import (
    MOTIF_DECLENCHEMENTS_ABSENT,
    MOTIF_ECRAN_NON_EVALUE,
    MOTIF_NUMERO_SERIE_ABSENT,
    constituer_dossier,
    deduire_type_materiel,
)
from preuve_image.telemetrie import extraire_telemetrie
from tests.test_conteneurs import SVG, gif, png, webp
from tests.test_isobmff import cr3, heic
from tests.test_quantification import jpeg
from tests.test_raw import raw_tiff
from tests.test_telemetrie import XMP_DJI


def jpeg_avec_serie(serie=b"012345006789", serie_obj=b"0000c1e2f3") -> bytes:
    """Un JPEG portant BodySerialNumber et LensSerialNumber.

    Ce sont des tags EXIF STANDARD, pas des MakerNotes : la plupart des reflex
    et des hybrides les écrivent en clair.
    """
    from tests.test_metadata import (
        _envelopper_en_jpeg, campo_ascii, campo_rational, campo_short, construire_tiff,
    )
    return _envelopper_en_jpeg(construire_tiff(
        {0x010F: campo_ascii("Canon"), 0x0110: campo_ascii("EOS R5")},
        {0xA431: campo_ascii(serie.decode()),
         0xA435: campo_ascii(serie_obj.decode()),
         0xA434: campo_ascii("RF24-105mm F4 L IS USM"),
         0xA433: campo_ascii("Canon"),
         0xA430: campo_ascii("J. Dupont"),
         0x8827: campo_short(400),
         0x829D: campo_rational((400, 100))}))


def jpeg_telephone() -> bytes:
    """Un JPEG dont le nom d'objectif déclare une caméra arrière."""
    from tests.test_metadata import _envelopper_en_jpeg, campo_ascii, construire_tiff
    return _envelopper_en_jpeg(construire_tiff(
        {0x010F: campo_ascii("Apple"), 0x0110: campo_ascii("iPhone 15 Pro")},
        {0xA434: campo_ascii("iPhone 15 Pro back triple camera 6.86mm f/1.78")}))


# ─────────────────────────────────────────────────────────────────────────────
# La même structure, quel que soit le format
# ─────────────────────────────────────────────────────────────────────────────

BLOCS = (
    "file_analysis", "device_identification", "capture_settings",
    "telemetry_and_location", "provenance_and_software", "deep_fingerprint",
)


@pytest.mark.parametrize("nom,fabrique", [
    ("jpeg", lambda: jpeg()),
    ("png", png),
    ("webp", webp),
    ("gif", gif),
    ("svg", lambda: SVG),
    ("heic", heic),
    ("cr3", cr3),
    ("raw tiff", raw_tiff),
])
def test_structure_identique_quel_que_soit_le_format(nom, fabrique):
    """Le propos même du module : un format n'a pas à changer la forme du relevé."""
    d = constituer_dossier(fabrique(), f"essai.{nom}")
    doc = d.en_dict()
    for bloc in BLOCS:
        assert bloc in doc, f"{nom} : bloc {bloc} manquant"
        assert isinstance(doc[bloc], dict)


def test_format_reconnu_aux_octets_pas_a_l_extension():
    """Une extension se renomme ; c'est le premier geste de qui veut tromper."""
    d = constituer_dossier(png(), "photo.jpg")
    assert d.file_analysis["mime_type"] == "image/png"
    assert d.file_analysis["extension_declaree"] == ".jpg"
    assert d.file_analysis["mime_source"].startswith("octets")
    assert any("annonce un JPEG" in a for a in d.avertissements)


def test_extension_coherente_ne_declenche_aucun_avertissement():
    assert constituer_dossier(png(), "photo.png").avertissements == []


def test_extension_inconnue_ne_declenche_pas_de_faux_positif():
    """Une table extension → format serait incomplète et ferait de faux positifs."""
    assert constituer_dossier(png(), "photo.dat").avertissements == []


def test_empreinte_et_taille_toujours_presentes():
    d = constituer_dossier(png(), "x.png")
    assert len(d.file_analysis["sha256"]) == 64
    assert d.file_analysis["file_size_bytes"] > 0


# ─────────────────────────────────────────────────────────────────────────────
# Les numéros de série : des tags EXIF standard, jamais lus jusqu'ici
# ─────────────────────────────────────────────────────────────────────────────


def test_numeros_de_serie_lus():
    d = constituer_dossier(jpeg_avec_serie(), "reflex.jpg")
    dev = d.device_identification
    assert dev["serial_number"] == "012345006789"
    assert dev["lens_serial_number"] == "0000c1e2f3"
    assert dev["lens_model"] == "RF24-105mm F4 L IS USM"
    assert dev["lens_make"] == "Canon"
    assert dev["owner_declared"] == "J. Dupont"
    assert dev["motif_serial_number"] is None


def test_absence_de_numero_de_serie_porte_son_motif():
    """Beaucoup d'appareils n'en écrivent pas, et les téléphones jamais."""
    d = constituer_dossier(jpeg(), "sans-serie.jpg")
    assert d.device_identification["serial_number"] is None
    assert d.device_identification["motif_serial_number"] == MOTIF_NUMERO_SERIE_ABSENT
    assert "MakerNotes" in MOTIF_NUMERO_SERIE_ABSENT


def test_methode_de_detection_dit_d_ou_vient_l_identification():
    """Sans ce champ, « Apple / iPhone 15 Pro » ne dirait pas d'où il sort."""
    d = constituer_dossier(jpeg_avec_serie(), "reflex.jpg")
    m = d.device_identification["detection_method"]
    assert "EXIF standard" in m
    assert "numéros de série" in m
    assert "JPEG" in m

    nu = constituer_dossier(png(), "x.png")
    assert "aucune" in nu.device_identification["detection_method"]


def test_makernotes_signales_mais_non_decodes():
    """Les nommer sans les décoder est honnête ; prétendre les lire ne le serait pas."""
    d = constituer_dossier(cr3(), "photo.cr3")
    assert "NON DÉCODÉS" in d.device_identification["detection_method"]


# ─────────────────────────────────────────────────────────────────────────────
# Le type de matériel : DÉDUIT, et marqué comme tel
# ─────────────────────────────────────────────────────────────────────────────


def test_type_materiel_marque_comme_deduit_avec_sa_regle():
    """Une déduction n'a pas le statut d'une lecture, et le relevé le dit.

    `hardware_type_regle` permet de contester la conclusion sans relire le code
    — c'est ce qui distingue une déduction assumée d'une affirmation.
    """
    d = constituer_dossier(jpeg_telephone(), "iphone.jpg")
    dev = d.device_identification
    assert dev["hardware_type"] == "téléphone"
    assert "caméra avant ou arrière" in dev["hardware_type_regle"]
    assert dev["hardware_type_statut"] == "déduit, non lu"


def test_appareil_a_objectifs_interchangeables():
    d = constituer_dossier(jpeg_avec_serie(), "reflex.jpg")
    assert d.device_identification["hardware_type"] == "appareil à objectifs interchangeables"


def test_format_brut_designe_un_appareil_dedie():
    assert constituer_dossier(cr3(), "x.cr3").device_identification["hardware_type"] \
        == "appareil photo dédié"


def test_aeronef_reconnu_a_sa_telemetrie():
    t = extraire_telemetrie(XMP_DJI)
    d = deduire_type_materiel(None, t, "JPEG")
    assert d.valeur == "aéronef sans équipage"
    assert "télémétrie de vol" in d.regle


def test_aucune_regle_applicable_rend_none_pas_une_supposition():
    """Un « appareil photo » deviné d'après un fabricant vaudrait moins que rien."""
    d = constituer_dossier(png(), "x.png")
    assert d.device_identification["hardware_type"] is None
    assert d.device_identification["hardware_type_statut"] == "indéterminé"
    assert d.device_identification["hardware_type_regle"] is None


# ─────────────────────────────────────────────────────────────────────────────
# Ce qui ne peut PAS être renseigné, et le dit
# ─────────────────────────────────────────────────────────────────────────────


def test_decompte_de_declenchements_toujours_nul_avec_son_motif():
    """Il n'existe dans AUCUN tag EXIF standard, seulement dans les MakerNotes."""
    for donnees in (jpeg(), jpeg_avec_serie(), cr3()):
        d = constituer_dossier(donnees, "x")
        assert d.capture_settings["shutter_count"] is None
        assert d.capture_settings["motif_shutter_count"] == MOTIF_DECLENCHEMENTS_ABSENT
        assert "dictionnaire par appareil" in MOTIF_DECLENCHEMENTS_ABSENT


def test_correspondance_d_ecran_jamais_affirmee():
    """Le référentiel n'existe pas, et le motif dit aussi que le signal serait faible."""
    d = constituer_dossier(png(), "capture.png")
    assert d.deep_fingerprint["screen_resolution_match"] is None
    assert d.deep_fingerprint["motif_screen_resolution"] == MOTIF_ECRAN_NON_EVALUE
    assert "recadrée à ces dimensions" in MOTIF_ECRAN_NON_EVALUE


def test_rapprochement_de_quantification_jamais_affirme():
    d = constituer_dossier(jpeg(), "x.jpg")
    assert d.deep_fingerprint["jpeg_quantization_match"] is None
    assert "registre des signatures est vide" in d.deep_fingerprint["motif_quantization_match"]
    # Les tables, elles, sont bien là : c'est le RAPPROCHEMENT qui manque, pas
    # la donnée.
    assert d.deep_fingerprint["jpeg_quantization"]["empreinte_tables"]


def test_c2pa_present_n_est_jamais_c2pa_verifie():
    d = constituer_dossier(jpeg(), "x.jpg")
    assert d.provenance_and_software["c2pa_verified"] is False
    assert "DÉCLARÉ" in d.provenance_and_software["motif_c2pa_non_verifie"]


def test_absence_d_historique_xmp_ne_veut_pas_dire_absence_de_retouche():
    d = constituer_dossier(jpeg(), "x.jpg")
    assert d.provenance_and_software["xmp_history"] == []
    motif = d.provenance_and_software["motif_xmp_history"]
    assert "se retire, se tronque et se réécrit" in motif


# ─────────────────────────────────────────────────────────────────────────────
# Les blocs qui viennent de chaque lecteur
# ─────────────────────────────────────────────────────────────────────────────


def test_reglages_de_prise_de_vue():
    d = constituer_dossier(jpeg_avec_serie(), "x.jpg")
    c = d.capture_settings
    assert c["iso"] == 400
    assert c["f_number"] == pytest.approx(4.0)


def test_vitesse_mise_en_forme_et_valeur_exacte_toutes_deux_rendues():
    """Une fraction arrondie ne se recalcule pas : le nombre exact reste à côté."""
    from tests.test_metadata import (
        _envelopper_en_jpeg, campo_ascii, campo_rational, construire_tiff,
    )
    donnees = _envelopper_en_jpeg(construire_tiff(
        {0x010F: campo_ascii("Essai")}, {0x829A: campo_rational((1, 200))}))
    c = constituer_dossier(donnees, "x.jpg").capture_settings
    assert c["exposure_time"] == "1/200"
    assert c["exposure_time_s"] == pytest.approx(0.005)


def test_profil_icc_remonte_depuis_le_conteneur():
    d = constituer_dossier(png(), "x.png")
    assert d.deep_fingerprint["icc_profile"] == "Display P3"
    assert d.deep_fingerprint["motif_icc"] is None


def test_tables_de_quantification_seulement_pour_les_jpeg():
    assert constituer_dossier(jpeg(), "x.jpg").deep_fingerprint["jpeg_quantization"]
    assert constituer_dossier(png(), "x.png").deep_fingerprint["jpeg_quantization"] is None


def test_crc_png_remontes_avec_leur_asymetrie():
    sain = constituer_dossier(png(), "x.png")
    assert sain.deep_fingerprint["png_crc_corrompus"] == []
    assert "établit rien de plus" in sain.deep_fingerprint["motif_crc"]
    abime = constituer_dossier(png(crc_faux=True), "x.png")
    assert abime.deep_fingerprint["png_crc_corrompus"]


def test_apercus_embarques_listes_du_plus_grand_au_plus_petit():
    """Ils n'ont pas été écrits au même moment : leur comparaison a valeur d'indice."""
    d = constituer_dossier(raw_tiff(), "x.cr2")
    a = d.deep_fingerprint["apercus_embarques"]
    assert len(a) == 3
    assert [x["octets"] for x in a] == sorted([x["octets"] for x in a], reverse=True)


def test_telemetrie_de_drone_dans_le_bloc_dedie():
    """Un JPEG portant du XMP DJI doit remonter sa télémétrie."""
    from tests.test_metadata import _envelopper_en_jpeg, campo_ascii, construire_tiff
    import struct as st
    tiff = construire_tiff({0x010F: campo_ascii("DJI")})
    base = bytearray(_envelopper_en_jpeg(tiff))
    app1 = b"http://ns.adobe.com/xap/1.0/\x00" + XMP_DJI
    segment = b"\xff\xe1" + st.pack(">H", len(app1) + 2) + app1
    base[2:2] = segment
    d = constituer_dossier(bytes(base), "drone.jpg")
    t = d.telemetry_and_location["drone_telemetry"]
    assert t is not None
    assert t["origine"] == "DJI"
    assert t["relative_altitude_m"] == pytest.approx(87.50)
    assert t["ground_station"] is None
    assert "position du drone sous une autre étiquette" in t["motif_ground_station"]
    assert d.device_identification["hardware_type"] == "aéronef sans équipage"


# ─────────────────────────────────────────────────────────────────────────────
# Les échecs : consignés, jamais tus, jamais fatals
# ─────────────────────────────────────────────────────────────────────────────


def test_un_lecteur_en_echec_ne_fait_pas_tomber_les_autres():
    """Un JPEG sans EXIF garde ses tables de quantification.

    L'inverse ferait passer une lacune pour une absence de données.
    """
    donnees = jpeg()
    # On casse le segment APP1 sans toucher au reste.
    i = donnees.find(b"\xff\xe1")
    if i != -1:
        donnees = donnees[:i] + b"\xff\xe0" + donnees[i + 2:]
    d = constituer_dossier(donnees, "x.jpg")
    assert d.deep_fingerprint["jpeg_quantization"] is not None
    assert d.file_analysis["sha256"]


def test_echec_de_lecture_consigne_avec_son_motif():
    """L'absence d'un bloc et l'échec de sa lecture ne s'établissent pas pareil."""
    d = constituer_dossier(png(), "x.png")
    # Un PNG n'a pas d'EXIF au sens strict : le lecteur échoue, et le dit.
    assert any(e["lecteur"] == "EXIF" for e in d.lectures_en_echec)
    assert all(e["motif"] for e in d.lectures_en_echec)


def test_un_partage_de_responsabilite_n_est_pas_une_panne():
    """Un JPEG n'a rien à faire chez le lecteur de conteneurs hors EXIF.

    Le consigner comme un échec ferait prendre un partage de responsabilité
    entre lecteurs pour une panne.
    """
    d = constituer_dossier(jpeg(), "x.jpg")
    assert not any(e["lecteur"] == "conteneurs" for e in d.lectures_en_echec)


def test_fichier_inconnu_reste_exploitable():
    """L'empreinte et la taille valent toujours, même sans aucun lecteur."""
    d = constituer_dossier(b"ceci n'est pas une image du tout, vraiment pas", "x.bin")
    assert len(d.file_analysis["sha256"]) == 64
    assert d.file_analysis["mime_type"] is None
    assert d.lectures_en_echec


def test_le_dossier_se_serialise_entierement():
    """Un relevé qui ne passe pas en JSON ne sert à rien comme pièce."""
    import json
    for fabrique in (lambda: jpeg(), png, heic, cr3, lambda: SVG):
        json.dumps(constituer_dossier(fabrique(), "x").en_dict(), ensure_ascii=False)
