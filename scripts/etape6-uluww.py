#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Étape 6 — nouvel article de la Bibliothèque : « Où est Allah ? »

Sources déposées dans content/sources/brut/ :
  · ou-est-Allah.pdf — dossier documentaire : versets, hadiths, paroles des
    Compagnons, consensus rapportés, paroles des quatre imams, avec les
    numéros de hadith et les pages ;
  · uluww_cosmologie.docx — étude théologique reliant la cosmologie à la
    cohérence de l'ʿuluww littéral, avec les textes arabes.

Deux exigences de méthode, tenues dans l'article :

1. La grille de l'ijmāʿ que nous avons appliquée au « consensus sur la
   sphéricité » doit être appliquée ici de la même manière, y compris quand le
   résultat nous arrange. Elle l'est en section 06, et deux des six « consensus »
   rapportés par la source sont écartés comme non recevables au sens technique.

2. L'article établit un conditionnel, pas un fait sur la forme du monde. Il est
   dit en toutes lettres en section 11.

Contrôle : les numéros de hadith du PDF apparaissent deux fois, en chiffres
latins dans le texte français et en chiffres arabes dans la citation. Le PDF
rend ces derniers dans l'ordre inverse. Le script vérifie que chaque numéro
retenu est bien le miroir de sa forme arabe (voir CONCORDANCE).
"""

import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(RACINE, "content", "articles")

SLUG = "ou-est-allah-le-uluww-et-la-forme-du-monde"

# Numéro retenu dans l'article ↔ chaîne de chiffres arabes telle que le PDF la
# rend. Le rendu inverse l'ordre : la concordance se vérifie en retournant.
CONCORDANCE = {
    "7554": "٤٥٥٧",   # al-Bukhārī, le Livre au-dessus du Trône
    "2751": "١٥٧٢",   # Muslim, idem
    "4351": "١٥٣٤",   # al-Bukhārī, « dépositaire de Celui qui est au ciel »
    "1064": "٤٦٠١",   # Muslim, idem
    "1924": "٤٢٩١",   # al-Tirmidhī, les miséricordieux
    "1436": "٦٣٤١",   # Muslim
    "8166": "٦٦١٨",   # al-Nasāʾī, al-Sunan al-Kubrā
    "537":  "٧٣٥",    # Muslim, hadith de la servante
    "1739": "٩٣٧١",   # al-Bukhārī, sermon de l'adieu
    "1218": "٨١٢١",   # Muslim, Jābir
    "7420": "٠٢٤٧",   # al-Bukhārī, Zaynab
    "7108": "٨٠١٧",   # Ibn Ḥibbān, Ibn ʿAbbās à ʿĀʾisha
    "5991": "١٩٩٥",   # al-Bazzār, Abū Bakr
    "79":   "٩٧",     # al-Dārimī, al-Radd ʿalā al-Jahmiyya, ʿUmar
    "83":   "٣٨",     # al-Dārimī, ʿĀʾisha
    "8987": "٧٨٩٨",   # al-Ṭabarānī, al-Muʿjam al-Kabīr, Ibn Masʿūd
    "865":  "٥٦٨",    # al-Bayhaqī, al-Asmāʾ wa-l-Ṣifāt, al-Awzāʿī
}

AR_LATIN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def controle_numeros():
    """Chaque numéro retenu doit être le miroir de sa forme arabe."""
    pb = []
    for latin, arabe in CONCORDANCE.items():
        miroir = arabe.translate(AR_LATIN)[::-1].lstrip("0")
        if miroir != latin:
            pb.append("n° %s : la forme arabe %s se retourne en %s"
                      % (latin, arabe, miroir))
    return pb


BODY = """<p class="tei-lede">Le Prophète ﷺ a demandé à une servante « Où est Allah ? » et a tenu sa réponse pour la preuve de sa foi. Cette question a une réponse dans les textes — et elle suppose que le mot « en haut » désigne quelque chose.</p>

<h2 id="servante"><span class="tei-section-num">01</span>La question qui sert de critère</h2>

<p>Muʿāwiya ibn al-Ḥakam al-Sulamī devait affranchir une esclave croyante pour une expiation. Il l'amène au Prophète ﷺ, qui doit établir si elle est croyante. Il lui pose deux questions. La première est celle-ci.</p>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">أَيْنَ اللهُ؟ قَالَتْ: فِي السَّمَاءِ. قَالَ: مَنْ أَنَا؟ قَالَتْ: أَنْتَ رَسُولُ اللهِ. قَالَ: أَعْتِقْهَا فَإِنَّهَا مُؤْمِنَةٌ</span></p>
<p>« Il dit : “Où est Allah ?” Elle dit : “Au ciel.” Il dit : “Qui suis-je ?” Elle dit : “Tu es le Messager d'Allah.” Il dit : “Affranchis-la, car elle est croyante.” »</p>
<footer>— Ṣaḥīḥ Muslim, n° 537, d'après Muʿāwiya ibn al-Ḥakam al-Sulamī</footer></blockquote>

<p>Ce hadith porte plus qu'une information : il porte un <strong>critère</strong>. Le Prophète ﷺ n'a pas demandé une définition théologique, il a posé une question de lieu — <em>ayna</em>, « où » — et la réponse a suffi à établir la foi de cette femme. C'est le point de départ de tout ce qui suit.</p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Une question qui commence par « où » attend une réponse de lieu ou de direction. Si la bonne réponse avait été « Allah n'est nulle part » ou « Il est partout », la question elle-même n'aurait pas eu de sens — et le Prophète ﷺ n'aurait pas pu s'en servir pour trancher.</p></div>

<h2 id="coran"><span class="tei-section-num">02</span>Le dossier coranique : cinq familles de versets</h2>

<p>Ibn al-Qayyim al-Jawziyya (m. 751 H) a recensé dans son <em>Mukhtaṣar al-Ṣawāʿiq al-Mursala</em> plus d'un millier d'indices coraniques de l'<em>ʿuluww</em>. Ils se rangent en cinq familles, et la première est la plus nette.</p>

<h3 id="istiwa">L'<em>istiwāʾ</em> sur le Trône — sept versets</h3>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">الرَّحْمَٰنُ عَلَى الْعَرْشِ اسْتَوَىٰ</span></p>
<p>« Le Tout Miséricordieux S'est établi sur le Trône. »</p>
<footer>— Sourate Ṭā-Hā — S20 V5</footer></blockquote>

<p>Six autres versets portent la même affirmation : S7 V54, S10 V3, S13 V2, S25 V59, S32 V4 et S57 V4. Al-Qurṭubī en tire une observation de méthode.</p>

<blockquote class="tei-citation">
<p>« Personne parmi les pieux prédécesseurs n'a renié le fait qu'Allah S'est véritablement établi au-dessus de Son Trône, et Allah a mentionné spécifiquement le Trône pour cela, car il est la plus grande de Ses créatures. »</p>
<footer>— al-Qurṭubī (m. 671 H), <em>al-Jāmiʿ li-Aḥkām al-Qurʾān</em>, vol. 9 p. 239</footer></blockquote>

<h3 id="fi-sama">Celui qui est au ciel</h3>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">أَأَمِنتُم مَّن فِي السَّمَاءِ أَن يَخْسِفَ بِكُمُ الْأَرْضَ فَإِذَا هِيَ تَمُورُ</span></p>
<p>« Êtes-vous à l'abri que Celui qui est au ciel vous enfouisse dans la terre — et voici qu'elle tremble ? »</p>
<footer>— Sourate Al-Mulk — S67 V16</footer></blockquote>

<p>Deux exégètes de premier rang lèvent l'ambiguïté du pronom. Ibn ʿAbbās : « Êtes-vous à l'abri du châtiment de Celui qui est dans les cieux — il s'agit d'Allah » (rapporté par Ibn al-Jawzī, <em>Zād al-Masīr</em>, vol. 8 p. 322). Al-Ṭabarī, sur le même verset : « Il s'agit d'Allah » (<em>Jāmiʿ al-Bayān</em>, vol. 23 p. 129).</p>

<h3 id="fawqiyya">La <em>fawqiyya</em> — être au-dessus de Ses créatures</h3>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">وَهُوَ الْقَاهِرُ فَوْقَ عِبَادِهِ</span></p>
<p>« Il est le Dominateur au-dessus de Ses serviteurs. »</p>
<footer>— Sourate Al-Anʿām — S6 V18</footer></blockquote>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">يَخَافُونَ رَبَّهُم مِّن فَوْقِهِمْ وَيَفْعَلُونَ مَا يُؤْمَرُونَ</span></p>
<p>« Ils craignent leur Seigneur au-dessus d'eux, et ils font ce qui leur est ordonné. »</p>
<footer>— Sourate An-Naḥl — S16 V50</footer></blockquote>

<p>Ce second verset porte sur les anges. Sa précision est notable : <em>min fawqihim</em> — « de par au-dessus d'eux ». Les anges sont déjà dans les cieux, et pourtant leur Seigneur leur est décrit comme étant au-dessus.</p>

<h3 id="montee">Ce qui monte vers Lui</h3>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">إِلَيْهِ يَصْعَدُ الْكَلِمُ الطَّيِّبُ</span></p>
<p>« C'est vers Lui que montent les bonnes paroles. »</p>
<footer>— Sourate Fāṭir — S35 V10</footer></blockquote>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">تَعْرُجُ الْمَلَائِكَةُ وَالرُّوحُ إِلَيْهِ فِي يَوْمٍ كَانَ مِقْدَارُهُ خَمْسِينَ أَلْفَ سَنَةٍ</span></p>
<p>« Les anges ainsi que l'Esprit montent vers Lui en un jour dont la durée est de cinquante mille ans. »</p>
<footer>— Sourate Al-Maʿārij — S70 V4</footer></blockquote>

<p>Les verbes sont ceux de l'ascension : <em>yaṣʿadu</em>, <em>taʿruju</em>. Un mouvement « vers Lui » qui est un mouvement de montée présuppose une direction.</p>

<h3 id="pharaon">L'argument de Pharaon</h3>

<p>La cinquième famille est indirecte, et c'est ce qui en fait la force. Pharaon, pour ridiculiser Mūsā, fait bâtir une tour « peut-être atteindrai-je les voies, les voies des cieux, et ainsi j'apercevrai la divinité de Mūsā » (S40 V36-37). Sa moquerie n'a de sens que si Mūsā avait effectivement enseigné que son Seigneur est au-dessus. Ibn ʿAbd al-Barr le relève :</p>

<blockquote class="tei-citation">
<p>« Ce verset montre que Mūsā — sur lui la paix — affirmait que sa divinité était au-dessus du ciel. »</p>
<footer>— Ibn ʿAbd al-Barr (m. 463 H), <em>al-Tamhīd</em>, vol. 7 p. 133</footer></blockquote>

<div class="tei-fait library">
<span class="tei-fait-label">CE QUE LE TEXTE ÉTABLIT</span>
<p>Cinq familles de versets convergent : l'<em>istiwāʾ</em> sur le Trône dans sept passages, « Celui qui est au ciel », la <em>fawqiyya</em> au-dessus des serviteurs et au-dessus des anges eux-mêmes, l'ascension de ce qui monte vers Lui, et la moquerie de Pharaon qui n'a de sens que contre un enseignement de l'élévation. Le vocabulaire employé — <em>ʿalā</em>, <em>fawqa</em>, <em>fī al-samāʾ</em>, <em>yaṣʿadu</em>, <em>taʿruju</em>, <em>ilayhi</em> — est un vocabulaire de direction.</p>
</div>

<h2 id="sunna"><span class="tei-section-num">03</span>La Sunna : par la parole, par l'approbation, par le geste</h2>

<p>La tradition prophétique établit une chose de trois manières : ce que le Prophète ﷺ a dit, ce qu'il a vu et approuvé sans le désavouer (<em>taqrīr</em>), et ce qu'il a fait. Les trois voies sont ici documentées, ce qui est rare.</p>

<h3 id="sunna-parole">Par la parole</h3>

<table class="tei-table">
<thead><tr><th>Rapporteur</th><th>Texte</th><th>Référence</th></tr></thead>
<tbody>
<tr><td>Abū Hurayra</td><td>« Allah a écrit un livre avant de créer la création… et ce livre est auprès de Lui, <strong>au-dessus du Trône</strong>. »</td><td>al-Bukhārī n° 7554 ; Muslim n° 2751</td></tr>
<tr><td>Abū Saʿīd al-Khudrī</td><td>« Ne me faites-vous pas confiance, alors que je suis le dépositaire de <strong>Celui qui est au ciel</strong> ? »</td><td>al-Bukhārī n° 4351 ; Muslim n° 1064</td></tr>
<tr><td>ʿAbd Allāh ibn ʿAmr</td><td>« Faites miséricorde à ceux qui sont sur la terre, <strong>Celui qui est au-dessus des cieux</strong> vous fera miséricorde. »</td><td>al-Tirmidhī n° 1924, authentifié par lui, par Ibn Ḥajar et par al-Albānī</td></tr>
<tr><td>Abū Hurayra</td><td>« …sans que <strong>Celui qui est au ciel</strong> soit en colère contre elle jusqu'à ce qu'il soit satisfait. »</td><td>Muslim n° 1436</td></tr>
<tr><td>Saʿd ibn Abī Waqqāṣ</td><td>« Il a jugé par le jugement dont Allah a jugé <strong>du dessus des sept cieux</strong>. »</td><td>al-Nasāʾī, <em>al-Sunan al-Kubrā</em> n° 8166 ; jugé bon par Ibn Ḥajar, <em>Muwāfaqat al-Khubr al-Khabar</em> vol. 2 p. 439 ; authentifié par al-Albānī, <em>al-Silsila al-Ṣaḥīḥa</em> n° 2745</td></tr>
</tbody>
</table>

<h3 id="sunna-taqrir">Par l'approbation</h3>

<p>C'est le hadith de la servante, cité en ouverture. Sa valeur probante tient à sa forme : le Prophète ﷺ ne fait pas que rapporter une doctrine, il <strong>valide</strong> une réponse donnée par une tierce personne, et il en tire une conséquence juridique — l'affranchissement est valide, donc la femme est croyante.</p>

<h3 id="sunna-acte">Par le geste</h3>

<p>Deux fois, lors du pèlerinage de l'adieu, devant la plus grande assemblée qu'il ait jamais réunie, le Prophète ﷺ prend le ciel à témoin.</p>

<blockquote class="tei-citation">
<p>« Il répéta cela plusieurs fois, puis <strong>leva la tête</strong> et dit : “Ô Allah, ai-je transmis ? Ô Allah, ai-je transmis ?” »</p>
<footer>— Ṣaḥīḥ al-Bukhārī, n° 1739, d'après Ibn ʿAbbās</footer></blockquote>

<blockquote class="tei-citation">
<p>« Le Messager d'Allah ﷺ <strong>leva son index vers le ciel</strong>, puis le pointa vers les gens, en disant : “Ô Allah, témoigne ! Ô Allah, témoigne ! Ô Allah, témoigne !” »</p>
<footer>— Ṣaḥīḥ Muslim, n° 1218, d'après Jābir ibn ʿAbd Allāh</footer></blockquote>

<p>Le geste n'est pas commenté dans le hadith — c'est ce qui lui donne son poids. Personne ne le met en scène ni ne l'explique : il est rapporté parce qu'il a eu lieu.</p>

<h2 id="compagnons"><span class="tei-section-num">04</span>Les Compagnons, dans des situations où l'on ne théorise pas</h2>

<p>L'intérêt des paroles suivantes est qu'aucune n'est un exposé de doctrine. Ce sont des propos tenus dans l'urgence, la douleur ou la conversation ordinaire — là où l'on parle sans construire.</p>

<p><strong>Abū Bakr al-Ṣiddīq</strong>, le jour de la mort du Prophète ﷺ, monte au <em>minbar</em> : « Si Muḥammad est la divinité que vous adorez, alors votre divinité est morte. Et si la divinité que vous adorez est Allah <strong>qui est au-dessus du ciel</strong>, alors votre divinité est vivante et ne meurt pas. » <em>(al-Bazzār, </em>Musnad<em> n° 5991 ; authentifié par al-Dhahabī, </em>Kitāb al-ʿArsh<em> n° 101.)</em></p>

<p><strong>ʿUmar ibn al-Khaṭṭāb</strong>, arrêté en pleine rue par une vieille femme, s'attire une remarque et répond : « Malheur à toi ! Sais-tu qui elle est ? C'est la femme dont Allah a entendu la plainte <strong>du dessus des sept cieux</strong>. » <em>(al-Dārimī, </em>al-Radd ʿalā al-Jahmiyya<em> n° 79 ; authentifié par Ibn al-Qayyim, </em>Mukhtaṣar al-Ṣawāʿiq<em> p. 1071.)</em></p>

<p><strong>ʿĀʾisha</strong>, sur le meurtre de ʿUthmān : « Allah, <strong>du dessus de Son Trône</strong>, a su que je ne souhaitais pas qu'il soit tué. » <em>(al-Dārimī, </em>al-Radd<em> n° 83 ; authentifié par al-Albānī, </em>Mukhtaṣar al-ʿUluww<em> n° 52.)</em></p>

<p><strong>Zaynab</strong>, aux autres épouses du Prophète ﷺ : « Ce sont vos familles qui vous ont mariées ; moi, c'est Allah qui m'a mariée <strong>du haut des sept cieux</strong>. » <em>(al-Bukhārī n° 7420.)</em></p>

<p><strong>Ibn ʿAbbās</strong>, à ʿĀʾisha : « Allah a fait descendre ton innocence <strong>du dessus des sept cieux</strong>. » <em>(Ibn Ḥibbān, </em>Ṣaḥīḥ<em> n° 7108 ; authentifié par al-Albānī n° 7064.)</em></p>

<p><strong>Ibn Masʿūd</strong> : « Le Trône est au-dessus de l'eau, et Allah est au-dessus du Trône. Rien de vos actes ne Lui échappe. » <em>(al-Ṭabarānī, </em>al-Muʿjam al-Kabīr<em> n° 8987 ; authentifié par Ibn Taymiyya, </em>Majmūʿ al-Fatāwā<em> 3/139, et par al-Albānī, </em>Mukhtaṣar al-ʿUluww<em> n° 48.)</em></p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Ces six phrases n'ont pas été prononcées pour défendre une thèse. Abū Bakr console une communauté effondrée, ʿUmar rabroue un impatient, ʿĀʾisha se disculpe, Zaynab taquine ses coépouses. C'est précisément pour cela qu'elles comptent : la manière dont les gens parlent quand ils ne surveillent pas leurs mots dit ce qu'ils tiennent pour évident.</p></div>

<h2 id="consensus"><span class="tei-section-num">05</span>Les consensus rapportés — et la même grille que pour la sphéricité</h2>

<p>Le dossier documentaire dont nous disposons rapporte <strong>six</strong> consensus. Nous avons ailleurs démonté un « consensus sur la sphéricité » en lui appliquant les conditions techniques de l'<em>ijmāʿ</em>. La probité exige d'appliquer ici la même grille, et d'en accepter le résultat quel qu'il soit. <a href="/article/le-consensus-sur-la-sphericite">Les trois conditions sont exposées ici</a> : l'accord doit être celui des <em>mujtahids</em> de la Loi, il doit porter sur un point de religion, et il doit être établi et non supposé.</p>

<table class="tei-table">
<thead><tr><th>Consensus rapporté</th><th>Autorité</th><th>Recevable comme <em>ijmāʿ</em> ?</th></tr></thead>
<tbody>
<tr><td>Des Compagnons, des Tābiʿūn et des gens de science</td><td>Ibn Baṭṭa al-ʿUkbarī (m. 387 H), <em>al-Ibāna al-Kubrā</em>, vol. 3 p. 136</td><td><span class="tei-grade grade-a">oui</span> — juriste et traditionniste, sur un point de religion, avec nomination des générations concernées</td></tr>
<tr><td>Des Tābiʿūn</td><td>al-Awzāʿī (m. 157 H), rapporté par al-Bayhaqī, <em>al-Asmāʾ wa-l-Ṣifāt</em> n° 865</td><td><span class="tei-grade grade-a">oui</span> — témoignage direct d'un contemporain : « nous disions, alors que les Tābiʿūn étaient encore vivants »</td></tr>
<tr><td>Des gens de science</td><td>Isḥāq ibn Rāhawayh (m. 238 H), cité par al-Dhahabī, <em>al-ʿUluww</em> p. 1128</td><td><span class="tei-grade grade-b">oui, mais</span> — affirmation d'un <em>mujtahid</em>, sans documentation des accords individuels</td></tr>
<tr><td>De l'ensemble des musulmans</td><td>Ibn Abī Zayd al-Qayrawānī (m. 386 H), <em>al-Jāmiʿ</em> p. 107-108</td><td><span class="tei-grade grade-b">oui, mais</span> — même réserve : l'accord est affirmé, pas documenté</td></tr>
<tr><td>De tous les prophètes et de tous les Livres révélés</td><td>ʿAbd al-Qādir al-Jīlānī ; Ibn Rushd ; Ibn Taymiyya, <em>Majmūʿ al-Fatāwā</em> 2/188</td><td><span class="tei-grade grade-d">non</span> — ce n'est pas un <em>ijmāʿ</em> au sens technique, qui ne concerne que les <em>mujtahids</em> de cette communauté. C'est une thèse sur le contenu des révélations antérieures, à établir autrement</td></tr>
<tr><td>Des mécréants eux-mêmes</td><td>al-Dārimī (m. 280 H), <em>al-Radd ʿalā al-Marīsī</em> p. 25</td><td><span class="tei-grade grade-d">non</span> — un accord de non-musulmans n'est par définition pas un <em>ijmāʿ</em>. C'est une remarque anthropologique, pas une preuve légale</td></tr>
</tbody>
</table>

<p>Deux des six sont donc écartés. Ce retrait ne coûte presque rien à la thèse, et c'est bien pourquoi il faut le faire : un dossier qui garde ses pièces faibles fait douter des fortes.</p>

<p>Mais la comparaison avec l'autre dossier mérite d'être faite jusqu'au bout, car <strong>l'asymétrie est réelle et elle est décisive</strong>. Le « consensus sur la sphéricité » échouait à la première condition : son auteur d'origine, al-Farghānī, est un <em>astronome</em>, et un accord d'astronomes sur une question de cosmographie n'est pas un <em>ijmāʿ</em> juridique. Ici, les quatre autorités retenues — Ibn Baṭṭa, al-Awzāʿī, Isḥāq ibn Rāhawayh, Ibn Abī Zayd — sont toutes des <em>fuqahāʾ</em> et des traditionnistes, et l'objet est un point de croyance. La condition qui faisait défaut là est satisfaite ici. Ce n'est pas nous qui l'avons voulu : c'est ce que donne la grille quand on la passe des deux côtés.</p>

<h2 id="imams"><span class="tei-section-num">06</span>Les quatre imams</h2>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">قِيلَ لِمَالِكٍ: كَيْفَ اسْتَوَى؟ قَالَ: الاسْتِوَاءُ مَعْلُومٌ وَالْكَيْفُ مَجْهُولٌ وَالإِيمَانُ بِهِ وَاجِبٌ وَالسُّؤَالُ عَنْهُ بِدْعَةٌ</span></p>
<p>« On demanda à Mālik : “Comment S'est-Il établi ?” Il dit : “L'<em>istiwāʾ</em> est connu, la modalité est inconnue, y croire est obligatoire, et questionner sa modalité est une innovation.” »</p>
<footer>— Mālik ibn Anas (m. 179 H), rapporté par al-Bayhaqī, <em>al-Asmāʾ wa-l-Ṣifāt</em>, et par al-Lālakāʾī, <em>Sharḥ Uṣūl Iʿtiqād Ahl al-Sunna</em></footer></blockquote>

<p>Cette réponse est le modèle de la méthode : on affirme le fond, on suspend le jugement sur la modalité, on refuse l'enquête sur ce qui dépasse la portée humaine. Les trois autres imams vont dans le même sens.</p>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">اللهُ فَوْقَ الْعَرْشِ وَعِلْمُهُ فِي كُلِّ مَكَانٍ</span></p>
<p>« Allah est au-dessus du Trône, et Sa science est en tout lieu. »</p>
<footer>— Aḥmad ibn Ḥanbal (m. 241 H), rapporté par al-Lālakāʾī, <em>Sharḥ Uṣūl Iʿtiqād</em> n° 674 ; authentifié par al-Albānī, <em>Mukhtaṣar al-ʿUluww</em> n° 226</footer></blockquote>

<p>Mālik est rapporté dans les mêmes termes : « Allah est au-dessus du ciel et Sa science est en tout endroit » <em>(Abū Dāwūd, </em>Masāʾil al-Imām Aḥmad<em> n° 1699 ; authentifié par al-Albānī, </em>Mukhtaṣar al-ʿUluww<em> n° 130)</em>. Al-Shāfiʿī parle du califat d'Abū Bakr comme d'« une vérité qu'Allah a décrétée <strong>du haut du ciel</strong> » <em>(rapporté par ʿAbd al-Ghanī al-Maqdisī, </em>al-Iqtiṣād fī al-Iʿtiqād<em> p. 100, et par Ibn Qudāma, </em>Ithbāt Ṣifat al-ʿUluww<em> p. 124)</em>.</p>

<p>La position rapportée d'Abū Ḥanīfa est la plus tranchante des quatre, et il faut la citer avec sa réserve. Interrogé sur celui qui dirait « je ne sais pas si mon Seigneur est au-dessus des cieux ou sur la terre », il répond que cet homme a mécru, en s'appuyant sur S20 V5 <em>(al-Fiqh al-Absaṭ p. 49 ; al-Dhahabī, </em>al-ʿUluww<em> n° 332 p. 935)</em>. <strong>Réserve nécessaire :</strong> l'attribution d'<em>al-Fiqh al-Absaṭ</em> à Abū Ḥanīfa, par la voie d'Abū Muṭīʿ al-Balkhī, est discutée parmi les spécialistes du hadith. Nous rapportons la citation telle que notre source la donne, en signalant que sa chaîne est contestée — <span class="tei-grade grade-c">C</span>. Les trois autres imams ne présentent pas cette difficulté.</p>

<h2 id="cosmologie"><span class="tei-section-num">07</span>Pourquoi la forme du monde engage cette question</h2>

<p>Jusqu'ici, rien de ce qui précède ne dépend de la géométrie du monde. C'est maintenant que la question se pose, et voici l'argument, dans sa forme la plus dépouillée.</p>

<p>Pour qu'une élévation soit <strong>réelle</strong> et non seulement figurée, il faut que la direction « en haut » désigne quelque chose d'indépendant de celui qui regarde. Sur une surface étendue surmontée de cieux superposés, c'est le cas : « en haut » pointe dans le même sens pour tout le monde, et la hiérarchie — la terre, puis les cieux, puis le Trône, puis Allah au-dessus du Trône — est univoque.</p>

<p>Sur une sphère, « en haut » se définit localement : c'est la direction opposée au centre. Deux personnes aux antipodes, levant les yeux, pointent dans des directions <strong>opposées</strong>. La direction n'est plus une, elle est une infinité de directions divergentes. L'élévation reste dicible, mais elle cesse d'être univoque au sens où les textes semblent l'entendre.</p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Sur une plaine, si tout le monde tend le doigt vers le haut, tous les doigts sont parallèles. Sur un ballon, si tout le monde tend le doigt vers le haut, les doigts partent dans tous les sens. Ce n'est pas la même situation, et toute la question est de savoir si les textes ont besoin de la première.</p></div>

<h2 id="solutions"><span class="tei-section-num">08</span>Les deux réponses des théologiens qui ont admis la sphère</h2>

<p>Des théologiens musulmans ont accepté la sphéricité, héritée de la cosmographie grecque, tout en voulant maintenir l'<em>ʿuluww</em>. Deux solutions ont été proposées.</p>

<p><strong>Première solution — le haut absolu.</strong> On distingue le <em>fawq muqayyad</em>, haut relatif à l'observateur, et le <em>fawq muṭlaq</em>, haut absolu défini comme « au-delà de l'ensemble du créé, quelle que soit sa géométrie interne ». Allah est au-dessus en ce second sens. Cette réponse préserve l'affirmation ; elle a le défaut de la maintenir sur un fondement qui ne la porte pas naturellement.</p>

<p><strong>Seconde solution — l'enveloppement.</strong> Dans le cosmos ptoléméen des sphères concentriques, on identifie le Trône à la neuvième sphère, et Allah est à l'extérieur de tout. Il entoure la création. Cette réponse est plus lourde de conséquences, et il faut dire pourquoi sans excès.</p>

<p>Ses tenants se défendaient par la <em>mukhālafa</em> : Allah enveloppe sans Se mélanger, Son Essence ne se confond pas avec le créé. L'intention est irréprochable. Mais si la création est spatialement contenue dans la zone qu'occupe le Créateur, la relation devient celle du contenant au contenu — ce qui est <strong>structurellement</strong> analogue au panenthéisme, indépendamment de l'intention. Il faut être précis ici : dire que le schéma est structurellement panenthéiste n'est pas accuser ses partisans de panenthéisme. C'est constater qu'une prémisse importée les conduisait où ils ne voulaient pas aller.</p>

<p>Une racine plus profonde a été identifiée par Ibn Taymiyya dans le <em>Darʾ Taʿāruḍ al-ʿAql wa-l-Naql</em> : l'atomisme des <em>mutakallimūn</em>, où des atomes indivisibles recréés à chaque instant remplissent tout l'espace de façon continue. Dans une telle physique, poser un <em>ḥadd</em> — une frontière créée au-delà de laquelle se trouve le Créateur — revient à « localiser » Allah, ce que leur conception du <em>tanzīh</em> refusait. Le Trône cessait alors d'être une créature-frontière pour devenir un attribut. Le <em>ḥadd</em> disparaissait avec lui.</p>

<h2 id="taxonomie"><span class="tei-section-num">09</span>La gradation des positions — et pourquoi nous ne la transposons pas aux personnes</h2>

<p>Notre source propose une taxonomie graduée des courants. Nous la reproduisons parce qu'elle est plus juste que l'alternative — qui consiste à mettre dans le même sac tous ceux qui admettent la sphère. Mais elle porte sur des <strong>positions</strong>, et il faut le dire avant de la lire, pas après.</p>

<table class="tei-table">
<thead><tr><th>Courant</th><th>Cosmologie</th><th>Le <em>ḥadd</em></th><th>Statut de la position</th></tr></thead>
<tbody>
<tr><td>Jahmiyya, Muʿtazila extrêmes</td><td>Globe aristotélicien intégral, aucun haut absolu</td><td>Nié</td><td>Négation des attributs (<em>taʿṭīl</em>)</td></tr>
<tr><td>Ashʿarites tardifs à cosmologie sphérique</td><td>Trône = neuvième sphère, Allah enveloppe de l'extérieur</td><td>Effacé — le Trône devient attribut</td><td>Déviance grave</td></tr>
<tr><td><em>Mutakallimūn</em> proches de la Sunna</td><td>Globe, <em>ʿuluww</em> maintenu par <em>fawq muṭlaq</em></td><td>Maintenu, mais fragilisé</td><td>Déviance partielle</td></tr>
<tr><td>Atharīs admettant la sphéricité</td><td>Globe, <em>ʿuluww</em> littéral affirmé, modalité inconnue</td><td>Réel, géométrie inexpliquée</td><td>Acceptable, avec une tension non résolue</td></tr>
<tr><td>Atharīs, cosmologie coranique</td><td>Terre étendue, cieux superposés</td><td>Réel — le Trône est une créature-frontière</td><td>Conforme à la Sunna</td></tr>
</tbody>
</table>

<p>Notre source consacre sa dernière partie à une mise en garde que nous faisons entièrement nôtre, et que nous plaçons plus haut qu'elle : <strong>la sévérité d'un jugement sur une position ne se transporte pas sur les personnes qui la tiennent.</strong></p>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">التَّكْفِيرُ حُكْمٌ شَرْعِيٌّ مَرْجِعُهُ إِلَى اللهِ وَرَسُولِهِ، وَلَا يَجُوزُ الْحُكْمُ بِرِدَّةِ مُسْلِمٍ حَتَّى تَقُومَ عَلَيْهِ الْحُجَّةُ</span></p>
<p>« Le <em>takfīr</em> est un jugement légal dont la référence appartient à Allah et à Son Messager. Il n'est pas permis de prononcer l'apostasie d'un musulman tant que la preuve n'a pas été établie contre lui. »</p>
<footer>— Ibn Taymiyya, <em>Majmūʿ al-Fatāwā</em>, vol. 12 p. 180</footer></blockquote>

<p>Les conditions posées par les imams sont cumulatives : que l'argument correct ait été présenté correctement à l'intéressé, qu'il ne puisse pas être excusé par une ignorance involontaire, qu'il n'existe pas d'interprétation admissible qui lui laisse une défense sincère, qu'il n'y ait ni contrainte ni erreur de bonne foi. Un savant qui a reçu de son époque une cosmologie sphérique, et qui affirme l'<em>ʿuluww</em> sans avoir jamais eu à en examiner l'articulation, relève à l'évidence de l'excuse.</p>

<p><strong>Ce site ne prononce aucun jugement sur personne.</strong> Ce n'est ni notre rôle, ni notre compétence, et la source elle-même explique pourquoi c'est un <em>ghuluww</em> — un excès blâmable — que de le faire à la légère. Le critère qu'elle retient n'est d'ailleurs pas celui qu'on attendrait :</p>

<div class="tei-fait library">
<span class="tei-fait-label">CE QUE LE TEXTE ÉTABLIT</span>
<p>La ligne de partage n'est pas « croit-il au globe ou à la terre étendue ? ». Elle est : que sa cosmologie l'amène-t-elle à abandonner l'affirmation de l'<em>ʿuluww</em> réel, la réalité du Trône comme frontière créée, et la primauté du texte révélé sur la théorie humaine ? Un musulman qui tient ces trois principes reste dans la Sunna, quelle que soit la carte du monde qu'il a héritée. La déviance se mesure à l'abandon des fondements, pas à la géométrie.</p>
</div>

<h2 id="portee"><span class="tei-section-num">10</span>Ce que cet article établit — et ce qu'il n'établit pas</h2>

<p>Il faut être clair sur la nature de ce qui précède, parce qu'un raisonnement de ce type se laisse facilement pousser plus loin qu'il ne va.</p>

<p><strong>Ce qui est établi.</strong> Que l'<em>ʿuluww</em> littéral est massivement attesté — cinq familles de versets, la Sunna par ses trois voies, six Compagnons dans des situations non doctrinales, quatre <em>ijmāʿ</em> recevables sur six rapportés, les quatre imams. Que ce corpus emploie un vocabulaire de direction et non d'abstraction. Et que ce vocabulaire s'articule sans effort à une cosmologie de surface étendue et de cieux superposés, alors qu'il demande un appareil conceptuel supplémentaire dans une cosmologie sphérique.</p>

<p><strong>Ce qui n'est pas établi, et que nous ne prétendrons pas.</strong> Que la Terre est plate. L'argument de cet article est un <strong>conditionnel</strong>, pas une mesure : <em>si</em> le monde est sphérique, <em>alors</em> l'affirmation littérale de l'élévation coûte quelque chose — une distinction technique, ou un renoncement. Ce coût est un fait sur la cohérence d'un système, pas une donnée sur la figure de la Terre. Aucune considération théologique ne remplace une mesure, et nous n'en tirerons pas une.</p>

<p><strong>L'objection sérieuse, et ce qu'elle laisse debout.</strong> On peut répondre que sur une sphère, « en haut » se définit parfaitement bien comme « vers l'extérieur, en s'éloignant du centre » — direction que tout observateur détermine sans ambiguïté depuis sa position, et qui converge vers un unique « au-delà de tout le créé ». C'est le <em>fawq muṭlaq</em> des <em>mutakallimūn</em>, et il n'est pas absurde. Ce qu'il ne restitue pas, c'est l'<strong>univocité</strong> : « au-dessus des sept cieux » ne désigne plus une région mais une infinité de directions radiales. Le lecteur jugera si les textes exigent cette univocité. Nous pensons que oui ; nous ne prétendons pas que la question soit close.</p>

<p>La bonne façon de trancher la forme du monde reste la mesure. C'est l'objet de nos <a href="/article/monter-l-experience-des-trois-mires">protocoles expérimentaux</a> et de notre <a href="/article/mesurer-la-courbure-sur-l-eau-cinq-campagnes">campagne sur l'eau</a>, qui ne convoquent aucun verset et n'en ont pas besoin. Les deux ordres restent distincts, et c'est en les gardant distincts qu'on les sert le mieux.</p>

<p>Voir aussi : <a href="/article/la-terre-dans-le-coran">La Terre dans le Coran</a> · <a href="/article/le-consensus-sur-la-sphericite">Le « consensus » sur la sphéricité</a> · <a href="/article/le-concordisme">Le concordisme</a> · <a href="/article/debut-de-la-creation-selon-le-coran-et-la-sunna">Le début de la création</a> · <a href="/article/standards-et-methode">Standards et méthode</a>.</p>

<h2 id="sources"><span class="tei-section-num">11</span>Sources</h2>

<p>Les numéros de hadith proviennent du dossier <em>Où est Allah ?</em>, qui les donne deux fois — en chiffres latins dans le texte français, en chiffres arabes dans la citation. Le PDF rend ces derniers dans l'ordre inverse. Nous avons vérifié les dix-sept numéros retenus en retournant chaque forme arabe : les dix-sept concordent.</p>

<ol>
  <li><em>Où est Allah ?</em>, dossier documentaire, hadithdujour.com, 13 p. — versets, hadiths, paroles des Compagnons, consensus, paroles des quatre imams. Déposé dans notre fonds : <code>content/sources/brut/</code>. <span class="tei-grade grade-b">B</span> — chaque pièce porte sa référence, mais le dossier lui-même n'est pas signé.</li>
  <li><em>ʿUluww d'Allah et cosmologie islamique — terre plate, modèle globe et taxonomie des déviations kalāmiques</em>, étude en français, cinq parties. Déposée dans notre fonds. <span class="tei-grade grade-c">C</span> — étude non signée ; ses textes arabes sont propres et ses références précises, mais elle n'a pas d'auteur identifiable.</li>
  <li>Ṣaḥīḥ Muslim, n° 537 (hadith de la servante), 1064, 1218, 1436, 2751. <span class="tei-grade grade-a">A</span></li>
  <li>Ṣaḥīḥ al-Bukhārī, n° 1739, 4351, 7420, 7554. <span class="tei-grade grade-a">A</span></li>
  <li>al-Tirmidhī, <em>Sunan</em>, n° 1924 ; al-Nasāʾī, <em>al-Sunan al-Kubrā</em>, n° 8166 ; Ibn Ḥibbān, <em>Ṣaḥīḥ</em>, n° 7108. <span class="tei-grade grade-a">A</span></li>
  <li>al-Dārimī, ʿUthmān ibn Saʿīd (m. 280 H). <em>al-Radd ʿalā al-Jahmiyya</em>, n° 79 et 83 ; <em>al-Radd ʿalā al-Marīsī</em>, p. 25. <span class="tei-grade grade-b">B</span></li>
  <li>al-Ṭabarānī. <em>al-Muʿjam al-Kabīr</em>, n° 8987. <span class="tei-grade grade-b">B</span></li>
  <li>al-Bazzār. <em>Musnad</em>, n° 5991 ; al-Dhahabī, <em>Kitāb al-ʿArsh</em>, n° 101. <span class="tei-grade grade-b">B</span></li>
  <li>al-Qurṭubī (m. 671 H). <em>al-Jāmiʿ li-Aḥkām al-Qurʾān</em>, vol. 9 p. 239. <span class="tei-grade grade-b">B</span></li>
  <li>al-Ṭabarī (m. 310 H). <em>Jāmiʿ al-Bayān</em>, vol. 23 p. 129, sur S67 V16. <span class="tei-grade grade-b">B</span></li>
  <li>Ibn al-Jawzī. <em>Zād al-Masīr fī ʿilm al-tafsīr</em>, vol. 8 p. 322. <span class="tei-grade grade-b">B</span></li>
  <li>Ibn ʿAbd al-Barr (m. 463 H). <em>al-Tamhīd</em>, vol. 7 p. 133. <span class="tei-grade grade-b">B</span></li>
  <li>Ibn Baṭṭa al-ʿUkbarī (m. 387 H). <em>al-Ibāna al-Kubrā</em>, vol. 3 p. 136. <span class="tei-grade grade-b">B</span></li>
  <li>Ibn Abī Zayd al-Qayrawānī (m. 386 H). <em>al-Jāmiʿ fī al-sunan wa-l-ādāb</em>, p. 107-108. <span class="tei-grade grade-b">B</span></li>
  <li>al-Bayhaqī. <em>al-Asmāʾ wa-l-Ṣifāt</em>, n° 865 (al-Awzāʿī) ; al-Lālakāʾī, <em>Sharḥ Uṣūl Iʿtiqād Ahl al-Sunna</em>, n° 674 (Aḥmad). <span class="tei-grade grade-b">B</span></li>
  <li>al-Dhahabī. <em>al-ʿUluww lil-ʿAliyy al-Ghaffār</em>, p. 935 et p. 1128 ; al-Albānī, <em>Mukhtaṣar al-ʿUluww</em>, n° 48, 52, 130, 226. <span class="tei-grade grade-b">B</span></li>
  <li>Ibn Taymiyya. <em>Majmūʿ al-Fatāwā</em>, 2/188, 3/139, 5/521, 12/180 ; <em>Darʾ Taʿāruḍ al-ʿAql wa-l-Naql</em>. <span class="tei-grade grade-b">B</span></li>
  <li>Ibn al-Qayyim. <em>Mukhtaṣar al-Ṣawāʿiq al-Mursala</em>, p. 1071. <span class="tei-grade grade-b">B</span></li>
  <li><em>al-Fiqh al-Absaṭ</em>, p. 49, attribué à Abū Ḥanīfa par la voie d'Abū Muṭīʿ al-Balkhī. <span class="tei-grade grade-c">C</span> — attribution discutée, signalée comme telle en section 06.</li>
</ol>
"""

ARTICLE = {
    "title": "Où est Allah ? Le ʿuluww et la forme du monde",
    "description": "Le Prophète ﷺ a fait de la réponse à cette question le critère de la foi d'une servante. Le dossier complet — cinq familles de versets, la Sunna par ses trois voies, six Compagnons, les consensus passés à notre propre grille, les quatre imams — puis la question que la cosmologie pose à l'élévation littérale.",
    "date": "2026-08-06",
    "author": "Terre Etendue",
    "category": "library",
    "tags": ["la-bibliothèque", "ʿaqīda", "ʿuluww", "istiwāʾ", "hadith", "consensus", "kalām"],
    "pinned": False,
    "htmlBody": BODY,
}


def main():
    pb = controle_numeros()
    for p in pb:
        print("  ✗ %s" % p)
    if pb:
        return 1
    print("  ✓ %d numéros de hadith concordent avec leur forme arabe retournée"
          % len(CONCORDANCE))

    # Chaque numéro contrôlé doit effectivement figurer dans l'article.
    manquants = [n for n in CONCORDANCE if ("n° %s" % n) not in BODY]
    if manquants:
        print("  ✗ numéros contrôlés mais absents du texte : %s" % ", ".join(manquants))
        return 1

    chemin = os.path.join(ARTICLES, SLUG + ".json")
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(ARTICLE, f, ensure_ascii=False, indent=2)
        f.write("\n")
    mots = len(re.sub(r"<[^>]+>", " ", BODY).split())
    print("  ✓ %s : %d mots, %d citations, %d encadrés En clair"
          % (SLUG, mots, BODY.count("<blockquote"), BODY.count('class="tei-enclair"')))
    return 0


if __name__ == "__main__":
    sys.exit(main())
