"""
optique.py — Étalonnage spatial : d'une ligne de pixels à un angle (§14, §15).

Ce module convertit une position verticale dans le fichier image en angle
d'élévation depuis l'axe optique. C'est la seule opération de la chaîne qui
dépende de l'appareil ; tout le reste est de la géométrie.

TROIS CORRECTIONS AU CAHIER DES CHARGES
───────────────────────────────────────
Le cahier des charges initial donnait :

    r_angulaire (rad/px) = (taille_capteur_mm / largeur_image_px) / f_mm
    Echelle (m/px à D)   = D · tan(r_angulaire)
    angle = N_px · r_angulaire

Trois choses ne tiennent pas.

1. `largeur_image_px` doit être la définition NATIVE du capteur, pas celle du
   fichier livré. Un recadrage ne change pas le pas pixel : les pixels
   conservent leur identité, il y en a seulement moins. Une image recadrée de
   8000 px à 2000 px traitée avec sa largeur finale donne un pas pixel quatre
   fois trop grand, donc un angle quatre fois trop grand, donc une hauteur
   émergente quatre fois trop grande. C'est l'erreur la plus coûteuse de la
   chaîne, et elle est silencieuse. Le pas pixel est ici calculé depuis la
   définition native, et le rééchantillonnage éventuel est déclaré à part.

2. Le point principal n'est au centre du fichier que si l'image n'a pas été
   recadrée. Un recadrage le déplace, et l'angle mesuré depuis le mauvais
   centre est faux. `Cadrage` porte donc l'origine du recadrage dans le repère
   natif. Quand elle n'est pas connue, l'angle n'est pas refusé : il est rendu
   avec l'enveloppe de toutes les positions que le point principal peut
   occuper, ce qui est plus utile qu'un refus et plus honnête qu'un centre
   supposé.

3. `angle = N_px · r_angulaire` est la forme paraxiale. La projection
   rectilinéaire donne exactement

       angle(y₁, y₂) = arctan(u₁·p/f) − arctan(u₂·p/f)

   avec u mesuré depuis le point principal. Les deux formes sont calculées et
   leur écart est rendu : il est négligeable au centre du champ et cesse de
   l'être vers les bords, ce qui est précisément ce qu'un opérateur doit voir
   plutôt que supposer.

Aucune de ces trois corrections ne change le résultat d'une photographie non
recadrée dont le sujet est au centre. Elles changent le résultat de toutes les
autres, qui sont la majorité des visées à fort grossissement.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

INDISPONIBLE = "indisponible"

# Largeur du format 24×36, par définition de la « focale équivalent 35 mm ».
LARGEUR_24x36_MM = 36.0


class MetrologieError(ValueError):
    """Domaine invalide pour un calcul de métrologie d'image."""


@dataclass(frozen=True)
class Capteur:
    """Le capteur tel qu'il a enregistré la scène, avant tout traitement.

    largeur_mm : largeur physique de la surface sensible.
    largeur_native_px, hauteur_native_px : définition du capteur en sortie
        de boîtier, AVANT recadrage et rééchantillonnage. C'est cette
        définition, et non celle du fichier livré, qui fixe le pas pixel.
    """

    largeur_mm: float
    largeur_native_px: int
    hauteur_native_px: int

    def __post_init__(self):
        if self.largeur_mm <= 0:
            raise MetrologieError("La largeur du capteur doit être strictement positive.")
        if self.largeur_native_px <= 0 or self.hauteur_native_px <= 0:
            raise MetrologieError("La définition native doit être strictement positive.")

    @property
    def pas_pixel_mm(self) -> float:
        """p = largeur_mm / largeur_native_px.

        Les pixels sont supposés carrés — vrai de tous les capteurs
        photographiques courants. Ce pas vaut donc aussi verticalement, ce
        qui autorise à ne demander que la largeur du capteur.
        """
        return self.largeur_mm / self.largeur_native_px


def capteur_equivalent_35mm(largeur_native_px: int, hauteur_native_px: int) -> Capteur:
    """Capteur fictif de 36 mm de large, à employer avec une focale équivalent 35 mm.

    Une « focale équivalent 35 mm » est par construction la focale qui, sur un
    format 24×36, donnerait le même champ. Le couple (36 mm, f_eq) rend donc le
    même angle que le couple (largeur réelle, f_réelle), sans avoir à connaître
    la taille du capteur. C'est la seule voie ouverte quand l'EXIF ne donne que
    FocalLengthIn35mmFilm.
    """
    return Capteur(LARGEUR_24x36_MM, largeur_native_px, hauteur_native_px)


@dataclass(frozen=True)
class Objectif:
    """focale_mm : distance focale réelle, dans la même convention que le capteur.

    Avec `capteur_equivalent_35mm`, c'est la focale équivalente qu'il faut
    passer ici — jamais la focale réelle, sous peine de mélanger les deux
    conventions et de fausser l'angle du rapport des deux formats.
    """

    focale_mm: float

    def __post_init__(self):
        if self.focale_mm <= 0:
            raise MetrologieError("La focale doit être strictement positive.")


@dataclass(frozen=True)
class Cadrage:
    """Ce que le fichier livré est, relativement au capteur natif (§15).

    largeur_px, hauteur_px : dimensions du fichier livré.
    origine_x_px, origine_y_px : coin haut-gauche du recadrage dans le repère
        natif, ou None si le recadrage a eu lieu sans être documenté.
    largeur_recadree_px, hauteur_recadree_px : dimensions du recadrage AVANT
        rééchantillonnage, en pixels natifs. Égales aux dimensions livrées
        quand il n'y a pas eu de rééchantillonnage.

    Le facteur de rééchantillonnage est déduit, jamais saisi : le déduire
    interdit qu'il contredise les dimensions déclarées.
    """

    largeur_px: int
    hauteur_px: int
    largeur_recadree_px: int
    hauteur_recadree_px: int
    origine_x_px: Optional[int] = None
    origine_y_px: Optional[int] = None

    def __post_init__(self):
        for nom in ("largeur_px", "hauteur_px", "largeur_recadree_px", "hauteur_recadree_px"):
            if getattr(self, nom) <= 0:
                raise MetrologieError(f"{nom} doit être strictement positif.")
        rx = self.largeur_px / self.largeur_recadree_px
        ry = self.hauteur_px / self.hauteur_recadree_px
        # Un rééchantillonnage anisotrope déforme les angles verticaux et
        # horizontaux différemment : la chaîne ne le modélise pas, elle le
        # refuse plutôt que d'appliquer un facteur moyen qui n'existe pas.
        if abs(rx - ry) > 1e-6 * max(rx, ry):
            raise MetrologieError(
                "Rééchantillonnage anisotrope (%.6f en largeur, %.6f en hauteur) : "
                "les angles verticaux et horizontaux ne sont plus dans le même "
                "rapport, la mesure n'est pas définie." % (rx, ry)
            )
        if (self.origine_x_px is None) != (self.origine_y_px is None):
            raise MetrologieError(
                "L'origine du recadrage se déclare entière ou pas du tout : "
                "une seule des deux coordonnées ne suffit pas."
            )
        if self.origine_x_px is not None and (self.origine_x_px < 0 or self.origine_y_px < 0):
            raise MetrologieError("L'origine du recadrage ne peut pas être négative.")

    @property
    def facteur_reechantillonnage(self) -> float:
        """ρ = pixels livrés / pixels natifs employés. > 1 : image agrandie."""
        return self.largeur_px / self.largeur_recadree_px

    @property
    def recadree(self) -> bool:
        return (self.largeur_recadree_px, self.hauteur_recadree_px) != (
            self.largeur_px,
            self.hauteur_px,
        ) or (self.origine_x_px not in (None, 0) or self.origine_y_px not in (None, 0))

    @property
    def point_principal_connu(self) -> bool:
        """Vrai si l'ordonnée du point principal dans le fichier livré est déterminée."""
        return self.origine_y_px is not None


def cadrage_plein_capteur(capteur: Capteur) -> Cadrage:
    """Le cas courant : le fichier est la sortie native, sans recadrage ni rééchantillonnage."""
    return Cadrage(
        largeur_px=capteur.largeur_native_px,
        hauteur_px=capteur.hauteur_native_px,
        largeur_recadree_px=capteur.largeur_native_px,
        hauteur_recadree_px=capteur.hauteur_native_px,
        origine_x_px=0,
        origine_y_px=0,
    )


def pas_pixel_livre_mm(capteur: Capteur, cadrage: Cadrage) -> float:
    """Pas pixel effectif DANS LE FICHIER LIVRÉ.

    Le recadrage ne change pas le pas ; le rééchantillonnage le divise par ρ.
    Un fichier agrandi deux fois a des pixels deux fois plus fins — sans porter
    pour autant deux fois plus d'information (§15).
    """
    return capteur.pas_pixel_mm / cadrage.facteur_reechantillonnage


def pas_angulaire_rad(capteur: Capteur, cadrage: Cadrage, objectif: Objectif) -> float:
    """r = arctan(p_livré / f) — angle sous-tendu par un pixel SUR L'AXE.

    Le cahier des charges donnait p/f ; c'est le développement au premier ordre
    de cette arctangente. L'écart relatif vaut r²/3, soit 8·10⁻¹² pour un pixel
    de 1″ : indiscernable. La forme exacte est employée quand même, parce
    qu'elle ne coûte rien et qu'elle évite d'avoir à justifier une
    approximation de plus.

    Cette valeur ne vaut QUE sur l'axe optique : hors axe, l'angle par pixel
    décroît en cos². C'est `angle_entre_lignes` qui fait le calcul juste.
    """
    return math.atan(pas_pixel_livre_mm(capteur, cadrage) / objectif.focale_mm)


def ordonnee_point_principal_px(capteur: Capteur, cadrage: Cadrage) -> float:
    """Ordonnée du point principal dans le repère du fichier livré.

    Le point principal est au centre du capteur natif. Après recadrage à
    l'origine y₀ et rééchantillonnage ρ, il se trouve en
    (h_native/2 − y₀)·ρ dans le fichier livré — valeur qui peut tomber hors
    de l'image, ce qui est un fait, pas une erreur : un recadrage en bord de
    champ rejette l'axe optique hors du cadre.
    """
    if not cadrage.point_principal_connu:
        raise MetrologieError(
            "Origine du recadrage non déclarée : l'ordonnée du point principal "
            "est " + INDISPONIBLE + ". Employer `angle_entre_lignes_enveloppe`, "
            "qui borne le résultat au lieu de supposer un centre."
        )
    centre_natif = capteur.hauteur_native_px / 2.0
    return (centre_natif - cadrage.origine_y_px) * cadrage.facteur_reechantillonnage


def angle_entre_lignes(
    y_haut: float,
    y_bas: float,
    capteur: Capteur,
    cadrage: Cadrage,
    objectif: Objectif,
) -> float:
    """Angle vertical exact entre deux lignes du fichier, en radians.

    Projection rectilinéaire, exacte :

        θ = arctan(u_haut·p/f) − arctan(u_bas·p/f)

    où u est l'écart au point principal, compté positif vers le haut de
    l'image (donc u = y_pp − y, l'ordonnée croissant vers le bas dans un
    fichier image). Le résultat est positif quand y_haut < y_bas, c'est-à-dire
    quand la première ligne est effectivement au-dessus de la seconde.
    """
    p = pas_pixel_livre_mm(capteur, cadrage)
    y_pp = ordonnee_point_principal_px(capteur, cadrage)
    f = objectif.focale_mm
    return math.atan((y_pp - y_haut) * p / f) - math.atan((y_pp - y_bas) * p / f)


def angle_entre_lignes_paraxial(
    y_haut: float,
    y_bas: float,
    capteur: Capteur,
    cadrage: Cadrage,
    objectif: Objectif,
) -> float:
    """La forme du cahier des charges : θ ≈ (y_bas − y_haut) · p/f.

    Conservée pour être comparée à la forme exacte, jamais pour s'y substituer.
    Elle ne dépend pas du point principal, ce qui est à la fois sa commodité et
    sa faiblesse : elle reste calculable quand le recadrage n'est pas
    documenté, mais elle surestime l'angle dès que le sujet s'éloigne de l'axe.
    """
    p = pas_pixel_livre_mm(capteur, cadrage)
    return (y_bas - y_haut) * p / objectif.focale_mm


def angle_entre_lignes_enveloppe(
    y_haut: float,
    y_bas: float,
    capteur: Capteur,
    cadrage: Cadrage,
    objectif: Objectif,
) -> Tuple[float, float]:
    """Bornes de l'angle quand l'ordonnée du point principal est inconnue.

    L'angle rectilinéaire entre deux lignes est maximal quand le segment est
    centré sur l'axe et décroît strictement à mesure qu'il s'en éloigne. Le
    point principal, lui, n'est pas libre : le recadrage a une origine y₀
    comprise entre 0 et (h_native − h_recadrée), ce qui confine son ordonnée
    dans le fichier livré à

        y_pp = (h_native/2 − y₀)·ρ  ∈  [(h_rec − h_native/2)·ρ ; (h_native/2)·ρ]

    Les bornes de l'angle sont donc atteintes soit au centrage — s'il est dans
    ce domaine — soit à l'une des deux extrémités du domaine.

    Rendu en (borne_basse, borne_haute). Quand le point principal est connu,
    les deux bornes valent l'angle exact.
    """
    if cadrage.point_principal_connu:
        a = angle_entre_lignes(y_haut, y_bas, capteur, cadrage, objectif)
        return (a, a)

    if y_bas <= y_haut:
        raise MetrologieError(
            "y_haut doit être strictement au-dessus de y_bas (ordonnée plus petite)."
        )

    p = pas_pixel_livre_mm(capteur, cadrage)
    f = objectif.focale_mm
    rho = cadrage.facteur_reechantillonnage

    def angle_pour(y_pp: float) -> float:
        return math.atan((y_pp - y_haut) * p / f) - math.atan((y_pp - y_bas) * p / f)

    y_pp_min = (cadrage.hauteur_recadree_px - capteur.hauteur_native_px / 2.0) * rho
    y_pp_max = (capteur.hauteur_native_px / 2.0) * rho
    centre = (y_haut + y_bas) / 2.0

    candidats = [y_pp_min, y_pp_max]
    if y_pp_min <= centre <= y_pp_max:
        candidats.append(centre)
    valeurs = [angle_pour(y) for y in candidats]
    return (min(valeurs), max(valeurs))


def echelle_m_par_px(distance_m: float, capteur: Capteur, cadrage: Cadrage, objectif: Objectif) -> float:
    """Mètres par pixel à la distance donnée, SUR L'AXE : D · tan(r).

    Grandeur de tableau de bord, pas grandeur de calcul. L'inversion du
    coefficient de réfraction travaille en angles et ne passe jamais par cette
    conversion : une échelle en mètres par pixel n'est constante ni sur le
    champ (elle décroît hors axe) ni en profondeur (la cible n'est pas plane).
    Elle sert à se représenter ce qu'un pixel vaut, et à rien d'autre.
    """
    if distance_m <= 0:
        raise MetrologieError("La distance doit être strictement positive.")
    return distance_m * math.tan(pas_angulaire_rad(capteur, cadrage, objectif))


def resolution_angulaire_limite_rad(longueur_onde_m: float, diametre_pupille_m: float) -> float:
    """Critère de Rayleigh : θ = 1,22 · λ / D — limite de diffraction (§20).

    Sert à répondre à une question que le comptage de pixels ne peut pas
    trancher : deux lignes séparées de trois pixels sont-elles deux détails
    enregistrés, ou un seul détail étalé par l'optique ? Sous cette limite, un
    écart de pixels n'est plus une mesure. Ce n'est pas un critère de rejet
    automatique : c'est le nombre à mettre en regard du pas angulaire.
    """
    if longueur_onde_m <= 0 or diametre_pupille_m <= 0:
        raise MetrologieError("λ et le diamètre de pupille doivent être strictement positifs.")
    return 1.22 * longueur_onde_m / diametre_pupille_m
