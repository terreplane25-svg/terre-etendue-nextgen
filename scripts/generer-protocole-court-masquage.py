#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Protocole de terrain : une observation est-elle compatible avec R = 6 371 km ?

Cadre fixé par l'auteur du site
───────────────────────────────
  1. Question fermée : compatibilité d'une observation avec R = 6 371 km.
     Le document ne parle donc d'aucun autre modèle — ni pour, ni contre.
  2. Exécutable en amateur, avec le matériel réellement disponible.
  3. Distance recommandée portée à 40–50 km à sa demande.
  4. Résultat = photos calibrées + tableau de la hauteur masquée mesurée.
  5. Réfraction traitée par le seuil de basculement : le masquage minimal est
     calculé à k = 0,50, l'inversion la plus forte admissible. En dessous de
     cette valeur, aucune météo ne peut être invoquée.

Pourquoi 40–50 km change la nature du résultat
──────────────────────────────────────────────
À 20 km, voir la base d'une cible exigerait k = 0,94 ; à 40 km, k = 0,98 ; à
50 km, k = 0,99. Un conduit atmosphérique — mirage supérieur — correspond à
k = 1. Autrement dit : **à 40–50 km, voir la base sort de ce que peut produire
n'importe quel régime atmosphérique**, conduit compris. Le débat sur la météo
se ferme entièrement.

La contrepartie est la hauteur de cible. À 40 km, une surface de 6 371 km masque
82 m en conditions ordinaires ; à 50 km, 136 m. La cible doit donc dépasser
120 m à 40 km, 200 m à 50 km — ce qui désigne les éoliennes, les cheminées, les
pylônes de pont et les tours, plutôt que les phares.

Ce que le matériel doit réellement faire
────────────────────────────────────────
Le calcul dit une chose contre-intuitive : **l'appareil n'est pas le facteur
limitant**. Il faut environ 600 mm équivalent 24×36 pour que la cible couvre
deux cents pixels. Un P900 à 2 000 mm donne 0,72″/pixel, un P1000 à 3 000 mm
donne 0,48″/pixel — or la diffraction du P1000 vaut déjà 2,1″ et la turbulence
horizontale sur 40 km en vaut 5 à 20. La résolution supplémentaire du P1000 est
détruite par l'atmosphère avant d'atteindre le capteur.

Ce qui décide du succès n'est donc pas la focale mais, dans l'ordre : la
transparence de l'air, la stabilité du montage, et la sélection d'images par
lucky imaging.
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
K_ORD = 0.13               # coefficient ordinaire, pour comparaison
D_MINI = 20                # km — plancher absolu
D_RECO = 40                # km — distance recommandée
HAUTEURS = [1, 2, 3, 5, 10, 20]
DISTANCES = [20, 30, 40, 50, 60]
PIXELS_V = 3456            # capteur 1/2,3" des bridges, 16 Mpx
FOCALE_MINI = 600          # mm équivalent 24×36
PX_CIBLE = 200             # pixels souhaités sur la cible
APPAREILS = [("600 mm &#233;q. &#8212; minimum", 600),
             ("Nikon P900 / P950 &#8212; 2 000 mm", 2000),
             ("Nikon P1000 &#8212; 3 000 mm", 3000)]
SEEINGS = [5, 10, 20]      # turbulence horizontale, secondes d'arc


def cachee(h_m, d_km, k):
    """Portion masquée à la base de la cible, en mètres."""
    Rp = R / (1 - k)
    h = h_m / 1000.0
    a = math.sqrt((Rp + h) ** 2 - Rp ** 2)
    return 0.0 if d_km <= a else (math.sqrt(Rp ** 2 + (d_km - a) ** 2) - Rp) * 1000.0


def k_pour_voir_base(h_m, d_km):
    lo, hi = 0.0, 0.99999
    for _ in range(400):
        m = (lo + hi) / 2
        if cachee(h_m, d_km, m) > 0:
            lo = m
        else:
            hi = m
    return hi


def par_pixel(focale_eq):
    """Secondes d'arc par pixel, pour une focale équivalente 24×36."""
    return math.degrees(2 * math.atan(12.0 / focale_eq) / PIXELS_V) * 3600


def metres_par_pixel(focale_eq, d_km):
    return d_km * 1000.0 * math.radians(par_pixel(focale_eq) / 3600)


def controle():
    """Chaque valeur imprimée est recalculée ici."""
    assert abs(cachee(2, 20, K_MAX) - 6.5) < 0.2
    assert abs(cachee(2, 40, K_MAX) - 42) < 1
    assert abs(cachee(2, 50, K_MAX) - 72) < 1
    assert abs(cachee(2, 40, K_ORD) - 82) < 1
    assert abs(cachee(2, 50, K_ORD) - 136) < 1
    # Voir la base : k exigé au-delà de tout régime atmosphérique.
    assert abs(k_pour_voir_base(2, 40) - 0.984) < 0.002
    assert abs(k_pour_voir_base(2, 50) - 0.990) < 0.002
    assert k_pour_voir_base(2, 40) > K_MAX
    # Échelle des appareils.
    assert abs(par_pixel(2000) - 0.72) < 0.01
    assert abs(par_pixel(3000) - 0.48) < 0.01
    assert abs(par_pixel(600) - 2.39) < 0.02
    # La focale minimale pour PX_CIBLE pixels sur une cible de 100 m à 40 km.
    assert 100 / metres_par_pixel(FOCALE_MINI, 40) > PX_CIBLE
    # La marge décisive à la distance recommandée, turbulence défavorable.
    inc = 40 * 1000 * 20 / 206265.0
    marge = cachee(2, D_RECO, K_MAX) / inc
    assert marge > 10, marge
    return marge


def nb(x, n):
    return ("%.*f" % (n, x)).replace(".", ",")


def t_cmin():
    lignes = []
    for h in HAUTEURS:
        cells = "".join('<td class="n">%s</td>'
                        % ("&#8212;" if cachee(h, d, K_MAX) < 0.05
                           else nb(cachee(h, d, K_MAX), 0))
                        for d in DISTANCES)
        vedette = h == 2
        lib = "<strong>%d m</strong>" % h if vedette else "%d m" % h
        lignes.append('    <tr%s><td class="n">%s</td>%s</tr>'
                      % (' class="hi"' if vedette else "", lib, cells))
    return "\n".join(lignes)


def t_impossible():
    lignes = []
    for d in DISTANCES:
        k = k_pour_voir_base(2, d)
        lignes.append('    <tr%s><td class="n">%d km</td><td class="n">%s</td>'
                      '<td class="n">%s</td></tr>'
                      % (' class="hi"' if d in (40, 50) else "", d, nb(k, 3),
                         "hors d'atteinte" if k > 0.97 else
                         "au-del&#224; de l'inversion forte" if k > K_MAX
                         else "possible sous inversion"))
    return "\n".join(lignes)


def t_cible():
    lignes = []
    for d in (30, 40, 50):
        ord_, mini = cachee(2, d, K_ORD), cachee(2, d, K_MAX)
        lignes.append('    <tr%s><td class="n">%d km</td><td class="n">%s m</td>'
                      '<td class="n">%s m</td><td class="n">%d m</td></tr>'
                      % (' class="hi"' if d == 40 else "", d, nb(mini, 0),
                         nb(ord_, 0), int(ord_ * 1.5)))
    return "\n".join(lignes)


def t_appareils():
    lignes = []
    for nom, feq in APPAREILS:
        cells = "".join('<td class="n">%d px</td>'
                        % int(H / metres_par_pixel(feq, d))
                        for d, H in ((40, 100), (50, 150)))
        lignes.append('    <tr%s><td>%s</td><td class="n">%s&#8243;</td>%s</tr>'
                      % (' class="hi"' if feq == 2000 else "", nom,
                         nb(par_pixel(feq), 2), cells))
    return "\n".join(lignes)


def t_seeing():
    lignes = []
    for s in SEEINGS:
        cells = []
        for d in (40, 50):
            inc = d * 1000 * s / 206265.0
            cells.append('<td class="n">&#177;&#8239;%s m</td>' % nb(inc, 1))
            cells.append('<td class="n">%s&#215;</td>'
                         % nb(cachee(2, d, K_MAX) / inc, 0))
        lignes.append('    <tr%s><td class="n">%d&#8243;</td>%s</tr>'
                      % (' class="hi"' if s == 10 else "", s, "".join(cells)))
    return "\n".join(lignes)


def corps():
    marge = controle()
    return f"""<div class="masthead">
  <div class="kicker">Protocole de terrain &#183; Ex&#233;cutable en amateur &#183; Distance recommand&#233;e {D_RECO}&#8211;50&#8239;km</div>
  <h1>Une observation lointaine est-elle compatible avec une Terre de 6&#8239;371&#8239;km&#8239;?</h1>
  <p class="sub">Mesure de la portion masqu&#233;e d'une cible, au-dessus d'un plan d'eau</p>
</div>

<h2><span class="n">1</span>Le principe</h2>
<p class="lead">Sur une surface de rayon 6&#8239;371&#8239;km, une cible situ&#233;e au-del&#224;
de l'horizon a sa base masqu&#233;e d'une hauteur qui ne d&#233;pend que de la hauteur
d'&#339;il, de la distance, et de la r&#233;fraction.</p>
<p>La r&#233;fraction rel&#232;ve le rayon lumineux et <strong>r&#233;duit</strong> ce
masquage. Elle ne l'annule pas. On calcule donc le <strong>masquage
minimal</strong> <code>c<sub>min</sub></code>, celui qui subsiste au coefficient
extr&#234;me <code>k</code>&#8239;=&#8239;0,50, puis on mesure ce qui est
r&#233;ellement cach&#233;.</p>
<div class="box key">
  <span class="lab">Le crit&#232;re</span>
  <p>Si la portion mesur&#233;e est <strong>inf&#233;rieure &#224;
  <code>c<sub>min</sub></code></strong>, l'observation n'est pas compatible avec une
  surface de rayon 6&#8239;371&#8239;km &#8212; et la m&#233;t&#233;o ne peut pas
  &#234;tre invoqu&#233;e, <strong>puisque <code>c<sub>min</sub></code> est
  d&#233;j&#224; calcul&#233; &#224; sa valeur extr&#234;me</strong>.</p>
</div>

<h2><span class="n">2</span>Pourquoi viser {D_RECO}&#8211;50&#8239;km</h2>
<p class="lead">Plus la vis&#233;e est longue, plus le r&#233;sultat devient
inattaquable &#8212; et &#224; partir de 40&#8239;km il sort de ce que peut produire
n'importe quel r&#233;gime atmosph&#233;rique.</p>
<table>
  <caption>Tableau 1 &#8212; Coefficient de r&#233;fraction qu'il faudrait pour que la
  base de la cible redevienne visible, depuis 2&#8239;m de hauteur d'&#339;il. Rappel
  des ordres de grandeur&#160;: 0,13 en atmosph&#232;re ordinaire, 0,50 sous inversion
  la plus forte mesur&#233;e, 1,00 en conduit &#8212; le mirage sup&#233;rieur.</caption>
  <thead><tr><th class="n">distance</th><th class="n">k n&#233;cessaire</th><th class="n">r&#233;gime correspondant</th></tr></thead>
  <tbody>
{t_impossible()}
  </tbody>
</table>
<p>&#192; 20&#8239;km, un contradicteur peut encore parler d'inversion exceptionnelle.
&#192; {D_RECO}&#8211;50&#8239;km, <strong>il faudrait un r&#233;gime qui n'existe
pas</strong>&#160;: voir la base y demande davantage qu'un conduit.</p>
<table>
  <caption>Tableau 2 &#8212; Masquage minimal <code>c<sub>min</sub></code>, en
  m&#232;tres, au coefficient extr&#234;me <code>k</code>&#8239;=&#8239;0,50. Un tiret
  signifie que la cible est en de&#231;&#224; de l'horizon.</caption>
  <thead><tr><th class="n">hauteur d'&#339;il</th>{"".join('<th class="n">%d km</th>' % d for d in DISTANCES)}</tr></thead>
  <tbody>
{t_cmin()}
  </tbody>
</table>

<h2><span class="n">3</span>La contrepartie&#160;: la cible doit &#234;tre haute</h2>
<p class="lead">C'est la seule vraie difficult&#233; des longues vis&#233;es, et elle
d&#233;cide du choix du site.</p>
<p>&#192; 40&#8239;km, une surface de 6&#8239;371&#8239;km masque
{nb(cachee(2, 40, K_ORD), 0)}&#8239;m en conditions ordinaires. Une cible de
80&#8239;m serait donc <em>enti&#232;rement</em> invisible, et l'essai ne mesurerait
rien.</p>
<table>
  <caption>Tableau 3 &#8212; Hauteur de cible n&#233;cessaire, depuis 2&#8239;m de
  hauteur d'&#339;il.</caption>
  <thead><tr><th class="n">distance</th><th class="n">masqu&#233; au minimum</th><th class="n">masqu&#233; en conditions ordinaires</th><th class="n">cible d'au moins</th></tr></thead>
  <tbody>
{t_cible()}
  </tbody>
</table>
<div class="box warn">
  <span class="lab">Quelles cibles conviennent</span>
  <p><strong>&#201;oliennes</strong> &#8212; les meilleures. Un parc offshore est sur
  l'eau, le m&#226;t porte des rep&#232;res, le moyeu et le bout de pale donnent deux
  hauteurs publi&#233;es. Les machines actuelles font 150 &#224; 260&#8239;m en bout
  de pale.</p>
  <p><strong>Chemin&#233;es, tours de refroidissement, pyl&#244;nes de pont,
  gratte-ciel c&#244;tiers.</strong> Hauteurs publi&#233;es, structure &#224;
  &#233;tages ou &#224; sections.</p>
  <p><strong>Les phares ne conviennent plus</strong> au-del&#224; de 30&#8239;km&#160;:
  m&#234;me les plus hauts d'Europe plafonnent vers 80&#8239;m et seraient
  enti&#232;rement masqu&#233;s.</p>
</div>

<h2 class="brk"><span class="n">4</span>Le mat&#233;riel &#8212; strictement le
n&#233;cessaire</h2>
<p class="lead">Le calcul donne un r&#233;sultat contre-intuitif&#160;: l'appareil
n'est pas le facteur limitant.</p>
<p>Il faut que la cible couvre assez de pixels pour qu'on distingue ses rep&#232;res.
Deux cents pixels suffisent largement, ce qui demande environ
<strong>{FOCALE_MINI}&#8239;mm &#233;quivalent 24&#215;36</strong>.</p>
<table>
  <caption>Tableau 4 &#8212; &#201;chelle obtenue selon l'appareil, capteur de
  {mil_px()} pixels de haut.</caption>
  <thead><tr><th>appareil</th><th class="n">par pixel</th><th class="n">cible 100&#8239;m &#224; 40&#8239;km</th><th class="n">cible 150&#8239;m &#224; 50&#8239;km</th></tr></thead>
  <tbody>
{t_appareils()}
  </tbody>
</table>
<div class="box key">
  <span class="lab">Pourquoi le P1000 n'apporte rien de plus que le P900</span>
  <p>Le P1000 donne {nb(par_pixel(3000), 2)}&#8243; par pixel. Mais sa
  <strong>diffraction</strong> vaut d&#233;j&#224; 2,1&#8243; &#8212; sa pupille
  d'entr&#233;e ne mesure que 67&#8239;mm &#8212; et la <strong>turbulence
  horizontale</strong> sur 40&#8239;km en vaut 5 &#224; 20.</p>
  <p>La r&#233;solution suppl&#233;mentaire est d&#233;truite par l'atmosph&#232;re
  avant d'atteindre le capteur. <strong>Un P900 &#224; 2 000&#8239;mm est
  d&#233;j&#224; au-del&#224; du n&#233;cessaire</strong>, et un
  600&#8239;mm &#233;quivalent suffit &#224; la mesure.</p>
</div>
<p><strong>Le n&#233;cessaire, au minimum&#160;:</strong></p>
<ul>
  <li>Un appareil &#224; <strong>{FOCALE_MINI}&#8239;mm &#233;quivalent ou plus</strong>,
  capable d'enregistrer en brut et en vid&#233;o.</li>
  <li>Un <strong>tr&#233;pied lourd</strong>. &#192; 2 000&#8239;mm, un pixel vaut
  {nb(par_pixel(2000), 2)}&#8243;&#160;: la moindre vibration efface la mesure. C'est
  le poste o&#249; il ne faut pas &#233;conomiser.</li>
  <li><strong>D&#233;clenchement &#224; distance</strong> ou retardateur, et
  stabilisation optique <strong>d&#233;sactiv&#233;e</strong> sur tr&#233;pied.</li>
  <li>Un <strong>m&#232;tre</strong> pour la hauteur d'&#339;il au-dessus de l'eau.</li>
  <li>Une <strong>carte en ligne</strong> pour la distance, au dixi&#232;me de
  kilom&#232;tre.</li>
  <li>Un <strong>thermom&#232;tre</strong>, pour l'air et si possible pour l'eau.</li>
</ul>

<h2><span class="n">5</span>La mise en place qui fait r&#233;ussir</h2>
<p class="lead">&#192; {D_RECO}&#8211;50&#8239;km, l'&#233;chec vient rarement du
calcul. Il vient de trois choses, dans cet ordre.</p>

<h3>5.1 &#8212; La transparence de l'air, premi&#232;re cause d'&#233;chec</h3>
<p>La plupart des jours, on ne verra <strong>rien</strong> &#224; 40&#8239;km. Il
faut une visibilit&#233; m&#233;t&#233;orologique sup&#233;rieure &#224; la distance
vis&#233;e, ce qui est rare.</p>
<ul>
  <li>Guetter les <strong>masses d'air froid et sec apr&#232;s le passage d'un
  front</strong>&#160;: c'est l&#224; que la visibilit&#233; d&#233;passe
  50&#8239;km.</li>
  <li>Les <strong>bulletins a&#233;ronautiques</strong> (METAR de
  l'a&#233;rodrome le plus proche) donnent la visibilit&#233; en clair. En dessous de
  la distance vis&#233;e, ne pas se d&#233;placer.</li>
  <li>Automne et hiver valent mieux que l'&#233;t&#233;.</li>
  <li>Vent de secteur maritime, plut&#244;t que continental charg&#233; en
  a&#233;rosols.</li>
</ul>

<h3>5.2 &#8212; La stabilit&#233;, et le tri d'images</h3>
<p>&#192; ces focales, la turbulence fait <strong>bouillonner</strong> l'image
plusieurs fois par seconde. Une photo unique attrape un instant au hasard.</p>
<div class="box key">
  <span class="lab">La technique qui change tout&#160;: filmer, puis trier</span>
  <p>Enregistrer une <strong>vid&#233;o de trente secondes &#224; une minute</strong>
  plut&#244;t que des photos isol&#233;es. Extraire ensuite les images
  individuelles et <strong>ne garder que les plus nettes</strong> &#8212; une sur
  vingt, une sur cinquante.</p>
  <p>C'est la m&#233;thode employ&#233;e en imagerie plan&#233;taire. Elle transforme
  une bouillie en un bord franc, et c'est ce qui rend la lecture du 6.3 possible.</p>
</div>
<ul>
  <li>Tr&#233;pied lourd, colonne centrale <strong>rentr&#233;e</strong>, si possible
  lest&#233;.</li>
  <li>S'abriter du vent&#160;: un appareil &#224; 2 000&#8239;mm expos&#233; &#224;
  une brise est inutilisable.</li>
  <li>Vitesse d'obturation <strong>1/500&#8239;s ou plus courte</strong>.</li>
  <li>Mise au point manuelle sur la cible, puis <strong>verrouill&#233;e</strong> pour
  toute la s&#233;rie.</li>
  <li>Exposition <strong>manuelle et fixe</strong>. Une exposition automatique
  d&#233;placerait le seuil de d&#233;tection du bord d'une prise &#224; l'autre.</li>
</ul>
<table>
  <caption>Tableau 5 &#8212; Ce que la turbulence co&#251;te, et la marge qui reste.
  Depuis 2&#8239;m de hauteur d'&#339;il.</caption>
  <thead><tr><th class="n">turbulence</th><th class="n">incertitude &#224; 40&#8239;km</th><th class="n">marge</th><th class="n">incertitude &#224; 50&#8239;km</th><th class="n">marge</th></tr></thead>
  <tbody>
{t_seeing()}
  </tbody>
</table>
<p>M&#234;me dans le cas le plus d&#233;favorable, la marge reste sup&#233;rieure
&#224; dix. <strong>La turbulence g&#234;ne la lecture&#160;; elle ne menace pas la
conclusion.</strong></p>

<h3>5.3 &#8212; Le site, et ses quatre conditions</h3>
<div class="box warn">
  <span class="lab">Sans elles, la mesure ne vaut rien</span>
  <p><strong>1. La vis&#233;e passe enti&#232;rement au-dessus de l'eau.</strong> Une
  colline &#224; mi-parcours masque une base quelle que soit la forme du sol. C'est ce
  qui invalide le plus de relev&#233;s.</p>
  <p><strong>2. La base de la cible est &#224; la ligne d'eau</strong>, sur le
  m&#234;me plan d'eau que vous. Une &#233;olienne offshore satisfait cette condition
  par construction.</p>
  <p><strong>3. Hauteur d'&#339;il faible</strong>, un &#224; trois m&#232;tres.
  C'est ce qui rend le masquage grand.</p>
  <p><strong>4. Niveau d'eau relev&#233;</strong> aupr&#232;s du service
  mar&#233;graphique si le site est maritime&#160;: la mar&#233;e d&#233;place &#224;
  la fois votre hauteur d'&#339;il et la base de la cible.</p>
</div>
<p><strong>Rep&#233;rage pr&#233;alable, &#224; faire avant de se
d&#233;placer&#160;:</strong> relever les coordonn&#233;es de la station et de la
cible sur une carte, calculer la distance, v&#233;rifier au tableau 3 que la cible est
assez haute, et v&#233;rifier sur la carte qu'aucune terre n'est sur le trajet.</p>

<h2 class="brk"><span class="n">6</span>La prise de vue et la mesure</h2>
<ol>
  <li><strong>Mesurer la hauteur d'&#339;il</strong> au-dessus de l'eau et la noter,
  avec l'heure.</li>
  <li><strong>Filmer la cible</strong> trente &#224; soixante secondes au
  t&#233;l&#233;objectif, sans recadrage, r&#233;glages verrouill&#233;s (5.2). Puis
  quelques images fixes en brut.</li>
  <li><strong>Photographier la sc&#232;ne au grand angle</strong>, avec des
  rep&#232;res proches, pour qu'un tiers puisse retrouver la station.</li>
  <li><strong>Noter</strong> l'heure, la temp&#233;rature de l'air et, si possible,
  celle de l'eau, ainsi que le niveau mar&#233;graphique.</li>
  <li><strong>Recommencer depuis une hauteur d'&#339;il nettement
  diff&#233;rente</strong> &#8212; une digue, un balcon, un pont &#8212; sans changer
  de r&#233;glage. La base masqu&#233;e doit remonter d'une quantit&#233; que le
  tableau 2 donne. <strong>C'est le contr&#244;le le plus simple qui distingue une
  occultation d'un banc de brume.</strong></li>
</ol>
<div class="box">
  <span class="lab">Un signe qui ne trompe pas</span>
  <p>Une occultation coupe <strong>net</strong>, &#224; une hauteur pr&#233;cise, et
  <strong>change beaucoup</strong> quand on monte de quelques m&#232;tres. La brume
  s'efface progressivement et ne bouge presque pas avec la hauteur d'&#339;il.</p>
</div>
<h3>6.3 &#8212; La lecture, sur l'image</h3>
<p>L'&#233;chelle se lit sur la cible elle-m&#234;me, <strong>sans conna&#238;tre la
focale</strong>.</p>
<ol>
  <li>Rep&#233;rer deux rep&#232;res de hauteurs connues <code>z&#8321;</code> et
  <code>z&#8322;</code>, mesurer leur &#233;cart en pixels
  <code>&#916;px</code>.</li>
  <li>L'&#233;chelle vaut <code>(z&#8322; &#8722; z&#8321;) / &#916;px</code>, en
  m&#232;tres par pixel.</li>
  <li>Mesurer en pixels la distance entre le rep&#232;re le plus bas visible et le bord
  inf&#233;rieur apparent de la cible, puis convertir.</li>
  <li><code>c<sub>obs</sub></code> est la hauteur, compt&#233;e depuis la base
  r&#233;elle de la cible, du plus bas point encore visible.</li>
</ol>

<h2><span class="n">7</span>Conclusion &#8212; les trois issues</h2>
<div class="two">
  <div class="vc p">
    <p class="h">c<sub>obs</sub> &lt; c<sub>min</sub> &#8722; 3&#963;</p>
    <p class="v">Incompatible avec R = 6&#8239;371&#8239;km</p>
    <p>On voit plus bas que ce que la sph&#232;re autorise sous n'importe quelle
    r&#233;fraction.</p>
  </div>
  <div class="vc g">
    <p class="h">c<sub>obs</sub> &#8805; c<sub>min</sub></p>
    <p class="v">Compatible</p>
    <p>L'observation entre dans ce que la sph&#232;re autorise. La valeur de
    <code>c<sub>obs</sub></code> donne alors le coefficient de r&#233;fraction du
    moment.</p>
  </div>
</div>
<p><code>3&#963;</code> vaut trois fois l'incertitude du tableau 5 pour la turbulence
observ&#233;e. La troisi&#232;me issue est le <strong>rejet</strong>&#160;: si le
profil n'est pas d&#233;gag&#233;, si le bord est trop diffus pour qu'on lui assigne
une hauteur, ou si la cible est en de&#231;&#224; de l'horizon, la mesure ne conclut
rien et doit &#234;tre refaite.</p>

<h2><span class="n">8</span>Fiche de relev&#233;</h2>
<p>Station&#160;: &#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;
&#160;&#160;&#183;&#160;&#160; Date&#160;: &#8230;&#8230;&#8230;&#8230;&#8230;&#8230;
&#160;&#160;&#183;&#160;&#160; Appareil et focale&#160;: &#8230;&#8230;&#8230;&#8230;&#8230;<br/>
Cible&#160;: &#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;
&#160;&#160;&#183;&#160;&#160; Hauteur totale&#160;: &#8230;&#8230;&#8239;m
&#160;&#160;&#183;&#160;&#160; Source des rep&#232;res&#160;:
&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;<br/>
Distance&#160;: &#8230;&#8230;&#8239;km
&#160;&#160;&#183;&#160;&#160; Profil d&#233;gag&#233; v&#233;rifi&#233; sur&#160;:
&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;
&#160;&#160;&#183;&#160;&#160; Visibilit&#233; METAR&#160;: &#8230;&#8230;&#8239;km
&#160;&#160;&#183;&#160;&#160; Mar&#233;e&#160;: &#8230;&#8230;&#8239;m</p>
<table>
  <caption>Une ligne par hauteur d'&#339;il. Deux au minimum (&#233;tape 6.5).</caption>
  <thead><tr><th class="n">heure</th><th class="n">hauteur d'&#339;il</th><th class="n">images retenues / total</th><th class="n">&#233;chelle (m/px)</th><th class="n">c<sub>obs</sub></th><th class="n">c<sub>min</sub> (tab. 2)</th><th class="n">T air / T eau</th></tr></thead>
  <tbody>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
    <tr><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td><td class="n">&nbsp;</td></tr>
  </tbody>
</table>
<p><strong>Conclusion</strong> (section 7)&#160;:
&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;<br/>
<strong>Observations</strong> &#8212; &#233;tat de l'eau, nettet&#233; du bord,
couverture nuageuse, vent&#160;:<br/>
&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;&#8230;</p>
<p style="margin-top:14pt"><em>Les fichiers bruts et la vid&#233;o d'origine, non
recadr&#233;s, font partie du relev&#233;. Une conclusion sans eux n'est pas
v&#233;rifiable.</em></p>"""


def mil_px():
    return "{:,}".format(PIXELS_V).replace(",", "&#8239;")


def main():
    marge = controle()
    modele = open(GABARIT, encoding="utf-8").read()
    i = modele.find('<div class="page">')
    entete = re.sub(r"<title>[^<]*</title>",
                    "<title>Compatibilit&#233; d'une observation avec "
                    "R = 6 371 km</title>", modele[:i], count=1)
    open(CIBLE, "w", encoding="utf-8").write(
        entete + '<div class="page">\n' + corps() + '\n</div>\n')
    print("Protocole écrit : content/protocoles/masquage-court.html")
    for d in DISTANCES:
        print("  d=%2d km : c_min=%3.0f m · c(k=0,13)=%3.0f m · k pour voir la base %.3f"
              % (d, cachee(2, d, K_MAX), cachee(2, d, K_ORD),
                 k_pour_voir_base(2, d)))
    print("  marge à %d km, turbulence 20″ : %.0f×" % (D_RECO, marge))
    print("  échelle : 600 mm %.2f″/px · P900 %.2f″/px · P1000 %.2f″/px"
          % (par_pixel(600), par_pixel(2000), par_pixel(3000)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
