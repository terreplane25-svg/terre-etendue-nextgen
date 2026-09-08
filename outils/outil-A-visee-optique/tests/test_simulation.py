"""
La règle de lecture du simulateur : quand une visée départage, et quand non.

CE QUE CES TESTS ÉTABLISSENT
────────────────────────────
Que la grandeur jugée est bien l'occultation À LA BASE de la cible ; que le
seuil est appliqué à sa valeur nommée, des deux côtés ; que le relief prime sur
la courbure ; que l'enveloppe de réfraction est lue par son bord le plus
DÉFAVORABLE ; et que le pas d'échantillonnage s'élargit avec la distance sans
jamais la borner.

Le test qui compte le plus est celui du relief : une cible bloquée par une
colline est bloquée dans les deux modèles, pour une raison qui n'est pas la
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
    PAS_COURT_M,
    PAS_LONG_M,
    PAS_MOYEN_M,
    SEUIL_DISCRIMINATION_FRACTION,
    SEUIL_DISTANCE_LONGUE_M,
    SEUIL_DISTANCE_MOYENNE_M,
    juger,
    pas_echantillonnage_m,
)

H = 100.0


def analyse(masquee_m, obstacle=False, relief_evalue=True, distance_obstacle=500.0):
    """Une analyse de relief réduite à ce que la règle de lecture consulte.

    `masquee_m` est la hauteur occultée EN PARTANT DE LA BASE. Elle peut
    dépasser la hauteur de la cible : au-delà de la distance limite, elle
    continue de croître et dit de combien la cible est sous l'horizon.
    """
    o = Obstacle(distance_obstacle, 50.0, 40.0, 10.0) if obstacle else None
    return AnalyseRelief(
        modele="sphérique",
        rayon_effectif_m=7_000_000.0,
        hauteur_occultee_courbure_m=masquee_m,
        fraction_visible_courbure=min(1.0, max(0.0, (H - masquee_m) / H)),
        relief_evalue=relief_evalue,
        motif_relief_non_evalue=None if relief_evalue else "non évalué",
        obstacles=(o,) if o else (),
        obstacle_le_plus_genant=o,
        marge_minimale_m=-10.0 if o else 5.0,
        distance_marge_minimale_m=distance_obstacle,
    )


# ── Ce qui est jugé : la base, pas le sommet ────────────────────────────────


def test_c_est_l_occultation_a_la_base_qui_est_rendue():
    """Et elle N'EST PAS bornée à la hauteur de la cible.

    Au-delà de la distance limite, `c` continue de croître : la borner à H
    perdrait l'information au moment où elle devient la plus parlante.
    """
    v = juger(analyse(2042.0), analyse(2500.0), 300.0)
    assert v.hauteur_masquee_base_min_m == pytest.approx(2042.0)
    assert v.hauteur_masquee_base_max_m == pytest.approx(2500.0)
    assert v.fraction_masquee_base_min > 1.0, "la fraction a été bornée à 1"
    assert v.discriminante is True


def test_le_sommet_encore_visible_n_empeche_pas_de_discriminer():
    """Le pied disparaît bien avant le sommet : c'est lui qu'on regarde.

    15 m masqués sur 100 m : le sommet reste entièrement visible, et pourtant
    les deux modèles prédisent des choses nettement différentes.
    """
    v = juger(analyse(15.0), analyse(40.0), H)
    assert v.discriminante is True
    assert v.hauteur_masquee_base_min_m == pytest.approx(15.0)


# ── Le seuil, aux deux bords ────────────────────────────────────────────────


def test_au_seuil_exact_la_visee_discrimine():
    """10 % pile passe : le seuil est inclusif, et ici l'égalité est atteignable."""
    v = juger(analyse(H * SEUIL_DISCRIMINATION_FRACTION), analyse(40.0), H)
    assert v.fraction_masquee_base_min == pytest.approx(SEUIL_DISCRIMINATION_FRACTION)
    assert v.discriminante is True
    assert v.seuil_applique == SEUIL_DISCRIMINATION_FRACTION


def test_juste_sous_le_seuil_la_visee_ne_discrimine_pas():
    v = juger(analyse(math.nextafter(H * SEUIL_DISCRIMINATION_FRACTION, 0.0)),
              analyse(40.0), H)
    assert v.discriminante is False
    assert "sous le seuil" in v.motif


def test_une_cible_intacte_ne_departage_rien():
    """Rien de masqué : les deux modèles prédisent la même chose."""
    v = juger(analyse(0.0), analyse(0.0), H)
    assert v.discriminante is False
    assert v.fraction_masquee_base_min == pytest.approx(0.0)


# ── L'enveloppe se lit par son bord défavorable ─────────────────────────────


def test_c_est_le_bord_le_plus_favorable_au_modele_plan_qui_decide():
    """Une borne discriminante et l'autre non : le verdict suit la mauvaise.

    Sinon l'outil annoncerait « discriminante » sur une visée dont une
    réfraction plausible suffit à effacer l'écart.
    """
    v = juger(analyse(50.0), analyse(1.0), H)
    assert v.discriminante is False
    assert v.hauteur_masquee_base_min_m == pytest.approx(1.0)
    assert v.hauteur_masquee_base_max_m == pytest.approx(50.0)


def test_l_ordre_des_deux_bornes_ne_change_rien():
    """L'appelant n'a pas à savoir laquelle des deux masque le plus."""
    a, b = analyse(50.0), analyse(1.0)
    assert juger(a, b, H) == juger(b, a, H)


# ── Le relief prime, et il est LOCALISÉ ─────────────────────────────────────


def test_le_relief_qui_bloque_rend_la_visee_non_discriminante():
    """Même avec une occultation de courbure énorme.

    Les deux modèles prédisent une cible bloquée, pour la même raison, et
    cette raison n'est pas la courbure.
    """
    v = juger(analyse(90.0, obstacle=True), analyse(95.0, obstacle=True), H)
    assert v.discriminante is False
    assert v.masque_par_le_relief is True


def test_le_bandeau_dit_OU_le_relief_bloque():
    """« Bloquée par le relief » sans dire où n'apprend rien à personne.

    C'est la distance de l'obstacle qui permet d'aller le vérifier sur une
    carte, et de comprendre que le problème est à 500 m, pas à l'horizon.
    """
    v = juger(analyse(90.0, obstacle=True, distance_obstacle=500.0),
              analyse(95.0, obstacle=True, distance_obstacle=500.0), H)
    assert "0,50 km" in v.motif
    assert "relief local" in v.motif
    assert v.distance_obstacle_m == pytest.approx(500.0)
    assert "empêche d'évaluer la courbure à grande distance" in v.motif


def test_relief_non_evalue_donne_un_verdict_sous_reserve():
    """Un profil manquant ne vaut ni « dégagé » ni « bloqué ».

    Bloquer tout verdict rendrait l'outil inutilisable dès que le service
    altimétrique est en panne ; présumer le trajet dégagé serait un mensonge.
    Le verdict porte donc sur la courbure, et la réserve est rendue avec.
    """
    v = juger(analyse(50.0, relief_evalue=False), analyse(60.0, relief_evalue=False), H)
    assert v.masque_par_le_relief is None
    assert v.discriminante is True
    assert v.reserve_relief is True
    assert "présumée, pas établie" in v.motif


def test_relief_evalue_et_degage_ne_porte_aucune_reserve():
    v = juger(analyse(50.0), analyse(60.0), H)
    assert v.masque_par_le_relief is False
    assert v.reserve_relief is False
    assert "entièrement dégagée" in v.motif


# ── Le pas d'échantillonnage : il s'élargit, il ne borne pas ────────────────


@pytest.mark.parametrize("distance_km,attendu", [
    (1, PAS_COURT_M),
    (35.61, PAS_COURT_M),
    (99.999, PAS_COURT_M),
    (100, PAS_MOYEN_M),
    (300, PAS_MOYEN_M),
    (499.999, PAS_MOYEN_M),
    (500, PAS_LONG_M),
    (2000, PAS_LONG_M),
    (20000, PAS_LONG_M),
])
def test_le_pas_suit_la_distance(distance_km, attendu):
    assert pas_echantillonnage_m(distance_km * 1000.0) == attendu


def test_aucune_distance_n_est_refusee():
    """La moitié du tour de la Terre doit passer sans lever."""
    assert pas_echantillonnage_m(20_000_000.0) == PAS_LONG_M


def test_le_pas_variable_divise_le_nombre_de_points_par_huit():
    """C'est la raison d'être du pas variable, et elle se mesure.

    Elle ne PLAFONNE pas le nombre de points : à 20 000 km il en reste 10 000.
    Le test compare donc au pas fixe, ce que l'élargissement fait réellement,
    au lieu d'affirmer une borne qui n'existe pas.
    """
    for km in (500, 1000, 2000, 20000):
        d = km * 1000.0
        avec = d / pas_echantillonnage_m(d) + 1
        sans = d / PAS_COURT_M + 1
        assert avec <= sans / 7.9, "%d km : %d points au lieu de %d" % (km, avec, sans)


def test_la_moitie_du_tour_de_la_terre_passe_et_coute_ce_qu_elle_coute():
    """Aucune borne cachée : le coût est celui-là, et il est écrit."""
    d = 20_000_000.0
    points = d / pas_echantillonnage_m(d) + 1
    assert points == pytest.approx(10_001.0)


def test_distance_nulle_refusee():
    with pytest.raises(ValueError):
        pas_echantillonnage_m(0.0)


# ── Les constantes ──────────────────────────────────────────────────────────


def test_hauteur_nulle_refusee():
    """Diviser par une hauteur nulle rendrait des fractions infinies."""
    with pytest.raises(ValueError):
        juger(analyse(0.0), analyse(0.0), 0.0)


def test_les_constantes_sont_nommees_et_coherentes():
    """Seuil, enveloppe et pas sont des conventions : elles doivent être lisibles."""
    assert SEUIL_DISCRIMINATION_FRACTION == 0.10
    assert K_ENVELOPPE_MIN < K_STANDARD < K_ENVELOPPE_MAX
    assert PAS_COURT_M < PAS_MOYEN_M < PAS_LONG_M
    assert SEUIL_DISTANCE_MOYENNE_M < SEUIL_DISTANCE_LONGUE_M
