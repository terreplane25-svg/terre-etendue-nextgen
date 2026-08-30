# Dépôt — préenregistrement du protocole de dépression de l'horizon

**Ce dossier est vide de PDF, et c'est normal.** Il attend le DOI.

Depuis la version 1.6, le protocole porte un **emplacement réservé** pour son
propre DOI, en première page et en section 13. Les fichiers à déposer ne sont
donc produits qu'une fois le DOI connu — et Zenodo comme OSF le donnent *avant*
publication. C'est `scripts/inscrire-doi.py` qui remplit ce dossier.

## La marche à suivre

### 1. Réserver le DOI, sans publier

Sur <https://zenodo.org> : **New upload**, puis le bouton **Reserve DOI** dans
le champ « Digital Object Identifier ». Zenodo attribue le DOI immédiatement.
L'enregistrement reste un brouillon tant qu'on ne clique pas sur *Publish*.

Sur <https://osf.io>, la même chose passe par la création d'un projet puis
« Create DOI ».

Le DOI ressemble à `10.5281/zenodo.1234567` chez Zenodo, à
`10.17605/OSF.IO/ABCDE` chez OSF.

### 2. L'inscrire, et produire les fichiers

```bash
python3 scripts/inscrire-doi.py 10.5281/zenodo.1234567
```

Le script remplace le marqueur aux **quatre** emplacements — deux par langue —
regénère les deux PDF, les copie ici, calcule les empreintes SHA-256 et écrit
`SHA256SUMS.txt`.

Il refuse de travailler s'il ne trouve pas exactement quatre marqueurs, et
refuse d'être relancé une fois le DOI inscrit. Un DOI recopié à la main dans
trois emplacements sur quatre ne se verrait qu'après publication, c'est-à-dire
trop tard.

### 3. Téléverser, et seulement alors publier

- Les **deux** PDF dans le **même** enregistrement — celui dont le DOI vient
  d'être réservé. Un seul enregistrement, un seul DOI : le DOI porte sur
  l'enregistrement, pas sur chaque fichier. Deux dépôts séparés feraient de ces
  deux traductions deux travaux distincts.
- Le contenu de `SHA256SUMS.txt` dans le champ **Additional notes**.
- Les métadonnées ci-dessous.
- Puis **Publish**. Le DOI devient permanent à cet instant.

### 4. Ne commencer à collecter qu'ensuite

C'est le seul point qui ne se rattrape pas.

### 5. Mettre les fichiers en ligne sur le site

Copier les PDF de ce dossier — **ceux-là exactement**, pas des rendus refaits —
dans `public/protocoles/`, puis ajouter les liens de téléchargement et le DOI
dans la section 07 de l'article
`content/articles/les-protocoles-ce-que-c-est-et-pourquoi.json`, où la page
explique aujourd'hui pourquoi ils n'y sont pas encore.

Un rendu refait a une autre empreinte : servir un fichier dont le SHA-256 ne
correspond pas à celui annoncé sur le dépôt annule l'intérêt de tout le
dispositif.

## Pourquoi le DOI peut être dans le fichier et pas l'empreinte

Le DOI est attribué avant publication : il peut donc entrer dans le document,
qui est ensuite figé puis haché. L'empreinte, elle, se calcule **sur** le
fichier fini — l'y inscrire le modifierait, donc la fausserait. Elle vit
nécessairement à l'extérieur : dans les notes de l'enregistrement, et partout
où le protocole est annoncé.

## Pourquoi ces PDF seront versionnés, contrairement à tous les autres

Le `.gitignore` du projet exclut `*.pdf`, au motif documenté qu'ils se
régénèrent en quelques secondes. C'est vrai en général et **faux ici**, pour une
raison vérifiée et non supposée : le rendu n'est **pas reproductible octet à
octet**. Chromium inscrit un horodatage de création dans le PDF, si bien que deux
rendus successifs de la même source inchangée donnent deux empreintes
différentes. Contrôle fait le 26 août 2026 sur `horizon-fr.html` inchangé :

```
df2054a1a7bccf70005361a42a52e2017b8050dcb76141f0d82e35790afdc778
44039709cb3c10d523a22a519c0482a7d7ef140c81dccf8cd9c64995394cbb5c
```

Conséquence directe : **l'empreinte ne peut pas être recalculée depuis les
sources**. Elle ne vaut que pour l'exemplaire exact déposé, et si cet exemplaire
est perdu le préenregistrement devient invérifiable — ce qu'il est précisément
censé empêcher.

Les fichiers écrits ici par le script seront donc commités, en dérogation
assumée à la règle du projet. **Ne pas les regénérer, ne pas les remplacer.**
S'il faut corriger le protocole, c'est une nouvelle version qui se dépose, avec
son propre DOI et ses propres empreintes ; celle-ci reste en place.

## Une objection à écarter d'avance

L'inscription du DOI ne change pas le numéro de version : elle remplit un
emplacement ouvert à cet effet. Il s'ensuit que **la version 1.9 n'existe
publiquement que sous sa forme portant le DOI**. L'exemplaire à emplacement vide
est un état intermédiaire de travail et ne doit pas circuler : deux fichiers
distincts se réclamant du même numéro de version seraient exactement le genre
d'ambiguïté que ce dispositif existe pour écarter.

Concrètement : ne diffuser aucun PDF de la 1.9 avant d'avoir passé le script.

## Métadonnées du dépôt

**Titre**
> Measuring the dip of the sea horizon as a function of altitude — an open,
> pre-registered protocol (FR/EN)

**Type** — Zenodo : *Publication* → *Preprint*. OSF : *Preprint*, ou *Project*
avec registration.

**Description**

> Protocole ouvert et préenregistré pour la mesure de la dépression de l'horizon
> marin en fonction de l'altitude. L'observable est l'angle δ entre l'horizontale
> définie par le fil à plomb et la ligne d'horizon marin. Une surface sphérique
> prédit δ = √(2h/R′) ; une surface plane prédit δ = 0 à toute altitude.
>
> L'intérêt métrologique de cette observable tient à ce que la réfraction
> atmosphérique n'y intervient qu'au second ordre : sur toute la plage
> physiquement défendable du coefficient de réfraction (0 ≤ k ≤ 0,47), la
> prédiction sphérique ne varie que de 107′ à 78′ depuis 3 107 m d'altitude.
> L'écart entre les deux modèles vaut donc au minimum 78 minutes d'arc, pour un
> budget d'erreur instrumental de 2,2′ à 1 σ.
>
> Le document énonce ses deux prédictions sous forme falsifiable avant toute
> acquisition, fixe ses critères de décision a priori, donne l'ordre des
> opérations en six phases en signalant celles qui sont irréversibles, détaille
> son budget d'erreur poste par poste, et énonce les données à transmettre
> quelle que soit l'issue.
>
> Ce dépôt contient la version 1.9 en français et en anglais. Les deux fichiers
> ont le même contenu.
>
> ---
>
> Open, pre-registered protocol for measuring the dip of the sea horizon as a
> function of altitude. The observable is the angle δ between the plumb-line
> horizontal and the sea horizon line. A spherical surface predicts
> δ = √(2h/R′); a plane surface predicts δ = 0 at every altitude.
>
> The metrological value of this observable is that atmospheric refraction enters
> only at second order: over the whole physically defensible range of the
> refraction coefficient (0 ≤ k ≤ 0.47), the spherical prediction varies only
> from 107′ to 78′ from 3 107 m. The gap between the two models is therefore at
> least 78 arcminutes, against an instrumental error budget of 2.2′ at 1 σ.
>
> The document states both predictions in falsifiable form before any
> acquisition, fixes its decision criteria a priori, gives the order of
> operations in six phases while flagging the irreversible ones, details its
> error budget item by item, and states the data to be transmitted whatever the
> outcome.
>
> This deposit holds version 1.9 in French and English. The two files have the
> same content.

**Mots-clés** — `dip of the horizon`, `horizon dip`, `atmospheric refraction`,
`geodesy`, `pre-registration`, `open protocol`, `artificial horizon`,
`error budget`, `citizen science`, `replication`

**Langues** — français et anglais. Zenodo n'accepte qu'une langue principale :
choisir le français, l'anglais étant signalé dans la description.

**Version** — `1.9`

**Licence** — au choix. CC BY 4.0 convient à un document destiné à être repris
et exécuté par d'autres.

## Ce que ce dépôt établit, et ce qu'il n'établit pas

Il établit qu'à la date du DOI, ce texte-là existait, avec ce contenu-là, y
compris ses critères de décision et ses deux issues. Personne ne pourra soutenir
que les prédictions ont été écrites après avoir vu les données.

Il n'établit rien sur la qualité des mesures qui suivront, ni sur leur honnêteté.
Le préenregistrement rend une tricherie détectable ; il ne la rend pas
impossible. C'est la publication intégrale des fichiers bruts, promise en
section 13, qui fait le reste du travail.
