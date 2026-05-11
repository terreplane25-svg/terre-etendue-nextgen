---
title: "Le théodolite céleste"
description: ".nx-nav{width:100%;background:#F7F2E8;border-bottom:1px solid #DDD5C5;padding:0 2rem;position:sticky;top:0;z-index:999} .nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;ju..."
date: "2026-04-29"
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
:root{--bg:#F7F2E8;--bg2:#EDE5D5;--cobalt:#1B5E3C;--cobalt-l:#2D8B57;--cobalt-g:rgba(30,58,138,.15);--t1:#2C1810;--t2:#5C4A3A;--t3:#8A7A6A;--bdr:#DDD5C5;--f1:'Cormorant Garamond',Georgia,serif;--f2:'Outfit',sans-serif;--f3:'Cormorant Garamond',Georgia,serif}
.o8{background:var(--bg);color:var(--t1);padding:0}
.o8-h{padding:5rem 2rem 3.5rem;text-align:center;position:relative;overflow:hidden}
.o8-h::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 50% at 50% 30%,rgba(30,58,138,.05),transparent 70%);pointer-events:none}
.o8-tag{display:inline-block;font-family:var(--f2);font-size:.62rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--cobalt-l);background:var(--cobalt-g);border:1px solid rgba(30,58,138,.25);padding:.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.o8-title{font-family:var(--f1);font-size:clamp(1.7rem,4.5vw,2.5rem);font-weight:700;color:var(--cobalt-l);line-height:1.15;margin:0 0 1rem;max-width:800px;margin-left:auto;margin-right:auto}
.o8-sub{font-family:var(--f3);font-size:1.02rem;line-height:1.7;color:var(--t2);max-width:650px;margin:0 auto 2rem}
.o8-meta{max-width:800px;margin:0 auto;padding:1.2em 0;border-top:1px solid var(--bdr);border-bottom:1px solid var(--bdr);display:flex;flex-wrap:wrap;gap:.5em 2em;font-family:var(--f2);font-size:.75rem;color:var(--t3)}
.o8-meta dt{font-weight:600;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem}
.o8-meta dd{margin:0 0 .6em;color:var(--t2)}
.o8-lay{display:flex;gap:2.5rem;max-width:1200px;margin:0 auto;padding:2.5rem 2rem 5rem;align-items:flex-start}
.o8-nav{flex:0 0 255px;position:sticky;top:80px;max-height:calc(100vh - 100px);overflow-y:auto;padding:1.5rem;background:var(--bg2);border:1px solid var(--bdr);border-radius:10px}
.o8-nav::-webkit-scrollbar{width:3px}.o8-nav::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}
.o8-nav__t{font-family:var(--f2);font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--cobalt-l);margin:0 0 1rem;padding-bottom:.6rem;border-bottom:1px solid var(--bdr)}
.o8-nav ul{list-style:none;padding:0;margin:0}.o8-nav li{margin-bottom:.35rem}
.o8-nav a{display:block;font-family:var(--f2);font-size:.76rem;color:var(--t3);text-decoration:none;padding:.4em .8em;border-radius:5px;border-left:2px solid transparent;transition:all .25s ease;line-height:1.35}
.o8-nav a:hover{color:var(--t1);background:rgba(30,58,138,.06);border-left-color:var(--cobalt-l)}
.o8-nav a.active{color:var(--cobalt-l);background:var(--cobalt-g);border-left-color:var(--cobalt-l);font-weight:500}
.o8-nav .num{font-size:.6rem;font-weight:600;color:var(--cobalt-l);margin-right:.4em;opacity:.7}
.o8-nav__bk{display:block;margin-top:1.2rem;padding:.6em 1em;background:#2D8B57;color:#2C1810;font-family:var(--f2);font-size:.72rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;text-align:center;border-radius:5px;transition:background .3s ease}
.o8-nav__bk:hover{background:#3DA06A}
.o8-b{flex:1;min-width:0;max-width:800px;font-family:var(--f3);font-size:clamp(1rem,1.8vw,1.08rem);line-height:1.75;color:var(--t1)}
.o8-b p{margin-bottom:1.4em;text-align:justify;hyphens:auto}
.o8-b a{color:var(--cobalt-l);text-decoration:underline;text-underline-offset:3px}
.o8-b h2{font-family:var(--f1);font-size:clamp(1.4rem,3vw,1.85rem);font-weight:700;color:var(--t1);margin:3em 0 .8em;padding-bottom:.4em;border-bottom:1px solid var(--bdr);line-height:1.25;scroll-margin-top:90px}
.o8-b h3{font-family:var(--f2);font-size:clamp(1rem,1.8vw,1.15rem);font-weight:600;color:var(--cobalt-l);text-transform:uppercase;letter-spacing:.06em;margin:2em 0 .6em;line-height:1.35;scroll-margin-top:90px}
.sn{font-family:var(--f2);font-size:.65rem;font-weight:600;color:var(--cobalt-l);background:var(--cobalt-g);border:1px solid rgba(30,58,138,.25);padding:.2em .6em;border-radius:3px;margin-right:.6em;vertical-align:middle}
.bq{margin:2em 0;padding:1.5em 2em;background:linear-gradient(135deg,var(--cobalt-g),transparent 70%);border-left:3px solid var(--cobalt);border-radius:0 8px 8px 0;font-family:var(--f3);font-style:italic;font-size:1.02em;line-height:1.75;color:var(--t1)}
.bq cite{display:block;margin-top:.8em;font-size:.78em;font-style:normal;font-family:var(--f2);color:var(--t3)}
.db{margin:2em 0;padding:1.4em 1.8em;background:var(--bg2);border:1px solid var(--bdr);border-radius:8px}
.db__l{display:inline-block;font-family:var(--f2);font-size:.65rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:var(--cobalt-l);background:var(--cobalt-g);padding:.2em .7em;border-radius:3px;margin-bottom:.8em}
.db p{font-size:.92rem;margin-bottom:.8em;text-align:left}
.kp{margin:1.5em 0;padding:1.2em 1.6em;background:var(--bg2);border-left:3px solid var(--cobalt);border-radius:0 8px 8px 0;font-family:var(--f2);font-size:.9rem;line-height:1.6;color:var(--t2)}
.kp strong{color:var(--t1)}
.tw{margin:2em 0;overflow-x:auto}
.tb{width:100%;border-collapse:collapse;font-family:var(--f2);font-size:.75rem}
.tb th{background:var(--bg2);color:var(--cobalt-l);font-weight:600;text-transform:uppercase;letter-spacing:.06em;font-size:.64rem;padding:.6em .7em;text-align:left;border-bottom:1px solid var(--bdr)}
.tb td{padding:.5em .7em;border-bottom:1px solid var(--bdr);color:var(--t2);vertical-align:top}
.tb tr:hover td{background:rgba(30,58,138,.03)}
.o8-refs{margin-top:3em;padding-top:2em;border-top:1px solid var(--bdr)}
.o8-refs h2{border-bottom:none;padding-bottom:0;font-size:1.3rem}
.o8-refs ol{padding-left:1.5em;font-family:var(--f2);font-size:.82rem;color:var(--t2);line-height:1.7}
.o8-refs li{margin-bottom:.6em}
@media(max-width:900px){.o8-lay{flex-direction:column;padding:1.5rem}.o8-nav{position:static;flex:none;width:100%;max-height:none;margin-bottom:2rem}.o8-h{padding:3.5rem 1.5rem 2.5rem}}


 L'Observatoire — OBS-2026-008
 
# Le théodolite céleste : 11 000 points de données contre la courbure

 Une méthode inédite utilise les occultations stellaires et les éclipses solaires pour tester la géométrie de la Terre. 11 320 points de données. Résultat : la trigonométrie plane fonctionne parfaitement — la correction de courbure n'est jamais nécessaire.
 
 AuteurTerre Étendue Islam (d'après SpaceAudits / Llamazing)
 DateAvril 2026 — v1.0
 Lecture~35 min
 SourcesDonnées NASA · Stellarium · Astropy Python · 12 pics montagneux · 2 éclipses solaires
 

 
 
## Sommaire

 
 [01 Ptolémée et la navigation](#t-intro)

 - [02 La méthode du théodolite](#t-methode)

 - [03 Occultations stellaires : 12 pics](#t-occultations)

 - [04 Éclipse d'avril 2024](#t-eclipse2024)

 - [05 Éclipse d'octobre 2023](#t-eclipse2023)

 - [06 La hauteur du Soleil](#t-soleil)

 - [07 Le modèle globe échoue](#t-globe)

 - [08 La réfraction ne sauve rien](#t-refraction)

 - [09 Conclusion](#t-ccl)

 - [Références](#t-refs)

 

 [← Retour à l'Observatoire](/lobservatoire/)
 

## 01 Ptolémée, la navigation céleste et le modèle à deux sphères

💡 En termes simples


Depuis 2 000 ans, les marins utilisent les étoiles pour se repérer en mer. Pour que ça fonctionne, ils utilisent un modèle simple : une grande sphère céleste (les étoiles) qui tourne autour d'une petite sphère terrestre (la Terre). Ce modèle fonctionne parfaitement pour la navigation — il donne les bonnes positions. Mais la question que personne ne pose est : fonctionne-t-il parce que la Terre est une sphère, ou parce que la géométrie angulaire est la même sur un plan que sur une sphère quand la « sphère céleste » n'est qu'un hémisphère de vision ?


Ptolémée, dans sa *Cosmographia*, explique que l'horizon de chaque observateur peut être imaginé comme un plan tangent à la sphère céleste, divisant le ciel en deux moitiés : l'hémisphère visible au-dessus et l'hémisphère caché en dessous. La navigation céleste moderne utilise toujours ce modèle — les positions **apparentes** des astres, pas leurs positions réelles.


« Un observateur regardant le ciel nocturne sans rien savoir de la géographie et de l'astronomie pourrait spontanément avoir l'impression de se trouver sur un plan situé au centre d'une immense sphère creuse avec les corps célestes attachés à sa surface intérieure. Ce modèle naïf de l'univers était en usage depuis des millénaires. Encore aujourd'hui, il est un outil utile pour la navigation céleste. »
— Henning Umland, A Short Guide to Celestial Navigation (2015)
Le théodolite céleste exploite cette observation d'une manière nouvelle : au lieu d'utiliser les positions **apparentes** (qui gardent le système cohérent quelle que soit la géométrie), il utilise les positions **vraies** des étoiles — créant ainsi un **test externe** du modèle.


## 02 La méthode : comment fonctionne le théodolite céleste

Le protocole est simple :


Protocole en 4 étapes
**1.** Observer le moment exact où une étoile disparaît derrière un sommet montagneux (occultation).


**2.** Consulter un almanach astronomique pour déterminer la position vraie de l'étoile à cet instant (coordonnées J2000, non corrigées pour la réfraction).


**3.** Former un triangle rectangle : base = base de la montagne, sommet = pic, observateur. Calculer l'angle géométrique vers le pic par trigonométrie simple : θ = arctan(ΔH / distance).


**4.** Comparer l'angle géométrique calculé avec l'angle almanach de l'étoile.


**Le résultat empirique :** l'angle physique vers le sommet de la montagne est **identique** à l'angle almanach vers l'étoile — alors qu'aucune correction de courbure terrestre n'a été appliquée dans le calcul. La plupart des observations sont faites à des distances (40-130 km) où la courbure devrait être significative.


**Le test décisif :** Quand on refait les calculs avec la « géométrie globe » (en tenant compte de la courbure), les nombres sont décalés — exactement de la quantité de courbure introduite. Pour retrouver le bon résultat, il faut invoquer la réfraction atmosphérique pour compenser exactement la courbure ajoutée. La géométrie plane donne le bon résultat directement. La géométrie globe doit ajouter puis soustraire la même quantité.


## 03 Les occultations stellaires : 12 pics montagneux

À ce jour, des mesures de théodolite céleste ont été effectuées sur 12 sommets, à des distances allant de 8,8 km à 130,7 km :


PicDistance (m)ΔH pic (m)Angle d'occultation

Hound's Tooth8 8041 65610° 37′ 03″
Varley SE2 (Squamish)16 7261 4204° 47′ 09″
Old-Blyn Mountain22 0785921° 07′ 32″
Blodgett Peak35 9107961° 11′ 21″
Ediz-Blyn Mountain40 902——
Cheyenne Mountain42 6308080° 37′ 00″
Mount Rosa47 7301 4331° 42′ 41″
Getaway Mountain48 9907520° 45′ 17″
Blue Mountain49 770——
Pike's Peak50 7782 2262° 33′ 19″
Green Mountain52 690——
**North Peak****130 700****1 692****0° 58′ 05″**


Le résultat le plus distant — North Peak à 130,7 km — est particulièrement significatif. À cette distance, la courbure théorique cacherait **~1 340 m**. L'angle calculé par trigonométrie plane correspond néanmoins exactement à la position vraie de l'étoile au moment de l'occultation. Aucune correction de courbure n'a été nécessaire.


## 04 L'éclipse solaire d'avril 2024 : 6 770 points de données

Le 8 avril 2024, une éclipse solaire totale traverse les États-Unis du sud-ouest au nord-est. La totalité dure de 16h38 à 19h55 UTC, avec une durée maximale de 4 minutes 28 secondes pour un point donné. L'auteur de SpaceAudits applique la méthode du théodolite céleste à cette éclipse — étendant la distance d'observation de 130 km à **7 772 km** (un facteur 60).


### La découverte : Soleil et Lune sur des « sphères » différentes

En traçant l'angle d'altitude en fonction de la distance au sol pour le Soleil et la Lune séparément :


AstreTaux de descenteMilles nautiques/degréRayon de sphère céleste

Soleil−8,994 × 10⁻⁶ deg/m60,0386 370 773 m
**Lune****−9,131 × 10⁻⁶ deg/m****59,133****6 274 677 m**


Le Soleil descend de 1° tous les 60,04 milles nautiques — exactement ce qu'on attend (60 NM/degré = la définition d'un mille nautique). Mais la Lune descend de 1° tous les 59,13 milles nautiques seulement. Elle se comporte comme si elle voyageait sur une sphère céleste **plus petite** que celle du Soleil — environ 96 km plus basse. Cette différence de 1,6% est inattendue dans le modèle standard et n'avait jamais été documentée avant cette analyse.


### Le calcul de la hauteur du Soleil

En utilisant les données NASA du trajet de l'ombre de l'éclipse (6 770 points à intervalles d'une seconde), l'auteur effectue le calcul suivant :


Méthode de calcul
**1.** Fixer la hauteur de la Lune à 6 274 677 m (dérivée de la section précédente).


**2.** Pour chaque point de données, calculer l'angle d'occultation par trigonométrie : θ = arctan(h_lune / d_lune).


**3.** Utiliser ce même angle pour calculer la hauteur du Soleil : h_soleil = d_soleil × tan(θ).


**4.** Répéter pour les 6 770 points de données.


**Résultat :**


**Hauteur moyenne du Soleil : 6 374 896 m**

**Écart type : 6 203 m (0,1% de la valeur nominale)**


Sur 6 770 points de données couvrant 112 minutes, des distances variant de 2 601 000 à 7 772 000 m (facteur 3), des altitudes variant de 70° à 19° (changement de 51°), et des azimuts balayant 140° — le résultat est remarquablement constant. **Aucune correction de courbure terrestre n'a été appliquée.**

## 05 L'éclipse d'octobre 2023 : confirmation indépendante

La même technique appliquée à l'éclipse annulaire du 14 octobre 2023 donne :


ÉclipsePoints de donnéesHauteur moyenne du SoleilÉcart type

Avril 2024 (totale)6 7706 374 896 m6 203 m
**Octobre 2023 (annulaire)****4 550****6 367 512 m****7 506 m**


Deux éclipses indépendantes, des mois différents, des trajectoires différentes, des conditions atmosphériques différentes — et des résultats cohérents à 0,1%. **11 320 points de données au total.**


## 06 La hauteur du Soleil : ~6 375 km au-dessus d'une surface plane

Les deux éclipses convergent vers une hauteur du Soleil d'environ **6 370-6 375 km**. Ce nombre est frappant : c'est aussi la valeur du rayon terrestre dans le modèle globe. Mais dans l'interprétation du théodolite céleste, ce n'est pas un rayon — c'est une **hauteur physique** au-dessus d'une surface plane.


💡 En termes simples


Le Soleil se comporte comme s'il était à ~6 375 km au-dessus d'une Terre plane, pas à 150 millions de km au-delà d'une Terre sphérique. La trigonométrie plane, sans aucune correction de courbure, produit des résultats cohérents à 0,1% sur plus de 11 000 mesures. La question que pose l'auteur est : « Est-ce le sol sous nos pieds qui courbe ? Ou est-ce le ciel qui *semble* courber à cause de la façon dont nos yeux le perçoivent — notamment avec la même valeur de rayon ? »


La Lune, elle, se comporte comme si elle était à ~6 275 km — environ 100 km plus bas que le Soleil. Cette différence de hauteur est cohérente avec le fait que le Soleil et la Lune apparaissent de la même taille angulaire (~0,53°) bien qu'ils soient à des hauteurs différentes dans ce modèle : le Soleil est plus grand mais plus haut, la Lune est plus petite mais plus basse.


## 07 Quand le modèle globe est appliqué : il échoue


### La distance Lune : 274 500 km au lieu de 356 000-399 000 km

En appliquant le taux de descente angulaire de la Lune (88,7° de longitude pour atteindre 0°) au modèle globe, le calcul donne une distance Terre-Lune de **274 500 km**. La valeur attendue est 356 900 km (périgée) à 399 100 km (apogée). Le résultat est **en dehors de la fourchette attendue**.


### La hauteur du Soleil : triangle impossible

En tentant de calculer la hauteur du Soleil dans le modèle globe avec la distance minimale Terre-Lune (356 900 km), **aucune solution n'est trouvée**. La somme des angles intérieurs du triangle (centre de la Terre → observateur → Soleil) dépasse 180° — un triangle mathématiquement impossible.


**Ce que cela signifie :** La géométrie plane produit des résultats cohérents (σ = 0,1%) sur 11 320 points de données sans aucune correction. La géométrie globe produit soit des distances lunaires hors de la fourchette attendue, soit des triangles mathématiquement impossibles. L'auteur note que « la réfraction pourrait résoudre le problème en courbant le trajet de la lumière vers l'observateur, mais cela dépasse le cadre de cette étude ».

## 08 La réfraction ne sauve rien

L'analyse du théodolite céleste produit un résultat secondaire important : la divergence entre la **position physique** calculée du Soleil/de la Lune et la **position apparente** observée (même dans Stellarium sans correction de réfraction). À la fin de la fenêtre d'observation, la position apparente de la Lune est à 20° d'altitude tandis que sa position physique calculée est à 40° — un écart de 20°.


Les modèles standards de réfraction astronomique sont basés sur des **sphères concentriques stratifiées** — des couches d'air homogènes empilées autour d'une Terre sphérique. L'analyse du théodolite montre que lorsqu'on applique la « géométrie globe » aux données, la réfraction nécessaire pour compenser la courbure est systématiquement égale au **demi-angle central** (γ/2) entre l'observateur et le pic — c'est-à-dire exactement la quantité de courbure ajoutée. La réfraction annule la courbure. Pourquoi ajouter un terme pour le soustraire immédiatement ? (Voir aussi [O4](/lhorizon-la-perspective-et-la-refraction-ce-que-loptique-explique-vraiment/).)


L'analyse des émergences (étoiles qui *apparaissent* de derrière un pic) contre les occultations (étoiles qui *disparaissent*) produit des exigences de réfraction contradictoires selon la direction. Si la réfraction était un véritable phénomène atmosphérique indépendant, elle ne devrait pas changer de comportement selon que l'étoile apparaît ou disparaît.


## 09 Conclusion : la géométrie plane fonctionne, la géométrie globe échoue

Bilan quantitatif
**11 320 points de données** (6 770 + 4 550) provenant de 2 éclipses solaires


**12 sommets montagneux** (8,8 km à 130,7 km) pour les occultations stellaires


**Hauteur du Soleil : 6 375 km** (σ = 0,1%) par trigonométrie plane


**Hauteur de la Lune : 6 275 km** (100 km plus basse que le Soleil)


**Aucune correction de courbure** n'a été nécessaire — jamais


**Le modèle globe produit :** une distance lunaire hors fourchette (274 500 km vs 357-399 000 km) et un triangle impossible pour le Soleil


La méthode du théodolite céleste n'est pas une théorie — c'est un **protocole de mesure reproductible**. N'importe qui peut le reproduire avec un chronomètre, un almanach astronomique et une vue dégagée sur un sommet montagneux. Les données des éclipses sont publiées par la NASA. Les calculs sont documentés en Python et vérifiables. Le programme « Celestial Bounty » offre jusqu'à 200 $ par observation qualifiante pour encourager la reproduction indépendante.


## Références


 - SpaceAudits / Llamazing (2025-2026). « Celestial Theodolite & Solar Eclipses ». Vault Obsidian Publish.

 - NASA SVS (2024). « Total Solar Eclipse Path Data ». [svs.gsfc.nasa.gov/5073](https://svs.gsfc.nasa.gov/5073). Fichier KML avec 6 770 points à 1 seconde d'intervalle.

 - Ptolémée (~150 EC). *Cosmographia*. Trad. annotée : Princeton University Press, 2020.

 - Umland, H. (2015). *A Short Guide to Celestial Navigation*.

 - Heggie, D.C. (1982). *Archaeoastronomy in the Old World*. Cambridge University Press.

 - Salmon, T. (1777). *The New Universal Geographical Grammar*.

 - Copernic, N. (1543). *De Revolutionibus Orbium Coelestium*. « Que personne n'attende rien de certain de l'astronomie. »

 - Module Python Astropy — calcul des positions célestes.

 - Stellarium — planétarium open source pour vérification des positions apparentes.

 - SpaceAudits (2026). « Celestial Bounty — Programme de récompense ». Jusqu'à 200 $ par observation qualifiante.


					

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