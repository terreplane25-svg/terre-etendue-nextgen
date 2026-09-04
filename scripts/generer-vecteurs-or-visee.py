#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère les vecteurs d'or qui épinglent le port TypeScript au paquet Python.

Pourquoi ce fichier existe
──────────────────────────
Le calculateur du site tourne dans le navigateur, donc en TypeScript. Le
paquet `visee_optique` reste la référence : c'est lui qui porte les 321 tests.
Deux implémentations de la même formule, c'est exactement le défaut qu'on
passe son temps à corriger — une valeur rectifiée d'un côté et restée vieille
de l'autre.

Ce script transforme ce risque en contrainte vérifiable. Il fait calculer au
Python un jeu de cas couvrant chaque fonction portée, écrit le résultat dans
un fichier de vecteurs, et `scripts/verifier-port-visee.mjs` refait les mêmes
calculs en TypeScript et compare. Si le port dérive, le contrôle échoue.

Ce qui est couvert
──────────────────
  · Vincenty inverse : distance et les deux azimuts ;
  · les trois rayons de courbure de l'ellipsoïde, dont celui d'Euler ;
  · la géométrie du §9 : arc de tangence, distances critiques, hauteur
    occultée, fraction visible, y compris pour une base surélevée ;
  · la réfraction du §11 : k depuis un gradient, rayon effectif, régime ;
  · la condition de discrimination du §28.2, avec son balayage d'enveloppe.

Les cas ne sont pas choisis au hasard : on y trouve les quatre cas d'étude
livrés, les configurations limites du protocole, et des points où la formule
change de branche (D sous la distance critique, cible entièrement occultée).

    python3 scripts/generer-vecteurs-or-visee.py
"""
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
CIBLE = os.path.join(RACINE, "src", "lib", "visee-optique", "vecteurs-or.json")

# Ce module doit tourner sous le venv des outils, où `visee_optique` est
# installé. S'il est lancé avec un autre interpréteur, il se relance.
if "visee_optique" not in sys.modules:
    try:
        import visee_optique  # noqa: F401
    except ImportError:
        if not os.path.exists(VENV):
            sys.exit("venv des outils absent : %s\n"
                     "  python3 -m venv outils/.venv && "
                     "outils/.venv/bin/pip install -e outils/outil-A-visee-optique" % VENV)
        os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

from visee_optique.geodesy import (  # noqa: E402
    GRS80_A, GRS80_E2, GRS80_F,
    rayon_euler, rayon_grande_normale, rayon_meridien, vincenty_inverse,
)
from visee_optique.geometry import (  # noqa: E402
    IUGG_R1, Cible, arc_to_tangent, distance_critique, distance_limite,
    fraction_visible, hauteur_occultee,
)
from visee_optique.models import (  # noqa: E402
    ModeleSpherique, ModeleSurfacePlane, condition_discrimination,
)
from visee_optique.refraction import (  # noqa: E402
    HypotheseRefraction, classer_regime, k_depuis_gradient, rayon_effectif,
)


# Les quatre cas livrés, plus des couples choisis pour leur latitude et leur
# azimut — le rayon d'Euler dépend des deux.
COUPLES = [
    ("sangatte-south-foreland", 50.94642, 1.75305, 51.13152, 1.338825),
    ("chassiron-cordouan", 46.04722, -1.40889, 45.58500, -1.17250),
    ("garoupe-monte-cinto", 43.55389, 7.13222, 42.38028, 8.92250),
    ("equateur-est", 0.0, 0.0, 0.0, 1.5),
    ("meridien-nord", 44.0, 3.0, 46.0, 3.0),
    ("haute-latitude", 70.5, 20.1, 71.2, 22.8),
    ("hemisphere-sud", -33.9, 18.4, -34.4, 19.9),
    ("antimeridien", 40.0, 179.4, 40.5, -179.6),
]

# Géométries : (h_observateur, H_cible, z_base, D). Les deux dernières
# franchissent une branche — sous la distance critique, et au-delà de la
# distance limite.
GEOMETRIES = [
    (2.0, 110.0, 0.0, 35610.7),
    (800.0, 100.0, 0.0, 120000.0),
    (800.0, 100.0, 20.0, 125000.0),
    (100.0, 50.0, 0.0, 57800.0),
    (2000.0, 1500.0, 300.0, 250000.0),
    (12.0, 60.0, 0.0, 42000.0),
    (800.0, 100.0, 0.0, 50000.0),
    (800.0, 100.0, 0.0, 140000.0),
]

GRADIENTS = [
    (1013.25, 288.15, -34.16), (1013.25, 288.15, -13.0),
    (1013.25, 288.15, -6.5), (1013.25, 288.15, 0.0),
    (1013.25, 288.15, 25.0), (1013.25, 288.15, 100.0),
    (1013.25, 288.15, 128.65), (950.0, 275.0, -6.5),
]

K_ESSAIS = [0.0, 0.13, 0.17, 0.25, 0.40, 0.50, 0.80, 0.95]

# Condition §28.2 : (h, H, z_b, D, k_min, k_max, u_f, facteur)
DISCRIMINATIONS = [
    (2.0, 110.0, 0.0, 35610.7, 0.10, 0.40, 0.02, 5.0),
    (800.0, 100.0, 0.0, 120000.0, 0.10, 0.40, 0.02, 5.0),
    (800.0, 100.0, 0.0, 150000.0, 0.10, 0.40, 0.02, 5.0),
    (100.0, 50.0, 0.0, 40000.0, 0.13, 0.25, 0.05, 5.0),
    (12.0, 60.0, 0.0, 42000.0, 0.05, 0.30, 0.03, 3.0),
]


def vecteurs():
    v = {
        "genere_le": datetime.now(timezone.utc).isoformat(),
        "source": "visee_optique (paquet Python, 321 tests)",
        "avertissement": (
            "Fichier généré. Ne pas modifier à la main : il est la référence "
            "contre laquelle le port TypeScript est vérifié."
        ),
        "constantes": {
            "GRS80_A": GRS80_A, "GRS80_F": GRS80_F, "GRS80_E2": GRS80_E2,
            "IUGG_R1": IUGG_R1,
        },
        "vincenty": [], "rayons": [], "geometrie": [],
        "refraction": [], "discrimination": [],
    }

    for nom, la1, lo1, la2, lo2 in COUPLES:
        r = vincenty_inverse(la1, lo1, la2, lo2)
        lat_moy = (la1 + la2) / 2.0
        v["vincenty"].append({
            "nom": nom, "lat1": la1, "lon1": lo1, "lat2": la2, "lon2": lo2,
            "distance_m": r.distance_m,
            "azimut_depart_deg": r.azimut_depart_deg,
            "azimut_arrivee_deg": r.azimut_arrivee_deg,
            "converge": r.converge,
        })
        v["rayons"].append({
            "nom": nom, "latitude_deg": lat_moy,
            "azimut_deg": r.azimut_depart_deg,
            "meridien": rayon_meridien(lat_moy),
            "grande_normale": rayon_grande_normale(lat_moy),
            "euler": rayon_euler(lat_moy, r.azimut_depart_deg),
        })

    for h, H, z_b, D in GEOMETRIES:
        cible = Cible(H=H, z_b=z_b)
        for k in (0.0, 0.13, 0.25):
            R = rayon_effectif(IUGG_R1, k)
            v["geometrie"].append({
                "h": h, "H": H, "z_b": z_b, "D": D, "k": k, "R": R,
                "arc_tangence_h": arc_to_tangent(h, R),
                "distance_critique": distance_critique(h, cible, R),
                "distance_limite": distance_limite(h, cible, R),
                "hauteur_occultee": hauteur_occultee(D, h, cible, R),
                "fraction_visible": fraction_visible(D, h, cible, R),
            })

    for P, T, grad in GRADIENTS:
        k = k_depuis_gradient(P, T, grad)
        v["refraction"].append({
            "P_hPa": P, "T_K": T, "dT_dh_K_par_km": grad, "k": k,
            "regime": classer_regime(k).value,
        })
    for k in K_ESSAIS:
        v["refraction"].append({
            "k_direct": k, "rayon_effectif": rayon_effectif(IUGG_R1, k),
            "regime": classer_regime(k).value,
        })

    for h, H, z_b, D, k_min, k_max, u_f, facteur in DISCRIMINATIONS:
        S = ModeleSpherique(
            R=IUGG_R1, cible=Cible(H=H, z_b=z_b),
            hypothese_k=HypotheseRefraction(
                k_min=k_min, k_max=k_max,
                justification="vecteur d'or", depose_le=datetime.now(timezone.utc)),
        )
        cd = condition_discrimination(
            S, ModeleSurfacePlane(), D, u_f=u_f, facteur=facteur, h=h)
        v["discrimination"].append({
            "h": h, "H": H, "z_b": z_b, "D": D, "k_min": k_min, "k_max": k_max,
            "u_f": u_f, "facteur": facteur,
            "delta": cd.delta, "seuil": cd.seuil, "satisfaite": cd.satisfaite,
            "combinaison_defavorable": dict(cd.combinaison_defavorable),
        })
    return v


def main():
    v = vecteurs()
    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")
    n = sum(len(v[c]) for c in
            ("vincenty", "rayons", "geometrie", "refraction", "discrimination"))
    print("Écrit : %s" % os.path.relpath(CIBLE, RACINE))
    print("  %d vecteurs — %d Vincenty, %d rayons, %d géométrie, %d réfraction, "
          "%d discrimination"
          % (n, len(v["vincenty"]), len(v["rayons"]), len(v["geometrie"]),
             len(v["refraction"]), len(v["discrimination"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
