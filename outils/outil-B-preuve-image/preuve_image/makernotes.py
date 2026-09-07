"""
makernotes.py — La STRUCTURE des notes propriétaires, jamais leur sens (§16).

CE QUE CE MODULE FAIT, ET CE QU'IL SE REFUSE À FAIRE
───────────────────────────────────────────────────
Le tag EXIF 0x927C, dit MakerNote, est le seul champ de la norme dont le
contenu n'est pas normalisé : chaque constructeur y écrit ce qu'il veut, dans
la forme qu'il veut, et le change d'un millésime à l'autre. C'est là que
vivent le décompte des déclenchements, le type d'objectif monté, les réglages
de traitement — et c'est pour cela qu'on aimerait le lire.

IL FAIT : reconnaître le constructeur à sa SIGNATURE, qui est dans les octets ;
déterminer la base des offsets et la VÉRIFIER contre les données ; parcourir
l'IFD ; inventorier les tags avec leur identifiant, leur type, leur cardinalité,
leur taille et l'empreinte de leur valeur ; et reconnaître la FORME de certaines
valeurs (texte ASCII, liste de propriétés binaire, IFD imbriqué).

IL NE FAIT PAS : dire ce que les tags SIGNIFIENT. « Tag 0x0095 = type
d'objectif » écrit de mémoire est une attribution, pas une lecture — et une
attribution fausse dans un dossier probatoire coûte plus cher que pas
d'attribution du tout. Le registre `SENS_CONNUS` est donc vide et extensible,
comme celui des signatures de quantification.

Ce qui est rendu reste utile : savoir qu'un fichier porte 87 tags Canon, leurs
identifiants et leurs formes, et l'empreinte de l'ensemble, permet de
CONFRONTER deux fichiers qu'on a tous les deux. Deux MakerNotes de même
empreinte sortent du même appareil aux mêmes réglages.

LA BASE DES OFFSETS : LE PIÈGE, ET COMMENT IL EST DÉSAMORCÉ
───────────────────────────────────────────────────────────
Un IFD range ses valeurs longues à un OFFSET. Mais l'origine de cet offset
change selon le constructeur : l'en-tête TIFF du fichier pour les uns, le début
du MakerNote pour les autres, un en-tête TIFF interne pour Nikon. Se tromper
d'origine ne lève aucune erreur : on lit simplement des octets quelconques, qui
ressemblent à des données.

Ce module ne se fie donc pas à ce que la documentation dit de chaque
constructeur. Il ESSAIE les bases candidates et retient celle qui donne un IFD
COHÉRENT — nombre d'entrées plausible, types connus, offsets dans les bornes.
La base retenue est rendue avec le résultat, ainsi que le fait qu'elle
corresponde ou non à celle qu'on attendait. Un écart est signalé plutôt que
tu : c'est le genre de chose qui apprend quelque chose sur le fichier.
"""

import hashlib
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

__all__ = [
    "MakerNoteError",
    "SignatureConstructeur",
    "TagPropriétaire",
    "AnalyseMakerNote",
    "SIGNATURES",
    "SENS_CONNUS",
    "MOTIF_AUCUN_SENS",
    "reconnaitre_constructeur",
    "analyser_makernote",
]


class MakerNoteError(ValueError):
    """Note propriétaire illisible, ou structure incohérente sous toutes les bases."""


@dataclass(frozen=True)
class SignatureConstructeur:
    """Ce qu'on sait d'une famille de notes propriétaires.

    `base_attendue` est ce que la documentation publiée annonce. Elle n'est PAS
    appliquée telle quelle : elle sert de premier candidat, et le résultat dit
    si c'est bien elle qui a produit un IFD cohérent.
    """

    nom: str
    #: Les octets par lesquels la note commence.
    magie: bytes
    #: Où commence l'IFD, compté depuis le début de la note.
    decalage_ifd: int
    #: « note » (offsets depuis le début de la note), « tiff » (depuis l'en-tête
    #: TIFF du fichier), ou « tiff_interne » (un en-tête TIFF dans la note).
    base_attendue: str
    #: Boutisme imposé par le constructeur, ou None s'il suit celui du fichier.
    boutisme: Optional[str] = None
    #: Ce qui est publié sur cette famille, en une ligne.
    remarque: str = ""


#: Les signatures publiées. Elles sont reconnues AUX OCTETS ; ce qui suit la
#: reconnaissance est vérifié contre les données, jamais présumé.
#:
#: L'ordre compte : les signatures les plus longues d'abord, car certaines sont
#: préfixes d'autres (« OLYMP\0 » et « OLYMPUS\0 »).
SIGNATURES: Tuple[SignatureConstructeur, ...] = (
    SignatureConstructeur(
        "Apple", b"Apple iOS\x00\x00\x01MM", 14, "note", ">",
        "En-tête de 14 octets, boutisme gros-boutien imposé par les deux "
        "derniers octets « MM ».",
    ),
    SignatureConstructeur(
        "Apple (variante)", b"Apple iOS\x00", 14, "note", ">",
        "Même famille, octet de version différent selon la version d'iOS.",
    ),
    SignatureConstructeur(
        "Nikon (type 3)", b"Nikon\x00\x02", 10, "tiff_interne", None,
        "Dix octets d'en-tête, puis un en-tête TIFF COMPLET dont les offsets "
        "partent — c'est la seule famille à en porter un.",
    ),
    SignatureConstructeur(
        "Nikon (type 1)", b"Nikon\x00\x01", 8, "note", None,
        "Ancien format, sans en-tête TIFF interne.",
    ),
    SignatureConstructeur(
        "Olympus (type 2)", b"OLYMPUS\x00", 12, "note", None,
        "Huit octets de signature, puis le boutisme et une version.",
    ),
    SignatureConstructeur(
        "Olympus (type 1)", b"OLYMP\x00", 8, "tiff", None, "Ancien format Olympus.",
    ),
    SignatureConstructeur(
        "Fujifilm", b"FUJIFILM", 12, "note", "<",
        "Huit octets de signature, puis un entier petit-boutien qui donne "
        "l'offset de l'IFD depuis le début de la note.",
    ),
    SignatureConstructeur(
        "Panasonic", b"Panasonic\x00\x00\x00", 12, "tiff", None, "",
    ),
    SignatureConstructeur("Leica", b"LEICA\x00", 8, "tiff", None, ""),
    SignatureConstructeur("Pentax", b"AOC\x00", 6, "note", None, ""),
    SignatureConstructeur("Pentax (PENTAX)", b"PENTAX \x00", 10, "note", None, ""),
    SignatureConstructeur("Sony (DSC)", b"SONY DSC \x00\x00\x00", 12, "tiff", None, ""),
    SignatureConstructeur("Sony (CAM)", b"SONY CAM \x00\x00\x00", 12, "tiff", None, ""),
    SignatureConstructeur("Sony (PIC)", b"SONY PIC\x00", 12, "tiff", None, ""),
    SignatureConstructeur("Sigma / Foveon", b"SIGMA\x00\x00\x00", 10, "tiff", None, ""),
    SignatureConstructeur("Foveon", b"FOVEON\x00\x00", 10, "tiff", None, ""),
    SignatureConstructeur("Ricoh", b"RICOH\x00", 8, "tiff", None, ""),
    SignatureConstructeur("Casio (type 2)", b"QVC\x00\x00\x00", 6, "tiff", None, ""),
    SignatureConstructeur("Samsung", b"SAMSUNG\x00", 8, "tiff", None, ""),
)

#: Le registre du SENS des tags. VIDE, et c'est délibéré.
#:
#: Chaque entrée serait : (constructeur, identifiant de tag) → (nom, ce qui
#: l'établit). Le remplir demande la documentation d'un constructeur, ou un
#: corpus de fichiers réels dont on connaît les réglages. Y écrire « 0x0095 =
#: type d'objectif » de mémoire produirait des attributions fausses présentées
#: comme des lectures — et le sens d'un tag change d'un millésime à l'autre
#: chez le même constructeur.
SENS_CONNUS: Dict[Tuple[str, int], Tuple[str, str]] = {}

MOTIF_AUCUN_SENS = (
    "Les tags sont inventoriés par leur STRUCTURE — identifiant, type, "
    "cardinalité, taille, empreinte — jamais par leur sens. Le registre des "
    "significations est vide : le remplir demande la documentation d'un "
    "constructeur ou un corpus de fichiers dont on connaît les réglages, et le "
    "sens d'un même identifiant change d'un millésime à l'autre chez un même "
    "constructeur. L'inventaire reste utilisable pour CONFRONTER deux fichiers "
    "qu'on a tous les deux : deux notes de même empreinte sortent du même "
    "appareil aux mêmes réglages."
)

#: Taille d'un élément par type TIFF. Un type hors table rend la taille 0, ce
#: qui écarte l'entrée : mieux vaut ignorer un type inconnu que multiplier une
#: cardinalité par une taille devinée.
_TAILLE_TYPE = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8}

_NOMS_TYPE = {
    1: "BYTE", 2: "ASCII", 3: "SHORT", 4: "LONG", 5: "RATIONAL",
    6: "SBYTE", 7: "UNDEFINED", 8: "SSHORT", 9: "SLONG", 10: "SRATIONAL",
    11: "FLOAT", 12: "DOUBLE",
}


@dataclass(frozen=True)
class TagPropriétaire:
    """Un tag de note propriétaire, décrit par sa forme seule."""

    identifiant: int
    type_: int
    type_nom: str
    cardinalite: int
    octets: int
    #: Vrai si la valeur tient dans les quatre octets de l'entrée.
    en_ligne: bool
    #: Empreinte de la valeur. C'est elle qui permet de comparer deux fichiers.
    empreinte: str
    #: La forme reconnue aux octets : « texte », « liste de propriétés binaire »,
    #: « IFD imbriqué », « JPEG »… ou None. Jamais un SENS, seulement une forme.
    forme: Optional[str] = None
    #: Un aperçu du texte, quand la valeur EST du texte. Tronqué.
    apercu_texte: Optional[str] = None
    #: Le sens, s'il est au registre. Vide par construction.
    sens: Optional[Tuple[str, str]] = None


@dataclass
class AnalyseMakerNote:
    """Ce que la structure d'une note propriétaire permet de dire."""

    present: bool
    octets: int
    #: Le constructeur reconnu à la signature, ou None.
    constructeur: Optional[str] = None
    signature_hex: Optional[str] = None
    #: L'empreinte de la note ENTIÈRE. Deux fichiers qui la partagent sortent
    #: du même appareil aux mêmes réglages.
    empreinte: Optional[str] = None
    #: La base d'offset RETENUE, celle qui a donné un IFD cohérent.
    base_retenue: Optional[str] = None
    base_attendue: Optional[str] = None
    #: Vrai quand la base retenue est celle que la documentation annonçait.
    base_conforme: Optional[bool] = None
    boutisme: Optional[str] = None
    tags: Tuple[TagPropriétaire, ...] = ()
    #: Pourquoi la structure n'a pas pu être lue, le cas échéant.
    motif_structure_illisible: Optional[str] = None
    motif_aucun_sens: str = MOTIF_AUCUN_SENS
    remarque_constructeur: str = ""

    @property
    def nombre_de_tags(self) -> int:
        return len(self.tags)


def reconnaitre_constructeur(note: bytes) -> Optional[SignatureConstructeur]:
    """Le constructeur, reconnu à sa signature dans les octets.

    Canon n'a PAS de signature : sa note commence directement par un IFD. Elle
    n'est donc pas reconnue ici, et c'est volontaire — deviner « Canon » parce
    qu'aucune autre signature ne correspond attribuerait à Canon toutes les
    notes de constructeurs qu'on ne connaît pas.
    """
    for s in SIGNATURES:
        if note.startswith(s.magie):
            return s
    return None


def _lire_ifd(
    note: bytes, offset_ifd: int, endian: str, base: int,
) -> Optional[List[Tuple[int, int, int, int, bool]]]:
    """Parcourt un IFD et rend ses entrées, ou None si la structure est incohérente.

    Rendre None plutôt que lever : l'appelant essaie plusieurs bases, et un
    échec est une information normale du protocole d'essai, pas une anomalie.

    Une entrée est (identifiant, type, cardinalité, position de la valeur,
    valeur en ligne). La position est exprimée dans le repère de `note`.

    UNE CARDINALITÉ ABERRANTE est bien le signal le plus fiable d'une mauvaise
    base — mais elle n'a pas besoin d'un contrôle à elle. Un balayage l'a
    établi : toute taille supérieure à la note fait déborder le contrôle
    d'offset qui suit, puisqu'un offset négatif est écarté à part. Un second
    contrôle n'écarterait rien de plus, et se lirait comme une protection
    qu'il n'apporte pas.
    """
    if offset_ifd + 2 > len(note):
        return None
    nb = struct.unpack_from(endian + "H", note, offset_ifd)[0]
    # Un IFD réel dépasse rarement la centaine d'entrées ; au-delà de 512, on a
    # certainement lu des octets qui ne sont pas un compteur.
    if nb == 0 or nb > 512:
        return None
    if offset_ifd + 2 + 12 * nb > len(note):
        return None

    entrees: List[Tuple[int, int, int, int, bool]] = []
    for i in range(nb):
        p = offset_ifd + 2 + 12 * i
        tag, type_, cardinalite = struct.unpack_from(endian + "HHI", note, p)
        taille_elem = _TAILLE_TYPE.get(type_, 0)
        if taille_elem == 0:
            # Type inconnu : l'entrée est écartée, mais elle ne condamne pas
            # l'IFD — un constructeur peut employer un type non normalisé.
            continue
        total = taille_elem * cardinalite
        if total <= 4:
            entrees.append((tag, type_, cardinalite, p + 8, True))
        else:
            offset_valeur = struct.unpack_from(endian + "I", note, p + 8)[0] - base
            if offset_valeur < 0 or offset_valeur + total > len(note):
                return None
            entrees.append((tag, type_, cardinalite, offset_valeur, False))
    # Un IFD dont TOUTES les entrées ont été écartées n'est pas un IFD.
    return entrees or None


def _forme(valeur: bytes) -> Tuple[Optional[str], Optional[str]]:
    """La forme reconnue aux octets, et un aperçu si c'est du texte.

    Une forme n'est pas un sens : dire qu'un tag contient une liste de
    propriétés binaire ne dit rien de ce qu'il y a dedans. Mais savoir qu'un
    tag de 400 octets est du texte lisible, et non des données binaires, oriente
    l'analyste vers ce qu'il peut aller regarder.
    """
    if len(valeur) == 0:
        return None, None
    if valeur[:8] == b"bplist00":
        return "liste de propriétés binaire (bplist)", None
    if valeur[:2] == b"\xff\xd8" and len(valeur) > 4:
        return "JPEG embarqué", None
    if valeur[:4] in (b"II*\x00", b"MM\x00*"):
        return "en-tête TIFF imbriqué", None
    if valeur[:5] == b"<?xml" or valeur[:9] == b"<?xpacket":
        return "XML", None
    # Du texte : au moins 90 % d'octets imprimables, et au moins quatre octets.
    if len(valeur) >= 4:
        imprimables = sum(1 for o in valeur if 32 <= o < 127 or o in (9, 10, 13, 0))
        if imprimables >= 0.9 * len(valeur):
            texte = valeur.split(b"\x00", 1)[0].decode("ascii", errors="replace").strip()
            if texte:
                return "texte", texte[:120]
    return None, None


def analyser_makernote(
    note: bytes,
    offset_dans_le_tiff: int = 0,
    boutisme_fichier: str = "<",
) -> AnalyseMakerNote:
    """Analyse la STRUCTURE d'une note propriétaire.

    `offset_dans_le_tiff` est la position de la note depuis l'en-tête TIFF du
    fichier. Elle est nécessaire pour la base « tiff » : les offsets y sont
    comptés depuis cet en-tête, alors que `note` commence plus loin.

    `boutisme_fichier` est celui du bloc TIFF englobant. Il sert de défaut aux
    constructeurs qui n'imposent pas le leur.
    """
    if not note:
        return AnalyseMakerNote(present=False, octets=0)

    a = AnalyseMakerNote(
        present=True,
        octets=len(note),
        empreinte=hashlib.sha256(note).hexdigest(),
        signature_hex=note[:16].hex(),
    )

    s = reconnaitre_constructeur(note)
    if s is not None:
        a.constructeur = s.nom
        a.base_attendue = s.base_attendue
        a.remarque_constructeur = s.remarque
        boutisme = s.boutisme or boutisme_fichier
        decalage = s.decalage_ifd
    else:
        # Aucune signature. La note commence peut-être directement par un IFD —
        # c'est le cas de Canon — mais on ne le NOMME pas : attribuer à Canon
        # toute note sans signature lui attribuerait tous les constructeurs
        # qu'on ne connaît pas.
        a.constructeur = None
        a.base_attendue = None
        boutisme = boutisme_fichier
        decalage = 0

    # Les bases candidates, dans l'ordre où on les essaie. Les formes
    # PARTICULIÈRES d'abord — en-tête TIFF interne de Nikon, offset écrit en
    # clair chez Fujifilm — parce qu'elles se vérifient aux octets. Viennent
    # ensuite les deux bases générales, « note » puis « tiff ».
    #
    # Cet ordre ne privilégie PAS la base annoncée par la documentation, et
    # c'est délibéré : c'est la cohérence de l'IFD qui tranche, pas ce qu'on
    # attendait. `base_conforme` dit ensuite si les deux coïncident.
    candidats: List[Tuple[str, int, int, str]] = []

    def ajouter(nom: str, offset_ifd: int, base: int, endian: str) -> None:
        if (nom, offset_ifd, base, endian) not in candidats:
            candidats.append((nom, offset_ifd, base, endian))

    if s is not None and s.base_attendue == "tiff_interne":
        # Nikon type 3 : un en-tête TIFF COMPLET commence au décalage annoncé.
        # C'est la seule famille dans ce cas, et l'en-tête se vérifie.
        p = s.decalage_ifd
        if p + 8 <= len(note) and note[p:p + 2] in (b"II", b"MM"):
            e = "<" if note[p:p + 2] == b"II" else ">"
            magique = struct.unpack_from(e + "H", note, p + 2)[0]
            if magique == 42:
                offset0 = struct.unpack_from(e + "I", note, p + 4)[0]
                ajouter("tiff_interne", p + offset0, -p, e)
    if s is not None and s.nom == "Fujifilm" and len(note) >= 12:
        # L'offset de l'IFD est écrit en clair aux octets 8 à 11.
        off = struct.unpack_from("<I", note, 8)[0]
        if 0 < off < len(note):
            ajouter("note", off, 0, "<")

    for endian in ([boutisme] if s is not None and s.boutisme else [boutisme_fichier, "<", ">"]):
        ajouter("note", decalage, 0, endian)
        ajouter("tiff", decalage, offset_dans_le_tiff, endian)
        if s is None:
            # Sans signature, l'IFD peut aussi commencer plus loin — certaines
            # notes portent quelques octets d'en-tête non reconnus.
            for d in (2, 4, 6, 8, 10, 12):
                ajouter("note", d, 0, endian)

    for nom_base, offset_ifd, base, endian in candidats:
        entrees = _lire_ifd(note, offset_ifd, endian, base)
        if entrees is None:
            continue
        a.base_retenue = nom_base
        a.boutisme = "petit-boutien" if endian == "<" else "gros-boutien"
        a.base_conforme = (a.base_attendue is None) or (nom_base == a.base_attendue)
        tags: List[TagPropriétaire] = []
        for tag, type_, cardinalite, pos, en_ligne in entrees:
            total = _TAILLE_TYPE.get(type_, 0) * cardinalite
            valeur = note[pos:pos + total]
            forme, apercu = _forme(valeur)
            tags.append(TagPropriétaire(
                identifiant=tag, type_=type_,
                type_nom=_NOMS_TYPE.get(type_, "type %d" % type_),
                cardinalite=cardinalite, octets=total, en_ligne=en_ligne,
                empreinte=hashlib.sha256(valeur).hexdigest(),
                forme=forme, apercu_texte=apercu,
                sens=SENS_CONNUS.get((a.constructeur or "", tag)),
            ))
        a.tags = tuple(sorted(tags, key=lambda t: t.identifiant))
        return a

    a.motif_structure_illisible = (
        "Aucune base d'offset ne donne un IFD cohérent (%d essayées). La note "
        "est présente et son empreinte reste valide, mais sa structure n'est "
        "pas celle d'un IFD TIFF — plusieurs constructeurs emploient des "
        "formats binaires propres, et certains chiffrent une partie de leurs "
        "notes." % len(candidats)
    )
    return a
