"""
rapport_expertise — Outil C : générateur de rapports d'expertise.

Assemble les sorties de l'Outil A (visee_optique : prédiction, incertitude,
verdict) et de l'Outil B (preuve_image : intégrité, métadonnées, chaîne de
détention) dans le format figé du protocole « Portion visible d'une cible
éloignée au-dessus de la mer » v1.0 : la fiche standard d'observation (§33,
report_builder.py) et la structure d'archivage (§34, archive.py).

Ce paquet dépend réellement de visee_optique et de preuve_image — ce n'est
pas une dépendance déclarative de façade : report_builder.resume_verdicts
importe visee_optique.decision.Verdict, et archive.py importe et réexporte
plusieurs symboles de preuve_image.integrity plutôt que de les redéfinir.
Pour le développement dans cet environnement, conftest.py ajoute les deux
projets frères au chemin d'import ; en dehors, installez-les
(`pip install -e ../visee-optique -e ../preuve-image`).
"""

from .report_builder import (
    RapportError,
    INDISPONIBLE,
    declarer,
    Identification,
    PosteObservation,
    Cible,
    Geometrie,
    SystemePhotographique,
    Atmosphere,
    Images,
    Mesures,
    Resultat,
    FicheObservation,
    champs_indisponibles,
    resume_verdicts,
)

from .archive import (
    ArchiveError,
    ARBORESCENCE_IMPOSEE,
    DESCRIPTIONS_REPERTOIRES,
    nom_dossier_archive,
    creer_arborescence,
    verifier_arborescence,
    verrouiller_originaux,
    originaux_proteges,
    ElementNonDiffuse,
    verifier_licence_reprise,
    declarer_empreinte_archive,
    DeclarationIntegrite,
    JournalOperations,
    OperationJournal,
    calculer_manifeste,
    comparer_manifestes,
    empreinte_manifeste,
)

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
    "ArchiveError",
    "ARBORESCENCE_IMPOSEE",
    "DESCRIPTIONS_REPERTOIRES",
    "nom_dossier_archive",
    "creer_arborescence",
    "verifier_arborescence",
    "verrouiller_originaux",
    "originaux_proteges",
    "ElementNonDiffuse",
    "verifier_licence_reprise",
    "declarer_empreinte_archive",
    "DeclarationIntegrite",
    "JournalOperations",
    "OperationJournal",
    "calculer_manifeste",
    "comparer_manifestes",
    "empreinte_manifeste",
]
