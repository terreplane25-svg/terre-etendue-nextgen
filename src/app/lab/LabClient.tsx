'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { dash } from '@/lib/design-tokens';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

const TOOLS = [
  { label: 'Calculateur de courbure', desc: 'Calculez la courbure théorique pour n\'importe quelle distance', icon: '📐', color: dash.opal },
  { label: 'Dôme céleste 3D', desc: 'Modèle interactif du ciel observable depuis une Terre étendue', icon: '🌐', color: dash.cyan },
  { label: 'Simulateur optique', desc: 'Perspective, réfraction et limites angulaires en temps réel', icon: '🔭', color: dash.lavender },
];

export default function LabClient({ articles }: { articles: A[] }) {
  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '32px 24px 64px' }}>

      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: dash.opal, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 6, fontFamily: dash.fontMono }}>
          04 · Lab
        </div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: dash.ink, marginBottom: 4 }}>Le Lab</h1>
        <p style={{ fontSize: 14, color: dash.inkMuted }}>
          Modélisation 3D, simulateurs interactifs et outils de calcul
        </p>
      </motion.div>

      {/* ═══ TOOLS GRID ═══ */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 16, marginBottom: 36 }}>
        {TOOLS.map((tool, i) => (
          <motion.div key={tool.label} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.08 }}>
            <div className="dash-card" style={{ padding: '24px 22px', cursor: 'pointer' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                <div style={{
                  width: 40, height: 40, borderRadius: 10,
                  background: tool.color + '15', display: 'flex',
                  alignItems: 'center', justifyContent: 'center', fontSize: 20,
                }}>{tool.icon}</div>
                <div style={{ fontSize: 15, fontWeight: 700, color: dash.ink }}>{tool.label}</div>
              </div>
              <div style={{ fontSize: 13, color: dash.inkMuted, lineHeight: 1.5 }}>{tool.desc}</div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* ═══ ARTICLES ═══ */}
      {articles.length > 0 && (
        <>
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
            <h2 style={{ fontSize: 15, fontWeight: 750, color: dash.ink, marginBottom: 14 }}>
              Publications du Lab
            </h2>
          </motion.div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {articles.map((a, i) => (
              <motion.div key={a.slug} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.45 + i * 0.03 }}>
                <Link href={`/article/${a.slug}`} className="dash-card-sm" style={{
                  display: 'flex', alignItems: 'center', gap: 14, padding: '14px 18px', cursor: 'pointer',
                }}>
                  <span className="badge" style={{ background: dash.opalSoft, color: dash.opal }}>LAB</span>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 14, fontWeight: 600, color: dash.ink, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {a.title}
                    </div>
                  </div>
                  <span style={{ fontSize: 12, color: dash.inkGhost, fontFamily: dash.fontMono }}>{a.readTime}m</span>
                </Link>
              </motion.div>
            ))}
          </div>
        </>
      )}

      {articles.length === 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
          <div className="dash-card" style={{
            padding: '40px 24px', textAlign: 'center',
          }}>
            <div style={{ fontSize: 32, opacity: 0.3, marginBottom: 12 }}>△</div>
            <div style={{ fontSize: 14, color: dash.inkMuted }}>
              Les simulateurs 3D interactifs arrivent bientôt.
            </div>
            <div style={{ fontSize: 12, color: dash.inkGhost, marginTop: 8 }}>
              Calculateur de courbure · Dôme céleste · Simulateur optique
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
