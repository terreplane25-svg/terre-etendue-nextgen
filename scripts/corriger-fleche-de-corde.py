#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Termine la correction des « bosses » dans « L'eau ne ment pas ».

Un passage antérieur avait corrigé le tableau de synthèse de l'article : chaque
ligne y porte désormais le nom de la grandeur qui lui convient, et le canal de
Suez y vaut 731 m de flèche de corde et non 2 930. Le registre des corrections
l'annonce ainsi.

Le balayage montre que ce passage s'est arrêté au tableau de synthèse. Le corps
de l'article, ses encadrés « En clair », ses figures SVG et le tableau des
ouvrages d'art annonçaient toujours les anciennes valeurs — celles de
<code>d²/2R</code>, qui mesure la chute par rapport au plan tangent pris à une
extrémité, non le renflement au milieu d'une nappe d'eau. Suez y valait encore
2 930 m dans le texte et dans une figure, l'Alaska 130 km, les crues 200 m.

Un article qui se corrige dans son tableau et se contredit trois paragraphes
plus haut est pire qu'un article non corrigé : le lecteur qui compare y voit,
à juste titre, qu'on n'a pas relu.

Les trois grandeurs, pour mémoire :
  chute de courbure   d²/2R      écart au plan tangent pris au départ
  flèche de corde     L²/8R      renflement au milieu d'une corde — canaux, nappes
  hauteur masquée     formule exacte, dépend de la hauteur d'œil — visibilité

Aucune conclusion de l'article ne change : les flèches justes valent le quart
des chutes annoncées, et un canal de 193 km qui devrait bomber de 731 m au
milieu sans écluse pose exactement la même question qu'à 2 930 m.
"""
import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN = os.path.join(RACINE, "content", "articles", "leau-ne-ment-pas.json")
R = 6371000.0


def controle():
    """Les valeurs inscrites ci-dessous, recalculées avant toute écriture."""
    for nom, L, attendu in [("Suez", 193000, 731), ("Panama", 82000, 132),
                            ("Nîmes", 50000, 49), ("Alaska", 1287000, 32500),
                            ("lac 20 km", 20000, 7.85), ("crue 50 km", 50000, 49)]:
        got = L * L / (8 * R)
        if abs(got - attendu) > max(1.0, attendu * 0.002):
            sys.exit("Flèche %s : %.1f m, attendu %s" % (nom, got, attendu))
    if abs(193000 ** 2 / (2 * R) - 2923) > 1:
        sys.exit("Chute de courbure Suez incorrecte")
    print("Contrôle numérique : les 7 valeurs se recalculent.")


PAIRES = [
    # ── Section 01 : le tableau pédagogique des deux grandeurs ──────────────
    # La ligne portait « (Suez) », ce qui rattachait un canal à la chute de
    # courbure — l'erreur même que l'article corrige plus loin.
    ("<td>193 km (Suez)</td><td>2 930 m</td><td>2402 m</td>",
     "<td>193 km</td><td>2 923 m</td><td>2&#8239;402 m</td>"),

    # Le renflement au milieu d'un lac est une flèche de corde, pas une chute
    # de courbure. Le laser, lui, suit bien la tangente — mais raboté par (1−k).
    ("Sur un lac de 20 km, la surface de l'eau devrait former une « bosse » de "
     "31,4 m en son centre. Un laser au ras de l'eau d'une rive à l'autre devrait "
     "manquer la cible de plus de 31 m.",
     "Sur un lac de 20 km, la surface de l'eau devrait bomber de 7,85 m en son "
     "milieu par rapport à la corde qui joint les deux rives&nbsp;: c'est la flèche "
     "de corde, <code>L&#178;/8R</code>. Un laser tiré au ras de l'eau, lui, suit "
     "la tangente&nbsp;: il devrait toucher la rive d'en face 31,4 m trop haut, "
     "27,3 m une fois la réfraction standard prise en compte."),

    # La figure annonçait « hauteur cachée » pour d²/2R — le mot même que
    # l'article emploie ailleurs pour la grandeur qui décide de la visibilité.
    ('<text x="350" y="110" text-anchor="middle" fill="#cc4444" font-size="9" '
     'font-family="monospace">hauteur cachée</text>',
     '<text x="350" y="110" text-anchor="middle" fill="#cc4444" font-size="9" '
     'font-family="monospace">chute de courbure</text>'),

    # ── Section 02 : l'encadré « En clair » sur les crues ───────────────────
    ("le milieu de cette nappe devrait gonfler de près de 200 m",
     "le milieu de cette nappe devrait gonfler de 49 m"),

    # ── Section 03 : le canal de Bedford ────────────────────────────────────
    ("des cibles placées au ras de l'eau restent intégralement visibles alors que "
     "la courbure théorique devrait en masquer plus de 7 mètres.",
     "des cibles placées au ras de l'eau restent intégralement visibles alors que "
     "la sphère devrait en masquer 4,7 m, la lunette étant à 20 cm au-dessus de "
     "l'eau — de quoi cacher entièrement un drapeau à 1,50 m."),
    ("le bas du repère devrait se cacher derrière le renflement de l'eau — ici, "
     "environ 7 m, soit deux étages.",
     "le bas du repère devrait se cacher derrière le renflement de l'eau — ici, "
     "4,7 m, soit un étage et demi."),

    # ── Section 04 : Chicago depuis Michigan City ───────────────────────────
    # Le tableau de la section porte 203 m depuis le passage précédent ; ce
    # paragraphe-ci annonçait encore 283, la valeur de d²/2R.
    ("Selon la formule, les 283 premiers mètres du bas devraient être cachés "
     "derrière la courbure. La Willis Tower culmine à 442 m — seuls les ~159 m "
     "supérieurs devraient être visibles.",
     "Depuis un œil à 2 m et au coefficient de réfraction standard, la sphère y "
     "masque 203 m comptés depuis la base. La Willis Tower culmine à 442 m — seuls "
     "les 239 m supérieurs devraient être visibles, et le bas des tours, lui, ne "
     "devrait pas l'être du tout."),
    ("et encore 119&nbsp;m au coefficient extrême k = 0,47",
     "et encore 117&nbsp;m au coefficient extrême k = 0,47"),

    # ── Section 05 : l'encadré « En clair » sur le laser ────────────────────
    ("devrait toucher la rive d'en face nettement plus haut — environ 8 m sur 10 km.",
     "devrait toucher la rive d'en face nettement plus haut — 6,8 m sur 10 km, "
     "réfraction standard comprise."),

    # ── Section 06 : les ouvrages d'art ─────────────────────────────────────
    ("Selon la formule, la « bosse » théorique au milieu devrait être de "
     "<strong>~2 930 mètres</strong>.",
     "Sur une sphère, le milieu du canal devrait se trouver <strong>731 mètres</strong> "
     "au-dessus de la corde joignant ses deux extrémités — c'est la flèche de corde, "
     "<code>L&#178;/8R</code>, et non la chute de courbure que nous donnions ici."),
    ('font-family="monospace">Courbure théorique : 2 930 m de « bosse »</text>',
     'font-family="monospace">Flèche de corde : 731 m au milieu</text>'),
    ("1 287 km de Prudhoe Bay à Valdez · Courbure théorique : ~130 km de « bosse »",
     "1 287 km de Prudhoe Bay à Valdez · Flèche de corde : 32,5 km au milieu"),
    ("<th>Courbure théorique</th>",
     "<th>Flèche de corde<br><small>L&#178;/8R</small></th>"),
    ("<td>Canal de Suez</td><td>193 km</td><td>~2 930 m</td>",
     "<td>Canal de Suez</td><td>193 km</td><td>731 m</td>"),
    ("<td>Canal de Panama</td><td>82 km</td><td>~527 m</td>",
     "<td>Canal de Panama</td><td>82 km</td><td>132 m</td>"),
    ("<td>Aqueduc de Nîmes (romain)</td><td>50 km</td><td>~196 m</td>",
     "<td>Aqueduc de Nîmes (romain)</td><td>50 km</td><td>49 m</td>"),
    ("<td>Alaska Pipeline</td><td>1 287 km</td><td>~130 000 m</td>",
     "<td>Alaska Pipeline</td><td>1 287 km</td><td>32 500 m</td>"),
]


def main():
    controle()
    with open(CHEMIN, encoding="utf-8") as f:
        art = json.load(f)
    html = art["htmlBody"]
    for avant, apres in PAIRES:
        n = html.count(avant)
        if n != 1:
            sys.exit("« %s… » apparaît %d fois — rien n'est écrit." % (avant[:70], n))
        html = html.replace(avant, apres)
    art["htmlBody"] = html
    with open(CHEMIN, "w", encoding="utf-8") as f:
        json.dump(art, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("%d passages corrigés." % len(PAIRES))


if __name__ == "__main__":
    main()
