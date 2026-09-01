#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche de terrain — portion masquée d'un objet éloigné.

Ce que c'est, et pourquoi elle existe
─────────────────────────────────────
La méthode d'essai complète fait dix-sept pages. C'est la bonne longueur pour un
document opposable — définitions, budget d'incertitude, critères de rejet — et
la mauvaise pour quelqu'un debout sur une digue avec un trépied.

Les normes séparent d'ailleurs ces deux objets : la méthode d'essai d'un côté,
la feuille de relevé de l'autre. Voici la seconde. Elle tient sur deux pages,
ne démontre rien, ne justifie rien, et renvoie à la méthode pour tout le reste.

Ce qu'elle refuse de raccourcir
───────────────────────────────
Quatre lignes, parce que sans elles on rapporte une anecdote et non une mesure.
Chacune est chiffrée dans controle() :

  · **Le plan d'eau.** Une colline à mi-parcours masque la base d'une cible
    quelle que soit la forme de la Terre. C'est la clause qui invalide le plus
    de relevés existants, et elle ne coûte rien à respecter.

  · **La marée.** À trois mètres de hauteur d'œil et vingt-cinq kilomètres, une
    marée de deux mètres fait passer le masquage de 23 à 31 mètres. Un tiers du
    signal, pour un relevé de niveau qui prend dix secondes.

  · **Les trois hauteurs d'œil.** C'est le seul geste qui produise un verdict.
    Une surface courbe impose un écart — 26 mètres entre 1 et 20 mètres d'œil à
    vingt-cinq kilomètres — un plan à profil dégagé impose zéro, exactement et
    sans paramètre ajustable. Une mesure à hauteur unique ne distingue pas une
    occultation d'un banc de brume.

  · **Ne pas supposer k.** À vingt-cinq kilomètres et deux mètres d'œil, la
    « valeur théorique » vaut 31 m à k = 0, 26 m à k = 0,13 et 12 m à k = 0,50.
    Annoncer un chiffre théorique unique, c'est choisir la réponse avant la
    mesure. On relève ce qu'on voit, et k se déduit.
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from methode_essai import PROTOCOLES, mil, nb                     # noqa: E402

CIBLE = os.path.join(PROTOCOLES, "fiche-terrain-masquage.html")
GABARIT = os.path.join(PROTOCOLES, "visee-terrestre-bilingue.html")

R = 6371000.0
K_REF, K_MAX = 0.13, 0.50
D_REF, H_REF = 25.0, 2.0
HAUTEURS = [1, 2, 5, 10, 20]
GRILLE_H = [1, 2, 5, 10, 20]
GRILLE_D = [10, 15, 20, 25, 30, 40]


def cachee(h, d_km, k):
    if h <= 0:
        return None
    Rp = R / (1 - k)
    d = d_km * 1000.0
    a = math.sqrt((Rp + h) ** 2 - Rp ** 2)
    return 0.0 if d <= a else math.sqrt(Rp ** 2 + (d - a) ** 2) - Rp


def controle():
    """Chaque chiffre de la fiche est recalculé ici avant d'être imprimé."""
    assert abs(cachee(H_REF, D_REF, 0.00) - 31.2) < 0.3
    assert abs(cachee(H_REF, D_REF, K_REF) - 26.2) < 0.3
    assert abs(cachee(H_REF, D_REF, K_MAX) - 12.5) < 0.3
    ecart = cachee(1, D_REF, K_REF) - cachee(20, D_REF, K_REF)
    assert abs(ecart - 26.4) < 0.3, ecart
    assert abs(cachee(3, D_REF, K_REF) - 23.0) < 0.3
    assert abs(cachee(1, D_REF, K_REF) - 30.6) < 0.3
    return ecart


def grille(fr):
    lignes = []
    for h in GRILLE_H:
        cells = "".join('<td class="n">%s</td>' % nb(cachee(h, d, K_REF), 0, fr)
                        for d in GRILLE_D)
        vedette = h == 2
        lib = "<strong>%d m</strong>" % h if vedette else "%d m" % h
        lignes.append('    <tr%s><td class="n">%s</td>%s</tr>'
                      % (' class="hi"' if vedette else "", lib, cells))
    return "\n".join(lignes)


def corps(fr):
    ecart = cachee(1, D_REF, K_REF) - cachee(20, D_REF, K_REF)
    if fr:
        return f"""<div class="masthead">
  <div class="kicker">Fiche de terrain &#183; &#192; emporter &#183; Deux pages</div>
  <h1>Portion masqu&#233;e d'un objet &#233;loign&#233;</h1>
  <p class="sub">Feuille de relev&#233;. La m&#233;thode d'essai compl&#232;te,
  ses d&#233;finitions et son budget d'incertitude sont &#224; part.</p>
</div>

<h2><span class="n">1</span>Ce qu'il faut</h2>
<ul>
  <li><strong>Une cible &#224; la ligne d'eau</strong> portant au moins trois rep&#232;res
  de hauteur connus &#8212; &#233;tages, plateformes, bandes de peinture, changement de
  section. Sans rep&#232;res, on ne peut rien lire.</li>
  <li><strong>Un appareil photo</strong> et un t&#233;l&#233;objectif capables de
  r&#233;soudre le plus fin de ces rep&#232;res, sur tr&#233;pied. Format brut.</li>
  <li><strong>Un GPS</strong> pour la position, et un m&#232;tre pour la hauteur
  d'&#339;il au-dessus de l'eau.</li>
  <li><strong>Un thermom&#232;tre</strong> pour l'air et, si possible, pour l'eau.</li>
</ul>

<h2><span class="n">2</span>Le site &#8212; trois conditions non n&#233;gociables</h2>
<div class="box warn">
  <span class="lab">Sans elles, le relev&#233; ne mesure rien</span>
  <p><strong>1. La vis&#233;e passe enti&#232;rement au-dessus de l'eau.</strong> Une
  colline &#224; mi-parcours masque la base d'une cible quelle que soit la forme de la
  Terre. C'est ce qui invalide le plus de relev&#233;s en circulation.</p>
  <p><strong>2. La base de la cible est &#224; la ligne d'eau</strong>, sur le m&#234;me
  plan d'eau que vous.</p>
  <p><strong>3. Le niveau d'eau est relev&#233;</strong> aupr&#232;s du service
  mar&#233;graphique. &#192; {nb(3, 0, fr)} m d'&#339;il et {nb(D_REF, 0, fr)} km, une
  mar&#233;e de 2 m fait passer le masquage de {nb(cachee(3, D_REF, K_REF), 0, fr)} &#224;
  {nb(cachee(1, D_REF, K_REF), 0, fr)} m&#232;tres.</p>
</div>

<h2><span class="n">3</span>Sur place</h2>
<ol>
  <li><strong>Relever</strong> position, heure UTC, hauteur d'&#339;il au-dessus de
  l'eau &#224; &#177;&#8239;0,1&#8239;m, temp&#233;rature de l'air et de l'eau, niveau
  mar&#233;graphique.</li>
  <li><strong>Photographier la cible</strong> sans recadrage. Plusieurs vues.</li>
  <li><strong>Noter le plus bas rep&#232;re visible</strong> et sa hauteur au-dessus de
  la base de la cible. C'est la seule grandeur &#224; lire. Si la base elle-m&#234;me se
  voit, noter z&#233;ro.</li>
  <li><strong>Recommencer depuis trois hauteurs d'&#339;il</strong> couvrant un rapport
  d'au moins cinq &#8212; par exemple 2, 6 et 20 m&#232;tres &#8212; &#224; la
  m&#234;me distance et dans l'heure, sans toucher &#224; l'objectif.</li>
  <li><strong>Photographier la sc&#232;ne au grand angle</strong>, avec des rep&#232;res
  proches, pour qu'un tiers puisse retrouver la station.</li>
  <li><strong>Revenir un autre jour</strong>, avec un &#233;cart air&#8722;eau
  diff&#233;rent. Deux fois au moins.</li>
</ol>

<h2><span class="n">4</span>Les bonnes conditions &#8212; conseil, pas exigence</h2>
<p>Sur l'eau, tout se joue sur le signe de <code>T<sub>air</sub> &#8722;
T<sub>eau</sub></code>, parce que l'eau impose sa temp&#233;rature &#224; la couche d'air
qui la touche.</p>
<ul>
  <li><strong>Air plus chaud que l'eau</strong> &#8212; le gradient s'inverse, la
  r&#233;fraction grandit&#160;: mirages, conduits. <strong>&#192; &#233;viter.</strong></li>
  <li><strong>Air plus froid que l'eau</strong> &#8212; r&#233;fraction petite et
  stable, masquage maximal. C'est le bon r&#233;gime.</li>
  <li><strong>&#192; moins de 2&#8239;&#176;C d'&#233;cart</strong> &#8212; couche
  neutre, r&#233;fraction ordinaire et uniforme sur tout le trajet. C'est l'id&#233;al.</li>
</ul>
<div class="box key">
  <span class="lab">Le pi&#232;ge de la belle image</span>
  <p>Une inversion stratifie l'air et &#233;teint la turbulence&#160;: l'image devient
  nette, calme, magnifique. C'est justement le r&#233;gime o&#249; la r&#233;fraction est
  la plus grande et la moins fiable. Une eau plus chaude que l'air fait bouillonner
  l'image, mais la r&#233;fraction y est petite et r&#233;guli&#232;re.
  <strong>Les plus beaux clich&#233;s sont ceux auxquels il faut le moins se
  fier.</strong></p>
</div>
<ul>
  <li><strong>Ciel couvert</strong> plut&#244;t que grand soleil.</li>
  <li><strong>Vent mod&#233;r&#233;</strong>, 3 &#224; 6&#8239;m/s. Le calme plat laisse
  la stratification s'installer&#160;; le vent fort emp&#234;che de lire la ligne
  d'eau.</li>
  <li><strong>Pas dans les deux heures</strong> encadrant le lever et le coucher du
  soleil&#160;: le gradient s'y renverse.</li>
  <li><strong>Automne plut&#244;t que printemps</strong> sur mer temp&#233;r&#233;e&#160;:
  au printemps, l'air doux sur une eau encore hivernale est la saison des conduits.</li>
  <li><strong>Pas d'embouchure ni de front de courant</strong> sur le trajet.</li>
  <li><strong>Si le bord de la cible ondule</strong> visiblement dans le
  t&#233;l&#233;objectif, attendre.</li>
</ul>

<h2><span class="n">5</span>Ce qui annule la mesure</h2>
<ul>
  <li>De la terre &#233;merg&#233;e sur le trajet.</li>
  <li>Un bord si graduel qu'on ne peut pas lui assigner une hauteur&#160;: c'est de la
  brume, pas une occultation.</li>
  <li>Une seule hauteur d'&#339;il.</li>
  <li>La mise au point ou la focale chang&#233;es en cours de s&#233;rie.</li>
</ul>

<h2 class="brk"><span class="n">6</span>Ce qu'une surface de 6&#8239;371 km imposerait</h2>
<p>Portion masqu&#233;e en m&#232;tres, au coefficient de r&#233;fraction ordinaire
<code>k</code>&#8239;=&#8239;0,13. <strong>Ces valeurs sont un ordre de grandeur pour
choisir le site, pas une pr&#233;diction &#224; retrouver</strong>&#160;: &#224;
{nb(D_REF, 0, fr)}&#8239;km et {nb(H_REF, 0, fr)}&#8239;m d'&#339;il, la m&#234;me
formule donne {nb(cachee(H_REF, D_REF, 0.0), 0, fr)}&#8239;m sans r&#233;fraction et
{nb(cachee(H_REF, D_REF, K_MAX), 0, fr)}&#8239;m sous inversion forte.</p>
<table>
  <caption>Choisir une combinaison donnant au moins une dizaine de m&#232;tres.</caption>
  <thead><tr><th class="n">hauteur d'&#339;il</th>{"".join('<th class="n">%d km</th>' % d for d in GRILLE_D)}</tr></thead>
  <tbody>
{grille(fr)}
  </tbody>
</table>

<h2><span class="n">7</span>Relev&#233; &#8212; &#224; remplir</h2>
<table>
  <caption>Une ligne par hauteur d'&#339;il, trois au minimum, m&#234;me distance et
  m&#234;me heure.</caption>
  <thead><tr><th class="n">heure UTC</th><th class="n">hauteur d'&#339;il</th><th class="n">niveau d'eau</th><th class="n">plus bas rep&#232;re visible</th><th class="n">T air / T eau</th></tr></thead>
  <tbody>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
  </tbody>
</table>
<p>Distance station&#8722;cible&#160;: &#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8239;km
&#160;&#160;&#183;&#160;&#160; Cible et source de ses rep&#232;res&#160;:
&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;
&#160;&#160;&#183;&#160;&#160; Focale&#160;: &#8230;&#8230;&#8239;mm</p>

<div class="box key">
  <span class="lab">La seule chose &#224; comprendre avant de partir</span>
  <p>Ne cherchez pas &#224; retrouver un chiffre. <strong>Relevez ce que vous
  voyez</strong>, depuis trois hauteurs d'&#339;il, et laissez le calcul dire quel
  coefficient de r&#233;fraction en rend compte.</p>
  <p>Ce qui tranche n'est pas la valeur mesur&#233;e &#224; une hauteur, c'est
  l'<strong>&#233;cart entre les hauteurs</strong>. Une surface de 6&#8239;371&#8239;km
  l'impose non nul &#8212; {nb(ecart, 0, fr)}&#8239;m entre 1 et 20&#8239;m d'&#339;il
  &#224; {nb(D_REF, 0, fr)}&#8239;km. Une surface plane &#224; profil d&#233;gag&#233;
  l'impose nul, exactement, sans aucun param&#232;tre ajustable.</p>
</div>"""

    return f"""<div class="masthead">
  <div class="kicker">Field sheet &#183; To carry &#183; Two pages</div>
  <h1>Hidden portion of a distant object</h1>
  <p class="sub">Record sheet. The full test method, its definitions and its
  uncertainty budget are a separate document.</p>
</div>

<h2><span class="n">1</span>What is needed</h2>
<ul>
  <li><strong>A target at the water line</strong> bearing at least three known height
  markers &#8212; floors, platforms, paint bands, change of section. Without markers
  nothing can be read.</li>
  <li><strong>A camera</strong> and telephoto lens able to resolve the finest of those
  markers, on a tripod. Raw format.</li>
  <li><strong>A GPS</strong> for position, and a tape for the eye height above the
  water.</li>
  <li><strong>A thermometer</strong> for the air and, if possible, for the water.</li>
</ul>

<h2><span class="n">2</span>The site &#8212; three non-negotiable conditions</h2>
<div class="box warn">
  <span class="lab">Without these, the record measures nothing</span>
  <p><strong>1. The sight line passes entirely over water.</strong> A hill at mid-path
  hides a target's base whatever the shape of the Earth. This is what voids most of the
  records in circulation.</p>
  <p><strong>2. The target's base is at the water line</strong>, on the same body of
  water as you.</p>
  <p><strong>3. The water level is recorded</strong> from the tide-gauge service. At
  {nb(3, 0, fr)} m eye height and {nb(D_REF, 0, fr)} km, a 2 m tide takes the hidden
  portion from {nb(cachee(3, D_REF, K_REF), 0, fr)} to
  {nb(cachee(1, D_REF, K_REF), 0, fr)} metres.</p>
</div>

<h2><span class="n">3</span>On site</h2>
<ol>
  <li><strong>Record</strong> position, UTC time, eye height above the water to
  &#177;&#8239;0.1&#8239;m, air and water temperature, tide level.</li>
  <li><strong>Photograph the target</strong> without cropping. Several views.</li>
  <li><strong>Note the lowest visible marker</strong> and its height above the target's
  base. That is the only quantity to read. If the base itself is visible, record
  zero.</li>
  <li><strong>Repeat from three eye heights</strong> spanning a ratio of at least five
  &#8212; for instance 2, 6 and 20 metres &#8212; at the same distance and within the
  hour, without touching the lens.</li>
  <li><strong>Photograph the scene at wide angle</strong>, with near landmarks, so a
  third party can find the station again.</li>
  <li><strong>Come back another day</strong>, with a different air&#8722;water
  difference. At least twice.</li>
</ol>

<h2><span class="n">4</span>Good conditions &#8212; advice, not requirement</h2>
<p>Over water everything turns on the sign of <code>T<sub>air</sub> &#8722;
T<sub>water</sub></code>, because the water imposes its temperature on the air layer
touching it.</p>
<ul>
  <li><strong>Air warmer than water</strong> &#8212; the gradient inverts, refraction
  grows: mirages, ducts. <strong>To be avoided.</strong></li>
  <li><strong>Air colder than water</strong> &#8212; small, stable refraction, maximal
  hiding. This is the good regime.</li>
  <li><strong>Within 2&#8239;&#176;C</strong> &#8212; neutral layer, ordinary refraction,
  uniform along the whole path. This is the ideal.</li>
</ul>
<div class="box key">
  <span class="lab">The trap of the beautiful image</span>
  <p>An inversion stratifies the air and extinguishes turbulence: the image becomes
  sharp, calm, magnificent. That is exactly the regime where refraction is largest and
  least reliable. Water warmer than air makes the image boil, but refraction there is
  small and regular. <strong>The finest photographs are the ones to trust
  least.</strong></p>
</div>
<ul>
  <li><strong>Overcast</strong> rather than bright sun.</li>
  <li><strong>Moderate wind</strong>, 3 to 6&#8239;m/s. Dead calm lets stratification
  settle in; strong wind prevents reading the water line.</li>
  <li><strong>Not within two hours</strong> of sunrise or sunset: the gradient reverses
  there.</li>
  <li><strong>Autumn rather than spring</strong> on a temperate sea: in spring, mild air
  over still-wintry water is the ducting season.</li>
  <li><strong>No river mouth or current front</strong> on the path.</li>
  <li><strong>If the target's edge visibly undulates</strong> in the telephoto,
  wait.</li>
</ul>

<h2><span class="n">5</span>What voids the measurement</h2>
<ul>
  <li>Emerged land on the path.</li>
  <li>An edge so gradual that no height can be assigned to it: that is haze, not
  occultation.</li>
  <li>A single eye height.</li>
  <li>Focus or focal length changed mid-series.</li>
</ul>

<h2 class="brk"><span class="n">6</span>What a 6&#8239;371 km surface would require</h2>
<p>Hidden portion in metres, at the ordinary refraction coefficient
<code>k</code>&#8239;=&#8239;0.13. <strong>These values are an order of magnitude for
choosing the site, not a prediction to be recovered</strong>: at {nb(D_REF, 0, fr)}&#8239;km
and {nb(H_REF, 0, fr)}&#8239;m eye height, the same formula gives
{nb(cachee(H_REF, D_REF, 0.0), 0, fr)}&#8239;m with no refraction and
{nb(cachee(H_REF, D_REF, K_MAX), 0, fr)}&#8239;m under strong inversion.</p>
<table>
  <caption>Choose a combination giving at least ten metres or so.</caption>
  <thead><tr><th class="n">eye height</th>{"".join('<th class="n">%d km</th>' % d for d in GRILLE_D)}</tr></thead>
  <tbody>
{grille(fr)}
  </tbody>
</table>

<h2><span class="n">7</span>Record &#8212; to be filled in</h2>
<table>
  <caption>One row per eye height, three at minimum, same distance and same hour.</caption>
  <thead><tr><th class="n">UTC time</th><th class="n">eye height</th><th class="n">water level</th><th class="n">lowest visible marker</th><th class="n">T air / T water</th></tr></thead>
  <tbody>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
  </tbody>
</table>
<p>Station&#8722;target distance: &#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8239;km
&#160;&#160;&#183;&#160;&#160; Target and source of its markers:
&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;
&#160;&#160;&#183;&#160;&#160; Focal length: &#8230;&#8230;&#8239;mm</p>

<div class="box key">
  <span class="lab">The one thing to understand before leaving</span>
  <p>Do not try to recover a figure. <strong>Record what you see</strong>, from three eye
  heights, and let the calculation say which refraction coefficient accounts for it.</p>
  <p>What decides is not the value measured at one height, it is the
  <strong>difference between heights</strong>. A 6&#8239;371&#8239;km surface requires it
  non-zero &#8212; {nb(ecart, 0, fr)}&#8239;m between 1 and 20&#8239;m of eye height at
  {nb(D_REF, 0, fr)}&#8239;km. A plane surface with a clear profile requires it zero,
  exactly, with no adjustable parameter.</p>
</div>"""


def main():
    ecart = controle()
    modele = open(GABARIT, encoding="utf-8").read()
    i = modele.find('<div class="page">')
    entete = re.sub(r"<title>[^<]*</title>",
                    "<title>Fiche de terrain &#8212; portion masqu&#233;e</title>",
                    modele[:i], count=1)
    open(CIBLE, "w", encoding="utf-8").write(
        entete + '<div class="page">\n'
        '<div class="langbar"><span class="on">FRAN&#199;AIS</span>'
        '<span>ENGLISH &#8212; seconde moiti&#233;</span></div>\n\n'
        + corps(True) +
        '\n\n<div class="langbar"><span>FRAN&#199;AIS &#8212; first half</span>'
        '<span class="on">ENGLISH</span></div>\n\n'
        + corps(False) + '\n</div>\n')
    print("Fiche de terrain écrite : content/protocoles/fiche-terrain-masquage.html")
    print("  masquage à %.0f km / %.0f m d'œil : %.0f m (k=0) · %.0f m (k=0,13) · "
          "%.0f m (k=0,50)"
          % (D_REF, H_REF, cachee(H_REF, D_REF, 0.0),
             cachee(H_REF, D_REF, K_REF), cachee(H_REF, D_REF, K_MAX)))
    print("  écart différentiel 1 m → 20 m : %.0f m (plan : 0)" % ecart)
    return 0


if __name__ == "__main__":
    sys.exit(main())
