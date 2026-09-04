"""
refraction.py — Coefficient de réfraction atmosphérique k (§11 du protocole).

k est le rapport de la courbure du rayon lumineux à celle de la surface
de référence. Il doit être établi depuis un PROFIL VERTICAL RÉSOLU dans
les premières dizaines de mètres au-dessus de l'eau (§11.5, §21.1) —
jamais moyenné en hauteur (le §11.5 chiffre l'erreur : un profil à deux
couches équivalant à un k homogène de 0,563 donnerait 0,180 si on
moyennait naïvement), et jamais ajusté après avoir vu une image pour
expliquer un écart, dans un sens comme dans l'autre (§11.7).

Ce module fournit :
  - le calcul déterministe de k depuis un gradient thermique (§11.2) ;
  - R_eff, le rayon effectif à substituer à R dans geometry.py (§11.1) ;
  - un classement informatif en régimes (§11.3, Tableau 8), qui ne sert
    qu'à documenter et rechercher des signatures d'image (§19.4), jamais
    à décider ;
  - HypotheseRefraction, l'objet immuable qui porte la contrainte du
    §11.7 : un k déposé avant l'analyse ne peut plus être modifié.

Ne fait AUCUN traçage de rayon dans un profil multicouche (§11.6). Le
protocole ne rend cette étape obligatoire que pour k > 0,5 — en deçà,
il valide explicitement la substitution R_eff = R/(1-k) dans les
formules du §9 (Tableau 9 : accord sous-métrique). Le traçage complet
par intégration de l'invariant de Bouguer reste à faire (voir la tâche
de suivi) ; l'implémenter sans pouvoir le vérifier de façon indépendante
aurait donné une fausse assurance précisément dans le régime où le
protocole exige le plus de rigueur.
"""

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

__all__ = [
    "RefractionError",
    "RegimeRefraction",
    "HypotheseRefraction",
    "k_depuis_gradient",
    "rayon_effectif",
    "classer_regime",
    "rapport_conduit_radio_optique",
    "CONDUIT_OPTIQUE_GRADIENT_MIN_K_PAR_100M",
]


class RefractionError(ValueError):
    """Domaine invalide pour un calcul de réfraction (§11)."""


_G_SUR_RD = 0.0342  # K/m — gradient autoconvectif g/R_d ; annule k (§11.2, Tableau 7)
_CONSTANTE = 503.3  # constante de la formule redérivée (§11.2, §35.3)


def k_depuis_gradient(P_hPa: float, T_K: float, dT_dh_K_par_km: float) -> float:
    """k = 503,3 · (P/T²) · (0,0342 + dT/dh) — §11.2.

    P en hPa, T en K, dT/dh en K/km (converti en K/m pour la formule ;
    le Tableau 7 du protocole tabule dT/dh en K/km mais la constante
    0,0342 est en K/m — c'est le gradient autoconvectif g/R_d).

    Le résultat n'est pas borné ici : un k négatif (atmosphère instable,
    superréfraction inversée) ou k >= 1 (conduit) sont des sorties
    valides du calcul. Le bornage éventuel pour l'analyse est une
    décision du §21.3, pas de ce calcul.
    """
    if P_hPa <= 0:
        raise RefractionError("La pression doit être strictement positive.")
    if T_K <= 0:
        raise RefractionError("La température doit être strictement positive (kelvins).")
    dT_dh_K_par_m = dT_dh_K_par_km / 1000.0
    return _CONSTANTE * (P_hPa / T_K**2) * (_G_SUR_RD + dT_dh_K_par_m)


def rayon_effectif(R: float, k: float) -> float:
    """R_eff = R / (1 - k), valable pour k < 1 (§11.1).

    Le rayon à substituer à R dans toutes les fonctions de geometry.py
    pour tenir compte de la réfraction, tant que k reste sous le seuil
    de conduit optique.
    """
    if R <= 0:
        raise RefractionError("R doit être strictement positif.")
    if k >= 1:
        raise RefractionError(
            "k >= 1 : régime de conduit optique (Tableau 8). R_eff n'est "
            "plus défini par cette formule ; la construction du §8 ne "
            "s'applique plus (le rayon rasant épouse ou dépasse la "
            "courbure de la surface)."
        )
    return R / (1.0 - k)


class RegimeRefraction(str, Enum):
    """Les six régimes du Tableau 8 (§11.3). Classement informatif seulement."""

    AUCUNE = "aucune réfraction"
    STANDARD = "réfraction standard"
    FORTE = "réfraction forte"
    TRES_FORTE = "réfraction très forte"
    INVERSION = "inversion et mirage supérieur"
    CONDUIT = "conduit optique"


def classer_regime(k: float) -> RegimeRefraction:
    """Classement selon le Tableau 8 (§11.3) — informatif, jamais décisionnel.

    Sert uniquement à documenter une observation et à structurer la
    recherche des signatures d'image du §19.4 (mirage inférieur/supérieur,
    looming, conduit optique, déformation verticale). Le §11.7 interdit
    explicitement d'invoquer un régime pour justifier k après coup :
    cette fonction ne doit jamais intervenir dans le calcul de k lui-même,
    seulement dans son compte-rendu.

    Les bornes suivent les plages du Tableau 8 ; k = 0 et k = 1 sont les
    deux seuils physiques exacts (gradient autoconvectif et conduit),
    les bornes intermédiaires sont les plages typiques données par le
    protocole, pas des seuils physiques discrets.
    """
    if k <= 0:
        return RegimeRefraction.AUCUNE
    if k < 0.20:
        return RegimeRefraction.STANDARD
    if k < 0.40:
        return RegimeRefraction.FORTE
    if k < 0.80:
        return RegimeRefraction.TRES_FORTE
    if k < 1.0:
        return RegimeRefraction.INVERSION
    return RegimeRefraction.CONDUIT


# Conduit optique vs conduit d'évaporation (§11.4) — garde-fou documentaire contre
# l'erreur de domaine dénoncée à l'objection n°7 (§31) : un conduit d'évaporation
# est un phénomène radioélectrique piloté par l'humidité, pas un phénomène optique.
CONDUIT_OPTIQUE_GRADIENT_MIN_K_PAR_100M = 12.9  # K/100 m soutenu, seuil de conduit optique (§11.4)
_N_HUMIDE_OPTIQUE = -0.78  # N, à e = 20 hPa, T = 288 K (§11.4)
_N_HUMIDE_RADIO = 89.8  # N, mêmes conditions, en radioélectrique (§11.4)


def rapport_conduit_radio_optique() -> float:
    """Rapport (valeur absolue) entre le terme humide radioélectrique et optique.

    Vaut 115 dans les conditions du §11.4 (e = 20 hPa, T = 288 K) : c'est
    la mesure chiffrée de l'erreur de domaine qui consiste à invoquer un
    conduit d'évaporation marin (radioélectrique) pour expliquer une
    observation optique.
    """
    return abs(_N_HUMIDE_RADIO / _N_HUMIDE_OPTIQUE)


@dataclass(frozen=True)
class HypotheseRefraction:
    """Un intervalle de k déposé AVANT l'analyse, avec sa justification (§11.7, §26).

    Immuable : aucune méthode ne permet de modifier k_min/k_max après
    construction. Si une nouvelle donnée atmosphérique arrive après coup,
    elle donne lieu à une nouvelle HypotheseRefraction horodatée pour une
    nouvelle analyse — jamais à une mutation de celle déjà déposée. C'est
    l'objet qui porte, dans le code, l'interdiction d'ajustement du §11.7.
    """

    k_min: float
    k_max: float
    justification: str
    depose_le: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if self.k_min > self.k_max:
            raise RefractionError("k_min ne peut pas dépasser k_max.")
        if not self.justification or not self.justification.strip():
            raise RefractionError(
                "Toute hypothèse de réfraction doit être justifiée par les "
                "données atmosphériques du §21 avant l'analyse (§11.7)."
            )

    def couvre(self, k: float) -> bool:
        """True si k tombe dans l'intervalle déposé."""
        return self.k_min <= k <= self.k_max
