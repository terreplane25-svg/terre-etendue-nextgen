"""
Inversion de l'angle en coefficient de réfraction.

Le point de ces tests n'est pas que l'inversion trouve la bonne valeur — un
aller-retour le montre en trois lignes. Le point est qu'elle REFUSE d'en
trouver une là où l'angle n'en détermine pas, ce que le cahier des charges
(« ajuster k jusqu'à ce que H_théorique(k) == H_obs ») ne prévoyait pas.
"""

import random

import pytest
from visee_optique.geometry import Cible, distance_critique, distance_limite
from visee_optique.refraction import RegimeRefraction, rayon_effectif

from metrologie_image.inversion import (
    K_PLAFOND,
    K_PLANCHER,
    Plage,
    StatutK,
    angle_portion_visible,
    coefficient_refraction_effectif,
    enveloppe_coefficient,
    k_d_extinction,
    k_de_saturation,
)
from metrologie_image.optique import MetrologieError

R0 = 6_371_008.8

# Configuration de référence : phare de 60 m vu depuis 30 m d'œil à 40 km.
# Elle est choisie pour que la cible reste COUPÉE — ni entière, ni disparue —
# sur tout l'intervalle k ∈ [−0,3 ; 0,4], seul régime où l'image détermine
# vraiment k. À k = 0,13 il en émerge environ 35 m.
#
# Le premier jet de ce fichier prenait 10 m d'œil : à k ≤ 0, le phare y est
# occulté jusqu'au sommet, et l'aller-retour échouait. C'est ce qui a mis au
# jour l'absence de traitement de l'extinction — voir `k_d_extinction`.
H, Z_B, HOBS, D = 60.0, 0.0, 30.0, 40_000.0
CIBLE = Cible(H=H, z_b=Z_B)

# Une seconde configuration, sans saturation possible : le Monte Cinto
# (2706 m) à 200 km. Même au plafond d'exploration, sa base reste sous
# l'horizon — la cible ne peut pas devenir entière.
H_MONT, D_MONT = 2706.0, 200_000.0
CIBLE_MONT = Cible(H=H_MONT, z_b=0.0)


def angle_pour(k, D_=D, h=HOBS, cible=CIBLE):
    return angle_portion_visible(D_, h, cible, rayon_effectif(R0, k))


@pytest.mark.parametrize("k_vrai", [-0.3, 0.0, 0.13, 0.17, 0.25, 0.4])
def test_aller_retour(k_vrai):
    """L'angle produit par un k donné se réinverse en ce même k."""
    r = coefficient_refraction_effectif(angle_pour(k_vrai), 0.0, D, HOBS, CIBLE, R0)
    assert r.statut is StatutK.DETERMINE
    assert r.k == pytest.approx(k_vrai, abs=1e-9)


def test_enveloppe_encadre_la_valeur():
    u = 1e-6  # ~0,2″ élargi
    r = coefficient_refraction_effectif(angle_pour(0.13), u, D, HOBS, CIBLE, R0)
    assert r.k_min is not None and r.k_max is not None
    assert r.k_min < r.k < r.k_max


def test_enveloppe_s_elargit_avec_l_incertitude():
    largeurs = []
    for u in (1e-7, 1e-6, 5e-6):
        r = coefficient_refraction_effectif(angle_pour(0.13), u, D, HOBS, CIBLE, R0)
        largeurs.append(r.k_max - r.k_min)
    assert all(b > a for a, b in zip(largeurs, largeurs[1:]))


def test_cible_entierement_visible_ne_determine_pas_k():
    """LE cas que le cahier des charges ne prévoyait pas.

    À 8 km, le phare de 60 m est entier bien avant tout k plausible. L'angle
    relevé est alors compatible avec un continuum de valeurs, et l'inversion
    doit le dire — soit en signalant la zone saturée, soit en n'encadrant pas.
    """
    D_court = 8_000.0
    k_sat = k_de_saturation(D_court, HOBS, CIBLE, R0)
    assert k_sat is not None
    assert k_sat < 0.0  # saturé même sans réfraction du tout
    r = coefficient_refraction_effectif(
        angle_pour(0.13, D_=D_court), 1e-6, D_court, HOBS, CIBLE, R0
    )
    assert r.dans_zone_saturee
    # L'enveloppe couvre l'essentiel du domaine exploré : le relevé ne
    # distingue pas les valeurs entre elles.
    largeur = (r.k_max if r.k_max is not None else K_PLAFOND) - (
        r.k_min if r.k_min is not None else K_PLANCHER
    )
    assert largeur > 0.5


def test_saturation_absente_quand_la_cible_reste_coupee():
    """Le Monte Cinto à 200 km : aucun k exploré ne dégage sa base.

    Contre-épreuve du seuil : à 40 km le phare, lui, sature — mais tard,
    vers k = 0,92, bien au-delà de tout régime tabulé au §11.3.
    """
    assert k_de_saturation(D_MONT, HOBS, CIBLE_MONT, R0) is None
    k_sat_phare = k_de_saturation(D, HOBS, CIBLE, R0)
    assert k_sat_phare is not None and 0.7 < k_sat_phare < 0.99


def test_extinction_bornee_par_le_bas():
    """Sous un certain k, le phare disparaît entièrement — et k cesse d'être lisible."""
    k_ext = k_d_extinction(D, HOBS, CIBLE, R0)
    assert k_ext is not None
    assert K_PLANCHER < k_ext < 0.0
    R = rayon_effectif(R0, k_ext)
    assert distance_limite(HOBS, CIBLE, R) == pytest.approx(D, rel=1e-9)
    # Juste sous le seuil, plus rien ; juste au-dessus, quelque chose.
    assert angle_pour(k_ext - 0.01) == 0.0
    assert angle_pour(k_ext + 0.01) > 0.0


def test_releve_nul_majore_sans_valeur():
    """Le piège que la bissection naïve n'aurait pas vu.

    Sous le seuil d'extinction, l'angle prédit vaut zéro pour TOUTE valeur de
    k. Une bissection prise au mot converge alors vers le plancher
    d'exploration et le rend comme s'il s'agissait d'une mesure : un chiffre
    parfaitement précis et parfaitement vide.
    """
    r = coefficient_refraction_effectif(0.0, 1e-6, D, HOBS, CIBLE, R0)
    assert r.statut is StatutK.MAJORE
    assert r.k is None
    assert r.dans_zone_eteinte
    assert r.k_extinction is not None


def test_angle_trop_grand_minore_sans_valeur():
    """Un relevé qui excède le modèle ne donne pas un k : il donne une borne."""
    trop = angle_pour(K_PLAFOND) * 1.5
    r = coefficient_refraction_effectif(trop, 0.0, D, HOBS, CIBLE, R0)
    assert r.statut is StatutK.MINORE
    assert r.k is None
    assert r.regime is None
    assert r.enveloppe_ouverte


def test_angle_trop_petit_majore_sans_valeur():
    """Un relevé sous le modèle — brume, relief devant — ne donne pas un k.

    Le cas se distingue de l'extinction : il faut un relevé strictement
    positif mais inférieur à ce que la surface la plus courbe explorée
    prédit. Le Monte Cinto à 140 km convient — au plancher k = −1 il en
    émerge encore ~200 m, donc l'angle prédit n'y est pas nul.
    """
    D_maj = 140_000.0
    trop_peu = angle_pour(K_PLANCHER, D_=D_maj, cible=CIBLE_MONT) * 0.5
    assert trop_peu > 0.0  # sinon c'est l'extinction qu'on teste, pas ce cas
    r = coefficient_refraction_effectif(trop_peu, 0.0, D_maj, HOBS, CIBLE_MONT, R0)
    assert r.statut is StatutK.MAJORE
    assert r.k is None
    assert not r.dans_zone_eteinte
    assert r.enveloppe_ouverte


def test_regime_non_determine_quand_l_enveloppe_le_traverse():
    """Une enveloppe à cheval sur deux régimes n'en nomme aucun."""
    r = coefficient_refraction_effectif(angle_pour(0.19), 3e-5, D, HOBS, CIBLE, R0)
    assert r.k_min is not None and r.k_max is not None
    assert r.regime_min != r.regime_max
    assert not r.regime_determine


def test_regime_determine_quand_l_enveloppe_tient_dedans():
    r = coefficient_refraction_effectif(angle_pour(0.15), 1e-8, D, HOBS, CIBLE, R0)
    assert r.regime_determine
    assert r.regime is RegimeRefraction.STANDARD


def test_incertitude_negative_refusee():
    with pytest.raises(MetrologieError):
        coefficient_refraction_effectif(angle_pour(0.13), -1e-6, D, HOBS, CIBLE, R0)


# --- Enveloppe sur les quatre grandeurs d'entrée ---


def plages(dD=500.0, dh=1.0, dH=2.0, dzb=0.0):
    return (
        Plage("distance", D, D - dD, D + dD, "SHOM, fiche d'ouvrage"),
        Plage("altitude_observateur", HOBS, HOBS - dh, HOBS + dh, "IGN RGE ALTI"),
        Plage("hauteur_cible", H, H - dH, H + dH, "fiche d'ouvrage du phare"),
        Plage("altitude_base", Z_B, max(0.0, Z_B - dzb), Z_B + dzb, "niveau moyen adopté"),
    )


def test_enveloppe_balaie_seize_sommets():
    e = enveloppe_coefficient(angle_pour(0.13), 1e-6, *plages(), R0=R0)
    assert e.combinaisons == 16
    assert e.determinee
    assert e.k_min < 0.13 < e.k_max


def test_enveloppe_des_entrees_plus_large_que_celle_du_pointe():
    """Sur cette visée, l'incertitude sur D et H pèse plus que le pointé.

    C'est le genre de fait qu'une valeur centrale seule masque : affiner le
    pointé ne servirait à rien tant que la distance n'est pas mieux établie.
    """
    angle = angle_pour(0.13)
    pointe_seul = coefficient_refraction_effectif(angle, 1e-6, D, HOBS, CIBLE, R0)
    tout = enveloppe_coefficient(angle, 1e-6, *plages(), R0=R0)
    assert (tout.k_max - tout.k_min) > (pointe_seul.k_max - pointe_seul.k_min)


def test_sommets_bornent_le_tirage():
    """Les seize sommets encadrent-ils vraiment l'intérieur du domaine ?

    Le balayage aux sommets suppose que k est monotone en chacune des quatre
    entrées. La supposition n'est pas laissée telle quelle : mille tirages
    uniformes à l'intérieur du domaine sont confrontés à l'enveloppe. Un seul
    qui en sortirait invaliderait la méthode.
    """
    angle = angle_pour(0.13)
    p_D, p_h, p_H, p_zb = plages(dD=800.0, dh=2.0, dH=3.0, dzb=1.0)
    e = enveloppe_coefficient(angle, 1e-6, p_D, p_h, p_H, p_zb, R0=R0)
    assert e.determinee

    alea = random.Random(20260904)
    for _ in range(1000):
        d = alea.uniform(*p_D.bornes)
        h = alea.uniform(*p_h.bornes)
        hh = alea.uniform(*p_H.bornes)
        zb = alea.uniform(*p_zb.bornes)
        r = coefficient_refraction_effectif(
            angle, 1e-6, d, h, Cible(H=hh, z_b=zb), R0
        )
        assert r.k_min is not None and r.k_max is not None
        assert e.k_min - 1e-12 <= r.k_min
        assert r.k_max <= e.k_max + 1e-12


def test_une_seule_combinaison_non_bornee_ouvre_l_enveloppe():
    """Une enveloppe d'entrée assez large pour qu'un sommet sature n'est plus fermée."""
    angle = angle_pour(0.13)
    large = (
        Plage("distance", D, 8_000.0, D + 500.0, "borne délibérément large"),
        Plage("altitude_observateur", HOBS, HOBS - 1, HOBS + 1, "IGN"),
        Plage("hauteur_cible", H, H - 2, H + 2, "fiche d'ouvrage"),
        Plage("altitude_base", 0.0, 0.0, 0.0, "niveau moyen adopté"),
    )
    e = enveloppe_coefficient(angle, 1e-6, *large, R0=R0)
    assert e.combinaisons_non_bornees > 0
    assert not e.determinee


def test_plage_sans_source_est_construite_mais_le_signale():
    """La source est relevée, plus exigée — voir la docstring de `Plage`."""
    p = Plage("distance", D, D - 1, D + 1, "   ")
    assert p.source_declaree is False
    assert p.valeur == D


def test_plage_exige_une_valeur_dans_ses_bornes():
    with pytest.raises(MetrologieError, match="enveloppe"):
        Plage("distance", D, D + 10, D + 20, "SHOM")


def test_distance_critique_coherente_avec_la_saturation():
    """Contre-épreuve : au k de saturation, D vaut exactement D_crit."""
    for D_ in (12_000.0, 15_000.0, 20_000.0):
        k_sat = k_de_saturation(D_, HOBS, CIBLE, R0)
        if k_sat is None or k_sat <= K_PLANCHER:
            continue
        R = rayon_effectif(R0, k_sat)
        assert distance_critique(HOBS, CIBLE, R) == pytest.approx(D_, rel=1e-9)
