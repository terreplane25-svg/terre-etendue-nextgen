"""
isobmff.py — Les conteneurs à boîtes : HEIC, HEIF, AVIF, CR3 (§16).

POURQUOI UN MODULE À PART
─────────────────────────
Un JPEG range ses métadonnées dans des segments APP ; un TIFF dans des IFD.
Ces deux-là, le paquet les lisait déjà. Une troisième famille couvre
aujourd'hui la majorité des photographies prises au téléphone, et le paquet la
refusait en bloc : ISO/IEC 14496-12, dit ISOBMFF — le conteneur à boîtes du
MP4, réemployé par HEIF (les .HEIC d'Apple et de Samsung), par AVIF, et par le
CR3 des Canon récents.

Le refus était honnête — mieux vaut nommer un format qu'on ne lit pas que
rendre des champs vides — mais il laissait de côté les fichiers les plus
courants. Ce module lève ce refus.

CE QU'IL LIT
────────────
La structure de boîtes, puis, selon ce qu'elle contient :
  · l'item « Exif » d'un HEIF, qui porte un bloc TIFF ordinaire — donc lisible
    par le lecteur EXIF déjà écrit, sans le dupliquer ;
  · l'item « mime » de type RDF, qui porte le XMP ;
  · les items auxiliaires (carte de profondeur, carte de gain HDR), dont la
    PRÉSENCE est relevée sans que leur contenu soit décodé ;
  · les DIMENSIONS déclarées par les boîtes `ispe`, associées à chaque item par
    la boîte `ipma`. C'est la seule mesure de dimensions qu'un HEIF ou un AVIF
    porte hors de l'EXIF : elle permet de confronter les octets à la
    déclaration, ce qu'aucune lecture de l'EXIF seul ne peut faire ;
  · pour un CR3, la boîte `uuid` de Canon, qui range l'IFD0, l'IFD Exif, les
    MakerNotes et l'IFD GPS dans quatre boîtes CMT1 à CMT4 ;
  · les aperçus embarqués : `PRVW` et `THMB` d'un CR3, items image d'un HEIF.

CE QU'IL NE FAIT PAS
────────────────────
Il ne DÉCODE aucune image. Une carte de profondeur est signalée comme présente,
avec sa taille et son type ; l'interpréter demanderait de décompresser du HEVC,
ce qui n'est pas de son ressort et ne servirait pas le protocole.

Il ne valide aucune signature. Comme partout ici, ce qui est lu est ce que le
fichier DÉCLARE.
"""

import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

__all__ = [
    "IsobmffError",
    "Boite",
    "Item",
    "StructureIsobmff",
    "parcourir_boites",
    "analyser_isobmff",
    "UUID_CANON_CR3",
    "TYPES_AUXILIAIRES",
]


class IsobmffError(ValueError):
    """Structure de boîtes malformée, ou hors du domaine que ce lecteur couvre."""


#: La boîte `uuid` où Canon range les métadonnées d'un CR3. L'identifiant est
#: publié dans la documentation du format ; il ne se devine pas.
UUID_CANON_CR3 = bytes.fromhex("85c0b687820f11e08111f4ce462b6a48")

#: Les boîtes qui en contiennent d'autres. Une boîte absente de cette liste est
#: traitée comme opaque : on relève sa taille et son type, pas son contenu.
#: Mieux vaut ignorer une boîte qu'interpréter ses octets au hasard.
_CONTENEURS = {
    b"moov", b"trak", b"mdia", b"minf", b"stbl", b"udta", b"iprp", b"ipco",
    b"dinf", b"edts", b"mvex", b"moof", b"traf", b"grpl", b"mfra",
}

#: Boîtes-conteneurs précédées d'un champ version+flags de quatre octets
#: (« FullBox »). Les traiter comme des conteneurs ordinaires décalerait la
#: lecture de quatre octets et ferait apparaître des boîtes fantômes.
_CONTENEURS_PLEINS = {b"meta"}

#: Les types d'items auxiliaires qu'on sait NOMMER. Leur contenu n'est pas
#: décodé : ce sont des images compressées, et les décompresser n'apprendrait
#: rien que le protocole utilise.
TYPES_AUXILIAIRES = {
    "urn:com:apple:photo:2020:aux:hdrgainmap": "carte de gain HDR (Apple)",
    "urn:com:apple:photo:2019:aux:hdrgainmap": "carte de gain HDR (Apple, 2019)",
    "urn:com:apple:photo:2018:aux:hdrgainmap": "carte de gain HDR (Apple, 2018)",
    "urn:mpeg:hevc:2015:auxid:1": "carte de profondeur (alpha/profondeur MPEG)",
    "urn:mpeg:hevc:2015:auxid:2": "carte de profondeur (MPEG)",
    "urn:com:apple:photo:2020:aux:semanticsegmentationmatte": "masque de segmentation (Apple)",
}


@dataclass(frozen=True)
class Boite:
    """Une boîte, telle qu'elle est déclarée dans le fichier.

    `debut_charge` et `fin_charge` bornent le contenu utile, en-tête exclu :
    c'est ce qu'il faut pour relire les octets sans refaire l'arithmétique.
    """

    type: str
    debut: int
    taille: int
    debut_charge: int
    fin_charge: int
    profondeur: int
    uuid: Optional[bytes] = None

    @property
    def longueur_charge(self) -> int:
        return self.fin_charge - self.debut_charge


@dataclass(frozen=True)
class Item:
    """Un item d'un fichier HEIF : une image, un bloc EXIF, un paquet XMP…"""

    identifiant: int
    type: str
    nom: Optional[str]
    offset: Optional[int]
    longueur: Optional[int]
    #: Le type auxiliaire déclaré (profondeur, gain HDR), s'il y en a un.
    type_auxiliaire: Optional[str] = None
    #: L'item dont celui-ci est une déclinaison (miniature, auxiliaire).
    reference_vers: Tuple[int, ...] = ()
    #: Les dimensions DÉCLARÉES par la boîte `ispe` associée à cet item, quand
    #: `ipma` en associe une. None quand aucune ne l'est — jamais devinées
    #: depuis une autre `ispe` du fichier : chaque item a les siennes, et
    #: emprunter celles d'un voisin donnerait la taille de la carte de
    #: profondeur pour celle de la photographie.
    largeur: Optional[int] = None
    hauteur: Optional[int] = None


@dataclass
class StructureIsobmff:
    """Ce qu'on a pu lire du conteneur, sans rien interpréter au-delà."""

    marque: str
    marques_compatibles: Tuple[str, ...]
    boites: List[Boite] = field(default_factory=list)
    items: List[Item] = field(default_factory=list)
    item_principal: Optional[int] = None
    #: Le bloc TIFF de l'EXIF, prêt à passer au lecteur EXIF. None s'il n'y en a pas.
    bloc_exif: Optional[bytes] = None
    #: Les paquets XMP trouvés, tels quels.
    paquets_xmp: Tuple[bytes, ...] = ()
    #: Les aperçus embarqués : (origine, octets).
    apercus: Tuple[Tuple[str, bytes], ...] = ()
    #: Les items auxiliaires, nommés mais jamais décodés.
    auxiliaires: Tuple[Item, ...] = ()
    #: La version du codec Canon, pour un CR3 (boîte CNCV).
    version_codec: Optional[str] = None
    #: Les MakerNotes bruts d'un CR3 (boîte CMT3), non décodés ici.
    makernotes: Optional[bytes] = None
    #: Les dimensions de l'item PRINCIPAL, lues dans sa boîte `ispe`. C'est la
    #: mesure d'un HEIF ou d'un AVIF, celle qu'on confronte à la déclaration
    #: EXIF. None quand le fichier n'associe aucune `ispe` à son item principal
    #: — un CR3, par exemple, n'en porte pas du tout.
    largeur: Optional[int] = None
    hauteur: Optional[int] = None

    @property
    def est_heif(self) -> bool:
        marques = {self.marque, *self.marques_compatibles}
        return bool(marques & {"heic", "heix", "heim", "heis", "hevc", "mif1", "msf1"})

    @property
    def est_avif(self) -> bool:
        return bool({self.marque, *self.marques_compatibles} & {"avif", "avis"})

    @property
    def est_cr3(self) -> bool:
        return self.marque.strip("\x00 ") == "crx"


def _ascii(b: bytes) -> str:
    return b.decode("ascii", errors="replace")


def parcourir_boites(
    donnees: bytes, debut: int = 0, fin: Optional[int] = None,
    profondeur: int = 0, max_profondeur: int = 12,
) -> List[Boite]:
    """Parcourt les boîtes d'un intervalle, en descendant dans les conteneurs.

    Les tailles déclarées sont VÉRIFIÉES contre les bornes réelles : un fichier
    tronqué ou fabriqué annonce volontiers des boîtes qui débordent, et suivre
    une taille aberrante conduirait à lire n'importe quoi comme si c'était une
    métadonnée. Une boîte incohérente arrête le parcours de son niveau plutôt
    que de lever : le reste du fichier peut rester exploitable, et refuser
    l'ensemble pour une boîte douteuse perdrait ce qui est lisible.
    """
    if fin is None:
        fin = len(donnees)
    boites: List[Boite] = []
    pos = debut
    if profondeur > max_profondeur:
        return boites
    while pos + 8 <= fin:
        taille = struct.unpack_from(">I", donnees, pos)[0]
        type_ = donnees[pos + 4 : pos + 8]
        entete = 8
        uuid_ = None
        if taille == 1:
            # Grande taille sur 64 bits.
            if pos + 16 > fin:
                break
            taille = struct.unpack_from(">Q", donnees, pos + 8)[0]
            entete = 16
        elif taille == 0:
            # « Jusqu'à la fin » : légal, et fréquent pour la dernière boîte.
            taille = fin - pos
        if type_ == b"uuid":
            if pos + entete + 16 > fin:
                break
            uuid_ = donnees[pos + entete : pos + entete + 16]
            entete += 16
        if taille < entete or pos + taille > fin:
            # Taille aberrante : on s'arrête à ce niveau sans rien inventer.
            break

        b = Boite(
            type=_ascii(type_), debut=pos, taille=taille,
            debut_charge=pos + entete, fin_charge=pos + taille,
            profondeur=profondeur, uuid=uuid_,
        )
        boites.append(b)

        if type_ in _CONTENEURS:
            boites.extend(parcourir_boites(
                donnees, b.debut_charge, b.fin_charge, profondeur + 1, max_profondeur))
        elif type_ in _CONTENEURS_PLEINS:
            # FullBox : quatre octets de version et de drapeaux avant les enfants.
            if b.debut_charge + 4 <= b.fin_charge:
                boites.extend(parcourir_boites(
                    donnees, b.debut_charge + 4, b.fin_charge, profondeur + 1, max_profondeur))
        elif type_ == b"uuid" and uuid_ == UUID_CANON_CR3:
            # La boîte Canon contient des boîtes ordinaires (CMT1…CMT4, THMB).
            boites.extend(parcourir_boites(
                donnees, b.debut_charge, b.fin_charge, profondeur + 1, max_profondeur))

        pos += taille
    return boites


def _lire_iinf(donnees: bytes, b: Boite) -> Dict[int, Tuple[str, Optional[str]]]:
    """Les descriptions d'items : identifiant → (type, nom)."""
    pos = b.debut_charge
    if pos + 4 > b.fin_charge:
        return {}
    version = donnees[pos]
    pos += 4
    if version == 0:
        if pos + 2 > b.fin_charge:
            return {}
        nb = struct.unpack_from(">H", donnees, pos)[0]
        pos += 2
    else:
        if pos + 4 > b.fin_charge:
            return {}
        nb = struct.unpack_from(">I", donnees, pos)[0]
        pos += 4

    out: Dict[int, Tuple[str, Optional[str]]] = {}
    for _ in range(nb):
        if pos + 8 > b.fin_charge:
            break
        taille = struct.unpack_from(">I", donnees, pos)[0]
        if donnees[pos + 4 : pos + 8] != b"infe" or taille < 12 or pos + taille > b.fin_charge:
            break
        v = donnees[pos + 8]
        p = pos + 12
        if v >= 2:
            largeur_id = 2 if v == 2 else 4
            if p + largeur_id + 4 > b.fin_charge:
                break
            ident = (struct.unpack_from(">H", donnees, p)[0] if v == 2
                     else struct.unpack_from(">I", donnees, p)[0])
            p += largeur_id + 2  # + item_protection_index
            type_item = _ascii(donnees[p : p + 4])
            p += 4
            fin_nom = donnees.find(b"\x00", p, pos + taille)
            nom = _ascii(donnees[p:fin_nom]) if fin_nom != -1 else None
            out[ident] = (type_item, nom or None)
        pos += taille
    return out


def _lire_iloc(donnees: bytes, b: Boite) -> Dict[int, Tuple[int, int]]:
    """Les emplacements d'items : identifiant → (offset absolu, longueur).

    Seule la méthode de construction 0 (offset dans le fichier) est traitée.
    Les items « idat » (méthode 1) et par référence externe (méthode 2) sont
    IGNORÉS plutôt que lus de travers : rendre un offset faux placerait des
    octets arbitraires à la place d'un bloc EXIF.
    """
    pos = b.debut_charge
    if pos + 8 > b.fin_charge:
        return {}
    version = donnees[pos]
    pos += 4
    tailles = donnees[pos]
    offset_size, length_size = tailles >> 4, tailles & 0xF
    tailles2 = donnees[pos + 1]
    base_offset_size = tailles2 >> 4
    index_size = tailles2 & 0xF if version in (1, 2) else 0
    pos += 2

    if version < 2:
        nb = struct.unpack_from(">H", donnees, pos)[0]
        pos += 2
    else:
        nb = struct.unpack_from(">I", donnees, pos)[0]
        pos += 4

    def lire(n: int) -> int:
        nonlocal pos
        if n == 0:
            return 0
        val = int.from_bytes(donnees[pos : pos + n], "big")
        pos += n
        return val

    out: Dict[int, Tuple[int, int]] = {}
    for _ in range(nb):
        if pos + 2 > b.fin_charge:
            break
        ident = lire(2) if version < 2 else lire(4)
        methode = 0
        if version in (1, 2):
            methode = struct.unpack_from(">H", donnees, pos)[0] & 0xF
            pos += 2
        pos += 2  # data_reference_index
        base = lire(base_offset_size)
        if pos + 2 > b.fin_charge:
            break
        nb_extents = struct.unpack_from(">H", donnees, pos)[0]
        pos += 2
        premier: Optional[Tuple[int, int]] = None
        for j in range(nb_extents):
            lire(index_size)
            off = lire(offset_size)
            lon = lire(length_size)
            if j == 0:
                premier = (base + off, lon)
        # Méthode 0 seulement : un item rangé ailleurs n'est pas localisable ici.
        # Un item en plusieurs morceaux n'est pas contigu : on garde le premier
        # morceau et SA longueur, jamais le total, qui ferait lire au-delà.
        if methode == 0 and premier is not None:
            out[ident] = premier
    return out


def _lire_iref(donnees: bytes, b: Boite) -> Dict[int, Tuple[int, ...]]:
    """Les références entre items : identifiant → identifiants pointés."""
    pos = b.debut_charge
    if pos + 4 > b.fin_charge:
        return {}
    version = donnees[pos]
    pos += 4
    largeur = 2 if version == 0 else 4
    out: Dict[int, Tuple[int, ...]] = {}
    while pos + 8 <= b.fin_charge:
        taille = struct.unpack_from(">I", donnees, pos)[0]
        if taille < 12 or pos + taille > b.fin_charge:
            break
        p = pos + 8
        de = int.from_bytes(donnees[p : p + largeur], "big")
        p += largeur
        if p + 2 > pos + taille:
            break
        nb = struct.unpack_from(">H", donnees, p)[0]
        p += 2
        vers = []
        for _ in range(nb):
            if p + largeur > pos + taille:
                break
            vers.append(int.from_bytes(donnees[p : p + largeur], "big"))
            p += largeur
        out.setdefault(de, tuple())
        out[de] = out[de] + tuple(vers)
        pos += taille
    return out


def _lire_ispe(donnees: bytes, b: Boite) -> Optional[Tuple[int, int]]:
    """Les dimensions déclarées par une ImageSpatialExtentsProperty.

    FullBox : quatre octets de version et de drapeaux, puis largeur et hauteur
    sur quatre octets chacune. Une dimension nulle est REFUSÉE plutôt que
    rendue : elle ne décrit aucune image, et la laisser passer ferait diviser
    par zéro au calcul du rapport d'aspect. Une dimension énorme, en revanche,
    est rendue telle quelle — c'est ce que le fichier DÉCLARE, et le rôle de ce
    module s'arrête là.
    """
    if b.longueur_charge < 12:
        return None
    largeur, hauteur = struct.unpack_from(">II", donnees, b.debut_charge + 4)
    if largeur == 0 or hauteur == 0:
        return None
    return (largeur, hauteur)


def _lire_ipma(donnees: bytes, b: Boite) -> Dict[int, Tuple[int, ...]]:
    """Les associations item → propriétés : identifiant → indices dans `ipco`.

    Les indices sont ceux des ENFANTS DIRECTS d'`ipco`, numérotés à partir de
    1 dans l'ordre où ils apparaissent. L'indice 0 signifie « aucune » et
    n'est pas écarté ici : c'est l'appelant qui borne, une seule fois.

    Chaque association porte un bit `essential` en tête, sur le bit de poids
    fort du champ. Il dit qu'un lecteur qui ne comprend pas la propriété doit
    refuser l'item — ce n'est pas notre cas, on lit ce qui est là. Il est donc
    MASQUÉ, pas interprété ; ne pas le masquer ajouterait 128 ou 32 768 à
    l'indice et ferait pointer l'association hors de la liste, ce qui se
    traduirait par une absence de dimensions plutôt que par une erreur.
    """
    pos = b.debut_charge
    if pos + 8 > b.fin_charge:
        return {}
    version = donnees[pos]
    flags = int.from_bytes(donnees[pos + 1 : pos + 4], "big")
    pos += 4
    nb = struct.unpack_from(">I", donnees, pos)[0]
    pos += 4
    largeur_id = 2 if version < 1 else 4
    largeur_index = 2 if (flags & 1) else 1
    masque = 0x7FFF if largeur_index == 2 else 0x7F

    out: Dict[int, Tuple[int, ...]] = {}
    for _ in range(nb):
        if pos + largeur_id + 1 > b.fin_charge:
            break
        ident = int.from_bytes(donnees[pos : pos + largeur_id], "big")
        pos += largeur_id
        nb_assoc = donnees[pos]
        pos += 1
        indices: List[int] = []
        for _ in range(nb_assoc):
            if pos + largeur_index > b.fin_charge:
                break
            indices.append(
                int.from_bytes(donnees[pos : pos + largeur_index], "big") & masque)
            pos += largeur_index
        out[ident] = out.get(ident, ()) + tuple(indices)
    return out


def _enfants_directs(boites: List[Boite], parent: Boite) -> List[Boite]:
    """Les boîtes filles immédiates d'un conteneur, DANS L'ORDRE du fichier.

    L'ordre est ce qui donne son sens aux indices d'`ipma` : ils comptent les
    enfants d'`ipco` à partir de 1. `parcourir_boites` rend les boîtes dans
    l'ordre du fichier ; filtrer sur la profondeur et sur les bornes du parent
    conserve cet ordre sans le reconstruire.
    """
    return [b for b in boites
            if b.profondeur == parent.profondeur + 1
            and parent.debut_charge <= b.debut < parent.fin_charge]


def _dimensions_par_item(donnees: bytes, boites: List[Boite]) -> Dict[int, Tuple[int, int]]:
    """Les dimensions de chaque item, par le chemin `iprp` → `ipma` + `ipco`.

    L'association est résolue POUR DE BON, jamais approchée par « la plus
    grande `ispe` du fichier ». Un HEIF d'iPhone porte au moins deux `ispe` :
    celle de la photographie et celle de la carte de gain HDR. Prendre la plus
    grande donnerait la bonne réponse la plupart du temps, et la mauvaise sans
    prévenir — exactement le genre de quasi-justesse qu'un relevé probatoire ne
    peut pas se permettre.

    Chaque `ipma` est lu contre l'`ipco` de SON `iprp` : les indices sont
    relatifs à ce conteneur-là, et les croiser entre deux `iprp` associerait
    des propriétés au hasard.
    """
    out: Dict[int, Tuple[int, int]] = {}
    for iprp in [b for b in boites if b.type == "iprp"]:
        enfants = _enfants_directs(boites, iprp)
        ipcos = [b for b in enfants if b.type == "ipco"]
        if not ipcos:
            continue
        proprietes = _enfants_directs(boites, ipcos[0])
        for ipma in [b for b in enfants if b.type == "ipma"]:
            for ident, indices in _lire_ipma(donnees, ipma).items():
                for i in indices:
                    if not 1 <= i <= len(proprietes):
                        continue
                    p = proprietes[i - 1]
                    if p.type != "ispe":
                        continue
                    dim = _lire_ispe(donnees, p)
                    # La PREMIÈRE `ispe` associée fait foi : un item qui en
                    # porterait deux est incohérent, et choisir la seconde
                    # reviendrait à préférer arbitrairement la dernière écrite.
                    if dim is not None and ident not in out:
                        out[ident] = dim
    return out


def _bloc_exif_depuis_item(charge: bytes) -> Optional[bytes]:
    """Le bloc TIFF d'un item « Exif » de HEIF.

    L'item commence par un entier de quatre octets qui donne le décalage
    jusqu'à l'en-tête TIFF — presque toujours 6, pour sauter « Exif\\0\\0 ».
    On se fie à ce champ, puis on VÉRIFIE que l'en-tête TIFF est bien là ; si
    ce n'est pas le cas, on cherche « II » ou « MM ». Suivre aveuglément un
    décalage aberrant donnerait un bloc décalé, que le lecteur EXIF
    interpréterait comme corrompu alors que le fichier est sain.
    """
    if len(charge) < 8:
        return None
    decalage = struct.unpack_from(">I", charge, 0)[0]
    debut = 4 + decalage
    if 0 <= debut <= len(charge) - 8 and charge[debut : debut + 2] in (b"II", b"MM"):
        return charge[debut:]
    for marqueur in (b"II*\x00", b"MM\x00*"):
        i = charge.find(marqueur)
        if i != -1:
            return charge[i:]
    return None


def analyser_isobmff(donnees: bytes) -> StructureIsobmff:
    """Lit la structure d'un fichier à boîtes et en tire ce qui est exploitable."""
    if len(donnees) < 12 or donnees[4:8] != b"ftyp":
        raise IsobmffError(
            "Ce fichier ne commence pas par une boîte « ftyp » : ce n'est pas un "
            "conteneur ISOBMFF, ou il est tronqué en tête."
        )
    taille_ftyp = struct.unpack_from(">I", donnees, 0)[0]
    marque = _ascii(donnees[8:12]).strip("\x00 ")
    compat: List[str] = []
    if 16 <= taille_ftyp <= len(donnees):
        for i in range(16, taille_ftyp, 4):
            m = _ascii(donnees[i : i + 4]).strip("\x00 ")
            if m:
                compat.append(m)

    s = StructureIsobmff(marque=marque, marques_compatibles=tuple(compat))
    s.boites = parcourir_boites(donnees)
    par_type: Dict[str, List[Boite]] = {}
    for b in s.boites:
        par_type.setdefault(b.type, []).append(b)

    # --- HEIF : items, emplacements, références ---
    infos: Dict[int, Tuple[str, Optional[str]]] = {}
    for b in par_type.get("iinf", []):
        infos.update(_lire_iinf(donnees, b))
    emplacements: Dict[int, Tuple[int, int]] = {}
    for b in par_type.get("iloc", []):
        emplacements.update(_lire_iloc(donnees, b))
    references: Dict[int, Tuple[int, ...]] = {}
    for b in par_type.get("iref", []):
        references.update(_lire_iref(donnees, b))
    for b in par_type.get("pitm", []):
        if b.longueur_charge >= 6:
            version = donnees[b.debut_charge]
            p = b.debut_charge + 4
            s.item_principal = (struct.unpack_from(">H", donnees, p)[0] if version == 0
                                else struct.unpack_from(">I", donnees, p)[0])

    dimensions = _dimensions_par_item(donnees, s.boites)
    if s.item_principal is not None and s.item_principal in dimensions:
        s.largeur, s.hauteur = dimensions[s.item_principal]

    apercus: List[Tuple[str, bytes]] = []
    xmp: List[bytes] = []
    auxiliaires: List[Item] = []

    for ident, (type_item, nom) in sorted(infos.items()):
        off_lon = emplacements.get(ident)
        offset = off_lon[0] if off_lon else None
        longueur = off_lon[1] if off_lon else None
        charge = b""
        if offset is not None and longueur is not None and 0 <= offset <= len(donnees) - longueur:
            charge = donnees[offset : offset + longueur]

        aux = None
        if nom and nom in TYPES_AUXILIAIRES:
            aux = TYPES_AUXILIAIRES[nom]
        elif nom and nom.startswith("urn:"):
            # Un type auxiliaire inconnu est NOMMÉ tel quel plutôt qu'écarté :
            # savoir qu'il y a une couche qu'on ne sait pas lire est une
            # information ; la taire n'en est pas une.
            aux = f"auxiliaire non répertorié — {nom}"

        dim = dimensions.get(ident)
        item = Item(
            identifiant=ident, type=type_item, nom=nom,
            offset=offset, longueur=longueur, type_auxiliaire=aux,
            reference_vers=references.get(ident, ()),
            largeur=dim[0] if dim else None,
            hauteur=dim[1] if dim else None,
        )
        s.items.append(item)

        if type_item == "Exif" and charge and s.bloc_exif is None:
            s.bloc_exif = _bloc_exif_depuis_item(charge)
        elif type_item == "mime" and charge[:5] in (b"<?xpa", b"<x:xm", b"<?xml"):
            xmp.append(charge)
        elif type_item == "mime" and b"adobe:ns:meta" in charge[:2048]:
            xmp.append(charge)
        if aux is not None:
            auxiliaires.append(item)
        # Un item image dont les octets commencent par un SOI est un JPEG
        # embarqué : c'est un aperçu utilisable tel quel.
        if charge[:2] == b"\xff\xd8":
            apercus.append((f"item {ident} ({type_item})", charge))

    # --- CR3 : les quatre boîtes CMT de Canon ---
    #
    # CMT1 porte l'IFD0, CMT2 l'IFD Exif, CMT3 les MakerNotes, CMT4 le GPS.
    # Seule CMT1 est un bloc TIFF complet : c'est elle qu'on donne au lecteur.
    for b in par_type.get("CMT1", []):
        bloc = donnees[b.debut_charge : b.fin_charge]
        if bloc[:2] in (b"II", b"MM") and s.bloc_exif is None:
            s.bloc_exif = bloc
    for b in par_type.get("CMT3", []):
        s.makernotes = donnees[b.debut_charge : b.fin_charge]
    for b in par_type.get("CNCV", []):
        s.version_codec = _ascii(donnees[b.debut_charge : b.fin_charge]).strip("\x00")
    for nom_boite in ("PRVW", "THMB"):
        for b in par_type.get(nom_boite, []):
            charge = donnees[b.debut_charge : b.fin_charge]
            i = charge.find(b"\xff\xd8\xff")
            if i != -1:
                apercus.append((f"boîte {nom_boite}", charge[i:]))

    # --- XMP hors items : la boîte `xml ` ---
    for b in par_type.get("xml ", []):
        xmp.append(donnees[b.debut_charge : b.fin_charge])

    s.paquets_xmp = tuple(xmp)
    s.auxiliaires = tuple(auxiliaires)
    # Le plus grand aperçu d'abord : c'est celui qu'on affiche.
    s.apercus = tuple(sorted(apercus, key=lambda x: len(x[1]), reverse=True))
    return s
