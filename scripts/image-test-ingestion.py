#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fabrique l'image d'essai de l'ingestion : EXIF étendu, IFD1, GPS, C2PA, XMP, IPTC.

Ce que cette image est, et n'est pas
────────────────────────────────────
Un DIAGRAMME CALCULÉ, pas une photographie : aucune scène réelle n'a été
capturée. Elle porte délibérément tout ce que le module d'ingestion sait lire,
pour que l'essai de bout en bout confronte l'interface à un fichier complet
plutôt qu'à quatre fichiers partiels.

Le manifeste C2PA qu'elle contient est SYNTHÉTIQUE : sa structure suit la
spécification, sa « signature » est de quatre octets arbitraires, et rien dans
la chaîne ne prétend la vérifier. Confronter le lecteur à un fichier signé par
une implémentation du marché reste à faire — c'est noté dans outils/README.md.

Le fichier est écrit dans `public/audit/`, ignoré par git : il se reconstruit à
l'identique par ce script.

    python3 scripts/image-test-ingestion.py
"""
import os
import struct
import sys
from io import BytesIO

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
SORTIE = os.path.join(RACINE, "public", "audit", "image-test-ingestion.jpg")

if "preuve_image" not in sys.modules:
    try:
        import preuve_image  # noqa: F401
    except ImportError:
        if not os.path.exists(VENV):
            sys.exit("venv des outils absent : %s" % VENV)
        os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

sys.path.insert(0, os.path.join(RACINE, "outils", "outil-B-preuve-image", "tests"))

from PIL import Image  # noqa: E402
from PIL.TiffImagePlugin import IFDRational  # noqa: E402

from preuve_image.metadata import lire_exif_depuis_jpeg  # noqa: E402
from preuve_image.provenance import analyser_provenance  # noqa: E402
from test_provenance import (  # noqa: E402
    XMP_EXEMPLE, dataset_iim, manifeste_c2pa_synthetique,
)

LARGEUR, HAUTEUR = 800, 600


def base_avec_exif() -> bytes:
    """Un JPEG dont l'EXIF porte tous les champs d'ingestion, plus le GPS."""
    img = Image.new("RGB", (LARGEUR, HAUTEUR), (30, 45, 60))
    d = Image.new("RGB", (LARGEUR, HAUTEUR))  # noqa: F841 — lisibilité du diff
    from PIL import ImageDraw
    t = ImageDraw.Draw(img)
    t.rectangle([0, int(HAUTEUR * 0.62), LARGEUR, HAUTEUR], fill=(10, 22, 36))
    t.text((24, 24), "DIAGRAMME CALCULE — PAS UNE PHOTOGRAPHIE", fill=(168, 184, 204))

    exif = Image.Exif()
    exif[0x010F] = "EssaiCorp"
    exif[0x0110] = "Modele X"
    exif[0x0131] = "Adobe Photoshop 25.0"
    exif[0x0132] = "2026:09:05 11:02:33"
    exif[0x013B] = "A. Photographe"
    exif[0x8298] = "Tous droits reserves"
    exif[0x011A] = IFDRational(300, 1)
    exif[0x011B] = IFDRational(300, 1)
    exif[0x0128] = 2
    s = exif.get_ifd(0x8769)
    s[0x9003] = "2026:09:05 10:14:22"
    s[0x9004] = "2026:09:05 10:14:25"
    s[0x8822] = 2
    s[0x9209] = 0x19
    s[0xA001] = 1
    s[0xA402] = 1
    s[0xA403] = 0
    s[0xA404] = IFDRational(2, 1)
    s[0xA406] = 1
    s[0x8827] = 200
    s[0x829D] = IFDRational(28, 10)
    s[0x829A] = IFDRational(1, 250)
    s[0x920A] = IFDRational(24, 1)
    s[0xA405] = 36
    s[0xA002] = LARGEUR
    s[0xA003] = HAUTEUR
    g = exif.get_ifd(0x8825)
    g[1] = "N"
    g[2] = (IFDRational(50, 1), IFDRational(56, 1), IFDRational(47, 100))
    g[3] = "E"
    g[4] = (IFDRational(1, 1), IFDRational(45, 1), IFDRational(11, 100))
    g[5] = 0
    g[6] = IFDRational(23, 1)
    tampon = BytesIO()
    img.save(tampon, format="JPEG", exif=exif, quality=90)
    return tampon.getvalue()


def injecter_segments(src: bytes) -> bytes:
    """Ajoute XMP (APP1), IPTC (APP13) et C2PA (APP11) juste après le SOI."""
    xmp = b"http://ns.adobe.com/xap/1.0/\x00" + XMP_EXEMPLE.encode()
    seg_xmp = b"\xff\xe1" + struct.pack(">H", len(xmp) + 2) + xmp

    ds = (dataset_iim(80, "A. Photographe")
          + dataset_iim(120, "Vue de la digue au lever du jour")
          + dataset_iim(115, "Agence d'essai")
          + dataset_iim(25, "digue, phare, horizon"))
    res = (b"8BIM" + struct.pack(">H", 0x0404) + b"\x00\x00"
           + struct.pack(">I", len(ds)) + ds + (b"\x00" if len(ds) % 2 else b""))
    iptc = b"Photoshop 3.0\x00" + res
    seg_iptc = b"\xff\xed" + struct.pack(">H", len(iptc) + 2) + iptc

    # Fragments volontairement courts : le recollage doit être éprouvé.
    magasin = manifeste_c2pa_synthetique()
    seg_c2pa = b""
    for numero, i in enumerate(range(0, len(magasin), 200), start=1):
        corps = (b"JP" + struct.pack(">H", 1) + struct.pack(">I", numero)
                 + magasin[i : i + 200])
        seg_c2pa += b"\xff\xeb" + struct.pack(">H", len(corps) + 2) + corps

    return src[:2] + seg_xmp + seg_iptc + seg_c2pa + src[2:]


def ajouter_miniature(src: bytes) -> bytes:
    """Chaîne un IFD1 après l'IFD0 du bloc TIFF, et y range une vraie vignette.

    Pillow n'écrit pas d'IFD1 : sans cette étape, la miniature — que le §16
    demande de confronter à l'image principale — n'existerait pas dans le
    fichier d'essai, et le code qui la lit ne serait jamais exercé de bout en
    bout.
    """
    pos, app1 = 2, None
    while pos + 4 <= len(src):
        if src[pos] != 0xFF:
            break
        m = src[pos + 1]
        if m == 0xD8 or 0xD0 <= m <= 0xD7:
            pos += 2
            continue
        if m in (0xD9, 0xDA):
            break
        ln = struct.unpack_from(">H", src, pos + 2)[0]
        if m == 0xE1 and src[pos + 4 : pos + 10] == b"Exif\x00\x00":
            app1 = (pos, ln)
            break
        pos += 2 + ln
    if app1 is None:
        raise SystemExit("APP1 Exif introuvable : impossible d'ajouter la miniature.")

    debut, longueur = app1
    tiff = bytearray(src[debut + 10 : debut + 2 + longueur])

    img = Image.open(BytesIO(src))
    img.thumbnail((160, 120))
    tampon = BytesIO()
    img.save(tampon, format="JPEG", quality=80)
    vignette = tampon.getvalue()

    endian = "<" if tiff[:2] == b"II" else ">"
    off0 = struct.unpack_from(endian + "I", tiff, 4)[0]
    n0 = struct.unpack_from(endian + "H", tiff, off0)[0]
    ptr_suivant = off0 + 2 + 12 * n0
    if struct.unpack_from(endian + "I", tiff, ptr_suivant)[0] != 0:
        raise SystemExit("Un IFD1 existe déjà : rien à ajouter.")

    off1 = len(tiff)
    taille_ifd1 = 2 + 12 * 3 + 4
    off_vignette = off1 + taille_ifd1
    entrees = [
        (0x0103, 3, 1, struct.pack(endian + "HH", 6, 0)),
        (0x0201, 4, 1, struct.pack(endian + "I", off_vignette)),
        (0x0202, 4, 1, struct.pack(endian + "I", len(vignette))),
    ]
    bloc = struct.pack(endian + "H", len(entrees))
    for tag, typ, cnt, val in entrees:
        bloc += struct.pack(endian + "HHI", tag, typ, cnt) + val.ljust(4, b"\x00")[:4]
    bloc += struct.pack(endian + "I", 0)
    tiff += bloc + vignette
    struct.pack_into(endian + "I", tiff, ptr_suivant, off1)

    corps = b"Exif\x00\x00" + bytes(tiff)
    if len(corps) + 2 > 0xFFFF:
        raise SystemExit("Segment APP1 au-delà de 65 533 octets.")
    return src[:debut] + b"\xff\xe1" + struct.pack(">H", len(corps) + 2) + corps \
        + src[debut + 2 + longueur:]


def main():
    donnees = ajouter_miniature(injecter_segments(base_avec_exif()))
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "wb") as f:
        f.write(donnees)

    # Contrôle : le fichier écrit porte bien tout ce qu'il doit porter.
    e = lire_exif_depuis_jpeg(donnees)
    p = analyser_provenance(donnees)
    assert e.logiciel == "Adobe Photoshop 25.0"
    assert e.miniature is not None and e.miniature.est_jpeg
    assert e.gps is not None
    assert e.dpi_x == 300.0 and e.flash == 0x19
    assert p.c2pa.present and len(p.c2pa.manifestes) == 1
    assert len(p.xmp) == 1 and len(p.iptc) == 4
    assert "Photoshop" in p.marqueurs_logiciels

    print("Écrit : %s — %d octets" % (os.path.relpath(SORTIE, RACINE), len(donnees)))
    print("  EXIF étendu, miniature de %d octets, GPS, C2PA (%d o), XMP, %d champs IPTC"
          % (e.miniature.longueur, p.c2pa.octets, len(p.iptc)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
