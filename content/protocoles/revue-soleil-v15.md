# Revue du protocole solaire, en vue d'une version 1.5

**Document de travail. Rien n'est modifié dans `soleil-bilingue.html` tant que
cette revue n'est pas validée.**

La version 1.4 a été relue en entier, ses chiffres recalculés un par un. Ce
document dit ce qui ne tient pas, ce qui manque au regard des phénomènes qu'il
faut désormais prendre en compte, et ce que je propose d'écrire. Il ne modifie
rien.

---

## Ce que la 1.4 fait déjà, et qu'il ne faut pas défaire

Le protocole est solide et il porte déjà l'appareil complet : le choix du
diamètre horizontal et sa justification, le critère des 50 % qui neutralise
l'exposition, les deux contrôles positifs sur la Lune, le piège de la dérive
orbitale, la distinction géocentrique/topocentrique, la zone morte qui signale
un défaut de protocole plutôt qu'un résultat, et la sortie « projection » avec
son prix — trois nombres à reproduire simultanément.

Les chiffres instrumentaux se recalculent juste : à 400 mm sur plein format
échantillonné à 4 000 pixels, l'échelle vaut 3,094″/pixel, le disque couvre
611 pixels et 1 % vaut 6,1 pixels. Rien à reprendre.

---

## Trois contradictions internes

Elles sont du même genre que celles trouvées ailleurs dans le corpus : le
document se corrige à un endroit et garde l'ancienne valeur à deux autres.

### 1. Les « 14 % » du contrôle lunaire

La section 04 corrige explicitement, en signalant la faute de la version 1.1 :
356 500 et 406 700 km sont les extrêmes **pluriannuels**, un mois favorable
donne 12,0 % et un mois défavorable 9,5 %. Et elle conclut, justement : *« Le
test porte donc sur la loi, jamais sur une valeur pré-annoncée. »*

Or le résumé annonce toujours « valident la chaîne de mesure à 14 % », et la
procédure impose : *« Ne pas passer au Soleil tant que les 14 % ne sont pas
retrouvés. »* C'est exactement le critère que la section 04 déclare fautif. Un
observateur consciencieux, mesurant 9,5 % un mois défavorable, conclurait que sa
chaîne est en défaut et s'arrêterait là.

**À faire** : le résumé et la procédure adoptent le critère de la section 04 —
pente de θ contre 1/d égale à 1,000, dispersion autour de la droite. Aucune
valeur pré-annoncée nulle part.

### 2. Les « 1,7 % » du contrôle B

Même mécanisme. La section 04 corrige : le zénith est inaccessible à la plupart
des observateurs, et à Paris le signal vaut **1,42 %**, non 1,67 %. Le tableau 2
donne la valeur par latitude, de 1,52 % à l'équateur à 1,20 % à 65°.

Le résumé garde « puis à 1,7 % ». La procédure garde « tant que les 1,7 % ne
sont pas retrouvés ». Et la réponse à l'objection sur le grossissement
atmosphérique dit « plus petite de 1,7 % » là où il faut 1,42 % à Paris.

**À faire** : remplacer les trois occurrences par un renvoi au tableau 2, qui
donne la valeur à la latitude de l'observateur.

### 3. L'aplatissement à hauteur nulle

Le document annonce « jusqu'à 17 % à hauteur nulle ». Recalculé avec la formule
de Bennett, l'aplatissement vaut **10,4 % à 0°** et culmine vers **13,3 % à 1°**
de hauteur, parce que le gradient de réfraction, et non la réfraction elle-même,
est ce qui aplatit.

| hauteur | bord bas | bord haut | aplatissement |
|---|---|---|---|
| 0° | 34,5′ | 31,2′ | 10,4 % |
| 1° | 26,6′ | 22,4′ | **13,3 %** |
| 2° | 19,6′ | 17,0′ | 8,2 % |
| 5° | 10,3′ | 9,5′ | 2,7 % |
| 10° | 5,5′ | 5,3′ | 0,9 % |
| 15° | 3,7′ | 3,6′ | 0,4 % |

Les valeurs de la section 03 — « 15° → 0,4 % · 10° → 0,9 % » — sont justes et
concordent. C'est le seul « 17 % » qui ne l'est pas. À noter que la valeur
dépend du modèle de réfraction retenu : il faut nommer celui qu'on emploie
plutôt que citer un chiffre sans provenance.

**À faire** : corriger en 13 %, dire à quelle hauteur ce maximum se produit, et
nommer la formule employée.

---

## Quatre manques, au regard de ce qu'il faut prendre en compte

### A. La hauteur employée dans sin α est la hauteur **apparente**, pas la vraie

La procédure dit : *« La hauteur vraie du Soleil s'en déduit par éphéméride. »*
Mais l'observable est la direction dans laquelle on voit le disque, c'est-à-dire
la hauteur **apparente**, réfractée. Les deux ne coïncident pas, et l'écart
n'est pas négligeable devant le budget de 0,51 % :

| hauteur apparente | réfraction | écart induit sur sin α |
|---|---|---|
| 15° | 3,64′ | **0,40 %** |
| 20° | 2,70′ | 0,22 % |
| 30° | 1,72′ | 0,09 % |
| 45° | 0,99′ | 0,03 % |

À 15°, l'effet vaut les quatre cinquièmes du budget d'erreur total. Il ne change
pas la conclusion — le signal y est de 74 % — mais un protocole qui prétend au
demi-pourcent ne peut pas laisser passer un demi-pourcent sans le nommer.

**À faire** : une clause disant laquelle des deux hauteurs entre dans la
réduction, pourquoi, et comment on passe de l'une à l'autre. Et dire que la
comparaison des deux modèles se fait sur la **même** hauteur, faute de quoi on
compare deux choses différentes.

### B. Rien ne vérifie que la focale n'a pas bougé

Tout le protocole repose sur un rapport θ(20°)/θ(75°), qui est libre d'échelle
**à condition que la focale soit restée identique**. Le document l'impose —
bague immobilisée, mise au point verrouillée — et lui attribue 0,08 % au budget.
Mais rien ne le **vérifie** : si la bague glisse, ou si l'objectif respire à la
mise au point, la mesure sort fausse sans le moindre signe.

Il existe un étalon gratuit, présent sur chaque cliché : **la dérive du Soleil
lui-même**. Appareil fixe, sans suivi, le disque défile à 15,041″/s × cos δ,
soit 4,5 à 4,9 pixels par seconde à 400 mm. Une rafale de dix secondes à chaque
série donne l'échelle angulaire du moment, sans connaître la focale ni faire
confiance à ce qui est gravé sur la bague.

**À faire** : ajouter la rafale de dérive à la procédure, et remplacer le poste
« stabilité de la focale » du budget par une mesure au lieu d'une hypothèse.

### C. La projection ne prédit rien tant qu'elle n'a pas à répondre à deux stations

La section 02 traite honnêtement la sortie « le disque n'est pas l'astre » et
lui oppose son prix. Mais elle laisse cette classe de modèles hors de portée du
protocole, ce qui est vrai **d'un observateur isolé**.

Deux observateurs, au même instant, à des hauteurs solaires différentes, ferment
la sortie :

| hypothèse | station à 60° | station à 20° | rapport |
|---|---|---|---|
| source lointaine | 31,5′ | 31,5′ | 1,000 |
| source locale, hauteur finie | 27,3′ | 10,8′ | 0,395 |
| projection propre à l'observateur | **?** | **?** | **à énoncer** |

Le point n'est pas de piéger qui que ce soit : c'est qu'une projection qui ne
dit pas ce qu'elle prédit ici ne prédit rien du tout. Et le dispositif ne coûte
qu'un second participant.

**À faire** : une variante « deux stations » en section optionnelle, avec la
tolérance de simultanéité (une minute suffit : le Soleil ne bouge que de 0,25°).

### D. Deux objections nouvelles à traiter

**« Des vidéos montrent le Soleil changer de taille, filtre compris. »** C'est
la seule observation en circulation qui contredirait la source lointaine, et le
protocole doit la nommer plutôt que l'ignorer. La réponse tient en trois
points : ces enregistrements n'indiquent ni la focale, ni l'exposition, ni si le
disque était saturé — et un disque saturé s'élargit. Ce sont précisément les
trois grandeurs que ce protocole verrouille. **Si l'effet est réel, ce protocole
le trouve, et massivement.**

**« La diffusion près de l'horizon gonfle le disque. »** L'aureole de diffusion
peut élargir le limbe et fausser le critère des 50 % si le fond de ciel n'est
plus séparable du disque. Il faut un critère de rejet : écarter une série dont
le fond de ciel, mesuré à un rayon du bord, dépasse une fraction donnée du
plateau.

---

## Ce que je ne propose pas de toucher

La structure, les deux contrôles lunaires, le critère des 50 %, la zone morte,
les critères de décision a priori, l'engagement de publication. Tout cela tient.

Et la section 10 dit elle-même ce qui manque avant toute collecte : un
horodatage vérifiable par un tiers. C'est un dépôt, pas une réécriture — mais
c'est la condition pour que le reste vaille quelque chose.

---

## Décision demandée

1. Les trois corrections internes — 14 %, 1,7 %, aplatissement — sont-elles
   validées ? Elles ne changent aucune conclusion, elles suppriment des
   contradictions.
2. Les quatre ajouts — hauteur apparente, rafale de dérive, deux stations,
   deux objections — sont-ils retenus, en tout ou en partie ?
3. Y a-t-il des phénomènes que je n'ai pas vus et qu'il faut intégrer avant
   d'écrire la 1.5 ?
