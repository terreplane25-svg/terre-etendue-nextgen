'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { dash, TAG_COLORS } from '@/lib/design-tokens';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

// Reverse cross-links: analysis → experiment
const EXPERIMENT_LINKS: Record<string, { slug: string; label: string }> = {
  "pourquoi-les-choses-montent-et-descendent": { slug: "densite-et-flottabilite", label: "Fiche expérience : densité" },
  "pression-lumiere-halos-rayons-et-ondes": { slug: "la-pression-atmospherique", label: "Fiche expérience : pression" },
  "lhorizon-la-perspective-et-la-refraction": { slug: "la-perspective-lineaire", label: "Fiche expérience : perspective" },
  "ce-quon-voit-quand-on-ne-devrait-plus-voir": { slug: "diminution-angulaire-taille-apparente", label: "Fiche expérience : angle visuel" },
  "cartes-routes-boussoles-et-le-mystere-antarctique": { slug: "magnetisme-et-electromagnetisme", label: "Fiche expérience : magnétisme" },
};

function Spark({ data, color, w = 200, h = 60 }: { data: number[]; color: string; w?: number; h?: number }) {
  const max = Math.max(...data), min = Math.min(...data), r = max - min || 1;
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - 4 - ((v - min) / r) * (h - 8)}`).join(' ');
  const fill = pts + ` ${w},${h} 0,${h}`;
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ display: 'block', width: '100%' }}>
      <defs><linearGradient id="gLav" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={color} stopOpacity="0.15" /><stop offset="100%" stopColor={color} stopOpacity="0" /></linearGradient></defs>
      <polygon points={fill} fill="url(#gLav)" />
      <polyline points={pts} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

export default function ObservatoryClient({ articles }: { articles: A[] }) {
  const [filter, setFilter] = useState('all');

  const allTags = Array.from(new Set(articles.flatMap(a => a.tags))).filter(t => t !== 'l-observatoire');
  const filtered = filter === 'all' ? articles
    : filter === 'pinned' ? articles.filter(a => a.pinned)
    : articles.filter(a => a.tags.includes(filter));

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '32px 24px 64px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 28, alignItems: 'start' }}>
        <div>
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 28 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: dash.cyan, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 6, fontFamily: dash.fontMono }}>02 · Observatoire</div>
            <h1 style={{ fontSize: 28, fontWeight: 800, color: dash.ink, marginBottom: 4 }}>L&apos;Observatoire</h1>
            <p style={{ fontSize: 14, color: dash.inkMuted }}>{articles.length} publications analytiques · <Link href="/experiences" style={{ color: dash.opal, fontWeight: 600 }}>Voir les {14} fiches expériences →</Link></p>
          </motion.div>

          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 20 }}>
            {[{ id: 'all', label: 'Tout' }, { id: 'pinned', label: '★ Épinglés' }].map(f => (
              <button key={f.id} onClick={() => setFilter(f.id)} style={{
                padding: '6px 14px', borderRadius: 8, fontSize: 12, fontWeight: 600,
                fontFamily: dash.fontMain, border: `1px solid ${filter === f.id ? dash.ink : dash.border}`,
                background: filter === f.id ? dash.ink : dash.card,
                color: filter === f.id ? '#fff' : dash.inkMuted, cursor: 'pointer',
              }}>{f.label}</button>
            ))}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {filtered.map((a, i) => {
              const exp = EXPERIMENT_LINKS[a.slug];
              return (
                <motion.div key={a.slug} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}>
                  <div className="dash-card-sm" style={{ padding: '14px 18px' }}>
                    <Link href={`/article/${a.slug}`} style={{ display: 'flex', alignItems: 'center', gap: 14, cursor: 'pointer' }}>
                      <span className="badge" style={{ background: dash.cyanSoft, color: dash.cyan, minWidth: 40, textAlign: 'center' }}>OBS</span>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: 14, fontWeight: 600, color: dash.ink, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {a.pinned && <span style={{ color: dash.saffron, marginRight: 6 }}>★</span>}{a.title}
                        </div>
                        {a.description && <div style={{ fontSize: 12, color: dash.inkGhost, marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{a.description}</div>}
                      </div>
                      <span style={{ fontSize: 12, color: dash.inkGhost, fontFamily: dash.fontMono, whiteSpace: 'nowrap' }}>{a.readTime}m</span>
                    </Link>
                    {exp && (
                      <div style={{ marginTop: 8, paddingTop: 8, borderTop: `1px solid ${dash.borderSoft}` }}>
                        <Link href={`/article/${exp.slug}`} style={{ fontSize: 11, color: dash.opal, fontWeight: 600 }}>
                          🧪 {exp.label}
                        </Link>
                      </div>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Sidebar */}
        <div className="hidden lg:flex" style={{ flexDirection: 'column', gap: 16, position: 'sticky', top: 80 }}>
          <div className="dash-card" style={{ padding: '20px' }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: dash.ink, marginBottom: 4 }}>Activité</div>
            <div style={{ fontSize: 11, color: dash.inkGhost, marginBottom: 14 }}>Publications cumulées</div>
            <Spark data={[4, 8, 12, 18, 25, 35, 45, 52, articles.length + 14]} color={dash.lavender} h={70} />
          </div>
          <div className="dash-card" style={{ padding: '20px' }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: dash.ink, marginBottom: 12 }}>Tags</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {allTags.slice(0, 12).map(tag => {
                const c = TAG_COLORS[tag] || { bg: dash.borderSoft, color: dash.inkMuted };
                return (
                  <button key={tag} onClick={() => setFilter(tag === filter ? 'all' : tag)} className="badge" style={{
                    background: filter === tag ? c.color : c.bg, color: filter === tag ? '#fff' : c.color,
                    cursor: 'pointer', border: 'none', fontFamily: dash.fontMain,
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
