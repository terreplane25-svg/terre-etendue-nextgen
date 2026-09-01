#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Protocole court : une observation est-elle compatible avec R = 6 371 km ?

Cadre fixé par l'auteur du site, et suivi à la lettre
─────────────────────────────────────────────────────
  1. Question fermée : compatibilité d'une observation avec R = 6 371 km.
     Le document ne parle donc d'aucun autre modèle — ni pour, ni contre.
  2. Exécutable par un amateur : appareil photo, téléobjectif, trépied, carte.
  3. Pas de site imposé ; un cas standard chiffré sert d'exemple.
  4. Résultat = photos calibrées + tableau de la hauteur masquée mesurée.
  5. Réfraction traitée par le seuil de basculement : on calcule le masquage
     minimal à k = 0,50, l'inversion la plus forte admissible. En dessous de
     cette valeur, aucune météo ne peut être invoquée.
  6. Trois pages.

Le choix de calculer à k = 0,50 change la nature de la conclusion
────────────────────────────────────────────────────────────────
On ne compare plus une mesure à une prédiction « standard » qui dépend d'un
coefficient supposé. On la compare à une **borne** : la sphère impose que
*au moins* c_min soit masqué, quelle que soit l'atmosphère. Voir moins que
c_min n'est plus un désaccord discutable, c'est une incompatibilité.

Un point que le cadre initial ne prévoyait pas, et qu'il faut signaler
─────────────────────────────────────────────────────────────────────
Le cadre proposait « 15 à 20 km ». À 15 km depuis 2 m de hauteur d'œil, c_min
ne vaut que 2,4 m — quatre fois seulement l'incertitude de lecture à 300 mm.
À 20 km il vaut 6,5 m, soit huit fois ; à 25 km, 12,5 m, soit douze fois. Le
seuil pratique est donc **20 km**, et la campagne gagne beaucoup à viser 25
ou 30. La grille de la section 5 le montre, et la section 3 l'exige.
"""
import math
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTOCOLES = os.path.join(RACINE, "content", "protocoles")
CIBLE = os.path.join(PROTOCOLES, "masquage-court.html")
GABARIT = os.path.join(PROTOCOLES, "visee-terrestre-bilingue.html")

R = 6371.0
K_MAX = 0.50               # inversion la plus forte admissible
K_ORD = 0.13               # coefficient ordinaire, donné pour comparaison
D_MINI = 20                # km — seuil imposé par la marge décisive
HAUTEURS = [1, 2, 3, 5, 10, 20, 50]
DISTANCES = [10, 15, 20, 25, 30, 40]
FOCALE, PIXELS, CAPTEUR = 300, 4000, 24.0
LECTURE_PX = 2             # incertitude de pointé du bord, en pixels


def cachee(h_m, d_km, k):
    """Portion masquée à la base de la cible, en mètres."""
    Rp = R / (1 - k)
    h = h_m / 1000.0
    a = math.sqrt((Rp + h) ** 2 - Rp ** 2)
    return 0.0 if d_km <= a else (math.sqrt(Rp ** 2 + (d_km - a) ** 2) - Rp) * 1000.0


def horizon(h_m, k):
    Rp = R / (1 - k)
    return math.sqrt((Rp + h_m / 1000.0) ** 2 - Rp ** 2)


def echelle(d_km, focale=FOCALE):
    """Mètres par pixel sur la cible, capteur plein format en cadrage vertical."""
    champ = 2 * math.atan(CAPTEUR / (2 * focale))
    return d_km * 1000.0 * champ / PIXELS


def controle():
    """Chaque valeur imprimée est recalculée ici."""
    assert abs(cachee(2, 15, K_MAX) - 2.4) < 0.15
    assert abs(cachee(2, 20, K_MAX) - 6.5) < 0.15
    assert abs(cachee(2, 25, K_MAX) - 12.5) < 0.2
    assert abs(cachee(2, 30, K_MAX) - 20.5) < 0.3
    assert abs(cachee(2, 20, K_ORD) - 14.5) < 0.3
    assert abs(horizon(2, K_MAX) - 7.1) < 0.1
    assert abs(horizon(2, K_ORD) - 5.4) < 0.1
    assert abs(echelle(20) - 0.40) < 0.01
    # La marge décisive au seuil imposé.
    marge = cachee(2, D_MINI, K_MAX) / (LECTURE_PX * echelle(D_MINI))
    assert marge > 8.0, marge
    return marge


def nb(x, n):
    return ("%.*f" % (n, x)).replace(".", ",")


def t_cmin():
    lignes = []
    for h in HAUTEURS:
        cells = "".join('<td class="n">%s</td>'
                        % ("&#8212;" if cachee(h, d, K_MAX) < 0.05
                           else nb(cachee(h, d, K_MAX), 1))
                        for d in DISTANCES)
        vedette = h == 2
        lib = "<strong>%d m</strong>" % h if vedette else "%d m" % h
        lignes.append('    <tr%s><td class="n">%s</td>%s</tr>'
                      % (' class="hi"' if vedette else "", lib, cells))
    return "\n".join(lignes)


def t_marges():
    cas = [(2, 15), (2, 20), (2, 25), (2, 30), (1, 30), (5, 30)]
    lignes = []
    for h, d in cas:
        cm = cachee(h, d, K_MAX)
        inc = LECTURE_PX * echelle(d)
        lignes.append('    <tr%s><td class="n">%d m</td><td class="n">%d km</td>'
                      '<td class="n">%s m</td><td class="n">&#177;&#8239;%s m</td>'
                      '<td class="n">%s&#215;</td></tr>'
                      % (' class="hi"' if (h, d) == (2, 20) else "",
                         h, d, nb(cm, 1), nb(inc, 1), nb(cm / inc, 0)))
    return "\n".join(lignes)


def corps():
    marge = cachee(2, D_MINI, K_MAX) / (LECTURE_PX * echelle(D_MINI))
    return f"""<div class="masthead">
  <div class="kicker">Protocole de terrain &#183; Trois pages &#183; Ex&#233;cutable en amateur</div>
  <h1>Une observation lointaine est-elle compatible avec une Terre de 6&#8239;371&#8239;km&#8239;?</h1>
  <p class="sub">Mesure de la portion masqu&#233;e d'une cible, au-dessus d'un plan d'eau</p>
</div>

<h2><span class="n">1</span>Le principe, en trois phrases</h2>
<p class="lead">Sur une surface de rayon 6&#8239;371&#8239;km, une cible situ&#233;e au-del&#224;
de l'horizon a sa base masqu&#233;e d'une hauteur qui ne d&#233;pend que de la hauteur
d'&#339;il, de la distance, et de la r&#233;fraction.</p>
<p>La r&#233;fraction rel&#232;ve le rayon lumineux et <strong>r&#233;duit</strong> ce
masquage. Elle ne l'annule pas&#160;: pass&#233;e une certaine distance, m&#234;me
l'inversion thermique la plus forte qu'on mesure dans l'atmosph&#232;re laisse une
portion cach&#233;e.</p>
<p>On calcule donc le <strong>masquage minimal</strong> <code>c<sub>min</sub></code>,
c'est-&#224;-dire celui qui subsiste au coefficient de r&#233;fraction extr&#234;me
<code>k</code>&#8239;=&#8239;0,50. Puis on mesure ce qui est r&#233;ellement
cach&#233;.</p>
<div class="box key">
  <span class="lab">Le crit&#232;re, et pourquoi il ferme le d&#233;bat</span>
  <p>Si la portion mesur&#233;e est <strong>inf&#233;rieure &#224;
  <code>c<sub>min</sub></code></strong>, l'observation n'est pas compatible avec une
  surface de rayon 6&#8239;371&#8239;km.</p>
  <p>Et la r&#233;fraction ne peut pas &#234;tre invoqu&#233;e pour l'expliquer,
  <strong>puisque <code>c<sub>min</sub></code> est d&#233;j&#224; calcul&#233; &#224; sa
  valeur extr&#234;me</strong>. C'est tout l'int&#233;r&#234;t de proc&#233;der ainsi
  plut&#244;t que de comparer &#224; une valeur &#171;&#160;standard&#160;&#187; qui
  d&#233;pendrait d'un coefficient suppos&#233;.</p>
</div>

<h2><span class="n">2</span>Mat&#233;riel</h2>
<ul>
  <li><strong>Appareil photo</strong> et t&#233;l&#233;objectif de {FOCALE}&#8239;mm ou
  plus en &#233;quivalent plein format. Tr&#233;pied. Enregistrement en format brut,
  sans recadrage.</li>
  <li><strong>Une cible portant des rep&#232;res de hauteur connus</strong> &#8212;
  phare &#224; bandes, immeuble &#224; &#233;tages, pyl&#244;ne &#224; traverses,
  ch&#226;teau d'eau. <strong>Sans rep&#232;res, on ne peut rien mesurer</strong>&#160;:
  ils donnent l'&#233;chelle de l'image.</li>
  <li><strong>Un m&#232;tre</strong> pour la hauteur d'&#339;il au-dessus de l'eau.</li>
  <li><strong>Une carte en ligne ou un GPS</strong> pour la distance, au dixi&#232;me de
  kilom&#232;tre.</li>
</ul>
<p>Rien d'autre. Pas de th&#233;odolite, pas de laboratoire.</p>

<h2><span class="n">3</span>Le site &#8212; quatre conditions</h2>
<div class="box warn">
  <span class="lab">Sans elles, la mesure ne vaut rien</span>
  <p><strong>1. La vis&#233;e passe enti&#232;rement au-dessus de l'eau.</strong> Une
  colline &#224; mi-parcours masque une base quelle que soit la forme du sol. C'est ce
  qui invalide le plus de relev&#233;s.</p>
  <p><strong>2. La base de la cible est &#224; la ligne d'eau</strong>, sur le
  m&#234;me plan d'eau que vous.</p>
  <p><strong>3. Distance d'au moins {D_MINI}&#8239;km.</strong> En dessous, le masquage
  minimal devient trop petit devant la pr&#233;cision de lecture (section 5).</p>
  <p><strong>4. Hauteur d'&#339;il faible</strong>, deux ou trois m&#232;tres. C'est ce
  qui rend le masquage grand&#160;: l'horizon recule comme la racine de la
  hauteur.</p>
</div>
<p>Un grand lac ou une baie conviennent. Relever la mar&#233;e si le site est
maritime&#160;: elle d&#233;place &#224; la fois votre hauteur d'&#339;il et la base de
la cible.</p>

<h2><span class="n">4</span>La prise de vue</h2>
<ol>
  <li>Mesurer la <strong>hauteur d'&#339;il au-dessus de l'eau</strong> et la noter.</li>
  <li>Photographier la cible, <strong>plusieurs vues</strong>, sans recadrage ni
  redressement, mise au point verrouill&#233;e.</li>
  <li>Photographier ensuite la <strong>sc&#232;ne au grand angle</strong> avec des
  rep&#232;res proches, pour qu'un tiers puisse retrouver la station.</li>
  <li>Noter <strong>l'heure</strong>, la temp&#233;rature de l'air et, si possible, celle
  de l'eau.</li>
  <li><strong>Recommencer depuis une hauteur d'&#339;il nettement diff&#233;rente</strong>
  &#8212; une digue, un balcon, un pont &#8212; sans changer d'objectif. La base
  masqu&#233;e doit alors remonter d'une quantit&#233; que la grille donne. C'est le
  contr&#244;le le plus simple qui distingue une occultation d'un banc de brume.</li>
</ol>
<div class="box">
  <span class="lab">Un signe qui ne trompe pas</span>
  <p>Une occultation coupe <strong>net</strong>, &#224; une hauteur pr&#233;cise, et
  <strong>change beaucoup</strong> quand on monte de quelques m&#232;tres. La brume
  s'efface progressivement et ne bouge presque pas avec la hauteur d'&#339;il.</p>
</div>

<h2><span class="n">5</span>La grille &#8212; masquage minimal
<code>c<sub>min</sub></code></h2>
<p class="lead">Portion que la sph&#232;re impose de masquer <strong>au minimum</strong>,
en m&#232;tres, calcul&#233;e au coefficient extr&#234;me <code>k</code>&#8239;=&#8239;0,50.
Aucune atmosph&#232;re mesur&#233;e ne descend en dessous de ces valeurs.</p>
<table>
  <caption>Tableau 1 &#8212; <code>c<sub>min</sub></code>, masquage minimal en
  m&#232;tres. Un tiret signifie que la cible est en de&#231;&#224; de l'horizon&#160;:
  aucune conclusion possible.</caption>
  <thead><tr><th class="n">hauteur d'&#339;il</th>{"".join('<th class="n">%d km</th>' % d for d in DISTANCES)}</tr></thead>
  <tbody>
{t_cmin()}
  </tbody>
</table>
<p>&#192; titre de comparaison, en conditions ordinaires
(<code>k</code>&#8239;=&#8239;0,13) le masquage &#224; {D_MINI}&#8239;km depuis
2&#8239;m vaut {nb(cachee(2, D_MINI, K_ORD), 1)}&#8239;m au lieu de
{nb(cachee(2, D_MINI, K_MAX), 1)}&#8239;m. <strong>C'est la valeur basse qu'on
retient</strong>, parce qu'elle ne pr&#234;te &#224; aucune discussion m&#233;t&#233;o.</p>
<table>
  <caption>Tableau 2 &#8212; Pourquoi {D_MINI}&#8239;km au minimum. L'incertitude est
  celle d'un pointé du bord &#224; &#177;&#8239;{LECTURE_PX}&#8239;pixels &#224;
  {FOCALE}&#8239;mm sur un capteur de {PIXELS}&#8239;pixels.</caption>
  <thead><tr><th class="n">h</th><th class="n">d</th><th class="n">c<sub>min</sub></th><th class="n">incertitude</th><th class="n">marge</th></tr></thead>
  <tbody>
{t_marges()}
  </tbody>
</table>

<h2><span class="n">6</span>La mesure, sur l'image</h2>
<p>L'&#233;chelle se lit sur la cible elle-m&#234;me, sans conna&#238;tre la focale.</p>
<ol>
  <li>Rep&#233;rer deux rep&#232;res de hauteurs connues <code>z&#8321;</code> et
  <code>z&#8322;</code>, mesurer leur &#233;cart en pixels
  <code>&#916;px</code>.</li>
  <li>L'&#233;chelle vaut <code>(z&#8322; &#8722; z&#8321;) / &#916;px</code>, en
  m&#232;tres par pixel.</li>
  <li>Mesurer en pixels la distance entre le rep&#232;re le plus bas visible et le bord
  inf&#233;rieur de la cible tel qu'il appara&#238;t, puis convertir.</li>
  <li>La portion masqu&#233;e mesur&#233;e <code>c<sub>obs</sub></code> est la hauteur,
  compt&#233;e depuis la base r&#233;elle de la cible, du plus bas point encore visible.
  Si la base au ras de l'eau se voit, <code>c<sub>obs</sub></code>&#8239;=&#8239;0.</li>
</ol>
<p>&#192; {D_MINI}&#8239;km et {FOCALE}&#8239;mm, un pixel vaut
{nb(echelle(D_MINI), 2)}&#8239;m&#160;; l'incertitude de pointé est donc de l'ordre de
&#177;&#8239;{nb(LECTURE_PX * echelle(D_MINI), 1)}&#8239;m.</p>

<h2><span class="n">7</span>Conclusion &#8212; les trois issues</h2>
<div class="two">
  <div class="vc p">
    <p class="h">c<sub>obs</sub> &lt; c<sub>min</sub> &#8722; 3&#963;</p>
    <p class="v">Incompatible avec R = 6&#8239;371&#8239;km</p>
    <p>On voit plus bas que ce que la sph&#232;re autorise sous n'importe quelle
    r&#233;fraction. La m&#233;t&#233;o ne peut pas &#234;tre invoqu&#233;e.</p>
  </div>
  <div class="vc g">
    <p class="h">c<sub>obs</sub> &#8805; c<sub>min</sub></p>
    <p class="v">Compatible</p>
    <p>L'observation entre dans ce que la sph&#232;re autorise. La valeur de
    <code>c<sub>obs</sub></code> donne alors le coefficient de r&#233;fraction du
    moment.</p>
  </div>
</div>
<p><code>3&#963;</code> vaut trois fois l'incertitude de lecture de la section 6, soit
environ {nb(3 * LECTURE_PX * echelle(D_MINI), 1)}&#8239;m &#224; {D_MINI}&#8239;km. La
troisi&#232;me issue est le rejet&#160;: si le profil n'est pas d&#233;gag&#233;, si le
bord est trop diffus pour qu'on lui assigne une hauteur, ou si la cible est en
de&#231;&#224; de l'horizon, la mesure ne conclut rien et doit &#234;tre refaite.</p>

<h2 class="brk"><span class="n">8</span>Fiche de relev&#233;</h2>
<p>Station&#160;: &#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;
&#160;&#160;&#183;&#160;&#160; Date&#160;: &#8230;&#8230;&#8230;&#8230;&#8230;&#8230;
&#160;&#160;&#183;&#160;&#160; Focale&#160;: &#8230;&#8230;&#8239;mm<br/>
Cible&#160;: &#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;
&#160;&#160;&#183;&#160;&#160; Hauteur totale&#160;: &#8230;&#8230;&#8239;m
&#160;&#160;&#183;&#160;&#160; Source des rep&#232;res&#160;:
&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;<br/>
Distance mesur&#233;e&#160;: &#8230;&#8230;&#8239;km
&#160;&#160;&#183;&#160;&#160; Profil d&#233;gag&#233; v&#233;rifi&#233; sur&#160;:
&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;
&#160;&#160;&#183;&#160;&#160; Mar&#233;e&#160;: &#8230;&#8230;&#8239;m</p>
<table>
  <caption>Une ligne par hauteur d'&#339;il. Deux au minimum (&#233;tape 4.5).</caption>
  <thead><tr><th class="n">heure</th><th class="n">hauteur d'&#339;il</th><th class="n">&#233;chelle (m/px)</th><th class="n">c<sub>obs</sub> mesur&#233;</th><th class="n">c<sub>min</sub> (tableau 1)</th><th class="n">T air / T eau</th></tr></thead>
  <tbody>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
  </tbody>
</table>
<p><strong>Conclusion</strong> (section 7)&#160;:
&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;<br/>
<strong>Observations</strong> &#8212; &#233;tat de l'eau, nettet&#233; du bord, couverture
nuageuse&#160;:<br/>
&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;</p>
<p style="margin-top:14pt"><em>Les photographies brutes, non recadr&#233;es, font partie
du relev&#233;. Une conclusion sans elles n'est pas v&#233;rifiable.</em></p>"""


def main():
    marge = controle()
    modele = open(GABARIT, encoding="utf-8").read()
    i = modele.find('<div class="page">')
    entete = re.sub(r"<title>[^<]*</title>",
                    "<title>Compatibilit&#233; d'une observation avec "
                    "R = 6 371 km</title>", modele[:i], count=1)
    open(CIBLE, "w", encoding="utf-8").write(
        entete + '<div class="page">\n' + corps() + '\n</div>\n')
    print("Protocole court écrit : content/protocoles/masquage-court.html")
    print("  c_min à 20 km depuis 2 m : %.1f m  (ordinaire : %.1f m)"
          % (cachee(2, 20, K_MAX), cachee(2, 20, K_ORD)))
    print("  marge décisive au seuil de %d km : %.0f×" % (D_MINI, marge))
    print("  horizon à 2 m : %.1f km (k=0,50) · %.1f km (k=0,13)"
          % (horizon(2, K_MAX), horizon(2, K_ORD)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
