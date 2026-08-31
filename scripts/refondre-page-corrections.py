#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refond la page des corrections : le registre détaillé sort, la porte reste.

La page publiait soixante-quatorze entrées décrivant, une par une, ce que nous
avions écrit de faux et ce qui l'a remplacé. La décision est prise de ne plus
exposer ce détail : le principe reste — le site est relu et corrigé en
permanence — mais l'inventaire de nos propres reprises n'a pas à être la
première chose qu'un lecteur trouve.

Les entrées ne sont pas détruites. Elles sont déplacées dans
`content/corrections/registre-archive.json`, qui n'est servi par aucune route :
le dossier `content/corrections/` est un dossier de travail, comme
`content/protocoles/`. L'historique git les conserve de toute façon.

Ce que la page devient : ce qu'on appelle une erreur, comment en signaler une,
et l'endroit où les signalements traités apparaîtront. Cet endroit est vide, et
la page le dit plutôt que de faire semblant.
"""
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(RACINE, "content", "articles", "corrections.json")
ARCHIVE = os.path.join(RACINE, "content", "corrections", "registre-archive.json")

CORPS = """<p class="tei-lede">Ce site est relu, recalculé et corrigé en permanence. Cette page dit ce que nous appelons une erreur, comment nous en signaler une, et c'est ici que les signalements traités apparaîtront.</p>

<h2 id="pourquoi">Pourquoi cette page existe</h2>
<p>Un site qui prétend appliquer un barème de preuve exigeant doit s'appliquer ce barème à lui-même. La façon la plus simple de le vérifier n'est pas de lire ce qu'il affirme, c'est de regarder <strong>ce qu'il fait de ses erreurs</strong>.</p>
<p>Le corpus fait l'objet de contrôles réguliers&nbsp;: les valeurs numériques sont recalculées depuis leurs formules, les références sont revérifiées, et les raisonnements sont repris. Ce travail est continu et il n'a pas de fin prévue. Quand il fait apparaître un défaut, l'article est corrigé.</p>
<p>Les publications scientifiques pratiquent cela depuis longtemps sous des noms précis — erratum, corrigendum, addendum, rétractation. Le principe est toujours le même&nbsp;: une correction n'a de valeur que si elle est réelle, et non si elle est annoncée.</p>
<p>Le dépôt du site est public et versionné. Chaque modification y est datée et attribuée&nbsp;: une correction silencieuse serait visible dans l'historique. C'est ce qui rend cet engagement contraignant plutôt que déclaratif.</p>

<h2 id="categories">Ce que nous appelons une erreur</h2>
<p>Une coquille, une virgule ou une reformulation n'en sont pas. Est traité comme une erreur <strong>ce qui change ce qu'un lecteur doit croire</strong>&nbsp;:</p>
<table class="tei-table">
<thead><tr><th>Catégorie</th><th>Définition</th></tr></thead>
<tbody>
<tr><td><strong>FAIT</strong></td><td>Une erreur de fait ou de chiffre dans un article publié.</td></tr>
<tr><td><strong>MÉTHODE</strong></td><td>Une erreur de méthode&nbsp;: le raisonnement lui-même est fautif, ou une grandeur est employée à la place d'une autre.</td></tr>
<tr><td><strong>SOURCE</strong></td><td>Une source mal citée, mal attribuée, ou absente là où une affirmation en exigeait une.</td></tr>
<tr><td><strong>CONCEPTION</strong></td><td>Un défaut dans un protocole ou un dispositif proposé, avant toute mesure.</td></tr>
<tr><td><strong>TECHNIQUE</strong></td><td>Un défaut d'affichage ou de rendu qui altère la lecture.</td></tr>
</tbody>
</table>
<p>Les défauts de <strong>conception</strong> méritent un mot. Ils portent sur des protocoles publiés mais pas encore exécutés. Les traiter malgré l'absence de mesure est délibéré&nbsp;: un protocole préenregistré ne vaut que si l'on reprend aussi ce qui doit l'être avant la première séance.</p>

<h2 id="signaler">Signaler une erreur</h2>
<p>C'est la contribution la plus utile qu'on puisse nous apporter, et elle est ouverte à tous — y compris, et surtout, à qui ne partage pas nos conclusions.</p>
<p>La voie la plus efficace est de <strong>pointer l'affirmation exacte et la source qui la contredit</strong>. Une affirmation non sourcée peut être retirée sur simple constat. Une affirmation sourcée demande une source contraire. Un désaccord d'interprétation, lui, n'est pas une erreur&nbsp;: il peut donner lieu à un ajout contradictoire dans l'article, signé et daté.</p>
<p>S'il s'agit d'un calcul, indiquez la formule employée et les valeurs d'entrée. La plupart des grandeurs du site — hauteur masquée, flèche de corde, dépression de l'horizon — dépendent d'un paramètre qu'on oublie facilement, comme la hauteur d'œil de l'observateur&nbsp;; le désaccord vient souvent de là, et il se lève en deux lignes.</p>
<div class="tei-enclair">
  <span class="tei-enclair-label">En clair</span>
  <p>Vous avez trouvé un chiffre faux, une citation mal attribuée, une formule qui ne retombe pas sur son propre exemple&nbsp;? Écrivez-nous en donnant la page, la phrase et ce qui cloche. C'est traité, et si c'en est une, c'est corrigé.</p>
</div>

<h2 id="signalements">Les signalements traités</h2>
<p>Cette section recueillera les signalements extérieurs que nous aurons vérifiés, avec leur date, ce qui était affirmé et ce qui l'a remplacé.</p>
<div class="tei-data"><strong>Aucun signalement extérieur à ce jour.</strong><br/>La section est vide parce que rien n'a encore été signalé, et non parce que rien n'y serait porté.</div>

<h2 id="engagement">Engagement</h2>
<p>Toute erreur signalée et vérifiée est corrigée, quelle que soit sa portée pour la thèse du site. Une correction qui va contre nos conclusions est traitée exactement comme une autre&nbsp;: c'est le seul engagement de cette page, et c'est le seul qui compte.</p>
"""


def main():
    with open(PAGE, encoding="utf-8") as f:
        art = json.load(f)
    ancien = art["htmlBody"]

    entrees = re.findall(r'<div class="tei-correction">.*?</div>\s*(?=<div class="tei-correction">|<h2|$)',
                         ancien, re.S)
    if len(entrees) < 60:
        sys.exit("Seulement %d entrées retrouvées ; le registre en comptait "
                 "soixante-quatorze. Rien n'est écrit." % len(entrees))

    os.makedirs(os.path.dirname(ARCHIVE), exist_ok=True)
    with open(ARCHIVE, "w", encoding="utf-8") as f:
        json.dump({
            "note": ("Registre des corrections tel qu'il était publié jusqu'au "
                     "31 août 2026. Retiré de la page publique ce jour-là : le "
                     "principe reste, le détail de nos propres reprises n'est "
                     "plus exposé. Conservé ici, et dans l'historique git."),
            "retire_le": "2026-08-31",
            "entrees": entrees,
        }, f, ensure_ascii=False, indent=2)
        f.write("\n")

    art["title"] = "Corrections et signalements"
    art["description"] = (
        "Ce que nous appelons une erreur, comment nous en signaler une, et où "
        "les signalements vérifiés apparaissent. Le corpus est relu et recalculé "
        "en permanence.")
    art["updated"] = "2026-08-31"
    art["htmlBody"] = CORPS

    with open(PAGE, "w", encoding="utf-8") as f:
        json.dump(art, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("%d entrées archivées dans %s" % (len(entrees), os.path.relpath(ARCHIVE, RACINE)))
    print("page réécrite : %d caractères au lieu de %d" % (len(CORPS), len(ancien)))


if __name__ == "__main__":
    main()
