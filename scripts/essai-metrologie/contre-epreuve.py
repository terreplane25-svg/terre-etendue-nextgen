#!/usr/bin/env python3
"""Recalcule, avec le paquet Python de référence, ce que le navigateur a rendu.

Reçoit les trois ordonnées RÉELLEMENT enregistrées par l'interface — pas des
ordonnées idéales — et rend k, l'angle et la hauteur émergente. Le navigateur
est ainsi jugé sur son propre relevé, par l'implémentation qui fait référence.
"""
import json
import math
import sys

from visee_optique.geometry import Cible
from visee_optique.refraction import rayon_effectif
from metrologie_image.annotation import Pointes, angle_portion_emergente
from metrologie_image.inversion import coefficient_refraction_effectif
from metrologie_image.optique import Capteur, Objectif, cadrage_plein_capteur
from metrologie_image.synthese import hauteur_emergente_mesuree

CAPTEUR = Capteur(largeur_mm=36.0, largeur_native_px=3000, hauteur_native_px=2000)
OBJECTIF = Objectif(focale_mm=600.0)
CADRAGE = cadrage_plein_capteur(CAPTEUR)
R0, D, H_OBS, H_CIBLE, Z_B = 6_371_008.8, 40_000.0, 30.0, 60.0, 0.0

p = json.load(open(sys.argv[1], encoding="utf-8"))
pts = Pointes(
    y_horizon=p["y_horizon"], y_base=p["y_base"],
    y_sommet=p["y_sommet"], sigma_px=p["sigma_px"],
)
cible = Cible(H=H_CIBLE, z_b=Z_B)
a = angle_portion_emergente(pts, CAPTEUR, CADRAGE, OBJECTIF)
r = coefficient_refraction_effectif(a.valeur, a.incertitude, D, H_OBS, cible, R0)
hauteur = hauteur_emergente_mesuree(a.valeur, D, H_OBS, cible, rayon_effectif(R0, r.k))

print(json.dumps({
    "k": r.k,
    "statut": r.statut.value,
    "angle_arcsec": math.degrees(a.valeur) * 3600.0,
    "hauteur_m": hauteur,
}))
