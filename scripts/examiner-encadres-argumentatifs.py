#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contrôles n°38 à 71 — les encadrés argumentatifs et narratifs.

Trente-quatre énoncés qui ne portent ni sur une grandeur mesurable, ni sur une
source consultable, mais sur la VALEUR d'un raisonnement : ce qu'une preuve
établit, ce qu'un postulat détermine, ce qu'une théorie prédit. Ils ne se
vérifient pas, ils s'examinent.

Ce script ne les rejuge pas — les verdicts et leurs motifs sont dans
scripts/annoter-faits-etablis.py. Il fait deux choses :

  · il consigne le SCHÉMA de faute relevé pour chacun, ce qui fait apparaître
    que trente-quatre énoncés se ramènent à sept schémas seulement ;
  · il reproduit les trois calculs qui ont servi, pour qu'aucun chiffre cité
    dans les notes ne soit invérifiable.

Un mot sur la méthode. Un énoncé argumentatif n'a pas de valeur de vérité
tranchée par le calcul : il peut être sain, trop large, ou hors sujet. Nous
avons appliqué trois questions, dans cet ordre :

  1. Le raisonnement est-il valide en lui-même ?
  2. S'il l'est, sa portée est-elle celle que l'encadré lui donne ?
  3. Établit-il quelque chose de la FIGURE DE LA TERRE, ou d'autre chose ?

La troisième question est celle qui déclasse le plus d'énoncés, et c'est celle
qu'on oublie le plus facilement : un énoncé peut être entièrement vrai, bien
raisonné, bien sourcé, et ne rien établir de la thèse qu'il est censé soutenir.
"""

import math
import sys

# ── Les sept schémas ────────────────────────────────────────────────────────
SCHEMAS = {
    "SAIN": "raisonnement valide, portée juste — rien à corriger",
    "TROP LARGE": "raisonnement valide, mais conclusion plus vaste que ses prémisses",
    "ABSENCE": "argument tiré d'une absence — « jamais examiné », « jamais réfuté »",
    "AD HOMINEM": "porte sur une personne ou une institution, non sur une chose",
    "HORS SUJET": "peut être vrai sans rien établir de la figure de la Terre",
    "SOUDÉ": "deux affirmations de nature différente réunies en une seule",
    "RÉFUTÉ": "contredit par un calcul, ou par un autre encadré du même article",
}

# ── Le relevé, encadré par encadré ──────────────────────────────────────────
RELEVE = [
    (38, "200-ans-de-resultats-nuls", 8, "ABSENCE",
     "l'expérience d'Airy de 1871 examinait précisément cette hypothèse nulle"),
    (39, "chronologie-de-la-tromperie", 1, "SAIN", ""),
    (40, "chronologie-de-la-tromperie", 2, "SAIN", "coupe dans les deux sens"),
    (41, "chronologie-de-la-tromperie", 5, "SAIN", "Tycho est bien équivalent à Kepler"),
    (42, "chronologie-de-la-tromperie", 6, "SAIN", "coupe dans les deux sens"),
    (43, "chronologie-de-la-tromperie", 9, "TROP LARGE",
     "la « zone de silence » n'existe qu'en visibilité directe"),
    (44, "chronologie-de-la-tromperie", 10, "TROP LARGE",
     "juge un ensemble sur une seule de ses conséquences"),
    (45, "chronologie-de-la-tromperie", 11, "HORS SUJET", "porte sur Lambda, pas sur la Terre"),
    (46, "chronologie-de-la-tromperie", 12, "AD HOMINEM", "von Braun"),
    (47, "dune-terre-plate", 3, "TROP LARGE", "vrai à deux sites, faux à trois"),
    (48, "dune-terre-plate", 4, "TROP LARGE", "vrai de la genèse, faux de la base actuelle"),
    (49, "dune-terre-plate", 6, "SAIN", "les arguments d'Aristote sont bien des inférences"),
    (50, "la-cosmologie-instrument", 1, "HORS SUJET", "jeu de mots sur Philosophical Doctorate"),
    (51, "la-cosmologie-instrument", 2, "AD HOMINEM", "convictions de Hawking"),
    (52, "la-gravite-70-theories", 5, "HORS SUJET", "doublon du n°45"),
    (53, "la-rotation-terrestre", 5, "RÉFUTÉ", "décomposition des 38 µs, voir ci-dessous"),
    (54, "les-distances-cosmiques", 3, "SAIN", ""),
    (55, "les-trous-noirs", 7, "SOUDÉ", "circularité méthodologique + pressions institutionnelles"),
    (56, "ligo-londe", 3, "TROP LARGE", "le filtrage adapté n'est pas circulaire au sens vicieux"),
    (57, "ligo-londe", 4, "ABSENCE", "« aucune réfutation définitive » renverse la charge"),
    (58, "lire-le-ciel", 2, "SAIN", "et c'est la circularité du protocole du pôle"),
    (59, "lire-le-ciel", 5, "SAIN", "un des mieux fondés de l'inventaire"),
    (60, "neptune-et-pluton", 5, "TROP LARGE", "un paramètre ajusté qui prédit cesse d'être circulaire"),
    (61, "pourquoi-tout-remettre", 1, "TROP LARGE", "l'observation peut faire des prédictions risquées"),
    (62, "pourquoi-tout-remettre", 3, "TROP LARGE", "Woodward admet les expériences naturelles"),
    (63, "pourquoi-tout-remettre", 5, "SAIN", "mais hors sujet pour la figure de la Terre"),
    (64, "la-lune-six-anomalies", 3, "RÉFUTÉ", "le mois synodique varie, voir ci-dessous"),
    (65, "la-perspective-pourquoi", 4, "RÉFUTÉ", "les trois prédictions tombent, voir ci-dessous"),
    (66, "le-theodolite-celeste", 2, "TROP LARGE", "cohérence interne n'est pas comparaison"),
    (67, "mesurer-la-courbure", 3, "SAIN", "compliment méthodologique mérité"),
    (68, "vols-avion", 1, "TROP LARGE", "les manuels disent aussi pourquoi"),
    (69, "vols-avion", 7, "RÉFUTÉ", "par l'encadré n°8 du même article"),
    (70, "dhu-al-qarnayn", 2, "SAIN", "mais relève de la pile textuelle"),
    (71, "monter-les-trois-mires", 2, "SAIN", "paramètres à verser au dossier"),
]


def calcul_gps():
    c_, G, M, Re, r = 299792458.0, 6.674e-11, 5.972e24, 6371000.0, 26560000.0
    grav = (G * M / c_ ** 2) * (1 / Re - 1 / r) * 86400e6
    v = math.sqrt(G * M / r)
    cin = -0.5 * (v / c_) ** 2 * 86400e6
    vt = 2 * math.pi * Re / 86164.0
    sol = +0.5 * (vt / c_) ** 2 * 86400e6
    return [
        "   terme d'altitude seul (gravitationnel) : %+6.1f µs/jour" % grav,
        "   vitesse orbitale du satellite          : %+6.1f µs/jour" % cin,
        "   vitesse de la station au sol           : %+6.1f µs/jour" % sol,
        "   ───────────────────────────────────────────────────────",
        "   net                                    : %+6.1f µs/jour" % (grav + cin + sol),
        "",
        "   Un modèle « altitude-fréquence » seul prédirait %+.0f µs, pas 38." % grav,
        "   L'écart vaut %.0f %% et se mesure sans difficulté." % (100 * abs(cin) / (grav + cin + sol)),
    ]


def calcul_lunaison():
    return [
        "   minimum observé : 29,27 jours",
        "   moyenne         : 29,53 jours",
        "   maximum observé : 29,83 jours",
        "   amplitude       : %.2f jour = %.0f heures = %.1f %%"
        % (29.83 - 29.27, (29.83 - 29.27) * 24, 100 * (29.83 - 29.27) / 29.53),
        "",
        "   « Strictement identique » est faux, et cette variation est calculée",
        "   par le modèle standard à partir des excentricités.",
    ]


def calcul_trois_predictions():
    R = 6371000.0
    Rp = R / 0.87
    dip = math.degrees(math.acos(Rp / (Rp + 3107.0))) * 60
    h = 39040.0
    d_ = math.degrees(math.acos(R / (R + h)))
    rho = 90 - d_
    b = math.radians(15.0)
    sag = abs(math.degrees(math.acos(math.cos(math.radians(rho)) / math.cos(b))) - rho)
    return [
        "   « l'horizon reste au niveau des yeux »",
        "      il descend de %.0f′ depuis 3 107 m — protocole de dépression" % dip,
        "   « les objets zoomés réapparaissent »",
        "      la hauteur masquée ne dépend pas du grossissement — contrôle n°2",
        "   « la courbure filmée disparaît avec un objectif standard »",
        "      sa flèche vaut %.2f° sur 30° de champ à 39 km — contrôle n°30" % sag,
    ]


CALCULS = [
    (53, "Décomposition des 38 µs/jour du GPS", calcul_gps),
    (64, "Variation réelle du mois synodique", calcul_lunaison),
    (65, "Les trois prédictions de « la perspective »", calcul_trois_predictions),
]


def main():
    print("═" * 74)
    print("CONTRÔLES N°38 À 71 — ENCADRÉS ARGUMENTATIFS ET NARRATIFS")
    print("═" * 74)
    print()
    print("Les sept schémas relevés :")
    for k, v in SCHEMAS.items():
        print("   %-12s %s" % (k, v))
    print()
    print("─" * 74)
    print("  %-5s %-30s %-6s %-12s %s" % ("n°", "article", "encadré", "schéma", "note"))
    print("─" * 74)
    for n, art, enc, sch, note in RELEVE:
        print("  %-5d %-30s %-6d %-12s %s" % (n, art[:30], enc, sch, note[:26]))
    print("─" * 74)
    print()
    from collections import Counter
    cpt = Counter(s for _, _, _, s, _ in RELEVE)
    print("Répartition :")
    for k, v in cpt.most_common():
        print("   %-12s %2d" % (k, v))
    print()
    print("Trente-quatre énoncés, sept schémas. Le plus fréquent est TROP LARGE :")
    print("un raisonnement valide dont la conclusion excède les prémisses. C'est")
    print("aussi le plus facile à corriger — il suffit de resserrer l'énoncé.")
    print()
    for n, titre, f in CALCULS:
        print("┌─ n°%d · %s" % (n, titre))
        print("└" + "─" * 71)
        for l in f():
            print("   " + l)
        print()
    print("═" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
