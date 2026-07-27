# Réseaux de distances — état et feuille de route

Ce dossier contient les réseaux de distances du projet. Un réseau de distances ne
porte **aucune coordonnée et aucune projection** : il ne contient que des distances
entre points, et on cherche quelle figure les satisfait toutes.

## Fichiers

| Fichier | Version | État | Étendue |
|---|---|---|---|
| `reseau-mecque-noyau.json` | 3.0 | **CLOS — verrouillé** | 9 points, 37 km |
| `reseau-medine-noyau.json` | 3.0 | **CLOS — verrouillé** | 7 points, 12 km |
| `jonction-makkah-madinah.json` | 0.4 | Socle topologique non discriminant | axe de 338 km |
| `reseau-regional-hedjaz.json` | 0.3 | 2 cibles pré-enregistrées, 0 mesure | 11 points, jusqu'à 1 182 km |
| `reseau-mecque-modele.json` | 1.0 | Archivé (schéma abandonné) | — |

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
