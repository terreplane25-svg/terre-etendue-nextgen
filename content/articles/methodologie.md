---
title: "Méthodologie"
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

 

 
 - @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Outfit:wght@300;400;500;600&family=Amiri:ital,wght@0,400;0,700;1,400&display=swap');
.sp{background:#F7F2E8;color:#2C1810;min-height:80vh;padding:6rem 2rem 5rem}
.sp__inner{max-width:800px;margin:0 auto}
.sp__tag{display:inline-block;font-family:'Outfit',sans-serif;font-size:.62rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:#B8860B;background:rgba(212,175,55,.08);border:1px solid rgba(212,175,55,.2);padding:.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.sp__title{font-family:'Cormorant Garamond',Georgia,serif;font-size:clamp(1.8rem,4.5vw,2.6rem);font-weight:700;color:#B8860B;line-height:1.15;margin:0 0 1.5rem}
.sp__body{font-family:'Cormorant Garamond',Georgia,serif;font-size:1.05rem;line-height:1.8;color:#5C4A3A}
.sp__body p{margin-bottom:1.4em}
.sp__body h2{font-family:'Cormorant Garamond',Georgia,serif;font-size:1.3rem;font-weight:700;color:#2C1810;margin:2.5em 0 .8em;padding-bottom:.4em;border-bottom:1px solid #DDD5C5}
.sp__body h3{font-family:'Outfit',sans-serif;font-size:.95rem;font-weight:600;color:#B8860B;margin:1.8em 0 .5em}
.sp__body a{color:#B8860B;text-decoration:underline;text-underline-offset:3px}
.sp__body ul{padding-left:1.5em;margin-bottom:1.4em}
.sp__body li{margin-bottom:.6em}
.sp__body strong{color:#2C1810}
.sp__social{display:flex;gap:1rem;flex-wrap:wrap;margin:2em 0}
.sp__social a{display:inline-flex;align-items:center;gap:.5em;padding:.6em 1.2em;background:#EDE5D5;border:1px solid #DDD5C5;border-radius:6px;font-family:'Outfit',sans-serif;font-size:.8rem;font-weight:500;color:#5C4A3A;text-decoration:none;transition:all .3s ease}
.sp__social a:hover{border-color:rgba(212,175,55,.3);color:#2C1810;transform:translateY(-2px)}


 Ressources
 
# Méthodologie

Comment nous travaillons. Quelles sources nous utilisons. Quels critères nous appliquons. Cette page est la charte intellectuelle du site.

## Principe 1 — Distinguer le fait de l'interprétation

La chute d'un objet est un fait. L'appeler « gravité » est une interprétation. La trajectoire du soleil dans le ciel est un fait. L'appeler « rotation de la Terre » est une interprétation. Nous documentons les faits et identifions les interprétations comme telles.

## Principe 2 — Privilégier l'expérience sur l'observation

Francis Bacon, Claude Bernard, Karl Popper, Ian Hacking et James Woodward convergent : **l'expérimentation contrôlée est épistémiquement supérieure à la simple observation**. Un test reproductible sur un lac a plus de poids qu'une image satellite interprétée. L'expérience que tout le monde peut refaire vaut plus que l'observation que personne ne peut vérifier. Voir [N1](/pourquoi-tout-remettre-en-question/).

## Principe 3 — Ne jamais plier la Révélation

Le concordisme — faire coïncider le Coran avec les théories du moment — est une erreur méthodologique et théologique. Le Coran est *muhaymin* (dominant). Ses termes ont des sens précis, documentés par les Salaf et les dictionnaires classiques. Nous les laissons dire ce qu'ils disent. Voir [N5](/le-concordisme/) et [B1](/la-terre-dans-le-coran/).

## Principe 4 — Appeler les choses par leur nom

Une hypothèse est une hypothèse. Un consensus est un consensus, pas une preuve. Une inférence est une inférence, pas une mesure. Nous n'utilisons pas de vocabulaire trompeur.

## Sources utilisées

Nos articles s'appuient sur trois types de sources, toujours citées :

 **Sources islamiques primaires :** Coran, hadith authentiques (Bukhārī, Muslim), tafsīr classiques (al-Ṭabarī, al-Qurṭubī, al-Jalālayn, al-Rāzī...), dictionnaires arabes classiques (Ibn Manẓūr, al-Fayrūzābādī, al-Zabīdī...).

 - **Sources scientifiques à comité de lecture :** revues de physique, géodésie, optique, géophysique. Nous citons les auteurs et les références complètes.

 - **Données d'ingénierie :** canaux (Suez), pipelines (Alaska), infrastructures ferroviaires — construits sur des modèles plans sans correction de courbure.


## Ce que nous ne faisons pas


 - Nous ne citons pas de source sans la vérifier.

 - Nous ne cachons pas les arguments adverses — nous les présentons et les examinons.

 - Nous ne prétendons pas avoir toutes les réponses — nous identifions explicitement ce qui reste ouvert (voir [L2](/etat-des-lieux-ou-en-sommes-nous/)).


					

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