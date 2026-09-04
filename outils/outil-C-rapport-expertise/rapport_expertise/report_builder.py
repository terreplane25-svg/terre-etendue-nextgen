"""
report_builder.py — la fiche standard d'observation du §33.

Neuf blocs, dans l'ordre du protocole. Le texte du §33 est explicite dès sa
première phrase : « un dossier incomplet est indéterminé, pas défavorable. Un
champ sans valeur porte la mention indisponible ; il n'est jamais laissé en
blanc ni rempli d'une valeur plausible. » C'est la même règle qu'au §15.4 de
metadata.py (Outil B) et qu'au registre de conformité de chain_of_custody.py
— réimplémentée ici pour que ce module lève ses propres RapportError, avec le
même sentinel INDISPONIBLE, pour que « indisponible » signifie la même chose
partout dans les trois outils.

Le texte extrait du PDF fusionne « Identification » et le bloc qui décrit le
poste d'observation (opérateur, campagne... puis observateur, coordonnées,
géoïde...) en une seule liste : la mise en page d'origine sépare probablement
les deux par un sous-titre que l'extraction de texte n'a pas conservé. Je les
ai séparés en deux blocs (Identification, PosteObservation) parce que le
contenu est manifestement de deux natures différentes — l'un identifie le
dossier, l'autre décrit le poste — et le dis ici plutôt que de prétendre à
une fidélité littérale que le texte extrait ne permet pas de vérifier.

Ce module n'invente aucune valeur : quand un champ correspond à un type déjà
défini dans Outil A (visee_optique) ou Outil B (preuve_image), les tests de
ce module construisent la fiche avec de vraies instances de ces types
(DonneesExif, FicheGrossissement, GrandeurGeodesique, Verdict...) plutôt
qu'avec des chaînes libres — mais le champ lui-même reste typé `object` et
passe par `declarer()`, parce que la règle du §33 s'applique identiquement à
chacun des soixante et quelques champs de la fiche, qu'il ait ou non un type
dédié ailleurs dans l'outil.
"""

import dataclasses
from dataclasses import dataclass
from typing import Mapping, Tuple

__all__ = [
    "RapportError",
    "INDISPONIBLE",
    "declarer",
    "Identification",
    "PosteObservation",
    "Cible",
    "Geometrie",
    "SystemePhotographique",
    "Atmosphere",
    "Images",
    "Mesures",
    "Resultat",
    "FicheObservation",
    "champs_indisponibles",
    "resume_verdicts",
]


class RapportError(ValueError):
    """Domaine invalide, ou champ de la fiche omis sans le sentinel INDISPONIBLE (§33)."""


INDISPONIBLE = "indisponible"


def declarer(valeur, nom_champ: str):
    """Force un choix explicite : une vraie valeur, ou le sentinel INDISPONIBLE —
    jamais None, jamais une chaîne vide. Réimplémentation locale de la règle du
    §33 (voir aussi metadata.declarer, §15.4) : ChainOfCustodyError et
    MetadataError existent déjà pour leurs modules respectifs, RapportError
    est la sienne.
    """
    if valeur is None or valeur == "":
        raise RapportError(
            f"« {nom_champ} » doit être renseigné ou explicitement « {INDISPONIBLE} », jamais omis (§33)."
        )
    return valeur


def _exiger_tous_les_champs(instance) -> None:
    for champ in dataclasses.fields(instance):
        declarer(getattr(instance, champ.name), champ.name)


@dataclass(frozen=True)
class Identification:
    """Identifie le dossier — pas le poste d'observation (voir PosteObservation)."""

    identifiant_dossier: object
    date_heure_utc_serie: object
    ecart_horloge_mesure: object
    operateur: object
    campagne_et_reference_preenregistrement: object

    def __post_init__(self):
        _exiger_tous_les_champs(self)


@dataclass(frozen=True)
class PosteObservation:
    """Le poste d'observation. `coordonnees_et_systeme_reference` attend une
    PositionGPS ou une PositionGNSS (preuve_image.metadata) quand elle est
    disponible ; `hauteur_ellipsoidale_et_geoide`, une ConversionGeoide
    (visee_optique.geodesy)."""

    observateur: object
    coordonnees_et_systeme_reference: object
    incertitude_recepteur: object
    hauteur_ellipsoidale_et_geoide: object
    altitude_sol_ou_niveau_eau: object
    hauteur_axe_optique: object
    altitude_h_retenue_et_incertitude: object

    def __post_init__(self):
        _exiger_tous_les_champs(self)


@dataclass(frozen=True)
class Cible:
    """La cible visée — §33 « Cible », homonyme mais distincte de
    visee_optique.geometry.Cible (H, z_b) : celle-ci documente toutes les
    sources déclaratives, celle-là porte les deux nombres utilisés au calcul.
    """

    designation_et_sources: object
    coordonnees_et_systeme_reference: object
    altitude_base_zb_et_source: object
    hauteur_totale_H_et_source: object
    parties_pertinentes_cote_connue: object
    extension_longitudinale: object

    def __post_init__(self):
        _exiger_tous_les_champs(self)


@dataclass(frozen=True)
class Geometrie:
    """`distance_D_algorithme_et_incertitude`, `azimut_geodesique` et
    `rayon_courbure_euler` attendent chacun une GrandeurGeodesique
    (visee_optique.geodesy) quand ils sont disponibles — §12.4 : une grandeur
    géodésique établie indépendamment de la photographie analysée.
    """

    distance_D_algorithme_et_incertitude: object
    azimut_geodesique: object
    rayon_courbure_euler: object
    profil_intermediaire_source_et_pas: object
    altitude_maximale_profil_et_marge: object

    def __post_init__(self):
        _exiger_tous_les_champs(self)


@dataclass(frozen=True)
class SystemePhotographique:
    """`boitier_objectif_numeros_serie` et les champs de focale/ouverture/
    exposition attendent une DonneesExif (preuve_image.metadata) quand elle
    est disponible ; `grossissement`, une FicheGrossissement (même module,
    §15.4) — les deux couvrent déjà l'essentiel de ce que ce bloc demande,
    ce module ne les redéfinit pas.
    """

    boitier_objectif_numeros_serie: object
    focale_reelle_et_equivalente: object
    ouverture_temps_pose_sensibilite: object
    resolution_native_et_pas_photosite: object
    resolution_fichier_final: object
    grossissement: object
    recadrage_interne_avant_enregistrement: object
    traitements_computationnels_actifs: object
    profil_distorsion_et_residuel: object

    def __post_init__(self):
        _exiger_tous_les_champs(self)


@dataclass(frozen=True)
class Atmosphere:
    """`classe_de_chaque_donnee` attend une correspondance {grandeur:
    ClasseDonnee} (visee_optique.atmosphere) ; `intervalle_k_retenu_et_justification`,
    une HypotheseRefraction (visee_optique.refraction, §11.7)."""

    temperature_air_par_hauteur: object
    temperature_surface_mer: object
    pression_humidite: object
    profil_vertical_disponible: object
    classe_de_chaque_donnee: object
    intervalle_k_retenu_et_justification: object

    def __post_init__(self):
        _exiger_tous_les_champs(self)


@dataclass(frozen=True)
class Images:
    """`nombre_vues_noms_fichiers_empreintes` et `preuve_datation_empreintes`
    attendent des DeclarationIntegrite / HorodatageTiers (preuve_image.integrity)
    quand ils sont disponibles ; `classement_chaque_vue`, une correspondance
    {nom_fichier: CategorieValiditeImage} (visee_optique.decision, Tableau 11)."""

    nombre_vues_noms_fichiers_empreintes: object
    preuve_datation_empreintes: object
    classement_chaque_vue: object
    vues_exclues_et_motif: object
    resolution_effective_mesuree: object
    transformations_appliquees_copie: object

    def __post_init__(self):
        _exiger_tous_les_champs(self)


@dataclass(frozen=True)
class Mesures:
    """`echelle_par_focale_et_par_reperes` attend un ResultatEchelle
    (preuve_image.metadata, §19.1) quand il est disponible."""

    caracteristique_designee_et_date: object
    positions_pixels_par_analyste: object
    echelle_par_focale_et_par_reperes: object
    hauteur_visible_et_occultee: object
    fraction_visible_observee_et_incertitude: object
    rapports_hauteur_mesures_et_attendus: object

    def __post_init__(self):
        _exiger_tous_les_champs(self)


@dataclass(frozen=True)
class Resultat:
    """`fraction_predite_par_modele_avec_enveloppe` attend une EnveloppeSensibilite
    par modèle (visee_optique.uncertainty) ; `combinaison_plus_defavorable`, la
    combinaison rapportée par ConditionDiscrimination (visee_optique.models,
    §28.2) ; `verdict_par_modele`, une correspondance {nom_modele: Verdict}
    (visee_optique.decision, §28.3) — voir resume_verdicts."""

    fraction_predite_par_modele_avec_enveloppe: object
    ecart_observe_predit_et_incertitude: object
    combinaison_plus_defavorable: object
    resultat_recherche_regimes: object
    verdict_par_modele: object
    motif_indetermination: object

    def __post_init__(self):
        _exiger_tous_les_champs(self)


@dataclass(frozen=True)
class FicheObservation:
    """La fiche standard d'observation complète (§33), neuf blocs dans l'ordre
    du texte. Chaque bloc valide déjà ses propres champs ; rien à revalider
    ici — cette classe n'est qu'un assemblage nommé, comme DossierPreuve dans
    chain_of_custody.py (Outil B) assemble ses propres quatre piliers.
    """

    identification: Identification
    poste_observation: PosteObservation
    cible: Cible
    geometrie: Geometrie
    systeme_photographique: SystemePhotographique
    atmosphere: Atmosphere
    images: Images
    mesures: Mesures
    resultat: Resultat


def champs_indisponibles(fiche: FicheObservation) -> Tuple[str, ...]:
    """Chaque champ de la fiche portant le sentinel INDISPONIBLE, avec son
    chemin pointé (ex. "atmosphere.intervalle_k_retenu_et_justification").

    « Un dossier incomplet est indéterminé, pas défavorable » (§33) suppose de
    pouvoir dire précisément ce qui manque — cette fonction produit cette
    liste plutôt que de laisser deviner.
    """
    manquants = []
    for section in dataclasses.fields(fiche):
        sous_objet = getattr(fiche, section.name)
        for champ in dataclasses.fields(sous_objet):
            if getattr(sous_objet, champ.name) == INDISPONIBLE:
                manquants.append(f"{section.name}.{champ.name}")
    return tuple(manquants)


def resume_verdicts(verdict_par_modele: object) -> str:
    """Résume {nom_modele: Verdict} (visee_optique.decision, §28.3) en une
    ligne, ex. "S: compatible · P: incompatible". Lève si le champ est
    déclaré indisponible ou n'est pas une correspondance vers de vrais
    Verdict — ce module ne devine pas un résumé à partir de texte libre.
    """
    from visee_optique.decision import Verdict  # import différé : dépendance réelle, pas au chargement du module

    if verdict_par_modele == INDISPONIBLE:
        raise RapportError("Aucun verdict disponible : le champ est déclaré indisponible.")
    if not isinstance(verdict_par_modele, Mapping) or not verdict_par_modele:
        raise RapportError(
            "verdict_par_modele doit être une correspondance non vide {nom_modele: Verdict}."
        )
    for nom, verdict in verdict_par_modele.items():
        if not isinstance(verdict, Verdict):
            raise RapportError(f"« {nom} » n'est pas associé à un Verdict (visee_optique.decision).")
    return " · ".join(f"{nom}: {verdict.value}" for nom, verdict in verdict_par_modele.items())
