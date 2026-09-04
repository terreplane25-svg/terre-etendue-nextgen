"""
case_data.py — données publiques sourcées pour le troisième cas d'étude.

Poste d'observation : Digue de Sangatte (Pas-de-Calais), front de mer, à un
point d'altitude sourcée quasi nulle. Cible : phare de South Foreland /
falaises de Douvres (White Cliffs of Dover), Angleterre. Choisi au terme
d'une recherche explicite d'un couple « Manche/Atlantique près du niveau de
la mer » (demande de l'utilisateur), après l'écart de deux autres candidats :

  - Cap Gris-Nez ↔ South Foreland (33,9 km) : Gris-Nez est en réalité un cap
    élevé (falaise ~45 m). Avec h reflétant honnêtement cette altitude, la
    condition de discrimination du §28.2 n'est PAS satisfaite (delta quasi
    nul) — voir /home/claude/outils-verification/rapport_selection_site3.md
    pour le détail complet. Écarté pour cette raison, avant toute
    construction d'archive.
  - Cordouan ↔ Cap Ferret (104,7 km) : le pré-écran altimétrique a montré que
    la ligne droite remonte en réalité la presqu'île du Cap Ferret elle-même
    sur ses ~15 derniers km. Écarté avant toute construction d'archive
    (même rapport).

Digue de Sangatte est retenue à la place : un point sourcé à 2 m d'altitude
(Cirkwi), sur le cordon dunaire bas entre Cap Blanc-Nez et Cap Gris-Nez —
un poste authentiquement proche du niveau de la mer, contrairement à
Gris-Nez, avec une condition de discrimination satisfaite (voir
run_case.py) ET un profil intermédiaire confirmé 100 % maritime par
altimétrie officielle IGN, à résolution 2 km sur le corps de la route et
500 m aux deux extrémités (Tableau 10, §12.3) — voir plus bas.

Chaque grandeur porte sa source telle que trouvée le 2026-09-03 (§12.4 :
fiches indépendantes de toute photographie).
"""

import math


# --- Digue de Sangatte (poste d'observation) ---

SANGATTE_LAT_DEG = 50.94642
SANGATTE_LON_DEG = 1.75305
SANGATTE_COORDS_SOURCE = (
    "Cirkwi, point d'intérêt « Digue de Sangatte » "
    "(cirkwi.com/fr/point-interet/3648388-digue-de-sangatte), consulté le 2026-09-03"
)
SANGATTE_ALTITUDE_SITE_M = 2.0
SANGATTE_ALTITUDE_SOURCE = (
    "Cirkwi (point ci-dessus, altitude déclarée 2 m) ; convergent avec l'altitude moyenne de la "
    "commune de Sangatte (4 m, Wikipédia EN « Sangatte » ; 5 m, base Comersis, "
    "france.comersis.com/la-commune-de-Sangatte-62774-62.html), consultés le 2026-09-03. "
    "Wikipédia FR confirme par ailleurs que le point culminant de la commune (151 m) appartient "
    "au Cap Blanc-Nez, à 4 km au sud-ouest — la digue elle-même est sur le cordon dunaire bas."
)

# --- Phare de South Foreland / falaises de Douvres (cible) ---

SOUTHFORELAND_LAT_DEG = 51.13152
SOUTHFORELAND_LON_DEG = 1.338825
SOUTHFORELAND_COORDS_SOURCE = (
    "Mapcarta (données OpenStreetMap / National Trust, phare de South Foreland), "
    "consulté le 2026-09-03"
)
SOUTHFORELAND_HAUTEUR_TOTALE_M = 110.0
SOUTHFORELAND_HAUTEUR_SOURCE = (
    "Wikipédia EN « White Cliffs of Dover » : hauteur 110 m (350 pieds), falaises s'élevant "
    "directement depuis le niveau de la mer ; consulté le 2026-09-03. Le phare de South Foreland "
    "lui-même est un repère ponctuel sur ces falaises, pas la source de la hauteur retenue ici — "
    "c'est la falaise, pas la tour du phare, qui joue le rôle de cible occultée par la courbure."
)

# --- Sites écartés et pourquoi (traçabilité de la décision, §31 esprit) ---
#
# Voir /home/claude/outils-verification/rapport_selection_site3.md pour le détail complet
# (Cap Gris-Nez ↔ South Foreland, écarté pour discrimination insuffisante à h réaliste ;
# Cordouan ↔ Cap Ferret, écarté pour traversée de la presqu'île elle-même).

AVERTISSEMENT_PROFIL_INTERMEDIAIRE = (
    "Contrairement aux deux premiers cas d'étude, le profil intermédiaire de CE site a été vérifié "
    "AVANT la construction de cette archive (discipline instaurée après la correction du cas "
    "Chassiron↔Cordouan) — voir PROFIL_CONCLUSION_DEFINITIVE plus bas pour le résultat, positif."
)


# --- Algorithme géodésique : Vincenty inverse et direct (1975), ellipsoïde GRS80 ---
#
# Repris à l'identique des deux premiers cas d'étude (cas-cordouan/, cas-chassiron/) — pour que ce
# troisième dossier reste autonome et rejouable sans dépendre des précédents.


def vincenty_inverse(lat1_deg, lon1_deg, lat2_deg, lon2_deg, a, f, tol=1e-12, max_iter=1000):
    """Distance et azimuts géodésiques (Vincenty, 1975, formule inverse).

    Retourne (distance_m, azimut_1_vers_2_deg, azimut_2_vers_1_deg).
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


def vincenty_direct(lat1_deg, lon1_deg, azimut1_deg, distance_m, a, f):
    """Point géodésique atteint depuis (lat1, lon1) en suivant azimut1 sur distance_m mètres
    (Vincenty, 1975, formule directe). Utilisé uniquement pour interpoler des points le long de la
    route Sangatte→South Foreland (vérification du profil intermédiaire, Tableau 10, §12.3) — jamais
    pour la distance/l'azimut eux-mêmes, qui restent calculés par la formule inverse ci-dessus.
    """
    lat1 = math.radians(lat1_deg)
    az1 = math.radians(azimut1_deg)
    b = a * (1.0 - f)
    U1 = math.atan((1.0 - f) * math.tan(lat1))
    sigma1 = math.atan2(math.tan(U1), math.cos(az1))
    sinAlpha = math.cos(U1) * math.sin(az1)
    cos2Alpha = 1.0 - sinAlpha ** 2
    u2 = cos2Alpha * (a ** 2 - b ** 2) / b ** 2
    A = 1.0 + u2 / 16384.0 * (4096.0 + u2 * (-768.0 + u2 * (320.0 - 175.0 * u2)))
    B = u2 / 1024.0 * (256.0 + u2 * (-128.0 + u2 * (74.0 - 47.0 * u2)))
    sigma = distance_m / (b * A)
    two_sigma_m = 0.0
    for _ in range(200):
        two_sigma_m = 2.0 * sigma1 + sigma
        delta_sigma = B * math.sin(sigma) * (
            math.cos(two_sigma_m)
            + B / 4.0 * (
                math.cos(sigma) * (-1.0 + 2.0 * math.cos(two_sigma_m) ** 2)
                - B / 6.0 * math.cos(two_sigma_m) * (-3.0 + 4.0 * math.sin(sigma) ** 2)
                * (-3.0 + 4.0 * math.cos(two_sigma_m) ** 2)
            )
        )
        sigma_prec = sigma
        sigma = distance_m / (b * A) + delta_sigma
        if abs(sigma - sigma_prec) < 1e-12:
            break
    lat2 = math.atan2(
        math.sin(U1) * math.cos(sigma) + math.cos(U1) * math.sin(sigma) * math.cos(az1),
        (1.0 - f) * math.sqrt(sinAlpha ** 2 + (math.sin(U1) * math.sin(sigma) - math.cos(U1) * math.cos(sigma) * math.cos(az1)) ** 2),
    )
    lam = math.atan2(
        math.sin(sigma) * math.sin(az1),
        math.cos(U1) * math.cos(sigma) - math.sin(U1) * math.sin(sigma) * math.cos(az1),
    )
    C = f / 16.0 * cos2Alpha * (4.0 + f * (4.0 - 3.0 * cos2Alpha))
    L = lam - (1.0 - C) * f * sinAlpha * (
        sigma + C * math.sin(sigma) * (math.cos(two_sigma_m) + C * math.cos(sigma) * (-1.0 + 2.0 * math.cos(two_sigma_m) ** 2))
    )
    lon2 = math.radians(lon1_deg) + L
    return math.degrees(lat2), math.degrees(lon2)


# --- Contrôle géométrique préalable : absence de cap français intermédiaire ---
#
# Le Cap Blanc-Nez (azimut ~230,6° depuis la digue) et le Cap Gris-Nez (azimut ~234,3°) sont tous
# deux à l'opposé de la route vers l'Angleterre (azimut ~305,5°, vers le NO) : la ligne droite
# s'éloigne des deux caps dès le départ. Vérifié par échantillonnage tous les 2 km le long de la
# géodésique : la latitude ne redescend jamais sous celle de la digue elle-même (50,946°N), donc la
# route ne peut recroiser aucun des deux caps, situés plus au sud.

CAP_BLANC_NEZ_LAT_DEG, CAP_BLANC_NEZ_LON_DEG = 50.9230, 1.7080
CAP_GRIS_NEZ_LAT_DEG, CAP_GRIS_NEZ_LON_DEG = 50.8697, 1.58485


# --- Vérification du profil intermédiaire (Tableau 10, §12.3) — altimétrie officielle IGN ---
#
# Méthode identique à celle établie pour le cas Chassiron↔Cordouan (et re-testée prospectivement
# avant la construction de cette archive, contrairement aux deux premiers cas) : interrogation de
# l'API REST d'altimétrie de la Géoplateforme IGN
# (https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json, ressource
# `ign_rge_alti_wld`, plusieurs points par requête séparés par « | »), qui renvoie -99999 (à
# l'arrondi près) pour tout point hors de sa couverture terrestre, c'est-à-dire en mer.
#
# Deux résolutions, conformément au Tableau 10 (§12.3) : pas de 2 km sur le corps de la route
# (8 à 28 km), affiné à 500 m sur les 6 premiers et les 6 derniers km (zones de départ et
# d'arrivée) — contrôle réalisé le 2026-09-03, sur demande explicite de resserrement de la maille
# côtière.
#
# LIMITE ASSUMÉE ET DOCUMENTÉE : le RGE ALTI est une donnée SOUVERAINE FRANÇAISE — il ne couvre pas
# le territoire britannique. Les points interrogés près de South Foreland (29,6 à 35,6 km) renvoient
# tous la valeur -99999, ce qui signifie ici « hors de la couverture du référentiel », PAS
# nécessairement « mer confirmée » au sens où on l'entend côté français. La nature terrestre de
# l'arrivée (falaises de Douvres, 110 m) est établie par une source indépendante (Wikipédia EN,
# voir SOUTHFORELAND_HAUTEUR_SOURCE ci-dessus), pas par l'IGN — exactement comme Chassiron et
# Cordouan eux-mêmes n'ont jamais été « confirmés terrestres par l'IGN » : ce sont des points
# d'ancrage connus par construction (ce sont des phares/falaises réels), l'IGN ne sert qu'à
# vérifier l'ABSENCE de terre entre les deux.

PROFIL_ELEVATIONS_IGN = (
    # (distance_m_depuis_Sangatte, elevation_m_ou_None_si_mer_ou_hors_couverture)
    # --- zone de départ, résolution 500 m (0 à 6 km) ---
    (0, 5.76), (500, None), (1000, None), (1500, None), (2000, None), (2500, None),
    (3000, None), (3500, None), (4000, None), (4500, None), (5000, None), (5500, None),
    (6000, None),
    # --- corps de la route, résolution 2 km (8 à 28 km) ---
    (8000, None), (10000, None), (12000, None), (14000, None), (16000, None), (18000, None),
    (20000, None), (22000, None), (24000, None), (26000, None), (28000, None),
    # --- zone d'arrivée, résolution 500 m (29,61 à 35,61 km) — hors couverture IGN, voir limite ci-dessus ---
    (29610, None), (30110, None), (30610, None), (31110, None), (31610, None), (32110, None),
    (32610, None), (33110, None), (33610, None), (34110, None), (34610, None), (35110, None),
    (35610, None),
)

PROFIL_CROISEMENTS_TERRE = ()  # aucune traversée de terre ferme intermédiaire détectée

PROFIL_CONCLUSION_DEFINITIVE = (
    "Vérification réalisée le 2026-09-03, EN AMONT de la construction de cette archive (discipline "
    "instaurée après la correction du cas Chassiron↔Cordouan), à partir de l'altimétrie officielle "
    "IGN (RGE ALTI, API Géoplateforme data.geopf.fr — voir PROFIL_ELEVATIONS_IGN pour le relevé "
    "complet, 37 points). RÉSULTAT : aucune traversée de terre ferme intermédiaire n'est détectée sur "
    "toute la portion couverte par le référentiel français (500 m à 28 km depuis la digue de "
    "Sangatte) — mer en continu. La terre ferme n'apparaît qu'aux deux points d'ancrage eux-mêmes : "
    "le départ (Digue de Sangatte, 5,76 m à 0 km, cohérent avec les 2-4 m sourcés) et, au-delà de la "
    "couverture IGN, l'arrivée (falaises de Douvres, 110 m, confirmée par Wikipédia EN — voir la "
    "limite de couverture documentée ci-dessus). CONSÉQUENCE : ce couple de sites SATISFAIT "
    "l'exigence du Tableau 10 (§12.3) d'une visée directe sur mer, à la résolution testée (500 m aux "
    "deux extrémités, 2 km sur le corps de la route) — une résolution suffisante pour écarter tout "
    "cap ou île de taille significative, mais pas pour garantir l'absence d'un écueil ponctuel de "
    "quelques dizaines de mètres non répertorié. Ce résultat a été établi AVANT la construction de "
    "cette archive, contrairement aux deux premiers cas d'étude de ce projet, conformément à la "
    "discipline de pré-écran mise en place après la correction du cas Chassiron↔Cordouan (voir "
    "/home/claude/outils-verification/profil_altimetrique.py et rapport_selection_site3.md)."
)
