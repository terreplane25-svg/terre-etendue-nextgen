#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Les six références islamiques du rapport de pagination : reclassement.

shamela.ws est refusé par la politique réseau de l'environnement d'exécution,
au même titre que l'ensemble du web général. Aucune des six paginations ne peut
donc être relevée ici. En cherchant dans nos propres fonds avant de conclure,
deux d'entre elles se sont révélées ne pas relever de la pagination du tout.

  · Ibn Taymiyya, Darʾ Taʿāruḍ al-ʿAql wa-l-Naql, dans « D'une Terre plate
    universelle à la sphère grecque » ;
  · Ibn Taymiyya, Bayān Talbīs al-Jahmiyya, dans « Le consensus sur la
    sphéricité ».

Ces deux passages sont donnés en français seul, sans texte arabe, dans une
formulation générale, et ne correspondent mot pour mot à aucun des textes
d'Ibn Taymiyya que nous détenons — alors que notre fonds en contient quatre,
verbatim et référencés (Darʾ Taʿāruḍ 1/120, 1/152, 1/154 et 7/285), portant
exactement sur le même thème. Il est vraisemblable qu'il s'agisse de
reformulations et non de citations. On ne pagine pas une reformulation : on la
vérifie, ou on la remplace.

Leur marqueur passe donc de « à paginer » à « à vérifier — texte non retrouvé
dans nos sources », qui est ce que nous savons réellement.

Le script ajoute par ailleurs une réserve philologique sur le rapport de Mālik
concernant l'istiwāʾ, dont la forme que nous donnons n'est pas celle que les
recueils transmettent le plus souvent.
"""

import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(RACINE, "content", "articles")

RECLASSEMENTS = [
    ("dune-terre-plate-universelle-a-la-sphere-grecque",
     "— Ibn Taymiyyah, Darʾ Taʿāruḍ al-ʿAql wa al-Naql <em>(à paginer)</em>",
     "— Ibn Taymiyyah, <em>Darʾ Taʿāruḍ al-ʿAql wa-l-Naql</em> "
     "<em>(à vérifier — texte non retrouvé dans nos sources)</em>"),
    ("le-consensus-sur-la-sphericite",
     "— Ibn Taymiyyah, Bayān Talbīs al-Jahmiyyah <em>(à paginer)</em>",
     "— Ibn Taymiyyah, <em>Bayān Talbīs al-Jahmiyya</em> "
     "<em>(à vérifier — texte non retrouvé dans nos sources)</em>"),
]

# ── La réserve sur le rapport de Mālik ──────────────────────────────────────
# L'article donne la forme « al-istiwāʾ maʿlūm wa-l-kayf majhūl ». Les recueils
# transmettent le plus souvent « ghayr majhūl … ghayr maʿqūl », et le propos est
# rapporté tantôt de Mālik, tantôt de son maître Rabīʿa. Nous rapportons la
# forme de notre source et signalons l'écart, sans trancher.
MALIK_ANCRE = ("<p>Cette réponse est le modèle de la méthode : on affirme le fond, "
               "on suspend le jugement sur la modalité, on refuse l'enquête sur ce qui "
               "dépasse la portée humaine.")

MALIK_RESERVE = """<p><strong>Deux réserves philologiques, à vérifier sur l'édition.</strong> La forme que nous donnons — <em>al-istiwāʾ maʿlūm wa-l-kayf majhūl</em> — est celle de notre source, et c'est la plus répandue dans l'usage contemporain. Les recueils anciens transmettent le plus souvent une formulation voisine mais distincte : <span class="tei-arabic">الاستواء غير مجهول والكيف غير معقول</span>, « l'<em>istiwāʾ</em> n'est pas inconnu, et la modalité n'est pas saisissable par la raison ». Par ailleurs, le propos est rapporté tantôt de Mālik, tantôt de son maître Rabīʿa al-Raʾy. Nous rapportons ce que porte notre source et signalons l'écart, plutôt que de trancher une question d'établissement du texte que nous n'avons pas les moyens de trancher ici.</p>

"""


def main():
    faits = []
    for slug, avant, apres in RECLASSEMENTS:
        chemin = os.path.join(ARTICLES, slug + ".json")
        with open(chemin, encoding="utf-8") as f:
            data = json.load(f)
        if apres in data["htmlBody"]:
            continue
        if avant not in data["htmlBody"]:
            print("  ✗ %s : marqueur introuvable — %r" % (slug, avant[:60]))
            return 1
        data["htmlBody"] = data["htmlBody"].replace(avant, apres, 1)
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        faits.append(slug)

    chemin = os.path.join(ARTICLES, "ou-est-allah-le-uluww-et-la-forme-du-monde.json")
    with open(chemin, encoding="utf-8") as f:
        data = json.load(f)
    if "Deux réserves philologiques" not in data["htmlBody"]:
        if MALIK_ANCRE not in data["htmlBody"]:
            print("  ✗ ancre de la réserve Mālik introuvable")
            return 1
        i = data["htmlBody"].index(MALIK_ANCRE)
        j = data["htmlBody"].index("</p>", i) + 4
        data["htmlBody"] = (data["htmlBody"][:j] + "\n\n" + MALIK_RESERVE
                            + data["htmlBody"][j:].lstrip("\n"))
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        faits.append("ou-est-allah — réserve philologique sur le rapport de Mālik")

    for x in faits:
        print("  ✓ %s" % x)
    if not faits:
        print("  ✓ rien à faire, tout est déjà en place")
    return 0


if __name__ == "__main__":
    sys.exit(main())
