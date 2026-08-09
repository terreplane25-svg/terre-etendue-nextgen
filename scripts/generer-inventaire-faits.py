#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inventaire des « faits établis » du site.

Chaque article porte un ou plusieurs encadrés-clés — tei-fait — dont le label
varie selon le pilier : FAIT ÉTABLI N°X au Centre de Recherche, CE QUE MONTRENT
LES DONNÉES à l'Observatoire, CE QUE LE TEXTE ÉTABLIT à la Bibliothèque, CE QUE
L'EXPÉRIENCE ÉTABLIT aux Expériences. Ce sont, par construction, les
affirmations que le site présente comme acquises. Elles engagent donc le site
plus que le reste du texte.

Ce script les relève tous et produit content/corrections/faits-etablis.md, un
document de travail avec une colonne de verdict laissée vide. Le verdict se
remplit à la main, article par article, au fil de l'examen.

Vocabulaire de verdict proposé :
  GARDER      — l'énoncé est exact et à sa place
  RESSERRER   — vrai mais formulé plus largement que ce qui est démontré
  DÉCLASSER   — ce n'est pas un fait établi : c'est une hypothèse, une lecture
                ou une objection, et l'encadré lui donne un statut qu'il n'a pas
  RETIRER     — l'énoncé ne tient pas

Relancer le script écrase le fichier : les verdicts déjà saisis seraient
perdus. Il refuse donc d'écrire si le fichier existe et porte des verdicts,
sauf avec --forcer.
"""

import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(RACINE, "content", "articles")
SORTIE = os.path.join(RACINE, "content", "corrections", "faits-etablis.md")

PILIERS = [
    ("headquarters", "Centre de Recherche", "FAIT ÉTABLI N°X"),
    ("observatory", "Observatoire", "CE QUE MONTRENT LES DONNÉES"),
    ("library", "Bibliothèque", "CE QUE LE TEXTE ÉTABLIT"),
    ("experiences", "Expériences", "CE QUE L'EXPÉRIENCE ÉTABLIT"),
    ("meta", "Pages d'appareil", "—"),
    ("lab", "Lab", "—"),
]


def relever():
    """Rend {categorie: [(slug, titre, [textes des encadrés])]}."""
    par_pilier = {c: [] for c, _, _ in PILIERS}
    for f in sorted(os.listdir(ARTICLES)):
        if not f.endswith(".json"):
            continue
        with open(os.path.join(ARTICLES, f), encoding="utf-8") as fh:
            d = json.load(fh)
        corps = d.get("htmlBody", "")
        encadres = []
        for m in re.finditer(r'<div class="tei-fait \w+">(.*?)</div>', corps, re.S):
            sans_label = re.sub(r'<span class="tei-fait-label">.*?</span>', "",
                                m.group(1), flags=re.S)
            txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", sans_label)).strip()
            if txt:
                encadres.append(txt)
        if encadres:
            cat = d.get("category", "headquarters")
            par_pilier.setdefault(cat, []).append((f[:-5], d.get("title", f[:-5]), encadres))
    return par_pilier


def ecrire(par_pilier):
    total = sum(len(e) for v in par_pilier.values() for _, _, e in v)
    articles = sum(len(v) for v in par_pilier.values())

    L = []
    L.append("# Inventaire des faits établis")
    L.append("")
    L.append("**%d encadrés-clés dans %d articles.** Ce sont, par construction, les "
             "affirmations que le site présente comme acquises — elles l'engagent donc "
             "plus que le reste du texte." % (total, articles))
    L.append("")
    L.append("Document de travail. La colonne **Verdict** se remplit à la main, article "
             "par article. Vocabulaire :")
    L.append("")
    L.append("| Verdict | Sens |")
    L.append("|---|---|")
    L.append("| `GARDER` | l'énoncé est exact et à sa place |")
    L.append("| `RESSERRER` | vrai, mais formulé plus largement que ce qui est démontré |")
    L.append("| `DÉCLASSER` | ce n'est pas un fait établi — c'est une hypothèse, une "
             "lecture ou une objection, et l'encadré lui donne un statut qu'il n'a pas |")
    L.append("| `RETIRER` | l'énoncé ne tient pas |")
    L.append("")
    L.append("Généré par `scripts/generer-inventaire-faits.py`. **Relancer le script "
             "écraserait les verdicts saisis** : il refuse d'écrire si le fichier en "
             "porte déjà, sauf avec `--forcer`.")
    L.append("")
    L.append("---")

    for cat, nom, label in PILIERS:
        entrees = par_pilier.get(cat) or []
        if not entrees:
            continue
        n = sum(len(e) for _, _, e in entrees)
        L.append("")
        L.append("## %s — %d faits, %d articles" % (nom, n, len(entrees)))
        L.append("")
        L.append("Label imposé par la charte : **%s**" % label)
        for slug, titre, encadres in entrees:
            L.append("")
            L.append("### %s" % titre)
            L.append("")
            L.append("`%s` — %d encadré%s" % (slug, len(encadres),
                                              "s" if len(encadres) > 1 else ""))
            L.append("")
            L.append("| # | Énoncé | Verdict |")
            L.append("|---|---|---|")
            for i, txt in enumerate(encadres, 1):
                propre = txt.replace("|", "\\|")
                L.append("| %d | %s |  |" % (i, propre))

    L.append("")
    return "\n".join(L) + "\n"


def main():
    forcer = "--forcer" in sys.argv
    # Ce fichier est annoté à la main. La première version de ce garde-fou
    # cherchait un verdict SEUL entre deux barres — elle a laissé passer les
    # verdicts commentés « **RETIRER** — vérifié… » et écrasé cinq annotations.
    # On ne présume donc plus de la forme : dès que le fichier existe, on refuse.
    if os.path.exists(SORTIE) and not forcer:
        deja = open(SORTIE, encoding="utf-8").read()
        lignes = [l for l in deja.split("\n")
                  if re.match(r"\|\s*\d+\s*\|", l)
                  and re.search(r"GARDER|RESSERRER|DÉCLASSER|RETIRER", l)]
        print("  ✗ %s existe déjà%s." % (os.path.relpath(SORTIE, RACINE),
              " et porte %d verdict(s)" % len(lignes) if lignes else ""))
        print("    Le régénérer écraserait toute annotation manuelle. "
              "Utiliser --forcer si c'est voulu.")
        return 1

    par_pilier = relever()
    contenu = ecrire(par_pilier)
    with open(SORTIE, "w", encoding="utf-8") as f:
        f.write(contenu)

    total = sum(len(e) for v in par_pilier.values() for _, _, e in v)
    print("  ✓ %s" % os.path.relpath(SORTIE, RACINE))
    for cat, nom, _ in PILIERS:
        entrees = par_pilier.get(cat) or []
        if entrees:
            print("      %-22s %3d faits, %2d articles"
                  % (nom, sum(len(e) for _, _, e in entrees), len(entrees)))
    print("      %-22s %3d" % ("TOTAL", total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
