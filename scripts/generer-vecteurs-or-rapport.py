#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vecteurs d'or de la fiche d'observation — épinglent le port au paquet `rapport_expertise`.

Troisième port, même règle : le générateur de fiche du site tourne dans le
navigateur, la référence reste le paquet Python et ses 42 tests.

Ce qui est épinglé ici n'est pas du calcul mais une STRUCTURE, et c'est
justement ce qui se désynchronise sans bruit. Un champ ajouté au §33 côté
Python et oublié côté navigateur donnerait une fiche qui a l'air complète et
qui ne l'est pas. Les vecteurs figent donc :

  · les neuf blocs de la fiche, dans l'ordre, avec le nom exact et l'ordre
    exact de chacun de leurs champs ;
  · le sentinel INDISPONIBLE, qui doit être le même mot dans les trois
    paquets et dans les trois ports ;
  · les chemins pointés que `champs_indisponibles` produit sur trois fiches
    — entièrement remplie, entièrement indisponible, et panachée ;
  · le refus de `declarer` sur une valeur vide ou nulle ;
  · les dix répertoires de l'arborescence du §34, leur ordre et leur
    description ;
  · le nommage du dossier d'archive, et son refus sur un identifiant vide.

    python3 scripts/generer-vecteurs-or-rapport.py
"""
import dataclasses
import json
import os
import sys
from datetime import datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
CIBLE = os.path.join(RACINE, "src", "lib", "rapport-expertise", "vecteurs-or.json")

try:
    import rapport_expertise  # noqa: F401
except ImportError:
    if not os.path.exists(VENV):
        sys.exit("venv des outils absent : %s (voir outils/README.md)" % VENV)
    os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

from rapport_expertise.archive import (  # noqa: E402
    ARBORESCENCE_IMPOSEE, DESCRIPTIONS_REPERTOIRES, ArchiveError,
    nom_dossier_archive,
)
from rapport_expertise.report_builder import (  # noqa: E402
    INDISPONIBLE, Atmosphere, Cible, FicheObservation, Geometrie,
    Identification, Images, Mesures, PosteObservation, RapportError, Resultat,
    SystemePhotographique, champs_indisponibles, declarer,
)

BLOCS = [
    ("identification", Identification),
    ("poste_observation", PosteObservation),
    ("cible", Cible),
    ("geometrie", Geometrie),
    ("systeme_photographique", SystemePhotographique),
    ("atmosphere", Atmosphere),
    ("images", Images),
    ("mesures", Mesures),
    ("resultat", Resultat),
]


def bloc_rempli(classe, prefixe):
    """Un bloc dont chaque champ porte une valeur distincte et reconnaissable."""
    noms = [c.name for c in dataclasses.fields(classe)]
    return classe(**{n: f"{prefixe}::{n}" for n in noms})


def bloc_indisponible(classe):
    noms = [c.name for c in dataclasses.fields(classe)]
    return classe(**{n: INDISPONIBLE for n in noms})


def bloc_panache(classe, indices_indisponibles):
    """Certains champs renseignés, d'autres explicitement indisponibles."""
    noms = [c.name for c in dataclasses.fields(classe)]
    return classe(**{
        n: (INDISPONIBLE if i in indices_indisponibles else f"valeur::{n}")
        for i, n in enumerate(noms)
    })


def fiche(mode):
    if mode == "remplie":
        blocs = {nom: bloc_rempli(cl, nom) for nom, cl in BLOCS}
    elif mode == "indisponible":
        blocs = {nom: bloc_indisponible(cl) for nom, cl in BLOCS}
    else:
        # Panachée : le premier champ de chaque bloc impair est indisponible,
        # les deux premiers du bloc « atmosphere » le sont aussi — la
        # configuration la plus courante en pratique.
        blocs = {}
        for i, (nom, cl) in enumerate(BLOCS):
            if nom == "atmosphere":
                idx = {0, 1, 3}
            elif i % 2 == 1:
                idx = {0}
            else:
                idx = set()
            blocs[nom] = bloc_panache(cl, idx)
    return FicheObservation(**blocs)


def en_dict(f):
    d = {}
    for section in dataclasses.fields(f):
        sous = getattr(f, section.name)
        d[section.name] = {c.name: getattr(sous, c.name) for c in dataclasses.fields(sous)}
    return d


def main():
    v = {
        "genere_le": datetime.now(timezone.utc).isoformat(),
        "source": "rapport_expertise (paquet Python, 42 tests)",
        "avertissement": (
            "Fichier généré. Ne pas modifier à la main : il est la référence "
            "contre laquelle le port TypeScript est vérifié."
        ),
        "sentinel_indisponible": INDISPONIBLE,
        "blocs": [
            {"nom": nom, "champs": [c.name for c in dataclasses.fields(cl)]}
            for nom, cl in BLOCS
        ],
        "fiches": [], "refus_declarer": [], "arborescence": [],
        "nom_dossier": [], "refus_nom_dossier": [],
    }

    for mode in ("remplie", "indisponible", "panachee"):
        f = fiche(mode)
        v["fiches"].append({
            "mode": mode,
            "contenu": en_dict(f),
            "champs_indisponibles": list(champs_indisponibles(f)),
        })

    for valeur in (None, ""):
        try:
            declarer(valeur, "champ_de_test")
            sys.exit("declarer(%r) n'a pas levé côté Python" % valeur)
        except RapportError as exc:
            v["refus_declarer"].append({
                "valeur": "null" if valeur is None else "chaine_vide",
                "message_python": str(exc),
            })

    for nom in ARBORESCENCE_IMPOSEE:
        v["arborescence"].append({"nom": nom, "description": DESCRIPTIONS_REPERTOIRES[nom]})

    for ident in ("CAS-DEMO-SANGATTE-001", "a", "  espaces-autour  "):
        v["nom_dossier"].append({"identifiant": ident, "nom": nom_dossier_archive(ident)})
    for ident in ("", "   ", "\t\n"):
        try:
            nom_dossier_archive(ident)
            sys.exit("nom_dossier_archive(%r) n'a pas levé côté Python" % ident)
        except ArchiveError:
            v["refus_nom_dossier"].append({"identifiant": ident})

    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write("\n")

    total_champs = sum(len(b["champs"]) for b in v["blocs"])
    print("Écrit : %s" % os.path.relpath(CIBLE, RACINE))
    print("  %d blocs, %d champs, %d fiches, %d répertoires"
          % (len(v["blocs"]), total_champs, len(v["fiches"]), len(v["arborescence"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
