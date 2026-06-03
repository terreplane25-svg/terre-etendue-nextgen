'use client';
import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { dash } from '@/lib/design-tokens';
import { getArticleImage } from '@/lib/article-images';
import PageHero from '@/components/PageHero';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

export default function LibraryClient({ priority, articles }: { priority: A[]; articles: A[] }) {
  return (
    <div>
      <PageHero title="La Bibliothèque" subtitle={`${priority.length + articles.length} publications · Sources sacrées et textes historiques`} color={dash.saffron} image="https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/06/architecture-brutaliste-batiment-marais-scaled.jpg" />
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '0 24px 64px' }}>
        {priority.length > 0 && (
          <div style={{ marginBottom: 40 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 18 }}>
              <span style={{ fontSize: 18 }}>📖</span>
              <h2 style={{ fontSize: 18, fontWeight: 750, color: dash.ink }}>Lecture prioritaire</h2>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
              {priority.map((a, i) => (
                <motion.div key={a.slug} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 + i * 0.08 }}>
                  <Link href={`/article/${a.slug}`} className="dash-card" style={{ display: 'block', overflow: 'hidden', cursor: 'pointer' }}>
                    <div style={{ height: 200, overflow: 'hidden', position: 'relative' }}>
                      <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
                      <span className="badge" style={{ position: 'absolute', top: 14, left: 14, background: 'rgba(255,255,255,0.93)', color: dash.gold, border: `1px solid ${dash.gold}30`, backdropFilter: 'blur(8px)', fontSize: 11 }}>★ PRIORITAIRE</span>
                    </div>
                    <div style={{ padding: '22px 24px' }}>
                      <div style={{ fontSize: 18, fontWeight: 750, color: dash.ink, lineHeight: 1.35, marginBottom: 8 }}>{a.title}</div>
                      {a.description && <div style={{ fontSize: 14, color: dash.inkMuted, lineHeight: 1.55, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical' as any, overflow: 'hidden' }}>{a.description}</div>}
                      <div style={{ fontSize: 12, color: dash.inkGhost, marginTop: 12, fontFamily: dash.fontMono }}>{a.readTime} min de lecture</div>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>
        )}
        <h2 style={{ fontSize: 18, fontWeight: 750, color: dash.ink, marginBottom: 16 }}>Toutes les publications</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {articles.map((a, i) => (
            <motion.div key={a.slug} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 + i * 0.03 }}>
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
