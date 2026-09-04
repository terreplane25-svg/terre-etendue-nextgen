"""
Tests de atmosphere.py — classes A à E (Tableau 13, §21.2), contraintes de
distance et de temps des classes B et C, résolution du profil vertical
(§21.1), la moyenne piège du §11.5, et la réponse à l'insuffisance de
données du §21.3.
"""

from datetime import datetime, timezone

import pytest

from visee_optique.atmosphere import (
    AtmosphereError,
    ClasseDonnee,
    CoucheK,
    DonneeAtmospherique,
    PointProfil,
    ProfilVertical,
    definition,
    indique_inversion_probable,
    intervalle_k_faute_de_donnee_resolue,
    moyenne_ponderee_en_hauteur,
    resolution_par_mesure_directe,
    statut_au_rapport,
    verifier_resolution,
)
from visee_optique.refraction import HypotheseRefraction, RegimeRefraction


def _horodatage():
    return datetime(2026, 9, 3, 10, 0, tzinfo=timezone.utc)


# --- Tableau 13 : statut au rapport (colonne exacte du protocole) ---

@pytest.mark.parametrize(
    "classe, statut_attendu",
    [
        (ClasseDonnee.A, "mesure"),
        (ClasseDonnee.B, "mesure déportée"),
        (ClasseDonnee.C, "mesure de surface"),
        (ClasseDonnee.D, "valeur calculée"),
        (ClasseDonnee.E, "déclarative"),
    ],
)
def test_tableau_13_statut_au_rapport(classe, statut_attendu):
    assert statut_au_rapport(classe) == statut_attendu


def test_toutes_les_classes_ont_une_definition():
    for classe in ClasseDonnee:
        assert definition(classe)  # non vide


# --- §21.3 : donnée suffisante = au moins une classe A ou B ---

@pytest.mark.parametrize(
    "classes, attendu",
    [
        ([ClasseDonnee.A], True),
        ([ClasseDonnee.B], True),
        ([ClasseDonnee.C, ClasseDonnee.D, ClasseDonnee.E], False),
        ([], False),
    ],
)
def test_resolution_par_mesure_directe(classes, attendu):
    assert resolution_par_mesure_directe(classes) is attendu


# --- §21.1 : indicateur air-mer ---

def test_indique_inversion_probable():
    assert indique_inversion_probable(290.0, 288.0) is True
    assert indique_inversion_probable(286.0, 288.0) is False
    assert indique_inversion_probable(288.0, 288.0) is False


def test_indique_inversion_probable_rejette_temperatures_non_positives():
    with pytest.raises(AtmosphereError):
        indique_inversion_probable(0.0, 288.0)
    with pytest.raises(AtmosphereError):
        indique_inversion_probable(288.0, -1.0)


# --- DonneeAtmospherique : contraintes de distance et de temps (Tableau 13) ---

def test_donnee_classe_a_sans_contrainte():
    d = DonneeAtmospherique(
        grandeur="température", valeur=288.0, unite="K",
        classe=ClasseDonnee.A, source="thermomètre étalonné au point de vue",
        horodatage=_horodatage(),
    )
    assert d.classe is ClasseDonnee.A


def test_donnee_classe_b_dans_les_limites():
    d = DonneeAtmospherique(
        grandeur="température", valeur=286.0, unite="K",
        classe=ClasseDonnee.B, source="radiosondage Météo-France",
        horodatage=_horodatage(), distance_au_site_km=80.0, ecart_temporel_h=2.0,
    )
    assert d.distance_au_site_km == 80.0


@pytest.mark.parametrize("distance_km, ecart_h", [(150.0, 1.0), (50.0, 5.0)])
def test_donnee_classe_b_hors_limites_rejetee(distance_km, ecart_h):
    with pytest.raises(AtmosphereError):
        DonneeAtmospherique(
            grandeur="température", valeur=286.0, unite="K",
            classe=ClasseDonnee.B, source="radiosondage",
            horodatage=_horodatage(), distance_au_site_km=distance_km, ecart_temporel_h=ecart_h,
        )


def test_donnee_classe_b_sans_distance_ni_ecart_rejetee():
    with pytest.raises(AtmosphereError):
        DonneeAtmospherique(
            grandeur="température", valeur=286.0, unite="K",
            classe=ClasseDonnee.B, source="radiosondage", horodatage=_horodatage(),
        )


@pytest.mark.parametrize("distance_km, ecart_h", [(40.0, 0.5), (20.0, 2.0)])
def test_donnee_classe_c_hors_limites_rejetee(distance_km, ecart_h):
    with pytest.raises(AtmosphereError):
        DonneeAtmospherique(
            grandeur="température", valeur=286.0, unite="K",
            classe=ClasseDonnee.C, source="station officielle",
            horodatage=_horodatage(), distance_au_site_km=distance_km, ecart_temporel_h=ecart_h,
        )


def test_donnee_exige_source():
    with pytest.raises(AtmosphereError):
        DonneeAtmospherique(
            grandeur="température", valeur=286.0, unite="K",
            classe=ClasseDonnee.E, source="   ", horodatage=_horodatage(),
        )


# --- PointProfil et ProfilVertical ---

def test_point_profil_rejette_altitude_negative():
    with pytest.raises(AtmosphereError):
        PointProfil(altitude_m=-1.0, temperature_K=288.0)


def test_point_profil_rejette_temperature_non_positive():
    with pytest.raises(AtmosphereError):
        PointProfil(altitude_m=0.0, temperature_K=0.0)


def _profil_conforme(altitude_max=800.0):
    points = [PointProfil(z, 288.0 - 0.0065 * z) for z in range(0, 101, 10)]
    z = 200.0
    while z <= altitude_max:
        points.append(PointProfil(z, 288.0 - 0.0065 * z))
        z += 100.0
    return ProfilVertical(points=tuple(points), classe=ClasseDonnee.A, source="radiosondage test")


def test_profil_vertical_rejette_moins_de_deux_points():
    with pytest.raises(AtmosphereError):
        ProfilVertical(points=(PointProfil(0.0, 288.0),), classe=ClasseDonnee.A, source="s")


def test_profil_vertical_rejette_altitudes_non_triees():
    with pytest.raises(AtmosphereError):
        ProfilVertical(
            points=(PointProfil(10.0, 287.0), PointProfil(0.0, 288.0)),
            classe=ClasseDonnee.A, source="s",
        )


def test_profil_vertical_rejette_doublon_altitude():
    with pytest.raises(AtmosphereError):
        ProfilVertical(
            points=(PointProfil(0.0, 288.0), PointProfil(0.0, 287.0)),
            classe=ClasseDonnee.A, source="s",
        )


def test_profil_vertical_exige_source():
    with pytest.raises(AtmosphereError):
        ProfilVertical(
            points=(PointProfil(0.0, 288.0), PointProfil(10.0, 287.9)),
            classe=ClasseDonnee.A, source=" ",
        )


def test_gradient_moyen_interpolation_lineaire():
    profil = ProfilVertical(
        points=(PointProfil(0.0, 288.0), PointProfil(100.0, 287.0)),
        classe=ClasseDonnee.A, source="test",
    )
    assert profil.gradient_moyen_K_par_m(0.0, 100.0) == pytest.approx(-0.01)
    # interpolation au milieu du segment
    assert profil._temperature_a(50.0) == pytest.approx(287.5)


def test_gradient_couche_basse_convertit_en_K_par_km():
    profil = ProfilVertical(
        points=(PointProfil(0.0, 288.0), PointProfil(60.0, 287.4)),
        classe=ClasseDonnee.A, source="test",
    )
    # -0,01 K/m sur 60 m -> -10 K/km
    assert profil.gradient_couche_basse_K_par_km(epaisseur_m=60.0) == pytest.approx(-10.0)


def test_temperature_hors_profil_rejetee():
    profil = ProfilVertical(
        points=(PointProfil(0.0, 288.0), PointProfil(100.0, 287.0)),
        classe=ClasseDonnee.A, source="test",
    )
    with pytest.raises(AtmosphereError):
        profil._temperature_a(200.0)


# --- §21.1 : vérification de la résolution du profil ---

def test_profil_conforme_passe_la_verification():
    verifier_resolution(_profil_conforme(800.0), altitude_observateur=800.0)  # ne lève pas


def test_profil_ne_debutant_pas_pres_de_la_surface_rejete():
    points = (PointProfil(20.0, 288.0), PointProfil(800.0, 280.0))
    profil = ProfilVertical(points=points, classe=ClasseDonnee.A, source="test")
    with pytest.raises(AtmosphereError):
        verifier_resolution(profil, altitude_observateur=800.0)


def test_profil_natteignant_pas_laltitude_observateur_rejete():
    points = tuple(PointProfil(z, 288.0 - 0.0065 * z) for z in range(0, 101, 10))
    profil = ProfilVertical(points=points, classe=ClasseDonnee.A, source="test")
    with pytest.raises(AtmosphereError):
        verifier_resolution(profil, altitude_observateur=800.0)


def test_profil_avec_trou_sous_100m_rejete():
    # saut de 0 à 50 m directement : 50 m > 10 m requis sous 100 m
    points = (PointProfil(0.0, 288.0), PointProfil(50.0, 287.0), PointProfil(800.0, 280.0))
    profil = ProfilVertical(points=points, classe=ClasseDonnee.A, source="test")
    with pytest.raises(AtmosphereError):
        verifier_resolution(profil, altitude_observateur=800.0)


def test_profil_avec_trou_au_dessus_100m_rejete():
    points = list(PointProfil(z, 288.0 - 0.0065 * z) for z in range(0, 101, 10))
    points.append(PointProfil(800.0, 283.0))  # saut de 100 à 800 m : 700 m > 100 m requis
    profil = ProfilVertical(points=tuple(points), classe=ClasseDonnee.A, source="test")
    with pytest.raises(AtmosphereError):
        verifier_resolution(profil, altitude_observateur=800.0)


# --- §11.5 : la moyenne piège ---

def test_couche_k_rejette_epaisseur_non_positive():
    with pytest.raises(AtmosphereError):
        CoucheK(epaisseur_m=0.0, k=0.5)


def test_moyenne_ponderee_reproduit_lexemple_du_11_5():
    couches = [CoucheK(epaisseur_m=60.0, k=0.80), CoucheK(epaisseur_m=740.0, k=0.13)]
    assert moyenne_ponderee_en_hauteur(couches) == pytest.approx(0.180, abs=0.001)
    # rappel documentaire : ce n'est PAS le comportement réel (0,563 par traçage de rayon, §11.6)
    assert moyenne_ponderee_en_hauteur(couches) != pytest.approx(0.563, abs=0.01)


def test_moyenne_ponderee_exige_au_moins_une_couche():
    with pytest.raises(AtmosphereError):
        moyenne_ponderee_en_hauteur([])


# --- §21.3 : intervalle de k faute de donnée résolue ---

def test_intervalle_k_combine_les_bornes_des_regimes():
    hyp = intervalle_k_faute_de_donnee_resolue(
        [RegimeRefraction.STANDARD, RegimeRefraction.FORTE],
        "air plus froid que la mer (classe C) : régimes stables exclus",
    )
    assert isinstance(hyp, HypotheseRefraction)
    assert hyp.k_min == pytest.approx(0.13)
    assert hyp.k_max == pytest.approx(0.40)


def test_intervalle_k_un_seul_regime():
    hyp = intervalle_k_faute_de_donnee_resolue([RegimeRefraction.AUCUNE], "aucune indication disponible")
    assert hyp.k_min == pytest.approx(0.0)
    assert hyp.k_max == pytest.approx(0.0)


def test_intervalle_k_rejette_liste_vide():
    with pytest.raises(AtmosphereError):
        intervalle_k_faute_de_donnee_resolue([], "justification")


def test_intervalle_k_rejette_conduit():
    with pytest.raises(AtmosphereError):
        intervalle_k_faute_de_donnee_resolue([RegimeRefraction.CONDUIT], "justification")
