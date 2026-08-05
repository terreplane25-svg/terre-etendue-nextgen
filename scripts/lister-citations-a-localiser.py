#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Liste les citations dont l'attribution ne porte aucune localisation verifiable.

Une citation « — Tafsīr al-Ṭabarī » nomme l'ouvrage mais ne dit pas OU regarder.
Ce script produit la liste de travail. Il n'invente rien : completer demande de
consulter l'edition, ce qu'aucun script ne peut faire.
"""
import json, glob, os, re

LOC = re.compile(r'\bp{1,2}\.\s?\d|\bvol\.\s?\d|\bn°\s?\d|\bS\d+\s?V\d+|\b\d{1,4}\s?[,/]\s?\d|\bt\.\s?\d|shamela')
todo = []
for f in sorted(glob.glob('content/articles/*.json')):
    d = json.load(open(f, encoding='utf-8'))
    slug, h = os.path.basename(f)[:-5], d['htmlBody']
    for i, b in enumerate(re.findall(r'<blockquote[^>]*>.*?</blockquote>', h, re.S), 1):
        fo = re.search(r'<footer>(.*?)</footer>', b, re.S)
        if not fo or LOC.search(re.sub('<[^>]+>', ' ', b)):
            continue
        todo.append({"article": slug, "categorie": d.get('category'), "n": i,
                     "attribution": re.sub('<[^>]+>', '', fo.group(1)).strip(),
                     "extrait": re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ',
                                b.replace(fo.group(0), ''))).strip()[:110]})

json.dump({"_meta": {
    "titre": "Citations à localiser",
    "objet": ("Ces citations portent leur attribution — l'ouvrage est nommé — mais aucune "
              "localisation précise : ni volume, ni page, ni numéro. Elles ne sont donc pas "
              "vérifiables par un lecteur."),
    "regle": ("Ne jamais inventer une pagination. En cas de doute, retirer la citation plutôt "
              "que la sourcer approximativement."),
    "genere_par": "scripts/lister-citations-a-localiser.py",
    "total": len(todo)}, "citations": todo},
    open('content/corrections/citations-a-localiser.json', 'w', encoding='utf-8'),
    ensure_ascii=False, indent=2)

import collections
par_art = collections.Counter(t['article'] for t in todo)
par_ouv = collections.Counter(t['attribution'] for t in todo)
print(f"{len(todo)} citations sans localisation\n")
print("Par article :")
for a, n in par_art.most_common():
    print(f"  {n:3}  {a}")
print("\nOuvrages les plus concernés :")
for o, n in par_ouv.most_common(8):
    print(f"  {n:3}  {o}")
