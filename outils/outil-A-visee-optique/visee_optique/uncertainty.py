"""
uncertainty.py — Incertitude JCGM/GUM et analyse de sensibilité (§22-23).

Ce module a deux responsabilités distinctes, correspondant aux deux
sections du protocole :

  §22 — composer des incertitudes de mesure ou de prédiction, dont
        chaque composante porte son type (A si elle vient d'une
        dispersion statistique, B sinon) et sa source, composées en
        quadrature si indépendantes ou en tenant compte de leur
        corrélation sinon (§22.3).

  §23 — balayer systématiquement l'intervalle d'incertitude de chaque
        paramètre d'entrée et rapporter l'ENVELOPPE des prédictions qui
        en résulte, jamais une valeur centrale. Le §23.2 est intraitable
        sans discipline : « si une seule combinaison admissible des
        paramètres rend l'observation conforme à la prédiction d'un
        modèle, ce modèle n'est pas réfuté par cette observation ».

Ce module ne décide rien : la condition de discrimination (§28.2, qui
compare Δ à 5·u(f)) et le verdict à trois valeurs (§28.3) appartiennent
à un futur module de décision, qui consommera les objets définis ici
sans les redéfinir.
"""

import itertools
import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Mapping, Optional, Sequence

__all__ = [
    "UncertaintyError",
    "TypeIncertitude",
    "Composante",
    "Correlation",
    "Incertitude",
    "composer",
    "PlageParametre",
    "EnveloppeSensibilite",
    "balayer_enveloppe",
    "effet_sensibilite",
    "modele_refute_par",
]


class UncertaintyError(ValueError):
    """Domaine invalide pour un calcul ou une déclaration d'incertitude (§22-23)."""


class TypeIncertitude(str, Enum):
    """§22 : type d'évaluation d'une composante — pas sa distribution, sa méthode d'obtention."""

    A = "A"  # dispersion statistique (répétabilité, dispersion entre analystes...)
    B = "B"  # tout autre moyen (spécification constructeur, borne physique, littérature...)


@dataclass(frozen=True)
class Composante:
    """Une composante d'incertitude déjà exprimée en écart-type (§22.1, §22.2).

    valeur : l'incertitude-type u_i, dans la même unité que la grandeur
             qu'elle affecte. Toute conversion depuis une incertitude
             élargie ou une hypothèse de distribution (rectangulaire,
             triangulaire...) doit être faite avant de construire cet
             objet ; `distribution` ne fait que documenter ce choix,
             elle n'intervient dans aucun calcul ici.
    source : d'où vient la composante — jamais omise (Tableau 2, §6.2 :
             aucune valeur sans son statut et son origine).
    """

    nom: str
    type: TypeIncertitude
    valeur: float
    source: str
    distribution: str = "non précisée"

    def __post_init__(self):
        if self.valeur < 0:
            raise UncertaintyError("Une incertitude-type ne peut pas être négative.")
        if not self.nom.strip():
            raise UncertaintyError("Une composante doit être nommée pour pouvoir être corrélée.")
        if not self.source.strip():
            raise UncertaintyError(f"La composante « {self.nom} » doit citer sa source (Tableau 2).")


@dataclass(frozen=True)
class Correlation:
    """Une corrélation déclarée et justifiée entre deux composantes nommées (§22.3).

    Cas typique cité par le protocole : altitude de l'observateur et
    altitude de la base, quand les deux viennent du même modèle de
    terrain.
    """

    entre: "tuple[str, str]"
    coefficient: float
    justification: str

    def __post_init__(self):
        if not (-1.0 <= self.coefficient <= 1.0):
            raise UncertaintyError("Un coefficient de corrélation doit être dans [-1 ; 1].")
        if not self.justification.strip():
            raise UncertaintyError("Toute corrélation déclarée doit être justifiée (§22.3).")


def composer(
    composantes: Sequence[Composante], correlations: Sequence[Correlation] = ()
) -> float:
    """u_c = √(Σ u_i² + 2 ΣΣ r_ij·u_i·u_j) — loi de propagation du GUM (§22.3).

    Les composantes non citées dans `correlations` sont traitées comme
    indépendantes (composition en quadrature pure).
    """
    if not composantes:
        raise UncertaintyError("Au moins une composante est nécessaire pour composer une incertitude.")

    index = {c.nom: c for c in composantes}
    if len(index) != len(composantes):
        raise UncertaintyError("Deux composantes ne peuvent pas porter le même nom.")

    variance = sum(c.valeur**2 for c in composantes)
    for corr in correlations:
        nom_i, nom_j = corr.entre
        if nom_i not in index or nom_j not in index:
            raise UncertaintyError(
                f"Corrélation déclarée entre des composantes non fournies : {corr.entre}."
            )
        variance += 2.0 * corr.coefficient * index[nom_i].valeur * index[nom_j].valeur

    if variance < 0:
        # Mathématiquement possible seulement avec plusieurs corrélations
        # simultanées incohérentes entre elles (matrice de corrélation non
        # définie positive) : signale une déclaration à revoir, pas une
        # erreur d'arrondi à ignorer.
        raise UncertaintyError(
            "La composition donne une variance négative : les corrélations "
            "déclarées sont mutuellement incohérentes."
        )
    return math.sqrt(variance)


@dataclass(frozen=True)
class Incertitude:
    """Une incertitude composée, avec sa décomposition — jamais un chiffre nu (Tableau 2, §6.2).

    facteur_elargissement : k, tel que l'incertitude élargie U = k · u_c
    (§22). Rester à k = 1 tant qu'aucun facteur n'a été retenu et
    justifié ; ne jamais présumer k = 2 comme signifiant 95 % sans
    l'avoir établi pour la distribution en cause.
    """

    valeur_composee: float
    composantes: "tuple[Composante, ...]"
    correlations: "tuple[Correlation, ...]" = ()
    facteur_elargissement: float = 1.0

    def __post_init__(self):
        if self.facteur_elargissement <= 0:
            raise UncertaintyError("Le facteur d'élargissement doit être strictement positif.")

    @property
    def elargie(self) -> float:
        """U = k · u_c — l'incertitude élargie (§22)."""
        return self.valeur_composee * self.facteur_elargissement

    @classmethod
    def depuis_composantes(
        cls,
        composantes: Sequence[Composante],
        correlations: Sequence[Correlation] = (),
        facteur_elargissement: float = 1.0,
    ) -> "Incertitude":
        u_c = composer(composantes, correlations)
        return cls(u_c, tuple(composantes), tuple(correlations), facteur_elargissement)


# --- §23 : analyse de sensibilité ---


@dataclass(frozen=True)
class PlageParametre:
    """Un intervalle de paramètre à balayer, avec l'origine de ses bornes (§23.1).

    « L'intervalle retenu est celui que permettent les meilleures sources
    et les meilleurs instruments dont l'observateur disposait ; il n'est
    ni élargi par précaution, ni resserré par commodité, et son origine
    est citée. » — d'où le champ `source`, jamais optionnel.
    """

    nom: str
    minimum: float
    maximum: float
    source: str

    def __post_init__(self):
        if self.minimum > self.maximum:
            raise UncertaintyError(f"Plage invalide pour « {self.nom} » : minimum > maximum.")
        if not self.source.strip():
            raise UncertaintyError(f"L'origine de la plage de « {self.nom} » doit être citée (§23.1).")


@dataclass(frozen=True)
class EnveloppeSensibilite:
    """Le résultat d'un balayage de sensibilité (§23.1) — jamais une valeur centrale.

    combinaison_minimale / combinaison_maximale rapportent les paramètres
    qui produisent chaque borne : le §23.2 exige explicitement que « l'analyste
    rapporte la combinaison la plus défavorable à sa propre conclusion ».
    """

    minimum: float
    maximum: float
    combinaison_minimale: Mapping[str, float]
    combinaison_maximale: Mapping[str, float]
    methode: str  # "grille complète" ou "monte-carlo"
    n_evaluations: int
    germe: Optional[int] = None

    @property
    def largeur(self) -> float:
        return self.maximum - self.minimum

    def contient(self, valeur: float) -> bool:
        return self.minimum <= valeur <= self.maximum


def balayer_enveloppe(
    fonction: Callable[..., float],
    plages: Sequence[PlageParametre],
    pas_par_parametre: int = 5,
    max_grille: int = 100_000,
    germe: Optional[int] = None,
) -> EnveloppeSensibilite:
    """Balaie chaque paramètre dans sa plage et rapporte l'enveloppe des prédictions (§23.1).

    `fonction` est appelée en mots-clés, un argument par nom de plage
    (fonction(**{p.nom: valeur, ...})). Grille complète (pas régulier,
    bornes incluses) si le nombre de combinaisons ne dépasse pas
    `max_grille` ; au-delà, tirage aléatoire uniforme dont le germe doit
    être fourni et publié — jamais un intervalle élargi ou resserré à la
    main pour éviter le calcul.
    """
    if not plages:
        raise UncertaintyError("Au moins une plage de paramètre est nécessaire.")

    noms = [p.nom for p in plages]
    n_combinaisons_grille = pas_par_parametre ** len(plages)

    if n_combinaisons_grille <= max_grille:
        valeurs_par_param = []
        for p in plages:
            if pas_par_parametre <= 1 or p.minimum == p.maximum:
                valeurs_par_param.append([p.minimum])
            else:
                pas = (p.maximum - p.minimum) / (pas_par_parametre - 1)
                valeurs_par_param.append([p.minimum + i * pas for i in range(pas_par_parametre)])
        combinaisons = itertools.product(*valeurs_par_param)
        methode = "grille complète"
        n_prevu = 1
        for v in valeurs_par_param:
            n_prevu *= len(v)
    else:
        if germe is None:
            raise UncertaintyError(
                "Le balayage complet dépasserait max_grille "
                f"({n_combinaisons_grille} > {max_grille}) : un tirage "
                "Monte-Carlo est nécessaire, avec un germe publié (§23.1)."
            )
        rng = random.Random(germe)
        n_prevu = max_grille

        def _tirages():
            for _ in range(n_prevu):
                yield tuple(rng.uniform(p.minimum, p.maximum) for p in plages)

        combinaisons = _tirages()
        methode = "monte-carlo"

    minimum = math.inf
    maximum = -math.inf
    combi_min: Optional[Mapping[str, float]] = None
    combi_max: Optional[Mapping[str, float]] = None
    n_eval = 0

    for combo in combinaisons:
        params = dict(zip(noms, combo))
        valeur = fonction(**params)
        n_eval += 1
        if valeur < minimum:
            minimum = valeur
            combi_min = params
        if valeur > maximum:
            maximum = valeur
            combi_max = params

    return EnveloppeSensibilite(
        minimum=minimum,
        maximum=maximum,
        combinaison_minimale=combi_min or {},
        combinaison_maximale=combi_max or {},
        methode=methode,
        n_evaluations=n_eval,
        germe=germe if methode == "monte-carlo" else None,
    )


def effet_sensibilite(
    fonction: Callable[..., float], nominal: Mapping[str, float], parametre: str, delta: float
) -> float:
    """Différence finie centrée : [fonction(param+delta) − fonction(param−delta)] / 2.

    Reproduit la convention du Tableau 14 (§22.2) : pour un écart « ± δ »
    considéré sur un paramètre, l'effet rapporté est la demi-amplitude de
    la variation de la grandeur prédite autour du point nominal — vérifié
    ici contre les lignes h, D et k(±0,01) du tableau, à mieux de 0,1 %.

    Ne reproduit pas la ligne « coefficient k non mesuré, plage 0,10 à
    0,40 » du même tableau : cette ligne compare deux bornes larges et
    asymétriques autour du nominal (k = 0,13), pas un petit écart
    symétrique, et sa convention exacte n'est pas déductible du texte du
    protocole avec assez de certitude pour être affirmée testée ici.
    Utiliser balayer_enveloppe directement sur la plage complète pour ce
    cas, en rapportant le minimum et le maximum plutôt qu'un effet
    ponctuel.
    """
    if delta <= 0:
        raise UncertaintyError("delta doit être strictement positif.")
    if parametre not in nominal:
        raise UncertaintyError(f"« {parametre} » doit figurer dans le point nominal.")

    params_plus = dict(nominal)
    params_plus[parametre] = nominal[parametre] + delta
    params_moins = dict(nominal)
    params_moins[parametre] = nominal[parametre] - delta

    return (fonction(**params_plus) - fonction(**params_moins)) / 2.0


def modele_refute_par(enveloppe: EnveloppeSensibilite, valeur_observee: float) -> bool:
    """§23.2 : un modèle n'est réfuté que si l'observation tombe hors de l'enveloppe ENTIÈRE.

    Ne mêle pas ici l'incertitude de mesure sur `valeur_observee` : cette
    composition (Δ face à 5·u(f)) est la condition de discrimination du
    §28.2, portée par un futur module de décision qui utilisera cette
    fonction comme brique, pas qui la redéfinira.
    """
    return not enveloppe.contient(valeur_observee)
