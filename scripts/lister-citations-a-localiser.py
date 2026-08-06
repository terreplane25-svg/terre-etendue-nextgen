#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Liste les citations dont l'attribution ne permet pas de RETROUVER le passage.

DEFINITION, posee explicitement apres trois corrections successives d'un
detecteur trop etroit. Une reference est LOCALISEE si elle permet a un lecteur
de retrouver le passage sans lire l'ouvrage entier. Cela vaut dans cinq cas :

  1. pagination     — p. 342, vol. 6 p. 326, 1/152, t. II
  2. subdivision    — chapitre II, aphorisme 98, section 3, livre I
  3. numerotation   — hadith 4002, n° 202, Bukhari 3199
  4. reference      — sourate:verset (88:20, S88 V20)
  5. identifiant    — DOI, arXiv, URL directe, ou une DATE qui individue le
                      document (lettre du 25 fevrier 1693, journal du 3 fevrier
                      1774, numero de periodique daté)

Ce qui n'est PAS une localisation : le seul titre d'un ouvrage, le seul nom d'un
auteur, une annee de publication d'un livre (elle identifie l'edition, pas le
passage).

Le fichier produit est une liste de travail, pas un verdict : completer demande
de consulter la source.
"""
import json, glob, os, re, collections

LOC = re.compile(
    # 1. pagination
    r"\bp{1,2}\.?\s?\d"
    r"|\bvol\.?\s?\d|\bt\.\s?[IVXLC\d]"
    r"|\b\d{1,2}\s?/\s?\d{1,4}\b"
    # 2. subdivision nommee. Le \b devant § ne pouvait jamais matcher : § n'est
    #    pas un caractere de mot, donc « , § 6 » echouait. Ajout de « ch. » et
    #    des chapitres nommes entre guillemets.
    r"|(?:\bchap(?:itre)?\b|\bch\.|\blivre\b|\baphorisme\b|\bsection\b|§|\bpart(?:ie)?\b|\bprologue\b)\s*[\dIVXLC]"
    r"|\bpréface\b|\bintroduction\b"
    # 2 bis. Un dictionnaire est organise par racine ou par entree : la racine
    #    EST la localisation, exactement comme le verset l'est pour un tafsir.
    r"|\bracines?\s+[\u0600-\u06FF]|\bs\.\s?v\.|\bentrée\s+«"
    # 3. numerotation de recueil
    r"|\b(?:hadith|n°|no\.?)\s?\d"
    r"|(?:Bukh[āa]r[īi]|Muslim|Tirmidh[īi]|Nas[āa]|Ibn M[aā]ja|Ab[īi] D[āa]w[ūu]d|Ahmad|Sa[ḥh][īi][ḥh]a)\S*[\s,]+\S{0,8}\d{2,5}"
    # 4. reference scripturaire
    r"|\b\d{1,3}\s?:\s?\d{1,3}\b|\bS\s?\d{1,3}\s?V\s?\d{1,3}"
    # 5. identifiant ou date individuante
    r"|\barXiv:\s?\d|\bdoi[:\s]|\bhttps?://"
    # identifiant arXiv nu, tel qu'il apparait entre parentheses : (1505.07208)
    r"|\b\d{4}\.\d{4,5}\b"
    # volume(numero) d'un periodique : The Astronomical Journal, 105(5), 1993
    r"|\b\d{1,4}\s?\(\s?\d{1,3}\s?\)"
    r"|\b\d{1,2}(?:er)?\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}"
    r"|\b(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}"
    r"|\bNature\s+\d{2,3}\b|\bThe Physical Review\b.{0,18}\d{4}"
    , re.I)

todo, total = [], 0
for f in sorted(glob.glob('content/articles/*.json')):
    d = json.load(open(f, encoding='utf-8'))
    slug, h = os.path.basename(f)[:-5], d['htmlBody']
    for i, b in enumerate(re.findall(r'<blockquote[^>]*>.*?</blockquote>', h, re.S), 1):
        fo = re.search(r'<footer>(.*?)</footer>', b, re.S)
        if not fo:
            continue
        total += 1
        if LOC.search(re.sub('<[^>]+>', ' ', b)):
            continue
        todo.append({"article": slug, "categorie": d.get('category'), "n": i,
                     "attribution": re.sub('<[^>]+>', '', fo.group(1)).strip(),
                     "extrait": re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ',
                                b.replace(fo.group(0), ''))).strip()[:110]})

json.dump({"_meta": {
    "titre": "Citations à localiser",
    "definition": ("Une référence est localisée si elle permet de retrouver le passage sans lire "
                   "l'ouvrage entier : pagination, subdivision numérotée, numéro de recueil, "
                   "référence scripturaire, identifiant (DOI, arXiv, URL) ou date individuant le "
                   "document. Le seul titre d'un ouvrage n'en est pas une."),
    "regle": ("Ne jamais inventer une pagination. En cas de doute, retirer la citation plutôt "
              "que la sourcer approximativement."),
    "genere_par": "scripts/lister-citations-a-localiser.py",
    "citations_totales": total, "a_localiser": len(todo)}, "citations": todo},
    open('content/corrections/citations-a-localiser.json', 'w', encoding='utf-8'),
    ensure_ascii=False, indent=2)

print(f"{total} citations avec attribution · {len(todo)} sans localisation "
      f"({len(todo)/total*100:.0f} %)\n")
for a, n in collections.Counter(t['article'] for t in todo).most_common():
    print(f"  {n:3}  {a}")
