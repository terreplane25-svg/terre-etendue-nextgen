"""
integrity.py — Intégrité et traçabilité des fichiers (§17, et la part de
§34 qui concerne l'empreinte de l'archive entière).

Ce module s'en tient à ce que le §17 dit littéralement, ni plus ni
moins :

  - une empreinte SHA-256 établit qu'un fichier n'a pas changé depuis sa
    déclaration — rien de plus. Elle ne prouve ni qu'il sort d'un
    appareil, ni la date de la prise de vue (§17.1, encadré) ;
  - une date de calcul non déposée auprès d'un tiers n'est qu'une
    déclaration de l'opérateur, et doit être rapportée comme telle ;
  - toute manipulation se fait sur une copie, dont le journal des
    opérations est joint et ne s'efface jamais ;
  - seules certaines opérations laissent la copie valide pour la mesure
    (§17.2) — les autres existent peut-être réellement dans la chaîne
    (un appareil qui accentue en JPEG, par exemple), mais disqualifient
    la copie qui les subit.

Ce module NE FAIT PAS d'horodatage réel auprès d'un tiers (RFC 3161 ou
autre) : c'est un échange réseau avec une autorité externe, hors du
périmètre d'une bibliothèque de calcul. `HorodatageTiers` est la
structure qui reçoit l'attestation, quelle que soit l'autorité qui l'a
émise — pas le client qui va la chercher.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union

__all__ = [
    "IntegrityError",
    "empreinte_fichier",
    "verifier_integrite",
    "DeclarationIntegrite",
    "HorodatageTiers",
    "statut_horodatage",
    "OPERATIONS_ADMISES",
    "OPERATIONS_EXCLUES",
    "classer_operation",
    "verifier_chaine_operations",
    "OperationJournal",
    "JournalOperations",
    "CopieDeTravail",
    "calculer_manifeste",
    "empreinte_manifeste",
    "EcartManifeste",
    "comparer_manifestes",
]


class IntegrityError(ValueError):
    """Domaine invalide, empreinte malformée, ou chaîne d'opérations non conforme (§17)."""


CheminLike = Union[str, Path]


def empreinte_fichier(chemin: CheminLike, taille_bloc: int = 1 << 20) -> str:
    """SHA-256 d'un fichier, calculée par lecture en flux (§17.1).

    Lit par blocs de `taille_bloc` octets (1 Mio par défaut) pour ne
    jamais charger un fichier brut entier en mémoire — un fichier RAW
    peut peser plusieurs dizaines de mégaoctets.
    """
    chemin = Path(chemin)
    if not chemin.is_file():
        raise IntegrityError(f"Fichier introuvable : {chemin}")
    hachage = hashlib.sha256()
    with chemin.open("rb") as f:
        for bloc in iter(lambda: f.read(taille_bloc), b""):
            hachage.update(bloc)
    return hachage.hexdigest()


def _valider_empreinte(empreinte: str, contexte: str) -> str:
    valeur = empreinte.strip().lower()
    if len(valeur) != 64 or any(c not in "0123456789abcdef" for c in valeur):
        raise IntegrityError(
            f"{contexte} doit être une empreinte SHA-256 valide (64 caractères hexadécimaux)."
        )
    return valeur


def verifier_integrite(chemin: CheminLike, empreinte_attendue: str) -> bool:
    """True si le fichier actuel a exactement l'empreinte attendue — rien d'autre.

    Ne dit rien sur l'origine du fichier ni sur la date de la prise de
    vue (§17.1, encadré) : seulement qu'il n'a pas changé depuis le
    calcul de l'empreinte attendue.
    """
    attendue = _valider_empreinte(empreinte_attendue, "empreinte_attendue")
    return empreinte_fichier(chemin) == attendue


@dataclass(frozen=True)
class DeclarationIntegrite:
    """L'empreinte d'un fichier d'origine, consignée avec sa date (§17.1, premier bloc)."""

    fichier: str
    empreinte: str
    date_calcul: datetime
    operateur: str

    def __post_init__(self):
        if not self.fichier.strip():
            raise IntegrityError("Le fichier déclaré doit être nommé.")
        if not self.operateur.strip():
            raise IntegrityError("L'opérateur qui calcule l'empreinte doit être nommé.")
        object.__setattr__(self, "empreinte", _valider_empreinte(self.empreinte, f"L'empreinte de « {self.fichier} »"))


@dataclass(frozen=True)
class HorodatageTiers:
    """L'attestation qu'un tiers a daté une empreinte (§17.1, troisième point).

    Ne représente PAS un protocole particulier (RFC 3161, ancrage sur un
    registre public, accusé de réception notarié...) : `reference`
    documente lequel a été utilisé et comment le vérifier. Ce module ne
    contacte aucune autorité — il reçoit ce qu'elle a émis.
    """

    empreinte: str
    tiers: str
    date_reception: datetime
    reference: str

    def __post_init__(self):
        object.__setattr__(self, "empreinte", _valider_empreinte(self.empreinte, "L'empreinte horodatée"))
        if not self.tiers.strip():
            raise IntegrityError("Le tiers datant doit être nommé.")
        if not self.reference.strip():
            raise IntegrityError("La référence de l'horodatage (jeton, accusé, ancrage...) doit être fournie.")


def statut_horodatage(declaration: DeclarationIntegrite, horodatage: Optional[HorodatageTiers]) -> str:
    """Le statut exact à porter au rapport pour une déclaration d'empreinte (§17.1).

    « Déposée le jour même auprès d'un tiers qui la date. À défaut, la
    date de calcul n'est qu'une déclaration de l'opérateur, et le
    rapport le dit. » — cette fonction ne fait que dire, littéralement,
    ce que dit le protocole.
    """
    if horodatage is None:
        return "déclaration de l'opérateur seule — non daté par un tiers"
    if horodatage.empreinte != declaration.empreinte:
        raise IntegrityError(
            "L'horodatage fourni ne porte pas sur l'empreinte déclarée : "
            f"{horodatage.empreinte} != {declaration.empreinte}."
        )
    if horodatage.date_reception.date() == declaration.date_calcul.date():
        return "daté par un tiers le jour même"
    return "daté par un tiers, mais pas le jour même — délai à justifier au rapport"


# --- §17.2 : traitements admis et exclus sur la copie de travail ---

OPERATIONS_ADMISES = frozenset(
    {
        "reglage_contraste_luminosite",
        "conversion_lineaire_sans_accentuation",
        "agrandissement_interpolation_declaree",
        "recadrage_declare_coordonnees_conservees",
    }
)

OPERATIONS_EXCLUES = frozenset(
    {
        "synthese_generative",
        "sur_resolution_apprise",
        "reconstruction_detail",
        "interpolation_creatrice",
        "accentuation_agressive",
        "reduction_bruit_non_lineaire",
        "fusion_multivues_structure_absente",
    }
)


def classer_operation(nom: str) -> bool:
    """True si l'opération est admise, False si elle est exclue (§17.2).

    Lève IntegrityError si `nom` n'est ni l'une ni l'autre : une
    opération non reconnue doit être déclarée et classée avant d'entrer
    dans la chaîne, jamais présumée anodine (§15.4).
    """
    if nom in OPERATIONS_ADMISES:
        return True
    if nom in OPERATIONS_EXCLUES:
        return False
    raise IntegrityError(
        f"Opération non reconnue : « {nom} ». Doit être classée admise ou exclue avant "
        "d'être journalisée (§17.2)."
    )


def verifier_chaine_operations(operations: Sequence[str]) -> None:
    """Lève IntegrityError au premier nom d'opération exclu rencontré (§17.2)."""
    for nom in operations:
        if not classer_operation(nom):
            raise IntegrityError(f"Opération exclue de la mesure : « {nom} » (§17.2).")


@dataclass(frozen=True)
class OperationJournal:
    """Une entrée du journal des opérations appliquées à une copie de travail (§17.1, §34)."""

    horodatage: datetime
    nom: str
    description: str
    empreinte_avant: Optional[str] = None
    empreinte_apres: Optional[str] = None

    def __post_init__(self):
        if not self.description.strip():
            raise IntegrityError("Toute opération journalisée doit être décrite.")
        classer_operation(self.nom)  # lève si l'opération n'est pas reconnue ; accepte admise ou exclue


class JournalOperations:
    """Un journal en ajout seul (§34 : « on n'efface rien, on ajoute les corrections »).

    Volontairement pas un frozen dataclass : l'API n'expose que
    `ajouter`, jamais de suppression ni de remplacement. C'est la
    surface de la classe, pas une convention de nommage, qui interdit
    d'effacer une entrée.
    """

    def __init__(self) -> None:
        self._entrees: List[OperationJournal] = []

    @property
    def entrees(self) -> Tuple[OperationJournal, ...]:
        return tuple(self._entrees)

    def ajouter(self, operation: OperationJournal) -> None:
        self._entrees.append(operation)

    def noms_operations(self) -> Tuple[str, ...]:
        return tuple(e.nom for e in self._entrees)

    def __len__(self) -> int:
        return len(self._entrees)


@dataclass(frozen=True)
class CopieDeTravail:
    """Une copie de travail, reliée à l'empreinte de son origine et à son journal (§17.1).

    L'origine (le fichier d'origine) n'est jamais rouverte en écriture ;
    toute transformation se fait sur cette copie, et seul son journal
    décide si elle reste valide pour la mesure.
    """

    origine: DeclarationIntegrite
    journal: JournalOperations = field(default_factory=JournalOperations)

    def est_valide_pour_mesure(self) -> bool:
        """§17.2 : valide seulement si toutes les opérations journalisées sont admises."""
        try:
            verifier_chaine_operations(self.journal.noms_operations())
            return True
        except IntegrityError:
            return False

    def operation_disqualifiante(self) -> Optional[str]:
        """La première opération exclue journalisée, ou None si la copie est valide (§17.2)."""
        for nom in self.journal.noms_operations():
            if not classer_operation(nom):
                return nom
        return None


# --- §34 : empreinte de l'archive entière (SHA256SUMS) ---


def calculer_manifeste(dossier: CheminLike, suffixes: Optional[Sequence[str]] = None) -> Dict[str, str]:
    """Empreinte SHA-256 de chaque fichier sous `dossier`, indexée par chemin relatif.

    L'équivalent programmatique du fichier `SHA256SUMS` du §34.
    `suffixes`, si fourni, restreint aux extensions données (ex.
    [".cr2", ".jpg"]) — comparaison insensible à la casse.
    """
    racine = Path(dossier)
    if not racine.is_dir():
        raise IntegrityError(f"Dossier introuvable : {racine}")
    suffixes_normalises = {s.lower() for s in suffixes} if suffixes else None
    manifeste: Dict[str, str] = {}
    for chemin in sorted(racine.rglob("*")):
        if not chemin.is_file():
            continue
        if suffixes_normalises is not None and chemin.suffix.lower() not in suffixes_normalises:
            continue
        manifeste[str(chemin.relative_to(racine).as_posix())] = empreinte_fichier(chemin)
    return manifeste


def empreinte_manifeste(manifeste: Dict[str, str]) -> str:
    """Empreinte de l'archive entière — SHA-256 du manifeste trié (§34 : « son empreinte
    est elle-même déposée »). Le tri par chemin rend le résultat indépendant de l'ordre
    de parcours du système de fichiers.
    """
    lignes = [f"{empreinte}  {chemin}" for chemin, empreinte in sorted(manifeste.items())]
    texte = "\n".join(lignes) + ("\n" if lignes else "")
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EcartManifeste:
    """Le résultat de la comparaison entre un manifeste attendu et l'état actuel d'un dossier."""

    manquants: Tuple[str, ...]
    modifies: Tuple[str, ...]
    nouveaux: Tuple[str, ...]

    @property
    def identique(self) -> bool:
        return not (self.manquants or self.modifies or self.nouveaux)


def comparer_manifestes(attendu: Dict[str, str], actuel: Dict[str, str]) -> EcartManifeste:
    """Compare deux manifestes (voir calculer_manifeste) et rapporte l'écart, sans lever."""
    manquants = tuple(sorted(set(attendu) - set(actuel)))
    nouveaux = tuple(sorted(set(actuel) - set(attendu)))
    communs = set(attendu) & set(actuel)
    modifies = tuple(sorted(c for c in communs if attendu[c].lower() != actuel[c].lower()))
    return EcartManifeste(manquants=manquants, modifies=modifies, nouveaux=nouveaux)
