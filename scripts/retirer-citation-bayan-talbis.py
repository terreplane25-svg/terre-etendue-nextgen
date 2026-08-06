#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retire du « consensus sur la sphéricité » la citation du Bayān Talbīs
al-Jahmiyya, invérifiable.

Le passage était donné en français seul, sans texte arabe, sans volume ni page,
dans une formulation générale, et nous ne l'avons retrouvé dans aucune de nos
sources. Contrairement à la citation du Darʾ Taʿāruḍ traitée le même jour, notre
fonds ne contient aucun substitut du même auteur sur le même point. La règle du
site s'applique : en cas de doute, retirer plutôt que sourcer approximativement.

Le retrait n'est pas une simple suppression de bloc. Trois endroits en
dépendaient et sont repris :

  · la phrase d'annonce, « Et dans Bayān Talbīs al-Jahmiyya, il formule
    explicitement : », qui resterait suspendue ;
  · le paragraphe de conclusion de l'axe, dont la première proposition —
    « Ibn Taymiyyah rejette explicitement l'autorité doctrinale des cosmologues
    grecs » — ne reposait que sur la citation retirée ;
  · le point 5 de la synthèse finale, pour la même raison.

L'axe survit au retrait, plus étroit : il tient désormais au seul passage du
Majmūʿ al-Fatāwā 6/357, qui est référencé, et qui suffit à établir qu'Ibn
Taymiyyah emploie de sa propre plume le vocabulaire coranique de l'étendue dans
le volume même où figure le consensus contesté.

Le script corrige au passage le lede, qui annonçait « cinq axes » alors que
l'article en compte sept depuis la refonte de l'étape 3.
"""

import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN = os.path.join(RACINE, "content", "articles",
                      "le-consensus-sur-la-sphericite.json")

# ── 1. l'annonce et la citation ─────────────────────────────────────────────
BLOC = """<p>Et dans <em>Bayān Talbīs al-Jahmiyyah</em>, il formule explicitement :</p>
<blockquote class="tei-citation"><p>« La parole d'aucun d'entre eux [les cosmologues grecs] n'est une preuve, et il n'est pas permis de bâtir sur elle un fondement de la religion. »</p><footer>— Ibn Taymiyyah, <em>Bayān Talbīs al-Jahmiyya</em> <em>(à vérifier — texte non retrouvé dans nos sources)</em></footer></blockquote>
"""

# ── 2. le paragraphe qui s'appuyait dessus ──────────────────────────────────
PARA_AVANT = """<p>Ibn Taymiyyah rejette explicitement l'autorité doctrinale des cosmologues grecs, tout en rapportant — si le passage est authentique — un « consensus » dont le contenu provient directement de cette tradition. Il utilise <em>basaṭa</em>, <em>mihādan</em>, <em>firāshan</em> — les mêmes termes coraniques de planéité — pour décrire la Terre de sa propre plume.</p>"""

PARA_APRES = """<p>Le point tient à ce seul passage, et ce seul passage suffit : dans le volume même où figure le « consensus » contesté, Ibn Taymiyyah décrit la Terre de sa propre plume avec <em>basaṭa</em>, <em>mihādan</em> et <em>firāshan</em> — les termes coraniques de l'étendue. Il rapporte donc un accord dont le contenu vient de la cosmographie grecque, et emploie, quand il parle en son nom, le vocabulaire de la Révélation.</p>

<div class="tei-infobox">
<p><strong>Retrait d'une citation, 6 août 2026.</strong> Cette section en citait une seconde, tirée du <em>Bayān Talbīs al-Jahmiyya</em>, sur le refus de faire des cosmologues grecs une autorité doctrinale. Nous l'avons retirée : elle était donnée en français seul, sans texte arabe, sans volume ni page, et nous ne l'avons retrouvée dans aucune de nos sources. Notre règle est de retirer plutôt que de sourcer approximativement. L'argument de cette section repose désormais sur le seul passage que nous pouvons produire — ce qui la rend plus étroite, et vérifiable.</p>
</div>"""

# ── 3. le point 5 de la synthèse ────────────────────────────────────────────
SYNTH_AVANT = ("<strong>5. Incohérence :</strong> Ibn Taymiyyah rejette l'autorité des Grecs "
               "et utilise le vocabulaire coranique de planéité dans ses propres écrits.")
SYNTH_APRES = ("<strong>5. Incohérence :</strong> dans le volume même où figure le passage, "
               "Ibn Taymiyyah emploie de sa propre plume le vocabulaire coranique de "
               "l'étendue — <em>basaṭa</em>, <em>mihādan</em>, <em>firāshan</em>.")

# ── 4. l'entrée de la bibliographie, devenue orpheline ──────────────────────
SOURCE_AVANT = "  <li>Ibn Taymiyyah. <em>Bayān Talbīs al-Jahmiyyah</em>, éd. Ibn Qāsim.</li>\n"

# ── 5. le lede annonçait cinq axes ; il y en a sept depuis l'étape 3 ────────
LEDE_AVANT = "Analyse en cinq axes."
LEDE_APRES = "Analyse en sept axes."


def main():
    with open(CHEMIN, encoding="utf-8") as f:
        data = json.load(f)
    html = data["htmlBody"]

    if "Retrait d'une citation" in html:
        print("  ✓ le retrait est déjà fait")
        return 0

    for nom, avant, apres in (("citation et annonce", BLOC, ""),
                              ("paragraphe de l'axe", PARA_AVANT, PARA_APRES),
                              ("point 5 de la synthèse", SYNTH_AVANT, SYNTH_APRES),
                              ("entrée de bibliographie", SOURCE_AVANT, ""),
                              ("lede", LEDE_AVANT, LEDE_APRES)):
        if avant not in html:
            print("  ✗ %s : motif introuvable" % nom)
            return 1
        if html.count(avant) > 1:
            print("  ✗ %s : motif trouvé %d fois, ambigu" % (nom, html.count(avant)))
            return 1
        html = html.replace(avant, apres, 1)
        print("  ✓ %s" % nom)

    # L'ouvrage reste nommé une fois — dans la note de transparence, qui
    # explique le retrait. Ce qui ne doit plus exister, c'est une CITATION :
    # aucun bloc de citation ni aucun pied ne doit plus le porter.
    import re as _re
    for bloc in _re.findall(r"<blockquote.*?</blockquote>", html, _re.S):
        if "Bayān Talbīs" in bloc:
            print("  ✗ un bloc de citation porte encore Bayān Talbīs")
            return 1
    for pied in _re.findall(r"<footer>.*?</footer>", html, _re.S):
        if "Bayān Talbīs" in pied:
            print("  ✗ un pied de citation porte encore Bayān Talbīs")
            return 1
    if html.count("Bayān Talbīs") != 1:
        print("  ✗ %d mentions de Bayān Talbīs, une seule attendue "
              "(la note de transparence)" % html.count("Bayān Talbīs"))
        return 1

    data["htmlBody"] = html
    data["updated"] = "2026-08-06"
    with open(CHEMIN, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
