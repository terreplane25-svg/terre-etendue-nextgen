# Posture éditoriale du dépôt

Ce texte est opposable à tout ce qui est écrit ici : `README.md`, documents de
`docs/`, `outils/README.md`, en-têtes de modules, messages de commit. Il vaut
aussi contre les textes rédigés avec l'aide d'un assistant, y compris quand
celui-ci trouve la formule flatteuse.

Il ne couvre pas les articles du site, qui relèvent de la charte rédactionnelle
de `CLAUDE.md`. Le site s'adresse à quelqu'un qui apprend ; le dépôt s'adresse à
quelqu'un qui vérifie. Ce n'est pas la même personne, et ce n'est pas la même
voix : celle du dépôt est plus sèche.

Validé le 4 septembre 2026.

---

## Le principe qui commande tous les autres

**Le dépôt doit être jugeable par quelqu'un qui rejette toutes ses conclusions.**

Un métrologue, un magistrat, un journaliste d'investigation doivent pouvoir dire
« c'est correctement fait » sans avoir à dire « je suis d'accord ». Une vitrine
qui ne tient que pour un lecteur déjà acquis ne vaut rien.

Corollaire : **on montre le mécanisme, pas le résultat.** La vitrine n'a pas à
convaincre d'une conclusion. Son travail est de rendre la machinerie inspectable
— les seuils, les refus, les contre-épreuves, les commandes à taper pour tout
revérifier.

---

## Les sept principes directeurs

### 1. Ce que ça établit, et ce que ça n'établit pas, vont toujours ensemble

Jamais l'un sans l'autre, jamais le second en petits caractères. C'est déjà la
règle des articles du site (`src/lib/nature-articles.ts`) ; c'est la règle du
dépôt.

### 2. Toute affirmation vérifiable est accompagnée du moyen de la vérifier

Pas « les tests passent » mais la commande qui les fait passer. Pas « le port
est conforme » mais `npm run verifier:ports` et le nombre de contrôles. Un
chiffre sans moyen de contrôle est une opinion mise en forme.

### 3. Les défauts corrigés font partie de la vitrine

Un dépôt qui liste ses propres corrections est plus crédible qu'un dépôt qui
n'en a jamais eu, et c'est la seule manière honnête de montrer qu'un harnais de
test sert à quelque chose. Les défauts se citent avec leur ampleur chiffrée, pas
en termes vagues.

### 4. La provenance avant la valeur

Aucun nombre sans sa source et son incertitude. Le sentinel `indisponible`
s'écrit aussi en prose : un champ inconnu se déclare inconnu, il ne se comble
pas par une valeur plausible.

### 5. L'origine du travail est dite en clair

Ces outils sont nés d'un protocole portant sur une question contestée. Le cacher
serait une omission qu'un lecteur découvrira en dix minutes, et qui détruirait
tout le reste. Le dire est au contraire l'argument le plus fort : *ces outils
refusent de remplir un champ vide parce qu'ils ont été écrits pour une question
où chacun soupçonne l'autre de raisonner à l'envers.*

Cette section vient en tête du `README.md`, pas en note de bas de page.

### 6. La crédibilité vient de la vérifiabilité, jamais de l'auto-description

Pas d'« expert », pas de « référence », pas de « rigoureux » appliqué à soi-même.
Ce sont des jugements que d'autres portent, ou ne portent pas. Le dépôt montre le
travail et se tait sur son propre mérite.

### 7. Le dépôt ne plaide pas

Il ne discute pas les travaux d'autrui, ne répond pas aux objections d'un camp,
ne cite personne pour le corriger. Un outil qui plaide n'est plus un outil.

---

## Le ton

Registre du carnet de laboratoire qui se trouve être lisible. Présent de
l'indicatif, phrases courtes, aucune exclamation.

Le « nous » existe mais reste rare, et jamais pour s'attribuer un mérite :
« nous avons corrigé » oui, « nous avons conçu un système unique » non.

La sécheresse est permise, l'ironie non. L'humour non plus : il se lit comme de
la connivence, et la connivence suppose un camp.

---

## Lexique à proscrire

| À proscrire | Pourquoi | À la place |
|---|---|---|
| prouve, démontre | Aucun de ces outils ne démontre quoi que ce soit | établit, borne, mesure, contrôle |
| la science officielle, la version officielle, on nous cache | Registre conspirationniste — détruit la prétention métrologique en une ligne | *(rien : nommer le fait, pas l'institution)* |
| platistes, globistes, sceptiques, debunkers | Nommer les camps, c'est écrire pour un camp | *(rien)* |
| rigoureux, scientifique, sérieux *(appliqué à soi)* | Un jugement que le lecteur porte, pas l'auteur | *(montrer le contrôle)* |
| révolutionnaire, inédit, unique au monde | Registre publicitaire, invérifiable | *(rien)* |
| il suffit de, simplement, évidemment | Minimise la difficulté du lecteur, et cache souvent une étape | *(détailler l'étape)* |
| environ, à peu près, de l'ordre de | Une incertitude est un nombre | ± valeur, avec son origine |
| nous pensons que, selon nous | Soit c'est établi, soit c'est une hypothèse déclarée | établi par…, hypothèse : … |
| état de l'art, best-in-class, propulsé par | Marketing, et se démode en un an | *(rien)* |
| emojis dans les titres | Déjà proscrit par la charte du site | *(rien)* |

---

## Lexique recommandé

| Terme | Ce qu'il porte |
|---|---|
| **établit / n'établit pas** | Le couple, toujours ensemble |
| **indisponible** | Le sentinel, en prose comme en code |
| **déposé avant, daté du** | L'antériorité de l'engagement |
| **contre-épreuve** | Un contrôle par un moyen indépendant |
| **épinglé** | Deux implémentations liées par un test |
| **refuse, écarte, lève** | Un outil qui refuse est une fonctionnalité, pas une panne |
| **enveloppe** | Jamais une valeur centrale seule |
| **indéterminé** | Ni pour, ni contre — et ce n'est pas un échec |
| **vérifiable par** | Suivi de la commande exacte |
| **recalculé à chaque génération** | Rien n'est figé à la main |

---

## L'ordre de la vitrine

Une vitrine est une hiérarchie. **Ce que le dépôt refuse de faire vient avant ce
qu'il fait.** C'est contre-intuitif et c'est le meilleur filtre : le lecteur qui
cherche une confirmation part, celui qui cherche une méthode reste.

Puis, dans l'ordre :

1. L'origine du travail, dite en clair.
2. La commande qui vérifie tout.
3. Les chiffres de couverture, avec ce qu'ils signifient.
4. Les outils.
5. Les défauts trouvés et corrigés.
6. Ce qui reste ouvert ou non fait.

---

## Signature et langue

**Signature.** Les outils métrologiques et le dépôt sont signés **Jetmir**. Le
nom du projet — Terre Étendue — reste attaché au protocole. Un tribunal mandate
une personne, pas un site ; un protocole engage un projet.

**Langue.** Le français d'abord, et lui seul jusqu'à ce qu'il soit irréprochable.
Un `README.en.md` viendra ensuite. Pas les deux en même temps, sous peine de les
voir diverger — c'est le défaut que ce dépôt passe son temps à combattre
ailleurs, il n'y a pas de raison de l'introduire ici.

---

## Le test de relecture

Cinq questions auxquelles un lecteur pressé doit pouvoir répondre en une minute,
sans faire défiler :

1. Qu'est-ce que ce dépôt établit, et qu'est-ce qu'il n'établit pas ?
2. Comment je vérifie moi-même que ce qui est annoncé est vrai ?
3. Qu'est-ce qui a été trouvé faux ici, et corrigé ?
4. D'où vient ce travail, et pour quelle question ?
5. Qu'est-ce qui reste ouvert ou non fait ?

Si une seule reste sans réponse, la vitrine est à reprendre.
