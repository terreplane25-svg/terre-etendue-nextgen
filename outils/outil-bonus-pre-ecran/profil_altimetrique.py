"""
profil_altimetrique.py — pré-écran altimétrique a priori pour la sélection
d'un couple poste/cible (Tableau 10, §12.3 : « profil intermédiaire »).

NÉ D'UNE ERREUR : le cas CAS-DEMO-CHASSIRON-001 a d'abord été bâti (archive
complète A→B→C) sur un couple Chassiron↔Cordouan jugé valide par une
comparaison à quelques points côtiers nommés — jugement qui s'est révélé
faux : la ligne droite traverse en réalité ~20,5 km de terre ferme (l'île
d'Oléron elle-même, puis la presqu'île d'Arvert). Ce module existe pour que
cette vérification se fasse AVANT de construire une archive, pas après —
avec une source dense et faisant autorité plutôt qu'une poignée de points.

CE QUE CE MODULE FAIT : calcule les points échantillonnés le long de la
géodésique entre un poste et une cible (Vincenty, GRS80), et fournit les
fonctions d'analyse (détection des traversées de terre, verdict global) une
fois les élévations obtenues.

CE QUE CE MODULE NE PEUT PAS FAIRE SEUL DANS CETTE SESSION : interroger
lui-même l'API — le bac à sable réseau de cette session bloque tout hôte hors
des dépôts de paquets (testé : `curl`/`urllib` vers data.geopf.fr échouent
tous les deux avec une erreur de proxy 403). `interroger_ign_direct` est
fourni pour un usage HORS de cette session (poste de l'utilisateur, ou tout
environnement à accès réseau normal) ; DANS cette session, le point d'entrée
est `construire_urls_lots`, dont les URLs sont interrogées une par une via
l'outil WebFetch de Claude (séquentiellement — l'API rejette les appels
parallèles sur le même hôte, testé empiriquement), puis les élévations
obtenues sont passées à `analyser_profil`.

SOURCE : API REST d'altimétrie de la Géoplateforme IGN — RGE ALTI, donnée
souveraine officielle française (pas le SHOM lui-même, dont le visualiseur
cartographique interactif n'est pas restituable par les outils de
récupération web disponibles ici ; le RGE ALTI en est le meilleur substitut
atteignable, une autorité de même nature qu'un MNT officiel).
https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json
Le service renvoie environ -99999 pour tout point hors de sa couverture
terrestre, c'est-à-dire en mer — c'est ce sentinel qui sert de test « mer ».
"""

import math
import urllib.parse
import urllib.request

# --- Géodésie : importée du paquet, jamais recopiée ---
#
# `vincenty_inverse` et `vincenty_direct` vivaient ici en copie locale, hors de
# toute couverture de test. Elles sont maintenant dans `visee_optique.geodesy`,
# où vingt-six tests les éprouvent — dont deux qui les confrontent à des
# résultats obtenus sans Vincenty : la distance sur l'équateur, qui vaut
# analytiquement a·Δλ, et l'arc méridien, obtenu par quadrature.
#
# `vincenty_inverse` rend un GeodesiqueInverse (distance_m, azimut_depart_deg,
# azimut_arrivee_deg, iterations, converge) et non plus un triplet, et lève
# plutôt que de rendre le dernier itéré quand elle ne converge pas.
from visee_optique.geodesy import (  # noqa: E402
    GRS80_A,
    GRS80_F,
    vincenty_direct,
    vincenty_inverse,
)

A_GRS80 = GRS80_A
F_GRS80 = GRS80_F

SEUIL_TERRE_M = 0.0  # toute élévation > 0 m est du relief, donc invalidante
SENTINEL_MER_MAX = -1000.0  # en dessous : hors couverture, donc mer
RESOURCE_IGN = "ign_rge_alti_wld"
URL_BASE_IGN = "https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json"


def generer_points_echantillon(lat1, lon1, lat2, lon2, pas_m=1000.0, a=A_GRS80, f=F_GRS80):
    """Points (distance_m, lat_deg, lon_deg) tous les pas_m mètres le long de
    la géodésique de (lat1,lon1) vers (lat2,lon2), en incluant le point
    d'arrivée exact même s'il ne tombe pas rond. Tableau 10 (§12.3) demande un
    pas d'au plus 500 m pour un usage probatoire réel ; 1000 m est un
    pré-écran raisonnable, à affiner (voir raffiner_autour) si une transition
    terre/mer est repérée.
    """
    geo = vincenty_inverse(lat1, lon1, lat2, lon2, a, f)
    distance_totale, azimut = geo.distance_m, geo.azimut_depart_deg
    points = []
    d = 0.0
    while d < distance_totale:
        lat, lon = vincenty_direct(lat1, lon1, azimut, d, a, f)
        points.append((d, lat, lon))
        d += pas_m
    lat_f, lon_f = vincenty_direct(lat1, lon1, azimut, distance_totale, a, f)
    points.append((distance_totale, lat_f, lon_f))
    return points, distance_totale, azimut


def raffiner_autour(lat1, lon1, azimut, centre_m, demi_largeur_m=1000.0, pas_m=50.0, a=A_GRS80, f=F_GRS80):
    """Points supplémentaires à résolution fine autour d'une distance suspecte
    (typiquement une transition terre/mer repérée au pas grossier)."""
    points = []
    d = max(0.0, centre_m - demi_largeur_m)
    fin = centre_m + demi_largeur_m
    while d <= fin:
        lat, lon = vincenty_direct(lat1, lon1, azimut, d, a, f)
        points.append((d, lat, lon))
        d += pas_m
    return points


def construire_urls_lots(points, taille_lot=8):
    """Découpe `points` (liste de (distance,lat,lon)) en lots de taille_lot et
    renvoie une liste de (sous_liste_points, url) — une URL par lot, prête à
    être passée à WebFetch. INTERROGER LES LOTS UN PAR UN, PAS EN PARALLÈLE :
    l'API rejette (403, proxy) plusieurs requêtes simultanées vers le même
    hôte (constaté empiriquement lors de la vérification du cas Chassiron).
    """
    lots = []
    for i in range(0, len(points), taille_lot):
        sous = points[i:i + taille_lot]
        lons = "|".join(f"{lon:.5f}" for _, _, lon in sous)
        lats = "|".join(f"{lat:.5f}" for _, lat, _ in sous)
        params = {
            "lon": lons, "lat": lats, "resource": RESOURCE_IGN,
            "delimiter": "|", "indent": "false", "measures": "false", "zonly": "true",
        }
        url = URL_BASE_IGN + "?" + urllib.parse.urlencode(params, safe="|")
        lots.append((sous, url))
    return lots


def interroger_ign_direct(points, taille_lot=20, timeout=10):
    """Interroge l'API IGN directement en HTTP (urllib, bibliothèque standard)
    — NE FONCTIONNE PAS depuis cette session (réseau restreint, testé :
    échoue avec « Tunnel connection failed: 403 »). Fournie pour un usage
    HORS de cette session (poste de l'utilisateur ou tout environnement à
    accès réseau normal), où elle interroge l'API en une seule passe
    automatique. Retourne la liste de (distance, lat, lon, elevation_ou_None).
    """
    import json

    resultats = []
    for sous, url in construire_urls_lots(points, taille_lot=taille_lot):
        with urllib.request.urlopen(url, timeout=timeout) as reponse:
            data = json.loads(reponse.read().decode("utf-8"))
        for (d, lat, lon), elev in zip(sous, data["elevations"]):
            resultats.append((d, lat, lon, None if elev < SENTINEL_MER_MAX else elev))
    return resultats


def fusionner_avec_elevations(points, elevations_brutes):
    """Associe `points` (distance,lat,lon) à une liste plate d'élévations
    brutes dans le même ordre (telles que lues, une par une, dans les
    réponses JSON obtenues via WebFetch) — convertit le sentinel IGN
    (~-99999) en None (mer). Retourne une liste de (distance, lat, lon,
    elevation_ou_None).
    """
    if len(points) != len(elevations_brutes):
        raise ValueError(
            f"{len(points)} points mais {len(elevations_brutes)} élévations — "
            "vérifier qu'aucun lot n'a été omis ou dédoublé."
        )
    return [
        (d, lat, lon, None if elev < SENTINEL_MER_MAX else elev)
        for (d, lat, lon), elev in zip(points, elevations_brutes)
    ]


def detecter_traversees_terre(points_avec_elevation, seuil_m=SEUIL_TERRE_M):
    """Repère les segments contigus où l'élévation dépasse seuil_m (terre).
    Retourne une liste de dicts {debut_m, fin_m, longueur_m, elevation_max_m}.
    Un point isolé au-dessus du seuil compte déjà comme une traversée (même
    ponctuelle) — l'invalidation est automatique dès qu'UN point rencontre du
    relief, conformément à la consigne : pas de marge de tolérance implicite.
    """
    traversees = []
    en_cours = None
    for d, lat, lon, elev in points_avec_elevation:
        est_terre = elev is not None and elev > seuil_m
        if est_terre:
            if en_cours is None:
                en_cours = {"debut_m": d, "fin_m": d, "elevation_max_m": elev}
            else:
                en_cours["fin_m"] = d
                en_cours["elevation_max_m"] = max(en_cours["elevation_max_m"], elev)
        else:
            if en_cours is not None:
                en_cours["longueur_m"] = en_cours["fin_m"] - en_cours["debut_m"]
                traversees.append(en_cours)
                en_cours = None
    if en_cours is not None:
        en_cours["longueur_m"] = en_cours["fin_m"] - en_cours["debut_m"]
        traversees.append(en_cours)
    return traversees


def analyser_profil(points_avec_elevation, seuil_m=SEUIL_TERRE_M):
    """Verdict complet : traversées de terre détectées, longueur totale sur
    terre, statut 100% maritime ou non. Retourne un dict prêt à journaliser.
    ATTENTION : un pas d'échantillonnage grossier peut manquer une traversée
    étroite (îlot, banc émergé) — un verdict "100% maritime" à 1 km de pas
    est un indice favorable, pas une garantie ; affiner (raffiner_autour)
    partout où le terrain est composite (bras de mer, presqu'île, archipel)
    avant de bâtir une archive complète sur la foi de ce seul pré-écran.
    """
    traversees = detecter_traversees_terre(points_avec_elevation, seuil_m=seuil_m)
    distance_totale = points_avec_elevation[-1][0] if points_avec_elevation else 0.0
    longueur_terre = sum(t["longueur_m"] for t in traversees)
    return {
        "n_points": len(points_avec_elevation),
        "distance_totale_m": distance_totale,
        "traversees_terre": traversees,
        "longueur_totale_sur_terre_m": longueur_terre,
        "pourcentage_sur_terre": (100.0 * longueur_terre / distance_totale) if distance_totale else 0.0,
        "valide_100pc_maritime": len(traversees) == 0,
    }


if __name__ == "__main__":
    # Auto-test de non-régression : rejoue le relevé déjà obtenu manuellement
    # pour CAS-DEMO-CHASSIRON-001 (77 points, cas-chassiron/case_data.py,
    # PROFIL_ELEVATIONS_IGN) et vérifie que ce module retrouve bien les deux
    # traversées de terre identifiées à la main (île d'Oléron, presqu'île
    # d'Arvert), pour un total proche de 20,5 km.
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent
                           / "exemples-cas-etudes" / "cas-chassiron"))
    import case_data as cas_chassiron

    points_test = [
        (d, 0.0, 0.0, elev) for d, elev in cas_chassiron.PROFIL_ELEVATIONS_IGN
    ]
    resultat = analyser_profil(points_test)
    print(f"points : {resultat['n_points']}")
    print(f"traversées de terre détectées : {len(resultat['traversees_terre'])}")
    for t in resultat["traversees_terre"]:
        print(f"  {t['debut_m']/1000:.2f} – {t['fin_m']/1000:.2f} km "
              f"({t['longueur_m']/1000:.2f} km, max {t['elevation_max_m']:.2f} m)")
    print(f"longueur totale sur terre : {resultat['longueur_totale_sur_terre_m']/1000:.2f} km "
          f"({resultat['pourcentage_sur_terre']:.1f} %)")
    print(f"valide 100% maritime : {resultat['valide_100pc_maritime']}")
    assert len(resultat["traversees_terre"]) == 2, "régression : devrait retrouver 2 traversées"
    assert not resultat["valide_100pc_maritime"], "régression : ce cas est connu invalide"
    print("auto-test OK : le module retrouve bien le résultat déjà établi à la main pour Chassiron.")
