#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vecteurs d'or du relevé unifié — épinglent le port au paquet `preuve_image`.

La comparaison porte sur le DOCUMENT ENTIER, sérialisé : une clé oubliée,
renommée ou ajoutée d'un seul côté fait tomber le contrôle. C'est plus sévère
qu'une liste de champs choisis, et c'est ce qu'on veut d'un relevé dont la
forme est le contrat.

CONTRÔLE AVANT ÉCRITURE
───────────────────────
Le script revérifie que les cas couvrent chaque règle de déduction, que les
quatre champs définitivement nuls le sont partout avec leur motif, et qu'au
moins un cas porte chacun des blocs optionnels — sans quoi un port qui les
oublierait passerait.

    python3 scripts/generer-vecteurs-or-dossier.py
"""
import base64
import json
import os
import sys
from datetime import datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
PAQUET_B = os.path.join(RACINE, "outils", "outil-B-preuve-image")
CIBLE = os.path.join(RACINE, "src", "lib", "preuve-image", "vecteurs-or-dossier.json")

sys.path.insert(0, PAQUET_B)
# `tests/test_document.py` importe ses fixtures par un chemin plat
# (`from test_provenance import ...`) : le dossier des tests doit donc être
# sur le chemin, en plus du paquet.
sys.path.insert(0, os.path.join(PAQUET_B, "tests"))
try:
    import preuve_image  # noqa: F401
except ImportError:
    if not os.path.exists(VENV):
        sys.exit("venv des outils absent : %s (voir outils/README.md)" % VENV)
    os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

from preuve_image.dossier import (  # noqa: E402
    MOTIF_DECLENCHEMENTS_ABSENT, MOTIF_ECRAN_NON_EVALUE,
    MOTIF_NUMERO_SERIE_ABSENT, constituer_dossier,
)
from tests.test_conteneurs import SVG, bmp, gif, png, webp  # noqa: E402
from tests.test_document import jpeg_avec_c2pa  # noqa: E402
from tests.test_dossier import jpeg_avec_serie, jpeg_telephone  # noqa: E402
from tests.test_isobmff import cr3, heic  # noqa: E402
from tests.test_quantification import jpeg  # noqa: E402
from tests.test_raw import raw_tiff  # noqa: E402
from tests.test_telemetrie import XMP_DJI  # noqa: E402


def jpeg_drone() -> bytes:
    """Un JPEG portant du XMP DJI : la règle « aéronef » doit s'appliquer."""
    import struct as st
    from tests.test_metadata import _envelopper_en_jpeg, campo_ascii, construire_tiff
    base = bytearray(_envelopper_en_jpeg(construire_tiff({0x010F: campo_ascii("DJI")})))
    app1 = b"http://ns.adobe.com/xap/1.0/\x00" + XMP_DJI
    base[2:2] = b"\xff\xe1" + st.pack(">H", len(app1) + 2) + app1
    return bytes(base)


CAS = [
    ("jpeg ordinaire", jpeg(), "photo.jpg"),
    ("jpeg avec numéros de série", jpeg_avec_serie(), "reflex.jpg"),
    ("jpeg de téléphone", jpeg_telephone(), "IMG_0001.jpg"),
    ("jpeg de drone", jpeg_drone(), "DJI_0042.jpg"),
    # Un manifeste C2PA RÉELLEMENT présent. Sans ce cas, « présent » et
    # « vérifié » sont indistinguables, et rien n'empêcherait un port de
    # déclarer vérifié ce qui n'est que déclaré — la confusion même que ce
    # champ existe pour empêcher.
    ("jpeg avec manifeste C2PA", jpeg_avec_c2pa(), "signe.jpg"),
    ("png complet", png(), "capture.png"),
    ("png à CRC faux", png(crc_faux=True), "abime.png"),
    ("webp", webp(), "image.webp"),
    ("gif animé", gif(animation=True), "anim.gif"),
    ("bmp", bmp(), "image.bmp"),
    ("svg", SVG, "schema.svg"),
    ("heic", heic(), "IMG_4092.HEIC"),
    ("cr3", cr3(), "IMG_0001.CR3"),
    ("raw tiff", raw_tiff(), "IMG_0001.CR2"),
    # L'extension ment sur le contenu : l'écart doit être signalé.
    ("png renommé en jpg", png(), "photo.jpg"),
    # Aucun lecteur ne s'applique : l'empreinte et la taille valent quand même.
    ("fichier inconnu", b"ceci n'est pas une image, vraiment pas du tout", "x.bin"),
    ("sans nom de fichier", jpeg(), None),
]


def main():
    v = {
        "genere_le": datetime.now(timezone.utc).isoformat(),
        "source": "preuve_image.dossier (paquet Python)",
        "avertissement": (
            "Fichier généré. Ne pas modifier à la main : il est la référence "
            "contre laquelle le port TypeScript est vérifié."
        ),
        "motif_numero_serie": MOTIF_NUMERO_SERIE_ABSENT,
        "motif_declenchements": MOTIF_DECLENCHEMENTS_ABSENT,
        "motif_ecran": MOTIF_ECRAN_NON_EVALUE,
        "cas": [],
    }
    for nom, donnees, nom_fichier in CAS:
        v["cas"].append({
            "nom": nom,
            "nom_fichier": nom_fichier,
            "octets_b64": base64.b64encode(donnees).decode("ascii"),
            "dossier": constituer_dossier(donnees, nom_fichier).en_dict(),
        })

    controle(v)
    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Écrit : %s" % os.path.relpath(CIBLE, RACINE))
    print("  %d cas" % len(v["cas"]))
    return 0


def controle(v):
    par_nom = {c["nom"]: c["dossier"] for c in v["cas"]}

    # 1. Chaque règle de déduction est exercée par au moins un cas. Sans cela,
    #    une règle supprimée du port passerait inaperçue.
    types = {c["nom"]: c["device_identification"]["hardware_type"] for c in
             [{"nom": k, **{}} | {"device_identification": d["device_identification"]}
              for k, d in par_nom.items()]}
    assert types["jpeg de téléphone"] == "téléphone"
    assert types["jpeg avec numéros de série"] == "appareil à objectifs interchangeables"
    assert types["jpeg de drone"] == "aéronef sans équipage"
    assert types["cr3"] == "appareil photo dédié"
    assert types["png complet"] is None, "un cas sans règle applicable est nécessaire"

    # 2. Les quatre champs définitivement nuls le sont PARTOUT, avec leur motif.
    for nom, d in par_nom.items():
        assert d["capture_settings"]["shutter_count"] is None, nom
        assert d["capture_settings"]["motif_shutter_count"], nom
        assert d["deep_fingerprint"]["screen_resolution_match"] is None, nom
        assert d["deep_fingerprint"]["motif_screen_resolution"], nom
        assert d["deep_fingerprint"]["jpeg_quantization_match"] is None, nom
        assert d["provenance_and_software"]["c2pa_verified"] is False, nom

    # 3. Un manifeste C2PA est RÉELLEMENT présent quelque part, et il n'est
    #    pas pour autant vérifié. Sans ce cas, les deux champs seraient
    #    indistinguables et un port pourrait déclarer vérifié ce qui est déclaré.
    c2pa = par_nom["jpeg avec manifeste C2PA"]["provenance_and_software"]
    assert c2pa["c2pa_credentials"] is True, (
        "le cas C2PA ne porte pas de manifeste : « présent » et « vérifié » "
        "redeviennent indistinguables"
    )
    assert c2pa["c2pa_verified"] is False
    assert any(c["provenance_and_software"]["c2pa_credentials"] is False
               for c in [par_nom[k] for k in par_nom])

    # 4. Chaque bloc optionnel est porté par au moins un cas.
    assert par_nom["jpeg ordinaire"]["deep_fingerprint"]["jpeg_quantization"]
    assert par_nom["png complet"]["deep_fingerprint"]["icc_profile"] == "Display P3"
    assert par_nom["png à CRC faux"]["deep_fingerprint"]["png_crc_corrompus"]
    assert par_nom["jpeg de drone"]["telemetry_and_location"]["drone_telemetry"]
    assert len(par_nom["raw tiff"]["deep_fingerprint"]["apercus_embarques"]) == 3
    assert par_nom["jpeg avec numéros de série"]["device_identification"]["serial_number"]

    # 5. L'écart extension/octets est signalé, et seulement là où il existe.
    assert par_nom["png renommé en jpg"]["avertissements"], "l'écart n'est pas signalé"
    assert par_nom["png complet"]["avertissements"] == []
    assert par_nom["sans nom de fichier"]["avertissements"] == []

    # 6. Un fichier qu'aucun lecteur ne comprend garde son empreinte.
    inconnu = par_nom["fichier inconnu"]
    assert len(inconnu["file_analysis"]["sha256"]) == 64
    assert inconnu["file_analysis"]["mime_type"] is None
    assert inconnu["lectures_en_echec"]

    # 7. Le type MIME vient des octets : le cas renommé le prouve.
    assert par_nom["png renommé en jpg"]["file_analysis"]["mime_type"] == "image/png"
    assert par_nom["png renommé en jpg"]["file_analysis"]["extension_declaree"] == ".jpg"

    print("  7 contrôles passés avant écriture.")


if __name__ == "__main__":
    sys.exit(main())
