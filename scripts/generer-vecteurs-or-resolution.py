#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vecteurs d'or de l'analyse de résolution (outil B).

CE QUE CES VECTEURS ÉPINGLENT
─────────────────────────────
La confrontation mesure / déclaration, qui est tout l'apport du module : un
écart ÉTABLIT que le fichier a été redimensionné sans que la métadonnée suive.
Les phrases sont comparées caractère par caractère — une divergence
d'apostrophe entre les deux implémentations s'est produite quatre fois dans ce
dépôt, et elle est invisible à l'œil.

CONTRÔLE AVANT ÉCRITURE
───────────────────────
Le script revérifie que ses cas DISCRIMINENT : qu'un écart existe ET une
cohérence, qu'une absence rend None et non False, qu'un rapport non trivial est
présent, et que le registre d'écrans reste vide.

    python3 scripts/generer-vecteurs-or-resolution.py
"""
import json
import os
import sys
from datetime import datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
PAQUET_B = os.path.join(RACINE, "outils", "outil-B-preuve-image")
CIBLE = os.path.join(RACINE, "src", "lib", "preuve-image", "vecteurs-or-resolution.json")

sys.path.insert(0, PAQUET_B)
try:
    import preuve_image  # noqa: F401
except ImportError:
    if not os.path.exists(VENV):
        sys.exit("venv des outils absent : %s (voir outils/README.md)" % VENV)
    os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

from preuve_image.resolution import (  # noqa: E402
    DEFINITIONS_NOMMEES, ECRANS_CONNUS, MOTIF_ALIGNEMENT, MOTIF_AUCUN_ECRAN,
    MOTIF_DENOMINATION, analyser_resolution,
)

#: (nom, largeur mesurée, hauteur mesurée, largeur déclarée, hauteur déclarée)
CAS = [
    ("cohérent", 4032, 3024, 4032, 3024),
    # LE cas : un fichier redimensionné sans que l'EXIF suive.
    ("redimensionné sans que l'EXIF suive", 1024, 768, 4032, 3024),
    ("recadré à la marge", 4030, 3020, 4032, 3024),
    ("aucune déclaration", 4032, 3024, None, None),
    ("aucune mesure", None, None, 4032, 3024),
    ("ni l'un ni l'autre", None, None, None, None),
    ("portrait", 3024, 4032, 3024, 4032),
    ("carré", 1000, 1000, None, None),
    ("dénomination paysage", 1920, 1080, None, None),
    ("dénomination portrait", 1080, 1920, None, None),
    ("non aligné sur un bloc", 1023, 767, None, None),
    ("aligné sur 8 seulement", 1920, 1080, None, None),
    ("aligné sur 16", 1920, 1088, None, None),
    ("écran de téléphone, jamais rapproché", 1179, 2556, None, None),
    ("dimensions nulles", 0, 0, None, None),
    ("dimension négative", -1, 100, None, None),
]


def en_dict(r):
    return {
        "largeur_mesuree": r.largeur_mesuree,
        "hauteur_mesuree": r.hauteur_mesuree,
        "largeur_declaree": r.largeur_declaree,
        "hauteur_declaree": r.hauteur_declaree,
        "dimensions_coherentes": r.dimensions_coherentes,
        "motif_ecart": r.motif_ecart,
        "rapport": list(r.rapport) if r.rapport else None,
        "rapport_decimal": r.rapport_decimal,
        "orientation": r.orientation,
        "megapixels": r.megapixels,
        "denomination": r.denomination,
        "alignement_jpeg": r.alignement_jpeg,
        "ecran_rapproche": r.ecran_rapproche,
        "motif_aucun_ecran": r.motif_aucun_ecran,
    }


def main():
    v = {
        "genere_le": datetime.now(timezone.utc).isoformat(),
        "source": "preuve_image.resolution (paquet Python)",
        "avertissement": (
            "Fichier généré. Ne pas modifier à la main : il est la référence "
            "contre laquelle le port TypeScript est vérifié."
        ),
        "constantes": {
            "ecrans_connus": ECRANS_CONNUS,
            "definitions_nommees": {"%dx%d" % k: n for k, n in DEFINITIONS_NOMMEES.items()},
            "motif_aucun_ecran": MOTIF_AUCUN_ECRAN,
            "motif_denomination": MOTIF_DENOMINATION,
            "motif_alignement": MOTIF_ALIGNEMENT,
        },
        "cas": [
            {"nom": nom, "mesuree": [lm, hm], "declaree": [ld, hd],
             "resolution": en_dict(analyser_resolution(lm, hm, ld, hd))}
            for nom, lm, hm, ld, hd in CAS
        ],
    }
    controle(v)
    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Écrit : %s" % os.path.relpath(CIBLE, RACINE))
    print("  %d configurations" % len(v["cas"]))
    return 0


def controle(v):
    par_nom = {c["nom"]: c["resolution"] for c in v["cas"]}

    # 1. Un écart ET une cohérence existent : sans les deux, un port qui
    #    câblerait le verdict passerait.
    assert par_nom["redimensionné sans que l'EXIF suive"]["dimensions_coherentes"] is False
    assert par_nom["cohérent"]["dimensions_coherentes"] is True

    # 2. Une absence rend None, jamais False. Les confondre transformerait une
    #    lacune de donnée en indice.
    for nom in ("aucune déclaration", "aucune mesure", "ni l'un ni l'autre"):
        assert par_nom[nom]["dimensions_coherentes"] is None, nom
        assert par_nom[nom]["motif_ecart"] is None, nom

    # 3. Le motif d'écart nomme les DEUX jeux de dimensions et borne sa
    #    conclusion.
    m = par_nom["redimensionné sans que l'EXIF suive"]["motif_ecart"]
    assert "1024 × 768" in m and "4032 × 3024" in m
    assert "lequel des deux est le bon" in m

    # 4. Les trois orientations, et un rapport non trivial : 4:3 se réduit,
    #    1179 × 2556 aussi mais autrement.
    orientations = {x["orientation"] for x in par_nom.values() if x["orientation"]}
    assert orientations == {"paysage", "portrait", "carré"}, orientations
    assert par_nom["écran de téléphone, jamais rapproché"]["rapport"] == [131, 284]

    # 5. Les trois états d'alignement sont représentés.
    alignements = {x["alignement_jpeg"] for x in par_nom.values()}
    assert {None, 8, 16} <= alignements, alignements

    # 6. La dénomination se trouve dans les deux orientations, et manque là où
    #    il n'y en a pas.
    assert par_nom["dénomination paysage"]["denomination"] == "1080p"
    assert par_nom["dénomination portrait"]["denomination"] == "1080p"
    assert par_nom["cohérent"]["denomination"] is None

    # 7. Le registre d'écrans est vide, et aucun appareil n'est rapproché.
    assert v["constantes"]["ecrans_connus"] == {}
    for nom, x in par_nom.items():
        assert x["ecran_rapproche"] is None, nom

    # 8. Aucune dénomination ne nomme un appareil : les mélanger ferait passer
    #    « 1080p » pour une identification de matériel.
    for n in v["constantes"]["definitions_nommees"].values():
        for interdit in ("iPhone", "Galaxy", "Pixel", "MacBook", "Retina"):
            assert interdit not in n, n

    print("  8 contrôles passés avant écriture.")


if __name__ == "__main__":
    sys.exit(main())
