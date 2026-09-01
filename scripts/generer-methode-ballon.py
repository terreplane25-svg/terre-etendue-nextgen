#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Méthode d'essai « Dépression de l'horizon depuis un ballon stratosphérique ».

Reprend l'intégralité du contenu technique du protocole 1.1 et le remet dans
l'ordre de sections normalisé (scripts/methode_essai.py). Le raisonnement passe
en annexe X1 ; le corps ne garde que des exigences numérotées.

L'observable n'est pas la dépression δ mais l'angle 2δ entre deux points
diamétralement opposés de l'horizon, mesurés dans une seule image. Une
inclinaison de la nacelle ajoute ε d'un côté et retranche ε de l'autre : la
somme vaut 2δ quelle que soit l'inclinaison. Aucune référence verticale n'est
donc nécessaire à bord, ce qui rend la mesure possible sur une nacelle qui
balance et qui tourne.

Ce que ce protocole a d'unique dans le dossier
──────────────────────────────────────────────
La réfraction n'y est pas supposée mais **mesurée**. L'invariant de Bouguer
donne cos δ = n₀(R+t) / [n₁(R+h)] : la correction ne dépend que de l'indice aux
deux extrémités du rayon, et l'indice se déduit de la pression et de la
température par n = 1 + 77,6×10⁻⁶ P/T. Ces quatre grandeurs sont relevées — au
sol à l'heure du lâcher, à bord par la sonde. Aucun coefficient k n'apparaît.

Une erreur trouvée dans le protocole déposé
───────────────────────────────────────────
La version 1.1 annonçait un budget d'erreur de 1,09′ par image. Ses propres
postes — 0,65 · 0,50 · 0,30 · 0,25 · 0,25 — donnent une somme quadratique de
0,94′. L'écart est de 16 %, dans le sens qui SURESTIME le bruit : la conclusion
n'en était pas affectée, mais le chiffre était faux et le rapport signal sur
bruit sous-évalué. Il passe de 317 à 366.

Sur la vérification des chiffres
────────────────────────────────
controle() recalcule la colonne géométrique par arccos(R/(R+h)), les distances
d'horizon, la cohérence interne du tableau (correction = réfracté − géométrique,
2δ = 2×réfracté), la variation entre 2 et 30 km, le budget quadratique et le
rapport signal sur bruit. La colonne réfractée provient de l'atmosphère standard
1976 et est reprise du document déposé : elle est donnée comme donnée, non
recalculée ici, et le document le dit.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from methode_essai import (PROTOCOLES, clause, ecrire, encadre, h2, h2_annexe,
                           ligne, masthead, mil, nb, tableau)      # noqa: E402

CIBLE = os.path.join(PROTOCOLES, "ballon-bilingue.html")

R = 6371.0
# altitude km, δ géométrique °, δ réfracté °, horizon km
DEPRESSION = [(2, 1.435, 1.320, 160), (5, 2.269, 2.106, 252),
              (10, 3.208, 3.018, 357), (15, 3.928, 3.731, 437),
              (20, 4.534, 4.347, 505), (25, 5.068, 4.894, 565),
              (30, 5.549, 5.389, 619)]
PLAFONDS = [(10, 204), (15, 289), (20, 363), (25, 429), (30, 488), (35, 543)]
BUDGET_POSTES = [
    ("Point&#233; du bord d'horizon", "Horizon edge pointing", 0.65),
    ("Flou de boug&#233; r&#233;siduel apr&#232;s tri", "Residual motion blur after sorting", 0.50),
    ("R&#233;sidu de distorsion", "Distortion residual", 0.30),
    ("&#201;chelle angulaire", "Angular scale", 0.25),
    ("R&#233;fraction r&#233;siduelle", "Residual refraction", 0.25),
]
OPTIQUES = [("Pi HQ + 8 mm", 32.8, 16.4, 0.65, "recommand&#233;", "recommended"),
            ("Pi HQ + 12 mm", 22.2, 11.1, 0.44, "meilleure &#233;chelle",
             "better scale"),
            ("APS-C + 24 mm", 36.0, 18.0, 0.54, "excellent si la masse le permet",
             "excellent if mass allows"),
            ("Plein format + 50 mm", 27.0, 13.5, 0.41,
             "masse et consommation &#233;lev&#233;es", "high mass and power")]
RELIEF = [(5, -4.9, -12.6, -26.0), (10, -3.4, -8.7, -17.6),
          (20, -2.4, -6.0, -12.1), (30, -1.9, -4.8, -9.7)]
CADENCE, OBTURATION = 5, 1000
R_MIN, R_MAX = 6200, 6550


def delta_geometrique(h_km):
    return math.degrees(math.acos(R / (R + h_km)))


def horizon(h_km):
    return math.sqrt(2 * R * h_km + h_km ** 2)


def controle():
    """Recalcule ce qui est calculable, vérifie la cohérence du reste."""
    for h, geo, refr, hor in DEPRESSION:
        assert abs(delta_geometrique(h) - geo) < 0.004, (h, delta_geometrique(h))
        assert abs(horizon(h) - hor) < 1.5, (h, horizon(h))
        assert refr < geo, h                       # la réfraction abaisse δ
        corr = (refr - geo) * 60
        assert -12.5 < corr < -6.5, (h, corr)      # entre 7 et 12 minutes d'arc
    variation = (2 * DEPRESSION[-1][2] - 2 * DEPRESSION[0][2]) * 60
    assert abs(variation - 488) < 2, variation
    # Le protocole 1.1 annonçait un total quadratique de 1,09′ qui ne suit pas
    # de ses propres postes : 0,65 · 0,50 · 0,30 · 0,25 · 0,25 donnent 0,94′.
    # L'erreur SURESTIMAIT le bruit de 16 % ; la conclusion en était inchangée,
    # mais le chiffre était faux et le rapport signal sur bruit sous-évalué.
    quad = math.sqrt(sum(v ** 2 for _, _, v in BUDGET_POSTES))
    assert abs(quad - 0.94) < 0.01, quad
    snr = variation / (quad * math.sqrt(2))
    assert abs(snr - 366) < 5, snr
    return variation, quad, snr


def t_depression(fr):
    lignes = []
    for h, geo, refr, hor in DEPRESSION:
        lignes.append(ligne(["%d km" % h, nb(geo, 3, fr) + "&#176;",
                             nb(refr, 3, fr) + "&#176;",
                             nb((refr - geo) * 60, 1, fr) + "&#8242;",
                             "%s km" % mil(hor, fr),
                             nb(2 * refr, 3, fr) + "&#176;"], h == 30))
    return lignes


def t_plafonds(fr):
    def verdict(v):
        if fr:
            return ("d&#233;j&#224; d&#233;cisif" if v < 250 else "d&#233;cisif"
                    if v < 400 else "plafond recommand&#233;" if v < 450
                    else "confortable" if v < 500 else "gain marginal")
        return ("already decisive" if v < 250 else "decisive" if v < 400
                else "recommended ceiling" if v < 450 else "comfortable"
                if v < 500 else "marginal gain")
    return [ligne(["%d km" % p, "%d&#8242;" % v, "0&#8242;", verdict(v)],
                  p == 25) for p, v in PLAFONDS]


def t_optiques(fr):
    return [ligne([nom, nb(ch, 1, fr) + "&#176;", nb(demi, 1, fr) + "&#176;",
                   nb(ech, 2, fr) + "&#8242;/px", vfr if fr else ven],
                  nom.endswith("8 mm"))
            for nom, ch, demi, ech, vfr, ven in OPTIQUES]


def t_budget(fr):
    lignes = ['    <tr><td>%s</td><td class="n">%s&#8242;</td></tr>'
              % (a if fr else b, nb(v, 2, fr)) for a, b, v in BUDGET_POSTES]
    quad = math.sqrt(sum(v ** 2 for _, _, v in BUDGET_POSTES))
    lignes.append('    <tr class="hi"><td><strong>%s</strong></td>'
                  '<td class="n"><strong>%s&#8242;</strong></td></tr>'
                  % ("Total quadratique (1 &#963;), par image" if fr
                     else "Quadratic total (1 &#963;), per image", nb(quad, 2, fr)))
    return lignes


def t_relief(fr):
    return [ligne(["%d km" % h] + [nb(v, 1, fr) + "&#8242;" for v in (a, b, c)])
            for h, a, b, c in RELIEF]


def corps(fr):
    variation, quad, snr = controle()
    T = []
    A = T.append
    A(masthead(fr,
               "D&#233;pression de l'horizon depuis un ballon" if fr
               else "Horizon dip from a balloon",
               ("D&#233;termination de l'angle entre deux points oppos&#233;s de "
                "l'horizon, en fonction de l'altitude" if fr else
                "Determination of the angle between two opposite points of the "
                "horizon, as a function of altitude"), "2.0"))

    # ── 1 Domaine d'application ─────────────────────────────────────────────
    A(h2(1, fr))
    if fr:
        A(clause("1.1", "La pr&#233;sente m&#233;thode d&#233;termine "
                 "<code>2&#948;</code>, l'angle entre deux points "
                 "diam&#233;tralement oppos&#233;s de l'horizon mesur&#233;s dans une "
                 "<strong>seule image</strong>, en fonction de l'altitude, au cours de "
                 "la mont&#233;e d'un ballon libre non habit&#233;."))
        A(clause("1.2", "L'observable est <code>2&#948;</code> et non la "
                 "d&#233;pression <code>&#948;</code>&#160;: une inclinaison de la "
                 "nacelle ajoute <code>&#949;</code> d'un c&#244;t&#233; et retranche "
                 "<code>&#949;</code> de l'autre. <strong>Aucune r&#233;f&#233;rence "
                 "verticale n'est requise &#224; bord.</strong>"))
        A(clause("1.3", "Le crit&#232;re porte sur la <strong>variation</strong> de "
                 "<code>2&#948;</code> au cours de la mont&#233;e, non sur sa valeur. "
                 "Le d&#233;calage instrumental dispara&#238;t dans la "
                 "diff&#233;rence."))
        A(clause("1.4", "La r&#233;fraction est <strong>mesur&#233;e et non "
                 "suppos&#233;e</strong> (9.2). Aucun coefficient de r&#233;fraction "
                 "n'appara&#238;t dans cette m&#233;thode."))
        A(clause("1.5", "Elle produit la s&#233;rie <code>2&#948;(h)</code>, la valeur "
                 "ajust&#233;e du rayon <code>R</code>, et leurs incertitudes."))
        A(clause("1.6", "<em>Avertissement.</em> Un ballon libre non habit&#233; est "
                 "r&#233;glement&#233;. La pr&#233;sente m&#233;thode ne fournit aucun "
                 "conseil juridique&#160;: s'adresser &#224; l'autorit&#233; de "
                 "l'aviation civile comp&#233;tente (7.1)."))
    else:
        A(clause("1.1", "This method determines <code>2&#948;</code>, the angle "
                 "between two diametrically opposite points of the horizon measured in "
                 "a <strong>single image</strong>, as a function of altitude, during "
                 "the ascent of a free unmanned balloon."))
        A(clause("1.2", "The observable is <code>2&#948;</code> and not the dip "
                 "<code>&#948;</code>: a tilt of the gondola adds <code>&#949;</code> "
                 "on one side and subtracts <code>&#949;</code> on the other. "
                 "<strong>No vertical reference is required on board.</strong>"))
        A(clause("1.3", "The criterion bears on the <strong>variation</strong> of "
                 "<code>2&#948;</code> during the ascent, not on its value. The "
                 "instrumental offset cancels in the difference."))
        A(clause("1.4", "Refraction is <strong>measured, not assumed</strong> (9.2). "
                 "No refraction coefficient appears in this method."))
        A(clause("1.5", "It produces the series <code>2&#948;(h)</code>, the fitted "
                 "value of the radius <code>R</code>, and their uncertainties."))
        A(clause("1.6", "<em>Warning.</em> A free unmanned balloon is regulated. This "
                 "method gives no legal advice: apply to the competent civil aviation "
                 "authority (7.1)."))

    # ── 2 Documents de référence ────────────────────────────────────────────
    A(h2(2, fr))
    A(clause("2.1", "JCGM 100:2008 (GUM)."))
    A(clause("2.2", "BOMFORD, G. (1980). <em>Geodesy</em>, 4<sup>e</sup> &#233;d. "
             "Oxford University Press." if fr else
             "BOMFORD, G. (1980). <em>Geodesy</em>, 4th ed. Oxford University Press."))
    A(clause("2.3", "BRUNNER, F. K. (1984). <em>Geodetic Refraction</em>. "
             "Springer-Verlag, Berlin."))
    A(clause("2.4", "YOUNG, A. T. (2004). Sunset science. IV. Low-altitude refraction. "
             "<em>The Observatory</em>, 124, 201&#8211;215."))
    A(clause("2.5", "EDL&#201;N, B. (1966). The refractive index of air. "
             "<em>Metrologia</em>, 2(2), 71&#8211;80."))
    A(clause("2.6", "<em>U.S. Standard Atmosphere, 1976.</em> NOAA/NASA/USAF, "
             "Washington."))

    # ── 3 Terminologie ──────────────────────────────────────────────────────
    A(h2(3, fr))
    if fr:
        A("<p>3.1 <strong>d&#233;pression de l'horizon</strong>, <code>&#948;</code>, "
          "<em>degr&#233;s</em> &#8212; angle entre l'horizontale locale et la ligne "
          "d'horizon.</p>")
        A("<p>3.2 <strong>observable</strong>, <code>2&#948;</code>, "
          "<em>degr&#233;s</em> &#8212; somme des deux angles mesur&#233;s entre l'axe "
          "de l'instrument et les deux bords d'horizon oppos&#233;s.</p>")
        A("<p>3.3 <strong>d&#233;calage instrumental</strong>, <code>C</code>, "
          "<em>degr&#233;s</em> &#8212; constante fix&#233;e par la g&#233;om&#233;trie "
          "du montage, ind&#233;pendante de l'altitude, ajust&#233;e comme "
          "param&#232;tre libre.</p>")
        A("<p>3.4 <strong>di&#232;dre</strong> &#8212; deux miroirs de premi&#232;re "
          "surface formant une ar&#234;te &#224; 90&#176;, qui ram&#232;nent deux "
          "azimuts oppos&#233;s sur les deux moiti&#233;s d'un m&#234;me capteur.</p>")
        A("<p>3.5 <strong>point de tangence</strong>, altitude <code>t</code>, "
          "<em>km</em> &#8212; point o&#249; le rayon lumineux rase la surface.</p>")
        A("<p>3.6 <strong>altitude orthom&#233;trique</strong> &#8212; altitude "
          "au-dessus du g&#233;o&#239;de, et non de l'ellipso&#239;de. C'est celle "
          "qu'exige le calcul.</p>")
    else:
        A("<p>3.1 <strong>horizon dip</strong>, <code>&#948;</code>, <em>degrees</em> "
          "&#8212; angle between the local horizontal and the horizon line.</p>")
        A("<p>3.2 <strong>observable</strong>, <code>2&#948;</code>, "
          "<em>degrees</em> &#8212; sum of the two angles measured between the "
          "instrument axis and the two opposite horizon edges.</p>")
        A("<p>3.3 <strong>instrumental offset</strong>, <code>C</code>, "
          "<em>degrees</em> &#8212; constant set by the geometry of the mount, "
          "independent of altitude, fitted as a free parameter.</p>")
        A("<p>3.4 <strong>dihedral</strong> &#8212; two front-surface mirrors forming a "
          "90&#176; edge, bringing two opposite azimuths onto the two halves of a "
          "single sensor.</p>")
        A("<p>3.5 <strong>tangent point</strong>, altitude <code>t</code>, <em>km</em> "
          "&#8212; point where the light ray grazes the surface.</p>")
        A("<p>3.6 <strong>orthometric altitude</strong> &#8212; altitude above the "
          "geoid, not the ellipsoid. It is the one the calculation requires.</p>")

    # ── 4 Résumé de la méthode ──────────────────────────────────────────────
    A(h2(4, fr))
    if fr:
        A(clause("4.1", "Un instrument &#224; di&#232;dre est &#233;talonn&#233; sur un "
                 "champ d'&#233;toiles avant le vol, puis immobilis&#233; (8.4)."))
        A(clause("4.2", "Le ballon monte &#224; 4&#8211;5 m/s. Une image est acquise "
                 "toutes les %d secondes, chacune contenant les deux bords d'horizon "
                 "oppos&#233;s." % CADENCE))
        A(clause("4.3", "Chaque image est appari&#233;e &#224; son altitude "
                 "orthom&#233;trique par l'horloge et la trace GNSS."))
        A(clause("4.4", "<code>&#945;<sub>A</sub></code> et "
                 "<code>&#945;<sub>B</sub></code> sont mesur&#233;s au crit&#232;re de "
                 "point&#233; du 9.1&#160;; leur somme donne "
                 "<code>2&#948; + C</code>."))
        A(clause("4.5", "La r&#233;fraction est retir&#233;e par l'invariant de "
                 "Bouguer, &#224; partir des pression et temp&#233;rature "
                 "relev&#233;es au sol et &#224; bord (9.2)."))
        A(clause("4.6", "Les deux mod&#232;les sont ajust&#233;s sur la m&#234;me "
                 "s&#233;rie et compar&#233;s par <code>&#967;&#178;</code> par "
                 "degr&#233; de libert&#233; (9.5)."))
        A(clause("4.7", "Le r&#233;sultat d'essai est la variation de "
                 "<code>2&#948;</code> entre le plancher et le plafond atteints, avec "
                 "son incertitude, et la valeur ajust&#233;e de <code>R</code>."))
    else:
        A(clause("4.1", "A dihedral instrument is calibrated on a star field before "
                 "flight, then immobilised (8.4)."))
        A(clause("4.2", "The balloon rises at 4&#8211;5 m/s. One image is acquired "
                 "every %d seconds, each containing both opposite horizon edges."
                 % CADENCE))
        A(clause("4.3", "Each image is paired with its orthometric altitude through the "
                 "clock and the GNSS track."))
        A(clause("4.4", "<code>&#945;<sub>A</sub></code> and "
                 "<code>&#945;<sub>B</sub></code> are measured by the pointing criterion "
                 "of 9.1; their sum gives <code>2&#948; + C</code>."))
        A(clause("4.5", "Refraction is removed through the Bouguer invariant, from the "
                 "pressures and temperatures recorded on the ground and on board "
                 "(9.2)."))
        A(clause("4.6", "The two models are fitted to the same series and compared by "
                 "<code>&#967;&#178;</code> per degree of freedom (9.5)."))
        A(clause("4.7", "The test result is the variation of <code>2&#948;</code> "
                 "between the floor and ceiling reached, with its uncertainty, and the "
                 "fitted value of <code>R</code>."))

    # ── 5 Intérêt et emploi ─────────────────────────────────────────────────
    A(h2(5, fr))
    if fr:
        A(clause("5.1", "La d&#233;pression cro&#238;t comme la racine de l'altitude "
                 "aux basses hauteurs. Le ballon traverse continûment toute la plage "
                 "et fournit des centaines de points&#160;: <strong>c'est la forme de "
                 "la courbe qui tranche</strong>, et elle ne d&#233;pend d'aucun "
                 "r&#233;glage instrumental."))
        A(clause("5.2", "Une surface sph&#233;rique de rayon <code>R</code> impose "
                 "<code>cos &#948; = R/(R+h)</code>. Une surface plane impose "
                 "<code>&#948;</code> = 0 &#224; toute altitude&#160;: c'est une "
                 "propri&#233;t&#233; de la g&#233;om&#233;trie projective, l'horizon "
                 "&#233;tant le point de fuite du plan."))
        A(tableau("Tableau 1 &#8212; D&#233;pression pr&#233;dite, atmosph&#232;re "
                  "standard 1976, point de tangence au niveau de la mer. La "
                  "colonne r&#233;fract&#233;e est reprise du calcul en "
                  "atmosph&#232;re standard&#160;; la colonne "
                  "g&#233;om&#233;trique se recalcule par "
                  "<code>arccos(R/(R+h))</code>.",
                  ["altitude", "g&#233;om&#233;trique", "avec r&#233;fraction",
                   "correction", "horizon &#224;", "2&#948; mesur&#233;"],
                  t_depression(fr)))
        A(clause("5.3", "Entre 2 et 30 km, <code>2&#948;</code> passe de "
                 "%s&#176; &#224; %s&#176;, soit <strong>%s minutes d'arc</strong> de "
                 "variation. La surface plane en pr&#233;dit z&#233;ro."
                 % (nb(2 * DEPRESSION[0][2], 3, fr), nb(2 * DEPRESSION[-1][2], 3, fr),
                    nb(variation, 0, fr))))
        A(tableau("Tableau 2 &#8212; Variation attendue selon le plafond atteint. Le "
                  "vol n'a pas besoin d'aller haut pour trancher&#160;: il a besoin de "
                  "monter.",
                  ["mont&#233;e de 2 km &#224;", "variation de 2&#948;",
                   "surface plane", "verdict"], t_plafonds(fr)))
    else:
        A(clause("5.1", "The dip grows as the square root of altitude at low heights. "
                 "The balloon crosses the whole range continuously and yields hundreds "
                 "of points: <strong>it is the shape of the curve that decides</strong>, "
                 "and it depends on no instrumental setting."))
        A(clause("5.2", "A spherical surface of radius <code>R</code> imposes "
                 "<code>cos &#948; = R/(R+h)</code>. A plane surface imposes "
                 "<code>&#948;</code> = 0 at every altitude: a property of projective "
                 "geometry, the horizon being the vanishing point of the plane."))
        A(tableau("Table 1 &#8212; Predicted dip, 1976 standard atmosphere, tangent "
                  "point at sea level. The refracted column is taken from the standard "
                  "atmosphere calculation; the geometric column recomputes as "
                  "<code>arccos(R/(R+h))</code>.",
                  ["altitude", "geometric", "with refraction", "correction",
                   "horizon at", "2&#948; measured"], t_depression(fr)))
        A(clause("5.3", "Between 2 and 30 km, <code>2&#948;</code> goes from "
                 "%s&#176; to %s&#176;, that is <strong>%s arcminutes</strong> of "
                 "variation. The plane surface predicts zero."
                 % (nb(2 * DEPRESSION[0][2], 3, fr), nb(2 * DEPRESSION[-1][2], 3, fr),
                    nb(variation, 0, fr))))
        A(tableau("Table 2 &#8212; Expected variation by ceiling reached. The flight "
                  "does not need to go high to decide: it needs to climb.",
                  ["ascent from 2 km to", "variation of 2&#948;", "plane surface",
                   "verdict"], t_plafonds(fr)))

    # ── 6 Appareillage ──────────────────────────────────────────────────────
    A(h2(6, fr, saut=True))
    if fr:
        A(clause("6.1", "<strong>Une cam&#233;ra unique</strong> &#224; capteur de "
                 "dimensions connues, capable d'&#233;crire en brut. Le demi-champ "
                 "vertical doit contenir <code>&#948;</code> au plafond vis&#233;, le "
                 "balancement de la nacelle (&#177;8&#176; en pr&#233;vision "
                 "pessimiste) et une marge."))
        A(tableau("Tableau 3 &#8212; Choix optique.",
                  ["capteur et focale", "champ vertical", "demi-champ",
                   "&#233;chelle", "verdict"], t_optiques(fr)))
        A(clause("6.2", "<strong>Un di&#232;dre</strong> de deux miroirs de "
                 "premi&#232;re surface formant une ar&#234;te &#224; 90&#176;, "
                 "plac&#233; devant l'objectif."))
        A(clause("6.3", "<strong>Un support d'un seul tenant</strong>, usin&#233; ou en "
                 "composite &#224; faible dilatation. La rigidit&#233; entre les deux "
                 "miroirs est la seule pi&#232;ce m&#233;caniquement critique."))
        A(clause("6.4", "<strong>Un hublot plan</strong>, ou un bo&#238;tier "
                 "scell&#233; avec dessiccant."))
        A(clause("6.5", "<strong>Un r&#233;cepteur GNSS</strong> configur&#233; en mode "
                 "dynamique <em>Airborne &lt; 2g</em>. Les modules civils coupent la "
                 "restitution au-dessus de 18 km si ce mode n'est pas "
                 "s&#233;lectionn&#233;."))
        A(clause("6.6", "<strong>Un capteur de pression</strong> barom&#233;trique, "
                 "plage utile v&#233;rifi&#233;e, et une <strong>sonde de "
                 "temp&#233;rature</strong> ext&#233;rieure &#224; l'abri du "
                 "rayonnement direct."))
        A(clause("6.7", "<strong>Deux traceurs</strong> sur technologies distinctes et "
                 "alimentations s&#233;par&#233;es, journalisant aussi la pression et "
                 "l'altitude."))
        A(clause("6.8", "<strong>Piles au lithium primaire</strong>, non "
                 "rechargeables&#160;: elles tiennent &#224; &#8722;60 &#176;C. "
                 "Isolation en polystyr&#232;ne extrud&#233;, &#233;lectronique "
                 "group&#233;e. <strong>Deux enregistrements</strong> ind&#233;pendants "
                 "des images."))
        A(clause("6.9", "<strong>Parachute et cha&#238;ne de suspension</strong>, "
                 "dimensionn&#233;s pour la masse et la vitesse de chute vis&#233;e."))
    else:
        A(clause("6.1", "<strong>A single camera</strong> with a sensor of known "
                 "dimensions, able to write raw. The vertical half-field shall contain "
                 "<code>&#948;</code> at the intended ceiling, the gondola swing "
                 "(&#177;8&#176; as a pessimistic allowance) and a margin."))
        A(tableau("Table 3 &#8212; Optical choice.",
                  ["sensor and focal length", "vertical field", "half-field", "scale",
                   "verdict"], t_optiques(fr)))
        A(clause("6.2", "<strong>A dihedral</strong> of two front-surface mirrors "
                 "forming a 90&#176; edge, placed before the objective."))
        A(clause("6.3", "<strong>A one-piece mount</strong>, machined or in "
                 "low-expansion composite. Rigidity between the two mirrors is the only "
                 "mechanically critical part."))
        A(clause("6.4", "<strong>A plane window</strong>, or a sealed enclosure with "
                 "desiccant."))
        A(clause("6.5", "<strong>A GNSS receiver</strong> set to dynamic model "
                 "<em>Airborne &lt; 2g</em>. Civil modules stop reporting above 18 km if "
                 "that mode is not selected."))
        A(clause("6.6", "<strong>A barometric pressure sensor</strong>, useful range "
                 "verified, and an <strong>outside temperature probe</strong> shielded "
                 "from direct radiation."))
        A(clause("6.7", "<strong>Two trackers</strong> on distinct technologies and "
                 "separate power supplies, also logging pressure and altitude."))
        A(clause("6.8", "<strong>Primary lithium cells</strong>, non-rechargeable: they "
                 "hold at &#8722;60 &#176;C. Extruded polystyrene insulation, "
                 "electronics grouped together. <strong>Two independent "
                 "recordings</strong> of the images."))
        A(clause("6.9", "<strong>Parachute and suspension chain</strong>, sized for the "
                 "mass and the intended descent rate."))

    # ── 7 Conditions d'essai ────────────────────────────────────────────────
    A(h2(7, fr))
    if fr:
        A(clause("7.1", "<strong>Autorisation.</strong> Les r&#233;gimes de "
                 "d&#233;claration, les zones interdites et le pr&#233;avis sont "
                 "fix&#233;s par l'autorit&#233; de l'aviation civile. Ils sont "
                 "obtenus avant toute autre &#233;tape."))
        A(clause("7.2", "<strong>Ciel d&#233;gag&#233;</strong> sur un rayon de "
                 "600 km autour de la trajectoire pr&#233;vue, et couche limite peu "
                 "charg&#233;e. <strong>Un horizon de nuages n'est pas "
                 "l'horizon</strong> (11.3)."))
        A(clause("7.3", "<strong>Vitesse ascensionnelle</strong> de 4 &#224; 5 m/s, "
                 "r&#233;gl&#233;e par le gonflage. Plus lent donne plus d'images dans "
                 "la tranche utile&#160;; plus rapide &#233;loigne moins le point de "
                 "chute."))
        A(clause("7.4", "<strong>Plafond recommand&#233; 25 km</strong> (tableau 2). "
                 "Au-del&#224; de 35 km le gain devient marginal et les contraintes "
                 "augmentent."))
        A(clause("7.5", "<strong>Temps calme.</strong> La r&#233;fraction est "
                 "trait&#233;e en atmosph&#232;re &#224; sym&#233;trie "
                 "sph&#233;rique&#160;; un gradient horizontal marqu&#233; &#8212; "
                 "front, courant-jet &#8212; la mettrait en d&#233;faut. La situation "
                 "m&#233;t&#233;orologique est consign&#233;e."))
    else:
        A(clause("7.1", "<strong>Authorisation.</strong> Declaration regimes, forbidden "
                 "zones and notice periods are set by the civil aviation authority. "
                 "They are obtained before any other step."))
        A(clause("7.2", "<strong>Clear sky</strong> within a 600 km radius of the "
                 "planned trajectory, and a lightly loaded boundary layer. <strong>A "
                 "horizon of cloud is not the horizon</strong> (11.3)."))
        A(clause("7.3", "<strong>Ascent rate</strong> of 4 to 5 m/s, set by inflation. "
                 "Slower gives more images in the useful band; faster carries the "
                 "landing point less far."))
        A(clause("7.4", "<strong>Recommended ceiling 25 km</strong> (Table 2). Beyond "
                 "35 km the gain becomes marginal and the constraints increase."))
        A(clause("7.5", "<strong>Calm weather.</strong> Refraction is treated in a "
                 "spherically symmetric atmosphere; a marked horizontal gradient "
                 "&#8212; a front, a jet stream &#8212; would break it. The "
                 "meteorological situation is recorded."))

    # ── 8 Mode opératoire ───────────────────────────────────────────────────
    A(h2(8, fr, saut=True))
    if fr:
        A(encadre("Ce qui ne se rattrape jamais",
                  "  <p>Un vol de ballon ne se rejoue pas. Six &#233;tapes rendent les "
                  "pr&#233;c&#233;dentes irr&#233;cup&#233;rables&#160;:</p>\n"
                  "  <ul>\n"
                  "    <li>le <strong>r&#233;glage du GNSS en mode "
                  "a&#233;roport&#233;</strong> &#8212; sans altitude, il n'y a pas de "
                  "mesure&#160;;</li>\n"
                  "    <li>l'<strong>&#233;talonnage astrom&#233;trique avant "
                  "vol</strong> &#8212; sans lui, les images sont des dessins&#160;;</li>\n"
                  "    <li>l'<strong>immobilisation de la mise au point</strong> "
                  "&#8212; toute retouche annule l'&#233;talonnage&#160;;</li>\n"
                  "    <li><strong>P et T au sol</strong> &#224; l'heure du "
                  "l&#226;cher&#160;;</li>\n"
                  "    <li>la <strong>protection contre le givre</strong> &#8212; un "
                  "hublot givr&#233; supprime toutes les images au-dessus de "
                  "10 km&#160;;</li>\n"
                  "    <li>l'<strong>horodatage du protocole</strong>, s'il est "
                  "pr&#233;enregistr&#233; (X1.4).</li>\n"
                  "  </ul>"))
        A(clause("8.1", "<strong>Fixer le crit&#232;re de point&#233;</strong> du bord "
                 "d'horizon (9.1) et ne plus en changer. Sa constance importe plus que "
                 "son choix&#160;: un biais commun se lit dans <code>C</code>, un biais "
                 "qui d&#233;rive avec l'altitude se confond avec le signal."))
        A(clause("8.2", "<strong>Configurer le GNSS</strong> en mode <em>Airborne &lt; "
                 "2g</em>, puis <strong>relire la configuration</strong> du module au "
                 "sol pour la v&#233;rifier."))
        A(clause("8.3", "<strong>Incliner le di&#232;dre</strong> de "
                 "<code>&#946;</code> &#8776; 4&#176; vers le bas, ce qui centre les "
                 "deux horizons dans leurs demi-champs &#224; mi-parcours. Les deux "
                 "axes restant &#233;galement abaiss&#233;s, la sym&#233;trie est "
                 "pr&#233;serv&#233;e et l'abaissement s'ajoute &#224; "
                 "<code>C</code>."))
        A(clause("8.4", "<strong>&#201;talonner sur le ciel</strong>&#160;: nuit "
                 "claire, montage complet mont&#233; comme il volera, quelques poses sur "
                 "un champ &#233;toil&#233;. La r&#233;solution astrom&#233;trique de "
                 "chaque demi-champ donne l'<strong>&#233;chelle angulaire</strong>, le "
                 "<strong>profil de distorsion</strong> et l'<strong>angle exact entre "
                 "les deux axes</strong>. Puis immobiliser la bague."))
        A(clause("8.5", "<strong>Relever P et T au sol</strong> &#224; l'heure du "
                 "l&#226;cher, avec un instrument dont l'incertitude est connue."))
        A(clause("8.6", "<strong>D&#233;marrer l'acquisition vingt minutes avant le "
                 "l&#226;cher.</strong> Ces images &#224; <code>h</code> &#8776; 0 "
                 "mesurent directement le d&#233;calage <code>C</code>."))
        A(clause("8.7", "<strong>Acquisition&#160;:</strong> une image toutes les %d s, "
                 "obturation 1/%d s ou plus courte, <strong>exposition fixe</strong> "
                 "d&#233;termin&#233;e avant vol, format brut, sans recadrage ni "
                 "correction automatique." % (CADENCE, OBTURATION)))
        A(clause("8.8", "<strong>Consigner l'heure UTC du l&#226;cher</strong> &#224; la "
                 "seconde, pour appairer images et positions."))
        A(clause("8.9", "<strong>La mont&#233;e est la mesure.</strong> Les images de "
                 "descente ne sont pas exploitables et ne sont pas m&#233;lang&#233;es "
                 "&#224; celles de la mont&#233;e."))
        A(clause("8.10", "<strong>M&#233;thode B, contr&#244;le ind&#233;pendant&#160;:"
                 "</strong> une seconde cam&#233;ra &#224; tr&#232;s grand champ "
                 "point&#233;e vers le bas. L'horizon y forme une courbe ferm&#233;e "
                 "dont le rayon angulaire vaut 90&#176; &#8722; <code>&#948;</code>, "
                 "insensible &#224; l'inclinaison. Un d&#233;saccord entre A et B est "
                 "une information, pas une g&#234;ne."))
        A(clause("8.11", "<strong>R&#233;&#233;talonner apr&#232;s r&#233;cup&#233;ration"
                 "</strong>, sur le ciel, <strong>sans rien avoir "
                 "d&#233;mont&#233;</strong>. Si l'angle entre axes a boug&#233;, il "
                 "faut le savoir."))
    else:
        A(encadre("What can never be recovered",
                  "  <p>A balloon flight cannot be replayed. Six steps make the "
                  "preceding ones unrecoverable:</p>\n"
                  "  <ul>\n"
                  "    <li>setting the <strong>GNSS to airborne mode</strong> &#8212; "
                  "without altitude there is no measurement;</li>\n"
                  "    <li><strong>astrometric calibration before flight</strong> "
                  "&#8212; without it the images are drawings;</li>\n"
                  "    <li><strong>locking the focus</strong> &#8212; any adjustment "
                  "voids the calibration;</li>\n"
                  "    <li><strong>ground P and T</strong> at release time;</li>\n"
                  "    <li><strong>protection against icing</strong> &#8212; a frosted "
                  "window removes every image above 10 km;</li>\n"
                  "    <li><strong>timestamping the protocol</strong>, if it is "
                  "pre-registered (X1.4).</li>\n"
                  "  </ul>"))
        A(clause("8.1", "<strong>Fix the pointing criterion</strong> for the horizon "
                 "edge (9.1) and do not change it. Its constancy matters more than its "
                 "choice: a common bias shows in <code>C</code>, a bias drifting with "
                 "altitude is confounded with the signal."))
        A(clause("8.2", "<strong>Configure the GNSS</strong> to <em>Airborne &lt; "
                 "2g</em>, then <strong>read the configuration back</strong> from the "
                 "module on the ground to verify it."))
        A(clause("8.3", "<strong>Tilt the dihedral</strong> by <code>&#946;</code> "
                 "&#8776; 4&#176; downward, centring both horizons in their half-fields "
                 "at mid-ascent. Both axes being equally lowered, the symmetry is "
                 "preserved and the lowering simply adds to <code>C</code>."))
        A(clause("8.4", "<strong>Calibrate on the sky</strong>: clear night, the "
                 "complete assembly mounted as it will fly, a few exposures on a star "
                 "field. Astrometric solution of each half-field gives the "
                 "<strong>angular scale</strong>, the <strong>distortion profile</strong> "
                 "and the <strong>exact angle between the two axes</strong>. Then lock "
                 "the ring."))
        A(clause("8.5", "<strong>Record ground P and T</strong> at release time, with an "
                 "instrument of known uncertainty."))
        A(clause("8.6", "<strong>Start acquisition twenty minutes before release.</strong> "
                 "These images at <code>h</code> &#8776; 0 measure the offset "
                 "<code>C</code> directly."))
        A(clause("8.7", "<strong>Acquisition:</strong> one image every %d s, shutter "
                 "1/%d s or shorter, <strong>fixed exposure</strong> determined before "
                 "flight, raw format, no cropping and no automatic correction."
                 % (CADENCE, OBTURATION)))
        A(clause("8.8", "<strong>Record the UTC release time</strong> to the second, to "
                 "pair images with positions."))
        A(clause("8.9", "<strong>The ascent is the measurement.</strong> Descent images "
                 "are not usable and are not mixed with those of the ascent."))
        A(clause("8.10", "<strong>Method B, independent control:</strong> a second "
                 "very-wide-field camera pointed downward. The horizon there forms a "
                 "closed curve whose angular radius is 90&#176; &#8722; "
                 "<code>&#948;</code>, insensitive to tilt. A disagreement between A and "
                 "B is information, not a nuisance."))
        A(clause("8.11", "<strong>Recalibrate after recovery</strong>, on the sky, "
                 "<strong>without having dismantled anything</strong>. If the angle "
                 "between axes has moved, that must be known."))

    # ── 9 Calcul ────────────────────────────────────────────────────────────
    A(h2(9, fr))
    if fr:
        A(clause("9.1", "<strong>Crit&#232;re de point&#233; du bord.</strong> Sur le "
                 "fichier brut non recadr&#233;&#160;: pour chaque colonne de pixels, "
                 "prendre l'ordonn&#233;e du point &#224; <strong>mi-hauteur du "
                 "saut</strong> d'intensit&#233;, par interpolation "
                 "sous-pixellaire&#160;; moyenner sur toute la largeur exploitable de "
                 "chaque demi-champ, apr&#232;s avoir &#233;cart&#233; les colonnes "
                 "contenant un relief saillant ou un banc de nuage, et consigner "
                 "combien&#160;; consigner l'&#233;cart-type colonne &#224; colonne."))
        A(clause("9.2", "<strong>R&#233;fraction.</strong> Le rayon ob&#233;it &#224; "
                 "l'invariant de Bouguer <code>n(r)&#183;r&#183;cos&#952;</code> = "
                 "constante. Au point de tangence <code>&#952;</code> = 0, d'o&#249; "
                 "sans approximation&#160;:"))
        A('<div class="eq">\n  cos &#948; = n&#8320;(R+t) / [ n&#8321;(R+h) ]\n'
          '  <span class="cap">n&#8320; et t : indice et altitude au point de '
          'tangence&#160;; n&#8321; et h : indice et altitude au ballon. '
          'n = 1 + 77,6&#215;10<sup>&#8722;6</sup>&#183;P/T, avec P en hectopascals et '
          'T en kelvins.</span>\n</div>')
        A(clause("9.3", "La correction ne d&#233;pend que de l'indice aux <strong>deux "
                 "extr&#233;mit&#233;s</strong> du rayon, et non du profil "
                 "atmosph&#233;rique entre les deux. Les quatre grandeurs sont "
                 "relev&#233;es&#160;: <strong>aucun coefficient n'est "
                 "suppos&#233;</strong>."))
        A(clause("9.4", "<strong>Corriger du relief</strong> par mod&#232;le "
                 "num&#233;rique de terrain le long de chaque azimut de vis&#233;e. La "
                 "trace GNSS donne la position &#224; chaque instant&#160;; on cherche "
                 "le point de tangence r&#233;el et l'on en tire <code>t</code> pour "
                 "chacune des deux vis&#233;es."))
        A(tableau("Tableau 4 &#8212; Biais sur <code>2&#948;</code> selon l'altitude "
                  "moyenne du terrain sous l'horizon. &#192; comparer aux %s&#8242; du "
                  "signal&#160;: 2 &#224; 5 %%." % nb(variation, 0, fr),
                  ["altitude du ballon", "terrain 200 m", "terrain 500 m",
                   "terrain 1 000 m"], t_relief(fr)))
        A(clause("9.5", "<strong>Ajustement.</strong> Mod&#232;le sph&#233;rique "
                 "<code>2&#948;(h) = 2&#183;arccos[n&#8320;(R+t)/n&#8321;(R+h)] + "
                 "C</code>, deux param&#232;tres libres. Mod&#232;le plan "
                 "<code>2&#948;(h) = C</code>, un param&#232;tre. Pond&#233;ration par "
                 "l'inverse du carr&#233; de la <strong>dispersion observ&#233;e</strong> "
                 "dans chaque tranche d'altitude &#8212; non par le budget d'erreur. "
                 "Comparaison par <code>&#967;&#178;</code> par degr&#233; de "
                 "libert&#233;."))
        A(clause("9.6", "<strong>Test de forme libre&#160;:</strong> ajuster aussi "
                 "<code>2&#948; = C + a&#183;h<sup>p</sup></code> avec <code>p</code> "
                 "libre, et v&#233;rifier que <code>p</code> ressort compatible avec la "
                 "forme pr&#233;dite. C'est ce qui distingue un accord d'une "
                 "co&#239;ncidence &#224; deux param&#232;tres."))
        A(clause("9.7", "<strong>&#201;cartement d'une image&#160;:</strong> uniquement "
                 "sur crit&#232;re d&#233;clar&#233; d'avance &#8212; nettet&#233;, "
                 "nuage, saturation &#8212; <strong>jamais sur la valeur "
                 "obtenue</strong>."))
        A('<div class="two">\n'
          '  <div class="vc g">\n'
          '    <p class="h">2&#948; constant &#224; &#177;10&#8242;</p>\n'
          '    <p class="v">La surface sph&#233;rique est r&#233;fut&#233;e</p>\n'
          '    <p>Elle impose une variation de %s&#8242; entre 2 et 30 km. Une '
          's&#233;rie plate &#224; dix minutes d\'arc pr&#232;s la r&#233;fute par '
          'mesure directe.</p>\n'
          '  </div>\n'
          '  <div class="vc p">\n'
          '    <p class="h">2&#948;(h) suit la courbe, R &#8712; [%d ; %d] km</p>\n'
          '    <p class="v">La surface plane est r&#233;fut&#233;e</p>\n'
          '    <p>La valeur ajust&#233;e de <code>R</code> fournit en outre une mesure '
          'ind&#233;pendante du rayon.</p>\n'
          '  </div>\n'
          '</div>' % (nb(variation, 0, fr), R_MIN, R_MAX))
        A(encadre("Une variation qui ne suit pas la forme pr&#233;dite",
                  "  <p>Une variation significative mais de forme &#233;trang&#232;re "
                  "&#8212; lin&#233;aire en <code>h</code>, ou saturant &#224; "
                  "mi-parcours &#8212; ne confirme aucune des deux hypoth&#232;ses. "
                  "C'est le test du 9.6 qui la d&#233;tecte, et elle doit &#234;tre "
                  "trait&#233;e comme un <strong>d&#233;faut instrumental</strong>.</p>\n"
                  "  <p>Causes &#224; &#233;liminer par ordre de fr&#233;quence&#160;: "
                  "d&#233;rive thermique du support, exposition non fixe, horizon de "
                  "nuages &#224; altitude constante, flexion du di&#232;dre.</p>"))
    else:
        A(clause("9.1", "<strong>Edge pointing criterion.</strong> On the raw uncropped "
                 "file: for each pixel column, take the ordinate of the "
                 "<strong>half-height of the intensity step</strong>, by sub-pixel "
                 "interpolation; average over the whole usable width of each half-field, "
                 "after discarding columns containing salient relief or a cloud bank, "
                 "and record how many; record the column-to-column standard "
                 "deviation."))
        A(clause("9.2", "<strong>Refraction.</strong> The ray obeys the Bouguer "
                 "invariant <code>n(r)&#183;r&#183;cos&#952;</code> = constant. At the "
                 "tangent point <code>&#952;</code> = 0, whence, with no approximation:"))
        A('<div class="eq">\n  cos &#948; = n&#8320;(R+t) / [ n&#8321;(R+h) ]\n'
          '  <span class="cap">n&#8320; and t: index and altitude at the tangent point; '
          'n&#8321; and h: index and altitude at the balloon. '
          'n = 1 + 77.6&#215;10<sup>&#8722;6</sup>&#183;P/T, with P in hectopascals and '
          'T in kelvins.</span>\n</div>')
        A(clause("9.3", "The correction depends only on the index at the <strong>two "
                 "ends</strong> of the ray, not on the atmospheric profile between them. "
                 "All four quantities are recorded: <strong>no coefficient is "
                 "assumed</strong>."))
        A(clause("9.4", "<strong>Correct for relief</strong> using a digital terrain "
                 "model along each sighting azimuth. The GNSS track gives the position "
                 "at each instant; the real tangent point is sought and <code>t</code> "
                 "derived for each of the two sightings."))
        A(tableau("Table 4 &#8212; Bias on <code>2&#948;</code> by mean terrain "
                  "altitude beneath the horizon. To be compared with the %s&#8242; of "
                  "signal: 2 to 5 %%." % nb(variation, 0, fr),
                  ["balloon altitude", "terrain 200 m", "terrain 500 m",
                   "terrain 1 000 m"], t_relief(fr)))
        A(clause("9.5", "<strong>Fitting.</strong> Spherical model "
                 "<code>2&#948;(h) = 2&#183;arccos[n&#8320;(R+t)/n&#8321;(R+h)] + "
                 "C</code>, two free parameters. Plane model <code>2&#948;(h) = C</code>, "
                 "one parameter. Weighting by the inverse square of the "
                 "<strong>observed scatter</strong> in each altitude band &#8212; not by "
                 "the error budget. Comparison by <code>&#967;&#178;</code> per degree "
                 "of freedom."))
        A(clause("9.6", "<strong>Free-form test:</strong> also fit "
                 "<code>2&#948; = C + a&#183;h<sup>p</sup></code> with <code>p</code> "
                 "free, and check that <code>p</code> comes out compatible with the "
                 "predicted form. This is what separates agreement from a two-parameter "
                 "coincidence."))
        A(clause("9.7", "<strong>Discarding an image:</strong> only on a criterion "
                 "declared in advance &#8212; sharpness, cloud, saturation &#8212; "
                 "<strong>never on the value obtained</strong>."))
        A('<div class="two">\n'
          '  <div class="vc g">\n'
          '    <p class="h">2&#948; constant to &#177;10&#8242;</p>\n'
          '    <p class="v">The spherical surface is refuted</p>\n'
          '    <p>It imposes a variation of %s&#8242; between 2 and 30 km. A series '
          'flat to ten arcminutes refutes it by direct measurement.</p>\n'
          '  </div>\n'
          '  <div class="vc p">\n'
          '    <p class="h">2&#948;(h) follows the curve, R &#8712; [%d, %d] km</p>\n'
          '    <p class="v">The plane surface is refuted</p>\n'
          '    <p>The fitted value of <code>R</code> further provides an independent '
          'measurement of the radius.</p>\n'
          '  </div>\n'
          '</div>' % (nb(variation, 0, fr), R_MIN, R_MAX))
        A(encadre("A variation that does not follow the predicted form",
                  "  <p>A significant but oddly shaped variation &#8212; linear in "
                  "<code>h</code>, or saturating mid-way &#8212; confirms neither "
                  "hypothesis. The test of 9.6 detects it, and it shall be treated as an "
                  "<strong>instrumental defect</strong>.</p>\n"
                  "  <p>Causes to rule out, in order of frequency: thermal drift of the "
                  "mount, non-fixed exposure, a cloud horizon at constant altitude, "
                  "flexure of the dihedral.</p>"))

    # ── 10 Rapport d'essai ──────────────────────────────────────────────────
    A(h2(10, fr, saut=True))
    if fr:
        A(clause("10.1", "Le rapport mentionne&#160;:"))
        A("<ul>\n"
          "  <li>date, heure UTC du l&#226;cher, site&#160;;</li>\n"
          "  <li>P et T au sol &#224; l'heure du l&#226;cher, et incertitudes&#160;;</li>\n"
          "  <li>trace GNSS compl&#232;te et mode dynamique employ&#233;&#160;;</li>\n"
          "  <li>m&#233;thode de conversion en altitude orthom&#233;trique&#160;;</li>\n"
          "  <li>P et T &#224; bord, s&#233;rie compl&#232;te&#160;;</li>\n"
          "  <li>capteur, objectif, focale, dimensions, exposition employ&#233;e&#160;;</li>\n"
          "  <li>&#233;chelle angulaire r&#233;solue et angle entre axes, "
          "<strong>avant et apr&#232;s vol</strong>&#160;;</li>\n"
          "  <li>crit&#232;re de point&#233; et &#233;cart-type colonne &#224; "
          "colonne&#160;;</li>\n"
          "  <li><code>&#945;<sub>A</sub></code>, <code>&#945;<sub>B</sub></code> et "
          "<code>2&#948;</code> par image, avec l'altitude appari&#233;e&#160;;</li>\n"
          "  <li>correction de r&#233;fraction et correction de relief par image, "
          "MNT employ&#233;&#160;;</li>\n"
          "  <li>images &#233;cart&#233;es et le motif de chacune&#160;;</li>\n"
          "  <li>couverture nuageuse observ&#233;e, par tranche d'altitude&#160;;</li>\n"
          "  <li><code>R</code> et <code>C</code> ajust&#233;s, avec leurs intervalles "
          "de confiance&#160;;</li>\n"
          "  <li>r&#233;sultat de la m&#233;thode B et son &#233;cart &#224; la "
          "m&#233;thode A&#160;;</li>\n"
          "  <li>les images brutes, publi&#233;es et accessibles.</li>\n</ul>")
    else:
        A(clause("10.1", "The report shall state:"))
        A("<ul>\n"
          "  <li>date, UTC release time, site;</li>\n"
          "  <li>ground P and T at release time, and uncertainties;</li>\n"
          "  <li>complete GNSS track and dynamic model used;</li>\n"
          "  <li>method of conversion to orthometric altitude;</li>\n"
          "  <li>on-board P and T, complete series;</li>\n"
          "  <li>sensor, lens, focal length, dimensions, exposure used;</li>\n"
          "  <li>resolved angular scale and angle between axes, <strong>before and "
          "after flight</strong>;</li>\n"
          "  <li>pointing criterion and column-to-column standard deviation;</li>\n"
          "  <li><code>&#945;<sub>A</sub></code>, <code>&#945;<sub>B</sub></code> and "
          "<code>2&#948;</code> per image, with the paired altitude;</li>\n"
          "  <li>refraction and relief corrections per image, DTM used;</li>\n"
          "  <li>discarded images and the reason for each;</li>\n"
          "  <li>observed cloud cover, by altitude band;</li>\n"
          "  <li>fitted <code>R</code> and <code>C</code>, with confidence "
          "intervals;</li>\n"
          "  <li>method B result and its departure from method A;</li>\n"
          "  <li>the raw images, published and accessible.</li>\n</ul>")

    # ── 11 Fidélité et biais ────────────────────────────────────────────────
    A(h2(11, fr))
    if fr:
        A(clause("11.1", "<strong>Fid&#233;lit&#233;.</strong> Estimations &#224; "
                 "1&#963;, par image, sur <code>2&#948;</code>, pour un capteur Pi HQ "
                 "&#233;quip&#233; d'un 8 mm."))
        A(tableau("Tableau 5 &#8212; Budget d'erreur par image.",
                  ["source", "contribution"], t_budget(fr)))
        A(clause("11.2", "<strong>Deux rapports signal sur bruit, et non un "
                 "seul.</strong> Pour la discrimination des deux surfaces, le signal est "
                 "la variation (%s&#8242;) et le bruit celui d'une diff&#233;rence de "
                 "deux mesures (%s&#8242;)&#160;: <strong>rapport %s, sur deux images "
                 "seulement</strong>. Pour la mesure de <code>R</code>, tout entre "
                 "&#8212; &#233;chelle, relief, r&#233;fraction &#8212; et le plancher "
                 "syst&#233;matique est le relief, &#224; environ 1 %%."
                 % (nb(variation, 0, fr), nb(quad * math.sqrt(2), 2, fr),
                    nb(snr, 0, fr))))
        A(clause("11.3", "<strong>Biais connus.</strong> Le relief abaisse "
                 "<code>2&#948;</code> de 2 &#224; 5 %% du signal (tableau 4) et se "
                 "corrige par MNT. Un horizon de nuages &#224; altitude constante "
                 "imiterait une hauteur effective r&#233;duite. Une exposition "
                 "automatique d&#233;placerait le seuil de d&#233;tection du bord au "
                 "cours de la mont&#233;e &#8212; une d&#233;rive qui imiterait "
                 "exactement le signal."))
        A(clause("11.4", "<strong>Ce qu'un vol unique ne borne pas.</strong> Une "
                 "d&#233;rive instrumentale corr&#233;l&#233;e &#224; l'altitude, "
                 "thermique par exemple, imiterait le signal&#160;; le "
                 "r&#233;&#233;talonnage du 8.11 la borne sans l'exclure, et seul un "
                 "second vol avec un instrument construit diff&#233;remment la "
                 "l&#232;verait. Ces limites plafonnent la pr&#233;cision sur "
                 "<code>R</code>&#160;; elles ne menacent pas la discrimination, dont le "
                 "rapport d&#233;passe %s." % nb(snr, 0, fr)))
    else:
        A(clause("11.1", "<strong>Precision.</strong> Estimates at 1&#963;, per image, "
                 "on <code>2&#948;</code>, for a Pi HQ sensor with an 8 mm lens."))
        A(tableau("Table 5 &#8212; Error budget per image.",
                  ["source", "contribution"], t_budget(fr)))
        A(clause("11.2", "<strong>Two signal-to-noise ratios, not one.</strong> For "
                 "discriminating the two surfaces, the signal is the variation "
                 "(%s&#8242;) and the noise that of a difference of two measurements "
                 "(%s&#8242;): <strong>ratio %s, on two images alone</strong>. For "
                 "measuring <code>R</code>, everything enters &#8212; scale, relief, "
                 "refraction &#8212; and the systematic floor is relief, at about 1 %%."
                 % (nb(variation, 0, fr), nb(quad * math.sqrt(2), 2, fr),
                    nb(snr, 0, fr))))
        A(clause("11.3", "<strong>Known biases.</strong> Relief lowers "
                 "<code>2&#948;</code> by 2 to 5 %% of the signal (Table 4) and is "
                 "corrected by DTM. A cloud horizon at constant altitude would imitate a "
                 "reduced effective height. An automatic exposure would shift the edge "
                 "detection threshold during the ascent &#8212; a drift that would "
                 "imitate the signal exactly."))
        A(clause("11.4", "<strong>What a single flight does not bound.</strong> An "
                 "instrumental drift correlated with altitude, thermal for instance, "
                 "would imitate the signal; the recalibration of 8.11 bounds it without "
                 "excluding it, and only a second flight with a differently built "
                 "instrument would lift it. These limits cap the precision on "
                 "<code>R</code>; they do not threaten the discrimination, whose ratio "
                 "exceeds %s." % nb(snr, 0, fr)))

    # ── X1 Annexe ───────────────────────────────────────────────────────────
    A(h2_annexe(fr))
    if fr:
        A("<h3>X1.1 &#8212; Pourquoi 2&#948; et non &#948;</h3>")
        A("<p>Une nacelle suspendue balance et tourne. &#201;tablir la verticale &#224; "
          "bord est difficile et, comme le montre la sym&#233;trie, inutile.</p>")
        A("<p>Si l'instrument est inclin&#233; de <code>&#949;</code> dans le plan de "
          "vis&#233;e, le bord d'horizon du c&#244;t&#233; A se lit &#224; "
          "<code>&#948; + &#949;</code> sous l'axe, et celui du c&#244;t&#233; "
          "oppos&#233; &#224; <code>&#948; &#8722; &#949;</code>. Leur somme vaut "
          "<code>2&#948;</code>, <strong>exactement</strong>, quelle que soit "
          "l'inclinaison. C'est le raisonnement de la calibration par retournement en "
          "g&#233;od&#233;sie&#160;: une sym&#233;trie &#233;limine une inconnue sans "
          "qu'il faille la mesurer.</p>")
        A("<h3>X1.2 &#8212; Pourquoi une seule cam&#233;ra, et non deux</h3>")
        A("<p>Deux bo&#238;tiers regardant en sens oppos&#233; feraient la m&#234;me "
          "mesure &#8212; &#224; condition de d&#233;clencher simultan&#233;ment. Or un "
          "pendule de 10 m oscille avec une p&#233;riode de 6,3 s&#160;; &#224; "
          "5&#176; d'amplitude, la vitesse angulaire atteint 5&#176; par seconde.</p>")
        A("<p>Un d&#233;calage de 100 ms entre les deux d&#233;clenchements vaut alors "
          "<strong>30 minutes d'arc</strong> d'erreur &#8212; trente fois le budget, sur "
          "une grandeur dont rien ne signale la corruption. Un capteur unique supprime le "
          "probl&#232;me par construction&#160;: les deux vis&#233;es sont la m&#234;me "
          "exposition.</p>")
        A("<h3>X1.3 &#8212; Pourquoi le crit&#232;re porte sur la variation</h3>")
        A("<p>Le d&#233;calage instrumental <code>C</code> est inconnu et le restera. Il "
          "ne g&#234;ne pas, parce que le test porte sur la variation de "
          "<code>2&#948;</code> au cours de la mont&#233;e et non sur sa valeur. Dans "
          "une diff&#233;rence de deux mesures, <code>C</code> dispara&#238;t, "
          "l'&#233;chelle angulaire reste, et l'inclinaison a d&#233;j&#224; disparu par "
          "X1.1.</p>")
        A("<p>C'est la forme la plus robuste que puisse prendre ce test. Elle survit "
          "&#224; une erreur d'angle du di&#232;dre, &#224; un montage impr&#233;cis, "
          "&#224; une nacelle qui balance, et m&#234;me &#224; un instrument dont on "
          "ignorerait la g&#233;om&#233;trie exacte.</p>")
        A("<h3>X1.4 &#8212; Le pr&#233;enregistrement, s'il est recherch&#233;</h3>")
        A("<p>Un num&#233;ro de version ne prouve rien. Pour qu'un "
          "pr&#233;enregistrement soit opposable, il faut un horodatage v&#233;rifiable "
          "par un tiers&#160;: r&#233;server le DOI sans publier, l'inscrire dans le "
          "document, r&#233;g&#233;n&#233;rer le PDF, calculer son empreinte SHA-256, "
          "t&#233;l&#233;verser, coller l'empreinte dans les notes de l'enregistrement, "
          "publier &#8212; et <strong>ne voler qu'ensuite</strong>.</p>")
        A("<p>L'empreinte se calcule sur le fichier fini&#160;; l'y inscrire la "
          "fausserait. Elle vit dans les notes de l'enregistrement, pas dans le "
          "document.</p>")
    else:
        A("<h3>X1.1 &#8212; Why 2&#948; and not &#948;</h3>")
        A("<p>A suspended gondola swings and rotates. Establishing the vertical on board "
          "is difficult and, as the symmetry shows, unnecessary.</p>")
        A("<p>If the instrument is tilted by <code>&#949;</code> in the sighting plane, "
          "the horizon edge on side A reads at <code>&#948; + &#949;</code> below the "
          "axis, and the opposite one at <code>&#948; &#8722; &#949;</code>. Their sum "
          "is <code>2&#948;</code>, <strong>exactly</strong>, whatever the tilt. This is "
          "the reasoning of reversal calibration in geodesy: a symmetry eliminates an "
          "unknown without it having to be measured.</p>")
        A("<h3>X1.2 &#8212; Why one camera, and not two</h3>")
        A("<p>Two bodies looking in opposite directions would make the same measurement "
          "&#8212; provided they triggered simultaneously. But a 10 m pendulum swings "
          "with a period of 6.3 s; at 5&#176; amplitude the angular rate reaches "
          "5&#176; per second.</p>")
        A("<p>A 100 ms offset between the two triggers is then worth <strong>30 "
          "arcminutes</strong> of error &#8212; thirty times the budget, on a quantity "
          "whose corruption nothing signals. A single sensor removes the problem by "
          "construction: the two sightings are the same exposure.</p>")
        A("<h3>X1.3 &#8212; Why the criterion bears on the variation</h3>")
        A("<p>The instrumental offset <code>C</code> is unknown and will remain so. It "
          "does not matter, because the test bears on the variation of "
          "<code>2&#948;</code> during the ascent and not on its value. In a difference "
          "of two measurements <code>C</code> cancels, the angular scale remains, and "
          "the tilt has already gone through X1.1.</p>")
        A("<p>This is the most robust form this test can take. It survives an error in "
          "the dihedral angle, an imprecise mount, a swinging gondola, and even an "
          "instrument whose exact geometry is unknown.</p>")
        A("<h3>X1.4 &#8212; Pre-registration, if it is sought</h3>")
        A("<p>A version number proves nothing. For a pre-registration to be contestable, "
          "a third-party-verifiable timestamp is required: reserve the DOI without "
          "publishing, write it into the document, regenerate the PDF, compute its "
          "SHA-256 hash, upload, paste the hash into the record's notes, publish "
          "&#8212; and <strong>only then fly</strong>.</p>")
        A("<p>The hash is computed on the finished file; writing it into the file would "
          "falsify it. It lives in the record's notes, not in the document.</p>")

    return "\n\n".join(T)


def main():
    variation, quad, snr = controle()
    ecrire(CIBLE, "D&#233;pression de l'horizon depuis un ballon "
           "&#8212; m&#233;thode d'essai", corps(True), corps(False))
    print("Méthode d'essai écrite : content/protocoles/ballon-bilingue.html")
    print("  variation de 2δ entre 2 et 30 km : %.0f′" % variation)
    print("  budget quadratique par image     : %.2f′" % quad)
    print("  rapport signal sur bruit          : %.0f" % snr)
    print("  structure : 1→11 + annexe X1, contrôle de récit passé")
    return 0


if __name__ == "__main__":
    sys.exit(main())
