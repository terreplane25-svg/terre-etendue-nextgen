---
title: "État des lieux : où en sommes-nous ?"
description: ".nx-nav{width:100%;background:#F7F2E8;border-bottom:1px solid #DDD5C5;padding:0 2rem;position:sticky;top:0;z-index:999} .nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;ju..."
date: "2026-04-17"
author: "Terre Etendue"
category: "headquarters"
tags: []
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

 

 
 - @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Outfit:wght@300;400;500;600&family=Amiri:ital,wght@0,400;0,700;1,400&family=Amiri:ital,wght@0,400;0,700;1,400&display=swap');
:root{--bg:#F7F2E8;--bg2:#EDE5D5;--bg3:#111;--gold:#B8860B;--gold-s:#B8962E;--gold-g:rgba(212,175,55,.12);--green:#1B5E3C;--green-l:#2D8B57;--green-g:rgba(45,106,79,.12);--cobalt:#1B5E3C;--cobalt-l:#2D8B57;--brown:#6B4226;--brown-l:#8B5C36;--t1:#2C1810;--t2:#5C4A3A;--t3:#8A7A6A;--bdr:#DDD5C5;--f1:'Cormorant Garamond',Georgia,serif;--f2:'Outfit',sans-serif;--f3:'Cormorant Garamond',Georgia,serif;--fa:'Amiri',serif}
.l2{background:var(--bg);color:var(--t1);padding:0}
.l2-h{padding:5rem 2rem 3.5rem;text-align:center;position:relative;overflow:hidden}
.l2-h::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 50% at 50% 30%,rgba(45,106,79,.05),transparent 70%);pointer-events:none}
.l2-tag{display:inline-block;font-family:var(--f2);font-size:.62rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--green-l);background:var(--green-g);border:1px solid rgba(45,106,79,.25);padding:.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.l2-title{font-family:var(--f1);font-size:clamp(1.8rem,4.5vw,2.6rem);font-weight:700;color:var(--green-l);line-height:1.15;margin:0 0 1rem;max-width:800px;margin-left:auto;margin-right:auto}
.l2-sub{font-family:var(--f3);font-size:1.02rem;line-height:1.7;color:var(--t2);max-width:650px;margin:0 auto 2rem}
.l2-meta{max-width:800px;margin:0 auto;padding:1.2em 0;border-top:1px solid var(--bdr);border-bottom:1px solid var(--bdr);display:flex;flex-wrap:wrap;gap:.5em 2em;font-family:var(--f2);font-size:.75rem;color:var(--t3)}
.l2-meta dt{font-weight:600;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem}
.l2-meta dd{margin:0 0 .6em;color:var(--t2)}
.l2-lay{display:flex;gap:2.5rem;max-width:1200px;margin:0 auto;padding:2.5rem 2rem 5rem;align-items:flex-start}
.l2-nav{flex:0 0 255px;position:sticky;top:80px;max-height:calc(100vh - 100px);overflow-y:auto;padding:1.5rem;background:var(--bg2);border:1px solid var(--bdr);border-radius:10px}
.l2-nav::-webkit-scrollbar{width:3px}.l2-nav::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}
.l2-nav__t{font-family:var(--f2);font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--green-l);margin:0 0 1rem;padding-bottom:.6rem;border-bottom:1px solid var(--bdr)}
.l2-nav ul{list-style:none;padding:0;margin:0}.l2-nav li{margin-bottom:.35rem}
.l2-nav a{display:block;font-family:var(--f2);font-size:.76rem;color:var(--t3);text-decoration:none;padding:.4em .8em;border-radius:5px;border-left:2px solid transparent;transition:all .25s ease;line-height:1.35}
.l2-nav a:hover{color:var(--t1);background:rgba(45,106,79,.06);border-left-color:var(--green-l)}
.l2-nav a.active{color:var(--green-l);background:var(--green-g);border-left-color:var(--green-l);font-weight:500}
.l2-nav .num{font-size:.6rem;font-weight:600;color:var(--green-l);margin-right:.4em;opacity:.7}
.l2-nav__bk{display:block;margin-top:1.2rem;padding:.6em 1em;background:var(--green-l);color:#2C1810;font-family:var(--f2);font-size:.72rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;text-align:center;border-radius:5px;transition:background .3s ease}
.l2-nav__bk:hover{background:#52B788}
.l2-b{flex:1;min-width:0;max-width:800px;font-family:var(--f3);font-size:clamp(1rem,1.8vw,1.08rem);line-height:1.75;color:var(--t1)}
.l2-b p{margin-bottom:1.4em;text-align:justify;hyphens:auto}
.l2-b a{color:var(--green-l);text-decoration:underline;text-underline-offset:3px}
.l2-b h2{font-family:var(--f1);font-size:clamp(1.4rem,3vw,1.85rem);font-weight:700;color:var(--t1);margin:3em 0 .8em;padding-bottom:.4em;border-bottom:1px solid var(--bdr);line-height:1.25;scroll-margin-top:90px}
.l2-b h3{font-family:var(--f2);font-size:clamp(1rem,1.8vw,1.15rem);font-weight:600;color:var(--green-l);text-transform:uppercase;letter-spacing:.06em;margin:2em 0 .6em;line-height:1.35;scroll-margin-top:90px}
.sn{font-family:var(--f2);font-size:.65rem;font-weight:600;color:var(--green-l);background:var(--green-g);border:1px solid rgba(45,106,79,.25);padding:.2em .6em;border-radius:3px;margin-right:.6em;vertical-align:middle}
.bqs{margin:2em 0;padding:1.5em 2em 1.5em 2.2em;background:linear-gradient(135deg,var(--gold-g),transparent 70%);border-left:3px solid var(--gold);border-radius:0 8px 8px 0;font-family:var(--f1);font-style:italic;font-size:1.05em;line-height:1.8;color:var(--gold)}
.bqs cite{display:block;margin-top:.8em;font-size:.75em;font-style:normal;font-family:var(--f2);color:var(--t3);text-transform:uppercase;letter-spacing:.06em}
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
@media(max-width:900px){.l2-lay{flex-direction:column;padding:1.5rem}.l2-nav{position:static;flex:none;width:100%;max-height:none;margin-bottom:2rem}.l2-h{padding:3.5rem 1.5rem 2.5rem}}


 Le Lab — LAB-2026-002
 
# État des lieux : où en sommes-nous ?

 Ce que nous avons établi. Ce qui reste ouvert. Ce que vous pouvez vérifier vous-même.
 
 AuteurTerre Étendue Islam
 DateAvril 2026 — v1.0
 Lecture~15 min
 NatureSynthèse globale du site
 

 
 
## Sommaire

 
 [01 Bilan des quatre piliers](#e-bilan)

 - [02 Ce que nous avons établi](#e-etabli)

 - [03 Ce qui reste ouvert](#e-ouvert)

 - [04 Ce que vous pouvez faire](#e-vous)

 - [05 Nos principes, rappelés](#e-principes)

 - [06 Mot de fin](#e-fin)

 

 [← Retour au Lab](/le-lab/)
 

## 01 Bilan des quatre piliers

Ce site s'articule autour de quatre sections. Chacune a produit des résultats documentés et vérifiables. Voici la carte complète de ce que nous avons couvert.


Le Nexus — 8 articles
**N1 — Pourquoi tout remettre en question.** L'épistémologie (Bacon, Bernard, Popper, Hacking, Woodward) montre que l'observation seule ne peut pas vérifier une théorie. La cosmologie est un domaine sans expérience possible.


**N2 — Cosmologies antiques.** Six civilisations indépendantes (Babylone, Égypte, Chine, Aztèques, Mayas, Incas) concevaient toutes la Terre comme plane. La sphéricité naît de l'ésotérisme pythagoricien, pas de l'observation.


**N3 — Ératosthène.** Sources fragmentaires (Cléomède, 5 siècles après), 7 erreurs identifiées par Pinotsis, méthode du Phare de Rawlins, non-discrimination de Brenner. Convention numérique, pas mesure expérimentale.


**N4 — La gravité.** 70+ théories, constante G instable à 5σ, anomalies Pioneer/Flyby/Allais non résolues, univers à 95% hypothétique, cosmologie plasma d'Alfvén comme alternative.


**N5 — Le concordisme.** Ratq/Fatq ≠ Big Bang (8 dictionnaires, 9 mufassirīn, 18 traditions). Ibn Taymiyyah sur la subordination de la Révélation. Cinq versets concordistes démontés.


L'Observatoire — 8 articles
**O1 — L'eau ne ment pas.** Formule de courbure (référence unique). Canal de Bedford, Grands Lacs (Chicago à 60 km), expériences laser, ingénierie (Suez 193 km 0 écluse, Alaska Pipeline 1 287 km modèle plan), marégraphes, absence de Coriolis sur les Grands Lacs.


**O2 — Visibilités.** Phares (Port-Saïd 18 m visible à 93 km), îles (Elbe 201 km depuis Gênes), montagnes (Denali 209 km), skylines (Chicago 97 km, NYC+Philly 193 km). Réfraction insuffisante (7–14%) pour ces écarts.


**O3 — Observations célestes.** Lune : lumière aux propriétés opposées au Soleil, croissant à contre-sens, éclipses selenelion. Soleil : taille angulaire stable (argument pour le modèle officiel reconnu honnêtement). Étoiles : constellations visibles au-delà des 90° théoriques.


**O4 — Optique et atmosphère.** Horizon au niveau des yeux à toute altitude. Réfraction quantifiée et insuffisante. Fata Morgana ≠ Chicago. Fisheye crée une courbure artificielle — objectif standard = horizon plat.


**O5 — Cartographie et Antarctique.** Cartes islamiques Sud en haut. Routes aériennes hémisphère Sud passant par le Nord. Boussole : un seul Nord fixe. Anomalie Cook (60 000 km). Neuschwabenland, timeline 1928–1959, Terre Marie Byrd, Soleil de Minuit, Traité de 1959, Byrd.


**O6 — Phénomènes physiques.** Pression atmosphérique (transition vide/non-vide). Lumière et couleurs (Rayleigh, grossissement solaire). Halos (5 types). Rayons crépusculaires (convergence et point chaud). Propagation EM sans satellites (ionosphère, Marconi 1901). Acoustique à grande distance.


La Bibliothèque — 5 articles
**B1 — Sept mots, un seul sens.** Sept termes coraniques convergent vers l'extension plane. Al-udḥiyy = nid aplani, pas œuf. Al-Rāzī reconnaît le sens littéral. Le Falak = Mawj al-Makfūf.


**B2 — Près de cent savants.** 95 autorités documentées — Compagnons, Tābiʿūn, mufassirīn, fuqahāʾ, linguistes. Distinction ʿulamāʾ al-sharʿ vs ahl al-hayʾa.


**B3 — Début de la Création.** 44 cours vidéo du Cheikh Mohammed Madany — cosmogonie coranique complète.


**B4 — Dhū al-Qarnayn.** Source boueuse (ʿayn ḥamiʾah), confins terrestres, hadith d'Abū Dharr, 6 exégètes unanimes, chronologie de la rupture ptoléméenne, poème pré-islamique d'Umayya.


**B5 — Le « consensus » sur la sphéricité.** 5 axes d'invalidation : anomalie philologique (حركاتها vs أجزائها), filiation ptoléméenne, 400 ans de silence, Ibn al-Munādī contre lui-même, Ibn Taymiyyah contre les Grecs.


Le Lab — 2 articles
**L1 — Le MGPP.** Modèle Géocentrique à Plans Parallèles : gravité comme force EM résiduelle, marées corrélées à la conductivité (test décisif), redshift par fatigue lumineuse, rotation stellaire par trois mécanismes convergents. 100% matière observable, zéro entité ad hoc.


**L2 — État des lieux.** Cet article.


## 02 Ce que nous avons établi

Dix-huit articles, des centaines de sources primaires (dictionnaires arabes, tafsīr classiques, revues scientifiques à comité de lecture, données d'ingénierie), et une méthodologie constante (distinguer le fait de l'interprétation, privilégier l'expérience sur l'observation, ne jamais plier la Révélation). Voici ce qui se dégage.


DomaineRésultat établiArticle(s)

ÉpistémologieL'observation seule ne peut pas vérifier une théorie — seule l'expérimentation le peutN1
HistoireLa sphéricité naît de l'ésotérisme, pas de l'observation. Toutes les civilisations antiques étaient Terre plateN2
ÉratosthèneConvention numérique, pas mesure. 7 erreurs, méthode du Phare, non-discriminationN3
Gravité70+ théories, G instable à 5σ, 95% hypothétique. Distances cosmologiques = inférences, pas mesuresN4
ConcordismeInnovation sémantique moderne sans précédent classique. Le Coran n'annonce pas le Big BangN5, B1
Eau et CoriolisCourbure observée nulle sur 10–1 287 km. Absence de déviation de Coriolis sur les Grands LacsO1
VisibilitéDizaines d'observations dépassant la courbure théorique de centaines à milliers de mètresO2
OptiqueL'horizon reste au niveau des yeux. La réfraction (7–14%) est insuffisante. Le fisheye crée la courbureO4
Phénomènes physiquesRayons crépusculaires convergents, propagation EM sans satellites (ionosphère), transition vide/atmosphère non résolueO6
LinguistiqueSept termes coraniques convergent unanimement vers l'extension plane. Zéro terme de sphéricitéB1
Savants95 autorités documentées affirment la planéité. La sphéricité = position des philosophes grecsB2
Dhū al-QarnaynLe récit présuppose une Terre à confins réels. 6 exégètes unanimes. Rupture métaphorique = influence ptoléméenneB4
ConsensusLe « consensus » d'Ibn Taymiyyah ne satisfait pas les critères d'un ijmāʿ sharʿī (5 axes d'invalidation)B5
ModèleLe MGPP montre qu'un cosmos cohérent sans entité invisible est concevable et falsifiableL1


## 03 Ce qui reste ouvert

L'honnêteté intellectuelle exige de reconnaître ce que nous n'avons pas résolu et les arguments qui restent en faveur du modèle officiel.


Arguments du modèle officiel que nous reconnaissons
**La taille angulaire du Soleil est stable** tout au long de la journée (~32 minutes d'arc). C'est cohérent avec un Soleil très lointain et constitue un argument en faveur du modèle officiel sur ce point précis (O3).


**La chute libre dans le vide** n'est pas pleinement expliquée par la densité et Archimède seuls (N4, reconnu explicitement).


**Le MGPP est un cadre heuristique**, pas un modèle achevé. Son programme de recherche (4 chantiers) reste à réaliser (L1).


**Les distances et dimensions du MGPP sont indicatives** et demandent un ajustement paramétrique global (chantier I).


Ces points ouverts ne sont pas des aveux de faiblesse — ils sont la marque d'une démarche honnête. Aucune théorie n'est achevée à son stade de développement. Ce qui compte, c'est que les limites soient reconnues, les pistes de résolution identifiées, et la falsifiabilité maintenue.


## 04 Ce que vous pouvez faire vous-même

La force de notre démarche est que la plupart de nos observations sont **reproductibles par n'importe qui**. Voici ce que vous pouvez vérifier depuis chez vous.


Expériences reproductibles
**Niveau d'eau sur un lac.** Placez un laser ou une cible au ras de l'eau sur un lac calme de 5–10 km. Comparez l'écart mesuré avec la courbure théorique (h = d² × 0,0785). Conditions : aube, vent nul. (O1)


**Visibilité au zoom.** Photographiez un objet « disparu sous l'horizon » (bateau, phare, skyline). Utilisez un téléobjectif puissant. La base revient-elle au zoom ? Si oui : pas de courbure. (O2)


**Horizon au niveau des yeux.** À n'importe quelle altitude (drone, montagne, avion), vérifiez si l'horizon est en dessous de vos yeux ou au même niveau. (O4)


**Planche de niveau.** Une planche de 2–3 m parfaitement de niveau sur deux trépieds : l'horizon s'aligne-t-il avec le bord supérieur sur 16 km ou descend-il vers les extrémités ? (O4)


**Boussole.** Vérifiez que toutes les boussoles du monde pointent vers le même point fixe au Nord. Y a-t-il un point fixe équivalent au Sud ? (O5)


**Croissant lunaire.** Par nuit claire avec un croissant, tracez une ligne imaginaire de la partie éclairée vers le Soleil (couché ou visible). Passe-t-elle par le Soleil ? (O3)


## 05 Nos principes, rappelés

**Principe 1 — Distinguer le fait de l'interprétation.** La chute d'un objet est un fait. L'appeler « gravité » est une interprétation. La trajectoire du soleil dans le ciel est un fait. L'appeler « rotation de la Terre » est une interprétation.
**Principe 2 — Privilégier l'expérience sur l'observation.** Un test reproductible sur un lac a plus de poids épistémique qu'une image satellite interprétée par une agence. L'expérience que tout le monde peut refaire vaut plus que l'observation que personne ne peut vérifier.
**Principe 3 — Ne jamais plier la Révélation.** Le concordisme est une erreur méthodologique et théologique. Le Coran est muhaymin — dominant, non dominé. Ses termes ont des sens précis, documentés par les Salaf et les dictionnaires. Nous les laissons dire ce qu'ils disent.
**Principe 4 — Appeler les choses par leur nom.** Une hypothèse est une hypothèse. Un consensus est un consensus, pas une preuve. Une inférence est une inférence, pas une mesure.

## 06 Mot de fin

Ce site n'est pas un manifeste ni un pamphlet. C'est un espace d'examen — un lieu où les paradigmes sont testés, les sources vérifiées, les termes définis, et les alternatives explorées. Chaque article cite ses sources. Chaque observation est documentée. Chaque argument est accompagné de ses contre-arguments.


Nous ne demandons à personne de nous croire. Nous demandons à chacun de vérifier. Les expériences sont reproductibles. Les dictionnaires sont consultables. Les sources scientifiques sont publiées. Les observations sont photographiées et filmées.


Si une seule chose devait rester de ce site, que ce soit celle-ci : **la vérité n'a pas besoin d'être protégée — elle a besoin d'être examinée.**


أَفَلَا يَنظُرُونَ إِلَى ٱلْإِبِلِ كَيْفَ خُلِقَتْ ۝ وَإِلَى ٱلسَّمَآءِ كَيْفَ رُفِعَتْ ۝
وَإِلَى ٱلْجِبَالِ كَيْفَ نُصِبَتْ ۝ وَإِلَى ٱلْأَرْضِ كَيْفَ سُطِحَتْ


« Ne considèrent-ils pas les chameaux, comment ils ont été créés ; et le ciel, comment il a été élevé ; et les montagnes, comment elles ont été dressées ; et la terre, comment elle a été étendue ? »
Sourate Al-Ghashiyah — 88:17-20

					

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