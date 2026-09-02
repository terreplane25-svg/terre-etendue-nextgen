#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Protocole : le coefficient de réfraction exigé par une observation lointaine.

Ce que la méthode produit
─────────────────────────
Un nombre, k, et une longueur. Le nombre est le coefficient de réfraction qu'il
faudrait pour qu'une cible donnée soit visible depuis un point donné à une
distance donnée sur une surface de rayon 6 371 km. La longueur est celle du
trajet sur lequel ce coefficient devrait être maintenu.

Pourquoi ce choix, et non « l'objet est-il impossible à voir »
─────────────────────────────────────────────────────────────
Il n'existe aucune configuration où la géométrie interdise de voir. La hauteur
masquée c(h, d, k) tend vers zéro quand k tend vers 1, donc pour toute hauteur
d'observation, toute cible et toute distance, il existe un k inférieur à 1 qui
rend la cible visible. Écrire « aucun phénomène ne peut le faire réapparaître »
serait faux, et le premier lecteur compétent le verrait.

Ce qui est vrai et décisif, c'est autre chose : le k exigé se calcule
exactement, et il se compare à ce que l'atmosphère produit réellement. Un k de
0,9 tenu sur deux cents kilomètres n'a jamais été mesuré. Le document énonce
donc une échelle déclarée d'avance et y range chaque observation.

La configuration la plus contraignante est basse et longue
──────────────────────────────────────────────────────────
Contre-intuitif, et vérifié dans controle() : monter en altitude AFFAIBLIT
l'exigence, parce que la cible est moins profondément enfouie. Une cible de 50 m
à 200 km exige k = 0,907 depuis 100 m, mais seulement 0,145 depuis 2 000 m. Les
observations de haute montagne à très longue distance sont donc les moins
contraignantes ; ce sont les vues basses et lointaines qui pèsent.

La méthode accepte néanmoins toutes les hauteurs, puisque chacune se calcule.
Le plancher de 100 m écarte simplement la couche de surface, où les gradients
mesurés sont extrêmes et où le conduit d'évaporation vit.
"""
import math
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTOCOLES = os.path.join(RACINE, "content", "protocoles")
CIBLE = os.path.join(PROTOCOLES, "k-requis-bilingue.html")
GABARIT = os.path.join(PROTOCOLES, "visee-terrestre-bilingue.html")

R = 6371000.0
H_PLANCHER = 100           # m — plancher aux deux extrémités
HAUTEURS = [100, 300, 800, 2000, 4000]
FOCALE_MINI = 600          # mm équivalent 24×36
# L'échelle de lecture, déclarée avant toute mesure.
ECHELLE = [
    (0.25, "ordinaire", "ordinary",
     "atmosph&#232;re courante&#160;; l'observation n'a rien d'anormal",
     "everyday atmosphere; the observation is unremarkable"),
    (0.50, "inversion forte", "strong inversion",
     "inversion thermique marqu&#233;e, document&#233;e et fr&#233;quente au-dessus "
     "de l'eau", "marked thermal inversion, documented and frequent over water"),
    (0.75, "super-r&#233;fraction", "super-refraction",
     "r&#233;gime rare, mesur&#233; sur de courtes distances, jamais soutenu sur "
     "des dizaines de kilom&#232;tres",
     "rare regime, measured over short distances, never sustained over tens of "
     "kilometres"),
    (1.00, "conduit soutenu", "sustained duct",
     "le rayon suivrait presque la surface sur toute la port&#233;e&#160;; aucune "
     "mesure publi&#233;e n'approche cela sur une telle longueur",
     "the ray would nearly follow the surface over the whole range; no published "
     "measurement approaches this over such a length"),
]
EXEMPLES = [(100, 50, 90), (100, 100, 120), (100, 50, 200),
            (300, 200, 160), (300, 50, 200), (800, 500, 250),
            (2000, 1000, 350), (4000, 1500, 450)]
PLANIF = [50, 200, 500]    # hauteurs de cible pour le tableau de planification
SEUILS_PLANIF = [0.25, 0.50, 0.75]


def cachee(h, d_km, k):
    """Hauteur masquée à la base de la cible, en mètres."""
    if k >= 1:
        return 0.0
    Rp = R / (1 - k)
    d = d_km * 1000.0
    a = math.sqrt((Rp + h) ** 2 - Rp ** 2)
    return 0.0 if d <= a else math.sqrt(Rp ** 2 + (d - a) ** 2) - Rp


def k_requis(h_obs, H_cible, d_km):
    """Coefficient qu'il faudrait pour que le sommet de la cible affleure."""
    lo, hi = 0.0, 0.999999
    for _ in range(400):
        m = (lo + hi) / 2
        if cachee(h_obs, d_km, m) > H_cible:
            lo = m
        else:
            hi = m
    return hi


def d_pour_k(h_obs, H_cible, k_vise):
    """Distance à laquelle le k exigé atteint la valeur visée."""
    lo, hi = 1.0, 3000.0
    for _ in range(300):
        m = (lo + hi) / 2
        if k_requis(h_obs, H_cible, m) < k_vise:
            lo = m
        else:
            hi = m
    return hi


def regime(k, fr):
    for seuil, nfr, nen, _, _ in ECHELLE:
        if k < seuil:
            return nfr if fr else nen
    return "conduit soutenu" if fr else "sustained duct"


def controle():
    """Recalcule chaque valeur imprimée, et vérifie les deux faits structurants."""
    # 1. Le k exigé est toujours strictement inférieur à 1 : pas de mur géométrique.
    for h, H, d in EXEMPLES + [(100, 10, 500), (100, 1, 1000)]:
        assert k_requis(h, H, d) < 1.0
    # 2. Monter affaiblit l'exigence, à cible et distance égales.
    suite = [k_requis(h, 50, 200) for h in HAUTEURS]
    assert suite == sorted(suite, reverse=True), suite
    assert abs(suite[0] - 0.907) < 0.003, suite[0]
    assert abs(suite[3] - 0.145) < 0.005, suite[3]
    # 3. Quelques valeurs du tableau d'exemples.
    for h, H, d, attendu in ((100, 50, 90, 0.542), (300, 200, 160, 0.507),
                             (2000, 1000, 350, 0.394), (4000, 1500, 450, 0.346)):
        assert abs(k_requis(h, H, d) - attendu) < 0.003, (h, H, d)
    # 4. Le tableau de planification.
    assert abs(d_pour_k(100, 50, 0.75) - 122) < 2
    assert abs(d_pour_k(4000, 500, 0.75) - 611) < 4
    return True


def nb(x, n, fr):
    return ("%.*f" % (n, x)).replace(".", "," if fr else ".")


def t_echelle(fr):
    lignes, bas = [], 0.0
    for seuil, nfr, nen, dfr, den in ECHELLE:
        plage = ("%s &#8211; %s" % (nb(bas, 2, fr), nb(seuil, 2, fr))
                 if bas else "&lt; %s" % nb(seuil, 2, fr))
        vedette = seuil == 1.00
        g = (lambda s: "<strong>%s</strong>" % s) if vedette else (lambda s: s)
        lignes.append('    <tr%s><td class="n">%s</td><td>%s</td><td>%s</td></tr>'
                      % (' class="hi"' if vedette else "", g(plage),
                         g(nfr if fr else nen), dfr if fr else den))
        bas = seuil
    return "\n".join(lignes)


def t_exemples(fr):
    lignes = []
    for h, H, d in EXEMPLES:
        k = k_requis(h, H, d)
        lignes.append('    <tr%s><td class="n">%s m</td><td class="n">%s m</td>'
                      '<td class="n">%d km</td><td class="n">%s</td>'
                      '<td>%s</td></tr>'
                      % (' class="hi"' if k > 0.75 else "",
                         "{:,}".format(h).replace(",", "&#8239;"),
                         "{:,}".format(H).replace(",", "&#8239;"),
                         d, nb(k, 3, fr), regime(k, fr)))
    return "\n".join(lignes)


def t_planif(fr, H_cible):
    lignes = []
    for h in HAUTEURS:
        cells = "".join('<td class="n">%d km</td>' % round(d_pour_k(h, H_cible, s))
                        for s in SEUILS_PLANIF)
        lignes.append('    <tr%s><td class="n">%s m</td>%s</tr>'
                      % (' class="hi"' if h == 100 else "",
                         "{:,}".format(h).replace(",", "&#8239;"), cells))
    return "\n".join(lignes)


def t_hauteur(fr):
    lignes = []
    for h in HAUTEURS:
        k = k_requis(h, 50, 200)
        lignes.append('    <tr%s><td class="n">%s m</td><td class="n">%s</td>'
                      '<td>%s</td></tr>'
                      % (' class="hi"' if h == 100 else "",
                         "{:,}".format(h).replace(",", "&#8239;"),
                         nb(k, 3, fr), regime(k, fr)))
    return "\n".join(lignes)


# ── La fiche de relevé, sur une page ─────────────────────────────────────────
STYLE_FICHE = """<style>
.fiche{font-size:8.7pt; line-height:1.34}
.fiche h2{margin:0 0 10pt}
.fiche h3{font-family:"IBM Plex Mono",monospace; font-size:8.2pt; font-weight:600;
  letter-spacing:.13em; text-transform:uppercase; color:var(--globe);
  margin:11pt 0 5pt; padding-bottom:2.5pt; border-bottom:.6pt solid var(--line)}
.fiche table{width:100%; border-collapse:collapse; margin:0 0 4pt}
.fiche td,.fiche th{padding:4pt 5pt; border:.5pt solid var(--line); vertical-align:middle}
.fiche th{background:var(--wash); font-family:"IBM Plex Mono",monospace;
  font-size:7.4pt; font-weight:600; letter-spacing:.05em; text-transform:uppercase;
  color:var(--soft); text-align:center}
.fiche td.lab{width:21%; background:var(--wash); font-weight:600; color:var(--soft);
  font-size:8.2pt}
.fiche td.val{width:29%}
.fiche tr.vide td{height:15pt}
.rem{display:inline-block; border-bottom:.6pt solid var(--line2); min-width:26mm; height:9pt}
.rem.court{min-width:12mm}
.rem.long{min-width:100%}
.case{display:inline-block; width:9.5pt; height:9.5pt; border:.8pt solid var(--soft);
  vertical-align:-1.5pt; margin-right:5pt}
.fiche ul.just{list-style:none; padding:0; margin:0 0 6pt}
.fiche ul.just li{margin:0 0 5.5pt; padding-left:15pt; text-indent:-15pt; text-align:left}
.fiche p{margin:0 0 5pt; text-align:left}
.fiche .regle{border-left:2.4pt solid var(--alert); background:var(--alert-w);
  padding:6pt 9pt; margin-top:7pt; font-size:8.3pt}
</style>"""

REM = '<span class="rem"></span>'
RC = '<span class="rem court"></span>'
RL = '<span class="rem long"></span>'
CASE = '<span class="case"></span>'


def _l(a, b, c, d):
    return ('    <tr><td class="lab">%s</td><td class="val">%s</td>'
            '<td class="lab">%s</td><td class="val">%s</td></tr>' % (a, b, c, d))


def fiche(fr, style=True):
    s = STYLE_FICHE if style else ""
    if fr:
        t = "Fiche de relev&#233;"
        s1, s2, s3, s4 = ("1. La configuration", "2. Ce qui est vu",
                          "3. R&#233;sultat", "4. Pi&#232;ces &#224; joindre")
        ctx = "\n".join([
            _l("Station (lieu)", REM, "Date / heure",
               RC + " / " + RC + " / " + RC + " &#224; " + RC + " h"),
            _l("Altitude de l'&#339;il", RC + " m", "Source de cette altitude", REM),
            _l("Cible", REM, "Appareil / focale", RC + " / " + RC + " mm"),
            _l("Hauteur de la cible", RC + " m", "Source de cette hauteur", REM),
            _l("Distance", RC + " km", "Source de la distance", REM),
        ])
        ent = ["point le plus bas visible", "hauteur au-dessus de la base",
               "source du rep&#232;re"]
        r1 = ("<strong>Ce qui est visible.</strong> D&#233;crire le point le plus bas "
              "de la cible que l'on distingue, et donner sa hauteur au-dessus de la "
              "base de la cible.")
        r2 = ("<strong>k exig&#233;</strong> (section 5)&#160;: " + RC
              + "&#160;&#160;&#160;&#160;<strong>r&#233;gime</strong> (tableau 1)&#160;: "
              + REM)
        r3 = ("<strong>Longueur sur laquelle ce coefficient devrait &#234;tre "
              "tenu</strong>&#160;: " + RC + " km")
        obs = ("<strong>Conditions.</strong> Temp&#233;rature de l'air " + RC
               + " &#176;C, de l'eau " + RC + " &#176;C, visibilit&#233; annonc&#233;e "
               + RC + " km, &#233;tat du ciel " + REM)
        rejet = (CASE + "profil interm&#233;diaire d&#233;gag&#233;, "
                 "v&#233;rifi&#233; sur carte&#160;&#160;&#160;&#160;" + CASE
                 + "bord de la cible net, une hauteur peut lui &#234;tre "
                 "assign&#233;e")
        pieces = [
            ("Fichiers d'origine", "images ou vid&#233;o brutes issues de la carte "
             "m&#233;moire, non retouch&#233;es et non recadr&#233;es, "
             "m&#233;tadonn&#233;es intactes."),
            ("Photo d'amorce", "clich&#233; grand-angle situant la station et ses "
             "rep&#232;res proches."),
            ("Preuve d'altitude", "relev&#233; GNSS ou extrait cartographique donnant "
             "l'altitude de l'&#339;il."),
            ("Preuve de distance", "extrait de carte ou calcul g&#233;od&#233;sique "
             "entre les deux positions."),
            ("Source de la hauteur de cible", "document officiel, plan ou fiche "
             "technique."),
        ]
        regle = ("<strong>R&#232;gle d'analyse.</strong> Si une seule pi&#232;ce "
                 "manque, ou si l'une des trois grandeurs &#8212; altitude de "
                 "l'&#339;il, hauteur de cible, distance &#8212; n'est pas "
                 "sourc&#233;e, le relev&#233; est class&#233; <strong>&#171;&#160;non "
                 "&#233;valuable&#160;&#187;</strong> et le coefficient n'est pas "
                 "calcul&#233;.")
    else:
        t = "Record sheet"
        s1, s2, s3, s4 = ("1. The configuration", "2. What is seen", "3. Result",
                          "4. Evidence to attach")
        ctx = "\n".join([
            _l("Station (place)", REM, "Date / time",
               RC + " / " + RC + " / " + RC + " at " + RC + " h"),
            _l("Eye elevation", RC + " m", "Source of that elevation", REM),
            _l("Target", REM, "Camera / focal length", RC + " / " + RC + " mm"),
            _l("Target height", RC + " m", "Source of that height", REM),
            _l("Distance", RC + " km", "Source of the distance", REM),
        ])
        ent = ["lowest visible point", "height above the base", "source of the marker"]
        r1 = ("<strong>What is visible.</strong> Describe the lowest point of the "
              "target that can be made out, and give its height above the target's "
              "base.")
        r2 = ("<strong>k required</strong> (section 5): " + RC
              + "&#160;&#160;&#160;&#160;<strong>regime</strong> (Table 1): " + REM)
        r3 = ("<strong>Length over which that coefficient would have to be "
              "sustained</strong>: " + RC + " km")
        obs = ("<strong>Conditions.</strong> Air temperature " + RC
               + " &#176;C, water " + RC + " &#176;C, reported visibility " + RC
               + " km, state of the sky " + REM)
        rejet = (CASE + "intervening profile clear, verified on a "
                 "map&#160;&#160;&#160;&#160;" + CASE
                 + "target edge sharp, a height can be assigned to it")
        pieces = [
            ("Original files", "raw images or video straight from the memory card, "
             "neither retouched nor cropped, metadata intact."),
            ("Establishing shot", "wide-angle frame locating the station and its near "
             "landmarks."),
            ("Proof of elevation", "GNSS reading or map extract giving the eye "
             "elevation."),
            ("Proof of distance", "map extract or geodetic computation between the two "
             "positions."),
            ("Source of target height", "official document, drawing or data sheet."),
        ]
        regle = ("<strong>Analysis rule.</strong> If a single item is missing, or if "
                 "any of the three quantities &#8212; eye elevation, target height, "
                 "distance &#8212; is unsourced, the record is classified <strong>"
                 "&#8220;not assessable&#8221;</strong> and the coefficient is not "
                 "computed.")

    vides = "\n".join('    <tr class="vide">%s</tr>' % ("<td></td>" * len(ent))
                      for _ in range(2))
    return f"""{s}
<div class="fiche">
<h2 class="brk">{t}</h2>

<h3>{s1}</h3>
<table>
  <tbody>
{ctx}
  </tbody>
</table>

<h3>{s2}</h3>
<p>{r1}</p>
<table>
  <thead><tr>{"".join("<th>%s</th>" % e for e in ent)}</tr></thead>
  <tbody>
{vides}
  </tbody>
</table>
<p>{rejet}</p>

<h3>{s3}</h3>
<p>{r2}</p>
<p>{r3}</p>
<p style="margin-top:7pt">{obs}</p>

<h3>{s4}</h3>
<ul class="just">
{chr(10).join('  <li>%s<strong>%s</strong> &#8212; %s</li>' % (CASE, a, b)
              for a, b in pieces)}
</ul>
<div class="regle">{regle}</div>
</div>"""



def bloc_planif(fr):
    """Les trois tableaux de planification. Hors f-string : ils contiennent des \\n."""
    out = []
    for i, H in enumerate(PLANIF):
        if fr:
            cap = ("Tableau %d &#8212; Cible de %d&#8239;m de hauteur. Distance "
                   "&#224; partir de laquelle le coefficient exig&#233; entre dans "
                   "chaque r&#233;gime." % (3 + i, H))
            tete = "altitude de l'&#339;il"
        else:
            cap = ("Table %d &#8212; Target %d&#8239;m high. Distance from which the "
                   "required coefficient enters each regime." % (3 + i, H))
            tete = "eye elevation"
        virg = "," if fr else "."
        out.append(
            "<table>\n  <caption>%s</caption>\n"
            "  <thead><tr><th class=\"n\">%s</th>"
            "<th class=\"n\">k &gt; 0%s25</th><th class=\"n\">k &gt; 0%s50</th>"
            "<th class=\"n\">k &gt; 0%s75</th></tr></thead>\n"
            "  <tbody>\n%s\n  </tbody>\n</table>"
            % (cap, tete, virg, virg, virg, t_planif(fr, H)))
    return "\n".join(out)


def corps(fr):
    controle()
    if fr:
        return f"""<div class="masthead">
  <div class="kicker">Protocole de terrain &#183; Toutes altitudes &#183; Un r&#233;sultat chiffr&#233;</div>
  <h1>Quelle r&#233;fraction faudrait-il pour voir cet objet&#8239;?</h1>
  <p class="sub">M&#233;thode de calcul et de relev&#233; pour une observation &#224; longue distance</p>
</div>

<h2><span class="n">1</span>Ce que la m&#233;thode produit</h2>
<p class="lead">Un nombre et une longueur. Le nombre est le coefficient de
r&#233;fraction qu'il faudrait pour qu'une cible donn&#233;e soit visible depuis un
point donn&#233;, &#224; une distance donn&#233;e, sur une surface de rayon
6&#8239;371&#8239;km. La longueur est celle du trajet sur lequel ce coefficient
devrait &#234;tre maintenu.</p>
<p>Trois grandeurs suffisent &#224; le calculer&#160;: <strong>l'altitude de
l'&#339;il</strong>, <strong>la hauteur de la cible</strong> et <strong>la
distance</strong>. Rien d'autre n'entre dans le r&#233;sultat.</p>
<p>Ce coefficient se compare ensuite &#224; ce que l'atmosph&#232;re produit
r&#233;ellement, sur une &#233;chelle fix&#233;e avant toute observation.</p>
<table>
  <caption>Tableau 1 &#8212; L'&#233;chelle de lecture, arr&#234;t&#233;e avant toute
  mesure.</caption>
  <thead><tr><th class="n">k exig&#233;</th><th>r&#233;gime</th><th>ce que cela suppose</th></tr></thead>
  <tbody>
{t_echelle(fr)}
  </tbody>
</table>
<div class="box key">
  <span class="lab">Ce que le r&#233;sultat vaut</span>
  <p>Une observation qui ressort &#224; <strong>k&#8239;=&#8239;0,9 sur
  200&#8239;km</strong> n'est pas balay&#233;e d'un &#171;&#160;c'est la
  r&#233;fraction&#160;&#187;, parce que le calcul a d&#233;j&#224; dit
  <em>laquelle</em>, et sur quelle longueur il faudrait la tenir.</p>
  <p>Inversement, une observation qui ressort sous 0,25 est ordinaire, et il faut le
  dire aussi nettement.</p>
</div>

<h2><span class="n">2</span>La condition d'altitude</h2>
<p class="lead">L'&#339;il et le sommet de la cible doivent tous deux se trouver
&#224; <strong>{H_PLANCHER}&#8239;m au moins</strong> au-dessus de la surface.</p>
<p>Sous cette hauteur, on se trouve dans la couche o&#249; les gradients thermiques
mesur&#233;s sont extr&#234;mes et o&#249; se forment les conduits d'&#233;vaporation.
Un relev&#233; fait au ras de l'eau se discute&#160;; un relev&#233; fait
au-dessus de cette couche se discute beaucoup moins.</p>
<p>Au-del&#224; de ce plancher, <strong>toutes les altitudes sont accept&#233;es</strong>
&#8212; 300, 800, 2&#8239;000, 4&#8239;000&#8239;m &#8212; puisque chacune se calcule.
Une remarque toutefois, contre-intuitive et qu'il vaut mieux conna&#238;tre avant de
choisir son site.</p>
<table>
  <caption>Tableau 2 &#8212; Une m&#234;me cible de 50&#8239;m &#224; 200&#8239;km, vue
  de diff&#233;rentes altitudes. <strong>Monter affaiblit l'exigence</strong>&#160;: la
  cible est moins profond&#233;ment enfouie.</caption>
  <thead><tr><th class="n">altitude de l'&#339;il</th><th class="n">k exig&#233;</th><th>r&#233;gime</th></tr></thead>
  <tbody>
{t_hauteur(fr)}
  </tbody>
</table>
<p>Les vues de haute montagne &#224; tr&#232;s longue distance sont donc les
<em>moins</em> contraignantes. Ce sont les observations <strong>basses et
lointaines</strong> qui p&#232;sent le plus.</p>

<h2><span class="n">3</span>Choisir la configuration</h2>
<p class="lead">Les trois tableaux qui suivent donnent, pour chaque altitude
d'observation, la distance &#224; laquelle le coefficient exig&#233; atteint chaque
r&#233;gime.</p>
{bloc_planif(fr)}
<div class="box warn">
  <span class="lab">Ce qu'il faut viser</span>
  <p>Depuis {H_PLANCHER}&#8239;m sur une cible de 50&#8239;m, il faut d&#233;passer
  <strong>122&#8239;km</strong> pour entrer dans le r&#233;gime du conduit soutenu.
  Depuis 2&#8239;000&#8239;m sur la m&#234;me cible, il faut aller &#224;
  370&#8239;km.</p>
  <p>C'est le tableau qui d&#233;cide du site, et non l'inverse.</p>
</div>

<h2 class="brk"><span class="n">4</span>Le mat&#233;riel et le site</h2>
<ul>
  <li>Un appareil &#224; <strong>{FOCALE_MINI}&#8239;mm &#233;quivalent 24&#215;36 ou
  plus</strong>, enregistrant en brut et en vid&#233;o.</li>
  <li>Un <strong>tr&#233;pied lourd</strong>, colonne centrale rentr&#233;e,
  d&#233;clenchement &#224; distance, stabilisation d&#233;sactiv&#233;e.</li>
  <li>Un <strong>relev&#233; GNSS</strong> ou une carte donnant l'altitude de
  l'&#339;il et les deux positions.</li>
  <li>Un <strong>thermom&#232;tre</strong>, pour l'air et si possible pour l'eau.</li>
</ul>
<p>Le site doit satisfaire deux conditions, et elles ne se n&#233;gocient pas.</p>
<div class="box warn">
  <span class="lab">Les deux conditions du site</span>
  <p><strong>1. Le trajet est enti&#232;rement d&#233;gag&#233;.</strong> Un relief
  interm&#233;diaire masque une cible quelle que soit la forme du sol, et c'est ce qui
  invalide le plus de relev&#233;s. La v&#233;rification se fait sur carte, avant de se
  d&#233;placer, et la trace est jointe au relev&#233;.</p>
  <p><strong>2. La hauteur de la cible est publi&#233;e.</strong> Sans source, la
  troisi&#232;me grandeur du calcul manque, et le coefficient ne peut pas &#234;tre
  &#233;tabli.</p>
</div>

<h2><span class="n">5</span>Le calcul</h2>
<p>Avec <code>R</code>&#8239;=&#8239;6&#8239;371&#8239;km, <code>h</code> l'altitude de
l'&#339;il et <code>d</code> la distance&#160;:</p>
<div class="eq">
  R&#8242; = R / (1 &#8722; k)&#160;&#160;&#160;&#160;
  a = &#8730;[(R&#8242;+h)&#178; &#8722; R&#8242;&#178;]&#160;&#160;&#160;&#160;
  c = &#8730;[R&#8242;&#178; + (d&#8722;a)&#178;] &#8722; R&#8242;
  <span class="cap">c est la hauteur masqu&#233;e &#224; la base de la cible. Si d &#8804; a, la cible n'est pas masqu&#233;e et la m&#233;thode ne s'applique pas.</span>
</div>
<p>Le coefficient exig&#233; est celui qui rend <code>c</code> &#233;gal &#224; la
hauteur du point le plus bas r&#233;ellement visible. On le r&#233;sout par dichotomie
sur <code>k</code> entre 0 et 1.</p>
<p>Si la <strong>base</strong> de la cible est visible, la hauteur du point le plus bas
vaut z&#233;ro. Si seul le <strong>sommet</strong> affleure, elle vaut la hauteur totale
de la cible.</p>
<table>
  <caption>Tableau 6 &#8212; Exemples r&#233;solus. Les lignes surlign&#233;es
  demandent un conduit soutenu.</caption>
  <thead><tr><th class="n">&#339;il</th><th class="n">cible</th><th class="n">distance</th><th class="n">k exig&#233;</th><th>r&#233;gime</th></tr></thead>
  <tbody>
{t_exemples(fr)}
  </tbody>
</table>

<h2><span class="n">6</span>La prise de vue</h2>
<ol>
  <li><strong>Relever</strong> l'altitude de l'&#339;il, l'heure, les
  temp&#233;ratures, et la visibilit&#233; annonc&#233;e par le bulletin
  a&#233;ronautique le plus proche.</li>
  <li><strong>Filmer la cible</strong> trente &#224; soixante secondes au
  t&#233;l&#233;objectif, r&#233;glages verrouill&#233;s, exposition manuelle et fixe,
  sans recadrage. Puis quelques images fixes en brut.</li>
  <li><strong>Ne garder que les images les plus nettes</strong> &#8212; une sur vingt,
  une sur cinquante. &#192; ces distances la turbulence fait bouillonner l'image
  plusieurs fois par seconde&#160;; une prise unique attrape un instant au hasard.</li>
  <li><strong>Photographier la sc&#232;ne au grand angle</strong>, avec des
  rep&#232;res proches, pour qu'un tiers puisse retrouver la station.</li>
  <li><strong>Identifier le point le plus bas visible</strong> sur la cible et relever
  sa hauteur au-dessus de la base, en s'appuyant sur un rep&#232;re dont la hauteur
  est publi&#233;e.</li>
</ol>
<p>Un choix de jour&#160;: viser une masse d'air froid et s&#232;che apr&#232;s le
passage d'un front, quand la visibilit&#233; annonc&#233;e d&#233;passe la distance
vis&#233;e. La plupart des jours, on ne verra rien &#224; ces distances, et ce n'est
pas un r&#233;sultat.</p>

<h2><span class="n">7</span>Ce qui est rapport&#233;</h2>
<p>Le r&#233;sultat d'essai tient en trois lignes&#160;: le <strong>coefficient
exig&#233;</strong>, le <strong>r&#233;gime</strong> du tableau 1, et la
<strong>longueur</strong> sur laquelle ce coefficient devrait &#234;tre tenu &#8212;
c'est-&#224;-dire la distance elle-m&#234;me.</p>
<p>S'y ajoutent les trois grandeurs d'entr&#233;e avec leurs sources, les conditions
relev&#233;es, et les fichiers bruts. Un relev&#233; dont l'une des trois grandeurs
n'est pas sourc&#233;e n'est pas &#233;valu&#233;.</p>
<p>Le rapport n'&#233;nonce pas de conclusion sur un mod&#232;le. Il &#233;nonce un
coefficient et une longueur, et laisse chacun juger si l'atmosph&#232;re les
produit.</p>

""" + fiche(True, style=True)

    return f"""<div class="masthead">
  <div class="kicker">Field protocol &#183; All elevations &#183; A numerical result</div>
  <h1>What refraction would be needed to see this object?</h1>
  <p class="sub">Calculation and recording method for a long-range observation</p>
</div>

<h2><span class="n">1</span>What the method produces</h2>
<p class="lead">A number and a length. The number is the refraction coefficient that
would be needed for a given target to be visible from a given point, at a given
distance, on a surface of radius 6&#8239;371&#8239;km. The length is that of the path
over which the coefficient would have to be sustained.</p>
<p>Three quantities suffice to compute it: <strong>the eye elevation</strong>,
<strong>the target height</strong> and <strong>the distance</strong>. Nothing else
enters the result.</p>
<p>That coefficient is then compared with what the atmosphere actually produces, on a
scale fixed before any observation.</p>
<table>
  <caption>Table 1 &#8212; The reading scale, settled before any measurement.</caption>
  <thead><tr><th class="n">k required</th><th>regime</th><th>what it implies</th></tr></thead>
  <tbody>
{t_echelle(fr)}
  </tbody>
</table>
<div class="box key">
  <span class="lab">What the result is worth</span>
  <p>An observation coming out at <strong>k&#8239;=&#8239;0.9 over 200&#8239;km</strong>
  is not dismissed with &#8220;that's refraction&#8221;, because the calculation has
  already said <em>which</em> refraction, and over what length it would have to
  hold.</p>
  <p>Conversely, an observation coming out below 0.25 is ordinary, and that must be
  said just as plainly.</p>
</div>

<h2><span class="n">2</span>The elevation condition</h2>
<p class="lead">The eye and the top of the target shall both lie at least
<strong>{H_PLANCHER}&#8239;m</strong> above the surface.</p>
<p>Below that height one is in the layer where measured thermal gradients are extreme
and where evaporation ducts form. A record made at water level is arguable; one made
above that layer is far less so.</p>
<p>Above that floor, <strong>all elevations are accepted</strong> &#8212; 300, 800,
2&#8239;000, 4&#8239;000&#8239;m &#8212; since each one can be computed. One remark
though, counter-intuitive and worth knowing before choosing a site.</p>
<table>
  <caption>Table 2 &#8212; The same 50&#8239;m target at 200&#8239;km, seen from
  different elevations. <strong>Going higher weakens the requirement</strong>: the
  target is less deeply buried.</caption>
  <thead><tr><th class="n">eye elevation</th><th class="n">k required</th><th>regime</th></tr></thead>
  <tbody>
{t_hauteur(fr)}
  </tbody>
</table>
<p>High-mountain views at very long range are therefore the <em>least</em> demanding.
It is the <strong>low and distant</strong> observations that weigh most.</p>

<h2><span class="n">3</span>Choosing the configuration</h2>
<p class="lead">The three tables below give, for each observing elevation, the distance
at which the required coefficient reaches each regime.</p>
{bloc_planif(fr)}
<div class="box warn">
  <span class="lab">What to aim for</span>
  <p>From {H_PLANCHER}&#8239;m on a 50&#8239;m target, one must exceed
  <strong>122&#8239;km</strong> to enter the sustained-duct regime. From
  2&#8239;000&#8239;m on the same target, 370&#8239;km are needed.</p>
  <p>It is the table that decides the site, not the other way round.</p>
</div>

<h2 class="brk"><span class="n">4</span>Equipment and site</h2>
<ul>
  <li>A camera at <strong>{FOCALE_MINI}&#8239;mm full-frame equivalent or more</strong>,
  recording raw and video.</li>
  <li>A <strong>heavy tripod</strong>, centre column retracted, remote release,
  stabilisation switched off.</li>
  <li>A <strong>GNSS reading</strong> or a map giving the eye elevation and both
  positions.</li>
  <li>A <strong>thermometer</strong>, for the air and if possible for the water.</li>
</ul>
<p>The site shall satisfy two conditions, and they are not negotiable.</p>
<div class="box warn">
  <span class="lab">The two site conditions</span>
  <p><strong>1. The path is entirely clear.</strong> Intervening relief hides a target
  whatever the shape of the ground, and this is what voids most records. Verification is
  done on a map, before travelling, and the trace is attached to the record.</p>
  <p><strong>2. The target height is published.</strong> Without a source, the third
  quantity of the calculation is missing, and the coefficient cannot be
  established.</p>
</div>

<h2><span class="n">5</span>The calculation</h2>
<p>With <code>R</code>&#8239;=&#8239;6&#8239;371&#8239;km, <code>h</code> the eye
elevation and <code>d</code> the distance:</p>
<div class="eq">
  R&#8242; = R / (1 &#8722; k)&#160;&#160;&#160;&#160;
  a = &#8730;[(R&#8242;+h)&#178; &#8722; R&#8242;&#178;]&#160;&#160;&#160;&#160;
  c = &#8730;[R&#8242;&#178; + (d&#8722;a)&#178;] &#8722; R&#8242;
  <span class="cap">c is the height hidden at the target's base. If d &#8804; a the target is not hidden and the method does not apply.</span>
</div>
<p>The required coefficient is the one that makes <code>c</code> equal to the height of
the lowest point actually visible. It is solved by bisection on <code>k</code> between
0 and 1.</p>
<p>If the target's <strong>base</strong> is visible, the height of the lowest point is
zero. If only the <strong>top</strong> shows, it equals the target's full height.</p>
<table>
  <caption>Table 6 &#8212; Worked examples. Highlighted rows demand a sustained
  duct.</caption>
  <thead><tr><th class="n">eye</th><th class="n">target</th><th class="n">distance</th><th class="n">k required</th><th>regime</th></tr></thead>
  <tbody>
{t_exemples(fr)}
  </tbody>
</table>

<h2><span class="n">6</span>Shooting</h2>
<ol>
  <li><strong>Record</strong> the eye elevation, the time, the temperatures, and the
  visibility reported by the nearest aviation bulletin.</li>
  <li><strong>Film the target</strong> for thirty to sixty seconds at the telephoto
  setting, settings locked, manual fixed exposure, no cropping. Then a few raw
  stills.</li>
  <li><strong>Keep only the sharpest frames</strong> &#8212; one in twenty, one in
  fifty. At these distances turbulence makes the image boil several times per second; a
  single shot catches one instant at random.</li>
  <li><strong>Photograph the scene at wide angle</strong>, with near landmarks, so a
  third party can find the station again.</li>
  <li><strong>Identify the lowest visible point</strong> on the target and read its
  height above the base, using a marker whose height is published.</li>
</ol>
<p>One remark on choosing the day: aim for a cold dry air mass after a front has
passed, when the reported visibility exceeds the distance aimed at. On most days
nothing will be seen at these ranges, and that is not a result.</p>

<h2><span class="n">7</span>What is reported</h2>
<p>The test result is three lines: the <strong>required coefficient</strong>, the
<strong>regime</strong> from Table 1, and the <strong>length</strong> over which that
coefficient would have to hold &#8212; that is, the distance itself.</p>
<p>To these are added the three input quantities with their sources, the recorded
conditions, and the raw files. A record in which any one of the three quantities is
unsourced is not assessed.</p>
<p>The report states no conclusion about a model. It states a coefficient and a length,
and leaves each reader to judge whether the atmosphere produces them.</p>

""" + fiche(False, style=False)


def main():
    controle()
    modele = open(GABARIT, encoding="utf-8").read()
    i = modele.find('<div class="page">')
    entete = re.sub(r"<title>[^<]*</title>",
                    "<title>Quelle r&#233;fraction faudrait-il&#8239;?</title>",
                    modele[:i], count=1)
    open(CIBLE, "w", encoding="utf-8").write(
        entete + '<div class="page">\n'
        '<div class="langbar"><span class="on">FRAN&#199;AIS</span>'
        '<span>ENGLISH &#8212; seconde moiti&#233;</span></div>\n\n'
        + corps(True) +
        '\n\n<div class="langbar" style="break-before:page;page-break-before:always">'
        '<span>FRAN&#199;AIS &#8212; first half</span>'
        '<span class="on">ENGLISH</span></div>\n\n'
        + corps(False) + '\n</div>\n')
    print("Protocole écrit : content/protocoles/k-requis-bilingue.html")
    print("  plancher d'altitude : %d m aux deux extrémités" % H_PLANCHER)
    print("  exemples résolus :")
    for h, H, d in EXEMPLES:
        k = k_requis(h, H, d)
        print("    œil %5d m, cible %5d m, %3d km  →  k = %.3f  (%s)"
              % (h, H, d, k, regime(k, True)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
