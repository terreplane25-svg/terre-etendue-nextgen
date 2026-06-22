'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { dash } from '@/lib/design-tokens';
import SectionHeader from '@/components/SectionHeader';
import ArticleCarousel from '@/components/ArticleCarousel';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

const SECTIONS = [
  { id: 'optique', label: 'Optique & horizon', icon: '🔭', slugs: [
    'la-perspective-pourquoi-les-objets-disparaissent',
    'loeil-humain-la-machine-a-voir-qui-faconne-notre-realite',
    'pression-lumiere-halos-rayons-et-ondes',
  ]},
  { id: 'hydrologie', label: 'Hydrologie', icon: '🌊', slugs: [
    'leau-ne-ment-pas',
    'cartes-routes-boussoles-et-le-mystere-antarctique',
    'les-marees-contre-lheliocentrisme',
    'le-pole-sud-nexiste-pas',
    'lespace-une-frontiere-infranchissable',
    'densite-pourquoi-les-choses-montent-et-descendent',
  ]},
  { id: 'astronomie', label: 'Astronomie', icon: '🌙', slugs: [
    'la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre',
    'la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas',
    'la-lune-fonction-et-anomalies',
    'le-theodolite-celeste',
    'la-rotation-terrestre-deux-experiences-zero-preuve',
  ]},
];

function getSection(slug: string) {
  for (const s of SECTIONS) { if (s.slugs.includes(slug)) return s.id; }
  return null;
}

const EXP_LINKS: Record<string, { slug: string; label: string }> = {
  "densite-pourquoi-les-choses-montent-et-descendent": { slug: "densite-pourquoi-les-choses-montent-et-descendent", label: "Fiche expérience : densité" },
  "pression-lumiere-halos-rayons-et-ondes": { slug: "la-pression-atmospherique-un-ocean-d-air-invisible", label: "Fiche expérience : pression" },
  "lhorizon-la-perspective-et-la-refraction": { slug: "la-perspective-lineaire", label: "Fiche expérience : perspective" },
  "la-perspective-pourquoi-les-objets-disparaissent": { slug: "la-perspective-lineaire", label: "Fiche expérience : perspective" },
  "cartes-routes-boussoles-et-le-mystere-antarctique": { slug: "magnetisme-et-electromagnetisme", label: "Fiche expérience : magnétisme" },
};

export default function ObservatoryClient({ articles }: { articles: A[] }) {
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

  const articleFooter = (a: A) => {
    const exp = EXP_LINKS[a.slug];
    if (!exp) return null;
    return (
      <Link href={`/article/${exp.slug}`} style={{ fontSize: 11, color: dash.opal, fontWeight: 600 }}>
        🧪 {exp.label}
      </Link>
    );
  };

  return (
    <div>
      <SectionHeader pillar="OBS" pillarNum="02" subtitle="Données empiriques" title="L'Observatoire" color={dash.cyan} count={articles.length} countLabel="analyses — observations, optique, hydrologie et astronomie" />
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '0 24px 64px' }}>
        <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
          <Link href="/experiences" style={{ fontSize: 13, fontWeight: 600, color: dash.opal, padding: '6px 14px', borderRadius: 6, background: `${dash.opal}10` }}>
            Voir les fiches expériences →
          </Link>
        </div>

        {/* Section filters */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 24 }}>
          <button onClick={() => setFilter('all')} style={{
            padding: '6px 14px', borderRadius: 6, fontSize: 13, fontWeight: 600,
            border: `1px solid ${filter === 'all' ? dash.cyan : 'var(--border)'}`,
            background: filter === 'all' ? dash.cyan : 'var(--card)',
            color: filter === 'all' ? '#fff' : 'var(--ink-muted)',
            cursor: 'pointer', fontFamily: dash.fontMain,
          }}>Tout ({articles.length})</button>
          {SECTIONS.map(s => {
            const count = articles.filter(a => getSection(a.slug) === s.id).length;
            if (count === 0) return null;
            return (
              <button key={s.id} onClick={() => setFilter(filter === s.id ? 'all' : s.id)} style={{
                padding: '6px 14px', borderRadius: 6, fontSize: 13, fontWeight: 600,
                border: `1px solid ${filter === s.id ? dash.cyan : 'var(--border)'}`,
                background: filter === s.id ? dash.cyan : 'var(--card)',
                color: filter === s.id ? '#fff' : 'var(--ink-muted)',
                cursor: 'pointer', fontFamily: dash.fontMain,
              }}>{s.icon} {s.label} ({count})</button>
            );
          })}
        </div>

        {/* Articles carousel */}
        <ArticleCarousel
          articles={filtered as any}
          color={dash.cyan}
          badgeLabel={badgeLabel as any}
          badgeColor={dash.cyan}
          footer={articleFooter as any}
          showDate={false}
        />
      </div>
    </div>
  );
}
