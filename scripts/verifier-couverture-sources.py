#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contrôle de couverture de la liste de vérification des sources.

content/corrections/a-verifier-sources.md dit, pour chaque encadré reposant sur
une source externe, ce qu'il faut ouvrir et quelle question poser. Ce script
vérifie que le document couvre EXACTEMENT les encadrés concernés : ni un de
moins, ni un de trop.

Pourquoi ce contrôle
────────────────────
Une liste de tâches qui prétend être complète et ne l'est pas est pire qu'une
liste franchement partielle : elle donne l'impression d'avoir fait le tour. Le
risque est réel ici, parce que le document est écrit à la main tandis que la
liste des encadrés à couvrir évolue — chaque verdict posé en retire un.

Le document abrège les slugs pour tenir en largeur de tableau. L'appariement se
fait donc par préfixe, et le script signale les préfixes AMBIGUS : un préfixe
qui désigne deux articles ne prouve pas qu'on a traité les deux.

    python3 scripts/verifier-couverture-sources.py
"""

import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LISTE = os.path.join(RACINE, "content", "corrections", "a-verifier-sources.md")
TRI = os.path.join(RACINE, "scripts", "trier-faits-etablis.py")


def charger_tri():
    ns = {"__name__": "x", "__file__": TRI}
    exec(open(TRI, encoding="utf-8").read(), ns)
    return ns["relever"](), ns["classer"]


def attendus():
    """Les (slug, n) non tranchés des piles textuelle et historique."""
    lignes, classer = charger_tri()
    return {(s, n) for _, s, n, t, v in lignes
            if not v and classer(t, (s, n)) in ("TEXTUEL", "HISTORIQUE")}


def couverts(cibles):
    """Apparie les mentions du document aux cibles, par préfixe de slug.

    Le document emploie deux conventions d'écriture que le lecteur doit suivre :

      · des LIGNES DE CONTINUATION, où le slug n'est pas répété — « | n°2 | … »
        sous une première ligne qui l'a nommé. Le dernier slug rencontré est donc
        reporté tant qu'un nouveau n'apparaît pas ;
      · des LISTES DE NUMÉROS sur une même ligne — « n°1, n°2, n°5 » — quand
        plusieurs encadrés appellent la même vérification.

    Ces deux conventions rendent le document lisible ; c'est au contrôle de s'y
    plier, non au document de s'aplatir pour être contrôlable.
    """
    trouves, ambigus = set(), []
    courant = None
    for ligne in open(LISTE, encoding="utf-8"):
        m = re.search(r"`([a-z0-9-]+)`", ligne)
        if m and re.search(r"n°\d", ligne):
            courant = m.group(1)
        elif m and ligne.lstrip().startswith("|"):
            courant = m.group(1)
        if courant is None:
            continue
        for num in re.findall(r"n°(\d+)", ligne):
            n = int(num)
            candidats = [(s, k) for (s, k) in cibles
                         if s.startswith(courant) and k == n]
            if len(candidats) > 1:
                ambigus.append((courant, n, [s for s, _ in candidats]))
            trouves.update(candidats)
    return trouves, ambigus


def main():
    cibles = attendus()
    trouves, ambigus = couverts(cibles)
    manquants = sorted(cibles - trouves)

    print("═" * 74)
    print("COUVERTURE DE LA LISTE DE VÉRIFICATION DES SOURCES")
    print("═" * 74)
    print("  encadrés à couvrir : %d" % len(cibles))
    print("  couverts           : %d" % len(trouves))
    print("  manquants          : %d" % len(manquants))
    print()

    if ambigus:
        print("  Préfixes ambigus — ils désignent plusieurs articles :")
        for p, n, arts in ambigus:
            print("    `%s` n°%d → %s" % (p, n, ", ".join(arts)))
        print()

    if manquants:
        print("  Encadrés non couverts par la liste :")
        for s, n in manquants:
            print("    %s n°%d" % (s, n))
        print()
        print("  Le document se dit complet : il ne l'est pas. Compléter ou")
        print("  retirer la prétention à l'exhaustivité.")
        return 1

    print("  ✓ La liste couvre l'intégralité des encadrés concernés.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
