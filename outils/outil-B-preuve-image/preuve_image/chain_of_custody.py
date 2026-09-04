"""
chain_of_custody.py — identification, collecte, acquisition et préservation
alignées sur ISO/IEC 27037:2012 (« Guidelines for identification, collection,
acquisition and preservation of digital evidence »).

Comme sensor_forensics.py, ce module sort du périmètre du protocole
d'observation : ISO/IEC 27037 est une norme externe, citée par son nom et son
année, jamais par un numéro de clause inventé — je n'ai pas le texte de la
norme sous la main pour vérifier une référence plus précise, et préfère le
dire plutôt que fabriquer une citation.

La norme distingue quatre processus — identification, collecte, acquisition,
préservation — et la littérature du domaine résume généralement ses exigences
par quatre principes : auditabilité, répétabilité, reproductibilité,
justifiabilité. Ce module donne à chacun une structure vérifiable :

  - ElementPreuve documente l'identification (ce qui a été trouvé, où, dans
    quel état) ;
  - ChaineDeCustody est le registre de détention, en ajout seul — la même
    discipline que JournalOperations dans integrity.py, appliquée à des
    personnes plutôt qu'à des traitements d'image ;
  - RapportAcquisition documente la copie elle-même (méthode, outil,
    empreintes source et copie) et exige une justification réelle quand la
    méthode modifie nécessairement la source (acquisition en direct) ;
  - RegistreConformite force une justification écrite pour chacun des quatre
    principes, jamais un champ omis (même discipline que le §15.4 de
    metadata.py, dont ce module reprend le sentinel INDISPONIBLE — pour que
    « indisponible » signifie la même chose partout dans l'outil — mais pas
    la fonction declarer() elle-même, pour que ce module lève ses propres
    ChainOfCustodyError plutôt que les MetadataError d'un autre module).

Ce que ce module NE FAIT PAS : il ne réalise aucune acquisition (pas de
client d'imagerie disque, pas d'accès matériel). Comme HorodatageTiers dans
integrity.py pour l'horodatage RFC 3161, il structure et valide ce qu'un
examinateur déclare avoir fait — pas l'action elle-même.
"""

import dataclasses
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Tuple

from .metadata import INDISPONIBLE

__all__ = [
    "ChainOfCustodyError",
    "EtatAppareil",
    "ElementPreuve",
    "Transfert",
    "ChaineDeCustody",
    "MethodeAcquisition",
    "description_methode",
    "modifie_la_source",
    "RapportAcquisition",
    "RoleIntervenant",
    "necessite_specialiste",
    "PRINCIPES_ISO27037",
    "RegistreConformite",
    "DossierPreuve",
]


class ChainOfCustodyError(ValueError):
    """Domaine invalide, transfert de détention incohérent, ou justification manquante."""


def declarer(valeur, nom_champ: str):
    """Force un choix explicite : une vraie valeur, ou le sentinel INDISPONIBLE —
    jamais None, jamais une chaîne vide. Réimplémentation locale de la règle du
    §15.4 (voir metadata.declarer) : même discipline, mais ChainOfCustodyError
    en cas de manquement, pas MetadataError.
    """
    if valeur is None or valeur == "":
        raise ChainOfCustodyError(
            f"« {nom_champ} » doit être renseigné ou explicitement « {INDISPONIBLE} », jamais omis."
        )
    return valeur


def _exiger_non_vide(valeur: str, nom_champ: str) -> None:
    if not valeur.strip():
        raise ChainOfCustodyError(f"« {nom_champ} » doit être renseigné.")


def _valider_empreinte_locale(empreinte: str, contexte: str) -> str:
    valeur = empreinte.strip().lower()
    if len(valeur) != 64 or any(c not in "0123456789abcdef" for c in valeur):
        raise ChainOfCustodyError(
            f"{contexte} doit être une empreinte SHA-256 valide (64 caractères hexadécimaux)."
        )
    return valeur


# --- Identification ---


class EtatAppareil(str, Enum):
    ALLUME = "allumé"
    ETEINT = "éteint"
    INDETERMINE = "indéterminé"


@dataclass(frozen=True)
class ElementPreuve:
    """Ce qui a été identifié, où, par qui, dans quel état — le processus
    d'identification d'ISO/IEC 27037. Un appareil trouvé allumé, ou dont
    l'état n'a pas pu être déterminé, exige une justification réelle de la
    décision prise à son sujet (l'éteindre perd la mémoire vive ; le laisser
    allumé laisse le système évoluer) : ce module ne prend pas cette
    décision, il exige qu'elle soit écrite noir sur blanc.
    """

    identifiant: str
    description: str
    type_support: str
    lieu_decouverte: str
    date_heure: datetime
    identifie_par: str
    etat_appareil: EtatAppareil
    justification_etat: object  # valeur réelle ou INDISPONIBLE — jamais omis
    reference_photographie: object  # idem : ISO/IEC 27037 attend une trace de la scène avant tout contact

    def __post_init__(self):
        for nom_champ in ("identifiant", "description", "type_support", "lieu_decouverte", "identifie_par"):
            _exiger_non_vide(getattr(self, nom_champ), nom_champ)
        declarer(self.justification_etat, "justification_etat")
        declarer(self.reference_photographie, "reference_photographie")
        if self.etat_appareil != EtatAppareil.ETEINT and self.justification_etat == INDISPONIBLE:
            raise ChainOfCustodyError(
                "Un appareil trouvé allumé ou dans un état indéterminé exige une justification "
                "réelle de la décision prise à son sujet, pas le sentinel « indisponible »."
            )


# --- Chaîne de détention (collecte et préservation) ---


@dataclass(frozen=True)
class Transfert:
    """Une entrée du registre de détention : qui a remis l'élément à qui, quand,
    pourquoi, et où — le format canonique d'un registre de chaîne de possession."""

    horodatage: datetime
    cedant: str
    receveur: str
    raison: str
    lieu: str

    def __post_init__(self):
        for nom_champ in ("cedant", "receveur", "raison", "lieu"):
            _exiger_non_vide(getattr(self, nom_champ), nom_champ)
        if self.cedant.strip() == self.receveur.strip():
            raise ChainOfCustodyError("Un transfert exige un cédant et un receveur distincts.")


class ChaineDeCustody:
    """Le registre de détention d'un élément de preuve, en ajout seul — même
    discipline que JournalOperations dans integrity.py : aucune méthode de
    suppression ou de remplacement n'existe sur cette classe.

    Chaque transfert doit provenir du détenteur actuel : la chaîne rejette un
    transfert dont le cédant n'est pas celui qui, d'après son propre
    historique, détient actuellement l'élément. C'est cet invariant qui fait
    d'une suite de transferts une véritable chaîne, et pas une simple liste.
    """

    def __init__(self, element_id: str, detenteur_initial: str) -> None:
        _exiger_non_vide(element_id, "element_id")
        _exiger_non_vide(detenteur_initial, "detenteur_initial")
        self._element_id = element_id
        self._detenteur = detenteur_initial
        self._historique: List[Transfert] = []

    @property
    def element_id(self) -> str:
        return self._element_id

    @property
    def detenteur_actuel(self) -> str:
        return self._detenteur

    @property
    def historique(self) -> Tuple[Transfert, ...]:
        return tuple(self._historique)

    def transferer(self, transfert: Transfert) -> None:
        if transfert.cedant != self._detenteur:
            raise ChainOfCustodyError(
                f"Rupture de la chaîne : « {transfert.cedant} » n'est pas le détenteur actuel "
                f"(« {self._detenteur} »)."
            )
        self._historique.append(transfert)
        self._detenteur = transfert.receveur

    def __len__(self) -> int:
        return len(self._historique)


# --- Acquisition ---


class MethodeAcquisition(str, Enum):
    COPIE_BIT_A_BIT = "copie_bit_a_bit"
    COPIE_LOGIQUE = "copie_logique"
    ACQUISITION_EN_DIRECT = "acquisition_en_direct"


_DESCRIPTIONS_METHODE = {
    MethodeAcquisition.COPIE_BIT_A_BIT: (
        "image forensique bit à bit (secteur par secteur), y compris l'espace non alloué"
    ),
    MethodeAcquisition.COPIE_LOGIQUE: (
        "copie logique des fichiers et dossiers sélectionnés — l'espace non alloué est exclu"
    ),
    MethodeAcquisition.ACQUISITION_EN_DIRECT: (
        "acquisition en direct sur un système actif — modifie inévitablement l'état de la source"
    ),
}


def description_methode(methode: MethodeAcquisition) -> str:
    return _DESCRIPTIONS_METHODE[methode]


def modifie_la_source(methode: MethodeAcquisition) -> bool:
    """True si la méthode modifie nécessairement le support d'origine. Parmi les
    trois méthodes décrites ici, seule l'acquisition en direct est dans ce cas
    — une copie bit à bit ou logique se fait normalement derrière un bloqueur
    en écriture."""
    return methode == MethodeAcquisition.ACQUISITION_EN_DIRECT


@dataclass(frozen=True)
class RapportAcquisition:
    """Documente la copie elle-même : méthode, outil, empreintes source et
    copie, fenêtre temporelle, opérateur. `integrite_verifiee` n'est vraie que
    si les deux empreintes concordent — la preuve que la copie représente
    fidèlement la source au moment de l'acquisition, jamais une présomption.
    """

    element_id: str
    methode: MethodeAcquisition
    outil: str
    version_outil: str
    empreinte_source: str
    empreinte_copie: str
    debut: datetime
    fin: datetime
    operateur: str
    justification_modification_source: object  # valeur réelle ou INDISPONIBLE — jamais omis

    def __post_init__(self):
        for nom_champ in ("element_id", "outil", "version_outil", "operateur"):
            _exiger_non_vide(getattr(self, nom_champ), nom_champ)
        if self.fin <= self.debut:
            raise ChainOfCustodyError("La fin de l'acquisition doit être postérieure à son début.")
        object.__setattr__(
            self, "empreinte_source", _valider_empreinte_locale(self.empreinte_source, "L'empreinte source")
        )
        object.__setattr__(
            self, "empreinte_copie", _valider_empreinte_locale(self.empreinte_copie, "L'empreinte de la copie")
        )
        declarer(self.justification_modification_source, "justification_modification_source")
        if modifie_la_source(self.methode) and self.justification_modification_source == INDISPONIBLE:
            raise ChainOfCustodyError(
                "Une acquisition en direct modifie nécessairement la source : la justification de "
                "cette modification doit être réelle, jamais le sentinel « indisponible »."
            )

    @property
    def integrite_verifiee(self) -> bool:
        return self.empreinte_source == self.empreinte_copie


# --- Compétence ---


class RoleIntervenant(str, Enum):
    PREMIER_INTERVENANT = "premier_intervenant"  # Digital Evidence First Responder (DEFP)
    SPECIALISTE = "specialiste"  # Digital Evidence Specialist (DES)


def necessite_specialiste(methode: MethodeAcquisition, role: RoleIntervenant) -> bool:
    """Règle opérationnelle de ce projet, pas une citation littérale de la norme
    — qui laisse à chaque organisation le soin de fixer ses propres critères
    de compétence : ici, un premier intervenant (DEFP) n'est jamais présumé
    qualifié pour une acquisition bit à bit ou en direct ; seule la copie
    logique lui reste ouverte sans escalade vers un spécialiste (DES).
    """
    if role == RoleIntervenant.SPECIALISTE:
        return False
    return methode != MethodeAcquisition.COPIE_LOGIQUE


# --- Conformité ---

PRINCIPES_ISO27037 = ("auditabilite", "repetabilite", "reproductibilite", "justifiabilite")


@dataclass(frozen=True)
class RegistreConformite:
    """Justifie, pour cet examen, le respect de chacun des quatre principes que
    la littérature du domaine associe généralement à ISO/IEC 27037:2012 —
    auditabilité, répétabilité, reproductibilité, justifiabilité. Une
    justification réelle ou le sentinel INDISPONIBLE, jamais un champ omis
    (même règle que FicheGrossissement, §15.4, dans metadata.py).
    """

    auditabilite: object
    repetabilite: object
    reproductibilite: object
    justifiabilite: object

    def __post_init__(self):
        for champ in dataclasses.fields(self):
            declarer(getattr(self, champ.name), champ.name)


# --- Dossier de preuve : assemble les quatre piliers pour un même élément ---


@dataclass(frozen=True)
class DossierPreuve:
    """Assemble, pour un même élément, les quatre piliers d'ISO/IEC 27037 :
    identification, chaîne de détention, conformité justifiée et — si
    l'élément est numérique — le rapport d'acquisition. Ne certifie ni
    origine ni authenticité : ce dossier documente le traitement, pas la
    scène (même limite que l'empreinte seule au §17.1 de integrity.py).
    """

    element: ElementPreuve
    chaine: ChaineDeCustody
    conformite: RegistreConformite
    acquisition: Optional[RapportAcquisition] = None

    def __post_init__(self):
        if self.chaine.element_id != self.element.identifiant:
            raise ChainOfCustodyError(
                "La chaîne de détention ne porte pas sur le même élément que l'identification "
                f"(« {self.chaine.element_id} » != « {self.element.identifiant} »)."
            )
        if self.acquisition is not None and self.acquisition.element_id != self.element.identifiant:
            raise ChainOfCustodyError(
                "Le rapport d'acquisition ne porte pas sur le même élément que l'identification."
            )

    def pret_pour_acquisition_numerique(self) -> bool:
        """True si un rapport d'acquisition est joint et que son intégrité est vérifiée."""
        return self.acquisition is not None and self.acquisition.integrite_verifiee
