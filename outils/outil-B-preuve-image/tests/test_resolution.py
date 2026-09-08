"""
Les dimensions d'une image : ce qu'elles établissent, et ce qu'elles ne font pas.

CE QUE CES TESTS ÉTABLISSENT
────────────────────────────
Que les dimensions MESURÉES et les dimensions DÉCLARÉES sont rendues
séparément, et que leur écart est signalé. C'est le test qui compte : le relevé
préférait la déclaration à la mesure, ce qui masquait l'écart au lieu de le
montrer — un fichier redimensionné sans que l'EXIF suive passait pour cohérent.

Que le rapport d'aspect est exact et réduit, et qu'il conserve l'orientation.

Et que le référentiel d'écrans reste vide : le remplir de mémoire produirait
des identifications fausses présentées comme des faits.
"""

import pytest

from preuve_image.resolution import (
    DEFINITIONS_NOMMEES,
    ECRANS_CONNUS,
    MOTIF_AUCUN_ECRAN,
    analyser_resolution,
    rapport_exact,
)


# ── La confrontation mesure / déclaration ───────────────────────────────────


def test_les_deux_jeux_sont_rendus_separement():
    """Jamais l'un à la place de l'autre : c'est l'écart qui informe."""
    r = analyser_resolution(1024, 768, 4032, 3024)
    assert (r.largeur_mesuree, r.hauteur_mesuree) == (1024, 768)
    assert (r.largeur_declaree, r.hauteur_declaree) == (4032, 3024)


def test_un_ecart_est_signale_et_dit_ce_qu_il_etablit():
    """Le cas d'un fichier redimensionné sans que la métadonnée suive.

    C'est un signal FORT et gratuit : les deux grandeurs sont écrites à des
    moments différents, par des outils différents.
    """
    r = analyser_resolution(1024, 768, 4032, 3024)
    assert r.dimensions_coherentes is False
    assert "1024 × 768" in r.motif_ecart
    assert "4032 × 3024" in r.motif_ecart
    assert "ÉTABLIT" in r.motif_ecart
    # Et il borne sa conclusion : l'écart ne dit pas QUI, ni lequel est bon.
    assert "lequel des deux est le bon" in r.motif_ecart


def test_des_dimensions_qui_coincident_ne_portent_aucun_motif():
    r = analyser_resolution(4032, 3024, 4032, 3024)
    assert r.dimensions_coherentes is True
    assert r.motif_ecart is None


def test_une_declaration_absente_ne_vaut_pas_incoherence():
    """None, pas False. Un fichier sans EXIF n'est pas un fichier menteur.

    Les confondre transformerait une absence de donnée en indice.
    """
    r = analyser_resolution(4032, 3024, None, None)
    assert r.dimensions_coherentes is None
    assert r.motif_ecart is None


def test_une_mesure_absente_ne_vaut_pas_incoherence():
    r = analyser_resolution(None, None, 4032, 3024)
    assert r.dimensions_coherentes is None
    assert r.largeur_mesuree is None
    assert r.largeur_declaree == 4032


@pytest.mark.parametrize("l,h", [(0, 100), (100, 0), (-1, 100)])
def test_des_dimensions_non_positives_sont_ecartees(l, h):
    """Zéro ou négatif n'est pas une dimension : la traiter comme telle
    rendrait un rapport infini ou un nombre de mégapixels négatif."""
    r = analyser_resolution(l, h)
    assert r.largeur_mesuree is None
    assert r.rapport is None


# ── Le rapport d'aspect ─────────────────────────────────────────────────────


@pytest.mark.parametrize("l,h,attendu", [
    (1920, 1080, (16, 9)),
    (4032, 3024, (4, 3)),
    (6000, 4000, (3, 2)),
    (1179, 2556, (131, 284)),   # gcd = 9, pas 3 : mon attente initiale était fausse
    (1000, 1000, (1, 1)),
    (2048, 1080, (256, 135)),
])
def test_le_rapport_est_exact_et_reduit(l, h, attendu):
    assert rapport_exact(l, h) == attendu


def test_le_rapport_conserve_l_orientation():
    """3024 × 4032 rend 3:4, pas 4:3.

    Normaliser les deux au même rapport perdrait l'orientation, qui est
    précisément ce qui distingue un portrait d'un paysage.
    """
    assert rapport_exact(4032, 3024) == (4, 3)
    assert rapport_exact(3024, 4032) == (3, 4)
    assert analyser_resolution(3024, 4032).orientation == "portrait"
    assert analyser_resolution(4032, 3024).orientation == "paysage"
    assert analyser_resolution(1000, 1000).orientation == "carré"


def test_les_megapixels_suivent_les_dimensions_mesurees():
    r = analyser_resolution(4032, 3024, 1024, 768)
    assert r.megapixels == pytest.approx(12.192768)


def test_un_rapport_sur_dimension_nulle_est_refuse():
    with pytest.raises(ValueError):
        rapport_exact(0, 100)


# ── Les dénominations : un nom, pas une preuve ──────────────────────────────


def test_une_denomination_est_rendue_dans_les_deux_orientations():
    """Une capture portrait porte le même nom que son pendant paysage."""
    assert analyser_resolution(1920, 1080).denomination == "1080p"
    assert analyser_resolution(1080, 1920).denomination == "1080p"


def test_des_dimensions_sans_denomination_n_en_recoivent_pas():
    """Aucune invention : la plupart des clichés n'ont pas de nom d'usage."""
    assert analyser_resolution(4032, 3024).denomination is None


def test_les_denominations_ne_nomment_aucun_appareil():
    """Le registre des dénominations est distinct de celui des écrans.

    Les mélanger ferait passer « 1080p » pour une identification de matériel,
    alors que tout recadrage à ces dimensions porte le même nom.
    """
    for nom in DEFINITIONS_NOMMEES.values():
        for interdit in ("iPhone", "Galaxy", "Pixel", "MacBook", "Retina"):
            assert interdit not in nom, nom


# ── L'alignement JPEG ───────────────────────────────────────────────────────


@pytest.mark.parametrize("l,h,attendu", [
    (1920, 1080, 8),      # 1080 n'est pas multiple de 16
    (1920, 1088, 16),
    (4032, 3024, 16),
    (1023, 767, None),
    (1000, 1000, 8),
])
def test_l_alignement_est_rendu_sans_etre_interprete(l, h, attendu):
    assert analyser_resolution(l, h).alignement_jpeg == attendu


# ── Le référentiel d'écrans : vide, et il le reste ──────────────────────────


def test_le_referentiel_d_ecrans_est_vide():
    """Le remplir demande un corpus vérifié, modèle par modèle.

    Y écrire « 1179 × 2556 = iPhone 15 Pro » de mémoire produirait une
    identification fausse présentée comme un fait.
    """
    assert ECRANS_CONNUS == {}


def test_aucun_appareil_n_est_jamais_rapproche():
    for l, h in [(1179, 2556), (1920, 1080), (4032, 3024), (2556, 1179)]:
        assert analyser_resolution(l, h).ecran_rapproche is None


def test_le_motif_dit_pourquoi_et_ce_qui_est_rendu_a_la_place():
    r = analyser_resolution(1179, 2556)
    assert r.motif_aucun_ecran == MOTIF_AUCUN_ECRAN
    assert "référentiel" in r.motif_aucun_ecran
    # Il dit aussi que le signal serait faible MÊME vérifié : c'est le point
    # qui distingue une réserve d'un simple aveu de lacune.
    assert "même vérifié" in r.motif_aucun_ecran
    assert "image recadrée" in r.motif_aucun_ecran
    assert "à la place" in r.motif_aucun_ecran
