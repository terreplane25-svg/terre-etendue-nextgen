#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vecteurs d'or des notes propriétaires (MakerNote, tag EXIF 0x927C).

Le vérificateur du site tourne dans le navigateur, donc en TypeScript, mais la
référence reste le paquet Python. Les notes sont fabriquées par les mêmes
fonctions que `tests/test_makernotes.py`, pas réécrites ici.

CE QUE CES VECTEURS ÉPINGLENT EN PRIORITÉ
─────────────────────────────────────────
La détermination de la BASE des offsets. C'est le mode de défaillance
silencieuse du format : se tromper d'origine ne lève aucune erreur, on lit des
octets quelconques qui ressemblent à des données. Les cas comprennent donc la
MÊME note fabriquée sous deux bases différentes, une note dont la base réelle
dément la base annoncée par la documentation, et une note illisible sous
toutes les bases.

CONTRÔLE AVANT ÉCRITURE
───────────────────────
Le script revérifie que ses cas DISCRIMINENT : que deux bases distinctes sont
effectivement retenues selon le cas, qu'une non-conformité existe, qu'un
inventaire au moins est vide de sens, et que les deux fabrications de la même
note donnent le même inventaire. Sans ces contrôles, une fixture retouchée
rendrait des vecteurs qui passent des deux côtés sans rien épingler.

    python3 scripts/generer-vecteurs-or-makernotes.py
"""
import base64
import json
import os
import sys
from datetime import datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
PAQUET_B = os.path.join(RACINE, "outils", "outil-B-preuve-image")
CIBLE = os.path.join(RACINE, "src", "lib", "preuve-image", "vecteurs-or-makernotes.json")

sys.path.insert(0, PAQUET_B)
try:
    import preuve_image  # noqa: F401
except ImportError:
    if not os.path.exists(VENV):
        sys.exit("venv des outils absent : %s (voir outils/README.md)" % VENV)
    os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

import struct  # noqa: E402

from tests.test_makernotes import (  # noqa: E402
    ENTREES, ifd, note_apple, note_fujifilm, note_ifd_leurre, note_nikon,
    note_sans_signature,
)
from preuve_image.makernotes import analyser_makernote  # noqa: E402

#: (nom, octets de la note, position depuis l'en-tête TIFF, boutisme du fichier)
CAS = [
    ("apple, base note, gros-boutien imposé", note_apple(), 0, "<"),
    ("sans signature, offsets depuis la note", note_sans_signature(), 0, "<"),
    # Le cas central : la MÊME note, écrite avec des offsets comptés depuis
    # l'en-tête TIFF du fichier. Elle n'est lisible que si sa position est
    # connue, et les deux fabrications doivent donner le même inventaire.
    ("sans signature, offsets depuis le TIFF", note_sans_signature(base=1000), 1000, "<"),
    ("nikon, en-tête TIFF interne", note_nikon(), 0, "<"),
    ("fujifilm, offset écrit en clair", note_fujifilm(), 0, "<"),
    # Le décalage publié pour Fujifilm est 12 : il suffirait pour la note
    # ci-dessus. Ici l'IFD est ailleurs, et seul l'offset ÉCRIT y mène.
    ("fujifilm, ifd hors du décalage publié", note_fujifilm(debut=24), 0, "<"),
    # Un IFD-leurre dont aucune entrée n'est lisible. L'accepter retiendrait
    # une base avec un inventaire vide, sans que rien ne signale que le vrai
    # IFD est ailleurs — un échec plus insidieux qu'une erreur.
    ("ifd-leurre suivi du vrai ifd", note_ifd_leurre(), 0, "<"),
    # Panasonic annonce la base « tiff » ; celle-ci compte depuis la note. Une
    # implémentation qui APPLIQUE la base annoncée au lieu de l'essayer se
    # trahit ici, et `base_conforme` doit valoir faux.
    ("panasonic, base démentie par les octets",
     ifd(ENTREES, "<", 0, 12, b"Panasonic\x00\x00\x00"), 0, "<"),
    ("panasonic, base conforme",
     ifd(ENTREES, "<", 500, 12, b"Panasonic\x00\x00\x00"), 500, "<"),
    ("note gros-boutienne sans boutisme imposé",
     ifd(ENTREES, ">", 0, 8, b"RICOH\x00\x00\x00"), 0, ">"),
    ("note illisible sous toutes les bases", b"\xff" * 64, 0, "<"),
    ("note trop courte pour un IFD", b"\x00\x01", 0, "<"),
    ("note vide", b"", 0, "<"),
]


def analyse_en_dict(note, offset, boutisme):
    a = analyser_makernote(note, offset_dans_le_tiff=offset, boutisme_fichier=boutisme)
    return {
        "present": a.present, "octets": a.octets,
        "constructeur": a.constructeur, "signature_hex": a.signature_hex,
        "empreinte": a.empreinte,
        "base_retenue": a.base_retenue, "base_attendue": a.base_attendue,
        "base_conforme": a.base_conforme, "boutisme": a.boutisme,
        "nombre_de_tags": a.nombre_de_tags,
        "tags": [
            {"identifiant": t.identifiant, "type": t.type_, "type_nom": t.type_nom,
             "cardinalite": t.cardinalite, "octets": t.octets, "en_ligne": t.en_ligne,
             "empreinte": t.empreinte, "forme": t.forme,
             "apercu_texte": t.apercu_texte, "sens": list(t.sens) if t.sens else None}
            for t in a.tags
        ],
        "motif_structure_illisible": a.motif_structure_illisible,
        "motif_aucun_sens": a.motif_aucun_sens,
        "remarque_constructeur": a.remarque_constructeur,
    }


def main():
    v = {
        "genere_le": datetime.now(timezone.utc).isoformat(),
        "source": "preuve_image.makernotes (paquet Python)",
        "avertissement": (
            "Fichier généré. Ne pas modifier à la main : il est la référence "
            "contre laquelle le port TypeScript est vérifié."
        ),
        "cas": [],
    }
    for nom, note, offset, boutisme in CAS:
        v["cas"].append({
            "nom": nom,
            "octets_b64": base64.b64encode(note).decode("ascii"),
            "offset_dans_le_tiff": offset,
            "boutisme_fichier": boutisme,
            "analyse": analyse_en_dict(note, offset, boutisme),
        })

    controle(v)
    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Écrit : %s" % os.path.relpath(CIBLE, RACINE))
    print("  %d notes propriétaires" % len(v["cas"]))
    return 0


def controle(v):
    par_nom = {c["nom"]: c["analyse"] for c in v["cas"]}

    # 1. Les DEUX bases générales sont représentées. Sans les deux, une
    #    implémentation qui n'en essaie qu'une passerait.
    bases = {a["base_retenue"] for a in par_nom.values() if a["base_retenue"]}
    assert {"note", "tiff"} <= bases, "les deux bases générales ne sont pas couvertes : %s" % bases
    assert "tiff_interne" in bases, "l'en-tête TIFF interne de Nikon n'est pas couvert"

    # 2. La même note sous deux bases donne le MÊME inventaire. C'est ce qui
    #    prouve que la base est déterminée par les données, pas devinée.
    a = par_nom["sans signature, offsets depuis la note"]
    b = par_nom["sans signature, offsets depuis le TIFF"]
    assert a["base_retenue"] == "note" and b["base_retenue"] == "tiff"
    assert [t["identifiant"] for t in a["tags"]] == [t["identifiant"] for t in b["tags"]]
    assert [t["empreinte"] for t in a["tags"]] == [t["empreinte"] for t in b["tags"]], \
        "les valeurs lues diffèrent selon la base : la base « tiff » n'atteint pas les mêmes octets"

    # 3. Une non-conformité EXISTE, sinon `base_conforme` peut être câblé à vrai
    #    des deux côtés sans qu'on le voie.
    assert par_nom["panasonic, base démentie par les octets"]["base_conforme"] is False
    assert par_nom["panasonic, base conforme"]["base_conforme"] is True

    # 4. Les deux boutismes sont représentés.
    boutismes = {a["boutisme"] for a in par_nom.values() if a["boutisme"]}
    assert boutismes == {"petit-boutien", "gros-boutien"}, boutismes

    # 5. Aucun sens n'est jamais affirmé — c'est la promesse du module, et elle
    #    doit se lire dans les vecteurs eux-mêmes.
    for nom, a in par_nom.items():
        for t in a["tags"]:
            assert t["sens"] is None, "un sens de tag est affirmé dans « %s »" % nom

    # 6. Un cas au moins reste illisible, et un autre est absent : les deux
    #    sorties dégradées sont épinglées, pas seulement le chemin heureux.
    assert par_nom["note illisible sous toutes les bases"]["motif_structure_illisible"]
    assert par_nom["note illisible sous toutes les bases"]["empreinte"], \
        "l'empreinte doit rester valide même quand la structure ne se lit pas"
    assert par_nom["note vide"]["present"] is False

    # 7. Le leurre n'a PAS été retenu, et l'offset Fujifilm fait autorité.
    assert par_nom["ifd-leurre suivi du vrai ifd"]["nombre_de_tags"] == 5, \
        "le leurre a été retenu : le cas n'épingle plus rien"
    assert par_nom["fujifilm, ifd hors du décalage publié"]["nombre_de_tags"] == 5

    # 8. Les formes reconnues sont représentées, aperçu de texte compris.
    formes = {t["forme"] for a in par_nom.values() for t in a["tags"]}
    assert "liste de propriétés binaire (bplist)" in formes, formes
    assert "texte" in formes, formes
    apercus = [t["apercu_texte"] for a in par_nom.values()
               for t in a["tags"] if t["apercu_texte"]]
    assert any("EssaiCorp" in x for x in apercus), apercus


if __name__ == "__main__":
    sys.exit(main())
