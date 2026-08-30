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
NATURES = os.path.join(RACINE, "src", "lib", "nature-articles.ts")
CSS = os.path.join(RACINE, "src", "styles", "globals.css")

def sans_svg(html):
    """Retire les sous-arbres <svg> et les blocs <style> : ils ont leurs propres
    <text>, <tspan> et leur feuille de style inline, hors des règles du corps."""
    html = re.sub(r"<svg\b.*?</svg>", "", html, flags=re.S | re.I)
    html = re.sub(r"<style\b.*?</style>", "", html, flags=re.S | re.I)
    return html


def sources_non_notees(html):
    """Les entrées de source qui ne portent pas leur classe A/B/C/D.

    Une entrée sans note ne se distingue pas d'une entrée bien notée : elle
    passe simplement inaperçue. C'est exactement le genre de trou qui doit
    être signalé par une machine et non par la vigilance de quelqu'un.
    """
    m = re.search(r'id="sources"', html)
    if not m:
        return []
    d = html.find("</h2>", m.end())
    if d < 0:
        return []
    suite = re.search(r"<h2[\s>]", html[d:])
    section = html[d:d + suite.start()] if suite else html[d:]
    manquantes = []
    for li in re.findall(r"<li[^>]*>(.*?)</li>", section, re.S):
        if not li.lstrip().startswith('<span class="tei-grade'):
            manquantes.append(re.sub(r"<[^>]+>", "", li).strip()[:70])
    return manquantes


def notices_de_nature():
    """Les slugs qui ont une notice dans le registre des natures.

    Lu par expression rationnelle plutôt qu'en évaluant du TypeScript : le
    registre est un objet littéral, une clé par ligne, et il n'y a rien à
    gagner à embarquer un analyseur pour ça.
    """
    if not os.path.exists(NATURES):
        return None
    src = open(NATURES, encoding="utf-8").read()
    corps = src.split("const N: Record<string, Nature> = {", 1)[-1]
    return set(re.findall(r"^  '?([a-z0-9-]+)'?: \{", corps, re.M))


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
    for entree in sources_non_notees(html):
        pb.append("source sans classe A/B/C/D : %s…" % entree)
    if "VOTRE-URL" in html or "[Insérer" in html:
        pb.append("placeholder en production")
    if re.search(r"\son(mouse|click|load)\w*=", html):
        pb.append("gestionnaire d'événement inline dans le corps")
    return pb


def main():
    css = open(CSS, encoding="utf-8").read()
    natures = notices_de_nature()
    total = 0
    slugs = []
    for f in sorted(os.listdir(ARTICLES)):
        if not f.endswith(".json"):
            continue
        with open(os.path.join(ARTICLES, f), encoding="utf-8") as fh:
            data = json.load(fh)
        slugs.append(f[:-5])
        pb = controler(f[:-5], data, css)
        if pb:
            print("── %s" % f[:-5])
            for p in pb:
                print("   ✗ %s" % p)
            total += len(pb)
    # L'encadré « ce que cet article est » ne s'affiche pas sans notice, et son
    # absence est silencieuse à la lecture. C'est ici qu'elle doit se voir.
    if natures is not None:
        manquants = sorted(set(slugs) - natures)
        orphelines = sorted(natures - set(slugs))
        for m in manquants:
            print("── %s\n   ✗ pas de notice dans nature-articles.ts" % m)
        for o in orphelines:
            print("── %s\n   ✗ notice de nature sans article" % o)
        total += len(manquants) + len(orphelines)

    print("\n%d problème(s)" % total)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
