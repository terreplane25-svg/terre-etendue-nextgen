#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retire les cinq copies de Vincenty et les remplace par un import du paquet.

Ce que cette dette coûtait
──────────────────────────
La géodésique inverse vivait en cinq exemplaires hors de `visee_optique` : le
pré-écran altimétrique et les quatre `case_data.py`. Elle est pourtant ce qui
produit le D et l'azimut dont dépendent le rayon d'Euler et toute la géométrie
du §9. Les cinq copies donnaient le même résultat — le risque était latent, pas
réalisé — mais aucune n'était couverte par un test, et le jour où l'une aurait
divergé, rien ne l'aurait signalé.

Ce que le script change
───────────────────────
Chaque copie est supprimée et remplacée par un import depuis le paquet, qui
porte désormais vingt-six tests. Deux conséquences visibles aux appelants :

  · `vincenty_inverse` rend un `GeodesiqueInverse` et non plus un triplet ;
  · le troisième membre du triplet s'appelait `azimut_2_vers_1`, ce qui
    annonce le gisement de retour, alors que la formule rend α₂ — l'azimut
    AU POINT D'ARRIVÉE, dans le même sens de parcours. Les quatre appelants
    le rangeaient dans une variable nommée `_az_retour` et l'ignoraient ; la
    variable est renommée pour que le nom cesse de circuler.

Les trois `case_data.py` de Cordouan, Garoupe et Sangatte définissaient une
copie qu'aucun code n'appelait jamais : elle disparaît sans remplacement, les
`run_case.py` correspondants important directement depuis le paquet.

Chaque ancre est comptée avant écriture ; une ancre vue autrement qu'une fois
arrête tout sans rien modifier.
"""
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTILS = os.path.join(RACINE, "outils")
CAS = ("cas-chassiron", "cas-cordouan", "cas-garoupe", "cas-sangatte")

IMPORT_PAQUET = '''# --- Géodésie : importée du paquet, jamais recopiée ---
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
'''

BOOTSTRAP = '''# Les trois paquets sont rendus importables par le module commun, qui les
# cherche d'abord parmi les paquets installés puis, à défaut, à côté de ce
# fichier. Les chemins codés en dur d'origine — /home/claude/... — n'existaient
# que sur la machine où ces cas ont été écrits.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "commun"))
from bootstrap import preparer_chemins  # noqa: E402
preparer_chemins()
'''


def compter(texte, motif, etiquette, attendu=1):
    n = texte.count(motif)
    if n != attendu:
        sys.exit("ancre « %s » vue %d fois — attendu %d." % (etiquette, n, attendu))
    return n


def bloc_vincenty(source, chemin):
    """Le texte à retirer : du commentaire de section à la définition suivante."""
    debut = re.search(r"^# --- (?:Algorithme g[ée]od[ée]sique|G[ée]od[ée]sie) ?:", source, re.M)
    if not debut:
        sys.exit("commentaire de section géodésique introuvable dans %s" % chemin)
    apres = re.search(
        r"^(# --- (?!Algorithme g|G[ée]od)|def (?!vincenty_)|class )",
        source[debut.end():], re.M)
    fin = len(source) if not apres else debut.end() + apres.start()
    return source[debut.start():fin]


def traiter_case_data(nom):
    chemin = os.path.join(OUTILS, "exemples-cas-etudes", nom, "case_data.py")
    s = open(chemin, encoding="utf-8").read()
    bloc = bloc_vincenty(s, chemin)
    compter(s, bloc, "bloc Vincenty de %s" % nom)
    s = s.replace(bloc, IMPORT_PAQUET + "\n\n")

    if nom == "cas-chassiron":
        # Le seul cas qui appelle réellement Vincenty dans son case_data.
        vieux = ("    distance_totale, azimut, _ = vincenty_inverse("
                 "chassiron_lat, chassiron_lon, cordouan_lat, cordouan_lon, a, f)")
        compter(s, vieux, "appel de chassiron")
        s = s.replace(vieux,
                      "    geo = vincenty_inverse(chassiron_lat, chassiron_lon, "
                      "cordouan_lat, cordouan_lon, a, f)\n"
                      "    distance_totale, azimut = geo.distance_m, geo.azimut_depart_deg")

    # `math` peut devenir inutile ; on ne le retire que s'il ne sert plus.
    if re.search(r"\bmath\.", s) is None:
        s = re.sub(r"^import math\n", "", s, count=1, flags=re.M)
    open(chemin, "w", encoding="utf-8").write(s)
    return len(bloc.split("\n"))


def traiter_run_case(nom):
    chemin = os.path.join(OUTILS, "exemples-cas-etudes", nom, "run_case.py")
    s = open(chemin, encoding="utf-8").read()

    # 1. Les trois chemins codés en dur.
    vieux = ('sys.path.insert(0, "/home/claude/visee-optique")\n'
             'sys.path.insert(0, "/home/claude/preuve-image")\n'
             'sys.path.insert(0, "/home/claude/rapport-expertise")\n')
    compter(s, vieux, "chemins codés en dur de %s" % nom)
    s = s.replace(vieux, BOOTSTRAP)
    if not re.search(r"^from pathlib import Path$", s, re.M):
        compter(s, "\nimport sys\n", "import sys de %s" % nom)
        s = s.replace("\nimport sys\n", "\nimport sys\nfrom pathlib import Path\n", 1)

    # 2. L'appel qui dépaquetait un triplet.
    m = re.search(r"    D, az_aller, _az_retour = case_data\.vincenty_inverse\(\n"
                  r"((?:.*\n)*?)    \)\n", s)
    if not m:
        sys.exit("appel de vincenty_inverse introuvable dans %s" % chemin)
    s = s[:m.start()] + (
        "    geo = case_data.vincenty_inverse(\n" + m.group(1) + "    )\n"
        "    # az_arrivee est l'azimut AU POINT D'ARRIVÉE (α₂), pas le gisement de\n"
        "    # retour : il n'est pas employé ici, mais son nom ne doit pas mentir.\n"
        "    D, az_aller = geo.distance_m, geo.azimut_depart_deg\n"
    ) + s[m.end():]

    s = s.replace("case_data.vincenty_inverse, à partir des coordonnées sourcées",
                  "visee_optique.geodesy.vincenty_inverse, à partir des coordonnées sourcées")
    s = s.replace("voir case_data.vincenty_inverse ", "voir visee_optique.geodesy.vincenty_inverse ")
    open(chemin, "w", encoding="utf-8").write(s)


def traiter_pre_ecran():
    chemin = os.path.join(OUTILS, "outil-bonus-pre-ecran", "profil_altimetrique.py")
    s = open(chemin, encoding="utf-8").read()
    bloc = bloc_vincenty(s, chemin)
    compter(s, bloc, "bloc Vincenty du pré-écran")

    # Les constantes du bloc servent ailleurs dans le fichier : on les garde,
    # mais comme alias du paquet, pas comme nombres recopiés.
    remplacement = (
        IMPORT_PAQUET
        + "\nA_GRS80 = GRS80_A\nF_GRS80 = GRS80_F\n\n"
        + "SEUIL_TERRE_M = 0.0  # toute élévation > 0 m est du relief, donc invalidante\n"
        + "SENTINEL_MER_MAX = -1000.0  # en dessous : hors couverture, donc mer\n"
        + 'RESOURCE_IGN = "ign_rge_alti_wld"\n'
        + 'URL_BASE_IGN = "https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json"\n\n\n'
    )
    s = s.replace(bloc, remplacement)

    vieux = "    distance_totale, azimut, _ = vincenty_inverse(lat1, lon1, lat2, lon2, a, f)"
    compter(s, vieux, "appel du pré-écran")
    s = s.replace(vieux,
                  "    geo = vincenty_inverse(lat1, lon1, lat2, lon2, a, f)\n"
                  "    distance_totale, azimut = geo.distance_m, geo.azimut_depart_deg")
    open(chemin, "w", encoding="utf-8").write(s)
    return len(bloc.split("\n"))


def main():
    total = 0
    for nom in CAS:
        n = traiter_case_data(nom)
        traiter_run_case(nom)
        print("  %-14s copie retirée (%d lignes), chemins et appel corrigés" % (nom, n))
        total += n
    n = traiter_pre_ecran()
    print("  %-14s copie retirée (%d lignes)" % ("pré-écran", n))
    total += n
    print("\n%d lignes de Vincenty dupliquée retirées ; une seule implémentation "
          "subsiste, dans visee_optique.geodesy." % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
