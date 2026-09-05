# terre-etendue-nextgen

Un protocole de mesure optique à longue distance, les outils qui l'exécutent,
et le site qui les publie.

Ce fichier suit la posture éditoriale fixée dans
[`docs/posture-editoriale.md`](docs/posture-editoriale.md), qui lui est
opposable.

---

## Ce que ce dépôt refuse de faire

C'est ce qui vient en premier, parce que c'est ce qui distingue un instrument
d'un argument.

**Aucun outil ici ne conclut sur la forme de la Terre.** La condition de
discrimination du §28.2 dit si une configuration d'observation permettrait de
séparer deux prédictions — c'est un préalable géométrique. Chaque résultat
affiché le rappelle en toutes lettres.

**Aucun champ vide n'est comblé.** Une coordonnée, une altitude, une hauteur
non renseignée reste `indisponible`. Le code refuse de produire une fiche
plutôt que d'inventer une valeur plausible. Ce refus est testé — il existe des
tests dont le succès consiste à obtenir une erreur.

**Aucune donnée de relief n'est interpolée.** Le pré-écran altimétrique
interroge l'API IGN ou ne rend rien. Il ne génère jamais un profil crédible à
la place.

**Aucun nombre sans sa source.** Toute coordonnée et toute hauteur saisie dans
les outils du Lab exige un champ de provenance, affiché avec le résultat.

**Aucune valeur centrale seule.** Les prédictions sortent en enveloppes, avec
les bornes du coefficient de réfraction qui les produisent.

**Le verdict `indéterminé` est un résultat.** Quand les enveloppes se
recouvrent, l'observation ne tranche pas, et c'est ce qui est écrit. Ce n'est
pas un échec de l'outil.

---

## 1. D'où vient ce travail

Ces outils sont nés d'un protocole d'observation portant sur une question
contestée : quelle portion d'une cible éloignée reste visible au-dessus de la
mer, et quel modèle de la surface terrestre rend compte de la mesure.

C'est dit ici, en tête, et non en note. C'est aussi l'argument le plus fort du
dépôt : **ces outils refusent de remplir un champ vide parce qu'ils ont été
écrits pour une question où chacun soupçonne l'autre de raisonner à l'envers.**
Un logiciel de mesure écrit dans ce contexte n'a aucune marge : la première
valeur silencieusement complétée, le premier seuil ajusté après coup, et tout
le reste tombe.

Le protocole lui-même — 35 sections, 38 pages — est publié en PDF :
[`public/protocoles/Protocole-visibilite-cible-eloignee.pdf`](public/protocoles/Protocole-visibilite-cible-eloignee.pdf).
Il est régénéré par `scripts/generer-protocole-visibilite.py`, dont la fonction
`controle()` recalcule chaque valeur imprimée et refuse d'écrire le document en
cas d'écart.

---

## 2. La commande qui vérifie

Rien de ce qui suit n'a besoin d'être cru.

    # Les quatre paquets Python, qui font référence
    python3 -m venv outils/.venv
    outils/.venv/bin/pip install pytest numpy scipy Pillow PyWavelets
    outils/.venv/bin/pip install -e outils/outil-A-visee-optique \
                                 -e outils/outil-B-preuve-image \
                                 -e outils/outil-C-rapport-expertise \
                                 -e outils/outil-D-metrologie-image

    cd outils/outil-A-visee-optique     && ../.venv/bin/python -m pytest -q   # 321
    cd outils/outil-B-preuve-image      && ../.venv/bin/python -m pytest -q   # 137
    cd outils/outil-C-rapport-expertise && ../.venv/bin/python -m pytest -q   #  42
    cd outils/outil-D-metrologie-image  && ../.venv/bin/python -m pytest -q   #  99

    # Les quatre ports TypeScript, épinglés au Python
    npm run verifier:ports

    # Les quatre cas d'étude, de bout en bout
    cd outils/exemples-cas-etudes/cas-chassiron && ../../.venv/bin/python run_case.py

    # L'outil d'analyse d'image, piloté dans un vrai navigateur
    npm run essai:metrologie

    # Ce que les outils font sur un téléphone : mise en page, tactile, durées
    npm run audit:mobile

    # Le site
    npx next build

`npm run verifier:ports` recompile les quatre `noyau.ts` avec le `tsc` du
projet, rejoue les vecteurs d'or produits par le Python et compare. Il imprime
le nombre de contrôles passés et la date de génération des vecteurs.

`npm run essai:metrologie` fait autre chose, et c'est délibéré : il construit le
site, le sert, et pilote un vrai navigateur sur une image dont la scène est
connue d'avance. Les vecteurs épinglent les formules ; cet essai vérifie le
câblage — chargement du fichier, empreinte, EXIF, clics sur le canevas, tableau
de bord, exports — et fait juger le résultat du navigateur par le paquet Python,
à partir des pointés réellement enregistrés.

---

## 3. Les chiffres, et ce qu'ils signifient

| Grandeur | Valeur | Ce que ça veut dire |
|---|---|---|
| Tests Python | **599** | 321 + 137 + 42 + 99, exécutés par les commandes ci-dessus |
| Vecteurs d'or | **188** | 61 + 26 + 22 + 79 entrées produites par le Python, rejouées par le TypeScript |
| Contrôles de port | **1 318** | 263 + 152 + 117 + 786 comparaisons Python ↔ TypeScript |
| Cas d'étude | **4** | Chassiron↔Cordouan (invalidé), La Coubre↔Cordouan, Garoupe↔Monte Cinto, Sangatte↔South Foreland |
| Sections du protocole | **35** | 38 pages, valeurs recalculées à chaque génération |

Ce que ces chiffres n'établissent pas : qu'une formule soit la bonne. Un test
prouve qu'une implémentation fait ce qu'on lui a demandé, pas que la demande
était juste. Les deux contrôles qui échappent à cette limite sont dans
`outils/outil-A-visee-optique/tests/test_vincenty.py` : ils confrontent Vincenty
à des résultats obtenus **sans** elle — la distance sur l'équateur, qui vaut
analytiquement `a·Δλ`, et l'arc méridien, obtenu par quadrature de Simpson.

---

## 4. Les outils

Les paquets Python sont la référence. Les ports TypeScript existent parce que
le navigateur ne fait pas tourner de Python ; ils ne font pas autorité et
chacun le déclare dans son en-tête.

| Outil | Paquet de référence | Port navigateur | Page |
|---|---|---|---|
| A — visée optique | `outils/outil-A-visee-optique` | `src/lib/visee-optique/noyau.ts` | Lab, calculateur |
| B — preuve image | `outils/outil-B-preuve-image` | `src/lib/preuve-image/noyau.ts` | Lab, vérificateur d'intégrité |
| C — rapport d'expertise | `outils/outil-C-rapport-expertise` | `src/lib/rapport-expertise/noyau.ts` | Lab, générateur de fiche |
| D — métrologie d'image | `outils/outil-D-metrologie-image` | `src/lib/metrologie-image/noyau.ts` | Lab, analyse d'image |

**A** — géodésique de Vincenty sur GRS80, rayon d'Euler, hauteur cachée,
enveloppes de réfraction, condition de discrimination §28.2.
**B** — empreinte SHA-256, lecture EXIF/GPS, chaîne de détention ISO/IEC 27037.
**C** — fiche d'observation §33 et arborescence d'archive §34, en ZIP sans
compression pour qu'une empreinte de fichier soit la même dans l'archive et
hors d'elle.
**D** — trois pointés sur une photographie, étalonnage angulaire depuis la
définition native du capteur, inversion de l'angle en coefficient de réfraction
effectif. Il n'écrit un k que lorsque le relevé en détermine un ; sinon il
écrit `indisponible` et dit laquelle des trois branches il a rencontrée.

Toute correction de formule se fait dans le Python d'abord, se répercute
ensuite dans le port, et les vecteurs sont régénérés. Jamais l'inverse.

Détail dans [`outils/README.md`](outils/README.md).

---

## 5. Ce qui a été trouvé faux, et corrigé

Ces défauts sont ici parce qu'un harnais de test qui n'a jamais rien attrapé ne
prouve rien.

**Équations générales du protocole (§9.2, §9.3).** L'altitude de base `z_b` se
trouvait dans l'argument de la sécante, et `D_crit` valait `s(h)` au lieu de
`s(h) + s(z_b)`. Pour une base à 20 m : de 55 à 147 m d'erreur. L'exemple
numérique imprimé (base au niveau de la mer) et le code n'étaient pas touchés —
seul un tiers reproduisant depuis les équations imprimées aurait été égaré.
`controle()` vérifie désormais que `c = 0` en `D_crit` et `c = H` en `D_lim`
pour une base élevée.

**Bornes du rayon de courbure.** Le document imprimait « 6 335 km à 6 378 km ».
6 378 km est la grande normale à l'équateur, pas le maximum : au pôle elle vaut
6 399,6 km. L'écart réel est de 64,2 km, soit 1,01 %, et non « plus de 40 km,
soit 0,6 % ». Les gradients de la table 8 sont maintenant calculés depuis les
bornes de `k` au lieu d'être recopiés.

**`azimut_2_vers_1`, dans cinq copies.** Le nom annonce le gisement de retour ;
la formule rend α₂, l'azimut au point d'arrivée. Sur l'équateur, cap à l'est,
elle donne 90° sous un nom qui promet 270°. Aucun appelant ne s'en servait, ce
qui explique que personne ne l'ait vu. Renommé `azimut_arrivee_deg`.

**Cinq copies de Vincenty hors couverture.** La géodésique inverse vivait en
cinq exemplaires hors du paquet, aucun testé, alors qu'elle produit le `D` et
l'azimut dont dépend toute la géométrie. 475 lignes supprimées ; une seule
implémentation subsiste, avec 26 tests.

**Écriture EXIF en type TIFF 12.** Pillow encode un flottant nu en DOUBLE, que
la norme EXIF n'emploie pas pour `FocalLength`, `FNumber` ni `ExposureTime`.
Notre lecteur rendait alors les octets bruts, ce qui était le comportement
correct : c'est l'écriture qui était fautive. Le défaut n'est apparu que parce
que deux implémentations indépendantes se rencontraient.

**Comparaison d'en-tête EXIF dans le port.** Le port comparait une chaîne
décodée à `Exif` suivi de deux espaces, alors que l'en-tête porte deux octets
nuls. Remplacé par une comparaison octet par octet.

**Les quatre harnais eux-mêmes ont été éprouvés en cassant volontairement le
port** : un tag EXIF décalé d'un cran, le signe de l'hémisphère sud oublié,
l'arc de tangence biaisé de 10⁻⁷, un champ retiré d'un bloc de fiche, deux
répertoires d'archive intervertis, le pas pixel pris sur la largeur du fichier
livré au lieu du capteur, le point principal supposé au centre du recadrage, un
relevé nul inversé au lieu d'être majoré. Chacune des huit cassures est
détectée et nommée. Une neuvième ne l'est pas et ne doit pas l'être — `atan2`
remplacé par `atan` du quotient ne change rien sur le domaine admissible : le
commentaire qui affirmait le contraire a été corrigé, pas le code.

**Export d'audit arrondi au centième de pixel.** La synthèse JSON de l'outil D
arrondissait les ordonnées des pointés ; sur la visée d'essai, cet arrondi
déplace k de 8·10⁻⁵. Un fichier d'audit dont on ne peut pas refaire le calcul
ne remplit pas son office. Défaut trouvé par l'essai de bout en bout, en
confrontant l'export au paquet Python.

**Six défauts du cahier des charges de l'outil D**, dont trois qui changent un
résultat : l'écart horizon / bas visible tenu pour une « hauteur masquée par la
courbure » alors qu'il est nul par construction ; le pas pixel calculé sur la
largeur du fichier livré, ce qui donne un angle quatre fois trop grand sur une
image recadrée de 6000 à 1500 px ; et une inversion de k supposée toujours
avoir une solution, alors qu'une cible entière ou entièrement occultée n'en
détermine aucune. Détail dans [`outils/README.md`](outils/README.md).

**Chemins codés en dur.** Les quatre cas d'étude commençaient par trois
`sys.path.insert` vers `/home/claude/...`, qui ne pouvaient jamais aider :
inutiles quand les paquets sont installés, insuffisants sinon. Remplacés par une
résolution relative au fichier. Les quatre cas tournent maintenant sans
préparation.

---

## 6. Ce qui reste ouvert

**Le pré-écran altimétrique n'est pas intégré au site.** Il exige un accès
réseau serveur vers l'API IGN. Tant qu'il n'y en a pas, il reste un script
autonome : il n'est pas question de lui substituer un profil de relief calculé.

**`README.en.md` n'existe pas.** Le français d'abord, et lui seul jusqu'à ce
qu'il soit irréprochable ; deux versions maintenues en parallèle divergent, et
c'est précisément le défaut que ce dépôt combat ailleurs.

**Aucune campagne d'observation réelle n'a encore été menée sous ce protocole.**
Les quatre cas d'étude s'appuient sur des coordonnées sourcées et une image de
démonstration qui est un diagramme calculé, jamais une photographie. Le dépôt
fournit l'instrument ; il ne fournit pas de mesure.

**Cibles tactiles sous 44 px.** Les champs de saisie des outils A, B et C font
31 px de haut, dimensionnés pour une souris. L'outil D a été corrigé ; les
autres suivent une convention du site qu'il faudrait reprendre d'un bloc plutôt
qu'outil par outil. `npm run audit:mobile` compte les cibles concernées.

**Pas de licence.** À déterminer.

---

## Structure

    content/articles/       54 articles, un JSON par article — source unique
    docs/                   posture éditoriale
    outils/                 les quatre paquets Python, le pré-écran, les cas d'étude
    public/protocoles/      le protocole en PDF
    scripts/                85 générateurs, vérificateurs et essais
    src/lib/{visee-optique,preuve-image,rapport-expertise,metrologie-image}/  les ports et leurs vecteurs
    src/components/lab/     les outils du navigateur

Les conventions de rédaction du site — régime de preuve, gradation des sources,
identité par pilier — sont dans [`CLAUDE.md`](CLAUDE.md).

---

Dépôt et outils métrologiques : **Jetmir**.
Le protocole reste attaché au projet Terre Étendue.
