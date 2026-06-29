'use client';
import React from 'react';
import { dash } from '@/lib/design-tokens';
import SectionHeader from '@/components/SectionHeader';
import PageIntro from '@/components/PageIntro';
import CategoryFlow from '@/components/CategoryFlow';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

const SECTIONS = [
  { id: 'epistemologie', label: 'Épistémologie', icon: '🧠', slugs: [
    'pourquoi-tout-remettre-en-question',
    'la-cosmologie-comme-instrument-de-domination',
    'le-concordisme',
    'les-distances-cosmiques-au-dela-de-la-regle',
    'les-trous-noirs-nexistent-pas',
    'ligo-londe-qui-nexistait-pas',
  ]},
  { id: 'zetetique', label: 'Méthode zététique', icon: '🔬', slugs: [
    'le-mouvement-zetetique-150-ans-de-resistance-1849-2000',
    '200-ans-de-resultats-nuls-darago-a-einstein',
    'le-mythe-deratosthene',
    'kings-dethroned-leffondrement-de-la-triangulation-stellaire',
    'chronologie-de-la-tromperie-du-globe',
  ]},
  { id: 'question', label: 'Remise en question', icon: '❓', slugs: [
    'la-gravite-70-theories-et-aucune-preuve',
    'la-gravite-70-theories-et-aucune-certitude',
    'la-rotation-terrestre-deux-experiences-zero-preuve',
    'lhypothese-nulle-dynamique-et-cinematique',
    'neptune-et-pluton-les-faux-triomphes',
    'dune-terre-plate-universelle-a-la-sphere-grecque',
  ]},
];

export default function HeadquartersClient({ articles }: { articles: A[] }) {
  return (
    <div>
      <SectionHeader pillar="Q.G." pillarNum="01" subtitle="Épistémologie & méthode" title="Le Centre de Recherche" color={dash.lavender} count={articles.length} countLabel="publications — épistémologie, zététique et remise en question" />
      <PageIntro color={dash.lavender}
        lede="On a interprété. On n'a pas prouvé."
        body="Le Centre de Recherche retourne la méthode scientifique contre le consensus : chaque « preuve » de la rotation, de la gravité ou du globe est reprise pas à pas — affirmation, mise en doute, réfutation. On ne demande pas d'y croire, mais d'examiner ce qui est réellement démontré." />
      <CategoryFlow sections={SECTIONS} articles={articles} color={dash.lavender} basePath="/headquarters" />
    </div>
  );
}
