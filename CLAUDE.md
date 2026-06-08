# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev      # Start development server (localhost:3000)
npm run build    # Production build
npm run lint     # ESLint (Next.js default config)
```

No test framework is configured. There are no `.test.ts` / `.test.tsx` files.

## Architecture Overview

**Terre Étendue Islam** is a Next.js 15 academic publishing platform focused on Islamic cosmology and epistemology. It is entirely file-system–driven — no database, no CMS, no authentication.

### Content Pipeline

All articles live as JSON files in `/content/articles/` (60+ files). The `src/lib/articles.ts` module reads these from disk and provides:
- `getAllArticles()` — all articles, sorted/filtered
- `getArticle(slug)` — single article by slug
- `getArticlesByCategory(category)` — pillar-scoped listing
- `searchArticles(query)` — full-text search (used by `/api/search`)

Articles were migrated from WordPress/Elementor, so `articles.ts` also sanitizes CSS artifacts embedded in HTML strings. Each article's `htmlBody` field is raw HTML that gets rendered via `dangerouslySetInnerHTML` with the `.prose-dash` or `.prose-tei` CSS class applied.

**Article JSON shape:**
```json
{
  "title": "", "description": "", "date": "", "author": "",
  "category": "headquarters|observatory|library|lab|experiences|meta",
  "tags": [], "pinned": false, "htmlBody": "<HTML from Elementor>"
}
```

### Page Structure (App Router)

- `src/app/layout.tsx` — Root layout wrapping all pages with `<DashboardNav>` and `<DashboardFooter>`
- `src/app/page.tsx` — SSR homepage; fetches articles server-side, passes to `<HomeClient>` (client component)
- `src/app/article/[slug]/page.tsx` — SSG via `generateStaticParams()`, full SEO (OpenGraph, JSON-LD schema)
- `src/app/[pillar]/page.tsx` — One page per pillar (headquarters, observatory, library, lab, experiences), each filters articles by category
- `src/app/nexus/page.tsx` — Force-directed graph of semantic article relationships
- `src/app/api/search/route.ts` — GET `?q=query&categories=...`, returns top 10 Fuse.js results

### Two Parallel Theme Systems

The repo is mid-migration from a **dashboard/HUD** aesthetic to a **premium editorial** aesthetic. Both are functional:

| Theme | Config | Components | Tokens |
|---|---|---|---|
| Dashboard (current default) | `tailwind.config.ts` | `src/components/*.tsx` | `src/lib/design-tokens.ts` |
| Editorial (new) | `tailwind.config.ts` (merged) | `src/components/editorial/` | `src/lib/editorial-tokens.ts` |

The editorial theme uses `prose-tei` CSS and Cormorant/Crimson/Cinzel/DM Sans fonts. The dashboard theme uses Plus Jakarta Sans with `prose-dash`. `src/styles/globals.css` contains both sets of prose overrides.

**Do not consolidate the two Tailwind configs without explicit instruction** — the migration is intentional and ongoing.

### Component Directories

- `src/components/` — Top-level shared components (Nav, Footer, ArticleReader, SearchCommand, NexusGraph, GlossaryTooltip)
- `src/components/editorial/` — Premium editorial variants of nav, footer, article reader
- `src/components/lab/` — Three.js interactive simulations (FlatEarthSim, GeoHelioSim, ProjectionSim, CurvatureCalc)
- `src/components/ui/` — Generic UI primitives (BezelCard, ScrollReveal, Pill, Grain)

### Key Conventions

**Server vs Client split:** Pages handle data fetching as Server Components; interactive parts (`SearchCommand`, `NexusGraph`, all simulations, scroll animations) are marked `'use client'`. When adding a new feature, keep data fetching in the page file and extract the interactive shell to a `*Client.tsx` sibling.

**Path alias:** `@/*` maps to `src/*` (see `tsconfig.json`).

**Images:** `next.config.js` sets `images: { unoptimized: true }` for static-export compatibility. Use `<img>` or `<Image unoptimized>` — do not rely on Next.js image optimization.

**Fonts:** Configured in `src/lib/fonts.ts` via `next/font/google`. Editorial stack: Cormorant Garamond (titles), Crimson Pro (body), Cinzel (labels), DM Sans (UI), JetBrains Mono (data), Amiri (Arabic). Dashboard stack: Orbitron, Share Tech Mono, Rajdhani, Source Serif 4.

**Semantic graph data:** `src/lib/nexus-data.ts` (24 KB) contains the hand-authored node/edge graph powering the Nexus page. Editing it requires understanding the graph's node IDs and edge weights.

### Article HTML Classes

When authoring or editing article HTML bodies, these CSS classes receive special styling in `globals.css`:

```html
<div class="tei-quran">   <!-- Bronze border, gold bg, Amiri font, 32px -->
<div class="tei-data">    <!-- Green border, scientific data blocks -->
<div class="tei-ref">     <!-- Coral border, bibliographic references -->
<blockquote>              <!-- Black left bar, Cormorant italic 22px -->
```

### Design Tokens

`src/lib/design-tokens.ts` exports `dash.*` color tokens and the `PILLARS` array (used for nav, cards, and routing). `TAG_COLORS` maps tag strings to Tailwind color classes. Reference these rather than hardcoding colors when working on pillar-scoped UI.
