# Dépôt des documents sources

Ce dossier reçoit la matière première : pages copiées, relevés, listes, scans.
Il n'est **pas servi par le site** — rien de ce qui s'y trouve n'est publié
automatiquement. Ce qui doit paraître dans un article est repris et mis en forme
séparément.

## Où déposer quoi

| Dossier | Contenu | Format |
|---|---|---|
| `arabe/` | Pages de tafsīr, hadith, fatāwā — copiées depuis shamela ou saisies | `.md` ou `.txt`, UTF-8 |
| `occidental/` | Extraits de Poincaré, Hubble, Einstein, Newton, Copernic… | `.md` ou `.txt` |
| `savants/` | La liste des autorités : noms, dates, formulations, ouvrages | `.md`, `.csv` ou `.txt` |
| `dictionnaires/` | Entrées des dictionnaires classiques (daḥā, basaṭa, suṭiḥat…) | `.md` ou `.txt` |
| `images/` | Photos de pages, captures d'écran | `.jpg` de préférence |
| `brut/` | Tout ce qui ne rentre nulle part. En vrac, sans mise en forme. | n'importe quoi |

**En cas de doute : `brut/`.** Un document mal rangé est infiniment plus utile
qu'un document non déposé. Le tri est mon travail, pas le vôtre.

## Le format qui me fait gagner le plus de temps

Un bloc par citation. Rien de plus, et l'ordre n'a pas d'importance.

```
OUVRAGE : Tafsīr al-Ṭabarī
ÉDITION : éd. Aḥmad Shākir, Mu'assasat al-Risāla, 2000
URL     : https://shamela.ws/book/1687/3338
VOL/PAGE: 24 / 342
ARABE   :
[copier-coller brut de la page, même long, même en vrac, même avec les
 en-têtes et la pagination du site]
```

Trois précisions.

**L'URL shamela suffit presque à elle seule** : elle contient l'identifiant du
livre et celui de la page. Si vous n'avez qu'elle, déposez-la quand même.

**Le texte arabe n'est pas décoratif.** Il sert de contrôle : si ce qui est collé
ne correspond pas à la citation française publiée sur le site, c'est la référence
qui est fausse, et cela se verra. C'est le même principe que le contrôle croisé
appliqué aux mesures.

**L'édition ne se renseigne qu'une fois par ouvrage**, pas à chaque citation.

## Ce qu'il ne faut pas faire

**Ne jamais deviner une pagination.** Laisser le champ vide vaut mieux que
l'approximer. Une référence fausse est pire qu'une référence absente : elle donne
l'apparence de la vérifiabilité. En cas de doute, la citation sera retirée de
l'article plutôt que sourcée à peu près.

**Ne pas nettoyer avant de déposer.** Les en-têtes, les numéros de page du site,
les notes de bas de page : gardez tout. Ce sont souvent ces débris qui portent le
volume et la page.

## Images et droits

Le dépôt est **public**. Une photographie de page issue d'une édition critique
moderne relève du travail éditorial du muḥaqqiq et peut être protégée. Pour les
éditions anciennes et les textes eux-mêmes, la question ne se pose pas.

En pratique : déposez ce que vous voulez ici pour mon usage de lecture. Ce qui
sera **publié dans un article** sera choisi au cas par cas, et hébergé sur
Hostinger comme le reste des images du site — pas servi depuis ce dépôt.

## Priorités

Par ordre de valeur pour le site, à ce jour :

1. **20 citations arabes à localiser** — voir `content/corrections/citations-par-ouvrage.json`.
   Dix ouvrages seulement : Ibn Taymiyyah (4), Ṭabarī (3), Sunan Abī Dāwūd (2),
   Ibn Kathīr (2), Baghawī (2), Jalālayn (2), Qurṭubī (2), Ibn Rajab (1),
   Umayya ibn Abī al-Ṣalt (1), et un « al-Bukhārī et Muslim » à préciser.
2. **Les quatre-vingt-quinze savants** — même en désordre. Nom, dates, école,
   formulation exacte en arabe, ouvrage. Ça deviendra un jeu de données et une
   table triable.
3. **Les huit dictionnaires sur daḥā** — les entrées elles-mêmes. C'est
   l'argument central de l'article phare et il repose aujourd'hui sur une phrase.
4. **41 citations occidentales** — Poincaré (4), Hubble (3), Einstein (2),
   Mach (2), Newton (2), Copernic (2), et vingt-cinq autres à une occurrence.
5. **Variantes de lecture (qirāʾāt)** sur les versets clés, s'il en existe.
   Les mentionner quand elles ne changent rien renforce la démonstration.

## Et si c'est court

Pour deux ou trois références, un message direct est plus rapide qu'un commit.
Le dépôt vaut pour les volumes.
