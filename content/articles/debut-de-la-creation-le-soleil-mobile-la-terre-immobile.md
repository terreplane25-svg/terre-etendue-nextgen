---
title: "Début de la Création : le Soleil mobile, la Terre immobile"
description: ".nx-nav{width:100%;background:#F7F2E8;border-bottom:1px solid #DDD5C5;padding:0 2rem;position:sticky;top:0;z-index:999} .nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;ju..."
date: "2026-05-04"
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
:root{--bg:#F7F2E8;--bg2:#EDE5D5;--brun:#6B4226;--brun-l:#8B5C36;--brun-g:rgba(139,92,54,.12);--t1:#2C1810;--t2:#5C4A3A;--t3:#8A7A6A;--bdr:#DDD5C5;--f1:'Cormorant Garamond',Georgia,serif;--f2:'Outfit',sans-serif;--f3:'Cormorant Garamond',Georgia,serif;--f4:'Amiri',serif}
.b3{background:var(--bg);color:var(--t1);padding:0}
.b3-h{padding:5rem 2rem 3.5rem;text-align:center;position:relative;overflow:hidden}
.b3-h::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 50% at 50% 30%,rgba(139,92,54,.05),transparent 70%);pointer-events:none}
.b3-tag{display:inline-block;font-family:var(--f2);font-size:.62rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--brun-l);background:var(--brun-g);border:1px solid rgba(139,92,54,.25);padding:.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.b3-title{font-family:var(--f1);font-size:clamp(1.7rem,4.5vw,2.5rem);font-weight:700;color:var(--brun-l);line-height:1.15;margin:0 0 1rem;max-width:800px;margin-left:auto;margin-right:auto}
.b3-sub{font-family:var(--f3);font-size:1.02rem;line-height:1.7;color:var(--t2);max-width:650px;margin:0 auto 2rem}
.b3-meta{max-width:800px;margin:0 auto;padding:1.2em 0;border-top:1px solid var(--bdr);border-bottom:1px solid var(--bdr);display:flex;flex-wrap:wrap;gap:.5em 2em;font-family:var(--f2);font-size:.75rem;color:var(--t3)}
.b3-meta dt{font-weight:600;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem}
.b3-meta dd{margin:0 0 .6em;color:var(--t2)}
.b3-lay{display:flex;gap:2.5rem;max-width:1200px;margin:0 auto;padding:2.5rem 2rem 5rem;align-items:flex-start}
.b3-nav{flex:0 0 255px;position:sticky;top:80px;max-height:calc(100vh - 100px);overflow-y:auto;padding:1.5rem;background:var(--bg2);border:1px solid var(--bdr);border-radius:10px}
.b3-nav::-webkit-scrollbar{width:3px}.b3-nav::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}
.b3-nav__t{font-family:var(--f2);font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--brun-l);margin:0 0 1rem;padding-bottom:.6rem;border-bottom:1px solid var(--bdr)}
.b3-nav ul{list-style:none;padding:0;margin:0}.b3-nav li{margin-bottom:.35rem}
.b3-nav a{display:block;font-family:var(--f2);font-size:.76rem;color:var(--t3);text-decoration:none;padding:.4em .8em;border-radius:5px;border-left:2px solid transparent;transition:all .25s ease;line-height:1.35}
.b3-nav a:hover{color:var(--t1);background:rgba(139,92,54,.06);border-left-color:var(--brun-l)}
.b3-nav .num{font-size:.6rem;font-weight:600;color:var(--brun-l);margin-right:.4em;opacity:.7}
.b3-nav__bk{display:block;margin-top:1.2rem;padding:.6em 1em;background:var(--brun-l);color:#2C1810;font-family:var(--f2);font-size:.72rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;text-align:center;border-radius:5px;transition:background .3s ease}
.b3-nav__bk:hover{background:#A97544}
.b3-b{flex:1;min-width:0;max-width:800px;font-family:var(--f3);font-size:clamp(1rem,1.8vw,1.08rem);line-height:1.75;color:var(--t1)}
.b3-b p{margin-bottom:1.4em;text-align:justify;hyphens:auto}
.b3-b a{color:var(--brun-l);text-decoration:underline;text-underline-offset:3px}
.b3-b h2{font-family:var(--f1);font-size:clamp(1.4rem,3vw,1.85rem);font-weight:700;color:var(--t1);margin:3em 0 .8em;padding-bottom:.4em;border-bottom:1px solid var(--bdr);line-height:1.25;scroll-margin-top:90px}
.b3-b h3{font-family:var(--f2);font-size:clamp(1rem,1.8vw,1.15rem);font-weight:600;color:var(--brun-l);text-transform:uppercase;letter-spacing:.06em;margin:2em 0 .6em;line-height:1.35}
.sn{font-family:var(--f2);font-size:.65rem;font-weight:600;color:var(--brun-l);background:var(--brun-g);border:1px solid rgba(139,92,54,.25);padding:.2em .6em;border-radius:3px;margin-right:.6em;vertical-align:middle}
.hadith{margin:2em 0;padding:1.8em 2em;background:var(--bg2);border:1px solid rgba(139,92,54,.2);border-radius:10px}
.hadith__fr{font-family:var(--f3);font-size:.95rem;color:var(--t2);line-height:1.7;margin:0 0 .5em}
.hadith__ref{font-family:var(--f2);font-size:.7rem;font-weight:600;color:var(--brun-l);letter-spacing:.05em;margin:0}
.hadith__grade{display:inline-block;font-family:var(--f2);font-size:.6rem;font-weight:600;color:#1B5E3C;background:rgba(45,106,79,.1);border:1px solid rgba(45,106,79,.2);padding:.15em .5em;border-radius:3px;margin-left:.5em}
.ayah{margin:2em 0;padding:1.8em 2em;background:linear-gradient(135deg,rgba(139,92,54,.08),rgba(139,92,54,.02) 70%);border:1px solid rgba(139,92,54,.2);border-radius:10px}
.ayah__ar{font-family:var(--f4);font-size:1.5rem;line-height:2;color:var(--t1);direction:rtl;text-align:right;margin:0 0 1em;padding:.5em 0}
.ayah__fr{font-family:var(--f3);font-size:.95rem;font-style:italic;color:var(--t2);line-height:1.7;margin:0 0 .5em}
.ayah__ref{font-family:var(--f2);font-size:.7rem;font-weight:600;color:var(--brun-l);letter-spacing:.05em;margin:0}
.kp{margin:1.5em 0;padding:1.2em 1.6em;background:var(--bg2);border-left:3px solid var(--brun);border-radius:0 8px 8px 0;font-family:var(--f2);font-size:.9rem;line-height:1.6;color:var(--t2)}
.kp strong{color:var(--t1)}
.b3-refs{margin-top:3em;padding-top:2em;border-top:1px solid var(--bdr)}
.b3-refs h2{border-bottom:none;padding-bottom:0;font-size:1.3rem}
.b3-refs ol{padding-left:1.5em;font-family:var(--f2);font-size:.82rem;color:var(--t2);line-height:1.7}
.b3-refs li{margin-bottom:.6em}
@media(max-width:900px){.b3-lay{flex-direction:column;padding:1.5rem}.b3-nav{position:static;flex:none;width:100%;max-height:none;margin-bottom:2rem}.b3-h{padding:3.5rem 1.5rem 2.5rem}.ayah__ar{font-size:1.2rem}}


 La Bibliothèque — BIB-2026-003
 
# Début de la Création : le Soleil mobile, la Terre immobile

 Les hadiths authentiques décrivent un Soleil qui court, se prosterne, demande la permission de revenir — et une Terre stable, posée sur l'eau, fixée par des montagnes.
 
 AuteurTerre Étendue Islam
 DateAvril 2026 — v2.0
 Lecture~30 min
 SourcesSahih al-Bukhari · Sahih Muslim · Sunan · Tafsir classiques
 

 
 
## Sommaire

 
 [01 Ce que le Prophète a dit](#d-intro)

 - [02 Le Soleil qui court et se prosterne](#d-soleil)

 - [03 La Terre sur l'eau](#d-terre)

 - [04 La Terre stable et immobile](#d-immobile)

 - [05 Le ciel : un toit protégé](#d-ciel)

 - [06 Les signes de l'Heure](#d-signes)

 - [07 Conclusion](#d-ccl)

 - [Références](#d-refs)

 

 [← Retour à la Bibliothèque](/la-bibliotheque/)
 

## 01 Ce que le Prophète ﷺ a enseigné

Le Coran établit les principes (voir [B1](/la-terre-dans-le-coran/)). La Sunna les illustre avec des détails concrets. Le Prophète ﷺ a décrit un cosmos dans lequel le Soleil est un objet en mouvement — il court, il se prosterne, il demande la permission de revenir — et dans lequel la Terre est posée sur l'eau, stabilisée par des montagnes, immobile.


## 02 Le Soleil qui court et se prosterne

Le Prophète ﷺ dit à Abū Dharr au moment où le soleil se couchait : « Sais-tu où il se couche ? » — Allāh et Son Messager sont plus savants. — « **Il vogue jusqu'à se prosterner sous le Trône.** Il demande alors la permission de revenir et on la lui accorde. Peu s'en faut qu'il se prosterne et qu'on ne l'accepte pas, et qu'il demande et que la permission ne lui soit pas accordée, mais qu'on lui dise : "Retourne d'où tu es venu !" Et **le soleil se lèvera alors de son couchant.** »


Al-Bukhārī 3199 Ṣaḥīḥ


**Ce que ce hadith établit :** Le Soleil *vogue* (yadhhabu), *se prosterne* (yasjudu), *demande la permission* (yasta'dhinu) de revenir. Ce sont des verbes d'action attribués au Soleil — pas à la Terre. Le lever du Soleil depuis son couchant est un signe de l'Heure, ce qui implique que son trajet est-ouest est son mouvement normal.
D'après Salama ibn al-Aqwa', le Prophète ﷺ priait le maghrib dès que le soleil se couchait et **disparaissait de l'horizon**.


Muslim 636 Ṣaḥīḥ


'Abdallāh ibn 'Umar rapporte que le Messager ﷺ a dit : « Ne cherchez pas à prier lors du lever du soleil ni à son coucher ! En effet, **il se dresse entre les deux cornes du Diable.** »


Al-Bukhārī 581, Muslim 831 Ṣaḥīḥ


D'après Abū Hurayra, le Messager ﷺ a dit : « Certes, **le soleil n'a été retenu pour aucun être humain, excepté Josué**, lorsqu'il chemina de nuit vers Jérusalem. » Il dit au soleil : « Tu as un ordre à accomplir et j'ai un ordre à accomplir. Ô Allāh ! Retiens-le ! » Alors **le soleil arrêta sa course** en sa faveur.


As-Saḥīḥa 202 Ṣaḥīḥ


**Josué et l'arrêt du Soleil :** Si c'était la Terre qui tournait, le miracle aurait consisté à arrêter la rotation de la Terre. Le texte dit explicitement que le Soleil a arrêté *sa course*.

## 03 La Terre posée sur l'eau

D'après 'Abdallāh ibn 'Amr ibn al-'Āṣ, le Prophète ﷺ a dit : « **Allāh a écrit les destinées des créatures cinquante mille ans avant de créer les cieux et la terre, et Son Trône était sur l'eau.** »


Muslim 2653 Ṣaḥīḥ


وَهُوَ الَّذِي خَلَقَ السَّمَاوَاتِ وَالْأَرْضَ فِي سِتَّةِ أَيَّامٍ وَكَانَ عَرْشُهُ عَلَى الْمَاءِ


« Et c'est Lui qui a créé les cieux et la terre en six jours — et Son Trône était sur l'eau. »


Hūd — S11 V7


Les tafsīr d'Ibn Kathīr et d'al-Ṭabarī confirment que la Terre a été étendue sur l'eau. Al-Baghawī : « Nous l'avons nivelée au-dessus de l'eau. » Ce point renforce [O1 — L'eau ne ment pas](/leau-ne-ment-pas/) : si la Terre est posée sur l'eau, l'eau devrait être plate — et c'est ce que les expériences montrent.


## 04 La Terre stable et immobile

أَمَّن جَعَلَ الْأَرْضَ قَرَارًا وَجَعَلَ خِلَالَهَا أَنْهَارًا وَجَعَلَ لَهَا رَوَاسِيَ


« N'est-ce pas Lui qui a établi la Terre comme demeure stable (qarāran) ? »


An-Naml — S27 V61


وَأَلْقَىٰ فِي الْأَرْضِ رَوَاسِيَ أَن تَمِيدَ بِكُمْ


« Et Il a enfoncé des montagnes dans la terre pour qu'elle ne s'ébranle pas (tamīd) avec vous. »


Luqmān — S31 V10


**Le raisonnement :** Pourquoi Allāh placerait-Il des montagnes comme des ancres (rawāsī) pour empêcher la Terre de vaciller, si elle était déjà en rotation à 1 670 km/h et en orbite à 107 000 km/h ? Les montagnes stabilisent contre les secousses — sur un sol immobile.

## 05 Le ciel : un toit protégé au-dessus de la Terre

وَجَعَلْنَا السَّمَاءَ سَقْفًا مَّحْفُوظًا


« Et Nous avons fait du ciel un toit protégé. »


Al-Anbiyāʾ — S21 V32


Le ciel est un **saqf** (toit) — pas un vide infini. Un toit implique une construction : des fondations (la Terre), des piliers (invisibles — S13 V2), et un toit (le ciel). Cette cosmologie est un **bâtiment clos**, cohérent avec l'impossibilité de franchir les limites (S55 V33, voir [B1, §08](/la-terre-dans-le-coran/)) et les contraintes physiques de [O7](/lespace-une-frontiere-infranchissable/).


## 06 Les signes de l'Heure : le Soleil se lèvera de son couchant

D'après Ḥudhayfa ibn Asīd, le Prophète ﷺ dit : « L'Heure ne viendra pas avant l'apparition de dix signes : un engloutissement en Orient, un en Occident et un dans la péninsule arabe, la fumée, le Faux Messie, la bête de la terre, Gog et Magog, **le lever du soleil par son couchant** et un feu émanant du fond d'Aden. »


Muslim 2901 Ṣaḥīḥ


**Ce que le lever du Soleil par l'Occident implique :** Le hadith d'Abū Dharr (Bukhārī 3199) dit que c'est au *Soleil* qu'on refuse la permission de revenir. C'est le Soleil qui change de parcours, pas la Terre qui inverse sa rotation. Les deux hadiths sont parfaitement cohérents — mais uniquement dans un modèle où le Soleil se déplace réellement.

## 07 Conclusion

La Sunna authentique décrit un cosmos dans lequel le **Soleil** court (tajrī), vogue (yadhhabu), se prosterne (yasjudu), peut être retenu (Josué), et changera de direction (signe de l'Heure). La **Terre** est posée sur l'eau, étendue, stabilisée par des montagnes, immobile. Le **ciel** est un toit protégé construit au-dessus.


Pour les versets coraniques, voir [B1](/la-terre-dans-le-coran/). Pour les 95 savants, voir [B2](/pres-de-cent-savants-de-lislam/). Pour le pseudo-consensus, voir [B5](/le-consensus-sur-la-sphericite/).


 📄
 Document complet : Les preuves religieuses et scientifiques (PDF)


 25 versets sur l'immobilité, 22 preuves coraniques du Soleil mobile, hadiths sahih, citations de savants — le dossier intégral.


 [Consulter le PDF ↗](https://terre-etendue-islam.fr/wp-content/uploads/2026/04/document-maitre-preuves-religieuses.pdf)

## Références


 - Ṣaḥīḥ al-Bukhārī. Hadiths 581, 725, 3199.

 - Ṣaḥīḥ Muslim. Hadiths 636, 831, 2653, 2901.

 - Silsilat al-Aḥādīth al-Ṣaḥīḥa (al-Albānī). Hadith 202.

 - Al-Tuwayjirī, Al-Ṣawāʿiq al-Shadīda.


					

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