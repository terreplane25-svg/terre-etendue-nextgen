#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fabrique la photo de charge de l'audit mobile : 12 Mpx, EXIF, bruit réel.

Pourquoi générer plutôt que versionner
──────────────────────────────────────
Le fichier pèse 3,4 Mo. Le dépôt n'a pas à porter ce poids pour un usage qui
n'existe qu'au moment de l'audit : il est reconstruit à l'identique par ce
script, que `scripts/essai-metrologie/audit-mobile.mjs` appelle si le fichier
manque. `public/audit/` est donc ignoré par git.

Pourquoi ce contenu
───────────────────
Le bruit n'est pas décoratif. Une image lisse se compresse à quelques dizaines
de kilo-octets, et l'audit mesurerait alors une empreinte SHA-256 sur un
fichier qui n'a rien d'une photographie. Le tirage est déterministe (graine
fixe) pour que deux exécutions donnent le même fichier, donc la même empreinte.

Ce n'est pas une photographie : aucune scène réelle n'a été capturée, et l'EXIF
le déclare. Elle ne sert qu'à charger la chaîne, jamais à mesurer quoi que ce
soit.

    python3 scripts/photo-charge-mobile.py
"""
import os
import random
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
SORTIE = os.path.join(RACINE, "public", "audit", "photo-charge.jpg")

try:
    from PIL import Image, ImageDraw
    from PIL.TiffImagePlugin import IFDRational
except ImportError:  # pragma: no cover - dépend de l'environnement
    if not os.path.exists(VENV):
        sys.exit(
            "Pillow absent. Depuis la racine :\n"
            "  python3 -m venv outils/.venv && outils/.venv/bin/pip install Pillow"
        )
    os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

# Définition d'un capteur de téléphone courant.
LARGEUR, HAUTEUR = 4032, 3024
GRAINE = 7


def main():
    img = Image.new("RGB", (LARGEUR, HAUTEUR), (18, 26, 38))
    d = ImageDraw.Draw(img)
    alea = random.Random(GRAINE)
    for _ in range(60_000):
        x, y = alea.randrange(LARGEUR), alea.randrange(HAUTEUR)
        d.rectangle(
            [x, y, x + alea.randrange(2, 9), y + alea.randrange(2, 9)],
            fill=(alea.randrange(255), alea.randrange(255), alea.randrange(255)),
        )
    d.rectangle([0, int(HAUTEUR * 0.62), LARGEUR, HAUTEUR], fill=(10, 22, 36))

    exif = Image.Exif()
    exif[0x010F] = "Terre Etendue (image de charge, pas une photographie)"
    exif[0x0110] = "photo-charge-mobile.py"
    sous = exif.get_ifd(0x8769)
    sous[0x920A] = IFDRational(240, 1)   # FocalLength
    sous[0xA405] = 240                   # FocalLengthIn35mmFilm
    sous[0x829D] = IFDRational(56, 10)   # FNumber
    sous[0xA002] = LARGEUR
    sous[0xA003] = HAUTEUR
    sous[0x9003] = "2026:09:05 10:14:22"
    # Pas de sous-IFD GPS : cette image n'a pas été prise quelque part.

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    img.save(SORTIE, format="JPEG", quality=92, exif=exif)
    print("Écrit : %s — %.2f Mo, %d×%d"
          % (os.path.relpath(SORTIE, RACINE), os.path.getsize(SORTIE) / 1e6, LARGEUR, HAUTEUR))
    return 0


if __name__ == "__main__":
    sys.exit(main())
