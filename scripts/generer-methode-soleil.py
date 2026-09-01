#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Méthode d'essai « Profil de distance du Soleil au cours d'une journée ».

Reprend l'intégralité du contenu technique du protocole 1.7 et le remet dans
l'ordre de sections normalisé (voir scripts/methode_essai.py). Rien n'est perdu :
ce qui était du raisonnement passe en annexe X1, ce qui était une exigence
devient une clause numérotée.

L'observable est le rapport r = θ(bas)/θ(haut) entre deux hauteurs de la même
journée. Pour un corps rigide θ = D/d, donc r signifie que la distance a été
multipliée par 1/r. Aucune hypothèse sur la nature de l'astre n'entre dans cette
conversion — c'est la raison pour laquelle la méthode ne déclare aucune valeur
de r impossible.

Le seul critère de rejet est la symétrie matin/après-midi : une variation
géométrique ne dépend que de la hauteur, un artefact n'a aucune raison d'être
symétrique par rapport au midi solaire.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from methode_essai import (PROTOCOLES, clause, ecrire, encadre, h2, h2_annexe,
                           ligne, masthead, mil, nb, tableau)      # noqa: E402

CIBLE = os.path.join(PROTOCOLES, "soleil-bilingue.html")

BUDGET = 0.51          # % à 1 σ
REJET = 3 * BUDGET     # % — seuil de symétrie
FOCALE, PIXELS, DISQUE = 400, 4000, 611
LECTURE = [1.000, 0.990, 0.950, 0.910, 0.800, 0.600, 0.500]
HAUTEURS = [15, 20, 30, 45, 60]
LATITUDES = [(0.0, 90.0, 1.52), (30.0, 88.6, 1.52), (45.0, 73.6, 1.46),
             (48.9, 69.7, 1.42), (55.0, 63.6, 1.35), (65.0, 53.6, 1.20)]
DERIVE = [(2, 0.10), (4, 0.21), (6, 0.31), (8, 0.42)]
BUDGET_POSTES = [
    ("Point&#233; du limbe (&#177;2 px, crit&#232;re 50 %)",
     "Limb pointing (&#177;2 px, 50 per cent criterion)", 0.33),
    ("Turbulence r&#233;siduelle apr&#232;s empilement",
     "Residual turbulence after stacking", 0.25),
    ("Distorsion optique au centre du champ",
     "Optical distortion at field centre", 0.13),
    ("Stabilit&#233; de la focale", "Focal length stability", 0.08),
    ("Assombrissement centre-bord et rougissement du limbe",
     "Limb darkening and reddening", 0.20),
    ("R&#233;sidu d'&#233;ph&#233;m&#233;ride si la campagne s'&#233;tale",
     "Ephemeris residual if the campaign spreads", 0.15),
]
SINUS = math.sin(math.radians(20)) / math.sin(math.radians(70))


def controle():
    assert abs(SINUS - 0.3640) < 5e-5, SINUS
    assert abs(100 * (1 / SINUS - 1) - 174.7) < 0.2
    quad = math.sqrt(sum(v ** 2 for _, _, v in BUDGET_POSTES))
    assert abs(quad - BUDGET) < 0.02, quad
    assert abs(REJET - 1.53) < 1e-9
    # 1 % du disque, en pixels, à la focale de référence.
    assert abs(DISQUE / 100 - 6.11) < 0.02
    for r, attendu in ((0.990, 1.0), (0.950, 5.3), (0.910, 9.9),
                       (0.800, 25.0), (0.500, 100.0)):
        assert abs(100 * (1 / r - 1) - attendu) < 0.05, r
    return quad


def t_lecture(fr):
    lignes = [ligne([nb(r, 3, fr), "+%s%s" % (nb(100 * (1 / r - 1), 1, fr),
                                              "&#160;%" if fr else " per cent")])
              for r in LECTURE]
    lignes.append(ligne([nb(SINUS, 3, fr),
                         "+%s%s" % (nb(100 * (1 / SINUS - 1), 1, fr),
                                    "&#160;%" if fr else " per cent")], True))
    return lignes


def t_budget(fr):
    lignes = []
    for lfr, len_, v in BUDGET_POSTES:
        lignes.append('    <tr><td>%s</td><td class="n">%s&#160;%%</td></tr>'
                      % (lfr if fr else len_, nb(v, 2, fr)))
    lignes.append('    <tr class="hi"><td><strong>%s</strong></td>'
                  '<td class="n"><strong>%s&#160;%%</strong></td></tr>'
                  % ("Total quadratique (1 &#963;)" if fr
                     else "Quadratic total (1 &#963;)", nb(BUDGET, 2, fr)))
    return lignes


def t_latitudes(fr):
    return [ligne([nb(lat, 1, fr) + "&#176;", nb(hmax, 1, fr) + "&#176;",
                   nb(sig, 2, fr) + ("&#160;%" if fr else " per cent")],
                  abs(lat - 48.9) < 0.01)
            for lat, hmax, sig in LATITUDES]


def t_derive(fr):
    return [ligne([("%d h" % h), nb(d, 2, fr) + ("&#160;%" if fr else " per cent"),
                   nb(100 * d / 1.42, 0, fr) + ("&#160;%" if fr else " per cent")])
            for h, d in DERIVE]


def corps(fr):
    T = []
    A = T.append
    pc = "&#160;%" if fr else " per cent"

    A(masthead(fr,
               "Profil de distance du Soleil" if fr else "The Sun's distance profile",
               ("D&#233;termination du rapport des diam&#232;tres angulaires entre "
                "deux hauteurs d'une m&#234;me journ&#233;e" if fr else
                "Determination of the ratio of angular diameters between two "
                "altitudes of the same day"), "2.0"))

    # ── 1 Domaine d'application ──────────────────────────────────────────────
    A(h2(1, fr))
    if fr:
        A(clause("1.1", "La pr&#233;sente m&#233;thode d&#233;termine le "
                 "<strong>rapport</strong> <code>r = &#952;(bas)/&#952;(haut)</code> des "
                 "diam&#232;tres angulaires du Soleil mesur&#233;s &#224; deux hauteurs "
                 "d'une m&#234;me journ&#233;e, et la variation de distance "
                 "<code>1/r &#8722; 1</code> qui s'en d&#233;duit pour un corps rigide."))
        A(clause("1.2", "Elle s'applique aux hauteurs solaires comprises entre "
                 "15&#176; et le maximum du jour, depuis une station unique."))
        A(clause("1.3", "Elle <strong>ne mesure ni la taille du Soleil, ni son "
                 "altitude, ni sa distance</strong>, et ne suppose rien de sa "
                 "nature. Elle produit un rapport et son incertitude."))
        A(clause("1.4", "Les valeurs sont exprim&#233;es en unit&#233;s SI. Les "
                 "diam&#232;tres angulaires sont exprim&#233;s en minutes d'arc."))
        A(clause("1.5", "<em>Avertissement.</em> Un t&#233;l&#233;objectif concentre "
                 "l'&#233;nergie solaire. L'observation directe sans filtre "
                 "certifi&#233; provoque une l&#233;sion r&#233;tinienne "
                 "<strong>irr&#233;versible et indolore</strong>. Voir 6.2 et 6.6."))
    else:
        A(clause("1.1", "This method determines the <strong>ratio</strong> "
                 "<code>r = &#952;(low)/&#952;(high)</code> of the Sun's angular "
                 "diameters measured at two altitudes of the same day, and the "
                 "distance change <code>1/r &#8722; 1</code> that follows from it for "
                 "a rigid body."))
        A(clause("1.2", "It applies to solar altitudes between 15&#176; and the "
                 "day's maximum, from a single station."))
        A(clause("1.3", "It <strong>measures neither the Sun's size, nor its "
                 "altitude, nor its distance</strong>, and assumes nothing about its "
                 "nature. It produces a ratio and its uncertainty."))
        A(clause("1.4", "Values are expressed in SI units. Angular diameters are "
                 "expressed in arcminutes."))
        A(clause("1.5", "<em>Warning.</em> A telephoto lens concentrates solar "
                 "energy. Direct observation without a certified filter causes "
                 "<strong>irreversible and painless</strong> retinal injury. See 6.2 "
                 "and 6.6."))

    # ── 2 Documents de référence ─────────────────────────────────────────────
    A(h2(2, fr))
    A(clause("2.1", "JCGM 100:2008, <em>&#201;valuation des donn&#233;es de mesure "
             "&#8212; Guide pour l'expression de l'incertitude de mesure</em> (GUM)."
             if fr else
             "JCGM 100:2008, <em>Evaluation of measurement data &#8212; Guide to the "
             "expression of uncertainty in measurement</em> (GUM)."))
    A(clause("2.2", "ISO/IEC 17025:2017."))
    A(clause("2.3", "BENNETT, G. G., <em>The Calculation of Astronomical "
             "Refraction in Marine Navigation</em>, Journal of Navigation, 35 (1982), "
             "p. 255&#8211;259."))
    A(clause("2.4", "&#201;ph&#233;m&#233;rides plan&#233;taires d'un service "
             "reconnu, cit&#233;es avec leur version, fournissant la distance "
             "topocentrique de la Lune et la hauteur apparente du Soleil."
             if fr else
             "Planetary ephemerides from a recognised service, cited with their "
             "version, providing the Moon's topocentric distance and the Sun's "
             "apparent altitude."))

    # ── 3 Terminologie ───────────────────────────────────────────────────────
    A(h2(3, fr))
    if fr:
        A("<p>3.1 <strong>diam&#232;tre angulaire horizontal</strong>, "
          "<code>&#952;</code>, <em>minutes d'arc</em> &#8212; largeur du disque "
          "mesur&#233;e perpendiculairement &#224; la verticale du lieu.</p>")
        A("<p>3.2 <strong>hauteur apparente</strong>, <code>&#945;</code>, "
          "<em>degr&#233;s</em> &#8212; hauteur r&#233;fract&#233;e du centre du "
          "disque au-dessus de l'horizon.</p>")
        A("<p>3.3 <strong>rapport</strong>, <code>r</code>, sans dimension &#8212; "
          "<code>&#952;</code> &#224; la plus basse hauteur divis&#233; par "
          "<code>&#952;</code> &#224; la plus haute.</p>")
        A("<p>3.4 <strong>crit&#232;re des 50&#160;%</strong> &#8212; d&#233;finition "
          "du bord du disque prise &#224; mi-hauteur entre le fond de ciel et le "
          "plateau du limbe, sur le profil d'intensit&#233;.</p>")
        A("<p>3.5 <strong>s&#233;ries appari&#233;es</strong> &#8212; deux "
          "s&#233;ries acquises &#224; la m&#234;me hauteur apparente, l'une avant "
          "et l'autre apr&#232;s le midi solaire.</p>")
    else:
        A("<p>3.1 <strong>horizontal angular diameter</strong>, <code>&#952;</code>, "
          "<em>arcminutes</em> &#8212; width of the disk measured perpendicular to the "
          "local vertical.</p>")
        A("<p>3.2 <strong>apparent altitude</strong>, <code>&#945;</code>, "
          "<em>degrees</em> &#8212; refracted altitude of the disk centre above the "
          "horizon.</p>")
        A("<p>3.3 <strong>ratio</strong>, <code>r</code>, dimensionless &#8212; "
          "<code>&#952;</code> at the lower altitude divided by <code>&#952;</code> at "
          "the higher.</p>")
        A("<p>3.4 <strong>50 per cent criterion</strong> &#8212; definition of the "
          "disk edge taken at half height between sky background and limb plateau, on "
          "the intensity profile.</p>")
        A("<p>3.5 <strong>paired series</strong> &#8212; two series acquired at the "
          "same apparent altitude, one before and one after solar noon.</p>")

    # ── 4 Résumé de la méthode ───────────────────────────────────────────────
    A(h2(4, fr))
    if fr:
        A(clause("4.1", "La cha&#238;ne de mesure est qualifi&#233;e sur la Lune par "
                 "deux contr&#244;les pr&#233;alables (8.1, 8.2)."))
        A(clause("4.2", "Douze s&#233;ries appari&#233;es sont acquises au cours "
                 "d'une journ&#233;e, six en mont&#233;e et six en descente, aux "
                 "m&#234;mes hauteurs apparentes."))
        A(clause("4.3", "Le diam&#232;tre horizontal est r&#233;duit au crit&#232;re "
                 "des 50&#160;%, l'&#233;chelle angulaire &#233;tant relev&#233;e par "
                 "la d&#233;rive diurne sur chaque s&#233;rie."))
        A(clause("4.4", "Le rapport <code>r</code> est form&#233; entre la plus basse "
                 "et la plus haute hauteur atteintes."))
        A(clause("4.5", "La s&#233;rie est accept&#233;e ou rejet&#233;e sur le seul "
                 "crit&#232;re de sym&#233;trie matin/apr&#232;s-midi (8.9)."))
        A(clause("4.6", "Le r&#233;sultat d'essai est <code>r</code> et son "
                 "incertitude &#233;largie, accompagn&#233;s de la variation de "
                 "distance <code>1/r &#8722; 1</code>."))
    else:
        A(clause("4.1", "The measurement chain is qualified on the Moon by two "
                 "preliminary controls (8.1, 8.2)."))
        A(clause("4.2", "Twelve paired series are acquired over one day, six "
                 "ascending and six descending, at the same apparent altitudes."))
        A(clause("4.3", "The horizontal diameter is reduced by the 50 per cent "
                 "criterion, the angular scale being read from the diurnal drift on "
                 "each series."))
        A(clause("4.4", "The ratio <code>r</code> is formed between the lowest and "
                 "the highest altitudes reached."))
        A(clause("4.5", "The run is accepted or rejected on the sole criterion of "
                 "morning/afternoon symmetry (8.9)."))
        A(clause("4.6", "The test result is <code>r</code> and its expanded "
                 "uncertainty, together with the distance change "
                 "<code>1/r &#8722; 1</code>."))

    # ── 5 Intérêt et emploi ──────────────────────────────────────────────────
    A(h2(5, fr))
    if fr:
        A(clause("5.1", "Le diam&#232;tre angulaire d'un corps rigide vaut "
                 "<code>D/d</code>. Un rapport <code>r</code> mesur&#233; entre deux "
                 "hauteurs signifie donc que la distance &#224; l'&#339;il a "
                 "&#233;t&#233; multipli&#233;e par <code>1/r</code>."))
        A(clause("5.2", "La conversion ne suppose que la rigidit&#233; de l'astre. "
                 "<strong>Aucune valeur de <code>r</code> n'est d&#233;clar&#233;e "
                 "impossible</strong>&#160;; le tableau 1 en donne la lecture."))
        A(clause("5.3", "Une source dont la distance ne varie pas au cours du jour "
                 "donne <code>r = 1,000</code> &#224; 2&#215;10<sup>&#8722;2</sup>"
                 "&#160;% pr&#232;s. Une source &#224; hauteur finie au-dessus d'un "
                 "plan donne <code>r &lt; 1</code>."))
        A(tableau("Tableau 1 &#8212; Lecture d'un rapport mesur&#233;. La "
                  "derni&#232;re ligne, surlign&#233;e, est celle qu'imposerait une "
                  "hauteur constante au-dessus d'un plan entre 70&#176; et 20&#176; "
                  "&#8212; un cas parmi d'autres, non une borne.",
                  ["rapport mesur&#233; r", "la distance augmente de"],
                  t_lecture(fr)))
    else:
        A(clause("5.1", "The angular diameter of a rigid body is <code>D/d</code>. A "
                 "ratio <code>r</code> measured between two altitudes therefore means "
                 "the distance to the eye has been multiplied by <code>1/r</code>."))
        A(clause("5.2", "The conversion assumes only that the body is rigid. "
                 "<strong>No value of <code>r</code> is declared impossible</strong>; "
                 "Table 1 gives the reading."))
        A(clause("5.3", "A source whose distance does not vary through the day gives "
                 "<code>r = 1.000</code> to within 2&#215;10<sup>&#8722;2</sup> per "
                 "cent. A source at finite height above a plane gives "
                 "<code>r &lt; 1</code>."))
        A(tableau("Table 1 &#8212; Reading a measured ratio. The highlighted last row "
                  "is the one a constant height above a plane would require between "
                  "70&#176; and 20&#176; &#8212; one case among others, not a bound.",
                  ["measured ratio r", "distance increases by"], t_lecture(fr)))

    # ── 6 Appareillage ───────────────────────────────────────────────────────
    A(h2(6, fr))
    if fr:
        A(clause("6.1", "<strong>Objectif</strong> de %d mm ou plus en &#233;quivalent "
                 "plein format, &#224; focale fixe ou verrouill&#233;e "
                 "m&#233;caniquement. &#192; %d mm sur un capteur de %s pixels de "
                 "haut, le disque solaire couvre %d pixels&#160;: 1&#160;%% vaut alors "
                 "%s pixels." % (FOCALE, FOCALE, mil(PIXELS, fr), DISQUE,
                                 nb(DISQUE / 100, 1, fr))))
        A(clause("6.2", "<strong>Filtre solaire</strong> pleine ouverture, "
                 "densit&#233; 5 (ND100000), mont&#233; <strong>en avant</strong> de "
                 "l'objectif."))
        A(clause("6.3", "<strong>Tr&#233;pied</strong> et d&#233;clenchement "
                 "retard&#233; ou t&#233;l&#233;command&#233;."))
        A(clause("6.4", "<strong>Enregistrement en donn&#233;es brutes.</strong> "
                 "Aucun recadrage, aucune correction automatique de distorsion, aucun "
                 "traitement de compression."))
        A(clause("6.5", "<strong>Mise au point manuelle</strong> sur l'infini, "
                 "verrouill&#233;e pour toute la s&#233;rie."))
        A(clause("6.6", "La vis&#233;e s'effectue exclusivement sur &#233;cran. "
                 "<strong>Le viseur optique n'est pas utilis&#233;.</strong>"))
        A(clause("6.7", "<strong>Instruments m&#233;t&#233;orologiques</strong>&#160;: "
                 "thermom&#232;tre, barom&#232;tre, hygrom&#232;tre."))
    else:
        A(clause("6.1", "<strong>Lens</strong> of %d mm or more full-frame "
                 "equivalent, of fixed focal length or mechanically locked. At %d mm "
                 "on a sensor %s pixels high, the solar disk covers %d pixels: 1 per "
                 "cent is then %s pixels." % (FOCALE, FOCALE, mil(PIXELS, fr), DISQUE,
                                              nb(DISQUE / 100, 1, fr))))
        A(clause("6.2", "<strong>Full-aperture solar filter</strong>, density 5 "
                 "(ND100000), mounted <strong>in front of</strong> the objective."))
        A(clause("6.3", "<strong>Tripod</strong> and delayed or remote release."))
        A(clause("6.4", "<strong>Raw recording.</strong> No cropping, no automatic "
                 "distortion correction, no compression processing."))
        A(clause("6.5", "<strong>Manual focus</strong> at infinity, locked for the "
                 "whole run."))
        A(clause("6.6", "Sighting is done on screen only. <strong>The optical "
                 "viewfinder is not used.</strong>"))
        A(clause("6.7", "<strong>Meteorological instruments</strong>: thermometer, "
                 "barometer, hygrometer."))

    # ── 7 Conditions d'essai ─────────────────────────────────────────────────
    A(h2(7, fr))
    if fr:
        A(clause("7.1", "Ciel clair et air calme sur la journ&#233;e "
                 "enti&#232;re."))
        A(clause("7.2", "La journ&#233;e doit permettre la course "
                 "compl&#232;te&#160;: une demi-course rend l'appariement du 8.5 "
                 "impossible et l'essai est nul."))
        A(clause("7.3", "Temp&#233;rature, pression et humidit&#233; sont "
                 "relev&#233;es au d&#233;but et &#224; la fin de la journ&#233;e."))
        A(clause("7.4", "Les contr&#244;les pr&#233;alables du 8.1 et du 8.2 sont "
                 "ex&#233;cut&#233;s avec le m&#234;me mat&#233;riel et la m&#234;me "
                 "r&#233;duction que la mesure solaire."))
        A(clause("7.5", "Le contr&#244;le A du 8.1 requiert huit &#224; douze nuits "
                 "r&#233;parties sur un mois lunaire. Le contr&#244;le B du 8.2 en "
                 "requiert quatre au minimum, programm&#233;es &#224; moins d'un jour "
                 "du p&#233;rig&#233;e ou de l'apog&#233;e."))
    else:
        A(clause("7.1", "Clear sky and calm air over the whole day."))
        A(clause("7.2", "The day shall permit the full course: half a course makes "
                 "the pairing of 8.5 impossible and the test is void."))
        A(clause("7.3", "Temperature, pressure and humidity are recorded at the "
                 "start and end of the day."))
        A(clause("7.4", "The preliminary controls of 8.1 and 8.2 are performed with "
                 "the same equipment and the same reduction as the solar "
                 "measurement."))
        A(clause("7.5", "Control A of 8.1 requires eight to twelve nights spread over "
                 "a lunar month. Control B of 8.2 requires at least four, scheduled "
                 "within one day of perigee or apogee."))

    # ── 8 Mode opératoire ────────────────────────────────────────────────────
    A(h2(8, fr, saut=True))
    if fr:
        A(clause("8.1", "<strong>Contr&#244;le A &#8212; &#233;talonnage en "
                 "distance.</strong> Photographier la Lune huit &#224; douze nuits, "
                 "en relevant pour chaque clich&#233; la distance <em>topocentrique</em> "
                 "de l'&#233;ph&#233;m&#233;ride. Ajuster un cercle sur le limbe "
                 "externe &#8212; jamais mesurer une largeur &#8212; en excluant le "
                 "terminateur et en pond&#233;rant les portions gauche et droite. La "
                 "pente de <code>&#952;</code> contre <code>1/d</code> doit valoir "
                 "1,000&#160;; la dispersion autour de la droite donne l'incertitude "
                 "r&#233;elle de la cha&#238;ne."))
        A(encadre("Aucune valeur n'est pr&#233;-annonc&#233;e",
                  "  <p>L'amplitude d&#233;pend du mois observ&#233;&#160;: un mois "
                  "favorable donne 12,0&#160;%, un mois d&#233;favorable "
                  "<strong>9,5&#160;%</strong>. Le contr&#244;le porte sur la "
                  "<strong>loi</strong> &#8212; la constance du produit "
                  "<code>&#952;&#215;d</code> &#8212; et jamais sur une valeur "
                  "donn&#233;e d'avance.</p>"))
        A(clause("8.2", "<strong>Contr&#244;le B &#8212; parallaxe diurne.</strong> "
                 "Sur quatre nuits au minimum, photographier la Lune &#224; 5&#176; de "
                 "hauteur et &#224; son maximum accessible. Comparer chaque "
                 "diam&#232;tre au <code>d(a)</code> calcul&#233; pour son propre "
                 "instant&#160;:"))
        A('<div class="eq">\n  d(a) = &#8730;( D&#178; &#8722; R&#178; cos&#178;a ) '
          '&#8722; R sin a\n  <span class="cap">a = hauteur apparente&#160;; D = '
          'distance g&#233;ocentrique de l\'&#233;ph&#233;m&#233;ride&#160;; '
          'R = 6&#8239;371 km. Le diam&#232;tre apparent varie comme 1/d(a).</span>\n'
          '</div>')
        A(tableau("Tableau 2 &#8212; Signal attendu du contr&#244;le B entre une prise "
                  "&#224; 5&#176; et une prise au maximum accessible, et l'&#233;cart "
                  "type pour une seule nuit. Quatre nuits portent le r&#233;sultat "
                  "au-del&#224; de 6 &#963;.",
                  ["latitude", "hauteur max.", "signal pr&#233;dit"],
                  t_latitudes(fr)))
        A(tableau("Tableau 3 &#8212; D&#233;rive orbitale maximale entre la prise "
                  "basse et la prise haute, &#224; comparer au signal.",
                  ["intervalle", "d&#233;rive max.", "part du signal"],
                  t_derive(fr)))
        A(clause("8.3", "<strong>Ne pas passer au Soleil</strong> tant que 8.1 n'a pas "
                 "donn&#233; une pente de 1,000 et que 8.2 n'a pas retrouv&#233; le "
                 "signal pr&#233;dit &#224; la latitude de la station."))
        A(clause("8.4", "Mesurer exclusivement la <strong>largeur</strong> du disque, "
                 "perpendiculairement &#224; la verticale du lieu."))
        A(clause("8.5", "<strong>Acqu&#233;rir douze s&#233;ries appari&#233;es</strong>"
                 "&#160;: six en mont&#233;e le matin, six en descente "
                 "l'apr&#232;s-midi, aux hauteurs apparentes de %s&#176; et au maximum "
                 "du jour. Vingt clich&#233;s par s&#233;rie, &#224; empiler."
                 % ", ".join(str(h) for h in HAUTEURS)))
        A(clause("8.6", "&#192; chaque s&#233;rie, noter l'heure UTC &#224; la "
                 "seconde. La hauteur s'en d&#233;duit par "
                 "&#233;ph&#233;m&#233;ride. <strong>Employer la hauteur apparente, "
                 "r&#233;fract&#233;e</strong>, et non la hauteur vraie&#160;: "
                 "l'&#233;cart vaut 0,40&#160;% sur <code>sin &#945;</code> &#224; "
                 "15&#176;, 0,22&#160;% &#224; 20&#176;, 0,09&#160;% &#224; 30&#176;."))
        A(clause("8.7", "<strong>Relever l'&#233;chelle par la d&#233;rive.</strong> "
                 "Appareil fixe, sans suivi&#160;: le disque d&#233;file &#224; "
                 "15,041&#8243;/s &#215; cos &#948;, soit 4,9 pixels par seconde "
                 "&#224; %d mm. Une rafale de dix secondes &#224; chaque s&#233;rie "
                 "donne l'&#233;chelle angulaire du moment sans conna&#238;tre la "
                 "focale." % FOCALE))
        A(clause("8.8", "<strong>Ne rien changer.</strong> Focale, mise au point et "
                 "filtre restent identiques d'un bout &#224; l'autre. L'exposition "
                 "peut varier&#160;; le crit&#232;re du 9.1 la neutralise."))
        A(clause("8.9", "<strong>Crit&#232;re de rejet.</strong> Pour chaque couple de "
                 "hauteurs appari&#233;es, l'&#233;cart matin/apr&#232;s-midi doit "
                 "rester sous <strong>%s&#160;%%</strong> (3&#963;). Au-del&#224;, la "
                 "s&#233;rie est rejet&#233;e et refaite, <strong>quelle que soit la "
                 "valeur du rapport</strong>. Causes &#224; &#233;liminer&#160;: seuil "
                 "de luminosit&#233; fixe au lieu du crit&#232;re des 50&#160;%%, "
                 "diam&#232;tre vertical mesur&#233; au lieu de l'horizontal, focale "
                 "modifi&#233;e en cours de s&#233;rie, recadrage, correction "
                 "automatique de distorsion laiss&#233;e active."
                 % nb(REJET, 2, fr)))
        A(clause("8.10", "Consigner le rapport largeur/hauteur du disque &#224; chaque "
                 "s&#233;rie. Il mesure la r&#233;fraction du moment et permet de "
                 "rejeter une s&#233;rie prise dans un r&#233;gime anormal."))
    else:
        A(clause("8.1", "<strong>Control A &#8212; distance calibration.</strong> "
                 "Photograph the Moon on eight to twelve nights, recording for each "
                 "frame the <em>topocentric</em> distance from the ephemeris. Fit a "
                 "circle to the outer limb &#8212; never measure a width &#8212; "
                 "excluding the terminator and weighting the left and right portions. "
                 "The slope of <code>&#952;</code> against <code>1/d</code> shall be "
                 "1.000; the scatter about the line gives the chain's real "
                 "uncertainty."))
        A(encadre("No value is announced in advance",
                  "  <p>The amplitude depends on the month observed: a favourable "
                  "month gives 12.0 per cent, an unfavourable one <strong>9.5 per "
                  "cent</strong>. The control bears on the <strong>law</strong> "
                  "&#8212; the constancy of the product <code>&#952;&#215;d</code> "
                  "&#8212; and never on a value given in advance.</p>"))
        A(clause("8.2", "<strong>Control B &#8212; diurnal parallax.</strong> On at "
                 "least four nights, photograph the Moon at 5&#176; altitude and at "
                 "its attainable maximum. Compare each diameter with the "
                 "<code>d(a)</code> computed for its own instant:"))
        A('<div class="eq">\n  d(a) = &#8730;( D&#178; &#8722; R&#178; cos&#178;a ) '
          '&#8722; R sin a\n  <span class="cap">a = apparent altitude; D = geocentric '
          'distance from the ephemeris; R = 6&#8239;371 km. Apparent diameter varies '
          'as 1/d(a).</span>\n</div>')
        A(tableau("Table 2 &#8212; Expected signal of control B between a frame at "
                  "5&#176; and one at the attainable maximum. Four nights carry the "
                  "result beyond 6 &#963;.",
                  ["latitude", "max. altitude", "predicted signal"],
                  t_latitudes(fr)))
        A(tableau("Table 3 &#8212; Maximum orbital drift between the low and high "
                  "frames, to be compared with the signal.",
                  ["interval", "max. drift", "share of signal"], t_derive(fr)))
        A(clause("8.3", "<strong>Do not proceed to the Sun</strong> until 8.1 has "
                 "given a slope of 1.000 and 8.2 has recovered the signal predicted "
                 "for the station's latitude."))
        A(clause("8.4", "Measure the <strong>width</strong> of the disk only, "
                 "perpendicular to the local vertical."))
        A(clause("8.5", "<strong>Acquire twelve paired series</strong>: six ascending "
                 "in the morning, six descending in the afternoon, at apparent "
                 "altitudes of %s&#176; and at the day's maximum. Twenty frames per "
                 "series, to be stacked." % ", ".join(str(h) for h in HAUTEURS)))
        A(clause("8.6", "For each series, note UTC time to the second. The altitude "
                 "follows from the ephemeris. <strong>Use the apparent, refracted "
                 "altitude</strong>, not the true altitude: the departure is 0.40 per "
                 "cent on <code>sin &#945;</code> at 15&#176;, 0.22 per cent at "
                 "20&#176;, 0.09 per cent at 30&#176;."))
        A(clause("8.7", "<strong>Read the scale from the drift.</strong> Camera fixed, "
                 "no tracking: the disk drifts at 15.041&#8243;/s &#215; cos &#948;, "
                 "or 4.9 pixels per second at %d mm. A ten-second burst at each series "
                 "gives the angular scale of the moment without knowing the focal "
                 "length." % FOCALE))
        A(clause("8.8", "<strong>Change nothing.</strong> Focal length, focus and "
                 "filter remain identical throughout. Exposure may vary; the criterion "
                 "of 9.1 neutralises it."))
        A(clause("8.9", "<strong>Rejection criterion.</strong> For each paired "
                 "altitude, the morning/afternoon discrepancy shall stay below "
                 "<strong>%s per cent</strong> (3&#963;). Beyond that the run is "
                 "rejected and repeated, <strong>whatever the value of the "
                 "ratio</strong>. Causes to rule out: fixed brightness threshold "
                 "instead of the 50 per cent criterion, vertical diameter measured "
                 "instead of horizontal, focal length changed mid-run, cropping, "
                 "automatic distortion correction left enabled."
                 % nb(REJET, 2, fr)))
        A(clause("8.10", "Record the disk's width/height ratio at each series. It "
                 "measures the refraction of the moment and allows a series taken in "
                 "an abnormal regime to be rejected."))

    # ── 9 Calcul ─────────────────────────────────────────────────────────────
    A(h2(9, fr))
    if fr:
        A(clause("9.1", "<strong>Crit&#232;re des 50&#160;%.</strong> Tracer le profil "
                 "d'intensit&#233; le long d'un diam&#232;tre horizontal et prendre "
                 "le bord l&#224; o&#249; l'intensit&#233; vaut la moiti&#233; entre "
                 "le fond de ciel et le plateau du disque. Ne pas employer de seuil "
                 "fixe."))
        A(clause("9.2", "Convertir en minutes d'arc par l'&#233;chelle relev&#233;e "
                 "au 8.7 pour la s&#233;rie consid&#233;r&#233;e."))
        A(clause("9.3", "Former <code>r = &#952;(bas)/&#952;(haut)</code> entre la "
                 "plus basse et la plus haute hauteur atteintes, chaque "
                 "<code>&#952;</code> &#233;tant la moyenne des deux s&#233;ries "
                 "appari&#233;es de cette hauteur."))
        A(clause("9.4", "La variation de distance vaut <code>1/r &#8722; 1</code>."))
        A(clause("9.5", "&#201;valuer l'incertitude selon 2.1, avec au minimum les "
                 "composantes du tableau 4."))
        A(tableau("Tableau 4 &#8212; Budget d'erreur &#224; %d mm sur capteur plein "
                  "format &#233;chantillonn&#233; &#224; %s pixels."
                  % (FOCALE, mil(PIXELS, fr)),
                  ["source", "contribution"], t_budget(fr)))
    else:
        A(clause("9.1", "<strong>50 per cent criterion.</strong> Trace the intensity "
                 "profile along a horizontal diameter and take the edge where the "
                 "intensity is half way between sky background and disk plateau. Do "
                 "not use a fixed threshold."))
        A(clause("9.2", "Convert to arcminutes using the scale read at 8.7 for the "
                 "series concerned."))
        A(clause("9.3", "Form <code>r = &#952;(low)/&#952;(high)</code> between the "
                 "lowest and highest altitudes reached, each <code>&#952;</code> being "
                 "the mean of the two paired series at that altitude."))
        A(clause("9.4", "The distance change is <code>1/r &#8722; 1</code>."))
        A(clause("9.5", "Evaluate the uncertainty per 2.1, with at minimum the "
                 "components of Table 4."))
        A(tableau("Table 4 &#8212; Error budget at %d mm on a full-frame sensor "
                  "sampled at %s pixels." % (FOCALE, mil(PIXELS, fr)),
                  ["source", "contribution"], t_budget(fr)))

    # ── 10 Rapport d'essai ───────────────────────────────────────────────────
    A(h2(10, fr))
    if fr:
        A(clause("10.1", "Le rapport mentionne&#160;:"))
        A("<ul>\n"
          "  <li>position de la station, date, heures UTC de chaque s&#233;rie&#160;;</li>\n"
          "  <li>focale, ouverture, temps de pose, densit&#233; du filtre&#160;;</li>\n"
          "  <li>l'&#233;chelle angulaire relev&#233;e par d&#233;rive &#224; chaque "
          "s&#233;rie&#160;;</li>\n"
          "  <li>les douze diam&#232;tres, avec la hauteur apparente de chacun&#160;;</li>\n"
          "  <li>l'&#233;cart matin/apr&#232;s-midi de chaque couple, et sa comparaison "
          "au seuil du 8.9&#160;;</li>\n"
          "  <li><code>r</code> et son incertitude &#233;largie (k = 2), puis "
          "<code>1/r &#8722; 1</code>&#160;;</li>\n"
          "  <li>le rapport largeur/hauteur de chaque s&#233;rie&#160;;</li>\n"
          "  <li>les r&#233;sultats des contr&#244;les A et B&#160;;</li>\n"
          "  <li>temp&#233;rature, pression, humidit&#233;&#160;;</li>\n"
          "  <li>les fichiers bruts, publi&#233;s et accessibles.</li>\n</ul>")
        A(clause("10.2", "Le rapport <strong>ne conclut pas sur un mod&#232;le</strong>. "
                 "Il &#233;nonce <code>r</code> et la variation de distance."))
    else:
        A(clause("10.1", "The report shall state:"))
        A("<ul>\n"
          "  <li>station position, date, UTC times of each series;</li>\n"
          "  <li>focal length, aperture, exposure time, filter density;</li>\n"
          "  <li>the angular scale read from drift at each series;</li>\n"
          "  <li>the twelve diameters, with the apparent altitude of each;</li>\n"
          "  <li>the morning/afternoon discrepancy of each pair, and its comparison "
          "with the threshold of 8.9;</li>\n"
          "  <li><code>r</code> and its expanded uncertainty (k = 2), then "
          "<code>1/r &#8722; 1</code>;</li>\n"
          "  <li>the width/height ratio of each series;</li>\n"
          "  <li>the results of controls A and B;</li>\n"
          "  <li>temperature, pressure, humidity;</li>\n"
          "  <li>the raw files, published and accessible.</li>\n</ul>")
        A(clause("10.2", "The report <strong>shall not conclude on a model</strong>. "
                 "It states <code>r</code> and the distance change."))

    # ── 11 Fidélité et biais ─────────────────────────────────────────────────
    A(h2(11, fr))
    if fr:
        A(clause("11.1", "<strong>Fid&#233;lit&#233;.</strong> Aucune &#233;tude "
                 "interlaboratoires n'a &#233;t&#233; conduite &#224; ce jour. La "
                 "pr&#233;sente d&#233;claration sera compl&#233;t&#233;e d&#232;s que "
                 "trois op&#233;rateurs ind&#233;pendants auront appliqu&#233; la "
                 "m&#233;thode le m&#234;me jour."))
        A(clause("11.2", "<strong>Biais.</strong> L'assombrissement centre-bord et le "
                 "rougissement du limbe sont corr&#233;l&#233;s &#224; la hauteur et "
                 "constituent le seul biais syst&#233;matique connu&#160;; il est "
                 "port&#233; au tableau 4 pour 0,20&#160;%."))
        A(clause("11.3", "Le crit&#232;re de sym&#233;trie du 8.9 borne les biais "
                 "d&#233;pendant du temps &#8212; d&#233;rive thermique, mise au "
                 "point, transparence &#8212; sans les identifier "
                 "individuellement."))
    else:
        A(clause("11.1", "<strong>Precision.</strong> No interlaboratory study has "
                 "been conducted to date. This statement will be completed once three "
                 "independent operators have applied the method on the same day."))
        A(clause("11.2", "<strong>Bias.</strong> Limb darkening and reddening are "
                 "correlated with altitude and constitute the only known systematic "
                 "bias; it is carried in Table 4 at 0.20 per cent."))
        A(clause("11.3", "The symmetry criterion of 8.9 bounds time-dependent biases "
                 "&#8212; thermal drift, focus, transparency &#8212; without "
                 "identifying them individually."))

    # ── X1 Annexe ────────────────────────────────────────────────────────────
    A(h2_annexe(fr))
    if fr:
        A("<h3>X1.1 &#8212; Pourquoi le rapport, et non la taille</h3>")
        A("<p>Un astre de diam&#232;tre <code>D</code> port&#233; &#224; hauteur "
          "constante <code>H</code> au-dessus d'un plan est vu &#224; la distance "
          "<code>H/sin &#945;</code>, donc sous <code>&#952; = (D/H)&#183;sin "
          "&#945;</code>. Le rapport entre deux hauteurs vaut alors "
          "<code>sin &#945;&#8322;/sin &#945;&#8321;</code>&#160;: <strong>D et H "
          "s'&#233;liminent</strong>. Le rapport est donc pr&#233;dit sans qu'on "
          "connaisse ni la taille de l'astre ni son altitude, ce qui est la raison "
          "d'&#234;tre de la m&#233;thode.</p>")
        A("<p>Cette loi vaut pour <em>une</em> hypoth&#232;se de source proche, celle "
          "o&#249; la hauteur reste constante. Une variation qui ne la suivrait pas "
          "resterait une variation, et &#233;carterait tout autant une source dont la "
          "distance ne change pas. C'est pourquoi le tableau 1 ne d&#233;clare aucune "
          "valeur impossible.</p>")
        A("<h3>X1.2 &#8212; Pourquoi le diam&#232;tre horizontal</h3>")
        A("<p>La r&#233;fraction croissant vers le bas, le bord inf&#233;rieur du "
          "disque est relev&#233; davantage que le sup&#233;rieur. Calcul&#233; par la "
          "formule de Bennett (2.3), l'aplatissement atteint 19&#160;% au moment "
          "o&#249; le limbe inf&#233;rieur touche l'horizon, 17&#160;% lorsque le "
          "centre est &#224; un demi-degr&#233;, 13&#160;% &#224; un degr&#233;. Ce "
          "qui aplatit le disque n'est pas la r&#233;fraction mais son gradient.</p>")
        A("<p>&#192; azimut donn&#233;, la r&#233;fraction est en revanche la "
          "m&#234;me des deux c&#244;t&#233;s du disque et le d&#233;place en bloc. "
          "La largeur est donc l'observable propre, et le rapport largeur/hauteur "
          "mesur&#233; sur le m&#234;me clich&#233; fournit gratuitement une mesure de "
          "la r&#233;fraction du moment&#160;: 0,4&#160;% &#224; 15&#176;, "
          "0,9&#160;% &#224; 10&#176;, 3,7&#160;% &#224; 5&#176;, 23,6&#160;% &#224; "
          "2&#176;.</p>")
        A("<h3>X1.3 &#8212; Pourquoi les contr&#244;les se font sur la Lune</h3>")
        A("<p>Une mesure qui ne trouve rien ne prouve rien tant qu'on n'a pas "
          "&#233;tabli qu'elle aurait trouv&#233; quelque chose. La distance de la "
          "Lune varie r&#233;ellement, dans des proportions connues &#224; l'avance "
          "par &#233;ph&#233;m&#233;ride&#160;: elle fournit un &#233;talon de "
          "variation, ce que le Soleil ne peut pas &#234;tre.</p>")
        A("<p>Le contr&#244;le B tranche en outre par lui-m&#234;me&#160;: une source "
          "&#224; hauteur finie pr&#233;dirait, &#224; 15&#176; de hauteur, une Lune "
          "74&#160;% plus petite, quand la parallaxe diurne la donne 1,4&#160;% plus "
          "grande en haut qu'en bas. <strong>Les deux pr&#233;dictions sont de signe "
          "oppos&#233;.</strong> Il contredit au passage l'illusion lunaire&#160;: la "
          "Lune est r&#233;ellement plus petite &#224; l'horizon.</p>")
        A("<p>La distinction g&#233;ocentrique / topocentrique <em>est</em> le "
          "signal du contr&#244;le B. Les &#233;ph&#233;m&#233;rides publient par "
          "d&#233;faut la distance depuis le centre de la Terre&#160;; la correction "
          "qu'on omet d'ordinaire est pr&#233;cis&#233;ment la grandeur "
          "recherch&#233;e.</p>")
        A("<h3>X1.4 &#8212; Pourquoi le crit&#232;re de rejet est la sym&#233;trie</h3>")
        A("<p>Une variation g&#233;om&#233;trique ne d&#233;pend que de la hauteur. "
          "Une prise &#224; 40&#176; le matin et une prise &#224; 40&#176; "
          "l'apr&#232;s-midi doivent donc donner le m&#234;me diam&#232;tre, quelle "
          "que soit la nature de l'astre et quelle que soit la loi qu'il suit. Un "
          "artefact &#8212; d&#233;rive thermique du f&#251;t, mise au point, "
          "transparence, saturation &#8212; n'a aucune raison d'&#234;tre "
          "sym&#233;trique par rapport au midi solaire.</p>")
        A("<p>C'est cela, et non la valeur du rapport, qui s&#233;pare une mesure d'un "
          "rat&#233;. Un crit&#232;re fond&#233; sur la valeur supposerait connue la "
          "loi que suit l'astre&#160;; celui-ci ne suppose rien.</p>")
        A("<h3>X1.5 &#8212; Ce que la m&#233;thode n'&#233;tablit pas</h3>")
        A("<p>Elle ne donne ni la taille du Soleil, ni son altitude, ni sa distance. "
          "Un rapport inf&#233;rieur &#224; 1 signale une source dont la distance "
          "&#224; l'&#339;il varie au cours du jour&#160;; il ne dit pas de combien "
          "elle est &#233;loign&#233;e. Une station donne un profil de distance, "
          "jamais la distance elle-m&#234;me&#160;: il y faut une base.</p>")
        A("<p>Elle ne s&#233;pare pas une source lointaine d'une source dont la "
          "distance &#224; <em>chaque</em> observateur resterait constante par "
          "construction &#8212; une image form&#233;e par une couche atmosph&#233;rique, "
          "ou une projection propre &#224; l'&#339;il qui la regarde. Les deux "
          "pr&#233;disent la m&#234;me constance, et aucune mesure d'un observateur "
          "isol&#233; ne les distingue.</p>")
        A("<p>Deux stations simultan&#233;es referment cette sortie, &#224; des "
          "hauteurs solaires diff&#233;rentes, la tol&#233;rance de "
          "simultan&#233;it&#233; &#233;tant large &#8212; le Soleil ne se "
          "d&#233;place que de 0,25&#176; par minute.</p>")
        A(tableau("Tableau X1.1 &#8212; Ce que chaque hypoth&#232;se pr&#233;dit pour "
                  "deux stations simultan&#233;es, l'une voyant le Soleil &#224; "
                  "60&#176;, l'autre &#224; 20&#176;.",
                  ["hypoth&#232;se", "station &#224; 60&#176;",
                   "station &#224; 20&#176;", "rapport"],
                  [ligne(["distance constante", "31,5&#8242;", "31,5&#8242;", "1,000"]),
                   ligne(["hauteur constante au-dessus d'un plan", "27,3&#8242;",
                          "10,8&#8242;", "0,395"]),
                   ligne(["image propre &#224; l'observateur", "?", "?",
                          "&#224; &#233;noncer"])]))
        A("<p>Une hypoth&#232;se qui ne dit pas ce qu'elle pr&#233;dit ici ne "
          "pr&#233;dit rien, et cesse par l&#224; d'&#234;tre testable. Le dispositif "
          "ne co&#251;te qu'un second participant et s'ex&#233;cute avec le m&#234;me "
          "mat&#233;riel.</p>")
    else:
        A("<h3>X1.1 &#8212; Why the ratio, and not the size</h3>")
        A("<p>A body of diameter <code>D</code> held at constant height <code>H</code> "
          "above a plane is seen at distance <code>H/sin &#945;</code>, hence at "
          "<code>&#952; = (D/H)&#183;sin &#945;</code>. The ratio between two "
          "altitudes is then <code>sin &#945;&#8322;/sin &#945;&#8321;</code>: "
          "<strong>D and H cancel</strong>. The ratio is therefore predicted without "
          "knowing either the body's size or its height, which is the method's reason "
          "for existing.</p>")
        A("<p>That law holds for <em>one</em> near-source hypothesis, the one where "
          "the height stays constant. A variation that did not follow it would still "
          "be a variation, and would rule out a source of unchanging distance just as "
          "firmly. This is why Table 1 declares no value impossible.</p>")
        A("<h3>X1.2 &#8212; Why the horizontal diameter</h3>")
        A("<p>Refraction increasing downwards, the lower limb is raised more than the "
          "upper. Computed from Bennett's formula (2.3), the flattening reaches 19 per "
          "cent when the lower limb touches the horizon, 17 per cent when the centre "
          "is at half a degree, 13 per cent at one degree. What flattens the disk is "
          "not refraction but its gradient.</p>")
        A("<p>At a given azimuth, by contrast, refraction is the same on both sides of "
          "the disk and displaces it as a whole. Width is therefore the proper "
          "observable, and the width/height ratio measured on the same frame supplies a "
          "free measurement of the refraction of the moment: 0.4 per cent at 15&#176;, "
          "0.9 at 10&#176;, 3.7 at 5&#176;, 23.6 at 2&#176;.</p>")
        A("<h3>X1.3 &#8212; Why the controls are done on the Moon</h3>")
        A("<p>A measurement that finds nothing proves nothing until it has been "
          "established that it would have found something. The Moon's distance really "
          "does vary, in proportions known in advance from the ephemeris: it supplies "
          "a standard of variation, which the Sun cannot be.</p>")
        A("<p>Control B moreover decides by itself: a source at finite height would "
          "predict, at 15&#176; altitude, a Moon 74 per cent smaller, whereas diurnal "
          "parallax gives it 1.4 per cent larger high than low. <strong>The two "
          "predictions are of opposite sign.</strong> It contradicts the moon illusion "
          "in passing: the Moon is really smaller at the horizon.</p>")
        A("<p>The geocentric / topocentric distinction <em>is</em> the signal of "
          "control B. Ephemerides publish by default the distance from the Earth's "
          "centre; the correction usually omitted is precisely the quantity "
          "sought.</p>")
        A("<h3>X1.4 &#8212; Why the rejection criterion is symmetry</h3>")
        A("<p>A geometric variation depends on altitude alone. A frame at 40&#176; in "
          "the morning and one at 40&#176; in the afternoon must therefore give the "
          "same diameter, whatever the body's nature and whatever law it follows. An "
          "artefact &#8212; thermal drift of the barrel, focus, transparency, "
          "saturation &#8212; has no reason to be symmetric about solar noon.</p>")
        A("<p>That, and not the value of the ratio, is what separates a measurement "
          "from a failure. A criterion based on the value would presuppose the law the "
          "body follows; this one presupposes nothing.</p>")
        A("<h3>X1.5 &#8212; What the method does not establish</h3>")
        A("<p>It gives neither the Sun's size, nor its altitude, nor its distance. A "
          "ratio below 1 signals a source whose distance to the eye varies through the "
          "day; it does not say how far away it is. One station gives a distance "
          "profile, never the distance itself: that requires a baseline.</p>")
        A("<p>It does not separate a distant source from one whose distance to "
          "<em>each</em> observer would stay constant by construction &#8212; an image "
          "formed by an atmospheric layer, or a projection proper to the eye that "
          "beholds it. Both predict the same constancy, and no measurement by a single "
          "observer tells them apart.</p>")
        A("<p>Two simultaneous stations close that exit, at different solar altitudes, "
          "the simultaneity tolerance being wide &#8212; the Sun moves only 0.25&#176; "
          "per minute.</p>")
        A(tableau("Table X1.1 &#8212; What each hypothesis predicts for two "
                  "simultaneous stations, one seeing the Sun at 60&#176;, the other at "
                  "20&#176;.",
                  ["hypothesis", "station at 60&#176;", "station at 20&#176;",
                   "ratio"],
                  [ligne(["constant distance", "31.5&#8242;", "31.5&#8242;", "1.000"]),
                   ligne(["constant height above a plane", "27.3&#8242;", "10.8&#8242;",
                          "0.395"]),
                   ligne(["image proper to the observer", "?", "?", "to be stated"])]))
        A("<p>A hypothesis that does not say what it predicts here predicts nothing, "
          "and thereby ceases to be testable. The arrangement costs one further "
          "participant and runs on the same equipment.</p>")

    return "\n\n".join(T)


def main():
    quad = controle()
    ecrire(CIBLE, "Profil de distance du Soleil &#8212; m&#233;thode d'essai",
           corps(True), corps(False))
    print("Méthode d'essai écrite : content/protocoles/soleil-bilingue.html")
    print("  budget quadratique recalculé : %.2f %%" % quad)
    print("  seuil de rejet par symétrie  : %.2f %% (3σ)" % REJET)
    print("  structure : 1→11 + annexe X1, contrôle de récit passé")
    return 0


if __name__ == "__main__":
    sys.exit(main())
