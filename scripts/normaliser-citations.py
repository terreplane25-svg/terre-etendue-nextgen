#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normalise l'attribution des citations : <cite> -> <footer>.

La charte du site impose un <footer> en pied de citation. Le corpus employait
aussi <cite>, qui est du contenu de phrase et se retrouvait donc INSIDE le <p> —
un <footer> y serait invalide. On ferme donc le paragraphe avant de l'ouvrir.

Aucune attribution n'est ajoutée, modifiee ni supprimee : seul le balisage change.
"""
import json, glob, os, re, sys

def normalise(bloc):
    """Transforme un <blockquote> en sortant le <cite> du <p> et en le passant en <footer>."""
    m = re.search(r'<cite[^>]*>(.*?)</cite>', bloc, re.S)
    if not m:
        return bloc, 0
    attribution = m.group(1).strip()
    corps = bloc[:m.start()] + bloc[m.end():]

    # ouverture du blockquote, puis contenu
    mo = re.match(r'(<blockquote[^>]*>)(.*)(</blockquote>)$', corps, re.S)
    if not mo:
        return bloc, 0
    ouv, dedans, fer = mo.groups()

    # le <p> qui contenait le cite peut se retrouver vide ou mal ferme
    dedans = dedans.replace('<p></p>', '').strip()
    # texte nu directement sous blockquote (forme B) : on l'enveloppe
    reste = re.sub(r'<p>.*?</p>', '', dedans, flags=re.S).strip()
    if reste:
        dedans = dedans.replace(reste, f'<p>{reste}</p>')
    return f'{ouv}{dedans}<footer>{attribution}</footer>{fer}', 1

total_f = total_c = 0
for f in sorted(glob.glob('content/articles/*.json')):
    d = json.load(open(f, encoding='utf-8'))
    h = d['htmlBody']
    n = 0
    def repl(m):
        global n
        nouv, k = normalise(m.group(0))
        n += k
        return nouv
    h2 = re.sub(r'<blockquote[^>]*>.*?</blockquote>', repl, h, flags=re.S)
    if n:
        d['htmlBody'] = h2
        json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        open(f, 'a', encoding='utf-8').write('\n')
        print(f"  {n:3} citations  {os.path.basename(f)[:-5]}")
        total_f += 1; total_c += n

print(f"\n{total_c} citations normalisées dans {total_f} articles")

# ── controle : plus aucun <cite> en citation, aucun <footer> dans un <p> ──
pb = 0
for f in glob.glob('content/articles/*.json'):
    h = json.load(open(f, encoding='utf-8'))['htmlBody']
    for b in re.findall(r'<blockquote[^>]*>.*?</blockquote>', h, re.S):
        if '<cite' in b:
            print("  !! <cite> restant :", os.path.basename(f)[:-5]); pb += 1
        if re.search(r'<p>[^<]*(?:<(?!/p>)[^>]*>[^<]*)*<footer', b):
            print("  !! <footer> dans un <p> :", os.path.basename(f)[:-5]); pb += 1
print("contrôle :", "OK" if pb == 0 else f"{pb} problème(s)")
sys.exit(1 if pb else 0)
