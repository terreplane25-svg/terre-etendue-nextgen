#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ce que chaque fusion a avalé, et ce qu'on en retrouve aujourd'hui.

Une fusion se juge sur une seule question : la matière de l'article absorbé
est-elle encore là ? Le message de commit l'affirme toujours ; ce script le
vérifie section par section, sans croire le message sur parole.

Comment ne PAS le vérifier
──────────────────────────
Une première version cherchait les titres de sections dans le corpus actuel.
Elle donnait 46 sections « introuvables » sur 90, et c'était trompeur : une
fusion réécrit les titres, c'est même souvent son intérêt. « Expérience 2 : Le
test du zoom » est devenu « Test 1 — Le zoom décisif ». Rien n'était perdu, mais
la méthode l'annonçait perdu.

Chercher des phrases entières du corps ne marche pas mieux, pour la raison
inverse : une fusion réécrit aussi les phrases. Le contrôle est passé de trop
sévère à inutilisable.

Comment le vérifier
───────────────────
On cherche le vocabulaire rare. Pour chaque section, on retient les mots les
moins fréquents du corpus — noms propres, chiffres, termes techniques : Thirring,
Baumgartner, marshmallow, 61 Cygni. Ce sont eux qui identifient un contenu, et
ce sont eux qu'une réécriture conserve, parce qu'on ne peut pas paraphraser un
nom propre. Si la moitié d'entre eux se retrouve dans l'article récepteur, la
matière a suivi.

Le résultat n'est pas une preuve, c'est un tri : il dit où regarder. Les
sections marquées « à lire » sont celles qu'il faut ouvrir soi-même.
"""
import json
import os
import re
import subprocess
import sys
import unicodedata
from collections import Counter

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(RACINE, "content", "articles")

# La campagne d'épuration, dans l'ordre. Le récepteur est celui qu'annonce le
# message de commit ; None quand la fusion en visait plusieurs.
FUSIONS = [
    ("f959bde", ["la-perspective-pourquoi-les-objets-disparaissent"],
     "Les trois articles sur la perspective"),
    ("897a96a", ["la-perspective-pourquoi-les-objets-disparaissent"],
     "L'horizon, la perspective et la réfraction"),
    ("6dcb3ca", ["les-forces-invisibles-a-faire-chez-soi",
                 "la-pression-atmospherique-un-ocean-d-air-invisible"],
     "Les explications de physique courtes"),
    ("4667c03", ["la-gravite-70-theories-et-aucune-preuve"], "Le bloc gravité"),
    ("1a9bfad", ["les-distances-cosmiques-au-dela-de-la-regle",
                 "ligo-londe-qui-nexistait-pas"],
     "Trous noirs, LIGO, distances"),
    ("60546d5", ["la-rotation-terrestre-experiences-preuves-verdict"],
     "Rotation terrestre et pendule de Foucault"),
    ("fcca067", ["la-rotation-terrestre-experiences-preuves-verdict"],
     "Les horloges atomiques"),
    ("c29eb20", [], "Le nivellement avec fermeture — RETRAIT éditorial, pas fusion"),
]

VIDES = set("""alors ainsi apres aucun aucune aussi autre autres avait avant avec
beaucoup bien cela cependant certains comme dans deux donc dont elle elles encore
entre etait etaient etre faire fait leur leurs mais meme moins nous pour pourquoi
plus plusieurs quand quelle quelques sans selon seulement sont sous suite tous
toute toutes tres trop vous celui celle ceux depuis ensuite jamais lorsque parce
pendant peuvent presque puis quoi seule soit toujours voir cette cet ces""".split())


def git(*args):
    return subprocess.run(["git"] + list(args), cwd=RACINE, capture_output=True,
                          text=True).stdout


def nu(html):
    t = re.sub(r"<[^>]+>", " ", html)
    t = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), t)
    t = t.replace("&nbsp;", " ").replace("&amp;", "&")
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", t.lower())).strip()


def corpus_nu():
    out = {}
    for nom in sorted(os.listdir(ARTICLES)):
        if nom.endswith(".json"):
            with open(os.path.join(ARTICLES, nom), encoding="utf-8") as f:
                out[nom[:-5]] = nu(json.load(f)["htmlBody"])
    return out


def mots_rares(texte, frequences, combien=8):
    """Le vocabulaire qui identifie un contenu : ce que le corpus dit rarement."""
    candidats = {m for m in texte.split()
                 if len(m) >= 6 and m not in VIDES and not m.isdigit()}
    return sorted(candidats, key=lambda m: frequences.get(m, 0))[:combien]


def sections(html):
    out = []
    for m in re.finditer(r"<h[23][^>]*>(.*?)</h[23]>(.*?)(?=<h[23]|$)", html, re.S):
        titre = re.sub(r"^\d+", "", re.sub(r"<[^>]+>", "", m.group(1)).strip()).strip()
        out.append((titre, nu(m.group(2))))
    return out


def main():
    corpus = corpus_nu()
    frequences = Counter()
    for texte in corpus.values():
        frequences.update(set(texte.split()))

    a_lire = []
    for commit, recepteurs, libelle in FUSIONS:
        sortie = git("show", "--diff-filter=D", "--name-only", "--format=", commit)
        fichiers = [l.strip() for l in sortie.splitlines()
                    if l.strip().startswith("content/articles/")]
        print("\n" + "=" * 78)
        print("%s  %s" % (commit, libelle))
        if not fichiers:
            print("  aucun article supprimé par ce commit.")
            continue
        cible = " ".join(corpus.get(r, "") for r in recepteurs) or " ".join(corpus.values())

        for chemin in fichiers:
            brut = git("show", "%s^:%s" % (commit, chemin))
            if not brut.strip():
                print("  !! %s : version d'origine introuvable" % chemin)
                continue
            art = json.loads(brut)
            html = art["htmlBody"]
            print("\n  ── %s" % art["title"])
            print("     %d mots avant fusion" % len(nu(html).split()))
            for titre, corps in sections(html):
                if not corps or titre.lower().startswith(("source", "média", "media")):
                    continue
                rares = mots_rares(corps, frequences)
                if not rares:
                    continue
                repris = [m for m in rares if m in cible]
                part = len(repris) / len(rares)
                etat = "repris" if part >= 0.5 else ("partiel" if part >= 0.25
                                                     else "À LIRE")
                print("     %-7s %-50s %d/%d  %s"
                      % (etat, titre[:50], len(repris), len(rares),
                         " ".join(m for m in rares if m not in repris)[:40]))
                if etat == "À LIRE":
                    a_lire.append((art["title"], titre))

    print("\n" + "=" * 78)
    if a_lire:
        print("%d section(s) à ouvrir soi-même :" % len(a_lire))
        for source, titre in a_lire:
            print("   %-46s %s" % (source[:46], titre[:60]))
    else:
        print("Aucune section ne tombe sous le seuil. La matière a suivi partout.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
