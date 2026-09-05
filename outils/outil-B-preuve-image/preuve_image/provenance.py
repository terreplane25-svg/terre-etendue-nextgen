"""
provenance.py — Ce que le fichier DÉCLARE de son histoire (§16, §17.1).

Trois familles de déclarations vivent dans les en-têtes d'une image, à côté de
l'EXIF : le conteneur C2PA (JUMBF), le bloc XMP, et les enregistrements IPTC.
Ce module les localise, les décode, et les rend tels quels.

CE QUE CE MODULE ÉTABLIT, ET CE QU'IL N'ÉTABLIT PAS
───────────────────────────────────────────────────
Il établit ce qu'un fichier déclare. Il n'établit rien de ce que ces
déclarations affirment.

C'est particulièrement vrai du C2PA, et il faut le dire sans détour : **ce
module ne vérifie aucune signature.** Un manifeste C2PA tire sa valeur d'une
signature COSE adossée à une chaîne X.509 et confrontée à une liste de
confiance. Rien de tout cela n'est fait ici — ni la validation cryptographique,
ni le contrôle de la chaîne de certification, ni le calcul des empreintes de
liaison au contenu (`c2pa.hash.data`). Un manifeste présent et lisible peut
donc être :

  · authentique et intact ;
  · authentique mais désolidarisé de l'image (le contenu a changé depuis) ;
  · entièrement fabriqué, y compris sa structure et ses libellés.

Ce module ne les distingue pas, et l'interface qui l'emploie doit le répéter.
Ce qu'il rend est le CONTENU DÉCLARÉ, au même titre qu'un champ EXIF : « le
fichier affirme ceci », jamais « ceci est vrai ».

Symétriquement, l'absence de manifeste n'établit rien non plus. La quasi-totalité
des appareils n'en écrivent pas, et un recadrage par un outil ordinaire supprime
ce qui existait. Absence de C2PA ≠ suspicion.

POURQUOI DES LECTEURS ÉCRITS ICI
────────────────────────────────
Comme le lecteur EXIF de `metadata.py`, et pour la même raison : pour un usage
probatoire, savoir exactement ce qui est extrait — et ce qui ne l'est pas —
compte autant que l'extraction. Un décodeur CBOR de deux cents lignes que l'on
peut lire vaut mieux qu'une bibliothèque dont on ne saura pas dire ce qu'elle a
silencieusement corrigé.
"""

import hashlib
import re
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

__all__ = [
    "ProvenanceError",
    "decoder_cbor",
    "BoiteJumbf",
    "analyser_boites_jumbf",
    "ManifesteC2PA",
    "ResultatC2PA",
    "extraire_c2pa",
    "BlocXmp",
    "extraire_xmp",
    "EnregistrementIptc",
    "extraire_iptc",
    "ChaineTrouvee",
    "extraire_chaines",
    "Provenance",
    "analyser_provenance",
    "AVERTISSEMENT_C2PA",
    "MARQUEURS_LOGICIELS",
]


class ProvenanceError(ValueError):
    """Flux malformé, ou structure hors du domaine que ce module implémente."""


AVERTISSEMENT_C2PA = (
    "Aucune signature n'est vérifiée. Ce qui suit est ce que le fichier déclare, "
    "pas ce qui est établi : un manifeste C2PA peut être authentique, désolidarisé "
    "du contenu, ou entièrement fabriqué — cette lecture ne les distingue pas. "
    "L'absence de manifeste n'est pas davantage un indice : presque aucun appareil "
    "n'en écrit, et la plupart des retouches effacent ceux qui existaient."
)


# ─────────────────────────────────────────────────────────────────────────────
# CBOR (RFC 8949) — le strict nécessaire pour lire un manifeste C2PA
# ─────────────────────────────────────────────────────────────────────────────

_PROFONDEUR_MAX = 32


def _lire_tete(donnees: bytes, pos: int) -> Tuple[int, int, int]:
    """Rend (type majeur, argument, position suivante)."""
    if pos >= len(donnees):
        raise ProvenanceError("CBOR tronqué : en-tête attendu.")
    octet = donnees[pos]
    majeur = octet >> 5
    info = octet & 0x1F
    pos += 1
    if info < 24:
        return majeur, info, pos
    if info == 24:
        if pos + 1 > len(donnees):
            raise ProvenanceError("CBOR tronqué : argument sur 1 octet.")
        return majeur, donnees[pos], pos + 1
    for taille, fmt in ((25, ">H"), (26, ">I"), (27, ">Q")):
        if info == taille:
            n = struct.calcsize(fmt)
            if pos + n > len(donnees):
                raise ProvenanceError(f"CBOR tronqué : argument sur {n} octets.")
            return majeur, struct.unpack_from(fmt, donnees, pos)[0], pos + n
    if info == 31:
        return majeur, -1, pos  # longueur indéfinie
    raise ProvenanceError(f"CBOR : information additionnelle {info} réservée.")


def _decoder(donnees: bytes, pos: int, profondeur: int) -> Tuple[Any, int]:
    if profondeur > _PROFONDEUR_MAX:
        raise ProvenanceError("CBOR : imbrication au-delà de la profondeur admise.")
    majeur, arg, pos = _lire_tete(donnees, pos)

    if majeur == 0:
        return arg, pos
    if majeur == 1:
        return -1 - arg, pos
    if majeur in (2, 3):
        if arg == -1:
            # Longueur indéfinie : concaténation de fragments jusqu'au break.
            morceaux = []
            while True:
                if pos < len(donnees) and donnees[pos] == 0xFF:
                    pos += 1
                    break
                morceau, pos = _decoder(donnees, pos, profondeur + 1)
                morceaux.append(morceau)
            if majeur == 2:
                return b"".join(morceaux), pos
            return "".join(morceaux), pos
        if pos + arg > len(donnees):
            raise ProvenanceError("CBOR tronqué : chaîne hors des limites.")
        bloc = donnees[pos : pos + arg]
        pos += arg
        if majeur == 2:
            return bloc, pos
        return bloc.decode("utf-8", errors="replace"), pos
    if majeur == 4:
        elements: List[Any] = []
        if arg == -1:
            while True:
                if pos < len(donnees) and donnees[pos] == 0xFF:
                    pos += 1
                    break
                el, pos = _decoder(donnees, pos, profondeur + 1)
                elements.append(el)
        else:
            for _ in range(arg):
                el, pos = _decoder(donnees, pos, profondeur + 1)
                elements.append(el)
        return elements, pos
    if majeur == 5:
        table: Dict[Any, Any] = {}
        def poser(c, v):
            table[c if isinstance(c, (str, int)) else repr(c)] = v
        if arg == -1:
            while True:
                if pos < len(donnees) and donnees[pos] == 0xFF:
                    pos += 1
                    break
                cle, pos = _decoder(donnees, pos, profondeur + 1)
                val, pos = _decoder(donnees, pos, profondeur + 1)
                poser(cle, val)
        else:
            for _ in range(arg):
                cle, pos = _decoder(donnees, pos, profondeur + 1)
                val, pos = _decoder(donnees, pos, profondeur + 1)
                poser(cle, val)
        return table, pos
    if majeur == 6:
        # Étiquette sémantique : on garde la valeur étiquetée, en notant l'étiquette.
        valeur, pos = _decoder(donnees, pos, profondeur + 1)
        return {"_etiquette_cbor": arg, "valeur": valeur}, pos
    # majeur == 7 : valeurs simples et flottants
    if arg == 20:
        return False, pos
    if arg == 21:
        return True, pos
    if arg == 22:
        return None, pos
    if arg == 23:
        return "_indefini", pos
    return arg, pos


def decoder_cbor(donnees: bytes) -> Any:
    """Décode un élément CBOR. Les octets restants sont ignorés, et c'est voulu :
    un manifeste C2PA place parfois plusieurs structures à la suite."""
    valeur, _ = _decoder(donnees, 0, 0)
    return valeur


# ─────────────────────────────────────────────────────────────────────────────
# JUMBF (ISO/IEC 19566-5) — l'emboîtement de boîtes qui porte le C2PA
# ─────────────────────────────────────────────────────────────────────────────

_TYPE_SUPERBOITE = b"jumb"
_TYPE_DESCRIPTION = b"jumd"


@dataclass
class BoiteJumbf:
    """Une boîte JUMBF, avec ses filles si c'est une superboîte.

    `label` vient de la boîte de description (`jumd`) d'une superboîte : c'est
    lui qui nomme « c2pa.assertions », « c2pa.actions », « c2pa.claim »…
    """

    type_: str
    taille: int
    offset: int
    label: Optional[str] = None
    uuid_type: Optional[str] = None
    charge: bytes = b""
    filles: List["BoiteJumbf"] = field(default_factory=list)

    def trouver(self, label: str) -> Optional["BoiteJumbf"]:
        """Première descendante portant ce label, en parcours en profondeur."""
        if self.label == label:
            return self
        for f in self.filles:
            trouvee = f.trouver(label)
            if trouvee is not None:
                return trouvee
        return None

    def toutes(self) -> List["BoiteJumbf"]:
        out = [self]
        for f in self.filles:
            out.extend(f.toutes())
        return out


def _lire_description(charge: bytes) -> Tuple[Optional[str], Optional[str]]:
    """Décode une boîte `jumd` : rend (label, UUID de type).

    Structure : UUID de type (16 octets), drapeaux (1 octet), puis, selon les
    drapeaux, un label terminé par NUL, un identifiant, une signature.
    """
    if len(charge) < 17:
        return None, None
    uuid_type = charge[:16].hex()
    drapeaux = charge[16]
    pos = 17
    label = None
    if drapeaux & 0x02:
        fin = charge.find(b"\x00", pos)
        if fin == -1:
            fin = len(charge)
        label = charge[pos:fin].decode("utf-8", errors="replace")
    return label, uuid_type


def analyser_boites_jumbf(
    donnees: bytes, offset_base: int = 0, profondeur: int = 0
) -> List[BoiteJumbf]:
    """Décode une suite de boîtes JUMBF, récursivement pour les superboîtes.

    Les boîtes malformées arrêtent le parcours du niveau courant sans lever :
    un conteneur partiel se lit jusqu'où il est lisible, et ce qui a été lu
    reste utilisable. Une exception ferait perdre le reste.
    """
    if profondeur > _PROFONDEUR_MAX:
        return []
    boites: List[BoiteJumbf] = []
    pos = 0
    while pos + 8 <= len(donnees):
        lbox = struct.unpack_from(">I", donnees, pos)[0]
        tbox = donnees[pos + 4 : pos + 8]
        entete = 8
        if lbox == 1:
            if pos + 16 > len(donnees):
                break
            lbox = struct.unpack_from(">Q", donnees, pos + 8)[0]
            entete = 16
        elif lbox == 0:
            lbox = len(donnees) - pos  # la boîte court jusqu'à la fin
        if lbox < entete or pos + lbox > len(donnees):
            break
        charge = donnees[pos + entete : pos + lbox]
        boite = BoiteJumbf(
            type_=tbox.decode("ascii", errors="replace"),
            taille=lbox,
            offset=offset_base + pos,
        )
        if tbox == _TYPE_SUPERBOITE:
            boite.filles = analyser_boites_jumbf(
                charge, offset_base + pos + entete, profondeur + 1
            )
            for f in boite.filles:
                if f.type_ == _TYPE_DESCRIPTION.decode():
                    boite.label, boite.uuid_type = _lire_description(f.charge)
                    break
        else:
            boite.charge = charge
        boites.append(boite)
        pos += lbox
    return boites


# ─────────────────────────────────────────────────────────────────────────────
# C2PA : localisation dans le fichier, puis lecture du manifeste
# ─────────────────────────────────────────────────────────────────────────────

_ENTETE_APP11 = b"JP"
_CHUNK_PNG_C2PA = b"caBX"


def _reassembler_app11(segments: List[Tuple[int, int, bytes]]) -> bytes:
    """Recolle les fragments JUMBF répartis sur plusieurs segments APP11.

    Chaque segment porte un numéro d'instance de boîte et un numéro de paquet.
    On regroupe par instance, on trie par numéro de paquet, on concatène. Un
    fichier dont les paquets arriveraient dans le désordre serait ainsi lu
    correctement — et un fichier auquel il manque un paquet donnera une boîte
    tronquée, que `analyser_boites_jumbf` lira jusqu'où elle est lisible.
    """
    par_instance: Dict[int, List[Tuple[int, bytes]]] = {}
    for instance, paquet, charge in segments:
        par_instance.setdefault(instance, []).append((paquet, charge))
    morceaux = []
    for instance in sorted(par_instance):
        for _, charge in sorted(par_instance[instance], key=lambda t: t[0]):
            morceaux.append(charge)
    return b"".join(morceaux)


def _segments_c2pa_jpeg(donnees: bytes) -> List[Tuple[int, int, bytes]]:
    segments: List[Tuple[int, int, bytes]] = []
    pos = 2
    while pos + 4 <= len(donnees):
        if donnees[pos] != 0xFF:
            break
        marqueur = donnees[pos + 1]
        if marqueur == 0xD8 or 0xD0 <= marqueur <= 0xD7:
            pos += 2
            continue
        if marqueur in (0xD9, 0xDA):
            break
        longueur = struct.unpack_from(">H", donnees, pos + 2)[0]
        if marqueur == 0xEB:  # APP11
            corps = donnees[pos + 4 : pos + 2 + longueur]
            if corps[:2] == _ENTETE_APP11 and len(corps) >= 8:
                instance = struct.unpack_from(">H", corps, 2)[0]
                paquet = struct.unpack_from(">I", corps, 4)[0]
                segments.append((instance, paquet, corps[8:]))
        pos += 2 + longueur
    return segments


def _c2pa_depuis_png(donnees: bytes) -> bytes:
    morceaux = []
    pos = 8  # après la signature PNG
    while pos + 8 <= len(donnees):
        longueur = struct.unpack_from(">I", donnees, pos)[0]
        type_ = donnees[pos + 4 : pos + 8]
        if pos + 12 + longueur > len(donnees):
            break
        if type_ == _CHUNK_PNG_C2PA:
            morceaux.append(donnees[pos + 8 : pos + 8 + longueur])
        if type_ == b"IEND":
            break
        pos += 12 + longueur  # longueur + type + charge + CRC
    return b"".join(morceaux)


@dataclass(frozen=True)
class ManifesteC2PA:
    """Un manifeste, tel qu'il se déclare. Rien n'est vérifié."""

    label: str
    assertions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    revendication: Optional[Dict[str, Any]]
    signature_presente: bool
    algorithme_signature: Optional[str]
    generateur: Optional[str]


@dataclass(frozen=True)
class ResultatC2PA:
    """Ce qui a été trouvé, et l'avertissement qui l'accompagne toujours."""

    present: bool
    conteneur: Optional[str]
    octets: int
    manifestes: Tuple[ManifesteC2PA, ...]
    boites: Tuple[str, ...]
    avertissement: str = AVERTISSEMENT_C2PA
    signature_verifiee: bool = False
    motif_non_verifiee: str = (
        "La vérification exige la validation COSE, la chaîne X.509 et une liste de "
        "confiance : rien de cela n'est implémenté ici."
    )


def _charge_utile(boite: BoiteJumbf) -> Any:
    """Décode la charge d'une boîte de contenu selon son type (`cbor` ou `json`)."""
    for fille in boite.filles:
        if fille.type_ == "cbor":
            try:
                return decoder_cbor(fille.charge)
            except ProvenanceError:
                return None
        if fille.type_ == "json":
            import json as _json
            try:
                return _json.loads(fille.charge.decode("utf-8", errors="replace"))
            except ValueError:
                return None
    return None


def _lire_manifeste(boite: BoiteJumbf) -> ManifesteC2PA:
    assertions: Dict[str, Any] = {}
    actions: List[Dict[str, Any]] = []
    revendication = None
    signature_presente = False
    algorithme = None
    generateur = None

    for fille in boite.filles:
        if fille.label == "c2pa.assertions":
            for a in fille.filles:
                if a.label is None:
                    continue
                contenu = _charge_utile(a)
                assertions[a.label] = contenu
                if a.label.startswith("c2pa.actions") and isinstance(contenu, dict):
                    liste = contenu.get("actions")
                    if isinstance(liste, list):
                        actions.extend(x for x in liste if isinstance(x, dict))
        elif fille.label in ("c2pa.claim", "c2pa.claim.v2"):
            revendication = _charge_utile(fille)
            if isinstance(revendication, dict):
                gen = revendication.get("claim_generator")
                if isinstance(gen, str):
                    generateur = gen
                elif isinstance(revendication.get("claim_generator_info"), list):
                    infos = revendication["claim_generator_info"]
                    if infos and isinstance(infos[0], dict):
                        generateur = str(infos[0].get("name", "")) or None
                alg = revendication.get("alg")
                if isinstance(alg, str):
                    algorithme = alg
        elif fille.label == "c2pa.signature":
            signature_presente = True

    return ManifesteC2PA(
        label=boite.label or "(sans label)",
        assertions=assertions,
        actions=actions,
        revendication=revendication if isinstance(revendication, dict) else None,
        signature_presente=signature_presente,
        algorithme_signature=algorithme,
        generateur=generateur,
    )


def extraire_c2pa(donnees: bytes) -> ResultatC2PA:
    """Localise et lit le conteneur C2PA d'un JPEG ou d'un PNG.

    Ne vérifie AUCUNE signature — voir `AVERTISSEMENT_C2PA`, qui accompagne le
    résultat et doit accompagner tout affichage.
    """
    conteneur = None
    brut = b""
    if donnees[:2] == b"\xff\xd8":
        segments = _segments_c2pa_jpeg(donnees)
        if segments:
            conteneur = "JPEG APP11 / JUMBF"
            brut = _reassembler_app11(segments)
    elif donnees[:8] == b"\x89PNG\r\n\x1a\n":
        brut = _c2pa_depuis_png(donnees)
        if brut:
            conteneur = "PNG caBX / JUMBF"

    if not brut:
        return ResultatC2PA(present=False, conteneur=None, octets=0, manifestes=(), boites=())

    boites = analyser_boites_jumbf(brut)
    magasin = None
    for b in boites:
        trouve = b.trouver("c2pa")
        if trouve is not None:
            magasin = trouve
            break
    manifestes: List[ManifesteC2PA] = []
    if magasin is not None:
        for m in magasin.filles:
            if m.type_ == "jumb" and m.label:
                manifestes.append(_lire_manifeste(m))

    etiquettes = []
    for b in boites:
        for x in b.toutes():
            if x.label:
                etiquettes.append(x.label)

    return ResultatC2PA(
        present=True,
        conteneur=conteneur,
        octets=len(brut),
        manifestes=tuple(manifestes),
        boites=tuple(etiquettes),
    )


# ─────────────────────────────────────────────────────────────────────────────
# XMP
# ─────────────────────────────────────────────────────────────────────────────

_NS_XMP = b"http://ns.adobe.com/xap/1.0/\x00"
_NS_XMP_ETENDU = b"http://ns.adobe.com/xmp/extension/\x00"


@dataclass(frozen=True)
class BlocXmp:
    """Le paquet XMP tel qu'il est écrit, plus quelques champs relevés.

    Le XML n'est pas interprété au-delà d'un relevé d'attributs : lire un
    document XMP entier demanderait un analyseur RDF, et ce que le protocole en
    attend tient dans quelques champs — d'où ils viennent restant visible dans
    `brut`.
    """

    conteneur: str
    octets: int
    brut: str
    etendu: bool
    champs: Dict[str, str]


_CHAMPS_XMP = (
    "xmp:CreatorTool", "xmp:ModifyDate", "xmp:CreateDate", "xmp:MetadataDate",
    "tiff:Make", "tiff:Model", "dc:creator", "dc:rights",
    "photoshop:DateCreated", "photoshop:History",
    "crs:Version", "crs:ProcessVersion",
    "dcterms:provenance", "c2pa:manifest",
    "GCamera:MicroVideo", "Container:Directory",
)


def _relever_champs_xmp(texte: str) -> Dict[str, str]:
    champs: Dict[str, str] = {}
    for nom in _CHAMPS_XMP:
        # Forme attribut : nom="valeur"
        m = re.search(re.escape(nom) + r'\s*=\s*"([^"]*)"', texte)
        if m:
            champs[nom] = m.group(1)
            continue
        # Forme élément : <nom>valeur</nom>
        m = re.search(re.escape(nom) + r"[^>]*>([^<]{1,400})<", texte)
        if m:
            champs[nom] = m.group(1).strip()
    return champs


def extraire_xmp(donnees: bytes) -> List[BlocXmp]:
    """Relève les paquets XMP d'un JPEG (APP1) ou d'un PNG (iTXt/tEXt)."""
    blocs: List[BlocXmp] = []
    if donnees[:2] == b"\xff\xd8":
        pos = 2
        while pos + 4 <= len(donnees):
            if donnees[pos] != 0xFF:
                break
            marqueur = donnees[pos + 1]
            if marqueur == 0xD8 or 0xD0 <= marqueur <= 0xD7:
                pos += 2
                continue
            if marqueur in (0xD9, 0xDA):
                break
            longueur = struct.unpack_from(">H", donnees, pos + 2)[0]
            corps = donnees[pos + 4 : pos + 2 + longueur]
            if marqueur == 0xE1:
                for ns, etendu in ((_NS_XMP, False), (_NS_XMP_ETENDU, True)):
                    if corps.startswith(ns):
                        charge = corps[len(ns) :]
                        # Le XMP étendu porte 40 octets d'en-tête (GUID, tailles).
                        if etendu and len(charge) > 40:
                            charge = charge[40:]
                        texte = charge.decode("utf-8", errors="replace")
                        blocs.append(BlocXmp(
                            conteneur="JPEG APP1 / XMP" + (" étendu" if etendu else ""),
                            octets=len(charge), brut=texte, etendu=etendu,
                            champs=_relever_champs_xmp(texte),
                        ))
            pos += 2 + longueur
    elif donnees[:8] == b"\x89PNG\r\n\x1a\n":
        pos = 8
        while pos + 8 <= len(donnees):
            longueur = struct.unpack_from(">I", donnees, pos)[0]
            type_ = donnees[pos + 4 : pos + 8]
            if pos + 12 + longueur > len(donnees):
                break
            charge = donnees[pos + 8 : pos + 8 + longueur]
            if type_ in (b"iTXt", b"tEXt") and b"XML:com.adobe.xmp" in charge[:64]:
                debut = charge.find(b"<x:xmpmeta")
                if debut == -1:
                    debut = charge.find(b"<?xpacket")
                if debut != -1:
                    texte = charge[debut:].decode("utf-8", errors="replace")
                    blocs.append(BlocXmp(
                        conteneur=f"PNG {type_.decode()} / XMP", octets=len(texte),
                        brut=texte, etendu=False, champs=_relever_champs_xmp(texte),
                    ))
            if type_ == b"IEND":
                break
            pos += 12 + longueur
    return blocs


# ─────────────────────────────────────────────────────────────────────────────
# IPTC-IIM, dans le bloc de ressources Photoshop (APP13)
# ─────────────────────────────────────────────────────────────────────────────

_ENTETE_PHOTOSHOP = b"Photoshop 3.0\x00"
_RESSOURCE_IPTC = 0x0404

# Jeu 2 de l'IIM (IPTC-NAA 4.1) — les champs qu'un rédacteur remplit.
_CHAMPS_IIM = {
    5: "Titre de l'objet", 10: "Urgence", 15: "Catégorie", 20: "Catégorie supplémentaire",
    25: "Mots-clés", 40: "Instructions particulières", 55: "Date de création",
    60: "Heure de création", 62: "Date de numérisation", 65: "Programme d'origine",
    70: "Version du programme", 80: "Auteur", 85: "Fonction de l'auteur",
    90: "Ville", 92: "Lieu-dit", 95: "Région", 100: "Code pays", 101: "Pays",
    103: "Référence de transmission", 105: "Titre rédactionnel", 110: "Crédit",
    115: "Source", 116: "Mention de droits", 120: "Légende", 122: "Auteur de la légende",
}


@dataclass(frozen=True)
class EnregistrementIptc:
    jeu: int
    numero: int
    libelle: str
    valeur: str


def extraire_iptc(donnees: bytes) -> List[EnregistrementIptc]:
    """Relève les enregistrements IPTC-IIM d'un JPEG (APP13 / Photoshop IRB)."""
    if donnees[:2] != b"\xff\xd8":
        return []
    enregistrements: List[EnregistrementIptc] = []
    pos = 2
    while pos + 4 <= len(donnees):
        if donnees[pos] != 0xFF:
            break
        marqueur = donnees[pos + 1]
        if marqueur == 0xD8 or 0xD0 <= marqueur <= 0xD7:
            pos += 2
            continue
        if marqueur in (0xD9, 0xDA):
            break
        longueur = struct.unpack_from(">H", donnees, pos + 2)[0]
        corps = donnees[pos + 4 : pos + 2 + longueur]
        if marqueur == 0xED and corps.startswith(_ENTETE_PHOTOSHOP):
            enregistrements.extend(_lire_irb(corps[len(_ENTETE_PHOTOSHOP) :]))
        pos += 2 + longueur
    return enregistrements


def _lire_irb(bloc: bytes) -> List[EnregistrementIptc]:
    out: List[EnregistrementIptc] = []
    pos = 0
    while pos + 12 <= len(bloc):
        if bloc[pos : pos + 4] != b"8BIM":
            break
        identifiant = struct.unpack_from(">H", bloc, pos + 4)[0]
        taille_nom = bloc[pos + 6]
        # Le nom Pascal est complété à une longueur paire, en-tête compris.
        pos_apres_nom = pos + 6 + 1 + taille_nom
        if (taille_nom + 1) % 2:
            pos_apres_nom += 1
        if pos_apres_nom + 4 > len(bloc):
            break
        taille = struct.unpack_from(">I", bloc, pos_apres_nom)[0]
        debut = pos_apres_nom + 4
        if debut + taille > len(bloc):
            break
        if identifiant == _RESSOURCE_IPTC:
            out.extend(_lire_iim(bloc[debut : debut + taille]))
        pos = debut + taille + (taille % 2)  # complété à une longueur paire
    return out


def _lire_iim(bloc: bytes) -> List[EnregistrementIptc]:
    out: List[EnregistrementIptc] = []
    pos = 0
    while pos + 5 <= len(bloc):
        if bloc[pos] != 0x1C:
            pos += 1
            continue
        jeu = bloc[pos + 1]
        numero = bloc[pos + 2]
        taille = struct.unpack_from(">H", bloc, pos + 3)[0]
        debut = pos + 5
        if taille & 0x8000:  # jeu de données étendu : la taille est sur n octets
            n = taille & 0x7FFF
            if debut + n > len(bloc):
                break
            taille = int.from_bytes(bloc[debut : debut + n], "big")
            debut += n
        if debut + taille > len(bloc):
            break
        valeur = bloc[debut : debut + taille].decode("utf-8", errors="replace")
        out.append(EnregistrementIptc(
            jeu=jeu, numero=numero,
            libelle=_CHAMPS_IIM.get(numero, f"jeu {jeu}, champ {numero}"),
            valeur=valeur,
        ))
        pos = debut + taille
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Chaînes de caractères des en-têtes
# ─────────────────────────────────────────────────────────────────────────────

# Marqueurs qu'un éditeur laisse derrière lui. La liste ne prétend pas être
# complète, et une correspondance n'est pas une preuve de retouche : un
# convertisseur de format écrit son nom sans rien modifier du contenu visible.
MARQUEURS_LOGICIELS = (
    "Adobe", "Photoshop", "Lightroom", "GIMP", "Paint.NET", "Affinity",
    "Capture One", "darktable", "RawTherapee", "Luminar", "Snapseed",
    "PicsArt", "Canva", "Pixelmator", "ImageMagick", "libvips", "GraphicsMagick",
    "Google", "Picasa", "Instagram", "Facebook", "WhatsApp", "Signal",
    "Midjourney", "DALL", "Stable Diffusion", "Firefly", "Imagen",
)

_LONGUEUR_MIN_CHAINE = 6


@dataclass(frozen=True)
class ChaineTrouvee:
    offset: int
    encodage: str
    texte: str
    marqueur: Optional[str]


def extraire_chaines(
    donnees: bytes, longueur_min: int = _LONGUEUR_MIN_CHAINE, limite_octets: int = 262_144
) -> List[ChaineTrouvee]:
    """Relève les suites de caractères lisibles dans l'en-tête du fichier.

    Le balayage s'arrête à `limite_octets` — au-delà commencent les données
    d'image, où toute suite « lisible » est un artefact de compression et non un
    texte. Sur un JPEG, le balayage s'arrête au SOS, qui est la frontière exacte.

    Les doublons sont écartés : un même marqueur écrit par plusieurs segments
    n'apparaît qu'une fois, à sa première position.
    """
    fin = min(len(donnees), limite_octets)
    if donnees[:2] == b"\xff\xd8":
        sos = donnees.find(b"\xff\xda")
        if 0 < sos < fin:
            fin = sos
    zone = donnees[:fin]

    trouvees: List[ChaineTrouvee] = []
    vues = set()

    def ajouter(offset: int, encodage: str, texte: str) -> None:
        texte = texte.strip()
        if len(texte) < longueur_min or texte in vues:
            return
        vues.add(texte)
        marqueur = next((m for m in MARQUEURS_LOGICIELS if m.lower() in texte.lower()), None)
        trouvees.append(ChaineTrouvee(offset=offset, encodage=encodage, texte=texte, marqueur=marqueur))

    for m in re.finditer(rb"[\x20-\x7e]{%d,}" % longueur_min, zone):
        ajouter(m.start(), "ASCII", m.group().decode("ascii"))

    # UTF-16LE : un octet lisible sur deux, l'autre nul. Les XMP et certains
    # champs Windows (XPTitle, XPComment) sont écrits ainsi.
    for m in re.finditer(rb"(?:[\x20-\x7e]\x00){%d,}" % longueur_min, zone):
        ajouter(m.start(), "UTF-16LE", m.group().decode("utf-16-le", errors="replace"))

    trouvees.sort(key=lambda c: c.offset)
    return trouvees


# ─────────────────────────────────────────────────────────────────────────────
# Assemblage
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Provenance:
    """Tout ce que les en-têtes déclarent, réuni. Rien n'est vérifié ni conclu."""

    c2pa: ResultatC2PA
    xmp: Tuple[BlocXmp, ...]
    iptc: Tuple[EnregistrementIptc, ...]
    chaines: Tuple[ChaineTrouvee, ...]

    @property
    def marqueurs_logiciels(self) -> Tuple[str, ...]:
        """Les noms de logiciels relevés, sans doublon et dans l'ordre de rencontre.

        Ce n'est PAS une liste de retouches : un convertisseur de format écrit son
        nom sans toucher au contenu visible, et un éditeur peut n'en écrire aucun.
        """
        out: List[str] = []
        for c in self.chaines:
            if c.marqueur and c.marqueur not in out:
                out.append(c.marqueur)
        return tuple(out)


def analyser_provenance(chemin_ou_donnees: Union[str, Path, bytes]) -> Provenance:
    """Point d'entrée unique : tout ce que les en-têtes déclarent, d'un seul appel."""
    if isinstance(chemin_ou_donnees, (bytes, bytearray)):
        donnees = bytes(chemin_ou_donnees)
    else:
        donnees = Path(chemin_ou_donnees).read_bytes()
    return Provenance(
        c2pa=extraire_c2pa(donnees),
        xmp=tuple(extraire_xmp(donnees)),
        iptc=tuple(extraire_iptc(donnees)),
        chaines=tuple(extraire_chaines(donnees)),
    )


def empreinte_miniature(octets: bytes) -> str:
    """SHA-256 de la miniature, pour la citer dans une fiche sans la joindre."""
    return hashlib.sha256(octets).hexdigest()
