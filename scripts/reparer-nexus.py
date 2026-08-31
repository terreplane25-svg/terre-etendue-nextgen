#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Régénère src/lib/nexus-data.ts depuis le corpus réel.

Le graphe avait dérivé du corpus qu'il est censé représenter : titres d'articles
abandonnés depuis des mois, catégories fausses, un nœud fantôme laissé par une
fusion, un article absent, et sept champs par nœud que plus rien ne lit — dont
un `wordCount` à zéro pour 49 nœuds sur 52 et une couleur par nœud contredisant
la palette des piliers.

Ce script reconstruit le fichier à partir de la seule source qui fasse foi :
`content/articles/*.json`. Les titres et les catégories en viennent. Ce qui est
du travail humain — le domaine principal et les domaines partagés, les liens et
leurs scores — est conservé tel quel.

Le lancer est sans risque : il est idempotent et ne lit jamais sa propre sortie
comme une source.
"""
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(RACINE, "content", "articles")
CIBLE = os.path.join(RACINE, "src", "lib", "nexus-data.ts")

# Le nœud fantôme : « Le pendule de Foucault » a été absorbé dans le dossier
# sur la rotation terrestre, mais son nœud est resté, repointé sur l'identifiant
# de l'article absorbant. Deux points sur le graphe, deux titres, un seul
# article — et un `Map` par identifiant qui n'en garde qu'un au hasard.
FANTOMES = {"Le pendule de Foucault : une preuve contestée"}

# L'article de participation est né après la dernière génération du graphe.
# Ses liens sont posés à la main, faute de calcul de similarité disponible ;
# ils sont donc volontairement peu nombreux et évidents.
LIENS_AJOUTES = [
    ("participer-aux-campagnes-de-mesure", "les-protocoles-ce-que-c-est-et-pourquoi",
     "strong", ["epistemologie", "modelisation"]),
    ("participer-aux-campagnes-de-mesure", "monter-l-experience-des-trois-mires",
     "medium", ["geometrie", "epistemologie"]),
    ("participer-aux-campagnes-de-mesure", "standards-et-methode",
     "medium", ["epistemologie"]),
]
DOMAINES_AJOUTES = {
    "participer-aux-campagnes-de-mesure": ("epistemologie",
                                           ["epistemologie", "modelisation", "physique"]),
}
SCORE_AJOUTE = {"strong": 250.0, "medium": 150.0, "weak": 60.0}


def corpus():
    """Les articles réels, indexés par slug — le slug vient du nom de fichier."""
    out = {}
    for nom in sorted(os.listdir(ARTICLES)):
        if not nom.endswith(".json"):
            continue
        with open(os.path.join(ARTICLES, nom), encoding="utf-8") as f:
            d = json.load(f)
        out[nom[:-5]] = (d["title"], d["category"])
    return out


def ancien(src):
    """Ce qu'on garde de l'ancien fichier : les domaines et les liens."""
    domaines, fantomes = {}, set()
    bloc = re.compile(
        r'"id":\s*"([^"]+)",\s*"title":\s*"((?:[^"\\]|\\.)*)".*?'
        r'"primaryDomain":\s*"([^"]+)",\s*"topDomains":\s*\[([^\]]*)\]', re.S)
    for nid, titre, principal, top in bloc.findall(src):
        titre = titre.replace('\\"', '"')
        liste = re.findall(r'"([^"]+)"', top)
        if titre in FANTOMES:
            fantomes.add(nid)
            # Le fantôme disparaît, mais ses domaines décrivaient bien du contenu
            # qui, lui, existe toujours dans l'article absorbant.
            deja = domaines.get(nid)
            if deja:
                fusion = deja[1] + [d for d in liste if d not in deja[1]]
                domaines[nid] = (deja[0], fusion[:4])
            continue
        domaines[nid] = (principal, liste)

    liens = []
    for m in re.finditer(
            r'"source":\s*"([^"]+)",\s*"target":\s*"([^"]+)",\s*"score":\s*([\d.]+),'
            r'\s*"strength":\s*"([^"]+)",\s*"sharedDomains":\s*\[([^\]]*)\]', src):
        s, t, score, force, dom = m.groups()
        liens.append((s, t, float(score), force, re.findall(r'"([^"]+)"', dom)))
    return domaines, liens, fantomes


def main():
    with open(CIBLE, encoding="utf-8") as f:
        src = f.read()
    arts = corpus()
    domaines, liens, fantomes = ancien(src)

    manquants = [s for s in arts if s not in domaines and s not in DOMAINES_AJOUTES]
    if manquants:
        sys.exit("Domaines inconnus pour : %s\n"
                 "Les renseigner dans DOMAINES_AJOUTES avant de relancer." % manquants)
    domaines.update(DOMAINES_AJOUTES)

    noeuds = []
    for slug in sorted(arts, key=lambda s: arts[s][0].lower()):
        titre, cat = arts[slug]
        principal, top = domaines[slug]
        noeuds.append({"id": slug, "title": titre, "category": cat,
                       "primaryDomain": principal, "topDomains": top})

    # Les liens : on écarte ce qui pointe hors corpus, on replie les doublons
    # créés par les fusions — deux articles devenus un n'ont plus de lien entre
    # eux — et on garde le score le plus fort de chaque paire.
    par_paire = {}
    for s, t, score, force, dom in liens + [
            (a, b, SCORE_AJOUTE[f], f, d) for a, b, f, d in LIENS_AJOUTES]:
        if s not in arts or t not in arts or s == t:
            continue
        cle = tuple(sorted((s, t)))
        vieux = par_paire.get(cle)
        if vieux is None or score > vieux[2]:
            fusion = dom if vieux is None else dom + [d for d in vieux[4] if d not in dom]
            par_paire[cle] = (s, t, score, force, fusion)
        else:
            s2, t2, sc2, f2, d2 = vieux
            par_paire[cle] = (s2, t2, sc2, f2, d2 + [d for d in dom if d not in d2])
    finaux = sorted(par_paire.values(), key=lambda l: -l[2])

    j = lambda o: json.dumps(o, ensure_ascii=False)
    lignes = [
        "// ═══════════════════════════════════════════════════════",
        "// NEXUS DATA — %d articles, %d liens" % (len(noeuds), len(finaux)),
        "// Terre Étendue Islam — Graphe de connaissances",
        "//",
        "// Fichier généré. Ne pas éditer à la main :",
        "//   python3 scripts/reparer-nexus.py",
        "//",
        "// Les titres et les catégories viennent de content/articles/*.json,",
        "// seule source qui fasse foi. Les domaines et les liens sont conservés",
        "// d'une génération à l'autre : ce sont eux le travail humain.",
        "// ═══════════════════════════════════════════════════════",
        "",
        "export interface NexusNodeData {",
        "  id: string;",
        "  title: string;",
        "  category: 'headquarters' | 'observatory' | 'library' | 'experiences' | 'meta';",
        "  primaryDomain: string;",
        "  topDomains: string[];",
        "}",
        "",
        "export interface NexusLinkData {",
        "  source: string;",
        "  target: string;",
        "  score: number;",
        "  strength: 'strong' | 'medium' | 'weak';",
        "  sharedDomains: string[];",
        "}",
        "",
        "export const DOMAIN_LABELS: Record<string, string> = {",
    ]
    for cle, lib in re.findall(r'"([a-z_]+)": "([^"]+)"',
                              re.search(r"DOMAIN_LABELS[^{]*\{(.*?)\n\};", src, re.S).group(1)):
        lignes.append('  %s: %s,' % (j(cle), j(lib)))
    lignes += ["};", "", "export const NEXUS_NODES: NexusNodeData[] = ["]
    for n in noeuds:
        lignes += ["  {",
                   '    "id": %s,' % j(n["id"]),
                   '    "title": %s,' % j(n["title"]),
                   '    "category": %s,' % j(n["category"]),
                   '    "primaryDomain": %s,' % j(n["primaryDomain"]),
                   '    "topDomains": %s' % j(n["topDomains"]),
                   "  },"]
    lignes += ["];", "", "export const NEXUS_LINKS: NexusLinkData[] = ["]
    for s, t, score, force, dom in finaux:
        lignes += ["  {",
                   '    "source": %s,' % j(s),
                   '    "target": %s,' % j(t),
                   '    "score": %s,' % round(score, 1),
                   '    "strength": %s,' % j(force),
                   '    "sharedDomains": %s' % j(dom),
                   "  },"]
    lignes += ["];", ""]

    with open(CIBLE, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes))

    isoles = [n["id"] for n in noeuds
              if not any(n["id"] in (s, t) for s, t, *_ in finaux)]
    print("%d nœuds, %d liens écrits." % (len(noeuds), len(finaux)))
    if fantomes:
        print("Nœud fantôme retiré : %s" % ", ".join(sorted(fantomes)))
    print("Sans aucun lien : %s" % (", ".join(isoles) if isoles else "aucun"))


if __name__ == "__main__":
    main()
