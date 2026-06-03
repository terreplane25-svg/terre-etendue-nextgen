'use client';
import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { dash, PILLARS } from '@/lib/design-tokens';
import { getArticleImage } from '@/lib/article-images';

interface HomeProps {
  counts: { total: number; headquarters: number; observatory: number; library: number; lab: number; experiments: number };
  recent: { slug: string; title: string; category: string; tags: string[]; pinned: boolean; readTime: number; date?: string; description?: string }[];
}

function Spark({ data, color }: { data: number[]; color: string }) {
  const max = Math.max(...data), min = Math.min(...data), r = max - min || 1;
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * 80},${26 - ((v - min) / r) * 22 - 2}`).join(' ');
  return <svg width={80} height={28} viewBox="0 0 80 28"><polyline points={pts} fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>;
}

function KPI({ label, value, sub, color, spark, delay }: { label: string; value: string; sub: string; color: string; spark: number[]; delay: number }) {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay }}
      className="dash-card" style={{ padding: '22px 24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <div style={{ width: 8, height: 8, borderRadius: '50%', background: color, opacity: 0.7 }} />
        <span style={{ fontSize: 12, fontWeight: 600, color: dash.inkMuted, letterSpacing: '0.06em', textTransform: 'uppercase' as const }}>{label}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <span style={{ fontSize: 32, fontWeight: 800, color: dash.ink, lineHeight: 1 }}>{value}</span>
        <Spark data={spark} color={color} />
      </div>
      <span style={{ fontSize: 13, color: dash.inkGhost, marginTop: 6, display: 'block' }}>{sub}</span>
    </motion.div>
  );
}

const PILLAR_IMAGES: Record<string, string> = {
  headquarters: 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=600&h=400&fit=crop',
  observatory: 'https://images.unsplash.com/photo-1507400492013-162706c8c05e?w=600&h=400&fit=crop',
  library: 'https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=600&h=400&fit=crop',
  lab: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&h=400&fit=crop',
  experiences: 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=600&h=400&fit=crop',
};

export default function HomeClient({ counts, recent }: HomeProps) {
  return (
    <div>
      {/* ═══ HERO — plus visible ═══ */}
      <motion.section initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8 }}
        style={{ position: 'relative', overflow: 'hidden', height: 380, display: 'flex', alignItems: 'flex-end', marginBottom: 36 }}>
        <img src="https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/04/fond_horizon.jpg"
          alt="Horizon" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'center 60%' }} />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(244,245,247,0.85) 0%, transparent 40%)' }} />
        <div style={{ position: 'relative', maxWidth: 1200, margin: '0 auto', padding: '0 24px 40px', width: '100%' }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: dash.lavender, letterSpacing: '0.12em', textTransform: 'uppercase' as const, marginBottom: 10, fontFamily: dash.fontMono }}>Tableau de bord</div>
          <h1 style={{ fontSize: 38, fontWeight: 800, color: dash.ink, textShadow: '0 1px 8px rgba(255,255,255,0.6)', marginBottom: 8, lineHeight: 1.15 }}>Terre Étendue Islam</h1>
          <p style={{ fontSize: 16, color: dash.inkSoft, maxWidth: 500 }}>Revue indépendante de cosmologie · Examen critique · Données empiriques · Sources sacrées</p>
        </div>
      </motion.section>

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px 64px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 18, marginBottom: 40 }}>
          <KPI label="Publications" value={String(counts.total)} sub={`+${counts.experiments} expériences`} color={dash.lavender} spark={[8,12,18,25,35,48,counts.total]} delay={0.1} />
          <KPI label="Sources" value="450+" sub="primaires vérifiées" color={dash.saffron} spark={[40,80,150,250,350,420,450]} delay={0.15} />
          <KPI label="Observations" value="11K" sub="données empiriques" color={dash.opal} spark={[2,3,5,6,8,10,11]} delay={0.2} />
          <KPI label="Modèles 3D" value="3" sub="simulateurs interactifs" color={dash.cyan} spark={[0,0,1,1,2,3,3]} delay={0.25} />
        </div>

        <h2 style={{ fontSize: 20, fontWeight: 750, color: dash.ink, marginBottom: 18 }}>Les piliers</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 18, marginBottom: 48 }}>
          {PILLARS.map((p, i) => (
            <motion.div key={p.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45, delay: 0.35 + i * 0.06 }}>
              <Link href={p.href} className="dash-card" style={{ display: 'flex', flexDirection: 'column', cursor: 'pointer', overflow: 'hidden' }}>
                <div style={{ height: 140, overflow: 'hidden', position: 'relative' }}>
                  <img src={PILLAR_IMAGES[p.id] || PILLAR_IMAGES.observatory} alt={p.name} style={{ width: '100%', height: '100%', objectFit: 'cover', opacity: 0.85 }} loading="lazy" />
                  <div style={{ position: 'absolute', inset: 0, background: `linear-gradient(135deg, ${p.color}22 0%, transparent 60%)` }} />
                  <span className="badge" style={{ position: 'absolute', top: 12, right: 12, background: 'rgba(255,255,255,0.92)', color: p.color, backdropFilter: 'blur(8px)', fontSize: 11 }}>{p.num}</span>
                </div>
                <div style={{ padding: '20px 22px' }}>
                  <div style={{ fontSize: 17, fontWeight: 750, color: dash.ink, marginBottom: 4 }}>{p.name}</div>
                  <div style={{ fontSize: 14, color: dash.inkMuted, marginBottom: 14 }}>{p.sub}</div>
                  <div style={{ fontSize: 13, color: dash.inkGhost }}>
                    {p.id === 'headquarters' ? counts.headquarters : p.id === 'observatory' ? counts.observatory : p.id === 'library' ? counts.library : p.id === 'lab' ? counts.lab : counts.experiments} publications
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>

        <h2 style={{ fontSize: 20, fontWeight: 750, color: dash.ink, marginBottom: 18 }}>Publications récentes</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {recent.map((a, i) => (
            <motion.div key={a.slug} initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.35, delay: 0.5 + i * 0.04 }}>
              <Link href={`/article/${a.slug}`} className="dash-card" style={{ display: 'flex', overflow: 'hidden', cursor: 'pointer' }}>
                <div style={{ width: 180, minHeight: 140, flexShrink: 0, overflow: 'hidden' }}>
                  <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
                </div>
                <div style={{ padding: '18px 24px', flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 17, fontWeight: 700, color: dash.ink, marginBottom: 6, lineHeight: 1.35 }}>{a.title}</div>
                  <div style={{ fontSize: 12, color: dash.inkGhost, marginBottom: 8, fontFamily: dash.fontMono }}>Terre Etendue · {a.readTime} min</div>
                  {a.description && <div style={{ fontSize: 14, color: dash.inkMuted, lineHeight: 1.55, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as any }}>{a.description}</div>}
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
