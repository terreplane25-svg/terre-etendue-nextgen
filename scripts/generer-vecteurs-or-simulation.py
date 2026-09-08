#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vecteurs d'or de la règle de lecture du simulateur de visée.

Le simulateur tourne dans le navigateur, donc en TypeScript, mais la référence
reste le paquet Python. Les cas sont fabriqués par les mêmes fonctions que
`tests/test_simulation.py`, pas réécrites ici.

CE QUE CES VECTEURS ÉPINGLENT
─────────────────────────────
Le seuil à sa valeur nommée, la lecture de l'enveloppe par son bord le plus
DÉFAVORABLE, la primauté du relief sur la courbure, et les phrases affichées
au visiteur — caractère par caractère, apostrophes comprises. Une divergence
d'apostrophe entre les deux implémentations s'est produite trois fois dans ce
dépôt ; ici elle serait invisible à l'œil et changerait le texte affiché.

CONTRÔLE AVANT ÉCRITURE
───────────────────────
Le script revérifie que ses cas DISCRIMINENT : que les deux verdicts existent,
que les trois motifs distincts sont représentés, et qu'un cas au moins tient à
un cheveu du seuil. Sans cela, une constante changée passerait inaperçue.

    python3 scripts/generer-vecteurs-or-simulation.py
"""
import json
import math
import os
import sys
from datetime import datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
PAQUET_A = os.path.join(RACINE, "outils", "outil-A-visee-optique")
CIBLE = os.path.join(RACINE, "src", "lib", "visee-optique", "vecteurs-or-simulation.json")

sys.path.insert(0, PAQUET_A)
try:
    import visee_optique  # noqa: F401
except ImportError:
    if not os.path.exists(VENV):
        sys.exit("venv des outils absent : %s (voir outils/README.md)" % VENV)
    os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

from tests.test_simulation import analyse  # noqa: E402
from visee_optique.simulation import (  # noqa: E402
    K_ENVELOPPE_MAX, K_ENVELOPPE_MIN, K_STANDARD, MOTIF_REFRACTION, MOTIF_SEUIL,
    SEUIL_DISCRIMINATION_FRACTION, juger,
)

S = SEUIL_DISCRIMINATION_FRACTION

#: (nom, fraction visible à la borne 1, à la borne 2, obstacle, relief évalué, H)
CAS = [
    ("entièrement visible aux deux bornes", 1.0, 1.0, False, True, 100.0),
    ("entièrement sous l'horizon", 0.0, 0.0, False, True, 100.0),
    ("nettement discriminante", 1.0 - 0.35, 1.0 - 0.62, False, True, 110.0),
    # À un flottant près du seuil, des deux côtés. C'est là que se lit une
    # constante changée, et nulle part ailleurs.
    ("au plus près du seuil, au-dessus", 1.0 - S, 1.0 - 0.30, False, True, 100.0),
    ("au plus près du seuil, en dessous",
     math.nextafter(1.0 - S, 1.0), 1.0 - 0.30, False, True, 100.0),
    # Une borne discriminante, l'autre non : le verdict doit suivre la mauvaise.
    ("une seule borne discriminante", 1.0 - 0.50, 1.0 - 0.001, False, True, 100.0),
    ("bornes dans l'ordre inverse", 1.0 - 0.001, 1.0 - 0.50, False, True, 100.0),
    # Une occultation minuscule à une borne, franche à l'autre. En JavaScript
    # un tel nombre s'écrit « 1e-7 » : un tri par défaut, qui compare des
    # chaînes, le classerait APRÈS « 0.5 » et inverserait les deux bornes. Sans
    # ce cas, ce défaut passait le vérificateur.
    ("occultation minuscule à une borne", 1.0 - 1e-7, 1.0 - 0.50, False, True, 100.0),
    # Le relief prime, même sur une occultation de courbure totale.
    ("relief masquant", 0.0, 0.0, True, True, 100.0),
    ("relief non évalué", 1.0 - 0.50, 1.0 - 0.40, False, False, 100.0),
    ("grande cible", 1.0 - 0.20, 1.0 - 0.50, False, True, 250.0),
]


def verdict_en_dict(v):
    return {
        "discriminante": v.discriminante,
        "motif": v.motif,
        "fraction_cachee_min": v.fraction_cachee_min,
        "fraction_cachee_max": v.fraction_cachee_max,
        "hauteur_cachee_min_m": v.hauteur_cachee_min_m,
        "hauteur_cachee_max_m": v.hauteur_cachee_max_m,
        "masque_par_le_relief": v.masque_par_le_relief,
        "seuil_applique": v.seuil_applique,
    }


def main():
    v = {
        "genere_le": datetime.now(timezone.utc).isoformat(),
        "source": "visee_optique.simulation (paquet Python)",
        "avertissement": (
            "Fichier généré. Ne pas modifier à la main : il est la référence "
            "contre laquelle le port TypeScript est vérifié."
        ),
        "constantes": {
            "seuil_discrimination_fraction": SEUIL_DISCRIMINATION_FRACTION,
            "k_standard": K_STANDARD,
            "k_enveloppe_min": K_ENVELOPPE_MIN,
            "k_enveloppe_max": K_ENVELOPPE_MAX,
            "motif_seuil": MOTIF_SEUIL,
            "motif_refraction": MOTIF_REFRACTION,
        },
        "cas": [],
    }
    for nom, f1, f2, obstacle, evalue, H in CAS:
        a = analyse(f1, obstacle=obstacle, relief_evalue=evalue)
        b = analyse(f2, obstacle=obstacle, relief_evalue=evalue)
        v["cas"].append({
            "nom": nom,
            "fraction_visible_borne_1": f1,
            "fraction_visible_borne_2": f2,
            "obstacle": obstacle,
            "relief_evalue": evalue,
            "hauteur_cible_m": H,
            "verdict": verdict_en_dict(juger(a, b, H)),
        })

    controle(v)
    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Écrit : %s" % os.path.relpath(CIBLE, RACINE))
    print("  %d configurations" % len(v["cas"]))
    return 0


def controle(v):
    par_nom = {c["nom"]: c["verdict"] for c in v["cas"]}

    # 1. Les deux verdicts existent. Un jeu qui n'en porterait qu'un laisserait
    #    passer une règle câblée en dur.
    verdicts = {x["discriminante"] for x in par_nom.values()}
    assert verdicts == {True, False}, verdicts

    # 2. Les trois motifs distincts sont représentés — relief, écart trop
    #    petit, écart suffisant. Ce sont trois phrases affichées au visiteur.
    motifs = {x["motif"] for x in par_nom.values()}
    assert len(motifs) == 3, "il manque un motif : %d distincts" % len(motifs)

    # 3. Le seuil est éprouvé au plus près, des deux côtés. Sans cette paire,
    #    une constante changée du simple au double ne se verrait pas.
    assert par_nom["au plus près du seuil, au-dessus"]["discriminante"] is True
    assert par_nom["au plus près du seuil, en dessous"]["discriminante"] is False
    ecart = abs(par_nom["au plus près du seuil, au-dessus"]["fraction_cachee_min"]
                - SEUIL_DISCRIMINATION_FRACTION)
    assert ecart < 1e-15, "le cas de bord n'est plus au bord : écart %g" % ecart

    # 4. L'ordre des bornes ne change rien : les deux cas doivent coïncider.
    assert (par_nom["une seule borne discriminante"]
            == par_nom["bornes dans l'ordre inverse"]), \
        "l'ordre des bornes change le verdict : le tri ne fait plus son office"

    # 5. Le cas minuscule est bien classé en premier : c'est ce qui distingue
    #    un tri numérique d'un tri de chaînes.
    petit = par_nom["occultation minuscule à une borne"]
    assert petit["fraction_cachee_min"] < 1e-6 < petit["fraction_cachee_max"], petit
    assert petit["discriminante"] is False

    # 6. Le relief non évalué ne vaut PAS relief absent.
    assert par_nom["relief non évalué"]["masque_par_le_relief"] is None
    assert par_nom["relief masquant"]["masque_par_le_relief"] is True
    assert par_nom["nettement discriminante"]["masque_par_le_relief"] is False

    print("  6 contrôles passés avant écriture.")


if __name__ == "__main__":
    sys.exit(main())
