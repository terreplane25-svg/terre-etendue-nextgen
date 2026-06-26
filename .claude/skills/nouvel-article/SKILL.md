---
name: nouvel-article
description: Crée un nouvel article du site Terre Étendue Islam avec la structure homogène de sa page cible (Bibliothèque, Centre de Recherche, Observatoire ou Expériences). À utiliser quand l'utilisateur veut créer/scaffolder un nouvel article. Usage typique : "/nouvel-article observatoire Le titre de l'article".
---

# Créer un nouvel article homogène

Tu génères un nouvel article JSON respectant la charte du site. **Lis d'abord `CLAUDE.md`**
à la racine pour les conventions complètes (workflow git, images Hostinger, ArticleReader, etc.).

## Étapes

1. **Déterminer la page cible** depuis les arguments (ou demander si absent) :
   `library` | `headquarters` | `observatory` | `experiences`.
2. **Slug** : translittérer le titre en kebab-case sans accents (ex. « L'eau ne ment pas »
   → `leau-ne-ment-pas`). Le slug = nom de fichier.
3. **Construire le `htmlBody`** selon le gabarit de la page (ci-dessous).
4. **Écrire dans `content/articles/<slug>.json`** (dossier unique ; ne PAS copier ailleurs).
5. Ajouter l'image de couverture dans `src/lib/article-images.ts` (clé = slug).
6. `npx next build` puis commit + push sur `main` (voir CLAUDE.md).

## Schéma JSON

```json
{
  "title": "...",
  "description": "Résumé 1-2 phrases (meta + carte).",
  "date": "AAAA-MM-JJ",
  "category": "<page>",
  "tags": ["...", "..."],
  "pinned": false,
  "htmlBody": "<...>"
}
```

## Tronc commun (toutes pages)

- Ouvrir par `<p class="tei-lede">…</p>` (hook court). **Pas** de div couverture/sommaire.
- Sections : `<h2 id="..."><span class="tei-section-num">01</span>Titre</h2>` (01, 02… ; pas d'emoji).
- Encadré-clé via classe `tei-fait` (voir page).
- Section « Médias » (si vidéos) avant Sources.
- Section « Sources » OBLIGATOIRE en fin : `<h2 id="sources"><span class="tei-section-num">NN</span>Sources</h2>` + `<ol>`.
- Images Hostinger only + `data-zoomable` + légende italique.

## Encadré-clé par page

```html
<div class="tei-fait <category>">
  <span class="tei-fait-label">LABEL</span>
  <p>Fait clé.</p>
</div>
```

| category | LABEL |
|---|---|
| `library` | `CE QUE LE TEXTE ÉTABLIT` |
| `headquarters` | `FAIT ÉTABLI N°X` |
| `observatory` | `CE QUE MONTRENT LES DONNÉES` |
| `experiences` | `CE QUE L'EXPÉRIENCE ÉTABLIT` |

## Gabarits spécifiques

### library — édition critique savante-religieuse
Citations Coran/hadith en format unique :
```html
<blockquote class="tei-citation arabic-quote">
  <p>النص العربي</p>
  <p>Traduction française.</p>
  <footer>— An-Naml — S27 V61</footer>
</blockquote>
```
Notation : `Nom-translittéré — S<sourate> V<verset>`. Hadith : `Al-Bukhārī 3199, Ṣaḥīḥ`.
Translittération savante, ﷺ. Texte pur OK (images facultatives).

### headquarters — dossier d'investigation épistémologique
Intro « Avant de commencer » (hors numérotation) + résumé. Structure : affirmation
mainstream → mise en doute → réfutation → `Fait établi n°X`. Citations historiques
sourcées. SVG + portraits Hostinger.

### observatory — empirique-zététique
Tableaux de données (`<table>`), sources institutionnelles (NOAA/NASA/ESA/SHOM).
Schémas SVG optique/perspective. Encadré = données.

### experiences — démonstration reproductible
Protocole en `<h3>` : Matériel → Protocole (`<ol>`) → Ce qui se passe → Ce que ça change.
SVG faits-maison fond `#0d1117` + `data-zoomable`. Encadré = expérience.

## Rappels durs (CLAUDE.md)

- Push direct sur `main`, jamais de PR. Build avant commit.
- Un seul dossier (`content/articles/`). Jamais de Wikimedia ni de placeholder.
- Pas de `tei-article-cover` ni sommaire dans le HTML (ArticleReader les rend).
