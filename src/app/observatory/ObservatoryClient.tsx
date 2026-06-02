'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { dash, TAG_COLORS } from '@/lib/design-tokens';

interface ArticleEntry {
  slug: string; title: string; description: string;
  tags: string[]; pinned: boolean; readTime: number;
}

// Sparkline
function Spark({ data, color, w = 200, h = 60 }: { data: number[]; color: string; w?: number; h?: number }) {
  const max = Math.max(...data), min = Math.min(...data), r = max - min || 1;
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - 4 - ((v - min) / r) * (h - 8)}`).join(' ');
  const fill = pts + ` ${w},${h} 0,${h}`;
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ display: 'block', width: '100%' }}>
      <defs>
        <linearGradient id={`g-${color.replace('#','')}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.15" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon points={fill} fill={`url(#g-${color.replace('#','')})`} />
      <polyline points={pts} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

export default function ObservatoryClient({ articles }: { articles: ArticleEntry[] }) {
  const [filter, setFilter] = useState('all');

  const allTags = Array.from(new Set(articles.flatMap(a => a.tags))).filter(t => t !== 'l-observatoire');
  const filtered = filter === 'all' ? articles
    : filter === 'pinned' ? articles.filter(a => a.pinned)
    : articles.filter(a => a.tags.includes(filter));

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '32px 24px 64px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 28, alignItems: 'start' }}>

        {/* Main column */}
        <div>
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 28 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: dash.cyan, letterSpacing: '0.1em', textTransform: 'uppercase' as const, marginBottom: 6, fontFamily: dash.fontMono }}>02 · Observatoire</div>
            <h1 style={{ fontSize: 28, fontWeight: 800, color: dash.ink, marginBottom: 4 }}>L&apos;Observatoire</h1>
            <p style={{ fontSize: 14, color: dash.inkMuted }}>{articles.length} publications · Données empiriques & physique naturelle</p>
          </motion.div>

          {/* Filters */}
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' as const, marginBottom: 20 }}>
            {[{ id: 'all', label: 'Tout' }, { id: 'pinned', label: '★ Épinglés' }, { id: 'physique-naturelle', label: 'Expériences' }, { id: 'optique', label: 'Optique' }].map(f => (
              <button key={f.id} onClick={() => setFilter(f.id)} style={{
                padding: '6px 14px', borderRadius: 8, fontSize: 12, fontWeight: 600,
                fontFamily: dash.fontMain, border: `1px solid ${filter === f.id ? dash.ink : dash.border}`,
                background: filter === f.id ? dash.ink : dash.card,
                color: filter === f.id ? '#fff' : dash.inkMuted,
                cursor: 'pointer', transition: 'all 0.2s',
              }}>{f.label}</button>
            ))}
          </div>

          {/* Articles */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {filtered.map((a, i) => {
              const tc = TAG_COLORS[a.tags?.find(t => TAG_COLORS[t]) || ''] || { bg: dash.borderSoft, color: dash.inkMuted };
              const isExp = a.tags.includes('physique-naturelle');
              return (
                <motion.div key={a.slug} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03, duration: 0.3 }}>
                  <Link href={`/article/${a.slug}`} className="dash-card-sm" style={{
                    display: 'flex', alignItems: 'center', gap: 14, padding: '14px 18px',
                    cursor: 'pointer', transition: 'all 0.2s',
                  }}>
                    <span className="badge" style={{
                      background: isExp ? dash.opalSoft : dash.lavenderSoft,
                      color: isExp ? dash.opal : dash.lavender,
                      minWidth: 56, textAlign: 'center' as const, fontSize: 10,
                    }}>{isExp ? 'EXP' : 'OBS'}</span>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 14, fontWeight: 600, color: dash.ink, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' as const }}>
                        {a.pinned && <span style={{ color: dash.saffron, marginRight: 6 }}>★</span>}
                        {a.title}
                      </div>
                      {a.description && <div style={{ fontSize: 12, color: dash.inkGhost, marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' as const }}>{a.description}</div>}
                    </div>
                    <div className="hidden sm:flex" style={{ gap: 5 }}>
                      {a.tags.filter(t => t !== 'l-observatoire' && t !== 'expériences' && t !== 'physique-naturelle').slice(0, 2).map(t => {
                        const c = TAG_COLORS[t] || { bg: dash.borderSoft, color: dash.inkMuted };
                        return <span key={t} className="badge" style={{ background: c.bg, color: c.color }}>{t}</span>;
                      })}
                    </div>
                    <span style={{ fontSize: 12, color: dash.inkGhost, fontFamily: dash.fontMono, whiteSpace: 'nowrap' as const }}>{a.readTime}m</span>
                  </Link>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Sidebar */}
        <div className="hidden lg:flex" style={{ flexDirection: 'column' as const, gap: 16, position: 'sticky' as const, top: 80 }}>
          {/* Activity chart */}
          <div className="dash-card" style={{ padding: '20px' }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: dash.ink, marginBottom: 4 }}>Activité de recherche</div>
            <div style={{ fontSize: 11, color: dash.inkGhost, marginBottom: 14 }}>Publications cumulées 2024–2026</div>
            <Spark data={[4, 8, 12, 18, 25, 35, 45, 52, articles.length]} color={dash.lavender} h={70} />
            <div style={{ display: 'flex', gap: 16, marginTop: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <div style={{ width: 12, height: 2, background: dash.lavender, borderRadius: 2 }} />
                <span style={{ fontSize: 10, color: dash.inkMuted }}>Publications</span>
              </div>
            </div>
          </div>

          {/* Tags cloud */}
          <div className="dash-card" style={{ padding: '20px' }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: dash.ink, marginBottom: 12 }}>Tags</div>
            <div style={{ display: 'flex', flexWrap: 'wrap' as const, gap: 6 }}>
              {allTags.slice(0, 14).map(tag => {
                const c = TAG_COLORS[tag] || { bg: dash.borderSoft, color: dash.inkMuted };
                return (
                  <button key={tag} onClick={() => setFilter(tag)} className="badge" style={{
                    background: filter === tag ? c.color : c.bg,
                    color: filter === tag ? '#fff' : c.color,
                    cursor: 'pointer', border: 'none', fontFamily: dash.fontMain, transition: 'all 0.2s',
                  }}>{tag}</button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
