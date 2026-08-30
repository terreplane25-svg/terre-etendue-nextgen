#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Applique la grille A/B/C/D à chaque entrée de source, sur les 60 articles.

    python3 scripts/graduer-sources.py

Le script n'est pas idempotent : il ajoute une pastille en tête de chaque
entrée. Le relancer sur des articles déjà notés les doublerait. Repartir de
l'état du dépôt avant de le rejouer.

La grille est celle déjà énoncée dans « Standards et méthode », section 02 :

  A  mesure directe de la grandeur, protocole et instrument connus  → conclure
  B  chemin mesuré, mais indirect                                   → borner
  C  valeur rapportée, calculée depuis un modèle,
     ou source primaire non consultée                               → illustrer
  D  déclarative : affirmée sans donnée jointe                      → rien

Pour les sources textuelles, la même échelle se lit ainsi — c'est ce que dit
déjà la section 02 : « un manuscrit consulté n'est pas une citation de seconde
main, et un hadith porte son auteur, son numéro et son grade comme une mesure
porte son instrument ».

  A  source primaire à référence exacte : hadith avec recueil et numéro,
     manuscrit avec sa cote, verset avec sourate et numéro, texte officiel daté
  B  source primaire localisée par tome et page, ou par le verset commenté
  C  source primaire sans localisation, travail d'historien, manuel, synthèse
  D  affirmation sans référence localisable

Une cinquième valeur, « lien », marque les renvois vers nos propres articles.
Ce ne sont pas des sources et les noter reviendrait à se citer soi-même comme
preuve.

La note ne dit pas si la source est bonne. Elle dit ce qu'elle permet de faire.
Un manuel de physique en classe C dans un article d'explication est à sa place :
il illustre, et l'article n'en demande pas plus.

La note vit dans le <li>, donc dans le JSON de l'article, donc au même endroit
que la citation qu'elle qualifie. Un registre séparé se serait désaligné à la
première source ajoutée.

Le balisage n'est pas inventé ici : `tei-grade` / `grade-a…d` existait déjà,
stylé dans globals.css, et employé dans quatre articles de la Bibliothèque.
On l'étend, on ne le double pas. Seule différence : la pastille passe en tête
de l'entrée plutôt qu'en fin, parce qu'à 518 sources ce qui compte est de
pouvoir balayer une colonne de notes du regard.

Les quatre articles déjà notés servent de contrôle : leurs notes existantes
sont comparées aux nôtres avant d'être remplacées, et tout désaccord est
signalé plutôt que silencieusement écrasé.
"""

import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(RACINE, "content", "articles")

# ─────────────────────────────────────────────────────────────────────────────
# Les notes, dans l'ordre des entrées de chaque liste de sources.
# ─────────────────────────────────────────────────────────────────────────────
NOTES = {
# ══ CENTRE DE RECHERCHE ═════════════════════════════════════════════════════
"200-ans-de-resultats-nuls-darago-a-einstein":
    "B B C B C B B C C C C B C C C".split(),
"chronologie-de-la-tromperie-du-globe":
    "C C C C C C C B C C C C B B D D D D D A D C D B C".split(),
"dune-terre-plate-universelle-a-la-sphere-grecque":
    "C C C C C C C C C C C C C B C C C C C C C C C C".split(),
"kings-dethroned-leffondrement-de-la-triangulation-stellaire":
    "D C C B C C".split(),
"la-cosmologie-comme-instrument-de-domination":
    "D D D C C A".split(),
"la-gravite-70-theories-et-aucune-preuve":
    "C C A A B D B".split(),
"la-rotation-terrestre-deux-experiences-zero-preuve":
    "C C B B B B B C C C D C B C C C D D B C B B B C B B C".split(),
"le-concordisme":
    "B B C C B C C C B B B C C D B B B A".split(),
"le-mouvement-zetetique-150-ans-de-resistance":
    "D D D D C D".split(),
"le-mythe-deratosthene":
    "C C D C C C C C C C D C".split(),
"les-distances-cosmiques-au-dela-de-la-regle":
    "D B C B C B".split(),
"les-trous-noirs-nexistent-pas":
    "C C C C C C C D".split(),
"lhypothese-nulle-dynamique-et-cinematique":
    "D C C C C A B D D C C C D C D".split(),
"ligo-londe-qui-nexistait-pas":
    "B B C C C D".split(),
"lire-le-ciel-avant-le-globe":
    "C D C D C C C C C C C C".split(),
"neptune-et-pluton-les-faux-triomphes":
    "B C D C C D D D C B D".split(),
"par-rapport-a-quoi-mesure-t-on-une-altitude":
    "C B B A B C B B B A A A A A A A".split(),
"pourquoi-tout-remettre-en-question":
    "C C C C C C B B C C C B C C".split(),

# ══ OBSERVATOIRE ════════════════════════════════════════════════════════════
"cartes-routes-boussoles-et-le-mystere-antarctique":
    "C C D C C A A A D D C D C C".split(),
"la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre":
    "C D C D C B A".split(),
"la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas":
    "C D C D B A".split(),
"la-perspective-atmospherique":
    "C B A C A".split(),
"la-perspective-lineaire":
    "C C A D C".split(),
"la-perspective-pourquoi-les-objets-disparaissent":
    "B B D D C C C D C C C D C".split(),
"le-pole-sud-nexiste-pas":
    "A A A C B".split(),
"le-theodolite-celeste":
    "D A C C C C D C C D".split(),
"les-marees-contre-lheliocentrisme":
    "A A B A D C C C".split(),
"lespace-une-frontiere-infranchissable":
    "C C C C C C B D D".split(),
"lhorizon-la-perspective-et-la-refraction":
    "C D C C D D".split(),
"mesurer-la-courbure-sur-l-eau-cinq-campagnes":
    "A C C C C C C C D A A A lien lien lien".split(),
"vols-avion-et-courbure-terrestre":
    "C B B B B B B B B B B B B B B B B B B B C C A".split(),

# ══ BIBLIOTHÈQUE ════════════════════════════════════════════════════════════
"debut-de-la-creation-le-soleil-mobile-la-terre-immobile":
    "A A A C".split(),
"debut-de-la-creation-selon-le-coran-et-la-sunna":
    "D C C C".split(),
"dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne":
    "A A A C C C C C C B".split(),
"la-mobilite-de-la-terre-attribuee-a-ibn-taymiyyah":
    "B C D D D D D B".split(),
"la-qibla-et-la-direction-cote-ouest":
    "C C C A".split(),
"la-terre-dans-le-coran":
    "B B B B B B B C C D".split(),
"le-consensus-sur-la-sphericite":
    "B B C C C B C".split(),
"levolution-et-lislam":
    "A C C D".split(),
"mise-en-garde-la-kaaba-et-saturne":
    "A C C C".split(),
"ou-est-allah-le-uluww-et-la-forme-du-monde":
    "C C A A A B B B B B B B B B B B B B C".split(),
"pres-de-cent-savants-de-lislam":
    "C D C C C C C".split(),
"sources-historiques-fonds-documentaire":
    "D D D C".split(),
"un-traite-ottoman-contre-la-sphericite-1314h":
    # [1] : notre première note était B. La justification déjà écrite dans
    # l'article disait « traducteur non identifié » — une traduction anonyme
    # ne borne rien. Le C qui était en place avait raison contre nous.
    "A C A A A B B".split(),

# ══ EXPÉRIENCES ═════════════════════════════════════════════════════════════
"densite-pourquoi-les-choses-montent-et-descendent":
    "C C D A A A C".split(),
"electricite-statique-attraction-repulsion":
    "A C C C C".split(),
"experiences-sous-pression-reduite":
    "B B B B A".split(),
"la-pression-atmospherique-un-ocean-d-air-invisible":
    "B B B B A B".split(),
"leau-ne-ment-pas":
    "D C D A C C C".split(),
"les-protocoles-ce-que-c-est-et-pourquoi":
    "A C A C lien C".split(),
"loeil-humain-la-machine-a-voir-qui-faconne-notre-realite":
    "C A C A A C".split(),
"magnetisme-et-electromagnetisme":
    "B B C D".split(),
"monter-l-experience-des-trois-mires":
    "A C C A C C D lien lien".split(),
"pression-lumiere-halos-rayons-et-ondes":
    "D D C C C C C".split(),
"principe-action-reaction":
    "C D C D".split(),
}

# ─────────────────────────────────────────────────────────────────────────────
# Les notes déjà écrites en clair dans trois articles de la Bibliothèque.
# On les transforme en attribut plutôt que de les doubler : la lettre passe
# dans data-src, la justification qui la suivait reste en toutes lettres.
# ─────────────────────────────────────────────────────────────────────────────
DEJA_NOTES = {
    "la-mobilite-de-la-terre-attribuee-a-ibn-taymiyyah",
    "ou-est-allah-le-uluww-et-la-forme-du-monde",
    "un-traite-ottoman-contre-la-sphericite-1314h",
}

# Une pastille déjà posée, en fin d'entrée, éventuellement suivie de sa
# justification introduite par un tiret.
RE_PASTILLE = re.compile(
    r"\s*<span class=\"tei-grade grade-([abcd])\">[ABCD]</span>"
    r"(?:\s*(?:—|&mdash;|&#8212;)\s*(?P<note>.*?))?\s*$", re.S)
# Une lettre écrite en clair, sans balise, en fin d'entrée.
RE_LETTRE_NUE = re.compile(r"(?:\s|&nbsp;)+([ABCD])\s*$")

LIBELLE = {"lien": "renvoi"}


def extraire(corps):
    """Sépare la note déjà posée, s'il y en a une, du corps de l'entrée.

    Rend (corps nettoyé, note existante ou None). La justification qui suivait
    la pastille est conservée : elle dit pourquoi la note est celle-là, et
    c'est la partie qui a demandé du travail.
    """
    m = RE_PASTILLE.search(corps)
    if m:
        reste = corps[:m.start()].rstrip()
        note = m.group("note")
        if note:
            reste += ' <em class="tei-src-note">%s</em>' % note.strip()
        return reste, m.group(1).upper()
    m = RE_LETTRE_NUE.search(corps)
    if m:
        return corps[:m.start()].rstrip(), m.group(1)
    return corps.strip(), None


# Le rappel de la grille, posé une fois en tête de chaque liste de sources.
#
# Écrit dans le HTML de l'article, et non injecté par le composant de lecture.
# La première version passait par un effet client ; elle ne s'affichait pas du
# tout dans un navigateur qui n'exécute pas le script — et c'est justement le
# lecteur méfiant, celui qui coupe le JavaScript, qui a le plus besoin de
# savoir ce que vaut chaque source.
LEGENDE = (
    '<p class="tei-src-legende">Chaque source porte sa classe de vérifiabilité. '
    'Elle ne dit pas si la source est bonne, mais ce qu&#8217;elle permet de '
    'faire&nbsp;: <b>A</b> mesure directe, protocole et instrument connus '
    '&#8212; conclure. <b>B</b> chemin mesuré mais indirect &#8212; borner. '
    '<b>C</b> valeur rapportée, calculée depuis un modèle, ou source primaire '
    'non consultée &#8212; illustrer, jamais conclure. <b>D</b> déclarative, '
    'affirmée sans donnée jointe &#8212; rien. <b>renvoi</b> désigne un de nos '
    'propres articles, qui n&#8217;est pas une source. La grille est détaillée '
    'dans <a href="/article/standards-et-methode">Standards et méthode</a>.</p>'
)


def pastille(note):
    return '<span class="tei-grade grade-%s">%s</span> ' % (
        note.lower(), LIBELLE.get(note, note))


def bloc_sources(html):
    """La zone qui suit le titre Sources, jusqu'au prochain <h2> ou à la fin.

    Toutes les listes de sources ne sont pas un <ol> unique : plusieurs
    articles les regroupent en <ul> sous des <h3> thématiques. On prend donc
    toute la section, et on traite les <li> qu'elle contient, quel que soit
    leur contenant.
    """
    m = re.search(r'id="sources"', html)
    if not m:
        return None
    # Après la FERMETURE du titre, pas après l'ouverture de sa balise : un <p>
    # glissé dans un <h2> est remonté par le navigateur au-dessus du titre.
    d = html.find("</h2>", m.end())
    if d < 0:
        return None
    d += len("</h2>")
    suite = re.search(r"<h2[\s>]", html[d:])
    f = d + suite.start() if suite else len(html)
    return (d, f)


def main():
    # Deux temps : tout calculer, tout vérifier, et n'écrire qu'ensuite. Une
    # première version écrivait au fil de la boucle ; un échec au deuxième
    # article a laissé le premier modifié et le reste intact, c'est-à-dire le
    # dépôt dans un état que personne n'avait voulu.
    total = 0
    a_ecrire = []
    desaccords = []
    for slug, notes in sorted(NOTES.items()):
        chemin = os.path.join(ARTICLES, slug + ".json")
        data = json.load(open(chemin, encoding="utf-8"))
        html = data["htmlBody"]
        bornes = bloc_sources(html)
        if not bornes:
            sys.exit("  ✗ %s : pas de liste de sources" % slug)
        d, f = bornes
        bloc = html[d:f]

        lis = list(re.finditer(r"<li(?P<attrs>[^>]*)>(?P<corps>.*?)</li>", bloc, re.S))
        if len(lis) != len(notes):
            sys.exit("  ✗ %s : %d entrées, %d notes" % (slug, len(lis), len(notes)))

        neuf = []
        pos = 0
        for i, (m, note) in enumerate(zip(lis, notes)):
            neuf.append(bloc[pos:m.start()])
            corps, ancienne = extraire(m.group("corps"))
            if ancienne and ancienne != note:
                desaccords.append((slug, i, ancienne, note))
            neuf.append("<li%s>%s%s</li>" % (m.group("attrs"), pastille(note), corps))
            pos = m.end()
        neuf.append(bloc[pos:])

        section = "".join(neuf)
        if "tei-src-legende" not in section:
            section = "\n" + LEGENDE + section
        data["htmlBody"] = html[:d] + section + html[f:]
        a_ecrire.append((chemin, data))
        total += len(notes)

    for chemin, data in a_ecrire:
        with open(chemin, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
            fh.write("\n")

    if desaccords:
        print("  ! désaccord avec une note déjà posée :")
        for slug, i, ancienne, neuve in desaccords:
            print("      %s [%d] : %s → %s" % (slug, i, ancienne, neuve))
    print("  ✓ %d articles, %d sources notées" % (len(a_ecrire), total))
    from collections import Counter
    c = Counter(n for v in NOTES.values() for n in v)
    for k in ("A", "B", "C", "D", "lien"):
        print("     %-5s %3d  (%.0f %%)" % (k, c[k], 100 * c[k] / total))


main()
