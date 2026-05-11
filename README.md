# Terre Etendue Islam - Plateforme de Recherche Next-Gen

> Plateforme de recherche academique et scientifique explorant la convergence entre geometrie, physique et sources islamiques.

## Les 4 Piliers

| Pilier | Route | Description |
|--------|-------|-------------|
| **Le Q.G.** | `/headquarters` | Epistemologie - Fondements methodologiques |
| **L Observatoire** | `/observatory` | Empirique - Donnees scientifiques et observations |
| **La Bibliotheque** | `/library` | Sources Sacrees - Coran, hadiths, Kalam |
| **Le Lab** | `/lab` | Modelisation - Simulations 3D interactives |
| **Le Nexus** | `/nexus` | Graphe de connaissances |

## Stack Technique

- **Framework** : Next.js 15 (App Router, Server Components)
- **Langage** : TypeScript 5
- **Style** : Tailwind CSS 3.4 + plugin Typography
- **Animations** : Framer Motion 11
- **3D** : Three.js (via React Three Fiber + Drei)
- **Contenu** : Markdown avec gray-matter + remark
- **Etat global** : Zustand (switch Etude/Lab)
- **Deploiement** : Vercel (recommande)

## Structure du Projet

```
terre-etendue-nextgen/
|-- public/                     # Assets statiques
|-- content/
|   +-- articles/               # Articles Markdown avec frontmatter YAML
|-- src/
|   |-- app/                    # Routes Next.js (App Router)
|   |   |-- layout.tsx          # Layout racine (Navigation + Footer)
|   |   |-- page.tsx            # Page d accueil "Command Center"
|   |   |-- article/[slug]/     # Lecture article dynamique
|   |   |-- headquarters/       # Pilier Epistemologie
|   |   |-- observatory/        # Pilier Empirique
|   |   |-- library/            # Pilier Sources Sacrees
|   |   |-- lab/                # Pilier Modelisation (3D)
|   |   +-- nexus/              # Graphe de connaissances
|   |-- components/
|   |   |-- Navigation.tsx      # Navbar sticky + burger mobile
|   |   |-- Footer.tsx          # Pied de page 4 colonnes
|   |   |-- PillarCard.tsx      # Carte animee pour chaque pilier
|   |   |-- ArticleReader.tsx   # Lecteur (TOC, glossaire, modes)
|   |   |-- ViewModeSwitch.tsx  # Toggle Etude / Lab (Zustand)
|   |   |-- GlossaryTooltip.tsx # Pop-ups de definitions au survol
|   |   |-- NexusGraph.tsx      # Graphe force-directed (Canvas)
|   |   +-- TawhidSimulation.tsx # Simulation 3D orbitale (R3F)
|   |-- lib/
|   |   +-- articles.ts         # Utilitaires Markdown cote serveur
|   +-- styles/
|       +-- globals.css         # Variables CSS, styles de base
|-- package.json
|-- tsconfig.json
|-- tailwind.config.js
|-- postcss.config.js
|-- next.config.js
|-- MIGRATION_GUIDE.md
+-- README.md
```

## Installation

```bash
# 1. Cloner le depot
git clone https://github.com/votre-username/terre-etendue-nextgen.git
cd terre-etendue-nextgen

# 2. Installer les dependances
npm install

# 3. Lancer le serveur de developpement
npm run dev

# 4. Ouvrir http://localhost:3000
```

## Ajouter un Article

Creez un fichier `.md` dans `content/articles/` :

```yaml
---
title: "Titre de l article"
description: "Resume court"
date: "2026-01-15"
author: "Votre nom"
category: "library"        # headquarters | observatory | library | lab
tags: ["tag1", "tag2"]
connections: ["slug-autre-article"]
---

Votre contenu en Markdown ici...
```

## Design System

### Palette (Mode Sombre)

| Token | Hex | Usage |
|-------|-----|-------|
| `obs-dark` | `#0A0F14` | Fond principal |
| `obs-surface` | `#161D26` | Cartes et surfaces |
| `obs-cyan` | `#00D1FF` | Accent Science/Lab |
| `obs-gold` | `#D4AF37` | Accent Bibliotheque/Sacre |

### Typographie

- **Titres** : Inter (geometrique, moderne)
- **Sous-titres** : Montserrat (institution/premium)
- **Corps** : Source Serif 4 (confort de lecture longue)

## Scripts

```bash
npm run dev      # Serveur de developpement (port 3000)
npm run build    # Build de production
npm run start    # Serveur de production
npm run lint     # Linting ESLint
```

## Deploiement sur Vercel

1. Push le code sur GitHub
2. Aller sur vercel.com et importer le repo
3. Vercel detecte automatiquement Next.js
4. Chaque push sur `main` declenche un deploiement automatique

## Licence

MIT
