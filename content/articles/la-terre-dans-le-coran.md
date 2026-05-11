---
title: "La Terre dans le Coran"
description: ".nx-nav{width:100%;background:#F7F2E8;border-bottom:1px solid #DDD5C5;padding:0 2rem;position:sticky;top:0;z-index:999} .nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;ju..."
date: "2026-04-16"
author: "Terre Etendue"
category: "library"
tags: ["la-bibliothèque", "le-nexus"]
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
.b1{background:var(--bg);color:var(--t1);padding:0}
.b1-h{padding:5rem 2rem 3.5rem;text-align:center;position:relative;overflow:hidden}
.b1-h::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 50% at 50% 30%,rgba(139,92,54,.05),transparent 70%);pointer-events:none}
.b1-tag{display:inline-block;font-family:var(--f2);font-size:.62rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--brun-l);background:var(--brun-g);border:1px solid rgba(139,92,54,.25);padding:.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.b1-title{font-family:var(--f1);font-size:clamp(1.7rem,4.5vw,2.5rem);font-weight:700;color:var(--brun-l);line-height:1.15;margin:0 0 1rem;max-width:800px;margin-left:auto;margin-right:auto}
.b1-sub{font-family:var(--f3);font-size:1.02rem;line-height:1.7;color:var(--t2);max-width:650px;margin:0 auto 2rem}
.b1-meta{max-width:800px;margin:0 auto;padding:1.2em 0;border-top:1px solid var(--bdr);border-bottom:1px solid var(--bdr);display:flex;flex-wrap:wrap;gap:.5em 2em;font-family:var(--f2);font-size:.75rem;color:var(--t3)}
.b1-meta dt{font-weight:600;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem}
.b1-meta dd{margin:0 0 .6em;color:var(--t2)}
.b1-lay{display:flex;gap:2.5rem;max-width:1200px;margin:0 auto;padding:2.5rem 2rem 5rem;align-items:flex-start}
.b1-nav{flex:0 0 255px;position:sticky;top:80px;max-height:calc(100vh - 100px);overflow-y:auto;padding:1.5rem;background:var(--bg2);border:1px solid var(--bdr);border-radius:10px}
.b1-nav::-webkit-scrollbar{width:3px}.b1-nav::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}
.b1-nav__t{font-family:var(--f2);font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--brun-l);margin:0 0 1rem;padding-bottom:.6rem;border-bottom:1px solid var(--bdr)}
.b1-nav ul{list-style:none;padding:0;margin:0}.b1-nav li{margin-bottom:.35rem}
.b1-nav a{display:block;font-family:var(--f2);font-size:.76rem;color:var(--t3);text-decoration:none;padding:.4em .8em;border-radius:5px;border-left:2px solid transparent;transition:all .25s ease;line-height:1.35}
.b1-nav a:hover{color:var(--t1);background:rgba(139,92,54,.06);border-left-color:var(--brun-l)}
.b1-nav a.active{color:var(--brun-l);background:var(--brun-g);border-left-color:var(--brun-l);font-weight:500}
.b1-nav .num{font-size:.6rem;font-weight:600;color:var(--brun-l);margin-right:.4em;opacity:.7}
.b1-nav__bk{display:block;margin-top:1.2rem;padding:.6em 1em;background:var(--brun-l);color:#2C1810;font-family:var(--f2);font-size:.72rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;text-align:center;border-radius:5px;transition:background .3s ease}
.b1-nav__bk:hover{background:#A97544}
.b1-b{flex:1;min-width:0;max-width:800px;font-family:var(--f3);font-size:clamp(1rem,1.8vw,1.08rem);line-height:1.75;color:var(--t1)}
.b1-b p{margin-bottom:1.4em;text-align:justify;hyphens:auto}
.b1-b a{color:var(--brun-l);text-decoration:underline;text-underline-offset:3px}
.b1-b h2{font-family:var(--f1);font-size:clamp(1.4rem,3vw,1.85rem);font-weight:700;color:var(--t1);margin:3em 0 .8em;padding-bottom:.4em;border-bottom:1px solid var(--bdr);line-height:1.25;scroll-margin-top:90px}
.b1-b h3{font-family:var(--f2);font-size:clamp(1rem,1.8vw,1.15rem);font-weight:600;color:var(--brun-l);text-transform:uppercase;letter-spacing:.06em;margin:2em 0 .6em;line-height:1.35;scroll-margin-top:90px}
.sn{font-family:var(--f2);font-size:.65rem;font-weight:600;color:var(--brun-l);background:var(--brun-g);border:1px solid rgba(139,92,54,.25);padding:.2em .6em;border-radius:3px;margin-right:.6em;vertical-align:middle}
.ayah{margin:2em 0;padding:1.8em 2em;background:linear-gradient(135deg,rgba(139,92,54,.08),rgba(139,92,54,.02) 70%);border:1px solid rgba(139,92,54,.2);border-radius:10px}
.ayah__ar{font-family:var(--f4);font-size:1.5rem;line-height:2;color:var(--t1);direction:rtl;text-align:right;margin:0 0 1em;padding:.5em 0}
.ayah__fr{font-family:var(--f3);font-size:.95rem;font-style:italic;color:var(--t2);line-height:1.7;margin:0 0 .5em}
.ayah__ref{font-family:var(--f2);font-size:.7rem;font-weight:600;color:var(--brun-l);letter-spacing:.05em;margin:0}
.tafsir{margin:.8em 0;padding:.8em 1.2em;background:var(--bg2);border-left:2px solid rgba(139,92,54,.3);border-radius:0 6px 6px 0;font-family:var(--f3);font-size:.88rem;color:var(--t2);line-height:1.6}
.tafsir cite{display:block;margin-top:.4em;font-size:.75rem;font-style:normal;font-family:var(--f2);color:var(--t3)}
.kp{margin:1.5em 0;padding:1.2em 1.6em;background:var(--bg2);border-left:3px solid var(--brun);border-radius:0 8px 8px 0;font-family:var(--f2);font-size:.9rem;line-height:1.6;color:var(--t2)}
.kp strong{color:var(--t1)}
.db{margin:2em 0;padding:1.4em 1.8em;background:var(--bg2);border:1px solid var(--bdr);border-radius:8px}
.db__l{display:inline-block;font-family:var(--f2);font-size:.65rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:var(--brun-l);background:var(--brun-g);padding:.2em .7em;border-radius:3px;margin-bottom:.8em}
.db p{font-size:.92rem;margin-bottom:.8em;text-align:left}
.b1-refs{margin-top:3em;padding-top:2em;border-top:1px solid var(--bdr)}
.b1-refs h2{border-bottom:none;padding-bottom:0;font-size:1.3rem}
.b1-refs ol{padding-left:1.5em;font-family:var(--f2);font-size:.82rem;color:var(--t2);line-height:1.7}
.b1-refs li{margin-bottom:.6em}
@media(max-width:900px){.b1-lay{flex-direction:column;padding:1.5rem}.b1-nav{position:static;flex:none;width:100%;max-height:none;margin-bottom:2rem}.b1-h{padding:3.5rem 1.5rem 2.5rem}.ayah__ar{font-size:1.2rem}}


 La Bibliothèque — BIB-2026-001
 
# La Terre dans le Coran : ce que les mots disent vraiment

 Sept termes coraniques pour la Terre. Dix-huit versets explicites. Zéro mention de sphéricité. Le Coran décrit une Terre étendue, aplanie, immobile — et un Soleil en mouvement perpétuel.
 
 AuteurTerre Étendue Islam
 DateAvril 2026 — v2.0
 Lecture~35 min
 SourcesCoran · Tafsīr (Ṭabarī, Ibn Kathīr, Qurṭubī, Jalālayn, Baghawī) · Lisān al-ʿArab
 

 
 
## Sommaire

 
 [01 450 occurrences, 0 sphère](#q-intro)

 - [02 Sept termes, un seul sens](#q-termes)

 - [03 Les versets de la planéité](#q-versets)

 - [04 Dahā : l'imposture de l'œuf](#q-daha)

 - [05 La Terre n'est pas un kawkab](#q-kawkab)

 - [06 La Terre immobile et stable](#q-immobile)

 - [07 Le Soleil mobile](#q-soleil)

 - [08 Impossible de franchir les limites](#q-espace)

 - [09 Conclusion](#q-ccl)

 - [Références](#q-refs)

 

 [← Retour à la Bibliothèque](/la-bibliotheque/)
 

## 01 450 occurrences du mot « terre » — aucune mention de sphéricité

Le mot **أرض** (*arḍ*) apparaît environ 450 fois dans le Coran. Dans aucune de ces occurrences, la Terre n'est décrite comme sphérique, ronde, ou en rotation. En revanche, de nombreux termes indiquent explicitement sa planéité : elle est *aplanie*, *étendue*, *déployée comme un tapis*, *nivelée*, *fixée*, *stabilisée*.


Aucun récit des Compagnons ou des Tābiʿīn ne soutient la sphéricité. Auraient-ils tous négligé de partager cette information ? Pourquoi Allāh insisterait-Il sur le fait que la Terre a été aplanie, si elle était en réalité sphérique ? Allāh nous a mentionné les abeilles, les fourmis, les moustiques, les chameaux, les mers, les arbres — mais pas une seule fois la sphéricité de la Terre.


## 02 Sept termes coraniques, un seul sens

Les sept termes
**سُطِحَت** (*suṭiḥat*) — nivelée, aplanie · s88 v20


**مَدَّ** (*madda*) — étendue en long et en large · s13 v3, s15 v19, s50 v7


**فَرَشَ** (*faracha*) — déployée comme un tapis · s51 v48, s2 v22


**دَحَاهَا** (*daḥāhā*) — aplanie, étalée · s79 v30


**طَحَاهَا** (*ṭaḥāhā*) — élargie dans toutes les directions · s91 v6


**بِسَاطًا** (*bisāṭan*) — tapis étendu · s71 v19


**مِهَادًا / مَهْدًا** (*mihādan / mahdan*) — lit, berceau, couche · s78 v6, s20 v53, s43 v10


Ces sept termes convergent tous vers la même signification : une surface **plane, étendue, stable, déployée**. Aucun ne supporte l'idée d'une sphère — ni dans les dictionnaires classiques (Lisān al-ʿArab, Tāj al-ʿArūs), ni dans les exégèses des premiers siècles.


## 03 Les versets de la planéité : texte arabe et exégèses


### 1. Sourate Al-Ghāshiyah (88:20) — suṭiḥat

وَإِلَى الْأَرْضِ كَيْفَ سُطِحَتْ


« Et comment la terre a été nivelée ? »


Al-Ghāshiyah — S88 V20


« C'est-à-dire aplanie… ce qui est apparent est que la terre est aplanie et c'est l'avis des savants de la législation. Elle n'est pas sphérique contrairement à ce qu'affirment les membres du comité [astronomique]. »— Tafsīr al-Jalālayn
« C'est-à-dire étendue et aplanie. »— Tafsīr al-Qurṭubī
« Et comment la terre a été aplanie. On dit d'une montagne qu'elle est aplanie lorsque son sommet est nivelé. »— Tafsīr al-Ṭabarī
« C'est-à-dire étendue et aplanie. »— Tafsīr Ibn Kathīr

### 2. Sourate Ar-Raʿd (13:3) — madda

وَهُوَ الَّذِي مَدَّ الْأَرْضَ وَجَعَلَ فِيهَا رَوَاسِيَ وَأَنْهَارًا


« Et c'est Lui qui a étendu la terre et y a placé montagnes et fleuves. »


Ar-Raʿd — S13 V3


« C'est-à-dire qu'Il l'a élargie en long et en large. »— Tafsīr Ibn Kathīr
« Pour Abū Jaʿfar, Allāh a aplani la terre en long et en large. »— Tafsīr al-Ṭabarī
« Il a étendu c'est-à-dire aplani. »— Tafsīr al-Jalālayn

### 3. Sourate Al-Ḥijr (15:19) — madda

وَالْأَرْضَ مَدَدْنَاهَا وَأَلْقَيْنَا فِيهَا رَوَاسِيَ وَأَنبَتْنَا فِيهَا مِن كُلِّ شَيْءٍ مَّوْزُونٍ


« Et quant à la terre, Nous l'avons étendue, y avons placé des montagnes fermement ancrées. »


Al-Ḥijr — S15 V19


« Étalée, nivelée… Il mentionne que La Mecque est le centre de la terre, à partir duquel elle a été étalée. »— Tafsīr al-Ṭabarī
« Nous l'avons étendue c'est-à-dire aplanie. »— Tafsīr al-Jalālayn
« Nous l'avons nivelée au-dessus de l'eau. Il fut dit qu'elle a été élargie d'une distance de 500 ans de marche à partir de la Kaʿbah. »— Tafsīr al-Baghawī

### 4. Sourate Adh-Dhāriyāt (51:48) — faracha

وَالْأَرْضَ فَرَشْنَاهَا فَنِعْمَ الْمَاهِدُونَ


« Et la terre, Nous l'avons étendue. Et de quelle excellente façon Nous l'avons nivelée ! »


Adh-Dhāriyāt — S51 V48


« C'est-à-dire Nous l'avons déployée comme un tapis sur l'eau. »— Tafsīr al-Qurṭubī
« Nous avons fait de la terre un tapis pour les créatures. »— Tafsīr al-Ṭabarī

### 5. Sourate Al-Baqarah (2:22) — firāshan

الَّذِي جَعَلَ لَكُمُ الْأَرْضَ فِرَاشًا وَالسَّمَاءَ بِنَاءً


« C'est Lui qui vous a fait la Terre pour lit, et le ciel pour toit. »


Al-Baqarah — S2 V22


« Farashash-shayʾ c'est-à-dire qu'il l'a étendu (basaṭahu). Al-Layth dit que al-farsh est le fait de déployer et étendre sa couche, son lit. On dit iftarasha ses bras lorsqu'ils sont mis à plat sur le sol. »— Lisān al-ʿArab, vol. 6 p. 326 ([shamela.ws](https://shamela.ws/book/1687/3338))

### 6. Sourate Nūḥ (71:19) — bisāṭan

وَاللَّهُ جَعَلَ لَكُمُ الْأَرْضَ بِسَاطًا


« Et c'est Allāh qui a étendu la terre pour vous, comme un tapis. »


Nūḥ — S71 V19


« Il l'a étendue, nivelée, stabilisée et renforcée à travers les montagnes fermement ancrées. »— Tafsīr Ibn Kathīr
« Il l'a étendue d'une distance de cinq cents ans à partir du dessous de la Kaʿbah. »— Tafsīr Muqātil, vol. 4 p. 451 ([shamela.ws](https://shamela.ws/book/23614/1852#p1))

### 7. Sourate An-Nabaʾ (78:6) — mihādan

أَلَمْ نَجْعَلِ الْأَرْضَ مِهَادًا


« N'avons-Nous pas fait de la Terre une couche ? »


An-Nabaʾ — S78 V6


« C'est-à-dire un lit, un tapis d'une distance de cinq cents ans. »— Tafsīr Muqātil, vol. 4 p. 558 ([shamela.ws](https://shamela.ws/book/23614/1929#p1))

### 8. Sourate Ash-Shams (91:6) — ṭaḥāhā

وَالْأَرْضِ وَمَا طَحَاهَا


« Et par la terre et son étendue. »


Ash-Shams — S91 V6


« Il l'a élargie de gauche à droite et dans toutes les directions. Pour Mujāhid, ṭaḥāhā signifie le déploiement (daḥāhā) et pour Ibn Zayd il s'agit de l'aplanissement (bassaṭahā). »— Tafsīr al-Ṭabarī
« Ce dernier avis — l'aplanissement — est le plus répandu et celui que privilégie la plupart des exégètes et des linguistes. »— Tafsīr Ibn Kathīr

## 04 Dahā (دحاها) : l'imposture de l'œuf d'autruche

وَالْأَرْضَ بَعْدَ ذَٰلِكَ دَحَاهَا


« Et quant à la terre, après cela, Il l'a étendue. »


An-Nāziʿāt — S79 V30


Ce verset est le plus instrumentalisé par les concordistes. Ils affirment que **دحاها** (*daḥāhā*) dérive de **دُحْيَة** (*duḥya*), « l'œuf d'autruche », et que le Coran décrirait la Terre comme « en forme d'œuf ». Cette affirmation est **fausse sur trois plans** :


Triple réfutation
**Linguistique :** Lisān al-ʿArab (vol. 14 p. 251) : ad-daḥw = « l'aplanissement (al-basṭ) et l'extension (al-madd) ». Le nid d'autruche est appelé udḥiyya car il est **aplani au sol**.


**Exégétique :** Aucun exégète classique (Ṭabarī, Ibn Kathīr, Qurṭubī, Jalālayn, Baghawī, Samʿānī) n'a jamais interprété daḥā comme « en forme d'œuf ». Tous : « aplanir, étendre, niveler ». L'interprétation « œuf » apparaît au XXᵉ siècle seulement.


**Zoologique :** L'autruche ne construit pas de nid. Elle gratte et aplanit le sol avec ses pattes pour créer une dépression plate où elle dépose ses œufs. C'est cet aplanissement qui s'appelle daḥw.


« C'est-à-dire Il l'a aplani. Les arabes qualifient une chose comme étant duḥiyat lorsqu'elle est aplanie. Il est dit du nid d'autruche qu'il est udḥiya car il est aplani au sol. »— Tafsīr al-Qurṭubī
« Pour Qatāda, al-Suddī et Sufyān, le terme daḥāhā renvoie à l'aplanissement... Al-Ṭabarī dit : ad-daḥw chez les arabes est l'aplanissement (al-basṭ) et l'extension (al-madd). »— Tafsīr al-Ṭabarī ([shamela.ws](https://shamela.ws/book/43/14124#p1))
« Il l'a aplani. Elle a été conçue sans aplanissement avant la création des cieux. Pour Ibn ʿAbbās, Allāh a créé la terre avant les cieux mais sans l'avoir étendue, puis Il s'est occupé des cieux et en fit sept, puis après cela Il a aplani la terre. »— Tafsīr al-Baghawī

## 05 La Terre n'est pas un kawkab (planète)

Ni Allāh dans Son Livre, ni Son Messager ﷺ, ni les musulmans des premiers siècles n'ont désigné la Terre par le terme **كوكب** (*kawkab* — planète, étoile, astre). Ceux qui l'ont fait sont les imitateurs du « nouveau comité astronomique » européen.


إِنَّا زَيَّنَّا السَّمَاءَ الدُّنْيَا بِزِينَةٍ الْكَوَاكِبِ ۝ وَحِفْظًا مِّن كُلِّ شَيْطَانٍ مَّارِدٍ


« Nous avons décoré le ciel le plus proche d'un décor : les étoiles (kawākib), afin de le protéger contre tout diable rebelle. »


Al-Ṣāffāt — S37 V6-7


Le Coran dit que la Terre est un lit et le ciel est un toit. Comment les **fondations** d'une construction peuvent-elles être un **ornement de son toit** ? Le kawkab désigne l'étoile : sa place est en hauteur, ses caractéristiques sont l'illumination, l'éclat, l'ascension — tout l'inverse de la terre.


« Sa parole "la terre est un kawkab" n'est que fausseté et mensonge sur Allāh Le Très-Haut qui ne l'a pas nommée ainsi. Celui qui l'a créée l'a appelée "terre" (arḍ). Le kawkab désigne l'étoile et sa place est en hauteur. »— Shaykh al-Kāfī al-Tūnisī, Al-Masāʾil al-Kāfiyya ([shamela.ws](https://shamela.ws/book/13607/112#p1))

## 06 La Terre immobile, fixe et stable

Le mot « terre » est cité plus de 450 fois et **n'est jamais lié à un verbe de mouvement**. Le Soleil, cité 33 fois, est systématiquement lié à des verbes de déplacement : courir (tajrī), voguer, se lever, se coucher, se prosterner.


أَمَّن جَعَلَ الْأَرْضَ قَرَارًا وَجَعَلَ خِلَالَهَا أَنْهَارًا وَجَعَلَ لَهَا رَوَاسِيَ


« N'est-ce pas Lui qui a établi la Terre comme demeure stable (qarāran), placé des rivières à travers elle, et disposé des montagnes ? »


An-Naml — S27 V61


وَأَلْقَىٰ فِي الْأَرْضِ رَوَاسِيَ أَن تَمِيدَ بِكُمْ


« Et Il a enfoncé des montagnes dans la terre pour qu'elle ne s'ébranle pas (tamīd) avec vous. »


Luqmān — S31 V10


**Le raisonnement :** Pourquoi Allāh placerait-Il des montagnes comme des ancres (rawāsī) pour empêcher la Terre de vaciller, si elle était déjà en rotation à 1 670 km/h et en orbite à 107 000 km/h ? Les montagnes empêcheraient un vacillement mais pas une rotation de 465 m/s ? L'explication la plus simple : la Terre est immobile, et les montagnes la stabilisent contre les secousses.

## 07 Le Soleil est mobile

وَالشَّمْسُ تَجْرِي لِمُسْتَقَرٍّ لَّهَا


« Et le soleil court (tajrī) vers un gîte qui lui est assigné. »


Yā Sīn — S36 V38


Le terme **تَجْرِي** (*tajrī*) désigne le déplacement rapide. Dans le Lisān al-ʿArab, la course du Soleil s'effectue du levant vers le couchant. Le Shaykh Ḥamūd al-Tuwayjirī recense **22 endroits dans le Coran** qui prouvent la mobilité du Soleil (Al-Ṣawāʿiq al-Shadīda, p. 10).


وَسَخَّرَ لَكُمُ الشَّمْسَ وَالْقَمَرَ دَائِبَيْنِ


« Et pour vous, Il a assujetti le soleil et la lune à un mouvement perpétuel (dāʾibayn). »


Ibrāhīm — S14 V33


« C'est-à-dire constamment, continuellement jusqu'au jour du jugement. »— Tafsīr Ibn Kathīr

## 08 Impossible de franchir les limites des cieux et de la terre

يَا مَعْشَرَ الْجِنِّ وَالْإِنسِ إِنِ اسْتَطَعْتُمْ أَن تَنفُذُوا مِنْ أَقْطَارِ السَّمَاوَاتِ وَالْأَرْضِ فَانفُذُوا ۚ لَا تَنفُذُونَ إِلَّا بِسُلْطَانٍ


« Ô peuple de djinns et d'hommes, si vous pouvez franchir les limites des cieux et de la terre, alors faites-le — mais vous ne pourrez les franchir qu'à l'aide d'un pouvoir [que vous ne possédez pas]. »


Ar-Raḥmān — S55 V33


مِنْهَا خَلَقْنَاكُمْ وَفِيهَا نُعِيدُكُمْ وَمِنْهَا نُخْرِجُكُمْ تَارَةً أُخْرَىٰ


« C'est d'elle que Nous vous avons créés, en elle Nous vous ferons retourner, et c'est d'elle que Nous vous ferons sortir une autre fois. »


Ṭā Hā — S20 V55


La vie se fait sur terre. La mort se fait sur terre. La résurrection se fait depuis la terre. Il est impossible d'avoir des « côtés » ou des « limites » (aqṭār) sur une sphère — mais parfaitement cohérent sur un plan fini bordé (voir aussi [O7 — L'espace impossible](/lespace-une-frontiere-infranchissable/)).


## 09 Conclusion

Le Coran décrit, avec une clarté et une cohérence remarquables, une Terre **étendue, aplanie, déployée comme un lit, stabilisée par des montagnes, immobile**. Un Soleil **en mouvement perpétuel**. Un ciel **comme un toit protégé**. Et un défi lancé aux djinns et aux hommes de franchir les limites — défi qu'ils ne relèveront pas.


Ces descriptions ne sont pas des métaphores isolées. Sept termes différents, dans plus de vingt versets, confirmés par les exégèses classiques, les dictionnaires de la langue arabe, et le consensus des Compagnons et des Tābiʿīn. L'interprétation sphérique n'apparaît qu'avec le concordisme du XXᵉ siècle — elle n'a aucun fondement dans les 13 premiers siècles de l'exégèse.


Pour l'analyse du prétendu consensus sur la sphéricité, voir [B5](/le-consensus-sur-la-sphericite/). Pour la liste des 95 savants qui ont affirmé la planéité, voir [B2](/pres-de-cent-savants-de-lislam/). Pour la critique du concordisme, voir [N5](/le-concordisme/).


 📄
 Document complet : Les preuves religieuses et scientifiques (PDF)


 L'intégralité des preuves coraniques, prophétiques et linguistiques sur la planéité, l'immobilité de la Terre, la mobilité du Soleil et l'impossibilité de franchir les cieux.


 [Consulter le PDF ↗](https://terre-etendue-islam.fr/wp-content/uploads/2026/04/document-maitre-preuves-religieuses.pdf)

## Références


 - Tafsīr al-Ṭabarī (Jāmiʿ al-Bayān). [shamela.ws](https://shamela.ws/book/43)

 - Tafsīr Ibn Kathīr. [shamela.ws](https://shamela.ws/book/1014)

 - Tafsīr al-Qurṭubī (al-Jāmiʿ li-Aḥkām al-Qurʾān). [shamela.ws](https://shamela.ws/book/540)

 - Tafsīr al-Jalālayn. [shamela.ws](https://shamela.ws/book/203)

 - Tafsīr al-Baghawī (Maʿālim al-Tanzīl). [shamela.ws](https://shamela.ws/book/91)

 - Tafsīr Muqātil ibn Sulaymān. [shamela.ws](https://shamela.ws/book/23614)

 - Lisān al-ʿArab, Ibn Manẓūr. [shamela.ws](https://shamela.ws/book/1687)

 - Al-Kāfī al-Tūnisī, Al-Masāʾil al-Kāfiyya. [shamela.ws](https://shamela.ws/book/13607/112#p1)

 - Al-Tuwayjirī, Al-Ṣawāʿiq al-Shadīda ʿalā Atbāʿ al-Hayʾa al-Jadīda.

 - Document « Les preuves religieuses et scientifiques révélant l'imposture de la Terre sphérique ».


					

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