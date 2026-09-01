#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Écrit « Le rayon apparent de la Terre, mesuré par visées terrestres ».

Pourquoi ce protocole
─────────────────────
Le site affirme que la photographie du Shkhara depuis Karagöl — 493,07 km — ne
s'explique pas sur une Terre de 6 371 km de rayon. Le calcul est juste : au
coefficient de réfraction optique standard k = 0,13, la sphère masque 5 341 m
d'un massif qui en fait 5 193. Rien ne devrait dépasser.

Mais ce calcul repose sur une valeur de k **supposée, jamais mesurée sur le
trajet**. Et c'est le terme dominant : +0,01 sur k retire 108 m de masquage,
quand +10 m d'erreur sur la hauteur d'œil n'en retirent que 13 et +1 km sur la
distance n'en ajoutent que 38. Affirmer qu'une observation est impossible, c'est
affirmer une valeur de k. Tant qu'elle n'est pas mesurée, l'affirmation ne vaut
pas plus que celle d'en face.

Ce que le protocole mesure
──────────────────────────
Une seule grandeur, le **rayon apparent** R′ = R/(1−k), qui réunit la courbure
du sol et celle du rayon lumineux. Aucun modèle n'est supposé ; on rapporte ce
que chacun en exige.

Méthode A — la visée réciproque, et c'est le cœur du document.
Deux stations intervisibles, distantes de d, mesurent simultanément leurs angles
zénithaux mutuels. Le résultat classique de géodésie donne

    z_A + z_B = 180° + γ − 2ρ      γ = d/R,  ρ = k·γ/2

d'où, en éliminant la réfraction :   R′ = d / (z_A + z_B − 180°)

La somme **ne dépend pas des altitudes** : une différence de hauteur agit sur
chaque angle mais s'annule dans la somme. Ne subsiste que la convergence des
verticales. Sur un plan, les verticales sont parallèles, γ = 0, et la somme vaut
EXACTEMENT 180° quelles que soient les altitudes des deux stations.

Le test est donc le **signe** de (z_A + z_B − 180°). Positif : les verticales
convergent. Nul : elles sont parallèles. Et la réfraction ne peut pas inverser
ce signe tant que k < 1 — elle ne fait que réduire l'écart.

À 10 km, l'écart attendu vaut de 4,7′ à 5,4′ selon k ; un théodolite lisant 5″
le sépare de zéro par plus de vingt sigma. C'est une mesure de terrain, pas une
expédition.

Méthode B — l'ajustement multi-cibles, pour aller là où la réciprocité est
impraticable : depuis une station, viser N sommets identifiés à des distances
connues et ajuster s(d) + C = (h − h_obs)/d − d/(2R′). Le zéro C du référentiel
est ajusté au lieu d'être exigé, ce qui supprime la contrainte du calage absolu
de l'horizontale.

La limite honnête : la déviation de la verticale
────────────────────────────────────────────────
Le fil à plomb suit la gravité, que les masses montagneuses dévient de quelques
dizaines de secondes d'arc. Les deux déviations ne s'annulent pas dans la somme.
C'est le seul systématique sérieux de la méthode A — et il se traite en
allongeant la base, puisque le signal croît avec d quand la déviation, elle, ne
croît pas.

Document bilingue, non publié : destiné à la relecture.
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
COEFS = [(0.00, "aucune réfraction", "no refraction"),
         (0.13, "standard optique (Gauss)", "standard optical (Gauss)"),
         (0.25, "standard radio, 4/3 R", "standard radio, 4/3 R"),
         (0.47, "inversion thermique forte", "strong thermal inversion")]
BASES = [2, 5, 10, 20, 50, 100]
PORTEES = [25, 50, 100, 150, 200, 300, 443, 493]
LECTURE_THEODOLITE = 5.0        # secondes d'arc
DEVIATION_VERTICALE = 30.0      # secondes d'arc, cas montagneux défavorable
BRUIT_SIM = 15.0


# ── Géométrie ────────────────────────────────────────────────────────────────
def rayon_apparent(k):
    return R / (1 - k)


def cachee(h_oeil, d, k):
    """Hauteur masquée depuis la base de la cible, en mètres."""
    Rp = rayon_apparent(k)
    h = h_oeil / 1000.0
    a = math.sqrt((Rp + h) ** 2 - Rp ** 2)
    return 0.0 if d <= a else (math.sqrt(Rp ** 2 + (d - a) ** 2) - Rp) * 1000.0


def k_pour_cachee(h_oeil, d, cible_m):
    lo, hi = 0.0, 0.99
    for _ in range(200):
        mid = (lo + hi) / 2
        if cachee(h_oeil, d, mid) > cible_m:
            lo = mid
        else:
            hi = mid
    return hi


def somme_zenithale_arcsec(d, k):
    """(z_A + z_B − 180°) en secondes d'arc, pour une base de d km."""
    return math.degrees(d / rayon_apparent(k)) * 3600


def courbure_arcmin(d, k):
    """Le terme d/(2R') d'un angle de site, en minutes d'arc."""
    return math.degrees(d / (2 * rayon_apparent(k))) * 60


# ── La simulation de la méthode B ────────────────────────────────────────────
CIBLES_SIM = [(30.0, 2600.0), (55.0, 3200.0), (85.0, 3800.0),
              (120.0, 4100.0), (160.0, 4500.0), (210.0, 4800.0)]
H_STATION = 2000.0


def ajuster(observations, h_obs):
    X = [d for d, _, _ in observations]
    Y = [s - (h - h_obs) / 1000.0 / d for d, h, s in observations]
    n = len(X)
    mx, my = sum(X) / n, sum(Y) / n
    B = (sum((x - mx) * (y - my) for x, y in zip(X, Y))
         / sum((x - mx) ** 2 for x in X))
    Rp = -1 / (2 * B)
    return Rp, 1 - R / Rp, B


def simuler(k_vrai, bruit, tirages, graine):
    import random
    import statistics
    rng = random.Random(graine)
    ks, pentes = [], []
    for _ in range(tirages):
        obs = []
        for d, h in CIBLES_SIM:
            vrai = (h - H_STATION) / 1000.0 / d
            if k_vrai is not None:
                vrai -= d / (2 * rayon_apparent(k_vrai))
            obs.append((d, h, vrai + math.radians(rng.gauss(0, bruit) / 3600)))
        Rp, k, B = ajuster(obs, H_STATION)
        ks.append(k)
        pentes.append(B)
    return (statistics.mean(ks), statistics.pstdev(ks),
            statistics.pstdev(pentes))


def controle_numerique():
    """Recalcule chaque valeur que le document imprime. Rien n'est écrit à la main."""
    h1, d1, hm1 = KARAGOL
    masque = cachee(h1, d1, 0.13)
    assert abs(masque - 5341) < 3, masque
    assert masque > hm1
    assert abs(cachee(h1, d1, 0.47) - 2008) < 3
    k_base = k_pour_cachee(h1, d1, 0.0)
    k_cime = k_pour_cachee(h1, d1, hm1)
    assert abs(k_base - 0.837) < 0.002, k_base
    assert abs(k_cime - 0.144) < 0.002, k_cime

    h2, d2, _ = FINESTRELLES
    assert abs(cachee(h2, d2, 0.13) - 3917) < 3
    assert abs(k_pour_cachee(h2, d2, 0.0) - 0.817) < 0.002

    assert abs(rayon_apparent(0.13) - 7323) < 2
    assert abs(rayon_apparent(k_base) - 39086) < 200
    assert abs(rayon_apparent(k_base) / R - 6.13) < 0.05

    for lib, ecart, attendu in (
            ("k +0,01", cachee(h1, d1, 0.14) - masque, -108),
            ("œil +10 m", cachee(h1 + 10, d1, 0.13) - masque, -13),
            ("distance +1 km", cachee(h1, d1 + 1, 0.13) - masque, +38)):
        assert abs(ecart - attendu) < 3, (lib, ecart)

    assert abs(somme_zenithale_arcsec(10, 0.13) / 60 - 4.69) < 0.02
    assert abs(somme_zenithale_arcsec(10, 0.47) / 60 - 2.86) < 0.02
    sigma = LECTURE_THEODOLITE * math.sqrt(2)
    assert abs(somme_zenithale_arcsec(10, 0.47) / sigma - 24.3) < 0.3

    ecart_200 = abs(courbure_arcmin(200, 0.13) - courbure_arcmin(200, 0.14)) * 60
    assert abs(ecart_200 - 32.4) < 0.5, ecart_200
    return k_base, k_cime, ecart_200


# ── Mise en forme ────────────────────────────────────────────────────────────
def nb(x, n, fr):
    return ("%.*f" % (n, x)).replace(".", "," if fr else ".")


def mil(x, fr):
    return "{:,.0f}".format(x).replace(",", "&#8239;")


def t_rayon(fr, k_base):
    out = []
    for k, lfr, len_ in COEFS:
        Rp = rayon_apparent(k)
        out.append(f'    <tr><td>{lfr if fr else len_}</td>'
                   f'<td class="n">{nb(k, 2, fr)}</td>'
                   f'<td class="n">{mil(Rp, fr)} km</td>'
                   f'<td class="n">{nb(Rp / R, 2, fr)} R</td></tr>')
    Rp = rayon_apparent(k_base)
    lib = ("exig&#233; par le clich&#233; de 493 km" if fr
           else "required by the 493 km photograph")
    out.append(f'    <tr class="hi"><td><strong>{lib}</strong></td>'
               f'<td class="n"><strong>{nb(k_base, 2, fr)}</strong></td>'
               f'<td class="n"><strong>{mil(Rp, fr)} km</strong></td>'
               f'<td class="n"><strong>{nb(Rp / R, 2, fr)} R</strong></td></tr>')
    plan = "mod&#232;le plan" if fr else "plane model"
    inf = "infini" if fr else "infinite"
    out.append(f'    <tr><td>{plan}</td><td class="n">&#8212;</td>'
               f'<td class="n">{inf}</td><td class="n">&#8734;</td></tr>')
    return "\n".join(out)


def t_reciproque(fr):
    out = []
    for d in BASES:
        cells = "".join(f'<td class="n">{nb(somme_zenithale_arcsec(d, k) / 60, 2, fr)}</td>'
                        for k, _, _ in COEFS)
        sig = somme_zenithale_arcsec(d, 0.47) / (LECTURE_THEODOLITE * math.sqrt(2))
        cls = ' class="hi"' if d == 10 else ""
        out.append(f'    <tr{cls}><td class="n">{d}</td>{cells}'
                   f'<td class="n">{nb(0.0, 2, fr)}</td>'
                   f'<td class="n">{nb(sig, 0, fr)}</td></tr>')
    return "\n".join(out)


def t_sensibilite(fr):
    h1, d1, _ = KARAGOL
    base = cachee(h1, d1, 0.13)
    lignes = [
        ("k : +0,01" if fr else "k: +0.01", cachee(h1, d1, 0.14) - base, True),
        ("k : +0,05" if fr else "k: +0.05", cachee(h1, d1, 0.18) - base, False),
        ("hauteur d'&#339;il : +10 m" if fr else "eye height: +10 m",
         cachee(h1 + 10, d1, 0.13) - base, False),
        ("hauteur d'&#339;il : +100 m" if fr else "eye height: +100 m",
         cachee(h1 + 100, d1, 0.13) - base, False),
        ("distance : +1 km" if fr else "distance: +1 km",
         cachee(h1, d1 + 1, 0.13) - base, False),
        ("distance : +10 km" if fr else "distance: +10 km",
         cachee(h1, d1 + 10, 0.13) - base, False),
    ]
    out = []
    for lib, dv, vedette in lignes:
        signe = "+" if dv > 0 else "&#8722;"
        txt = f"{signe}{nb(abs(dv), 0, fr)} m"
        if vedette:
            out.append(f'    <tr class="hi"><td><strong>{lib}</strong></td>'
                       f'<td class="n"><strong>{txt}</strong></td></tr>')
        else:
            out.append(f'    <tr><td>{lib}</td><td class="n">{txt}</td></tr>')
    return "\n".join(out)


def t_portee(fr):
    out = []
    for d in PORTEES:
        cells = "".join(f'<td class="n">{nb(courbure_arcmin(d, k), 1, fr)}</td>'
                        for k, _, _ in COEFS)
        cls = ' class="hi"' if d in (443, 493) else ""
        out.append(f'    <tr{cls}><td class="n">{d}</td>{cells}'
                   f'<td class="n">{nb(0.0, 1, fr)}</td></tr>')
    return "\n".join(out)


def corps(fr, k_base, k_cime, ecart_200, sim, sep):
    """Le corps du document dans une langue. Aucun nombre n'y est écrit à la main."""
    h1, d1, hm1 = KARAGOL
    h2, d2, hm2 = FINESTRELLES
    masque = cachee(h1, d1, 0.13)
    masque_f = cachee(h2, d2, 0.13)
    Rp_std, Rp_exige = rayon_apparent(0.13), rayon_apparent(k_base)
    rec10_std = somme_zenithale_arcsec(10, 0.13) / 60
    rec10_inv = somme_zenithale_arcsec(10, 0.47) / 60
    sig10 = somme_zenithale_arcsec(10, 0.47) / (LECTURE_THEODOLITE * math.sqrt(2))
    sig20 = somme_zenithale_arcsec(20, 0.47) / (LECTURE_THEODOLITE * math.sqrt(2))
    dev2 = 2 * DEVIATION_VERTICALE

    if fr:
        return f"""<div class="masthead">
  <div class="kicker">Protocole ouvert &#183; Pr&#233;dictions pr&#233;enregistr&#233;es &#183; Deux m&#233;thodes ind&#233;pendantes</div>
  <h1>Le rayon apparent de la Terre</h1>
  <p class="sub">Mesure par vis&#233;es terrestres, et ce qu'il faut pour qu'une vis&#233;e record soit opposable</p>
  <p class="dek">Deux th&#233;odolites, une base de dix kilom&#232;tres, une matin&#233;e. Sur un plan,
  la somme des angles z&#233;nithaux r&#233;ciproques vaut <strong>exactement 180&#176;</strong>&#160;;
  sur une sph&#232;re elle la d&#233;passe de {nb(rec10_inv, 2, fr)}&#8242; &#224; {nb(rec10_std, 2, fr)}&#8242;.
  S&#233;paration&#160;: {nb(sig10, 0, fr)}&#160;&#963;.</p>
  <div class="byline">
    <span>R&#233;dacteur<b>&nbsp;</b></span><span>Affiliation<b>&nbsp;</b></span>
    <span>Contact<b>&nbsp;</b></span><span>Version<b>1.0</b></span><span>Date<b>&nbsp;</b></span>
  </div>
</div>

<div class="abstract">
  <span class="lab">R&#233;sum&#233;</span>
  <p>Ce protocole ne d&#233;montre aucun mod&#232;le. Il mesure une grandeur&#160;: le
  <strong>rayon apparent</strong> <code>R&#8242; = R/(1&#8722;k)</code>, qui r&#233;unit la courbure du sol
  et celle du rayon lumineux, et il rapporte ce que chaque mod&#232;le en exige.</p>
  <p>Le litige sur les vis&#233;es record tient tout entier dans un nombre que personne n'a
  mesur&#233; sur le trajet&#160;: le coefficient de r&#233;fraction <code>k</code>. Sur la vis&#233;e
  Karag&#246;l&#8594;Shkhara ({nb(d1, 2, fr)} km), <strong>+0,01 sur k retire 108 m de masquage</strong>,
  quand +10 m d'erreur sur la hauteur d'&#339;il n'en retirent que 13, et +1 km sur la distance
  n'en ajoutent que 38. Affirmer qu'une observation est impossible, c'est affirmer une valeur
  de <code>k</code>&#160;; tant qu'elle n'est pas mesur&#233;e, l'affirmation ne p&#232;se pas plus que
  celle d'en face.</p>
  <p><strong>M&#233;thode A, la vis&#233;e r&#233;ciproque.</strong> Deux stations intervisibles distantes de
  <code>d</code> mesurent simultan&#233;ment leurs angles z&#233;nithaux mutuels. Le r&#233;sultat classique
  de g&#233;od&#233;sie donne <code>z<sub>A</sub> + z<sub>B</sub> = 180&#176; + &#947; &#8722; 2&#961;</code>,
  d'o&#249; <code>R&#8242; = d / (z<sub>A</sub> + z<sub>B</sub> &#8722; 180&#176;)</code>. <strong>Cette somme ne
  d&#233;pend pas des altitudes</strong>&#160;: une diff&#233;rence de hauteur agit sur chaque angle mais
  s'annule dans la somme. Ne subsiste que la convergence des verticales.</p>
  <p>Sur un plan les verticales sont parall&#232;les&#160;: la somme vaut <strong>exactement
  180&#176;</strong>, quelles que soient les altitudes et quelle que soit la r&#233;fraction. Le test
  est donc le <strong>signe</strong> de <code>z<sub>A</sub> + z<sub>B</sub> &#8722; 180&#176;</code>, et
  la r&#233;fraction ne peut pas l'inverser tant que <code>k &lt; 1</code>. Sur une base de 10 km
  l'&#233;cart attendu va de {nb(rec10_inv, 2, fr)}&#8242; &#224; {nb(rec10_std, 2, fr)}&#8242; selon <code>k</code>&#160;;
  un th&#233;odolite lisant 5&#8243; le s&#233;pare de z&#233;ro par {nb(sig10, 0, fr)}&#160;&#963;.</p>
  <p><strong>M&#233;thode B, l'ajustement multi-cibles</strong>, pour les port&#233;es o&#249; la
  r&#233;ciprocit&#233; est impraticable. Six sommets identifi&#233;s, une s&#233;rie d'angles de site, et
  l'ajustement de <code>s(d) + C = (h &#8722; h<sub>obs</sub>)/d &#8722; d/(2R&#8242;)</code>&#160;: le z&#233;ro
  <code>C</code> du r&#233;f&#233;rentiel est <strong>ajust&#233; au lieu d'&#234;tre exig&#233;</strong>. Simulation
  &#224; {nb(BRUIT_SIM, 0, fr)}&#8243; de bruit par vis&#233;e&#160;: <code>k</code> restitu&#233; &#224;
  <strong>&#177;{nb(sim[1], 3, fr)}</strong>, mod&#232;le plan s&#233;par&#233; de <strong>{nb(sep, 0, fr)}&#160;&#963;</strong>.</p>
</div>

<div class="box">
  <span class="lab">Ce que ce protocole n'&#233;tablit pas</span>
  <p>Il ne donne <strong>pas la forme de la Terre</strong>. Il donne <code>R&#8242;</code> le long
  d'un azimut, &#224; un moment, dans une masse d'air. C'est une mesure locale, et elle doit
  &#234;tre r&#233;p&#233;t&#233;e avant qu'on en tire quoi que ce soit de g&#233;n&#233;ral.</p>
  <p>Il ne <strong>valide pas r&#233;troactivement</strong> le clich&#233; de {nb(d1, 2, fr)} km. Cette
  photographie a &#233;t&#233; prise ailleurs, un autre jour, dans une autre atmosph&#232;re. Le
  protocole rend possible de refaire la vis&#233;e de mani&#232;re opposable&#160;; il ne s'y substitue
  pas. Tant qu'elle n'a pas &#233;t&#233; reprise sur place avec <code>k</code> mesur&#233;,
  <strong>ni son impossibilit&#233; ni sa validit&#233; ne sont &#233;tablies</strong> &#8212; et cela vaut
  contre nous autant que contre le mod&#232;le adverse.</p>
  <p>Il ne s&#233;pare pas la courbure du sol de celle du rayon. <code>R&#8242;</code> contient les
  deux, et seule une mesure ind&#233;pendante du profil thermique les d&#233;m&#234;lerait. C'est
  pourquoi le r&#233;sultat s'&#233;nonce en <code>R&#8242;</code> et jamais en
  &#171;&#160;rayon de la Terre&#160;&#187;.</p>
</div>

<h2><span class="n">01</span>L'observable&#160;: le rayon apparent</h2>
<p class="lead">Une vis&#233;e terrestre longue ne mesure pas la courbure du sol. Elle mesure la
courbure du sol <em>diminu&#233;e</em> de celle du rayon lumineux, et ces deux termes ne se
s&#233;parent pas dans une observation unique.</p>
<p>On les r&#233;unit donc dans une seule grandeur, le rayon apparent
<code>R&#8242; = R/(1&#8722;k)</code>, o&#249; <code>k</code> est le coefficient de r&#233;fraction. Toute la
g&#233;om&#233;trie d'une vis&#233;e s'&#233;crit avec <code>R&#8242;</code> seul. C'est lui qu'on mesure&#160;; c'est
lui que les mod&#232;les doivent affronter.</p>
<div class="eq">
  R&#8242; = R / (1 &#8722; k)
  <span class="cap">La r&#233;fraction &#233;quivaut &#224; une Terre plus grande et plus plate. k = 0 : aucun effet. k = 1 : le rayon suit exactement la surface.</span>
</div>
<table>
  <caption>Tableau 1 &#8212; Le rayon apparent selon la r&#233;fraction. La derni&#232;re ligne est le
  mod&#232;le plan, o&#249; aucune convergence des verticales n'existe.</caption>
  <thead><tr><th>r&#233;gime</th><th class="n">k</th><th class="n">R&#8242;</th><th class="n">en rayons terrestres</th></tr></thead>
  <tbody>
{t_rayon(fr, k_base)}
  </tbody>
</table>

<h2><span class="n">02</span>Pourquoi les clich&#233;s existants ne tranchent pas</h2>
<p class="lead">Le calcul que l'on oppose &#224; ces photographies est juste. Ce qui manque, c'est
la seule quantit&#233; dont il d&#233;pend vraiment.</p>
<p>Sur la vis&#233;e Karag&#246;l&#8594;Shkhara &#8212; hauteur d'&#339;il {mil(h1, fr)} m, distance
{nb(d1, 2, fr)} km, massif de {mil(hm1, fr)} m &#8212; la sph&#232;re au coefficient optique standard
<code>k = 0,13</code> masque <strong>{mil(masque, fr)} m</strong> depuis la base. C'est davantage que la
hauteur du massif&#160;: rien ne devrait d&#233;passer. Sur la vis&#233;e Finestrelles&#8594;Barre des
&#201;crins, elle en masque {mil(masque_f, fr)} m sur {mil(hm2, fr)}, ne laissant affleurer que
{nb(hm2 - masque_f, 0, fr)} m de cime.</p>
<p>Mais ce r&#233;sultat suit la valeur de <code>k</code>, et rien d'autre ne p&#232;se autant.</p>
<table>
  <caption>Tableau 2 &#8212; Ce que change chaque erreur, sur la vis&#233;e de {nb(d1, 2, fr)} km,
  autour de <code>k = 0,13</code>. Une seule ligne domine.</caption>
  <thead><tr><th>&#233;cart introduit</th><th class="n">variation du masquage</th></tr></thead>
  <tbody>
{t_sensibilite(fr)}
  </tbody>
</table>
<div class="box warn">
  <span class="lab">Le c&#339;ur du litige</span>
  <p>Pour que la base du Shkhara redevienne visible, il faudrait <code>k = {nb(k_base, 3, fr)}</code>,
  soit un rayon apparent de {mil(Rp_exige, fr)} km &#8212; <strong>{nb(Rp_exige / R, 1, fr)} fois le rayon
  terrestre</strong>, tenu sur cinq cents kilom&#232;tres. Pour que la seule cime affleure, il
  suffirait de <code>k = {nb(k_cime, 3, fr)}</code>.</p>
  <p>Ces deux nombres bornent le d&#233;bat, et <strong>aucun des deux camps ne les a
  mesur&#233;s</strong>. Nous affirmons que la premi&#232;re valeur est inatteignable&#160;; c'est
  probable, mais nous ne l'avons pas mesur&#233;e sur ce trajet, et nous ne disposons pour cette
  observation que de ce que son auteur a publi&#233; &#8212; une image, une distance, deux altitudes.
  C'est exactement le reproche que nous adressons &#224; l'argumentaire adverse.</p>
</div>

<h2 class="brk"><span class="n">03</span>M&#233;thode A &#8212; la vis&#233;e r&#233;ciproque</h2>
<p class="lead">C'est la mesure la plus propre du document, et la moins co&#251;teuse&#160;: elle ne
demande ni longue portée, ni altitude, ni conditions exceptionnelles.</p>
<p>Deux stations A et B, intervisibles, s&#233;par&#233;es de <code>d</code>. Chacune mesure au m&#234;me
instant l'angle z&#233;nithal vers l'autre. Si <code>&#947; = d/R</code> est l'angle au centre et
<code>&#961;</code> la r&#233;fraction &#224; chaque extr&#233;mit&#233;&#160;:</p>
<div class="eq">
  z<sub>A</sub> + z<sub>B</sub> = 180&#176; + &#947; &#8722; 2&#961;
  <span class="cap">R&#233;sultat classique de la g&#233;od&#233;sie. En posant &#961; = k&#947;/2, il vient R&#8242; = d / (z<sub>A</sub> + z<sub>B</sub> &#8722; 180&#176;).</span>
</div>
<p>Deux propri&#233;t&#233;s font la force de cette &#233;galit&#233;.</p>
<p><strong>La somme ne d&#233;pend pas des altitudes.</strong> Une diff&#233;rence de hauteur entre A et B
augmente l'un des angles d'autant qu'elle diminue l'autre&#160;; elle dispara&#238;t de la somme. Il
ne reste que l'angle dont les deux verticales locales divergent. On n'a donc besoin de conna&#238;tre
ni l'altitude des stations, ni leur d&#233;nivel&#233;.</p>
<p><strong>Le signe suffit &#224; trancher.</strong> Sur un plan, les verticales sont parall&#232;les&#160;:
<code>&#947; = 0</code>, et la somme vaut <strong>exactement 180&#176;</strong>. Sur une surface courbe elle
la d&#233;passe. La r&#233;fraction ne fait que r&#233;duire l'&#233;cart&#160;: elle ne peut l'annuler ni
l'inverser tant que <code>k &lt; 1</code>, c'est-&#224;-dire tant que le rayon lumineux se courbe moins
que la surface. On n'a donc <strong>pas besoin de conna&#238;tre <code>k</code></strong> pour lire le
r&#233;sultat &#8212; on le d&#233;duit ensuite.</p>
<table>
  <caption>Tableau 3 &#8212; &#201;cart attendu <code>z<sub>A</sub> + z<sub>B</sub> &#8722; 180&#176;</code>, en
  minutes d'arc. La derni&#232;re colonne donne la s&#233;paration d'avec z&#233;ro pour deux th&#233;odolites
  lisant 5&#8243;, dans le cas le plus favorable au mod&#232;le plan (k = 0,47).</caption>
  <thead><tr><th class="n">base (km)</th><th class="n">k = 0</th><th class="n">k = 0,13</th><th class="n">k = 0,25</th><th class="n">k = 0,47</th><th class="n">plan</th><th class="n">&#963;</th></tr></thead>
  <tbody>
{t_reciproque(fr)}
  </tbody>
</table>
<div class="box warn">
  <span class="lab">La d&#233;viation de la verticale &#8212; le seul syst&#233;matique s&#233;rieux</span>
  <p>Le fil &#224; plomb suit la gravit&#233;, que les masses montagneuses d&#233;tournent de quelques
  dizaines de secondes d'arc. Les deux d&#233;viations <strong>ne s'annulent pas</strong> dans la
  somme&#160;: elles s'y ajoutent. Dans un cas montagneux d&#233;favorable, {nb(DEVIATION_VERTICALE, 0, fr)}&#8243;
  &#224; chaque station font {nb(dev2, 0, fr)}&#8243; de biais possible.</p>
  <p>Le traitement est direct&#160;: <strong>allonger la base</strong>. Le signal cro&#238;t
  proportionnellement &#224; <code>d</code>, la d&#233;viation ne cro&#238;t pas. &#192; 10 km le signal vaut
  {nb(somme_zenithale_arcsec(10, 0.47), 0, fr)}&#8243; dans le cas le plus d&#233;favorable, soit
  {nb(somme_zenithale_arcsec(10, 0.47) / dev2, 1, fr)} fois le biais&#160;; &#224; 20 km,
  {nb(somme_zenithale_arcsec(20, 0.47) / dev2, 1, fr)} fois. Second traitement&#160;: choisir des
  stations en terrain peu accident&#233;, o&#249; la d&#233;viation tombe &#224; quelques secondes, ou corriger
  par une grille publi&#233;e de d&#233;viations lorsqu'il en existe une pour la r&#233;gion.</p>
</div>

<h2><span class="n">04</span>M&#233;thode B &#8212; l'ajustement multi-cibles</h2>
<p class="lead">La r&#233;ciprocit&#233; exige deux &#233;quipes et deux instruments. Sur les grandes
port&#233;es, elle devient impraticable. On la remplace par une station unique et plusieurs cibles.</p>
<p>Depuis une station d'altitude <code>h<sub>obs</sub></code>, on vise N sommets identifi&#233;s, de
hauteurs <code>h<sub>i</sub></code> et de distances <code>d<sub>i</sub></code> connues par leurs
coordonn&#233;es. L'angle de site mesur&#233; s'&#233;crit&#160;:</p>
<div class="eq">
  s(d) + C = (h &#8722; h<sub>obs</sub>)/d &#8722; d/(2R&#8242;)
  <span class="cap">C est le z&#233;ro inconnu du r&#233;f&#233;rentiel. Il est ajust&#233; avec R&#8242; au lieu d'&#234;tre exig&#233;.</span>
</div>
<p>C'est le point d&#233;cisif de la m&#233;thode. Le calage absolu de l'horizontale est la
contrainte la plus difficile de toute la m&#233;trologie de terrain&#160;: bulle mal r&#233;gl&#233;e, capteur
inclin&#233;, horizon artificiel asservi. Ici, <strong>l'erreur de z&#233;ro est absorb&#233;e par
<code>C</code></strong>, qu'on ajuste. Il suffit que le z&#233;ro reste <em>stable</em> pendant la
s&#233;rie, ce qui est infiniment plus facile que d'&#234;tre juste.</p>
<p>Deux param&#232;tres, N cibles&#160;: d&#232;s N = 4 l'ajustement est surd&#233;termin&#233;, et
<strong>les r&#233;sidus disent si un seul <code>k</code> rend compte de toute la s&#233;rie</strong>. S'ils
ne sont pas al&#233;atoires, la r&#233;fraction n'est pas homog&#232;ne le long des vis&#233;es, et le r&#233;sultat
doit &#234;tre &#233;nonc&#233; comme tel plut&#244;t que moyenn&#233;.</p>
<table>
  <caption>Tableau 4 &#8212; Terme de courbure <code>d/(2R&#8242;)</code> d'un angle de site, en minutes
  d'arc. Les deux lignes surlign&#233;es sont les vis&#233;es record.</caption>
  <thead><tr><th class="n">port&#233;e (km)</th><th class="n">k = 0</th><th class="n">k = 0,13</th><th class="n">k = 0,25</th><th class="n">k = 0,47</th><th class="n">plan</th></tr></thead>
  <tbody>
{t_portee(fr)}
  </tbody>
</table>
<div class="box key">
  <span class="lab">Ce que donne la simulation</span>
  <p>Six cibles entre 30 et 210 km depuis une station &#224; {mil(H_STATION, fr)} m, bruit gaussien de
  {nb(BRUIT_SIM, 0, fr)}&#8243; sur chaque vis&#233;e, 400 tirages&#160;: <code>k</code> est restitu&#233; &#224;
  <strong>&#177;{nb(sim[1], 3, fr)}</strong> &#8212; mieux que le &#177;0,01 exig&#233; par le tableau 2. Et une
  s&#233;rie engendr&#233;e sur un plan se s&#233;pare de la pente sph&#233;rique la plus favorable au plan
  (k = 0,47) par <strong>{nb(sep, 0, fr)}&#160;&#963;</strong>.</p>
  <p>La pr&#233;cision angulaire &#224; tenir pour distinguer <code>k</code> &#224; &#177;0,01 vaut
  {nb(ecart_200, 1, fr)}&#8243; &#224; 200 km de port&#233;e, soit une dizaine de pixels &#224; 400 mm sur capteur
  plein format. Un th&#233;odolite de chantier fait dix fois mieux.</p>
</div>

<h2 class="brk"><span class="n">05</span>L'identification des cibles</h2>
<p class="lead">C'est la faute la plus fr&#233;quente des vis&#233;es longues, et la plus silencieuse&#160;:
un sommet mal identifi&#233; change tout, sans que rien dans l'image ne le signale.</p>
<p>Le crit&#232;re ne doit rien devoir au mod&#232;le vertical qu'on teste. On emploie donc
l'<strong>azimut</strong>, grandeur horizontale, que l'on compare au relèvement calcul&#233; depuis
les coordonn&#233;es des deux points.</p>
<ol>
  <li><strong>Mesurer l'azimut</strong> de chaque cible au th&#233;odolite, r&#233;f&#233;renc&#233; &#224; une
  direction connue &#8212; une mire g&#233;od&#233;sique, ou une vis&#233;e solaire r&#233;duite par &#233;ph&#233;m&#233;ride.</li>
  <li><strong>Calculer le relèvement</strong> station&#8594;cible sur l'ellipso&#239;de, &#224; partir des
  coordonn&#233;es publi&#233;es. C'est une op&#233;ration purement horizontale&#160;: elle ne suppose rien de
  la courbure verticale.</li>
  <li><strong>Exiger l'unicit&#233;</strong>&#160;: l'&#233;cart mesur&#233;&#8722;calcul&#233; doit rester sous 0,05&#176;,
  et <strong>aucun autre sommet candidat</strong> ne doit se trouver dans une fen&#234;tre de
  &#177;0,2&#176; autour de l'azimut mesur&#233;. Une cible qui &#233;choue &#224; ce test est &#233;cart&#233;e de
  l'ajustement, pas r&#233;interpr&#233;t&#233;e.</li>
  <li><strong>Consigner la sc&#232;ne enti&#232;re</strong>&#160;: un panoramique large, non recadr&#233;, o&#249;
  figurent des rep&#232;res proches identifiables, permet &#224; un tiers de refaire l'identification
  sans nous croire sur parole.</li>
</ol>

<h2><span class="n">06</span>Mat&#233;riel et stations</h2>
<ul>
  <li><strong>M&#233;thode A</strong>&#160;: deux th&#233;odolites ou stations totales lisant 5&#8243; ou mieux,
  avec compensateur bi-axial. Deux op&#233;rateurs, deux montres synchronis&#233;es par GNSS.</li>
  <li><strong>M&#233;thode B</strong>&#160;: un th&#233;odolite, ou un bo&#238;tier plein format sur monture
  ferme avec t&#233;l&#233;objectif de 300 &#224; 600 mm, bague de zoom et mise au point immobilis&#233;es
  m&#233;caniquement pour toute la s&#233;rie.</li>
  <li><strong>Position</strong>&#160;: r&#233;cepteur GNSS bifr&#233;quence, ou point g&#233;od&#233;sique
  mat&#233;rialis&#233;. La hauteur d'instrument se mesure au ruban et se consigne.</li>
  <li><strong>Atmosph&#232;re</strong>&#160;: temp&#233;rature, pression et humidit&#233; &#224; chaque station, au
  d&#233;but et &#224; la fin. Ces valeurs ne servent pas &#224; corriger &#8212; elles servent &#224; d&#233;crire les
  conditions sous lesquelles <code>R&#8242;</code> a &#233;t&#233; trouv&#233;.</li>
</ul>

<h2><span class="n">07</span>Proc&#233;dure</h2>
<ol>
  <li><strong>Choisir la fen&#234;tre horaire</strong>&#160;: milieu de journ&#233;e, gradient thermique
  &#233;tabli, plut&#244;t que l'aube o&#249; l'inversion est forte et instable. On veut une atmosph&#232;re
  <em>stable</em>, pas une atmosph&#232;re favorable.</li>
  <li><strong>M&#233;thode A &#8212; s&#233;rie r&#233;ciproque.</strong> Dix pointés altern&#233;s cercle
  gauche / cercle droit &#224; chaque station, dans la m&#234;me minute. L'alternance des cercles
  &#233;limine l'erreur de collimation verticale.</li>
  <li><strong>R&#233;p&#233;ter la s&#233;rie r&#233;ciproque trois fois</strong>, espac&#233;es d'une heure. Un
  <code>R&#8242;</code> qui d&#233;rive entre les s&#233;ries mesure la variation de la r&#233;fraction&#160;; c'est
  une information, pas un &#233;chec.</li>
  <li><strong>M&#233;thode B &#8212; balayage.</strong> Sans toucher au calage, viser les N cibles dans
  l'ordre croissant des distances, puis dans l'ordre d&#233;croissant. La comparaison aller/retour
  d&#233;tecte une d&#233;rive du z&#233;ro pendant la s&#233;rie.</li>
  <li><strong>Ne rien recadrer, ne rien redresser.</strong> Les fichiers bruts sont
  conserv&#233;s et publi&#233;s avec le r&#233;sultat, quel qu'il soit.</li>
</ol>
<div class="box warn">
  <span class="lab">Crit&#232;re de rejet</span>
  <p><strong>M&#233;thode A</strong>&#160;: si les trois s&#233;ries r&#233;ciproques donnent des
  <code>R&#8242;</code> dont l'&#233;cart d&#233;passe trois fois l'incertitude de lecture, la r&#233;fraction a
  chang&#233; pendant la mesure. La journ&#233;e est rapport&#233;e comme telle, avec les trois valeurs.</p>
  <p><strong>M&#233;thode B</strong>&#160;: si l'&#233;cart aller/retour sur une m&#234;me cible d&#233;passe
  3&#963;, le z&#233;ro a d&#233;riv&#233; et la s&#233;rie est refaite. Si les r&#233;sidus de l'ajustement montrent une
  tendance au lieu d'&#234;tre al&#233;atoires, un seul <code>k</code> ne suffit pas&#160;: on le dit, on ne
  moyenne pas.</p>
</div>

<h2 class="brk"><span class="n">08</span>Ce que la mesure &#233;tablit</h2>
<p class="lead">Le r&#233;sultat est un nombre assorti de son incertitude, et la liste de ce que
chaque mod&#232;le en exige. Il n'y a pas de verdict &#224; rendre, seulement une valeur &#224; publier.</p>
<div class="two">
  <div class="vc g">
    <p class="h">z<sub>A</sub> + z<sub>B</sub> &#8722; 180&#176; &gt; 0</p>
    <p class="v">Les verticales convergent</p>
    <p>La surface est courbe le long de cette base, et <code>R&#8242;</code> mesure de combien.
    Aucune valeur de <code>k</code> inf&#233;rieure &#224; 1 ne peut produire ce signe sur un plan.</p>
  </div>
  <div class="vc p">
    <p class="h">z<sub>A</sub> + z<sub>B</sub> &#8722; 180&#176; = 0</p>
    <p class="v">Les verticales sont parall&#232;les</p>
    <p>C'est ce que pr&#233;dit le plan, exactement et sans param&#232;tre libre. Sur une base de
    10 km, la sph&#232;re en est &#233;loign&#233;e de {nb(sig10, 0, fr)}&#160;&#963; dans le cas qui lui est le
    plus d&#233;favorable&#160;; sur 20 km, de {nb(sig20, 0, fr)}&#160;&#963;.</p>
  </div>
</div>
<p>Dans les deux cas, la valeur de <code>R&#8242;</code> et son incertitude sont publi&#233;es avec les
conditions atmosph&#233;riques, l'azimut, la base, l'heure et les fichiers bruts. Une seule mesure
ne d&#233;crit qu'une ligne de vis&#233;e dans une masse d'air&#160;; c'est leur accumulation, sur des
azimuts et des saisons diff&#233;rents, qui a de la valeur.</p>

<h2><span class="n">09</span>Refaire les vis&#233;es record</h2>
<p class="lead">C'est l'objet final, et il faut dire &#224; quelles conditions une telle vis&#233;e
deviendrait opposable.</p>
<p>Une photographie &#224; {nb(d1, 2, fr)} km n'a de valeur probante que si elle est accompagn&#233;e de
ce que les clich&#233;s existants ne fournissent pas&#160;:</p>
<ol>
  <li><strong>La position et la hauteur d'&#339;il</strong> par GNSS, avec l'incertitude verticale.</li>
  <li><strong>L'azimut mesur&#233;</strong> de la cible, et la d&#233;monstration d'unicit&#233; de la
  section 05.</li>
  <li><strong>Une mesure de <code>k</code> le long du m&#234;me azimut</strong>, le m&#234;me jour, par la
  m&#233;thode A sur une base courte ou par la m&#233;thode B sur des cibles interm&#233;diaires. Sans elle,
  le clich&#233; ne d&#233;montre rien, quel que soit le camp qui l'invoque.</li>
  <li><strong>L'angle de site du point le plus bas visible</strong> sur le massif, et non une
  appr&#233;ciation visuelle de &#171;&#160;on voit la base&#160;&#187;. C'est cette grandeur-l&#224; qui se
  compare au calcul.</li>
  <li><strong>Les fichiers bruts</strong> et la focale, publi&#233;s.</li>
</ol>
<div class="box">
  <span class="lab">Ce que nous nous engageons &#224; publier</span>
  <p>Si une campagne men&#233;e selon ce protocole trouve un <code>R&#8242;</code> compatible avec une
  Terre sph&#233;rique et une r&#233;fraction ordinaire, ce r&#233;sultat sera publi&#233; tel quel, avec les
  donn&#233;es brutes, et les pages du site qui affirment l'inverse seront corrig&#233;es. Un protocole
  dont on n'accepte qu'une issue n'est pas un protocole.</p>
</div>

<h2><span class="n">10</span>Objections anticip&#233;es</h2>
<ol>
  <li><strong>&#171;&#160;La r&#233;fraction peut tout expliquer.&#160;&#187;</strong> Elle peut r&#233;duire
  l'&#233;cart de la m&#233;thode A, jamais en inverser le signe, tant que <code>k &lt; 1</code>. Et c'est
  pr&#233;cis&#233;ment ce que la mesure fournit&#160;: la valeur de <code>k</code>, au lieu de l'invoquer.</li>
  <li><strong>&#171;&#160;Vos th&#233;odolites sont r&#233;gl&#233;s sur une Terre sph&#233;rique.&#160;&#187;</strong>
  Un th&#233;odolite mesure des angles par rapport &#224; la verticale locale, mat&#233;rialis&#233;e par un
  compensateur &#224; gravit&#233;. Aucune constante de rayon terrestre n'entre dans la lecture. La
  m&#233;thode A n'utilise ensuite que la somme de deux lectures et la distance.</li>
  <li><strong>&#171;&#160;La d&#233;viation de la verticale ruine la mesure.&#160;&#187;</strong> Elle la
  biaise, et le document la chiffre plut&#244;t que de l'ignorer. Elle est born&#233;e et ne cro&#238;t pas
  avec la base, quand le signal cro&#238;t proportionnellement&#160;: c'est pourquoi la base
  recommand&#233;e est de 20 km plut&#244;t que de 2.</li>
  <li><strong>&#171;&#160;Le mod&#232;le plan pr&#233;dit aussi une disparition par perspective.&#160;&#187;</strong>
  La perspective agit sur la <em>position</em> angulaire, pas sur la convergence des verticales.
  La m&#233;thode A ne mesure que cette convergence, et le plan lui assigne z&#233;ro sans param&#232;tre
  ajustable.</li>
  <li><strong>&#171;&#160;Une seule base ne prouve rien.&#160;&#187;</strong> Exact, et c'est &#233;crit dans
  l'encadr&#233; de bornage. Ce protocole donne <code>R&#8242;</code> sur une ligne&#160;; il faut le
  r&#233;p&#233;ter.</li>
</ol>

<h2><span class="n">11</span>Colophon</h2>
<p>Valeurs de r&#233;f&#233;rence&#160;: rayon terrestre 6&#8239;371 km&#160;; vis&#233;e Karag&#246;l&#8594;Shkhara
{mil(h1, fr)} m / {nb(d1, 2, fr)} km / {mil(hm1, fr)} m&#160;; vis&#233;e Finestrelles&#8594;Barre des
&#201;crins {mil(h2, fr)} m / {nb(d2, 0, fr)} km / {mil(hm2, fr)} m. Le document se reconstruit
enti&#232;rement depuis ces valeurs et les relations
<code>R&#8242; = R/(1&#8722;k)</code> et
<code>z<sub>A</sub> + z<sub>B</sub> &#8722; 180&#176; = d/R&#8242;</code>. &#8212; Protocole ouvert, version 1.0.</p>"""

    return f"""<div class="masthead">
  <div class="kicker">Open protocol &#183; Pre-registered predictions &#183; Two independent methods</div>
  <h1>The Earth's apparent radius</h1>
  <p class="sub">Measured by terrestrial sight lines, and what a record sight line needs to be contestable</p>
  <p class="dek">Two theodolites, a ten-kilometre baseline, one morning. On a plane the sum of
  reciprocal zenith angles is <strong>exactly 180&#176;</strong>; on a sphere it exceeds it by
  {nb(rec10_inv, 2, fr)}&#8242; to {nb(rec10_std, 2, fr)}&#8242;. Separation: {nb(sig10, 0, fr)}&#160;&#963;.</p>
  <div class="byline">
    <span>Author<b>&nbsp;</b></span><span>Affiliation<b>&nbsp;</b></span>
    <span>Contact<b>&nbsp;</b></span><span>Version<b>1.0</b></span><span>Date<b>&nbsp;</b></span>
  </div>
</div>

<div class="abstract">
  <span class="lab">Abstract</span>
  <p>This protocol demonstrates no model. It measures a quantity: the <strong>apparent
  radius</strong> <code>R&#8242; = R/(1&#8722;k)</code>, which combines the curvature of the ground with
  that of the light ray, and it reports what each model requires of it.</p>
  <p>The dispute over record sight lines rests entirely on one number nobody has measured along
  the path: the refraction coefficient <code>k</code>. On the Karag&#246;l&#8594;Shkhara line
  ({nb(d1, 2, fr)} km), <strong>+0.01 in k removes 108 m of hiding</strong>, whereas a +10 m error
  in eye height removes only 13, and +1 km in distance adds only 38. To declare an observation
  impossible is to assert a value of <code>k</code>; until it is measured, the assertion weighs
  no more than the opposing one.</p>
  <p><strong>Method A, the reciprocal sight.</strong> Two intervisible stations a distance
  <code>d</code> apart measure their mutual zenith angles simultaneously. The classical geodetic
  result gives <code>z<sub>A</sub> + z<sub>B</sub> = 180&#176; + &#947; &#8722; 2&#961;</code>, hence
  <code>R&#8242; = d / (z<sub>A</sub> + z<sub>B</sub> &#8722; 180&#176;)</code>. <strong>That sum does not
  depend on the altitudes</strong>: a height difference raises one angle exactly as much as it
  lowers the other, and cancels. Only the convergence of the two local verticals survives.</p>
  <p>On a plane the verticals are parallel: the sum is <strong>exactly 180&#176;</strong>, whatever
  the altitudes and whatever the refraction. The test is therefore the <strong>sign</strong> of
  <code>z<sub>A</sub> + z<sub>B</sub> &#8722; 180&#176;</code>, and refraction cannot reverse it as long
  as <code>k &lt; 1</code>. Over a 10 km baseline the expected gap runs from {nb(rec10_inv, 2, fr)}&#8242;
  to {nb(rec10_std, 2, fr)}&#8242; depending on <code>k</code>; two theodolites reading 5&#8243; separate
  it from zero by {nb(sig10, 0, fr)}&#160;&#963;.</p>
  <p><strong>Method B, the multi-target fit</strong>, for ranges where reciprocity is
  impractical. Six identified summits, one run of elevation angles, and a fit of
  <code>s(d) + C = (h &#8722; h<sub>obs</sub>)/d &#8722; d/(2R&#8242;)</code>: the reference zero <code>C</code>
  is <strong>fitted rather than required</strong>. Simulated at {nb(BRUIT_SIM, 0, fr)}&#8243; of noise
  per sight: <code>k</code> recovered to <strong>&#177;{nb(sim[1], 3, fr)}</strong>, plane model
  separated by <strong>{nb(sep, 0, fr)}&#160;&#963;</strong>.</p>
</div>

<div class="box">
  <span class="lab">What this protocol does not establish</span>
  <p>It does <strong>not give the shape of the Earth</strong>. It gives <code>R&#8242;</code> along
  one azimuth, at one moment, through one air mass. That is a local measurement and must be
  repeated before anything general is drawn from it.</p>
  <p>It does <strong>not retroactively validate</strong> the {nb(d1, 2, fr)} km photograph. That
  picture was taken elsewhere, on another day, through another atmosphere. The protocol makes it
  possible to redo the sight line in a contestable way; it is not a substitute for doing so.
  Until the line has been re-shot on site with <code>k</code> measured, <strong>neither its
  impossibility nor its validity is established</strong> &#8212; and that cuts against us as much
  as against the opposing model.</p>
  <p>It does not separate the curvature of the ground from that of the ray. <code>R&#8242;</code>
  contains both, and only an independent measurement of the thermal profile would disentangle
  them. That is why the result is stated as <code>R&#8242;</code> and never as
  &#8220;the radius of the Earth&#8221;.</p>
</div>

<h2><span class="n">01</span>The observable: the apparent radius</h2>
<p class="lead">A long terrestrial sight line does not measure the curvature of the ground. It
measures the curvature of the ground <em>less</em> that of the light ray, and those two terms do
not separate in a single observation.</p>
<p>They are therefore combined into one quantity, the apparent radius
<code>R&#8242; = R/(1&#8722;k)</code>, where <code>k</code> is the refraction coefficient. The whole
geometry of a sight line can be written with <code>R&#8242;</code> alone. It is what one measures; it
is what the models must confront.</p>
<div class="eq">
  R&#8242; = R / (1 &#8722; k)
  <span class="cap">Refraction is equivalent to a larger, flatter Earth. k = 0: no effect. k = 1: the ray follows the surface exactly.</span>
</div>
<table>
  <caption>Table 1 &#8212; The apparent radius by refraction regime. The last row is the plane
  model, where no convergence of the verticals exists.</caption>
  <thead><tr><th>regime</th><th class="n">k</th><th class="n">R&#8242;</th><th class="n">in Earth radii</th></tr></thead>
  <tbody>
{t_rayon(fr, k_base)}
  </tbody>
</table>

<h2><span class="n">02</span>Why the existing photographs settle nothing</h2>
<p class="lead">The calculation set against these photographs is correct. What is missing is the
only quantity it truly depends on.</p>
<p>On the Karag&#246;l&#8594;Shkhara line &#8212; eye height {mil(h1, fr)} m, distance {nb(d1, 2, fr)} km,
massif {mil(hm1, fr)} m &#8212; the sphere at the standard optical coefficient <code>k = 0.13</code>
hides <strong>{mil(masque, fr)} m</strong> measured from the base. That is more than the height of
the massif: nothing should show. On the Finestrelles&#8594;Barre des &#201;crins line it hides
{mil(masque_f, fr)} m out of {mil(hm2, fr)}, leaving only {nb(hm2 - masque_f, 0, fr)} m of summit.</p>
<p>But that result follows the value of <code>k</code>, and nothing else weighs as much.</p>
<table>
  <caption>Table 2 &#8212; What each error changes, on the {nb(d1, 2, fr)} km line, around
  <code>k = 0.13</code>. One row dominates.</caption>
  <thead><tr><th>error introduced</th><th class="n">change in hiding</th></tr></thead>
  <tbody>
{t_sensibilite(fr)}
  </tbody>
</table>
<div class="box warn">
  <span class="lab">The heart of the dispute</span>
  <p>For the base of Shkhara to become visible again, <code>k = {nb(k_base, 3, fr)}</code> would be
  required &#8212; an apparent radius of {mil(Rp_exige, fr)} km, <strong>{nb(Rp_exige / R, 1, fr)} times
  the Earth's radius</strong>, sustained over five hundred kilometres. For the summit alone to
  graze, <code>k = {nb(k_cime, 3, fr)}</code> would suffice.</p>
  <p>Those two numbers bound the debate, and <strong>neither camp has measured them</strong>. We
  assert that the first is unreachable; that is likely, but we have not measured it on that path,
  and for this observation we hold only what its author published &#8212; an image, a distance, two
  altitudes. Which is precisely the reproach we address to the opposing case.</p>
</div>

<h2 class="brk"><span class="n">03</span>Method A &#8212; the reciprocal sight</h2>
<p class="lead">This is the cleanest measurement in the document, and the cheapest: it demands no
long range, no altitude, no exceptional conditions.</p>
<p>Two intervisible stations A and B, separated by <code>d</code>. Each measures, at the same
instant, the zenith angle to the other. With <code>&#947; = d/R</code> the angle at the centre and
<code>&#961;</code> the refraction at each end:</p>
<div class="eq">
  z<sub>A</sub> + z<sub>B</sub> = 180&#176; + &#947; &#8722; 2&#961;
  <span class="cap">Classical geodetic result. Setting &#961; = k&#947;/2 gives R&#8242; = d / (z<sub>A</sub> + z<sub>B</sub> &#8722; 180&#176;).</span>
</div>
<p>Two properties give this identity its force.</p>
<p><strong>The sum does not depend on the altitudes.</strong> A height difference between A and B
raises one angle exactly as much as it lowers the other; it drops out of the sum. What remains is
the angle by which the two local verticals diverge. Neither the stations' altitudes nor their
height difference need to be known.</p>
<p><strong>The sign alone decides.</strong> On a plane the verticals are parallel:
<code>&#947; = 0</code>, and the sum is <strong>exactly 180&#176;</strong>. On a curved surface it exceeds
it. Refraction only reduces the gap: it cannot cancel or reverse it as long as <code>k &lt; 1</code>,
that is, as long as the ray bends less than the surface. One therefore <strong>does not need to
know <code>k</code></strong> to read the result &#8212; it is deduced afterwards.</p>
<table>
  <caption>Table 3 &#8212; Expected gap <code>z<sub>A</sub> + z<sub>B</sub> &#8722; 180&#176;</code>, in
  arcminutes. The last column is the separation from zero for two theodolites reading 5&#8243;, in
  the case most favourable to the plane model (k = 0.47).</caption>
  <thead><tr><th class="n">baseline (km)</th><th class="n">k = 0</th><th class="n">k = 0.13</th><th class="n">k = 0.25</th><th class="n">k = 0.47</th><th class="n">plane</th><th class="n">&#963;</th></tr></thead>
  <tbody>
{t_reciproque(fr)}
  </tbody>
</table>
<div class="box warn">
  <span class="lab">Deflection of the vertical &#8212; the only serious systematic</span>
  <p>The plumb line follows gravity, which mountain masses deflect by a few tens of arcseconds.
  The two deflections <strong>do not cancel</strong> in the sum: they add. In an unfavourable
  mountain case, {nb(DEVIATION_VERTICALE, 0, fr)}&#8243; at each station makes {nb(dev2, 0, fr)}&#8243; of
  possible bias.</p>
  <p>The remedy is direct: <strong>lengthen the baseline</strong>. The signal grows in proportion
  to <code>d</code>; the deflection does not. At 10 km the signal is
  {nb(somme_zenithale_arcsec(10, 0.47), 0, fr)}&#8243; in the worst case, or
  {nb(somme_zenithale_arcsec(10, 0.47) / dev2, 1, fr)} times the bias; at 20 km,
  {nb(somme_zenithale_arcsec(20, 0.47) / dev2, 1, fr)} times. Second remedy: choose stations in
  gentle terrain, where the deflection falls to a few arcseconds, or correct from a published
  deflection grid where one exists for the region.</p>
</div>

<h2><span class="n">04</span>Method B &#8212; the multi-target fit</h2>
<p class="lead">Reciprocity requires two teams and two instruments. At long range it becomes
impractical. It is replaced by a single station and several targets.</p>
<p>From a station at altitude <code>h<sub>obs</sub></code>, sight N identified summits of heights
<code>h<sub>i</sub></code> at distances <code>d<sub>i</sub></code> known from coordinates. The
measured elevation angle is:</p>
<div class="eq">
  s(d) + C = (h &#8722; h<sub>obs</sub>)/d &#8722; d/(2R&#8242;)
  <span class="cap">C is the unknown zero of the reference. It is fitted alongside R&#8242; rather than required.</span>
</div>
<p>That is the decisive point of the method. Absolute levelling is the hardest constraint in all
field metrology: a mis-set bubble, a tilted sensor, a slaved artificial horizon. Here the
<strong>zero error is absorbed by <code>C</code></strong>, which is fitted. The zero need only be
<em>stable</em> through the run, which is vastly easier than being correct.</p>
<p>Two parameters, N targets: from N = 4 the fit is over-determined, and <strong>the residuals say
whether a single <code>k</code> accounts for the whole run</strong>. If they are not random,
refraction is not homogeneous along the sight lines, and the result must be stated as such rather
than averaged.</p>
<table>
  <caption>Table 4 &#8212; Curvature term <code>d/(2R&#8242;)</code> of an elevation angle, in
  arcminutes. The two highlighted rows are the record sight lines.</caption>
  <thead><tr><th class="n">range (km)</th><th class="n">k = 0</th><th class="n">k = 0.13</th><th class="n">k = 0.25</th><th class="n">k = 0.47</th><th class="n">plane</th></tr></thead>
  <tbody>
{t_portee(fr)}
  </tbody>
</table>
<div class="box key">
  <span class="lab">What the simulation gives</span>
  <p>Six targets between 30 and 210 km from a station at {mil(H_STATION, fr)} m, Gaussian noise of
  {nb(BRUIT_SIM, 0, fr)}&#8243; on each sight, 400 draws: <code>k</code> is recovered to
  <strong>&#177;{nb(sim[1], 3, fr)}</strong> &#8212; better than the &#177;0.01 that Table 2 requires. And a
  run generated on a plane separates from the spherical slope most favourable to the plane
  (k = 0.47) by <strong>{nb(sep, 0, fr)}&#160;&#963;</strong>.</p>
  <p>The angular precision needed to distinguish <code>k</code> to &#177;0.01 is
  {nb(ecart_200, 1, fr)}&#8243; at 200 km range, about ten pixels at 400 mm on a full-frame sensor. A
  builder's theodolite does ten times better.</p>
</div>

<h2 class="brk"><span class="n">05</span>Identifying the targets</h2>
<p class="lead">This is the commonest fault in long sight lines, and the quietest: a
misidentified summit changes everything, with nothing in the image to signal it.</p>
<p>The criterion must owe nothing to the vertical model under test. One therefore uses
<strong>azimuth</strong>, a horizontal quantity, compared with the bearing computed from the
coordinates of the two points.</p>
<ol>
  <li><strong>Measure the azimuth</strong> of each target with the theodolite, referenced to a
  known direction &#8212; a geodetic marker, or a solar sight reduced by ephemeris.</li>
  <li><strong>Compute the bearing</strong> station&#8594;target on the ellipsoid from published
  coordinates. That is a purely horizontal operation: it assumes nothing about vertical
  curvature.</li>
  <li><strong>Require uniqueness</strong>: the measured&#8722;computed gap must stay below 0.05&#176;,
  and <strong>no other candidate summit</strong> may lie within &#177;0.2&#176; of the measured
  azimuth. A target failing this test is dropped from the fit, not reinterpreted.</li>
  <li><strong>Record the whole scene</strong>: a wide, uncropped panorama containing identifiable
  near landmarks lets a third party redo the identification without taking our word for it.</li>
</ol>

<h2><span class="n">06</span>Equipment and stations</h2>
<ul>
  <li><strong>Method A</strong>: two theodolites or total stations reading 5&#8243; or better, with
  dual-axis compensator. Two operators, two clocks synchronised by GNSS.</li>
  <li><strong>Method B</strong>: one theodolite, or a full-frame body on a firm mount with a 300
  to 600 mm telephoto, zoom ring and focus mechanically immobilised for the whole run.</li>
  <li><strong>Position</strong>: dual-frequency GNSS receiver, or a materialised geodetic point.
  Instrument height measured by tape and recorded.</li>
  <li><strong>Atmosphere</strong>: temperature, pressure and humidity at each station, at the
  start and at the end. These values are not there to correct anything &#8212; they are there to
  describe the conditions under which <code>R&#8242;</code> was found.</li>
</ul>

<h2><span class="n">07</span>Procedure</h2>
<ol>
  <li><strong>Choose the time window</strong>: midday, with an established thermal gradient,
  rather than dawn where the inversion is strong and unstable. What is wanted is a
  <em>stable</em> atmosphere, not a favourable one.</li>
  <li><strong>Method A &#8212; reciprocal run.</strong> Ten pointings alternating face left / face
  right at each station, within the same minute. Alternating faces eliminates vertical
  collimation error.</li>
  <li><strong>Repeat the reciprocal run three times</strong>, an hour apart. An <code>R&#8242;</code>
  that drifts between runs measures the variation of refraction; that is information, not
  failure.</li>
  <li><strong>Method B &#8212; sweep.</strong> Without touching the setup, sight the N targets in
  increasing order of distance, then in decreasing order. The out-and-back comparison detects a
  drift of the zero during the run.</li>
  <li><strong>Crop nothing, straighten nothing.</strong> Raw files are kept and published with
  the result, whatever it is.</li>
</ol>
<div class="box warn">
  <span class="lab">Rejection criterion</span>
  <p><strong>Method A</strong>: if the three reciprocal runs give <code>R&#8242;</code> values
  differing by more than three times the reading uncertainty, refraction changed during the
  measurement. The day is reported as such, with all three values.</p>
  <p><strong>Method B</strong>: if the out-and-back discrepancy on a target exceeds 3&#963;, the
  zero has drifted and the run is repeated. If the fit residuals show a trend instead of being
  random, a single <code>k</code> does not suffice: say so, do not average.</p>
</div>

<h2 class="brk"><span class="n">08</span>What the measurement establishes</h2>
<p class="lead">The result is a number with its uncertainty, and the list of what each model
requires of it. There is no verdict to deliver, only a value to publish.</p>
<div class="two">
  <div class="vc g">
    <p class="h">z<sub>A</sub> + z<sub>B</sub> &#8722; 180&#176; &gt; 0</p>
    <p class="v">The verticals converge</p>
    <p>The surface is curved along this baseline, and <code>R&#8242;</code> measures by how much. No
    value of <code>k</code> below 1 can produce this sign on a plane.</p>
  </div>
  <div class="vc p">
    <p class="h">z<sub>A</sub> + z<sub>B</sub> &#8722; 180&#176; = 0</p>
    <p class="v">The verticals are parallel</p>
    <p>This is what the plane predicts, exactly and with no free parameter. Over a 10 km
    baseline the sphere is {nb(sig10, 0, fr)}&#160;&#963; away in the case least favourable to it;
    over 20 km, {nb(sig20, 0, fr)}&#160;&#963;.</p>
  </div>
</div>
<p>In either case the value of <code>R&#8242;</code> and its uncertainty are published with the
atmospheric conditions, the azimuth, the baseline, the time and the raw files. A single
measurement describes only one sight line through one air mass; it is their accumulation, across
azimuths and seasons, that carries weight.</p>

<h2><span class="n">09</span>Redoing the record sight lines</h2>
<p class="lead">This is the final object, and it must be said on what conditions such a sight line
would become contestable.</p>
<p>A photograph at {nb(d1, 2, fr)} km carries probative weight only if accompanied by what the
existing pictures do not supply:</p>
<ol>
  <li><strong>Position and eye height</strong> by GNSS, with the vertical uncertainty.</li>
  <li><strong>The measured azimuth</strong> of the target, and the uniqueness demonstration of
  section 05.</li>
  <li><strong>A measurement of <code>k</code> along the same azimuth</strong>, on the same day, by
  method A on a short baseline or method B on intermediate targets. Without it the photograph
  demonstrates nothing, whichever camp invokes it.</li>
  <li><strong>The elevation angle of the lowest visible point</strong> on the massif, rather than
  a visual impression that &#8220;the base is visible&#8221;. That is the quantity which compares
  with the calculation.</li>
  <li><strong>The raw files</strong> and the focal length, published.</li>
</ol>
<div class="box">
  <span class="lab">What we commit to publishing</span>
  <p>If a campaign run under this protocol finds an <code>R&#8242;</code> consistent with a spherical
  Earth and ordinary refraction, that result will be published as it stands, with the raw data,
  and the pages of the site asserting the contrary will be corrected. A protocol with only one
  acceptable outcome is not a protocol.</p>
</div>

<h2><span class="n">10</span>Anticipated objections</h2>
<ol>
  <li><strong>&#8220;Refraction can explain anything.&#8221;</strong> It can reduce the gap in
  method A, never reverse its sign, as long as <code>k &lt; 1</code>. And that is precisely what
  the measurement supplies: the value of <code>k</code>, instead of an appeal to it.</li>
  <li><strong>&#8220;Your theodolites are calibrated on a spherical Earth.&#8221;</strong> A
  theodolite measures angles relative to the local vertical, materialised by a gravity
  compensator. No Earth-radius constant enters the reading. Method A then uses only the sum of
  two readings and the distance.</li>
  <li><strong>&#8220;Deflection of the vertical ruins the measurement.&#8221;</strong> It biases
  it, and the document quantifies it rather than ignoring it. It is bounded and does not grow
  with the baseline, whereas the signal grows in proportion: which is why the recommended
  baseline is 20 km rather than 2.</li>
  <li><strong>&#8220;The plane model also predicts disappearance by perspective.&#8221;</strong>
  Perspective acts on angular <em>position</em>, not on the convergence of verticals. Method A
  measures only that convergence, and the plane assigns it zero with no adjustable parameter.</li>
  <li><strong>&#8220;One baseline proves nothing.&#8221;</strong> Correct, and it is written in the
  bounding box. This protocol gives <code>R&#8242;</code> on one line; it has to be repeated.</li>
</ol>

<h2><span class="n">11</span>Colophon</h2>
<p>Reference values: Earth radius 6&#8239;371 km; Karag&#246;l&#8594;Shkhara line {mil(h1, fr)} m /
{nb(d1, 2, fr)} km / {mil(hm1, fr)} m; Finestrelles&#8594;Barre des &#201;crins line {mil(h2, fr)} m /
{nb(d2, 0, fr)} km / {mil(hm2, fr)} m. The document reconstructs entirely from these values and
the relations <code>R&#8242; = R/(1&#8722;k)</code> and
<code>z<sub>A</sub> + z<sub>B</sub> &#8722; 180&#176; = d/R&#8242;</code>. &#8212; Open protocol, version 1.0.</p>"""


def main():
    k_base, k_cime, ecart_200 = controle_numerique()
    sim = simuler(0.13, BRUIT_SIM, 400, 20260901)
    sim_plan = simuler(None, BRUIT_SIM, 400, 20260902)
    sep = abs(-1 / (2 * rayon_apparent(0.47))) / sim_plan[2]
    assert abs(sim[0] - 0.13) < 0.01 and sim[1] < 0.010, sim
    assert sep > 50, sep

    modele = open(MODELE, encoding="utf-8").read()
    i = modele.find('<div class="page">')
    if i < 0:
        sys.exit("squelette introuvable")
    entete = re.sub(r"<title>[^<]*</title>",
                    "<title>Rayon apparent de la Terre &#8212; protocole bilingue</title>",
                    modele[:i], count=1)

    pages = [entete, '<div class="page">\n',
             '<div class="langbar"><span class="on">FRAN&#199;AIS</span>'
             '<span>ENGLISH &#8212; seconde moiti&#233;</span></div>\n\n',
             corps(True, k_base, k_cime, ecart_200, sim, sep),
             '\n\n<div class="langbar"><span>FRAN&#199;AIS &#8212; first half</span>'
             '<span class="on">ENGLISH</span></div>\n\n',
             corps(False, k_base, k_cime, ecart_200, sim, sep),
             '\n</div>\n']
    open(CIBLE, "w", encoding="utf-8").write("".join(pages))

    print("Protocole écrit : content/protocoles/visee-terrestre-bilingue.html")
    print("  Karagöl→Shkhara, k=0,13 : %.0f m masqués (massif %.0f m)"
          % (cachee(KARAGOL[0], KARAGOL[1], 0.13), KARAGOL[2]))
    print("  k pour que la base réapparaisse : %.3f → R' = %.0f km = %.2f R"
          % (k_base, rayon_apparent(k_base), rayon_apparent(k_base) / R))
    print("  Réciproque à 10 km : %.2f′ (k=0,13), %.2f′ (k=0,47), 0 sur un plan"
          % (somme_zenithale_arcsec(10, 0.13) / 60,
             somme_zenithale_arcsec(10, 0.47) / 60))
    print("  Méthode B simulée : k = %.3f ± %.3f ; plan séparé de %.0f σ"
          % (sim[0], sim[1], sep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
