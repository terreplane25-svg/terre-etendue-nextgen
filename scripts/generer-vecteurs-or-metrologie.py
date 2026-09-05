#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère les vecteurs d'or qui épinglent le port TypeScript du paquet `metrologie_image`.

Pourquoi ce fichier existe
──────────────────────────
L'outil d'analyse d'image tourne dans le navigateur — l'image ne doit pas
quitter la machine de l'opérateur — donc en TypeScript, alors que la référence
testée est le paquet Python `metrologie_image` (outil D). Deux implémentations
de la même formule, c'est le défaut que ce dépôt passe son temps à corriger.

Ce script fait calculer au Python un jeu de cas couvrant chaque fonction
portée, écrit le résultat, et `scripts/verifier-port-metrologie.mjs` refait les
mêmes calculs en TypeScript et compare.

Ce qui est couvert
──────────────────
  · l'étalonnage : pas pixel natif, recadrage, rééchantillonnage, point
    principal déplacé, angle exact contre angle paraxial, enveloppe quand le
    recadrage n'est pas documenté ;
  · la géométrie d'image : élévation apparente, dépression de l'horizon,
    angle de la portion émergente, coïncidence horizon / bas visible ;
  · l'inversion : aller-retour sur k, seuils de saturation et d'extinction,
    statuts de borne, régimes du Tableau 8 ;
  · la restitution : hauteur émergente exacte contre petit angle, fraction
    visible, et l'identité qui lie les deux chemins.

Les cas incluent délibérément les trois branches où le résultat cesse d'être
une valeur : cible entièrement visible, cible entièrement occultée, relevé
hors du domaine du modèle.

    python3 scripts/generer-vecteurs-or-metrologie.py
"""
import json
import math
import os
import sys
from datetime import datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
CIBLE = os.path.join(RACINE, "src", "lib", "metrologie-image", "vecteurs-or.json")

if "metrologie_image" not in sys.modules:
    try:
        import metrologie_image  # noqa: F401
    except ImportError:
        if not os.path.exists(VENV):
            sys.exit(
                "venv des outils absent : %s\n"
                "  python3 -m venv outils/.venv && outils/.venv/bin/pip install \\\n"
                "      -e outils/outil-A-visee-optique -e outils/outil-D-metrologie-image"
                % VENV
            )
        os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

from visee_optique.geometry import Cible, fraction_visible  # noqa: E402
from visee_optique.refraction import rayon_effectif  # noqa: E402

from metrologie_image.annotation import (  # noqa: E402
    FACTEUR_ELARGISSEMENT,
    Pointes,
    angle_portion_emergente,
    controler_horizon,
    dispersion_pointes,
)
from metrologie_image.inversion import (  # noqa: E402
    K_PLAFOND,
    K_PLANCHER,
    angle_horizon_base,
    angle_portion_visible,
    coefficient_refraction_effectif,
    elevation,
    elevation_horizon,
    k_d_extinction,
    k_de_saturation,
)
from metrologie_image.optique import (  # noqa: E402
    Cadrage,
    Capteur,
    Objectif,
    angle_entre_lignes,
    angle_entre_lignes_enveloppe,
    angle_entre_lignes_paraxial,
    cadrage_plein_capteur,
    capteur_equivalent_35mm,
    echelle_m_par_px,
    ordonnee_point_principal_px,
    pas_angulaire_rad,
    pas_pixel_livre_mm,
    resolution_angulaire_limite_rad,
)
from metrologie_image.synthese import (  # noqa: E402
    hauteur_emergente_mesuree,
    hauteur_emergente_petit_angle,
)

R0 = 6_371_008.8

# --- Les configurations d'appareil couvertes ---

APPAREILS = [
    # (nom, capteur, cadrage, objectif)
    (
        "plein format 24×36, 6000×4000, 300 mm, non recadré",
        Capteur(36.0, 6000, 4000),
        None,  # cadrage plein capteur, construit plus bas
        Objectif(300.0),
    ),
    (
        "même boîtier, recadré 1500×1000 à partir de (2250, 1500)",
        Capteur(36.0, 6000, 4000),
        Cadrage(1500, 1000, 1500, 1000, origine_x_px=2250, origine_y_px=1500),
        Objectif(300.0),
    ),
    (
        "recadré puis agrandi ×2 — le pas pixel se divise, l'information non",
        Capteur(36.0, 6000, 4000),
        Cadrage(3000, 2000, 1500, 1000, origine_x_px=2250, origine_y_px=1500),
        Objectif(300.0),
    ),
    (
        "recadré hors axe, en haut du capteur",
        Capteur(36.0, 6000, 4000),
        Cadrage(1200, 800, 1200, 800, origine_x_px=0, origine_y_px=0),
        Objectif(600.0),
    ),
    (
        "recadrage non documenté — le point principal est indisponible",
        Capteur(36.0, 6000, 4000),
        Cadrage(1500, 1000, 1500, 1000),
        Objectif(300.0),
    ),
    (
        "APS-C 23,5 mm, 6000×4000, 200 mm réels",
        Capteur(23.5, 6000, 4000),
        None,
        Objectif(200.0),
    ),
    (
        "équivalent 35 mm : capteur fictif de 36 mm, focale équivalente 306,4 mm",
        capteur_equivalent_35mm(6000, 4000),
        None,
        Objectif(200.0 * 36.0 / 23.5),
    ),
]

# --- Les scènes couvertes ---

SCENES = [
    # (nom, h_obs, H, z_b, D, k)
    ("phare 60 m, œil 30 m, 40 km, k standard", 30.0, 60.0, 0.0, 40_000.0, 0.13),
    ("même visée, sans réfraction", 30.0, 60.0, 0.0, 40_000.0, 0.0),
    ("même visée, réfraction forte", 30.0, 60.0, 0.0, 40_000.0, 0.30),
    ("même visée, infra-réfraction", 30.0, 60.0, 0.0, 40_000.0, -0.20),
    ("base surélevée de 12 m", 30.0, 45.0, 12.0, 55_000.0, 0.17),
    ("cible entière : 8 km, zone saturée", 30.0, 60.0, 0.0, 8_000.0, 0.13),
    ("Monte Cinto 2706 m à 200 km", 30.0, 2706.0, 0.0, 200_000.0, 0.13),
    ("Monte Cinto à 140 km", 30.0, 2706.0, 0.0, 140_000.0, 0.13),
    ("œil au ras de l'eau, 2 m", 2.0, 120.0, 0.0, 30_000.0, 0.13),
]


def cadrage_de(capteur, cadrage):
    return cadrage_plein_capteur(capteur) if cadrage is None else cadrage


def vecteurs_etalonnage():
    out = []
    for nom, capteur, cadrage, objectif in APPAREILS:
        c = cadrage_de(capteur, cadrage)
        entree = {
            "nom": nom,
            "capteur": {
                "largeur_mm": capteur.largeur_mm,
                "largeur_native_px": capteur.largeur_native_px,
                "hauteur_native_px": capteur.hauteur_native_px,
            },
            "cadrage": {
                "largeur_px": c.largeur_px,
                "hauteur_px": c.hauteur_px,
                "largeur_recadree_px": c.largeur_recadree_px,
                "hauteur_recadree_px": c.hauteur_recadree_px,
                "origine_x_px": c.origine_x_px,
                "origine_y_px": c.origine_y_px,
            },
            "focale_mm": objectif.focale_mm,
            "pas_pixel_mm": capteur.pas_pixel_mm,
            "pas_pixel_livre_mm": pas_pixel_livre_mm(capteur, c),
            "pas_angulaire_rad": pas_angulaire_rad(capteur, c, objectif),
            "facteur_reechantillonnage": c.facteur_reechantillonnage,
            "point_principal_connu": c.point_principal_connu,
            "recadree": c.recadree,
            "echelle_m_par_px_a_40km": echelle_m_par_px(40_000.0, capteur, c, objectif),
        }
        if c.point_principal_connu:
            entree["ordonnee_point_principal_px"] = ordonnee_point_principal_px(capteur, c)
        # Trois segments : centré sur l'axe quand c'est possible, et deux
        # excentrés, pour que l'écart exact/paraxial soit couvert des deux côtés.
        segments = []
        for y_haut, y_bas in ((100.0, 200.0), (300.0, 340.0), (10.0, 700.0)):
            if y_bas >= c.hauteur_px:
                continue
            seg = {
                "y_haut": y_haut,
                "y_bas": y_bas,
                "paraxial_rad": angle_entre_lignes_paraxial(
                    y_haut, y_bas, capteur, c, objectif
                ),
            }
            basse, haute = angle_entre_lignes_enveloppe(y_haut, y_bas, capteur, c, objectif)
            seg["borne_basse_rad"] = basse
            seg["borne_haute_rad"] = haute
            if c.point_principal_connu:
                seg["exact_rad"] = angle_entre_lignes(y_haut, y_bas, capteur, c, objectif)
            segments.append(seg)
        entree["segments"] = segments
        out.append(entree)
    return out


def vecteurs_geometrie():
    out = []
    for nom, h, H, z_b, D, k in SCENES:
        R = rayon_effectif(R0, k)
        cible = Cible(H=H, z_b=z_b)
        angle = angle_portion_visible(D, h, cible, R)
        out.append({
            "nom": nom,
            "h": h, "H": H, "z_b": z_b, "D": D, "k": k, "R": R,
            "elevation_horizon_rad": elevation_horizon(h, R),
            "elevation_sommet_rad": elevation(z_b + H, D, h, R),
            "elevation_base_rad": elevation(z_b, D, h, R),
            "angle_portion_visible_rad": angle,
            "angle_horizon_base_rad": angle_horizon_base(D, h, cible, R),
            "fraction_visible": fraction_visible(D, h, cible, R),
            "hauteur_emergente_m": (
                hauteur_emergente_mesuree(angle, D, h, cible, R) if angle > 0 else 0.0
            ),
            "hauteur_petit_angle_m": hauteur_emergente_petit_angle(angle, D),
        })
    return out


def vecteurs_inversion():
    out = []
    for nom, h, H, z_b, D, k in SCENES:
        cible = Cible(H=H, z_b=z_b)
        R = rayon_effectif(R0, k)
        angle = angle_portion_visible(D, h, cible, R)
        for u in (0.0, 1e-6, 3e-5):
            r = coefficient_refraction_effectif(angle, u, D, h, cible, R0)
            out.append({
                "nom": "%s | u=%g" % (nom, u),
                "h": h, "H": H, "z_b": z_b, "D": D,
                "angle_rad": angle, "u_rad": u,
                "statut": r.statut.value,
                "k": r.k, "k_min": r.k_min, "k_max": r.k_max,
                "k_saturation": r.k_saturation,
                "k_extinction": r.k_extinction,
                "dans_zone_saturee": r.dans_zone_saturee,
                "dans_zone_eteinte": r.dans_zone_eteinte,
                "regime": r.regime.value if r.regime else None,
                "regime_determine": r.regime_determine,
            })
    # Les trois branches sans valeur, explicitement.
    cible = Cible(H=60.0, z_b=0.0)
    R_plaf = rayon_effectif(R0, K_PLAFOND)
    R_planch = rayon_effectif(R0, K_PLANCHER)
    hors = [
        ("relevé nul — extinction", 0.0, 40_000.0, 30.0, Cible(H=60.0, z_b=0.0)),
        (
            "relevé au-delà du plafond — minoré",
            angle_portion_visible(40_000.0, 30.0, cible, R_plaf) * 1.5,
            40_000.0, 30.0, cible,
        ),
        (
            "relevé sous le plancher — majoré",
            angle_portion_visible(140_000.0, 30.0, Cible(H=2706.0), R_planch) * 0.5,
            140_000.0, 30.0, Cible(H=2706.0),
        ),
    ]
    for nom, angle, D, h, cbl in hors:
        r = coefficient_refraction_effectif(angle, 1e-6, D, h, cbl, R0)
        out.append({
            "nom": nom, "h": h, "H": cbl.H, "z_b": cbl.z_b, "D": D,
            "angle_rad": angle, "u_rad": 1e-6,
            "statut": r.statut.value,
            "k": r.k, "k_min": r.k_min, "k_max": r.k_max,
            "k_saturation": r.k_saturation,
            "k_extinction": r.k_extinction,
            "dans_zone_saturee": r.dans_zone_saturee,
            "dans_zone_eteinte": r.dans_zone_eteinte,
            "regime": r.regime.value if r.regime else None,
            "regime_determine": r.regime_determine,
        })
    return out


def vecteurs_seuils():
    out = []
    for nom, h, H, z_b, D, _k in SCENES:
        cible = Cible(H=H, z_b=z_b)
        out.append({
            "nom": nom, "h": h, "H": H, "z_b": z_b, "D": D,
            "k_saturation": k_de_saturation(D, h, cible, R0),
            "k_extinction": k_d_extinction(D, h, cible, R0),
        })
    return out


def vecteurs_pointes():
    """Trois clics complets, avec le contrôle d'horizon dans ses deux états."""
    capteur, objectif = Capteur(36.0, 6000, 4000), Objectif(300.0)
    c = cadrage_plein_capteur(capteur)
    y_pp = ordonnee_point_principal_px(capteur, c)
    r_pas = pas_angulaire_rad(capteur, c, objectif)
    out = []
    for nom, h, H, z_b, D, k in SCENES:
        cible = Cible(H=H, z_b=z_b)
        R = rayon_effectif(R0, k)
        angle = angle_portion_visible(D, h, cible, R)
        if angle <= 0:
            continue
        # L'horizon est placé là où le modèle le prédit, PLUS un décalage
        # délibéré. Sur une scène non occultée l'écart prédit n'est pas nul :
        # la base réelle y est au-dessous de l'horizon (voir
        # `test_base_sous_l_horizon_avant_la_distance_critique`). Un premier
        # jet plaçait l'horizon sur la base quelle que soit la scène, ce qui
        # rendait le cas « cible entière » incohérent — c'est le contrôle n° 9
        # qui l'a signalé avant l'écriture du fichier.
        ecart_predit_px = angle_horizon_base(D, h, cible, R) / r_pas
        for decalage, sigma in ((0.0, 3.0), (40.0, 3.0), (6.0, 6.0)):
            p = Pointes(
                y_horizon=y_pp + ecart_predit_px + decalage, y_base=y_pp,
                y_sommet=y_pp - angle / r_pas, sigma_px=sigma,
            )
            a = angle_portion_emergente(p, capteur, c, objectif)
            ctl = controler_horizon(p, capteur, c, objectif, D, h, cible, R)
            out.append({
                "nom": "%s | décalage %g px, σ %g px" % (nom, decalage, sigma),
                "decalage_px": decalage,
                "h": h, "H": H, "z_b": z_b, "D": D, "R": R,
                "y_horizon": p.y_horizon, "y_base": p.y_base, "y_sommet": p.y_sommet,
                "sigma_px": sigma,
                "angle_exact_rad": a.exact,
                "angle_paraxial_rad": a.paraxial,
                "incertitude_rad": a.incertitude,
                "controle_ecart_px": ctl.ecart_px,
                "controle_ecart_predit_px": ctl.ecart_predit_px,
                "controle_tolerance_px": ctl.tolerance_px,
                "controle_coherent": ctl.coherent,
            })
    return out


def vecteurs_divers():
    return {
        "facteur_elargissement": FACTEUR_ELARGISSEMENT,
        "k_plancher": K_PLANCHER,
        "k_plafond": K_PLAFOND,
        "dispersion": [
            {"pointes": [10.0, 12.0, 14.0], "ecart_type": dispersion_pointes((10.0, 12.0, 14.0))},
            {
                "pointes": [1901.0, 1904.5, 1899.0, 1902.0, 1900.5],
                "ecart_type": dispersion_pointes((1901.0, 1904.5, 1899.0, 1902.0, 1900.5)),
            },
        ],
        "diffraction": [
            {
                "lambda_m": 550e-9, "diametre_m": d,
                "limite_rad": resolution_angulaire_limite_rad(550e-9, d),
            }
            for d in (0.050, 0.0136, 0.100)
        ],
    }


def controle(doc):
    """Recalcule ce qui vient d'être écrit, par un chemin différent quand il y en a un.

    Un générateur qui se contente d'appeler les fonctions qu'il exporte ne
    prouve rien : il rendrait fidèlement une erreur. Ces contrôles confrontent
    les vecteurs à des identités que le code ne peut pas satisfaire par accident.
    """
    # 1. Coïncidence horizon / bas visible, sur toutes les scènes occultées.
    for g in doc["geometrie"]:
        if g["fraction_visible"] < 1.0 and g["angle_portion_visible_rad"] > 0:
            assert abs(g["angle_horizon_base_rad"]) < 1e-12, g["nom"]

    # 2. La fraction visible se retrouve depuis la hauteur émergente.
    for g in doc["geometrie"]:
        if g["angle_portion_visible_rad"] > 0:
            f = g["hauteur_emergente_m"] / g["H"]
            assert abs(f - g["fraction_visible"]) < 1e-9, g["nom"]

    # 3. Aller-retour de l'inversion à incertitude nulle.
    for i in doc["inversion"]:
        if i["u_rad"] == 0.0 and i["statut"] == "déterminé":
            assert i["k_min"] == i["k_max"] == i["k"], i["nom"]

    # 4. Un statut sans valeur n'a pas de k, ni de régime.
    for i in doc["inversion"]:
        if i["statut"] != "déterminé":
            assert i["k"] is None and i["regime"] is None, i["nom"]

    # 5. L'enveloppe encadre la valeur dès que l'incertitude est non nulle.
    for i in doc["inversion"]:
        if i["statut"] == "déterminé" and i["u_rad"] > 0:
            if i["k_min"] is not None and i["k_max"] is not None:
                assert i["k_min"] <= i["k"] <= i["k_max"], i["nom"]

    # 6. Le pas pixel livré ne dépend que du capteur et du rééchantillonnage.
    for e in doc["etalonnage"]:
        attendu = e["pas_pixel_mm"] / e["facteur_reechantillonnage"]
        assert abs(e["pas_pixel_livre_mm"] - attendu) < 1e-15, e["nom"]

    # 7. L'enveloppe d'angle encadre l'exact quand les deux existent.
    for e in doc["etalonnage"]:
        for s in e["segments"]:
            if "exact_rad" in s:
                assert s["borne_basse_rad"] <= s["exact_rad"] <= s["borne_haute_rad"], e["nom"]
                assert s["borne_basse_rad"] == s["borne_haute_rad"], e["nom"]

    # 8. Les deux voies de saisie de la focale rendent le même angle.
    aps = next(e for e in doc["etalonnage"] if e["nom"].startswith("APS-C"))
    eq = next(e for e in doc["etalonnage"] if e["nom"].startswith("équivalent"))
    for sa, se in zip(aps["segments"], eq["segments"]):
        assert abs(sa["exact_rad"] - se["exact_rad"]) < 1e-15, "voies de focale"

    # 9. Le contrôle d'horizon : cohérent si et seulement si l'écart relevé
    #    tient dans la tolérance autour de l'écart prédit — et l'écart prédit
    #    est nul exactement sur les scènes occultées.
    for p in doc["pointes"]:
        attendu = abs(p["controle_ecart_px"] - p["controle_ecart_predit_px"]) <= (
            p["controle_tolerance_px"]
        )
        assert p["controle_coherent"] is attendu, p["nom"]
        assert p["controle_coherent"] == (p["decalage_px"] <= p["controle_tolerance_px"]), p["nom"]
    for g in doc["geometrie"]:
        occultee = g["fraction_visible"] < 1.0
        if occultee and g["angle_portion_visible_rad"] > 0:
            assert g["angle_horizon_base_rad"] == 0.0 or abs(g["angle_horizon_base_rad"]) < 1e-12
        elif g["fraction_visible"] >= 1.0:
            assert g["angle_horizon_base_rad"] <= 0.0, g["nom"]

    # 10. La limite de Rayleigh contre la règle de pouce 138/D(mm) à 550 nm.
    for d in doc["divers"]["diffraction"]:
        arcsec = math.degrees(d["limite_rad"]) * 3600.0
        assert abs(arcsec - 138.0 / (d["diametre_m"] * 1000.0)) / arcsec < 0.01

    return 10


def main():
    doc = {
        "genere_le": datetime.now(timezone.utc).isoformat(),
        "source": "outils/outil-D-metrologie-image (paquet Python metrologie_image)",
        "avertissement": (
            "Fichier produit par scripts/generer-vecteurs-or-metrologie.py. "
            "Ne pas éditer à la main : il n'aurait plus de valeur d'épinglage. "
            "Corriger le Python, puis régénérer."
        ),
        "R0": R0,
        "etalonnage": vecteurs_etalonnage(),
        "geometrie": vecteurs_geometrie(),
        "inversion": vecteurs_inversion(),
        "seuils": vecteurs_seuils(),
        "pointes": vecteurs_pointes(),
        "divers": vecteurs_divers(),
    }
    n = controle(doc)
    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")
    total = (
        len(doc["etalonnage"]) + len(doc["geometrie"]) + len(doc["inversion"])
        + len(doc["seuils"]) + len(doc["pointes"])
    )
    print("Vecteurs écrits : %s" % os.path.relpath(CIBLE, RACINE))
    print("  %d cas — %d étalonnage, %d géométrie, %d inversion, %d seuils, %d pointés"
          % (total, len(doc["etalonnage"]), len(doc["geometrie"]),
             len(doc["inversion"]), len(doc["seuils"]), len(doc["pointes"])))
    print("  %d familles d'identités revérifiées avant écriture." % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
