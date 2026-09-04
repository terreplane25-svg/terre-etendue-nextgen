"""
Tests de uncertainty.py — composition JCGM (§22), analyse de sensibilité
(§23), rejouant le Tableau 14 (effets ponctuels) et le Tableau 15
(enveloppe du modèle S) comme fixtures de non-régression.
"""

import math

import pytest

from visee_optique.geometry import Cible, IUGG_R1, fraction_visible
from visee_optique.refraction import rayon_effectif
from visee_optique.uncertainty import (
    Composante,
    Correlation,
    EnveloppeSensibilite,
    Incertitude,
    PlageParametre,
    TypeIncertitude,
    UncertaintyError,
    balayer_enveloppe,
    composer,
    effet_sensibilite,
    modele_refute_par,
)

R = IUGG_R1
CIBLE = Cible(H=100.0, z_b=0.0)


def _f(D, h, k):
    """Fraction visible du modèle S, en fonction de D, h et k — pour les tests de sensibilité."""
    return fraction_visible(D, h, CIBLE, rayon_effectif(R, k))


def _c(D, h, k):
    """Hauteur occultée du modèle S — pour reproduire le Tableau 14, qui porte sur c, pas f."""
    from visee_optique.geometry import hauteur_occultee

    return hauteur_occultee(D, h, CIBLE, rayon_effectif(R, k))


# --- §22.3 : composition d'incertitudes ---

def test_composition_quadrature_independantes():
    # triangle 3-4-5 : cas canonique de composition en quadrature
    composantes = [
        Composante("a", TypeIncertitude.A, 3.0, "dispersion entre analystes"),
        Composante("b", TypeIncertitude.B, 4.0, "résolution effective"),
    ]
    assert composer(composantes) == pytest.approx(5.0)


def test_composition_correlation_parfaite_positive():
    composantes = [
        Composante("h_obs", TypeIncertitude.B, 3.0, "GNSS + géoïde"),
        Composante("z_base", TypeIncertitude.B, 4.0, "même modèle de terrain"),
    ]
    correlations = [
        Correlation(("h_obs", "z_base"), 1.0, "même modèle numérique de terrain (§22.3)")
    ]
    # r = 1 : les incertitudes s'additionnent linéairement, pas en quadrature
    assert composer(composantes, correlations) == pytest.approx(7.0)


def test_composition_correlation_parfaite_negative():
    composantes = [
        Composante("a", TypeIncertitude.B, 3.0, "source a"),
        Composante("b", TypeIncertitude.B, 4.0, "source b"),
    ]
    correlations = [Correlation(("a", "b"), -1.0, "anti-corrélées par construction")]
    assert composer(composantes, correlations) == pytest.approx(1.0)


def test_composition_rejette_nom_de_correlation_inconnu():
    composantes = [Composante("a", TypeIncertitude.A, 1.0, "source")]
    correlations = [Correlation(("a", "inconnue"), 0.5, "justification")]
    with pytest.raises(UncertaintyError):
        composer(composantes, correlations)


def test_composition_rejette_coefficient_hors_bornes():
    with pytest.raises(UncertaintyError):
        Correlation(("a", "b"), 1.5, "justification")


def test_composante_rejette_valeur_negative():
    with pytest.raises(UncertaintyError):
        Composante("a", TypeIncertitude.A, -1.0, "source")


def test_composante_exige_source():
    with pytest.raises(UncertaintyError):
        Composante("a", TypeIncertitude.A, 1.0, "   ")


def test_incertitude_elargie():
    composantes = [Composante("a", TypeIncertitude.A, 3.0, "source"), Composante("b", TypeIncertitude.B, 4.0, "source")]
    inc = Incertitude.depuis_composantes(composantes, facteur_elargissement=2.0)
    assert inc.valeur_composee == pytest.approx(5.0)
    assert inc.elargie == pytest.approx(10.0)


def test_incertitude_rejette_facteur_elargissement_non_positif():
    with pytest.raises(UncertaintyError):
        Incertitude(valeur_composee=1.0, composantes=(), facteur_elargissement=0.0)


# --- PlageParametre : même discipline que Cible et HypotheseRefraction ---

def test_plage_parametre_rejette_min_superieur_max():
    with pytest.raises(UncertaintyError):
        PlageParametre("h", 10.0, 5.0, "source")


def test_plage_parametre_exige_source():
    with pytest.raises(UncertaintyError):
        PlageParametre("h", 5.0, 10.0, "")


# --- Tableau 14 : effets de sensibilité ponctuels (§22.2) ---

@pytest.mark.parametrize(
    "D_km, parametre, delta, effet_attendu",
    [
        (120, "h", 1.0, 0.109),
        (150, "h", 1.0, 0.386),
        (120, "D", 100.0, 0.161),
        (150, "D", 100.0, 0.570),
        (120, "k", 0.01, 1.108),
        (150, "k", 0.01, 4.917),
    ],
)
def test_tableau_14_effets_ponctuels(D_km, parametre, delta, effet_attendu):
    nominal = {"D": D_km * 1000.0, "h": 800.0, "k": 0.13}
    effet = effet_sensibilite(_c, nominal, parametre, delta)
    assert abs(effet) == pytest.approx(effet_attendu, abs=0.01)


def test_tableau_14_hauteur_cible_sans_effet_sur_c():
    """La hauteur de cible n'intervient pas dans c (§22.2 : « la hauteur de la cible
    n'intervient pas dans c ; elle n'intervient que dans la fraction »). Vérifié ici en
    variant H dans fraction_visible tout en gardant c constant par construction : c ne
    dépend pas de H, donc toute variation de H à D, h, k fixés laisse c inchangé."""
    D, h, k = 120_000.0, 800.0, 0.13
    R_eff = rayon_effectif(R, k)
    c_H100 = fraction_visible(D, h, Cible(H=100.0), R_eff)
    c_H100_5 = fraction_visible(D, h, Cible(H=100.5), R_eff)
    # la hauteur occultée elle-même (avant division par H) est identique :
    from visee_optique.geometry import hauteur_occultee

    assert hauteur_occultee(D, h, Cible(H=100.0), R_eff) == hauteur_occultee(
        D, h, Cible(H=100.5), R_eff
    )


def test_effet_sensibilite_exige_parametre_present_dans_nominal():
    with pytest.raises(UncertaintyError):
        effet_sensibilite(_c, {"D": 1.0, "h": 1.0}, "k", 0.01)


def test_effet_sensibilite_exige_delta_positif():
    with pytest.raises(UncertaintyError):
        effet_sensibilite(_c, {"D": 1.0}, "D", 0.0)


# --- Tableau 15 : enveloppe du modèle S sur l'exemple (§23.3) ---

TABLEAU_15 = {
    100: {0.00: 1.000, 0.13: 1.000, 0.25: 1.000, 0.50: 1.000},
    110: {0.00: 0.936, 0.13: 0.998, 0.25: 1.000, 0.50: 1.000},
    120: {0.00: 0.715, 0.13: 0.906, 0.25: 0.993, 0.50: 1.000},
    130: {0.00: 0.338, 0.13: 0.677, 0.25: 0.894, 0.50: 1.000},
    140: {0.00: 0.000, 0.13: 0.311, 0.25: 0.677, 0.50: 1.000},
    150: {0.00: 0.000, 0.13: 0.000, 0.25: 0.343, 0.50: 0.980},
    160: {0.00: 0.000, 0.13: 0.000, 0.25: 0.000, 0.50: 0.884},
}


@pytest.mark.parametrize(
    "D_km, k, f_attendu",
    [(D_km, k, f) for D_km, row in TABLEAU_15.items() for k, f in row.items()],
)
def test_tableau_15_modele_S(D_km, k, f_attendu):
    f = _f(D_km * 1000.0, 800.0, k)
    assert f == pytest.approx(f_attendu, abs=0.001)


def test_balayer_enveloppe_reproduit_tableau_15_a_120km():
    """L'enveloppe du modèle S balayée sur k ∈ [0 ; 0,50] à 120 km doit retrouver les
    bornes du Tableau 15 : minimum au k le plus faible, maximum au k le plus fort —
    exactement la lecture qu'en fait le §23.3 (« les deux modèles ne se séparent
    qu'au-delà de la distance où l'enveloppe du modèle S s'écarte de 1 »)."""
    plage_k = PlageParametre("k", 0.0, 0.50, "Tableau 8 : régimes standard à très forte")
    enveloppe = balayer_enveloppe(
        lambda k: _f(120_000.0, 800.0, k), [plage_k], pas_par_parametre=51
    )
    assert enveloppe.minimum == pytest.approx(0.715, abs=0.001)
    assert enveloppe.maximum == pytest.approx(1.000, abs=0.001)
    assert enveloppe.combinaison_minimale["k"] == pytest.approx(0.0)
    # Le maximum (f = 1,000) est atteint dès k ≈ 0,30 pour cette géométrie et reste
    # saturé jusqu'à k = 0,50 (Tableau 15) : plusieurs k de la grille l'atteignent,
    # balayer_enveloppe rapporte le premier rencontré, pas nécessairement k = 0,50.
    assert _f(120_000.0, 800.0, enveloppe.combinaison_maximale["k"]) == pytest.approx(1.0, abs=0.001)
    assert enveloppe.methode == "grille complète"


def test_balayer_enveloppe_grille_simple_bidimensionnelle():
    plages = [
        PlageParametre("x", 0.0, 2.0, "test"),
        PlageParametre("y", 0.0, 3.0, "test"),
    ]
    enveloppe = balayer_enveloppe(lambda x, y: x + y, plages, pas_par_parametre=3)
    assert enveloppe.minimum == pytest.approx(0.0)
    assert enveloppe.maximum == pytest.approx(5.0)
    assert enveloppe.combinaison_minimale == {"x": 0.0, "y": 0.0}
    assert enveloppe.combinaison_maximale == {"x": 2.0, "y": 3.0}
    assert enveloppe.n_evaluations == 9


def test_balayer_enveloppe_bascule_en_monte_carlo_au_dela_de_max_grille():
    plages = [PlageParametre("x", 0.0, 1.0, "test")]
    with pytest.raises(UncertaintyError):
        # grille de 1000 points, plafond à 10 : exige un germe
        balayer_enveloppe(lambda x: x, plages, pas_par_parametre=1000, max_grille=10)

    enveloppe = balayer_enveloppe(
        lambda x: x, plages, pas_par_parametre=1000, max_grille=10, germe=42
    )
    assert enveloppe.methode == "monte-carlo"
    assert enveloppe.germe == 42
    assert enveloppe.n_evaluations == 10
    assert 0.0 <= enveloppe.minimum <= enveloppe.maximum <= 1.0


def test_balayer_enveloppe_monte_carlo_est_reproductible_avec_le_meme_germe():
    plages = [
        PlageParametre("x", 0.0, 1.0, "test"),
        PlageParametre("y", -1.0, 1.0, "test"),
    ]

    def f(x, y):
        return x * y

    e1 = balayer_enveloppe(f, plages, pas_par_parametre=1000, max_grille=50, germe=7)
    e2 = balayer_enveloppe(f, plages, pas_par_parametre=1000, max_grille=50, germe=7)
    assert e1.minimum == e2.minimum
    assert e1.maximum == e2.maximum


def test_enveloppe_largeur_et_contient():
    enveloppe = EnveloppeSensibilite(
        minimum=0.7,
        maximum=1.0,
        combinaison_minimale={},
        combinaison_maximale={},
        methode="grille complète",
        n_evaluations=10,
    )
    assert enveloppe.largeur == pytest.approx(0.3)
    assert enveloppe.contient(0.85)
    assert not enveloppe.contient(0.5)


# --- §23.2 : un modèle n'est réfuté que si l'observation tombe hors de l'enveloppe entière ---

def test_modele_non_refute_si_observation_dans_enveloppe():
    plage_k = PlageParametre("k", 0.0, 0.50, "Tableau 8")
    enveloppe = balayer_enveloppe(lambda k: _f(120_000.0, 800.0, k), [plage_k], pas_par_parametre=21)
    # une observation à 0,80 tombe dans [0,715 ; 1,000] : le modèle S n'est pas réfuté
    assert modele_refute_par(enveloppe, 0.80) is False


def test_modele_refute_si_observation_hors_enveloppe_entiere():
    plage_k = PlageParametre("k", 0.0, 0.50, "Tableau 8")
    enveloppe = balayer_enveloppe(lambda k: _f(120_000.0, 800.0, k), [plage_k], pas_par_parametre=21)
    # une observation à 0,3 tombe sous le minimum de l'enveloppe (0,715) : réfuté
    assert modele_refute_par(enveloppe, 0.30) is True
