---
title: "Pourquoi tout remettre en question"
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
:root {
 --nx-bg:#F7F2E8;--nx-bg2:#EDE5D5;--nx-bg3:#111111;
 --nx-gold:#B8860B;--nx-gold-soft:#B8962E;--nx-gold-glow:rgba(212,175,55,0.12);
 --nx-cobalt:#1B5E3C;--nx-cobalt-light:#2D8B57;--nx-cobalt-glow:rgba(30,58,138,0.15);
 --nx-text:#2C1810;--nx-text2:#5C4A3A;--nx-text3:#8A7A6A;--nx-border:#DDD5C5;
 --nx-sacred:'Cormorant Garamond',Georgia,serif;--nx-science:'Outfit',sans-serif;
 --nx-body:'Cormorant Garamond',Georgia,serif;--nx-arabic:'Amiri',serif;
}
.n1-article{background:var(--nx-bg);color:var(--nx-text);padding:0}
/* Hero */
.n1-hero{padding:5rem 2rem 3.5rem;text-align:center;position:relative;overflow:hidden}
.n1-hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 50% at 50% 30%,rgba(212,175,55,0.04),transparent 70%);pointer-events:none}
.n1-hero__tag{display:inline-block;font-family:var(--nx-science);font-size:0.62rem;font-weight:600;letter-spacing:0.18em;text-transform:uppercase;color:var(--nx-gold);background:var(--nx-gold-glow);border:1px solid rgba(212,175,55,0.2);padding:0.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.n1-hero__title{font-family:var(--nx-sacred);font-size:clamp(2rem,5vw,2.8rem);font-weight:700;color:var(--nx-gold);line-height:1.15;margin:0 0 1rem;max-width:750px;margin-left:auto;margin-right:auto}
.n1-hero__subtitle{font-family:var(--nx-body);font-size:1.05rem;line-height:1.7;color:var(--nx-text2);max-width:620px;margin:0 auto 2rem}
.n1-meta{max-width:800px;margin:0 auto;padding:1.2em 0;border-top:1px solid var(--nx-border);border-bottom:1px solid var(--nx-border);display:flex;flex-wrap:wrap;gap:0.5em 2em;font-family:var(--nx-science);font-size:0.75rem;color:var(--nx-text3)}
.n1-meta dt{font-weight:600;text-transform:uppercase;letter-spacing:0.08em;font-size:0.65rem}
.n1-meta dd{margin:0 0 0.6em;color:var(--nx-text2)}
/* Layout sidebar + corps */
.n1-layout{display:flex;gap:2.5rem;max-width:1200px;margin:0 auto;padding:2.5rem 2rem 5rem;align-items:flex-start}
/* Sidebar sommaire */
.n1-sidebar{flex:0 0 250px;position:sticky;top:80px;max-height:calc(100vh - 100px);overflow-y:auto;padding:1.5rem;background:var(--nx-bg2);border:1px solid var(--nx-border);border-radius:10px}
.n1-sidebar::-webkit-scrollbar{width:3px}
.n1-sidebar::-webkit-scrollbar-thumb{background:var(--nx-border);border-radius:3px}
.n1-sidebar__title{font-family:var(--nx-science);font-size:0.65rem;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;color:var(--nx-gold);margin:0 0 1rem;padding-bottom:0.6rem;border-bottom:1px solid var(--nx-border)}
.n1-sidebar__list{list-style:none;padding:0;margin:0}
.n1-sidebar__list li{margin-bottom:0.4rem}
.n1-sidebar__list a{display:block;font-family:var(--nx-science);font-size:0.78rem;color:var(--nx-text3);text-decoration:none;padding:0.45em 0.8em;border-radius:5px;border-left:2px solid transparent;transition:all 0.25s ease;line-height:1.4}
.n1-sidebar__list a:hover{color:var(--nx-text);background:rgba(212,175,55,0.05);border-left-color:var(--nx-gold)}
.n1-sidebar__list a.active{color:var(--nx-gold);background:var(--nx-gold-glow);border-left-color:var(--nx-gold);font-weight:500}
.n1-sidebar__num{font-size:0.62rem;font-weight:600;color:var(--nx-gold-soft);margin-right:0.4em;opacity:0.7}
.n1-sidebar__sub{list-style:none;padding:0 0 0 1.2em;margin:0.2rem 0 0.3rem}
.n1-sidebar__sub a{font-size:0.72rem;color:var(--nx-text3);padding:0.3em 0.8em}
.n1-sidebar__back{display:block;margin-top:1.2rem;padding:0.6em 1em;background:var(--nx-gold);color:var(--nx-bg);font-family:var(--nx-science);font-size:0.72rem;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;text-decoration:none;text-align:center;border-radius:5px;transition:background 0.3s ease}
.n1-sidebar__back:hover{background:#D4A017}
/* Corps article */
.n1-body{flex:1;min-width:0;max-width:800px;font-family:var(--nx-body);font-size:clamp(1rem,1.8vw,1.08rem);line-height:1.75;color:var(--nx-text)}
.n1-body p{margin-bottom:1.4em;text-align:justify;hyphens:auto}
.n1-body a{color:var(--nx-gold);text-decoration:underline;text-underline-offset:3px;text-decoration-color:var(--nx-gold-soft)}
.n1-body h2{font-family:var(--nx-sacred);font-size:clamp(1.5rem,3vw,1.9rem);font-weight:700;color:var(--nx-text);margin:3em 0 0.8em;padding-bottom:0.4em;border-bottom:1px solid var(--nx-border);line-height:1.25;scroll-margin-top:90px}
.n1-body h3{font-family:var(--nx-science);font-size:clamp(1.05rem,2vw,1.25rem);font-weight:600;color:var(--nx-cobalt-light);text-transform:uppercase;letter-spacing:0.06em;margin:2.2em 0 0.6em;line-height:1.35;scroll-margin-top:90px}
.n1-section-num{font-family:var(--nx-science);font-size:0.65rem;font-weight:600;color:var(--nx-gold);background:var(--nx-gold-glow);border:1px solid rgba(212,175,55,0.2);padding:0.2em 0.6em;border-radius:3px;margin-right:0.6em;vertical-align:middle}
/* Blocs */
.n1-quote{margin:2em 0;padding:1.5em 2em;background:linear-gradient(135deg,var(--nx-cobalt-glow),transparent 70%);border-left:3px solid var(--nx-cobalt);border-radius:0 8px 8px 0;font-family:var(--nx-body);font-style:italic;font-size:1.02em;line-height:1.75;color:var(--nx-text)}
.n1-quote cite{display:block;margin-top:0.8em;font-size:0.78em;font-style:normal;font-family:var(--nx-science);color:var(--nx-text3)}
.n1-quote-sacred{margin:2em 0;padding:1.5em 2em 1.5em 2.2em;background:linear-gradient(135deg,var(--nx-gold-glow),transparent 70%);border-left:3px solid var(--nx-gold);border-radius:0 8px 8px 0;font-family:var(--nx-sacred);font-style:italic;font-size:1.05em;line-height:1.8;color:var(--nx-gold)}
.n1-quote-sacred cite{display:block;margin-top:0.8em;font-size:0.75em;font-style:normal;font-family:var(--nx-science);color:var(--nx-text3);text-transform:uppercase;letter-spacing:0.06em}
.n1-data{margin:2em 0;padding:1.4em 1.8em;background:var(--nx-bg2);border:1px solid var(--nx-border);border-radius:8px}
.n1-data__label{display:inline-block;font-family:var(--nx-science);font-size:0.65rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;color:var(--nx-cobalt-light);background:var(--nx-cobalt-glow);padding:0.2em 0.7em;border-radius:3px;margin-bottom:0.8em}
.n1-data p{font-size:0.92rem;margin-bottom:0.8em;text-align:left}
.n1-keypoint{margin:1.5em 0;padding:1.2em 1.6em;background:var(--nx-bg2);border-left:3px solid var(--nx-gold);border-radius:0 8px 8px 0;font-family:var(--nx-science);font-size:0.9rem;line-height:1.6;color:var(--nx-text2)}
.n1-keypoint strong{color:var(--nx-text)}
.n1-table-wrap{margin:2em 0;overflow-x:auto}
.n1-table{width:100%;border-collapse:collapse;font-family:var(--nx-science);font-size:0.82rem}
.n1-table th{background:var(--nx-bg2);color:var(--nx-gold);font-weight:600;text-transform:uppercase;letter-spacing:0.06em;font-size:0.7rem;padding:0.8em 1em;text-align:left;border-bottom:1px solid var(--nx-border)}
.n1-table td{padding:0.7em 1em;border-bottom:1px solid var(--nx-border);color:var(--nx-text2);vertical-align:top}
.n1-table tr:hover td{background:rgba(212,175,55,0.03)}
.n1-refs{margin-top:3em;padding-top:2em;border-top:1px solid var(--nx-border)}
.n1-refs h2{border-bottom:none;padding-bottom:0;font-size:1.3rem}
.n1-refs ol{padding-left:1.5em;font-family:var(--nx-science);font-size:0.82rem;color:var(--nx-text2);line-height:1.7}
.n1-refs li{margin-bottom:0.6em}
/* Responsive */
@media(max-width:900px){
 .n1-layout{flex-direction:column;padding:1.5rem}
 .n1-sidebar{position:static;flex:none;width:100%;max-height:none;margin-bottom:2rem}
 .n1-hero{padding:3.5rem 1.5rem 2.5rem}
}


 Le Nexus — NXS-2026-001
 
# Pourquoi tout remettre en question

 Avant de parler de la Terre, du ciel ou des étoiles, il faut poser une question plus fondamentale : comment savons-nous ce que nous croyons savoir ?
 
 AuteurTerre Étendue Islam
 DateAvril 2026 — v1.0
 Lecture~25 min
 DomaineÉpistémologie & Méthodologie
 

 
 
## Sommaire

 
 [01 Observer n'est pas expérimenter](#s1)
 [Claude Bernard](#s1a)
- [Francis Bacon](#s1b)


 
 - [02 Prédire n'est pas prouver](#s2)
 [Exemples historiques](#s2a)
- [Karl Popper](#s2b)


 
 - [03 Sans intervention, pas de causalité](#s3)
 [Woodward](#s3a)
- [Hacking](#s3b)


 
 - [04 La cosmologie sans expérience](#s4)

 - [05 Les distances cosmologiques](#s5)
 [La parallaxe](#s5a)
- [L'échelle des distances](#s5b)
- [Le redshift](#s5c)


 
 - [06 Notre démarche](#s6)

 - [Références](#refs)

 

 [← Retour au Nexus](/le-nexus/)
 
On nous dit que la Terre est un globe tournant à 1 670 km/h sur elle-même, lancé à 107 000 km/h autour du Soleil, dans une galaxie qui file à 2,1 millions de km/h à travers un univers en expansion.


On nous dit que cette description est un *fait scientifique* — aussi certain que la chute d'une pomme ou l'ébullition de l'eau. Qu'il n'y a plus de débat depuis des siècles. Que toute personne qui pose des questions à ce sujet est irrationnelle, ignorante ou en proie à la conspiration.


Cet article ne prétend pas démontrer que ces affirmations sont fausses. Il pose une question préalable, plus fondamentale : **sur quels fondements reposent-elles ?** Sont-elles le fruit d'expériences reproductibles et vérifiables, ou d'observations lointaines interprétées à travers des modèles théoriques ? La distinction est essentielle — et c'est d'elle que dépend la suite de votre lecture sur ce site.


**Ce que cet article établit :** La cosmologie moderne repose sur l'observation, pas sur l'expérimentation. Or, la philosophie des sciences — de Bacon à Popper, de Claude Bernard à Hacking — montre que l'observation seule ne peut pas vérifier une théorie. Elle peut seulement la rendre plausible.

## 01 Observer n'est pas expérimenter

L'une des confusions les plus répandues dans le discours scientifique populaire est l'assimilation entre observation et expérience. On dit « la science a prouvé que... » sans jamais préciser *comment* cette preuve a été obtenue. Or, il existe une différence fondamentale entre ces deux démarches — et cette différence change tout.


### L'observateur constate, l'expérimentateur interroge

« L'observateur constate ; l'expérimentateur interroge. »— Claude Bernard, Introduction à l'étude de la médecine expérimentale, 1865
L'observation consiste à enregistrer passivement des phénomènes tels qu'ils se produisent dans la nature. L'observateur n'intervient pas — il se contente de noter. C'est ce que fait un astronome lorsqu'il mesure la trajectoire d'une planète ou enregistre la luminosité d'une étoile.


L'expérimentation, au contraire, implique une **intervention active** : le chercheur modifie une variable, maintient les autres constantes, et mesure les effets. C'est ce que fait un chimiste en laboratoire ou un ingénieur qui teste un matériau.


La distinction n'est pas secondaire. Claude Bernard soulignait déjà un danger : l'observation passive peut engendrer des corrélations trompeuses, des régularités apparentes qui ne reflètent aucune relation causale réelle. Voir que deux phénomènes se produisent ensemble ne prouve pas que l'un cause l'autre. Seule l'intervention permet de le tester.


### Francis Bacon : contraindre la nature à répondre

« Les secrets de la nature se révèlent plus aisément sous les contraintes de l'art que dans leur liberté naturelle. »— Francis Bacon, Novum Organum, 1620, Livre I, Aphorisme 98
Par « art », Bacon désigne les dispositifs expérimentaux. Son intuition est profonde : la nature, livrée à elle-même, ne « parle » pas spontanément. Elle doit être interrogée, contrainte, mise sous pression par l'expérimentateur. Sans cette contrainte, nos observations sont corrompues par ce que Bacon appelle les « idoles » — des biais cognitifs qui faussent systématiquement notre perception : les biais propres à l'espèce humaine (idoles de la tribu), les biais individuels (idoles de la caverne), ceux introduits par le langage (idoles du forum), et ceux liés aux systèmes philosophiques établis (idoles du théâtre).


Ces idoles corrompent inévitablement l'observation ordinaire. Seule l'expérimentation rigoureuse, en forçant la nature à répondre à des questions précises, peut les contourner.


## 02 Prédire n'est pas prouver

L'une des implications les plus importantes de cette distinction est que **le succès prédictif d'une théorie ne garantit pas sa vérité**. L'histoire des sciences est remplie de théories mathématiquement réussies qui se sont avérées fausses dans leurs prémisses fondamentales.


 Exemples historiques
 **Les épicycles de Ptolémée :** le modèle géocentrique, avec ses cercles sur des cercles, a prédit les positions planétaires avec précision pendant plus de mille ans. Il fonctionnait mathématiquement — et pourtant, même le modèle héliocentrique l'a remplacé.


 **La théorie du calorique :** au XVIIIᵉ siècle, la chaleur était expliquée par un fluide invisible. Cette théorie prédisait correctement de nombreux phénomènes thermiques. Elle fut abandonnée quand les expériences de Joule et Rumford montrèrent que la chaleur est une forme de mouvement mécanique.


 **L'espace absolu de Newton :** la mécanique newtonienne prédit le mouvement des corps avec une précision extraordinaire. Pourtant, son présupposé d'un espace et d'un temps absolus fut réfuté par la théorie de la relativité d'Einstein.


Le philosophe Larry Laudan a baptisé cette récurrence la « méta-induction pessimiste » : les théories passées qui semblaient vraies et prédictives ont été régulièrement remplacées. Pourquoi nos théories actuelles échapperaient-elles à ce destin ?


### Karl Popper : réfuter, jamais confirmer

« Aucun nombre d'observations de cygnes blancs ne peut justifier la conclusion que tous les cygnes sont blancs. Mais une seule observation d'un cygne noir suffit à réfuter cette conclusion. »— Karl Popper, La logique de la découverte scientifique, 1934
Accumuler des observations favorables ne prouve jamais rien de façon définitive. La vérification est asymétrique : on peut réfuter, mais jamais confirmer absolument. De plus, Popper souligne que toute observation est « imprégnée de théorie » — ce qu'on observe dépend des catégories conceptuelles et des présuppositions que l'on apporte à l'acte d'observer. Une observation ne peut donc pas servir d'arbitre neutre entre deux théories concurrentes.


## 03 Sans intervention, pas de causalité


### James Woodward : la définition interventionniste

« X est une cause de Y si et seulement si des interventions qui modifient X entraînent des modifications de Y. »— James Woodward, Making Things Happen, 2003
Cette définition est radicale : elle exclut les corrélations observationnelles de l'établissement de relations causales. Sans intervention, l'inférence causale reste sous-déterminée. Voir que A et B varient ensemble ne suffit pas à dire que A cause B — il faut pouvoir agir sur A et mesurer l'effet sur B dans des conditions contrôlées.


### Ian Hacking : si vous pouvez le manipuler, c'est réel

« Si vous pouvez les pulvériser, c'est qu'ils sont réels. »— Ian Hacking, Representing and Intervening, 1983
Ce n'est pas l'observation ni la théorie qui fonde la réalité d'un phénomène, mais la capacité à *intervenir* dessus. Hacking insiste : « L'expérience a une vie propre, indépendante de la théorie. » Les pratiques expérimentales produisent des phénomènes, créent des connaissances et établissent des réalités qui peuvent exister avant même qu'une théorie ne les explique.


## 04 La cosmologie : un domaine sans expérience possible

Appliquons maintenant ces principes à la cosmologie et à la gravitation. C'est précisément dans ces domaines que l'impossibilité expérimentale est la plus criante.


 Ce qu'on ne peut pas faire en cosmologie
 **Isoler la gravité :** contrairement à l'électromagnétisme (qu'on peut bloquer par une cage de Faraday), la gravité ne peut être ni écrantée ni annulée.


 **Déclencher ou éteindre la gravité :** aucune expérience ne peut « allumer » puis « éteindre » la gravité pour mesurer son effet par contraste.


 **Manipuler l'espace-temps :** à l'échelle humaine, il est impossible d'agir sur la géométrie de l'espace-temps pour en tester les effets.


 **L'Univers est unique :** il n'existe pas d'Univers « contrôle » avec lequel comparer. Toute observation cosmologique manque du groupe contrôle qui est la base de toute inférence expérimentale solide.


Cela signifie que la relativité générale d'Einstein — aussi élégante et prédictive soit-elle — demeure, dans le cadre interventionniste que nous venons de développer, une *hypothèse* plutôt qu'une loi vérifiée expérimentalement au sens strict. Ses vérifications portent sur des effets locaux (orbites planétaires, horloges GPS, fusion de trous noirs). L'extrapolation de ces succès à l'Univers entier — à des milliards d'années-lumière — est une inférence, pas une expérience.


## 05 « Mesurer » les étoiles : ce que les distances cosmologiques sont vraiment

Dans la vie courante, mesurer signifie comparer directement un objet à un étalon connu. On mesure une table avec un mètre. L'instrument est en contact — au moins indirect — avec ce qu'il mesure. En astronomie, la situation est radicalement différente. L'astronome ne peut pas tendre un mètre jusqu'à Andromède. Il doit *inférer* la distance à partir de ce qu'il observe, en s'appuyant sur des hypothèses.


### La parallaxe : la seule vraie mesure

La parallaxe trigonométrique est la seule méthode qui s'approche d'une mesure géométrique directe. Le principe est simple : on observe une étoile à six mois d'intervalle et on mesure son décalage angulaire apparent. Mais même avec la mission Gaia de l'Agence spatiale européenne, cette méthode reste impraticable au-delà de quelques kiloparsecs. Au-delà, aucune base géométrique directe n'existe.


### L'échelle des distances : une cascade d'hypothèses

 
 ÉchelonMéthodePortéeHypothèse requise
 
 1Parallaxe~kiloparsecsGéométrie + orbite terrestre
 2Céphéides~mégaparsecsLuminosité intrinsèque universelle
 3Supernovæ Ia~milliards d'alUniformité des explosions stellaires
 4RedshiftUnivers observableModèle cosmologique complet (Λ-CDM)
 
 
Chaque échelon hérite et amplifie les incertitudes des précédents. Une erreur systématique dans la calibration des céphéides se propage à toute l'échelle. Et les différentes méthodes ne sont pas vraiment indépendantes : elles partagent des hypothèses communes sur la physique stellaire et les corrections d'extinction.


### Le redshift ne mesure pas une distance

Le décalage vers le rouge (redshift) est un fait observationnel : la lumière d'une galaxie lointaine arrive avec ses longueurs d'onde allongées. C'est une mesure directe. Mais convertir ce décalage en distance n'est *pas* une mesure — c'est une interprétation qui nécessite un modèle cosmologique, une hypothèse sur l'expansion de l'Univers, et une valeur de la constante de Hubble. Edwin Hubble lui-même était prudent :


« Si le facteur de récession est abandonné, si les décalages spectraux ne sont pas principalement des décalages de vitesse, le tableau est simple et plausible. Il n'y a aucune preuve d'expansion et aucune restriction sur l'échelle temporelle. »— Edwin Hubble, The Observational Approach to Cosmology, 1937
La « tension de Hubble » confirme cette fragilité : les deux méthodes principales d'estimation de la constante H₀ donnent des résultats incompatibles à 5σ — un niveau de discordance statistiquement très significatif. Cela suggère soit des erreurs systématiques non identifiées, soit une physique au-delà du modèle standard.


## 06 Ce que les physiciens eux-mêmes admettent

L'argument central de ce site — que la forme et le mouvement de la Terre sont des questions ouvertes, pas des faits prouvés — peut sembler radical. Il ne l'est pas. Les plus grands physiciens du XXᵉ siècle ont dit exactement la même chose. Voici six citations directes, vérifiables dans les sources primaires :


« La lutte, si violente aux premiers jours de la science, entre les vues de Ptolémée et de Copernic serait alors tout à fait dépourvue de sens. L'un ou l'autre système de coordonnées pourrait être utilisé avec une justification égale. »— Albert Einstein et Leopold Infeld, L'Évolution de la physique (1938), p. 212
« Bien qu'il ne soit pas rare que les gens disent que Copernic a prouvé que Ptolémée avait tort, ce n'est pas vrai. On peut utiliser l'un ou l'autre modèle comme description de l'univers. »— Stephen Hawking et Leonard Mlodinow, The Grand Design (2010), p. 39
« Cela nous donne la liberté de revenir au point de vue de Ptolémée d'une "Terre immobile". Du point de vue supérieur d'Einstein, Ptolémée et Copernic ont également raison. »— Max Born, Einstein's Theory of Relativity (1965), pp. 276-277
« Je peux vous construire un univers à symétrie sphérique avec la Terre en son centre, et vous ne pouvez pas le réfuter sur la base des observations. Vous ne pouvez l'exclure que sur des critères philosophiques. »— George F.R. Ellis, Scientific American (octobre 1995), p. 55
« Les mouvements de l'univers sont les mêmes que l'on adopte le mode de vue ptoléméen ou copernicien. Les deux sont en effet également corrects. »— Ernst Mach, La Mécanique (1883)
« Ces deux propositions, "la Terre tourne" et "il est plus commode de supposer que la Terre tourne", ont une seule et même signification. »— Henri Poincaré, La Science et l'Hypothèse (1902)
Ces citations ne viennent pas de marginaux. Einstein, Hawking, Born, Ellis, Mach et Poincaré sont les architectes de la physique moderne. Quand ils disent que le géocentrisme et l'héliocentrisme sont « également corrects », ils ne font pas du relativisme philosophique — ils constatent un fait mathématique. Les deux cadres produisent les mêmes prédictions observationnelles. Le choix entre eux est un choix de convention, pas de vérité (pour l'analyse complète, voir [N6](/lhypothese-nulle-la-dynamique-najoute-rien-a-la-cinematique/)).


### L'état de l'académie moderne

Quand ces faits sont portés à l'attention d'universitaires, la réponse typique n'est pas une réfutation — c'est une **intimidation**. Le vault SpaceAudits documente des échanges avec des académiciens qui confondent systématiquement cinématique et dynamique, utilisent des équations cinématiques tout en les labellant « dynamiques », et recourent à l'argument d'autorité (« j'ai enseigné la dynamique pendant 3 ans ») quand la logique leur échappe.


Les manuels de physique eux-mêmes confirment la distinction : la cinématique décrit le mouvement (positions, vitesses, accélérations), la dynamique ajoute la masse et la force (Watson, *A Text-book of Physics*, 1911 ; Shankar, *Fundamentals of Physics I*, Yale, 2019 ; Giancoli, *Physics for Scientists and Engineers*, 2008). Or les équations de la mécanique céleste — celles qui gouvernent le mouvement des planètes — sont cinématiques : elles reposent sur le ratio a³/T² de Kepler, dans lequel la masse se simplifie algébriquement (voir [N6, §04](/lhypothese-nulle-la-dynamique-najoute-rien-a-la-cinematique/)).


## 07 Notre démarche sur ce site

Ce site n'est pas un manifeste ni un pamphlet. C'est un espace d'examen. Voici les principes qui guident chaque article publié ici.


**Principe 1 — Distinguer le fait de l'interprétation.** La chute d'un objet est un fait. L'appeler « gravité » est une interprétation. La trajectoire du soleil dans le ciel est un fait. L'appeler « rotation de la Terre » est une interprétation. Nous séparons toujours les deux.
**Principe 2 — Privilégier l'expérience sur l'observation.** Un test reproductible sur un lac (laser, zoom, visibilité) a plus de poids épistémique qu'une image satellite interprétée par une agence. L'expérience que tout le monde peut refaire vaut plus que l'observation que personne ne peut vérifier.
**Principe 3 — Ne jamais plier la Révélation pour la faire entrer dans un modèle humain.** Le concordisme — cette tentative de faire coïncider le Coran avec les théories scientifiques du moment — est une erreur méthodologique et théologique. Si la théorie change demain, le Coran se retrouve en porte-à-faux. Nous laissons les textes dire ce qu'ils disent, dans la langue dans laquelle ils ont été révélés.
**Principe 4 — Appeler les choses par leur nom.** Une hypothèse est une hypothèse, aussi élégante soit-elle. Un consensus est un consensus, pas une preuve. Une inférence est une inférence, pas une mesure. La rigueur commence par le vocabulaire.
Ces principes ne sont pas anti-scientifiques. Ils *sont* scientifiques — au sens le plus classique du terme. C'est précisément ce que Bacon, Bernard, Popper, Hacking et Woodward ont défendu pendant cinq siècles. Ce que nous faisons ici, c'est appliquer leurs propres critères aux théories que le monde tient pour acquises.


 أَفَلَا يَنظُرُونَ إِلَى ٱلْإِبِلِ كَيْفَ خُلِقَتْ ۝ وَإِلَى ٱلسَّمَآءِ كَيْفَ رُفِعَتْ ۝ وَإِلَى ٱلْجِبَالِ كَيْفَ نُصِبَتْ ۝ وَإِلَى ٱلْأَرْضِ كَيْفَ سُطِحَتْ
 


 « Ne considèrent-ils pas les chameaux, comment ils ont été créés ; et le ciel, comment il a été élevé ; et les montagnes, comment elles ont été dressées ; et la terre, comment elle a été étendue ? »
 Sourate Al-Ghashiyah — 88:17-20
Le Coran lui-même invite à l'observation directe. « Ne considèrent-ils pas... » Ce n'est pas un appel à croire aveuglément un modèle hérité. C'est un appel à regarder, à examiner, à réfléchir. C'est exactement ce que nous proposons de faire — en commençant par ne rien tenir pour acquis.


## Références


 - Bernard, Claude. *Introduction à l'étude de la médecine expérimentale* (1865). Paris : Flammarion, rééd. 2008.

 - Bacon, Francis. *Novum Organum* (1620). Trad. fr. : Malherbe & Pousseur, PUF, 1986.

 - Popper, Karl. *La Logique de la découverte scientifique* (1934). Trad. fr. : Payot, 1973.

 - Woodward, James. *Making Things Happen: A Theory of Causal Explanation*. Oxford University Press, 2003.

 - Hacking, Ian. *Representing and Intervening* (1983). Trad. fr. : *Concevoir et expérimenter*, Christian Bourgois, 1989.

 - Laudan, Larry. « A Confutation of Convergent Realism ». *Philosophy of Science*, 48(1), 1981.

 - Freedman, W. L. et al. « The Carnegie Chicago Hubble Program ». *Astrophysical Journal*, 882(1), 2019.

 - Riess, A. G. et al. « A Comprehensive Measurement of the Local Value of the Hubble Constant ». *ApJ Letters*, 934(1), 2022.

 - Di Valentino, E. et al. « In the Realm of the Hubble Tension — A Review of Solutions ». *Classical and Quantum Gravity*, 38(15), 2021.

 - Singh, R. « Evidence for possible systematic underestimation of uncertainties in extragalactic distances ». arXiv:2111.07872, 2021.

 - Hubble, Edwin. *The Observational Approach to Cosmology*. Oxford : Clarendon Press, 1937.

 - ESA Gaia Collaboration. « Gaia Data Release 2 ». *Astronomy & Astrophysics*, 616, A1, 2018.

 - van Fraassen, Bas C. *The Scientific Image*. Oxford University Press, 1980.

 - Kuhn, Thomas S. *La Structure des révolutions scientifiques* (1962). Trad. fr. : Flammarion, 1983.


					

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