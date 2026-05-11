# Guide de Migration : Elementor/WordPress vers Next.js

Ce guide explique comment migrer vos articles existants depuis votre blog
WordPress/Elementor vers la plateforme Terre Etendue Islam.

## Etape 1 : Exporter les articles WordPress

### Option A : Export XML natif
1. Dans WordPress, aller dans Outils > Exporter
2. Selectionner "Articles" et telecharger le fichier XML

### Option B : Plugin WP All Export
1. Installer WP All Export
2. Exporter en CSV avec les champs : titre, contenu, date, categories, tags

## Etape 2 : Convertir en Markdown

Pour chaque article, creer un fichier `.md` dans `content/articles/` :

### Structure du frontmatter

```yaml
---
title: "Votre titre"
description: "Resume en 1-2 phrases"
date: "2026-01-15"
author: "Auteur"
category: "library"
tags: ["tag1", "tag2"]
connections: ["slug-article-lie"]
---
```

### Categorie (category)

Attribuez chaque article a un des 4 piliers :

- `headquarters` : Articles epistemologiques, methodologiques
- `observatory` : Donnees empiriques, observations scientifiques
- `library` : Sources coraniques, hadiths, textes classiques
- `lab` : Modeles, formules, simulations

### Convertir le HTML en Markdown

Utilisez un outil comme :
- https://www.convertsimple.com/convert-html-to-markdown/
- Ou en ligne de commande : `pandoc article.html -t markdown -o article.md`

## Etape 3 : Adapter le contenu

### Citations sacrees
Utilisez les blockquotes Markdown avec le format standard :

```markdown
> Dis : Il est Dieu, l Unique. -- Sourate Al-Ikhlas (112:1)
```

Elles seront automatiquement stylisees avec une bordure doree.

### Termes du glossaire
Les mots suivants sont automatiquement enrichis avec des pop-ups :
tawhid, kalam, singularite, fractale, sourate, ayah,
geodesique, hadith, topologie, isnad

Pour ajouter de nouveaux termes, editez `src/components/GlossaryTooltip.tsx`.

### Tableaux
Utilisez la syntaxe Markdown standard :

```markdown
| Colonne 1 | Colonne 2 |
|-----------|-----------|
| Valeur    | Valeur    |
```

### Connexions entre articles
Le champ `connections` dans le frontmatter definit les liens
visibles dans le Nexus Graph. Utilisez les slugs des autres articles.

## Etape 4 : Verifier

```bash
npm run dev
```

1. Verifiez que l article apparait dans le bon pilier
2. Verifiez le rendu Markdown (titres, tableaux, citations)
3. Verifiez que les termes du glossaire sont soulignés
4. Verifiez les connexions dans le Nexus

## Etape 5 : Rediriger l ancien site

Si vous gardez l ancien domaine, configurez des redirections 301 :

```
# Dans votre .htaccess ou config Vercel
/ancien-slug -> /article/nouveau-slug
```

### Fichier vercel.json pour les redirections

```json
{
  "redirects": [
    {
      "source": "/ancien-article-wordpress",
      "destination": "/article/nouveau-slug",
      "permanent": true
    }
  ]
}
```

## Outils utiles

- **pandoc** : Conversion HTML vers Markdown en batch
- **turndown** : Librairie JS pour HTML-to-Markdown
- **gray-matter** : Deja inclus dans le projet pour parser le frontmatter
