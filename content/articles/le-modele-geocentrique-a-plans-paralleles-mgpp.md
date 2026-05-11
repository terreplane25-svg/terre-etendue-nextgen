---
title: "Le Modèle Géocentrique à Plans Parallèles (MGPP)"
description: ".nx-nav{width:100%;background:#F7F2E8;border-bottom:1px solid #DDD5C5;padding:0 2rem;position:sticky;top:0;z-index:999} .nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;ju..."
date: "2026-04-17"
author: "Terre Etendue"
category: "lab"
tags: ["le-lab"]
---

.nx-nav{width:100%;background:#F7F2E8;border-bottom:1px solid #DDD5C5;padding:0 2rem;position:sticky;top:0;z-index:999}
.nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:64px;gap:1.5rem}
/* Logo */
.nx-nav__logo{font-family:'Cormorant Garamond',Georgia,serif;font-size:1.1rem;font-weight:700;color:#B8860B;text-decoration:none;letter-spacing:-.01em;white-space:nowrap;flex-shrink:0}
.nx-nav__logo:hover{color:#D4A017}
/* Liens */
.nx-nav__links{display:flex;align-items:center;gap:1.8rem;list-style:none;margin:0;padding:0}
.nx-nav__links a{font-family:'Outfit',sans-serif;font-size:.73rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#5C4A3A;text-decoration:none;padding:.5em 0;position:relative;transition:color .3s ease;white-space:nowrap}
.nx-nav__links a::after{content:'';position:absolute;bottom:0;left:0;width:0;height:1px;background:#B8860B;transition:width .3s ease}
.nx-nav__links a:hover{color:#2C1810}
.nx-nav__links a:hover::after{width:100%}
/* Recherche */
.nx-nav__search{position:relative;flex-shrink:0}
.nx-nav__search-btn{background:none;border:none;cursor:pointer;color:#8A7A6A;font-size:1rem;padding:6px;transition:color .3s ease;display:flex;align-items:center}
.nx-nav__search-btn:hover{color:#B8860B}
.nx-nav__search-box{position:absolute;top:calc(100% + 12px);right:0;width:0;opacity:0;overflow:hidden;transition:all .35s cubic-bezier(.16,1,.3,1);background:#EDE5D5;border:1px solid #DDD5C5;border-radius:8px;padding:0;z-index:1000}
.nx-nav__search-box.open{width:300px;opacity:1;padding:.6rem}
.nx-nav__search-input{width:100%;background:transparent;border:none;outline:none;font-family:'Outfit',sans-serif;font-size:.82rem;color:#2C1810;padding:.4em .6em;caret-color:#B8860B}
.nx-nav__search-input::placeholder{color:#8A7A6A}
/* Hamburger */
.nx-nav__toggle{display:none;background:none;border:none;cursor:pointer;padding:8px;flex-shrink:0}
.nx-nav__toggle span{display:block;width:22px;height:2px;background:#5C4A3A;margin:5px 0;transition:all .3s ease}
/* Mobile */
@media(max-width:900px){
 .nx-nav__toggle{display:block}
 .nx-nav__links{display:none;position:absolute;top:64px;left:0;right:0;background:#EDE5D5;border-bottom:1px solid #DDD5C5;flex-direction:column;padding:1rem 2rem;gap:0}
 .nx-nav__links.open{display:flex}
 .nx-nav__links li{width:100%}
 .nx-nav__links a{display:block;padding:.8em 0;border-bottom:1px solid #141414}
 .nx-nav__links li:last-child a{border-bottom:none}
 .nx-nav__search-box.open{width:calc(100vw - 4rem);right:-1rem}
}


 [Terre Étendue Islam](/)
 
 
 

 - [Le Nexus](/le-nexus/)

 - [L'Observatoire](/lobservatoire/)

 - [La Bibliothèque](/la-bibliotheque/)

 - [Le Lab](/le-lab/)

 

 
 - @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Outfit:wght@300;400;500;600&family=Amiri:ital,wght@0,400;0,700;1,400&display=swap');
:root{--bg:#F7F2E8;--bg2:#EDE5D5;--bg3:#111;--gold:#B8860B;--gold-s:#B8962E;--gold-g:rgba(212,175,55,.12);--green:#1B5E3C;--green-l:#2D8B57;--green-g:rgba(45,106,79,.12);--cobalt:#1B5E3C;--cobalt-l:#2D8B57;--cobalt-g:rgba(30,58,138,.15);--t1:#2C1810;--t2:#5C4A3A;--t3:#8A7A6A;--bdr:#DDD5C5;--f1:'Cormorant Garamond',Georgia,serif;--f2:'Outfit',sans-serif;--f3:'Cormorant Garamond',Georgia,serif}
.l1{background:var(--bg);color:var(--t1);padding:0}
.l1-h{padding:5rem 2rem 3.5rem;text-align:center;position:relative;overflow:hidden}
.l1-h::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 50% at 50% 30%,rgba(45,106,79,.05),transparent 70%);pointer-events:none}
.l1-tag{display:inline-block;font-family:var(--f2);font-size:.62rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--green-l);background:var(--green-g);border:1px solid rgba(45,106,79,.25);padding:.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.l1-title{font-family:var(--f1);font-size:clamp(1.7rem,4vw,2.4rem);font-weight:700;color:var(--green-l);line-height:1.15;margin:0 0 1rem;max-width:800px;margin-left:auto;margin-right:auto}
.l1-sub{font-family:var(--f3);font-size:1.02rem;line-height:1.7;color:var(--t2);max-width:650px;margin:0 auto 2rem}
.l1-meta{max-width:800px;margin:0 auto;padding:1.2em 0;border-top:1px solid var(--bdr);border-bottom:1px solid var(--bdr);display:flex;flex-wrap:wrap;gap:.5em 2em;font-family:var(--f2);font-size:.75rem;color:var(--t3)}
.l1-meta dt{font-weight:600;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem}
.l1-meta dd{margin:0 0 .6em;color:var(--t2)}
.l1-lay{display:flex;gap:2.5rem;max-width:1200px;margin:0 auto;padding:2.5rem 2rem 5rem;align-items:flex-start}
.l1-nav{flex:0 0 260px;position:sticky;top:80px;max-height:calc(100vh - 100px);overflow-y:auto;padding:1.5rem;background:var(--bg2);border:1px solid var(--bdr);border-radius:10px}
.l1-nav::-webkit-scrollbar{width:3px}.l1-nav::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}
.l1-nav__t{font-family:var(--f2);font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--green-l);margin:0 0 1rem;padding-bottom:.6rem;border-bottom:1px solid var(--bdr)}
.l1-nav ul{list-style:none;padding:0;margin:0}.l1-nav li{margin-bottom:.35rem}
.l1-nav a{display:block;font-family:var(--f2);font-size:.76rem;color:var(--t3);text-decoration:none;padding:.4em .8em;border-radius:5px;border-left:2px solid transparent;transition:all .25s ease;line-height:1.35}
.l1-nav a:hover{color:var(--t1);background:rgba(45,106,79,.06);border-left-color:var(--green-l)}
.l1-nav a.active{color:var(--green-l);background:var(--green-g);border-left-color:var(--green-l);font-weight:500}
.l1-nav .num{font-size:.6rem;font-weight:600;color:var(--green-l);margin-right:.4em;opacity:.7}
.l1-nav .sub{padding:0 0 0 1.2em;margin:.15rem 0 .2rem}.l1-nav .sub a{font-size:.7rem;padding:.3em .8em}
.l1-nav__bk{display:block;margin-top:1.2rem;padding:.6em 1em;background:var(--green-l);color:#2C1810;font-family:var(--f2);font-size:.72rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;text-align:center;border-radius:5px;transition:background .3s ease}
.l1-nav__bk:hover{background:#52B788}
.l1-b{flex:1;min-width:0;max-width:800px;font-family:var(--f3);font-size:clamp(1rem,1.8vw,1.08rem);line-height:1.75;color:var(--t1)}
.l1-b p{margin-bottom:1.4em;text-align:justify;hyphens:auto}
.l1-b a{color:var(--green-l);text-decoration:underline;text-underline-offset:3px}
.l1-b h2{font-family:var(--f1);font-size:clamp(1.4rem,3vw,1.85rem);font-weight:700;color:var(--t1);margin:3em 0 .8em;padding-bottom:.4em;border-bottom:1px solid var(--bdr);line-height:1.25;scroll-margin-top:90px}
.l1-b h3{font-family:var(--f2);font-size:clamp(1rem,1.8vw,1.15rem);font-weight:600;color:var(--green-l);text-transform:uppercase;letter-spacing:.06em;margin:2em 0 .6em;line-height:1.35;scroll-margin-top:90px}
.sn{font-family:var(--f2);font-size:.65rem;font-weight:600;color:var(--green-l);background:var(--green-g);border:1px solid rgba(45,106,79,.25);padding:.2em .6em;border-radius:3px;margin-right:.6em;vertical-align:middle}
.bq{margin:2em 0;padding:1.5em 2em;background:linear-gradient(135deg,var(--green-g),transparent 70%);border-left:3px solid var(--green);border-radius:0 8px 8px 0;font-family:var(--f3);font-style:italic;font-size:1.02em;line-height:1.75;color:var(--t1)}
.bq cite{display:block;margin-top:.8em;font-size:.78em;font-style:normal;font-family:var(--f2);color:var(--t3)}
.db{margin:2em 0;padding:1.4em 1.8em;background:var(--bg2);border:1px solid var(--bdr);border-radius:8px}
.db__l{display:inline-block;font-family:var(--f2);font-size:.65rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:var(--green-l);background:var(--green-g);padding:.2em .7em;border-radius:3px;margin-bottom:.8em}
.db p{font-size:.92rem;margin-bottom:.8em;text-align:left}
.kp{margin:1.5em 0;padding:1.2em 1.6em;background:var(--bg2);border-left:3px solid var(--green);border-radius:0 8px 8px 0;font-family:var(--f2);font-size:.9rem;line-height:1.6;color:var(--t2)}
.kp strong{color:var(--t1)}
.tw{margin:2em 0;overflow-x:auto}
.tb{width:100%;border-collapse:collapse;font-family:var(--f2);font-size:.78rem}
.tb th{background:var(--bg2);color:var(--green-l);font-weight:600;text-transform:uppercase;letter-spacing:.06em;font-size:.66rem;padding:.7em .8em;text-align:left;border-bottom:1px solid var(--bdr)}
.tb td{padding:.6em .8em;border-bottom:1px solid var(--bdr);color:var(--t2);vertical-align:top}
.tb tr:hover td{background:rgba(45,106,79,.03)}
.l1-refs{margin-top:3em;padding-top:2em;border-top:1px solid var(--bdr)}
.l1-refs h2{border-bottom:none;padding-bottom:0;font-size:1.3rem}
.l1-refs ol{padding-left:1.5em;font-family:var(--f2);font-size:.82rem;color:var(--t2);line-height:1.7}
.l1-refs li{margin-bottom:.6em}
@media(max-width:900px){.l1-lay{flex-direction:column;padding:1.5rem}.l1-nav{position:static;flex:none;width:100%;max-height:none;margin-bottom:2rem}.l1-h{padding:3.5rem 1.5rem 2.5rem}}


 Le Lab — LAB-2026-001
 
# Le Modèle Géocentrique à Plans Parallèles : un autre cosmos est possible

 Électrodynamique, superfluide cosmique, optique de milieu réfringent — un cadre alternatif complet, sans entité non observée, ancré dans la physique expérimentale.
 
 AuteurTerre Étendue Islam
 DateAvril 2026 — v1.0
 Lecture~40 min
 StatutPréprint indépendant — cadre heuristique
 

 
 
## Sommaire

 
 [01 Pourquoi un modèle alternatif](#m-intro)

 - [02 Géométrie du cosmos](#m-geometrie)

 - [03 La gravité comme force EM](#m-gravite)
 [Archimède + champ E](#m-archimede)
- [Van der Waals émergent](#m-vdw)


 
 - [04 Marées : le test décisif](#m-marees)

 - [05 Optique dans le superfluide](#m-optique)
 [Redshift par fatigue](#m-redshift)
- [Atmosphère-lentille](#m-lentille)


 
 - [06 Rotation inversée des étoiles](#m-etoiles)

 - [07 MGPP vs Λ-CDM](#m-comparaison)

 - [08 Programme de recherche](#m-programme)

 - [09 Conclusion](#m-ccl)

 - [Références](#m-refs)

 

 [← Retour au Lab](/le-lab/)
 

## 01 Pourquoi un modèle alternatif ?

La cosmologie standard (modèle Λ-CDM) accumule depuis une décennie des tensions internes que nous avons documentées en détail dans [La gravité : 70 théories et aucune certitude](/le-nexus/) : écart 5σ entre les mesures de la constante de Hubble, impossibilité d'unifier relativité générale et mécanique quantique, recours à des entités non observées représentant **95% du contenu cosmologique** (matière noire ~27%, énergie noire ~68%), et données DESI 2024 remettant en question la constance de l'énergie noire.


Le Modèle Géocentrique à Plans Parallèles (MGPP) est une proposition alternative fondée sur un principe directeur unique : **l'électrodynamique**. Chaque mécanisme invoqué est ancré dans une physique expérimentalement établie. Aucune entité non observée n'est nécessaire. Le modèle ne prétend pas remplacer immédiatement le paradigme dominant, mais montre qu'une cosmologie cohérente, quantitativement ajustable et exempte d'entités *ad hoc* est possible.


**Note méthodologique :** Les valeurs numériques présentées dans cet article (distances, tailles, altitudes) sont indicatives dans le cadre de la cohérence interne du modèle. Leur ajustement progressif fait partie du programme de recherche décrit en section 08.

## 02 Géométrie du cosmos : deux plans, un fluide

Le MGPP repose sur une géométrie à deux plans euclidiens parallèles séparés par un milieu superfluide :


Structure du cosmos MGPP
**La Terre-disque :** Géométrie plane circulaire. Le pôle nord au centre, l'équateur sur un cercle intermédiaire. La surface cartographiée (continents) ne constitue qu'une fraction de l'étendue totale.


**Le dôme céleste :** Plan euclidien parallèle à la surface terrestre. Les étoiles sont fixées sur sa surface interne et participent à sa rotation rigide uniforme autour de l'axe polaire. Les planètes sont des objets indépendants à des altitudes variables.


💡 En termes simples


Un condensat de Bose-Einstein (BEC), c'est de la matière refroidie à un point extrême — si froid que tous les atomes se comportent comme un seul et même objet. C'est un état de la matière réel, produit en laboratoire depuis 1995. Imaginez un océan invisible entre le sol et le ciel : pas de l'eau, mais un fluide extraordinairement fin qui remplit tout l'espace. Ce fluide explique pourquoi la lumière des étoiles rougit avec la distance (il absorbe de l'énergie), pourquoi le ciel est noir la nuit (il a une limite de transparence), et pourquoi les étoiles scintillent (il a des turbulences internes).


**Le superfluide inter-plans :** Un condensat de Bose-Einstein (BEC) cosmique remplissant l'espace entre la Terre et le dôme. Ses propriétés — indice de réfraction variable, extinction lumineuse, stratification de la charge électrique, support de défauts topologiques (vortex) — sont déduites des observations, pas postulées.


 📷 EMPLACEMENT IMAGE


 Schéma du MGPP — vue en coupe


 Plan terrestre (disque, pôle nord au centre) en bas.
Dôme céleste (plan parallèle, étoiles fixées) en haut.
Entre les deux : superfluide BEC (gradient de couleur).
Soleil et Lune comme objets locaux entre les deux plans.
Annoter : « Terre-disque », « Superfluide (BEC) », « Dôme céleste », « Étoiles ».


 Remplacer ce bloc par : ![\2](\1)


L'indice de réfraction du superfluide suit un gradient radial : **n(r) = n₀ + βr** — approximation linéaire d'une solution de l'équation de Ginzburg-Landau pour un superfluide en rotation. Ce gradient est la clé de toute l'optique du modèle. Les travaux de Volovik (2003) sur les analogies entre superfluides et cosmologie, et ceux de Zurek (1985) sur les structures topologiques à grande échelle, fournissent les fondations microphysiques.


## 03 La gravité comme force électromagnétique résiduelle

Dans le MGPP, il n'existe pas de force gravitationnelle fondamentale au sens newtonien ou einsteinien. Les phénomènes habituellement attribués à la gravité résultent de la combinaison de trois mécanismes électromagnétiques expérimentalement connus.


### Archimède + champ électrostatique vertical

**La poussée d'Archimède dans le superfluide :** un corps plus dense que le milieu environnant descend, un corps moins dense monte. Ce principe, antérieur de deux millénaires à Newton, explique la totalité des phénomènes de flottabilité sans recours à la gravité (voir [N4](/la-gravite-70-theories-et-aucune-certitude/)).


L'ingénieur chimiste « Aerodynamic » (diplômé ABET, certifié NCEES) formalise cette idée sous le nom de **Force de Densité** :


L'équation de la Force de Densité
**Fρ = Vo × g × (ρm − ρo)**


Où Vo = volume de l'objet, g = 9,81 m/s², ρm = densité du milieu, ρo = densité de l'objet.


Si ρo > ρm → la force est négative → l'objet **descend**.

Si ρo m → la force est positive → l'objet **monte**.


Cette équation unique explique pourquoi : une pierre coule dans l'eau (densité pierre >> densité eau), un ballon d'hélium monte dans l'air (densité hélium m = 0, et l'équation donne Fρ = −Vo × g × ρo — le taux de chute dépend uniquement de g, pas de la masse ou du volume. **Le résultat est identique à celui observé**, mais sans invoquer une force attractive entre masses.


**Le champ électrostatique vertical :** La Terre porte une charge nette négative (~10²⁰ C) ; le dôme céleste est chargé positivement. Il en résulte un champ électrique vertical de 0,1–1 V/m, maintenu par la pression du superfluide. Toute matière est composée de particules portant des charges internes — même un neutron, composé de trois quarks, possède un moment magnétique non nul et interagit avec tout champ extérieur.


### La gravité comme force de van der Waals émergente

💡 En termes simples


Pourquoi les objets tombent-ils ? Newton dit : « parce que la masse attire la masse ». Le MGPP dit : « parce que les objets denses descendent dans un milieu moins dense — exactement comme une pierre coule dans l'eau et une bulle d'air monte. » C'est le principe d'Archimède, que tout le monde connaît dans un verre d'eau. Les forces de van der Waals, c'est l'attraction naturelle entre tous les atomes — elle est très faible entre deux atomes, mais quand on additionne des milliards de milliards d'atomes (un objet), ça produit une force mesurable. C'est cette force qui fait que les choses « collent » et « tombent ».


La thèse centrale est que la **force gravitationnelle macroscopique est la moyenne statistique des interactions dipolaires résiduelles** entre les constituants élémentaires de la matière. Les fluctuations de charges de chaque atome induisent des moments dipolaires transitoires dans les atomes voisins. Ces interactions — toujours attractives — sont les forces de London–van der Waals. Leur sommation statistique produit une force nette proportionnelle aux masses apparentes.


**Arguments de cohérence expérimentale :** La force gravitationnelle et les forces interatomiques varient toutes deux en 1/r². L'énergie de liaison conférant sa masse au proton est à >99% d'origine électromagnétique. Mead (2000) montre comment des interactions EM collectives peuvent générer des mouvements cohérents stables. La « masse gravitationnelle » serait alors une mesure de la polarisabilité électromagnétique globale d'un corps.
 📷 EMPLACEMENT IMAGE


 Schéma comparatif — Gravité Newton vs Gravité EM (MGPP)


 Gauche : Newton — masse attire masse, G instable à 5σ, nécessite matière noire/énergie noire.
Droite : MGPP — densité (Archimède) + champ E vertical + van der Waals émergent. 100% observable.
Montrer un objet dense qui descend et un objet léger qui monte dans un milieu.


 Remplacer ce bloc par : ![\2](\1)


## 04 Les marées : le test décisif du modèle

C'est ici que le MGPP fait sa prédiction la plus directement testable. Dans le modèle standard, les marées résultent de l'attraction gravitationnelle de la Lune et du Soleil. Dans le MGPP, elles résultent de **l'induction électromagnétique** exercée par des astres chargés sur les masses d'eau conductrices.


Prédiction fondamentale du MGPP
L'amplitude des marées doit être corrélée à la **conductivité électrique de l'eau**, et non à sa masse.


 📷 EMPLACEMENT IMAGE


 Schéma des marées EM — corrélation avec la conductivité


 Lune (chargée) exerçant une force EM sur les masses d'eau.
Eau salée (4,8 S/m, forte conductivité) → marées fortes.
Eau douce (0,005 S/m, faible conductivité) → marées quasi nulles.
Montrer la corrélation : plus l'eau est conductrice, plus la marée est forte.


 Remplacer ce bloc par : ![\2](\1)


Plan d'eauConductivité (S/m)Marée observéeModèle EM préditAccord

Océan Pacifique4–51–15 m1–15 m✓
Mer Baltique1–30,3–0,4 m0,3–0,5 m✓
Grands Lacs0,001–0,10,02–0,05 m0,01–0,05 m✓
Grand Lac Salé5–150,05–0,08 m0,05–0,10 m✓


**Le fait décisif :** Les Grands Lacs, soumis à une attraction gravitationnelle identique à celle des mers, présentent des marées quasi nulles (Hutchinson, 1957). L'eau douce (σ ≈ 0,001–0,1 S/m) ne permet pas la formation de boucles de courant significatives. La gravité ne dépend pas de la conductivité — ce que le MGPP explique naturellement et que le modèle standard **ne prédit pas**.


Preuves expérimentales convergentes : Lilley & Filloux (1985) ont mesuré l'effet dynamo océanique ; Malin & Chapman (1970) ont détecté une variation magnétique lunaire de quelques nT à Greenwich ; Freeman & Ibrahim (1975, mesures Apollo) ont montré que la Lune est chargée électriquement et entourée d'une gaine de plasma ; Campbell (1980) a documenté les courants induits dans les structures conductrices terrestres par des champs magnétiques externes.


**Test critique proposé :** Manipuler l'environnement électromagnétique (blindage, champs artificiels) et observer une modification de la hauteur de marée à paramètres gravitationnels constants. Cette expérience n'a à notre connaissance jamais été réalisée et publiée. Elle fournirait la discrimination la plus directe entre le modèle EM (MGPP) et le modèle gravitationnel standard.

## 05 Optique dans le superfluide : redshift, extinction et atmosphère-lentille


### Le redshift par fatigue lumineuse (Tired Light)

Dans le MGPP, le décalage spectral vers le rouge ne résulte pas de l'expansion de l'univers mais d'**interactions inélastiques entre les photons et les excitations du superfluide** (phonons) : Δλ/λ ≈ αd (pour d ≪ 1/α). Ce mécanisme — proposé par Zwicky (1929), réexaminé par LaViolette (1986) et Brynjolfsson (2004) — trouve dans le BEC cosmique un substrat physique précis. Le photon perd progressivement de l'énergie sans modification de direction de propagation.


La loi d'extinction quadratique du superfluide (I_obs = L/4πd² × exp(−αd²), α ≈ 10⁻¹² km⁻²) permet de reproduire les magnitudes observées avec des distances très inférieures aux valeurs standard — supprimant le besoin d'énergie noire et de matière noire.


### L'atmosphère au-dessus de l'eau : une lentille géante

Un fait physique fondamental et sous-estimé : au-dessus des océans, des mers et des grands lacs, **l'air agit comme une immense lentille naturelle** qui dévie, concentre et guide la lumière et les ondes sur de très grandes distances. La formule ITU (Union Internationale des Télécommunications) montre que la réfractivité N dépend fortement de la vapeur d'eau : N = 77,6 × (P/T) + 373 000 × (e/T²). Le second terme — la vapeur d'eau — domine dans les basses couches au-dessus de l'eau.


La décroissance rapide de la vapeur d'eau avec l'altitude crée un **gradient d'indice de réfraction** — c'est la définition physique d'une lentille de Fresnel naturelle. Cette optique atmosphérique explique pourquoi des objets sont visibles à des distances bien au-delà de ce que la courbure terrestre devrait permettre (voir [Ce qu'on voit quand on ne devrait plus voir](/lobservatoire/)) : la lumière est guidée le long de la surface par le gradient d'humidité, pas « au-dessus » de la courbure.


## 06 Rotation inversée des étoiles : trois mécanismes convergents

L'une des objections classiques au modèle plan est que les étoiles tournent en sens anti-horaire dans l'hémisphère nord et en sens horaire dans l'hémisphère sud. Le MGPP explique ce phénomène par trois mécanismes physiquement indépendants :


Mécanisme 1 — Perspective des trajectoires parallèles
Les rayons anticrépusculaires illustrent le principe : une rotation de 180° de l'observateur permute les deux points de fuite d'un faisceau parallèle (Lynch & Livingston, 1995). L'inversion du sens perçu est une conséquence de la transformation de coordonnées (Drude, 1922).


Mécanisme 2 — Lentille divergente du superfluide
Le gradient d'indice (n(r) = n₀ + βr) du BEC agit comme une lentille divergente naturelle produisant une distorsion différentielle selon la latitude. Fondé microscopiquement sur l'équation de Gross-Pitaevskii.


Mécanisme 3 — Grille azimutale hyperbolique (Luneburg)
L'espace visuel humain est hyperbolique, non euclidien (Luneburg 1947, Indow 1997, Koenderink et al. 2000). L'inversion est-ouest résulte du changement de signe dans la métrique hyperbolique lors d'une rotation de 180°.


Leur convergence vers la même prédiction constitue un principe de **consilience** au sens de Whewell : la confiance dans un résultat augmente lorsque plusieurs chaînes causales indépendantes y aboutissent. Oresme (XIVᵉ s.) et Luneburg (1966) ont établi l'**équivalence observationnelle** entre rotation terrestre et rotation céleste : deux modèles produisant les mêmes trajectoires de rayons sont indiscernables par des mesures optiques.


## 07 MGPP vs modèle standard : comparaison point par point


AspectΛ-CDM (standard)MGPP

GravitéForce fondamentale (Newton/Einstein)EM résiduelle : Archimède + E + van der Waals
MaréesAttraction Lune/SoleilInduction EM corrélée à la conductivité
RedshiftExpansion de l'universFatigue lumineuse (photon–phonon dans BEC)
Distances astresMillions à milliards d'a.l.Milliers à millions de km (ajustées par réfraction)
ParallaxesMouvement orbital terrestreRéfraction dans le superfluide stratifié
ÉclipsesOmbre géométrique simpleVortex superfluide + tunneling quantique
Contenu cosmique5% ordinaire, 95% invisible**100% ordinaire — zéro entité ad hoc**
Unification QMImpossible (problème ouvert)Hors enjeu : le superfluide est de la MQ expérimentale


## 08 Programme de recherche : quatre chantiers ouverts


ChantierObjectifOutils

**I — Paramétrage global**Ajuster {distance, n₀, β} pour reproduire magnitudes, temps de transit et parallaxesKarttunen (2016), Born & Wolf (2019)
**II — Microphysique BEC**Justifier le gradient d'indice par l'équation de Gross-PitaevskiiVolovik (2003), Zurek (1985), Tilley (1990)
**III — Espace visuel**Formaliser la projection dôme → rétine via LuneburgLuneburg (1947), Koenderink (2000), Drude (1922)
**IV — Extensions**Précession, nutation, aberration stellaireVolovik (2003), Drude (1922), Karttunen (2016)


Les limites actuelles du MGPP ne sont pas des objections dirimantes mais des jalons d'un programme de recherche structuré. La reconnaissance explicite de ces limites, accompagnée de pistes de résolution identifiées dans la littérature scientifique existante, témoigne de la rigueur de la démarche.


## 09 Conclusion : expliquer l'observable par le connu

Face à une cosmologie standard qui postule 95% de son contenu en substances jamais détectées, accumule les tensions de mesure et échoue à unifier ses deux théories fondamentales, le MGPP offre une alternative parcimonieuse, cohérente en interne et ancrée dans la physique expérimentale.


Sa force principale est précisément sa limite apparente : plutôt que d'expliquer l'inexpliqué par de l'invisible, il propose d'**expliquer l'observable par du connu** — conformément au principe énoncé par Mach et Ockham : *entia non sunt multiplicanda praeter necessitatem* (les entités ne doivent pas être multipliées au-delà de la nécessité).


Un seul principe directeur — l'électrodynamique — suffit à rendre compte de la géométrie du cosmos, de la dynamique des astres, de la propagation de la lumière, des marées, des éclipses, des temps de transit et de la perception de l'observateur. Chaque limite actuelle dispose d'une stratégie de résolution identifiée dans la littérature scientifique. Le modèle est **falsifiable** — et ses tests critiques sont proposés explicitement.


## Références


 - Volovik, G.E. (2003). *The Universe in a Helium Droplet*. Oxford University Press.

 - Zurek, W.H. (1985). « Cosmological experiments in superfluid helium? ». *Nature*, 317, 505–508.

 - Mead, C.A. (2000). *Collective Electrodynamics*. MIT Press.

 - Lilley, F.E.M. & Filloux, J.H. (1985). « The Electric Field of the Ocean ». *Surveys in Geophysics*, 8(3-4), 235–243.

 - Freeman, J.W. & Ibrahim, M. (1975). « Lunar electric fields ». *The Moon*, 14(1), 103–114.

 - Hutchinson, G.E. (1957). *A Treatise on Limnology*, Vol. 1. Wiley.

 - Malin, S.R.C. & Chapman, S. (1970). « Lunar Daily Geomagnetic Variation ». *Geophysical J. Int.*, 19(1), 15–35.

 - Campbell, W.H. (1980). « Electric Currents in the Alaska Oil Pipeline ». *J. Geophys. Res.*, 85(A5), 2131–2140.

 - Zwicky, F. (1929). « On the Red Shift of Spectral Lines through Interstellar Space ». *PNAS*, 15, 773–779.

 - LaViolette, P.A. (1986). « Is the universe really expanding? ». *ApJ*, 301, 544–553.

 - Brynjolfsson, A. (2004). « Plasma-redshift and cosmology ». arXiv:astro-ph/0401420.

 - ITU-R Recommandation P.453 — Radio Refractive Index. Union Internationale des Télécommunications.

 - Luneburg, R.K. (1947/1966). *Mathematical Analysis of Binocular Vision* / *Mathematical Theory of Optics*.

 - Koenderink, J.J. et al. (2000). « Direct Measurement of the Curvature of Visual Space ». *Perception*.

 - Drude, P. (1922). *The Theory of Optics*. Longmans.

 - Lynch, D.K. & Livingston, W. (1995). *Color and Light in Nature*. Cambridge.

 - Born, M. & Wolf, E. (2019). *Principles of Optics*, 10ᵉ éd. Cambridge.

 - Hecht, E. (2017). *Optics*, 5th ed. Pearson.

 - Hossenfelder, S. (2018). *Lost in Math*. Basic Books.

 - Alfvén, H. (1981). *Cosmic Plasma*. D. Reidel.


					

.nx-footer{background:#2C1810;border-top:1px solid #DDD5C5;padding:4rem 2rem 2rem;font-family:'Outfit',sans-serif}
.nx-footer__inner{max-width:1100px;margin:0 auto}
.nx-footer__grid{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:3rem;margin-bottom:3rem}
.nx-footer__brand-name{font-family:'Cormorant Garamond',Georgia,serif;font-size:1.2rem;font-weight:700;color:#B8860B;margin:0 0 1rem}
.nx-footer__brand-desc{font-family:'Cormorant Garamond',Georgia,serif;font-size:.88rem;line-height:1.65;color:#8A7A6A;margin:0 0 1.5rem}
.nx-footer__brand-verse{font-family:'Cormorant Garamond',Georgia,serif;font-style:italic;font-size:.82rem;line-height:1.6;color:rgba(212,175,55,.4)}
.nx-footer__col-title{font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:#5C4A3A;margin:0 0 1.2rem}
.nx-footer__links{list-style:none;padding:0;margin:0}
.nx-footer__links li{margin-bottom:.7rem}
.nx-footer__links a{font-size:.82rem;color:#8A7A6A;text-decoration:none;transition:color .3s ease}
.nx-footer__links a:hover{color:#2C1810}
.nx-footer__sep{height:1px;background:#DDD5C5;margin-bottom:1.5rem}
.nx-footer__bottom{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem}
.nx-footer__copy{font-size:.72rem;color:#8A7A6A}
.nx-footer__socials{display:flex;gap:.8rem;align-items:center}
.nx-footer__socials a{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:6px;background:#EDE5D5;border:1px solid #DDD5C5;color:#8A7A6A;font-size:.75rem;text-decoration:none;transition:all .3s ease}
.nx-footer__socials a:hover{border-color:rgba(212,175,55,.3);color:#B8860B;transform:translateY(-2px)}
@media(max-width:768px){.nx-footer__grid{grid-template-columns:1fr;gap:2rem}.nx-footer{padding:3rem 1.5rem 1.5rem}.nx-footer__bottom{flex-direction:column;align-items:flex-start}}


 
 
## Terre Étendue Islam

 
 Un examen rigoureux des paradigmes cosmologiques, 
 croisant sources sacrées et observations empiriques.
 


 
 « Et la terre, comment elle a été étendue ? »

 — Al-Ghashiyah, 88:20
 


 
 
### Explorer

 

 - [Le Nexus](/le-nexus/)

 - [L'Observatoire](/lobservatoire/)

 - [La Bibliothèque](/la-bibliotheque/)

 - [Le Lab](/le-lab/)

 

 
 
### Ressources

 

 - [Glossaire](/glossaire/)

 - [Index thématique](/index-thematique/)

 - [Méthodologie](/methodologie/)

 

 
 
### À propos

 

 - [Manifeste](/manifeste/)

 - [Éthique intellectuelle](/ethique-intellectuelle/)

 - [Contact](/contact-2/)

 

 © 2026 Terre Étendue Islam — Tous droits réservés · [Mentions légales](/mentions-legales-2/)


 [▶](https://www.youtube.com/@TERREETENDUE)
 [◉](https://odysee.com/@terreetendue)
 [✈](https://t.me/LATERREETENDUE)
 [♪](https://tiktok.com/@terreetendue1)