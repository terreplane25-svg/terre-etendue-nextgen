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
    cd outils/outil-B-preuve-image      && ../.venv/bin/python -m pytest -q   # 263
    cd outils/outil-C-rapport-expertise && ../.venv/bin/python -m pytest -q   #  42
    cd outils/outil-D-metrologie-image  && ../.venv/bin/python -m pytest -q   # 102

Et, pour l'outil D, un essai qui pilote un vrai navigateur — les vecteurs
épinglent les formules, celui-ci vérifie le câblage :

    npm run essai:metrologie

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
