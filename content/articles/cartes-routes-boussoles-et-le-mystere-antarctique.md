---
title: "Cartes, routes, boussoles et le mystère antarctique"
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
.o5{background:var(--bg);color:var(--t1);padding:0}
.o5-h{padding:5rem 2rem 3.5rem;text-align:center;position:relative;overflow:hidden}
.o5-h::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 50% at 50% 30%,rgba(30,58,138,.05),transparent 70%);pointer-events:none}
.o5-tag{display:inline-block;font-family:var(--f2);font-size:.62rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--cobalt-l);background:var(--cobalt-g);border:1px solid rgba(30,58,138,.25);padding:.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.o5-title{font-family:var(--f1);font-size:clamp(1.8rem,4.5vw,2.6rem);font-weight:700;color:var(--cobalt-l);line-height:1.15;margin:0 0 1rem;max-width:800px;margin-left:auto;margin-right:auto}
.o5-sub{font-family:var(--f3);font-size:1.02rem;line-height:1.7;color:var(--t2);max-width:650px;margin:0 auto 2rem}
.o5-meta{max-width:800px;margin:0 auto;padding:1.2em 0;border-top:1px solid var(--bdr);border-bottom:1px solid var(--bdr);display:flex;flex-wrap:wrap;gap:.5em 2em;font-family:var(--f2);font-size:.75rem;color:var(--t3)}
.o5-meta dt{font-weight:600;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem}
.o5-meta dd{margin:0 0 .6em;color:var(--t2)}
.o5-lay{display:flex;gap:2.5rem;max-width:1200px;margin:0 auto;padding:2.5rem 2rem 5rem;align-items:flex-start}
.o5-nav{flex:0 0 255px;position:sticky;top:80px;max-height:calc(100vh - 100px);overflow-y:auto;padding:1.5rem;background:var(--bg2);border:1px solid var(--bdr);border-radius:10px}
.o5-nav::-webkit-scrollbar{width:3px}.o5-nav::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}
.o5-nav__t{font-family:var(--f2);font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--cobalt-l);margin:0 0 1rem;padding-bottom:.6rem;border-bottom:1px solid var(--bdr)}
.o5-nav ul{list-style:none;padding:0;margin:0}.o5-nav li{margin-bottom:.35rem}
.o5-nav a{display:block;font-family:var(--f2);font-size:.76rem;color:var(--t3);text-decoration:none;padding:.4em .8em;border-radius:5px;border-left:2px solid transparent;transition:all .25s ease;line-height:1.35}
.o5-nav a:hover{color:var(--t1);background:rgba(30,58,138,.06);border-left-color:var(--cobalt-l)}
.o5-nav a.active{color:var(--cobalt-l);background:var(--cobalt-g);border-left-color:var(--cobalt-l);font-weight:500}
.o5-nav .num{font-size:.6rem;font-weight:600;color:var(--cobalt-l);margin-right:.4em;opacity:.7}
.o5-nav .sub{padding:0 0 0 1.2em;margin:.15rem 0 .2rem}.o5-nav .sub a{font-size:.7rem;padding:.3em .8em}
.o5-nav__bk{display:block;margin-top:1.2rem;padding:.6em 1em;background:#2D8B57;color:#2C1810;font-family:var(--f2);font-size:.72rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;text-align:center;border-radius:5px;transition:background .3s ease}
.o5-nav__bk:hover{background:#3DA06A}
.o5-b{flex:1;min-width:0;max-width:800px;font-family:var(--f3);font-size:clamp(1rem,1.8vw,1.08rem);line-height:1.75;color:var(--t1)}
.o5-b p{margin-bottom:1.4em;text-align:justify;hyphens:auto}
.o5-b a{color:var(--cobalt-l);text-decoration:underline;text-underline-offset:3px}
.o5-b h2{font-family:var(--f1);font-size:clamp(1.4rem,3vw,1.85rem);font-weight:700;color:var(--t1);margin:3em 0 .8em;padding-bottom:.4em;border-bottom:1px solid var(--bdr);line-height:1.25;scroll-margin-top:90px}
.o5-b h3{font-family:var(--f2);font-size:clamp(1rem,1.8vw,1.15rem);font-weight:600;color:var(--cobalt-l);text-transform:uppercase;letter-spacing:.06em;margin:2em 0 .6em;line-height:1.35;scroll-margin-top:90px}
.sn{font-family:var(--f2);font-size:.65rem;font-weight:600;color:var(--cobalt-l);background:var(--cobalt-g);border:1px solid rgba(30,58,138,.25);padding:.2em .6em;border-radius:3px;margin-right:.6em;vertical-align:middle}
.bq{margin:2em 0;padding:1.5em 2em;background:linear-gradient(135deg,var(--cobalt-g),transparent 70%);border-left:3px solid var(--cobalt);border-radius:0 8px 8px 0;font-family:var(--f3);font-style:italic;font-size:1.02em;line-height:1.75;color:var(--t1)}
.bq cite{display:block;margin-top:.8em;font-size:.78em;font-style:normal;font-family:var(--f2);color:var(--t3)}
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
.o5-refs{margin-top:3em;padding-top:2em;border-top:1px solid var(--bdr)}
.o5-refs h2{border-bottom:none;padding-bottom:0;font-size:1.3rem}
.o5-refs ol{padding-left:1.5em;font-family:var(--f2);font-size:.82rem;color:var(--t2);line-height:1.7}
.o5-refs li{margin-bottom:.6em}
@media(max-width:900px){.o5-lay{flex-direction:column;padding:1.5rem}.o5-nav{position:static;flex:none;width:100%;max-height:none;margin-bottom:2rem}.o5-h{padding:3.5rem 1.5rem 2.5rem}}


 L'Observatoire — OBS-2026-005
 
# Cartes, routes, boussoles et le mystère antarctique

 Les cartes ne sont jamais neutres. Les routes aériennes non plus. Et l'Antarctique reste le continent le plus verrouillé, le plus surveillé, le plus inaccessible de la planète.
 
 AuteurTerre Étendue Islam
 DateAvril 2026 — v1.0
 Lecture~40 min
 DomaineGéographie · Navigation · Antarctique
 

 
 
## Sommaire

 
 [01 Les cartes anciennes](#m-cartes)

 - [02 Projections et distorsions](#m-projections)

 - [03 La carte de l'ONU](#m-onu)

 - [04 Routes aériennes anormales](#m-routes)

 - [05 La boussole et le Nord unique](#m-boussole)

 - [06 GPS et LORAN](#m-gps)

 - [07 L'énigme antarctique](#m-antarctique)
 
 [Cook (1774)](#m-cook)

 - [Le Traité de 1959](#m-traite)

 - [Les déclarations de Byrd](#m-byrd)

 

 
 - [08 Fuseaux horaires](#m-synthese)

 - [09 Synthèse](#m-bilan)

 - [Références](#m-refs)

 

 [← Retour à l'Observatoire](/lobservatoire/)
 

## 01 Les cartes anciennes : ce qu'elles révèlent

Les cartes ne sont jamais neutres. Chaque carte est une représentation d'une réalité sur une surface plane, impliquant des choix : quel centre ? Quelle projection ? Quelles distorsions accepter ? Ces choix révèlent souvent plus que ce qu'on croit sur la vision du monde de ceux qui les ont conçues.


Le monde islamique médiéval a produit des cartographes de premier rang : **Al-Idrisi** (1100–1165), **Ibn Hawqal** (Xᵉ siècle), **Al-Biruni** (973–1048). Une caractéristique frappante de leurs cartes : elles sont orientées avec le **Sud en haut**. Certaines sont centrées sur La Mecque, d'autres sur le monde islamique connu. Leurs routes commerciales et de pèlerinage sont d'une précision remarquable.


La *Tabula Rogeriana* d'Al-Idrisi (1154), réalisée pour le roi Roger II de Sicile, est considérée comme la carte la plus précise du monde médiéval. Orientée Sud en haut, elle représente l'ensemble de l'Eurasie et de l'Afrique connue avec une précision étonnante. Retournée à 180°, elle ressemble presque parfaitement aux cartes modernes.


 📷 EMPLACEMENT IMAGE


 Tabula Rogeriana d'Al-Idrisi (1154)


 Carte originale orientée Sud en haut. Montrer les routes commerciales et la précision.
Alternative : version retournée (Nord en haut) pour comparaison avec les cartes modernes.


 Remplacer ce bloc par : ![\2](\1)


CarteÉpoqueOrientationParticularité

Tabula Rogeriana (Al-Idrisi)1154Sud en hautPlus précise du Moyen Âge
Mappa Mundi (Hereford)1300Est en hautJérusalem au centre
Carte de Fra Mauro1450Sud en hautAfrique très précise
Carte de Piri Reis1513VariableCôte australe pré-découverte ?
Carte d'Urbano Monte1587Nord en hautAntarctique comme ceinture verdoyante


L'orientation « Nord en haut » n'est pas une vérité naturelle mais une **convention européenne récente**, imposée à partir du XVIᵉ siècle avec la domination coloniale et commerciale de l'Europe. Les savants islamiques, qui ont cartographié le monde avec plus de précision que leurs contemporains européens, utilisaient l'orientation Sud en haut sans que cela ne nuise à leur exactitude géographique.


## 02 Projections cartographiques : Mercator vs azimutale

Toute carte est une projection. Si la Terre est sphérique, la projeter sur une surface plane implique nécessairement des distorsions. Selon la projection choisie, les formes, les surfaces ou les distances sont déformées différemment. Ces choix ne sont jamais innocents.


La **projection de Mercator** (Gerardus Mercator, 1569) est une projection cylindrique conforme destinée à l'origine aux navigateurs. Son avantage : les lignes de cap sont des lignes droites, ce qui facilite la navigation maritime. Ses inconvénients sont massifs : les surfaces sont profondément distordues aux hautes latitudes.


**Distorsions de Mercator :** Le Groenland apparaît aussi grand que l'Afrique — il est en réalité **14 fois plus petit** (2,16 M km² contre 30,3 M km²). L'Afrique peut contenir simultanément les États-Unis, la Chine, l'Inde, l'Europe et le Japon. L'Antarctique est étiré à l'infini vers le bas. Les pôles ne peuvent même pas être représentés.
💡 En termes simples


Impossible de représenter parfaitement une sphère sur une feuille plate — il faut toujours déformer quelque chose. C'est pourquoi il existe des dizaines de « projections » cartographiques différentes. La plus connue, Mercator, déforme les surfaces : le Groenland semble aussi grand que l'Afrique, alors qu'il est 14 fois plus petit en réalité. La projection azimutale équidistante, elle, fonctionne comme une cible de tir : un point central, et des cercles concentriques autour. Toutes les distances mesurées depuis le centre sont exactes. C'est celle qu'utilisent les Nations Unies sur leur emblème officiel — et c'est aussi, visuellement, celle qui ressemble le plus à une Terre plane vue du dessus.


La **projection azimutale équidistante** représente un point central (un pôle, une ville) entouré de cercles concentriques. Toutes les distances depuis le point central sont exactes, et toutes les directions depuis le centre sont exactes. C'est la projection idéale pour représenter le monde « vu du dessus ».


 📷 EMPLACEMENT IMAGE


 Projection Mercator vs projection azimutale équidistante — côte à côte


 Gauche : Mercator (cylindrique, Groenland démesuré, Antarctique étiré, pôles impossibles).
Droite : Azimutale équidistante centrée sur le Pôle Nord (cercles concentriques, distances exactes depuis le centre).
Montrer que la carte ONU utilise l'azimutale.


 Remplacer ce bloc par : ![\2](\1)


La projection Mercator a été utilisée pendant des siècles comme carte mondiale standard dans l'enseignement — pendant toute la période coloniale. Elle sur-représente l'Europe et l'Amérique du Nord, sous-représente l'Afrique, l'Amérique du Sud et l'Asie du Sud. Ces distorsions ne sont pas anodines : elles induisent une vision du monde où les puissances coloniales apparaissent plus grandes et plus importantes.


## 03 La carte de l'ONU : une projection révélatrice

L'emblème officiel des Nations Unies, adopté en 1946, représente le monde sur une **projection azimutale équidistante centrée sur le Pôle Nord**, entourée de branches d'olivier. C'est le symbole de l'organisation la plus internationale du monde, présent sur toutes ses publications et ses bâtiments.


Tous les continents y sont disposés en cercle autour du Pôle Nord central : l'Eurasie à droite, l'Amérique à gauche, l'Afrique en bas à droite, l'Australie en bas. La carte s'arrête à environ 60° de latitude Sud — **l'Antarctique n'est pas représenté**, ou constitue la bordure extérieure du disque.


Deux lectures d'un même symbole
**Lecture officielle :** Choix pragmatique de neutralité géographique. La projection azimutale centrée sur le Pôle Nord est la meilleure façon de représenter le monde à égale distance de tous, sans avantager aucun pays. Elle était couramment utilisée dans la navigation aérienne arctique dans les années 1940.


**Lecture alternative :** Cette carte ressemble exactement à ce que serait une Terre étendue et plane vue du dessus — avec le Pôle Nord au centre, les continents disposés en cercle, et l'Antarctique absent ou formant la périphérie extérieure. Pourquoi l'organisation mondiale la plus officielle a-t-elle choisi, sur son symbole le plus visible, une projection qui ressemble à une carte de Terre plane plutôt qu'une image de globe ?


## 04 Routes aériennes de l'hémisphère Sud : des détours systématiques

L'hémisphère Sud pose des questions cartographiques sérieuses. Plusieurs routes aériennes qui devraient, sur un globe sphérique, emprunter un trajet direct dans l'hémisphère Sud, font au contraire des **détours spectaculaires par l'hémisphère Nord**.


TrajetDistance théoriqueEscale réelleLogique sur azimutale

Sydney → Santiago~11 300 kmLos Angeles (+70%)Oui — ligne plus directe
Johannesburg → Perth~9 000 kmDubaï / Hong KongOui
Johannesburg → São Paulo~7 500 kmLondres (50° N)Oui
Santiago → Johannesburg~7 700 kmSénégal (Dakar)Oui — mi-chemin exact
Cape Town → Buenos Aires~6 800 kmLondres / DubaïOui


Entre Sydney (34°S) et Santiago (33°S), le grand cercle devrait passer directement par le Pacifique Sud. Distance théorique : 11 300 km. En réalité, les vols rejoignent l'hémisphère Nord via Los Angeles pour une distance totale de plus de 19 000 km — **70% de plus**.


**Nuance reconnue :** Les détours aériens peuvent avoir des explications pratiques — vents dominants, jet stream, demande commerciale, hubs mondiaux, accords bilatéraux. Cependant, la *systématique* remontée dans l'hémisphère Nord pour des trajets entièrement au Sud reste difficile à expliquer par ces seuls facteurs. Sur une carte azimutale (Terre plane), ces trajets forment des lignes droites logiques.

## 05 La boussole : un seul Nord fixe

La boussole est l'un des instruments de navigation les plus anciens et les plus fiables. Son principe est simple : une aiguille magnétique s'aligne toujours vers le Nord magnétique. Ce fait, observable partout dans le monde avec n'importe quelle boussole, est l'une des observations les plus puissantes sur la structure de notre environnement.


Quelle que soit la position sur Terre, **toutes les boussoles pointent vers le même point fixe au Nord**. Les aimants en anneau (comme ceux des haut-parleurs) ont un pôle central Nord avec le pôle Sud distribué tout le long de la circonférence extérieure — ce qui correspond exactement à la géométrie de la carte azimutale.


Il n'existe pas de « Pôle Sud » magnétique clairement localisé et accessible de la même façon que le Pôle Nord. Le soi-disant « Pôle Sud de cérémonie » en Antarctique n'est pas le vrai pôle magnétique — en témoigne le fait qu'une boussole n'y montrerait pas le Nord à 360° autour de l'observateur, comme cela devrait être le cas si l'on se trouvait véritablement au point antipodal du Pôle Nord.


## 06 GPS et LORAN : la triangulation ne prouve pas le modèle

Le GPS est présenté comme un système entièrement dépendant de satellites en orbite. Mais le principe de triangulation est purement géométrique — il fonctionne que les points de référence soient des satellites ou des tours radio terrestres.


Le système **LORAN** (*Long Range Navigation*), développé pendant la Seconde Guerre mondiale, fonctionnait par triangulation depuis des émetteurs radio terrestres côtiers. LORAN-C (1957–2010) offrait une précision de ~200 m sur les océans Atlantique, Pacifique Nord et dans l'Arctique. Il a été utilisé par l'aviation civile et militaire, la marine marchande et les navires de pêche du monde entier pendant plus de 60 ans — **sans un seul satellite**.


SystèmeTypeÉpoquePrécision

LORAN-CTerrestre1957–2010~200 m
Triangulation GSMTerrestre1990–aujourd'hui50–300 m
GPSSatellite1973–aujourd'hui~3–10 m
eLORAN (moderne)Terrestre2010–aujourd'hui~10–20 m


Le GPS est plus précis et plus universel, mais il n'est pas la seule façon techniquement possible de se localiser. La précision du GPS est une preuve de la qualité de la triangulation, **pas nécessairement de la sphéricité de la Terre**. Les équations géométriques du GPS calculent la distance relative entre émetteur et récepteur — indépendamment du modèle cosmologique.


## 07 L'énigme antarctique : le continent le plus verrouillé du monde

L'Antarctique demeure l'une des dernières zones inexplorées. Contrairement à tous les autres continents, il est le seul territoire où :


- Les revendications territoriales sont gelées indéfiniment (Traité de 1959)

- L'exploitation des ressources est interdite (Protocole de Madrid, 1991)

- L'accès civil est strictement contrôlé par une organisation privée (IAATO)

- Les expéditions indépendantes sont systématiquement interceptées

- Une partie significative reste officiellement non revendiquée (Terre Marie Byrd)


**Question centrale :** Que protège-t-on réellement avec un verrouillage aussi total — plus strict que n'importe quelle frontière nationale, maintenu depuis plus de 65 ans par des nations qui s'opposent sur tout le reste ?

### L'anomalie Cook (1772–1775) : 60 000 km autour de quoi ?

Le Capitaine James Cook, à bord du HMS Resolution, a parcouru plus de **60 000 milles nautiques (~111 000 km)** durant ses trois années d'exploration, traversant trois fois le Cercle Polaire Antarctique. Il atteint sa limite maximale à 71°10' Sud le 3 février 1774, stoppé par une banquise dense.


« À 4 heures du matin, nous avons aperçu les nuages près de l'horizon au sud d'une couleur blanc neige intense... Bientôt nous avons rencontré la glace [...] aussi compacte qu'un mur et qui semblait s'étendre sans fin d'est en ouest. »
— Journal de bord du Capitaine James Cook, 3 février 1774
**L'anomalie géométrique :** Sur un globe, le périmètre de l'Antarctique à 65° S (latitude moyenne de navigation de Cook) est de ~16 900 km. Cook a parcouru environ 50 000 à 70 000 km dans les latitudes subantarctiques en 18 mois cumulés. Cela représenterait **3 à 6 tours complets** du continent — **or Cook ne mentionne nulle part avoir bouclé le continent ni retrouvé son point de départ**. Il décrit au contraire une barrière de glace « s'étendant sans fin d'est en ouest ».


Si le périmètre réel de cette barrière de glace est de ~60 000 km, Cook aurait fait environ un seul tour — cohérent avec sa description d'une « barrière continue ». Cette hypothèse résout simultanément l'anomalie distance/temps et correspond aux descriptions narratives de Cook.


### Le Traité de 1959 : le verrouillage géopolitique

Signé le 1ᵉʳ décembre 1959 à Washington par 12 nations (dont USA, URSS, Royaume-Uni, France, Japon, Argentine, Chili, Australie), le **Traité sur l'Antarctique** gèle toutes les revendications territoriales et interdit toute activité militaire et toute exploitation commerciale. Le Protocole de Madrid (1991) a prolongé cette interdiction jusqu'en 2048.


L'accès est géré par l'**IAATO** (International Association of Antarctica Tour Operators), organisation privée, qui filtre strictement les visiteurs. Les expéditions indépendantes sont systématiquement interceptées. L'espace aérien est restreint. Aucun survol commercial ne passe au-dessus de l'Antarctique — fait unique dans le trafic aérien mondial.


Comment expliquer que les plus grandes puissances mondiales, qui s'opposent sur tout le reste, soient parfaitement alignées depuis 65 ans pour verrouiller l'accès au plus grand continent inexploité de la planète ?


### Les déclarations de l'Amiral Byrd

L'Amiral Richard E. Byrd, explorateur américain de l'Antarctique, a fait plusieurs déclarations publiques troublantes lors d'interviews télévisées. En 1954, il déclare : « *Je voudrais vous voir la terre au-delà du pôle. Cette zone au-delà du pôle est le centre du Grand Inconnu.* » En 1956 lors de l'opération Deep Freeze, il parle d'une terre « *aussi grande que les États-Unis qui n'a jamais été vue par un être humain* » au-delà du pôle Sud.


L'opération militaire **Highjump** (1946–1947), dirigée par Byrd, a mobilisé 4 700 hommes, 13 navires et 33 aéronefs pour ce qui était officiellement une « expédition scientifique ». Elle s'est terminée prématurément dans des conditions non expliquées publiquement. Pourquoi une « expédition scientifique » nécessiterait-elle une flotte militaire de cette ampleur ?


 📷 EMPLACEMENT IMAGE


 Photo historique de l'Amiral Richard E. Byrd ou de l'Opération Highjump (1946-1947)


 4 700 hommes, 13 navires, 33 aéronefs. Photo de la flotte ou portrait de Byrd en tenue polaire.
Alternative : photo aérienne d'un survol antarctique de l'époque.


 Remplacer ce bloc par : ![\2](\1)


### L'Âge Héroïque (1895–1922) et Neuschwabenland

L'Âge Héroïque de l'exploration antarctique voit des expéditions britanniques (Scott, Shackleton), norvégiennes (Amundsen) et australiennes tenter de pénétrer le continent. Amundsen atteint le « Pôle Sud » en décembre 1911, Scott un mois plus tard. Mais aucune de ces expéditions ne cartographie l'intégralité du continent — elles suivent des routes linéaires vers un point unique, sans circumnavigation du périmètre intérieur.


En 1938–1939, l'Allemagne nazie envoie l'expédition **Neuschwabenland** (Nouvelle-Souabe) en Antarctique. Officiellement : une mission d'exploration pour sécuriser des droits baleiniers. Mais l'expédition est dirigée par la Luftwaffe, utilise un porte-hydravions (Schwabenland) et cartographie 350 000 km² de territoire par survol aérien, y plantant des marqueurs métalliques portant la croix gammée. La question reste : pourquoi une opération militaire de cette envergure pour de simples droits de pêche à la baleine, à quelques mois du déclenchement de la Seconde Guerre mondiale ?


 📷 EMPLACEMENT IMAGE


 Carte de l'expédition Neuschwabenland (1938-1939) ou photo du navire Schwabenland


 350 000 km² cartographiés par la Luftwaffe. Territoire revendiqué par l'Allemagne nazie.
Alternative : carte montrant la zone Neuschwabenland sur le continent antarctique.


 Remplacer ce bloc par : ![\2](\1)


### La timeline convergente (1928–1959)


AnnéeÉvénementSignification

1928–1930Byrd I — première exploration aérienneReconnaissance militaire US
1938–1939Neuschwabenland — Allemagne nazie350 000 km² cartographiés par la Luftwaffe
1939–1945Seconde Guerre mondialeActivités antarctiques suspendues officiellement
1946–1947**Opération Highjump** — 4 700 hommes, 13 naviresPlus grande opération militaire antarctique de l'histoire
1947Fin prématurée de HighjumpRaisons non expliquées publiquement
1947–1948Opération WindmillCartographie complémentaire
1955–1956**Opération Deep Freeze** — déclarations de Byrd« Terre aussi grande que les USA au-delà du pôle »
1957–1958Année Géophysique Internationale12 nations collaborent en Antarctique
**1959****Traité sur l'Antarctique**Verrouillage total — toujours en vigueur


En 30 ans, on passe d'explorations pionnières à des opérations militaires massives, puis à un verrouillage international sans précédent. Cette séquence n'a pas d'équivalent pour aucun autre territoire de la planète.


### La Terre Marie Byrd : le territoire de personne

La **Terre Marie Byrd** est la plus grande zone non revendiquée de la surface terrestre — environ 1,6 million de km². Aucune nation ne la revendique. Aucune base permanente n'y est installée. Aucune explication officielle n'est donnée pour cette anomalie géopolitique. Sur un globe, c'est un territoire comme un autre — immense, inexploité et abandonné volontairement par toutes les puissances. Pourquoi ?


### Le Soleil de Minuit austral : un phénomène sous contrôle

Le modèle sphérique prédit un « Soleil de Minuit » en Antarctique pendant l'été austral (décembre–janvier), symétrique à celui observé en Arctique pendant l'été boréal. Cependant, le Soleil de Minuit arctique est observable par n'importe qui depuis la Norvège, la Suède, la Finlande, l'Islande ou le nord du Canada — destinations touristiques accessibles. Le Soleil de Minuit antarctique, lui, n'est observable que depuis des bases militaires ou scientifiques dont l'accès est contrôlé par l'IAATO et les gouvernements. Aucun touriste ne peut aller vérifier librement ce phénomène dans les mêmes conditions qu'en Arctique.


### L'Encyclopédie Américaine (1958)

L'édition 1958 de l'*Encyclopaedia Americana*, publiée un an avant le Traité, décrit l'Antarctique comme un territoire dont **la superficie totale reste « inconnue »** et dont les limites intérieures n'ont jamais été cartographiées. Comment signer un traité international sur un territoire dont on reconnaît ne pas connaître les dimensions ?


## 08 Les fuseaux horaires : une asymétrie révélatrice

💡 En termes simples


Sur un globe, la Terre est divisée en 24 fuseaux horaires — des « tranches d'orange » de 15° de longitude chacune, toutes de la même largeur du pôle nord au pôle sud. C'est simple et symétrique. Mais quand on regarde la carte réelle des fuseaux horaires, elle ressemble à tout sauf à des tranches régulières — surtout dans l'hémisphère sud. Sur une Terre plane (disque vu du dessus), les fuseaux s'élargissent naturellement vers l'extérieur, comme les parts d'une pizza. Plus on s'éloigne du centre (le pôle nord), plus la « part » est large. C'est exactement ce que la carte réelle montre.


### La symétrie attendue vs la réalité observée

Sur un globe parfait, chaque fuseau horaire couvre exactement 15° de longitude — soit environ 1 670 km de large à l'équateur, se rétrécissant progressivement vers les pôles jusqu'à converger en un point. Cette géométrie impose une **symétrie parfaite** entre les deux hémisphères : les fuseaux de l'hémisphère nord devraient être le miroir exact de ceux de l'hémisphère sud.


Or la réalité est radicalement différente :


AspectHémisphère NordHémisphère Sud

Régularité des fuseauxRelativement réguliers (Europe, Amérique du Nord)Extrêmement irréguliers (Pacifique, Océanie)
Décalages extrêmesRaresFréquents (Samoa +13/−11, Kiribati +14)
Largeur des fuseauxConforme aux 15° théoriquesCertains fuseaux couvrent 30° à 60° de longitude
Ligne de changement de dateTraverse l'océan (peu d'anomalies)Zigzags extrêmes (Fidji, Samoa, Tonga, Kiribati)


### Le cas de la Chine : 5 fuseaux en 1

La Chine couvre **62° de longitude** — de 73°E (Kashgar, Xinjiang) à 135°E (Fuyuan, Heilongjiang). Sur un globe, cela correspond à **plus de 4 fuseaux horaires**. Pourtant, la Chine entière fonctionne sur un seul fuseau (UTC+8). Quand il est midi à Pékin, il devrait être 9h du matin à Kashgar — mais l'horloge officielle indique midi. Résultat : le soleil se lève à 10h en hiver à Kashgar.


L'explication officielle est politique (centralisation du pouvoir sous Mao). Mais le fait demeure : un pays de 9,6 millions de km² fonctionne sur un seul fuseau sans que le système ne « s'effondre ». Sur un globe strict, cela devrait créer des incohérences astronomiques majeures. Sur une Terre plane, la distance angulaire entre Kashgar et Pékin est simplement moins grande que ce que la projection Mercator suggère.


### L'Antarctique : pas de fuseau local

Le cas le plus révélateur est l'Antarctique. Sur un globe, le « continent » antarctique devrait avoir ses propres fuseaux horaires — comme l'Arctique, où chaque pays (Norvège, Suède, Finlande, Russie, Canada, Alaska) a son fuseau normal. En Antarctique, **chaque base utilise le fuseau de son pays d'origine** ou le fuseau UTC. La base américaine McMurdo utilise l'heure de la Nouvelle-Zélande (UTC+12). La base argentine Esperanza utilise UTC−3. La base russe Vostok utilise UTC+6.


**Pourquoi c'est significatif :** Sur un globe, tous les fuseaux convergent vers les pôles — au pôle sud géographique, tous les fuseaux se rejoignent en un seul point. Faire un pas dans n'importe quelle direction change théoriquement de fuseau horaire. Cette absurdité géométrique est résolue… en ignorant les fuseaux locaux. Sur une Terre plane avec l'Antarctique en périphérie (le bord extérieur du disque), la notion de « fuseau local » n'a tout simplement pas de sens — les fuseaux s'élargissent vers l'extérieur jusqu'à perdre leur cohérence. C'est exactement ce qu'on observe.

### La ligne de changement de date : des zigzags inexplicables

La ligne internationale de changement de date (LID) devrait théoriquement suivre le méridien 180° — une ligne droite au milieu du Pacifique. En réalité, elle fait des **zigzags spectaculaires** pour contourner des îles et des archipels : elle passe à l'est de la Russie, à l'ouest des Aléoutiennes (USA), puis fait un énorme détour vers l'est pour inclure Kiribati (qui a « sauté » de l'autre côté en 1995), contourne les Samoa (qui ont changé de côté en 2011), et zigzague autour de Tonga et Fidji.


Sur un globe, ces zigzags sont des « ajustements politiques ». Sur une Terre plane, ils reflètent la **distorsion naturelle** des distances aux extrémités du disque — les mêmes distances qui rendent les vols transpacifiques sud inexplicablement longs (voir section §04).


 🎬 EMPLACEMENT VIDÉO


 Les fuseaux horaires : globe vs Terre plane


 Animation comparative montrant les fuseaux sur un globe (symétriques) vs sur une projection azimutale (parts de pizza élargies). Inclure les zigzags de la ligne de changement de date et le cas de l'Antarctique sans fuseau local.


 Remplacer ce bloc par : 


## 09 Synthèse : ce que la cartographie révèle

Les sept sujets de cet article convergent vers un constat : les représentations cartographiques dominantes ne sont pas des vérités neutres mais des **constructions historiques, politiques et culturelles**. L'orientation Nord en haut, la projection Mercator, la présentation de l'Antarctique comme un simple continent austral — chacun de ces éléments résulte de choix délibérés, souvent pris à une époque de domination coloniale européenne.


Bilan des observations
**🗺️ Cartes anciennes :** L'orientation « Nord en haut » est une convention européenne récente — les cartographes islamiques utilisaient le Sud en haut avec une précision supérieure.


**📐 Projections :** Mercator déforme massivement — Afrique 14× plus grande que le Groenland. Azimutale donne les distances exactes depuis le centre.


**🌐 Carte ONU :** Projection azimutale centrée sur le Pôle Nord — identique à une représentation de Terre plane vue du dessus.


**✈️ Routes aériennes :** Plusieurs trajets hémisphère Sud passent systématiquement par l'hémisphère Nord — incohérents sur globe, logiques en ligne droite sur carte azimutale.


**🧭 Boussole :** Un seul centre magnétique Nord observable et fixe. Pas de Pôle Sud équivalent clairement localisé.


**📡 GPS & LORAN :** Navigation mondiale précise sans satellites existe depuis 70 ans. La triangulation est indépendante du modèle cosmologique.


**🧊 Antarctique :** Anomalie Cook (60 000 km autour d'un continent de 14 000 km), Traité de 1959, accès verrouillé depuis 65 ans, déclarations de Byrd.


Ces observations ne prouvent pas à elles seules un modèle cosmologique particulier. Mais elles invitent à interroger la représentation habituelle du monde qu'on nous a enseignée — et à reconnaître que l'Antarctique est la zone géographique la plus verrouillée de la planète, pour des raisons qui restent officiellement non expliquées.


## Références


 - Al-Idrisi, Abū ʿAbd Allāh Muḥammad (1154). *Nuzhat al-mushtāq* / Tabula Rogeriana.

 - Cook, James (1777). *A Voyage Towards the South Pole and Round the World*. Journaux de bord, Archives de l'Amirauté britannique.

 - Mercator, Gerardus (1569). Projection cylindrique conforme.

 - Nations Unies (1946). Emblème officiel — résolution A/RES/92.

 - Traité sur l'Antarctique (1959). Signé à Washington, 12 nations fondatrices.

 - Protocole de Madrid sur la protection de l'environnement en Antarctique (1991).

 - Byrd, Richard E. — Interviews et déclarations publiques (1947, 1954, 1956).

 - Opération Highjump (1946–1947) — archives US Navy.

 - Système LORAN — documentation USCG (United States Coast Guard).

 - Dubay, Eric. *200 Preuves que la Terre n'est pas une Boule* — preuves #42–48 (routes aériennes), #106–111 (boussole et Pôle Sud).

 - Carte de Piri Reis (1513) — Musée du palais de Topkapı, Istanbul.

 - Carte d'Urbano Monte (1587) — David Rumsey Map Collection.


					

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