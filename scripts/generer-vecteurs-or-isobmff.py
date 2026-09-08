#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vecteurs d'or des conteneurs à boîtes — épinglent le port au paquet `preuve_image`.

Le vérificateur d'intégrité tourne dans le navigateur, donc en TypeScript, mais
la référence reste le paquet Python. Ce script fabrique des HEIC, AVIF et CR3
déterministes, les fait lire au Python, et écrit octets et résultats attendus
dans un fichier que `scripts/verifier-port-isobmff.mjs` rejoue en TypeScript.

Les fichiers sont construits par les mêmes fonctions que les tests du paquet
(`tests/test_isobmff.py`), pas réécrites ici : un fixture qui divergerait de ce
que les tests éprouvent ne vérifierait rien.

CONTRÔLE AVANT ÉCRITURE
───────────────────────
Le script revérifie ses propres cas avant d'écrire. Cinq d'entre eux n'existent
que parce que, sans eux, cinq ruptures délibérées du port passaient inaperçues :
un seul aperçu ne montre pas l'ordre de tri, des largeurs d'`iloc` symétriques
ne montrent pas une interversion de nibbles, un décalage EXIF hors bornes ne
montre pas qu'on le vérifie. Chacun isole UNE dimension, et le contrôle vérifie
qu'il la discrimine encore.

    python3 scripts/generer-vecteurs-or-isobmff.py
"""
import base64
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
PAQUET_B = os.path.join(RACINE, "outils", "outil-B-preuve-image")
CIBLE = os.path.join(RACINE, "src", "lib", "preuve-image", "vecteurs-or-isobmff.json")

sys.path.insert(0, PAQUET_B)
try:
    import preuve_image  # noqa: F401
except ImportError:
    if not os.path.exists(VENV):
        sys.exit("venv des outils absent : %s (voir outils/README.md)" % VENV)
    os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

from tests.test_isobmff import cr3, heic  # noqa: E402
from preuve_image.isobmff import analyser_isobmff  # noqa: E402
from preuve_image.metadata import detecter_conteneur, lire_exif  # noqa: E402

CAS = [
    ("heic complet", heic()),
    ("heic sans auxiliaire ni xmp", heic(avec_auxiliaire=False, avec_xmp=False)),
    ("avif", heic(marque=b"avif")),
    ("heic items non localisables", heic(methode=1)),
    ("cr3", cr3()),
    # Les cinq cas suivants existent parce que, sans eux, cinq ruptures
    # délibérées du port passaient inaperçues. Chacun isole UNE dimension que
    # les autres ne discriminaient pas.
    ("heic à deux aperçus de tailles différentes", heic(second_apercu=True)),
    ("heic à auxiliaire hors répertoire",
     heic(nom_auxiliaire=b"urn:inconnu:2099:aux:quelquechose\x00")),
    # Le décalage doit tomber DANS le fichier, sinon les deux versions du
    # lecteur — celle qui vérifie et celle qui ne vérifie pas — prennent le
    # même repli, et le cas ne discrimine rien. 10 pointe quatre octets après
    # le début réel du bloc TIFF.
    ("heic à décalage EXIF menteur", heic(decalage_exif=10)),
    ("heic à largeurs iloc dissymétriques", heic(largeur_offset=8)),
    ("heic suivi d'une boîte aberrante", heic(boite_aberrante=True)),
    # Les quatre suivants isolent la lecture d'`ispe` et son association par
    # `ipma`. Sans eux, un port qui ignorerait le drapeau d'indices 16 bits,
    # oublierait de masquer le bit `essential`, ou approcherait l'association
    # par « la plus grande `ispe` » rendrait les mêmes dimensions partout.
    ("heic à indices ipma sur seize bits", heic(indices_ipma_16=True)),
    ("heic à bit essential sur toutes les associations", heic(essentiel_partout=True)),
    ("heic aux ispe inversées",
     heic(ispe_principale=(2016, 1512), ispe_auxiliaire=(8064, 6048))),
    ("heic sans ispe", heic(avec_ispe=False)),
    ("heic à ispe de dimension nulle", heic(ispe_principale=(0, 6048))),
    ("heic à propriété imbriquée", heic(propriete_imbriquee=True)),
]


def structure_en_dict(donnees):
    s = analyser_isobmff(donnees)
    return {
        "marque": s.marque,
        "marques_compatibles": list(s.marques_compatibles),
        "est_heif": s.est_heif,
        "est_avif": s.est_avif,
        "est_cr3": s.est_cr3,
        "item_principal": s.item_principal,
        "version_codec": s.version_codec,
        # Les dimensions de l'item principal, lues dans `ispe` via `ipma`.
        "largeur": s.largeur,
        "hauteur": s.hauteur,
        # Les octets ne passent pas en JSON, et les recopier gonflerait le
        # fichier sans rien vérifier de plus : c'est l'EMPREINTE qui atteste
        # que les deux implémentations ont extrait exactement les mêmes octets.
        "bloc_exif_sha256": None if s.bloc_exif is None else hashlib.sha256(s.bloc_exif).hexdigest(),
        "bloc_exif_octets": None if s.bloc_exif is None else len(s.bloc_exif),
        "makernotes_sha256": None if s.makernotes is None else hashlib.sha256(s.makernotes).hexdigest(),
        "paquets_xmp": [hashlib.sha256(x).hexdigest() for x in s.paquets_xmp],
        "boites": [
            {"type": b.type, "debut": b.debut, "taille": b.taille,
             "debut_charge": b.debut_charge, "profondeur": b.profondeur}
            for b in s.boites
        ],
        "items": [
            {"identifiant": i.identifiant, "type": i.type, "nom": i.nom,
             "offset": i.offset, "longueur": i.longueur,
             "type_auxiliaire": i.type_auxiliaire,
             "reference_vers": list(i.reference_vers),
             "largeur": i.largeur, "hauteur": i.hauteur}
            for i in s.items
        ],
        "auxiliaires": [i.identifiant for i in s.auxiliaires],
        "apercus": [
            {"origine": o, "octets": len(b), "sha256": hashlib.sha256(b).hexdigest()}
            for o, b in s.apercus
        ],
    }


def main():
    v = {
        "genere_le": datetime.now(timezone.utc).isoformat(),
        "source": "preuve_image.isobmff (paquet Python)",
        "avertissement": (
            "Fichier généré. Ne pas modifier à la main : il est la référence "
            "contre laquelle le port TypeScript est vérifié."
        ),
        "cas": [],
    }

    for nom, donnees in CAS:
        conteneur = detecter_conteneur(donnees)
        entree = {
            "nom": nom,
            "octets_b64": base64.b64encode(donnees).decode("ascii"),
            "conteneur_detecte": conteneur,
            "empreinte": hashlib.sha256(donnees).hexdigest(),
            "structure": structure_en_dict(donnees),
        }
        # Ce que `lire_exif` en fait, quand il y arrive. C'est le chemin réel :
        # épingler la structure sans épingler la lecture laisserait passer une
        # erreur de câblage entre les deux.
        try:
            e = lire_exif(donnees)
            entree["exif"] = {
                "lu": True,
                "conteneur": e.conteneur,
                "fabricant": e.fabricant,
                "modele": e.modele,
                "sensibilite_iso": e.sensibilite_iso,
                "largeur_px": e.largeur_px,
                "previsualisations": [
                    {"origine": m.origine, "longueur": m.longueur,
                     "sha256": hashlib.sha256(m.octets).hexdigest()}
                    for m in e.previsualisations
                ],
            }
        except Exception as exc:  # noqa: BLE001 — on épingle aussi les refus
            entree["exif"] = {"lu": False, "motif_python": str(exc)}
        v["cas"].append(entree)

    controle(v)

    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Écrit : %s" % os.path.relpath(CIBLE, RACINE))
    print("  %d cas" % len(v["cas"]))
    return 0


def controle(v):
    """Revérifie que les vecteurs épinglent bien ce qu'ils prétendent épingler."""
    par_nom = {c["nom"]: c for c in v["cas"]}

    # 1. Les conteneurs sont NOMMÉS distinctement, pas fondus en « ISO BMFF ».
    assert par_nom["heic complet"]["conteneur_detecte"] == "HEIC"
    assert par_nom["avif"]["conteneur_detecte"] == "AVIF"
    assert par_nom["cr3"]["conteneur_detecte"] == "CR3"

    # 2. L'EXIF est réellement atteint, sur les deux familles.
    for nom, fabricant in (("heic complet", "Apple"), ("cr3", "Canon")):
        e = par_nom[nom]["exif"]
        assert e["lu"] is True, nom
        assert e["fabricant"] == fabricant, nom
        assert e["sensibilite_iso"] is not None, nom

    # 3. L'auxiliaire est nommé, et il n'est pas décodé (il n'a pas d'aperçu).
    s = par_nom["heic complet"]["structure"]
    assert len(s["auxiliaires"]) == 1
    aux = [i for i in s["items"] if i["identifiant"] in s["auxiliaires"]][0]
    assert "HDR" in (aux["type_auxiliaire"] or "")

    # 4. Un item non localisable ne l'est PAS. Sans ce cas, rien ne
    #    distinguerait un lecteur prudent d'un lecteur qui devine.
    ni = par_nom["heic items non localisables"]
    assert ni["structure"]["bloc_exif_sha256"] is None
    assert all(i["offset"] is None for i in ni["structure"]["items"])
    assert ni["exif"]["lu"] is False
    assert "aucun bloc EXIF localisable" in ni["exif"]["motif_python"]

    # 5. Le cas sans auxiliaire ni XMP diffère réellement du cas complet.
    nu = par_nom["heic sans auxiliaire ni xmp"]["structure"]
    assert nu["auxiliaires"] == []
    assert nu["paquets_xmp"] == []
    assert len(s["paquets_xmp"]) == 1

    # 6. Les aperçus sont ordonnés du plus grand au plus petit.
    for c in v["cas"]:
        tailles = [a["octets"] for a in c["structure"]["apercus"]]
        assert tailles == sorted(tailles, reverse=True), c["nom"]

    # 7. Les cinq cas anti-rupture discriminent bien ce pour quoi ils existent.
    #    Un cas qui ne discriminerait plus — parce qu'une fixture a changé —
    #    redeviendrait un vecteur qui passe toujours, sans qu'on le voie.
    deux = par_nom["heic à deux aperçus de tailles différentes"]["structure"]["apercus"]
    assert len(deux) == 2 and deux[0]["octets"] != deux[1]["octets"], (
        "le cas à deux aperçus n'en a pas deux de tailles différentes : l'ordre "
        "de tri redevient inobservable"
    )
    inc = par_nom["heic à auxiliaire hors répertoire"]["structure"]
    assert len(inc["auxiliaires"]) == 1
    assert "non répertorié" in [
        i["type_auxiliaire"] for i in inc["items"]
        if i["identifiant"] in inc["auxiliaires"]
    ][0]
    menteur = par_nom["heic à décalage EXIF menteur"]["structure"]
    sain = par_nom["heic complet"]["structure"]
    # Le décalage doit être DANS les bornes, sinon le cas ne discrimine rien.
    charge_exif = [i for i in menteur["items"] if i["type"] == "Exif"][0]
    assert 4 + 10 <= charge_exif["longueur"] - 8, (
        "le décalage menteur tombe hors du fichier : les deux lecteurs prennent "
        "le même repli, et le cas ne teste plus rien"
    )
    assert menteur["bloc_exif_sha256"] == sain["bloc_exif_sha256"], (
        "le décalage menteur ne redonne pas le bon bloc : le repli ne fonctionne pas"
    )
    dissym = par_nom["heic à largeurs iloc dissymétriques"]["structure"]
    assert dissym["bloc_exif_sha256"] == sain["bloc_exif_sha256"]
    aberrante = par_nom["heic suivi d'une boîte aberrante"]["structure"]
    assert [b["type"] for b in aberrante["boites"] if b["profondeur"] == 0] == \
        [b["type"] for b in sain["boites"] if b["profondeur"] == 0], (
        "la boîte aberrante a été suivie, ou a emporté le reste"
    )

    # 8. Les dimensions viennent de l'association `ipma`, pas d'une heuristique.
    #    L'`ispe` de l'image principale est la DERNIÈRE d'`ipco` et n'est pas
    #    toujours la plus grande : si l'un de ces deux traits disparaissait du
    #    fixture, « la première » ou « la plus grande » redeviendraient justes
    #    et ces vecteurs cesseraient de discriminer sans qu'on le voie.
    assert sain["largeur"] == 8064 and sain["hauteur"] == 6048
    aux_dim = [(i["largeur"], i["hauteur"]) for i in sain["items"]
               if i["identifiant"] == 4][0]
    assert aux_dim == (2016, 1512), (
        "l'auxiliaire n'a plus de dimensions propres : emprunter celles de "
        "l'image principale redeviendrait indétectable"
    )
    inversees = par_nom["heic aux ispe inversées"]["structure"]
    assert (inversees["largeur"], inversees["hauteur"]) == (2016, 1512), (
        "le cas aux ispe inversées ne prend plus « la plus grande » en défaut"
    )
    for nom in ("heic à indices ipma sur seize bits",
                "heic à bit essential sur toutes les associations"):
        s16 = par_nom[nom]["structure"]
        assert (s16["largeur"], s16["hauteur"]) == (8064, 6048), nom
    sans = par_nom["heic sans ispe"]["structure"]
    assert sans["largeur"] is None and sans["hauteur"] is None
    # Sans `ispe`, le reste doit rester lisible : une absence ne fait pas tomber
    # la lecture, elle la borne.
    assert sans["bloc_exif_sha256"] == sain["bloc_exif_sha256"]
    # Une dimension nulle est refusée, et le refus ne contamine pas l'auxiliaire.
    nulle = par_nom["heic à ispe de dimension nulle"]["structure"]
    assert nulle["largeur"] is None and nulle["hauteur"] is None
    assert [i["largeur"] for i in nulle["items"] if i["identifiant"] == 4] == [2016]
    # La propriété imbriquée cache une `ispe` un niveau plus bas : elle ne doit
    # décaler aucun indice, et ses dimensions ne doivent atterrir sur aucun item.
    imbr = par_nom["heic à propriété imbriquée"]["structure"]
    assert any(b["type"] == "ispe" and b["profondeur"] == 4 for b in imbr["boites"]), (
        "le leurre n'est plus imbriqué : le cas ne distingue plus les enfants "
        "directs des descendants"
    )
    assert (imbr["largeur"], imbr["hauteur"]) == (8064, 6048)
    assert all((i["largeur"], i["hauteur"]) != (111, 222) for i in imbr["items"])

    print("  8 contrôles passés avant écriture.")


if __name__ == "__main__":
    sys.exit(main())
