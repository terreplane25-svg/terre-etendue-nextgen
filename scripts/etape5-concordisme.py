#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Étape 5, volet B — enrichissement de content/articles/le-concordisme.json.

Source : content/sources/brut/Réfutation_du_concordisme_cosmologique_et_du_culte
_scientiste_moderne.docx.

Ce que le script ajoute :

1. Section 03 (ratq / fatq, S21 V30) — l'appareil lexical manquait. L'article
   citait le Lisān al-ʿArab de mémoire, sans texte arabe ni les deux autres
   dictionnaires. Ajout des six entrées (Tāj al-ʿArūs, Lisān al-ʿArab, Mukhtār
   al-Ṣiḥāḥ, pour les racines ر-ت-ق et ف-ت-ق), en arabe et en traduction.

2. Section 03 — les trois lectures exégétiques traditionnelles, avec le texte
   arabe des tafsīr et un tableau de synthèse. L'article n'en donnait qu'un
   résumé de trois lignes, ce qui laissait croire à une lecture unique alors que
   la pluralité des lectures est précisément l'argument.

3. Nouvelle section sur S51 V47 et le mot mūsiʿūn — le second pilier du
   discours concordiste, entièrement absent de l'article. Cinq tafsīr en arabe
   et en traduction, plus l'argument intra-coranique décisif : al-Ṭabarī gloss
   mūsiʿūn par le même mot en S2 V236.

4. Réparation de deux liens fautifs : une balise <a> imbriquée dans une autre
   (HTML invalide) et un lien vers /library présenté comme un article.

Renumérotation des sections, des « Cas » et des « FAIT ÉTABLI N° » en fin de
course, pour qu'ils restent continus.
"""

import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN = os.path.join(RACINE, "content", "articles", "le-concordisme.json")


# ═══════════════════════════════════════════════════════════════════════════
# 1. L'appareil lexical des deux racines
# ═══════════════════════════════════════════════════════════════════════════

LEXIQUE = """
<p>Trois dictionnaires font autorité sur l'arabe classique : le <em>Tāj al-ʿArūs</em> de al-Zabīdī, le <em>Lisān al-ʿArab</em> d'Ibn Manẓūr, et le <em>Mukhtār al-Ṣiḥāḥ</em> d'al-Rāzī. Les trois sont antérieurs de plusieurs siècles à toute cosmologie moderne, ce qui est exactement leur intérêt : ils ne peuvent pas avoir été contaminés par ce qu'on cherche à leur faire dire. Voici ce qu'ils portent, en entier.</p>

<h3 id="c-racine-ratq">La racine <span class="tei-arabic">ر ت ق</span> — <em>ratq</em></h3>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">الرَّتْقُ: ضِدُّ الفَتْقِ، وهو إِلْتِئَامُ الشَّيْءِ بَعْضِهِ إِلَى بَعْضٍ بَعْدَ أَنْ كَانَ مَفْتُوقًا.</span></p>
<p>« Le <em>ratq</em> est l'opposé du <em>fatq</em> : c'est le fait pour une chose de se ressouder, de s'unir, de se refermer après avoir été ouverte ou fendue. »</p>
<footer>— <em>Tāj al-ʿArūs</em>, racine ر-ت-ق</footer></blockquote>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">الرَّتْقُ نَقِيضُ الفَتْقِ. رَتَقْتُ الفَتْقَ أَرْتُقُهُ رَتْقًا فَارْتَتَقَ. وَالمَرْأَةُ الرَّتْقَاءُ: الَّتِي الْتَصَقَ فَرْجُهَا.</span></p>
<p>« Le <em>ratq</em> est le contraire du <em>fatq</em>. On dit “j'ai <em>ratq</em> le <em>fatq</em>” pour signifier que j'ai refermé ou ressoudé une ouverture, et cela se dit aussi d'une chose qui se ressoude d'elle-même. Une femme <em>ratqāʾ</em> est celle dont l'ouverture intime est refermée. »</p>
<footer>— <em>Lisān al-ʿArab</em>, racine ر-ت-ق</footer></blockquote>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">الرَّتْقُ : ضِدُّ الفَتْقِ. يُقَالُ رَتَقْتُ الشَّيءَ أَرْتُقُهُ رَتْقًا.</span></p>
<p>« Le <em>ratq</em> est l'opposé du <em>fatq</em>. On dit : j'ai <em>ratq</em> quelque chose, c'est-à-dire je l'ai refermé, ressoudé. »</p>
<footer>— <em>Mukhtār al-Ṣiḥāḥ</em>, racine ر-ت-ق</footer></blockquote>

<p>Le dernier exemple du <em>Lisān</em> est cru, et c'est pourquoi il compte : les lexicographes illustrent <em>ratq</em> par une <strong>soudure de chair</strong>. On est dans le registre du concret et du tangible — deux surfaces qui adhèrent l'une à l'autre. Pas une seule des trois entrées ne fait place à une abstraction du type « état de densité infinie ».</p>

<h3 id="c-racine-fatq">La racine <span class="tei-arabic">ف ت ق</span> — <em>fatq</em></h3>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">الفَتْقُ: شَقُّ المَفْتُوقِ، وَهُوَ نَقِيضُ الرَّتْقِ. يُقَالُ: فَتَقَ الشَّيءَ فَتْقًا، أَيْ شَقَّهُ وَفَصَلَهُ.</span></p>
<p>« Le <em>fatq</em> : c'est fendre une chose, l'ouvrir, la séparer. C'est le contraire du <em>ratq</em>. On dit : <em>fataqtu al-shayʾ fatqan</em>, pour signifier que je l'ai fendu ou séparé. »</p>
<footer>— <em>Tāj al-ʿArūs</em>, racine ف-ت-ق</footer></blockquote>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">الفَتْقُ نَقِيضُ الرَّتْقِ. وَقَدْ فَتَقَهُ فَتْقًا، أَيْ شَقَّهُ. وَمِنْهُ قِيلَ: فَتَقَ السَّمَاءَ بِالْمَطَرِ وَفَتَقَ الأَرْضَ بِالنَّبَاتِ.</span></p>
<p>« Le <em>fatq</em> est l'opposé du <em>ratq</em>. On dit : il l'a <em>fatq</em>, c'est-à-dire il l'a fendu. Et de là on dit : Allah a fendu le ciel par la pluie, et la terre par la végétation. »</p>
<footer>— <em>Lisān al-ʿArab</em>, racine ف-ت-ق</footer></blockquote>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">الفَتْقُ : شَقُّ الشَّيْءِ. وَالْفَتْقُ أَيْضًا الإِبْتِدَاءُ وَالفَتْرَةُ.</span></p>
<p>« Le <em>fatq</em> : fendre une chose. Par extension, cela peut aussi désigner un commencement, une ouverture dans le temps, une période initiale. »</p>
<footer>— <em>Mukhtār al-Ṣiḥāḥ</em>, racine ف-ت-ق</footer></blockquote>

<p>La deuxième entrée est le pivot de tout le dossier, et il faut s'y arrêter. Le <em>Lisān al-ʿArab</em> — écrit au VIII<sup>e</sup> siècle de l'hégire, sans le moindre rapport avec l'exégèse coranique — donne comme <strong>exemple d'usage courant</strong> de la racine : « fendre le ciel par la pluie et la terre par la végétation ». C'est mot pour mot la lecture qu'Ibn ʿAbbās donne du verset et que retient al-Ṭabarī. Le dictionnaire et le <em>tafsīr</em>, deux traditions indépendantes, se rejoignent sur le même sens.</p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Un dictionnaire ne fait pas d'exégèse : il enregistre comment les gens parlaient. Quand celui d'Ibn Manẓūr, pour expliquer le verbe <em>fataqa</em>, prend spontanément l'exemple « fendre le ciel par la pluie », il nous dit que c'était là un emploi ordinaire de la langue — pas une interprétation savante inventée après coup pour un verset.</p></div>
"""


# ═══════════════════════════════════════════════════════════════════════════
# 2. Les trois lectures exégétiques, avec leur texte arabe
# ═══════════════════════════════════════════════════════════════════════════

LECTURES = """
<h3 id="c-trois-lectures">Trois lectures, pas une</h3>

<p>Le point le plus souvent escamoté est celui-ci : les exégètes n'ont pas transmis <em>une</em> lecture de ce verset, mais <strong>trois</strong>, toutes authentiquement rapportées, toutes remontant aux Compagnons ou à leurs élèves directs. Le discours du « miracle scientifique » n'en retient qu'une — la deuxième — et passe les deux autres sous silence. Les voici toutes les trois, en arabe.</p>

<h4>Lecture 1 — le ciel fermé à la pluie, la terre fermée à la végétation</h4>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">وقال آخرون: بل معنى ذلك أن السماوات كانت رتقًا لا تمطر، والأرض كذلك رتقًا لا تنبت، ففتق السماء بالمطر، والأرض بالنبات… عن عكرمة: كانتا رتقًا لا يخرج منهما شيء، ففتق السماء بالمطر، وفتق الأرض بالنبات.</span></p>
<p>« D'autres ont dit : le sens est que les cieux étaient <em>ratq</em> et ne laissaient pas tomber de pluie, et que la terre était <em>ratq</em> et ne faisait pas pousser de végétation ; Allah a donc <em>fatq</em> le ciel par la pluie et la terre par la végétation… Rapporté de ʿIkrima : “Les deux étaient <em>ratq</em>, rien n'en sortait ; puis Allah fendit le ciel pour la pluie et la terre pour la végétation.” »</p>
<footer>— al-Ṭabarī, <em>Jāmiʿ al-Bayān</em>, sur S21 V30</footer></blockquote>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">قال ابن عباس: كانت السماء رتقا لا تمطر، وكانت الأرض رتقا لا تنبت، فلما خلق الله الأرض وأهلها فتق السماء بالمطر، وفتق الأرض بالنبات.</span></p>
<p>« Ibn ʿAbbās a dit : le ciel était <em>ratq</em>, il ne pleuvait pas ; la terre était <em>ratq</em>, elle ne faisait pas pousser. Lorsque Allah eut créé la terre et ses habitants, Il fendit le ciel par la pluie et la terre par la végétation. »</p>
<footer>— Ibn Kathīr, <em>Tafsīr al-Qurʾān al-ʿAẓīm</em>, sur S21 V30</footer></blockquote>

<p>Al-Ṭabarī tient cette lecture pour la plus forte, et il le motive par le texte : la fin du verset dit « et Nous avons fait de l'eau toute chose vivante ». La proposition qui suit immédiatement le <em>fatq</em> parle d'eau et de vie. Il cite en parallèle S86 V11-12 — « par le ciel qui renvoie [la pluie], et par la terre qui se fend » — où le même couple ciel/terre reçoit exactement ce sens.</p>

<h4>Lecture 2 — le ciel et la terre adhérents, séparés par l'air</h4>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">قال ابن عباس والحسن وعطاء والضحاك وقتادة: يعني أنها كانت شيئًا واحدًا ملتصقتين، ففصل الله بينهما بالهواء. وكعب قال: خلق الله السماوات والأرض بعضها على بعض، ثم خلق ريحًا في وسطها ففتحها بها.</span></p>
<p>« Ibn ʿAbbās, al-Ḥasan, ʿAṭāʾ, al-Ḍaḥḥāk et Qatāda ont dit : elles formaient une seule chose, adhérentes, puis Allah les a séparées par l'air. Kaʿb a dit : Allah créa les cieux et la terre les uns sur les autres, puis Il créa un vent au milieu et les ouvrit par lui. »</p>
<footer>— al-Qurṭubī, <em>al-Jāmiʿ li-Aḥkām al-Qurʾān</em>, sur S21 V30</footer></blockquote>

<p>C'est cette lecture, et elle seule, que le discours concordiste retient — parce que « une seule masse » sonne comme « singularité ». Mais lisez ce que les exégètes en disent : la séparation se fait <strong>par l'air</strong> ou <strong>par un vent</strong>, le ciel est <strong>élevé</strong> et la terre <strong>posée</strong>. C'est une mise en ordre verticale de deux réalités déjà créées, pas la naissance de la matière à partir d'un point.</p>

<h4>Lecture 3 — une couche unique déployée en sept cieux et sept terres</h4>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">وقال آخرون: بل معنى ذلك أن السماوات كانت مرتتقة طبقة، ففتقها الله فجعلها سبع سماوات، وكذلك الأرض كانت كذلك مرتتقة، ففتقها فجعلها سبع أرضين.</span></p>
<p>« D'autres ont dit : le sens est que les cieux étaient soudés en une seule couche, puis Allah les a fendus et en a fait sept cieux ; et de même la terre était soudée, Il l'a fendue et en a fait sept terres. »</p>
<footer>— al-Ṭabarī, <em>Jāmiʿ al-Bayān</em>, sur S21 V30, d'après Mujāhid</footer></blockquote>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">وقال إسماعيل بن أبي خالد: سألت أبا صالح الحنفي عن قوله: أَنَّ السَّمَاوَاتِ وَالأرْضَ كَانَتَا رَتْقًا فَفَتَقْنَاهُمَا، قال: كانت السماء واحدة، ففتق منها سبع سماوات، وكانت الأرض واحدة، ففتق منها سبع أرضين.</span></p>
<p>« Ismāʿīl ibn Abī Khālid rapporte : “J'ai interrogé Abū Ṣāliḥ al-Ḥanafī au sujet de cette parole d'Allah. Il répondit : le ciel était une seule entité, Allah en fendit sept cieux ; et la terre était une seule entité, Il en fendit sept terres.” »</p>
<footer>— Ibn Kathīr, <em>Tafsīr al-Qurʾān al-ʿAẓīm</em>, sur S21 V30</footer></blockquote>

<table class="tei-table">
<thead><tr><th>Lecture</th><th>Ce qu'est le <em>ratq</em></th><th>Ce qu'est le <em>fatq</em></th><th>Autorités</th></tr></thead>
<tbody>
<tr><td><strong>1. Pluie et végétation</strong></td><td>Ciel et terre fermés, stériles</td><td>Ouverture pour la pluie et la germination</td><td>Ibn ʿAbbās, ʿIkrima — retenue par al-Ṭabarī</td></tr>
<tr><td><strong>2. Séparation ciel-terre</strong></td><td>Adhérence physique de deux entités</td><td>Séparation par l'air ou par un vent</td><td>Ibn ʿAbbās, al-Ḥasan, ʿAṭāʾ, al-Ḍaḥḥāk, Qatāda, Kaʿb</td></tr>
<tr><td><strong>3. Sept cieux, sept terres</strong></td><td>Une couche unique et compacte</td><td>Déploiement en sept étages</td><td>Mujāhid, Ismāʿīl ibn Abī Khālid, al-Suddī</td></tr>
</tbody>
</table>

<p>Ibn ʿAbbās figure dans <strong>deux</strong> des trois lectures. Ce n'est pas une contradiction : c'est l'indice que ces sens circulaient ensemble dès la première génération, et que les anciens ne les tenaient pas pour exclusifs. Nombre de commentateurs les lisent comme trois <em>fatq</em> successifs — un cosmique, un structurel, un fonctionnel — étagés dans la mise en ordre de la création.</p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Le procédé est simple à repérer, et une fois qu'on l'a vu on le voit partout : on prend un verset que les anciens ont expliqué de trois façons, on garde la seule qui ressemble vaguement à une théorie du XX<sup>e</sup> siècle, on jette les deux autres, et on annonce que « le Coran l'avait dit ». Ce n'est pas de l'exégèse — c'est de la sélection.</p></div>
"""


# ═══════════════════════════════════════════════════════════════════════════
# 3. La section neuve : S51 V47 et le mot mūsiʿūn
# ═══════════════════════════════════════════════════════════════════════════

MUSIUN = """<h2 id="c-musiun"><span class="tei-section-num">04</span>Cas 2 : <em>mūsiʿūn</em> ne signifie pas « en expansion »</h2>

<p>Le second pilier du discours concordiste est un seul mot, à la fin d'un seul verset.</p>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">وَالسَّمَاءَ بَنَيْنَاهَا بِأَيْدٍ وَإِنَّا لَمُوسِعُونَ</span></p>
<p>« Et le ciel, Nous l'avons édifié par Notre puissance, et en vérité Nous sommes <em>la-mūsiʿūn</em>. »</p>
<footer>— Sourate Adh-Dhāriyāt — S51 V47</footer></blockquote>

<p>Les traductions concordistes rendent <em>la-mūsiʿūn</em> par « et Nous l'étendons [le ciel] », « Nous sommes en train de l'élargir » — et lisent l'expansion de l'univers. Trois objections grammaticales se posent avant même d'ouvrir un <em>tafsīr</em>.</p>

<p><strong>Le mot n'a pas de complément.</strong> Le verset ne dit pas « Nous l'élargissons », avec un pronom renvoyant au ciel. Il dit « Nous sommes <em>mūsiʿūn</em> », un participe actif pluriel, sans objet exprimé. Grammaticalement, la phrase attribue une qualité au sujet ; elle ne décrit pas une action exercée sur le ciel.</p>

<p><strong>La racine <span class="tei-arabic">و س ع</span> est celle de l'ampleur, pas du gonflement.</strong> Elle donne <em>saʿa</em> (ampleur, capacité, aisance), <em>wāsiʿ</em> (vaste, qui embrasse tout — un des noms divins), <em>mūsiʿ</em> (celui qui a les moyens). Aucun de ces emplois ne suppose un processus continu.</p>

<p><strong>Le Coran s'explique par le Coran.</strong> Le même participe apparaît en S2 V236, dans un contexte où il ne peut désigner que l'aisance financière :</p>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">عَلَى الْمُوسِعِ قَدَرُهُ وَعَلَى الْمُقْتِرِ قَدَرُهُ</span></p>
<p>« À celui qui est dans l'aisance (<em>al-mūsiʿ</em>) selon ses moyens, et à celui qui est démuni selon ses moyens. »</p>
<footer>— Sourate Al-Baqarah — S2 V236</footer></blockquote>

<p>Ce rapprochement n'est pas de nous : c'est al-Ṭabarī lui-même qui l'établit pour gloser S51 V47. Voici les cinq <em>tafsīr</em>.</p>

<h3 id="c-musiun-tafsir">Ce que disent les cinq exégètes</h3>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">وقوله: وَإِنَّا لَمُوسِعُونَ يقول: لذو سعة بخلقها وخلق ما شئنا أن نخلقه وقدرة عليه. ومنه قوله: عَلَى الْمُوسِعِ قَدَرُهُ وَعَلَى الْمُقْتِرِ قَدَرُهُ، يراد به القوي.</span></p>
<p>« Sa parole “et en vérité Nous sommes <em>la-mūsiʿūn</em>” signifie : Nous sommes détenteurs d'une ample capacité à la créer, et à créer tout ce que Nous voulons, et Nous en avons le pouvoir. De là aussi Sa parole : “À celui qui est dans l'aisance selon ses moyens…” — où le mot désigne celui qui a la force. »</p>
<footer>— al-Ṭabarī, <em>Jāmiʿ al-Bayān</em>, sur S51 V47</footer></blockquote>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">وَإِنَّا لَمُوسِعُونَ أي قد وسعنا أرجاءها ورفعناها بغير عمد حتى استقلت كما هي.</span></p>
<p>« “Et en vérité Nous sommes <em>la-mūsiʿūn</em>” — c'est-à-dire : Nous en avons élargi les étendues et Nous l'avons élevé sans colonnes, jusqu'à ce qu'il se tienne tel qu'il est. »</p>
<footer>— Ibn Kathīr, <em>Tafsīr al-Qurʾān al-ʿAẓīm</em>, sur S51 V47</footer></blockquote>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">قال ابن عباس: لقادرون. وقيل: وإنا لذو سعة، وبخلقها وخلق غيرها لا يضيق علينا شيء نريده. وقيل: وإنا لموسعون الرزق على خلقنا. الحسن: وإنا لمطيقون. وقال الضحاك: أغنيناكم؛ دليله: عَلَى الْمُوسِعِ قَدَرُهُ.</span></p>
<p>« Ibn ʿAbbās a dit : c'est-à-dire Nous sommes capables. On a dit aussi : Nous sommes détenteurs de largesse — créer le ciel et le reste ne Nous restreint en rien. Et encore : Nous sommes ceux qui élargissent la subsistance de Nos créatures. Al-Ḥasan a dit : Nous sommes puissants. Al-Ḍaḥḥāk a dit : Nous vous avons enrichis, preuve en est le verset “À celui qui est dans l'aisance selon ses moyens”. »</p>
<footer>— al-Qurṭubī, <em>al-Jāmiʿ li-Aḥkām al-Qurʾān</em>, sur S51 V47</footer></blockquote>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">وَالسَّمَاء بَنَيْنَاهَا بِأَيْدٍ بقوة. وَإِنَّا لَمُوسِعُونَ قادرون.</span></p>
<p>« “Et le ciel, Nous l'avons bâti <em>bi-aydin</em>” — par la force. “Et en vérité Nous sommes <em>la-mūsiʿūn</em>” — capables, puissants. »</p>
<footer>— al-Maḥallī et al-Suyūṭī, <em>Tafsīr al-Jalālayn</em>, sur S51 V47</footer></blockquote>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">والسماء خلقناها وأتقناها، وجعلناها سقفًا للأرض بقوة وقدرة عظيمة، وإنا لموسعون لأرجائها وأنحائها.</span></p>
<p>« Le ciel, Nous l'avons créé et parfait, Nous en avons fait un toit pour la terre par une grande puissance, et Nous en avons élargi les confins et les régions. »</p>
<footer>— al-Saʿdī, <em>Taysīr al-Karīm al-Raḥmān</em>, sur S51 V47</footer></blockquote>

<table class="tei-table">
<thead><tr><th>Exégète</th><th>Sens donné à <em>mūsiʿūn</em></th><th>Nature</th></tr></thead>
<tbody>
<tr><td>al-Ṭabarī (m. 310 H)</td><td>Détenteurs de puissance et de largesse</td><td>attribut du sujet — <em>qudra</em>, <em>saʿa</em></td></tr>
<tr><td>Ibn Kathīr (m. 774 H)</td><td>Nous en avons élargi les étendues</td><td>élargissement accompli</td></tr>
<tr><td>al-Qurṭubī (m. 671 H)</td><td>Capables, puissants, riches, pourvoyeurs</td><td>attribut du sujet</td></tr>
<tr><td>al-Jalālayn (m. 864 / 911 H)</td><td><em>Qādirūn</em> — capables</td><td>attribut du sujet</td></tr>
<tr><td>al-Saʿdī (m. 1376 H)</td><td>Nous en avons élargi les confins</td><td>élargissement accompli</td></tr>
</tbody>
</table>

<p>Le résultat est net, et il faut le dire tel quel : <strong>trois des cinq</strong> lisent un attribut de la puissance divine, sans le moindre élargissement spatial ; <strong>deux</strong> — Ibn Kathīr et al-Saʿdī — lisent bien un élargissement du ciel. Le concordisme n'est donc pas absurde au point d'inventer un sens : il en existe un qui va dans sa direction.</p>

<p>Mais ces deux-là ne lui donnent pas ce qu'il lui faut, et pour une raison de temps grammatical. Ibn Kathīr écrit <em>qad wassaʿnā</em> — « Nous <strong>avons</strong> élargi » — et enchaîne sur « jusqu'à ce qu'il se tienne tel qu'il est ». Al-Saʿdī place l'élargissement dans la même série que « Nous l'avons créé et parfait ». Chez l'un comme chez l'autre, l'élargissement est un <strong>acte de la création, achevé</strong>, dont l'état actuel est le résultat. Or l'expansion cosmologique est, par définition, un processus <strong>en cours</strong>, dont le taux se mesure aujourd'hui. C'est précisément ce qu'aucun des cinq n'affirme.</p>

<div class="tei-fait headquarters">
<span class="tei-fait-label">FAIT ÉTABLI N°4</span>
<p>Sur les cinq <em>tafsīr</em> de référence, trois glosent <em>mūsiʿūn</em> par la puissance ou la largesse divine, sans aucune notion spatiale, et al-Ṭabarī l'appuie par le même mot en S2 V236, où il désigne l'aisance matérielle. Les deux qui lisent un élargissement du ciel le donnent à l'accompli, comme un acte de la création achevé — jamais comme un processus en cours. Aucun des cinq ne décrit une expansion continue.</p>
</div>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Le mot est le même que dans « selon les moyens de celui qui est aisé ». En français, « le Seigneur est large » ne veut pas dire qu'Il grossit — cela veut dire qu'Il donne sans compter. Et même les deux commentateurs qui y voient un ciel élargi le disent au passé composé : Il l'a élargi, une fois, en le créant. Pas : Il continue de l'élargir en ce moment.</p></div>

<p>Un mot enfin sur l'usage de cet argument. Nous l'avons vu employé dans l'autre sens — « le Coran réfute l'expansion » — et c'est le même défaut de méthode, à l'envers. Le verset ne dit rien de l'expansion, ni pour, ni contre. Il dit que le ciel a été bâti avec puissance par Celui qui n'est jamais à court de moyens. La question de savoir si l'univers s'étend se règle par l'observation, et nous la traitons ailleurs, sans le Coran.</p>

"""


# ═══════════════════════════════════════════════════════════════════════════
# 4. Réparations
# ═══════════════════════════════════════════════════════════════════════════

REPARATIONS = [
    # <a> imbriqué dans <a> — HTML invalide, le second lien avale le premier
    ('<a href="/article/la-terre-dans-le-coran">B1 — La <a href="/article/la-terre-dans-le-coran">Terre dans le Coran</a>, §04</a>',
     '<a href="/article/la-terre-dans-le-coran">La Terre dans le Coran</a>, section 04'),
    # « Sept mots, un seul sens » n'est pas un article : le lien menait à la
    # page de catégorie sous un titre qui n'existe pas.
    ('(Voir l\'article <a href="/library">Sept mots, un seul sens</a> dans La Bibliothèque pour l\'analyse complète.)',
     '<p>L\'analyse des sept termes coraniques et de leur champ sémantique est '
     'développée dans <a href="/article/la-terre-dans-le-coran">La Terre dans le '
     'Coran</a>, section 02.</p>'),
]


def transformer(html):
    pb = []
    n_bq_avant = html.count("<blockquote")

    for avant, apres in REPARATIONS:
        if avant not in html:
            pb.append("réparation introuvable : %r" % avant[:52])
        else:
            html = html.replace(avant, apres, 1)

    # 1. lexique — après le paragraphe d'annonce de « La philologie tranche »
    ancre = '<h3 id="c-philo">La philologie tranche</h3>\n'
    if ancre not in html:
        pb.append("ancre philologie introuvable")
    else:
        html = html.replace(ancre, ancre + LEXIQUE, 1)

    # 2. les trois lectures — juste avant l'encadré « En clair » de la section
    ancre = '<div class="tei-enclair">\n<span class="tei-enclair-label">En clair</span>\n<p>Le mot <em>ratq</em> veut dire'
    if ancre not in html:
        pb.append("ancre encadré ratq introuvable")
    else:
        html = html.replace(ancre, LECTURES + "\n" + ancre, 1)

    # 3. la section mūsiʿūn — avant le cas daḥā
    ancre = '<h2 id="c-daha">'
    if ancre not in html:
        pb.append("ancre section daḥā introuvable")
    else:
        html = html.replace(ancre, MUSIUN + ancre, 1)

    # 4. renumérotations continues
    c = [0]

    def renum_section(m):
        c[0] += 1
        return '<span class="tei-section-num">%02d</span>' % c[0]

    html = re.sub(r'<span class="tei-section-num">\d+</span>', renum_section, html)

    k = [0]

    def renum_cas(m):
        k[0] += 1
        return "Cas %d" % k[0]

    html = re.sub(r"Cas \d+", renum_cas, html)

    n = [0]

    def renum_fait(m):
        n[0] += 1
        return "FAIT ÉTABLI N°%d" % n[0]

    html = re.sub(r"FAIT ÉTABLI N°\d+", renum_fait, html)

    # ── contrôles ──
    attendu = n_bq_avant + 6 + 5 + 7   # lexique, lectures, mūsiʿūn
    if html.count("<blockquote") != attendu:
        pb.append("citations : %d après, %d attendues" % (html.count("<blockquote"), attendu))
    if re.search(r"<a[^>]*>[^<]*<a", html):
        pb.append("balise <a> imbriquée subsistante")
    for b in ("p", "blockquote", "div", "ol", "ul", "table", "thead", "tbody",
              "tr", "td", "th", "h2", "h3", "h4", "span", "footer", "a"):
        o = len(re.findall(r"<%s[\s>]" % b, html))
        f = len(re.findall(r"</%s>" % b, html))
        if o != f:
            pb.append("<%s> : %d ouvrants, %d fermants" % (b, o, f))
    nums = re.findall(r'<span class="tei-section-num">(\d+)</span>', html)
    if nums != ["%02d" % (i + 1) for i in range(len(nums))]:
        pb.append("numérotation discontinue : %s" % nums)
    for bq in re.findall(r"<blockquote.*?</blockquote>", html, re.S):
        if "<footer>" not in bq:
            pb.append("citation sans attribution : %s" % bq[:60])
    return html, pb


def main():
    with open(CHEMIN, encoding="utf-8") as f:
        data = json.load(f)
    html, pb = transformer(data["htmlBody"])
    for p in pb:
        print("  ✗ %s" % p)
    if pb:
        return 1
    data["htmlBody"] = html
    data["updated"] = "2026-08-05"
    if not data.get("tags"):
        data["tags"] = ["le-centre-de-recherche", "concordisme", "iʿjāz", "exégèse",
                        "big-bang", "philologie"]
    with open(CHEMIN, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    mots = len(re.sub(r"<[^>]+>", " ", html).split())
    print("  ✓ le-concordisme : %d mots, %d citations, %d encadrés En clair"
          % (mots, html.count("<blockquote"), html.count('class="tei-enclair"')))
    return 0


if __name__ == "__main__":
    sys.exit(main())
