#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Protocole solaire : version 1.4 → 1.5, dans les deux langues.

ATTENTION — ce script a été exécuté une fois, le 31 août 2026, sur la version 1.4.
Il n'est pas idempotent : le relancer sur la 1.5 échouera au contrôle des motifs,
et c'est voulu. Il est conservé comme trace de ce qui a été changé et pourquoi.
La variante à deux stations et la renumérotation des tableaux 4 et 5 ont été
appliquées séparément, après coup.

Deux corrections et quatre ajouts, validés après revue.

Les corrections suppriment des contradictions internes : le document se
corrigeait à un endroit et gardait l'ancienne valeur ailleurs. Aucune ne change
une conclusion.

  1. Le critère « retrouver 14 % » du contrôle lunaire. La section 04 démontre
     elle-même qu'il est fautif — 356 500 et 406 700 km sont les extrêmes
     pluriannuels, un mois défavorable donne 9,5 % — puis le résumé et la
     procédure l'imposaient quand même. Le critère devient la loi : pente de θ
     contre 1/d égale à 1,000.

  2. Les « 1,7 % » du contrôle B, corrigés en 1,42 % à Paris dans le tableau 2
     et maintenus dans trois autres phrases. Ils renvoient au tableau.

Une troisième correction avait été proposée, sur l'aplatissement annoncé à
17 % — elle est RETIRÉE. Mon calcul de revue séparait les deux limbes de 0,27°
au lieu de 0,526°, et sous-estimait donc l'effet d'un facteur deux. Recalculé
correctement par la formule de Bennett, l'aplatissement vaut 19,0 % quand le
limbe inférieur touche l'horizon, 16,8 % quand le centre est à 0,5°, 13,0 % à 1°.
La valeur du document était du bon ordre. Ce qui reste utile est de nommer le
modèle de réfraction et de dire à quelle configuration le maximum se rapporte —
c'est une précision, pas une correction.

Les quatre ajouts prennent en compte des phénomènes qui n'étaient pas traités :

  A. La hauteur employée dans sin α est l'apparente, pas la vraie d'éphéméride.
     L'écart induit vaut 0,40 % à 15°, soit les quatre cinquièmes du budget.

  B. Rien ne vérifiait que la focale n'avait pas bougé. La dérive du Soleil
     lui-même — 4,9 pixels par seconde à 400 mm — donne l'échelle du moment
     sans connaître la focale.

  C. La sortie « projection » reste ouverte tant qu'on n'oppose pas deux
     stations simultanées à des hauteurs différentes.

  D. Deux objections nouvelles : les vidéos montrant un disque qui change de
     taille, et la diffusion près de l'horizon.

Le script vérifie chaque motif avant d'écrire quoi que ce soit : si un seul
n'apparaît pas exactement le nombre de fois attendu, rien n'est écrit.
"""
import math
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIBLE = os.path.join(RACINE, "content", "protocoles", "soleil-bilingue.html")
RAYON = 0.263  # rayon angulaire du Soleil, en degrés


def bennett(h):
    """Réfraction en minutes d'arc pour une hauteur apparente h en degrés."""
    return 1.0 / math.tan(math.radians(h + 7.31 / (h + 4.4)))


def controle_numerique():
    """Chaque valeur inscrite ci-dessous, recalculée avant écriture."""
    apl = 100 * (bennett(0.0) - bennett(2 * RAYON)) / 31.5
    if abs(apl - 19.0) > 0.5:
        sys.exit("Aplatissement limbe bas à l'horizon : %.1f %%, attendu 19,0" % apl)
    for h, attendu in [(15.0, 0.40), (20.0, 0.22)]:
        r = bennett(h) / 60.0
        ecart = 100 * (math.sin(math.radians(h)) / math.sin(math.radians(h - r)) - 1)
        if abs(ecart - attendu) > 0.03:
            sys.exit("Écart sin α à %.0f° : %.2f %%, attendu %.2f" % (h, ecart, attendu))
    sec_px = math.degrees(24.0 / 4000 / 1000 / 0.400) * 3600
    if abs(sec_px - 3.094) > 0.005:
        sys.exit("Échelle : %.3f″/px, attendu 3,094" % sec_px)
    if abs(15.041 / sec_px - 4.86) > 0.05:
        sys.exit("Dérive : %.2f px/s, attendu 4,86" % (15.041 / sec_px))
    if abs(math.sin(math.radians(20)) / math.sin(math.radians(60)) - 0.395) > 0.002:
        sys.exit("Rapport deux stations incorrect")
    print("Contrôle numérique : aplatissement, réfraction, échelle, dérive et rapport.")


R = []   # (motif, remplacement, occurrences attendues)

# ══════════ CORRECTION 1 et 2 — français ═══════════════════════════════════
R.append((
    "Deux contr&#244;les positifs sur la Lune\n"
    "  valident la cha&#238;ne de mesure &#224; 14 % puis &#224; 1,7 %, avant toute conclusion sur le Soleil.",
    "Deux contr&#244;les positifs sur la Lune qualifient la cha&#238;ne de mesure avant toute\n"
    "  conclusion sur le Soleil. Aucun des deux ne porte sur une valeur pr&#233;-annonc&#233;e&#160;: "
    "le premier v&#233;rifie une <em>loi</em>, le second un signal dont la valeur d&#233;pend de la "
    "latitude de l'observateur.", 1))

R.append((
    "cuter les contr&#244;les A et B de la section 04. Ne pas\n"
    "  passer au Soleil tant que les 14 % et les 1,7 % ne sont pas retrouv&#233;s.",
    "cuter les contr&#244;les A et B de la section 04. Ne pas\n"
    "  passer au Soleil tant que le contr&#244;le A n'a pas donn&#233; une pente de 1,000 pour "
    "&#952; contre 1/d, et que le contr&#244;le B n'a pas retrouv&#233; le signal pr&#233;dit "
    "<em>&#224; la latitude de la station</em> (tableau&#160;2). Aucune valeur n'est &#224; "
    "retrouver&#160;: un mois lunaire d&#233;favorable donne 9,5&#160;% l&#224; o&#249; un mois "
    "favorable en donne 12,0, et les deux sont corrects.", 1))

R.append((
    "gonfler la Lune basse dans les m&#234;mes proportions, alors que la mesure la trouve\n"
    "  <em>plus petite</em> de 1,7 %.",
    "gonfler la Lune basse dans les m&#234;mes proportions, alors que la mesure la trouve\n"
    "  <em>plus petite</em> &#8212; de 1,42&#160;% &#224; la latitude de Paris, et de 1,20 &#224; "
    "1,52&#160;% selon la latitude (tableau&#160;2).", 1))

# ══════════ CORRECTION 1 et 2 — anglais ════════════════════════════════════
R.append((
    "Two positive controls on the Moon validate the\n"
    "  measurement chain at 14 per cent and then at 1.7 per cent, before any conclusion about the\n"
    "  Sun.",
    "Two positive controls on the Moon qualify the measurement chain before any conclusion\n"
    "  about the Sun. Neither turns on a pre-announced figure: the first verifies a <em>law</em>,\n"
    "  the second a signal whose value depends on the observer's latitude.", 1))

R.append((
    "Run controls A and B of section 04. Do not proceed to the Sun\n"
    "  until the 14 per cent and the 1.7 per cent have been recovered.",
    "Run controls A and B of section 04. Do not proceed to the Sun\n"
    "  until control A has yielded a slope of 1.000 for &#952; against 1/d, and control B has\n"
    "  recovered the predicted signal <em>at the station's latitude</em> (table&#160;2). No figure\n"
    "  is to be matched: an unfavourable lunar month gives 9.5 per cent where a favourable one\n"
    "  gives 12.0, and both are correct.", 1))

R.append((
    "finds it <em>smaller</em> by 1.7 per cent.",
    "finds it <em>smaller</em> &#8212; by 1.42 per cent at the latitude of Paris, and by 1.20 to\n"
    "  1.52 per cent depending on latitude (table&#160;2).", 1))

# ══════════ PRÉCISION sur l'aplatissement (pas une correction) ═════════════
R.append((
    "pr&#232;s de\nl'horizon, jusqu'&#224; 17 % &#224; hauteur nulle. Cet effet est r&#233;el, "
    "bien document&#233;, et il\ncontaminerait toute mesure verticale.",
    "pr&#232;s de\nl'horizon. Calcul&#233; par la formule de Bennett (1982), l'aplatissement "
    "atteint 19&#160;% au moment o&#249; le limbe inf&#233;rieur touche l'horizon, 17&#160;% "
    "lorsque le centre du disque est &#224; un demi-degr&#233;, et 13&#160;% &#224; un "
    "degr&#233;&#160;: ce qui aplatit le disque n'est pas la r&#233;fraction elle-m&#234;me mais "
    "son <em>gradient</em>, maximal juste au-dessus de l'horizon. Un autre mod&#232;le de "
    "r&#233;fraction donnerait des valeurs voisines&#160;; c'est pourquoi celui qu'on emploie est "
    "nomm&#233;. Cet effet est r&#233;el, bien document&#233;, et il\ncontaminerait toute mesure "
    "verticale.", 1))

R.append((
    "near the horizon, by up to 17 per cent at zero\nelevation. The effect is real, well "
    "documented, and would contaminate any vertical\nmeasurement.",
    "near the horizon. Computed with Bennett's formula (1982), the flattening reaches 19 per cent "
    "at the moment the lower limb touches the horizon, 17 per cent when the disk centre is at half "
    "a degree, and 13 per cent at one degree: what flattens the disk is not refraction itself but "
    "its <em>gradient</em>, greatest just above the horizon. Another refraction model would give "
    "neighbouring values; this is why the one used is named. The effect is real, well documented, "
    "and would contaminate any vertical\nmeasurement.", 1))

# ══════════ AJOUT A — hauteur apparente, français ══════════════════════════
R.append((
    "<li><b>Relever la hauteur</b>&#192; chaque s&#233;rie, noter l'heure UTC &#224; la seconde. "
    "La hauteur\n  vraie du Soleil s'en d&#233;duit par &#233;ph&#233;m&#233;ride, sans instrument "
    "suppl&#233;mentaire.</li>",
    "<li><b>Relever la hauteur</b>&#192; chaque s&#233;rie, noter l'heure UTC &#224; la seconde. "
    "La hauteur\n  du Soleil s'en d&#233;duit par &#233;ph&#233;m&#233;ride, sans instrument "
    "suppl&#233;mentaire. <strong>Employer la hauteur apparente, r&#233;fract&#233;e</strong>, et "
    "non la hauteur vraie&#160;: l'observable est la direction dans laquelle le disque est vu. "
    "L'&#233;cart n'est pas n&#233;gligeable devant le budget d'erreur &#8212; il vaut 0,40&#160;% "
    "sur sin&#160;&#945; &#224; 15&#176; de hauteur, 0,22&#160;% &#224; 20&#176;, 0,09&#160;% "
    "&#224; 30&#176; &#8212; et les deux mod&#232;les doivent &#234;tre compar&#233;s sur la "
    "<em>m&#234;me</em> hauteur, faute de quoi on compare deux grandeurs "
    "diff&#233;rentes.</li>\n"
    "  <li><b>Relever l'&#233;chelle par la d&#233;rive</b>Appareil fixe, sans suivi&#160;: le "
    "disque d&#233;file &#224; 15,041&#8243;/s &#215; cos&#160;&#948;, soit 4,9 pixels par seconde "
    "&#224; 400&#160;mm sur plein format. Une rafale de dix secondes &#224; chaque s&#233;rie donne "
    "l'&#233;chelle angulaire du moment <strong>sans conna&#238;tre la focale</strong>. C'est le "
    "seul contr&#244;le qui d&#233;tecte une bague qui a gliss&#233; ou un objectif qui respire "
    "&#224; la mise au point.</li>", 1))

# ══════════ AJOUT A et B — anglais ═════════════════════════════════════════
R.append((
    "<li><b>Record the altitude</b>For each series, note UTC time to the second. The Sun's true\n"
    "  altitude then follows from ephemeris, with no additional instrument.</li>",
    "<li><b>Record the altitude</b>For each series, note UTC time to the second. The Sun's\n"
    "  altitude then follows from ephemeris, with no additional instrument. <strong>Use the "
    "apparent, refracted altitude</strong>, not the true one: the observable is the direction in "
    "which the disk is seen. The difference is not negligible against the error budget &#8212; it "
    "amounts to 0.40 per cent on sin&#160;&#945; at 15&#176;, 0.22 per cent at 20&#176;, 0.09 per "
    "cent at 30&#176; &#8212; and both models must be compared at the <em>same</em> altitude, "
    "failing which one compares two different quantities.</li>\n"
    "  <li><b>Record the plate scale by drift</b>Camera fixed, no tracking: the disk drifts at "
    "15.041&#8243;/s &#215; cos&#160;&#948;, that is 4.9 pixels per second at 400&#160;mm on full "
    "frame. A ten-second burst at each series gives the angular scale of the moment <strong>without "
    "knowing the focal length</strong>. It is the only check that catches a ring that has slipped "
    "or a lens that breathes on focus.</li>", 1))

# ══════════ AJOUT B — le budget d'erreur ═══════════════════════════════════
R.append((
    "<tr><td>Stabilit&#233; de la focale</td><td class=\"n\">0,08 %</td><td>bague "
    "immobilis&#233;e</td></tr>",
    "<tr><td>Stabilit&#233; de la focale</td><td class=\"n\">0,08 %</td><td>mesur&#233;e par la "
    "d&#233;rive, non suppos&#233;e</td></tr>", 1))

# ══════════ AJOUT D — objections, français ═════════════════════════════════
R.append((
    "<li><strong>&#171; L'illusion lunaire prouve que l'&#339;il se trompe. &#187;</strong>",
    "<li><strong>&#171; Des vid&#233;os montrent le Soleil changer de taille, filtre compris. "
    "&#187;</strong> C'est la seule observation en circulation qui contredirait la source "
    "lointaine, et il faut la nommer plut&#244;t que l'ignorer. Ces enregistrements n'indiquent "
    "ni la focale employ&#233;e, ni l'exposition, ni si le disque &#233;tait satur&#233; &#8212; "
    "et un disque satur&#233; s'&#233;largit. Ce sont pr&#233;cis&#233;ment les trois grandeurs que "
    "ce protocole verrouille. <strong>Si l'effet est r&#233;el, ce protocole le trouve, et "
    "massivement&#160;:</strong> le signal pr&#233;dit &#224; 20&#176; vaut 66&#160;% pour un "
    "budget de 0,51.</li>\n"
    "  <li><strong>&#171; La diffusion pr&#232;s de l'horizon gonfle le disque. &#187;</strong> "
    "L'aur&#233;ole de diffusion peut &#233;largir le limbe et fausser le crit&#232;re des "
    "50&#160;% si le fond de ciel cesse d'&#234;tre s&#233;parable du disque. C'est une objection "
    "juste, et elle se traite par un crit&#232;re de rejet&#160;: &#233;carter toute s&#233;rie "
    "dont le fond de ciel, mesur&#233; &#224; un rayon du bord, d&#233;passe le cinqui&#232;me du "
    "plateau. Une s&#233;rie rejet&#233;e est consign&#233;e comme telle, jamais "
    "supprim&#233;e.</li>\n"
    "  <li><strong>&#171; L'illusion lunaire prouve que l'&#339;il se trompe. &#187;</strong>", 1))

# ══════════ AJOUT D — objections, anglais ══════════════════════════════════
R.append((
    "<li><strong>&#8220;The Moon illusion proves the eye is fooled.&#8221;</strong>",
    "<li><strong>&#8220;Videos show the Sun changing size, solar filter included.&#8221;</strong> "
    "This is the only observation in circulation that would contradict the distant source, and it "
    "must be named rather than ignored. Those recordings state neither the focal length used, nor "
    "the exposure, nor whether the disk was saturated &#8212; and a saturated disk grows. These are "
    "precisely the three quantities this protocol locks down. <strong>If the effect is real, this "
    "protocol finds it, and massively:</strong> the predicted signal at 20&#176; is 66 per cent "
    "against a budget of 0.51.</li>\n"
    "  <li><strong>&#8220;Scattering near the horizon inflates the disk.&#8221;</strong> The "
    "scattering aureole can broaden the limb and corrupt the 50 per cent criterion if the sky "
    "background ceases to be separable from the disk. The objection is sound, and it is handled by "
    "a rejection criterion: discard any series whose sky background, measured one radius from the "
    "edge, exceeds one fifth of the plateau. A rejected series is recorded as such, never "
    "deleted.</li>\n"
    "  <li><strong>&#8220;The Moon illusion proves the eye is fooled.&#8221;</strong>", 1))

# ══════════ Numéro de version ══════════════════════════════════════════════
R.append(("<span>Version<b>1.4</b></span>", "<span>Version<b>1.5</b></span>", 2))
R.append(("version 1.4.", "version 1.5.", 2))


def main():
    controle_numerique()
    with open(CIBLE, encoding="utf-8") as f:
        s = f.read()
    for motif, _, attendu in R:
        n = s.count(motif)
        if n != attendu:
            sys.exit("« %s… » : %d occurrence(s), %d attendue(s). Rien n'est écrit."
                     % (motif[:60].replace("\n", " "), n, attendu))
    for motif, remplacement, _ in R:
        s = s.replace(motif, remplacement)
    with open(CIBLE, "w", encoding="utf-8") as f:
        f.write(s)
    print("%d remplacements appliqués." % len(R))


if __name__ == "__main__":
    main()
