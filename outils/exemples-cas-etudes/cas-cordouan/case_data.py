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


# --- Géodésie : importée du paquet, jamais recopiée ---
#
# `vincenty_inverse` et `vincenty_direct` vivaient ici en copie locale, hors de
# toute couverture de test. Elles sont maintenant dans `visee_optique.geodesy`,
# où vingt-six tests les éprouvent — dont deux qui les confrontent à des
# résultats obtenus sans Vincenty : la distance sur l'équateur, qui vaut
# analytiquement a·Δλ, et l'arc méridien, obtenu par quadrature.
#
# `vincenty_inverse` rend un GeodesiqueInverse (distance_m, azimut_depart_deg,
# azimut_arrivee_deg, iterations, converge) et non plus un triplet, et lève
# plutôt que de rendre le dernier itéré quand elle ne converge pas.
from visee_optique.geodesy import (  # noqa: E402
    GRS80_A,
    GRS80_F,
    vincenty_direct,
    vincenty_inverse,
)


