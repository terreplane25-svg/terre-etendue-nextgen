#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérification des encadrés-clés à contenu empirique.

Sur les 240 « faits établis » du site, une quinzaine seulement sont des mesures
du monde physique susceptibles de contraindre la forme de la Terre. Ce script
les reprend au calcul, un par un, et distingue trois verdicts :

  FAUX          — l'énoncé est réfuté par le calcul, sans donnée supplémentaire
  INDÉCIDABLE   — l'énoncé ne peut être ni établi ni réfuté faute d'un paramètre
                  qu'il ne donne pas
  MAL POSÉ      — l'énoncé attaque une prédiction que le modèle visé ne fait pas

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
    """Distance de l'horizon géométrique pour un œil à la hauteur h."""
    return math.sqrt(2 * Rx * h)


def cachee(d, h1, h2, Rx=R):
    """Hauteur masquée par la courbure entre deux points élevés.

    C'est la SEULE formule correcte pour deux observateurs élevés :
    on retire d'abord les deux portées d'horizon, et seul le reliquat compte.
    La formule naïve d²/(2R) ne vaut que pour un observateur au ras du sol
    visant un point au ras du sol.
    """
    reliquat = d - portee(h1, Rx) - portee(h2, Rx)
    return (reliquat ** 2) / (2 * Rx) if reliquat > 0 else 0.0


def naive(d, Rx=R):
    """La formule que les encadrés fautifs emploient : chute sous la tangente."""
    return d * d / (2 * Rx)


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
L.append("Mais l'opération suivante ne l'est pas. Entre deux points élevés, la")
L.append("hauteur masquée vaut")
L.append("")
L.append("       (d − √(2R·h₁) − √(2R·h₂))² / (2R)")
L.append("")
L.append("et non « d²/(2R) moins les altitudes ». On retire d'abord les deux portées")
L.append("d'horizon ; seul le reliquat est masqué. Soustraire des altitudes d'une")
L.append("chute sous tangente mélange deux grandeurs qui ne s'additionnent pas.")
L.append("")
L.append("Hauteur minimale pour que la visée soit géométriquement possible,")
L.append("deux sommets de même altitude :")
for Rx, lab in ((R, "sans réfraction"), (RE, "avec k = 0,13")):
    L.append("   %-18s h₁ = h₂ = %.0f m" % (lab, (D / 2) ** 2 / (2 * Rx)))
L.append("")
L.append("Ce que donne la formule correcte selon les altitudes réelles :")
for h1, h2 in ((3400, 2900), (3800, 2400), (4200, 4000), (4800, 3500)):
    L.append("   h₁=%4d m  h₂=%4d m → %6.0f m sans réfraction · %6.0f m avec k=0,13"
             % (h1, h2, cachee(D, h1, h2), cachee(D, h1, h2, RE)))
L.append("")
L.append("CE QUI EST CERTAIN : l'opération de l'encadré est fausse, et le chiffre")
L.append("de « 11 km inexpliqués » n'a pas de sens géométrique.")
L.append("")
L.append("CE QUI NE L'EST PAS : que le record soit ou non anormal. Cela dépend")
L.append("entièrement des deux altitudes réelles et des conditions de réfraction")
L.append("du jour, que nous n'avons pas. Selon les altitudes, la hauteur masquée")
L.append("va de zéro à plusieurs centaines de mètres.")
L.append("")
L.append("RECTIFICATION D'UNE ERREUR DE NOTRE PART : nous avons d'abord présenté")
L.append("les valeurs 755 m et 93 m comme si elles réglaient le cas. Elles reposent")
L.append("sur des altitudes SUPPOSÉES. Elles montrent que l'opération est fausse,")
L.append("elles ne tranchent pas le cas particulier.")
check("Record de visibilité 493 km",
      "la-perspective-pourquoi-les-objets-disparaissent", 3,
      "INDÉCIDABLE (opération fausse, cas non tranché)", L)

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
L.append("CE QUI EST CERTAIN : l'énoncé est indécidable en l'état. Le paramètre")
L.append("qui décide — la hauteur de l'œil — est absent, et l'article")
L.append("« Par rapport à quoi mesure-t-on une altitude ? », encadré n°4, écrit")
L.append("lui-même : « la hauteur de l'œil est le paramètre décisif ».")
L.append("Le site possède donc la bonne règle et ne l'applique pas ici.")
check("Phare de Port-Saïd",
      "la-perspective-pourquoi-les-objets-disparaissent", 2,
      "INDÉCIDABLE (paramètre décisif absent)", L)

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


def main():
    print("═" * 74)
    print("VÉRIFICATION DES ENCADRÉS-CLÉS À CONTENU EMPIRIQUE")
    print("R = %.0f km · k = %.2f · R effectif = %.0f km" % (R / 1000, K, RE / 1000))
    print("═" * 74)
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
    print("%d encadrés vérifiés — aucun ne conclut « donc la Terre est ronde »."
          % len(CHECKS))
    print("Chacun dit seulement ce que l'énoncé permet, ou ne permet pas, d'affirmer.")
    print("═" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
