# Terre Étendue Islam — Guide du projet

Site de recherche en cosmologie (Next.js 15 App Router, React 19, TypeScript) qui examine
la cosmologie coranique et la science moderne avec la même rigueur. Ton pédagogique,
bienveillant, jamais méprisant.

## Workflow git (IMPÉRATIF)

- **Push directement sur `main`.** Pas de branche, pas de PR, pas de merge, pas de preview.
- Vérifier `npx next build` AVANT chaque commit.
- Push avec retry backoff exponentiel (2s, 4s, 8s, 16s) sur erreurs réseau.
- Ne JAMAIS créer de PR sauf demande explicite.
- Trailer de commit :
  ```
  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
  ```
- Ne jamais mettre l'identifiant de modèle dans un commit/artefact poussé.

## Système d'articles

- Articles = fichiers JSON dans `content/articles/<slug>.json`. **Source unique.**
- `content/articles/` est le SEUL dossier lu (`src/lib/articles.ts`, `src/app/sitemap.ts`).
  Ne PAS copier dans `public/content/articles/` (dossier mort, non servi, supprimé).
- Le **slug vient du nom de fichier** (le champ `slug` du JSON est ignoré).
- `readTime` est **recalculé automatiquement** depuis `htmlBody` (champ JSON ignoré).
- `author` par défaut = "Terre Etendue".
- Schéma JSON : `title`, `description`, `date`, `category`, `tags`, `pinned`, `htmlBody`.
- Catégories valides : `library`, `headquarters`, `observatory`, `experiences`, `lab`, `meta`.
- Le contenu vit dans `htmlBody` (HTML inline). Trop gros pour l'outil Edit → manipuler
  via scripts Python (échapper backticks/`${}` pour les template literals TS).

### ArticleReader (CRITIQUE)
- Le composant `ArticleReader` rend **automatiquement** l'image de couverture + le
  sommaire (TOC hamburger). **NE PAS** inclure de `tei-article-cover` ni de div sommaire
  dans le `htmlBody`.
- Image de couverture : ajoutée dans `src/lib/article-images.ts` (clé = slug).

## Images & médias

- 🔴 **Images Hostinger UNIQUEMENT.** Wikimedia Commons bloque le hotlinking (403).
  Base : `https://green-gnat-134443.hostingersite.com/wp-content/uploads`
- 🔴 **Jamais de placeholder `VOTRE-URL.jpg` ni `[Insérer visuel]`** en production.
- Toute `<img>` porte `data-zoomable` (lightbox au clic) + légende en italique.
- Diagrammes physiques : **SVG inline**, fond sombre `#0d1117`, police mono, palette
  pilier. Ajouter `data-zoomable` aux SVG aussi quand pertinent.
- Vidéos : section **« Médias »** en BAS de l'article, juste avant Sources. YouTube en
  `<iframe>`. Présentation des intervenants à la première mention (brève bio).
- 🖼️ **Image de couverture / partage social (Open Graph, Google Discover)** :
  **1200×630 px minimum, format paysage (~1.91:1), JPEG < 1 Mo.** Jamais de carré
  1024×1024, jamais de logo/schéma comme visuel principal (Discover exige ≥1200 px de
  large sinon l'article perd la grande carte). Les vignettes Unsplash sont agrandies
  automatiquement en 1200×630 (`getArticleOgImage` dans `src/lib/article-images.ts`) ;
  les fichiers Hostinger sont servis tels quels → les uploader déjà en ≥1200 px de large.

## Charte rédactionnelle — tronc commun (toutes les pages)

1. **Lede** : ouvrir par un `<p class="tei-lede">` court et percutant (1-2 phrases,
   souvent chiffré). Pas d'image de couverture dans le HTML.
2. **Sections** : `<h2 id="slug-section"><span class="tei-section-num">01</span>Titre</h2>`.
   Numérotation occidentale zéro-paddée `01, 02, …`. **Jamais d'emoji** dans les titres.
   **Jamais de chiffres arabes orientaux** (۰۱) — toujours `01`.
3. **Encadré-clé** : voir système par page ci-dessous. Utiliser la **classe CSS**
   `tei-fait`, pas du style inline.
4. **Médias** (si vidéos) : `<h2 id="medias"><span class="tei-section-num">NN</span>Médias</h2>`
   puis les iframes, AVANT Sources.
5. **Sources** : OBLIGATOIRE. `<h2 id="sources"><span class="tei-section-num">NN</span>Sources</h2>`
   suivi d'un `<ol>`. Références datées et vérifiables.
6. Introduire chaque personnage à sa première mention (brève bio).
7. Aucune suppression de contenu existant lors d'un enrichissement.

## Identité par page (couleur du pilier + label propre)

Même structure partout ; l'encadré-clé prend la **couleur du pilier** et un **label**
adapté à l'identité de la page. Markup :

```html
<div class="tei-fait <CATEGORY>">
  <span class="tei-fait-label">LABEL</span>
  <p>Énoncé du fait clé.</p>
</div>
```

| Page | category | Couleur | `<CATEGORY>` | LABEL de l'encadré |
|---|---|---|---|---|
| Bibliothèque | `library` | Saffron `#D4943A` | `library` | `CE QUE LE TEXTE ÉTABLIT` |
| Centre de Recherche | `headquarters` | Lavande `#8B7EC8` | `headquarters` | `FAIT ÉTABLI N°X` |
| Observatoire | `observatory` | Cyan `#3B8FD4` | `observatory` | `CE QUE MONTRENT LES DONNÉES` |
| Expériences | `experiences` | Rose `#C45E6A` | `experiences` | `CE QUE L'EXPÉRIENCE ÉTABLIT` |

### Bibliothèque (`library`) — édition critique savante-religieuse
- Identité : démonstration scripturaire façon édition critique de texte.
- **Citations Coran/hadith — format unique** : `<blockquote class="tei-citation arabic-quote">`
  → `<p>` arabe → `<p>` traduction → `<footer>— Sourate Nom, S:V</footer>`.
- Notation sourate unifiée : `An-Naml — S27 V61` (nom translittéré — S<n° sourate> V<n° verset>).
- Sources hadith : `Al-Bukhārī 3199, Ṣaḥīḥ` (auteur, n°, grade).
- Translittération savante (ṣ, ḥ, ʿ), ﷺ après le Prophète.
- Texte pur acceptable (images non obligatoires).

### Centre de Recherche (`headquarters`) — dossier d'investigation épistémologique
- Identité : retourne la méthode scientifique contre le consensus (« on a interprété,
  pas prouvé »).
- Intro « Avant de commencer » recommandée (hors numérotation) + résumé.
- Structure : affirmation mainstream → mise en doute → réfutation → `Fait établi n°X`.
- Citations historiques sourcées (`<blockquote class="tei-citation">` + `<footer>`).
- Diagrammes SVG + portraits Hostinger.

### Observatoire (`observatory`) — empirique-zététique
- Identité : « regardez ce que vous observez vraiment », données officielles à l'appui.
- Tableaux de données/mesures (`<table>`), sources institutionnelles (NOAA, NASA, ESA, SHOM).
- Schémas SVG (optique, perspective, géométrie).
- Encadré-clé = `CE QUE MONTRENT LES DONNÉES`.

### Expériences (`experiences`) — démonstration reproductible chez soi
- Identité : « fais-le toi-même ».
- Protocole standard en `<h3>` : **Matériel** → **Protocole** (`<ol>`) → **Ce qui se passe**
  → **Ce que ça change**.
- Schémas SVG faits-maison fond sombre `#0d1117`, palette rose/cyan/or, `data-zoomable`.
- Encadré-clé = `CE QUE L'EXPÉRIENCE ÉTABLIT`.

## Variables CSS (src/styles/globals.css)

- Couleurs piliers : `--saffron #D4943A`, `--lavender #8B7EC8`, `--cyan #3B8FD4`,
  `--rose #C45E6A`, `--opal #3D9E7C`, `--gold #B8941F`.
- Texte/fond : `--ink`, `--ink-soft`, `--ink-muted`, `--bg`, `--cream`, `--card`, `--border`.
- Dark mode via `[data-theme="dark"]`. Toujours utiliser les variables, jamais de couleur
  en dur pour le texte/fond.
- Classes prêtes : `.tei-section-num`, `.tei-lede`, `.tei-fait(.library|.headquarters|.observatory|.experiences)`,
  `.tei-citation`, `.tei-quran`, `.tei-data`, `.tei-table`, `.tei-highlight`, `.tei-timeline`.

## Registres à tenir à jour quand on ajoute/supprime un article

- `src/lib/article-images.ts` — image de couverture (clé = slug).
- `src/lib/nexus-data.ts` — nœud + liens du graphe (si pertinent).
- L'article apparaît automatiquement sur sa page de catégorie.

## Vérification avant commit

```bash
npx next build   # doit passer
```
