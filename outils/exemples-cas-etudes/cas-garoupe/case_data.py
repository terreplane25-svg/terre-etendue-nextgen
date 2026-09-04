"""
case_data.py — données publiques sourcées pour le quatrième cas d'étude.

Poste d'observation : phare de la Garoupe, Cap d'Antibes — un promontoire réel
(103-106 m selon les sources), pas un poste au niveau de la mer comme les cas
1, 2 et 3. Cible : Monte Cinto, point culminant de la Corse (2706 m). Choisi
sur la piste Méditerranée de la feuille de route (« Pic de l'Ours / Mont Agel
vers les reliefs corses, garanties sans relief intermédiaire »), retenue
comme second candidat validé après un premier candidat écarté (Cordouan ↔
Cap Ferret, présenté ci-dessous) — voir aussi
le rapport de sélection de site (non joint à cette livraison) pour le rapport
de sélection complet.

Comme pour CAS-DEMO-SANGATTE-001, le profil intermédiaire a été vérifié par
altimétrie officielle IGN AVANT la construction de cette archive (discipline
instaurée après la correction du cas Chassiron↔Cordouan) — voir
PROFIL_CONCLUSION_DEFINITIVE plus bas.

Chaque grandeur porte sa source telle que trouvée le 2026-09-03 (§12.4 :
fiches indépendantes de toute photographie).
"""



# --- Phare de la Garoupe, Cap d'Antibes (poste d'observation) ---

GAROUPE_LAT_DEG = 43.564341
GAROUPE_LON_DEG = 7.132716
GAROUPE_COORDS_SOURCE = (
    "Mapcarta (données OpenStreetMap), phare de la Garoupe, consulté le 2026-09-03"
)

# Deux sources divergent légèrement sur l'altitude du SITE (pas de la tour, haute de 29-29,5 m) :
GAROUPE_ALTITUDE_SITE_MIN_M = 103.0
GAROUPE_ALTITUDE_SITE_MAX_M = 106.0
GAROUPE_ALTITUDE_SOURCE = (
    "Wikipédia FR « Phare de la Garoupe » et Mapcarta (données OpenStreetMap), consultés le "
    "2026-09-03 — divergence mineure (103 m contre 106 m) signalée plutôt que silencieusement "
    "arbitrée (Tableau 2, §6.2) ; la plage [103 ; 106] m est retenue pour englober les deux. Tour "
    "du phare elle-même : 29-29,5 m, NON utilisée ici (c'est l'altitude du site, pas le sommet de "
    "la tour, qui sert de repère pour un observateur posé au sol du promontoire)."
)

# --- Monte Cinto (cible) ---

CINTO_LAT_DEG = 42.37953
CINTO_LON_DEG = 8.94601
CINTO_COORDS_SOURCE = "PeakVisor, Monte Cinto, consulté le 2026-09-03"
CINTO_ALTITUDE_M = 2706.0
CINTO_ALTITUDE_SOURCE = (
    "Wikipédia EN « Monte Cinto » et PeakVisor (convergentes à 2706 m), consultés le 2026-09-03. "
    "Wikipédia EN mentionne elle-même un « panorama théorique » vers l'Europe continentale depuis "
    "ce sommet, point culminant de la Corse."
)

# --- Site écarté et pourquoi (traçabilité de la décision, §31 esprit) ---
#
# Voir le rapport de sélection de site (non joint à cette livraison) pour le détail complet.

AVERTISSEMENT_PROFIL_INTERMEDIAIRE = (
    "Comme pour CAS-DEMO-SANGATTE-001 et contrairement aux deux premiers cas, le profil "
    "intermédiaire de CE site a été vérifié AVANT la construction de cette archive — voir "
    "PROFIL_CONCLUSION_DEFINITIVE plus bas pour le résultat, positif."
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


# --- Vérification du profil intermédiaire (Tableau 10, §12.3) — altimétrie officielle IGN ---
#
# Méthode identique à celle établie pour les cas précédents : interrogation de l'API REST
# d'altimétrie de la Géoplateforme IGN (https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/
# elevation.json, ressource `ign_rge_alti_wld`), qui renvoie -99999 (à l'arrondi près) pour tout
# point hors de sa couverture terrestre, c'est-à-dire en mer. Contrôle réalisé le 2026-09-03, EN
# AMONT de la construction de cette archive, à un pas de 6 km sur toute la route (34 points, 0 à
# 198 km) — plus grossier que les cas 2 et 3 en raison de la distance bien plus grande (198 km
# contre 35-54 km), mais suffisant pour écarter tout obstacle de la taille d'une île ou d'un cap.
#
# LIMITE ASSUMÉE : résolution 6 km, pas encore affinée à 500 m sur les zones critiques (départ,
# arrivée) comme cela a été fait pour CAS-DEMO-SANGATTE-001 sur demande explicite — un affinement
# recommandé avant toute vraie campagne de mesure sur ce site (voir 70-rapport/synthese.md).

PROFIL_ELEVATIONS_IGN = (
    # (distance_m_depuis_Garoupe, elevation_m_ou_None_si_mer)
    (0, 77.19),
    (6000, None), (12000, None), (18000, None), (24000, None), (30000, None), (36000, None),
    (42000, None), (48000, None), (54000, None), (60000, None), (66000, None), (72000, None),
    (78000, None), (84000, None), (90000, None), (96000, None), (102000, None), (108000, None),
    (114000, None), (120000, None), (126000, None), (132000, None), (138000, None), (144000, None),
    (150000, None), (156000, None), (162000, None), (168000, None),
    (174000, 104.34), (180000, 146.52), (186000, 462.71), (192000, 1761.77), (197997, 2693.34),
)

PROFIL_CROISEMENTS_TERRE = ()  # aucune traversée de terre ferme intermédiaire détectée

PROFIL_CONCLUSION_DEFINITIVE = (
    "Vérification réalisée le 2026-09-03, EN AMONT de la construction de cette archive, à partir de "
    "l'altimétrie officielle IGN (RGE ALTI, API Géoplateforme data.geopf.fr — voir "
    "PROFIL_ELEVATIONS_IGN pour le relevé complet, 34 points, pas 6 km). RÉSULTAT : aucune traversée "
    "de terre ferme intermédiaire n'est détectée — mer en continu de 6 à 168 km (28 points "
    "consécutifs, soit 162 km). La terre ferme n'apparaît qu'aux deux extrémités : le départ (phare "
    "de la Garoupe, 77,19 m, cohérent avec les 103-106 m sourcés pour le site — l'écart s'explique "
    "par la résolution de grille et la position exacte interrogée sur le promontoire) et l'arrivée, "
    "progressive, en Corse (104,34 m à 174 km jusqu'à 2693,34 m au point le plus proche du sommet "
    "réel, 2706 m — écart cohérent avec la résolution de la grille RGE ALTI). CONSÉQUENCE : ce "
    "couple de sites SATISFAIT l'exigence du Tableau 10 (§12.3) d'une visée directe sur mer, à la "
    "résolution testée (6 km) — suffisante pour écarter tout cap, île ou presqu'île de taille "
    "significative en mer Ligure, mais pas pour garantir l'absence d'un écueil ponctuel : un "
    "affinement à 500 m sur les zones de départ et d'arrivée, comme celui réalisé pour "
    "CAS-DEMO-SANGATTE-001, reste recommandé avant toute vraie campagne de mesure sur ce site plus "
    "long (198 km). Ce résultat a été établi AVANT la construction de cette archive, conformément à "
    "la discipline de pré-écran mise en place après la correction du cas Chassiron↔Cordouan — voir "
    "outils/outil-bonus-pre-ecran/profil_altimetrique.py et rapport_selection_site3.md."
)
