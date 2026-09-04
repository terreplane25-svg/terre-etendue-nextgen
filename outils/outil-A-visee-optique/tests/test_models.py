"""
Tests de models.py — discipline du §29 (un modèle incomplet n'entre pas
dans la comparaison) et condition de discrimination du §28.2, rejouant
le Tableau 19 comme fixture de non-régression.
"""

import pytest

from visee_optique.geometry import Cible, IUGG_R1
from visee_optique.refraction import HypotheseRefraction
from visee_optique.uncertainty import PlageParametre, UncertaintyError
from visee_optique.models import (
    ConditionDiscrimination,
    Modele,
    ModelError,
    ModeleSpherique,
    ModeleSurfacePlane,
    condition_discrimination,
    delta_le_plus_defavorable,
)

R = IUGG_R1


def _hyp(k_min, k_max, justification="test"):
    return HypotheseRefraction(k_min=k_min, k_max=k_max, justification=justification)


# --- §29 : un modèle n'entre dans la comparaison que déposé au complet ---

def test_modele_est_abstrait():
    with pytest.raises(TypeError):
        Modele()  # type: ignore[abstract]


def test_modele_plan_sans_parametre_libre():
    p = ModeleSurfacePlane()
    assert p.parametres_libres == ()
    assert p.nombre_parametres_libres == 0
    assert p.predire(150_000.0) == 1.0
    # les paramètres superflus sont ignorés, pas rejetés (§29.2 : même interface pour les deux modèles)
    assert p.predire(150_000.0, h=800.0, k=0.13) == 1.0


def test_modele_spherique_parametres_libres_depuis_hypothese():
    s = ModeleSpherique(R=R, cible=Cible(H=100.0), hypothese_k=_hyp(0.10, 0.40, "profil du §21"))
    (plage,) = s.parametres_libres
    assert plage.nom == "k"
    assert plage.minimum == pytest.approx(0.10)
    assert plage.maximum == pytest.approx(0.40)
    assert plage.source == "profil du §21"
    assert s.nombre_parametres_libres == 1


def test_modele_spherique_predire_exige_h_et_k():
    s = ModeleSpherique(R=R, cible=Cible(H=100.0), hypothese_k=_hyp(0.13, 0.13))
    with pytest.raises(ModelError):
        s.predire(120_000.0, k=0.13)  # h manquant
    with pytest.raises(ModelError):
        s.predire(120_000.0, h=800.0)  # k manquant


def test_modele_spherique_predire_coherent_avec_geometry():
    from visee_optique.geometry import fraction_visible
    from visee_optique.refraction import rayon_effectif

    s = ModeleSpherique(R=R, cible=Cible(H=100.0), hypothese_k=_hyp(0.13, 0.13))
    attendu = fraction_visible(120_000.0, 800.0, Cible(H=100.0), rayon_effectif(R, 0.13))
    assert s.predire(120_000.0, h=800.0, k=0.13) == pytest.approx(attendu)


# --- §23.1 via l'interface Modele : reproduit le Tableau 15 ---

def test_enveloppe_prediction_reproduit_tableau_15_a_120km():
    s = ModeleSpherique(
        R=R, cible=Cible(H=100.0), hypothese_k=_hyp(0.0, 0.50, "Tableau 8 : standard à très forte")
    )
    enveloppe = s.enveloppe_prediction(120_000.0, pas_par_parametre=51, h=800.0)
    assert enveloppe.minimum == pytest.approx(0.715, abs=0.001)
    assert enveloppe.maximum == pytest.approx(1.000, abs=0.001)


def test_enveloppe_prediction_rejette_plage_dupliquee():
    s = ModeleSpherique(R=R, cible=Cible(H=100.0), hypothese_k=_hyp(0.10, 0.40))
    with pytest.raises(ModelError):
        s.enveloppe_prediction(
            120_000.0,
            plages_supplementaires=[PlageParametre("k", 0.0, 1.0, "doublon")],
            h=800.0,
        )


# --- §28.2 : condition de discrimination, Tableau 19 ---

TABLEAU_19_KM = {
    2: {
        2: {0.20: 18.3, 0.35: 20.3, 0.50: 23.1},
        5: {0.20: 25.6, 0.35: 28.4, 0.50: 32.4},
    },
    10: {
        2: {0.20: 25.2, 0.35: 28.0, 0.50: 31.9},
        5: {0.20: 32.6, 0.35: 36.1, 0.50: 41.2},
    },
    50: {
        2: {0.20: 40.8, 0.35: 45.3, 0.50: 51.7},
        5: {0.20: 48.2, 0.35: 53.4, 0.50: 60.9},
    },
    100: {
        2: {0.20: 52.5, 0.35: 58.3, 0.50: 66.4},
        5: {0.20: 59.9, 0.35: 66.4, 0.50: 75.7},
    },
    300: {
        2: {0.20: 81.7, 0.35: 90.7, 0.50: 103.4},
        5: {0.20: 89.1, 0.35: 98.8, 0.50: 112.7},
    },
    800: {
        2: {0.20: 125.5, 0.35: 139.2, 0.50: 158.7},
        5: {0.20: 132.8, 0.35: 147.4, 0.50: 168.0},
    },
    2000: {
        2: {0.20: 191.1, 0.35: 212.0, 0.50: 241.7},
        5: {0.20: 198.4, 0.35: 220.1, 0.50: 251.0},
    },
}


def _condition_a_distance(D_m, h, k_max, u_c, H=100.0):
    modele_s = ModeleSpherique(R=R, cible=Cible(H=H), hypothese_k=_hyp(k_max, k_max, "k retenu, test"))
    modele_p = ModeleSurfacePlane()
    return condition_discrimination(
        modele_s, modele_p, D_m, u_f=u_c / H, pas_par_parametre=1, h=h
    )


@pytest.mark.parametrize(
    "h, u_c, k_max, D_km_attendu",
    [
        (h, u_c, k_max, D_km)
        for h, par_u_c in TABLEAU_19_KM.items()
        for u_c, par_k in par_u_c.items()
        for k_max, D_km in par_k.items()
    ],
)
def test_tableau_19_seuil_de_discrimination(h, u_c, k_max, D_km_attendu):
    D_seuil = D_km_attendu * 1000.0

    juste_avant = _condition_a_distance(D_seuil - 500.0, h, k_max, u_c)
    juste_apres = _condition_a_distance(D_seuil + 500.0, h, k_max, u_c)

    assert juste_avant.satisfaite is False
    assert juste_apres.satisfaite is True


def test_condition_discrimination_delta_exact_au_seuil():
    # h = 800, k_max = 0,35, u(c) = 5 -> seuil à 147,4 km (Tableau 19)
    resultat = _condition_a_distance(147_400.0, 800.0, 0.35, 5.0)
    assert isinstance(resultat, ConditionDiscrimination)
    assert resultat.seuil == pytest.approx(resultat.facteur * resultat.u_f)
    assert resultat.satisfaite is True
    assert resultat.delta >= resultat.seuil


def test_condition_discrimination_rejette_u_f_negative():
    modele_s = ModeleSpherique(R=R, cible=Cible(H=100.0), hypothese_k=_hyp(0.13, 0.13))
    modele_p = ModeleSurfacePlane()
    with pytest.raises(ModelError):
        condition_discrimination(modele_s, modele_p, 120_000.0, u_f=-1.0, h=800.0)


# --- §28.2.1 : la condition ne dépend pas de la hauteur de cible H ---

def test_condition_independante_de_H():
    # même h, D, k_max, u(c) absolu ; H différent -> même verdict, par construction du §28.2.1
    resultat_H100 = _condition_a_distance(147_400.0, 800.0, 0.35, 5.0, H=100.0)
    resultat_H50 = _condition_a_distance(147_400.0, 800.0, 0.35, 5.0, H=50.0)
    assert resultat_H100.satisfaite == resultat_H50.satisfaite is True

    resultat_H100_avant = _condition_a_distance(147_400.0 - 2000.0, 800.0, 0.35, 5.0, H=100.0)
    resultat_H50_avant = _condition_a_distance(147_400.0 - 2000.0, 800.0, 0.35, 5.0, H=50.0)
    assert resultat_H100_avant.satisfaite == resultat_H50_avant.satisfaite is False


# --- delta_le_plus_defavorable : bord d'enveloppe, pas point nominal ---

def test_delta_le_plus_defavorable_diminue_avec_lincertitude_sur_k():
    """Un intervalle de k plus large ne peut que RAPPROCHER les deux modèles au pire cas
    (k plus grand => moins d'occultation => f_S plus proche de f_P = 1), jamais les éloigner."""
    modele_p = ModeleSurfacePlane()

    etroit = ModeleSpherique(R=R, cible=Cible(H=100.0), hypothese_k=_hyp(0.13, 0.13))
    large = ModeleSpherique(R=R, cible=Cible(H=100.0), hypothese_k=_hyp(0.10, 0.40))

    delta_etroit, _ = delta_le_plus_defavorable(etroit, modele_p, 120_000.0, h=800.0)
    delta_large, _ = delta_le_plus_defavorable(large, modele_p, 120_000.0, h=800.0, pas_par_parametre=31)

    assert delta_large <= delta_etroit


def test_delta_le_plus_defavorable_rejette_plages_dupliquees():
    s = ModeleSpherique(R=R, cible=Cible(H=100.0), hypothese_k=_hyp(0.10, 0.40))
    p = ModeleSurfacePlane()
    with pytest.raises(ModelError):
        delta_le_plus_defavorable(
            s, p, 120_000.0, plages_supplementaires=[PlageParametre("k", 0.0, 1.0, "doublon")], h=800.0
        )
