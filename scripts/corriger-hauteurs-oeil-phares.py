#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Harmonise les hauteurs d'œil et les seuils de réfraction.

Trois défauts trouvés au balayage, tous du même genre : une hauteur masquée
citée sans la hauteur d'œil qui la produit, puis mélangée à une valeur calculée
pour une autre hauteur d'œil.

1. Section 09 (phares) calcule tout à l'œil de 4,6 m des tables nautiques.
   L'encadré-clé de cette section y collait 210 m — valeur du tableau de la
   section 14, qui place l'observateur à 20 m sur la passerelle d'un navire.
   À 4,6 m, l'extrême k = 0,47 laisse 283 m masqués, seize fois la hauteur du feu.

2. La question fréquente sur Port-Saïd annonçait « 466 m sans aucune réfraction,
   491 m au coefficient standard ». C'est physiquement impossible dans cet ordre :
   moins il y a de réfraction, plus la sphère masque. Le 466 venait du tableau à
   20 m, le 491 de la section à 4,6 m. À 4,6 m la série est 572 / 491 / 283.

3. Le seuil de réfraction qui découvrirait la base était donné à « 0,96 » pour
   Port-Saïd et « 0,96 à 0,99 » pour les trois cas de la section 14. Le seuil
   exact est celui où l'horizon de l'observateur atteint l'objet, soit
   R′ = (d² − h₁²)/2h₁ puis k = 1 − R/R′. Il vaut 0,993 pour Port-Saïd à 4,6 m,
   et de 0,97 à 0,9996 pour les trois cas — des rayons apparents de 34 à 2 279
   fois celui de la Terre, pas « vingt fois ».

Les chiffres corrigés sont tous plus défavorables à notre propre thèse que ceux
qu'ils remplacent, sauf le 283 qui est plus favorable. C'est le hasard du calcul,
pas un choix ; ils sont retenus parce qu'ils sont justes.

Vérification indépendante des valeurs employées ici, avec R = 6 371 km :
    a = √((R′+h₁)² − R′²)   puis   cachée = √(R′² + (d−a)²) − R′
"""
import json
import math
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = 6371000.0


def cachee(h1, d, k=0.13):
    Rp = R / (1 - k)
    a = math.sqrt((Rp + h1) ** 2 - Rp ** 2)
    return max(0.0, math.sqrt(Rp ** 2 + (d - a) ** 2) - Rp)


def k_base(h1, d):
    """Le coefficient qui amènerait l'horizon jusqu'à l'objet — base découverte."""
    Rp = (d * d - h1 * h1) / (2 * h1)
    return 1 - R / Rp, Rp / R


def controle():
    """Aucune écriture si un seul des chiffres inscrits ne se recalcule pas."""
    attendu = [
        (4.6, 93000, 0.00, 572), (4.6, 93000, 0.13, 491), (4.6, 93000, 0.47, 283),
        (20.0, 93000, 0.13, 393), (2.0, 241000, 0.13, 3789), (2.0, 97000, 0.47, 337),
    ]
    for h1, d, k, val in attendu:
        got = round(cachee(h1, d, k))
        if got != val:
            sys.exit("Contrôle échoué : h₁=%s d=%s k=%s → %s, attendu %s"
                     % (h1, d, k, got, val))
    for h1, d, k, rap in [(20.0, 93000, 0.970, 34), (2.0, 97000, 0.997, 369),
                          (2.0, 241000, 0.9996, 2279)]:
        kk, rr = k_base(h1, d)
        if abs(kk - k) > 0.001 or abs(rr - rap) > 1:
            sys.exit("Seuil échoué : h₁=%s d=%s → k=%.4f R′/R=%.0f" % (h1, d, kk, rr))
    print("Contrôle numérique : les 9 valeurs se recalculent.")


REMPLACEMENTS = {
    "la-perspective-pourquoi-les-objets-disparaissent": [
        # La colonne doit dire à quelle hauteur d'œil elle est calculée : c'est
        # cette omission qui a permis le mélange avec le tableau de la section 14.
        ("<th>masqué depuis la base</th>",
         "<th>masqué depuis la base<br><small>œil à 4,6&nbsp;m, k = 0,13</small></th>"),

        # Espace fine manquante sur un millier.
        ("3699&nbsp;m", "3&#8239;699&nbsp;m"),

        # Deux hauteurs de tour dans le même article pour le même ouvrage.
        ("Great Grimsby (91,5 m)", "Great Grimsby (94&nbsp;m)"),

        # L'encadré mélangeait 491 m (œil à 4,6 m) et 210 m (œil à 20 m).
        ("il resterait 210&nbsp;m masqués, soit douze fois la hauteur du feu.",
         "il resterait 283&nbsp;m masqués, soit seize fois la hauteur du feu. "
         "Les hauteurs masquées de cette section sont toutes calculées pour l'œil "
         "à 4,6&nbsp;m des tables nautiques&nbsp;; la section&nbsp;13 reprend le "
         "même phare depuis la passerelle d'un navire, à 20&nbsp;m, et trouve "
         "393&nbsp;m. La conclusion ne dépend pas de ce choix."),

        # L'ordre annoncé était physiquement impossible.
        ("la sphère masque 466&nbsp;m sans aucune réfraction, 491&nbsp;m au "
         "coefficient standard, et encore <strong>210&nbsp;m au coefficient extrême "
         "k = 0,47</strong>, soit douze fois la hauteur du feu. Il faudrait "
         "k ≈ 0,96 pour que sa base se découvre.",
         "la sphère masque 572&nbsp;m sans aucune réfraction, 491&nbsp;m au "
         "coefficient standard, et encore <strong>283&nbsp;m au coefficient extrême "
         "k = 0,47</strong>, soit seize fois la hauteur du feu&nbsp;— ces trois "
         "valeurs pour l'œil à 4,6&nbsp;m des tables nautiques. Plus la réfraction "
         "est forte, moins la sphère masque&nbsp;: pour que la base du feu se "
         "découvre, il faudrait k ≈ 0,99, c'est-à-dire un rayon apparent cent "
         "quarante-huit fois celui de la Terre, tenu sur les 93&nbsp;kilomètres "
         "de la visée."),

        # Le seuil des trois cas de la section 14, calculé pour chacun.
        ("Pour que la base redevienne visible dans ces trois cas, il faudrait un "
         "coefficient voisin de <strong>0,96 à 0,99</strong> — soit un rayon "
         "apparent vingt fois celui de la Terre, sur toute la longueur de la visée.",
         "Pour que la base redevienne visible, il faudrait un coefficient de "
         "<strong>0,97</strong> pour le phare, <strong>0,997</strong> pour Chicago "
         "et <strong>0,9996</strong> pour Anvers — soit un rayon apparent de "
         "trente-quatre à deux mille deux cent soixante-dix-neuf fois celui de la "
         "Terre, tenu sur toute la longueur de la visée."),
    ],
    "etat-des-lieux-ou-en-sommes-nous": [
        # « Ces trois objets restent entièrement masqués » était faux du troisième :
        # à k = 0,47 la sphère ne masque plus que 337 m à Chicago, et la Willis
        # Tower en fait 442. Le haut affleurerait ; c'est la base qui décide.
        ("Phares (Port-Saïd, feu de 18&nbsp;m rapporté visible à 93&nbsp;km, "
         "491&nbsp;m masqués), îles (Elbe à 201&nbsp;km depuis Gênes, "
         "2&#8239;298&nbsp;m masqués pour un sommet de 1&#8239;019), skylines "
         "(Chicago à 97&nbsp;km, 573&nbsp;m masqués pour une tour de 442). "
         "La réfraction entre par le coefficient k&nbsp;: même à sa valeur extrême "
         "de 0,47, ces trois objets restent entièrement masqués.",
         "Phares (Port-Saïd, feu de 18&nbsp;m rapporté visible à 93&nbsp;km, "
         "491&nbsp;m masqués pour l'œil à 4,6&nbsp;m des tables nautiques), îles "
         "(Elbe à 201&nbsp;km depuis Gênes, 2&#8239;298&nbsp;m masqués pour un "
         "sommet de 1&#8239;019, œil à 21&nbsp;m), skylines (Chicago à 97&nbsp;km, "
         "573&nbsp;m masqués pour une tour de 442, œil à 2&nbsp;m). La réfraction "
         "entre par le coefficient k&nbsp;: à sa valeur extrême de 0,47, le phare "
         "et l'île restent entièrement masqués&nbsp;; à Chicago il resterait "
         "337&nbsp;m masqués, de sorte que le haut de la tour pourrait affleurer "
         "sur 105&nbsp;m — mais pas sa base, qui est ce que montrent les clichés."),
    ],
}


def main():
    controle()
    charges = {}
    for slug, paires in REMPLACEMENTS.items():
        chemin = os.path.join(RACINE, "content", "articles", slug + ".json")
        with open(chemin, encoding="utf-8") as f:
            art = json.load(f)
        html = art["htmlBody"]
        for avant, apres in paires:
            n = html.count(avant)
            if n != 1:
                sys.exit("« %s… » apparaît %d fois dans %s — rien n'est écrit."
                         % (avant[:60], n, slug))
            html = html.replace(avant, apres)
        art["htmlBody"] = html
        charges[chemin] = art

    # Tout est vérifié avant que quoi que ce soit ne soit écrit : un script qui
    # écrit dans sa boucle laisse un article corrigé et l'autre non.
    for chemin, art in charges.items():
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(art, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print("%d articles réécrits." % len(charges))


if __name__ == "__main__":
    main()
