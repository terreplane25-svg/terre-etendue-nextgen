#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vecteurs d'or des conteneurs hors EXIF — PNG, WebP, GIF, BMP, SVG, ICC.

Le vérificateur du site tourne dans le navigateur, donc en TypeScript, mais la
référence reste le paquet Python. Les fichiers sont construits par les mêmes
fonctions que `tests/test_conteneurs.py`, pas réécrites ici.

CONTRÔLE AVANT ÉCRITURE
───────────────────────
Le script revérifie que ses cas discriminent : qu'un CRC faux est présent ET
un CRC sain, qu'un texte compressé est réellement absent du fichier brut,
qu'une hauteur BMP négative existe, et qu'une dimension SVG non pixel reste
nulle. Sans ces contrôles, une fixture retouchée rendrait des vecteurs qui
passent des deux côtés sans rien épingler.

    python3 scripts/generer-vecteurs-or-conteneurs.py
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
CIBLE = os.path.join(RACINE, "src", "lib", "preuve-image", "vecteurs-or-conteneurs.json")

sys.path.insert(0, PAQUET_B)
try:
    import preuve_image  # noqa: F401
except ImportError:
    if not os.path.exists(VENV):
        sys.exit("venv des outils absent : %s (voir outils/README.md)" % VENV)
    os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

import struct  # noqa: E402
from tests.test_conteneurs import (  # noqa: E402
    SVG, bmp, gif, png, profil_icc, profil_icc_tags_aberrants, profil_icc_v4, webp,
)
from preuve_image.conteneurs import ConteneurError, inventorier, lire_profil_icc  # noqa: E402


def bmp_hauteur_negative() -> bytes:
    brut = bytearray(bmp())
    brut[22:26] = struct.pack("<i", -30)
    return bytes(brut)


def png_chunk_qui_deborde() -> bytes:
    brut = bytearray(png(avec_textes=False, avec_icc=False))
    brut[33:37] = struct.pack(">I", 10_000_000)
    return bytes(brut)


def webp_impair() -> bytes:
    """Un morceau de longueur impaire, suivi d'un autre : l'alignement se voit."""
    from tests.test_conteneurs import morceau_riff
    corps = morceau_riff(b"XMP ", b"abc") + morceau_riff(b"VP8 ", b"\x00" * 20)
    return b"RIFF" + struct.pack("<I", 4 + len(corps)) + b"WEBP" + corps


CAS = [
    ("png complet", png()),
    ("png sans textes ni icc", png(avec_textes=False, avec_icc=False)),
    ("png à CRC faux", png(crc_faux=True)),
    ("png animé (APNG)", png(animation=True)),
    ("png à chunk qui déborde", png_chunk_qui_deborde()),
    ("webp complet", webp()),
    ("webp nu", webp(avec_exif=False, avec_xmp=False, avec_icc=False)),
    ("webp animé", webp(animation=True)),
    ("webp à morceau impair", webp_impair()),
    ("gif fixe", gif()),
    ("gif animé", gif(animation=True)),
    ("bmp", bmp()),
    ("bmp à hauteur négative", bmp_hauteur_negative()),
    ("svg", SVG),
    ("svg à largeur en millimètres", SVG.replace(b'width="800"', b'width="210mm"')),
]

CAS_ICC = [
    ("profil v2, tag desc", profil_icc()),
    ("profil v2, autre description", profil_icc(description="sRGB IEC61966-2.1")),
    ("profil de scanner", profil_icc(classe=b"scnr", espace=b"GRAY")),
    # Ces deux cas existent parce que, sans eux, deux ruptures délibérées du
    # port passaient inaperçues : lire un `mluc` v4 en latin-1, et ne pas
    # borner un nombre de tags aberrant.
    ("profil v4, description en UTF-16 (mluc)", profil_icc_v4()),
    ("profil annonçant un nombre de tags aberrant", profil_icc_tags_aberrants()),
]

REFUS = [
    ("format non couvert (JPEG)", b"\xff\xd8\xff\xe0" + b"\x00" * 64),
    ("fichier trop court", b"\x89PNG"),
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def inventaire_en_dict(donnees):
    inv = inventorier(donnees)
    return {
        "format": inv.format, "octets": inv.octets,
        "largeur": inv.largeur, "hauteur": inv.hauteur,
        "profondeur_bits": inv.profondeur_bits,
        "dpi_x": inv.dpi_x, "dpi_y": inv.dpi_y,
        "chunks": [
            {"type": c.type, "offset": c.offset, "longueur": c.longueur,
             "crc_valide": c.crc_valide, "role": c.role}
            for c in inv.chunks
        ],
        "textes": [
            {"origine": t.origine, "cle": t.cle, "valeur": t.valeur,
             "compresse": t.compresse, "langue": t.langue}
            for t in inv.textes
        ],
        "profil_icc": None if inv.profil_icc is None else profil_en_dict(inv.profil_icc),
        # Les octets ne passent pas en JSON : c'est l'empreinte qui atteste que
        # les deux implémentations ont extrait exactement les mêmes.
        "bloc_exif_sha256": None if inv.bloc_exif is None else sha(inv.bloc_exif),
        "bloc_exif_octets": None if inv.bloc_exif is None else len(inv.bloc_exif),
        "paquets_xmp": [sha(x) for x in inv.paquets_xmp],
        "proprietes": {k: (list(v) if isinstance(v, tuple) else v)
                       for k, v in inv.proprietes.items()},
        "chunks_corrompus": list(inv.chunks_corrompus),
    }


def profil_en_dict(p):
    return {
        "octets": p.octets, "version": p.version,
        "classe": p.classe, "classe_libelle": p.classe_libelle,
        "espace": p.espace, "espace_libelle": p.espace_libelle,
        "espace_connexion": p.espace_connexion,
        "plateforme": p.plateforme, "createur": p.createur,
        "date": p.date, "description": p.description, "copyright": p.copyright_,
    }


def main():
    v = {
        "genere_le": datetime.now(timezone.utc).isoformat(),
        "source": "preuve_image.conteneurs (paquet Python)",
        "avertissement": (
            "Fichier généré. Ne pas modifier à la main : il est la référence "
            "contre laquelle le port TypeScript est vérifié."
        ),
        "cas": [], "icc": [], "refus": [],
    }

    for nom, donnees in CAS:
        v["cas"].append({
            "nom": nom,
            "octets_b64": base64.b64encode(donnees).decode("ascii"),
            "inventaire": inventaire_en_dict(donnees),
        })
    for nom, donnees in CAS_ICC:
        v["icc"].append({
            "nom": nom,
            "octets_b64": base64.b64encode(donnees).decode("ascii"),
            "profil": profil_en_dict(lire_profil_icc(donnees)),
        })
    for nom, donnees in REFUS:
        try:
            inventorier(donnees)
            sys.exit("le cas de refus « %s » n'a pas levé côté Python" % nom)
        except ConteneurError as exc:
            v["refus"].append({
                "nom": nom,
                "octets_b64": base64.b64encode(donnees).decode("ascii"),
                "message_python": str(exc),
            })

    controle(v)
    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Écrit : %s" % os.path.relpath(CIBLE, RACINE))
    print("  %d conteneurs, %d profils ICC, %d refus"
          % (len(v["cas"]), len(v["icc"]), len(v["refus"])))
    return 0


def controle(v):
    par_nom = {c["nom"]: c["inventaire"] for c in v["cas"]}

    # 1. Un CRC faux ET un CRC sain, sinon l'asymétrie ne se voit pas.
    assert par_nom["png à CRC faux"]["chunks_corrompus"], "aucun chunk corrompu détecté"
    assert par_nom["png complet"]["chunks_corrompus"] == []

    # 2. Le texte compressé est RÉELLEMENT absent du fichier brut : sans cela,
    #    un lecteur qui ne décompresse rien pourrait quand même le trouver.
    brut = base64.b64decode(
        next(c for c in v["cas"] if c["nom"] == "png complet")["octets_b64"])
    assert b"invisible" not in brut
    textes = {t["cle"]: t for t in par_nom["png complet"]["textes"]}
    assert "invisible" in textes["Comment"]["valeur"]
    assert textes["Comment"]["compresse"] is True
    assert textes["Software"]["compresse"] is False

    # 3. Le profil ICC est atteint par les deux voies : chunk PNG et morceau WebP.
    assert par_nom["png complet"]["profil_icc"]["description"] == "Display P3"
    assert par_nom["webp complet"]["profil_icc"]["description"] == "Display P3"

    # 4. Le cas à hauteur négative en porte bien une.
    assert par_nom["bmp à hauteur négative"]["proprietes"]["lignes_de_haut_en_bas"] is True
    assert par_nom["bmp"]["proprietes"]["lignes_de_haut_en_bas"] is False
    assert par_nom["bmp à hauteur négative"]["hauteur"] == 30

    # 5. La dimension SVG non pixel reste nulle, et l'attribut brut est gardé.
    mm = par_nom["svg à largeur en millimètres"]
    assert mm["largeur"] is None and mm["proprietes"]["width"] == "210mm"
    assert par_nom["svg"]["largeur"] == 800

    # 6. L'animation se distingue du fixe, dans les trois formats qui en ont.
    assert par_nom["gif animé"]["proprietes"]["trames"] > 1
    assert par_nom["gif fixe"]["proprietes"]["trames"] == 1
    assert par_nom["webp animé"]["proprietes"]["animation"] is True
    assert par_nom["png animé (APNG)"]["proprietes"]["animation"] is True

    # 7. Le morceau WebP impair est suivi d'un autre : sans cela, l'alignement
    #    sur deux octets ne s'observe pas.
    impair = par_nom["webp à morceau impair"]
    assert [c["type"] for c in impair["chunks"]] == ["XMP ", "VP8 "]
    assert impair["chunks"][0]["longueur"] % 2 == 1

    # 8. Le chunk qui déborde arrête le parcours sans emporter le reste.
    assert [c["type"] for c in par_nom["png à chunk qui déborde"]["chunks"]] == ["IHDR"]

    # 9. Les deux cas ICC ajoutés après coup discriminent bien.
    par_icc = {c["nom"]: c["profil"] for c in v["icc"]}
    v4 = par_icc["profil v4, description en UTF-16 (mluc)"]
    assert v4["version"] == "4.3"
    assert v4["description"] == "sRGB IEC61966-2.1", (
        "le profil v4 ne rend pas sa description : le cas ne discrimine plus"
    )
    aberrant = par_icc["profil annonçant un nombre de tags aberrant"]
    assert aberrant["description"] is None

    print("  9 contrôles passés avant écriture.")


if __name__ == "__main__":
    sys.exit(main())
