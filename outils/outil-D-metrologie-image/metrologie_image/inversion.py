"""
inversion.py — Du seul angle mesuré au coefficient de réfraction (§9, §11, §28).

Ce module ne mesure rien. Il prend un angle relevé sur l'image, le confronte
au modèle sphérique de `visee_optique.geometry` — la référence, jamais recopiée
ici — et rend le coefficient de réfraction k qui rendrait compte de cet angle.

CE QUE k VAUT ICI, ET CE QU'IL NE VAUT PAS
──────────────────────────────────────────
Le k rendu par ce module est le coefficient qui réconcilierait l'angle mesuré
avec le modèle sphérique, SI D, h_obs, H et l'étalonnage angulaire sont exacts.
Ce n'est pas une mesure de la réfraction : aucune donnée atmosphérique n'entre
dans le calcul. Ce n'est pas non plus un verdict sur la forme de la surface :
le modèle sphérique est posé en entrée, pas conclu en sortie. Toute erreur sur
D, h_obs ou H se déverse intégralement dans k, qui est la variable
d'ajustement — c'est pourquoi l'enveloppe, et non la valeur centrale, est le
résultat.

DEUX CORRECTIONS AU CAHIER DES CHARGES
──────────────────────────────────────
1. « Px_masqué = |y_bas − y_horizon| » ne mesure pas la hauteur masquée par la
   courbure. Le rayon rasant qui définit l'horizon est LE MÊME qui définit le
   point le plus bas visible de la cible : il touche la surface au point de
   tangence, puis continue et rencontre la cible à l'altitude z_v. Les deux
   points sont donc sur la même droite de visée et apparaissent exactement à
   la même élévation. On le vérifie analytiquement — c'est
   `test_horizon_et_base_confondus` :

       tan E(z_v, D) = −tan(s(h)/R) = tan E_horizon    pour tout D > D_crit

   La portion cachée n'a aucune extension verticale sur l'image ; elle est
   derrière l'horizon, pas au-dessous de lui. |y_bas − y_horizon| vaut donc
   zéro aux incertitudes de pointé près, et sa vraie valeur est celle d'un
   CONTRÔLE : un écart significatif signale une cible qui n'émerge pas de
   l'eau, un horizon confondu avec autre chose, ou un régime de mirage — pas
   une hauteur.

2. « Ajuster k jusqu'à ce que H_théorique(k) == H_obs » suppose une solution
   unique. Il n'y en a pas toujours. Au-delà d'un certain k la cible est
   entièrement visible et l'angle cesse pratiquement de dépendre de k : toute
   valeur au-dessus convient également. L'égalité n'a alors pas de solution
   déterminée, et en rendre une serait fabriquer un chiffre. Ce module rend un
   statut à quatre valeurs — déterminé, minoré, majoré, indéterminé — et
   n'écrit jamais un k qu'il n'a pas établi.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Sequence, Tuple

from visee_optique.geometry import (
    Cible,
    arc_to_tangent,
    distance_critique,
    distance_limite,
    hauteur_occultee,
)
from visee_optique.refraction import RegimeRefraction, classer_regime, rayon_effectif

from .optique import MetrologieError

# Bornes d'exploration par défaut. Le plafond est sous 1 parce que R_eff n'est
# plus défini au-delà (§11.1) : k ≥ 1 est le régime de conduit optique, où la
# construction du §8 ne s'applique plus. Le plancher est bien au-dessous de
# tout régime tabulé (§11.3) : il est là pour que l'absence de solution soit
# constatée, pas pour être atteinte.
K_PLANCHER = -1.0
K_PLAFOND = 0.99


def elevation(z: float, D: float, h: float, R: float) -> float:
    """Élévation apparente, en radians, d'un point à l'altitude z et à l'arc D.

    Observateur à l'altitude h, surface sphérique de rayon R (y substituer
    R_eff pour tenir compte de la réfraction, §11.1). Angle compté depuis
    l'horizontale locale de l'observateur, positif vers le haut :

        tan E = (r₂·cos ψ − r₁) / (r₂·sin ψ)     ψ = D/R, r₁ = R+h, r₂ = R+z

    C'est la relation de triangle géocentrique, sans approximation de petit
    angle. Le numérateur est presque toujours négatif — une cible lointaine se
    voit sous l'horizontale — mais le dénominateur reste positif sur tout le
    domaine admissible (0 < ψ < π), si bien qu'`atan2` y coïncide avec `atan`
    du quotient. Il est employé parce qu'il ne divise pas, et reste donc défini
    au bord du domaine ; ce n'est pas une correction de signe. Substituer l'un
    à l'autre ne change aucun résultat, et le contrôle d'épinglage le confirme
    en ne signalant rien.
    """
    if R <= 0:
        raise MetrologieError("R doit être strictement positif.")
    if D <= 0:
        raise MetrologieError("La distance D doit être strictement positive.")
    if h < 0 or z < 0:
        raise MetrologieError("Les altitudes ne peuvent pas être négatives.")
    psi = D / R
    if psi >= math.pi:
        raise MetrologieError("D/R ≥ π : la cible est au-delà de l'antipode.")
    r1, r2 = R + h, R + z
    return math.atan2(r2 * math.cos(psi) - r1, r2 * math.sin(psi))


def elevation_horizon(h: float, R: float) -> float:
    """Dépression de l'horizon : E = −s(h)/R, exactement.

    L'arc jusqu'au point de tangence divisé par le rayon donne l'angle
    géocentrique ; la dépression lui est égale, en négatif. Se déduit de
    `elevation` en y portant z = 0 et D = s(h), et c'est ce que vérifie
    `test_horizon_par_deux_chemins`.
    """
    return -arc_to_tangent(h, R) / R


def altitude_visible_la_plus_basse(D: float, h: float, cible: Cible, R: float) -> float:
    """z_v = c + z_b — altitude du point le plus bas encore visible de la cible."""
    return hauteur_occultee(D, h, cible, R) + cible.z_b


def angle_portion_visible(D: float, h: float, cible: Cible, R: float) -> float:
    """Angle vertical entre le point le plus bas visible et le sommet, en radians.

    C'est la grandeur que l'image mesure : l'écart angulaire entre le clic
    « bas visible » et le clic « sommet ». Vaut 0 quand la cible est
    entièrement occultée.
    """
    z_v = altitude_visible_la_plus_basse(D, h, cible, R)
    z_sommet = cible.z_b + cible.H
    if z_v >= z_sommet:
        return 0.0
    return elevation(z_sommet, D, h, R) - elevation(z_v, D, h, R)


def angle_horizon_base(D: float, h: float, cible: Cible, R: float) -> float:
    """Angle prédit entre l'horizon et le point le plus bas visible, en radians.

    Vaut exactement 0 dès que D dépasse D_crit — c'est le théorème rappelé en
    tête de module. En deçà, la base réelle de la cible est encore au-dessus de
    l'horizon et l'angle est positif. C'est la valeur à confronter au relevé
    des clics 1 et 2.
    """
    z_v = altitude_visible_la_plus_basse(D, h, cible, R)
    return elevation(z_v, D, h, R) - elevation_horizon(h, R)


def _bissecter_k_sur_distance(
    distance_modele, D: float, h: float, cible: Cible, R0: float,
    k_plancher: float, k_plafond: float,
) -> Optional[float]:
    """k tel que `distance_modele(h, cible, R_eff(k))` vaille D, ou None hors domaine.

    D_crit et D_lim croissent toutes deux avec R, donc avec k : la bissection
    est bien posée pour l'une comme pour l'autre.

    Rend None quand le croisement n'a pas lieu dans l'intervalle exploré. Les
    deux appelants n'en tirent pas la même conclusion, et c'est pourquoi cette
    fonction ne la tire pas à leur place.
    """
    def ecart(k: float) -> float:
        return distance_modele(h, cible, rayon_effectif(R0, k)) - D

    if ecart(k_plancher) >= 0 or ecart(k_plafond) < 0:
        return None
    lo, hi = k_plancher, k_plafond
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if ecart(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def k_de_saturation(
    D: float, h: float, cible: Cible, R0: float,
    k_plancher: float = K_PLANCHER, k_plafond: float = K_PLAFOND,
) -> Optional[float]:
    """Le k au-dessus duquel plus rien n'est occulté (D = D_crit), ou None.

    Au-delà de ce seuil, l'angle mesuré ne dépend presque plus de k : c'est la
    zone où l'inversion perd son pouvoir de résolution, et la connaître permet
    de le dire au lieu de rendre une valeur précise dépourvue de sens.

    None quand la saturation n'est pas atteinte dans les bornes explorées :
    la cible reste alors partiellement occultée pour tout k admissible.
    Le plancher lui-même est rendu quand la cible est déjà entière à ce
    plancher — la saturation couvre alors tout le domaine.
    """
    if distance_critique(h, cible, rayon_effectif(R0, k_plancher)) >= D:
        return k_plancher
    return _bissecter_k_sur_distance(
        distance_critique, D, h, cible, R0, k_plancher, k_plafond
    )


def k_d_extinction(
    D: float, h: float, cible: Cible, R0: float,
    k_plancher: float = K_PLANCHER, k_plafond: float = K_PLAFOND,
) -> Optional[float]:
    """Le k au-dessous duquel la cible est entièrement occultée (D = D_lim), ou None.

    Symétrique de `k_de_saturation`, et tout aussi destructeur d'information :
    sous ce seuil l'angle prédit vaut exactement zéro pour TOUTE valeur de k.
    Un relevé nul ne détermine donc pas k, il le majore — et c'est ce que le
    cahier des charges ne prévoyait pas en écrivant « ajuster k jusqu'à ce que
    H_théorique(k) == H_obs ». La bissection, prise au mot, aurait rendu le
    plancher d'exploration comme s'il s'agissait d'une mesure : un chiffre
    parfaitement précis et parfaitement vide.

    None quand la cible reste partiellement visible pour tout k exploré. Le
    plafond est rendu quand elle est occultée jusqu'au plafond — l'extinction
    couvre alors tout le domaine, et aucun relevé ne peut y déterminer k.
    """
    if distance_limite(h, cible, rayon_effectif(R0, k_plafond)) < D:
        return k_plafond
    return _bissecter_k_sur_distance(
        distance_limite, D, h, cible, R0, k_plancher, k_plafond
    )


class StatutK(str, Enum):
    """Ce que l'inversion a pu établir. Quatre valeurs, jamais un chiffre par défaut."""

    DETERMINE = "déterminé"
    MINORE = "minoré seulement"       # l'angle mesuré excède ce que k_plafond prédit
    MAJORE = "majoré seulement"       # l'angle mesuré est sous ce que k_plancher prédit
    INDETERMINE = "indéterminé"


def _resoudre_k(
    angle_mesure_rad: float, D: float, h: float, cible: Cible, R0: float,
    k_plancher: float, k_plafond: float,
) -> Tuple[Optional[float], StatutK]:
    """Bissection sur k. Rend (k, statut) ; k est None dès que le statut ne l'établit pas.

    L'angle prédit croît avec k — plus la réfraction courbe le rayon, moins la
    cible est occultée. La monotonie n'est pas supposée : la bissection exige
    un changement de signe aux bornes et le constate, faute de quoi elle rend
    un statut de borne au lieu d'une valeur.
    """
    def ecart(k: float) -> float:
        return angle_portion_visible(D, h, cible, rayon_effectif(R0, k)) - angle_mesure_rad

    if angle_mesure_rad <= 0.0:
        # Rien de visible relevé. L'angle prédit vaut exactement zéro sur tout
        # l'intervalle où la cible est occultée jusqu'au sommet : la bissection
        # y convergerait vers le plancher d'exploration et rendrait ce plancher
        # comme s'il s'agissait d'une mesure. C'est une borne, pas une valeur.
        return None, StatutK.MAJORE

    e_bas, e_haut = ecart(k_plancher), ecart(k_plafond)
    if e_bas > 0:
        # Même la surface la plus courbe explorée laisse voir plus que le relevé.
        return None, StatutK.MAJORE
    if e_haut < 0:
        # Même la surface la plus plate explorée laisse voir moins que le relevé.
        return None, StatutK.MINORE
    lo, hi = k_plancher, k_plafond
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if ecart(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0, StatutK.DETERMINE


@dataclass(frozen=True)
class ResultatK:
    """Ce que l'inversion établit, avec ce qu'elle n'établit pas.

    k : valeur centrale, ou None si le statut ne l'établit pas.
    k_min, k_max : bornes de l'enveloppe ; None du côté où elle est ouverte.
    regime_determine : vrai seulement si les deux bornes tombent dans le même
        régime du Tableau 8. Faux, l'enveloppe traverse plusieurs régimes et
        nommer l'un d'eux serait choisir.
    """

    statut: StatutK
    k: Optional[float]
    k_min: Optional[float]
    k_max: Optional[float]
    angle_mesure_rad: float
    angle_modele_rad: Optional[float]
    k_saturation: Optional[float]
    k_extinction: Optional[float]
    dans_zone_saturee: bool
    dans_zone_eteinte: bool
    regime: Optional[RegimeRefraction]
    regime_min: Optional[RegimeRefraction]
    regime_max: Optional[RegimeRefraction]

    @property
    def regime_determine(self) -> bool:
        return (
            self.regime_min is not None
            and self.regime_max is not None
            and self.regime_min == self.regime_max
        )

    @property
    def enveloppe_ouverte(self) -> bool:
        return self.k_min is None or self.k_max is None


def coefficient_refraction_effectif(
    angle_mesure_rad: float,
    angle_incertitude_rad: float,
    D: float,
    h: float,
    cible: Cible,
    R0: float,
    k_plancher: float = K_PLANCHER,
    k_plafond: float = K_PLAFOND,
) -> ResultatK:
    """Inverse l'angle mesuré en coefficient de réfraction, avec son enveloppe.

    `angle_incertitude_rad` est une incertitude ÉLARGIE (elle est employée
    telle quelle pour les bornes, sans facteur d'élargissement ajouté ici :
    c'est à l'appelant de déclarer ce qu'il fournit). L'enveloppe est obtenue
    en réinversant aux deux bornes de l'angle, pas en dérivant : la relation
    k ↦ angle est trop plate près de la saturation pour qu'une dérivée y ait
    un sens, et une enveloppe ouverte est un résultat, pas un échec.
    """
    if angle_incertitude_rad < 0:
        raise MetrologieError("L'incertitude sur l'angle ne peut pas être négative.")

    k, statut = _resoudre_k(angle_mesure_rad, D, h, cible, R0, k_plancher, k_plafond)
    k_bas, _ = _resoudre_k(
        angle_mesure_rad - angle_incertitude_rad, D, h, cible, R0, k_plancher, k_plafond
    )
    k_haut, _ = _resoudre_k(
        angle_mesure_rad + angle_incertitude_rad, D, h, cible, R0, k_plancher, k_plafond
    )
    k_sat = k_de_saturation(D, h, cible, R0, k_plancher, k_plafond)
    k_ext = k_d_extinction(D, h, cible, R0, k_plancher, k_plafond)

    angle_modele = (
        angle_portion_visible(D, h, cible, rayon_effectif(R0, k)) if k is not None else None
    )
    dans_zone_saturee = k is not None and k_sat is not None and k >= k_sat
    dans_zone_eteinte = statut is StatutK.MAJORE and angle_mesure_rad <= 0.0

    return ResultatK(
        statut=statut,
        k=k,
        k_min=k_bas,
        k_max=k_haut,
        angle_mesure_rad=angle_mesure_rad,
        angle_modele_rad=angle_modele,
        k_saturation=k_sat,
        k_extinction=k_ext,
        dans_zone_saturee=dans_zone_saturee,
        dans_zone_eteinte=dans_zone_eteinte,
        regime=classer_regime(k) if k is not None else None,
        regime_min=classer_regime(k_bas) if k_bas is not None else None,
        regime_max=classer_regime(k_haut) if k_haut is not None else None,
    )


@dataclass(frozen=True)
class Plage:
    """Un paramètre d'entrée, son enveloppe, et la source qui l'établit (§6.2).

    LA SOURCE EST RELEVÉE, PLUS EXIGÉE — ET POURQUOI
    ────────────────────────────────────────────────
    Une première version refusait de construire une `Plage` sans source. Le
    raisonnement était bon et la conséquence mauvaise : une chaîne saisie dans
    un champ n'est pas une source vérifiée, et l'analyste qui reprend le dossier
    refait le travail de toute façon. Le verrou ne garantissait donc rien ; il
    empêchait seulement de calculer.

    La source reste donc portée, et son ABSENCE est portée avec elle :
    `source_declaree` le dit, `synthese.sources_manquantes` en fait la liste, et
    cette liste voyage jusque dans la synthèse exportée. L'information n'est pas
    perdue — elle est rendue visible au lieu d'être rendue bloquante, ce qui est
    précisément ce qu'un analyste doit trouver dans un dossier.

    Ce qui reste refusé, parce que c'est une incohérence et non une lacune : une
    valeur hors de sa propre enveloppe.
    """

    nom: str
    valeur: float
    borne_basse: float
    borne_haute: float
    source: str = ""

    def __post_init__(self):
        if not (self.borne_basse <= self.valeur <= self.borne_haute):
            raise MetrologieError(
                "%s : la valeur %g doit être dans son enveloppe [%g ; %g]."
                % (self.nom, self.valeur, self.borne_basse, self.borne_haute)
            )

    @property
    def bornes(self) -> Tuple[float, float]:
        return (self.borne_basse, self.borne_haute)

    @property
    def source_declaree(self) -> bool:
        return bool(self.source and self.source.strip())


@dataclass(frozen=True)
class EnveloppeK:
    """L'enveloppe de k sur toutes les combinaisons d'entrées explorées.

    k_min / k_max valent None du côté où au moins une combinaison ne borne
    pas k. Une borne ouverte contamine l'enveloppe entière : c'est délibéré,
    puisqu'une seule combinaison admissible non bornée suffit à ce que k ne
    soit pas borné de ce côté.
    """

    k_min: Optional[float]
    k_max: Optional[float]
    combinaisons: int
    combinaisons_non_bornees: int
    statuts: Tuple[StatutK, ...]

    @property
    def determinee(self) -> bool:
        return self.k_min is not None and self.k_max is not None


def enveloppe_coefficient(
    angle_mesure_rad: float,
    angle_incertitude_rad: float,
    distance: Plage,
    altitude_observateur: Plage,
    hauteur_cible: Plage,
    altitude_base: Plage,
    R0: float,
    k_plancher: float = K_PLANCHER,
    k_plafond: float = K_PLAFOND,
) -> EnveloppeK:
    """Balaie les seize sommets des quatre enveloppes d'entrée, plus l'angle.

    Le balayage se fait aux sommets et non par tirage : les quatre grandeurs
    entrent de façon monotone dans la géométrie, donc l'extremum de k est
    atteint sur un sommet. Ce n'est pas une hypothèse de commodité — c'est ce
    que `test_sommets_bornent_le_tirage` vérifie contre un tirage aléatoire
    dense.
    """
    sommets: List[Tuple[float, float, float, float]] = []
    for d in distance.bornes:
        for h in altitude_observateur.bornes:
            for H in hauteur_cible.bornes:
                for zb in altitude_base.bornes:
                    sommets.append((d, h, H, zb))

    ks: List[float] = []
    statuts: List[StatutK] = []
    ouvert_bas = ouvert_haut = False
    non_bornees = 0

    for d, h, H, zb in sommets:
        cible = Cible(H=H, z_b=zb)
        r = coefficient_refraction_effectif(
            angle_mesure_rad, angle_incertitude_rad, d, h, cible, R0, k_plancher, k_plafond
        )
        statuts.append(r.statut)
        if r.k_min is None:
            ouvert_bas = True
        else:
            ks.append(r.k_min)
        if r.k_max is None:
            ouvert_haut = True
        else:
            ks.append(r.k_max)
        if r.enveloppe_ouverte:
            non_bornees += 1

    return EnveloppeK(
        k_min=None if (ouvert_bas or not ks) else min(ks),
        k_max=None if (ouvert_haut or not ks) else max(ks),
        combinaisons=len(sommets),
        combinaisons_non_bornees=non_bornees,
        statuts=tuple(statuts),
    )
