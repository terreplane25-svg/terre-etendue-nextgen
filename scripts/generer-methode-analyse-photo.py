#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Méthode d'essai : analyse a posteriori d'une photographie d'objet éloigné.

Ce que la méthode fait
──────────────────────
Elle sépare l'observation de son analyse. Phase 1, quelqu'un photographie un
objet lointain et conserve le fichier d'origine ; il n'a besoin de rien savoir,
à l'instant du déclenchement, de la distance, de la hauteur de la cible ou de
l'état de l'atmosphère. Phase 2, des semaines plus tard s'il le faut, on
reconstitue chacun de ces paramètres à partir de sources indépendantes de la
photographie, on prédit la portion masquée, on mesure la portion visible, et on
compare.

La règle qui structure tout le document
───────────────────────────────────────
Aucun paramètre ne se lit dans l'image qu'on cherche à juger. La hauteur d'une
montagne vient des données topographiques, celle d'un navire de ses
spécifications et de sa position horodatée, celle d'un phare de sa fiche
officielle. Ajuster après coup une hauteur ou une distance pour que le calcul
retombe sur l'image, c'est écrire la réponse dans l'énoncé.

Pourquoi une classe pour chaque donnée
──────────────────────────────────────
La sensibilité n'est pas répartie également. Sur le cas de référence — œil à
12 m, cible à 42 km — un mètre d'erreur sur la hauteur d'œil déplace la
prédiction de 2,2 m, cent mètres d'erreur sur la distance de 0,4 m, et un
centième sur le coefficient de réfraction de 0,9 m. Or c'est justement le
coefficient qu'on ne peut pas mesurer a posteriori. Une plage plausible de
0,05 à 0,30 vaut à elle seule ±12 m d'incertitude, soit davantage que toutes
les autres réunies. D'où la classification des données atmosphériques, et
l'interdiction de présenter une estimation comme une mesure.

Ce qui fait déclarer « non concluante »
───────────────────────────────────────
Un critère quantitatif plutôt qu'une liste d'humeurs : quand l'incertitude
propagée sur la prédiction dépasse le tiers de l'écart qu'on prétend constater,
la photographie ne tranche rien. S'y ajoutent quatre disqualifications
matérielles, énoncées en section 11.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from methode_essai import (PROTOCOLES, clause, ecrire, encadre, h2, h2_annexe,
                           masthead, nb)

NUM4 = (1, 2, 3)   # colonnes numériques du tableau 4

CIBLE = os.path.join(PROTOCOLES, "analyse-photo-bilingue.html")

R = 6371000.0

# Cas de référence, utilisé pour la table de sensibilité de la section 9.
H_REF, D_REF, HT_REF = 12.0, 42.0, 60.0     # m, km, m
K_REF = 0.13
K_PLAGE = (0.05, 0.30)                       # plage plausible sans mesure

# Résolution : capteur 1 pouce, pas de 4,4 µm ; focale 600 mm équivalent.
PAS_PIXEL = 4.4e-6
FOCALE = 0.600
PUPILLE = 0.067                              # m — 600 mm à f/9


def cachee(h, d_km, k):
    """Hauteur masquée à la base de la cible, en mètres."""
    if k >= 1:
        return 0.0
    rp = R / (1 - k)
    d = d_km * 1000.0
    a = math.sqrt((rp + h) ** 2 - rp ** 2)
    return 0.0 if d <= a else math.sqrt(rp ** 2 + (d - a) ** 2) - rp


def k_exige(h, d_km, c_obs):
    """Coefficient qu'il faudrait pour que la hauteur masquée vaille c_obs."""
    lo, hi = 0.0, 0.999999
    for _ in range(400):
        m = (lo + hi) / 2
        if cachee(h, d_km, m) > c_obs:
            lo = m
        else:
            hi = m
    return hi


def k_gradient(p_hpa, t_k, dtdz):
    """Coefficient de réfraction déduit d'un gradient thermique, en K/m."""
    return 503.0 * (p_hpa / t_k ** 2) * (0.0342 + dtdz)


def sensibilites():
    """Dérivées partielles de c au cas de référence, par différences centrées."""
    base = cachee(H_REF, D_REF, K_REF)
    dh = (cachee(H_REF + 0.5, D_REF, K_REF)
          - cachee(H_REF - 0.5, D_REF, K_REF))            # par mètre
    dd = (cachee(H_REF, D_REF + 0.05, K_REF)
          - cachee(H_REF, D_REF - 0.05, K_REF)) * 10      # par km
    dk = (cachee(H_REF, D_REF, K_REF + 0.005)
          - cachee(H_REF, D_REF, K_REF - 0.005))          # par 0,01
    return base, dh, dd, dk


def budget():
    """Incertitude propagée sur la prédiction, cas de référence.

    Les composantes retenues sont celles d'un dossier bien documenté : hauteur
    d'œil au mètre, distance à cent mètres, coefficient laissé à sa plage
    plausible faute de mesure.
    """
    _, dh, dd, dk = sensibilites()
    u_h = abs(dh) * 1.0
    u_d = abs(dd) * 0.1
    demi = (K_PLAGE[1] - K_PLAGE[0]) / 2
    u_k = abs(dk) * (demi / 0.01)
    return u_h, u_d, u_k, math.sqrt(u_h ** 2 + u_d ** 2 + u_k ** 2)


def resolution():
    """Échelle au sol et limites optiques, au cas de référence."""
    theta_px = PAS_PIXEL / FOCALE                     # rad
    sol = theta_px * D_REF * 1000.0                   # m par pixel
    diffr = 1.22 * 550e-9 / PUPILLE                   # rad
    return theta_px * 206265, sol, diffr * 206265


def controle():
    """Recalcule chaque valeur imprimée. Rien n'est écrit en dur dans le texte."""
    base, dh, dd, dk = sensibilites()
    assert abs(base - 56.4) < 0.15, base
    assert abs(dh + 2.169) < 0.02, dh
    assert abs(dd - 3.925) < 0.02, dd
    assert abs(dk + 0.947) < 0.02, dk
    # Le coefficient domine le budget : c'est ce qui justifie la section 8.3.
    u_h, u_d, u_k, u = budget()
    assert u_k > u_h + u_d, (u_h, u_d, u_k)
    assert abs(u_k - 11.84) < 0.1, u_k
    # La formule du gradient et ses deux points d'ancrage.
    assert abs(k_gradient(1013.0, 288.0, -0.0130) - 0.13) < 0.005
    assert abs(k_gradient(1013.0, 288.0, +0.1286) - 1.0) < 0.01
    # Le coefficient exigé croît avec la portion visible réclamée.
    suite = [k_exige(H_REF, D_REF, c) for c in (50, 40, 30, 20)]
    assert suite == sorted(suite), suite
    assert all(x < 1.0 for x in suite), suite
    # Aucune configuration n'interdit de voir : k tend vers 1, c tend vers 0.
    assert cachee(H_REF, 400.0, 0.999) < 1.0
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Les quinze déterminations de la phase 2. Chaque entrée : ce qu'il faut
# établir, la source indépendante admise, la précision visée.
# ─────────────────────────────────────────────────────────────────────────────
DETERMINATIONS = [
    ("Identit&#233; exacte de la cible",
     "Exact identity of the target",
     "recoupement carte, liste officielle de feux, registre AIS horodat&#233;, "
     "cadastre &#233;olien&#160;; jamais la seule ressemblance visuelle",
     "cross-check against maps, official light lists, timestamped AIS records, "
     "wind-farm registers; never visual resemblance alone",
     "sans ambigu&#239;t&#233;", "unambiguous"),
    ("Coordonn&#233;es g&#233;ographiques de la cible",
     "Geographic coordinates of the target",
     "relev&#233; g&#233;od&#233;sique, fiche officielle de l'ouvrage, position "
     "AIS &#224; l'heure du clich&#233;",
     "geodetic survey, the structure's official record, AIS position at the "
     "time of the frame",
     "&#177;&#8239;10&#8239;m", "&#177;&#8239;10&#8239;m"),
    ("Distance observateur&#8211;cible",
     "Observer-to-target distance",
     "calcul g&#233;od&#233;sique sur l'ellipso&#239;de &#224; partir des deux "
     "positions, et non une r&#232;gle sur une carte",
     "geodesic computation on the ellipsoid from the two positions, not a "
     "ruler on a map",
     "&#177;&#8239;100&#8239;m", "&#177;&#8239;100&#8239;m"),
    ("Altitude de l'observateur au moment du clich&#233;",
     "Observer altitude at the moment of the frame",
     "mod&#232;le num&#233;rique de terrain au point GNSS, plus la hauteur "
     "d'&#339;il au-dessus du sol&#160;; en mer, le niveau d'eau &#224; "
     "l'heure exacte",
     "digital terrain model at the GNSS point, plus eye height above ground; "
     "at sea, the water level at the exact time",
     "&#177;&#8239;1&#8239;m", "&#177;&#8239;1&#8239;m"),
    ("Altitude de la base de la cible",
     "Altitude of the target's base",
     "mod&#232;le num&#233;rique de terrain, ou niveau de la mer corrig&#233; "
     "de la mar&#233;e pour un ouvrage c&#244;tier",
     "digital terrain model, or sea level corrected for tide for a coastal "
     "structure",
     "&#177;&#8239;1&#8239;m", "&#177;&#8239;1&#8239;m"),
    ("Altitude et hauteur des parties pertinentes",
     "Altitude and height of the relevant parts",
     "plan cot&#233;, fiche technique, sp&#233;cifications du constructeur "
     "pour chaque &#233;l&#233;ment servant de rep&#232;re",
     "dimensioned drawing, data sheet, manufacturer's specification for every "
     "element used as a marker",
     "&#177;&#8239;0,5&#8239;m", "&#177;&#8239;0.5&#8239;m"),
    ("Hauteur totale de la cible",
     "Total height of the target",
     "m&#234;me source que la pr&#233;c&#233;dente, en distinguant hauteur "
     "au-dessus de la base et altitude du sommet",
     "same source as the previous item, distinguishing height above base from "
     "summit elevation",
     "&#177;&#8239;0,5&#8239;m", "&#177;&#8239;0.5&#8239;m"),
    ("G&#233;om&#233;trie de la ligne de vis&#233;e",
     "Geometry of the line of sight",
     "azimut g&#233;od&#233;sique et profil altim&#233;trique &#233;chantillonn"
     "&#233; au moins tous les 500&#8239;m entre les deux points",
     "geodesic azimuth and an elevation profile sampled at least every "
     "500&#8239;m between the two points",
     "profil complet", "complete profile"),
    ("Topographie ou bathym&#233;trie interm&#233;diaire",
     "Intervening topography or bathymetry",
     "mod&#232;le de terrain pour la partie terrestre, carte marine et "
     "hauteur d'eau pour la partie maritime",
     "terrain model for the land portion, nautical chart and water level for "
     "the sea portion",
     "&#177;&#8239;2&#8239;m", "&#177;&#8239;2&#8239;m"),
    ("Conditions m&#233;t&#233;orologiques au lieu et &#224; l'heure",
     "Meteorological conditions at the place and time",
     "observation de station la plus proche &#224; l'heure la plus proche, "
     "avec la distance et l'&#233;cart horaire consign&#233;s",
     "the nearest station's observation at the nearest hour, with distance "
     "and time offset recorded",
     "classe d&#233;clar&#233;e (8.3)", "declared class (8.3)"),
    ("Donn&#233;es n&#233;cessaires &#224; l'estimation de la r&#233;fraction",
     "Data required to estimate refraction",
     "profil vertical de temp&#233;rature, pression et humidit&#233; sur les "
     "premi&#232;res centaines de m&#232;tres&#160;; &#224; d&#233;faut, "
     "temp&#233;rature de l'air et de l'eau",
     "vertical profile of temperature, pressure and humidity over the first "
     "few hundred metres; failing that, air and water temperature",
     "classe d&#233;clar&#233;e (8.3)", "declared class (8.3)"),
    ("Caract&#233;ristiques optiques du syst&#232;me",
     "Optical characteristics of the system",
     "mod&#232;le de bo&#238;tier et d'objectif, focale r&#233;elle, ouverture, "
     "dimensions et pas du capteur, d'apr&#232;s les m&#233;tadonn&#233;es et "
     "la documentation du constructeur",
     "camera and lens model, actual focal length, aperture, sensor dimensions "
     "and pixel pitch, from the metadata and the manufacturer's documentation",
     "focale &#224; &#177;&#8239;2&#8239;%", "focal length to &#177;&#8239;2&#8239;%"),
    ("Champ couvert pour cette focale et ce capteur",
     "Field of view for that focal length and sensor",
     "calcul&#233; en 9.2, puis v&#233;rifi&#233; sur deux rep&#232;res de "
     "position connue pr&#233;sents dans le m&#234;me clich&#233;",
     "computed in 9.2, then checked against two landmarks of known position "
     "present in the same frame",
     "&#233;cart &lt;&#8239;2&#8239;%", "discrepancy &lt;&#8239;2&#8239;%"),
    ("R&#233;solution angulaire effective",
     "Effective angular resolution",
     "la plus grande des trois&#160;: pas de pixel projet&#233;, limite de "
     "diffraction, largeur mesur&#233;e d'un bord franc dans l'image",
     "the largest of three: projected pixel pitch, diffraction limit, measured "
     "width of a sharp edge in the image",
     "en secondes d'arc", "in arcseconds"),
    ("Corrections li&#233;es &#224; l'objectif",
     "Corrections tied to the lens",
     "distorsion, courbure de champ et d&#233;centrement, d'apr&#232;s le "
     "profil d'&#233;talonnage du couple bo&#238;tier-objectif",
     "distortion, field curvature and decentring, from the calibration profile "
     "of the camera-lens pair",
     "r&#233;siduel &lt;&#8239;1 pixel", "residual &lt;&#8239;1 pixel"),
]

# Les classes de donnée atmosphérique. L'ordre est celui de la force probante.
CLASSES = [
    ("A", "Mesure directe sur site", "Direct on-site measurement",
     "instrument relev&#233; par l'observateur au point de vue, pendant "
     "l'observation", "instrument read by the observer at the viewpoint, "
     "during the observation", "mesure", "measurement"),
    ("B", "Station officielle ou sondage a&#233;rologique",
     "Official station or radiosonde",
     "observation horodat&#233;e d'un r&#233;seau reconnu, &#224; moins de "
     "30&#8239;km et 1&#8239;h du clich&#233;&#160;; le d&#233;calage est "
     "consign&#233; et report&#233; dans l'incertitude",
     "timestamped observation from a recognised network, within 30&#8239;km "
     "and 1&#8239;h of the frame; the offset is recorded and carried into the "
     "uncertainty", "mesure d&#233;port&#233;e", "displaced measurement"),
    ("C", "Sortie de mod&#232;le ou climatologie",
     "Model output or climatology",
     "r&#233;analyse, pr&#233;vision, moyenne mensuelle&#160;: une valeur "
     "calcul&#233;e, jamais observ&#233;e en ce point",
     "reanalysis, forecast, monthly mean: a computed value, never observed at "
     "that point", "valeur calcul&#233;e", "computed value"),
    ("D", "Estimation a posteriori", "A posteriori estimate",
     "valeur choisie par l'analyste faute de mieux, y compris le coefficient "
     "de r&#233;fraction &#171;&#160;standard&#160;&#187;",
     "a value chosen by the analyst for want of better, including the "
     "&#8220;standard&#8221; refraction coefficient",
     "d&#233;clarative", "declarative"),
]

# La chaîne de traçabilité du rapport. Chaque maillon porte sa source.
CHAINE = [
    ("Photographie brute", "Raw photograph"),
    ("M&#233;tadonn&#233;es de l'appareil", "Camera metadata"),
    ("Position de l'observateur", "Observer position"),
    ("Identification de la cible", "Target identification"),
    ("Position de la cible", "Target position"),
    ("Distance", "Distance"),
    ("Altitude de l'observateur", "Observer altitude"),
    ("Altitude et dimensions de la cible", "Target altitude and dimensions"),
    ("Donn&#233;es topographiques", "Topographic data"),
    ("Donn&#233;es m&#233;t&#233;orologiques", "Meteorological data"),
    ("Mod&#232;le de r&#233;fraction retenu", "Refraction model used"),
    ("Calcul g&#233;om&#233;trique", "Geometric computation"),
    ("Pr&#233;diction th&#233;orique", "Theoretical prediction"),
    ("Mesure de la partie visible", "Measurement of the visible part"),
    ("Comparaison observation&#8211;pr&#233;diction",
     "Observation-versus-prediction comparison"),
    ("Conclusion", "Conclusion"),
]

REFERENCES = [
    ("CIPA DC-008-2019 / JEITA CP-3451E, <em>Exchangeable image file format "
     "for digital still cameras&#160;: Exif Version 2.32</em>.",
     "CIPA DC-008-2019 / JEITA CP-3451E, <em>Exchangeable image file format "
     "for digital still cameras: Exif Version 2.32</em>."),
    ("JCGM 100:2008, <em>&#201;valuation des donn&#233;es de mesure &#8212; "
     "Guide pour l'expression de l'incertitude de mesure</em>.",
     "JCGM 100:2008, <em>Evaluation of measurement data &#8212; Guide to the "
     "expression of uncertainty in measurement</em>."),
    ("IGN, <em>RGE ALTI</em>, mod&#232;le num&#233;rique de terrain, pas de "
     "1&#8239;m&#160;; Copernicus, <em>DEM GLO-30</em>, pas de 30&#8239;m.",
     "IGN, <em>RGE ALTI</em>, digital terrain model, 1&#8239;m grid; "
     "Copernicus, <em>DEM GLO-30</em>, 30&#8239;m grid."),
    ("SHOM, cartes marines et <em>Annuaire des mar&#233;es</em>, &#233;dition "
     "de l'ann&#233;e de l'observation.",
     "SHOM, nautical charts and <em>Tide tables</em>, edition of the year of "
     "the observation."),
    ("OACI, Annexe 3, <em>Assistance m&#233;t&#233;orologique &#224; la "
     "navigation a&#233;rienne internationale</em> &#8212; format METAR.",
     "ICAO, Annex 3, <em>Meteorological Service for International Air "
     "Navigation</em> &#8212; METAR format."),
    ("UIT-R M.1371, <em>Caract&#233;ristiques techniques d'un syst&#232;me "
     "d'identification automatique</em> (AIS).",
     "ITU-R M.1371, <em>Technical characteristics for an automatic "
     "identification system</em> (AIS)."),
    ("C. Hirt, S. Guillaume, A. Wisbar, B. B&#252;rki, H. Sterling (2010), "
     "&#171;&#160;Monitoring of the refraction coefficient in the lower "
     "atmosphere&#160;&#187;, <em>Journal of Geophysical Research</em> 115, "
     "D21102.",
     "C. Hirt, S. Guillaume, A. Wisbar, B. B&#252;rki, H. Sterling (2010), "
     "&#8220;Monitoring of the refraction coefficient in the lower "
     "atmosphere&#8221;, <em>Journal of Geophysical Research</em> 115, D21102."),
    ("B. R. Bean, E. J. Dutton, <em>Radio Meteorology</em>, NBS Monograph 92, "
     "1966 &#8212; r&#233;fractivit&#233; et conduits.",
     "B. R. Bean, E. J. Dutton, <em>Radio Meteorology</em>, NBS Monograph 92, "
     "1966 &#8212; refractivity and ducting."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Tableaux de prose. Le `tableau()` partagé aligne toutes les cellules à droite
# en police mono : c'est ce qu'il faut pour des colonnes de nombres, et c'est
# illisible pour des colonnes de texte. Ces deux fonctions rendent la même
# structure en laissant la prose à gauche, et n'appliquent la mise en forme
# numérique qu'aux colonnes désignées.
# ─────────────────────────────────────────────────────────────────────────────
def tab(legende, entetes, lignes, num=()):
    th = "".join('<th%s>%s</th>' % (' class="n"' if i in num else "", e)
                 for i, e in enumerate(entetes))
    return ("<table>\n  <caption>%s</caption>\n  <thead><tr>%s</tr></thead>\n"
            "  <tbody>\n%s\n  </tbody>\n</table>" % (legende, th,
                                                      "\n".join(lignes)))


def rang(cellules, num=(), vedette=False):
    tds = "".join('<td%s>%s</td>' % (' class="n"' if i in num else "", c)
                  for i, c in enumerate(cellules))
    return '    <tr%s>%s</tr>' % (' class="hi"' if vedette else "", tds)

# ─────────────────────────────────────────────────────────────────────────────
# Corps du document
# ─────────────────────────────────────────────────────────────────────────────
def bloc_1(fr):
    """Domaine d'application."""
    if fr:
        return "\n".join([
            h2(1, fr),
            clause("1.1", "La pr&#233;sente m&#233;thode couvre l'analyse a "
                   "posteriori d'une photographie d'un objet &#233;loign&#233;. "
                   "Elle d&#233;termine si la portion de cet objet visible sur "
                   "l'image est compatible avec une surface de rayon "
                   "6&#8239;371&#8239;km, et sinon, quel coefficient de "
                   "r&#233;fraction il faudrait pour l'expliquer."),
            clause("1.2", "La m&#233;thode se d&#233;roule en deux phases. La "
                   "<strong>phase 1</strong> est l'acquisition&#160;: quelqu'un "
                   "photographie et conserve. La <strong>phase 2</strong> est "
                   "l'analyse&#160;: on reconstitue les param&#232;tres et on "
                   "calcule. Les deux phases peuvent &#234;tre s&#233;par&#233;es "
                   "de plusieurs semaines et conduites par des personnes "
                   "diff&#233;rentes."),
            clause("1.3", "&#192; l'instant du d&#233;clenchement, "
                   "l'op&#233;rateur n'a besoin de conna&#238;tre ni la "
                   "distance, ni la hauteur de la cible, ni la courbure "
                   "attendue, ni l'&#233;tat de l'atmosph&#232;re. Son objectif "
                   "est de pr&#233;server une observation authentique et "
                   "exploitable."),
            clause("1.4", "La m&#233;thode s'applique &#233;galement &#224; une "
                   "photographie prise sans aucune intention "
                   "exp&#233;rimentale, sous r&#233;serve des conditions "
                   "d'admissibilit&#233; de la section&#160;7."),
            clause("1.5", "La m&#233;thode ne s'applique pas &#224; une image "
                   "dont le fichier d'origine est indisponible, ni &#224; une "
                   "image recadr&#233;e, redimensionn&#233;e ou "
                   "r&#233;&#233;chantillonn&#233;e sans que l'original puisse "
                   "&#234;tre produit."),
            clause("1.6", "Les valeurs sont exprim&#233;es en unit&#233;s SI. "
                   "Les angles sont en degr&#233;s d&#233;cimaux ou en secondes "
                   "d'arc, l'unit&#233; &#233;tant indiqu&#233;e &#224; chaque "
                   "occurrence."),
            clause("1.7", "La phase 1 peut conduire &#224; op&#233;rer en bord "
                   "de falaise, sur un ouvrage ou de nuit. La m&#233;thode "
                   "n'autorise aucun acc&#232;s&#160;; il appartient &#224; "
                   "l'op&#233;rateur d'&#233;tablir les conditions de "
                   "s&#233;curit&#233; et les autorisations applicables."),
        ])
    return "\n".join([
        h2(1, fr),
        clause("1.1", "This method covers the a posteriori analysis of a "
               "photograph of a distant object. It determines whether the "
               "portion of that object visible in the image is compatible with "
               "a surface of radius 6&#8239;371&#8239;km, and if not, what "
               "refraction coefficient would be required to account for it."),
        clause("1.2", "The method proceeds in two phases. <strong>Phase 1</strong> "
               "is acquisition: someone photographs and preserves. "
               "<strong>Phase 2</strong> is analysis: the parameters are "
               "reconstructed and the computation is made. The two phases may "
               "be weeks apart and carried out by different people."),
        clause("1.3", "At the moment of the frame, the operator needs to know "
               "neither the distance, nor the target's height, nor the expected "
               "curvature, nor the state of the atmosphere. The objective is to "
               "preserve an authentic and usable observation."),
        clause("1.4", "The method also applies to a photograph taken with no "
               "experimental intent whatsoever, subject to the admissibility "
               "conditions of section&#160;7."),
        clause("1.5", "The method does not apply to an image whose original "
               "file is unavailable, nor to an image cropped, resized or "
               "resampled without the original being producible."),
        clause("1.6", "Values are expressed in SI units. Angles are in decimal "
               "degrees or arcseconds, the unit being stated at each occurrence."),
        clause("1.7", "Phase 1 may involve working at a cliff edge, on a "
               "structure, or at night. The method grants no right of access; "
               "establishing the applicable safety conditions and permissions "
               "is the operator's responsibility."),
    ])


def bloc_2(fr):
    items = "\n".join("  <li>%s</li>" % r[0 if fr else 1] for r in REFERENCES)
    return "%s\n<ol class=\"refs\">\n%s\n</ol>" % (h2(2, fr), items)


def bloc_3(fr):
    """Terminologie."""
    if fr:
        defs = [
            ("cible", "l'objet &#233;loign&#233; dont la portion visible est "
             "mesur&#233;e. Un phare, une &#233;olienne, un immeuble, un "
             "navire, un relief."),
            ("partie pertinente", "un &#233;l&#233;ment de la cible dont "
             "l'altitude et la hauteur sont connues ind&#233;pendamment, et qui "
             "sert de rep&#232;re m&#233;trique dans l'image."),
            ("hauteur masqu&#233;e, <em>c</em>", "la hauteur, compt&#233;e "
             "depuis la base de la cible, qu'une surface de rayon "
             "6&#8239;371&#8239;km soustrait &#224; la vue pour une hauteur "
             "d'&#339;il et une distance donn&#233;es. Elle ne d&#233;pend pas "
             "de la hauteur de la cible&#160;: celle-ci n'est que le terme de "
             "comparaison."),
            ("coefficient de r&#233;fraction, <em>k</em>", "rapport entre la "
             "courbure du rayon lumineux et celle de la surface. "
             "<em>k</em>&#160;=&#160;0 pour un rayon droit&#160;; "
             "<em>k</em>&#160;=&#160;1 pour un rayon qui &#233;pouse la "
             "surface."),
            ("coefficient exig&#233;, <em>k</em><sub>ex</sub>", "le coefficient "
             "qu'il faudrait pour que la hauteur masqu&#233;e calcul&#233;e "
             "&#233;gale la hauteur masqu&#233;e mesur&#233;e sur l'image. "
             "C'est le r&#233;sultat principal de la m&#233;thode."),
            ("source ind&#233;pendante", "une source qui existait avant "
             "l'analyse et qui ne d&#233;rive pas de la photographie "
             "examin&#233;e. Une hauteur lue dans l'image n'est pas une source "
             "ind&#233;pendante."),
            ("classe de donn&#233;e", "l'&#233;tiquette A &#224; D d&#233;finie "
             "en 8.3, qui dit comment une valeur a &#233;t&#233; obtenue et non "
             "si elle est juste."),
            ("non concluante", "le verdict rendu lorsque les donn&#233;es "
             "disponibles ne permettent pas de distinguer la compatibilit&#233; "
             "de l'incompatibilit&#233;. Les crit&#232;res sont &#233;nonc&#233;s "
             "en section&#160;11."),
            ("cha&#238;ne de tra&#231;abilit&#233;", "la suite ordonn&#233;e "
             "des &#233;l&#233;ments de la section&#160;10, chacun "
             "accompagn&#233; de sa source, de sa pr&#233;cision et de son "
             "incertitude."),
            ("conduit", "couche atmosph&#233;rique dans laquelle la "
             "r&#233;fractivit&#233; modifi&#233;e d&#233;cro&#238;t avec "
             "l'altitude, et qui peut guider un rayon le long de la surface."),
        ]
    else:
        defs = [
            ("target", "the distant object whose visible portion is measured. "
             "A lighthouse, a wind turbine, a building, a ship, a landform."),
            ("relevant part", "an element of the target whose elevation and "
             "height are independently known, used as a metric marker in the "
             "image."),
            ("hidden height, <em>c</em>", "the height, counted from the "
             "target's base, that a surface of radius 6&#8239;371&#8239;km "
             "withholds from view for a given eye height and distance. It does "
             "not depend on the target's height; that height is only the term "
             "of comparison."),
            ("refraction coefficient, <em>k</em>", "the ratio of the light "
             "ray's curvature to the surface's. <em>k</em>&#160;=&#160;0 for a "
             "straight ray; <em>k</em>&#160;=&#160;1 for a ray that follows the "
             "surface."),
            ("required coefficient, <em>k</em><sub>req</sub>", "the coefficient "
             "that would make the computed hidden height equal the hidden "
             "height measured on the image. It is the method's principal "
             "result."),
            ("independent source", "a source that existed before the analysis "
             "and does not derive from the photograph under examination. A "
             "height read off the image is not an independent source."),
            ("data class", "the label A to D defined in 8.3, which states how a "
             "value was obtained, not whether it is correct."),
            ("inconclusive", "the verdict returned when the available data "
             "cannot distinguish compatibility from incompatibility. The "
             "criteria are stated in section&#160;11."),
            ("traceability chain", "the ordered sequence of elements of "
             "section&#160;10, each accompanied by its source, its precision "
             "and its uncertainty."),
            ("duct", "an atmospheric layer in which modified refractivity "
             "decreases with height, capable of guiding a ray along the "
             "surface."),
        ]
    lignes = "\n".join("  <li><strong>%s</strong> &#8212; %s</li>" % d for d in defs)
    return "%s\n<ul>\n%s\n</ul>" % (h2(3, fr), lignes)


def bloc_4(fr):
    """Résumé de la méthode."""
    if fr:
        etapes = [
            ("Acquisition", "un op&#233;rateur photographie un objet "
             "&#233;loign&#233; en format brut, sur support stable, et "
             "conserve le fichier d'origine avec l'ensemble de ses "
             "m&#233;tadonn&#233;es."),
            ("Recevabilit&#233;", "l'analyste v&#233;rifie que la "
             "photographie satisfait les six conditions de la section&#160;7. "
             "Sinon, la proc&#233;dure s'arr&#234;te ici."),
            ("Reconstitution", "les quinze param&#232;tres de la "
             "section&#160;8.2 sont &#233;tablis un &#224; un &#224; partir de "
             "sources ind&#233;pendantes de la photographie."),
            ("Pr&#233;diction", "la hauteur masqu&#233;e est calcul&#233;e pour "
             "le coefficient de r&#233;fraction retenu, avec son incertitude "
             "propag&#233;e."),
            ("Mesure", "la hauteur masqu&#233;e r&#233;ellement "
             "observ&#233;e est mesur&#233;e dans l'image, &#224; l'aide des "
             "parties pertinentes servant d'&#233;chelle."),
            ("Comparaison", "les deux valeurs sont compar&#233;es. Le rapport "
             "&#233;nonce l'un des trois verdicts de 9.6 et, en cas d'&#233;cart, "
             "le coefficient exig&#233;."),
        ]
    else:
        etapes = [
            ("Acquisition", "an operator photographs a distant object in raw "
             "format on a stable support, and preserves the original file with "
             "all its metadata."),
            ("Admissibility", "the analyst checks that the photograph meets the "
             "six conditions of section&#160;7. Otherwise the procedure stops "
             "here."),
            ("Reconstruction", "the fifteen parameters of section&#160;8.2 are "
             "established one by one from sources independent of the "
             "photograph."),
            ("Prediction", "the hidden height is computed for the adopted "
             "refraction coefficient, with its propagated uncertainty."),
            ("Measurement", "the hidden height actually observed is measured in "
             "the image, using the relevant parts as a scale."),
            ("Comparison", "the two values are compared. The report states one "
             "of the three verdicts of 9.6 and, where they differ, the required "
             "coefficient."),
        ]
    lignes = "\n".join("  <li><b>%s</b>%s</li>" % e for e in etapes)
    return "%s\n<ol class=\"st\">\n%s\n</ol>" % (h2(4, fr), lignes)


def bloc_5(fr):
    """Intérêt et emploi."""
    if fr:
        return "\n".join([
            h2(5, fr),
            clause("5.1", "Une photographie est une donn&#233;e historique. "
                   "Elle a &#233;t&#233; prise une fois, dans un &#233;tat de "
                   "l'atmosph&#232;re qui ne se reproduira pas, et elle ne peut "
                   "&#234;tre refaite. La m&#233;thode existe pour tirer d'un "
                   "tel document tout ce qu'il contient, sans lui faire dire "
                   "davantage."),
            clause("5.2", "La conclusion vaut ce que vaut le maillon le plus "
                   "faible de la cha&#238;ne de la section&#160;10. Une "
                   "distance au m&#232;tre pr&#232;s ne rachète pas une hauteur "
                   "de cible inconnue, et un mat&#233;riel de haut de gamme ne "
                   "rachète pas une position d'observateur approximative."),
            clause("5.3", "La m&#233;thode rend l'un de trois verdicts&#160;: "
                   "compatible, incompatible, non concluante. Le troisi&#232;me "
                   "n'est pas un &#233;chec de la m&#233;thode&#160;: c'est ce "
                   "qu'elle doit rendre chaque fois que les donn&#233;es ne "
                   "tranchent pas."),
            clause("5.4", "La m&#233;thode est utilisable par une personne "
                   "distincte de l'op&#233;rateur, sur un dossier "
                   "re&#231;u&#160;; c'est m&#234;me le cas normal. Rien dans "
                   "la phase 2 ne suppose d'avoir &#233;t&#233; sur place."),
        ])
    return "\n".join([
        h2(5, fr),
        clause("5.1", "A photograph is a historical datum. It was taken once, "
               "in a state of the atmosphere that will not recur, and it cannot "
               "be retaken. The method exists to extract everything such a "
               "document contains, without making it say more."),
        clause("5.2", "The conclusion is worth what the weakest link of the "
               "chain in section&#160;10 is worth. A distance known to the "
               "metre does not redeem an unknown target height, and high-end "
               "equipment does not redeem an approximate observer position."),
        clause("5.3", "The method returns one of three verdicts: compatible, "
               "incompatible, inconclusive. The third is not a failure of the "
               "method: it is what the method must return whenever the data do "
               "not decide."),
        clause("5.4", "The method may be applied by someone other than the "
               "operator, working from a submitted file; that is in fact the "
               "normal case. Nothing in phase 2 presupposes having been on "
               "site."),
    ])


def bloc_6(fr):
    """Appareillage."""
    if fr:
        return "\n".join([
            h2(6, fr),
            "<h3>6.1 Phase 1 &#8212; acquisition</h3>",
            clause("6.1.1", "Appareil enregistrant en format brut, focale "
                   "&#233;quivalente 24&#215;36 d'au moins 400&#8239;mm, "
                   "horloge interne r&#233;gl&#233;e sur le temps universel "
                   "&#224; mieux que 5&#8239;s."),
            clause("6.1.2", "Support stable&#160;: tr&#233;pied ou appui fixe. "
                   "Le d&#233;clenchement se fait par retardateur ou "
                   "commande &#224; distance."),
            clause("6.1.3", "R&#233;cepteur GNSS, celui de l'appareil ou d'un "
                   "t&#233;l&#233;phone, avec enregistrement de la position et "
                   "de son incertitude annonc&#233;e."),
            clause("6.1.4", "M&#232;tre ruban pour relever la hauteur de l'axe "
                   "de l'objectif au-dessus du sol ou du plan d'eau."),
            "<h3>6.2 Phase 2 &#8212; analyse</h3>",
            clause("6.2.1", "La phase 2 ne demande aucun appareil. Elle demande "
                   "l'acc&#232;s aux sources de donn&#233;es &#233;num&#233;"
                   "r&#233;es en 8.2 et un lecteur de m&#233;tadonn&#233;es qui "
                   "n'&#233;crit pas dans le fichier."),
            clause("6.2.2", "Le fichier d'origine n'est jamais ouvert en "
                   "&#233;criture. L'empreinte SHA-256 de l'original est "
                   "calcul&#233;e avant toute manipulation et report&#233;e au "
                   "rapport&#160;; toutes les op&#233;rations se font sur une "
                   "copie."),
            clause("6.2.3", "L'outil de mesure sur l'image doit conserver les "
                   "coordonn&#233;es en pixels de l'image d'origine. Un "
                   "recadrage, une correction de perspective ou un "
                   "r&#233;&#233;chantillonnage appliqu&#233;s avant mesure "
                   "invalident l'&#233;chelle &#233;tablie en 9.2."),
        ])
    return "\n".join([
        h2(6, fr),
        "<h3>6.1 Phase 1 &#8212; acquisition</h3>",
        clause("6.1.1", "A camera recording in raw format, 35&#8239;mm-equivalent "
               "focal length of at least 400&#8239;mm, internal clock set to "
               "universal time to better than 5&#8239;s."),
        clause("6.1.2", "A stable support: tripod or fixed rest. The shutter is "
               "released by self-timer or remote control."),
        clause("6.1.3", "A GNSS receiver, the camera's or a phone's, recording "
               "the position and its stated uncertainty."),
        clause("6.1.4", "A tape measure to record the height of the lens axis "
               "above the ground or the water surface."),
        "<h3>6.2 Phase 2 &#8212; analysis</h3>",
        clause("6.2.1", "Phase 2 requires no apparatus. It requires access to "
               "the data sources listed in 8.2 and a metadata reader that does "
               "not write to the file."),
        clause("6.2.2", "The original file is never opened for writing. The "
               "SHA-256 digest of the original is computed before any handling "
               "and carried into the report; all operations are performed on a "
               "copy."),
        clause("6.2.3", "The image measurement tool shall preserve the pixel "
               "coordinates of the original image. Cropping, perspective "
               "correction or resampling applied before measurement invalidate "
               "the scale established in 9.2."),
    ])


def bloc_7(fr):
    """Conditions d'essai — recevabilité."""
    if fr:
        cond = [
            "le fichier d'origine est disponible&#160;;",
            "son authenticit&#233; peut &#234;tre &#233;tablie&#160;;",
            "les caract&#233;ristiques de l'appareil sont connues ou "
            "retrouvables&#160;;",
            "la cible est identifiable sans ambigu&#239;t&#233;&#160;;",
            "la position de l'observateur est d&#233;terminable&#160;;",
            "les autres param&#232;tres de 8.2 sont &#233;tablissables avec la "
            "pr&#233;cision qui y est vis&#233;e.",
        ]
        return "\n".join([
            h2(7, fr),
            clause("7.1", "Une photographie est recevable si les six conditions "
                   "suivantes sont r&#233;unies&#160;:"),
            "<ul>\n%s\n</ul>" % "\n".join("  <li>%s</li>" % c for c in cond),
            clause("7.2", "Ces conditions ne portent pas sur l'intention de "
                   "l'op&#233;rateur. Une photographie prise en vacances, sans "
                   "aucun projet de mesure, est recevable si elle les "
                   "satisfait."),
            clause("7.3", "L'authenticit&#233; s'&#233;tablit par la "
                   "coh&#233;rence entre le fichier brut, ses "
                   "m&#233;tadonn&#233;es et les faits v&#233;rifiables "
                   "ind&#233;pendamment&#160;: position du Soleil &#224; "
                   "l'heure et au lieu d&#233;clar&#233;s, &#233;tat de la "
                   "mar&#233;e, position d'un navire au registre AIS, "
                   "pr&#233;sence des rep&#232;res attendus dans le champ."),
            clause("7.4", "Une photographie non recevable est class&#233;e "
                   "<strong>non concluante</strong> et l'analyse s'arr&#234;te. "
                   "Elle n'est ni retenue comme favorable ni retenue comme "
                   "d&#233;favorable."),
            encadre("Ce qui n'est jamais fait",
                    "<p>Aucun param&#232;tre manquant n'est reconstruit &#224; "
                    "partir de l'image elle-m&#234;me pour compl&#233;ter un "
                    "dossier. Si la hauteur de la cible est inconnue, elle "
                    "reste inconnue&#160;; on ne la d&#233;duit pas de sa "
                    "taille apparente dans le clich&#233; qu'on cherche "
                    "pr&#233;cis&#233;ment &#224; juger.</p>"),
        ])
    cond = [
        "the original file is available;",
        "its authenticity can be established;",
        "the camera's characteristics are known or recoverable;",
        "the target is unambiguously identifiable;",
        "the observer's position is determinable;",
        "the remaining parameters of 8.2 are establishable to the precision "
        "stated there.",
    ]
    return "\n".join([
        h2(7, fr),
        clause("7.1", "A photograph is admissible if the following six "
               "conditions are met:"),
        "<ul>\n%s\n</ul>" % "\n".join("  <li>%s</li>" % c for c in cond),
        clause("7.2", "These conditions do not bear on the operator's intent. A "
               "holiday snapshot, taken with no measurement in mind, is "
               "admissible if it meets them."),
        clause("7.3", "Authenticity is established by the consistency between "
               "the raw file, its metadata and independently verifiable facts: "
               "the Sun's position at the declared time and place, the state of "
               "the tide, a ship's position in the AIS record, the presence of "
               "the expected landmarks in the field."),
        clause("7.4", "An inadmissible photograph is classified "
               "<strong>inconclusive</strong> and the analysis stops. It is "
               "counted neither as favourable nor as unfavourable."),
        encadre("What is never done",
                "<p>No missing parameter is reconstructed from the image itself "
                "in order to complete a file. If the target's height is "
                "unknown, it stays unknown; it is not inferred from its "
                "apparent size in the very frame under judgement.</p>"),
    ])


# Ce que la phase 1 consigne. Automatique = écrit par l'appareil.
CONSIGNES = [
    ("Date et heure, en temps universel", "Date and time, universal time",
     "auto", "auto"),
    ("Position GNSS et incertitude annonc&#233;e",
     "GNSS position and stated uncertainty", "auto", "auto"),
    ("Altitude du point de vue", "Elevation of the viewpoint", "auto", "auto"),
    ("Hauteur de l'axe optique au-dessus du sol ou de l'eau",
     "Height of the optical axis above ground or water", "manuel", "manual"),
    ("Orientation de l'appareil, azimut et assiette",
     "Camera orientation, azimuth and attitude", "auto", "auto"),
    ("Bo&#238;tier, objectif, focale r&#233;elle",
     "Camera body, lens, actual focal length", "auto", "auto"),
    ("Ouverture, temps de pose, sensibilit&#233;",
     "Aperture, shutter speed, sensitivity", "auto", "auto"),
    ("Format brut conserv&#233; et non converti",
     "Raw format preserved and unconverted", "manuel", "manual"),
    ("Ce qui est vis&#233;, en une phrase", "What is being aimed at, in one "
     "sentence", "manuel", "manual"),
    ("Temp&#233;rature de l'air, et de l'eau si la vis&#233;e la survole",
     "Air temperature, and water temperature if the sight line passes over it",
     "manuel", "manual"),
]


def bloc_8(fr):
    """Mode opératoire."""
    if fr:
        t_consignes = tab(
            "Tableau&#160;1 &#8212; ce que la phase 1 consigne. Les champs "
            "automatiques sont &#233;crits par l'appareil&#160;; il suffit de "
            "ne pas les effacer.",
            ["&#201;l&#233;ment", "Saisie"],
            [rang([c[0], c[2]]) for c in CONSIGNES])
        t_det = tab(
            "Tableau&#160;2 &#8212; les quinze d&#233;terminations de la "
            "phase 2. Chacune s'&#233;tablit sans lire la photographie "
            "analys&#233;e.",
            ["N&#176;", "&#192; &#233;tablir", "Source ind&#233;pendante admise",
             "Pr&#233;cision vis&#233;e"],
            [rang(["%02d" % (i + 1), d[0], d[2], d[4]], num=(0,))
             for i, d in enumerate(DETERMINATIONS)])
        t_cls = tab(
            "Tableau&#160;3 &#8212; classes de donn&#233;e atmosph&#233;rique. "
            "La classe dit comment la valeur a &#233;t&#233; obtenue, pas si "
            "elle est juste.",
            ["Classe", "Origine", "D&#233;finition", "Statut au rapport"],
            [rang([c[0], c[1], c[3], c[5]], num=(0,)) for c in CLASSES])
        return "\n".join([
            h2(8, fr, saut=True),
            "<h3>8.1 Phase 1 &#8212; acquisition</h3>",
            clause("8.1.1", "Installer l'appareil sur son support et relever "
                   "la hauteur de l'axe optique."),
            clause("8.1.2", "Enregistrer en format brut. Si l'appareil produit "
                   "aussi un fichier compress&#233;, conserver les deux."),
            clause("8.1.3", "Prendre au moins trois clich&#233;s de la cible "
                   "&#224; la focale maximale utile, et un clich&#233; "
                   "grand-angle montrant le point de vue et ses rep&#232;res "
                   "proches."),
            clause("8.1.4", "Consigner les &#233;l&#233;ments du "
                   "tableau&#160;1. Les champs marqu&#233;s <em>auto</em> sont "
                   "&#233;crits par l'appareil&#160;: la seule exigence est de "
                   "ne pas les supprimer par la suite."),
            t_consignes,
            clause("8.1.5", "Archiver le fichier brut sans conversion, sans "
                   "recadrage et sans retouche. Les m&#233;tadonn&#233;es sont "
                   "conserv&#233;es m&#234;me si l'analyse n'a lieu que "
                   "plusieurs semaines plus tard."),
            clause("8.1.6", "La phase 1 s'arr&#234;te ici. Aucun calcul n'y est "
                   "conduit et aucune conclusion n'y est tir&#233;e."),
            "<h3>8.2 Phase 2 &#8212; reconstitution des param&#232;tres</h3>",
            clause("8.2.1", "&#201;tablir les quinze &#233;l&#233;ments du "
                   "tableau&#160;2, chacun &#224; partir d'une source "
                   "ind&#233;pendante de la photographie analys&#233;e."),
            clause("8.2.2", "Consigner pour chaque &#233;l&#233;ment la source "
                   "exacte, sa date d'&#233;dition et l'incertitude "
                   "retenue. Une source sans date n'est pas admise."),
            t_det,
            clause("8.2.3", "Lorsqu'un &#233;l&#233;ment ne peut &#234;tre "
                   "&#233;tabli &#224; la pr&#233;cision vis&#233;e, la valeur "
                   "retenue est report&#233;e avec son incertitude "
                   "r&#233;elle, plus large. Elle n'est jamais remplac&#233;e "
                   "par une valeur commode."),
            "<h3>8.3 Donn&#233;es atmosph&#233;riques a posteriori</h3>",
            clause("8.3.1", "Le cas normal est celui o&#249; l'op&#233;rateur "
                   "n'a effectu&#233; aucune mesure atmosph&#233;rique. Chaque "
                   "donn&#233;e retenue re&#231;oit alors la classe du "
                   "tableau&#160;3 qui correspond &#224; son origine."),
            t_cls,
            clause("8.3.2", "Une donn&#233;e atmosph&#233;rique estim&#233;e a "
                   "posteriori n'est jamais pr&#233;sent&#233;e comme une "
                   "mesure directe. La classe accompagne la valeur partout "
                   "o&#249; celle-ci appara&#238;t, y compris dans la "
                   "conclusion."),
            clause("8.3.3", "L'insuffisance des donn&#233;es atmosph&#233;riques "
                   "ne se traite pas par un choix prudent&#160;: elle se "
                   "traite en reportant la plage enti&#232;re des valeurs "
                   "plausibles dans l'incertitude, selon 9.4."),
            "<h3>8.4 Interdiction d'ajustement</h3>",
            clause("8.4.1", "La hauteur ou la distance n'est jamais ajust&#233;e "
                   "apr&#232;s observation pour faire correspondre le calcul "
                   "&#224; l'image."),
            clause("8.4.2", "Si une valeur retenue en 8.2 est corrig&#233;e "
                   "apr&#232;s le premier calcul, la correction n'est admise "
                   "que si elle provient d'une source ind&#233;pendante "
                   "nouvelle, et le rapport indique la valeur ant&#233;rieure, "
                   "la valeur retenue et la source qui a tranch&#233;."),
            clause("8.4.3", "La photographie n'est pas modifi&#233;e pour les "
                   "besoins de l'analyse. Les traitements admis sont ceux qui "
                   "ne d&#233;placent aucun pixel&#160;: r&#233;glage "
                   "d'affichage du contraste et de la luminosit&#233;, "
                   "agrandissement &#224; l'&#233;cran. Ils s'appliquent "
                   "&#224; la copie, et le rapport les &#233;num&#232;re."),
        ])
    t_consignes = tab(
        "Table&#160;1 &#8212; what phase 1 records. Automatic fields are "
        "written by the camera; it is enough not to delete them.",
        ["Item", "Entry"],
        [rang([c[1], c[3]]) for c in CONSIGNES])
    t_det = tab(
        "Table&#160;2 &#8212; the fifteen determinations of phase 2. Each is "
        "established without reading the photograph under analysis.",
        ["No.", "To establish", "Admissible independent source",
         "Target precision"],
        [rang(["%02d" % (i + 1), d[1], d[3], d[5]], num=(0,))
         for i, d in enumerate(DETERMINATIONS)])
    t_cls = tab(
        "Table&#160;3 &#8212; atmospheric data classes. The class states how "
        "the value was obtained, not whether it is correct.",
        ["Class", "Origin", "Definition", "Status in the report"],
        [rang([c[0], c[2], c[4], c[6]], num=(0,)) for c in CLASSES])
    return "\n".join([
        h2(8, fr, saut=True),
        "<h3>8.1 Phase 1 &#8212; acquisition</h3>",
        clause("8.1.1", "Set the camera on its support and record the height of "
               "the optical axis."),
        clause("8.1.2", "Record in raw format. If the camera also produces a "
               "compressed file, keep both."),
        clause("8.1.3", "Take at least three frames of the target at the "
               "longest useful focal length, and one wide-angle frame showing "
               "the viewpoint and its near landmarks."),
        clause("8.1.4", "Record the items of table&#160;1. The fields marked "
               "<em>auto</em> are written by the camera: the only requirement "
               "is not to delete them afterwards."),
        t_consignes,
        clause("8.1.5", "Archive the raw file unconverted, uncropped and "
               "unretouched. The metadata are preserved even if the analysis "
               "takes place only weeks later."),
        clause("8.1.6", "Phase 1 stops here. No computation is carried out and "
               "no conclusion is drawn in it."),
        "<h3>8.2 Phase 2 &#8212; reconstruction of the parameters</h3>",
        clause("8.2.1", "Establish the fifteen items of table&#160;2, each from "
               "a source independent of the photograph under analysis."),
        clause("8.2.2", "Record for each item the exact source, its edition "
               "date and the uncertainty adopted. An undated source is not "
               "admissible."),
        t_det,
        clause("8.2.3", "Where an item cannot be established to the target "
               "precision, the adopted value is reported with its real, wider "
               "uncertainty. It is never replaced by a convenient value."),
        "<h3>8.3 A posteriori atmospheric data</h3>",
        clause("8.3.1", "The normal case is one in which the operator made no "
               "atmospheric measurement. Each adopted datum then receives the "
               "class from table&#160;3 matching its origin."),
        t_cls,
        clause("8.3.2", "An atmospheric datum estimated a posteriori is never "
               "presented as a direct measurement. The class accompanies the "
               "value wherever it appears, including in the conclusion."),
        clause("8.3.3", "Insufficient atmospheric data are not handled by a "
               "cautious choice: they are handled by carrying the whole range "
               "of plausible values into the uncertainty, per 9.4."),
        "<h3>8.4 No adjustment</h3>",
        clause("8.4.1", "A height or a distance is never adjusted after the "
               "observation to make the computation match the image."),
        clause("8.4.2", "If a value adopted in 8.2 is corrected after the first "
               "computation, the correction is admissible only if it comes from "
               "a new independent source, and the report states the previous "
               "value, the adopted value and the source that settled it."),
        clause("8.4.3", "The photograph is not modified for the purposes of the "
               "analysis. The admissible treatments are those that displace no "
               "pixel: display adjustment of contrast and brightness, "
               "magnification on screen. They are applied to the copy, and the "
               "report lists them."),
    ])


def bloc_9(fr):
    """Calcul."""
    base, dh, dd, dk = sensibilites()
    u_h, u_d, u_k, u = budget()
    arcsec_px, sol_px, diffr = resolution()
    n = lambda x, p: nb(x, p, fr)

    eq_c = (
        '<div class="eq">R&#8242; = R / (1 &#8722; k)'
        '&#160;&#160;&#160;&#160;a = &#8730;[(R&#8242;+h)&#178; &#8722; R&#8242;&#178;]'
        '&#160;&#160;&#160;&#160;c = &#8730;[R&#8242;&#178; + (d &#8722; a)&#178;] '
        '&#8722; R&#8242;<span class="cap">%s</span></div>')
    eq_ech = ('<div class="eq">&#952;<sub>px</sub> = p / f'
              '&#160;&#160;&#160;&#160;s = &#952;<sub>px</sub> &#183; d'
              '<span class="cap">%s</span></div>')
    eq_m = ('<div class="eq">N = 77,6&#160;P/T + 3,73&#215;10&#8309;&#160;e/T&#178;'
            '&#160;&#160;&#160;&#160;M = N + 0,157&#160;z'
            '<span class="cap">%s</span></div>')
    eq_k = ('<div class="eq">k = 503&#160;(P/T&#178;)&#160;(0,0342 + dT/dz)'
            '<span class="cap">%s</span></div>')

    if fr:
        t_sens = tab(
            "Tableau&#160;4 &#8212; sensibilit&#233; de la pr&#233;diction, "
            "pour un &#339;il &#224; %s&#8239;m et une cible &#224; "
            "%s&#8239;km, o&#249; <em>c</em> vaut %s&#8239;m."
            % (n(H_REF, 0), n(D_REF, 0), n(base, 1)),
            ["Param&#232;tre", "&#201;cart consid&#233;r&#233;",
             "Effet sur <em>c</em>", "Contribution &#224; u(c)"],
            [rang(["hauteur d'&#339;il <em>h</em>", "1&#8239;m",
                   "%s&#8239;m" % n(dh, 2), "%s&#8239;m" % n(u_h, 1)], num=NUM4),
             rang(["distance <em>d</em>", "100&#8239;m",
                   "%s&#8239;m" % n(dd / 10, 2), "%s&#8239;m" % n(u_d, 1)], num=NUM4),
             rang(["coefficient <em>k</em>", "0,01",
                   "%s&#8239;m" % n(dk, 2), "&#8212;"], num=NUM4),
             rang(["coefficient <em>k</em>, non mesur&#233;",
                    "plage %s &#224; %s" % (n(K_PLAGE[0], 2), n(K_PLAGE[1], 2)),
                    "%s&#8239;m" % n(abs(dk) * (K_PLAGE[1] - K_PLAGE[0]) * 100, 1),
                   "%s&#8239;m" % n(u_k, 1)], num=NUM4, vedette=True),
             rang(["<strong>total quadratique</strong>", "", "",
                   "<strong>%s&#8239;m</strong>" % n(u, 1)], num=NUM4)])
        return "\n".join([
            h2(9, fr, saut=True),
            "<h3>9.1 Hauteur masqu&#233;e pr&#233;dite</h3>",
            clause("9.1.1", "Calculer la hauteur masqu&#233;e <em>c</em> pour "
                   "la hauteur d'&#339;il <em>h</em>, la distance <em>d</em> et "
                   "le coefficient <em>k</em> retenus&#160;:"),
            eq_c % ("R = 6&#8239;371&#8239;km. Toutes les longueurs en "
                    "m&#232;tres."),
            clause("9.1.2", "<em>c</em> ne d&#233;pend pas de la hauteur de la "
                   "cible. Celle-ci n'intervient qu'&#224; la comparaison, en "
                   "9.7."),
            clause("9.1.3", "Lorsque le profil de la section&#160;8.2, "
                   "&#233;l&#233;ment&#160;09, comporte un relief "
                   "interm&#233;diaire dont l'altitude d&#233;passe la ligne de "
                   "vis&#233;e, le masquage est topographique et non "
                   "g&#233;om&#233;trique&#160;: la m&#233;thode ne "
                   "s'applique pas &#224; ce clich&#233;."),
            "<h3>9.2 &#201;chelle de l'image</h3>",
            clause("9.2.1", "L'angle sous-tendu par un pixel, puis "
                   "l'&#233;chelle au sol &#224; la distance de la cible&#160;:"),
            eq_ech % ("p, pas du capteur&#160;; f, focale r&#233;elle&#160;; "
                      "d, distance."),
            clause("9.2.2", "Pour un pas de %s&#8239;&#181;m et une focale de "
                   "%s&#8239;mm, un pixel couvre %s&#8243;, soit %s&#8239;m au "
                   "sol &#224; %s&#8239;km."
                   % (n(PAS_PIXEL * 1e6, 1), n(FOCALE * 1000, 0),
                      n(arcsec_px, 2), n(sol_px, 2), n(D_REF, 0))),
            clause("9.2.3", "V&#233;rifier l'&#233;chelle sur deux "
                   "rep&#232;res de position connue pr&#233;sents dans le "
                   "m&#234;me clich&#233;. Un &#233;cart sup&#233;rieur "
                   "&#224; 2&#8239;% par rapport &#224; la focale "
                   "d&#233;clar&#233;e invalide la focale, non les "
                   "rep&#232;res."),
            clause("9.2.4", "La r&#233;solution effective est la plus grande "
                   "des trois&#160;: le pixel projet&#233;, la limite de "
                   "diffraction &#8212; %s&#8243; pour une pupille de "
                   "%s&#8239;mm &#8212; et la largeur mesur&#233;e d'un bord "
                   "franc dans l'image. Sur une vis&#233;e rasante de plusieurs "
                   "dizaines de kilom&#232;tres, c'est habituellement la "
                   "troisi&#232;me."
                   % (n(diffr, 1), n(PUPILLE * 1000, 0))),
            "<h3>9.3 Hauteur masqu&#233;e observ&#233;e</h3>",
            clause("9.3.1", "Rep&#233;rer dans l'image deux parties pertinentes "
                   "d'altitude connue et mesurer leur &#233;cart en pixels. "
                   "L'&#233;chelle m&#233;trique de la cible s'en d&#233;duit, "
                   "ind&#233;pendamment de 9.2."),
            clause("9.3.2", "Mesurer la position du bord inf&#233;rieur visible "
                   "de la cible. La hauteur masqu&#233;e observ&#233;e "
                   "<em>c</em><sub>obs</sub> est la diff&#233;rence entre "
                   "l'altitude de la base et l'altitude de ce bord."),
            clause("9.3.3", "Assigner &#224; <em>c</em><sub>obs</sub> une "
                   "incertitude &#233;gale &#224; la r&#233;solution effective "
                   "de 9.2.4, convertie en m&#232;tres &#224; la distance de la "
                   "cible, et jamais inf&#233;rieure &#224; celle-ci."),
            "<h3>9.4 Incertitude de la pr&#233;diction</h3>",
            clause("9.4.1", "Composer les incertitudes en quadrature, chaque "
                   "param&#232;tre &#233;tant affect&#233; de sa "
                   "d&#233;riv&#233;e partielle. Le tableau&#160;4 donne les "
                   "ordres de grandeur sur un cas courant."),
            t_sens,
            clause("9.4.2", "Le coefficient de r&#233;fraction domine le "
                   "budget d&#232;s qu'il n'est pas mesur&#233;. C'est la "
                   "raison d'&#234;tre des classes de 8.3&#160;: une "
                   "donn&#233;e de classe&#160;D laisse une incertitude qui "
                   "&#233;crase toutes les autres."),
            clause("9.4.3", "Lorsque le coefficient rel&#232;ve de la "
                   "classe&#160;C ou&#160;D, la plage report&#233;e dans "
                   "l'incertitude est la plage plausible enti&#232;re pour le "
                   "site, la saison et l'heure, et non une valeur unique "
                   "assortie d'une marge choisie."),
            "<h3>9.5 Estimation du coefficient de r&#233;fraction</h3>",
            clause("9.5.1", "Si un profil vertical de temp&#233;rature est "
                   "disponible, le coefficient se calcule&#160;:"),
            eq_k % ("P en hPa, T en K, dT/dz en K/m."),
            clause("9.5.2", "&#192; 1&#8239;013&#8239;hPa et 288&#8239;K, "
                   "<em>k</em>&#160;=&#160;0,13 correspond &#224; un gradient "
                   "de &#8722;1,30&#8239;K par 100&#8239;m, et "
                   "<em>k</em>&#160;=&#160;1 &#224; +12,9&#8239;K par "
                   "100&#8239;m."),
            clause("9.5.3", "Au-dessus de l'eau, le gradient thermique ne "
                   "suffit pas&#160;: c'est l'humidit&#233; qui pilote. "
                   "Calculer alors la r&#233;fractivit&#233; modifi&#233;e "
                   "<em>M</em>&#160;:"),
            eq_m % ("P pression en hPa, e pression partielle de vapeur d'eau en "
                    "hPa, T en K, z altitude en m."),
            clause("9.5.4", "Une couche o&#249; <em>M</em> d&#233;cro&#238;t "
                   "avec l'altitude est un conduit. Si le point le plus bas du "
                   "rayon traverse une telle couche, le coefficient n'est pas "
                   "born&#233; par le profil moyen et l'analyse conclut selon "
                   "11.2."),
            clause("9.5.5", "Les coefficients mesur&#233;s pr&#232;s du sol "
                   "s'&#233;tendent de &#8722;4 &#224; +16 (r&#233;f. 7). "
                   "Aucune borne sup&#233;rieure n'est donc pos&#233;e a priori "
                   "sur <em>k</em>&#160;; c'est la valeur exig&#233;e qui est "
                   "calcul&#233;e, puis compar&#233;e."),
            "<h3>9.6 Coefficient exig&#233;</h3>",
            clause("9.6.1", "R&#233;soudre en <em>k</em> l'&#233;quation de "
                   "9.1.1 avec <em>c</em>&#160;=&#160;<em>c</em><sub>obs</sub>. "
                   "La solution <em>k</em><sub>ex</sub> est le coefficient "
                   "qu'il aurait fallu pour que l'image soit ce qu'elle est."),
            clause("9.6.2", "Reporter <em>k</em><sub>ex</sub> avec son "
                   "intervalle, et la longueur du trajet sur laquelle il "
                   "devrait avoir &#233;t&#233; maintenu."),
            clause("9.6.3", "L'&#233;quation admet toujours une solution "
                   "inf&#233;rieure &#224; 1&#160;: la hauteur masqu&#233;e "
                   "tend vers z&#233;ro quand <em>k</em> tend vers 1. Aucune "
                   "observation n'est donc g&#233;om&#233;triquement "
                   "impossible, et la m&#233;thode ne conclut jamais qu'elle "
                   "l'est."),
            "<h3>9.7 Verdict</h3>",
            clause("9.7.1", "<strong>Compatible</strong> &#8212; "
                   "<em>c</em><sub>obs</sub> et <em>c</em> pr&#233;dit "
                   "diff&#232;rent de moins de 3&#963;, o&#249; &#963; est la "
                   "composition quadratique de l'incertitude de pr&#233;diction "
                   "et de celle de mesure."),
            clause("9.7.2", "<strong>Incompatible</strong> &#8212; l'&#233;cart "
                   "d&#233;passe 3&#963; et <em>k</em><sub>ex</sub> se situe "
                   "hors de la plage document&#233;e pour ce site, cette saison "
                   "et cette heure. Le rapport &#233;nonce alors "
                   "<em>k</em><sub>ex</sub>, sa longueur de maintien, et la "
                   "plage &#224; laquelle il est compar&#233;."),
            clause("9.7.3", "<strong>Non concluante</strong> &#8212; dans tous "
                   "les autres cas, et dans ceux de la section&#160;11."),
        ])

    t_sens = tab(
        "Table&#160;4 &#8212; sensitivity of the prediction, for an eye at "
        "%s&#8239;m and a target at %s&#8239;km, where <em>c</em> is "
        "%s&#8239;m." % (n(H_REF, 0), n(D_REF, 0), n(base, 1)),
        ["Parameter", "Departure considered", "Effect on <em>c</em>",
         "Contribution to u(c)"],
        [rang(["eye height <em>h</em>", "1&#8239;m", "%s&#8239;m" % n(dh, 2),
               "%s&#8239;m" % n(u_h, 1)], num=NUM4),
         rang(["distance <em>d</em>", "100&#8239;m",
               "%s&#8239;m" % n(dd / 10, 2), "%s&#8239;m" % n(u_d, 1)], num=NUM4),
         rang(["coefficient <em>k</em>", "0.01", "%s&#8239;m" % n(dk, 2),
               "&#8212;"], num=NUM4),
         rang(["coefficient <em>k</em>, unmeasured",
                "range %s to %s" % (n(K_PLAGE[0], 2), n(K_PLAGE[1], 2)),
                "%s&#8239;m" % n(abs(dk) * (K_PLAGE[1] - K_PLAGE[0]) * 100, 1),
               "%s&#8239;m" % n(u_k, 1)], num=NUM4, vedette=True),
         rang(["<strong>quadratic total</strong>", "", "",
               "<strong>%s&#8239;m</strong>" % n(u, 1)], num=NUM4)])
    return "\n".join([
        h2(9, fr, saut=True),
        "<h3>9.1 Predicted hidden height</h3>",
        clause("9.1.1", "Compute the hidden height <em>c</em> for the adopted "
               "eye height <em>h</em>, distance <em>d</em> and coefficient "
               "<em>k</em>:"),
        eq_c % "R = 6&#8239;371&#8239;km. All lengths in metres.",
        clause("9.1.2", "<em>c</em> does not depend on the target's height. "
               "That height enters only at the comparison, in 9.7."),
        clause("9.1.3", "Where the profile of section&#160;8.2, item&#160;09, "
               "contains intervening ground whose elevation exceeds the line of "
               "sight, the masking is topographic and not geometric: the method "
               "does not apply to that frame."),
        "<h3>9.2 Image scale</h3>",
        clause("9.2.1", "The angle subtended by one pixel, then the ground "
               "scale at the target's distance:"),
        eq_ech % "p, sensor pitch; f, actual focal length; d, distance.",
        clause("9.2.2", "For a pitch of %s&#8239;&#181;m and a focal length of "
               "%s&#8239;mm, one pixel covers %s&#8243;, that is %s&#8239;m on "
               "the ground at %s&#8239;km."
               % (n(PAS_PIXEL * 1e6, 1), n(FOCALE * 1000, 0), n(arcsec_px, 2),
                  n(sol_px, 2), n(D_REF, 0))),
        clause("9.2.3", "Check the scale against two landmarks of known "
               "position present in the same frame. A discrepancy greater than "
               "2&#8239;% relative to the declared focal length invalidates the "
               "focal length, not the landmarks."),
        clause("9.2.4", "The effective resolution is the largest of three: the "
               "projected pixel, the diffraction limit &#8212; %s&#8243; for a "
               "%s&#8239;mm pupil &#8212; and the measured width of a sharp "
               "edge in the image. On a grazing sight line of tens of "
               "kilometres it is usually the third."
               % (n(diffr, 1), n(PUPILLE * 1000, 0))),
        "<h3>9.3 Observed hidden height</h3>",
        clause("9.3.1", "Locate in the image two relevant parts of known "
               "elevation and measure their separation in pixels. The target's "
               "metric scale follows, independently of 9.2."),
        clause("9.3.2", "Measure the position of the target's visible lower "
               "edge. The observed hidden height <em>c</em><sub>obs</sub> is "
               "the difference between the elevation of the base and the "
               "elevation of that edge."),
        clause("9.3.3", "Assign to <em>c</em><sub>obs</sub> an uncertainty "
               "equal to the effective resolution of 9.2.4, converted to metres "
               "at the target's distance, and never smaller than it."),
        "<h3>9.4 Uncertainty of the prediction</h3>",
        clause("9.4.1", "Combine the uncertainties in quadrature, each "
               "parameter weighted by its partial derivative. Table&#160;4 "
               "gives the orders of magnitude on a common case."),
        t_sens,
        clause("9.4.2", "The refraction coefficient dominates the budget as "
               "soon as it is not measured. That is the reason for the classes "
               "of 8.3: a class&#160;D datum leaves an uncertainty that "
               "swamps every other."),
        clause("9.4.3", "Where the coefficient is of class&#160;C or&#160;D, "
               "the range carried into the uncertainty is the whole plausible "
               "range for the site, season and hour, not a single value with a "
               "chosen margin."),
        "<h3>9.5 Estimating the refraction coefficient</h3>",
        clause("9.5.1", "If a vertical temperature profile is available, the "
               "coefficient follows from:"),
        eq_k % "P in hPa, T in K, dT/dz in K/m.",
        clause("9.5.2", "At 1&#8239;013&#8239;hPa and 288&#8239;K, "
               "<em>k</em>&#160;=&#160;0.13 corresponds to a gradient of "
               "&#8722;1.30&#8239;K per 100&#8239;m, and "
               "<em>k</em>&#160;=&#160;1 to +12.9&#8239;K per 100&#8239;m."),
        clause("9.5.3", "Over water the thermal gradient is not enough: "
               "humidity governs. Compute the modified refractivity "
               "<em>M</em>:"),
        eq_m % ("P pressure in hPa, e partial pressure of water vapour in hPa, "
                "T in K, z height in m."),
        clause("9.5.4", "A layer in which <em>M</em> decreases with height is a "
               "duct. If the ray's lowest point crosses such a layer, the "
               "coefficient is not bounded by the mean profile and the analysis "
               "concludes per 11.2."),
        clause("9.5.5", "Coefficients measured near the ground range from "
               "&#8722;4 to +16 (ref. 7). No upper bound is therefore assumed a "
               "priori on <em>k</em>; the required value is computed, then "
               "compared."),
        "<h3>9.6 Required coefficient</h3>",
        clause("9.6.1", "Solve the equation of 9.1.1 for <em>k</em> with "
               "<em>c</em>&#160;=&#160;<em>c</em><sub>obs</sub>. The solution "
               "<em>k</em><sub>req</sub> is the coefficient that would have "
               "been needed for the image to be what it is."),
        clause("9.6.2", "Report <em>k</em><sub>req</sub> with its interval, and "
               "the length of path over which it would have had to be "
               "sustained."),
        clause("9.6.3", "The equation always admits a solution below 1: the "
               "hidden height tends to zero as <em>k</em> tends to 1. No "
               "observation is therefore geometrically impossible, and the "
               "method never concludes that one is."),
        "<h3>9.7 Verdict</h3>",
        clause("9.7.1", "<strong>Compatible</strong> &#8212; "
               "<em>c</em><sub>obs</sub> and the predicted <em>c</em> differ by "
               "less than 3&#963;, where &#963; is the quadratic combination of "
               "the prediction and measurement uncertainties."),
        clause("9.7.2", "<strong>Incompatible</strong> &#8212; the difference "
               "exceeds 3&#963; and <em>k</em><sub>req</sub> lies outside the "
               "documented range for that site, season and hour. The report "
               "then states <em>k</em><sub>req</sub>, its sustaining length, "
               "and the range against which it is compared."),
        clause("9.7.3", "<strong>Inconclusive</strong> &#8212; in every other "
               "case, and in those of section&#160;11."),
    ])


def bloc_10(fr):
    """Rapport d'essai — la chaîne de traçabilité."""
    t = tab(
        ("Tableau&#160;5 &#8212; cha&#238;ne de tra&#231;abilit&#233;. Un "
         "maillon sans source est un maillon rompu&#160;; le rapport "
         "l'indique plut&#244;t que de le combler."
         if fr else
         "Table&#160;5 &#8212; traceability chain. A link without a source is "
         "a broken link; the report says so rather than filling it in."),
        (["N&#176;", "&#201;l&#233;ment", "Source", "Pr&#233;cision",
          "Incertitude", "Classe"] if fr else
         ["No.", "Element", "Source", "Precision", "Uncertainty", "Class"]),
        [rang(["%02d" % (i + 1), e[0 if fr else 1], "", "", "", ""], num=(0,))
         for i, e in enumerate(CHAINE)])
    if fr:
        return "\n".join([
            h2(10, fr, saut=True),
            clause("10.1", "Le rapport reprend la cha&#238;ne du "
                   "tableau&#160;5 dans l'ordre. Chaque &#233;l&#233;ment porte "
                   "sa source, sa pr&#233;cision, son incertitude et, pour les "
                   "donn&#233;es atmosph&#233;riques, sa classe au sens de 8.3."),
            t,
            clause("10.2", "Y figurent en outre&#160;: l'empreinte SHA-256 du "
                   "fichier d'origine, la liste des traitements "
                   "appliqu&#233;s &#224; la copie, le nom de l'op&#233;rateur "
                   "de la phase 1 et celui de l'analyste de la phase 2 lorsque "
                   "ce sont deux personnes, et l'&#233;cart de temps entre les "
                   "deux phases."),
            clause("10.3", "La conclusion cite le verdict de 9.7, la valeur de "
                   "<em>c</em><sub>obs</sub>, celle de <em>c</em> pr&#233;dit, "
                   "l'incertitude compos&#233;e, et <em>k</em><sub>ex</sub>."),
            clause("10.4", "Lorsque le verdict est <em>non concluante</em>, le "
                   "rapport nomme le ou les maillons qui manquent, et ce qu'il "
                   "faudrait pour les &#233;tablir. Un dossier "
                   "compl&#233;t&#233; plus tard est r&#233;analys&#233; sans "
                   "que la photographie soit reprise."),
            clause("10.5", "Le rapport est publi&#233; avec le fichier "
                   "d'origine ou, si celui-ci ne peut &#234;tre diffus&#233;, "
                   "avec son empreinte et l'indication de qui le d&#233;tient."),
        ])
    return "\n".join([
        h2(10, fr, saut=True),
        clause("10.1", "The report follows the chain of table&#160;5 in order. "
               "Each element carries its source, its precision, its uncertainty "
               "and, for atmospheric data, its class within the meaning of 8.3."),
        t,
        clause("10.2", "It further states: the SHA-256 digest of the original "
               "file, the list of treatments applied to the copy, the name of "
               "the phase 1 operator and that of the phase 2 analyst where "
               "these are two people, and the time elapsed between the two "
               "phases."),
        clause("10.3", "The conclusion quotes the verdict of 9.7, the value of "
               "<em>c</em><sub>obs</sub>, that of the predicted <em>c</em>, the "
               "combined uncertainty, and <em>k</em><sub>req</sub>."),
        clause("10.4", "Where the verdict is <em>inconclusive</em>, the report "
               "names the missing link or links, and what would be needed to "
               "establish them. A file completed later is re-analysed without "
               "the photograph being retaken."),
        clause("10.5", "The report is published with the original file or, if "
               "that file cannot be circulated, with its digest and a statement "
               "of who holds it."),
    ])


def bloc_11(fr):
    """Fidélité et biais."""
    if fr:
        disq = [
            "le fichier d'origine est indisponible, ou ses "
            "m&#233;tadonn&#233;es ont &#233;t&#233; r&#233;&#233;crites sans "
            "que la version ant&#233;rieure puisse &#234;tre produite&#160;;",
            "la focale r&#233;elle est inconnue et ne peut &#234;tre "
            "retrouv&#233;e par deux rep&#232;res de position connue&#160;;",
            "la cible n'est identifiable que par ressemblance&#160;;",
            "la position de l'observateur n'est d&#233;terminable ni par le "
            "r&#233;cepteur GNSS, ni par les rep&#232;res proches du "
            "clich&#233; d'amorce.",
        ]
        return "\n".join([
            h2(11, fr),
            clause("11.1", "<strong>Crit&#232;re quantitatif.</strong> Une "
                   "photographie est class&#233;e non concluante lorsque "
                   "l'incertitude compos&#233;e &#963; d&#233;passe le tiers de "
                   "l'&#233;cart constat&#233; entre "
                   "<em>c</em><sub>obs</sub> et <em>c</em> pr&#233;dit. En "
                   "d'autres termes, la m&#233;thode ne conclut qu'&#224; "
                   "partir de 3&#963;."),
            clause("11.2", "<strong>Conduit non exclu.</strong> Lorsque le "
                   "point le plus bas du rayon passe &#224; moins de "
                   "40&#8239;m au-dessus de l'eau et qu'aucune donn&#233;e de "
                   "classe A ou B ne documente le profil d'humidit&#233;, le "
                   "coefficient n'est pas born&#233; et le verdict est non "
                   "concluant, quelle que soit l'ampleur de l'&#233;cart."),
            clause("11.3", "<strong>Disqualifications mat&#233;rielles.</strong> "
                   "Le verdict est non concluant si l'une des situations "
                   "suivantes est constat&#233;e&#160;:"),
            "<ul>\n%s\n</ul>" % "\n".join("  <li>%s</li>" % d for d in disq),
            clause("11.4", "<strong>Biais de s&#233;lection.</strong> Les "
                   "photographies parviennent &#224; l'analyse parce qu'elles "
                   "ont paru remarquables. Une s&#233;rie de dossiers ne "
                   "renseigne donc pas sur la fr&#233;quence des observations "
                   "atypiques, seulement sur celles qu'on a "
                   "conserv&#233;es et transmises."),
            clause("11.5", "<strong>Biais d'identification.</strong> Quand "
                   "l'analyste sait quelle r&#233;ponse arrangerait, il "
                   "identifie plus volontiers la cible qui la produit. C'est "
                   "pourquoi l'&#233;l&#233;ment&#160;01 exige un recoupement "
                   "et refuse la ressemblance."),
            clause("11.6", "<strong>Biais de traitement.</strong> "
                   "L'accentuation appliqu&#233;e par d&#233;faut aux fichiers "
                   "compress&#233;s cr&#233;e des bords nets l&#224; o&#249; "
                   "l'image n'en contient pas. C'est pourquoi la mesure se fait "
                   "sur le fichier brut."),
            clause("11.7", "<strong>Fid&#233;lit&#233;.</strong> Deux analystes "
                   "travaillant s&#233;par&#233;ment sur le m&#234;me dossier "
                   "doivent obtenir des <em>c</em><sub>obs</sub> "
                   "compatibles &#224; l'incertitude de 9.3.3 pr&#232;s. Un "
                   "&#233;cart sup&#233;rieur signale une ambigu&#239;t&#233; "
                   "sur le bord mesur&#233;, et le dossier revient en 9.3."),
            clause("11.8", "<strong>Justesse.</strong> La m&#233;thode n'a pas "
                   "d'&#233;talon&#160;: il n'existe pas de photographie de "
                   "r&#233;f&#233;rence dont la hauteur masqu&#233;e serait "
                   "connue par ailleurs. La justesse s'appr&#233;cie en "
                   "appliquant la m&#233;thode &#224; des clich&#233;s pris "
                   "dans des conditions document&#233;es par des mesures de "
                   "classe&#160;A."),
        ])
    disq = [
        "the original file is unavailable, or its metadata have been rewritten "
        "without the earlier version being producible;",
        "the actual focal length is unknown and cannot be recovered from two "
        "landmarks of known position;",
        "the target is identifiable only by resemblance;",
        "the observer's position is determinable neither from the GNSS receiver "
        "nor from the near landmarks of the establishing frame.",
    ]
    return "\n".join([
        h2(11, fr),
        clause("11.1", "<strong>Quantitative criterion.</strong> A photograph "
               "is classified inconclusive when the combined uncertainty &#963; "
               "exceeds one third of the observed difference between "
               "<em>c</em><sub>obs</sub> and the predicted <em>c</em>. In other "
               "words, the method concludes only from 3&#963; upward."),
        clause("11.2", "<strong>Duct not excluded.</strong> Where the ray's "
               "lowest point passes within 40&#8239;m of the water surface and "
               "no class A or B datum documents the humidity profile, the "
               "coefficient is not bounded and the verdict is inconclusive, "
               "whatever the size of the difference."),
        clause("11.3", "<strong>Material disqualifications.</strong> The "
               "verdict is inconclusive if any of the following is found:"),
        "<ul>\n%s\n</ul>" % "\n".join("  <li>%s</li>" % d for d in disq),
        clause("11.4", "<strong>Selection bias.</strong> Photographs reach the "
               "analysis because they looked remarkable. A series of files "
               "therefore says nothing about how often atypical observations "
               "occur, only about which ones were kept and sent in."),
        clause("11.5", "<strong>Identification bias.</strong> When the analyst "
               "knows which answer would suit, they identify more readily the "
               "target that produces it. Hence item&#160;01 requires a "
               "cross-check and refuses resemblance."),
        clause("11.6", "<strong>Processing bias.</strong> The sharpening "
               "applied by default to compressed files creates crisp edges "
               "where the image holds none. Hence the measurement is made on "
               "the raw file."),
        clause("11.7", "<strong>Precision.</strong> Two analysts working "
               "separately on the same file shall obtain values of "
               "<em>c</em><sub>obs</sub> agreeing within the uncertainty of "
               "9.3.3. A larger spread signals an ambiguity about which edge "
               "was measured, and the file returns to 9.3."),
        clause("11.8", "<strong>Bias.</strong> The method has no reference "
               "standard: there exists no benchmark photograph whose hidden "
               "height is otherwise known. Bias is assessed by applying the "
               "method to frames taken in conditions documented by class&#160;A "
               "measurements."),
    ])


def bloc_x1(fr):
    """Annexe non normative — d'où viennent les exigences."""
    base, dh, dd, dk = sensibilites()
    u_h, u_d, u_k, u = budget()
    n = lambda x, p: nb(x, p, fr)
    if fr:
        return "\n".join([
            h2_annexe(fr),
            "<h3>X1.1 Pourquoi deux phases s&#233;par&#233;es</h3>",
            "<p>La plupart des photographies int&#233;ressantes existent "
            "d&#233;j&#224;. Elles ont &#233;t&#233; prises par des gens qui ne "
            "pensaient pas &#224; la courbure, souvent des ann&#233;es plus "
            "t&#244;t, et il serait absurde d'exiger d'eux un protocole "
            "qu'ils ne connaissaient pas. Ce qu'on peut exiger, en revanche, "
            "c'est qu'ils n'aient rien d&#233;truit&#160;: le fichier brut et "
            "ses m&#233;tadonn&#233;es suffisent &#224; presque tout "
            "reconstituer.</p>",
            "<p>La s&#233;paration a un second effet, utile. Celui qui "
            "d&#233;clenche ne sait pas ce que le calcul donnera&#160;; celui "
            "qui calcule n'&#233;tait pas l&#224;. Aucun des deux ne peut "
            "orienter l'autre.</p>",
            "<h3>X1.2 Pourquoi des sources ind&#233;pendantes</h3>",
            "<p>L'erreur la plus fr&#233;quente dans ce domaine n'est pas une "
            "erreur de calcul&#160;: c'est un param&#232;tre lu dans l'image "
            "qu'on pr&#233;tend juger. On estime la hauteur d'un b&#226;timent "
            "&#224; sa taille apparente, puis on constate que la portion "
            "visible correspond &#8212; &#233;videmment, puisque la hauteur en "
            "a &#233;t&#233; d&#233;duite. Le tableau&#160;2 nomme donc, pour "
            "chaque param&#232;tre, la source ext&#233;rieure qui doit le "
            "fournir.</p>",
            "<h3>X1.3 Pourquoi le coefficient est trait&#233; &#224; part</h3>",
            "<p>Le tableau&#160;4 est la raison de toute la section&#160;8.3. "
            "Sur le cas de r&#233;f&#233;rence, un m&#232;tre d'erreur sur la "
            "hauteur d'&#339;il d&#233;place la pr&#233;diction de "
            "%s&#8239;m et cent m&#232;tres sur la distance de %s&#8239;m, "
            "quand l'ignorance du coefficient en vaut &#224; elle seule "
            "%s&#8239;m. Toute la difficult&#233; de l'analyse a posteriori "
            "tient dans ce d&#233;s&#233;quilibre, et c'est pourquoi une "
            "valeur estim&#233;e ne peut pas &#234;tre pr&#233;sent&#233;e "
            "comme une mesure&#160;: ce serait cacher la seule incertitude qui "
            "compte."
            % (n(abs(dh), 1), n(u_d, 1), n(u_k, 1)),
            "<h3>X1.4 Pourquoi la m&#233;thode ne d&#233;clare jamais une "
            "observation impossible</h3>",
            "<p>La hauteur masqu&#233;e tend vers z&#233;ro quand le "
            "coefficient tend vers 1. Il existe donc, pour toute hauteur "
            "d'&#339;il, toute cible et toute distance, une valeur du "
            "coefficient inf&#233;rieure &#224; 1 qui rend la cible visible. "
            "&#201;crire qu'une observation est g&#233;om&#233;triquement "
            "impossible serait faux, et le premier lecteur comp&#233;tent le "
            "verrait. Ce qui est vrai et v&#233;rifiable, c'est le coefficient "
            "exig&#233; et la longueur sur laquelle il devrait tenir.</p>",
            "<h3>X1.5 D'o&#249; viennent les bornes du coefficient</h3>",
            "<p>Les coefficients mesur&#233;s pr&#232;s du sol s'&#233;tendent "
            "de &#8722;4 &#224; +16 (r&#233;f.&#160;7)&#160;; sous couverture "
            "nuageuse, de &#8722;2 &#224; +5. Ces valeurs extr&#234;mes sont "
            "obtenues sur des trajets courts, dans la couche o&#249; le "
            "gradient thermique est le plus violent. C'est pourquoi la "
            "section&#160;9.6.2 demande la longueur de maintien&#160;: un "
            "coefficient de 0,9 mesur&#233; sur deux cents m&#232;tres et un "
            "coefficient de 0,9 tenu sur cinquante kilom&#232;tres ne sont pas "
            "le m&#234;me &#233;nonc&#233;.</p>",
            "<h3>X1.6 Pourquoi le seuil de 40&#8239;m au-dessus de l'eau</h3>",
            "<p>Le conduit d'&#233;vaporation est pilot&#233; par le gradient "
            "d'humidit&#233; imm&#233;diatement au-dessus de la surface, non "
            "par la temp&#233;rature. Il d&#233;passe rarement quelques "
            "dizaines de m&#232;tres d'&#233;paisseur, mais il est "
            "fr&#233;quent&#160;: aux basses latitudes, il est pr&#233;sent la "
            "majeure partie du temps. Un rayon qui rase l'eau le traverse par "
            "construction, et le profil thermique moyen ne dit rien de ce qui "
            "s'y passe. D'o&#249; 11.2, qui rend le verdict non concluant "
            "plut&#244;t que de choisir une valeur.</p>",
            "<h3>X1.7 Ce que la m&#233;thode ne fait pas</h3>",
            "<p>Elle ne mesure pas le rayon de la Terre&#160;: elle teste la "
            "compatibilit&#233; d'une image avec une valeur pos&#233;e. Elle ne "
            "d&#233;partage pas non plus deux hypoth&#232;ses de forme, ce qui "
            "demanderait un jeu d'observations et non une photographie. Elle "
            "r&#233;pond &#224; une question &#233;troite, et c'est ce qui lui "
            "permet d'y r&#233;pondre.</p>",
        ])
    return "\n".join([
        h2_annexe(fr),
        "<h3>X1.1 Why two separate phases</h3>",
        "<p>Most of the interesting photographs already exist. They were taken "
        "by people who were not thinking about curvature, often years earlier, "
        "and it would be absurd to require of them a protocol they had never "
        "heard of. What can be required is that they destroyed nothing: the raw "
        "file and its metadata are enough to reconstruct almost everything.</p>",
        "<p>The separation has a second, useful effect. The person who releases "
        "the shutter does not know what the computation will give; the person "
        "who computes was not there. Neither can steer the other.</p>",
        "<h3>X1.2 Why independent sources</h3>",
        "<p>The commonest error in this field is not an arithmetic one: it is a "
        "parameter read off the very image under judgement. A building's height "
        "is estimated from its apparent size, and the visible portion is then "
        "found to match &#8212; of course it does, since the height was derived "
        "from it. Table&#160;2 therefore names, for each parameter, the outside "
        "source that must supply it.</p>",
        "<h3>X1.3 Why the coefficient is treated apart</h3>",
        "<p>Table&#160;4 is the reason for the whole of section&#160;8.3. On "
        "the reference case, one metre of error in eye height moves the "
        "prediction by %s&#8239;m and a hundred metres of distance by "
        "%s&#8239;m, while ignorance of the coefficient is worth %s&#8239;m on "
        "its own. The entire difficulty of a posteriori analysis lies in that "
        "imbalance, and it is why an estimated value cannot be presented as a "
        "measurement: doing so would hide the only uncertainty that matters.</p>"
        % (n(abs(dh), 1), n(u_d, 1), n(u_k, 1)),
        "<h3>X1.4 Why the method never declares an observation impossible</h3>",
        "<p>The hidden height tends to zero as the coefficient tends to 1. "
        "There exists therefore, for any eye height, any target and any "
        "distance, a coefficient below 1 that makes the target visible. To "
        "write that an observation is geometrically impossible would be false, "
        "and the first competent reader would see it. What is true and checkable "
        "is the required coefficient and the length over which it would have to "
        "hold.</p>",
        "<h3>X1.5 Where the bounds on the coefficient come from</h3>",
        "<p>Coefficients measured near the ground range from &#8722;4 to +16 "
        "(ref.&#160;7); under cloud cover, from &#8722;2 to +5. These extremes "
        "are obtained over short paths, in the layer where the thermal gradient "
        "is most violent. Hence 9.6.2 asks for the sustaining length: a "
        "coefficient of 0.9 measured over two hundred metres and a coefficient "
        "of 0.9 held over fifty kilometres are not the same statement.</p>",
        "<h3>X1.6 Why the 40&#8239;m threshold over water</h3>",
        "<p>The evaporation duct is governed by the humidity gradient "
        "immediately above the surface, not by temperature. It rarely exceeds a "
        "few tens of metres in thickness, but it is common: at low latitudes it "
        "is present most of the time. A ray grazing the water crosses it by "
        "construction, and the mean thermal profile says nothing about what "
        "happens inside. Hence 11.2, which returns an inconclusive verdict "
        "rather than choosing a value.</p>",
        "<h3>X1.7 What the method does not do</h3>",
        "<p>It does not measure the Earth's radius: it tests an image against a "
        "posited value. Nor does it decide between two hypotheses about shape, "
        "which would take a body of observations rather than one photograph. It "
        "answers a narrow question, and that is what lets it answer.</p>",
    ])


def corps(fr):
    titre = ("Analyse a posteriori d'une photographie d'objet "
             "&#233;loign&#233;" if fr else
             "A posteriori analysis of a photograph of a distant object")
    sous = ("Acquisition et analyse s&#233;par&#233;es &#8212; reconstitution "
            "des param&#232;tres par sources ind&#233;pendantes &#8212; "
            "cha&#238;ne de tra&#231;abilit&#233;" if fr else
            "Acquisition and analysis separated &#8212; parameters "
            "reconstructed from independent sources &#8212; traceability chain")
    resume = (
        '<div class="abstract"><span class="lab">%s</span>%s</div>' % (
            "En bref" if fr else "In brief",
            ("<p>Une photographie prise sans intention exp&#233;rimentale peut "
             "&#234;tre analys&#233;e, &#224; une condition&#160;: que le "
             "fichier d'origine existe. Tout le reste &#8212; distance, "
             "hauteurs, altitudes, optique, atmosph&#232;re &#8212; se "
             "reconstitue apr&#232;s coup, &#224; partir de sources qui ne "
             "d&#233;rivent pas de l'image.</p>"
             "<p>La m&#233;thode rend trois verdicts&#160;: compatible, "
             "incompatible, non concluante. Le dernier n'est pas un aveu "
             "d'impuissance&#160;: c'est ce qu'elle doit rendre chaque fois "
             "que les donn&#233;es ne tranchent pas, et la section&#160;11 dit "
             "&#224; quelles conditions exactes.</p>")
            if fr else
            ("<p>A photograph taken with no experimental intent can be "
             "analysed, on one condition: that the original file exists. "
             "Everything else &#8212; distance, heights, elevations, optics, "
             "atmosphere &#8212; is reconstructed afterwards, from sources that "
             "do not derive from the image.</p>"
             "<p>The method returns three verdicts: compatible, incompatible, "
             "inconclusive. The last is not an admission of defeat: it is what "
             "the method must return whenever the data do not decide, and "
             "section&#160;11 states under exactly which conditions.</p>")))
    return "\n\n".join([
        masthead(fr, titre, sous, "1.0"), resume,
        bloc_1(fr), bloc_2(fr), bloc_3(fr), bloc_4(fr), bloc_5(fr), bloc_6(fr),
        bloc_7(fr), bloc_8(fr), bloc_9(fr), bloc_10(fr), bloc_11(fr),
        bloc_x1(fr),
    ])


def main():
    controle()
    ecrire(CIBLE,
           "Analyse a posteriori d'une photographie &#8212; m&#233;thode "
           "d'essai",
           corps(True), corps(False))
    print("Écrit : %s (%d ko)"
          % (os.path.relpath(CIBLE, os.path.dirname(PROTOCOLES)),
             os.path.getsize(CIBLE) // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
