#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Écrit content/articles/participer-aux-campagnes-de-mesure.json.

    python3 scripts/generer-page-participer.py

La page d'appel. Elle a une fonction que « Qu'est-ce qu'un protocole » n'a
pas : celle-ci explique ce qu'est un protocole, celle-là demande à des gens
d'en exécuter un, et invite ceux qui en ont les moyens à en écrire.

Le contact passe par un lien mailto avec objet et corps préremplis. Le site
est statique et n'a pas de serveur pour recevoir un formulaire ; un mailto
fonctionne partout, ne dépend de personne, et laisse une trace chez
l'expéditeur — ce qu'un formulaire ne fait pas.
"""

import json
import pathlib
import urllib.parse

RACINE = pathlib.Path(__file__).resolve().parent.parent
CIBLE = RACINE / "content" / "articles" / "participer-aux-campagnes-de-mesure.json"
ADRESSE = "terreplane25@gmail.com"


def lien(objet, corps, texte, style=""):
    url = "mailto:%s?subject=%s&body=%s" % (
        ADRESSE,
        urllib.parse.quote(objet),
        urllib.parse.quote(corps.replace("\n", "\r\n")),
    )
    return '<a href="%s"%s>%s</a>' % (url, style, texte)


CORPS_HORIZON = """Bonjour,

Je souhaite participer a la campagne de mesure de la depression de l'horizon marin.

Ce que je peux apporter
-----------------------
Altitude(s) accessible(s) :
Facade maritime / plan d'eau vise :
Materiel photographique :
Experience prealable en photographie ou en astronomie :

Ce sur quoi je m'engage
-----------------------
[ ] Je transmettrai les fichiers bruts, quel que soit le resultat.
[ ] Je releverai les conditions atmospheriques au moment de la pose.
[ ] Je n'ai encore fait aucune acquisition.

Contact :
"""

CORPS_PROTOCOLE = """Bonjour,

Je souhaite proposer un protocole, ou en discuter un avant de l'ecrire.

Grandeur mesuree :
Ce que chaque modele predit, en chiffres :
Budget d'erreur envisage :
Critere de decision :
Ce que le protocole n'etablirait pas :

Contact :
"""

BOUTON = (' style="display:inline-block;background:var(--rose);color:#0D1528;'
          'font-weight:700;padding:14px 26px;border-radius:10px;text-decoration:none"')

CORPS = f"""<p class="tei-lede">Un protocole déposé qui n'est exécuté par personne ne vaut pas mieux qu'une opinion. Nous en avons publié un, préenregistré et horodaté&nbsp;; il attend maintenant des gens pour le faire, et des contradicteurs pour en écrire de meilleurs.</p>

<h2 id="avant-de-commencer">Avant de commencer</h2>
<p>Cette page est un appel, et rien d'autre. Si vous cherchez à comprendre <em>ce qu'est</em> un protocole et pourquoi nous en écrivons, c'est <a href="/article/les-protocoles-ce-que-c-est-et-pourquoi">l'autre page</a> qu'il faut lire d'abord.</p>
<p>Celle-ci s'adresse à deux publics à la fois, et l'un n'est pas l'autre&nbsp;: <strong>ceux qui veulent exécuter une mesure</strong>, et <strong>ceux qui ont les moyens d'en concevoir une</strong>. Les seconds n'ont pas besoin d'être d'accord avec nous. C'est même préférable qu'ils ne le soient pas.</p>

<h2 id="pourquoi"><span class="tei-section-num">01</span>Pourquoi nous cherchons des participants</h2>
<p>Une mesure faite par une seule personne, à un seul endroit, ne tranche rien — quel que soit son soin. Ce qui tranche, c'est une <strong>loi</strong>&nbsp;: la même grandeur mesurée à plusieurs altitudes, par plusieurs observateurs, avec le même critère de pointé, et l'ensemble ajusté.</p>
<p>C'est pourquoi le protocole demande au moins une station au-dessus de 300&nbsp;m et les autres réparties régulièrement — non pour être plus précis, mais pour mesurer une chose qu'une station unique ne peut pas produire&nbsp;: la façon dont l'angle varie avec la hauteur.</p>
<div class="tei-fait experiences">
  <span class="tei-fait-label">CE QUE L'EXPÉRIENCE ÉTABLIT</span>
  <p>Une station isolée donne un nombre. Sept stations étagées donnent une pente, et c'est la pente qui départage les deux modèles&nbsp;: une sphère prédit que la dépression croît comme la racine de l'altitude, un plan prédit qu'elle reste nulle partout.</p>
</div>

<h2 id="protocoles"><span class="tei-section-num">02</span>Les protocoles, et ce qu'ils demandent</h2>

<h3>Dépression de l'horizon marin — <span style="color:var(--opal)">ouvert aux participants</span></h3>
<p>Photographier, dans une seule image, une étoile ou une planète, son reflet dans une nappe d'huile, et la ligne d'horizon marin. Le milieu entre l'astre et son reflet donne l'horizontale vraie&nbsp;; l'écart entre ce milieu et l'horizon est la grandeur cherchée.</p>
<p><strong>Ce qu'il faut&nbsp;:</strong> un boîtier à objectifs interchangeables sachant écrire en brut — un reflex d'occasion suffit —, un 100&nbsp;mm à focale fixe, un trépied, un plat à gratin et de l'huile de paraffine. Un thermomètre infrarouge et un baromètre de téléphone. Des logiciels libres pour la réduction.</p>
<p><strong>Ce qui compte le plus&nbsp;:</strong> l'altitude. Sous 50&nbsp;m la mesure n'est qu'indicative&nbsp;; au-dessus de 300&nbsp;m elle devient solide&nbsp;; à 3&nbsp;000&nbsp;m elle est décisive. Une façade maritime dégagée sur toute la portée théorique est indispensable.</p>
<p><strong>Version 1.9, déposée le 30 août 2026</strong> — DOI <a href="https://doi.org/10.5281/zenodo.22167798" rel="nofollow noopener" target="_blank">10.5281/zenodo.22167798</a>, licence CC BY 4.0. Les deux exemplaires, français et anglais, sont en téléchargement sur <a href="/article/les-protocoles-ce-que-c-est-et-pourquoi">la page des protocoles</a>.</p>

<h3>Les trois mires sur un plan d'eau — <span style="color:var(--saffron)">prêt, non déposé</span></h3>
<p>Trois perches identiques plantées dans un plan d'eau calme, la centrale graduée. On vise le sommet de la première vers celui de la troisième et on lit la graduation de celle du milieu. À deux kilomètres, les deux modèles prédisent des lectures qui diffèrent de sept centimètres.</p>
<p><strong>Ce qu'il faut&nbsp;:</strong> trois perches, un tube de PVC percé pour tranquilliser l'eau, une lunette, un plan d'eau de deux à dix kilomètres. Une après-midi suffit pour le premier point.</p>
<p>Les prédictions sont figées depuis le 2 août 2026 dans un fichier public daté. Le protocole n'est pas encore déposé&nbsp;: il le sera avant toute campagne. Le mode d'emploi est là&nbsp;: <a href="/article/monter-l-experience-des-trois-mires">Monter l'expérience des trois mires</a>.</p>

<h3>Dépression de l'horizon depuis un ballon stratosphérique — <span style="color:var(--ink-muted)">en attente</span></h3>
<p>L'angle entre deux points diamétralement opposés de l'horizon, vus dans une seule image depuis 2 à 30&nbsp;km&nbsp;: 180° moins deux fois la dépression sur une sphère, 180° sur un plan. Le critère est une <em>variation</em> et non une valeur, ce qui élimine tout décalage instrumental constant.</p>
<p>Le document est rédigé. Il n'est ni déposé ni diffusé, pour une raison que nous préférons dire&nbsp;: <strong>sa modélisation n'est pas encore confirmée de notre côté</strong>. Donner un DOI à une hypothèse de travail est exactement ce que notre propre règle interdit.</p>

<h2 id="postuler"><span class="tei-section-num">03</span>Prendre part à une mesure</h2>
<p>Écrivez-nous. Le message ci-dessous s'ouvre prérempli avec les seules informations dont nous avons besoin pour savoir si une station est utilisable — et pour vous dire franchement quand elle ne l'est pas.</p>
<p style="margin:26px 0">{lien("Participation — protocole de dépression de l'horizon", CORPS_HORIZON, "Proposer une station de mesure", BOUTON)}</p>
<p><strong>Ce que nous vous demandons</strong>&nbsp;: de transmettre les fichiers bruts <em>quel que soit le résultat</em>, de relever les conditions atmosphériques au moment de la pose, et de n'avoir rien photographié avant d'avoir lu la phase 0. Une station n'est écartée que sur un motif écrit et publié&nbsp;; jamais parce que le chiffre déplaît.</p>
<p><strong>Ce que nous ne vous demandons pas</strong>&nbsp;: d'être d'accord avec nous, d'avoir un diplôme, ni de croire quoi que ce soit. Le protocole énonce ses deux issues possibles avant la mesure. Si vos données donnent tort à ce que nous pensons, elles seront publiées telles quelles, avec votre nom si vous le souhaitez.</p>
<p><strong>Ce que vous obtenez&nbsp;:</strong> vos données publiées avec les autres, l'ajustement complet, et le résultat qu'il impose. Rien de plus, et c'est déjà ce qui manque le plus souvent.</p>

<h2 id="scientifiques"><span class="tei-section-num">04</span>Aux scientifiques : écrivez les vôtres</h2>
<p>C'est la partie de cette page qui nous tient le plus à cœur, et elle ne demande pas d'être d'accord avec nous.</p>
<p>Nous n'avons trouvé, sur les questions que ce site examine, <strong>aucune campagne d'observation longue distance préenregistrée</strong>&nbsp;: avec ses prédictions écrites avant l'acquisition, son budget d'erreur poste par poste, ses conditions atmosphériques relevées et ses données brutes publiées. Il en existe peut-être&nbsp;; nous n'en avons pas trouvé, et nous serions sincèrement heureux qu'on nous en signale une.</p>
<p>En attendant, la seule chose que nous puissions faire est d'en écrire et d'en déposer. Un protocole qui vous donnerait tort à nous serait le meilleur service à rendre au débat — et si vous en écrivez un, nous l'exécuterons.</p>
<p>Ce qu'un protocole doit contenir pour que nous le prenions au sérieux, et que nous nous imposons&nbsp;:</p>
<ul>
  <li><strong>L'observable et les deux prédictions chiffrées</strong>, écrites avant toute acquisition.</li>
  <li><strong>Un budget d'erreur poste par poste</strong>, avec son total à 1&nbsp;σ. Si ce total approche l'écart à mesurer, la mesure ne tranche pas et il vaut mieux le savoir avant.</li>
  <li><strong>Les critères de décision fixés d'avance</strong>, y compris ceux qui vous font perdre.</li>
  <li><strong>L'ordre des opérations</strong>, en signalant les étapes qui ne se rattrapent pas.</li>
  <li><strong>Un dépôt horodaté</strong> avant la première mesure, et les données brutes publiées après.</li>
</ul>
<p style="margin:26px 0">{lien("Proposition de protocole", CORPS_PROTOCOLE, "Proposer ou discuter un protocole", BOUTON)}</p>
<div class="tei-fait experiences">
  <span class="tei-fait-label">CE QUE L'EXPÉRIENCE ÉTABLIT</span>
  <p>Rien, pour l'instant. Aucune campagne n'a commencé, et cette page ne rapporte aucun résultat. Elle dit ce qui est prêt à être fait, par qui, et à quelles conditions — et elle sera remplacée par des chiffres, ou par l'aveu qu'il n'y en a pas.</p>
</div>

<h2 id="sources"><span class="tei-section-num">05</span>Sources</h2>
<p class="tei-src-legende">Chaque source porte sa classe de vérifiabilité. Elle ne dit pas si la source est bonne, mais ce qu&#8217;elle permet de faire&nbsp;: <b>A</b> mesure directe, protocole et instrument connus &#8212; conclure. <b>B</b> chemin mesuré mais indirect &#8212; borner. <b>C</b> valeur rapportée, calculée depuis un modèle, ou source primaire non consultée &#8212; illustrer, jamais conclure. <b>D</b> déclarative, affirmée sans donnée jointe &#8212; rien. <b>renvoi</b> désigne un de nos propres articles, qui n&#8217;est pas une source. La grille est détaillée dans <a href="/article/standards-et-methode">Standards et méthode</a>.</p>
<ol>
<li><span class="tei-grade grade-a">A</span> Protocole de mesure de la dépression de l'horizon marin en fonction de l'altitude, version 1.9, français et anglais. Zenodo, 30 août 2026. <a href="https://doi.org/10.5281/zenodo.22167798" rel="nofollow noopener" target="_blank">doi.org/10.5281/zenodo.22167798</a>, licence CC BY 4.0.</li>
<li><span class="tei-grade grade-a">A</span> Dépôt du site, <code>content/reseau/protocole-cote-trois-mires.json</code> v1.3, 2 août 2026&nbsp;: préenregistrement des prédictions, budget d'erreur et règles de rejet de l'expérience des trois mires.</li>
<li><span class="tei-grade grade-c">C</span> Nosek, B. A., Ebersole, C. R., DeHaven, A. C., Mellor, D. T. (2018). The preregistration revolution. <em>Proceedings of the National Academy of Sciences</em>, 115(11), 2600–2606.</li>
<li><span class="tei-grade grade-lien">renvoi</span> <a href="/article/les-protocoles-ce-que-c-est-et-pourquoi">Qu'est-ce qu'un protocole, et pourquoi nous en écrivons</a> — les six règles et le budget d'erreur en détail.</li>
<li><span class="tei-grade grade-lien">renvoi</span> <a href="/article/monter-l-experience-des-trois-mires">Monter l'expérience des trois mires</a> — le mode d'emploi complet.</li>
<li><span class="tei-grade grade-lien">renvoi</span> <a href="/article/standards-et-methode">Standards et méthode</a> — les règles que nous nous imposons, dont le préenregistrement.</li>
</ol>
"""

ARTICLE = {
    "title": "Participer : nos protocoles, et comment y prendre part",
    "description": (
        "Un protocole déposé que personne n'exécute ne vaut pas mieux qu'une opinion. "
        "Ce que chaque protocole demande, ce qu'il faut comme matériel, comment proposer "
        "une station de mesure — et un appel aux scientifiques pour qu'ils écrivent les "
        "leurs, y compris contre nous."
    ),
    "date": "2026-08-30",
    "author": "Terre Etendue",
    "category": "experiences",
    "tags": ["participer", "protocole", "campagne", "appel", "pre-enregistrement",
             "collaboration", "donnees-ouvertes"],
    "pinned": True,
    "htmlBody": CORPS,
}

CIBLE.write_text(json.dumps(ARTICLE, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("écrit :", CIBLE.name, "—", len(CORPS), "caractères")
