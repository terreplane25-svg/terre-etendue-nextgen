# Dépôt — préenregistrement du protocole de dépression de l'horizon

Ce dossier contient **le couple de fichiers à déposer**, figé, et son empreinte.
C'est lui qui fait foi, et non les sources HTML : celles-ci se recompilent, les
fichiers déposés ne bougent plus.

## Les deux fichiers

| fichier | langue | pages | SHA-256 |
|---|---|---|---|
| `Protocole-depression-horizon.pdf` | français | 23 | `cd7788750e41248300f668e6b242590ac3aefca82e64c2001d379b6c0b8ff404` |
| `Horizon-Dip-Protocol.pdf` | anglais | 23 | `ea37e162b1c1d81fd968aa1693b167a9d03c938979660c364b16d6172856db5f` |

Les empreintes sont aussi dans `SHA256SUMS.txt`, au format de `sha256sum`, ce
qui permet à n'importe qui de les vérifier d'une commande :

```bash
sha256sum -c SHA256SUMS.txt
```

## Pourquoi ces PDF sont versionnés, contrairement à tous les autres

Le `.gitignore` du projet exclut `*.pdf`, et le README des protocoles explique
que rien n'est perdu à ne pas les commiter puisqu'ils se régénèrent en quelques
secondes. **C'est vrai en général et faux ici**, pour une raison vérifiée et non
supposée : le rendu n'est **pas reproductible octet à octet**. Chromium inscrit
un horodatage de création dans le PDF, si bien que deux rendus successifs de la
même source donnent deux empreintes différentes.

Vérification faite le 26 août 2026, deux rendus consécutifs de `horizon-fr.html`
inchangé :

```
df2054a1a7bccf70005361a42a52e2017b8050dcb76141f0d82e35790afdc778
44039709cb3c10d523a22a519c0482a7d7ef140c81dccf8cd9c64995394cbb5c
```

Conséquence directe : **l'empreinte ne peut pas être recalculée depuis les
sources**. Elle ne vaut que pour l'exemplaire exact qui a été déposé. Si cet
exemplaire est perdu, le préenregistrement devient invérifiable — ce qui est
précisément ce qu'il est censé empêcher. Les deux fichiers sont donc conservés
ici, en dérogation assumée à la règle du projet.

Ne pas les régénérer. Ne pas les remplacer. S'il faut corriger le protocole,
c'est une **nouvelle version** qui se dépose, avec ses propres empreintes, et
celle-ci reste en place.

## Métadonnées du dépôt

À reporter dans le formulaire Zenodo ou OSF.

**Titre**
> Measuring the dip of the sea horizon as a function of altitude — an open,
> pre-registered protocol (FR/EN)

**Type de dépôt** — Zenodo : *Publication* → *Preprint*. OSF : *Preprint* ou
*Project* avec registration.

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
> acquisition, fixe ses critères de décision a priori, et situe la mesure parmi
> ses précédents — la formule est celle des tables de dépression employées en
> navigation astronomique depuis le XIXᵉ siècle.
>
> Ce dépôt contient la version 1.5 en français et en anglais. Les deux fichiers
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
> acquisition, fixes its decision criteria a priori, and situates the measurement
> among its precedents — the formula is that of the dip tables used in celestial
> navigation since the nineteenth century.
>
> This deposit holds version 1.5 in French and English. The two files have the
> same content.

**Mots-clés** — `dip of the horizon`, `horizon dip`, `atmospheric refraction`,
`geodesy`, `pre-registration`, `open protocol`, `artificial horizon`,
`celestial navigation`, `citizen science`, `replication`

**Langues** — français et anglais (Zenodo n'accepte qu'une langue principale :
choisir le français, et signaler l'anglais dans la description).

**Version** — `1.5`

**Licence** — au choix. CC BY 4.0 convient à un document destiné à être repris
et exécuté par d'autres.

**Champ « Notes » ou « Additional notes »** — y coller les deux empreintes :

```
SHA-256 des fichiers déposés :
cd7788750e41248300f668e6b242590ac3aefca82e64c2001d379b6c0b8ff404  Protocole-depression-horizon.pdf
ea37e162b1c1d81fd968aa1693b167a9d03c938979660c364b16d6172856db5f  Horizon-Dip-Protocol.pdf
```

## Marche à suivre

Un seul enregistrement, deux fichiers, un seul DOI — c'est ce que Zenodo et OSF
font l'un comme l'autre par défaut : le DOI porte sur l'**enregistrement**, pas
sur chaque fichier.

1. Créer un compte sur <https://zenodo.org> (ou <https://osf.io>).
2. **New upload**, puis déposer les **deux** PDF dans le même enregistrement.
   Ne pas créer deux enregistrements : ce sont deux traductions d'un même
   document, et deux DOI en feraient deux travaux distincts.
3. Renseigner les métadonnées ci-dessus. Coller les empreintes dans les notes.
4. Réserver le DOI (Zenodo propose « Reserve DOI » avant publication) puis
   **publier**. Le DOI ne devient permanent qu'à la publication.
5. Reporter le DOI obtenu dans la section « Engagement » du protocole — mais
   **attention** : modifier le PDF pour y inscrire le DOI change son empreinte
   et invalide ce qui vient d'être déposé. Deux façons propres de s'en sortir :
   - publier le DOI et les empreintes **ailleurs** — sur le site, dans un billet
     daté — et laisser les PDF déposés intacts. C'est la solution simple ;
   - ou n'inscrire le DOI que dans la **version suivante**, en indiquant qu'elle
     succède au dépôt initial.
6. Ne commencer à collecter qu'**après** la publication du DOI.

## Ce que ce dépôt établit, et ce qu'il n'établit pas

Il établit qu'à la date du DOI, ce texte-là existait, avec ce contenu-là, y
compris ses critères de décision et ses deux issues. Personne ne pourra soutenir
que les prédictions ont été écrites après avoir vu les données.

Il n'établit rien sur la qualité des mesures qui suivront, ni sur leur
honnêteté. Le préenregistrement rend une tricherie détectable ; il ne la rend pas
impossible. C'est la publication intégrale des fichiers bruts, promise en
section 13, qui fait le reste du travail.
