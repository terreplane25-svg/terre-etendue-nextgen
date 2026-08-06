#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mise en conformité structurelle du corpus.

Ce que ce script corrige, et ce qu'il ne corrige pas
────────────────────────────────────────────────────
Le premier relevé annonçait 249 fragments de « texte hors conteneur » sur 32
articles. En examinant les cas un à un, la majorité s'est révélée légitime :
la migration Elementor a laissé des cartes et des grilles bâties sur des <div>
qui portent leur propre style typographique. Ce texte est le contenu de son
élément, il est stylé, et l'enfermer dans un <p> ajouterait des marges qui
casseraient la grille. La règle du contrôle était trop large.

Avec la règle juste — un fragment est fautif si son parent contient au moins un
enfant de niveau bloc, c'est-à-dire si du texte nu cohabite avec des frères de
bloc et n'est donc porté par rien — il reste 68 fragments sur 14 articles.
Ce sont eux que ce script traite, en trois familles :

  1. Sous-titres orphelins (26) — « Bilan des observations », « Protocole en
     4 étapes ». Leur balise de titre a été perdue à la migration ; ils
     redeviennent des <h3>. Sept d'entre eux, dans l'article des vidéos, font
     doublon avec le titre de section qui les précède : ils deviennent des
     étiquettes plutôt que des titres, pour ne pas répéter la même information
     dans deux niveaux de plan.

  2. Encadrés de remarque (40) — ils commencent par « <strong>Libellé :</strong> »
     et suivent un tableau, une citation ou un paragraphe. Leur conteneur a
     disparu ; ils redeviennent des <p>. Nous ne leur rendons pas un habillage
     visuel que nous ne pouvons pas vérifier : le défaut corrigé est
     structurel, pas décoratif.

  3. Deux cas particuliers, traités nommément.

Le script traite en outre 17 citations sans attribution, qui relèvent de deux
défauts distincts, et une balise de citation qui avait avalé un encadré.

Garantie : après chaque famille, le texte de l'article — balises retirées,
espaces normalisés — est comparé à celui d'avant. Toute divergence bloque
l'écriture. Les seules transformations qui déplacent du texte sont déclarées
comme telles et vérifiées à part.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_html_articles import runs_fautifs, texte_nu  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(RACINE, "content", "articles")


# ═══════════════════════════════════════════════════════════════════════════
# Famille 1 — les sous-titres orphelins
# ═══════════════════════════════════════════════════════════════════════════

# Les sept étiquettes de l'article des vidéos : l'information figure déjà dans
# le <h2> qui précède immédiatement (« Bloc 1 — Avant la Création (Vidéos 1–3) »).
# En faire des <h3> dupliquerait le plan ; on leur rend leur rôle d'étiquette.
ETIQUETTES = re.compile(r"^Vidéos \d+–\d+$")

# Un fragment est un sous-titre s'il est court, sans balise et sans ponctuation
# finale de phrase. Au-delà, c'est du corps de texte.
def est_sous_titre(txt):
    return (len(txt) <= 60 and "<" not in txt and not txt.endswith(".")
            and not txt.startswith("«"))


def slugifier(txt):
    s = txt.lower()
    for a, b in (("àâä", "a"), ("éèêë", "e"), ("îï", "i"), ("ôö", "o"),
                 ("ùûü", "u"), ("ç", "c"), ("’'", "-")):
        for c in a:
            s = s.replace(c, b)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:52]


def traiter_runs(slug, html):
    """Enveloppe chaque fragment fautif. Travaille de la fin vers le début pour
    que les décalages déjà appliqués ne déplacent pas ceux qui restent."""
    compte = {"h3": 0, "etiquette": 0, "p": 0}
    for debut, fin in reversed(runs_fautifs(html)):
        txt = html[debut:fin]
        if ETIQUETTES.match(txt):
            remplacement = '<p class="tei-etiquette">%s</p>' % txt
            compte["etiquette"] += 1
        elif est_sous_titre(txt):
            remplacement = '<h3 id="%s-%s">%s</h3>' % (slug[:18], slugifier(txt), txt)
            compte["h3"] += 1
        else:
            remplacement = "<p>%s</p>" % txt
            compte["p"] += 1
        html = html[:debut] + remplacement + html[fin:]
    return html, compte


# ═══════════════════════════════════════════════════════════════════════════
# Famille 2 — les citations sans attribution
# ═══════════════════════════════════════════════════════════════════════════

# 2a. Onze <blockquote> qui ne citent personne : ce sont des encadrés
#     d'explication ou d'analogie (« Imaginez un drap tendu… »). Exiger une
#     attribution serait absurde ; c'est la balise qui est fausse. Ils
#     deviennent des encadrés de mise en relief.
# vols-avion en fait partie pour son dernier bloc (« Règle épistémologique
# fondamentale »), qui ne cite personne : la conversion ignore les blocs qui
# portent déjà un <footer>, donc ses cinq vraies citations ne sont pas touchées.
SANS_CITATION = {"les-trous-noirs-nexistent-pas", "lhypothese-nulle-dynamique-et-cinematique",
                 "vols-avion-et-courbure-terrestre"}

# 2b. Cinq citations de vols-avion portent bien leur source, mais dans un <p>
#     final commençant par un tiret cadratin au lieu d'un <footer>. Le texte ne
#     bouge pas : seule la balise change.
ATTRIBUTION_EN_P = re.compile(
    r"(<blockquote[^>]*>)(.*?)\n?<p>(—\s*[^<][^\n]*?)</p>(</blockquote>)", re.S)


def blockquote_en_encadre(html):
    """Retire la balise de citation des blocs qui ne citent personne."""
    n = 0
    sortie, reste = [], html
    while True:
        m = re.search(r"<blockquote([^>]*)>(.*?)</blockquote>", reste, re.S)
        if not m:
            sortie.append(reste)
            break
        bloc = m.group(0)
        sortie.append(reste[:m.start()])
        if "<footer>" in bloc or "<cite>" in bloc:
            sortie.append(bloc)
        else:
            corps = m.group(2)
            if not corps.strip().startswith("<p"):
                corps = "<p>%s</p>" % corps.strip()
            sortie.append('<div class="tei-highlight">%s</div>' % corps)
            n += 1
        reste = reste[m.end():]
    return "".join(sortie), n


def attribution_en_footer(html):
    def sub(m):
        return "%s%s<footer>%s</footer>%s" % (m.group(1), m.group(2).rstrip(),
                                             m.group(3).strip(), m.group(4))
    return ATTRIBUTION_EN_P.subn(sub, html)


# ═══════════════════════════════════════════════════════════════════════════
# Famille 3 — les cas nommés
# ═══════════════════════════════════════════════════════════════════════════

PDF_AVANT = """  📄
    <p>Sources complètes en arabe (PDF — 159 pages)</p>
    <p>Citations originales des 95 savants avec texte arabe intégral, références des ouvrages et chaînes de transmission.</p>
  <a href="https://terre-etendue-islam.fr/wp-content/uploads/2026/04/Pres_de_cent_savants_de_lislam_%E2%80%94_des_Compagnons_du_Prophete_%EF%B7%BA_aux.pdf" target="_blank" onmouseover="this.style.background='#A97544';this.style.transform='translateY(-2px)'" onmouseout="this.style.background='#8B5C36';this.style.transform='none'">Consulter le PDF ↗</a>
"""

PDF_APRES = """<div class="tei-infobox">
<p><strong>Sources complètes en arabe (PDF — 159 pages)</strong></p>
<p>Citations originales des 95 savants avec texte arabe intégral, références des ouvrages et chaînes de transmission. <a href="https://terre-etendue-islam.fr/wp-content/uploads/2026/04/Pres_de_cent_savants_de_lislam_%E2%80%94_des_Compagnons_du_Prophete_%EF%B7%BA_aux.pdf" target="_blank" rel="noopener">Consulter le PDF</a>.</p>
</div>
"""

# La balise de citation ouvrait avant l'encadré-clé et l'avalait : le titre
# « CE QUE LE TEXTE ÉTABLIT » se rendait à l'intérieur du bloc de citation, et
# la citation d'al-Jalālayn qui suivait n'était pas dans un <p>.
BQ_AVANT = '<blockquote class="tei-citation"><div class="tei-fait library">'
BQ_APRES = '<div class="tei-fait library">'
CIT_AVANT = ('\n\n\n« Suṭiḥat est évident en ce que la Terre est un saṭḥ (surface plane), '
             "et c'est l'avis des savants de la Sharīʿa (ʿulamāʾ al-sharʿ) — pas une sphère "
             "comme le disent les gens de l'astronomie (ahl al-hayʾa). »<footer>")
CIT_APRES = ('\n\n<blockquote class="tei-citation">\n<p>« <em>Suṭiḥat</em> est évident en ce que '
             "la Terre est un <em>saṭḥ</em> (surface plane), et c'est l'avis des savants de la "
             "Sharīʿa (<em>ʿulamāʾ al-sharʿ</em>) — pas une sphère comme le disent les gens de "
             "l'astronomie (<em>ahl al-hayʾa</em>). »</p>\n<footer>")


def cas_nommes(slug, html):
    notes = []
    if slug == "pres-de-cent-savants-de-lislam":
        if PDF_AVANT in html:
            html = html.replace(PDF_AVANT, PDF_APRES, 1)
            notes.append("bloc PDF remis en encadré, gestionnaires inline retirés")
        if BQ_AVANT in html:
            html = html.replace(BQ_AVANT, BQ_APRES, 1)
            html = html.replace(CIT_AVANT, CIT_APRES, 1)
            notes.append("la citation n'avale plus l'encadré-clé")
    return html, notes


# ═══════════════════════════════════════════════════════════════════════════

def main():
    total = {"h3": 0, "etiquette": 0, "p": 0, "encadres": 0, "footers": 0, "nommes": 0}
    modifies = []
    erreurs = []

    for f in sorted(os.listdir(ARTICLES)):
        if not f.endswith(".json"):
            continue
        slug = f[:-5]
        chemin = os.path.join(ARTICLES, f)
        with open(chemin, encoding="utf-8") as fh:
            data = json.load(fh)
        origine = data.get("htmlBody", "")
        html = origine
        journal = []

        # 3. cas nommés d'abord : ils suppriment du texte parasite (📄) et
        #    déplacent une balise, donc avant tout relevé de positions.
        html, notes = cas_nommes(slug, html)
        if notes:
            total["nommes"] += len(notes)
            journal += notes

        # 1. fragments hors conteneur — le texte doit rester identique
        avant = texte_nu(html)
        html, compte = traiter_runs(slug, html)
        if texte_nu(html) != avant:
            erreurs.append("%s : le texte a changé pendant l'enveloppement" % slug)
            continue
        for k in ("h3", "etiquette", "p"):
            total[k] += compte[k]
        if any(compte.values()):
            journal.append("%d sous-titres, %d étiquettes, %d paragraphes"
                           % (compte["h3"], compte["etiquette"], compte["p"]))

        # 2b. attributions : re-balisage pur, texte identique
        avant = texte_nu(html)
        html, n = attribution_en_footer(html)
        if n:
            if texte_nu(html) != avant:
                erreurs.append("%s : le texte a changé pendant la mise en footer" % slug)
                continue
            total["footers"] += n
            journal.append("%d attributions passées en <footer>" % n)

        # 2a. blockquotes qui ne citent personne
        if slug in SANS_CITATION:
            avant = texte_nu(html)
            html, n = blockquote_en_encadre(html)
            if n:
                if texte_nu(html) != avant:
                    erreurs.append("%s : le texte a changé pendant la conversion" % slug)
                    continue
                total["encadres"] += n
                journal.append("%d encadrés sortis de la balise de citation" % n)

        if html != origine:
            data["htmlBody"] = html
            with open(chemin, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            modifies.append(slug)
            print("── %s" % slug)
            for j in journal:
                print("   · %s" % j)

    for e in erreurs:
        print("  ✗ %s" % e)
    print("\n%d articles modifiés" % len(modifies))
    print("  %d sous-titres rendus à <h3>" % total["h3"])
    print("  %d étiquettes" % total["etiquette"])
    print("  %d paragraphes enveloppés" % total["p"])
    print("  %d attributions passées en <footer>" % total["footers"])
    print("  %d encadrés sortis de la balise de citation" % total["encadres"])
    print("  %d cas nommés" % total["nommes"])
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
