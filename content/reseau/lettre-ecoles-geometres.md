# Proposition de projet d'application — mesure de l'excès sphérique

*Lettre destinée aux enseignants-chercheurs et directions des études — ESGT Le Mans, ENSG
Marne-la-Vallée, INSA Strasbourg, Ordre des géomètres-experts.*

*Version 1.0 — 28 juillet 2026. Fondée sur `content/reseau/protocole-triangulation-terrain.json` v1.0.*

---

**Objet :** proposition de projet d'application — mesure de la fermeture angulaire d'un grand
triangle géodésique (Aigoual – Mézenc – Ventoux)

Madame, Monsieur,

Je vous écris au sujet d'un projet de mesure qui relève exactement de vos travaux pratiques de
topométrie, et pour lequel je cherche un partenaire académique. Je commence par le contexte,
parce qu'il détermine si la demande vous intéresse ou non.

## Qui je suis, et pourquoi je vous écris

J'anime **terre-etendue-islam.fr**, un site francophone qui examine la cosmologie coranique et
la cosmologie scientifique. Une partie de son public s'intéresse aux objections de type « Terre
plate » et considère que la question de la forme de la Terre n'est pas tranchée.

Je vous le dis d'emblée pour deux raisons. D'abord parce que vous l'auriez découvert, et qu'une
découverte tardive rendrait la collaboration impossible et la donnée inutilisable. Ensuite parce
que c'est précisément ce contexte qui fait l'intérêt du projet : il existe très peu de mesures
géodésiques **récentes, francophones, publiques et pré-enregistrées** vers lesquelles renvoyer
quelqu'un qui demande à voir plutôt qu'à croire.

Je n'attends de vous aucune position sur ce débat, et le protocole ci-dessous est conçu pour
qu'aucune ne soit nécessaire.

## Ce que je propose de mesurer

**La somme des angles d'un triangle formé par trois sommets intervisibles du Massif central et
de Provence :**

| Sommet | Altitude | Accès |
|---|---|---|
| Mont Aigoual (Gard) | 1 567 m | route, observatoire |
| Mont Mézenc (Haute-Loire / Ardèche) | 1 753 m | route + marche courte |
| Mont Ventoux (Vaucluse) | 1 912 m | route |

Côtés : 100,3 km, 135,9 km et 119,5 km. Aire : environ 5 810 km².

L'observable est la **fermeture brute** : la somme des trois angles horizontaux, mesurés chacun
depuis son sommet, sans aucune compensation.

## Pourquoi cette grandeur et pas une autre

Une distance mesurée doit être comparée à une distance prédite, ce qui suppose de savoir où sont
les points — donc un modèle. Une somme d'angles se compare à **180°**. Il n'y a rien à supposer :
ni datum, ni projection, ni échelle, ni même une unité de longueur.

C'est le seul observable que je connaisse qui soit à la fois décisif et entièrement local.

## Ordres de grandeur

Excès sphérique attendu : `ε = A/R² ≈ 29,5″`.

Avec une station totale de classe 1″ et 12 séries par angle :

- σ par direction : 1″/√12 ≈ 0,29″
- σ sur la somme des trois : √3 × 0,29 ≈ 0,50″
- **rapport signal / bruit : environ 59**

Autrement dit, la grandeur cherchée dépasse le bruit d'un facteur soixante. Le matériel courant
d'un cabinet ou d'une école suffit très largement ; il n'y a aucun besoin d'instrumentation
particulière.

## Le point technique qui commande le choix du triangle

Vous verrez immédiatement l'objection : le théodolite se cale sur la **verticale locale**, pas
sur une normale théorique, et l'écart atteint 5 à 30″ en terrain montagneux. Son effet sur un
angle horizontal vaut `η·tan z`.

| Déviation | Inclinaison de visée | Effet sur l'angle |
|---|---|---|
| 10″ | 1° | 0,17″ |
| 10″ | 3° | 0,52″ |
| 30″ | 1° | 0,52″ |
| 30″ | 3° | 1,57″ |

Ajoutons la hauteur de cible (≈ 0,11″ pour 1 000 m) et la réfraction latérale (quelques
dixièmes de seconde sur visées rasantes).

**C'est la raison pour laquelle ce triangle a été retenu plutôt qu'un plus petit.** À 29,5″
d'excès, ces corrections réunies pèsent moins de 1″ et ne peuvent pas fabriquer le signal. Sur
un triangle de 30 km, l'excès tomberait à 2″ — du même ordre que les corrections — et le
résultat deviendrait contestable. Les trois sommets ont en outre des altitudes proches
(1 567 / 1 753 / 1 912 m), ce qui maintient les visées sous 1° d'inclinaison.

## Protocole demandé

1. Occuper successivement les trois sommets.
2. 12 séries par angle minimum, double retournement, cercle gauche et cercle droit.
3. Consigner pour chaque visée : lectures brutes, distance zénithale, heure, température,
   pression, visibilité.
4. **Désactiver toute compensation automatique de fermeture et toute correction de projection
   dans le logiciel de la station.** Exporter les lectures brutes.
5. **Ne jamais fermer à 180°.** La fermeture brute *est* le résultat.
6. Publier le carnet complet, y compris les séries écartées et le motif de leur rejet.

Le point 4 mérite une vérification avant la campagne : plusieurs firmwares appliquent une
compensation en silence.

## Pré-enregistrement

Les deux prédictions sont déjà consignées, datées et publiées dans un dépôt Git public, **avant
toute mesure** :

```
modèle plan       somme = 180° 00′ 00,00″     (excès nul par construction)
modèle sphérique  somme = 180° 00′ 29,52″     (ε = A/R²)
```

Elles ne seront pas recalculées après réception de la mesure. Toute modification resterait
visible dans l'historique du dépôt.

## Ce que j'attends du résultat — et ce que je m'engage à en faire

Je dois être franc sur un point, sans quoi la proposition serait malhonnête : **la discipline
considère cette question comme tranchée depuis deux siècles**, et vos étudiants mesurent
d'ailleurs des fermetures de ce type en travaux pratiques. Je n'attends aucune surprise.

L'intérêt du projet n'est donc pas de découvrir quelque chose, mais de produire une
**reproduction publique, datée, pré-enregistrée et francophone**, dont chaque étape est
vérifiable par quelqu'un qui ne fait pas confiance à la conclusion.

Mes engagements, quel que soit le résultat :

- publication du carnet brut intégral, sans tri ni retouche ;
- publication du résultat **même s'il contredit ce que j'espérais** — le protocole est
  symétrique et je l'ai accepté avant de vous écrire ;
- aucun droit de regard éditorial de ma part sur le rapport technique, qui reste à ses auteurs ;
- crédit nominatif de l'équipe et de l'établissement, ou anonymat complet, à votre choix ;
- accès libre aux données sous licence ouverte.

Si vos étudiants souhaitent rédiger eux-mêmes la note d'interprétation, elle sera publiée telle
quelle et sans commentaire de ma part.

## Ce que je fournis

- Le protocole complet et les cinq triplets candidats calculés, avec excès attendu et rapport
  signal/bruit pour chacun (le triangle proposé ici est le n°2 ; quatre variantes de repli
  existent, de 7,1″ à 34,2″).
- Les feuilles de relevé.
- L'analyse des corrections instrumentales et de leur poids relatif.
- Le dépôt Git public où tout est horodaté.
- La prise en charge des frais de déplacement et de séjour, si le cadre de l'établissement le
  permet.

## Volume de travail estimé

Trois journées de terrain, une par sommet, à choisir dans une fenêtre de transparence
atmosphérique — mistral établi, lendemain de pluie, aube ou crépuscule. Plus le dépouillement.
C'est le format d'un projet de deuxième année ou d'un TP long.

---

Je reste à votre disposition pour tout complément, et je comprendrai parfaitement un refus lié
au contexte que j'ai exposé en ouverture. Si l'un des points techniques vous paraît discutable,
je suis preneur de la critique : elle vaudra pour la suite du projet même si la collaboration ne
se fait pas.

Je vous prie d'agréer, Madame, Monsieur, l'expression de ma considération distinguée.

*[Nom, qualité, coordonnées]*
*terre-etendue-islam.fr*
*Dépôt public : [URL du dépôt]*

---

## Notes internes — non destinées à l'envoi

**Deux décisions de cadrage assumées dans cette lettre.**

1. **Le contexte est dit en ouverture.** L'alternative — une demande neutre présentée comme de
   la médiation scientifique — obtiendrait plus de réponses positives, mais le contexte est
   découvrable en une recherche. Sa découverte après la campagne détruirait la crédibilité de la
   donnée et exposerait l'établissement. Une donnée obtenue sur un malentendu ne vaut rien pour
   un projet dont le seul capital est la vérifiabilité.

2. **L'issue attendue est annoncée.** Présenter la mesure comme un test dont l'issue serait
   incertaine décrédibiliserait l'ensemble auprès d'un enseignant-chercheur en géodésie, qui
   sait que la fermeture de ce triangle est un exercice classique. Assumer la reproduction est
   la seule position tenable — et c'est aussi ce qui rend l'engagement de publication crédible.

**À personnaliser avant envoi :** nom et qualité de l'expéditeur, URL du dépôt, et un paragraphe
d'accroche propre à chaque établissement (l'ESGT et l'ENSG ont des pratiques de projet
différentes ; l'Ordre des géomètres-experts relève d'une approche professionnelle et non
pédagogique — pour lui, insister sur la valeur de démonstration publique du métier plutôt que
sur le format projet étudiant).
