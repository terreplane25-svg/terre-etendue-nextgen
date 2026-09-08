"""
resolution.py — Ce que les dimensions d'une image établissent (§16).

CE QUE CE MODULE FAIT, ET CE QU'IL SE REFUSE À FAIRE
───────────────────────────────────────────────────
La directive demandait un « référentiel global des définitions d'écrans » pour
rapprocher une résolution d'un appareil du marché. Ce référentiel n'existe pas
dans ce dépôt, et l'écrire de mémoire produirait des correspondances fausses
présentées comme des faits. `ECRANS_CONNUS` reste donc VIDE.

Mais le signal serait faible même vérifié, et c'est le point le plus
important : 1179 × 2556 identifie une capture d'écran d'iPhone 15 Pro autant
que n'importe quelle image recadrée à ces dimensions. Un rapprochement par la
résolution ne prouve rien sur l'origine ; il désigne au mieux une famille.

CE QUI EST VÉRIFIABLE, ET QUI VAUT MIEUX
────────────────────────────────────────
Le rapport d'aspect EXACT, en fraction réduite : c'est de l'arithmétique, sans
référentiel. 4032 × 3024 donne 4:3, 1920 × 1080 donne 16:9. Le rapport dit la
FAMILLE de la source mieux que la résolution ne dit l'appareil.

Et surtout la COHÉRENCE entre deux grandeurs que le fichier porte séparément :

  · les dimensions LUES DANS LES OCTETS — marqueur SOF d'un JPEG, IHDR d'un
    PNG, boîte `ispe` d'un HEIF. C'est une mesure ;
  · les dimensions DÉCLARÉES dans l'EXIF, tags PixelXDimension et
    PixelYDimension. C'est une déclaration.

Un écart entre les deux ÉTABLIT que le fichier a été redimensionné ou recadré
sans que la métadonnée suive. C'est un signal fort, gratuit, et que rien ne
lisait jusqu'ici — le relevé préférait même la déclaration à la mesure, ce qui
masquait l'écart au lieu de le montrer.

L'ALIGNEMENT SUR LES BLOCS JPEG
───────────────────────────────
Un JPEG code par blocs de 8 × 8 pixels, groupés en unités de 8 ou 16 pixels
selon le sous-échantillonnage. Des dimensions qui ne sont pas des multiples de
cette unité signifient que l'encodeur a stocké une image dont le bord est
partiel — ce qui arrive à tout recadrage. C'est faible, et rendu comme tel :
la plupart des appareils produisent des dimensions alignées, mais l'inverse
n'établit rien de précis.
"""

from dataclasses import dataclass
from math import gcd
from typing import Dict, Optional, Tuple

__all__ = [
    "ECRANS_CONNUS",
    "DEFINITIONS_NOMMEES",
    "MOTIF_AUCUN_ECRAN",
    "MOTIF_DENOMINATION",
    "MOTIF_ALIGNEMENT",
    "Resolution",
    "analyser_resolution",
    "rapport_exact",
]

#: Le référentiel des écrans d'appareils. VIDE, et c'est délibéré.
#:
#: Chaque entrée serait : (largeur, hauteur) → nom d'un appareil du marché. Le
#: remplir demande un corpus vérifié, collecté modèle par modèle. Y écrire
#: « 1179 × 2556 = iPhone 15 Pro » de mémoire produirait une identification
#: fausse présentée comme un fait — et une identification fausse dans un
#: dossier probatoire coûte plus cher que pas d'identification du tout.
ECRANS_CONNUS: Dict[Tuple[int, int], str] = {}

#: Les dénominations d'USAGE de quelques définitions. Ce ne sont PAS des
#: identifications d'appareil : ce sont les noms sous lesquels ces dimensions
#: circulent, et ils n'attribuent rien.
#:
#: Leur valeur probatoire est nulle et le module le dit. Ils servent seulement
#: à ce qu'un lecteur reconnaisse « 1920 × 1080 » sans compter les zéros.
DEFINITIONS_NOMMEES: Dict[Tuple[int, int], str] = {
    (640, 480): "VGA",
    (800, 600): "SVGA",
    (1024, 768): "XGA",
    (1280, 720): "720p",
    (1280, 1024): "SXGA",
    (1366, 768): "WXGA",
    (1600, 900): "HD+",
    (1920, 1080): "1080p",
    (2048, 1080): "2K DCI",
    (2560, 1440): "1440p",
    (3840, 2160): "2160p (UHD)",
    (4096, 2160): "4K DCI",
    (7680, 4320): "4320p (UHD-2)",
}

MOTIF_AUCUN_ECRAN = (
    "Aucun rapprochement avec un appareil : il n'existe pas de référentiel "
    "vérifié des définitions d'écrans dans ce dépôt, et en écrire un de mémoire "
    "produirait des correspondances fausses présentées comme des faits. Le "
    "signal serait d'ailleurs faible même vérifié — une résolution de "
    "1179 × 2556 identifie une capture d'écran d'iPhone 15 Pro autant que "
    "n'importe quelle image recadrée à ces dimensions. Ce qui est rendu à la "
    "place se vérifie : le rapport d'aspect exact, et la cohérence entre les "
    "dimensions mesurées et celles que l'EXIF déclare."
)

MOTIF_DENOMINATION = (
    "Une dénomination d'usage, sans valeur probatoire. Elle dit sous quel nom "
    "ces dimensions circulent, jamais d'où vient l'image : un cliché recadré "
    "à 1920 × 1080 porte le même nom qu'une capture d'écran."
)

MOTIF_ALIGNEMENT = (
    "Un JPEG code par blocs de 8 × 8 pixels, groupés en unités de 8 ou 16 "
    "selon le sous-échantillonnage. Des dimensions non alignées sur cette "
    "unité signifient que le bord de l'image est un bloc partiel, ce qui "
    "arrive à tout recadrage. Le signal est faible dans les deux sens : la "
    "plupart des appareils produisent des dimensions alignées, et un "
    "alignement n'établit pas l'absence de recadrage."
)


def rapport_exact(largeur: int, hauteur: int) -> Tuple[int, int]:
    """Le rapport d'aspect en fraction réduite. Arithmétique, sans référentiel.

    3024 × 4032 rend (3, 4) et non (4, 3) : l'ordre suit les dimensions
    reçues, parce qu'une image portrait n'est pas une image paysage et que
    normaliser les deux au même rapport perdrait l'orientation.
    """
    if largeur <= 0 or hauteur <= 0:
        raise ValueError("Les dimensions doivent être strictement positives.")
    d = gcd(largeur, hauteur)
    return (largeur // d, hauteur // d)


@dataclass(frozen=True)
class Resolution:
    """Ce que les dimensions d'une image permettent de dire."""

    #: Les dimensions LUES DANS LES OCTETS. C'est la mesure.
    largeur_mesuree: Optional[int]
    hauteur_mesuree: Optional[int]
    #: Les dimensions DÉCLARÉES dans l'EXIF. C'est une déclaration.
    largeur_declaree: Optional[int]
    hauteur_declaree: Optional[int]
    #: Vrai quand les deux coïncident, faux quand elles diffèrent, None quand
    #: l'une des deux manque — jamais faux par défaut.
    dimensions_coherentes: Optional[bool]
    #: Ce que l'écart établit, quand il y en a un.
    motif_ecart: Optional[str]
    #: Le rapport d'aspect exact des dimensions MESURÉES, en fraction réduite.
    rapport: Optional[Tuple[int, int]]
    rapport_decimal: Optional[float]
    orientation: Optional[str]
    megapixels: Optional[float]
    #: La dénomination d'usage, si les dimensions en portent une. Sans valeur
    #: probatoire — voir MOTIF_DENOMINATION.
    denomination: Optional[str]
    #: L'unité d'alignement JPEG respectée, ou None. 16 implique 8.
    alignement_jpeg: Optional[int]
    #: L'appareil rapproché. Toujours None : le référentiel est vide.
    ecran_rapproche: Optional[str] = None
    motif_aucun_ecran: str = MOTIF_AUCUN_ECRAN


def analyser_resolution(
    largeur_mesuree: Optional[int],
    hauteur_mesuree: Optional[int],
    largeur_declaree: Optional[int] = None,
    hauteur_declaree: Optional[int] = None,
) -> Resolution:
    """Confronte les dimensions mesurées aux dimensions déclarées.

    Les deux jeux sont rendus SÉPARÉMENT, et jamais l'un à la place de
    l'autre : c'est leur écart qui porte l'information, et le masquer en
    n'affichant qu'une valeur reviendrait à jeter le seul signal gratuit que
    ce fichier offre.
    """
    mesuree = (largeur_mesuree, hauteur_mesuree)
    declaree = (largeur_declaree, hauteur_declaree)
    a_mesure = all(x is not None and x > 0 for x in mesuree)
    a_declare = all(x is not None and x > 0 for x in declaree)

    coherentes: Optional[bool] = None
    motif_ecart: Optional[str] = None
    if a_mesure and a_declare:
        coherentes = mesuree == declaree
        if not coherentes:
            motif_ecart = (
                "Les octets portent %d × %d, l'EXIF déclare %d × %d. L'écart "
                "ÉTABLIT que le fichier a été redimensionné ou recadré sans "
                "que la métadonnée suive : les deux grandeurs sont écrites à "
                "des moments différents, par des outils différents. Ce qu'il "
                "n'établit pas, c'est lequel des deux est le bon, ni qui a "
                "fait la modification."
                % (largeur_mesuree, hauteur_mesuree,
                   largeur_declaree, hauteur_declaree)
            )

    rapport = None
    rapport_decimal = None
    orientation = None
    megapixels = None
    denomination = None
    alignement = None
    if a_mesure:
        assert largeur_mesuree is not None and hauteur_mesuree is not None
        rapport = rapport_exact(largeur_mesuree, hauteur_mesuree)
        rapport_decimal = largeur_mesuree / hauteur_mesuree
        if largeur_mesuree > hauteur_mesuree:
            orientation = "paysage"
        elif largeur_mesuree < hauteur_mesuree:
            orientation = "portrait"
        else:
            orientation = "carré"
        megapixels = (largeur_mesuree * hauteur_mesuree) / 1e6
        # La dénomination se cherche dans les deux sens : une capture portrait
        # de 1080 × 1920 porte le même nom que son pendant paysage.
        denomination = (DEFINITIONS_NOMMEES.get((largeur_mesuree, hauteur_mesuree))
                        or DEFINITIONS_NOMMEES.get((hauteur_mesuree, largeur_mesuree)))
        if largeur_mesuree % 16 == 0 and hauteur_mesuree % 16 == 0:
            alignement = 16
        elif largeur_mesuree % 8 == 0 and hauteur_mesuree % 8 == 0:
            alignement = 8

    return Resolution(
        largeur_mesuree=largeur_mesuree if a_mesure else None,
        hauteur_mesuree=hauteur_mesuree if a_mesure else None,
        largeur_declaree=largeur_declaree if a_declare else None,
        hauteur_declaree=hauteur_declaree if a_declare else None,
        dimensions_coherentes=coherentes,
        motif_ecart=motif_ecart,
        rapport=rapport,
        rapport_decimal=rapport_decimal,
        orientation=orientation,
        megapixels=megapixels,
        denomination=denomination,
        alignement_jpeg=alignement,
        # Le référentiel est vide : le rapprochement ne peut rien rendre.
        ecran_rapproche=ECRANS_CONNUS.get((largeur_mesuree or 0, hauteur_mesuree or 0)),
    )
