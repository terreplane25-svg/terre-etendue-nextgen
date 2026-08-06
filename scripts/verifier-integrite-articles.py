#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contrôle d'intégrité de tous les articles — à relancer avant chaque commit.

Vérifie, pour chaque content/articles/*.json :

  · texte hors conteneur — du texte nu qui cohabite avec des frères de niveau
    bloc, et n'est donc porté par aucun élément. Un <div> qui ne contient que
    du texte et de l'inline n'est PAS fautif, même sans <p> : c'est un
    conteneur de texte, souvent stylé, et l'envelopper casserait sa grille.
    La règle exacte est dans lib_html_articles.py ;
  · classes CSS employées et jamais définies dans globals.css — une coquille
    dans un nom de classe ne provoque aucune erreur de build ;
  · citations sans attribution — la charte impose un <footer> ou un <cite> ;
  · numérotation des sections continue à partir de 01 ;
  · équilibre des balises ;
  · balise <a> imbriquée dans une autre ;
  · exigences de la charte : lede, section Sources, encadré-clé, pas d'emoji
    ni de chiffres arabes orientaux dans les titres, data-zoomable sur les
    images, aucun placeholder.

Les sous-arbres <svg> sont ignorés : ils ont leurs propres <text>, <tspan> et
leur feuille de style inline, qui ne relèvent d'aucune de ces règles.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_html_articles import runs_fautifs  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(RACINE, "content", "articles")
CSS = os.path.join(RACINE, "src", "styles", "globals.css")

def sans_svg(html):
    """Retire les sous-arbres <svg> et les blocs <style> : ils ont leurs propres
    <text>, <tspan> et leur feuille de style inline, hors des règles du corps."""
    html = re.sub(r"<svg\b.*?</svg>", "", html, flags=re.S | re.I)
    html = re.sub(r"<style\b.*?</style>", "", html, flags=re.S | re.I)
    return html


def controler(slug, data, css):
    html = data.get("htmlBody", "")
    nu = sans_svg(html)
    pb = []

    for debut, fin in runs_fautifs(html):
        pb.append("texte hors conteneur : %r" % html[debut:fin][:64])

    inconnues = set()
    for attr in re.findall(r'class="([^"]+)"', nu):
        for cls in attr.split():
            if "." + cls not in css:
                inconnues.add(cls)
    for cls in sorted(inconnues):
        pb.append("classe CSS jamais définie : %s" % cls)

    for bq in re.findall(r"<blockquote.*?</blockquote>", nu, re.S):
        if "<footer>" not in bq and "<cite>" not in bq:
            pb.append("citation sans attribution : %s"
                      % re.sub(r"<[^>]+>", "", bq).strip()[:64])

    nums = re.findall(r'<span class="tei-section-num">(\d+)</span>', html)
    if nums and nums != ["%02d" % (i + 1) for i in range(len(nums))]:
        pb.append("numérotation des sections : %s" % " ".join(nums))

    for balise in ("p", "blockquote", "div", "table", "thead", "tbody", "tr",
                   "td", "th", "ol", "ul", "li", "h2", "h3", "a", "footer", "span"):
        o = len(re.findall(r"<%s[\s>]" % balise, nu))
        f = len(re.findall(r"</%s>" % balise, nu))
        if o != f:
            pb.append("<%s> : %d ouvrants, %d fermants" % (balise, o, f))

    if re.search(r"<a[^>]*>[^<]*<a", nu):
        pb.append("balise <a> imbriquée")

    # ── exigences de la charte ──
    # Les pages « meta » (glossaire, index, registre des corrections, état des
    # lieux, standards) sont des pages d'appareil, pas des articles de fond :
    # la charte ne leur impose ni lede, ni encadré-clé, ni section Sources.
    if data.get("category") != "meta":
        if 'class="tei-lede"' not in html:
            pb.append("pas de lede")
        if 'id="sources"' not in html:
            pb.append("pas de section Sources")
        if "tei-fait" not in html:
            pb.append("pas d'encadré-clé")
    for titre in re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.S):
        if re.search(r"[٠-٩۰-۹]", titre):
            pb.append("chiffres arabes orientaux dans un titre")
        if re.search(r"[\U0001F300-\U0001FAFF]", titre):
            pb.append("emoji dans un titre")
    for img in re.findall(r"<img[^>]*>", html):
        if "data-zoomable" not in img:
            pb.append("img sans data-zoomable : %s" % img[:60])
    if "VOTRE-URL" in html or "[Insérer" in html:
        pb.append("placeholder en production")
    if re.search(r"\son(mouse|click|load)\w*=", html):
        pb.append("gestionnaire d'événement inline dans le corps")
    return pb


def main():
    css = open(CSS, encoding="utf-8").read()
    total = 0
    for f in sorted(os.listdir(ARTICLES)):
        if not f.endswith(".json"):
            continue
        with open(os.path.join(ARTICLES, f), encoding="utf-8") as fh:
            data = json.load(fh)
        pb = controler(f[:-5], data, css)
        if pb:
            print("── %s" % f[:-5])
            for p in pb:
                print("   ✗ %s" % p)
            total += len(pb)
    print("\n%d problème(s)" % total)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
