'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { dash, TAG_COLORS } from '@/lib/design-tokens';
import { getArticleImage } from '@/lib/article-images';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

const EXP_LINKS: Record<string, { slug: string; label: string }> = {
  "pourquoi-les-choses-montent-et-descendent": { slug: "densite-et-flottabilite", label: "Fiche expérience : densité" },
  "pression-lumiere-halos-rayons-et-ondes": { slug: "la-pression-atmospherique", label: "Fiche expérience : pression" },
  "lhorizon-la-perspective-et-la-refraction": { slug: "la-perspective-lineaire", label: "Fiche expérience : perspective" },
  "ce-quon-voit-quand-on-ne-devrait-plus-voir": { slug: "diminution-angulaire-taille-apparente", label: "Fiche expérience : angle visuel" },
  "cartes-routes-boussoles-et-le-mystere-antarctique": { slug: "magnetisme-et-electromagnetisme", label: "Fiche expérience : magnétisme" },
};

export default function ObservatoryClient({ articles }: { articles: A[] }) {
  const [filter, setFilter] = useState('all');
  const filtered = filter === 'all' ? articles : filter === 'pinned' ? articles.filter(a => a.pinned) : articles.filter(a => a.tags.includes(filter));

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '32px 24px 64px' }}>
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 28 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: dash.cyan, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 6, fontFamily: dash.fontMono }}>02 · Observatoire</div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: dash.ink, marginBottom: 4 }}>L&apos;Observatoire</h1>
        <p style={{ fontSize: 14, color: dash.inkMuted }}>{articles.length} analyses · <Link href="/experiences" style={{ color: dash.opal, fontWeight: 600 }}>Voir les fiches expériences →</Link></p>
      </motion.div>

      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 24 }}>
        {[{ id: 'all', label: 'Tout' }, { id: 'pinned', label: '★ Épinglés' }].map(f => (
          <button key={f.id} onClick={() => setFilter(f.id)} style={{
            padding: '6px 14px', borderRadius: 8, fontSize: 12, fontWeight: 600, fontFamily: dash.fontMain,
            border: `1px solid ${filter === f.id ? dash.ink : dash.border}`,
            background: filter === f.id ? dash.ink : dash.card, color: filter === f.id ? '#fff' : dash.inkMuted, cursor: 'pointer',
          }}>{f.label}</button>
        ))}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {filtered.map((a, i) => {
          const exp = EXP_LINKS[a.slug];
          return (
            <motion.div key={a.slug} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}>
              <div className="dash-card" style={{ overflow: 'hidden' }}>
                <Link href={`/article/${a.slug}`} style={{ display: 'flex', cursor: 'pointer' }}>
                  <div style={{ width: 140, minHeight: 100, flexShrink: 0, overflow: 'hidden' }}>
                    <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
                  </div>
                  <div style={{ padding: '14px 20px', flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 15, fontWeight: 700, color: dash.ink, marginBottom: 4, lineHeight: 1.3 }}>
                      {a.pinned && <span style={{ color: dash.saffron, marginRight: 6 }}>★</span>}{a.title}
                    </div>
                    <div style={{ fontSize: 11, color: dash.inkGhost, marginBottom: 6, fontFamily: dash.fontMono }}>Terre Etendue · {a.readTime} min</div>
                    {a.description && <div style={{ fontSize: 13, color: dash.inkMuted, lineHeight: 1.5, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as any }}>{a.description}</div>}
                  </div>
                </Link>
                {exp && (
                  <div style={{ padding: '8px 20px 12px', borderTop: `1px solid ${dash.borderSoft}` }}>
                    <Link href={`/article/${exp.slug}`} style={{ fontSize: 11, color: dash.opal, fontWeight: 600 }}>🧪 {exp.label}</Link>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
