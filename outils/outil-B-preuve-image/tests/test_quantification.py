"""
Les tables de quantification d'un JPEG.

CE QUI EST ÉPROUVÉ, ET PAR QUEL MOYEN
─────────────────────────────────────
La reconstruction des tables IJG est confrontée à une voie INDÉPENDANTE : les
tables que Pillow écrit réellement pour un facteur de qualité donné. Pillow
appelle libjpeg, qui est la bibliothèque de référence — si notre
réimplémentation de `jpeg_set_quality` divergeait d'un seul coefficient, la
comparaison le dirait. Vérifier notre formule contre elle-même ne prouverait
rien.

Le point le plus important n'est pas la qualité estimée : c'est que l'ÉCART à
la table IJG soit rendu avec elle. Un encodeur d'appareil photo n'emploie pas
les tables IJG ; rendre « qualité 92 » sans dire que douze coefficients
diffèrent laisserait croire à une identification là où il n'y a qu'une
ressemblance.
"""

import struct
from io import BytesIO

import pytest
from PIL import Image

from preuve_image.quantification import (
    MOTIF_AUCUNE_SIGNATURE,
    SIGNATURES_CONNUES,
    TABLE_LUMINANCE_ANNEXE_K,
    QuantificationError,
    analyser_quantification,
    qualite_ijg_estimee,
    table_ijg,
)


def jpeg(qualite=90, taille=(64, 48), progressif=False, sous_ech=None) -> bytes:
    t = BytesIO()
    im = Image.new("RGB", taille, (30, 120, 200))
    # Un peu de contenu, pour que l'encodeur ne dégénère pas.
    for x in range(0, taille[0], 4):
        for y in range(0, taille[1], 4):
            im.putpixel((x, y), (200, 30, 60))
    args = {"format": "JPEG", "quality": qualite}
    if progressif:
        args["progressive"] = True
    if sous_ech is not None:
        args["subsampling"] = sous_ech
    im.save(t, **args)
    return t.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# La reconstruction IJG, confrontée à libjpeg par l'intermédiaire de Pillow
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("q", [1, 10, 25, 49, 50, 51, 75, 85, 90, 95, 100])
def test_table_ijg_reproduit_celle_de_libjpeg(q):
    """Notre `jpeg_set_quality` doit rendre exactement ce que libjpeg écrit.

    C'est le contrôle qui compte : Pillow n'est pas notre code, et libjpeg est
    la référence dont dérivent la quasi-totalité des encodeurs. Un écart d'un
    seul coefficient fausserait toutes les estimations de qualité.
    """
    a = analyser_quantification(jpeg(qualite=q))
    luminance = next(t for t in a.tables if t.identifiant == 0)
    assert luminance.valeurs == table_ijg(q), (
        f"qualité {q} : notre table diverge de celle de libjpeg"
    )


@pytest.mark.parametrize("q", [10, 50, 75, 90, 95])
def test_qualite_retrouvee_exactement_sur_un_encodage_ijg(q):
    a = analyser_quantification(jpeg(qualite=q))
    assert a.qualite_ijg == q
    assert a.ecart_a_ijg == 0
    assert a.conforme_ijg is True


def test_bornes_du_facteur_refusees():
    with pytest.raises(QuantificationError):
        table_ijg(0)
    with pytest.raises(QuantificationError):
        table_ijg(101)


def test_table_bornee_a_255_aux_basses_qualites():
    """L'algorithme IJG borne chaque coefficient à [1 ; 255]. À q=1 tout sature."""
    t = table_ijg(1)
    assert max(t) == 255
    assert min(t) >= 1


def test_table_de_qualite_100_est_presque_toute_a_un():
    assert table_ijg(100)[:4] == (1, 1, 1, 1)


# ─────────────────────────────────────────────────────────────────────────────
# L'écart : ce qui distingue une identification d'une ressemblance
# ─────────────────────────────────────────────────────────────────────────────


def test_une_table_non_ijg_est_signalee_comme_telle():
    """Un encodeur qui n'emploie pas les tables IJG doit être vu comme tel.

    C'est le cas de tous les appareils photo et de plusieurs messageries.
    Rendre « qualité 92 » sans l'écart laisserait croire à une identification
    là où il n'y a qu'une ressemblance.
    """
    # On part d'une table IJG et on modifie quelques coefficients, comme le
    # ferait un encodeur qui a sa propre table.
    brut = bytearray(jpeg(qualite=90))
    i = brut.find(b"\xff\xdb")
    assert i != -1
    # Le premier coefficient de la table 0 est à i+5 (marqueur, longueur, en-tête).
    for k in range(5, 12):
        brut[i + k] = min(255, brut[i + k] + 7)
    a = analyser_quantification(bytes(brut))
    assert a.conforme_ijg is False
    assert a.ecart_a_ijg is not None and a.ecart_a_ijg > 0
    # Une qualité est quand même proposée — mais avec son écart, et c'est ce
    # couple qui est honnête.
    assert a.qualite_ijg is not None


def test_qualite_estimee_rend_toujours_l_ecart():
    q, e = qualite_ijg_estimee(tuple(v + 3 for v in TABLE_LUMINANCE_ANNEXE_K))
    assert q is not None
    assert e is not None and e > 0


def test_table_de_mauvaise_longueur_ne_donne_aucune_qualite():
    assert qualite_ijg_estimee((16, 11, 12)) == (None, None)


# ─────────────────────────────────────────────────────────────────────────────
# L'empreinte : pour comparer deux fichiers, jamais pour identifier
# ─────────────────────────────────────────────────────────────────────────────


def test_deux_encodages_identiques_ont_la_meme_empreinte():
    a = analyser_quantification(jpeg(qualite=85))
    b = analyser_quantification(jpeg(qualite=85, taille=(120, 90)))
    assert a.empreinte_ensemble == b.empreinte_ensemble
    assert a.largeur != b.largeur, "les images devaient différer par ailleurs"


def test_deux_qualites_differentes_ont_des_empreintes_differentes():
    a = analyser_quantification(jpeg(qualite=85))
    b = analyser_quantification(jpeg(qualite=86))
    assert a.empreinte_ensemble != b.empreinte_ensemble


def test_l_empreinte_porte_sur_toutes_les_tables_pas_seulement_la_luminance():
    """Deux images de même luminance mais de chrominance différente ne viennent
    pas de la même chaîne. Les confondre serait un faux rapprochement.
    """
    a = analyser_quantification(jpeg(qualite=90, sous_ech=0))
    brut = bytearray(jpeg(qualite=90, sous_ech=0))
    # On modifie la SECONDE table (chrominance) en laissant la première intacte.
    i = brut.find(b"\xff\xdb")
    j = brut.find(b"\xff\xdb", i + 2)
    cible = j if j != -1 else i + 2 + 65  # seconde table, même segment ou suivant
    brut[cible + 20] = (brut[cible + 20] + 5) % 256
    b = analyser_quantification(bytes(brut))
    lum_a = next(t for t in a.tables if t.identifiant == 0)
    lum_b = next(t for t in b.tables if t.identifiant == 0)
    assert lum_a.valeurs == lum_b.valeurs, "la luminance devait rester identique"
    assert a.empreinte_ensemble != b.empreinte_ensemble


def test_aucune_signature_et_le_motif_le_dit():
    """Le registre est VIDE, délibérément, et le résultat l'explique.

    Une correspondance affirmée sans corpus derrière serait une conjecture
    présentée comme un fait. Le motif dit ce qui manque et ce que l'empreinte
    permet quand même.
    """
    a = analyser_quantification(jpeg())
    assert SIGNATURES_CONNUES == {}
    assert a.signature is None
    assert a.motif_absence_signature == MOTIF_AUCUNE_SIGNATURE
    assert "registre des signatures est vide" in a.motif_absence_signature
    assert "COMPARER deux fichiers" in a.motif_absence_signature


# ─────────────────────────────────────────────────────────────────────────────
# Ce que le SOF déclare
# ─────────────────────────────────────────────────────────────────────────────


def test_dimensions_et_composantes():
    a = analyser_quantification(jpeg(taille=(200, 150)))
    assert (a.largeur, a.hauteur) == (200, 150)
    assert a.composantes == 3


@pytest.mark.parametrize("code,attendu", [(0, "4:4:4"), (1, "4:2:2"), (2, "4:2:0")])
def test_sous_echantillonnage(code, attendu):
    assert analyser_quantification(jpeg(sous_ech=code)).sous_echantillonnage == attendu


def test_progressif_distingue_du_sequentiel():
    """Un JPEG progressif sort rarement d'un appareil photo : le choix compte."""
    assert analyser_quantification(jpeg(progressif=True)).progressif is True
    assert analyser_quantification(jpeg(progressif=False)).progressif is False


def test_marqueurs_nommes():
    m = analyser_quantification(jpeg()).marqueurs
    assert any("DQT" in x for x in m)
    assert any("SOF0" in x for x in m)
    assert any("DHT" in x for x in m)


def test_niveaux_de_gris_n_a_pas_de_sous_echantillonnage():
    """La notation « 4:x:x » n'a de sens qu'à trois composantes."""
    t = BytesIO()
    Image.new("L", (32, 32), 128).save(t, format="JPEG", quality=80)
    a = analyser_quantification(t.getvalue())
    assert a.composantes == 1
    assert a.sous_echantillonnage is None


# ─────────────────────────────────────────────────────────────────────────────
# Robustesse et refus
# ─────────────────────────────────────────────────────────────────────────────


def test_les_valeurs_sont_en_ordre_zigzag_celui_du_fichier():
    """Les réordonner ferait diverger l'empreinte de celle d'un autre outil."""
    a = analyser_quantification(jpeg(qualite=50))
    lum = next(t for t in a.tables if t.identifiant == 0)
    # À q=50, l'échelle IJG vaut 100 : la table est celle de l'annexe K.
    assert lum.valeurs == TABLE_LUMINANCE_ANNEXE_K


def test_deux_tables_dans_un_meme_segment():
    """Un segment DQT peut porter plusieurs tables à la suite."""
    a = analyser_quantification(jpeg(sous_ech=2))
    assert len(a.tables) >= 2
    assert {t.identifiant for t in a.tables} >= {0, 1}


def test_pas_un_jpeg_refuse():
    with pytest.raises(QuantificationError, match="SOI absent"):
        analyser_quantification(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)


def test_jpeg_sans_dqt_refuse():
    """Un JPEG en porte toujours : son absence dit que le fichier est tronqué."""
    donnees = b"\xff\xd8" + b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + b"\x00" * 11 + b"\xff\xd9"
    with pytest.raises(QuantificationError, match="Aucune table"):
        analyser_quantification(donnees)


def test_segment_qui_deborde_arrete_sans_inventer():
    brut = bytearray(jpeg())
    i = brut.find(b"\xff\xdb")
    brut[i + 2 : i + 4] = struct.pack(">H", 60000)
    with pytest.raises(QuantificationError, match="Aucune table"):
        analyser_quantification(bytes(brut))


def test_precision_16_bits_lue():
    """Les tables 16 bits existent, et les lire en 8 donnerait n'importe quoi."""
    valeurs = tuple(range(1, 65))
    corps = b"\x10" + struct.pack(">64H", *valeurs)
    donnees = (b"\xff\xd8"
               + b"\xff\xdb" + struct.pack(">H", 2 + len(corps)) + corps
               + b"\xff\xc0" + struct.pack(">H", 8) + b"\x08" + struct.pack(">HH", 16, 16)
               + b"\x01" + b"\x01\x11\x00"
               + b"\xff\xda" + struct.pack(">H", 2))
    a = analyser_quantification(donnees)
    assert a.tables[0].precision_bits == 16
    assert a.tables[0].valeurs == valeurs
