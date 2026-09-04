"""
models.py — Modèles concurrents et condition de discrimination (§29, §28.2).

§29 pose une règle unique : un modèle n'entre dans la comparaison que
s'il est déposé avec ses quatre éléments — géométrie de surface, loi de
propagation de la lumière, paramètres libres et leurs intervalles, et
la prédiction explicite qu'il fait sur f(D). Un modèle dont la loi de
propagation reste libre reproduit n'importe quelle observation ; il
n'est pas réfutable, donc pas comparable — et cela vaut identiquement
pour un modèle plan à réfraction ad hoc et pour un modèle sphérique à k
libre (§29.1). D'où la classe `Modele` : ses quatre éléments sont des
attributs obligatoires, pas des conventions de nommage.

§28.2 en découle : la configuration observée n'est exploitable que si
l'écart Δ entre les deux prédictions, évalué au bord d'enveloppe le
plus défavorable à la discrimination, atteint au moins 5 fois
l'incertitude composée sur la fraction observée. Ce module calcule Δ
sur l'enveloppe jointe des deux modèles (§23.1), pas au point nominal.

Ce que ce module NE fait PAS : le verdict à trois valeurs du §28.3
(compatible / incompatible / indéterminé) mêle cette condition à des
éléments que rien ici ne mesure — validité d'image (§18), régimes
atmosphériques recherchés (§19.4), convergence des trois analystes
(§25) — et à la comparaison de vraisemblance pénalisée du §27.2. Ces
deux étapes sont dans decision.py, qui consomme `ConditionDiscrimination`
et `EnveloppeSensibilite` tels que définis ici, sans les redéfinir.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Mapping, Sequence, Tuple

from .geometry import Cible, fraction_visible, fraction_visible_modele_plan
from .refraction import HypotheseRefraction, rayon_effectif
from .uncertainty import EnveloppeSensibilite, PlageParametre, balayer_enveloppe

__all__ = [
    "ModelError",
    "Modele",
    "ModeleSpherique",
    "ModeleSurfacePlane",
    "ConditionDiscrimination",
    "delta_le_plus_defavorable",
    "condition_discrimination",
]


class ModelError(ValueError):
    """Domaine invalide, ou modèle déposé de façon incomplète (§29)."""


class Modele(ABC):
    """Un modèle candidat au sens du §29.

    Les sous-classes doivent porter `nom`, `geometrie` et `loi_propagation`
    comme attributs (des chaînes descriptives, pas des valeurs de calcul),
    déclarer `parametres_libres`, et implémenter `predire`. Rien dans ce
    module n'admet un modèle qui ne fournirait pas les quatre.
    """

    nom: str
    geometrie: str
    loi_propagation: str

    @property
    @abstractmethod
    def parametres_libres(self) -> Tuple[PlageParametre, ...]:
        """Les paramètres propres au modèle, avec leurs intervalles déposés (§26, §29).

        Ne comprend PAS les grandeurs géodésiques ou instrumentales
        partagées par tous les modèles (h, D, position, focale...) : celles-là
        sont des plages de sensibilité communes (§23.1), pas des paramètres
        du modèle. Un modèle sans paramètre libre (le modèle P, §29.3)
        retourne un tuple vide.
        """

    @abstractmethod
    def predire(self, D: float, **parametres) -> float:
        """f(D) prédit par ce modèle pour les paramètres fournis.

        Doit accepter, en plus de ses propres `parametres_libres`, toute
        grandeur géodésique ou instrumentale nécessaire à sa géométrie
        (typiquement `h`), passée par nom. Les paramètres superflus pour
        ce modèle sont ignorés plutôt que rejetés, pour permettre
        d'appeler deux modèles avec le même jeu de paramètres balayés.
        """

    @property
    def nombre_parametres_libres(self) -> int:
        """Pour la pénalisation du nombre de paramètres libres (§27.2, hors de ce module)."""
        return len(self.parametres_libres)

    def enveloppe_prediction(
        self,
        D: float,
        plages_supplementaires: Sequence[PlageParametre] = (),
        pas_par_parametre: int = 5,
        max_grille: int = 100_000,
        germe: "int | None" = None,
        **fixes,
    ) -> EnveloppeSensibilite:
        """Balaie parametres_libres + les plages supplémentaires fournies (§23.1).

        `plages_supplementaires` porte les grandeurs communes aux deux
        modèles (h, D lui-même s'il est incertain, position, etc.) —
        jamais dupliquées ici depuis le modèle, puisqu'elles ne lui
        appartiennent pas.
        """
        toutes_plages = tuple(self.parametres_libres) + tuple(plages_supplementaires)
        noms = [p.nom for p in toutes_plages]
        if len(set(noms)) != len(noms):
            raise ModelError(
                f"Des plages portent le même nom pour le modèle « {self.nom} » : {noms}."
            )

        def fonction(**params):
            return self.predire(D, **{**fixes, **params})

        return balayer_enveloppe(
            fonction,
            toutes_plages,
            pas_par_parametre=pas_par_parametre,
            max_grille=max_grille,
            germe=germe,
        )


@dataclass(frozen=True)
class ModeleSpherique(Modele):
    """Modèle S (§4.1) : surface sphérique de rayon R, rayon rasant courbé par k.

    Seul paramètre libre : k, dans l'intervalle déposé par `hypothese_k`
    (§11.7, §26) — jamais un k ponctuel choisi après coup.
    """

    R: float
    cible: Cible
    hypothese_k: HypotheseRefraction
    nom: str = field(default="S — surface sphérique", init=False)
    geometrie: str = field(
        default="Sphère de rayon R, occultation par le rayon rasant tangent (§4.1, §8)",
        init=False,
    )
    loi_propagation: str = field(
        default="Rayon courbé par réfraction atmosphérique, coefficient k (§4.1, §11)",
        init=False,
    )

    @property
    def parametres_libres(self) -> Tuple[PlageParametre, ...]:
        return (
            PlageParametre(
                "k",
                self.hypothese_k.k_min,
                self.hypothese_k.k_max,
                self.hypothese_k.justification,
            ),
        )

    def predire(self, D: float, **parametres) -> float:
        try:
            h = parametres["h"]
            k = parametres["k"]
        except KeyError as exc:
            raise ModelError(
                f"Modèle S : paramètre manquant pour la prédiction : {exc}"
            ) from exc
        return fraction_visible(D, h, self.cible, rayon_effectif(self.R, k))


@dataclass(frozen=True)
class ModeleSurfacePlane(Modele):
    """Modèle P (§4.2) : surface plane, aucune occultation géométrique.

    Aucun paramètre libre (§29.3) : c'est un avantage dans une comparaison
    pénalisée par le nombre de paramètres, et une fragilité symétrique —
    c'est exactement pour ça que le §28.2 exige la condition de
    discrimination avant toute comparaison, plutôt que de laisser le
    nombre de paramètres trancher seul.
    """

    nom: str = field(default="P — surface plane", init=False)
    geometrie: str = field(default="Plan, aucune occultation géométrique (§4.2)", init=False)
    loi_propagation: str = field(
        default="Propagation rectiligne — aucune réfraction n'est modélisée (§4.2)", init=False
    )

    @property
    def parametres_libres(self) -> Tuple[PlageParametre, ...]:
        return ()

    def predire(self, D: float, **parametres) -> float:
        return fraction_visible_modele_plan(D)


# --- §28.2 : condition de discrimination ---


@dataclass(frozen=True)
class ConditionDiscrimination:
    """Le résultat de la condition de discrimination du §28.2.

    `delta` est l'écart minimal entre les deux prédictions sur
    l'enveloppe jointe — le bord le plus défavorable à la discrimination,
    jamais un écart au point nominal. `satisfaite` est le verdict de
    recevabilité géométrique lui-même : au-dessous, l'observation est
    classée indéterminée avant même que la fraction visible soit mesurée
    (§28.2, dernier paragraphe).
    """

    delta: float
    combinaison_defavorable: Mapping[str, float]
    u_f: float
    facteur: float
    satisfaite: bool

    @property
    def seuil(self) -> float:
        return self.facteur * self.u_f


def delta_le_plus_defavorable(
    modele_a: Modele,
    modele_b: Modele,
    D: float,
    plages_supplementaires: Sequence[PlageParametre] = (),
    pas_par_parametre: int = 9,
    max_grille: int = 100_000,
    germe: "int | None" = None,
    **fixes,
) -> Tuple[float, Mapping[str, float]]:
    """Écart minimal |f_a(D) − f_b(D)| sur l'enveloppe jointe des deux modèles (§28.2).

    Balaie ensemble les paramètres libres des deux modèles et les plages
    supplémentaires fournies ; retourne le minimum de |Δf| et la
    combinaison qui l'atteint — le bord d'enveloppe le plus défavorable
    à la discrimination, tel qu'exigé par le §28.2 (« pour le couple S
    contre P, le coefficient de réfraction maximal retenu » n'est pas un
    cas particulier câblé ici, c'est ce que ce balayage retrouve de
    lui-même pour ce couple précis).
    """
    toutes_plages = tuple(modele_a.parametres_libres) + tuple(modele_b.parametres_libres) + tuple(
        plages_supplementaires
    )
    noms = [p.nom for p in toutes_plages]
    if len(set(noms)) != len(noms):
        raise ModelError(f"Des plages portent le même nom dans la comparaison : {noms}.")

    def ecart(**params):
        params_complets = {**fixes, **params}
        return abs(modele_a.predire(D, **params_complets) - modele_b.predire(D, **params_complets))

    enveloppe = balayer_enveloppe(
        ecart,
        toutes_plages,
        pas_par_parametre=pas_par_parametre,
        max_grille=max_grille,
        germe=germe,
    )
    return enveloppe.minimum, enveloppe.combinaison_minimale


def condition_discrimination(
    modele_a: Modele,
    modele_b: Modele,
    D: float,
    u_f: float,
    plages_supplementaires: Sequence[PlageParametre] = (),
    facteur: float = 5.0,
    pas_par_parametre: int = 9,
    max_grille: int = 100_000,
    germe: "int | None" = None,
    **fixes,
) -> ConditionDiscrimination:
    """Δ ≥ facteur · u(f) — condition de discrimination du §28.2.

    `facteur = 5` est la valeur recommandée au §26 comme barre
    d'admission, au-dessus du seuil de réfutation à 3σ ; elle n'a rien
    d'obligatoire (§28.2) et se remplace par la valeur réellement
    déposée avant l'observation.

    Évaluée a posteriori, sur les paramètres réellement établis (§28.2) —
    jamais avant, et jamais avec un intervalle élargi ou resserré après
    avoir vu le résultat.
    """
    if u_f < 0:
        raise ModelError("u(f) ne peut pas être négative.")
    delta, combinaison = delta_le_plus_defavorable(
        modele_a,
        modele_b,
        D,
        plages_supplementaires,
        pas_par_parametre=pas_par_parametre,
        max_grille=max_grille,
        germe=germe,
        **fixes,
    )
    seuil = facteur * u_f
    return ConditionDiscrimination(
        delta=delta,
        combinaison_defavorable=combinaison,
        u_f=u_f,
        facteur=facteur,
        satisfaite=delta >= seuil,
    )
