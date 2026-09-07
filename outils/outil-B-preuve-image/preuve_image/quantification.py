"""
quantification.py — Les tables de quantification d'un JPEG (§16, §20).

CE QUE CE MODULE ÉTABLIT, ET CE QU'IL N'ÉTABLIT PAS
───────────────────────────────────────────────────
Une image JPEG porte, dans ses segments DQT, les tables qui ont servi à la
quantifier. Ce sont des données EXACTES, présentes dans tout JPEG, et elles
survivent à la purge de l'EXIF : un fichier dont toutes les métadonnées ont été
retirées porte encore ses tables. C'est ce qui en fait un objet intéressant.

CE QUI EST ÉTABLI :
  · les tables elles-mêmes, telles qu'écrites, et leur empreinte ;
  · le facteur de qualité au sens de la bibliothèque de référence (IJG), quand
    les tables en dérivent — avec l'écart résiduel, qui dit à quel point ;
  · le nombre de tables, leur précision, et le sous-échantillonnage chromatique
    lu dans le segment SOF ;
  · le fait qu'une image a été RÉENCODÉE quand ses tables ne correspondent à
    aucun facteur IJG entier, ce qui est le cas des encodeurs propriétaires.

CE QUI N'EST PAS ÉTABLI, ET NE PEUT PAS L'ÊTRE ICI :
  · la MARQUE de l'appareil ou du logiciel. Associer une signature de
    quantification à « Canon DIGIC » ou « algorithme WhatsApp » demande un
    corpus de fichiers réels, collectés et vérifiés, appareil par appareil et
    version par version. Ce paquet n'en a pas. Un registre vide et extensible
    est fourni — `SIGNATURES_CONNUES` — plutôt qu'une table inventée : une
    correspondance affirmée sans corpus derrière serait une conjecture
    présentée comme un fait, et c'est exactement ce que le protocole interdit.

L'empreinte des tables est donc rendue pour être COMPARÉE : deux fichiers dont
les tables ont la même empreinte sont sortis de la même chaîne d'encodage, aux
mêmes réglages. C'est un rapprochement entre deux fichiers qu'on a tous les
deux, jamais une identification contre une base qu'on n'a pas.
"""

import hashlib
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

__all__ = [
    "QuantificationError",
    "TableQuantification",
    "AnalyseQuantification",
    "analyser_quantification",
    "TABLE_LUMINANCE_ANNEXE_K",
    "TABLE_CHROMINANCE_ANNEXE_K",
    "table_ijg",
    "qualite_ijg_estimee",
    "SIGNATURES_CONNUES",
    "MOTIF_AUCUNE_SIGNATURE",
]


class QuantificationError(ValueError):
    """Flux JPEG malformé, ou dépourvu de table de quantification."""


#: Table de luminance de l'annexe K de la norme ISO/IEC 10918-1, en ordre
#: zigzag. C'est la table dont dérivent, par mise à l'échelle, celles de la
#: quasi-totalité des encodeurs — la référence de l'IJG (libjpeg) comme celle
#: de la plupart des appareils.
TABLE_LUMINANCE_ANNEXE_K = (
    16, 11, 12, 14, 12, 10, 16, 14, 13, 14, 18, 17, 16, 19, 24, 40,
    26, 24, 22, 22, 24, 49, 35, 37, 29, 40, 58, 51, 61, 60, 57, 51,
    56, 55, 64, 72, 92, 78, 64, 68, 87, 69, 55, 56, 80, 109, 81, 87,
    95, 98, 103, 104, 103, 62, 77, 113, 121, 112, 100, 120, 92, 101, 103, 99,
)

#: Table de chrominance de la même annexe.
TABLE_CHROMINANCE_ANNEXE_K = (
    17, 18, 18, 24, 21, 24, 47, 26, 26, 47, 99, 66, 56, 66, 99, 99,
    99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99,
    99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99,
    99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99,
)

#: Le registre des signatures reconnues. VIDE, et c'est délibéré.
#:
#: Le remplir demande un corpus de fichiers réels, collectés appareil par
#: appareil et version par version, dont on puisse dire d'où ils viennent.
#: Chaque entrée serait : empreinte des tables → (producteur, ce qui l'établit).
#: Y écrire des correspondances de mémoire produirait des identifications
#: fausses présentées comme des faits — et une identification fausse dans un
#: dossier probatoire coûte plus cher que pas d'identification du tout.
SIGNATURES_CONNUES: Dict[str, Tuple[str, str]] = {}

MOTIF_AUCUNE_SIGNATURE = (
    "Aucun rapprochement : le registre des signatures est vide. Le remplir "
    "demande un corpus de fichiers réels dont la provenance est établie, "
    "appareil par appareil et version par version. L'empreinte ci-dessus reste "
    "utilisable pour COMPARER deux fichiers que vous avez tous les deux — "
    "des tables identiques sortent de la même chaîne d'encodage aux mêmes "
    "réglages — mais elle n'identifie rien contre une base qu'on n'a pas."
)


@dataclass(frozen=True)
class TableQuantification:
    """Une table DQT, telle qu'elle est écrite dans le fichier.

    `valeurs` est en ordre ZIGZAG, celui du fichier, et non en ordre de
    balayage : les réordonner ici ferait diverger l'empreinte de celle qu'un
    autre outil calculerait sur les mêmes octets.
    """

    identifiant: int
    precision_bits: int
    valeurs: Tuple[int, ...]
    offset: int

    @property
    def empreinte(self) -> str:
        return hashlib.sha256(
            ",".join(str(v) for v in self.valeurs).encode("ascii")
        ).hexdigest()

    @property
    def somme(self) -> int:
        """La somme des coefficients. Grossière, mais elle ordonne les qualités."""
        return sum(self.valeurs)


@dataclass(frozen=True)
class AnalyseQuantification:
    """Ce que les tables d'un JPEG permettent de dire."""

    tables: Tuple[TableQuantification, ...]
    #: L'empreinte de l'ENSEMBLE des tables, dans l'ordre du fichier. C'est
    #: elle qui sert à rapprocher deux fichiers.
    empreinte_ensemble: str
    #: Le facteur de qualité IJG le plus proche, et l'écart qui reste.
    qualite_ijg: Optional[int]
    #: Nombre de coefficients qui diffèrent de la table IJG reconstruite.
    ecart_a_ijg: Optional[int]
    #: Vrai quand les tables coïncident EXACTEMENT avec un facteur IJG entier.
    conforme_ijg: bool
    #: Le sous-échantillonnage chromatique lu dans le SOF, ex. « 4:2:0 ».
    sous_echantillonnage: Optional[str]
    #: Progressif ou séquentiel : un réencodage change souvent ce choix.
    progressif: Optional[bool]
    largeur: Optional[int] = None
    hauteur: Optional[int] = None
    composantes: int = 0
    #: Le rapprochement, s'il y en a un. Voir SIGNATURES_CONNUES.
    signature: Optional[Tuple[str, str]] = None
    motif_absence_signature: str = MOTIF_AUCUNE_SIGNATURE
    marqueurs: Tuple[str, ...] = field(default_factory=tuple)


def table_ijg(qualite: int, base: Tuple[int, ...] = TABLE_LUMINANCE_ANNEXE_K) -> Tuple[int, ...]:
    """La table que produit la bibliothèque de référence IJG pour ce facteur.

    L'algorithme est celui de `jpeg_set_quality` : le facteur est converti en
    une échelle, puis chaque coefficient de la table de l'annexe K est mis à
    l'échelle et borné à [1 ; 255]. Il est reproduit ici plutôt qu'appelé, pour
    que la comparaison ne dépende d'aucune bibliothèque installée.
    """
    if not 1 <= qualite <= 100:
        raise QuantificationError("Le facteur de qualité IJG est compris entre 1 et 100.")
    echelle = 5000 // qualite if qualite < 50 else 200 - qualite * 2
    return tuple(
        min(255, max(1, (v * echelle + 50) // 100))
        for v in base
    )


def qualite_ijg_estimee(
    valeurs: Tuple[int, ...], base: Tuple[int, ...] = TABLE_LUMINANCE_ANNEXE_K
) -> Tuple[Optional[int], Optional[int]]:
    """Le facteur IJG dont la table est la plus proche, et l'écart qui reste.

    L'écart est le nombre de coefficients qui DIFFÈRENT, pas une distance :
    zéro veut dire que la table est exactement celle de ce facteur, et tout le
    reste veut dire qu'elle n'en vient pas — ce qui est le cas des encodeurs
    d'appareils photo et de plusieurs services de messagerie.

    Rendre un facteur « approché » sans cet écart laisserait croire à une
    identification là où il n'y a qu'une ressemblance.
    """
    if len(valeurs) != 64:
        return None, None
    meilleur, ecart_min = None, None
    for q in range(1, 101):
        candidate = table_ijg(q, base)
        ecart = sum(1 for a, b in zip(valeurs, candidate) if a != b)
        if ecart_min is None or ecart < ecart_min:
            meilleur, ecart_min = q, ecart
            if ecart == 0:
                break
    return meilleur, ecart_min


#: Les marqueurs JPEG qu'on nomme. Leur présence renseigne sur la chaîne : un
#: JPEG progressif sort rarement d'un appareil photo.
_MARQUEURS = {
    0xC0: "SOF0 (séquentiel, Huffman)",
    0xC1: "SOF1 (séquentiel étendu)",
    0xC2: "SOF2 (progressif)",
    0xC3: "SOF3 (sans perte)",
    0xC4: "DHT (tables de Huffman)",
    0xC9: "SOF9 (arithmétique)",
    0xCC: "DAC (codage arithmétique)",
    0xDB: "DQT (tables de quantification)",
    0xDD: "DRI (intervalle de redémarrage)",
    0xDA: "SOS (début du balayage)",
    0xE0: "APP0 (JFIF)",
    0xE1: "APP1 (EXIF ou XMP)",
    0xE2: "APP2 (ICC ou MPF)",
    0xEC: "APP12 (Ducky, Picture Info)",
    0xED: "APP13 (Photoshop IRB)",
    0xEE: "APP14 (Adobe)",
    0xFE: "COM (commentaire)",
}


def _sous_echantillonnage(composantes: List[Tuple[int, int, int]]) -> Optional[str]:
    """Déduit la notation « 4:x:x » des facteurs d'échantillonnage du SOF.

    La notation usuelle se lit sur les facteurs de la composante de luminance,
    rapportés à ceux de la chrominance. Elle n'a de sens qu'à trois composantes ;
    au-delà ou en deçà, on rend None plutôt qu'une notation qui n'existe pas.
    """
    if len(composantes) != 3:
        return None
    hy, vy = composantes[0][1], composantes[0][2]
    hc, vc = composantes[1][1], composantes[1][2]
    if hc == 0 or vc == 0:
        return None
    rh, rv = hy // hc, vy // vc
    return {
        (1, 1): "4:4:4", (2, 1): "4:2:2", (2, 2): "4:2:0",
        (1, 2): "4:4:0", (4, 1): "4:1:1", (4, 2): "4:1:0",
    }.get((rh, rv))


def analyser_quantification(donnees: bytes) -> AnalyseQuantification:
    """Lit les tables DQT d'un JPEG et ce que le SOF déclare.

    Le balayage s'arrête au SOS : au-delà commencent les données comprimées,
    où toute séquence d'octets peut ressembler à un marqueur.
    """
    if len(donnees) < 4 or donnees[0] != 0xFF or donnees[1] != 0xD8:
        raise QuantificationError("Fichier non reconnu comme JPEG (SOI absent).")

    tables: List[TableQuantification] = []
    marqueurs: List[str] = []
    composantes: List[Tuple[int, int, int]] = []
    largeur = hauteur = None
    progressif = None

    pos = 2
    while pos + 4 <= len(donnees):
        if donnees[pos] != 0xFF:
            break
        m = donnees[pos + 1]
        if m == 0xD8 or 0xD0 <= m <= 0xD7:
            pos += 2
            continue
        if m == 0xD9:
            break
        longueur = struct.unpack_from(">H", donnees, pos + 2)[0]
        if longueur < 2 or pos + 2 + longueur > len(donnees):
            break
        corps = donnees[pos + 4 : pos + 2 + longueur]
        nom = _MARQUEURS.get(m, f"0x{m:02X}")
        if nom not in marqueurs:
            marqueurs.append(nom)

        if m == 0xDB:
            # Un même segment DQT peut porter plusieurs tables à la suite.
            p = 0
            while p < len(corps):
                entete = corps[p]
                precision = 16 if (entete >> 4) else 8
                identifiant = entete & 0x0F
                n = 64 * (2 if precision == 16 else 1)
                if p + 1 + n > len(corps):
                    break
                brut = corps[p + 1 : p + 1 + n]
                if precision == 16:
                    valeurs = struct.unpack(f">{64}H", brut)
                else:
                    valeurs = tuple(brut)
                tables.append(TableQuantification(
                    identifiant=identifiant, precision_bits=precision,
                    valeurs=tuple(valeurs), offset=pos + 4 + p,
                ))
                p += 1 + n
        elif m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC9) and len(corps) >= 6:
            progressif = m == 0xC2
            hauteur, largeur = struct.unpack_from(">HH", corps, 1)
            nb = corps[5]
            for i in range(nb):
                q = 6 + i * 3
                if q + 3 > len(corps):
                    break
                composantes.append((corps[q], corps[q + 1] >> 4, corps[q + 1] & 0x0F))
        elif m == 0xDA:
            break

        pos += 2 + longueur

    if not tables:
        raise QuantificationError(
            "Aucune table de quantification (DQT) trouvée avant le début du balayage. "
            "Un JPEG en porte toujours : le fichier est tronqué, ou ce n'en est pas un."
        )

    # L'empreinte porte sur TOUTES les tables, dans l'ordre du fichier : deux
    # images de même table de luminance mais de chrominance différente ne
    # viennent pas de la même chaîne, et les confondre serait un faux
    # rapprochement.
    ensemble = ";".join(
        f"{t.identifiant}:{t.precision_bits}:" + ",".join(str(v) for v in t.valeurs)
        for t in tables
    )
    empreinte_ensemble = hashlib.sha256(ensemble.encode("ascii")).hexdigest()

    # Le facteur IJG se lit sur la table de luminance, celle d'identifiant 0.
    luminance = next((t for t in tables if t.identifiant == 0), tables[0])
    qualite, ecart = qualite_ijg_estimee(luminance.valeurs)

    return AnalyseQuantification(
        tables=tuple(tables),
        empreinte_ensemble=empreinte_ensemble,
        qualite_ijg=qualite,
        ecart_a_ijg=ecart,
        conforme_ijg=ecart == 0,
        sous_echantillonnage=_sous_echantillonnage(composantes),
        progressif=progressif,
        largeur=largeur,
        hauteur=hauteur,
        composantes=len(composantes),
        signature=SIGNATURES_CONNUES.get(empreinte_ensemble),
        marqueurs=tuple(marqueurs),
    )
