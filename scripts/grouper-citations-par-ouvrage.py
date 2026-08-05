#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regroupe les citations a localiser PAR OUVRAGE, et non par article.

Motif : les memes ouvrages reviennent dans plusieurs articles. Travailler par
ouvrage permet de n'ouvrir chaque volume qu'une fois. Le fichier produit sert
de feuille de saisie : chaque citation a un emplacement vide a remplir.
"""
import json, re, collections

SRC = json.load(open('content/corrections/citations-a-localiser.json', encoding='utf-8'))

def cle(att):
    """Normalise l'attribution pour regrouper « — Tafsīr al-Ṭabarī » et variantes."""
    a = re.sub(r'^[—–-]\s*', '', att).strip()
    a = re.sub(r'\s*\([^)]*\)\s*$', '', a)
    a = re.sub(r',.*$', '', a)
    return a.strip()

groupes = collections.defaultdict(list)
for c in SRC['citations']:
    groupes[cle(c['attribution'])].append(c)

# les ouvrages arabes d'abord : ils sont sur shamela, donc les plus rapides a faire
def arabe(nom):
    return bool(re.search(r'Tafsīr|Ṣaḥīḥ|Ibn |al-|Al-|Musnad|Sunan|Fatāwā|Sourate', nom))

ordre = sorted(groupes.items(), key=lambda kv: (not arabe(kv[0]), -len(kv[1]), kv[0]))

out = {"_meta": {
  "titre": "Feuille de saisie — localisation des citations, groupées par ouvrage",
  "mode_d_emploi": [
    "1. Ouvrir l'ouvrage une seule fois, traiter toutes ses citations d'affilée.",
    "2. Pour chaque citation, remplir : volume, page, et si possible l'URL shamela de la page.",
    "3. Coller aussi le texte arabe TEL QUEL depuis l'edition : il sert de controle — si le",
    "   texte colle ne correspond pas a la citation francaise, c'est que la reference est fausse.",
    "4. Renseigner l'edition UNE SEULE FOIS par ouvrage, dans le champ 'edition'.",
    "5. Ne jamais deviner une pagination. Laisser vide vaut mieux qu'approximer."
  ],
  "regle": "Une reference fausse est pire qu'une reference absente : elle donne l'apparence de la verifiabilite.",
  "genere_par": "scripts/grouper-citations-par-ouvrage.py",
  "ouvrages": len(ordre),
  "citations": sum(len(v) for v in groupes.values())
}, "ouvrages": []}

for nom, cits in ordre:
    out["ouvrages"].append({
      "ouvrage": nom,
      "citations_a_localiser": len(cits),
      "edition": {"muhaqqiq_ou_editeur": "", "lieu_et_annee": "", "shamela_book_id": ""},
      "citations": [
        {"article": c["article"], "n_dans_l_article": c["n"],
         "texte_publie_sur_le_site": c["extrait"],
         "a_remplir": {"volume": "", "page": "", "url_shamela": "", "texte_arabe_source": ""}}
        for c in cits
      ]
    })

json.dump(out, open('content/corrections/citations-par-ouvrage.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)

print(f"{out['_meta']['citations']} citations réparties sur {out['_meta']['ouvrages']} ouvrages\n")
print(f"{'ouvrage':58} {'citations':>10}")
print("─" * 70)
for o in out["ouvrages"][:22]:
    print(f"{o['ouvrage'][:58]:58} {o['citations_a_localiser']:10}")
reste = out["ouvrages"][22:]
if reste:
    print(f"{'… ' + str(len(reste)) + ' autres ouvrages':58} {sum(o['citations_a_localiser'] for o in reste):10}")
