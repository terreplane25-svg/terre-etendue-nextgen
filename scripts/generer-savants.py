#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Jeu de donnees des autorites citees sur la forme de la Terre.

SOURCE UNIQUE : content/sources/brut/PAROLES_DE_SAVANTS_DE_DIVERSES_EPOQUES,
_SUR_LA_FORME_DE_LA_TERRE.pdf, transcrit a la main entree par entree.

Regles de transcription tenues :
  - aucune reference n'est completee, devinee ni « corrigee » ;
  - les incertitudes du document source sont signalees dans `_incertitude`,
    jamais resolues en silence ;
  - le grade dit ce que la reference permet de VERIFIER, pas la reputation de
    l'auteur : A = lien direct vers la page, B = volume et page sans lien,
    C = page seule ou lien vers un depot non pagine.

Produit content/bibliotheque/savants-forme-terre.json et la table de l'article.
"""
import json, re, collections

def E(n, nom, mort, ouvrage, citations, naissance=None, note=None):
    return {"n": n, "nom": nom, "naissance_H": naissance, "mort_H": mort,
            "ouvrage": ouvrage, "citations": citations, "_incertitude": note}

def C(verset, texte, vol=None, page=None, url=None, note=None):
    return {"verset": verset, "citation": texte, "volume": vol, "page": page,
            "url": url, "_incertitude": note}

SAVANTS = [
 E(1, "El Qahtânî El Andaloûssî", 383, "Noûnîyyatoul Qahtânî", [
   C(None, "Ont menti les astronomes, les astrologues et leurs semblables — de la science d'Allah ils se sont prétendus. La terre chez tous deux est sphérique et ils se sont associés dans cette prétention. Et pour les gens doués de raison la terre est plane, avec pour preuves le Coran clair et véridique. Et Il l'a étalée, déployée comme un lieu de repos pour la créature, et construit son ciel de la meilleure construction. Et Allāh a informé que la terre est plate, et cela de la plus illustre et la plus claire des façons Il nous l'a appris. Il nous a informés de sa longueur et de sa largeur — n'est-ce pas les caractéristiques d'une chose nivelée ?",
     None, "32-33", "https://shamela.ws/book/7533/16#p1", "vers 245-255")]),

 E(2, "Aboû Mansoûr AbdelQâhir El Baghdâdî", 429, "Oussouloud-Dîne, éd. Ed-Dawlah", [
   C(None, "Le nom d'Allah al-Bāsiṭ désigne Sa capacité à étendre la subsistance à qui Il veut, ainsi que le fait d'étendre. C'est pourquoi Il l'a désignée [dans le Coran] comme étant un tapis [bisāṭa], contrairement à la parole des philosophes et des astrologues qui prétendaient que la terre était sphérique et non aplanie.",
     None, "124", "https://archive.org/details/osooluldeen")], naissance=350),

 E(3, "Mekkî Ben Abî Tâlib El Qayssî El Qayrawânî", 437, "El Hidâyah Ilâ Bouloughin-Nihâyah", [
   C("s50 v7 · s15 v19", "Ne voient-ils pas comment la terre est vastement plate et dépourvue de courbure ?",
     "11", "7031", "https://shamela.ws/book/22593/6941")]),

 E(4, "Alî Ben Mouhammed El Mawroûdî", 450, "En-Noukatou Wal ʿOuyoûne", [
   C("s13 v3", "C'est-à-dire qu'Il l'a aplanie afin d'y vivre stablement, répliquant ainsi à ceux qui prétendaient qu'elle était ronde telle une sphère.",
     "3", "92", "https://shamela.ws/book/8346/1744#p1"),
   C("s71 v19", "C'est-à-dire aplanie, et il y a en cela une preuve qu'elle est plate.",
     "6", "103", "https://shamela.ws/book/8346/4080")], naissance=364),

 E(5, "Abou Qassim El Qoucheyrî", 465, "Et-Teysîr fî ʿIlmit-Tefsîr", [
   C("s2 v22", "Dans ce verset il y a une preuve que la terre est aplanie et qu'elle n'est pas de forme sphérique.",
     None, "462", "https://ia803400.us.archive.org/6/items/quran05001/quran05321.pdf")], naissance=376),

 E(6, "El Hâkim El Djechmî El Beyhaqî", 494, "Et-Tehdhîb fit-Tefsîr", [
   C("s2 v22", "Cela prouve que la terre est aplanie et pas sphérique.",
     None, "283-284", None, "lien vers une archive .rar non paginée : grade C")]),

 E(7, "Mahmoud Ben Hamza El Karmânî", 531, "Loubâbout-Tafâssir", [
   C("s88 v20", "Certains se sont appuyés dessus pour décrire la forme plate de la terre et démentir sa forme sphérique.",
     None, "588", "https://shamela.ws/book/36/3588#p1")]),

 E(8, "Ibn ʿAtiyyah El Andaloûsî El Maharbî", 542, "El Mouharraroul Wadjîz fî Tefsîril Kitâbil ʿAzîz", [
   C("s13 v3", "Étendre la terre implique qu'elle soit plane et non pas sphérique, et c'est le sens apparent de la législation.",
     "3", "293", "https://shamela.ws/book/23632/1412#p1"),
   C("s88 v20", "Ce verset prouve clairement que la terre est plate et n'est pas une sphère, et c'est l'avis des gens de science. L'avis soutenant sa sphéricité, même s'il n'invalide aucun des piliers de l'Islam, ne fait pas partie des avis des savants de l'Islam.",
     "5", "475", "https://shamela.ws/book/23632/2722#p1"),
   C("s71 v19", "Le sens apparent de la parole du Très-Haut « tapis » [bisāṭa] indique que la terre est plate. La croyance en l'un des deux n'est pas répréhensible en soi, sauf que l'affirmation de la sphéricité est basée sur une vision corrompue. Quant à la croyance qu'elle est plate, elle repose sur le sens apparent du Livre d'Allāh et n'est entachée d'aucune perversion. Ibn Mujāhid a démontré la validité de cela en s'appuyant sur l'eau de mer autour du globe, disant que si la terre était sphérique alors l'eau ne pourrait s'y stabiliser.",
     "5", "375", "https://shamela.ws/book/23632/2622#p1",
     "le document source porte « la terre est plate, sphérique » — lapsus manifeste pour « et non sphérique », le reste du passage l'établissant ; transcrit ici sans le lapsus, à vérifier sur la page")], naissance=481),

 E(9, "Mouhammed Ben Ahmad El Qourtoubî", 671, "El Jâmiʿ li Ahkâmil Qour'ân", [
   C("s13 v3", "Il y a dans ce verset une réponse à ceux qui prétendent que la terre est comme une sphère. Et ce sur quoi sont les savants musulmans et les gens du Livre est l'immobilité, la stabilité et l'étendue de la terre, et que son mouvement est causé par les séismes.",
     "9", "280", "https://shamela.ws/book/20855/3611")], naissance=600),

 E(10, "Ibnou Djazî El Gharnâtî", 741, "Et-Teshîl li ʿOuloûmit-Tenzîl", [
   C("s13 v3", "Étendre la terre implique qu'elle soit plate et non sphérique, et c'est ce qui apparaît de la législation.",
     "1", "399", "https://shamela.ws/book/23626/395")], naissance=693),

 E(11, "Aboul Hassan ʿAlâ'ou Dîne El Khâzin", 741, "Tefsîroul Khâzin — Libâbit-Ta'wîl fî Maʿânit-Tanzîl", [
   C("s13 v3", "C'est-à-dire qu'Il l'a aplanie sur la surface de l'eau. Il a été dit que la terre était regroupée puis Il l'étendit depuis le dessous de la maison sacrée, et cette parole n'est valide que si nous disons que la terre est plate, alors que chez les astronomes la terre est sphérique. Et il est possible que l'on dise : si le globe est très grand alors chaque parcelle est vue comme étant plate, ainsi a lieu la conciliation. Malgré cela, Allāh nous informe qu'Il a étendu la terre, qu'Il l'a aplanie et nivelée. Tout cela indique l'aplatissement.",
     "3", "4", "https://shamela.ws/book/23628/1014#p1"),
   C("s15 v19", "C'est-à-dire que Nous l'avons aplanie sur la surface de l'eau. Comme il a été dit qu'elle fut étendue depuis le dessous de la maison sacrée ; et c'est l'avis des exégètes. Les hauts membres du comité [astronomique] ont prétendu que la terre était une sphère immense dont une partie est submergée dans l'eau et l'autre non… Ils ont justifié le verset en avançant le fait que si une sphère est immense alors chaque partie d'elle est perçue comme une grande surface plane. De cette façon, il est confirmé que la terre est plane et étendue, et qu'elle est également sphérique. Les exégètes ont répondu qu'Allāh informe dans Son Livre qu'elle est aplanie et étendue, et que si c'était une sphère Il l'aurait assurément indiqué, et Allāh est plus connaisseur du message.",
     "3", "52", "https://shamela.ws/book/23628/1062#p1",
     "l'ellipse après « et l'autre non » est celle du document source, non la nôtre. "
     "Noter que cette citation RAPPORTE l'argument de conciliation des astronomes avant "
     "de donner la réponse des exégètes : al-Khâzin expose un débat, il ne se contente "
     "pas d'affirmer.")], naissance=678),

 E(12, "Âthîroud Dîne Abou Hayân El Andaloûssî", 745, "El Bahroul Mouhît", [
   C("s71 v19", "Ce qui apparaît du verset est que la terre n'est pas sphérique mais bien aplanie.",
     "10", "284", "https://shamela.ws/book/23591/5915#p1")], naissance=654),

 E(13, "Adhadou Dîne El Iyadjî", 756, "El Mawâqif fî ʿIlmil Kalâm", [
   C(None, "La terre n'est pas sphérique mais plate.",
     None, "199", "http://noor-book.com/en/flcws3"),
   C(None, "Ils prétendent que la terre est sphérique…",
     None, "217", "http://noor-book.com/en/flcws3",
     "citation laissée en suspens par le document source lui-même : le texte s'arrête "
     "sur des points de suspension. Elle est conservée telle quelle et ne doit pas être "
     "présentée comme complète.")],
   note="un second document de notre fonds, la traduction d'El Adilla El Kâchifa, donne "
        "pour la position du même auteur les pages 100, 210 et 217 de El Mawâqif. Les deux "
        "sources ne concordent que sur 217 : la pagination reste à vérifier sur l'édition."),

 E(14, "Ibn Samîn El Halabî", 756, "ʿOumdatoul Houfâdh", [
   C("s88 v20", "C'est-à-dire aplanie et élargie, comme dans Sa parole « Et quant à la terre, après cela, Il l'a étendue » (s79 v30), c'est-à-dire aplanie après avoir été une boule.",
     "2", "197", "https://shamela.ws/book/17829/712")]),

 E(15, "Abou Rachîd En-Neyssâboûrî", 832, "Massâiloul Khilâf Beynal Basriyîn wal Baghdâdiyyîn", [
   C(None, "La terre est plane, elle n'est pas sphérique.",
     None, "71", "https://down.ketabpedia.com/files/bkb/bkb-ol04488-ketabpedia.com.pdf")], naissance=775),

 E(16, "Djalâloud-Dîne El Mahallî", 864, "Tefsîroul Jalâleyn", [
   C("s88 v20", "C'est-à-dire aplanie ; démontre l'omnipotence et l'unicité, et fut précédé par le verset des chameaux car ils sont les plus reliés à la terre. Et Sa parole suṭiḥat [aplanie] nous indique clairement la planéité de sa surface, et c'est sur quoi sont les savants de la législation [šarīʿa], et non pas une sphère comme l'affirment les membres de la hayʾa [commission astronomique], même si elle n'annule aucun des piliers de la législation.",
     None, "305", "https://shamela.ws/book/12876/6678")], naissance=791),

 E(17, "Abderrahmân Aboû Zeyd Eth-Thaʿâlibî", 872, "El Jawâhiroul Hissân fî Tafsîril Qour'ân", [
   C("s88 v20", "Et ce verset indique qu'elle est plane et non sphérique, et c'est l'avis des gens de science.",
     "5", "583", "https://shamela.ws/book/23618/2610"),
   C("s71 v19", "Ce qui est apparent du verset est que la terre est plane et non sphérique. La croyance en l'un des deux n'est pas répréhensible en soi, sauf que l'affirmation de la sphéricité est basée sur une vision corrompue. Quant à la croyance qu'elle est plate, elle repose sur le sens apparent du Livre d'Allāh et n'est entachée d'aucune perversion. Ibn Mujāhid a démontré la validité de cela en s'appuyant sur l'eau de mer autour du globe, disant que si la terre était sphérique alors l'eau ne pourrait s'y stabiliser.",
     "5", "490", "https://shamela.ws/book/23618/2517")], naissance=786),

 E(18, "Mouhammed Ben Abderrahmân El Îydjî", 905, "Djâmiʿoul Bayân fî Tefsîril Qour'ân", [
   C("s50 v7", "C'est-à-dire aplanie et élargie, et c'est une indication qu'elle n'est pas sphérique.",
     "4", "178", "https://shamela.ws/book/29743/1896#p1")]),

 E(19, "Djalâloud-Dîne Es-Souyoutî", 911, "El Iklîl fî Istinbâtit-Tenzîl", [
   C("s2 v22", "La plupart des exégètes s'est appuyée sur ce verset pour décrire la forme plate de la terre, en opposition à la sphère.",
     None, "27", "https://shamela.ws/book/1385/17",
     "le document source insère ici le nom de Mahmoud Ben Hamza El Karmânî, vraisemblablement par report accidentel depuis l'entrée 7 ; attribution à vérifier sur la page"),
   C("s88 v20", "C'est une réplique aux membres de la hayʾa [commission astronomique] qui prétendent que la terre n'est pas plate mais sphérique, comme le rappelle šayḫ Jalāl al-Dīn al-Maḥallī dans son tafsīr.",
     None, "286", "https://shamela.ws/book/1385/276")], naissance=849),

 E(20, "Mouhammed Ben Mouhammed Es-Siddîqî El Bakrî", 952, "Tefsîroul Bakrî, éd. Dār al-Kutub al-ʿIlmiyya", [
   C("s88 v20", "C'est-à-dire aplanie, s'appuyant sur cela pour montrer la puissance d'Allāh. Et l'aplanissement de la terre indique qu'elle est plate et non sphérique. Et l'affirmation des membres du comité astronomique selon laquelle la terre serait une sphère ne contredit pas sa planéité ni ne détruit un fondement législatif. Leurs allégations ne portent atteinte en rien à la religion.",
     "3", "467", "https://quranpedia.net/book/14548")]),

 E(21, "Shemsou Dîne Esh-Shirbînî", 977, "Es-Sirâdjoul Mounîr", [
   C("s13 v3", "C'est-à-dire qu'Il l'a aplanie en long et en large pour nous permettre de marcher dessus et permettre aux animaux de s'y déplacer. S'Il avait voulu, Il l'aurait faite tel un mur rendant la stabilité dessus impossible. Cela, si on admet que la terre est plate et pas sphérique. Et selon les membres du comité elle est sphérique. Comment peuvent-ils affirmer cela alors que l'élargissement de la terre contredit la forme sphérique ? Tout cela indique une planéité, et Allāh est plus véridique dans les propos et plus clair dans les preuves que les membres du comité.",
     "2", "145", "https://shamela.ws/book/1466/799#p1")]),

 E(22, "Mouhammed Ibn Ahmed Nedjmoud-Dîne El Ghîtî", 981, "El Adjwibatoul Moufîda ʿanil As'ilatil ʿAdîdah", [
   C(None, "Ce sur quoi ont penché tous les exégètes dans le Livre Sublime est que le ciel est plat et non sphérique, tout comme la terre qui est également plate et non sphérique.",
     None, None, "https://rattibha.com/thread/1598356740176740359",
     "aucune pagination dans le document source ; le lien renvoie à un fil de réseau social et non à l'ouvrage : grade C")], naissance=910),

 E(23, "Shihâbou Dîne El Khifâdjî", 1069, "Hâshiyatoush-Shihâb ʿalâ Tefsîr El Baydhâwî", [
   C("s88 v20", "C'est-à-dire aplanie, soit pour nier sa sphéricité comme le font les adeptes de la législation, soit par rapport à ce que nous voyons de sa grandeur.",
     "8", "353", "https://shamela.ws/book/1535/3091#p1")]),

 E(24, "El Qawnawî", 1195, "Hâchiyatoul Qawnâwî", [
   C(None, "Les versets du Coran prouvent que la terre est plate. Ibn ʿAbbās ainsi qu'un grand nombre de savants sont plus connaisseurs de la langue et de la façon de s'exprimer clairement. Il ne fait donc aucun doute que le fait de pencher vers cela est acceptable auprès des connaisseurs. Quant à sa sphéricité, elle émane des philosophes.",
     None, "382", "https://ia601605.us.archive.org/35/items/WAQ75141/hqb02.pdf")]),

 E(25, "Ahmed Ben Mouhammed Es-Sâwî", 1241, "Hâshiyatous-Sâwî ʿalâ Tefsîril Djalâleyn", [
   C(None, "La terre a été créée sphérique dans un premier temps, puis a été aplanie après la création des cieux.",
     "1", "532", "https://ketabonline.com/ar/books/70941/read?part=1&page=510",
     "position distincte des autres entrées : sphéricité initiale puis aplanissement. À conserver telle quelle, elle nuance le tableau")], naissance=1125),

 E(26, "Mouhammed Ben Alî Esh-Shawkânî", 1255, "Fethoul Qadîr", [
   C("s50 v7 · s15 v19", "C'est-à-dire aplanie et étalée, comme dans Sa parole « Et quant à la terre, après cela, Il l'a étendue » (s79 v30), et dans Sa parole « Et la terre, Nous l'avons étendue. Et de quelle excellente façon Nous l'avons nivelée ! » (s51 v48). Il y a en cela une réplique à ceux qui prétendent qu'elle est sphérique.",
     "3", "151", "https://shamela.ws/book/23623/1381")], naissance=1173),

 E(27, "Siddiq Khân Ben Hassan El Qinnawdjî", 1307, "Fethoul Bayân fî Maqâssidil Qour'ân", [
   C("s50 v7 · s15 v19", "C'est-à-dire aplanie et étalée sur la surface de l'eau, comme dans Sa parole « Et quant à la terre, après cela, Il l'a étendue » (s79 v30), et dans Sa parole « Et la terre, Nous l'avons étendue. Et de quelle excellente façon Nous l'avons nivelée ! » (s51 v48). Il y a en cela une réplique contre ceux qui prétendent qu'elle est sphérique.",
     "7", "157", "https://shamela.ws/book/37458/42666"),
   C("s2 v22", "Al-firāš est un lit sur lequel ils reposent, et la plupart des commentateurs l'ont utilisé comme preuve que la forme de la terre est plate et non sphérique.",
     "1", "104", "https://shamela.ws/book/37458/130"),
   C("s13 v3", "Cette apparente étendue constatée par la vision ne contredit pas sa sphéricité en elle-même, du fait de l'éloignement de ses bords, et c'est ce que soutiennent les membres du comité. Allāh nous informe qu'Il a étendu la terre, qu'Il l'a aplanie et étalée, et qu'Il en a fait un tapis, et tout ceci indique qu'elle est plate.",
     "7", "12", "https://shamela.ws/book/37458/4015#p1",
     "cette troisième citation rapporte l'argument de la conciliation avant de le récuser : à citer entière, sans quoi elle est retournable")], naissance=1248),

 E(28, "Mohammed Abderrahmân El Moubârakfoûrî", 1353, "Touhfatoul Ahwadhî bi Sharh Djâmiʿit-Tirmidhî", [
   C(None, "J'ai dit que s'il voulait dire par sa parole « la terre est sphérique à l'unanimité » que les imams de la religion parmi les prédécesseurs et les successeurs sont d'accord sur sa sphéricité, alors c'est faux sans aucun doute. Mais s'il visait l'unanimité des philosophes et des gens de la commission astronomique, alors c'est quelque chose dont nous ne devons pas prêter attention.",
     "1", "424", "https://shamela.ws/book/21662/422")], naissance=1283),

 E(29, "Mouhammed Ben Youssouf El Kâfî Et-Tounsi", 1353, "El Massâîloul Kâfiyyah", [
   C(None, "Sur le fait qu'Allāh aurait fait de la terre une sphère, il n'y a absolument aucun verset du Coran pour appuyer cela.",
     None, "70", "https://dlib.nyu.edu/files/books/columbia_aco001329/columbia_aco001329_lo.pdf")], naissance=1278),

 E(30, "Mouhammed El Moukhtâr Es-Soûssî", 1383, "El Ilghiyât, éd. Dār al-Kutub al-ʿIlmiyya", [
   C("s50 v7 · s15 v19 · s79 v30", "Si vous sous-entendez par le terme « sphère » que la terre est entourée par le falak comme le halo entoure la lune, alors nous ne le nions pas ; sauf que nous disons en plus de cela que sa surface est plane, nivelée et étendue, avec une largeur et une longueur, d'après les textes du Coran.",
     "3", "51", None, "aucun lien dans le document source : grade B")]),
]

def grade(c):
    if c["url"] and "shamela.ws" in c["url"]: return "A"
    if c["volume"] and c["page"]: return "B"
    if c["page"] or c["url"]: return "C"
    return "D"

for s in SAVANTS:
    for c in s["citations"]:
        c["grade"] = "D" if not c["citation"] else grade(c)

tot = sum(len(s["citations"]) for s in SAVANTS)
complets = sum(1 for s in SAVANTS for c in s["citations"] if c["citation"])
g = collections.Counter(c["grade"] for s in SAVANTS for c in s["citations"])

doc = {"_meta": {
  "titre": "Autorités citées sur la forme de la Terre",
  "source_unique": ("content/sources/brut/PAROLES_DE_SAVANTS_DE_DIVERSES_EPOQUES,"
                    "_SUR_LA_FORME_DE_LA_TERRE.pdf — transcrit à la main, entrée par entrée"),
  "regles_de_transcription": [
    "Aucune référence n'est complétée, devinée ni corrigée en silence.",
    "Les incertitudes du document source sont signalées dans _incertitude.",
    "Le grade dit ce que la référence permet de VÉRIFIER, non la réputation de l'auteur.",
    "Une citation dont le texte n'a pas été capté à l'extraction est conservée avec son URL et marquée à reprendre."],
  "grades": {"A": "lien direct vers la page de l'ouvrage (shamela)",
             "B": "volume et page, sans lien direct",
             "C": "page seule, ou lien vers un dépôt non paginé",
             "D": "texte à reprendre : entrée incomplète dans l'extraction"},
  "savants": len(SAVANTS), "citations": tot, "citations_transcrites": complets,
  "repartition_des_grades": dict(g),
  "amplitude": f"{SAVANTS[0]['mort_H']} H – {SAVANTS[-1]['mort_H']} H",
  "genere_par": "scripts/generer-savants.py"},
  "savants": SAVANTS}

with open('content/bibliotheque/savants-forme-terre.json', 'w', encoding='utf-8') as f:
    json.dump(doc, f, ensure_ascii=False, indent=2); f.write("\n")

print(f"{len(SAVANTS)} savants · {tot} citations · {complets} transcrites")
print("grades :", dict(g))
print("incertitudes signalées :",
      sum(1 for s in SAVANTS if s['_incertitude']) + sum(1 for s in SAVANTS for c in s['citations'] if c['_incertitude']))


# ═══════════════════════════════════════════════════════════════════════════
# Section d'article : le noyau verifiable, insere sans toucher aux tableaux
# existants des 95 autorites.
# ═══════════════════════════════════════════════════════════════════════════
import html as _html

def esc(s): return _html.escape(s, quote=False) if s else ""

BADGE = {"A": "grade-a", "B": "grade-b", "C": "grade-c", "D": "grade-d"}

lignes = []
for s in SAVANTS:
    for i, c in enumerate(s["citations"]):
        if not c["citation"]:
            continue
        loc = " ".join(x for x in [f"vol. {c['volume']}" if c['volume'] else None,
                                   f"p. {c['page']}" if c['page'] else None] if x) or "—"
        lien = (f'<a href="{c["url"]}" rel="nofollow noopener" target="_blank">voir la page</a>'
                if c["url"] else "—")
        nom = f"{esc(s['nom'])}" if i == 0 else '<span class="tei-idem">idem</span>'
        mort = f"m. {s['mort_H']} H" if i == 0 else ""
        note = (f'<br><em class="tei-reserve">{esc(c["_incertitude"])}</em>'
                if c["_incertitude"] else "")
        lignes.append(
          f"<tr><td>{s['n']}</td><td>{nom}<br><small>{mort}</small></td>"
          f"<td>{esc(c['verset']) or '—'}</td>"
          f"<td>{esc(s['ouvrage']) or '—'}{note}</td>"
          f"<td>{loc}</td>"
          f"<td><span class=\"tei-grade {BADGE[c['grade']]}\">{c['grade']}</span></td>"
          f"<td>{lien}</td></tr>")

nA = g["A"]; nAB = g["A"] + g["B"]
section = f"""<h2 id="noyau-verifiable"><span class="tei-section-num">12</span>Le noyau vérifiable : {complets} citations que vous pouvez contrôler</h2>
<p>Les sections précédentes recensent quatre-vingt-quinze autorités. Cette section ne les remplace pas : elle isole celles dont la référence est <strong>aujourd'hui vérifiable</strong>, ouvrage, volume, page et lien direct vers la page numérisée.</p>
<p>Elles sont <strong>{len(SAVANTS)} savants, de {SAVANTS[0]['mort_H']} H à {SAVANTS[-1]['mort_H']} H</strong> — un millénaire — pour {complets} citations transcrites. <strong>{nA} portent un lien direct</strong> vers la page de l'ouvrage sur shamela.ws : un clic suffit à contrôler.</p>
<p>Le reste des quatre-vingt-quinze attend le même traitement. Nous le disons plutôt que de laisser croire à une vérification qui n'a pas eu lieu.</p>
<div class="tei-enclair"><span class="tei-enclair-label">En clair</span>
<p>Une citation, ça se vérifie en trois temps : qui l'a dite, dans quel livre, et à quelle page. Sans la page, il faut lire trente volumes pour contrôler — autant dire que personne ne contrôle. La colonne de droite de ce tableau évite ce problème : elle ouvre directement la page numérisée. Vous n'avez pas à nous croire.</p></div>
<h3>Comment lire la colonne « grade »</h3>
<p>Le grade dit ce que la référence permet de <em>vérifier</em>, pas la réputation de l'auteur. C'est la même grille que celle appliquée aux mesures physiques ailleurs sur ce site.</p>
<table class="tei-table">
<thead><tr><th>Grade</th><th>Ce que porte la référence</th><th>Nombre</th></tr></thead>
<tbody>
<tr><td><span class="tei-grade grade-a">A</span></td><td>Lien direct vers la page de l'ouvrage numérisé</td><td>{g['A']}</td></tr>
<tr><td><span class="tei-grade grade-b">B</span></td><td>Volume et page, sans lien direct</td><td>{g['B']}</td></tr>
<tr><td><span class="tei-grade grade-c">C</span></td><td>Page seule, ou lien vers un dépôt non paginé</td><td>{g['C']}</td></tr>
</tbody></table>
<h3>Le tableau</h3>
<div class="table-scroll-wrapper">
<table class="tei-table tei-savants">
<thead><tr><th>#</th><th>Autorité</th><th>Verset</th><th>Ouvrage</th><th>Localisation</th><th>Grade</th><th>Contrôle</th></tr></thead>
<tbody>{''.join(lignes)}</tbody>
</table>
</div>
<h3>Ce que ce tableau montre, et ce qu'il ne montre pas</h3>
<p>Il montre que la lecture de la planéité n'est pas une invention récente : elle est portée, verset à l'appui, sur onze siècles, par des exégètes qui se citent les uns les autres. Plusieurs opposent explicitement les <em>ʿulamāʾ al-šarʿ</em> aux <em>ahl al-hayʾa</em>, les savants de la Loi aux gens de l'astronomie — c'est-à-dire qu'ils savaient parfaitement qu'un autre avis existait, et qu'ils le situaient hors de leur discipline.</p>
<p>Il ne montre pas que la question soit close. Deux entrées vont dans un autre sens et sont conservées telles quelles : <strong>al-Sāwī</strong> (m. 1241 H) écrit que la terre fut créée sphérique <em>puis</em> aplanie après la création des cieux, et <strong>al-Qinnawjī</strong> (m. 1307 H) rapporte l'argument de conciliation — l'étendue apparente ne contredirait pas la sphéricité, vu l'éloignement des bords — avant de le récuser. Les retirer serait fabriquer une unanimité que les sources ne donnent pas.</p>
<div class="tei-fait library"><span class="tei-fait-label">CE QUE LE TEXTE ÉTABLIT</span>
<p>{len(SAVANTS)} autorités, de {SAVANTS[0]['mort_H']} H à {SAVANTS[-1]['mort_H']} H, portent la lecture de la planéité avec référence d'ouvrage. {nA} de ces citations ouvrent directement la page numérisée. Le jeu de données complet, avec ses {sum(1 for s in SAVANTS if s['_incertitude']) + sum(1 for s in SAVANTS for c in s['citations'] if c['_incertitude'])} réserves de transcription signalées, est versionné dans <code>content/bibliotheque/savants-forme-terre.json</code>.</p></div>
"""

art_path = 'content/articles/pres-de-cent-savants-de-lislam.json'
art = json.load(open(art_path, encoding='utf-8'))
h = art['htmlBody']
anc = '<h2 id="sources">'
i = h.find(anc)
assert i > 0, "section Sources introuvable"
# Idempotence : si la section a déjà été posée, on la remplace. Sans cela, une
# seconde exécution empilait un deuxième exemplaire et cassait la numérotation.
deja = h.find('<h2 id="noyau-verifiable">')
if deja >= 0:
    h = h[:deja] + section + h[i:]
else:
    h = h[:i] + section + h[i:]
    # la section Sources passe de 12 à 13
    h = re.sub(r'(<h2 id="sources"><span class="tei-section-num">)12(</span>)',
               r'\g<1>13\g<2>', h)
art['htmlBody'] = h
art['updated'] = '2026-08-06'
json.dump(art, open(art_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
open(art_path, 'a', encoding='utf-8').write('\n')

mots = len(re.sub('<[^>]+>', ' ', h).split())
print(f"\narticle mis à jour — {mots} mots, {h.count('<table')} tableaux, "
      f"{len(lignes)} lignes dans la table des autorités")
