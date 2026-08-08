#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Article : « Le nivellement avec fermeture — l'argument adverse le plus solide ».

Pourquoi cet article. Le site examine les démonstrations de la sphéricité et
montre que la plupart ne discriminent pas. Il ne traitait nulle part la seule
qui résiste vraiment : la condition de fermeture d'un réseau de nivellement.
Un examen qui écarte les arguments faibles et tait le fort n'est pas un examen.

Toutes les valeurs numériques de l'article sont recalculées ici et comparées à
ce qui est écrit dans le HTML. Voir CONTROLES en fin de fichier.
"""

import json
import math
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(RACINE, "content", "articles")
SLUG = "le-nivellement-avec-fermeture"

# ═══════════════════════════════════════════════════════════════════════════
# Le calcul
# ═══════════════════════════════════════════════════════════════════════════

R = 6371000.0          # m, rayon moyen
K = 0.13               # coefficient de réfraction moyen (Hirt et al. 2010)
OMEGA = 7.292115e-5    # rad/s
A_WGS = 6378137.0      # m, demi-grand axe
GE = 9.7803267715      # m/s², pesanteur normale à l'équateur
F_WGS = 1 / 298.257223563
BETA_MESURE = 0.0053024

LAT_SUD, LAT_NORD = 42.3, 51.1   # Cerbère → Dunkerque


def fleche_tangente(d, k=K):
    """Écart entre la ligne de visée et la surface de niveau, sur une visée
    de longueur d. C'est la « chute sous la tangente », corrigée de la
    réfraction : (1−k)·d²/(2R)."""
    return (1.0 - k) * d * d / (2.0 * R)


def g_normale(phi_deg):
    """Pesanteur normale à la latitude phi (formule de la gravité normale)."""
    p = math.radians(phi_deg)
    return GE * (1 + BETA_MESURE * math.sin(p) ** 2
                 - 0.0000058 * math.sin(2 * p) ** 2)


G_SUD, G_NORD = g_normale(LAT_SUD), g_normale(LAT_NORD)
DG_SUR_G = (G_NORD - G_SUD) / ((G_NORD + G_SUD) / 2)
ECART_POLE = (g_normale(90) - g_normale(0)) / g_normale(0)

M_CENTRIFUGE = OMEGA ** 2 * A_WGS / GE
BETA_CLAIRAUT = 2.5 * M_CENTRIFUGE - F_WGS
ECART_CLAIRAUT = abs(BETA_CLAIRAUT - BETA_MESURE) / BETA_MESURE


BODY = """<p class="tei-lede">Une boucle de nivellement qui revient à son point de départ doit se refermer sur zéro. Elle ne s'y referme pas — et le terme qui manque n'existe que si les surfaces de niveau ne sont pas parallèles. C'est l'argument le plus solide contre nous, et nous ne l'avions jamais traité.</p>

<h2 id="niv-pourquoi"><span class="tei-section-num">01</span>Pourquoi cet article existe</h2>

<p>Ce site passe en revue les démonstrations classiques de la sphéricité et montre que la plupart ne <strong>discriminent pas</strong> : l'ombre d'Ératosthène, la disparition des navires, la montée de l'Étoile polaire, la circumnavigation, l'ombre circulaire des éclipses — toutes sont compatibles avec deux géométries, ou contaminées par la réfraction.</p>

<p>Ce constat est juste, et il ne suffit pas. Un examen qui écarte les arguments faibles et passe le fort sous silence n'est pas un examen : c'est une sélection. Or il existe un argument qui résiste, et nous ne le traitions nulle part. Le voici, dans sa forme la plus forte, avec les ordres de grandeur.</p>

<p>Prévenons d'emblée : cette section-là ne se termine pas à notre avantage. Elle se termine sur une tâche.</p>

<h2 id="niv-quest-ce"><span class="tei-section-num">02</span>Ce qu'est un nivellement de précision</h2>

<p>Le nivellement géométrique est la plus terre-à-terre des mesures géodésiques. On plante deux mires verticales, on installe un niveau entre elles, on lit la graduation arrière puis la graduation avant. La différence des deux lectures donne la <strong>dénivelée</strong> entre les deux points. On avance de portée en portée, et l'on additionne.</p>

<p>Aucun satellite. Aucun modèle de Terre. Un instrument optique, deux règles graduées et une addition. C'est exactement le genre de mesure que nous réclamons : reproductible, instrumentale, à portée d'un opérateur soigneux. Les réseaux nationaux — en France le <strong>NGF-IGN69</strong> — sont bâtis là-dessus, sur des dizaines de milliers de kilomètres de cheminements.</p>

<p>Ce qui définit un niveau, c'est qu'il matérialise une <strong>surface de niveau</strong> : la surface perpendiculaire en tout point à la direction du fil à plomb. Une bulle se cale sur elle, un plan d'eau s'y range. Retenez ce mot : tout ce qui suit tourne autour de la question de savoir si ces surfaces sont <em>parallèles entre elles</em>.</p>

<h2 id="niv-annulation"><span class="tei-section-num">03</span>La courbure s'annule dans une portée — et notre camp se trompe souvent là-dessus</h2>

<p>On lit régulièrement, dans la littérature qui nous est proche, que les géomètres « sont bien obligés d'appliquer une correction de courbure », ce qui prouverait la courbure. <strong>C'est faux, et il faut le dire.</strong></p>

<p>Sur une visée de longueur <em>d</em>, la ligne de visée s'écarte de la surface de niveau de (1−k)·<em>d</em>²/(2R). Voici ce que cela vaut.</p>

<table class="tei-table">
<thead><tr><th>Longueur de visée</th><th>Écart visée / surface de niveau</th></tr></thead>
<tbody>
<tr><td>30 m</td><td>0,0615 mm</td></tr>
<tr><td>40 m</td><td>0,1092 mm</td></tr>
<tr><td>60 m</td><td>0,2458 mm</td></tr>
<tr><td>100 m</td><td>0,6828 mm</td></tr>
<tr><td>200 m</td><td>2,7311 mm</td></tr>
</tbody>
</table>

<p>Mais surtout : l'opérateur place son instrument <strong>à égale distance</strong> des deux mires. L'écart est alors le même à l'arrière et à l'avant, et il <strong>disparaît dans la différence</strong>. Le nivellement de précision ne corrige pas la courbure : il l'annule par construction. C'est d'ailleurs la raison pour laquelle la règle des portées équilibrées est la première du métier.</p>

<p>Et le résidu, si l'équilibrage n'est pas parfait, est dérisoire.</p>

<table class="tei-table">
<thead><tr><th>Visée arrière / avant</th><th>Résidu non compensé</th></tr></thead>
<tbody>
<tr><td>60 m / 59 m</td><td>0,0081 mm</td></tr>
<tr><td>60 m / 55 m</td><td>0,0393 mm</td></tr>
<tr><td>60 m / 50 m</td><td>0,0751 mm</td></tr>
<tr><td>100 m / 90 m</td><td>0,1297 mm</td></tr>
</tbody>
</table>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Si vous mettez votre appareil pile au milieu entre les deux règles, l'effet de courbure vous trompe exactement de la même quantité à gauche et à droite. En faisant la soustraction, il s'efface. Le géomètre n'a donc rien à corriger — et c'est pour ça qu'un argument de notre côté, celui qui dit « ils appliquent une correction, donc c'est courbe », ne vaut rien. Il faut chercher ailleurs. Et il y a ailleurs.</p></div>

<h2 id="niv-trigo"><span class="tei-section-num">04</span>Là où la courbure ne s'annule pas : le nivellement trigonométrique</h2>

<p>Autre méthode, autre affaire. Pour franchir une vallée ou un bras de mer, on ne peut pas poser de mires tous les soixante mètres : on mesure un <strong>angle vertical</strong> depuis une station vers un point lointain, et l'on en déduit la dénivelée. Là, il n'y a plus de symétrie qui sauve, et la correction devient massive.</p>

<table class="tei-table">
<thead><tr><th>Distance visée</th><th>Correction (1−k)<em>d</em>²/(2R)</th></tr></thead>
<tbody>
<tr><td>1 km</td><td>0,068 m</td></tr>
<tr><td>5 km</td><td>1,707 m</td></tr>
<tr><td>10 km</td><td>6,828 m</td></tr>
<tr><td>50 km</td><td>170,695 m</td></tr>
</tbody>
</table>

<p>Sans cette correction, un nivellement trigonométrique sur 10 km se tromperait de près de sept mètres. Avec elle, il se raccorde au nivellement géométrique au centimètre. C'est un indice, pas une preuve : la correction contient le rayon <em>R</em>, donc le modèle. Un modèle plan aurait besoin d'un autre terme, du même ordre, pour expliquer la même chose — mais il pourrait en principe le postuler. Ce n'est pas encore l'argument décisif.</p>

<h2 id="niv-fermeture"><span class="tei-section-num">05</span>La fermeture de boucle : l'effet qui résiste</h2>

<p>Voici l'argument. Il ne porte pas sur une lecture, mais sur une <strong>contrainte de cohérence</strong>, et c'est ce qui fait sa force.</p>

<p>Partez d'un repère, cheminez en boucle — vers le nord, en altitude, puis retour par la côte — et revenez au point de départ. Additionnez toutes les dénivelées lues. Le total <strong>doit</strong> être nul : vous êtes revenu là où vous étiez. C'est une tautologie géométrique, indépendante de tout modèle.</p>

<p>Or la somme n'est pas nulle. Elle porte un résidu systématique, reproductible, qui n'est pas du bruit : refaites le cheminement, vous le retrouvez. Et il dépend du <strong>trajet</strong> — de l'amplitude en latitude de la boucle et de son profil d'altitude — alors qu'une différence d'altitude entre deux points ne devrait dépendre que des deux points.</p>

<p>La raison est que les surfaces de niveau <strong>ne sont pas parallèles</strong>. Elles se resserrent vers les pôles, parce que la pesanteur y est plus forte : à énergie égale, il faut monter moins haut là où <em>g</em> est plus grand. Une dénivelée lue est un écart <em>géométrique</em> ; ce qui se conserve autour d'une boucle est l'écart <em>de potentiel</em>. Les deux ne coïncident que si <em>g</em> est partout le même.</p>

<p>C'est pourquoi les réseaux nationaux ne publient pas des sommes de dénivelées brutes, mais des <strong>cotes géopotentielles</strong>, converties ensuite en altitudes par une <strong>correction orthométrique</strong>. Cette correction n'est pas un artifice de calcul : c'est le terme qui rend la boucle fermable.</p>

<div class="tei-fait observatory">
<span class="tei-fait-label">CE QUE MONTRENT LES DONNÉES</span>
<p>Sur une Terre plane où la pesanteur serait uniforme, les surfaces de niveau seraient des plans parallèles, la dénivelée lue vaudrait exactement l'écart de potentiel divisé par <em>g</em>, et une boucle de nivellement se refermerait sur zéro au bruit près. Le modèle plan à pesanteur uniforme <strong>n'a aucun terme</strong> pour un résidu systématique dépendant du trajet. Le modèle ellipsoïdal en prédit un, et en donne la valeur.</p>
</div>

<h2 id="niv-ordres"><span class="tei-section-num">06</span>Les ordres de grandeur, mis côte à côte</h2>

<p>C'est ici que l'argument devient sérieux. La pesanteur normale varie de <strong>0,5302 %</strong> entre l'équateur et le pôle. Sur la seule traversée de la France — de Cerbère (42,3° N) à Dunkerque (51,1° N), soit 8,8° et environ 979 km — elle varie de 9,803760 à 9,811682 m/s², c'est-à-dire de <strong>0,0808 %</strong>.</p>

<p>Le terme orthométrique est de l'ordre de <em>H</em> × Δ<em>g</em>/<em>g</em>, où <em>H</em> est l'altitude du cheminement. Voici ce que cela donne pour une boucle traversant la France.</p>

<table class="tei-table">
<thead><tr><th>Altitude du cheminement</th><th>Terme orthométrique</th></tr></thead>
<tbody>
<tr><td>100 m</td><td>80,8 mm</td></tr>
<tr><td>500 m</td><td>403,9 mm</td></tr>
<tr><td>1 000 m</td><td>807,7 mm</td></tr>
<tr><td>2 000 m</td><td>1 615,4 mm</td></tr>
</tbody>
</table>

<p>Comparez maintenant les deux colonnes du dossier. L'effet de courbure sur une visée de 30 m vaut <strong>0,0615 mm</strong>, et il s'annule. Le terme orthométrique sur une boucle française à 100 m d'altitude vaut <strong>80,8 mm</strong>, et il ne s'annule pas. <strong>Trois ordres de grandeur d'écart</strong>, et ce n'est pas le petit terme qui compte.</p>

<p>Il faut le dire nettement : un opérateur muni d'un niveau, de deux mires et de patience mesure une quantité de l'ordre de huit centimètres qu'un modèle plan à pesanteur uniforme ne peut pas produire. Ce n'est pas une image satellite, ce n'est pas un calcul d'agence. C'est de l'arpentage.</p>

<h2 id="niv-clairaut"><span class="tei-section-num">07</span>Le théorème de Clairaut : deux mesures indépendantes qui se recoupent</h2>

<p>Et il y a pire pour nous — ou mieux, selon le point de vue. Deux grandeurs se mesurent de façon entièrement séparée :</p>

<ul>
  <li>l'<strong>aplatissement géométrique</strong> <em>f</em>, obtenu en comparant des arcs de méridien mesurés à différentes latitudes — de l'arpentage, encore ;</li>
  <li>le <strong>coefficient de variation de la pesanteur</strong> β, obtenu au gravimètre, instrument qui ne mesure aucune distance.</li>
</ul>

<p>Le théorème de Clairaut les relie par la rotation : β ≈ 5<em>m</em>/2 − <em>f</em>, où <em>m</em> est le rapport centrifuge ω²<em>a</em>/<em>g</em>. Le calcul donne <em>m</em> = 3,4677 × 10⁻³ et, avec <em>f</em> = 1/298,257, une prédiction β = 5,3166 × 10⁻³. La valeur mesurée est 5,3024 × 10⁻³. <strong>Écart : 0,27 %.</strong></p>

<p>Deux instruments sans rapport — une chaîne d'arpenteur et un gravimètre — donnent deux nombres qu'une relation théorique lie, et ils concordent au quart de pour cent. Un modèle plan qui voudrait reproduire la variation de <em>g</em> avec la latitude devrait la reproduire <strong>avec exactement la valeur qu'un aplatissement mesuré indépendamment prédit</strong>. C'est possible en principe. Ce n'est pas gratuit.</p>

<h2 id="niv-circularite"><span class="tei-section-num">08</span>Où est la prise circulaire, et où il n'y en a pas</h2>

<p>Notre méthode consiste à chercher si une mesure présuppose ce qu'elle établit. Faisons-le honnêtement, en séparant les deux couches.</p>

<p><strong>Ce qui n'est pas circulaire.</strong> L'observation elle-même : la somme des dénivelées lues autour d'une boucle fermée n'est pas nulle, et le résidu dépend du trajet de façon reproductible. Ce fait ne suppose aucun rayon, aucun ellipsoïde, aucun satellite. Il se constate avec un niveau et des mires. C'est le noyau dur de l'argument, et il tient.</p>

<p><strong>Ce qui l'est.</strong> La <em>valeur prédite</em> du résidu, elle, passe par la formule de pesanteur normale, qui est définie sur un ellipsoïde de référence. Là, le modèle est dans le calcul. On ne peut donc pas dire que la boucle « mesure l'ellipsoïde » sans plus de précaution : elle mesure un écart, et c'est le modèle ellipsoïdal qui en rend compte quantitativement.</p>

<p><strong>Ce qu'un modèle plan devrait faire.</strong> Postuler un champ de pesanteur non uniforme, variant avec la position d'une manière précise. Cette échappatoire existe, et beaucoup de modèles plans la prennent déjà, sous une forme ou une autre. Mais elle a un prix, et il faut l'énoncer : la variation postulée doit reproduire <strong>à la fois</strong> le terme de fermeture des boucles de nivellement, la variation mesurée au gravimètre, et la relation de Clairaut qui la lie à un aplatissement mesuré par des arcs de méridien. Trois contraintes, un seul degré de liberté. Personne, de notre côté, ne l'a fait.</p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Imaginez un escalier dont les marches ne font pas toutes la même hauteur. Vous montez par un côté, vous descendez par l'autre, et vous ne retombez pas exactement là d'où vous êtes parti — alors que vous avez compté vos marches. C'est ce qui arrive au nivellement. L'explication officielle est que les « marches » se resserrent vers le nord parce que la pesanteur y est plus forte. Nous pouvons en proposer une autre, mais elle devra expliquer le même écart, avec les mêmes chiffres, et se raccorder à deux autres mesures qui n'ont rien à voir.</p></div>

<h2 id="niv-canaux"><span class="tei-section-num">09</span>Ce que cela oblige à corriger chez nous : l'argument des canaux</h2>

<p>Nos propres articles avancent que des canaux sans écluses sur des centaines de kilomètres, des aqueducs, des pipelines, « n'intègrent aucune correction de courbure ». Il faut réviser cet argument, parce qu'il ne dit pas ce que nous croyions.</p>

<p>La surface d'un canal <strong>est</strong> une surface de niveau. L'eau s'y range d'elle-même : c'est sa définition physique. L'ingénieur n'a donc rien à « ajouter » — non parce que la surface serait plane, mais parce que l'eau trouve le niveau sans lui. Sur les deux modèles, le résultat est identique, et le fait ne discrimine rien.</p>

<p>La vraie question est ailleurs, et elle est plus dure : les repères qui servent à implanter l'ouvrage viennent d'un réseau de nivellement, et ce réseau porte la correction orthométrique. L'argument des canaux, tel que nous le formulions, se retourne donc : il ne prouve pas la planéité, il montre seulement que l'eau obéit au potentiel — ce que tout le monde admet.</p>

<p>Nous laissons le passage dans <a href="/article/leau-ne-ment-pas">L'eau ne ment pas</a> et signalons la réserve plutôt que de la faire disparaître, comme le veut notre <a href="/article/standards-et-methode">règle sur les corrections</a>. Mais il ne doit plus être compté comme une pièce à charge.</p>

<h2 id="niv-trancher"><span class="tei-section-num">10</span>Ce qui trancherait</h2>

<p>Cet argument n'est pas réfutable par la discussion. Il est vérifiable, et c'est mieux. Voici la tâche, dans l'ordre.</p>

<p><strong>Obtenir les observations brutes</strong>, pas les altitudes publiées. Ce qu'il faut, ce sont les carnets de cheminement d'une boucle fermée du NGF — dénivelées lues portée par portée, longueurs de visée, altitudes approchées — et la valeur de fermeture avant toute correction. Les altitudes publiées ne servent à rien : elles sont le résultat de l'ajustement, donc du modèle.</p>

<p><strong>Puis trois vérifications, dans cet ordre.</strong> La fermeture brute est-elle non nulle au-delà du bruit annoncé ? Son signe et sa taille suivent-ils l'amplitude en latitude et le profil d'altitude de la boucle ? Et la valeur observée coïncide-t-elle avec <em>H</em> × Δ<em>g</em>/<em>g</em>, soit environ 81 mm pour cent mètres d'altitude sur la traversée de la France ?</p>

<p><strong>Si les trois réponses sont oui</strong>, alors le nivellement établit que les surfaces de niveau convergent, et notre camp doit soit produire un champ de pesanteur qui rende compte des mêmes chiffres, soit admettre l'ellipsoïde. Notre charte ne laisse pas de troisième voie.</p>

<p>Un mot sur la place de cet argument par rapport au nôtre. Le <a href="/article/monter-l-experience-des-trois-mires">protocole des trois mires</a> lit un <strong>exposant</strong> et ne suppose aucun rayon : c'est sa force, et il reste à faire. Le nivellement, lui, est une <strong>contrainte de fermeture</strong> — une condition de cohérence sur un réseau entier, pas une lecture isolée — et il a déjà été fait, des dizaines de milliers de fois. Les deux ne s'excluent pas. Le second est simplement plus avancé que le nôtre, et il serait malhonnête de faire comme si le nôtre était le seul en jeu.</p>

<p>Voir aussi : <a href="/article/par-rapport-a-quoi-mesure-t-on-une-altitude">Par rapport à quoi mesure-t-on une altitude ?</a> · <a href="/article/leau-ne-ment-pas">L'eau ne ment pas</a> · <a href="/article/mesurer-la-courbure-sur-l-eau-cinq-campagnes">Mesurer la courbure sur l'eau</a> · <a href="/article/monter-l-experience-des-trois-mires">Monter l'expérience des trois mires</a> · <a href="/article/standards-et-methode">Standards et méthode</a>.</p>

<h2 id="sources"><span class="tei-section-num">11</span>Sources</h2>

<p>Les valeurs numériques de cet article sont calculées, non relevées : elles proviennent des formules citées, avec <em>R</em> = 6 371 km, <em>k</em> = 0,13 et la formule de pesanteur normale. Le script <code>scripts/generer-nivellement-fermeture.py</code> les recalcule et refuse d'écrire si l'une d'elles ne concorde plus. <strong>Ce qui n'est pas fait</strong> — et l'article le demande en section 10 — c'est de les confronter aux fermetures brutes d'un réseau réel.</p>

<ol>
  <li>Institut national de l'information géographique et forestière. <em>Nivellement général de la France, NGF-IGN69</em> — réseau de référence altimétrique français. <span class="tei-grade grade-b">B</span> — référentiel identifié ; les carnets de cheminement et les fermetures brutes restent à demander.</li>
  <li>Heiskanen, W. A. et Moritz, H. (1967). <em>Physical Geodesy</em>. San Francisco : W. H. Freeman — cotes géopotentielles, correction orthométrique, non-parallélisme des surfaces de niveau. <span class="tei-grade grade-c">C</span> <em>(à paginer)</em></li>
  <li>Torge, W. et Müller, J. (2012). <em>Geodesy</em>, 4<sup>e</sup> éd. Berlin : De Gruyter — nivellement géométrique, portées équilibrées, nivellement trigonométrique. <span class="tei-grade grade-c">C</span> <em>(à paginer)</em></li>
  <li>Clairaut, A. C. (1743). <em>Théorie de la figure de la Terre, tirée des principes de l'hydrostatique</em>. Paris : Durand — la relation entre aplatissement, rotation et variation de la pesanteur. <span class="tei-grade grade-c">C</span> <em>(à paginer)</em></li>
  <li>Formule de pesanteur normale et paramètres géométriques : ω = 7,292115 × 10⁻⁵ rad/s, <em>a</em> = 6 378 137 m, <em>g</em><sub>e</sub> = 9,780 327 m/s², 1/<em>f</em> = 298,257 223 563 — WGS 84. <span class="tei-grade grade-a">A</span></li>
  <li>Hirt, C., Guillaume, S., Wisbar, A., Bürki, B. et Sternberg, H. (2010). « Monitoring of the refraction coefficient in the lower atmosphere using a controlled setup of simultaneous reciprocal vertical angle measurements ». <em>Journal of Geophysical Research: Atmospheres</em>, 115, D21102. DOI : <a href="https://doi.org/10.1029/2010JD014067" target="_blank" rel="noopener">10.1029/2010JD014067</a>. <span class="tei-grade grade-a">A</span></li>
</ol>
"""

ARTICLE = {
    "title": "Le nivellement avec fermeture : l'argument adverse le plus solide",
    "description": "Une boucle de nivellement doit se refermer sur zéro. Elle ne s'y referme pas, et le terme qui manque n'existe que si les surfaces de niveau convergent. Ordres de grandeur, part circulaire, ce que cela oblige à corriger chez nous, et ce qu'il faudrait obtenir pour trancher.",
    "date": "2026-08-06",
    "author": "Terre Etendue",
    "category": "observatory",
    "tags": ["l-observatoire", "géodésie", "nivellement", "pesanteur", "métrologie", "épistémologie"],
    "pinned": False,
    "htmlBody": BODY,
}


# ═══════════════════════════════════════════════════════════════════════════
# CONTROLES — chaque valeur écrite dans le HTML est recalculée
# ═══════════════════════════════════════════════════════════════════════════

def controles():
    pb = []
    attendus = [
        # (libellé, valeur recalculée, chaîne qui doit figurer dans le HTML)
        ("visée 30 m", fleche_tangente(30) * 1000, "0,0615 mm"),
        ("visée 40 m", fleche_tangente(40) * 1000, "0,1092 mm"),
        ("visée 60 m", fleche_tangente(60) * 1000, "0,2458 mm"),
        ("visée 100 m", fleche_tangente(100) * 1000, "0,6828 mm"),
        ("visée 200 m", fleche_tangente(200) * 1000, "2,7311 mm"),
        ("résidu 60/59", (1 - K) * (60 ** 2 - 59 ** 2) / (2 * R) * 1000, "0,0081 mm"),
        ("résidu 60/55", (1 - K) * (60 ** 2 - 55 ** 2) / (2 * R) * 1000, "0,0393 mm"),
        ("résidu 60/50", (1 - K) * (60 ** 2 - 50 ** 2) / (2 * R) * 1000, "0,0751 mm"),
        ("résidu 100/90", (1 - K) * (100 ** 2 - 90 ** 2) / (2 * R) * 1000, "0,1297 mm"),
        ("trigo 1 km", fleche_tangente(1000), "0,068 m"),
        ("trigo 5 km", fleche_tangente(5000), "1,707 m"),
        ("trigo 10 km", fleche_tangente(10000), "6,828 m"),
        ("trigo 50 km", fleche_tangente(50000), "170,695 m"),
        ("g Cerbère", G_SUD, "9,803760"),
        ("g Dunkerque", G_NORD, "9,811682"),
        ("écart pôle %", ECART_POLE * 100, "0,5302 %"),
        ("Δg/g France %", DG_SUR_G * 100, "0,0808 %"),
        ("orthométrique 100 m", 100 * DG_SUR_G * 1000, "80,8 mm"),
        ("orthométrique 500 m", 500 * DG_SUR_G * 1000, "403,9 mm"),
        ("orthométrique 1000 m", 1000 * DG_SUR_G * 1000, "807,7 mm"),
        ("orthométrique 2000 m", 2000 * DG_SUR_G * 1000, "1 615,4 mm"),
        ("m centrifuge", M_CENTRIFUGE * 1e3, "3,4677"),
        ("β Clairaut", BETA_CLAIRAUT * 1e3, "5,3166"),
        ("β mesuré", BETA_MESURE * 1e3, "5,3024"),
        ("écart Clairaut %", ECART_CLAIRAUT * 100, "0,27 %"),
    ]

    for nom, valeur, chaine in attendus:
        # La chaîne doit figurer telle quelle dans l'article…
        if chaine not in BODY:
            pb.append("%s : « %s » absent du texte" % (nom, chaine))
            continue
        # …et le nombre qu'elle porte doit correspondre au recalcul.
        nombre = chaine.replace(" ", "").replace(" ", "")
        nombre = re.sub(r"[^0-9,.\-]", "", nombre).replace(",", ".")
        try:
            annonce = float(nombre)
        except ValueError:
            pb.append("%s : « %s » illisible" % (nom, chaine))
            continue
        # Le texte affiche une valeur ARRONDIE : on compare à ce même arrondi,
        # sinon « 0,27 % » serait rejeté alors qu'il arrondit correctement 0,267.
        decimales = len(nombre.split(".")[1]) if "." in nombre else 0
        if round(valeur, decimales) != annonce:
            pb.append("%s : recalcul %.6f → arrondi %.*f, texte %.*f"
                      % (nom, valeur, decimales, round(valeur, decimales),
                         decimales, annonce))

    # L'amplitude en latitude annoncée
    if "8,8°" not in BODY or "979 km" not in BODY:
        pb.append("amplitude en latitude absente du texte")
    span = LAT_NORD - LAT_SUD
    if abs(span - 8.8) > 0.05 or abs(span * 111.2 - 979) > 5:
        pb.append("amplitude : %.2f° soit %.0f km" % (span, span * 111.2))

    # Le rapport de trois ordres de grandeur annoncé en section 06
    rapport = (100 * DG_SUR_G) / fleche_tangente(30)
    if not (500 <= rapport <= 5000):
        pb.append("le rapport annoncé « trois ordres de grandeur » vaut %.0f" % rapport)
    return pb, rapport


def controles_charte(html):
    pb = []
    if 'class="tei-lede"' not in html:
        pb.append("pas de lede")
    if 'id="sources"' not in html:
        pb.append("pas de section Sources")
    if 'tei-fait observatory' not in html:
        pb.append("encadré-clé absent ou de la mauvaise couleur")
    if "CE QUE MONTRENT LES DONNÉES" not in html:
        pb.append("label d'encadré non conforme au pilier Observatoire")
    nums = re.findall(r'<span class="tei-section-num">(\d+)</span>', html)
    if nums != ["%02d" % (i + 1) for i in range(len(nums))]:
        pb.append("numérotation : %s" % " ".join(nums))
    for titre in re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.S):
        if re.search(r"[\U0001F300-\U0001FAFF]", titre):
            pb.append("emoji dans un titre")
    for balise in ("p", "div", "table", "thead", "tbody", "tr", "td", "th",
                   "ol", "ul", "li", "h2", "a", "span", "em", "strong", "sup", "sub"):
        o = len(re.findall(r"<%s[\s>]" % balise, html))
        f = len(re.findall(r"</%s>" % balise, html))
        if o != f:
            pb.append("<%s> : %d / %d" % (balise, o, f))
    return pb


def main():
    pb, rapport = controles()
    for p in pb:
        print("  ✗ %s" % p)
    if pb:
        return 1
    print("  ✓ 25 valeurs numériques concordent avec leur recalcul")
    print("    rapport terme orthométrique / courbure par visée : ×%.0f" % rapport)

    pb = controles_charte(BODY)
    for p in pb:
        print("  ✗ %s" % p)
    if pb:
        return 1

    chemin = os.path.join(ARTICLES, SLUG + ".json")
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(ARTICLE, f, ensure_ascii=False, indent=2)
        f.write("\n")
    mots = len(re.sub(r"<[^>]+>", " ", BODY).split())
    print("  ✓ %s : %d mots, %d tableaux, %d encadrés En clair"
          % (SLUG, mots, BODY.count("<table"), BODY.count('class="tei-enclair"')))
    return 0


if __name__ == "__main__":
    sys.exit(main())
