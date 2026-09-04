"""
archive.py — la structure d'archivage figée du §34.

« L'archive doit permettre à un tiers de refaire l'analyse depuis les
fichiers d'origine, sans rien demander à personne. » Le §34 fixe une
arborescence numérotée (l'ordre de lecture), impose 10-originaux/ en lecture
seule, exige un SHA256SUMS couvrant l'archive entière dont l'empreinte est
elle-même déposée, et un journal en ajout seul.

Ce module ne redéfinit RIEN de ce qu'Outil B (preuve_image) a déjà : le
calcul et la comparaison de manifeste (calculer_manifeste, empreinte_manifeste,
comparer_manifestes), la déclaration d'intégrité (DeclarationIntegrite) et le
journal en ajout seul (JournalOperations) sont importés et réexportés d'ici,
pas réimplémentés. Ce module ajoute ce qui manquait : l'arborescence imposée
elle-même, le verrou (au mieux) sur 10-originaux/, et le petit type que le
§34 prévoit pour un fichier qu'on ne peut pas diffuser.

LIMITE ASSUMÉE : `verrouiller_originaux` retire les permissions d'écriture
Unix — une protection par permissions, pas une garantie. Un processus
privilégié (root) ou un accès direct au disque la contourne ; une garantie
réelle demande un support matériellement en écriture unique (WORM) ou un
attribut immuable du système de fichiers (chattr +i), hors du périmètre
d'une bibliothèque Python portable. Ce module fait ce qu'un chmod peut faire,
et le dit plutôt que de laisser croire à plus.
"""

import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Tuple, Union

from preuve_image.integrity import (
    DeclarationIntegrite,
    IntegrityError,
    JournalOperations,
    OperationJournal,
    calculer_manifeste,
    comparer_manifestes,
    empreinte_manifeste,
)

from .report_builder import INDISPONIBLE, declarer

__all__ = [
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
    # réexportés depuis preuve_image.integrity — pas redéfinis ici (§34)
    "DeclarationIntegrite",
    "JournalOperations",
    "OperationJournal",
    "calculer_manifeste",
    "comparer_manifestes",
    "empreinte_manifeste",
]


class ArchiveError(ValueError):
    """Domaine invalide, arborescence non conforme, ou élément non diffusé mal déclaré."""


CheminLike = Union[str, Path]

ARBORESCENCE_IMPOSEE: Tuple[str, ...] = (
    "00-preenregistrement",
    "10-originaux",
    "11-empreintes",
    "20-fiche",
    "30-donnees-externes",
    "40-controles",
    "50-mesures",
    "60-calcul",
    "70-rapport",
    "90-journal",
)

DESCRIPTIONS_REPERTOIRES: Mapping[str, str] = {
    "00-preenregistrement": "plan daté, seuil, modèles déposés, preuve de dépôt",
    "10-originaux": "fichiers tels que sortis de l'appareil, jamais modifiés",
    "11-empreintes": "SHA256SUMS, date de calcul, preuve de datation par un tiers",
    "20-fiche": "fiche du §33, en texte structuré et en PDF",
    "30-donnees-externes": (
        "extraits géodésiques, topographiques, marégraphiques, météorologiques, avec leur date d'édition"
    ),
    "40-controles": "mire, distorsion, stabilité, orientation, cohérence entre focales",
    "50-mesures": "relevés en pixels de chaque analyste, journal de classement horodaté",
    "60-calcul": "code, paramètres, germe aléatoire, sorties intermédiaires",
    "70-rapport": "rapport de chaque analyste, déclarations d'intérêt, rapport de synthèse",
    "90-journal": "journal horodaté de toutes les opérations, y compris les écarts au plan",
}


def nom_dossier_archive(identifiant: str) -> str:
    if not identifiant.strip():
        raise ArchiveError("Un identifiant de dossier est requis pour nommer l'archive.")
    return f"dossier-{identifiant}"


def creer_arborescence(racine: CheminLike, identifiant: str) -> Path:
    """Crée dossier-<identifiant>/ avec les dix répertoires imposés (§34).

    « Les numéros fixent l'ordre de lecture » : ce module les crée dans cet
    ordre, mais ne verrouille pas encore 10-originaux/ — voir
    verrouiller_originaux, à appeler une fois les fichiers d'origine déposés
    dedans, jamais avant.
    """
    racine_dossier = Path(racine) / nom_dossier_archive(identifiant)
    if racine_dossier.exists():
        raise ArchiveError(f"« {racine_dossier} » existe déjà : ne pas écraser une archive existante.")
    for nom in ARBORESCENCE_IMPOSEE:
        (racine_dossier / nom).mkdir(parents=True)
    return racine_dossier


def verifier_arborescence(racine_dossier: CheminLike) -> Tuple[str, ...]:
    """Les noms de répertoires imposés qui manquent sous racine_dossier — un
    tuple vide si l'arborescence est conforme au §34."""
    racine_dossier = Path(racine_dossier)
    if not racine_dossier.is_dir():
        raise ArchiveError(f"Répertoire introuvable : {racine_dossier}")
    return tuple(nom for nom in ARBORESCENCE_IMPOSEE if not (racine_dossier / nom).is_dir())


def verrouiller_originaux(chemin_originaux: CheminLike) -> None:
    """Retire les permissions d'écriture sur 10-originaux/ et tout son contenu,
    au mieux (§34 : « le répertoire 10-originaux est en lecture seule »).

    Voir la limite assumée en tête de module : ceci est un chmod, pas une
    garantie d'immutabilité.
    """
    chemin = Path(chemin_originaux)
    if not chemin.is_dir():
        raise ArchiveError(f"Répertoire introuvable : {chemin}")
    for fichier in chemin.rglob("*"):
        if fichier.is_file():
            fichier.chmod(0o444)
    for sous_dossier in sorted(chemin.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if sous_dossier.is_dir():
            sous_dossier.chmod(0o555)
    chemin.chmod(0o555)


def originaux_proteges(chemin_originaux: CheminLike) -> bool:
    """True si 10-originaux/ et tout son contenu ne portent plus aucun bit
    d'écriture — un contrôle de mode, pas une preuve d'immutabilité (voir
    verrouiller_originaux)."""
    chemin = Path(chemin_originaux)
    if not chemin.is_dir():
        raise ArchiveError(f"Répertoire introuvable : {chemin}")

    bits_ecriture = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH

    def _lecture_seule(p: Path) -> bool:
        return not (p.stat().st_mode & bits_ecriture)

    if not _lecture_seule(chemin):
        return False
    return all(_lecture_seule(p) for p in chemin.rglob("*"))


@dataclass(frozen=True)
class ElementNonDiffuse:
    """§34 : « si un fichier ne peut être diffusé, son empreinte et le nom de
    son détenteur le sont. » Ce que l'archive publie à la place du fichier
    lui-même."""

    nom_fichier: str
    empreinte: str
    detenteur: str

    def __post_init__(self):
        if not self.nom_fichier.strip():
            raise ArchiveError("Le nom du fichier non diffusé doit être renseigné.")
        if not self.detenteur.strip():
            raise ArchiveError("Le détenteur d'un fichier non diffusé doit être nommé.")
        valeur = self.empreinte.strip().lower()
        if len(valeur) != 64 or any(c not in "0123456789abcdef" for c in valeur):
            raise ArchiveError(
                f"L'empreinte de « {self.nom_fichier} » doit être une empreinte SHA-256 valide "
                "(64 caractères hexadécimaux)."
            )
        object.__setattr__(self, "empreinte", valeur)


def verifier_licence_reprise(texte_licence: object) -> object:
    """§34 : « l'archive est publiée sous une licence permettant la reprise et
    la redémarche. » Le protocole ne nomme aucune licence précise — ce module
    ne complète donc pas ce choix à la place de l'opérateur, il vérifie
    seulement qu'un texte réel (ou le sentinel INDISPONIBLE, réexporté de
    report_builder) est déclaré.
    """
    return declarer(texte_licence, "licence_de_reprise")


def declarer_empreinte_archive(manifeste: Mapping[str, str], operateur: str, date_calcul) -> DeclarationIntegrite:
    """Empaquette l'empreinte du manifeste entier (§34 : « son empreinte est
    elle-même déposée ») dans une DeclarationIntegrite (preuve_image.integrity,
    §17.1) — le même objet que pour un fichier isolé de l'Outil B, appliqué
    ici au SHA256SUMS de l'archive plutôt qu'à une photo.
    """
    return DeclarationIntegrite(
        fichier="SHA256SUMS", empreinte=empreinte_manifeste(manifeste), date_calcul=date_calcul, operateur=operateur
    )
