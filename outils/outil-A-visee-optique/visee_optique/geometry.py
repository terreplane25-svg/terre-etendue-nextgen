"""
geometry.py — Géométrie exacte de la portion visible (§8-9 du protocole).

Implémente la construction du rayon rasant tangent à une surface de
référence sphérique, sans aucune approximation de petit angle : la
corde ne remplace jamais l'arc, la sécante n'est jamais développée au
premier ordre. Le §9.4 du protocole montre que ces approximations
classiques divergent de plusieurs dizaines de mètres au-delà de
quelques centaines de mètres d'altitude d'observation ; elles ne sont
fournies ici que pour comparaison explicite (arc_approx_petit_angle,
hauteur_occultee_approx), jamais pour la mesure elle-même.

Chaque fonction correspond à un CALCUL au sens du Tableau 2 (§6.2) :
une opération déterministe sur des grandeurs déjà établies (faits
mesurés, données externes, hypothèses). Aucune fonction ici ne lit une
image ni ne produit une décision.
"""

import math
from dataclasses import dataclass

__all__ = [
    "GeometryError",
    "Cible",
    "arc_to_tangent",
    "altitude_from_arc",
    "distance_critique",
    "distance_limite",
    "distance_pour_hauteur_occultee",
    "hauteur_occultee",
    "fraction_visible",
    "fraction_visible_modele_plan",
    "arc_approx_petit_angle",
    "hauteur_occultee_approx",
    "resoudre_altitude_par_dichotomie",
    "IUGG_R1",
]


class GeometryError(ValueError):
    """Domaine invalide pour un calcul géométrique (§8-9)."""


# Rayon moyen R1 = (2a+b)/3 de l'ellipsoïde GRS80 (§4.1, Moritz 2000).
# Valeur de travail par défaut / exemples uniquement : pour une observation
# réelle, le §12.2 impose le rayon de courbure normal à l'azimut de la
# visée (rayon d'Euler), jamais R1, sous peine de l'écart de ~1% chiffré
# à l'objection n°1 (§31).
IUGG_R1 = 6_371_008.8  # m


def arc_to_tangent(x: float, R: float) -> float:
    """s(x) = R·arccos[R/(R+x)] — §9.1.

    Arc au sol, mesuré sur la sphère de rayon R, entre le pied d'un point
    situé à l'altitude x au-dessus de la surface et son point de tangence.
    x et R en mètres ; résultat en mètres.
    """
    if R <= 0:
        raise GeometryError("R doit être strictement positif.")
    if x < 0:
        raise GeometryError("L'altitude x ne peut pas être négative.")
    return R * math.acos(R / (R + x))


def altitude_from_arc(arc: float, R: float) -> float:
    """Inverse exacte de arc_to_tangent : x tel que arc_to_tangent(x, R) == arc.

    Redérivée directement de s(x) = R·arccos[R/(R+x)] :
        theta = arc / R
        R/(R+x) = cos(theta)  =>  x = R·(sec(theta) - 1)

    C'est exactement la construction de z_v au §9.3 (« l'argument de la
    sécante est un angle géocentrique, en radians » — l'altitude de base
    n'entre pas dans cet argument, elle se retranche après, cf.
    hauteur_occultee ci-dessous).
    """
    if R <= 0:
        raise GeometryError("R doit être strictement positif.")
    if arc < 0:
        raise GeometryError("Un arc ne peut pas être négatif.")
    theta = arc / R
    if theta >= math.pi / 2:
        raise GeometryError(
            "Arc hors du domaine défini de la construction de tangence "
            "(theta = arc/R >= pi/2)."
        )
    return R * (1.0 / math.cos(theta) - 1.0)


@dataclass(frozen=True)
class Cible:
    """Paramètres de cible établis indépendamment de la photographie (§12.4).

    H : hauteur totale de la cible, en mètres (§6.1).
    z_b : altitude de la base au-dessus de la surface de référence adoptée,
          en mètres (0 pour une base au niveau moyen de la mer, §10).
    """

    H: float
    z_b: float = 0.0

    def __post_init__(self):
        if self.H <= 0:
            raise GeometryError("La hauteur de cible H doit être strictement positive.")
        if self.z_b < 0:
            raise GeometryError("L'altitude de base z_b ne peut pas être négative.")


def distance_pour_hauteur_occultee(c: float, h: float, cible: Cible, R: float) -> float:
    """D tel que hauteur_occultee(D, h, cible, R) == c — inverse de hauteur_occultee (§9.2-9.3).

    Généralise distance_critique (c = 0) et distance_limite (c = H) à toute
    hauteur occultée cible, y compris au-delà de H (§9.3 : c continue de
    croître après D_lim). Utile pour résoudre en distance une condition
    posée sur c, comme la condition de discrimination du §28.2.
    """
    if c < 0:
        raise GeometryError("La hauteur occultée cible ne peut pas être négative.")
    return arc_to_tangent(h, R) + arc_to_tangent(c + cible.z_b, R)


def distance_critique(h: float, cible: Cible, R: float) -> float:
    """D_crit = s(h) + s(z_b) — distance au-delà de laquelle la base cesse d'être visible (§9.2)."""
    return distance_pour_hauteur_occultee(0.0, h, cible, R)


def distance_limite(h: float, cible: Cible, R: float) -> float:
    """D_lim = s(h) + s(z_b + H) — distance au-delà de laquelle le sommet cesse d'être visible (§9.2)."""
    return distance_pour_hauteur_occultee(cible.H, h, cible, R)


def hauteur_occultee(D: float, h: float, cible: Cible, R: float) -> float:
    """c(D) — hauteur occultée à la distance D (§9.3).

    Pour D <= D_crit, rien n'est occulté : c = 0 (borne physique basse,
    en-deçà de l'horizon rien ne peut être caché). Au-delà, c suit la
    construction exacte en sécante et peut dépasser H une fois D > D_lim
    (le Tableau 6 du protocole l'illustre : c continue de croître au-delà
    de la hauteur de cible). C'est fraction_visible, et non cette
    fonction, qui borne le résultat physiquement interprétable à [0 ; 1].
    """
    d_crit = distance_critique(h, cible, R)
    if D <= d_crit:
        return 0.0
    s_h = arc_to_tangent(h, R)
    z_v = altitude_from_arc(D - s_h, R)
    return z_v - cible.z_b


def fraction_visible(D: float, h: float, cible: Cible, R: float) -> float:
    """f = (H - c) / H, bornée à [0 ; 1] (§6.1, §9.3).

    Grandeur comparée entre modèles et mesure. Modèle S (§4.1) : surface
    sphérique de rayon R (ou du rayon effectif R_eff, cf. refraction.py,
    si l'appelant y substitue R).
    """
    c = hauteur_occultee(D, h, cible, R)
    f = (cible.H - c) / cible.H
    return min(1.0, max(0.0, f))


def fraction_visible_modele_plan(D: float) -> float:
    """Modèle P (§4.2) : surface plane, aucune occultation géométrique.

    f = 1 pour toute distance D > 0. La disparition éventuelle de la
    cible relève de la résolution du système optique ou de l'extinction
    atmosphérique (§15, §20) — jamais de cette fonction, qui ne modélise
    que la géométrie.
    """
    if D <= 0:
        raise GeometryError("La distance D doit être strictement positive.")
    return 1.0


# --- Approximations classiques (§9.4) — comparaison uniquement, jamais la mesure ---


def arc_approx_petit_angle(x: float, R: float) -> float:
    """√(2·R·x) — approximation classique de s(x) (corde + petit angle).

    Le Tableau 3 du protocole montre un écart croissant avec x : sous le
    mètre jusqu'à 100 m d'altitude d'observation, mais 40 m à 3107 m.
    Fournie ici pour reproduire cette comparaison, jamais pour la mesure.
    """
    if x < 0:
        raise GeometryError("x ne peut pas être négatif.")
    if R <= 0:
        raise GeometryError("R doit être strictement positif.")
    return math.sqrt(2.0 * R * x)


def hauteur_occultee_approx(D: float, h: float, R: float) -> float:
    """c ≈ (D - √(2·R·h))² / (2·R) — approximation classique (§9.4).

    Le Tableau 4 du protocole la compare à hauteur_occultee (à z_b = 0) :
    l'écart reste sous 4 cm pour la géométrie de l'exemple du §10, mais
    « cette conclusion doit être revérifiée pour toute autre géométrie »
    — l'approximation n'est jamais bornée a priori par ce module.
    """
    if R <= 0:
        raise GeometryError("R doit être strictement positif.")
    return (D - arc_approx_petit_angle(h, R)) ** 2 / (2.0 * R)


# --- Résolution numérique indépendante (§10.3) — non-régression, jamais la mesure ---


def resoudre_altitude_par_dichotomie(
    arc: float, R: float, tol: float = 1e-6, max_iter: int = 200
) -> float:
    """Retrouve x tel que arc_to_tangent(x, R) == arc, par bissection.

    Méthode indépendante de altitude_from_arc, exigée par le §10.3 comme
    test de non-régression : le protocole demande un accord à mieux d'un
    micromètre avec la forme fermée sur toute la plage utile. N'est
    jamais utilisée pour produire une prédiction — seulement pour vérifier
    que la forme fermée est correctement implémentée.
    """
    if R <= 0:
        raise GeometryError("R doit être strictement positif.")
    if arc < 0:
        raise GeometryError("Un arc ne peut pas être négatif.")
    if arc / R >= math.pi / 2:
        raise GeometryError(
            "Arc hors du domaine défini de la construction de tangence "
            "(arc/R >= pi/2)."
        )
    if arc == 0:
        return 0.0

    lo, hi = 0.0, 1.0
    while arc_to_tangent(hi, R) < arc:
        hi *= 2.0
    for _ in range(max_iter):
        mid = (lo + hi) / 2.0
        if arc_to_tangent(mid, R) < arc:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2.0
