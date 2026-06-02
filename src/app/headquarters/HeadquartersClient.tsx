'use client';
import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { dash, TAG_COLORS } from '@/lib/design-tokens';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

export default function HeadquartersClient({ articles }: { articles: A[] }) {
  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '32px 24px 64px' }}>
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 28 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: dash.lavender, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 6, fontFamily: dash.fontMono }}>01 · Quartier Général</div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: dash.ink, marginBottom: 4 }}>Le Quartier Général</h1>
        <p style={{ fontSize: 14, color: dash.inkMuted }}>{articles.length} publications · Épistémologie et méthode</p>
      </motion.div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {articles.map((a, i) => (
          <motion.div key={a.slug} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}>
            <Link href={`/headquarters/${a.slug}`} className="dash-card-sm" style={{
              display: 'flex', alignItems: 'center', gap: 14, padding: '14px 18px', cursor: 'pointer',
            }}>
              <span className="badge" style={{ background: dash.lavenderSoft, color: dash.lavender }}>QG</span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: dash.ink, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {a.pinned && <span style={{ color: dash.saffron, marginRight: 6 }}>★</span>}{a.title}
                </div>
              </div>
              <span style={{ fontSize: 12, color: dash.inkGhost, fontFamily: dash.fontMono }}>{a.readTime}m</span>
            </Link>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
