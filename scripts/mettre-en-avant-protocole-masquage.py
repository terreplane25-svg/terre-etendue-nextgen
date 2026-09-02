#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Met le protocole de la portion masquée en avant sur la page des protocoles.

Pourquoi celui-ci et pas un autre
─────────────────────────────────
C'est le seul de la série qu'un lecteur puisse exécuter le week-end suivant avec
ce qu'il possède déjà. Les quatre autres demandent un ballon, un théodolite, un
mois lunaire ou une expédition ; celui-ci demande un appareil photo, un trépied
et un plan d'eau.

Il est aussi le seul dont la conclusion ne se discute pas par la météo, et
c'est ce qui justifie de le placer avant le tableau plutôt que dedans : à
40–50 km, voir la base de la cible exigerait un coefficient de réfraction de
0,98 à 0,99, quand un conduit atmosphérique — le mirage supérieur, le cas
extrême — correspond à 1,00.

Ce que le script fait
─────────────────────
  · copie le PDF dans public/protocoles/ pour qu'il soit servi ;
  · insère un encadré de mise en avant en tête de la section 07 ;
  · ajoute la ligne correspondante au tableau des protocoles ;
  · corrige la phrase d'introduction, qui annonçait deux documents arrêtés.

Il n'est pas idempotent : chaque ancre est vérifiée avant écriture.
"""
import json
import os
import shutil
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLE = os.path.join(RACINE, "content", "articles",
                       "les-protocoles-ce-que-c-est-et-pourquoi.json")
PDF_SOURCE = os.path.join(RACINE, "content", "protocoles", "pdf",
                          "Protocole-court-masquage.pdf")
PDF_PUBLIC = os.path.join(RACINE, "public", "protocoles",
                          "Protocole-portion-masquee.pdf")

ENCADRE = (
    '<div class="tei-fait experiences">\n'
    '<span class="tei-fait-label">LE PROTOCOLE &#192; FAIRE EN PREMIER</span>\n'
    '<p><strong>Portion masqu&#233;e d\'un objet &#233;loign&#233;.</strong> C\'est le '
    'seul de la s&#233;rie qu\'on puisse ex&#233;cuter le week-end prochain avec ce '
    'qu\'on poss&#232;de d&#233;j&#224;&#160;: un appareil photo &#224; long '
    'zoom, un tr&#233;pied, un plan d\'eau et une cible haute.</p>\n'
    '<p>Et c\'est le seul dont la conclusion ne se discute pas par la '
    'm&#233;t&#233;o. &#192; 40&#8211;50&#8239;km, voir la base de la cible exigerait '
    'un coefficient de r&#233;fraction de <strong>0,98 &#224; 0,99</strong>, quand un '
    'conduit atmosph&#233;rique &#8212; le mirage sup&#233;rieur, le cas le plus '
    'extr&#234;me qu\'on mesure &#8212; correspond &#224; 1,00. Il faudrait un '
    'r&#233;gime qui n\'existe pas.</p>\n'
    '</div>\n'
    '<p><a href="/protocoles/Protocole-portion-masquee.pdf"><strong>T&#233;l&#233;charger '
    'le protocole</strong></a> &#8212; bilingue fran&#231;ais et anglais, 12 pages, PDF. '
    'Il contient la grille de choix du site, le mat&#233;riel strictement '
    'n&#233;cessaire, la mise en place d&#233;taill&#233;e et une fiche de relev&#233; '
    'd\'une page &#224; imprimer.</p>\n'
    '<div class="tei-fait experiences">\n'
    '<span class="tei-fait-label">CE QUE L\'EXP&#201;RIENCE &#201;TABLIT</span>\n'
    '<p>Depuis 2&#8239;m de hauteur d\'&#339;il &#224; 40&#8239;km, une surface de '
    '6&#8239;371&#8239;km masque <strong>au minimum 42&#8239;m</strong> de la base de '
    'la cible &#8212; valeur calcul&#233;e sous l\'inversion thermique la plus forte '
    'jamais mesur&#233;e. La turbulence limite la lecture &#224; deux ou quatre '
    'm&#232;tres. <strong>Le rapport reste sup&#233;rieur &#224; dix dans le cas le '
    'plus d&#233;favorable.</strong></p>\n'
    '</div>\n'
)

LIGNE_TABLEAU = (
    '    <tr><td><strong>Portion masqu&#233;e d\'un objet &#233;loign&#233;</strong>'
    '</td><td>la hauteur masqu&#233;e &#224; la base d\'une cible, &#224; 40&#8211;50 km '
    'au-dessus d\'un plan d\'eau</td><td>bilingue</td><td>1.0</td>'
    '<td>publi&#233;, non d&#233;pos&#233;</td></tr>\n'
)


def remplacer(html, vieux, neuf, etiquette):
    if html.count(vieux) != 1:
        sys.exit("ancre « %s » vue %d fois — attendu 1."
                 % (etiquette, html.count(vieux)))
    return html.replace(vieux, neuf)


def main():
    if not os.path.exists(PDF_SOURCE):
        sys.exit("PDF absent : %s" % PDF_SOURCE)
    os.makedirs(os.path.dirname(PDF_PUBLIC), exist_ok=True)
    shutil.copy2(PDF_SOURCE, PDF_PUBLIC)

    with open(ARTICLE, encoding="utf-8") as f:
        data = json.load(f)
    html = data["htmlBody"]

    # 1. L'encadré de mise en avant, en tête de la section 07.
    ancre = ('<h2 id="les-protocoles"><span class="tei-section-num">07</span>'
             'Les protocoles</h2>\n')
    html = remplacer(html, ancre, ancre + ENCADRE, "titre de la section 07")

    # 2. La phrase d'introduction, qui ne compte plus juste.
    html = remplacer(
        html,
        "<p>Deux documents sont arrêtés. Deux autres sont gelés, et nous préférons "
        "le dire que laisser croire à un catalogue plus fourni qu'il ne l'est.</p>",
        "<p>Trois documents sont arrêtés. Deux autres sont gelés, et nous préférons "
        "le dire que laisser croire à un catalogue plus fourni qu'il ne l'est.</p>",
        "phrase d'introduction")

    # 3. La ligne du tableau, en tête de corps puisque c'est le plus accessible.
    ancre_tbody = "  <tbody>\n    <tr><td><strong>Dépression de l'horizon marin</strong>"
    html = remplacer(html, ancre_tbody,
                     "  <tbody>\n" + LIGNE_TABLEAU
                     + "    <tr><td><strong>Dépression de l'horizon marin</strong>",
                     "corps du tableau des protocoles")

    data["htmlBody"] = html
    with open(ARTICLE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("PDF servi   : public/protocoles/Protocole-portion-masquee.pdf (%d ko)"
          % (os.path.getsize(PDF_PUBLIC) // 1024))
    print("Article mis à jour : encadré de mise en avant, ligne de tableau, "
          "décompte corrigé")
    return 0


if __name__ == "__main__":
    sys.exit(main())
