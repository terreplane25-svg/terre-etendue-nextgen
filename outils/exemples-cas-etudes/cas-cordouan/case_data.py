"""
case_data.py — données publiques sourcées pour le premier cas d'étude.

Cible : phare de Cordouan (estuaire de la Gironde, classé monument
historique, inscrit à l'UNESCO). Poste de référence : phare de la Coubre
(rive nord de l'estuaire). Aucune de ces deux valeurs n'est déduite d'une
photographie — conformément à la règle d'indépendance du §12.4 du
protocole, ce sont des fiches d'ouvrage publiques.

Chaque grandeur porte sa source telle que trouvée le 2026-09-03. Une
divergence entre deux sources est signalée explicitement plutôt que
silencieusement arbitrée — c'est la discipline même que le protocole
demande à un opérateur humain (Tableau 2, §6.2).
"""

import math
from dataclasses import dataclass


# --- Phare de Cordouan (cible) ---

CORDOUAN_LAT_DEG = 45 + 35.180 / 60          # 45°35,180' N
CORDOUAN_LON_DEG = -(1 + 10.401 / 60)        # 1°10,401' W
CORDOUAN_COORDS_SOURCE = (
    "planete-tp-plus.com/geophares, position.php?num=85 "
    "(base de géolocalisation des phares de France), consulté le 2026-09-03"
)

# Hauteur focale (feu) au-dessus de la mer : 60 m d'après Wikipédia FR ; hauteur
# totale de la tour : 67,50 m, convergente entre Wikipédia FR/EN et la notice
# Mérimée (qui indique par ailleurs une "élévation" de 69,70 m, une grandeur
# non identifiée avec certitude — probablement le sommet du lanternon incluant
# le paratonnerre, non retenue ici). C'est la hauteur TOTALE de la tour depuis
# le niveau de la mer, 67,50 m, qui est utilisée comme H (Cible.H de
# visee_optique.geometry) : c'est la grandeur la mieux corroborée par deux
# sources indépendantes.
CORDOUAN_HAUTEUR_TOTALE_M = 67.50
CORDOUAN_HAUTEUR_SOURCE = (
    "Wikipédia FR « Phare de Cordouan » et Wikipédia EN « Cordouan Lighthouse » "
    "(convergentes à 67,5 m), et notice Mérimée du ministère de la Culture "
    "(pop.culture.gouv.fr/notice/merimee/IA33001224) qui cite en outre 60 m pour "
    "la hauteur focale du feu ; consultés le 2026-09-03"
)


# --- Phare de la Coubre (poste de référence) ---

COUBRE_LAT_DEG = 45 + 41.791 / 60            # 45°41,791' N
COUBRE_LON_DEG = -(1 + 13.993 / 60)          # 1°13,993' W
COUBRE_COORDS_SOURCE = (
    "planete-tp-plus.com/geophares, position.php?num=76 "
    "(base de géolocalisation des phares de France), consulté le 2026-09-03"
)

# Divergence de source assumée et non arbitrée : la notice Mérimée
# (pop.culture.gouv.fr/notice/merimee/IA17008905) donne « hauteur au-dessus de
# la mer : 64 m » pour la tour actuelle, ce que confirme Wikipédia EN pour la
# hauteur de tour ("La Coubre is 64 metres high") ; mais Wikipédia EN cite par
# ailleurs "42 m F RW" pour un feu directionnel distinct (secteur rouge/blanc),
# probablement un feu secondaire d'alignement et non le feu principal. Cette
# incohérence n'est PAS résolue ici : le phare de la Coubre n'est pas la cible
# de ce cas (c'est Cordouan), sa hauteur ne sert qu'à situer le point de
# référence horizontal ; seule sa POSITION (lat/lon) est utilisée dans le
# calcul géodésique ci-dessous.
COUBRE_HAUTEUR_TOUR_M = 64.0
COUBRE_HAUTEUR_SOURCE_DIVERGENTE = (
    "notice Mérimée IA17008905 (64 m, hauteur de tour) vs Wikipédia EN "
    "'La Coubre Lighthouse' (64 m tour ; mais aussi '42 m F RW' pour un feu "
    "directionnel distinct, non résolu) — à vérifier auprès des Instructions "
    "Nautiques (SHOM) avant tout usage probatoire réel"
)


# --- Algorithme géodésique : Vincenty inverse (1975), sur l'ellipsoïde GRS80 ---
#
# Le Tableau 10 (§12.3, visee_optique.geodesy) exige "un algorithme publié et
# vérifié" pour la distance et l'azimut géodésiques — jamais déduits de la
# photographie. geodesy.py fournit les rayons de courbure (méridien, grande
# normale, Euler) mais ne fournit délibérément aucune routine directe/inverse
# sur l'ellipsoïde : c'est un choix d'architecture du protocole lui-même
# (§12.4, l'algorithme est externe et cité, pas réimplémenté comme une vérité
# du module). Vincenty (1975) est implémenté ici, à cet effet précis, en
# réutilisant GRS80_A / GRS80_F de visee_optique.geodesy pour qu'aucune
# incohérence d'ellipsoïde ne se glisse entre le rayon d'Euler et la distance.


def vincenty_inverse(lat1_deg, lon1_deg, lat2_deg, lon2_deg, a, f, tol=1e-12, max_iter=1000):
    """Distance et azimuts géodésiques directs (Vincenty, 1975, formule inverse).

    Retourne (distance_m, azimut_1_vers_2_deg, azimut_2_vers_1_deg). Peut ne
    pas converger pour des points quasi antipodaux — non pertinent à l'échelle
    de ce cas (13 km).
    """
    b = a * (1.0 - f)
    L = math.radians(lon2_deg - lon1_deg)
    U1 = math.atan((1.0 - f) * math.tan(math.radians(lat1_deg)))
    U2 = math.atan((1.0 - f) * math.tan(math.radians(lat2_deg)))
    sinU1, cosU1 = math.sin(U1), math.cos(U1)
    sinU2, cosU2 = math.sin(U2), math.cos(U2)

    lam = L
    for _ in range(max_iter):
        sinLam, cosLam = math.sin(lam), math.cos(lam)
        sin_sigma = math.sqrt((cosU2 * sinLam) ** 2 + (cosU1 * sinU2 - sinU1 * cosU2 * cosLam) ** 2)
        if sin_sigma == 0.0:
            return 0.0, 0.0, 0.0
        cos_sigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLam
        sigma = math.atan2(sin_sigma, cos_sigma)
        sin_alpha = cosU1 * cosU2 * sinLam / sin_sigma
        cos2_alpha = 1.0 - sin_alpha ** 2
        cos2_sigma_m = cos_sigma - 2.0 * sinU1 * sinU2 / cos2_alpha if cos2_alpha != 0.0 else 0.0
        C = f / 16.0 * cos2_alpha * (4.0 + f * (4.0 - 3.0 * cos2_alpha))
        lam_prec = lam
        lam = L + (1.0 - C) * f * sin_alpha * (
            sigma + C * sin_sigma * (cos2_sigma_m + C * cos_sigma * (-1.0 + 2.0 * cos2_sigma_m ** 2))
        )
        if abs(lam - lam_prec) < tol:
            break

    u2 = cos2_alpha * (a ** 2 - b ** 2) / b ** 2
    A = 1.0 + u2 / 16384.0 * (4096.0 + u2 * (-768.0 + u2 * (320.0 - 175.0 * u2)))
    B = u2 / 1024.0 * (256.0 + u2 * (-128.0 + u2 * (74.0 - 47.0 * u2)))
    delta_sigma = B * sin_sigma * (
        cos2_sigma_m
        + B / 4.0 * (
            cos_sigma * (-1.0 + 2.0 * cos2_sigma_m ** 2)
            - B / 6.0 * cos2_sigma_m * (-3.0 + 4.0 * sin_sigma ** 2) * (-3.0 + 4.0 * cos2_sigma_m ** 2)
        )
    )
    distance_m = b * A * (sigma - delta_sigma)
    azimut_1_vers_2 = math.degrees(math.atan2(cosU2 * sinLam, cosU1 * sinU2 - sinU1 * cosU2 * cosLam)) % 360.0
    azimut_2_vers_1 = math.degrees(math.atan2(cosU1 * sinLam, -sinU1 * cosU2 + cosU1 * sinU2 * cosLam)) % 360.0
    return distance_m, azimut_1_vers_2, azimut_2_vers_1
