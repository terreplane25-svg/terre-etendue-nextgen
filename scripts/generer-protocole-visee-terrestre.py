#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Écrit la méthode d'essai « Hauteur masquée sur une visée terrestre longue ».

Forme du document
─────────────────
Le document suit l'ordre des sections d'une méthode d'essai normalisée — celui
que l'ASTM impose à ses standard test methods et que reprennent la plupart des
agences :

    1 Domaine d'application · 2 Documents de référence · 3 Terminologie ·
    4 Résumé de la méthode · 5 Intérêt et emploi · 6 Appareillage ·
    7 Station et cible · 8 Mode opératoire · 9 Calcul · 10 Rapport d'essai ·
    11 Fidélité et biais · Annexe X1 (non normative)

La règle qui compte, et que nos protocoles violaient : **le raisonnement, la
justification, l'histoire et la polémique ne figurent pas dans le corps.** Ils
vont en appendice non normatif. Le corps ne contient que ce qu'il faut faire,
à l'impératif, avec des seuils chiffrés.

L'expérience, réduite à son os
──────────────────────────────
Entrées : la hauteur d'œil h1, la distance d, et l'altitude du point le plus bas
qui reste visible sur l'objet visé.
Sortie  : le coefficient de réfraction k qui rend compte de l'observation, et le
rayon apparent R' = R/(1−k) qui s'en déduit.

Il n'y a pas de verdict binaire. Sur la visée Karagöl→Shkhara, voir la base
exige k = 0,837 ; voir à partir de 2 000 m exige k = 0,471 ; ne voir que la cime
exige k = 0,144. La question « cette observation est-elle possible ? » n'a de
sens qu'une fois dit **jusqu'où** l'objet est vu — et une fois k mesuré le même
jour, ce que personne n'a fait.

C'est pourquoi la méthode impose une seconde mesure, indépendante : les visées
zénithales réciproques simultanées, qui sont la manière normalisée de déterminer
k en géodésie. Le résultat est un couple (k exigé par l'observation, k mesuré
sur place). Aucun des deux n'est supposé.
"""
import math
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTOCOLES = os.path.join(RACINE, "content", "protocoles")
MODELE = os.path.join(PROTOCOLES, "soleil-bilingue.html")
CIBLE = os.path.join(PROTOCOLES, "visee-terrestre-bilingue.html")

R = 6371.0
KARAGOL = (3107.0, 493.07, 5193.0)
FINESTRELLES = (2826.0, 443.0, 4102.0)
K_MOYEN, K_INVERSION = 0.13, 0.47
BASE_MINI = 10          # km
LECTURE = 5.0           # secondes d'arc
DEVIATION = 30.0        # secondes d'arc, cas montagneux défavorable
PALIERS = [0.0, 1000.0, 2000.0, 3000.0, 4000.0]


def rayon_apparent(k):
    return R / (1 - k)


def cachee(h1, d, k):
    Rp = rayon_apparent(k)
    a = math.sqrt((Rp + h1 / 1000.0) ** 2 - Rp ** 2)
    return 0.0 if d <= a else (math.sqrt(Rp ** 2 + (d - a) ** 2) - Rp) * 1000.0


def k_pour(h1, d, c):
    lo, hi = 0.0, 0.99
    for _ in range(300):
        m = (lo + hi) / 2
        if cachee(h1, d, m) > c:
            lo = m
        else:
            hi = m
    return hi


def ecart_reciproque(d, k):
    """(z_A + z_B − 180°) en secondes d'arc."""
    return math.degrees(d / rayon_apparent(k)) * 3600


def controle():
    h1, d, som = KARAGOL
    assert abs(cachee(h1, d, K_MOYEN) - 5341) < 3
    assert abs(k_pour(h1, d, 0.0) - 0.837) < 0.002
    assert abs(k_pour(h1, d, som) - 0.144) < 0.002
    assert abs(k_pour(h1, d, 2000.0) - 0.471) < 0.002
    h2, d2, som2 = FINESTRELLES
    assert abs(cachee(h2, d2, K_MOYEN) - 3917) < 3
    assert abs(k_pour(h2, d2, 0.0) - 0.817) < 0.002
    assert abs(rayon_apparent(K_MOYEN) - 7323) < 2
    assert abs(rayon_apparent(k_pour(h1, d, 0.0)) - 39123) < 200
    base = cachee(h1, d, K_MOYEN)
    assert abs((cachee(h1, d, K_MOYEN + 0.01) - base) + 108) < 3
    assert abs((cachee(h1 + 10, d, K_MOYEN) - base) + 13) < 2
    assert abs((cachee(h1, d + 1, K_MOYEN) - base) - 38) < 2
    assert abs(ecart_reciproque(BASE_MINI, K_INVERSION) - 172) < 2
    return True


def nb(x, n, fr):
    return ("%.*f" % (n, x)).replace(".", "," if fr else ".")


def mil(x, fr):
    return "{:,.0f}".format(x).replace(",", "&#8239;")


def t_paliers(fr):
    h1, d, som = KARAGOL
    out = []
    for c in PALIERS + [som]:
        k = k_pour(h1, d, c)
        lib = (("la base du massif" if fr else "the base of the massif") if c == 0
               else ("la cime seule" if fr else "the summit alone") if c == som
               else ("%s m au-dessus de la base" % mil(c, fr)) if fr
               else "%s m above the base" % mil(c, fr))
        cls = ' class="hi"' if c == 0 else ""
        g = (lambda s: "<strong>%s</strong>" % s) if cls else (lambda s: s)
        out.append('    <tr%s><td>%s</td><td class="n">%s</td>'
                   '<td class="n">%s</td><td class="n">%s km</td></tr>'
                   % (cls, g(lib), g(mil(c, fr)), g(nb(k, 3, fr)),
                      g(mil(rayon_apparent(k), fr))))
    return "\n".join(out)


def t_sensibilite(fr):
    h1, d, _ = KARAGOL
    base = cachee(h1, d, K_MOYEN)
    lignes = [("k : +0,01" if fr else "k: +0.01", cachee(h1, d, 0.14) - base, True),
              ("hauteur d'&#339;il : +10 m" if fr else "eye height: +10 m",
               cachee(h1 + 10, d, K_MOYEN) - base, False),
              ("hauteur d'&#339;il : +100 m" if fr else "eye height: +100 m",
               cachee(h1 + 100, d, K_MOYEN) - base, False),
              ("distance : +1 km" if fr else "distance: +1 km",
               cachee(h1, d + 1, K_MOYEN) - base, False),
              ("distance : +10 km" if fr else "distance: +10 km",
               cachee(h1, d + 10, K_MOYEN) - base, False)]
    out = []
    for lib, dv, vedette in lignes:
        txt = "%s%s m" % ("+" if dv > 0 else "&#8722;", nb(abs(dv), 0, fr))
        cls = ' class="hi"' if vedette else ""
        g = (lambda s: "<strong>%s</strong>" % s) if vedette else (lambda s: s)
        out.append('    <tr%s><td>%s</td><td class="n">%s</td></tr>'
                   % (cls, g(lib), g(txt)))
    return "\n".join(out)


def t_reciproque(fr):
    out = []
    for d in (5, 10, 20, 50):
        cells = "".join('<td class="n">%s</td>' % nb(ecart_reciproque(d, k), 0, fr)
                        for k in (0.0, K_MOYEN, 0.25, K_INVERSION))
        sig = ecart_reciproque(d, K_INVERSION) / (LECTURE * math.sqrt(2))
        cls = ' class="hi"' if d == BASE_MINI else ""
        out.append('    <tr%s><td class="n">%d</td>%s<td class="n">0</td>'
                   '<td class="n">%s</td></tr>' % (cls, d, cells, nb(sig, 0, fr)))
    return "\n".join(out)


def corps(fr):
    h1, d, som = KARAGOL
    h2, d2, som2 = FINESTRELLES
    masque = cachee(h1, d, K_MOYEN)
    masque_f = cachee(h2, d2, K_MOYEN)
    k_base = k_pour(h1, d, 0.0)
    k_cime = k_pour(h1, d, som)
    sig10 = ecart_reciproque(BASE_MINI, K_INVERSION) / (LECTURE * math.sqrt(2))

    if fr:
        return f"""<div class="masthead">
  <div class="kicker">M&#233;thode d'essai &#183; Structure normalis&#233;e &#183; Annexe non normative</div>
  <h1>Hauteur masqu&#233;e sur une vis&#233;e terrestre longue</h1>
  <p class="sub">D&#233;termination du coefficient de r&#233;fraction rendant compte d'une observation &#224; longue distance</p>
  <div class="byline">
    <span>R&#233;dacteur<b>&nbsp;</b></span><span>Affiliation<b>&nbsp;</b></span>
    <span>Contact<b>&nbsp;</b></span><span>Version<b>2.0</b></span><span>Date<b>&nbsp;</b></span>
  </div>
</div>

<h2><span class="n">1</span>Domaine d'application</h2>
<p>1.1 &#8212; La pr&#233;sente m&#233;thode d&#233;termine, pour une vis&#233;e terrestre dont la port&#233;e est
comprise entre 10 et 500 km, le <strong>coefficient de r&#233;fraction</strong> <code>k</code> qui
rend compte de la hauteur d'objet demeur&#233;e visible, et le <strong>rayon apparent</strong>
<code>R&#8242;</code> qui s'en d&#233;duit.</p>
<p>1.2 &#8212; Elle exige, sur la m&#234;me journ&#233;e et le long du m&#234;me azimut, une seconde
d&#233;termination de <code>k</code> par vis&#233;es z&#233;nithales r&#233;ciproques simultan&#233;es. Le
r&#233;sultat d'essai est le couple form&#233; par ces deux valeurs.</p>
<p>1.3 &#8212; Elle s'applique aux objets dont les coordonn&#233;es et l'altitude de base sont
publi&#233;es par un service g&#233;od&#233;sique national.</p>
<p>1.4 &#8212; La m&#233;thode <strong>ne d&#233;termine pas la forme de la Terre</strong> et ne conclut sur
aucun mod&#232;le. Elle produit deux nombres et leurs incertitudes.</p>
<p>1.5 &#8212; Les valeurs sont exprim&#233;es en unit&#233;s SI.</p>
<p>1.6 &#8212; <em>Avertissement.</em> Les stations utilisables sont en altitude et d'acc&#232;s
alpin. La pr&#233;sente m&#233;thode ne traite pas la s&#233;curit&#233; en montagne, qui rel&#232;ve de
l'op&#233;rateur.</p>

<h2><span class="n">2</span>Documents de r&#233;f&#233;rence</h2>
<p>2.1 &#8212; JCGM 100:2008, <em>&#201;valuation des donn&#233;es de mesure &#8212; Guide pour
l'expression de l'incertitude de mesure</em> (GUM).</p>
<p>2.2 &#8212; ISO/IEC 17025:2017, <em>Exigences g&#233;n&#233;rales concernant la comp&#233;tence des
laboratoires d'&#233;talonnages et d'essais</em>.</p>
<p>2.3 &#8212; NOAA Technical Report NOS 92 NGS 22, <em>Results of Leveling Refraction Tests by
the National Geodetic Survey</em>.</p>
<p>2.4 &#8212; <em>Practical Formulas for the Refraction Coefficient</em>, Journal of Surveying
Engineering, vol. 140, n&#176; 2.</p>
<p>2.5 &#8212; Coordonn&#233;es et altitudes&#160;: r&#233;f&#233;rentiel du service g&#233;od&#233;sique national du
pays de la station et de celui de la cible, cit&#233;s avec leur millésime.</p>

<h2><span class="n">3</span>Terminologie</h2>
<p>3.1 <strong>hauteur d'&#339;il</strong>, <code>h&#8321;</code>, <em>m</em> &#8212; altitude du centre
optique de l'instrument au-dessus du niveau de r&#233;f&#233;rence.</p>
<p>3.2 <strong>port&#233;e</strong>, <code>d</code>, <em>km</em> &#8212; distance g&#233;od&#233;sique entre la
station et la cible.</p>
<p>3.3 <strong>point bas visible</strong> &#8212; point de la cible, identifiable sur son profil
publi&#233;, situ&#233; &#224; la plus basse altitude encore observ&#233;e depuis la station.</p>
<p>3.4 <strong>hauteur masqu&#233;e observ&#233;e</strong>, <code>c<sub>obs</sub></code>, <em>m</em>
&#8212; altitude du point bas visible diminu&#233;e de l'altitude de la base de la cible.</p>
<p>3.5 <strong>coefficient de r&#233;fraction</strong>, <code>k</code>, sans dimension &#8212; rapport
de la courbure du rayon lumineux &#224; celle de la surface de r&#233;f&#233;rence.</p>
<p>3.6 <strong>rayon apparent</strong>, <code>R&#8242;</code>, <em>km</em> &#8212;
<code>R&#8242; = R/(1&#8722;k)</code>, avec <code>R</code> = 6&#8239;371 km.</p>

<h2><span class="n">4</span>R&#233;sum&#233; de la m&#233;thode</h2>
<p>4.1 &#8212; La position et la hauteur d'&#339;il de la station sont d&#233;termin&#233;es par GNSS.</p>
<p>4.2 &#8212; La cible est identifi&#233;e par son azimut, compar&#233; au rel&#232;vement calcul&#233; depuis
les coordonn&#233;es publi&#233;es.</p>
<p>4.3 &#8212; Le point bas visible est identifi&#233; sur le profil publi&#233; de la cible et son
altitude relev&#233;e, d'o&#249; <code>c<sub>obs</sub></code>.</p>
<p>4.4 &#8212; On r&#233;sout <code>c(k) = c<sub>obs</sub></code>, ce qui donne
<code>k<sub>exig&#233;</sub></code> et <code>R&#8242;</code>.</p>
<p>4.5 &#8212; Le m&#234;me jour, sur une base d'au moins {BASE_MINI} km align&#233;e sur le m&#234;me azimut,
<code>k<sub>mesur&#233;</sub></code> est d&#233;termin&#233; par vis&#233;es z&#233;nithales r&#233;ciproques
simultan&#233;es.</p>
<p>4.6 &#8212; Le r&#233;sultat d'essai est le couple
<code>(k<sub>exig&#233;</sub>, k<sub>mesur&#233;</sub>)</code> avec leurs incertitudes &#233;largies.</p>

<h2><span class="n">5</span>Int&#233;r&#234;t et emploi</h2>
<p>5.1 &#8212; La hauteur masqu&#233;e est la seule grandeur qu'une photographie &#224; longue distance
permette de confronter directement au calcul g&#233;om&#233;trique.</p>
<p>5.2 &#8212; Ce calcul d&#233;pend de <code>k</code> plus que de toute autre entr&#233;e. Le tableau 1
donne les d&#233;riv&#233;es partielles sur une vis&#233;e de {nb(d, 2, fr)} km.</p>
<p>5.3 &#8212; Une observation &#224; longue distance non accompagn&#233;e d'une d&#233;termination de
<code>k</code> le m&#234;me jour <strong>n'est pas exploitable</strong>, quelle que soit la
conclusion qu'on en tire.</p>
<table>
  <caption>Tableau 1 &#8212; Variation de la hauteur masqu&#233;e pour un &#233;cart sur chaque
  entr&#233;e. Vis&#233;e de r&#233;f&#233;rence&#160;: {mil(h1, fr)} m, {nb(d, 2, fr)} km, autour de
  <code>k = 0,13</code>.</caption>
  <thead><tr><th>&#233;cart sur l'entr&#233;e</th><th class="n">variation de c</th></tr></thead>
  <tbody>
{t_sensibilite(fr)}
  </tbody>
</table>

<h2><span class="n">6</span>Appareillage</h2>
<p>6.1 &#8212; <strong>Th&#233;odolite ou station totale</strong>, &#233;cart-type de lecture angulaire
&#8804; {nb(LECTURE, 0, fr)}&#8243;, compensateur bi-axial, certificat d'&#233;talonnage de moins de
douze mois. Deux exemplaires sont n&#233;cessaires pour la section 8.6.</p>
<p>6.2 &#8212; <strong>Appareil photographique</strong> &#224; capteur plein format, objectif de
300 &#224; 600 mm, bague de mise au point et de focale immobilis&#233;es m&#233;caniquement pour la
dur&#233;e de l'essai. Enregistrement en donn&#233;es brutes.</p>
<p>6.3 &#8212; <strong>R&#233;cepteur GNSS</strong> bifr&#233;quence, incertitude verticale &#233;largie
&#8804; 0,5 m.</p>
<p>6.4 &#8212; <strong>Instruments m&#233;t&#233;orologiques</strong>&#160;: thermom&#232;tre &#177; 0,5 &#176;C,
barom&#232;tre &#177; 1 hPa, hygrom&#232;tre &#177; 5 %.</p>
<p>6.5 &#8212; <strong>Horloges</strong> synchronis&#233;es sur GNSS, &#233;cart &#8804; 1 s entre les deux
stations.</p>

<h2><span class="n">7</span>Station et cible</h2>
<p>7.1 &#8212; La station est mat&#233;rialis&#233;e par un rep&#232;re permanent ou, &#224; d&#233;faut, par un
point dont les coordonn&#233;es sont relev&#233;es pendant au moins trente minutes d'observation
GNSS statique.</p>
<p>7.2 &#8212; La cible poss&#232;de des coordonn&#233;es et une altitude de base publi&#233;es, ainsi qu'un
mod&#232;le num&#233;rique de terrain permettant d'attribuer une altitude au point bas visible.</p>
<p>7.3 &#8212; La base des vis&#233;es r&#233;ciproques mesure au moins {BASE_MINI} km et son azimut ne
s'&#233;carte pas de plus de 30&#176; de celui de la cible.</p>
<p>7.4 &#8212; Les deux extr&#233;mit&#233;s de la base sont choisies en terrain de relief mod&#233;r&#233;,
sauf &#224; disposer d'une grille publi&#233;e de d&#233;viation de la verticale pour la r&#233;gion.</p>

<h2 class="brk"><span class="n">8</span>Mode op&#233;ratoire</h2>
<p>8.1 &#8212; Relever la position et la hauteur d'&#339;il de la station&#160;; consigner
l'incertitude verticale.</p>
<p>8.2 &#8212; Mesurer l'azimut de la cible, r&#233;f&#233;renc&#233; &#224; une direction connue ou &#224; une
vis&#233;e solaire r&#233;duite par &#233;ph&#233;m&#233;ride. Calculer le rel&#232;vement g&#233;od&#233;sique
station&#8594;cible.</p>
<p>8.3 &#8212; <strong>Crit&#232;re d'identification.</strong> L'&#233;cart azimut mesur&#233; moins
rel&#232;vement calcul&#233; doit rester inf&#233;rieur &#224; 0,05&#176;, et aucune autre cible candidate ne
doit se trouver dans une fen&#234;tre de &#177; 0,20&#176; autour de l'azimut mesur&#233;. Si l'un des deux
crit&#232;res n'est pas satisfait, l'essai est nul.</p>
<p>8.4 &#8212; Photographier la cible sans recadrage ni redressement, puis photographier la
sc&#232;ne enti&#232;re au grand angle avec des rep&#232;res proches identifiables.</p>
<p>8.5 &#8212; Identifier le point bas visible par comparaison avec le profil publi&#233; de la
cible et relever son altitude. Consigner l'incertitude d'attribution.</p>
<p>8.6 &#8212; <strong>Vis&#233;es r&#233;ciproques.</strong> Aux deux extr&#233;mit&#233;s de la base, mesurer
l'angle z&#233;nithal vers l'autre station&#160;: dix point&#233;s altern&#233;s cercle gauche / cercle
droit, l'ensemble des vingt point&#233;s tenant dans la m&#234;me minute aux deux stations.</p>
<p>8.7 &#8212; R&#233;p&#233;ter 8.6 trois fois, &#224; une heure d'intervalle.</p>
<p>8.8 &#8212; Relever temp&#233;rature, pression et humidit&#233; &#224; chaque station au d&#233;but et &#224; la
fin de chaque s&#233;rie.</p>
<p>8.9 &#8212; <strong>Crit&#232;res de rejet.</strong> L'essai est rejet&#233; si l'un des cas suivants
se pr&#233;sente&#160;:</p>
<ul>
  <li>l'&#233;cart entre deux des trois valeurs de <code>k<sub>mesur&#233;</sub></code> d&#233;passe trois
  fois leur incertitude combin&#233;e&#160;;</li>
  <li>l'&#233;cart de simultan&#233;it&#233; entre les deux stations d&#233;passe 60 s pour une s&#233;rie&#160;;</li>
  <li>le point bas visible ne peut pas &#234;tre attribu&#233; &#224; une altitude &#224; mieux que
  &#177; 200 m&#160;;</li>
  <li>la mise au point ou la focale ont &#233;t&#233; modifi&#233;es pendant l'essai.</li>
</ul>

<h2><span class="n">9</span>Calcul</h2>
<p>9.1 &#8212; Hauteur masqu&#233;e observ&#233;e&#160;:
<code>c<sub>obs</sub> = H<sub>point bas</sub> &#8722; H<sub>base</sub></code>.</p>
<p>9.2 &#8212; Hauteur masqu&#233;e calcul&#233;e, pour un coefficient <code>k</code> donn&#233;&#160;:</p>
<div class="eq">
  a = &#8730;[(R&#8242;+h&#8321;)&#178; &#8722; R&#8242;&#178;]&#160;&#160;&#160;&#160;
  c(k) = &#8730;[R&#8242;&#178; + (d&#8722;a)&#178;] &#8722; R&#8242;
  <span class="cap">a est la port&#233;e du point tangent. R&#8242; = R/(1&#8722;k). h&#8321; et c en km dans la formule, converties en m&#232;tres au r&#233;sultat.</span>
</div>
<p>9.3 &#8212; R&#233;soudre <code>c(k) = c<sub>obs</sub></code> par dichotomie sur
<code>k &#8712; [0 ; 0,99]</code>. La solution est <code>k<sub>exig&#233;</sub></code>, d'o&#249;
<code>R&#8242; = R/(1&#8722;k<sub>exig&#233;</sub>)</code>.</p>
<p>9.4 &#8212; Vis&#233;es r&#233;ciproques&#160;: <code>R&#8242; = d / (z<sub>A</sub> + z<sub>B</sub> &#8722;
180&#176;)</code>, angles en radians, d'o&#249; <code>k<sub>mesur&#233;</sub> = 1 &#8722; R/R&#8242;</code>.
Moyenner les trois s&#233;ries.</p>
<p>9.5 &#8212; &#201;valuer les incertitudes selon 2.1. Les composantes &#224; retenir au minimum sont
celles du tableau 1, l'incertitude d'attribution du point bas visible, et la d&#233;viation de la
verticale pour 9.4.</p>
<table>
  <caption>Tableau 2 &#8212; &#201;cart <code>z<sub>A</sub>+z<sub>B</sub>&#8722;180&#176;</code> attendu, en
  secondes d'arc, et s&#233;paration d'avec z&#233;ro pour deux instruments &#224; {nb(LECTURE, 0, fr)}&#8243;
  dans le cas le moins favorable (k = 0,47).</caption>
  <thead><tr><th class="n">base (km)</th><th class="n">k = 0</th><th class="n">k = 0,13</th><th class="n">k = 0,25</th><th class="n">k = 0,47</th><th class="n">R&#8242; infini</th><th class="n">&#963;</th></tr></thead>
  <tbody>
{t_reciproque(fr)}
  </tbody>
</table>

<h2><span class="n">10</span>Rapport d'essai</h2>
<p>10.1 &#8212; Le rapport mentionne&#160;:</p>
<ul>
  <li>coordonn&#233;es, hauteur d'&#339;il et incertitude verticale de la station, avec le
  r&#233;f&#233;rentiel employ&#233;&#160;;</li>
  <li>identification de la cible, azimut mesur&#233;, rel&#232;vement calcul&#233;, et la
  d&#233;monstration d'unicit&#233; du 8.3&#160;;</li>
  <li>altitude attribu&#233;e au point bas visible et son incertitude&#160;;</li>
  <li><code>c<sub>obs</sub></code>, <code>k<sub>exig&#233;</sub></code>, <code>R&#8242;</code>, avec
  incertitudes &#233;largies (k = 2)&#160;;</li>
  <li>les trois valeurs de <code>k<sub>mesur&#233;</sub></code>, leur moyenne et leur
  dispersion&#160;;</li>
  <li>heure UTC, temp&#233;rature, pression et humidit&#233; de chaque s&#233;rie&#160;;</li>
  <li>focale, ouverture, temps de pose&#160;;</li>
  <li>tout crit&#232;re de 8.9 non satisfait&#160;;</li>
  <li>les fichiers bruts, publi&#233;s et accessibles.</li>
</ul>
<p>10.2 &#8212; Le rapport ne conclut pas sur un mod&#232;le. Il &#233;nonce
<code>k<sub>exig&#233;</sub></code> et <code>k<sub>mesur&#233;</sub></code>.</p>

<h2><span class="n">11</span>Fid&#233;lit&#233; et biais</h2>
<p>11.1 &#8212; <strong>Fid&#233;lit&#233;.</strong> Aucune &#233;tude interlaboratoires n'a &#233;t&#233; conduite
&#224; ce jour. La pr&#233;sente d&#233;claration sera compl&#233;t&#233;e d&#232;s que trois op&#233;rateurs
ind&#233;pendants auront appliqu&#233; la m&#233;thode &#224; la m&#234;me vis&#233;e.</p>
<p>11.2 &#8212; <strong>Biais.</strong> La d&#233;viation de la verticale biaise 9.4&#160;: les
d&#233;viations aux deux stations ne se compensent pas dans la somme. Une valeur de
{nb(DEVIATION, 0, fr)}&#8243; &#224; chaque extr&#233;mit&#233; produit jusqu'&#224; {nb(2 * DEVIATION, 0, fr)}&#8243;
de biais, &#224; comparer aux {nb(ecart_reciproque(BASE_MINI, K_INVERSION), 0, fr)}&#8243; de signal
sur une base de {BASE_MINI} km dans le cas le moins favorable. Le biais ne cro&#238;t pas avec la
base&#160;; le signal y cro&#238;t proportionnellement.</p>
<p>11.3 &#8212; L'attribution du point bas visible est la seconde source de biais. Elle est
born&#233;e par le crit&#232;re de rejet du 8.9.</p>

<h2 class="brk"><span class="n">X1</span>Annexe non normative &#8212; d'o&#249; viennent ces exigences</h2>
<p class="lead">Les informations de la pr&#233;sente annexe ne constituent pas des exigences.</p>
<h3>X1.1 &#8212; Pourquoi la question n'a pas de r&#233;ponse binaire</h3>
<p>On demande souvent si telle observation &#171;&#160;est possible sur une Terre
sph&#233;rique&#160;&#187;. La question n'est pas ferm&#233;e tant qu'on n'a pas dit
<strong>jusqu'o&#249;</strong> l'objet est vu. Chaque hauteur de point bas visible correspond &#224;
un coefficient de r&#233;fraction, et c'est lui, non un verdict, que la m&#233;thode produit.</p>
<table>
  <caption>Tableau X1.1 &#8212; Vis&#233;e Karag&#246;l&#8594;Shkhara&#160;: {mil(h1, fr)} m,
  {nb(d, 2, fr)} km, massif de {mil(som, fr)} m. Le coefficient exig&#233; selon la hauteur
  effectivement visible.</caption>
  <thead><tr><th>point bas visible</th><th class="n">c<sub>obs</sub></th><th class="n">k exig&#233;</th><th class="n">R&#8242;</th></tr></thead>
  <tbody>
{t_paliers(fr)}
  </tbody>
</table>
<p>&#192; titre de comparaison, l'atmosph&#232;re r&#233;elle donne <code>k &#8776; 0,13</code> en r&#233;gime
ordinaire et jusqu'&#224; <code>k &#8776; 0,47</code> sous inversion thermique forte au ras du sol
(2.3, 2.4). Au coefficient ordinaire, la sph&#232;re masque {mil(masque, fr)} m sur cette vis&#233;e,
soit davantage que la hauteur du massif&#160;; sur la vis&#233;e
Finestrelles&#8594;Barre des &#201;crins ({mil(h2, fr)} m, {nb(d2, 0, fr)} km), elle en masque
{mil(masque_f, fr)} m sur {mil(som2, fr)}.</p>
<h3>X1.2 &#8212; Pourquoi une seconde d&#233;termination de k est impos&#233;e</h3>
<p>Voir la base du Shkhara exige <code>k = {nb(k_base, 3, fr)}</code>, soit un rayon apparent de
{mil(rayon_apparent(k_base), fr)} km &#8212; {nb(rayon_apparent(k_base) / R, 1, fr)} fois le rayon
terrestre. N'en voir que la cime exige <code>k = {nb(k_cime, 3, fr)}</code>. Ces deux nombres
bornent le d&#233;bat public sur cette photographie, et <strong>aucun des deux camps ne les a
mesur&#233;s sur le trajet</strong>. La m&#233;thode impose donc la mesure plut&#244;t que l'hypoth&#232;se.</p>
<h3>X1.3 &#8212; Pourquoi les vis&#233;es r&#233;ciproques, et pourquoi simultan&#233;es</h3>
<p>La somme des deux angles z&#233;nithaux r&#233;ciproques ne d&#233;pend pas des altitudes des
stations&#160;: une diff&#233;rence de hauteur augmente un angle d'autant qu'elle diminue l'autre.
Il ne subsiste que l'angle dont les deux verticales locales divergent. C'est la m&#233;thode
normalis&#233;e de d&#233;termination de <code>k</code> en g&#233;od&#233;sie (2.3, 2.4). La simultan&#233;it&#233;
est requise parce que <code>k</code> varie au cours de la journ&#233;e&#160;; deux vis&#233;es
d&#233;cal&#233;es mesureraient deux atmosph&#232;res.</p>
<h3>X1.4 &#8212; Ce que la m&#233;thode n'&#233;tablit pas</h3>
<p>Elle donne <code>R&#8242;</code> le long d'un azimut, &#224; un moment, dans une masse d'air.
Elle ne donne pas la forme de la Terre, et elle ne s&#233;pare pas la courbure du sol de celle du
rayon&#160;: <code>R&#8242;</code> contient les deux.</p>
<p>Elle ne valide ni n'invalide r&#233;troactivement une photographie prise ailleurs, un autre
jour, dans une autre atmosph&#232;re. Tant qu'une vis&#233;e n'a pas &#233;t&#233; reprise sur place selon
la pr&#233;sente m&#233;thode, ni son impossibilit&#233; ni sa validit&#233; ne sont &#233;tablies.</p>
<p>Si une application de la m&#233;thode produit un <code>k<sub>exig&#233;</sub></code> compatible
avec le <code>k<sub>mesur&#233;</sub></code> du jour, l'observation est rendue coh&#233;rente avec la
surface de r&#233;f&#233;rence employ&#233;e, et doit &#234;tre rapport&#233;e comme telle.</p>"""

    return f"""<div class="masthead">
  <div class="kicker">Test method &#183; Standard section order &#183; Non-mandatory appendix</div>
  <h1>Hidden height on a long terrestrial sight line</h1>
  <p class="sub">Determination of the refraction coefficient accounting for a long-range observation</p>
  <div class="byline">
    <span>Author<b>&nbsp;</b></span><span>Affiliation<b>&nbsp;</b></span>
    <span>Contact<b>&nbsp;</b></span><span>Version<b>2.0</b></span><span>Date<b>&nbsp;</b></span>
  </div>
</div>

<h2><span class="n">1</span>Scope</h2>
<p>1.1 &#8212; This method determines, for a terrestrial sight line of range between 10 and
500 km, the <strong>refraction coefficient</strong> <code>k</code> that accounts for the height
of the target remaining visible, and the <strong>apparent radius</strong> <code>R&#8242;</code>
derived from it.</p>
<p>1.2 &#8212; It requires, on the same day and along the same azimuth, a second determination of
<code>k</code> by simultaneous reciprocal zenith angles. The test result is the pair formed by
these two values.</p>
<p>1.3 &#8212; It applies to targets whose coordinates and base elevation are published by a
national geodetic service.</p>
<p>1.4 &#8212; The method <strong>does not determine the shape of the Earth</strong> and concludes
on no model. It produces two numbers and their uncertainties.</p>
<p>1.5 &#8212; Values are expressed in SI units.</p>
<p>1.6 &#8212; <em>Warning.</em> Usable stations are at altitude and of alpine access. This method
does not address mountain safety, which rests with the operator.</p>

<h2><span class="n">2</span>Referenced documents</h2>
<p>2.1 &#8212; JCGM 100:2008, <em>Evaluation of measurement data &#8212; Guide to the expression of
uncertainty in measurement</em> (GUM).</p>
<p>2.2 &#8212; ISO/IEC 17025:2017, <em>General requirements for the competence of testing and
calibration laboratories</em>.</p>
<p>2.3 &#8212; NOAA Technical Report NOS 92 NGS 22, <em>Results of Leveling Refraction Tests by
the National Geodetic Survey</em>.</p>
<p>2.4 &#8212; <em>Practical Formulas for the Refraction Coefficient</em>, Journal of Surveying
Engineering, vol. 140, no. 2.</p>
<p>2.5 &#8212; Coordinates and elevations: the national geodetic reference frame of the station's
country and of the target's, cited with their epoch.</p>

<h2><span class="n">3</span>Terminology</h2>
<p>3.1 <strong>eye height</strong>, <code>h&#8321;</code>, <em>m</em> &#8212; elevation of the
instrument's optical centre above the reference level.</p>
<p>3.2 <strong>range</strong>, <code>d</code>, <em>km</em> &#8212; geodetic distance between
station and target.</p>
<p>3.3 <strong>lowest visible point</strong> &#8212; the point of the target, identifiable on its
published profile, at the lowest elevation still observed from the station.</p>
<p>3.4 <strong>observed hidden height</strong>, <code>c<sub>obs</sub></code>, <em>m</em> &#8212;
elevation of the lowest visible point less the elevation of the target's base.</p>
<p>3.5 <strong>refraction coefficient</strong>, <code>k</code>, dimensionless &#8212; ratio of the
curvature of the light ray to that of the reference surface.</p>
<p>3.6 <strong>apparent radius</strong>, <code>R&#8242;</code>, <em>km</em> &#8212;
<code>R&#8242; = R/(1&#8722;k)</code>, with <code>R</code> = 6&#8239;371 km.</p>

<h2><span class="n">4</span>Summary of method</h2>
<p>4.1 &#8212; The station's position and eye height are determined by GNSS.</p>
<p>4.2 &#8212; The target is identified by its azimuth, compared with the bearing computed from
published coordinates.</p>
<p>4.3 &#8212; The lowest visible point is identified on the target's published profile and its
elevation read, giving <code>c<sub>obs</sub></code>.</p>
<p>4.4 &#8212; <code>c(k) = c<sub>obs</sub></code> is solved, giving
<code>k<sub>required</sub></code> and <code>R&#8242;</code>.</p>
<p>4.5 &#8212; On the same day, over a baseline of at least {BASE_MINI} km aligned on the same
azimuth, <code>k<sub>measured</sub></code> is determined by simultaneous reciprocal zenith
angles.</p>
<p>4.6 &#8212; The test result is the pair
<code>(k<sub>required</sub>, k<sub>measured</sub>)</code> with their expanded uncertainties.</p>

<h2><span class="n">5</span>Significance and use</h2>
<p>5.1 &#8212; Hidden height is the only quantity a long-range photograph allows to be compared
directly with geometric calculation.</p>
<p>5.2 &#8212; That calculation depends on <code>k</code> more than on any other input. Table 1
gives the partial derivatives on a {nb(d, 2, fr)} km line.</p>
<p>5.3 &#8212; A long-range observation unaccompanied by a same-day determination of
<code>k</code> <strong>is not usable</strong>, whatever conclusion is drawn from it.</p>
<table>
  <caption>Table 1 &#8212; Change in hidden height for a departure in each input. Reference line:
  {mil(h1, fr)} m, {nb(d, 2, fr)} km, about <code>k = 0.13</code>.</caption>
  <thead><tr><th>departure in input</th><th class="n">change in c</th></tr></thead>
  <tbody>
{t_sensibilite(fr)}
  </tbody>
</table>

<h2><span class="n">6</span>Apparatus</h2>
<p>6.1 &#8212; <strong>Theodolite or total station</strong>, angular reading standard deviation
&#8804; {nb(LECTURE, 0, fr)}&#8243;, dual-axis compensator, calibration certificate less than twelve
months old. Two units are required for 8.6.</p>
<p>6.2 &#8212; <strong>Camera</strong> with full-frame sensor, 300 to 600 mm lens, focus and focal
rings mechanically immobilised for the duration of the test. Raw recording.</p>
<p>6.3 &#8212; <strong>GNSS receiver</strong>, dual-frequency, expanded vertical uncertainty
&#8804; 0.5 m.</p>
<p>6.4 &#8212; <strong>Meteorological instruments</strong>: thermometer &#177; 0.5 &#176;C, barometer
&#177; 1 hPa, hygrometer &#177; 5 per cent.</p>
<p>6.5 &#8212; <strong>Clocks</strong> synchronised to GNSS, offset &#8804; 1 s between stations.</p>

<h2><span class="n">7</span>Station and target</h2>
<p>7.1 &#8212; The station is materialised by a permanent mark or, failing that, by a point whose
coordinates are recorded over at least thirty minutes of static GNSS observation.</p>
<p>7.2 &#8212; The target has published coordinates and base elevation, and a digital terrain
model allowing an elevation to be assigned to the lowest visible point.</p>
<p>7.3 &#8212; The reciprocal baseline is at least {BASE_MINI} km long and its azimuth departs by
no more than 30&#176; from that of the target.</p>
<p>7.4 &#8212; Both ends of the baseline are chosen in moderate relief, unless a published
deflection-of-the-vertical grid is available for the region.</p>

<h2 class="brk"><span class="n">8</span>Procedure</h2>
<p>8.1 &#8212; Record the station's position and eye height; record the vertical uncertainty.</p>
<p>8.2 &#8212; Measure the target's azimuth, referenced to a known direction or to a solar sight
reduced by ephemeris. Compute the geodetic bearing station&#8594;target.</p>
<p>8.3 &#8212; <strong>Identification criterion.</strong> The measured-minus-computed azimuth
departure shall be less than 0.05&#176;, and no other candidate target shall lie within
&#177; 0.20&#176; of the measured azimuth. If either criterion fails, the test is void.</p>
<p>8.4 &#8212; Photograph the target without cropping or straightening, then photograph the whole
scene at wide angle with identifiable near landmarks.</p>
<p>8.5 &#8212; Identify the lowest visible point by comparison with the target's published profile
and read its elevation. Record the attribution uncertainty.</p>
<p>8.6 &#8212; <strong>Reciprocal sights.</strong> At both ends of the baseline, measure the zenith
angle to the other station: ten pointings alternating face left / face right, all twenty
pointings falling within the same minute at both stations.</p>
<p>8.7 &#8212; Repeat 8.6 three times, one hour apart.</p>
<p>8.8 &#8212; Record temperature, pressure and humidity at each station at the start and end of
each run.</p>
<p>8.9 &#8212; <strong>Rejection criteria.</strong> The test is rejected if any of the following
occurs:</p>
<ul>
  <li>the departure between any two of the three <code>k<sub>measured</sub></code> values
  exceeds three times their combined uncertainty;</li>
  <li>the simultaneity offset between stations exceeds 60 s for a run;</li>
  <li>the lowest visible point cannot be assigned an elevation to better than
  &#177; 200 m;</li>
  <li>focus or focal length were altered during the test.</li>
</ul>

<h2><span class="n">9</span>Calculation</h2>
<p>9.1 &#8212; Observed hidden height:
<code>c<sub>obs</sub> = H<sub>lowest visible</sub> &#8722; H<sub>base</sub></code>.</p>
<p>9.2 &#8212; Calculated hidden height, for a given <code>k</code>:</p>
<div class="eq">
  a = &#8730;[(R&#8242;+h&#8321;)&#178; &#8722; R&#8242;&#178;]&#160;&#160;&#160;&#160;
  c(k) = &#8730;[R&#8242;&#178; + (d&#8722;a)&#178;] &#8722; R&#8242;
  <span class="cap">a is the range of the tangent point. R&#8242; = R/(1&#8722;k). h&#8321; and c in km within the formula, converted to metres in the result.</span>
</div>
<p>9.3 &#8212; Solve <code>c(k) = c<sub>obs</sub></code> by bisection over
<code>k &#8712; [0, 0.99]</code>. The solution is <code>k<sub>required</sub></code>, whence
<code>R&#8242; = R/(1&#8722;k<sub>required</sub>)</code>.</p>
<p>9.4 &#8212; Reciprocal sights: <code>R&#8242; = d / (z<sub>A</sub> + z<sub>B</sub> &#8722;
180&#176;)</code>, angles in radians, whence <code>k<sub>measured</sub> = 1 &#8722; R/R&#8242;</code>.
Average the three runs.</p>
<p>9.5 &#8212; Evaluate uncertainties per 2.1. The components to be retained as a minimum are those
of Table 1, the attribution uncertainty of the lowest visible point, and the deflection of the
vertical for 9.4.</p>
<table>
  <caption>Table 2 &#8212; Expected <code>z<sub>A</sub>+z<sub>B</sub>&#8722;180&#176;</code>, in
  arcseconds, and separation from zero for two instruments at {nb(LECTURE, 0, fr)}&#8243; in the
  least favourable case (k = 0.47).</caption>
  <thead><tr><th class="n">baseline (km)</th><th class="n">k = 0</th><th class="n">k = 0.13</th><th class="n">k = 0.25</th><th class="n">k = 0.47</th><th class="n">R&#8242; infinite</th><th class="n">&#963;</th></tr></thead>
  <tbody>
{t_reciproque(fr)}
  </tbody>
</table>

<h2><span class="n">10</span>Report</h2>
<p>10.1 &#8212; The report shall state:</p>
<ul>
  <li>station coordinates, eye height and vertical uncertainty, with the reference frame
  used;</li>
  <li>target identification, measured azimuth, computed bearing, and the uniqueness
  demonstration of 8.3;</li>
  <li>elevation assigned to the lowest visible point and its uncertainty;</li>
  <li><code>c<sub>obs</sub></code>, <code>k<sub>required</sub></code>, <code>R&#8242;</code>, with
  expanded uncertainties (k = 2);</li>
  <li>the three <code>k<sub>measured</sub></code> values, their mean and their spread;</li>
  <li>UTC time, temperature, pressure and humidity for each run;</li>
  <li>focal length, aperture, exposure time;</li>
  <li>any criterion of 8.9 not met;</li>
  <li>the raw files, published and accessible.</li>
</ul>
<p>10.2 &#8212; The report shall not conclude on a model. It states
<code>k<sub>required</sub></code> and <code>k<sub>measured</sub></code>.</p>

<h2><span class="n">11</span>Precision and bias</h2>
<p>11.1 &#8212; <strong>Precision.</strong> No interlaboratory study has been conducted to date.
This statement will be completed once three independent operators have applied the method to the
same sight line.</p>
<p>11.2 &#8212; <strong>Bias.</strong> Deflection of the vertical biases 9.4: the deflections at the
two stations do not compensate in the sum. A value of {nb(DEVIATION, 0, fr)}&#8243; at each end
produces up to {nb(2 * DEVIATION, 0, fr)}&#8243; of bias, against
{nb(ecart_reciproque(BASE_MINI, K_INVERSION), 0, fr)}&#8243; of signal over a {BASE_MINI} km
baseline in the least favourable case. The bias does not grow with the baseline; the signal grows
in proportion.</p>
<p>11.3 &#8212; Attribution of the lowest visible point is the second source of bias. It is bounded
by the rejection criterion of 8.9.</p>

<h2 class="brk"><span class="n">X1</span>Non-mandatory appendix &#8212; where these requirements come from</h2>
<p class="lead">The information in this appendix does not constitute requirements.</p>
<h3>X1.1 &#8212; Why the question has no binary answer</h3>
<p>It is often asked whether a given observation &#8220;is possible on a spherical Earth&#8221;.
The question is not closed until it is said <strong>how far down</strong> the target is seen. Each
elevation of the lowest visible point corresponds to a refraction coefficient, and it is that
coefficient, not a verdict, that the method produces.</p>
<table>
  <caption>Table X1.1 &#8212; Karag&#246;l&#8594;Shkhara line: {mil(h1, fr)} m, {nb(d, 2, fr)} km,
  massif of {mil(som, fr)} m. The coefficient required by the height actually visible.</caption>
  <thead><tr><th>lowest visible point</th><th class="n">c<sub>obs</sub></th><th class="n">k required</th><th class="n">R&#8242;</th></tr></thead>
  <tbody>
{t_paliers(fr)}
  </tbody>
</table>
<p>For comparison, the real atmosphere gives <code>k &#8776; 0.13</code> in ordinary regime and up
to <code>k &#8776; 0.47</code> under strong ground-level thermal inversion (2.3, 2.4). At the
ordinary coefficient the sphere hides {mil(masque, fr)} m on this line, more than the height of the
massif; on the Finestrelles&#8594;Barre des &#201;crins line ({mil(h2, fr)} m, {nb(d2, 0, fr)} km) it
hides {mil(masque_f, fr)} m out of {mil(som2, fr)}.</p>
<h3>X1.2 &#8212; Why a second determination of k is imposed</h3>
<p>Seeing the base of Shkhara requires <code>k = {nb(k_base, 3, fr)}</code>, an apparent radius of
{mil(rayon_apparent(k_base), fr)} km &#8212; {nb(rayon_apparent(k_base) / R, 1, fr)} times the
Earth's radius. Seeing only the summit requires <code>k = {nb(k_cime, 3, fr)}</code>. These two
numbers bound the public dispute over this photograph, and <strong>neither camp has measured them
along the path</strong>. The method therefore imposes measurement rather than assumption.</p>
<h3>X1.3 &#8212; Why reciprocal sights, and why simultaneous</h3>
<p>The sum of two reciprocal zenith angles does not depend on the stations' elevations: a height
difference raises one angle exactly as much as it lowers the other. What remains is the angle by
which the two local verticals diverge. This is the standard method of determining <code>k</code>
in geodesy (2.3, 2.4). Simultaneity is required because <code>k</code> varies through the day;
two offset sights would measure two atmospheres.</p>
<h3>X1.4 &#8212; What the method does not establish</h3>
<p>It gives <code>R&#8242;</code> along one azimuth, at one moment, through one air mass. It does not
give the shape of the Earth, and it does not separate the curvature of the ground from that of the
ray: <code>R&#8242;</code> contains both.</p>
<p>It neither validates nor invalidates, retroactively, a photograph taken elsewhere, on another
day, through another atmosphere. Until a sight line has been re-shot on site under this method,
neither its impossibility nor its validity is established.</p>
<p>If an application of the method yields a <code>k<sub>required</sub></code> consistent with the
day's <code>k<sub>measured</sub></code>, the observation is made coherent with the reference
surface used, and shall be reported as such.</p>"""


def main():
    controle()
    modele = open(MODELE, encoding="utf-8").read()
    i = modele.find('<div class="page">')
    if i < 0:
        sys.exit("squelette introuvable")
    entete = re.sub(r"<title>[^<]*</title>",
                    "<title>Hauteur masqu&#233;e sur une vis&#233;e longue "
                    "&#8212; m&#233;thode d'essai</title>", modele[:i], count=1)
    open(CIBLE, "w", encoding="utf-8").write(
        entete + '<div class="page">\n'
        '<div class="langbar"><span class="on">FRAN&#199;AIS</span>'
        '<span>ENGLISH &#8212; seconde moiti&#233;</span></div>\n\n'
        + corps(True) +
        '\n\n<div class="langbar"><span>FRAN&#199;AIS &#8212; first half</span>'
        '<span class="on">ENGLISH</span></div>\n\n'
        + corps(False) + '\n</div>\n')

    h1, d, som = KARAGOL
    print("Méthode d'essai écrite : content/protocoles/visee-terrestre-bilingue.html")
    print("  structure : 1 Domaine · 2 Références · 3 Terminologie · 4 Résumé ·")
    print("              5 Intérêt · 6 Appareillage · 7 Station · 8 Mode opératoire ·")
    print("              9 Calcul · 10 Rapport · 11 Fidélité et biais · X1 annexe")
    print("  k exigé selon le point bas visible (Karagöl→Shkhara) :")
    for c in PALIERS + [som]:
        print("    c_obs = %5.0f m  →  k = %.3f  →  R' = %6.0f km"
              % (c, k_pour(h1, d, c), rayon_apparent(k_pour(h1, d, c))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
