"""
geodesy.py — Rayon d'Euler, conversion d'altitude et sources géodésiques (§12).

§12.1 distingue trois surfaces qui ne coïncident pas : l'ellipsoïde, sur
lequel se calcule la géodésique ; le géoïde, auquel se rapportent les
altitudes ; et la sphère de référence de geometry.py, qui n'est qu'une
commodité de calcul. Confondre géoïde et ellipsoïde vaut plusieurs
dizaines de mètres d'erreur sur une altitude, donc plusieurs mètres sur
la hauteur occultée.

§12.2 est la contrainte structurante de ce module : la sphère de rayon
R1 = 6 371 008,8 m (§4.1) est une commodité, jamais la valeur à utiliser
pour une observation réelle. Le rayon de courbure réel de l'ellipsoïde
dépend de la latitude ET de l'azimut de la visée — du rayon méridien à
l'équateur (~6 335,4 km) à la grande normale au pôle (~6 399,6 km), un
écart de ~1 %, supérieur à l'erreur de l'approximation corde-arc du
§9.4. Le protocole exige donc le rayon de courbure normal à l'azimut de
la visée (rayon d'Euler), calculé à la latitude du trajet — jamais R1.
C'est `rayon_euler` ci-dessous qu'il faut passer à geometry.py et
refraction.rayon_effectif, jamais `geometry.IUGG_R1`.

§12.3 (Tableau 10) est repris comme donnée de référence, pas comme
validation : ce sont des « valeurs indicatives », le protocole le dit
lui-même — chaque observation reporte l'incertitude réelle de sa propre
source, jamais une borne imposée par ce module.

§12.4 pose une règle de processus, pas de calcul : aucune grandeur
géodésique n'est déduite de la photographie analysée. `GrandeurGeodesique`
en porte un garde-fou textuel — imparfait par nature, une chaîne de
caractères ne prouve pas une provenance — documenté comme tel.
"""

import math
from dataclasses import dataclass
from typing import Tuple

__all__ = [
    "GeodesyError",
    "GRS80_A",
    "GRS80_F",
    "GRS80_B",
    "GRS80_E2",
    "rayon_meridien",
    "rayon_grande_normale",
    "rayon_euler",
    "GeodesiqueInverse",
    "vincenty_inverse",
    "vincenty_direct",
    "ConversionGeoide",
    "altitude_depuis_hauteur_ellipsoidale",
    "PosteGeodesique",
    "TABLEAU_10",
    "incertitude_typique",
    "GrandeurGeodesique",
]


class GeodesyError(ValueError):
    """Domaine invalide pour un calcul géodésique, ou grandeur déposée sans provenance (§12)."""


# Ellipsoïde GRS80 (§4.1, Moritz 2000 ; §12.2). a : demi-grand axe ; f : aplatissement ;
# b : demi-petit axe ; e2 : excentricité au carré. (2a+b)/3 redonne IUGG_R1 de geometry.py
# à la précision du dixième de mètre — une vérification faite dans les tests, pas supposée ici.
GRS80_A = 6_378_137.0  # m
GRS80_F = 1.0 / 298.257222101
GRS80_B = GRS80_A * (1.0 - GRS80_F)  # m
GRS80_E2 = GRS80_F * (2.0 - GRS80_F)


def _valider_latitude(latitude_deg: float) -> float:
    if not (-90.0 <= latitude_deg <= 90.0):
        raise GeodesyError("La latitude doit être comprise entre -90° et 90°.")
    return math.radians(latitude_deg)


def _valider_azimut(azimut_deg: float) -> float:
    if not (0.0 <= azimut_deg < 360.0):
        raise GeodesyError("L'azimut doit être compris entre 0° (inclus) et 360° (exclu).")
    return math.radians(azimut_deg)


def rayon_meridien(latitude_deg: float, a: float = GRS80_A, e2: float = GRS80_E2) -> float:
    """M(φ) = a(1-e²) / (1-e² sin²φ)^(3/2) — rayon de courbure méridien (§12.2).

    Minimal à l'équateur (~6 335,4 km pour GRS80), maximal aux pôles.
    """
    phi = _valider_latitude(latitude_deg)
    sin_phi = math.sin(phi)
    return a * (1.0 - e2) / (1.0 - e2 * sin_phi**2) ** 1.5


def rayon_grande_normale(latitude_deg: float, a: float = GRS80_A, e2: float = GRS80_E2) -> float:
    """N(φ) = a / √(1 - e² sin²φ) — grande normale (§12.2).

    Vaut a à l'équateur, ~6 399,6 km au pôle pour GRS80.
    """
    phi = _valider_latitude(latitude_deg)
    sin_phi = math.sin(phi)
    return a / math.sqrt(1.0 - e2 * sin_phi**2)


def rayon_euler(latitude_deg: float, azimut_deg: float, a: float = GRS80_A, e2: float = GRS80_E2) -> float:
    """Rayon de courbure normal à l'azimut de la visée — rayon d'Euler (§12.2).

    1/R = cos²(azimut)/M(φ) + sin²(azimut)/N(φ), calculé à la latitude du
    trajet et à l'azimut géodésique de la visée. C'est ce rayon, et non
    IUGG_R1 (§4.1), qu'il faut passer à geometry.py et à
    refraction.rayon_effectif pour une observation réelle (objection
    n°1, §31 : substituer R1 au rayon d'Euler peut changer la hauteur
    occultée de plusieurs pour cent).
    """
    phi = _valider_latitude(latitude_deg)
    az = _valider_azimut(azimut_deg)
    M = a * (1.0 - e2) / (1.0 - e2 * math.sin(phi) ** 2) ** 1.5
    N = a / math.sqrt(1.0 - e2 * math.sin(phi) ** 2)
    denominateur = (math.cos(az) ** 2) / M + (math.sin(az) ** 2) / N
    return 1.0 / denominateur


# --- §12.3 : la géodésique elle-même ---
#
# Le Tableau 10 exige que la distance soit « calculée par un algorithme publié
# et vérifiable » sur l'ellipsoïde, et l'azimut « issu du même calcul ». C'est
# Vincenty (1975) qui est employé ici.
#
# Ces deux fonctions vivaient jusqu'ici en cinq copies hors du paquet — dans le
# pré-écran altimétrique et dans chacun des quatre cas d'étude — donc hors de
# toute couverture de test, alors que ce sont elles qui produisent le D et
# l'azimut dont dépendent le rayon d'Euler et toute la géométrie. Les cinq
# copies étaient numériquement identiques ; le risque était latent, pas réalisé.
# Elles sont ramenées ici, testées, et une différence a été introduite à
# dessein : la non-convergence n'est plus silencieuse.


@dataclass(frozen=True)
class GeodesiqueInverse:
    """Résultat du problème géodésique inverse (§12.3).

    `azimut_arrivee_deg` est l'azimut de la visée AU POINT D'ARRIVÉE, dans
    le même sens de parcours — α₂ chez Vincenty — et non l'azimut de
    retour de la cible vers l'observateur. Les cinq copies antérieures le
    nommaient `azimut_2_vers_1`, ce qui annonce le gisement inverse : sur
    l'équateur vers l'est, elles retournaient 90° sous un nom qui promet
    270°. Qui s'en servait comme d'un azimut de retour se trompait d'un
    demi-tour. Le gisement de retour, si on le veut, est cette valeur
    plus 180° modulo 360.

    `iterations` et `converge` sont exposés parce que Vincenty ne converge
    pas pour les couples quasi-antipodaux : une valeur retournée après
    épuisement du compteur n'est pas une distance, c'est le dernier itéré.
    Les copies antérieures sortaient de la boucle sans le signaler.
    """

    distance_m: float
    azimut_depart_deg: float
    azimut_arrivee_deg: float
    iterations: int
    converge: bool


def vincenty_inverse(
    lat1_deg: float,
    lon1_deg: float,
    lat2_deg: float,
    lon2_deg: float,
    a: float = GRS80_A,
    f: float = GRS80_F,
    tol: float = 1e-12,
    max_iter: int = 200,
) -> GeodesiqueInverse:
    """Distance et azimuts géodésiques sur l'ellipsoïde, méthode de Vincenty (1975).

    Lève GeodesyError si l'itération n'a pas convergé dans `max_iter`
    tours — cas des couples quasi-antipodaux, où la formule est connue
    pour échouer. Aucune valeur approchée n'est retournée en silence.
    """
    for nom, val in (("lat1", lat1_deg), ("lat2", lat2_deg)):
        if not (-90.0 <= val <= 90.0):
            raise GeodesyError(f"{nom} hors domaine : {val}°. Attendu entre -90 et 90.")
    b = a * (1.0 - f)
    L = math.radians(lon2_deg - lon1_deg)
    U1 = math.atan((1.0 - f) * math.tan(math.radians(lat1_deg)))
    U2 = math.atan((1.0 - f) * math.tan(math.radians(lat2_deg)))
    sinU1, cosU1 = math.sin(U1), math.cos(U1)
    sinU2, cosU2 = math.sin(U2), math.cos(U2)

    lam = L
    converge = False
    tours = 0
    sin_sigma = cos_sigma = sigma = cos2_alpha = cos2_sigma_m = 0.0
    sinLam = cosLam = 0.0
    for tours in range(1, max_iter + 1):
        sinLam, cosLam = math.sin(lam), math.cos(lam)
        sin_sigma = math.sqrt(
            (cosU2 * sinLam) ** 2 + (cosU1 * sinU2 - sinU1 * cosU2 * cosLam) ** 2
        )
        if sin_sigma == 0.0:
            # Points confondus : distance nulle, azimut indéterminé — et le
            # dire, plutôt que de retourner un azimut de 0° qui aurait l'air
            # d'une direction mesurée.
            return GeodesiqueInverse(0.0, float("nan"), float("nan"), tours, True)
        cos_sigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLam
        sigma = math.atan2(sin_sigma, cos_sigma)
        sin_alpha = cosU1 * cosU2 * sinLam / sin_sigma
        cos2_alpha = 1.0 - sin_alpha**2
        cos2_sigma_m = (
            cos_sigma - 2.0 * sinU1 * sinU2 / cos2_alpha if cos2_alpha != 0.0 else 0.0
        )
        C = f / 16.0 * cos2_alpha * (4.0 + f * (4.0 - 3.0 * cos2_alpha))
        lam_prec = lam
        lam = L + (1.0 - C) * f * sin_alpha * (
            sigma
            + C
            * sin_sigma
            * (cos2_sigma_m + C * cos_sigma * (-1.0 + 2.0 * cos2_sigma_m**2))
        )
        if abs(lam - lam_prec) < tol:
            converge = True
            break

    if not converge:
        raise GeodesyError(
            f"Vincenty n'a pas convergé en {max_iter} itérations : le couple est "
            "probablement quasi-antipodal. Aucune distance n'est retournée."
        )

    u2 = cos2_alpha * (a**2 - b**2) / b**2
    A = 1.0 + u2 / 16384.0 * (4096.0 + u2 * (-768.0 + u2 * (320.0 - 175.0 * u2)))
    B = u2 / 1024.0 * (256.0 + u2 * (-128.0 + u2 * (74.0 - 47.0 * u2)))
    delta_sigma = B * sin_sigma * (
        cos2_sigma_m
        + B
        / 4.0
        * (
            cos_sigma * (-1.0 + 2.0 * cos2_sigma_m**2)
            - B
            / 6.0
            * cos2_sigma_m
            * (-3.0 + 4.0 * sin_sigma**2)
            * (-3.0 + 4.0 * cos2_sigma_m**2)
        )
    )
    return GeodesiqueInverse(
        distance_m=b * A * (sigma - delta_sigma),
        azimut_depart_deg=math.degrees(
            math.atan2(cosU2 * sinLam, cosU1 * sinU2 - sinU1 * cosU2 * cosLam)
        )
        % 360.0,
        azimut_arrivee_deg=math.degrees(
            math.atan2(cosU1 * sinLam, -sinU1 * cosU2 + cosU1 * sinU2 * cosLam)
        )
        % 360.0,
        iterations=tours,
        converge=True,
    )


def vincenty_direct(
    lat1_deg: float,
    lon1_deg: float,
    azimut1_deg: float,
    distance_m: float,
    a: float = GRS80_A,
    f: float = GRS80_F,
    tol: float = 1e-12,
    max_iter: int = 200,
) -> Tuple[float, float]:
    """Point atteint depuis (lat1, lon1) en suivant azimut1 sur distance_m (§12.3).

    Sert à échantillonner le profil intermédiaire du Tableau 10, pas à
    calculer la distance ou l'azimut — ceux-là viennent de la formule
    inverse ci-dessus.
    """
    if distance_m < 0.0:
        raise GeodesyError("La distance ne peut pas être négative.")
    lat1 = math.radians(lat1_deg)
    az1 = math.radians(_valider_azimut(azimut1_deg % 360.0) * 180.0 / math.pi)
    b = a * (1.0 - f)
    U1 = math.atan((1.0 - f) * math.tan(lat1))
    sigma1 = math.atan2(math.tan(U1), math.cos(az1))
    sinAlpha = math.cos(U1) * math.sin(az1)
    cos2Alpha = 1.0 - sinAlpha**2
    u2 = cos2Alpha * (a**2 - b**2) / b**2
    A = 1.0 + u2 / 16384.0 * (4096.0 + u2 * (-768.0 + u2 * (320.0 - 175.0 * u2)))
    B = u2 / 1024.0 * (256.0 + u2 * (-128.0 + u2 * (74.0 - 47.0 * u2)))
    sigma = distance_m / (b * A)
    two_sigma_m = 0.0
    for _ in range(max_iter):
        two_sigma_m = 2.0 * sigma1 + sigma
        delta_sigma = B * math.sin(sigma) * (
            math.cos(two_sigma_m)
            + B
            / 4.0
            * (
                math.cos(sigma) * (-1.0 + 2.0 * math.cos(two_sigma_m) ** 2)
                - B
                / 6.0
                * math.cos(two_sigma_m)
                * (-3.0 + 4.0 * math.sin(sigma) ** 2)
                * (-3.0 + 4.0 * math.cos(two_sigma_m) ** 2)
            )
        )
        sigma_prec = sigma
        sigma = distance_m / (b * A) + delta_sigma
        if abs(sigma - sigma_prec) < tol:
            break
    lat2 = math.atan2(
        math.sin(U1) * math.cos(sigma) + math.cos(U1) * math.sin(sigma) * math.cos(az1),
        (1.0 - f)
        * math.sqrt(
            sinAlpha**2
            + (
                math.sin(U1) * math.sin(sigma)
                - math.cos(U1) * math.cos(sigma) * math.cos(az1)
            )
            ** 2
        ),
    )
    lam = math.atan2(
        math.sin(sigma) * math.sin(az1),
        math.cos(U1) * math.cos(sigma) - math.sin(U1) * math.sin(sigma) * math.cos(az1),
    )
    C = f / 16.0 * cos2Alpha * (4.0 + f * (4.0 - 3.0 * cos2Alpha))
    L = lam - (1.0 - C) * f * sinAlpha * (
        sigma
        + C
        * math.sin(sigma)
        * (
            math.cos(two_sigma_m)
            + C * math.cos(sigma) * (-1.0 + 2.0 * math.cos(two_sigma_m) ** 2)
        )
    )
    return math.degrees(lat2), math.degrees(math.radians(lon1_deg) + L)


# --- §12.1 : géoïde vs ellipsoïde ---


@dataclass(frozen=True)
class ConversionGeoide:
    """L'ondulation du géoïde à retrancher d'une hauteur ellipsoïdale (§12.1, §12.3).

    ondulation_m : N, positif si le géoïde est au-dessus de l'ellipsoïde
                   à cette position (convention EGM2008 usuelle).
    modele, source : jamais omis — l'écart géoïde-ellipsoïde atteint
                      plusieurs dizaines de mètres, sa provenance doit
                      être traçable comme toute autre donnée externe
                      (Tableau 2, §6.2).
    """

    ondulation_m: float
    modele: str
    source: str

    def __post_init__(self):
        if not self.modele.strip():
            raise GeodesyError("Le modèle de géoïde utilisé doit être nommé (ex. EGM2008).")
        if not self.source.strip():
            raise GeodesyError("La source de l'ondulation du géoïde doit être citée.")


def altitude_depuis_hauteur_ellipsoidale(
    hauteur_ellipsoidale_m: float, conversion: ConversionGeoide
) -> float:
    """h_orthométrique = h_ellipsoïdale - N (§12.1).

    Ne jamais utiliser une hauteur ellipsoïdale GNSS brute comme altitude
    (§12.1 : « le confondre avec zéro est une erreur de plusieurs
    dizaines de mètres sur l'altitude, donc de plusieurs mètres sur la
    hauteur occultée » — objection n°3, §31).
    """
    return hauteur_ellipsoidale_m - conversion.ondulation_m


# --- §12.3 : sources et précisions typiques (Tableau 10) — référence, pas validation ---


@dataclass(frozen=True)
class PosteGeodesique:
    """Une ligne du Tableau 10 : poste, source admise, référentiel, incertitude typique.

    Les bornes d'incertitude sont indicatives (le protocole le dit
    lui-même, légende du Tableau 10) : ce module ne les impose à
    aucune donnée, il les expose pour comparaison.
    """

    nom: str
    source_admise: str
    referentiel: str
    incertitude_min: float
    incertitude_max: float
    unite: str


TABLEAU_10: Tuple[PosteGeodesique, ...] = (
    PosteGeodesique(
        "Position horizontale de l'observateur",
        "récepteur GNSS bi-fréquence en post-traitement, ou positionnement sur un point géodésique publié",
        "ITRF / ETRS89",
        0.1, 5.0, "m",
    ),
    PosteGeodesique(
        "Altitude de l'observateur",
        "hauteur ellipsoïdale GNSS convertie en altitude par un modèle de géoïde publié, plus la hauteur mesurée de l'axe optique au-dessus du sol",
        "ellipsoïde GRS80 → géoïde",
        0.3, 2.0, "m",
    ),
    PosteGeodesique(
        "Position de la cible",
        "fiche officielle de l'ouvrage, relevé géodésique, base cartographique nationale ; pour un navire, position horodatée d'un registre",
        "ITRF / système national",
        1.0, 50.0, "m",
    ),
    PosteGeodesique(
        "Altitude de la base de la cible",
        "modèle numérique de terrain officiel ; pour un ouvrage côtier ou un navire, niveau d'eau à l'heure exacte, corrigé de la marée et du zéro hydrographique",
        "altitude normale ou orthométrique",
        0.2, 2.0, "m",
    ),
    PosteGeodesique(
        "Hauteur de la cible",
        "plan coté, fiche technique du constructeur, spécification de navire ; jamais déduite de la photographie",
        "—",
        0.1, 1.0, "m",
    ),
    PosteGeodesique(
        "Distance",
        "géodésique sur l'ellipsoïde calculée par un algorithme publié et vérifié",
        "GRS80 / WGS84",
        1.0, 10.0, "m",
    ),
    PosteGeodesique(
        "Azimut",
        "azimut géodésique direct issu du même calcul",
        "GRS80 / WGS84",
        0.01, 0.01, "°",
    ),
    PosteGeodesique(
        "Profil intermédiaire",
        "échantillonnage du modèle de terrain et de la bathymétrie le long de la géodésique, au pas de 500 m au plus",
        "id.",
        2.0, 10.0, "m",
    ),
)


def incertitude_typique(nom: str) -> Tuple[float, float]:
    """(min, max) indicatifs du Tableau 10 pour le poste nommé — comparaison, pas seuil."""
    for poste in TABLEAU_10:
        if poste.nom == nom:
            return (poste.incertitude_min, poste.incertitude_max)
    noms_connus = ", ".join(p.nom for p in TABLEAU_10)
    raise GeodesyError(f"Poste géodésique inconnu : « {nom} ». Postes du Tableau 10 : {noms_connus}.")


# --- §12.4 : règle d'indépendance ---


_MOTIFS_SOURCE_INTERDITE = ("photo", "image", "cliché", "photographie")


@dataclass(frozen=True)
class GrandeurGeodesique:
    """Une grandeur géodésique établie indépendamment de la photographie analysée (§12.4).

    Le contrôle sur `source` est un garde-fou textuel, pas une preuve de
    provenance : une chaîne de caractères ne peut pas établir qu'une
    valeur n'a pas été lue dans l'image. Il attrape la violation la plus
    directe (déclarer une source qui nomme la photographie elle-même),
    rien de plus — la garantie réelle reste la discipline humaine que le
    §12.4 impose.
    """

    nom: str
    valeur: float
    unite: str
    referentiel: str
    source: str
    incertitude: float

    def __post_init__(self):
        if not self.nom.strip():
            raise GeodesyError("Une grandeur géodésique doit être nommée.")
        if not self.unite.strip():
            raise GeodesyError(f"« {self.nom} » doit préciser son unité.")
        if not self.referentiel.strip():
            raise GeodesyError(f"« {self.nom} » doit préciser son référentiel (§12.1).")
        if not self.source.strip():
            raise GeodesyError(f"« {self.nom} » doit citer sa source (Tableau 2, §6.2).")
        if self.incertitude < 0:
            raise GeodesyError("Une incertitude ne peut pas être négative.")
        source_normalisee = self.source.lower()
        if any(motif in source_normalisee for motif in _MOTIFS_SOURCE_INTERDITE):
            raise GeodesyError(
                f"« {self.nom} » : la source « {self.source} » évoque la photographie analysée — "
                "interdit par la règle d'indépendance du §12.4."
            )
