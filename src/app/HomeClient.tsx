'use client';
import React from 'react';
import Link from 'next/link';
import { getArticleImage } from '@/lib/article-images';

interface A { slug: string; title: string; description: string; category: string; tags: string[]; readTime: number; date: string; pinned: boolean; }

const CAT_LABEL: Record<string, string> = { headquarters: 'Centre de Recherche', observatory: 'Observatoire', library: 'Bibliothèque', lab: 'Outils', meta: 'TEI' };
const CAT_COLOR: Record<string, string> = { headquarters: '#7C6FC4', observatory: '#3580C0', library: '#C48A2E', lab: '#3A8F6E', meta: '#8A857D' };

export default function HomeClient({ articles }: { articles: A[] }) {
  const featured = articles[0];
  const medium = articles.slice(1, 4);
  const sidebar = articles.slice(4, 9);
  const latest = articles.slice(9, 18);

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px 24px 80px', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>

      {/* ═══ HERO GRID ═══ */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px 220px', gap: 24, marginBottom: 48 }}>

        {/* Featured article — large */}
        {featured && (
          <Link href={`/article/${featured.slug}`} style={{ position: 'relative', borderRadius: 8, overflow: 'hidden', display: 'block', minHeight: 420 }}>
            <img src={getArticleImage(featured.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', position: 'absolute', inset: 0 }} />
            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.75) 0%, transparent 60%)' }} />
            <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '28px 24px' }}>
              <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.7)', marginBottom: 8 }}>
                {featured.date && new Date(featured.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })} | {featured.readTime} min
              </div>
              <h2 style={{ fontSize: 26, fontWeight: 700, color: '#fff', lineHeight: 1.3, marginBottom: 8 }}>{featured.title}</h2>
              <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.8)', lineHeight: 1.5 }}>{featured.description}</p>
            </div>
          </Link>
        )}

        {/* Medium articles — stacked */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {medium.map(a => (
            <Link key={a.slug} href={`/article/${a.slug}`} style={{ display: 'flex', flexDirection: 'column', gap: 8, paddingBottom: 20, borderBottom: '1px solid #eee' }}>
              <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: 120, objectFit: 'cover', borderRadius: 6 }} />
              <div style={{ fontSize: 11, color: '#999' }}>{a.date && new Date(a.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })} | {a.readTime} min</div>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: '#141210', lineHeight: 1.35 }}>{a.title}</h3>
            </Link>
          ))}
        </div>

        {/* Sidebar — text only */}
        <div className="hidden lg:flex" style={{ flexDirection: 'column', gap: 0 }}>
          {sidebar.map(a => (
            <Link key={a.slug} href={`/article/${a.slug}`} style={{ display: 'block', padding: '14px 0', borderBottom: '1px solid #eee' }}>
              <div style={{ fontSize: 11, color: '#999', marginBottom: 4 }}>{a.date && new Date(a.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })} | {a.readTime} min</div>
              <h4 style={{ fontSize: 14, fontWeight: 700, color: '#141210', lineHeight: 1.35 }}>{a.title}</h4>
            </Link>
          ))}
        </div>
      </div>

      {/* ═══ LATEST ═══ */}
      <h2 style={{ fontSize: 28, fontWeight: 800, color: '#141210', marginBottom: 20, paddingBottom: 12, borderBottom: '3px solid #7C6FC4', display: 'inline-block' }}>Latest</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
        {latest.map(a => (
          <Link key={a.slug} href={`/article/${a.slug}`} style={{ display: 'flex', gap: 20, padding: '20px 0', borderBottom: '1px solid #eee', alignItems: 'flex-start' }}>
            <img src={getArticleImage(a.slug)} alt="" style={{ width: 180, height: 120, objectFit: 'cover', borderRadius: 6, flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <span style={{ fontSize: 11, fontWeight: 700, color: CAT_COLOR[a.category] || '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {CAT_LABEL[a.category] || a.category}
              </span>
              <h3 style={{ fontSize: 18, fontWeight: 700, color: '#141210', lineHeight: 1.35, margin: '6px 0' }}>{a.title}</h3>
              <div style={{ fontSize: 12, color: '#999' }}>
                Terre Etendue | {a.date && new Date(a.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })} | {a.readTime} min
              </div>
              <p style={{ fontSize: 14, color: '#666', lineHeight: 1.5, marginTop: 6 }}>{a.description}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
