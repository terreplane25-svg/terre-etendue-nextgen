# Proposition de campagne de mesure — la loi flèche/distance sur un plan d'eau

*Lettre destinée aux bases nautiques, clubs de plongée et de voile, lycées à section
topographie, IUT génie civil, associations d'astronomie, cabinets de géomètres-experts et
gestionnaires de plans d'eau.*

*Version 1.1 — 2 août 2026. Fondée sur `content/reseau/protocole-cote-trois-mires.json` v1.1,
pré-enregistré et horodaté dans un dépôt public. Schémas du dispositif dans
`public/schemas/`.*

---

**Objet :** proposition de campagne de mesure sur un plan d'eau — la flèche à sept distances,
de 1 à 10 km

Madame, Monsieur,

Je vous écris pour vous proposer d'accueillir, ou de co-réaliser, une campagne de mesure qui
tient en trois perches et une lunette, et dont le résultat n'a jamais été publié par personne.
Je commence par le contexte, parce qu'il détermine si la demande vous intéresse ou non.

## Qui je suis, et pourquoi je vous le dis d'emblée

J'anime **terre-etendue-islam.fr**, un site francophone qui examine la cosmologie coranique et
la cosmologie scientifique. Une partie de son public s'intéresse aux objections de type « Terre
plate » et considère que la question de la forme de la Terre n'est pas tranchée.

Je vous le dis en ouverture pour deux raisons. D'abord parce que vous l'auriez découvert, et
qu'une découverte tardive rendrait la collaboration impossible et la donnée inutilisable.
Ensuite parce que c'est ce contexte qui fait l'intérêt du projet : il existe très peu de mesures
**récentes, francophones, publiques et pré-enregistrées** vers lesquelles renvoyer quelqu'un qui
demande à voir plutôt qu'à croire.

Je n'attends de vous aucune position sur ce débat, et le protocole ci-dessous est conçu pour
qu'aucune ne soit nécessaire.

## Ce qui manque réellement dans la littérature

Cinq campagnes ont mesuré la courbure au-dessus de l'eau depuis 1870. Je les ai recensées, avec
leurs qualités et leurs défauts.

| Campagne | Année | Distance | Ce qui manque |
|---|---|---|---|
| Canal Old Bedford, de Rowbotham à Blount | 1838-1904 | 9,66 km | hauteur d'œil non contrôlée d'une observation à l'autre, et test d'occultation peu discriminant à cette distance |
| Rainy Lake (Minnesota) | 2018 | 10 km | prédictions non horodatées, une seule distance |
| FECORE, lacs Balaton et IJssel | 2018 | 12 à 40 km | laser divergent et mal calibré, aucun instrument normalisé |
| Lac Pontchartrain (Louisiane) | 2017 | 24,27 km | une seule distance, conditions atmosphériques non consignées |
| Hirt *et al.*, *J. Geophys. Res.* | 2010 | 4 à 23 km | porte sur la réfraction, pas sur la forme |

Un mot sur la première ligne, parce qu'elle est souvent mal citée dans les deux camps. Le
canal Old Bedford a vu des dizaines d'observations entre 1838 et 1904 — Rowbotham à répétition,
puis Wallace en 1870, puis Lady Blount en 1904. Ce ne sont pas des répétitions d'un même
protocole : la hauteur de l'œil change à chaque fois, et c'est elle qui commande le résultat.
Sur les 9,66 km du canal, avec une cible de 1,52 m et k = 0,13, le modèle sphérique masque
4,31 m depuis un œil à 20 cm, 3,06 m depuis 60 cm, et seulement **0,26 m** depuis les 4,04 m de
la lunette de Wallace. Autrement dit : au ras de l'eau on se place dans la couche où la
réfraction est ingérable — il faudrait k = 0,615 pour tout voir, ce qui n'est pas impossible en
régime de superréfraction sur un canal ; et à quatre mètres, le test d'occultation ne
discrimine presque plus, puisque le globe lui-même ne masque plus qu'un quart de mètre.

C'est précisément l'argument qui commande le choix de l'observable de cette campagne. Au même
endroit, à la même distance, la flèche vaut **1,59 m** contre 0,26 m pour l'occultation : six
fois plus de signal, pour un montage plus simple.

Le point commun aux cinq lignes saute aux yeux quand on les met côte à côte. **Chacune mesure une valeur à une
distance. Aucune ne mesure la loi.**

C'est précisément là que se trouve la place à prendre, et c'est un argument technique et non
rhétorique : voir la section suivante.

## L'observable, et pourquoi c'est celui-là

Trois perches identiques de 4,00 m, calées non pas sur le fond mais **sur la ligne d'eau**.
Appelons-les A, B et C. A et C séparées d'une distance D, B exactement au milieu, graduée au
millimètre. L'œil au sommet de A, la visée sur le sommet de C, et on lit où cette ligne croise
la graduation de B.

L'eau fait le nivellement : trois repères calés sur la ligne d'eau sont à la même hauteur par
construction, sans instrument, sans cheminement, sans datum, sans projection, et sans même une
unité de longueur imposée. La seule chose que l'opérateur apporte est une ligne de visée, et une
ligne de visée est droite.

La grandeur mesurée est la **flèche** :

```
f = (1 − k) · D² / (8 R)
```

Sur un plan, f = 0 à toute distance. Sur une sphère de rayon R, f croît comme le carré de D.

**Mais l'observable de cette campagne n'est pas f. C'est l'exposant de D.**

C'est le point décisif, et il mérite d'être posé lentement, parce qu'il désamorce à l'avance
l'objection qui a tué toutes les campagnes précédentes.

La réfraction atmosphérique agit par le facteur multiplicatif **(1 − k)**. Elle rabote la flèche
d'un certain **pourcentage** — le même à toutes les distances. Elle ne lui retire pas un nombre
fixe de centimètres. Sur un graphe log-log, cela déplace la droite verticalement sans en changer
la pente. Et l'étude de Hirt *et al.* (2010) établit que les écarts sur les angles de réfraction
restent sous 1″ **indépendamment de la longueur de la ligne**, de 4 à 23 km : k ne dérive donc
pas systématiquement avec la distance.

Conséquence : les pentes attendues séparent nettement les hypothèses.

| Hypothèse | Pente de log(f) contre log(D) |
|---|---|
| Sphère de rayon R | **2,000** |
| Surface plane | aucune pente, f compatible avec zéro |
| Artefact de perspective ou divergence optique | ≈ 1,0 |
| Gradient thermique régulier le long de la visée | ≈ 1,0 |

Aucune de ces alternatives ne produit un exposant 2. **C'est le seul observable de cette famille
qui soit robuste à l'objection de réfraction — et il l'est dans les deux sens** : il empêche
aussi d'invoquer la réfraction pour expliquer une flèche absente.

## Le pré-enregistrement

Les deux prédictions sont déjà consignées, datées et publiées dans un dépôt Git public, **avant
toute mesure**, et elles ne seront pas recalculées après réception des relevés. Toute
modification resterait visible dans l'historique.

Hauteur des trois perches : 4,00 m. Lecture attendue sur la graduation de B :

| D (A–C) | Modèle plan | Sphère, k = 0,10 | Sphère, k = 0,13 | Sphère, k = 0,34 | Garde d'eau au milieu |
|---|---|---|---|---|---|
| 1 km | 4,000 m | 17,7 mm | 17,1 mm | 12,9 mm | 3,98 m |
| 1,5 km | 4,000 m | 39,7 mm | 38,4 mm | 29,1 mm | 3,96 m |
| 2 km | 4,000 m | 70,6 mm | 68,3 mm | 51,8 mm | 3,92 m |
| 3 km | 4,000 m | 158,9 mm | 153,6 mm | 116,5 mm | 3,82 m |
| 5 km | 4,000 m | 441,4 mm | 426,7 mm | 323,7 mm | 3,51 m |
| 7 km | 4,000 m | 865,2 mm | 836,4 mm | 634,5 mm | 3,04 m |
| 10 km | 4,000 m | 1 765,8 mm | 1 707,0 mm | 1 294,9 mm | 2,04 m |

*(colonnes sphériques : de combien la lecture descend sous 4,000 m ; R = 6 371 km)*

Deux remarques de conception sur ce tableau. La colonne du modèle plan vaut 4,000 m à chaque
ligne : ce modèle prédit que **la lecture ne bouge jamais**, quelle que soit la distance. Et la
garde d'eau — hauteur à laquelle la visée passe au-dessus de l'eau au point milieu — reste
supérieure à 2 m à 10 km : **une seule hauteur de perche couvre les sept configurations**, ce
qui rend la série comparable et permet d'ajuster une pente.

## Le budget d'erreur, et la pièce du dispositif qui décide de tout

C'est la partie de cette lettre que je vous demande de critiquer en priorité.

Le budget ci-dessous m'a fait **corriger mon propre protocole**. Dans sa première version, je
tolérais un clapot de 10 cm. Le calcul montre que la lecture de la ligne d'eau écrasait alors le
signal : rapport signal/bruit de 0,3 à 1 km, et jamais au-delà de 8 même à 10 km.

**A. Sans puits de tranquillisation, une séance de trois lectures**

| D | Flèche | σ total | Signal/bruit |
|---|---|---|---|
| 1 km | 19,6 mm | 70,9 mm | **0,3** |
| 3 km | 176,6 mm | 74,8 mm | 2,4 |
| 10 km | 1 962 mm | 249,0 mm | 7,9 |

La correction est un objet à quinze euros : **un puits de tranquillisation**, c'est-à-dire un
simple tube plongeur de 50 à 100 mm de diamètre, percé de trous fins en partie basse et
solidaire de la perche. Il amortit le clapot et fait passer la lecture de la ligne d'eau de
100 mm à 5 mm. C'est la technique des marégraphes depuis le XIX<sup>e</sup> siècle.

**C. Avec puits de tranquillisation, dix séances — protocole retenu**

| D | Flèche | Pointe | Hauteur/eau | Réfraction | σ total | Signal/bruit |
|---|---|---|---|---|---|---|
| 1 km | 19,6 mm | 1,25 mm | 1,18 mm | 0,74 mm | 1,88 mm | **10,5** |
| 2 km | 78,5 mm | 2,50 mm | 1,18 mm | 2,98 mm | 4,07 mm | 19,3 |
| 3 km | 176,6 mm | 3,76 mm | 1,18 mm | 6,70 mm | 7,77 mm | 22,7 |
| 5 km | 490,5 mm | 6,26 mm | 1,18 mm | 18,61 mm | 19,67 mm | 24,9 |
| 7 km | 961,4 mm | 8,76 mm | 1,18 mm | 36,48 mm | 37,54 mm | 25,6 |
| 10 km | 1 962 mm | 12,52 mm | 1,18 mm | 74,45 mm | 75,51 mm | **26,0** |

Hypothèses retenues : précision de pointe 2″ par visée, lecture de la ligne d'eau 5 mm dans le
puits, longueur de perche connue à 1 mm, verticalité tolérée à 1 cm sur 4 m, dispersion de
terrain du coefficient de réfraction σ<sub>k</sub> = 0,12, trois lectures par séance.

Trois choses se lisent dans ce tableau.

La **pointe** croît comme D, la **flèche** comme D² : le rapport signal/bruit s'améliore donc
mécaniquement avec la distance. La **hauteur/eau** est constante, et c'est elle qui condamnait la
version sans puits. La **réfraction** domine au-delà de 3 km, et c'est irréductible — d'où le
choix de mesurer la pente plutôt que l'amplitude.

## Le pouvoir de discrimination

C'est le chiffre qui justifie la campagne. Incertitude sur la pente *a* de log(f) = *a*·log(D) + *b* :

| Séances par distance | σ sur la pente | Sépare 2,000 de 1,000 | Sépare 2,000 de 0 (modèle plan) |
|---|---|---|---|
| 1 | 0,087 | 11,6 σ | 23,1 σ |
| 5 | 0,039 | 25,8 σ | 51,7 σ |
| **10** | **0,027** | **36,5 σ** | **73,1 σ** |
| 20 | 0,019 | 51,7 σ | 103,3 σ |

Ce qui fait la force du dispositif n'est pas la précision sur une flèche. C'est le **bras de
levier de la décade en distance** : de 1 à 10 km, la flèche prédite passe de 19,6 mm à 1 962 mm,
soit un facteur 100 pour un facteur 10 en distance. C'est ce rapport que la réfraction ne sait
pas imiter.

## Protocole demandé

1. Trois perches identiques de 4,00 m, verticalité vérifiée au fil à plomb, chacune munie de son
   puits de tranquillisation. La perche B graduée au millimètre sur ses 2,50 m supérieurs.
2. Positionnement de B au milieu de A–C à 0,5 % près ; D relevée au télémètre ou au GPS.
3. Trois lectures par séance, espacées de dix minutes, avec température de l'air, température de
   l'eau, pression, vent et visibilité à chaque lecture.
4. **Dix séances retenues minimum par distance**, réparties sur cinq journées distinctes au
   moins, matin et après-midi obligatoirement représentés.
5. **Aucun compensateur, aucune bulle, aucune horizontale instrumentale entre A et C.** La visée
   A→C doit être une droite géométrique. Un compensateur se cale sur la verticale locale, qui
   tourne avec la surface, et réintroduirait exactement l'aveuglement que ce montage sert à
   contourner. Ce point mérite une vérification avant la campagne : plusieurs firmwares
   appliquent une correction en silence.
6. **Pas de laser.** C'est ce qui a fait échouer la campagne FECORE de 2018 : à 20 km la tache
   atteint plusieurs mètres et une erreur d'inclinaison d'un centième de degré produit 3,50 m
   d'écart. Mire graduée et visée optique uniquement.
7. Publier le carnet complet, y compris les séances écartées et le motif de leur rejet.

### Règles de rejet, écrites avant les séances

Une séance est écartée si les trois lectures s'écartent de plus de 20 % de leur médiane ; si un
mirage est visible ; si le vent dépasse 8 m/s ; si les trois lectures de ligne d'eau d'une même
station s'écartent de plus de 10 mm ; si l'écart de température air-eau dépasse 5 K ; ou si une
perche s'écarte de la verticale de plus de 1 cm sur 4 m.

Une précision méthodologique sur la moyenne des séances : la réduction du bruit de réfraction en
1/√n n'est légitime que si les séances échantillonnent des **états atmosphériques indépendants**.
Dix séances faites le même jour ne valent pas dix séances. C'est la raison de l'exigence de cinq
journées distinctes, et non un excès de prudence.

## Règle de décision, écrite avant les séances

**Issue 1 — surface plane.** Si la flèche reste indiscernable de zéro sur les sept
configurations, en particulier sous 600 mm à 10 km, la surface des eaux est plane sur cette
plage, et c'est ce qui sera publié, sans atténuation.

**Issue 2 — surface courbe.** Si la pente vaut 2,00 à 0,10 près et que le rayon déduit tombe à
25 % près autour de 6 371 km après correction de k, la courbure est établie sur cette plage.

**Issue 3 — non concluant.** Pente comprise entre 1,2 et 1,8, ou dispersion entre séances
supérieure à 40 % : la campagne est déclarée non concluante et publiée comme telle. Un résultat
non concluant n'est pas un échec ; c'est ce qui manque le plus dans ce dossier.

Les trois issues sont écrites avec le même soin, et l'issue plane est formulée en premier. Un
protocole qui ne peut pas donner tort à celui qui le tient ne vaut rien.

## Sites envisagés

| Site | Longueur utile | Profondeur moyenne | Avantage | Contrainte |
|---|---|---|---|---|
| Étang de Vaccarès (Camargue) | 13 km | 1,5 m | assez peu profond pour planter les perches à pied ou en barque plate sur toute la ligne | réserve naturelle, autorisation du Parc naturel régional |
| Étang de Thau (Sète–Marseillan) | 19 km | 4,5 m | permet d'aller au-delà de 10 km | tables conchylicoles, trafic |
| Étang de Berre | 15 km | 6,0 m | accès routier sur tout le pourtour | mistral fréquent |
| Étang de Leucate-Salses | 14 km | 2,0 m | peu profond, rives accessibles | tramontane |
| Baie de Somme à marée basse | 15 km | estran | sable dur nivelé par la mer, on y marche et on y plante des piquets | la ligne d'eau bouge pendant la séance |

L'absence de marée est le critère premier : elle garantit que la ligne d'eau ne se déplace pas
entre l'installation de A et la lecture sur B.

## Volume de travail

Sept distances, dix séances, trois lectures : **210 lectures**, soit environ **14 heures
d'observation** réparties sur cinq à huit journées de terrain selon la météo et le temps de
déplacement des perches. C'est le format d'un projet de fin d'année, d'un cycle de sorties de
club, ou d'une série de week-ends.

## Ce que je fournis

- Le protocole complet, le budget d'erreur détaillé poste par poste, et les feuilles de relevé.
- Les scripts de calcul, versionnés, qui reproduisent chaque chiffre de cette lettre à l'octet
  près — aucun nombre n'y est saisi à la main.
- Le dépôt Git public où tout est horodaté.
- Les trois perches, les puits de tranquillisation et la mire graduée, ou leur financement.
- La prise en charge des frais de déplacement, si le cadre de votre structure le permet.

## Ce que je m'engage à faire du résultat

Je dois être franc sur un point, sans quoi la proposition serait malhonnête : **la discipline
considère cette question comme tranchée depuis deux siècles.** Je n'attends pas de surprise sur
l'issue. Ce que j'attends, c'est une donnée qu'un sceptique puisse vérifier ligne par ligne, et
qui n'existe aujourd'hui nulle part en français.

Mes engagements, quelle que soit l'issue :

- publication du carnet brut intégral, sans tri ni retouche ;
- publication du résultat **même s'il contredit ce que j'espérais** — le protocole est symétrique
  et je l'ai accepté avant de vous écrire ;
- aucun droit de regard éditorial de ma part sur votre rapport technique, qui reste à ses auteurs ;
- crédit nominatif de l'équipe et de la structure, ou anonymat complet, à votre choix ;
- données brutes, photographies et paramètres météo sous licence ouverte.

Si vos participants souhaitent rédiger eux-mêmes la note d'interprétation, elle sera publiée
telle quelle et sans commentaire de ma part.

---

Je reste à votre disposition pour tout complément, et je comprendrai parfaitement un refus lié au
contexte exposé en ouverture. Si l'un des points techniques vous paraît discutable — et le budget
d'erreur en particulier —, je suis preneur de la critique : elle vaudra pour la suite du projet
même si la collaboration ne se fait pas.

Je vous prie d'agréer, Madame, Monsieur, l'expression de ma considération distinguée.

*[Nom, qualité, coordonnées]*
*terre-etendue-islam.fr*
*Dépôt public : [URL du dépôt]*

---

## Notes internes — non destinées à l'envoi

**Différence avec la lettre aux écoles de géomètres.** Celle-ci vise un public plus large et une
mesure plus légère. L'excès sphérique d'un grand triangle demande une station totale de classe 1″
et trois sommets de montagne ; la flèche sur un plan d'eau demande trois perches et une lunette.
Les deux campagnes sont indépendantes et se renforcent : l'une mesure une somme d'angles
comparée à 180°, l'autre un exposant comparé à 2. Aucune ne suppose la conclusion de l'autre.

**Le budget d'erreur est l'argument principal, pas un appendice.** C'est lui qui distingue cette
proposition des campagnes amateurs précédentes, et c'est lui qu'un interlocuteur technique lira
en premier. Il a d'ailleurs corrigé le protocole en cours de rédaction — le mentionner est un
gage de sérieux, pas un aveu de faiblesse.

**Ne pas promettre une issue.** La tentation est de présenter la campagne comme un test dont le
résultat serait incertain. Ce serait décrédibilisant auprès de quiconque connaît le dossier, et
inutile : la valeur du projet tient à la vérifiabilité du protocole, pas au suspense.

**À personnaliser avant envoi :** nom et qualité de l'expéditeur, URL du dépôt, site visé, et un
paragraphe d'accroche propre au destinataire. Une base nautique s'intéressera à la logistique et
à la visibilité ; un lycée à section topographie au format pédagogique et au budget d'erreur ; un
cabinet de géomètres-experts à la valeur de démonstration publique du métier ; une association
d'astronomie à la parenté avec les mesures de réfraction.
