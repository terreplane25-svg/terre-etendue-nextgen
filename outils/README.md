# Outils de visée optique — paquets Python de référence

Quatre paquets qui implémentent le protocole « Portion visible d'une cible
éloignée au-dessus de la mer » v1.0, plus un pré-écran altimétrique et quatre
cas d'étude.

- **A — `visee_optique`** : géométrie géodésique et réfraction (§8-12, §28).
- **B — `preuve_image`** : empreinte, EXIF/GPS, chaîne de détention (§16).
- **C — `rapport_expertise`** : fiche d'observation §33 et archive §34.
- **D — `metrologie_image`** : du pointé sur l'image à l'angle, puis de
  l'angle au coefficient de réfraction effectif (§14-15, §19). Il ne recopie
  aucune géométrie : il importe l'outil A.

## Ce que ces paquets sont pour le site

**La référence.** Les outils du Lab tournent dans le navigateur, donc en
TypeScript, mais ces ports ne font pas autorité : chacun est épinglé à son
paquet Python par des vecteurs d'or.

    python3 scripts/generer-vecteurs-or-visee.py      # outil A — regénère les vecteurs
    python3 scripts/generer-vecteurs-or-preuve.py     # outil B — idem
    python3 scripts/generer-vecteurs-or-provenance.py # outil B, ingestion — idem
    python3 scripts/generer-vecteurs-or-rapport.py    # outil C — idem
    python3 scripts/generer-vecteurs-or-metrologie.py # outil D — idem
    npm run verifier:ports                            # vérifie que les quatre ports n'ont pas dérivé

Les quatre ports sont épinglés :

| Port | Référence | Vecteurs | Contrôles |
|---|---|---|---|
| `src/lib/visee-optique/noyau.ts` | outil A, 321 tests | 61 | 263 |
| `src/lib/preuve-image/noyau.ts` | outil B, 263 tests | 26 | 152 |
| `src/lib/preuve-image/provenance.ts` + `document.ts` | outil B, ingestion | 76 | 388 |
| `src/lib/rapport-expertise/noyau.ts` | outil C, 42 tests | 22 | 117 |
| `src/lib/metrologie-image/noyau.ts` | outil D, 102 tests | 79 | 789 |

Les quatre harnais ont été éprouvés en cassant volontairement le port : un tag
EXIF décalé d'un cran, le signe de l'hémisphère sud oublié, l'arc de tangence
biaisé de 10⁻⁷, un champ retiré d'un bloc de la fiche, deux répertoires de
l'arborescence intervertis, le pas pixel pris sur la largeur du fichier livré
au lieu du capteur, le point principal supposé au centre du recadrage, un
relevé nul inversé au lieu d'être majoré — chacun est détecté et nommé.

Une huitième cassure ne l'est pas, et c'est le contrôle qui a raison :
remplacer `atan2` par `atan` du quotient dans le calcul d'élévation ne change
rien, le dénominateur restant positif sur tout le domaine admissible. C'est le
commentaire qui prétendait le contraire qui a été corrigé, pas le code.

Toute correction de formule se fait **dans le Python d'abord**, puis se
répercute dans le port, puis les vecteurs sont régénérés. Jamais l'inverse.

## Installation

    python3 -m venv outils/.venv
    outils/.venv/bin/pip install pytest numpy scipy Pillow PyWavelets
    outils/.venv/bin/pip install -e outils/outil-A-visee-optique \
                                 -e outils/outil-B-preuve-image \
                                 -e outils/outil-C-rapport-expertise \
                                 -e outils/outil-D-metrologie-image

## Tests

    cd outils/outil-A-visee-optique     && ../.venv/bin/python -m pytest -q   # 321
    cd outils/outil-B-preuve-image      && ../.venv/bin/python -m pytest -q   # 289
    cd outils/outil-C-rapport-expertise && ../.venv/bin/python -m pytest -q   #  42
    cd outils/outil-D-metrologie-image  && ../.venv/bin/python -m pytest -q   # 102

Et, pour l'outil D, un essai qui pilote un vrai navigateur — les vecteurs
épinglent les formules, celui-ci vérifie le câblage :

    npm run essai:metrologie

## Simulateur de Visée (outil A) — quatre champs, un bouton

L'interface publique demande **quatre valeurs** : où vous êtes et la hauteur de
votre œil, ce que vous regardez et sa hauteur totale. Un seul bouton. Une
version antérieure en demandait onze, dont l'intervalle de réfraction, une
incertitude de mesure et un facteur d'admission, et renvoyait le visiteur à des
paragraphes d'un document qu'il n'a pas lu. Elle était juste et inutilisable :
un outil qu'il faut avoir compris avant de s'en servir ne sert qu'à ceux qui
n'en ont pas besoin.

**Ce qui a quitté l'écran n'a pas quitté le calcul.** La géodésique reste
celle de Vincenty sur l'ellipsoïde, et la réfraction reste rendue en enveloppe
tant que l'analyste ne la déclare pas. Ces choix sont pris par le moteur et
énoncés en prose dans un bloc rétractable — donc toujours contestables, ce qui
était le point.

### Ce qui est mesuré : le PIED de la cible, pas son sommet

C'est le pied qui disparaît en premier sous l'horizon, et c'est là que les deux
modèles divergent en premier. La grandeur mise en avant est donc `c`, la
hauteur masquée **en partant de la base** — « 54,3 m de la base masqués », avec
la fourchette de réfraction sur une ligne subordonnée — et non la part visible
du sommet, qui reste à 100 % longtemps après que la divergence est devenue
mesurable.

`c` **n'est pas bornée** à la hauteur de la cible. Au-delà de la distance
limite elle continue de croître et dit de combien la cible est passée sous
l'horizon. La borner à `H` perdrait cette information au moment où elle devient
la plus parlante. Quand `c` dépasse `H`, l'interface cesse d'afficher un
pourcentage — « 156 190 % masqués » est exact et illisible — et donne à la
place la profondeur du sommet sous l'horizon, en kilomètres.

### La règle de discrimination, et son seuil

`visee_optique/simulation.py` porte les **conventions** que cette refonte
ajoute. Ce n'est pas de la physique, et c'est pour cela que ce sont des
constantes nommées — affichées à l'écran plutôt que cachées dans une condition
d'interface.

Une visée est dite **discriminante** quand la courbure masque au moins **10 %
de la hauteur de la cible en partant de sa base**
(`SEUIL_DISCRIMINATION_FRACTION = 0.10`) — 11 m sur une cible de 110 m. Sous ce
seuil, les deux modèles prédisent des choses trop proches pour qu'une
photographie les sépare, et annoncer « discriminante » promettrait une mesure
que personne ne pourrait faire.

Une condition sur le relief a existé, et elle a été retirée avec le MNT : le
simulateur ne consulte plus de modèle de terrain, donc il n'a plus rien à dire
sur les obstacles. Ce contrôle appartient à l'analyste, sur l'image.

### Aucune distance n'est refusée

50 km, 500 km, 2 000 km : la géométrie ne borne rien, et rien n'a été ajouté
pour la borner. Depuis la suppression du modèle de terrain, la longueur d'une
visée ne coûte plus rien non plus — il n'y a plus d'altitudes à demander.

### Géométrie pure : plus aucun modèle de terrain

Le simulateur ne consulte plus de profil altimétrique et ne cherche plus
d'obstacle local. Le calcul porte exclusivement sur la ligne de visée théorique
entre les deux altitudes saisies.

Ce n'est pas un renoncement, c'est un partage des rôles : ce qui bouche
réellement la vue depuis un poste — une haie, un cargo, un bâtiment récent — ne
figure dans **aucun** modèle numérique de terrain, et se constate sur l'image.
C'est le contrôle de l'analyste, pas celui du simulateur. Un simulateur qui
prétendrait trancher cette question donnerait une fausse assurance.

`src/lib/visee-optique/altimetrie-ign.ts` et son contrôle ont été supprimés.
`relief.py` et `relief.ts` restent : le second fournit encore le tracé exact de
la ligne de visée, et le premier garde ses propres tests.

### Deux schémas, et pourquoi la Terre se bombe

Un tracé unique en « altitude au-dessus de la surface » faisait plonger la
ligne de visée sous le niveau zéro. Le calcul était exact — une corde droite
entre deux points bas traverse bel et bien la Terre, et c'est précisément
pourquoi la cible est occultée — mais l'image était absurde : une visée ne
passe pas sous le sol.

**C'est le repère qu'il fallait changer, pas le calcul.** Les altitudes sont
décalées du bombement de la surface au-dessus de la corde A–B :

    b(d) = R · [ cos(d/R − D/2R) − cos(D/2R) ]

nul aux deux extrémités, égal à la flèche au milieu. La surface devient un arc
qui monte, et c'est **lui** qui vient couper la visée — la description physique
juste. Le décalage étant le même pour la surface et pour la visée, tous les
écarts verticaux sont préservés exactement : la bande rouge sur la cible mesure
la hauteur masquée réelle.

La visée tracée est le **rayon rasant**, celui qui frôle la surface à
l'horizon. C'est le rayon le plus bas que l'observateur puisse envoyer, donc la
limite de ce qu'il voit, et il ne descend jamais sous la surface. Sa hauteur
au-dessus de la base de la cible vaut **exactement** l'occultation calculée :
les deux ont été confrontées numériquement, l'écart est nul à l'epsilon
machine. Le dessin et le chiffre disent donc la même chose.

Deux schémas empilés, une seule échelle verticale — sans échelle commune, la
bande rouge d'un schéma ne serait pas comparable à la cible entière de l'autre,
et la comparaison, qui est tout l'objet de l'outil, serait fausse. La cible est
découpée en **rouge** (masqué à la base) et **vert** (émergent) ; sur le modèle
plat elle est entièrement verte.

Un contrôle au navigateur lit les chemins SVG et mesure, abscisse par abscisse,
de combien la visée passe sous le sol : zéro pixel sur trois configurations,
dont une cible enfouie à 2 548 km. Rétablir l'ancien tracé fait remonter le
contrôle à 38 pixels — il discrimine.

### L'altitude du sol et la hauteur de l'ouvrage sont deux champs distincts

Google Earth affiche l'altitude du **terrain** sous le curseur. Ce n'est ni la
hauteur de l'œil de l'observateur, ni la hauteur d'un phare : il faut ajouter
la seconde à la première. Un seul champ « hauteur » invitait à saisir l'une
pour l'autre, et l'erreur ne se voit pas dans le résultat — elle le décale.

Le formulaire demande donc, pour chaque point : la position, l'**altitude du
sol**, et la **hauteur propre** de l'équipement ou de l'ouvrage.

**La séparation change la géométrie, pas seulement l'ergonomie.** La base de la
cible n'est plus au niveau de la mer mais à l'altitude de son terrain, ce qui
recule la distance critique `D_crit = s(h) + s(z_b)` et réduit l'occultation.
Mesuré : la même cible de 110 m à 35,6 km voit 54,3 m de sa base masqués si
elle est posée sur l'eau, et **rien du tout** si elle est posée sur une falaise
de 200 m — la visée devient non discriminante.

Un mot sur les référentiels verticaux, parce que le piège est réel : les
altitudes doivent être comptées **au-dessus du niveau moyen de la mer**, comme
les donnent Google Earth (géoïde EGM96) et l'IGN. La géodésie de Vincenty
n'intervient que sur la distance HORIZONTALE, sur l'ellipsoïde WGS-84 ; les
altitudes, elles, sont des hauteurs au-dessus de la surface de référence et ne
se mélangent pas à l'ellipsoïde. Il n'y a donc aucun décalage d'origine — sauf
si l'on y verse une hauteur ellipsoïdale brute de récepteur GNSS, qui diffère
de près de 50 m en France. L'interface le dit.

### Le coefficient de réfraction, par défaut et à la main

Par défaut, `k = 0,13` et l'enveloppe 0,10–0,40 affichée à part. Une case à
cocher discrète — « Spécifier le coefficient k de réfraction » — révèle un
champ prérempli à 0,13 ; la valeur saisie sert alors au calcul, au verdict et
au tracé.

Quand k est déclaré, **l'enveloppe disparaît** : l'afficher quand même
contredirait ce que l'analyste affirme connaître. La carte dit « k = 0,25,
valeur unique — aucune enveloppe », et le bloc du bas nomme le coefficient
employé.

`motif_refraction(k)` produit la phrase affichée **à partir de la valeur
employée**, et le port est épinglé sur ce texte pour onze valeurs de k. Une
phrase figée qui nommerait 0,13 alors que le calcul a tourné sur 0,18 serait un
mensonge d'affichage — le genre qui survit longtemps parce que personne ne
relit la prose.

Le refus de `k ≥ 1` illustre un partage utile : la **règle** reste celle de
`rayon_effectif`, qui décide seul, et `verifier_k` ne fait que rhabiller son
refus. Le message du paquet de référence parle de « §8 » et de « Tableau 8 » —
juste dans un protocole, illisible dans un simulateur dont on a retiré tous les
renvois. Un contrôle vérifie qu'aucun « § » ni « Tableau » ne remonte au
visiteur : sans lui, le nettoyage se défaisait par la porte des messages
d'erreur.

### La saisie des coordonnées : décimales ou DMS

`geocodage-ign.ts` lit la saisie comme des coordonnées **avant** de songer à
une adresse : degrés décimaux (« 50.94642, 1.75305 ») ou degrés-minutes-secondes
(« 50°52'47.56"N 1°38'46.91"E »). Aucune requête ne part dans ces deux cas, et
un contrôle compte les requêtes pour l'établir.

Répondre « adresse introuvable » à des coordonnées parfaitement lisibles serait
un refus de lire, pas une information. Le parseur DMS accepte les guillemets
typographiques — un copier-coller de carte en produit toujours —, la virgule
décimale, les minuscules, le « O » français comme le « W » anglais, et les
minutes ou secondes omises.

**Le point cardinal fait autorité sur l'ordre** : « 1°38'E 50°52'N » est compris
comme « 50°52'N 1°38'E ». Se fier à la position dans la chaîne inverserait
latitude et longitude sur une saisie valide, sans rien signaler. Une saisie
incohérente — deux latitudes, 60 minutes, aucun cardinal — est refusée plutôt
que devinée.

## Le relief (outil A) — hors du simulateur, conservé côté Python

`visee_optique/relief.py` garde ses tests et reste dans le paquet de
référence : la coupe du terrain, la détection d'obstacles et la ligne de visée
exacte y sont éprouvées, et le protocole peut en avoir besoin.

Ce qui a été **supprimé**, c'est son port navigateur — `relief.ts`, ses
vecteurs d'or, son générateur et son vérificateur de 804 contrôles. Le
simulateur ne consulte plus aucun modèle de terrain ; le module n'était plus
importé par aucune page. Un port qu'aucun appelant ne touche ne se vérifie que
contre lui-même : il coûte un vérificateur à chaque passe et ne protège rien.
`git` le garde, si la question revient.

Deux points de conception commandent le module Python :

- **Un profil absent donne « relief non évalué », jamais « aucun obstacle ».**
  Le champ vaut `None`, pas `False`. Les confondre transformerait une lacune de
  donnée en preuve.
- **Un point ne devient obstacle que s'il coupe la visée ET s'élève au-dessus
  de la surface de référence.** Sans cette seconde condition, dès que la
  courbure occulte quoi que ce soit, la mer coupe la visée dirigée vers le
  sommet et serait rapportée comme obstacle de relief : la distinction
  s'effondrerait dans les cas mêmes où elle sert. Conséquence assumée : une
  plaine à l'altitude zéro est traitée comme la surface elle-même, et son
  masquage est imputé à la courbure.

La ligne de visée est construite exactement (segment droit dans l'espace),
pas par l'approximation `d(D−d)/2R`. Les tests la confrontent à une forme
fermée indépendante — la corde d'un triangle isocèle, exacte à l'epsilon
machine — et à l'approximation classique dans son domaine de validité.

### Le profil altimétrique, et ce qu'il change à la posture

Les autres outils du Lab ne transmettent rien. Celui-ci est différent :
demander un profil de terrain à l'IGN suppose de lui envoyer les coordonnées
du poste et de la cible. L'appel n'est **jamais automatique**, l'interface le
dit avant, et l'outil reste entièrement utilisable sans réseau — par saisie
manuelle du profil, ou sans relief du tout.

🔴 **Le service de l'IGN n'a jamais été interrogé.** L'environnement de
développement n'a pas d'accès sortant vers `data.geopf.fr`. `altimetrie-ign.ts`
est écrit d'après le contrat publié, et `scripts/verifier-altimetrie-ign.mjs`
(37 contrôles) éprouve la mise en forme des requêtes, l'appariement des
réponses conformes et le refus des réponses non conformes — **pas** que le
service réponde ce qu'on croit. La confrontation au service réel reste à
faire, et l'interface affiche cette réserve.

Le RGE ALTI couvre la France et les DOM. Ailleurs le service rend `-99999`,
qui veut dire « pas de donnée » et surtout pas « altitude zéro » : traité comme
une lacune, jamais comblé.

## Le relevé unifié (outil B)

`dossier.py` n'extrait rien : il ORCHESTRE les six lecteurs et range ce qu'ils
rendent dans une structure identique quel que soit le format d'entrée —
`file_analysis`, `device_identification`, `capture_settings`,
`telemetry_and_location`, `provenance_and_software`, `deep_fingerprint`.

### Le défaut propre à un relevé unifié

Il présente côte à côte des champs qui ne s'établissent pas de la même façon :
une marque **lue**, un numéro de série **lu**, un type de matériel **déduit**,
une correspondance d'écran qui **n'existe pas**. Dans un JSON, les quatre ont
exactement la même apparence, et un lecteur pressé les prendrait pour des
faits de même nature.

Trois dispositions l'en empêchent :

- chaque bloc porte un `detection_method` qui dit d'où vient l'information ;
- un champ qu'on ne peut pas renseigner vaut `null` **et** porte son motif ;
- les déductions portent la **règle** qui les a produites, pour qu'on puisse
  les contester sans relire le code.

### Les quatre champs définitivement nuls

| Champ | Ce qui manque |
|---|---|
| `shutter_count` | n'existe dans aucun tag EXIF standard, seulement dans les MakerNotes |
| `screen_resolution_match` | pas de référentiel vérifié — et le signal serait faible même vérifié |
| `jpeg_quantization_match` | pas de corpus de fichiers réels dont la provenance soit établie |
| `c2pa_verified` | faux par construction : aucune signature n'est validée |

### Le type MIME vient des octets

Jamais de l'extension. L'écart entre les deux est signalé quand il est franc.
Un fichier se renomme par mégarde : ce n'est pas une preuve de manipulation,
mais c'est un écart, et il est relevé.

### Le type de matériel est déduit par quatre règles

Télémétrie de vol présente ; nom d'objectif déclarant une caméra avant ou
arrière ; double numéro de série boîtier + objectif ; format brut de
constructeur. Chacune s'appuie sur une trace non ambiguë. **Aucune règle
applicable rend `null`** — un « appareil photo » deviné d'après un fabricant
vaudrait moins que rien.

### Aucun lecteur en échec n'interrompt les autres

Un JPEG dont l'EXIF a été purgé garde ses tables de quantification. Chaque
échec est consigné avec son motif : l'absence d'un bloc et l'échec de sa
lecture ne s'établissent pas de la même façon. Un partage de responsabilité
entre lecteurs — un JPEG chez le lecteur de PNG — n'est pas consigné comme
une panne.

## Extraction universelle (outil B)

Quatre familles de lecteurs se partagent le travail. Un format non couvert par
l'un d'eux est **refusé en le disant**, jamais rendu comme un inventaire vide —
qui laisserait croire que le fichier ne déclare rien.

| Lecteur | Ce qu'il couvre |
|---|---|
| `metadata.py` | EXIF/TIFF : JPEG, TIFF et tous les RAW à structure TIFF, RAF |
| `isobmff.py` | conteneurs à boîtes : HEIC, HEIF, AVIF, **CR3** |
| `conteneurs.py` | PNG, WebP, GIF, BMP, SVG, et le profil ICC |
| `provenance.py` | C2PA/JUMBF, XMP, IPTC, chaînes lisibles |
| `quantification.py` | tables DQT d'un JPEG |
| `telemetrie.py` | télémétrie de vol dans le XMP (DJI, Parrot, Autel) |
| `makernotes.py` | la **structure** des notes propriétaires (tag 0x927C) |

### Ce que le profil ICC donne

La description (`desc` en v2, `mluc` UTF-16 en v4) porte le nom qu'on attend :
« Display P3 », « sRGB IEC61966-2.1 ». L'en-tête dit ce que le profil PRÉTEND
être ; rien ne vérifie qu'il décrit les couleurs du fichier.

### Le CRC des chunks PNG, et son asymétrie

Un CRC faux **établit** que les octets ont changé depuis l'écriture du chunk.
Un CRC juste **n'établit rien de plus** que « celui qui a modifié le chunk a
recalculé le CRC », ce que fait tout éditeur. Les deux sont rendus, et
l'asymétrie est affichée avec.

### Les tables de quantification

Elles survivent à la purge de l'EXIF : un fichier dont toutes les métadonnées
ont été retirées porte encore ses tables. Le facteur de qualité IJG est
toujours rendu **avec son écart** — zéro veut dire « c'est exactement cette
table », tout le reste veut dire « elle n'en vient pas », ce qui est le cas de
tout appareil photo.

🔴 **Le registre `SIGNATURES_CONNUES` est VIDE, délibérément.** Associer une
empreinte de tables à « Canon DIGIC » ou « algorithme WhatsApp » demande un
corpus de fichiers réels dont la provenance est établie, appareil par appareil
et version par version. Ce dépôt n'en a pas. Y écrire des correspondances de
mémoire produirait des identifications fausses présentées comme des faits.
L'empreinte reste utilisable pour **comparer deux fichiers qu'on a tous les
deux** : des tables identiques sortent de la même chaîne d'encodage aux mêmes
réglages.

### La note propriétaire, et pourquoi son sens n'est pas rendu

Le tag EXIF 0x927C est le seul champ de la norme dont le contenu n'est **pas**
normalisé : chaque constructeur y écrit ce qu'il veut, dans la forme qu'il
veut, et le change d'un millésime à l'autre. C'est là que vivent le décompte
des déclenchements et le type d'objectif — d'où l'envie de le lire.

`makernotes.py` en lit la STRUCTURE : le constructeur reconnu à sa signature,
qui est dans les octets ; l'inventaire des tags avec leur identifiant, leur
type, leur cardinalité, leur taille, leur forme et l'empreinte de leur valeur.

🔴 **Le registre `SENS_CONNUS` est VIDE, délibérément.** « Tag 0x0095 = type
d'objectif » écrit de mémoire est une attribution, pas une lecture, et le sens
d'un même identifiant change d'un millésime à l'autre chez un même
constructeur. L'inventaire reste utilisable pour **confronter deux fichiers
qu'on a tous les deux** : deux notes de même empreinte sortent du même appareil
aux mêmes réglages.

#### La base des offsets : le piège du format

Un IFD range ses valeurs longues à un offset, mais l'ORIGINE de cet offset
change selon le constructeur — l'en-tête TIFF du fichier pour les uns, le début
de la note pour les autres, un en-tête TIFF interne chez Nikon. Se tromper
d'origine **ne lève aucune erreur** : on lit des octets quelconques, qui
ressemblent à des données.

Les bases candidates sont donc ESSAYÉES, celle qui donne un IFD cohérent est
retenue, et le relevé dit laquelle — ainsi que le fait qu'elle corresponde ou
non à celle qu'annonce la documentation. Un écart est signalé plutôt que tu :
c'est le genre de chose qui apprend quelque chose sur le fichier.

Deux garde-fous qui se lisaient bien ont été retirés après vérification : un
contrôle de cardinalité et une borne à quatre octets, dont un balayage a établi
qu'ils n'écartaient rien que les contrôles voisins n'écartaient déjà. Un
garde-fou qui ne garde rien coûte plus qu'il ne rapporte : il fait croire à une
protection.

### La télémétrie de vol

DJI écrit `GpsLongtitude`, avec un t de trop, depuis des années : ne traiter
que l'orthographe correcte ferait perdre la longitude sur la majorité des
images de drone en circulation. Les deux formes d'écriture XMP sont lues,
attribut et élément.

La **station sol** n'est presque jamais écrite : ce que le fichier porte, c'est
la position du drone. Le champ reste nul avec son motif. L'**altitude
relative** est comptée depuis le point de décollage, pas depuis le sol survolé
ni le niveau de la mer, et l'avertissement l'accompagne partout.

### Un garde-fou sur les sources

`scripts/verifier-sources-texte.mjs` refuse tout octet de contrôle en clair
dans un fichier source. Quatre fois dans ce dépôt, un octet nul réel s'est
glissé dans un littéral en écrivant du code qui compare des octets : le
fichier devient binaire, et la comparaison qu'on croit lire dans le source
n'est pas celle qui est écrite. Ni le compilateur ni les tests ne le voient.

### Ce que rien de tout cela n'établit

Les fichiers d'essai sont **fabriqués** à partir des structures publiées, pas
prélevés sur des appareils réels. Ce qui est vérifié, c'est que les lecteurs
suivent ces structures — pas qu'ils lisent ce qu'un iPhone, un Canon ou un DJI
écrivent vraiment. Les **notes propriétaires** sont lues en structure, jamais en
sens : on sait qu'un tag existe, son type et sa taille, pas ce qu'il signifie.
Confronter l'ensemble à des fichiers d'appareils réels reste à faire.

## Formats bruts d'appareil photo (outil B)

L'outil B lit l'EXIF, le GPS et les aperçus embarqués des fichiers RAW, en
plus des JPEG. La quasi-totalité des formats bruts sont en fait des TIFF —
CR2, NEF, ARW, DNG, ORF, PEF, SRW, RW2, IIQ, 3FR — et leur EXIF est à la
racine du fichier, dans l'IFD0 et le sous-IFD Exif, sans segment APP1 à
chercher. Le RAF de Fujifilm n'est pas un TIFF, mais embarque un JPEG complet
dont l'en-tête donne l'offset en clair.

**Le CR3 des Canon récents n'est pas lu.** C'est un conteneur ISO BMFF, comme
un MP4 : les métadonnées y sont dans des boîtes que ce lecteur n'implémente
pas. Il est détecté et **refusé en se nommant**, plutôt que lu de travers —
rendre des champs vides laisserait croire que le fichier n'en porte pas. Son
empreinte SHA-256 reste valide : sceller un fichier et savoir le lire sont
deux propriétés indépendantes.

Un RAW porte **plusieurs** images embarquées — un aperçu pleine résolution,
un aperçu moyen, une vignette — écrites à des moments potentiellement
différents du traitement. Elles sont toutes rendues, de la plus grande à la
plus petite, avec leur provenance (IFD0, IFD1, sous-IFD n). N'en montrer
qu'une masquerait les autres, or c'est leur comparaison qui a valeur d'indice.

**Ce que cela n'établit pas.** Les fichiers d'essai sont fabriqués ici à
partir des structures publiées, pas prélevés sur des boîtiers réels. Ce qui
est vérifié, c'est que le lecteur suit ces structures — pas qu'il lit ce
qu'un Canon ou un Nikon écrit vraiment. Un vrai CR2 fait 25 Mo et porte des
MakerNotes propriétaires que rien ici ne décode. **Confronter le lecteur à des
fichiers de boîtiers réels reste à faire.** L'extension `.REF` mentionnée dans
la demande n'est pas un format brut identifiable : c'est vraisemblablement
`.RAF` (Fujifilm), qui, lui, est couvert.

## Ce qui a changé depuis la livraison

**Vincenty a été promue dans `visee_optique.geodesy`.** Elle vivait en cinq
copies hors du paquet — le pré-écran et les quatre `case_data.py` — donc hors
de toute couverture, alors que c'est elle qui produit le D et l'azimut dont
dépend tout le reste. Les cinq copies étaient numériquement identiques : le
risque était latent, pas réalisé.

Les cinq copies ont depuis été **supprimées**, soit 475 lignes : chaque
appelant importe le paquet. Trois des quatre `case_data.py` en portaient une
qu'aucun code n'appelait jamais.

Deux différences ont été introduites à dessein :

- **La non-convergence n'est plus silencieuse.** Les copies sortaient de la
  boucle après `max_iter` sans le signaler, et retournaient le dernier itéré
  comme si c'était une distance. Un couple quasi-antipodal lève maintenant.
- **`azimut_2_vers_1` est renommé `azimut_arrivee_deg`.** La formule retourne
  α₂, l'azimut *au point d'arrivée dans le même sens de parcours*, pas le
  gisement de retour. Sur l'équateur vers l'est, les copies retournaient 90°
  sous un nom qui promet 270° : qui s'en servait comme d'un azimut de retour
  se trompait d'un demi-tour. Le test l'a attrapé.

Vingt-six tests couvrent désormais ces deux fonctions, dont deux qui les
confrontent à des résultats obtenus **sans** Vincenty : sur l'équateur la
distance vaut exactement a·Δλ, et sur un méridien elle vaut l'intégrale du
rayon méridien, calculée ici par quadrature.

## Ce que le port de l'outil B fait en plus

Le vérificateur d'intégrité tourne **entièrement dans le navigateur** : le
fichier de l'utilisateur n'est jamais transmis, ni stocké, ni journalisé. Ce
n'est pas qu'une commodité d'hébergement, c'est ce qu'un tiers de confiance
doit pouvoir dire de son propre outil — et c'est vérifié plutôt qu'affirmé :
zéro requête réseau relevée pendant l'analyse d'un fichier.

Le SHA-256 passe par WebCrypto, la même primitive dans le navigateur et dans
Node. Il a été confronté à `sha256sum` du système, une troisième
implémentation indépendante du Python comme du navigateur : identique.

## L'archive produite par le navigateur, validée par le Python

Le générateur de fiche écrit un ZIP sans compression, à la main
(`src/lib/rapport-expertise/zip.ts`, aucune dépendance). Sans compression
délibérément : l'empreinte d'un fichier est alors la même dans l'archive et
hors d'elle, donc le manifeste se contrôle sans décompresseur.

Trois contre-épreuves indépendantes plutôt qu'une affirmation :

- `unzip -t` ne détecte aucune erreur, et le CRC-32 rend la valeur normalisée
  `cbf43926` sur la chaîne d'épreuve `123456789` ;
- `sha256sum -c SHA256SUMS` valide le manifeste produit dans le navigateur,
  avec les vrais fichiers ;
- `rapport_expertise.archive.verifier_arborescence` — la fonction Python
  elle-même — déclare l'arborescence conforme au §34, aucun répertoire
  manquant.

Et `originaux_proteges` retourne False, comme attendu : le verrouillage Unix de
`10-originaux/` est la seule chose que le navigateur ne peut pas faire. Le
LISEZ-MOI de l'archive donne la commande plutôt que de la simuler.

## Les quatre cas d'étude

Ils tournent depuis leur propre dossier, sans rien installer d'autre que les
paquets :

    cd outils/exemples-cas-etudes/cas-sangatte && python3 run_case.py

Chacun produit `sortie/dossier-<identifiant>/` — l'arborescence du §34, remplie
— et son ZIP. Ces sorties ne sont pas commitées : elles se régénèrent.

| Cas | Distance | Conclusion |
|---|---|---|
| Chassiron ↔ Cordouan | 54,4 km | **invalidé** — 19,4 km de terre ferme sur la visée |
| Cordouan | — | validé |
| Garoupe ↔ Monte Cinto | — | validé |
| Sangatte ↔ South Foreland | 35,6 km | validé — profil 100 % maritime |

Trois choses les empêchaient de tourner, et sont corrigées :

- **`build_demo_image` était absent de la livraison.** Le module est écrit, dans
  `exemples-cas-etudes/commun/`. Il produit un diagramme JPEG avec un EXIF
  lisible — un diagramme calculé, jamais une photographie, et l'EXIF le
  déclare. Aucune coordonnée GPS n'y est écrite : un diagramme n'a pas été pris
  quelque part, et en inventer une serait exactement ce que le protocole
  interdit.
- **Les chemins étaient codés en dur** (`/home/claude/...`), donc inertes
  ailleurs. `commun/bootstrap.py` résout les paquets relativement au fichier,
  après avoir essayé l'import direct.
- **L'archive copiait le code depuis le mauvais endroit** une fois
  `build_demo_image` mutualisé. Elle le prend là où il est.

Au passage, l'EXIF écrit par Pillow et relu par `preuve_image` a révélé un
défaut d'écriture : un flottant Python nu est encodé en DOUBLE (type TIFF 12),
que la norme EXIF n'emploie pas pour FocalLength, FNumber ni ExposureTime. Notre
lecteur, qui n'implémente que les types du protocole, rendait alors les octets
bruts au lieu de les coercer en silence. C'est l'écriture qui était fautive :
elle passe désormais par `IFDRational`, et les dix champs font l'aller-retour.

## Ce qui reste à faire

- Le pré-écran altimétrique exige un accès réseau serveur vers l'API IGN, non
  disponible côté navigateur (CORS) ni depuis l'environnement de développement
  actuel. Il n'est pas intégré au site. Son auto-test, lui, tourne hors réseau :
  il rejoue les 77 points d'altimétrie déjà relevés pour Chassiron et retrouve
  les deux traversées de terre, 19,40 km au total.


## Ce que l'outil D corrige au cahier des charges

Il a été spécifié à partir d'un cahier des charges qui portait six défauts. Ils
sont énoncés en tête des modules concernés, avec leur correction ; les trois
qui changent un résultat :

**« Px_masqué = |y_bas − y_horizon| » ne mesure pas une hauteur masquée par la
courbure.** Le rayon rasant qui définit l'horizon est le même qui définit le
point le plus bas visible de la cible : les deux tombent exactement à la même
élévation. On l'établit analytiquement — tan E(z_v, D) = −tan(s(h)/R) — et
`test_horizon_et_base_confondus` le vérifie sur six configurations. La portion
cachée est *derrière* l'horizon, pas au-dessous : elle n'a aucune extension
verticale dans l'image. Le premier clic n'est donc pas une mesure mais un
CONTRÔLE, et c'est ce qui en fait la partie la plus utile du relevé.

**Le pas pixel se calcule sur la définition native du capteur, jamais sur celle
du fichier livré.** Un recadrage ne change pas le pas : il enlève des pixels, il
ne les agrandit pas. Une image recadrée de 6000 à 1500 px traitée avec sa
largeur finale donne un angle quatre fois trop grand — silencieusement. Le
recadrage déplace en outre le point principal, que la forme paraxiale du cahier
des charges ignore.

**« Ajuster k jusqu'à ce que H_théorique(k) == H_obs » suppose une solution
unique.** Il n'y en a pas toujours : au-delà d'un seuil la cible est entière et
l'angle cesse de dépendre de k ; en deçà d'un autre elle est occultée jusqu'au
sommet et l'angle prédit vaut exactement zéro pour toute valeur de k. Une
bissection prise au mot rend alors le bord du domaine d'exploration comme s'il
s'agissait d'une mesure — un chiffre parfaitement précis et parfaitement vide.
L'outil rend un statut à quatre valeurs et n'écrit jamais un k qu'il n'a pas
établi.

Les trois autres : les seuils d'interprétation proposés (k > 0,25) ne sont pas
ceux du Tableau 8 du protocole (0,20) ; « cible surélevée » est une conclusion
sur la scène quand seule une valeur de k est établie ; et la conversion
D·tan(θ) suppose la scène plane et perpendiculaire à la visée, si bien qu'elle
est rendue à côté de la forme exacte plutôt qu'à sa place.


## Ce qui tourne sur un téléphone, et ce qui n'y tourne pas

`npm run audit:mobile` mesure, sur un iPhone 13 émulé (390×844, tactile) avec
le processeur bridé ×4, ce que chaque outil du Lab fait réellement : débordement
horizontal, cibles tactiles, erreurs, et durée des calculs sur une photo de
4032 × 3024 (12,2 Mpx, 3,4 Mo).

**Rien de lourd ne tourne dans le navigateur.** Les traitements coûteux du
protocole — carte ELA, résidu de bruit par ondelettes, empreinte de capteur et
pic de corrélation (§16) — vivent dans `preuve_image.sensor_forensics`, en
Python, et ne sont pas portés en TypeScript. Ils s'exécutent sur un poste de
travail, avec numpy, scipy et PyWavelets. Il n'y a donc rien à désactiver sur
téléphone : ces modules n'y sont pas.

Ce qui tourne dans le navigateur, mesuré :

| Opération | Durée (processeur bridé ×4) |
|---|---|
| Empreinte SHA-256 + lecture EXIF + affichage | 310 à 760 ms |
| Décodage et rendu du canevas 12 Mpx | ~200 ms |
| Pointé au doigt → barre de validation | ~390 ms |

Toutes sous le seuil de 3 s, et d'un ordre de grandeur. `crypto.subtle.digest`
est natif ; l'analyse EXIF ne lit que quelques centaines d'octets d'en-tête.

**La contrainte réelle sur téléphone n'est pas le calcul, c'est le pointé.** Le
canevas affiche l'image réduite : sur un écran de 390 px, un pixel d'écran vaut
13,4 pixels d'image. C'est la loupe ×8 qui rend le pointé possible — elle ramène
la résolution à 1,7 pixel d'image — et les boutons de retouche ±1 px qui
permettent d'atteindre le pixel. L'outil affiche cette résolution, mesurée sur
le canevas rendu, et signale un σ déclaré plus fin que ce que le geste peut
produire.


## Le module d'ingestion, et la limite qu'il ne franchit pas

`preuve_image.provenance` lit ce qu'un fichier DÉCLARE de son histoire : le
conteneur C2PA (JUMBF, en JPEG APP11 comme en PNG `caBX`), les paquets XMP, les
enregistrements IPTC-IIM, et les chaînes lisibles des en-têtes. `metadata.py`
lit en outre les champs d'ingestion de l'EXIF — logiciel, horodatages, densité,
espace colorimétrique, mode et programme d'exposition, flash, rapport de zoom
numérique — et la miniature de l'IFD1.

Les lecteurs sont écrits ici plutôt qu'empruntés, pour la raison déjà donnée en
tête de `metadata.py` : pour un usage probatoire, savoir exactement ce qui est
extrait — et ce qui ne l'est pas — compte autant que l'extraction. Cela inclut
un décodeur CBOR de deux cents lignes, éprouvé par les vecteurs de l'annexe A
de la RFC 8949 : une table écrite par d'autres.

**Aucune signature n'est vérifiée, et c'est dit partout où un manifeste
s'affiche.** La validation d'un manifeste C2PA exige la vérification COSE, le
contrôle de la chaîne X.509 contre une liste de confiance, et le recalcul des
empreintes de liaison au contenu. Rien de cela n'est implémenté. Un manifeste
lisible peut donc être authentique, désolidarisé de l'image, ou entièrement
fabriqué — cette lecture ne les distingue pas. Symétriquement, son absence n'est
pas un indice : presque aucun appareil n'en écrit, et la plupart des retouches
effacent ceux qui existaient.

Ce que les autres lectures n'établissent pas, dans le même esprit :

  · un **logiciel déclaré** ou un **marqueur de chaîne** n'établit pas qu'il y a
    eu retouche — un convertisseur de format écrit son nom sans toucher au
    contenu visible — et son absence n'établit pas le contraire ;
  · **XMP et IPTC** sont des champs rédactionnels : n'importe qui les écrit,
    les modifie ou les efface avec un éditeur de texte ;
  · une **miniature** qui concorde avec l'image n'établit rien, car tout éditeur
    qui la régénère efface la trace. Seul un ÉCART est un fait.

### Ce qui reste à faire

Les conteneurs C2PA employés par les tests et les vecteurs sont **construits à
partir de la spécification**, pas produits par une implémentation du marché.
Ils établissent que le lecteur suit la structure décrite ; ils n'établissent pas
qu'il lit ce qu'un outil C2PA réel écrit. Confronter le lecteur à un fichier
signé par une implémentation de référence reste ouvert — c'est la contre-épreuve
qui manque, et rien ici ne prétend le contraire.


## Le document d'ingestion, et quatre écarts assumés au schéma

`preuve_image.document.document_ingestion(octets)` rend d'un seul appel tout ce
qu'un fichier déclare, dans la forme convenue : `file_info`, `exif`, `c2pa`,
`thumbnail`, plus XMP, IPTC et les marqueurs de chaînes. Le port TypeScript
(`src/lib/preuve-image/document.ts`) en fait autant dans le navigateur, et la
comparaison d'épinglage porte sur le **document entier sérialisé** : une clé
oubliée, renommée ou ajoutée d'un seul côté fait tomber le contrôle.

Quatre points du schéma reçu ne pouvaient pas être suivis tels quels sans
écrire quelque chose de faux. Dans les quatre cas la clé demandée existe, et une
clé voisine porte ce qui manquait.

**1. L'horodatage ne porte pas de fuseau que le fichier ne déclare pas.** Le
schéma d'exemple donnait `"2014-07-31T18:05:43+02:00"`. Or `DateTimeOriginal`
est une heure locale SANS fuseau : l'offset n'existe que si l'appareil a écrit
`OffsetTimeOriginal` (tag 0x9011), ce que peu de boîtiers font. Offset présent →
ISO 8601 complet ; offset absent → heure locale nue et `offset_declare: false`.
Sur une observation horodatée, supposer « +02:00 » est le genre d'invention qui
décide d'un résultat.

**2. `dpi` est un scalaire, la réalité en a deux.** XResolution et YResolution
peuvent différer, et aucune densité n'est définie quand ResolutionUnit vaut 1
(« sans unité » : le nombre est un rapport d'aspect). `dpi` n'est rempli que si
les deux axes coïncident ; `dpi_x` et `dpi_y` sont toujours là.

**3. `camera` concatène Make et Model, ce qui ne se défait pas.** « SONY
ILCE-6000 » ne redonne pas à coup sûr le couple d'origine : `make` et `model`
restent disponibles séparément.

**4. `c2pa.signature` ne peut pas se lire comme un verdict.** La clé porte
l'identité DÉCLARÉE du signataire, et `verified: false` l'accompagne toujours
avec son motif. Une clé nommée « signature » ne doit pas pouvoir passer pour
« signature valide ».

Deux ajouts au passage, demandés par la section 1 du cahier des charges mais
absents de l'exemple : l'altitude et l'incertitude GPS — cette dernière rendue
`null` quand l'appareil ne l'a pas écrite, jamais comblée — et la valeur exacte
de la vitesse d'obturation à côté de sa forme « 1/200 », car une fraction
arrondie ne se recalcule pas.


## La source : d'un verrou à un relevé

Les outils du Lab exigeaient une source pour chaque grandeur avant de calculer.
La règle a changé, et il vaut la peine de dire pourquoi : **une chaîne saisie
dans un champ n'est pas une source vérifiée.** Rien dans ces outils ne contrôle
qu'une fiche d'ouvrage dit ce qu'on lui fait dire, et l'analyste qui reprend le
dossier refait ce travail de toute façon. Le verrou ne garantissait donc rien ;
il empêchait seulement de calculer.

Ce qui remplace le verrou est plus utile qu'une case cochée :

  · `Plage.source_declaree` dit, pour chaque grandeur, si une provenance a été
    déclarée ;
  · `synthese.sources_manquantes` en fait la liste ;
  · cette liste voyage dans la synthèse exportée, sous
    `traçabilité.sources_manquantes`, accompagnée de l'avertissement qui rappelle
    qu'une source déclarée reste une déclaration ;
  · l'interface l'affiche sous le tableau de bord, en clair.

Ce qui reste refusé n'a pas changé : une valeur hors de sa propre enveloppe, une
grandeur absente, un k que le relevé n'établit pas. Ce sont des incohérences et
des lacunes, pas des formalités.

## Ce qui remplit les champs à votre place

Quatre voies, dans l'outil D. Aucune ne dispense de vérifier : chacune pose une
source qui dit exactement d'où vient la valeur, y compris quand c'est un calcul
ou une valeur nominale.

**L'EXIF adopté d'un geste.** Focale et définition native sont lues du fichier.
La largeur du capteur est en outre DÉDUITE quand l'EXIF porte les deux focales :
36 mm ÷ (f₃₅ ÷ f). La focale équivalente étant arrondie à l'entier par la
plupart des boîtiers, le résultat porte quelques pour-cent d'incertitude — la
source posée avec la valeur le dit.

**Les formats de capteur courants**, du 24×36 au 1/2,3, en un bouton. Ce sont
des dimensions NOMINALES : un « APS-C » varie de 22,2 à 23,7 mm selon le
constructeur, soit quelques pour-cent sur l'angle. La source le dit aussi.

**La distance calculée depuis deux couples de coordonnées**, par la géodésique
de Vincenty du port de l'outil A — jamais recalculée ici. C'est le champ le plus
pénible à sourcer à la main, et le seul des quatre qui se déduise de données que
l'opérateur a déjà. La distance sera exacte si les coordonnées le sont : ce sont
elles qui restent à établir, et la source posée le rappelle.

**La synthèse d'ingestion de l'outil B, reprise telle quelle.** Le flux B → D :
ce qu'un lecteur a déjà lu du fichier remplit l'étalonnage, sans le retaper.
Cela reste déclaratif — l'EXIF s'écrit.
