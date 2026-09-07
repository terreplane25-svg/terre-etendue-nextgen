"""
conteneurs.py — Ce que chaque format d'image déclare, hors EXIF (§16).

POURQUOI CE MODULE
──────────────────
`metadata.py` lit l'EXIF, `isobmff.py` les conteneurs à boîtes, `provenance.py`
le C2PA, le XMP et l'IPTC. Il reste tout le reste : les blocs propres à chaque
format, qui portent souvent la seule information disponible quand l'EXIF a été
purgé — ce qui est le cas ordinaire d'une capture d'écran, d'une image
réexportée par un service web, ou d'un fichier passé par une messagerie.

Un PNG ne porte jamais d'EXIF au sens strict, mais il porte des chunks de
texte, un profil ICC et une résolution physique. Un WebP range tout dans des
morceaux RIFF. Un GIF a ses extensions. Un SVG est du XML, donc lisible en
clair. Aucun de ces formats n'était couvert.

CE QU'IL FAIT, ET CE QU'IL NE FAIT PAS
──────────────────────────────────────
Il inventorie et il décode ce qui est documenté. Il ne DÉCOMPRESSE aucune
image, et il n'interprète pas : un chunk de type inconnu est listé avec sa
taille et son type, jamais deviné.

Le CRC des chunks PNG est VÉRIFIÉ, et le résultat est rendu. C'est une des
rares vérifications que ce paquet peut faire réellement : un CRC faux dit que
les octets ont changé depuis l'écriture du chunk. Un CRC juste ne dit rien de
plus que « celui qui a modifié le chunk a recalculé le CRC », ce qui est le cas
de tout éditeur — et c'est écrit là où le résultat s'affiche.
"""

import binascii
import re
import struct
import zlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

__all__ = [
    "ConteneurError",
    "Chunk",
    "TexteEmbarque",
    "ProfilIcc",
    "InventaireConteneur",
    "inventorier",
    "lire_profil_icc",
    "CLASSES_ICC",
    "ESPACES_ICC",
]


class ConteneurError(ValueError):
    """Structure de conteneur malformée, ou format non couvert par ce module."""


@dataclass(frozen=True)
class Chunk:
    """Un bloc du conteneur, tel qu'il est déclaré.

    `crc_valide` vaut None quand le format n'en porte pas — seul le PNG en a.
    """

    type: str
    offset: int
    longueur: int
    crc_valide: Optional[bool] = None
    #: Une description courte quand le type est documenté. Jamais devinée.
    role: Optional[str] = None


@dataclass(frozen=True)
class TexteEmbarque:
    """Un texte trouvé dans le conteneur, avec d'où il vient.

    `compresse` dit s'il était compressé à l'origine : un zTXt de PNG l'est,
    un tEXt non. L'information compte, parce qu'un texte compressé échappe à
    une recherche de chaînes dans le fichier brut — quelqu'un qui aurait
    inspecté le fichier « à la main » ne l'aurait pas vu.
    """

    origine: str
    cle: str
    valeur: str
    compresse: bool = False
    langue: Optional[str] = None


#: Classes de profil ICC (ICC.1:2010, tableau 17).
CLASSES_ICC = {
    "scnr": "périphérique d'entrée (scanner, capteur)",
    "mntr": "périphérique d'affichage (écran)",
    "prtr": "périphérique de sortie (imprimante)",
    "link": "liaison entre périphériques",
    "spac": "espace colorimétrique abstrait",
    "abst": "transformation abstraite",
    "nmcl": "nuancier nommé",
}

#: Espaces colorimétriques ICC les plus courants.
ESPACES_ICC = {
    "RGB ": "RVB", "GRAY": "niveaux de gris", "CMYK": "CMJN",
    "XYZ ": "CIE XYZ", "Lab ": "CIE L*a*b*", "YCbr": "YCbCr",
}


@dataclass(frozen=True)
class ProfilIcc:
    """L'en-tête d'un profil ICC et sa description.

    C'est la description (`desc`, ou `mluc` sur les profils v4) qui porte le nom
    lisible — « Display P3 », « sRGB IEC61966-2.1 ». Le reste de l'en-tête dit
    ce que le profil PRÉTEND être ; rien ici ne vérifie qu'il décrit bien les
    couleurs du fichier.
    """

    octets: int
    version: str
    classe: str
    classe_libelle: Optional[str]
    espace: str
    espace_libelle: Optional[str]
    espace_connexion: str
    plateforme: Optional[str]
    createur: Optional[str]
    date: Optional[str]
    description: Optional[str]
    copyright_: Optional[str] = None


@dataclass
class InventaireConteneur:
    """Tout ce que le conteneur déclare, format par format."""

    format: str
    octets: int
    largeur: Optional[int] = None
    hauteur: Optional[int] = None
    #: Profondeur en bits par canal (PNG, BMP), ou None si le format n'en déclare pas.
    profondeur_bits: Optional[int] = None
    chunks: List[Chunk] = field(default_factory=list)
    textes: List[TexteEmbarque] = field(default_factory=list)
    profil_icc: Optional[ProfilIcc] = None
    #: Les blocs EXIF et XMP bruts, à passer aux lecteurs dédiés.
    bloc_exif: Optional[bytes] = None
    paquets_xmp: Tuple[bytes, ...] = ()
    #: Résolution physique déclarée, en pixels par mètre puis convertie.
    dpi_x: Optional[float] = None
    dpi_y: Optional[float] = None
    #: Ce que le format déclare de particulier : animation, transparence, etc.
    proprietes: Dict[str, object] = field(default_factory=dict)
    #: Les chunks dont le CRC ne tombe pas juste. Vide n'atteste de rien.
    chunks_corrompus: Tuple[str, ...] = ()


def _ascii(b: bytes) -> str:
    return b.decode("ascii", errors="replace")


def _texte(b: bytes) -> str:
    return b.decode("utf-8", errors="replace")


# ─────────────────────────────────────────────────────────────────────────────
# ICC
# ─────────────────────────────────────────────────────────────────────────────


def _lire_tag_texte(donnees: bytes, offset: int, longueur: int) -> Optional[str]:
    """Lit un tag ICC textuel, dans l'une des trois formes en circulation.

    `text` est de l'ASCII terminé par NUL (ICC v2). `desc` porte une longueur
    puis le texte. `mluc` (v4) est de l'UTF-16BE avec une table de langues ; on
    prend le premier enregistrement, faute d'une langue à préférer — et le dire
    vaut mieux que de choisir en silence.
    """
    if offset + 8 > len(donnees) or longueur < 8:
        return None
    type_ = donnees[offset : offset + 4]
    corps = donnees[offset : offset + longueur]
    if type_ == b"text":
        return _texte(corps[8:]).split("\x00", 1)[0].strip() or None
    if type_ == b"desc":
        if len(corps) < 12:
            return None
        n = struct.unpack_from(">I", corps, 8)[0]
        return _texte(corps[12 : 12 + n]).split("\x00", 1)[0].strip() or None
    if type_ == b"mluc":
        if len(corps) < 16:
            return None
        nb = struct.unpack_from(">I", corps, 8)[0]
        if nb == 0 or len(corps) < 28:
            return None
        taille = struct.unpack_from(">I", corps, 20)[0]
        pos = struct.unpack_from(">I", corps, 24)[0]
        if pos + taille > len(corps):
            return None
        return corps[pos : pos + taille].decode("utf-16-be", errors="replace").strip() or None
    return None


def lire_profil_icc(donnees: bytes) -> ProfilIcc:
    """Lit l'en-tête d'un profil ICC et sa description.

    L'en-tête fait 128 octets (ICC.1:2010 §7.2), suivi d'une table de tags.
    On n'y cherche que la description et la mention de droits : le reste des
    tags décrit des transformations colorimétriques, que ce paquet n'applique
    pas et qu'il n'a donc pas à lire.
    """
    if len(donnees) < 132:
        raise ConteneurError("Profil ICC trop court pour porter un en-tête (128 octets).")
    taille_declaree = struct.unpack_from(">I", donnees, 0)[0]
    if taille_declaree > len(donnees):
        # On lit ce qui est là plutôt que de refuser : un profil tronqué garde
        # un en-tête exploitable, et le signaler vaut mieux que de tout perdre.
        taille_declaree = len(donnees)
    majeur = donnees[8]
    mineur = donnees[9] >> 4
    classe = _ascii(donnees[12:16])
    espace = _ascii(donnees[16:20])
    pcs = _ascii(donnees[20:24])
    an, mois, jour, h, mi, s = struct.unpack_from(">6H", donnees, 24)
    date = None
    if 1 <= mois <= 12 and 1 <= jour <= 31 and an > 1980:
        date = f"{an:04d}-{mois:02d}-{jour:02d}T{h:02d}:{mi:02d}:{s:02d}"
    plateforme = _ascii(donnees[40:44]).strip("\x00 ") or None
    createur = _ascii(donnees[80:84]).strip("\x00 ") or None

    description = None
    copyright_ = None
    nb_tags = struct.unpack_from(">I", donnees, 128)[0] if len(donnees) >= 132 else 0
    # Borne de sûreté : un profil réel dépasse rarement la centaine de tags, et
    # un nombre aberrant ferait boucler sur des octets quelconques.
    for i in range(min(nb_tags, 256)):
        p = 132 + i * 12
        if p + 12 > len(donnees):
            break
        sig = donnees[p : p + 4]
        off, lon = struct.unpack_from(">II", donnees, p + 4)
        if off + lon > len(donnees):
            continue
        if sig == b"desc":
            description = _lire_tag_texte(donnees, off, lon)
        elif sig == b"cprt":
            copyright_ = _lire_tag_texte(donnees, off, lon)

    return ProfilIcc(
        octets=taille_declaree,
        version=f"{majeur}.{mineur}",
        classe=classe,
        classe_libelle=CLASSES_ICC.get(classe),
        espace=espace,
        espace_libelle=ESPACES_ICC.get(espace),
        espace_connexion=pcs,
        plateforme=plateforme,
        createur=createur,
        date=date,
        description=description,
        copyright_=copyright_,
    )


# ─────────────────────────────────────────────────────────────────────────────
# PNG
# ─────────────────────────────────────────────────────────────────────────────

_MAGIE_PNG = b"\x89PNG\r\n\x1a\n"

#: Le rôle des chunks PNG documentés. Un type absent est listé sans rôle
#: plutôt qu'interprété : les chunks privés sont libres, et leur prêter un sens
#: serait inventer.
_ROLES_PNG = {
    "IHDR": "en-tête : dimensions, profondeur, type de couleur",
    "PLTE": "palette",
    "IDAT": "données d'image compressées",
    "IEND": "fin du flux",
    "tEXt": "texte non compressé (Latin-1)",
    "zTXt": "texte compressé",
    "iTXt": "texte international (UTF-8), avec langue",
    "iCCP": "profil ICC intégré",
    "gAMA": "gamma",
    "cHRM": "primaires et point blanc",
    "sRGB": "déclaration d'espace sRGB",
    "pHYs": "résolution physique",
    "tIME": "date de dernière modification",
    "bKGD": "couleur de fond",
    "tRNS": "transparence",
    "sBIT": "bits significatifs",
    "eXIf": "bloc EXIF (PNG 1.5 et suivantes)",
    "acTL": "animation APNG : table de contrôle",
    "fcTL": "animation APNG : contrôle de trame",
    "fdAT": "animation APNG : données de trame",
    "caBX": "manifeste C2PA (JUMBF)",
}

_TYPES_COULEUR_PNG = {
    0: "niveaux de gris", 2: "RVB", 3: "palette",
    4: "niveaux de gris + alpha", 6: "RVB + alpha",
}


def _decompresser(charge: bytes, quoi: str) -> Optional[bytes]:
    """Décompresse un bloc zlib, ou rend None si c'est impossible.

    Un bloc illisible n'interrompt pas l'inventaire : le reste du fichier
    reste exploitable, et l'échec se voit à l'absence du texte.
    """
    try:
        return zlib.decompress(charge)
    except zlib.error:
        del quoi
        return None


def _inventorier_png(donnees: bytes) -> InventaireConteneur:
    inv = InventaireConteneur(format="PNG", octets=len(donnees))
    corrompus: List[str] = []
    xmp: List[bytes] = []
    pos = 8
    while pos + 8 <= len(donnees):
        longueur = struct.unpack_from(">I", donnees, pos)[0]
        type_b = donnees[pos + 4 : pos + 8]
        type_ = _ascii(type_b)
        if pos + 12 + longueur > len(donnees):
            # Chunk qui déborde : on s'arrête sans rien inventer.
            break
        charge = donnees[pos + 8 : pos + 8 + longueur]
        crc_declare = struct.unpack_from(">I", donnees, pos + 8 + longueur)[0]
        # Le CRC porte sur le TYPE et la charge, pas sur la longueur.
        crc_calcule = binascii.crc32(type_b + charge) & 0xFFFFFFFF
        valide = crc_declare == crc_calcule
        if not valide:
            corrompus.append(f"{type_} à l'octet {pos}")
        inv.chunks.append(Chunk(
            type=type_, offset=pos, longueur=longueur,
            crc_valide=valide, role=_ROLES_PNG.get(type_),
        ))

        if type_ == "IHDR" and longueur >= 13:
            l, h = struct.unpack_from(">II", charge, 0)
            inv.largeur, inv.hauteur = l, h
            inv.profondeur_bits = charge[8]
            inv.proprietes["type_couleur"] = charge[9]
            inv.proprietes["type_couleur_libelle"] = _TYPES_COULEUR_PNG.get(charge[9])
            inv.proprietes["entrelacement"] = charge[12] != 0
        elif type_ == "pHYs" and longueur >= 9:
            px, py = struct.unpack_from(">II", charge, 0)
            if charge[8] == 1:  # unité : le mètre
                # 1 pouce = 0,0254 m — la conversion est exacte, pas approchée.
                inv.dpi_x = px * 0.0254
                inv.dpi_y = py * 0.0254
            inv.proprietes["pixels_par_unite"] = (px, py)
            inv.proprietes["unite_physique"] = "mètre" if charge[8] == 1 else "inconnue"
        elif type_ == "tIME" and longueur >= 7:
            an, = struct.unpack_from(">H", charge, 0)
            inv.proprietes["derniere_modification"] = (
                f"{an:04d}-{charge[2]:02d}-{charge[3]:02d}"
                f"T{charge[4]:02d}:{charge[5]:02d}:{charge[6]:02d}"
            )
        elif type_ == "eXIf":
            inv.bloc_exif = charge
        elif type_ == "acTL" and longueur >= 8:
            nb, boucles = struct.unpack_from(">II", charge, 0)
            inv.proprietes["animation"] = True
            inv.proprietes["trames_declarees"] = nb
            inv.proprietes["boucles"] = boucles
        elif type_ == "tEXt":
            cle, _, val = charge.partition(b"\x00")
            inv.textes.append(TexteEmbarque(
                origine="PNG tEXt", cle=_texte(cle),
                valeur=val.decode("latin-1", errors="replace"),
            ))
        elif type_ == "zTXt":
            cle, _, reste = charge.partition(b"\x00")
            # Le premier octet du reste est la méthode de compression (0 = zlib).
            clair = _decompresser(reste[1:], "zTXt") if len(reste) > 1 else None
            inv.textes.append(TexteEmbarque(
                origine="PNG zTXt", cle=_texte(cle),
                valeur=clair.decode("latin-1", errors="replace") if clair else "",
                compresse=True,
            ))
        elif type_ == "iTXt":
            # cle \0 drapeau_compression methode \0 langue \0 cle_traduite \0 texte
            parties = charge.split(b"\x00", 1)
            if len(parties) == 2 and len(parties[1]) >= 2:
                cle = _texte(parties[0])
                comprime = parties[1][0] == 1
                reste = parties[1][2:]
                bouts = reste.split(b"\x00", 2)
                langue = _texte(bouts[0]) if bouts else None
                corps = bouts[2] if len(bouts) >= 3 else b""
                if comprime:
                    clair = _decompresser(corps, "iTXt")
                    corps = clair if clair else b""
                valeur = _texte(corps)
                if "XML:com.adobe.xmp" in cle or valeur.lstrip().startswith(("<?xpacket", "<x:xmpmeta")):
                    xmp.append(corps)
                inv.textes.append(TexteEmbarque(
                    origine="PNG iTXt", cle=cle, valeur=valeur,
                    compresse=comprime, langue=langue or None,
                ))
        elif type_ == "iCCP":
            nom, _, reste = charge.partition(b"\x00")
            clair = _decompresser(reste[1:], "iCCP") if len(reste) > 1 else None
            inv.proprietes["nom_profil_icc"] = _texte(nom)
            if clair:
                try:
                    inv.profil_icc = lire_profil_icc(clair)
                except ConteneurError:
                    inv.profil_icc = None
        elif type_ == "sRGB" and longueur >= 1:
            inv.proprietes["intention_srgb"] = charge[0]

        if type_ == "IEND":
            break
        pos += 12 + longueur

    inv.paquets_xmp = tuple(xmp)
    inv.chunks_corrompus = tuple(corrompus)
    return inv


# ─────────────────────────────────────────────────────────────────────────────
# WebP (RIFF)
# ─────────────────────────────────────────────────────────────────────────────

_ROLES_WEBP = {
    "VP8 ": "image avec perte",
    "VP8L": "image sans perte",
    "VP8X": "en-tête étendu : dimensions et drapeaux",
    "ALPH": "canal alpha",
    "ANIM": "paramètres d'animation",
    "ANMF": "trame d'animation",
    "EXIF": "bloc EXIF",
    "XMP ": "paquet XMP",
    "ICCP": "profil ICC",
}


def _inventorier_webp(donnees: bytes) -> InventaireConteneur:
    inv = InventaireConteneur(format="WebP", octets=len(donnees))
    xmp: List[bytes] = []
    pos = 12  # « RIFF » + taille + « WEBP »
    while pos + 8 <= len(donnees):
        type_ = _ascii(donnees[pos : pos + 4])
        longueur = struct.unpack_from("<I", donnees, pos + 4)[0]
        if pos + 8 + longueur > len(donnees):
            break
        charge = donnees[pos + 8 : pos + 8 + longueur]
        inv.chunks.append(Chunk(
            type=type_, offset=pos, longueur=longueur, role=_ROLES_WEBP.get(type_),
        ))

        if type_ == "VP8X" and longueur >= 10:
            drapeaux = charge[0]
            # Les dimensions sont écrites diminuées de 1, sur 24 bits.
            l = int.from_bytes(charge[4:7], "little") + 1
            h = int.from_bytes(charge[7:10], "little") + 1
            inv.largeur, inv.hauteur = l, h
            inv.proprietes["icc"] = bool(drapeaux & 0x20)
            inv.proprietes["alpha"] = bool(drapeaux & 0x10)
            inv.proprietes["exif"] = bool(drapeaux & 0x08)
            inv.proprietes["xmp"] = bool(drapeaux & 0x04)
            inv.proprietes["animation"] = bool(drapeaux & 0x02)
        elif type_ == "VP8 " and longueur >= 10 and inv.largeur is None:
            # En-tête de trame clé VP8 : 3 octets de balise, puis la signature
            # 0x9D 0x01 0x2A, puis les dimensions sur 14 bits.
            if charge[3:6] == b"\x9d\x01\x2a":
                l, h = struct.unpack_from("<HH", charge, 6)
                inv.largeur, inv.hauteur = l & 0x3FFF, h & 0x3FFF
        elif type_ == "VP8L" and longueur >= 5 and inv.largeur is None:
            if charge[0] == 0x2F:
                bits = int.from_bytes(charge[1:5], "little")
                inv.largeur = (bits & 0x3FFF) + 1
                inv.hauteur = ((bits >> 14) & 0x3FFF) + 1
        elif type_ == "ANIM" and longueur >= 6:
            inv.proprietes["boucles"] = struct.unpack_from("<H", charge, 4)[0]
        elif type_ == "ANMF":
            inv.proprietes["trames"] = int(inv.proprietes.get("trames", 0)) + 1
        elif type_ == "EXIF":
            # Certains encodeurs préfixent « Exif\0\0 », d'autres non.
            inv.bloc_exif = charge[6:] if charge[:6] == b"Exif\x00\x00" else charge
        elif type_ == "XMP ":
            xmp.append(charge)
        elif type_ == "ICCP":
            try:
                inv.profil_icc = lire_profil_icc(charge)
            except ConteneurError:
                inv.profil_icc = None

        # Les morceaux RIFF sont alignés sur deux octets.
        pos += 8 + longueur + (longueur & 1)

    inv.paquets_xmp = tuple(xmp)
    return inv


# ─────────────────────────────────────────────────────────────────────────────
# GIF
# ─────────────────────────────────────────────────────────────────────────────


def _inventorier_gif(donnees: bytes) -> InventaireConteneur:
    inv = InventaireConteneur(format="GIF", octets=len(donnees))
    inv.proprietes["version"] = _ascii(donnees[3:6])
    if len(donnees) >= 10:
        l, h = struct.unpack_from("<HH", donnees, 6)
        inv.largeur, inv.hauteur = l, h
        champ = donnees[10]
        inv.profondeur_bits = ((champ >> 4) & 0x07) + 1
        table_globale = bool(champ & 0x80)
        inv.proprietes["table_couleurs_globale"] = table_globale
        taille_table = 3 * (2 ** ((champ & 0x07) + 1)) if table_globale else 0
    else:
        taille_table = 0

    pos = 13 + taille_table
    trames = 0

    def sauter_sous_blocs(p: int) -> Tuple[int, bytes]:
        """Les données GIF sont en sous-blocs longueur+octets, terminés par 0."""
        morceaux = []
        while p < len(donnees):
            n = donnees[p]
            if n == 0:
                return p + 1, b"".join(morceaux)
            morceaux.append(donnees[p + 1 : p + 1 + n])
            p += 1 + n
        return p, b"".join(morceaux)

    while pos < len(donnees):
        bloc = donnees[pos]
        if bloc == 0x3B:  # terminateur
            inv.chunks.append(Chunk(type="Trailer", offset=pos, longueur=1, role="fin du flux"))
            break
        if bloc == 0x21 and pos + 1 < len(donnees):  # extension
            etiquette = donnees[pos + 1]
            debut = pos
            if etiquette == 0xFE:  # commentaire
                pos, texte = sauter_sous_blocs(pos + 2)
                inv.textes.append(TexteEmbarque(
                    origine="GIF Comment Extension", cle="commentaire",
                    valeur=texte.decode("latin-1", errors="replace"),
                ))
                inv.chunks.append(Chunk(type="Comment", offset=debut,
                                        longueur=pos - debut, role="commentaire"))
            elif etiquette == 0xFF and pos + 14 <= len(donnees):  # application
                identifiant = _ascii(donnees[pos + 3 : pos + 11])
                code = _ascii(donnees[pos + 11 : pos + 14])
                pos, charge = sauter_sous_blocs(pos + 14)
                inv.chunks.append(Chunk(type=f"Application/{identifiant}", offset=debut,
                                        longueur=pos - debut, role="extension d'application"))
                if identifiant == "NETSCAPE" and len(charge) >= 3:
                    inv.proprietes["boucles"] = struct.unpack_from("<H", charge, 1)[0]
                inv.proprietes.setdefault("extensions_application", []).append(
                    identifiant + code)
                # XMP est transporté par une extension d'application dédiée.
                if identifiant == "XMP Data":
                    inv.paquets_xmp = inv.paquets_xmp + (charge,)
            elif etiquette == 0xF9:  # contrôle graphique
                pos, _ = sauter_sous_blocs(pos + 2)
                inv.chunks.append(Chunk(type="GraphicControl", offset=debut,
                                        longueur=pos - debut, role="contrôle de trame"))
            else:
                pos, _ = sauter_sous_blocs(pos + 2)
                inv.chunks.append(Chunk(type=f"Extension 0x{etiquette:02X}",
                                        offset=debut, longueur=pos - debut))
            continue
        if bloc == 0x2C and pos + 10 <= len(donnees):  # descripteur d'image
            trames += 1
            champ = donnees[pos + 9]
            saut = 10 + (3 * (2 ** ((champ & 0x07) + 1)) if champ & 0x80 else 0)
            p = pos + saut + 1  # + l'octet de taille de code LZW
            p, _ = sauter_sous_blocs(p)
            inv.chunks.append(Chunk(type="Image", offset=pos, longueur=p - pos,
                                    role="descripteur et données d'image"))
            pos = p
            continue
        break

    inv.proprietes["trames"] = trames
    inv.proprietes["animation"] = trames > 1
    return inv


# ─────────────────────────────────────────────────────────────────────────────
# BMP
# ─────────────────────────────────────────────────────────────────────────────

_COMPRESSIONS_BMP = {
    0: "aucune (BI_RGB)", 1: "RLE 8 bits", 2: "RLE 4 bits",
    3: "champs de bits (BI_BITFIELDS)", 4: "JPEG", 5: "PNG",
}


def _inventorier_bmp(donnees: bytes) -> InventaireConteneur:
    inv = InventaireConteneur(format="BMP", octets=len(donnees))
    if len(donnees) < 26:
        return inv
    taille_entete = struct.unpack_from("<I", donnees, 14)[0]
    inv.chunks.append(Chunk(type="BITMAPFILEHEADER", offset=0, longueur=14,
                            role="en-tête de fichier"))
    inv.chunks.append(Chunk(type=f"DIB ({taille_entete} octets)", offset=14,
                            longueur=taille_entete, role="en-tête d'image"))
    if taille_entete >= 40 and len(donnees) >= 54:
        l, h = struct.unpack_from("<ii", donnees, 18)
        inv.largeur = abs(l)
        # Une hauteur négative signifie que les lignes sont stockées de haut en
        # bas. C'est une propriété d'écriture, pas une dimension : on la note.
        inv.hauteur = abs(h)
        inv.proprietes["lignes_de_haut_en_bas"] = h < 0
        inv.profondeur_bits = struct.unpack_from("<H", donnees, 28)[0]
        compression = struct.unpack_from("<I", donnees, 30)[0]
        inv.proprietes["compression"] = compression
        inv.proprietes["compression_libelle"] = _COMPRESSIONS_BMP.get(compression)
        ppm_x, ppm_y = struct.unpack_from("<ii", donnees, 38)
        if ppm_x > 0:
            inv.dpi_x = ppm_x * 0.0254
        if ppm_y > 0:
            inv.dpi_y = ppm_y * 0.0254
    return inv


# ─────────────────────────────────────────────────────────────────────────────
# SVG
# ─────────────────────────────────────────────────────────────────────────────

_ATTRS_SVG = ("width", "height", "viewBox", "xmlns:inkscape", "xmlns:sodipodi")


def _inventorier_svg(donnees: bytes) -> InventaireConteneur:
    """Un SVG est du XML : tout y est lisible en clair, et c'est le propos.

    On relève ce qui identifie le producteur — les logiciels d'édition
    vectorielle laissent des espaces de noms qui leur sont propres — et les
    commentaires, qui portent souvent le nom de l'outil et sa version.
    """
    inv = InventaireConteneur(format="SVG", octets=len(donnees))
    texte = donnees.decode("utf-8", errors="replace")

    m = re.search(r"<svg\b[^>]*>", texte, re.IGNORECASE | re.DOTALL)
    entete = m.group(0) if m else ""
    for attr in _ATTRS_SVG:
        a = re.search(re.escape(attr) + r'\s*=\s*"([^"]*)"', entete)
        if a:
            inv.proprietes[attr] = a.group(1)
    # Les dimensions ne sont extraites que si elles sont en pixels nus : une
    # largeur en millimètres ou en pourcentage n'est pas un nombre de pixels,
    # et la convertir demanderait de connaître le contexte de rendu.
    for cle, attr in (("largeur", "width"), ("hauteur", "height")):
        val = inv.proprietes.get(attr)
        if isinstance(val, str):
            n = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*(?:px)?\s*", val)
            if n:
                if cle == "largeur":
                    inv.largeur = int(float(n.group(1)))
                else:
                    inv.hauteur = int(float(n.group(1)))

    for i, commentaire in enumerate(re.findall(r"<!--(.{0,2000}?)-->", texte, re.DOTALL)):
        c = commentaire.strip()
        if c:
            inv.textes.append(TexteEmbarque(
                origine="SVG commentaire", cle=f"commentaire {i + 1}", valeur=c))
    for balise in ("title", "desc"):
        for t in re.findall(rf"<{balise}\b[^>]*>(.{{0,2000}}?)</{balise}>", texte, re.DOTALL | re.IGNORECASE):
            if t.strip():
                inv.textes.append(TexteEmbarque(
                    origine=f"SVG <{balise}>", cle=balise, valeur=t.strip()))

    meta = re.search(r"<metadata\b[^>]*>(.*?)</metadata>", texte, re.DOTALL | re.IGNORECASE)
    if meta:
        inv.chunks.append(Chunk(type="metadata", offset=meta.start(),
                                longueur=len(meta.group(0)), role="bloc de métadonnées RDF"))
        # Le XMP d'un SVG vit dans <metadata>, sans marqueur de paquet.
        if "adobe:ns:meta" in meta.group(1) or "rdf:RDF" in meta.group(1):
            inv.paquets_xmp = (meta.group(1).encode("utf-8"),)
    return inv


# ─────────────────────────────────────────────────────────────────────────────
# Point d'entrée
# ─────────────────────────────────────────────────────────────────────────────


def inventorier(donnees: bytes) -> InventaireConteneur:
    """Inventorie ce que le conteneur déclare, quel que soit son format.

    Lève `ConteneurError` pour un format que ce module ne couvre pas — le
    nommer vaut mieux que rendre un inventaire vide, qui laisserait croire que
    le fichier ne déclare rien.
    """
    if len(donnees) < 12:
        raise ConteneurError("Fichier trop court pour porter un en-tête de conteneur.")
    if donnees[:8] == _MAGIE_PNG:
        return _inventorier_png(donnees)
    if donnees[:4] == b"RIFF" and donnees[8:12] == b"WEBP":
        return _inventorier_webp(donnees)
    if donnees[:6] in (b"GIF87a", b"GIF89a"):
        return _inventorier_gif(donnees)
    if donnees[:2] == b"BM":
        return _inventorier_bmp(donnees)
    tete = donnees[:512].lstrip()
    if tete[:5] == b"<?xml" or tete[:4] == b"<svg":
        if b"<svg" in donnees[:4096]:
            return _inventorier_svg(donnees)
    raise ConteneurError(
        "Format non couvert par ce module : ni PNG, ni WebP, ni GIF, ni BMP, ni SVG. "
        "Les JPEG et TIFF se lisent par metadata.py, les conteneurs à boîtes par "
        "isobmff.py."
    )
