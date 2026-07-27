# Réseaux de distances — état et feuille de route

Ce dossier contient les réseaux de distances du projet. Un réseau de distances ne
porte **aucune coordonnée et aucune projection** : il ne contient que des distances
entre points, et on cherche quelle figure les satisfait toutes.

## Fichiers

| Fichier | Version | État | Étendue |
|---|---|---|---|
| `reseau-mecque-noyau.json` | 3.0 | **CLOS — verrouillé** | 9 points, 37 km |
| `reseau-medine-noyau.json` | 3.0 | **CLOS — verrouillé** | 7 points, 12 km |
| `jonction-makkah-madinah.json` | 0.1 | Structure seule, 0 mesure | axe de 338 km |
| `reseau-regional-hedjaz.json` | 0.1 | Structure seule, 0 liaison | 11 points, jusqu'à 1 182 km |
| `reseau-mecque-modele.json` | 1.0 | Archivé (schéma abandonné) | — |

### Pouvoir discriminant des trois réseaux

| Réseau | Étendue | Flèche sphérique | Incertitude | Verdict |
|---|---|---|---|---|
| Noyau Médine | 12 km | 11 m | ±250 m | non discriminant |
| Noyau La Mecque | 37 km | 30 m | ±250 m | non discriminant |
| Jonction Makkah–Madinah | 338 km | 8 959 m | ±250 m | **discriminant (×36)** |

Additionner des noyaux ne crée pas de pouvoir discriminant : deux réseaux non
discriminants restent non discriminants. C'est la **jonction** qui porte l'enjeu, et
elle exige une mesure de classe A ou B — la méthode des noyaux (coordonnées WGS84 +
Vincenty) y devient circulaire.

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
