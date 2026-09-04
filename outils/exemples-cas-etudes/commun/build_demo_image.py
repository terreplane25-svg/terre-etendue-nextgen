"""
build_demo_image.py — Le diagramme JPEG que les quatre cas d'étude attendaient.

Les `run_case.py` livrés importaient `construire_image_demo` d'un module
`build_demo_image` absent de l'archive : les quatre cas échouaient à l'import.
Ce module le fournit.

CE QUE CETTE IMAGE EST, ET N'EST PAS
────────────────────────────────────
C'est un **diagramme calculé**, pas une photographie. Aucune scène réelle n'a
été capturée : ni capteur, ni objectif, ni lieu. C'est délibéré et c'est dit
partout où le fichier apparaît — les cas d'étude eux-mêmes le déclarent dans
leur chaîne de détention (« image générée par ordinateur, aucune scène réelle
capturée »), et l'EXIF écrit ici porte un fabricant qui ne laisse aucun doute.

Elle sert uniquement à faire tourner la chaîne de bout en bout : un fichier
existe, il a une empreinte, il porte des métadonnées lisibles. Une vraie
campagne remplacerait ce fichier par une vraie photographie, et la fiche
d'observation le dirait.

L'EXIF est écrit par Pillow et relu par `preuve_image.metadata` — deux
implémentations indépendantes qui se rencontrent, ce qui donne au passage un
contrôle croisé que ni l'une ni l'autre ne fournirait seule.

Aucune coordonnée GPS n'est écrite : un diagramme n'a pas été pris quelque
part, et inventer une position serait exactement ce que le protocole interdit.
"""

from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw
from PIL.TiffImagePlugin import IFDRational

# Le boîtier déclaré. Personne ne peut confondre ça avec un appareil.
FABRICANT = "Terre Etendue (diagramme calcule)"
MODELE = "build_demo_image.py"

LARGEUR, HAUTEUR = 1600, 900
# Les trois grandeurs rationnelles sont écrites en IFDRational, pas en flottant
# Python. Pillow encode un flottant nu en DOUBLE (type TIFF 12), que la norme
# EXIF n'emploie pas pour ces tags : notre lecteur, qui n'implémente que les
# types du protocole, rendait alors les octets bruts. Le contrôle croisé entre
# les deux implémentations a mis le défaut au jour, et c'est l'écriture qui
# était fautive, pas la lecture.
FOCALE_MM = IFDRational(300, 1)
FOCALE_EQ_35MM = 300
OUVERTURE = IFDRational(80, 10)
TEMPS_POSE_S = IFDRational(1, 500)
SENSIBILITE_ISO = 100

FOND = (13, 17, 23)        # #0d1117, le fond sombre des schémas du site
CIEL = (18, 26, 38)
MER = (10, 22, 36)
TRAIT = (59, 143, 212)     # cyan
CIBLE = (196, 94, 106)     # rose
TEXTE = (168, 184, 204)


def _dessiner(img: Image.Image) -> None:
    """Un horizon courbe et une silhouette partiellement occultée.

    La courbure est exagérée : c'est un schéma de principe, pas une projection
    à l'échelle, et le prendre pour une mesure serait un contresens.
    """
    d = ImageDraw.Draw(img)
    horizon_y = int(HAUTEUR * 0.62)

    d.rectangle([0, 0, LARGEUR, horizon_y], fill=CIEL)
    d.rectangle([0, horizon_y, LARGEUR, HAUTEUR], fill=MER)

    # Ligne d'horizon, légèrement bombée.
    fleche = 26
    points = [
        (x, horizon_y - int(fleche * math.sin(math.pi * x / LARGEUR)))
        for x in range(0, LARGEUR + 1, 8)
    ]
    d.line(points, fill=TRAIT, width=3)

    # Silhouette schématique : la base passe sous l'horizon, le sommet dépasse.
    base_x, largeur_cible = int(LARGEUR * 0.68), 54
    sommet_y = horizon_y - 150
    base_y = horizon_y + 40
    d.rectangle([base_x, sommet_y, base_x + largeur_cible, base_y], fill=CIBLE)
    # La partie sous l'horizon est masquée par la mer : on la recouvre.
    y_horizon_local = horizon_y - int(fleche * math.sin(math.pi * base_x / LARGEUR))
    d.rectangle([base_x - 4, y_horizon_local, base_x + largeur_cible + 4, HAUTEUR], fill=MER)
    d.line(points, fill=TRAIT, width=3)

    d.text((28, 24), "DIAGRAMME CALCULE — PAS UNE PHOTOGRAPHIE", fill=TEXTE)
    d.text((28, 46), "Aucune scene reelle n'a ete capturee.", fill=TEXTE)
    d.text((28, HAUTEUR - 40), f"{LARGEUR}x{HAUTEUR} — {MODELE}", fill=TEXTE)


def construire_image_demo(chemin: Path | str, maintenant: datetime) -> Path:
    """Écrit le diagramme en JPEG, avec un EXIF lisible par `preuve_image`.

    `maintenant` doit être un datetime conscient du fuseau (les cas passent
    l'heure UTC) : il devient DateTimeOriginal, au format EXIF.
    """
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (LARGEUR, HAUTEUR), FOND)
    _dessiner(img)

    exif = Image.Exif()
    exif[0x010F] = FABRICANT          # Make
    exif[0x0110] = MODELE             # Model
    exif[0x0112] = 1                  # Orientation, normale
    sous = exif.get_ifd(0x8769)       # sous-IFD Exif
    sous[0x920A] = FOCALE_MM          # FocalLength
    sous[0xA405] = FOCALE_EQ_35MM     # FocalLengthIn35mmFilm
    sous[0x829D] = OUVERTURE          # FNumber
    sous[0x829A] = TEMPS_POSE_S       # ExposureTime
    sous[0x8827] = SENSIBILITE_ISO    # ISOSpeedRatings
    sous[0xA002] = LARGEUR            # PixelXDimension
    sous[0xA003] = HAUTEUR            # PixelYDimension
    sous[0x9003] = maintenant.strftime("%Y:%m:%d %H:%M:%S")  # DateTimeOriginal
    # Pas de sous-IFD GPS : un diagramme n'a pas été pris quelque part.

    img.save(chemin, format="JPEG", quality=92, exif=exif)
    return chemin


if __name__ == "__main__":
    import sys
    from datetime import timezone

    sortie = Path(sys.argv[1] if len(sys.argv) > 1 else "DEMO_diagramme_horizon.jpg")
    construire_image_demo(sortie, datetime.now(timezone.utc))
    print(f"Écrit : {sortie} ({sortie.stat().st_size} octets)")
