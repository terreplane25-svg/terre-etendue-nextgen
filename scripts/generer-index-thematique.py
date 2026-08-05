#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genere content/articles/index-thematique.json depuis les articles eux-memes.

L'index etait maintenu a la main et divergeait du corpus. Il est desormais
derive des tags : ajouter un article suffit, l'index suit.
"""
import json, glob, os, re, collections, unicodedata

PILIER = {'library': ('Bibliothèque', 'B'), 'headquarters': ('Centre de Recherche', 'Q'),
          'observatory': ('Observatoire', 'O'), 'experiences': ('Expériences', 'E'),
          'meta': ('À propos', 'M')}

def norme(t):
    """Les tags du corpus melangent accents et graphies : « epistemologie » et
    « épistémologie » coexistent. On normalise avant de comparer."""
    t = unicodedata.normalize('NFKD', t.lower()).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')

# Regroupement des tags en themes lisibles, sur tags normalises. Un article qui
# ne tombe dans aucun theme est classe par son pilier — jamais laisse de cote.
THEMES = {
  "La Terre — forme et surface": ['courbure','eau','fleche','horizon','hydrologie','geometrie','bedford',
                                  'rainy-lake','fecore','pontchartrain','reproductible','terre','marees',
                                  'antarctique','pole-sud','geographie','cartographie','navigation'],
  "Mesure et métrologie":        ['metrologie','geoide','refraction','hauteur-cachee','canigou','altitude',
                                  'nivellement','pre-enregistrement','puits-de-tranquillisation','protocole',
                                  'instruments','distances','parallaxe','triangulation','theodolite','mesure'],
  "Optique et atmosphère":       ['optique','perspective','lumiere','oeil','vision','atmosphere','pression',
                                  'pression-reduite','cloche-a-vide','mecanique-des-fluides','mirage'],
  "Ciel et astronomie":          ['lune','soleil','etoiles','astronomie','eclipse','planetes','cosmologie',
                                  'nasa','espace','satellites','trous-noirs','ligo','relativite'],
  "Épistémologie et méthode":    ['epistemologie','methode','zetetique','hypothese','standards','ethique',
                                  'transparence','corrections','erratum','observation','sources','consensus',
                                  'le-qg','concordisme'],
  "Sources coraniques et sunna": ['coran','sunna','tafsir','hadith','savants','islam','arabe','qibla',
                                  'exegese','versets','creation','la-bibliotheque'],
  "Histoire et transmission":    ['histoire','antiquite','grecs','eratosthene','transmission','rowbotham',
                                  'carpenter','newton','einstein','cia','hickson'],
  "Physique et forces":          ['gravite','densite','magnetisme','electricite','forces','mecanique',
                                  'electromagnetisme','physique-naturelle','rotation','coriolis'],
}

arts = []
for f in sorted(glob.glob('content/articles/*.json')):
    slug = os.path.basename(f)[:-5]
    if slug in ('index-thematique',):
        continue
    d = json.load(open(f, encoding='utf-8'))
    arts.append((slug, d.get('title', slug), d.get('category', '?'),
                 sorted({norme(t) for t in d.get('tags', [])})))

PAR_PILIER = {'library': "Sources coraniques et sunna", 'headquarters': "Épistémologie et méthode",
              'observatory': "La Terre — forme et surface", 'experiences': "Optique et atmosphère",
              'meta': "Épistémologie et méthode"}

par_theme = collections.OrderedDict((k, []) for k in THEMES)
for slug, titre, cat, tags in arts:
    place = False
    for theme, mots in THEMES.items():
        communs = [t for t in tags if t in mots]
        if communs:
            par_theme[theme].append((slug, titre, cat, communs))
            place = True
    if not place:
        # Repli par pilier : aucun article ne reste hors de l'index.
        par_theme[PAR_PILIER.get(cat, "Épistémologie et méthode")].append((slug, titre, cat, tags[:3]))
orphelins = []

def bloc(theme, items):
    if not items: return ''
    lignes = "".join(
        f'<li><a href="/article/{s}">{t}</a> '
        f'<span class="tei-index-pilier">{PILIER.get(c, (c, "?"))[0]}</span> '
        f'<span class="tei-index-tags">{" · ".join(tg)}</span></li>'
        for s, t, c, tg in sorted(items, key=lambda x: x[1]))
    sid = re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', theme).encode('ascii', 'ignore').decode().lower()).strip('-')
    return f'<h2 id="{sid}">{theme} <span class="tei-index-compte">{len(items)}</span></h2>\n<ul class="tei-index">{lignes}</ul>\n'

corps = "".join(bloc(k, v) for k, v in par_theme.items())
if orphelins:
    corps += bloc("Non classés", orphelins)

body = f"""
<p class="tei-lede">{len(arts)} articles, classés par thème. Un même article apparaît dans plusieurs thèmes s'il les traite tous.</p>
<p>Cet index est <strong>généré depuis les articles eux-mêmes</strong> et non tenu à la main : il ne peut donc pas diverger du corpus réel. Ajouter un article suffit à l'y faire figurer. Le script qui le produit est <code>scripts/generer-index-thematique.py</code>.</p>
{corps}"""

art = {
  "title": "Index thématique",
  "description": f"Les {len(arts)} articles du site classés par thème. Index généré depuis les articles, jamais tenu à la main.",
  "date": "2026-04-17",
  "updated": "2026-08-03",
  "author": "Terre Etendue",
  "category": "meta",
  "tags": ["index", "navigation", "themes"],
  "pinned": False,
  "htmlBody": body.strip(),
}
with open('content/articles/index-thematique.json', 'w', encoding='utf-8') as fh:
    json.dump(art, fh, ensure_ascii=False, indent=2); fh.write("\n")
print(f"index-thematique — {len(arts)} articles, {sum(1 for v in par_theme.values() if v)} thèmes, "
      f"{len(orphelins)} non classé(s)")
if orphelins:
    print("  non classés :", ", ".join(s for s, _, _, _ in orphelins))
