---
title: "L'horizon, la perspective et la réfraction"
description: ".nx-nav{width:100%;background:#F7F2E8;border-bottom:1px solid #DDD5C5;padding:0 2rem;position:sticky;top:0;z-index:999} .nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;ju..."
date: "2026-04-16"
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
:root{--bg:#F7F2E8;--bg2:#EDE5D5;--bg3:#111;--gold:#B8860B;--gold-s:#B8962E;--gold-g:rgba(212,175,55,.12);--cobalt:#1B5E3C;--cobalt-l:#2D8B57;--cobalt-g:rgba(30,58,138,.15);--t1:#2C1810;--t2:#5C4A3A;--t3:#8A7A6A;--bdr:#DDD5C5;--f1:'Cormorant Garamond',Georgia,serif;--f2:'Outfit',sans-serif;--f3:'Cormorant Garamond',Georgia,serif}
.o4{background:var(--bg);color:var(--t1);padding:0}
.o4-h{padding:5rem 2rem 3.5rem;text-align:center;position:relative;overflow:hidden}
.o4-h::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 50% at 50% 30%,rgba(30,58,138,.05),transparent 70%);pointer-events:none}
.o4-tag{display:inline-block;font-family:var(--f2);font-size:.62rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--cobalt-l);background:var(--cobalt-g);border:1px solid rgba(30,58,138,.25);padding:.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.o4-title{font-family:var(--f1);font-size:clamp(1.8rem,4.5vw,2.6rem);font-weight:700;color:var(--cobalt-l);line-height:1.15;margin:0 0 1rem;max-width:800px;margin-left:auto;margin-right:auto}
.o4-sub{font-family:var(--f3);font-size:1.02rem;line-height:1.7;color:var(--t2);max-width:650px;margin:0 auto 2rem}
.o4-meta{max-width:800px;margin:0 auto;padding:1.2em 0;border-top:1px solid var(--bdr);border-bottom:1px solid var(--bdr);display:flex;flex-wrap:wrap;gap:.5em 2em;font-family:var(--f2);font-size:.75rem;color:var(--t3)}
.o4-meta dt{font-weight:600;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem}
.o4-meta dd{margin:0 0 .6em;color:var(--t2)}
.o4-lay{display:flex;gap:2.5rem;max-width:1200px;margin:0 auto;padding:2.5rem 2rem 5rem;align-items:flex-start}
.o4-nav{flex:0 0 255px;position:sticky;top:80px;max-height:calc(100vh - 100px);overflow-y:auto;padding:1.5rem;background:var(--bg2);border:1px solid var(--bdr);border-radius:10px}
.o4-nav::-webkit-scrollbar{width:3px}.o4-nav::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}
.o4-nav__t{font-family:var(--f2);font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--cobalt-l);margin:0 0 1rem;padding-bottom:.6rem;border-bottom:1px solid var(--bdr)}
.o4-nav ul{list-style:none;padding:0;margin:0}.o4-nav li{margin-bottom:.35rem}
.o4-nav a{display:block;font-family:var(--f2);font-size:.76rem;color:var(--t3);text-decoration:none;padding:.4em .8em;border-radius:5px;border-left:2px solid transparent;transition:all .25s ease;line-height:1.35}
.o4-nav a:hover{color:var(--t1);background:rgba(30,58,138,.06);border-left-color:var(--cobalt-l)}
.o4-nav a.active{color:var(--cobalt-l);background:var(--cobalt-g);border-left-color:var(--cobalt-l);font-weight:500}
.o4-nav .num{font-size:.6rem;font-weight:600;color:var(--cobalt-l);margin-right:.4em;opacity:.7}
.o4-nav__bk{display:block;margin-top:1.2rem;padding:.6em 1em;background:#2D8B57;color:#2C1810;font-family:var(--f2);font-size:.72rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;text-align:center;border-radius:5px;transition:background .3s ease}
.o4-nav__bk:hover{background:#3DA06A}
.o4-b{flex:1;min-width:0;max-width:800px;font-family:var(--f3);font-size:clamp(1rem,1.8vw,1.08rem);line-height:1.75;color:var(--t1)}
.o4-b p{margin-bottom:1.4em;text-align:justify;hyphens:auto}
.o4-b a{color:var(--cobalt-l);text-decoration:underline;text-underline-offset:3px}
.o4-b h2{font-family:var(--f1);font-size:clamp(1.4rem,3vw,1.85rem);font-weight:700;color:var(--t1);margin:3em 0 .8em;padding-bottom:.4em;border-bottom:1px solid var(--bdr);line-height:1.25;scroll-margin-top:90px}
.o4-b h3{font-family:var(--f2);font-size:clamp(1rem,1.8vw,1.15rem);font-weight:600;color:var(--cobalt-l);text-transform:uppercase;letter-spacing:.06em;margin:2em 0 .6em;line-height:1.35;scroll-margin-top:90px}
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
.o4-refs{margin-top:3em;padding-top:2em;border-top:1px solid var(--bdr)}
.o4-refs h2{border-bottom:none;padding-bottom:0;font-size:1.3rem}
.o4-refs ol{padding-left:1.5em;font-family:var(--f2);font-size:.82rem;color:var(--t2);line-height:1.7}
.o4-refs li{margin-bottom:.6em}
@media(max-width:900px){.o4-lay{flex-direction:column;padding:1.5rem}.o4-nav{position:static;flex:none;width:100%;max-height:none;margin-bottom:2rem}.o4-h{padding:3.5rem 1.5rem 2.5rem}}


 L'Observatoire — OBS-2026-004
 
# L'horizon, la perspective et la réfraction : ce que l'optique explique vraiment

 Quand une observation contredit le modèle globe, on invoque la réfraction ou la perspective. Sont-elles suffisantes ? Que prédisent-elles réellement ?
 
 AuteurTerre Étendue Islam
 DateAvril 2026 — v1.0
 Lecture~25 min
 DomainePhysique optique · Atmosphère
 

 
 
## Sommaire

 
 [01 Introduction](#h-intro)

 - [02 L'horizon au niveau des yeux](#h-horizon)

 - [03 La perspective](#h-perspective)

 - [04 La réfraction : réelle mais limitée](#h-refraction)

 - [05 Les mirages](#h-mirages)

 - [06 Fisheye et haute altitude](#h-fisheye)

 - [07 Synthèse](#h-synthese)

 - [Références](#h-refs)

 

 [← Retour à l'Observatoire](/lobservatoire/)
 

## 01 L'optique comme terrain de débat

Lorsque des observations contredisent le modèle sphérique — objets visibles trop loin (voir [Ce qu'on voit quand on ne devrait plus voir](/lobservatoire/)), horizon trop plat, courbure absente — la réponse standard fait appel à deux grands phénomènes optiques : la **réfraction atmosphérique** et les **effets de perspective**. Ces explications sont-elles suffisantes ? Sont-elles cohérentes ? Couvrent-elles réellement tous les cas documentés ?


Cet article examine en détail chacun de ces phénomènes : comment fonctionne l'horizon, ce que la perspective produit réellement, les limites physiques quantifiées de la réfraction, le comportement des mirages, et enfin la question des photographies à haute altitude — entre objectifs déformants et images sans retouche.


## 02 L'horizon reste au niveau des yeux

La prédiction la plus directement vérifiable du modèle sphérique est que l'horizon devrait **baisser** à mesure qu'on monte. Sur une sphère, un observateur qui s'élève devrait voir l'horizon de plus en plus loin en dessous de son horizontale. À 10 675 m (avion de ligne), l'horizon devrait être ~3,6° sous l'horizontale. À 39 000 m (Baumgartner), la courbure devrait être spectaculaire.


**Ce qu'on observe réellement :** Confirmé par des milliers de ballons amateurs, drones, avions de ligne et fusées non gouvernementales — **l'horizon reste toujours au niveau des yeux**, quelle que soit l'altitude. À 10 675 m en avion, l'horizon est visible par les fenêtres bâbord et tribord *simultanément*. Sur un globe, cela serait impossible : vous ne devriez voir que « l'espace » par ces fenêtres latérales, la Terre étant censée se trouver en dessous.
Le cas de **Felix Baumgartner** (Red Bull Stratos, 2012, 39 040 m) est particulièrement instructif : la caméra extérieure grand-angle montrait une courbure visible — due à la distorsion fisheye. La caméra intérieure de la capsule, avec un objectif standard, montrait un horizon **parfaitement plat, au niveau des yeux**, au même moment, à la même altitude. Deux images du même saut, deux résultats opposés — uniquement à cause de l'objectif.


 📷 EMPLACEMENT IMAGE


 Comparaison Red Bull Stratos — fisheye vs objectif standard


 Deux captures du saut de Baumgartner à 39 km : caméra extérieure (courbé) vs caméra intérieure (plat).
Même altitude, même moment, résultat opposé.


 Remplacer ce bloc par : ![\2](\1)


L'expérience de la planche de niveau, reproductible par n'importe qui, confirme ce constat : une planche lisse de 1,8 à 3,6 m montée parfaitement de niveau sur deux trépieds permet de tracer l'horizon en demi-cercle sur 16 à 32 km. Sur un globe de 40 225 km de circonférence, l'horizon devrait descendre vers les extrémités de la planche — 20 m de dépression pour 16 km. Aucun observateur n'a jamais constaté cette dépression.


## 03 La perspective : la loi optique fondamentale

La loi de perspective stipule que l'angle et la hauteur apparente auxquels un objet est perçu diminuent à mesure qu'on s'en éloigne. À une certaine distance, le champ de vision converge vers un **point de fuite** situé à l'horizon. Au-delà, l'objet devient invisible — non parce qu'il a physiquement disparu derrière une courbure, mais parce qu'il est sorti du cône de vision. C'est l'effet bien connu des rails de chemin de fer qui « se rejoignent » au loin.


**Test décisif : les objets verticaux ne penchent pas.** Sur un globe, tout objet vertical éloigné devrait sembler pencher vers l'arrière, s'écartant progressivement de la verticale de l'observateur. Une montgolfière qui s'éloigne devrait s'incliner de plus en plus. Les immeubles lointains devraient tous ressembler à des tours de Pise. Or dans la réalité, bâtiments, arbres, ballons, personnes, antennes — **tout ce qui est perpendiculaire à la surface reste parfaitement vertical**, indépendamment de la distance. Aucune inclinaison vers l'arrière n'est jamais observée, même avec des instruments optiques puissants.


**Le coucher du Soleil et la perspective.** Un Soleil local se déplaçant au-dessus d'une surface plane agirait comme un projecteur progressivement éloigné. À mesure qu'il s'éloigne, il descend vers le point de fuite (l'horizon), puis y disparaît. Ce processus est graduel — ce qui explique le crépuscule long, parfois d'une heure. Sur un globe en rotation à 1 600 km/h à l'équateur, la transition jour/nuit devrait être rapide — ce n'est pas ce qu'on observe. (Voir aussi [Observations célestes](/lobservatoire/).)


## 04 La réfraction atmosphérique : réelle mais limitée

💡 En termes simples


Quand vous plongez une paille dans un verre d'eau, elle semble « cassée » à la surface. C'est la réfraction : la lumière change de direction quand elle passe d'un milieu à un autre (ici, de l'air à l'eau). La même chose se produit dans l'atmosphère : l'air chaud et l'air froid n'ont pas la même densité, et la lumière se courbe légèrement en passant de l'un à l'autre. C'est un phénomène réel. La question n'est pas « est-ce que la réfraction existe ? » — bien sûr que oui. La question est : « est-elle assez forte pour expliquer des objets visibles à des centaines de mètres en dessous de la courbure théorique ? »


La réfraction atmosphérique est un phénomène physique **réel et bien documenté** depuis Ibn al-Haytham (*Kitāb al-Manāẓir*, XIᵉ siècle). Lorsque la lumière passe d'une couche d'air à une autre de densité différente, elle se courbe légèrement. En conditions normales, la réfraction augmente la portée visuelle de **7 à 14%**. Dans des conditions exceptionnelles (fort gradient thermique), elle peut atteindre 20 à 25% sur l'eau calme.


Mais la réfraction est-elle suffisante pour expliquer *tous* les cas de visibilité anormale ? Appliquons les chiffres maximaux aux observations documentées :


ObservationCourbure bruteAprès correction 14%Écart résiduel

Phare Port-Saïd (18 m / 93 km)665 m~500 m à 80 kmEncore 482 m inexpliqués
Île d'Elbe depuis Gênes (201 km)2 675 m~2 200 m à 173 kmEncore 2 km inexpliqués
Chicago depuis lac Michigan (97 km)732 m~570 m à 83 kmEncore 130 m inexpliqués
Notre-Dame d'Anvers (241 km)4 574 m~3 700 m à 207 kmEncore 3,5 km inexpliqués


**Le problème fondamental :** La réfraction est invoquée de manière *sélective* — uniquement quand une observation contredit le modèle globe, jamais appliquée systématiquement ni quantifiée dans le détail. Si elle permettait vraiment de voir des centaines de mètres « en dessous » de la courbure, les calculs nautiques devraient l'intégrer systématiquement. Ils ne le font pas avec les corrections massives requises ici.
Ce qui est contesté ici n'est pas la réfraction elle-même — phénomène scientifiquement valide décrit par Ibn al-Haytham il y a mille ans — mais son usage comme **explication universelle et sans limite** pour justifier des observations dont les écarts dépassent de loin ce que la physique peut produire.


 📷 EMPLACEMENT IMAGE


 Schéma de la réfraction atmosphérique


 Rayons lumineux courbés dans les couches d'air de densités différentes.
Annoter : « Correction max : 7-14% en conditions normales, 20-25% exceptionnel ».
Montrer que même à 25%, les écarts de centaines de mètres restent inexpliqués.


 Remplacer ce bloc par : ![\2](\1)


## 05 Les mirages : phénomène réel, explication limitée

Il existe deux types principaux de mirages. Le **mirage inférieur** (mirage de chaleur) se produit quand l'air très chaud près du sol crée une couche de faible densité — c'est la flaque d'eau sur la route goudronnée, image inversée et tremblante. Le **mirage supérieur** (Fata Morgana) se produit dans les régions froides quand l'air froid est surplombé par de l'air chaud — la lumière se courbe vers le bas, rendant visibles des objets normalement sous l'horizon.


Fata Morgana vs skyline de Chicago : comparaison
**Caractéristiques réelles d'un Fata Morgana :** image floue et déformée, instable et tremblante, souvent dupliquée ou empilée, parfois inversée, flotte *au-dessus* de l'horizon, requiert de fortes inversions thermiques.


**Photo Nowicki 2015 (Chicago depuis lac Michigan, 97 km) :** image nette et détaillée, stable et immobile, unique et non dupliquée, proportions normales reconnaissables, posée sur l'horizon de face, conditions météo ordinaires documentées.


Le Fata Morgana ne crée pas une image plus basse que l'horizon — il fait *flotter* des images au-dessus. Il ne peut pas résoudre le problème des 732 mètres de courbure théorique manquants.


 📷 EMPLACEMENT IMAGE


 Comparaison — vrai Fata Morgana vs photo de Chicago (Nowicki 2015)


 Gauche : Fata Morgana réel (image floue, déformée, flottante, instable).
Droite : Chicago à 97 km (image nette, stable, proportions normales, posée sur l'horizon).


 Remplacer ce bloc par : ![\2](\1)


## 06 Fisheye, haute altitude et photographies

Un objectif **fisheye** (grand-angle à 170°) possède une distorsion optique caractéristique : il courbe les lignes droites vers l'extérieur du centre de l'image. Une ligne horizontale droite filmée avec un fisheye apparaîtra courbée — convexe ou concave selon l'inclinaison de la caméra.


La majorité des caméras embarquées sur des ballons stratosphériques et fusées amateurs utilisent des GoPro ou équivalents avec champ de vision large. À 170°, la distorsion est substantielle : **une surface parfaitement plane filmée avec une GoPro montrera une courbure visible prononcée**. Et cette courbure change selon l'angle de la caméra — la même surface peut paraître convexe ou concave, sans que la réalité change.


Le constat partagé par les expériences amateurs indépendantes est constant : lorsque les images sont prises avec des **objectifs standards sans distorsion fisheye**, l'horizon apparaît parfaitement plat à 360°, même à des altitudes supérieures à 32 km. Le logiciel de correction d'objectif (lens corrector), qui supprime la distorsion, restitue systématiquement un horizon droit à partir de séquences qui semblaient montrer une courbure.


**Le test que tout le monde peut faire :** Filmez une ligne droite (un mur, un horizon marin) avec une GoPro à 170° et regardez le résultat — la ligne est courbée. Activez ensuite la correction d'objectif dans votre logiciel de montage. La ligne redevient droite. Ce simple test illustre que la courbure visible dans les images de haute altitude provient de l'optique, pas de la surface filmée.
**Témoignages de pilotes.** Des pilotes de ligne et navigateurs expérimentés déclarent qu'à toutes leurs altitudes de croisière (jusqu'à 10 675 m), l'horizon apparaît toujours plat et au niveau des yeux. Sur un globe, à cette altitude, l'horizon devrait se trouver environ 3,6° en dessous de l'horizontale — une dépression mesurable et perceptible. Les pilotes devraient abaisser le nez de leur appareil pour voir l'horizon. **Ce n'est jamais le cas.**


### La visibilité atmosphérique : ce qui limite réellement la vue

Le site spécialisé Astro-Geo-GIS, référence en géodésie et observations à longue distance, documente avec une précision remarquable les facteurs qui limitent réellement la portée visuelle. Leurs données confirment involontairement un point central de notre argument : **ce qui empêche de voir loin, ce n'est pas la courbure — c'est l'atmosphère.**


Les facteurs documentés sont le **contraste** (différence de luminosité entre l'objet et l'arrière-plan), la **diffusion de Rayleigh** (les molécules d'air diffusent la lumière bleue, créant un voile bleuté sur les objets lointains), le **forward scattering** (diffusion vers l'avant par les aérosols, maximale sous le soleil), et l'**humidité** (qui réduit la transparence de l'air). Leurs études montrent que le contraste d'un objet suit une courbe logarithmique : il diminue rapidement sur les premiers kilomètres, puis se stabilise. Un objet à peine visible à 100 km ne sera pas beaucoup moins visible à 130 km — ce qui explique pourquoi les records de visibilité sont possibles.


**Ce que cela signifie :** Même les spécialistes de la visibilité atmosphérique confirment que la limite de la vue est atmosphérique, pas géométrique. Le coefficient de contraste, l'humidité et les aérosols déterminent jusqu'où on peut voir — pas la courbure terrestre. C'est pourquoi les conditions idéales (air sec, nuit/crépuscule, altitude, contraste maximal) permettent des observations à 443 km et 493 km (voir [O2, §06](/ce-quon-voit-quand-on-ne-devrait-plus-voir/)).

### La réfraction astronomique : un modèle circulaire

Les modèles de réfraction astronomique utilisés pour corriger les positions des astres reposent sur un ensemble d'hypothèses rarement questionnées. L'analyse détaillée des équations fondamentales (SpaceAudits, « On Astronomical Refraction ») révèle que **le rayon terrestre est la condition aux limites principale** de ces modèles — pas une sortie, mais une entrée.


Les hypothèses du modèle standard de réfraction astronomique sont les suivantes : l'atmosphère est composée de **sphères concentriques stratifiées** homogènes, chaque couche ayant un indice de réfraction uniforme décroissant avec l'altitude. La gravité est supposée radiale et constante. L'atmosphère est un gaz parfait en équilibre hydrostatique. Les variations locales — inversions de température, conduits thermiques, turbulences — sont **lissées** par la symétrie du modèle.


La chaîne de circularité
**Équation 1** — Hauteur d'échelle de l'atmosphère : calculée avec la loi des gaz parfaits + équilibre hydrostatique + gravité constante.


**Équation 2** — Potentiel gravitationnel : défini par la gravité newtonienne pour une masse sphérique. **Hypothèse : la Terre est sphérique, la gravité est radiale, R est connu et fixe.**


**Équation 3** — Potentiel normalisé : adimensionne l'Eq. 2 pour faciliter les développements en série.


**Équation 4** — Coordonnée radiale adimensionnée : ne fonctionne que si l'atmosphère est lisse et monotone (pas de pliage, pas de conduit). Exclut par construction l'effet Novaya Zemlya (voir [O3](/la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre/)).


L'auteur de SpaceAudits note que ces modèles, construits pour normaliser les données sur la sphéricité, ne peuvent par construction rien produire qui contredise la sphéricité. Les coefficients de réfraction ne sont pas mesurés indépendamment — ils sont **ajustés pour que les observations correspondent au modèle sphérique**. Le même auteur relève que les densités d'air utilisées dans ces modèles n'ont jamais été mesurées in situ à haute altitude — elles sont extrapolées à partir du modèle d'atmosphère standard.


**En résumé :** Le modèle de réfraction astronomique suppose une Terre sphérique pour calculer comment la lumière se courbe dans l'atmosphère. Il utilise ensuite cette courbure calculée pour « corriger » les positions des astres. Les positions corrigées confirment le modèle sphérique. C'est un circuit fermé : la sphéricité entre comme hypothèse et sort comme conclusion. Les phénomènes réels d'atmosphère (Novaya Zemlya, conduits thermiques, inversions) sont exclus par la symétrie du modèle.

## 07 Synthèse : ce que l'optique enseigne réellement


PhénomènePrédit sur globePrédit sur planObservé

Horizon au niveau des yeuxDescend avec l'altitudeReste au niveau**Reste au niveau**
Horizon à 360°Courbure convexe visibleParfaitement plat**Plat (obj. standard)**
Objets verticaux lointainsPenchent en arrièreRestent verticaux**Restent verticaux**
Réfraction 7–14%Correction ~10%N/AInsuffisante pour grands écarts
Courbure photos fisheyeConfirme globeDistorsion artificielle**Disparaît avec correction**
Courbure photos obj. standardVisible à >30 kmHorizon plat**Horizon plat (ballons amateurs)**


Trois grands résultats se dégagent. **Premièrement,** l'horizon se comporte en tout point comme une limite de perspective sur surface plane — il reste au niveau des yeux quelle que soit l'altitude. **Deuxièmement,** la réfraction atmosphérique est un phénomène réel mais quantifié (7–14%), insuffisant pour expliquer les écarts de plusieurs centaines à plusieurs milliers de mètres documentés. **Troisièmement,** la courbure visible dans les photos de haute altitude est entièrement produite par la distorsion des objectifs grand-angle — elle disparaît systématiquement avec un objectif standard ou une correction de distorsion.


## Références


 - Ibn al-Haytham (965–1040). *Kitāb al-Manāẓir* (Livre d'Optique).

 - Rowbotham, S.B. (1865). *Zetetic Astronomy: Earth Not a Globe* — expérience de la planche de niveau.

 - Red Bull Stratos (2012) — caméra intérieure vs extérieure à 39 040 m.

 - Nowicki, Joshua (2015). Photographie de Chicago depuis le lac Michigan.

 - Dubay, Eric. *200 Preuves que la Terre n'est pas une Boule qui Tourne*.

 - Témoignages documentés de pilotes de ligne et navigateurs — horizon à hauteur des yeux.

 - Archives d'expériences amateurs en ballons stratosphériques — objectifs standards vs fisheye.


					

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