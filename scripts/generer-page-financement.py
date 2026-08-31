#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Écrit la page « Soutenir le travail ».

Version courte, voulue comme telle. La première mouture chiffrait les campagnes
poste par poste, ouvrait un registre des versements et énonçait huit règles.
C'était juste et c'était trop&nbsp;: mettre un prix sur une expérience laisse
entendre qu'il faudrait payer pour qu'elle ait lieu, alors que chacun paie son
matériel, ici comme ailleurs, et que rien n'est conditionné à quoi que ce soit.

Ce qui reste tient en trois idées. Il y a du travail derrière ce site — de la
réflexion, du terrain, du temps, des dépenses. Un don est une reconnaissance de
ce travail, pas l'achat d'une prestation. Et il ne change rien à ce qui est
publié.

Le slug ne bouge pas : la page est déjà en ligne, liée depuis le pied de page,
le graphe et « Standards et méthode ». Changer l'adresse coûterait une
redirection pour rien.
"""
import json
import os

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "financement-et-independance"
CIBLE = os.path.join(RACINE, "content", "articles", SLUG + ".json")
KOFI = "https://ko-fi.com/terreetendue"

CORPS = """<p class="tei-lede">Tout ce que vous lisez ici est gratuit et le restera. Si ce travail vous paraît mériter un geste, il y a un bouton plus bas — et rien d'autre à faire.</p>

<h2 id="derriere" ><span class="tei-section-num">01</span>Ce qu'il y a derrière une page</h2>
<p>Un article de ce site n'est pas une opinion mise en forme. Derrière chacun, il y a des heures de lecture, des calculs refaits jusqu'à ce qu'ils retombent sur leurs pieds, des références retrouvées une par une, des sorties sur le terrain, du matériel, et le temps qu'il faut pour recommencer quand le résultat ne dit pas ce qu'on espérait. Ce travail est continu, il coûte, et il ne se voit pas depuis la page finie.</p>
<p>Nous menons nos propres mesures et nous publions les résultats quels qu'ils soient, exactement comme nous invitons chacun à le faire de son côté. Chacun paie son matériel&nbsp;: c'est la règle ici comme partout ailleurs, et elle ne changera pas.</p>

<h2 id="don"><span class="tei-section-num">02</span>Ce qu'un don est, et ce qu'il n'est pas</h2>
<p>Un don est une <strong>reconnaissance</strong> pour le travail accompli. Rien de plus, et c'est déjà beaucoup.</p>
<p>Ce n'en est pas le prix. Aucune expérience n'est mise en vente, aucun montant n'est demandé, aucun palier n'existe, aucune contrepartie n'est promise. Personne n'a à donner quoi que ce soit pour lire, pour utiliser un protocole, ou pour participer&nbsp;: tout est ouvert et le reste.</p>
<p>Et un don ne change pas une ligne de ce qui est publié. Ni ce qui est mesuré, ni ce qui est conclu, ni ce qui est corrigé quand nous nous sommes trompés. C'est la seule chose que ce site ait à offrir&nbsp;; elle n'est pas à vendre.</p>

<h2 id="contribuer"><span class="tei-section-num">03</span>Contribuer</h2>
<p style="margin:1.6rem 0"><a href="%(kofi)s" target="_blank" rel="noopener noreferrer" style="display:inline-block;padding:14px 30px;border-radius:8px;background:var(--gold);color:#fff;font-weight:700;text-decoration:none">Faire un don · Ko-fi</a></p>
<p>Il y a deux autres façons de contribuer, et elles valent au moins autant&nbsp;:</p>
<ul>
<li><strong>Exécuter un protocole.</strong> C'est ce qui manque le plus — voir <a href="/article/participer-aux-campagnes-de-mesure">Participer aux campagnes de mesure</a>.</li>
<li><strong>Signaler une erreur.</strong> Pointez la phrase et ce qui cloche&nbsp;: voir <a href="/article/corrections">Corrections et signalements</a>.</li>
</ul>
""" % {"kofi": KOFI}


def main():
    art = {
        "title": "Soutenir le travail",
        "description": (
            "Tout est gratuit et le restera. Un don est une reconnaissance pour "
            "le travail accompli — pas le prix d'une expérience, et rien qui "
            "change une ligne de ce qui est publié."),
        "date": "2026-08-31",
        "updated": "2026-08-31",
        "author": "Terre Etendue",
        "category": "meta",
        "tags": ["soutien", "dons", "independance", "transparence"],
        "pinned": False,
        "htmlBody": CORPS,
    }
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(art, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("écrit : %s (%d caractères)" % (os.path.relpath(CIBLE, RACINE), len(CORPS)))


if __name__ == "__main__":
    main()
