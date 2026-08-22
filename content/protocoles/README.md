# Protocoles de terrain

Sources des protocoles expérimentaux diffusables. Ce sont des documents destinés
à être remis à des observateurs extérieurs — ils énoncent leurs prédictions
**avant** toute acquisition et disent à l'avance ce que signifie chaque issue.

## Ce qui se trouve ici

| Fichier | Contenu |
|---|---|
| `horizon-fr.html` | Dépression de l'horizon marin — français, 11 pages, v1.1 |
| `horizon-en.html` | Même document en anglais, v1.1 |
| `soleil-bilingue.html` | Diamètre angulaire du Soleil — bilingue, 21 pages, v1.2 |
| `pole-celeste-bilingue.html` | Hauteur du pôle céleste — bilingue, 18 pages, v1.1 |
| `horizon-artefact-web.html` | Version web du protocole d'horizon (artefact consultable en ligne) |
| `polices.css` | Spectral, IBM Plex Sans, IBM Plex Mono en base64 |

## Reconstruire les PDF

```bash
pip install playwright pymupdf
python3 scripts/rendre-protocoles.py            # les quatre
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

## Les trois protocoles

### Dépression de l'horizon

L'angle entre l'horizontale vraie et la ligne d'horizon marin. Une sphère prédit
`δ = √(2h/R′)`, un plan prédit `δ = 0` à toute altitude.

Son intérêt tient à ce que la réfraction n'y intervient qu'au second ordre : sur
toute la plage défendable (0 ≤ k ≤ 0,47) la prédiction sphérique ne varie que de
107′ à 78′ depuis 3 107 m. **L'écart entre les modèles vaut au minimum 78′ pour
un budget d'erreur de 2,2′** — rapport signal sur bruit d'environ 36. C'est la
première mesure du dossier où l'incertitude sur la réfraction est plus petite que
l'écart à mesurer.

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

## Historique des versions

Les corrections sont consignées dans les documents eux-mêmes, en pied de page et
dans des encadrés à l'endroit concerné. Elles ne sont pas effacées : un relecteur
les trouverait de toute façon.

- **Soleil 1.1** — le domaine de validité est énoncé en section 02. La 1.0
  opposait « modèle plan » et « modèle sphérique », attribuant ainsi à toute une
  famille de modèles une prédiction que seuls certains formulent. Un modèle où le
  disque visible est une projection n'est pas contraint par la loi en sin α, et
  le document le dit désormais.
- **Horizon 1.1** — la méthode à horizon artificiel devient le procédé de
  référence. Le référentiel d'altitude est imposé : la 1.0 écrivait « altitude du
  sol » sans le préciser, ce qui fausse δ de 178 % à 10 m pour une erreur de 30 m.
  La marée et l'état de la mer, absents, deviennent des champs obligatoires. La
  méthode différentielle est restreinte aux cas où le montage n'est pas défait
  entre les stations, son hypothèse d'annulation du biais étant sinon intenable.
  Les rapports signal sur bruit par altitude sont affichés — sous 50 m ils tombent
  sous 6 et ces points ne sont pas décisifs.
- **Pôle 1.1** — le test 2 est entièrement réécrit. Il se disait « sans paramètre
  libre » et annonçait 156 à 200 km de base : les deux affirmations tiraient la
  prédiction azimutale de la latitude, laquelle vient du GPS — donc du modèle
  testé — ou de la hauteur du pôle elle-même. En distances au sol le modèle plan a
  deux paramètres et imite une droite à 0,03° près sur 200 km ; il faut 1 500 km
  et quatre stations, ou épingler `r₀` par une mesure est-ouest. Le test 3 est
  réexprimé en distance au sol pour la même raison, et le test 1 restreint aux
  cartes à centre unique.
- **Soleil 1.2** — la section 04 est réécrite. Elle annonçait des valeurs à
  retrouver (14,1 %, 1,67 %) qui ne sont atteignables ni un mois quelconque ni
  depuis les latitudes moyennes, et passait sous silence la mesure d'un disque en
  phase, la dérive orbitale et la distinction géocentrique/topocentrique.

## Ce que ces protocoles ne font pas

Ils ne concluent pas sur la forme de la Terre. Chacun mesure une grandeur
précise et écarte une famille de modèles ; aucun ne prétend trancher davantage.
Le protocole solaire mesure une **distance**, pas une forme.

Les valeurs numériques se recalculent toutes depuis `scripts/rendre-protocoles.py`
et les formules citées en pied de chaque document.
