# Fiche de relevé — les six références islamiques

**Pourquoi cette fiche.** shamela.ws est refusé par la politique réseau de
l'environnement d'exécution distant, au même titre que l'ensemble du web
général. Aucune de ces six références n'a pu être relevée depuis là. La fiche
prépare le travail pour qu'il se fasse en quelques minutes depuis une machine
connectée : pour chacune, la chaîne arabe à chercher, ce qu'il faut relever, et
où le reporter.

**Rectification préalable.** Le rapport précédent annonçait « cinq références
islamiques ». Elles sont **six** — j'avais mal compté les lignes de mon propre
tableau.

**Deux d'entre elles ne relèvent pas de la pagination**, ce qui a été établi en
cherchant dans nos fonds avant de conclure. Voir la section 3.

---

## 1. Les quatre à paginer

### 1.1 · Sunan Abī Dāwūd — la lecture *ḥamiʾa* d'Ibn ʿAbbās

Article `dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne`.

Chercher : `حمأة سوداء تغرب فيها الشمس`

Le passage relève du *Kitāb al-ḥurūf wa-l-qirāʾāt*. L'article cite déjà, dans le
même livre, le hadith **4002** (Abū Dharr, « il se couche dans une source
chaude ») : les deux sont vraisemblablement voisins. **Relever le numéro de
hadith**, et le grade de la chaîne si l'édition le porte — le pied dit
aujourd'hui « authentique » sans dire qui l'authentifie.

### 1.2 · Umayya ibn Abī al-Ṣalt — le vers cité

Article `dhu-al-qarnayn-…`.

Ce n'est pas dans shamela qu'il faut chercher mais dans une édition du *dīwān*
du poète. **Relever l'édition et le numéro de la pièce.** À défaut, la citation
tombe sous la règle du site : sans référence vérifiable, la retirer.

### 1.3 · al-Bayhaqī et al-Lālakāʾī — le rapport de Mālik sur l'*istiwāʾ*

Article `ou-est-allah-le-uluww-et-la-forme-du-monde`.

Chercher dans *al-Asmāʾ wa-l-Ṣifāt* : `الاستواء غير مجهول`
Puis dans *Sharḥ Uṣūl Iʿtiqād Ahl al-Sunna* : `كيف استوى`

**Attention, ce relevé est double.** L'article vient de recevoir une réserve
philologique qu'il faut trancher en même temps que la pagination : la forme que
nous donnons est *al-istiwāʾ maʿlūm wa-l-kayf majhūl*, alors que les recueils
transmettent le plus souvent `الاستواء غير مجهول والكيف غير معقول`. Et le propos
est rapporté tantôt de Mālik, tantôt de son maître Rabīʿa al-Raʾy. **Relever la
forme exacte de l'édition en même temps que le numéro**, et corriger le texte de
l'article s'il diverge.

### 1.4 · Ibn Rajab al-Ḥanbalī — *Ar-Radd*

Article `pres-de-cent-savants-de-lislam`.

Chercher : `أقام الله للناس أئمة من الفقهاء`

Le pied ne donne qu'un titre tronqué, « Ar-Radd ». Il s'agit très
vraisemblablement d'*al-Radd ʿalā man ittabaʿa ghayr al-madhāhib al-arbaʿa* —
**à confirmer avant d'écrire le titre complet**, puis relever la page.

## 2. Le tableau de report

| Où | Fichier | Ce qu'il faut écrire |
|---|---|---|
| Sunan Abī Dāwūd | `content/articles/dhu-al-qarnayn-….json` | `— Sunan Abī Dāwūd, n° XXXX` |
| Umayya | `content/articles/dhu-al-qarnayn-….json` | `— Umayya ibn Abī al-Ṣalt, Dīwān, éd. XXX, n° XX` |
| Mālik | `content/articles/ou-est-allah-….json` | `— …al-Asmāʾ wa-l-Ṣifāt n° XXX ; …Sharḥ Uṣūl Iʿtiqād n° XXX` |
| Ibn Rajab | `content/articles/pres-de-cent-savants-de-lislam.json` | `— Ibn Rajab al-Ḥanbalī, <em>titre complet</em>, p. XXX` |

Le marqueur *(à paginer)* se retire tout seul : il suffit de relancer
`python3 scripts/localiser-citations-occidentales.py`, qui le repose et le
retire selon l'état réel de chaque pied.

## 3. Les deux qui ne relèvent pas de la pagination

En cherchant dans nos fonds avant de conclure, deux des six se sont révélées
être autre chose qu'un défaut de pagination.

| Article | Référence | Ce qui a été constaté |
|---|---|---|
| `dune-terre-plate-universelle-a-la-sphere-grecque` | Ibn Taymiyya, *Darʾ Taʿāruḍ al-ʿAql wa-l-Naql* — « Quiconque élève la parole des philosophes grecs au-dessus du Coran et de la Sunna a commis une grave erreur. » | Français seul, aucun texte arabe, formulation générale. Ne correspondait mot pour mot à aucun texte d'Ibn Taymiyya de notre fonds. **Réglé** : remplacée par le 1/120. |
| `le-consensus-sur-la-sphericite` | Ibn Taymiyya, *Bayān Talbīs al-Jahmiyya* — « La parole d'aucun d'entre eux n'est une preuve… » | Même constat. |

Ces deux passages sont vraisemblablement des **reformulations** et non des
citations. On ne pagine pas une reformulation : on la vérifie, ou on la
remplace. Leur marqueur est donc passé de *(à paginer)* à
*(à vérifier — texte non retrouvé dans nos sources)*, qui est ce que nous
savons réellement.

**Une solution est déjà à portée pour la première.** Notre fonds contient
quatre textes d'Ibn Taymiyya, verbatim, en arabe et référencés, portant très
exactement sur le même thème — la subordination de la Révélation à la
philosophie. Ils viennent du dossier *Réfutation du concordisme cosmologique*,
déposé dans `content/sources/brut/`, et l'article `le-concordisme` en cite déjà
trois.

| Référence | Texte |
|---|---|
| *Darʾ Taʿāruḍ* 1/120 | `وإذا تعارض العقل الصريح والنقل الصحيح وجب تقديم النقل` — « Quand la raison claire et la transmission saine s'opposent, il faut donner la primauté à la transmission. » |
| *Darʾ Taʿāruḍ* 1/152 | `فالعقل الصريح لا يعارض النقل الصحيح، ولكن من ظن تعارضهما فهو إما لفسادٍ في العقل أو لعدم فهمٍ للنقل` |
| *Darʾ Taʿāruḍ* 1/154 | `لا يمكن في العقل الصريح أن يعارض النقل الصحيح أبدًا، ولكن الجهل أو الظلم هو الذي يوقع التعارض` |
| *Darʾ Taʿāruḍ* 7/285 | `كل من عارض الشرع بالعقل فإنما قال بغير عقلٍ صريح، أو نقلٍ صحيح` — « Quiconque oppose la Loi à la raison n'a parlé ni avec une raison claire, ni avec une transmission saine. » |

**Fait le 6 août 2026** : la reformulation a été remplacée par le texte 1/120,
en arabe et en traduction. Le remplacement énonce la règle générale de primauté
du <em>naql</em> sur le <em>ʿaql</em> et ne nomme pas les philosophes grecs : le
paragraphe d'introduction a été réécrit en conséquence, pour que l'article ne
fasse pas dire au texte plus qu'il ne dit. La ligne correspondante disparaît
donc du chantier.

Pour la seconde, le *Bayān Talbīs al-Jahmiyya*, nous n'avons aucun substitut en
fonds. Il faudra soit retrouver le passage, soit retirer la citation.
