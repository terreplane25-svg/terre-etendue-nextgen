#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vecteurs d'or du vérificateur d'intégrité — épinglent le port au paquet `preuve_image`.

Même principe que pour l'outil A : le vérificateur du site tourne dans le
navigateur, donc en TypeScript, mais la référence reste le paquet Python et
ses 137 tests. Ce script fabrique des JPEG déterministes, les fait lire au
Python, et écrit octets et résultat attendu dans un fichier de vecteurs que
`scripts/verifier-port-preuve.mjs` rejoue en TypeScript.

Les JPEG sont construits par les mêmes fonctions que les tests du paquet
(`tests/test_metadata.py`), pas réécrites ici : un fixture qui divergerait de
ce que les tests éprouvent ne vérifierait rien.

Ce qui est couvert
──────────────────
  · SHA-256, y compris sur l'entrée vide — le cas où une implémentation
    naïve renvoie une chaîne vide plutôt que le condensat de zéro octet ;
  · lecture EXIF en petit-boutien et en grand-boutien ;
  · GPS nord-est, GPS sud-ouest avec altitude négative, GPS sans
    incertitude annoncée, absence totale de GPS ;
  · tous les types TIFF que le décodeur gère : ASCII, SHORT, LONG,
    RATIONAL, BYTE ;
  · les refus : JPEG sans segment EXIF, en-tête TIFF invalide, nombre
    magique faux, flux tronqué ;
  · le classement des opérations admises et exclues du §17.2.

    python3 scripts/generer-vecteurs-or-preuve.py
"""
import base64
import dataclasses
import hashlib
import json
import os
import struct
import sys
from datetime import datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
PAQUET_B = os.path.join(RACINE, "outils", "outil-B-preuve-image")
CIBLE = os.path.join(RACINE, "src", "lib", "preuve-image", "vecteurs-or.json")

try:
    import preuve_image  # noqa: F401
except ImportError:
    if not os.path.exists(VENV):
        sys.exit("venv des outils absent : %s (voir outils/README.md)" % VENV)
    os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

# Les constructeurs de fixtures vivent dans la suite de tests du paquet : on
# les réutilise plutôt que d'en écrire une seconde version.
sys.path.insert(0, PAQUET_B)
from tests.test_metadata import (  # noqa: E402
    _envelopper_en_jpeg, campo_ascii, campo_byte, campo_long, campo_rational,
    campo_short, construire_tiff,
)
from preuve_image.integrity import (  # noqa: E402
    OPERATIONS_ADMISES, OPERATIONS_EXCLUES, classer_operation,
)
from preuve_image.metadata import (  # noqa: E402
    INDISPONIBLE, MetadataError, lire_exif_depuis_jpeg,
)
from preuve_image.metadata import (  # noqa: E402
    _TAG_DATETIME_ORIGINAL, _TAG_EXPOSURE_TIME, _TAG_FNUMBER,
    _TAG_FOCAL_LENGTH, _TAG_FOCAL_LENGTH_35MM, _TAG_GPS_ALT, _TAG_GPS_ALT_REF,
    _TAG_GPS_H_POSITIONING_ERROR, _TAG_GPS_LAT, _TAG_GPS_LAT_REF, _TAG_GPS_LON,
    _TAG_GPS_LON_REF, _TAG_ISO_SPEED, _TAG_LENS_MODEL, _TAG_MAKE, _TAG_MODEL,
    _TAG_ORIENTATION, _TAG_PIXEL_X_DIMENSION, _TAG_PIXEL_Y_DIMENSION,
)


def jpeg_complet():
    """Boîtier, objectif, tous les réglages, GPS nord-est avec incertitude."""
    return _envelopper_en_jpeg(construire_tiff(
        {_TAG_MAKE: campo_ascii("Canon"), _TAG_MODEL: campo_ascii("EOS R5"),
         _TAG_ORIENTATION: campo_short(1)},
        {_TAG_FOCAL_LENGTH: campo_rational((2400, 100)),
         _TAG_FOCAL_LENGTH_35MM: campo_short(24),
         _TAG_FNUMBER: campo_rational((280, 100)),
         _TAG_EXPOSURE_TIME: campo_rational((1, 500)),
         _TAG_ISO_SPEED: campo_short(200),
         _TAG_PIXEL_X_DIMENSION: campo_long(6000),
         _TAG_PIXEL_Y_DIMENSION: campo_long(4000),
         _TAG_DATETIME_ORIGINAL: campo_ascii("2026:09:03 10:15:00"),
         _TAG_LENS_MODEL: campo_ascii("RF24-105mm F4 L IS USM")},
        {_TAG_GPS_LAT_REF: campo_ascii("N"),
         _TAG_GPS_LAT: campo_rational((48, 1), (51, 1), (30, 1)),
         _TAG_GPS_LON_REF: campo_ascii("E"),
         _TAG_GPS_LON: campo_rational((2, 1), (21, 1), (3, 1)),
         _TAG_GPS_ALT_REF: campo_byte(0),
         _TAG_GPS_ALT: campo_rational((35, 1)),
         _TAG_GPS_H_POSITIONING_ERROR: campo_rational((5, 1))}))


def jpeg_sud_ouest():
    """Hémisphère sud, longitude ouest, altitude sous le niveau de référence."""
    return _envelopper_en_jpeg(construire_tiff(
        {_TAG_MAKE: campo_ascii("Nikon")},
        {_TAG_FOCAL_LENGTH: campo_rational((500, 10))},
        {_TAG_GPS_LAT_REF: campo_ascii("S"),
         _TAG_GPS_LAT: campo_rational((33, 1), (52, 1), (12, 1)),
         _TAG_GPS_LON_REF: campo_ascii("W"),
         _TAG_GPS_LON: campo_rational((70, 1), (39, 1), (0, 1)),
         _TAG_GPS_ALT_REF: campo_byte(1),
         _TAG_GPS_ALT: campo_rational((12, 1))}))


def jpeg_sans_gps():
    """IFD0 seul : ni sous-IFD Exif, ni GPS. Tous les champs doivent rester nuls."""
    return _envelopper_en_jpeg(construire_tiff(
        {_TAG_MAKE: campo_ascii("Sony"), _TAG_MODEL: campo_ascii("A7 IV"),
         _TAG_ORIENTATION: campo_short(6)}))


def jpeg_gps_sans_incertitude():
    """Cas courant : l'appareil écrit la position mais pas GPSHPositioningError."""
    return _envelopper_en_jpeg(construire_tiff(
        {_TAG_MAKE: campo_ascii("Apple"), _TAG_MODEL: campo_ascii("iPhone 15 Pro")},
        {_TAG_FOCAL_LENGTH: campo_rational((677, 100)),
         _TAG_ISO_SPEED: campo_short(64)},
        {_TAG_GPS_LAT_REF: campo_ascii("N"),
         _TAG_GPS_LAT: campo_rational((50, 1), (56, 1), (47, 1)),
         _TAG_GPS_LON_REF: campo_ascii("E"),
         _TAG_GPS_LON: campo_rational((1, 1), (45, 1), (11, 1))}))


def jpeg_big_endian():
    """En-tête « MM ». Le décodeur doit lire les deux boutismes."""
    tiff = bytearray(construire_tiff(
        {_TAG_MAKE: campo_ascii("Leica"), _TAG_ORIENTATION: campo_short(3)}))
    # construire_tiff n'émet que du petit-boutien : on refait le flux en gros-boutien
    # à la main, sur une structure minimale, pour éprouver l'autre branche.
    entrees = [(_TAG_MAKE, 2, 6, b"Leica\x00"), (_TAG_ORIENTATION, 3, 1, None)]
    corps = b"MM" + struct.pack(">H", 42) + struct.pack(">I", 8)
    corps += struct.pack(">H", len(entrees))
    debordement = b""
    offset_deb = 8 + 2 + 12 * len(entrees) + 4
    for tag, type_, count, brut in entrees:
        if brut is not None:
            corps += struct.pack(">HHI", tag, type_, count)
            corps += struct.pack(">I", offset_deb + len(debordement))
            debordement += brut
        else:
            corps += struct.pack(">HHI", tag, type_, count)
            corps += struct.pack(">H", 3) + b"\x00\x00"
    corps += struct.pack(">I", 0) + debordement
    del tiff
    return _envelopper_en_jpeg(corps)


REFUS = [
    ("pas_un_jpeg", b"PNG\x89 ceci n'est pas un JPEG"),
    ("jpeg_sans_exif", b"\xff\xd8" + b"\xff\xe0" + struct.pack(">H", 16)
     + b"JFIF\x00\x01\x02\x00\x00\x01\x00\x01\x00\x00" + b"\xff\xd9"),
    ("entete_tiff_invalide", _envelopper_en_jpeg(b"XX" + struct.pack("<H", 42)
                                                 + struct.pack("<I", 8) + b"\x00" * 8)),
    ("nombre_magique_faux", _envelopper_en_jpeg(b"II" + struct.pack("<H", 43)
                                                + struct.pack("<I", 8) + b"\x00" * 8)),
    ("flux_trop_court", _envelopper_en_jpeg(b"II*\x00")),
]

OCTETS_SHA = [
    ("vide", b""),
    ("abc", b"abc"),
    ("ligne_utf8", "Portion visible d'une cible éloignée".encode("utf-8")),
    ("un_mega", b"\xa5" * (1 << 20)),
    ("tous_les_octets", bytes(range(256))),
]


def exif_en_dict(d):
    brut = dataclasses.asdict(d)
    if brut.get("gps") is not None:
        brut["gps"] = dict(brut["gps"])
    return brut


def main():
    v = {
        "genere_le": datetime.now(timezone.utc).isoformat(),
        "source": "preuve_image (paquet Python, 137 tests)",
        "avertissement": (
            "Fichier généré. Ne pas modifier à la main : il est la référence "
            "contre laquelle le port TypeScript est vérifié."
        ),
        "sentinel_indisponible": INDISPONIBLE,
        "sha256": [], "exif": [], "refus": [], "operations": [],
    }

    for nom, octets in OCTETS_SHA:
        v["sha256"].append({
            "nom": nom,
            "octets_b64": base64.b64encode(octets).decode("ascii"),
            "empreinte": hashlib.sha256(octets).hexdigest(),
            "taille": len(octets),
        })

    for nom, fabrique in (
        ("complet", jpeg_complet), ("sud_ouest", jpeg_sud_ouest),
        ("sans_gps", jpeg_sans_gps),
        ("gps_sans_incertitude", jpeg_gps_sans_incertitude),
        ("big_endian", jpeg_big_endian),
    ):
        octets = fabrique()
        v["exif"].append({
            "nom": nom,
            "jpeg_b64": base64.b64encode(octets).decode("ascii"),
            "empreinte": hashlib.sha256(octets).hexdigest(),
            "attendu": exif_en_dict(lire_exif_depuis_jpeg(octets)),
        })

    for nom, octets in REFUS:
        try:
            lire_exif_depuis_jpeg(octets)
            sys.exit("le cas de refus « %s » n'a pas levé côté Python" % nom)
        except MetadataError as exc:
            v["refus"].append({
                "nom": nom,
                "jpeg_b64": base64.b64encode(octets).decode("ascii"),
                "message_python": str(exc),
            })

    for nom in sorted(OPERATIONS_ADMISES | OPERATIONS_EXCLUES):
        v["operations"].append({"nom": nom, "admise": classer_operation(nom)})
    v["operations_inconnues"] = ["retouche_locale", "", "sur-resolution"]

    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("Écrit : %s" % os.path.relpath(CIBLE, RACINE))
    print("  %d empreintes, %d lectures EXIF, %d refus, %d opérations"
          % (len(v["sha256"]), len(v["exif"]), len(v["refus"]), len(v["operations"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
