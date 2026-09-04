"""
decision.py — verdict à trois valeurs (§28.3) et comparaison de vraisemblance
pénalisée (§27.2), plus tout ce que le §28.3 mêle et que models.py annonçait
laisser à un « futur module de décision » : validité d'image (§18), régimes
atmosphériques recherchés (§19.4), convergence des trois analystes (§19.5,
§25), recevabilité préalable du dossier (§28.1), et le dimensionnement
d'échantillon du §27.3.

Ce module consomme `ConditionDiscrimination` et `EnveloppeSensibilite`
(models.py, uncertainty.py) sans les redéfinir — exactement ce que
models.py annonçait dans son propre docstring. Il ne mesure rien : chaque
fonction ici applique une règle de lecture à des faits déjà établis
ailleurs (une enveloppe déjà balayée, une image déjà classée poste par
poste, des mesures d'analystes déjà recueillies).

Correspondance avec le texte du protocole :

  §18   → classer_validite_image (Tableau 11), majorer_incertitude_si_reserves
  §19.4 → RechercheRegime, un_regime_est_etabli — « jamais introduit après
          coup pour rendre compte d'un écart »
  §19.5, §25 → dispersion_analystes, convergence_analystes
  §26, §27.3 → taille_echantillon_minimale (Tableau 18)
  §27.2 → log_vraisemblance_gaussienne, critere_penalise, comparer_modeles
  §28.1 → evaluer_recevabilite
  §28.2 → consommé via ConditionDiscrimination (models.py), pas redéfini
  §28.3 → Verdict, ElementsVerdict, classer_verdict, DossierVerdict

Ce que ce module NE FAIT PAS : il ne mesure aucune image, ne recueille
aucune donnée atmosphérique, et ne calcule aucune vraisemblance à la place
de l'analyste — log_vraisemblance_gaussienne suppose des résidus gaussiens
indépendants, une hypothèse à vérifier au cas par cas (§27.1 : les
observations sont ajustées conjointement sur f(D), l'indépendance n'est
pas automatique — voir aussi §27.3 sur ce que « indépendant » exclut).
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import List, Mapping, Optional, Sequence, Tuple

from .models import ConditionDiscrimination, Modele
from .uncertainty import EnveloppeSensibilite

__all__ = [
    "DecisionError",
    "Colonne",
    "CategorieValiditeImage",
    "classer_validite_image",
    "majorer_incertitude_si_reserves",
    "SignatureRegime",
    "RechercheRegime",
    "un_regime_est_etabli",
    "dispersion_analystes",
    "convergence_analystes",
    "Z_ALPHA_BILATERAL_0999",
    "Z_BETA_PUISSANCE_95",
    "taille_echantillon_minimale",
    "CriterePenalisation",
    "log_vraisemblance_gaussienne",
    "critere_penalise",
    "ComparaisonModeles",
    "comparer_modeles",
    "comparer_deux_modeles",
    "Recevabilite",
    "evaluer_recevabilite",
    "ecart_a_enveloppe",
    "Verdict",
    "ResultatVerdict",
    "ElementsVerdict",
    "classer_verdict",
    "DossierVerdict",
    "evaluer_dossier",
]


class DecisionError(ValueError):
    """Domaine invalide, grille de validation incomplète, ou entrée de décision incohérente."""


# --- §18 : validation des images (Tableau 11) ---


class Colonne(int, Enum):
    """La colonne du Tableau 11 dans laquelle un poste de la grille a été classé —
    par un opérateur qui ignore la prédiction (§18), jamais déduite ici."""

    VALIDE = 1
    RESERVES = 2
    NON_VALIDE = 3


class CategorieValiditeImage(str, Enum):
    VALIDE = "valide"
    VALIDE_AVEC_RESERVES = "valide avec réserves"
    INVALIDE = "invalide"


def classer_validite_image(postes: Mapping[str, Colonne]) -> CategorieValiditeImage:
    """Tableau 11 (§18) : valide si tous les postes sont en colonne 1 ; valide avec
    réserves si aucun n'est en colonne 3 ; non valide dès qu'un poste est en
    colonne 3.

    Ne juge pas les critères eux-mêmes (mise au point, flou de bougé,
    turbulence, exposition, contraste, artefacts, distorsion, occultation
    parasite...) : ce module ne mesure pas d'image. Il applique seulement la
    règle qui, à partir d'un classement déjà fait poste par poste, produit
    la catégorie — le classement lui-même doit être fait avant toute mesure
    de la fraction visible, par une personne qui ignore la prédiction et la
    distance (§18, encadré « contre le tri d'après le résultat »).
    """
    if not postes:
        raise DecisionError("La grille de validation (Tableau 11) exige au moins un poste classé.")
    colonnes = list(postes.values())
    if any(c == Colonne.NON_VALIDE for c in colonnes):
        return CategorieValiditeImage.INVALIDE
    if all(c == Colonne.VALIDE for c in colonnes):
        return CategorieValiditeImage.VALIDE
    return CategorieValiditeImage.VALIDE_AVEC_RESERVES


def majorer_incertitude_si_reserves(
    u_mesure: float, facteur_majoration: float, categorie: CategorieValiditeImage
) -> float:
    """« Une image valide avec réserves entre dans l'analyse avec une incertitude de
    mesure majorée d'un facteur déclaré d'avance. » (§18) Une image invalide n'a
    rien à majorer : elle est exclue, jamais mesurée avec une incertitude plus
    large — d'où l'exception plutôt qu'un facteur silencieusement appliqué.
    """
    if u_mesure < 0:
        raise DecisionError("u_mesure ne peut pas être négative.")
    if categorie == CategorieValiditeImage.INVALIDE:
        raise DecisionError("Une image invalide est exclue de l'analyse — aucune incertitude à majorer.")
    if categorie == CategorieValiditeImage.VALIDE:
        return u_mesure
    if facteur_majoration < 1.0:
        raise DecisionError("Le facteur de majoration doit être déclaré d'avance et être ≥ 1.")
    return u_mesure * facteur_majoration


# --- §19.4 : régimes atmosphériques à rechercher ---


class SignatureRegime(str, Enum):
    MIRAGE_INFERIEUR = "mirage_inferieur"
    MIRAGE_SUPERIEUR = "mirage_superieur"
    LOOMING = "looming"
    CONDUIT_OPTIQUE = "conduit_optique"
    DEFORMATION_VERTICALE = "deformation_verticale"


@dataclass(frozen=True)
class RechercheRegime:
    """§19.4 : « un régime ne peut être invoqué que s'il a été recherché avant la
    comparaison [du §28] et s'il est établi par des signatures relevées dans les
    images et par les données atmosphériques du §21. Il n'est jamais introduit
    après coup pour rendre compte d'un écart, dans un sens comme dans l'autre. »

    Les trois conditions sont sur un pied d'égalité : `etabli` n'est vrai que si
    les trois le sont, y compris `recherchee_avant_comparaison` — un régime dont
    la signature est repérée après avoir vu l'écart n'est pas établi au sens du
    protocole, quelle que soit la qualité de la signature elle-même.
    """

    signature: SignatureRegime
    recherchee_avant_comparaison: bool
    signature_relevee_sur_images: bool
    donnees_atmospheriques_corroborantes: bool  # au sens du §21 (voir atmosphere.py)

    @property
    def etabli(self) -> bool:
        return (
            self.recherchee_avant_comparaison
            and self.signature_relevee_sur_images
            and self.donnees_atmospheriques_corroborantes
        )


def un_regime_est_etabli(recherches: Sequence[RechercheRegime]) -> bool:
    """True si au moins un régime recherché est établi au sens de RechercheRegime.etabli.

    Une séquence vide (aucune recherche menée) donne False : l'absence de
    recherche n'établit rien, elle ne dit rien non plus sur l'absence de régime
    — ce module ne présume jamais qu'une non-recherche vaut négation.
    """
    return any(r.etabli for r in recherches)


# --- §19.5, §25 : convergence entre analystes ---


def dispersion_analystes(mesures: Sequence[float]) -> float:
    """Écart-type expérimental de mesures indépendantes (§19.5 : « la dispersion
    entre analystes est reportée comme composante d'incertitude de type A »).

    Le protocole ne précise pas la statistique exacte au-delà de « dispersion » ;
    l'écart-type expérimental est le choix usuel pour une composante de type A
    au sens du JCGM/GUM (§22, voir uncertainty.TypeIncertitude.A) — un choix
    documenté ici, pas une définition du protocole lui-même.
    """
    if len(mesures) < 2:
        raise DecisionError("Au moins deux mesures indépendantes sont nécessaires pour une dispersion.")
    moyenne = sum(mesures) / len(mesures)
    variance = sum((m - moyenne) ** 2 for m in mesures) / (len(mesures) - 1)
    return math.sqrt(variance)


def convergence_analystes(mesures: Sequence[float], resolution_effective: float) -> bool:
    """§19.5 : « Si [la dispersion entre analystes] excède la résolution effective
    du §20, le dossier revient en 19.3 : le bord mesuré est ambigu. » — pas de
    convergence dans ce cas. §25 exige au moins trois analyses indépendantes ;
    ce module le vérifie plutôt que de le supposer.
    """
    if len(mesures) < 3:
        raise DecisionError("§25 exige au moins trois analyses indépendantes pour statuer sur la convergence.")
    if resolution_effective <= 0:
        raise DecisionError("La résolution effective (§20) doit être strictement positive.")
    return dispersion_analystes(mesures) <= resolution_effective


# --- §27.3 : dimensionnement d'échantillon ---

Z_ALPHA_BILATERAL_0999 = 3.2905  # z_(1-α/2), α = 0,001 bilatéral
Z_BETA_PUISSANCE_95 = 1.6449  # z_(1-β), puissance 95 %


def taille_echantillon_minimale(sigma: float, delta: float) -> float:
    """n ≥ (z_(1-α/2) + z_(1-β))² · (σ/Δ)² (§27.3) — un dimensionnement, pas
    l'analyse elle-même. Suppose des observations indépendantes et un bruit de
    même écart-type ; deux vues du même jour, depuis le même site, sur la même
    cible, ne sont PAS deux observations indépendantes au sens de cette formule
    (§27.3 : le décompte porte sur les configurations distinctes — site, cible,
    date, conditions).
    """
    if sigma <= 0 or delta <= 0:
        raise DecisionError("sigma et delta doivent être strictement positifs.")
    facteur = (Z_ALPHA_BILATERAL_0999 + Z_BETA_PUISSANCE_95) ** 2
    return facteur * (sigma / delta) ** 2


# --- §27.2 : comparaison de modèles par vraisemblance pénalisée ---


class CriterePenalisation(str, Enum):
    AIC = "AIC"
    BIC = "BIC"


def log_vraisemblance_gaussienne(residus: Sequence[float], sigmas: Sequence[float]) -> float:
    """Log-vraisemblance jointe d'observations gaussiennes indépendantes, un sigma
    par observation (§27.1 : « les observations d'une campagne sont ajustées
    conjointement sur la courbe f(D), et non comparées une à une »).

    Suppose des résidus gaussiens et indépendants — une hypothèse à vérifier,
    pas une garantie de ce module (voir §27.3 sur ce que « indépendant » exclut).
    """
    if len(residus) != len(sigmas):
        raise DecisionError("residus et sigmas doivent avoir la même longueur.")
    if len(residus) == 0:
        raise DecisionError("Au moins une observation est nécessaire pour une vraisemblance.")
    if any(s <= 0 for s in sigmas):
        raise DecisionError("Tous les sigmas doivent être strictement positifs.")
    return sum(
        -0.5 * ((r / s) ** 2 + math.log(2 * math.pi * s**2)) for r, s in zip(residus, sigmas)
    )


def critere_penalise(
    log_vraisemblance: float, nombre_parametres: int, n_observations: int, critere: CriterePenalisation
) -> float:
    """AIC = 2k − 2·ln L ; BIC = k·ln(n) − 2·ln L (§27.2 : « les modèles sont
    comparés par leur vraisemblance, pénalisée du nombre de paramètres libres
    déclarés au §26 »). Dans les deux cas, le modèle PRÉFÉRÉ est celui dont le
    critère est le plus bas — jamais le plus haut.
    """
    if nombre_parametres < 0:
        raise DecisionError("Le nombre de paramètres libres ne peut pas être négatif.")
    if critere == CriterePenalisation.AIC:
        return 2 * nombre_parametres - 2 * log_vraisemblance
    if critere == CriterePenalisation.BIC:
        if n_observations <= 0:
            raise DecisionError("Le BIC exige au moins une observation.")
        return nombre_parametres * math.log(n_observations) - 2 * log_vraisemblance
    raise DecisionError(f"Critère de pénalisation non reconnu : {critere}")


@dataclass(frozen=True)
class ComparaisonModeles:
    """§27.2 : « aucun modèle ne reçoit le statut d'hypothèse nulle privilégiée :
    les deux sont traités symétriquement. » Les deux modèles sont ici nommés,
    jamais rangés en « nul » et « alternatif » — `modele_favorise` se déduit des
    deux critères, il n'est jamais fixé d'avance.
    """

    nom_a: str
    critere_a: float
    nom_b: str
    critere_b: float
    critere: CriterePenalisation

    @property
    def modele_favorise(self) -> Optional[str]:
        """Le nom du modèle au critère le plus bas, ou None en cas d'égalité stricte."""
        if self.critere_a < self.critere_b:
            return self.nom_a
        if self.critere_b < self.critere_a:
            return self.nom_b
        return None

    @property
    def ecart(self) -> float:
        return abs(self.critere_a - self.critere_b)


def comparer_modeles(
    nom_a: str,
    log_vraisemblance_a: float,
    parametres_a: int,
    nom_b: str,
    log_vraisemblance_b: float,
    parametres_b: int,
    n_observations: int,
    critere: CriterePenalisation = CriterePenalisation.AIC,
) -> ComparaisonModeles:
    """Compare deux modèles par critère pénalisé (§27.2). Symétrique par
    construction : échanger (nom_a, ...) et (nom_b, ...) échange exactement
    `modele_favorise`, rien d'autre ne dépend de l'ordre des arguments.
    """
    critere_a = critere_penalise(log_vraisemblance_a, parametres_a, n_observations, critere)
    critere_b = critere_penalise(log_vraisemblance_b, parametres_b, n_observations, critere)
    return ComparaisonModeles(nom_a=nom_a, critere_a=critere_a, nom_b=nom_b, critere_b=critere_b, critere=critere)


def comparer_deux_modeles(
    modele_a: Modele,
    log_vraisemblance_a: float,
    modele_b: Modele,
    log_vraisemblance_b: float,
    n_observations: int,
    critere: CriterePenalisation = CriterePenalisation.AIC,
) -> ComparaisonModeles:
    """Comme comparer_modeles, mais lit le nombre de paramètres libres directement
    sur les modèles (Modele.nombre_parametres_libres, models.py) plutôt que de
    le faire redéclarer à l'appelant — pour que le modèle P (§29.3, aucun
    paramètre libre) et le modèle S (k, un paramètre) portent chacun leur propre
    compte sans risque de désaccord avec models.py.
    """
    return comparer_modeles(
        modele_a.nom,
        log_vraisemblance_a,
        modele_a.nombre_parametres_libres,
        modele_b.nom,
        log_vraisemblance_b,
        modele_b.nombre_parametres_libres,
        n_observations,
        critere,
    )


# --- §28.1 : filtre préalable de recevabilité ---


@dataclass(frozen=True)
class Recevabilite:
    """§28.1 : « la recevabilité est un filtre, non une conclusion. [...] Un
    dossier irrecevable n'est ni favorable ni défavorable : il n'entre pas dans
    l'analyse, et son exclusion est publiée. » `motifs_exclusion` est donc
    toujours rempli quand `recevable` est faux — jamais une exclusion muette.
    """

    recevable: bool
    motifs_exclusion: Tuple[str, ...]


def evaluer_recevabilite(
    pieces_du_dossier_fournies: bool,
    controles_du_tableau_17_passes: bool,
    validite_image: CategorieValiditeImage,
    toute_occultation_identifiee_et_attribuee: bool,
) -> Recevabilite:
    """§28.1 : recevable si et seulement si les pièces du §33 sont fournies, les
    contrôles du §24 (Tableau 17) sont passés, l'image est valide ou valide
    avec réserves (§18), et toute occultation visible est identifiée et
    attribuée. Une image invalide exclut le dossier ; valide avec réserves
    ne l'exclut pas (voir majorer_incertitude_si_reserves pour sa conséquence
    sur l'incertitude de mesure).
    """
    motifs: List[str] = []
    if not pieces_du_dossier_fournies:
        motifs.append("pièces du dossier (§33) incomplètes")
    if not controles_du_tableau_17_passes:
        motifs.append("contrôles expérimentaux du §24 (Tableau 17) non passés")
    if validite_image == CategorieValiditeImage.INVALIDE:
        motifs.append("image invalide au sens du §18")
    if not toute_occultation_identifiee_et_attribuee:
        motifs.append("occultation visible non identifiée ou non attribuée")
    return Recevabilite(recevable=not motifs, motifs_exclusion=tuple(motifs))


# --- §28.3 : les trois catégories ---


def ecart_a_enveloppe(enveloppe: EnveloppeSensibilite, valeur_observee: float) -> float:
    """Distance de `valeur_observee` à l'enveloppe de prédiction (§23) : 0 si elle
    y tombe, sinon la distance au bord le plus proche. Jamais un écart à un
    point nominal unique — le §23 rapporte une enveloppe, pas une valeur
    centrale, et c'est elle que ce module compare à l'observation.
    """
    if enveloppe.contient(valeur_observee):
        return 0.0
    if valeur_observee < enveloppe.minimum:
        return enveloppe.minimum - valeur_observee
    return valeur_observee - enveloppe.maximum


class Verdict(str, Enum):
    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    INDETERMINE = "indéterminé"


@dataclass(frozen=True)
class ResultatVerdict:
    """Le verdict et ses motifs — toujours au moins un motif, compatible ou pas
    (§28.3, encadré « symétrie de traitement » : « une observation indéterminée
    [...] est publiée avec le motif exact de l'indétermination »)."""

    verdict: Verdict
    motifs: Tuple[str, ...]


@dataclass(frozen=True)
class ElementsVerdict:
    """Tout ce que le §28.3 mêle pour trancher, pour UN modèle donné. Chaque champ
    correspond à une clause du texte ; rien n'est calculé ici, tout est reçu
    d'un module qui le mesure ou le calcule réellement (uncertainty.py,
    models.py, ou l'analyste qui remplit la fiche du §33).
    """

    fraction_observee: float
    enveloppe_prediction: EnveloppeSensibilite  # §23, pour ce modèle
    u_mesure: float  # incertitude de mesure composée sur f_obs (§22)
    seuil_refutation: float  # déposé au §26 avant l'analyse
    discrimination: ConditionDiscrimination  # §28.2 — consommé, jamais redéfini
    regimes_recherches: Tuple[RechercheRegime, ...]  # §19.4
    toutes_occultations_attribuees: bool  # §18, poste « occultation parasite »
    caracteristique_resolue: bool  # §19.3
    bord_mesurable: bool  # §19.3
    donnees_atmospheriques_suffisantes: bool  # pour borner k, §21
    mesures_analystes: Tuple[float, ...]  # §19.5, §25 — au moins trois
    resolution_effective: float  # §20

    def __post_init__(self):
        if self.u_mesure < 0:
            raise DecisionError("u_mesure ne peut pas être négative.")
        if self.seuil_refutation <= 0:
            raise DecisionError("Le seuil de réfutation doit être strictement positif.")


def classer_verdict(elements: ElementsVerdict) -> ResultatVerdict:
    """Applique le §28.3 : Compatible / Incompatible / Indéterminé.

    Les motifs d'indétermination sont cumulés, pas arrêtés au premier trouvé
    (§28.3 : « une observation indéterminée [...] est publiée avec le motif
    exact » — au pluriel s'il y en a plusieurs) : un dossier peut être à la
    fois hors résolution ET en régime établi, et le rapport doit le dire.
    """
    motifs_indetermine: List[str] = []

    if not elements.discrimination.satisfaite:
        motifs_indetermine.append(
            "condition de discrimination du §28.2 non satisfaite — indéterminé avant même la mesure de f"
        )
    if not elements.donnees_atmospheriques_suffisantes:
        motifs_indetermine.append("données atmosphériques insuffisantes pour borner k")
    if not elements.caracteristique_resolue:
        motifs_indetermine.append("caractéristique non résolue")
    if not elements.bord_mesurable:
        motifs_indetermine.append("bord non mesurable (§19.3 : dégradé, pas une discontinuité résolue)")
    if not convergence_analystes(elements.mesures_analystes, elements.resolution_effective):
        motifs_indetermine.append("divergence entre analystes (§19.5, §25)")
    if un_regime_est_etabli(elements.regimes_recherches):
        motifs_indetermine.append("régime atmosphérique établi (§19.4)")

    if motifs_indetermine:
        return ResultatVerdict(Verdict.INDETERMINE, tuple(motifs_indetermine))

    ecart = ecart_a_enveloppe(elements.enveloppe_prediction, elements.fraction_observee)

    if ecart <= elements.u_mesure and ecart < elements.seuil_refutation:
        return ResultatVerdict(
            Verdict.COMPATIBLE,
            (
                f"f observée dans l'enveloppe de prédiction à u_mesure={elements.u_mesure:g} près "
                f"(écart à l'enveloppe {ecart:g}), sous le seuil de réfutation {elements.seuil_refutation:g}",
            ),
        )

    if ecart >= elements.seuil_refutation and elements.toutes_occultations_attribuees:
        return ResultatVerdict(
            Verdict.INCOMPATIBLE,
            (
                f"écart à l'enveloppe entière ({ecart:g}) atteint le seuil de réfutation "
                f"({elements.seuil_refutation:g}) ; aucun régime établi, occultations attribuées, "
                "analyses convergentes",
            ),
        )

    motifs_reste: List[str] = []
    if ecart > elements.u_mesure:
        motifs_reste.append(
            f"hors de l'enveloppe combinée (écart {ecart:g} > u_mesure {elements.u_mesure:g}), "
            f"sans franchir le seuil de réfutation ({elements.seuil_refutation:g})"
        )
    if not elements.toutes_occultations_attribuees:
        motifs_reste.append("occultation visible non attribuée")
    if not motifs_reste:
        motifs_reste.append("cas non tranché par les critères du §28.3")
    return ResultatVerdict(Verdict.INDETERMINE, tuple(motifs_reste))


@dataclass(frozen=True)
class DossierVerdict:
    """Le verdict pour les deux modèles en présence, sur le même dossier (§28.3 :
    « un même dossier peut être compatible avec un modèle et incompatible avec
    l'autre : c'est le cas recherché. Il peut aussi être compatible avec les
    deux, ou incompatible avec les deux »)."""

    nom_a: str
    resultat_a: ResultatVerdict
    nom_b: str
    resultat_b: ResultatVerdict

    @property
    def cas_recherche(self) -> bool:
        """Compatible avec l'un, incompatible avec l'autre — le cas que le §28.3 dit recherché."""
        return {self.resultat_a.verdict, self.resultat_b.verdict} == {Verdict.COMPATIBLE, Verdict.INCOMPATIBLE}

    @property
    def alerte_dispositif(self) -> bool:
        """Compatible avec les deux modèles, ou incompatible avec les deux : publié
        tel quel, la seconde situation « signalant qu'un élément du dispositif
        est mal compris » (§28.3)."""
        return (
            self.resultat_a.verdict == self.resultat_b.verdict
            and self.resultat_a.verdict != Verdict.INDETERMINE
        )


def evaluer_dossier(
    nom_a: str, elements_a: ElementsVerdict, nom_b: str, elements_b: ElementsVerdict
) -> DossierVerdict:
    """Applique classer_verdict aux deux modèles, avec un traitement identique
    (§28.3, encadré « symétrie de traitement ») : mêmes règles, appelées de la
    même façon, pour chacun des deux noms."""
    return DossierVerdict(
        nom_a=nom_a,
        resultat_a=classer_verdict(elements_a),
        nom_b=nom_b,
        resultat_b=classer_verdict(elements_b),
    )
