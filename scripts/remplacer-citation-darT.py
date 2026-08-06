#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remplace, dans « D'une Terre plate universelle à la sphère grecque », la
reformulation prêtée à Ibn Taymiyya par le texte du Darʾ Taʿāruḍ 1/120.

Ce qui était en place :

    « Quiconque élève la parole des philosophes grecs au-dessus du Coran et de
      la Sunna a commis une grave erreur. »
    — Ibn Taymiyyah, Darʾ Taʿāruḍ al-ʿAql wa-l-Naql

Français seul, sans arabe, formulation générale, et aucune correspondance mot
pour mot avec un texte d'Ibn Taymiyya de notre fonds. Vraisemblablement une
reformulation présentée comme une citation.

Ce qui la remplace : le passage du Darʾ Taʿāruḍ 1/120, en arabe et en
traduction, tel qu'il figure dans le dossier « Réfutation du concordisme
cosmologique » déposé dans content/sources/brut/. Trois passages du même
ouvrage, dont celui-ci, sont déjà cités dans l'article « Le concordisme ».

Le texte de remplacement énonce la règle générale de primauté du naql sur le
ʿaql — il ne nomme pas les philosophes grecs. Le paragraphe d'introduction est
donc réécrit en conséquence : l'article ne doit pas faire dire au texte plus
qu'il ne dit. C'est le prix de la substitution, et il vaut mieux le payer qu'une
citation invérifiable.
"""

import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN = os.path.join(RACINE, "content", "articles",
                      "dune-terre-plate-universelle-a-la-sphere-grecque.json")

AVANT = """<p>Ibn Taymiyyah (1263–1328), imam hanbalite et l'une des figures intellectuelles majeures de l'islam sunnite, systématise cette position :</p>
<blockquote class="tei-citation"><p>« Quiconque élève la parole des philosophes grecs au-dessus du Coran et de la Sunna a commis une grave erreur. »</p><footer>— Ibn Taymiyyah, <em>Darʾ Taʿāruḍ al-ʿAql wa-l-Naql</em> <em>(à vérifier — texte non retrouvé dans nos sources)</em></footer></blockquote>"""

APRES = """<p>Ibn Taymiyyah (m. 728 H / 1328), imam hanbalite et l'une des figures intellectuelles majeures de l'islam sunnite, ne traite pas la question au cas par cas : il pose la règle générale dont le cas grec n'est qu'une application.</p>
<blockquote class="tei-citation arabic-quote">
<p><span class="tei-arabic">وإذا تعارض العقل الصريح والنقل الصحيح وجب تقديم النقل، فإن العقل يعلم صدق الرسول بالنقل، والنقل هو الذي دل على صحة العقل، فصار تقديم العقل على النقل قدحًا في العقل والنقل جميعًا.</span></p>
<p>« Et lorsque la raison claire et la transmission saine s'opposent, il faut donner la primauté à la transmission — car c'est par la transmission que la raison connaît la véracité du Messager, et c'est la transmission qui a établi la validité de la raison. Donner la primauté à la raison sur la transmission revient donc à récuser la raison et la transmission ensemble. »</p>
<footer>— Ibn Taymiyyah, <em>Darʾ Taʿāruḍ al-ʿAql wa-l-Naql</em>, 1/120</footer></blockquote>
<p>L'argument n'est pas un refus de la raison, et il faut le lire précisément : Ibn Taymiyyah soutient que subordonner la Révélation à une construction rationnelle scie la branche sur laquelle cette construction est assise, puisque c'est la Révélation qui garantit la validité de l'instrument. La règle vaut pour la cosmologie grecque comme pour toute autre théorie humaine — mais elle est énoncée comme règle, et l'article ne lui fait pas dire davantage.</p>"""


def main():
    with open(CHEMIN, encoding="utf-8") as f:
        data = json.load(f)
    html = data["htmlBody"]

    if "1/120" in html:
        print("  ✓ la substitution est déjà en place")
        return 0
    if AVANT not in html:
        print("  ✗ le passage à remplacer est introuvable")
        return 1

    data["htmlBody"] = html.replace(AVANT, APRES, 1)
    data["updated"] = "2026-08-06"
    with open(CHEMIN, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("  ✓ reformulation remplacée par Darʾ Taʿāruḍ 1/120, arabe et traduction")
    return 0


if __name__ == "__main__":
    sys.exit(main())
