# 🏛️ TEI Editorial Redesign — Guide d'intégration

## Vue d'ensemble

Ce pack contient le redesign complet « Revue de Cosmologie d'Avant-Garde » 
pour terre-etendue-nextgen. Il remplace le thème HUD/sci-fi par un style 
éditorial premium inspiré des grandes publications académiques.

---

## Fichiers inclus

```
tei-editorial/
├── README.md                          ← Ce fichier
├── tailwind.config.ts                 ← Config Tailwind avec fonts/couleurs
├── lib/
│   └── editorial-tokens.ts            ← Design tokens JS (pour inline styles)
├── app/
│   ├── globals.css                    ← Thème complet + prose-tei éditorial
│   ├── layout.tsx                     ← Layout racine avec Nav + Footer
│   ├── page.tsx                       ← Homepage (Server Component)
│   ├── HomeClient.tsx                 ← Homepage animations (Client Component)
│   └── headquarters/
│       └── page.tsx                   ← Exemple de page pilier
└── components/editorial/
    ├── Navigation.tsx                 ← Nav sticky avec blur au scroll
    ├── Footer.tsx                     ← Footer avec compteur dynamique
    ├── ScrollReveal.tsx               ← Wrapper d'animation au scroll
    ├── ArticleReader.tsx              ← Lecteur d'article avec TOC latéral
    └── EditorialArticleList.tsx       ← Index des articles par pilier
```

---

## Étapes d'intégration

### 1. Backup
```bash
cp app/globals.css app/globals.css.bak
cp app/layout.tsx app/layout.tsx.bak
cp app/page.tsx app/page.tsx.bak
cp tailwind.config.ts tailwind.config.ts.bak
```

### 2. Copier les fichiers
```bash
# Depuis la racine du repo
cp tei-editorial/lib/editorial-tokens.ts lib/
cp tei-editorial/app/globals.css app/
cp tei-editorial/app/layout.tsx app/
cp tei-editorial/app/page.tsx app/
cp tei-editorial/app/HomeClient.tsx app/
cp tei-editorial/tailwind.config.ts .

# Créer le dossier si nécessaire
mkdir -p components/editorial
cp tei-editorial/components/editorial/* components/editorial/
```

### 3. Adapter les imports

Les fichiers supposent que `lib/articles.ts` exporte :
- `getAllArticles()` → tous les articles
- `getArticlesByPillar(slug)` → articles d'un pilier

Et que chaque article a au minimum :
```ts
interface Article {
  slug: string;
  title: string;
  content: string;      // HTML natif
  pillar: string;        // "headquarters" | "observatory" | "library"
  description?: string;
  type?: string;
  tags?: string[];
  citations?: number;
  pinned?: boolean;
  order?: number;
}
```

**Adapte les noms de propriétés** si ton interface est différente.

### 4. Remplacer le composant article

Dans tes pages `[slug]/page.tsx`, remplace l'ancien ArticleReader :
```tsx
// AVANT
import ArticleReader from "@/components/ArticleReader";

// APRÈS
import ArticleReader from "@/components/editorial/ArticleReader";
```

Et passe les props :
```tsx
<ArticleReader
  title={article.title}
  subtitle={article.description}
  content={article.content}
  pillar={article.pillar}
  pillarIndex={article.order}
  articleType={article.type}
  tags={article.tags}
  citations={article.citations}
  charCount={article.content.length}
  pinned={article.pinned}
  prevArticle={prev}
  nextArticle={next}
/>
```

### 5. Dupliquer la page pilier

Copie `app/headquarters/page.tsx` pour les autres piliers :
```bash
cp app/headquarters/page.tsx app/observatory/page.tsx
cp app/headquarters/page.tsx app/library/page.tsx
```
Puis adapte le `pillar`, le `title`, le `subtitle` et la `description` dans chaque copie.

### 6. SearchCommand

Le `Navigation.tsx` éditorial a un bouton de recherche prêt à être branché.
Décommente l'import de ton `SearchCommand` existant et branche-le :
```tsx
import SearchCommand from "@/components/SearchCommand";
// ... dans le JSX :
<SearchCommand open={searchOpen} setOpen={setSearchOpen} />
```

### 7. Lab et Nexus

Ces pages gardent leur propre logique (Three.js, graphe).
Elles héritent automatiquement de la Nav + Footer éditoriaux via le `layout.tsx`.
Aucun changement nécessaire dans leurs composants internes.

---

## Citations dans le HTML des articles

Le `prose-tei` CSS reconnaît automatiquement ces classes dans le HTML natif :

### Citation coranique
```html
<div class="tei-quran">
  <small>Coran · Sourate An-Naba' (78:6)</small>
  <div lang="ar">أَلَمْ نَجْعَلِ الْأَرْضَ مِهَادًا</div>
  <p class="quran-translation">« N'avons-Nous pas fait de la terre une couche ? »</p>
</div>
```
→ Bordure bronze + fond doré + Amiri 32px + hexagone décoratif

### Données expérimentales
```html
<div class="tei-data">
  <small>Données expérimentales — Bedford Level, 1838</small>
  <p>Distance : 6 milles. Courbure théorique : 7,2 m. Résultat : 0.</p>
</div>
```
→ Bordure verte + fond teinté vert

### Référence bibliographique
```html
<div class="tei-ref">
  <small>Référence bibliographique</small>
  <p>Blount, Lady E. A. <em>Earth Not a Globe Review</em>, vol. XIV, 1904.</p>
</div>
```
→ Bordure terre cuite + fond rosé

### Pull quote (blockquote standard)
```html
<blockquote>
  <p>Trois expériences, un même résultat.</p>
</blockquote>
```
→ Barre noire latérale + Cormorant italic 22px

---

## Typographie (triple stack)

| Usage | Font | Taille | Poids |
|-------|------|--------|-------|
| Titres, hero, h1-h3 | Cormorant Garamond | 22-68px | 300-500 |
| Corps des articles | Crimson Pro | 18px | 300 |
| Labels, overlines, ALL-CAPS | Cinzel | 9-11px | 500-600 |
| Navigation, UI | DM Sans | 12-14px | 400-600 |
| Données, compteurs, tags | JetBrains Mono | 10-13px | 400-500 |
| Texte arabe | Amiri | 24-32px | 400-700 |

---

## Palette

| Token | Hex | Usage |
|-------|-----|-------|
| --bg | #FAFAF8 | Fond principal |
| --bg-warm | #F5F2ED | Sections alternées, footer |
| --ink | #0C0A09 | Titres, texte principal |
| --ink-soft | #2C2825 | Corps d'article |
| --ink-muted | #6B6560 | Descriptions |
| --ink-ghost | #A09890 | Labels tertiaires |
| --bronze | #8B6914 | Accent sacré, CTA, citations |
| --green | #1B6B45 | Données scientifiques |
| --coral | #8B3A2A | Références bibliographiques |
| --indigo | #3B3F8C | Lab, simulations |

---

## Ce qui ne change PAS

- `content/articles/*.json` → Aucune modification du contenu
- `lib/articles.ts` → Garde tes fonctions utilitaires
- Lab (Three.js) → Les simulations gardent leur fond sombre
- Nexus → Le graphe garde sa propre esthétique
- SearchCommand → Réutilisé tel quel
- SEO (sitemap, robots, JSON-LD) → Inchangé
