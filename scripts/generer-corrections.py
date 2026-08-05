#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genere content/articles/corrections.json depuis content/corrections/registre.json.

Ajouter une correction = ajouter une entree au registre, puis relancer ce script.
Les entrees ne sont jamais retirees ni reecrites : si une correction est elle-meme
corrigee, on ajoute une nouvelle entree.
"""
import json, collections, re

REG = json.load(open('content/corrections/registre.json', encoding='utf-8'))
E = sorted(REG['entrees'], key=lambda x: x['date'], reverse=True)
CAT = REG['categories']

LIB = {'fait': 'FAIT', 'methode': 'MÉTHODE', 'source': 'SOURCE',
       'technique': 'TECHNIQUE', 'conception': 'CONCEPTION'}

def fr(d):
    a, m, j = d.split('-')
    MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet',
            'août', 'septembre', 'octobre', 'novembre', 'décembre']
    return f"{int(j)} {MOIS[int(m) - 1]} {a}"

compte = collections.Counter(e['categorie'] for e in E)
graves = sum(1 for e in E if e.get('gravite') == 'haute')

lignes_cat = "".join(
    f"<tr><td><strong>{LIB[k]}</strong></td><td>{CAT[k]}</td><td>{compte.get(k, 0)}</td></tr>"
    for k in ['fait', 'methode', 'source', 'conception', 'technique'])

def bloc(e):
    grave = ' — <strong>correction de fond</strong>' if e.get('gravite') == 'haute' else ''
    return (
        '<div class="tei-correction">'
        f'<div class="tei-correction-tete"><span class="tei-correction-date">{fr(e["date"])}</span>'
        f'<span class="tei-correction-cat cat-{e["categorie"]}">{LIB[e["categorie"]]}</span></div>'
        f'<p class="tei-correction-ou">{e["ou"]}{grave}</p>'
        f'<p><strong>Ce qui était affirmé.</strong> {e["erreur"]}</p>'
        f'<p><strong>Ce qui l\'a remplacé.</strong> {e["correction"]}</p>'
        f'<p class="tei-correction-ref">Commit {e["commit"]}</p>'
        '</div>')

body = f"""
<p class="tei-lede">{len(E)} corrections consignées à ce jour, dont {graves} corrections de fond. Chacune est datée, décrit ce qui était affirmé et ce qui l'a remplacé, et renvoie au commit qui le prouve. Aucune entrée n'est jamais retirée.</p>

<h2 id="pourquoi">Pourquoi cette page existe</h2>
<p>Un site qui prétend appliquer un barème de preuve exigeant doit s'appliquer ce barème à lui-même. La façon la plus simple de le vérifier n'est pas de lire ce qu'il affirme, c'est de regarder <strong>ce qu'il fait de ses erreurs</strong>.</p>
<p>Les publications scientifiques le pratiquent depuis longtemps sous des noms précis — erratum, corrigendum, addendum, rétractation. Le principe est toujours le même : l'erreur reste visible après sa correction, sinon la correction ne vaut rien.</p>
<p>Ce registre applique ce principe. <strong>Une entrée n'est jamais supprimée ni réécrite.</strong> Si une correction se révèle elle-même fautive, une nouvelle entrée est ajoutée en dessous, et l'ancienne demeure.</p>
<p>Le dépôt du site étant public et versionné, chaque entrée renvoie à l'identifiant du commit qui l'a appliquée. N'importe qui peut vérifier que le texte a bien changé, dans quel sens, et à quelle date. Une correction silencieuse serait visible dans l'historique — c'est ce qui rend cet engagement contraignant plutôt que déclaratif.</p>

<h2 id="categories">Ce que nous appelons une correction</h2>
<table class="tei-table">
<thead><tr><th>Catégorie</th><th>Définition</th><th>Nombre</th></tr></thead>
<tbody>{lignes_cat}</tbody>
</table>
<p>Une coquille, une virgule ou une reformulation ne figurent pas ici. Est consigné ce qui change ce qu'un lecteur doit croire : un chiffre faux, un raisonnement fautif, une source absente ou mal attribuée, un défaut de conception dans un protocole proposé, ou un défaut d'affichage qui altérait la lecture.</p>
<p>Les corrections de <strong>conception</strong> méritent un mot. Elles portent sur des protocoles publiés mais pas encore exécutés. Les consigner malgré l'absence de mesure est délibéré : un protocole pré-enregistré ne vaut que si l'on voit aussi ce qu'il a fallu y reprendre avant la première séance.</p>

<h2 id="registre">Le registre</h2>
{"".join(bloc(e) for e in E)}

<h2 id="engagement">Engagement</h2>
<p>Toute erreur signalée et vérifiée est corrigée et consignée ici, quelle que soit sa portée pour la thèse du site. Les corrections qui vont contre nos conclusions sont traitées exactement comme les autres — plusieurs entrées ci-dessus en sont.</p>
<p>Pour signaler une erreur, la voie la plus efficace est de pointer l'affirmation exacte et la source qui la contredit. Une affirmation non sourcée peut être retirée sur simple constat ; une affirmation sourcée demande une source contraire.</p>
"""

art = {
  "title": "Registre des corrections",
  "description": (f"{len(E)} corrections consignées, dont {graves} de fond. Chacune est datée, décrit ce qui "
                  "était affirmé et ce qui l'a remplacé, et renvoie au commit qui le prouve. Aucune entrée "
                  "n'est jamais retirée."),
  "date": "2026-08-03",
  "updated": max(e['date'] for e in E),
  "author": "Terre Etendue",
  "category": "meta",
  "tags": ["corrections", "erratum", "transparence", "methode", "standards"],
  "pinned": False,
  "htmlBody": body.strip(),
}
with open('content/articles/corrections.json', 'w', encoding='utf-8') as fh:
    json.dump(art, fh, ensure_ascii=False, indent=2); fh.write("\n")
mots = len(re.sub('<[^>]+>', ' ', body).split())
print(f"corrections.json — {len(E)} entrées, {mots} mots, {graves} de gravité haute")
