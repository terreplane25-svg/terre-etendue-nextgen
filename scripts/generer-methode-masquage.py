#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Méthode d'essai « Portion masquée d'un objet éloigné ».

Remplace la méthode de visée terrestre longue, dont elle est la généralisation.

Ce qui change, et pourquoi
──────────────────────────
La méthode précédente était bâtie autour d'une visée de 493 km. C'était une
erreur de conception : rien n'oblige à aller si loin. Depuis une hauteur d'œil
de deux mètres, à trente kilomètres, une surface sphérique masque déjà
quarante et un mètres. La méthode s'applique donc à n'importe quel couple
(hauteur d'œil, distance) satisfaisant le seuil de la section 7.

Deux corrections à la liste des paramètres couramment donnée
────────────────────────────────────────────────────────────
On énonce d'ordinaire quatre paramètres : hauteur d'œil h, distance d, hauteur
de l'objet H, coefficient de réfraction k.

  · **H n'entre pas dans le calcul.** La portion masquée vaut c(h, d, k) et ne
    dépend pas de la hauteur de l'objet — vérifié dans controle(). H ne sert
    qu'à comparer : si c > H, rien de l'objet ne devrait se voir. L'observable
    est c, pas H.

  · **k n'est pas une donnée d'entrée, c'est le résultat.** Le fixer à 0,13
    revient à affirmer ce qu'on prétend établir. La méthode le déduit des
    mesures.

Et il manque à cette liste le paramètre qui invalide le plus de relevés : le
**profil du terrain intermédiaire**. La formule suppose que rien n'intervient
entre l'œil et la cible. Sur terre, il y a presque toujours quelque chose. C'est
la raison pour laquelle la méthode impose un plan d'eau.

Le cœur de la méthode : la mesure différentielle
────────────────────────────────────────────────
À distance fixe, on fait varier la hauteur d'œil.

  · Sur une surface courbe, la portion masquée décroît quand l'œil monte, d'une
    quantité prédite. À 30 km, elle passe de 47 m à 1 m de hauteur d'œil à 6 m
    à 30 m de hauteur d'œil.
  · Sur un plan à profil dégagé, la base de l'objet reste visible quelle que
    soit la hauteur d'œil : l'écart vaut **zéro, exactement, sans paramètre
    ajustable**.

Ce dispositif règle en outre le seul confusionnisme sérieux du test simple : la
brume. Un voile atmosphérique efface le bas d'un objet lointain et imite une
occultation. Mais la brume ne change guère quand on monte de vingt mètres, là
où l'occultation change beaucoup — et elle s'efface graduellement quand
l'occultation coupe net à une hauteur définie.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from methode_essai import (PROTOCOLES, clause, ecrire, encadre, h2, h2_annexe,
                           ligne, masthead, mil, nb, tableau)      # noqa: E402

CIBLE = os.path.join(PROTOCOLES, "visee-terrestre-bilingue.html")

R = 6371.0
K_STANDARD = 0.13
SEUIL_MASQUAGE = 10.0      # m — signal minimal exigé pour que l'essai ait un sens
LECTURE_C = 2.0            # m — incertitude de lecture visée sur c
HAUTEURS = [1, 2, 5, 10, 20, 50]
DISTANCES = [10, 20, 30, 50, 80]
DIFF_D = [10, 15, 20, 30, 40, 50]
H_BAS, H_HAUT = 1, 20
K_MAX = 0.50               # borne haute admissible hors conduit
JOURS_MINI = 3             # journées à conditions thermiques distinctes

# Les régimes de réfraction, et ce qu'ils autorisent. La dernière ligne est la
# raison pour laquelle un seul relevé ne suffit jamais : au-delà de k = 1, le
# rayon se courbe plus que la surface et des objets normalement masqués
# redeviennent visibles.
REGIMES = [
    (0.00, "aucune r&#233;fraction", "no refraction",
     "borne g&#233;om&#233;trique inf&#233;rieure", "lower geometric bound"),
    (0.13, "standard optique", "standard optical",
     "atmosph&#232;re ordinaire", "ordinary atmosphere"),
    (0.25, "4/3 R, standard radio", "4/3 R, radio standard",
     "gradient renforc&#233;", "enhanced gradient"),
    (0.50, "inversion forte au ras de l'eau", "strong inversion above water",
     "borne haute retenue", "upper bound adopted"),
    (1.00, "conduit, mirage sup&#233;rieur", "duct, superior mirage",
     "le test de 8.6 le d&#233;tecte", "detected by the test of 8.6"),
]


def cachee(h_m, d_km, k):
    """Portion masquée depuis la base de la cible, en mètres."""
    Rp = R / (1 - k)
    h = h_m / 1000.0
    a = math.sqrt((Rp + h) ** 2 - Rp ** 2)
    return 0.0 if d_km <= a else (math.sqrt(Rp ** 2 + (d_km - a) ** 2) - Rp) * 1000.0


def k_pour(h, d, c):
    lo, hi = 0.0, 0.999
    for _ in range(300):
        m = (lo + hi) / 2
        if cachee(h, d, m) > c:
            lo = m
        else:
            hi = m
    return hi


def d_minimale(h, seuil=SEUIL_MASQUAGE):
    for d in range(1, 400):
        if cachee(h, d, K_STANDARD) >= seuil:
            return d
    return None


def controle():
    # 1. La portion masquée ne dépend pas de la hauteur de l'objet : la fonction
    #    ne la prend pas en argument, et c'est le point à démontrer au lecteur.
    assert "H" not in cachee.__code__.co_varnames
    # 2. Les valeurs imprimées.
    assert abs(cachee(2, 30, K_STANDARD) - 41.3) < 0.3
    assert abs(cachee(1, 30, K_STANDARD) - 46.8) < 0.3
    assert abs(cachee(30, 30, K_STANDARD) - 5.6) < 0.3
    assert abs(cachee(2, 50, K_STANDARD) - 136) < 1
    # 3. Sur un plan, rien n'est masqué : c'est la limite k → 1 de la formule,
    #    et le modèle plan la donne exactement, sans paramètre.
    assert cachee(2, 30, 0.999) < 1.0
    # 4. Le k qu'il faudrait pour voir la base.
    assert abs(k_pour(2, 20, 0.0) - 0.936) < 0.003
    assert abs(k_pour(2, 30, 0.0) - 0.972) < 0.003
    assert abs(k_pour(10, 30, 0.0) - 0.858) < 0.003
    # 5. Le seuil de distance par hauteur d'œil.
    assert d_minimale(1) == 16 and d_minimale(2) == 18 and d_minimale(20) == 30
    # 6. La sensibilité : lire c à ±2 m sépare k à mieux que ±0,02 à 30 km.
    ecart = cachee(1, 30, K_STANDARD) - cachee(1, 30, K_STANDARD + 0.02)
    assert ecart > LECTURE_C / 2, ecart
    return True


def t_masquage(fr):
    return [ligne(["%d m" % h] + [nb(cachee(h, d, K_STANDARD), 0, fr) + " m"
                                  for d in DISTANCES], h == 2)
            for h in HAUTEURS]


def t_differentiel(fr):
    lignes = []
    for d in DIFF_D:
        bas, haut = cachee(H_BAS, d, K_STANDARD), cachee(H_HAUT, d, K_STANDARD)
        lignes.append(ligne(["%d km" % d, nb(bas, 1, fr) + " m",
                             nb(haut, 1, fr) + " m", nb(bas - haut, 1, fr) + " m",
                             nb(0.0, 1, fr) + " m"],
                            d == 30))
    return lignes


def t_seuil(fr):
    return [ligne(["%d m" % h, "%d km" % d_minimale(h),
                   nb(cachee(h, d_minimale(h), K_STANDARD), 0, fr) + " m"], h == 2)
            for h in HAUTEURS]


def t_k(fr):
    cas = [(2, 10), (2, 20), (2, 30), (10, 30), (10, 50), (30, 80)]
    return [ligne(["%d m" % h, "%d km" % d, nb(k_pour(h, d, 0.0), 3, fr),
                   ("oui" if k_pour(h, d, 0.0) <= K_MAX else "non") if fr
                   else ("yes" if k_pour(h, d, 0.0) <= K_MAX else "no")],
                  (h, d) == (2, 30)) for h, d in cas]


def t_regimes(fr):
    return [ligne([nb(k, 2, fr), lfr if fr else len_, cfr if fr else cen],
                  abs(k - K_MAX) < 1e-9)
            for k, lfr, len_, cfr, cen in REGIMES]


def corps(fr):
    T = []
    A = T.append
    A(masthead(fr,
               "Portion masqu&#233;e d'un objet &#233;loign&#233;" if fr
               else "Hidden portion of a distant object",
               ("D&#233;termination du coefficient de r&#233;fraction rendant compte "
                "d'une observation, &#224; distance et hauteur libres" if fr else
                "Determination of the refraction coefficient accounting for an "
                "observation, at free distance and height"), "3.0"))

    # ── 1 Domaine d'application ─────────────────────────────────────────────
    A(h2(1, fr))
    if fr:
        A(clause("1.1", "La pr&#233;sente m&#233;thode d&#233;termine la "
                 "<strong>portion masqu&#233;e</strong> <code>c</code> &#224; la base "
                 "d'un objet &#233;loign&#233;, et le <strong>coefficient de "
                 "r&#233;fraction</strong> <code>k</code> qui en rend compte."))
        A(clause("1.2", "La hauteur d'&#339;il et la distance sont "
                 "<strong>libres</strong>, sous la seule condition du 7.5. Elles ne "
                 "sont pas impos&#233;es par la m&#233;thode."))
        A(clause("1.3", "Elle comporte deux d&#233;terminations&#160;: une mesure "
                 "&#224; hauteur unique (8.4) et une mesure "
                 "<strong>diff&#233;rentielle</strong> &#224; trois hauteurs d'&#339;il "
                 "au moins (8.5). La seconde est exig&#233;e&#160;; la premi&#232;re "
                 "seule ne conclut pas."))
        A(clause("1.4", "Elle <strong>conclut</strong> sur deux mod&#232;les "
                 "enti&#232;rement sp&#233;cifi&#233;s&#160;: une surface "
                 "<strong>sph&#233;rique de rayon 6&#8239;371 km</strong> assortie d'un "
                 "coefficient de r&#233;fraction admissible, et une surface "
                 "<strong>plane &#224; profil d&#233;gag&#233;</strong>. Le verdict est "
                 "&#233;nonc&#233; au 9.7, et chacun des deux mod&#232;les peut y "
                 "&#234;tre r&#233;fut&#233;."))
        A(clause("1.5", "Les valeurs sont exprim&#233;es en unit&#233;s SI."))
    else:
        A(clause("1.1", "This method determines the <strong>hidden portion</strong> "
                 "<code>c</code> at the base of a distant object, and the "
                 "<strong>refraction coefficient</strong> <code>k</code> that accounts "
                 "for it."))
        A(clause("1.2", "Eye height and distance are <strong>free</strong>, subject "
                 "only to the condition of 7.5. They are not imposed by the method."))
        A(clause("1.3", "It comprises two determinations: a single-height measurement "
                 "(8.4) and a <strong>differential</strong> measurement at three eye "
                 "heights at least (8.5). The second is required; the first alone does "
                 "not conclude."))
        A(clause("1.4", "It <strong>concludes</strong> on two fully specified models: a "
                 "<strong>spherical surface of radius 6&#8239;371 km</strong> with an "
                 "admissible refraction coefficient, and a <strong>plane surface with a "
                 "clear profile</strong>. The verdict is stated at 9.7, and either model "
                 "can be refuted there."))
        A(clause("1.5", "Values are expressed in SI units."))

    # ── 2 Documents de référence ────────────────────────────────────────────
    A(h2(2, fr))
    A(clause("2.1", "JCGM 100:2008 (GUM)."))
    A(clause("2.2", "ISO/IEC 17025:2017."))
    A(clause("2.3", "NOAA Technical Report NOS 92 NGS 22, <em>Results of Leveling "
             "Refraction Tests by the National Geodetic Survey</em>."))
    A(clause("2.4", "Service mar&#233;graphique national, pour le niveau d'eau "
             "instantan&#233; (7.3)." if fr else
             "National tide-gauge service, for the instantaneous water level (7.3)."))

    # ── 3 Terminologie ──────────────────────────────────────────────────────
    A(h2(3, fr))
    if fr:
        A("<p>3.1 <strong>hauteur d'&#339;il</strong>, <code>h</code>, <em>m</em> "
          "&#8212; hauteur du centre optique au-dessus de la surface de "
          "r&#233;f&#233;rence, mesur&#233;e au moment de la prise.</p>")
        A("<p>3.2 <strong>distance</strong>, <code>d</code>, <em>km</em> &#8212; "
          "distance g&#233;od&#233;sique entre l'&#339;il et la cible.</p>")
        A("<p>3.3 <strong>surface de r&#233;f&#233;rence</strong> &#8212; plan d'eau "
          "libre commun &#224; l'observateur et &#224; la base de la cible.</p>")
        A("<p>3.4 <strong>portion masqu&#233;e</strong>, <code>c</code>, <em>m</em> "
          "&#8212; hauteur, compt&#233;e depuis la base de la cible, du plus bas point "
          "encore visible.</p>")
        A("<p>3.5 <strong>rep&#232;re de hauteur</strong> &#8212; d&#233;tail de la "
          "cible dont la hauteur au-dessus de sa base est connue et "
          "publi&#233;e.</p>")
        A("<p>3.6 <strong>coefficient de r&#233;fraction</strong>, <code>k</code>, "
          "sans dimension &#8212; rapport de la courbure du rayon lumineux &#224; celle "
          "de la surface de r&#233;f&#233;rence.</p>")
    else:
        A("<p>3.1 <strong>eye height</strong>, <code>h</code>, <em>m</em> &#8212; "
          "height of the optical centre above the reference surface, measured at the "
          "moment of the exposure.</p>")
        A("<p>3.2 <strong>distance</strong>, <code>d</code>, <em>km</em> &#8212; "
          "geodetic distance between eye and target.</p>")
        A("<p>3.3 <strong>reference surface</strong> &#8212; free water surface common "
          "to the observer and the target's base.</p>")
        A("<p>3.4 <strong>hidden portion</strong>, <code>c</code>, <em>m</em> &#8212; "
          "height, counted from the target's base, of the lowest point still "
          "visible.</p>")
        A("<p>3.5 <strong>height marker</strong> &#8212; a detail of the target whose "
          "height above its base is known and published.</p>")
        A("<p>3.6 <strong>refraction coefficient</strong>, <code>k</code>, "
          "dimensionless &#8212; ratio of the curvature of the light ray to that of the "
          "reference surface.</p>")

    # ── 4 Résumé ────────────────────────────────────────────────────────────
    A(h2(4, fr))
    if fr:
        A(clause("4.1", "Une cible portant des rep&#232;res de hauteur connus est "
                 "photographi&#233;e depuis un point situ&#233; sur le m&#234;me plan "
                 "d'eau."))
        A(clause("4.2", "Le plus bas rep&#232;re visible est identifi&#233; et sa "
                 "hauteur relev&#233;e&#160;: c'est <code>c<sub>obs</sub></code>."))
        A(clause("4.3", "L'op&#233;ration est r&#233;p&#233;t&#233;e depuis au moins "
                 "trois hauteurs d'&#339;il diff&#233;rentes, &#224; la m&#234;me "
                 "distance et dans la m&#234;me heure."))
        A(clause("4.4", "On r&#233;sout <code>c(h, d, k) = c<sub>obs</sub></code> pour "
                 "chaque hauteur, puis on v&#233;rifie qu'un seul <code>k</code> rend "
                 "compte des trois."))
        A(clause("4.5", "Le r&#233;sultat d'essai est <code>k</code>, son incertitude, "
                 "et l'&#233;cart mesur&#233; entre la portion masqu&#233;e la plus "
                 "basse et la plus haute."))
    else:
        A(clause("4.1", "A target bearing known height markers is photographed from a "
                 "point on the same water surface."))
        A(clause("4.2", "The lowest visible marker is identified and its height read: "
                 "this is <code>c<sub>obs</sub></code>."))
        A(clause("4.3", "The operation is repeated from at least three different eye "
                 "heights, at the same distance and within the same hour."))
        A(clause("4.4", "<code>c(h, d, k) = c<sub>obs</sub></code> is solved for each "
                 "height, then it is verified that a single <code>k</code> accounts for "
                 "all three."))
        A(clause("4.5", "The test result is <code>k</code>, its uncertainty, and the "
                 "measured difference between the lowest and the highest hidden "
                 "portion."))

    # ── 5 Intérêt et emploi ─────────────────────────────────────────────────
    A(h2(5, fr))
    if fr:
        A(clause("5.1", "La portion masqu&#233;e vaut <code>c(h, d, k)</code>. Elle "
                 "<strong>ne d&#233;pend pas de la hauteur de l'objet</strong>&#160;: "
                 "celle-ci ne sert qu'&#224; comparer. Si <code>c</code> exc&#232;de la "
                 "hauteur de la cible, rien ne devrait s'en voir."))
        A(clause("5.2", "<strong>Il n'est pas n&#233;cessaire d'observer loin.</strong> "
                 "Le tableau 1 donne <code>c</code> au coefficient standard&#160;: "
                 "&#224; 2 m de hauteur d'&#339;il et 30 km, une surface de rayon "
                 "6&#8239;371 km masque d&#233;j&#224; "
                 "%s m." % nb(cachee(2, 30, K_STANDARD), 0, fr)))
        A(tableau("Tableau 1 &#8212; Portion masqu&#233;e, en m&#232;tres, au "
                  "coefficient standard <code>k</code> = 0,13.",
                  ["hauteur d'&#339;il"] + ["%d km" % d for d in DISTANCES],
                  t_masquage(fr)))
        A(clause("5.3", "<strong>Une surface plane &#224; profil d&#233;gag&#233; "
                 "pr&#233;dit <code>c</code> = 0 &#224; toute hauteur et &#224; toute "
                 "distance</strong>, exactement et sans param&#232;tre ajustable. "
                 "C'est la pr&#233;diction la plus rigide des deux."))
        A(clause("5.4", "L'&#233;cart entre deux hauteurs d'&#339;il est donc "
                 "l'observable d&#233;cisive&#160;: une surface courbe l'impose non "
                 "nul, un plan le donne nul."))
        A(tableau("Tableau 2 &#8212; &#201;cart de portion masqu&#233;e entre "
                  "%d m et %d m de hauteur d'&#339;il, &#224; <code>k</code> = 0,13."
                  % (H_BAS, H_HAUT),
                  ["distance", "c &#224; %d m" % H_BAS, "c &#224; %d m" % H_HAUT,
                   "&#233;cart", "&#233;cart, surface plane"],
                  t_differentiel(fr)))
    else:
        A(clause("5.1", "The hidden portion is <code>c(h, d, k)</code>. It "
                 "<strong>does not depend on the height of the object</strong>: that "
                 "serves only for comparison. If <code>c</code> exceeds the target's "
                 "height, none of it should be visible."))
        A(clause("5.2", "<strong>Long range is not required.</strong> Table 1 gives "
                 "<code>c</code> at the standard coefficient: at 2 m eye height and "
                 "30 km, a surface of radius 6&#8239;371 km already hides %s m."
                 % nb(cachee(2, 30, K_STANDARD), 0, fr)))
        A(tableau("Table 1 &#8212; Hidden portion, in metres, at the standard "
                  "coefficient <code>k</code> = 0.13.",
                  ["eye height"] + ["%d km" % d for d in DISTANCES],
                  t_masquage(fr)))
        A(clause("5.3", "<strong>A plane surface with a clear profile predicts "
                 "<code>c</code> = 0 at every height and every distance</strong>, "
                 "exactly and with no adjustable parameter. It is the more rigid of the "
                 "two predictions."))
        A(clause("5.4", "The difference between two eye heights is therefore the "
                 "decisive observable: a curved surface requires it non-zero, a plane "
                 "gives it zero."))
        A(tableau("Table 2 &#8212; Difference in hidden portion between %d m and %d m "
                  "eye height, at <code>k</code> = 0.13." % (H_BAS, H_HAUT),
                  ["distance", "c at %d m" % H_BAS, "c at %d m" % H_HAUT,
                   "difference", "difference, plane surface"],
                  t_differentiel(fr)))

    # ── 6 Appareillage ──────────────────────────────────────────────────────
    A(h2(6, fr))
    if fr:
        A(clause("6.1", "<strong>Appareil photographique</strong> et "
                 "t&#233;l&#233;objectif permettant de r&#233;soudre le rep&#232;re de "
                 "hauteur le plus fin de la cible. Enregistrement en donn&#233;es "
                 "brutes."))
        A(clause("6.2", "<strong>Tr&#233;pied</strong> et d&#233;clenchement "
                 "&#224; distance."))
        A(clause("6.3", "<strong>R&#233;cepteur GNSS</strong>, ou point dont les "
                 "coordonn&#233;es sont publi&#233;es, pour la position de la "
                 "station."))
        A(clause("6.4", "<strong>M&#232;tre ou t&#233;l&#233;m&#232;tre</strong> pour "
                 "la hauteur d'&#339;il au-dessus de l'eau, &#224; &#177; 0,1 m."))
        A(clause("6.5", "<strong>Thermom&#232;tre</strong> pour l'air et, si "
                 "possible, pour l'eau. L'&#233;cart entre les deux gouverne la "
                 "r&#233;fraction au ras de la surface."))
    else:
        A(clause("6.1", "<strong>Camera</strong> and telephoto lens able to resolve the "
                 "finest height marker on the target. Raw recording."))
        A(clause("6.2", "<strong>Tripod</strong> and remote release."))
        A(clause("6.3", "<strong>GNSS receiver</strong>, or a point with published "
                 "coordinates, for the station position."))
        A(clause("6.4", "<strong>Tape or rangefinder</strong> for the eye height above "
                 "the water, to &#177; 0.1 m."))
        A(clause("6.5", "<strong>Thermometer</strong> for the air and, if possible, for "
                 "the water. The difference between the two governs refraction close to "
                 "the surface."))

    # ── 7 Conditions d'essai ────────────────────────────────────────────────
    A(h2(7, fr, saut=True))
    if fr:
        A(encadre("La condition qui invalide le plus de relev&#233;s",
                  "  <p>La formule du 9.2 suppose que <strong>rien n'intervient</strong> "
                  "entre l'&#339;il et la cible. Sur terre, il y a presque toujours "
                  "quelque chose&#160;: une colline &#224; mi-parcours masque la base "
                  "d'une cible quelle que soit la forme de la Terre.</p>\n"
                  "  <p>Un relev&#233; dont le profil interm&#233;diaire n'est pas "
                  "&#233;tabli ne mesure rien. C'est pourquoi la m&#233;thode impose un "
                  "plan d'eau libre.</p>"))
        A(clause("7.1", "<strong>La vis&#233;e passe enti&#232;rement au-dessus d'un "
                 "plan d'eau libre</strong> &#8212; mer, grand lac, estuaire &#8212; "
                 "sans terre &#233;merg&#233;e ni ouvrage sur le trajet."))
        A(clause("7.2", "La base de la cible est <strong>&#224; la ligne d'eau</strong>, "
                 "sur le m&#234;me plan d'eau que la station."))
        A(clause("7.3", "Le <strong>niveau d'eau instantan&#233;</strong> est "
                 "relev&#233; aupr&#232;s du service mar&#233;graphique (2.4). En mer, "
                 "la mar&#233;e d&#233;place &#224; la fois la hauteur d'&#339;il et la "
                 "base de la cible."))
        A(clause("7.4", "La cible porte <strong>au moins trois rep&#232;res de hauteur "
                 "connus</strong>, r&#233;partis sur sa hauteur&#160;: &#233;tages, "
                 "bandes de peinture, plateformes, changement de section."))
        A(clause("7.5", "<strong>Condition de signal.</strong> Le couple choisi doit "
                 "donner, au coefficient standard, une portion masqu&#233;e d'au moins "
                 "<strong>%s m</strong>. Le tableau 3 donne la distance minimale par "
                 "hauteur d'&#339;il." % nb(SEUIL_MASQUAGE, 0, fr)))
        A(tableau("Tableau 3 &#8212; Distance minimale donnant %s m de portion "
                  "masqu&#233;e &#224; <code>k</code> = 0,13."
                  % nb(SEUIL_MASQUAGE, 0, fr),
                  ["hauteur d'&#339;il", "distance minimale", "portion masqu&#233;e"],
                  t_seuil(fr)))
        A(clause("7.6", "La mesure diff&#233;rentielle du 8.5 exige trois hauteurs "
                 "d'&#339;il couvrant un rapport d'au moins <strong>cinq</strong> "
                 "&#8212; par exemple 2, 6 et 20 m&#232;tres."))
        A(clause("7.7", "Air calme, et pr&#233;f&#233;rablement temp&#233;rature de "
                 "l'eau proche de celle de l'air. Une forte inversion au ras de l'eau "
                 "&#233;l&#232;ve <code>k</code>&#160;; ce n'est pas un motif de rejet, "
                 "mais elle doit &#234;tre consign&#233;e."))
    else:
        A(encadre("The condition that voids the most records",
                  "  <p>The formula of 9.2 assumes that <strong>nothing "
                  "intervenes</strong> between eye and target. On land there is almost "
                  "always something: a hill at mid-path hides a target's base whatever "
                  "the shape of the Earth.</p>\n"
                  "  <p>A record whose intervening profile is not established measures "
                  "nothing. This is why the method requires a free water surface.</p>"))
        A(clause("7.1", "<strong>The sight line passes entirely over a free water "
                 "surface</strong> &#8212; sea, large lake, estuary &#8212; with no "
                 "emerged land or structure on the path."))
        A(clause("7.2", "The target's base is <strong>at the water line</strong>, on "
                 "the same body of water as the station."))
        A(clause("7.3", "The <strong>instantaneous water level</strong> is obtained "
                 "from the tide-gauge service (2.4). At sea, the tide displaces both "
                 "the eye height and the target's base."))
        A(clause("7.4", "The target bears <strong>at least three known height "
                 "markers</strong>, distributed over its height: floors, paint bands, "
                 "platforms, change of section."))
        A(clause("7.5", "<strong>Signal condition.</strong> The chosen pair shall give, "
                 "at the standard coefficient, a hidden portion of at least "
                 "<strong>%s m</strong>. Table 3 gives the minimum distance per eye "
                 "height." % nb(SEUIL_MASQUAGE, 0, fr)))
        A(tableau("Table 3 &#8212; Minimum distance giving %s m of hidden portion at "
                  "<code>k</code> = 0.13." % nb(SEUIL_MASQUAGE, 0, fr),
                  ["eye height", "minimum distance", "hidden portion"], t_seuil(fr)))
        A(clause("7.6", "The differential measurement of 8.5 requires three eye heights "
                 "spanning a ratio of at least <strong>five</strong> &#8212; for "
                 "instance 2, 6 and 20 metres."))
        A(clause("7.7", "Calm air, and preferably a water temperature close to the "
                 "air's. A strong inversion just above the water raises <code>k</code>; "
                 "that is not a ground for rejection, but it shall be recorded."))

    # ── 8 Mode opératoire ───────────────────────────────────────────────────
    A(h2(8, fr))
    if fr:
        A(clause("8.1", "Relever la position de la station et celle de la cible, puis "
                 "calculer la distance g&#233;od&#233;sique."))
        A(clause("8.2", "Mesurer la hauteur d'&#339;il au-dessus de l'eau &#224; "
                 "&#177; 0,1 m, et noter l'heure."))
        A(clause("8.3", "Relever temp&#233;rature de l'air, temp&#233;rature de l'eau, "
                 "et niveau mar&#233;graphique."))
        A(clause("8.4", "<strong>Mesure &#224; hauteur unique.</strong> Photographier "
                 "la cible sans recadrage. Identifier le plus bas rep&#232;re de "
                 "hauteur visible et relever sa hauteur au-dessus de la base&#160;: "
                 "c'est <code>c<sub>obs</sub></code>. Si la base elle-m&#234;me est "
                 "visible, <code>c<sub>obs</sub></code> = 0."))
        A(clause("8.5", "<strong>Mesure diff&#233;rentielle &#8212; exig&#233;e.</strong> "
                 "R&#233;p&#233;ter 8.2 et 8.4 depuis au moins trois hauteurs "
                 "d'&#339;il satisfaisant 7.6, <strong>&#224; la m&#234;me distance et "
                 "dans la m&#234;me heure</strong>, sans changer d'objectif ni de "
                 "r&#233;glage."))
        A(clause("8.6", "<strong>Test de proportionnalit&#233; &#8212; exig&#233;.</strong> "
                 "Mesurer sur le clich&#233; l'&#233;cart angulaire entre chaque paire de "
                 "rep&#232;res de hauteur. Sous une atmosph&#232;re r&#233;guli&#232;re, "
                 "cet &#233;cart vaut <code>(z&#8322;&#8722;z&#8321;)/d</code> et ne "
                 "d&#233;pend <strong>ni de <code>k</code>, ni de la hauteur "
                 "d'&#339;il</strong>. Un &#233;cart mesur&#233; s'&#233;loignant de "
                 "plus de 10&#160;% de cette valeur signale un gradient non uniforme "
                 "&#8212; un conduit &#8212; et la formule du 9.2 ne s'applique "
                 "plus."))
        A(clause("8.7", "<strong>R&#233;p&#233;tition &#8212; exig&#233;e.</strong> La "
                 "s&#233;rie compl&#232;te est reprise sur au moins <strong>%d "
                 "journ&#233;es</strong> pr&#233;sentant des &#233;carts "
                 "air&#8722;eau distincts. Une occultation g&#233;om&#233;trique est "
                 "pr&#233;sente tous les jours&#160;; un conduit ne l'est pas."
                 % JOURS_MINI))
        A(clause("8.8", "Photographier &#233;galement la sc&#232;ne au grand angle, "
                 "avec des rep&#232;res proches identifiables, pour permettre &#224; un "
                 "tiers de v&#233;rifier la station et l'orientation."))
        A(encadre("Distinguer la brume de l'occultation",
                  "  <p>Un voile atmosph&#233;rique efface le bas d'un objet "
                  "lointain et imite une occultation. Deux signes les "
                  "s&#233;parent&#160;:</p>\n"
                  "  <ul>\n"
                  "    <li>l'occultation coupe <strong>net</strong>, &#224; une hauteur "
                  "d&#233;finie&#160;; la brume s'efface graduellement&#160;;</li>\n"
                  "    <li>l'occultation <strong>change beaucoup</strong> quand on "
                  "monte de vingt m&#232;tres&#160;; la brume, presque pas.</li>\n"
                  "  </ul>\n"
                  "  <p>C'est la seconde raison d'&#234;tre de la mesure "
                  "diff&#233;rentielle du 8.5.</p>"))
        A(clause("8.7", "<strong>Crit&#232;res de rejet.</strong> L'essai est "
                 "rejet&#233; si&#160;:"))
        A("<ul>\n"
          "  <li>le profil interm&#233;diaire n'est pas &#233;tabli comme "
          "d&#233;gag&#233; (7.1)&#160;;</li>\n"
          "  <li>le plus bas rep&#232;re visible ne peut pas &#234;tre "
          "identifi&#233; &#224; mieux que &#177; %s m&#160;;</li>\n"
          "  <li>le bord observ&#233; est graduel au point qu'on ne puisse pas lui "
          "assigner une hauteur (brume)&#160;;</li>\n"
          "  <li>les trois hauteurs d'&#339;il ne couvrent pas le rapport de cinq "
          "exig&#233; au 7.6&#160;;</li>\n"
          "  <li>plus d'une heure s&#233;pare la premi&#232;re et la derni&#232;re "
          "prise de la s&#233;rie diff&#233;rentielle.</li>\n"
          "</ul>" % nb(LECTURE_C, 0, fr))
    else:
        A(clause("8.1", "Record the position of the station and of the target, then "
                 "compute the geodetic distance."))
        A(clause("8.2", "Measure the eye height above the water to &#177; 0.1 m, and "
                 "note the time."))
        A(clause("8.3", "Record air temperature, water temperature, and tide-gauge "
                 "level."))
        A(clause("8.4", "<strong>Single-height measurement.</strong> Photograph the "
                 "target without cropping. Identify the lowest visible height marker and "
                 "read its height above the base: this is <code>c<sub>obs</sub></code>. "
                 "If the base itself is visible, <code>c<sub>obs</sub></code> = 0."))
        A(clause("8.5", "<strong>Differential measurement &#8212; required.</strong> "
                 "Repeat 8.2 and 8.4 from at least three eye heights satisfying 7.6, "
                 "<strong>at the same distance and within the same hour</strong>, "
                 "without changing lens or settings."))
        A(clause("8.6", "<strong>Proportionality test &#8212; required.</strong> Measure "
                 "on the frame the angular spacing between each pair of height markers. "
                 "Under a regular atmosphere that spacing equals "
                 "<code>(z&#8322;&#8722;z&#8321;)/d</code> and depends on <strong>neither "
                 "<code>k</code> nor the eye height</strong>. A measured spacing "
                 "departing by more than 10 per cent from that value signals a "
                 "non-uniform gradient &#8212; a duct &#8212; and the formula of 9.2 no "
                 "longer applies."))
        A(clause("8.7", "<strong>Repetition &#8212; required.</strong> The full series "
                 "is repeated on at least <strong>%d days</strong> showing distinct "
                 "air&#8722;water temperature differences. A geometric occultation is "
                 "present every day; a duct is not." % JOURS_MINI))
        A(clause("8.8", "Also photograph the scene at wide angle, with identifiable near "
                 "landmarks, so a third party can verify the station and the bearing."))
        A(encadre("Telling haze from occultation",
                  "  <p>An atmospheric veil erases the bottom of a distant object and "
                  "imitates an occultation. Two signs separate them:</p>\n"
                  "  <ul>\n"
                  "    <li>occultation cuts <strong>sharply</strong>, at a definite "
                  "height; haze fades gradually;</li>\n"
                  "    <li>occultation <strong>changes a great deal</strong> when one "
                  "climbs twenty metres; haze barely at all.</li>\n"
                  "  </ul>\n"
                  "  <p>This is the second reason for the differential measurement of "
                  "8.5.</p>"))
        A(clause("8.7", "<strong>Rejection criteria.</strong> The test is rejected if:"))
        A("<ul>\n"
          "  <li>the intervening profile is not established as clear (7.1);</li>\n"
          "  <li>the lowest visible marker cannot be identified to better than "
          "&#177; %s m;</li>\n"
          "  <li>the observed edge is so gradual that no height can be assigned to it "
          "(haze);</li>\n"
          "  <li>the three eye heights do not span the ratio of five required at "
          "7.6;</li>\n"
          "  <li>more than one hour separates the first and last exposure of the "
          "differential series.</li>\n"
          "</ul>" % nb(LECTURE_C, 0, fr))

    # ── 9 Calcul ────────────────────────────────────────────────────────────
    A(h2(9, fr))
    if fr:
        A(clause("9.1", "Corriger la hauteur d'&#339;il et la hauteur de base de la "
                 "cible du niveau mar&#233;graphique relev&#233; au 8.3."))
        A(clause("9.2", "Portion masqu&#233;e calcul&#233;e, pour un <code>k</code> "
                 "donn&#233;&#160;:"))
        A('<div class="eq">\n  R&#8242; = R / (1 &#8722; k)&#160;&#160;&#160;&#160;'
          'a = &#8730;[(R&#8242;+h)&#178; &#8722; R&#8242;&#178;]&#160;&#160;&#160;&#160;'
          'c = &#8730;[R&#8242;&#178; + (d&#8722;a)&#178;] &#8722; R&#8242;\n'
          '  <span class="cap">R = 6&#8239;371 km. a est la distance de l\'horizon. '
          'h, a, d et c en kilom&#232;tres, c converti en m&#232;tres au '
          'r&#233;sultat. Si d &#8804; a, alors c = 0.</span>\n</div>')
        A(clause("9.3", "Pour chaque hauteur d'&#339;il, r&#233;soudre "
                 "<code>c(h, d, k) = c<sub>obs</sub></code> par dichotomie sur "
                 "<code>k</code>."))
        A(clause("9.4", "<strong>V&#233;rifier la coh&#233;rence.</strong> Les trois "
                 "valeurs de <code>k</code> doivent s'accorder dans leurs "
                 "incertitudes. Si elles divergent, la r&#233;fraction n'&#233;tait pas "
                 "la m&#234;me d'une prise &#224; l'autre&#160;: le dire, ne pas "
                 "moyenner."))
        A(clause("9.5", "Reporter l'&#233;cart mesur&#233; entre la portion "
                 "masqu&#233;e &#224; la plus basse et &#224; la plus haute hauteur "
                 "d'&#339;il, avec son incertitude. C'est la grandeur que le tableau 2 "
                 "pr&#233;dit non nulle sur une surface courbe et exactement nulle sur "
                 "un plan."))
        A(clause("9.6", "&#201;valuer les incertitudes selon 2.1. Les composantes "
                 "minimales sont&#160;: lecture du rep&#232;re, hauteur d'&#339;il, "
                 "niveau d'eau, distance."))
        A(tableau("Tableau 4 &#8212; R&#233;gimes de r&#233;fraction. La ligne "
                  "surlign&#233;e est la <strong>borne haute admissible</strong> "
                  "retenue pour le verdict du 9.7.",
                  ["k", "r&#233;gime", "remarque"], t_regimes(fr)))
        A(tableau("Tableau 5 &#8212; Coefficient qu'il faudrait pour que la base de la "
                  "cible reste visible, et compatibilit&#233; avec la borne du "
                  "tableau 4.",
                  ["hauteur d'&#339;il", "distance", "k n&#233;cessaire",
                   "admissible&#160;?"], t_k(fr)))
        A(clause("9.7", "<strong>Verdict.</strong> Il s'&#233;nonce sur les deux "
                 "mod&#232;les du 1.4, et seulement si 7.1, 8.6 et 8.7 sont "
                 "satisfaits&#160;:"))
        A('<div class="two">\n'
          '  <div class="vc p">\n'
          '    <p class="h">k<sub>exig&#233;</sub> &gt; %s</p>\n'
          '    <p class="v">La sph&#232;re de 6&#8239;371 km est r&#233;fut&#233;e sur '
          'cette ligne</p>\n'
          '    <p>Aucun coefficient de r&#233;fraction admissible ne rend compte de ce '
          'qui est vu, le profil est d&#233;gag&#233;, la proportionnalit&#233; est '
          'respect&#233;e, et le r&#233;sultat tient sur %d journ&#233;es de conditions '
          'thermiques diff&#233;rentes.</p>\n'
          '  </div>\n'
          '  <div class="vc g">\n'
          '    <p class="h">&#233;cart diff&#233;rentiel &gt; 3&#963;</p>\n'
          '    <p class="v">Le plan &#224; profil d&#233;gag&#233; est '
          'r&#233;fut&#233;</p>\n'
          '    <p>Il pr&#233;dit un &#233;cart nul entre deux hauteurs d\'&#339;il, '
          'exactement et sans param&#232;tre ajustable. Un &#233;cart mesur&#233; non '
          'nul le r&#233;fute sans qu\'aucune valeur de <code>k</code> puisse le '
          'sauver.</p>\n'
          '  </div>\n'
          '</div>' % (nb(K_MAX, 2, fr), JOURS_MINI))
        A(encadre("Les deux mod&#232;les ne se r&#233;futent pas au m&#234;me prix",
                  "  <p>Le plan &#224; profil d&#233;gag&#233; pr&#233;dit "
                  "<strong>z&#233;ro, sans param&#232;tre libre</strong>&#160;: il "
                  "suffit d'un &#233;cart diff&#233;rentiel mesur&#233; pour le "
                  "r&#233;futer. La sph&#232;re dispose d'un param&#232;tre, "
                  "<code>k</code>&#160;; la r&#233;futer demande donc de le "
                  "<strong>borner</strong>, ce que fait le tableau 4, et d'&#233;carter "
                  "le conduit, ce que font 8.6 et 8.7.</p>\n"
                  "  <p>Cette asym&#233;trie n'est pas un parti pris&#160;: c'est la "
                  "structure des deux hypoth&#232;ses. Une pr&#233;diction rigide se "
                  "r&#233;fute plus facilement qu'une pr&#233;diction &#224; "
                  "param&#232;tre &#8212; et c'est le mod&#232;le plan qui porte ici la "
                  "pr&#233;diction rigide.</p>", "key"))
    else:
        A(clause("9.1", "Correct the eye height and the target's base height for the "
                 "tide level recorded at 8.3."))
        A(clause("9.2", "Calculated hidden portion, for a given <code>k</code>:"))
        A('<div class="eq">\n  R&#8242; = R / (1 &#8722; k)&#160;&#160;&#160;&#160;'
          'a = &#8730;[(R&#8242;+h)&#178; &#8722; R&#8242;&#178;]&#160;&#160;&#160;&#160;'
          'c = &#8730;[R&#8242;&#178; + (d&#8722;a)&#178;] &#8722; R&#8242;\n'
          '  <span class="cap">R = 6&#8239;371 km. a is the horizon distance. h, a, d '
          'and c in kilometres, c converted to metres in the result. If d &#8804; a, '
          'then c = 0.</span>\n</div>')
        A(clause("9.3", "For each eye height, solve "
                 "<code>c(h, d, k) = c<sub>obs</sub></code> by bisection on "
                 "<code>k</code>."))
        A(clause("9.4", "<strong>Check consistency.</strong> The three values of "
                 "<code>k</code> shall agree within their uncertainties. If they "
                 "diverge, refraction was not the same from one exposure to the next: "
                 "say so, do not average."))
        A(clause("9.5", "Report the measured difference between the hidden portion at "
                 "the lowest and at the highest eye height, with its uncertainty. This "
                 "is the quantity Table 2 predicts non-zero on a curved surface and "
                 "exactly zero on a plane."))
        A(clause("9.6", "Evaluate uncertainties per 2.1. The minimum components are: "
                 "marker reading, eye height, water level, distance."))
        A(tableau("Table 4 &#8212; Refraction regimes. The highlighted row is the "
                  "<strong>admissible upper bound</strong> adopted for the verdict of "
                  "9.7.", ["k", "regime", "remark"], t_regimes(fr)))
        A(tableau("Table 5 &#8212; Coefficient that would be required for the target's "
                  "base to remain visible, and compatibility with the bound of Table 4.",
                  ["eye height", "distance", "k required", "admissible?"], t_k(fr)))
        A(clause("9.7", "<strong>Verdict.</strong> It is stated on the two models of "
                 "1.4, and only if 7.1, 8.6 and 8.7 are satisfied:"))
        A('<div class="two">\n'
          '  <div class="vc p">\n'
          '    <p class="h">k<sub>required</sub> &gt; %s</p>\n'
          '    <p class="v">The 6&#8239;371 km sphere is refuted on this line</p>\n'
          '    <p>No admissible refraction coefficient accounts for what is seen, the '
          'profile is clear, proportionality holds, and the result stands over %d days '
          'of differing thermal conditions.</p>\n'
          '  </div>\n'
          '  <div class="vc g">\n'
          '    <p class="h">differential &gt; 3&#963;</p>\n'
          '    <p class="v">The plane with clear profile is refuted</p>\n'
          '    <p>It predicts a zero difference between two eye heights, exactly and '
          'with no adjustable parameter. A measured non-zero difference refutes it, and '
          'no value of <code>k</code> can save it.</p>\n'
          '  </div>\n'
          '</div>' % (nb(K_MAX, 2, fr), JOURS_MINI))
        A(encadre("The two models are not refuted at the same price",
                  "  <p>The plane with clear profile predicts <strong>zero, with no free "
                  "parameter</strong>: a single measured differential refutes it. The "
                  "sphere has one parameter, <code>k</code>; refuting it therefore "
                  "requires <strong>bounding</strong> it, which Table 4 does, and ruling "
                  "out ducting, which 8.6 and 8.7 do.</p>\n"
                  "  <p>That asymmetry is not a bias: it is the structure of the two "
                  "hypotheses. A rigid prediction is easier to refute than one with a "
                  "parameter &#8212; and here it is the plane model that carries the "
                  "rigid prediction.</p>", "key"))

    # ── 10 Rapport d'essai ──────────────────────────────────────────────────
    A(h2(10, fr))
    if fr:
        A(clause("10.1", "Le rapport mentionne&#160;:"))
        A("<ul>\n"
          "  <li>coordonn&#233;es de la station et de la cible, distance "
          "calcul&#233;e&#160;;</li>\n"
          "  <li>identification de la cible et liste des rep&#232;res de hauteur "
          "employ&#233;s, avec leur source&#160;;</li>\n"
          "  <li>les trois hauteurs d'&#339;il, mesur&#233;es et corrig&#233;es du "
          "niveau d'eau&#160;;</li>\n"
          "  <li>les trois <code>c<sub>obs</sub></code> et leurs incertitudes&#160;;</li>\n"
          "  <li>les trois <code>k</code> d&#233;duits, et leur accord ou "
          "d&#233;saccord&#160;;</li>\n"
          "  <li>l'&#233;cart de portion masqu&#233;e entre la plus basse et la plus "
          "haute hauteur d'&#339;il&#160;;</li>\n"
          "  <li>d&#233;monstration que le profil interm&#233;diaire est "
          "d&#233;gag&#233;&#160;;</li>\n"
          "  <li>heures UTC, temp&#233;ratures air et eau, niveau "
          "mar&#233;graphique&#160;;</li>\n"
          "  <li>focale, ouverture, temps de pose&#160;;</li>\n"
          "  <li>les fichiers bruts, publi&#233;s et accessibles.</li>\n</ul>")
        A(clause("10.2", "Le rapport <strong>ne conclut pas sur un mod&#232;le</strong>. "
                 "Il &#233;nonce <code>c<sub>obs</sub></code>, <code>k</code>, et "
                 "l'&#233;cart diff&#233;rentiel."))
    else:
        A(clause("10.1", "The report shall state:"))
        A("<ul>\n"
          "  <li>coordinates of station and target, computed distance;</li>\n"
          "  <li>target identification and the list of height markers used, with their "
          "source;</li>\n"
          "  <li>the three eye heights, measured and corrected for water level;</li>\n"
          "  <li>the three <code>c<sub>obs</sub></code> and their uncertainties;</li>\n"
          "  <li>the three derived <code>k</code>, and their agreement or "
          "disagreement;</li>\n"
          "  <li>the difference in hidden portion between the lowest and highest eye "
          "height;</li>\n"
          "  <li>demonstration that the intervening profile is clear;</li>\n"
          "  <li>UTC times, air and water temperatures, tide level;</li>\n"
          "  <li>focal length, aperture, exposure time;</li>\n"
          "  <li>the raw files, published and accessible.</li>\n</ul>")
        A(clause("10.2", "The report <strong>shall not conclude on a model</strong>. It "
                 "states <code>c<sub>obs</sub></code>, <code>k</code>, and the "
                 "differential."))

    # ── 11 Fidélité et biais ────────────────────────────────────────────────
    A(h2(11, fr))
    if fr:
        A(clause("11.1", "<strong>Fid&#233;lit&#233;.</strong> Aucune &#233;tude "
                 "interlaboratoires n'a &#233;t&#233; conduite &#224; ce jour."))
        A(clause("11.2", "<strong>Sensibilit&#233;.</strong> &#192; 30 km et 1 m de "
                 "hauteur d'&#339;il, lire <code>c<sub>obs</sub></code> &#224; "
                 "&#177; %s m s&#233;pare <code>k</code> &#224; mieux que "
                 "&#177; 0,02." % nb(LECTURE_C, 0, fr)))
        A(clause("11.3", "<strong>Biais.</strong> Le premier est l'obstruction du "
                 "profil interm&#233;diaire&#160;; il est &#233;limin&#233; par 7.1 et "
                 "non born&#233;. Le second est la brume, born&#233;e par le "
                 "crit&#232;re du 8.7. Le troisi&#232;me est l'inversion thermique au "
                 "ras de l'eau, qui &#233;l&#232;ve <code>k</code> et se lit dans le "
                 "d&#233;saccord des trois d&#233;terminations."))
    else:
        A(clause("11.1", "<strong>Precision.</strong> No interlaboratory study has been "
                 "conducted to date."))
        A(clause("11.2", "<strong>Sensitivity.</strong> At 30 km and 1 m eye height, "
                 "reading <code>c<sub>obs</sub></code> to &#177; %s m separates "
                 "<code>k</code> to better than &#177; 0.02." % nb(LECTURE_C, 0, fr)))
        A(clause("11.3", "<strong>Bias.</strong> The first is obstruction of the "
                 "intervening profile; it is eliminated by 7.1 and not bounded. The "
                 "second is haze, bounded by the criterion of 8.7. The third is thermal "
                 "inversion just above the water, which raises <code>k</code> and shows "
                 "in the disagreement of the three determinations."))

    # ── X1 Annexe ───────────────────────────────────────────────────────────
    A(h2_annexe(fr))
    if fr:
        A("<h3>X1.1 &#8212; Les param&#232;tres, et les deux qu'on &#233;nonce "
          "&#224; tort</h3>")
        A("<p>On donne d'ordinaire quatre param&#232;tres&#160;: hauteur d'&#339;il, "
          "distance, <em>hauteur de l'objet</em>, coefficient de r&#233;fraction. Deux "
          "de ces &#233;nonc&#233;s sont &#224; corriger.</p>")
        A("<p><strong>La hauteur de l'objet n'entre pas dans le calcul.</strong> La "
          "portion masqu&#233;e vaut <code>c(h, d, k)</code>&#160;: un pylône de "
          "dix m&#232;tres et une montagne de mille sont masqu&#233;s de la m&#234;me "
          "hauteur &#224; la m&#234;me distance. La hauteur de l'objet ne sert qu'&#224; "
          "comparer, et &#224; savoir s'il reste quelque chose &#224; voir.</p>")
        A("<p><strong>Le coefficient de r&#233;fraction n'est pas une donn&#233;e "
          "d'entr&#233;e, c'est le r&#233;sultat.</strong> Le fixer &#224; 0,13 revient "
          "&#224; affirmer ce qu'on pr&#233;tend &#233;tablir. Il varie de 0 &#224; plus "
          "de 0,5 selon le gradient thermique, et davantage encore au ras de l'eau. La "
          "m&#233;thode le d&#233;duit des mesures.</p>")
        A("<p>Il manque en revanche &#224; cette liste le param&#232;tre qui invalide le "
          "plus de relev&#233;s&#160;: <strong>le profil du terrain "
          "interm&#233;diaire</strong>. C'est l'objet de la section 7.</p>")
        A("<h3>X1.2 &#8212; Pourquoi il est inutile d'aller loin</h3>")
        A("<p>Le tableau 1 le montre&#160;: &#224; deux m&#232;tres de hauteur "
          "d'&#339;il et trente kilom&#232;tres, une surface de rayon 6&#8239;371 km "
          "masque %s m&#232;tres. La question ne demande donc ni expédition, ni "
          "altitude, ni conditions exceptionnelles&#160;: une plage, un phare et une "
          "dune suffisent.</p>" % nb(cachee(2, 30, K_STANDARD), 0, fr))
        A("<p>Le facteur qui compte n'est pas la distance mais la "
          "<strong>faiblesse de la hauteur d'&#339;il</strong>. L'horizon recule comme "
          "la racine de la hauteur&#160;; rester bas est ce qui rend le masquage "
          "grand.</p>")
        A("<h3>X1.3 &#8212; Pourquoi la mesure diff&#233;rentielle est exig&#233;e</h3>")
        A("<p>Une mesure &#224; hauteur unique donne un <code>k</code>, mais ne "
          "distingue pas une occultation d'un voile atmosph&#233;rique, et repose sur "
          "une seule lecture. Faire varier la hauteur d'&#339;il &#224; distance "
          "constante r&#232;gle les deux&#160;:</p>")
        A("<ul>\n"
          "  <li>la surface courbe impose un &#233;cart pr&#233;dit&#160;; le plan en "
          "impose un nul, <strong>exactement et sans param&#232;tre "
          "ajustable</strong>&#160;;</li>\n"
          "  <li>l'occultation change beaucoup avec la hauteur d'&#339;il, la brume "
          "presque pas&#160;;</li>\n"
          "  <li>trois lectures au lieu d'une donnent une dispersion, donc une "
          "incertitude mesur&#233;e plut&#244;t que suppos&#233;e.</li>\n"
          "</ul>")
        A("<h3>X1.4 &#8212; Pourquoi k doit &#234;tre born&#233; et le conduit "
          "&#233;cart&#233;</h3>")
        A("<p>Une observation isol&#233;e ne donne pas <code>R</code> mais "
          "<code>R&#8242; = R/(1&#8722;k)</code>&#160;: la courbure de la surface et "
          "celle du rayon lumineux entrent dans la m&#234;me quantit&#233; et ne s'en "
          "s&#233;parent pas. Un relev&#233; seul est donc muet &#8212; il admet "
          "n'importe quelle surface pourvu qu'on lui accorde le <code>k</code> "
          "correspondant.</p>")
        A("<p>Les trois clauses de la m&#233;thode sont ce qui referme cette "
          "libert&#233;, et c'est &#224; elles que le verdict du 9.7 doit d'&#234;tre "
          "prononçable&#160;:</p>")
        A("<ul>\n"
          "  <li>le <strong>tableau 4</strong> borne <code>k</code> &#224; %s, valeur "
          "au-del&#224; de laquelle aucun r&#233;gime atmosph&#233;rique ordinaire ne "
          "va&#160;;</li>\n"
          "  <li>le <strong>test de proportionnalit&#233; du 8.6</strong> "
          "&#233;carte le conduit, seul r&#233;gime capable de franchir cette "
          "borne&#160;;</li>\n"
          "  <li>la <strong>r&#233;p&#233;tition du 8.7</strong> distingue une "
          "occultation g&#233;om&#233;trique, pr&#233;sente tous les jours, d'un "
          "conduit qui ne l'est pas.</li>\n"
          "</ul>" % nb(K_MAX, 2, fr))
        A("<p>Sans ces trois clauses, un r&#233;sultat ne serait qu'une "
          "observation de plus. Avec elles, c'est une mesure opposable.</p>")
        A("<p>Si une application de la m&#233;thode trouve un &#233;cart "
          "diff&#233;rentiel nul l&#224; o&#249; le tableau 2 en pr&#233;dit un, ou un "
          "<code>k</code> compatible avec l'atmosph&#232;re ordinaire l&#224; o&#249; "
          "nous soutenons le contraire, ce r&#233;sultat sera publi&#233; tel quel avec "
          "ses donn&#233;es brutes, et les pages concern&#233;es seront "
          "corrig&#233;es.</p>")
    else:
        A("<h3>X1.1 &#8212; The parameters, and the two commonly misstated</h3>")
        A("<p>Four parameters are usually given: eye height, distance, <em>height of "
          "the object</em>, refraction coefficient. Two of those statements need "
          "correcting.</p>")
        A("<p><strong>The height of the object does not enter the "
          "calculation.</strong> The hidden portion is <code>c(h, d, k)</code>: a "
          "ten-metre mast and a thousand-metre mountain are hidden by the same height "
          "at the same distance. The object's height serves only for comparison, and to "
          "know whether anything is left to see.</p>")
        A("<p><strong>The refraction coefficient is not an input, it is the "
          "result.</strong> Fixing it at 0.13 amounts to asserting what one claims to "
          "establish. It varies from 0 to more than 0.5 with the thermal gradient, and "
          "further still just above water. The method derives it from the "
          "measurements.</p>")
        A("<p>What the list omits, on the other hand, is the parameter that voids the "
          "most records: <strong>the intervening terrain profile</strong>. That is the "
          "subject of section 7.</p>")
        A("<h3>X1.2 &#8212; Why long range is unnecessary</h3>")
        A("<p>Table 1 shows it: at two metres of eye height and thirty kilometres, a "
          "surface of radius 6&#8239;371 km hides %s metres. The question therefore "
          "demands neither expedition, nor altitude, nor exceptional conditions: a "
          "beach, a lighthouse and a dune suffice.</p>"
          % nb(cachee(2, 30, K_STANDARD), 0, fr))
        A("<p>The factor that matters is not distance but <strong>lowness of the "
          "eye</strong>. The horizon recedes as the square root of height; staying low "
          "is what makes the hiding large.</p>")
        A("<h3>X1.3 &#8212; Why the differential measurement is required</h3>")
        A("<p>A single-height measurement gives a <code>k</code>, but does not "
          "distinguish an occultation from an atmospheric veil, and rests on one "
          "reading. Varying the eye height at constant distance settles both:</p>")
        A("<ul>\n"
          "  <li>the curved surface requires a predicted difference; the plane requires "
          "zero, <strong>exactly and with no adjustable parameter</strong>;</li>\n"
          "  <li>occultation changes greatly with eye height, haze barely at all;</li>\n"
          "  <li>three readings instead of one give a scatter, hence a measured rather "
          "than assumed uncertainty.</li>\n"
          "</ul>")
        A("<h3>X1.4 &#8212; Why k must be bounded and ducting ruled out</h3>")
        A("<p>An isolated observation does not give <code>R</code> but "
          "<code>R&#8242; = R/(1&#8722;k)</code>: the curvature of the surface and that "
          "of the light ray enter the same quantity and do not separate within it. A "
          "single record is therefore mute &#8212; it admits any surface provided one "
          "grants it the matching <code>k</code>.</p>")
        A("<p>The method's three clauses are what close that freedom, and it is to them "
          "that the verdict of 9.7 owes being pronounceable:</p>")
        A("<ul>\n"
          "  <li><strong>Table 4</strong> bounds <code>k</code> at %s, beyond which no "
          "ordinary atmospheric regime goes;</li>\n"
          "  <li>the <strong>proportionality test of 8.6</strong> rules out ducting, the "
          "only regime able to cross that bound;</li>\n"
          "  <li>the <strong>repetition of 8.7</strong> distinguishes a geometric "
          "occultation, present every day, from a duct which is not.</li>\n"
          "</ul>" % nb(K_MAX, 2, fr))
        A("<p>Without these three clauses a result would be one more observation. With "
          "them, it is a measurement that can be contested on its merits.</p>")
        A("<p>If an application of the method finds a null differential where Table 2 "
          "predicts one, or a <code>k</code> consistent with the ordinary atmosphere "
          "where we maintain the contrary, that result will be published as it stands "
          "with its raw data, and the pages concerned will be corrected.</p>")

    return "\n\n".join(T)


def main():
    controle()
    ecrire(CIBLE, "Portion masqu&#233;e d'un objet &#233;loign&#233; "
           "&#8212; m&#233;thode d'essai", corps(True), corps(False))
    print("Méthode d'essai écrite : content/protocoles/visee-terrestre-bilingue.html")
    print("  h = 2 m, d = 30 km  →  %.0f m masqués (k = 0,13)"
          % cachee(2, 30, K_STANDARD))
    print("  écart différentiel 1 m → 20 m à 30 km : %.1f m (plan : 0 exactement)"
          % (cachee(1, 30, K_STANDARD) - cachee(20, 30, K_STANDARD)))
    print("  distance minimale pour 10 m de masquage :")
    for h in HAUTEURS:
        print("    h = %3d m → %2d km" % (h, d_minimale(h)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
