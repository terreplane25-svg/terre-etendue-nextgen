"""
atmosphere.py — Données atmosphériques et leur classe de fiabilité (§21).

La grandeur qui gouverne la prédiction est le gradient vertical de
température DANS LA COUCHE OÙ PASSE LE RAYON RASANT, pas une
température moyenne (§21.1, §11.5) : une couche basse de quelques
dizaines de mètres peut à elle seule tripler le coefficient effectif.
Ce module fournit :

  - `ClasseDonnee` (A à E, Tableau 13) : la classe dit COMMENT une
    valeur a été obtenue, jamais si elle est juste. Elle accompagne la
    valeur partout où elle apparaît, y compris dans la conclusion.
  - `DonneeAtmospherique` : une lecture ponctuelle (température,
    pression, humidité, température de surface), avec les contraintes
    de distance et d'écart temporel que le Tableau 13 impose aux
    classes B et C.
  - `ProfilVertical` : un profil résolu en altitude, avec la
    vérification de résolution du §21.1 et le calcul du gradient dans
    la couche basse qu'exige refraction.py (§11.5).
  - `moyenne_ponderee_en_hauteur` : la moyenne piège que le §11.5
    interdit explicitement — fournie pour la démasquer, jamais pour
    mesurer.
  - `intervalle_k_faute_de_donnee_resolue` : la réponse du §21.3 à
    l'insuffisance de données — reporter la plage entière que les
    conditions de surface autorisent, jamais un choix prudent ponctuel.
"""

import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Sequence, Tuple

from .refraction import HypotheseRefraction, RegimeRefraction

__all__ = [
    "AtmosphereError",
    "ClasseDonnee",
    "definition",
    "statut_au_rapport",
    "DonneeAtmospherique",
    "resolution_par_mesure_directe",
    "indique_inversion_probable",
    "PointProfil",
    "ProfilVertical",
    "verifier_resolution",
    "CoucheK",
    "moyenne_ponderee_en_hauteur",
    "BORNES_REGIME",
    "intervalle_k_faute_de_donnee_resolue",
]


class AtmosphereError(ValueError):
    """Domaine invalide, ou donnée atmosphérique déclarée hors des limites de sa classe (§21)."""


class ClasseDonnee(str, Enum):
    """Tableau 13 (§21.2) : la classe dit COMMENT la valeur a été obtenue, pas si elle est juste."""

    A = "A"  # mesure directe sur site
    B = "B"  # sondage aérologique
    C = "C"  # station météorologique officielle
    D = "D"  # sortie de modèle ou réanalyse
    E = "E"  # climatologie ou estimation


_DEFINITIONS = {
    ClasseDonnee.A: "Instrument étalonné relevé par l'opérateur au point de vue, pendant l'observation.",
    ClasseDonnee.B: (
        "Profil vertical mesuré par ballon, à moins de 100 km et 3 h ; "
        "l'écart est consigné et reporté dans l'incertitude."
    ),
    ClasseDonnee.C: (
        "Observation horodatée d'un réseau reconnu, à moins de 30 km et 1 h ; "
        "ne donne que des valeurs de surface."
    ),
    ClasseDonnee.D: "Valeur calculée sur une maille, jamais observée au point ; résolution verticale insuffisante près de la surface.",
    ClasseDonnee.E: "Moyenne saisonnière, ou valeur choisie par l'analyste faute de mieux, y compris le coefficient dit standard.",
}

_STATUTS = {
    ClasseDonnee.A: "mesure",
    ClasseDonnee.B: "mesure déportée",
    ClasseDonnee.C: "mesure de surface",
    ClasseDonnee.D: "valeur calculée",
    ClasseDonnee.E: "déclarative",
}

_LIMITE_DISTANCE_KM = {ClasseDonnee.B: 100.0, ClasseDonnee.C: 30.0}
_LIMITE_ECART_H = {ClasseDonnee.B: 3.0, ClasseDonnee.C: 1.0}


def definition(classe: ClasseDonnee) -> str:
    """La définition de la classe, telle que le Tableau 13 la donne."""
    return _DEFINITIONS[classe]


def statut_au_rapport(classe: ClasseDonnee) -> str:
    """Le statut sous lequel une donnée de cette classe doit apparaître au rapport (Tableau 13)."""
    return _STATUTS[classe]


def resolution_par_mesure_directe(classes: Sequence[ClasseDonnee]) -> bool:
    """True si au moins une donnée de classe A ou B figure parmi `classes` (§21.3)."""
    return any(c in (ClasseDonnee.A, ClasseDonnee.B) for c in classes)


def indique_inversion_probable(temperature_air_K: float, temperature_mer_K: float) -> bool:
    """§21.1 : l'écart air-mer est « le meilleur indicateur disponible d'une inversion de surface ».

    Air plus chaud que la mer : stratification stable, favorable à une
    inversion de surface (k élevé). Air plus froid ou égal : mélange,
    pas d'indication d'inversion. Un indicateur, pas une mesure de k —
    à ne jamais substituer à un profil résolu (§11.5, §11.7).
    """
    if temperature_air_K <= 0 or temperature_mer_K <= 0:
        raise AtmosphereError("Les températures doivent être en kelvins, strictement positives.")
    return temperature_air_K > temperature_mer_K


@dataclass(frozen=True)
class DonneeAtmospherique:
    """Une lecture ponctuelle, avec sa classe et — pour B et C — les bornes du Tableau 13.

    `distance_au_site_km` et `ecart_temporel_h` sont obligatoires pour
    les classes B et C, et vérifiés contre les limites du Tableau 13 dès
    la construction : une donnée hors limites n'existe pas comme objet
    de cette classe, elle doit être déclarée d'une classe inférieure.
    """

    grandeur: str
    valeur: float
    unite: str
    classe: ClasseDonnee
    source: str
    horodatage: datetime
    distance_au_site_km: Optional[float] = None
    ecart_temporel_h: Optional[float] = None

    def __post_init__(self):
        if not self.grandeur.strip():
            raise AtmosphereError("La grandeur mesurée doit être nommée.")
        if not self.source.strip():
            raise AtmosphereError(f"La donnée « {self.grandeur} » doit citer sa source (Tableau 2).")

        if self.classe in _LIMITE_DISTANCE_KM:
            if self.distance_au_site_km is None or self.ecart_temporel_h is None:
                raise AtmosphereError(
                    f"Une donnée de classe {self.classe.value} doit préciser sa distance "
                    "au site et son écart temporel (Tableau 13)."
                )
            limite_distance = _LIMITE_DISTANCE_KM[self.classe]
            limite_ecart = _LIMITE_ECART_H[self.classe]
            if self.distance_au_site_km > limite_distance or self.ecart_temporel_h > limite_ecart:
                raise AtmosphereError(
                    f"Classe {self.classe.value} exige moins de {limite_distance:g} km et "
                    f"{limite_ecart:g} h d'écart (Tableau 13) ; reçu "
                    f"{self.distance_au_site_km:g} km, {self.ecart_temporel_h:g} h."
                )


# --- Profil vertical résolu (§21.1, §11.5) ---


@dataclass(frozen=True)
class PointProfil:
    """Une lecture de température à une altitude donnée au-dessus de la surface."""

    altitude_m: float
    temperature_K: float

    def __post_init__(self):
        if self.altitude_m < 0:
            raise AtmosphereError("L'altitude d'un point de profil ne peut pas être négative.")
        if self.temperature_K <= 0:
            raise AtmosphereError("La température doit être en kelvins, strictement positive.")


@dataclass(frozen=True)
class ProfilVertical:
    """Un profil vertical résolu, trié par altitude croissante, sans doublon (§21.1).

    La résolution requise n'est PAS vérifiée à la construction — un
    profil incomplet reste un objet valide, décrivant ce qu'on a
    réellement mesuré. C'est `verifier_resolution` qui applique le
    critère du §21.1, séparément, pour qu'un profil insuffisant puisse
    être inspecté plutôt que rejeté silencieusement.
    """

    points: Tuple[PointProfil, ...]
    classe: ClasseDonnee
    source: str

    def __post_init__(self):
        if len(self.points) < 2:
            raise AtmosphereError("Un profil vertical doit comporter au moins deux points.")
        if not self.source.strip():
            raise AtmosphereError("Un profil vertical doit citer sa source (Tableau 2).")
        altitudes = [p.altitude_m for p in self.points]
        if altitudes != sorted(altitudes):
            raise AtmosphereError("Les points d'un profil doivent être triés par altitude croissante.")
        if len(set(altitudes)) != len(altitudes):
            raise AtmosphereError("Deux points d'un profil ne peuvent pas partager la même altitude.")

    def _temperature_a(self, altitude: float) -> float:
        """Température interpolée linéairement entre les deux points encadrants."""
        if altitude < self.points[0].altitude_m or altitude > self.points[-1].altitude_m:
            raise AtmosphereError(
                f"Altitude {altitude:g} m hors du profil "
                f"[{self.points[0].altitude_m:g} ; {self.points[-1].altitude_m:g}] m."
            )
        for a, b in zip(self.points, self.points[1:]):
            if a.altitude_m <= altitude <= b.altitude_m:
                if b.altitude_m == a.altitude_m:
                    return a.temperature_K
                t = (altitude - a.altitude_m) / (b.altitude_m - a.altitude_m)
                return a.temperature_K + t * (b.temperature_K - a.temperature_K)
        raise AtmosphereError("Altitude non trouvée dans le profil (état interne incohérent).")

    def gradient_moyen_K_par_m(self, z_min: float, z_max: float) -> float:
        """dT/dh moyen (K/m) entre deux altitudes du profil, par interpolation linéaire."""
        if z_max <= z_min:
            raise AtmosphereError("z_max doit être strictement supérieur à z_min.")
        return (self._temperature_a(z_max) - self._temperature_a(z_min)) / (z_max - z_min)

    def gradient_couche_basse_K_par_km(self, epaisseur_m: float = 60.0) -> float:
        """dT/dh moyen (K/km) dans la couche basse, prêt pour refraction.k_depuis_gradient.

        `epaisseur_m` par défaut reprend l'exemple à deux couches du §11.5
        (couche basse de 60 m). La couche basse est celle qui pèse le plus
        sur le rayon rasant (§11.5) — jamais la moyenne du profil entier.
        """
        return self.gradient_moyen_K_par_m(0.0, epaisseur_m) * 1000.0

    @property
    def altitude_max(self) -> float:
        return self.points[-1].altitude_m


def verifier_resolution(profil: ProfilVertical, altitude_observateur: float) -> None:
    """Applique le critère de résolution du §21.1 : lève AtmosphereError sinon.

    Interprétation retenue, littérale : un point tous les 10 m au plus
    tant que l'altitude de départ du segment est sous 100 m, puis un
    point tous les 100 m au plus jusqu'à l'altitude de l'observateur ;
    le profil doit démarrer au plus à 10 m de la surface et atteindre
    cette altitude.
    """
    if profil.points[0].altitude_m > 10.0:
        raise AtmosphereError(
            f"Le profil doit débuter à 10 m au plus de la surface (§21.1) ; "
            f"premier point à {profil.points[0].altitude_m:g} m."
        )
    if profil.altitude_max < altitude_observateur:
        raise AtmosphereError(
            f"Le profil doit atteindre l'altitude de l'observateur ({altitude_observateur:g} m) ; "
            f"il s'arrête à {profil.altitude_max:g} m (§21.1)."
        )
    for a, b in zip(profil.points, profil.points[1:]):
        limite = 10.0 if a.altitude_m < 100.0 else 100.0
        ecart = b.altitude_m - a.altitude_m
        if ecart > limite:
            raise AtmosphereError(
                f"Résolution insuffisante entre {a.altitude_m:g} m et {b.altitude_m:g} m "
                f"(écart {ecart:g} m > {limite:g} m requis à cette altitude, §21.1)."
            )


# --- La moyenne piège du §11.5 — pour la démasquer, jamais pour mesurer ---


@dataclass(frozen=True)
class CoucheK:
    """Une couche d'épaisseur donnée, à coefficient de réfraction constant."""

    epaisseur_m: float
    k: float

    def __post_init__(self):
        if self.epaisseur_m <= 0:
            raise AtmosphereError("L'épaisseur d'une couche doit être strictement positive.")


def moyenne_ponderee_en_hauteur(couches: Sequence[CoucheK]) -> float:
    """Moyenne de k pondérée par l'épaisseur des couches — PIÈGE dénoncé par le §11.5.

    Sur l'exemple du protocole (couche de 60 m à k = 0,80, puis k = 0,13
    jusqu'à 800 m), cette moyenne vaut 0,180 — mais le comportement réel
    du rayon rasant, qui passe l'essentiel de son trajet à faible pente
    près de la surface, équivaut à un k homogène de 0,563 (obtenu par
    traçage de rayon, §11.6, non implémenté dans refraction.py). Cette
    fonction existe pour rendre l'écart démontrable, jamais pour établir
    un k de mesure : le §11.5 l'interdit explicitement.
    """
    if not couches:
        raise AtmosphereError("Au moins une couche est nécessaire.")
    epaisseur_totale = sum(c.epaisseur_m for c in couches)
    return sum(c.epaisseur_m * c.k for c in couches) / epaisseur_totale


# --- §21.3 : insuffisance de données ---

# Bornes du Tableau 8 (§11.3), reprises telles quelles. Le régime CONDUIT est délibérément
# absent : il exige un gradient soutenu établi (§11.4), jamais une hypothèse « faute de mieux ».
BORNES_REGIME = {
    RegimeRefraction.AUCUNE: (0.0, 0.0),
    RegimeRefraction.STANDARD: (0.13, 0.17),
    RegimeRefraction.FORTE: (0.20, 0.40),
    RegimeRefraction.TRES_FORTE: (0.40, 0.80),
    RegimeRefraction.INVERSION: (0.80, 1.0),
}


def intervalle_k_faute_de_donnee_resolue(
    regimes_plausibles: Sequence[RegimeRefraction], justification: str
) -> HypotheseRefraction:
    """§21.3 : en l'absence de donnée de classe A ou B, borne k aux régimes que les
    conditions de surface autorisent — jamais élargi par précaution au-delà de ces
    régimes, jamais resserré par commodité à l'un d'eux sans justification.

    `regimes_plausibles` doit être établi depuis ce qui EST connu (classe C, D ou E :
    par exemple `indique_inversion_probable` sur un écart air-mer de classe C exclut
    les régimes instables) — pas choisi pour obtenir un résultat. Le régime CONDUIT
    ne peut pas être demandé ici : il exige une donnée établie (§11.4), pas une
    hypothèse par défaut.
    """
    if not regimes_plausibles:
        raise AtmosphereError("Au moins un régime plausible doit être fourni (§21.3).")
    if RegimeRefraction.CONDUIT in regimes_plausibles:
        raise AtmosphereError(
            "Le régime de conduit optique exige un gradient soutenu établi (§11.4) ; "
            "il ne peut pas être posé « faute de mieux »."
        )
    bornes = [BORNES_REGIME[r] for r in regimes_plausibles]
    k_min = min(b[0] for b in bornes)
    k_max = max(b[1] for b in bornes)
    return HypotheseRefraction(k_min=k_min, k_max=k_max, justification=justification)
