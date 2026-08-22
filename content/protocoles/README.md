# Protocoles de terrain

Sources des protocoles expérimentaux diffusables. Ce sont des documents destinés
à être remis à des observateurs extérieurs — ils énoncent leurs prédictions
**avant** toute acquisition et disent à l'avance ce que signifie chaque issue.

## Ce qui se trouve ici

| Fichier | Contenu |
|---|---|
| `horizon-fr.html` | Dépression de l'horizon marin — français, 7 pages |
| `horizon-en.html` | Même document en anglais |
| `soleil-bilingue.html` | Diamètre angulaire du Soleil — bilingue, 21 pages, v1.2 |
| `horizon-artefact-web.html` | Version web du protocole d'horizon (artefact consultable en ligne) |
| `polices.css` | Spectral, IBM Plex Sans, IBM Plex Mono en base64 |

## Reconstruire les PDF

```bash
pip install playwright pymupdf
python3 scripts/rendre-protocoles.py            # les trois
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
source : le bloc pèse 290 ko et il y a trois documents. Le script les injecte au
rendu à la place du repère `@@POLICES@@`.

## Les deux protocoles

### Dépression de l'horizon

L'angle entre l'horizontale vraie et la ligne d'horizon marin. Une sphère prédit
`δ = √(2h/R′)`, un plan prédit `δ = 0` à toute altitude.

Son intérêt tient à ce que la réfraction n'y intervient qu'au second ordre : sur
toute la plage défendable (0 ≤ k ≤ 0,47) la prédiction sphérique ne varie que de
107′ à 78′ depuis 3 107 m. **L'écart entre les modèles vaut au minimum 78′ pour
un budget d'erreur de 2,2′** — rapport signal sur bruit d'environ 36. C'est la
première mesure du dossier où l'incertitude sur la réfraction est plus petite que
l'écart à mesurer.

Deux méthodes : absolue avec calibration par retournement du boîtier, ou
différentielle entre deux altitudes — celle-ci n'exige aucun niveau et aucun
étalonnage.

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

## Historique des versions

Les corrections sont consignées dans les documents eux-mêmes, en pied de page et
dans des encadrés à l'endroit concerné. Elles ne sont pas effacées : un relecteur
les trouverait de toute façon.

- **Soleil 1.1** — le domaine de validité est énoncé en section 02. La 1.0
  opposait « modèle plan » et « modèle sphérique », attribuant ainsi à toute une
  famille de modèles une prédiction que seuls certains formulent. Un modèle où le
  disque visible est une projection n'est pas contraint par la loi en sin α, et
  le document le dit désormais.
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
