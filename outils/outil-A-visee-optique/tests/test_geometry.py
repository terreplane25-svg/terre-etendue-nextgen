"""
Tests de geometry.py — rejouent les Tableaux 3, 4, 5 et 6 du protocole
« Portion visible d'une cible éloignée au-dessus de la mer » v1.0 comme
fixtures de non-régression. Les valeurs de référence sont recopiées du
document, pas recalculées ailleurs : c'est le protocole lui-même qui
sert de jeu de test.
"""

import math

import pytest

from visee_optique.geometry import (
    Cible,
    GeometryError,
    IUGG_R1,
    altitude_from_arc,
    arc_approx_petit_angle,
    arc_to_tangent,
    distance_critique,
    distance_limite,
    fraction_visible,
    fraction_visible_modele_plan,
    hauteur_occultee,
    hauteur_occultee_approx,
    resoudre_altitude_par_dichotomie,
)

R = IUGG_R1  # sphère de référence du §4.1, utilisée telle quelle dans l'exemple du §10


# --- Tableau 3 : arc exact vs approximation classique √(2Rh) ---

@pytest.mark.parametrize(
    "h, arc_exact_attendu, sqrt2Rh_attendu, ecart_attendu",
    [
        (2, 5048.2, 5048.2, -0.00),
        (100, 35695.7, 35696.0, -0.23),
        (800, 100958.1, 100963.4, -5.28),
        (3107, 198930.6, 198971.0, -40.42),
    ],
)
def test_tableau_3_arc_vs_approximation(h, arc_exact_attendu, sqrt2Rh_attendu, ecart_attendu):
    arc_exact = arc_to_tangent(h, R)
    approx = arc_approx_petit_angle(h, R)
    assert arc_exact == pytest.approx(arc_exact_attendu, abs=0.1)
    assert approx == pytest.approx(sqrt2Rh_attendu, abs=0.1)
    assert (arc_exact - approx) == pytest.approx(ecart_attendu, abs=0.05)


# --- Tableau 4 : hauteur occultée exacte vs approchée, h = 800 m ---

@pytest.mark.parametrize(
    "D_km, c_exact_attendu, c_approx_attendu, ecart_attendu",
    [
        (110.000, 6.416, 6.409, 0.007),
        (120.000, 28.457, 28.441, 0.016),
        (130.000, 66.193, 66.169, 0.025),
        (136.654, 100.001, 99.970, 0.031),
    ],
)
def test_tableau_4_hauteur_occultee_exacte_vs_approchee(
    D_km, c_exact_attendu, c_approx_attendu, ecart_attendu
):
    D = D_km * 1000.0
    h = 800.0
    cible = Cible(H=100.0, z_b=0.0)

    c_exact = hauteur_occultee(D, h, cible, R)
    c_approx = hauteur_occultee_approx(D, h, R)

    assert c_exact == pytest.approx(c_exact_attendu, abs=0.005)
    assert c_approx == pytest.approx(c_approx_attendu, abs=0.005)
    assert (c_exact - c_approx) == pytest.approx(ecart_attendu, abs=0.005)


# --- Tableau 5 : valeurs intermédiaires de l'exemple numérique du §10 ---

def test_tableau_5_valeurs_intermediaires():
    h = 800.0
    cible = Cible(H=100.0, z_b=0.0)

    ratio = R / (R + h)
    assert ratio == pytest.approx(0.999874447, abs=1e-9)

    theta = math.acos(ratio)
    assert theta == pytest.approx(0.015846493, abs=1e-9)

    s_h = arc_to_tangent(h, R)
    assert s_h == pytest.approx(100958.147, abs=0.001)

    s_H = arc_to_tangent(cible.H, R)
    assert s_H == pytest.approx(35695.729, abs=0.001)

    d_crit = distance_critique(h, cible, R)
    assert d_crit == pytest.approx(100958.147, abs=0.001)

    d_lim = distance_limite(h, cible, R)
    assert d_lim == pytest.approx(136653.876, abs=0.001)

    approx_2Rh = arc_approx_petit_angle(h, R)
    assert approx_2Rh == pytest.approx(100963.429, abs=0.001)

    assert (s_h - approx_2Rh) == pytest.approx(-5.282, abs=0.01)


# --- Tableau 6 : hauteur occultée et fraction visible en fonction de D ---

@pytest.mark.parametrize(
    "D_km, c_attendu, fraction_attendue",
    [
        (50.000, 0.000, 1.0000),
        (100.958, 0.000, 1.0000),
        (110.000, 6.416, 0.9358),
        (120.000, 28.457, 0.7154),
        (130.000, 66.193, 0.3381),
        (136.654, 100.001, 0.0000),
    ],
)
def test_tableau_6_fraction_visible(D_km, c_attendu, fraction_attendue):
    D = D_km * 1000.0
    h = 800.0
    cible = Cible(H=100.0, z_b=0.0)

    c = hauteur_occultee(D, h, cible, R)
    f = fraction_visible(D, h, cible, R)

    assert c == pytest.approx(c_attendu, abs=0.005)
    assert f == pytest.approx(fraction_attendue, abs=0.0005)


def test_tableau_6_au_dela_de_D_lim_hauteur_continue_de_croitre():
    """Au-delà de D_lim, c continue de croître au-delà de H (Tableau 6, ligne 140 km) ;
    c'est fraction_visible, bornée à [0;1], qui rend compte de l'occultation totale."""
    D = 140.000 * 1000.0
    h = 800.0
    cible = Cible(H=100.0, z_b=0.0)

    c = hauteur_occultee(D, h, cible, R)
    assert c == pytest.approx(119.627, abs=0.005)
    assert c > cible.H

    f = fraction_visible(D, h, cible, R)
    assert f == 0.0


# --- Modèle P : aucune occultation géométrique ---

def test_modele_plan_toujours_visible():
    for D in (1.0, 1_000.0, 1_000_000.0, 1e8):
        assert fraction_visible_modele_plan(D) == 1.0


def test_modele_plan_rejette_distance_non_positive():
    with pytest.raises(GeometryError):
        fraction_visible_modele_plan(0.0)


# --- §10.3 : résolution numérique indépendante, accord à mieux d'un micromètre ---

@pytest.mark.parametrize("arc", [0.0, 100.0, 35_695.729, 100_958.147, 500_000.0])
def test_dichotomie_egale_forme_fermee(arc):
    x_ferme = altitude_from_arc(arc, R)
    x_dichotomie = resoudre_altitude_par_dichotomie(arc, R, tol=1e-7)
    assert x_dichotomie == pytest.approx(x_ferme, abs=1e-6)


def test_s_puis_inverse_est_identite():
    """arc_to_tangent et altitude_from_arc doivent être des inverses exactes l'une de l'autre."""
    for x in (0.0, 2.0, 100.0, 800.0, 3107.0, 50_000.0):
        arc = arc_to_tangent(x, R)
        assert altitude_from_arc(arc, R) == pytest.approx(x, abs=1e-6)


# --- Garde-fous de domaine ---

def test_altitude_negative_rejetee():
    with pytest.raises(GeometryError):
        arc_to_tangent(-1.0, R)


def test_rayon_non_positif_rejete():
    with pytest.raises(GeometryError):
        arc_to_tangent(100.0, 0.0)
    with pytest.raises(GeometryError):
        altitude_from_arc(100.0, -1.0)


def test_arc_hors_domaine_rejete():
    with pytest.raises(GeometryError):
        altitude_from_arc(R * math.pi / 2, R)  # theta = pi/2 exactement : hors domaine


def test_cible_hauteur_non_positive_rejetee():
    with pytest.raises(GeometryError):
        Cible(H=0.0)
    with pytest.raises(GeometryError):
        Cible(H=-10.0)


def test_cible_altitude_base_negative_rejetee():
    with pytest.raises(GeometryError):
        Cible(H=100.0, z_b=-1.0)
