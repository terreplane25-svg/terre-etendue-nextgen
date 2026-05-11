---
title: "Le concordisme"
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
:root{--bg:#F7F2E8;--bg2:#EDE5D5;--bg3:#111;--gold:#B8860B;--gold-s:#B8962E;--gold-g:rgba(212,175,55,.12);--cobalt:#1B5E3C;--cobalt-l:#2D8B57;--cobalt-g:rgba(30,58,138,.15);--t1:#2C1810;--t2:#5C4A3A;--t3:#8A7A6A;--bdr:#DDD5C5;--f1:'Cormorant Garamond',Georgia,serif;--f2:'Outfit',sans-serif;--f3:'Cormorant Garamond',Georgia,serif;--fa:'Amiri',serif}
.n5{background:var(--bg);color:var(--t1);padding:0}
.n5-h{padding:5rem 2rem 3.5rem;text-align:center;position:relative;overflow:hidden}
.n5-h::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 50% at 50% 30%,rgba(212,175,55,.04),transparent 70%);pointer-events:none}
.n5-tag{display:inline-block;font-family:var(--f2);font-size:.62rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);background:var(--gold-g);border:1px solid rgba(212,175,55,.2);padding:.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.n5-title{font-family:var(--f1);font-size:clamp(1.8rem,4.5vw,2.6rem);font-weight:700;color:var(--gold);line-height:1.15;margin:0 0 1rem;max-width:800px;margin-left:auto;margin-right:auto}
.n5-sub{font-family:var(--f3);font-size:1.02rem;line-height:1.7;color:var(--t2);max-width:650px;margin:0 auto 2rem}
.n5-meta{max-width:800px;margin:0 auto;padding:1.2em 0;border-top:1px solid var(--bdr);border-bottom:1px solid var(--bdr);display:flex;flex-wrap:wrap;gap:.5em 2em;font-family:var(--f2);font-size:.75rem;color:var(--t3)}
.n5-meta dt{font-weight:600;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem}
.n5-meta dd{margin:0 0 .6em;color:var(--t2)}
.n5-lay{display:flex;gap:2.5rem;max-width:1200px;margin:0 auto;padding:2.5rem 2rem 5rem;align-items:flex-start}
.n5-nav{flex:0 0 255px;position:sticky;top:80px;max-height:calc(100vh - 100px);overflow-y:auto;padding:1.5rem;background:var(--bg2);border:1px solid var(--bdr);border-radius:10px}
.n5-nav::-webkit-scrollbar{width:3px}.n5-nav::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}
.n5-nav__t{font-family:var(--f2);font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--gold);margin:0 0 1rem;padding-bottom:.6rem;border-bottom:1px solid var(--bdr)}
.n5-nav ul{list-style:none;padding:0;margin:0}.n5-nav li{margin-bottom:.35rem}
.n5-nav a{display:block;font-family:var(--f2);font-size:.76rem;color:var(--t3);text-decoration:none;padding:.4em .8em;border-radius:5px;border-left:2px solid transparent;transition:all .25s ease;line-height:1.35}
.n5-nav a:hover{color:var(--t1);background:rgba(212,175,55,.05);border-left-color:var(--gold)}
.n5-nav a.active{color:var(--gold);background:var(--gold-g);border-left-color:var(--gold);font-weight:500}
.n5-nav .num{font-size:.6rem;font-weight:600;color:var(--gold-s);margin-right:.4em;opacity:.7}
.n5-nav .sub{padding:0 0 0 1.2em;margin:.15rem 0 .2rem}.n5-nav .sub a{font-size:.7rem;padding:.3em .8em}
.n5-nav__bk{display:block;margin-top:1.2rem;padding:.6em 1em;background:var(--gold);color:var(--bg);font-family:var(--f2);font-size:.72rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;text-align:center;border-radius:5px;transition:background .3s ease}
.n5-nav__bk:hover{background:#D4A017}
.n5-b{flex:1;min-width:0;max-width:800px;font-family:var(--f3);font-size:clamp(1rem,1.8vw,1.08rem);line-height:1.75;color:var(--t1)}
.n5-b p{margin-bottom:1.4em;text-align:justify;hyphens:auto}
.n5-b a{color:var(--gold);text-decoration:underline;text-underline-offset:3px;text-decoration-color:var(--gold-s)}
.n5-b h2{font-family:var(--f1);font-size:clamp(1.4rem,3vw,1.85rem);font-weight:700;color:var(--t1);margin:3em 0 .8em;padding-bottom:.4em;border-bottom:1px solid var(--bdr);line-height:1.25;scroll-margin-top:90px}
.n5-b h3{font-family:var(--f2);font-size:clamp(1rem,1.8vw,1.15rem);font-weight:600;color:var(--cobalt-l);text-transform:uppercase;letter-spacing:.06em;margin:2em 0 .6em;line-height:1.35;scroll-margin-top:90px}
.sn{font-family:var(--f2);font-size:.65rem;font-weight:600;color:var(--gold);background:var(--gold-g);border:1px solid rgba(212,175,55,.2);padding:.2em .6em;border-radius:3px;margin-right:.6em;vertical-align:middle}
.bq{margin:2em 0;padding:1.5em 2em;background:linear-gradient(135deg,var(--cobalt-g),transparent 70%);border-left:3px solid var(--cobalt);border-radius:0 8px 8px 0;font-family:var(--f3);font-style:italic;font-size:1.02em;line-height:1.75;color:var(--t1)}
.bq cite{display:block;margin-top:.8em;font-size:.78em;font-style:normal;font-family:var(--f2);color:var(--t3)}
.bqs{margin:2em 0;padding:1.5em 2em 1.5em 2.2em;background:linear-gradient(135deg,var(--gold-g),transparent 70%);border-left:3px solid var(--gold);border-radius:0 8px 8px 0;font-family:var(--f1);font-style:italic;font-size:1.05em;line-height:1.8;color:var(--gold)}
.bqs cite{display:block;margin-top:.8em;font-size:.75em;font-style:normal;font-family:var(--f2);color:var(--t3);text-transform:uppercase;letter-spacing:.06em}
.bqa{margin:2em 0;padding:1.5em 2em;background:linear-gradient(135deg,var(--gold-g),transparent 70%);border-left:3px solid var(--gold);border-radius:0 8px 8px 0;font-family:var(--fa);font-size:1.2em;line-height:2;color:var(--gold);direction:rtl;text-align:right}
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
.n5-refs{margin-top:3em;padding-top:2em;border-top:1px solid var(--bdr)}
.n5-refs h2{border-bottom:none;padding-bottom:0;font-size:1.3rem}
.n5-refs ol{padding-left:1.5em;font-family:var(--f2);font-size:.82rem;color:var(--t2);line-height:1.7}
.n5-refs li{margin-bottom:.6em}
@media(max-width:900px){.n5-lay{flex-direction:column;padding:1.5rem}.n5-nav{position:static;flex:none;width:100%;max-height:none;margin-bottom:2rem}.n5-h{padding:3.5rem 1.5rem 2.5rem}}


 Le Nexus — NXS-2026-005
 
# Le concordisme : quand le Coran est trahi par ses défenseurs

 Plier la Révélation pour la faire entrer dans le moule des hypothèses humaines ne défend pas l'islam — il le diminue.
 
 AuteurTerre Étendue Islam
 DateAvril 2026 — v1.0
 Lecture~30 min
 DomaineExégèse · Épistémologie · Critique
 

 
 
## Sommaire

 
 [01 Le courant concordiste](#c-intro)

 - [02 Ibn Taymiyyah : le couperet](#c-taymiyyah)

 - [03 Cas 1 : Ratq/Fatq ≠ Big Bang](#c-ratq)
 [Philologie](#c-philo)
- [Les Salaf](#c-salaf)
- [Al-Ṭabarī](#c-tabari)


 
 - [04 Cas 2 : Daḥā ≠ œuf d'autruche](#c-daha)

 - [05 Cas 3 : Falak ≠ orbite](#c-falak)

 - [06 Le schéma répétitif](#c-schema)

 - [07 Le raisonnement circulaire](#c-cercle)

 - [08 Le danger théologique](#c-danger)

 - [09 Conclusion](#c-ccl)

 - [Références](#c-refs)

 

 [← Retour au Nexus](/le-nexus/)
 

## 01 Le courant concordiste : genèse et propagation

Au cours des dernières décennies, une tendance s'est largement diffusée dans certains milieux musulmans : celle qui consiste à chercher dans le Coran des preuves anticipées de découvertes scientifiques modernes, et à présenter ces correspondances supposées comme une preuve de la vérité de l'islam. Ce discours, communément appelé *iʿjāz ʿilmī* (« miracle scientifique »), a été institutionnalisé par Ṭanṭāwī Jawharī (m. 1940), popularisé par Maurice Bucaille (*La Bible, le Coran et la Science*, 1976) et développé par Zaghlūl al-Najjār.


Le concordisme affirme que le Coran « contient » le Big Bang (verset 21:30), l'expansion de l'univers (51:47), les stades embryologiques modernes (23:13-14), la rotation de la Terre (27:88), et l'halocline marine (55:19-20). Cette démarche souffre de quatre défauts fondamentaux : elle **déforme les tafsīr classiques** en sélectionnant uniquement les sens qui semblent correspondre à une théorie moderne ; elle **détache les versets de leur contexte** linguistique et spirituel ; elle **repose sur des théories instables**, susceptibles d'être abandonnées ; et elle **affaiblit la lecture théologique** des versets en les réduisant à des prédictions pseudo-scientifiques.


💡 Qu'est-ce que le concordisme ?


Le concordisme, c'est l'idée que le Coran « prédit » les découvertes scientifiques modernes. Par exemple : « Le Big Bang est mentionné dans le Coran » ou « Le Coran décrit les couches de l'atmosphère ». Le problème ? Les premiers exégètes — ceux qui comprenaient l'arabe mieux que quiconque — n'ont jamais lu ces versets de cette façon. Les sens « scientifiques » n'apparaissent qu'au XXᵉ siècle, quand des auteurs musulmans cherchent à « prouver » le Coran par la science moderne. Si demain la science change de modèle (comme elle l'a déjà fait des dizaines de fois), ces « preuves » s'effondrent — et le Coran est affaibli aux yeux du public. C'est le piège du concordisme.


وَأَنزَلْنَا إِلَيْكَ الْكِتَابَ بِالْحَقِّ مُصَدِّقًا لِمَا بَيْنَ يَدَيْهِ مِنَ الْكِتَابِ وَمُهَيْمِنًا عَلَيْهِ


« Et Nous t'avons révélé le Livre avec la vérité, confirmant ce qui était avant lui et dominant (muhaymin) sur lui. »
Sourate Al-Māʾida — 5:48
Le Coran est *muhaymin* — **dominant**, non dominé. Celui qui le subordonne à des théories mouvantes n'a rien compris à la nature même de la Parole d'Allah.


## 02 Ibn Taymiyyah : le couperet

Cette pathologie n'est pas nouvelle. Déjà au XIIIᵉ siècle, Taqī ad-Dīn Aḥmad ibn Taymiyyah affrontait ceux qui voulaient subordonner le Coran aux philosophies grecques, comme aujourd'hui on veut le subordonner aux cosmologies athées. Son œuvre *Darʾ Taʿāruḍ al-ʿAql wa al-Naql* (Réfutation de la Contradiction entre Raison et Révélation) tranche net :


وإذا تعارض العقل الصريح والنقل الصحيح وجب تقديم النقل، فإن العقل يعلم صدق الرسول بالنقل، والنقل هو الذي دل على صحة العقل، فصار تقديم العقل على النقل قدحًا في العقل والنقل جميعًا
« Lorsque la raison claire et la Révélation authentique semblent s'opposer, il est obligatoire de donner priorité à la Révélation. Car c'est la raison qui atteste de la véracité du Messager par la Révélation, et c'est la Révélation qui a attesté de la validité de la raison. Préférer la raison à la Révélation revient à invalider les deux à la fois. »
— Ibn Taymiyyah, Darʾ Taʿāruḍ al-ʿAql wa al-Naql, 1/120
فالعقل الصريح لا يعارض النقل الصحيح، ولكن من ظن تعارضهما فهو إما لفسادٍ في العقل أو لعدم فهمٍ للنقل
« La raison claire ne contredit jamais la Révélation authentique. Celui qui pense qu'elles s'opposent, c'est soit par corruption de sa raison, soit par incompréhension de la Révélation. »
— Ibn Taymiyyah, Darʾ Taʿāruḍ, 1/152
Celui qui élève les hypothèses humaines au-dessus du Livre d'Allah a porté atteinte à la Révélation et à sa propre raison. Le Prophète ﷺ avait annoncé cette maladie :


لَتَتَّبِعُنَّ سَنَنَ مَنْ كَانَ قَبْلَكُمْ شِبْرًا بِشِبْرٍ وَذِرَاعًا بِذِرَاعٍ حَتَّى لَوْ دَخَلُوا جُحْرَ ضَبٍّ لَدَخَلْتُمُوهُ


« Vous suivrez assurément les voies de ceux qui vous ont précédés, pouce par pouce, coudée par coudée, au point que s'ils entraient dans le terrier d'un lézard, vous les y suivriez. »
Rapporté par Al-Bukhari et Muslim

## 03 Cas 1 : Ratq et Fatq — quand le Coran ne dit pas Big Bang

Le verset 21:30 est l'argument central du concordisme cosmologique :


أَوَلَمْ يَرَ الَّذِينَ كَفَرُوا أَنَّ السَّمَاوَاتِ وَالْأَرْضَ كَانَتَا رَتْقًا فَفَتَقْنَاهُمَا ۖ وَجَعَلْنَا مِنَ الْمَاءِ كُلَّ شَيْءٍ حَيٍّ


« Les mécréants n'ont-ils pas vu que les cieux et la terre étaient ratqan [soudés], puis Nous les avons fataqnāhumā [séparés] ? Et Nous avons fait de l'eau toute chose vivante. »
Sourate Al-Anbiyāʾ — 21:30
Le courant concordiste interprète *ratq* comme « singularité cosmique » et *fatq* comme « explosion du Big Bang ». Examinons cette prétention.


### La philologie tranche

Ibn Manẓūr (*Lisān al-ʿArab*, tome IX, p. 119) définit *ratq* : « Le ratq est l'opposé du fatq. Rataqa une chose : la souder, la réparer, la joindre. » Le champ sémantique est exclusivement concret et tangible : soudure, adhérence, fermeture. Le terme n'est jamais utilisé dans les dictionnaires classiques pour désigner une abstraction de type « singularité à densité infinie ».


Quant à *fatq*, il désigne une séparation ordonnée et délibérée — radicalement distincte du terme *infijār* (انفجار, explosion, jaillissement), que le Coran possède et utilise ailleurs : le jaillissement des sources de Mūsā (2:60), un jaillissement de source (17:90), la terre qui jaillit lors du Déluge (54:12). **Le fait que le Coran choisisse fatq plutôt que infijār en 21:30 est un indicateur lexical clair : le texte ne décrit pas une explosion.**


### Les six autorités des premières générations

**Ibn ʿAbbās** (m. 68H) : « Le ciel était ratq, il ne pleuvait pas ; la terre était ratq, elle ne produisait pas ; puis Allah a ouvert le ciel par la pluie et ouvert la terre par la végétation. » **Qatāda** (m. 118H) : « Elles formaient une seule chose adhérente, puis Allah les a séparées. » **Mujāhid** (m. 104H) : « Les cieux et la terre étaient soudés en une couche, puis Allah les a fendus et en a fait sept cieux et sept terres. »


Le vocabulaire des Salaf est systématiquement concret : adhérence, soudure, fermeture. Aucun n'emploie de terme relevant de l'abstraction cosmologique. Aucun ne mentionne une singularité, une densité infinie ou une explosion.


### Al-Ṭabarī tranche

« L'avis le plus correct concernant ce verset est celui qui dit : le ciel était ratq et ne pleuvait pas, la terre était ratq et ne produisait pas, puis Allah a ouvert le ciel par la pluie et la terre par la végétation. »
— Al-Ṭabarī (m. 310H), Jāmiʿ al-Bayān, commentaire de 21:30
La lecture privilégiée par le plus grand exégète de l'islam est l'ouverture fonctionnelle — pluie et végétation. Elle est confirmée par le contexte immédiat du verset : « Et Nous avons fait de l'eau toute chose vivante. » Le verset parle de l'eau, de la vie et de la pluie, non de cosmologie abstraite. La sourate al-Ṭāriq (86:11-12) le confirme en parallèle : « Par le ciel qui renvoie [la pluie], et par la terre qui se fend [pour la végétation]. »


## 04 Cas 2 : Daḥā ≠ œuf d'autruche

Ce cas a été traité en détail dans l'article [B1 — La Terre dans le Coran, §04](/la-terre-dans-le-coran/), avec les preuves linguistiques (Lisān al-ʿArab), exégétiques (Ṭabarī, Qurṭubī, Baghawī, Ibn Kathīr) et zoologiques (l'autruche aplanit le sol, elle ne construit pas de nid en forme d'œuf). Résumé : **daḥā = aplanir, étendre**. L'interprétation « œuf d'autruche » n'apparaît qu'au XXᵉ siècle et n'a aucun fondement dans les 13 premiers siècles d'exégèse.


## 05 Cas 3 : Falak ne signifie pas « orbite newtonienne »

Le terme *Falak* (فَلَك) dans les versets 21:33 et 36:40 est traduit par « orbite » dans les éditions contemporaines. L'analyse lexicographique montre que les linguistes des premières générations — al-Kalbi, al-Farraʾ (m. 207H), Abū ʿUbayd al-Harawī (m. 401H) — définissent Falak comme « vague de la mer dans son mouvement circulaire ». Le *jumhūr* des mufassirīn identifie le Falak au **Mawj al-Makfūf** (vague suspendue sous le Trône). Le verbe *yasbahūn* (« ils nagent ») exclut toute structure rigide — on ne nage pas dans le vide spatial.


(Voir l'article [Sept mots, un seul sens](/la-bibliotheque/) dans La Bibliothèque pour l'analyse complète.)


## 06 Le schéma répétitif : cinq versets, même méthode, même erreur


VersetPrétention concordisteSens classique (Salaf)Erreur principale

21:30 (ratq/fatq)Big Bang / singularitéPluie/végétation ou séparation ou 7 couchesAnachronisme + sélectivité
79:30 (daḥā)Forme d'œuf d'autrucheÉtendre, aplanir (basaṭa)Faux dérivé (udḥiyy = nid, pas œuf)
51:47 (mūsiʿūn)Expansion cosmique de HubbleAttribut divin : capacité ou vastitudeDistorsion grammaticale
27:88 (montagnes)Rotation de la TerreDescription eschatologique (contexte 27:87-90)Contexte eschatologique ignoré
55:19-20 (barzakh)Halocline marineSéparation visible entre deux mersPhénomène connu depuis l'Antiquité


Dans chaque cas, la méthode est la même : on sélectionne un verset, on ampute un sens classique de son contexte théologique, on force une correspondance avec une théorie moderne, et on proclame le « miracle ». C'est un schéma systématique, non un accident ponctuel.


## 07 Le raisonnement circulaire

Structure logique du concordisme
**(1)** Présupposition que le Coran contient des miracles scientifiques modernes


**(2)** Recherche sélective de versets ressemblant à des théories modernes


**(3)** Torsion sémantique des termes arabes pour forcer la correspondance


**(4)** Proclamation du « miracle »


**(5)** Conclusion que le Coran contient des miracles scientifiques


La conclusion (5) est identique à la présupposition (1). C'est un **raisonnement circulaire classique** — un biais de confirmation structurel.


Le concordisme inverse la hiérarchie épistémologique islamique : c'est la théorie scientifique qui valide ou invalide la lecture du Coran, non l'inverse. Le Coran devient un texte qui a besoin de la science moderne pour être « prouvé » — alors qu'il se définit lui-même comme *muhaymin*, dominant.


## 08 Le danger théologique : une foi suspendue à un modèle provisoire

Le concordisme crée une **dépendance théologique à un modèle provisoire**. Si le modèle Λ-CDM est significativement révisé — ce qui est historiquement probable au vu de la tension de Hubble à 5σ, des données JWST, de l'instabilité de l'énergie noire (DESI 2024), et des 95% d'entités hypothétiques (voir l'article [La gravité : 70 théories](/le-nexus/)) — la foi d'un croyant ayant accepté le Coran « parce qu'il annonce le Big Bang » risque de s'effondrer avec la théorie.


L'histoire des modèles cosmologiques montre cette instabilité : l'univers statique éternel d'Einstein (années 1920) a été abandonné ; l'état stationnaire de Hoyle (années 1950) a été abandonné ; le Big Bang sans inflation a été révisé ; le Λ-CDM actuel est en crise. Aucun de ces modèles n'a duré plus de quelques décennies. Le Coran, lui, est là depuis 14 siècles.


**Le vrai fondement de la foi coranique :** Le Coran définit son propre statut en 17:9 — il guide vers ce qu'il y a de plus droit. Son miracle réside dans sa guidance spirituelle intemporelle (Hudā), son inimitabilité stylistique (iʿjāz bayānī), son appel au monothéisme pur (Tawḥīd) — non dans une supposée anticipation de modèles scientifiques que les hommes changent tous les cinquante ans.

## 09 Conclusion : le Coran n'a pas besoin du Big Bang

Le concordisme ne défend pas la Révélation — il la diminue. Il ne renforce pas la foi — il la met en position d'infériorité. Il ne propage pas la daʿwa — il travestit la vérité pour complaire à ceux qui ne croient pas en Allah.


L'analyse philologique, exégétique et épistémologique converge : les termes coraniques ont des sens classiques précis, documentés par les Salaf et les dictionnaires arabes, qui n'ont rien à voir avec la cosmologie moderne. Le Big Bang est un modèle provisoire en crise. L'œuf d'autruche est un faux dérivé linguistique. L'orbite newtonienne est une projection anachronique sur un terme qui désigne une vague suspendue.


La Parole d'Allah n'a pas besoin du Big Bang pour être crédible. Elle était vérité avant ces théories et le restera après leur effondrement, comme tant d'autres doctrines humaines l'ont été avant elles.


قُلْ هُوَ ٱللَّهُ أَحَدٌ ۝ ٱللَّهُ ٱلصَّمَدُ ۝ لَمْ يَلِدْ وَلَمْ يُولَدْ ۝ وَلَمْ يَكُن لَّهُۥ كُفُوًا أَحَدٌ


« Dis : Il est Allah, Unique. Allah, le Seul à être imploré. Il n'a pas engendré et n'a pas été engendré. Et nul n'est égal à Lui. »
Sourate Al-Ikhlāṣ — 112:1-4

## Références


 - Ibn Manẓūr, Muḥammad ibn Mukarram (m. 711H). *Lisān al-ʿArab*, tome IX, p. 119.

 - Al-Ṭabarī, Muḥammad ibn Jarīr (m. 310H). *Jāmiʿ al-Bayān*, commentaire de 21:30.

 - Ibn Kathīr, Ismāʿīl ibn ʿUmar (m. 774H). *Tafsīr al-Qurʾān al-ʿAẓīm*.

 - Al-Qurṭubī, Muḥammad ibn Aḥmad (m. 671H). *Al-Jāmiʿ li-Aḥkām al-Qurʾān*.

 - Ibn Taymiyyah, Taqī al-Dīn (m. 728H). *Darʾ Taʿāruḍ al-ʿAql wa al-Naql*, vol. 1, p. 120, 152, 154 ; vol. 7, p. 285.

 - Al-Jawharī, Ismāʿīl ibn Ḥammād (m. 393H). *Al-Ṣiḥāḥ*.

 - Al-Fayrūzābādī, Muḥammad ibn Yaʿqūb (m. 817H). *Al-Qāmūs al-Muḥīṭ*.

 - Al-Zabīdī, Muḥammad Murtaḍā (m. 1205H). *Tāj al-ʿArūs*.

 - Jawharī, Ṭanṭāwī (m. 1940). *Tafsīr al-Jawāhir*.

 - Bucaille, Maurice (1976). *La Bible, le Coran et la Science*. Paris : Seghers.

 - Planck Collaboration (2018). « Planck 2018 results VI ». *A&A*, 641, A6.

 - Riess, A.G. et al. (2022). « Local Value of H₀ ». *ApJ Letters*, 934, L7.

 - DESI Collaboration (2024). « Cosmological Constraints from BAO ». Prépublication arXiv.

 - Ṣaḥīḥ al-Bukhārī, n° 3456 ; Ṣaḥīḥ Muslim, n° 2669.


					

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