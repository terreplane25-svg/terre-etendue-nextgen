#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vérifie que chaque média cité par un article répond encore.

Une image morte ne casse pas la construction du site, ne déclenche aucune
alerte, et ne se voit qu'en ouvrant la page. Le corpus cite aujourd'hui une
centaine de fichiers hébergés chez Hostinger, une dizaine de vignettes Unsplash
et une cinquantaine de vidéos ; rien ne garantit qu'un fichier renommé ou
supprimé ait été répercuté ici.

Trois sources d'adresses sont vérifiées :
  - les <img> et <iframe> des corps d'articles,
  - les images de couverture de src/lib/article-images.ts,
  - les couvertures de partage social, qui passent par getArticleOgImage et
    peuvent donc différer de la vignette.

Ce script demande un accès réseau sortant vers hostingersite.com, unsplash.com,
youtube.com et odysee.com. Il n'en a pas dans l'environnement d'intégration, où
la politique du proxy refuse ces hôtes : la sortie y serait « 000 » partout,
c'est-à-dire aucune information. Il est fait pour être lancé depuis un poste
ordinaire :

    python3 scripts/verifier-medias.py

Sortie non nulle s'il reste une adresse qui ne répond pas 200.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(RACINE, "content", "articles")
IMAGES = os.path.join(RACINE, "src", "lib", "article-images.ts")

# Certains hôtes refusent les clients sans en-tête d'agent, et YouTube répond
# 404 à une requête HEAD sur /embed alors que la page existe.
AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
DELAI = 25


def adresses():
    """Les adresses à vérifier, chacune avec l'endroit qui la cite."""
    out = {}
    for nom in sorted(os.listdir(ARTICLES)):
        if not nom.endswith(".json"):
            continue
        with open(os.path.join(ARTICLES, nom), encoding="utf-8") as f:
            html = json.load(f).get("htmlBody", "")
        for m in re.finditer(r'<(?:img|iframe)[^>]+src="(https?://[^"]+)"', html):
            out.setdefault(m.group(1), set()).add(nom[:-5])

    src = open(IMAGES, encoding="utf-8").read()
    hostinger = re.search(r'const HOSTINGER = "([^"]+)"', src).group(1)
    unsplash = re.search(r'const UNSPLASH = "([^"]+)"', src).group(1)
    for slug, gabarit in re.findall(r'"?([a-z0-9-]+)"?:\s*`([^`]+)`', src):
        url = (gabarit.replace("${HOSTINGER}", hostinger)
                      .replace("${UNSPLASH}", unsplash))
        out.setdefault(url, set()).add("couverture de " + slug)
        # getArticleOgImage réécrit les vignettes Unsplash en 1200×630 : c'est
        # cette adresse-là que Google et les réseaux vont chercher, pas l'autre.
        if "images.unsplash.com" in url:
            og = re.sub(r"w=\d+", "w=1200", url)
            og = re.sub(r"h=\d+", "h=630", og)
            out.setdefault(og, set()).add("partage social de " + slug)
    return out


def interroger(url):
    """Le code de réponse, ou 0 si la connexion elle-même échoue."""
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    try:
        with urllib.request.urlopen(req, timeout=DELAI) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def main():
    cibles = adresses()
    print("%d adresse(s) à vérifier…\n" % len(cibles))
    with ThreadPoolExecutor(max_workers=8) as pool:
        codes = dict(zip(cibles, pool.map(interroger, cibles)))

    injoignables = sum(1 for c in codes.values() if c == 0)
    if injoignables == len(cibles):
        print("Aucune adresse n'a répondu — c'est l'accès réseau qui manque,\n"
              "pas les fichiers. Relancer depuis un poste sans proxy filtrant.")
        return 2

    fautives = sorted((c, u) for u, c in codes.items() if c != 200)
    for code, url in fautives:
        ou = ", ".join(sorted(cibles[url]))
        print("%s  %s\n      cité par : %s" % (code or "injoignable", url, ou))

    print("\n%d adresse(s) sur %d ne répondent pas 200."
          % (len(fautives), len(cibles)))
    return 1 if fautives else 0


if __name__ == "__main__":
    sys.exit(main())
