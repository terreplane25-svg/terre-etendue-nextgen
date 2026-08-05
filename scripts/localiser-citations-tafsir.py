#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Complete l'attribution des citations de tafsir par la reference du verset.

PRINCIPE, et il n'y a aucune invention la-dedans. Un commentaire coranique est
ORGANISE PAR VERSET : la glose d'al-Tabari sur S88 V20 se trouve, dans n'importe
quelle edition et sur n'importe quel site, en allant a S88 V20. La reference du
verset EST donc la localisation, au meme titre qu'une pagination pour un ouvrage
a texte continu.

Le verset n'est pas devine : il est repris du titre de section qui gouverne la
citation dans l'article lui-meme. On rend explicite ce que la structure dit deja.

N'AFFECTE QUE : les citations dont le pied nomme un tafsir ET qui n'ont aucune
localisation. Les autres ne sont pas touchees.
"""
import json, glob, os, re, sys

sys.path.insert(0, 'scripts')
LOC = re.compile(r"\bp{1,2}\.?\s?\d|\bvol\.?\s?\d|\b\d{1,2}\s?/\s?\d{1,4}\b"
                 r"|\bS\s?\d{1,3}\s?V\s?\d{1,3}|\b\d{1,3}\s?:\s?\d{1,3}\b"
                 r"|\bhttps?://|\bn°\s?\d|\bhadith\s?\d", re.I)
TAFSIR = re.compile(r"Tafs[īi]r|Tefs[îi]r|Jal[āa]layn|Qur[ṭt]ub[īi]|[ṬT]abar[īi]"
                    r"|Ibn Kath[īi]r|Baghaw[īi]|Sam[ʿ']?[āa]n[īi]", re.I)

modifs = []
for f in sorted(glob.glob('content/articles/*.json')):
    d = json.load(open(f, encoding='utf-8'))
    if d.get('category') != 'library':
        continue
    slug, h = os.path.basename(f)[:-5], d['htmlBody']
    # positions des titres porteurs d'un verset
    titres = [(m.start(), m.group(0)) for m in re.finditer(r'<h[23][^>]*>.*?</h[23]>', h, re.S)]

    out, curseur, n = [], 0, 0
    for m in re.finditer(r'<blockquote[^>]*>.*?</blockquote>', h, re.S):
        bloc = m.group(0)
        fo = re.search(r'<footer>(.*?)</footer>', bloc, re.S)
        nouveau = bloc
        if fo and TAFSIR.search(fo.group(1)) and not LOC.search(re.sub('<[^>]+>', ' ', bloc)):
            # dernier titre precedant la citation
            prec = [t for p, t in titres if p < m.start()]
            v = None
            for t in reversed(prec):
                mv = re.search(r'\((\d{1,3})\s?:\s?(\d{1,3})\)', re.sub('<[^>]+>', '', t))
                if mv:
                    v = (mv.group(1), mv.group(2)); break
            if v:
                att = fo.group(1).rstrip()
                nouveau = bloc.replace(fo.group(0),
                          f'<footer>{att}, sur S{v[0]} V{v[1]}</footer>')
                n += 1
                modifs.append((slug, re.sub('<[^>]+>', '', att).strip(), f"S{v[0]} V{v[1]}"))
        out.append(h[curseur:m.start()]); out.append(nouveau); curseur = m.end()
    out.append(h[curseur:])
    if n:
        d['htmlBody'] = "".join(out)
        d['updated'] = '2026-08-05'
        json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        open(f, 'a', encoding='utf-8').write('\n')
        print(f"  {n:3} citations complétées  {slug}")

print(f"\n{len(modifs)} citations de tafsīr localisées par leur verset :")
for s, a, v in modifs:
    print(f"   {a[:32]:32} → {v:9} [{s}]")
