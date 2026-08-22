#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contrôles n°18 à 35 — second lot des encadrés à contenu métrologique.

Le premier lot, dans verifier-encadres-empiriques.py, portait sur les dix-sept
encadrés qui touchaient directement à la courbure et à la réfraction. Celui-ci
reprend les dix-huit derniers de la pile métrologique, une fois le tri de
scripts/trier-faits-etablis.py appliqué et corrigé à la main.

Chaque contrôle rend le chiffre annoncé par l'encadré et celui du calcul, sans
commentaire : la lecture des deux est dans les notes de
scripts/annoter-faits-etablis.py, qui renvoient aux numéros ci-dessous. Un
numéro cité là-bas et absent d'ici serait une référence en l'air.

Aucune donnée extérieure n'est requise : tout se dérive des constantes déclarées
en tête et des formules du premier lot, redéclarées ici pour que le script
tourne seul.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

R = 6371000.0          # m
K = 0.13
RE = R / (1 - K)
P0 = 1013.25           # hPa au niveau de la mer, atmosphère standard


def portee(h, Rx=R):
    return math.sqrt((Rx + h) ** 2 - Rx * Rx)


def cachee(d, h1, Rx=R):
    """Hauteur masquée — Pythagore exact, cf. lot 1 pour la démonstration."""
    a = portee(h1, Rx)
    return 0.0 if d <= a else math.sqrt(Rx * Rx + (d - a) ** 2) - Rx


def barometrique(h):
    """Pression de l'atmosphère standard à l'altitude h, en hPa."""
    return P0 * (1 - 2.25577e-5 * h) ** 5.2559


def k_requis(d, h1, h2):
    """Coefficient de réfraction minimal pour que h2 soit visible à d depuis h1."""
    lo, hi = 0.0, 0.95
    for _ in range(60):
        mid = (lo + hi) / 2
        if cachee(d, h1, R / (1 - mid)) > h2:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


LOT = []


def c(n, titre, lignes):
    LOT.append((n, titre, lignes))


# 18 ── Parallaxe de Halley
L = ["Énoncé : « un astre plus petit que la Terre ne peut être au-dessus de",
     "l'horizon des deux points d'observation à la fois ».", "",
     "La taille de l'astre n'entre dans aucune des relations. Seule sa distance",
     "compte. Deux observateurs séparés d'une base b voient un astre lointain",
     "situé dans la direction bissectrice à la hauteur 90° − b/(2R) :", ""]
for base in (2000, 6000, 11000, 12742):
    demi = math.degrees(base * 1000 / (2 * R))
    L.append("   base %6d km → demi-angle %5.1f° → hauteur %5.1f° chez chacun"
             % (base, demi, 90 - demi))
L += ["", "Les transits de Vénus s'observent depuis des bases de l'ordre de",
      "10 000 km, le Soleil restant plusieurs heures au-dessus des deux horizons."]
c(18, "Parallaxe de Halley et les « horizons parallèles »", L)

# 19 ── Gnomons chinois
c(19, "Gnomons : la méthode est-elle « intrinsèquement » non discriminante ?", [
    "Avec DEUX sites, non : un Soleil proche à hauteur finie reproduit exactement",
    "le rapport d'ombres d'un Soleil lointain sur une sphère. L'énoncé est juste.",
    "",
    "Avec TROIS sites ou plus, oui : la hauteur de Soleil impliquée par chaque",
    "paire doit être identique sur un plan, et les paires ne s'accordent pas.",
    "C'est donc le nombre de sites qui décide, non la méthode.",
])

# 20 ── Le stade d'Ératosthène
L = ["Énoncé : la « précision à 1 % » dépend du stade retenu.", ""]
for st in (157.5, 185.0):
    v = st * 252000 / 1000
    L.append("   252 000 stades × %5.1f m = %6.0f km → écart au réel (40 008 km) : %+5.1f %%"
             % (st, v, 100 * (v - 40008) / 40008))
c(20, "Ératosthène et le choix du stade", L)

# 21 ── Puy de Dôme
L = ["Énoncé : 124 hPa prédits, soit 93 mmHg, contre 84,6 mm mesurés en 1648.", ""]
p1, p2 = barometrique(340.0), barometrique(1465.0)
L += ["   atmosphère standard à  340 m : %.1f hPa" % p1,
      "   atmosphère standard à 1465 m : %.1f hPa" % p2,
      "   différence : %.1f hPa = %.1f mmHg" % (p1 - p2, (p1 - p2) / 1.33322),
      "",
      "   écart aux 84,6 mm historiques : %.0f %%" % (100 * ((p1 - p2) / 1.33322 - 84.6) / 84.6)]
c(21, "Puy de Dôme, 1648", L)

# 22 ── Nos propres chiffres de visibilité
L = ["Énoncé : 5,0 km de portée, 616 m à 100 km, 4 200 m à 253 km, et pour le",
     "Canigou un k requis passant de 0,42 à 0,15 selon la hauteur d'œil.", ""]
L.append("   portée depuis 1,70 m, k = 0,13 : %.1f km" % (portee(1.7, RE) / 1000))
for d in (100000, 253000):
    L.append("   masqué à %3d km : %.0f m" % (d / 1000, cachee(d, 1.7, RE)))
L.append("")
for h1 in (1.7, 160.0):
    L.append("   Canigou 2 784 m à 263 km, œil à %5.1f m → k requis %.2f"
             % (h1, k_requis(263000, h1, 2784.0)))
L += ["", "Les trois premières valeurs se confirment au mètre près. Les deux",
      "coefficients ne se reproduisent pas : 0,46 et 0,21 contre 0,42 et 0,15."]
c(22, "Article « Par rapport à quoi… », encadré n°4", L)

# 23-24 ── SRTM et géoïde : valeurs de référence, rien à recalculer
c(23, "SRTM", ["Onze jours de vol, 60° N à 56° S, 16 m d'exactitude absolue et",
               "10 m relative : conforme aux spécifications publiées de la mission.",
               "Aucun calcul à refaire — la vérification est documentaire."])
c(24, "Amplitude du géoïde", ["De −106 m à +85 m par rapport à l'ellipsoïde : valeur",
                             "admise. Vérification documentaire également."])

# 25-26 ── Sélénélion
L = ["Énoncé : voir Soleil et Lune éclipsée ensemble serait incompatible avec",
     "une réfraction standard de 0,5°.", "",
     "Budget angulaire réellement disponible pour « dépasser 180° » :", ""]
budget = [("réfraction du Soleil à l'horizon", 0.57),
          ("réfraction de la Lune à l'horizon", 0.57),
          ("demi-diamètre solaire", 0.27),
          ("demi-diamètre lunaire", 0.25),
          ("parallaxe lunaire horizontale", 0.95)]
for lab, v in budget:
    L.append("   %-36s %.2f°" % (lab, v))
L += ["   %-36s %.2f°" % ("TOTAL", sum(v for _, v in budget)), "",
      "L'encadré ne retient que 0,5°. La parallaxe lunaire vaut à elle seule",
      "le double de ce qu'il compte."]
c(25, "Sélénélion (article la-lune-le-soleil-et-les-etoiles)", L)
c(26, "Sélénélion (article la-lune-six-anomalies)", ["Même calcul que le n°25 :",
                                                     "2,61° disponibles contre 0,5° comptés."])

# 27 ── Portée visuelle
c(27, "Portée visuelle de 50 m à 500 km", [
    "La plage est réelle. Mais deux limites coexistent — atmosphérique et",
    "géométrique — et c'est la plus courte qui s'applique. Constater que l'une",
    "varie n'établit pas que l'autre est absente."])

# 28 ── Théodolite céleste
c(28, "Théodolite céleste, encadré n°3", [
    "Le jeu de données de l'article est nécessaire pour refaire le calcul.",
    "",
    "Indication : une somme d'angles supérieure à 180° est impossible en",
    "trigonométrie PLANE et normale en trigonométrie SPHÉRIQUE, où l'excès",
    "vaut E = aire / R². Un « triangle mathématiquement impossible » signale",
    "d'ordinaire qu'on a appliqué la trigonométrie plane à une base courbe."])

# 29 ── Oxygène atomique
L = ["Énoncé : « les conditions empirent exponentiellement avec l'altitude ».", "",
     "Densité d'oxygène atomique, ordres de grandeur admis :", ""]
for alt, n in ((200, 3e9), (300, 3e8), (400, 4e7), (600, 1e6), (800, 6e4)):
    L.append("   %3d km : %8.0e cm⁻³" % (alt, n))
L += ["", "Elle DÉCROÎT de cinq ordres de grandeur entre 200 et 800 km. L'érosion",
      "par l'oxygène atomique est un problème d'orbite basse ; elle s'atténue",
      "en montant. L'énoncé dit le contraire du fait."]
c(29, "Érosion par l'oxygène atomique", L)

# 30 ── Baumgartner
h = 39040.0
dip = math.degrees(math.acos(R / (R + h)))
rho = 90 - dip
L = ["Énoncé : « la courbure provient de l'objectif, pas de la surface filmée ».", "",
     "   dépression de l'horizon à %.0f m : %.2f°" % (h, dip),
     "   l'horizon est un cercle de rayon angulaire %.2f° autour du nadir" % rho, "",
     "Flèche réelle de l'arc d'horizon dans l'image :", ""]
for champ in (30, 50, 70, 110):
    b = math.radians(champ / 2)
    cc = math.cos(math.radians(rho)) / math.cos(b)
    L.append("   champ %3d° → %.2f°" % (champ, abs(math.degrees(math.acos(cc)) - rho)))
L += ["", "La courbure existe. Elle est seulement trop faible pour être vue sur un",
      "objectif standard — ce qui n'est pas la même chose que « elle provient de",
      "l'objectif »."]
c(30, "Le saut de Baumgartner", L)

# 31 ── Accélération centripète en vol
L = []
v = 900 / 3.6
L.append("   v = 900 km/h = %.1f m/s → v²/R = %.5f m/s² = %.3f milli-g"
         % (v, v * v / R, v * v / R / 9.81 * 1000))
L.append("")
L.append("Les 0,0098 m/s² annoncés sont exacts, et la conclusion l'est aussi.")
c(31, "Accélération centripète d'un vol de croisière", L)

# 32 ── La canette
dia, haut = 0.066, 0.115
S = math.pi * dia * haut + 2 * math.pi * (dia / 2) ** 2
c(32, "Force de la pression sur une canette", [
    "   surface d'une canette 66 × 115 mm : %.4f m²" % S,
    "   force sous 1 013 hPa : %.0f N = %.0f kgf" % (101325 * S, 101325 * S / 9.81),
    "",
    "Les « environ 300 kg » annoncés sont justes."])

# 33-34 ── Bedford et Chicago
for n, nom, d, h1, cible, ann in ((33, "Canal de Bedford", 10000.0, 0.20, None, 7.0),
                                  (34, "Skyline de Chicago", 60000.0, 1.70, 527.0, 283.0)):
    L = ["Énoncé : %.0f m de courbure théorique." % ann, "",
         "   règle de pouce d²/2R      : %7.1f m" % (d * d / (2 * R)),
         "   formule exacte, k = 0     : %7.1f m" % cachee(d, h1),
         "   formule exacte, k = 0,13  : %7.1f m" % cachee(d, h1, RE)]
    if cible:
        L += ["   cible de %.0f m → %s" % (cible, "VISIBLE" if cachee(d, h1, RE) < cible
                                           else "masquée"),
              "", "Les deux tiers supérieurs de la silhouette restent visibles :",
              "c'est ce qu'on photographie. Il n'y a pas d'incompatibilité."]
    else:
        L += ["", "Le chiffre opposé est surévalué de %.0f %%."
              % (100 * (ann - cachee(d, h1, RE)) / cachee(d, h1, RE))]
    c(n, nom, L)

# 35 ── Pression atmosphérique
c(35, "Pression atmosphérique au niveau de la mer", [
    "   1 013 hPa : valeur de l'atmosphère standard, exacte.",
    "",
    "La proposition qui suit dans l'encadré — « sa transition vers un prétendu",
    "vide spatial reste un problème physique non résolu » — est une affirmation",
    "distincte, que la mesure qui précède n'établit pas."])

# 36 ── Le Canigou depuis la Provence, et la direction de l'ombre lunaire
def k_crit(d, h1, h2):
    return 1 - 2 * R * ((math.sqrt(h1) + math.sqrt(h2)) ** 2) / (d * d)


CANIGOU = 2784.0
L = ["Le Canigou est photographié depuis la Provence depuis 2004. Les sites réels",
     "ne sont pas au niveau de la mer :", "",
     "   %-38s %8s %9s %10s" % ("site", "altitude", "distance", "k critique")]
for nom, h1, d in (("Sainte-Victoire, Pic des Mouches", 1011.0, 277000.0),
                   ("Le Garlaban", 714.0, 265000.0),
                   ("Hauteurs de la rade de Toulon", 300.0, 290000.0),
                   ("Niveau de la mer — jamais employé", 2.0, 277000.0)):
    L.append("   %-38s %6.0f m %7.0f km %9.3f"
             % (nom, h1, d / 1000, k_crit(d, h1, CANIGOU)))
L += ["",
      "Depuis les deux premiers, le coefficient critique est NÉGATIF : le sommet",
      "serait visible même sans aucune réfraction. Il n'y a là aucune anomalie,",
      "et l'encadré qui calcule depuis 1,70 m compare à une situation fictive.",
      "",
      "L'observation devient en revanche un TEST si l'on mesure la hauteur",
      "APPARENTE du massif depuis la Sainte-Victoire :", ""]
d, h1 = 277000.0, 1011.0
for lab, hv in (("Canigou entier, du pied 500 m au sommet", 2284.0),
                ("Globe, k = 0,25", CANIGOU - cachee(d, h1, R / 0.75)),
                ("Globe, k = 0,17", CANIGOU - cachee(d, h1, R / 0.83)),
                ("Globe, k = 0,13", CANIGOU - cachee(d, h1, RE)),
                ("Globe, k = 0", CANIGOU - cachee(d, h1, R))):
    ang = hv / d * (180 / math.pi) * 60
    L.append("   %-40s %6.0f m → %5.1f′ (%.2f Lune)" % (lab, hv, ang, ang / 31))
L += ["",
      "Facteur deux entre « entier » et « globe standard ». Mesurable en pixels",
      "sur les clichés existants, comme pour la panoramique du Caucase."]
c(36, "Le Canigou depuis la Provence", L)


def angle_parallactique(phi, dec, H):
    phi, dec, H = map(math.radians, (phi, dec, H))
    return math.degrees(math.atan2(
        math.sin(H), math.tan(phi) * math.cos(dec) - math.sin(dec) * math.cos(H)))


L = ["Objection reçue : « l'éclipse se fait de haut en bas, alors qu'on devrait",
     "voir l'ombre passer du bas vers le haut ».", "",
     "Le premier contact se produit toujours sur le limbe EST CÉLESTE de la Lune,",
     "parce que la Lune se déplace vers l'est par rapport à l'ombre, de 0,55° par",
     "heure. Cela, les deux modèles doivent le rendre de la même façon.",
     "",
     "Mais où se trouve l'est céleste SUR L'IMAGE ? À l'angle parallactique près,",
     "qui tourne au cours de la nuit :", "",
     "   observateur à 45° N, Lune de déclinaison +15°", "",
     "   %14s %20s   %s" % ("angle horaire", "angle parallactique", "l'est est vers…")]
for H in (-75, -45, 0, 45, 75):
    a = angle_parallactique(45, 15, H)
    L.append("   %10d°     %16.1f°   %s"
             % (H, a, "le bas" if a < -30 else "le haut" if a > 30 else "le côté"))
L += ["",
      "L'orientation du disque tourne de plus de cent degrés entre le lever et le",
      "coucher. « L'ombre vient du haut » et « l'ombre vient du bas » sont donc",
      "TOUS DEUX observés, selon l'heure et le lieu.",
      "",
      "Aucun des deux modèles ne prédit une direction fixe. L'objection ne porte",
      "pas — elle attaque une prédiction que personne ne fait."]
c(37, "Direction de l'ombre pendant une éclipse de Lune", L)


def main():
    print("═" * 74)
    print("CONTRÔLES N°18 À 35 — SECOND LOT MÉTROLOGIQUE")
    print("R = %.0f km · k = %.2f · atmosphère standard" % (R / 1000, K))
    print("═" * 74)
    for n, titre, lignes in LOT:
        print()
        print("┌─ n°%d · %s" % (n, titre))
        print("└" + "─" * 71)
        for l in lignes:
            print("   " + l)
    print()
    print("═" * 74)
    print("%d contrôles. Les verdicts correspondants sont posés par" % len(LOT))
    print("scripts/annoter-faits-etablis.py, qui renvoie à ces numéros.")
    print("═" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
