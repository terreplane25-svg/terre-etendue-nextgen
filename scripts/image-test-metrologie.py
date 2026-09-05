#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fabrique l'image de test de l'outil D, et le relevé attendu qui va avec.

Ce que cette image est, et n'est pas
────────────────────────────────────
C'est un DIAGRAMME CALCULÉ, pas une photographie. Aucune scène réelle n'a été
capturée. Elle est construite à l'envers de la mesure : on part d'une scène
connue (D, h_obs, H, k), on calcule l'angle que le modèle prédit, on le
convertit en pixels avec l'étalonnage déclaré, et on dessine la cible à
exactement ces ordonnées.

L'interface doit alors retrouver le k de départ. Ce n'est pas une tautologie :
le chemin aller est ici, en Python, et le chemin retour est dans le navigateur,
en TypeScript, à travers le chargement de fichier, la lecture EXIF, les clics
sur le canevas et le tableau de bord. Ce test-là ne vérifie pas les formules —
les 786 contrôles d'épinglage s'en chargent — il vérifie le CÂBLAGE.

L'EXIF écrit porte un fabricant qui ne laisse aucun doute sur la nature du
fichier, et aucune coordonnée GPS : un diagramme n'a pas été pris quelque part.

    python3 scripts/image-test-metrologie.py
"""
import json
import math
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
SORTIE_IMG = os.path.join(RACINE, "public", "protocoles", "image-test-metrologie.jpg")
SORTIE_JSON = os.path.join(
    RACINE, "outils", "outil-D-metrologie-image", "tests", "releve-attendu.json"
)

if "metrologie_image" not in sys.modules:
    try:
        import metrologie_image  # noqa: F401
    except ImportError:
        os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

from PIL import Image, ImageDraw  # noqa: E402
from PIL.TiffImagePlugin import IFDRational  # noqa: E402
from visee_optique.geometry import Cible, fraction_visible  # noqa: E402
from visee_optique.refraction import rayon_effectif  # noqa: E402

from metrologie_image.annotation import Pointes, angle_portion_emergente  # noqa: E402
from metrologie_image.inversion import (  # noqa: E402
    angle_horizon_base,
    angle_portion_visible,
    coefficient_refraction_effectif,
)
from metrologie_image.optique import (  # noqa: E402
    Capteur,
    Objectif,
    cadrage_plein_capteur,
    ordonnee_point_principal_px,
    pas_angulaire_rad,
)
from metrologie_image.synthese import hauteur_emergente_mesuree  # noqa: E402

# --- L'appareil déclaré et la scène choisie ---

LARGEUR, HAUTEUR = 3000, 2000
CAPTEUR = Capteur(largeur_mm=36.0, largeur_native_px=LARGEUR, hauteur_native_px=HAUTEUR)
OBJECTIF = Objectif(focale_mm=600.0)
CADRAGE = cadrage_plein_capteur(CAPTEUR)

R0 = 6_371_008.8
D, H_OBS, H_CIBLE, Z_B, K_VRAI = 40_000.0, 30.0, 60.0, 0.0, 0.13
CIBLE = Cible(H=H_CIBLE, z_b=Z_B)

FABRICANT = "Terre Etendue (diagramme calcule)"
MODELE = "image-test-metrologie.py"

FOND_CIEL = (18, 26, 38)
FOND_MER = (10, 22, 36)
TRAIT = (59, 143, 212)
CIBLE_COULEUR = (196, 94, 106)
TEXTE = (168, 184, 204)


def main():
    R = rayon_effectif(R0, K_VRAI)
    angle = angle_portion_visible(D, H_OBS, CIBLE, R)
    pas = pas_angulaire_rad(CAPTEUR, CADRAGE, OBJECTIF)
    y_pp = ordonnee_point_principal_px(CAPTEUR, CADRAGE)

    # Le bas visible est placé sur l'axe optique : l'angle exact y coïncide
    # avec l'angle paraxial, ce qui rend le relevé attendu lisible à la main.
    y_base = y_pp
    y_sommet = y_base - angle / pas
    # L'horizon est placé là où le modèle le prédit — c'est-à-dire confondu
    # avec le bas visible, la cible étant occultée à cette distance.
    y_horizon = y_base + angle_horizon_base(D, H_OBS, CIBLE, R) / pas

    assert abs(y_horizon - y_base) < 1e-6, "cible non occultée : le test perd son objet"

    # --- Le dessin ---
    img = Image.new("RGB", (LARGEUR, HAUTEUR), FOND_CIEL)
    d = ImageDraw.Draw(img)
    y_h = int(round(y_horizon))
    d.rectangle([0, y_h, LARGEUR, HAUTEUR], fill=FOND_MER)
    d.line([(0, y_h), (LARGEUR, y_h)], fill=TRAIT, width=2)

    # La cible : un fût dont le sommet et le pied visible tombent exactement
    # aux ordonnées calculées. Le pied est à l'horizon, par construction.
    x0, larg = int(LARGEUR * 0.62), 34
    d.rectangle([x0, int(round(y_sommet)), x0 + larg, y_h], fill=CIBLE_COULEUR)
    d.rectangle([x0 - 8, int(round(y_sommet)) - 12, x0 + larg + 8, int(round(y_sommet))],
                fill=(228, 170, 120))

    d.text((30, 26), "DIAGRAMME CALCULE — PAS UNE PHOTOGRAPHIE", fill=TEXTE)
    d.text((30, 48), "Aucune scene reelle n'a ete capturee.", fill=TEXTE)
    d.text((30, HAUTEUR - 46),
           "D = 40 km, h_obs = 30 m, H = 60 m, k = 0,130 — f = 600 mm, capteur 36 mm, %dx%d"
           % (LARGEUR, HAUTEUR), fill=TEXTE)

    exif = Image.Exif()
    exif[0x010F] = FABRICANT
    exif[0x0110] = MODELE
    exif[0x0112] = 1
    sous = exif.get_ifd(0x8769)
    # IFDRational, et non un flottant nu : Pillow encoderait celui-ci en DOUBLE
    # (type TIFF 12), que la norme EXIF n'emploie pas pour ces tags.
    sous[0x920A] = IFDRational(600, 1)          # FocalLength
    sous[0xA405] = 600                          # FocalLengthIn35mmFilm — capteur 24×36
    sous[0x829D] = IFDRational(80, 10)          # FNumber
    sous[0xA002] = LARGEUR
    sous[0xA003] = HAUTEUR
    # Pas de sous-IFD GPS : un diagramme n'a pas été pris quelque part.

    os.makedirs(os.path.dirname(SORTIE_IMG), exist_ok=True)
    img.save(SORTIE_IMG, format="JPEG", quality=94, exif=exif)

    # --- Le relevé attendu, calculé sur les ordonnées ENTIÈRES réellement
    # dessinées : c'est ce que l'opérateur pourra pointer, au pixel près.
    pts = Pointes(
        y_horizon=float(y_h), y_base=float(y_h), y_sommet=float(int(round(y_sommet))),
        sigma_px=3.0,
    )
    a = angle_portion_emergente(pts, CAPTEUR, CADRAGE, OBJECTIF)
    res = coefficient_refraction_effectif(a.valeur, a.incertitude, D, H_OBS, CIBLE, R0)
    R_ret = rayon_effectif(R0, res.k)
    hauteur = hauteur_emergente_mesuree(a.valeur, D, H_OBS, CIBLE, R_ret)

    attendu = {
        "avertissement": (
            "Produit par scripts/image-test-metrologie.py. Diagramme calculé, "
            "pas une photographie."
        ),
        "image": os.path.relpath(SORTIE_IMG, RACINE),
        "appareil": {
            "largeur_capteur_mm": CAPTEUR.largeur_mm,
            "largeur_native_px": LARGEUR,
            "hauteur_native_px": HAUTEUR,
            "focale_mm": OBJECTIF.focale_mm,
        },
        "scene": {"D_km": D / 1000.0, "h_obs_m": H_OBS, "H_m": H_CIBLE, "z_b_m": Z_B},
        "k_de_construction": K_VRAI,
        "pointes_a_cliquer": {
            "y_horizon": pts.y_horizon, "y_base": pts.y_base, "y_sommet": pts.y_sommet,
            "sigma_px": pts.sigma_px,
        },
        "attendu": {
            "pas_angulaire_arcsec": math.degrees(pas) * 3600.0,
            "angle_emergent_arcsec": math.degrees(a.valeur) * 3600.0,
            "k": res.k,
            "k_min": res.k_min,
            "k_max": res.k_max,
            "statut": res.statut.value,
            "regime": res.regime.value if res.regime else None,
            "hauteur_emergente_m": hauteur,
            "fraction_visible": fraction_visible(D, H_OBS, CIBLE, R_ret),
            "ecart_horizon_base_predit_px": angle_horizon_base(D, H_OBS, CIBLE, R_ret) / pas,
        },
    }
    with open(SORTIE_JSON, "w", encoding="utf-8") as f:
        json.dump(attendu, f, ensure_ascii=False, indent=1)
        f.write("\n")

    print("Image écrite : %s (%d octets)"
          % (os.path.relpath(SORTIE_IMG, RACINE), os.path.getsize(SORTIE_IMG)))
    print("Relevé attendu : %s" % os.path.relpath(SORTIE_JSON, RACINE))
    print("  clics y = %.0f (horizon et base confondus), %.0f (sommet)"
          % (pts.y_base, pts.y_sommet))
    print("  angle %.3f″ — k retrouvé %.4f (construit à %.4f), régime « %s »"
          % (math.degrees(a.valeur) * 3600.0, res.k, K_VRAI, res.regime.value))
    print("  arrondi des ordonnées au pixel : %.4f d'écart sur k"
          % abs(res.k - K_VRAI))
    return 0


if __name__ == "__main__":
    sys.exit(main())
