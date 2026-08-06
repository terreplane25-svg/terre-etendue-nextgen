#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pose les localisations que l'on peut établir sûrement, marque le reste.

Règle absolue, héritée du chantier précédent : ne jamais inventer une
pagination. Une référence fausse est pire qu'une référence absente, parce
qu'elle a l'air vérifiable.

Ce script n'ajoute donc une localisation que dans deux cas :

  · le repère est une subdivision nommée dont l'identité ne fait pas de doute
    — le chapitre « God's Utility Function » de River Out of Eden, le chapitre
    Tianwen du Huainanzi, la troisième lettre de Newton à Bentley ;
  · le numéro figure déjà, affirmé, dans la section Sources du même article, et
    n'est donc pas une information nouvelle : on le remonte simplement dans le
    pied de citation, là où le lecteur en a besoin.

Tout le reste — vingt-quatre citations, essentiellement des ouvrages
occidentaux dont la pagination demande d'avoir le volume en main — reçoit un
marqueur « (à paginer) » dans son pied. Le marqueur est discret, il est déjà
prévu par la feuille de style, et il dit au lecteur ce que nous savons et ce
que nous ne savons pas. Il disparaît de lui-même quand la pagination arrive.
"""

import importlib.util
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(RACINE, "content", "articles")

MARQUEUR = " <em>(à paginer)</em>"


# ═══════════════════════════════════════════════════════════════════════════
# Les localisations sûres — chacune avec son motif
# ═══════════════════════════════════════════════════════════════════════════

LOCALISATIONS = [
    # ── Le hadith de l'imitation. Les deux numéros figurent déjà dans la
    #    section Sources de l'article ; on les remonte dans le pied.
    ("le-concordisme",
     "Rapporté par Al-Bukhari et Muslim",
     "Rapporté par al-Bukhārī, <em>Ṣaḥīḥ</em> n° 3456, et Muslim, <em>Ṣaḥīḥ</em> n° 2669",
     "les deux numéros sont déjà affirmés dans la section Sources du même article"),

    # ── Newton à Bentley. Il existe quatre lettres ; le passage sur l'action à
    #    distance est celui de la troisième, du 25 février 1692/3. La date
    #    individue le document, ce que l'année seule ne faisait pas.
    ("chronologie-de-la-tromperie-du-globe",
     "— Isaac Newton, Lettre à Bentley, 1693",
     "— Isaac Newton, troisième lettre à Richard Bentley, 25 février 1693",
     "quatre lettres à Bentley existent ; le passage est celui de la troisième"),

    # ── L'Ad lectorem d'Osiander n'est pas paginé : c'est une préface d'une
    #    page et demie, en tête de l'édition de Nuremberg. La nommer et nommer
    #    l'édition est la localisation ; il n'y a pas de page à donner.
    ("chronologie-de-la-tromperie-du-globe",
     "avant-propos anonyme de <em>De revolutionibus orbium coelestium</em>, Nuremberg, 1543",
     "préface anonyme non paginée, en tête de <em>De revolutionibus orbium coelestium</em>, "
     "Nuremberg, 1543",
     "préface d'une page et demie, non paginée : la nommer suffit à la retrouver"),

    # ── Dawkins. Deux chapitres dont le titre ne fait pas de doute.
    ("la-cosmologie-comme-instrument-de-domination",
     "— Richard Dawkins, <em>River Out of Eden</em>, 1995",
     "— Richard Dawkins, <em>River Out of Eden</em>, 1995, ch. 4, « God's Utility Function »",
     "chapitre nommé, sans ambiguïté"),
    ("la-cosmologie-comme-instrument-de-domination",
     "— Richard Dawkins, <em>Le Gène Égoïste</em>, 1976",
     "— Richard Dawkins, <em>The Selfish Gene</em>, 1976, ch. 1, « Why are people? »",
     "chapitre nommé, sans ambiguïté"),

    # ── Popper. Le problème de l'induction ouvre le livre.
    ("pourquoi-tout-remettre-en-question",
     "— Karl Popper, La logique de la découverte scientifique, 1934",
     "— Karl Popper, <em>La Logique de la découverte scientifique</em>, 1934, ch. I § 1, "
     "« Le problème de l'induction »",
     "section nommée et numérotée, en ouverture de l'ouvrage"),

    # ── Le Huainanzi est divisé en vingt et un chapitres nommés.
    ("dune-terre-plate-universelle-a-la-sphere-grecque",
     "— Huainanzi (淮南子), IIᵉ siècle av. J.-C.",
     "— <em>Huainanzi</em> (淮南子), II<sup>e</sup> s. av. J.-C., ch. 3 « Tianwen » (天文, Motifs célestes)",
     "chapitre nommé parmi les vingt et un du recueil"),

    # ── Le propos prêté à Einstein sur Michelson circule sans référence. Il
    #    remonte à la conférence de Kyoto, connue par les notes d'un auditeur :
    #    c'est une reconstitution, et le lecteur doit le savoir.
    ("chronologie-de-la-tromperie-du-globe",
     "— Albert Einstein",
     "— Albert Einstein, conférence de Kyoto, 14 décembre 1922 — texte connu par les notes "
     "de Jun Ishiwara, donc une reconstitution et non une transcription",
     "date individuante, et réserve sur la nature du témoignage"),
]


def detecteur():
    """Réutilise le motif du script de relevé, pour que marquage et relevé ne
    puissent jamais diverger : une seule définition de « localisé »."""
    chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "lister-citations-a-localiser.py")
    source = open(chemin, encoding="utf-8").read()
    # Le script produit un fichier en s'exécutant : on n'en extrait que le motif.
    debut = source.index("LOC = re.compile(")
    fin = source.index("todo, total")
    espace = {"re": re}
    exec(compile(source[debut:fin], chemin, "exec"), espace)
    return espace["LOC"]


def marquer(html, LOC):
    """Ajoute « (à paginer) » au pied des citations non localisées."""
    n = 0

    def sub(m):
        nonlocal n
        bloc = m.group(0)
        fo = re.search(r"<footer>(.*?)</footer>", bloc, re.S)
        if not fo or "à paginer" in fo.group(1):
            return bloc
        if LOC.search(re.sub("<[^>]+>", " ", bloc)):
            return bloc
        n += 1
        return bloc.replace(fo.group(0),
                            "<footer>%s%s</footer>" % (fo.group(1).rstrip(), MARQUEUR), 1)

    return re.sub(r"<blockquote[^>]*>.*?</blockquote>", sub, html, flags=re.S), n


def appliquer(html, avant, apres):
    """Remplace dans les pieds de citation uniquement."""
    n = 0
    def sub(m):
        nonlocal n
        corps = m.group(1)
        if avant in corps:
            n += 1
            return "<footer>%s</footer>" % corps.replace(avant, apres, 1)
        return m.group(0)
    return re.sub(r"<footer>(.*?)</footer>", sub, html, flags=re.S), n


def main():
    poses, deja, notes = 0, 0, []
    for slug, avant, apres, motif in LOCALISATIONS:
        chemin = os.path.join(ARTICLES, slug + ".json")
        with open(chemin, encoding="utf-8") as f:
            data = json.load(f)
        # Idempotence : si la localisation est déjà posée, on passe. Le script
        # doit pouvoir être relancé sans échouer sur son propre résultat.
        if apres in data["htmlBody"]:
            deja += 1
            continue
        html, n = appliquer(data["htmlBody"], avant, apres)
        if n == 0:
            print("  ✗ %s : motif introuvable — %r" % (slug, avant[:56]))
            return 1
        if n > 1:
            print("  ✗ %s : motif trouvé %d fois, ambigu" % (slug, n))
            return 1
        data["htmlBody"] = html
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        poses += 1
        notes.append("%s — %s" % (slug, motif))

    print("  ✓ %d localisations posées%s"
          % (poses, ", %d déjà en place" % deja if deja else ""))
    for n in notes:
        print("     · %s" % n)

    # ── marquage du reste ──
    LOC = detecteur()
    marquees = 0
    for f in sorted(os.listdir(ARTICLES)):
        if not f.endswith(".json"):
            continue
        chemin = os.path.join(ARTICLES, f)
        with open(chemin, encoding="utf-8") as fh:
            data = json.load(fh)
        html, n = marquer(data.get("htmlBody", ""), LOC)
        if n:
            data["htmlBody"] = html
            with open(chemin, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            marquees += n
            print("     %-52s %d marquée(s)" % (f[:-5], n))
    print("  ✓ %d citations marquées « à paginer »" % marquees)
    return 0


if __name__ == "__main__":
    sys.exit(main())
