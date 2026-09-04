"""
test_vincenty.py — La géodésique inverse et directe (§12.3).

Ces deux fonctions vivaient hors du paquet, en cinq copies, donc sans
couverture. Ce sont pourtant elles qui produisent le D et l'azimut dont
dépendent le rayon d'Euler et toute la géométrie du §9 : une erreur ici
se propage à tout le reste sans rien déclencher.

Les contrôles ci-dessous n'opposent pas Vincenty à lui-même. Deux d'entre
eux la confrontent à des résultats obtenus autrement :

  · sur l'équateur, la géodésique EST l'équateur, donc la distance vaut
    exactement a·Δλ — un résultat analytique, indépendant de la formule ;
  · sur un méridien, la distance vaut l'intégrale du rayon méridien, que
    l'on calcule ici par quadrature, sans passer par Vincenty.

Le reste vérifie les propriétés qu'une géodésique doit avoir de toute
façon : symétrie, bouclage inverse→direct, et refus explicite là où la
méthode est connue pour échouer.
"""

import math

import pytest

from visee_optique.geodesy import (
    GRS80_A,
    GRS80_E2,
    GRS80_F,
    GeodesyError,
    rayon_meridien,
    vincenty_direct,
    vincenty_inverse,
)


# --- Confrontation à des résultats obtenus sans Vincenty ---


@pytest.mark.parametrize("delta_lon", [0.5, 5.0, 40.0, 120.0])
def test_sur_equateur_la_distance_vaut_exactement_a_delta_lambda(delta_lon):
    """Sur l'équateur, la géodésique est l'équateur : D = a·Δλ, analytiquement."""
    r = vincenty_inverse(0.0, 0.0, 0.0, delta_lon)
    attendu = GRS80_A * math.radians(delta_lon)
    # 0,5 mm est la précision que Vincenty revendique ; l'écart observé sur
    # 13 000 km vaut 6 µm, soit une erreur relative de 4·10⁻¹³ — c'est la
    # troncature de la série, pas un défaut d'implémentation.
    assert r.distance_m == pytest.approx(attendu, abs=5e-4)
    assert r.azimut_depart_deg == pytest.approx(90.0, abs=1e-9)
    # α₂ est l'azimut À L'ARRIVÉE dans le même sens de parcours, pas le
    # gisement de retour : vers l'est, il vaut 90° et non 270°.
    assert r.azimut_arrivee_deg == pytest.approx(90.0, abs=1e-9)
    assert (r.azimut_arrivee_deg + 180.0) % 360.0 == pytest.approx(270.0, abs=1e-9)


def _arc_meridien_par_quadrature(lat1_deg, lat2_deg, n=200_001):
    """∫ M(φ) dφ par Simpson — indépendant de Vincenty."""
    p1, p2 = math.radians(lat1_deg), math.radians(lat2_deg)
    h = (p2 - p1) / (n - 1)
    total = 0.0
    for i in range(n):
        phi = p1 + i * h
        poids = 1 if i in (0, n - 1) else (4 if i % 2 else 2)
        total += poids * rayon_meridien(math.degrees(phi), GRS80_A, GRS80_E2)
    return total * h / 3.0


@pytest.mark.parametrize("lat1,lat2", [(0.0, 1.0), (44.0, 46.0), (10.0, 60.0)])
def test_sur_un_meridien_la_distance_vaut_l_integrale_du_rayon_meridien(lat1, lat2):
    """Le long d'un méridien, D = ∫M(φ)dφ, calculée ici par quadrature."""
    r = vincenty_inverse(lat1, 3.0, lat2, 3.0)
    attendu = _arc_meridien_par_quadrature(lat1, lat2)
    assert r.distance_m == pytest.approx(attendu, abs=1e-3)
    assert r.azimut_depart_deg == pytest.approx(0.0, abs=1e-9)


# --- Propriétés que toute géodésique doit avoir ---


CAS = [
    (50.94642, 1.75305, 51.13152, 1.338825),   # Sangatte → South Foreland
    (0.0, 0.0, 10.0, 10.0),
    (45.1, -1.2, 45.9, -0.9),
    (-33.9, 18.4, -37.8, 144.9),               # Le Cap → Melbourne
    (78.2, 15.6, -54.8, -68.3),                # longue, forte latitude
]


@pytest.mark.parametrize("lat1,lon1,lat2,lon2", CAS)
def test_bouclage_inverse_puis_direct(lat1, lon1, lat2, lon2):
    """Partir de A dans l'azimut trouvé, sur la distance trouvée, doit rendre B."""
    r = vincenty_inverse(lat1, lon1, lat2, lon2)
    lat3, lon3 = vincenty_direct(lat1, lon1, r.azimut_depart_deg, r.distance_m)
    ecart_m = math.hypot(
        (lat3 - lat2) * 111_320.0,
        (lon3 - lon2) * 111_320.0 * math.cos(math.radians(lat2)),
    )
    assert ecart_m < 1e-4


@pytest.mark.parametrize("lat1,lon1,lat2,lon2", CAS)
def test_symetrie_des_distances_et_des_azimuts(lat1, lon1, lat2, lon2):
    aller = vincenty_inverse(lat1, lon1, lat2, lon2)
    retour = vincenty_inverse(lat2, lon2, lat1, lon1)
    assert aller.distance_m == pytest.approx(retour.distance_m, abs=1e-6)
    # α₂ de l'aller, tourné d'un demi-tour, est l'azimut de départ du retour.
    assert (aller.azimut_arrivee_deg - 180.0) % 360.0 == pytest.approx(
        retour.azimut_depart_deg % 360.0, abs=1e-7
    )


def test_points_confondus_distance_nulle_et_azimut_non_defini():
    """Un azimut de 0° aurait l'air d'une direction mesurée. C'est NaN."""
    r = vincenty_inverse(43.5, 1.48, 43.5, 1.48)
    assert r.distance_m == 0.0
    assert math.isnan(r.azimut_depart_deg)
    assert math.isnan(r.azimut_arrivee_deg)
    assert r.converge is True


# --- Refus explicites ---


def test_quasi_antipodal_leve_plutot_que_de_rendre_le_dernier_itere():
    """Vincenty ne converge pas près des antipodes : ne rien retourner."""
    with pytest.raises(GeodesyError, match="convergé"):
        vincenty_inverse(0.0, 0.0, 0.0, 179.5)


@pytest.mark.parametrize("lat", [-90.5, 90.5, 1000.0])
def test_latitude_hors_domaine(lat):
    with pytest.raises(GeodesyError):
        vincenty_inverse(lat, 0.0, 0.0, 0.0)


def test_distance_negative_refusee_en_direct():
    with pytest.raises(GeodesyError):
        vincenty_direct(43.5, 1.48, 90.0, -1.0)


# --- Repère de non-régression ---


def test_valeur_de_reference_des_cinq_copies_anterieures():
    """Les cinq copies hors paquet donnaient toutes cette valeur : elle est figée.

    Si ce test casse, ce n'est pas la promotion dans le paquet qui a
    changé le résultat — c'est autre chose, et il faut le savoir.
    """
    r = vincenty_inverse(50.94642, 1.75305, 51.13152, 1.338825)
    assert r.distance_m == pytest.approx(35_610.736137, abs=1e-6)
    assert r.azimut_depart_deg == pytest.approx(305.488930006, abs=1e-9)


def test_convergence_rapide_sur_un_cas_courant():
    """Une visée côtière converge en quelques tours ; le compteur l'atteste."""
    r = vincenty_inverse(50.94642, 1.75305, 51.13152, 1.338825)
    assert r.converge is True
    assert r.iterations <= 10


def test_l_aplatissement_compte():
    """Sur une sphère (f = 0) la distance diffère : l'ellipsoïde n'est pas décoratif."""
    ell = vincenty_inverse(0.0, 0.0, 60.0, 0.0)
    sph = vincenty_inverse(0.0, 0.0, 60.0, 0.0, a=GRS80_A, f=0.0)
    assert abs(ell.distance_m - sph.distance_m) > 10_000.0
    assert GRS80_F > 0.0
