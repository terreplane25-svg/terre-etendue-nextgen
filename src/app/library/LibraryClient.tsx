'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { dash } from '@/lib/design-tokens';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

export default function LibraryClient({ priority, articles }: { priority: A[]; articles: A[] }) {
  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '32px 24px 64px' }}>

      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: dash.saffron, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 6, fontFamily: dash.fontMono }}>
          03 · Bibliothèque
        </div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: dash.ink, marginBottom: 4 }}>La Bibliothèque</h1>
        <p style={{ fontSize: 14, color: dash.inkMuted }}>
          {priority.length + articles.length} publications · Sources sacrées, textes historiques et analyses fondatrices
        </p>
      </motion.div>

      {/* ═══ PRIORITY READING ═══ */}
      {priority.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          style={{ marginBottom: 36 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <span style={{ fontSize: 16 }}>📖</span>
            <h2 style={{ fontSize: 15, fontWeight: 750, color: dash.ink }}>Lecture prioritaire</h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
            {priority.map((a, i) => (
              <motion.div key={a.slug} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 + i * 0.08 }}>
                <Link href={`/article/${a.slug}`} style={{
                  display: 'block', borderRadius: dash.radius, overflow: 'hidden',
                  border: `2px solid ${dash.gold}22`, cursor: 'pointer',
                  background: `linear-gradient(135deg, ${dash.goldSoft} 0%, ${dash.card} 100%)`,
                  boxShadow: dash.shadow, transition: 'all 0.25s',
                }}>
                  <div style={{ padding: '22px 22px 20px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                      <span className="badge" style={{
                        background: dash.goldSoft, color: dash.gold,
                        border: `1px solid ${dash.gold}30`,
                      }}>★ PRIORITAIRE</span>
                    </div>
                    <div style={{ fontSize: 16, fontWeight: 750, color: dash.ink, lineHeight: 1.35, marginBottom: 6 }}>
                      {a.title}
                    </div>
                    {a.description && (
                      <div style={{
                        fontSize: 13, color: dash.inkMuted, lineHeight: 1.5,
                        display: '-webkit-box', WebkitLineClamp: 3,
                        WebkitBoxOrient: 'vertical' as any, overflow: 'hidden',
                      }}>{a.description}</div>
                    )}
                    <div style={{ fontSize: 11, color: dash.inkGhost, marginTop: 10, fontFamily: dash.fontMono }}>
                      {a.readTime} min de lecture
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* ═══ ALL ARTICLES ═══ */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
        <h2 style={{ fontSize: 15, fontWeight: 750, color: dash.ink, marginBottom: 14 }}>
          Toutes les publications
        </h2>
      </motion.div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {articles.map((a, i) => (
          <motion.div key={a.slug} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 + i * 0.03 }}>
            <Link href={`/article/${a.slug}`} className="dash-card-sm" style={{
              display: 'flex', alignItems: 'center', gap: 14, padding: '14px 18px', cursor: 'pointer',
            }}>
              <span className="badge" style={{ background: dash.saffronSoft, color: dash.saffron }}>BIB</span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: dash.ink, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {a.pinned && <span style={{ color: dash.saffron, marginRight: 6 }}>★</span>}
                  {a.title}
                </div>
                {a.description && (
                  <div style={{ fontSize: 12, color: dash.inkGhost, marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {a.description}
                  </div>
                )}
              </div>
              <span style={{ fontSize: 12, color: dash.inkGhost, fontFamily: dash.fontMono }}>{a.readTime}m</span>
            </Link>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
