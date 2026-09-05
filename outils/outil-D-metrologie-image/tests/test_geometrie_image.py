"""
Le théorème sur lequel repose le contrôle d'horizon, et son inverse.

Le cahier des charges attribuait à l'écart horizon / bas-visible une « hauteur
masquée par la courbure ». Ces tests établissent que cet écart est nul : le
rayon rasant qui définit l'horizon est le même qui définit le point le plus bas
visible de la cible. La conséquence pratique est que le clic 1 n'est pas une
mesure mais un contrôle — c'est ce que `annotation.controler_horizon` en fait.
"""

import math

import pytest
from visee_optique.geometry import Cible, arc_to_tangent, distance_critique
from visee_optique.refraction import rayon_effectif

from metrologie_image.inversion import (
    altitude_visible_la_plus_basse,
    angle_horizon_base,
    angle_portion_visible,
    elevation,
    elevation_horizon,
)
from metrologie_image.optique import MetrologieError

R0 = 6_371_008.8

CONFIGS = [
    # (h_obs m, H m, z_b m, D m, k)
    (10.0, 60.0, 0.0, 40_000.0, 0.13),
    (60.0, 60.0, 0.0, 80_000.0, 0.13),
    (2.0, 120.0, 0.0, 30_000.0, 0.00),
    (300.0, 2706.0, 0.0, 200_000.0, 0.17),
    (25.0, 45.0, 5.0, 55_000.0, 0.40),
    (150.0, 90.0, 0.0, 120_000.0, -0.20),
]


@pytest.mark.parametrize("h,H,z_b,D,k", CONFIGS)
def test_horizon_et_base_confondus(h, H, z_b, D, k):
    """E(z_v, D) = E_horizon exactement, dès que la cible est partiellement occultée.

    C'est le résultat qui prive l'écart horizon/base de toute valeur de mesure
    et lui donne sa valeur de contrôle.
    """
    R = rayon_effectif(R0, k)
    cible = Cible(H=H, z_b=z_b)
    if D <= distance_critique(h, cible, R):
        pytest.skip("configuration sans occultation : le théorème ne s'applique pas")
    z_v = altitude_visible_la_plus_basse(D, h, cible, R)
    # Tolérance 1e-12 rad, et non le zéro machine : `elevation` retranche
    # (R+h) de R·cos ψ, deux nombres de l'ordre de 6·10⁶ dont la différence
    # vaut quelques dizaines. La double précision y laisse ~10⁻⁹ m d'erreur
    # absolue, soit ~10⁻¹⁴ rad sur l'angle. Le résidu est numérique, pas
    # physique : 10⁻¹² rad, c'est 0,2 microseconde d'arc, quand un pixel de
    # ces visées en vaut environ une seconde entière — 5·10⁻⁶ rad.
    assert elevation(z_v, D, h, R) == pytest.approx(elevation_horizon(h, R), abs=1e-12)
    assert angle_horizon_base(D, h, cible, R) == pytest.approx(0.0, abs=1e-12)


@pytest.mark.parametrize("h,H,z_b,D,k", CONFIGS)
def test_residu_de_coincidence_negligeable_devant_un_pixel(h, H, z_b, D, k):
    """Le résidu du théorème vaut moins d'un millionième de pixel.

    Ce test répond à l'objection que la tolérance de 10⁻¹² rad du test
    précédent aurait été choisie pour faire passer le test : le résidu y est
    comparé non pas à un seuil arbitraire, mais au pas angulaire d'un pixel
    d'une visée à 300 mm sur capteur 24×36 — 1,2 seconde d'arc.
    """
    R = rayon_effectif(R0, k)
    cible = Cible(H=H, z_b=z_b)
    if D <= distance_critique(h, cible, R):
        pytest.skip("configuration sans occultation")
    pas_pixel_rad = math.atan((36.0 / 6000) / 300.0)  # ≈ 1,2″
    residu = abs(angle_horizon_base(D, h, cible, R))
    assert residu < pas_pixel_rad * 1e-6


@pytest.mark.parametrize("h,H,z_b,D,k", CONFIGS)
def test_horizon_par_deux_chemins(h, H, z_b, D, k):
    """La dépression de l'horizon, obtenue de deux façons indépendantes.

    D'un côté −s(h)/R, la forme fermée. De l'autre, `elevation` appliquée au
    point de tangence lui-même (z = 0, D = s(h)), qui n'emploie pas cette
    forme mais la relation de triangle géocentrique. Les deux doivent coïncider.
    """
    R = rayon_effectif(R0, k)
    s_h = arc_to_tangent(h, R)
    assert elevation(0.0, s_h, h, R) == pytest.approx(elevation_horizon(h, R), abs=1e-13)


def test_depression_horizon_vaut_la_formule_classique():
    """tan(dépression) = √(2Rh + h²)/R — troisième chemin, purement algébrique."""
    for h in (2.0, 10.0, 100.0, 1000.0):
        R = R0
        attendu = -math.atan(math.sqrt(2 * R * h + h * h) / R)
        assert elevation_horizon(h, R) == pytest.approx(attendu, abs=1e-13)


def test_base_sous_l_horizon_avant_la_distance_critique():
    """En deçà de D_crit, la base est visible — et apparaît SOUS la ligne d'horizon.

    C'est contre-intuitif et c'est pourtant la règle : l'horizon est le point
    le plus haut de la mer dans l'image, puisque l'élévation apparente de la
    surface croît avec la distance jusqu'au point de tangence. Une cible plus
    proche que l'horizon a donc sa base au-dessous de lui, d'un écart qui
    tend vers zéro quand D tend vers D_crit.

    Cet écart, lui, est bien une grandeur mesurable sur l'image — mais ce
    n'est toujours pas une « hauteur masquée par la courbure » : rien n'est
    masqué dans ce régime, la cible est entière.
    """
    R = rayon_effectif(R0, 0.13)
    cible = Cible(H=60.0, z_b=0.0)
    h = 60.0
    d_crit = distance_critique(h, cible, R)
    ecarts = [angle_horizon_base(d_crit * f, h, cible, R) for f in (0.4, 0.6, 0.8, 0.95)]
    assert all(e < 0.0 for e in ecarts)
    assert all(b > a for a, b in zip(ecarts, ecarts[1:]))  # remonte vers 0
    assert angle_horizon_base(d_crit * 0.999, h, cible, R) == pytest.approx(0.0, abs=1e-6)


def test_angle_visible_croit_avec_k():
    """Plus la réfraction courbe le rayon, plus la cible émerge. La monotonie
    n'est pas supposée par la bissection : elle est vérifiée ici."""
    cible = Cible(H=60.0, z_b=0.0)
    h, D = 10.0, 60_000.0
    angles = [
        angle_portion_visible(D, h, cible, rayon_effectif(R0, k))
        for k in [-0.5, -0.2, 0.0, 0.13, 0.3, 0.6, 0.9]
    ]
    assert all(b >= a for a, b in zip(angles, angles[1:]))
    assert angles[-1] > angles[0]


def test_cible_entierement_occultee_donne_un_angle_nul():
    cible = Cible(H=20.0, z_b=0.0)
    R = rayon_effectif(R0, 0.0)
    assert angle_portion_visible(200_000.0, 2.0, cible, R) == 0.0


def test_elevation_refuse_hors_domaine():
    with pytest.raises(MetrologieError):
        elevation(10.0, -1.0, 10.0, R0)
    with pytest.raises(MetrologieError):
        elevation(-1.0, 1000.0, 10.0, R0)
    with pytest.raises(MetrologieError):
        elevation(10.0, 1000.0, 10.0, -R0)


def test_elevation_croit_avec_l_altitude():
    """Monotonie exigée par `altitude_pour_elevation`, qui bissecte dessus."""
    R, D, h = R0, 50_000.0, 20.0
    valeurs = [elevation(z, D, h, R) for z in (0.0, 10.0, 100.0, 1000.0, 10_000.0)]
    assert all(b > a for a, b in zip(valeurs, valeurs[1:]))
