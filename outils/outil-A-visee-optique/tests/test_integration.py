"""
Test d'intégration geometry.py + refraction.py — rejoue la colonne
« R_eff (m) » du Tableau 9 (§11.6) : l'arc au sol jusqu'au point rasant à
800 m d'altitude, calculé par la forme fermée du §9.1 en substituant le
rayon effectif R_eff = R/(1-k) à R.

Ce que ce test NE couvre PAS : la colonne « traçage (m) » du même
tableau, qui vient d'une intégration exacte de l'invariant de Bouguer
dans un profil d'indice réel (§11.6). Le protocole valide la
substitution R_eff pour k <= 0,5 (écart sous-métrique) et rend le
traçage obligatoire au-delà — ce traçage n'est pas encore implémenté
(cf. tâche de suivi « Outil A : traçage de rayon multicouche »), pour ne
pas donner une fausse assurance dans le régime où le protocole exige le
plus de rigueur.
"""

import pytest

from visee_optique.geometry import IUGG_R1, arc_to_tangent
from visee_optique.refraction import rayon_effectif

R = IUGG_R1
H_OBSERVATEUR = 800.0


@pytest.mark.parametrize(
    "k, s_eff_attendu",
    [
        (0.00, 100_958.15),
        (0.13, 108_239.23),
        (0.25, 116_577.95),
        (0.50, 142_780.12),
    ],
)
def test_tableau_9_substitution_rayon_effectif(k, s_eff_attendu):
    R_eff = rayon_effectif(R, k)
    s_eff = arc_to_tangent(H_OBSERVATEUR, R_eff)
    assert s_eff == pytest.approx(s_eff_attendu, abs=0.5)
