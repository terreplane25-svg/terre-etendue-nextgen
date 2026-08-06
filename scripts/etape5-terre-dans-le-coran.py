#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Étape 5, volet A — refonte structurelle de content/articles/la-terre-dans-le-coran.json.

Ce que fait ce script, et pourquoi :

1. Les seize versets de l'article étaient rendus en texte courant — trois <p>
   successifs : arabe, traduction, référence. La charte impose pour toute
   citation coranique le bloc unique
   <blockquote class="tei-citation arabic-quote"> → <p> arabe → <p> traduction
   → <footer>. Sans ce bloc, la référence se lisait comme une phrase du corps
   de l'article et rien ne distinguait visuellement la Révélation du commentaire.

2. Trois attributions portaient une référence de verset fausse. Elles ont été
   posées par scripts/localiser-citations-tafsir.py, qui reprend le verset du
   titre gouvernant : quand une section n'avait pas de titre porteur de verset,
   le script a fait suivre celui de la section précédente. Deux commentaires
   de daḥāhā (S79 V30) et un de dāʾibayn (S14 V33) se sont ainsi retrouvés
   attribués à S91 V6.

3. Six blocs de texte flottaient hors de toute balise, dont trois citations
   entières avec leur <cite> — invalides et non stylées.

4. Ajout d'une section sur les deux versets que le concordisme substitue à
   ceux-ci, et de trois encadrés « En clair ».

Le script est vérificatif : il refuse d'écrire si un contrôle échoue, et il
compte les citations avant et après pour garantir qu'aucune n'a disparu.
"""

import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN = os.path.join(RACINE, "content", "articles", "la-terre-dans-le-coran.json")


def charger():
    with open(CHEMIN, encoding="utf-8") as f:
        return json.load(f)


# ── 1. Les trois attributions fautives ──────────────────────────────────────
# (motif exact, remplacement, motif de contrôle du contexte)
CORRECTIONS_FOOTER = [
    # daḥāhā — nid d'autruche : commentaire de S79 V30, pas de S91 V6
    ("nid d'autruche qu'il est udḥiya car il est aplani au sol. »</p><footer>"
     "— Tafsīr al-Qurṭubī, sur S91 V6</footer>",
     "nid d'autruche qu'il est udḥiya car il est aplani au sol. »</p><footer>"
     "— Tafsīr al-Qurṭubī, sur S79 V30</footer>"),
    # daḥāhā — Ibn ʿAbbās : idem
    ("puis après cela Il a aplani la terre. »</p><footer>"
     "— Tafsīr al-Baghawī, sur S91 V6</footer>",
     "puis après cela Il a aplani la terre. »</p><footer>"
     "— Tafsīr al-Baghawī, sur S79 V30</footer>"),
    # dāʾibayn — Soleil et Lune : commentaire de S14 V33
    ("« C'est-à-dire constamment, continuellement jusqu'au jour du jugement. »</p><footer>"
     "— Tafsīr Ibn Kathīr, sur S91 V6</footer>",
     "« C'est-à-dire constamment, continuellement jusqu'au jour du jugement. »</p><footer>"
     "— Tafsīr Ibn Kathīr, sur S14 V33</footer>"),
]

# ── 2. Les blocs de texte nu ────────────────────────────────────────────────
NU = [
    ("\nLes sept termes\n",
     '\n<p>Voici les sept, avec la racine, le sens que lui donnent les '
     'dictionnaires classiques, et les versets où elle apparaît.</p>\n'),

    ("\nTriple réfutation\n",
     '\n<p>La réfutation porte sur trois plans indépendants — un seul suffirait, '
     'les trois convergent.</p>\n'),

    ("<strong>Le raisonnement :</strong> Pourquoi Allāh placerait-Il des montagnes "
     "comme des ancres (rawāsī) pour empêcher la Terre de vaciller, si elle était "
     "déjà en rotation à 1 670 km/h et en orbite à 107 000 km/h ? Les montagnes "
     "empêcheraient un vacillement mais pas une rotation de 465 m/s ? L'explication "
     "la plus simple : la Terre est immobile, et les montagnes la stabilisent contre "
     "les secousses.\n",
     "<p><strong>Le raisonnement :</strong> pourquoi Allāh placerait-Il des montagnes "
     "comme des ancres (<em>rawāsī</em>) pour empêcher la Terre de vaciller, si elle "
     "était déjà en rotation à 1 670 km/h à l'équateur et en révolution à "
     "107 000 km/h ? Des ancres qui arrêteraient un balancement mais laisseraient "
     "passer 465 m/s ? Le verset choisit <em>tamīd</em> — vaciller, tanguer — et "
     "l'oppose à l'état stable que les montagnes produisent. La lecture la plus "
     "économique est que la Terre est immobile et que les montagnes la tiennent "
     "contre les secousses.</p>\n"),
]

# Les trois citations orphelines : texte nu + <cite>, à remettre en blockquote.
ORPHELINES = [
    ('« Farashash-shayʾ c\'est-à-dire qu\'il l\'a étendu (basaṭahu). Al-Layth dit que '
     'al-farsh est le fait de déployer et étendre sa couche, son lit. On dit iftarasha '
     'ses bras lorsqu\'ils sont mis à plat sur le sol. »<cite>— Lisān al-ʿArab, vol. 6 '
     'p. 326 (<a href="https://shamela.ws/book/1687/3338" target="_blank">shamela.ws</a>)</cite>',
     'Lisān al-ʿArab, vol. 6 p. 326',
     'https://shamela.ws/book/1687/3338',
     '« <em>Farasha al-shayʾ</em>, c\'est-à-dire qu\'il l\'a étendu (<em>basaṭahu</em>). '
     'Al-Layth dit que <em>al-farsh</em> est le fait de déployer et d\'étendre sa couche, '
     'son lit. On dit <em>iftarasha</em> ses bras lorsqu\'ils sont mis à plat sur le sol. »'),

    ('« Il l\'a étendue d\'une distance de cinq cents ans à partir du dessous de la '
     'Kaʿbah. »<cite>— Tafsīr Muqātil, vol. 4 p. 451 '
     '(<a href="https://shamela.ws/book/23614/1852#p1" target="_blank">shamela.ws</a>)</cite>',
     'Tafsīr Muqātil ibn Sulaymān, vol. 4 p. 451, sur S71 V19',
     'https://shamela.ws/book/23614/1852#p1',
     '« Il l\'a étendue d\'une distance de cinq cents ans à partir du dessous de la Kaʿbah. »'),

    ('« C\'est-à-dire un lit, un tapis d\'une distance de cinq cents ans. »<cite>'
     '— Tafsīr Muqātil, vol. 4 p. 558 '
     '(<a href="https://shamela.ws/book/23614/1929#p1" target="_blank">shamela.ws</a>)</cite>',
     'Tafsīr Muqātil ibn Sulaymān, vol. 4 p. 558, sur S78 V6',
     'https://shamela.ws/book/23614/1929#p1',
     '« C\'est-à-dire un lit, un tapis d\'une distance de cinq cents ans. »'),

    ('« Pour Qatāda, al-Suddī et Sufyān, le terme daḥāhā renvoie à l\'aplanissement... '
     'Al-Ṭabarī dit : ad-daḥw chez les arabes est l\'aplanissement (al-basṭ) et '
     'l\'extension (al-madd). »<cite>— Tafsīr al-Ṭabarī '
     '(<a href="https://shamela.ws/book/43/14124#p1" target="_blank">shamela.ws</a>)</cite>',
     'Tafsīr al-Ṭabarī, sur S79 V30',
     'https://shamela.ws/book/43/14124#p1',
     '« Pour Qatāda, al-Suddī et Sufyān, le terme <em>daḥāhā</em> renvoie à '
     'l\'aplanissement… Al-Ṭabarī dit : <em>ad-daḥw</em> chez les Arabes est '
     'l\'aplanissement (<em>al-basṭ</em>) et l\'extension (<em>al-madd</em>). »'),

    ('« Sa parole "la terre est un kawkab" n\'est que fausseté et mensonge sur Allāh '
     'Le Très-Haut qui ne l\'a pas nommée ainsi. Celui qui l\'a créée l\'a appelée "terre" '
     '(arḍ). Le kawkab désigne l\'étoile et sa place est en hauteur. »<cite>'
     '— Shaykh al-Kāfī al-Tūnisī, Al-Masāʾil al-Kāfiyya '
     '(<a href="https://shamela.ws/book/13607/112#p1" target="_blank">shamela.ws</a>)</cite>',
     'Al-Kāfī al-Tūnisī, <em>Al-Masāʾil al-Kāfiyya</em>, p. 112',
     'https://shamela.ws/book/13607/112#p1',
     '« Sa parole “la terre est un <em>kawkab</em>” n\'est que fausseté et mensonge sur '
     'Allāh le Très-Haut, qui ne l\'a pas nommée ainsi. Celui qui l\'a créée l\'a appelée '
     '“terre” (<em>arḍ</em>). Le <em>kawkab</em> désigne l\'astre, et sa place est en hauteur. »'),
]

# ── 3. Le bloc PDF, rendu en texte nu avec des gestionnaires inline ─────────
PDF_AVANT = """  📄
    <p>Document complet : Les preuves religieuses et scientifiques (PDF)</p>
    <p>L'intégralité des preuves coraniques, prophétiques et linguistiques sur la planéité, l'immobilité de la Terre, la mobilité du Soleil et l'impossibilité de franchir les cieux.</p>
  <a href="https://terre-etendue-islam.fr/wp-content/uploads/2026/04/document-maitre-preuves-religieuses.pdf" target="_blank" onmouseover="this.style.background='#A97544';this.style.transform='translateY(-2px)'" onmouseout="this.style.background='#8B5C36';this.style.transform='none'">Consulter le PDF ↗</a>
"""

PDF_APRES = """<div class="tei-infobox">
<p><strong>Document complet — Les preuves religieuses et scientifiques (PDF)</strong></p>
<p>L'intégralité des preuves coraniques, prophétiques et linguistiques sur la planéité, l'immobilité de la Terre, la mobilité du Soleil et l'impossibilité de franchir les cieux. <a href="https://terre-etendue-islam.fr/wp-content/uploads/2026/04/document-maitre-preuves-religieuses.pdf" target="_blank" rel="noopener">Consulter le PDF</a>.</p>
</div>
"""


def bloc_verset(m):
    """Trois <p> successifs → le bloc de citation unique imposé par la charte."""
    arabe, trad, ref = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
    nom, versets = [x.strip() for x in ref.split("—")]
    return ('<blockquote class="tei-citation arabic-quote">\n'
            '<p><span class="tei-arabic">%s</span></p>\n'
            '<p>%s</p>\n'
            '<footer>— Sourate %s — %s</footer></blockquote>' % (arabe, trad, nom, versets))


# ── 4. Nouvelle section : les deux versets substitués ───────────────────────
SECTION_SUBSTITUTION = """<h2 id="q-ailleurs"><span class="tei-section-num">09</span>Les deux versets qu'on met à la place</h2>

<p>Une objection revient à chaque fois que l'on aligne ces sept termes : « mais le Coran annonce le Big Bang et l'expansion de l'univers ». Elle mérite d'être prise au sérieux, et elle mérite surtout d'être <strong>située</strong>, car elle repose sur deux versets — et ni l'un ni l'autre ne parle de la forme de la Terre.</p>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">أَوَلَمْ يَرَ الَّذِينَ كَفَرُوا أَنَّ السَّمَاوَاتِ وَالْأَرْضَ كَانَتَا رَتْقًا فَفَتَقْنَاهُمَا</span></p>
<p>« Ceux qui ont mécru ne voient-ils pas que les cieux et la terre formaient une masse compacte, et que Nous les avons ensuite séparés ? »</p>
<footer>— Sourate Al-Anbiyāʾ — S21 V30</footer></blockquote>

<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">وَالسَّمَاءَ بَنَيْنَاهَا بِأَيْدٍ وَإِنَّا لَمُوسِعُونَ</span></p>
<p>« Et le ciel, Nous l'avons édifié par Notre puissance, et en vérité Nous sommes <em>mūsiʿūn</em>. »</p>
<footer>— Sourate Adh-Dhāriyāt — S51 V47</footer></blockquote>

<p>Le premier porte sur la <em>séparation</em> des cieux et de la terre, le second sur l'<em>édification du ciel</em>. Aucun des deux n'emploie l'un des sept termes de forme relevés ci-dessus, et aucun ne qualifie la surface terrestre. Ils décrivent des actes de création, pas une géométrie.</p>

<p>Cela ne suffit évidemment pas à réfuter la lecture concordiste : encore faut-il montrer que <em>ratq</em> ne signifie pas « singularité », que <em>fatq</em> ne signifie pas « explosion », et que <em>mūsiʿūn</em> ne signifie pas « en expansion ». Cette démonstration lexicale — trois dictionnaires classiques pour la première paire, cinq <em>tafsīr</em> pour le second mot, textes arabes à l'appui — occupe deux sections entières de l'article <a href="/article/le-concordisme">Le concordisme</a>. Elle n'a pas sa place ici, où il s'agit de la Terre et non des cieux.</p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Quand une discussion sur la forme de la Terre bascule sur le Big Bang, on a changé de sujet sans le dire. Les versets qu'on avance alors parlent du ciel et de sa création, pas du sol. On peut discuter des deux — mais séparément, et c'est ce que nous faisons.</p></div>

"""

ENCLAIR_TERMES = """<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Ces sept mots ne sont pas sept synonymes vagues. Chacun a une racine et un emploi concret dans la langue courante : on <em>farasha</em> un tapis qu'on déroule, on <em>madda</em> une corde qu'on tend, on <em>sataha</em> le toit plat d'une maison. Ce sont des gestes du quotidien, et tous les sept décrivent la même chose faite au sol : on l'aplatit et on l'étale.</p></div>
"""

ENCLAIR_IMMOBILE = """<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Comptez les verbes. Le Soleil, dans le Coran, court, se lève, se couche, nage, se prosterne, chemine sans relâche. La Terre, elle, est posée, étendue, ancrée, stabilisée — jamais elle ne bouge. Ce n'est pas un argument de traduction : ce sont deux vocabulaires distincts, appliqués systématiquement à deux objets distincts, sur plus de quatre cents occurrences.</p></div>
"""


"""« Conteneurs de texte » : tout texte du corps doit se trouver dans l'un d'eux.
Un fragment posé directement entre deux balises de bloc n'est pas invalide au
sens du navigateur, mais il échappe à toute règle de style — c'est ainsi que
« Les sept termes » et trois citations entières se rendaient en corps nu.
"""
CONTENEURS = {"p", "li", "footer", "td", "th", "h1", "h2", "h3", "h4",
              "figcaption", "caption", "cite", "small", "blockquote",
              "span", "strong", "em", "a"}


def texte_hors_conteneur(html):
    pb = []
    profondeur = 0
    for morceau in re.split(r"(<[^>]+>)", html):
        if morceau.startswith("<"):
            m = re.match(r"<\s*(/?)\s*([a-zA-Z][a-zA-Z0-9]*)", morceau)
            if m and m.group(2).lower() in CONTENEURS and not morceau.rstrip().endswith("/>"):
                profondeur += -1 if m.group(1) else 1
                profondeur = max(0, profondeur)
        elif profondeur == 0 and morceau.strip():
            pb.append("texte hors conteneur : %r" % morceau.strip()[:60])
    return pb


def transformer(html):
    pb = []
    n_bq_avant = html.count("<blockquote")

    # 1. attributions fautives
    for avant, apres in CORRECTIONS_FOOTER:
        if avant not in html:
            pb.append("attribution à corriger introuvable : %s" % avant[-48:])
        else:
            html = html.replace(avant, apres, 1)

    # 2. blocs de texte nu
    for avant, apres in NU:
        if avant not in html:
            pb.append("bloc de texte nu introuvable : %r" % avant[:40])
        else:
            html = html.replace(avant, apres, 1)

    # 3. citations orphelines → blockquote
    for avant, attrib, lien, corps in ORPHELINES:
        if avant not in html:
            pb.append("citation orpheline introuvable : %r" % avant[:48])
            continue
        apres = ('<blockquote class="tei-citation"><p>%s</p>'
                 '<footer>— %s (<a href="%s" target="_blank" rel="noopener">shamela.ws</a>)'
                 '</footer></blockquote>' % (corps, attrib, lien))
        html = html.replace(avant, apres, 1)

    # 4. bloc PDF
    if PDF_AVANT not in html:
        pb.append("bloc PDF introuvable")
    else:
        html = html.replace(PDF_AVANT, PDF_APRES, 1)

    # 5. les seize versets
    motif = re.compile(
        r'<p><span class="tei-arabic">(.*?)</span></p>\s*\n'
        r'<p>(«.*?»)</p>\s*\n'
        r'<p>([^<]*?— S\d+ V[\d\-]+)</p>', re.S)
    html, n = motif.subn(bloc_verset, html)
    if n != 16:
        pb.append("%d blocs de verset convertis au lieu de 16" % n)

    # 6. encadrés « En clair »
    ancre = '<div class="tei-fait library">\n<span class="tei-fait-label">CE QUE LE TEXTE ÉTABLIT</span>\n<p>Sur plus de 450 occurrences'
    if ancre not in html:
        pb.append("ancre de l'encadré des sept termes introuvable")
    else:
        html = html.replace(ancre, ENCLAIR_TERMES + ancre, 1)

    ancre = '<h2 id="q-soleil">'
    if ancre not in html:
        pb.append("ancre section Soleil introuvable")
    else:
        html = html.replace(ancre, ENCLAIR_IMMOBILE + ancre, 1)

    # 7. nouvelle section, avant la conclusion
    ancre = '<h2 id="q-ccl">'
    if ancre not in html:
        pb.append("ancre conclusion introuvable")
    else:
        html = html.replace(ancre, SECTION_SUBSTITUTION + ancre, 1)

    # 8. renumérotation continue des sections
    compteur = [0]

    def renum(m):
        compteur[0] += 1
        return '<span class="tei-section-num">%02d</span>' % compteur[0]

    html = re.sub(r'<span class="tei-section-num">\d+</span>', renum, html)

    # ── contrôles ──
    n_bq_apres = html.count("<blockquote")
    # 16 versets + 5 orphelines + 1 dans la nouvelle section... la nouvelle
    # section en apporte 2. Aucune citation ne doit avoir disparu.
    attendu = n_bq_avant + 16 + 5 + 2
    if n_bq_apres != attendu:
        pb.append("citations : %d avant, %d après, %d attendues" % (n_bq_avant, n_bq_apres, attendu))
    if "<cite>" in html:
        pb.append("il reste un <cite> hors blockquote")
    if ", sur S91 V6" in html:
        # il n'en reste que les deux légitimes de la section 03
        n = html.count(", sur S91 V6")
        if n != 2:
            pb.append("%d attributions « sur S91 V6 » subsistent, 2 attendues" % n)
    pb += texte_hors_conteneur(html)
    for b in ("p", "blockquote", "div", "ol", "ul", "table", "h2", "h3", "span", "footer"):
        o = len(re.findall(r"<%s[\s>]" % b, html))
        f = len(re.findall(r"</%s>" % b, html))
        if o != f:
            pb.append("<%s> : %d ouvrants, %d fermants" % (b, o, f))
    return html, pb


def main():
    data = charger()
    html, pb = transformer(data["htmlBody"])
    for p in pb:
        print("  ✗ %s" % p)
    if pb:
        return 1
    data["htmlBody"] = html
    data["updated"] = "2026-08-05"
    with open(CHEMIN, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    mots = len(re.sub(r"<[^>]+>", " ", html).split())
    print("  ✓ la-terre-dans-le-coran : %d mots, %d citations, %d encadrés En clair"
          % (mots, html.count("<blockquote"), html.count('class="tei-enclair"')))
    return 0


if __name__ == "__main__":
    sys.exit(main())
