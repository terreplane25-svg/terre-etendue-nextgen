'use client';
import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { dash } from '@/lib/design-tokens';
import { getArticleImage } from '@/lib/article-images';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

export default function LibraryClient({ priority, articles }: { priority: A[]; articles: A[] }) {
  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '32px 24px 64px' }}>
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: dash.saffron, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 6, fontFamily: dash.fontMono }}>03 · Bibliothèque</div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: dash.ink, marginBottom: 4 }}>La Bibliothèque</h1>
        <p style={{ fontSize: 14, color: dash.inkMuted }}>{priority.length + articles.length} publications · Sources sacrées, textes historiques et analyses fondatrices</p>
      </motion.div>

      {/* ═══ PRIORITY — Image 1 style (card + big image on top) ═══ */}
      {priority.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} style={{ marginBottom: 40 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <span style={{ fontSize: 16 }}>📖</span>
            <h2 style={{ fontSize: 15, fontWeight: 750, color: dash.ink }}>Lecture prioritaire</h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 20 }}>
            {priority.map((a, i) => (
              <motion.div key={a.slug} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 + i * 0.08 }}>
                <Link href={`/article/${a.slug}`} className="dash-card" style={{ display: 'block', overflow: 'hidden', cursor: 'pointer' }}>
                  <div style={{ height: 180, overflow: 'hidden', position: 'relative' }}>
                    <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
                    <span className="badge" style={{ position: 'absolute', top: 12, left: 12, background: 'rgba(255,255,255,0.92)', color: dash.gold, border: `1px solid ${dash.gold}30`, backdropFilter: 'blur(8px)' }}>★ PRIORITAIRE</span>
                  </div>
                  <div style={{ padding: '20px 22px' }}>
                    <div style={{ fontSize: 17, fontWeight: 750, color: dash.ink, lineHeight: 1.35, marginBottom: 8 }}>{a.title}</div>
                    {a.description && <div style={{ fontSize: 13, color: dash.inkMuted, lineHeight: 1.55, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical' as any, overflow: 'hidden' }}>{a.description}</div>}
                    <div style={{ fontSize: 11, color: dash.inkGhost, marginTop: 10, fontFamily: dash.fontMono }}>{a.readTime} min de lecture</div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* ═══ ALL ARTICLES — Image 2 style (horizontal, image left) ═══ */}
      <h2 style={{ fontSize: 15, fontWeight: 750, color: dash.ink, marginBottom: 14 }}>Toutes les publications</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {articles.map((a, i) => (
          <motion.div key={a.slug} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 + i * 0.03 }}>
            <Link href={`/article/${a.slug}`} className="dash-card" style={{ display: 'flex', overflow: 'hidden', cursor: 'pointer' }}>
              <div style={{ width: 140, minHeight: 100, flexShrink: 0, overflow: 'hidden' }}>
                <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
              </div>
              <div style={{ padding: '14px 20px', flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 15, fontWeight: 700, color: dash.ink, marginBottom: 4, lineHeight: 1.3 }}>{a.title}</div>
                <div style={{ fontSize: 11, color: dash.inkGhost, marginBottom: 6, fontFamily: dash.fontMono }}>Terre Etendue · {a.readTime} min</div>
                {a.description && <div style={{ fontSize: 13, color: dash.inkMuted, lineHeight: 1.5, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as any }}>{a.description}</div>}
              </div>
            </Link>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
