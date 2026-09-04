"""
Tests de refraction.py — rejouent le Tableau 7 du protocole comme fixture
de non-régression, et vérifient les garde-fous du §11 (bornes de R_eff,
classement en régimes, immuabilité de HypotheseRefraction pour le §11.7).
"""

import dataclasses

import pytest

from visee_optique.refraction import (
    HypotheseRefraction,
    RefractionError,
    RegimeRefraction,
    classer_regime,
    k_depuis_gradient,
    rapport_conduit_radio_optique,
    rayon_effectif,
)
from visee_optique.geometry import IUGG_R1

P_STANDARD = 1013.25  # hPa
T_STANDARD = 288.15  # K


# --- Tableau 7 : correspondance gradient-coefficient à 1013,25 hPa et 288,15 K ---

@pytest.mark.parametrize(
    "dT_dh_km, k_attendu",
    [
        (-34.16, 0.0000),
        (-13.00, 0.1300),
        (-6.50, 0.1699),
        (0.00, 0.2098),
        (25.00, 0.3634),
        (50.00, 0.5169),
        (100.00, 0.8240),
        (128.65, 1.0000),
    ],
)
def test_tableau_7_gradient_vers_coefficient(dT_dh_km, k_attendu):
    k = k_depuis_gradient(P_STANDARD, T_STANDARD, dT_dh_km)
    assert k == pytest.approx(k_attendu, abs=0.001)


def test_gradient_rejette_pression_ou_temperature_non_positives():
    with pytest.raises(RefractionError):
        k_depuis_gradient(0.0, T_STANDARD, 0.0)
    with pytest.raises(RefractionError):
        k_depuis_gradient(P_STANDARD, 0.0, 0.0)
    with pytest.raises(RefractionError):
        k_depuis_gradient(P_STANDARD, -1.0, 0.0)


# --- Rayon effectif (§11.1) ---

def test_rayon_effectif_k_nul_egale_R():
    assert rayon_effectif(IUGG_R1, 0.0) == pytest.approx(IUGG_R1)


def test_rayon_effectif_croit_avec_k():
    r_faible = rayon_effectif(IUGG_R1, 0.13)
    r_fort = rayon_effectif(IUGG_R1, 0.50)
    assert IUGG_R1 < r_faible < r_fort


def test_rayon_effectif_rejette_conduit():
    with pytest.raises(RefractionError):
        rayon_effectif(IUGG_R1, 1.0)
    with pytest.raises(RefractionError):
        rayon_effectif(IUGG_R1, 1.2)


def test_rayon_effectif_rejette_rayon_non_positif():
    with pytest.raises(RefractionError):
        rayon_effectif(0.0, 0.1)


# --- Classement en régimes (Tableau 8, §11.3) — informatif seulement ---

@pytest.mark.parametrize(
    "k, regime_attendu",
    [
        (-0.5, RegimeRefraction.AUCUNE),
        (0.0, RegimeRefraction.AUCUNE),
        (0.13, RegimeRefraction.STANDARD),
        (0.17, RegimeRefraction.STANDARD),
        (0.20, RegimeRefraction.FORTE),
        (0.35, RegimeRefraction.FORTE),
        (0.40, RegimeRefraction.TRES_FORTE),
        (0.60, RegimeRefraction.TRES_FORTE),
        (0.80, RegimeRefraction.INVERSION),
        (0.99, RegimeRefraction.INVERSION),
        (1.0, RegimeRefraction.CONDUIT),
        (1.5, RegimeRefraction.CONDUIT),
    ],
)
def test_classement_regimes(k, regime_attendu):
    assert classer_regime(k) is regime_attendu


# --- §11.4 : conduit optique vs conduit d'évaporation, garde-fou de domaine ---

def test_rapport_conduit_radio_optique_vaut_environ_115():
    assert rapport_conduit_radio_optique() == pytest.approx(115.13, abs=0.5)


# --- §11.7 : HypotheseRefraction, immuable et justifiée ---

def test_hypothese_refraction_valide():
    h = HypotheseRefraction(k_min=0.10, k_max=0.40, justification="Profil vertical du §21, campagne du 3/9/2026.")
    assert h.couvre(0.25)
    assert not h.couvre(0.05)
    assert not h.couvre(0.50)


def test_hypothese_refraction_rejette_intervalle_inverse():
    with pytest.raises(RefractionError):
        HypotheseRefraction(k_min=0.5, k_max=0.1, justification="donnée")


def test_hypothese_refraction_exige_justification():
    with pytest.raises(RefractionError):
        HypotheseRefraction(k_min=0.1, k_max=0.4, justification="")
    with pytest.raises(RefractionError):
        HypotheseRefraction(k_min=0.1, k_max=0.4, justification="   ")


def test_hypothese_refraction_est_immuable():
    h = HypotheseRefraction(k_min=0.1, k_max=0.4, justification="Profil résolu, station côtière.")
    with pytest.raises(dataclasses.FrozenInstanceError):
        h.k_max = 0.8  # type: ignore[misc]
