# Inventaire des documents sources déposés

*Dressé le 5 août 2026, après extraction et lecture des 28 fichiers de
`content/sources/brut/`. Cet inventaire n'est pas un résumé de complaisance : il
dit ce que chaque document permet d'établir, et ce qu'il ne permet pas.*

---

## Contrainte technique à connaître avant tout usage

**L'arabe extrait des PDF est corrompu.** Lettres disjointes, diacritiques
séparés, ordre des caractères altéré. Exemple relevé dans
`Versets sur la forme de la terre.pdf` :

```
﴿ٱلَّذ ِیِجَعَلَِلَكُمُِ ٱلۡأَرأضَ  فِرَ ٰ  شࣰا …
```

Le texte est illisible et **inutilisable pour publication**. Les traductions
françaises des mêmes PDF sortent en revanche correctement.

**Les `.docx` s'extraient proprement**, arabe compris. Règle qui en découle :

- pour un **texte arabe destiné à être publié** → source `.docx`, ou saisie
  manuelle, ou capture d'image ;
- pour une **référence, une pagination, une URL** → les PDF font parfaitement
  l'affaire.

---

## Les pièces maîtresses

### 1. `PAROLES_DE_SAVANTS_DE_DIVERSES_EPOQUES.pdf` — le socle

**30 savants, de 383 H à 1383 H.** Un millénaire d'autorités, du plus ancien au
plus récent. Chaque entrée porte, sans exception :

- le nom translittéré et la ou les dates de décès ;
- le verset commenté, en notation `sNN vNN` ;
- la citation traduite ;
- l'ouvrage, avec **volume et page** ;
- une **URL shamela** ou archive.org.

Décompte : 27 URL shamela, 4 archive.org, 17 références volume+page, 37 pages
seules, 22 renvois de versets.

C'est un appareil critique complet, prêt à devenir un jeu de données. Il répond
à lui seul au chantier 3 de l'audit de la Bibliothèque.

### 2. `Comparaison Consensus El Farghani et Ibn Mounadi.pdf` — la démonstration

Collation **phrase par phrase** entre le « consensus » d'Ibn al-Munādī (336 H),
tel que le rapporte Ibn Taymiyyah dans le *Majmūʿ al-Fatāwā*, et le texte
d'Ibn Kathīr al-Farghānī — un **astronome** mort vers 247 H — tel que le
conserve Ibn Rustah dans *al-Aʿlāq al-Nafīsa*.

Les formulations se recouvrent presque mot pour mot. Conclusion documentée :
ce n'est pas un consensus religieux (*šarʿī*) mais un consensus d'astronomes
(*ahl al-hayʾa*).

Cela transforme une affirmation de l'article `le-consensus-sur-la-sphericite`
en collation vérifiable. C'est le gain qualitatif le plus net du lot.

### 3. `Erreur Fausse Attribution Mobilité Terre Ibn Taymiyyah.pdf`

Établit qu'une variante textuelle a été prise pour une position doctrinale.
Le *Majmūʿ al-Fatāwā* imprimé porte **بجميع حركاتها** — « avec tous ses
mouvements » — d'où l'on a conclu qu'Ibn Taymiyyah admettait la mobilité de la
Terre. Or trois témoins antérieurs portent **بجميع أجزائها** — « dans toutes ses
parties » :

- Ibn Kathīr al-Farghānī (m. ~247 H), la source ;
- Ibn Rustah (m. ~300 H), *al-Aʿlāq al-Nafīsa* ;
- al-Masʿūdī (m. 346 H), *Murūj al-Dhahab*.

Un cas d'école de critique textuelle, et le sujet d'un article à lui seul.

### 4. `Traduction_Risala_Nafi_Kuriyyat_Ard.docx` — une source primaire

Traduction intégrale d'un traité ottoman, *Arzın küreviyyetini nefyedir*
(« réfutation de la sphéricité de la Terre »), avec **fiche catalographique du
manuscrit**, description du frontispice, glossaire des unités de mesure et note
du traducteur.

C'est le seul document du lot qui soit une **source primaire éditée** plutôt
qu'une compilation. Il mérite son propre article, avec son apparat.

---

## Les dossiers thématiques

| Document | Contenu | Article concerné |
|---|---|---|
| `D'OÙ VIENT LE « CONSENSUS ».docx` | Traité structuré : définition de l'*ijmāʿ*, ses trois conditions cardinales, cinq points établis. 468 blocs arabes propres. | `le-consensus-sur-la-sphericite` |
| `réponse détaillée au consensus.pdf` | 680 lignes, 27 shamela, 25 réf. volume. Reprend la liste des savants et discute Ibn Ḥazm, al-Kindī, al-Farghānī. | idem |
| `Réfutation_du_concordisme_cosmologique.docx` | Analyse lexicale des versets 21:30 et 51:47, mot par mot. 370 blocs arabes propres. | `le-concordisme` |
| `uluww_cosmologie.docx` | L'*ʿuluww* d'Allah comme contrainte cosmologique : preuves textuelles, position des Salaf, rupture du « haut absolu » dans le modèle sphérique, critique du panenthéisme structurel. 117 blocs arabes. | article à créer |
| `ou-est-Allah.pdf` | Dossier textuel de l'*ʿuluww* : sept versets sur l'*istiwāʾ*, l'ascension des créatures, le hadith de la servante. | complète le précédent |
| `tafsir_sajda5_verset5.docx` | Tafsīr ciblé de 32:5, « il administre l'Ordre depuis le ciel jusqu'à la terre ». | dossier cosmologie |
| `ard_plate_TRADUCTION_COMPLETE.docx` | Ouvrage complet avec sommaire : preuves, les sept terres, le mont Qāf, le Ciel, l'Eau, le mouvement des avions. | plusieurs |
| `The Flat Earth in Islam.pdf` | 67 pages en anglais, verset par verset. **3 657 blocs arabes, mais corrompus** — n'utiliser que la structure argumentative. | plusieurs |
| `Falsification cosmologique.pdf` | Critique de la cosmologie aristotélicienne : monde sublunaire et supralunaire, éther, sphères automatiques, exclusion de l'intervention divine. | `la-cosmologie-comme-instrument-de-domination` |
| `Projet regroupement pdf.pdf` | 1 223 blocs arabes, **60 URL shamela, 32 réf. volume/page**. Le réservoir de références. | tous |
| `Versets sur la forme de la terre.pdf` | Les versets clés avec traduction. Arabe corrompu, traductions exploitables. | `la-terre-dans-le-coran` |
| `article_evolution_islam.docx` | Micro contre macroévolution, ADN, ressemblance biologique, impasse concordiste. | `levolution-et-lislam` |
| `quran-tracing-workbook.pdf` | **72 618 blocs arabes** — vraisemblablement le texte coranique complet. Utile comme corpus de **vérification** du texte des versets cités. | contrôle |
| `messages.html`, `quiz-cieux-terre.html` | Exports de réseaux sociaux et quiz. Valeur documentaire faible. | — |

## Les documents adjacents

Cinq PDF d'ʿAbd al-ʿAzīz al-Ṭarīfī — *Le monde des anges*, *Le monde des djinns
et des démons*, *La petite Résurrection*, *La grande Résurrection*, *Les imams*,
*Résumé des signes de la fin des temps*. Ils ne portent pas sur la forme de la
Terre. Matière réelle, mais pour d'autres sujets que ceux du site aujourd'hui.

---

## Ce que le corpus ne contient pas

Honnêteté sur les manques, pour ne pas les découvrir en cours de route :

- **peu de pages shamela d'Ibn Taymiyyah** : les quatre citations du
  *Majmūʿ al-Fatāwā* restant à localiser ne sont pas couvertes par des URL ;
- **aucune variante de lecture (*qirāʾāt*)** sur les versets clés ;
- **aucune image de page** — que du texte ;
- **les gloses courtes** de Jalālayn et Qurṭubī sur *suṭiḥat* et *madda*
  apparaissent sans pagination dans les documents comme sur le site.
