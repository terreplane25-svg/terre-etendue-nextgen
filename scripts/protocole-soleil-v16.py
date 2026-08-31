#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Protocole du diamètre solaire — passage de la version 1.5 à la version 1.6.

Ce que 1.6 change, et pourquoi.

La version 1.5 annonçait « 66 % d'écart entre les deux modèles ». Le chiffre est
juste, mais il est rapporté au **zénith**, une hauteur qu'un observateur hors des
tropiques n'atteint jamais. Il présuppose en outre qu'on sache où est le Soleil :
on ne prédit 66 % que si l'on tient déjà pour acquis qu'il est à une hauteur H
au-dessus d'un plan. Or le protocole est censé tester cela, pas en partir.

La version 1.6 ramène l'énoncé à ce que la mesure établit réellement. Elle
s'appuie sur un fait géométrique qui rend l'exigence tenable :

    astre de diamètre D à hauteur constante H, hauteur apparente α
    distance   d = H / sin α
    diamètre   θ = D / d = (D/H) · sin α
    rapport    θ(α₂) / θ(α₁) = sin α₂ / sin α₁

D et H se sont éliminés. Le **rapport** des diamètres entre deux hauteurs de la
même journée est donc prédit sans qu'on connaisse ni la taille de l'astre, ni son
altitude, ni sa distance. C'est exactement ce qu'on voulait : une prédiction qui
ne suppose rien de la nature du Soleil.

L'énoncé général, lui, ne suppose même plus le plan : le diamètre angulaire est
constant au cours de la journée si et seulement si la distance œil-astre est
constante. La question devient « cette distance change-t-elle ? », et la réponse
se lit sur un rapport de deux images.

Correction numérique au passage : 1.5 annonçait une constance à 4×10⁻³ % près
pour la source lointaine. Ce chiffre ne couvre que la parallaxe diurne (±R/UA).
Le déplacement orbital sur douze heures ajoute jusqu'à 1,4×10⁻² %. La borne
correcte est 2×10⁻² %, soit vingt-cinq fois plus petite que le budget d'erreur —
la conclusion ne bouge pas, mais le chiffre était faux.

Ce script n'est PAS idempotent : il remplace des passages précis de la 1.5. Le
relancer sur une 1.6 échoue proprement, chaque ancre étant vérifiée avant
écriture.
"""
import os
import re
import sys
from math import asin, degrees, radians, sin

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIBLE = os.path.join(RACINE, "content", "protocoles", "soleil-bilingue.html")

BUDGET = 0.51          # % à 1 σ, inchangé depuis la 1.5
UA = 149.6e6           # km
RAYON = 6371.0         # km
EXCENTRICITE = 0.0167

# Les couples de hauteurs d'une même journée. Le premier est le cas de référence.
COUPLES = [(70, 20), (70, 30), (60, 20), (60, 30), (50, 20),
           (40, 20), (60, 50), (70, 60), (30, 20)]


def rapport(haut, bas):
    return sin(radians(bas)) / sin(radians(haut))


def controle_numerique():
    """Refuse d'écrire si une seule valeur citée dans le texte est fausse."""
    # 1. Le rapport ne dépend ni de D ni de H.
    temoin = rapport(70, 20)
    for D, H in ((1, 100), (5, 100), (37, 6000), (0.5, 12000)):
        r = (D / H * sin(radians(20))) / (D / H * sin(radians(70)))
        assert abs(r - temoin) < 1e-12, (D, H, r)
    assert abs(temoin - 0.3640) < 5e-5, temoin
    assert abs(100 * (1 - temoin) - 63.6) < 0.05, temoin

    # 2. Les valeurs du tableau, telles qu'elles seront imprimées.
    attendu = {(70, 20): 63.6, (70, 30): 46.8, (60, 20): 60.5, (60, 30): 42.3,
               (50, 20): 55.4, (40, 20): 46.8, (60, 50): 11.5, (70, 60): 7.8,
               (30, 20): 31.6}
    for couple, val in attendu.items():
        calc = 100 * (1 - rapport(*couple))
        assert abs(calc - val) < 0.05, (couple, calc, val)

    # 3. La borne de la source lointaine sur une journée.
    parallaxe = 100 * RAYON / UA
    orbital = 100 * EXCENTRICITE * 2 * 3.14159265 / 365.25 * 0.5
    total = parallaxe + orbital
    assert abs(parallaxe - 0.0043) < 5e-5, parallaxe
    assert abs(orbital - 0.0144) < 5e-4, orbital
    assert 0.015 < total < 0.020, total

    # 4. L'écart de hauteur minimal pour un signal à 3 σ depuis 70°.
    seuil = 3 * BUDGET / 100
    bas = degrees(asin((1 - seuil) * sin(radians(70))))
    assert abs((70 - bas) - 2.3) < 0.1, bas

    # 5. Le rapport signal sur bruit du cas de référence.
    snr = 100 * (1 - rapport(70, 20)) / BUDGET
    assert abs(snr - 125) < 2, snr
    return round(snr)


def remplacer(src, ancre, neuf, etiquette):
    if src.count(ancre) != 1:
        sys.exit("ancre « %s » vue %d fois — attendu 1. Document déjà en 1.6 ?"
                 % (etiquette, src.count(ancre)))
    return src.replace(ancre, neuf)


def lignes_tableau(virgule):
    """Les lignes du tableau des couples, dans la langue demandée."""
    sep = "," if virgule else "."
    unite = "&#160;%" if virgule else " per cent"

    def nb(x, n):
        return ("%.*f" % (n, x)).replace(".", sep)

    out = []
    for haut, bas in COUPLES:
        r = rapport(haut, bas)
        red = 100 * (1 - r)
        vedette = (haut, bas) == (70, 20)
        g = (lambda t: "<strong>%s</strong>" % t) if vedette else (lambda t: t)
        cellules = [
            "%d&#176;" % haut,
            "%d&#176;" % bas,
            nb(r, 4),
            nb(red, 1) + unite,
            nb(1.0, 3),
            "%d" % round(red / BUDGET),
        ]
        out.append('    <tr%s>%s</tr>'
                   % (' class="hi"' if vedette else "",
                      "".join('<td class="n">%s</td>' % g(c) for c in cellules)))
    return "\n".join(out)


def main():
    snr = controle_numerique()
    src = open(CIBLE, encoding="utf-8").read()

    # ══ 1. Les deux chapeaux ════════════════════════════════════════════════
    src = remplacer(
        src,
        "<p class=\"dek\">Un observateur, une journ&#233;e, un t&#233;l&#233;objectif. "
        "&#201;cart pr&#233;dit entre les\n  deux mod&#232;les : 66 %. "
        "Pr&#233;cision requise : 1 %.</p>",
        "<p class=\"dek\">Un observateur, une journ&#233;e, un t&#233;l&#233;objectif. "
        "Le disque r&#233;tr&#233;cit-il\n  en descendant&#160;? &#201;cart pr&#233;dit entre "
        "les deux mod&#232;les, du plus haut au plus bas\n  du jour (70&#176;&#8594;20&#176;) : "
        "63,6 %. Budget d'erreur : 0,51 %.</p>",
        "dek FR")
    src = remplacer(
        src,
        "<p class=\"dek\">One observer, one day, one telephoto lens. Predicted gap "
        "between the two\n  models: 66 per cent. Required precision: 1 per cent.</p>",
        "<p class=\"dek\">One observer, one day, one telephoto lens. Does the disk "
        "shrink as it\n  descends? Predicted gap between the two models, from the day's "
        "highest point to its\n  lowest (70&#176;&#8594;20&#176;): 63.6 per cent. "
        "Error budget: 0.51 per cent.</p>",
        "dek EN")

    # ══ 2. Le premier paragraphe du résumé ══════════════════════════════════
    src = remplacer(
        src,
        "  <p>Tout mod&#232;le pla&#231;ant le Soleil &#224; une hauteur finie H au-dessus "
        "d'une surface plane\n  implique que la distance &#339;il-Soleil vaut "
        "<code>H / sin &#945;</code>, o&#249; &#945; est la hauteur\n  apparente de l'astre. "
        "Le diam&#232;tre angulaire doit donc varier comme <code>sin &#945;</code> :\n"
        "  &#224; 20&#176; de hauteur, le Soleil devrait para&#238;tre "
        "<strong>2,9 fois plus petit</strong> qu'au\n  z&#233;nith. Un mod&#232;le "
        "pla&#231;ant le Soleil &#224; 149,6 millions de kilom&#232;tres pr&#233;dit une\n"
        "  constance &#224; 4&#215;10<sup>&#8722;3</sup> % pr&#232;s sur une journ&#233;e.</p>",
        "  <p>Ce protocole ne mesure ni la taille du Soleil, ni son altitude, ni sa "
        "distance,\n  et ne suppose rien de sa nature. Il tranche une seule question&#160;: "
        "<strong>le diam&#232;tre\n  angulaire du Soleil change-t-il au cours d'une "
        "journ&#233;e&#160;?</strong> Le diam&#232;tre angulaire\n  d'un corps est le "
        "rapport de son diam&#232;tre &#224; sa distance&#160;; il reste constant si et\n"
        "  seulement si la distance &#224; l'&#339;il reste constante. Une source &#224; "
        "149,6 millions de\n  kilom&#232;tres satisfait cette condition &#224; "
        "2&#215;10<sup>&#8722;2</sup> % pr&#232;s en un jour&#160;: la\n  parallaxe "
        "diurne y vaut 4,3&#215;10<sup>&#8722;3</sup> % et le d&#233;placement orbital sur "
        "douze heures\n  1,4&#215;10<sup>&#8722;2</sup> %.</p>\n"
        "  <p>Une source &#224; hauteur finie ne la satisfait pas. Sa distance &#224; "
        "l'&#339;il vaut\n  <code>H / sin &#945;</code>, et le <strong>rapport</strong> des "
        "diam&#232;tres entre deux hauteurs de la\n  m&#234;me journ&#233;e vaut "
        "<code>sin &#945;&#8322; / sin &#945;&#8321;</code> &#8212; grandeur o&#249; le "
        "diam&#232;tre D et la\n  hauteur H se sont &#233;limin&#233;s. <strong>Le rapport "
        "est donc pr&#233;dit sans qu'on connaisse\n  rien de l'astre</strong>, et c'est lui "
        "que la campagne mesure. Du plus haut au plus bas\n  d'une journ&#233;e ordinaire "
        "de moyenne latitude (70&#176; puis 20&#176;), la famille locale\n  impose une "
        "r&#233;duction de <strong>63,6 %</strong> et la source lointaine "
        "<strong>z&#233;ro</strong>.</p>",
        "résumé §1 FR")
    src = remplacer(
        src,
        "  <p>Any model placing the Sun at a finite height H above a plane surface implies "
        "that the\n  eye-Sun distance is <code>H / sin &#945;</code>, where &#945; is the "
        "body's apparent altitude. The\n  angular diameter must therefore vary as "
        "<code>sin &#945;</code>: at 20&#176; elevation the Sun should\n  appear "
        "<strong>2.9 times smaller</strong> than at the zenith. A model placing the Sun at\n"
        "  149.6 million kilometres predicts constancy to within "
        "4&#215;10<sup>&#8722;3</sup> per cent over a\n  day.</p>",
        "  <p>This protocol measures neither the Sun's size, nor its altitude, nor its "
        "distance,\n  and assumes nothing about its nature. It settles one question: "
        "<strong>does the Sun's\n  angular diameter change over the course of a day?</strong> "
        "A body's angular diameter is the\n  ratio of its diameter to its distance; it stays "
        "constant if and only if the distance to\n  the eye stays constant. A source at 149.6 "
        "million kilometres meets that condition to\n  within 2&#215;10<sup>&#8722;2</sup> per "
        "cent in one day: diurnal parallax contributes\n  4.3&#215;10<sup>&#8722;3</sup> per "
        "cent and twelve hours of orbital motion "
        "1.4&#215;10<sup>&#8722;2</sup> per cent.</p>\n"
        "  <p>A source at finite height does not. Its distance to the eye is "
        "<code>H / sin &#945;</code>,\n  and the <strong>ratio</strong> of diameters between "
        "two altitudes of the same day is\n  <code>sin &#945;&#8322; / sin &#945;&#8321;</code> "
        "&#8212; a quantity in which the diameter D and the height H\n  have cancelled. "
        "<strong>The ratio is therefore predicted without knowing anything about\n  the "
        "body</strong>, and it is what the campaign measures. From the highest to the lowest "
        "point\n  of an ordinary mid-latitude day (70&#176; then 20&#176;), the local family "
        "requires a reduction\n  of <strong>63.6 per cent</strong> and the distant source "
        "<strong>zero</strong>.</p>",
        "résumé §1 EN")

    # ══ 3. Les deux dernières phrases du résumé ═════════════════════════════
    src = remplacer(
        src,
        "sur capteur plein format. Signal pr&#233;dit &#224; 20&#176; de hauteur : 66 %.\n"
        "  <strong>Rapport signal sur bruit &#8776; 130.</strong>",
        "sur capteur plein format. Signal pr&#233;dit du plus haut au plus bas du jour "
        "(70&#176;&#8594;20&#176;) : 63,6 %%.\n"
        "  <strong>Rapport signal sur bruit &#8776; %d.</strong>" % snr,
        "SNR résumé FR")
    src = remplacer(
        src,
        "400 mm on a full-frame sensor. Predicted signal at 20&#176; elevation: 66 per cent.\n"
        "  <strong>Signal-to-noise ratio &#8776; 130.</strong>",
        "400 mm on a full-frame sensor. Predicted signal from the day's highest to its lowest "
        "point (70&#176;&#8594;20&#176;): 63.6 per cent.\n"
        "  <strong>Signal-to-noise ratio &#8776; %d.</strong>" % snr,
        "SNR résumé EN")

    # ══ 4. L'encadré de bornage, ajouté après le résumé ═════════════════════
    borne_fr = (
        "\n<div class=\"box\">\n"
        "  <span class=\"lab\">Ce que ce protocole n'&#233;tablit pas</span>\n"
        "  <p>Il ne donne <strong>ni la taille du Soleil, ni son altitude, ni sa "
        "distance</strong>, et\n  n'en dit rien de sa nature. Une r&#233;duction "
        "mesur&#233;e signerait une source dont la distance\n  &#224; l'&#339;il varie au "
        "cours du jour&#160;; elle ne dirait pas de combien elle est &#233;loign&#233;e. "
        "Si\n  cette r&#233;duction suit <code>sin &#945;</code>, alors &#8212; et seulement "
        "alors &#8212; la hauteur H se\n  d&#233;duit d'une seconde station, ce qui est un "
        "autre protocole.</p>\n"
        "  <p>Il ne s&#233;pare pas non plus une source lointaine d'une source dont la "
        "distance &#224; <em>chaque</em>\n  observateur resterait constante par "
        "construction &#8212; une projection propre &#224; l'&#339;il qui la\n  regarde. Les "
        "deux pr&#233;disent la m&#234;me constance, et aucune mesure d'un observateur "
        "isol&#233;\n  ne les distingue. Ce que le protocole tranche, c'est l'existence "
        "d'un changement, pas ce\n  qui le produit.</p>\n"
        "</div>\n")
    borne_en = (
        "\n<div class=\"box\">\n"
        "  <span class=\"lab\">What this protocol does not establish</span>\n"
        "  <p>It yields <strong>neither the Sun's size, nor its altitude, nor its "
        "distance</strong>, and\n  says nothing of its nature. A measured reduction would "
        "indicate a source whose distance to\n  the eye varies through the day; it would not "
        "say how far away it is. If that reduction\n  follows <code>sin &#945;</code>, then "
        "&#8212; and only then &#8212; the height H follows from a second\n  station, which "
        "is a different protocol.</p>\n"
        "  <p>Nor does it separate a distant source from one whose distance to "
        "<em>each</em> observer\n  would stay constant by construction &#8212; a projection "
        "proper to the eye that beholds it.\n  Both predict the same constancy, and no "
        "measurement by a single observer tells them apart.\n  What the protocol settles is "
        "whether a change exists, not what produces it.</p>\n"
        "</div>\n")
    src = remplacer(src, "\n<h2><span class=\"n\">01</span>L'observable et sa "
                    "pr&#233;diction</h2>",
                    borne_fr + "\n<h2><span class=\"n\">01</span>L'observable et sa "
                    "pr&#233;diction</h2>", "encadré bornage FR")
    ancre_en = re.search(r"\n<h2><span class=\"n\">01</span>The observable[^<]*</h2>", src)
    if not ancre_en:
        sys.exit("titre 01 anglais introuvable")
    src = src.replace(ancre_en.group(0), borne_en + ancre_en.group(0))

    # ══ 5. Le tableau 1, refait sur des couples observables ═════════════════
    # Le tableau réécrit ressemble à celui qu'on cherche : sans repartir d'après
    # lui, la seconde passe réécrirait le premier au lieu du second.
    depuis = 0
    for langue, virgule, cap, entetes in (
            ("FR", True,
             "Tableau 1 &#8212; Ce que la famille locale impose entre les deux hauteurs "
             "extr&#234;mes\n  d'une m&#234;me journ&#233;e. Le rapport ne d&#233;pend ni de "
             "la taille de l'astre ni de son altitude&#160;:\n  ces deux grandeurs "
             "s'&#233;liminent. La derni&#232;re colonne est le rapport signal sur bruit pour "
             "un\n  budget de 0,51 %.",
             ("plus haute", "plus basse", "rapport pr&#233;dit<br>source locale",
              "r&#233;duction", "source<br>lointaine", "S/B")),
            ("EN", False,
             "Table 1 &#8212; What the local family requires between the two extreme "
             "altitudes of a\n  single day. The ratio depends neither on the body's size nor "
             "on its height: both cancel.\n  The last column is the signal-to-noise ratio for "
             "a 0.51 per cent budget.",
             ("highest", "lowest", "predicted ratio<br>local source",
              "reduction", "distant<br>source", "S/N"))):
        vieux = re.search(
            r"<table>\n  <caption>Table(?:au)? 1 [^<]*(?:<[^>]+>[^<]*)*?</caption>\n"
            r"  <thead>.*?</thead>\n  <tbody>.*?</tbody>\n</table>",
            src[depuis:], re.S)
        if not vieux:
            sys.exit("tableau 1 %s introuvable" % langue)
        neuf = ("<table>\n  <caption>%s</caption>\n"
                "  <thead><tr>%s</tr></thead>\n  <tbody>\n%s\n  </tbody>\n</table>"
                % (cap,
                   "".join('<th class="n">%s</th>' % e for e in entetes),
                   lignes_tableau(virgule)))
        debut, fin = depuis + vieux.start(), depuis + vieux.end()
        src = src[:debut] + neuf + src[fin:]
        depuis = debut + len(neuf)

    # ══ 6. Les légendes de la figure 2 ══════════════════════════════════════
    src = remplacer(
        src,
        "Les points marquent les six hauteurs recommandées pour la campagne. "
        "À 20&#176;, les deux modèles diffèrent de <b>66 %</b> du "
        "diamètre ; à 15&#176;, de 74 %.",
        "Les points marquent les six hauteurs recommandées pour la campagne. La "
        "courbe est tracée en rapportant tout au zénith, mais ce n'est qu'un "
        "choix d'échelle&#160;: la grandeur mesurable est le <b>rapport entre deux "
        "points de la courbe</b>, et il ne dépend pas de ce à quoi on la "
        "normalise. De 70&#176; à 20&#176;, ce rapport vaut <b>0,364</b> pour la "
        "source locale et <b>1,000</b> pour la source lointaine.",
        "figure 2 FR")
    src = remplacer(
        src,
        "Points mark the six altitudes recommended for the campaign. At 20&#176; the two "
        "models differ by <b>66 per cent</b> of the diameter; at 15&#176;, by 74 per cent.",
        "Points mark the six altitudes recommended for the campaign. The curve is drawn "
        "relative to the zenith, but that is only a choice of scale: the measurable quantity "
        "is the <b>ratio between two points on the curve</b>, and it does not depend on what "
        "the curve is normalised to. From 70&#176; to 20&#176; that ratio is <b>0.364</b> for "
        "the local source and <b>1.000</b> for the distant one.",
        "figure 2 EN")

    # ══ 7. L'encadré signal sur bruit ═══════════════════════════════════════
    src = remplacer(
        src,
        "  <p>Signal pr&#233;dit par le mod&#232;le &#224; source locale &#224; 20&#176; de "
        "hauteur : <strong>66 %</strong>.\n  Incertitude totale : "
        "<strong>0,51 %</strong>. <strong>Rapport &#8776; 130.</strong>",
        "  <p>Signal pr&#233;dit par la famille locale entre 70&#176; et 20&#176; de "
        "hauteur : <strong>63,6 %%</strong>.\n  Incertitude totale : "
        "<strong>0,51 %%</strong>. <strong>Rapport &#8776; %d.</strong> Un &#233;cart de "
        "hauteur bien\n  moindre suffirait d&#233;j&#224;&#160;: depuis 70&#176;, descendre "
        "de <strong>2,3&#176;</strong> place le signal &#224; 3 &#963;."
        % snr,
        "encadré S/B FR")
    src = remplacer(
        src,
        "  <p>Signal predicted by the local-source model at 20&#176; elevation: "
        "<strong>66 per cent</strong>.\n  Total uncertainty: <strong>0.51 per cent</strong>. "
        "<strong>Ratio &#8776; 130.</strong>",
        "  <p>Signal predicted by the local family between 70&#176; and 20&#176; elevation: "
        "<strong>63.6 per cent</strong>.\n  Total uncertainty: "
        "<strong>0.51 per cent</strong>. <strong>Ratio &#8776; %d.</strong> A far smaller "
        "altitude\n  swing would already do: from 70&#176;, descending "
        "<strong>2.3&#176;</strong> puts the signal at 3 &#963;."
        % snr,
        "encadré S/B EN")

    # ══ 8. La réfutation sur les vidéos ═════════════════════════════════════
    src = remplacer(
        src,
        "le signal pr&#233;dit &#224; 20&#176; vaut 66&#160;% pour un budget de 0,51.",
        "le signal pr&#233;dit entre 70&#176; et 20&#176; vaut 63,6&#160;% pour un budget "
        "de 0,51.", "réfutation FR")
    src = remplacer(
        src,
        "the predicted signal at 20&#176; is 66 per cent against a budget of 0.51.",
        "the predicted signal between 70&#176; and 20&#176; is 63.6 per cent against a "
        "budget of 0.51.", "réfutation EN")

    # ══ 9. Le numéro de version ═════════════════════════════════════════════
    if src.count("<b>1.5</b>") != 2:
        sys.exit("numéro de version : %d occurrence(s), attendu 2"
                 % src.count("<b>1.5</b>"))
    src = src.replace("<b>1.5</b>", "<b>1.6</b>")
    src = src.replace("Protocole ouvert, version 1.5.", "Protocole ouvert, version 1.6.")
    src = src.replace("Open protocol, version 1.5.", "Open protocol, version 1.6.")

    for reste in ("66 %", "66 per cent"):
        i = src.find(reste)
        if i >= 0:
            sys.exit("il reste une mention de « %s » : %r"
                     % (reste, src[max(0, i - 120):i + 60]))

    open(CIBLE, "w", encoding="utf-8").write(src)
    print("Version 1.6 écrite. S/B = %d. Toutes les valeurs contrôlées." % snr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
