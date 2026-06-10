'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { dash } from '@/lib/design-tokens';
import { getArticleImage } from '@/lib/article-images';
import PageHero from '@/components/PageHero';

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

  return (
    <div>
      <PageHero title="Le Centre de Recherche" subtitle={`${articles.length} publications · Épistémologie et méthode`} color={dash.lavender} image="https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/04/livres_ia.jpg" />
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '0 24px 64px' }}>

        {/* Section filters */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 24 }}>
          <button onClick={() => setFilter('all')} style={{
            padding: '6px 14px', borderRadius: 6, fontSize: 13, fontWeight: 600,
            border: `1px solid ${filter === 'all' ? dash.lavender : dash.border}`,
            background: filter === 'all' ? dash.lavender : dash.card,
            color: filter === 'all' ? '#fff' : dash.inkMuted,
            cursor: 'pointer', fontFamily: dash.fontMain,
          }}>Tout ({articles.length})</button>
          {SECTIONS.map(s => {
            const count = articles.filter(a => getSection(a.slug) === s.id).length;
            if (count === 0) return null;
            return (
              <button key={s.id} onClick={() => setFilter(filter === s.id ? 'all' : s.id)} style={{
                padding: '6px 14px', borderRadius: 6, fontSize: 13, fontWeight: 600,
                border: `1px solid ${filter === s.id ? dash.lavender : dash.border}`,
                background: filter === s.id ? dash.lavender : dash.card,
                color: filter === s.id ? '#fff' : dash.inkMuted,
                cursor: 'pointer', fontFamily: dash.fontMain,
              }}>{s.icon} {s.label} ({count})</button>
            );
          })}
        </div>

        {/* Articles list */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {filtered.map((a, i) => {
            const section = SECTIONS.find(s => s.id === getSection(a.slug));
            return (
              <motion.div key={a.slug} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}>
                <Link href={`/article/${a.slug}`} className="dash-card" style={{ display: 'flex', overflow: 'hidden', cursor: 'pointer' }}>
                  <div style={{ width: 180, minHeight: 140, flexShrink: 0, overflow: 'hidden' }}>
                    <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
                  </div>
                  <div style={{ padding: '18px 24px', flex: 1, minWidth: 0 }}>
                    {section && filter === 'all' && (
                      <div style={{ fontSize: 11, fontWeight: 700, color: dash.lavender, marginBottom: 4, letterSpacing: '0.04em' }}>
                        {section.icon} {section.label}
                      </div>
                    )}
                    <div style={{ fontSize: 17, fontWeight: 700, color: dash.ink, marginBottom: 6, lineHeight: 1.35 }}>
                      {a.pinned && <span style={{ color: dash.saffron, marginRight: 6 }}>★</span>}{a.title}
                    </div>
                    <div style={{ fontSize: 12, color: dash.inkGhost, marginBottom: 8, fontFamily: dash.fontMono }}>Terre Etendue · {a.readTime} min</div>
                    {a.description && (
                      <div style={{ fontSize: 14, color: dash.inkMuted, lineHeight: 1.55, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as never }}>{a.description}</div>
                    )}
                  </div>
                </Link>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
