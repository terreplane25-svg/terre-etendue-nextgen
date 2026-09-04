"""
Tests de geodesy.py — rayon d'Euler, conversion géoïde/ellipsoïde, Tableau 10
et règle d'indépendance du §12.4, avec les valeurs de référence citées au
§12.2 (rayon méridien à l'équateur, grande normale au pôle, écart de ~1 %).
"""

import math

import pytest

from visee_optique.geodesy import (
    GRS80_A,
    GRS80_B,
    GRS80_E2,
    GRS80_F,
    ConversionGeoide,
    GeodesyError,
    GrandeurGeodesique,
    TABLEAU_10,
    altitude_depuis_hauteur_ellipsoidale,
    incertitude_typique,
    rayon_euler,
    rayon_grande_normale,
    rayon_meridien,
)
from visee_optique.geometry import IUGG_R1


# --- §4.1 / §12.2 : cohérence de l'ellipsoïde GRS80 avec IUGG_R1 ---

def test_grs80_redonne_iugg_r1():
    r1 = (2 * GRS80_A + GRS80_B) / 3.0
    assert r1 == pytest.approx(IUGG_R1, abs=0.1)


def test_grs80_e2_coherent_avec_a_et_b():
    e2_attendu = 1.0 - (GRS80_B / GRS80_A) ** 2
    assert GRS80_E2 == pytest.approx(e2_attendu, abs=1e-12)


# --- §12.2 : valeurs de référence citées dans le protocole ---

def test_rayon_meridien_equateur():
    # « rayon méridien à l'équateur, 6 335,4 km » (§12.2)
    assert rayon_meridien(0.0) == pytest.approx(6_335_439.3, abs=100.0)


def test_grande_normale_pole():
    # « grande normale au pôle, 6 399,6 km » (§12.2)
    assert rayon_grande_normale(90.0) == pytest.approx(6_399_593.6, abs=100.0)


def test_grande_normale_equateur_egale_a():
    assert rayon_grande_normale(0.0) == pytest.approx(GRS80_A, abs=1e-6)


def test_ecart_meridien_normale_environ_1_pourcent():
    ecart_km = (rayon_grande_normale(90.0) - rayon_meridien(0.0)) / 1000.0
    assert ecart_km == pytest.approx(64.2, abs=0.1)  # §12.2 : « l'écart atteint 64,2 km »
    ecart_relatif = (rayon_grande_normale(90.0) - rayon_meridien(0.0)) / IUGG_R1
    assert ecart_relatif == pytest.approx(0.0101, abs=0.0005)  # « soit 1,01 % »


# --- Rayon d'Euler : cas particuliers et valeurs redérivées ---

def test_rayon_euler_azimut_nord_egale_meridien():
    for latitude in (0.0, 30.0, 48.0, 75.0):
        assert rayon_euler(latitude, 0.0) == pytest.approx(rayon_meridien(latitude))


def test_rayon_euler_azimut_est_egale_grande_normale():
    for latitude in (0.0, 30.0, 48.0, 75.0):
        assert rayon_euler(latitude, 90.0) == pytest.approx(rayon_grande_normale(latitude))


def test_rayon_euler_valeurs_redérivées():
    assert rayon_euler(0.0, 45.0) == pytest.approx(6_356_716.46, abs=0.5)
    assert rayon_euler(48.0, 30.0) == pytest.approx(6_375_531.30, abs=0.5)


def test_rayon_euler_est_toujours_entre_meridien_et_normale():
    for latitude in (10.0, 48.0, 65.0):
        m = rayon_meridien(latitude)
        n = rayon_grande_normale(latitude)
        for azimut in (0.0, 15.0, 60.0, 90.0, 180.0, 270.0):
            r = rayon_euler(latitude, azimut)
            assert min(m, n) - 1.0 <= r <= max(m, n) + 1.0


def test_substituer_r1_change_la_hauteur_occultee_de_plusieurs_pour_cent():
    """Objection n°1 (§31) chiffrée : à une latitude et un azimut défavorables, l'écart
    entre R1 et le rayon d'Euler dépasse l'erreur de l'approximation corde-arc du §9.4."""
    r_euler = rayon_euler(48.0, 90.0)  # grande normale à 48° : la plus éloignée de R1 à cette latitude
    ecart_relatif = abs(r_euler - IUGG_R1) / IUGG_R1
    assert ecart_relatif > 0.001  # bien supérieur au sous-pourcent de l'approximation §9.4


# --- Validation de domaine ---

@pytest.mark.parametrize("latitude", [-91.0, 91.0, 180.0])
def test_latitude_hors_bornes_rejetee(latitude):
    with pytest.raises(GeodesyError):
        rayon_meridien(latitude)


@pytest.mark.parametrize("azimut", [-1.0, 360.0, 400.0])
def test_azimut_hors_bornes_rejete(azimut):
    with pytest.raises(GeodesyError):
        rayon_euler(48.0, azimut)


# --- §12.1 : conversion géoïde / ellipsoïde ---

def test_conversion_geoide_arithmetique():
    conversion = ConversionGeoide(ondulation_m=45.3, modele="EGM2008", source="grille publiée, point le plus proche")
    altitude = altitude_depuis_hauteur_ellipsoidale(120.0, conversion)
    assert altitude == pytest.approx(120.0 - 45.3)


def test_conversion_geoide_exige_modele_et_source():
    with pytest.raises(GeodesyError):
        ConversionGeoide(ondulation_m=45.0, modele="", source="grille")
    with pytest.raises(GeodesyError):
        ConversionGeoide(ondulation_m=45.0, modele="EGM2008", source="  ")


# --- §12.3 : Tableau 10 ---

def test_tableau_10_a_huit_postes():
    assert len(TABLEAU_10) == 8


def test_incertitude_typique_position_observateur():
    assert incertitude_typique("Position horizontale de l'observateur") == (0.1, 5.0)


def test_incertitude_typique_hauteur_cible():
    assert incertitude_typique("Hauteur de la cible") == (0.1, 1.0)


def test_incertitude_typique_poste_inconnu():
    with pytest.raises(GeodesyError):
        incertitude_typique("Poste inexistant")


# --- §12.4 : règle d'indépendance ---

def test_grandeur_geodesique_valide():
    g = GrandeurGeodesique(
        nom="Altitude de la base de la cible",
        valeur=0.0,
        unite="m",
        referentiel="altitude normale",
        source="marégraphe local, corrigé de la marée",
        incertitude=0.3,
    )
    assert g.valeur == 0.0


@pytest.mark.parametrize(
    "source",
    ["estimée depuis la photographie", "mesurée sur l'image", "d'après le cliché", "Photo du 3/9/2026"],
)
def test_grandeur_geodesique_rejette_source_photographique(source):
    with pytest.raises(GeodesyError):
        GrandeurGeodesique(
            nom="Hauteur de la cible", valeur=100.0, unite="m",
            referentiel="—", source=source, incertitude=1.0,
        )


def test_grandeur_geodesique_exige_tous_les_champs():
    with pytest.raises(GeodesyError):
        GrandeurGeodesique(nom="", valeur=1.0, unite="m", referentiel="ITRF", source="GNSS", incertitude=0.1)
    with pytest.raises(GeodesyError):
        GrandeurGeodesique(nom="x", valeur=1.0, unite="", referentiel="ITRF", source="GNSS", incertitude=0.1)
    with pytest.raises(GeodesyError):
        GrandeurGeodesique(nom="x", valeur=1.0, unite="m", referentiel="", source="GNSS", incertitude=0.1)
    with pytest.raises(GeodesyError):
        GrandeurGeodesique(nom="x", valeur=1.0, unite="m", referentiel="ITRF", source="  ", incertitude=0.1)


def test_grandeur_geodesique_rejette_incertitude_negative():
    with pytest.raises(GeodesyError):
        GrandeurGeodesique(
            nom="x", valeur=1.0, unite="m", referentiel="ITRF", source="GNSS", incertitude=-0.1
        )
