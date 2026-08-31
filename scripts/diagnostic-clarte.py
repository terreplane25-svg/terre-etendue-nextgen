#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Où le corpus s'étale, et pourquoi.

Le dossier LIGO est court parce qu'il est construit ainsi : une idée par
section, un fait établi par section, la conclusion en tête et le développement
ensuite. Ce script cherche, dans les 53 articles, ce qui s'écarte de cette
forme. Il ne mesure pas la qualité — il mesure des symptômes, et il dit dans
quel ordre ouvrir les fichiers.

Six symptômes, chacun vérifiable à la main en trente secondes :

  section-fleuve   Une section de plus de 900 mots. Au-delà, le lecteur ne sait
                   plus ce qu'on lui démontre ; c'est le seuil où le dossier des
                   trous noirs avait deux sections illisibles.
  sans-fait        Une section de plus de 400 mots qui ne conclut sur rien. Si
                   elle ne produit pas d'encadré-clé, ou bien elle est du
                   remplissage, ou bien sa conclusion est restée implicite.
  redite           Une phrase de huit mots ou plus qui revient ailleurs dans le
                   même article. C'est ce qui a fait perdre 1 700 mots au
                   dossier des trous noirs sans rien lui retirer.
  biographie       Une même personne présentée deux fois avec sa qualité. On
                   présente quelqu'un à sa première mention, pas à chacune.
  numerotation     Des sous-titres en « 1.1, 2.1 » : un second système de
                   numérotation concurrent de celui des sections.
  cheville         Les formules qui n'ajoutent rien — « il est important de
                   noter que », « il convient de souligner », « comme nous
                   l'avons vu ». Elles signalent la phrase qu'on aurait pu
                   écrire directement.

Le score est le nombre de symptômes pondéré ; il sert à trier, pas à juger.
"""
import json
import os
import re
import sys
import unicodedata
from collections import Counter

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(RACINE, "content", "articles")

CHEVILLES = [
    "il est important de noter", "il convient de souligner", "il convient de noter",
    "il est intéressant de", "comme nous l'avons vu", "comme nous venons de",
    "il faut bien comprendre", "il est essentiel de comprendre", "force est de constater",
    "il n'en demeure pas moins", "cela étant dit", "en d'autres termes",
    "il est à noter", "notons que", "précisons que", "rappelons que",
    "il est crucial de", "il est indispensable de", "on ne saurait",
]

# Ce qui, dans une phrase, désigne une présentation de personne.
QUALITE = re.compile(
    r"(physicien|astronome|mathématicien|géologue|professeur|chercheur|directeur|"
    r"historien|ingénieur|astrophysicien|philosophe|prix Nobel|membre de l&#8217;Académie|"
    r"membre de l'Académie)", re.I)


def sans_sources(html):
    """Le corps sans sa bibliographie.

    Les entrées de sources répètent nécessairement leurs formules — « NASA NTRS,
    page », « Majmūʿ al-Fatāwā, vol. » — et faisaient passer un article
    scrupuleusement sourcé pour un article qui se répète. Elles sortent du
    calcul des redites.
    """
    i = html.find('id="sources"')
    if i < 0:
        return html
    return html[:html.rfind("<h2", 0, i)]


def nu(html):
    t = re.sub(r"<[^>]+>", " ", html)
    t = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), t)
    t = t.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", t)


def sans_accent(t):
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def sections(html):
    out = []
    for m in re.finditer(r"<h2[^>]*>(.*?)</h2>(.*?)(?=<h2|$)", html, re.S):
        titre = re.sub(r"^\d+", "", re.sub(r"<[^>]+>", "", m.group(1)).strip()).strip()
        out.append((titre, m.group(2)))
    return out


def redites(texte):
    """Les suites de huit mots qui reviennent. Deux occurrences suffisent."""
    mots = re.findall(r"[a-zà-ÿ]+", texte.lower())
    fenetres = Counter(" ".join(mots[i:i + 8]) for i in range(len(mots) - 8))
    return [f for f, n in fenetres.items() if n > 1]


def biographies(texte):
    """Les noms propres présentés plus d'une fois avec une qualité."""
    doubles = []
    phrases = re.split(r"(?<=[.!?])\s+", texte)
    presente = Counter()
    for p in phrases:
        if not QUALITE.search(p):
            continue
        for nom in re.findall(r"\b([A-ZÉÈÀÎÔÜ][a-zà-ÿ']+(?:\s+[A-ZÉÈÀÎÔÜ][a-zà-ÿ']+)?)\b", p):
            if len(nom) > 5 and nom.split()[0] not in ("Le", "La", "Les", "Un", "Une",
                                                       "Ce", "Cette", "Dans", "Selon"):
                presente[nom] += 1
    return [n for n, c in presente.items() if c > 1]


def main():
    lignes = []
    for fichier in sorted(os.listdir(ARTICLES)):
        if not fichier.endswith(".json"):
            continue
        with open(os.path.join(ARTICLES, fichier), encoding="utf-8") as f:
            art = json.load(f)
        html = art["htmlBody"]
        texte = nu(html)
        total = len(texte.split())
        corps_nu = nu(sans_sources(html))

        fleuves, sans_fait = [], []
        for titre, corps in sections(html):
            n = len(nu(corps).split())
            if n > 900:
                fleuves.append((titre, n))
            elif n > 400 and "tei-fait" not in corps and not titre.lower().startswith(
                    ("source", "média", "media", "questions")):
                sans_fait.append((titre, n))

        red = redites(corps_nu)
        bio = biographies(corps_nu)
        deci = len(re.findall(r"<h3[^>]*>\s*\d+\.\d+", html))
        chev = sum(sans_accent(corps_nu).count(sans_accent(c)) for c in CHEVILLES)

        score = (3 * len(fleuves) + 2 * len(sans_fait) + len(red)
                 + 2 * len(bio) + deci + chev)
        if score:
            lignes.append((score, fichier[:-5], total, fleuves, sans_fait,
                           len(red), bio, deci, chev))

    lignes.sort(reverse=True)
    print("%-52s %6s %5s  symptômes" % ("article", "mots", "score"))
    print("─" * 100)
    for score, slug, total, fleuves, sans_fait, nred, bio, deci, chev in lignes:
        sym = []
        if fleuves:
            sym.append("%d section(s)-fleuve" % len(fleuves))
        if sans_fait:
            sym.append("%d sans encadré-clé" % len(sans_fait))
        if nred:
            sym.append("%d redite(s)" % nred)
        if bio:
            sym.append("bio ×2 : %s" % ", ".join(bio[:2]))
        if deci:
            sym.append("numérotation décimale")
        if chev:
            sym.append("%d cheville(s)" % chev)
        print("%-52s %6d %5d  %s" % (slug[:52], total, score, " · ".join(sym)))
        for titre, n in fleuves:
            print("%59s → %d mots : %s" % ("", n, titre[:50]))
    print("\n%d articles portent au moins un symptôme." % len(lignes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
