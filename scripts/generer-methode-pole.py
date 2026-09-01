#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Méthode d'essai « Hauteur du pôle céleste en fonction de la distance au sol ».

Reprend l'intégralité du contenu technique du protocole 1.3 et le remet dans
l'ordre de sections normalisé (scripts/methode_essai.py). Le raisonnement passe
en annexe X1 ; le corps ne garde que des exigences numérotées.

L'observable est la hauteur du centre de rotation du ciel au-dessus de
l'horizontale vraie, portée contre la distance au sol parcourue vers le sud —
jamais contre la latitude, qui est elle-même définie par cette hauteur.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from methode_essai import (PROTOCOLES, clause, ecrire, encadre, h2, h2_annexe,
                           ligne, masthead, mil, nb, tableau)      # noqa: E402

CIBLE = os.path.join(PROTOCOLES, "pole-celeste-bilingue.html")

KM_PAR_DEGRE = 111.194
BUDGET = 0.09           # degrés, 1 σ
ECART_POLAIRE = 0.65    # degrés
REFRACTION = 58.3       # secondes d'arc, coefficient de cot(a)
SEUIL_LATITUDE = 61.4   # degrés — au-dessous, la pente azimutale ne peut valoir 1
R_TERRE = 6371.0

BUDGET_POSTES = [
    ("Rep&#233;rage du centre de rotation", "Location of the rotation centre", 0.03),
    ("Rides r&#233;siduelles de la nappe", "Residual ripples on the surface", 0.05),
    ("Distorsion du grand-angle", "Wide-angle distortion", 0.06),
    ("R&#233;fraction r&#233;siduelle au-dessus de 30&#176;",
     "Residual refraction above 30&#176;", 0.02),
    ("R&#233;fraction r&#233;siduelle &#224; 10&#176;",
     "Residual refraction at 10&#176;", 0.018),
]
BASES = [(200, 0.032), (800, 0.132), (1200, 0.244), (1500, 0.437),
         (2200, 0.968), (2600, 1.644)]
PENTES = [(0.0, 10007, 0.318), (20.0, 7784, 0.409), (40.0, 5560, 0.573),
          (55.0, 3892, 0.819), (60.0, 3336, 0.955), (61.4, 3186, 1.002),
          (70.0, 2224, 1.432)]
CHAMPS = [(8, 112.6, 56.3), (14, 81.2, 40.6), (20, 61.9, 31.0),
          (24, 53.1, 26.6), (35, 37.8, 18.9)]
DEVIATIONS = [("plaine r&#233;guli&#232;re", "regular plain", 5, 0.15),
              ("relief mod&#233;r&#233;", "moderate relief", 15, 0.46),
              ("montagne", "mountain", 40, 1.24),
              ("extr&#234;me document&#233;", "documented extreme", 60, 1.85)]
AUSTRAL = [("Sph&#232;re", "Sphere", "SUD", "SOUTH", 33.5),
           ("Plan azimutal, H = 3 000 km", "Azimuthal plane, H = 3 000 km",
            "NORD", "NORTH", 12.3),
           ("Plan azimutal, H = 4 500 km", "Azimuthal plane, H = 4 500 km",
            "NORD", "NORTH", 18.1),
           ("Plan azimutal, H = 6 000 km", "Azimuthal plane, H = 6 000 km",
            "NORD", "NORTH", 23.6),
           ("Plan azimutal, H = 9 000 km", "Azimuthal plane, H = 9 000 km",
            "NORD", "NORTH", 33.2)]
GLOBAL = [(0, 60.0, 52.2), (1000, 51.0, 44.8), (2000, 42.0, 38.9),
          (3000, 33.0, 34.2), (4000, 24.0, 30.4), (5000, 15.0, 27.3)]


def controle():
    quad = math.sqrt(sum(v ** 2 for _, _, v in BUDGET_POSTES))
    assert abs(quad - BUDGET) < 0.005, quad
    # La pente azimutale maximale vaut R/(2r), atteinte en H = r.
    for lat, r0, pente in PENTES:
        assert abs(R_TERRE / (2 * r0) - pente) < 0.003, (lat, pente)
    # Le seuil : la pente ne peut valoir 1 que si r0 <= R/2.
    assert abs(PENTES[5][1] - R_TERRE / 2) < 3, PENTES[5]
    # Le champ vertical doit valoir deux fois la latitude.
    for f, champ, lat in CHAMPS:
        assert abs(champ / 2 - lat) < 0.1, f
    # La correction de réfraction aux deux hauteurs citées.
    assert abs(REFRACTION / 3600 / math.tan(math.radians(45)) - 0.016) < 0.001
    assert abs(REFRACTION / 3600 / math.tan(math.radians(10)) - 0.092) < 0.002
    # La déviation de la verticale, convertie en distance au sol.
    for _, _, sec, km in DEVIATIONS:
        assert abs(sec / 3600 * KM_PAR_DEGRE - km) < 0.02, sec
    return quad


def t_budget(fr):
    lignes = ['    <tr><td>%s</td><td class="n">%s&#176;</td></tr>'
              % (a if fr else b, nb(v, 3, fr)) for a, b, v in BUDGET_POSTES]
    lignes.append('    <tr class="hi"><td><strong>%s</strong></td>'
                  '<td class="n"><strong>%s&#176;</strong></td></tr>'
                  % ("Total quadratique (1 &#963;)" if fr
                     else "Quadratic total (1 &#963;)", nb(BUDGET, 2, fr)))
    return lignes


def t_bases(fr):
    def verdict(km, res):
        s = res / BUDGET
        if fr:
            return ("ind&#233;tectable" if s < 1 else "insuffisant" if s < 2.5
                    else "limite" if s < 4 else "minimum acceptable" if s < 6
                    else "confortable" if s < 15 else "d&#233;cisif")
        return ("undetectable" if s < 1 else "insufficient" if s < 2.5
                else "marginal" if s < 4 else "acceptable minimum" if s < 6
                else "comfortable" if s < 15 else "decisive")
    return [ligne(["%s km" % mil(km, fr), nb(res, 3, fr) + "&#176;",
                   nb(res / BUDGET, 1, fr), verdict(km, res)],
                  km == 1500) for km, res in BASES]


def t_pentes(fr):
    return [ligne([nb(lat, 1, fr) + "&#176;", "%s km" % mil(r0, fr),
                   nb(p, 3, fr),
                   ("non" if p >= 1.0 else "oui") if fr
                   else ("no" if p >= 1.0 else "yes")],
                  abs(lat - SEUIL_LATITUDE) < 0.01)
            for lat, r0, p in PENTES]


def t_champs(fr):
    return [ligne(["%d mm" % f, nb(c, 1, fr) + "&#176;", nb(l, 1, fr) + "&#176;"],
                  f == 14) for f, c, l in CHAMPS]


def t_deviations(fr):
    return [ligne([a if fr else b, "%d&#8243;" % s, nb(s / 3600, 4, fr) + "&#176;",
                   nb(km, 2, fr) + " km"]) for a, b, s, km in DEVIATIONS]


def t_austral(fr):
    return [ligne([a if fr else b, d if fr else e, nb(h, 1, fr) + "&#176;"],
                  h == 33.5) for a, b, d, e, h in AUSTRAL]


def t_global(fr):
    return [ligne(["%s km" % mil(s, fr), nb(sp, 1, fr) + "&#176;",
                   nb(pl, 1, fr) + "&#176;",
                   ("+" if pl - sp > 0 else "&#8722;") + nb(abs(pl - sp), 1, fr)
                   + "&#176;"]) for s, sp, pl in GLOBAL]


def corps(fr):
    T = []
    A = T.append
    A(masthead(fr,
               "Hauteur du p&#244;le c&#233;leste" if fr
               else "Altitude of the celestial pole",
               ("D&#233;termination de la pente de la hauteur du p&#244;le contre la "
                "distance au sol" if fr else
                "Determination of the slope of pole altitude against ground "
                "distance"), "2.0"))

    A(h2(1, fr))
    if fr:
        A(clause("1.1", "La pr&#233;sente m&#233;thode d&#233;termine la "
                 "<strong>pente</strong> de la hauteur du p&#244;le c&#233;leste "
                 "au-dessus de l'horizontale vraie, port&#233;e contre la "
                 "<strong>distance au sol</strong> parcourue le long d'une ligne "
                 "nord-sud."))
        A(clause("1.2", "La variable ind&#233;pendante est la distance au sol "
                 "relev&#233;e &#224; l'odom&#232;tre. <strong>La latitude n'est "
                 "jamais employ&#233;e comme variable ind&#233;pendante</strong> "
                 "(voir X1.1)."))
        A(clause("1.3", "Elle comporte trois d&#233;terminations "
                 "ind&#233;pendantes&#160;: la direction du centre de rotation "
                 "austral (8.2), la pente locale (8.3) et l'ajustement global "
                 "(8.4)."))
        A(clause("1.4", "Elle produit une pente en degr&#233;s par kilom&#232;tre et "
                 "son incertitude. Elle ne conclut sur aucun mod&#232;le."))
        A(clause("1.5", "Les valeurs sont exprim&#233;es en unit&#233;s SI, les "
                 "angles en degr&#233;s."))
    else:
        A(clause("1.1", "This method determines the <strong>slope</strong> of the "
                 "celestial pole's altitude above the true horizontal, plotted against "
                 "the <strong>ground distance</strong> travelled along a north-south "
                 "line."))
        A(clause("1.2", "The independent variable is the ground distance read from an "
                 "odometer. <strong>Latitude is never used as an independent "
                 "variable</strong> (see X1.1)."))
        A(clause("1.3", "It comprises three independent determinations: the direction "
                 "of the southern rotation centre (8.2), the local slope (8.3) and the "
                 "global fit (8.4)."))
        A(clause("1.4", "It produces a slope in degrees per kilometre and its "
                 "uncertainty. It concludes on no model."))
        A(clause("1.5", "Values are expressed in SI units, angles in degrees."))

    A(h2(2, fr))
    A(clause("2.1", "JCGM 100:2008 (GUM)."))
    A(clause("2.2", "ISO/IEC 17025:2017."))
    A(clause("2.3", "M&#233;thode d'essai &#171;&#160;D&#233;pression de l'horizon "
             "marin&#160;&#187;, section 05, pour l'&#233;talonnage par retournement."
             if fr else
             "Test method &#8220;Dip of the sea horizon&#8221;, section 05, for "
             "reversal calibration."))
    A(clause("2.4", "&#201;ph&#233;m&#233;rides d'un service reconnu, pour la "
             "correction de r&#233;fraction." if fr else
             "Ephemerides from a recognised service, for the refraction correction."))

    A(h2(3, fr))
    if fr:
        A("<p>3.1 <strong>p&#244;le c&#233;leste</strong> &#8212; centre des arcs "
          "d&#233;crits par les &#233;toiles sur une pose longue.</p>")
        A("<p>3.2 <strong>hauteur du p&#244;le</strong>, <code>h</code>, "
          "<em>degr&#233;s</em> &#8212; angle du p&#244;le c&#233;leste au-dessus de "
          "l'horizontale vraie, celle-ci &#233;tant d&#233;finie par le fil &#224; "
          "plomb et non par l'horizon visible.</p>")
        A("<p>3.3 <strong>horizon artificiel</strong> &#8212; nappe liquide libre, "
          "perpendiculaire au fil &#224; plomb par construction.</p>")
        A("<p>3.4 <strong>distance au sol</strong>, <code>s</code>, <em>km</em> "
          "&#8212; distance parcourue vers le sud depuis la station de "
          "r&#233;f&#233;rence, relev&#233;e &#224; l'odom&#232;tre.</p>")
        A("<p>3.5 <strong>d&#233;viation de la verticale</strong> &#8212; &#233;cart "
          "entre le fil &#224; plomb et la normale &#224; l'ellipso&#239;de.</p>")
    else:
        A("<p>3.1 <strong>celestial pole</strong> &#8212; centre of the arcs traced by "
          "stars on a long exposure.</p>")
        A("<p>3.2 <strong>pole altitude</strong>, <code>h</code>, <em>degrees</em> "
          "&#8212; angle of the celestial pole above the true horizontal, the latter "
          "defined by the plumb line and not by the visible horizon.</p>")
        A("<p>3.3 <strong>artificial horizon</strong> &#8212; free liquid surface, "
          "perpendicular to the plumb line by construction.</p>")
        A("<p>3.4 <strong>ground distance</strong>, <code>s</code>, <em>km</em> "
          "&#8212; distance travelled southward from the reference station, read from "
          "an odometer.</p>")
        A("<p>3.5 <strong>deflection of the vertical</strong> &#8212; departure between "
          "the plumb line and the normal to the ellipsoid.</p>")

    A(h2(4, fr))
    if fr:
        A(clause("4.1", "La hauteur du p&#244;le est mesur&#233;e par pose longue "
                 "au-dessus d'un horizon artificiel, l'angle entre l'astre et son "
                 "reflet valant deux fois la hauteur."))
        A(clause("4.2", "L'op&#233;ration est r&#233;p&#233;t&#233;e sur au moins "
                 "quatre stations align&#233;es nord-sud, trois nuits chacune."))
        A(clause("4.3", "La direction du centre de rotation est relev&#233;e depuis "
                 "au moins une station de l'h&#233;misph&#232;re sud."))
        A(clause("4.4", "La hauteur est port&#233;e contre la distance au sol et la "
                 "pente ajust&#233;e par moindres carr&#233;s pond&#233;r&#233;s."))
        A(clause("4.5", "Le r&#233;sultat d'essai est la pente, son incertitude, et "
                 "la direction observ&#233;e du centre austral."))
    else:
        A(clause("4.1", "The pole altitude is measured by long exposure over an "
                 "artificial horizon, the angle between the body and its reflection "
                 "being twice the altitude."))
        A(clause("4.2", "The operation is repeated at at least four stations aligned "
                 "north-south, three nights each."))
        A(clause("4.3", "The direction of the rotation centre is recorded from at "
                 "least one southern-hemisphere station."))
        A(clause("4.4", "Altitude is plotted against ground distance and the slope "
                 "fitted by weighted least squares."))
        A(clause("4.5", "The test result is the slope, its uncertainty, and the "
                 "observed direction of the southern centre."))

    A(h2(5, fr))
    if fr:
        A(clause("5.1", "Une surface sph&#233;rique impose une pente de "
                 "<strong>1&#176; par %s km</strong>, en tout lieu et sans "
                 "param&#232;tre ajustable. Un plan azimutal &#233;quidistant donne "
                 "<code>h = arctan(H/r)</code>, dont la pente vaut au plus "
                 "<code>R/(2r&#8320;)</code>." % nb(KM_PAR_DEGRE, 3, fr)))
        A(clause("5.2", "Cette borne d&#233;cide de la longueur de base "
                 "n&#233;cessaire. Au-dessous de %s&#176; de latitude, la pente "
                 "azimutale ne peut pas atteindre 1 quelle que soit <code>H</code>, "
                 "et une base courte suffit &#224; condition d'&#233;pingler "
                 "<code>r&#8320;</code> par une mesure est-ouest (7.4)."
                 % nb(SEUIL_LATITUDE, 1, fr)))
        A(tableau("Tableau 1 &#8212; Pente maximale que le mod&#232;le azimutal peut "
                  "atteindre, toutes valeurs de <code>H</code> confondues. La ligne "
                  "surlign&#233;e est le seuil.",
                  ["latitude", "r&#8320;", "pente maximale",
                   "une seule pente suffit-elle&#160;?"], t_pentes(fr)))
        A(clause("5.3", "Sans mesure est-ouest, la base doit &#234;tre longue&#160;: "
                 "un ajustement azimutal &#224; deux param&#232;tres imite une droite "
                 "d'autant mieux que la base est courte."))
        A(tableau("Tableau 2 &#8212; R&#233;sidu maximal du meilleur ajustement "
                  "azimutal &#224; deux param&#232;tres, contre la longueur de base. "
                  "Budget d'erreur %s&#176;." % nb(BUDGET, 2, fr),
                  ["base nord-sud", "r&#233;sidu maximal", "&#963;", "verdict"],
                  t_bases(fr)))
    else:
        A(clause("5.1", "A spherical surface imposes a slope of <strong>1&#176; per "
                 "%s km</strong>, everywhere and with no adjustable parameter. An "
                 "equidistant azimuthal plane gives <code>h = arctan(H/r)</code>, whose "
                 "slope is at most <code>R/(2r&#8320;)</code>."
                 % nb(KM_PAR_DEGRE, 3, fr)))
        A(clause("5.2", "That bound decides the baseline length required. Below "
                 "%s&#176; of latitude the azimuthal slope cannot reach 1 whatever "
                 "<code>H</code>, and a short baseline suffices provided "
                 "<code>r&#8320;</code> is pinned by an east-west measurement (7.4)."
                 % nb(SEUIL_LATITUDE, 1, fr)))
        A(tableau("Table 1 &#8212; Maximum slope the azimuthal model can reach, over "
                  "all values of <code>H</code>. The highlighted row is the threshold.",
                  ["latitude", "r&#8320;", "maximum slope",
                   "does one slope suffice?"], t_pentes(fr)))
        A(clause("5.3", "Without an east-west measurement the baseline must be long: a "
                 "two-parameter azimuthal fit imitates a straight line the better, the "
                 "shorter the baseline."))
        A(tableau("Table 2 &#8212; Maximum residual of the best two-parameter azimuthal "
                  "fit, against baseline length. Error budget %s&#176;."
                  % nb(BUDGET, 2, fr),
                  ["north-south baseline", "maximum residual", "&#963;", "verdict"],
                  t_bases(fr)))

    A(h2(6, fr))
    if fr:
        A(clause("6.1", "<strong>Horizon artificiel</strong>&#160;: plateau large et "
                 "peu profond, rempli d'eau ou d'une huile sombre et visqueuse, "
                 "abrit&#233; du vent."))
        A(clause("6.2", "<strong>Bo&#238;tier</strong> et objectif grand-angle. Le "
                 "champ vertical doit couvrir <strong>deux fois</strong> la hauteur du "
                 "p&#244;le."))
        A(tableau("Tableau 3 &#8212; Champ vertical requis, capteur 24&#215;36.",
                  ["focale", "champ vertical", "latitude maximale couverte"],
                  t_champs(fr)))
        A(clause("6.3", "<strong>Tr&#233;pied</strong> stable et d&#233;clenchement "
                 "&#224; distance."))
        A(clause("6.4", "<strong>Odom&#232;tre</strong> pour la distance au sol entre "
                 "stations."))
        A(clause("6.5", "<strong>Solution de repli</strong>&#160;: inclinom&#232;tre "
                 "avec &#233;talonnage par retournement selon 2.3 &#8212; une pose "
                 "bo&#238;tier normal, une pose bo&#238;tier tourn&#233; &#224; "
                 "180&#176; sur la m&#234;me embase, la moyenne des deux lectures "
                 "&#233;liminant le biais de montage."))
        A(clause("6.6", "Le profil de distorsion de l'objectif doit &#234;tre "
                 "disponible et appliqu&#233;."))
    else:
        A(clause("6.1", "<strong>Artificial horizon</strong>: a wide shallow tray "
                 "filled with water or a dark viscous oil, sheltered from wind."))
        A(clause("6.2", "<strong>Camera body</strong> and wide-angle lens. The vertical "
                 "field shall cover <strong>twice</strong> the pole altitude."))
        A(tableau("Table 3 &#8212; Vertical field required, 24&#215;36 sensor.",
                  ["focal length", "vertical field", "maximum latitude covered"],
                  t_champs(fr)))
        A(clause("6.3", "<strong>Tripod</strong>, stable, and remote release."))
        A(clause("6.4", "<strong>Odometer</strong> for ground distance between "
                 "stations."))
        A(clause("6.5", "<strong>Fallback</strong>: inclinometer with reversal "
                 "calibration per 2.3 &#8212; one exposure body normal, one body turned "
                 "180&#176; on the same base, the mean of the two readings eliminating "
                 "the mounting bias."))
        A(clause("6.6", "The lens distortion profile shall be available and applied."))

    A(h2(7, fr))
    if fr:
        A(clause("7.1", "<strong>Quatre stations au minimum</strong> sur une ligne "
                 "nord-sud, trois nuits chacune. Deux param&#232;tres libres "
                 "s'ajustent exactement sur trois points, qui ne testent donc "
                 "rien."))
        A(clause("7.2", "Une station au moins doit &#234;tre situ&#233;e "
                 "<strong>sous 30&#176; de latitude</strong>."))
        A(clause("7.3", "<strong>Voie longue</strong> &#8212; sans mesure est-ouest, "
                 "la base nord-sud mesure au moins <strong>1 500 km</strong> "
                 "(tableau 2)."))
        A(clause("7.4", "<strong>Voie courte</strong> &#8212; avec une mesure "
                 "est-ouest &#233;pinglant <code>r&#8320;</code>, une base de 200 km "
                 "suffit &#224; condition que la station soit sous %s&#176; de "
                 "latitude (tableau 1). La voie est choisie et "
                 "d&#233;clar&#233;e <strong>avant</strong> la campagne."
                 % nb(SEUIL_LATITUDE, 1, fr)))
        A(clause("7.5", "Nappe au repos, abrit&#233;e, ciel d&#233;gag&#233; sur la "
                 "dur&#233;e de pose."))
    else:
        A(clause("7.1", "<strong>Four stations minimum</strong> on a north-south line, "
                 "three nights each. Two free parameters fit exactly on three points, "
                 "which therefore test nothing."))
        A(clause("7.2", "At least one station shall lie <strong>below 30&#176; of "
                 "latitude</strong>."))
        A(clause("7.3", "<strong>Long route</strong> &#8212; without an east-west "
                 "measurement, the north-south baseline is at least <strong>1 500 "
                 "km</strong> (Table 2)."))
        A(clause("7.4", "<strong>Short route</strong> &#8212; with an east-west "
                 "measurement pinning <code>r&#8320;</code>, a 200 km baseline suffices "
                 "provided the station is below %s&#176; of latitude (Table 1). The "
                 "route is chosen and declared <strong>before</strong> the campaign."
                 % nb(SEUIL_LATITUDE, 1, fr)))
        A(clause("7.5", "Surface at rest, sheltered, sky clear for the exposure "
                 "duration."))

    A(h2(8, fr, saut=True))
    if fr:
        A(clause("8.1", "<strong>Installer l'horizon artificiel.</strong> Laisser "
                 "reposer jusqu'&#224; disparition des rides. L'inclinaison moyenne de "
                 "la nappe doit rester sous 1,5&#8242;, soit 0,13 mm de "
                 "d&#233;nivellation sur un plateau de 30 cm."))
        A(clause("8.2", "<strong>Relever la direction du centre de rotation</strong> "
                 "depuis une station australe&#160;: pose longue, sans mesure d'angle. "
                 "Consigner <strong>nord</strong> ou <strong>sud</strong>."))
        A(clause("8.3", "<strong>Cadrer astre et reflet ensemble</strong>, l'astre "
                 "dans la moiti&#233; haute du cadre, son reflet dans la basse."))
        A(clause("8.4", "<strong>Poser par fractions</strong>&#160;: vingt &#224; "
                 "quarante minutes d'arcs au total, d&#233;coup&#233;es en sous-poses "
                 "de deux &#224; trois minutes, empil&#233;es ensuite. Comparer les "
                 "sous-poses entre elles&#160;: leur dispersion mesure la d&#233;rive "
                 "lente &#8212; &#233;vaporation, thermique, tassement du sol &#8212; "
                 "qui d&#233;place tout sans se voir."))
        A(clause("8.5", "<strong>R&#233;p&#233;ter trois nuits</strong> par station, "
                 "pour disposer d'une dispersion mesur&#233;e."))
        A(clause("8.6", "<strong>Relever la distance au sol</strong> &#224; "
                 "l'odom&#232;tre entre stations cons&#233;cutives. Consigner "
                 "s&#233;par&#233;ment la latitude GPS, sans l'employer au "
                 "calcul."))
        A(encadre("Le pi&#232;ge de circularit&#233;",
                  "  <p><strong>Ne jamais rapporter la hauteur du p&#244;le &#224; "
                  "l'horizon visible.</strong> La ligne d'horizon est abaiss&#233;e "
                  "sous l'horizontale vraie d'une quantit&#233; dont la valeur "
                  "d&#233;pend du mod&#232;le que l'on cherche &#224; tester. La "
                  "r&#233;f&#233;rence est le fil &#224; plomb, mat&#233;rialis&#233; "
                  "par la nappe.</p>"))
        A(clause("8.7", "<strong>Crit&#232;res de rejet.</strong> Une station est "
                 "&#233;cart&#233;e uniquement sur un crit&#232;re d&#233;clar&#233; "
                 "d'avance &#8212; couverture nuageuse, nappe agit&#233;e, montage "
                 "d&#233;plac&#233; &#8212; consign&#233; au journal la nuit "
                 "m&#234;me. <strong>Aucun &#233;cartement fond&#233; sur la valeur "
                 "obtenue.</strong>"))
    else:
        A(clause("8.1", "<strong>Set up the artificial horizon.</strong> Let it settle "
                 "until ripples vanish. The mean tilt of the surface shall stay below "
                 "1.5&#8242;, that is 0.13 mm of height difference over a 30 cm "
                 "tray."))
        A(clause("8.2", "<strong>Record the direction of the rotation centre</strong> "
                 "from a southern station: long exposure, no angle measurement. Record "
                 "<strong>north</strong> or <strong>south</strong>."))
        A(clause("8.3", "<strong>Frame body and reflection together</strong>, the body "
                 "in the upper half of the frame, its reflection in the lower."))
        A(clause("8.4", "<strong>Expose in fractions</strong>: twenty to forty minutes "
                 "of arcs in total, cut into sub-exposures of two to three minutes, "
                 "stacked afterwards. Compare sub-exposures with one another: their "
                 "scatter measures the slow drift &#8212; evaporation, thermal, ground "
                 "settling &#8212; which displaces everything without showing."))
        A(clause("8.5", "<strong>Repeat on three nights</strong> per station, to obtain "
                 "a measured scatter."))
        A(clause("8.6", "<strong>Record the ground distance</strong> by odometer "
                 "between consecutive stations. Record the GPS latitude separately, "
                 "without using it in the calculation."))
        A(encadre("The circularity trap",
                  "  <p><strong>Never refer the pole altitude to the visible "
                  "horizon.</strong> The horizon line is depressed below the true "
                  "horizontal by an amount whose value depends on the model under test. "
                  "The reference is the plumb line, materialised by the liquid "
                  "surface.</p>"))
        A(clause("8.7", "<strong>Rejection criteria.</strong> A station is discarded "
                 "only on a criterion declared in advance &#8212; cloud cover, disturbed "
                 "surface, mount displaced &#8212; logged the same night. <strong>No "
                 "rejection based on the value obtained.</strong>"))

    A(h2(9, fr))
    if fr:
        A(clause("9.1", "Mesurer l'angle entre les deux centres de rotation. Il vaut "
                 "<strong>deux fois</strong> la hauteur du p&#244;le. Convertir les "
                 "pixels en angle par le champ du capteur, apr&#232;s application du "
                 "profil de distorsion."))
        A(clause("9.2", "Corriger la r&#233;fraction&#160;: retrancher "
                 "<code>%s&#8243; &#215; cot(h)</code>. La correction vaut "
                 "%s&#176; &#224; 45&#176; de hauteur et %s&#176; &#224; 10&#176;."
                 % (nb(REFRACTION, 1, fr),
                    nb(REFRACTION / 3600 / math.tan(math.radians(45)), 3, fr),
                    nb(REFRACTION / 3600 / math.tan(math.radians(10)), 3, fr))))
        A(clause("9.3", "Ajuster <code>h(s)</code> contre la distance au sol par "
                 "moindres carr&#233;s pond&#233;r&#233;s par "
                 "<code>1/&#963;&#178;</code>, o&#249; <code>&#963;</code> est la "
                 "<strong>dispersion observ&#233;e</strong> des nuits d'une "
                 "m&#234;me station &#8212; non la valeur du budget. Un budget est une "
                 "pr&#233;vision&#160;; la dispersion est une mesure."))
        A(clause("9.4", "Comparer les mod&#232;les par <code>&#967;&#178;</code> par "
                 "degr&#233; de libert&#233;, un mod&#232;le &#224; deux "
                 "param&#232;tres en perdant un de plus qu'un mod&#232;le &#224; un "
                 "seul."))
        A(clause("9.5", "&#201;valuer l'incertitude selon 2.1, avec au minimum les "
                 "composantes du tableau 4."))
        A(tableau("Tableau 4 &#8212; Budget d'erreur, m&#233;thode &#224; horizon "
                  "artificiel, objectif 14 mm.", ["source", "contribution"],
                  t_budget(fr)))
    else:
        A(clause("9.1", "Measure the angle between the two rotation centres. It is "
                 "<strong>twice</strong> the pole altitude. Convert pixels to angle "
                 "using the sensor field, after applying the distortion profile."))
        A(clause("9.2", "Correct for refraction: subtract "
                 "<code>%s&#8243; &#215; cot(h)</code>. The correction is %s&#176; at "
                 "45&#176; altitude and %s&#176; at 10&#176;."
                 % (nb(REFRACTION, 1, fr),
                    nb(REFRACTION / 3600 / math.tan(math.radians(45)), 3, fr),
                    nb(REFRACTION / 3600 / math.tan(math.radians(10)), 3, fr))))
        A(clause("9.3", "Fit <code>h(s)</code> against ground distance by least squares "
                 "weighted by <code>1/&#963;&#178;</code>, where <code>&#963;</code> is "
                 "the <strong>observed scatter</strong> of the nights at one station "
                 "&#8212; not the budget value. A budget is a forecast; scatter is a "
                 "measurement."))
        A(clause("9.4", "Compare models by <code>&#967;&#178;</code> per degree of "
                 "freedom, a two-parameter model losing one more than a one-parameter "
                 "model."))
        A(clause("9.5", "Evaluate the uncertainty per 2.1, with at minimum the "
                 "components of Table 4."))
        A(tableau("Table 4 &#8212; Error budget, artificial horizon method, 14 mm "
                  "lens.", ["source", "contribution"], t_budget(fr)))

    A(h2(10, fr))
    if fr:
        A(clause("10.1", "Le rapport mentionne&#160;:"))
        A("<ul>\n  <li>date, heures UTC de d&#233;but et de fin de chaque pose&#160;;</li>\n"
          "  <li>coordonn&#233;es GPS de chaque station <em>et</em> distance nord-sud "
          "&#224; l'odom&#232;tre&#160;;</li>\n"
          "  <li>bo&#238;tier, objectif, focale, dimensions du capteur, profil de "
          "distorsion appliqu&#233;&#160;;</li>\n"
          "  <li>m&#233;thode employ&#233;e&#160;: horizon artificiel ou "
          "inclinom&#232;tre avec retournement&#160;;</li>\n"
          "  <li>liquide, abri, temps de repos&#160;;</li>\n"
          "  <li>position en pixels des deux centres de rotation&#160;;</li>\n"
          "  <li>hauteur avant et apr&#232;s correction de r&#233;fraction&#160;;</li>\n"
          "  <li>direction du centre austral&#160;: nord ou sud&#160;;</li>\n"
          "  <li>nombre de nuits et dispersion observ&#233;e par station&#160;;</li>\n"
          "  <li>la voie choisie au 7.3 ou 7.4, et la date de ce choix&#160;;</li>\n"
          "  <li>les fichiers bruts, publi&#233;s et accessibles.</li>\n</ul>")
        A(clause("10.2", "Le rapport <strong>ne conclut pas sur un mod&#232;le</strong>. "
                 "Il &#233;nonce la pente, son incertitude et la direction "
                 "observ&#233;e."))
    else:
        A(clause("10.1", "The report shall state:"))
        A("<ul>\n  <li>date, UTC start and end times of each exposure;</li>\n"
          "  <li>GPS coordinates of each station <em>and</em> north-south odometer "
          "distance;</li>\n"
          "  <li>body, lens, focal length, sensor dimensions, distortion profile "
          "applied;</li>\n"
          "  <li>method used: artificial horizon or inclinometer with reversal;</li>\n"
          "  <li>liquid, shelter, settling time;</li>\n"
          "  <li>pixel positions of the two rotation centres;</li>\n"
          "  <li>altitude before and after refraction correction;</li>\n"
          "  <li>direction of the southern centre: north or south;</li>\n"
          "  <li>number of nights and observed scatter per station;</li>\n"
          "  <li>the route chosen at 7.3 or 7.4, and the date of that choice;</li>\n"
          "  <li>the raw files, published and accessible.</li>\n</ul>")
        A(clause("10.2", "The report <strong>shall not conclude on a model</strong>. It "
                 "states the slope, its uncertainty and the observed direction."))

    A(h2(11, fr))
    if fr:
        A(clause("11.1", "<strong>Fid&#233;lit&#233;.</strong> Aucune &#233;tude "
                 "interlaboratoires n'a &#233;t&#233; conduite &#224; ce jour."))
        A(clause("11.2", "<strong>Biais.</strong> La d&#233;viation de la verticale "
                 "est syst&#233;matique par site et reste sous le budget de "
                 "%s&#176;." % nb(BUDGET, 2, fr)))
        A(tableau("Tableau 5 &#8212; D&#233;viation de la verticale selon le terrain, "
                  "et son &#233;quivalent en distance au sol.",
                  ["terrain", "d&#233;viation", "en degr&#233;s",
                   "&#233;quivalent au sol"], t_deviations(fr)))
        A(clause("11.3", "Sur une base de 200 km, l'erreur instrumentale domine "
                 "largement&#160;: 7,1&#160;% contre 0,1 &#224; 0,9&#160;% pour la "
                 "d&#233;viation."))
    else:
        A(clause("11.1", "<strong>Precision.</strong> No interlaboratory study has been "
                 "conducted to date."))
        A(clause("11.2", "<strong>Bias.</strong> Deflection of the vertical is "
                 "systematic per site and stays below the %s&#176; budget."
                 % nb(BUDGET, 2, fr)))
        A(tableau("Table 5 &#8212; Deflection of the vertical by terrain, and its "
                  "ground-distance equivalent.",
                  ["terrain", "deflection", "in degrees", "ground equivalent"],
                  t_deviations(fr)))
        A(clause("11.3", "Over a 200 km baseline the instrumental error dominates "
                 "widely: 7.1 per cent against 0.1 to 0.9 per cent for the "
                 "deflection."))

    A(h2_annexe(fr))
    if fr:
        A("<h3>X1.1 &#8212; Pourquoi une distance au sol, jamais une latitude</h3>")
        A("<p>Porter la hauteur du p&#244;le contre la latitude rend le test "
          "circulaire&#160;: la latitude astronomique <em>est d&#233;finie</em> par la "
          "hauteur du p&#244;le, et la latitude g&#233;od&#233;sique suppose "
          "l'ellipso&#239;de, c'est-&#224;-dire le mod&#232;le test&#233;. La "
          "d&#233;viation de la verticale (tableau 5) montre du reste qu'il existe "
          "<strong>deux</strong> latitudes, qui ne co&#239;ncident nulle part "
          "exactement. La distance au sol les &#233;vite toutes les deux.</p>")
        A("<h3>X1.2 &#8212; Ce que la m&#233;thode contraint, et ce qu'elle ne "
          "contraint pas</h3>")
        A("<p>Elle contraint les constructions o&#249; les astres sont des lumi&#232;res "
          "&#224; hauteur finie au-dessus d'un plan et o&#249; la latitude est "
          "port&#233;e par la distance &#224; un centre &#8212; la projection azimutale "
          "&#233;quidistante. Elle ne contraint pas les mod&#232;les o&#249; le ciel "
          "poss&#232;de sa propre cin&#233;matique, ni ceux o&#249; la rotation "
          "observ&#233;e n'est pas celle d'objets vus en ligne droite&#160;: "
          "<code>arctan(H/r)</code> ne s'y applique pas.</p>")
        A("<h3>X1.3 &#8212; Le centre de rotation austral</h3>")
        A("<p>Le test de direction est le moins co&#251;teux et le plus discriminant. "
          "Il ne porte pas sur une hauteur mais sur une <strong>direction</strong>, et "
          "aucune valeur de <code>H</code> ne d&#233;place un centre du nord vers le "
          "sud.</p>")
        A(tableau("Tableau X1.1 &#8212; Position pr&#233;dite du centre de rotation "
                  "pour un observateur &#224; 33,5&#176; de latitude sud.",
                  ["construction", "direction", "hauteur"], t_austral(fr)))
        A("<p>Remarquer la derni&#232;re ligne&#160;: &#224; <code>H</code> = 9 000 km "
          "la hauteur pr&#233;dite tombe presque juste, mais la direction reste "
          "oppos&#233;e.</p>")
        A("<p><strong>Port&#233;e du test.</strong> Il vaut contre les cartes "
          "azimutales &#224; centre unique. Une carte &#224; deux centres &#8212; un "
          "disque par h&#233;misph&#232;re &#8212; poss&#232;de un p&#244;le austral et "
          "y &#233;chappe&#160;; elle doit alors r&#233;pondre du parall&#232;le &#224; "
          "33,5&#176; sud, qui vaut 33 381 km sur une sph&#232;re et 86 284 km sur la "
          "carte azimutale, soit 2,58 fois plus. Cette partie-l&#224; se v&#233;rifie "
          "par les temps de vol commerciaux, sans aucune observation "
          "astronomique.</p>")
        A("<h3>X1.4 &#8212; L'ajustement global</h3>")
        A(tableau("Tableau X1.2 &#8212; Station de r&#233;f&#233;rence &#224; 60&#176;, "
                  "distances compt&#233;es vers le sud, meilleur ajustement azimutal "
                  "<code>H</code> = 4 300 km. Le r&#233;sidu change de signe&#160;: la "
                  "courbe coupe la droite au lieu de l'&#233;pouser.",
                  ["distance sud", "sph&#232;re", "plan azimutal", "r&#233;sidu"],
                  t_global(fr)))
        A("<h3>X1.5 &#8212; Pi&#232;ges observ&#233;s</h3>")
        A("<ul>\n"
          "  <li><strong>L'horizon visible comme r&#233;f&#233;rence.</strong> Le seul "
          "pi&#232;ge qui invalide compl&#232;tement un relev&#233;.</li>\n"
          "  <li><strong>Confondre l'&#233;toile polaire et le p&#244;le.</strong> "
          "%s&#176; d'&#233;cart, soit sept fois l'incertitude de la m&#233;thode.</li>\n"
          "  <li><strong>Ne travailler qu'&#224; haute latitude.</strong> La pente y "
          "perd sa force.</li>\n"
          "  <li><strong>Distorsion du grand-angle non corrig&#233;e.</strong> Elle "
          "atteint plusieurs degr&#233;s en bord de champ sur un fisheye.</li>\n"
          "  <li><strong>Nappe agit&#233;e.</strong> Une ride d'un degr&#233; "
          "d&#233;place le reflet de deux.</li>\n"
          "</ul>" % nb(ECART_POLAIRE, 2, fr))
    else:
        A("<h3>X1.1 &#8212; Why ground distance, never latitude</h3>")
        A("<p>Plotting pole altitude against latitude makes the test circular: "
          "astronomical latitude <em>is defined</em> by the pole's altitude, and "
          "geodetic latitude assumes the ellipsoid, that is, the model under test. "
          "Deflection of the vertical (Table 5) shows moreover that there are "
          "<strong>two</strong> latitudes, which coincide exactly nowhere. Ground "
          "distance avoids both.</p>")
        A("<h3>X1.2 &#8212; What the method constrains, and what it does not</h3>")
        A("<p>It constrains constructions where the stars are lights at finite height "
          "above a plane and where latitude is carried by distance from a centre "
          "&#8212; the equidistant azimuthal projection. It does not constrain models "
          "where the sky has its own kinematics, nor those where the observed rotation "
          "is not that of objects seen in a straight line: <code>arctan(H/r)</code> does "
          "not apply there.</p>")
        A("<h3>X1.3 &#8212; The southern rotation centre</h3>")
        A("<p>The direction test is the cheapest and the most discriminating. It bears "
          "not on an altitude but on a <strong>direction</strong>, and no value of "
          "<code>H</code> moves a centre from north to south.</p>")
        A(tableau("Table X1.1 &#8212; Predicted position of the rotation centre for an "
                  "observer at 33.5&#176; south.",
                  ["construction", "direction", "altitude"], t_austral(fr)))
        A("<p>Note the last row: at <code>H</code> = 9 000 km the predicted altitude "
          "almost lands, but the direction remains opposite.</p>")
        A("<p><strong>Scope of the test.</strong> It holds against single-centre "
          "azimuthal maps. A two-centre map &#8212; one disc per hemisphere &#8212; has "
          "a southern pole and escapes it; it must then answer for the parallel at "
          "33.5&#176; south, which is 33 381 km on a sphere and 86 284 km on the "
          "azimuthal map, 2.58 times longer. That part is checked from commercial "
          "flight times, with no astronomical observation at all.</p>")
        A("<h3>X1.4 &#8212; The global fit</h3>")
        A(tableau("Table X1.2 &#8212; Reference station at 60&#176;, distances counted "
                  "southward, best azimuthal fit <code>H</code> = 4 300 km. The residual "
                  "changes sign: the curve crosses the line instead of following it.",
                  ["southward distance", "sphere", "azimuthal plane", "residual"],
                  t_global(fr)))
        A("<h3>X1.5 &#8212; Observed pitfalls</h3>")
        A("<ul>\n"
          "  <li><strong>The visible horizon as reference.</strong> The only pitfall "
          "that voids a record entirely.</li>\n"
          "  <li><strong>Confusing Polaris with the pole.</strong> %s&#176; apart, seven "
          "times the method's uncertainty.</li>\n"
          "  <li><strong>Working only at high latitude.</strong> The slope loses its "
          "force there.</li>\n"
          "  <li><strong>Uncorrected wide-angle distortion.</strong> Several degrees at "
          "the field edge on a fisheye.</li>\n"
          "  <li><strong>Disturbed surface.</strong> A one-degree ripple displaces the "
          "reflection by two.</li>\n"
          "</ul>" % nb(ECART_POLAIRE, 2, fr))

    return "\n\n".join(T)


def main():
    quad = controle()
    ecrire(CIBLE, "Hauteur du p&#244;le c&#233;leste &#8212; m&#233;thode d'essai",
           corps(True), corps(False))
    print("Méthode d'essai écrite : content/protocoles/pole-celeste-bilingue.html")
    print("  budget quadratique recalculé : %.3f°" % quad)
    print("  seuil de latitude (pente azimutale = 1) : %.1f°" % SEUIL_LATITUDE)
    print("  structure : 1→11 + annexe X1, contrôle de récit passé")
    return 0


if __name__ == "__main__":
    sys.exit(main())
