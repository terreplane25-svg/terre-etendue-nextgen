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
    K_ENVELOPPE_MAX, K_ENVELOPPE_MIN, K_STANDARD, MOTIF_REFRACTION,
    MOTIF_RESERVE_RELIEF, MOTIF_SEUIL, PAS_COURT_M, PAS_LONG_M, PAS_MOYEN_M,
    SEUIL_DISCRIMINATION_FRACTION, SEUIL_DISTANCE_LONGUE_M,
    SEUIL_DISTANCE_MOYENNE_M, juger, pas_echantillonnage_m,
)

S = SEUIL_DISCRIMINATION_FRACTION

#: (nom, hauteur masquée à la base borne 1, borne 2, obstacle, relief évalué, H)
#:
#: La grandeur jugée est l'occultation À LA BASE, non bornée à la hauteur de la
#: cible : au-delà de la distance limite elle continue de croître.
CAS = [
    ("rien de masqué aux deux bornes", 0.0, 0.0, False, True, 100.0),
    ("cible enfouie sous l'horizon", 2042.0, 2500.0, False, True, 300.0),
    ("nettement discriminante", 38.5, 68.2, False, True, 110.0),
    # Le sommet reste entièrement visible et la visée discrimine quand même :
    # c'est tout l'objet du passage à l'occultation basse.
    ("sommet visible, pied masqué", 15.0, 40.0, False, True, 100.0),
    # Au seuil exact, des deux côtés. C'est là que se lit une constante
    # changée, et nulle part ailleurs.
    ("au seuil exact", 100.0 * S, 30.0, False, True, 100.0),
    ("juste sous le seuil",
     math.nextafter(100.0 * S, 0.0), 30.0, False, True, 100.0),
    # Une borne discriminante, l'autre non : le verdict doit suivre la mauvaise.
    ("une seule borne discriminante", 50.0, 1.0, False, True, 100.0),
    ("bornes dans l'ordre inverse", 1.0, 50.0, False, True, 100.0),
    # Une occultation minuscule à une borne, franche à l'autre. En JavaScript
    # un tel nombre s'écrit « 1e-7 » : un tri par défaut, qui compare des
    # chaînes, le classerait APRÈS « 50 » et inverserait les deux bornes. Sans
    # ce cas, ce défaut passait le vérificateur.
    ("occultation minuscule à une borne", 1e-7, 50.0, False, True, 100.0),
    # Le relief prime, même sur une occultation de courbure totale. La
    # distance de l'obstacle doit apparaître dans le bandeau.
    ("relief bloquant à 500 m", 90.0, 95.0, True, True, 100.0),
    ("relief non évalué", 50.0, 60.0, False, False, 100.0),
    ("grande cible", 20.0, 50.0, False, True, 250.0),
]

#: Le pas d'échantillonnage, par distance. Aucune n'est refusée.
CAS_PAS = [1_000.0, 35_610.0, 99_999.0, 100_000.0, 300_000.0, 499_999.0,
           500_000.0, 2_000_000.0, 20_000_000.0]


def verdict_en_dict(v):
    return {
        "discriminante": v.discriminante,
        "motif": v.motif,
        "hauteur_masquee_base_min_m": v.hauteur_masquee_base_min_m,
        "hauteur_masquee_base_max_m": v.hauteur_masquee_base_max_m,
        "fraction_masquee_base_min": v.fraction_masquee_base_min,
        "fraction_masquee_base_max": v.fraction_masquee_base_max,
        "masque_par_le_relief": v.masque_par_le_relief,
        "distance_obstacle_m": v.distance_obstacle_m,
        "reserve_relief": v.reserve_relief,
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
            "motif_reserve_relief": MOTIF_RESERVE_RELIEF,
            "pas_court_m": PAS_COURT_M,
            "pas_moyen_m": PAS_MOYEN_M,
            "pas_long_m": PAS_LONG_M,
            "seuil_distance_moyenne_m": SEUIL_DISTANCE_MOYENNE_M,
            "seuil_distance_longue_m": SEUIL_DISTANCE_LONGUE_M,
        },
        "cas": [],
        "pas_echantillonnage": [
            {"distance_m": d, "pas_m": pas_echantillonnage_m(d)} for d in CAS_PAS
        ],
    }
    for nom, f1, f2, obstacle, evalue, H in CAS:
        a = analyse(f1, obstacle=obstacle, relief_evalue=evalue)
        b = analyse(f2, obstacle=obstacle, relief_evalue=evalue)
        v["cas"].append({
            "nom": nom,
            "masquee_borne_1_m": f1,
            "masquee_borne_2_m": f2,
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
    assert {x["discriminante"] for x in par_nom.values()} == {True, False}

    # 2. Les quatre GENRES de motif sont représentés — relief bloquant, écart
    #    trop petit, écart suffisant avec relief dégagé, écart suffisant sous
    #    réserve. Compter les motifs distincts ne dirait rien : ils portent
    #    des chiffres, donc presque tous diffèrent sans rien couvrir de plus.
    motifs = [x["motif"] for x in par_nom.values()]
    for marque in ("relief local", "sous le seuil",
                   "entièrement dégagée", "présumée, pas établie"):
        assert any(marque in m for m in motifs), "genre de motif absent : %s" % marque

    # 3. Le seuil est éprouvé au plus près, des deux côtés. Sans cette paire,
    #    une constante ramenée de 10 % à 1 % ne se verrait pas.
    assert par_nom["au seuil exact"]["discriminante"] is True
    assert par_nom["juste sous le seuil"]["discriminante"] is False
    ecart = abs(par_nom["au seuil exact"]["fraction_masquee_base_min"]
                - SEUIL_DISCRIMINATION_FRACTION)
    assert ecart < 1e-15, "le cas de bord n'est plus au bord : écart %g" % ecart

    # 4. L'occultation basse N'EST PAS bornée à la hauteur de la cible : sans
    #    ce cas, une implémentation qui la borne passerait.
    enfouie = par_nom["cible enfouie sous l'horizon"]
    assert enfouie["fraction_masquee_base_min"] > 1.0, enfouie
    assert enfouie["hauteur_masquee_base_min_m"] == 2042.0

    # 5. Le pied peut être masqué alors que le sommet reste entièrement
    #    visible. C'est tout l'objet du passage à l'occultation basse.
    assert par_nom["sommet visible, pied masqué"]["discriminante"] is True

    # 6. L'ordre des bornes ne change rien : les deux cas doivent coïncider.
    assert (par_nom["une seule borne discriminante"]
            == par_nom["bornes dans l'ordre inverse"]), \
        "l'ordre des bornes change le verdict : le tri ne fait plus son office"

    # 7. Le cas minuscule est bien classé en premier : c'est ce qui distingue
    #    un tri numérique d'un tri de chaînes.
    petit = par_nom["occultation minuscule à une borne"]
    assert petit["hauteur_masquee_base_min_m"] < 1e-6, petit
    assert petit["discriminante"] is False

    # 8. Le bandeau du relief DIT OÙ ça bloque : « bloquée par le relief » sans
    #    la distance n'apprend rien à personne.
    bloque = par_nom["relief bloquant à 500 m"]
    assert bloque["masque_par_le_relief"] is True
    assert bloque["distance_obstacle_m"] == 500.0
    assert "0,50 km" in bloque["motif"], bloque["motif"]

    # 9. Le relief non évalué ne vaut ni « dégagé » ni « bloqué » : le verdict
    #    porte sur la courbure et la réserve est rendue avec.
    reserve = par_nom["relief non évalué"]
    assert reserve["masque_par_le_relief"] is None
    assert reserve["reserve_relief"] is True
    assert par_nom["nettement discriminante"]["reserve_relief"] is False

    # 10. Le pas s'élargit avec la distance, et les trois paliers sont
    #     représentés — sinon un pas fixe passerait.
    pas = {p["pas_m"] for p in v["pas_echantillonnage"]}
    assert pas == {PAS_COURT_M, PAS_MOYEN_M, PAS_LONG_M}, pas
    for p in v["pas_echantillonnage"]:
        assert p["pas_m"] == pas_echantillonnage_m(p["distance_m"])

    print("  10 contrôles passés avant écriture.")


if __name__ == "__main__":
    sys.exit(main())
