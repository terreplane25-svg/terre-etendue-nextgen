# Réseaux de distances — état et feuille de route

Ce dossier contient les réseaux de distances du projet. Un réseau de distances ne
porte **aucune coordonnée et aucune projection** : il ne contient que des distances
entre points, et on cherche quelle figure les satisfait toutes.

## État en un coup d'œil

| | |
|---|---|
| Noyaux clos et verrouillés | **21** — 6 continents, 4 océans |
| **dont discriminants** | **18** (critère corrigé) |
| Points relevés | 130 |
| Distances **calculées** (classe C) | 342 |
| **Mesures de terrain (classe A ou B)** | **0** |
| Modèle plan de référence | verrouillé le 2026-07-27 |
| Cibles pré-enregistrées | 10, prédictions datées, non mesurées |
| Page web | `/carte` |

**Le dossier reste sans aucune donnée expérimentale** — mais il sait maintenant précisément
*où* mesurer, et la réponse n'est pas celle qu'on aurait devinée. Le facteur décisif n'est ni
la qualité du relevé ni l'étendue du noyau : c'est la **latitude**, via le facteur d'étirement
`θ/sin θ` du modèle plan. Deux monuments distants de 1 155 m à Buenos Aires discriminent mieux
qu'une base de 44 km à Reykjavík.

### Prochain jalon — cible n°1, Buenos Aires

```
Axe            Obelisco → Casa Rosada (Plaza de Mayo)
Azimut         115,4°  (est-sud-est, à 34,6° de latitude SUD)
Prédiction WGS84             1 155 m
Prédiction modèle plan       2 794 m
Signal                      +1 639 m,  soit +141,8 %  — un facteur 2,4
Prédictions consignées       2026-07-28, avant toute mesure
Classe exigée                A  (mesure directe de séparation)
```

**1,2 km de base en plein centre-ville, et les deux modèles diffèrent d'un facteur 2,4.**
Deux monuments majeurs, terrain plat et dégagé, quinze minutes de marche. Mesurable au
télémètre laser, voire au décamètre. C'est le meilleur rapport accessibilité / signal de tout
le projet.

Les dix cibles sont dans `cibles-experimentales.json` v2.0 et visibles sur `/carte`.

Trois repères pour situer :

| | Base | Écart entre modèles | Accessibilité |
|---|---|---|---|
| **Signal maximal** — Kerguelen, Mont Ross → Rallier du Baty | 49 861 m | **+274,2 %** | quasi nulle |
| **Meilleur compromis** — Buenos Aires, Obelisco → Casa Rosada | 1 155 m | **+141,8 %** | triviale |
| **Contre-exemple** — Reykjavík, Þingvellir → Grótta | 44 489 m | +3,3 % | facile, mais inutile |

Le contre-exemple est le plus instructif du lot : 44 km d'étendue, un relevé irréprochable,
et un écart de 3,3 % seulement. À 64° N les deux modèles convergent — c'est exactement ce que
prédit `θ/sin θ → 1` au pôle Nord. **Une mesure faite là ne trancherait rien.**

## Fichiers

| Fichier | Version | État | Étendue |
|---|---|---|---|
| `reseau-acores-noyau.json` | 3.0 | **CLOS** — discriminant | 6 points, 593 km |
| `reseau-buenosaires-noyau.json` | 3.0 | **CLOS** — discriminant | 6 points, 44 km |
| `reseau-caire-noyau.json` | 3.0 | **CLOS** | 6 points, 22 km |
| `reseau-hawaii-noyau.json` | 3.0 | **CLOS** — discriminant | 6 points, 72 km |
| `reseau-kerguelen-noyau.json` | 3.0 | **CLOS** — discriminant | 6 points, 134 km |
| `reseau-lecap-noyau.json` | 3.0 | **CLOS** — discriminant | 6 points, 62 km |
| `reseau-maurice-noyau.json` | 3.0 | **CLOS** — discriminant | 6 points, 60 km |
| `reseau-mecque-noyau.json` | 3.0 | **CLOS** | 9 points, 37 km |
| `reseau-medine-noyau.json` | 3.0 | **CLOS** | 7 points, 12 km |
| `reseau-mumbai-noyau.json` | 3.0 | **CLOS** — discriminant | 6 points, 33 km |
| `reseau-newyork-noyau.json` | 3.0 | **CLOS** | 6 points, 11 km |
| `reseau-paques-noyau.json` | 3.0 | **CLOS** — discriminant | 6 points, 26 km |
| `reseau-paris-noyau.json` | 3.0 | **CLOS** | 6 points, 5 km |
| `reseau-pekin-noyau.json` | 3.0 | **CLOS** — discriminant | 6 points, 62 km |
| `reseau-reunion-noyau.json` | 3.0 | **CLOS** — discriminant | 6 points, 51 km |
| `reseau-reykjavik-noyau.json` | 3.0 | **CLOS** — discriminant | 6 points, 78 km |
| `reseau-saopaulo-noyau.json` | 3.0 | **CLOS** | 6 points, 6 km |
| `reseau-sydney-noyau.json` | 3.0 | **CLOS** | 6 points, 2 km |
| `reseau-tahiti-noyau.json` | 3.0 | **CLOS** — discriminant | 6 points, 48 km |
| `reseau-tokyo-noyau.json` | 3.0 | **CLOS** | 6 points, 11 km |
| `reseau-vancouver-noyau.json` | 3.0 | **CLOS** — discriminant | 6 points, 24 km |
| `cibles-experimentales.json` | 2.0 | 10 cibles pré-enregistrées, 0 mesure | mondial |
| `jonction-makkah-madinah.json` | 0.4 | Socle topologique non discriminant | axe de 338 km |
| `reseau-regional-hedjaz.json` | 0.3 | 2 cibles pré-enregistrées, 0 mesure | jusqu'à 1 182 km |
| `reseau-global-terre.json` | 0.6 | Moteur ECEF, 21 noyaux + Point Nemo | intercontinental |
| `reseau-mecque-modele.json` | 1.0 | Archivé (schéma abandonné) | — |

## Les 21 noyaux — classés par pouvoir discriminant réel

> ### ⚠ Correction de critère
>
> Le champ `discriminant` reposait jusqu'ici sur « flèche sphérique > incertitude », qui ne
> mesure que l'**étendue** du noyau. **Ce critère était faux sur 9 des 21 noyaux.** Reykjavík
> (78 km d'étendue, meilleur rapport signal/bruit du lot après les Açores) y passait pour
> discriminant alors que les deux modèles n'y diffèrent que de 3,3 % ; Sydney (2,3 km, pire
> rapport du lot) y passait pour non discriminant alors qu'il offre +158,1 %.
>
> Le bon critère est l'**écart maximal entre les deux modèles** sur les paires du noyau,
> seuil fixé à 10 %. L'ancien champ est conservé sous `etendue_superieure_a_incertitude`.
>
> Bilan de la correction : 7 noyaux déclarés non discriminants le sont (Sydney, São Paulo,
> La Mecque, Médine, Le Caire, Tokyo, New York) et 2 déclarés discriminants ne le sont pas
> (Vancouver, Reykjavík). Le compte passe de 13 à **18 discriminants sur 21**.

| Noyau | Étirement | Écart max | Sphérique | Plan | Étendue | Discriminant |
|---|---|---|---|---|---|---|
| des Kerguelen | 3.734 | **+274.2 %** | 49 861 m | 186 572 m | 134 km | **oui** |
| du Cap | 2.607 | **+159.3 %** | 18 457 m | 47 854 m | 62 km | **oui** |
| de Sydney | 2.603 | **+158.1 %** | 957 m | 2 469 m | 2 km | **oui** |
| de Buenos Aires | 2.642 | **+141.8 %** | 1 155 m | 2 794 m | 44 km | **oui** |
| de l'île de Pâques | 2.298 | **+126.5 %** | 15 018 m | 34 008 m | 26 km | **oui** |
| de São Paulo | 2.162 | **+106.9 %** | 1 611 m | 3 333 m | 6 km | **oui** |
| de La Réunion | 2.071 | **+105.0 %** | 6 568 m | 13 462 m | 51 km | **oui** |
| de Maurice | 2.048 | **+104.7 %** | 37 437 m | 76 628 m | 60 km | **oui** |
| de Tahiti | 1.968 | **+96.4 %** | 7 025 m | 13 793 m | 48 km | **oui** |
| de Mumbai | 1.311 | **+29.3 %** | 10 418 m | 13 472 m | 33 km | **oui** |
| d'Hawaï | 1.287 | **+28.6 %** | 22 569 m | 29 022 m | 72 km | **oui** |
| de La Mecque | 1.286 | **+28.3 %** | 5 754 m | 7 384 m | 37 km | **oui** |
| de Médine | 1.257 | **+25.0 %** | 4 827 m | 6 033 m | 12 km | **oui** |
| du Caire | 1.209 | **+20.8 %** | 3 646 m | 4 404 m | 22 km | **oui** |
| de Tokyo | 1.167 | **+16.1 %** | 4 940 m | 5 734 m | 11 km | **oui** |
| des Açores | 1.153 | **+14.6 %** | 123 550 m | 141 596 m | 593 km | **oui** |
| de Pékin | 1.140 | **+13.8 %** | 10 365 m | 11 799 m | 62 km | **oui** |
| de New York | 1.135 | **+11.6 %** | 944 m | 1 054 m | 11 km | **oui** |
| de Paris | 1.091 | **+8.9 %** | 4 111 m | 4 479 m | 5 km | non |
| de Vancouver | 1.089 | **+8.9 %** | 24 481 m | 26 664 m | 24 km | non |
| de Reykjavík | 1.035 | **+3.3 %** | 44 489 m | 45 945 m | 78 km | non |

**Le tableau est trié par écart décroissant — et il reproduit exactement l'ordre du facteur
d'étirement.** C'est la vérification la plus nette du principe : sur 21 cas indépendants
répartis de 64° N à 49° S, le pouvoir discriminant d'un noyau est déterminé par sa latitude
seule. Ni l'étendue, ni le nombre de points, ni la finesse du relevé n'y changent quoi que ce
soit — la colonne « Étendue » saute de 2 km à 593 km sans perturber l'ordre.

Les trois derniers du classement (Paris, Vancouver, Reykjavík) sont tous à haute latitude
nord, où `θ/sin θ → 1`. Aucune mesure faite là ne peut trancher, quelle que soit sa précision.

### Pouvoir discriminant — correction de méthode

> **La flèche sphérique n'est pas le bon discriminant pour un réseau de distances.**
> Les premières versions de ce README et des fichiers régionaux classaient les paires par
> flèche `s = R(1 − cos(d/R))`. C'est le mauvais critère. La flèche est la *sagitta* :
> l'écart **vertical** entre la corde et l'arc. Elle gouverne les expériences de ligne de
> visée (hauteur cachée, type Bedford), pas les mesures de distance. Un réseau de
> distances mesure des longueurs **le long du sol**, jamais des cordes.

Le vrai signal est l'écart entre la distance géodésique et celle que la **carte plane
candidate** prédit pour la même paire. Sur une azimutale équidistante polaire nord, les
distances le long d'un méridien sont exactes par construction ; celles le long d'un
parallèle sont étirées du facteur `θ/sin θ` (θ = colatitude). À la latitude de La Mecque
(colatitude 68,58°) ce facteur vaut **1,2857**, soit +28,6 %.

**Le discriminant n'est donc pas la longueur de la liaison mais son azimut.** Une paire
est-ouest de 60 km discrimine massivement ; une paire nord-sud de 340 km ne discrimine rien.

| Cible depuis La Mecque | Azimut | Géodésique | Carte plate | Écart | % |
|---|---|---|---|---|---|
| **Djeddah** | 276,2° | 66,1 km | 84,7 km | +18,61 km | **+28,2** |
| **Taïf** | 105,4° | 63,4 km | 80,4 km | +16,97 km | **+26,8** |
| Riyad | 61,1° | 790,6 km | 961,5 km | +170,87 km | +21,6 |
| Dammam | 59,9° | 1 181,8 km | 1 426,6 km | +244,77 km | +20,7 |
| Abha | 141,4° | 452,5 km | 509,1 km | +56,68 km | +12,5 |
| Yanbu | 329,0° | 346,5 km | 374,6 km | +28,11 km | +8,1 |
| Rabigh | 332,1° | 172,9 km | 184,7 km | +11,81 km | +6,8 |
| Tabuk | 337,6° | 838,8 km | 874,8 km | +35,97 km | +4,3 |
| Al-Lith | 162,0° | 148,2 km | 152,9 km | +4,66 km | +3,1 |
| Médine | 356,3° | 337,9 km | 338,3 km | +0,44 km | **+0,1** |

Le classement précédent est presque exactement **inversé**. Djeddah et Taïf, déclarées
« insuffisantes » sur le critère de la flèche, sont les deux meilleures paires. Médine,
déclarée « discriminante ×36 », est la pire : à 356,3° d'azimut elle longe un méridien,
là où les deux modèles coïncident par construction.

Additionner des noyaux ne crée toujours aucun pouvoir discriminant. Mais l'axe à tester
n'est pas Makkah–Madinah : c'est **Makkah–Djeddah**, cinq fois plus court et quarante-deux
fois plus discriminant.

### ⚠ Piège de coïncidence sur Makkah–Djeddah

La route mesure ~84 km. La carte plane prédit 84,7 km pour la **séparation**. Les deux
coïncident presque — et c'est un hasard sans signification : la route serpente et monte,
son excédent sur la corde de 66 km n'a rien à voir avec la géométrie de la Terre.

Un odomètre routier donnant 84 km ne confirme **pas** la carte plane. Sur cet axe la
classe B n'est pas seulement insuffisante, elle est **activement trompeuse**. Seule une
mesure de classe A — séparation en ligne droite — peut trancher.

## Projection d'affichage — UTM 37N (EPSG:32637)

Les 16 points des deux noyaux sont entre 39,54° E et 39,99° E, tous dans la zone 37N
(36° E – 42° E) : aucun raccord de zone à gérer. Facteur d'échelle ponctuel calculé
entre 0,9996376 et 0,9997287, soit un écart à l'unité sous **0,04 %** qui ne *varie*
que de 0,009 % d'un bout à l'autre de la région — un facteur moyen unique suffit.

Attention : ce n'est pas une erreur aléatoire mais un **retrait systématique** de
0,035 % dû à k0 = 0,9996, soit 105 m sur les 338 km de l'axe Makkah–Madinah. Toute
distance lue sur la carte doit être divisée par k pour redevenir une distance terrain.

**Usage : affichage seulement.** Projeter, c'est déjà choisir un modèle de surface ; les
coordonnées UTM dérivent de WGS84 et en héritent. Mesurer une distance sur la carte
projetée pour alimenter un test de géométrie serait de la classe C déguisée.

## Le noyau de La Mecque — clos en v3.0

**Source unique : la table des 9 coordonnées WGS84 du bloc `points`.** Les 36 distances
en sont dérivées par calcul (Vincenty inverse). Aucune distance ne se modifie à la main :
toute évolution passe par une correction de coordonnée suivie d'un recalcul complet.

Graphe complet K9, 84 triangles, 0 violation de l'inégalité triangulaire, RMS
d'ajustement plan 0,2 m. La rigidité n'est pas un résultat obtenu ici mais une
propriété de départ : une matrice de distances complète et cohérente détermine la
figure à une isométrie près, trivialement.

**Ce que le noyau ne peut pas faire.** Sur 37 km d'étendue, l'écart entre un plan et
une sphère de 6 371 km vaut ~30 m, sous l'incertitude de ±250 m liée à la définition
du centre de chaque site. Les deux géométries prédisent la même matrice. Le noyau
valide la cohérence des données, il ne tranche pas la forme — quelle que soit la
qualité du relevé. Cet avertissement est inscrit dans `_meta`.

### Historique et leçon de méthode

Les versions 2.0 à 2.3 reposaient sur des distances **saisies à la main**, corrigées
par lots successifs. Le RMS baissait à chaque lot (587 → 314 → 201 m) et chaque lot
paraissait un progrès.

Le passage en v3.0 a montré que l'écart médian au terrain était de **1 531 m** tout du
long, avec un maximum de 4 629 m — et que le meilleur RMS de la série (201 m)
correspondait à des données fausses de plus d'un kilomètre et demi.

Trois enseignements, conservés parce qu'ils gouvernent tout le reste :

1. **Un RMS faible sur des données mutuellement ajustées ne mesure pas l'exactitude.**
   Il mesure la cohérence interne. Les deux ne sont pas la même chose.
2. **Ne jamais remplacer une mesure par la prédiction du solveur.** Le modèle s'ajuste
   alors forcément mieux : le score ne mesure plus que l'accord du solveur avec
   lui-même. Une valeur qui arrive *après* la prédiction et tombe dessus ne teste rien.
3. **Dans un réseau surdéterminé où plusieurs valeurs sont fausses, la liaison qui
   ressort le plus n'est pas forcément la coupable.** Cas vécu : Kaaba–Jabal an-Nour
   valait 5 100 m, le réseau exigeait ~6 786 m, la valeur a été écartée comme erronée.
   Le calcul WGS84 donne **5 169 m** : elle était juste, et ce sont ses voisines fausses
   qui la poussaient hors de sa place. Les trois valeurs qui l'ont remplacée (6 750,
   6 250, 6 700) étaient toutes fausses de plus de 1,5 km.

Les 28 valeurs saisies des versions 2.x sont conservées en annexe du fichier, avec leur
écart au géodésique, pour traçabilité.

## L'anneau régional du Hedjaz — structure seule

**La méthode du noyau ne se transporte pas.** C'est le seul point où la continuité
serait une faute.

À 37 km, calculer les distances depuis des coordonnées WGS84 était légitime : l'écart
plan/sphère y valait 30 m, sous l'incertitude, donc le choix de formule était sans
conséquence. À 338 km il vaut 8 966 m. Calculer Mecque–Médine par Vincenty revient à
demander à l'ellipsoïde WGS84 quelle distance il prédit ; l'injecter ensuite dans un
ajustement plan mesurerait la distorsion de la projection assumée, pas le terrain.
On aurait testé WGS84 contre WGS84.

Corollaire : toute carte régionale est déjà une projection, donc déjà un modèle. Lire
une distance sur une carte, un SIG ou un service d'itinéraire, c'est lire la sortie du
modèle qu'on voulait tester.

### Classes de source

Chaque liaison doit porter une classe. **Seules A et B ont valeur de test.** C et D
vivent dans un bloc séparé que le solveur ne lit jamais.

| Classe | Nature | Test ? | Exemples |
|---|---|---|---|
| **A** — mesure terrestre directe | séparation | oui | cheminement tachéométrique, EDM en cascade, triangulation optique, base à l'invar |
| **B** — mesure de parcours | trajet | oui | odomètre étalonné, loch, log de vol enregistré |
| **C** — dérivée de coordonnées | référence modèle | **non** | Vincenty/Karney sur WGS84, GNSS, SIG, itinéraire |
| **D** — déclarative | indéterminée | **non** | distance annoncée par une compagnie, un panneau, un article |

La classe B mesure un **trajet**, jamais une séparation : la route serpente, le navire
dérive. Elle donne une borne haute stricte, pas une distance. Ne jamais mélanger A et B
sur une même paire.

### Où la question devient décidable

Flèche sphérique `s = R(1 − cos(d/R))`, R = 6 371 km. Ratio = flèche ÷ 250 m.

| Paire | Distance | Flèche | Ratio | Verdict |
|---|---|---|---|---|
| Mecque – Djeddah | 66 km | 342 m | 1,4 | insuffisant |
| Mecque – Taïf | 63 km | 316 m | 1,3 | insuffisant |
| Mecque – Al-Lith | 148 km | 1 724 m | 6,9 | marginal |
| Mecque – Rabigh | 173 km | 2 345 m | 9,4 | marginal |
| Mecque – Médine | 338 km | 8 966 m | 35,9 | **discriminant** |
| Mecque – Yanbu | 347 km | 9 420 m | 37,7 | **discriminant** |
| Mecque – Abha | 453 km | 16 060 m | 64,2 | **discriminant** |
| Mecque – Riyad | 791 km | 48 997 m | 196 | massif |
| Mecque – Tabuk | 839 km | 55 141 m | 221 | massif |
| Mecque – Dammam | 1 182 km | 109 295 m | 437 | massif |

Contre-intuitif : Djeddah et Taïf, les deux voisines évidentes, sont **inutiles** pour
trancher — à 65 km le signal est du même ordre que le bruit. Le seuil utile commence
vers 150 km et devient franc à 300 km. La première liaison à viser est Mecque–Médine
ou Mecque–Yanbu.

Ces distances sont elles-mêmes de classe C : elles dimensionnent l'expérience, elles ne
la conduisent pas.

### Pourquoi le fichier est vide

11 points déclarés, 0 liaison, délibérément. Rien n'a été prérempli en classe C, même
étiqueté comme tel : la leçon des versions 2.x est qu'une valeur présente dans un
fichier finit par être utilisée. La seule protection est l'absence de donnée non
qualifiée.

Prochain jalon : **une** liaison de classe A ou B, sur une paire dont la flèche dépasse
largement l'incertitude de la méthode employée. Sans cela, ajouter des points ne fait
qu'agrandir un graphe vide.

## Règles permanentes

- Aucune distance sans classe de source explicite et référence vérifiable.
- Le solveur ne consomme que les classes A et B.
- Ne jamais mélanger `separation` et `trajet` sur une même paire.
- Rigidité : pour N points, minimum 2N−3 liaisons, toutes valences ≥ 3, graphe
  3-connexe. Un réseau en étoile depuis un moyeu n'est **jamais** rigide.
- Consigner la prédiction du réseau **avant** réception d'une mesure. C'est le seul
  test réel.
- L'incertitude ne se transporte pas d'une échelle à l'autre : elle s'estime liaison
  par liaison, selon la méthode employée.

## Modèle plan de référence — VERROUILLÉ le 2026-07-27

```
Azimutale équidistante polaire nord, métrique euclidienne du plan,
rayon calibré sur l'arc de méridien WGS84 depuis le pôle Nord.

r = arc_méridien(pôle → latitude)
angle = longitude
d = √(r₁² + r₂² − 2·r₁·r₂·cos Δλ)
```

C'est le seul candidat qui soit une **hypothèse** et non une représentation. Les
projections de l'ellipsoïde restituent WGS84 et ne peuvent donc pas lui servir
d'alternative :

| Candidat écarté | Prédiction Makkah–Madinah | Écart WGS84 |
|---|---|---|
| Azimutale équidistante centrée sur Makkah | 337 903 m | **0 m** — exact par construction |
| Plan tangent gnomonique | 339 594 m | +1 691 m |
| Plan tangent stéréographique | 339 353 m | +1 450 m |
| Plan tangent orthographique | 339 113 m | +1 210 m |
| UTM 37N euclidien direct | 337 791 m | −112 m (= le k0, corrigible) |
| *(arc sphérique R·σ, pour repère)* | *339 273 m* | *+1 370 m* |

L'essentiel de l'écart des plans tangents n'est pas un effet de projection mais l'écart
sphère/ellipsoïde : l'arc sphérique vaut déjà +1 370 m. Un plan tangent *approche* la
sphère, il n'en est pas une alternative.

Le calibrage retenu est **délibérément favorable au modèle plan** : caler le rayon sur
l'arc de méridien WGS84 rend ses distances nord-sud exactes. Un échec ne pourra pas être
imputé au calibrage.

## Cibles expérimentales pré-enregistrées

Prédictions consignées le **2026-07-27, avant toute mesure**. Elles ne doivent plus être
recalculées après réception d'une mesure.

| # | Axe | Azimut | WGS84 | Carte plane | Écart | Classe admise |
|---|---|---|---|---|---|---|
| **1** | Kaaba → Djeddah (Masjid al-Juffali) | 276,2° | 66 054 m | 84 660 m | **+18 605 m (28,2 %)** | **A seule** |
| 2 | Kaaba → Taïf (centre) | 105,4° | 63 441 m | 80 414 m | +16 973 m (26,8 %) | A ou B |
| — | Kaaba → Al-Masjid an-Nabawi | 356,3° | 337 903 m | 338 344 m | +441 m (0,1 %) | *non discriminant* |

### ⚠ Sensibilité au point de référence

« Makkah–Djeddah » n'est pas une paire : Djeddah s'étend sur une vingtaine de kilomètres.

| Point retenu | Azimut | WGS84 | Carte plane | Écart |
|---|---|---|---|---|
| Masjid al-Juffali (centre historique) | 276,2° | 66,05 km | 84,66 km | +28,2 % |
| Corniche ouest | 279,7° | 71,59 km | 91,44 km | +27,7 % |
| Aéroport King Abdulaziz | 292,6° | 74,98 km | 93,48 km | +24,7 % |
| Périphérie est | 269,8° | 56,63 km | 72,75 km | +28,5 % |
| Port islamique | 272,6° | 70,16 km | 90,10 km | +28,4 % |

La distance WGS84 varie de **18,4 km** selon le point — du même ordre que le signal de
18,6 km. Ce qui sauve le test : l'écart **relatif** reste à 25–28 % partout. Le signal est
proportionnel, pas absolu.

**Exigence :** toute mesure de classe A doit nommer ses deux bornes physiques, et la
prédiction être recalculée sur *ces* bornes — jamais sur un centre-ville nominal.

## Réseau global — moteur ECEF 3D

### ⚠ ECEF n'est pas un repère neutre

Passer en ECEF (X, Y, Z géocentriques) n'évite pas le problème des projections planes : il
le remplace par l'adoption **silencieuse** d'une des deux hypothèses.

ECEF se calcule depuis (φ, λ, h) et le rayon de courbure `N = a/√(1−e²sin²φ)` **de
l'ellipsoïde WGS84**. Le résultat est l'ellipsoïde WGS84 en cartésien. Ce n'est pas un
repère indépendant du modèle : c'est le modèle.

Et le modèle plan de référence du projet — azimutale équidistante polaire nord — est une
géométrie à **deux** dimensions. Il n'a pas de Z et ne peut pas s'exprimer en ECEF. Passer
en ECEF ne met donc pas les deux hypothèses à égalité : cela retire l'une des deux du cadre.

**Conséquence :** un réseau ECEF ne peut produire aucune tension. Toute matrice de cordes
dérivée de coordonnées XYZ est exactement plongeable dans ℝ³ — le résidu est nul pour
*n'importe quel* jeu de coordonnées. Ce n'est pas une validation, c'est une identité. Ne
jamais rapporter ce résidu comme un résultat.

Ce qu'ECEF apporte réellement : un bookkeeping commode (coordonnées additives, distance
par simple norme, pas de zones, pas de facteur d'échelle). C'est un outil de calcul et
d'affichage 3D, légitime comme tel.

### ⚠ Une corde 3D n'est pas mesurable

La corde ECEF traverse l'intérieur du globe. Aucun instrument terrestre, maritime ou aérien
ne peut la mesurer. Ces valeurs sont donc de **classe C définitive**, sans échéance de
qualification — contrairement aux cibles du Hedjaz, qui attendent une mesure possible.

Seule la distance **le long de la surface** est accessible à la mesure. C'est elle, et non
la corde, qui doit porter tout test de géométrie.

| Paire de centres | Corde 3D | Géodésique | Écart |
|---|---|---|---|
| Kaaba – Al-Masjid an-Nabawi | 337 863,2 m | 337 903,1 m | −39,9 m (−0,012 %) |
| Kaaba – Khéops | 1 285 067,3 m | 1 287 261,1 m | −2 193,8 m (−0,170 %) |
| Al-Masjid an-Nabawi – Khéops | 1 036 592,3 m | 1 037 739,2 m | −1 146,9 m (−0,111 %) |

La corde est toujours **plus courte** que la géodésique, puisqu'elle coupe au travers. Un
écart positif signalerait une erreur de code.

### Les trois noyaux, et ce qu'ils ne font pas

| Noyau | Points | Étendue | Flèche | Incertitude | Signal/bruit | Discriminant |
|---|---|---|---|---|---|---|
| Sydney | 6 | 2 320 m | 0,42 m | ±25 m | 1/59,2 | non |
| Médine | 7 | 11 985 m | 11,3 m | ±250 m | 1/22,1 | non |
| Paris | 6 | 5 194 m | 2,12 m | ±25 m | 1/11,8 | non |
| São Paulo | 6 | 5 907 m | 2,74 m | ±25 m | 1/9,1 | non |
| La Mecque | 9 | 37 095 m | 30,0 m | ±250 m | 1/8,3 | non |
| Le Caire | 6 | 22 090 m | 38,3 m | ±250 m | 1/6,5 | non |
| Tokyo | 6 | 10 752 m | 9,07 m | ±25 m | 1/2,8 | non |
| New York | 6 | 11 288 m | 10,0 m | ±25 m | 1/2,5 | non |

Le meilleur rapport des huit — New York, 1/2,5 — reste **sous l'unité** : dans les huit cas,
l'écart entre plan et sphère est plus petit que l'incertitude sur la position des points.

**Le classement suit exactement l'étendue**, pas la qualité du relevé ni le nombre de points.
C'est la confirmation empirique que le facteur limitant est l'échelle et rien d'autre : le
plus resserré (Sydney, 2 320 m) est le pire (1/59,2), le plus étendu à incertitude fine
(New York) est le meilleur.

La cause est une loi, pas une contingence : **s ≈ d²/(2R)**, la flèche croît comme le carré
de l'étendue. Pour atteindre un rapport de 1 à ±25 m il faudrait une étendue de ~18 km ; pour
un rapport de 10, ~57 km. Aucun bassin urbain ne s'y prête, et un relevé plus fin ne
changerait pas l'ordre de grandeur. **Ajouter un neuvième noyau donnerait le même résultat.**

52 points, 147 distances calculées, **0 mesure de terrain** dans tout le projet. La cible
reste unique : Kaaba → Djeddah, 66 km, 28,2 % d'écart entre modèles, classe A exigée.

### Les 28 cordes 3D — et pourquoi l'écart explose

Extraits du graphe complet K8, trié par distance croissante :

| Paire de centres | Corde 3D | Géodésique | Écart | % |
|---|---|---|---|---|
| Kaaba – Nabawi | 337 863 m | 337 903 m | −40 m | −0,012 |
| Nabawi – Khéops | 1 036 592 m | 1 037 739 m | −1 147 m | −0,111 |
| Khéops – Notre-Dame | 3 177 577 m | 3 211 416 m | −33 839 m | −1,054 |
| Kaaba – Notre-Dame | 4 404 204 m | 4 496 942 m | −92 737 m | −2,062 |
| Notre-Dame – Empire State | 5 647 069 m | 5 849 203 m | −202 134 m | −3,456 |
| Kaaba – Empire State | 9 232 813 m | 10 320 377 m | −1 087 564 m | −10,538 |
| Khéops – Opéra de Sydney | 11 532 059 m | 14 422 884 m | −2 890 825 m | −20,043 |
| Empire State – Opéra de Sydney | 12 107 113 m | 15 988 923 m | −3 881 810 m | −24,278 |
| Notre-Dame – Opéra de Sydney | 12 371 964 m | 16 957 341 m | −4 585 377 m | −27,041 |
| **Tour de Tokyo – Cathédrale de la Sé** | 12 660 221 m | 18 531 582 m | **−5 871 361 m** | **−31,683** |

Les 28 écarts sont négatifs : la corde coupe au travers du globe, elle est toujours plus
courte. Contrôle de cohérence du moteur validé sur l'ensemble du graphe.

La loi : pour un angle au centre σ, `corde = 2R·sin(σ/2)` et `géodésique ≈ R·σ`. Le rapport
vaut `sin(σ/2)/(σ/2)` — il tend vers 1 aux courtes distances et vers **2/π ≈ 0,6366** à
l'antipode, soit −36,3 % au maximum. Les −31,7 % de Tokyo – São Paulo en sont proches : ces
deux villes sont presque antipodales.

Confondre corde et géodésique n'est donc pas une erreur d'arrondi : c'est une erreur pouvant
atteindre **le tiers de la distance**. Ces deux colonnes ne doivent jamais entrer dans le même
solveur ni dans la même comparaison.

## Phase 3.3 — ce qui a déplacé la cible

Les trois noyaux insulaires ne sont pas des bassins urbains : Tahiti fait 48 km d'étendue,
La Réunion 51 km, les Açores **593 km**. Tous trois franchissent le seuil discriminant.

| Noyau | Étendue | Flèche | Incertitude | Signal/bruit | Discriminant |
|---|---|---|---|---|---|
| Tahiti | 48 330 m | 183,3 m | ±25 m | **7,3 / 1** | oui |
| La Réunion | 51 300 m | 206,5 m | ±25 m | **8,3 / 1** | oui |
| Açores | 593 163 m | 27 592,8 m | ±25 m | **1 104 / 1** | oui |

### Le facteur austral

Le vrai levier n'est pas seulement l'étendue : c'est la **latitude**. Sur l'azimutale
équidistante polaire nord, une paire est-ouest est multipliée par `θ/sin θ` (θ = colatitude),
et ce facteur explose vers le sud.

| Lieu | Latitude | Colatitude | Facteur | Étirement |
|---|---|---|---|---|
| Flores, Açores | 39,45° N | 50,55° | 1,1426 | +14,3 % |
| La Mecque | 21,42° N | 68,58° | 1,2858 | +28,6 % |
| Tahiti | 17,50° S | 107,50° | 1,9673 | **+96,7 %** |
| La Réunion | 21,10° S | 111,10° | 2,0784 | **+107,8 %** |
| Sydney | 33,86° S | 123,86° | 2,6033 | +160,3 % |
| Point Nemo | 48,88° S | 138,88° | 3,6858 | +268,6 % |

**Une base est-ouest de 6 km dans l'hémisphère sud discrimine mieux qu'une base de 66 km dans
l'hémisphère nord.** C'est ce qui fait passer La Réunion devant Djeddah.

Coïncidence défavorable, et pas fortuite : la divergence croît vers le sud, là où les terres
émergées se raréfient. Le Point Nemo, où le facteur atteint 3,686, est le point le plus éloigné
de toute terre — inscrit comme repère de couverture, sans noyau : il n'y a rien à y mesurer.

### Les cinq cibles pré-enregistrées

| # | Axe | Azimut | Sphérique | Plan | Écart |
|---|---|---|---|---|---|
| **1** | Saint-Denis → Roland-Garros (La Réunion) | 98,1° | 6 568 m | 13 462 m | **+105,0 %** |
| 2 | Mont Orohena → Marae Arahurahu (Tahiti) | 267,2° | 7 025 m | 13 793 m | +96,4 % |
| 3 | Cathédrale de Papeete → Aéroport de Faaa | 245,4° | 5 187 m | 9 512 m | +83,4 % |
| 4 | Angra do Heroísmo → Horta (Açores) | 264,3° | 123 550 m | 141 596 m | +14,6 % |
| 5 | Kaaba → Djeddah | 276,2° | 66 054 m | 84 660 m | +28,2 % |

La cible n°4 est la seule mesurable **sans se déplacer à terre** : liaison inter-îles, donc
qualifiable en classe B (loch, log de vol) et potentiellement en classe A (câbles sous-marins).

> **Rappel indispensable.** Ces 192 distances restent de **classe C** — calculées depuis des
> coordonnées WGS84, donc circulaires. Qu'un noyau soit géométriquement discriminant ne le rend
> pas probant : cela indique seulement qu'une *mesure* de classe A ou B faite là aurait valeur
> de test. Le dépôt dit où mesurer. Il ne mesure pas.

## Page web — `/carte`

`src/app/carte/` + `src/lib/reseau.ts`. Lit directement les JSON de ce dossier, sans duplication
de données. SVG inline, **aucune dépendance externe et aucune tuile distante** : bascule entre
la projection équirectangulaire (WGS84) et l'azimutale équidistante polaire nord — c'est-à-dire
entre les deux hypothèses, l'une à côté de l'autre.

Ce choix est délibéré. Une carte Leaflet ou MapLibre affiche ses tuiles en Web Mercator, une
projection de l'ellipsoïde WGS84 : le fond de carte trancherait visuellement la question avant
même qu'on la pose. Ici les deux projections sont dessinées à égalité, sur une grille nue.
