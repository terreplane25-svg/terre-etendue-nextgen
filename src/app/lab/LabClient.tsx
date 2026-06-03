'use client';
import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { dash } from '@/lib/design-tokens';
import { getArticleImage } from '@/lib/article-images';
import PageHero from '@/components/PageHero';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }
const TOOLS = [
  { label: 'Calculateur de courbure', desc: "Calculez la courbure théorique pour n'importe quelle distance", icon: '📐', color: dash.opal },
  { label: 'Dôme céleste 3D', desc: "Modèle interactif du ciel observable", icon: '🌐', color: dash.cyan },
  { label: 'Simulateur optique', desc: "Perspective et réfraction en temps réel", icon: '🔭', color: dash.lavender },
];
// Exclure MGPP (toutes variantes possibles du slug)
const EXCLUDED_PATTERNS = ['mgpp', 'modele-geostationnaire', 'monde-plat-et-du-paradis'];

export default function LabClient({ articles }: { articles: A[] }) {
  const filtered = articles.filter(a => !EXCLUDED_PATTERNS.some(p => a.slug.includes(p)));
  return (
    <div>
      <PageHero title="Le Lab" subtitle="Modélisation 3D, simulateurs et outils de calcul" color={dash.opal} image="https://green-gnat-134443.hostingersite.com/wp-content/uploads/2025/10/cropped-entete-logo-e1760704486721.png" />
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '0 24px 64px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(270px, 1fr))', gap: 18, marginBottom: 40 }}>
          {TOOLS.map((t, i) => (
            <motion.div key={t.label} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 + i * 0.08 }}>
              <div className="dash-card" style={{ padding: '26px 24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
                  <div style={{ width: 44, height: 44, borderRadius: 12, background: t.color + '15', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22 }}>{t.icon}</div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: dash.ink }}>{t.label}</div>
                </div>
                <div style={{ fontSize: 14, color: dash.inkMuted, lineHeight: 1.5, marginBottom: 14 }}>{t.desc}</div>
                <span className="badge" style={{ background: dash.bg, color: dash.inkGhost, fontSize: 11 }}>Bientôt disponible</span>
              </div>
            </motion.div>
          ))}
        </div>
        {filtered.length > 0 && (
          <>
            <h2 style={{ fontSize: 18, fontWeight: 750, color: dash.ink, marginBottom: 16 }}>Publications du Lab</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {filtered.map((a, i) => (
                <motion.div key={a.slug} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 + i * 0.03 }}>
                  <Link href={`/article/${a.slug}`} className="dash-card" style={{ display: 'flex', overflow: 'hidden', cursor: 'pointer' }}>
                    <div style={{ width: 180, minHeight: 140, flexShrink: 0, overflow: 'hidden' }}>
                      <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
                    </div>
                    <div style={{ padding: '18px 24px', flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 17, fontWeight: 700, color: dash.ink, marginBottom: 6, lineHeight: 1.35 }}>{a.title}</div>
                      <div style={{ fontSize: 12, color: dash.inkGhost, fontFamily: dash.fontMono }}>{a.readTime} min</div>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
