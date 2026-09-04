"""
case_data.py — données publiques sourcées pour le second cas d'étude.

Cible : phare de Cordouan (même cible que le premier cas d'étude,
CAS-DEMO-CORDOUAN-001 — voir le dossier cas-cordouan/). Poste de référence :
phare de Chassiron, pointe nord-ouest de l'île d'Oléron. Choisi précisément
parce que la distance (54,4 km) satisfait la condition de discrimination du
§28.2 — contrairement au premier cas (13,1 km, La Coubre), où le calcul
géométrique seul montrait qu'aucune mesure n'aurait pu trancher entre les
modèles S et P.

Aucune de ces deux valeurs n'est déduite d'une photographie — conformément à
la règle d'indépendance du §12.4 du protocole, ce sont des fiches d'ouvrage
publiques.

Chaque grandeur porte sa source telle que trouvée le 2026-09-03. Une
divergence entre deux sources, ou une option écartée, est signalée
explicitement plutôt que silencieusement arbitrée — c'est la discipline même
que le protocole demande à un opérateur humain (Tableau 2, §6.2).
"""

import math


# --- Phare de Cordouan (cible) — reprise à l'identique du premier cas ---

CORDOUAN_LAT_DEG = 45 + 35.180 / 60          # 45°35,180' N
CORDOUAN_LON_DEG = -(1 + 10.401 / 60)        # 1°10,401' W
CORDOUAN_COORDS_SOURCE = (
    "planete-tp-plus.com/geophares, position.php?num=85 "
    "(base de géolocalisation des phares de France), consulté le 2026-09-03"
)

CORDOUAN_HAUTEUR_TOTALE_M = 67.50
CORDOUAN_HAUTEUR_SOURCE = (
    "Wikipédia FR « Phare de Cordouan » et Wikipédia EN « Cordouan Lighthouse » "
    "(convergentes à 67,5 m), et notice Mérimée du ministère de la Culture "
    "(pop.culture.gouv.fr/notice/merimee/IA33001224) qui cite en outre 60 m pour "
    "la hauteur focale du feu ; consultés le 2026-09-03"
)


# --- Phare de Chassiron (poste de référence) ---

CHASSIRON_LAT_DEG = 46 + 2.802 / 60           # 46°02,802' N
CHASSIRON_LON_DEG = -(1 + 24.615 / 60)        # 1°24,615' W
CHASSIRON_COORDS_SOURCE = (
    "planete-tp-plus.com/geophares (page d'index de la subdivision La Rochelle), "
    "entrée n°82 « PHARE DE CHASSIRON » (base de géolocalisation des phares de "
    "France), consulté le 2026-09-03"
)

# La hauteur propre du phare de Chassiron n'est PAS utilisée dans ce cas : comme
# pour La Coubre dans le premier cas, seul son EMPLACEMENT sert de repère
# horizontal pour un observateur posé au niveau du sol/de la dune (§ hauteur
# d'observateur h, plage [2 ; 8] m — voir run_case.py), pas au sommet de la
# tour. Aucune recherche de sa hauteur propre n'a donc été menée.

# --- Site écarté et pourquoi (traçabilité de la décision, §31 esprit) ---
#
# Phare de l'Île d'Aix (46°00,594' N, 1°10,670' W, même base géophares,
# entrée n°83) est à seulement 47,1 km de Cordouan et satisferait lui aussi
# la condition de discrimination (calcul fait, non retenu). Écarté parce que
# l'azimut Cordouan→Aix est quasi plein nord (359,6°) : la ligne droite passe
# alors très probablement au-dessus ou à proximité immédiate de l'île
# d'Oléron elle-même (dont la façade est estimée entre 45,8° et 46,0° N sur
# cette longitude), ce qui violerait la condition de visée directe sur mer du
# protocole. Chassiron est retenu à la place parce qu'il se trouve à
# l'extrémité OUEST de la même île, face au large : la ligne Cordouan→
# Chassiron reste alors plausiblement en mer ouverte, à l'ouest de la côte
# et de l'île. Ce raisonnement géographique n'est PAS une vérification
# cartographique du profil intermédiaire (voir avertissement ci-dessous et
# dans 30-donnees-externes/sources.md de l'archive) — il justifie seulement
# le choix du site parmi les candidats disponibles dans la même base.

AVERTISSEMENT_PROFIL_INTERMEDIAIRE = (
    "Le profil intermédiaire (bathymétrie/terrain entre Cordouan et Chassiron, "
    "échantillonné au pas de 500 m au plus) exigé par le Tableau 10 du "
    "protocole (§12.3) N'A PAS été vérifié pour ce cas de démonstration. Le "
    "choix de Chassiron plutôt que l'Île d'Aix repose sur un raisonnement "
    "géographique (voir ci-dessus), pas sur une vérification cartographique. "
    "Avant tout usage probatoire réel, ce profil doit être établi sur une "
    "carte marine ou un modèle numérique de terrain officiel."
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


# --- Vérification du profil intermédiaire (Tableau 10, §12.3) ---
#
# Contrôle réalisé le 2026-09-03, EN PLUS du raisonnement géographique déjà
# consigné plus haut (site écarté). Méthode : pour une sélection de points
# côtiers réels et NOMMÉS (chacun sourcé individuellement par recherche web),
# on calcule par Vincenty direct la longitude du grand cercle Chassiron→
# Cordouan à la même latitude que le point, et on compare à la longitude
# réelle du point. Un écart négatif (ligne plus à l'ouest, donc plus au
# large) signifie que la route reste en mer à cette latitude ; un écart nul
# ou positif signalerait un empiètement sur la terre ferme.
#
# LIMITE ASSUMÉE : ceci n'est PAS une carte marine SHOM ni un MNT/bathymétrie
# officiel — ces services ne sont pas atteignables depuis cette session
# (réseau restreint aux dépôts de paquets). Les coordonnées ci-dessous
# proviennent de sites cartographiques grand public (Mapcarta, à partir de
# données OpenStreetMap), avec l'arrondi de position que cela suppose
# (typiquement de l'ordre de quelques dizaines à quelques centaines de
# mètres pour un point nommé sur un site web).

PROFIL_POINTS_CONTROLE = (
    # (nom, lat_deg, lon_deg, source)
    ("La Cotinière (port, côte ouest d'Oléron)", 45.91316, -1.32751,
     "mapcarta.com/fr/W122072987 (données OpenStreetMap), consulté le 2026-09-03"),
    ("Grand-Village-Plage (côte sud-ouest d'Oléron)", 45.86439, -1.23738,
     "mapcarta.com/fr/N8026430028 (données OpenStreetMap), consulté le 2026-09-03"),
    ("Pointe de Gatseau (pointe sud d'Oléron, façade Atlantique)", 45.80106, -1.23148,
     "mapcarta.com/18378754 (données OpenStreetMap), consulté le 2026-09-03"),
    ("Pointe de la Coubre (cap continental, presqu'île d'Arvert)", 45.66968, -1.21406,
     "mapcarta.com/18392430 (données OpenStreetMap), consulté le 2026-09-03"),
)

PROFIL_BANC_COUBRE_NOTE = (
    "Un « Banc de la Coubre » (banc de sable, mapcarta.com/fr/18392434, consulté le 2026-09-03) "
    "est signalé à proximité de la route, vers 45,65°N / 1,30°O — position affichée arrondie au "
    "centième de degré (soit une incertitude de position de l'ordre du kilomètre), sans indication "
    "s'il est émergé ou submergé à marée basse. Le tableau des points de contrôle ne l'utilise "
    "donc qu'à titre de signalement, pas comme un point de contrôle fiable."
)

PROFIL_CONCLUSION_PREMIERE_PASSE = (
    "Vérification PARTIELLE réalisée le 2026-09-03 à partir de quatre points côtiers réels et "
    "individuellement sourcés (PROFIL_POINTS_CONTROLE ci-dessus). Le long de la façade ouest et de "
    "la pointe sud de l'île d'Oléron, la ligne géodésique Chassiron→Cordouan restait en mer avec une "
    "marge confortable (de 1,1 à 6,1 km au large des trois premiers points testés) à LA MÊME "
    "LATITUDE que chacun d'eux ; au niveau de la Pointe de la Coubre, l'écart n'était que d'environ "
    "150 m, jugé à l'époque non significatif. SUPERSEDÉE : cette méthode (comparaison à quelques "
    "points nommés, un par latitude) ne détecte pas un empiètement sur la terre ferme À D'AUTRES "
    "LONGITUDES le long de la route — en particulier tout empiètement près du point de départ "
    "lui-même. Voir PROFIL_CONCLUSION_DEFINITIVE ci-dessous, établie ensuite à partir d'une "
    "véritable source altimétrique officielle, qui corrige et complète ce premier résultat."
)

# --- Vérification définitive : altimétrie officielle IGN (RGE ALTI) ---
#
# Contrôle réalisé le 2026-09-03, en réponse directe à une demande de vérification sur une vraie
# carte marine SHOM. Le visualiseur SHOM lui-même n'est pas atteignable depuis cette session (page
# cartographique interactive, JavaScript, non restituable par les outils de récupération web
# disponibles ici). L'API REST d'altimétrie de la Géoplateforme IGN (data.geopf.fr), elle, l'est :
# https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json
# (paramètres lon=.., lat=.., resource=ign_rge_alti_wld, delimiter=|, zonly=true — plusieurs points
# par requête, séparés par « | »). C'est le Référentiel à Grande Échelle Altimétrique de l'IGN,
# donnée souveraine officielle française (pas une source cartographique grand public comme
# précédemment) — une autorité équivalente à un MNT officiel, même si ce n'est pas la vue SHOM elle
# -même. Le service renvoie -99999 (à l'arrondi près) pour tout point hors de la couverture
# terrestre du référentiel, c'est-à-dire en mer.
#
# Méthode : élévation interrogée tous les 1 km le long de la géodésique Chassiron→Cordouan
# (Vincenty direct, GRS80), affinée à 50-200 m près des deux transitions terre/mer trouvées.

PROFIL_ELEVATIONS_IGN = (
    # (distance_m_depuis_Chassiron, elevation_m_ou_None_si_mer)
    (0, 10.12), (1000, 7.8), (2000, 8.28), (3000, 8.75), (4000, 6.48),
    (5000, 3.77), (6000, 3.79), (7000, 4.16), (8000, 6.2), (9000, 4.08),
    (10000, 5.62), (11000, 3.92), (12000, 1.83), (13000, 5.3), (14000, 5.4),
    (15000, -0.09), (16000, None), (17000, None), (20000, None), (23000, None),
    (26000, None), (28000, None), (29000, None), (30000, None), (31000, None),
    (32000, None), (33000, None), (34000, None), (35000, None), (36000, None),
    (37000, None), (38000, None), (39000, None), (39200, 1.09), (39400, 4.18),
    (39600, 10.1), (39800, 13.76), (40000, 12.38), (40200, 6.36), (40400, 4.15),
    (40600, 4.76), (40800, 4.53), (41000, 5.54), (41200, 4.65), (41400, 6.1),
    (41600, 5.84), (41800, 1.81), (42000, 1.23), (42200, 1.11), (42400, 1.19),
    (42600, 1.45), (42800, 1.58), (43000, 1.43), (43200, 1.7), (43400, 2.29),
    (43600, 2.47), (43800, 3.74), (44000, 2.45), (44200, 6.51), (44400, 3.48),
    (44600, 0.42), (44650, None), (44700, None), (44750, None), (44800, None),
    (45000, None), (45200, None), (46000, None), (47000, None), (48000, None),
    (49000, None), (50000, None), (51000, None), (52000, None), (53000, None),
    (54000, None), (54380, None),
)

PROFIL_CROISEMENTS_TERRE = (
    ("île d'Oléron elle-même (partie nord, plus large)", 0, 15300,
     "de Chassiron (0 km, terre par construction — c'est un phare sur l'île) jusqu'à la transition "
     "terre/mer trouvée entre 15,0 km (-0,09 m, essentiellement le niveau de la mer) et 16,0 km "
     "(mer confirmée)"),
    ("presqu'île d'Arvert (région de La Tremblade / Bonne-Anse / forêt de la Coubre)", 39100, 44625,
     "transition mer→terre entre 39,0 km (mer) et 39,2 km (+1,09 m), puis terre→mer entre 44,6 km "
     "(+0,42 m) et 44,65 km (mer confirmée)"),
)

PROFIL_CONCLUSION_DEFINITIVE = (
    "Vérification DÉFINITIVE réalisée le 2026-09-03 à partir de l'altimétrie officielle IGN "
    "(RGE ALTI, API Géoplateforme data.geopf.fr — voir PROFIL_ELEVATIONS_IGN pour le relevé complet, "
    "77 points). RÉSULTAT : la ligne droite Chassiron→Cordouan traverse la terre ferme à DEUX "
    "reprises, pour un total d'environ 20,5 km sur 54,4 km (38 % de la route) — voir "
    "PROFIL_CROISEMENTS_TERRE pour le détail des deux traversées (l'île d'Oléron elle-même sur ses "
    "15 premiers kilomètres depuis Chassiron, puis la presqu'île d'Arvert vers le 40e kilomètre, "
    "sur environ 5,5 km). CONSÉQUENCE : ce couple de sites NE SATISFAIT PAS l'exigence du Tableau "
    "10 (§12.3) d'une visée directe sur mer, quel que soit le modèle de courbure retenu — un "
    "observateur posé au phare de Chassiron ne peut pas voir le phare de Cordouan : la ligne droite "
    "entre les deux est matériellement obstruée par le relief (dunes, forêt, bâti), bien avant que "
    "la courbure terrestre ou la réfraction n'entrent en jeu. Le calcul du §28.2 (condition de "
    "discrimination) reste arithmétiquement correct en tant qu'exercice géométrique abstrait sur "
    "cette distance, mais il est SANS OBJET pour ce site précis : une mesure n'y est de toute façon "
    "pas physiquement réalisable. Ce résultat CORRIGE la conclusion précédente de ce dossier "
    "(PROFIL_CONCLUSION_PREMIERE_PASSE), qui avait sous-estimé le problème faute d'une source "
    "altimétrique dense et faisant autorité. Le site Chassiron↔Cordouan est donc déclaré INVALIDE "
    "pour une vraie campagne de mesure, malgré la condition de discrimination satisfaite."
)


def calculer_verification_profil(chassiron_lat, chassiron_lon, cordouan_lat, cordouan_lon, a, f):
    """Reproduit le calcul décrit ci-dessus : pour chaque point de
    PROFIL_POINTS_CONTROLE, la longitude de la route à la même latitude, et
    l'écart en mètres au point réel (négatif = route au large, à l'ouest).
    Retourne une liste de dicts, dans l'ordre de PROFIL_POINTS_CONTROLE.
    """
    geo = vincenty_inverse(chassiron_lat, chassiron_lon, cordouan_lat, cordouan_lon, a, f)
    distance_totale, azimut = geo.distance_m, geo.azimut_depart_deg

    def lon_route_a_latitude(lat_cible):
        borne_basse, borne_haute = 0.0, distance_totale
        for _ in range(60):
            milieu = (borne_basse + borne_haute) / 2.0
            lat_milieu, _ = vincenty_direct(chassiron_lat, chassiron_lon, azimut, milieu, a, f)
            if lat_milieu > lat_cible:
                borne_basse = milieu
            else:
                borne_haute = milieu
        d_finale = (borne_basse + borne_haute) / 2.0
        lat_finale, lon_finale = vincenty_direct(chassiron_lat, chassiron_lon, azimut, d_finale, a, f)
        return d_finale, lon_finale

    resultats = []
    for nom, lat_ref, lon_ref, source in PROFIL_POINTS_CONTROLE:
        d_le_long_route, lon_route = lon_route_a_latitude(lat_ref)
        m_par_degre_lon = 111320.0 * math.cos(math.radians(lat_ref))
        ecart_m = (lon_route - lon_ref) * m_par_degre_lon
        resultats.append({
            "nom": nom, "lat_ref": lat_ref, "lon_ref": lon_ref, "source": source,
            "distance_le_long_route_m": d_le_long_route, "lon_route_meme_latitude": lon_route,
            "ecart_m": ecart_m,
        })
    return resultats
