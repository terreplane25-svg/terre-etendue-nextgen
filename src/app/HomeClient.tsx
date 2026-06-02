'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { dash, PILLARS, TAG_COLORS } from '@/lib/design-tokens';

interface HomeProps {
  counts: { total: number; headquarters: number; observatory: number; library: number; lab: number; experiments: number };
  recent: { slug: string; title: string; category: string; tags: string[]; pinned: boolean; readTime: number }[];
}

// ── Sparkline ──
function Spark({ data, color }: { data: number[]; color: string }) {
  const max = Math.max(...data), min = Math.min(...data), r = max - min || 1;
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * 80},${26 - ((v - min) / r) * 22 - 2}`).join(' ');
  return <svg width={80} height={28} viewBox="0 0 80 28"><polyline points={pts} fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>;
}

// ── KPI Card ──
function KPI({ label, value, sub, color, spark, delay }: { label: string; value: string; sub: string; color: string; spark: number[]; delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="dash-card" style={{ padding: '20px 22px' }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <div style={{ width: 8, height: 8, borderRadius: '50%', background: color, opacity: 0.7 }} />
        <span style={{ fontSize: 11, fontWeight: 600, color: dash.inkMuted, letterSpacing: '0.06em', textTransform: 'uppercase' as const }}>{label}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <span style={{ fontSize: 30, fontWeight: 800, color: dash.ink, lineHeight: 1 }}>{value}</span>
        <Spark data={spark} color={color} />
      </div>
      <span style={{ fontSize: 12, color: dash.inkGhost, marginTop: 4, display: 'block' }}>{sub}</span>
    </motion.div>
  );
}

// ── Category route ──
function catRoute(_c: string) {
  return '/article';
}

export default function HomeClient({ counts, recent }: HomeProps) {
  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '32px 24px 64px' }}>

      {/* ═══ HEADER ═══ */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
        style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: dash.lavender, letterSpacing: '0.1em', textTransform: 'uppercase' as const, marginBottom: 8, fontFamily: dash.fontMono }}>
          Tableau de bord
        </div>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: dash.ink, marginBottom: 6, lineHeight: 1.2 }}>
          Terre Étendue Islam
        </h1>
        <p style={{ fontSize: 15, color: dash.inkMuted, maxWidth: 500 }}>
          Revue indépendante de cosmologie · Examen critique · Données empiriques · Sources sacrées
        </p>
      </motion.div>

      {/* ═══ KPI ROW ═══ */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 36 }}>
        <KPI label="Publications" value={String(counts.total)} sub={`+${counts.experiments} expériences`} color={dash.lavender} spark={[8, 12, 18, 25, 35, 48, counts.total]} delay={0.1} />
        <KPI label="Sources" value="450+" sub="primaires vérifiées" color={dash.saffron} spark={[40, 80, 150, 250, 350, 420, 450]} delay={0.15} />
        <KPI label="Observations" value="11K" sub="données empiriques" color={dash.opal} spark={[2, 3, 5, 6, 8, 10, 11]} delay={0.2} />
        <KPI label="Modèles 3D" value="3" sub="simulateurs interactifs" color={dash.cyan} spark={[0, 0, 1, 1, 2, 3, 3]} delay={0.25} />
      </div>

      {/* ═══ BENTO GRID — PILIERS ═══ */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4, delay: 0.3 }}>
        <h2 style={{ fontSize: 18, fontWeight: 750, color: dash.ink, marginBottom: 16 }}>Les piliers</h2>
      </motion.div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16, marginBottom: 40 }}>
        {PILLARS.map((p, i) => (
          <motion.div
            key={p.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.35 + i * 0.06 }}
          >
            <Link href={p.href} className="dash-card" style={{
              display: 'flex', flexDirection: 'column', gap: 12,
              padding: '26px 24px', cursor: 'pointer',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: 28, opacity: 0.45 }}>{p.icon}</span>
                <span className="badge" style={{ background: p.colorSoft, color: p.color }}>{p.num}</span>
              </div>
              <div>
                <div style={{ fontSize: 16, fontWeight: 750, color: dash.ink, marginBottom: 3 }}>{p.name}</div>
                <div style={{ fontSize: 13, color: dash.inkMuted }}>{p.sub}</div>
              </div>
              <div style={{ fontSize: 12, color: dash.inkGhost, marginTop: 'auto' }}>
                {p.id === 'headquarters' ? counts.headquarters :
                 p.id === 'observatory' ? counts.observatory :
                 p.id === 'library' ? counts.library :
                 p.id === 'lab' ? counts.lab :
                 counts.experiments} publications
              </div>
            </Link>
          </motion.div>
        ))}
      </div>

      {/* ═══ RECENT ARTICLES ═══ */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4, delay: 0.6 }}>
        <h2 style={{ fontSize: 18, fontWeight: 750, color: dash.ink, marginBottom: 16 }}>Publications récentes</h2>
      </motion.div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {recent.map((a, i) => {
          const tc = TAG_COLORS[a.tags?.[0]] || { bg: dash.borderSoft, color: dash.inkMuted };
          return (
            <motion.div key={a.slug}
              initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.35, delay: 0.65 + i * 0.04 }}
            >
              <Link href={`${catRoute(a.category)}/${a.slug}`} className="dash-card-sm" style={{
                display: 'flex', alignItems: 'center', gap: 14, padding: '12px 18px',
                cursor: 'pointer', transition: 'all 0.2s',
              }}>
                {a.pinned && <span style={{ color: dash.saffron, fontSize: 14 }}>★</span>}
                <span style={{ flex: 1, fontSize: 14, fontWeight: 600, color: dash.ink, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' as const }}>
                  {a.title}
                </span>
                {a.tags?.slice(0, 1).map(t => (
                  <span key={t} className="badge" style={{ background: tc.bg, color: tc.color, fontSize: 10 }}>{t}</span>
                ))}
                <span style={{ fontSize: 12, color: dash.inkGhost, fontFamily: dash.fontMono, whiteSpace: 'nowrap' as const }}>{a.readTime} min</span>
              </Link>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
