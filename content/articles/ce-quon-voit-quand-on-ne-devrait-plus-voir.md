---
title: "Ce qu'on voit quand on ne devrait plus voir"
description: ".nx-nav{width:100%;background:#F7F2E8;border-bottom:1px solid #DDD5C5;padding:0 2rem;position:sticky;top:0;z-index:999} .nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;ju..."
date: "2026-04-15"
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
.o2{background:var(--bg);color:var(--t1);padding:0}
.o2-h{padding:5rem 2rem 3.5rem;text-align:center;position:relative;overflow:hidden}
.o2-h::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 50% at 50% 30%,rgba(30,58,138,.05),transparent 70%);pointer-events:none}
.o2-tag{display:inline-block;font-family:var(--f2);font-size:.62rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--cobalt-l);background:var(--cobalt-g);border:1px solid rgba(30,58,138,.25);padding:.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.o2-title{font-family:var(--f1);font-size:clamp(1.8rem,4.5vw,2.6rem);font-weight:700;color:var(--cobalt-l);line-height:1.15;margin:0 0 1rem;max-width:800px;margin-left:auto;margin-right:auto}
.o2-sub{font-family:var(--f3);font-size:1.02rem;line-height:1.7;color:var(--t2);max-width:650px;margin:0 auto 2rem}
.o2-meta{max-width:800px;margin:0 auto;padding:1.2em 0;border-top:1px solid var(--bdr);border-bottom:1px solid var(--bdr);display:flex;flex-wrap:wrap;gap:.5em 2em;font-family:var(--f2);font-size:.75rem;color:var(--t3)}
.o2-meta dt{font-weight:600;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem}
.o2-meta dd{margin:0 0 .6em;color:var(--t2)}
.o2-lay{display:flex;gap:2.5rem;max-width:1200px;margin:0 auto;padding:2.5rem 2rem 5rem;align-items:flex-start}
.o2-nav{flex:0 0 255px;position:sticky;top:80px;max-height:calc(100vh - 100px);overflow-y:auto;padding:1.5rem;background:var(--bg2);border:1px solid var(--bdr);border-radius:10px}
.o2-nav::-webkit-scrollbar{width:3px}.o2-nav::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}
.o2-nav__t{font-family:var(--f2);font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--cobalt-l);margin:0 0 1rem;padding-bottom:.6rem;border-bottom:1px solid var(--bdr)}
.o2-nav ul{list-style:none;padding:0;margin:0}.o2-nav li{margin-bottom:.35rem}
.o2-nav a{display:block;font-family:var(--f2);font-size:.76rem;color:var(--t3);text-decoration:none;padding:.4em .8em;border-radius:5px;border-left:2px solid transparent;transition:all .25s ease;line-height:1.35}
.o2-nav a:hover{color:var(--t1);background:rgba(30,58,138,.06);border-left-color:var(--cobalt-l)}
.o2-nav a.active{color:var(--cobalt-l);background:var(--cobalt-g);border-left-color:var(--cobalt-l);font-weight:500}
.o2-nav .num{font-size:.6rem;font-weight:600;color:var(--cobalt-l);margin-right:.4em;opacity:.7}
.o2-nav__bk{display:block;margin-top:1.2rem;padding:.6em 1em;background:var(--cobalt-l);color:#fff;font-family:var(--f2);font-size:.72rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;text-align:center;border-radius:5px;transition:background .3s ease}
.o2-nav__bk:hover{background:#3B5FC8}
.o2-b{flex:1;min-width:0;max-width:800px;font-family:var(--f3);font-size:clamp(1rem,1.8vw,1.08rem);line-height:1.75;color:var(--t1)}
.o2-b p{margin-bottom:1.4em;text-align:justify;hyphens:auto}
.o2-b a{color:var(--cobalt-l);text-decoration:underline;text-underline-offset:3px}
.o2-b h2{font-family:var(--f1);font-size:clamp(1.4rem,3vw,1.85rem);font-weight:700;color:var(--t1);margin:3em 0 .8em;padding-bottom:.4em;border-bottom:1px solid var(--bdr);line-height:1.25;scroll-margin-top:90px}
.o2-b h3{font-family:var(--f2);font-size:clamp(1rem,1.8vw,1.15rem);font-weight:600;color:var(--cobalt-l);text-transform:uppercase;letter-spacing:.06em;margin:2em 0 .6em;line-height:1.35;scroll-margin-top:90px}
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
.o2-refs{margin-top:3em;padding-top:2em;border-top:1px solid var(--bdr)}
.o2-refs h2{border-bottom:none;padding-bottom:0;font-size:1.3rem}
.o2-refs ol{padding-left:1.5em;font-family:var(--f2);font-size:.82rem;color:var(--t2);line-height:1.7}
.o2-refs li{margin-bottom:.6em}
@media(max-width:900px){.o2-lay{flex-direction:column;padding:1.5rem}.o2-nav{position:static;flex:none;width:100%;max-height:none;margin-bottom:2rem}.o2-h{padding:3.5rem 1.5rem 2.5rem}}


 L'Observatoire — OBS-2026-002
 
# Ce qu'on voit quand on ne devrait plus voir

 Phares, bateaux, îles, montagnes, skylines — des dizaines d'observations documentées où la visibilité dépasse largement ce que la courbure devrait permettre.
 
 AuteurTerre Étendue Islam
 DateAvril 2026 — v1.0
 Lecture~25 min
 DomaineObservations empiriques · Visibilité
 

 
 
## Sommaire

 
 [01 Le test direct](#v-intro)

 - [02 Bateaux et zoom](#v-bateaux)

 - [03 Les phares impossibles](#v-phares)

 - [04 Îles et montagnes](#v-iles)

 - [05 Skylines urbaines](#v-skylines)

 - [06 Tableau de synthèse](#v-synthese)

 - [07 Questions fréquentes](#v-faq)

 - [Références](#v-refs)

 

 [← Retour à l'Observatoire](/lobservatoire/)
 

## 01 La visibilité comme test direct de la courbure

Si la Terre est une sphère, toute observation à grande distance doit butter contre la courbure. Un objet suffisamment éloigné devrait disparaître progressivement par le bas — sa base cachée derrière l'arrondi du globe. Ce principe est calculable avec la formule de courbure (voir [L'eau ne ment pas](/lobservatoire/), section 00, pour le tableau de référence).


Et il est vérifiable directement, sur le terrain, avec des instruments accessibles à tous : un télescope, une longue-vue, un appareil photo avec téléobjectif. Cet article recense des dizaines d'observations documentées — de sources indépendantes, de siècles différents, de continents différents — où la visibilité réelle dépasse très largement ce que la courbure théorique devrait permettre.


## 02 Bateaux à l'horizon : le zoom qui change tout

L'argument le plus classiquement avancé pour prouver la rotondité est la disparition progressive des navires : la coque disparaît en premier, suivie du pont, puis des mâts — comme si le bateau « descendait derrière » la courbure. Mais sur une surface parfaitement plate, la loi de perspective produit **exactement le même effet** : les parties basses convergent vers la ligne d'horizon avant les parties hautes.


**La différence décisive :** Sur un globe, si la coque a réellement passé derrière la courbure, aucun zoom ne peut la rappeler — elle est physiquement cachée, comme derrière une colline. Sur une surface plane, un zoom suffisamment puissant la ramène immédiatement. Ce test est reproductible et documenté : des navires dont la coque a « disparu sous l'horizon » à l'œil nu réapparaissent entièrement au téléobjectif, y compris leur ligne de flottaison.
Rowbotham a mené une série d'expériences sur plusieurs décennies. À Brighton (64 km de ligne droite), un vaisseau observé pendant plusieurs heures reste visible sous une ligne tendue entre deux poteaux — alors qu'il devrait être à 81 m sous l'horizon. À Liverpool (51 km), un paquebot pour Dublin reste visible au ras de l'horizon au télescope — alors que 146 m de courbure devraient le cacher entièrement. En 1895, le *Chambers' Journal* rapporte un navire vu à 321 km depuis l'île Maurice, confirmé par un témoin indépendant à Aden — à cette distance, il devrait être à 8 km sous l'horizon.


## 03 Les phares impossibles

Les phares sont des cas de test idéaux : hauteur connue, altitude précise, distance de visibilité documentée dans les registres nautiques.


PhareHauteurVisible àCourbure cachéeDevrait être sous l'horizon de

Dunkerque (France)59 m45 km158 m99 m
Cordouan (France)63 m50 km195 m132 m
Cap Bonavista (Terre-Neuve)46 m56 km249 m203 m
St-Botolph Boston (USA)88 m64 km325 m237 m
Île de Wight (Angleterre)55 m68 km359 m304 m
Cap Agulhas (Afrique du Sud)73 m80 km508 m435 m
Statue de la Liberté (New York)99 m97 km731 m632 m
**Port-Saïd (Égypte)****18 m****93 km****684 m****666 m**
**Notre-Dame d'Anvers****123 m****241 km****4 574 m****4 451 m**


Le cas de Port-Saïd est le plus spectaculaire : un phare de seulement 18 mètres, visible à 93 km. La courbure à cette distance cache **684 mètres** — soit 37 fois la hauteur du phare. Même avec une correction de réfraction maximale (14%), il resterait 35 fois la hauteur du phare inexpliqué.


 📷 EMPLACEMENT IMAGE


 Photo du phare de Port-Saïd (Égypte)


 Phare de 18 m de haut. Annoter : « visible à 93 km — courbure attendue : 684 m (37× sa hauteur) ».
Alternative : schéma montrant le phare minuscule vs la courbure colossale qu'il devrait franchir.


 Remplacer ce bloc par : ![\2](\1)


La flèche de Notre-Dame d'Anvers (123 m) est visible à 241 km depuis le large selon de nombreux capitaines. Elle devrait être à plus d'un kilomètre et demi sous l'horizon.


## 04 Îles et montagnes : des centaines de mètres ignorés


### Gênes : quatre îles visibles à l'impossible


ÎleDistance depuis Gênes (21 m alt.)Courbure cachée

Gorgone130 km1 016 m
Capraia164 km1 710 m
Corse160 km1 600 m
**Île d'Elbe****201 km****2 675 m**


Depuis Gênes, à seulement 21 m d'altitude, l'île d'Elbe est visible à 201 km par temps clair — la courbure devrait cacher **2 675 mètres**, soit plus d'une montagne de moyenne taille.


### Alaska : le Mont McKinley visible en entier à 209 km

Depuis Anchorage (31 m d'altitude), le Denali (Mont McKinley, 6 197 m) est visible à 209 km, de la base au sommet. La courbure à cette distance cache 2 812 mètres — presque la moitié de la montagne devrait être dissimulée. Elle est pourtant visible en totalité, parfaitement droite, sans aucun signe d'occultation basale.


 📷 EMPLACEMENT IMAGE


 Photo du Mont Denali (6 197 m) vu depuis Anchorage à 209 km


 Montagne visible de la base au sommet. Annoter la courbure attendue (2 812 m cachés = presque la moitié).


 Remplacer ce bloc par : ![\2](\1)


### Île Sainte-Hélène (1872)

Le Capitaine Gibson, à bord du *Thomas Wood*, rapporte avoir vu la totalité de l'île à 120 km. L'île aurait dû se trouver à plus de 1 000 mètres sous le champ de vision.


## 05 Skylines urbaines : les villes qu'on ne devrait pas voir

**Chicago depuis le Lac Michigan (97 km).** En 2015, le photographe Joshua Nowicki photographie la skyline de Chicago depuis la rive est du lac, à 97 km. Plusieurs chaînes d'information tentent d'expliquer le phénomène comme un « mirage supérieur ». Deux problèmes : les mirages produisent des images floues, déformées et instables — la photo est nette et stable. Et surtout, la skyline devrait être à **732 mètres sous l'horizon** — aucune réfraction réaliste ne compense un tel écart.


 📷 EMPLACEMENT IMAGE


 Photo de Joshua Nowicki — skyline de Chicago vue à 97 km depuis le Michigan


 Photo nette, stable, immeubles identifiables. Annoter : « 97 km — 732 m de courbure attendue ».
Comparer avec un vrai Fata Morgana (image floue, déformée) si possible.


 Remplacer ce bloc par : ![\2](\1)


**New York + Philadelphie simultanément depuis Washington's Rock (193 km total).** Depuis Washington's Rock (New Jersey, 122 m d'altitude), par journée claire, les deux skylines sont visibles simultanément dans des directions opposées — 193 km d'un bout à l'autre. Chacune devrait être cachée derrière plus de 244 m de courbure.


**Tour de Grimsby depuis Hull (113 km, 1854).** Le *Times* du 16 octobre 1854 rapporte que la tour du quai de Great Grimsby (91,5 m) est vue distinctement depuis Hull à 113 km. Elle devrait être à 793 m sous l'horizon.


## 06 Les records mondiaux : 443 km et 493 km photographiés

Les cas présentés ci-dessus datent du XIXᵉ et du début du XXIᵉ siècle. Mais les progrès de la photographie numérique et du téléobjectif ont permis de repousser les limites de la visibilité documentée à des distances qui défient toute tentative d'explication par la réfraction.


### Le record de 2016 : Pyrénées → Alpes (443 km)

Le 16 juillet 2016, l'équipe Beyond Horizons (Marc Bret et al.) photographie le **Pic Gaspard et la Barre des Écrins** (Alpes françaises, 4 102 m) depuis le **Pic de Finestrelles** (Pyrénées catalanes, 2 174 m) — une distance de **443 km**. La photo, prise avant le lever du soleil pour maximiser le contraste, montre une fine ligne de montagnes alpines se découpant au-dessus de l'horizon. Cette observation a été certifiée par le Guinness World Records comme la plus longue ligne de vue photographiée sur Terre.


**Calcul de courbure à 443 km :** La formule h = d²/2R donne une courbure théorique de **15 420 mètres** (15,4 km). Même en soustrayant les altitudes des deux sommets (2 174 m + 4 102 m = 6 276 m), il reste **9 144 mètres** de courbure non compensée — soit l'équivalent de 3 Tour Eiffel empilées. Aucune réfraction réaliste ne peut compenser un tel écart.

### Le record actuel (décembre 2024) : Turquie → Géorgie (493 km)

Le 15 décembre 2024, le photographe slovaque **Richard Jezik** bat le record depuis un sous-sommet près de Karagöl (Giresun, Turquie) en photographiant le mont **Shkhara** (frontière Géorgie-Russie, 5 193 m) à une distance de **493,07 km**. Ce nouveau record Guinness a été réalisé dans des conditions extrêmes : -12°C, vents de 20-25 m/s, après 10 heures d'ascension de nuit à pied dans la neige (le sommet n'étant pas accessible en voiture). La photo a été prise avant le lever du soleil.


**Calcul de courbure à 493 km :** h = d²/2R = **19 100 mètres** (19,1 km). Altitude combinée des deux points : ~3 000 m (observateur) + 5 193 m (Shkhara) = ~8 193 m. **Il reste ~10 900 mètres de courbure inexpliquée** — presque 11 kilomètres. Même en appliquant une réfraction atmosphérique exceptionnelle de 25%, il resterait encore ~8 000 mètres inexpliqués.

Ces records ne sont pas des observations isolées ou des témoignages douteux — ce sont des **photographies géolocalisées, horodatées, certifiées par le Guinness World Records**, prises avec du matériel identifié, dans des conditions météorologiques documentées. Le site Astro-Geo-GIS (spécialiste en géodésie et observations à longue distance) confirme que la visibilité dépend principalement du contraste atmosphérique, de la diffusion de Rayleigh et de l'humidité — mais jamais que la courbure soit le facteur limitant. Au contraire, leurs propres données montrent que des objets sont régulièrement photographiés à 130, 150, 160 km et au-delà, exactement comme le prédit un modèle de surface plane.


## 07 Tableau de synthèse général


TypeObservationDistanceCourbure cachéeRésultat

🏆**Karagöl → Shkhara (Record 2024)****493 km****19 100 m****Photo certifiée Guinness**
🏆**Finestrelles → Alpes (Record 2016)****443 km****15 420 m****Photo certifiée Guinness**
🚢Navire (Île Maurice, 1895)321 km~8 000 mNavire vu et décrit avec précision
🔦Notre-Dame d'Anvers (123 m)241 km4 574 mFlèche visible par capitaines
🏔️Denali depuis Anchorage209 km2 812 mMontagne visible base→sommet
🏝️Île d'Elbe depuis Gênes201 km2 675 mÎle visible à l'œil nu
🏙️NYC + Philly (Washington's Rock)193 km244 m × 2Deux skylines visibles ensemble
🔦Tour de Grimsby depuis Hull113 km793 mTour visible (1854, The Times)
🏙️Chicago depuis lac Michigan97 km732 mSkyline nette et photographiée
🔦Port-Saïd (18 m)93 km684 mPhare visible (37× sa hauteur)
🌊Côte galloise depuis Île de Man80 km127 mLigne parfaitement horizontale
🚢Paquebot Dublin (Liverpool)51 km146 mMât visible au ras de l'horizon


Dans la **totalité** des cas — des 51 km du paquebot dublinois aux **493 km du record Guinness mondial** — la visibilité réelle dépasse ce que la courbure théorique devrait permettre. Les écarts vont de quelques dizaines de mètres à **près de 11 kilomètres**.


## 07 Questions fréquentes

La réfraction n'explique-t-elle pas tout ?
La réfraction atmosphérique augmente la portée visuelle de 7 à 14% dans des conditions normales. Pour le phare de Port-Saïd (18 m visible à 93 km), même avec 14% de correction, il resterait ~580 m de courbure inexpliquée — soit 32 fois la hauteur du phare. La réfraction ne peut pas compenser des écarts de cette magnitude.


Chicago n'était-elle pas un mirage ?
Les mirages supérieurs (Fata Morgana) produisent des images floues, déformées et instables. La photo de Nowicki montre une skyline nette, stable, de face, avec tous les immeubles identifiables. De plus, un mirage ne peut pas faire apparaître un objet qui devrait se trouver à 732 m *sous* l'horizon — il ne fait que déplacer l'image vers le haut de quelques degrés.


Pourquoi ne voit-on pas à l'infini sur une Terre plane ?
Sur une surface plane, l'horizon est une limite optique due à la perspective et aux conditions atmosphériques (brume, diffusion). Plus l'atmosphère est transparente et l'instrument puissant, plus on voit loin — c'est exactement ce que confirment toutes les observations documentées ici. Le zoom ramène les objets « disparus », ce qui est impossible si c'est une courbure physique qui les cache.


## Références


 - Rowbotham, S.B. (1865). *Zetetic Astronomy: Earth Not a Globe*.

 - Carpenter, W. (1885). *100 Proofs that the Earth is Not a Globe*.

 - *Chambers' Journal*, février 1895 — observation du navire à 321 km (île Maurice).

 - *The Times*, 16 octobre 1854 — tour de Grimsby visible depuis Hull.

 - Nowicki, Joshua (2015). Photographie de la skyline de Chicago depuis le lac Michigan.

 - Capitaine Gibson, navire *Thomas Wood* (1872) — île Sainte-Hélène à 120 km.

 - Registres nautiques des phares — données de visibilité documentées.

 - Guinness World Records (2024). « Longest line of sight on earth photographed » — 493,07 km, Richard Jezik, Giresun (Turquie) → Shkhara (Géorgie/Russie), 15 décembre 2024.

 - Beyond Horizons / Marc Bret (2016). Pic de Finestrelles → Pic Gaspard/Barre des Écrins — 443 km. Précédent record Guinness.

 - Astro-Geo-GIS — « Horizontal visibility as a main factor of long-distance observation ». Données sur le contraste, la diffusion de Rayleigh et la visibilité atmosphérique.


					

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