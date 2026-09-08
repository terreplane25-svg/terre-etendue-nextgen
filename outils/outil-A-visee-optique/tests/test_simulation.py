"""
La règle de lecture du simulateur : quand une visée départage, et quand non.

CE QUE CES TESTS ÉTABLISSENT
────────────────────────────
Que le seuil est bien appliqué à sa valeur nommée, des deux côtés ; que le
relief prime sur la courbure ; et que l'enveloppe de réfraction est lue par
son bord le plus DÉFAVORABLE, pas par sa valeur centrale.

Le test qui compte le plus est celui du relief : une cible cachée par une
colline est cachée dans les deux modèles, pour une raison qui n'est pas la
forme de la Terre. Déclarer cette visée discriminante attribuerait à la
courbure ce qui revient à un talus — et l'erreur va dans les deux sens.
"""

import math

import pytest

from visee_optique.relief import AnalyseRelief, Obstacle
from visee_optique.simulation import (
    K_ENVELOPPE_MAX,
    K_ENVELOPPE_MIN,
    K_STANDARD,
    SEUIL_DISCRIMINATION_FRACTION,
    juger,
)


def analyse(fraction_visible, obstacle=False, relief_evalue=True):
    """Une analyse de relief réduite à ce que la règle de lecture consulte."""
    o = Obstacle(1000.0, 50.0, 40.0, 10.0) if obstacle else None
    return AnalyseRelief(
        modele="sphérique",
        rayon_effectif_m=7_000_000.0,
        hauteur_occultee_courbure_m=0.0,
        fraction_visible_courbure=fraction_visible,
        relief_evalue=relief_evalue,
        motif_relief_non_evalue=None if relief_evalue else "non évalué",
        obstacles=(o,) if o else (),
        obstacle_le_plus_genant=o,
        marge_minimale_m=-10.0 if o else 5.0,
        distance_marge_minimale_m=1000.0,
    )


# ── Le seuil, aux deux bords ────────────────────────────────────────────────


def test_le_seuil_exact_est_inatteignable_et_c_est_verifie():
    """Aucun flottant `f` ne donne `1 - f == 0,01` exactement.

    La conséquence compte : au seuil, « supérieur » et « supérieur ou égal »
    sont indiscernables, parce qu'aucune entrée ne produit l'égalité. Plutôt
    que d'écrire un test de borne qui n'éprouverait rien, on établit
    l'inatteignabilité — et les deux tests suivants éprouvent les deux
    flottants voisins, qui, eux, sont atteignables.
    """
    voisins = {1.0 - f for f in (
        math.nextafter(1.0 - SEUIL_DISCRIMINATION_FRACTION, 0.0),
        1.0 - SEUIL_DISCRIMINATION_FRACTION,
        math.nextafter(1.0 - SEUIL_DISCRIMINATION_FRACTION, 1.0),
    )}
    assert SEUIL_DISCRIMINATION_FRACTION not in voisins


def test_le_flottant_voisin_au_dessus_du_seuil_est_discriminant():
    """Le plus petit dépassement du seuil que l'arithmétique permette."""
    v = juger(analyse(1.0 - SEUIL_DISCRIMINATION_FRACTION),
              analyse(1.0 - 0.30), 100.0)
    assert 1.0 - (1.0 - SEUIL_DISCRIMINATION_FRACTION) > SEUIL_DISCRIMINATION_FRACTION
    assert v.discriminante is True
    assert v.seuil_applique == SEUIL_DISCRIMINATION_FRACTION


def test_le_flottant_voisin_sous_le_seuil_n_est_pas_discriminant():
    dessous = math.nextafter(1.0 - SEUIL_DISCRIMINATION_FRACTION, 1.0)
    assert 1.0 - dessous < SEUIL_DISCRIMINATION_FRACTION
    v = juger(analyse(dessous), analyse(1.0 - 0.30), 100.0)
    assert v.discriminante is False
    assert "presque rien" in v.motif


def test_une_cible_entierement_visible_ne_departage_rien():
    """Les deux modèles prédisent 100 % visible : il n'y a rien à comparer."""
    v = juger(analyse(1.0), analyse(1.0), 100.0)
    assert v.discriminante is False
    assert v.fraction_cachee_min == pytest.approx(0.0)


def test_une_cible_entierement_sous_l_horizon_departage():
    """Le modèle plan la montre entière, le sphérique pas du tout.

    C'est le cas le plus discriminant qui soit, et une règle mal écrite
    pourrait l'exclure en ne regardant que « partiellement caché ».
    """
    v = juger(analyse(0.0), analyse(0.0), 100.0)
    assert v.discriminante is True
    assert v.fraction_cachee_min == pytest.approx(1.0)


# ── L'enveloppe se lit par son bord défavorable ─────────────────────────────


def test_c_est_le_bord_le_plus_favorable_au_modele_plan_qui_decide():
    """Une borne discriminante et l'autre non : le verdict suit la mauvaise.

    Sinon l'outil annoncerait « discriminante » sur une visée dont une
    réfraction plausible suffit à effacer l'écart.
    """
    v = juger(analyse(1.0 - 0.50), analyse(1.0 - 0.001), 100.0)
    assert v.discriminante is False
    assert v.fraction_cachee_min == pytest.approx(0.001)
    assert v.fraction_cachee_max == pytest.approx(0.50)


def test_l_ordre_des_deux_bornes_ne_change_rien():
    """L'appelant n'a pas à savoir laquelle des deux cache le plus."""
    a, b = analyse(1.0 - 0.50), analyse(1.0 - 0.001)
    assert juger(a, b, 100.0) == juger(b, a, 100.0)


# ── Le relief prime ─────────────────────────────────────────────────────────


def test_le_relief_qui_masque_rend_la_visee_non_discriminante():
    """Même avec une occultation de courbure énorme.

    Les deux modèles prédisent une cible cachée, pour la même raison, et cette
    raison n'est pas la courbure.
    """
    v = juger(analyse(0.0, obstacle=True), analyse(0.0, obstacle=True), 100.0)
    assert v.discriminante is False
    assert v.masque_par_le_relief is True
    assert "relief" in v.motif


def test_relief_non_evalue_n_est_pas_relief_absent():
    """Un profil manquant ne doit jamais valoir « aucun obstacle »."""
    v = juger(analyse(1.0 - 0.50, relief_evalue=False),
              analyse(1.0 - 0.40, relief_evalue=False), 100.0)
    assert v.masque_par_le_relief is None
    # La courbure décide quand même : ne rien conclure du relief n'empêche pas
    # de lire ce que la courbure implique.
    assert v.discriminante is True


# ── Les hauteurs rendues ────────────────────────────────────────────────────


def test_les_hauteurs_suivent_la_hauteur_de_la_cible():
    v = juger(analyse(1.0 - 0.20), analyse(1.0 - 0.50), 250.0)
    assert v.hauteur_cachee_min_m == pytest.approx(50.0)
    assert v.hauteur_cachee_max_m == pytest.approx(125.0)


def test_hauteur_nulle_refusee():
    """Diviser par une hauteur nulle rendrait des fractions infinies."""
    with pytest.raises(ValueError):
        juger(analyse(1.0), analyse(1.0), 0.0)


# ── Les constantes ──────────────────────────────────────────────────────────


def test_les_constantes_sont_nommees_et_coherentes():
    """Le seuil et l'enveloppe sont des conventions : elles doivent être lisibles."""
    assert SEUIL_DISCRIMINATION_FRACTION == 0.01
    assert K_ENVELOPPE_MIN < K_STANDARD < K_ENVELOPPE_MAX
