---
title: "Le « consensus » sur la sphéricité"
description: ".nx-nav{width:100%;background:#F7F2E8;border-bottom:1px solid #DDD5C5;padding:0 2rem;position:sticky;top:0;z-index:999} .nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;ju..."
date: "2026-04-18"
author: "Terre Etendue"
category: "library"
tags: ["la-bibliothèque"]
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
:root{--bg:#F7F2E8;--bg2:#EDE5D5;--brown:#6B4226;--brown-l:#8B5C36;--brown-g:rgba(139,92,54,.12);--gold:#B8860B;--gold-g:rgba(212,175,55,.12);--t1:#2C1810;--t2:#5C4A3A;--t3:#8A7A6A;--bdr:#DDD5C5;--f1:'Cormorant Garamond',Georgia,serif;--f2:'Outfit',sans-serif;--f3:'Cormorant Garamond',Georgia,serif;--fa:'Amiri',serif}
.b5{background:var(--bg);color:var(--t1);padding:0}
.b5-h{padding:5rem 2rem 3.5rem;text-align:center;position:relative;overflow:hidden}
.b5-h::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 50% at 50% 30%,rgba(139,92,54,.05),transparent 70%);pointer-events:none}
.b5-tag{display:inline-block;font-family:var(--f2);font-size:.62rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--brown-l);background:var(--brown-g);border:1px solid rgba(139,92,54,.25);padding:.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.b5-title{font-family:var(--f1);font-size:clamp(1.7rem,4vw,2.4rem);font-weight:700;color:var(--brown-l);line-height:1.15;margin:0 0 1rem;max-width:800px;margin-left:auto;margin-right:auto}
.b5-sub{font-family:var(--f3);font-size:1.02rem;line-height:1.7;color:var(--t2);max-width:650px;margin:0 auto 2rem}
.b5-meta{max-width:800px;margin:0 auto;padding:1.2em 0;border-top:1px solid var(--bdr);border-bottom:1px solid var(--bdr);display:flex;flex-wrap:wrap;gap:.5em 2em;font-family:var(--f2);font-size:.75rem;color:var(--t3)}
.b5-meta dt{font-weight:600;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem}
.b5-meta dd{margin:0 0 .6em;color:var(--t2)}
.b5-lay{display:flex;gap:2.5rem;max-width:1200px;margin:0 auto;padding:2.5rem 2rem 5rem;align-items:flex-start}
.b5-nav{flex:0 0 255px;position:sticky;top:80px;max-height:calc(100vh - 100px);overflow-y:auto;padding:1.5rem;background:var(--bg2);border:1px solid var(--bdr);border-radius:10px}
.b5-nav::-webkit-scrollbar{width:3px}.b5-nav::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}
.b5-nav__t{font-family:var(--f2);font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--brown-l);margin:0 0 1rem;padding-bottom:.6rem;border-bottom:1px solid var(--bdr)}
.b5-nav ul{list-style:none;padding:0;margin:0}.b5-nav li{margin-bottom:.35rem}
.b5-nav a{display:block;font-family:var(--f2);font-size:.76rem;color:var(--t3);text-decoration:none;padding:.4em .8em;border-radius:5px;border-left:2px solid transparent;transition:all .25s ease;line-height:1.35}
.b5-nav a:hover{color:var(--t1);background:rgba(139,92,54,.06);border-left-color:var(--brown-l)}
.b5-nav a.active{color:var(--brown-l);background:var(--brown-g);border-left-color:var(--brown-l);font-weight:500}
.b5-nav .num{font-size:.6rem;font-weight:600;color:var(--brown-l);margin-right:.4em;opacity:.7}
.b5-nav__bk{display:block;margin-top:1.2rem;padding:.6em 1em;background:var(--brown-l);color:#2C1810;font-family:var(--f2);font-size:.72rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;text-align:center;border-radius:5px;transition:background .3s ease}
.b5-nav__bk:hover{background:#A97544}
.b5-b{flex:1;min-width:0;max-width:800px;font-family:var(--f3);font-size:clamp(1rem,1.8vw,1.08rem);line-height:1.75;color:var(--t1)}
.b5-b p{margin-bottom:1.4em;text-align:justify;hyphens:auto}
.b5-b a{color:var(--brown-l);text-decoration:underline;text-underline-offset:3px}
.b5-b h2{font-family:var(--f1);font-size:clamp(1.4rem,3vw,1.85rem);font-weight:700;color:var(--t1);margin:3em 0 .8em;padding-bottom:.4em;border-bottom:1px solid var(--bdr);line-height:1.25;scroll-margin-top:90px}
.b5-b h3{font-family:var(--f2);font-size:clamp(1rem,1.8vw,1.15rem);font-weight:600;color:var(--brown-l);text-transform:uppercase;letter-spacing:.06em;margin:2em 0 .6em;line-height:1.35;scroll-margin-top:90px}
.sn{font-family:var(--f2);font-size:.65rem;font-weight:600;color:var(--brown-l);background:var(--brown-g);border:1px solid rgba(139,92,54,.25);padding:.2em .6em;border-radius:3px;margin-right:.6em;vertical-align:middle}
.bq{margin:2em 0;padding:1.5em 2em;background:linear-gradient(135deg,var(--brown-g),transparent 70%);border-left:3px solid var(--brown);border-radius:0 8px 8px 0;font-family:var(--f3);font-style:italic;font-size:1.02em;line-height:1.75;color:var(--t1)}
.bq cite{display:block;margin-top:.8em;font-size:.78em;font-style:normal;font-family:var(--f2);color:var(--t3)}
.bqa{margin:2em 0;padding:1.5em 2em;background:linear-gradient(135deg,var(--gold-g),transparent 70%);border-left:3px solid var(--gold);border-radius:0 8px 8px 0;font-family:var(--fa);font-size:1.15em;line-height:2;color:var(--gold);direction:rtl;text-align:right}
.db{margin:2em 0;padding:1.4em 1.8em;background:var(--bg2);border:1px solid var(--bdr);border-radius:8px}
.db__l{display:inline-block;font-family:var(--f2);font-size:.65rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:var(--brown-l);background:var(--brown-g);padding:.2em .7em;border-radius:3px;margin-bottom:.8em}
.db p{font-size:.92rem;margin-bottom:.8em;text-align:left}
.kp{margin:1.5em 0;padding:1.2em 1.6em;background:var(--bg2);border-left:3px solid var(--brown);border-radius:0 8px 8px 0;font-family:var(--f2);font-size:.9rem;line-height:1.6;color:var(--t2)}
.kp strong{color:var(--t1)}
.tw{margin:2em 0;overflow-x:auto}
.tb{width:100%;border-collapse:collapse;font-family:var(--f2);font-size:.78rem}
.tb th{background:var(--bg2);color:var(--brown-l);font-weight:600;text-transform:uppercase;letter-spacing:.06em;font-size:.66rem;padding:.7em .8em;text-align:left;border-bottom:1px solid var(--bdr)}
.tb td{padding:.6em .8em;border-bottom:1px solid var(--bdr);color:var(--t2);vertical-align:top}
.tb tr:hover td{background:rgba(139,92,54,.03)}
.b5-refs{margin-top:3em;padding-top:2em;border-top:1px solid var(--bdr)}
.b5-refs h2{border-bottom:none;padding-bottom:0;font-size:1.3rem}
.b5-refs ol{padding-left:1.5em;font-family:var(--f2);font-size:.82rem;color:var(--t2);line-height:1.7}
.b5-refs li{margin-bottom:.6em}
@media(max-width:900px){.b5-lay{flex-direction:column;padding:1.5rem}.b5-nav{position:static;flex:none;width:100%;max-height:none;margin-bottom:2rem}.b5-h{padding:3.5rem 1.5rem 2.5rem}}


 La Bibliothèque — BIB-2026-005
 
# Le « consensus » sur la sphéricité : cinq raisons de le remettre en question

 Le passage du Majmūʿ al-Fatāwā (6/586-587) ne satisfait pas les critères d'un ijmāʿ sharʿī valide. Analyse en cinq axes.
 
 AuteurTerre Étendue Islam
 DateAvril 2026 — v1.0
 Lecture~25 min
 SourcesMajmūʿ al-Fatāwā · Al-Malāḥim · Almageste
 

 
 
## Sommaire

 
 [01 Le texte contesté](#i-texte)

 - [02 L'anomalie philologique](#i-philo)

 - [03 La chaîne ptoléméenne](#i-chaine)

 - [04 400 ans de silence](#i-silence)

 - [05 Ibn al-Munādī contre lui-même](#i-contradiction)

 - [06 Ibn Taymiyyah contre les Grecs](#i-taymiyyah)

 - [07 Conclusion](#i-ccl)

 - [Références](#i-refs)

 

 [← Retour à la Bibliothèque](/la-bibliotheque/)
 

## 01 Le texte contesté

Dans le monde musulman contemporain, un passage est régulièrement cité comme preuve définitive d'un « consensus islamique sur la sphéricité de la Terre ». Il se trouve dans le *Majmūʿ al-Fatāwā* d'Ibn Taymiyyah (vol. 6, p. 586-587) et rapporte un propos d'Ibn al-Munādī (m. 336H) :


وأما إجماع العلماء، فقال الإمام أبو الحسين أحمد بن جعفر بن المنادي: لا خلاف بين العلماء أن السماء على مثال الكرة... وكذلك أجمعوا على أن الأرض بجميع حركاتها من البر والبحر مثل الكرة
« Quant au consensus des savants, l'imam Ibn al-Munādī a déclaré : il n'y a pas de divergence parmi les savants que le ciel est à l'image d'une sphère... et de même ils ont été unanimes que la Terre, dans l'ensemble de **ses mouvements**, terres et mers, est semblable à une sphère. »
— Ibn Taymiyyah, Majmūʿ al-Fatāwā, vol. 6, p. 586-587
L'expression critique est **بجميع حركاتها** (*bi-jamīʿ ḥarakātihā* — « dans tous ses mouvements »). Cinq anomalies convergentes remettent en question l'authenticité et la validité de ce consensus.


## 02 Axe 1 — L'anomalie philologique : حركاتها ou أجزائها ?

💡 En termes simples


Imaginez qu'on vous montre un testament et qu'un seul mot change tout l'héritage. Le mot « mouvements » (حركاتها) dans le texte d'Ibn Taymiyyah n'apparaît dans aucune source antérieure — toutes les sources plus anciennes disent « parties » (أجزائها). C'est comme trouver un mot dans un contrat que personne n'a jamais écrit. Soit quelqu'un l'a ajouté, soit un copiste a fait une erreur en recopiant le manuscrit à la main (en arabe manuscrit, les deux mots se ressemblent graphiquement). De plus, le mot « mouvements » implique que la Terre bouge — une idée que ni les astronomes du IVᵉ siècle hégirien ni Ptolémée lui-même n'enseignaient.


Toutes les sources astronomiques antérieures à Ibn Taymiyyah emploient le terme **أجزائها** (*ajzāʾihā* — « ses parties »), non حركاتها (« ses mouvements ») :


SourceDateTermeSens

Ptolémée (trad. arabe)IIᵉ s. / trad. IXᵉأجزائهاses parties
Al-Farghānī~861 ECأجزائهاses parties
Ibn Rustah~300Hأجزائهاses parties
Al-Masʿūdī~345Hأجزائهاses parties
**Ibn Taymiyyah (Fatāwā)****~700H****حركاتها****ses mouvements ⚠**


La divergence est **isolée** au texte transmis par Ibn Taymiyyah. En écriture arabe manuscrite, la différence graphique entre أجزائها et حركاتها est minimale — rendant une corruption de copiste plausible sur quatre siècles de transmission manuscrite. De plus, l'expression « ses mouvements » implique que la Terre possède des mouvements propres — notion incompatible avec la cosmologie du IVᵉ siècle hégirien, tant islamique que ptoléméenne, qui décrivait une **Terre immobile**.


## 03 Axe 2 — La filiation ptoléméenne

Le contenu doctrinal du « consensus » est traçable directement jusqu'à l'Almageste de Ptolémée, transmis en arabe via al-Farghānī et Ibn Rustah. C'est une chaîne de transmission de contenu astronomique hellénisé — **pas un isnād sharʿī** fondé sur le Coran et la Sunna.


**Ce n'est pas un consensus de savants de la Loi sur la base de la Révélation.** C'est un accord d'astronomes ptoléméens présenté, par raccourci, comme un consensus théologique. La distinction entre ʿulamāʾ al-sharʿ et ahl al-hayʾa (voir [B2](/pres-de-cent-savants-de-lislam/)) est ici fondamentale : « les savants » d'Ibn al-Munādī sont les astronomes hellénisés, pas les mufassirīn.

## 04 Axe 3 — Quatre cents ans de silence

Entre Ibn al-Munādī (m. 336H) et Ibn Taymiyyah (m. 728H), **aucun savant intermédiaire** ne mentionne ce consensus :


SavantDécèsSpécialitéMention du consensus ?

Ibn ʿAbd al-Barr463HCompilateur d'ijmāʿAucune
Al-Baghawī516HExégèse, ḥadīthAucune
Ibn al-Jawzī597HḤanbalite, encyclopédisteAucune
Al-Qurṭubī671HExégèse exhaustiveAucune
Ibn Kathīr774HÉlève d'Ibn TaymiyyahNe reprend pas


Ibn ʿAbd al-Barr, le plus grand compilateur de consensus de l'histoire islamique, ne mentionne nulle part un ijmāʿ sur la sphéricité. Ibn Kathīr, propre élève d'Ibn Taymiyyah, ne reprend pas ce consensus dans son tafsīr. **Un consensus qui n'est transmis par personne pendant 400 ans n'est pas un consensus — c'est une citation isolée.**


## 05 Axe 4 — Ibn al-Munādī contre lui-même

Dans *al-Malāḥim* (p. 337), le seul ouvrage édité et conservé d'Ibn al-Munādī, on lit :


ويأذن للأرضين فيستطَّحن كما كن
« Et [Allah] autorisera les terres à redevenir planes (yastaṭṭiḥna) comme elles l'étaient. »
— Ibn al-Munādī, al-Malāḥim, p. 337
**Contradiction fatale :** Le verbe *istaṭṭaḥa* dérive de la racine **س-ط-ح** — la même racine que le verset coranique 88:20 (suṭiḥat). La formulation « *yastaṭṭiḥna kamā kunna* » (« elles redeviendront planes comme elles l'étaient ») implique un **état originel de planéité**. Comment le même auteur pourrait-il affirmer un consensus de sphéricité et décrire la Terre comme originellement plane dans son propre ouvrage ?

## 06 Axe 5 — Ibn Taymiyyah lui-même réfute sa propre citation

Dans le même recueil (*Majmūʿ al-Fatāwā*, 6/357), Ibn Taymiyyah écrit de sa propre plume :


والله تعالى بسط الأرض للأنام، وأرساها بالجبال لئلا تميد بهم، وجعلها قراراً ومهاداً وفراشاً
« Allah a étendu (basaṭa) la Terre pour les créatures, et l'a ancrée par des montagnes pour qu'elle ne vacille pas, et en a fait un lieu stable (qarāran), un berceau (mihādan) et un tapis (firāshan). »
— Ibn Taymiyyah, Majmūʿ al-Fatāwā, vol. 6, p. 357
Et dans *Bayān Talbīs al-Jahmiyyah*, il formule explicitement :


« La parole d'aucun d'entre eux [les cosmologues grecs] n'est une preuve, et il n'est pas permis de bâtir sur elle un fondement de la religion. »
— Ibn Taymiyyah, Bayān Talbīs al-Jahmiyyah
Ibn Taymiyyah rejette explicitement l'autorité doctrinale des cosmologues grecs, tout en rapportant — si le passage est authentique — un « consensus » dont le contenu provient directement de cette tradition. Il utilise *basaṭa*, *mihādan*, *firāshan* — les mêmes termes coraniques de planéité — pour décrire la Terre de sa propre plume.


## 07 Conclusion : cinq failles, aucun consensus

Cinq anomalies convergentes
**1. Philologie :** حركاتها est un hapax isolé — toutes les sources antérieures attestent أجزائها. Corruption de copiste plausible.


**2. Filiation :** Le contenu est ptoléméen, transmis par des astronomes hellénisés — pas un isnād sharʿī.


**3. Silence :** 400 ans sans transmission. Aucun compilateur d'ijmāʿ ne le mentionne. Ibn Kathīr ne le reprend pas.


**4. Contradiction :** Ibn al-Munādī lui-même décrit les terres comme « originellement planes » dans al-Malāḥim.


**5. Incohérence :** Ibn Taymiyyah rejette l'autorité des Grecs et utilise le vocabulaire coranique de planéité dans ses propres écrits.


Ce passage ne satisfait pas les critères méthodologiques d'un ijmāʿ sharʿī — pas même ceux qu'Ibn Taymiyyah lui-même établit dans d'autres contextes juridiques : des imams identifiés par leurs noms, une chaîne de transmission documentée, et une absence de divergence connue. **Ce consensus n'en remplit aucun.**


## Références


 - Ibn Taymiyyah (m. 728H). *Majmūʿ al-Fatāwā*, éd. Ibn Qāsim, vol. 6, p. 356-357 et 586-587.

 - Ibn Taymiyyah. *Bayān Talbīs al-Jahmiyyah*, éd. Ibn Qāsim.

 - Ibn al-Munādī (m. 336H). *Al-Malāḥim*, p. 337.

 - Al-Farghānī (m. ~861 EC). *Kitāb fī Jawāmiʿ ʿIlm al-Nujūm*.

 - Ptolémée (IIᵉ s. EC). *Al-Majisṭī* — traductions arabes.

 - Ibn Rustah (m. ~300H). *Al-Aʿlāq al-Nafīsa*.

 - Ibn ʿAbd al-Barr (m. 463H). *Al-Tamhīd* — aucune mention du consensus.

 - Ibn Kathīr (m. 774H). *Tafsīr al-Qurʾān al-ʿAẓīm* — ne reprend pas le consensus.


					

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