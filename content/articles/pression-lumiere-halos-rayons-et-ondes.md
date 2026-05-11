---
title: "Pression, lumière, halos, rayons et ondes"
description: ".nx-nav{width:100%;background:#F7F2E8;border-bottom:1px solid #DDD5C5;padding:0 2rem;position:sticky;top:0;z-index:999} .nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;ju..."
date: "2026-04-17"
author: "Terre Etendue"
category: "observatory"
tags: ["lobservatoire"]
---

.nx-nav{width:100%;background:#F7F2E8;border-bottom:1px solid #DDD5C5;padding:0 2rem;position:sticky;top:0;z-index:999}
.nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:64px;gap:1.5rem}
/* Logo */
.nx-nav__logo{font-family:'Cormorant Garamond',Georgia,serif;font-size:1.1rem;font-weight:700;color:#B8860B;text-decoration:none;letter-spacing:-.01em;white-space:nowrap;flex-shrink:0}
.nx-nav__logo:hover{color:#D4A017}
/* Liens */
.nx-nav__links{display:flex;align-items:center;gap:1.8rem;list-style:none;margin:0;padding:0}
.nx-nav__links a{font-family:'Outfit',sans-serif;font-size:.73rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#5C4A3A;text-decoration:none;padding:.5em 0;position:relative;transition:color .3s ease;white-space:nowrap}
.nx-nav__links a::after{content:'';position:absolute;bottom:0;left:0;width:0;height:1px;background:#B8860B;transition:width .3s ease}
.nx-nav__links a:hover{color:#2C1810}
.nx-nav__links a:hover::after{width:100%}
/* Recherche */
.nx-nav__search{position:relative;flex-shrink:0}
.nx-nav__search-btn{background:none;border:none;cursor:pointer;color:#8A7A6A;font-size:1rem;padding:6px;transition:color .3s ease;display:flex;align-items:center}
.nx-nav__search-btn:hover{color:#B8860B}
.nx-nav__search-box{position:absolute;top:calc(100% + 12px);right:0;width:0;opacity:0;overflow:hidden;transition:all .35s cubic-bezier(.16,1,.3,1);background:#EDE5D5;border:1px solid #DDD5C5;border-radius:8px;padding:0;z-index:1000}
.nx-nav__search-box.open{width:300px;opacity:1;padding:.6rem}
.nx-nav__search-input{width:100%;background:transparent;border:none;outline:none;font-family:'Outfit',sans-serif;font-size:.82rem;color:#2C1810;padding:.4em .6em;caret-color:#B8860B}
.nx-nav__search-input::placeholder{color:#8A7A6A}
/* Hamburger */
.nx-nav__toggle{display:none;background:none;border:none;cursor:pointer;padding:8px;flex-shrink:0}
.nx-nav__toggle span{display:block;width:22px;height:2px;background:#5C4A3A;margin:5px 0;transition:all .3s ease}
/* Mobile */
@media(max-width:900px){
 .nx-nav__toggle{display:block}
 .nx-nav__links{display:none;position:absolute;top:64px;left:0;right:0;background:#EDE5D5;border-bottom:1px solid #DDD5C5;flex-direction:column;padding:1rem 2rem;gap:0}
 .nx-nav__links.open{display:flex}
 .nx-nav__links li{width:100%}
 .nx-nav__links a{display:block;padding:.8em 0;border-bottom:1px solid #141414}
 .nx-nav__links li:last-child a{border-bottom:none}
 .nx-nav__search-box.open{width:calc(100vw - 4rem);right:-1rem}
}


 [Terre Étendue Islam](/)
 
 
 

 - [Le Nexus](/le-nexus/)

 - [L'Observatoire](/lobservatoire/)

 - [La Bibliothèque](/la-bibliotheque/)

 - [Le Lab](/le-lab/)

 

 
 - @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Outfit:wght@300;400;500;600&family=Amiri:ital,wght@0,400;0,700;1,400&display=swap');
:root{--bg:#F7F2E8;--bg2:#EDE5D5;--bg3:#111;--cobalt:#1B5E3C;--cobalt-l:#2D8B57;--cobalt-g:rgba(30,58,138,.15);--t1:#2C1810;--t2:#5C4A3A;--t3:#8A7A6A;--bdr:#DDD5C5;--f1:'Cormorant Garamond',Georgia,serif;--f2:'Outfit',sans-serif;--f3:'Cormorant Garamond',Georgia,serif}
.o6{background:var(--bg);color:var(--t1);padding:0}
.o6-h{padding:5rem 2rem 3.5rem;text-align:center;position:relative;overflow:hidden}
.o6-h::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 50% at 50% 30%,rgba(30,58,138,.05),transparent 70%);pointer-events:none}
.o6-tag{display:inline-block;font-family:var(--f2);font-size:.62rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--cobalt-l);background:var(--cobalt-g);border:1px solid rgba(30,58,138,.25);padding:.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.o6-title{font-family:var(--f1);font-size:clamp(1.8rem,4.5vw,2.6rem);font-weight:700;color:var(--cobalt-l);line-height:1.15;margin:0 0 1rem;max-width:800px;margin-left:auto;margin-right:auto}
.o6-sub{font-family:var(--f3);font-size:1.02rem;line-height:1.7;color:var(--t2);max-width:650px;margin:0 auto 2rem}
.o6-meta{max-width:800px;margin:0 auto;padding:1.2em 0;border-top:1px solid var(--bdr);border-bottom:1px solid var(--bdr);display:flex;flex-wrap:wrap;gap:.5em 2em;font-family:var(--f2);font-size:.75rem;color:var(--t3)}
.o6-meta dt{font-weight:600;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem}
.o6-meta dd{margin:0 0 .6em;color:var(--t2)}
.o6-lay{display:flex;gap:2.5rem;max-width:1200px;margin:0 auto;padding:2.5rem 2rem 5rem;align-items:flex-start}
.o6-nav{flex:0 0 255px;position:sticky;top:80px;max-height:calc(100vh - 100px);overflow-y:auto;padding:1.5rem;background:var(--bg2);border:1px solid var(--bdr);border-radius:10px}
.o6-nav::-webkit-scrollbar{width:3px}.o6-nav::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}
.o6-nav__t{font-family:var(--f2);font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--cobalt-l);margin:0 0 1rem;padding-bottom:.6rem;border-bottom:1px solid var(--bdr)}
.o6-nav ul{list-style:none;padding:0;margin:0}.o6-nav li{margin-bottom:.35rem}
.o6-nav a{display:block;font-family:var(--f2);font-size:.76rem;color:var(--t3);text-decoration:none;padding:.4em .8em;border-radius:5px;border-left:2px solid transparent;transition:all .25s ease;line-height:1.35}
.o6-nav a:hover{color:var(--t1);background:rgba(30,58,138,.06);border-left-color:var(--cobalt-l)}
.o6-nav a.active{color:var(--cobalt-l);background:var(--cobalt-g);border-left-color:var(--cobalt-l);font-weight:500}
.o6-nav .num{font-size:.6rem;font-weight:600;color:var(--cobalt-l);margin-right:.4em;opacity:.7}
.o6-nav__bk{display:block;margin-top:1.2rem;padding:.6em 1em;background:#2D8B57;color:#2C1810;font-family:var(--f2);font-size:.72rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;text-align:center;border-radius:5px;transition:background .3s ease}
.o6-nav__bk:hover{background:#3DA06A}
.o6-b{flex:1;min-width:0;max-width:800px;font-family:var(--f3);font-size:clamp(1rem,1.8vw,1.08rem);line-height:1.75;color:var(--t1)}
.o6-b p{margin-bottom:1.4em;text-align:justify;hyphens:auto}
.o6-b a{color:var(--cobalt-l);text-decoration:underline;text-underline-offset:3px}
.o6-b h2{font-family:var(--f1);font-size:clamp(1.4rem,3vw,1.85rem);font-weight:700;color:var(--t1);margin:3em 0 .8em;padding-bottom:.4em;border-bottom:1px solid var(--bdr);line-height:1.25;scroll-margin-top:90px}
.o6-b h3{font-family:var(--f2);font-size:clamp(1rem,1.8vw,1.15rem);font-weight:600;color:var(--cobalt-l);text-transform:uppercase;letter-spacing:.06em;margin:2em 0 .6em;line-height:1.35;scroll-margin-top:90px}
.sn{font-family:var(--f2);font-size:.65rem;font-weight:600;color:var(--cobalt-l);background:var(--cobalt-g);border:1px solid rgba(30,58,138,.25);padding:.2em .6em;border-radius:3px;margin-right:.6em;vertical-align:middle}
.db{margin:2em 0;padding:1.4em 1.8em;background:var(--bg2);border:1px solid var(--bdr);border-radius:8px}
.db__l{display:inline-block;font-family:var(--f2);font-size:.65rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:var(--cobalt-l);background:var(--cobalt-g);padding:.2em .7em;border-radius:3px;margin-bottom:.8em}
.db p{font-size:.92rem;margin-bottom:.8em;text-align:left}
.kp{margin:1.5em 0;padding:1.2em 1.6em;background:var(--bg2);border-left:3px solid var(--cobalt);border-radius:0 8px 8px 0;font-family:var(--f2);font-size:.9rem;line-height:1.6;color:var(--t2)}
.kp strong{color:var(--t1)}
.tw{margin:2em 0;overflow-x:auto}
.tb{width:100%;border-collapse:collapse;font-family:var(--f2);font-size:.78rem}
.tb th{background:var(--bg2);color:var(--cobalt-l);font-weight:600;text-transform:uppercase;letter-spacing:.06em;font-size:.66rem;padding:.7em .8em;text-align:left;border-bottom:1px solid var(--bdr)}
.tb td{padding:.6em .8em;border-bottom:1px solid var(--bdr);color:var(--t2);vertical-align:top}
.tb tr:hover td{background:rgba(30,58,138,.03)}
.o6-refs{margin-top:3em;padding-top:2em;border-top:1px solid var(--bdr)}
.o6-refs h2{border-bottom:none;padding-bottom:0;font-size:1.3rem}
.o6-refs ol{padding-left:1.5em;font-family:var(--f2);font-size:.82rem;color:var(--t2);line-height:1.7}
.o6-refs li{margin-bottom:.6em}
@media(max-width:900px){.o6-lay{flex-direction:column;padding:1.5rem}.o6-nav{position:static;flex:none;width:100%;max-height:none;margin-bottom:2rem}.o6-h{padding:3.5rem 1.5rem 2.5rem}}


 L'Observatoire — OBS-2026-006
 
# Pression, lumière, halos, rayons et ondes : la physique observable

 Des phénomènes que tout le monde peut observer et reproduire — et dont les implications cosmologiques sont rarement examinées.
 
 AuteurTerre Étendue Islam
 DateAvril 2026 — v1.0
 Lecture~30 min
 DomainePhysique · Optique · Électromagnétisme
 

 
 
## Sommaire

 
 [01 Pression atmosphérique](#p-pression)

 - [02 Lumière et couleurs](#p-lumiere)

 - [03 Halos solaires et lunaires](#p-halos)

 - [04 Rayons crépusculaires](#p-rayons)

 - [05 Électromagnétisme et ondes](#p-em)

 - [06 Acoustique](#p-son)

 - [07 Synthèse](#p-synthese)

 - [Références](#p-refs)

 

 [← Retour à l'Observatoire](/lobservatoire/)
 

## 01 Pression atmosphérique : un milieu dense, pas le vide

La pression atmosphérique standard au niveau de la mer est de **1 013,25 hPa** — soit environ 1 kg de force par cm² de surface, dans toutes les directions. Elle diminue régulièrement avec l'altitude : à 5 500 m, la moitié ; à 10 000 m (avion de ligne), 26% du sol ; au sommet de l'Everest, un tiers.


AltitudePression (hPa)% du solEffet

0 m (mer)1 013100%Référence
2 000 m79578%Stations de ski
5 500 m~50050%Moitié de l'oxygène
8 849 m (Everest)~33733%Limite sans oxygène artificiel
10 000 m (avion)26526%Pressurisation obligatoire


**Implication cosmologique :** La pression atmosphérique prouve que l'atmosphère est un milieu physique réel, de masse et de densité mesurables, qui diminue progressivement avec l'altitude. Le modèle officiel postule qu'à une certaine altitude, cette atmosphère dense rencontre le « vide spatial infini ». Or un vide ne peut exister directement relié à un non-vide sans barrière physique. La transition d'une atmosphère pressurisée vers un vide absolu est un problème physique non résolu.
**Expérience reproductible :** Une bouteille plastique remplie d'eau chaude, refermée hermétiquement puis refroidie, s'écrase sous la pression extérieure. Une ventouse ne colle au mur que grâce à la pression atmosphérique — un trou la fait tomber. Ces expériences simples démontrent la réalité physique de cette pression.


## 02 Lumière et couleurs : du prisme à l'arc-en-ciel

La lumière blanche contient simultanément toutes les longueurs d'onde du spectre visible (380–780 nm). Un prisme les sépare par réfraction différentielle — le violet est le plus dévié, le rouge le moins. Un second prisme inversé recombine toutes les couleurs en lumière blanche, prouvant qu'elles étaient présentes dès le départ.


### Pourquoi le ciel est bleu et le Soleil rouge au coucher

La **diffusion de Rayleigh** : les molécules d'air diffusent préférentiellement les courtes longueurs d'onde (bleu, violet) dans toutes les directions — d'où le ciel bleu en journée. Au lever et au coucher, la lumière traverse une épaisseur d'atmosphère bien plus grande : le bleu est entièrement diffusé, seuls les rouges et oranges atteignent l'observateur.


Rowbotham note que cette épaisseur supplémentaire produit également un **effet de grossissement apparent** du Soleil — la lumière traversant un milieu plus dense apparaît avec un disque plus grand, comme un réverbère dans le brouillard. Ce phénomène est cohérent avec un Soleil local traversant des couches atmosphériques plus denses à l'horizon, et non avec un Soleil distant de 150 millions de km dont la taille angulaire ne devrait pas changer.


### L'arc-en-ciel : géométrie précise

Chaque gouttelette d'eau agit comme un prisme-miroir : la lumière entre, se réfracte, se réfléchit sur la face arrière, puis se réfracte à nouveau en sortant. Le rouge sort à 42° par rapport à la direction du Soleil, le violet à 40°. L'arc est toujours centré sur le **point anti-solaire** — le point diamétralement opposé au Soleil par rapport à l'observateur.


 📷 EMPLACEMENT IMAGE


 Photo d'arc-en-ciel + schéma du prisme


 Photo d'un arc-en-ciel réel + petit schéma montrant la décomposition prismatique.
Annoter les angles de sortie : rouge 42°, violet 40°.


 Remplacer ce bloc par : ![\2](\1)


## 03 Halos solaires et lunaires

Un halo est un anneau lumineux à **exactement 22°** autour du Soleil ou de la Lune, produit par la réfraction de la lumière à travers des cristaux de glace hexagonaux en suspension dans les cirrus (6 000–12 000 m). C'est l'un des phénomènes optiques les plus fréquents — visible plusieurs dizaines de fois par an — et pourtant rarement observé car peu de gens regardent le ciel autour du Soleil.


 📷 EMPLACEMENT IMAGE


 Photo d'un halo solaire à 22°


 Anneau lumineux complet autour du Soleil. Cristaux de glace hexagonaux dans les cirrus.
Annoter l'angle de 22° si possible.


 Remplacer ce bloc par : ![\2](\1)


PhénomèneAngleFréquenceCristaux

Halo à 22°22°Fréquent (100+/an)Hexagonaux aléatoires
Halo à 46°46°RareColonnes hexagonales
Parhélies (« chiens du Soleil »)22° latéralFréquentPlaques horizontales
Arc circumzénithalAu-dessus du SoleilAssez fréquentPlaques horizontales
Pilier solaireVerticalRarePlaques tombant lentement


Les halos lunaires fonctionnent sur le même principe, avec la lumière de la Lune. Dans de nombreuses traditions mondiales, un halo lunaire annonce la pluie — ce qui est physiquement fondé : les cirrus qui le produisent précèdent souvent les systèmes dépressionnaires.


## 04 Rayons crépusculaires : source distante ou projecteur local ?

Les rayons crépusculaires sont des faisceaux alternés d'air éclairé et d'ombre, projetés par les nuages et rendus visibles par la diffusion dans les particules atmosphériques. Ils semblent tous partir d'un **même point proche** — comme si le Soleil était un projecteur local plutôt qu'un astre à 150 millions de km.


 📷 EMPLACEMENT IMAGE


 Photo de rayons crépusculaires convergents


 Faisceaux lumineux à travers les nuages convergeant vers un point unique au-dessus des nuages.
Annoter le point de convergence apparent. Si possible, montrer aussi le point chaud sur les nuages.


 Remplacer ce bloc par : ![\2](\1)


Deux lectures, présentées honnêtement
**Lecture officielle :** Des rayons parallèles (source très distante) semblent converger vers un point de fuite par effet de perspective — comme les rails d'un chemin de fer. Les rayons crépusculaires sont parallèles en réalité.


**Lecture alternative :** En traçant les lignes de convergence sur des photos, le point d'intersection se situe clairement au-dessus des nuages, à quelques kilomètres d'altitude. Un point chaud lumineux est souvent visible sur les nuages directement sous le Soleil — impossible si la source est à 150 millions de km (illumination uniforme attendue, pas localisée).


L'argument anti-solaire (les rayons convergent aussi du côté opposé au Soleil) est souvent cité pour réfuter l'hypothèse locale. Mais cette convergence opposée est également cohérente avec une source locale : des rayons divergent depuis une source proche dans toutes les directions. Ce sont les **deux points de fuite** d'un même faisceau divergent.


## 05 Électromagnétisme : propagation sans satellites

Le spectre électromagnétique va des ondes radio (longueurs d'onde de kilomètres) aux rayons gamma (fractions de nanomètre). Deux bandes sont particulièrement pertinentes pour notre sujet : les ondes radio basses fréquences et les micro-ondes.


### L'ionosphère comme miroir naturel

💡 En termes simples


Très haut dans le ciel (entre 60 et 1 000 km d'altitude), il y a une couche d'air chargée électriquement par le Soleil — c'est l'ionosphère. Cette couche agit comme un miroir pour les ondes radio : un signal envoyé depuis le sol rebondit dessus et retombe à des milliers de kilomètres. C'est grâce à ce « miroir naturel » que la radio a fonctionné partout dans le monde dès 1901 — bien avant qu'un seul satellite n'existe. La question centrale est : si ce miroir naturel permet déjà les communications mondiales, à quoi servent exactement les satellites ?


L'ionosphère — couche de l'atmosphère supérieure ionisée par le rayonnement solaire — agit comme un **miroir naturel pour les ondes radio** de basses et moyennes fréquences. Les ondes émises depuis la surface terrestre rebondissent sur l'ionosphère et retombent à des milliers de kilomètres de distance. C'est ce principe qui a permis les communications radio intercontinentales **dès les années 1920** — des décennies avant le moindre satellite.


**Fait historique documenté :** Marconi a établi la première communication radio transatlantique en 1901, entre la Cornouailles (Angleterre) et Terre-Neuve (Canada) — 3 500 km — sans satellite. Le système LORAN a navigué dans le monde entier de 1942 à 2010 par triangulation d'émetteurs terrestres (voir [O5](/cartes-routes-boussoles-et-le-mystere-antarctique/)). La BBC a émis en ondes courtes vers le monde entier depuis les années 1930. Toutes ces communications fonctionnent par réflexion ionosphérique — un phénomène naturel qui ne dépend d'aucun satellite.
 📷 EMPLACEMENT IMAGE


 Photo historique de la station de Marconi (1901) ou schéma de la réflexion ionosphérique


 Schéma : émetteur terrestre → signal radio → rebond sur l'ionosphère → récepteur à 3 500 km.
Alternative : photo de la station de Poldhu (Cornouailles) ou Signal Hill (Terre-Neuve).


 Remplacer ce bloc par : ![\2](\1)


La question est directe : si les communications mondiales sont possibles par réflexion ionosphérique (ondes radio) et par câbles sous-marins (internet), quelle est la nécessité absolue des satellites ? Le GPS peut être répliqué par triangulation terrestre (eLORAN, précision ~10 m). La télévision par câble et fibre optique. L'internet par câbles sous-marins. Les communications voix par ondes radio ionosphériques.


## 06 Acoustique : le son voyage plus loin qu'il ne devrait

Le son se propage dans l'air à environ 343 m/s au niveau de la mer (à 20°C). Sa vitesse dépend de la température, de l'humidité et de la pression. Comme pour la lumière, la réfraction acoustique dévie le son vers les couches d'air plus denses (plus froides).


Des sons ont été documentés à des distances considérables : les éruptions volcaniques (Krakatoa 1883, entendu à 4 800 km), les canons navals (entendus à plus de 200 km dans certaines conditions), et même des voix humaines portant à plus de 10 km au-dessus de l'eau calme par nuit froide. Ces distances de propagation sonore sont cohérentes avec une surface plane — sur une surface courbe, la courbure créerait une zone d'ombre acoustique limitant la portée.


## 07 Synthèse : ce que la physique observable nous enseigne

Six phénomènes, six enseignements
**Pression :** L'atmosphère est un milieu dense et réel. Sa transition vers le « vide spatial » est un problème non résolu.


**Lumière :** Le grossissement apparent du Soleil à l'horizon est cohérent avec un Soleil local traversant des couches denses. La décomposition spectrale confirme les propriétés optiques de l'atmosphère.


**Halos :** Des phénomènes parfaitement expliqués par la physique optique — preuve que l'atmosphère contient des structures cristallines à haute altitude qui réfractent la lumière de manière mesurable et prédictible.


**Rayons crépusculaires :** La convergence vers un point proche et le point chaud localisé soulèvent des questions légitimes sur la distance du Soleil.


**Électromagnétisme :** Les communications mondiales sans satellites ont fonctionné pendant des décennies. L'ionosphère est un miroir naturel documenté.


**Acoustique :** La propagation sonore à très grande distance est cohérente avec une surface plane sans zone d'ombre de courbure.


## Références


 - Rowbotham, S.B. (1865). *Zetetic Astronomy: Earth Not a Globe* — grossissement solaire, décomposition spectrale.

 - Dubay, Eric. *200 Preuves* — preuves #125 (rayons crépusculaires), #159 (pression/vide).

 - Marconi, G. (1901). Communication transatlantique radio — Cornouailles → Terre-Neuve, 3 500 km.

 - Système LORAN — USCG, 1942–2010.

 - Greenler, R. (1980). *Rainbows, Halos, and Glories*. Cambridge University Press.

 - Lynch, D.K. & Livingston, W. (1995). *Color and Light in Nature*. Cambridge University Press.

 - Day, J.A. (2005). *The Book of Clouds*. Sterling Publishing.


					

.nx-footer{background:#2C1810;border-top:1px solid #DDD5C5;padding:4rem 2rem 2rem;font-family:'Outfit',sans-serif}
.nx-footer__inner{max-width:1100px;margin:0 auto}
.nx-footer__grid{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:3rem;margin-bottom:3rem}
.nx-footer__brand-name{font-family:'Cormorant Garamond',Georgia,serif;font-size:1.2rem;font-weight:700;color:#B8860B;margin:0 0 1rem}
.nx-footer__brand-desc{font-family:'Cormorant Garamond',Georgia,serif;font-size:.88rem;line-height:1.65;color:#8A7A6A;margin:0 0 1.5rem}
.nx-footer__brand-verse{font-family:'Cormorant Garamond',Georgia,serif;font-style:italic;font-size:.82rem;line-height:1.6;color:rgba(212,175,55,.4)}
.nx-footer__col-title{font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:#5C4A3A;margin:0 0 1.2rem}
.nx-footer__links{list-style:none;padding:0;margin:0}
.nx-footer__links li{margin-bottom:.7rem}
.nx-footer__links a{font-size:.82rem;color:#8A7A6A;text-decoration:none;transition:color .3s ease}
.nx-footer__links a:hover{color:#2C1810}
.nx-footer__sep{height:1px;background:#DDD5C5;margin-bottom:1.5rem}
.nx-footer__bottom{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem}
.nx-footer__copy{font-size:.72rem;color:#8A7A6A}
.nx-footer__socials{display:flex;gap:.8rem;align-items:center}
.nx-footer__socials a{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:6px;background:#EDE5D5;border:1px solid #DDD5C5;color:#8A7A6A;font-size:.75rem;text-decoration:none;transition:all .3s ease}
.nx-footer__socials a:hover{border-color:rgba(212,175,55,.3);color:#B8860B;transform:translateY(-2px)}
@media(max-width:768px){.nx-footer__grid{grid-template-columns:1fr;gap:2rem}.nx-footer{padding:3rem 1.5rem 1.5rem}.nx-footer__bottom{flex-direction:column;align-items:flex-start}}


 
 
## Terre Étendue Islam

 
 Un examen rigoureux des paradigmes cosmologiques, 
 croisant sources sacrées et observations empiriques.
 


 
 « Et la terre, comment elle a été étendue ? »

 — Al-Ghashiyah, 88:20
 


 
 
### Explorer

 

 - [Le Nexus](/le-nexus/)

 - [L'Observatoire](/lobservatoire/)

 - [La Bibliothèque](/la-bibliotheque/)

 - [Le Lab](/le-lab/)

 

 
 
### Ressources

 

 - [Glossaire](/glossaire/)

 - [Index thématique](/index-thematique/)

 - [Méthodologie](/methodologie/)

 

 
 
### À propos

 

 - [Manifeste](/manifeste/)

 - [Éthique intellectuelle](/ethique-intellectuelle/)

 - [Contact](/contact-2/)

 

 © 2026 Terre Étendue Islam — Tous droits réservés · [Mentions légales](/mentions-legales-2/)


 [▶](https://www.youtube.com/@TERREETENDUE)
 [◉](https://odysee.com/@terreetendue)
 [✈](https://t.me/LATERREETENDUE)
 [♪](https://tiktok.com/@terreetendue1)