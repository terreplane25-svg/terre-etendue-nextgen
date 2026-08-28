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
| `soleil-bilingue.html` | Diamètre angulaire du Soleil — bilingue, 21 pages, **v1.4** |
| `ballon-bilingue.html` | Dépression de l'horizon depuis un ballon stratosphérique — bilingue, 29 pages, **v1.1** |
| `pole-celeste-bilingue.html` | Hauteur du pôle céleste — bilingue, 20 pages, **v1.3** |
| `horizon-artefact-web.html` | Version web du protocole d'horizon (artefact consultable en ligne) |
| `polices.css` | Spectral, IBM Plex Sans, IBM Plex Mono en base64 |

## Reconstruire les PDF

```bash
pip install playwright pymupdf
python3 scripts/rendre-protocoles.py            # les cinq documents
python3 scripts/rendre-protocoles.py soleil     # un seul
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

## Les quatre protocoles

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

### Diamètre angulaire du Soleil

Toute source compacte à hauteur finie implique `θ(α)/θ(90°) = sin α`, sans
dépendre de la hauteur retenue. À 20° d'élévation l'écart entre les deux modèles
atteint 66 % du diamètre, pour une précision requise de 1 %. Rapport signal sur
bruit d'environ 150.

L'observable est le **diamètre horizontal** : la réfraction aplatit le disque
verticalement près de l'horizon, jusqu'à 17 %, mais ne l'affecte pas
latéralement.

Deux contrôles préalables sur la Lune qualifient la chaîne avant qu'elle serve —
étalonnage en distance sur un mois lunaire, puis parallaxe diurne. Le second
discrimine par lui-même, les deux modèles y prédisant des variations de signe
opposé.

### Hauteur du pôle céleste

Trois tests d'exigence croissante. Le premier ne mesure **aucun angle** : une pose
longue depuis un site austral montre un centre de rotation au **sud**, à une
hauteur égale à la latitude, là où le modèle azimutal — dépourvu de pôle austral —
place son unique centre au **nord**. Les deux prédictions désignent des moitiés
opposées du ciel, et aucune valeur de H ne déplace un centre du nord vers le sud.

Le deuxième porte sur la **pente locale**, mesurée en distance au sol pour éviter
toute circularité. Deux voies : soit `r₀` est épinglé par une mesure est-ouest, et
une seule paire de stations suffit sous 61,4° de latitude — aucune valeur de H
n'y produit une pente de 1,000 ; soit on n'emploie que des distances nord-sud, et
il faut alors **1 500 km de base et quatre stations**, le modèle plan à deux
paramètres imitant une droite à 0,03° près sur 200 km.

Le troisième confronte l'ensemble des stations à la droite, également en distance
au sol : le meilleur ajustement azimutal laisse un résidu qui change de signe et
atteint 12,3° sur 5 000 km.

La méthode évite le piège de circularité qui guette ici — on ne peut pas rapporter
une hauteur à l'horizon visible, dont la dépression dépend du modèle testé. La
référence est le fil à plomb, matérialisé par un **horizon artificiel** : une
nappe d'eau immobile, où l'angle entre l'astre et son reflet vaut exactement deux
fois la hauteur. Aucun étalonnage.

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
