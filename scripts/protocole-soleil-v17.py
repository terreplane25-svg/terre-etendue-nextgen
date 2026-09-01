#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Protocole du diamètre solaire — passage de la version 1.6 à la version 1.7.

Ce que 1.7 change, et pourquoi.

La 1.6 avait déjà cessé de prétendre mesurer la taille du Soleil. Elle gardait
pourtant une pièce qui présuppose la réponse : la **zone morte**, qui déclarait
« défaut de protocole » tout rapport mesuré entre 0,40 et 0,95, au motif
qu'« aucun des deux modèles ne prédit cette plage ».

Cette règle n'est légitime que si l'on tient d'avance pour acquis que le Soleil
est un disque rigide, de diamètre fixe, porté à hauteur constante au-dessus
d'un plan — car c'est cette hypothèse-là, et elle seule, qui impose la loi
sin α et donc la valeur 0,364. On ne connaît pas la nature du Soleil. Un rapport
de 0,50, de 0,80 ou de 0,91 n'est pas une faute de manipulation : c'est une
mesure, qui dit que la distance a changé d'une certaine quantité et pas d'une
autre. La déclarer impossible revient à jeter le résultat qui ne ressemble à
aucun des deux modèles qu'on avait en tête.

La 1.7 remplace donc la zone morte par un critère qui ne suppose rien du
Soleil : **le contrôle par symétrie**. Si la variation du diamètre est
géométrique, elle ne dépend que de la hauteur ; une prise à 40° le matin et une
prise à 40° l'après-midi doivent donner le même diamètre. Un artefact — dérive
thermique, mise au point, transparence, saturation — n'a aucune raison d'être
symétrique par rapport au midi solaire. C'est cela, et non la valeur du rapport,
qui sépare une mesure d'un raté.

Et l'objet du protocole est ramené à sa seule question tenable : **le Soleil
est-il proche ou lointain ?** Autrement dit : sa distance à l'œil change-t-elle
au cours d'une journée, et de combien. La loi sin α n'est plus la définition de
« proche » ; elle n'est qu'une hypothèse particulière à l'intérieur de la
famille des sources proches, celle où la hauteur reste constante. Si le profil
mesuré varie sans suivre sin α, « proche » tient toujours — c'est la hauteur
constante qui tombe.

La conversion est directe et sans modèle : pour un corps rigide, θ ∝ 1/d, donc
un rapport r entre deux hauteurs signifie que la distance a été multipliée
par 1/r.

Ce script n'est PAS idempotent. Chaque ancre est vérifiée avant écriture.
"""
import os
import re
import sys
from math import radians, sin

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIBLE = os.path.join(RACINE, "content", "protocoles", "soleil-bilingue.html")

BUDGET = 0.51
# Rapports de lecture : r mesuré → variation de distance impliquée, 1/r − 1.
LECTURE = [1.000, 0.990, 0.950, 0.910, 0.800, 0.600, 0.500]


def controle_numerique():
    for r in LECTURE:
        assert 0 < r <= 1
    attendu = {1.000: 0.0, 0.990: 1.0, 0.950: 5.3, 0.910: 9.9,
               0.800: 25.0, 0.600: 66.7, 0.500: 100.0}
    for r, val in attendu.items():
        assert abs(100 * (1 / r - 1) - val) < 0.05, (r, val)
    sinus = sin(radians(20)) / sin(radians(70))
    assert abs(sinus - 0.3640) < 5e-5, sinus
    assert abs(100 * (1 / sinus - 1) - 174.7) < 0.2, sinus
    assert abs(3 * BUDGET - 1.53) < 1e-9
    return sinus


def remplacer(src, vieux, neuf, etiquette):
    if src.count(vieux) != 1:
        sys.exit("ancre « %s » vue %d fois — attendu 1. Déjà en 1.7 ?"
                 % (etiquette, src.count(vieux)))
    return src.replace(vieux, neuf)


def table_lecture(virgule, sinus):
    sep = "," if virgule else "."
    pct = "&#160;%" if virgule else " per cent"

    def nb(x, n):
        return ("%.*f" % (n, x)).replace(".", sep)

    lignes = []
    for r in LECTURE:
        lignes.append('    <tr><td class="n">%s</td><td class="n">+%s%s</td></tr>'
                      % (nb(r, 3), nb(100 * (1 / r - 1), 1), pct))
    lignes.append('    <tr class="hi"><td class="n"><strong>%s</strong></td>'
                  '<td class="n"><strong>+%s%s</strong></td></tr>'
                  % (nb(sinus, 3), nb(100 * (1 / sinus - 1), 1), pct))
    return "\n".join(lignes)


def main():
    sinus = controle_numerique()
    src = open(CIBLE, encoding="utf-8").read()

    # ══ 1. Les critères, reformulés sur la distance et non sur les modèles ══
    criteres_fr = (
        "<h3>Ce que la mesure &#233;tablit</h3>\n"
        "<p>Le r&#233;sultat de la campagne n'est pas un mod&#232;le mais une "
        "grandeur&#160;: le <strong>profil de\ndistance</strong> du Soleil au cours "
        "de la journ&#233;e. Pour un corps rigide, le diam&#232;tre angulaire vaut "
        "D/d,\ndonc un rapport <code>r = &#952;(bas)/&#952;(haut)</code> signifie que "
        "la distance a &#233;t&#233; multipli&#233;e par\n<code>1/r</code>. Aucune "
        "hypoth&#232;se sur la nature de l'astre n'entre dans cette conversion.</p>\n"
        "<div class=\"two\">\n"
        "  <div class=\"vc g\">\n"
        "    <p class=\"h\">r = 1,000 &#177; 0,010</p>\n"
        "    <p class=\"v\">Le Soleil est lointain</p>\n"
        "    <p>Sa distance &#224; l'&#339;il ne change pas mesurablement pendant "
        "qu'il traverse le ciel d'un\n    horizon &#224; l'autre. Aucune source "
        "port&#233;e &#224; hauteur finie au-dessus d'un plan ne reproduit cela&#160;: "
        "en\n    s'&#233;loignant vers l'horizon elle devrait reculer.</p>\n"
        "  </div>\n"
        "  <div class=\"vc p\">\n"
        "    <p class=\"h\">r &lt; 0,99</p>\n"
        "    <p class=\"v\">Le Soleil est proche</p>\n"
        "    <p>Sa distance &#224; l'&#339;il augmente quand il descend, de "
        "<code>1/r &#8722; 1</code>. C'est incompatible\n    avec une source "
        "&#224; 149,6 millions de kilom&#232;tres, dont la distance ne peut varier que "
        "de\n    2&#215;10<sup>&#8722;2</sup> % en un jour. La valeur du rapport dit "
        "<em>de combien</em>&#160;; elle ne dit pas\n    par quelle "
        "g&#233;om&#233;trie.</p>\n"
        "  </div>\n"
        "</div>\n"
        "<table>\n"
        "  <caption>Tableau 6 &#8212; Lecture d'un rapport mesur&#233;. La conversion "
        "ne suppose que la rigidit&#233; de\n  l'astre. <strong>Aucune valeur n'est "
        "d&#233;clar&#233;e impossible</strong>&#160;: la derni&#232;re ligne, "
        "surlign&#233;e, est\n  simplement celle qu'imposerait une hauteur constante "
        "au-dessus d'un plan entre 70&#176; et 20&#176;.</caption>\n"
        "  <thead><tr><th class=\"n\">rapport mesur&#233; r</th>"
        "<th class=\"n\">la distance augmente de</th></tr></thead>\n"
        "  <tbody>\n@@TABLE@@\n  </tbody>\n</table>\n"
        "<div class=\"box warn\">\n"
        "  <span class=\"lab\">Contr&#244;le par sym&#233;trie &#8212; le seul "
        "crit&#232;re de rejet</span>\n"
        "  <p>Une variation g&#233;om&#233;trique ne d&#233;pend que de la "
        "<strong>hauteur</strong>. Une prise &#224; 40&#176; le matin et\n  une prise "
        "&#224; 40&#176; l'apr&#232;s-midi doivent donc donner le m&#234;me "
        "diam&#232;tre. Un artefact &#8212; d&#233;rive thermique\n  du fut, "
        "d&#233;placement de la mise au point, transparence, saturation du disque "
        "&#8212; n'a aucune raison\n  d'&#234;tre sym&#233;trique par rapport au midi "
        "solaire.</p>\n"
        "  <p><strong>Crit&#232;re&#160;:</strong> pour chaque couple de hauteurs "
        "appari&#233;es, l'&#233;cart matin/apr&#232;s-midi doit\n  rester sous "
        "<strong>1,53 %</strong> (3&#963;). Au-del&#224;, la s&#233;rie est "
        "rejet&#233;e et refaite &#8212; quelle que soit la\n  valeur du rapport. "
        "Causes &#224; &#233;liminer&#160;: seuil de luminosit&#233; fixe au lieu du "
        "crit&#232;re des 50 %,\n  diam&#232;tre vertical mesur&#233; au lieu de "
        "l'horizontal, focale modifi&#233;e en cours de s&#233;rie, recadrage,\n  "
        "correction automatique de distorsion laiss&#233;e active.</p>\n"
        "</div>").replace("@@TABLE@@", table_lecture(True, sinus))

    vieux_fr = re.search(
        r"<h3>Crit&#232;res fix&#233;s a priori</h3>\n<div class=\"two\">.*?"
        r"distorsion laiss&#233;e active\.</p>\n</div>", src, re.S)
    if not vieux_fr:
        sys.exit("bloc des critères FR introuvable")
    src = src[:vieux_fr.start()] + criteres_fr + src[vieux_fr.end():]

    criteres_en = (
        "<h3>What the measurement establishes</h3>\n"
        "<p>The campaign's output is not a model but a quantity: the Sun's "
        "<strong>distance profile</strong>\nover the day. For a rigid body the angular "
        "diameter is D/d, so a ratio\n<code>r = &#952;(low)/&#952;(high)</code> means "
        "the distance has been multiplied by <code>1/r</code>. No\nassumption about "
        "the body's nature enters that conversion.</p>\n"
        "<div class=\"two\">\n"
        "  <div class=\"vc g\">\n"
        "    <p class=\"h\">r = 1.000 &#177; 0.010</p>\n"
        "    <p class=\"v\">The Sun is distant</p>\n"
        "    <p>Its distance to the eye does not measurably change while it crosses "
        "the sky from one\n    horizon to the other. No source held at a finite height "
        "above a plane reproduces that: as it\n    moves towards the horizon it would "
        "have to recede.</p>\n"
        "  </div>\n"
        "  <div class=\"vc p\">\n"
        "    <p class=\"h\">r &lt; 0.99</p>\n"
        "    <p class=\"v\">The Sun is near</p>\n"
        "    <p>Its distance to the eye grows as it descends, by "
        "<code>1/r &#8722; 1</code>. That is incompatible\n    with a source at 149.6 "
        "million kilometres, whose distance can vary by no more than\n    "
        "2&#215;10<sup>&#8722;2</sup> per cent in a day. The value of the ratio says "
        "<em>by how much</em>; it does not\n    say through what geometry.</p>\n"
        "  </div>\n"
        "</div>\n"
        "<table>\n"
        "  <caption>Table 6 &#8212; Reading a measured ratio. The conversion assumes "
        "only that the body is rigid.\n  <strong>No value is declared "
        "impossible</strong>: the highlighted last row is simply the one a constant\n"
        "  height above a plane would require between 70&#176; and 20&#176;.</caption>\n"
        "  <thead><tr><th class=\"n\">measured ratio r</th>"
        "<th class=\"n\">distance increases by</th></tr></thead>\n"
        "  <tbody>\n@@TABLE@@\n  </tbody>\n</table>\n"
        "<div class=\"box warn\">\n"
        "  <span class=\"lab\">Symmetry control &#8212; the only rejection "
        "criterion</span>\n"
        "  <p>A geometric variation depends on <strong>altitude</strong> alone. A "
        "frame taken at 40&#176; in the\n  morning and one at 40&#176; in the afternoon "
        "must therefore give the same diameter. An artefact &#8212;\n  thermal drift of "
        "the barrel, focus shift, transparency, disk saturation &#8212; has no reason to "
        "be\n  symmetric about solar noon.</p>\n"
        "  <p><strong>Criterion:</strong> for each paired altitude, the "
        "morning/afternoon discrepancy must stay\n  below <strong>1.53 per "
        "cent</strong> (3&#963;). Beyond that the series is rejected and repeated "
        "&#8212; whatever\n  the value of the ratio. Causes to rule out: fixed "
        "brightness threshold instead of the 50 per cent\n  criterion, vertical "
        "diameter measured instead of horizontal, focal length changed mid-series,\n  "
        "cropping, automatic distortion correction left enabled.</p>\n"
        "</div>").replace("@@TABLE@@", table_lecture(False, sinus))

    vieux_en = re.search(
        r"<h3>Criteria fixed a priori</h3>\n<div class=\"two\">.*?"
        r"correction left\n  enabled\.</p>\n</div>", src, re.S)
    if not vieux_en:
        sys.exit("bloc des critères EN introuvable")
    src = src[:vieux_en.start()] + criteres_en + src[vieux_en.end():]

    # ══ 2. Le chapeau et le titre disent la question, pas les modèles ═══════
    src = remplacer(
        src,
        "<h1>Le diam&#232;tre angulaire du Soleil au cours d'une journ&#233;e</h1>",
        "<h1>Le Soleil est-il proche ou lointain&#160;?</h1>\n  <p class=\"sub\">"
        "Mesure de son diam&#232;tre angulaire au cours d'une journ&#233;e</p>",
        "titre FR")
    src = remplacer(
        src,
        "<h1>The Sun's angular diameter over the course of a day</h1>",
        "<h1>Is the Sun near or distant?</h1>\n  <p class=\"sub\">Measuring its "
        "angular diameter over the course of a day</p>",
        "titre EN")

    # ══ 3. Le résumé : sin α cesse d'être la définition de « proche » ═══════
    src = remplacer(
        src,
        "diam&#232;tres entre deux hauteurs de la\n  m&#234;me journ&#233;e vaut "
        "<code>sin &#945;&#8322; / sin &#945;&#8321;</code> &#8212; grandeur o&#249; le "
        "diam&#232;tre D et la\n  hauteur H se sont &#233;limin&#233;s.",
        "diam&#232;tres entre deux hauteurs de la\n  m&#234;me journ&#233;e vaut "
        "<code>sin &#945;&#8322; / sin &#945;&#8321;</code> &#8212; grandeur o&#249; le "
        "diam&#232;tre D et la\n  hauteur H se sont &#233;limin&#233;s. Cette loi vaut "
        "pour <em>une</em> hypoth&#232;se de source proche, celle o&#249;\n  la hauteur "
        "reste constante&#160;; une variation qui ne la suivrait pas resterait une "
        "variation, et\n  &#233;carterait tout autant la source lointaine.",
        "résumé sin α FR")
    src = remplacer(
        src,
        "two altitudes of the same day is\n  <code>sin &#945;&#8322; / "
        "sin &#945;&#8321;</code> &#8212; a quantity in which the diameter D and the "
        "height H\n  have cancelled.",
        "two altitudes of the same day is\n  <code>sin &#945;&#8322; / "
        "sin &#945;&#8321;</code> &#8212; a quantity in which the diameter D and the "
        "height H\n  have cancelled. That law holds for <em>one</em> near-source "
        "hypothesis, the one where the height\n  stays constant; a variation that did "
        "not follow it would still be a variation, and would rule\n  out the distant "
        "source just as firmly.",
        "résumé sin α EN")

    # ══ 4. L'encadré de bornage gagne la limite d'une seule station ═════════
    src = remplacer(
        src,
        "d&#233;duit d'une seconde station, ce qui est un autre protocole.</p>",
        "d&#233;duit d'une seconde station, ce qui est un autre protocole. "
        "<strong>Une station donne le\n  profil de distance, jamais la distance "
        "elle-m&#234;me</strong>&#160;: il y faut une base.</p>",
        "bornage FR")
    src = remplacer(
        src,
        "follows from a second\n  station, which is a different protocol.</p>",
        "follows from a second\n  station, which is a different protocol. "
        "<strong>One station yields the distance profile, never the\n  distance "
        "itself</strong>: that requires a baseline.</p>",
        "bornage EN")

    # ══ 5. Version ══════════════════════════════════════════════════════════
    if src.count("<b>1.6</b>") != 2:
        sys.exit("version : %d occurrence(s), attendu 2" % src.count("<b>1.6</b>"))
    src = src.replace("<b>1.6</b>", "<b>1.7</b>")
    src = src.replace("Protocole ouvert, version 1.6.", "Protocole ouvert, version 1.7.")
    src = src.replace("Open protocol, version 1.6.", "Open protocol, version 1.7.")

    for reste in ("Zone morte", "Dead zone", "a priori"):
        if reste in src:
            i = src.find(reste)
            sys.exit("il reste « %s » : %r" % (reste, src[max(0, i - 100):i + 60]))

    open(CIBLE, "w", encoding="utf-8").write(src)
    print("Version 1.7 écrite. Zone morte remplacée par le contrôle par symétrie.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
