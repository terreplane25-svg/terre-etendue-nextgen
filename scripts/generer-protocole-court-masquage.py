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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fiche_releve import fiche                       # noqa: E402

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
APPAREILS = [("600 mm &#233;q. &#8212; minimum", "600 mm eq. &#8212; minimum", 600),
             ("Nikon P900 / P950 &#8212; 2 000 mm",
              "Nikon P900 / P950 &#8212; 2 000 mm", 2000),
             ("Nikon P1000 &#8212; 3 000 mm", "Nikon P1000 &#8212; 3 000 mm", 3000)]
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


def nb(x, n, fr=True):
    return ("%.*f" % (n, x)).replace(".", "," if fr else ".")


def t_cmin(fr):
    lignes = []
    for h in HAUTEURS:
        cells = "".join('<td class="n">%s</td>'
                        % ("&#8212;" if cachee(h, d, K_MAX) < 0.05
                           else nb(cachee(h, d, K_MAX), 0, fr))
                        for d in DISTANCES)
        vedette = h == 2
        lib = "<strong>%d m</strong>" % h if vedette else "%d m" % h
        lignes.append('    <tr%s><td class="n">%s</td>%s</tr>'
                      % (' class="hi"' if vedette else "", lib, cells))
    return "\n".join(lignes)


def t_impossible(fr):
    lignes = []
    for d in DISTANCES:
        k = k_pour_voir_base(2, d)
        lignes.append('    <tr%s><td class="n">%d km</td><td class="n">%s</td>'
                      '<td class="n">%s</td></tr>'
                      % (' class="hi"' if d in (40, 50) else "", d, nb(k, 3, fr),
                         (("hors d'atteinte" if k > 0.97 else
                           "au-del&#224; de l'inversion forte" if k > K_MAX
                           else "possible sous inversion") if fr else
                          ("beyond reach" if k > 0.97 else
                           "beyond the strongest inversion" if k > K_MAX
                           else "possible under inversion"))))
    return "\n".join(lignes)


def t_cible(fr):
    lignes = []
    for d in (30, 40, 50):
        ord_, mini = cachee(2, d, K_ORD), cachee(2, d, K_MAX)
        lignes.append('    <tr%s><td class="n">%d km</td><td class="n">%s m</td>'
                      '<td class="n">%s m</td><td class="n">%d m</td></tr>'
                      % (' class="hi"' if d == 40 else "", d, nb(mini, 0, fr),
                         nb(ord_, 0, fr), int(ord_ * 1.5)))
    return "\n".join(lignes)


def t_appareils(fr):
    lignes = []
    for nfr, nen, feq in APPAREILS:
        cells = "".join('<td class="n">%d px</td>'
                        % int(H / metres_par_pixel(feq, d))
                        for d, H in ((40, 100), (50, 150)))
        lignes.append('    <tr%s><td>%s</td><td class="n">%s&#8243;</td>%s</tr>'
                      % (' class="hi"' if feq == 2000 else "", nfr if fr else nen,
                         nb(par_pixel(feq), 2, fr), cells))
    return "\n".join(lignes)


def t_seeing(fr):
    lignes = []
    for s in SEEINGS:
        cells = []
        for d in (40, 50):
            inc = d * 1000 * s / 206265.0
            cells.append('<td class="n">&#177;&#8239;%s m</td>' % nb(inc, 1, fr))
            cells.append('<td class="n">%s&#215;</td>'
                         % nb(cachee(2, d, K_MAX) / inc, 0, fr))
        lignes.append('    <tr%s><td class="n">%d&#8243;</td>%s</tr>'
                      % (' class="hi"' if s == 10 else "", s, "".join(cells)))
    return "\n".join(lignes)




def mil_px():
    return "{:,}".format(PIXELS_V).replace(",", "&#8239;")


def corps(fr):
    controle()
    D = DISTANCES
    if fr:
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
masquage. Elle ne l'annule pas. On calcule donc le <strong>masquage minimal</strong>
<code>c<sub>min</sub></code>, celui qui subsiste au coefficient extr&#234;me
<code>k</code>&#8239;=&#8239;0,50, puis on mesure ce qui est r&#233;ellement
cach&#233;.</p>
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
  base de la cible redevienne visible, depuis 2&#8239;m de hauteur d'&#339;il. Ordres de
  grandeur&#160;: 0,13 en atmosph&#232;re ordinaire, 0,50 sous l'inversion la plus forte
  mesur&#233;e, 1,00 en conduit &#8212; le mirage sup&#233;rieur.</caption>
  <thead><tr><th class="n">distance</th><th class="n">k n&#233;cessaire</th><th class="n">r&#233;gime correspondant</th></tr></thead>
  <tbody>
{t_impossible(fr)}
  </tbody>
</table>
<p>&#192; 20&#8239;km, un contradicteur peut encore parler d'inversion exceptionnelle.
&#192; {D_RECO}&#8211;50&#8239;km, <strong>il faudrait un r&#233;gime qui n'existe
pas</strong>&#160;: voir la base y demande davantage qu'un conduit.</p>
<table>
  <caption>Tableau 2 &#8212; Masquage minimal <code>c<sub>min</sub></code>, en
  m&#232;tres, au coefficient extr&#234;me <code>k</code>&#8239;=&#8239;0,50. Un tiret
  signifie que la cible est en de&#231;&#224; de l'horizon.</caption>
  <thead><tr><th class="n">hauteur d'&#339;il</th>{"".join('<th class="n">%d km</th>' % d for d in D)}</tr></thead>
  <tbody>
{t_cmin(fr)}
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
{t_cible(fr)}
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
{t_appareils(fr)}
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
  <li>Les <strong>bulletins a&#233;ronautiques</strong> (METAR de l'a&#233;rodrome le
  plus proche) donnent la visibilit&#233; en clair. En dessous de la distance
  vis&#233;e, ne pas se d&#233;placer.</li>
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
  plut&#244;t que des photos isol&#233;es. Extraire ensuite les images individuelles
  et <strong>ne garder que les plus nettes</strong> &#8212; une sur vingt, une sur
  cinquante.</p>
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
{t_seeing(fr)}
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
<p><strong>Rep&#233;rage pr&#233;alable, avant de se d&#233;placer&#160;:</strong>
relever les coordonn&#233;es de la station et de la cible sur une carte, calculer la
distance, v&#233;rifier au tableau 3 que la cible est assez haute, et v&#233;rifier
qu'aucune terre n'est sur le trajet.</p>

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

""" + fiche(True, avec_style=True)

    return f"""<div class="masthead">
  <div class="kicker">Field protocol &#183; Amateur-executable &#183; Recommended distance {D_RECO}&#8211;50&#8239;km</div>
  <h1>Is a long-range observation compatible with an Earth of 6&#8239;371&#8239;km?</h1>
  <p class="sub">Measuring the hidden portion of a target, over a body of water</p>
</div>

<h2><span class="n">1</span>The principle</h2>
<p class="lead">On a surface of radius 6&#8239;371&#8239;km, a target lying beyond the
horizon has its base hidden by a height that depends only on eye height, distance, and
refraction.</p>
<p>Refraction lifts the light ray and <strong>reduces</strong> that hiding. It does not
cancel it. One therefore computes the <strong>minimum hiding</strong>
<code>c<sub>min</sub></code>, the amount that survives at the extreme coefficient
<code>k</code>&#8239;=&#8239;0.50, and then measures what is actually hidden.</p>
<div class="box key">
  <span class="lab">The criterion</span>
  <p>If the measured portion is <strong>less than <code>c<sub>min</sub></code></strong>,
  the observation is not compatible with a surface of radius 6&#8239;371&#8239;km
  &#8212; and the weather cannot be invoked, <strong>since
  <code>c<sub>min</sub></code> is already computed at its extreme value</strong>.</p>
</div>

<h2><span class="n">2</span>Why aim for {D_RECO}&#8211;50&#8239;km</h2>
<p class="lead">The longer the sight line, the more unassailable the result &#8212; and
beyond 40&#8239;km it leaves what any atmospheric regime can produce.</p>
<table>
  <caption>Table 1 &#8212; Refraction coefficient that would be required for the
  target's base to become visible again, from 2&#8239;m of eye height. Orders of
  magnitude: 0.13 in ordinary atmosphere, 0.50 under the strongest inversion measured,
  1.00 in a duct &#8212; the superior mirage.</caption>
  <thead><tr><th class="n">distance</th><th class="n">k required</th><th class="n">corresponding regime</th></tr></thead>
  <tbody>
{t_impossible(fr)}
  </tbody>
</table>
<p>At 20&#8239;km an objector can still invoke an exceptional inversion. At
{D_RECO}&#8211;50&#8239;km, <strong>a regime would be needed that does not
exist</strong>: seeing the base there demands more than a duct.</p>
<table>
  <caption>Table 2 &#8212; Minimum hiding <code>c<sub>min</sub></code>, in metres, at the
  extreme coefficient <code>k</code>&#8239;=&#8239;0.50. A dash means the target lies
  within the horizon.</caption>
  <thead><tr><th class="n">eye height</th>{"".join('<th class="n">%d km</th>' % d for d in D)}</tr></thead>
  <tbody>
{t_cmin(fr)}
  </tbody>
</table>

<h2><span class="n">3</span>The trade-off: the target must be tall</h2>
<p class="lead">This is the only real difficulty of long sight lines, and it decides the
choice of site.</p>
<p>At 40&#8239;km, a surface of 6&#8239;371&#8239;km hides
{nb(cachee(2, 40, K_ORD), 0, fr)}&#8239;m in ordinary conditions. An 80&#8239;m target
would therefore be <em>entirely</em> invisible, and the test would measure nothing.</p>
<table>
  <caption>Table 3 &#8212; Target height required, from 2&#8239;m of eye height.</caption>
  <thead><tr><th class="n">distance</th><th class="n">hidden at minimum</th><th class="n">hidden in ordinary conditions</th><th class="n">target of at least</th></tr></thead>
  <tbody>
{t_cible(fr)}
  </tbody>
</table>
<div class="box warn">
  <span class="lab">Which targets are suitable</span>
  <p><strong>Wind turbines</strong> &#8212; the best. An offshore farm stands on the
  water, the tower carries markers, hub and blade tip give two published heights.
  Current machines reach 150 to 260&#8239;m at blade tip.</p>
  <p><strong>Chimneys, cooling towers, bridge pylons, coastal high-rises.</strong>
  Published heights, storeyed or sectioned structure.</p>
  <p><strong>Lighthouses no longer serve</strong> beyond 30&#8239;km: even the tallest
  in Europe top out near 80&#8239;m and would be entirely hidden.</p>
</div>

<h2 class="brk"><span class="n">4</span>Equipment &#8212; strictly what is needed</h2>
<p class="lead">The calculation gives a counter-intuitive result: the camera is not the
limiting factor.</p>
<p>The target must cover enough pixels for its markers to be distinguished. Two hundred
pixels are ample, which calls for about <strong>{FOCALE_MINI}&#8239;mm full-frame
equivalent</strong>.</p>
<table>
  <caption>Table 4 &#8212; Scale obtained by camera, sensor {mil_px()} pixels
  high.</caption>
  <thead><tr><th>camera</th><th class="n">per pixel</th><th class="n">100&#8239;m target at 40&#8239;km</th><th class="n">150&#8239;m target at 50&#8239;km</th></tr></thead>
  <tbody>
{t_appareils(fr)}
  </tbody>
</table>
<div class="box key">
  <span class="lab">Why the P1000 adds nothing over the P900</span>
  <p>The P1000 gives {nb(par_pixel(3000), 2, fr)}&#8243; per pixel. But its
  <strong>diffraction</strong> already amounts to 2.1&#8243; &#8212; its entrance pupil
  is only 67&#8239;mm &#8212; and <strong>horizontal turbulence</strong> over
  40&#8239;km amounts to 5 to 20.</p>
  <p>The extra resolution is destroyed by the atmosphere before reaching the sensor.
  <strong>A P900 at 2 000&#8239;mm is already beyond what is needed</strong>, and a
  600&#8239;mm equivalent suffices for the measurement.</p>
</div>
<p><strong>The minimum needed:</strong></p>
<ul>
  <li>A camera at <strong>{FOCALE_MINI}&#8239;mm equivalent or more</strong>, able to
  record raw and video.</li>
  <li>A <strong>heavy tripod</strong>. At 2 000&#8239;mm one pixel is
  {nb(par_pixel(2000), 2, fr)}&#8243;: the slightest vibration erases the measurement.
  This is where not to economise.</li>
  <li><strong>Remote release</strong> or self-timer, and optical stabilisation
  <strong>switched off</strong> on a tripod.</li>
  <li>A <strong>tape measure</strong> for the eye height above the water.</li>
  <li>An <strong>online map</strong> for the distance, to the tenth of a kilometre.</li>
  <li>A <strong>thermometer</strong>, for the air and if possible for the water.</li>
</ul>

<h2><span class="n">5</span>The set-up that makes it succeed</h2>
<p class="lead">At {D_RECO}&#8211;50&#8239;km, failure rarely comes from the
calculation. It comes from three things, in this order.</p>

<h3>5.1 &#8212; Air transparency, the leading cause of failure</h3>
<p>On most days, <strong>nothing</strong> will be seen at 40&#8239;km. Meteorological
visibility must exceed the distance aimed at, which is rare.</p>
<ul>
  <li>Watch for <strong>cold dry air masses after a front has passed</strong>: that is
  when visibility exceeds 50&#8239;km.</li>
  <li><strong>Aviation bulletins</strong> (METAR from the nearest aerodrome) give
  visibility in plain figures. Below the distance aimed at, do not travel.</li>
  <li>Autumn and winter beat summer.</li>
  <li>Maritime airflow rather than continental air laden with aerosols.</li>
</ul>

<h3>5.2 &#8212; Stability, and frame selection</h3>
<p>At these focal lengths, turbulence makes the image <strong>boil</strong> several
times per second. A single photograph catches one instant at random.</p>
<div class="box key">
  <span class="lab">The technique that changes everything: film, then select</span>
  <p>Record a <strong>video of thirty seconds to a minute</strong> rather than isolated
  photographs. Then extract the individual frames and <strong>keep only the sharpest
  ones</strong> &#8212; one in twenty, one in fifty.</p>
  <p>This is the method used in planetary imaging. It turns a boiling mush into a crisp
  edge, and it is what makes the reading of 6.3 possible.</p>
</div>
<ul>
  <li>Heavy tripod, centre column <strong>retracted</strong>, weighted if possible.</li>
  <li>Shelter from the wind: a camera at 2 000&#8239;mm exposed to a breeze is
  unusable.</li>
  <li>Shutter speed <strong>1/500&#8239;s or shorter</strong>.</li>
  <li>Manual focus on the target, then <strong>locked</strong> for the whole run.</li>
  <li><strong>Manual, fixed exposure.</strong> An automatic exposure would shift the
  edge detection threshold from one frame to the next.</li>
</ul>
<table>
  <caption>Table 5 &#8212; What turbulence costs, and the margin that remains. From
  2&#8239;m of eye height.</caption>
  <thead><tr><th class="n">turbulence</th><th class="n">uncertainty at 40&#8239;km</th><th class="n">margin</th><th class="n">uncertainty at 50&#8239;km</th><th class="n">margin</th></tr></thead>
  <tbody>
{t_seeing(fr)}
  </tbody>
</table>
<p>Even in the least favourable case the margin stays above ten. <strong>Turbulence
hampers the reading; it does not threaten the conclusion.</strong></p>

<h3>5.3 &#8212; The site, and its four conditions</h3>
<div class="box warn">
  <span class="lab">Without these, the measurement is worthless</span>
  <p><strong>1. The sight line passes entirely over water.</strong> A hill at mid-path
  hides a base whatever the shape of the ground. This is what voids most records.</p>
  <p><strong>2. The target's base is at the water line</strong>, on the same body of
  water as you. An offshore turbine satisfies this by construction.</p>
  <p><strong>3. Low eye height</strong>, one to three metres. That is what makes the
  hiding large.</p>
  <p><strong>4. Water level recorded</strong> from the tide-gauge service if the site is
  maritime: the tide displaces both your eye height and the target's base.</p>
</div>
<p><strong>Advance reconnaissance, before travelling:</strong> read off the coordinates
of station and target on a map, compute the distance, check in Table 3 that the target
is tall enough, and check that no land lies on the path.</p>

<h2 class="brk"><span class="n">6</span>Shooting and measuring</h2>
<ol>
  <li><strong>Measure the eye height</strong> above the water and record it, with the
  time.</li>
  <li><strong>Film the target</strong> for thirty to sixty seconds at the telephoto
  setting, without cropping, settings locked (5.2). Then a few raw stills.</li>
  <li><strong>Photograph the scene at wide angle</strong>, with near landmarks, so a
  third party can find the station again.</li>
  <li><strong>Record</strong> the time, the air temperature and, if possible, the water
  temperature, together with the tide level.</li>
  <li><strong>Repeat from a markedly different eye height</strong> &#8212; a dyke, a
  balcony, a bridge &#8212; without changing any setting. The hidden base shall rise by
  the amount Table 2 gives. <strong>This is the simplest control that separates an
  occultation from a bank of haze.</strong></li>
</ol>
<div class="box">
  <span class="lab">A sign that does not deceive</span>
  <p>An occultation cuts <strong>sharply</strong>, at a definite height, and
  <strong>changes a great deal</strong> when one climbs a few metres. Haze fades
  progressively and barely moves with eye height.</p>
</div>
<h3>6.3 &#8212; The reading, on the image</h3>
<p>The scale is read on the target itself, <strong>without knowing the focal
length</strong>.</p>
<ol>
  <li>Identify two markers of known heights <code>z&#8321;</code> and
  <code>z&#8322;</code>, measure their separation in pixels <code>&#916;px</code>.</li>
  <li>The scale is <code>(z&#8322; &#8722; z&#8321;) / &#916;px</code>, in metres per
  pixel.</li>
  <li>Measure in pixels the distance between the lowest visible marker and the apparent
  lower edge of the target, then convert.</li>
  <li><code>c<sub>obs</sub></code> is the height, counted from the target's real base, of
  the lowest point still visible.</li>
</ol>

<h2><span class="n">7</span>Conclusion &#8212; the three outcomes</h2>
<div class="two">
  <div class="vc p">
    <p class="h">c<sub>obs</sub> &lt; c<sub>min</sub> &#8722; 3&#963;</p>
    <p class="v">Incompatible with R = 6&#8239;371&#8239;km</p>
    <p>More is seen below than the sphere allows under any refraction whatever.</p>
  </div>
  <div class="vc g">
    <p class="h">c<sub>obs</sub> &#8805; c<sub>min</sub></p>
    <p class="v">Compatible</p>
    <p>The observation falls within what the sphere allows. The value of
    <code>c<sub>obs</sub></code> then gives the refraction coefficient of the
    moment.</p>
  </div>
</div>
<p><code>3&#963;</code> is three times the uncertainty of Table 5 for the turbulence
observed. The third outcome is <strong>rejection</strong>: if the profile is not clear,
if the edge is too diffuse for a height to be assigned to it, or if the target lies
within the horizon, the measurement concludes nothing and must be repeated.</p>

""" + fiche(False, avec_style=False)


def main():
    marge = controle()
    modele = open(GABARIT, encoding="utf-8").read()
    i = modele.find('<div class="page">')
    entete = re.sub(r"<title>[^<]*</title>",
                    "<title>Compatibilit&#233; d'une observation avec "
                    "R = 6 371 km</title>", modele[:i], count=1)
    open(CIBLE, "w", encoding="utf-8").write(
        entete + '<div class="page">\n'
        '<div class="langbar"><span class="on">FRAN&#199;AIS</span>'
        '<span>ENGLISH &#8212; seconde moiti&#233;</span></div>\n\n'
        + corps(True) +
        '\n\n<div class="langbar" style="break-before:page;page-break-before:always">'
        '<span>FRAN&#199;AIS &#8212; first half</span>'
        '<span class="on">ENGLISH</span></div>\n\n'
        + corps(False) + '\n</div>\n')
    print("Protocole bilingue écrit : content/protocoles/masquage-court.html")
    for d in DISTANCES:
        print("  d=%2d km : c_min=%3.0f m · c(k=0,13)=%3.0f m · k pour voir la base %.3f"
              % (d, cachee(2, d, K_MAX), cachee(2, d, K_ORD),
                 k_pour_voir_base(2, d)))
    print("  marge à %d km, turbulence 20″ : %.0f×" % (D_RECO, marge))
    return 0


if __name__ == "__main__":
    sys.exit(main())
