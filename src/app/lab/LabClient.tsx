'use client';
import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { dash } from '@/lib/design-tokens';
import { getArticleImage } from '@/lib/article-images';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

const TOOLS = [
  { label: 'Calculateur de courbure', desc: "Calculez la courbure théorique pour n'importe quelle distance", icon: '📐', color: dash.opal, href: '/lab' },
  { label: 'Dôme céleste 3D', desc: "Modèle interactif du ciel observable", icon: '🌐', color: dash.cyan, href: '/lab' },
  { label: 'Simulateur optique', desc: "Perspective et réfraction en temps réel", icon: '🔭', color: dash.lavender, href: '/lab' },
];

const EXCLUDED = ['le-modele-geostationnaire-du-monde-plat-et-du-paradis'];

export default function LabClient({ articles }: { articles: A[] }) {
  const filtered = articles.filter(a => !EXCLUDED.some(ex => a.slug.includes(ex)));

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '32px 24px 64px' }}>
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: dash.opal, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 6, fontFamily: dash.fontMono }}>04 · Lab</div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: dash.ink, marginBottom: 4 }}>Le Lab</h1>
        <p style={{ fontSize: 14, color: dash.inkMuted }}>Modélisation 3D, simulateurs interactifs et outils de calcul</p>
      </motion.div>

      {/* Tools — non-clickable, coming soon */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 16, marginBottom: 36 }}>
        {TOOLS.map((t, i) => (
          <motion.div key={t.label} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 + i * 0.08 }}>
            <div className="dash-card" style={{ padding: '24px 22px', position: 'relative', overflow: 'hidden' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: t.color + '15', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20 }}>{t.icon}</div>
                <div style={{ fontSize: 15, fontWeight: 700, color: dash.ink }}>{t.label}</div>
              </div>
              <div style={{ fontSize: 13, color: dash.inkMuted, lineHeight: 1.5 }}>{t.desc}</div>
              <div style={{ marginTop: 12 }}>
                <span className="badge" style={{ background: dash.bg, color: dash.inkGhost }}>Bientôt disponible</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Articles */}
      {filtered.length > 0 && (
        <>
          <h2 style={{ fontSize: 15, fontWeight: 750, color: dash.ink, marginBottom: 14 }}>Publications du Lab</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {filtered.map((a, i) => (
              <motion.div key={a.slug} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 + i * 0.03 }}>
                <Link href={`/article/${a.slug}`} className="dash-card" style={{ display: 'flex', overflow: 'hidden', cursor: 'pointer' }}>
                  <div style={{ width: 140, minHeight: 100, flexShrink: 0, overflow: 'hidden' }}>
                    <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
                  </div>
                  <div style={{ padding: '14px 20px', flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 15, fontWeight: 700, color: dash.ink, marginBottom: 4, lineHeight: 1.3 }}>{a.title}</div>
                    <div style={{ fontSize: 11, color: dash.inkGhost, fontFamily: dash.fontMono }}>{a.readTime} min</div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
