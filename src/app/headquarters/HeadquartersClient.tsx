'use client';
import React, { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { dash } from '@/lib/design-tokens';
import SectionHeader from '@/components/SectionHeader';
import PageIntro from '@/components/PageIntro';
import ArticleCarousel from '@/components/ArticleCarousel';

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

function getSection(slug: string) {
  for (const s of SECTIONS) { if (s.slugs.includes(slug)) return s.id; }
  return null;
}

export default function HeadquartersClient({ articles }: { articles: A[] }) {
  const searchParams = useSearchParams();
  const initialFilter = searchParams.get('filter') || 'all';
  const [filter, setFilter] = useState(initialFilter);

  const filtered = filter === 'all'
    ? articles
    : articles.filter(a => getSection(a.slug) === filter);

  const badgeLabel = (a: A) => {
    if (filter !== 'all') return null;
    const section = SECTIONS.find(s => s.id === getSection(a.slug));
    return section ? `${section.icon} ${section.label}` : null;
  };

  return (
    <div>
      <SectionHeader pillar="Q.G." pillarNum="01" subtitle="Épistémologie & méthode" title="Le Centre de Recherche" color={dash.lavender} count={articles.length} countLabel="publications — épistémologie, zététique et remise en question" />
      <PageIntro color={dash.lavender}
        lede="On a interprété. On n'a pas prouvé."
        body="Le Centre de Recherche retourne la méthode scientifique contre le consensus : chaque « preuve » de la rotation, de la gravité ou du globe est reprise pas à pas — affirmation, mise en doute, réfutation. On ne demande pas d'y croire, mais d'examiner ce qui est réellement démontré." />
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '0 24px 64px' }}>

        {/* Section filters */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 24 }}>
          <button onClick={() => setFilter('all')} style={{
            padding: '6px 14px', borderRadius: 6, fontSize: 13, fontWeight: 600,
            border: `1px solid ${filter === 'all' ? dash.lavender : 'var(--border)'}`,
            background: filter === 'all' ? dash.lavender : 'var(--card)',
            color: filter === 'all' ? '#fff' : 'var(--ink-muted)',
            cursor: 'pointer', fontFamily: dash.fontMain,
          }}>Tout ({articles.length})</button>
          {SECTIONS.map(s => {
            const count = articles.filter(a => getSection(a.slug) === s.id).length;
            if (count === 0) return null;
            return (
              <button key={s.id} onClick={() => setFilter(filter === s.id ? 'all' : s.id)} style={{
                padding: '6px 14px', borderRadius: 6, fontSize: 13, fontWeight: 600,
                border: `1px solid ${filter === s.id ? dash.lavender : 'var(--border)'}`,
                background: filter === s.id ? dash.lavender : 'var(--card)',
                color: filter === s.id ? '#fff' : 'var(--ink-muted)',
                cursor: 'pointer', fontFamily: dash.fontMain,
              }}>{s.icon} {s.label} ({count})</button>
            );
          })}
        </div>

        {/* Articles carousel */}
        <ArticleCarousel
          articles={filtered as any}
          color={dash.lavender}
          badgeLabel={badgeLabel as any}
          badgeColor={dash.lavender}
          showDate={false}
        />
      </div>
    </div>
  );
}
