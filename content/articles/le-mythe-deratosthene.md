---
title: "Le mythe d'Ératosthène"
description: ".nx-nav{width:100%;background:#050505;border-bottom:1px solid #1A1A1A;padding:0 2rem;position:sticky;top:0;z-index:999} .nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;ju..."
date: "2026-04-15"
author: "Terre Etendue"
category: "headquarters"
tags: ["le-nexus"]
---

.nx-nav{width:100%;background:#050505;border-bottom:1px solid #1A1A1A;padding:0 2rem;position:sticky;top:0;z-index:999}
.nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:64px;gap:1.5rem}
/* Logo */
.nx-nav__logo{font-family:'Playfair Display',Georgia,serif;font-size:1.1rem;font-weight:700;color:#D4AF37;text-decoration:none;letter-spacing:-.01em;white-space:nowrap;flex-shrink:0}
.nx-nav__logo:hover{color:#E8C84A}
/* Liens */
.nx-nav__links{display:flex;align-items:center;gap:1.8rem;list-style:none;margin:0;padding:0}
.nx-nav__links a{font-family:'Montserrat',sans-serif;font-size:.73rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#9A9589;text-decoration:none;padding:.5em 0;position:relative;transition:color .3s ease;white-space:nowrap}
.nx-nav__links a::after{content:'';position:absolute;bottom:0;left:0;width:0;height:1px;background:#D4AF37;transition:width .3s ease}
.nx-nav__links a:hover{color:#E8E4DC}
.nx-nav__links a:hover::after{width:100%}
/* Dropdown À propos & Ressources */
.nx-nav__item-dropdown{position:relative}
.nx-nav__dropdown-toggle{font-family:'Montserrat',sans-serif;font-size:.73rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;background:none;border:none;color:#9A9589;cursor:pointer;padding:.5em 0;transition:color .3s ease;display:flex;align-items:center;gap:.4em;position:relative}
.nx-nav__dropdown-toggle::after{content:'';position:absolute;bottom:0;left:0;width:0;height:1px;background:#D4AF37;transition:width .3s ease}
.nx-nav__dropdown-toggle:hover{color:#E8E4DC}
.nx-nav__dropdown-toggle:hover::after{width:100%}
.nx-nav__dropdown-toggle svg{width:12px;height:12px;transition:transform .3s ease}
.nx-nav__dropdown-toggle.open svg{transform:rotate(180deg)}
.nx-nav__dropdown-menu{position:absolute;top:calc(100% + 12px);left:0;background:#0A0A0A;border:1px solid #1A1A1A;border-radius:8px;padding:.8rem 0;min-width:220px;opacity:0;visibility:hidden;transform:translateY(-10px);transition:all .3s ease;z-index:1000;box-shadow:0 8px 32px rgba(0,0,0,.4)}
.nx-nav__dropdown-menu.open{opacity:1;visibility:visible;transform:translateY(0)}
.nx-nav__dropdown-menu a{display:block;padding:.7em 1.2em;color:#9A9589;text-decoration:none;font-size:.72rem;letter-spacing:.08em;transition:all .3s ease;white-space:nowrap;position:relative}
.nx-nav__dropdown-menu a::after{display:none}
.nx-nav__dropdown-menu a:hover{background:rgba(212,175,55,.1);color:#E8E4DC;padding-left:1.6em}
/* Recherche */
.nx-nav__search{position:relative;flex-shrink:0}
.nx-nav__search-btn{background:none;border:none;cursor:pointer;color:#5C5850;font-size:1rem;padding:6px;transition:color .3s ease;display:flex;align-items:center}
.nx-nav__search-btn:hover{color:#D4AF37}
.nx-nav__search-box{position:absolute;top:calc(100% + 12px);right:0;width:0;opacity:0;overflow:hidden;transition:all .35s cubic-bezier(.16,1,.3,1);background:#0A0A0A;border:1px solid #1A1A1A;border-radius:8px;padding:0;z-index:1000}
.nx-nav__search-box.open{width:300px;opacity:1;padding:.6rem}
.nx-nav__search-input{width:100%;background:transparent;border:none;outline:none;font-family:'Montserrat',sans-serif;font-size:.82rem;color:#E8E4DC;padding:.4em .6em;caret-color:#D4AF37}
.nx-nav__search-input::placeholder{color:#5C5850}
/* Hamburger */
.nx-nav__toggle{display:none;background:none;border:none;cursor:pointer;padding:8px;flex-shrink:0}
.nx-nav__toggle span{display:block;width:22px;height:2px;background:#9A9589;margin:5px 0;transition:all .3s ease}
/* Mobile */
@media(max-width:900px){
 .nx-nav__toggle{display:block}
 .nx-nav__links{display:none;position:absolute;top:64px;left:0;right:0;background:#0A0A0A;border-bottom:1px solid #1A1A1A;flex-direction:column;padding:1rem 2rem;gap:0}
 .nx-nav__links.open{display:flex}
 .nx-nav__links li{width:100%}
 .nx-nav__links a{display:block;padding:.8em 0;border-bottom:1px solid #141414}
 .nx-nav__links li:last-child a{border-bottom:none}
 .nx-nav__item-dropdown{position:static}
 .nx-nav__dropdown-toggle{display:block;width:100%;padding:.8em 0;border-bottom:1px solid #141414;text-align:left;justify-content:space-between}
 .nx-nav__dropdown-menu{position:static;opacity:1;visibility:visible;transform:none;background:transparent;border:none;box-shadow:none;padding:0;max-height:0;overflow:hidden;transition:max-height .3s ease}
 .nx-nav__dropdown-menu.open{max-height:300px}
 .nx-nav__dropdown-menu a{padding:.6em 0 .6em 1.5em;border:none;background:none}
 .nx-nav__dropdown-menu a:hover{background:none;padding-left:2em}
 .nx-nav__search-box.open{width:calc(100vw - 4rem);right:-1rem}
}


 [Terre Étendue Islam](/)
 
 
 

 - [Le Nexus](/le-nexus/)

 - [L'Observatoire](/lobservatoire/)

 - [La Bibliothèque](/la-bibliotheque/)

 - [Le Lab](/le-lab/)

 
 - À propos
 
 
 [Manifeste](/manifeste/)
 [Éthique intellectuelle](/ethique-intellectuelle/)
 [Contact](/contact/)

 
 - Ressources
 
 
 [Glossaire](/glossaire/)
 [Index thématique](/index-thematique/)
 [Méthodologie](/methodologie/)

 

 
 - @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Outfit:wght@300;400;500;600&family=Amiri:ital,wght@0,400;0,700;1,400&family=Amiri:ital,wght@0,400;0,700;1,400&display=swap');
:root{--bg:#F7F2E8;--bg2:#EDE5D5;--bg3:#111;--gold:#B8860B;--gold-s:#B8962E;--gold-g:rgba(212,175,55,.12);--cobalt:#1B5E3C;--cobalt-l:#2D8B57;--cobalt-g:rgba(30,58,138,.15);--t1:#2C1810;--t2:#5C4A3A;--t3:#8A7A6A;--bdr:#DDD5C5;--f1:'Cormorant Garamond',Georgia,serif;--f2:'Outfit',sans-serif;--f3:'Cormorant Garamond',Georgia,serif}
.n3{background:var(--bg);color:var(--t1);padding:0}
.n3-h{padding:5rem 2rem 3.5rem;text-align:center;position:relative;overflow:hidden}
.n3-h::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 50% at 50% 30%,rgba(212,175,55,.04),transparent 70%);pointer-events:none}
.n3-tag{display:inline-block;font-family:var(--f2);font-size:.62rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);background:var(--gold-g);border:1px solid rgba(212,175,55,.2);padding:.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.n3-title{font-family:var(--f1);font-size:clamp(1.8rem,4.5vw,2.6rem);font-weight:700;color:var(--gold);line-height:1.15;margin:0 0 1rem;max-width:800px;margin-left:auto;margin-right:auto}
.n3-sub{font-family:var(--f3);font-size:1.02rem;line-height:1.7;color:var(--t2);max-width:650px;margin:0 auto 2rem}
.n3-meta{max-width:800px;margin:0 auto;padding:1.2em 0;border-top:1px solid var(--bdr);border-bottom:1px solid var(--bdr);display:flex;flex-wrap:wrap;gap:.5em 2em;font-family:var(--f2);font-size:.75rem;color:var(--t3)}
.n3-meta dt{font-weight:600;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem}
.n3-meta dd{margin:0 0 .6em;color:var(--t2)}
.n3-lay{display:flex;gap:2.5rem;max-width:1200px;margin:0 auto;padding:2.5rem 2rem 5rem;align-items:flex-start}
.n3-nav{flex:0 0 255px;position:sticky;top:80px;max-height:calc(100vh - 100px);overflow-y:auto;padding:1.5rem;background:var(--bg2);border:1px solid var(--bdr);border-radius:10px}
.n3-nav::-webkit-scrollbar{width:3px}
.n3-nav::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}
.n3-nav__t{font-family:var(--f2);font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--gold);margin:0 0 1rem;padding-bottom:.6rem;border-bottom:1px solid var(--bdr)}
.n3-nav ul{list-style:none;padding:0;margin:0}
.n3-nav li{margin-bottom:.35rem}
.n3-nav a{display:block;font-family:var(--f2);font-size:.76rem;color:var(--t3);text-decoration:none;padding:.4em .8em;border-radius:5px;border-left:2px solid transparent;transition:all .25s ease;line-height:1.35}
.n3-nav a:hover{color:var(--t1);background:rgba(212,175,55,.05);border-left-color:var(--gold)}
.n3-nav a.active{color:var(--gold);background:var(--gold-g);border-left-color:var(--gold);font-weight:500}
.n3-nav .num{font-size:.6rem;font-weight:600;color:var(--gold-s);margin-right:.4em;opacity:.7}
.n3-nav .sub{padding:0 0 0 1.2em;margin:.15rem 0 .2rem}
.n3-nav .sub a{font-size:.7rem;padding:.3em .8em}
.n3-nav__bk{display:block;margin-top:1.2rem;padding:.6em 1em;background:var(--gold);color:var(--bg);font-family:var(--f2);font-size:.72rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;text-align:center;border-radius:5px;transition:background .3s ease}
.n3-nav__bk:hover{background:#D4A017}
.n3-b{flex:1;min-width:0;max-width:800px;font-family:var(--f3);font-size:clamp(1rem,1.8vw,1.08rem);line-height:1.75;color:var(--t1)}
.n3-b p{margin-bottom:1.4em;text-align:justify;hyphens:auto}
.n3-b a{color:var(--gold);text-decoration:underline;text-underline-offset:3px;text-decoration-color:var(--gold-s)}
.n3-b h2{font-family:var(--f1);font-size:clamp(1.4rem,3vw,1.85rem);font-weight:700;color:var(--t1);margin:3em 0 .8em;padding-bottom:.4em;border-bottom:1px solid var(--bdr);line-height:1.25;scroll-margin-top:90px}
.n3-b h3{font-family:var(--f2);font-size:clamp(1rem,1.8vw,1.15rem);font-weight:600;color:var(--cobalt-l);text-transform:uppercase;letter-spacing:.06em;margin:2em 0 .6em;line-height:1.35;scroll-margin-top:90px}
.sn{font-family:var(--f2);font-size:.65rem;font-weight:600;color:var(--gold);background:var(--gold-g);border:1px solid rgba(212,175,55,.2);padding:.2em .6em;border-radius:3px;margin-right:.6em;vertical-align:middle}
.bq{margin:2em 0;padding:1.5em 2em;background:linear-gradient(135deg,var(--cobalt-g),transparent 70%);border-left:3px solid var(--cobalt);border-radius:0 8px 8px 0;font-family:var(--f3);font-style:italic;font-size:1.02em;line-height:1.75;color:var(--t1)}
.bq cite{display:block;margin-top:.8em;font-size:.78em;font-style:normal;font-family:var(--f2);color:var(--t3)}
.db{margin:2em 0;padding:1.4em 1.8em;background:var(--bg2);border:1px solid var(--bdr);border-radius:8px}
.db__l{display:inline-block;font-family:var(--f2);font-size:.65rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:var(--cobalt-l);background:var(--cobalt-g);padding:.2em .7em;border-radius:3px;margin-bottom:.8em}
.db p{font-size:.92rem;margin-bottom:.8em;text-align:left}
.kp{margin:1.5em 0;padding:1.2em 1.6em;background:var(--bg2);border-left:3px solid var(--gold);border-radius:0 8px 8px 0;font-family:var(--f2);font-size:.9rem;line-height:1.6;color:var(--t2)}
.kp strong{color:var(--t1)}
.tw{margin:2em 0;overflow-x:auto}
.tb{width:100%;border-collapse:collapse;font-family:var(--f2);font-size:.8rem}
.tb th{background:var(--bg2);color:var(--gold);font-weight:600;text-transform:uppercase;letter-spacing:.06em;font-size:.68rem;padding:.8em 1em;text-align:left;border-bottom:1px solid var(--bdr)}
.tb td{padding:.7em 1em;border-bottom:1px solid var(--bdr);color:var(--t2);vertical-align:top}
.tb tr:hover td{background:rgba(212,175,55,.03)}
.n3-refs{margin-top:3em;padding-top:2em;border-top:1px solid var(--bdr)}
.n3-refs h2{border-bottom:none;padding-bottom:0;font-size:1.3rem}
.n3-refs ol{padding-left:1.5em;font-family:var(--f2);font-size:.82rem;color:var(--t2);line-height:1.7}
.n3-refs li{margin-bottom:.6em}
@media(max-width:900px){
 .n3-lay{flex-direction:column;padding:1.5rem}
 .n3-nav{position:static;flex:none;width:100%;max-height:none;margin-bottom:2rem}
 .n3-h{padding:3.5rem 1.5rem 2.5rem}
}


 Le Nexus — NXS-2026-003
 
# Le mythe d'Ératosthène : déconstruction d'une légende scolaire

 Depuis les bancs de l'école, on nous raconte qu'un savant grec a « prouvé » que la Terre est ronde il y a 2 200 ans. L'examen des sources raconte une tout autre histoire.
 
 AuteurTerre Étendue Islam
 DateAvril 2026 — v1.0
 Lecture~35 min
 SourcesPinotsis 2006 · Rawlins 2008 · Brenner 2025
 

 
 
## Sommaire

 
 [01 Le récit scolaire](#e-intro)

 - [02 Des sources fragiles](#e-sources)
 [Cléomède](#e-cleomede)
- [Contexte politique](#e-politique)


 
 - [03 Sept erreurs (Pinotsis)](#e-erreurs)

 - [04 La méthode du Phare (Rawlins)](#e-phare)
 [Un Soleil 12× plus petit](#e-soleil)


 
 - [05 Non-discrimination (Brenner)](#e-brenner)

 - [06 Le problème du stade](#e-stade)

 - [07 Réplications modernes](#e-replications)

 - [08 Le paradoxe de la quasi-exactitude](#e-paradoxe)

 - [09 Conclusion](#e-ccl)

 - [Références](#e-refs)

 

 [← Retour au Nexus](/le-nexus/)
 

## 01 Le récit scolaire

L'histoire est connue de tous. Ératosthène de Cyrène (~276–194 av. J.-C.), directeur de la Bibliothèque d'Alexandrie, aurait observé qu'au solstice d'été, le Soleil tombait parfaitement à la verticale à Syène (Assouan) — sans ombre dans les puits — tandis qu'un gnomon projetait une ombre de 7,2° à Alexandrie. En postulant des rayons solaires parallèles et une distance de 5 000 stades entre les deux villes, il aurait calculé une circonférence terrestre de ~252 000 stades, soit ~39 000 km — à moins de 3% de la valeur moderne.


 📷 EMPLACEMENT IMAGE


 Schéma classique de l'expérience d'Ératosthène (version textbook)


 Terre sphérique, rayons solaires parallèles, gnomon à Alexandrie projette une ombre de 7,2°,
puits sans ombre à Syène. Annoter : 5 000 stades entre les deux villes.
C'est le schéma que tout le monde connaît — il sera contredit par le schéma suivant.


 Remplacer ce bloc par : ![\2](\1)


Ce récit est enseigné partout comme un modèle de science antique triomphante. Il constitue l'un des arguments les plus fréquemment invoqués en faveur de la sphéricité terrestre. Mais que disent réellement les sources ?


## 02 Des sources fragmentaires et tardives


### Cléomède : cinq siècles plus tard

Le récit détaillé de l'expérience ne provient pas d'Ératosthène. **Aucun texte de sa main ne nous est parvenu.** La source principale est Cléomède, philosophe stoïcien, dans son *De Motu Circulari* — daté de ~370 apr. J.-C., soit cinq à six siècles après les faits supposés. L'objectif de Cléomède n'était pas de transmettre un protocole expérimental, mais d'illustrer des principes philosophiques stoïciens.


**Détail systématiquement omis :** Cléomède ne dit pas que la distance de 5 000 stades a été *mesurée*. Il la qualifie de *prémisse* — c'est-à-dire de postulat de départ. Ératosthène n'a pas mesuré la distance : il l'a supposée.
Strabon mentionne deux valeurs contradictoires : 250 000 et 252 000 stades, sans jamais décrire la méthode. Pinotsis (2006) et Rawlins (2008) expliquent cette discordance : Ératosthène aurait arrondi à 252 000 pour obtenir 700 stades par degré (252 000 / 360°), un nombre commode, divisible par 60°. Ce n'est pas une correction empirique — c'est un **ajustement arithmétique de commodité**.


### Un contexte politique oublié

Ératosthène était un favori du régime théocratique sérapique des Ptolémées. Rawlins (2008) identifie une motivation institutionnelle : réduire le Soleil à une taille inférieure à la Terre n'était pas une erreur naïve — c'était un choix politiquement rentable. Reconnaître un Soleil immense aurait donné raison à Aristarque de Samos et menacé la cosmologie géocentrique que le pouvoir soutenait. La seule œuvre certaine d'Ératosthène — sa carte du monde — ne reflète d'ailleurs aucune révolution géodésique récente.


## 03 Sept catégories d'erreurs (Pinotsis 2006)

Antonios D. Pinotsis, professeur à l'Université d'Athènes, a publié en 2006 dans le *Journal of Astronomical History and Heritage* une analyse identifiant sept catégories d'erreurs dans la méthode d'Ératosthène.


#ErreurImpact

1Effet de pénombre du gnomonAngle réel 7°12', non 7,2°. Écart de 6'.
2Réfraction atmosphériqueBiais de 0,132' à Alexandrie (unilatéral → surestimation)
3Déviation de la verticale (rotation)0,0885° à Alexandrie → circonf. corrigée : 253 129 stades
4Aplatissement du géoïdeÉcart latitude géographique/géocentrique : γ = 0,18'
5Non-alignement sur un méridienSyène et Alexandrie décalées de ~3° en longitude
6Distance approximative (5 000 stades)Estimations de caravanes, pas de triangulation. Erreur ~2%.
7Position erronée de SyèneSyène à 8' au nord du tropique. Le « puits sans ombre » est inexact.


**Le paradoxe de la compensation :** Pinotsis reconnaît que ces erreurs se compensent mutuellement — certaines positives, d'autres négatives. Ce constat est épistémologiquement accablant : si les erreurs se compensent *par chance*, le résultat ne peut pas être attribué à la rigueur de la méthode. Une méthode fiable produit des résultats corrects *parce que* la méthode est bonne — non parce que les erreurs s'annulent fortuitement.

## 04 La vraie méthode : le Phare d'Alexandrie (Rawlins 2008)

Dennis Rawlins, historien des sciences et fondateur de la revue *DIO*, a publié en 2008 une analyse qui change radicalement la compréhension du calcul d'Ératosthène. En repartant des données d'Eusèbe de Césarée (*Præparatio Evangelica*, ~310 apr. J.-C.) — Lune à 780 000 stades, Soleil à 4 080 000 stades — Rawlins montre que le Soleil était placé à exactement 100 rayons terrestres, avec un rayon terrestre de 40 800 stades.


Or, la formule de visibilité du Phare d'Alexandrie (r = v² / 2h) avec une hauteur h ≈ 300 pieds grecs (½ stade) et une distance de visibilité v ≈ 202 stades, donne directement : r = (202)² / (2 × 0,5) = **40 804 stades ≈ 40 800 stades**. La méthode du Phare produit directement un *rayon* — jamais une circonférence. Or la méthode Syène-Alexandrie produit directement une *circonférence* (C = 50 × 5 000). Cette asymétrie arithmétique démontre que la mesure de base était le rayon, pas la circonférence — donc que c'est le Phare, et non le gnomon, qui est à l'origine du calcul.


### Un Soleil 12 fois plus petit que la Terre

Rawlins calcule que dans le modèle d'Ératosthène, le volume du Soleil est environ **1/12ᵉ de celui de la Terre**. Un Soleil minuscule qui ne peut pas expliquer la constance de sa taille apparente dans le ciel, ni les phases de la Lune, ni les éclipses. Ce n'est pas une erreur de mesure — c'est un choix idéologique : un Soleil immense aurait validé l'héliocentrisme d'Aristarque, menaçant le géocentrisme ptolémaïque.


## 05 Postulats arbitraires et non-discrimination (Brenner 2025)

Michael Brenner, ingénieur mécanicien et linguiste (Université de Technologie de Vienne), a souligné trois failles conceptuelles fondamentales.


**Le postulat des rayons parallèles est arbitraire.** Le Soleil est une source omnidirectionnelle. Si le Soleil est proche, ses rayons sont divergents, et la différence d'ombre entre Syène et Alexandrie s'explique sans Terre sphérique — simplement par la distance au point subsolaire.


**La parallaxe solaire n'a jamais été testée.** Pour discriminer entre Soleil lointain (rayons parallèles) et Soleil proche (rayons divergents), le test de la parallaxe était disponible et connu. Ératosthène ne l'a jamais effectué.


L'argument visuel décisif
💡 En termes simples


Imaginez que vous êtes dans une pièce fermée et que vous entendez un bruit derrière le mur. Ce bruit peut venir d'un chat ou d'un chien — le son seul ne vous permet pas de trancher. Il vous faudrait ouvrir la porte pour savoir. C'est exactement ce que dit Brenner : les ombres des gnomons sont le « bruit ». Elles sont compatibles avec deux modèles différents (globe + Soleil lointain, ou plan + Soleil proche). L'observation seule ne permet pas de trancher entre les deux — il faudrait une mesure supplémentaire (la parallaxe solaire) qu'Ératosthène n'a jamais faite.


Les deux modèles produisent exactement la même observation :


**Globe + Soleil lointain :** rayons parallèles → ombres différentes par courbure de la surface.


**Terre plane + Soleil local :** rayons divergents → ombres différentes par distance au point subsolaire.


Seule la mesure de la parallaxe solaire permettrait de les discriminer. Ératosthène ne l'a pas effectuée. Son expérience est *compatible* avec la sphéricité — elle ne la *démontre* pas.


 📷 EMPLACEMENT IMAGE


 Schéma alternatif — même résultat sur Terre plane avec Soleil proche


 Terre plane, Soleil local à ~5 000 km d'altitude. Rayons divergents.
Le gnomon à Alexandrie reçoit la lumière sous un angle de 7,2° par rapport à la verticale,
le puits à Syène reçoit la lumière à la verticale — mêmes observations, modèle différent.
Placer les deux schémas côte à côte (globe vs plan) pour montrer la non-discrimination.


 Remplacer ce bloc par : ![\2](\1)


## 06 Le problème du stade : une précision construite rétrospectivement


### La preuve historique : le « Ératosthène chinois » de la Terre plane

Cette non-discrimination n'est pas seulement théorique — elle a un **précédent historique documenté**. Au IIᵉ–Iᵉʳ siècle av. J.-C., les astronomes chinois du *Zhōu Bì Suàn Jīng* (周髀算經) ont effectué exactement la même expérience de gnomons qu'Ératosthène. Ils ont mesuré des ombres à différentes distances et appliqué la triangulation géométrique (le théorème de Pythagore, qu'ils connaissaient indépendamment sous le nom de *gōu-gǔ* 勾股).


Leur conclusion : le Soleil se trouve à **80 000 lǐ** (~40 000 km) au-dessus d'une Terre plane. Pas 150 millions de km autour d'une Terre sphérique. Les mêmes mesures, la même mathématique, un postulat de départ différent — et une conclusion radicalement opposée.


L'article académique de C. Cullen (Cambridge, *Bulletin of SOAS*, 1976), intitulé « A Chinese Eratosthenes of the Flat Earth », analyse en détail ce parallèle. Dirk L. Couprie (Springer, 2018) le confirme dans un chapitre entier intitulé « An Ancient Chinese Flat Earth Cosmology: Details and Calculations ». Ces deux publications universitaires à comité de lecture établissent que la méthode des gnomons est **intrinsèquement non-discriminante**.


**Ce que la Chine démontre définitivement :** Ératosthène n'a pas « mesuré la Terre ». Il a effectué un calcul dont le résultat dépend entièrement du postulat de départ. Les Chinois ont fait le même calcul avec le postulat inverse — et leur résultat est tout aussi cohérent mathématiquement. Affirmer que l'expérience d'Ératosthène « prouve » la sphéricité, c'est ignorer que la même expérience a été interprétée pendant plus de 1 500 ans par une civilisation sophistiquée comme une preuve d'un Soleil local.

## 07 Le problème du stade : une précision construite rétrospectivement


Type de stadeLongueurCirconférence calculéeÉcart / 40 075 km

« Stade d'Ératosthène » (Diller 1949)157,5 m39 690 km−1% ← choix rétrospectif
Stade olympique (mieux attesté)185 m46 620 km**+16,3%**
Stade attique177 m44 604 km+11,3%
Stade romain148,1 m37 321 km−6,9%


La « précision remarquable à 1% » n'existe que par un **choix rétrospectif** de la valeur du stade. La valeur de 157,5 m correspond à 1/10ᵉ du mille géographique (1 852 m) — unité définie au XVIIIᵉ siècle. Avec le stade olympique de 185 m, mieux attesté pour l'Alexandrie ptolémaïque, le résultat serait 46 620 km — une surestimation de 16%. Rawlins note que cette manipulation n'est plus prise au sérieux par les spécialistes (Dicks, Neugebauer, Berggren, Jones).


## 07 Les réplications scolaires : le test qui invalide


ContexteRésultatsÉcart maximal

Projet « Eratosthenes Experiment » (Europe, 2012–2020)36 000 – 46 000 km±14%
Réplications universitaires (France)37 000 – 45 000 km±12%
Classes primaires (gnomon simple)33 000 – 50 000 km±20%


Si la méthode produit une dispersion de ±15% même avec des coordonnées GPS exactes, des tables astronomiques modernes et des instruments calibrés, un résultat à ±1% ne peut pas être le fruit de cette méthode. Cela confirme que le chiffre d'Ératosthène est une **convention numérique** (700 stades/degré), pas une mesure expérimentale.


## 08 Le paradoxe de la quasi-exactitude

C'est le point décisif. Si la méthode avait été réellement expérimentale mais entachée de sept catégories d'erreurs cumulatives, le résultat aurait dû s'éloigner fortement de la réalité. Or l'écart est inférieur à 3% (avec le stade de 157,5 m). La probabilité que toutes ces erreurs se compensent est infinitésimale.


L'explication la plus parcimonieuse : le chiffre est une **convention arithmétique préétablie** — 700 stades par degré, choisie pour sa régularité, reprise par Hipparque puis Ptolémée, auto-validée par la continuité de son usage. La science moderne ne fait pas que « corriger » Ératosthène : elle reproduit et valide une valeur conventionnelle héritée, plutôt qu'elle ne l'établit de manière indépendante par une expérience falsifiable.


**Ce que l'argument « la science a progressé » ne résout pas :** Une science qui progresse reconnaît ses erreurs — ici, le mythe est maintenu et répété. Les erreurs sont fondamentales, pas mineures. Les réplications montrent ±15% de dispersion. La quasi-exactitude s'explique par une convention, pas par la rigueur. Et des tests empiriques plus rigoureux (Bedford Level, Lac Pontchartrain) sont falsifiables et reproductibles — deux qualités absentes de la méthode d'Ératosthène.

## 09 Conclusion

Pinotsis (2006) a identifié sept catégories d'erreurs dont les valeurs chiffrées montrent que chaque étape était biaisée. Rawlins (2008) a démontré que la mesure de base provenait probablement du Phare et que le Soleil d'Ératosthène était 12 fois plus petit que la Terre — un choix politique calculé. Brenner (2025) a établi que le postulat des rayons parallèles est non justifié et que l'expérience ne discrimine pas entre les deux modèles géométriques.


Ces trois analyses, menées indépendamment, convergent : le récit d'Ératosthène ne constitue pas une démonstration scientifique rigoureuse de la sphéricité terrestre. Le chiffre de ~252 000 stades est une **convention numérique transmise sans vérification indépendante**, non le fruit d'une mesure expérimentale.


Le cas Ératosthène expose une tension structurelle de la science elle-même : le récit prime sur l'expérience, la convention numérique sur la mesure indépendante, la cohérence de modèle sur la falsifiabilité, et l'autorité institutionnelle sur la reproductibilité. Reconnaître cela n'est pas rejeter la science — c'est exiger d'elle des expériences falsifiables, des protocoles reproductibles, et une vigilance constante face à ses propres mythes fondateurs.


## Références


 - Pinotsis, A.D. (2006). « The Significance and Errors of Eratosthenes' Method ». *Journal of Astronomical History and Heritage*, 9(1), 57–63.

 - Rawlins, D. (2008, rév. 2013). « Eratosthenes' Too-Big Earth & Too-Tiny Universe ». *DIO*, 14, 3–12.

 - Brenner, M. (2025). « Is Eratosthenes' method logical and reasonable? ». Réponse publiée, 23 février 2025.

 - Cléomède (~370 apr. J.-C.). *De Motu Circulari*, 1.10.

 - Strabon. *Géographie*, 2.5.7.

 - Eusèbe de Césarée (~310 apr. J.-C.). *Præparatio Evangelica*, 15.53.

 - Diller, A. (1949). « The ancient measurements of the earth ». *Isis*, 40(1), 6–9.

 - Heath, T.L. (1913). *Aristarchus of Samos: The Ancient Copernicus*. Oxford University Press.

 - Rowbotham, S.B. (1865). *Zetetic Astronomy: Earth Not a Globe*.

 - Dreyer, J.L.E. (1953). *A History of Astronomy from Thales to Kepler*. Dover.


					

.nx-footer{background:#050505;border-top:1px solid #1A1A1A;padding:4rem 2rem 2rem;font-family:'Montserrat',sans-serif}
.nx-footer__inner{max-width:1100px;margin:0 auto}
.nx-footer__grid{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:3rem;margin-bottom:3rem}
.nx-footer__brand-name{font-family:'Playfair Display',Georgia,serif;font-size:1.2rem;font-weight:700;color:#D4AF37;margin:0 0 1rem}
.nx-footer__brand-desc{font-family:'Source Serif 4',Georgia,serif;font-size:.88rem;line-height:1.65;color:#5C5850;margin:0 0 1.5rem}
.nx-footer__brand-verse{font-family:'Playfair Display',Georgia,serif;font-style:italic;font-size:.82rem;line-height:1.6;color:rgba(212,175,55,.4)}
.nx-footer__col-title{font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:#9A9589;margin:0 0 1.2rem}
.nx-footer__links{list-style:none;padding:0;margin:0}
.nx-footer__links li{margin-bottom:.7rem}
.nx-footer__links a{font-size:.82rem;color:#5C5850;text-decoration:none;transition:color .3s ease}
.nx-footer__links a:hover{color:#E8E4DC}
.nx-footer__sep{height:1px;background:#1A1A1A;margin-bottom:1.5rem}
.nx-footer__bottom{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem}
.nx-footer__copy{font-size:.72rem;color:#5C5850}
.nx-footer__socials{display:flex;gap:.8rem;align-items:center}
.nx-footer__socials a{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:6px;background:#0A0A0A;border:1px solid #1A1A1A;color:#5C5850;font-size:.75rem;text-decoration:none;transition:all .3s ease}
.nx-footer__socials a:hover{border-color:rgba(212,175,55,.3);color:#D4AF37;transform:translateY(-2px)}
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

 - [Contact](/contact/)

 

 © 2026 Terre Étendue Islam — Tous droits réservés · [Mentions légales](/mentions-legales/)


 [▶](https://www.youtube.com/@TERREETENDUE)
 [◉](https://odysee.com/@terreetendue)
 [✈](https://t.me/LATERREETENDUE)
 [♪](https://tiktok.com/@terreetendue1)