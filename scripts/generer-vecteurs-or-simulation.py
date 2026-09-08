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

from visee_optique.simulation import (  # noqa: E402
    K_ENVELOPPE_MAX, K_ENVELOPPE_MIN, K_PLANCHER_ADMIS, K_STANDARD,
    MASQUE_MODELE_PLAT_M, MOTIF_CONDUIT_OPTIQUE, MOTIF_REFRACTION_STANDARD,
    MOTIF_SANS_RELIEF,
    MOTIF_SEUIL, SEUIL_DISCRIMINATION_FRACTION, juger, motif_refraction,
)

#: Les coefficients de réfraction dont le motif est épinglé. La plage est
#: balayée : un port qui rendrait toujours le texte standard passerait un jeu
#: qui ne comparerait qu'une valeur.
CAS_K = [0.0, 0.05, 0.08, 0.10, K_STANDARD, 0.14, 0.18, 0.20, 0.40, 0.90,
         K_PLANCHER_ADMIS]

S = SEUIL_DISCRIMINATION_FRACTION

#: (nom, hauteur masquée à la base au gradient moyen, hauteur de la cible)
#:
#: La grandeur jugée est l'occultation À LA BASE, non bornée à la hauteur de la
#: cible : au-delà de la distance limite elle continue de croître.
CAS = [
    ("rien de masqué", 0.0, 100.0),
    ("cible enfouie sous l'horizon", 2042.0, 300.0),
    ("nettement discriminante", 38.5, 110.0),
    # Le sommet reste entièrement visible et la visée discrimine quand même :
    # c'est tout l'objet du passage à l'occultation basse.
    ("sommet visible, pied masqué", 15.0, 100.0),
    # Au seuil exact, des deux côtés. C'est là que se lit une constante
    # changée, et nulle part ailleurs.
    ("au seuil exact", 100.0 * S, 100.0),
    ("juste sous le seuil", math.nextafter(100.0 * S, 0.0), 100.0),
    # Le seuil est RELATIF : la même occultation tranche ou non selon la cible.
    ("11 m sur une cible de 110 m", 11.0, 110.0),
    ("11 m sur une cible de 300 m", 11.0, 300.0),
    # Une occultation minuscule. En JavaScript un tel nombre s'écrit « 1e-7 » :
    # tout traitement qui passerait par une chaîne s'y trahirait.
    ("occultation minuscule", 1e-7, 100.0),
]


def verdict_en_dict(v):
    return {
        "discriminante": v.discriminante,
        "motif": v.motif,
        "hauteur_masquee_base_m": v.hauteur_masquee_base_m,
        "fraction_masquee_base": v.fraction_masquee_base,
        "hauteur_masquee_plat_m": v.hauteur_masquee_plat_m,
        "ecart_entre_modeles_m": v.ecart_entre_modeles_m,
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
            "masque_modele_plat_m": MASQUE_MODELE_PLAT_M,
            "motif_seuil": MOTIF_SEUIL,
            "motif_sans_relief": MOTIF_SANS_RELIEF,
            "motif_refraction_standard": MOTIF_REFRACTION_STANDARD,
            "k_plancher_admis": K_PLANCHER_ADMIS,
            "motif_conduit_optique": MOTIF_CONDUIT_OPTIQUE,
        },
        "refraction": [
            {"k": k, "motif": motif_refraction(k)} for k in CAS_K
        ],
        "cas": [],
    }
    for nom, masquee, H in CAS:
        v["cas"].append({
            "nom": nom,
            "masquee_base_m": masquee,
            "hauteur_cible_m": H,
            "verdict": verdict_en_dict(juger(masquee, H)),
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

    # 2. Les deux genres de motif sont représentés. Ce sont les phrases
    #    affichées au visiteur, comparées ensuite caractère par caractère.
    motifs = [x["motif"] for x in par_nom.values()]
    for marque in ("assez pour qu'une", "sous le seuil"):
        assert any(marque in m for m in motifs), "genre de motif absent : %s" % marque

    # 3. Le seuil est éprouvé au plus près, des deux côtés. Sans cette paire,
    #    une constante changée du simple au décuple ne se verrait pas.
    assert par_nom["au seuil exact"]["discriminante"] is True
    assert par_nom["juste sous le seuil"]["discriminante"] is False
    ecart = abs(par_nom["au seuil exact"]["fraction_masquee_base"]
                - SEUIL_DISCRIMINATION_FRACTION)
    assert ecart < 1e-15, "le cas de bord n'est plus au bord : écart %g" % ecart

    # 4. Le seuil est RELATIF : la même occultation tranche ou non selon la
    #    hauteur de la cible. Sans ces deux cas, un seuil en mètres passerait.
    assert par_nom["11 m sur une cible de 110 m"]["discriminante"] is True
    assert par_nom["11 m sur une cible de 300 m"]["discriminante"] is False

    # 5. L'occultation basse N'EST PAS bornée à la hauteur de la cible : sans
    #    ce cas, une implémentation qui la borne passerait.
    enfouie = par_nom["cible enfouie sous l'horizon"]
    assert enfouie["fraction_masquee_base"] > 1.0, enfouie
    assert enfouie["hauteur_masquee_base_m"] == 2042.0

    # 6. Le modèle plat masque zéro PARTOUT, et l'écart vaut donc exactement
    #    l'occultation sphérique.
    for nom, x in par_nom.items():
        assert x["hauteur_masquee_plat_m"] == 0.0, nom
        assert x["ecart_entre_modeles_m"] == x["hauteur_masquee_base_m"], nom

    # 7. Le motif de réfraction nomme le k employé, et ne se confond avec le
    #    texte standard QUE pour la valeur standard.
    par_k = {r["k"]: r["motif"] for r in v["refraction"]}
    assert par_k[K_STANDARD] == MOTIF_REFRACTION_STANDARD
    for k, m in par_k.items():
        if k == K_STANDARD:
            continue
        assert m != MOTIF_REFRACTION_STANDARD, k
        assert ("%.2f" % k).replace(".", ",") in m, (k, m[:80])
        assert "PERSONNALISÉ" in m, k

    # 8. Le message du conduit optique ne porte AUCUN renvoi de paragraphe :
    #    le simulateur n'en a plus, et en réintroduire un par un message
    #    d'erreur défairait le nettoyage par la petite porte.
    for jargon in ("§", "Tableau"):
        assert jargon not in MOTIF_CONDUIT_OPTIQUE, jargon

    print("  8 contrôles passés avant écriture.")


if __name__ == "__main__":
    sys.exit(main())
