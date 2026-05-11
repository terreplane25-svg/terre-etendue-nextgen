---
title: "L'hypothèse nulle : dynamique et cinématique"
description: "Imaginez deux commentateurs sportifs qui décrivent le même match de football. L'un dit : « Le joueur court vers la gauche à 10 km/h. » L'autre dit : « Le terrain glisse vers la droite à 10 km/h sous un joueur immobile...."
date: "2026-04-29"
author: "Terre Etendue"
category: "headquarters"
tags: ["le-nexus"]
---

## 01 Le problème fondamental


💡 En termes simples


Imaginez deux commentateurs sportifs qui décrivent le même match de football. L'un dit : « Le joueur court vers la gauche à 10 km/h. » L'autre dit : « Le terrain glisse vers la droite à 10 km/h sous un joueur immobile. » Le match est le même. Les buts sont les mêmes. Le résultat est le même. Seul le choix du commentateur change. C'est exactement ce qui se passe entre l'héliocentrisme (« la Terre tourne ») et le géocentrisme (« le ciel tourne »). Même match. Même résultat. Commentaire différent.


La physique divise la description du mouvement en deux catégories. La **cinématique** décrit le mouvement avec des positions, des vitesses et des accélérations — elle dit *comment* les choses bougent. La **dynamique** ajoute la masse et la force — elle prétend dire *pourquoi* les choses bougent. La prétention centrale de la physique moderne est que la dynamique est plus fondamentale que la cinématique, qu'elle « explique » le mouvement au lieu de simplement le « décrire ».


Cet article démontre que cette prétention est fausse. La dynamique est la cinématique multipliée par 1. La masse s'annule de toutes les équations du mouvement. Les solutions dynamiques ne peuvent pas diverger des solutions cinématiques parce qu'elles sont algébriquement identiques. Et le choix entre géocentrisme et héliocentrisme est un choix de commentaire, pas de physique.


## 02 Ce que Newton a vraiment écrit : une équation d'équilibre


Newton n'a pas écrit F = ma. Il a écrit :


L'équation originale de Newton
**F − ma = 0**


C'est une **équation d'équilibre**. Pour chaque action (F), il y a une réaction égale et opposée (ma). Le total est toujours zéro. Il n'y a pas de « cause ». Il y a une contrainte.


La forme moderne **F = ma** réécrit cette équation comme un énoncé causal : « la force *cause* l'accélération ». Mais l'équation originale de Newton dit que le système est toujours en équilibre et que toutes les forces (y compris les réactions inertielles) s'annulent. La seconde forme ne privilégie aucun terme comme « la cause ». C'est une différence logique fondamentale, pas une nuance de notation (Bouw 2013, p. 416).


## 03 La masse s'annule : la preuve algébrique


L'équation généralisée des forces dans un référentiel en rotation contient quatre termes :


Quatre forces, un seul label
**Force imposée** (gravité, poids) — change la position ou la direction


**Force centrifuge** — tire vers l'extérieur du centre de rotation


**Force de Coriolis** — dévie un objet en mouvement sur une plateforme en rotation


**Force d'Euler** — réaction gyroscopique


En physique officielle, la première est « réelle » et les trois autres sont « fictives ». Cette distinction est arbitraire : les quatre contiennent le facteur **m**.


L'équation généralisée somme les quatre :


**Fimposée + Fcentrifuge + FCoriolis + FEuler = 0**


Chaque terme est de la forme **m × a**. Divisez chaque terme par m :


**aimposée + acentrifuge + aCoriolis + aEuler = 0**


**La masse a disparu de chaque terme.** Ce qui reste est une équation d'accélérations pures. L'équation de force est devenue une équation cinématique. Le contenu « dynamique » s'est évaporé.


**Le tour de passe-passe :** Considérez la vitesse d'un corps en mouvement circulaire : **v = ωr**. C'est cinématique. Maintenant multipliez les deux côtés par m/m (= 1) : **mv = mωr**. Renommez le côté gauche « p » (quantité de mouvement) : **p = mωr**. Déclarez « dynamique ». Mais m/m = 1. Rien n'a été ajouté. L'équation dynamique contient exactement la même information que l'équation cinématique. La seule différence est un label.


## 04 GM = le ratio de Kepler × 4π²


Chaque planète en orbite autour du Soleil partage la même valeur :


Planètea (m)T (s)a³/T²

Mercure5,791 × 10¹⁰7 600 5303,3617 × 10¹⁸
Vénus1,082 × 10¹¹19 414 1663,3617 × 10¹⁸
Terre1,496 × 10¹¹31 558 1183,3617 × 10¹⁸
Mars2,279 × 10¹¹59 355 0723,3616 × 10¹⁸
Jupiter7,783 × 10¹¹374 335 5263,3650 × 10¹⁸
Saturne1,427 × 10¹²929 596 6083,3608 × 10¹⁸
Uranus2,871 × 10¹²2 651 486 4003,3640 × 10¹⁸
Neptune4,498 × 10¹²5 200 848 0003,3649 × 10¹⁸


Kepler a trouvé ce ratio en 1619 à partir des observations de Brahe. **Pas de théorie, pas de force, pas de masse, pas de G.** Juste des distances et des périodes mesurées depuis la Terre. Le ratio est le même pour Mercure (0,39 UA, 88 jours) et Neptune (30 UA, 165 ans).


### Les trois couches d'interprétation


**Couche 1 — Kepler (1619) :** a³/T² = 3,36 × 10¹⁸ m³/s². Des distances et des temps. C'est la mesure brute.


**Couche 2 — Newton (1687) :** GM = 4π² × (a³/T²) = 1,327 × 10²⁰ m³/s². Le 4π² vient de la géométrie du cercle. Newton a nommé ce produit « GM » et lui a donné une histoire (F = GMm/r²). Mais GM est juste le ratio de Kepler multiplié par une constante géométrique. **Aucune information nouvelle sur le Soleil n'a été ajoutée.**


**Couche 3 — Cavendish (1798) :** M = GM/G = 1,99 × 10³⁰ kg. G vient d'une balance de torsion (des boules de plomb sur un fil). C'est la **seule mesure non-orbitale** de toute la chaîne. Les différents laboratoires obtiennent des valeurs de G qui ne s'accordent pas (voir [N4](/la-gravite-70-theories-et-aucune-certitude/)). Changez la valeur de G → « la masse du Soleil » change. **Le ciel ne change pas.**


**Ce que « la masse du Soleil » signifie réellement :** (ratio mesuré dans le ciel) ÷ (boules de plomb dans un laboratoire). Sans G, il n'y a pas de masse. Il y a juste le ratio. Et personne en mécanique orbitale n'utilise jamais M seul — chaque équation utilise GM comme une unité indivisible. La NASA/JPL publie GM à 12+ chiffres significatifs. Ils ne le séparent jamais.


## 05 La masse en kilogrammes : un artefact de laboratoire


Pour obtenir la « masse » d'un corps céleste en kilogrammes, il faut diviser GM par G. Mais G est la constante fondamentale la moins bien connue de toute la physique (~5 chiffres significatifs). Les mesures modernes ne s'accordent pas entre elles :


SourceG (× 10⁻¹¹ m³/kg/s²)

CODATA 20186,67430 ± 0,00015
CODATA 20146,67408 ± 0,00010
Quinn 20136,67545 ± 0,00018


Ces valeurs sont incompatibles au-delà de leurs propres incertitudes déclarées. Personne ne sait pourquoi. La « masse du Soleil » est littéralement un nombre précis (a³/T²) divisé par un nombre imprécis (G) provenant d'une expérience complètement différente. **Chaque couche ajoute de l'interprétation. Aucune n'ajoute de l'information.**


Et surtout : **on ne peut pas obtenir la masse d'une planète à partir de sa propre orbite.** La formule GM = 4π²a³/T² donne la masse de ce qui est *au centre* — l'objet orbitté, pas l'objet orbitant. La masse de la planète s'annule : F = GMm/r² = mv²/r → m s'annule → GM = 4π²a³/T². Pour connaître le GM de Mercure, il a fallu attendre la sonde MESSENGER en orbite (2011-2015). Avant cela, la masse de Mercure était « si incertaine qu'il ne semble pas utile d'appliquer une correction » (de Sitter, 1938).


## 06 Le problème des trois corps : là où la dynamique s'effondre


💡 En termes simples


Si la gravité de Newton fonctionne parfaitement, on devrait pouvoir calculer le mouvement de 3 corps qui s'attirent mutuellement. Or en 1887, un mathématicien nommé Bruns a prouvé que c'est impossible — pas « difficile », pas « pas encore résolu » : mathématiquement impossible. Les équations n'ont pas de solution générale. Pour 2 corps, ça marche (Kepler). Pour 3 ou plus, la dynamique échoue. Pourtant, les éphémérides (les tables de positions des planètes) fonctionnent parfaitement depuis Kepler. Comment ? Parce qu'elles utilisent la cinématique — des positions mesurées et extrapolées — pas la dynamique.


En 1887, Heinrich Bruns prouve que le problème gravitationnel à N corps n'a pas d'intégrales algébriques au-delà des 10 intégrales classiques (énergie + quantité de mouvement + moment cinétique). La 11ᵉ intégrale — le vecteur de Laplace, qui ferme le problème à 2 corps — **n'existe pas** pour 3 corps ou plus. En 1890, Henri Poincaré généralise ce résultat : le problème des trois corps n'a pas de solution analytique générale.


Cela signifie que la décomposition « la Lune est perturbée par le Soleil de X degrés par an, par Jupiter de Y secondes d'arc par siècle » n'a **aucune base mathématique rigoureuse**. Le système Terre-Lune-Soleil est couplé. Les interactions sont non linéaires et ne peuvent pas être proprement partitionnées (voir aussi [N4](/la-gravite-70-theories-et-aucune-certitude/), section précession lunaire).


## 07 Le même ciel, des forces différentes


Gerardus Bouw (2013) effectue un calcul complet de décomposition des forces dans le référentiel géocentrique pour 11 corps célestes. Les résultats sont spectaculaires :


CorpsVitesse (km/s)Force requise (N)

Soleil (héliocentrique)300 (référentiel propre)
**Soleil (géocentrique)****10 909****1,58 × 10³³**
Lune281,50 × 10²³
Jupiter56 7587,86 × 10³⁰
α Centauri A1 466 620 574 (~4,9c)4,71 × 10³⁸
**Sirius A****5 683 018 964 (~19c)****1,78 × 10³⁹**


Les forces sont gigantesques. Les vitesses dépassent la lumière. Le GM effectif de la Terre devrait être 10²⁷ fois plus grand que sa valeur newtonienne pour retenir le Soleil. Mais — et c'est le point central — **rien de cela ne change une seule observation :**


ObservablePrédiction héliocentriquePrédiction géocentriqueMatch

Jour sidéral86 164,09 s86 164,09 s✓
Année solaire365,256 j365,256 j✓
Déclinaison max du Soleil±23,44°±23,44°✓
Rétrogradation de Mars~72 j~72 j✓
Parallaxe annuelle d'α Cen0,7474″0,7474″✓
Aberration stellaire20,49″20,49″✓
Pendule de Foucaultsin(φ) × 360°/jsin(φ) × 360°/j✓
Éclipses lunaires (100 ans)identiquesidentiques✓


**Chaque observable est identique**, y compris ceux qui sont censés « prouver » que la Terre tourne (Foucault, aberration, parallaxe). Ils prouvent seulement qu'il y a une rotation relative entre l'observateur et la sphère céleste — ce sur quoi les deux cadres sont d'accord. Les différences sont entièrement dans les labels : à qui appartient la période ? à qui appartient la vitesse ? quel est le « vrai » référentiel ? Ce ne sont pas des mesures. Ce sont des choix de commentaire.


## 08 Ce que les physiciens admettent


« La lutte, si violente aux premiers jours de la science, entre les vues de Ptolémée et de Copernic serait alors tout à fait dépourvue de sens. L'un ou l'autre système de coordonnées pourrait être utilisé avec une justification égale. Les deux phrases, "le Soleil est au repos et la Terre se déplace" ou "le Soleil se déplace et la Terre est au repos" signifieraient simplement deux conventions différentes. »
— Albert Einstein et Leopold Infeld, L'Évolution de la physique (1938), p. 212
« Bien qu'il ne soit pas rare que les gens disent que Copernic a prouvé que Ptolémée avait tort, ce n'est pas vrai. On peut utiliser l'un ou l'autre modèle comme description de l'univers, car nos observations du ciel peuvent être expliquées en supposant soit que la Terre, soit que le Soleil est au repos. »
— Stephen Hawking et Leonard Mlodinow, The Grand Design (2010), p. 39
« Cela nous donne la liberté de revenir au point de vue de Ptolémée d'une "Terre immobile". [...] Du point de vue supérieur d'Einstein, Ptolémée et Copernic ont également raison. »
— Max Born, Einstein's Theory of Relativity (1965), pp. 276-277
« Je peux vous construire un univers à symétrie sphérique avec la Terre en son centre, et vous ne pouvez pas le réfuter sur la base des observations. Vous ne pouvez l'exclure que sur des critères philosophiques. »
— George F. R. Ellis, Scientific American (octobre 1995), p. 55
« Les mouvements de l'univers sont les mêmes que l'on adopte le mode de vue ptoléméen ou copernicien. Les deux sont en effet également corrects ; seul le second est plus simple et plus pratique. »
— Ernst Mach, La Mécanique (1883), Chapitre II
« Ces deux propositions, "la Terre tourne" et "il est plus commode de supposer que la Terre tourne", ont une seule et même signification. »
— Henri Poincaré, La Science et l'Hypothèse (1902), Chapitre VII


## 09 Conclusion : le commentaire n'est pas le match


Résumons ce que cet article a démontré :


Cinq résultats convergents
**1.** Newton a écrit F − ma = 0 (équilibre), pas F = ma (cause). La forme causale est une réinterprétation posthume.


**2.** La masse s'annule de toutes les équations du mouvement. Dynamique = cinématique × m/m = cinématique × 1.


**3.** GM = a³/T² × 4π². La « masse » en kilogrammes est le ratio du ciel divisé par une mesure de laboratoire imprécise (G). Sans G, pas de kilogrammes.


**4.** Le problème des trois corps n'a pas de solution dynamique (Bruns 1887, Poincaré 1890). La dynamique échoue là où la cinématique continue de fonctionner.


**5.** Le géocentrisme et l'héliocentrisme produisent des forces radicalement différentes mais un ciel identique. Les physiciens les plus éminents du XXᵉ siècle — Einstein, Hawking, Born, Mach, Poincaré, Ellis — l'admettent explicitement.


Le choix entre « la Terre tourne » et « le ciel tourne » est un choix de **convention**, pas de physique. C'est un choix de commentaire. Le match — les positions, les angles, les périodes, les éclipses, les rétrogradations — est le même. Comme le dit Bouw dans sa conclusion (2013, p. 747) :


« Nous avons montré que la physique de l'univers géocentrique rend parfaitement compte de ce que nous voyons et mesurons de la rotation quotidienne, que cette rotation soit celle de la Terre dans l'univers ou celle de l'univers autour de la Terre. En dernière analyse, les preuves fondées sur des équations dynamiques ne sont des preuves de rien ; et elles ne sont pas non plus des preuves contre l'univers géocentrique. »
— Gerardus Bouw, Geocentricity (2013), Appendice E, p. 747


## Références


 - Bouw, G.D. (2013). *Geocentricity: Christianity in the Woodshed*, 4ᵉ éd. Chapitre 27, pp. 414-418 ; Appendice E, pp. 740-747.

 - Bruns, H. (1887). « Über die Integrale des Vielkörper-Problems ». *Acta Mathematica*, 11, pp. 25-96.

 - Poincaré, H. (1890). « Sur le problème des trois corps et les équations de la dynamique ». *Acta Mathematica*, 13, pp. 1-270.

 - Kepler, J. (1619). *Harmonices Mundi*.

 - Newton, I. (1687). *Philosophiæ Naturalis Principia Mathematica*.

 - Cavendish, H. (1798). « Experiments to determine the Density of the Earth ». *Phil. Trans. R. Soc.*, 88, pp. 469-526.

 - De Sitter, W. & Brouwer, D. (1938). « On the system of astronomical constants ». *Bull. Astron. Inst. Netherlands*, 8, pp. 213-231.

 - Einstein, A. & Infeld, L. (1938). *L'Évolution de la physique*. Simon & Schuster, p. 212.

 - Hawking, S. & Mlodinow, L. (2010). *The Grand Design*. Bantam Books, p. 39.

 - Born, M. (1965). *Einstein's Theory of Relativity*, 2ᵉ éd. Dover, pp. 276-277.

 - Mach, E. (1883). *Die Mechanik in ihrer Entwickelung*, Chapitre II.

 - Poincaré, H. (1902). *La Science et l'Hypothèse*, Chapitre VII.

 - Ellis, G.F.R. (1995). Cité dans *Scientific American*, 273(4), p. 55.

 - Popov, L. (2013). « Newtonian-Machian analysis of the neo-Tychonian model ». *Eur. J. Phys.*, 34(2), pp. 383-391. arXiv:1301.6045.

 - SpaceAudits / Llamazing (2025-2026). Vault Obsidian : Cosmological Dynamics Null, First Principles Dynamics, Three Body Null, Bouw Celestial Dynamics, GM Kepler Mass Illusion.