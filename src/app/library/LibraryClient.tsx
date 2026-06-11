'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { dash } from '@/lib/design-tokens';
import { getArticleImage } from '@/lib/article-images';
import SectionHeader from '@/components/SectionHeader';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

const SECTIONS = [
  { id: 'coran', label: 'Coran & Sunna', icon: '📖', slugs: [
    'debut-de-la-creation-selon-le-coran-et-la-sunna',
    'debut-de-la-creation-le-soleil-mobile-la-terre-immobile',
    'la-terre-dans-le-coran',
    'dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne',
    'la-qibla-et-la-direction-cote-ouest',
  ]},
  { id: 'historique', label: 'Textes historiques', icon: '🕌', slugs: [
    'le-consensus-sur-la-sphericite',
    'pres-de-cent-savants-de-lislam',
    'sources-historiques-le-fonds-documentaire-1865-1920',
  ]},
  { id: 'cosmographie', label: 'Cosmographie', icon: '🌍', slugs: [
    'levolution-et-lislam',
    'mise-en-garde-la-kaaba-et-saturne',
  ]},
];

function getSection(slug: string) {
  for (const s of SECTIONS) { if (s.slugs.includes(slug)) return s.id; }
  return null;
}

export default function LibraryClient({ priority, articles }: { priority: A[]; articles: A[] }) {
  const searchParams = useSearchParams();
  const initialFilter = searchParams.get('filter') || 'all';
  const [filter, setFilter] = useState(initialFilter);

  const allArticles = [...priority, ...articles];
  const filtered = filter === 'all'
    ? allArticles
    : allArticles.filter(a => getSection(a.slug) === filter);

  const showPrioritySection = filter === 'all' || filter === 'coran';
  const priorityInFilter = filtered.filter(a => priority.some(p => p.slug === a.slug));
  const othersInFilter = filtered.filter(a => !priority.some(p => p.slug === a.slug));

  return (
    <div>
      <SectionHeader pillar="BIBLIO" pillarNum="03" subtitle="Sources sacrées" title="La Bibliothèque" color={dash.saffron} count={allArticles.length} countLabel="publications — Coran, Sunna, textes historiques et cosmographie" />
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '0 24px 64px' }}>

        {/* Section filters */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 24 }}>
          <button onClick={() => setFilter('all')} style={{
            padding: '6px 14px', borderRadius: 6, fontSize: 13, fontWeight: 600,
            border: `1px solid ${filter === 'all' ? dash.saffron : dash.border}`,
            background: filter === 'all' ? dash.saffron : dash.card,
            color: filter === 'all' ? '#fff' : dash.inkMuted,
            cursor: 'pointer', fontFamily: dash.fontMain,
          }}>Tout ({allArticles.length})</button>
          {SECTIONS.map(s => {
            const count = allArticles.filter(a => getSection(a.slug) === s.id).length;
            if (count === 0) return null;
            return (
              <button key={s.id} onClick={() => setFilter(filter === s.id ? 'all' : s.id)} style={{
                padding: '6px 14px', borderRadius: 6, fontSize: 13, fontWeight: 600,
                border: `1px solid ${filter === s.id ? dash.saffron : dash.border}`,
                background: filter === s.id ? dash.saffron : dash.card,
                color: filter === s.id ? '#fff' : dash.inkMuted,
                cursor: 'pointer', fontFamily: dash.fontMain,
              }}>{s.icon} {s.label} ({count})</button>
            );
          })}
        </div>

        {/* Priority articles */}
        {showPrioritySection && priorityInFilter.length > 0 && (
          <div style={{ marginBottom: 40 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 18 }}>
              <span style={{ fontSize: 18 }}>📖</span>
              <h2 style={{ fontSize: 18, fontWeight: 750, color: dash.ink }}>Lecture prioritaire</h2>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
              {priorityInFilter.map((a, i) => (
                <motion.div key={a.slug} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 + i * 0.08 }}>
                  <Link href={`/article/${a.slug}`} className="dash-card" style={{ display: 'block', overflow: 'hidden', cursor: 'pointer' }}>
                    <div style={{ height: 200, overflow: 'hidden', position: 'relative' }}>
                      <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
                      <span className="badge" style={{ position: 'absolute', top: 14, left: 14, background: 'rgba(255,255,255,0.93)', color: dash.gold, border: `1px solid ${dash.gold}30`, backdropFilter: 'blur(8px)', fontSize: 11 }}>★ PRIORITAIRE</span>
                    </div>
                    <div style={{ padding: '22px 24px' }}>
                      <div style={{ fontSize: 18, fontWeight: 750, color: dash.ink, lineHeight: 1.35, marginBottom: 8 }}>{a.title}</div>
                      {a.description && <div style={{ fontSize: 14, color: dash.inkMuted, lineHeight: 1.55, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical' as never, overflow: 'hidden' }}>{a.description}</div>}
                      <div style={{ fontSize: 12, color: dash.inkGhost, marginTop: 12, fontFamily: dash.fontMono }}>{a.readTime} min de lecture</div>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Other articles */}
        {othersInFilter.length > 0 && (
          <>
            {(showPrioritySection && priorityInFilter.length > 0) && (
              <h2 style={{ fontSize: 18, fontWeight: 750, color: dash.ink, marginBottom: 16 }}>
                {filter === 'all' ? 'Toutes les publications' : SECTIONS.find(s => s.id === filter)?.label || 'Publications'}
              </h2>
            )}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {othersInFilter.map((a, i) => {
                const section = SECTIONS.find(s => s.id === getSection(a.slug));
                return (
                  <motion.div key={a.slug} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 + i * 0.03 }}>
                    <Link href={`/article/${a.slug}`} className="dash-card article-card-row" style={{ display: 'flex', overflow: 'hidden', cursor: 'pointer' }}>
                      <div className="article-card-thumb" style={{ width: 180, minHeight: 140, flexShrink: 0, overflow: 'hidden' }}>
                        <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
                      </div>
                      <div style={{ padding: '18px 24px', flex: 1, minWidth: 0 }}>
                        {section && filter === 'all' && (
                          <div style={{ fontSize: 11, fontWeight: 700, color: dash.saffron, marginBottom: 4, letterSpacing: '0.04em' }}>
                            {section.icon} {section.label}
                          </div>
                        )}
                        <div style={{ fontSize: 17, fontWeight: 700, color: dash.ink, marginBottom: 6, lineHeight: 1.35 }}>{a.title}</div>
                        <div style={{ fontSize: 12, color: dash.inkGhost, marginBottom: 8, fontFamily: dash.fontMono }}>Terre Etendue · {a.readTime} min</div>
                        {a.description && <div style={{ fontSize: 14, color: dash.inkMuted, lineHeight: 1.55, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as never }}>{a.description}</div>}
                      </div>
                    </Link>
                  </motion.div>
                );
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
