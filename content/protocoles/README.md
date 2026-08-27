# Protocoles de terrain

Sources des protocoles expérimentaux diffusables. Ce sont des documents destinés
à être remis à des observateurs extérieurs — ils énoncent leurs prédictions
**avant** toute acquisition et disent à l'avance ce que signifie chaque issue.

## Ce qui se trouve ici

| Fichier | Contenu |
|---|---|
| `horizon-fr.html` | Dépression de l'horizon marin — français, 25 pages, **v1.8** |
| `horizon-en.html` | Même document en anglais, 24 pages, **v1.8** |
| `depot/` | Le dépôt : marche à suivre, métadonnées, et les fichiers figés une fois le DOI inscrit |
| `soleil-bilingue.html` | Diamètre angulaire du Soleil — bilingue, 23 pages, v1.3 |
| `pole-celeste-bilingue.html` | Hauteur du pôle céleste — bilingue, 22 pages, v1.2 |
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
- **Horizon 1.2** — après relecture extérieure. Le budget d'erreur omettait
  l'incertitude de **modèle** due à la variation de k avec l'altitude : ±2,6′ à
  3 107 m, soit plus que le budget instrumental entier. Le rapport signal sur
  bruit passe de 36 à **23** — le test reste décisif, le chiffre annoncé était
  trop flatteur. La turbulence de visée rasante se mesure désormais sur une
  rafale au lieu d'être postulée ; la symétrie de l'horizon artificiel se teste
  par recoupement ; la méthode d'ajustement statistique est spécifiée. Une
  nouvelle section 04 situe le protocole parmi ses précédents : la formule est
  celle des tables de dépression de la navigation astronomique, et la mesure a
  déjà été faite des millions de fois. L'absence d'horodatage vérifiable est
  signalée comme le manque restant.
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
- **Soleil 1.3** — la relecture extérieure du protocole d'horizon vaut aussi ici.
  Le budget omettait deux termes de **modèle** : l'assombrissement centre-bord,
  systématique et corrélé à la hauteur (0,20 %), et le résidu d'éphéméride si la
  campagne s'étale (0,019 % par jour, soit 0,15 %). Le budget passe de 0,44 % à
  **0,51 %** et le rapport signal sur bruit de 150 à **130** — le test reste
  écrasant. L'aplatissement vertical du disque, jusque-là simple nuisance, devient
  une mesure gratuite de la réfraction du moment : 0,4 % à 15°, 0,9 % à 10°,
  3,7 % à 5°, 23,6 % à 2°. Une section 08 situe le protocole parmi ses précédents
  — l'astrométrie solaire suit le diamètre à la fraction de seconde d'arc, et la
  parallaxe diurne lunaire de 1,67 % est un effet classique publié.
- **Pôle 1.2** — même relecture. Le terme de **modèle** omis était la **déviation
  de la verticale** : la hauteur du pôle donne la latitude *astronomique*, non la
  géodésique, et l'écart va de 5″ en plaine à 60″ dans le cas documenté extrême
  (11,6″ au Schiehallion, Maskelyne 1775). Il reste sous le budget de 0,09° — soit
  324″ — mais il est systématique par site, et c'est une seconde raison de compter
  en distance au sol plutôt qu'en latitude : il y a en réalité *deux* latitudes,
  qui ne coïncident nulle part exactement. Le plan d'ajustement statistique est
  spécifié — σ vient de la dispersion observée et non du budget, le modèle
  azimutal paie son paramètre supplémentaire au χ² par degré de liberté, et les
  critères d'écartement d'une station sont posés d'avance. Une section 08 situe le
  protocole parmi ses précédents : la latitude par la Polaire est la pratique
  ordinaire de la navigation, et les arcs de méridien — Delambre et Méchain,
  Struve — sont exactement le test 3 mené sur 2 800 km. L'absence d'horodatage
  vérifiable est signalée. Les tableaux sont renumérotés : la 1.1 en portait deux
  au numéro 6 et sautait le 3.
- **Horizon 1.3** — seconde relecture extérieure. Quatre points, dont deux
  touchent au budget.
  1. **L'échelle angulaire** était un poste non chiffré. δ se lit en pixels et se
     convertit par la focale ; or la focale gravée est nominale à 2–5 % près, ce
     qui vaut 2 à 5′ sur une dépression de 100′ et ferait tomber le rapport
     signal sur bruit de 23 à 17. La 1.2 écartait l'étalon lunaire (7,0′) sans
     remarquer que la « méthode capteur » portait son propre terme.
     **L'astrométrie de champ** le ramène à 0,05′ et fournit en prime le profil
     de distorsion. L'échelle résolue devient un champ obligatoire.
  2. **La couche limite au-dessus de l'eau.** Le tableau de sensibilité traitait
     la variation de k avec l'altitude ; il manquait l'écart air–mer, qui
     commande le gradient des premiers mètres — donc k sous 50 m. ΔT devient un
     champ obligatoire, avec les trois régimes énoncés. Le sens tombe à l'inverse
     de l'intuition : c'est l'air froid sur eau chaude qui rapproche l'horizon.
  3. **La nappe** passe à un liquide visqueux (paraffine, glycérine), son
     agitation résiduelle se mesure sur la rafale — la dispersion du reflet
     divisée par deux — au lieu d'être supposée, et un couvercle de verre
     s'élimine par rotation de 180°.
  4. **L'exposant p est laissé libre.** Ajuster δ = a·h^p plutôt que δ = a√h
     teste la loi en racine au lieu de la supposer : six stations de 10 m à
     3 107 m déterminent p à ±0,022, soit 22 σ entre p = 0,5 et p = 1.
  La procédure d'horodatage est détaillée : figer le PDF, calculer le SHA-256,
  déposer sur OSF ou Zenodo, obtenir le DOI, publier les deux — et seulement
  ensuite collecter.
- **Horizon 1.4** — relecture complète du document de bout en bout, avant arrêt
  de la version.

  **Le rapport signal sur bruit.** Trois chiffres différents circulaient dans la
  même page : 36 au résumé, 23 en section 08, 45 au tableau des altitudes. Ils
  répondent en réalité à deux questions distinctes, désormais séparées.
  *Contre l'hypothèse plane* : le signal est l'écart entre δ = 0 et la plus
  petite dépression qu'une sphère puisse produire, 78,2′ à 3 107 m, valeur qui
  suppose déjà le k le plus défavorable ; le bruit est le budget instrumental
  seul, 2,2′ ; **rapport 36**. *Sur la détermination de a* : l'incertitude de
  modèle entre pleinement, σ = 3,41′ pour δ = 100,1′ ; **rapport 29**. Le 23 de
  la 1.2 combinait le signal le plus défavorable avec le bruit le plus large —
  il comptait k deux fois. La correction de la 1.2 était juste dans son principe
  mais appliquée à la mauvaise question, et sa note de version se reprochait à
  tort d'avoir été « trop flatteuse ». Les tableaux des altitudes et de l'échelle
  angulaire sont recalculés.

  **Ce qui manquait à qui voudrait faire l'expérience.** La *fenêtre
  d'observation* — la méthode A demande l'astre, son reflet et la ligne
  d'horizon marin dans une même image, et de nuit noire l'horizon n'est plus
  visible. Aucune version ne le disait. La réponse est celle du point stellaire
  au sextant : crépuscule nautique, ou Vénus et Jupiter avant le coucher du
  Soleil. Le *critère de pointé* de la ligne d'horizon, qui est un saut
  d'intensité où trois pixels valent 0,62′ à 100 mm. Et le *matériel*, encore
  organisé autour de l'inclinomètre et muet sur le plateau, le liquide et les
  éphémérides : qui suivait la liste ne pouvait pas exécuter la méthode A.

  **Un contrôle gratuit non exploité.** L'écart entre l'astre et son reflet vaut
  deux fois sa hauteur apparente, que l'éphéméride donne. Il vérifie l'échelle à
  0,5 % indépendamment du solveur — mais ne mesure pas k le long de la visée
  rasante, et le document le dit.

  **Corrections.** L'étape « étalon d'angle » de la solution de repli
  recommandait encore la focale gravée que la section 08 venait de disqualifier ;
  « aucun étalonnage » devient « aucun étalonnage de biais », l'échelle angulaire
  en étant un ; les figures 2 et 3 étaient dans le désordre ; les 1 873 km du
  modèle plan ne disaient pas depuis quelle altitude ils sont calculés.

- **Horizon 1.5** — le document contenait tous les éléments pour exécuter
  l'expérience, mais dispersés entre six sections et **sans leur ordre**. Or
  l'ordre n'est pas indifférent : plusieurs étapes rendent les précédentes
  irrécupérables. L'horodatage doit précéder la première image ; la vérification
  cartographique de l'azimut doit précéder la station, car une côte dans l'axe ne
  se distingue pas de l'horizon sur la photo ; la bague de mise au point doit être
  immobilisée *avant* la pose de mesure, sous peine d'annuler le report d'échelle
  vers la pose de résolution ; ΔT, marée et état de la mer se relèvent sur place ou
  jamais ; le critère de pointé doit être fixé avant la réduction et être le même
  partout.

  Une **section 05 « Marche à suivre »** donne l'ordre des opérations en cinq
  phases — préparation de campagne, préparation de station, mise en place,
  acquisition, réduction — signale les cinq étapes irréversibles, énumère le
  nécessaire réel (boîtier d'occasion, plat à gratin, huile de paraffine de
  pharmacie, Stellarium, Astrometry.net) et sépare ce qui **détruit** la mesure
  sans laisser de trace de ce qui la **dégrade** visiblement. Une consigne de
  sécurité y entre aussi : le protocole envoie des gens sur des falaises, de nuit,
  et n'en disait rien. Les sections suivantes glissent d'un rang.

- **Horizon 1.6** — un **emplacement réservé pour le DOI** est ouvert en première
  page et en section 13. Zenodo et OSF attribuent le DOI *avant* publication
  (« Reserve DOI »), il peut donc figurer dans le document lui-même plutôt qu'à
  côté, et la marche à suivre de la section 13 est réécrite dans cet ordre :
  réserver, inscrire, figer, hacher, téléverser les deux fichiers dans le même
  enregistrement, publier, et seulement alors collecter.

  L'empreinte, elle, ne peut pas y figurer : elle se calcule *sur* le fichier
  fini, et l'y inscrire le modifierait donc la fausserait. Elle vit dans les
  notes de l'enregistrement. Le document le dit, et dit aussi ceci : tant que la
  ligne du DOI porte la mention « en attente », le préenregistrement n'est pas
  opposable.

  `scripts/inscrire-doi.py` remplit les quatre emplacements — deux par langue —
  regénère les PDF, les copie dans `depot/` et calcule les empreintes. Il refuse
  de travailler s'il n'en trouve pas exactement quatre, et refuse d'être relancé.
  Un DOI recopié à la main dans trois emplacements sur quatre ne se verrait
  qu'après publication, c'est-à-dire trop tard.

  L'inscription du DOI ne change pas le numéro de version : elle remplit un
  emplacement prévu. **La 1.6 n'existe donc publiquement que sous sa forme
  portant le DOI** — l'exemplaire à emplacement vide ne doit pas circuler.

- **Horizon 1.7** — la section 04 est réécrite, sur une objection fondée. Elle
  citait six travaux antérieurs *sur parole* — sans leurs données, sans vérifier
  qu'ils satisfont les critères que le protocole s'impose — alors que toute sa
  méthode consiste précisément à ne pas croire une table sur parole. Deux
  standards : un pour les autres, un pour soi.

  Le tableau 3 les **gradue** désormais, colonne par colonne : préenregistré,
  budget d'erreur, données brutes *vues par nous*. **Aucun ne satisfait les
  quatre critères**, et la mesure en avion de ligne est reclassée « indicatif
  seulement » par les règles du document lui-même — mesure unique, échelle
  angulaire non documentée. Ce n'est pas un reproche : la plupart n'ont jamais
  prétendu être des expériences préenregistrées. Mais cela interdit de les
  invoquer comme des preuves acquises.

  Ce qui se vérifie **sans faire confiance à personne** est séparé du reste : le
  coefficient du Bowditch, qui se recalcule depuis le tableau 1 du protocole
  (0,97 par racine de pied ↔ k = 0,168, contre 1,7548 pour k = 0,17), et la
  conséquence géométrique du point à trois astres — ignorer la dépression depuis
  une passerelle de 15 m ouvrirait un chapeau de gendarme d'une vingtaine de
  milles nautiques.

  La prétention du document est reformulée en conséquence : non pas « personne
  n'a mesuré cela », mais **« personne ne l'a mesuré à ce niveau d'exigence »**.

  Deux précisions s'y ajoutent. Le sextant date de 1731 et la correction de
  dépression est antérieure à l'édition de 1802 du Bowditch — « depuis le XIXᵉ
  siècle » se rapportait à cette tabulation-là. Et une phrase énonce que le
  protocole **n'avance aucune hypothèse sur la cause** de la perpendicularité
  entre la nappe et le fil à plomb : il n'utilise que le fait, vérifiable à
  l'équerre, qu'elle a lieu. Le fil à plomb est un instrument, pas une théorie.

- **Horizon 1.8** — retrait de l'archéologie des versions. Le document
  expliquait, à une vingtaine d'endroits, ce que telle version antérieure disait
  de faux et comment telle autre l'avait corrigé. C'est utile à qui suit la
  rédaction, et sans valeur pour qui ouvre le document pour l'exécuter — le seul
  lecteur qu'il aura. Aucune version antérieure n'ayant été déposée ni diffusée,
  il n'y a rien à réconcilier pour personne, et l'audit reste possible par
  l'historique des sources.

  **Le contenu des corrections reste** — le double standard de la section 04, les
  deux rapports signal sur bruit, le référentiel d'altitude, l'échelle angulaire,
  la couche limite. Ils sont désormais énoncés comme des faits de méthode et non
  comme des repentirs : « Pourquoi un k unique ne suffit pas » plutôt que
  « Correction apportée à la version 1.1 ».

  **Ce qui est conservé** : le numéro de version en première page, qui identifie
  le fichier déposé ; l'encadré de la section 13 disant qu'un numéro de version
  ne prouve rien, qui relève du préenregistrement et non de l'histoire ; et une
  phrase — une seule — indiquant que le document a été révisé avant dépôt et que
  l'historique complet est fourni sur demande.

  Le numéro passe à 1.8 parce que le contenu change : la section 13 pose
  elle-même la règle que deux fichiers distincts ne peuvent pas porter le même
  numéro de version.

## Ce que ces protocoles ne font pas

Ils ne concluent pas sur la forme de la Terre. Chacun mesure une grandeur
précise et écarte une famille de modèles ; aucun ne prétend trancher davantage.
Le protocole solaire mesure une **distance**, pas une forme.

Les valeurs numériques se recalculent toutes depuis `scripts/rendre-protocoles.py`
et les formules citées en pied de chaque document.
