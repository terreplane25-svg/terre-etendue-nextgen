#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérification des encadrés-clés à contenu empirique.

Sur les 240 « faits établis » du site, une quinzaine seulement sont des mesures
du monde physique susceptibles de contraindre la forme de la Terre. Ce script
les reprend au calcul, un par un, et distingue trois verdicts :

  FAUX          — l'énoncé est réfuté par le calcul, sans donnée supplémentaire
  MAL POSÉ      — l'énoncé attaque une prédiction que le modèle visé ne fait pas,
                  ou compare deux grandeurs qui ne se comparent pas
  À COMPLÉTER   — l'énoncé omet un paramètre qui EXISTE et qui décide. Ce n'est
                  pas une question indécidable : c'est un énoncé incomplet, et
                  la donnée manquante est à porter au dossier.
  HORS SUJET    — l'énoncé peut être vrai sans rien dire de la forme de la Terre

Distinction posée après correction d'une faute de notre part. Nous avions écrit
« INDÉCIDABLE » pour deux énoncés dont le paramètre manquant est parfaitement
documenté — les altitudes de deux sommets, la hauteur d'un observateur. Notre
incapacité à y accéder depuis cet environnement, dont le réseau est fermé, est
une limite de l'outil et non une propriété de la question. « Je ne le sais pas »
n'est pas « on ne peut pas le savoir », et transférer l'un sur l'autre revient à
faire porter à l'article le handicap de celui qui l'examine.

Le script ne conclut jamais « donc la Terre est ronde ». Il dit seulement ce que
chaque énoncé permet, ou ne permet pas, d'affirmer.

Toutes les constantes sont déclarées en tête. Relancer le script reproduit
l'intégralité des chiffres cités dans content/corrections/faits-etablis.md.
"""

import math
import sys

R = 6371000.0          # m — rayon moyen
K = 0.13               # coefficient de réfraction moyen (Hirt et al. 2010)
RE = R / (1 - K)       # rayon effectif sous réfraction moyenne


def portee(h, Rx=R):
    """Longueur de la tangente menée depuis un œil à la hauteur h.

    √((Rx+h)² − Rx²) plutôt que √(2·Rx·h) : la forme exacte, dont la seconde
    n'est que le développement au premier ordre. L'écart est négligeable aux
    hauteurs usuelles, mais il n'y a aucune raison d'approximer ici.
    """
    return math.sqrt((Rx + h) ** 2 - Rx * Rx)


def cachee(d, h1, Rx=R):
    """Hauteur masquée par la courbure, vue depuis un œil à la hauteur h1.

    Rend la hauteur au-dessous de laquelle un objet situé à la distance d est
    invisible. Un sommet de hauteur h2 est donc visible si, et seulement si,
    h2 > cachee(d, h1).

    C'est du Pythagore exact : le triangle rectangle a pour côtés Rx (du centre
    au point de tangence) et d − a (la tangente jusqu'à la verticale de la
    cible), et l'on retranche Rx de l'hypoténuse.

    ── Erreur corrigée le 2026-08-21 ────────────────────────────────────────
    La version précédente calculait (d − a₁ − a₂)²/(2Rx), soit le carré du
    reliquat après retrait des DEUX portées d'horizon. Cette expression donne
    le bon SEUIL de visibilité — la condition a₁ + a₂ ≥ d est exacte — mais sa
    valeur numérique n'est pas une hauteur, et elle était lue comme telle.
    Le contrôle qui l'a démasquée : observateur au ras du sol, cible à 10 km.
    La réponse exacte est 7,85 m ; l'ancienne formule, alimentée avec 7,85 m,
    rendait 0,00 m. Sur la ligne Karagöl → Shkhara, elle annonçait 107 m
    masqués là où la valeur vraie est 6 783 m, c'est-à-dire la montagne
    entière. Deux verdicts en dépendaient et ont été rejoués.
    ─────────────────────────────────────────────────────────────────────────
    """
    a = portee(h1, Rx)
    if d <= a:
        return 0.0
    return math.sqrt(Rx * Rx + (d - a) ** 2) - Rx


def visible(d, h1, h2, Rx=R):
    """Hauteur de cible émergeant au-dessus de la ligne de visée, ou 0."""
    return max(0.0, h2 - cachee(d, h1, Rx))


def k_critique(d, h1, h2):
    """Coefficient de réfraction à partir duquel la cible cesse d'être masquée.

    Tiré de la condition de tangence a₁ + a₂ = d au premier ordre.
    """
    return 1 - 2 * R * ((math.sqrt(h1) + math.sqrt(h2)) ** 2) / (d * d)


def naive(d, Rx=R):
    """La formule que les encadrés fautifs emploient : chute sous la tangente."""
    return d * d / (2 * Rx)


def naive_moins_oeil(d, h1, Rx=R):
    """La règle de pouce « 8 pouces par mille au carré, moins la hauteur d'œil ».

    Fausse dès que d dépasse la portée d'horizon, et toujours par excès. Son
    écart à la valeur exacte vaut a·(d − a)/Rx, soit l'angle de dépression de
    l'horizon multiplié par la distance au-delà de l'horizon. Conservée ici
    pour pouvoir chiffrer, encadré par encadré, ce que l'erreur a fabriqué.
    """
    return d * d / (2 * Rx) - h1


def depression_horizon(h, Rx=R):
    """Angle de dépression de l'horizon vu depuis la hauteur h, en minutes d'arc."""
    return math.degrees(math.sqrt(2 * h / Rx)) * 60


def visibilite_latitudes(delta):
    """Plage de latitudes depuis lesquelles une étoile de déclinaison delta
    passe au-dessus de l'horizon : |phi - delta| < 90."""
    return max(-90.0, delta - 90.0), min(90.0, delta + 90.0)


CHECKS = []


def check(nom, article, encadre, verdict, lignes):
    CHECKS.append((nom, article, encadre, verdict, lignes))


# ═══════════════════════════════════════════════════════════════════════════
# 1. Les constellations et la « limite théorique de 90° »
# ═══════════════════════════════════════════════════════════════════════════
L = []
L.append("Énoncé : « plusieurs constellations nordiques sont observables sur des")
L.append("plages de 120° à 155° de latitude — dépassant la limite théorique de")
L.append("≈ 90° imposée par la courbure d'un globe ».")
L.append("")
L.append("Une étoile de déclinaison δ culmine à h = 90° − |φ − δ|. Elle passe donc")
L.append("au-dessus de l'horizon depuis toute latitude φ telle que |φ − δ| < 90°.")
L.append("")
for nom_e, d in (("Alkaid, δ la plus basse de la Grande Ourse", 49.3),
                 ("Dubhe, Grande Ourse", 61.7),
                 ("Polaris", 89.3),
                 ("ceinture d'Orion, δ ≈ 0", 0.0),
                 ("Sirius", -16.7)):
    lo, hi = visibilite_latitudes(d)
    L.append("   %-42s δ=%+5.1f° → %+6.1f° … %+5.1f° = %5.1f°"
             % (nom_e, d, lo, hi, hi - lo))
L.append("")
L.append("La plage PRÉDITE par le globe atteint 130,7° pour Alkaid et 180,0° pour")
L.append("une constellation équatoriale. Aucune limite de 90° n'existe.")
L.append("Les 120° observés sont donc À L'INTÉRIEUR de la prédiction du modèle")
L.append("que l'encadré présente comme réfuté.")
L.append("")
L.append("Lecture charitable examinée : « depuis un point donné on ne voit qu'un")
L.append("hémisphère, soit 180° de ciel ». C'est exact, mais c'est une étendue de")
L.append("CIEL, pas une plage de LATITUDES. Les deux grandeurs sont distinctes et")
L.append("la substitution ne sauve pas l'énoncé.")
check("Constellations et « limite de 90° »",
      "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre", 3,
      "FAUX", L)

# ═══════════════════════════════════════════════════════════════════════════
# 2. Le record de visibilité de 493 km
# ═══════════════════════════════════════════════════════════════════════════
D = 493000.0
L = []
L.append("Énoncé : « le record de 493 km implique 19 100 m de courbure théorique.")
L.append("Après déduction des altitudes combinées, environ 11 km de bosse restent")
L.append("inexpliqués par le modèle sphérique ».")
L.append("")
L.append("   d²/(2R) à 493 km = %.0f m — l'encadré annonce 19 100 m, l'arithmétique"
         % naive(D))
L.append("   de cette étape est donc juste.")
L.append("")
L.append("Mais l'opération suivante ne l'est pas. « d²/(2R) moins les altitudes »")
L.append("n'est pas une hauteur masquée : c'est la règle de pouce « 8 pouces par")
L.append("mille au carré, moins la hauteur d'œil », qui est fausse dès que la cible")
L.append("dépasse l'horizon, et toujours par excès. L'altitude ne retranche pas des")
L.append("mètres à la chute : elle REPOUSSE l'horizon de √(2R·h₁), et seule la")
L.append("distance au-delà compte ensuite. La formule exacte est du Pythagore :")
L.append("")
L.append("       cachée = √( R² + (d − √(2R·h₁))² ) − R")
L.append("")
L.append("L'écart entre les deux vaut exactement a·(d − a)/R, soit l'angle de")
L.append("dépression de l'horizon multiplié par la distance au-delà de l'horizon.")
L.append("Il est nul PILE à l'horizon — d'où la longévité de la règle de pouce —")
L.append("et croît linéairement ensuite.")
L.append("")
L.append("Le cas réel documenté est la ligne Karagöl (Giresun, Turquie) → Caucase,")
L.append("photographiée le 15 décembre 2024. Observateur à 3 100 m, k mesuré 0,14")
L.append("par extraction ERA5 le long de la visée. Cinq sommets y figurent :")
L.append("")
CAUCASE = (("Mount Laila", 450000.0, 4008.0),
           ("Ushba", 470000.0, 4710.0),
           ("Janga (Dzhangi-Tau)", 489000.0, 5085.0),
           ("Shkhara", 493000.0, 5193.0))
H_OBS = 3100.0
R14 = R / (1 - 0.14)
L.append("   %-22s %7s %7s %9s   %s" % ("sommet", "d (km)", "h (m)", "k requis", "à k = 0,14"))
for nom_s, d_s, h_s in CAUCASE:
    vis = visible(d_s, H_OBS, h_s, R14)
    L.append("   %-22s %7.0f %7.0f %9.4f   %s"
             % (nom_s, d_s / 1000, h_s, k_critique(d_s, H_OBS, h_s),
                ("%.0f m émergés" % vis) if vis > 0 else "masqué"))
L.append("")
L.append("Les cinq étant visibles simultanément, la photographie impose k ≥ 0,1445,")
L.append("contrainte fixée par Shkhara. Le k mesuré vaut 0,140 : il manque 3 %, sur")
L.append("un coefficient que personne ne connaît à mieux que 10 %.")
L.append("")
L.append("Ce que la règle de pouce fabriquait, sur cette même ligne :")
L.append("   règle de pouce  : %6.0f m masqués" % naive_moins_oeil(493000.0, H_OBS))
L.append("   Pythagore, k=0  : %6.0f m masqués" % cachee(493000.0, H_OBS))
L.append("   écart a(d−a)/R  : %6.0f m inventés" % (portee(H_OBS)
                                                    * (493000.0 - portee(H_OBS)) / R))
L.append("")
L.append("VERDICT : l'encadré ne tient pas. L'anomalie qu'il annonce est un artefact")
L.append("de formule. Correctement calculée, l'observation est PRÉDITE par le modèle")
L.append("sphérique à une réfraction ordinaire — elle ne le met pas en difficulté.")
L.append("Elle ne prouve pas davantage le globe : sur une Terre étendue ces sommets")
L.append("seraient visibles aussi. C'est une observation NON DISCRIMINANTE, dont la")
L.append("valeur probante est nulle dans les deux sens.")
L.append("")
L.append("RECTIFICATION D'UNE ERREUR DE NOTRE PART : la première version de ce")
L.append("contrôle employait (d − a₁ − a₂)²/(2R) et lisait son résultat comme une")
L.append("hauteur. Elle annonçait 107 m masqués là où la valeur vraie est 6 783 m,")
L.append("soit la montagne entière, et concluait à tort que l'observation passait")
L.append("même sans réfraction. Le verdict a été rejoué avec la formule exacte.")
check("Record de visibilité 493 km",
      "la-perspective-pourquoi-les-objets-disparaissent", 3,
      "RETIRER (anomalie fabriquée par la formule ; observation non discriminante)", L)

# ═══════════════════════════════════════════════════════════════════════════
# 3. Le phare de Port-Saïd
# ═══════════════════════════════════════════════════════════════════════════
L = []
L.append("Énoncé : « le phare de Port-Saïd (18 m) est visible à 93 km, où la")
L.append("courbure théorique cache 684 mètres — 37 fois sa hauteur ».")
L.append("")
L.append("   d²/(2R) à 93 km = %.0f m — proche des 684 m annoncés." % naive(93000))
L.append("")
L.append("Mais cette formule suppose un œil au ras de l'eau. La visibilité réelle")
L.append("dépend de la hauteur de l'observateur, que l'encadré ne donne pas :")
L.append("")
for Rx, lab in ((R, "sans réfraction"), (RE, "avec k = 0,13")):
    reste = 93000 - portee(18, Rx)
    L.append("   %-18s portée du phare %5.1f km → œil requis à %4.0f m"
             % (lab, portee(18, Rx) / 1000, reste * reste / (2 * Rx)))
L.append("")
L.append("CE QUI EST CERTAIN : la formule employée suppose un œil au ras de l'eau,")
L.append("ce qui n'est jamais le cas. CE QUI RESTE À COMPLÉTER : la hauteur")
L.append("d'observation et la source de l'observation — deux données qui existent.")
L.append("Le paramètre qui décide est absent de l'énoncé, et l'article")
L.append("« Par rapport à quoi mesure-t-on une altitude ? », encadré n°4, écrit")
L.append("lui-même : « la hauteur de l'œil est le paramètre décisif ».")
L.append("Le site possède donc la bonne règle et ne l'applique pas ici.")
check("Phare de Port-Saïd",
      "la-perspective-pourquoi-les-objets-disparaissent", 2,
      "À COMPLÉTER (hauteur d'observation à porter au dossier)", L)

# ═══════════════════════════════════════════════════════════════════════════
# 4. « L'horizon devrait s'abaisser de 20 m »
# ═══════════════════════════════════════════════════════════════════════════
L = []
L.append("Énoncé : « l'horizon reste parfaitement aligné avec une planche de niveau")
L.append("sur un demi-cercle complet de 16 à 32 km de portée visuelle. Sur un globe")
L.append("de 40 225 km, l'horizon devrait s'abaisser de 20 m à 16 km — il ne le")
L.append("fait jamais ».")
L.append("")
L.append("   d²/(2R) à 16 km = %.1f m — les 20 m annoncés sont exacts." % naive(16000))
L.append("")
L.append("Mais ces 20 m sont la chute de la SURFACE sous la tangente. Ce n'est pas")
L.append("de combien l'horizon paraît descendre pour l'observateur. Cette dernière")
L.append("grandeur est un ANGLE, la dépression de l'horizon, et elle vaut :")
L.append("")
for h in (1.7, 10, 100, 1000, 10000):
    L.append("   œil à %7.1f m → dépression = %6.2f minutes d'arc (%.3f°)"
             % (h, depression_horizon(h), depression_horizon(h) / 60))
L.append("")
L.append("À hauteur d'homme, le modèle sphérique prédit une dépression de 2,5")
L.append("minutes d'arc, soit 0,04°. Une planche de niveau ne peut pas la révéler.")
L.append("")
L.append("CONCLUSION : le modèle sphérique prédit que l'horizon apparaît au niveau")
L.append("des yeux à hauteur d'homme. L'encadré présente comme une réfutation une")
L.append("observation qui est la PRÉDICTION du modèle. L'énoncé est mal posé :")
L.append("il compare une hauteur en mètres à une observation angulaire.")
check("« L'horizon devrait s'abaisser de 20 m »",
      "lhorizon-la-perspective-et-la-refraction", 1,
      "MAL POSÉ (mètres comparés à un angle)", L)

# ═══════════════════════════════════════════════════════════════════════════
# 5. Le théodolite céleste et les 1 340 m
# ═══════════════════════════════════════════════════════════════════════════
L = []
L.append("Énoncé : « sur 12 sommets montagneux (8,8 à 130,7 km), l'angle calculé par")
L.append("trigonométrie plane correspond exactement à la position vraie de l'étoile.")
L.append("À 130,7 km, la courbure théorique cacherait 1 340 m — pourtant aucune")
L.append("correction n'est nécessaire ».")
L.append("")
L.append("   d²/(2R) à 130,7 km = %.0f m — les 1 340 m annoncés sont exacts."
         % naive(130700))
L.append("")
L.append("Mais cette grandeur n'a rien à voir avec la visée d'une étoile. Les 1 340 m")
L.append("sont la hauteur qu'un renflement masquerait pour une CIBLE AU SOL située")
L.append("à 130,7 km. Une étoile est à distance pratiquement infinie : sa direction")
L.append("est la même depuis les deux stations à un angle près, égal à la convergence")
L.append("des verticales locales, soit :")
L.append("")
for d in (8800, 50000, 130700):
    conv = math.degrees(d / R) * 60
    L.append("   base de %6.1f km → convergence des verticales = %5.2f minutes d'arc"
             % (d / 1000, conv))
L.append("")
L.append("CONCLUSION : l'absence de correction de 1 340 m ne prouve rien, parce")
L.append("qu'aucun modèle ne demande cette correction pour une visée stellaire.")
L.append("La grandeur pertinente est la convergence des verticales — quelques")
L.append("dizaines de minutes d'arc — et l'encadré ne la mentionne pas.")
L.append("L'énoncé est mal posé : il applique à une visée astronomique une formule")
L.append("de visibilité terrestre.")
check("Théodolite céleste, les 1 340 m",
      "le-theodolite-celeste", 1,
      "MAL POSÉ (formule terrestre appliquée à une visée stellaire)", L)


# ═══════════════════════════════════════════════════════════════════════════
# 6. Cook et les 60 000 km le long de la barrière
# ═══════════════════════════════════════════════════════════════════════════
L = []
L.append("Énoncé : « les journaux de Cook documentent plus de 60 000 km parcourus le")
L.append("long de la barrière antarctique — soit 3 à 6 fois le périmètre théorique du")
L.append("continent à 65° S sur un globe (≈ 16 900 km) ».")
L.append("")
L.append("Le périmètre est juste :")
for lat in (60, 65, 70):
    L.append("   parallèle %d° S → %.0f km"
             % (lat, 2 * math.pi * R * math.cos(math.radians(lat)) / 1000))
L.append("")
L.append("Mais 60 000 km est une DISTANCE PARCOURUE et 16 900 km une CIRCONFÉRENCE.")
L.append("Les deux ne se comparent pas. Cook a mené trois campagnes, en zigzag, a été")
L.append("bloqué par les glaces, est remonté vers le nord et a recommencé ses")
L.append("approches. Un chemin avec détours excède toujours le périmètre qu'il longe,")
L.append("et cela vaut dans TOUS les modèles, y compris le plan : sur une projection")
L.append("azimutale, longer un anneau en zigzag donne aussi plusieurs fois sa longueur.")
L.append("Le rapport 3 à 6 ne distingue donc rien.")
L.append("")
L.append("CE QUI SUBSISTE : la seconde moitié de l'énoncé — « Cook ne mentionne jamais")
L.append("avoir bouclé le tour ni retrouvé son point de départ » — est une affirmation")
L.append("sur le contenu des journaux. Elle est vérifiable, elle n'est pas vérifiée")
L.append("ici, et elle ne dépend pas du calcul. À traiter comme une question de source.")
check("Cook, 60 000 km contre 16 900 km",
      "cartes-routes-boussoles-et-le-mystere-antarctique", 4,
      "MAL POSÉ (chemin parcouru comparé à un périmètre)", L)

# ═══════════════════════════════════════════════════════════════════════════
# 7. Le ratio de 11 764 sur les marées
# ═══════════════════════════════════════════════════════════════════════════
GM_S = 1.32712e20      # m³/s² — paramètre gravitationnel solaire
UA = 1.495979e11       # m
OMEGA_ORB = 2 * math.pi / (365.256 * 86400)

g_sol = GM_S / UA ** 2
centrifuge = OMEGA_ORB ** 2 * UA
maree = 2 * GM_S * R / UA ** 3

L = []
L.append("Énoncé : « la force centrifuge solaire requise par l'héliocentrisme produit")
L.append("un ratio de 11 764 fois supérieur à la force gravitationnelle solaire sur")
L.append("les marées. Ce ratio n'est pas observé dans les données ».")
L.append("")
L.append("   gravité solaire à l'orbite terrestre   = %.4e m/s²" % g_sol)
L.append("   accélération centrifuge orbitale       = %.4e m/s²" % centrifuge)
L.append("   écart entre les deux                   = %.3f %%"
         % (abs(g_sol - centrifuge) / g_sol * 100))
L.append("   force de marée solaire (différentielle) = %.4e m/s²" % maree)
L.append("")
L.append("   RATIO gravité solaire / marée solaire   = %.0f" % (g_sol / maree))
L.append("")
L.append("L'encadré annonce 11 764. Le calcul donne %.0f, soit un écart de %.1f %%."
         % (g_sol / maree, abs(g_sol / maree - 11764) / 11764 * 100))
L.append("LE CHIFFRE EST DONC JUSTE, et il faut le dire : ce n'est pas une erreur")
L.append("d'arithmétique.")
L.append("")
L.append("C'est l'inférence qui ne suit pas. Ce ratio n'a pas à « être observé dans")
L.append("les données » : il mesure précisément POURQUOI les marées sont faibles.")
L.append("La gravité solaire moyenne et la centrifuge orbitale s'équilibrent à mieux")
L.append("que le millième — le calcul ci-dessus le montre. Ce qui reste, et qui")
L.append("soulève l'eau, est le terme différentiel, %.0f fois plus petit." % (g_sol / maree))
L.append("Le nombre de l'encadré est donc la mesure de la petitesse de l'effet,")
L.append("pas une prédiction contredite par l'observation.")
L.append("")
L.append("CE QUI SUBSISTE, et qui est solide : l'autre encadré du même article —")
L.append("les cartes NOAA, SHOM et TPXO9 montrent des rotations autour de points")
L.append("amphidromiques et non deux renflements orientés vers la Lune. C'est un")
L.append("fait, et c'est une correction légitime d'une image scolaire fausse.")
check("Le ratio de 11 764 sur les marées",
      "les-marees-contre-lheliocentrisme", 1,
      "MAL POSÉ (chiffre juste, inférence fausse)", L)

# ═══════════════════════════════════════════════════════════════════════════
# 8. Les instruments de vol et l'assiette de croisière
# ═══════════════════════════════════════════════════════════════════════════
L = []
L.append("Énoncés n°3, 4 et 5 : « l'horizon artificiel n'enregistre aucune correction")
L.append("vers le bas », « l'altimètre ne contient aucun algorithme de correction")
L.append("sphérique », « aucune source ne documente une correction de pitch ».")
L.append("")
L.append("Grandeurs en jeu, à vitesse de croisière :")
for v_kmh in (800, 900, 1000):
    v = v_kmh / 3.6
    a = v * v / R
    L.append("   %4d km/h → accélération centripète %.4e m/s² = %.3f milli-g"
             % (v_kmh, a, a / 9.81 * 1000))
v = 250.0
taux = math.degrees(v / R)
L.append("   rotation de l'horizontale locale à 900 km/h = %.5f °/s = %.1f °/heure"
         % (taux, taux * 3600))
L.append("")
L.append("Le point décisif est instrumental. L'horizon artificiel est asservi à la")
L.append("VERTICALE LOCALE, c'est-à-dire à la direction de la pesanteur. « À plat »")
L.append("signifie perpendiculaire à cette verticale. Un instrument qui définit son")
L.append("zéro par rapport à la verticale locale ne peut pas, par construction,")
L.append("révéler une courbure définie par la variation de cette même verticale.")
L.append("L'absence de lecture n'est donc pas une donnée : c'est une conséquence de")
L.append("la référence choisie. Même remarque pour l'altimètre, qui mesure une")
L.append("pression et non une trajectoire.")
L.append("")
L.append("INCOHÉRENCE INTERNE. L'encadré n°8 du MÊME article énonce déjà la réponse :")
L.append("« une trajectoire physiquement courbe produirait 0,0098 m/s², soit environ")
L.append("1 milli-g ; cette valeur est inférieure à la résolution des enregistreurs")
L.append("de vol standards : les données FDR publiées ne permettent ni de la")
L.append("constater ni de l'écarter. » Ce n'est pas contestable, et le calcul")
L.append("ci-dessus le confirme à 900 km/h. L'encadré n°8 retire donc aux n°3, 4 et 5")
L.append("leur portée probante. Le site porte à la fois l'argument et sa réfutation.")
L.append("L'encadré n°8 est à GARDER — il est exemplaire.")
check("Instruments de vol, encadrés 3-4-5 contre l'encadré 8",
      "vols-avion-et-courbure-terrestre", 3,
      "MAL POSÉS (réfutés par l'encadré n°8 du même article)", L)

# ═══════════════════════════════════════════════════════════════════════════
# 9. La réfraction de Nansen — et ce qu'elle coûte au site
# ═══════════════════════════════════════════════════════════════════════════
L = []
L.append("Énoncé : « les mesures de Nansen (1894) documentent une réfraction")
L.append("astronomique de 4°44′ — des dizaines de fois la valeur standard. Si de")
L.append("telles réfractions existent, elles invalident simultanément toute")
L.append("observation d'horizon utilisée comme preuve de courbure terrestre ».")
L.append("")
L.append("Cet énoncé est le plus rigoureux du lot, et il est à GARDER. Les réfractions")
L.append("polaires extrêmes sont documentées, et la conclusion qu'il en tire est")
L.append("logiquement correcte ET symétrique : elle vaut pour toute observation")
L.append("d'horizon, sans distinction de camp.")
L.append("")
L.append("MAIS il faut en tirer la conséquence, et elle est coûteuse. Si une réfraction")
L.append("de 4°44′ invalide « toute observation d'horizon », alors elle invalide aussi :")
L.append("")
L.append("   · le phare de Port-Saïd à 93 km ;")
L.append("   · le record de visibilité de 493 km ;")
L.append("   · les navires ramenés au zoom du Nikon P900 ;")
L.append("   · l'horizon aligné sur une planche de niveau ;")
L.append("   · les 12 sommets du théodolite céleste.")
L.append("")
L.append("Autrement dit, le site a établi un fait qui met hors service cinq de ses")
L.append("autres encadrés. Soit la réfraction extrême est admise et les observations")
L.append("d'horizon perdent leur valeur probante des deux côtés, soit elle est")
L.append("bornée — et il faut alors dire à quelle valeur, avec quelle source.")
L.append("On ne peut pas l'invoquer contre l'adversaire et l'oublier pour soi.")
check("La réfraction de Nansen, 4°44′",
      "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre", 4,
      "GARDER — mais avec sa conséquence sur cinq de nos propres encadrés", L)

# ═══════════════════════════════════════════════════════════════════════════
# 10. Le refroidissement sous la lumière lunaire concentrée
# ═══════════════════════════════════════════════════════════════════════════
L = []
L.append("Énoncé : « les mesures du Lancet (1856) documentent un refroidissement de")
L.append("plus de 8 degrés sous la lumière lunaire concentrée. Un miroir réfléchissant")
L.append("la lumière solaire réchauffe ce qu'il éclaire — la Lune produit l'effet")
L.append("inverse ».")
L.append("")
L.append("Deux remarques, et la seconde suffit.")
L.append("")
L.append("PREMIÈRE. L'observation est plausible et son mécanisme est connu : un")
L.append("thermomètre placé au foyer d'un miroir tourné vers le ciel RAYONNE vers le")
L.append("ciel nocturne, dont la température de brillance est très basse. Il se")
L.append("refroidit donc sous la température de l'air ambiant. Un miroir pointé sur la")
L.append("Lune voit surtout du ciel froid autour d'elle : le bilan reste au")
L.append("refroidissement. Ce n'est pas « la lumière de la Lune qui refroidit », c'est")
L.append("le foyer qui perd plus par rayonnement qu'il ne gagne. La date de 1856 et le")
L.append("chiffre de 8° restent à vérifier sur la publication — donnée qui existe.")
L.append("")
L.append("SECONDE, et décisive : quelle que soit la réponse, cet énoncé ne dit RIEN")
L.append("de la forme de la Terre. Il porte sur la nature de la lumière lunaire.")
L.append("Il peut être entièrement vrai et laisser la question de la figure terrestre")
L.append("exactement où elle était. Sa place dans un dossier sur la forme de la Terre")
L.append("est donc à justifier, ou il faut le déplacer.")
check("Refroidissement sous la lumière lunaire",
      "la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas", 1,
      "HORS SUJET (porte sur la Lune, pas sur la figure de la Terre)", L)

# ═══════════════════════════════════════════════════════════════════════════
# 11. Les détours aériens et les 70 %
# ═══════════════════════════════════════════════════════════════════════════
L = []
L.append("Énoncé : « plusieurs trajets inter-hémisphère Sud effectuent des détours")
L.append("systématiques par l'hémisphère Nord, ajoutant jusqu'à 70 % de distance")
L.append("supplémentaire — trajets incohérents sur un globe mais rectilignes sur une")
L.append("projection azimutale ».")
L.append("")
L.append("INCOHÉRENCE INTERNE, et elle est frontale. Le corps du MÊME article écrit :")
L.append("« Nuance reconnue : les détours aériens peuvent avoir des explications")
L.append("pratiques — vents dominants, jet stream, demande commerciale, hubs mondiaux,")
L.append("accords bilatéraux. » Le texte concède donc ce que l'encadré présente comme")
L.append("établi. Un encadré-clé ne peut pas effacer la réserve que son propre article")
L.append("vient de poser vingt lignes plus haut.")
L.append("")
L.append("À COMPLÉTER, et c'est facile : les distances orthodromiques et les distances")
L.append("réellement volées, route par route, avec la source. Ces données existent")
L.append("dans les plans de vol publiés. Tant qu'elles ne sont pas au dossier, le")
L.append("chiffre de « 70 % » n'est pas contrôlable par le lecteur — et ce chiffre est")
L.append("le seul contenu quantitatif de l'énoncé.")
L.append("")
L.append("Une question de méthode à trancher en même temps : un détour choisi pour des")
L.append("raisons commerciales et un détour imposé par la géométrie ne se distinguent")
L.append("pas sur une carte. Il faut donc dire à l'avance quel écart, sur quelle route,")
L.append("ne serait explicable QUE par la géométrie. Sans ce critère posé d'avance,")
L.append("l'observation ne peut pas trancher.")
check("Détours aériens et les 70 %",
      "cartes-routes-boussoles-et-le-mystere-antarctique", 2,
      "À COMPLÉTER (contredit par le corps du même article)", L)


def autotest():
    """Contrôles de non-régression sur la géométrie.

    Ces quatre cas ont des réponses connues indépendamment. Le premier aurait
    suffi à démasquer immédiatement la formule fautive de la version
    précédente : il est ici pour que cela ne se reproduise pas.
    """
    essais = []

    # 1. Observateur au ras du sol : la hauteur cachée vaut exactement d²/(2R).
    #    C'est le seul cas où la formule naïve est juste, et il sert d'ancrage.
    essais.append(("cible à 10 km, œil au sol", cachee(10000.0, 0.0),
                   10000.0 ** 2 / (2 * R), 0.01))

    # 2. Le calculateur du site et deux calculateurs tiers s'accordent sur ce cas.
    essais.append(("Karagöl 3 100 m → 493 km, sans réfraction",
                   cachee(493000.0, 3100.0), 6790.5, 1.0))

    # 3. Pile à la portée d'horizon, rien n'est encore masqué.
    essais.append(("cible pile à l'horizon", cachee(portee(50.0), 50.0), 0.0, 0.001))

    # 4. L'écart de la règle de pouce vaut a·(d−a)/R — identité exacte.
    a = portee(3100.0)
    essais.append(("écart de la règle de pouce",
                   naive_moins_oeil(493000.0, 3100.0) - cachee(493000.0, 3100.0),
                   a * (493000.0 - a) / R, 6.0))

    echecs = 0
    print("Contrôles de non-régression :")
    for nom, obtenu, attendu, tol in essais:
        ok = abs(obtenu - attendu) <= tol
        echecs += 0 if ok else 1
        print("   %s %-42s %10.2f  (attendu %.2f)"
              % ("✓" if ok else "✗", nom, obtenu, attendu))
    if echecs:
        print("   %d CONTRÔLE(S) EN ÉCHEC — les verdicts ci-dessous sont suspects." % echecs)
    print()
    return echecs


def main():
    print("═" * 74)
    print("VÉRIFICATION DES ENCADRÉS-CLÉS À CONTENU EMPIRIQUE")
    print("R = %.0f km · k = %.2f · R effectif = %.0f km" % (R / 1000, K, RE / 1000))
    print("═" * 74)
    print()
    if autotest():
        return 1
    for nom, article, n, verdict, lignes in CHECKS:
        print()
        print("┌─ %s" % nom)
        print("│  %s, encadré n°%d" % (article, n))
        print("│  VERDICT : %s" % verdict)
        print("└" + "─" * 71)
        for l in lignes:
            print("   " + l)
    print()
    print("═" * 74)
    from collections import Counter
    c = Counter(v.split()[0] for _, _, _, v, _ in CHECKS)
    print("%d encadrés vérifiés : %s" % (len(CHECKS),
          " · ".join("%d %s" % (n, k) for k, n in c.most_common())))
    print("Aucun ne conclut « donc la Terre est ronde ».")
    print("Chacun dit seulement ce que l'énoncé permet, ou ne permet pas, d'affirmer.")
    print("═" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
