#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrait les triplets (ouvrage, volume/page, URL shamela) des documents deposes.

Produit content/sources/references-extraites.json : une table de correspondance
reutilisable. Elle n'est PAS appliquee automatiquement aux articles — chaque
appariement doit etre verifie a la lecture, l'appariement flou ayant deja failli
me faire attribuer le Lisan al-Arab a Ibn Kathir.
"""
import re, json, glob, os, collections

EXT = '/tmp/claude-0/-home-user-terre-etendue-nextgen/812b9415-e612-52d5-8790-ea0c6c910b93/scratchpad/extrait'

# Un ouvrage nomme, suivi d'une pagination et/ou d'une URL shamela, dans un
# rayon de 200 caracteres. On capture large et on trie ensuite a la main.
OUVRAGE = (r"(Lis[âaā]noul?\s?[عʿ]arab|Lis[āa]n al-[ʿع]Arab|Tef?s[îiī]r\s+E[lt]?[-\s]?\w+"
           r"|Tefs[îiī]r\s+Et-?Tabar[îi]|Tafs[īi]r\s+\w+|Mou?[ʿع]?jam\s+\w+"
           r"|Es-?Souyo[ûu]t[îi]|Ibn\s+Mandhour|Ibn\s+Man[ẓz][ūu]r|El\s?Iklil[^,\n]{0,30}"
           r"|Sah[îiī]h\s+\w+|Mouslim|El\s?Boukh[âaā]r[îi]|Et-?Tirmidh[îi])")
PAGIN   = r"(v(?:ol)?\.?\s?\d{1,2}\s*,?\s*p{1,2}\.?\s?\d{1,4}|p{1,2}\.?\s?\d{1,4})"
SHAM    = r"(https?://shamela\.ws/\S+)"

refs = []
for f in sorted(glob.glob(f'{EXT}/*.txt')):
    doc = os.path.basename(f)[:-4]
    t = open(f, encoding='utf-8').read()
    t = re.sub(r'[ \t]+', ' ', t)
    for m in re.finditer(SHAM, t):
        fen = t[max(0, m.start()-260):m.end()+80]
        ouv = re.findall(OUVRAGE, fen)
        pag = re.findall(PAGIN, fen)
        refs.append({"document": doc,
                     "url_shamela": m.group(1).rstrip(').,;'),
                     "ouvrage_voisin": ouv[-1].strip() if ouv else None,
                     "pagination_voisine": pag[-1].strip() if pag else None,
                     "contexte": re.sub(r'\s+', ' ', fen).strip()[-230:]})

# regroupement par identifiant de livre shamela : c'est la cle stable
par_livre = collections.defaultdict(list)
for r in refs:
    m = re.search(r'/book/(\d+)', r['url_shamela'])
    if m: par_livre[m.group(1)].append(r)

out = {"_meta": {
  "titre": "Références extraites des documents sources déposés",
  "avertissement": ("Table de correspondance BRUTE. Elle n'est pas appliquée automatiquement : "
                    "chaque appariement doit être vérifié à la lecture du contexte. Un appariement "
                    "flou a déjà failli attribuer le Lisān al-ʿArab à Ibn Kathīr."),
  "genere_par": "scripts/extraire-references-sources.py",
  "urls_shamela": len(refs),
  "livres_distincts": len(par_livre)},
  "livres": []}

for bid, items in sorted(par_livre.items(), key=lambda kv: -len(kv[1])):
    noms = collections.Counter(i['ouvrage_voisin'] for i in items if i['ouvrage_voisin'])
    out["livres"].append({
      "shamela_book_id": bid,
      "ouvrage_probable": noms.most_common(1)[0][0] if noms else None,
      "noms_rencontres": [n for n, _ in noms.most_common()],
      "occurrences": len(items),
      "pages": [{"url": i['url_shamela'], "pagination": i['pagination_voisine'],
                 "document": i['document'], "contexte": i['contexte']} for i in items]})

json.dump(out, open('content/sources/references-extraites.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)

print(f"{len(refs)} URL shamela, {len(par_livre)} livres distincts\n")
print(f"{'book id':>8}  {'occ':>4}  ouvrage probable")
print("─" * 76)
for l in out["livres"]:
    print(f"{l['shamela_book_id']:>8}  {l['occurrences']:>4}  {l['ouvrage_probable'] or '(non identifié dans le contexte)'}")
