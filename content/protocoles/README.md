# Protocoles de terrain

Sources des protocoles expérimentaux diffusables. Ce sont des documents destinés
à être remis à des observateurs extérieurs — ils énoncent leurs prédictions
**avant** toute acquisition et disent à l'avance ce que signifie chaque issue.

## Ce qui se trouve ici

| Fichier | Contenu |
|---|---|
| `horizon-fr.html` | Dépression de l'horizon marin — français, 22 pages, **v1.9** |
| `horizon-en.html` | Même document en anglais, 22 pages, **v1.9** |
| `depot/` | Le dépôt : marche à suivre, métadonnées, et les fichiers figés une fois le DOI inscrit |
| `soleil-bilingue.html` | Diamètre angulaire du Soleil — **SUSPENDU**, voir plus bas |
| `ballon-bilingue.html` | Dépression de l'horizon depuis un ballon stratosphérique — bilingue, 29 pages, **v1.1** |
| `mire-bilingue.html` | Hauteur masquée d'une mire graduée — bilingue, 24 pages, **v1.0** |
| `pole-celeste-bilingue.html` | Hauteur du pôle céleste — **SUSPENDU**, voir plus bas |
| `horizon-artefact-web.html` | Version web du protocole d'horizon (artefact consultable en ligne) |
| `polices.css` | Spectral, IBM Plex Sans, IBM Plex Mono en base64 |

## Reconstruire les PDF

```bash
pip install playwright pymupdf
python3 scripts/rendre-protocoles.py            # les protocoles actifs
python3 scripts/rendre-protocoles.py soleil     # y compris un suspendu
```

Les PDF sortent dans `content/protocoles/pdf/`. **Ils ne sont pas versionnés** :
le `.gitignore` du projet exclut `*.pdf`, et ils se régénèrent en quelques
secondes depuis ces sources. Rien n'est perdu à ne pas les commiter.

## Pourquoi les polices sont intégrées

La politique réseau de l'environnement de travail bloque `fonts.googleapis.com`.
Un premier rendu est sorti en Liberation et DejaVu **sans le signaler** — le
document paraissait correct et ne l'était pas. Les polices sont donc embarquées
en base64, récupérées depuis npm (`@fontsource/*`, licence SIL OFL).

Elles sont factorisées dans `polices.css` plutôt que dupliquées dans chaque
source : le bloc pèse 290 ko et il y a quatre documents. Le script les injecte au
rendu à la place du repère `@@POLICES@@`.

## Les protocoles actifs

### Dépression de l'horizon

L'angle entre l'horizontale vraie et la ligne d'horizon marin. Une sphère prédit
`δ = √(2h/R′)`, un plan prédit `δ = 0` à toute altitude.

Son intérêt tient à ce que la réfraction n'y intervient qu'au second ordre : sur
toute la plage défendable (0 ≤ k ≤ 0,47) la prédiction sphérique ne varie que de
107′ à 78′ depuis 3 107 m. **L'écart entre les modèles vaut au minimum 78′ pour
un budget d'erreur instrumental de 2,2′** — rapport signal sur bruit d'environ
36 contre l'hypothèse plane, et de 29 sur la détermination du coefficient a, où
l'incertitude de réfraction entre pleinement. C'est la première mesure du dossier
où l'incertitude sur la réfraction est plus petite que l'écart à mesurer.

La mesure se fait par **horizon artificiel** : une étoile, son reflet dans une
nappe d'eau et la ligne d'horizon marin dans une même image. Le milieu entre
l'étoile et son reflet matérialise l'horizontale vraie, sans aucune mise de
niveau. La mise de niveau avec retournement du boîtier reste en solution de
repli.

### Dépression de l'horizon depuis un ballon stratosphérique

La même grandeur que le protocole d'horizon, mais mesurée depuis 2 à 30 km. δ y
vaut 2,1° à 5 km et 5,4° à 30 km, contre 1,8° depuis le meilleur sommet
accessible.

**L'observable est l'angle entre deux points diamétralement opposés de
l'horizon**, vus dans une seule image : 180° − 2δ sur une sphère, 180° sur un
plan. Une inclinaison de la nacelle ajoute ε d'un côté et le retranche de
l'autre — la somme est invariante. Aucune référence verticale n'est donc
nécessaire à bord, ce qui rend la mesure possible sur une nacelle qui balance.

Le montage est **une seule caméra devant un dièdre de deux miroirs**. Le point
n'est pas l'économie : deux boîtiers séparés exigeraient une synchronisation au
millième de seconde, faute de quoi le balancement — jusqu'à 5°/s — injecte 30′
d'erreur pour 100 ms de décalage. Un capteur unique supprime le problème par
construction.

**La réfraction cesse d'être supposée.** L'invariant de Bouguer donne
`cos δ = n₀(R+t)/n₁(R+h)` : la correction ne dépend que de l'indice aux deux
extrémités du rayon, donc de P et T au sol et à bord — quatre grandeurs
*mesurées*. Aucun coefficient k n'apparaît dans ce protocole. La correction vaut
−9′ à −12′ sur toute la plage 5–35 km.

Le critère de décision est une **variation**, non une valeur : entre 2 et 30 km,
2δ change de **488′** sur une sphère et de **zéro** sur un plan. Le décalage
instrumental disparaît dans la différence. Rapport signal sur bruit **317 sur
deux images**, et l'ajustement de la montée entière restitue R à environ 1 % —
plancher fixé par le relief, corrigeable par modèle numérique de terrain.

### Hauteur masquée d'une mire graduée

Une mire de douze mètres, bandes alternées d'un mètre, plantée au bord de l'eau,
base au niveau de la surface. Observée depuis l'autre rive à 20 km, depuis cinq
hauteurs d'œil. **On compte les bandes masquées.**

Sa particularité : **aucune mesure d'angle**. La mire porte sa propre échelle
métrique. Ni focale à étalonner, ni distorsion à corriger, ni horizontale à
matérialiser, ni mise à niveau — trois postes d'erreur qui pèsent lourd ailleurs
disparaissent. C'est la mesure la plus directe du dossier.

Son prix est énoncé en section 02 plutôt que découvert à la réduction. La
hauteur masquée ne dépend de R et de k que par leur combinaison
`R′ = R/(1−k)` : **aucune mesure d'occultation ne peut les séparer.** Elle
restitue R′, compatible avec un facteur 1,89 de valeurs de R. Une méthode B
facultative — visées zénithales réciproques simultanées — lève la
dégénérescence en *mesurant* k : la somme des deux angles excède 180° de
`(d/R)(1−k)`, soit 9,39′ sur une base de 20 km, ce qu'un théodolite à 5″ résout
à σ(k) = 0,011.

Le critère de discrimination prend le k le plus favorable au modèle plan. À
20 km depuis un œil à 5 m, la sphère garantit **3,40 m masqués** même en régime
de conduit atmosphérique, pour un budget de 0,55 m — rapport 6,2. Le plan prédit
zéro, sous propagation rectiligne comme sous réfraction réelle.

Son mode d'échec propre est l'**extinction atmosphérique** : une visée de 20 km
exige 35 km de visibilité météorologique, une visée de 25 km en exige 45. Une
mire noyée dans la brume n'est pas une mire masquée par la courbure, et le
protocole donne le critère qui les distingue.

## Les protocoles suspendus

`soleil-bilingue.html` et `pole-celeste-bilingue.html` sont **gelés**. Leurs
sources restent dans le dépôt, le script de rendu les ignore par défaut, et
aucun PDF n'en est produit.

La raison n'est pas un défaut trouvé dans les documents : c'est que leur auteur
n'avait pas transmis tout ce qu'il sait de ces deux expériences au moment où
elles ont été écrites. Un protocole incomplet qui a l'air fini est plus
dangereux qu'un protocole absent — il se diffuse, il se dépose, et l'erreur
voyage avec un DOI.

Ils reprendront quand les informations manquantes seront là. D'ici là, ils ne
doivent être ni diffusés, ni déposés, ni cités.

## Ce que ces documents sont, et ne sont pas

Ce sont des **protocoles**, et rien d'autre. Ils décrivent une mesure à faire :
l'observable, la prédiction de chaque modèle, le matériel, l'ordre des
opérations, le budget d'erreur, les critères de décision posés d'avance, et les
données à transmettre.

Ils ne discutent aucune expérience antérieure, ne citent aucun travail d'autrui
pour s'en réclamer ou le critiquer, et ne situent pas la question dans son
histoire. Ce débat existe, il est légitime, et il a sa place ailleurs — pas dans
le document qu'on remet à quelqu'un pour qu'il fasse la mesure lui-même.

Les seules références conservées sont celles qui **fondent une formule
employée** : indice de réfraction de l'air, réfraction géodésique, atmosphère
standard. Un protocole doit dire d'où viennent ses constantes.

Les versions se suivent, mais le journal des révisions ne figure plus dans les
documents : il vit dans l'historique des sources, et se fournit sur demande.

## Ce que ces protocoles ne font pas

Ils ne concluent pas sur la forme de la Terre. Chacun mesure une grandeur
précise et écarte une famille de modèles ; aucun ne prétend trancher davantage.
Le protocole solaire mesure une **distance**, pas une forme.

Les valeurs numériques se recalculent toutes depuis `scripts/rendre-protocoles.py`
et les formules citées en pied de chaque document.
