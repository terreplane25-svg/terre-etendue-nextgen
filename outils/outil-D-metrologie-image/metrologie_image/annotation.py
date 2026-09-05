"""
annotation.py — Les trois clics, et ce que chacun établit (§19).

Le relevé se fait par trois pointés sur l'image :

    1. la ligne d'horizon (limite eau/ciel) ;
    2. le point le plus bas encore visible de la cible ;
    3. le sommet de la cible.

CE QUE CHAQUE CLIC SERT À FAIRE
───────────────────────────────
Le cahier des charges attribuait au couple (1, 2) une « hauteur masquée par la
courbure ». Elle n'existe pas : le rayon rasant qui définit l'horizon est le
même qui définit le point le plus bas visible, donc les deux pointés tombent à
la même hauteur dans l'image dès que la cible est partiellement occultée. La
démonstration est en tête de `inversion.py`, la vérification numérique dans
`tests/test_geometrie_image.py`.

Le couple (1, 2) n'est donc pas une mesure : c'est un CONTRÔLE, et c'est ce
qui en fait la partie la plus utile du relevé. Un écart significatif entre les
deux pointés ne peut avoir que des causes nommables :

    · la cible n'émerge pas de l'eau (relief, estran, jetée devant la base) ;
    · l'« horizon » pointé n'en est pas un (banc de brume, côte lointaine) ;
    · un mirage dédouble ou soulève la base (§11.3, §19.4) ;
    · un des deux pointés est simplement faux.

Aucune de ces causes ne se corrige par le calcul. Le contrôle les signale, il
ne les arbitre pas.

Le couple (2, 3) est la mesure : l'angle sous lequel se voit la portion
émergente. C'est la seule grandeur de l'image qui entre dans l'inversion.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

from visee_optique.geometry import Cible

from .inversion import angle_horizon_base
from .optique import (
    Cadrage,
    Capteur,
    MetrologieError,
    Objectif,
    angle_entre_lignes,
    angle_entre_lignes_enveloppe,
    angle_entre_lignes_paraxial,
    pas_angulaire_rad,
)

# Incertitude de pointé par défaut, en pixels, à un écart-type. Trois pixels
# est ce qu'un opérateur atteint sur une limite franche à l'écran, loupe
# activée. Ce n'est pas une constante physique : c'est une valeur par défaut
# que l'opérateur doit remplacer par la dispersion de ses propres pointés
# répétés, ce que le §19.3 impose et ce que `dispersion_pointes` calcule.
SIGMA_POINTE_PX_DEFAUT = 3.0

# Facteur d'élargissement. k = 2, soit environ 95 % pour une loi normale
# (JCGM 100:2008, §6.3.2).
FACTEUR_ELARGISSEMENT = 2.0


@dataclass(frozen=True)
class Pointes:
    """Les trois ordonnées relevées, en pixels du fichier livré.

    L'ordonnée croît vers le bas, comme dans tout fichier image. Le sommet a
    donc l'ordonnée la plus petite.
    """

    y_horizon: float
    y_base: float
    y_sommet: float
    sigma_px: float = SIGMA_POINTE_PX_DEFAUT

    def __post_init__(self):
        if self.sigma_px <= 0:
            raise MetrologieError("L'incertitude de pointé doit être strictement positive.")
        if self.y_sommet >= self.y_base:
            raise MetrologieError(
                "Le sommet doit être au-dessus du bas visible : y_sommet < y_base. "
                "Relevé : y_sommet=%g, y_base=%g." % (self.y_sommet, self.y_base)
            )


def dispersion_pointes(ordonnees: Tuple[float, ...]) -> float:
    """Écart-type expérimental de pointés répétés sur le même repère (§19.3).

    À employer pour remplacer `SIGMA_POINTE_PX_DEFAUT` par une valeur établie
    plutôt que supposée. Exige au moins trois pointés : sur deux, l'écart-type
    existe formellement mais ne dit rien.
    """
    n = len(ordonnees)
    if n < 3:
        raise MetrologieError(
            "Au moins trois pointés répétés sont nécessaires pour une dispersion (§19.3)."
        )
    moyenne = sum(ordonnees) / n
    return math.sqrt(sum((y - moyenne) ** 2 for y in ordonnees) / (n - 1))


@dataclass(frozen=True)
class AngleReleve:
    """Un angle lu sur l'image, sous ses trois formes, avec son incertitude.

    exact : projection rectilinéaire, point principal connu.
    paraxial : la forme du cahier des charges, N_px · p/f.
    borne_basse / borne_haute : enveloppe quand le point principal est inconnu ;
        égales à `exact` quand il est connu.
    incertitude : incertitude élargie due au seul pointé (k = 2, deux pointés
        indépendants).
    """

    exact: Optional[float]
    paraxial: float
    borne_basse: float
    borne_haute: float
    incertitude: float

    @property
    def ecart_paraxial(self) -> Optional[float]:
        """paraxial − exact. Ce que coûte l'approximation du cahier des charges."""
        return None if self.exact is None else self.paraxial - self.exact

    @property
    def valeur(self) -> float:
        """La valeur à employer : l'exacte si elle existe, le milieu de l'enveloppe sinon."""
        if self.exact is not None:
            return self.exact
        return (self.borne_basse + self.borne_haute) / 2.0


def _angle_releve(
    y_haut: float, y_bas: float, sigma_px: float,
    capteur: Capteur, cadrage: Cadrage, objectif: Objectif,
) -> AngleReleve:
    paraxial = angle_entre_lignes_paraxial(y_haut, y_bas, capteur, cadrage, objectif)
    basse, haute = angle_entre_lignes_enveloppe(y_haut, y_bas, capteur, cadrage, objectif)
    exact = (
        angle_entre_lignes(y_haut, y_bas, capteur, cadrage, objectif)
        if cadrage.point_principal_connu
        else None
    )
    # Deux pointés indépendants : les variances s'ajoutent, d'où le √2.
    u = FACTEUR_ELARGISSEMENT * math.sqrt(2.0) * sigma_px * pas_angulaire_rad(
        capteur, cadrage, objectif
    )
    return AngleReleve(
        exact=exact, paraxial=paraxial, borne_basse=basse, borne_haute=haute, incertitude=u
    )


def angle_portion_emergente(
    pointes: Pointes, capteur: Capteur, cadrage: Cadrage, objectif: Objectif
) -> AngleReleve:
    """Clics 2 → 3 : l'angle sous lequel se voit la portion émergente. La mesure."""
    return _angle_releve(
        pointes.y_sommet, pointes.y_base, pointes.sigma_px, capteur, cadrage, objectif
    )


@dataclass(frozen=True)
class ControleHorizon:
    """Confrontation du couple (horizon, bas visible) à ce que le modèle prédit.

    ecart_px : y_horizon − y_base relevé. Positif si l'horizon est SOUS la base
        dans l'image, ce qui est le cas anormal.
    ecart_predit_px : ce que le modèle prédit pour ce même écart, au k retenu.
        Vaut 0 dès que la cible est partiellement occultée.
    tolerance_px : incertitude élargie de l'écart entre deux pointés.
    coherent : vrai si l'écart relevé est compatible avec l'écart prédit.
    """

    ecart_px: float
    ecart_predit_px: float
    tolerance_px: float
    coherent: bool
    causes_possibles: Tuple[str, ...]


CAUSES_ECART_HORIZON = (
    "la cible n'émerge pas directement de l'eau (relief, estran ou ouvrage devant sa base)",
    "la ligne pointée comme horizon n'en est pas un (banc de brume, côte lointaine, nuage bas)",
    "un mirage soulève, abaisse ou dédouble la base (régimes du Tableau 8, §11.3 et §19.4)",
    "l'altitude de base z_b déclarée ne correspond pas à la surface de référence adoptée",
    "l'un des deux pointés est erroné",
)


def controler_horizon(
    pointes: Pointes,
    capteur: Capteur,
    cadrage: Cadrage,
    objectif: Objectif,
    D: float,
    h: float,
    cible: Cible,
    R: float,
) -> ControleHorizon:
    """Vérifie que l'horizon et le bas visible coïncident, comme le modèle l'exige.

    L'écart prédit est converti en pixels par le pas angulaire sur l'axe — une
    conversion au premier ordre, largement suffisante pour un écart qui vaut
    zéro ou presque, et qui n'entre dans aucun calcul de k.

    Ce contrôle ne valide pas la mesure : il peut être satisfait sur un relevé
    faux dont les deux pointés sont faux de la même manière. Il ne fait
    qu'écarter une famille de défauts, celle où les deux pointés se
    contredisent.
    """
    ecart_px = pointes.y_horizon - pointes.y_base
    r = pas_angulaire_rad(capteur, cadrage, objectif)
    ecart_predit_px = angle_horizon_base(D, h, cible, R) / r
    tolerance_px = FACTEUR_ELARGISSEMENT * math.sqrt(2.0) * pointes.sigma_px
    coherent = abs(ecart_px - ecart_predit_px) <= tolerance_px
    return ControleHorizon(
        ecart_px=ecart_px,
        ecart_predit_px=ecart_predit_px,
        tolerance_px=tolerance_px,
        coherent=coherent,
        causes_possibles=() if coherent else CAUSES_ECART_HORIZON,
    )
