---
title: "L'eau ne ment pas"
description: ".nx-nav{width:100%;background:#F7F2E8;border-bottom:1px solid #DDD5C5;padding:0 2rem;position:sticky;top:0;z-index:999} .nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;ju..."
date: "2026-04-15"
author: "Terre Etendue"
category: "observatory"
tags: ["lobservatoire"]
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
:root{--bg:#F7F2E8;--bg2:#EDE5D5;--bg3:#111;--gold:#B8860B;--gold-s:#B8962E;--gold-g:rgba(212,175,55,.12);--cobalt:#1B5E3C;--cobalt-l:#2D8B57;--cobalt-g:rgba(30,58,138,.15);--t1:#2C1810;--t2:#5C4A3A;--t3:#8A7A6A;--bdr:#DDD5C5;--f1:'Cormorant Garamond',Georgia,serif;--f2:'Outfit',sans-serif;--f3:'Cormorant Garamond',Georgia,serif}
.o1{background:var(--bg);color:var(--t1);padding:0}
.o1-h{padding:5rem 2rem 3.5rem;text-align:center;position:relative;overflow:hidden}
.o1-h::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 50% at 50% 30%,rgba(30,58,138,.05),transparent 70%);pointer-events:none}
.o1-tag{display:inline-block;font-family:var(--f2);font-size:.62rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--cobalt-l);background:var(--cobalt-g);border:1px solid rgba(30,58,138,.25);padding:.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.o1-title{font-family:var(--f1);font-size:clamp(1.8rem,4.5vw,2.6rem);font-weight:700;color:var(--cobalt-l);line-height:1.15;margin:0 0 1rem;max-width:800px;margin-left:auto;margin-right:auto}
.o1-sub{font-family:var(--f3);font-size:1.02rem;line-height:1.7;color:var(--t2);max-width:650px;margin:0 auto 2rem}
.o1-meta{max-width:800px;margin:0 auto;padding:1.2em 0;border-top:1px solid var(--bdr);border-bottom:1px solid var(--bdr);display:flex;flex-wrap:wrap;gap:.5em 2em;font-family:var(--f2);font-size:.75rem;color:var(--t3)}
.o1-meta dt{font-weight:600;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem}
.o1-meta dd{margin:0 0 .6em;color:var(--t2)}
.o1-lay{display:flex;gap:2.5rem;max-width:1200px;margin:0 auto;padding:2.5rem 2rem 5rem;align-items:flex-start}
.o1-nav{flex:0 0 255px;position:sticky;top:80px;max-height:calc(100vh - 100px);overflow-y:auto;padding:1.5rem;background:var(--bg2);border:1px solid var(--bdr);border-radius:10px}
.o1-nav::-webkit-scrollbar{width:3px}.o1-nav::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}
.o1-nav__t{font-family:var(--f2);font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--cobalt-l);margin:0 0 1rem;padding-bottom:.6rem;border-bottom:1px solid var(--bdr)}
.o1-nav ul{list-style:none;padding:0;margin:0}.o1-nav li{margin-bottom:.35rem}
.o1-nav a{display:block;font-family:var(--f2);font-size:.76rem;color:var(--t3);text-decoration:none;padding:.4em .8em;border-radius:5px;border-left:2px solid transparent;transition:all .25s ease;line-height:1.35}
.o1-nav a:hover{color:var(--t1);background:rgba(30,58,138,.06);border-left-color:var(--cobalt-l)}
.o1-nav a.active{color:var(--cobalt-l);background:var(--cobalt-g);border-left-color:var(--cobalt-l);font-weight:500}
.o1-nav .num{font-size:.6rem;font-weight:600;color:var(--cobalt-l);margin-right:.4em;opacity:.7}
.o1-nav .sub{padding:0 0 0 1.2em;margin:.15rem 0 .2rem}.o1-nav .sub a{font-size:.7rem;padding:.3em .8em}
.o1-nav__bk{display:block;margin-top:1.2rem;padding:.6em 1em;background:var(--cobalt-l);color:#fff;font-family:var(--f2);font-size:.72rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;text-align:center;border-radius:5px;transition:background .3s ease}
.o1-nav__bk:hover{background:#3B5FC8}
.o1-b{flex:1;min-width:0;max-width:800px;font-family:var(--f3);font-size:clamp(1rem,1.8vw,1.08rem);line-height:1.75;color:var(--t1)}
.o1-b p{margin-bottom:1.4em;text-align:justify;hyphens:auto}
.o1-b a{color:var(--cobalt-l);text-decoration:underline;text-underline-offset:3px}
.o1-b h2{font-family:var(--f1);font-size:clamp(1.4rem,3vw,1.85rem);font-weight:700;color:var(--t1);margin:3em 0 .8em;padding-bottom:.4em;border-bottom:1px solid var(--bdr);line-height:1.25;scroll-margin-top:90px}
.o1-b h3{font-family:var(--f2);font-size:clamp(1rem,1.8vw,1.15rem);font-weight:600;color:var(--cobalt-l);text-transform:uppercase;letter-spacing:.06em;margin:2em 0 .6em;line-height:1.35;scroll-margin-top:90px}
.sn{font-family:var(--f2);font-size:.65rem;font-weight:600;color:var(--cobalt-l);background:var(--cobalt-g);border:1px solid rgba(30,58,138,.25);padding:.2em .6em;border-radius:3px;margin-right:.6em;vertical-align:middle}
.bq{margin:2em 0;padding:1.5em 2em;background:linear-gradient(135deg,var(--cobalt-g),transparent 70%);border-left:3px solid var(--cobalt);border-radius:0 8px 8px 0;font-family:var(--f3);font-style:italic;font-size:1.02em;line-height:1.75;color:var(--t1)}
.bq cite{display:block;margin-top:.8em;font-size:.78em;font-style:normal;font-family:var(--f2);color:var(--t3)}
.db{margin:2em 0;padding:1.4em 1.8em;background:var(--bg2);border:1px solid var(--bdr);border-radius:8px}
.db__l{display:inline-block;font-family:var(--f2);font-size:.65rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:var(--cobalt-l);background:var(--cobalt-g);padding:.2em .7em;border-radius:3px;margin-bottom:.8em}
.db p{font-size:.92rem;margin-bottom:.8em;text-align:left}
.kp{margin:1.5em 0;padding:1.2em 1.6em;background:var(--bg2);border-left:3px solid var(--cobalt);border-radius:0 8px 8px 0;font-family:var(--f2);font-size:.9rem;line-height:1.6;color:var(--t2)}
.kp strong{color:var(--t1)}
.tw{margin:2em 0;overflow-x:auto}
.tb{width:100%;border-collapse:collapse;font-family:var(--f2);font-size:.8rem}
.tb th{background:var(--bg2);color:var(--cobalt-l);font-weight:600;text-transform:uppercase;letter-spacing:.06em;font-size:.68rem;padding:.8em 1em;text-align:left;border-bottom:1px solid var(--bdr)}
.tb td{padding:.7em 1em;border-bottom:1px solid var(--bdr);color:var(--t2);vertical-align:top}
.tb tr:hover td{background:rgba(30,58,138,.03)}
.o1-refs{margin-top:3em;padding-top:2em;border-top:1px solid var(--bdr)}
.o1-refs h2{border-bottom:none;padding-bottom:0;font-size:1.3rem}
.o1-refs ol{padding-left:1.5em;font-family:var(--f2);font-size:.82rem;color:var(--t2);line-height:1.7}
.o1-refs li{margin-bottom:.6em}
.n2-img{margin:2em 0;padding:1.2em;background:var(--bg2);border:1px dashed var(--bdr);border-radius:8px;text-align:center}
.n2-img__cap{font-family:var(--f2);font-size:.75rem;color:var(--t3);line-height:1.5;margin-top:.8em;font-style:italic}
@media(max-width:900px){.o1-lay{flex-direction:column;padding:1.5rem}.o1-nav{position:static;flex:none;width:100%;max-height:none;margin-bottom:2rem}.o1-h{padding:3.5rem 1.5rem 2.5rem}}


 L'Observatoire — OBS-2026-001
 
# L'eau ne ment pas : niveau, lacs, canaux et ingénierie

 L'eau obéit aux lois physiques, pas aux théories. Si la Terre est courbe, toute grande étendue d'eau devrait le montrer. Voici ce que l'observation révèle.
 
 AuteurTerre Étendue Islam
 DateAvril 2026 — v1.0
 Lecture~35 min
 DomaineObservations empiriques · Ingénierie
 

 
 
## Sommaire

 
 [00 La formule de courbure](#w-formule)

 - [01 L'eau trouve son niveau](#w-niveau)

 - [02 Canal de Bedford (1838)](#w-bedford)

 - [03 Les Grands Lacs](#w-lacs)
 [Remontée au zoom](#w-zoom)


 
 - [04 Expériences laser sur lac](#w-laser)

 - [05 L'ingénierie sans courbure](#w-ingenierie)
 [Canal de Suez](#w-suez)
- [Pipelines](#w-pipeline)


 
 - [06 Tableau de synthèse](#w-synthese)

 - [07 Marégraphes & océans](#w-maregraphes)

 - [08 Conclusion](#w-ccl)

 - [Références](#w-refs)

 

 [← Retour à l'Observatoire](/lobservatoire/)
 


## 00 La formule de courbure terrestre — référence pour tout le site

💡 En termes simples


Imaginez que la Terre est un ballon géant. Si vous posez une règle bien droite sur ce ballon, les deux bouts de la règle touchent la surface — mais au milieu, il y a un espace entre la règle et le ballon. C'est la « courbure ». Plus la règle est longue, plus l'espace au milieu est grand. La formule ci-dessous calcule exactement cet espace. Si la Terre est une sphère de 6 371 km de rayon, alors sur 10 km de distance, l'eau devrait former une « bosse » de presque 8 mètres — la hauteur d'un immeuble de 3 étages. C'est ce que nous allons tester.


Formule officielle de la géodésie
**h = d² × 0,0785 m/km²**


h = hauteur cachée par la courbure (en mètres) · d = distance (en kilomètres) · Rayon terrestre = 6 371 km


Cette formule est dérivée du modèle sphérique officiel. Les chiffres utilisés dans cet article et dans tout le site sont ceux du modèle lui-même — pas des approximations.


DistanceCourbure attendueÉquivalent concret

1 km0,08 m (8 cm)Imperceptible
5 km1,96 mHauteur d'une porte
10 km7,85 mImmeuble de 2-3 étages
20 km31,4 mImmeuble de 10 étages
50 km196 mUn grand building
100 km785 mUne montagne entière
193 km (Suez)2 930 mPresque 3 km de « bosse »


**Ce que ces chiffres impliquent :** Sur un lac de 20 km, la surface de l'eau devrait former une « bosse » de 31,4 m en son centre. Un laser au ras de l'eau d'une rive à l'autre devrait manquer la cible de plus de 31 m. C'est précisément ce que les expériences suivantes ont testé.
 📷 EMPLACEMENT IMAGE


 Schéma de la formule de courbure h = d²/2R


 Arc de cercle annoté avec la distance d, le rayon R=6371 km, et la hauteur cachée h.
Exemples visuels : à 10 km → 7,85 m / à 50 km → 196 m / à 100 km → 785 m.
Format : schéma vectoriel ou diagramme annoté, fond sombre.


 Remplacer ce bloc par : ![\2](\1)


## 01 L'eau trouve toujours son niveau

« L'eau trouve toujours son niveau » est l'un des principes physiques les plus anciens et les plus universellement observés. Des vases communicants aux océans, en passant par les niveaux à bulle et les canaux d'irrigation, ce principe est appliqué quotidiennement par des ingénieurs, des maçons et des agriculteurs du monde entier.


Le principe des vases communicants est démontrable avec deux récipients reliés par un tube : le niveau s'égalise toujours. C'est ce même principe qui a permis aux Romains de construire l'aqueduc du Pont du Gard — 50 km avec une pente de seulement 34 cm par kilomètre, sans jamais corriger une quelconque courbure.


Un argument particulièrement parlant est celui des grandes crues. Lors des inondations du Mississippi, du Nil ou de l'Amazone, l'eau se répand sur des plaines alluviales de 50 à 100 km de largeur, formant une nappe parfaitement plane. Sur 50 km, la courbure théorique au centre serait de **196 mètres**. Pourtant, les ingénieurs hydrauliciens qui modélisent ces inondations utilisent des modèles à surface plane — jamais à surface sphérique. La nappe est plate. Toujours.


## 02 Le Canal de Bedford : l'expérience fondatrice (1838)

Le canal Old Bedford, dans le Cambridgeshire (Angleterre), est rectiligne sur 9,66 km, parfaitement plat, avec une eau calme peu profonde. La courbure attendue sur cette distance est de **~7,32 mètres**.


En 1838, Samuel Birley Rowbotham s'allonge au ras de l'eau avec une longue-vue, l'œil à ~20 cm au-dessus du canal. Un assistant s'éloigne en bateau. Résultat : le bas du bateau — qui devrait être caché à 7 m sous l'horizon — **reste visible au ras de l'eau sur toute la distance**.


En 1870, Alfred Russel Wallace répète l'expérience avec trois cibles et affirme observer la courbure. En 1904, Lady Blount fait photographier un calicot blanc au ras de l'eau — il apparaît pleinement visible sur 9,66 km. Les résultats sont contradictoires, et la réfraction atmosphérique est invoquée comme facteur. Mais la question demeure : la réfraction peut-elle expliquer l'absence *totale* de 7,32 mètres de courbure au ras de l'eau ?


 📷 EMPLACEMENT IMAGE


 Photo ou gravure historique de l'expérience de Bedford Level (1838)


 Canal Old Bedford, Cambridgeshire, Angleterre. Vue du canal rectiligne.
Alternative : schéma de l'expérience (observateur au ras de l'eau + bateau à 9,66 km + courbure attendue en pointillé).


 Remplacer ce bloc par : ![\2](\1)


## 03 Les Grands Lacs : la courbure devrait être massive


ObservationDistanceCourbure attendueRésultat

Chicago depuis Michigan City~60 km~283 mBase des bâtiments visible au zoom
CN Tower depuis rive sud (Ontario)~52 km~212 mTour visible, base récupérable au zoom
Skyline Chicago depuis Indiana Dunes~50 km~196 mImmeubles entiers visibles par temps clair


Le skyline de Chicago est visible depuis Michigan City (Indiana), à ~60 km. Selon la formule, les 283 premiers mètres du bas devraient être cachés derrière la courbure. La Willis Tower culmine à 442 m — seuls les ~159 m supérieurs devraient être visibles. Pourtant, des photographes documentent depuis les années 2010 que le bas des bâtiments est visible bien au-delà de ce que la courbure permettrait.


### La remontée au zoom : le test décisif

Un objet qui semble avoir disparu derrière l'horizon peut souvent être « récupéré » visuellement en augmentant le grossissement optique d'un télescope ou d'un téléobjectif. La lecture officielle l'explique par la limite de résolution angulaire — l'objet devient trop petit pour l'œil nu. Mais si la courbure cachait physiquement le bas d'un bâtiment, aucun zoom ne devrait pouvoir le récupérer — car il serait derrière la surface courbe de l'eau, pas simplement trop petit.


**Le test clé :** Au zoom le plus puissant disponible, la base des bâtiments (niveau de la rue) est-elle visible depuis 60 km ? Si la courbure cache physiquement 283 m, aucun zoom ne peut récupérer cette information. Si elle est visible, c'est cohérent avec une surface plane. Ce test est reproductible par n'importe qui avec un bon téléobjectif depuis les rives du Lac Michigan.


## 04 Expériences laser sur lac

Un faisceau laser se propage en ligne droite absolue dans l'air. Si la surface de l'eau est courbée, un laser au ras de l'eau devrait frapper une cible à distance bien au-dessus du niveau de l'eau — la différence correspondant à la courbure. Sur 10 km, le laser devrait frapper ~7,85 m au-dessus de son point de départ.


Les mesures laser sur lac aboutissent systématiquement au même constat : **l'écart mesuré est nettement inférieur à la courbure théorique**. La lecture officielle attribue cet écart à la réfraction atmosphérique au ras de l'eau. La lecture alternative fait valoir que si la réfraction s'ajustait exactement pour masquer la courbure quelle que soit la distance, cela serait physiquement improbable.


Les expériences sérieuses sont effectuées à l'aube ou au coucher du soleil (gradient thermique minimal), vent nul, température constante. Les résultats, même dans ces conditions optimales, ne montrent pas la courbure attendue.


## 05 L'ingénierie sans courbure : canaux, pipelines, aqueducs

Si la courbure est significative sur des distances de plusieurs kilomètres, les ingénieurs qui construisent canaux, aqueducs et pipelines devraient l'intégrer dans leurs calculs. Le font-ils ?


### Le Canal de Suez : 193 km, zéro écluse

Le Canal de Suez (inauguré en 1869) s'étend sur 193 km entre la Méditerranée et la Mer Rouge. **Aucune écluse** sur toute sa longueur — l'eau circule librement. Selon la formule, la « bosse » théorique au milieu devrait être de **~2 930 mètres**. Une telle courbure rendrait impossible la circulation libre sans pompage colossal. Pourtant, le canal fonctionne parfaitement depuis 155 ans.


 📷 EMPLACEMENT IMAGE


 Photo aérienne ou coupe longitudinale du Canal de Suez


 193 km entre Méditerranée et Mer Rouge, 0 écluse.
Idéal : vue aérienne montrant la ligne droite du canal + annotation « 193 km, 0 écluse, 0 correction de courbure ».


 Remplacer ce bloc par : ![\2](\1)


### Pipelines transcontinentaux

Le Trans-Alaska Pipeline System (1 287 km) calcule la pression interne du fluide sur la base d'un **modèle de surface plane** pour les tronçons horizontaux. Aucune correction de courbure sphérique n'est intégrée dans les équations de pression hydraulique. De même pour les grands gazoducs sibériens et le pipeline Keystone (3 456 km).


 📷 EMPLACEMENT IMAGE


 Photo de l'Alaska Pipeline (Trans-Alaska Pipeline System)


 1 287 km de Prudhoe Bay à Valdez. Pipeline traversant le paysage enneigé.
Annotation : « 1 287 km — modèle hydraulique plan, aucune correction de courbure ».


 Remplacer ce bloc par : ![\2](\1)


OuvrageLongueurCourbure théoriqueÉcluses ?Courbure dans l'hydraulique ?

Canal de Suez193 km~2 930 mNonNon — eau libre
Canal de Panama82 km~527 mOui (terrain)Non — eau libre par paliers
Aqueduc de Nîmes (romain)50 km~196 mNonNon — pente 34 cm/km
Alaska Pipeline1 287 km~130 000 mN/ANon — modèle plan


**L'argument de l'ingénierie :** Des canaux sans écluses sur des centaines de kilomètres, des pipelines sur des milliers de kilomètres, des aqueducs romains sur 50 km — aucun n'intègre de correction de courbure dans le calcul de sa surface de référence hydraulique. Les ingénieurs traitent la surface de l'eau comme un plan. Depuis toujours.


## 06 L'absence de Coriolis sur les Grands Lacs

La **force de Coriolis** est un effet prédit par le modèle d'une Terre en rotation : tout objet en mouvement à la surface devrait être dévié vers la droite dans l'hémisphère nord, vers la gauche dans l'hémisphère sud. Cette déviation affecte théoriquement les courants océaniques, les systèmes météorologiques, et les grandes masses d'eau.


Les Grands Lacs nord-américains — avec des surfaces de 19 000 à 82 000 km² — devraient présenter une déviation de Coriolis mesurable sur leurs courants. Or les études limnologiques documentent que les courants des Grands Lacs sont dominés par le vent, la topographie des fonds et les différences de température — **la déviation de Coriolis y est au niveau du bruit de mesure** (Hutchinson, 1957).


**L'argument :** Si la Terre tourne à 1 600 km/h à l'équateur (~1 100 km/h à la latitude des Grands Lacs), une masse d'eau de 82 000 km² devrait montrer une déviation systématique et mesurable de ses courants. L'absence de cet effet observable sur des étendues aussi vastes est cohérente avec une Terre stationnaire.
Le modèle standard explique cette absence par la petite taille relative des lacs par rapport aux océans — mais une surface de 82 000 km² (Lac Supérieur) est comparable à la surface de l'Autriche. À cette échelle, Coriolis devrait être mesurable si la Terre tournait.


## 07 Tableau général de synthèse


ObservationDistanceCourbure attendueRésultat observé

Canal de Bedford (Rowbotham)9,66 km~7,32 mBateau visible au ras de l'eau
Canal de Bedford (Blount)9,66 km~7,32 mCalicot visible en photo
Lac Michigan — Chicago~60 km~283 mBase bâtiments visible au zoom
Lac Ontario — CN Tower~52 km~212 mBase récupérable au zoom
Laser sur réservoir~10 km~7,85 mÉcart bien inférieur
Canal de Suez (ingénierie)193 km~2 930 mSurface plate, 0 écluse
Alaska Pipeline (hydraulique)1 287 km~130 000 mModèle plan, opérationnel
Crues du Mississippi~50 km~196 mNappe plate, modèles plans


Sur toutes les distances testées — de 10 km à 1 287 km — la courbure observée est **nulle ou bien inférieure à la théorie**.


## 07 Marégraphes et niveau des océans

Le réseau mondial de marégraphes (PSMSL, plus de 2 000 stations) mesure le niveau de la mer sur tous les continents depuis le XIXᵉ siècle. Un fait remarquable : les niveaux moyens locaux, mesurés indépendamment sur tous les continents, **s'accordent à quelques centimètres près** — sans que ces stations soient reliées entre elles par autre chose que la surface de l'eau.


Ce fait est compatible avec les deux lectures : un géoïde sphérique (l'eau suit la gravité locale) ou une surface plane étendue (l'eau est au même niveau parce que la surface est plate). La question est : lequel de ces deux modèles prédit mieux l'ensemble des observations dans cet article ?


**Note sur l'altimétrie satellite :** Les mesures satellitaires de la surface des océans sont calculées à partir d'un modèle sphérique préalablement supposé (géoïde EGM2008). Elles ne constituent donc pas une preuve indépendante de la forme de la Terre — elles la présupposent.


## 08 Conclusion : reproduisez ces expériences

L'eau est le témoin le plus fiable dont nous disposons. Elle ne ment pas, ne se laisse pas influencer par des théories, et obéit uniquement aux lois physiques. Sur toutes les distances testées — du Canal de Bedford aux Grands Lacs, des expériences laser au Canal de Suez, des pipelines transcontinentaux aux crues des grands fleuves — la courbure attendue par le modèle sphérique n'est pas observée.


Chacune de ces observations est reproductible. Chacune est vérifiable. Et chacune pose la même question simple : si la Terre est courbée, pourquoi l'eau ne le montre-t-elle jamais ?


Reproduire vous-même
1. Identifier une étendue d'eau calme et rectiligne (canal, lac, réservoir).


2. Calculer la courbure attendue : h = d² × 0,0785.


3. Placer un laser ou une cible à hauteur connue au niveau de l'eau.


4. Mesurer où le laser frappe à la distance choisie.


5. Conditions idéales : aube ou coucher de soleil, vent nul, température stable.


6. Documenter les conditions météo pour évaluer la réfraction.


## Références


 - Rowbotham, S.B. (1865). *Zetetic Astronomy: Earth Not a Globe*. Chapitres I et II.

 - Wallace, A.R. (1870). Expérience du Canal de Bedford — rapport publié.

 - Blount, Lady E.A. (1904). Photographies du Canal de Bedford.

 - PSMSL — Permanent Service for Mean Sea Level. *psmsl.org*.

 - Suez Canal Authority. Données techniques et historiques du canal.

 - Trans-Alaska Pipeline System (Alyeska Pipeline). Documentation technique.

 - Formule géodésique standard : h = d²/(2R), R = 6 371 km.


					

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