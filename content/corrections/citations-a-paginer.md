# Les vingt-trois citations qui restent à localiser

**Règle** : une référence est localisée si elle permet de retrouver le passage
sans lire l'ouvrage entier — pagination, subdivision numérotée ou nommée,
numéro de recueil, référence scripturaire, identifiant, ou date individuant le
document. Le seul titre d'un ouvrage n'en est pas une.

**Règle absolue** : ne jamais inventer une pagination. En cas de doute, retirer
la citation plutôt que la sourcer approximativement. Une référence fausse est
pire qu'une référence absente, parce qu'elle a l'air vérifiable.

Chacune de ces vingt-trois citations porte, dans son pied, la mention
*(à paginer)*. Le marqueur est posé et retiré automatiquement par
`scripts/localiser-citations-occidentales.py` ; il disparaît de lui-même dès
qu'une localisation est ajoutée. Le relevé se refait avec
`python3 scripts/lister-citations-a-localiser.py`.

**État** : 193 citations attribuées, 23 sans localisation — 12 %. Le relevé
précédent en annonçait 43 : douze étaient des faux positifs du détecteur, et
huit ont reçu leur localisation.

---

## 1. Doutes à lever en priorité — l'attribution elle-même est en cause

Ces trois-là ne sont pas de simples paginations manquantes. Tant qu'elles ne
sont pas levées, l'attribution n'est pas sûre.

### « Lee, 2005 » — `la-rotation-terrestre-experiences-preuves-verdict`

> « Le plan du pendule de Foucault ne reste, en tout état de cause, qu'une hypothèse. »

Un nom de famille et une année. Ni titre, ni revue, ni éditeur. En l'état, la
citation est invérifiable par n'importe quel lecteur. **Si la référence
complète n'est pas retrouvée, la règle du site impose de retirer la citation**,
pas de la laisser marquée indéfiniment.

### Poincaré cité trois fois — deux passages, un seul ouvrage allégué

Trois citations renvoient à *La Science et l'Hypothèse* (1902) :

| Article | Passage |
|---|---|
| `la-gravite-70-theories-et-aucune-preuve` | « Ces deux propositions, "la Terre tourne" et "il est plus commode de supposer que la Terre tourne", ont un seul et même sens » |
| `pourquoi-tout-remettre-en-question` | le même passage |
| `la-rotation-terrestre-experiences-preuves-verdict` | « Cette affirmation : "la Terre tourne", n'a aucun sens » |

Le premier passage est bien de *La Science et l'Hypothèse*. **Le second est à
vérifier** : cette formule circule aussi comme venant de *La Valeur de la
Science* (1905) ou de *Science et Méthode* (1908), et nous n'avons pas pu
trancher. Il faut identifier l'ouvrage avant la page. Une fois le premier
passage localisé, la référence vaut pour deux articles.

### « — Edwin Hubble », sans ouvrage — `chronologie-critique-du-modele-globe`

> « Une telle condition impliquerait que nous occupions une position unique dans l'univers, analogue à… »

Le pied ne nomme aucun ouvrage : c'est plus grave qu'une pagination manquante.
Le passage vient vraisemblablement de *The Observational Approach to Cosmology*
(Oxford, 1937), déjà cité dans deux autres articles, mais **nous ne l'avons pas
vérifié** et ne l'écrirons pas avant de l'avoir fait.

## 2. Faciles — une URL suffit, pas une page

Ce sont des ressources en ligne : la localisation attendue est un lien direct,
consulté et daté.

| Article | Référence | À faire |
|---|---|---|
| `vols-avion-et-courbure-terrestre` | AOPA, *Autopilot Basics* | URL de l'article, date de consultation |
| `vols-avion-et-courbure-terrestre` | Flight Safety Foundation, *Upset by a False Cue* | Numéro et date d'*AeroSafety World*, ou URL du PDF |
| `neptune-et-pluton-les-faux-triomphes` | JHU Applied Physics Laboratory, matériaux éducatifs New Horizons | URL de la page, date de consultation |
| `mesures-sous-le-ciel-trigonometrie-plane` | Henning Umland, *A Short Guide to Celestial Navigation* (2015) | Le PDF est libre et paginé : chapitre et page |

## 3. Ouvrages occidentaux — pagination à relever, volume en main

| Article | Référence | Remarque |
|---|---|---|
| `lenigme-de-la-terre-immobile` | E.T. Whittaker, *A History of the Theories of Aether and Electricity* | Deux volumes ; préciser lequel avant la page |
| `pourquoi-tout-remettre-en-question` | James Woodward, *Making Things Happen*, 2003 | La définition manipulationniste de la cause |
| `pourquoi-tout-remettre-en-question` | Ian Hacking, *Representing and Intervening*, 1983 | « Si vous pouvez les pulvériser, c'est qu'ils sont réels » — la formule apparaît à deux endroits du livre, choisir celui qui porte l'argument |
| `pourquoi-tout-remettre-en-question` | Ernst Mach, *La Mécanique* (1883) | Équivalence Ptolémée / Copernic, dans la critique du seau de Newton |
| `pourquoi-tout-remettre-en-question` · `les-distances-cosmiques-au-dela-de-la-regle` | Edwin Hubble, *The Observational Approach to Cosmology*, 1937 | Même passage dans les deux articles : une seule vérification |
| `les-marees-contre-lheliocentrisme` | Robert Bennett, *The Geocentric Testimony of Our Tides* | Vérifier aussi le statut de la publication |

## 4. Sources islamiques — cinq références à compléter

| Article | Référence | Ce qu'il faut |
|---|---|---|
| `dhu-al-qarnayn-…` | *Sunan Abī Dāwūd*, « authentique » | Le numéro du hadith. L'article en cite un autre avec son numéro (4002) : celui-ci est resté sans. |
| `dhu-al-qarnayn-…` | Umayya ibn Abī al-Ṣalt | Référence au *dīwān* — édition et numéro de pièce |
| `dune-terre-plate-universelle-a-la-sphere-grecque` | Ibn Taymiyya, *Darʾ Taʿāruḍ al-ʿAql wa-l-Naql* | Volume et page. L'article `le-concordisme` donne déjà 1/120, 1/152, 1/154 et 7/285 pour d'autres passages du même ouvrage : vérifier si celui-ci en fait partie. |
| `le-consensus-sur-la-sphericite` | Ibn Taymiyya, *Bayān Talbīs al-Jahmiyya* | Volume et page, édition Ibn Qāsim |
| `ou-est-allah-le-uluww-et-la-forme-du-monde` | Mālik, l'*istiwāʾ*, rapporté par al-Bayhaqī et al-Lālakāʾī | Numéro dans *al-Asmāʾ wa-l-Ṣifāt* et dans *Sharḥ Uṣūl Iʿtiqād*. Les autres citations du même article portent leur numéro ; celle-ci, la plus célèbre, ne l'a pas. |
| `pres-de-cent-savants-de-lislam` | Ibn Rajab al-Ḥanbalī, *Ar-Radd* | Titre complet de l'ouvrage, puis page |

Les cinq références islamiques sont les plus accessibles : shamela.ws porte
*al-Asmāʾ wa-l-Ṣifāt*, *Sharḥ Uṣūl Iʿtiqād*, le *Darʾ Taʿāruḍ* et le *Bayān
Talbīs*, avec la pagination de l'édition imprimée.
