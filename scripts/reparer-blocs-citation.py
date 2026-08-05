#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repare les blocs de citation qui ont avale du contenu qui n'est pas cite.

DEUX DEFAUTS, trouves en verifiant les pieds de citation attaches a de la prose.

1. HTML INVALIDE ET STRUCTURE CASSEE. Des <blockquote> contiennent des <h2>,
   des <h3> et meme un <table> entier, souvent imbriques dans un <p> — ce qui
   est invalide. Consequence visible : des titres de section, avec leur
   numerotation, s'affichent A L'INTERIEUR d'un encadre de citation.

2. PIED SUR DE LA PROSE. Le paragraphe d'amorce du site est enferme dans le
   bloc avec la citation, si bien que le pied semble attribuer la prose.

Reparation : on ferme le bloc avant ce qui n'est pas cite. L'amorce redevient un
paragraphe normal, les titres et tableaux retournent au niveau superieur, et
seule la citation reste dans le bloc avec son pied.
"""
import json, glob, os, re, sys

BLOC = re.compile(r'<blockquote([^>]*)>(.*?)</blockquote>', re.S)
INTRUS = re.compile(r'<(h[1-6]|table)\b', re.I)

def repare(attrs, corps):
    """Retourne le HTML de remplacement, et le nombre de defauts corriges."""
    fo = re.search(r'<footer>.*?</footer>', corps, re.S)
    pied = fo.group(0) if fo else ''
    corps = corps.replace(pied, '') if pied else corps

    # on deplie les <p> qui enveloppent un titre ou un tableau : invalide
    corps = re.sub(r'<p>\s*(<(?:h[1-6]|table)\b)', r'\1', corps, flags=re.I)

    # decoupage en morceaux : titres/tableaux d'un cote, reste de l'autre
    morceaux = re.split(r'(<h[1-6]\b.*?</h[1-6]>|<table\b.*?</table>)', corps, flags=re.S | re.I)
    avant, intrus, apres = [], [], []
    vu = False
    for m in morceaux:
        if re.match(r'\s*<(h[1-6]|table)\b', m, re.I):
            intrus.append(m.strip()); vu = True
        elif vu:
            apres.append(m)
        else:
            avant.append(m)

    def nettoie(x):
        x = "".join(x).strip()
        x = re.sub(r'<p>\s*</p>', '', x)
        return x.strip()

    amorce, citation = nettoie(avant), nettoie(apres)
    if not vu:
        # pas d'intrus : on sort seulement le premier <p> s'il n'est pas cite
        ps = re.findall(r'<p>.*?</p>', corps, re.S)
        if len(ps) >= 2 and not re.search(r'[«"“]', ps[0]):
            amorce, citation = ps[0], "".join(ps[1:])
            return f'{amorce}\n<blockquote{attrs}>{citation}{pied}</blockquote>', 1
        return None, 0

    out = []
    if amorce: out.append(amorce)
    out += intrus
    if citation: out.append(f'<blockquote{attrs}>{citation}{pied}</blockquote>')
    elif pied: out.append(f'<blockquote{attrs}>{pied}</blockquote>')
    return "\n".join(out), 1

total_i = total_p = 0
for f in sorted(glob.glob('content/articles/*.json')):
    d = json.load(open(f, encoding='utf-8'))
    slug, h = os.path.basename(f)[:-5], d['htmlBody']
    ni = np = 0
    out, curseur = [], 0
    for m in BLOC.finditer(h):
        attrs, corps = m.group(1), m.group(2)
        besoin = bool(INTRUS.search(corps))
        rep, k = repare(attrs, corps)
        if k and rep:
            out.append(h[curseur:m.start()]); out.append(rep); curseur = m.end()
            if besoin: ni += 1
            else: np += 1
    if ni or np:
        out.append(h[curseur:])
        d['htmlBody'] = "".join(out)
        d['updated'] = '2026-08-05'
        json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        open(f, 'a', encoding='utf-8').write('\n')
        print(f"  {slug:52} {ni} titre/tableau extrait(s), {np} amorce(s) sortie(s)")
        total_i += ni; total_p += np

print(f"\n{total_i} blocs contenaient un titre ou un tableau · {total_p} pieds portaient sur une amorce")

# ── controle : plus aucun titre ni tableau dans un blockquote ──────────────
pb = 0
for f in glob.glob('content/articles/*.json'):
    h = json.load(open(f, encoding='utf-8'))['htmlBody']
    for b in BLOC.finditer(h):
        if INTRUS.search(b.group(2)):
            print("  !! reste un intrus :", os.path.basename(f)[:-5]); pb += 1
    if re.search(r'<p>\s*<h[1-6]', h, re.I):
        print("  !! titre encore dans un <p> :", os.path.basename(f)[:-5]); pb += 1
print("contrôle :", "OK" if pb == 0 else f"{pb} problème(s)")
sys.exit(1 if pb else 0)
