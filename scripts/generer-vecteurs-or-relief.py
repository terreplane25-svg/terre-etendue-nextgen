#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vecteurs d'or du relief — épinglent le port TypeScript au paquet `visee_optique`.

Le simulateur du site tourne dans le navigateur, donc en TypeScript, mais la
référence reste le paquet Python et ses tests. Ce script fait calculer au
Python une série de cas, et écrit entrées et résultats attendus dans un fichier
que `scripts/verifier-port-relief.mjs` rejoue en TypeScript.

CE QUI EST COUVERT
──────────────────
  · la ligne de visée sphérique, sur cinq portées et cinq positions, avec des
    géométries inclinées et horizontales ;
  · la ligne de visée plane ;
  · le rayon effectif, sur tout l'intervalle de k usuel ;
  · les quatre situations que le module doit distinguer : rien ne masque,
    la courbure seule masque, le relief seul masque, les deux masquent ;
  · le relief NON ÉVALUÉ, qui n'est pas l'absence d'obstacle ;
  · la garde au-dessus du terrain, qui change le verdict sans changer la
    géométrie ;
  · les refus : profil désordonné, sans source, trop court, marge négative.

CONTRÔLE AVANT ÉCRITURE
───────────────────────
Le script revérifie ses propres cas avant d'écrire : que les quatre situations
sont bien QUATRE situations distinctes, et non quatre fois la même. Un
générateur dont tous les cas tomberaient dans le même régime produirait des
vecteurs qui passent toujours, des deux côtés, sans rien épingler.

    python3 scripts/generer-vecteurs-or-relief.py
"""
import json
import math
import os
import sys
from datetime import datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
PAQUET_A = os.path.join(RACINE, "outils", "outil-A-visee-optique")
CIBLE = os.path.join(RACINE, "src", "lib", "visee-optique", "vecteurs-or-relief.json")

sys.path.insert(0, PAQUET_A)
try:
    import visee_optique  # noqa: F401
except ImportError:
    if not os.path.exists(VENV):
        sys.exit("venv des outils absent : %s (voir outils/README.md)" % VENV)
    os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

from visee_optique.geodesy import (  # noqa: E402
    GRS80_A, GRS80_F, vincenty_direct, vincenty_inverse,
)
from visee_optique.geometry import Cible  # noqa: E402
from visee_optique.refraction import rayon_effectif  # noqa: E402
from visee_optique.relief import (  # noqa: E402
    RELIEF_NON_EVALUE,
    ReliefError,
    altitude_ligne_de_visee,
    altitude_ligne_de_visee_plane,
    analyser_relief,
    profil_depuis_couples,
    Obstacle,
    grouper_occlusions,
)

R_TERRE = 6371008.8


def profil_plat(D, n=40, altitude=0.0):
    return [(D * i / n, altitude) for i in range(n + 1)]


def profil_colline(D, n=40, indice=20, hauteur=200.0):
    couples = profil_plat(D, n)
    couples[indice] = (D * indice / n, hauteur)
    return couples


#: Une colline placée EXACTEMENT un mètre sous la ligne de visée, à mi-chemin.
#: La hauteur est calculée depuis la géométrie, jamais devinée : une valeur
#: choisie à la main tomberait du mauvais côté de la ligne au premier
#: changement de portée, et le cas cesserait silencieusement de tester la
#: garde — ce qui s'est produit à la première rédaction, et que le contrôle en
#: fin de script a intercepté.
_COLLINE_RASANTE = altitude_ligne_de_visee(5_000.0, 10_000.0, 10.0, 110.0, R_TERRE) - 1.0

#: Les quatre situations à distinguer, plus les variantes. Chaque entrée :
#: (nom, D, h, H, z_b, k, couples de profil ou None, marge requise).
CAS = [
    ("rien ne masque", 8_000.0, 10.0, 110.0, 0.0, 0.13, profil_plat(8_000.0), 0.0),
    ("la courbure seule masque", 60_000.0, 10.0, 110.0, 0.0, 0.13, profil_plat(60_000.0), 0.0),
    ("le relief seul masque", 8_000.0, 10.0, 110.0, 0.0, 0.13, profil_colline(8_000.0), 0.0),
    ("les deux masquent", 60_000.0, 10.0, 110.0, 0.0, 0.13,
     profil_colline(60_000.0, hauteur=300.0), 0.0),
    ("relief non évalué", 30_000.0, 10.0, 110.0, 0.0, 0.13, None, 0.0),
    ("garde de 5 m sur terrain rasant", 10_000.0, 10.0, 110.0, 0.0, 0.0,
     profil_colline(10_000.0, indice=20, hauteur=_COLLINE_RASANTE), 5.0),
    ("sans garde sur le même terrain", 10_000.0, 10.0, 110.0, 0.0, 0.0,
     profil_colline(10_000.0, indice=20, hauteur=_COLLINE_RASANTE), 0.0),
    ("trois bosses, la pire au milieu", 12_000.0, 10.0, 110.0, 0.0, 0.2,
     [(12_000.0 * i / 60, 400.0 if i == 30 else (150.0 if i == 15 else (200.0 if i == 45 else 0.0)))
      for i in range(61)], 0.0),
    ("cible surélevée sur un plateau", 25_000.0, 300.0, 40.0, 250.0, 0.13,
     profil_plat(25_000.0, altitude=100.0), 0.0),
    ("k nul, sphère nue", 45_000.0, 12.0, 110.0, 0.0, 0.0, profil_plat(45_000.0), 0.0),
    ("k fort, réfraction marquée", 45_000.0, 12.0, 110.0, 0.0, 0.4, profil_plat(45_000.0), 0.0),
]

REFUS = [
    ("profil désordonné", lambda: profil_depuis_couples([(0, 0), (500, 1), (200, 2)], "essai")),
    ("profil sans source", lambda: profil_depuis_couples([(0, 0), (100, 1)], "   ")),
    ("profil d'un seul point", lambda: profil_depuis_couples([(0, 0)], "essai")),
    ("marge requise négative", lambda: analyser_relief(
        1000.0, 1.0, Cible(H=10.0), R_TERRE,
        profil=profil_depuis_couples(profil_plat(1000.0), "essai"), marge_requise_m=-1.0)),
    ("distance nulle", lambda: analyser_relief(0.0, 1.0, Cible(H=10.0), R_TERRE)),
    ("rayon nul", lambda: altitude_ligne_de_visee(0.0, 1000.0, 0.0, 0.0, 0.0)),
]


def obstacle_en_dict(o):
    if o is None:
        return None
    return {
        "distance_m": o.distance_m,
        "altitude_terrain_m": o.altitude_terrain_m,
        "altitude_visee_m": o.altitude_visee_m,
        "manque_m": o.manque_m,
    }


#: Les cas du regroupement. Chacun isole UNE dimension : sans eux, une
#: implémentation qui compterait les points au lieu des reliefs, ou qui
#: retiendrait le premier point au lieu du plus gênant, passerait.
CAS_OCCLUSIONS = [
    ("aucun obstacle", 250.0, []),
    ("un point isolé", 250.0, [(7000, 3)]),
    # Une colline large : c'est le cas qui distingue « compter les reliefs »
    # de « compter les points ».
    ("une colline de vingt points", 250.0,
     [(4000 + 250 * i, 10 + i) for i in range(20)]),
    # Le sommet n'est ni le premier ni le dernier point.
    ("sommet au milieu", 250.0, [(4000, 5), (4250, 31), (4500, 12)]),
    # Une trouée d'un pas entier sépare ; le pas nominal ne sépare pas.
    ("deux reliefs séparés par une trouée", 250.0,
     [(4250, 10), (4500, 10), (5000, 10), (5250, 14)]),
    ("trois reliefs", 500.0,
     [(2000, 4), (2500, 9), (11000, 2), (30000, 40), (30500, 38)]),
    # Points désordonnés : l'ordre décide des groupes.
    ("points en désordre", 250.0, [(4500, 10), (4000, 10), (4250, 10)]),
    # Sans pas déclaré, l'écart minimal observé sert de référence.
    ("sans pas déclaré", None, [(4000, 10), (4250, 10), (9000, 10)]),
]


def main():
    v = {
        "genere_le": datetime.now(timezone.utc).isoformat(),
        "source": "visee_optique.relief (paquet Python)",
        "avertissement": (
            "Fichier généré. Ne pas modifier à la main : il est la référence "
            "contre laquelle le port TypeScript est vérifié."
        ),
        "relief_non_evalue": RELIEF_NON_EVALUE,
        "rayon_terre_m": R_TERRE,
        "vincenty_direct": [],
        "ligne_de_visee": [],
        "ligne_de_visee_plane": [],
        "analyses": [],
        "refus": [],
        # Le regroupement des points qui dépassent en RELIEFS contigus. Sans
        # lui, une colline échantillonnée vingt fois s'annoncerait « 20
        # occlusions » — faux dans le seul sens qui compte, celui du nombre.
        "occlusions": [
            {
                "nom": nom,
                "pas_m": pas,
                "obstacles": [[d, mq] for d, mq in points],
                "groupes": [
                    {
                        "debut_m": o.debut_m, "fin_m": o.fin_m,
                        "largeur_m": o.largeur_m, "nb_points": o.nb_points,
                        "sommet": obstacle_en_dict(o.sommet),
                    }
                    for o in grouper_occlusions(
                        [Obstacle(float(d), 100.0, 100.0 - mq, float(mq)) for d, mq in points],
                        pas,
                    )
                ],
            }
            for nom, pas, points in CAS_OCCLUSIONS
        ],
    }

    # La formule directe, qui place les points du profil le long de la
    # géodésique. Les cas couvrent les deux hémisphères, le passage de
    # l'antiméridien, les azimuts cardinaux et obliques, et des distances de
    # 100 m à 500 km.
    for lat, lon in ((50.94642, 1.75305), (-33.87, 151.21), (0.0, 179.9), (78.2, -15.6)):
        for az in (0.0, 45.0, 90.0, 187.5, 270.0, 359.9):
            for dist in (100.0, 5_000.0, 35_610.7, 200_000.0, 500_000.0):
                lat2, lon2 = vincenty_direct(lat, lon, az, dist)
                v["vincenty_direct"].append({
                    "lat1": lat, "lon1": lon, "azimut1": az, "distance_m": dist,
                    "lat2": lat2, "lon2": lon2,
                })

    # La ligne de visée, sur des géométries variées : inclinée, horizontale,
    # descendante, et à des portées couvrant trois ordres de grandeur.
    for D in (1_000.0, 10_000.0, 35_610.7, 100_000.0, 250_000.0):
        for h, z in ((12.0, 110.0), (12.0, 12.0), (300.0, 20.0), (0.0, 980.0)):
            for frac in (0.0, 0.1, 0.5, 0.9, 1.0):
                for k in (0.0, 0.13, 0.4):
                    R = rayon_effectif(R_TERRE, k)
                    v["ligne_de_visee"].append({
                        "D": D, "h": h, "z_vise": z, "k": k, "R": R,
                        "distance_m": frac * D,
                        "altitude": altitude_ligne_de_visee(frac * D, D, h, z, R),
                    })
                v["ligne_de_visee_plane"].append({
                    "D": D, "h": h, "z_vise": z, "distance_m": frac * D,
                    "altitude": altitude_ligne_de_visee_plane(frac * D, D, h, z),
                })

    for nom, D, h, H, z_b, k, couples, marge in CAS:
        cible = Cible(H=H, z_b=z_b)
        R = rayon_effectif(R_TERRE, k)
        profil = None
        if couples is not None:
            profil = profil_depuis_couples(couples, source="profil d'essai", pas_m=None)
        spherique = analyser_relief(D, h, cible, R, profil=profil, marge_requise_m=marge)
        plan = analyser_relief(D, h, cible, None, profil=profil,
                               modele="plan", marge_requise_m=marge)
        v["analyses"].append({
            "nom": nom, "D": D, "h": h, "H": H, "z_b": z_b, "k": k, "R": R,
            "marge_requise_m": marge,
            "profil": None if couples is None else [list(c) for c in couples],
            "spherique": {
                "hauteur_occultee_courbure_m": spherique.hauteur_occultee_courbure_m,
                "fraction_visible_courbure": spherique.fraction_visible_courbure,
                "relief_evalue": spherique.relief_evalue,
                "motif_relief_non_evalue": spherique.motif_relief_non_evalue,
                "masque_par_le_relief": spherique.masque_par_le_relief,
                "nombre_obstacles": len(spherique.obstacles),
                "obstacle_le_plus_genant": obstacle_en_dict(spherique.obstacle_le_plus_genant),
                "marge_minimale_m": spherique.marge_minimale_m,
                "distance_marge_minimale_m": spherique.distance_marge_minimale_m,
            },
            "plan": {
                "hauteur_occultee_courbure_m": plan.hauteur_occultee_courbure_m,
                "fraction_visible_courbure": plan.fraction_visible_courbure,
                "masque_par_le_relief": plan.masque_par_le_relief,
                "nombre_obstacles": len(plan.obstacles),
                "obstacle_le_plus_genant": obstacle_en_dict(plan.obstacle_le_plus_genant),
                "marge_minimale_m": plan.marge_minimale_m,
            },
        })

    for nom, appel in REFUS:
        try:
            appel()
            sys.exit("le cas de refus « %s » n'a pas levé côté Python" % nom)
        except (ReliefError, ValueError) as exc:
            v["refus"].append({"nom": nom, "message_python": str(exc)})

    controle(v)

    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("Écrit : %s" % os.path.relpath(CIBLE, RACINE))
    print("  %d Vincenty direct, %d lignes de visée, %d visées planes, %d analyses, %d refus"
          % (len(v["vincenty_direct"]), len(v["ligne_de_visee"]),
             len(v["ligne_de_visee_plane"]), len(v["analyses"]), len(v["refus"])))
    return 0


def controle(v):
    # 0. Le regroupement compte des RELIEFS, pas des points de mesure.
    par_nom = {c["nom"]: c for c in v["occlusions"]}
    vingt = par_nom["une colline de vingt points"]
    assert len(vingt["obstacles"]) == 20, "le cas n'a plus vingt points"
    assert len(vingt["groupes"]) == 1, (
        "la colline se compte encore en points : le regroupement ne sert à rien")
    assert vingt["groupes"][0]["nb_points"] == 20
    # Le sommet retenu est le pire, ni le premier ni le dernier.
    milieu = par_nom["sommet au milieu"]["groupes"][0]
    assert milieu["sommet"]["manque_m"] == 31.0, milieu["sommet"]
    assert milieu["sommet"]["distance_m"] == 4250.0
    # Une trouée sépare réellement — sinon le cas ne discrimine rien.
    assert len(par_nom["deux reliefs séparés par une trouée"]["groupes"]) == 2
    assert len(par_nom["trois reliefs"]["groupes"]) == 3
    assert par_nom["aucun obstacle"]["groupes"] == []
    assert par_nom["un point isolé"]["groupes"][0]["largeur_m"] == 0.0

    """Revérifie que les vecteurs épinglent bien ce qu'ils prétendent épingler.

    Un générateur qui écrirait onze cas tombant tous dans le même régime
    produirait des vecteurs qui passent des deux côtés sans rien contrôler. Ces
    contrôles échouent AVANT l'écriture du fichier.
    """
    par_nom = {a["nom"]: a for a in v["analyses"]}

    # 1. Les quatre situations sont bien quatre situations distinctes.
    rien = par_nom["rien ne masque"]["spherique"]
    assert rien["hauteur_occultee_courbure_m"] == 0.0, "« rien ne masque » : la courbure masque"
    assert rien["masque_par_le_relief"] is False, "« rien ne masque » : le relief masque"

    courbure = par_nom["la courbure seule masque"]["spherique"]
    assert courbure["hauteur_occultee_courbure_m"] > 0.0
    assert courbure["masque_par_le_relief"] is False, "la mer est comptée comme relief"

    relief = par_nom["le relief seul masque"]["spherique"]
    assert relief["hauteur_occultee_courbure_m"] == 0.0
    assert relief["masque_par_le_relief"] is True

    deux = par_nom["les deux masquent"]["spherique"]
    assert deux["hauteur_occultee_courbure_m"] > 0.0
    assert deux["masque_par_le_relief"] is True

    # 2. Le relief non évalué n'est pas une absence d'obstacle.
    non_eval = par_nom["relief non évalué"]["spherique"]
    assert non_eval["masque_par_le_relief"] is None
    assert non_eval["relief_evalue"] is False
    assert non_eval["motif_relief_non_evalue"] == RELIEF_NON_EVALUE

    # 3. La garde change le verdict, sur un terrain identique.
    avec = par_nom["garde de 5 m sur terrain rasant"]["spherique"]
    sans = par_nom["sans garde sur le même terrain"]["spherique"]
    assert avec["masque_par_le_relief"] is True, "la garde ne change rien : cas mal choisi"
    assert sans["masque_par_le_relief"] is False, "la garde ne change rien : cas mal choisi"
    assert avec["marge_minimale_m"] == sans["marge_minimale_m"], (
        "la géométrie devrait être identique entre les deux"
    )

    # 4. Le modèle plan n'occulte jamais, mais voit le même relief.
    for a in v["analyses"]:
        assert a["plan"]["hauteur_occultee_courbure_m"] == 0.0, a["nom"]
        assert a["plan"]["fraction_visible_courbure"] == 1.0, a["nom"]
    assert par_nom["le relief seul masque"]["plan"]["masque_par_le_relief"] is True

    # 5. Le relief se voit IDENTIQUEMENT dans les deux modèles quand la visée
    #    ne plonge pas sous la surface. C'est ce qui en fait un discriminant.
    r = par_nom["le relief seul masque"]
    assert r["spherique"]["nombre_obstacles"] == r["plan"]["nombre_obstacles"]

    # 6. k modifie réellement le résultat : sinon la réfraction ne serait pas câblée.
    assert (par_nom["k nul, sphère nue"]["spherique"]["hauteur_occultee_courbure_m"]
            > par_nom["k fort, réfraction marquée"]["spherique"]["hauteur_occultee_courbure_m"]), (
        "k ne change pas l'occultation : la réfraction n'est pas prise en compte"
    )

    # 7. La formule directe est l'inverse de la formule inverse. Ce contrôle
    #    ne compare pas la fonction à elle-même : il l'oppose à une AUTRE
    #    fonction du paquet, écrite séparément et éprouvée par ses propres
    #    tests. Un décalage de signe ou une confusion latitude/longitude y
    #    apparaîtrait immédiatement.
    ecart_max = 0.0
    for c in v["vincenty_direct"]:
        geo = vincenty_inverse(c["lat1"], c["lon1"], c["lat2"], c["lon2"])
        ecart_max = max(ecart_max, abs(geo.distance_m - c["distance_m"]))
    # Le seuil est DÉRIVÉ, pas choisi : les deux formules itèrent jusqu'à ce
    # que sigma varie de moins de 1e-12 radian, et sigma est multiplié par le
    # demi-petit axe b ≈ 6,36·10⁶ m. L'accord ne peut donc pas être meilleur
    # que b·tol ≈ 6,4 µm, quelle que soit la justesse des deux implémentations.
    # Un désaccord de formule, lui, se compterait en mètres.
    seuil = GRS80_A * (1.0 - GRS80_F) * 1e-12 * 2.0
    assert ecart_max < seuil, (
        "aller-retour direct/inverse : écart de %.3e m au-delà du plancher de "
        "convergence %.3e m — les deux formules ne décrivent pas la même "
        "géodésique" % (ecart_max, seuil)
    )

    # 8. Aucun NaN ni infini n'a été écrit : ils traverseraient JSON en `null`
    #    ou en littéral invalide, et le port comparerait n'importe quoi.
    def sans_nan(x, chemin=""):
        if isinstance(x, float):
            assert math.isfinite(x), "valeur non finie en %s" % chemin
        elif isinstance(x, dict):
            for k, val in x.items():
                sans_nan(val, chemin + "/" + str(k))
        elif isinstance(x, list):
            for i, val in enumerate(x):
                sans_nan(val, chemin + "[%d]" % i)
    sans_nan(v)

    print("  8 contrôles passés avant écriture (dont l'aller-retour Vincenty, écart max %.1e m)."
          % ecart_max)


if __name__ == "__main__":
    sys.exit(main())
