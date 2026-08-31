# Couvertures 1200×630 — ce qui manque, et ce que chaque image doit montrer

**Règle** (charte, section « Images & médias ») : 1200 × 630 px minimum, format
paysage voisin de 1,91:1, JPEG de moins de 1 Mo. Jamais de carré 1024×1024,
jamais de logo ni de schéma comme visuel principal — en dessous de 1200 px de
large, Google Discover retire la grande carte et l'article perd sa vignette
pleine largeur.

**Vérification** : `python3 scripts/auditer-couvertures.py` lit les dimensions
réelles dans l'en-tête de chaque fichier et signale tout ce qui échoue. À
lancer depuis une machine qui atteint Hostinger et Unsplash.

**État au 6 août 2026** — 59 articles, aucun sur l'image de repli.
13 articles partagent une couverture avec un autre article ; 7 articles de fond
sont sur une photographie Unsplash générique ; 5 pages d'appareil (glossaire,
index, corrections, standards, état des lieux) sont hors priorité, leur vocation
n'étant pas d'être partagées.

---

## Priorité 1 — les treize couvertures partagées

Deux articles qui portent la même image se cannibalisent dans les partages et
dans Discover : la deuxième carte semble un doublon de la première.

| Article | Pilier | Image actuelle | Ce que la nouvelle image doit montrer |
|---|---|---|---|
| `debut-de-la-creation-selon-le-coran-et-la-sunna` | Bibliothèque | `mer_horizon.png` (partagée) | Ciel nocturne très sombre au-dessus d'une eau immobile, avant l'aube. Aucun repère humain, aucune construction — l'article traite de ce qui précède la création. |
| `mesurer-la-courbure-sur-l-eau-cinq-campagnes` | Observatoire | `mer_horizon.png` | **Garde l'image**, recadrée en 1200×630 paysage. |
| `leau-ne-ment-pas` | Expériences | `mer_horizon-e178…png` (partagée) | Surface d'un plan d'eau parfaitement calme, prise au ras de l'eau, la rive opposée à peine discernable dans la brume. |
| `monter-l-experience-des-trois-mires` | Expériences | `mer_horizon-e178…png` | Une perche graduée plantée dans l'eau peu profonde au premier plan, l'étendue d'eau derrière. C'est le dispositif de l'article. |
| `le-consensus-sur-la-sphericite` | Bibliothèque | `Ibn_Taymiyyah.jpg` | **Garde l'image**, recadrée en 1200×630 paysage. |
| `la-mobilite-de-la-terre-attribuee-a-ibn-taymiyyah` | Bibliothèque | `Ibn_Taymiyyah.jpg` (partagée) | Gros plan sur un folio manuscrit arabe en lumière rasante, l'encre et le grain du papier bien lisibles. L'article porte sur **un mot** : le cadrage doit être serré, pas un plan de bibliothèque. |
| `la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre` | Observatoire | `lune_soleil_etoile.png` | **Garde l'image**, recadrée en 1200×630. |
| `ou-est-allah-le-uluww-et-la-forme-du-monde` | Bibliothèque | `lune_soleil_etoile.png` (partagée) | Ciel nocturne en contre-plongée — la voûte occupant tout le cadre, une ligne d'horizon basse et sombre en bas. Le sujet est la direction du haut. |
| `dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne` | Bibliothèque | Unsplash (partagée) | Coucher de soleil sur une étendue d'eau trouble vue depuis un rivage bas, lumière rasante orangée — l'image du verset S18 V86, « une source boueuse ». |
| `mise-en-garde-la-kaaba-et-saturne` | Bibliothèque | Unsplash (partagée) | La Kaaba de nuit, vue de haut, le ṭawāf en cours. Sobre, aucune surimpression ni montage : l'article met en garde contre les rapprochements symboliques, il ne doit pas en fabriquer un. |
| `sources-historiques-fonds-documentaire` | Bibliothèque | Unsplash (partagée) | Rayonnage de reliures anciennes pris en enfilade, faible profondeur de champ. |
| `un-traite-ottoman-contre-la-sphericite-1314h` | Bibliothèque | Unsplash (partagée) | **À terme : un folio de la Risāla elle-même** (Bibliothèque du Roi Abd al-Aziz, collection al-Mahmūdiyya, cote 3.1.13) — les folios 4-5, 7 et 8 sont déjà demandés pour l'article. En attendant, un manuscrit ottoman en écriture naskhī-taʿlīq, plan large. |

## Priorité 2 — les sept articles de fond sur photographie générique

Ces images ne sont pas fautives : `getArticleOgImage` les agrandit déjà en
1200×630 pour le partage. Elles sont seulement interchangeables — la même photo
pourrait illustrer n'importe quel article de n'importe quel site.

| Article | Pilier | Ce que la nouvelle image doit montrer |
|---|---|---|
| `la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas` | Observatoire | Pleine lune au téléobjectif, très détaillée, décentrée à gauche du cadre sur fond noir — le format paysage impose de ne pas la centrer. |
| `la-qibla-et-la-direction-cote-ouest` | Bibliothèque | Un miḥrāb en lumière rasante, ou une boussole de qibla ancienne. |
| `levolution-et-lislam` | Bibliothèque | Sobre : une page de traité, ou une strate géologique. Éviter le cliché du primate, qui caricature le débat au lieu de l'ouvrir. |
| `loeil-humain-la-machine-a-voir` | Expériences | Macro d'un iris humain, cadré à droite du format paysage. |

## Priorité 3 — les cinq pages d'appareil

`glossaire`, `index-thematique`, `corrections`, `standards-et-methode`,
`etat-des-lieux-ou-en-sommes-nous`. Ces pages ne sont pas destinées au partage
social ni à Discover. Leur couverture actuelle convient ; deux d'entre elles
partagent une image, ce qui est sans conséquence ici.

---

## Où déposer les fichiers

Base Hostinger : `https://green-gnat-134443.hostingersite.com/wp-content/uploads`

Téléverser en **1200 px de large au minimum** : les fichiers Hostinger sont
servis tels quels, sans redimensionnement, contrairement aux vignettes Unsplash
que `getArticleOgImage` agrandit à la volée.

Puis reporter chaque URL dans `src/lib/article-images.ts` — la clé est le slug
de l'article — et relancer `python3 scripts/auditer-couvertures.py` pour
confirmer que les dimensions et le poids sont conformes.
