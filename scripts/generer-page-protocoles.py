#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Écrit content/articles/les-protocoles-ce-que-c-est-et-pourquoi.json.

    python3 scripts/generer-page-protocoles.py

La page d'entrée des protocoles. Elle porte le cadrage général — pourquoi une
observation seule ne tranche pas, quelles règles on s'est données, dans quel
ordre les opérations se font — c'est-à-dire exactement ce qu'on a retiré des
protocoles eux-mêmes pour qu'ils restent de purs protocoles.

Les trois figures viennent de figures-page-protocoles.py, qui les calcule.
"""

import json
import pathlib

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "figures_page_protocoles",
    pathlib.Path(__file__).resolve().parent / "figures-page-protocoles.py")
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)

RACINE = pathlib.Path(__file__).resolve().parent.parent
CIBLE = RACINE / "content" / "articles" / "les-protocoles-ce-que-c-est-et-pourquoi.json"

fig1, fig2, fig3 = F.figure_geometrie(), F.figure_budget(), F.figure_chaine()

CORPS = f"""<p class="tei-lede">Un protocole de vingt-deux pages pour une mesure qui dure vingt minutes. Le rapport paraît absurde&nbsp;: il est exactement l'inverse. Les vingt minutes produisent un nombre&nbsp;; les vingt-deux pages sont ce qui empêche qu'on puisse en discuter le sens après coup.</p>

<h2 id="avant-de-commencer">Avant de commencer</h2>
<p>Cette page n'est pas une expérience. C'est la porte d'entrée des protocoles que nous publions&nbsp;: ce qu'ils sont, quelles règles nous nous sommes données pour les écrire, et comment les lire quand on découvre le sujet.</p>
<p>Nous l'écrivons pour une raison concrète. Un protocole complet est dense par construction, et plusieurs personnes qui voulaient réellement faire la mesure nous ont dit la même chose&nbsp;: elles n'arrivaient pas à se représenter l'ensemble avant d'entrer dans le détail. Les trois figures de cette page sont là pour ça — l'observable, le rapport signal sur bruit, l'enchaînement des phases. Trois images, et on sait de quoi il retourne.</p>
<p>Les règles générales que nous nous imposons sur l'ensemble du site — sourçage, disponibilité des données, politique de correction — sont énoncées à part, dans <a href="/article/standards-et-methode">Standards et méthode</a>. Ce qui suit ne les répète pas&nbsp;: il dit ce qui s'y ajoute quand on passe du principe à un document remis à un inconnu.</p>

<h2 id="observation-ne-tranche-rien"><span class="tei-section-num">01</span>Une observation ne tranche rien</h2>
<p>Prenez n'importe quelle photo d'horizon marin publiée dans un débat sur la forme de la Terre. Elle circule, elle est commentée, elle ne convainc personne. Ce n'est pas un problème d'honnêteté&nbsp;: c'est que l'image seule ne porte aucune des informations qui permettraient d'en tirer une conclusion.</p>
<p>Il y manque quatre choses, toujours les mêmes.</p>
<ul>
  <li><strong>La prédiction de chaque modèle, chiffrée.</strong> Sans elle, chacun lit dans l'image ce qu'il y cherchait. Avec elle, l'image donne un nombre qui tombe d'un côté ou de l'autre.</li>
  <li><strong>L'incertitude de la mesure.</strong> Un écart de trois minutes d'arc ne veut rien dire tant qu'on ignore si l'appareil sait mesurer à une minute près ou à dix.</li>
  <li><strong>Les conditions du moment.</strong> Température de l'air et de l'eau, pression, marée, état de la mer. Elles ne se retrouvent pas après coup, et sans elles la réfraction atmosphérique reste un argument invérifiable que chaque camp invoque à sa convenance.</li>
  <li><strong>Le critère de décision, fixé avant.</strong> Faute de quoi le seuil se déplace après la mesure, dans le sens qui arrange — souvent sans mauvaise foi consciente.</li>
</ul>
<p>Un protocole est le document qui fournit ces quatre choses à l'avance. Ce n'est pas une formalité académique&nbsp;: c'est ce qui transforme une image en preuve, ou en réfutation.</p>

<h2 id="les-six-regles"><span class="tei-section-num">02</span>Les six règles que nous nous sommes données</h2>
<p>Elles ne sont pas tombées du ciel. Chacune est née d'un problème rencontré en écrivant les documents, et plusieurs nous ont obligés à retirer du texte déjà rédigé.</p>

<h3>1. L'observable et les deux prédictions, écrits avant toute acquisition</h3>
<p>Pas «&nbsp;on va regarder l'horizon&nbsp;», mais&nbsp;: <em>on mesure l'angle entre l'horizontale vraie et la ligne d'horizon marin&nbsp;; une sphère prédit δ = √(2h/R′), un plan prédit δ = 0 à toute altitude</em>. Les deux modèles doivent produire un nombre différent, et ce nombre doit être écrit avant la première image.</p>

<h3>2. Un budget d'erreur chiffré, poste par poste</h3>
<p>Chaque source d'erreur reçoit une valeur et un traitement. Le total quadratique donne l'incertitude à 1&nbsp;σ. Si ce total est du même ordre que l'écart à mesurer, l'expérience ne vaut pas la peine d'être montée — et il vaut mieux le savoir avant de monter sur une falaise de nuit.</p>

<h3>3. Les critères de décision posés d'avance, y compris ceux qui nous font perdre</h3>
<p>Le protocole de l'horizon dit ce qui le réfuterait&nbsp;: une pente nulle dans la régression de δ contre √h, ou un exposant incompatible avec 0,500. Un document qui n'énonce que les conditions de sa victoire n'est pas un protocole, c'est une plaidoirie.</p>

<h3>4. Aucun appui sur une expérience antérieure</h3>
<p>C'est la règle qui nous a coûté le plus. Les premières versions citaient des campagnes passées, des calculateurs, des résultats publiés. Nous les avons toutes retirées, pour une raison que nous assumons&nbsp;: <strong>nous n'avions pas vu leurs données brutes</strong>. S'en réclamer, c'était faire exactement ce que la méthode interdit — accepter un résultat parce qu'il est répandu.</p>
<p>Les seules références que les protocoles conservent sont celles qui <em>fondent une formule employée</em>&nbsp;: indice de réfraction de l'air, réfraction géodésique, atmosphère standard. Un protocole doit dire d'où viennent ses constantes. Il n'a pas à dire qui a eu raison avant lui.</p>

<h3>5. L'ordre des opérations est contraignant</h3>
<p>Certaines étapes rendent les précédentes irrécupérables. L'horodatage déposé après la première image ne prouve plus rien. La température de l'eau se relève au moment de la pose, ou jamais. Une bague de mise au point qui bouge entre la mesure et la pose de résolution supprime l'unité de tout ce qui précède. Un protocole doit donc dire non seulement quoi faire, mais dans quel ordre, et laquelle des étapes ne se rattrape pas.</p>

<h3>6. Publier ce qu'on n'a pas mesuré</h3>
<p>Les stations en régime réfractif anormal sont conservées et signalées, pas écartées. Une station n'est retirée que sur un motif écrit et publié&nbsp;; jamais parce que le chiffre déplaît. Et le document dit explicitement ce qu'il ne mesure pas — le protocole solaire mesure une distance, pas une forme.</p>

<h2 id="ce-que-mesure-lhorizon"><span class="tei-section-num">03</span>Ce que mesure le protocole de l'horizon</h2>
<p>La dépression de l'horizon, notée δ, est l'angle entre l'horizontale vraie — celle que définit le fil à plomb — et la direction dans laquelle on voit la ligne d'horizon marin. Sur une surface courbe, cette ligne est en dessous de l'horizontale, et d'autant plus bas qu'on est haut. Sur une surface plane, le point de fuite est dans le plan horizontal de l'œil, quelle que soit la hauteur de l'œil.</p>
{fig1}
<p><em>Figure 1 — L'observable, dans les deux modèles. La courbure du panneau de gauche est très fortement exagérée&nbsp;: à 3&nbsp;107&nbsp;m d'altitude, δ vaut 100 minutes d'arc, soit un degré et sept dixièmes.</em></p>
<p>L'intérêt de cette grandeur est métrologique, et il est décisif&nbsp;: <strong>la réfraction atmosphérique n'y intervient qu'au second ordre</strong>. On l'absorbe dans un rayon apparent R′ = R/(1−k), où k est le coefficient de réfraction. Or sur toute la plage physiquement défendable de k, de 0 à 0,47, la prédiction sphérique ne descend que de 107′ à 78′. La prédiction plane, elle, reste zéro.</p>
<p>Autrement dit&nbsp;: même en accordant à la réfraction sa valeur la plus défavorable, il reste 78 minutes d'arc entre les deux modèles. C'est la première mesure de notre dossier où l'incertitude sur la réfraction est plus petite que l'écart à mesurer.</p>

<h2 id="pourquoi-decidable"><span class="tei-section-num">04</span>Pourquoi la question est décidable</h2>
<p>Voici le graphique qui justifie à lui seul de monter l'expérience. Toutes les barres sont à la même échelle.</p>
{fig2}
<p><em>Figure 2 — L'écart entre les modèles, et l'incertitude de la mesure, dans la même unité. Station à 3&nbsp;107&nbsp;m d'altitude.</em></p>
<p>Le budget instrumental de 2,20′ n'est pas une estimation optimiste&nbsp;: il suppose le poste dominant déjà éliminé. Le zéro d'un inclinomètre ordinaire vaut 3,0′ à lui seul, et il disparaît par retournement du boîtier — on mesure deux fois, appareil à l'endroit puis à l'envers, et le décalage s'annule dans la moyenne. Il reste 1,5′ de répétabilité de remise en station, 1,0′ de définition de la ligne d'horizon, et l'échelle angulaire ramenée à 0,05′ par astrométrie de champ plutôt que par la focale nominale de l'objectif.</p>
<p>Toutes les altitudes ne se valent pas. C'est le point que les amateurs sous-estiment le plus souvent&nbsp;: une mesure depuis une plage ne tranche rien, et ce n'est pas une question de soin.</p>
<table class="tei-table">
  <thead><tr><th>altitude de l'œil</th><th>dépression prédite (k = 0,13)</th><th>incertitude totale</th><th>rapport contre la prédiction plane</th><th>usage</th></tr></thead>
  <tbody>
    <tr><td>5 m</td><td>4,0′</td><td>2,20′</td><td>1,4</td><td>indicatif seulement</td></tr>
    <tr><td>10 m</td><td>5,7′</td><td>2,20′</td><td>2,0</td><td>indicatif seulement</td></tr>
    <tr><td>50 m</td><td>12,7′</td><td>2,22′</td><td>4,5</td><td>contributif</td></tr>
    <tr><td>120 m</td><td>19,7′</td><td>2,26′</td><td>7,0</td><td>contributif</td></tr>
    <tr><td>300 m</td><td>31,1′</td><td>2,34′</td><td>11,0</td><td>solide</td></tr>
    <tr><td>1 000 m</td><td>56,8′</td><td>2,65′</td><td>20,2</td><td>solide</td></tr>
    <tr><td>3 107 m</td><td>100,1′</td><td>3,41′</td><td>35,5</td><td>décisif</td></tr>
  </tbody>
</table>
<p><em>Ce que vaut chaque altitude. L'incertitude est donnée à 1&nbsp;σ. La dernière colonne chiffrée rapporte le signal le plus défavorable — celui obtenu à k = 0,47 — au seul budget instrumental de 2,20′.</em></p>
<p>À cinq mètres au-dessus de l'eau, deux mètres de marée valent 41&nbsp;% de δ. La campagne doit donc comporter au moins une station au-dessus de 300 m, et les autres réparties régulièrement en √h — pas en h, puisque c'est √h qui est la variable de l'ajustement.</p>

<div class="tei-fait experiences">
  <span class="tei-fait-label">CE QUE L'EXPÉRIENCE ÉTABLIT</span>
  <p>Depuis 3&nbsp;107 m, l'écart entre les deux prédictions vaut au minimum 78,2 minutes d'arc, contre une incertitude instrumentale de 2,20 minutes d'arc. Rapport signal sur bruit&nbsp;: 35,5. Ce chiffre est calculé avant toute image — c'est lui qui autorise à monter l'expérience, et c'est son absence qui condamne la plupart des observations amateurs à ne rien trancher.</p>
</div>

<h2 id="ordre-des-operations"><span class="tei-section-num">05</span>L'ordre des opérations</h2>
<p>C'est la partie du protocole dont personne ne soupçonne l'existence avant d'avoir raté une soirée. Les éléments nécessaires sont dispersés dans six sections du document&nbsp;; l'ordre dans lequel on les prend, lui, n'est écrit qu'une fois.</p>
{fig3}
<p><em>Figure 3 — Les six phases et leur ordre contraignant. Les phases marquées d'un trait rose contiennent au moins une étape irréversible.</em></p>
<p>Une remarque sur la phase 0, parce qu'elle surprend&nbsp;: <strong>le dépôt précède la première image</strong>. Le protocole est figé, son empreinte SHA-256 calculée, le fichier déposé, le DOI obtenu et publié — et seulement ensuite on photographie. C'est ce qui rend impossible l'objection la plus efficace contre n'importe quel résultat&nbsp;: «&nbsp;les prédictions ont été écrites après avoir vu les données&nbsp;».</p>
<p>Ce dispositif rend la tricherie détectable. Il ne la rend pas impossible&nbsp;: c'est la publication intégrale des fichiers bruts qui fait le reste du travail.</p>

<h2 id="ce-quun-protocole-ne-fait-pas"><span class="tei-section-num">06</span>Ce qu'un protocole ne fait pas</h2>
<p>Il ne conclut pas sur la forme de la Terre.</p>
<p>Chacun de nos protocoles mesure une grandeur précise et écarte une famille de modèles. Aucun ne prétend trancher davantage, et nous tenons à le dire ici plutôt que de laisser le lecteur le déduire. Le protocole de l'horizon détermine si δ croît comme √h ou reste nul&nbsp;; c'est beaucoup, ce n'est pas tout.</p>
<p>Il ne discute pas non plus les travaux d'autrui. Ce débat existe, il est légitime, et il a sa place — ailleurs. Pas dans le document qu'on remet à quelqu'un pour qu'il fasse la mesure lui-même. Un protocole qui plaide n'est plus un protocole&nbsp;; il devient l'argumentaire d'un camp, et l'observateur qui le suit ne mesure plus, il vérifie une thèse.</p>
<p>Enfin, il ne garantit rien sur la qualité des mesures qui suivront. Il garantit qu'à la date du DOI, ce texte-là existait, avec ce contenu-là, y compris ses critères de décision et ses deux issues possibles.</p>

<h2 id="les-protocoles"><span class="tei-section-num">07</span>Les protocoles</h2>
<p>Deux documents sont arrêtés. Deux autres sont gelés, et nous préférons le dire que laisser croire à un catalogue plus fourni qu'il ne l'est.</p>
<table class="tei-table">
  <thead><tr><th>protocole</th><th>ce qu'il mesure</th><th>langues</th><th>version</th><th>état</th></tr></thead>
  <tbody>
    <tr><td><strong>Dépression de l'horizon marin</strong></td><td>l'angle δ entre l'horizontale vraie et la ligne d'horizon, en fonction de l'altitude</td><td>français, anglais</td><td>1.9</td><td>arrêté, DOI en cours de dépôt</td></tr>
    <tr><td><strong>Dépression de l'horizon depuis un ballon stratosphérique</strong></td><td>l'angle entre deux points diamétralement opposés de l'horizon, de 2 à 30 km</td><td>bilingue</td><td>1.1</td><td>arrêté, dépôt à suivre</td></tr>
    <tr><td>Diamètre angulaire du Soleil</td><td>—</td><td>—</td><td>—</td><td>suspendu</td></tr>
    <tr><td>Hauteur du pôle céleste</td><td>—</td><td>—</td><td>—</td><td>suspendu</td></tr>
  </tbody>
</table>
<p><em>État des protocoles au 30 août 2026.</em></p>

<h3>Pourquoi les fichiers ne sont pas encore en téléchargement ici</h3>
<p>Le protocole de l'horizon porte, depuis sa version 1.6, un emplacement réservé pour son propre DOI — en première page et en section finale. Tant que cet emplacement est vide, le fichier ne doit pas circuler&nbsp;: deux exemplaires distincts se réclamant du même numéro de version seraient exactement l'ambiguïté que le préenregistrement existe pour écarter.</p>
<p>Les PDF seront donc mis en ligne ici <strong>après</strong> l'inscription du DOI, et ce seront les exemplaires exacts déposés — pas des rendus refaits. Un rendu PDF n'est pas reproductible octet à octet, le moteur y inscrivant un horodatage&nbsp;: l'empreinte SHA-256 ne vaut que pour l'exemplaire précis qui a été déposé.</p>

<h3>Le second protocole, en deux mots</h3>
<p>Le protocole ballon mesure la même grandeur autrement, et il a un avantage que celui de l'horizon n'a pas. L'observable y est l'angle entre <em>deux</em> points diamétralement opposés de l'horizon, vus dans une seule image&nbsp;: 180° − 2δ sur une sphère, 180° sur un plan. Une inclinaison de la nacelle ajoute autant d'un côté qu'elle retranche de l'autre — la somme est invariante, et aucune référence verticale n'est nécessaire à bord. C'est ce qui rend la mesure possible sur une nacelle qui balance.</p>
<p>Surtout, la réfraction y cesse d'être supposée. L'invariant de Bouguer donne cos δ = n₀(R+t)/n₁(R+h)&nbsp;: la correction ne dépend que de l'indice de l'air aux deux extrémités du rayon, donc de la pression et de la température au sol et à bord — quatre grandeurs <em>mesurées</em>. Aucun coefficient k n'apparaît dans ce protocole.</p>
<p>Et le critère de décision y est une <em>variation</em>, non une valeur&nbsp;: entre 2 et 30 km d'altitude, l'angle change de 488′ sur une sphère et de zéro sur un plan. Tout décalage instrumental constant disparaît dans la différence.</p>

<h2 id="sources"><span class="tei-section-num">08</span>Sources</h2>
<ol>
  <li>Ciddor, P. E. (1996). Refractive index of air&nbsp;: new equations for the visible and near infrared. <em>Applied Optics</em>, 35(9), 1566–1573. — fonde la relation n = 1 + 77,6×10⁻⁶ P/T employée dans les deux protocoles.</li>
  <li>Nosek, B. A., Ebersole, C. R., DeHaven, A. C., Mellor, D. T. (2018). The preregistration revolution. <em>Proceedings of the National Academy of Sciences</em>, 115(11), 2600–2606. — sur ce que le préenregistrement établit, et ce qu'il n'établit pas.</li>
  <li>Zenodo, <em>Reserve DOI</em> — procédure d'attribution d'un identifiant avant publication d'un dépôt&nbsp;: <a href="https://help.zenodo.org/docs/deposit/describe-records/reserve-doi/" rel="nofollow noopener" target="_blank">help.zenodo.org</a>. Consulté le 30 août 2026.</li>
  <li>Coefficient de réfraction géodésique standard k = 0,13, et sa dépendance k = 503·(P/T²)·(0,0342 + dT/dh) avec P en hectopascals — relation classique de la géodésie, rappelée en section 02 du protocole de l'horizon.</li>
  <li><a href="/article/standards-et-methode">Standards et méthode</a> — les règles générales du site, dont la grille de sourçage A/B/C/D et le préenregistrement des prédictions.</li>
  <li>Les valeurs numériques citées ici — 107,4′, 100,1′, 78,2′, budget 2,20′ et 3,41′, rapports 35,5 et 29,4 — proviennent des tableaux 7 à 10 du protocole de dépression de l'horizon, version 1.9, et se recalculent depuis les formules qu'il énonce.</li>
</ol>
"""

ARTICLE = {
    "title": "Qu'est-ce qu'un protocole, et pourquoi nous en écrivons",
    "description": (
        "Une observation ne tranche rien tant que manquent la prédiction chiffrée de "
        "chaque modèle, l'incertitude, les conditions du moment et le critère fixé "
        "d'avance. Les six règles que nous nous sommes données, le rapport signal sur "
        "bruit qui rend la question décidable, et l'ordre des opérations en six phases."
    ),
    "date": "2026-08-30",
    "author": "Terre Etendue",
    "category": "experiences",
    "tags": ["protocole", "methode", "pre-enregistrement", "budget-d-erreur",
             "depression-de-l-horizon", "refraction", "doi", "reproductible"],
    "pinned": False,
    "htmlBody": CORPS,
}

CIBLE.write_text(json.dumps(ARTICLE, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("écrit :", CIBLE, "—", len(CORPS), "caractères de corps")
