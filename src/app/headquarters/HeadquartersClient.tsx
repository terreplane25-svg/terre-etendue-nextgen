'use client';
import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { dash } from '@/lib/design-tokens';
import { getArticleImage } from '@/lib/article-images';
import PageHero from '@/components/PageHero';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

export default function HeadquartersClient({ articles }: { articles: A[] }) {
  return (
    <div>
      <PageHero num="01 · Quartier Général" title="Le Quartier Général" subtitle={`${articles.length} publications · Épistémologie et méthode`} color={dash.lavender} image="https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=1400&h=400&fit=crop" />
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '0 24px 64px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {articles.map((a, i) => (
            <motion.div key={a.slug} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}>
              <Link href={`/article/${a.slug}`} className="dash-card" style={{ display: 'flex', overflow: 'hidden', cursor: 'pointer' }}>
                <div style={{ width: 180, minHeight: 140, flexShrink: 0, overflow: 'hidden' }}>
                  <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
                </div>
                <div style={{ padding: '18px 24px', flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 17, fontWeight: 700, color: dash.ink, marginBottom: 6, lineHeight: 1.35 }}>
                    {a.pinned && <span style={{ color: dash.saffron, marginRight: 6 }}>★</span>}{a.title}
                  </div>
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
