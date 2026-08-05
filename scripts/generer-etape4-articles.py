#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Étape 4 — deux articles de la Bibliothèque écrits depuis les sources déposées
dans content/sources/brut/ :

  A. Erreur Fausse Attribution Mobilité Terre Ibn Taymiyyah.pdf
     -> la-mobilite-de-la-terre-attribuee-a-ibn-taymiyyah

  B. Traduction_Risala_Nafi_Kuriyyat_Ard.docx
     -> un-traite-ottoman-contre-la-sphericite-1314h

Le script est idempotent : il réécrit les deux JSON à partir de zéro.
Les vérifications numériques de l'article B sont recalculées ici même et
comparées aux valeurs écrites dans le HTML (voir CONTROLES en fin de fichier).
"""

import json
import math
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(RACINE, "content", "articles")

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTES DE CONTRÔLE (article B)
# ═══════════════════════════════════════════════════════════════════════════

FARSAKH = 5.6           # km — farsakh ottoman tardif, celui de l'auteur
DHIRA = 0.462           # m  — coudée noire
C_REEL = 40075.0        # km — circonférence équatoriale
DEG_REEL = 111.2        # km par degré de latitude (valeur moyenne)
LAT_ISTANBUL = 41.0     # degrés
D_SOLEIL = 149.6e6      # km


def fleche(d, circonference):
    """Flèche (sagitta) d'un arc de longueur d sur un cercle de circonférence C.
    f = d²/(8R) avec R = C/(2π), soit f = π·d²/(4C)."""
    return math.pi * d * d / (4.0 * circonference)


# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE A — la fausse attribution à Ibn Taymiyyah
# ═══════════════════════════════════════════════════════════════════════════

A_SLUG = "la-mobilite-de-la-terre-attribuee-a-ibn-taymiyyah"

A_BODY = """<p class="tei-lede">L'édition imprimée du <em>Majmūʿ al-Fatāwā</em> fait dire à Ibn al-Munādī que la Terre est sphérique « avec tous ses mouvements ». Trois témoins antérieurs de trois siècles portent « dans toutes ses parties ». Un mot, et un avis cosmologique tout entier.</p>

<h2 id="edition"><span class="tei-section-num">01</span>Ce que porte l'édition imprimée</h2>

<p>On lit régulièrement, dans les débats contemporains, qu'Ibn Taymiyyah (m. 728 H) aurait soutenu la mobilité de la Terre. L'unique appui de cette lecture est une phrase de son recueil de fatwas, où il rapporte un consensus attribué à Ibn al-Munādī — Abū al-Ḥusayn Aḥmad ibn Jaʿfar ibn al-Munādī, traditionniste et lecteur du Coran de Bagdad, mort en 336 H.</p>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">وكذلك أجمعوا على أن الأرض بجميع حركاتها من البر والبحر مثل الكرة</span></p>
<p>« Et de même ils ont été unanimes que la Terre, avec tous <strong>ses mouvements</strong>, de la terre ferme et de la mer, est semblable à une sphère. »</p>
<footer>— Ibn Taymiyyah, <em>Majmūʿ al-Fatāwā</em>, éd. Ibn Qāsim, vol. 6, p. 586-587</footer></blockquote>

<p>Le mot en cause est <strong><span class="tei-arabic">بجميع حركاتها</span></strong> (<em>bi-jamīʿ ḥarakātihā</em>, « avec tous ses mouvements »). C'est de ce seul mot que la thèse dépend : retirez-le, et il ne reste dans tout le corpus taymiyyien aucune trace d'un avis sur la mobilité de la Terre.</p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Toute la démonstration adverse repose sur un mot dans un livre imprimé au XX<sup>e</sup> siècle. Un mot n'est pas rien — mais quand un mot porte à lui seul une thèse, la première chose à faire est de vérifier ce mot dans les manuscrits et chez les auteurs antérieurs. C'est exactement ce que fait cet article.</p></div>

<h2 id="tashif"><span class="tei-section-num">02</span>Le <em>taṣḥīf</em> : une catégorie classique, pas une échappatoire</h2>

<p>Avant de proposer qu'un mot imprimé soit fautif, il faut rappeler que la tradition islamique dispose d'un nom, d'une définition et d'une bibliographie pour ce phénomène. Le <em><span class="tei-arabic">تصحيف</span></em> (<em>taṣḥīf</em>) désigne le fait d'écrire ou de lire un mot avec un sens incorrect en raison d'une ressemblance graphique. Ce n'est pas une commodité polémique : c'est une discipline auxiliaire du hadith, avec ses ouvrages spécialisés.</p>

<ul>
  <li>Abū Aḥmad al-ʿAskarī (m. 382 H), <em>Taṣḥīfāt al-Muḥaddithīn</em> — un recueil entier consacré aux mots que les transmetteurs ont mal lus.</li>
  <li>Ibn al-Dabbāgh, <em>al-Taṣḥīf wa-l-Taḥrīf</em> — la distinction entre l'erreur de points diacritiques (<em>taṣḥīf</em>) et l'altération du squelette consonantique (<em>taḥrīf</em>).</li>
</ul>

<p>La discipline existe parce que l'écriture arabe le permet : le squelette consonantique (<em>rasm</em>) est ambigu tant que les points ne sont pas posés, et les points sont précisément ce que les copistes omettent, déplacent ou ajoutent. <span class="tei-arabic">ج</span>, <span class="tei-arabic">ح</span> et <span class="tei-arabic">خ</span> partagent un même tracé ; <span class="tei-arabic">ر</span> et <span class="tei-arabic">ز</span> aussi.</p>

<p>Honnêtement : entre <span class="tei-arabic">أجزائها</span> et <span class="tei-arabic">حركاتها</span>, la ressemblance n'est <strong>que partielle</strong>. Les deux mots partagent le tracé initial <span class="tei-arabic">ج/ح</span> suivi d'un <span class="tei-arabic">ر/ز</span>, un <em>alif</em> médian et la finale <span class="tei-arabic">ـها</span> ; ils diffèrent par l'<em>alif</em> initial et par la lettre centrale. L'argument paléographique est donc un <strong>appui</strong>, non une preuve. Ce qui fait la démonstration, c'est la section suivante.</p>

<h2 id="temoins"><span class="tei-section-num">03</span>Trois témoins antérieurs, tous d'accord contre l'imprimé</h2>

<p>Le texte que rapporte Ibn Taymiyyah n'est pas de lui : il circule depuis le III<sup>e</sup> siècle de l'hégire. On peut donc le confronter à ses états antérieurs. Trois auteurs le donnent avant lui, et les trois portent <span class="tei-arabic">أجزائها</span> — « ses parties ».</p>

<table class="tei-table tei-savants">
<thead><tr><th>Témoin</th><th>Mort</th><th>Ouvrage</th><th>Leçon</th><th>Grade</th></tr></thead>
<tbody>
<tr><td>Aḥmad ibn Muḥammad <strong>ibn Kathīr al-Farghānī</strong></td><td>~247 H</td><td><em>Jawāmiʿ ʿilm al-nujūm</em></td><td><span class="tei-arabic">بجميع أجزائها</span><br><small>« dans toutes ses parties »</small></td><td><span class="tei-grade grade-d">D</span></td></tr>
<tr><td>Aḥmad ibn ʿUmar <strong>ibn Rustah</strong> al-Iṣfahānī</td><td>~300 H</td><td><em>al-Aʿlāq al-Nafīsa</em></td><td><span class="tei-arabic">بجميع أجزائها</span><br><small>reprend al-Farghānī</small></td><td><span class="tei-grade grade-d">D</span></td></tr>
<tr><td><strong>al-Masʿūdī</strong></td><td>346 H</td><td><em>Murūj al-Dhahab</em></td><td><span class="tei-arabic">بجميع أجزائها</span><br><small>« de la terre ferme et de la mer »</small></td><td><span class="tei-grade grade-d">D</span></td></tr>
<tr><td>Ibn Taymiyyah <small>(rapportant Ibn al-Munādī)</small></td><td>728 H</td><td><em>Majmūʿ al-Fatāwā</em>, éd. imprimée</td><td><span class="tei-arabic">بجميع حركاتها</span><br><small>« avec tous ses mouvements »</small></td><td><span class="tei-grade grade-b">B</span></td></tr>
</tbody>
</table>

<p><strong>Le grade D des trois témoins est un aveu, pas une coquetterie.</strong> La source dont nous disposons — un traité en arabe traduit en français, déposé dans notre fonds documentaire — cite les trois auteurs <em>sans pagination ni édition</em>. Nous rapportons donc la collation telle qu'elle nous est transmise, et nous la marquons comme non vérifiée à la source. Les éditions à consulter sont identifiées en fin d'article : le jour où la pagination est établie, ces trois lignes passeront en A ou B, et cette section sera modifiée en conséquence.</p>

<p>Une précision de nom, parce qu'elle prête à confusion et que nous nous y sommes nous-mêmes presque laissé prendre : le <strong>« ibn Kathīr »</strong> d'al-Farghānī est son propre <em>nasab</em> — le nom de son grand-père. Il n'a rien à voir avec Ismāʿīl ibn Kathīr (m. 774 H), l'exégète du <em>Tafsīr</em>. Al-Farghānī est un astronome de Ferghana, actif à Bagdad au milieu du III<sup>e</sup> siècle de l'hégire, auteur d'un abrégé de l'<em>Almageste</em>.</p>

<div class="tei-fait library">
<span class="tei-fait-label">CE QUE LE TEXTE ÉTABLIT</span>
<p>Trois auteurs antérieurs de trois à cinq siècles à Ibn Taymiyyah donnent la même formule avec <span class="tei-arabic">أجزائها</span> (« ses parties »). L'unique état du texte portant <span class="tei-arabic">حركاتها</span> (« ses mouvements ») est une édition imprimée moderne. En critique textuelle, la leçon isolée et tardive n'emporte pas contre trois témoins indépendants et anciens.</p>
</div>

<h2 id="avis-inexistant"><span class="tei-section-num">04</span>Un avis qui n'avait pas cours</h2>

<p>La leçon <span class="tei-arabic">حركاتها</span> suppose qu'Ibn al-Munādī, au IV<sup>e</sup> siècle de l'hégire, ait rapporté un <em>consensus</em> sur la mobilité de la Terre. Or, à cette époque, l'avis dominant — chez les <em>ahl al-hayʾa</em> (les spécialistes de la cosmographie) comme chez les juristes — était celui de son <strong>immobilité</strong>. Le géocentrisme ptoléméen, qui est le cadre même dans lequel al-Farghānī écrit, tient la Terre pour fixe au centre des sphères.</p>

<p>La difficulté n'est donc pas qu'un auteur du IV<sup>e</sup> siècle ait pu soutenir la mobilité — quelques-uns l'ont discutée. Elle est qu'il l'aurait rapportée comme un <strong>consensus établi et incontesté</strong>, ce qui est chronologiquement intenable : c'est faire de l'avis le plus marginal de son temps l'avis unanime de son temps.</p>

<h2 id="silence"><span class="tei-section-num">05</span>Le silence d'Ibn Taymiyyah, et celui de ses disciples</h2>

<p>Deuxième anomalie, et elle est massive. Ibn Taymiyyah a laissé une œuvre considérable : fatwas, épîtres, traités de théologie et de logique. La mobilité de la Terre n'y est <strong>jamais</strong> mentionnée, jamais discutée, jamais défendue. Aucun de ses élèves ne la lui attribue — pas même Ibn al-Qayyim (m. 751 H), qui l'a suivi pendant quinze ans et qui rapporte ses positions jusque dans le détail.</p>

<p>Un auteur qui aurait tenu pour acquis un consensus sur la mobilité de la Terre aurait eu mille occasions d'y revenir, ne serait-ce que pour l'articuler aux versets qui décrivent la Terre. Le silence total, du maître et de toute son école, est un argument de poids : il indique que la phrase, telle qu'elle est imprimée, ne portait pas ce sens pour ceux qui l'ont lue avant nous.</p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Si quelqu'un vous soutient que votre grand-père pensait telle chose, et que rien dans ses carnets, ses lettres, ni dans les souvenirs de ceux qui vivaient avec lui n'en garde trace — la thèse ne tient qu'à la ligne unique sur laquelle elle est fondée. Vérifier cette ligne devient la seule chose à faire.</p></div>

<h2 id="pluriel"><span class="tei-section-num">06</span>Le pluriel impossible : « tous ses mouvements »</h2>

<p>La formule imprimée ne dit pas « son mouvement » au singulier. Elle dit <em>bi-jamīʿ ḥarakātihā</em> : « avec <strong>tous ses mouvements</strong> », au pluriel, et avec le quantificateur <em>jamīʿ</em> qui les embrasse tous.</p>

<p>Attribuer à la Terre plusieurs mouvements distincts est une idée <strong>moderne</strong>. Rotation diurne, révolution annuelle, précession des équinoxes rapportée à la Terre plutôt qu'au ciel, mouvement du Soleil dans la Galaxie : cette pluralité est le produit de l'astronomie post-copernicienne. Elle n'est pas concevable pour un auteur du IV<sup>e</sup> siècle de l'hégire, dont le système ne connaît que des mouvements <em>célestes</em>, et une Terre fixe.</p>

<p>Autrement dit : la leçon <span class="tei-arabic">حركاتها</span> ne rend pas seulement l'auteur hétérodoxe pour son temps ; elle le rend <strong>anachronique</strong>. C'est le signe habituel d'une contamination du texte par la langue de ses éditeurs.</p>

<h2 id="sens"><span class="tei-section-num">07</span>Le test de sens : « parties » ou « mouvements » ?</h2>

<p>Reste la lecture la plus simple, et peut-être la plus décisive : mettre les deux leçons dans la phrase complète et regarder laquelle veut dire quelque chose. Le contexte, ici, est la <strong>forme</strong> de la Terre — la phrase précédente porte sur la forme du ciel.</p>

<table class="tei-table tei-collation">
<thead><tr><th>Leçon imprimée — <span class="tei-arabic">حركاتها</span></th><th>Leçon des trois témoins — <span class="tei-arabic">أجزائها</span></th></tr></thead>
<tbody>
<tr>
<td>« la Terre, avec <strong>tous ses mouvements</strong>, de la terre ferme et de la mer, est semblable à une sphère »</td>
<td>« la Terre, dans <strong>toutes ses parties</strong>, de la terre ferme et de la mer, est semblable à une sphère »</td>
</tr>
<tr>
<td>Qu'est-ce qu'un mouvement <em>semblable à une sphère</em> ? Un mouvement peut être circulaire, pas sphérique.</td>
<td>Une partie de surface peut être dite sphérique : c'est un énoncé de forme, cohérent avec le sujet.</td>
</tr>
<tr>
<td>Quel rapport entre « la terre ferme et la mer » et des <em>mouvements</em> de la Terre ? La précision devient inintelligible.</td>
<td>La Terre a des parties émergées — régions, pays, continents — et des parties immergées — mers et océans. La précision est naturelle.</td>
</tr>
<tr>
<td>Le membre de phrase précédent porte sur la forme du ciel. Passer sans transition à la cinématique terrestre rompt le fil.</td>
<td>Le parallélisme est exact : forme du ciel, puis forme de la Terre. Une même phrase, un même objet.</td>
</tr>
</tbody>
</table>

<p>La leçon <span class="tei-arabic">أجزائها</span> n'est pas seulement mieux attestée. Elle est la seule des deux qui produise une phrase intelligible.</p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>« La Terre, avec tous ses mouvements de la terre ferme et de la mer, est comme une boule » : essayez de vous représenter la chose. Des mouvements en forme de boule, dont certains seraient marins ? La phrase ne veut rien dire. Remplacez « mouvements » par « parties » et tout se remet en place : la Terre a des parties sur la terre ferme et des parties sous la mer, et l'ensemble a la forme dont on parle. Quand une leçon rend une phrase absurde et l'autre la rend limpide, ce n'est pas une question d'opinion.</p></div>

<h2 id="hikaya"><span class="tei-section-num">08</span>Et même si la leçon imprimée était exacte : rapporter n'est pas adopter</h2>

<p>Supposons, pour la discussion, que l'édition ait raison et que les trois témoins soient tous fautifs. La thèse adverse ne serait toujours pas établie, parce qu'elle confond deux actes que la tradition distingue soigneusement.</p>

<ul>
  <li><strong><em>Ḥikāya</em></strong> (<span class="tei-arabic">حكاية</span>) — rapporter le propos d'un autre. C'est ce que fait ici Ibn Taymiyyah : il cite Ibn al-Munādī pour discuter d'un consensus allégué.</li>
  <li><strong><em>Iqrār</em></strong> (<span class="tei-arabic">إقرار</span>) — adopter ce propos pour son compte, par une formule d'assentiment.</li>
</ul>

<p>Il n'y a dans le passage aucune formule d'assentiment. Le contexte est celui d'un examen : Ibn Taymiyyah rapporte ce qu'on présente comme un accord des savants. Faire de la citation l'avis du citateur revient à attribuer à un juge la position de la partie qu'il entend. Le même raisonnement vaut, symétriquement, pour ceux qui tirent de ce passage un <em>ijmāʿ</em> sur la sphéricité — c'est l'objet d'un <a href="/article/le-consensus-sur-la-sphericite">article distinct</a>.</p>

<h2 id="limites"><span class="tei-section-num">09</span>Ce qui reste à vérifier, et comment</h2>

<p>Cet article est une pièce de critique textuelle. Il doit donc dire précisément où s'arrête ce qu'il établit.</p>

<p><strong>Ce qui est établi :</strong> la phrase imprimée est incohérente avec son propre contexte (section 07), anachronique dans sa formulation au pluriel (section 06), et sans écho dans une œuvre entière ni dans son école (section 05). Ces trois constats ne dépendent d'aucune collation manuscrite : ils se lisent sur le texte imprimé lui-même.</p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Il y a deux façons de conclure ce genre d'enquête. La première : « nous avons prouvé que le mot est faux ». La seconde : « nous avons montré que le mot ne tient pas debout dans sa phrase, et nous avons trois témoins contraires que nous n'avons pas encore pu ouvrir nous-mêmes ». La seconde est la vraie, et c'est celle que nous écrivons.</p></div>

<p><strong>Ce qui n'est pas encore vérifié à la source :</strong> les trois témoins antérieurs. Notre collation les reprend d'un traité de seconde main, sans pagination. Voici exactement ce qu'il faut consulter pour clore le dossier.</p>

<table class="tei-table">
<thead><tr><th>À vérifier</th><th>Édition à consulter</th><th>Ce qu'on y cherche</th></tr></thead>
<tbody>
<tr><td>Ibn Rustah, <em>al-Aʿlāq al-Nafīsa</em></td><td>éd. M. J. de Goeje, <em>Bibliotheca Geographorum Arabicorum</em> VII, Leyde, 1892</td><td>le passage sur la forme de la Terre, et la leçon du mot</td></tr>
<tr><td>al-Farghānī, <em>Jawāmiʿ ʿilm al-nujūm</em></td><td>éd. J. Golius, Amsterdam, 1669 ; éditions arabes modernes</td><td>la formule dont Ibn Rustah dit qu'il la reprend</td></tr>
<tr><td>al-Masʿūdī, <em>Murūj al-Dhahab</em></td><td>éd. Ch. Pellat, Beyrouth ; éd. Barbier de Meynard</td><td>chapitre cosmographique d'ouverture</td></tr>
<tr><td>Ibn Taymiyyah, <em>Majmūʿ al-Fatāwā</em></td><td>manuscrits antérieurs à l'édition Ibn Qāsim</td><td>la leçon manuscrite du mot, si un témoin subsiste</td></tr>
</tbody>
</table>

<p>Nous publions ce dossier ouvert plutôt que fermé, avec ses grades et ses trous. Si un lecteur dispose de l'une de ces éditions, la vérification d'une seule ligne suffirait à faire progresser l'article — <a href="/article/standards-et-methode">signaler une correction</a>.</p>

<p>Voir aussi : <a href="/article/le-consensus-sur-la-sphericite">Le « consensus » sur la sphéricité</a> · <a href="/article/pres-de-cent-savants-de-lislam">Près de cent savants de l'Islam</a> · <a href="/article/un-traite-ottoman-contre-la-sphericite-1314h">Un traité ottoman contre la sphéricité (1314 H)</a> · <a href="/article/standards-et-methode">Standards et méthode</a>.</p>

<h2 id="sources"><span class="tei-section-num">10</span>Sources</h2>
<ol>
  <li>Ibn Taymiyyah (m. 728 H). <em>Majmūʿ al-Fatāwā</em>, éd. ʿAbd al-Raḥmān ibn Qāsim, vol. 6, p. 586-587. <span class="tei-grade grade-b">B</span> — volume et pages, édition consultée en reproduction.</li>
  <li><em>Éclaircissement et explication de l'erreur de la fausse attribution de la mobilité de la Terre à Ibn Taymiyyah</em>, traité anonyme traduit en français, 2 p. Déposé dans notre fonds : <code>content/sources/brut/</code>. <span class="tei-grade grade-c">C</span> — document paginé, mais ses propres références ne le sont pas.</li>
  <li>Aḥmad ibn Muḥammad ibn Kathīr al-Farghānī (m. ~247 H). <em>Jawāmiʿ ʿilm al-nujūm wa-uṣūl al-ḥarakāt al-samāwiyya</em>. <span class="tei-grade grade-d">D</span> — cité de seconde main, sans pagination.</li>
  <li>Aḥmad ibn ʿUmar ibn Rustah al-Iṣfahānī (m. ~300 H). <em>Kitāb al-Aʿlāq al-Nafīsa</em>. <span class="tei-grade grade-d">D</span> — cité de seconde main, sans pagination.</li>
  <li>al-Masʿūdī (m. 346 H). <em>Murūj al-Dhahab wa-maʿādin al-jawhar</em>, chapitre cosmographique. <span class="tei-grade grade-d">D</span> — cité de seconde main, sans pagination.</li>
  <li>Abū Aḥmad al-Ḥasan al-ʿAskarī (m. 382 H). <em>Taṣḥīfāt al-Muḥaddithīn</em>. <span class="tei-grade grade-d">D</span> — cité comme attestation de la discipline, sans localisation.</li>
  <li>Ibn al-Dabbāgh. <em>al-Taṣḥīf wa-l-Taḥrīf</em>. <span class="tei-grade grade-d">D</span> — idem.</li>
  <li>Ibn al-Munādī (m. 336 H). <em>al-Malāḥim</em>, p. 337 — pour l'avis propre de l'auteur auquel le consensus est attribué. <span class="tei-grade grade-b">B</span></li>
</ol>
"""

A_JSON = {
    "title": "La mobilité de la Terre attribuée à Ibn Taymiyyah : anatomie d'un taṣḥīf",
    "description": "Le Majmūʿ al-Fatāwā imprimé porte « avec tous ses mouvements » (ḥarakātihā). Trois témoins antérieurs de trois à cinq siècles portent « dans toutes ses parties » (ajzāʾihā). Reconstitution d'une erreur de copie, et de ce qu'on en a tiré.",
    "date": "2026-08-05",
    "author": "Terre Etendue",
    "category": "library",
    "tags": ["la-bibliothèque", "ibn-taymiyyah", "critique-textuelle", "taṣḥīf", "consensus", "manuscrits"],
    "pinned": False,
    "htmlBody": A_BODY,
}


# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE B — la Risāla fī nafyi kuriyyat al-arḍ
# ═══════════════════════════════════════════════════════════════════════════

B_SLUG = "un-traite-ottoman-contre-la-sphericite-1314h"

B_BODY = """<p class="tei-lede">Un manuscrit de 39 feuillets, copié à Médine en 1314 H, catalogué au rayon Géographie de la Bibliothèque du Roi Abd al-Aziz : un traité ottoman qui réfute la sphéricité de la Terre. Nous en publions la fiche, le plan, et la vérification de tous ses calculs — y compris ceux qui sont faux.</p>

<h2 id="fiche"><span class="tei-section-num">01</span>La fiche du manuscrit</h2>

<p>Ce document n'est ni une compilation ni une paraphrase : c'est un objet physique, avec une cote, dans une bibliothèque publique. C'est ce qui en fait, dans notre fonds documentaire, la seule <strong>source primaire</strong> du lot.</p>

<div class="tei-data">
<small>Fiche de catalogage — Bibliothèque du Roi Abd al-Aziz, Médine</small>
<p>Titre arabe : <em>Risāla fī nafyi kuriyyat al-arḍ</em> (<span class="tei-arabic">رسالة في نفي كروية الأرض</span>)<br>
Titre ottoman : <em>Arzın Küreviyyetini Nefyeden Risale</em><br>
Auteur : İsmail Ferid, <em>müderris</em> à Médine<br>
Copiste : inconnu — Date de copie : 1314 H (ca. 1896-1897)<br>
Collection al-Mahmūdiyya — Cote 3.1.13 — Classification 900<br>
39 feuillets — 16 lignes par page — 21 × 18 cm<br>
Écriture : naskhī-taʿlīq ottomane — Langue : turc ottoman, citations coraniques en arabe<br>
Colophon : « Achevé — louange à Allah — le 18 Rabīʿ al-Awwal 1314 »</p>
</div>

<p>La note manuscrite du frontispice le décrit comme un « <em>kitāb turkī fī nafyi kuriyyat al-arḍ mutaʿalliq bi-ʿilm al-hayʾa</em> » — un livre en turc sur la réfutation de la sphéricité de la Terre, relevant de la science de la cosmographie. Il est rangé sous « Mektebe-i Umūmiyye — al-Jughrāfā » : bibliothèque générale, section Géographie. Le classement n'est pas un détail : l'institution le range parmi les ouvrages de science, non parmi les curiosités.</p>

<h2 id="auteur"><span class="tei-section-num">02</span>L'auteur, le lieu, la date</h2>

<p>İsmail Ferid est identifié sur la fiche comme <em>müderris</em> — enseignant titulaire d'une <em>madrasa</em> — à Médine. Nous n'en savons pas davantage : le traité est, à notre connaissance, son seul texte conservé, et nous n'avons trouvé aucune notice biographique le concernant. C'est une limite qu'il faut poser d'emblée, car elle empêche d'évaluer sa formation astronomique.</p>

<p>La date compte plus que l'homme. <strong>1314 H, soit 1896-1897</strong> : nous sommes dix-sept ans après la fondation de la <em>Zetetic Society</em> de Samuel Rowbotham en Angleterre, et à trois décennies de la fin de l'Empire ottoman. Le traité est donc contemporain du mouvement zététique anglais — <a href="/article/le-mouvement-zetetique-150-ans-de-resistance">dont nous avons retracé l'histoire ailleurs</a> — mais il n'en cite rien et ne s'y rattache pas. Son outillage est intégralement islamique et ottoman : <em>ʿilm al-hayʾa</em>, unités en farsakhs et coudées, versets et hadiths.</p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Ce manuscrit règle une question de fait, indépendamment de qui a raison sur la forme de la Terre : à la fin du XIX<sup>e</sup> siècle, un enseignant de Médine écrit un traité entier contre la sphéricité, le dépose dans une bibliothèque, et l'institution le catalogue comme ouvrage de géographie. La thèse ne descend donc pas d'un mouvement anglais, et elle n'était pas invisible dans le monde musulman de son temps.</p></div>

<h2 id="unites"><span class="tei-section-num">03</span>Les unités : lire le traité sans se tromper d'un facteur cinq</h2>

<p>Tout le traité raisonne en unités islamiques classiques. Les convertir n'est pas un confort de lecture : sans conversion, on ne peut pas savoir si un calcul est juste. Voici les valeurs, telles que le traducteur les établit et telles que nous les employons dans toutes les vérifications qui suivent.</p>

<table class="tei-table">
<thead><tr><th>Unité</th><th>Valeur retenue</th><th>Remarque</th></tr></thead>
<tbody>
<tr><td><em>Farsakh</em> (<span class="tei-arabic">فرسخ</span>) — parasange</td><td><strong>5,6 km</strong></td><td>farsakh ottoman tardif, celui de l'auteur. Le farsakh canonique persan-arabe vaut 5,544 km.</td></tr>
<tr><td><em>Dhirāʿ</em> (<span class="tei-arabic">ذراع</span>) — coudée</td><td>0,462 m</td><td>coudée noire. Le traité pose 1 farsakh = 12 000 <em>dhirāʿ</em>.</td></tr>
<tr><td>Mille arabe (<span class="tei-arabic">ميل</span>)</td><td>1 848 m</td><td>soit 4 000 <em>dhirāʿ</em>. À ne pas confondre avec le mille romain (1 480 m).</td></tr>
<tr><td><em>Sahm al-qaws</em> (<span class="tei-arabic">سهم القوس</span>)</td><td>—</td><td>« flèche de l'arc » : la sagitta, ou versine. La grandeur centrale de tout le débat sur la courbure.</td></tr>
<tr><td><em>Shākūl</em> (<span class="tei-arabic">شاقول</span>)</td><td>—</td><td>fil à plomb.</td></tr>
<tr><td>Farsakh carré</td><td>31,2 km²</td><td>employé occasionnellement.</td></tr>
</tbody>
</table>

<p>Une incohérence interne apparaît dès le glossaire, et il faut la relever tout de suite : <strong>1 farsakh = 12 000 dhirāʿ = 5 544 m</strong> avec la coudée noire, ce qui correspond au farsakh canonique et non aux 5,6 km employés par l'auteur. L'écart est de 1 %, négligeable pour la suite, mais il annonce ce que la section 05 va montrer à plus grande échelle : les valeurs numériques du traité ne sont pas mutuellement compatibles.</p>

<h2 id="plan"><span class="tei-section-num">04</span>Le plan : quatre arguments adverses, vingt et un paragraphes</h2>

<p>L'auteur pose lui-même la structure de son livre. Il commence par énumérer, sans les caricaturer, les <strong>quatre arguments</strong> qui ont selon lui conduit les savants à admettre la sphéricité, puis il les réfute l'un après l'autre. C'est une méthode honnête, et elle mérite d'être notée : le traité expose la thèse adverse avant de l'attaquer.</p>

<ol>
  <li><strong>L'ombre circulaire des éclipses de Lune</strong> — l'ombre de la Terre est ronde quelle que soit la direction d'observation ; seule une sphère projette une ombre ronde dans toutes les directions.</li>
  <li><strong>L'horizon marin</strong> — depuis un navire, l'horizon forme un cercle parfait dans toutes les directions.</li>
  <li><strong>La variation de hauteur des étoiles selon la latitude</strong> — l'Étoile polaire monte vers le nord, descend vers le sud.</li>
  <li><strong>La circumnavigation</strong> — on part vers l'ouest, on revient par l'est, sans jamais rencontrer de bord.</li>
</ol>

<p>Suivent vingt et un paragraphes numérotés, seize diagrammes géométriques dessinés à la main, et un chapitre final de preuves scripturaires. L'auteur revendique explicitement de s'appuyer sur « les données astronomiques et l'observation directe » (<em>mushāhadāt</em>) — non sur le seul texte.</p>

<h2 id="portent"><span class="tei-section-num">05</span>Les objections qui portent</h2>

<p>Trois de ses objections sont d'authentiques objections de méthode, et elles n'ont pas vieilli.</p>

<h3>La circularité des mesures astronomiques</h3>

<blockquote class="tei-citation">
<p>« Les astronomes mesurent la distance au Soleil par la méthode de la parallaxe : ils observent le Soleil depuis deux points éloignés sur la Terre, mesurent la légère différence d'angle, puis calculent la distance par triangulation. Mais cette méthode suppose déjà que la Terre est sphérique pour calculer la distance réelle entre les deux points d'observation. On retombe donc inévitablement dans un raisonnement circulaire. »</p>
<footer>— İsmail Ferid, <em>Risāla fī nafyi kuriyyat al-arḍ</em>, § 6</footer></blockquote>

<p>L'objection est nommée dans le texte par son nom technique arabe : <em>muṣādara ʿalā al-maṭlūb</em> (<span class="tei-arabic">مصادرة على المطلوب</span>) — pétition de principe. Elle est réelle. La base d'une triangulation parallactique est en effet calculée dans un référentiel géodésique, lequel présuppose la figure de la Terre. C'est précisément le problème que notre <a href="/article/par-rapport-a-quoi-mesure-t-on-une-altitude">article sur les altitudes</a> examine dans le détail, et c'est la raison pour laquelle notre <a href="/article/monter-l-experience-des-trois-mires">protocole des trois mires</a> est construit pour ne dépendre d'aucune valeur de rayon terrestre supposée.</p>

<h3>L'horizon n'est pas la limite de la surface</h3>

<p>L'auteur distingue l'<em>ufq al-ẓāhir</em> — l'horizon apparent — de la limite réelle de la surface, et attribue le premier à la portée de la vision et à l'état de l'atmosphère. C'est exactement la distinction qu'il faut faire, et elle reste au centre du débat : la question empirique n'est pas de savoir si un horizon apparaît, mais si la <strong>manière</strong> dont les objets s'y effacent suit une loi géométrique ou une loi de contraste.</p>

<h3>Le gnomon sur une surface plane</h3>

<p>Sa réfutation de l'argument du gnomon est correcte dans sa forme : si le Soleil est petit et proche, les longueurs d'ombre varient d'un lieu à l'autre sur une surface plane, exactement comme sous une lampe posée au-dessus d'une table. C'est la version ottomane de ce que nous avons appelé ailleurs le <a href="/article/le-mythe-deratosthene">problème d'Ératosthène</a> : la mesure des ombres est compatible avec deux géométries, et ne tranche donc pas à elle seule.</p>

<div class="tei-fait library">
<span class="tei-fait-label">CE QUE LE TEXTE ÉTABLIT</span>
<p>Le traité formule, en 1314 H et dans un vocabulaire islamique, l'objection de circularité qui est aujourd'hui au cœur du débat métrologique : une mesure calculée dans un référentiel qui présuppose la figure de la Terre ne peut pas servir à établir cette figure. L'objection est indépendante de la valeur des chiffres de l'auteur — et ceux-ci, comme la section suivante le montre, sont faux.</p>
</div>

<h2 id="chiffres"><span class="tei-section-num">06</span>Les chiffres : vérification poste par poste</h2>

<p>Notre charte impose de vérifier tout ce que nous publions, y compris ce qui nous arrange. Nous avons donc recalculé chaque valeur numérique du traité. <strong>La plupart sont fausses, et certaines sont incompatibles entre elles.</strong></p>

<table class="tei-table">
<thead><tr><th>Grandeur</th><th>Valeur du traité</th><th>Recalcul / valeur d'aujourd'hui</th><th>Écart</th></tr></thead>
<tbody>
<tr><td>Circonférence de la Terre (§ 4)</td><td>8 000 farsakhs ≈ 44 800 km</td><td>40 075 km</td><td>+12 %</td></tr>
<tr><td>Circonférence de la Terre (§ 9)</td><td>78 540 farsakhs ≈ 439 800 km</td><td>40 075 km</td><td>× 11</td></tr>
<tr><td>Flèche sur 100 farsakhs (§ 4)</td><td>100² ÷ 8 000 = 1,25 farsakh ≈ 7,0 km</td><td>Avec sa propre circonférence : π·100² ÷ (4 × 8 000) = 0,98 farsakh ≈ 5,5 km</td><td>+27 % <small>(formule <em>d</em>²/C au lieu de π<em>d</em>²/4C)</small></td></tr>
<tr><td>La même flèche, en coudées (§ 4)</td><td>8 000 dhirāʿ ≈ 3 700 m</td><td>1,25 farsakh = 15 000 dhirāʿ ≈ 6 930 m</td><td>× 1,9 <small>(incohérent avec sa propre ligne précédente)</small></td></tr>
<tr><td>Distance Istanbul – équateur (§ 8)</td><td>2 600 farsakhs ≈ 14 560 km</td><td>41,0° × 111,2 km ≈ 4 560 km</td><td>× 3,2</td></tr>
<tr><td>Hauteur du Soleil (§ 8)</td><td>800 farsakhs ≈ 4 480 km</td><td>2 600 × tan 60° = 4 503 farsakhs ≈ 25 200 km</td><td>le résultat ne suit pas de la formule annoncée</td></tr>
<tr><td>Distance Terre – Soleil <small>(telle qu'il l'attribue aux astronomes)</small></td><td>20 000 farsakhs ≈ 112 000 km</td><td>149 600 000 km</td><td>÷ 1 340</td></tr>
<tr><td>Flèche réelle sur 560 km</td><td>—</td><td>π × 560² ÷ (4 × 40 075) ≈ 6,15 km</td><td>supérieure à celle qu'il calcule</td></tr>
</tbody>
</table>

<p>Trois remarques s'imposent, et aucune n'est à notre avantage.</p>

<p><strong>Premièrement, sa formule de flèche est fausse d'un facteur 4/π.</strong> Il calcule <em>d</em>²/C là où la géométrie donne π<em>d</em>²/(4C), soit <em>d</em>²/(8R). Il surestime donc la courbure de 27 %. C'est le même piège de facteur que nous avons documenté dans <a href="/article/leau-ne-ment-pas">L'eau ne ment pas</a> : sur ce genre de calcul, l'erreur ne vient jamais du principe, toujours du coefficient.</p>

<p><strong>Deuxièmement, sa conclusion se retourne contre lui.</strong> Il affirme qu'une courbure de 7 km sur 560 km serait « parfaitement détectable par les ingénieurs et les navigateurs, ce qui n'est nullement le cas ». Mais la flèche réelle sur 560 km est de <strong>6,15 km</strong> — c'est-à-dire du même ordre que la valeur qu'il déclare indétectable. Son argument, s'il tenait, condamnerait sa propre estimation autant que celle de ses adversaires. En réalité, la courbure est mesurée par les géodésiens depuis le XVIII<sup>e</sup> siècle, précisément par des chaînes de nivellement — ce qui est aussi la raison d'être de notre campagne côtière.</p>

<p><strong>Troisièmement, le § 8 est arithmétiquement incohérent.</strong> Avec une distance de 2 600 farsakhs et un angle de 60°, la hauteur du Soleil serait de 4 503 farsakhs, non de 800. La valeur de 800 farsakhs correspondrait à un angle de <strong>17°</strong>. Soit l'angle, soit la distance, soit le résultat a été mal transmis — nous ne pouvons pas trancher sans le folio original.</p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Nous publions un document qui va dans le sens de nos hypothèses, et nous montrons que ses chiffres sont faux. Ce n'est pas de la coquetterie : un argument ne vaut que par ce qui le soutient. Un calcul erroné qui aboutit à la bonne conclusion reste un calcul erroné, et le citer sans le vérifier serait exactement le reproche que nous adressons au camp adverse.</p></div>

<h2 id="degre"><span class="tei-section-num">07</span>Quatre valeurs incompatibles pour le degré de latitude</h2>

<p>Le point le plus révélateur n'est pas qu'une valeur soit fausse, mais que le traité en contienne <strong>quatre différentes</strong>, sans jamais les confronter. Le degré de latitude — la longueur d'arc correspondant à un degré — est la grandeur pivot de toute la géodésie. Voici ce que le manuscrit en dit, selon l'endroit où on le lit.</p>

<table class="tei-table">
<thead><tr><th>Où, dans le traité</th><th>Farsakhs / degré</th><th>km / degré</th><th>Écart au réel</th></tr></thead>
<tbody>
<tr><td>Glossaire de l'auteur</td><td>26 à 27</td><td>146 à 151</td><td>+31 à +36 %</td></tr>
<tr><td>Impliqué par la circonférence du § 4 (8 000 farsakhs)</td><td>22,2</td><td>124,4</td><td>+12 %</td></tr>
<tr><td>Argument adverse rapporté au § 3 (100 farsakhs)</td><td>100</td><td>560</td><td>× 5,0</td></tr>
<tr><td>Impliqué par la circonférence du § 9 (78 540 farsakhs)</td><td>218</td><td>1 222</td><td>× 11</td></tr>
<tr><td><strong>Valeur d'aujourd'hui</strong></td><td><strong>19,9</strong></td><td><strong>111,2</strong></td><td>—</td></tr>
</tbody>
</table>

<p>La valeur la moins fausse est celle qu'il utilise le moins : les 22,2 farsakhs par degré impliqués par sa circonférence de 8 000 farsakhs, à 12 % du réel. La plus fausse est celle du § 9. Et une observation, que nous donnons comme <strong>hypothèse et non comme conclusion</strong> : 78 540 est exactement 10⁵ × π/4. Associé au « 21 600 degrés de circonférence » qui figure sur le même folio — et 21 600 est le nombre de minutes d'arc dans un cercle — cela ressemble à une valeur de table lue dans la mauvaise colonne. Nous n'irons pas plus loin sans le folio.</p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Le degré de latitude, c'est la distance qu'il faut parcourir vers le nord pour que l'Étoile polaire monte d'un degré. C'est la mesure de base : tout le reste — circonférence, courbure, distances — en découle. Un traité qui en donne quatre valeurs différentes, écartées d'un facteur onze entre la plus petite et la plus grande, ne peut pas conclure quoi que ce soit de quantitatif. C'est le cas ici.</p></div>

<h2 id="retournent"><span class="tei-section-num">08</span>Deux arguments qui se retournent contre l'auteur</h2>

<h3>Le télescope qui « fait réapparaître » la coque</h3>

<p>L'auteur tient cet argument pour le plus décisif de tout son traité : si une lunette suffisamment puissante fait réapparaître la coque d'un navire prétendument disparue derrière la courbure, c'est que rien n'était géométriquement caché.</p>

<p>Le raisonnement est valide dans sa forme — mais il ne conclut que si l'on vérifie l'antécédent. Un grossissement restitue en effet du détail perdu au contraste atmosphérique, et il existe des cas où l'on récupère ainsi une coque que l'œil nu ne distinguait plus. Il existe aussi des cas où <strong>aucun grossissement ne la restitue</strong>, la ligne d'eau restant tranchée quelle que soit l'ouverture de l'instrument. Les deux situations existent, et l'observation unique ne les départage pas.</p>

<p>C'est exactement pourquoi nous avons construit un protocole qui ne repose <strong>pas</strong> sur la disparition des objets, mais sur l'<a href="/article/monter-l-experience-des-trois-mires">exposant de la loi hauteur-distance</a>. La réfraction change l'amplitude de l'effet ; elle ne change pas la puissance de <em>d</em>. Un traité de 1314 H ne pouvait pas formuler ce test — c'est la limite historique du document, pas un reproche.</p>

<h3>Les deux fils à plomb</h3>

<p>L'auteur écrit que deux fils à plomb séparés de plusieurs farsakhs « demeurent parfaitement parallèles », et il en fait sa preuve directe de la platitude. Ici, l'objection se retourne complètement.</p>

<p>Deux verticales séparées d'un degré de latitude — soit 111 km — divergent, sur une Terre sphérique, d'exactement <strong>un degré</strong>, ce qui représente 17,5 mm par mètre de longueur de fil. Cette divergence n'est pas seulement mesurable : <strong>c'est l'opération que l'on appelle « mesurer une latitude »</strong>. Relever la hauteur de l'Étoile polaire au-dessus de l'horizon, c'est mesurer l'angle entre la verticale locale et une direction fixe. Tout point astronomique en navigation est cette mesure, répétée depuis des siècles, sur tous les océans.</p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>L'auteur cherche une divergence entre deux fils à plomb éloignés, ne la trouve pas avec les instruments de maçon dont il dispose, et conclut qu'elle n'existe pas. Mais cette divergence a un autre nom, bien plus ancien : la différence de latitude. Chaque fois qu'un navigateur relève la hauteur d'une étoile pour savoir où il se trouve, il mesure l'angle entre sa verticale et une direction fixe du ciel. L'instrument existait, il était à bord de tous les navires de son époque — ce n'était simplement pas un fil à plomb.</p></div>

<p>L'auteur ne peut donc pas à la fois accepter que la hauteur de l'Étoile polaire varie avec la latitude (ce qu'il concède au § 3, en l'expliquant par la perspective) et soutenir que les verticales ne divergent pas. Sa propre section 13 en dépend : il y affirme que tous les observateurs d'une même latitude voient l'Étoile polaire à la même hauteur — ce qui définit un angle attaché à la latitude, c'est-à-dire à la verticale locale.</p>

<h2 id="zahir"><span class="tei-section-num">09</span>Le recours au <em>ẓāhir</em> des versets</h2>

<p>Le traité se clôt sur les preuves scripturaires, que l'auteur tient pour les plus décisives. Il en cite trois.</p>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">وَالْأَرْضَ فَرَشْنَاهَا فَنِعْمَ الْمَاهِدُونَ</span></p>
<p>« Quant à la Terre, Nous l'avons étendue — et quels excellents étendeurs Nous sommes ! »</p>
<footer>— Sourate Adh-Dhāriyāt — S51 V48</footer></blockquote>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">وَاللَّهُ جَعَلَ لَكُمُ الْأَرْضَ بِسَاطًا</span></p>
<p>« Et Allah vous a fait de la Terre un tapis étendu. »</p>
<footer>— Sourate Nūḥ — S71 V19</footer></blockquote>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">وَإِلَى الْأَرْضِ كَيْفَ سُطِحَتْ</span></p>
<p>« Et vers la Terre, comment elle a été aplanie ? »</p>
<footer>— Sourate Al-Ghāshiyah — S88 V20</footer></blockquote>

<p>Son commentaire porte sur le sens premier des trois racines : <em>farasha</em> (étendre comme un tapis), <em>bisāṭ</em> (tapis, surface étendue), <em>suṭiḥat</em> (fut aplanie). Il anticipe l'objection concordiste — « une sphère est localement plane » — et y répond que les versets décrivent la Terre <em>dans son ensemble</em>, non des portions de sa surface.</p>

<p>Sur le plan des principes, il énonce enfin la règle qui gouverne tout son traité :</p>

<blockquote class="tei-citation">
<p>« Nous ne nions pas que certains savants musulmans aient soutenu la sphéricité. Mais nous affirmons que leur opinion est erronée : elle est fondée sur des preuves insuffisantes, et elle contredit le sens littéral des textes coraniques et prophétiques. »</p>
<footer>— İsmail Ferid, <em>Risāla fī nafyi kuriyyat al-arḍ</em>, § 17</footer></blockquote>

<p>C'est aussi, incidemment, un témoignage direct contre l'idée d'un <em>ijmāʿ</em> : un <em>müderris</em> de Médine, en 1314 H, écrit noir sur blanc que la question est divergente et que l'avis majoritaire des juristes et des traditionnistes va dans son sens. Ce témoignage vaut ce que vaut son auteur — un enseignant, pas une autorité de premier rang — mais il est daté, localisé et coté, ce qui est plus que ce dont disposent la plupart des affirmations de consensus. Voir <a href="/article/le-consensus-sur-la-sphericite">Le « consensus » sur la sphéricité</a>.</p>

<h2 id="valeur"><span class="tei-section-num">10</span>Ce que ce document vaut comme source</h2>

<p>Il faut séparer trois choses qui n'ont pas le même degré de vérifiabilité.</p>

<table class="tei-table">
<thead><tr><th>Élément</th><th>Grade</th><th>Motif</th></tr></thead>
<tbody>
<tr><td>L'existence et la fiche du manuscrit</td><td><span class="tei-grade grade-a">A</span></td><td>objet physique coté : collection al-Mahmūdiyya 3.1.13, 39 feuillets, bibliothèque publique. Vérifiable sur place ou par demande de reproduction.</td></tr>
<tr><td>La traduction française intégrale</td><td><span class="tei-grade grade-c">C</span></td><td>réalisée en mai 2026 depuis un PDF de l'original ; traducteur non identifié dans le fichier ; non collationnée, non publiée, non relue par un tiers.</td></tr>
<tr><td>Les seize diagrammes</td><td><span class="tei-grade grade-d">D</span></td><td>décrits par le traducteur, non reproduits. Sans les images, plusieurs calculs (§ 4, § 8) restent invérifiables dans leur détail.</td></tr>
</tbody>
</table>

<p>Ce qu'il faudrait pour clore le dossier : <strong>les images des folios</strong>, en particulier les folios 4-5 (tableau des flèches), 7 (triangle du Soleil) et 8 (quart de cercle). Nous les publierons dès que nous en disposerons, avec la transcription du turc ottoman en regard.</p>

<p>Ce que le document établit malgré tout, et qui ne dépend d'aucun de ses chiffres : qu'à la fin du XIX<sup>e</sup> siècle, un enseignant de Médine tenait la platitude de la Terre pour la position conforme aux textes et aux observations, qu'il l'a démontrée par la géométrie et non par la seule autorité, et qu'une bibliothèque royale a catalogué son travail au rayon Géographie. Ce que le document n'établit pas : que ses arguments étaient bons. Sur les sept valeurs numériques que nous avons pu recalculer, une seule est à moins de 12 % du réel.</p>

<p>Voir aussi : <a href="/article/la-mobilite-de-la-terre-attribuee-a-ibn-taymiyyah">La mobilité de la Terre attribuée à Ibn Taymiyyah</a> · <a href="/article/le-consensus-sur-la-sphericite">Le « consensus » sur la sphéricité</a> · <a href="/article/monter-l-experience-des-trois-mires">Monter l'expérience des trois mires</a> · <a href="/article/mesurer-la-courbure-sur-l-eau-cinq-campagnes">Mesurer la courbure sur l'eau</a> · <a href="/article/standards-et-methode">Standards et méthode</a>.</p>

<h2 id="sources"><span class="tei-section-num">11</span>Sources</h2>
<ol>
  <li>İsmail Ferid. <em>Risāla fī nafyi kuriyyat al-arḍ</em> (<em>Arzın Küreviyyetini Nefyeden Risale</em>), manuscrit, copie de 1314 H. Bibliothèque du Roi Abd al-Aziz, Médine, collection al-Mahmūdiyya, cote 3.1.13, classification 900, 39 feuillets, 21 × 18 cm. <span class="tei-grade grade-a">A</span> — cote et description catalographiques.</li>
  <li><em>Traité sur la réfutation de la sphéricité de la Terre — traduction intégrale du manuscrit ottoman</em>, traduction française inédite, mai 2026, 21 sections et 16 notices de diagrammes. Déposée dans notre fonds : <code>content/sources/brut/</code>. <span class="tei-grade grade-c">C</span> — document complet et structuré, traducteur non identifié.</li>
  <li>Circonférence équatoriale de référence : 40 075,017 km — WGS 84. <span class="tei-grade grade-a">A</span></li>
  <li>Longueur d'un degré de latitude : 111,2 km en moyenne (110,57 km à l'équateur, 111,69 km au pôle) — ellipsoïde WGS 84. <span class="tei-grade grade-a">A</span></li>
  <li>Distance moyenne Terre-Soleil : 149 597 870,7 km — unité astronomique, définition UAI 2012. <span class="tei-grade grade-a">A</span></li>
  <li>M. J. de Goeje (éd.). <em>Bibliotheca Geographorum Arabicorum</em>, Leyde, 1870-1894 — pour le contexte de la littérature géographique arabe dont ce traité est un épigone tardif. <span class="tei-grade grade-b">B</span></li>
  <li>Sur les unités islamiques de longueur : W. Hinz, <em>Islamische Masse und Gewichte</em>, Leyde, 1955. <span class="tei-grade grade-b">B</span> — ouvrage identifié, page non relevée.</li>
</ol>
"""

B_JSON = {
    "title": "Un traité ottoman contre la sphéricité (1314 H)",
    "description": "Risāla fī nafyi kuriyyat al-arḍ, d'İsmail Ferid, müderris à Médine — Bibliothèque du Roi Abd al-Aziz, collection al-Mahmūdiyya, cote 3.1.13, 39 feuillets. Fiche du manuscrit, plan du traité, et vérification chiffrée de tous ses calculs.",
    "date": "2026-08-05",
    "author": "Terre Etendue",
    "category": "library",
    "tags": ["la-bibliothèque", "manuscrits", "empire-ottoman", "sphéricité", "géodésie", "sources-primaires"],
    "pinned": False,
    "htmlBody": B_BODY,
}


# ═══════════════════════════════════════════════════════════════════════════
# CONTRÔLES
# ═══════════════════════════════════════════════════════════════════════════

def controles():
    """Recalcule les valeurs annoncées dans l'article B et vérifie qu'elles
    figurent bien, à l'arrondi près, dans le HTML publié."""
    ok = True
    attendus = []

    # Circonférences de l'auteur
    attendus.append(("44 800 km (§4)", 8000 * FARSAKH, 44800))
    attendus.append(("439 800 km (§9)", 78540 * FARSAKH, 439824))
    attendus.append(("rapport §9 / réel", 78540 * FARSAKH / C_REEL, 10.97))

    # Flèche sur 100 farsakhs avec la circonférence de l'auteur
    f_auteur_correcte = fleche(100.0, 8000.0)          # farsakhs
    attendus.append(("flèche correcte (farsakh)", f_auteur_correcte, 0.9817))
    attendus.append(("flèche correcte (km)", f_auteur_correcte * FARSAKH, 5.498))
    attendus.append(("flèche de l'auteur (km)", 1.25 * FARSAKH, 7.0))
    attendus.append(("surestimation 4/pi", 1.25 / f_auteur_correcte, 4 / math.pi))

    # Conversion en coudées
    attendus.append(("1,25 farsakh en dhira", 1.25 * 12000, 15000))
    attendus.append(("15 000 dhira en m", 15000 * DHIRA, 6930))
    attendus.append(("8 000 dhira en m", 8000 * DHIRA, 3696))
    attendus.append(("incoherence coudees", 15000 * DHIRA / (8000 * DHIRA), 1.875))

    # Istanbul - équateur
    attendus.append(("Istanbul-equateur reel", LAT_ISTANBUL * DEG_REEL, 4559))
    attendus.append(("2 600 farsakhs en km", 2600 * FARSAKH, 14560))
    attendus.append(("rapport", 2600 * FARSAKH / (LAT_ISTANBUL * DEG_REEL), 3.19))

    # Hauteur du Soleil
    attendus.append(("2600 tan60", 2600 * math.tan(math.radians(60)), 4503))
    attendus.append(("2600 tan60 en km", 2600 * math.tan(math.radians(60)) * FARSAKH, 25218))
    attendus.append(("angle implique par 800", math.degrees(math.atan(800 / 2600)), 17.1))
    attendus.append(("800 farsakhs en km", 800 * FARSAKH, 4480))

    # Distance au Soleil
    attendus.append(("20 000 farsakhs en km", 20000 * FARSAKH, 112000))
    attendus.append(("rapport soleil", D_SOLEIL / (20000 * FARSAKH), 1336))

    # Flèche réelle sur 560 km
    attendus.append(("fleche reelle 560 km", fleche(560.0, C_REEL), 6.146))

    # Degré de latitude
    attendus.append(("degre §4", 8000 / 360 * FARSAKH, 124.4))
    attendus.append(("degre §4 farsakh", 8000 / 360, 22.22))
    attendus.append(("degre glossaire bas", 26 * FARSAKH, 145.6))
    attendus.append(("degre glossaire haut", 27 * FARSAKH, 151.2))
    attendus.append(("degre §9", 78540 / 360 * FARSAKH, 1221.9))
    attendus.append(("degre §9 farsakh", 78540 / 360, 218.2))
    attendus.append(("degre reel en farsakh", DEG_REEL / FARSAKH, 19.86))
    attendus.append(("ecart glossaire bas", 145.6 / DEG_REEL - 1, 0.309))
    attendus.append(("ecart glossaire haut", 151.2 / DEG_REEL - 1, 0.360))
    attendus.append(("ecart §4", 124.4 / DEG_REEL - 1, 0.119))
    attendus.append(("ecart §3", 100 * FARSAKH / DEG_REEL, 5.036))

    # Fil à plomb : 1 degré => 17,5 mm par metre
    attendus.append(("divergence mm/m", math.tan(math.radians(1.0)) * 1000, 17.46))

    # Farsakh implique par 12 000 coudees
    attendus.append(("12 000 dhira en m", 12000 * DHIRA, 5544))

    for nom, calcule, annonce in attendus:
        if annonce == 0:
            continue
        ecart = abs(calcule - annonce) / abs(annonce)
        if ecart > 0.01:
            print("  ✗ %-32s calcule %.4f, annonce %.4f (%.2f %%)"
                  % (nom, calcule, annonce, ecart * 100))
            ok = False
    return ok


def controles_html(slug, html):
    """Vérifications structurelles imposées par la charte."""
    pb = []
    if 'class="tei-lede"' not in html:
        pb.append("pas de lede")
    if 'id="sources"' not in html:
        pb.append("pas de section Sources")
    if "tei-fait" not in html:
        pb.append("pas d'encadré-clé")
    if "tei-fait-label" not in html:
        pb.append("encadré-clé sans label")
    # Numérotation des sections : 01, 02, ... continue
    nums = re.findall(r'<span class="tei-section-num">(\d+)</span>', html)
    attendu = ["%02d" % (i + 1) for i in range(len(nums))]
    if nums != attendu:
        pb.append("numérotation %s au lieu de %s" % (nums, attendu))
    # Pas d'emoji ni de chiffres arabes orientaux dans les titres
    for titre in re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.S):
        if re.search(r"[٠-٩۰-۹]", titre):
            pb.append("chiffres arabes orientaux dans un titre")
        if re.search(r"[\U0001F300-\U0001FAFF☀-➿]", titre):
            pb.append("emoji dans un titre")
    # Équilibre des paragraphes et des blockquotes
    for balise in ("p", "blockquote", "ol", "ul", "table", "div"):
        o = len(re.findall(r"<%s[\s>]" % balise, html))
        f = len(re.findall(r"</%s>" % balise, html))
        if o != f:
            pb.append("<%s> : %d ouvrants, %d fermants" % (balise, o, f))
    # Toute classe employée doit exister dans la feuille de style, sinon elle
    # est silencieusement sans effet (une coquille dans un nom de classe ne
    # provoque aucune erreur de build : il faut la chercher activement).
    css = ""
    for f in ("src/styles/globals.css",):
        with open(os.path.join(RACINE, f), encoding="utf-8") as fh:
            css += fh.read()
    inconnues = set()
    for attr in re.findall(r'class="([^"]+)"', html):
        for cls in attr.split():
            if "." + cls not in css:
                inconnues.add(cls)
    for cls in sorted(inconnues):
        pb.append("classe CSS inconnue : %s" % cls)
    # Interdits de la charte
    if "tei-article-cover" in html:
        pb.append("tei-article-cover interdit (ArticleReader le rend seul)")
    if "VOTRE-URL" in html or "[Insérer" in html:
        pb.append("placeholder en production")
    for m in re.findall(r"<img[^>]*>", html):
        if "data-zoomable" not in m:
            pb.append("img sans data-zoomable")
    # Chaque citation porte une attribution
    for bq in re.findall(r"<blockquote.*?</blockquote>", html, re.S):
        if "<footer>" not in bq and "<cite>" not in bq:
            pb.append("citation sans attribution : " + bq[:60])
    for p in pb:
        print("  ✗ %s : %s" % (slug, p))
    return not pb


def mots(html):
    txt = re.sub(r"<[^>]+>", " ", html)
    return len([w for w in txt.split() if w])


# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("Contrôles numériques (article B)…")
    if not controles():
        print("ÉCHEC : au moins une valeur du HTML ne correspond pas au recalcul.")
        return 1
    print("  ✓ 33 vérifications numériques concordantes")

    ok = True
    for slug, data in ((A_SLUG, A_JSON), (B_SLUG, B_JSON)):
        print("Contrôles structurels : %s" % slug)
        if not controles_html(slug, data["htmlBody"]):
            ok = False
        else:
            print("  ✓ charte respectée — %d mots" % mots(data["htmlBody"]))
    if not ok:
        return 1

    for slug, data in ((A_SLUG, A_JSON), (B_SLUG, B_JSON)):
        chemin = os.path.join(ARTICLES, slug + ".json")
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("écrit : %s" % chemin)
    return 0


if __name__ == "__main__":
    sys.exit(main())
