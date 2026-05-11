---
title: "Le théodolite céleste"
description: "Depuis 2 000 ans, les marins utilisent les étoiles pour se repérer en mer. Pour que ça fonctionne, ils utilisent un modèle simple : une grande sphère céleste (les étoiles) qui tourne autour d'une petite sphère terrestre..."
date: "2026-04-29"
author: "Terre Etendue"
category: "observatory"
tags: ["lobservatoire"]
---

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


**Hauteur moyenne du Soleil : 6 374 896 m****
Écart type : 6 203 m (0,1% de la valeur nominale)****

Sur 6 770 points de données couvrant 112 minutes, des distances variant de 2 601 000 à 7 772 000 m (facteur 3), des altitudes variant de 70° à 19° (changement de 51°), et des azimuts balayant 140° — le résultat est remarquablement constant. Aucune correction de courbure terrestre n'a été appliquée.**


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