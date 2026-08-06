#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit des images de couverture — dimensions réelles contre la règle Discover.

La charte impose, pour l'image de partage social : au moins 1200 px de large,
format paysage voisin de 1,91:1, moins de 1 Mo. En dessous de 1200 px, Google
Discover retire la grande carte et l'article perd sa vignette pleine largeur.

Ce script lit les dimensions dans l'en-tête de chaque fichier — PNG, JPEG,
GIF, WebP, AVIF — sans télécharger l'image entière et sans dépendance externe.
Il n'a besoin que de la bibliothèque standard, pour tourner sur n'importe
quelle machine.

    python3 scripts/auditer-couvertures.py            # tout le corpus
    python3 scripts/auditer-couvertures.py --defauts  # seulement ce qui échoue

À lancer depuis une machine qui atteint green-gnat-134443.hostingersite.com et
images.unsplash.com. Dans l'environnement d'exécution distant de Claude, ces
deux hôtes sont refusés par la politique réseau : l'audit ne peut pas y tourner.
"""

import json
import os
import re
import struct
import sys
import urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRE = os.path.join(RACINE, "src", "lib", "article-images.ts")
ARTICLES = os.path.join(RACINE, "content", "articles")

LARGEUR_MINI = 1200
RATIO_CIBLE = 1.91
POIDS_MAXI = 1_000_000

# On ne télécharge que le début du fichier : les dimensions sont dans l'en-tête.
# 64 Kio suffisent largement, y compris pour un JPEG à vignette EXIF.
TETE = 65536


def dimensions(donnees):
    """Rend (largeur, hauteur, format) lues dans l'en-tête, ou (0, 0, format)."""
    if donnees[:8] == b"\x89PNG\r\n\x1a\n":
        if donnees[12:16] == b"IHDR":
            l, h = struct.unpack(">II", donnees[16:24])
            return l, h, "PNG"
        return 0, 0, "PNG"

    if donnees[:3] == b"\xff\xd8\xff":
        i = 2
        while i + 9 < len(donnees):
            if donnees[i] != 0xFF:
                i += 1
                continue
            marqueur = donnees[i + 1]
            # SOF0..SOF15, sauf DHT (C4), JPG (C8) et DAC (CC)
            if 0xC0 <= marqueur <= 0xCF and marqueur not in (0xC4, 0xC8, 0xCC):
                h, l = struct.unpack(">HH", donnees[i + 5:i + 9])
                return l, h, "JPEG"
            if marqueur in (0xD8, 0x01) or 0xD0 <= marqueur <= 0xD7:
                i += 2
                continue
            taille = struct.unpack(">H", donnees[i + 2:i + 4])[0]
            i += 2 + taille
        return 0, 0, "JPEG"

    if donnees[:6] in (b"GIF87a", b"GIF89a"):
        l, h = struct.unpack("<HH", donnees[6:10])
        return l, h, "GIF"

    if donnees[:4] == b"RIFF" and donnees[8:12] == b"WEBP":
        bloc = donnees[12:16]
        if bloc == b"VP8 ":
            l, h = struct.unpack("<HH", donnees[26:30])
            return l & 0x3FFF, h & 0x3FFF, "WebP"
        if bloc == b"VP8L":
            b = struct.unpack("<I", donnees[21:25])[0]
            return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1, "WebP"
        if bloc == b"VP8X":
            l = int.from_bytes(donnees[24:27], "little") + 1
            h = int.from_bytes(donnees[27:30], "little") + 1
            return l, h, "WebP"
        return 0, 0, "WebP"

    # AVIF / HEIF : les dimensions sont dans une boîte « ispe ».
    if donnees[4:8] == b"ftyp":
        i = donnees.find(b"ispe")
        if i != -1 and i + 12 <= len(donnees):
            l, h = struct.unpack(">II", donnees[i + 8:i + 16])
            return l, h, "AVIF"
        return 0, 0, "AVIF"

    return 0, 0, "?"


def registre():
    src = open(REGISTRE, encoding="utf-8").read()
    hostinger = re.search(r'const HOSTINGER = "([^"]+)"', src).group(1)
    unsplash = re.search(r'const UNSPLASH = "([^"]+)"', src).group(1)
    bases = {"HOSTINGER": hostinger, "UNSPLASH": unsplash}
    entrees = {}
    for slug, base, suite in re.findall(
            r'"([^"]+)":\s*`\$\{(HOSTINGER|UNSPLASH)\}([^`]+)`', src):
        # getArticleOgImage agrandit les vignettes Unsplash pour le partage.
        url = bases[base] + suite
        if base == "UNSPLASH":
            url = re.sub(r"w=\d+", "w=1200", url)
            url = re.sub(r"h=\d+", "h=630", url)
        entrees[slug] = (url, base)
    return entrees


def interroger(url):
    requete = urllib.request.Request(url, headers={
        "User-Agent": "terre-etendue-audit/1.0",
        "Range": "bytes=0-%d" % (TETE - 1),
    })
    with urllib.request.urlopen(requete, timeout=25) as r:
        donnees = r.read(TETE)
        longueur = r.headers.get("Content-Range")
        if longueur and "/" in longueur:
            poids = int(longueur.rsplit("/", 1)[1])
        else:
            poids = int(r.headers.get("Content-Length") or len(donnees))
    return donnees, poids


def main():
    seuls_defauts = "--defauts" in sys.argv
    entrees = registre()
    slugs = {f[:-5] for f in os.listdir(ARTICLES) if f.endswith(".json")}
    lignes, defauts = [], 0

    for slug in sorted(slugs):
        url, base = entrees.get(slug, (None, "REPLI"))
        if url is None:
            lignes.append((slug, "—", "image de repli générique", True))
            defauts += 1
            continue
        try:
            donnees, poids = interroger(url)
        except Exception as e:  # réseau, 403, 404…
            lignes.append((slug, base, "inaccessible : %s" % e, True))
            defauts += 1
            continue

        l, h, fmt = dimensions(donnees)
        pb = []
        if l == 0:
            pb.append("dimensions illisibles (%s)" % fmt)
        else:
            if l < LARGEUR_MINI:
                pb.append("largeur %d px < %d" % (l, LARGEUR_MINI))
            if h and l / h < 1.4:
                pb.append("ratio %.2f — trop carré, viser %.2f" % (l / h, RATIO_CIBLE))
        if poids > POIDS_MAXI:
            pb.append("poids %.2f Mo > 1 Mo" % (poids / 1e6))

        etat = "%s %d×%d, %.0f Ko" % (fmt, l, h, poids / 1024)
        if pb:
            etat += " — " + " ; ".join(pb)
            defauts += 1
        lignes.append((slug, base, etat, bool(pb)))

    for slug, base, etat, mauvais in lignes:
        if seuls_defauts and not mauvais:
            continue
        print("%s %-52s %-10s %s" % ("✗" if mauvais else "✓", slug, base, etat))

    print("\n%d couverture(s) à revoir sur %d" % (defauts, len(lignes)))
    return 1 if defauts else 0


if __name__ == "__main__":
    sys.exit(main())
