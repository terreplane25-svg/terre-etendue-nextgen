#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rend à LIGO son article, et au dossier des trous noirs sa taille.

La fusion du 30 août faisait entrer les six sections de « LIGO : l'onde qui
n'existait pas » dans « Les trous noirs existent-ils ? », au motif que la
détection de 2015 est la principale observation avancée à l'appui de
l'existence des trous noirs. Le motif était bon ; le résultat ne l'est pas.

Deux raisons de revenir en arrière. La première est de dimension : le dossier
des trous noirs passait à 9 685 mots et treize sections, dont une seule pesait
11 500 caractères — un article dans l'article, que rien n'oblige un lecteur venu
pour les trous noirs à traverser. La seconde est de sujet : LIGO mesure une
déformation de l'espace-temps, et les objections qu'on lui oppose portent sur le
traitement du signal, les injections de test et l'ajustement à des gabarits.
C'est un dossier d'instrumentation. Il tient debout sans les trous noirs, et il
se cherche par son propre nom.

Ce qui reste dans le dossier des trous noirs : sa sous-section 6.4, « Les ondes
gravitationnelles : preuve ou inférence ? », qui y était avant la fusion et qui
traite la question au niveau où ce dossier en a besoin — l'inférence de l'objet
à partir du signal, et non la qualité du signal lui-même.

Le texte restitué n'est pas celui d'avant la fusion : c'est celui d'après, qui
avait gagné un avertissement en tête — aucune de ces objections n'est de nous,
et nous n'avons pas accès aux données. Il est conservé.
"""
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(RACINE, "content", "articles")
TROUS = os.path.join(A, "les-trous-noirs-existent-ils.json")
LIGO = os.path.join(A, "ligo-londe-qui-nexistait-pas.json")

LEGENDE = (
    '<p class="tei-src-legende">Chaque source porte sa classe de vérifiabilité. '
    "Elle ne dit pas si la source est bonne, mais ce qu&#8217;elle permet de "
    "faire&nbsp;: <b>A</b> mesure directe, protocole et instrument connus "
    "&#8212; conclure. <b>B</b> chemin mesuré mais indirect &#8212; borner. "
    "<b>C</b> valeur rapportée, calculée depuis un modèle, ou source primaire "
    "non consultée &#8212; illustrer, jamais conclure. <b>D</b> déclarative, "
    "affirmée sans donnée jointe &#8212; rien. <b>renvoi</b> désigne un de nos "
    "propres articles, qui n&#8217;est pas une source. La grille est détaillée "
    'dans <a href="/article/standards-et-methode">Standards et méthode</a>.</p>\n')

# Les cinq sources propres au dossier LIGO. La sixième — l'article de détection
# d'Abbott et al. — reste aussi chez les trous noirs, qui la citent en 6.4.
SOURCES_LIGO = """<ol>
<li><span class="tei-grade grade-b">B</span> B. P. Abbott et al. (LIGO Scientific Collaboration &amp; Virgo Collaboration), «&nbsp;Observation of Gravitational Waves from a Binary Black Hole Merger&nbsp;», <em>Physical Review Letters</em> 116, 061102, 2016. DOI&nbsp;: <a href="https://doi.org/10.1103/PhysRevLett.116.061102" target="_blank" rel="noopener noreferrer">10.1103/PhysRevLett.116.061102</a></li>
<li><span class="tei-grade grade-b">B</span> J. Creswell, S. von Hausegger, A. D. Jackson, H. Liu, P. Naselsky, «&nbsp;On the time lags of the LIGO signals&nbsp;», arXiv:1706.04191&nbsp;; publié dans <em>JCAP</em> 08(2017)013, DOI&nbsp;: <a href="https://doi.org/10.1088/1475-7516/2017/08/013" target="_blank" rel="noopener noreferrer">10.1088/1475-7516/2017/08/013</a> (Niels Bohr Institute, 2017).</li>
<li><span class="tei-grade grade-c">C</span> A. D. Jackson et al. (groupe de Copenhague, Niels Bohr Institute), analyses critiques de la qualité des données LIGO/Virgo, 2017-2019.</li>
<li><span class="tei-grade grade-c">C</span> P. Ulianov, X. Mei, P. Yu, «&nbsp;Was the Zero Lag Problem of LIGO and Virgo Signals Caused by 60 Hz Electrical Network Interference?&nbsp;», <em>Journal of Modern Physics</em>, 2016.</li>
<li><span class="tei-grade grade-c">C</span> X. Mei et al., analyse des formes d&#8217;ondes LIGO après filtrage (band-pass/band-stop), 2022.</li>
<li><span class="tei-grade grade-d">D</span> J. Kanner, A. Weinstein (LIGO/Caltech), sur les Blind Hardware Injections, <em>Wired</em>, 2016.</li>
<li><span class="tei-grade grade-lien">renvoi</span> <a href="/article/les-trous-noirs-existent-ils">Les trous noirs existent-ils&nbsp;?</a> — ce que la détection de 2015 permet et ne permet pas d&#8217;inférer sur l&#8217;objet qui l&#8217;aurait produite.</li>
<li><span class="tei-grade grade-lien">renvoi</span> <a href="/article/la-gravite-70-theories-et-aucune-preuve">La gravité&nbsp;: 70 théories et aucune preuve</a> — le cadre théorique dont ces ondes sont une prédiction.</li>
</ol>
"""

# Ce qui remplace la section retirée, chez les trous noirs : un renvoi, pas un
# résumé. Un résumé recréerait en trois paragraphes le doublon qu'on défait.
RENVOI_TROUS = """<p>Les objections méthodologiques adressées à la détection elle-même — injections de faux signaux à des fins de test, corrélations de bruit relevées par le groupe de Copenhague, circularité de l&#8217;ajustement aux gabarits — ne portent pas sur l&#8217;inférence du trou noir mais sur la qualité du signal. Elles relèvent d&#8217;un autre dossier, et elles y sont traitées&nbsp;: <a href="/article/ligo-londe-qui-nexistait-pas">LIGO&nbsp;: l&#8217;onde qui n&#8217;existait pas</a>.</p>
"""


def h3_en_h2(section):
    """Rend aux sous-sections leur rang de sections, numérotation comprise."""
    compteur = [0]

    def refaire(m):
        compteur[0] += 1
        ident, titre = m.group(1), m.group(2)
        return ('<h2 id="%s"><span class="tei-section-num">%02d</span>%s</h2>'
                % (ident, compteur[0], titre))

    section = re.sub(r'<h3 id="([^"]+)">(.*?)</h3>', refaire, section, flags=re.S)
    if compteur[0] != 6:
        sys.exit("6 sous-sections attendues, %d trouvées." % compteur[0])
    return section, compteur[0]


def main():
    if os.path.exists(LIGO):
        sys.exit("L'article LIGO existe déjà. Rien n'est écrit.")

    with open(TROUS, encoding="utf-8") as f:
        trous = json.load(f)
    html = trous["htmlBody"]

    debut = html.find('<h2 id="ligo">')
    if debut < 0:
        sys.exit("Section LIGO introuvable dans le dossier des trous noirs.")
    fin = html.find("<h2", debut + 10)
    section = html[debut:fin]

    # ── L'article LIGO ────────────────────────────────────────────────────
    corps = section[section.find("</h2>") + 5:]
    # Le paragraphe d'avertissement ouvre l'article au lieu d'ouvrir une section.
    m = re.match(r"\s*<p>(.*?)</p>", corps, re.S)
    if not m:
        sys.exit("Paragraphe d'introduction introuvable dans la section.")
    corps = corps[m.end():]
    corps, n = h3_en_h2(corps)

    lede = ('<p class="tei-lede">La détection d&#8217;ondes gravitationnelles de '
            "2015 est l&#8217;observation la plus citée de la physique "
            "contemporaine. Six objections méthodologiques lui ont été opposées "
            "dans la littérature&nbsp;; aucune n&#8217;est de nous, et nous "
            "n&#8217;avons pas accès aux données de LIGO.</p>\n")

    ligo_html = (lede + corps.rstrip() + "\n"
                 + '<h2 id="sources"><span class="tei-section-num">%02d</span>Sources</h2>\n' % (n + 1)
                 + LEGENDE + SOURCES_LIGO)

    ligo = {
        "title": "LIGO : l'onde qui n'existait pas",
        "description": (
            "Injections aveugles de faux signaux, corrélations de bruit relevées "
            "par le Niels Bohr Institute, ajustement circulaire aux gabarits, "
            "hypothèse d'une interférence électrique : six objections publiées à "
            "la détection de 2015, et l'état de leur réponse."),
        "date": "2025-05-20",
        "updated": "2026-08-31",
        "author": "Terre Etendue",
        "category": "headquarters",
        "tags": ["ligo", "ondes-gravitationnelles", "instrumentation",
                 "traitement-du-signal", "epistemologie", "relativite"],
        "pinned": False,
        "htmlBody": ligo_html,
    }

    # ── Le dossier des trous noirs ────────────────────────────────────────
    html = html[:debut] + RENVOI_TROUS + html[fin:]

    # Les cinq sources devenues sans objet ici. Abbott 2016 reste : la
    # sous-section 6.4 s'y appuie toujours.
    for motif in ["Creswell", "A. D. Jackson et al.", "Ulianov", "X. Mei et al.",
                  "Kanner"]:
        entrees = [li for li in re.findall(r"<li>.*?</li>", html, re.S) if motif in li]
        if len(entrees) != 1:
            sys.exit("Source « %s » : %d entrée(s) trouvée(s)." % (motif, len(entrees)))
        html = html.replace(entrees[0] + "\n", "").replace(entrees[0], "")

    # Le « Voir aussi » pointait sur l'ancienne adresse de LIGO, c'est-à-dire
    # sur la redirection, c'est-à-dire sur l'article lui-même.
    html = html.replace(
        '<a href="/article/ligo-londe-qui-nexistait-pas">LIGO&nbsp;: l&#8217;onde qui n&#8217;existait pas</a>',
        '<a href="/article/ligo-londe-qui-nexistait-pas">LIGO&nbsp;: l&#8217;onde qui n&#8217;existait pas</a>',
    )

    # Renumérotation : les sections qui suivaient la section retirée reculent.
    compteur = [0]

    def renumeroter(m):
        compteur[0] += 1
        return '<span class="tei-section-num">%02d</span>' % compteur[0]

    html = re.sub(r'<span class="tei-section-num">\d+</span>', renumeroter, html)
    trous["htmlBody"] = html
    trous["updated"] = "2026-08-31"

    for chemin, art in ((LIGO, ligo), (TROUS, trous)):
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(art, f, ensure_ascii=False, indent=2)
            f.write("\n")

    mots = lambda h: len(re.sub(r"<[^>]+>", " ", h).split())
    print("LIGO restauré : %d sections + sources, %d mots." % (n, mots(ligo_html)))
    print("Trous noirs : %d sections, %d mots (contre 13 et 9 685)."
          % (compteur[0], mots(html)))


if __name__ == "__main__":
    main()
